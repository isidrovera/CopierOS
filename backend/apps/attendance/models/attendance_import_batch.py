# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class AttendanceImportBatch(models.Model):
    """
    Lote de importación de información del módulo de asistencia.

    Permite importar datos desde archivos, dispositivos biométricos,
    APIs, migraciones y otros sistemas externos.

    El lote conserva:

    - Archivo o fuente original.
    - Configuración de interpretación.
    - Mapeo de columnas.
    - Reglas de validación.
    - Reglas de duplicados.
    - Progreso.
    - Resultados.
    - Errores.
    - Revisión y aprobación.
    - Reintentos.
    - Reversión.
    - Auditoría completa.
    """

    class ImportType(models.TextChoices):
        ATTENDANCE_RECORDS = (
            "attendance_records",
            "Marcaciones de asistencia",
        )
        EMPLOYEES = (
            "employees",
            "Trabajadores",
        )
        WORK_SCHEDULES = (
            "work_schedules",
            "Horarios",
        )
        SCHEDULE_ASSIGNMENTS = (
            "schedule_assignments",
            "Asignaciones de horario",
        )
        WORK_LOCATIONS = (
            "work_locations",
            "Ubicaciones de trabajo",
        )
        DEVICE_PERMISSIONS = (
            "device_permissions",
            "Permisos de dispositivos",
        )
        LEAVE_REQUESTS = (
            "leave_requests",
            "Permisos y licencias",
        )
        OVERTIME_REQUESTS = (
            "overtime_requests",
            "Horas extras",
        )
        OPERATIONAL_SESSIONS = (
            "operational_sessions",
            "Sesiones operativas",
        )
        MONTHLY_SUMMARIES = (
            "monthly_summaries",
            "Resúmenes mensuales",
        )
        GENERIC = (
            "generic",
            "Importación genérica",
        )

    class SourceType(models.TextChoices):
        XLSX = (
            "xlsx",
            "Excel XLSX",
        )
        XLS = (
            "xls",
            "Excel XLS",
        )
        CSV = (
            "csv",
            "CSV",
        )
        JSON = (
            "json",
            "JSON",
        )
        BIOMETRIC_DEVICE = (
            "biometric_device",
            "Dispositivo biométrico",
        )
        ATTENDANCE_DEVICE = (
            "attendance_device",
            "Dispositivo de asistencia",
        )
        EXTERNAL_API = (
            "external_api",
            "API externa",
        )
        INTERNAL_API = (
            "internal_api",
            "API interna",
        )
        MANUAL_ENTRY = (
            "manual_entry",
            "Registro manual",
        )
        DATABASE_MIGRATION = (
            "database_migration",
            "Migración de base de datos",
        )
        MANAGEMENT_COMMAND = (
            "management_command",
            "Comando de administración",
        )
        OTHER = (
            "other",
            "Otra fuente",
        )

    class Status(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        UPLOADED = (
            "uploaded",
            "Archivo recibido",
        )
        PENDING_VALIDATION = (
            "pending_validation",
            "Pendiente de validación",
        )
        VALIDATING = (
            "validating",
            "Validando",
        )
        VALIDATED = (
            "validated",
            "Validado",
        )
        VALIDATED_WITH_WARNINGS = (
            "validated_with_warnings",
            "Validado con observaciones",
        )
        REJECTED = (
            "rejected",
            "Rechazado",
        )
        PENDING_IMPORT = (
            "pending_import",
            "Pendiente de importación",
        )
        IMPORTING = (
            "importing",
            "Importando",
        )
        COMPLETED = (
            "completed",
            "Completado",
        )
        PARTIALLY_COMPLETED = (
            "partially_completed",
            "Completado parcialmente",
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
        ROLLED_BACK = (
            "rolled_back",
            "Revertido",
        )

    class DuplicateAction(models.TextChoices):
        IGNORE = (
            "ignore",
            "Ignorar duplicado",
        )
        REJECT = (
            "reject",
            "Rechazar duplicado",
        )
        UPDATE = (
            "update",
            "Actualizar registro existente",
        )
        CREATE_INCIDENT = (
            "create_incident",
            "Crear incidencia",
        )
        REQUIRE_REVIEW = (
            "require_review",
            "Requiere revisión",
        )

    class InvalidRecordAction(models.TextChoices):
        REJECT_BATCH = (
            "reject_batch",
            "Rechazar todo el lote",
        )
        SKIP_RECORD = (
            "skip_record",
            "Omitir registro",
        )
        IMPORT_VALID_RECORDS = (
            "import_valid_records",
            "Importar registros válidos",
        )
        REQUIRE_REVIEW = (
            "require_review",
            "Requiere revisión",
        )

    class DateFormat(models.TextChoices):
        AUTO = (
            "auto",
            "Detección automática",
        )
        DMY = (
            "dmy",
            "Día/Mes/Año",
        )
        MDY = (
            "mdy",
            "Mes/Día/Año",
        )
        YMD = (
            "ymd",
            "Año/Mes/Día",
        )
        ISO = (
            "iso",
            "ISO 8601",
        )

    class TimeFormat(models.TextChoices):
        AUTO = (
            "auto",
            "Detección automática",
        )
        H24 = (
            "24h",
            "24 horas",
        )
        H12 = (
            "12h",
            "12 horas",
        )

    class EmployeeMatchMode(models.TextChoices):
        AUTO = (
            "auto",
            "Automático",
        )
        EMPLOYEE_CODE = (
            "employee_code",
            "Código de trabajador",
        )
        USERNAME = (
            "username",
            "Usuario",
        )
        EMAIL = (
            "email",
            "Correo electrónico",
        )
        DOCUMENT_NUMBER = (
            "document_number",
            "Documento de identidad",
        )
        EXTERNAL_ID = (
            "external_id",
            "ID externo",
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

    import_type = models.CharField(
        max_length=40,
        choices=ImportType.choices,
        db_index=True,
        verbose_name="Tipo de importación",
    )

    source_type = models.CharField(
        max_length=40,
        choices=SourceType.choices,
        db_index=True,
        verbose_name="Tipo de fuente",
    )

    status = models.CharField(
        max_length=40,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    attendance_device = models.ForeignKey(
        "attendance.AttendanceDevice",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="import_batches",
        verbose_name="Dispositivo de asistencia",
    )

    processing_run = models.ForeignKey(
        "attendance.AttendanceProcessingRun",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="import_batches",
        verbose_name="Ejecución de procesamiento",
    )

    source_file = models.FileField(
        upload_to="attendance/imports/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Archivo de origen",
    )

    original_file_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre original del archivo",
    )

    source_file_extension = models.CharField(
        max_length=20,
        blank=True,
        db_index=True,
        verbose_name="Extensión",
    )

    source_mime_type = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Tipo MIME",
    )

    source_file_size = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Tamaño del archivo",
    )

    file_checksum = models.CharField(
        max_length=128,
        blank=True,
        db_index=True,
        verbose_name="Checksum del archivo",
    )

    source_system = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Sistema de origen",
    )

    source_reference = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Referencia de origen",
    )

    external_batch_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="ID de lote externo",
    )

    sheet_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Hoja",
    )

    header_row_number = models.PositiveIntegerField(
        default=1,
        verbose_name="Fila de encabezado",
    )

    first_data_row_number = models.PositiveIntegerField(
        default=2,
        verbose_name="Primera fila de datos",
    )

    delimiter = models.CharField(
        max_length=10,
        blank=True,
        default=",",
        verbose_name="Separador CSV",
    )

    encoding = models.CharField(
        max_length=50,
        default="utf-8",
        verbose_name="Codificación",
    )

    date_format = models.CharField(
        max_length=20,
        choices=DateFormat.choices,
        default=DateFormat.AUTO,
        verbose_name="Formato de fecha",
    )

    time_format = models.CharField(
        max_length=20,
        choices=TimeFormat.choices,
        default=TimeFormat.AUTO,
        verbose_name="Formato de hora",
    )

    timezone_name = models.CharField(
        max_length=100,
        default="America/Lima",
        verbose_name="Zona horaria",
    )

    employee_match_mode = models.CharField(
        max_length=30,
        choices=EmployeeMatchMode.choices,
        default=EmployeeMatchMode.AUTO,
        verbose_name="Modo de identificación de trabajador",
    )

    duplicate_action = models.CharField(
        max_length=30,
        choices=DuplicateAction.choices,
        default=DuplicateAction.REQUIRE_REVIEW,
        verbose_name="Acción ante duplicados",
    )

    invalid_record_action = models.CharField(
        max_length=30,
        choices=InvalidRecordAction.choices,
        default=InvalidRecordAction.IMPORT_VALID_RECORDS,
        verbose_name="Acción ante registros inválidos",
    )

    column_mapping = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Mapeo de columnas",
    )

    normalization_rules = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Reglas de normalización",
    )

    validation_rules = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Reglas de validación",
    )

    transformation_rules = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Reglas de transformación",
    )

    import_options = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Opciones de importación",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos",
    )

    dry_run = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Solo validar",
    )

    allow_updates = models.BooleanField(
        default=True,
        verbose_name="Permitir actualizaciones",
    )

    allow_create_employees = models.BooleanField(
        default=False,
        verbose_name="Permitir creación de trabajadores",
    )

    allow_create_devices = models.BooleanField(
        default=False,
        verbose_name="Permitir creación de dispositivos",
    )

    stop_on_first_error = models.BooleanField(
        default=False,
        verbose_name="Detener en primer error",
    )

    requires_review = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere revisión",
    )

    uploaded_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Archivo recibido el",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_import_batches_uploaded",
        verbose_name="Cargado por",
    )

    validation_started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Validación iniciada el",
    )

    validation_finished_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Validación finalizada el",
    )

    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_import_batches_validated",
        verbose_name="Validado por",
    )

    import_started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Importación iniciada el",
    )

    import_finished_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Importación finalizada el",
    )

    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_import_batches_imported",
        verbose_name="Importado por",
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

    total_rows = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Total de filas",
    )

    processed_rows = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Filas procesadas",
    )

    valid_rows = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Filas válidas",
    )

    warning_rows = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Filas con observaciones",
    )

    invalid_rows = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Filas inválidas",
    )

    duplicate_rows = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Filas duplicadas",
    )

    imported_rows = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Filas importadas",
    )

    updated_rows = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Filas actualizadas",
    )

    unchanged_rows = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Filas sin cambios",
    )

    skipped_rows = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Filas omitidas",
    )

    failed_rows = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Filas fallidas",
    )

    validation_summary = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resumen de validación",
    )

    import_summary = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resumen de importación",
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

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Revisado el",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_import_batches_reviewed",
        verbose_name="Revisado por",
    )

    review_observation = models.TextField(
        blank=True,
        verbose_name="Observación de revisión",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Aprobado el",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_import_batches_approved",
        verbose_name="Aprobado por",
    )

    approval_observation = models.TextField(
        blank=True,
        verbose_name="Observación de aprobación",
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
        related_name="attendance_import_batches_cancel_requested",
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
        related_name="attendance_import_batches_cancelled",
        verbose_name="Cancelado por",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    rollback_available = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Permite reversión",
    )

    rollback_started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Reversión iniciada el",
    )

    rolled_back_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Revertido el",
    )

    rolled_back_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_import_batches_rolled_back",
        verbose_name="Revertido por",
    )

    rollback_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de reversión",
    )

    rollback_result = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resultado de reversión",
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
        related_name="attendance_import_batches_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_import_batches_updated",
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
        related_name="attendance_import_batches_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Lote de importación de asistencia"
        verbose_name_plural = "Lotes de importación de asistencia"

        ordering = (
            "-created_at",
        )

        constraints = (
            models.CheckConstraint(
                condition=(
                    models.Q(progress_percentage__gte=0)
                    & models.Q(progress_percentage__lte=100)
                ),
                name="att_imp_progress_range",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    processed_rows__lte=models.F("total_rows")
                ),
                name="att_imp_processed_lte_total",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    valid_rows__lte=models.F("total_rows")
                ),
                name="att_imp_valid_lte_total",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    warning_rows__lte=models.F("total_rows")
                ),
                name="att_imp_warning_lte_total",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    invalid_rows__lte=models.F("total_rows")
                ),
                name="att_imp_invalid_lte_total",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    duplicate_rows__lte=models.F("total_rows")
                ),
                name="att_imp_duplicate_lte_total",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    retry_count__lte=models.F("maximum_retries")
                ),
                name="att_imp_retry_lte_max",
            ),
        )

        indexes = (
            models.Index(
                fields=(
                    "import_type",
                    "status",
                    "created_at",
                ),
                name="att_imp_type_status_idx",
            ),
            models.Index(
                fields=(
                    "source_type",
                    "status",
                    "created_at",
                ),
                name="att_imp_source_status_idx",
            ),
            models.Index(
                fields=(
                    "attendance_device",
                    "status",
                ),
                name="att_imp_device_status_idx",
            ),
            models.Index(
                fields=(
                    "processing_run",
                    "status",
                ),
                name="att_imp_process_status_idx",
            ),
            models.Index(
                fields=(
                    "uploaded_by",
                    "uploaded_at",
                ),
                name="att_imp_uploaded_idx",
            ),
            models.Index(
                fields=(
                    "validation_started_at",
                    "validation_finished_at",
                ),
                name="att_imp_validation_idx",
            ),
            models.Index(
                fields=(
                    "import_started_at",
                    "import_finished_at",
                ),
                name="att_imp_importing_idx",
            ),
            models.Index(
                fields=(
                    "requires_review",
                    "reviewed_at",
                    "status",
                ),
                name="att_imp_review_idx",
            ),
            models.Index(
                fields=(
                    "rollback_available",
                    "rolled_back_at",
                ),
                name="att_imp_rollback_idx",
            ),
            models.Index(
                fields=(
                    "next_retry_at",
                    "retry_count",
                    "status",
                ),
                name="att_imp_retry_idx",
            ),
            models.Index(
                fields=(
                    "source_system",
                    "external_batch_id",
                ),
                name="att_imp_external_idx",
            ),
            models.Index(
                fields=(
                    "batch_key",
                    "correlation_id",
                ),
                name="att_imp_batch_corr_idx",
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
            self.Status.FAILED,
            self.Status.CANCELLED,
            self.Status.REJECTED,
            self.Status.ROLLED_BACK,
        )

    @property
    def can_import(self):
        return (
            self.status in (
                self.Status.VALIDATED,
                self.Status.VALIDATED_WITH_WARNINGS,
                self.Status.PENDING_IMPORT,
            )
            and not self.dry_run
            and self.archived_at is None
        )

    @property
    def can_retry(self):
        return (
            self.status == self.Status.FAILED
            and self.retry_count < self.maximum_retries
            and self.archived_at is None
        )

    @property
    def can_rollback(self):
        return (
            self.rollback_available
            and self.status in (
                self.Status.COMPLETED,
                self.Status.PARTIALLY_COMPLETED,
            )
            and not self.rolled_back_at
            and self.archived_at is None
        )

    def calculate_progress(self):
        if self.total_rows <= 0:
            self.progress_percentage = 0
            return self.progress_percentage

        self.progress_percentage = min(
            100,
            round(
                (
                    self.processed_rows
                    / self.total_rows
                )
                * 100,
                2,
            ),
        )

        return self.progress_percentage

    def clean(self):
        super().clean()

        errors = {}

        if not str(self.batch_number or "").strip():
            errors["batch_number"] = (
                "Debes indicar el número de lote."
            )

        if not str(self.name or "").strip():
            errors["name"] = (
                "Debes indicar el nombre del lote."
            )

        if (
            self.attendance_device_id
            and self.attendance_device.archived_at
        ):
            errors["attendance_device"] = (
                "El dispositivo seleccionado está archivado."
            )

        if (
            self.processing_run_id
            and self.processing_run.archived_at
        ):
            errors["processing_run"] = (
                "La ejecución de procesamiento está archivada."
            )

        file_source_types = (
            self.SourceType.XLSX,
            self.SourceType.XLS,
            self.SourceType.CSV,
            self.SourceType.JSON,
        )

        if (
            self.source_type in file_source_types
            and self.status != self.Status.DRAFT
            and not self.source_file
        ):
            errors["source_file"] = (
                "Este tipo de importación requiere "
                "un archivo de origen."
            )

        if (
            self.source_type
            == self.SourceType.ATTENDANCE_DEVICE
            and not self.attendance_device_id
        ):
            errors["attendance_device"] = (
                "Debes indicar el dispositivo de asistencia."
            )

        if self.header_row_number < 1:
            errors["header_row_number"] = (
                "La fila de encabezado debe ser mayor que cero."
            )

        if self.first_data_row_number < 1:
            errors["first_data_row_number"] = (
                "La primera fila de datos debe ser mayor que cero."
            )

        if (
            self.source_type
            in (
                self.SourceType.XLSX,
                self.SourceType.XLS,
                self.SourceType.CSV,
            )
            and self.first_data_row_number
            <= self.header_row_number
        ):
            errors["first_data_row_number"] = (
                "La primera fila de datos debe estar después "
                "de la fila de encabezado."
            )

        json_object_fields = (
            "column_mapping",
            "normalization_rules",
            "validation_rules",
            "transformation_rules",
            "import_options",
            "metadata",
            "validation_summary",
            "import_summary",
            "rollback_result",
        )

        for field_name in json_object_fields:
            if not isinstance(
                getattr(self, field_name),
                dict,
            ):
                errors[field_name] = (
                    "El valor debe ser un objeto JSON."
                )

        json_list_fields = (
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

        count_fields = (
            "processed_rows",
            "valid_rows",
            "warning_rows",
            "invalid_rows",
            "duplicate_rows",
            "imported_rows",
            "updated_rows",
            "unchanged_rows",
            "skipped_rows",
            "failed_rows",
        )

        for field_name in count_fields:
            if getattr(self, field_name) > self.total_rows:
                errors[field_name] = (
                    "El valor no puede superar "
                    "el total de filas."
                )

        if (
            self.status == self.Status.VALIDATING
            and not self.validation_started_at
        ):
            errors["validation_started_at"] = (
                "Una importación en validación debe registrar "
                "la fecha de inicio."
            )

        if (
            self.status in (
                self.Status.VALIDATED,
                self.Status.VALIDATED_WITH_WARNINGS,
                self.Status.PENDING_IMPORT,
                self.Status.IMPORTING,
                self.Status.COMPLETED,
                self.Status.PARTIALLY_COMPLETED,
            )
            and not self.validation_finished_at
        ):
            errors["validation_finished_at"] = (
                "El lote debe registrar la finalización "
                "de la validación."
            )

        if (
            self.status == self.Status.IMPORTING
            and not self.import_started_at
        ):
            errors["import_started_at"] = (
                "Una importación activa debe registrar "
                "la fecha de inicio."
            )

        if (
            self.status in (
                self.Status.COMPLETED,
                self.Status.PARTIALLY_COMPLETED,
            )
            and not self.import_finished_at
        ):
            errors["import_finished_at"] = (
                "Una importación finalizada debe registrar "
                "la fecha de finalización."
            )

        if (
            self.status == self.Status.FAILED
            and not str(self.error_message or "").strip()
        ):
            errors["error_message"] = (
                "Un lote fallido debe registrar el error."
            )

        if (
            self.requires_review
            and not self.reviewed_at
            and self.status
            in (
                self.Status.PENDING_IMPORT,
                self.Status.COMPLETED,
                self.Status.PARTIALLY_COMPLETED,
            )
        ):
            errors["reviewed_at"] = (
                "El lote requiere revisión antes "
                "de continuar."
            )

        if (
            self.reviewed_at
            and not self.reviewed_by_id
        ):
            errors["reviewed_by"] = (
                "Debes indicar quién revisó el lote."
            )

        if (
            self.approved_at
            and not self.approved_by_id
        ):
            errors["approved_by"] = (
                "Debes indicar quién aprobó el lote."
            )

        if (
            self.status in (
                self.Status.CANCEL_REQUESTED,
                self.Status.CANCELLED,
            )
            and not str(
                self.cancellation_reason or ""
            ).strip()
        ):
            errors["cancellation_reason"] = (
                "Debes indicar el motivo de cancelación."
            )

        if (
            self.status == self.Status.CANCELLED
            and not self.cancelled_at
        ):
            errors["cancelled_at"] = (
                "Un lote cancelado debe registrar "
                "la fecha de cancelación."
            )

        if (
            self.rolled_back_at
            and not self.rolled_back_by_id
        ):
            errors["rolled_back_by"] = (
                "Debes indicar quién realizó la reversión."
            )

        if (
            self.rolled_back_at
            and not str(self.rollback_reason or "").strip()
        ):
            errors["rollback_reason"] = (
                "Debes indicar el motivo de reversión."
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

        self.original_file_name = str(
            self.original_file_name or ""
        ).strip()

        self.source_file_extension = str(
            self.source_file_extension or ""
        ).strip().lower().lstrip(".")

        self.source_mime_type = str(
            self.source_mime_type or ""
        ).strip().lower()

        self.file_checksum = str(
            self.file_checksum or ""
        ).strip()

        self.source_system = str(
            self.source_system or ""
        ).strip()

        self.source_reference = str(
            self.source_reference or ""
        ).strip()

        self.external_batch_id = str(
            self.external_batch_id or ""
        ).strip()

        self.sheet_name = str(
            self.sheet_name or ""
        ).strip()

        self.encoding = str(
            self.encoding or "utf-8"
        ).strip()

        self.timezone_name = str(
            self.timezone_name or "America/Lima"
        ).strip()

        self.calculate_progress()
        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def mark_uploaded(
        self,
        *,
        user=None,
        source_file=None,
        original_file_name="",
        mime_type="",
        file_size=0,
        checksum="",
    ):
        if self.status != self.Status.DRAFT:
            raise ValidationError(
                "Solo puedes cargar un archivo "
                "en un lote en borrador."
            )

        if source_file is not None:
            self.source_file = source_file

        self.original_file_name = str(
            original_file_name or ""
        ).strip()

        self.source_mime_type = str(
            mime_type or ""
        ).strip()

        self.source_file_size = max(
            0,
            file_size,
        )

        self.file_checksum = str(
            checksum or ""
        ).strip()

        if "." in self.original_file_name:
            self.source_file_extension = (
                self.original_file_name.rsplit(
                    ".",
                    1,
                )[-1].lower()
            )

        self.status = self.Status.UPLOADED
        self.uploaded_at = timezone.now()
        self.uploaded_by = user
        self.updated_by = user

        self.save()

    def start_validation(
        self,
        *,
        total_rows=0,
        user=None,
    ):
        if self.status not in (
            self.Status.DRAFT,
            self.Status.UPLOADED,
            self.Status.PENDING_VALIDATION,
            self.Status.FAILED,
        ):
            raise ValidationError(
                "El lote no está disponible para validación."
            )

        if total_rows < 0:
            raise ValidationError(
                "El total de filas no puede ser negativo."
            )

        self.status = self.Status.VALIDATING
        self.validation_started_at = timezone.now()
        self.validation_finished_at = None
        self.total_rows = total_rows
        self.processed_rows = 0
        self.valid_rows = 0
        self.warning_rows = 0
        self.invalid_rows = 0
        self.duplicate_rows = 0
        self.current_stage = "Validando registros"
        self.progress_percentage = 0
        self.validation_summary = {}
        self.warnings = []
        self.errors = []
        self.error_code = ""
        self.error_message = ""
        self.exception_type = ""
        self.stack_trace = ""
        self.next_retry_at = None
        self.updated_by = user

        self.save()

    def update_validation_progress(
        self,
        *,
        processed_increment=0,
        valid_increment=0,
        warning_increment=0,
        invalid_increment=0,
        duplicate_increment=0,
        current_stage="",
    ):
        if self.status != self.Status.VALIDATING:
            raise ValidationError(
                "El lote no está en validación."
            )

        increments = (
            processed_increment,
            valid_increment,
            warning_increment,
            invalid_increment,
            duplicate_increment,
        )

        if any(
            value < 0
            for value in increments
        ):
            raise ValidationError(
                "Los incrementos no pueden ser negativos."
            )

        self.processed_rows += processed_increment
        self.valid_rows += valid_increment
        self.warning_rows += warning_increment
        self.invalid_rows += invalid_increment
        self.duplicate_rows += duplicate_increment

        if current_stage:
            self.current_stage = str(
                current_stage
            ).strip()

        self.calculate_progress()
        self.save()

    def finish_validation(
        self,
        *,
        summary=None,
        warnings=None,
        errors=None,
        requires_review=False,
        user=None,
    ):
        if self.status != self.Status.VALIDATING:
            raise ValidationError(
                "El lote no está en validación."
            )

        self.validation_finished_at = timezone.now()
        self.validated_by = user
        self.validation_summary = summary or {}
        self.warnings = warnings or []
        self.errors = errors or []
        self.requires_review = requires_review
        self.current_stage = "Validación finalizada"

        if self.invalid_rows > 0:
            if (
                self.invalid_record_action
                == self.InvalidRecordAction.REJECT_BATCH
            ):
                self.status = self.Status.REJECTED
            else:
                self.status = (
                    self.Status.VALIDATED_WITH_WARNINGS
                )
        elif (
            self.warning_rows > 0
            or self.duplicate_rows > 0
            or self.warnings
        ):
            self.status = (
                self.Status.VALIDATED_WITH_WARNINGS
            )
        else:
            self.status = self.Status.VALIDATED

        if (
            not self.dry_run
            and self.status
            in (
                self.Status.VALIDATED,
                self.Status.VALIDATED_WITH_WARNINGS,
            )
            and not requires_review
        ):
            self.status = self.Status.PENDING_IMPORT

        self.updated_by = user

        self.save()

    def approve(
        self,
        *,
        user,
        observation="",
    ):
        if self.status not in (
            self.Status.VALIDATED,
            self.Status.VALIDATED_WITH_WARNINGS,
            self.Status.PENDING_IMPORT,
        ):
            raise ValidationError(
                "El lote no está disponible para aprobación."
            )

        now = timezone.now()

        self.requires_review = False
        self.reviewed_at = now
        self.reviewed_by = user
        self.review_observation = str(
            observation or ""
        ).strip()

        self.approved_at = now
        self.approved_by = user
        self.approval_observation = str(
            observation or ""
        ).strip()

        if not self.dry_run:
            self.status = self.Status.PENDING_IMPORT

        self.updated_by = user
        self.save()

    def start_import(
        self,
        *,
        user=None,
    ):
        if not self.can_import:
            raise ValidationError(
                "El lote no está disponible para importación."
            )

        self.status = self.Status.IMPORTING
        self.import_started_at = timezone.now()
        self.import_finished_at = None
        self.imported_rows = 0
        self.updated_rows = 0
        self.unchanged_rows = 0
        self.skipped_rows = 0
        self.failed_rows = 0
        self.current_stage = "Importando registros"
        self.import_summary = {}
        self.error_code = ""
        self.error_message = ""
        self.exception_type = ""
        self.stack_trace = ""
        self.next_retry_at = None
        self.updated_by = user

        self.save()

    def update_import_progress(
        self,
        *,
        imported_increment=0,
        updated_increment=0,
        unchanged_increment=0,
        skipped_increment=0,
        failed_increment=0,
        current_stage="",
    ):
        if self.status != self.Status.IMPORTING:
            raise ValidationError(
                "El lote no está importándose."
            )

        increments = (
            imported_increment,
            updated_increment,
            unchanged_increment,
            skipped_increment,
            failed_increment,
        )

        if any(
            value < 0
            for value in increments
        ):
            raise ValidationError(
                "Los incrementos no pueden ser negativos."
            )

        self.imported_rows += imported_increment
        self.updated_rows += updated_increment
        self.unchanged_rows += unchanged_increment
        self.skipped_rows += skipped_increment
        self.failed_rows += failed_increment

        if current_stage:
            self.current_stage = str(
                current_stage
            ).strip()

        self.save()

    def finish_import(
        self,
        *,
        summary=None,
        warnings=None,
        errors=None,
        user=None,
    ):
        if self.status != self.Status.IMPORTING:
            raise ValidationError(
                "El lote no está importándose."
            )

        self.import_finished_at = timezone.now()
        self.imported_by = user
        self.import_summary = summary or {}
        self.warnings = warnings or self.warnings
        self.errors = errors or self.errors
        self.current_stage = "Importación finalizada"
        self.progress_percentage = 100
        self.rollback_available = bool(
            self.imported_rows
            or self.updated_rows
        )

        if (
            self.failed_rows > 0
            or self.skipped_rows > 0
        ):
            self.status = (
                self.Status.PARTIALLY_COMPLETED
            )
        else:
            self.status = self.Status.COMPLETED

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
        user=None,
    ):
        error = str(
            error or ""
        ).strip()

        if not error:
            raise ValidationError(
                "Debes indicar el error."
            )

        if self.is_finished:
            raise ValidationError(
                "El lote ya está finalizado."
            )

        now = timezone.now()

        self.status = self.Status.FAILED
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
        self.current_stage = "Error de procesamiento"

        if (
            self.validation_started_at
            and not self.validation_finished_at
        ):
            self.validation_finished_at = now

        if (
            self.import_started_at
            and not self.import_finished_at
        ):
            self.import_finished_at = now

        if (
            self.retry_count < self.maximum_retries
            and next_retry_at
        ):
            self.next_retry_at = next_retry_at
        else:
            self.next_retry_at = None

        self.updated_by = user
        self.save()

    def prepare_retry(
        self,
        *,
        next_retry_at=None,
        user=None,
    ):
        if not self.can_retry:
            raise ValidationError(
                "El lote no admite otro reintento."
            )

        if (
            next_retry_at
            and next_retry_at <= timezone.now()
        ):
            raise ValidationError(
                "El próximo reintento debe ser futuro."
            )

        self.retry_count += 1
        self.next_retry_at = next_retry_at
        self.status = self.Status.PENDING_VALIDATION
        self.error_code = ""
        self.error_message = ""
        self.exception_type = ""
        self.stack_trace = ""
        self.errors = []
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
                "El lote ya no puede cancelarse."
            )

        now = timezone.now()

        self.cancel_requested_at = now
        self.cancel_requested_by = user
        self.cancellation_reason = reason
        self.updated_by = user

        if self.status in (
            self.Status.DRAFT,
            self.Status.UPLOADED,
            self.Status.PENDING_VALIDATION,
            self.Status.VALIDATED,
            self.Status.VALIDATED_WITH_WARNINGS,
            self.Status.PENDING_IMPORT,
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
                "El lote no tiene una cancelación pendiente."
            )

        now = timezone.now()

        self.status = self.Status.CANCELLED
        self.cancelled_at = now
        self.cancelled_by = user
        self.next_retry_at = None
        self.current_stage = "Importación cancelada"
        self.updated_by = user

        if (
            self.import_started_at
            and not self.import_finished_at
        ):
            self.import_finished_at = now

        self.save()

    def start_rollback(
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
                "Debes indicar el motivo de reversión."
            )

        if not self.can_rollback:
            raise ValidationError(
                "El lote no está disponible para reversión."
            )

        self.rollback_started_at = timezone.now()
        self.rolled_back_by = user
        self.rollback_reason = reason
        self.current_stage = "Revirtiendo importación"
        self.updated_by = user

        self.save()

    def mark_rolled_back(
        self,
        *,
        result=None,
        user=None,
    ):
        if not self.rollback_started_at:
            raise ValidationError(
                "La reversión no ha sido iniciada."
            )

        self.status = self.Status.ROLLED_BACK
        self.rolled_back_at = timezone.now()
        self.rolled_back_by = (
            user
            or self.rolled_back_by
        )
        self.rollback_result = result or {}
        self.rollback_available = False
        self.current_stage = "Importación revertida"
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
                "Solo puedes archivar un lote finalizado."
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