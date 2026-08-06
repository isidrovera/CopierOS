# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class AttendanceProcessingRun(models.Model):
    """
    Registro de ejecución de procesos automáticos de asistencia.

    Permite controlar procesos como:

    - Procesamiento diario de asistencia.
    - Reprocesamiento de marcaciones.
    - Detección automática de incidencias.
    - Cierre de asistencias diarias.
    - Consolidación mensual.
    - Recálculo de indicadores.
    - Vencimiento de permisos y justificaciones.
    - Vencimiento de correcciones.
    - Verificación de horas extras.
    - Cierre de sesiones operativas.
    - Generación de reportes.
    - Entrega de reportes.
    - Envío de notificaciones.
    - Limpieza y archivado controlado.

    Cada ejecución conserva:

    - Periodo procesado.
    - Parámetros.
    - Estado.
    - Progreso.
    - Registros procesados.
    - Errores.
    - Advertencias.
    - Reintentos.
    - Usuario o proceso que inició la ejecución.
    """

    class ProcessType(models.TextChoices):
        DAILY_ATTENDANCE = (
            "daily_attendance",
            "Procesamiento diario de asistencia",
        )
        DAILY_REPROCESSING = (
            "daily_reprocessing",
            "Reprocesamiento diario",
        )
        CLOCKING_VALIDATION = (
            "clocking_validation",
            "Validación de marcaciones",
        )
        INCIDENT_DETECTION = (
            "incident_detection",
            "Detección de incidencias",
        )
        DAILY_CLOSURE = (
            "daily_closure",
            "Cierre diario",
        )
        MONTHLY_CONSOLIDATION = (
            "monthly_consolidation",
            "Consolidación mensual",
        )
        MONTHLY_RECALCULATION = (
            "monthly_recalculation",
            "Recálculo mensual",
        )
        MONTHLY_CLOSURE = (
            "monthly_closure",
            "Cierre mensual",
        )
        LEAVE_EXPIRATION = (
            "leave_expiration",
            "Vencimiento de permisos",
        )
        JUSTIFICATION_EXPIRATION = (
            "justification_expiration",
            "Vencimiento de justificaciones",
        )
        CORRECTION_EXPIRATION = (
            "correction_expiration",
            "Vencimiento de correcciones",
        )
        OVERTIME_VERIFICATION = (
            "overtime_verification",
            "Verificación de horas extras",
        )
        OPERATIONAL_SESSION_REVIEW = (
            "operational_session_review",
            "Revisión de sesiones operativas",
        )
        REPORT_GENERATION = (
            "report_generation",
            "Generación de reportes",
        )
        REPORT_DELIVERY = (
            "report_delivery",
            "Entrega de reportes",
        )
        NOTIFICATION_DELIVERY = (
            "notification_delivery",
            "Envío de notificaciones",
        )
        POLICY_ACTIVATION = (
            "policy_activation",
            "Activación de políticas",
        )
        POLICY_EXPIRATION = (
            "policy_expiration",
            "Vencimiento de políticas",
        )
        SCHEDULE_ACTIVATION = (
            "schedule_activation",
            "Activación de horarios",
        )
        SCHEDULE_EXPIRATION = (
            "schedule_expiration",
            "Vencimiento de horarios",
        )
        DEVICE_PERMISSION_EXPIRATION = (
            "device_permission_expiration",
            "Vencimiento de permisos de dispositivo",
        )
        DATA_ARCHIVING = (
            "data_archiving",
            "Archivado de información",
        )
        DATA_CLEANUP = (
            "data_cleanup",
            "Limpieza de información",
        )
        DATA_IMPORT = (
            "data_import",
            "Importación de información",
        )
        DATA_EXPORT = (
            "data_export",
            "Exportación de información",
        )
        MANUAL_PROCESS = (
            "manual_process",
            "Proceso manual",
        )
        OTHER = (
            "other",
            "Otro proceso",
        )

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        QUEUED = (
            "queued",
            "En cola",
        )
        RUNNING = (
            "running",
            "En ejecución",
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
        TIMED_OUT = (
            "timed_out",
            "Tiempo agotado",
        )
        SKIPPED = (
            "skipped",
            "Omitido",
        )

    class TriggerType(models.TextChoices):
        SCHEDULED = (
            "scheduled",
            "Programado",
        )
        MANUAL = (
            "manual",
            "Manual",
        )
        API = (
            "api",
            "API",
        )
        MANAGEMENT_COMMAND = (
            "management_command",
            "Comando de administración",
        )
        SYSTEM_EVENT = (
            "system_event",
            "Evento del sistema",
        )
        RETRY = (
            "retry",
            "Reintento",
        )
        DEPENDENCY = (
            "dependency",
            "Proceso dependiente",
        )

    class ScopeType(models.TextChoices):
        GLOBAL = (
            "global",
            "Global",
        )
        DATE = (
            "date",
            "Fecha",
        )
        DATE_RANGE = (
            "date_range",
            "Rango de fechas",
        )
        MONTH = (
            "month",
            "Mes",
        )
        EMPLOYEE = (
            "employee",
            "Trabajador",
        )
        EMPLOYEE_DATE = (
            "employee_date",
            "Trabajador y fecha",
        )
        EMPLOYEE_RANGE = (
            "employee_range",
            "Trabajador y rango",
        )
        LOCATION = (
            "location",
            "Ubicación",
        )
        DEPARTMENT = (
            "department",
            "Área",
        )
        COMPANY = (
            "company",
            "Empresa",
        )
        OBJECT = (
            "object",
            "Objeto específico",
        )
        CUSTOM = (
            "custom",
            "Personalizado",
        )

    class ResultType(models.TextChoices):
        SUCCESS = (
            "success",
            "Correcto",
        )
        SUCCESS_WITH_WARNINGS = (
            "success_with_warnings",
            "Correcto con advertencias",
        )
        PARTIAL = (
            "partial",
            "Parcial",
        )
        ERROR = (
            "error",
            "Error",
        )
        CANCELLED = (
            "cancelled",
            "Cancelado",
        )
        NO_DATA = (
            "no_data",
            "Sin información",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    run_number = models.CharField(
        max_length=60,
        unique=True,
        db_index=True,
        verbose_name="Número de ejecución",
    )

    process_type = models.CharField(
        max_length=50,
        choices=ProcessType.choices,
        db_index=True,
        verbose_name="Tipo de proceso",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    trigger_type = models.CharField(
        max_length=30,
        choices=TriggerType.choices,
        default=TriggerType.SCHEDULED,
        db_index=True,
        verbose_name="Tipo de ejecución",
    )

    scope_type = models.CharField(
        max_length=30,
        choices=ScopeType.choices,
        default=ScopeType.GLOBAL,
        db_index=True,
        verbose_name="Alcance",
    )

    result_type = models.CharField(
        max_length=30,
        choices=ResultType.choices,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Resultado",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Título",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    employee_profile = models.ForeignKey(
        "attendance.EmployeeProfile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="processing_runs",
        verbose_name="Trabajador",
    )

    work_location = models.ForeignKey(
        "attendance.WorkLocation",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="processing_runs",
        verbose_name="Ubicación",
    )

    company_name = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
        verbose_name="Empresa",
    )

    department_name = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Área o departamento",
    )

    process_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de proceso",
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

    target_model = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Modelo objetivo",
    )

    target_object_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="ID del objeto objetivo",
    )

    parameters = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Parámetros",
    )

    filters = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Filtros",
    )

    options = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Opciones",
    )

    requested_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Solicitado el",
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_processing_runs_requested",
        verbose_name="Solicitado por",
    )

    queued_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Enviado a cola el",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Iniciado el",
    )

    heartbeat_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Último latido",
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Finalizado el",
    )

    timeout_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Tiempo máximo hasta",
    )

    timeout_seconds = models.PositiveIntegerField(
        default=3600,
        verbose_name="Tiempo máximo en segundos",
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

    processed_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Registros procesados",
    )

    successful_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Registros correctos",
    )

    warning_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Registros con advertencias",
    )

    failed_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Registros fallidos",
    )

    skipped_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Registros omitidos",
    )

    total_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Total de registros",
    )

    created_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Registros creados",
    )

    updated_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Registros actualizados",
    )

    deleted_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Registros eliminados",
    )

    archived_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Registros archivados",
    )

    unchanged_records = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Registros sin cambios",
    )

    result_summary = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resumen del resultado",
    )

    result_details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Detalle del resultado",
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

    task_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="ID de tarea",
    )

    worker_name = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Trabajador de tareas",
    )

    queue_name = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Cola",
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
        verbose_name="Clave de lote",
    )

    correlation_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="ID de correlación",
    )

    parent_run = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="child_runs",
        verbose_name="Ejecución principal",
    )

    retry_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="retry_runs",
        verbose_name="Reintento de",
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
        related_name="attendance_processing_runs_cancel_requested",
        verbose_name="Cancelación solicitada por",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Cancelado el",
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
        related_name="attendance_processing_runs_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_processing_runs_updated",
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
        related_name="attendance_processing_runs_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Ejecución de procesamiento de asistencia"
        verbose_name_plural = (
            "Ejecuciones de procesamiento de asistencia"
        )

        ordering = (
            "-requested_at",
            "-created_at",
        )

        indexes = (
            models.Index(
                fields=(
                    "process_type",
                    "status",
                    "requested_at",
                ),
                name="att_prun_type_status_idx",
            ),
            models.Index(
                fields=(
                    "scope_type",
                    "process_date",
                    "status",
                ),
                name="att_prun_scope_date_idx",
            ),
            models.Index(
                fields=(
                    "employee_profile",
                    "process_type",
                    "status",
                ),
                name="att_prun_emp_process_idx",
            ),
            models.Index(
                fields=(
                    "work_location",
                    "process_type",
                    "status",
                ),
                name="att_prun_location_idx",
            ),
            models.Index(
                fields=(
                    "start_date",
                    "end_date",
                    "process_type",
                ),
                name="att_prun_date_range_idx",
            ),
            models.Index(
                fields=(
                    "year",
                    "month",
                    "process_type",
                ),
                name="att_prun_month_idx",
            ),
            models.Index(
                fields=(
                    "queued_at",
                    "started_at",
                    "finished_at",
                ),
                name="att_prun_lifecycle_idx",
            ),
            models.Index(
                fields=(
                    "heartbeat_at",
                    "status",
                ),
                name="att_prun_heartbeat_idx",
            ),
            models.Index(
                fields=(
                    "timeout_at",
                    "status",
                ),
                name="att_prun_timeout_idx",
            ),
            models.Index(
                fields=(
                    "next_retry_at",
                    "retry_count",
                    "status",
                ),
                name="att_prun_retry_idx",
            ),
            models.Index(
                fields=(
                    "task_id",
                    "queue_name",
                    "status",
                ),
                name="att_prun_task_queue_idx",
            ),
            models.Index(
                fields=(
                    "batch_key",
                    "correlation_id",
                ),
                name="att_prun_batch_corr_idx",
            ),
            models.Index(
                fields=(
                    "parent_run",
                    "process_type",
                ),
                name="att_prun_parent_idx",
            ),
            models.Index(
                fields=(
                    "error_code",
                    "exception_type",
                    "status",
                ),
                name="att_prun_error_idx",
            ),
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
                name="att_prun_progress_range",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    processed_records__lte=models.F(
                        "total_records"
                    ),
                ),
                name="att_prun_processed_lte_total",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    successful_records__lte=models.F(
                        "processed_records"
                    ),
                ),
                name="att_prun_success_lte_processed",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    failed_records__lte=models.F(
                        "processed_records"
                    ),
                ),
                name="att_prun_failed_lte_processed",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    warning_records__lte=models.F(
                        "processed_records"
                    ),
                ),
                name="att_prun_warning_lte_processed",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    skipped_records__lte=models.F(
                        "total_records"
                    ),
                ),
                name="att_prun_skipped_lte_total",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    retry_count__lte=models.F(
                        "maximum_retries"
                    ),
                ),
                name="att_prun_retry_lte_max",
            ),
        )

    def __str__(self):
        return (
            f"{self.run_number} - "
            f"{self.get_process_type_display()} - "
            f"{self.get_status_display()}"
        )

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_running(self):
        return self.status == self.Status.RUNNING

    @property
    def is_finished(self):
        return self.status in (
            self.Status.COMPLETED,
            self.Status.PARTIALLY_COMPLETED,
            self.Status.FAILED,
            self.Status.CANCELLED,
            self.Status.TIMED_OUT,
            self.Status.SKIPPED,
        )

    @property
    def has_errors(self):
        return bool(
            self.error_message
            or self.errors
            or self.failed_records
        )

    @property
    def has_warnings(self):
        return bool(
            self.warnings
            or self.warning_records
        )

    @property
    def can_retry(self):
        return (
            self.status
            in (
                self.Status.FAILED,
                self.Status.TIMED_OUT,
            )
            and self.retry_count < self.maximum_retries
            and self.archived_at is None
        )

    @property
    def duration_seconds(self):
        if not self.started_at:
            return 0

        end_at = (
            self.finished_at
            or timezone.now()
        )

        if end_at <= self.started_at:
            return 0

        return int(
            (
                end_at - self.started_at
            ).total_seconds()
        )

    @property
    def remaining_records(self):
        return max(
            0,
            self.total_records
            - self.processed_records
            - self.skipped_records,
        )

    def clean(self):
        super().clean()

        errors = {}

        if not self.title.strip():
            errors["title"] = (
                "Debes indicar el título de la ejecución."
            )

        if (
            self.employee_profile_id
            and self.employee_profile.archived_at
        ):
            errors["employee_profile"] = (
                "El perfil laboral está archivado."
            )

        if (
            self.work_location_id
            and self.work_location.archived_at
        ):
            errors["work_location"] = (
                "La ubicación está archivada."
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
            self.scope_type == self.ScopeType.DATE
            and not self.process_date
        ):
            errors["process_date"] = (
                "Debes indicar la fecha que será procesada."
            )

        if (
            self.scope_type == self.ScopeType.DATE_RANGE
            and (
                not self.start_date
                or not self.end_date
            )
        ):
            errors["start_date"] = (
                "Debes indicar el rango de fechas."
            )

        if (
            self.scope_type == self.ScopeType.MONTH
            and (
                self.year is None
                or self.month is None
            )
        ):
            errors["year"] = (
                "Debes indicar el año y mes."
            )

        if (
            self.scope_type
            in (
                self.ScopeType.EMPLOYEE,
                self.ScopeType.EMPLOYEE_DATE,
                self.ScopeType.EMPLOYEE_RANGE,
            )
            and not self.employee_profile_id
        ):
            errors["employee_profile"] = (
                "Debes seleccionar el trabajador."
            )

        if (
            self.scope_type == self.ScopeType.EMPLOYEE_DATE
            and not self.process_date
        ):
            errors["process_date"] = (
                "Debes indicar la fecha del trabajador."
            )

        if (
            self.scope_type == self.ScopeType.EMPLOYEE_RANGE
            and (
                not self.start_date
                or not self.end_date
            )
        ):
            errors["start_date"] = (
                "Debes indicar el rango del trabajador."
            )

        if (
            self.scope_type == self.ScopeType.LOCATION
            and not self.work_location_id
        ):
            errors["work_location"] = (
                "Debes seleccionar la ubicación."
            )

        if (
            self.scope_type == self.ScopeType.DEPARTMENT
            and not self.department_name.strip()
        ):
            errors["department_name"] = (
                "Debes indicar el área o departamento."
            )

        if (
            self.scope_type == self.ScopeType.COMPANY
            and not self.company_name.strip()
        ):
            errors["company_name"] = (
                "Debes indicar la empresa."
            )

        if (
            self.scope_type == self.ScopeType.OBJECT
            and (
                not self.target_model.strip()
                or not self.target_object_id.strip()
            )
        ):
            errors["target_object_id"] = (
                "Debes indicar el modelo y el ID objetivo."
            )

        json_object_fields = (
            "parameters",
            "filters",
            "options",
            "result_summary",
            "result_details",
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

        if self.processed_records > self.total_records:
            errors["processed_records"] = (
                "Los registros procesados no pueden superar "
                "el total."
            )

        if (
            self.successful_records
            > self.processed_records
        ):
            errors["successful_records"] = (
                "Los registros correctos no pueden superar "
                "los procesados."
            )

        if self.failed_records > self.processed_records:
            errors["failed_records"] = (
                "Los registros fallidos no pueden superar "
                "los procesados."
            )

        if self.warning_records > self.processed_records:
            errors["warning_records"] = (
                "Los registros observados no pueden superar "
                "los procesados."
            )

        if self.skipped_records > self.total_records:
            errors["skipped_records"] = (
                "Los registros omitidos no pueden superar "
                "el total."
            )

        if (
            self.status == self.Status.QUEUED
            and not self.queued_at
        ):
            errors["queued_at"] = (
                "Una ejecución en cola debe registrar "
                "la fecha de encolado."
            )

        if (
            self.status
            in (
                self.Status.RUNNING,
                self.Status.CANCEL_REQUESTED,
            )
            and not self.started_at
        ):
            errors["started_at"] = (
                "Una ejecución iniciada debe registrar "
                "la fecha de inicio."
            )

        if (
            self.status == self.Status.RUNNING
            and not self.heartbeat_at
        ):
            errors["heartbeat_at"] = (
                "Una ejecución activa debe registrar "
                "su último latido."
            )

        if self.is_finished and not self.finished_at:
            errors["finished_at"] = (
                "Una ejecución finalizada debe registrar "
                "la fecha de finalización."
            )

        if (
            self.status == self.Status.COMPLETED
            and self.result_type
            not in (
                self.ResultType.SUCCESS,
                self.ResultType.SUCCESS_WITH_WARNINGS,
                self.ResultType.NO_DATA,
            )
        ):
            errors["result_type"] = (
                "El resultado no corresponde a una ejecución "
                "completada."
            )

        if (
            self.status
            == self.Status.PARTIALLY_COMPLETED
            and self.result_type != self.ResultType.PARTIAL
        ):
            errors["result_type"] = (
                "Una ejecución parcial debe tener "
                "resultado parcial."
            )

        if (
            self.status == self.Status.FAILED
            and not self.error_message.strip()
        ):
            errors["error_message"] = (
                "Una ejecución fallida debe registrar "
                "el mensaje de error."
            )

        if (
            self.status == self.Status.FAILED
            and self.result_type != self.ResultType.ERROR
        ):
            errors["result_type"] = (
                "Una ejecución fallida debe tener "
                "resultado de error."
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
                "Una ejecución cancelada debe registrar "
                "la fecha de cancelación."
            )

        if (
            self.status == self.Status.TIMED_OUT
            and self.result_type != self.ResultType.ERROR
        ):
            errors["result_type"] = (
                "Una ejecución agotada debe tener "
                "resultado de error."
            )

        if (
            self.timeout_at
            and self.started_at
            and self.timeout_at <= self.started_at
        ):
            errors["timeout_at"] = (
                "El vencimiento debe ser posterior al inicio."
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
            self.parent_run_id
            and self.parent_run_id == self.id
        ):
            errors["parent_run"] = (
                "Una ejecución no puede depender de sí misma."
            )

        if (
            self.retry_of_id
            and self.retry_of_id == self.id
        ):
            errors["retry_of"] = (
                "Una ejecución no puede ser reintento "
                "de sí misma."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.run_number = str(
            self.run_number or ""
        ).strip().upper()

        self.title = str(
            self.title or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        self.company_name = str(
            self.company_name or ""
        ).strip()

        self.department_name = str(
            self.department_name or ""
        ).strip()

        self.target_model = str(
            self.target_model or ""
        ).strip().lower()

        self.target_object_id = str(
            self.target_object_id or ""
        ).strip()

        if (
            self.started_at
            and not self.timeout_at
            and self.timeout_seconds > 0
        ):
            self.timeout_at = (
                self.started_at
                + timezone.timedelta(
                    seconds=self.timeout_seconds,
                )
            )

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def queue(
        self,
        *,
        task_id="",
        queue_name="",
        user=None,
    ):
        if self.status not in (
            self.Status.PENDING,
            self.Status.FAILED,
            self.Status.TIMED_OUT,
        ):
            raise ValidationError(
                "La ejecución no puede enviarse a cola "
                "desde su estado actual."
            )

        self.status = self.Status.QUEUED
        self.queued_at = timezone.now()
        self.task_id = str(
            task_id or ""
        ).strip()
        self.queue_name = str(
            queue_name or ""
        ).strip()
        self.next_retry_at = None
        self.error_code = ""
        self.error_message = ""
        self.exception_type = ""
        self.stack_trace = ""
        self.updated_by = user

        self.save()

    def start(
        self,
        *,
        total_records=0,
        worker_name="",
        task_id="",
        user=None,
    ):
        if self.status not in (
            self.Status.PENDING,
            self.Status.QUEUED,
        ):
            raise ValidationError(
                "La ejecución no puede iniciarse "
                "desde su estado actual."
            )

        if total_records < 0:
            raise ValidationError(
                "El total de registros no puede ser negativo."
            )

        now = timezone.now()

        self.status = self.Status.RUNNING
        self.started_at = now
        self.heartbeat_at = now
        self.finished_at = None
        self.timeout_at = (
            now
            + timezone.timedelta(
                seconds=self.timeout_seconds,
            )
            if self.timeout_seconds > 0
            else None
        )
        self.total_records = total_records
        self.processed_records = 0
        self.successful_records = 0
        self.warning_records = 0
        self.failed_records = 0
        self.skipped_records = 0
        self.progress_percentage = 0
        self.current_stage = "Iniciando procesamiento"
        self.worker_name = str(
            worker_name or ""
        ).strip()

        if task_id:
            self.task_id = str(
                task_id
            ).strip()

        self.result_type = None
        self.error_code = ""
        self.error_message = ""
        self.exception_type = ""
        self.stack_trace = ""
        self.warnings = []
        self.errors = []
        self.updated_by = user

        self.save()

    def heartbeat(
        self,
        *,
        current_stage="",
        processed_records=None,
        total_records=None,
    ):
        if self.status not in (
            self.Status.RUNNING,
            self.Status.CANCEL_REQUESTED,
        ):
            raise ValidationError(
                "Solo una ejecución activa puede "
                "actualizar su latido."
            )

        if total_records is not None:
            if total_records < 0:
                raise ValidationError(
                    "El total de registros no puede ser negativo."
                )

            self.total_records = total_records

        if processed_records is not None:
            if processed_records < 0:
                raise ValidationError(
                    "Los registros procesados no pueden "
                    "ser negativos."
                )

            if (
                self.total_records > 0
                and processed_records > self.total_records
            ):
                raise ValidationError(
                    "Los registros procesados no pueden superar "
                    "el total."
                )

            self.processed_records = processed_records

        if current_stage:
            self.current_stage = str(
                current_stage
            ).strip()

        self.heartbeat_at = timezone.now()
        self._calculate_progress()

        self.save(
            update_fields=[
                "total_records",
                "processed_records",
                "current_stage",
                "heartbeat_at",
                "progress_percentage",
                "updated_at",
            ]
        )

    def update_progress(
        self,
        *,
        processed_increment=0,
        successful_increment=0,
        warning_increment=0,
        failed_increment=0,
        skipped_increment=0,
        created_increment=0,
        updated_increment=0,
        deleted_increment=0,
        archived_increment=0,
        unchanged_increment=0,
        current_stage="",
    ):
        if self.status not in (
            self.Status.RUNNING,
            self.Status.CANCEL_REQUESTED,
        ):
            raise ValidationError(
                "La ejecución no está activa."
            )

        increments = (
            processed_increment,
            successful_increment,
            warning_increment,
            failed_increment,
            skipped_increment,
            created_increment,
            updated_increment,
            deleted_increment,
            archived_increment,
            unchanged_increment,
        )

        if any(
            value < 0
            for value in increments
        ):
            raise ValidationError(
                "Los incrementos no pueden ser negativos."
            )

        self.processed_records += processed_increment
        self.successful_records += successful_increment
        self.warning_records += warning_increment
        self.failed_records += failed_increment
        self.skipped_records += skipped_increment
        self.created_records += created_increment
        self.updated_records += updated_increment
        self.deleted_records += deleted_increment
        self.archived_records += archived_increment
        self.unchanged_records += unchanged_increment

        if current_stage:
            self.current_stage = str(
                current_stage
            ).strip()

        self.heartbeat_at = timezone.now()
        self._calculate_progress()
        self.save()

    def _calculate_progress(self):
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

        self.progress_percentage = round(
            (
                completed_records
                / self.total_records
            )
            * 100,
            2,
        )

        return self.progress_percentage

    def add_warning(
        self,
        *,
        message,
        code="",
        record_reference="",
        details=None,
    ):
        message = str(
            message or ""
        ).strip()

        if not message:
            raise ValidationError(
                "Debes indicar la advertencia."
            )

        warnings = list(
            self.warnings or []
        )

        warnings.append(
            {
                "code": str(
                    code or ""
                ).strip(),
                "message": message,
                "record_reference": str(
                    record_reference or ""
                ).strip(),
                "details": details or {},
                "occurred_at": timezone.now().isoformat(),
            }
        )

        self.warnings = warnings
        self.warning_records += 1
        self.heartbeat_at = timezone.now()

        self.save(
            update_fields=[
                "warnings",
                "warning_records",
                "heartbeat_at",
                "updated_at",
            ]
        )

    def add_error(
        self,
        *,
        message,
        code="",
        record_reference="",
        exception_type="",
        details=None,
    ):
        message = str(
            message or ""
        ).strip()

        if not message:
            raise ValidationError(
                "Debes indicar el error."
            )

        errors = list(
            self.errors or []
        )

        errors.append(
            {
                "code": str(
                    code or ""
                ).strip(),
                "message": message,
                "record_reference": str(
                    record_reference or ""
                ).strip(),
                "exception_type": str(
                    exception_type or ""
                ).strip(),
                "details": details or {},
                "occurred_at": timezone.now().isoformat(),
            }
        )

        self.errors = errors
        self.failed_records += 1
        self.heartbeat_at = timezone.now()

        self.save(
            update_fields=[
                "errors",
                "failed_records",
                "heartbeat_at",
                "updated_at",
            ]
        )

    def complete(
        self,
        *,
        summary=None,
        details=None,
        user=None,
    ):
        if self.status not in (
            self.Status.RUNNING,
            self.Status.CANCEL_REQUESTED,
        ):
            raise ValidationError(
                "La ejecución no está activa."
            )

        if self.status == self.Status.CANCEL_REQUESTED:
            self.mark_cancelled(
                user=user,
            )
            return

        now = timezone.now()

        self.finished_at = now
        self.heartbeat_at = now
        self.progress_percentage = 100
        self.result_summary = summary or {}
        self.result_details = details or {}
        self.next_retry_at = None
        self.current_stage = "Procesamiento finalizado"
        self.updated_by = user

        if self.total_records == 0:
            self.status = self.Status.COMPLETED
            self.result_type = self.ResultType.NO_DATA

        elif self.failed_records > 0:
            if self.successful_records > 0:
                self.status = (
                    self.Status.PARTIALLY_COMPLETED
                )
                self.result_type = self.ResultType.PARTIAL
            else:
                self.status = self.Status.FAILED
                self.result_type = self.ResultType.ERROR

                if not self.error_message:
                    self.error_message = (
                        "La ejecución finalizó sin registros "
                        "procesados correctamente."
                    )

        elif self.warning_records > 0:
            self.status = self.Status.COMPLETED
            self.result_type = (
                self.ResultType.SUCCESS_WITH_WARNINGS
            )

        else:
            self.status = self.Status.COMPLETED
            self.result_type = self.ResultType.SUCCESS

        self.save()

    def fail(
        self,
        *,
        error,
        error_code="",
        exception_type="",
        stack_trace="",
        details=None,
        next_retry_at=None,
        user=None,
    ):
        error = str(
            error or ""
        ).strip()

        if not error:
            raise ValidationError(
                "Debes indicar el error del proceso."
            )

        if self.status not in (
            self.Status.PENDING,
            self.Status.QUEUED,
            self.Status.RUNNING,
            self.Status.CANCEL_REQUESTED,
        ):
            raise ValidationError(
                "La ejecución no puede marcarse como fallida."
            )

        now = timezone.now()

        self.status = self.Status.FAILED
        self.result_type = self.ResultType.ERROR
        self.finished_at = now
        self.heartbeat_at = now
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
        self.result_details = details or {}
        self.current_stage = "Proceso fallido"
        self.updated_by = user

        if (
            self.retry_count < self.maximum_retries
            and next_retry_at
        ):
            self.next_retry_at = next_retry_at
        else:
            self.next_retry_at = None

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

        if self.status not in (
            self.Status.PENDING,
            self.Status.QUEUED,
            self.Status.RUNNING,
        ):
            raise ValidationError(
                "La ejecución ya no puede cancelarse."
            )

        now = timezone.now()

        self.cancel_requested_at = now
        self.cancel_requested_by = user
        self.cancellation_reason = reason
        self.updated_by = user

        if self.status in (
            self.Status.PENDING,
            self.Status.QUEUED,
        ):
            self.status = self.Status.CANCELLED
            self.result_type = self.ResultType.CANCELLED
            self.cancelled_at = now
            self.finished_at = now
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
                "La ejecución no tiene una cancelación pendiente."
            )

        now = timezone.now()

        self.status = self.Status.CANCELLED
        self.result_type = self.ResultType.CANCELLED
        self.cancelled_at = now
        self.finished_at = now
        self.heartbeat_at = now
        self.current_stage = "Proceso cancelado"
        self.next_retry_at = None
        self.updated_by = user

        self.save()

    def mark_timed_out(
        self,
        *,
        user=None,
    ):
        if self.status not in (
            self.Status.RUNNING,
            self.Status.CANCEL_REQUESTED,
        ):
            raise ValidationError(
                "Solo una ejecución activa puede "
                "marcarse por tiempo agotado."
            )

        if (
            self.timeout_at
            and self.timeout_at > timezone.now()
        ):
            raise ValidationError(
                "La ejecución todavía no ha superado "
                "su tiempo máximo."
            )

        now = timezone.now()

        self.status = self.Status.TIMED_OUT
        self.result_type = self.ResultType.ERROR
        self.finished_at = now
        self.heartbeat_at = now
        self.error_code = "PROCESS_TIMEOUT"
        self.error_message = (
            "La ejecución superó el tiempo máximo permitido."
        )
        self.current_stage = "Tiempo de ejecución agotado"
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

        if self.status not in (
            self.Status.PENDING,
            self.Status.QUEUED,
        ):
            raise ValidationError(
                "La ejecución no puede omitirse "
                "desde su estado actual."
            )

        now = timezone.now()

        self.status = self.Status.SKIPPED
        self.result_type = self.ResultType.NO_DATA
        self.finished_at = now
        self.current_stage = "Proceso omitido"
        self.result_summary = {
            "skip_reason": reason,
        }
        self.updated_by = user

        self.save()

    def prepare_retry(
        self,
        *,
        run_number,
        requested_by=None,
        next_retry_at=None,
    ):
        if not self.can_retry:
            raise ValidationError(
                "La ejecución no admite otro reintento."
            )

        retry_run = AttendanceProcessingRun(
            run_number=run_number,
            process_type=self.process_type,
            status=self.Status.PENDING,
            trigger_type=self.TriggerType.RETRY,
            scope_type=self.scope_type,
            title=self.title,
            description=self.description,
            employee_profile=self.employee_profile,
            work_location=self.work_location,
            company_name=self.company_name,
            department_name=self.department_name,
            process_date=self.process_date,
            start_date=self.start_date,
            end_date=self.end_date,
            year=self.year,
            month=self.month,
            target_model=self.target_model,
            target_object_id=self.target_object_id,
            parameters=dict(
                self.parameters or {}
            ),
            filters=dict(
                self.filters or {}
            ),
            options=dict(
                self.options or {}
            ),
            requested_at=timezone.now(),
            requested_by=requested_by,
            timeout_seconds=self.timeout_seconds,
            batch_key=self.batch_key,
            correlation_id=self.correlation_id,
            parent_run=self.parent_run,
            retry_of=self,
            retry_count=self.retry_count + 1,
            maximum_retries=self.maximum_retries,
            next_retry_at=next_retry_at,
            metadata={
                **dict(self.metadata or {}),
                "original_run_id": str(self.id),
                "original_run_number": self.run_number,
            },
            created_by=requested_by,
            updated_by=requested_by,
        )

        retry_run.save()

        self.next_retry_at = next_retry_at
        self.save(
            update_fields=[
                "next_retry_at",
                "updated_at",
            ]
        )

        return retry_run

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
                "Solo puedes archivar una ejecución finalizada."
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