# -*- coding: utf-8 -*-
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class AgentCommandLog(MonitoringBaseModel):
    """
    Historial inmutable de una orden enviada al agente.

    Registra cada cambio relevante:

    - Creación.
    - Disponibilidad.
    - Toma de la orden.
    - Inicio.
    - Progreso.
    - Renovación del bloqueo.
    - Reintento.
    - Error.
    - Solicitud de cancelación.
    - Cancelación confirmada.
    - Finalización.
    - Expiración.
    """

    class EventType(models.TextChoices):
        CREATED = (
            "created",
            "Orden creada",
        )
        AVAILABLE = (
            "available",
            "Orden disponible",
        )
        CLAIMED = (
            "claimed",
            "Orden tomada",
        )
        STARTED = (
            "started",
            "Orden iniciada",
        )
        PROGRESS = (
            "progress",
            "Progreso actualizado",
        )
        HEARTBEAT = (
            "heartbeat",
            "Heartbeat recibido",
        )
        LOCK_RENEWED = (
            "lock_renewed",
            "Bloqueo renovado",
        )
        RETRY_SCHEDULED = (
            "retry_scheduled",
            "Reintento programado",
        )
        COMPLETED = (
            "completed",
            "Orden completada",
        )
        PARTIAL = (
            "partial",
            "Orden parcialmente completada",
        )
        FAILED = (
            "failed",
            "Orden fallida",
        )
        CANCEL_REQUESTED = (
            "cancel_requested",
            "Cancelación solicitada",
        )
        CANCELLED = (
            "cancelled",
            "Orden cancelada",
        )
        EXPIRED = (
            "expired",
            "Orden expirada",
        )
        REJECTED = (
            "rejected",
            "Orden rechazada",
        )
        RESULT_RECEIVED = (
            "result_received",
            "Resultado recibido",
        )
        AGENT_MESSAGE = (
            "agent_message",
            "Mensaje del agente",
        )
        SYSTEM_MESSAGE = (
            "system_message",
            "Mensaje del sistema",
        )
        ERROR = (
            "error",
            "Error",
        )

    class SourceType(models.TextChoices):
        SYSTEM = (
            "system",
            "Sistema",
        )
        AGENT = (
            "agent",
            "Agente",
        )
        USER = (
            "user",
            "Usuario",
        )
        SCHEDULER = (
            "scheduler",
            "Programador",
        )
        API = (
            "api",
            "API",
        )

    command = models.ForeignKey(
        "monitoring.AgentCommand",
        on_delete=models.PROTECT,
        related_name="logs",
        verbose_name="Orden",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        on_delete=models.PROTECT,
        related_name="command_logs",
        verbose_name="Agente",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_agent_command_logs",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_agent_command_logs",
        verbose_name="Sede",
    )

    event_uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="UUID del evento",
    )

    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices,
        db_index=True,
        verbose_name="Tipo de evento",
    )

    source_type = models.CharField(
        max_length=20,
        choices=SourceType.choices,
        default=SourceType.SYSTEM,
        db_index=True,
        verbose_name="Origen",
    )

    previous_status = models.CharField(
        max_length=30,
        blank=True,
        db_index=True,
        verbose_name="Estado anterior",
    )

    new_status = models.CharField(
        max_length=30,
        blank=True,
        db_index=True,
        verbose_name="Estado nuevo",
    )

    message = models.TextField(
        blank=True,
        verbose_name="Mensaje",
    )

    progress_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Progreso",
    )

    attempt_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Número de intento",
    )

    lock_token_reference = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        verbose_name="Referencia del bloqueo",
        help_text=(
            "Referencia parcial o huella del token. "
            "Nunca debe guardar el token completo."
        ),
    )

    lock_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Expiración del bloqueo",
    )

    occurred_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha del evento",
    )

    agent_occurred_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha informada por el agente",
    )

    received_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de recepción",
    )

    agent_command_id = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Identificador del agente",
    )

    agent_version = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Versión del agente",
    )

    agent_event_id = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Identificador del evento del agente",
        help_text=(
            "Permite evitar duplicados cuando el agente "
            "reenvía eventos."
        ),
    )

    error_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de error",
    )

    error_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de error",
    )

    payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos del evento",
        help_text=(
            "No debe contener secretos, comunidades ni "
            "contraseñas SNMP."
        ),
    )

    result_summary = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resumen del resultado",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos",
    )

    created_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_agent_command_logs",
        verbose_name="Registrado por",
    )

    class Meta:
        verbose_name = "Historial de orden de agente"
        verbose_name_plural = "Historiales de órdenes de agentes"
        ordering = (
            "occurred_at",
            "created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "command",
                    "occurred_at",
                ],
                name="mon_cmdlog_command_date_idx",
            ),
            models.Index(
                fields=[
                    "agent",
                    "event_type",
                    "occurred_at",
                ],
                name="mon_cmdlog_agent_event_idx",
            ),
            models.Index(
                fields=[
                    "customer",
                    "new_status",
                    "occurred_at",
                ],
                name="mon_cmdlog_customer_status_idx",
            ),
            models.Index(
                fields=[
                    "source_type",
                    "occurred_at",
                ],
                name="mon_cmdlog_source_date_idx",
            ),
            models.Index(
                fields=[
                    "error_code",
                    "occurred_at",
                ],
                name="mon_cmdlog_error_date_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "agent",
                    "agent_event_id",
                ],
                condition=models.Q(
                    agent_event_id__gt="",
                ),
                name="unique_agent_command_log_event",
            ),
        ]

    def __str__(self):
        return (
            f"{self.command} - "
            f"{self.get_event_type_display()}"
        )

    @classmethod
    def register(
        cls,
        *,
        command,
        event_type,
        source_type=SourceType.SYSTEM,
        previous_status="",
        new_status="",
        message="",
        progress_percent=None,
        attempt_number=None,
        lock_token_reference="",
        lock_expires_at=None,
        agent_occurred_at=None,
        agent_event_id="",
        error_code="",
        error_message="",
        payload=None,
        result_summary=None,
        metadata=None,
        user=None,
    ):
        """
        Crea un registro histórico de la orden.

        Esta operación debe llamarse desde la capa de servicio
        que modifica AgentCommand.
        """

        return cls.objects.create(
            command=command,
            agent=command.agent,
            customer=command.customer,
            branch=command.branch,
            event_type=event_type,
            source_type=source_type,
            previous_status=str(
                previous_status or ""
            ).strip(),
            new_status=str(
                new_status or ""
            ).strip(),
            message=str(
                message or ""
            ).strip(),
            progress_percent=progress_percent,
            attempt_number=attempt_number,
            lock_token_reference=str(
                lock_token_reference or ""
            ).strip(),
            lock_expires_at=lock_expires_at,
            agent_occurred_at=agent_occurred_at,
            agent_command_id=command.agent_command_id,
            agent_version=command.agent_version,
            agent_event_id=str(
                agent_event_id or ""
            ).strip(),
            error_code=str(
                error_code or ""
            ).strip().upper(),
            error_message=str(
                error_message or ""
            ).strip(),
            payload=payload or {},
            result_summary=result_summary or {},
            metadata=metadata or {},
            created_by=user,
        )

    def clean(self):
        super().clean()

        text_fields = [
            "previous_status",
            "new_status",
            "message",
            "lock_token_reference",
            "agent_command_id",
            "agent_version",
            "agent_event_id",
            "error_code",
            "error_message",
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

        self.error_code = self.error_code.upper()

        if not self.command_id:
            raise ValidationError(
                {
                    "command": "La orden es obligatoria.",
                }
            )

        if self.command.agent_id != self.agent_id:
            raise ValidationError(
                {
                    "agent": (
                        "El agente no coincide con la orden."
                    ),
                }
            )

        if self.command.customer_id != self.customer_id:
            raise ValidationError(
                {
                    "customer": (
                        "El cliente no coincide con la orden."
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

        if not self.event_type:
            raise ValidationError(
                {
                    "event_type": (
                        "El tipo de evento es obligatorio."
                    ),
                }
            )

        if not self.occurred_at:
            raise ValidationError(
                {
                    "occurred_at": (
                        "La fecha del evento es obligatoria."
                    ),
                }
            )

        if (
            self.agent_occurred_at
            and self.received_at
            and self.agent_occurred_at
            > self.received_at
            + timezone.timedelta(minutes=10)
        ):
            raise ValidationError(
                {
                    "agent_occurred_at": (
                        "La fecha informada por el agente "
                        "está demasiado adelantada."
                    ),
                }
            )

        if self.progress_percent is not None:
            if (
                self.progress_percent < 0
                or self.progress_percent > 100
            ):
                raise ValidationError(
                    {
                        "progress_percent": (
                            "El progreso debe estar "
                            "entre 0 y 100."
                        ),
                    }
                )

        error_events = {
            self.EventType.FAILED,
            self.EventType.ERROR,
            self.EventType.REJECTED,
        }

        if (
            self.event_type in error_events
            and not self.error_message
            and not self.message
        ):
            raise ValidationError(
                {
                    "error_message": (
                        "El evento de error debe registrar "
                        "un mensaje."
                    ),
                }
            )

        if (
            self.event_type == self.EventType.PROGRESS
            and self.progress_percent is None
        ):
            raise ValidationError(
                {
                    "progress_percent": (
                        "El evento de progreso requiere "
                        "un porcentaje."
                    ),
                }
            )

        if (
            self.event_type == self.EventType.CLAIMED
            and self.attempt_number is None
        ):
            raise ValidationError(
                {
                    "attempt_number": (
                        "El evento de toma requiere "
                        "el número de intento."
                    ),
                }
            )

        if not isinstance(
            self.payload,
            dict,
        ):
            raise ValidationError(
                {
                    "payload": (
                        "Los datos del evento deben ser un objeto."
                    ),
                }
            )

        if not isinstance(
            self.result_summary,
            dict,
        ):
            raise ValidationError(
                {
                    "result_summary": (
                        "El resumen del resultado debe "
                        "ser un objeto."
                    ),
                }
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValidationError(
                {
                    "metadata": (
                        "Los metadatos deben ser un objeto."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        if self.pk:
            original = (
                AgentCommandLog.objects
                .filter(
                    pk=self.pk,
                )
                .values(
                    "command_id",
                    "event_type",
                    "occurred_at",
                )
                .first()
            )

            if original:
                immutable_changed = any(
                    [
                        original["command_id"]
                        != self.command_id,
                        original["event_type"]
                        != self.event_type,
                        original["occurred_at"]
                        != self.occurred_at,
                    ]
                )

                if immutable_changed:
                    raise ValidationError(
                        "Los datos principales del historial "
                        "no pueden modificarse."
                    )

        if self.command_id:
            self.agent = self.command.agent
            self.customer = self.command.customer
            self.branch = self.command.branch

            if not self.agent_command_id:
                self.agent_command_id = (
                    self.command.agent_command_id
                )

            if not self.agent_version:
                self.agent_version = (
                    self.command.agent_version
                )

        self.error_code = str(
            self.error_code or ""
        ).strip().upper()

        self.agent_event_id = str(
            self.agent_event_id or ""
        ).strip()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )

    def delete(self, *args, **kwargs):
        raise ValidationError(
            "El historial de órdenes no puede eliminarse."
        )

    def archive(
        self,
        user=None,
        reason="",
        save=True,
    ):
        raise ValidationError(
            "El historial de órdenes no puede archivarse."
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        raise ValidationError(
            "El historial de órdenes no puede restaurarse."
        )