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

from .attendance_export_batch import AttendanceExportBatch

class AttendanceExportItem(models.Model):
    """
    Registro individual procesado dentro de una exportación.

    Cada elemento puede representar:

    - Una marcación.
    - Una asistencia diaria.
    - Una incidencia.
    - Un permiso.
    - Una corrección.
    - Una solicitud de horas extras.
    - Una sesión operativa.
    - Un resumen mensual.
    - Un trabajador.
    - Un registro de auditoría.
    - Cualquier objeto genérico.

    Conserva:

    - Objeto de origen.
    - Trabajador relacionado.
    - Fecha del registro.
    - Valores originales.
    - Valores transformados.
    - Datos exportados.
    - Columnas omitidas.
    - Datos sensibles ocultados.
    - Advertencias.
    - Errores.
    - Estado individual.
    - Número de fila o posición en el archivo.
    - Reintentos y revisión manual.
    """

    class ItemType(models.TextChoices):
        ATTENDANCE_RECORD = (
            "attendance_record",
            "Marcación de asistencia",
        )
        DAILY_ATTENDANCE = (
            "daily_attendance",
            "Asistencia diaria",
        )
        ATTENDANCE_INCIDENT = (
            "attendance_incident",
            "Incidencia de asistencia",
        )
        LEAVE_REQUEST = (
            "leave_request",
            "Permiso o licencia",
        )
        ATTENDANCE_CORRECTION = (
            "attendance_correction",
            "Corrección de asistencia",
        )
        OVERTIME_REQUEST = (
            "overtime_request",
            "Solicitud de horas extras",
        )
        OPERATIONAL_SESSION = (
            "operational_session",
            "Sesión operativa",
        )
        OPERATIONAL_EVENT = (
            "operational_event",
            "Evento operativo",
        )
        MONTHLY_SUMMARY = (
            "monthly_summary",
            "Resumen mensual",
        )
        EMPLOYEE = (
            "employee",
            "Trabajador",
        )
        WORK_SCHEDULE = (
            "work_schedule",
            "Horario",
        )
        DEVICE_USAGE = (
            "device_usage",
            "Uso de dispositivo",
        )
        AUDIT_LOG = (
            "audit_log",
            "Registro de auditoría",
        )
        REPORT_DATA = (
            "report_data",
            "Dato de reporte",
        )
        GENERIC_OBJECT = (
            "generic_object",
            "Objeto genérico",
        )
        SUMMARY_ROW = (
            "summary_row",
            "Fila de resumen",
        )
        OTHER = (
            "other",
            "Otro registro",
        )

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        PROCESSING = (
            "processing",
            "Procesando",
        )
        EXPORTED = (
            "exported",
            "Exportado",
        )
        EXPORTED_WITH_WARNINGS = (
            "exported_with_warnings",
            "Exportado con observaciones",
        )
        SKIPPED = (
            "skipped",
            "Omitido",
        )
        FAILED = (
            "failed",
            "Fallido",
        )
        CANCELLED = (
            "cancelled",
            "Cancelado",
        )

    class ResultType(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        EXPORTED = (
            "exported",
            "Exportado",
        )
        TRANSFORMED = (
            "transformed",
            "Transformado y exportado",
        )
        MASKED = (
            "masked",
            "Exportado con datos ocultos",
        )
        PARTIAL = (
            "partial",
            "Exportado parcialmente",
        )
        SKIPPED = (
            "skipped",
            "Omitido",
        )
        FAILED = (
            "failed",
            "Fallido",
        )
        CANCELLED = (
            "cancelled",
            "Cancelado",
        )

    class ErrorCategory(models.TextChoices):
        NONE = (
            "none",
            "Sin error",
        )
        SOURCE_NOT_FOUND = (
            "source_not_found",
            "Registro de origen no encontrado",
        )
        PERMISSION_DENIED = (
            "permission_denied",
            "Permiso denegado",
        )
        INVALID_DATA = (
            "invalid_data",
            "Información inválida",
        )
        SERIALIZATION = (
            "serialization",
            "Error de serialización",
        )
        TRANSFORMATION = (
            "transformation",
            "Error de transformación",
        )
        SENSITIVE_DATA = (
            "sensitive_data",
            "Error de datos sensibles",
        )
        COLUMN_MAPPING = (
            "column_mapping",
            "Error de columnas",
        )
        FILE_WRITE = (
            "file_write",
            "Error de escritura",
        )
        EXTERNAL_SYSTEM = (
            "external_system",
            "Error de sistema externo",
        )
        TIMEOUT = (
            "timeout",
            "Tiempo agotado",
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

    export_batch = models.ForeignKey(
        AttendanceExportBatch,
        on_delete=models.PROTECT,
        related_name="items",
        verbose_name="Lote de exportación",
    )

    sequence_number = models.PositiveBigIntegerField(
        default=1,
        verbose_name="Número de secuencia",
    )

    output_row_number = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Número de fila de salida",
    )

    output_sheet_name = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Hoja de salida",
    )

    item_type = models.CharField(
        max_length=40,
        choices=ItemType.choices,
        default=ItemType.GENERIC_OBJECT,
        db_index=True,
        verbose_name="Tipo de elemento",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    result_type = models.CharField(
        max_length=30,
        choices=ResultType.choices,
        default=ResultType.PENDING,
        db_index=True,
        verbose_name="Resultado",
    )

    employee_profile = models.ForeignKey(
        "attendance.EmployeeProfile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="export_items",
        verbose_name="Trabajador",
    )

    record_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha del registro",
    )

    content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_export_items",
        verbose_name="Tipo de objeto de origen",
    )

    object_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="ID del objeto de origen",
    )

    content_object = GenericForeignKey(
        "content_type",
        "object_id",
    )

    object_model = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Modelo de origen",
    )

    object_representation = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Representación del objeto",
    )

    external_reference = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Referencia externa",
    )

    source_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos originales",
    )

    serialized_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos serializados",
    )

    transformed_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos transformados",
    )

    exported_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos exportados",
    )

    selected_fields = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Campos seleccionados",
    )

    omitted_fields = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Campos omitidos",
    )

    transformed_fields = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Campos transformados",
    )

    masked_fields = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Campos ocultados",
    )

    empty_fields = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Campos vacíos",
    )

    has_sensitive_data = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Contiene datos sensibles",
    )

    sensitive_data_masked = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Datos sensibles ocultados",
    )

    sensitive_fields_detected = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Campos sensibles detectados",
    )

    source_checksum = models.CharField(
        max_length=128,
        blank=True,
        db_index=True,
        verbose_name="Checksum de origen",
    )

    exported_checksum = models.CharField(
        max_length=128,
        blank=True,
        db_index=True,
        verbose_name="Checksum exportado",
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

    processing_duration_milliseconds = (
        models.PositiveBigIntegerField(
            default=0,
            verbose_name="Duración del procesamiento",
        )
    )

    warnings = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Advertencias",
    )

    warning_code = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Código de advertencia",
    )

    warning_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de advertencia",
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

    errors = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Errores",
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
        related_name="attendance_export_items_reviewed",
        verbose_name="Revisado por",
    )

    review_observation = models.TextField(
        blank=True,
        verbose_name="Observación de revisión",
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

    parent_item = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="child_items",
        verbose_name="Elemento principal",
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
        related_name="attendance_export_items_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_export_items_updated",
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
        related_name="attendance_export_items_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Elemento de exportación de asistencia"
        verbose_name_plural = (
            "Elementos de exportación de asistencia"
        )

        ordering = (
            "export_batch",
            "sequence_number",
        )

        constraints = (
            models.UniqueConstraint(
                fields=(
                    "export_batch",
                    "sequence_number",
                ),
                name="att_eitem_batch_seq_unique",
            ),
            models.UniqueConstraint(
                fields=(
                    "export_batch",
                    "output_sheet_name",
                    "output_row_number",
                ),
                condition=models.Q(
                    output_row_number__isnull=False,
                ),
                name="att_eitem_output_row_unique",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    retry_count__lte=models.F(
                        "maximum_retries"
                    ),
                ),
                name="att_eitem_retry_lte_max",
            ),
        )

        indexes = (
            models.Index(
                fields=(
                    "export_batch",
                    "status",
                    "sequence_number",
                ),
                name="att_eitem_batch_status_idx",
            ),
            models.Index(
                fields=(
                    "export_batch",
                    "result_type",
                    "status",
                ),
                name="att_eitem_batch_result_idx",
            ),
            models.Index(
                fields=(
                    "output_sheet_name",
                    "output_row_number",
                ),
                name="att_eitem_output_row_idx",
            ),
            models.Index(
                fields=(
                    "employee_profile",
                    "record_date",
                    "status",
                ),
                name="att_eitem_emp_date_idx",
            ),
            models.Index(
                fields=(
                    "content_type",
                    "object_id",
                    "status",
                ),
                name="att_eitem_object_idx",
            ),
            models.Index(
                fields=(
                    "item_type",
                    "result_type",
                    "status",
                ),
                name="att_eitem_type_result_idx",
            ),
            models.Index(
                fields=(
                    "processing_started_at",
                    "processing_finished_at",
                ),
                name="att_eitem_processing_idx",
            ),
            models.Index(
                fields=(
                    "has_sensitive_data",
                    "sensitive_data_masked",
                ),
                name="att_eitem_sensitive_idx",
            ),
            models.Index(
                fields=(
                    "error_category",
                    "error_code",
                    "status",
                ),
                name="att_eitem_error_idx",
            ),
            models.Index(
                fields=(
                    "warning_code",
                    "requires_review",
                ),
                name="att_eitem_warning_idx",
            ),
            models.Index(
                fields=(
                    "next_retry_at",
                    "retry_count",
                    "status",
                ),
                name="att_eitem_retry_idx",
            ),
            models.Index(
                fields=(
                    "retry_of",
                    "retry_count",
                ),
                name="att_eitem_retry_of_idx",
            ),
            models.Index(
                fields=(
                    "parent_item",
                    "status",
                ),
                name="att_eitem_parent_idx",
            ),
            models.Index(
                fields=(
                    "external_reference",
                    "source_checksum",
                ),
                name="att_eitem_external_idx",
            ),
        )

    def __str__(self):
        reference = (
            self.object_representation
            or self.external_reference
            or self.object_id
            or self.get_item_type_display()
        )

        return (
            f"{self.export_batch.batch_number} - "
            f"{self.sequence_number} - "
            f"{reference}"
        )

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_finished(self):
        return self.status in (
            self.Status.EXPORTED,
            self.Status.EXPORTED_WITH_WARNINGS,
            self.Status.SKIPPED,
            self.Status.FAILED,
            self.Status.CANCELLED,
        )

    @property
    def is_successful(self):
        return self.status in (
            self.Status.EXPORTED,
            self.Status.EXPORTED_WITH_WARNINGS,
        )

    @property
    def has_warnings(self):
        return bool(
            self.warning_code
            or self.warning_message
            or self.warnings
        )

    @property
    def has_errors(self):
        return bool(
            self.error_code
            or self.error_message
            or self.errors
        )

    @property
    def can_retry(self):
        return (
            self.status == self.Status.FAILED
            and self.retry_count < self.maximum_retries
            and self.archived_at is None
        )

    @property
    def object_reference(self):
        if self.object_model and self.object_id:
            return (
                f"{self.object_model}:"
                f"{self.object_id}"
            )

        return self.external_reference

    def calculate_processing_duration(self):
        if (
            not self.processing_started_at
            or not self.processing_finished_at
            or self.processing_finished_at
            <= self.processing_started_at
        ):
            self.processing_duration_milliseconds = 0
            return 0

        self.processing_duration_milliseconds = int(
            (
                self.processing_finished_at
                - self.processing_started_at
            ).total_seconds()
            * 1000
        )

        return self.processing_duration_milliseconds

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.export_batch_id
            and self.export_batch.archived_at
        ):
            errors["export_batch"] = (
                "El lote de exportación está archivado."
            )

        if (
            self.employee_profile_id
            and self.employee_profile.archived_at
        ):
            errors["employee_profile"] = (
                "El perfil laboral está archivado."
            )

        if bool(self.content_type_id) != bool(self.object_id):
            errors["object_id"] = (
                "Debes registrar tanto el tipo como el ID "
                "del objeto de origen."
            )

        object_item_types = (
            self.ItemType.ATTENDANCE_RECORD,
            self.ItemType.DAILY_ATTENDANCE,
            self.ItemType.ATTENDANCE_INCIDENT,
            self.ItemType.LEAVE_REQUEST,
            self.ItemType.ATTENDANCE_CORRECTION,
            self.ItemType.OVERTIME_REQUEST,
            self.ItemType.OPERATIONAL_SESSION,
            self.ItemType.OPERATIONAL_EVENT,
            self.ItemType.MONTHLY_SUMMARY,
            self.ItemType.EMPLOYEE,
            self.ItemType.WORK_SCHEDULE,
            self.ItemType.DEVICE_USAGE,
            self.ItemType.AUDIT_LOG,
            self.ItemType.GENERIC_OBJECT,
        )

        if (
            self.item_type in object_item_types
            and not self.content_type_id
        ):
            errors["content_type"] = (
                "Este tipo de elemento requiere "
                "un objeto de origen."
            )

        json_object_fields = (
            "source_data",
            "serialized_data",
            "transformed_data",
            "exported_data",
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
            "selected_fields",
            "omitted_fields",
            "transformed_fields",
            "masked_fields",
            "empty_fields",
            "sensitive_fields_detected",
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

        if (
            self.processing_started_at
            and self.processing_finished_at
            and self.processing_finished_at
            < self.processing_started_at
        ):
            errors["processing_finished_at"] = (
                "La fecha de finalización no puede ser "
                "anterior al inicio."
            )

        if (
            self.status == self.Status.PROCESSING
            and not self.processing_started_at
        ):
            errors["processing_started_at"] = (
                "Un elemento en procesamiento debe registrar "
                "la fecha de inicio."
            )

        if self.is_finished and not self.processing_finished_at:
            errors["processing_finished_at"] = (
                "Un elemento finalizado debe registrar "
                "la fecha de finalización."
            )

        if (
            self.status == self.Status.EXPORTED
            and self.result_type
            not in (
                self.ResultType.EXPORTED,
                self.ResultType.TRANSFORMED,
                self.ResultType.MASKED,
            )
        ):
            errors["result_type"] = (
                "El resultado no corresponde a un elemento "
                "exportado correctamente."
            )

        if (
            self.status
            == self.Status.EXPORTED_WITH_WARNINGS
            and not self.has_warnings
        ):
            errors["warning_message"] = (
                "Debes registrar al menos una advertencia."
            )

        if (
            self.status
            == self.Status.EXPORTED_WITH_WARNINGS
            and self.result_type
            not in (
                self.ResultType.PARTIAL,
                self.ResultType.TRANSFORMED,
                self.ResultType.MASKED,
            )
        ):
            errors["result_type"] = (
                "El resultado no corresponde a una exportación "
                "con observaciones."
            )

        if (
            self.status == self.Status.SKIPPED
            and self.result_type != self.ResultType.SKIPPED
        ):
            errors["result_type"] = (
                "Un elemento omitido debe tener "
                "resultado omitido."
            )

        if (
            self.status == self.Status.FAILED
            and self.result_type != self.ResultType.FAILED
        ):
            errors["result_type"] = (
                "Un elemento fallido debe tener "
                "resultado fallido."
            )

        if (
            self.status == self.Status.FAILED
            and not self.error_message.strip()
        ):
            errors["error_message"] = (
                "Un elemento fallido debe registrar el error."
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
            self.status == self.Status.CANCELLED
            and self.result_type
            != self.ResultType.CANCELLED
        ):
            errors["result_type"] = (
                "Un elemento cancelado debe tener "
                "resultado cancelado."
            )

        if (
            self.has_sensitive_data
            and not self.sensitive_fields_detected
        ):
            errors["sensitive_fields_detected"] = (
                "Debes registrar los campos sensibles "
                "detectados."
            )

        if (
            self.sensitive_data_masked
            and not self.masked_fields
        ):
            errors["masked_fields"] = (
                "Debes registrar los campos ocultados."
            )

        if (
            self.sensitive_data_masked
            and not self.has_sensitive_data
        ):
            errors["has_sensitive_data"] = (
                "No puedes ocultar datos sensibles si "
                "no fueron detectados."
            )

        if (
            self.export_batch_id
            and self.export_batch.sensitive_data_mode
            == AttendanceExportBatch.SensitiveDataMode.EXCLUDE
            and self.has_sensitive_data
            and self.status in (
                self.Status.EXPORTED,
                self.Status.EXPORTED_WITH_WARNINGS,
            )
            and not self.omitted_fields
        ):
            errors["omitted_fields"] = (
                "Los datos sensibles deben excluirse "
                "de esta exportación."
            )

        if (
            self.export_batch_id
            and self.export_batch.sensitive_data_mode
            == AttendanceExportBatch.SensitiveDataMode.MASK
            and self.has_sensitive_data
            and self.status in (
                self.Status.EXPORTED,
                self.Status.EXPORTED_WITH_WARNINGS,
            )
            and not self.sensitive_data_masked
        ):
            errors["sensitive_data_masked"] = (
                "Los datos sensibles deben ocultarse "
                "antes de exportarlos."
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
                "Debes indicar quién revisó el elemento."
            )

        if (
            self.reviewed_by_id
            and not self.reviewed_at
        ):
            errors["reviewed_at"] = (
                "Debes indicar cuándo fue revisado."
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
                "Un elemento no puede ser reintento "
                "de sí mismo."
            )

        if (
            self.retry_of_id
            and self.retry_of.export_batch_id
            != self.export_batch_id
        ):
            errors["retry_of"] = (
                "El elemento original debe pertenecer "
                "al mismo lote."
            )

        if (
            self.parent_item_id
            and self.parent_item_id == self.id
        ):
            errors["parent_item"] = (
                "Un elemento no puede depender de sí mismo."
            )

        if (
            self.parent_item_id
            and self.parent_item.export_batch_id
            != self.export_batch_id
        ):
            errors["parent_item"] = (
                "El elemento principal debe pertenecer "
                "al mismo lote."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.output_sheet_name = str(
            self.output_sheet_name or ""
        ).strip()

        self.external_reference = str(
            self.external_reference or ""
        ).strip()

        self.source_checksum = str(
            self.source_checksum or ""
        ).strip()

        self.exported_checksum = str(
            self.exported_checksum or ""
        ).strip()

        self.warning_code = str(
            self.warning_code or ""
        ).strip()

        self.warning_message = str(
            self.warning_message or ""
        ).strip()

        self.error_code = str(
            self.error_code or ""
        ).strip()

        self.error_message = str(
            self.error_message or ""
        ).strip()

        self.exception_type = str(
            self.exception_type or ""
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

        if (
            self.processing_started_at
            and self.processing_finished_at
        ):
            self.calculate_processing_duration()

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def start_processing(
        self,
        user=None,
    ):
        if self.status != self.Status.PENDING:
            raise ValidationError(
                "Solo puedes iniciar un elemento pendiente."
            )

        if self.export_batch.status not in (
            AttendanceExportBatch.Status.PROCESSING,
            AttendanceExportBatch.Status.CANCEL_REQUESTED,
        ):
            raise ValidationError(
                "El lote de exportación no está activo."
            )

        self.status = self.Status.PROCESSING
        self.result_type = self.ResultType.PENDING
        self.processing_started_at = timezone.now()
        self.processing_finished_at = None
        self.processing_duration_milliseconds = 0
        self.warnings = []
        self.warning_code = ""
        self.warning_message = ""
        self.error_category = self.ErrorCategory.NONE
        self.error_code = ""
        self.error_message = ""
        self.exception_type = ""
        self.stack_trace = ""
        self.errors = []
        self.requires_review = False
        self.review_reason = ""
        self.updated_by = user

        self.save()

    def mark_exported(
        self,
        *,
        exported_data,
        output_row_number=None,
        output_sheet_name="",
        serialized_data=None,
        transformed_data=None,
        selected_fields=None,
        omitted_fields=None,
        transformed_fields=None,
        masked_fields=None,
        empty_fields=None,
        sensitive_fields_detected=None,
        source_checksum="",
        exported_checksum="",
        user=None,
    ):
        if self.status != self.Status.PROCESSING:
            raise ValidationError(
                "El elemento no está procesándose."
            )

        exported_data = exported_data or {}

        if not isinstance(
            exported_data,
            dict,
        ):
            raise ValidationError(
                "Los datos exportados deben ser "
                "un objeto JSON."
            )

        selected_fields = selected_fields or []
        omitted_fields = omitted_fields or []
        transformed_fields = transformed_fields or []
        masked_fields = masked_fields or []
        empty_fields = empty_fields or []
        sensitive_fields_detected = (
            sensitive_fields_detected or []
        )

        self.exported_data = exported_data
        self.serialized_data = serialized_data or {}
        self.transformed_data = transformed_data or {}
        self.selected_fields = selected_fields
        self.omitted_fields = omitted_fields
        self.transformed_fields = transformed_fields
        self.masked_fields = masked_fields
        self.empty_fields = empty_fields
        self.sensitive_fields_detected = (
            sensitive_fields_detected
        )
        self.has_sensitive_data = bool(
            sensitive_fields_detected
        )
        self.sensitive_data_masked = bool(
            masked_fields
        )
        self.output_row_number = output_row_number
        self.output_sheet_name = str(
            output_sheet_name or ""
        ).strip()
        self.source_checksum = str(
            source_checksum or ""
        ).strip()
        self.exported_checksum = str(
            exported_checksum or ""
        ).strip()
        self.processing_finished_at = timezone.now()
        self.status = self.Status.EXPORTED

        if masked_fields:
            self.result_type = self.ResultType.MASKED
        elif transformed_fields:
            self.result_type = (
                self.ResultType.TRANSFORMED
            )
        else:
            self.result_type = self.ResultType.EXPORTED

        self.updated_by = user

        self.calculate_processing_duration()
        self.save()

    def mark_exported_with_warnings(
        self,
        *,
        exported_data,
        warning_message,
        warnings=None,
        warning_code="",
        output_row_number=None,
        output_sheet_name="",
        serialized_data=None,
        transformed_data=None,
        selected_fields=None,
        omitted_fields=None,
        transformed_fields=None,
        masked_fields=None,
        empty_fields=None,
        sensitive_fields_detected=None,
        requires_review=False,
        review_reason="",
        user=None,
    ):
        warning_message = str(
            warning_message or ""
        ).strip()

        if not warning_message:
            raise ValidationError(
                "Debes indicar la advertencia."
            )

        if self.status != self.Status.PROCESSING:
            raise ValidationError(
                "El elemento no está procesándose."
            )

        self.status = (
            self.Status.EXPORTED_WITH_WARNINGS
        )
        self.result_type = self.ResultType.PARTIAL
        self.exported_data = exported_data or {}
        self.serialized_data = serialized_data or {}
        self.transformed_data = transformed_data or {}
        self.selected_fields = selected_fields or []
        self.omitted_fields = omitted_fields or []
        self.transformed_fields = (
            transformed_fields or []
        )
        self.masked_fields = masked_fields or []
        self.empty_fields = empty_fields or []
        self.sensitive_fields_detected = (
            sensitive_fields_detected or []
        )
        self.has_sensitive_data = bool(
            self.sensitive_fields_detected
        )
        self.sensitive_data_masked = bool(
            self.masked_fields
        )
        self.warning_code = str(
            warning_code or ""
        ).strip()
        self.warning_message = warning_message
        self.warnings = warnings or []
        self.output_row_number = output_row_number
        self.output_sheet_name = str(
            output_sheet_name or ""
        ).strip()
        self.processing_finished_at = timezone.now()
        self.requires_review = requires_review
        self.review_reason = str(
            review_reason
            or warning_message
        ).strip()
        self.updated_by = user

        self.calculate_processing_duration()
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

        if self.status not in (
            self.Status.PENDING,
            self.Status.PROCESSING,
        ):
            raise ValidationError(
                "El elemento no puede omitirse "
                "desde su estado actual."
            )

        now = timezone.now()

        if not self.processing_started_at:
            self.processing_started_at = now

        self.status = self.Status.SKIPPED
        self.result_type = self.ResultType.SKIPPED
        self.processing_finished_at = now
        self.warning_code = "EXPORT_SKIPPED"
        self.warning_message = reason
        self.warnings = [
            *list(self.warnings or []),
            {
                "code": "EXPORT_SKIPPED",
                "message": reason,
                "recorded_at": now.isoformat(),
            },
        ]
        self.updated_by = user

        self.calculate_processing_duration()
        self.save()

    def mark_failed(
        self,
        *,
        error,
        error_category=ErrorCategory.SYSTEM,
        error_code="",
        exception_type="",
        stack_trace="",
        errors=None,
        next_retry_at=None,
        requires_review=True,
        user=None,
    ):
        error = str(
            error or ""
        ).strip()

        if not error:
            raise ValidationError(
                "Debes indicar el error de exportación."
            )

        if self.status not in (
            self.Status.PENDING,
            self.Status.PROCESSING,
        ):
            raise ValidationError(
                "El elemento no puede marcarse como fallido."
            )

        now = timezone.now()

        if not self.processing_started_at:
            self.processing_started_at = now

        self.status = self.Status.FAILED
        self.result_type = self.ResultType.FAILED
        self.processing_finished_at = now
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
        self.errors = errors or []
        self.requires_review = requires_review
        self.review_reason = (
            error
            if requires_review
            else ""
        )

        if (
            self.retry_count < self.maximum_retries
            and next_retry_at
        ):
            self.next_retry_at = next_retry_at
        else:
            self.next_retry_at = None

        self.updated_by = user

        self.calculate_processing_duration()
        self.save()

    def cancel(
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
                "Debes indicar el motivo de cancelación."
            )

        if self.is_finished:
            raise ValidationError(
                "El elemento ya está finalizado."
            )

        now = timezone.now()

        if not self.processing_started_at:
            self.processing_started_at = now

        self.status = self.Status.CANCELLED
        self.result_type = self.ResultType.CANCELLED
        self.processing_finished_at = now
        self.warning_code = "EXPORT_CANCELLED"
        self.warning_message = reason
        self.updated_by = user

        self.calculate_processing_duration()
        self.save()

    def mark_reviewed(
        self,
        *,
        user,
        observation="",
    ):
        if not self.requires_review:
            raise ValidationError(
                "El elemento no requiere revisión."
            )

        self.requires_review = False
        self.reviewed_at = timezone.now()
        self.reviewed_by = user
        self.review_observation = str(
            observation or ""
        ).strip()
        self.updated_by = user

        self.save(
            update_fields=[
                "requires_review",
                "reviewed_at",
                "reviewed_by",
                "review_observation",
                "updated_by",
                "updated_at",
            ]
        )

    def prepare_retry(
        self,
        *,
        sequence_number,
        next_retry_at=None,
        user=None,
    ):
        if not self.can_retry:
            raise ValidationError(
                "El elemento no admite otro reintento."
            )

        if (
            next_retry_at
            and next_retry_at <= timezone.now()
        ):
            raise ValidationError(
                "El próximo reintento debe ser futuro."
            )

        retry_item = AttendanceExportItem(
            export_batch=self.export_batch,
            sequence_number=sequence_number,
            item_type=self.item_type,
            status=self.Status.PENDING,
            result_type=self.ResultType.PENDING,
            employee_profile=self.employee_profile,
            record_date=self.record_date,
            content_type=self.content_type,
            object_id=self.object_id,
            object_model=self.object_model,
            object_representation=(
                self.object_representation
            ),
            external_reference=self.external_reference,
            source_data=dict(
                self.source_data or {}
            ),
            serialized_data=dict(
                self.serialized_data or {}
            ),
            selected_fields=list(
                self.selected_fields or []
            ),
            has_sensitive_data=self.has_sensitive_data,
            sensitive_fields_detected=list(
                self.sensitive_fields_detected or []
            ),
            source_checksum=self.source_checksum,
            retry_count=self.retry_count + 1,
            maximum_retries=self.maximum_retries,
            next_retry_at=next_retry_at,
            retry_of=self,
            parent_item=self.parent_item,
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
                "Solo puedes archivar un elemento finalizado."
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

    @classmethod
    def create_for_object(
        cls,
        *,
        export_batch,
        sequence_number,
        content_object,
        item_type=ItemType.GENERIC_OBJECT,
        employee_profile=None,
        record_date=None,
        external_reference="",
        source_data=None,
        selected_fields=None,
        maximum_retries=0,
        parent_item=None,
        created_by=None,
    ):
        """
        Crea un elemento de exportación vinculado
        con cualquier modelo mediante ContentType.
        """

        if content_object is None:
            raise ValidationError(
                "Debes indicar el objeto de origen."
            )

        content_type = (
            ContentType.objects.get_for_model(
                content_object,
                for_concrete_model=False,
            )
        )

        item = cls(
            export_batch=export_batch,
            sequence_number=sequence_number,
            item_type=item_type,
            employee_profile=employee_profile,
            record_date=record_date,
            content_type=content_type,
            object_id=str(
                content_object.pk
            ),
            object_representation=str(
                content_object
            )[:500],
            external_reference=str(
                external_reference or ""
            ).strip(),
            source_data=source_data or {},
            selected_fields=selected_fields or [],
            maximum_retries=maximum_retries,
            parent_item=parent_item,
            created_by=created_by,
            updated_by=created_by,
        )

        item.save()

        return item