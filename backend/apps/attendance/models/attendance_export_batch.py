# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class AttendanceExportBatch(models.Model):
    """
    Lote de exportación de información del módulo de asistencia.

    Permite exportar:

    - Marcaciones.
    - Asistencias diarias.
    - Incidencias.
    - Permisos y licencias.
    - Correcciones.
    - Horas extras.
    - Sesiones operativas.
    - Resúmenes mensuales.
    - Información para planilla.
    - Información para evaluación.
    - Datos para sistemas externos.

    Conserva:

    - Periodo exportado.
    - Filtros utilizados.
    - Columnas seleccionadas.
    - Estado del proceso.
    - Progreso.
    - Registros exportados.
    - Archivo resultante.
    - Errores.
    - Descargas.
    - Entregas externas.
    - Reintentos.
    - Auditoría.
    """

    class ExportType(models.TextChoices):
        ATTENDANCE_RECORDS = (
            "attendance_records",
            "Marcaciones de asistencia",
        )
        DAILY_ATTENDANCE = (
            "daily_attendance",
            "Asistencia diaria",
        )
        ATTENDANCE_INCIDENTS = (
            "attendance_incidents",
            "Incidencias de asistencia",
        )
        LEAVE_REQUESTS = (
            "leave_requests",
            "Permisos y licencias",
        )
        ATTENDANCE_CORRECTIONS = (
            "attendance_corrections",
            "Correcciones de asistencia",
        )
        OVERTIME_REQUESTS = (
            "overtime_requests",
            "Horas extras",
        )
        OPERATIONAL_SESSIONS = (
            "operational_sessions",
            "Sesiones operativas",
        )
        OPERATIONAL_EVENTS = (
            "operational_events",
            "Eventos operativos",
        )
        MONTHLY_SUMMARIES = (
            "monthly_summaries",
            "Resúmenes mensuales",
        )
        PAYROLL = (
            "payroll",
            "Información para planilla",
        )
        STAFF_EVALUATION = (
            "staff_evaluation",
            "Información para evaluación",
        )
        EMPLOYEES = (
            "employees",
            "Trabajadores",
        )
        WORK_SCHEDULES = (
            "work_schedules",
            "Horarios",
        )
        DEVICE_USAGE = (
            "device_usage",
            "Uso de dispositivos",
        )
        AUDIT_LOGS = (
            "audit_logs",
            "Registros de auditoría",
        )
        REPORT_DATA = (
            "report_data",
            "Datos de reporte",
        )
        GENERIC = (
            "generic",
            "Exportación genérica",
        )

    class DestinationType(models.TextChoices):
        DOWNLOAD = (
            "download",
            "Descarga manual",
        )
        EMAIL = (
            "email",
            "Correo electrónico",
        )
        INTERNAL_STORAGE = (
            "internal_storage",
            "Almacenamiento interno",
        )
        EXTERNAL_STORAGE = (
            "external_storage",
            "Almacenamiento externo",
        )
        EXTERNAL_API = (
            "external_api",
            "API externa",
        )
        PAYROLL_SYSTEM = (
            "payroll_system",
            "Sistema de planilla",
        )
        ODOO = (
            "odoo",
            "Odoo",
        )
        SFTP = (
            "sftp",
            "Servidor SFTP",
        )
        WEBHOOK = (
            "webhook",
            "Webhook",
        )
        OTHER = (
            "other",
            "Otro destino",
        )

    class FileFormat(models.TextChoices):
        XLSX = (
            "xlsx",
            "Excel",
        )
        CSV = (
            "csv",
            "CSV",
        )
        JSON = (
            "json",
            "JSON",
        )
        PDF = (
            "pdf",
            "PDF",
        )
        XML = (
            "xml",
            "XML",
        )
        TXT = (
            "txt",
            "Texto",
        )
        ZIP = (
            "zip",
            "Archivo comprimido",
        )

    class Status(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        PENDING = (
            "pending",
            "Pendiente",
        )
        QUEUED = (
            "queued",
            "En cola",
        )
        PROCESSING = (
            "processing",
            "Procesando",
        )
        COMPLETED = (
            "completed",
            "Completado",
        )
        PARTIALLY_COMPLETED = (
            "partially_completed",
            "Completado parcialmente",
        )
        DELIVERY_PENDING = (
            "delivery_pending",
            "Entrega pendiente",
        )
        DELIVERING = (
            "delivering",
            "Entregando",
        )
        DELIVERED = (
            "delivered",
            "Entregado",
        )
        DELIVERY_FAILED = (
            "delivery_failed",
            "Error de entrega",
        )
        FAILED = (
            "failed",
            "Fallido",
        )
        CANCEL_REQUESTED = (
            "cancel_requested",
            "Cancelación solicitada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelado",
        )
        EXPIRED = (
            "expired",
            "Vencido",
        )

    class GenerationSource(models.TextChoices):
        USER = (
            "user",
            "Usuario",
        )
        SCHEDULED = (
            "scheduled",
            "Programado",
        )
        API = (
            "api",
            "API",
        )
        SYSTEM = (
            "system",
            "Sistema",
        )
        MANAGEMENT_COMMAND = (
            "management_command",
            "Comando de administración",
        )
        INTEGRATION = (
            "integration",
            "Integración",
        )

    class CompressionType(models.TextChoices):
        NONE = (
            "none",
            "Sin compresión",
        )
        ZIP = (
            "zip",
            "ZIP",
        )
        GZIP = (
            "gzip",
            "GZIP",
        )

    class SensitiveDataMode(models.TextChoices):
        EXCLUDE = (
            "exclude",
            "Excluir datos sensibles",
        )
        MASK = (
            "mask",
            "Ocultar parcialmente",
        )
        INCLUDE = (
            "include",
            "Incluir datos completos",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    batch_number = models.CharField(
        max_length=60,
        unique=True,
        db_index=True,
        verbose_name="Número de lote",
    )

    name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name="Nombre",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    export_type = models.CharField(
        max_length=40,
        choices=ExportType.choices,
        db_index=True,
        verbose_name="Tipo de exportación",
    )

    destination_type = models.CharField(
        max_length=30,
        choices=DestinationType.choices,
        default=DestinationType.DOWNLOAD,
        db_index=True,
        verbose_name="Destino",
    )

    file_format = models.CharField(
        max_length=10,
        choices=FileFormat.choices,
        default=FileFormat.XLSX,
        db_index=True,
        verbose_name="Formato",
    )

    compression_type = models.CharField(
        max_length=10,
        choices=CompressionType.choices,
        default=CompressionType.NONE,
        verbose_name="Compresión",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    generation_source = models.CharField(
        max_length=30,
        choices=GenerationSource.choices,
        default=GenerationSource.USER,
        db_index=True,
        verbose_name="Origen de generación",
    )

    processing_run = models.ForeignKey(
        "attendance.AttendanceProcessingRun",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="export_batches",
        verbose_name="Ejecución de procesamiento",
    )

    report = models.ForeignKey(
        "attendance.AttendanceReport",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="export_batches",
        verbose_name="Reporte relacionado",
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha inicial",
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha final",
    )

    year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Año",
    )

    month = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Mes",
    )

    timezone_name = models.CharField(
        max_length=100,
        default="America/Lima",
        verbose_name="Zona horaria",
    )

    employee_profiles = models.ManyToManyField(
        "attendance.EmployeeProfile",
        blank=True,
        related_name="export_batches",
        verbose_name="Trabajadores",
    )

    work_locations = models.ManyToManyField(
        "attendance.WorkLocation",
        blank=True,
        related_name="export_batches",
        verbose_name="Ubicaciones",
    )

    work_schedules = models.ManyToManyField(
        "attendance.WorkSchedule",
        blank=True,
        related_name="export_batches",
        verbose_name="Horarios",
    )

    company_names = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Empresas",
    )

    department_names = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Áreas o departamentos",
    )

    job_titles = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Cargos",
    )

    filters = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Filtros",
    )

    selected_columns = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Columnas seleccionadas",
    )

    column_labels = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Etiquetas de columnas",
    )

    ordering_fields = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Ordenamiento",
    )

    grouping_fields = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Agrupación",
    )

    transformation_rules = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Reglas de transformación",
    )

    export_options = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Opciones de exportación",
    )

    include_headers = models.BooleanField(
        default=True,
        verbose_name="Incluir encabezados",
    )

    include_summary = models.BooleanField(
        default=True,
        verbose_name="Incluir resumen",
    )

    include_details = models.BooleanField(
        default=True,
        verbose_name="Incluir detalle",
    )

    include_archived = models.BooleanField(
        default=False,
        verbose_name="Incluir archivados",
    )

    include_empty_values = models.BooleanField(
        default=True,
        verbose_name="Incluir valores vacíos",
    )

    sensitive_data_mode = models.CharField(
        max_length=20,
        choices=SensitiveDataMode.choices,
        default=SensitiveDataMode.MASK,
        db_index=True,
        verbose_name="Tratamiento de datos sensibles",
    )

    password_protected = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Archivo protegido",
    )

    encrypted_password = models.TextField(
        blank=True,
        verbose_name="Contraseña cifrada",
        help_text=(
            "La contraseña debe almacenarse cifrada. "
            "No debe guardarse en texto plano."
        ),
    )

    requested_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Solicitado el",
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_export_batches_requested",
        verbose_name="Solicitado por",
    )

    queued_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Enviado a cola el",
    )

    processing_started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Procesamiento iniciado el",
    )

    processing_finished_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Procesamiento finalizado el",
    )

    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Porcentaje de avance",
    )

    current_stage = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Etapa actual",
    )

    total_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Total de registros",
    )

    processed_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Registros procesados",
    )

    exported_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Registros exportados",
    )

    skipped_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Registros omitidos",
    )

    warning_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Registros con observaciones",
    )

    failed_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Registros fallidos",
    )

    result_file = models.FileField(
        upload_to="attendance/exports/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Archivo exportado",
    )

    result_file_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre del archivo",
    )

    result_file_extension = models.CharField(
        max_length=20,
        blank=True,
        db_index=True,
        verbose_name="Extensión",
    )

    result_mime_type = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Tipo MIME",
    )

    result_file_size = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Tamaño del archivo",
    )

    result_checksum = models.CharField(
        max_length=128,
        blank=True,
        db_index=True,
        verbose_name="Checksum",
    )

    result_summary = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resumen del resultado",
    )

    result_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos del resultado",
    )

    temporary_file_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Ruta temporal",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Disponible hasta",
    )

    download_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="Token de descarga",
    )

    maximum_downloads = models.PositiveSmallIntegerField(
        default=10,
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

    last_downloaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_export_batches_downloaded",
        verbose_name="Última descarga por",
    )

    last_downloaded_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP de última descarga",
    )

    delivery_started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Entrega iniciada el",
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Entregado el",
    )

    destination_reference = models.CharField(
        max_length=500,
        blank=True,
        db_index=True,
        verbose_name="Referencia del destino",
    )

    destination_configuration = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Configuración del destino",
    )

    delivery_response = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Respuesta de entrega",
    )

    external_delivery_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="ID externo de entrega",
    )

    error_code = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Código de error",
    )

    error_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de error",
    )

    exception_type = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Tipo de excepción",
    )

    stack_trace = models.TextField(
        blank=True,
        verbose_name="Traza del error",
    )

    warnings = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Advertencias",
    )

    errors = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Errores",
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

    cancel_requested_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Cancelación solicitada el",
    )

    cancel_requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_export_batches_cancel_requested",
        verbose_name="Cancelación solicitada por",
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Cancelado el",
    )

    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_export_batches_cancelled",
        verbose_name="Cancelado por",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    idempotency_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        verbose_name="Clave de idempotencia",
    )

    batch_key = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Clave de agrupación",
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

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
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
        related_name="attendance_export_batches_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_export_batches_updated",
        verbose_name="Actualizado por",
    )

    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Archivado el",
    )

    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_export_batches_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Lote de exportación de asistencia"
        verbose_name_plural = (
            "Lotes de exportación de asistencia"
        )

        ordering = (
            "-created_at",
        )

        constraints = (
            models.CheckConstraint(
                condition=(
                    models.Q(
                        progress_percentage__gte=0,
                    )
                    & models.Q(
                        progress_percentage__lte=100,
                    )
                ),
                name="att_exp_progress_range",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    processed_records__lte=models.F(
                        "total_records"
                    ),
                ),
                name="att_exp_processed_lte_total",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    exported_records__lte=models.F(
                        "processed_records"
                    ),
                ),
                name="att_exp_exported_lte_proc",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    skipped_records__lte=models.F(
                        "total_records"
                    ),
                ),
                name="att_exp_skipped_lte_total",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    retry_count__lte=models.F(
                        "maximum_retries"
                    ),
                ),
                name="att_exp_retry_lte_max",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        maximum_downloads=0,
                    )
                    | models.Q(
                        download_count__lte=models.F(
                            "maximum_downloads"
                        ),
                    )
                ),
                name="att_exp_download_lte_max",
            ),
        )

        indexes = (
            models.Index(
                fields=(
                    "export_type",
                    "status",
                    "created_at",
                ),
                name="att_exp_type_status_idx",
            ),
            models.Index(
                fields=(
                    "destination_type",
                    "status",
                    "created_at",
                ),
                name="att_exp_dest_status_idx",
            ),
            models.Index(
                fields=(
                    "file_format",
                    "compression_type",
                    "status",
                ),
                name="att_exp_format_status_idx",
            ),
            models.Index(
                fields=(
                    "requested_by",
                    "requested_at",
                    "status",
                ),
                name="att_exp_requested_idx",
            ),
            models.Index(
                fields=(
                    "processing_run",
                    "status",
                ),
                name="att_exp_process_status_idx",
            ),
            models.Index(
                fields=(
                    "report",
                    "status",
                ),
                name="att_exp_report_status_idx",
            ),
            models.Index(
                fields=(
                    "start_date",
                    "end_date",
                    "export_type",
                ),
                name="att_exp_period_idx",
            ),
            models.Index(
                fields=(
                    "year",
                    "month",
                    "export_type",
                ),
                name="att_exp_month_idx",
            ),
            models.Index(
                fields=(
                    "processing_started_at",
                    "processing_finished_at",
                ),
                name="att_exp_processing_idx",
            ),
            models.Index(
                fields=(
                    "delivery_started_at",
                    "delivered_at",
                    "status",
                ),
                name="att_exp_delivery_idx",
            ),
            models.Index(
                fields=(
                    "expires_at",
                    "status",
                ),
                name="att_exp_expire_idx",
            ),
            models.Index(
                fields=(
                    "next_retry_at",
                    "retry_count",
                    "status",
                ),
                name="att_exp_retry_idx",
            ),
            models.Index(
                fields=(
                    "external_delivery_id",
                    "destination_type",
                ),
                name="att_exp_external_idx",
            ),
            models.Index(
                fields=(
                    "batch_key",
                    "correlation_id",
                ),
                name="att_exp_batch_corr_idx",
            ),
            models.Index(
                fields=(
                    "sensitive_data_mode",
                    "password_protected",
                ),
                name="att_exp_sensitive_idx",
            ),
        )

    def __str__(self):
        return (
            f"{self.batch_number} - "
            f"{self.name} - "
            f"{self.get_status_display()}"
        )

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_finished(self):
        return self.status in (
            self.Status.COMPLETED,
            self.Status.PARTIALLY_COMPLETED,
            self.Status.DELIVERED,
            self.Status.DELIVERY_FAILED,
            self.Status.FAILED,
            self.Status.CANCELLED,
            self.Status.EXPIRED,
        )

    @property
    def is_expired(self):
        return (
            self.expires_at is not None
            and self.expires_at <= timezone.now()
        )

    @property
    def download_limit_reached(self):
        return (
            self.maximum_downloads > 0
            and self.download_count >= self.maximum_downloads
        )

    @property
    def can_download(self):
        return (
            self.status in (
                self.Status.COMPLETED,
                self.Status.PARTIALLY_COMPLETED,
                self.Status.DELIVERY_PENDING,
                self.Status.DELIVERING,
                self.Status.DELIVERED,
                self.Status.DELIVERY_FAILED,
            )
            and bool(self.result_file)
            and not self.is_expired
            and not self.download_limit_reached
            and self.archived_at is None
        )

    @property
    def can_retry(self):
        return (
            self.status in (
                self.Status.FAILED,
                self.Status.DELIVERY_FAILED,
            )
            and self.retry_count < self.maximum_retries
            and not self.is_expired
            and self.archived_at is None
        )

    @property
    def success_percentage(self):
        if self.processed_records <= 0:
            return 0

        return round(
            (
                self.exported_records
                / self.processed_records
            )
            * 100,
            2,
        )

    def calculate_progress(self):
        if self.total_records <= 0:
            self.progress_percentage = 0
            return self.progress_percentage

        completed_records = min(
            self.total_records,
            (
                self.processed_records
                + self.skipped_records
            ),
        )

        self.progress_percentage = min(
            100,
            round(
                (
                    completed_records
                    / self.total_records
                )
                * 100,
                2,
            ),
        )

        return self.progress_percentage

    def clean(self):
        super().clean()

        errors = {}

        if not self.name.strip():
            errors["name"] = (
                "Debes indicar el nombre de la exportación."
            )

        if (
            self.start_date
            and self.end_date
            and self.end_date < self.start_date
        ):
            errors["end_date"] = (
                "La fecha final no puede ser anterior "
                "a la fecha inicial."
            )

        if self.month is not None:
            if self.month < 1 or self.month > 12:
                errors["month"] = (
                    "El mes debe estar entre 1 y 12."
                )

            if self.year is None:
                errors["year"] = (
                    "Debes indicar el año junto con el mes."
                )

        if (
            self.processing_run_id
            and self.processing_run.archived_at
        ):
            errors["processing_run"] = (
                "La ejecución de procesamiento está archivada."
            )

        if (
            self.report_id
            and self.report.archived_at
        ):
            errors["report"] = (
                "El reporte relacionado está archivado."
            )

        json_list_fields = (
            "company_names",
            "department_names",
            "job_titles",
            "selected_columns",
            "ordering_fields",
            "grouping_fields",
            "warnings",
            "errors",
        )

        for field_name in json_list_fields:
            if not isinstance(
                getattr(self, field_name),
                list,
            ):
                errors[field_name] = (
                    "El valor debe ser una lista JSON."
                )

        json_object_fields = (
            "filters",
            "column_labels",
            "transformation_rules",
            "export_options",
            "result_summary",
            "result_metadata",
            "destination_configuration",
            "delivery_response",
            "metadata",
        )

        for field_name in json_object_fields:
            if not isinstance(
                getattr(self, field_name),
                dict,
            ):
                errors[field_name] = (
                    "El valor debe ser un objeto JSON."
                )

        if (
            not self.include_details
            and not self.include_summary
        ):
            errors["include_details"] = (
                "La exportación debe incluir detalle "
                "o resumen."
            )

        if (
            self.sensitive_data_mode
            == self.SensitiveDataMode.INCLUDE
            and not self.password_protected
            and self.destination_type
            not in (
                self.DestinationType.INTERNAL_STORAGE,
                self.DestinationType.DOWNLOAD,
            )
        ):
            errors["password_protected"] = (
                "Una exportación externa con datos sensibles "
                "debe protegerse con contraseña."
            )

        if (
            self.password_protected
            and not self.encrypted_password.strip()
        ):
            errors["encrypted_password"] = (
                "Debes registrar la contraseña cifrada."
            )

        if (
            not self.password_protected
            and self.encrypted_password.strip()
        ):
            errors["encrypted_password"] = (
                "No debe existir una contraseña cuando "
                "la protección está desactivada."
            )

        if self.processed_records > self.total_records:
            errors["processed_records"] = (
                "Los registros procesados no pueden superar "
                "el total."
            )

        if (
            self.exported_records
            > self.processed_records
        ):
            errors["exported_records"] = (
                "Los registros exportados no pueden superar "
                "los procesados."
            )

        if self.skipped_records > self.total_records:
            errors["skipped_records"] = (
                "Los registros omitidos no pueden superar "
                "el total."
            )

        if (
            self.warning_records
            > self.processed_records
        ):
            errors["warning_records"] = (
                "Los registros observados no pueden superar "
                "los procesados."
            )

        if self.failed_records > self.processed_records:
            errors["failed_records"] = (
                "Los registros fallidos no pueden superar "
                "los procesados."
            )

        if (
            self.status
            in (
                self.Status.PENDING,
                self.Status.QUEUED,
                self.Status.PROCESSING,
                self.Status.COMPLETED,
                self.Status.PARTIALLY_COMPLETED,
                self.Status.DELIVERY_PENDING,
                self.Status.DELIVERING,
                self.Status.DELIVERED,
                self.Status.DELIVERY_FAILED,
                self.Status.FAILED,
            )
            and not self.requested_at
        ):
            errors["requested_at"] = (
                "La exportación debe registrar "
                "la fecha de solicitud."
            )

        if (
            self.status == self.Status.QUEUED
            and not self.queued_at
        ):
            errors["queued_at"] = (
                "Una exportación en cola debe registrar "
                "la fecha de encolado."
            )

        if (
            self.status == self.Status.PROCESSING
            and not self.processing_started_at
        ):
            errors["processing_started_at"] = (
                "Una exportación activa debe registrar "
                "la fecha de inicio."
            )

        if (
            self.status
            in (
                self.Status.COMPLETED,
                self.Status.PARTIALLY_COMPLETED,
                self.Status.DELIVERY_PENDING,
                self.Status.DELIVERING,
                self.Status.DELIVERED,
                self.Status.DELIVERY_FAILED,
            )
            and not self.processing_finished_at
        ):
            errors["processing_finished_at"] = (
                "La exportación debe registrar "
                "la finalización del procesamiento."
            )

        if (
            self.status
            in (
                self.Status.COMPLETED,
                self.Status.PARTIALLY_COMPLETED,
                self.Status.DELIVERY_PENDING,
                self.Status.DELIVERING,
                self.Status.DELIVERED,
                self.Status.DELIVERY_FAILED,
            )
            and not self.result_file
        ):
            errors["result_file"] = (
                "La exportación debe tener "
                "un archivo resultante."
            )

        if (
            self.status == self.Status.DELIVERING
            and not self.delivery_started_at
        ):
            errors["delivery_started_at"] = (
                "Una entrega activa debe registrar "
                "la fecha de inicio."
            )

        if (
            self.status == self.Status.DELIVERED
            and not self.delivered_at
        ):
            errors["delivered_at"] = (
                "Una exportación entregada debe registrar "
                "la fecha de entrega."
            )

        if (
            self.status
            in (
                self.Status.FAILED,
                self.Status.DELIVERY_FAILED,
            )
            and not self.error_message.strip()
        ):
            errors["error_message"] = (
                "Una exportación fallida debe registrar "
                "el error."
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
            self.last_downloaded_at
            and not self.last_downloaded_by_id
        ):
            errors["last_downloaded_by"] = (
                "Debes indicar quién realizó "
                "la última descarga."
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
            self.status
            in (
                self.Status.CANCEL_REQUESTED,
                self.Status.CANCELLED,
            )
            and not self.cancellation_reason.strip()
        ):
            errors["cancellation_reason"] = (
                "Debes indicar el motivo de cancelación."
            )

        if (
            self.status == self.Status.CANCELLED
            and not self.cancelled_at
        ):
            errors["cancelled_at"] = (
                "Una exportación cancelada debe registrar "
                "la fecha de cancelación."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.batch_number = str(
            self.batch_number or ""
        ).strip().upper()

        self.name = str(
            self.name or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        self.result_file_name = str(
            self.result_file_name or ""
        ).strip()

        self.result_file_extension = str(
            self.result_file_extension or ""
        ).strip().lower().lstrip(".")

        self.result_mime_type = str(
            self.result_mime_type or ""
        ).strip().lower()

        self.destination_reference = str(
            self.destination_reference or ""
        ).strip()

        self.external_delivery_id = str(
            self.external_delivery_id or ""
        ).strip()

        if self.is_expired and self.status not in (
            self.Status.CANCELLED,
            self.Status.EXPIRED,
        ):
            self.status = self.Status.EXPIRED
            self.next_retry_at = None

        self.calculate_progress()
        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def submit(
        self,
        user=None,
    ):
        if self.status != self.Status.DRAFT:
            raise ValidationError(
                "Solo puedes presentar una exportación "
                "en borrador."
            )

        self.status = self.Status.PENDING
        self.requested_at = timezone.now()
        self.requested_by = user
        self.updated_by = user

        self.save()

    def queue(
        self,
        user=None,
    ):
        if self.status not in (
            self.Status.PENDING,
            self.Status.FAILED,
        ):
            raise ValidationError(
                "La exportación no puede enviarse a cola."
            )

        if self.is_expired:
            raise ValidationError(
                "La exportación se encuentra vencida."
            )

        self.status = self.Status.QUEUED
        self.queued_at = timezone.now()
        self.next_retry_at = None
        self.error_code = ""
        self.error_message = ""
        self.exception_type = ""
        self.stack_trace = ""
        self.updated_by = user

        self.save()

    def start_processing(
        self,
        *,
        total_records=0,
        user=None,
    ):
        if self.status not in (
            self.Status.PENDING,
            self.Status.QUEUED,
        ):
            raise ValidationError(
                "La exportación no puede iniciar "
                "desde su estado actual."
            )

        if total_records < 0:
            raise ValidationError(
                "El total de registros no puede ser negativo."
            )

        self.status = self.Status.PROCESSING
        self.processing_started_at = timezone.now()
        self.processing_finished_at = None
        self.progress_percentage = 0
        self.current_stage = "Preparando exportación"
        self.total_records = total_records
        self.processed_records = 0
        self.exported_records = 0
        self.skipped_records = 0
        self.warning_records = 0
        self.failed_records = 0
        self.result_summary = {}
        self.result_metadata = {}
        self.warnings = []
        self.errors = []
        self.error_code = ""
        self.error_message = ""
        self.exception_type = ""
        self.stack_trace = ""
        self.next_retry_at = None
        self.updated_by = user

        self.save()

    def update_progress(
        self,
        *,
        processed_increment=0,
        exported_increment=0,
        skipped_increment=0,
        warning_increment=0,
        failed_increment=0,
        current_stage="",
    ):
        if self.status != self.Status.PROCESSING:
            raise ValidationError(
                "La exportación no está procesándose."
            )

        increments = (
            processed_increment,
            exported_increment,
            skipped_increment,
            warning_increment,
            failed_increment,
        )

        if any(
            value < 0
            for value in increments
        ):
            raise ValidationError(
                "Los incrementos no pueden ser negativos."
            )

        self.processed_records += processed_increment
        self.exported_records += exported_increment
        self.skipped_records += skipped_increment
        self.warning_records += warning_increment
        self.failed_records += failed_increment

        if current_stage:
            self.current_stage = str(
                current_stage
            ).strip()

        self.calculate_progress()
        self.save()

    def mark_completed(
        self,
        *,
        result_file,
        file_name,
        file_size=0,
        mime_type="",
        checksum="",
        summary=None,
        metadata=None,
        expires_at=None,
        partial=False,
        user=None,
    ):
        if self.status != self.Status.PROCESSING:
            raise ValidationError(
                "Solo puedes completar una exportación "
                "en procesamiento."
            )

        if not result_file:
            raise ValidationError(
                "Debes indicar el archivo exportado."
            )

        file_name = str(
            file_name or ""
        ).strip()

        if not file_name:
            raise ValidationError(
                "Debes indicar el nombre del archivo."
            )

        self.status = (
            self.Status.PARTIALLY_COMPLETED
            if partial
            else self.Status.COMPLETED
        )
        self.result_file = result_file
        self.result_file_name = file_name
        self.result_file_size = max(
            0,
            file_size,
        )
        self.result_mime_type = str(
            mime_type or ""
        ).strip().lower()
        self.result_checksum = str(
            checksum or ""
        ).strip()
        self.result_summary = summary or {}
        self.result_metadata = metadata or {}
        self.processing_finished_at = timezone.now()
        self.progress_percentage = 100
        self.current_stage = "Exportación finalizada"
        self.expires_at = expires_at
        self.next_retry_at = None
        self.error_code = ""
        self.error_message = ""
        self.updated_by = user

        if "." in file_name:
            self.result_file_extension = (
                file_name.rsplit(
                    ".",
                    1,
                )[-1].lower()
            )

        if self.destination_type != self.DestinationType.DOWNLOAD:
            self.status = self.Status.DELIVERY_PENDING

        self.save()

    def start_delivery(
        self,
        user=None,
    ):
        if self.status not in (
            self.Status.COMPLETED,
            self.Status.PARTIALLY_COMPLETED,
            self.Status.DELIVERY_PENDING,
            self.Status.DELIVERY_FAILED,
        ):
            raise ValidationError(
                "La exportación no está disponible "
                "para entrega."
            )

        if not self.result_file:
            raise ValidationError(
                "No existe un archivo para entregar."
            )

        if self.is_expired:
            raise ValidationError(
                "La exportación se encuentra vencida."
            )

        self.status = self.Status.DELIVERING
        self.delivery_started_at = timezone.now()
        self.delivered_at = None
        self.delivery_response = {}
        self.error_code = ""
        self.error_message = ""
        self.next_retry_at = None
        self.updated_by = user

        self.save()

    def mark_delivered(
        self,
        *,
        external_delivery_id="",
        destination_reference="",
        response=None,
        user=None,
    ):
        if self.status != self.Status.DELIVERING:
            raise ValidationError(
                "La exportación no está entregándose."
            )

        self.status = self.Status.DELIVERED
        self.delivered_at = timezone.now()
        self.external_delivery_id = str(
            external_delivery_id or ""
        ).strip()
        self.destination_reference = str(
            destination_reference or ""
        ).strip()
        self.delivery_response = response or {}
        self.error_code = ""
        self.error_message = ""
        self.next_retry_at = None
        self.updated_by = user

        self.save()

    def mark_failed(
        self,
        *,
        error,
        error_code="",
        exception_type="",
        stack_trace="",
        errors=None,
        next_retry_at=None,
        delivery_failure=False,
        user=None,
    ):
        error = str(
            error or ""
        ).strip()

        if not error:
            raise ValidationError(
                "Debes indicar el error de exportación."
            )

        if self.is_finished and self.status not in (
            self.Status.DELIVERY_FAILED,
        ):
            raise ValidationError(
                "La exportación ya está finalizada."
            )

        now = timezone.now()

        self.status = (
            self.Status.DELIVERY_FAILED
            if delivery_failure
            else self.Status.FAILED
        )
        self.error_code = str(
            error_code or ""
        ).strip()
        self.error_message = error
        self.exception_type = str(
            exception_type or ""
        ).strip()
        self.stack_trace = str(
            stack_trace or ""
        )
        self.errors = errors or []
        self.current_stage = (
            "Error de entrega"
            if delivery_failure
            else "Error de exportación"
        )
        self.updated_by = user

        if (
            not delivery_failure
            and self.processing_started_at
            and not self.processing_finished_at
        ):
            self.processing_finished_at = now

        if (
            self.retry_count < self.maximum_retries
            and next_retry_at
        ):
            self.next_retry_at = next_retry_at
        else:
            self.next_retry_at = None

        self.save()

    def prepare_retry(
        self,
        *,
        next_retry_at=None,
        user=None,
    ):
        if not self.can_retry:
            raise ValidationError(
                "La exportación no admite otro reintento."
            )

        if (
            next_retry_at
            and next_retry_at <= timezone.now()
        ):
            raise ValidationError(
                "El próximo reintento debe ser futuro."
            )

        previous_status = self.status

        self.retry_count += 1
        self.next_retry_at = next_retry_at
        self.error_code = ""
        self.error_message = ""
        self.exception_type = ""
        self.stack_trace = ""
        self.errors = []
        self.updated_by = user

        if previous_status == self.Status.DELIVERY_FAILED:
            self.status = self.Status.DELIVERY_PENDING
        else:
            self.status = self.Status.PENDING
            self.processing_started_at = None
            self.processing_finished_at = None
            self.progress_percentage = 0
            self.current_stage = "Preparada para reintento"
            self.processed_records = 0
            self.exported_records = 0
            self.skipped_records = 0
            self.warning_records = 0
            self.failed_records = 0

        self.save()

    def register_download(
        self,
        *,
        user,
        ip_address=None,
    ):
        if not self.can_download:
            raise ValidationError(
                "La exportación no está disponible "
                "para descarga."
            )

        now = timezone.now()

        if not self.first_downloaded_at:
            self.first_downloaded_at = now

        self.last_downloaded_at = now
        self.last_downloaded_by = user
        self.last_downloaded_ip = ip_address
        self.download_count += 1
        self.updated_by = user

        self.save()

    def request_cancel(
        self,
        *,
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

        if self.is_finished:
            raise ValidationError(
                "La exportación ya no puede cancelarse."
            )

        now = timezone.now()

        self.cancel_requested_at = now
        self.cancel_requested_by = user
        self.cancellation_reason = reason
        self.updated_by = user

        if self.status in (
            self.Status.DRAFT,
            self.Status.PENDING,
            self.Status.QUEUED,
            self.Status.DELIVERY_PENDING,
        ):
            self.status = self.Status.CANCELLED
            self.cancelled_at = now
            self.cancelled_by = user
            self.next_retry_at = None
        else:
            self.status = self.Status.CANCEL_REQUESTED

        self.save()

    def mark_cancelled(
        self,
        *,
        user=None,
    ):
        if self.status != self.Status.CANCEL_REQUESTED:
            raise ValidationError(
                "La exportación no tiene "
                "una cancelación pendiente."
            )

        now = timezone.now()

        self.status = self.Status.CANCELLED
        self.cancelled_at = now
        self.cancelled_by = user
        self.next_retry_at = None
        self.current_stage = "Exportación cancelada"
        self.updated_by = user

        if (
            self.processing_started_at
            and not self.processing_finished_at
        ):
            self.processing_finished_at = now

        self.save()

    def mark_expired(
        self,
        user=None,
    ):
        if not self.is_expired:
            raise ValidationError(
                "La exportación todavía no ha vencido."
            )

        if self.status in (
            self.Status.CANCELLED,
            self.Status.EXPIRED,
        ):
            raise ValidationError(
                "La exportación ya no puede marcarse "
                "como vencida."
            )

        self.status = self.Status.EXPIRED
        self.next_retry_at = None
        self.updated_by = user

        self.save()

    def archive(
        self,
        *,
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

        if not self.is_finished:
            raise ValidationError(
                "Solo puedes archivar una exportación "
                "finalizada."
            )

        self.archived_at = timezone.now()
        self.archived_by = user
        self.archived_reason = reason
        self.updated_by = user

        self.save(
            update_fields=[
                "archived_at",
                "archived_by",
                "archived_reason",
                "updated_by",
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
        self.updated_by = user

        self.save(
            update_fields=[
                "archived_at",
                "archived_by",
                "archived_reason",
                "updated_by",
                "updated_at",
            ]
        )