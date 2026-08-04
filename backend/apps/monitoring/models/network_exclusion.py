# -*- coding: utf-8 -*-
import ipaddress

from django.core.exceptions import ValidationError
from django.db import models

from .base import MonitoringBaseModel


class MonitoringNetworkExclusion(MonitoringBaseModel):
    """
    Dirección, rango o subred que un agente no debe consultar.

    Permite excluir:

    - Una IP individual.
    - Un rango continuo de direcciones.
    - Una subred completa.
    - Gateways, routers, servidores u otros equipos.
    """

    class ExclusionType(models.TextChoices):
        SINGLE_IP = (
            "single_ip",
            "Dirección IP",
        )
        IP_RANGE = (
            "ip_range",
            "Rango de direcciones",
        )
        CIDR = (
            "cidr",
            "Subred CIDR",
        )

    class ReasonType(models.TextChoices):
        ROUTER = (
            "router",
            "Router o gateway",
        )
        SERVER = (
            "server",
            "Servidor",
        )
        NETWORK_DEVICE = (
            "network_device",
            "Equipo de red",
        )
        SECURITY_DEVICE = (
            "security_device",
            "Equipo de seguridad",
        )
        NON_PRINTER_DEVICE = (
            "non_printer_device",
            "No es impresora",
        )
        CUSTOMER_REQUEST = (
            "customer_request",
            "Solicitud del cliente",
        )
        TECHNICAL = (
            "technical",
            "Restricción técnica",
        )
        OTHER = (
            "other",
            "Otro motivo",
        )

    network = models.ForeignKey(
        "monitoring.MonitoringNetwork",
        on_delete=models.CASCADE,
        related_name="exclusions",
        verbose_name="Red de monitoreo",
    )

    exclusion_type = models.CharField(
        max_length=20,
        choices=ExclusionType.choices,
        db_index=True,
        verbose_name="Tipo de exclusión",
    )

    start_ip_address = models.GenericIPAddressField(
        protocol="both",
        unpack_ipv4=True,
        db_index=True,
        verbose_name="Dirección inicial",
        help_text=(
            "En una exclusión individual contiene la única "
            "dirección que no debe consultarse."
        ),
    )

    end_ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        protocol="both",
        unpack_ipv4=True,
        db_index=True,
        verbose_name="Dirección final",
        help_text=(
            "Solo se utiliza para exclusiones por rango."
        ),
    )

    cidr = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Subred excluida",
        help_text=(
            "Solo se utiliza cuando el tipo de exclusión "
            "es una subred CIDR."
        ),
    )

    reason_type = models.CharField(
        max_length=30,
        choices=ReasonType.choices,
        default=ReasonType.OTHER,
        db_index=True,
        verbose_name="Motivo",
    )

    reason = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Descripción del motivo",
    )

    is_enabled = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Habilitada",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Exclusión de red"
        verbose_name_plural = "Exclusiones de red"
        ordering = (
            "network",
            "start_ip_address",
        )
        indexes = [
            models.Index(
                fields=[
                    "network",
                    "is_enabled",
                    "exclusion_type",
                ],
                name="mon_excl_network_type_idx",
            ),
            models.Index(
                fields=[
                    "network",
                    "start_ip_address",
                    "end_ip_address",
                ],
                name="mon_excl_ip_range_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "network",
                    "exclusion_type",
                    "start_ip_address",
                    "end_ip_address",
                    "cidr",
                ],
                condition=models.Q(
                    archived_at__isnull=True,
                ),
                name="unique_active_network_exclusion",
            ),
        ]

    def __str__(self):
        if self.exclusion_type == self.ExclusionType.CIDR:
            value = self.cidr
        elif self.exclusion_type == self.ExclusionType.IP_RANGE:
            value = (
                f"{self.start_ip_address} - "
                f"{self.end_ip_address}"
            )
        else:
            value = str(
                self.start_ip_address
            )

        return (
            f"{self.network} - "
            f"{value}"
        )

    def contains_ip(self, ip_address):
        """
        Indica si una dirección está incluida
        dentro de esta exclusión.
        """

        if not self.is_enabled:
            return False

        if self.archived_at is not None:
            return False

        try:
            address = ipaddress.ip_address(
                str(ip_address)
            )
        except ValueError:
            return False

        if self.exclusion_type == self.ExclusionType.SINGLE_IP:
            return address == ipaddress.ip_address(
                str(self.start_ip_address)
            )

        if self.exclusion_type == self.ExclusionType.IP_RANGE:
            if not self.end_ip_address:
                return False

            start = ipaddress.ip_address(
                str(self.start_ip_address)
            )

            end = ipaddress.ip_address(
                str(self.end_ip_address)
            )

            return start <= address <= end

        if self.exclusion_type == self.ExclusionType.CIDR:
            try:
                excluded_network = ipaddress.ip_network(
                    self.cidr,
                    strict=False,
                )
            except ValueError:
                return False

            return address in excluded_network

        return False

    def clean(self):
        super().clean()

        self.cidr = str(
            self.cidr or ""
        ).strip()

        self.reason = str(
            self.reason or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        if not self.network_id:
            raise ValidationError(
                {
                    "network": (
                        "La red de monitoreo es obligatoria."
                    ),
                }
            )

        try:
            monitoring_network = ipaddress.ip_network(
                self.network.cidr,
                strict=False,
            )
        except ValueError:
            raise ValidationError(
                {
                    "network": (
                        "La red asociada no tiene un CIDR válido."
                    ),
                }
            )

        try:
            start_ip = ipaddress.ip_address(
                str(self.start_ip_address)
            )
        except ValueError:
            raise ValidationError(
                {
                    "start_ip_address": (
                        "La dirección IP inicial no es válida."
                    ),
                }
            )

        if start_ip.version != monitoring_network.version:
            raise ValidationError(
                {
                    "start_ip_address": (
                        "La dirección inicial debe utilizar "
                        "la misma versión IP de la red."
                    ),
                }
            )

        if (
            self.exclusion_type
            == self.ExclusionType.SINGLE_IP
        ):
            self.end_ip_address = None
            self.cidr = ""

            if start_ip not in monitoring_network:
                raise ValidationError(
                    {
                        "start_ip_address": (
                            "La dirección excluida no pertenece "
                            "a la red seleccionada."
                        ),
                    }
                )

        elif (
            self.exclusion_type
            == self.ExclusionType.IP_RANGE
        ):
            self.cidr = ""

            if not self.end_ip_address:
                raise ValidationError(
                    {
                        "end_ip_address": (
                            "Debe indicar la dirección final "
                            "del rango."
                        ),
                    }
                )

            try:
                end_ip = ipaddress.ip_address(
                    str(self.end_ip_address)
                )
            except ValueError:
                raise ValidationError(
                    {
                        "end_ip_address": (
                            "La dirección IP final no es válida."
                        ),
                    }
                )

            if end_ip.version != start_ip.version:
                raise ValidationError(
                    {
                        "end_ip_address": (
                            "Las direcciones inicial y final deben "
                            "utilizar la misma versión IP."
                        ),
                    }
                )

            if end_ip < start_ip:
                raise ValidationError(
                    {
                        "end_ip_address": (
                            "La dirección final no puede ser menor "
                            "que la dirección inicial."
                        ),
                    }
                )

            if (
                start_ip not in monitoring_network
                or end_ip not in monitoring_network
            ):
                raise ValidationError(
                    {
                        "end_ip_address": (
                            "Todo el rango debe pertenecer "
                            "a la red seleccionada."
                        ),
                    }
                )

        elif (
            self.exclusion_type
            == self.ExclusionType.CIDR
        ):
            self.end_ip_address = None

            if not self.cidr:
                raise ValidationError(
                    {
                        "cidr": (
                            "Debe indicar la subred que desea excluir."
                        ),
                    }
                )

            try:
                excluded_network = ipaddress.ip_network(
                    self.cidr,
                    strict=False,
                )
            except ValueError:
                raise ValidationError(
                    {
                        "cidr": (
                            "La subred excluida no tiene "
                            "un formato válido."
                        ),
                    }
                )

            self.cidr = str(
                excluded_network
            )

            self.start_ip_address = str(
                excluded_network.network_address
            )

            if (
                excluded_network.version
                != monitoring_network.version
            ):
                raise ValidationError(
                    {
                        "cidr": (
                            "La subred excluida debe utilizar "
                            "la misma versión IP."
                        ),
                    }
                )

            if not excluded_network.subnet_of(
                monitoring_network
            ):
                raise ValidationError(
                    {
                        "cidr": (
                            "La subred excluida debe estar contenida "
                            "dentro de la red de monitoreo."
                        ),
                    }
                )

        else:
            raise ValidationError(
                {
                    "exclusion_type": (
                        "El tipo de exclusión no es válido."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        self.cidr = str(
            self.cidr or ""
        ).strip()

        self.reason = str(
            self.reason or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )

    def archive(
        self,
        user=None,
        reason="",
        save=True,
    ):
        self.is_enabled = False

        if save:
            self.save(
                update_fields=[
                    "is_enabled",
                    "updated_at",
                ]
            )

        return super().archive(
            user=user,
            reason=reason,
            save=save,
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        self.is_enabled = True

        if save:
            self.save(
                update_fields=[
                    "is_enabled",
                    "updated_at",
                ]
            )

        return super().restore(
            user=user,
            save=save,
        )