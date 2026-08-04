# -*- coding: utf-8 -*-
import ipaddress

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class MonitoringNetwork(MonitoringBaseModel):
    """
    Red autorizada para descubrimiento y monitoreo.

    Un agente puede controlar varias redes, incluso cuando no
    pertenecen a la misma subred local, siempre que exista acceso
    entre ellas mediante rutas, VLAN o VPN.
    """

    class IPVersion(models.TextChoices):
        IPV4 = (
            "ipv4",
            "IPv4",
        )
        IPV6 = (
            "ipv6",
            "IPv6",
        )

    class DiscoveryMethod(models.TextChoices):
        SNMP_ONLY = (
            "snmp_only",
            "Solo SNMP",
        )
        PING_AND_SNMP = (
            "ping_and_snmp",
            "Ping y SNMP",
        )
        PORT_AND_SNMP = (
            "port_and_snmp",
            "Puerto y SNMP",
        )
        COMPLETE = (
            "complete",
            "Descubrimiento completo",
        )

    class DiscoveryStatus(models.TextChoices):
        NEVER = (
            "never",
            "Nunca ejecutado",
        )
        PENDING = (
            "pending",
            "Pendiente",
        )
        RUNNING = (
            "running",
            "En ejecución",
        )
        COMPLETED = (
            "completed",
            "Completado",
        )
        PARTIAL = (
            "partial",
            "Completado parcialmente",
        )
        ERROR = (
            "error",
            "Con error",
        )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        on_delete=models.PROTECT,
        related_name="networks",
        verbose_name="Agente",
    )

    name = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Nombre de la red",
        help_text=(
            "Ejemplo: Red principal, VLAN administrativa "
            "o red de impresoras."
        ),
    )

    cidr = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name="Red CIDR",
        help_text=(
            "Ejemplo: 192.168.1.0/24, "
            "192.168.0.0/24 o 10.20.0.0/16."
        ),
    )

    ip_version = models.CharField(
        max_length=10,
        choices=IPVersion.choices,
        editable=False,
        db_index=True,
        verbose_name="Versión IP",
    )

    gateway = models.GenericIPAddressField(
        null=True,
        blank=True,
        protocol="both",
        unpack_ipv4=True,
        verbose_name="Puerta de enlace",
    )

    source_ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        protocol="both",
        unpack_ipv4=True,
        verbose_name="IP de origen",
        help_text=(
            "Dirección local que el agente debe utilizar "
            "cuando posee varias interfaces de red."
        ),
    )

    source_interface = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Interfaz de origen",
        help_text=(
            "Ejemplo: Ethernet, eth0, ens33 o Wi-Fi."
        ),
    )

    is_routed_network = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Red enrutada",
        help_text=(
            "Indica que la red no es local al agente, pero puede "
            "alcanzarse mediante router, VLAN, VPN u otra ruta."
        ),
    )

    discovery_method = models.CharField(
        max_length=30,
        choices=DiscoveryMethod.choices,
        default=DiscoveryMethod.SNMP_ONLY,
        db_index=True,
        verbose_name="Método de descubrimiento",
    )

    discovery_enabled = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Permitir descubrimiento",
    )

    monitoring_enabled = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Permitir monitoreo",
    )

    scan_network_address = models.BooleanField(
        default=False,
        verbose_name="Consultar dirección de red",
    )

    scan_broadcast_address = models.BooleanField(
        default=False,
        verbose_name="Consultar dirección broadcast",
    )

    timeout_seconds = models.PositiveIntegerField(
        default=3,
        verbose_name="Tiempo de espera",
    )

    retry_count = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad de reintentos",
    )

    maximum_concurrent_hosts = models.PositiveIntegerField(
        default=20,
        verbose_name="Consultas simultáneas",
        help_text=(
            "Cantidad máxima de direcciones que el agente "
            "puede consultar al mismo tiempo."
        ),
    )

    maximum_hosts_per_cycle = models.PositiveIntegerField(
        default=1024,
        verbose_name="Máximo de hosts por ciclo",
        help_text=(
            "Protege al agente frente a redes demasiado grandes. "
            "La red puede procesarse en varios ciclos."
        ),
    )

    priority = models.PositiveIntegerField(
        default=100,
        db_index=True,
        verbose_name="Prioridad",
        help_text=(
            "Las redes con menor valor se procesan primero."
        ),
    )

    last_discovery_status = models.CharField(
        max_length=20,
        choices=DiscoveryStatus.choices,
        default=DiscoveryStatus.NEVER,
        db_index=True,
        verbose_name="Estado del último descubrimiento",
    )

    last_discovery_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio del último descubrimiento",
    )

    last_discovery_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin del último descubrimiento",
    )

    last_discovery_error = models.TextField(
        blank=True,
        verbose_name="Error del último descubrimiento",
    )

    last_scanned_host_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Hosts consultados",
    )

    last_responding_host_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Hosts con respuesta",
    )

    last_snmp_device_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Dispositivos SNMP detectados",
    )

    next_discovery_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Próximo descubrimiento",
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
        verbose_name = "Red de monitoreo"
        verbose_name_plural = "Redes de monitoreo"
        ordering = (
            "agent",
            "priority",
            "name",
        )
        indexes = [
            models.Index(
                fields=[
                    "agent",
                    "is_enabled",
                    "priority",
                ],
                name="mon_net_agent_enabled_idx",
            ),
            models.Index(
                fields=[
                    "discovery_enabled",
                    "next_discovery_at",
                ],
                name="mon_net_discovery_next_idx",
            ),
            models.Index(
                fields=[
                    "last_discovery_status",
                    "last_discovery_completed_at",
                ],
                name="mon_net_status_completed_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "agent",
                    "cidr",
                ],
                condition=models.Q(
                    archived_at__isnull=True,
                ),
                name="unique_active_agent_network",
            ),
        ]

    def __str__(self):
        return (
            f"{self.agent} - "
            f"{self.name} - "
            f"{self.cidr}"
        )

    @property
    def network_object(self):
        try:
            return ipaddress.ip_network(
                self.cidr,
                strict=False,
            )
        except ValueError:
            return None

    @property
    def total_address_count(self):
        network = self.network_object

        if not network:
            return 0

        return network.num_addresses

    @property
    def usable_host_count(self):
        network = self.network_object

        if not network:
            return 0

        if network.version == 4:
            if network.prefixlen >= 31:
                return network.num_addresses

            return max(
                network.num_addresses - 2,
                0,
            )

        return network.num_addresses

    def contains_ip(self, ip_address):
        network = self.network_object

        if not network:
            return False

        try:
            address = ipaddress.ip_address(
                str(ip_address)
            )
        except ValueError:
            return False

        return address in network

    def mark_discovery_started(self):
        self.last_discovery_status = (
            self.DiscoveryStatus.RUNNING
        )
        self.last_discovery_started_at = (
            timezone.now()
        )
        self.last_discovery_error = ""

        self.save(
            update_fields=[
                "last_discovery_status",
                "last_discovery_started_at",
                "last_discovery_error",
                "updated_at",
            ]
        )

    def mark_discovery_completed(
        self,
        *,
        scanned_host_count=0,
        responding_host_count=0,
        snmp_device_count=0,
        partial=False,
        next_discovery_at=None,
    ):
        self.last_discovery_status = (
            self.DiscoveryStatus.PARTIAL
            if partial
            else self.DiscoveryStatus.COMPLETED
        )

        self.last_discovery_completed_at = (
            timezone.now()
        )

        self.last_scanned_host_count = max(
            int(scanned_host_count or 0),
            0,
        )

        self.last_responding_host_count = max(
            int(responding_host_count or 0),
            0,
        )

        self.last_snmp_device_count = max(
            int(snmp_device_count or 0),
            0,
        )

        self.last_discovery_error = ""
        self.next_discovery_at = next_discovery_at

        self.save(
            update_fields=[
                "last_discovery_status",
                "last_discovery_completed_at",
                "last_scanned_host_count",
                "last_responding_host_count",
                "last_snmp_device_count",
                "last_discovery_error",
                "next_discovery_at",
                "updated_at",
            ]
        )

    def mark_discovery_error(
        self,
        error_message,
        *,
        next_discovery_at=None,
    ):
        self.last_discovery_status = (
            self.DiscoveryStatus.ERROR
        )

        self.last_discovery_completed_at = (
            timezone.now()
        )

        self.last_discovery_error = str(
            error_message or ""
        ).strip()

        self.next_discovery_at = next_discovery_at

        self.save(
            update_fields=[
                "last_discovery_status",
                "last_discovery_completed_at",
                "last_discovery_error",
                "next_discovery_at",
                "updated_at",
            ]
        )

    def clean(self):
        super().clean()

        self.name = str(
            self.name or ""
        ).strip()

        self.cidr = str(
            self.cidr or ""
        ).strip()

        self.source_interface = str(
            self.source_interface or ""
        ).strip()

        self.last_discovery_error = str(
            self.last_discovery_error or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        if not self.agent_id:
            raise ValidationError(
                {
                    "agent": (
                        "El agente de monitoreo es obligatorio."
                    ),
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": (
                        "El nombre de la red es obligatorio."
                    ),
                }
            )

        if not self.cidr:
            raise ValidationError(
                {
                    "cidr": (
                        "La red CIDR es obligatoria."
                    ),
                }
            )

        try:
            network = ipaddress.ip_network(
                self.cidr,
                strict=False,
            )
        except ValueError:
            raise ValidationError(
                {
                    "cidr": (
                        "La red CIDR no tiene un formato válido."
                    ),
                }
            )

        self.cidr = str(network)

        self.ip_version = (
            self.IPVersion.IPV4
            if network.version == 4
            else self.IPVersion.IPV6
        )

        if self.gateway:
            try:
                gateway = ipaddress.ip_address(
                    str(self.gateway)
                )
            except ValueError:
                raise ValidationError(
                    {
                        "gateway": (
                            "La puerta de enlace no es válida."
                        ),
                    }
                )

            if gateway.version != network.version:
                raise ValidationError(
                    {
                        "gateway": (
                            "La puerta de enlace debe utilizar "
                            "la misma versión IP de la red."
                        ),
                    }
                )

        if self.source_ip_address:
            try:
                source_ip = ipaddress.ip_address(
                    str(self.source_ip_address)
                )
            except ValueError:
                raise ValidationError(
                    {
                        "source_ip_address": (
                            "La dirección IP de origen no es válida."
                        ),
                    }
                )

            if source_ip.version != network.version:
                raise ValidationError(
                    {
                        "source_ip_address": (
                            "La IP de origen debe utilizar la misma "
                            "versión IP de la red."
                        ),
                    }
                )

        if self.timeout_seconds < 1:
            raise ValidationError(
                {
                    "timeout_seconds": (
                        "El tiempo de espera debe ser como mínimo "
                        "de un segundo."
                    ),
                }
            )

        if self.timeout_seconds > 60:
            raise ValidationError(
                {
                    "timeout_seconds": (
                        "El tiempo de espera no puede superar "
                        "los 60 segundos."
                    ),
                }
            )

        if self.retry_count > 10:
            raise ValidationError(
                {
                    "retry_count": (
                        "La cantidad de reintentos no puede "
                        "superar diez."
                    ),
                }
            )

        if self.maximum_concurrent_hosts < 1:
            raise ValidationError(
                {
                    "maximum_concurrent_hosts": (
                        "Debe permitirse por lo menos una "
                        "consulta simultánea."
                    ),
                }
            )

        if self.maximum_concurrent_hosts > 500:
            raise ValidationError(
                {
                    "maximum_concurrent_hosts": (
                        "No pueden ejecutarse más de 500 "
                        "consultas simultáneas."
                    ),
                }
            )

        if self.maximum_hosts_per_cycle < 1:
            raise ValidationError(
                {
                    "maximum_hosts_per_cycle": (
                        "Debe procesarse por lo menos un host "
                        "por ciclo."
                    ),
                }
            )

        if (
            self.last_discovery_started_at
            and self.last_discovery_completed_at
            and self.last_discovery_completed_at
            < self.last_discovery_started_at
        ):
            raise ValidationError(
                {
                    "last_discovery_completed_at": (
                        "La finalización del descubrimiento no puede "
                        "ser anterior a su inicio."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        self.name = str(
            self.name or ""
        ).strip()

        self.cidr = str(
            self.cidr or ""
        ).strip()

        self.source_interface = str(
            self.source_interface or ""
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
        self.discovery_enabled = False
        self.monitoring_enabled = False

        if save:
            self.save(
                update_fields=[
                    "is_enabled",
                    "discovery_enabled",
                    "monitoring_enabled",
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