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

from .attendance_processing_run import (
    AttendanceProcessingRun,
)


class AttendanceProcessingItem(models.Model):
    """
    Resultado individual procesado dentro de una ejecución.

    Una ejecución puede contener uno o varios elementos:

    - Un trabajador.
    - Un trabajador y una fecha.
    - Una asistencia diaria.
    - Una marcación.
    - Una incidencia.
    - Una solicitud de permiso.
    - Una corrección.
    - Una solicitud de horas extras.
    - Una sesión operativa.
    - Un resumen mensual.
    - Un reporte.
    - Una notificación.
    - Cualquier otro objeto relacionado.

    Este modelo permite conocer exactamente qué ocurrió con
    cada elemento sin depender únicamente del resultado global
    de AttendanceProcessingRun.
    """

    class ItemType(models.TextChoices):
        EMPLOYEE = (
            "employee",
            "Trabajador",
        )
        EMPLOYEE_DATE = (
            "employee_date",
            "Trabajador y fecha",
        )
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
            "Solicitud de permiso",
        )
        ATTENDANCE_CORRECTION = (
            "attendance_correction",
            "Corrección de asistencia",
        )
        OVERTIME_REQUEST = (
            "overtime_request",
            "Solicitud de horas extras",
        )
        OPERATIONAL_WORK_SESSION = (
            "operational_work_session",
            "Sesión de trabajo operativo",
        )
        OPERATIONAL_WORK_EVENT = (
            "operational_work_event",
            "Evento de trabajo operativo",
        )
        MONTHLY_SUMMARY = (
            "monthly_summary",
            "Resumen mensual",
        )
        REPORT = (
            "report",
            "Reporte",
        )
        REPORT_DELIVERY = (
            "report_delivery",
            "Entrega de reporte",
        )
        NOTIFICATION = (
            "notification",
            "Notificación",
        )
        POLICY_ASSIGNMENT = (
            "policy_assignment",
            "Asignación de política",
        )
        SCHEDULE_ASSIGNMENT = (
            "schedule_assignment",
            "Asignación de horario",
        )
        DEVICE_PERMISSION = (
            "device_permission",
            "Permiso de dispositivo",
        )
        GENERIC_OBJECT = (
            "generic_object",
            "Objeto genérico",
        )
        OTHER = (
            "other",
            "Otro elemento",
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
        SUCCESS = (
            "success",
            "Correcto",
        )
        SUCCESS_WITH_WARNINGS = (
            "success_with_warnings",
            "Correcto con advertencias",
        )
        FAILED = (
            "failed",
            "Fallido",
        )
        SKIPPED = (
            "skipped",
            "Omitido",
        )
        CANCELLED = (
            "cancelled",
            "Cancelado",
        )
        ROLLED_BACK = (
            "rolled_back",
            "Revertido",
        )

    class ActionType(models.TextChoices):
        CREATE = (
            "create",
            "Crear",
        )
        UPDATE = (
            "update",
            "Actualizar",
        )
        DELETE = (
            "delete",
            "Eliminar",
        )
        ARCHIVE = (
            "archive",
            "Archivar",
        )
        RESTORE = (
            "restore",
            "Restaurar",
        )
        VALIDATE = (
            "validate",
            "Validar",
        )
        CALCULATE = (
            "calculate",
            "Calcular",
        )
        RECALCULATE = (
            "recalculate",
            "Recalcular",
        )
        CONSOLIDATE = (
            "consolidate",
            "Consolidar",
        )
        CLOSE = (
            "close",
            "Cerrar",
        )
        REOPEN = (
            "reopen",
            "Reabrir",
        )
        EXPIRE = (
            "expire",
            "Vencer",
        )
        NOTIFY = (
            "notify",
            "Notificar",
        )
        GENERATE = (
            "generate",
            "Generar",
        )
        DELIVER = (
            "deliver",
            "Entregar",
        )
        SYNCHRONIZE = (
            "synchronize",
            "Sincronizar",
        )
        IMPORT = (
            "import",
            "Importar",
        )
        EXPORT = (
            "export",
            "Exportar",
        )
        VERIFY = (
            "verify",
            "Verificar",
        )
        NO_CHANGE = (
            "no_change",
            "Sin cambios",
        )
        OTHER = (
            "other",
            "Otra acción",
        )

    class ResultType(models.TextChoices):
        CREATED = (
            "created",
            "Creado",
        )
        UPDATED = (
            "updated",
            "Actualizado",
        )
        DELETED = (
            "deleted",
            "Eliminado",
        )
        ARCHIVED = (
            "archived",
            "Archivado",
        )
        RESTORED = (
            "restored",
            "Restaurado",
        )
        VALIDATED = (
            "validated",
            "Validado",
        )
        CALCULATED = (
            "calculated",
            "Calculado",
        )
        CLOSED = (
            "closed",
            "Cerrado",
        )
        EXPIRED = (
            "expired",
            "Vencido",
        )
        SENT = (
            "sent",
            "Enviado",
        )
        GENERATED = (
            "generated",
            "Generado",
        )
        DELIVERED = (
            "delivered",
            "Entregado",
        )
        SYNCHRONIZED = (
            "synchronized",
            "Sincronizado",
        )
        UNCHANGED = (
            "unchanged",
            "Sin cambios",
        )
        WARNING = (
            "warning",
            "Procesado con advertencia",
        )
        ERROR = (
            "error",
            "Error",
        )
        SKIPPED = (
            "skipped",
            "Omitido",
        )
        CANCELLED = (
            "cancelled",
            "Cancelado",
        )
        ROLLED_BACK = (
            "rolled_back",
            "Revertido",
        )
        OTHER = (
            "other",
            "Otro resultado",
        )

    class ErrorCategory(models.TextChoices):
        NONE = (
            "none",
            "Sin error",
        )
        VALIDATION = (
            "validation",
            "Error de validación",
        )
        CONFIGURATION = (
            "configuration",
            "Error de configuración",
        )
        MISSING_DATA = (
            "missing_data",
            "Información faltante",
        )
        DUPLICATE = (
            "duplicate",
            "Registro duplicado",
        )
        PERMISSION = (
            "permission",
            "Permiso denegado",
        )
        INTEGRITY = (
            "integrity",
            "Error de integridad",
        )
        BUSINESS_RULE = (
            "business_rule",
            "Regla de negocio",
        )
        EXTERNAL_SERVICE = (
            "external_service",
            "Servicio externo",
        )
        CONNECTION = (
            "connection",
            "Error de conexión",
        )
        TIMEOUT = (
            "timeout",
            "Tiempo agotado",
        )
        NOT_FOUND = (
            "not_found",
            "Registro no encontrado",
        )
        SYSTEM = (
            "system",
            "Error del sistema",
        )
        UNKNOWN = (
            "unknown",
            "Error desconocido",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    processing_run = models.ForeignKey(
        AttendanceProcessingRun,
        on_delete=models.PROTECT,
        related_name="items",
        verbose_name="Ejecución de procesamiento",
    )

    sequence_number = models.PositiveBigIntegerField(
        default=1,
        verbose_name="Número de secuencia",
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

    action_type = models.CharField(
        max_length=30,
        choices=ActionType.choices,
        default=ActionType.OTHER,
        db_index=True,
        verbose_name="Acción",
    )

    result_type = models.CharField(
        max_length=30,
        choices=ResultType.choices,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Resultado",
    )

    employee_profile = models.ForeignKey(
        "attendance.EmployeeProfile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="processing_items",
        verbose_name="Trabajador",
    )

    process_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha procesada",
    )

    content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_processing_items",
        verbose_name="Tipo de objeto",
    )

    object_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="ID del objeto",
    )

    content_object = GenericForeignKey(
        "content_type",
        "object_id",
    )

    object_model = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Modelo del objeto",
    )

    object_representation = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Representación del objeto",
    )

    external_reference = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Referencia externa",
    )

    idempotency_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        verbose_name="Clave de idempotencia",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Iniciado el",
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Finalizado el",
    )

    duration_milliseconds = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Duración en milisegundos",
    )

    input_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos de entrada",
    )

    previous_values = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Valores anteriores",
    )

    new_values = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Valores posteriores",
    )

    changed_fields = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Campos modificados",
    )

    output_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos resultantes",
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

    warnings = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Advertencias",
    )

    error_category = models.CharField(
        max_length=30,
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

    was_created = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Registro creado",
    )

    was_updated = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Registro actualizado",
    )

    was_deleted = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Registro eliminado",
    )

    was_archived = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Registro archivado",
    )

    was_unchanged = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Sin cambios",
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
        related_name="attendance_processing_items_reviewed",
        verbose_name="Revisado por",
    )

    review_observation = models.TextField(
        blank=True,
        verbose_name="Observación de revisión",
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
        related_name="attendance_processing_items_rolled_back",
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
        related_name="attendance_processing_items_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_processing_items_updated",
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
        related_name="attendance_processing_items_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Elemento de procesamiento de asistencia"
        verbose_name_plural = (
            "Elementos de procesamiento de asistencia"
        )

        ordering = (
            "processing_run",
            "sequence_number",
            "created_at",
        )

        constraints = (
            models.UniqueConstraint(
                fields=(
                    "processing_run",
                    "sequence_number",
                ),
                name="att_pitem_run_sequence_unique",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    retry_count__lte=models.F(
                        "maximum_retries"
                    ),
                ),
                name="att_pitem_retry_lte_max",
            ),
        )

        indexes = (
            models.Index(
                fields=(
                    "processing_run",
                    "status",
                    "sequence_number",
                ),
                name="att_pitem_run_status_idx",
            ),
            models.Index(
                fields=(
                    "processing_run",
                    "item_type",
                    "status",
                ),
                name="att_pitem_run_type_idx",
            ),
            models.Index(
                fields=(
                    "employee_profile",
                    "process_date",
                    "status",
                ),
                name="att_pitem_emp_date_idx",
            ),
            models.Index(
                fields=(
                    "content_type",
                    "object_id",
                    "status",
                ),
                name="att_pitem_object_idx",
            ),
            models.Index(
                fields=(
                    "action_type",
                    "result_type",
                    "status",
                ),
                name="att_pitem_action_result_idx",
            ),
            models.Index(
                fields=(
                    "started_at",
                    "finished_at",
                ),
                name="att_pitem_lifecycle_idx",
            ),
            models.Index(
                fields=(
                    "error_category",
                    "error_code",
                    "status",
                ),
                name="att_pitem_error_idx",
            ),
            models.Index(
                fields=(
                    "warning_code",
                    "requires_review",
                ),
                name="att_pitem_warning_review_idx",
            ),
            models.Index(
                fields=(
                    "retry_of",
                    "retry_count",
                ),
                name="att_pitem_retry_idx",
            ),
            models.Index(
                fields=(
                    "parent_item",
                    "status",
                ),
                name="att_pitem_parent_idx",
            ),
            models.Index(
                fields=(
                    "was_created",
                    "was_updated",
                    "was_unchanged",
                ),
                name="att_pitem_changes_idx",
            ),
            models.Index(
                fields=(
                    "rollback_available",
                    "rolled_back_at",
                ),
                name="att_pitem_rollback_idx",
            ),
            models.Index(
                fields=(
                    "external_reference",
                    "status",
                ),
                name="att_pitem_external_idx",
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
            f"{self.processing_run.run_number} - "
            f"{self.sequence_number} - "
            f"{reference}"
        )

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_finished(self):
        return self.status in (
            self.Status.SUCCESS,
            self.Status.SUCCESS_WITH_WARNINGS,
            self.Status.FAILED,
            self.Status.SKIPPED,
            self.Status.CANCELLED,
            self.Status.ROLLED_BACK,
        )

    @property
    def is_successful(self):
        return self.status in (
            self.Status.SUCCESS,
            self.Status.SUCCESS_WITH_WARNINGS,
        )

    @property
    def has_warnings(self):
        return bool(
            self.warning_message
            or self.warning_code
            or self.warnings
        )

    @property
    def has_errors(self):
        return bool(
            self.error_message
            or self.error_code
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
    def can_rollback(self):
        return (
            self.rollback_available
            and self.is_successful
            and not self.rolled_back_at
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

    def calculate_duration(self):
        if (
            not self.started_at
            or not self.finished_at
            or self.finished_at <= self.started_at
        ):
            self.duration_milliseconds = 0
            return 0

        self.duration_milliseconds = int(
            (
                self.finished_at
                - self.started_at
            ).total_seconds()
            * 1000
        )

        return self.duration_milliseconds

    def clean(self):
        super().clean()

        validation_errors = {}

        if (
            self.processing_run_id
            and self.processing_run.archived_at
        ):
            validation_errors["processing_run"] = (
                "La ejecución de procesamiento está archivada."
            )

        if (
            self.employee_profile_id
            and self.employee_profile.archived_at
        ):
            validation_errors["employee_profile"] = (
                "El perfil laboral está archivado."
            )

        if bool(self.content_type_id) != bool(self.object_id):
            validation_errors["object_id"] = (
                "Debes registrar tanto el tipo como el ID "
                "del objeto."
            )

        if (
            self.item_type == self.ItemType.EMPLOYEE
            and not self.employee_profile_id
        ):
            validation_errors["employee_profile"] = (
                "Debes seleccionar el trabajador."
            )

        if (
            self.item_type == self.ItemType.EMPLOYEE_DATE
            and (
                not self.employee_profile_id
                or not self.process_date
            )
        ):
            validation_errors["process_date"] = (
                "Debes indicar el trabajador y la fecha."
            )

        object_item_types = (
            self.ItemType.ATTENDANCE_RECORD,
            self.ItemType.DAILY_ATTENDANCE,
            self.ItemType.ATTENDANCE_INCIDENT,
            self.ItemType.LEAVE_REQUEST,
            self.ItemType.ATTENDANCE_CORRECTION,
            self.ItemType.OVERTIME_REQUEST,
            self.ItemType.OPERATIONAL_WORK_SESSION,
            self.ItemType.OPERATIONAL_WORK_EVENT,
            self.ItemType.MONTHLY_SUMMARY,
            self.ItemType.REPORT,
            self.ItemType.REPORT_DELIVERY,
            self.ItemType.NOTIFICATION,
            self.ItemType.POLICY_ASSIGNMENT,
            self.ItemType.SCHEDULE_ASSIGNMENT,
            self.ItemType.DEVICE_PERMISSION,
            self.ItemType.GENERIC_OBJECT,
        )

        if (
            self.item_type in object_item_types
            and not self.content_type_id
        ):
            validation_errors["content_type"] = (
                "Este tipo de elemento requiere un objeto "
                "relacionado."
            )

        json_object_fields = (
            "input_data",
            "previous_values",
            "new_values",
            "output_data",
            "rollback_result",
            "metadata",
        )

        for field_name in json_object_fields:
            field_value = getattr(
                self,
                field_name,
            )

            if not isinstance(
                field_value,
                dict,
            ):
                validation_errors[field_name] = (
                    "El valor debe ser un objeto JSON."
                )

        json_list_fields = (
            "changed_fields",
            "warnings",
            "errors",
        )

        for field_name in json_list_fields:
            field_value = getattr(
                self,
                field_name,
            )

            if not isinstance(
                field_value,
                list,
            ):
                validation_errors[field_name] = (
                    "El valor debe ser una lista JSON."
                )

        if (
            self.started_at
            and self.finished_at
            and self.finished_at < self.started_at
        ):
            validation_errors["finished_at"] = (
                "La finalización no puede ser anterior "
                "al inicio."
            )

        if (
            self.status == self.Status.PROCESSING
            and not self.started_at
        ):
            validation_errors["started_at"] = (
                "Un elemento en procesamiento debe registrar "
                "la fecha de inicio."
            )

        if self.is_finished and not self.finished_at:
            validation_errors["finished_at"] = (
                "Un elemento finalizado debe registrar "
                "la fecha de finalización."
            )

        if (
            self.status == self.Status.SUCCESS
            and self.result_type in (
                None,
                "",
                self.ResultType.ERROR,
                self.ResultType.SKIPPED,
                self.ResultType.CANCELLED,
                self.ResultType.ROLLED_BACK,
            )
        ):
            validation_errors["result_type"] = (
                "El resultado no corresponde a un procesamiento "
                "correcto."
            )

        if (
            self.status == self.Status.SUCCESS_WITH_WARNINGS
            and not self.has_warnings
        ):
            validation_errors["warning_message"] = (
                "Debes registrar al menos una advertencia."
            )

        if (
            self.status == self.Status.SUCCESS_WITH_WARNINGS
            and self.result_type
            not in (
                self.ResultType.WARNING,
                self.ResultType.CREATED,
                self.ResultType.UPDATED,
                self.ResultType.VALIDATED,
                self.ResultType.CALCULATED,
                self.ResultType.GENERATED,
                self.ResultType.DELIVERED,
                self.ResultType.SYNCHRONIZED,
            )
        ):
            validation_errors["result_type"] = (
                "El resultado no corresponde a un elemento "
                "procesado con advertencias."
            )

        if (
            self.status == self.Status.FAILED
            and not self.error_message.strip()
        ):
            validation_errors["error_message"] = (
                "Un elemento fallido debe registrar el error."
            )

        if (
            self.status == self.Status.FAILED
            and self.error_category
            == self.ErrorCategory.NONE
        ):
            validation_errors["error_category"] = (
                "Debes indicar la categoría del error."
            )

        if (
            self.status == self.Status.FAILED
            and self.result_type != self.ResultType.ERROR
        ):
            validation_errors["result_type"] = (
                "Un elemento fallido debe tener resultado "
                "de error."
            )

        if (
            self.status == self.Status.SKIPPED
            and self.result_type != self.ResultType.SKIPPED
        ):
            validation_errors["result_type"] = (
                "Un elemento omitido debe tener resultado "
                "omitido."
            )

        if (
            self.status == self.Status.CANCELLED
            and self.result_type != self.ResultType.CANCELLED
        ):
            validation_errors["result_type"] = (
                "Un elemento cancelado debe tener resultado "
                "cancelado."
            )

        if (
            self.status == self.Status.ROLLED_BACK
            and self.result_type != self.ResultType.ROLLED_BACK
        ):
            validation_errors["result_type"] = (
                "Un elemento revertido debe tener resultado "
                "revertido."
            )

        change_flags = (
            self.was_created,
            self.was_updated,
            self.was_deleted,
            self.was_archived,
            self.was_unchanged,
        )

        if sum(
            bool(flag)
            for flag in change_flags
        ) > 1:
            validation_errors["was_created"] = (
                "Solo puede registrarse un resultado principal "
                "de modificación."
            )

        if (
            self.was_created
            and self.result_type != self.ResultType.CREATED
        ):
            validation_errors["result_type"] = (
                "Un registro creado debe tener resultado creado."
            )

        if (
            self.was_updated
            and self.result_type != self.ResultType.UPDATED
        ):
            validation_errors["result_type"] = (
                "Un registro actualizado debe tener "
                "resultado actualizado."
            )

        if (
            self.was_deleted
            and self.result_type != self.ResultType.DELETED
        ):
            validation_errors["result_type"] = (
                "Un registro eliminado debe tener "
                "resultado eliminado."
            )

        if (
            self.was_archived
            and self.result_type != self.ResultType.ARCHIVED
        ):
            validation_errors["result_type"] = (
                "Un registro archivado debe tener "
                "resultado archivado."
            )

        if (
            self.was_unchanged
            and self.result_type != self.ResultType.UNCHANGED
        ):
            validation_errors["result_type"] = (
                "Un registro sin cambios debe tener "
                "resultado sin cambios."
            )

        if (
            self.requires_review
            and not self.review_reason.strip()
        ):
            validation_errors["review_reason"] = (
                "Debes indicar el motivo de revisión."
            )

        if (
            self.reviewed_at
            and not self.reviewed_by_id
        ):
            validation_errors["reviewed_by"] = (
                "Debes indicar quién revisó el elemento."
            )

        if (
            self.reviewed_by_id
            and not self.reviewed_at
        ):
            validation_errors["reviewed_at"] = (
                "Debes indicar cuándo fue revisado."
            )

        if (
            self.rolled_back_at
            and not self.rolled_back_by_id
        ):
            validation_errors["rolled_back_by"] = (
                "Debes indicar quién realizó la reversión."
            )

        if (
            self.rolled_back_at
            and not self.rollback_reason.strip()
        ):
            validation_errors["rollback_reason"] = (
                "Debes indicar el motivo de reversión."
            )

        if (
            self.rolled_back_at
            and not self.rollback_available
        ):
            validation_errors["rollback_available"] = (
                "El elemento no estaba habilitado "
                "para reversión."
            )

        if self.retry_count > self.maximum_retries:
            validation_errors["retry_count"] = (
                "Los reintentos no pueden superar "
                "el máximo permitido."
            )

        if (
            self.next_retry_at
            and self.retry_count >= self.maximum_retries
        ):
            validation_errors["next_retry_at"] = (
                "No puedes programar otro reintento."
            )

        if (
            self.retry_of_id
            and self.retry_of_id == self.id
        ):
            validation_errors["retry_of"] = (
                "Un elemento no puede ser reintento "
                "de sí mismo."
            )

        if (
            self.parent_item_id
            and self.parent_item_id == self.id
        ):
            validation_errors["parent_item"] = (
                "Un elemento no puede depender de sí mismo."
            )

        if (
            self.retry_of_id
            and self.retry_of.processing_run_id
            != self.processing_run_id
        ):
            validation_errors["retry_of"] = (
                "El elemento original debe pertenecer "
                "a la misma ejecución."
            )

        if (
            self.parent_item_id
            and self.parent_item.processing_run_id
            != self.processing_run_id
        ):
            validation_errors["parent_item"] = (
                "El elemento principal debe pertenecer "
                "a la misma ejecución."
            )

        if validation_errors:
            raise ValidationError(
                validation_errors
            )

    def save(self, *args, **kwargs):
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
            self.started_at
            and self.finished_at
        ):
            self.calculate_duration()

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def start(
        self,
        user=None,
    ):
        if self.status != self.Status.PENDING:
            raise ValidationError(
                "Solo puedes iniciar un elemento pendiente."
            )

        if self.processing_run.status not in (
            AttendanceProcessingRun.Status.RUNNING,
            AttendanceProcessingRun.Status.CANCEL_REQUESTED,
        ):
            raise ValidationError(
                "La ejecución principal no está activa."
            )

        self.status = self.Status.PROCESSING
        self.started_at = timezone.now()
        self.finished_at = None
        self.result_type = None
        self.error_category = self.ErrorCategory.NONE
        self.error_code = ""
        self.error_message = ""
        self.exception_type = ""
        self.stack_trace = ""
        self.updated_by = user

        self.save()

    def mark_success(
        self,
        *,
        result_type,
        output_data=None,
        new_values=None,
        changed_fields=None,
        was_created=False,
        was_updated=False,
        was_deleted=False,
        was_archived=False,
        was_unchanged=False,
        rollback_available=False,
        user=None,
    ):
        if self.status != self.Status.PROCESSING:
            raise ValidationError(
                "Solo puedes completar un elemento "
                "que está procesándose."
            )

        now = timezone.now()

        self.status = self.Status.SUCCESS
        self.result_type = result_type
        self.finished_at = now
        self.output_data = output_data or {}
        self.new_values = new_values or {}
        self.changed_fields = changed_fields or []
        self.was_created = was_created
        self.was_updated = was_updated
        self.was_deleted = was_deleted
        self.was_archived = was_archived
        self.was_unchanged = was_unchanged
        self.rollback_available = rollback_available
        self.requires_review = False
        self.review_reason = ""
        self.warning_code = ""
        self.warning_message = ""
        self.warnings = []
        self.error_category = self.ErrorCategory.NONE
        self.error_code = ""
        self.error_message = ""
        self.errors = []
        self.updated_by = user

        self.calculate_duration()
        self.save()

    def mark_success_with_warning(
        self,
        *,
        result_type,
        warning_message,
        warning_code="",
        warnings=None,
        output_data=None,
        new_values=None,
        changed_fields=None,
        requires_review=True,
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
                "Solo puedes completar un elemento "
                "que está procesándose."
            )

        self.status = self.Status.SUCCESS_WITH_WARNINGS
        self.result_type = result_type
        self.finished_at = timezone.now()
        self.warning_code = str(
            warning_code or ""
        ).strip()
        self.warning_message = warning_message
        self.warnings = warnings or []
        self.output_data = output_data or {}
        self.new_values = new_values or {}
        self.changed_fields = changed_fields or []
        self.requires_review = requires_review
        self.review_reason = str(
            review_reason
            or warning_message
        ).strip()
        self.updated_by = user

        self.calculate_duration()
        self.save()

    def mark_failed(
        self,
        *,
        error_message,
        error_category=ErrorCategory.UNKNOWN,
        error_code="",
        exception_type="",
        stack_trace="",
        errors=None,
        output_data=None,
        next_retry_at=None,
        requires_review=True,
        user=None,
    ):
        error_message = str(
            error_message or ""
        ).strip()

        if not error_message:
            raise ValidationError(
                "Debes indicar el error."
            )

        if self.status not in (
            self.Status.PENDING,
            self.Status.PROCESSING,
        ):
            raise ValidationError(
                "El elemento no puede marcarse como fallido."
            )

        now = timezone.now()

        if not self.started_at:
            self.started_at = now

        self.status = self.Status.FAILED
        self.result_type = self.ResultType.ERROR
        self.finished_at = now
        self.error_category = error_category
        self.error_code = str(
            error_code or ""
        ).strip()
        self.error_message = error_message
        self.exception_type = str(
            exception_type or ""
        ).strip()
        self.stack_trace = str(
            stack_trace or ""
        )
        self.errors = errors or []
        self.output_data = output_data or {}
        self.requires_review = requires_review
        self.review_reason = (
            error_message
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

        self.calculate_duration()
        self.save()

    def skip(
        self,
        *,
        reason,
        output_data=None,
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

        if not self.started_at:
            self.started_at = now

        self.status = self.Status.SKIPPED
        self.result_type = self.ResultType.SKIPPED
        self.finished_at = now
        self.output_data = output_data or {}
        self.warning_message = reason
        self.updated_by = user

        self.calculate_duration()
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
                "El elemento ya se encuentra finalizado."
            )

        now = timezone.now()

        if not self.started_at:
            self.started_at = now

        self.status = self.Status.CANCELLED
        self.result_type = self.ResultType.CANCELLED
        self.finished_at = now
        self.warning_message = reason
        self.updated_by = user

        self.calculate_duration()
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
                "El elemento no admite otro reintento."
            )

        retry_item = AttendanceProcessingItem(
            processing_run=self.processing_run,
            sequence_number=sequence_number,
            item_type=self.item_type,
            status=self.Status.PENDING,
            action_type=self.action_type,
            employee_profile=self.employee_profile,
            process_date=self.process_date,
            content_type=self.content_type,
            object_id=self.object_id,
            object_model=self.object_model,
            object_representation=(
                self.object_representation
            ),
            external_reference=self.external_reference,
            input_data=dict(
                self.input_data or {}
            ),
            previous_values=dict(
                self.previous_values or {}
            ),
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
                "El elemento no está disponible para reversión."
            )

        self.status = self.Status.ROLLED_BACK
        self.result_type = self.ResultType.ROLLED_BACK
        self.rolled_back_at = timezone.now()
        self.rolled_back_by = user
        self.rollback_reason = reason
        self.rollback_result = result or {}
        self.finished_at = (
            self.finished_at
            or self.rolled_back_at
        )
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
        processing_run,
        sequence_number,
        content_object,
        item_type=ItemType.GENERIC_OBJECT,
        action_type=ActionType.OTHER,
        employee_profile=None,
        process_date=None,
        external_reference="",
        input_data=None,
        previous_values=None,
        maximum_retries=0,
        parent_item=None,
        created_by=None,
    ):
        """
        Crea un elemento vinculado con cualquier objeto
        mediante ContentType.
        """

        if content_object is None:
            raise ValidationError(
                "Debes indicar el objeto que será procesado."
            )

        content_type = (
            ContentType.objects
            .get_for_model(
                content_object,
                for_concrete_model=False,
            )
        )

        item = cls(
            processing_run=processing_run,
            sequence_number=sequence_number,
            item_type=item_type,
            action_type=action_type,
            employee_profile=employee_profile,
            process_date=process_date,
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
            input_data=input_data or {},
            previous_values=previous_values or {},
            maximum_retries=maximum_retries,
            parent_item=parent_item,
            created_by=created_by,
            updated_by=created_by,
        )

        item.save()

        return item