# -*- coding: utf-8 -*-

import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .employee_calendar_assignment import (
    EmployeeCalendarAssignment,
)
from .employee_profile import EmployeeProfile
from .employee_schedule_assignment import (
    EmployeeScheduleAssignment,
)
from .holiday_calendar import HolidayCalendarDay
from .work_location import WorkLocation
from .work_schedule import WorkScheduleDay


class DailyAttendance(models.Model):
    """
    Consolidado diario de asistencia de un trabajador.

    No reemplaza las marcaciones originales. Resume y calcula:

    - Jornada programada.
    - Primera entrada.
    - Última salida.
    - Refrigerio.
    - Minutos trabajados.
    - Tardanza.
    - Salida anticipada.
    - Horas extras.
    - Ausencias.
    - Permisos, vacaciones y feriados.
    - Incidencias pendientes.
    """

    class AttendanceStatus(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente de procesar",
        )
        PRESENT = (
            "present",
            "Presente",
        )
        PRESENT_WITH_INCIDENTS = (
            "present_with_incidents",
            "Presente con incidencias",
        )
        ABSENT = (
            "absent",
            "Ausente",
        )
        JUSTIFIED_ABSENCE = (
            "justified_absence",
            "Ausencia justificada",
        )
        VACATION = (
            "vacation",
            "Vacaciones",
        )
        MEDICAL_LEAVE = (
            "medical_leave",
            "Descanso médico",
        )
        PAID_LEAVE = (
            "paid_leave",
            "Permiso con goce",
        )
        UNPAID_LEAVE = (
            "unpaid_leave",
            "Permiso sin goce",
        )
        HOLIDAY = (
            "holiday",
            "Feriado",
        )
        NON_WORKING_DAY = (
            "non_working_day",
            "Día no laborable",
        )
        REST_DAY = (
            "rest_day",
            "Día de descanso",
        )
        COMMISSION = (
            "commission",
            "Comisión de servicio",
        )
        REMOTE_WORK = (
            "remote_work",
            "Trabajo remoto",
        )
        SUSPENDED = (
            "suspended",
            "Suspendido",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )

    class ProcessingStatus(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        PROCESSING = (
            "processing",
            "Procesando",
        )
        PROCESSED = (
            "processed",
            "Procesado",
        )
        REVIEW_REQUIRED = (
            "review_required",
            "Requiere revisión",
        )
        APPROVED = (
            "approved",
            "Aprobado",
        )
        CLOSED = (
            "closed",
            "Cerrado",
        )
        ERROR = (
            "error",
            "Error",
        )

    class DaySource(models.TextChoices):
        SCHEDULE = (
            "schedule",
            "Horario laboral",
        )
        HOLIDAY = (
            "holiday",
            "Calendario laboral",
        )
        LEAVE = (
            "leave",
            "Permiso o licencia",
        )
        VACATION = (
            "vacation",
            "Vacaciones",
        )
        MANUAL = (
            "manual",
            "Registro manual",
        )
        SYSTEM = (
            "system",
            "Calculado por el sistema",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    employee_profile = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.PROTECT,
        related_name="daily_attendances",
        verbose_name="Perfil laboral",
    )

    date = models.DateField(
        db_index=True,
        verbose_name="Fecha",
    )

    attendance_status = models.CharField(
        max_length=40,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PENDING,
        db_index=True,
        verbose_name="Estado de asistencia",
    )

    processing_status = models.CharField(
        max_length=30,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
        db_index=True,
        verbose_name="Estado de procesamiento",
    )

    day_source = models.CharField(
        max_length=20,
        choices=DaySource.choices,
        default=DaySource.SYSTEM,
        db_index=True,
        verbose_name="Origen del día",
    )

    schedule_assignment = models.ForeignKey(
        EmployeeScheduleAssignment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="daily_attendances",
        verbose_name="Asignación de horario",
    )

    schedule_day = models.ForeignKey(
        WorkScheduleDay,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="daily_attendances",
        verbose_name="Día de horario",
    )

    calendar_assignment = models.ForeignKey(
        EmployeeCalendarAssignment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="daily_attendances",
        verbose_name="Asignación de calendario",
    )

    holiday_day = models.ForeignKey(
        HolidayCalendarDay,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="daily_attendances",
        verbose_name="Día especial",
    )

    primary_location = models.ForeignKey(
        WorkLocation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="daily_attendances",
        verbose_name="Ubicación principal",
    )

    is_scheduled_working_day = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Día laborable programado",
    )

    attendance_required = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere asistencia",
    )

    scheduled_entry_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Ingreso programado",
    )

    scheduled_exit_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Salida programada",
    )

    scheduled_break_start_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio de refrigerio programado",
    )

    scheduled_break_end_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin de refrigerio programado",
    )

    scheduled_shift_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos programados de jornada",
    )

    scheduled_break_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos programados de refrigerio",
    )

    scheduled_work_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos programados de trabajo",
    )

    first_clock_in_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Primera entrada",
    )

    last_clock_out_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Última salida",
    )

    first_break_start_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Primer inicio de refrigerio",
    )

    last_break_end_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último fin de refrigerio",
    )

    first_field_work_start_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio de trabajo de campo",
    )

    last_field_work_end_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin de trabajo de campo",
    )

    first_remote_work_start_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio de trabajo remoto",
    )

    last_remote_work_end_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin de trabajo remoto",
    )

    gross_presence_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos totales de presencia",
    )

    valid_break_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos válidos de refrigerio",
    )

    excess_break_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Exceso de refrigerio",
    )

    effective_work_minutes = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos efectivos trabajados",
    )

    operational_work_minutes = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos de trabajo operativo",
    )

    administrative_work_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos de trabajo administrativo",
    )

    unclassified_minutes = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos sin clasificar",
    )

    late_minutes = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos de tardanza",
    )

    early_departure_minutes = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos de salida anticipada",
    )

    missing_work_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos faltantes de jornada",
    )

    overtime_minutes = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos de horas extras",
    )

    approved_overtime_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos extra aprobados",
    )

    compensation_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos de compensación",
    )

    attendance_record_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad de marcaciones",
    )

    valid_record_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Marcaciones válidas",
    )

    observed_record_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Marcaciones observadas",
    )

    rejected_record_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Marcaciones rechazadas",
    )

    manual_record_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Marcaciones manuales",
    )

    incomplete_clocking = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Marcación incompleta",
    )

    missing_clock_in = models.BooleanField(
        default=False,
        verbose_name="Falta marcación de entrada",
    )

    missing_clock_out = models.BooleanField(
        default=False,
        verbose_name="Falta marcación de salida",
    )

    missing_break_start = models.BooleanField(
        default=False,
        verbose_name="Falta inicio de refrigerio",
    )

    missing_break_end = models.BooleanField(
        default=False,
        verbose_name="Falta fin de refrigerio",
    )

    location_incident = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Incidencia de ubicación",
    )

    device_incident = models.BooleanField(
        default=False,
        verbose_name="Incidencia de dispositivo",
    )

    schedule_incident = models.BooleanField(
        default=False,
        verbose_name="Incidencia de horario",
    )

    requires_review = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere revisión",
    )

    review_reasons = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Motivos de revisión",
    )

    employee_explanation = models.TextField(
        blank=True,
        verbose_name="Explicación del trabajador",
    )

    supervisor_observation = models.TextField(
        blank=True,
        verbose_name="Observación del supervisor",
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
        related_name="daily_attendances_reviewed",
        verbose_name="Revisado por",
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
        related_name="daily_attendances_approved",
        verbose_name="Aprobado por",
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Cerrado el",
    )

    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="daily_attendances_closed",
        verbose_name="Cerrado por",
    )

    processing_error = models.TextField(
        blank=True,
        verbose_name="Error de procesamiento",
    )

    last_processed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Último procesamiento",
    )

    calculation_version = models.PositiveIntegerField(
        default=1,
        verbose_name="Versión de cálculo",
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
        related_name="daily_attendances_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="daily_attendances_updated",
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
        related_name="daily_attendances_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Asistencia diaria"
        verbose_name_plural = "Asistencias diarias"

        ordering = (
            "-date",
            "employee_profile",
        )

        constraints = (
            models.UniqueConstraint(
                fields=(
                    "employee_profile",
                    "date",
                ),
                condition=models.Q(
                    archived_at__isnull=True,
                ),
                name="att_daily_employee_date_unique",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    approved_overtime_minutes__lte=models.F(
                        "overtime_minutes"
                    ),
                ),
                name="att_daily_approved_ot_lte_total",
            ),
        )

        indexes = (
            models.Index(
                fields=(
                    "employee_profile",
                    "date",
                    "attendance_status",
                ),
                name="att_daily_emp_date_status_idx",
            ),
            models.Index(
                fields=(
                    "processing_status",
                    "requires_review",
                    "date",
                ),
                name="att_daily_proc_review_idx",
            ),
            models.Index(
                fields=(
                    "attendance_required",
                    "is_scheduled_working_day",
                    "date",
                ),
                name="att_daily_required_work_idx",
            ),
            models.Index(
                fields=(
                    "late_minutes",
                    "early_departure_minutes",
                ),
                name="att_daily_late_early_idx",
            ),
            models.Index(
                fields=(
                    "effective_work_minutes",
                    "operational_work_minutes",
                ),
                name="att_daily_work_oper_idx",
            ),
            models.Index(
                fields=(
                    "incomplete_clocking",
                    "location_incident",
                    "device_incident",
                ),
                name="att_daily_incidents_idx",
            ),
            models.Index(
                fields=(
                    "holiday_day",
                    "date",
                ),
                name="att_daily_holiday_idx",
            ),
        )

    def __str__(self):
        return (
            f"{self.employee_profile.user.full_name} - "
            f"{self.date} - "
            f"{self.get_attendance_status_display()}"
        )

    @property
    def employee(self):
        return self.employee_profile.user

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_closed(self):
        return (
            self.processing_status
            == self.ProcessingStatus.CLOSED
        )

    @property
    def has_clock_in(self):
        return self.first_clock_in_at is not None

    @property
    def has_clock_out(self):
        return self.last_clock_out_at is not None

    @property
    def has_complete_presence(self):
        return (
            self.has_clock_in
            and self.has_clock_out
            and self.last_clock_out_at
            > self.first_clock_in_at
        )

    @property
    def worked_hours(self):
        return round(
            self.effective_work_minutes / 60,
            2,
        )

    @property
    def operational_hours(self):
        return round(
            self.operational_work_minutes / 60,
            2,
        )

    @property
    def overtime_hours(self):
        return round(
            self.overtime_minutes / 60,
            2,
        )

    @property
    def attendance_percentage(self):
        if self.scheduled_work_minutes <= 0:
            return 100

        percentage = (
            self.effective_work_minutes
            / self.scheduled_work_minutes
        ) * 100

        return round(
            min(
                100,
                max(
                    0,
                    percentage,
                ),
            ),
            2,
        )

    @property
    def productivity_time_percentage(self):
        if self.effective_work_minutes <= 0:
            return 0

        percentage = (
            self.operational_work_minutes
            / self.effective_work_minutes
        ) * 100

        return round(
            min(
                100,
                max(
                    0,
                    percentage,
                ),
            ),
            2,
        )

    def build_scheduled_datetimes(self):
        if (
            not self.schedule_day_id
            or not self.schedule_day.is_working_day
            or not self.schedule_day.entry_time
            or not self.schedule_day.exit_time
        ):
            return

        entry_datetime = timezone.make_aware(
            datetime.combine(
                self.date,
                self.schedule_day.entry_time,
            )
        )

        exit_date = self.date

        if self.schedule_day.exit_next_day:
            exit_date += timedelta(days=1)

        exit_datetime = timezone.make_aware(
            datetime.combine(
                exit_date,
                self.schedule_day.exit_time,
            )
        )

        if (
            not self.schedule_day.exit_next_day
            and exit_datetime <= entry_datetime
        ):
            exit_datetime += timedelta(days=1)

        self.scheduled_entry_at = entry_datetime
        self.scheduled_exit_at = exit_datetime

        if (
            self.schedule_day.break_enabled
            and self.schedule_day.break_start_time
            and self.schedule_day.break_end_time
        ):
            break_start_date = self.date

            break_start = timezone.make_aware(
                datetime.combine(
                    break_start_date,
                    self.schedule_day.break_start_time,
                )
            )

            break_end_date = self.date

            if self.schedule_day.break_end_next_day:
                break_end_date += timedelta(days=1)

            break_end = timezone.make_aware(
                datetime.combine(
                    break_end_date,
                    self.schedule_day.break_end_time,
                )
            )

            if break_end <= break_start:
                break_end += timedelta(days=1)

            self.scheduled_break_start_at = break_start
            self.scheduled_break_end_at = break_end

        else:
            self.scheduled_break_start_at = None
            self.scheduled_break_end_at = None

        self.scheduled_shift_minutes = (
            self.schedule_day.scheduled_shift_minutes
        )

        self.scheduled_break_minutes = (
            self.schedule_day.scheduled_break_minutes
        )

        self.scheduled_work_minutes = (
            self.schedule_day.scheduled_work_minutes
        )

        self.is_scheduled_working_day = (
            self.schedule_day.is_working_day
        )

        self.attendance_required = (
            self.schedule_day.requires_attendance
        )

    def calculate_presence_minutes(self):
        if not self.has_complete_presence:
            self.gross_presence_minutes = 0
            return 0

        minutes = int(
            (
                self.last_clock_out_at
                - self.first_clock_in_at
            ).total_seconds()
            // 60
        )

        self.gross_presence_minutes = max(
            0,
            minutes,
        )

        return self.gross_presence_minutes

    def calculate_late_minutes(self):
        if (
            not self.first_clock_in_at
            or not self.scheduled_entry_at
        ):
            self.late_minutes = 0
            return 0

        tolerance = 0

        if self.schedule_assignment_id:
            tolerance = (
                self.schedule_assignment
                .effective_entry_tolerance_minutes
            )

        allowed_entry = (
            self.scheduled_entry_at
            + timedelta(
                minutes=tolerance,
            )
        )

        if self.first_clock_in_at <= allowed_entry:
            self.late_minutes = 0
            return 0

        self.late_minutes = int(
            (
                self.first_clock_in_at
                - allowed_entry
            ).total_seconds()
            // 60
        )

        return self.late_minutes

    def calculate_early_departure_minutes(self):
        if (
            not self.last_clock_out_at
            or not self.scheduled_exit_at
        ):
            self.early_departure_minutes = 0
            return 0

        tolerance = 0

        if self.schedule_assignment_id:
            tolerance = (
                self.schedule_assignment
                .effective_early_departure_tolerance_minutes
            )

        allowed_exit = (
            self.scheduled_exit_at
            - timedelta(
                minutes=tolerance,
            )
        )

        if self.last_clock_out_at >= allowed_exit:
            self.early_departure_minutes = 0
            return 0

        self.early_departure_minutes = int(
            (
                allowed_exit
                - self.last_clock_out_at
            ).total_seconds()
            // 60
        )

        return self.early_departure_minutes

    def calculate_effective_work_minutes(self):
        gross_minutes = (
            self.calculate_presence_minutes()
        )

        deducted_break = min(
            gross_minutes,
            self.valid_break_minutes,
        )

        self.effective_work_minutes = max(
            0,
            gross_minutes - deducted_break,
        )

        self.missing_work_minutes = max(
            0,
            self.scheduled_work_minutes
            - self.effective_work_minutes,
        )

        self.overtime_minutes = max(
            0,
            self.effective_work_minutes
            - self.scheduled_work_minutes,
        )

        return self.effective_work_minutes

    def calculate_unclassified_minutes(self):
        classified_minutes = (
            self.operational_work_minutes
            + self.administrative_work_minutes
        )

        self.unclassified_minutes = max(
            0,
            self.effective_work_minutes
            - classified_minutes,
        )

        return self.unclassified_minutes

    def determine_incomplete_clocking(self):
        self.missing_clock_in = (
            self.attendance_required
            and not self.first_clock_in_at
        )

        self.missing_clock_out = (
            self.attendance_required
            and self.first_clock_in_at is not None
            and self.last_clock_out_at is None
        )

        requires_break_clocking = False

        if (
            self.schedule_assignment_id
            and self.schedule_assignment.schedule_id
        ):
            requires_break_clocking = (
                self.schedule_assignment
                .schedule
                .requires_break_clocking
            )

        has_scheduled_break = (
            self.schedule_day_id
            and self.schedule_day.break_enabled
        )

        self.missing_break_start = (
            self.attendance_required
            and requires_break_clocking
            and has_scheduled_break
            and self.first_clock_in_at is not None
            and self.first_break_start_at is None
        )

        self.missing_break_end = (
            self.attendance_required
            and requires_break_clocking
            and has_scheduled_break
            and self.first_break_start_at is not None
            and self.last_break_end_at is None
        )

        self.incomplete_clocking = any(
            (
                self.missing_clock_in,
                self.missing_clock_out,
                self.missing_break_start,
                self.missing_break_end,
            )
        )

        return self.incomplete_clocking

    def update_review_reasons(self):
        reasons = []

        if self.missing_clock_in:
            reasons.append(
                "Falta marcación de entrada."
            )

        if self.missing_clock_out:
            reasons.append(
                "Falta marcación de salida."
            )

        if self.missing_break_start:
            reasons.append(
                "Falta inicio de refrigerio."
            )

        if self.missing_break_end:
            reasons.append(
                "Falta fin de refrigerio."
            )

        if self.late_minutes > 0:
            reasons.append(
                f"Tardanza de {self.late_minutes} minutos."
            )

        if self.early_departure_minutes > 0:
            reasons.append(
                "Salida anticipada de "
                f"{self.early_departure_minutes} minutos."
            )

        if self.excess_break_minutes > 0:
            reasons.append(
                "Exceso de refrigerio de "
                f"{self.excess_break_minutes} minutos."
            )

        if self.location_incident:
            reasons.append(
                "Existe una incidencia de ubicación."
            )

        if self.device_incident:
            reasons.append(
                "Existe una incidencia de dispositivo."
            )

        if self.schedule_incident:
            reasons.append(
                "Existe una incidencia de horario."
            )

        if self.observed_record_count > 0:
            reasons.append(
                "Existen marcaciones observadas."
            )

        if self.rejected_record_count > 0:
            reasons.append(
                "Existen marcaciones rechazadas."
            )

        self.review_reasons = reasons
        self.requires_review = bool(reasons)

        return reasons

    def determine_attendance_status(self):
        if not self.attendance_required:
            if self.holiday_day_id:
                if self.holiday_day.is_working_day:
                    self.attendance_status = (
                        self.AttendanceStatus.PRESENT
                        if self.first_clock_in_at
                        else self.AttendanceStatus.PENDING
                    )
                elif (
                    self.holiday_day.day_type
                    == HolidayCalendarDay.DayType.NATIONAL_HOLIDAY
                ):
                    self.attendance_status = (
                        self.AttendanceStatus.HOLIDAY
                    )
                else:
                    self.attendance_status = (
                        self.AttendanceStatus.NON_WORKING_DAY
                    )

            elif not self.is_scheduled_working_day:
                self.attendance_status = (
                    self.AttendanceStatus.REST_DAY
                )

            else:
                self.attendance_status = (
                    self.AttendanceStatus.NOT_APPLICABLE
                )

            return self.attendance_status

        if (
            self.first_clock_in_at
            or self.last_clock_out_at
        ):
            if self.requires_review:
                self.attendance_status = (
                    self.AttendanceStatus
                    .PRESENT_WITH_INCIDENTS
                )
            else:
                self.attendance_status = (
                    self.AttendanceStatus.PRESENT
                )

            return self.attendance_status

        if (
            self.date < timezone.localdate()
            and self.is_scheduled_working_day
        ):
            self.attendance_status = (
                self.AttendanceStatus.ABSENT
            )
        else:
            self.attendance_status = (
                self.AttendanceStatus.PENDING
            )

        return self.attendance_status

    def recalculate(self):
        if self.is_closed:
            raise ValidationError(
                "No puedes recalcular una asistencia cerrada."
            )

        self.processing_status = (
            self.ProcessingStatus.PROCESSING
        )

        self.processing_error = ""

        try:
            self.build_scheduled_datetimes()
            self.calculate_late_minutes()
            self.calculate_early_departure_minutes()
            self.calculate_effective_work_minutes()
            self.calculate_unclassified_minutes()
            self.determine_incomplete_clocking()
            self.update_review_reasons()
            self.determine_attendance_status()

            if self.requires_review:
                self.processing_status = (
                    self.ProcessingStatus.REVIEW_REQUIRED
                )
            else:
                self.processing_status = (
                    self.ProcessingStatus.PROCESSED
                )

            self.last_processed_at = timezone.now()
            self.calculation_version += 1

        except Exception as exception:
            self.processing_status = (
                self.ProcessingStatus.ERROR
            )

            self.processing_error = str(
                exception
            )

            self.last_processed_at = timezone.now()

            raise

        finally:
            self.save()

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.employee_profile_id
            and self.employee_profile.archived_at
        ):
            errors["employee_profile"] = (
                "El perfil laboral está archivado."
            )

        if (
            self.schedule_assignment_id
            and self.schedule_assignment.employee_profile_id
            != self.employee_profile_id
        ):
            errors["schedule_assignment"] = (
                "La asignación de horario no corresponde "
                "al trabajador."
            )

        if (
            self.calendar_assignment_id
            and self.calendar_assignment.employee_profile_id
            != self.employee_profile_id
        ):
            errors["calendar_assignment"] = (
                "La asignación de calendario no corresponde "
                "al trabajador."
            )

        if (
            self.schedule_day_id
            and self.schedule_assignment_id
            and self.schedule_day.schedule_id
            != self.schedule_assignment.schedule_id
        ):
            errors["schedule_day"] = (
                "El día no pertenece al horario asignado."
            )

        if (
            self.holiday_day_id
            and self.calendar_assignment_id
            and self.holiday_day.calendar_id
            != self.calendar_assignment.calendar_id
        ):
            errors["holiday_day"] = (
                "El día especial no pertenece al calendario "
                "asignado."
            )

        if (
            self.first_clock_in_at
            and self.last_clock_out_at
            and self.last_clock_out_at
            <= self.first_clock_in_at
        ):
            errors["last_clock_out_at"] = (
                "La salida debe ser posterior a la entrada."
            )

        if (
            self.first_break_start_at
            and self.last_break_end_at
            and self.last_break_end_at
            <= self.first_break_start_at
        ):
            errors["last_break_end_at"] = (
                "El fin de refrigerio debe ser posterior "
                "al inicio."
            )

        if (
            self.approved_overtime_minutes
            > self.overtime_minutes
        ):
            errors["approved_overtime_minutes"] = (
                "Los minutos extra aprobados no pueden superar "
                "las horas extras calculadas."
            )

        if (
            self.operational_work_minutes
            + self.administrative_work_minutes
            > self.effective_work_minutes
        ):
            errors["operational_work_minutes"] = (
                "Los minutos clasificados no pueden superar "
                "el tiempo efectivo trabajado."
            )

        if (
            self.processing_status
            == self.ProcessingStatus.APPROVED
            and not self.approved_at
        ):
            errors["approved_at"] = (
                "Una asistencia aprobada debe tener fecha "
                "de aprobación."
            )

        if (
            self.processing_status
            == self.ProcessingStatus.CLOSED
            and not self.closed_at
        ):
            errors["closed_at"] = (
                "Una asistencia cerrada debe tener fecha "
                "de cierre."
            )

        if (
            self.reviewed_at
            and not self.reviewed_by_id
        ):
            errors["reviewed_by"] = (
                "Debes indicar quién revisó la asistencia."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def mark_reviewed(
        self,
        user,
        observation="",
    ):
        self.reviewed_at = timezone.now()
        self.reviewed_by = user
        self.supervisor_observation = str(
            observation or ""
        ).strip()
        self.updated_by = user

        if self.requires_review:
            self.processing_status = (
                self.ProcessingStatus.REVIEW_REQUIRED
            )

        self.save(
            update_fields=[
                "reviewed_at",
                "reviewed_by",
                "supervisor_observation",
                "processing_status",
                "updated_by",
                "updated_at",
            ]
        )

    def approve(
        self,
        user,
        observation="",
    ):
        if self.processing_status == (
            self.ProcessingStatus.ERROR
        ):
            raise ValidationError(
                "No puedes aprobar una asistencia con error."
            )

        self.processing_status = (
            self.ProcessingStatus.APPROVED
        )

        self.approved_at = timezone.now()
        self.approved_by = user
        self.reviewed_at = timezone.now()
        self.reviewed_by = user
        self.supervisor_observation = str(
            observation or ""
        ).strip()
        self.requires_review = False
        self.updated_by = user

        self.save(
            update_fields=[
                "processing_status",
                "approved_at",
                "approved_by",
                "reviewed_at",
                "reviewed_by",
                "supervisor_observation",
                "requires_review",
                "updated_by",
                "updated_at",
            ]
        )

    def close(
        self,
        user,
        observation="",
    ):
        if self.processing_status not in (
            self.ProcessingStatus.APPROVED,
            self.ProcessingStatus.PROCESSED,
        ):
            raise ValidationError(
                "Solo puedes cerrar una asistencia procesada "
                "o aprobada."
            )

        self.processing_status = (
            self.ProcessingStatus.CLOSED
        )

        self.closed_at = timezone.now()
        self.closed_by = user
        self.supervisor_observation = str(
            observation
            or self.supervisor_observation
            or ""
        ).strip()
        self.updated_by = user

        self.save(
            update_fields=[
                "processing_status",
                "closed_at",
                "closed_by",
                "supervisor_observation",
                "updated_by",
                "updated_at",
            ]
        )

    def reopen(
        self,
        user,
        reason,
    ):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de reapertura."
            )

        if not self.is_closed:
            raise ValidationError(
                "La asistencia no se encuentra cerrada."
            )

        self.processing_status = (
            self.ProcessingStatus.REVIEW_REQUIRED
        )

        self.closed_at = None
        self.closed_by = None
        self.requires_review = True

        current_reasons = list(
            self.review_reasons or []
        )

        current_reasons.append(
            f"Reabierta: {reason}"
        )

        self.review_reasons = current_reasons
        self.updated_by = user

        self.save(
            update_fields=[
                "processing_status",
                "closed_at",
                "closed_by",
                "requires_review",
                "review_reasons",
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

        if self.is_closed:
            raise ValidationError(
                "No puedes archivar una asistencia cerrada."
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

    def restore(self, user=None):
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