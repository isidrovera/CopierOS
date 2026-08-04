# -*- coding: utf-8 -*-
import hashlib
import json
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class MonitoringNotificationInstance(MonitoringBaseModel):
    """
    Activación concreta de una regla de notificación.

    Conserva:

    - Regla que originó la notificación.
    - Dispositivo, agente, red o elemento relacionado.
    - Condición detectada.
    - Valor observado y umbral configurado.
    - Destinatarios resueltos.
    - Canales utilizados.
    - Intentos y repeticiones.
    - Reconocimiento y resolución.
    - Estado de envío por canal.
    """

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        ACTIVE = (
            "active",
            "Activa",
        )
        SENDING = (
            "sending",
            "Enviando",
        )
        SENT = (
            "sent",
            "Enviada",
        )
        PARTIAL = (
            "partial",
            "Envío parcial",
        )
        FAILED = (
            "failed",
            "Fallida",
        )
        ACKNOWLEDGED = (
            "acknowledged",
            "Reconocida",
        )
        RESOLVED = (
            "resolved",
            "Resuelta",
        )
        SUPPRESSED = (
            "suppressed",
            "Suprimida",
        )
        EXPIRED = (
            "expired",
            "Expirada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )

    class ResolutionType(models.TextChoices):
        AUTOMATIC = (
            "automatic",
            "Automática",
        )
        MANUAL = (
            "manual",
            "Manual",
        )
        CONDITION_CLEARED = (
            "condition_cleared",
            "Condición normalizada",
        )
        DEVICE_RESTORED = (
            "device_restored",
            "Dispositivo restablecido",
        )
        ALERT_CLOSED = (
            "alert_closed",
            "Alerta cerrada",
        )
        REPLACEMENT_DETECTED = (
            "replacement_detected",
            "Reemplazo detectado",
        )
        RULE_DISABLED = (
            "rule_disabled",
            "Regla deshabilitada",
        )
        DUPLICATE = (
            "duplicate",
            "Duplicada",
        )
        OTHER = (
            "other",
            "Otra",
        )

    notification_uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="UUID de notificación",
    )

    rule = models.ForeignKey(
        "monitoring.MonitoringNotificationRule",
        on_delete=models.PROTECT,
        related_name="notification_instances",
        verbose_name="Regla",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_notifications",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_notifications",
        verbose_name="Sede",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="notification_instances",
        verbose_name="Agente",
    )

    network = models.ForeignKey(
        "monitoring.MonitoringNetwork",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="notification_instances",
        verbose_name="Red",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="notification_instances",
        verbose_name="Dispositivo",
    )

    snapshot = models.ForeignKey(
        "monitoring.DeviceSnapshot",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="notification_instances",
        verbose_name="Captura",
    )

    device_event = models.ForeignKey(
        "monitoring.DeviceEvent",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="notification_instances",
        verbose_name="Evento",
    )

    device_alert = models.ForeignKey(
        "monitoring.DeviceAlert",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="notification_instances",
        verbose_name="Alerta",
    )

    agent_sync = models.ForeignKey(
        "monitoring.AgentSync",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="notification_instances",
        verbose_name="Sincronización",
    )

    agent_command = models.ForeignKey(
        "monitoring.AgentCommand",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="notification_instances",
        verbose_name="Orden",
    )

    duplicate_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="duplicate_notifications",
        verbose_name="Duplicada de",
    )

    notification_key = models.CharField(
        max_length=64,
        db_index=True,
        editable=False,
        verbose_name="Clave de notificación",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    severity = models.CharField(
        max_length=20,
        choices=[
            (
                "info",
                "Informativa",
            ),
            (
                "notice",
                "Aviso",
            ),
            (
                "warning",
                "Advertencia",
            ),
            (
                "error",
                "Error",
            ),
            (
                "critical",
                "Crítica",
            ),
        ],
        default="warning",
        db_index=True,
        verbose_name="Severidad",
    )

    rule_code = models.CharField(
        max_length=150,
        editable=False,
        db_index=True,
        verbose_name="Código de regla",
    )

    rule_type = models.CharField(
        max_length=40,
        editable=False,
        db_index=True,
        verbose_name="Tipo de regla",
    )

    title = models.CharField(
        max_length=500,
        verbose_name="Título",
    )

    message = models.TextField(
        verbose_name="Mensaje",
    )

    resolution_title = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Título de resolución",
    )

    resolution_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de resolución",
    )

    action_url = models.CharField(
        max_length=1000,
        blank=True,
        verbose_name="Enlace de acción",
    )

    metric_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de métrica",
    )

    entity_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de entidad",
    )

    entity_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre de entidad",
    )

    condition_field = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Campo evaluado",
    )

    condition_operator = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Operador evaluado",
    )

    observed_value = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Valor observado",
    )

    threshold_value = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Valor de umbral",
    )

    previous_value = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Valor anterior",
    )

    condition_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos de condición",
    )

    trigger_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos de activación",
    )

    context_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Contexto",
    )

    triggered_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de activación",
    )

    first_detected_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Primera detección",
    )

    last_detected_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Última detección",
    )

    condition_started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Inicio de condición",
    )

    condition_cleared_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fin de condición",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de expiración",
    )

    next_notification_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Próxima notificación",
    )

    last_notification_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Última notificación",
    )

    occurrence_count = models.PositiveBigIntegerField(
        default=1,
        verbose_name="Cantidad de ocurrencias",
    )

    notification_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad de envíos",
    )

    maximum_notifications = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Máximo de envíos",
    )

    channels = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Canales",
    )

    pending_channels = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Canales pendientes",
    )

    successful_channels = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Canales correctos",
    )

    failed_channels = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Canales fallidos",
    )

    recipient_user_ids = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Usuarios destinatarios",
    )

    recipient_role_codes = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Roles destinatarios",
    )

    recipient_emails = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Correos destinatarios",
    )

    recipient_contact_ids = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Contactos destinatarios",
    )

    resolved_recipients = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Destinatarios resueltos",
        help_text=(
            "Conserva los destinatarios determinados en el momento "
            "de la activación."
        ),
    )

    channel_results = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resultado por canal",
    )

    delivery_attempt_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Intentos de envío",
    )

    last_delivery_attempt_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último intento de envío",
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de envío",
    )

    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de reconocimiento",
    )

    acknowledged_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acknowledged_monitoring_notifications",
        verbose_name="Reconocida por",
    )

    acknowledgement_notes = models.TextField(
        blank=True,
        verbose_name="Notas de reconocimiento",
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de resolución",
    )

    resolved_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_monitoring_notifications",
        verbose_name="Resuelta por",
    )

    resolution_type = models.CharField(
        max_length=30,
        choices=ResolutionType.choices,
        blank=True,
        db_index=True,
        verbose_name="Tipo de resolución",
    )

    resolution_notes = models.TextField(
        blank=True,
        verbose_name="Notas de resolución",
    )

    suppressed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de supresión",
    )

    suppression_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de supresión",
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de cancelación",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    requires_acknowledgement = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere reconocimiento",
    )

    requires_user_action = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere acción",
    )

    is_acknowledged = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Reconocida",
    )

    is_resolved = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Resuelta",
    )

    is_condition_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Condición activa",
    )

    is_duplicate = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Duplicada",
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

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Notificación de monitoreo"
        verbose_name_plural = "Notificaciones de monitoreo"
        ordering = (
            "-triggered_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "rule",
                    "status",
                    "triggered_at",
                ],
                name="mon_ninst_rule_status_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "is_condition_active",
                    "triggered_at",
                ],
                name="mon_ninst_device_active_idx",
            ),
            models.Index(
                fields=[
                    "customer",
                    "severity",
                    "triggered_at",
                ],
                name="mon_ninst_customer_sev_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "next_notification_at",
                ],
                name="mon_ninst_next_status_idx",
            ),
            models.Index(
                fields=[
                    "requires_acknowledgement",
                    "is_acknowledged",
                    "triggered_at",
                ],
                name="mon_ninst_ack_idx",
            ),
            models.Index(
                fields=[
                    "is_resolved",
                    "is_condition_active",
                    "triggered_at",
                ],
                name="mon_ninst_resolution_idx",
            ),
            models.Index(
                fields=[
                    "metric_code",
                    "entity_code",
                    "triggered_at",
                ],
                name="mon_ninst_metric_entity_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "rule",
                    "notification_key",
                ],
                condition=models.Q(
                    is_condition_active=True,
                    is_duplicate=False,
                    archived_at__isnull=True,
                ),
                name="unique_active_notification_key",
            ),
        ]

    def __str__(self):
        return (
            f"{self.rule_code} - "
            f"{self.title} - "
            f"{self.get_status_display()}"
        )

    @staticmethod
    def normalize_hash_value(value):
        if value is None:
            return ""

        if isinstance(
            value,
            (
                dict,
                list,
                tuple,
            ),
        ):
            return json.dumps(
                value,
                sort_keys=True,
                ensure_ascii=False,
                default=str,
            )

        return str(value).strip()

    def calculate_notification_key(self):
        """
        La clave identifica una condición activa equivalente.

        No incluye el momento exacto para permitir agrupar nuevas
        ocurrencias mientras la condición siga abierta.
        """

        values = [
            str(self.rule_id or ""),
            str(self.customer_id or ""),
            str(self.branch_id or ""),
            str(self.agent_id or ""),
            str(self.network_id or ""),
            str(self.device_id or ""),
            str(self.metric_code or "").strip().upper(),
            str(self.entity_code or "").strip().upper(),
            str(self.condition_field or "").strip(),
            str(self.condition_operator or "").strip(),
            self.normalize_hash_value(
                self.threshold_value
            ),
        ]

        return hashlib.sha256(
            "|".join(values).encode("utf-8")
        ).hexdigest()

    def can_send_again(
        self,
        *,
        current_datetime=None,
    ):
        current_datetime = (
            current_datetime
            or timezone.now()
        )

        if self.status in {
            self.Status.RESOLVED,
            self.Status.SUPPRESSED,
            self.Status.EXPIRED,
            self.Status.CANCELLED,
        }:
            return False

        if not self.is_condition_active:
            return False

        if (
            self.maximum_notifications is not None
            and self.notification_count
            >= self.maximum_notifications
        ):
            return False

        if (
            self.next_notification_at
            and self.next_notification_at
            > current_datetime
        ):
            return False

        return True

    def register_occurrence(
        self,
        *,
        observed_value=None,
        trigger_data=None,
        detected_at=None,
    ):
        if self.is_resolved:
            raise ValidationError(
                "Una notificación resuelta no admite nuevas ocurrencias."
            )

        detected_at = (
            detected_at
            or timezone.now()
        )

        self.occurrence_count += 1
        self.last_detected_at = detected_at
        self.is_condition_active = True

        if observed_value is not None:
            self.previous_value = self.observed_value
            self.observed_value = observed_value

        if trigger_data is not None:
            self.trigger_data = trigger_data

        if self.status in {
            self.Status.FAILED,
            self.Status.SENT,
            self.Status.PARTIAL,
        }:
            self.status = self.Status.ACTIVE

        self.save(
            update_fields=[
                "occurrence_count",
                "last_detected_at",
                "is_condition_active",
                "previous_value",
                "observed_value",
                "trigger_data",
                "status",
                "updated_at",
            ]
        )

    def begin_sending(self):
        if not self.can_send_again():
            raise ValidationError(
                "La notificación no está disponible para envío."
            )

        self.status = self.Status.SENDING
        self.delivery_attempt_count += 1
        self.last_delivery_attempt_at = timezone.now()
        self.pending_channels = list(
            self.channels
        )
        self.successful_channels = []
        self.failed_channels = []
        self.channel_results = {}
        self.error_code = ""
        self.error_message = ""

        self.save(
            update_fields=[
                "status",
                "delivery_attempt_count",
                "last_delivery_attempt_at",
                "pending_channels",
                "successful_channels",
                "failed_channels",
                "channel_results",
                "error_code",
                "error_message",
                "updated_at",
            ]
        )

    def complete_delivery(
        self,
        *,
        successful_channels,
        failed_channels=None,
        channel_results=None,
    ):
        successful_channels = list(
            successful_channels
            or []
        )

        failed_channels = list(
            failed_channels
            or []
        )

        self.successful_channels = successful_channels
        self.failed_channels = failed_channels
        self.pending_channels = []

        if channel_results is not None:
            self.channel_results = channel_results

        if successful_channels and failed_channels:
            self.status = self.Status.PARTIAL
        elif successful_channels:
            self.status = self.Status.SENT
        else:
            self.status = self.Status.FAILED

        now = timezone.now()

        if successful_channels:
            self.sent_at = now
            self.last_notification_at = now
            self.notification_count += 1

            if (
                self.rule.repeat_interval_seconds
                and self.is_condition_active
            ):
                self.next_notification_at = (
                    now
                    + timezone.timedelta(
                        seconds=(
                            self.rule.repeat_interval_seconds
                        )
                    )
                )
            else:
                self.next_notification_at = None

        if self.status != self.Status.FAILED:
            self.error_code = ""
            self.error_message = ""

        self.save()

    def mark_delivery_failed(
        self,
        *,
        error_message,
        error_code="",
        channel_results=None,
        retry_at=None,
    ):
        self.status = self.Status.FAILED
        self.error_code = str(
            error_code or ""
        ).strip().upper()
        self.error_message = str(
            error_message or ""
        ).strip()
        self.pending_channels = []

        if channel_results is not None:
            self.channel_results = channel_results

        self.next_notification_at = retry_at

        self.save()

    def acknowledge(
        self,
        *,
        user,
        notes="",
    ):
        if self.is_acknowledged:
            return self

        self.is_acknowledged = True
        self.acknowledged_at = timezone.now()
        self.acknowledged_by = user
        self.acknowledgement_notes = str(
            notes or ""
        ).strip()

        if not self.is_resolved:
            self.status = self.Status.ACKNOWLEDGED

        self.save(
            update_fields=[
                "is_acknowledged",
                "acknowledged_at",
                "acknowledged_by",
                "acknowledgement_notes",
                "status",
                "updated_at",
            ]
        )

        return self

    def resolve(
        self,
        *,
        resolution_type,
        user=None,
        notes="",
        resolution_title="",
        resolution_message="",
        cleared_at=None,
    ):
        if self.is_resolved:
            return self

        now = cleared_at or timezone.now()

        self.status = self.Status.RESOLVED
        self.is_resolved = True
        self.is_condition_active = False
        self.condition_cleared_at = now
        self.resolved_at = now
        self.resolved_by = user
        self.resolution_type = resolution_type
        self.resolution_notes = str(
            notes or ""
        ).strip()
        self.resolution_title = str(
            resolution_title or ""
        ).strip()
        self.resolution_message = str(
            resolution_message or ""
        ).strip()
        self.next_notification_at = None
        self.pending_channels = []

        self.save()

        return self

    def suppress(
        self,
        *,
        reason,
    ):
        if self.is_resolved:
            raise ValidationError(
                "Una notificación resuelta no puede suprimirse."
            )

        self.status = self.Status.SUPPRESSED
        self.suppressed_at = timezone.now()
        self.suppression_reason = str(
            reason or ""
        ).strip()
        self.next_notification_at = None
        self.pending_channels = []

        self.save()

    def cancel(
        self,
        *,
        reason,
    ):
        if self.is_resolved:
            raise ValidationError(
                "Una notificación resuelta no puede cancelarse."
            )

        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancellation_reason = str(
            reason or ""
        ).strip()
        self.is_condition_active = False
        self.next_notification_at = None
        self.pending_channels = []

        self.save()

    def expire(self):
        if self.status in {
            self.Status.RESOLVED,
            self.Status.CANCELLED,
            self.Status.EXPIRED,
        }:
            return self

        self.status = self.Status.EXPIRED
        self.is_condition_active = False
        self.next_notification_at = None
        self.pending_channels = []

        self.save(
            update_fields=[
                "status",
                "is_condition_active",
                "next_notification_at",
                "pending_channels",
                "updated_at",
            ]
        )

        return self

    def mark_duplicate(
        self,
        original_notification,
    ):
        if original_notification.rule_id != self.rule_id:
            raise ValidationError(
                "La notificación original pertenece a otra regla."
            )

        self.is_duplicate = True
        self.duplicate_of = original_notification
        self.status = self.Status.SUPPRESSED
        self.suppressed_at = timezone.now()
        self.suppression_reason = (
            "Condición duplicada de una notificación activa."
        )
        self.is_condition_active = False
        self.next_notification_at = None

        self.save()

    def clean(self):
        super().clean()

        text_fields = [
            "rule_code",
            "rule_type",
            "title",
            "message",
            "resolution_title",
            "resolution_message",
            "action_url",
            "metric_code",
            "entity_code",
            "entity_name",
            "condition_field",
            "condition_operator",
            "acknowledgement_notes",
            "resolution_notes",
            "suppression_reason",
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

        self.rule_code = self.rule_code.upper()
        self.metric_code = self.metric_code.upper()
        self.entity_code = self.entity_code.upper()
        self.error_code = self.error_code.upper()

        if not self.rule_id:
            raise ValidationError(
                {
                    "rule": (
                        "La regla es obligatoria."
                    ),
                }
            )

        if not self.title:
            raise ValidationError(
                {
                    "title": (
                        "El título es obligatorio."
                    ),
                }
            )

        if not self.message:
            raise ValidationError(
                {
                    "message": (
                        "El mensaje es obligatorio."
                    ),
                }
            )

        if (
            self.customer_id
            and self.branch_id
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
            self.agent_id
            and self.customer_id
            and self.agent.customer_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "agent": (
                        "El agente no pertenece al cliente."
                    ),
                }
            )

        if (
            self.network_id
            and self.agent_id
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
            and self.customer_id
            and self.device.customer_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo no pertenece al cliente."
                    ),
                }
            )

        if (
            self.device_id
            and self.agent_id
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

        related_device_objects = [
            (
                "snapshot",
                self.snapshot,
            ),
            (
                "device_event",
                self.device_event,
            ),
            (
                "device_alert",
                self.device_alert,
            ),
        ]

        for field_name, related_object in related_device_objects:
            if (
                related_object is not None
                and self.device_id
                and related_object.device_id
                != self.device_id
            ):
                raise ValidationError(
                    {
                        field_name: (
                            "El registro relacionado pertenece "
                            "a otro dispositivo."
                        ),
                    }
                )

        if (
            self.agent_sync_id
            and self.agent_id
            and self.agent_sync.agent_id
            != self.agent_id
        ):
            raise ValidationError(
                {
                    "agent_sync": (
                        "La sincronización pertenece a otro agente."
                    ),
                }
            )

        if (
            self.agent_command_id
            and self.agent_id
            and self.agent_command.agent_id
            != self.agent_id
        ):
            raise ValidationError(
                {
                    "agent_command": (
                        "La orden pertenece a otro agente."
                    ),
                }
            )

        if (
            self.duplicate_of_id
            and self.duplicate_of_id == self.id
        ):
            raise ValidationError(
                {
                    "duplicate_of": (
                        "Una notificación no puede duplicarse "
                        "a sí misma."
                    ),
                }
            )

        if self.is_duplicate and not self.duplicate_of_id:
            raise ValidationError(
                {
                    "duplicate_of": (
                        "Debe indicar la notificación original."
                    ),
                }
            )

        if (
            not self.is_duplicate
            and self.duplicate_of_id
        ):
            raise ValidationError(
                {
                    "is_duplicate": (
                        "Debe marcar la notificación como duplicada."
                    ),
                }
            )

        if (
            self.last_detected_at
            < self.first_detected_at
        ):
            raise ValidationError(
                {
                    "last_detected_at": (
                        "La última detección no puede ser anterior "
                        "a la primera."
                    ),
                }
            )

        if (
            self.condition_cleared_at
            and self.condition_started_at
            and self.condition_cleared_at
            < self.condition_started_at
        ):
            raise ValidationError(
                {
                    "condition_cleared_at": (
                        "El fin de la condición no puede ser "
                        "anterior al inicio."
                    ),
                }
            )

        if (
            self.is_acknowledged
            and not self.acknowledged_at
        ):
            raise ValidationError(
                {
                    "acknowledged_at": (
                        "Debe registrar la fecha de reconocimiento."
                    ),
                }
            )

        if (
            self.is_resolved
            and not self.resolved_at
        ):
            raise ValidationError(
                {
                    "resolved_at": (
                        "Debe registrar la fecha de resolución."
                    ),
                }
            )

        if (
            self.is_resolved
            and not self.resolution_type
        ):
            raise ValidationError(
                {
                    "resolution_type": (
                        "Debe indicar el tipo de resolución."
                    ),
                }
            )

        if (
            self.status == self.Status.SUPPRESSED
            and not self.suppression_reason
        ):
            raise ValidationError(
                {
                    "suppression_reason": (
                        "Debe indicar el motivo de supresión."
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

        if (
            self.status == self.Status.FAILED
            and not self.error_message
        ):
            raise ValidationError(
                {
                    "error_message": (
                        "Una notificación fallida debe registrar "
                        "el error."
                    ),
                }
            )

        if (
            self.maximum_notifications is not None
            and self.notification_count
            > self.maximum_notifications
        ):
            raise ValidationError(
                {
                    "notification_count": (
                        "Los envíos no pueden superar el máximo."
                    ),
                }
            )

        allowed_channels = {
            choice[0]
            for choice in self.rule.Channel.choices
        }

        channel_fields = [
            "channels",
            "pending_channels",
            "successful_channels",
            "failed_channels",
        ]

        for field_name in channel_fields:
            value = getattr(
                self,
                field_name,
            )

            if not isinstance(
                value,
                list,
            ):
                raise ValidationError(
                    {
                        field_name: (
                            "Este campo debe ser una lista."
                        ),
                    }
                )

            invalid_channels = [
                channel
                for channel in value
                if channel not in allowed_channels
            ]

            if invalid_channels:
                raise ValidationError(
                    {
                        field_name: (
                            "Existen canales no válidos."
                        ),
                    }
                )

        list_fields = [
            "recipient_user_ids",
            "recipient_role_codes",
            "recipient_emails",
            "recipient_contact_ids",
            "resolved_recipients",
        ]

        for field_name in list_fields:
            if not isinstance(
                getattr(
                    self,
                    field_name,
                ),
                list,
            ):
                raise ValidationError(
                    {
                        field_name: (
                            "Este campo debe ser una lista."
                        ),
                    }
                )

        dict_fields = [
            "condition_data",
            "trigger_data",
            "context_data",
            "channel_results",
            "metadata",
        ]

        for field_name in dict_fields:
            if not isinstance(
                getattr(
                    self,
                    field_name,
                ),
                dict,
            ):
                raise ValidationError(
                    {
                        field_name: (
                            "Este campo debe ser un objeto."
                        ),
                    }
                )

        self.notification_key = (
            self.calculate_notification_key()
        )

    def save(self, *args, **kwargs):
        if self.rule_id:
            self.rule_code = self.rule.code
            self.rule_type = self.rule.rule_type
            self.severity = self.rule.severity
            self.requires_acknowledgement = (
                self.rule.require_acknowledgement
            )
            self.maximum_notifications = (
                self.rule.maximum_notifications
            )

            if not self.channels:
                self.channels = list(
                    self.rule.channels
                )

            if not self.customer_id:
                self.customer = self.rule.customer

            if not self.branch_id:
                self.branch = self.rule.branch

            if not self.agent_id:
                self.agent = self.rule.agent

            if not self.network_id:
                self.network = self.rule.network

            if not self.device_id:
                self.device = self.rule.device

        if self.device_id:
            self.customer = (
                self.customer
                or self.device.customer
            )
            self.branch = (
                self.branch
                or self.device.branch
            )
            self.agent = (
                self.agent
                or self.device.agent
            )
            self.network = (
                self.network
                or self.device.network
            )

        self.rule_code = str(
            self.rule_code or ""
        ).strip().upper()

        self.metric_code = str(
            self.metric_code or ""
        ).strip().upper()

        self.entity_code = str(
            self.entity_code or ""
        ).strip().upper()

        self.channels = [
            str(channel).strip().lower()
            for channel in (
                self.channels
                or []
            )
            if str(channel).strip()
        ]

        self.pending_channels = [
            str(channel).strip().lower()
            for channel in (
                self.pending_channels
                or []
            )
            if str(channel).strip()
        ]

        self.successful_channels = [
            str(channel).strip().lower()
            for channel in (
                self.successful_channels
                or []
            )
            if str(channel).strip()
        ]

        self.failed_channels = [
            str(channel).strip().lower()
            for channel in (
                self.failed_channels
                or []
            )
            if str(channel).strip()
        ]

        self.notification_key = (
            self.calculate_notification_key()
        )

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )