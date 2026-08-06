# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .attendance_report import AttendanceReport
from .attendance_report_schedule import (
    AttendanceReportSchedule,
)


class AttendanceReportDelivery(models.Model):
    """
    Registro individual de entrega de un reporte de asistencia.

    Cada destinatario y canal debe generar un registro separado.

    Permite controlar:

    - Entrega interna.
    - Correo electrónico.
    - WhatsApp.
    - Notificación push.
    - Enlace de descarga.
    - Estado de envío.
    - Confirmación de entrega.
    - Lectura.
    - Descarga.
    - Vencimiento.
    - Errores.
    - Reintentos.
    - Cancelación.
    - Auditoría del destinatario.

    No genera el reporte. Solo registra la entrega de un
    AttendanceReport ya creado.
    """

    class RecipientType(models.TextChoices):
        USER = (
            "user",
            "Usuario del sistema",
        )
        EMAIL = (
            "email",
            "Correo externo",
        )
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
        OTHER = (
            "other",
            "Otro destinatario",
        )

    class DeliveryChannel(models.TextChoices):
        INTERNAL = (
            "internal",
            "Notificación interna",
        )
        EMAIL = (
            "email",
            "Correo electrónico",
        )
        WHATSAPP = (
            "whatsapp",
            "WhatsApp",
        )
        PUSH = (
            "push",
            "Notificación push",
        )
        DOWNLOAD_LINK = (
            "download_link",
            "Enlace de descarga",
        )
        API = (
            "api",
            "Entrega por API",
        )
        OTHER = (
            "other",
            "Otro canal",
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
        DELIVERED = (
            "delivered",
            "Entregada",
        )
        READ = (
            "read",
            "Leída",
        )
        DOWNLOADED = (
            "downloaded",
            "Descargada",
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

    class FailureType(models.TextChoices):
        NONE = (
            "none",
            "Sin error",
        )
        INVALID_RECIPIENT = (
            "invalid_recipient",
            "Destinatario inválido",
        )
        INVALID_EMAIL = (
            "invalid_email",
            "Correo inválido",
        )
        REPORT_UNAVAILABLE = (
            "report_unavailable",
            "Reporte no disponible",
        )
        REPORT_EXPIRED = (
            "report_expired",
            "Reporte vencido",
        )
        PERMISSION_DENIED = (
            "permission_denied",
            "Permiso denegado",
        )
        PROVIDER_ERROR = (
            "provider_error",
            "Error del proveedor",
        )
        CONNECTION_ERROR = (
            "connection_error",
            "Error de conexión",
        )
        TIMEOUT = (
            "timeout",
            "Tiempo de espera agotado",
        )
        RATE_LIMIT = (
            "rate_limit",
            "Límite de envíos alcanzado",
        )
        TEMPLATE_ERROR = (
            "template_error",
            "Error de plantilla",
        )
        ATTACHMENT_ERROR = (
            "attachment_error",
            "Error de archivo adjunto",
        )
        SYSTEM_ERROR = (
            "system_error",
            "Error del sistema",
        )
        OTHER = (
            "other",
            "Otro error",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    report = models.ForeignKey(
        AttendanceReport,
        on_delete=models.PROTECT,
        related_name="deliveries",
        verbose_name="Reporte",
    )

    report_schedule = models.ForeignKey(
        AttendanceReportSchedule,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deliveries",
        verbose_name="Programación de reporte",
    )

    recipient_type = models.CharField(
        max_length=30,
        choices=RecipientType.choices,
        default=RecipientType.USER,
        db_index=True,
        verbose_name="Tipo de destinatario",
    )

    recipient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_report_deliveries",
        verbose_name="Usuario destinatario",
    )

    employee_profile = models.ForeignKey(
        "attendance.EmployeeProfile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_report_deliveries",
        verbose_name="Trabajador relacionado",
    )

    recipient_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre del destinatario",
    )

    recipient_email = models.EmailField(
        max_length=254,
        blank=True,
        db_index=True,
        verbose_name="Correo del destinatario",
    )

    recipient_phone = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Teléfono del destinatario",
    )

    delivery_channel = models.CharField(
        max_length=30,
        choices=DeliveryChannel.choices,
        db_index=True,
        verbose_name="Canal de entrega",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    subject = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Asunto",
    )

    message = models.TextField(
        blank=True,
        verbose_name="Mensaje",
    )

    attach_report_file = models.BooleanField(
        default=True,
        verbose_name="Adjuntar archivo del reporte",
    )

    include_download_link = models.BooleanField(
        default=True,
        verbose_name="Incluir enlace de descarga",
    )

    download_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="Token de descarga",
    )

    download_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Ruta de descarga",
    )

    download_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Enlace válido hasta",
    )

    maximum_downloads = models.PositiveSmallIntegerField(
        default=5,
        verbose_name="Máximo de descargas",
    )

    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad de descargas",
    )

    first_downloaded_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Primera descarga",
    )

    last_downloaded_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Última descarga",
    )

    last_downloaded_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP de última descarga",
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Programada para",
    )

    processing_started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
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

    provider_name = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Proveedor de envío",
    )

    provider_message_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="ID de mensaje del proveedor",
    )

    provider_status = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Estado del proveedor",
    )

    provider_response = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Respuesta del proveedor",
    )

    failure_type = models.CharField(
        max_length=30,
        choices=FailureType.choices,
        default=FailureType.NONE,
        db_index=True,
        verbose_name="Tipo de error",
    )

    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fallida el",
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

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Entrega válida hasta",
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
        related_name="attendance_report_deliveries_cancelled",
        verbose_name="Cancelada por",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
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
        related_name="attendance_report_deliveries_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_report_deliveries_updated",
        verbose_name="Actualizado por",
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
        related_name="attendance_report_deliveries_archived",
        verbose_name="Archivada por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Entrega de reporte de asistencia"
        verbose_name_plural = (
            "Entregas de reportes de asistencia"
        )

        ordering = (
            "-created_at",
        )

        indexes = (
            models.Index(
                fields=(
                    "report",
                    "status",
                    "delivery_channel",
                ),
                name="att_rdel_report_status_idx",
            ),
            models.Index(
                fields=(
                    "report_schedule",
                    "status",
                    "created_at",
                ),
                name="att_rdel_sched_status_idx",
            ),
            models.Index(
                fields=(
                    "recipient_user",
                    "status",
                    "created_at",
                ),
                name="att_rdel_user_status_idx",
            ),
            models.Index(
                fields=(
                    "employee_profile",
                    "status",
                ),
                name="att_rdel_employee_status_idx",
            ),
            models.Index(
                fields=(
                    "recipient_email",
                    "delivery_channel",
                    "status",
                ),
                name="att_rdel_email_channel_idx",
            ),
            models.Index(
                fields=(
                    "scheduled_at",
                    "status",
                ),
                name="att_rdel_schedule_status_idx",
            ),
            models.Index(
                fields=(
                    "next_retry_at",
                    "retry_count",
                    "status",
                ),
                name="att_rdel_retry_status_idx",
            ),
            models.Index(
                fields=(
                    "provider_name",
                    "provider_message_id",
                ),
                name="att_rdel_provider_msg_idx",
            ),
            models.Index(
                fields=(
                    "download_token",
                    "download_expires_at",
                ),
                name="att_rdel_token_expire_idx",
            ),
            models.Index(
                fields=(
                    "batch_key",
                    "correlation_id",
                ),
                name="att_rdel_batch_corr_idx",
            ),
            models.Index(
                fields=(
                    "failure_type",
                    "failed_at",
                ),
                name="att_rdel_failure_idx",
            ),
        )

        constraints = (
            models.CheckConstraint(
                condition=models.Q(
                    retry_count__lte=models.F(
                        "maximum_retries"
                    ),
                ),
                name="att_rdel_retry_lte_max",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    download_count__lte=models.F(
                        "maximum_downloads"
                    ),
                ),
                name="att_rdel_download_lte_max",
            ),
        )

    def __str__(self):
        recipient = (
            self.recipient_name
            or self.recipient_email
            or str(self.recipient_user)
            or "Sin destinatario"
        )

        return (
            f"{self.report.report_number} - "
            f"{recipient} - "
            f"{self.get_status_display()}"
        )

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_expired(self):
        return (
            self.expires_at is not None
            and self.expires_at <= timezone.now()
        )

    @property
    def is_download_expired(self):
        return (
            self.download_expires_at is not None
            and self.download_expires_at <= timezone.now()
        )

    @property
    def has_download_limit(self):
        return self.maximum_downloads > 0

    @property
    def download_limit_reached(self):
        return (
            self.has_download_limit
            and self.download_count
            >= self.maximum_downloads
        )

    @property
    def can_download(self):
        return (
            self.report.can_download
            and self.include_download_link
            and not self.is_download_expired
            and not self.download_limit_reached
            and self.status
            not in (
                self.Status.CANCELLED,
                self.Status.EXPIRED,
                self.Status.FAILED,
            )
            and self.archived_at is None
        )

    @property
    def can_retry(self):
        return (
            self.status == self.Status.FAILED
            and self.retry_count < self.maximum_retries
            and not self.is_expired
            and self.archived_at is None
        )

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.report_id
            and self.report.archived_at
        ):
            errors["report"] = (
                "El reporte está archivado."
            )

        if (
            self.report_schedule_id
            and self.report_schedule.archived_at
        ):
            errors["report_schedule"] = (
                "La programación está archivada."
            )

        if (
            self.report_schedule_id
            and self.report_id
            and self.report.result_metadata.get(
                "report_schedule_id"
            )
            not in (
                None,
                "",
                str(self.report_schedule_id),
            )
        ):
            errors["report_schedule"] = (
                "La programación no corresponde al reporte."
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
            in (
                self.RecipientType.USER,
                self.RecipientType.SUPERVISOR,
                self.RecipientType.HUMAN_RESOURCES,
                self.RecipientType.MANAGEMENT,
                self.RecipientType.ADMINISTRATOR,
            )
            and not self.recipient_user_id
        ):
            errors["recipient_user"] = (
                "Debes seleccionar el usuario destinatario."
            )

        if (
            self.recipient_type
            == self.RecipientType.EMPLOYEE
            and not self.employee_profile_id
        ):
            errors["employee_profile"] = (
                "Debes seleccionar el trabajador destinatario."
            )

        if (
            self.recipient_type
            == self.RecipientType.EMPLOYEE
            and self.employee_profile_id
            and self.recipient_user_id
            and self.recipient_user_id
            != self.employee_profile.user_id
        ):
            errors["recipient_user"] = (
                "El usuario destinatario no corresponde "
                "al trabajador."
            )

        if (
            self.delivery_channel
            == self.DeliveryChannel.EMAIL
            and not self.recipient_email.strip()
        ):
            errors["recipient_email"] = (
                "Debes indicar el correo del destinatario."
            )

        if (
            self.delivery_channel
            == self.DeliveryChannel.WHATSAPP
            and not self.recipient_phone.strip()
        ):
            errors["recipient_phone"] = (
                "Debes indicar el teléfono del destinatario."
            )

        if (
            self.delivery_channel
            in (
                self.DeliveryChannel.INTERNAL,
                self.DeliveryChannel.PUSH,
            )
            and not self.recipient_user_id
        ):
            errors["recipient_user"] = (
                "Este canal requiere un usuario del sistema."
            )

        if (
            self.attach_report_file
            and self.report_id
            and not self.report.result_file
            and self.status
            in (
                self.Status.PROCESSING,
                self.Status.SENT,
                self.Status.DELIVERED,
                self.Status.READ,
                self.Status.DOWNLOADED,
            )
        ):
            errors["attach_report_file"] = (
                "El reporte todavía no tiene un archivo disponible."
            )

        if (
            self.include_download_link
            and not self.download_url.strip()
            and self.status
            in (
                self.Status.SENT,
                self.Status.DELIVERED,
                self.Status.READ,
                self.Status.DOWNLOADED,
            )
        ):
            errors["download_url"] = (
                "Debes registrar la ruta de descarga."
            )

        if (
            self.download_expires_at
            and self.expires_at
            and self.download_expires_at > self.expires_at
        ):
            errors["download_expires_at"] = (
                "El enlace de descarga no puede vencer después "
                "de la entrega."
            )

        if (
            self.download_count > self.maximum_downloads
            and self.maximum_downloads > 0
        ):
            errors["download_count"] = (
                "La cantidad de descargas supera "
                "el máximo permitido."
            )

        if (
            self.download_count > 0
            and not self.first_downloaded_at
        ):
            errors["first_downloaded_at"] = (
                "Debe registrarse la primera descarga."
            )

        if (
            self.status == self.Status.SCHEDULED
            and not self.scheduled_at
        ):
            errors["scheduled_at"] = (
                "Una entrega programada debe tener fecha."
            )

        if (
            self.status == self.Status.PROCESSING
            and not self.processing_started_at
        ):
            errors["processing_started_at"] = (
                "Una entrega en proceso debe registrar "
                "el inicio del procesamiento."
            )

        if (
            self.status
            in (
                self.Status.SENT,
                self.Status.DELIVERED,
                self.Status.READ,
                self.Status.DOWNLOADED,
            )
            and not self.sent_at
        ):
            errors["sent_at"] = (
                "Una entrega enviada debe registrar "
                "la fecha de envío."
            )

        if (
            self.status
            in (
                self.Status.DELIVERED,
                self.Status.READ,
                self.Status.DOWNLOADED,
            )
            and not self.delivered_at
        ):
            errors["delivered_at"] = (
                "Una entrega confirmada debe registrar "
                "la fecha de entrega."
            )

        if (
            self.status == self.Status.READ
            and not self.first_read_at
        ):
            errors["first_read_at"] = (
                "Una entrega leída debe registrar "
                "la primera lectura."
            )

        if (
            self.status == self.Status.DOWNLOADED
            and not self.first_downloaded_at
        ):
            errors["first_downloaded_at"] = (
                "Una entrega descargada debe registrar "
                "la primera descarga."
            )

        if (
            self.status == self.Status.FAILED
            and not self.last_error.strip()
        ):
            errors["last_error"] = (
                "Una entrega fallida debe registrar el error."
            )

        if (
            self.status == self.Status.FAILED
            and self.failure_type == self.FailureType.NONE
        ):
            errors["failure_type"] = (
                "Debes indicar el tipo de error."
            )

        if (
            self.failure_type != self.FailureType.NONE
            and not self.last_error.strip()
        ):
            errors["last_error"] = (
                "Debes registrar el detalle del error."
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
                "No puedes programar otro reintento."
            )

        if (
            self.status == self.Status.CANCELLED
            and not self.cancellation_reason.strip()
        ):
            errors["cancellation_reason"] = (
                "Debes indicar el motivo de cancelación."
            )

        if not isinstance(
            self.provider_response,
            dict,
        ):
            errors["provider_response"] = (
                "La respuesta del proveedor debe ser "
                "un objeto JSON."
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            errors["metadata"] = (
                "Los metadatos deben ser un objeto JSON."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.recipient_name = str(
            self.recipient_name or ""
        ).strip()

        self.recipient_email = str(
            self.recipient_email or ""
        ).strip().lower()

        self.recipient_phone = str(
            self.recipient_phone or ""
        ).strip()

        self.subject = str(
            self.subject or ""
        ).strip()

        self.message = str(
            self.message or ""
        ).strip()

        self.download_url = str(
            self.download_url or ""
        ).strip()

        self.provider_name = str(
            self.provider_name or ""
        ).strip()

        self.provider_message_id = str(
            self.provider_message_id or ""
        ).strip()

        self.provider_status = str(
            self.provider_status or ""
        ).strip()

        if (
            self.recipient_user_id
            and not self.recipient_name
        ):
            self.recipient_name = str(
                self.recipient_user
            )

        if (
            self.recipient_type
            == self.RecipientType.EMPLOYEE
            and self.employee_profile_id
            and not self.recipient_user_id
        ):
            self.recipient_user = (
                self.employee_profile.user
            )

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
                "La entrega no puede programarse "
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
                "El vencimiento debe ser posterior "
                "a la fecha programada."
            )

        self.status = self.Status.SCHEDULED
        self.scheduled_at = scheduled_at
        self.expires_at = expires_at
        self.next_retry_at = None

        self.save()

    def start_processing(self):
        if self.status not in (
            self.Status.PENDING,
            self.Status.SCHEDULED,
            self.Status.FAILED,
        ):
            raise ValidationError(
                "La entrega no puede procesarse "
                "desde su estado actual."
            )

        if self.is_expired:
            self.status = self.Status.EXPIRED
            self.next_retry_at = None
            self.save()

            raise ValidationError(
                "La entrega se encuentra vencida."
            )

        if (
            self.status == self.Status.SCHEDULED
            and self.scheduled_at
            and self.scheduled_at > timezone.now()
        ):
            raise ValidationError(
                "La entrega todavía no debe procesarse."
            )

        if not self.report.can_download:
            raise ValidationError(
                "El reporte no se encuentra disponible."
            )

        self.status = self.Status.PROCESSING
        self.processing_started_at = timezone.now()
        self.failure_type = self.FailureType.NONE
        self.last_error = ""
        self.next_retry_at = None

        self.save()

    def mark_sent(
        self,
        *,
        provider_name="",
        provider_message_id="",
        provider_status="",
        provider_response=None,
    ):
        if self.status != self.Status.PROCESSING:
            raise ValidationError(
                "Solo una entrega en procesamiento "
                "puede marcarse como enviada."
            )

        now = timezone.now()

        self.status = self.Status.SENT
        self.sent_at = now
        self.processing_started_at = None
        self.provider_name = str(
            provider_name or ""
        ).strip()
        self.provider_message_id = str(
            provider_message_id or ""
        ).strip()
        self.provider_status = str(
            provider_status or ""
        ).strip()
        self.provider_response = provider_response or {}
        self.failure_type = self.FailureType.NONE
        self.last_error = ""
        self.next_retry_at = None

        self.save()

    def mark_delivered(
        self,
        *,
        provider_status="",
        provider_response=None,
    ):
        if self.status not in (
            self.Status.SENT,
            self.Status.DELIVERED,
        ):
            raise ValidationError(
                "Solo una entrega enviada puede "
                "marcarse como entregada."
            )

        now = timezone.now()

        self.status = self.Status.DELIVERED
        self.delivered_at = now

        if not self.sent_at:
            self.sent_at = now

        if provider_status:
            self.provider_status = str(
                provider_status
            ).strip()

        if provider_response is not None:
            self.provider_response = provider_response

        self.save()

    def mark_read(self):
        if self.status in (
            self.Status.CANCELLED,
            self.Status.EXPIRED,
            self.Status.FAILED,
        ):
            raise ValidationError(
                "La entrega no puede marcarse como leída."
            )

        now = timezone.now()

        if not self.sent_at:
            self.sent_at = now

        if not self.delivered_at:
            self.delivered_at = now

        if not self.first_read_at:
            self.first_read_at = now

        self.last_read_at = now
        self.read_count += 1
        self.status = self.Status.READ

        self.save()

    def register_download(
        self,
        *,
        ip_address=None,
    ):
        if not self.can_download:
            raise ValidationError(
                "El reporte no está disponible para descarga."
            )

        now = timezone.now()

        if not self.sent_at:
            self.sent_at = now

        if not self.delivered_at:
            self.delivered_at = now

        if not self.first_downloaded_at:
            self.first_downloaded_at = now

        self.last_downloaded_at = now
        self.last_downloaded_ip = ip_address
        self.download_count += 1
        self.status = self.Status.DOWNLOADED

        self.save()

    def mark_failed(
        self,
        *,
        error,
        failure_type=FailureType.OTHER,
        provider_name="",
        provider_status="",
        provider_response=None,
        next_retry_at=None,
    ):
        error = str(
            error or ""
        ).strip()

        if not error:
            raise ValidationError(
                "Debes indicar el error de entrega."
            )

        if self.status not in (
            self.Status.PENDING,
            self.Status.SCHEDULED,
            self.Status.PROCESSING,
        ):
            raise ValidationError(
                "La entrega no puede marcarse como fallida "
                "desde su estado actual."
            )

        self.status = self.Status.FAILED
        self.failed_at = timezone.now()
        self.failure_type = failure_type
        self.last_error = error
        self.processing_started_at = None
        self.provider_name = str(
            provider_name or ""
        ).strip()
        self.provider_status = str(
            provider_status or ""
        ).strip()
        self.provider_response = provider_response or {}

        if (
            self.retry_count < self.maximum_retries
            and not self.is_expired
        ):
            self.next_retry_at = next_retry_at
        else:
            self.next_retry_at = None

        self.save()

    def prepare_retry(
        self,
        next_retry_at=None,
    ):
        if not self.can_retry:
            raise ValidationError(
                "La entrega no admite otro reintento."
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
        self.scheduled_at = next_retry_at
        self.next_retry_at = next_retry_at
        self.processing_started_at = None
        self.failed_at = None
        self.failure_type = self.FailureType.NONE
        self.last_error = ""

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
            self.Status.DELIVERED,
            self.Status.READ,
            self.Status.DOWNLOADED,
            self.Status.CANCELLED,
            self.Status.EXPIRED,
        ):
            raise ValidationError(
                "La entrega ya no puede cancelarse."
            )

        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancelled_by = user
        self.cancellation_reason = reason
        self.processing_started_at = None
        self.next_retry_at = None
        self.updated_by = user

        self.save()

    def mark_expired(self):
        if not self.is_expired:
            raise ValidationError(
                "La entrega todavía no ha vencido."
            )

        if self.status in (
            self.Status.CANCELLED,
            self.Status.EXPIRED,
            self.Status.DOWNLOADED,
        ):
            raise ValidationError(
                "La entrega no puede marcarse como vencida."
            )

        self.status = self.Status.EXPIRED
        self.processing_started_at = None
        self.next_retry_at = None

        self.save()

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
                "No puedes archivar una entrega "
                "que está procesándose."
            )

        self.archived_at = timezone.now()
        self.archived_by = user
        self.archived_reason = reason
        self.updated_by = user

        self.save()

    def restore(
        self,
        user=None,
    ):
        self.archived_at = None
        self.archived_by = None
        self.archived_reason = ""
        self.updated_by = user

        self.save()

    @classmethod
    def create_delivery(
        cls,
        *,
        report,
        delivery_channel,
        recipient_type=RecipientType.USER,
        recipient_user=None,
        employee_profile=None,
        recipient_name="",
        recipient_email="",
        recipient_phone="",
        report_schedule=None,
        subject="",
        message="",
        attach_report_file=True,
        include_download_link=True,
        download_url="",
        download_expires_at=None,
        maximum_downloads=5,
        scheduled_at=None,
        expires_at=None,
        deduplication_key=None,
        batch_key="",
        correlation_id="",
        metadata=None,
        created_by=None,
    ):
        """
        Crea una entrega individual para un destinatario.
        """

        delivery = cls(
            report=report,
            report_schedule=report_schedule,
            recipient_type=recipient_type,
            recipient_user=recipient_user,
            employee_profile=employee_profile,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            recipient_phone=recipient_phone,
            delivery_channel=delivery_channel,
            subject=subject,
            message=message,
            attach_report_file=attach_report_file,
            include_download_link=include_download_link,
            download_url=download_url,
            download_expires_at=download_expires_at,
            maximum_downloads=maximum_downloads,
            scheduled_at=scheduled_at,
            expires_at=expires_at,
            deduplication_key=deduplication_key,
            batch_key=batch_key,
            correlation_id=correlation_id,
            metadata=metadata or {},
            created_by=created_by,
            updated_by=created_by,
        )

        if scheduled_at:
            delivery.status = cls.Status.SCHEDULED
        else:
            delivery.status = cls.Status.PENDING

        delivery.save()

        return delivery