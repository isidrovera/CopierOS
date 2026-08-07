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

from .attendance_import_batch import AttendanceImportBatch


class AttendanceImportItem(models.Model):
    """
    Fila individual perteneciente a un lote de importación.

    Conserva:

    - Número de fila original.
    - Contenido recibido.
    - Contenido normalizado.
    - Trabajador identificado.
    - Dispositivo identificado.
    - Fecha y hora interpretadas.
    - Resultado de validación.
    - Detección de duplicados.
    - Registro creado o actualizado.
    - Advertencias y errores.
    - Reintentos.
    - Revisión manual.
    - Reversión individual.

    Este modelo permite auditar cada fila sin modificar ni perder
    el contenido original del archivo o sistema de origen.
    """

    class ItemType(models.TextChoices):
        ATTENDANCE_RECORD = (
            "attendance_record",
            "Marcación de asistencia",
        )
        EMPLOYEE = (
            "employee",
            "Trabajador",
        )
        WORK_SCHEDULE = (
            "work_schedule",
            "Horario",
        )
        SCHEDULE_ASSIGNMENT = (
            "schedule_assignment",
            "Asignación de horario",
        )
        WORK_LOCATION = (
            "work_location",
            "Ubicación de trabajo",
        )
        DEVICE_PERMISSION = (
            "device_permission",
            "Permiso de dispositivo",
        )
        LEAVE_REQUEST = (
            "leave_request",
            "Permiso o licencia",
        )
        OVERTIME_REQUEST = (
            "overtime_request",
            "Horas extras",
        )
        OPERATIONAL_SESSION = (
            "operational_session",
            "Sesión operativa",
        )
        MONTHLY_SUMMARY = (
            "monthly_summary",
            "Resumen mensual",
        )
        GENERIC = (
            "generic",
            "Registro genérico",
        )

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        PARSING = (
            "parsing",
            "Interpretando",
        )
        VALIDATING = (
            "validating",
            "Validando",
        )
        VALID = (
            "valid",
            "Válido",
        )
        VALID_WITH_WARNINGS = (
            "valid_with_warnings",
            "Válido con observaciones",
        )
        INVALID = (
            "invalid",
            "Inválido",
        )
        DUPLICATE = (
            "duplicate",
            "Duplicado",
        )
        PENDING_REVIEW = (
            "pending_review",
            "Pendiente de revisión",
        )
        APPROVED = (
            "approved",
            "Aprobado",
        )
        REJECTED = (
            "rejected",
            "Rechazado",
        )
        IMPORTING = (
            "importing",
            "Importando",
        )
        IMPORTED = (
            "imported",
            "Importado",
        )
        UPDATED = (
            "updated",
            "Actualizado",
        )
        UNCHANGED = (
            "unchanged",
            "Sin cambios",
        )
        SKIPPED = (
            "skipped",
            "Omitido",
        )
        FAILED = (
            "failed",
            "Fallido",
        )
        ROLLED_BACK = (
            "rolled_back",
            "Revertido",
        )
        CANCELLED = (
            "cancelled",
            "Cancelado",
        )

    class ValidationResult(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        VALID = (
            "valid",
            "Válido",
        )
        WARNING = (
            "warning",
            "Con observaciones",
        )
        INVALID = (
            "invalid",
            "Inválido",
        )
        DUPLICATE = (
            "duplicate",
            "Duplicado",
        )
        REVIEW_REQUIRED = (
            "review_required",
            "Requiere revisión",
        )

    class ImportResult(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        CREATED = (
            "created",
            "Creado",
        )
        UPDATED = (
            "updated",
            "Actualizado",
        )
        UNCHANGED = (
            "unchanged",
            "Sin cambios",
        )
        SKIPPED = (
            "skipped",
            "Omitido",
        )
        REJECTED = (
            "rejected",
            "Rechazado",
        )
        FAILED = (
            "failed",
            "Fallido",
        )
        ROLLED_BACK = (
            "rolled_back",
            "Revertido",
        )

    class DuplicateMatchType(models.TextChoices):
        NONE = (
            "none",
            "Sin duplicado",
        )
        EXACT = (
            "exact",
            "Coincidencia exacta",
        )
        SAME_EMPLOYEE_TIME = (
            "same_employee_time",
            "Mismo trabajador y hora",
        )
        SAME_DEVICE_REFERENCE = (
            "same_device_reference",
            "Misma referencia de dispositivo",
        )
        SAME_EXTERNAL_REFERENCE = (
            "same_external_reference",
            "Misma referencia externa",
        )
        SAME_CHECKSUM = (
            "same_checksum",
            "Mismo contenido",
        )
        POSSIBLE = (
            "possible",
            "Posible duplicado",
        )

    class EmployeeMatchResult(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        MATCHED = (
            "matched",
            "Trabajador identificado",
        )
        MULTIPLE_MATCHES = (
            "multiple_matches",
            "Varias coincidencias",
        )
        NOT_FOUND = (
            "not_found",
            "Trabajador no encontrado",
        )
        CREATED = (
            "created",
            "Trabajador creado",
        )
        NOT_REQUIRED = (
            "not_required",
            "No requerido",
        )

    class DeviceMatchResult(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        MATCHED = (
            "matched",
            "Dispositivo identificado",
        )
        MULTIPLE_MATCHES = (
            "multiple_matches",
            "Varias coincidencias",
        )
        NOT_FOUND = (
            "not_found",
            "Dispositivo no encontrado",
        )
        CREATED = (
            "created",
            "Dispositivo registrado",
        )
        NOT_REQUIRED = (
            "not_required",
            "No requerido",
        )

    class ErrorCategory(models.TextChoices):
        NONE = (
            "none",
            "Sin error",
        )
        FILE_STRUCTURE = (
            "file_structure",
            "Estructura de archivo",
        )
        REQUIRED_FIELD = (
            "required_field",
            "Campo obligatorio",
        )
        INVALID_FORMAT = (
            "invalid_format",
            "Formato inválido",
        )
        INVALID_DATE = (
            "invalid_date",
            "Fecha inválida",
        )
        INVALID_TIME = (
            "invalid_time",
            "Hora inválida",
        )
        INVALID_DATETIME = (
            "invalid_datetime",
            "Fecha y hora inválidas",
        )
        INVALID_VALUE = (
            "invalid_value",
            "Valor inválido",
        )
        EMPLOYEE_NOT_FOUND = (
            "employee_not_found",
            "Trabajador no encontrado",
        )
        EMPLOYEE_AMBIGUOUS = (
            "employee_ambiguous",
            "Trabajador ambiguo",
        )
        DEVICE_NOT_FOUND = (
            "device_not_found",
            "Dispositivo no encontrado",
        )
        DEVICE_AMBIGUOUS = (
            "device_ambiguous",
            "Dispositivo ambiguo",
        )
        DUPLICATE = (
            "duplicate",
            "Registro duplicado",
        )
        PERMISSION_DENIED = (
            "permission_denied",
            "Permiso denegado",
        )
        BUSINESS_RULE = (
            "business_rule",
            "Regla de negocio",
        )
        DATABASE = (
            "database",
            "Error de base de datos",
        )
        SYSTEM = (
            "system",
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

    import_batch = models.ForeignKey(
        AttendanceImportBatch,
        on_delete=models.PROTECT,
        related_name="items",
        verbose_name="Lote de importación",
    )

    sequence_number = models.PositiveBigIntegerField(
        default=1,
        verbose_name="Número de secuencia",
    )

    source_row_number = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Número de fila original",
    )

    source_sheet_name = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Hoja de origen",
    )

    item_type = models.CharField(
        max_length=40,
        choices=ItemType.choices,
        default=ItemType.ATTENDANCE_RECORD,
        db_index=True,
        verbose_name="Tipo de registro",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    validation_result = models.CharField(
        max_length=30,
        choices=ValidationResult.choices,
        default=ValidationResult.PENDING,
        db_index=True,
        verbose_name="Resultado de validación",
    )

    import_result = models.CharField(
        max_length=30,
        choices=ImportResult.choices,
        default=ImportResult.PENDING,
        db_index=True,
        verbose_name="Resultado de importación",
    )

    raw_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos originales",
    )

    normalized_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos normalizados",
    )

    transformed_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos transformados",
    )

    validated_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos validados",
    )

    previous_values = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Valores anteriores",
    )

    imported_values = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Valores importados",
    )

    changed_fields = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Campos modificados",
    )

    employee_profile = models.ForeignKey(
        "attendance.EmployeeProfile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="import_items",
        verbose_name="Trabajador identificado",
    )

    employee_match_result = models.CharField(
        max_length=30,
        choices=EmployeeMatchResult.choices,
        default=EmployeeMatchResult.PENDING,
        db_index=True,
        verbose_name="Resultado de identificación del trabajador",
    )

    employee_match_value = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Valor usado para identificar al trabajador",
    )

    employee_match_field = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Campo usado para identificar al trabajador",
    )

    employee_match_candidates = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Candidatos de trabajador",
    )

    attendance_device = models.ForeignKey(
        "attendance.AttendanceDevice",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="import_items",
        verbose_name="Dispositivo identificado",
    )

    device_match_result = models.CharField(
        max_length=30,
        choices=DeviceMatchResult.choices,
        default=DeviceMatchResult.PENDING,
        db_index=True,
        verbose_name="Resultado de identificación del dispositivo",
    )

    device_match_value = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Valor usado para identificar el dispositivo",
    )

    device_match_field = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Campo usado para identificar el dispositivo",
    )

    device_match_candidates = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Candidatos de dispositivo",
    )

    parsed_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha interpretada",
    )

    parsed_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora interpretada",
    )

    parsed_datetime = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha y hora interpretadas",
    )

    source_timezone_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Zona horaria original",
    )

    external_reference = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Referencia externa",
    )

    device_record_id = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="ID de registro del dispositivo",
    )

    source_checksum = models.CharField(
        max_length=128,
        blank=True,
        db_index=True,
        verbose_name="Checksum de la fila",
    )

    is_duplicate = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Es duplicado",
    )

    duplicate_match_type = models.CharField(
        max_length=40,
        choices=DuplicateMatchType.choices,
        default=DuplicateMatchType.NONE,
        db_index=True,
        verbose_name="Tipo de coincidencia duplicada",
    )

    duplicate_of_item = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="duplicate_items",
        verbose_name="Duplicado de la fila",
    )

    duplicate_content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_import_item_duplicates",
        verbose_name="Tipo de registro duplicado",
    )

    duplicate_object_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="ID del registro duplicado",
    )

    duplicate_object = GenericForeignKey(
        "duplicate_content_type",
        "duplicate_object_id",
    )

    duplicate_details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Detalle del duplicado",
    )

    result_content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_import_item_results",
        verbose_name="Tipo de registro resultante",
    )

    result_object_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="ID del registro resultante",
    )

    result_object = GenericForeignKey(
        "result_content_type",
        "result_object_id",
    )

    result_model = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Modelo resultante",
    )

    result_representation = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Representación del resultado",
    )

    attendance_record = models.ForeignKey(
        "attendance.AttendanceRecord",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="import_items",
        verbose_name="Marcación resultante",
    )

    daily_attendance = models.ForeignKey(
        "attendance.DailyAttendance",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="import_items",
        verbose_name="Asistencia diaria resultante",
    )

    warnings = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Advertencias",
    )

    validation_errors = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Errores de validación",
    )

    error_category = models.CharField(
        max_length=40,
        choices=ErrorCategory.choices,
        default=ErrorCategory.NONE,
        db_index=True,
        verbose_name="Categoría del error",
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

    requires_review = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere revisión",
    )

    review_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de revisión",
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
        related_name="attendance_import_items_reviewed",
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
        related_name="attendance_import_items_approved",
        verbose_name="Aprobado por",
    )

    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Rechazado el",
    )

    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_import_items_rejected",
        verbose_name="Rechazado por",
    )

    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de rechazo",
    )

    parsing_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Interpretación iniciada el",
    )

    validation_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Validación iniciada el",
    )

    validation_finished_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Validación finalizada el",
    )

    import_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Importación iniciada el",
    )

    import_finished_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Importación finalizada el",
    )

    processing_duration_milliseconds = (
        models.PositiveBigIntegerField(
            default=0,
            verbose_name="Duración del procesamiento",
        )
    )

    retry_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Cantidad de reintentos",
    )

    maximum_retries = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Máximo de reintentos",
    )

    next_retry_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Próximo reintento",
    )

    retry_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="retry_items",
        verbose_name="Reintento de",
    )

    rollback_available = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Permite reversión",
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
        related_name="attendance_import_items_rolled_back",
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

    idempotency_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        verbose_name="Clave de idempotencia",
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
        related_name="attendance_import_items_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_import_items_updated",
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
        related_name="attendance_import_items_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Fila de importación de asistencia"
        verbose_name_plural = (
            "Filas de importación de asistencia"
        )

        ordering = (
            "import_batch",
            "sequence_number",
        )

        constraints = (
            models.UniqueConstraint(
                fields=(
                    "import_batch",
                    "sequence_number",
                ),
                name="att_iitem_batch_seq_unique",
            ),
            models.UniqueConstraint(
                fields=(
                    "import_batch",
                    "source_sheet_name",
                    "source_row_number",
                ),
                condition=models.Q(
                    source_row_number__isnull=False,
                ),
                name="att_iitem_source_row_unique",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    retry_count__lte=models.F(
                        "maximum_retries"
                    ),
                ),
                name="att_iitem_retry_lte_max",
            ),
        )

        indexes = (
            models.Index(
                fields=(
                    "import_batch",
                    "status",
                    "sequence_number",
                ),
                name="att_iitem_batch_status_idx",
            ),
            models.Index(
                fields=(
                    "import_batch",
                    "validation_result",
                    "import_result",
                ),
                name="att_iitem_results_idx",
            ),
            models.Index(
                fields=(
                    "source_sheet_name",
                    "source_row_number",
                ),
                name="att_iitem_source_row_idx",
            ),
            models.Index(
                fields=(
                    "employee_profile",
                    "parsed_datetime",
                    "status",
                ),
                name="att_iitem_emp_datetime_idx",
            ),
            models.Index(
                fields=(
                    "attendance_device",
                    "device_record_id",
                ),
                name="att_iitem_device_record_idx",
            ),
            models.Index(
                fields=(
                    "employee_match_result",
                    "device_match_result",
                ),
                name="att_iitem_match_results_idx",
            ),
            models.Index(
                fields=(
                    "is_duplicate",
                    "duplicate_match_type",
                ),
                name="att_iitem_duplicate_idx",
            ),
            models.Index(
                fields=(
                    "duplicate_content_type",
                    "duplicate_object_id",
                ),
                name="att_iitem_dup_object_idx",
            ),
            models.Index(
                fields=(
                    "result_content_type",
                    "result_object_id",
                ),
                name="att_iitem_result_object_idx",
            ),
            models.Index(
                fields=(
                    "attendance_record",
                    "daily_attendance",
                ),
                name="att_iitem_attendance_idx",
            ),
            models.Index(
                fields=(
                    "error_category",
                    "error_code",
                    "status",
                ),
                name="att_iitem_error_idx",
            ),
            models.Index(
                fields=(
                    "requires_review",
                    "reviewed_at",
                    "status",
                ),
                name="att_iitem_review_idx",
            ),
            models.Index(
                fields=(
                    "next_retry_at",
                    "retry_count",
                    "status",
                ),
                name="att_iitem_retry_idx",
            ),
            models.Index(
                fields=(
                    "rollback_available",
                    "rolled_back_at",
                ),
                name="att_iitem_rollback_idx",
            ),
            models.Index(
                fields=(
                    "external_reference",
                    "source_checksum",
                ),
                name="att_iitem_external_idx",
            ),
        )

    def __str__(self):
        row_reference = (
            f"{self.source_sheet_name}:"
            f"{self.source_row_number}"
            if self.source_row_number
            else f"Secuencia {self.sequence_number}"
        )

        return (
            f"{self.import_batch.batch_number} - "
            f"{row_reference} - "
            f"{self.get_status_display()}"
        )

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_valid(self):
        return self.validation_result in (
            self.ValidationResult.VALID,
            self.ValidationResult.WARNING,
        )

    @property
    def is_finished(self):
        return self.status in (
            self.Status.IMPORTED,
            self.Status.UPDATED,
            self.Status.UNCHANGED,
            self.Status.SKIPPED,
            self.Status.REJECTED,
            self.Status.FAILED,
            self.Status.ROLLED_BACK,
            self.Status.CANCELLED,
        )

    @property
    def has_warnings(self):
        return bool(self.warnings)

    @property
    def has_errors(self):
        return bool(
            self.validation_errors
            or self.error_message
        )

    @property
    def can_import(self):
        return (
            self.status in (
                self.Status.VALID,
                self.Status.VALID_WITH_WARNINGS,
                self.Status.APPROVED,
            )
            and not self.is_duplicate
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
                self.Status.IMPORTED,
                self.Status.UPDATED,
            )
            and not self.rolled_back_at
            and self.archived_at is None
        )

    @property
    def result_reference(self):
        if self.result_model and self.result_object_id:
            return (
                f"{self.result_model}:"
                f"{self.result_object_id}"
            )

        return ""

    def calculate_processing_duration(self):
        start_at = (
            self.parsing_started_at
            or self.validation_started_at
            or self.import_started_at
        )

        end_at = (
            self.import_finished_at
            or self.validation_finished_at
        )

        if (
            not start_at
            or not end_at
            or end_at <= start_at
        ):
            self.processing_duration_milliseconds = 0
            return 0

        self.processing_duration_milliseconds = int(
            (
                end_at - start_at
            ).total_seconds()
            * 1000
        )

        return self.processing_duration_milliseconds

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.import_batch_id
            and self.import_batch.archived_at
        ):
            errors["import_batch"] = (
                "El lote de importación está archivado."
            )

        if (
            self.employee_profile_id
            and self.employee_profile.archived_at
        ):
            errors["employee_profile"] = (
                "El perfil laboral está archivado."
            )

        if (
            self.attendance_device_id
            and self.attendance_device.archived_at
        ):
            errors["attendance_device"] = (
                "El dispositivo está archivado."
            )

        json_object_fields = (
            "raw_data",
            "normalized_data",
            "transformed_data",
            "validated_data",
            "previous_values",
            "imported_values",
            "duplicate_details",
            "rollback_result",
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

        json_list_fields = (
            "changed_fields",
            "employee_match_candidates",
            "device_match_candidates",
            "warnings",
            "validation_errors",
        )

        for field_name in json_list_fields:
            if not isinstance(
                getattr(self, field_name),
                list,
            ):
                errors[field_name] = (
                    "El valor debe ser una lista JSON."
                )

        if (
            self.employee_match_result
            == self.EmployeeMatchResult.MATCHED
            and not self.employee_profile_id
        ):
            errors["employee_profile"] = (
                "Debes vincular el trabajador identificado."
            )

        if (
            self.employee_match_result
            == self.EmployeeMatchResult.CREATED
            and not self.employee_profile_id
        ):
            errors["employee_profile"] = (
                "Debes vincular el trabajador creado."
            )

        if (
            self.employee_match_result
            == self.EmployeeMatchResult.MULTIPLE_MATCHES
            and not self.employee_match_candidates
        ):
            errors["employee_match_candidates"] = (
                "Debes registrar las coincidencias encontradas."
            )

        if (
            self.device_match_result
            == self.DeviceMatchResult.MATCHED
            and not self.attendance_device_id
        ):
            errors["attendance_device"] = (
                "Debes vincular el dispositivo identificado."
            )

        if (
            self.device_match_result
            == self.DeviceMatchResult.CREATED
            and not self.attendance_device_id
        ):
            errors["attendance_device"] = (
                "Debes vincular el dispositivo registrado."
            )

        if (
            self.device_match_result
            == self.DeviceMatchResult.MULTIPLE_MATCHES
            and not self.device_match_candidates
        ):
            errors["device_match_candidates"] = (
                "Debes registrar los dispositivos encontrados."
            )

        if (
            self.parsed_datetime
            and self.parsed_date
            and self.parsed_datetime.date()
            != self.parsed_date
        ):
            errors["parsed_date"] = (
                "La fecha interpretada no coincide con "
                "la fecha y hora."
            )

        if (
            self.parsed_datetime
            and self.parsed_time
            and self.parsed_datetime.time().replace(
                tzinfo=None,
            )
            != self.parsed_time.replace(
                tzinfo=None,
            )
        ):
            errors["parsed_time"] = (
                "La hora interpretada no coincide con "
                "la fecha y hora."
            )

        if bool(self.duplicate_content_type_id) != bool(
            self.duplicate_object_id
        ):
            errors["duplicate_object_id"] = (
                "Debes registrar tanto el tipo como el ID "
                "del objeto duplicado."
            )

        if bool(self.result_content_type_id) != bool(
            self.result_object_id
        ):
            errors["result_object_id"] = (
                "Debes registrar tanto el tipo como el ID "
                "del registro resultante."
            )

        if self.is_duplicate:
            if (
                self.duplicate_match_type
                == self.DuplicateMatchType.NONE
            ):
                errors["duplicate_match_type"] = (
                    "Debes indicar el tipo de duplicado."
                )

            if not any(
                (
                    self.duplicate_of_item_id,
                    self.duplicate_content_type_id,
                    self.duplicate_details,
                )
            ):
                errors["duplicate_details"] = (
                    "Debes registrar la referencia "
                    "del duplicado."
                )

        elif (
            self.duplicate_match_type
            != self.DuplicateMatchType.NONE
        ):
            errors["duplicate_match_type"] = (
                "Una fila no duplicada debe tener "
                "el tipo 'Sin duplicado'."
            )

        if (
            self.duplicate_of_item_id
            and self.duplicate_of_item_id == self.id
        ):
            errors["duplicate_of_item"] = (
                "Una fila no puede ser duplicada de sí misma."
            )

        if (
            self.duplicate_of_item_id
            and self.duplicate_of_item.import_batch_id
            != self.import_batch_id
        ):
            errors["duplicate_of_item"] = (
                "La fila duplicada debe pertenecer "
                "al mismo lote."
            )

        if (
            self.status == self.Status.PARSING
            and not self.parsing_started_at
        ):
            errors["parsing_started_at"] = (
                "Una fila en interpretación debe registrar "
                "la fecha de inicio."
            )

        if (
            self.status == self.Status.VALIDATING
            and not self.validation_started_at
        ):
            errors["validation_started_at"] = (
                "Una fila en validación debe registrar "
                "la fecha de inicio."
            )

        if (
            self.status in (
                self.Status.VALID,
                self.Status.VALID_WITH_WARNINGS,
                self.Status.INVALID,
                self.Status.DUPLICATE,
                self.Status.PENDING_REVIEW,
                self.Status.APPROVED,
                self.Status.REJECTED,
                self.Status.IMPORTING,
                self.Status.IMPORTED,
                self.Status.UPDATED,
                self.Status.UNCHANGED,
                self.Status.SKIPPED,
                self.Status.FAILED,
            )
            and not self.validation_finished_at
        ):
            errors["validation_finished_at"] = (
                "La fila debe registrar la finalización "
                "de la validación."
            )

        if (
            self.status == self.Status.VALID
            and self.validation_result
            != self.ValidationResult.VALID
        ):
            errors["validation_result"] = (
                "El estado válido requiere resultado válido."
            )

        if (
            self.status == self.Status.VALID_WITH_WARNINGS
            and self.validation_result
            != self.ValidationResult.WARNING
        ):
            errors["validation_result"] = (
                "El estado con observaciones requiere "
                "resultado con observaciones."
            )

        if (
            self.status == self.Status.VALID_WITH_WARNINGS
            and not self.warnings
        ):
            errors["warnings"] = (
                "Debes registrar al menos una observación."
            )

        if (
            self.status == self.Status.INVALID
            and self.validation_result
            != self.ValidationResult.INVALID
        ):
            errors["validation_result"] = (
                "El estado inválido requiere resultado inválido."
            )

        if (
            self.status == self.Status.INVALID
            and not self.validation_errors
        ):
            errors["validation_errors"] = (
                "Debes registrar los errores de validación."
            )

        if (
            self.status == self.Status.DUPLICATE
            and self.validation_result
            != self.ValidationResult.DUPLICATE
        ):
            errors["validation_result"] = (
                "El estado duplicado requiere "
                "resultado duplicado."
            )

        if (
            self.status == self.Status.PENDING_REVIEW
            and self.validation_result
            != self.ValidationResult.REVIEW_REQUIRED
        ):
            errors["validation_result"] = (
                "La revisión pendiente requiere "
                "resultado de revisión."
            )

        if (
            self.requires_review
            and not self.review_reason.strip()
        ):
            errors["review_reason"] = (
                "Debes indicar el motivo de revisión."
            )

        if (
            self.reviewed_at
            and not self.reviewed_by_id
        ):
            errors["reviewed_by"] = (
                "Debes indicar quién revisó la fila."
            )

        if (
            self.status == self.Status.APPROVED
            and not self.approved_at
        ):
            errors["approved_at"] = (
                "Una fila aprobada debe registrar "
                "la fecha de aprobación."
            )

        if (
            self.status == self.Status.REJECTED
            and not self.rejection_reason.strip()
        ):
            errors["rejection_reason"] = (
                "Debes indicar el motivo de rechazo."
            )

        if (
            self.status == self.Status.IMPORTING
            and not self.import_started_at
        ):
            errors["import_started_at"] = (
                "Una fila en importación debe registrar "
                "la fecha de inicio."
            )

        if self.status in (
            self.Status.IMPORTED,
            self.Status.UPDATED,
            self.Status.UNCHANGED,
            self.Status.SKIPPED,
            self.Status.FAILED,
            self.Status.ROLLED_BACK,
        ) and not self.import_finished_at:
            errors["import_finished_at"] = (
                "La fila finalizada debe registrar "
                "el fin de importación."
            )

        import_result_by_status = {
            self.Status.IMPORTED: (
                self.ImportResult.CREATED
            ),
            self.Status.UPDATED: (
                self.ImportResult.UPDATED
            ),
            self.Status.UNCHANGED: (
                self.ImportResult.UNCHANGED
            ),
            self.Status.SKIPPED: (
                self.ImportResult.SKIPPED
            ),
            self.Status.REJECTED: (
                self.ImportResult.REJECTED
            ),
            self.Status.FAILED: (
                self.ImportResult.FAILED
            ),
            self.Status.ROLLED_BACK: (
                self.ImportResult.ROLLED_BACK
            ),
        }

        expected_import_result = import_result_by_status.get(
            self.status
        )

        if (
            expected_import_result
            and self.import_result
            != expected_import_result
        ):
            errors["import_result"] = (
                "El resultado de importación no corresponde "
                "al estado de la fila."
            )

        if (
            self.status == self.Status.FAILED
            and not self.error_message.strip()
        ):
            errors["error_message"] = (
                "Una fila fallida debe registrar el error."
            )

        if (
            self.status == self.Status.FAILED
            and self.error_category
            == self.ErrorCategory.NONE
        ):
            errors["error_category"] = (
                "Debes indicar la categoría del error."
            )

        if (
            self.status in (
                self.Status.IMPORTED,
                self.Status.UPDATED,
            )
            and not any(
                (
                    self.result_content_type_id,
                    self.attendance_record_id,
                    self.daily_attendance_id,
                )
            )
        ):
            errors["result_object_id"] = (
                "Debes registrar el objeto creado "
                "o actualizado."
            )

        if (
            self.attendance_record_id
            and self.employee_profile_id
            and self.attendance_record.employee_profile_id
            != self.employee_profile_id
        ):
            errors["attendance_record"] = (
                "La marcación resultante no corresponde "
                "al trabajador identificado."
            )

        if (
            self.daily_attendance_id
            and self.employee_profile_id
            and self.daily_attendance.employee_profile_id
            != self.employee_profile_id
        ):
            errors["daily_attendance"] = (
                "La asistencia diaria no corresponde "
                "al trabajador identificado."
            )

        if (
            self.daily_attendance_id
            and self.parsed_date
            and self.daily_attendance.date
            != self.parsed_date
        ):
            errors["daily_attendance"] = (
                "La asistencia diaria no corresponde "
                "a la fecha interpretada."
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
            self.retry_of_id
            and self.retry_of_id == self.id
        ):
            errors["retry_of"] = (
                "Una fila no puede ser reintento de sí misma."
            )

        if (
            self.retry_of_id
            and self.retry_of.import_batch_id
            != self.import_batch_id
        ):
            errors["retry_of"] = (
                "La fila original debe pertenecer "
                "al mismo lote."
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
            and not self.rollback_reason.strip()
        ):
            errors["rollback_reason"] = (
                "Debes indicar el motivo de reversión."
            )

        if (
            self.rolled_back_at
            and not self.rollback_available
        ):
            errors["rollback_available"] = (
                "La fila no estaba habilitada para reversión."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.source_sheet_name = str(
            self.source_sheet_name or ""
        ).strip()

        self.employee_match_value = str(
            self.employee_match_value or ""
        ).strip()

        self.employee_match_field = str(
            self.employee_match_field or ""
        ).strip()

        self.device_match_value = str(
            self.device_match_value or ""
        ).strip()

        self.device_match_field = str(
            self.device_match_field or ""
        ).strip()

        self.external_reference = str(
            self.external_reference or ""
        ).strip()

        self.device_record_id = str(
            self.device_record_id or ""
        ).strip()

        self.source_checksum = str(
            self.source_checksum or ""
        ).strip()

        if self.result_content_type_id:
            self.result_model = (
                f"{self.result_content_type.app_label}."
                f"{self.result_content_type.model}"
            )

        if (
            self.result_object is not None
            and not self.result_representation
        ):
            self.result_representation = str(
                self.result_object
            )[:500]

        if (
            self.validation_finished_at
            or self.import_finished_at
        ):
            self.calculate_processing_duration()

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def start_parsing(
        self,
        user=None,
    ):
        if self.status != self.Status.PENDING:
            raise ValidationError(
                "Solo puedes interpretar una fila pendiente."
            )

        self.status = self.Status.PARSING
        self.parsing_started_at = timezone.now()
        self.updated_by = user

        self.save()

    def start_validation(
        self,
        user=None,
    ):
        if self.status not in (
            self.Status.PENDING,
            self.Status.PARSING,
            self.Status.FAILED,
        ):
            raise ValidationError(
                "La fila no está disponible para validación."
            )

        self.status = self.Status.VALIDATING
        self.validation_result = (
            self.ValidationResult.PENDING
        )
        self.validation_started_at = timezone.now()
        self.validation_finished_at = None
        self.warnings = []
        self.validation_errors = []
        self.error_category = self.ErrorCategory.NONE
        self.error_code = ""
        self.error_message = ""
        self.exception_type = ""
        self.stack_trace = ""
        self.updated_by = user

        self.save()

    def mark_valid(
        self,
        *,
        validated_data=None,
        user=None,
    ):
        if self.status != self.Status.VALIDATING:
            raise ValidationError(
                "La fila no está validándose."
            )

        self.status = self.Status.VALID
        self.validation_result = (
            self.ValidationResult.VALID
        )
        self.validated_data = validated_data or {}
        self.validation_finished_at = timezone.now()
        self.requires_review = False
        self.review_reason = ""
        self.error_category = self.ErrorCategory.NONE
        self.error_code = ""
        self.error_message = ""
        self.updated_by = user

        self.save()

    def mark_valid_with_warnings(
        self,
        *,
        warnings,
        validated_data=None,
        requires_review=False,
        review_reason="",
        user=None,
    ):
        warnings = list(
            warnings or []
        )

        if not warnings:
            raise ValidationError(
                "Debes registrar al menos una advertencia."
            )

        if self.status != self.Status.VALIDATING:
            raise ValidationError(
                "La fila no está validándose."
            )

        self.validation_result = (
            self.ValidationResult.WARNING
        )
        self.validated_data = validated_data or {}
        self.validation_finished_at = timezone.now()
        self.warnings = warnings
        self.requires_review = requires_review
        self.review_reason = str(
            review_reason or ""
        ).strip()
        self.updated_by = user

        if requires_review:
            self.status = self.Status.PENDING_REVIEW
            self.validation_result = (
                self.ValidationResult.REVIEW_REQUIRED
            )

            if not self.review_reason:
                self.review_reason = (
                    "La fila contiene observaciones "
                    "que requieren revisión."
                )
        else:
            self.status = (
                self.Status.VALID_WITH_WARNINGS
            )

        self.save()

    def mark_invalid(
        self,
        *,
        validation_errors,
        error_category=ErrorCategory.INVALID_VALUE,
        error_code="",
        error_message="",
        user=None,
    ):
        validation_errors = list(
            validation_errors or []
        )

        if not validation_errors:
            raise ValidationError(
                "Debes registrar al menos un error "
                "de validación."
            )

        if self.status != self.Status.VALIDATING:
            raise ValidationError(
                "La fila no está validándose."
            )

        self.status = self.Status.INVALID
        self.validation_result = (
            self.ValidationResult.INVALID
        )
        self.validation_finished_at = timezone.now()
        self.validation_errors = validation_errors
        self.error_category = error_category
        self.error_code = str(
            error_code or ""
        ).strip()
        self.error_message = str(
            error_message
            or "La fila contiene información inválida."
        ).strip()
        self.updated_by = user

        self.save()

    def mark_duplicate(
        self,
        *,
        duplicate_match_type,
        duplicate_of_item=None,
        duplicate_object=None,
        duplicate_details=None,
        user=None,
    ):
        if self.status not in (
            self.Status.PENDING,
            self.Status.PARSING,
            self.Status.VALIDATING,
        ):
            raise ValidationError(
                "La fila no puede marcarse como duplicada."
            )

        if duplicate_match_type == (
            self.DuplicateMatchType.NONE
        ):
            raise ValidationError(
                "Debes indicar el tipo de duplicado."
            )

        duplicate_content_type = None
        duplicate_object_id = ""

        if duplicate_object is not None:
            duplicate_content_type = (
                ContentType.objects.get_for_model(
                    duplicate_object,
                    for_concrete_model=False,
                )
            )
            duplicate_object_id = str(
                duplicate_object.pk
            )

        if (
            duplicate_of_item is None
            and duplicate_object is None
            and not duplicate_details
        ):
            raise ValidationError(
                "Debes indicar la referencia del duplicado."
            )

        self.status = self.Status.DUPLICATE
        self.validation_result = (
            self.ValidationResult.DUPLICATE
        )
        self.validation_finished_at = timezone.now()
        self.is_duplicate = True
        self.duplicate_match_type = (
            duplicate_match_type
        )
        self.duplicate_of_item = duplicate_of_item
        self.duplicate_content_type = (
            duplicate_content_type
        )
        self.duplicate_object_id = (
            duplicate_object_id
        )
        self.duplicate_details = (
            duplicate_details or {}
        )
        self.updated_by = user

        self.save()

    def approve(
        self,
        *,
        user,
        observation="",
        validated_data=None,
    ):
        if self.status not in (
            self.Status.PENDING_REVIEW,
            self.Status.VALID_WITH_WARNINGS,
        ):
            raise ValidationError(
                "La fila no está pendiente de aprobación."
            )

        self.status = self.Status.APPROVED
        self.validation_result = (
            self.ValidationResult.WARNING
            if self.warnings
            else self.ValidationResult.VALID
        )
        self.requires_review = False
        self.reviewed_at = timezone.now()
        self.reviewed_by = user
        self.review_observation = str(
            observation or ""
        ).strip()
        self.approved_at = timezone.now()
        self.approved_by = user

        if validated_data is not None:
            self.validated_data = validated_data

        self.updated_by = user

        self.save()

    def reject(
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
                "Debes indicar el motivo de rechazo."
            )

        if self.status not in (
            self.Status.PENDING_REVIEW,
            self.Status.VALID_WITH_WARNINGS,
            self.Status.INVALID,
            self.Status.DUPLICATE,
        ):
            raise ValidationError(
                "La fila no está disponible para rechazo."
            )

        self.status = self.Status.REJECTED
        self.import_result = (
            self.ImportResult.REJECTED
        )
        self.rejected_at = timezone.now()
        self.rejected_by = user
        self.rejection_reason = reason
        self.import_finished_at = timezone.now()
        self.updated_by = user

        self.save()

    def start_import(
        self,
        user=None,
    ):
        if not self.can_import:
            raise ValidationError(
                "La fila no está disponible para importación."
            )

        if self.import_batch.dry_run:
            raise ValidationError(
                "El lote está configurado únicamente "
                "para validación."
            )

        self.status = self.Status.IMPORTING
        self.import_result = (
            self.ImportResult.PENDING
        )
        self.import_started_at = timezone.now()
        self.import_finished_at = None
        self.error_category = self.ErrorCategory.NONE
        self.error_code = ""
        self.error_message = ""
        self.exception_type = ""
        self.stack_trace = ""
        self.updated_by = user

        self.save()

    def mark_created(
        self,
        *,
        result_object,
        imported_values=None,
        daily_attendance=None,
        rollback_available=True,
        user=None,
    ):
        if self.status != self.Status.IMPORTING:
            raise ValidationError(
                "La fila no está importándose."
            )

        if result_object is None:
            raise ValidationError(
                "Debes indicar el registro creado."
            )

        content_type = ContentType.objects.get_for_model(
            result_object,
            for_concrete_model=False,
        )

        now = timezone.now()

        self.status = self.Status.IMPORTED
        self.import_result = self.ImportResult.CREATED
        self.result_content_type = content_type
        self.result_object_id = str(
            result_object.pk
        )
        self.result_representation = str(
            result_object
        )[:500]
        self.imported_values = imported_values or {}
        self.import_finished_at = now
        self.rollback_available = rollback_available
        self.daily_attendance = daily_attendance

        if (
            content_type.app_label == "attendance"
            and content_type.model == "attendancerecord"
        ):
            self.attendance_record = result_object

        self.updated_by = user
        self.save()

    def mark_updated(
        self,
        *,
        result_object,
        previous_values,
        imported_values,
        changed_fields,
        daily_attendance=None,
        rollback_available=True,
        user=None,
    ):
        if self.status != self.Status.IMPORTING:
            raise ValidationError(
                "La fila no está importándose."
            )

        if result_object is None:
            raise ValidationError(
                "Debes indicar el registro actualizado."
            )

        content_type = ContentType.objects.get_for_model(
            result_object,
            for_concrete_model=False,
        )

        now = timezone.now()

        self.status = self.Status.UPDATED
        self.import_result = self.ImportResult.UPDATED
        self.result_content_type = content_type
        self.result_object_id = str(
            result_object.pk
        )
        self.result_representation = str(
            result_object
        )[:500]
        self.previous_values = previous_values or {}
        self.imported_values = imported_values or {}
        self.changed_fields = changed_fields or []
        self.import_finished_at = now
        self.rollback_available = rollback_available
        self.daily_attendance = daily_attendance

        if (
            content_type.app_label == "attendance"
            and content_type.model == "attendancerecord"
        ):
            self.attendance_record = result_object

        self.updated_by = user
        self.save()

    def mark_unchanged(
        self,
        *,
        result_object=None,
        imported_values=None,
        user=None,
    ):
        if self.status != self.Status.IMPORTING:
            raise ValidationError(
                "La fila no está importándose."
            )

        if result_object is not None:
            content_type = ContentType.objects.get_for_model(
                result_object,
                for_concrete_model=False,
            )

            self.result_content_type = content_type
            self.result_object_id = str(
                result_object.pk
            )
            self.result_representation = str(
                result_object
            )[:500]

        self.status = self.Status.UNCHANGED
        self.import_result = self.ImportResult.UNCHANGED
        self.imported_values = imported_values or {}
        self.import_finished_at = timezone.now()
        self.rollback_available = False
        self.updated_by = user

        self.save()

    def skip(
        self,
        *,
        reason,
        user=None,
    ):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de omisión."
            )

        if self.is_finished:
            raise ValidationError(
                "La fila ya se encuentra finalizada."
            )

        now = timezone.now()

        if not self.validation_finished_at:
            self.validation_finished_at = now

        self.status = self.Status.SKIPPED
        self.import_result = self.ImportResult.SKIPPED
        self.import_finished_at = now
        self.warnings = [
            *list(self.warnings or []),
            {
                "code": "SKIPPED",
                "message": reason,
                "recorded_at": now.isoformat(),
            },
        ]
        self.updated_by = user

        self.save()

    def mark_failed(
        self,
        *,
        error,
        error_category=ErrorCategory.SYSTEM,
        error_code="",
        exception_type="",
        stack_trace="",
        next_retry_at=None,
        user=None,
    ):
        error = str(
            error or ""
        ).strip()

        if not error:
            raise ValidationError(
                "Debes indicar el error de importación."
            )

        if self.is_finished:
            raise ValidationError(
                "La fila ya se encuentra finalizada."
            )

        now = timezone.now()

        if not self.validation_finished_at:
            self.validation_finished_at = now

        if not self.import_started_at:
            self.import_started_at = now

        self.status = self.Status.FAILED
        self.import_result = self.ImportResult.FAILED
        self.import_finished_at = now
        self.error_category = error_category
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
        self.requires_review = True
        self.review_reason = error

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
        sequence_number,
        next_retry_at=None,
        user=None,
    ):
        if not self.can_retry:
            raise ValidationError(
                "La fila no admite otro reintento."
            )

        retry_item = AttendanceImportItem(
            import_batch=self.import_batch,
            sequence_number=sequence_number,
            source_row_number=self.source_row_number,
            source_sheet_name=self.source_sheet_name,
            item_type=self.item_type,
            raw_data=dict(
                self.raw_data or {}
            ),
            normalized_data=dict(
                self.normalized_data or {}
            ),
            transformed_data=dict(
                self.transformed_data or {}
            ),
            employee_profile=self.employee_profile,
            employee_match_result=(
                self.employee_match_result
            ),
            employee_match_value=self.employee_match_value,
            employee_match_field=self.employee_match_field,
            employee_match_candidates=list(
                self.employee_match_candidates or []
            ),
            attendance_device=self.attendance_device,
            device_match_result=self.device_match_result,
            device_match_value=self.device_match_value,
            device_match_field=self.device_match_field,
            device_match_candidates=list(
                self.device_match_candidates or []
            ),
            parsed_date=self.parsed_date,
            parsed_time=self.parsed_time,
            parsed_datetime=self.parsed_datetime,
            source_timezone_name=self.source_timezone_name,
            external_reference=self.external_reference,
            device_record_id=self.device_record_id,
            source_checksum=self.source_checksum,
            retry_count=self.retry_count + 1,
            maximum_retries=self.maximum_retries,
            next_retry_at=next_retry_at,
            retry_of=self,
            metadata={
                **dict(self.metadata or {}),
                "original_item_id": str(self.id),
                "original_sequence_number": (
                    self.sequence_number
                ),
            },
            created_by=user,
            updated_by=user,
        )

        retry_item.save()

        self.next_retry_at = next_retry_at
        self.updated_by = user

        self.save(
            update_fields=[
                "next_retry_at",
                "updated_by",
                "updated_at",
            ]
        )

        return retry_item

    def mark_rolled_back(
        self,
        *,
        user,
        reason,
        result=None,
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
                "La fila no está disponible para reversión."
            )

        now = timezone.now()

        self.status = self.Status.ROLLED_BACK
        self.import_result = (
            self.ImportResult.ROLLED_BACK
        )
        self.rolled_back_at = now
        self.rolled_back_by = user
        self.rollback_reason = reason
        self.rollback_result = result or {}
        self.import_finished_at = (
            self.import_finished_at
            or now
        )
        self.rollback_available = False
        self.updated_by = user

        self.save()

    def cancel(
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
                "Debes indicar el motivo de cancelación."
            )

        if self.is_finished:
            raise ValidationError(
                "La fila ya está finalizada."
            )

        now = timezone.now()

        if not self.validation_finished_at:
            self.validation_finished_at = now

        self.status = self.Status.CANCELLED
        self.import_result = (
            self.ImportResult.SKIPPED
        )
        self.import_finished_at = now
        self.warnings = [
            *list(self.warnings or []),
            {
                "code": "CANCELLED",
                "message": reason,
                "recorded_at": now.isoformat(),
            },
        ]
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
                "Solo puedes archivar una fila finalizada."
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