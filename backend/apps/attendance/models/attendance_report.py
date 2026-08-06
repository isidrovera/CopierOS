# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class AttendanceReport(models.Model):
    """
    Solicitud y resultado de generación de reportes del módulo.

    Permite generar reportes por:

    - Día.
    - Semana.
    - Mes.
    - Año.
    - Rango personalizado.
    - Trabajador.
    - Área.
    - Empresa.
    - Ubicación.
    - Horario.
    - Asistencia.
    - Incidencias.
    - Permisos.
    - Correcciones.
    - Horas extras.
    - Tiempo operativo.
    - Resúmenes mensuales.

    Conserva los filtros utilizados, estado de procesamiento,
    archivo generado, errores y auditoría básica de descarga.
    """

    class ReportType(models.TextChoices):
        DAILY_ATTENDANCE = (
            "daily_attendance",
            "Asistencia diaria",
        )
        WEEKLY_ATTENDANCE = (
            "weekly_attendance",
            "Asistencia semanal",
        )
        MONTHLY_ATTENDANCE = (
            "monthly_attendance",
            "Asistencia mensual",
        )
        ANNUAL_ATTENDANCE = (
            "annual_attendance",
            "Asistencia anual",
        )
        ATTENDANCE_DETAIL = (
            "attendance_detail",
            "Detalle de marcaciones",
        )
        LATE_ARRIVALS = (
            "late_arrivals",
            "Tardanzas",
        )
        ABSENCES = (
            "absences",
            "Ausencias",
        )
        INCOMPLETE_CLOCKINGS = (
            "incomplete_clockings",
            "Marcaciones incompletas",
        )
        ATTENDANCE_INCIDENTS = (
            "attendance_incidents",
            "Incidencias de asistencia",
        )
        LEAVE_REQUESTS = (
            "leave_requests",
            "Permisos y licencias",
        )
        VACATIONS = (
            "vacations",
            "Vacaciones",
        )
        MEDICAL_LEAVES = (
            "medical_leaves",
            "Descansos médicos",
        )
        ATTENDANCE_CORRECTIONS = (
            "attendance_corrections",
            "Correcciones de asistencia",
        )
        OVERTIME = (
            "overtime",
            "Horas extras",
        )
        OPERATIONAL_TIME = (
            "operational_time",
            "Tiempo operativo",
        )
        OPERATIONAL_SESSIONS = (
            "operational_sessions",
            "Sesiones operativas",
        )
        OPERATIONAL_DELAYS = (
            "operational_delays",
            "Demoras operativas",
        )
        PRODUCTIVITY_TIME = (
            "productivity_time",
            "Tiempo productivo",
        )
        EMPLOYEE_MONTHLY_SUMMARY = (
            "employee_monthly_summary",
            "Resumen mensual por trabajador",
        )
        CONSOLIDATED_MONTHLY_SUMMARY = (
            "consolidated_monthly_summary",
            "Resumen mensual consolidado",
        )
        PAYROLL_ATTENDANCE = (
            "payroll_attendance",
            "Asistencia para planilla",
        )
        STAFF_EVALUATION = (
            "staff_evaluation",
            "Asistencia para evaluación",
        )
        DEVICE_USAGE = (
            "device_usage",
            "Uso de dispositivos",
        )
        LOCATION_USAGE = (
            "location_usage",
            "Uso de ubicaciones",
        )
        AUDIT_LOG = (
            "audit_log",
            "Auditoría de asistencia",
        )
        CUSTOM = (
            "custom",
            "Reporte personalizado",
        )

    class PeriodType(models.TextChoices):
        DAY = (
            "day",
            "Día",
        )
        WEEK = (
            "week",
            "Semana",
        )
        MONTH = (
            "month",
            "Mes",
        )
        QUARTER = (
            "quarter",
            "Trimestre",
        )
        YEAR = (
            "year",
            "Año",
        )
        CUSTOM = (
            "custom",
            "Rango personalizado",
        )

    class FileFormat(models.TextChoices):
        PDF = (
            "pdf",
            "PDF",
        )
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
        FAILED = (
            "failed",
            "Fallido",
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
            "Solicitado por usuario",
        )
        SCHEDULED = (
            "scheduled",
            "Generación programada",
        )
        SYSTEM = (
            "system",
            "Generado por el sistema",
        )
        API = (
            "api",
            "Solicitado por API",
        )
        MANAGEMENT_COMMAND = (
            "management_command",
            "Comando de administración",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    report_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Número de reporte",
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

    report_type = models.CharField(
        max_length=50,
        choices=ReportType.choices,
        db_index=True,
        verbose_name="Tipo de reporte",
    )

    period_type = models.CharField(
        max_length=20,
        choices=PeriodType.choices,
        default=PeriodType.CUSTOM,
        db_index=True,
        verbose_name="Tipo de periodo",
    )

    file_format = models.CharField(
        max_length=10,
        choices=FileFormat.choices,
        default=FileFormat.XLSX,
        db_index=True,
        verbose_name="Formato",
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

    start_date = models.DateField(
        db_index=True,
        verbose_name="Fecha inicial",
    )

    end_date = models.DateField(
        db_index=True,
        verbose_name="Fecha final",
    )

    timezone_name = models.CharField(
        max_length=100,
        default="America/Lima",
        verbose_name="Zona horaria",
    )

    employee_profiles = models.ManyToManyField(
        "attendance.EmployeeProfile",
        blank=True,
        related_name="attendance_reports",
        verbose_name="Trabajadores",
    )

    work_locations = models.ManyToManyField(
        "attendance.WorkLocation",
        blank=True,
        related_name="attendance_reports",
        verbose_name="Ubicaciones",
    )

    work_schedules = models.ManyToManyField(
        "attendance.WorkSchedule",
        blank=True,
        related_name="attendance_reports",
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

    attendance_statuses = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Estados de asistencia",
    )

    incident_types = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Tipos de incidencia",
    )

    leave_types = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Tipos de permiso o licencia",
    )

    overtime_types = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Tipos de horas extras",
    )

    operational_session_types = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Tipos de sesión operativa",
    )

    filters = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Filtros adicionales",
    )

    selected_columns = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Columnas seleccionadas",
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

    include_archived = models.BooleanField(
        default=False,
        verbose_name="Incluir registros archivados",
    )

    include_details = models.BooleanField(
        default=True,
        verbose_name="Incluir detalle",
    )

    include_summary = models.BooleanField(
        default=True,
        verbose_name="Incluir resumen",
    )

    include_charts = models.BooleanField(
        default=False,
        verbose_name="Incluir gráficos",
    )

    include_incidents = models.BooleanField(
        default=True,
        verbose_name="Incluir incidencias",
    )

    include_justifications = models.BooleanField(
        default=True,
        verbose_name="Incluir justificaciones",
    )

    include_operational_time = models.BooleanField(
        default=True,
        verbose_name="Incluir tiempo operativo",
    )

    include_external_delays = models.BooleanField(
        default=True,
        verbose_name="Incluir demoras externas",
    )

    include_sensitive_data = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Incluir datos sensibles",
    )

    mask_sensitive_data = models.BooleanField(
        default=True,
        verbose_name="Ocultar parcialmente datos sensibles",
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
        related_name="attendance_reports_requested",
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

    processed_rows = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Filas procesadas",
    )

    total_rows = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Total de filas",
    )

    result_file = models.FileField(
        upload_to="attendance/reports/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Archivo generado",
    )

    result_file_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre del archivo",
    )

    result_file_size = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Tamaño del archivo",
    )

    result_mime_type = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Tipo MIME",
    )

    checksum = models.CharField(
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

    processing_error = models.TextField(
        blank=True,
        verbose_name="Error de procesamiento",
    )

    error_code = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Código de error",
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
        verbose_name="Archivo disponible hasta",
    )

    is_private = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Reporte privado",
    )

    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="attendance_reports_allowed",
        verbose_name="Usuarios autorizados",
    )

    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad de descargas",
    )

    first_downloaded_at = models.DateTimeField(
        null=True,
        blank=True,
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
        related_name="attendance_reports_last_downloaded",
        verbose_name="Última descarga por",
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
        related_name="attendance_reports_cancelled",
        verbose_name="Cancelado por",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
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
        related_name="attendance_reports_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_reports_updated",
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
        related_name="attendance_reports_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Reporte de asistencia"
        verbose_name_plural = "Reportes de asistencia"

        ordering = (
            "-created_at",
        )

        indexes = (
            models.Index(
                fields=(
                    "report_type",
                    "status",
                    "created_at",
                ),
                name="att_rep_type_status_idx",
            ),
            models.Index(
                fields=(
                    "requested_by",
                    "status",
                    "created_at",
                ),
                name="att_rep_user_status_idx",
            ),
            models.Index(
                fields=(
                    "start_date",
                    "end_date",
                    "report_type",
                ),
                name="att_rep_period_type_idx",
            ),
            models.Index(
                fields=(
                    "file_format",
                    "status",
                ),
                name="att_rep_format_status_idx",
            ),
            models.Index(
                fields=(
                    "generation_source",
                    "status",
                ),
                name="att_rep_source_status_idx",
            ),
            models.Index(
                fields=(
                    "processing_started_at",
                    "processing_finished_at",
                ),
                name="att_rep_processing_idx",
            ),
            models.Index(
                fields=(
                    "expires_at",
                    "status",
                ),
                name="att_rep_expire_status_idx",
            ),
            models.Index(
                fields=(
                    "next_retry_at",
                    "retry_count",
                    "status",
                ),
                name="att_rep_retry_status_idx",
            ),
            models.Index(
                fields=(
                    "include_sensitive_data",
                    "is_private",
                ),
                name="att_rep_sensitive_private_idx",
            ),
            models.Index(
                fields=(
                    "last_downloaded_by",
                    "last_downloaded_at",
                ),
                name="att_rep_download_idx",
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
                name="att_rep_progress_range",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    processed_rows__lte=models.F(
                        "total_rows"
                    ),
                ),
                name="att_rep_processed_lte_total",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    retry_count__lte=models.F(
                        "maximum_retries"
                    ),
                ),
                name="att_rep_retry_lte_max",
            ),
        )

    def __str__(self):
        return (
            f"{self.report_number} - "
            f"{self.name} - "
            f"{self.get_status_display()}"
        )

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_completed(self):
        return self.status in (
            self.Status.COMPLETED,
            self.Status.PARTIALLY_COMPLETED,
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
    def can_download(self):
        return (
            self.is_completed
            and bool(self.result_file)
            and not self.is_expired
            and self.archived_at is None
        )

    @property
    def period_days(self):
        if not self.start_date or not self.end_date:
            return 0

        return (
            self.end_date - self.start_date
        ).days + 1

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.end_date
            and self.start_date
            and self.end_date < self.start_date
        ):
            errors["end_date"] = (
                "La fecha final no puede ser anterior "
                "a la fecha inicial."
            )

        json_list_fields = (
            "company_names",
            "department_names",
            "job_titles",
            "attendance_statuses",
            "incident_types",
            "leave_types",
            "overtime_types",
            "operational_session_types",
            "selected_columns",
            "ordering_fields",
            "grouping_fields",
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
            "result_summary",
            "result_metadata",
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
            self.include_sensitive_data
            and not self.is_private
        ):
            errors["is_private"] = (
                "Un reporte con datos sensibles debe ser privado."
            )

        if (
            self.include_sensitive_data
            and self.mask_sensitive_data
            is False
            and not self.requested_by_id
        ):
            errors["requested_by"] = (
                "Debes identificar al usuario que solicitó "
                "datos sensibles sin ocultamiento."
            )

        if (
            self.status
            in (
                self.Status.PENDING,
                self.Status.QUEUED,
                self.Status.PROCESSING,
                self.Status.COMPLETED,
                self.Status.PARTIALLY_COMPLETED,
                self.Status.FAILED,
            )
            and not self.requested_at
        ):
            errors["requested_at"] = (
                "Un reporte solicitado debe tener "
                "fecha de solicitud."
            )

        if (
            self.status == self.Status.QUEUED
            and not self.queued_at
        ):
            errors["queued_at"] = (
                "Un reporte en cola debe registrar "
                "la fecha de encolado."
            )

        if (
            self.status == self.Status.PROCESSING
            and not self.processing_started_at
        ):
            errors["processing_started_at"] = (
                "Un reporte en procesamiento debe registrar "
                "la fecha de inicio."
            )

        if (
            self.is_completed
            and not self.processing_finished_at
        ):
            errors["processing_finished_at"] = (
                "Un reporte completado debe registrar "
                "la fecha de finalización."
            )

        if (
            self.is_completed
            and not self.result_file
        ):
            errors["result_file"] = (
                "Un reporte completado debe tener "
                "un archivo generado."
            )

        if (
            self.status == self.Status.FAILED
            and not self.processing_error.strip()
        ):
            errors["processing_error"] = (
                "Un reporte fallido debe registrar "
                "el error de procesamiento."
            )

        if self.processed_rows > self.total_rows:
            errors["processed_rows"] = (
                "Las filas procesadas no pueden superar "
                "el total de filas."
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
            self.expires_at
            and self.processing_finished_at
            and self.expires_at
            <= self.processing_finished_at
        ):
            errors["expires_at"] = (
                "El vencimiento debe ser posterior "
                "a la generación del reporte."
            )

        if (
            self.download_count > 0
            and not self.first_downloaded_at
        ):
            errors["first_downloaded_at"] = (
                "Debe existir una fecha de primera descarga."
            )

        if (
            self.last_downloaded_at
            and not self.last_downloaded_by_id
        ):
            errors["last_downloaded_by"] = (
                "Debes indicar quién realizó "
                "la última descarga."
            )

        if (
            self.status == self.Status.CANCELLED
            and not self.cancellation_reason.strip()
        ):
            errors["cancellation_reason"] = (
                "Debes indicar el motivo de cancelación."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.name = str(
            self.name or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        if self.is_expired and self.status in (
            self.Status.COMPLETED,
            self.Status.PARTIALLY_COMPLETED,
            self.Status.FAILED,
        ):
            self.status = self.Status.EXPIRED
            self.next_retry_at = None

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
                "Solo puedes presentar un reporte en borrador."
            )

        self.status = self.Status.PENDING
        self.requested_at = timezone.now()
        self.requested_by = user
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "requested_at",
                "requested_by",
                "updated_by",
                "updated_at",
            ]
        )

    def queue(
        self,
        user=None,
    ):
        if self.status not in (
            self.Status.PENDING,
            self.Status.FAILED,
        ):
            raise ValidationError(
                "El reporte no puede enviarse a cola "
                "desde su estado actual."
            )

        if self.is_expired:
            raise ValidationError(
                "El reporte se encuentra vencido."
            )

        self.status = self.Status.QUEUED
        self.queued_at = timezone.now()
        self.next_retry_at = None
        self.processing_error = ""
        self.error_code = ""
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "queued_at",
                "next_retry_at",
                "processing_error",
                "error_code",
                "updated_by",
                "updated_at",
            ]
        )

    def start_processing(
        self,
        total_rows=0,
        user=None,
    ):
        if self.status not in (
            self.Status.PENDING,
            self.Status.QUEUED,
        ):
            raise ValidationError(
                "El reporte no puede comenzar a procesarse."
            )

        if total_rows < 0:
            raise ValidationError(
                "El total de filas no puede ser negativo."
            )

        self.status = self.Status.PROCESSING
        self.processing_started_at = timezone.now()
        self.processing_finished_at = None
        self.progress_percentage = 0
        self.processed_rows = 0
        self.total_rows = total_rows
        self.processing_error = ""
        self.error_code = ""
        self.next_retry_at = None
        self.updated_by = user

        self.save()

    def update_progress(
        self,
        processed_rows,
        total_rows=None,
    ):
        if self.status != self.Status.PROCESSING:
            raise ValidationError(
                "Solo puedes actualizar el avance "
                "de un reporte en procesamiento."
            )

        if processed_rows < 0:
            raise ValidationError(
                "Las filas procesadas no pueden ser negativas."
            )

        if total_rows is not None:
            if total_rows < 0:
                raise ValidationError(
                    "El total de filas no puede ser negativo."
                )

            self.total_rows = total_rows

        if (
            self.total_rows > 0
            and processed_rows > self.total_rows
        ):
            raise ValidationError(
                "Las filas procesadas no pueden superar "
                "el total."
            )

        self.processed_rows = processed_rows

        if self.total_rows > 0:
            self.progress_percentage = min(
                100,
                round(
                    (
                        processed_rows
                        / self.total_rows
                    )
                    * 100,
                    2,
                ),
            )
        else:
            self.progress_percentage = 0

        self.save(
            update_fields=[
                "processed_rows",
                "total_rows",
                "progress_percentage",
                "updated_at",
            ]
        )

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
        partial=False,
        expires_at=None,
        user=None,
    ):
        if self.status != self.Status.PROCESSING:
            raise ValidationError(
                "Solo puedes completar un reporte "
                "que está procesándose."
            )

        if not result_file:
            raise ValidationError(
                "Debes indicar el archivo generado."
            )

        if not str(file_name or "").strip():
            raise ValidationError(
                "Debes indicar el nombre del archivo."
            )

        self.status = (
            self.Status.PARTIALLY_COMPLETED
            if partial
            else self.Status.COMPLETED
        )

        self.result_file = result_file
        self.result_file_name = str(
            file_name
        ).strip()
        self.result_file_size = max(
            0,
            file_size,
        )
        self.result_mime_type = str(
            mime_type or ""
        ).strip()
        self.checksum = str(
            checksum or ""
        ).strip()
        self.result_summary = summary or {}
        self.result_metadata = metadata or {}
        self.processing_finished_at = timezone.now()
        self.progress_percentage = 100

        if self.total_rows > 0:
            self.processed_rows = self.total_rows

        self.expires_at = expires_at
        self.processing_error = ""
        self.error_code = ""
        self.next_retry_at = None
        self.updated_by = user

        self.save()

    def mark_failed(
        self,
        *,
        error,
        error_code="",
        next_retry_at=None,
        user=None,
    ):
        error = str(
            error or ""
        ).strip()

        if not error:
            raise ValidationError(
                "Debes indicar el error de procesamiento."
            )

        if self.status not in (
            self.Status.PENDING,
            self.Status.QUEUED,
            self.Status.PROCESSING,
        ):
            raise ValidationError(
                "El reporte no puede marcarse como fallido "
                "desde su estado actual."
            )

        self.status = self.Status.FAILED
        self.processing_error = error
        self.error_code = str(
            error_code or ""
        ).strip()
        self.processing_finished_at = timezone.now()
        self.next_retry_at = next_retry_at
        self.updated_by = user

        self.save()

    def prepare_retry(
        self,
        next_retry_at=None,
        user=None,
    ):
        if not self.can_retry:
            raise ValidationError(
                "El reporte no admite otro reintento."
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
            self.Status.QUEUED
            if next_retry_at is None
            else self.Status.PENDING
        )
        self.next_retry_at = next_retry_at
        self.processing_started_at = None
        self.processing_finished_at = None
        self.processing_error = ""
        self.error_code = ""
        self.progress_percentage = 0
        self.processed_rows = 0
        self.updated_by = user

        self.save()

    def register_download(
        self,
        user,
    ):
        if not self.can_download:
            raise ValidationError(
                "El reporte no está disponible para descarga."
            )

        if (
            self.is_private
            and user != self.requested_by
            and user != self.created_by
            and not self.allowed_users.filter(
                pk=user.pk
            ).exists()
        ):
            raise ValidationError(
                "El usuario no tiene permiso "
                "para descargar este reporte."
            )

        now = timezone.now()

        if not self.first_downloaded_at:
            self.first_downloaded_at = now

        self.last_downloaded_at = now
        self.last_downloaded_by = user
        self.download_count += 1

        self.save(
            update_fields=[
                "first_downloaded_at",
                "last_downloaded_at",
                "last_downloaded_by",
                "download_count",
                "updated_at",
            ]
        )

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
            self.Status.COMPLETED,
            self.Status.PARTIALLY_COMPLETED,
            self.Status.CANCELLED,
            self.Status.EXPIRED,
        ):
            raise ValidationError(
                "El reporte ya no puede cancelarse."
            )

        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancelled_by = user
        self.cancellation_reason = reason
        self.next_retry_at = None
        self.updated_by = user

        self.save()

    def mark_expired(
        self,
        user=None,
    ):
        if not self.is_expired:
            raise ValidationError(
                "El reporte todavía no ha vencido."
            )

        if self.status in (
            self.Status.CANCELLED,
            self.Status.EXPIRED,
        ):
            raise ValidationError(
                "El reporte ya no puede marcarse como vencido."
            )

        self.status = self.Status.EXPIRED
        self.next_retry_at = None
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "next_retry_at",
                "updated_by",
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

        if self.status in (
            self.Status.QUEUED,
            self.Status.PROCESSING,
        ):
            raise ValidationError(
                "No puedes archivar un reporte "
                "que está en cola o procesándose."
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