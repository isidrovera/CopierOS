# -*- coding: utf-8 -*-

import uuid
from calendar import monthrange
from datetime import date, datetime, time, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .attendance_report import AttendanceReport


class AttendanceReportSchedule(models.Model):
    """
    Programación automática de reportes de asistencia.

    Permite generar reportes:

    - Diariamente.
    - Semanalmente.
    - Mensualmente.
    - Trimestralmente.
    - Anualmente.
    - Mediante una expresión cron controlada.
    - En una fecha única.

    Conserva:

    - Tipo de reporte.
    - Formato.
    - Periodo que debe consultar.
    - Filtros.
    - Destinatarios.
    - Próxima ejecución.
    - Última ejecución.
    - Reporte generado.
    - Errores.
    - Reintentos.
    - Historial básico de activación y suspensión.

    La creación física del archivo y el envío a los destinatarios
    debe ejecutarse desde servicios o tareas automáticas.
    """

    class Frequency(models.TextChoices):
        ONCE = (
            "once",
            "Una sola vez",
        )
        DAILY = (
            "daily",
            "Diario",
        )
        WEEKLY = (
            "weekly",
            "Semanal",
        )
        MONTHLY = (
            "monthly",
            "Mensual",
        )
        QUARTERLY = (
            "quarterly",
            "Trimestral",
        )
        YEARLY = (
            "yearly",
            "Anual",
        )
        CUSTOM_CRON = (
            "custom_cron",
            "Expresión cron",
        )

    class PeriodMode(models.TextChoices):
        CURRENT_DAY = (
            "current_day",
            "Día actual",
        )
        PREVIOUS_DAY = (
            "previous_day",
            "Día anterior",
        )
        CURRENT_WEEK = (
            "current_week",
            "Semana actual",
        )
        PREVIOUS_WEEK = (
            "previous_week",
            "Semana anterior",
        )
        LAST_SEVEN_DAYS = (
            "last_seven_days",
            "Últimos siete días",
        )
        CURRENT_MONTH = (
            "current_month",
            "Mes actual",
        )
        PREVIOUS_MONTH = (
            "previous_month",
            "Mes anterior",
        )
        LAST_THIRTY_DAYS = (
            "last_thirty_days",
            "Últimos treinta días",
        )
        CURRENT_QUARTER = (
            "current_quarter",
            "Trimestre actual",
        )
        PREVIOUS_QUARTER = (
            "previous_quarter",
            "Trimestre anterior",
        )
        CURRENT_YEAR = (
            "current_year",
            "Año actual",
        )
        PREVIOUS_YEAR = (
            "previous_year",
            "Año anterior",
        )
        CUSTOM_OFFSET = (
            "custom_offset",
            "Desplazamiento personalizado",
        )
        FIXED_RANGE = (
            "fixed_range",
            "Rango fijo",
        )

    class Weekday(models.IntegerChoices):
        MONDAY = (
            0,
            "Lunes",
        )
        TUESDAY = (
            1,
            "Martes",
        )
        WEDNESDAY = (
            2,
            "Miércoles",
        )
        THURSDAY = (
            3,
            "Jueves",
        )
        FRIDAY = (
            4,
            "Viernes",
        )
        SATURDAY = (
            5,
            "Sábado",
        )
        SUNDAY = (
            6,
            "Domingo",
        )

    class Status(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        ACTIVE = (
            "active",
            "Activa",
        )
        PAUSED = (
            "paused",
            "Pausada",
        )
        RUNNING = (
            "running",
            "Ejecutándose",
        )
        COMPLETED = (
            "completed",
            "Completada",
        )
        ERROR = (
            "error",
            "Con error",
        )
        DISABLED = (
            "disabled",
            "Deshabilitada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )

    class DeliveryMode(models.TextChoices):
        INTERNAL = (
            "internal",
            "Notificación interna",
        )
        EMAIL = (
            "email",
            "Correo electrónico",
        )
        INTERNAL_AND_EMAIL = (
            "internal_and_email",
            "Interna y correo",
        )
        DOWNLOAD_ONLY = (
            "download_only",
            "Solo descarga",
        )
        NONE = (
            "none",
            "Sin entrega automática",
        )

    class FailureAction(models.TextChoices):
        RETRY = (
            "retry",
            "Reintentar",
        )
        PAUSE = (
            "pause",
            "Pausar programación",
        )
        DISABLE = (
            "disable",
            "Deshabilitar programación",
        )
        NOTIFY_ONLY = (
            "notify_only",
            "Solo notificar",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código",
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

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.MONTHLY,
        db_index=True,
        verbose_name="Frecuencia",
    )

    report_type = models.CharField(
        max_length=50,
        choices=AttendanceReport.ReportType.choices,
        db_index=True,
        verbose_name="Tipo de reporte",
    )

    file_format = models.CharField(
        max_length=10,
        choices=AttendanceReport.FileFormat.choices,
        default=AttendanceReport.FileFormat.XLSX,
        db_index=True,
        verbose_name="Formato",
    )

    period_mode = models.CharField(
        max_length=30,
        choices=PeriodMode.choices,
        default=PeriodMode.PREVIOUS_MONTH,
        db_index=True,
        verbose_name="Periodo del reporte",
    )

    timezone_name = models.CharField(
        max_length=100,
        default="America/Lima",
        verbose_name="Zona horaria",
    )

    execution_time = models.TimeField(
        default=time(
            hour=8,
            minute=0,
        ),
        verbose_name="Hora de ejecución",
    )

    weekday = models.PositiveSmallIntegerField(
        choices=Weekday.choices,
        null=True,
        blank=True,
        verbose_name="Día de la semana",
    )

    month_day = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Día del mes",
        help_text=(
            "Valor entre 1 y 31. Si el mes tiene menos días, "
            "se utilizará el último día disponible."
        ),
    )

    year_month = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Mes del año",
        help_text="Valor entre 1 y 12.",
    )

    one_time_execution_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Ejecución única",
    )

    cron_expression = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Expresión cron",
        help_text=(
            "Debe ser validada por el servicio de programación "
            "antes de activar la tarea."
        ),
    )

    custom_period_start_offset_days = models.IntegerField(
        default=0,
        verbose_name="Desplazamiento inicial en días",
        help_text=(
            "Cantidad de días respecto de la fecha de ejecución. "
            "Puede ser negativa."
        ),
    )

    custom_period_end_offset_days = models.IntegerField(
        default=0,
        verbose_name="Desplazamiento final en días",
        help_text=(
            "Cantidad de días respecto de la fecha de ejecución. "
            "Puede ser negativa."
        ),
    )

    fixed_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha fija inicial",
    )

    fixed_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha fija final",
    )

    employee_profiles = models.ManyToManyField(
        "attendance.EmployeeProfile",
        blank=True,
        related_name="attendance_report_schedules",
        verbose_name="Trabajadores",
    )

    work_locations = models.ManyToManyField(
        "attendance.WorkLocation",
        blank=True,
        related_name="attendance_report_schedules",
        verbose_name="Ubicaciones",
    )

    work_schedules = models.ManyToManyField(
        "attendance.WorkSchedule",
        blank=True,
        related_name="attendance_report_schedules",
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

    delivery_mode = models.CharField(
        max_length=30,
        choices=DeliveryMode.choices,
        default=DeliveryMode.INTERNAL_AND_EMAIL,
        db_index=True,
        verbose_name="Modo de entrega",
    )

    recipient_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="attendance_report_schedule_recipients",
        verbose_name="Usuarios destinatarios",
    )

    recipient_emails = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Correos adicionales",
    )

    email_subject = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Asunto del correo",
    )

    email_message = models.TextField(
        blank=True,
        verbose_name="Mensaje del correo",
    )

    notify_on_success = models.BooleanField(
        default=True,
        verbose_name="Notificar generación correcta",
    )

    notify_on_failure = models.BooleanField(
        default=True,
        verbose_name="Notificar error de generación",
    )

    failure_action = models.CharField(
        max_length=20,
        choices=FailureAction.choices,
        default=FailureAction.RETRY,
        verbose_name="Acción ante error",
    )

    maximum_retries = models.PositiveSmallIntegerField(
        default=3,
        verbose_name="Máximo de reintentos",
    )

    retry_delay_minutes = models.PositiveIntegerField(
        default=30,
        verbose_name="Minutos entre reintentos",
    )

    consecutive_failure_count = models.PositiveSmallIntegerField(
        default=0,
        db_index=True,
        verbose_name="Errores consecutivos",
    )

    total_execution_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Ejecuciones totales",
    )

    successful_execution_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Ejecuciones correctas",
    )

    failed_execution_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Ejecuciones fallidas",
    )

    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Activada el",
    )

    activated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_report_schedules_activated",
        verbose_name="Activada por",
    )

    paused_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Pausada el",
    )

    paused_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_report_schedules_paused",
        verbose_name="Pausada por",
    )

    pause_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de pausa",
    )

    resumed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Reanudada el",
    )

    resumed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_report_schedules_resumed",
        verbose_name="Reanudada por",
    )

    next_execution_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Próxima ejecución",
    )

    last_execution_started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Última ejecución iniciada",
    )

    last_execution_finished_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Última ejecución finalizada",
    )

    last_success_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Última ejecución correcta",
    )

    last_failure_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Último error",
    )

    last_error = models.TextField(
        blank=True,
        verbose_name="Último mensaje de error",
    )

    last_report = models.ForeignKey(
        AttendanceReport,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="schedule_last_report_for",
        verbose_name="Último reporte generado",
    )

    current_report = models.ForeignKey(
        AttendanceReport,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="schedule_current_report_for",
        verbose_name="Reporte en ejecución",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Completada el",
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
        related_name="attendance_report_schedules_cancelled",
        verbose_name="Cancelada por",
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
        related_name="attendance_report_schedules_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_report_schedules_updated",
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
        related_name="attendance_report_schedules_archived",
        verbose_name="Archivada por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Programación de reporte de asistencia"
        verbose_name_plural = (
            "Programaciones de reportes de asistencia"
        )

        ordering = (
            "next_execution_at",
            "name",
        )

        indexes = (
            models.Index(
                fields=(
                    "status",
                    "next_execution_at",
                ),
                name="att_rsch_status_next_idx",
            ),
            models.Index(
                fields=(
                    "frequency",
                    "status",
                ),
                name="att_rsch_freq_status_idx",
            ),
            models.Index(
                fields=(
                    "report_type",
                    "file_format",
                ),
                name="att_rsch_type_format_idx",
            ),
            models.Index(
                fields=(
                    "period_mode",
                    "frequency",
                ),
                name="att_rsch_period_freq_idx",
            ),
            models.Index(
                fields=(
                    "last_execution_started_at",
                    "last_execution_finished_at",
                ),
                name="att_rsch_last_execution_idx",
            ),
            models.Index(
                fields=(
                    "consecutive_failure_count",
                    "status",
                ),
                name="att_rsch_failure_status_idx",
            ),
            models.Index(
                fields=(
                    "delivery_mode",
                    "notify_on_failure",
                ),
                name="att_rsch_delivery_notify_idx",
            ),
            models.Index(
                fields=(
                    "include_sensitive_data",
                    "status",
                ),
                name="att_rsch_sensitive_idx",
            ),
            models.Index(
                fields=(
                    "activated_at",
                    "paused_at",
                    "resumed_at",
                ),
                name="att_rsch_lifecycle_idx",
            ),
        )

        constraints = (
            models.CheckConstraint(
                condition=(
                    models.Q(
                        weekday__isnull=True,
                    )
                    | (
                        models.Q(
                            weekday__gte=0,
                        )
                        & models.Q(
                            weekday__lte=6,
                        )
                    )
                ),
                name="att_rsch_weekday_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        month_day__isnull=True,
                    )
                    | (
                        models.Q(
                            month_day__gte=1,
                        )
                        & models.Q(
                            month_day__lte=31,
                        )
                    )
                ),
                name="att_rsch_month_day_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        year_month__isnull=True,
                    )
                    | (
                        models.Q(
                            year_month__gte=1,
                        )
                        & models.Q(
                            year_month__lte=12,
                        )
                    )
                ),
                name="att_rsch_year_month_range",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    successful_execution_count__lte=models.F(
                        "total_execution_count"
                    ),
                ),
                name="att_rsch_success_lte_total",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    failed_execution_count__lte=models.F(
                        "total_execution_count"
                    ),
                ),
                name="att_rsch_failed_lte_total",
            ),
        )

    def __str__(self):
        return (
            f"{self.code} - "
            f"{self.name} - "
            f"{self.get_status_display()}"
        )

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_active(self):
        return (
            self.status == self.Status.ACTIVE
            and self.archived_at is None
        )

    @property
    def is_due(self):
        return (
            self.is_active
            and self.next_execution_at is not None
            and self.next_execution_at <= timezone.now()
        )

    @property
    def success_percentage(self):
        if self.total_execution_count <= 0:
            return 0

        return round(
            (
                self.successful_execution_count
                / self.total_execution_count
            )
            * 100,
            2,
        )

    def get_period_range(
        self,
        reference_datetime=None,
    ):
        """
        Calcula el rango que utilizará el reporte.

        El valor de referencia debe corresponder al momento
        de ejecución de la programación.
        """

        reference_datetime = (
            reference_datetime
            or timezone.now()
        )

        local_reference = timezone.localtime(
            reference_datetime
        )

        reference_date = local_reference.date()

        if self.period_mode == self.PeriodMode.CURRENT_DAY:
            return (
                reference_date,
                reference_date,
            )

        if self.period_mode == self.PeriodMode.PREVIOUS_DAY:
            previous_day = (
                reference_date
                - timedelta(days=1)
            )

            return (
                previous_day,
                previous_day,
            )

        if self.period_mode == self.PeriodMode.CURRENT_WEEK:
            start_date = (
                reference_date
                - timedelta(
                    days=reference_date.weekday(),
                )
            )

            end_date = (
                start_date
                + timedelta(days=6)
            )

            return (
                start_date,
                end_date,
            )

        if self.period_mode == self.PeriodMode.PREVIOUS_WEEK:
            current_week_start = (
                reference_date
                - timedelta(
                    days=reference_date.weekday(),
                )
            )

            end_date = (
                current_week_start
                - timedelta(days=1)
            )

            start_date = (
                end_date
                - timedelta(days=6)
            )

            return (
                start_date,
                end_date,
            )

        if self.period_mode == self.PeriodMode.LAST_SEVEN_DAYS:
            return (
                reference_date - timedelta(days=6),
                reference_date,
            )

        if self.period_mode == self.PeriodMode.CURRENT_MONTH:
            start_date = reference_date.replace(
                day=1,
            )

            last_day = monthrange(
                reference_date.year,
                reference_date.month,
            )[1]

            end_date = reference_date.replace(
                day=last_day,
            )

            return (
                start_date,
                end_date,
            )

        if self.period_mode == self.PeriodMode.PREVIOUS_MONTH:
            current_month_start = reference_date.replace(
                day=1,
            )

            end_date = (
                current_month_start
                - timedelta(days=1)
            )

            start_date = end_date.replace(
                day=1,
            )

            return (
                start_date,
                end_date,
            )

        if self.period_mode == self.PeriodMode.LAST_THIRTY_DAYS:
            return (
                reference_date - timedelta(days=29),
                reference_date,
            )

        if self.period_mode == self.PeriodMode.CURRENT_QUARTER:
            quarter_start_month = (
                (
                    reference_date.month - 1
                )
                // 3
            ) * 3 + 1

            start_date = date(
                reference_date.year,
                quarter_start_month,
                1,
            )

            quarter_end_month = (
                quarter_start_month + 2
            )

            end_date = date(
                reference_date.year,
                quarter_end_month,
                monthrange(
                    reference_date.year,
                    quarter_end_month,
                )[1],
            )

            return (
                start_date,
                end_date,
            )

        if self.period_mode == self.PeriodMode.PREVIOUS_QUARTER:
            current_quarter_start_month = (
                (
                    reference_date.month - 1
                )
                // 3
            ) * 3 + 1

            current_quarter_start = date(
                reference_date.year,
                current_quarter_start_month,
                1,
            )

            end_date = (
                current_quarter_start
                - timedelta(days=1)
            )

            previous_quarter_start_month = (
                (
                    end_date.month - 1
                )
                // 3
            ) * 3 + 1

            start_date = date(
                end_date.year,
                previous_quarter_start_month,
                1,
            )

            return (
                start_date,
                end_date,
            )

        if self.period_mode == self.PeriodMode.CURRENT_YEAR:
            return (
                date(
                    reference_date.year,
                    1,
                    1,
                ),
                date(
                    reference_date.year,
                    12,
                    31,
                ),
            )

        if self.period_mode == self.PeriodMode.PREVIOUS_YEAR:
            previous_year = reference_date.year - 1

            return (
                date(
                    previous_year,
                    1,
                    1,
                ),
                date(
                    previous_year,
                    12,
                    31,
                ),
            )

        if self.period_mode == self.PeriodMode.CUSTOM_OFFSET:
            start_date = (
                reference_date
                + timedelta(
                    days=self.custom_period_start_offset_days,
                )
            )

            end_date = (
                reference_date
                + timedelta(
                    days=self.custom_period_end_offset_days,
                )
            )

            return (
                start_date,
                end_date,
            )

        if self.period_mode == self.PeriodMode.FIXED_RANGE:
            return (
                self.fixed_start_date,
                self.fixed_end_date,
            )

        raise ValidationError(
            "No se pudo determinar el periodo del reporte."
        )

    def calculate_next_execution(
        self,
        reference_datetime=None,
    ):
        """
        Calcula la próxima ejecución para frecuencias estándar.

        Las expresiones cron deben resolverse mediante el servicio
        de tareas, porque requieren un analizador cron específico.
        """

        reference_datetime = (
            reference_datetime
            or timezone.now()
        )

        local_reference = timezone.localtime(
            reference_datetime
        )

        current_date = local_reference.date()

        def make_aware_datetime(target_date):
            naive_datetime = datetime.combine(
                target_date,
                self.execution_time,
            )

            return timezone.make_aware(
                naive_datetime,
                timezone.get_current_timezone(),
            )

        if self.frequency == self.Frequency.ONCE:
            return self.one_time_execution_at

        if self.frequency == self.Frequency.CUSTOM_CRON:
            return None

        if self.frequency == self.Frequency.DAILY:
            candidate = make_aware_datetime(
                current_date
            )

            if candidate <= reference_datetime:
                candidate = make_aware_datetime(
                    current_date
                    + timedelta(days=1)
                )

            return candidate

        if self.frequency == self.Frequency.WEEKLY:
            target_weekday = self.weekday

            days_ahead = (
                target_weekday
                - current_date.weekday()
            ) % 7

            candidate_date = (
                current_date
                + timedelta(days=days_ahead)
            )

            candidate = make_aware_datetime(
                candidate_date
            )

            if candidate <= reference_datetime:
                candidate = make_aware_datetime(
                    candidate_date
                    + timedelta(days=7)
                )

            return candidate

        if self.frequency == self.Frequency.MONTHLY:
            year = current_date.year
            month = current_date.month

            target_day = min(
                self.month_day,
                monthrange(
                    year,
                    month,
                )[1],
            )

            candidate_date = date(
                year,
                month,
                target_day,
            )

            candidate = make_aware_datetime(
                candidate_date
            )

            if candidate <= reference_datetime:
                if month == 12:
                    year += 1
                    month = 1
                else:
                    month += 1

                target_day = min(
                    self.month_day,
                    monthrange(
                        year,
                        month,
                    )[1],
                )

                candidate = make_aware_datetime(
                    date(
                        year,
                        month,
                        target_day,
                    )
                )

            return candidate

        if self.frequency == self.Frequency.QUARTERLY:
            quarter_start_month = (
                (
                    current_date.month - 1
                )
                // 3
            ) * 3 + 1

            target_month = (
                quarter_start_month + 2
            )

            target_day = min(
                self.month_day,
                monthrange(
                    current_date.year,
                    target_month,
                )[1],
            )

            candidate = make_aware_datetime(
                date(
                    current_date.year,
                    target_month,
                    target_day,
                )
            )

            if candidate <= reference_datetime:
                target_month += 3
                target_year = current_date.year

                if target_month > 12:
                    target_month -= 12
                    target_year += 1

                target_day = min(
                    self.month_day,
                    monthrange(
                        target_year,
                        target_month,
                    )[1],
                )

                candidate = make_aware_datetime(
                    date(
                        target_year,
                        target_month,
                        target_day,
                    )
                )

            return candidate

        if self.frequency == self.Frequency.YEARLY:
            target_year = current_date.year

            target_day = min(
                self.month_day,
                monthrange(
                    target_year,
                    self.year_month,
                )[1],
            )

            candidate = make_aware_datetime(
                date(
                    target_year,
                    self.year_month,
                    target_day,
                )
            )

            if candidate <= reference_datetime:
                target_year += 1

                target_day = min(
                    self.month_day,
                    monthrange(
                        target_year,
                        self.year_month,
                    )[1],
                )

                candidate = make_aware_datetime(
                    date(
                        target_year,
                        self.year_month,
                        target_day,
                    )
                )

            return candidate

        return None

    def clean(self):
        super().clean()

        errors = {}

        if not self.name.strip():
            errors["name"] = (
                "Debes indicar el nombre de la programación."
            )

        if self.frequency == self.Frequency.ONCE:
            if not self.one_time_execution_at:
                errors["one_time_execution_at"] = (
                    "Debes indicar la fecha y hora "
                    "de ejecución única."
                )

        elif self.one_time_execution_at:
            errors["one_time_execution_at"] = (
                "La fecha única solo corresponde "
                "a una programación de una sola ejecución."
            )

        if self.frequency == self.Frequency.WEEKLY:
            if self.weekday is None:
                errors["weekday"] = (
                    "Debes indicar el día de la semana."
                )

        elif self.weekday is not None:
            errors["weekday"] = (
                "El día de la semana solo corresponde "
                "a una programación semanal."
            )

        if self.frequency in (
            self.Frequency.MONTHLY,
            self.Frequency.QUARTERLY,
            self.Frequency.YEARLY,
        ):
            if self.month_day is None:
                errors["month_day"] = (
                    "Debes indicar el día del mes."
                )

        elif self.month_day is not None:
            errors["month_day"] = (
                "El día del mes no corresponde "
                "a esta frecuencia."
            )

        if self.frequency == self.Frequency.YEARLY:
            if self.year_month is None:
                errors["year_month"] = (
                    "Debes indicar el mes del año."
                )

        elif self.year_month is not None:
            errors["year_month"] = (
                "El mes del año solo corresponde "
                "a una programación anual."
            )

        if self.frequency == self.Frequency.CUSTOM_CRON:
            if not self.cron_expression.strip():
                errors["cron_expression"] = (
                    "Debes indicar la expresión cron."
                )

        elif self.cron_expression.strip():
            errors["cron_expression"] = (
                "La expresión cron solo corresponde "
                "a una frecuencia personalizada."
            )

        if self.period_mode == self.PeriodMode.FIXED_RANGE:
            if not self.fixed_start_date:
                errors["fixed_start_date"] = (
                    "Debes indicar la fecha fija inicial."
                )

            if not self.fixed_end_date:
                errors["fixed_end_date"] = (
                    "Debes indicar la fecha fija final."
                )

            if (
                self.fixed_start_date
                and self.fixed_end_date
                and self.fixed_end_date
                < self.fixed_start_date
            ):
                errors["fixed_end_date"] = (
                    "La fecha final no puede ser anterior "
                    "a la fecha inicial."
                )

        elif self.fixed_start_date or self.fixed_end_date:
            errors["fixed_start_date"] = (
                "Las fechas fijas solo corresponden "
                "al modo de rango fijo."
            )

        if (
            self.period_mode
            == self.PeriodMode.CUSTOM_OFFSET
            and self.custom_period_end_offset_days
            < self.custom_period_start_offset_days
        ):
            errors["custom_period_end_offset_days"] = (
                "El desplazamiento final no puede ser menor "
                "que el desplazamiento inicial."
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
            "recipient_emails",
        )

        for field_name in json_list_fields:
            if not isinstance(
                getattr(
                    self,
                    field_name,
                ),
                list,
            ):
                errors[field_name] = (
                    "El valor debe ser una lista JSON."
                )

        if not isinstance(
            self.filters,
            dict,
        ):
            errors["filters"] = (
                "Los filtros deben ser un objeto JSON."
            )

        if (
            self.include_sensitive_data
            and not self.mask_sensitive_data
            and self.delivery_mode
            in (
                self.DeliveryMode.EMAIL,
                self.DeliveryMode.INTERNAL_AND_EMAIL,
            )
        ):
            errors["mask_sensitive_data"] = (
                "Los reportes enviados por correo deben ocultar "
                "los datos sensibles."
            )

        if self.delivery_mode in (
            self.DeliveryMode.EMAIL,
            self.DeliveryMode.INTERNAL_AND_EMAIL,
        ):
            has_email_recipients = bool(
                self.recipient_emails
            )

            has_user_recipients = (
                self.pk
                and self.recipient_users.exists()
            )

            if not has_email_recipients and not has_user_recipients:
                errors["recipient_emails"] = (
                    "Debes registrar al menos un destinatario "
                    "para el envío por correo."
                )

        if (
            self.failure_action
            == self.FailureAction.RETRY
            and self.maximum_retries <= 0
        ):
            errors["maximum_retries"] = (
                "Debes permitir al menos un reintento."
            )

        if (
            self.maximum_retries > 0
            and self.retry_delay_minutes <= 0
        ):
            errors["retry_delay_minutes"] = (
                "El tiempo entre reintentos debe ser "
                "mayor a cero."
            )

        if (
            self.successful_execution_count
            > self.total_execution_count
        ):
            errors["successful_execution_count"] = (
                "Las ejecuciones correctas no pueden superar "
                "el total de ejecuciones."
            )

        if (
            self.failed_execution_count
            > self.total_execution_count
        ):
            errors["failed_execution_count"] = (
                "Las ejecuciones fallidas no pueden superar "
                "el total de ejecuciones."
            )

        if (
            self.status == self.Status.ACTIVE
            and not self.activated_at
        ):
            errors["activated_at"] = (
                "Una programación activa debe registrar "
                "la fecha de activación."
            )

        if (
            self.status == self.Status.ACTIVE
            and not self.next_execution_at
            and self.frequency
            != self.Frequency.CUSTOM_CRON
        ):
            errors["next_execution_at"] = (
                "Una programación activa debe tener "
                "una próxima ejecución."
            )

        if (
            self.status == self.Status.PAUSED
            and not self.paused_at
        ):
            errors["paused_at"] = (
                "Una programación pausada debe registrar "
                "la fecha de pausa."
            )

        if (
            self.status == self.Status.PAUSED
            and not self.pause_reason.strip()
        ):
            errors["pause_reason"] = (
                "Debes indicar el motivo de pausa."
            )

        if (
            self.status == self.Status.RUNNING
            and not self.last_execution_started_at
        ):
            errors["last_execution_started_at"] = (
                "Una programación en ejecución debe registrar "
                "el inicio de la ejecución."
            )

        if (
            self.status == self.Status.RUNNING
            and not self.current_report_id
        ):
            errors["current_report"] = (
                "Una programación en ejecución debe estar "
                "vinculada con el reporte actual."
            )

        if (
            self.status == self.Status.ERROR
            and not self.last_error.strip()
        ):
            errors["last_error"] = (
                "Una programación con error debe registrar "
                "el detalle del problema."
            )

        if (
            self.status == self.Status.COMPLETED
            and not self.completed_at
        ):
            errors["completed_at"] = (
                "Una programación completada debe registrar "
                "la fecha de finalización."
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
        self.code = str(
            self.code or ""
        ).strip().upper()

        self.name = str(
            self.name or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        self.cron_expression = str(
            self.cron_expression or ""
        ).strip()

        if (
            self.status == self.Status.ACTIVE
            and not self.next_execution_at
            and self.frequency
            != self.Frequency.CUSTOM_CRON
        ):
            self.next_execution_at = (
                self.calculate_next_execution()
            )

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def activate(
        self,
        user=None,
    ):
        if self.status not in (
            self.Status.DRAFT,
            self.Status.PAUSED,
            self.Status.ERROR,
            self.Status.DISABLED,
        ):
            raise ValidationError(
                "La programación no puede activarse "
                "desde su estado actual."
            )

        if (
            self.frequency == self.Frequency.ONCE
            and self.one_time_execution_at
            and self.one_time_execution_at <= timezone.now()
        ):
            raise ValidationError(
                "La fecha de ejecución única ya venció."
            )

        now = timezone.now()

        self.status = self.Status.ACTIVE
        self.activated_at = (
            self.activated_at
            or now
        )
        self.activated_by = (
            self.activated_by
            or user
        )
        self.resumed_at = now
        self.resumed_by = user
        self.paused_at = None
        self.paused_by = None
        self.pause_reason = ""
        self.last_error = ""
        self.updated_by = user

        if self.frequency != self.Frequency.CUSTOM_CRON:
            self.next_execution_at = (
                self.calculate_next_execution(
                    reference_datetime=now,
                )
            )

        self.save()

    def pause(
        self,
        user,
        reason,
    ):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de pausa."
            )

        if self.status not in (
            self.Status.ACTIVE,
            self.Status.ERROR,
        ):
            raise ValidationError(
                "Solo puedes pausar una programación "
                "activa o con error."
            )

        self.status = self.Status.PAUSED
        self.paused_at = timezone.now()
        self.paused_by = user
        self.pause_reason = reason
        self.next_execution_at = None
        self.updated_by = user

        self.save()

    def resume(
        self,
        user=None,
    ):
        if self.status != self.Status.PAUSED:
            raise ValidationError(
                "Solo puedes reanudar una programación pausada."
            )

        self.activate(
            user=user,
        )

    def disable(
        self,
        user=None,
        reason="",
    ):
        if self.status == self.Status.RUNNING:
            raise ValidationError(
                "No puedes deshabilitar una programación "
                "que está ejecutándose."
            )

        self.status = self.Status.DISABLED
        self.next_execution_at = None

        if reason:
            self.notes = str(
                reason
            ).strip()

        self.updated_by = user

        self.save()

    def start_execution(
        self,
        report,
        user=None,
    ):
        if self.status != self.Status.ACTIVE:
            raise ValidationError(
                "Solo una programación activa puede ejecutarse."
            )

        if self.current_report_id:
            raise ValidationError(
                "La programación ya tiene un reporte "
                "en ejecución."
            )

        if not report:
            raise ValidationError(
                "Debes indicar el reporte que será generado."
            )

        self.status = self.Status.RUNNING
        self.current_report = report
        self.last_execution_started_at = timezone.now()
        self.last_execution_finished_at = None
        self.last_error = ""
        self.updated_by = user

        self.save()

    def mark_execution_success(
        self,
        report,
        user=None,
    ):
        if self.status != self.Status.RUNNING:
            raise ValidationError(
                "La programación no está ejecutándose."
            )

        if (
            self.current_report_id
            and report.pk != self.current_report_id
        ):
            raise ValidationError(
                "El reporte no corresponde "
                "a la ejecución actual."
            )

        now = timezone.now()

        self.total_execution_count += 1
        self.successful_execution_count += 1
        self.consecutive_failure_count = 0

        self.last_report = report
        self.current_report = None
        self.last_execution_finished_at = now
        self.last_success_at = now
        self.last_error = ""
        self.updated_by = user

        if self.frequency == self.Frequency.ONCE:
            self.status = self.Status.COMPLETED
            self.completed_at = now
            self.next_execution_at = None

        else:
            self.status = self.Status.ACTIVE

            if self.frequency != self.Frequency.CUSTOM_CRON:
                self.next_execution_at = (
                    self.calculate_next_execution(
                        reference_datetime=now,
                    )
                )

        self.save()

    def mark_execution_failure(
        self,
        error,
        report=None,
        user=None,
    ):
        error = str(
            error or ""
        ).strip()

        if not error:
            raise ValidationError(
                "Debes indicar el error de ejecución."
            )

        if self.status != self.Status.RUNNING:
            raise ValidationError(
                "La programación no está ejecutándose."
            )

        now = timezone.now()

        self.total_execution_count += 1
        self.failed_execution_count += 1
        self.consecutive_failure_count += 1

        if report:
            self.last_report = report

        self.current_report = None
        self.last_execution_finished_at = now
        self.last_failure_at = now
        self.last_error = error
        self.updated_by = user

        if self.failure_action == self.FailureAction.PAUSE:
            self.status = self.Status.PAUSED
            self.paused_at = now
            self.paused_by = user
            self.pause_reason = error
            self.next_execution_at = None

        elif self.failure_action == self.FailureAction.DISABLE:
            self.status = self.Status.DISABLED
            self.next_execution_at = None

        elif (
            self.failure_action == self.FailureAction.RETRY
            and self.consecutive_failure_count
            <= self.maximum_retries
        ):
            self.status = self.Status.ACTIVE
            self.next_execution_at = (
                now
                + timedelta(
                    minutes=self.retry_delay_minutes,
                )
            )

        else:
            self.status = self.Status.ERROR
            self.next_execution_at = None

        self.save()

    def create_report(
        self,
        report_number,
        user=None,
        reference_datetime=None,
    ):
        """
        Crea el registro del reporte que luego será procesado.

        No genera el archivo. Solo copia la configuración
        de esta programación al reporte.
        """

        reference_datetime = (
            reference_datetime
            or timezone.now()
        )

        start_date, end_date = self.get_period_range(
            reference_datetime=reference_datetime,
        )

        if not start_date or not end_date:
            raise ValidationError(
                "No se pudo calcular el periodo del reporte."
            )

        if end_date < start_date:
            raise ValidationError(
                "El periodo calculado no es válido."
            )

        report = AttendanceReport.objects.create(
            report_number=report_number,
            name=self.name,
            description=self.description,
            report_type=self.report_type,
            period_type=self._get_report_period_type(),
            file_format=self.file_format,
            status=AttendanceReport.Status.PENDING,
            generation_source=(
                AttendanceReport.GenerationSource.SCHEDULED
            ),
            start_date=start_date,
            end_date=end_date,
            timezone_name=self.timezone_name,
            company_names=list(
                self.company_names or []
            ),
            department_names=list(
                self.department_names or []
            ),
            job_titles=list(
                self.job_titles or []
            ),
            attendance_statuses=list(
                self.attendance_statuses or []
            ),
            incident_types=list(
                self.incident_types or []
            ),
            leave_types=list(
                self.leave_types or []
            ),
            overtime_types=list(
                self.overtime_types or []
            ),
            operational_session_types=list(
                self.operational_session_types or []
            ),
            filters=dict(
                self.filters or {}
            ),
            selected_columns=list(
                self.selected_columns or []
            ),
            ordering_fields=list(
                self.ordering_fields or []
            ),
            grouping_fields=list(
                self.grouping_fields or []
            ),
            include_archived=self.include_archived,
            include_details=self.include_details,
            include_summary=self.include_summary,
            include_charts=self.include_charts,
            include_incidents=self.include_incidents,
            include_justifications=(
                self.include_justifications
            ),
            include_operational_time=(
                self.include_operational_time
            ),
            include_external_delays=(
                self.include_external_delays
            ),
            include_sensitive_data=(
                self.include_sensitive_data
            ),
            mask_sensitive_data=self.mask_sensitive_data,
            requested_at=reference_datetime,
            requested_by=user,
            is_private=True,
            created_by=user,
            updated_by=user,
            result_metadata={
                "report_schedule_id": str(self.id),
                "report_schedule_code": self.code,
                "delivery_mode": self.delivery_mode,
            },
        )

        report.employee_profiles.set(
            self.employee_profiles.all()
        )

        report.work_locations.set(
            self.work_locations.all()
        )

        report.work_schedules.set(
            self.work_schedules.all()
        )

        report.allowed_users.set(
            self.recipient_users.all()
        )

        return report

    def _get_report_period_type(self):
        mapping = {
            self.PeriodMode.CURRENT_DAY: (
                AttendanceReport.PeriodType.DAY
            ),
            self.PeriodMode.PREVIOUS_DAY: (
                AttendanceReport.PeriodType.DAY
            ),
            self.PeriodMode.CURRENT_WEEK: (
                AttendanceReport.PeriodType.WEEK
            ),
            self.PeriodMode.PREVIOUS_WEEK: (
                AttendanceReport.PeriodType.WEEK
            ),
            self.PeriodMode.LAST_SEVEN_DAYS: (
                AttendanceReport.PeriodType.WEEK
            ),
            self.PeriodMode.CURRENT_MONTH: (
                AttendanceReport.PeriodType.MONTH
            ),
            self.PeriodMode.PREVIOUS_MONTH: (
                AttendanceReport.PeriodType.MONTH
            ),
            self.PeriodMode.LAST_THIRTY_DAYS: (
                AttendanceReport.PeriodType.MONTH
            ),
            self.PeriodMode.CURRENT_QUARTER: (
                AttendanceReport.PeriodType.QUARTER
            ),
            self.PeriodMode.PREVIOUS_QUARTER: (
                AttendanceReport.PeriodType.QUARTER
            ),
            self.PeriodMode.CURRENT_YEAR: (
                AttendanceReport.PeriodType.YEAR
            ),
            self.PeriodMode.PREVIOUS_YEAR: (
                AttendanceReport.PeriodType.YEAR
            ),
        }

        return mapping.get(
            self.period_mode,
            AttendanceReport.PeriodType.CUSTOM,
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
            self.Status.RUNNING,
            self.Status.COMPLETED,
            self.Status.CANCELLED,
        ):
            raise ValidationError(
                "La programación ya no puede cancelarse."
            )

        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancelled_by = user
        self.cancellation_reason = reason
        self.next_execution_at = None
        self.updated_by = user

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

        if self.status in (
            self.Status.ACTIVE,
            self.Status.RUNNING,
        ):
            raise ValidationError(
                "No puedes archivar una programación "
                "activa o en ejecución."
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