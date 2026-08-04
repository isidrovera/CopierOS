# -*- coding: utf-8 -*-
import hashlib

from django.core.exceptions import ValidationError
from django.db import models

from .base import MonitoringBaseModel


class JobReading(MonitoringBaseModel):
    """
    Lectura histórica de un trabajo publicado por el dispositivo.

    Puede representar trabajos de impresión, copia, escaneo o fax.

    Los datos sensibles, como usuario y nombre del documento,
    pueden almacenarse completos, anonimizados o no almacenarse,
    según la configuración del cliente.
    """

    class JobType(models.TextChoices):
        PRINT = (
            "print",
            "Impresión",
        )
        COPY = (
            "copy",
            "Copia",
        )
        SCAN = (
            "scan",
            "Escaneo",
        )
        FAX_SEND = (
            "fax_send",
            "Envío de fax",
        )
        FAX_RECEIVE = (
            "fax_receive",
            "Recepción de fax",
        )
        OTHER = (
            "other",
            "Otro",
        )
        UNKNOWN = (
            "unknown",
            "Sin identificar",
        )

    class Status(models.TextChoices):
        UNKNOWN = (
            "unknown",
            "Desconocido",
        )
        QUEUED = (
            "queued",
            "En cola",
        )
        PROCESSING = (
            "processing",
            "Procesando",
        )
        PRINTING = (
            "printing",
            "Imprimiendo",
        )
        SCANNING = (
            "scanning",
            "Escaneando",
        )
        SENDING = (
            "sending",
            "Enviando",
        )
        RECEIVING = (
            "receiving",
            "Recibiendo",
        )
        HELD = (
            "held",
            "Retenido",
        )
        PAUSED = (
            "paused",
            "Pausado",
        )
        COMPLETED = (
            "completed",
            "Completado",
        )
        CANCELLED = (
            "cancelled",
            "Cancelado",
        )
        ERROR = (
            "error",
            "Con error",
        )
        DELETED = (
            "deleted",
            "Eliminado",
        )

    class ColorMode(models.TextChoices):
        BLACK = (
            "black",
            "Blanco y negro",
        )
        COLOR = (
            "color",
            "Color",
        )
        AUTO = (
            "auto",
            "Automático",
        )
        MIXED = (
            "mixed",
            "Mixto",
        )
        UNKNOWN = (
            "unknown",
            "No identificado",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )

    class SidesMode(models.TextChoices):
        SIMPLEX = (
            "simplex",
            "Una cara",
        )
        DUPLEX = (
            "duplex",
            "Doble cara",
        )
        MIXED = (
            "mixed",
            "Mixto",
        )
        UNKNOWN = (
            "unknown",
            "No identificado",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )

    class PrivacyMode(models.TextChoices):
        FULL = (
            "full",
            "Información completa",
        )
        ANONYMIZED = (
            "anonymized",
            "Información anonimizada",
        )
        OMITTED = (
            "omitted",
            "Información omitida",
        )

    snapshot = models.ForeignKey(
        "monitoring.DeviceSnapshot",
        on_delete=models.PROTECT,
        related_name="job_readings",
        verbose_name="Captura",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        on_delete=models.PROTECT,
        related_name="job_readings",
        verbose_name="Dispositivo",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_job_readings",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_job_readings",
        verbose_name="Sede",
    )

    captured_at = models.DateTimeField(
        db_index=True,
        verbose_name="Fecha de lectura",
    )

    job_key = models.CharField(
        max_length=64,
        db_index=True,
        editable=False,
        verbose_name="Clave del trabajo",
    )

    vendor_job_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Identificador original",
    )

    queue_position = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Posición en cola",
    )

    job_type = models.CharField(
        max_length=30,
        choices=JobType.choices,
        default=JobType.UNKNOWN,
        db_index=True,
        verbose_name="Tipo de trabajo",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.UNKNOWN,
        db_index=True,
        verbose_name="Estado",
    )

    raw_status = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Estado original",
    )

    privacy_mode = models.CharField(
        max_length=20,
        choices=PrivacyMode.choices,
        default=PrivacyMode.OMITTED,
        db_index=True,
        verbose_name="Tratamiento de privacidad",
    )

    username = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Usuario",
    )

    username_hash = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        editable=False,
        verbose_name="Huella del usuario",
    )

    department_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de departamento",
    )

    document_name = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Nombre del documento",
    )

    document_name_hash = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        editable=False,
        verbose_name="Huella del documento",
    )

    source_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Origen del trabajo",
    )

    destination_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Destino del trabajo",
    )

    color_mode = models.CharField(
        max_length=30,
        choices=ColorMode.choices,
        default=ColorMode.UNKNOWN,
        db_index=True,
        verbose_name="Modo de color",
    )

    sides_mode = models.CharField(
        max_length=30,
        choices=SidesMode.choices,
        default=SidesMode.UNKNOWN,
        db_index=True,
        verbose_name="Caras",
    )

    requested_copies = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Copias solicitadas",
    )

    completed_copies = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Copias completadas",
    )

    total_pages = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Total de páginas",
    )

    completed_pages = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Páginas completadas",
    )

    black_pages = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Páginas blanco y negro",
    )

    color_pages = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Páginas color",
    )

    paper_size = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Formato de papel",
    )

    media_type = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Tipo de papel",
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de envío",
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

    duration_seconds = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración",
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

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Trabajo activo",
    )

    is_completed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Trabajo completado",
    )

    is_cancelled = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Trabajo cancelado",
    )

    has_error = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Trabajo con error",
    )

    oid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="OID principal",
    )

    oid_index = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Índice OID",
    )

    raw_value = models.TextField(
        blank=True,
        verbose_name="Valor original",
    )

    extra_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Información adicional",
    )

    is_visible_in_reports = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Visible en reportes",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Lectura de trabajo"
        verbose_name_plural = "Lecturas de trabajos"
        ordering = (
            "-captured_at",
            "queue_position",
        )
        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "captured_at",
                    "job_type",
                ],
                name="mon_job_customer_date_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "status",
                    "captured_at",
                ],
                name="mon_job_device_status_idx",
            ),
            models.Index(
                fields=[
                    "username_hash",
                    "captured_at",
                ],
                name="mon_job_user_date_idx",
            ),
            models.Index(
                fields=[
                    "department_code",
                    "captured_at",
                ],
                name="mon_job_department_idx",
            ),
            models.Index(
                fields=[
                    "has_error",
                    "is_cancelled",
                    "captured_at",
                ],
                name="mon_job_result_date_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "snapshot",
                    "job_key",
                ],
                name="unique_snapshot_job",
            ),
        ]

    def __str__(self):
        return (
            f"{self.device} - "
            f"{self.job_type} - "
            f"{self.status}"
        )

    @staticmethod
    def calculate_hash(value):
        normalized = str(
            value or ""
        ).strip().lower()

        if not normalized:
            return ""

        return hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()

    def calculate_job_key(self):
        values = [
            str(self.device_id or ""),
            str(self.vendor_job_id or "").strip(),
            str(self.oid_index or "").strip(),
            str(self.submitted_at or ""),
            str(self.document_name_hash or ""),
            str(self.username_hash or ""),
        ]

        return hashlib.sha256(
            "|".join(values).encode("utf-8")
        ).hexdigest()

    def apply_privacy(self):
        original_username = str(
            self.username or ""
        ).strip()

        original_document = str(
            self.document_name or ""
        ).strip()

        self.username_hash = self.calculate_hash(
            original_username
        )

        self.document_name_hash = self.calculate_hash(
            original_document
        )

        if self.privacy_mode == self.PrivacyMode.ANONYMIZED:
            self.username = ""
            self.document_name = ""

        if self.privacy_mode == self.PrivacyMode.OMITTED:
            self.username = ""
            self.username_hash = ""
            self.document_name = ""
            self.document_name_hash = ""
            self.source_name = ""
            self.destination_name = ""

    def calculate_result_flags(self):
        completed_statuses = {
            self.Status.COMPLETED,
            self.Status.CANCELLED,
            self.Status.ERROR,
            self.Status.DELETED,
        }

        self.is_active = self.status not in completed_statuses
        self.is_completed = self.status == self.Status.COMPLETED
        self.is_cancelled = self.status == self.Status.CANCELLED
        self.has_error = self.status == self.Status.ERROR

        if self.error_code or self.error_message:
            self.has_error = True

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
            "vendor_job_id",
            "raw_status",
            "username",
            "department_code",
            "document_name",
            "source_name",
            "destination_name",
            "paper_size",
            "media_type",
            "error_code",
            "error_message",
            "oid",
            "oid_index",
            "raw_value",
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

        self.department_code = self.department_code.upper()
        self.paper_size = self.paper_size.upper()
        self.error_code = self.error_code.upper()

        if not self.snapshot_id:
            raise ValidationError(
                {
                    "snapshot": "La captura es obligatoria.",
                }
            )

        if self.snapshot.device_id != self.device_id:
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo no coincide con la captura."
                    ),
                }
            )

        if self.snapshot.customer_id != self.customer_id:
            raise ValidationError(
                {
                    "customer": (
                        "El cliente no coincide con la captura."
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
            self.started_at
            and self.submitted_at
            and self.started_at < self.submitted_at
        ):
            raise ValidationError(
                {
                    "started_at": (
                        "El inicio no puede ser anterior "
                        "al envío del trabajo."
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
                        "al inicio del trabajo."
                    ),
                }
            )

        if (
            self.completed_pages is not None
            and self.total_pages is not None
            and self.completed_pages > self.total_pages
        ):
            raise ValidationError(
                {
                    "completed_pages": (
                        "Las páginas completadas no pueden superar "
                        "el total de páginas."
                    ),
                }
            )

        if (
            self.black_pages is not None
            and self.color_pages is not None
            and self.total_pages is not None
            and self.black_pages + self.color_pages
            > self.total_pages
        ):
            raise ValidationError(
                {
                    "total_pages": (
                        "La suma de páginas B/N y color no puede "
                        "superar el total."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        if self.snapshot_id:
            self.device = self.snapshot.device
            self.customer = self.snapshot.customer
            self.branch = self.snapshot.branch
            self.captured_at = self.snapshot.captured_at

        self.apply_privacy()
        self.calculate_result_flags()
        self.calculate_duration()

        self.job_key = self.calculate_job_key()

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
            "Las lecturas históricas no pueden archivarse."
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        raise ValidationError(
            "Las lecturas históricas no pueden restaurarse."
        )