# -*- coding: utf-8 -*-
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class AgentCommand(MonitoringBaseModel):
    """
    Orden enviada desde Copier OS hacia un agente de monitoreo.

    Permite controlar tareas como:

    - Descubrir una red.
    - Consultar un dispositivo.
    - Ejecutar inventario completo.
    - Probar una credencial SNMP.
    - Probar o activar un perfil SNMP.
    - Actualizar la configuración del agente.
    - Rotar credenciales del agente.
    - Actualizar el software del agente.
    - Reiniciar servicios internos del agente.

    El agente obtiene las órdenes pendientes durante su sincronización
    y devuelve posteriormente su progreso y resultado.
    """

    class CommandType(models.TextChoices):
        DISCOVER_NETWORK = (
            "discover_network",
            "Descubrir red",
        )
        POLL_DEVICE = (
            "poll_device",
            "Consultar dispositivo",
        )
        FULL_INVENTORY = (
            "full_inventory",
            "Inventario completo",
        )
        TEST_SNMP_CREDENTIAL = (
            "test_snmp_credential",
            "Probar credencial SNMP",
        )
        TEST_SNMP_PROFILE = (
            "test_snmp_profile",
            "Probar perfil SNMP",
        )
        APPLY_SNMP_PROFILE = (
            "apply_snmp_profile",
            "Aplicar perfil SNMP",
        )
        REFRESH_CONFIGURATION = (
            "refresh_configuration",
            "Actualizar configuración",
        )
        ROTATE_AGENT_CREDENTIAL = (
            "rotate_agent_credential",
            "Rotar credencial del agente",
        )
        UPDATE_AGENT = (
            "update_agent",
            "Actualizar agente",
        )
        RESTART_AGENT = (
            "restart_agent",
            "Reiniciar agente",
        )
        RESTART_SERVICE = (
            "restart_service",
            "Reiniciar servicio",
        )
        RUN_DIAGNOSTIC = (
            "run_diagnostic",
            "Ejecutar diagnóstico",
        )
        COLLECT_RAW_WALK = (
            "collect_raw_walk",
            "Ejecutar WALK completo",
        )
        CANCEL_COMMAND = (
            "cancel_command",
            "Cancelar orden",
        )
        CUSTOM = (
            "custom",
            "Orden personalizada",
        )

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        AVAILABLE = (
            "available",
            "Disponible para el agente",
        )
        CLAIMED = (
            "claimed",
            "Tomada por el agente",
        )
        RUNNING = (
            "running",
            "En ejecución",
        )
        COMPLETED = (
            "completed",
            "Completada",
        )
        PARTIAL = (
            "partial",
            "Completada parcialmente",
        )
        FAILED = (
            "failed",
            "Fallida",
        )
        CANCEL_REQUESTED = (
            "cancel_requested",
            "Cancelación solicitada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )
        EXPIRED = (
            "expired",
            "Expirada",
        )
        REJECTED = (
            "rejected",
            "Rechazada",
        )

    class Priority(models.IntegerChoices):
        LOW = (
            10,
            "Baja",
        )
        NORMAL = (
            50,
            "Normal",
        )
        HIGH = (
            80,
            "Alta",
        )
        CRITICAL = (
            100,
            "Crítica",
        )

    class SourceType(models.TextChoices):
        SYSTEM = (
            "system",
            "Sistema",
        )
        USER = (
            "user",
            "Usuario",
        )
        SCHEDULE = (
            "schedule",
            "Programación",
        )
        ALERT = (
            "alert",
            "Alerta",
        )
        API = (
            "api",
            "API",
        )
        AGENT = (
            "agent",
            "Agente",
        )

    command_uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="UUID de la orden",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        on_delete=models.PROTECT,
        related_name="commands",
        verbose_name="Agente",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_agent_commands",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_agent_commands",
        verbose_name="Sede",
    )

    network = models.ForeignKey(
        "monitoring.MonitoringNetwork",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="agent_commands",
        verbose_name="Red",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="agent_commands",
        verbose_name="Dispositivo",
    )

    snmp_credential = models.ForeignKey(
        "monitoring.SNMPCredential",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="agent_commands",
        verbose_name="Credencial SNMP",
    )

    snmp_profile = models.ForeignKey(
        "monitoring.SNMPProfile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="agent_commands",
        verbose_name="Perfil SNMP",
    )

    profile_assignment = models.ForeignKey(
        "monitoring.DeviceProfileAssignment",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="agent_commands",
        verbose_name="Asignación de perfil",
    )

    parent_command = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="child_commands",
        verbose_name="Orden principal",
    )

    command_type = models.CharField(
        max_length=40,
        choices=CommandType.choices,
        db_index=True,
        verbose_name="Tipo de orden",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    priority = models.PositiveSmallIntegerField(
        choices=Priority.choices,
        default=Priority.NORMAL,
        db_index=True,
        verbose_name="Prioridad",
    )

    source_type = models.CharField(
        max_length=20,
        choices=SourceType.choices,
        default=SourceType.SYSTEM,
        db_index=True,
        verbose_name="Origen",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Título",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    idempotency_key = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Clave de idempotencia",
        help_text=(
            "Evita crear órdenes equivalentes repetidas dentro "
            "del mismo agente."
        ),
    )

    payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Parámetros de ejecución",
        help_text=(
            "Nunca debe contener comunidades, contraseñas "
            "o secretos SNMP sin cifrar."
        ),
    )

    result = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resultado",
    )

    progress_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Detalle de progreso",
    )

    progress_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Progreso",
    )

    agent_command_id = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Identificador interno del agente",
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

    available_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Disponible desde",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de expiración",
    )

    claimed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de toma",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de inicio",
    )

    heartbeat_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último progreso recibido",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de finalización",
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de cancelación",
    )

    duration_ms = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración en milisegundos",
    )

    attempt_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Intentos realizados",
    )

    maximum_attempts = models.PositiveIntegerField(
        default=3,
        verbose_name="Intentos máximos",
    )

    retry_after = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Reintentar después de",
    )

    last_attempt_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último intento",
    )

    lock_token = models.UUIDField(
        null=True,
        blank=True,
        editable=False,
        db_index=True,
        verbose_name="Token de bloqueo",
    )

    lock_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Expiración del bloqueo",
    )

    cancellation_requested = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Cancelación solicitada",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
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

    error_details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Detalle del error",
    )

    created_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_monitoring_agent_commands",
        verbose_name="Creada por",
    )

    cancelled_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cancelled_monitoring_agent_commands",
        verbose_name="Cancelada por",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Orden de agente"
        verbose_name_plural = "Órdenes de agentes"
        ordering = (
            "-priority",
            "available_at",
            "created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "agent",
                    "status",
                    "available_at",
                    "priority",
                ],
                name="mon_cmd_agent_queue_idx",
            ),
            models.Index(
                fields=[
                    "customer",
                    "command_type",
                    "created_at",
                ],
                name="mon_cmd_customer_type_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "status",
                    "created_at",
                ],
                name="mon_cmd_device_status_idx",
            ),
            models.Index(
                fields=[
                    "network",
                    "command_type",
                    "status",
                ],
                name="mon_cmd_network_type_idx",
            ),
            models.Index(
                fields=[
                    "retry_after",
                    "status",
                ],
                name="mon_cmd_retry_status_idx",
            ),
            models.Index(
                fields=[
                    "lock_expires_at",
                    "status",
                ],
                name="mon_cmd_lock_status_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "agent",
                    "idempotency_key",
                ],
                condition=models.Q(
                    idempotency_key__gt="",
                    archived_at__isnull=True,
                ),
                name="unique_agent_command_idempotency",
            ),
        ]

    def __str__(self):
        return (
            f"{self.agent} - "
            f"{self.title} - "
            f"{self.get_status_display()}"
        )

    def is_terminal(self):
        return self.status in {
            self.Status.COMPLETED,
            self.Status.PARTIAL,
            self.Status.FAILED,
            self.Status.CANCELLED,
            self.Status.EXPIRED,
            self.Status.REJECTED,
        }

    def can_be_claimed(self, now=None):
        now = now or timezone.now()

        if self.status not in {
            self.Status.PENDING,
            self.Status.AVAILABLE,
        }:
            return False

        if self.available_at > now:
            return False

        if self.retry_after and self.retry_after > now:
            return False

        if self.expires_at and self.expires_at <= now:
            return False

        if (
            self.lock_expires_at
            and self.lock_expires_at > now
        ):
            return False

        if self.attempt_count >= self.maximum_attempts:
            return False

        return True

    def mark_available(self):
        if self.is_terminal():
            raise ValidationError(
                "Una orden finalizada no puede volver a estar disponible."
            )

        self.status = self.Status.AVAILABLE
        self.lock_token = None
        self.lock_expires_at = None

        self.save(
            update_fields=[
                "status",
                "lock_token",
                "lock_expires_at",
                "updated_at",
            ]
        )

    def claim(
        self,
        *,
        agent_command_id="",
        agent_version="",
        lock_seconds=300,
    ):
        if not self.can_be_claimed():
            raise ValidationError(
                "La orden no está disponible para ser tomada."
            )

        now = timezone.now()

        self.status = self.Status.CLAIMED
        self.claimed_at = now
        self.last_attempt_at = now
        self.attempt_count += 1
        self.lock_token = uuid.uuid4()
        self.lock_expires_at = now + timezone.timedelta(
            seconds=max(
                int(lock_seconds or 300),
                30,
            )
        )

        self.agent_command_id = str(
            agent_command_id or ""
        ).strip()

        self.agent_version = str(
            agent_version or ""
        ).strip()

        self.error_code = ""
        self.error_message = ""
        self.error_details = {}

        self.save(
            update_fields=[
                "status",
                "claimed_at",
                "last_attempt_at",
                "attempt_count",
                "lock_token",
                "lock_expires_at",
                "agent_command_id",
                "agent_version",
                "error_code",
                "error_message",
                "error_details",
                "updated_at",
            ]
        )

        return self.lock_token

    def start(
        self,
        *,
        lock_token,
    ):
        if self.status != self.Status.CLAIMED:
            raise ValidationError(
                "La orden debe estar tomada antes de iniciarse."
            )

        self.validate_lock_token(
            lock_token
        )

        now = timezone.now()

        self.status = self.Status.RUNNING
        self.started_at = self.started_at or now
        self.heartbeat_at = now

        self.save(
            update_fields=[
                "status",
                "started_at",
                "heartbeat_at",
                "updated_at",
            ]
        )

    def register_progress(
        self,
        *,
        lock_token,
        progress_percent,
        progress_data=None,
        lock_seconds=300,
    ):
        if self.status not in {
            self.Status.CLAIMED,
            self.Status.RUNNING,
            self.Status.CANCEL_REQUESTED,
        }:
            raise ValidationError(
                "La orden no admite actualizaciones de progreso."
            )

        self.validate_lock_token(
            lock_token
        )

        now = timezone.now()

        self.progress_percent = progress_percent
        self.heartbeat_at = now
        self.lock_expires_at = now + timezone.timedelta(
            seconds=max(
                int(lock_seconds or 300),
                30,
            )
        )

        if progress_data is not None:
            self.progress_data = progress_data

        if (
            self.status == self.Status.CLAIMED
            and not self.cancellation_requested
        ):
            self.status = self.Status.RUNNING
            self.started_at = self.started_at or now

        self.save(
            update_fields=[
                "status",
                "started_at",
                "progress_percent",
                "progress_data",
                "heartbeat_at",
                "lock_expires_at",
                "updated_at",
            ]
        )

    def complete(
        self,
        *,
        lock_token,
        result=None,
        partial=False,
    ):
        if self.status not in {
            self.Status.CLAIMED,
            self.Status.RUNNING,
            self.Status.CANCEL_REQUESTED,
        }:
            raise ValidationError(
                "La orden no puede completarse en su estado actual."
            )

        self.validate_lock_token(
            lock_token
        )

        self.status = (
            self.Status.PARTIAL
            if partial
            else self.Status.COMPLETED
        )

        self.completed_at = timezone.now()
        self.progress_percent = 100
        self.lock_token = None
        self.lock_expires_at = None
        self.retry_after = None
        self.error_code = ""
        self.error_message = ""
        self.error_details = {}

        if result is not None:
            self.result = result

        self.calculate_duration()

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "progress_percent",
                "lock_token",
                "lock_expires_at",
                "retry_after",
                "error_code",
                "error_message",
                "error_details",
                "result",
                "duration_ms",
                "updated_at",
            ]
        )

    def fail(
        self,
        *,
        lock_token=None,
        error_message,
        error_code="",
        error_details=None,
        retry_after=None,
        allow_retry=True,
    ):
        if self.is_terminal():
            raise ValidationError(
                "La orden ya se encuentra finalizada."
            )

        if self.lock_token:
            self.validate_lock_token(
                lock_token
            )

        self.error_code = str(
            error_code or ""
        ).strip().upper()

        self.error_message = str(
            error_message or ""
        ).strip()

        if error_details is not None:
            self.error_details = error_details

        self.lock_token = None
        self.lock_expires_at = None

        can_retry = (
            allow_retry
            and self.attempt_count < self.maximum_attempts
            and not self.cancellation_requested
        )

        if can_retry:
            self.status = self.Status.AVAILABLE
            self.retry_after = retry_after or timezone.now()
        else:
            self.status = self.Status.FAILED
            self.completed_at = timezone.now()
            self.retry_after = None
            self.calculate_duration()

        self.save()

    def request_cancellation(
        self,
        *,
        reason,
        user=None,
    ):
        if self.is_terminal():
            raise ValidationError(
                "Una orden finalizada no puede cancelarse."
            )

        self.cancellation_requested = True
        self.cancellation_reason = str(
            reason or ""
        ).strip()

        self.cancelled_by = user

        if self.status in {
            self.Status.PENDING,
            self.Status.AVAILABLE,
        }:
            self.status = self.Status.CANCELLED
            self.cancelled_at = timezone.now()
            self.completed_at = self.cancelled_at
            self.lock_token = None
            self.lock_expires_at = None
            self.calculate_duration()
        else:
            self.status = self.Status.CANCEL_REQUESTED

        self.save()

    def confirm_cancelled(
        self,
        *,
        lock_token=None,
        result=None,
    ):
        if self.status not in {
            self.Status.CANCEL_REQUESTED,
            self.Status.CLAIMED,
            self.Status.RUNNING,
        }:
            raise ValidationError(
                "La orden no tiene una cancelación pendiente."
            )

        if self.lock_token:
            self.validate_lock_token(
                lock_token
            )

        now = timezone.now()

        self.status = self.Status.CANCELLED
        self.cancellation_requested = True
        self.cancelled_at = now
        self.completed_at = now
        self.lock_token = None
        self.lock_expires_at = None

        if result is not None:
            self.result = result

        self.calculate_duration()
        self.save()

    def expire(self):
        if self.is_terminal():
            return self

        self.status = self.Status.EXPIRED
        self.completed_at = timezone.now()
        self.lock_token = None
        self.lock_expires_at = None
        self.calculate_duration()

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "lock_token",
                "lock_expires_at",
                "duration_ms",
                "updated_at",
            ]
        )

        return self

    def validate_lock_token(self, lock_token):
        if not self.lock_token:
            raise ValidationError(
                "La orden no posee un bloqueo activo."
            )

        try:
            supplied_token = uuid.UUID(
                str(lock_token)
            )
        except (
            TypeError,
            ValueError,
            AttributeError,
        ) as exc:
            raise ValidationError(
                "El token de bloqueo no es válido."
            ) from exc

        if supplied_token != self.lock_token:
            raise ValidationError(
                "El token de bloqueo no coincide."
            )

        if (
            self.lock_expires_at
            and self.lock_expires_at <= timezone.now()
        ):
            raise ValidationError(
                "El bloqueo de la orden expiró."
            )

    def calculate_duration(self):
        if self.started_at and self.completed_at:
            milliseconds = (
                self.completed_at - self.started_at
            ).total_seconds() * 1000

            self.duration_ms = max(
                int(milliseconds),
                0,
            )

    def clean(self):
        super().clean()

        text_fields = [
            "title",
            "description",
            "idempotency_key",
            "agent_command_id",
            "agent_version",
            "cancellation_reason",
            "error_code",
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

        self.error_code = self.error_code.upper()

        if not self.agent_id:
            raise ValidationError(
                {
                    "agent": "El agente es obligatorio.",
                }
            )

        if not self.command_type:
            raise ValidationError(
                {
                    "command_type": (
                        "El tipo de orden es obligatorio."
                    ),
                }
            )

        if not self.title:
            raise ValidationError(
                {
                    "title": (
                        "El título de la orden es obligatorio."
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

        if (
            self.network_id
            and self.network.agent_id
            != self.agent_id
        ):
            raise ValidationError(
                {
                    "network": (
                        "La red no pertenece al agente."
                    ),
                }
            )

        if (
            self.device_id
            and self.device.agent_id
            != self.agent_id
        ):
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo no pertenece al agente."
                    ),
                }
            )

        if (
            self.snmp_credential_id
            and self.snmp_credential.customer_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "snmp_credential": (
                        "La credencial SNMP no pertenece al cliente."
                    ),
                }
            )

        if (
            self.profile_assignment_id
            and self.profile_assignment.device_id
            != self.device_id
        ):
            raise ValidationError(
                {
                    "profile_assignment": (
                        "La asignación no pertenece al dispositivo."
                    ),
                }
            )

        if (
            self.snmp_profile_id
            and self.profile_assignment_id
            and self.profile_assignment.profile_id
            != self.snmp_profile_id
        ):
            raise ValidationError(
                {
                    "snmp_profile": (
                        "El perfil no coincide con la asignación."
                    ),
                }
            )

        if (
            self.parent_command_id
            and self.parent_command.agent_id
            != self.agent_id
        ):
            raise ValidationError(
                {
                    "parent_command": (
                        "La orden principal pertenece a otro agente."
                    ),
                }
            )

        if (
            self.parent_command_id
            and self.parent_command_id == self.id
        ):
            raise ValidationError(
                {
                    "parent_command": (
                        "Una orden no puede depender de sí misma."
                    ),
                }
            )

        if self.maximum_attempts < 1:
            raise ValidationError(
                {
                    "maximum_attempts": (
                        "Debe permitirse al menos un intento."
                    ),
                }
            )

        if self.attempt_count > self.maximum_attempts:
            raise ValidationError(
                {
                    "attempt_count": (
                        "Los intentos realizados no pueden superar "
                        "el máximo permitido."
                    ),
                }
            )

        if (
            self.progress_percent < 0
            or self.progress_percent > 100
        ):
            raise ValidationError(
                {
                    "progress_percent": (
                        "El progreso debe estar entre 0 y 100."
                    ),
                }
            )

        if (
            self.expires_at
            and self.expires_at <= self.available_at
        ):
            raise ValidationError(
                {
                    "expires_at": (
                        "La expiración debe ser posterior "
                        "a la disponibilidad."
                    ),
                }
            )

        if (
            self.started_at
            and self.claimed_at
            and self.started_at < self.claimed_at
        ):
            raise ValidationError(
                {
                    "started_at": (
                        "El inicio no puede ser anterior "
                        "a la toma de la orden."
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
            self.status == self.Status.COMPLETED
            and self.progress_percent != 100
        ):
            raise ValidationError(
                {
                    "progress_percent": (
                        "Una orden completada debe registrar "
                        "100% de progreso."
                    ),
                }
            )

        if (
            self.cancellation_requested
            and not self.cancellation_reason
        ):
            raise ValidationError(
                {
                    "cancellation_reason": (
                        "Debe indicar el motivo de cancelación."
                    ),
                }
            )

        if self.status == self.Status.FAILED:
            if not self.error_message:
                raise ValidationError(
                    {
                        "error_message": (
                            "Una orden fallida debe registrar "
                            "el error."
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
                        "Los parámetros deben ser un objeto."
                    ),
                }
            )

        if not isinstance(
            self.result,
            dict,
        ):
            raise ValidationError(
                {
                    "result": (
                        "El resultado debe ser un objeto."
                    ),
                }
            )

        if not isinstance(
            self.progress_data,
            dict,
        ):
            raise ValidationError(
                {
                    "progress_data": (
                        "El detalle de progreso debe ser un objeto."
                    ),
                }
            )

        if not isinstance(
            self.error_details,
            dict,
        ):
            raise ValidationError(
                {
                    "error_details": (
                        "El detalle del error debe ser un objeto."
                    ),
                }
            )

        command_requirements = {
            self.CommandType.DISCOVER_NETWORK: (
                "network",
                self.network_id,
            ),
            self.CommandType.POLL_DEVICE: (
                "device",
                self.device_id,
            ),
            self.CommandType.FULL_INVENTORY: (
                "device",
                self.device_id,
            ),
            self.CommandType.TEST_SNMP_CREDENTIAL: (
                "snmp_credential",
                self.snmp_credential_id,
            ),
            self.CommandType.TEST_SNMP_PROFILE: (
                "snmp_profile",
                self.snmp_profile_id,
            ),
            self.CommandType.APPLY_SNMP_PROFILE: (
                "profile_assignment",
                self.profile_assignment_id,
            ),
            self.CommandType.COLLECT_RAW_WALK: (
                "device",
                self.device_id,
            ),
        }

        requirement = command_requirements.get(
            self.command_type
        )

        if requirement:
            field_name, value = requirement

            if not value:
                raise ValidationError(
                    {
                        field_name: (
                            "Este campo es obligatorio para "
                            "el tipo de orden seleccionado."
                        ),
                    }
                )

        if (
            self.expires_at
            and self.expires_at <= timezone.now()
            and not self.is_terminal()
        ):
            self.status = self.Status.EXPIRED

        self.calculate_duration()

    def save(self, *args, **kwargs):
        if self.agent_id:
            self.customer = self.agent.customer
            self.branch = self.agent.branch

        self.title = str(
            self.title or ""
        ).strip()

        self.idempotency_key = str(
            self.idempotency_key or ""
        ).strip()

        self.agent_command_id = str(
            self.agent_command_id or ""
        ).strip()

        self.error_code = str(
            self.error_code or ""
        ).strip().upper()

        self.calculate_duration()
        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )