# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
)
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .employee_profile import EmployeeProfile


class AttendanceNotification(models.Model):
    """
    Notificación generada por el módulo de asistencia.

    Puede informar sobre:

    - Tardanzas.
    - Ausencias.
    - Marcaciones incompletas.
    - Incidencias.
    - Solicitudes de permisos.
    - Correcciones.
    - Horas extras.
    - Sesiones operativas.
    - Aprobaciones pendientes.
    - Documentos por vencer.
    - Compensaciones pendientes.
    - Cierres diarios.
    - Cierres mensuales.
    - Errores de procesamiento.

    La notificación puede dirigirse al trabajador, supervisor,
    recursos humanos, gerencia u otro usuario específico.
    """

    class NotificationType(models.TextChoices):
        LATE_ARRIVAL = (
            "late_arrival",
            "Tardanza",
        )
        ABSENCE = (
            "absence",
            "Ausencia",
        )
        INCOMPLETE_CLOCKING = (
            "incomplete_clocking",
            "Marcación incompleta",
        )
        LOCATION_INCIDENT = (
            "location_incident",
            "Incidencia de ubicación",
        )
        DEVICE_INCIDENT = (
            "device_incident",
            "Incidencia de dispositivo",
        )
        ATTENDANCE_INCIDENT = (
            "attendance_incident",
            "Incidencia de asistencia",
        )
        JUSTIFICATION_REQUIRED = (
            "justification_required",
            "Justificación requerida",
        )
        JUSTIFICATION_DUE = (
            "justification_due",
            "Justificación por vencer",
        )
        JUSTIFICATION_OVERDUE = (
            "justification_overdue",
            "Justificación vencida",
        )
        LEAVE_SUBMITTED = (
            "leave_submitted",
            "Permiso presentado",
        )
        LEAVE_APPROVED = (
            "leave_approved",
            "Permiso aprobado",
        )
        LEAVE_REJECTED = (
            "leave_rejected",
            "Permiso rechazado",
        )
        LEAVE_CANCELLED = (
            "leave_cancelled",
            "Permiso cancelado",
        )
        CORRECTION_SUBMITTED = (
            "correction_submitted",
            "Corrección presentada",
        )
        CORRECTION_APPROVED = (
            "correction_approved",
            "Corrección aprobada",
        )
        CORRECTION_REJECTED = (
            "correction_rejected",
            "Corrección rechazada",
        )
        CORRECTION_APPLIED = (
            "correction_applied",
            "Corrección aplicada",
        )
        CORRECTION_ERROR = (
            "correction_error",
            "Error al aplicar corrección",
        )
        OVERTIME_SUBMITTED = (
            "overtime_submitted",
            "Horas extras presentadas",
        )
        OVERTIME_APPROVED = (
            "overtime_approved",
            "Horas extras aprobadas",
        )
        OVERTIME_REJECTED = (
            "overtime_rejected",
            "Horas extras rechazadas",
        )
        OVERTIME_VERIFICATION = (
            "overtime_verification",
            "Horas extras por verificar",
        )
        OVERTIME_VERIFIED = (
            "overtime_verified",
            "Horas extras verificadas",
        )
        COMPENSATION_PENDING = (
            "compensation_pending",
            "Compensación pendiente",
        )
        COMPENSATION_DUE = (
            "compensation_due",
            "Compensación por vencer",
        )
        POLICY_ASSIGNED = (
            "policy_assigned",
            "Política asignada",
        )
        POLICY_CHANGED = (
            "policy_changed",
            "Política modificada",
        )
        SCHEDULE_ASSIGNED = (
            "schedule_assigned",
            "Horario asignado",
        )
        SCHEDULE_CHANGED = (
            "schedule_changed",
            "Horario modificado",
        )
        DEVICE_AUTHORIZED = (
            "device_authorized",
            "Dispositivo autorizado",
        )
        DEVICE_REVOKED = (
            "device_revoked",
            "Dispositivo revocado",
        )
        OPERATIONAL_SESSION_ASSIGNED = (
            "operational_session_assigned",
            "Sesión operativa asignada",
        )
        OPERATIONAL_SESSION_REVIEW = (
            "operational_session_review",
            "Sesión operativa por revisar",
        )
        DAILY_REVIEW_REQUIRED = (
            "daily_review_required",
            "Asistencia diaria por revisar",
        )
        DAILY_ATTENDANCE_CLOSED = (
            "daily_attendance_closed",
            "Asistencia diaria cerrada",
        )
        MONTHLY_REVIEW_REQUIRED = (
            "monthly_review_required",
            "Resumen mensual por revisar",
        )
        MONTHLY_SUMMARY_APPROVED = (
            "monthly_summary_approved",
            "Resumen mensual aprobado",
        )
        MONTHLY_SUMMARY_CLOSED = (
            "monthly_summary_closed",
            "Resumen mensual cerrado",
        )
        PROCESSING_ERROR = (
            "processing_error",
            "Error de procesamiento",
        )
        APPROVAL_PENDING = (
            "approval_pending",
            "Aprobación pendiente",
        )
        DEADLINE_REMINDER = (
            "deadline_reminder",
            "Recordatorio de vencimiento",
        )
        GENERAL = (
            "general",
            "Notificación general",
        )

    class RecipientType(models.TextChoices):
        EMPLOYEE = (
            "employee",
            "Trabajador",
        )
        SUPERVISOR = (
            "supervisor",
            "Supervisor",
        )
        HUMAN_RESOURCES = (
            "human_resources",
            "Recursos humanos",
        )
        MANAGEMENT = (
            "management",
            "Gerencia",
        )
        ADMINISTRATOR = (
            "administrator",
            "Administrador",
        )
        SPECIFIC_USER = (
            "specific_user",
            "Usuario específico",
        )
        SYSTEM = (
            "system",
            "Sistema",
        )

    class Priority(models.TextChoices):
        LOW = (
            "low",
            "Baja",
        )
        NORMAL = (
            "normal",
            "Normal",
        )
        HIGH = (
            "high",
            "Alta",
        )
        URGENT = (
            "urgent",
            "Urgente",
        )
        CRITICAL = (
            "critical",
            "Crítica",
        )

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        SCHEDULED = (
            "scheduled",
            "Programada",
        )
        PROCESSING = (
            "processing",
            "Procesando",
        )
        SENT = (
            "sent",
            "Enviada",
        )
        PARTIALLY_SENT = (
            "partially_sent",
            "Enviada parcialmente",
        )
        DELIVERED = (
            "delivered",
            "Entregada",
        )
        READ = (
            "read",
            "Leída",
        )
        FAILED = (
            "failed",
            "Fallida",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )
        EXPIRED = (
            "expired",
            "Vencida",
        )

    class Channel(models.TextChoices):
        INTERNAL = (
            "internal",
            "Notificación interna",
        )
        EMAIL = (
            "email",
            "Correo electrónico",
        )
        PUSH = (
            "push",
            "Notificación push",
        )
        WHATSAPP = (
            "whatsapp",
            "WhatsApp",
        )
        SMS = (
            "sms",
            "Mensaje SMS",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="attendance_notifications",
        verbose_name="Destinatario",
    )

    recipient_type = models.CharField(
        max_length=30,
        choices=RecipientType.choices,
        default=RecipientType.SPECIFIC_USER,
        db_index=True,
        verbose_name="Tipo de destinatario",
    )

    employee_profile = models.ForeignKey(
        EmployeeProfile,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_notifications",
        verbose_name="Trabajador relacionado",
    )

    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        db_index=True,
        verbose_name="Tipo de notificación",
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
        db_index=True,
        verbose_name="Prioridad",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Título",
    )

    message = models.TextField(
        verbose_name="Mensaje",
    )

    short_message = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Mensaje corto",
    )

    content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_notifications",
        verbose_name="Tipo de objeto relacionado",
    )

    object_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="ID del objeto relacionado",
    )

    content_object = GenericForeignKey(
        "content_type",
        "object_id",
    )

    object_model = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Modelo relacionado",
    )

    object_representation = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Representación del objeto",
    )

    action_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Ruta de acción",
    )

    action_label = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Texto de acción",
    )

    channels = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Canales solicitados",
    )

    successful_channels = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Canales enviados correctamente",
    )

    failed_channels = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Canales fallidos",
    )

    channel_results = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resultado por canal",
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Programada para",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Vence el",
    )

    processing_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Procesamiento iniciado el",
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Enviada el",
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Entregada el",
    )

    first_read_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Primera lectura",
    )

    last_read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última lectura",
    )

    read_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad de lecturas",
    )

    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fallida el",
    )

    failure_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Cantidad de errores",
    )

    last_error = models.TextField(
        blank=True,
        verbose_name="Último error",
    )

    retry_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Cantidad de reintentos",
    )

    maximum_retries = models.PositiveSmallIntegerField(
        default=3,
        verbose_name="Máximo de reintentos",
    )

    next_retry_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Próximo reintento",
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Cancelada el",
    )

    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_notifications_cancelled",
        verbose_name="Cancelada por",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    is_internal_visible = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Visible internamente",
    )

    is_read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Leída",
    )

    requires_action = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere acción",
    )

    action_completed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Acción completada",
    )

    action_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Acción completada el",
    )

    action_completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_notification_actions_completed",
        verbose_name="Acción completada por",
    )

    deduplication_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        verbose_name="Clave de deduplicación",
    )

    batch_key = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Clave de lote",
    )

    correlation_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="ID de correlación",
    )

    source = models.CharField(
        max_length=100,
        default="attendance",
        db_index=True,
        verbose_name="Origen",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Creado el",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        db_index=True,
        verbose_name="Actualizado el",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_notifications_created",
        verbose_name="Creado por",
    )

    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Archivada el",
    )

    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_notifications_archived",
        verbose_name="Archivada por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Notificación de asistencia"
        verbose_name_plural = "Notificaciones de asistencia"

        ordering = (
            "-created_at",
        )

        indexes = (
            models.Index(
                fields=(
                    "recipient",
                    "is_read",
                    "created_at",
                ),
                name="att_notif_rec_read_idx",
            ),
            models.Index(
                fields=(
                    "recipient",
                    "status",
                    "priority",
                ),
                name="att_notif_rec_status_idx",
            ),
            models.Index(
                fields=(
                    "employee_profile",
                    "notification_type",
                    "created_at",
                ),
                name="att_notif_emp_type_idx",
            ),
            models.Index(
                fields=(
                    "notification_type",
                    "status",
                    "priority",
                ),
                name="att_notif_type_status_idx",
            ),
            models.Index(
                fields=(
                    "content_type",
                    "object_id",
                    "created_at",
                ),
                name="att_notif_object_idx",
            ),
            models.Index(
                fields=(
                    "scheduled_at",
                    "status",
                ),
                name="att_notif_schedule_idx",
            ),
            models.Index(
                fields=(
                    "expires_at",
                    "status",
                ),
                name="att_notif_expire_idx",
            ),
            models.Index(
                fields=(
                    "requires_action",
                    "action_completed",
                    "recipient",
                ),
                name="att_notif_action_idx",
            ),
            models.Index(
                fields=(
                    "next_retry_at",
                    "retry_count",
                    "status",
                ),
                name="att_notif_retry_idx",
            ),
            models.Index(
                fields=(
                    "batch_key",
                    "correlation_id",
                ),
                name="att_notif_batch_corr_idx",
            ),
            models.Index(
                fields=(
                    "is_internal_visible",
                    "archived_at",
                ),
                name="att_notif_visible_arch_idx",
            ),
        )

        constraints = (
            models.CheckConstraint(
                condition=models.Q(
                    retry_count__lte=models.F(
                        "maximum_retries"
                    ),
                ),
                name="att_notif_retry_lte_max",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        failure_count__gte=0,
                    )
                ),
                name="att_notif_failure_positive",
            ),
        )

    def __str__(self):
        return (
            f"{self.recipient} - "
            f"{self.title} - "
            f"{self.get_status_display()}"
        )

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_pending(self):
        return self.status in (
            self.Status.PENDING,
            self.Status.SCHEDULED,
            self.Status.PROCESSING,
        )

    @property
    def is_expired(self):
        return (
            self.expires_at is not None
            and self.expires_at <= timezone.now()
        )

    @property
    def can_retry(self):
        return (
            self.status == self.Status.FAILED
            and self.retry_count < self.maximum_retries
            and not self.is_expired
            and self.archived_at is None
        )

    @property
    def pending_channels(self):
        requested = set(
            self.channels or []
        )

        successful = set(
            self.successful_channels or []
        )

        return list(
            requested - successful
        )

    @property
    def object_reference(self):
        if self.object_model and self.object_id:
            return (
                f"{self.object_model}:"
                f"{self.object_id}"
            )

        return ""

    def clean(self):
        super().clean()

        errors = {}

        if bool(self.content_type_id) != bool(self.object_id):
            errors["object_id"] = (
                "Debes registrar tanto el tipo como el ID "
                "del objeto relacionado."
            )

        if (
            self.employee_profile_id
            and self.employee_profile.archived_at
        ):
            errors["employee_profile"] = (
                "El perfil laboral está archivado."
            )

        if (
            self.recipient_type
            == self.RecipientType.EMPLOYEE
            and self.employee_profile_id
            and self.recipient_id
            != self.employee_profile.user_id
        ):
            errors["recipient"] = (
                "El destinatario no corresponde al trabajador."
            )

        if not self.title.strip():
            errors["title"] = (
                "Debes indicar el título de la notificación."
            )

        if not self.message.strip():
            errors["message"] = (
                "Debes indicar el contenido de la notificación."
            )

        if not isinstance(
            self.channels,
            list,
        ):
            errors["channels"] = (
                "Los canales deben ser una lista."
            )

        if not isinstance(
            self.successful_channels,
            list,
        ):
            errors["successful_channels"] = (
                "Los canales exitosos deben ser una lista."
            )

        if not isinstance(
            self.failed_channels,
            list,
        ):
            errors["failed_channels"] = (
                "Los canales fallidos deben ser una lista."
            )

        if not isinstance(
            self.channel_results,
            dict,
        ):
            errors["channel_results"] = (
                "Los resultados por canal deben ser "
                "un objeto JSON."
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            errors["metadata"] = (
                "Los metadatos deben ser un objeto JSON."
            )

        allowed_channels = set(
            self.Channel.values
        )

        for channel in self.channels:
            if channel not in allowed_channels:
                errors["channels"] = (
                    f"El canal '{channel}' no es válido."
                )
                break

        for channel in self.successful_channels:
            if channel not in self.channels:
                errors["successful_channels"] = (
                    "Un canal exitoso debe formar parte "
                    "de los canales solicitados."
                )
                break

        for channel in self.failed_channels:
            if channel not in self.channels:
                errors["failed_channels"] = (
                    "Un canal fallido debe formar parte "
                    "de los canales solicitados."
                )
                break

        if (
            self.scheduled_at
            and self.expires_at
            and self.expires_at <= self.scheduled_at
        ):
            errors["expires_at"] = (
                "La fecha de vencimiento debe ser posterior "
                "a la fecha programada."
            )

        if (
            self.status == self.Status.SCHEDULED
            and not self.scheduled_at
        ):
            errors["scheduled_at"] = (
                "Una notificación programada debe tener fecha."
            )

        if (
            self.status == self.Status.PROCESSING
            and not self.processing_started_at
        ):
            errors["processing_started_at"] = (
                "Una notificación en proceso debe registrar "
                "cuándo inició el procesamiento."
            )

        if (
            self.status
            in (
                self.Status.SENT,
                self.Status.PARTIALLY_SENT,
                self.Status.DELIVERED,
                self.Status.READ,
            )
            and not self.sent_at
        ):
            errors["sent_at"] = (
                "Una notificación enviada debe tener "
                "fecha de envío."
            )

        if (
            self.status == self.Status.DELIVERED
            and not self.delivered_at
        ):
            errors["delivered_at"] = (
                "Una notificación entregada debe registrar "
                "la fecha de entrega."
            )

        if (
            self.status == self.Status.READ
            and not self.first_read_at
        ):
            errors["first_read_at"] = (
                "Una notificación leída debe registrar "
                "la primera lectura."
            )

        if (
            self.is_read
            and not self.first_read_at
        ):
            errors["first_read_at"] = (
                "Debes registrar cuándo se leyó "
                "la notificación."
            )

        if (
            self.read_count > 0
            and not self.first_read_at
        ):
            errors["read_count"] = (
                "No puede haber lecturas sin fecha "
                "de primera lectura."
            )

        if (
            self.status == self.Status.FAILED
            and not self.last_error.strip()
        ):
            errors["last_error"] = (
                "Una notificación fallida debe registrar "
                "el error."
            )

        if self.retry_count > self.maximum_retries:
            errors["retry_count"] = (
                "Los reintentos no pueden superar "
                "el máximo permitido."
            )

        if (
            self.next_retry_at
            and self.retry_count >= self.maximum_retries
        ):
            errors["next_retry_at"] = (
                "No puedes programar otro reintento porque "
                "se alcanzó el máximo."
            )

        if (
            self.status == self.Status.CANCELLED
            and not self.cancellation_reason.strip()
        ):
            errors["cancellation_reason"] = (
                "Debes indicar el motivo de cancelación."
            )

        if (
            self.requires_action
            and not self.action_url.strip()
        ):
            errors["action_url"] = (
                "Una notificación que requiere acción debe "
                "tener una ruta de acción."
            )

        if (
            self.action_completed
            and not self.action_completed_at
        ):
            errors["action_completed_at"] = (
                "Debes registrar cuándo se completó la acción."
            )

        if (
            self.action_completed_at
            and not self.action_completed_by_id
        ):
            errors["action_completed_by"] = (
                "Debes indicar quién completó la acción."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.title = str(
            self.title or ""
        ).strip()

        self.message = str(
            self.message or ""
        ).strip()

        self.short_message = str(
            self.short_message or ""
        ).strip()

        self.action_url = str(
            self.action_url or ""
        ).strip()

        self.action_label = str(
            self.action_label or ""
        ).strip()

        if self.content_type_id:
            self.object_model = (
                f"{self.content_type.app_label}."
                f"{self.content_type.model}"
            )

        if (
            self.content_object is not None
            and not self.object_representation
        ):
            self.object_representation = str(
                self.content_object
            )[:500]

        if self.is_expired and self.status in (
            self.Status.PENDING,
            self.Status.SCHEDULED,
            self.Status.FAILED,
        ):
            self.status = self.Status.EXPIRED
            self.next_retry_at = None

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def schedule(
        self,
        scheduled_at,
        expires_at=None,
    ):
        if self.status not in (
            self.Status.PENDING,
            self.Status.SCHEDULED,
        ):
            raise ValidationError(
                "La notificación no puede programarse "
                "desde su estado actual."
            )

        if scheduled_at <= timezone.now():
            raise ValidationError(
                "La fecha programada debe ser futura."
            )

        if (
            expires_at
            and expires_at <= scheduled_at
        ):
            raise ValidationError(
                "La fecha de vencimiento debe ser posterior "
                "a la fecha programada."
            )

        self.status = self.Status.SCHEDULED
        self.scheduled_at = scheduled_at
        self.expires_at = expires_at
        self.next_retry_at = None

        self.save(
            update_fields=[
                "status",
                "scheduled_at",
                "expires_at",
                "next_retry_at",
                "updated_at",
            ]
        )

    def start_processing(self):
        if self.status not in (
            self.Status.PENDING,
            self.Status.SCHEDULED,
            self.Status.FAILED,
        ):
            raise ValidationError(
                "La notificación no puede procesarse "
                "desde su estado actual."
            )

        if self.is_expired:
            self.status = self.Status.EXPIRED
            self.next_retry_at = None

            self.save(
                update_fields=[
                    "status",
                    "next_retry_at",
                    "updated_at",
                ]
            )

            raise ValidationError(
                "La notificación se encuentra vencida."
            )

        if (
            self.status == self.Status.SCHEDULED
            and self.scheduled_at
            and self.scheduled_at > timezone.now()
        ):
            raise ValidationError(
                "La notificación todavía no debe enviarse."
            )

        self.status = self.Status.PROCESSING
        self.processing_started_at = timezone.now()
        self.last_error = ""
        self.next_retry_at = None

        self.save(
            update_fields=[
                "status",
                "processing_started_at",
                "last_error",
                "next_retry_at",
                "updated_at",
            ]
        )

    def mark_channel_success(
        self,
        channel,
        result=None,
    ):
        if channel not in self.channels:
            raise ValidationError(
                "El canal no forma parte de la notificación."
            )

        successful = list(
            self.successful_channels or []
        )

        failed = list(
            self.failed_channels or []
        )

        if channel not in successful:
            successful.append(channel)

        if channel in failed:
            failed.remove(channel)

        results = dict(
            self.channel_results or {}
        )

        results[channel] = {
            "success": True,
            "result": result or {},
            "processed_at": timezone.now().isoformat(),
        }

        self.successful_channels = successful
        self.failed_channels = failed
        self.channel_results = results

        self.save(
            update_fields=[
                "successful_channels",
                "failed_channels",
                "channel_results",
                "updated_at",
            ]
        )

    def mark_channel_failure(
        self,
        channel,
        error,
        result=None,
    ):
        if channel not in self.channels:
            raise ValidationError(
                "El canal no forma parte de la notificación."
            )

        error = str(
            error or ""
        ).strip()

        if not error:
            raise ValidationError(
                "Debes indicar el error del canal."
            )

        failed = list(
            self.failed_channels or []
        )

        successful = list(
            self.successful_channels or []
        )

        if channel not in failed:
            failed.append(channel)

        if channel in successful:
            successful.remove(channel)

        results = dict(
            self.channel_results or {}
        )

        results[channel] = {
            "success": False,
            "error": error,
            "result": result or {},
            "processed_at": timezone.now().isoformat(),
        }

        self.failed_channels = failed
        self.successful_channels = successful
        self.channel_results = results
        self.last_error = error

        self.save(
            update_fields=[
                "failed_channels",
                "successful_channels",
                "channel_results",
                "last_error",
                "updated_at",
            ]
        )

    def finalize_delivery(self):
        requested_channels = set(
            self.channels or []
        )

        successful_channels = set(
            self.successful_channels or []
        )

        failed_channels = set(
            self.failed_channels or []
        )

        now = timezone.now()

        if not requested_channels:
            self.status = self.Status.SENT
            self.sent_at = now
            self.processing_started_at = None

        elif requested_channels == successful_channels:
            self.status = self.Status.SENT
            self.sent_at = now
            self.processing_started_at = None
            self.last_error = ""

        elif successful_channels and failed_channels:
            self.status = self.Status.PARTIALLY_SENT
            self.sent_at = now
            self.processing_started_at = None

        else:
            self.status = self.Status.FAILED
            self.failed_at = now
            self.failure_count += 1
            self.processing_started_at = None

        self.save()

    def mark_delivered(self):
        if self.status not in (
            self.Status.SENT,
            self.Status.PARTIALLY_SENT,
            self.Status.DELIVERED,
        ):
            raise ValidationError(
                "Solo una notificación enviada puede "
                "marcarse como entregada."
            )

        self.status = self.Status.DELIVERED
        self.delivered_at = timezone.now()

        if not self.sent_at:
            self.sent_at = self.delivered_at

        self.save(
            update_fields=[
                "status",
                "delivered_at",
                "sent_at",
                "updated_at",
            ]
        )

    def mark_read(self):
        if self.status in (
            self.Status.CANCELLED,
            self.Status.EXPIRED,
        ):
            raise ValidationError(
                "La notificación no puede marcarse como leída."
            )

        now = timezone.now()

        if not self.first_read_at:
            self.first_read_at = now

        self.last_read_at = now
        self.read_count += 1
        self.is_read = True
        self.status = self.Status.READ

        if not self.sent_at:
            self.sent_at = now

        if not self.delivered_at:
            self.delivered_at = now

        self.save(
            update_fields=[
                "first_read_at",
                "last_read_at",
                "read_count",
                "is_read",
                "status",
                "sent_at",
                "delivered_at",
                "updated_at",
            ]
        )

    def mark_unread(self):
        if not self.is_read:
            return

        self.is_read = False

        if self.delivered_at:
            self.status = self.Status.DELIVERED
        elif self.sent_at:
            self.status = self.Status.SENT
        else:
            self.status = self.Status.PENDING

        self.save(
            update_fields=[
                "is_read",
                "status",
                "updated_at",
            ]
        )

    def mark_action_completed(
        self,
        user,
    ):
        if not self.requires_action:
            raise ValidationError(
                "La notificación no requiere ninguna acción."
            )

        if self.action_completed:
            raise ValidationError(
                "La acción ya fue completada."
            )

        self.action_completed = True
        self.action_completed_at = timezone.now()
        self.action_completed_by = user

        self.save(
            update_fields=[
                "action_completed",
                "action_completed_at",
                "action_completed_by",
                "updated_at",
            ]
        )

    def mark_failed(
        self,
        error,
        next_retry_at=None,
    ):
        error = str(
            error or ""
        ).strip()

        if not error:
            raise ValidationError(
                "Debes indicar el error de envío."
            )

        self.failure_count += 1
        self.last_error = error
        self.failed_at = timezone.now()
        self.processing_started_at = None

        if (
            self.retry_count < self.maximum_retries
            and not self.is_expired
        ):
            self.status = self.Status.FAILED
            self.next_retry_at = next_retry_at

        else:
            self.status = self.Status.FAILED
            self.next_retry_at = None

        self.save()

    def prepare_retry(
        self,
        next_retry_at=None,
    ):
        if not self.can_retry:
            raise ValidationError(
                "La notificación no admite otro reintento."
            )

        if (
            next_retry_at
            and next_retry_at <= timezone.now()
        ):
            raise ValidationError(
                "El próximo reintento debe ser futuro."
            )

        self.retry_count += 1
        self.status = (
            self.Status.SCHEDULED
            if next_retry_at
            else self.Status.PENDING
        )
        self.next_retry_at = next_retry_at
        self.scheduled_at = next_retry_at
        self.processing_started_at = None

        self.save()

    def cancel(
        self,
        user,
        reason,
    ):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de cancelación."
            )

        if self.status in (
            self.Status.READ,
            self.Status.CANCELLED,
            self.Status.EXPIRED,
        ):
            raise ValidationError(
                "La notificación ya no puede cancelarse."
            )

        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancelled_by = user
        self.cancellation_reason = reason
        self.next_retry_at = None
        self.processing_started_at = None

        self.save()

    def mark_expired(self):
        if not self.is_expired:
            raise ValidationError(
                "La notificación todavía no ha vencido."
            )

        if self.status in (
            self.Status.READ,
            self.Status.CANCELLED,
            self.Status.EXPIRED,
        ):
            raise ValidationError(
                "La notificación no puede marcarse como vencida."
            )

        self.status = self.Status.EXPIRED
        self.next_retry_at = None
        self.processing_started_at = None

        self.save(
            update_fields=[
                "status",
                "next_retry_at",
                "processing_started_at",
                "updated_at",
            ]
        )

    def archive(
        self,
        user=None,
        reason="",
    ):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de archivado."
            )

        if self.status == self.Status.PROCESSING:
            raise ValidationError(
                "No puedes archivar una notificación "
                "que está procesándose."
            )

        self.archived_at = timezone.now()
        self.archived_by = user
        self.archived_reason = reason

        self.save(
            update_fields=[
                "archived_at",
                "archived_by",
                "archived_reason",
                "updated_at",
            ]
        )

    def restore(
        self,
        user=None,
    ):
        self.archived_at = None
        self.archived_by = None
        self.archived_reason = ""

        self.save(
            update_fields=[
                "archived_at",
                "archived_by",
                "archived_reason",
                "updated_at",
            ]
        )

    @classmethod
    def create_notification(
        cls,
        *,
        recipient,
        notification_type,
        title,
        message,
        employee_profile=None,
        recipient_type=RecipientType.SPECIFIC_USER,
        priority=Priority.NORMAL,
        content_object=None,
        channels=None,
        short_message="",
        action_url="",
        action_label="",
        requires_action=False,
        scheduled_at=None,
        expires_at=None,
        deduplication_key=None,
        batch_key="",
        correlation_id="",
        source="attendance",
        metadata=None,
        created_by=None,
    ):
        """
        Crea una notificación vinculada opcionalmente
        con cualquier objeto del sistema.
        """

        content_type = None
        object_id = ""
        object_representation = ""

        if content_object is not None:
            content_type = (
                ContentType.objects
                .get_for_model(
                    content_object,
                    for_concrete_model=False,
                )
            )

            object_id = str(
                content_object.pk
            )

            object_representation = str(
                content_object
            )[:500]

        selected_channels = (
            channels
            if channels is not None
            else [cls.Channel.INTERNAL]
        )

        notification = cls(
            recipient=recipient,
            recipient_type=recipient_type,
            employee_profile=employee_profile,
            notification_type=notification_type,
            priority=priority,
            title=title,
            message=message,
            short_message=short_message,
            content_type=content_type,
            object_id=object_id,
            object_representation=object_representation,
            action_url=action_url,
            action_label=action_label,
            requires_action=requires_action,
            channels=selected_channels,
            scheduled_at=scheduled_at,
            expires_at=expires_at,
            deduplication_key=deduplication_key,
            batch_key=batch_key,
            correlation_id=correlation_id,
            source=source,
            metadata=metadata or {},
            created_by=created_by,
        )

        if scheduled_at:
            notification.status = cls.Status.SCHEDULED
        else:
            notification.status = cls.Status.PENDING

        notification.save()

        return notification