# -*- coding: utf-8 -*-
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class MonitoringDiscovery(MonitoringBaseModel):
    """
    Ejecución de descubrimiento realizada por un agente
    sobre una red autorizada.

    Registra:

    - Red escaneada.
    - Rango procesado.
    - Fechas de inicio y fin.
    - Cantidad de IP consultadas.
    - Equipos que respondieron.
    - Dispositivos SNMP encontrados.
    - Credenciales probadas.
    - Errores y resultados.
    """

    class DiscoveryType(models.TextChoices):
        AUTOMATIC = (
            "automatic",
            "Automático",
        )
        MANUAL = (
            "manual",
            "Manual",
        )
        INITIAL = (
            "initial",
            "Descubrimiento inicial",
        )
        SCHEDULED = (
            "scheduled",
            "Programado",
        )
        DIAGNOSTIC = (
            "diagnostic",
            "Diagnóstico",
        )

    class Status(models.TextChoices):
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
            "Parcial",
        )
        CANCELLED = (
            "cancelled",
            "Cancelado",
        )
        ERROR = (
            "error",
            "Con error",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        on_delete=models.PROTECT,
        related_name="discoveries",
        verbose_name="Agente",
    )

    network = models.ForeignKey(
        "monitoring.MonitoringNetwork",
        on_delete=models.PROTECT,
        related_name="discoveries",
        verbose_name="Red",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_discoveries",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_discoveries",
        verbose_name="Sede",
    )

    discovery_type = models.CharField(
        max_length=20,
        choices=DiscoveryType.choices,
        default=DiscoveryType.AUTOMATIC,
        db_index=True,
        verbose_name="Tipo de descubrimiento",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    agent_discovery_id = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Identificador del agente",
        help_text=(
            "Identificador único generado por el agente para evitar "
            "duplicar una ejecución reenviada."
        ),
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de inicio",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de finalización",
    )

    received_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de recepción",
    )

    start_ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        protocol="both",
        unpack_ipv4=True,
        verbose_name="Primera IP procesada",
    )

    end_ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        protocol="both",
        unpack_ipv4=True,
        verbose_name="Última IP procesada",
    )

    total_target_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Total de objetivos",
    )

    scanned_host_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Hosts consultados",
    )

    excluded_host_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Hosts excluidos",
    )

    responding_host_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Hosts con respuesta",
    )

    snmp_responding_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Hosts con respuesta SNMP",
    )

    confirmed_printer_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Impresoras confirmadas",
    )

    new_device_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Dispositivos nuevos",
    )

    updated_device_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Dispositivos actualizados",
    )

    offline_device_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Dispositivos sin respuesta",
    )

    credential_attempt_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Credenciales probadas",
    )

    successful_credential_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Credenciales correctas",
    )

    timeout_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Tiempos de espera agotados",
    )

    authentication_error_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Errores de autenticación",
    )

    network_error_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Errores de red",
    )

    other_error_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Otros errores",
    )

    duration_seconds = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración en segundos",
    )

    agent_version = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Versión del agente",
    )

    configuration_version = models.PositiveBigIntegerField(
        default=1,
        verbose_name="Versión de configuración",
    )

    was_partial_scan = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Escaneo parcial",
    )

    next_cursor_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        protocol="both",
        unpack_ipv4=True,
        verbose_name="Próxima IP pendiente",
        help_text=(
            "Permite continuar una red grande en el siguiente ciclo."
        ),
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    error_message = models.TextField(
        blank=True,
        verbose_name="Error general",
    )

    result_summary = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resumen de resultados",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Descubrimiento de red"
        verbose_name_plural = "Descubrimientos de red"
        ordering = (
            "-received_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "started_at",
                    "status",
                ],
                name="mon_disc_customer_date_idx",
            ),
            models.Index(
                fields=[
                    "agent",
                    "network",
                    "started_at",
                ],
                name="mon_disc_agent_network_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "received_at",
                ],
                name="mon_disc_status_received_idx",
            ),
            models.Index(
                fields=[
                    "confirmed_printer_count",
                    "completed_at",
                ],
                name="mon_disc_printer_date_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "agent",
                    "agent_discovery_id",
                ],
                name="unique_agent_discovery_id",
            ),
        ]

    def __str__(self):
        return (
            f"{self.network} - "
            f"{self.get_status_display()}"
        )

    def mark_started(self):
        if self.status not in {
            self.Status.PENDING,
            self.Status.ERROR,
        }:
            raise ValidationError(
                "Este descubrimiento no puede volver a iniciarse."
            )

        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.completed_at = None
        self.duration_seconds = None
        self.error_message = ""
        self.cancellation_reason = ""

        self.save(
            update_fields=[
                "status",
                "started_at",
                "completed_at",
                "duration_seconds",
                "error_message",
                "cancellation_reason",
                "updated_at",
            ]
        )

        self.network.mark_discovery_started()

    def mark_completed(
        self,
        *,
        scanned_host_count=0,
        excluded_host_count=0,
        responding_host_count=0,
        snmp_responding_count=0,
        confirmed_printer_count=0,
        new_device_count=0,
        updated_device_count=0,
        offline_device_count=0,
        credential_attempt_count=0,
        successful_credential_count=0,
        timeout_count=0,
        authentication_error_count=0,
        network_error_count=0,
        other_error_count=0,
        partial=False,
        next_cursor_ip=None,
        result_summary=None,
        next_discovery_at=None,
    ):
        now = timezone.now()

        self.status = (
            self.Status.PARTIAL
            if partial
            else self.Status.COMPLETED
        )

        self.completed_at = now
        self.was_partial_scan = partial
        self.next_cursor_ip = next_cursor_ip

        self.scanned_host_count = max(
            int(scanned_host_count or 0),
            0,
        )
        self.excluded_host_count = max(
            int(excluded_host_count or 0),
            0,
        )
        self.responding_host_count = max(
            int(responding_host_count or 0),
            0,
        )
        self.snmp_responding_count = max(
            int(snmp_responding_count or 0),
            0,
        )
        self.confirmed_printer_count = max(
            int(confirmed_printer_count or 0),
            0,
        )
        self.new_device_count = max(
            int(new_device_count or 0),
            0,
        )
        self.updated_device_count = max(
            int(updated_device_count or 0),
            0,
        )
        self.offline_device_count = max(
            int(offline_device_count or 0),
            0,
        )
        self.credential_attempt_count = max(
            int(credential_attempt_count or 0),
            0,
        )
        self.successful_credential_count = max(
            int(successful_credential_count or 0),
            0,
        )
        self.timeout_count = max(
            int(timeout_count or 0),
            0,
        )
        self.authentication_error_count = max(
            int(authentication_error_count or 0),
            0,
        )
        self.network_error_count = max(
            int(network_error_count or 0),
            0,
        )
        self.other_error_count = max(
            int(other_error_count or 0),
            0,
        )

        self.error_message = ""

        if result_summary is not None:
            self.result_summary = result_summary

        self.calculate_duration()

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "was_partial_scan",
                "next_cursor_ip",
                "scanned_host_count",
                "excluded_host_count",
                "responding_host_count",
                "snmp_responding_count",
                "confirmed_printer_count",
                "new_device_count",
                "updated_device_count",
                "offline_device_count",
                "credential_attempt_count",
                "successful_credential_count",
                "timeout_count",
                "authentication_error_count",
                "network_error_count",
                "other_error_count",
                "duration_seconds",
                "error_message",
                "result_summary",
                "updated_at",
            ]
        )

        self.network.mark_discovery_completed(
            scanned_host_count=self.scanned_host_count,
            responding_host_count=self.responding_host_count,
            snmp_device_count=self.snmp_responding_count,
            partial=partial,
            next_discovery_at=next_discovery_at,
        )

    def mark_error(
        self,
        error_message,
        *,
        next_discovery_at=None,
    ):
        self.status = self.Status.ERROR
        self.completed_at = timezone.now()
        self.error_message = str(
            error_message or ""
        ).strip()

        self.calculate_duration()

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "error_message",
                "duration_seconds",
                "updated_at",
            ]
        )

        self.network.mark_discovery_error(
            self.error_message,
            next_discovery_at=next_discovery_at,
        )

    def cancel(
        self,
        *,
        reason="",
    ):
        if self.status in {
            self.Status.COMPLETED,
            self.Status.PARTIAL,
            self.Status.CANCELLED,
        }:
            raise ValidationError(
                "Este descubrimiento ya terminó."
            )

        self.status = self.Status.CANCELLED
        self.completed_at = timezone.now()
        self.cancellation_reason = str(
            reason or ""
        ).strip()

        self.calculate_duration()

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "cancellation_reason",
                "duration_seconds",
                "updated_at",
            ]
        )

    def calculate_duration(self):
        if self.started_at and self.completed_at:
            seconds = (
                self.completed_at - self.started_at
            ).total_seconds()

            self.duration_seconds = max(
                int(seconds),
                0,
            )

    def clean(self):
        super().clean()

        text_fields = [
            "agent_discovery_id",
            "agent_version",
            "cancellation_reason",
            "error_message",
            "notes",
        ]

        for field_name in text_fields:
            value = getattr(
                self,
                field_name,
                "",
            )

            setattr(
                self,
                field_name,
                str(value or "").strip(),
            )

        if not self.agent_id:
            raise ValidationError(
                {
                    "agent": (
                        "El agente es obligatorio."
                    ),
                }
            )

        if not self.network_id:
            raise ValidationError(
                {
                    "network": (
                        "La red es obligatoria."
                    ),
                }
            )

        if self.network.agent_id != self.agent_id:
            raise ValidationError(
                {
                    "network": (
                        "La red no pertenece al agente."
                    ),
                }
            )

        if self.agent.customer_id != self.customer_id:
            raise ValidationError(
                {
                    "customer": (
                        "El cliente no coincide con el agente."
                    ),
                }
            )

        if (
            self.branch_id
            and self.branch.partner_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "branch": (
                        "La sede no pertenece al cliente."
                    ),
                }
            )

        if not self.agent_discovery_id:
            raise ValidationError(
                {
                    "agent_discovery_id": (
                        "El identificador del descubrimiento "
                        "es obligatorio."
                    ),
                }
            )

        if (
            self.completed_at
            and self.started_at
            and self.completed_at < self.started_at
        ):
            raise ValidationError(
                {
                    "completed_at": (
                        "La finalización no puede ser anterior "
                        "al inicio."
                    ),
                }
            )

        if (
            self.scanned_host_count
            > self.total_target_count
            and self.total_target_count > 0
        ):
            raise ValidationError(
                {
                    "scanned_host_count": (
                        "Los hosts consultados no pueden superar "
                        "el total de objetivos."
                    ),
                }
            )

        if (
            self.responding_host_count
            > self.scanned_host_count
        ):
            raise ValidationError(
                {
                    "responding_host_count": (
                        "Los hosts con respuesta no pueden superar "
                        "los hosts consultados."
                    ),
                }
            )

        if (
            self.snmp_responding_count
            > self.responding_host_count
        ):
            raise ValidationError(
                {
                    "snmp_responding_count": (
                        "Las respuestas SNMP no pueden superar "
                        "los hosts con respuesta."
                    ),
                }
            )

        if (
            self.confirmed_printer_count
            > self.snmp_responding_count
        ):
            raise ValidationError(
                {
                    "confirmed_printer_count": (
                        "Las impresoras confirmadas no pueden superar "
                        "los dispositivos SNMP."
                    ),
                }
            )

        if (
            self.status == self.Status.ERROR
            and not self.error_message
        ):
            raise ValidationError(
                {
                    "error_message": (
                        "Debe indicar el error del descubrimiento."
                    ),
                }
            )

        if (
            self.status == self.Status.CANCELLED
            and not self.cancellation_reason
        ):
            raise ValidationError(
                {
                    "cancellation_reason": (
                        "Debe indicar el motivo de cancelación."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        if self.agent_id:
            self.customer = self.agent.customer
            self.branch = self.agent.branch

        self.agent_discovery_id = str(
            self.agent_discovery_id or ""
        ).strip()

        self.agent_version = str(
            self.agent_version or ""
        ).strip()

        self.calculate_duration()
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
        raise ValidationError(
            "Los descubrimientos históricos no pueden archivarse."
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        raise ValidationError(
            "Los descubrimientos históricos no pueden restaurarse."
        )