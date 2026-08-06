# -*- coding: utf-8 -*-

import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class WorkSchedule(models.Model):
    """
    Horario laboral reutilizable.

    Ejemplos:

    - Taller regular.
    - Servicios técnicos.
    - Ventas.
    - Administración.
    - Horario de sábado.
    - Turno nocturno.
    - Jornada parcial.
    """

    class ScheduleType(models.TextChoices):
        FIXED = (
            "fixed",
            "Horario fijo",
        )
        ROTATING = (
            "rotating",
            "Horario rotativo",
        )
        FLEXIBLE = (
            "flexible",
            "Horario flexible",
        )
        PART_TIME = (
            "part_time",
            "Tiempo parcial",
        )
        NIGHT = (
            "night",
            "Turno nocturno",
        )
        SPECIAL = (
            "special",
            "Horario especial",
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
        max_length=150,
        db_index=True,
        verbose_name="Nombre",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    schedule_type = models.CharField(
        max_length=20,
        choices=ScheduleType.choices,
        default=ScheduleType.FIXED,
        db_index=True,
        verbose_name="Tipo de horario",
    )

    timezone_name = models.CharField(
        max_length=100,
        default="America/Lima",
        verbose_name="Zona horaria",
    )

    weekly_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=48,
        verbose_name="Horas semanales programadas",
    )

    default_entry_tolerance_minutes = (
        models.PositiveSmallIntegerField(
            default=0,
            verbose_name=(
                "Tolerancia predeterminada de ingreso"
            ),
        )
    )

    default_early_departure_tolerance_minutes = (
        models.PositiveSmallIntegerField(
            default=0,
            verbose_name=(
                "Tolerancia predeterminada de salida anticipada"
            ),
        )
    )

    minimum_overtime_minutes = (
        models.PositiveSmallIntegerField(
            default=30,
            verbose_name=(
                "Minutos mínimos para considerar horas extras"
            ),
        )
    )

    allows_early_clock_in = models.BooleanField(
        default=True,
        verbose_name="Permitir marcación anticipada",
    )

    maximum_early_clock_in_minutes = (
        models.PositiveSmallIntegerField(
            default=120,
            verbose_name=(
                "Máximo de anticipación para marcar ingreso"
            ),
        )
    )

    allows_late_clock_out = models.BooleanField(
        default=True,
        verbose_name="Permitir marcación posterior a la salida",
    )

    maximum_late_clock_out_minutes = (
        models.PositiveSmallIntegerField(
            default=240,
            verbose_name=(
                "Máximo de demora permitido para marcar salida"
            ),
        )
    )

    automatically_deduct_break = models.BooleanField(
        default=False,
        verbose_name="Descontar refrigerio automáticamente",
        help_text=(
            "Solo debe activarse cuando la política de la empresa "
            "permita descontar el refrigerio programado aunque no "
            "existan marcaciones de inicio y fin."
        ),
    )

    requires_break_clocking = models.BooleanField(
        default=True,
        verbose_name="Requiere marcación de refrigerio",
    )

    allows_split_shift = models.BooleanField(
        default=False,
        verbose_name="Permite jornada dividida",
    )

    allows_overnight_shift = models.BooleanField(
        default=False,
        verbose_name="Permite turnos que terminan al día siguiente",
    )

    effective_from = models.DateField(
        default=timezone.localdate,
        db_index=True,
        verbose_name="Vigente desde",
    )

    effective_until = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Vigente hasta",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activo",
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
        related_name="attendance_work_schedules_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_work_schedules_updated",
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
        related_name="attendance_work_schedules_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Horario laboral"
        verbose_name_plural = "Horarios laborales"

        ordering = (
            "name",
            "code",
        )

        indexes = (
            models.Index(
                fields=(
                    "schedule_type",
                    "is_active",
                ),
                name="att_sched_type_active_idx",
            ),
            models.Index(
                fields=(
                    "effective_from",
                    "effective_until",
                ),
                name="att_sched_effective_idx",
            ),
        )

        constraints = (
            models.CheckConstraint(
                condition=(
                    models.Q(
                        weekly_hours__gte=0,
                    )
                    & models.Q(
                        weekly_hours__lte=168,
                    )
                ),
                name="att_sched_weekly_hours_range",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    default_entry_tolerance_minutes__lte=180,
                ),
                name="att_sched_entry_tol_max_180",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    default_early_departure_tolerance_minutes__lte=180,
                ),
                name="att_sched_exit_tol_max_180",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    maximum_early_clock_in_minutes__lte=720,
                ),
                name="att_sched_early_max_720",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    maximum_late_clock_out_minutes__lte=1440,
                ),
                name="att_sched_late_max_1440",
            ),
        )

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_current(self):
        today = timezone.localdate()

        if self.archived_at is not None:
            return False

        if not self.is_active:
            return False

        if self.effective_from > today:
            return False

        if (
            self.effective_until
            and self.effective_until < today
        ):
            return False

        return True

    @property
    def calculated_weekly_minutes(self):
        return sum(
            day.scheduled_work_minutes
            for day in self.days.filter(
                is_working_day=True,
                is_active=True,
                archived_at__isnull=True,
            )
        )

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.effective_until
            and self.effective_until < self.effective_from
        ):
            errors["effective_until"] = (
                "La fecha final no puede ser anterior "
                "a la fecha inicial."
            )

        if (
            self.automatically_deduct_break
            and self.requires_break_clocking
        ):
            errors["automatically_deduct_break"] = (
                "No puedes descontar automáticamente el refrigerio "
                "y exigir su marcación al mismo tiempo."
            )

        if (
            not self.allows_early_clock_in
            and self.maximum_early_clock_in_minutes
        ):
            errors[
                "maximum_early_clock_in_minutes"
            ] = (
                "El máximo de anticipación debe ser cero cuando "
                "no se permite marcar antes."
            )

        if (
            not self.allows_late_clock_out
            and self.maximum_late_clock_out_minutes
        ):
            errors[
                "maximum_late_clock_out_minutes"
            ] = (
                "El máximo posterior debe ser cero cuando no se "
                "permite marcar después de la salida."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def archive(self, user=None, reason=""):
        self.is_active = False
        self.archived_at = timezone.now()
        self.archived_by = user
        self.archived_reason = reason
        self.updated_by = user

        self.save(
            update_fields=[
                "is_active",
                "archived_at",
                "archived_by",
                "archived_reason",
                "updated_by",
                "updated_at",
            ]
        )

    def restore(self, user=None):
        self.is_active = True
        self.archived_at = None
        self.archived_by = None
        self.archived_reason = ""
        self.updated_by = user

        self.save(
            update_fields=[
                "is_active",
                "archived_at",
                "archived_by",
                "archived_reason",
                "updated_by",
                "updated_at",
            ]
        )


class WorkScheduleDay(models.Model):
    """
    Configuración de un día dentro de un horario laboral.

    Permite definir individualmente:

    - Hora de ingreso.
    - Hora de salida.
    - Refrigerio.
    - Tolerancias.
    - Jornada nocturna.
    - Día no laborable.
    """

    class Weekday(models.IntegerChoices):
        MONDAY = (
            1,
            "Lunes",
        )
        TUESDAY = (
            2,
            "Martes",
        )
        WEDNESDAY = (
            3,
            "Miércoles",
        )
        THURSDAY = (
            4,
            "Jueves",
        )
        FRIDAY = (
            5,
            "Viernes",
        )
        SATURDAY = (
            6,
            "Sábado",
        )
        SUNDAY = (
            7,
            "Domingo",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    schedule = models.ForeignKey(
        WorkSchedule,
        on_delete=models.CASCADE,
        related_name="days",
        verbose_name="Horario",
    )

    weekday = models.PositiveSmallIntegerField(
        choices=Weekday.choices,
        db_index=True,
        verbose_name="Día de la semana",
    )

    is_working_day = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Día laborable",
    )

    entry_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora de ingreso",
    )

    exit_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora de salida",
    )

    exit_next_day = models.BooleanField(
        default=False,
        verbose_name="La salida ocurre al día siguiente",
    )

    break_enabled = models.BooleanField(
        default=True,
        verbose_name="Tiene refrigerio",
    )

    break_start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Inicio de refrigerio",
    )

    break_end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Fin de refrigerio",
    )

    break_end_next_day = models.BooleanField(
        default=False,
        verbose_name=(
            "El refrigerio termina al día siguiente"
        ),
    )

    paid_break = models.BooleanField(
        default=False,
        verbose_name="Refrigerio remunerado",
    )

    entry_tolerance_minutes = (
        models.PositiveSmallIntegerField(
            null=True,
            blank=True,
            verbose_name=(
                "Tolerancia de ingreso en minutos"
            ),
            help_text=(
                "Si se deja vacío, se utiliza la tolerancia "
                "configurada en el horario."
            ),
        )
    )

    early_departure_tolerance_minutes = (
        models.PositiveSmallIntegerField(
            null=True,
            blank=True,
            verbose_name=(
                "Tolerancia de salida anticipada"
            ),
            help_text=(
                "Si se deja vacío, se utiliza la tolerancia "
                "configurada en el horario."
            ),
        )
    )

    minimum_work_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Mínimo de minutos de trabajo",
    )

    expected_work_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos de trabajo esperados",
        help_text=(
            "Se puede dejar en cero para calcularlos "
            "automáticamente."
        ),
    )

    allows_overtime = models.BooleanField(
        default=True,
        verbose_name="Permite horas extras",
    )

    requires_attendance = models.BooleanField(
        default=True,
        verbose_name="Requiere asistencia",
    )

    notes = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Observaciones",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activo",
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
        related_name="attendance_schedule_days_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_schedule_days_updated",
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
        related_name="attendance_schedule_days_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Día de horario laboral"
        verbose_name_plural = "Días de horarios laborales"

        ordering = (
            "schedule",
            "weekday",
        )

        constraints = (
            models.UniqueConstraint(
                fields=(
                    "schedule",
                    "weekday",
                ),
                condition=models.Q(
                    archived_at__isnull=True,
                ),
                name="att_sched_day_unique_active",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        weekday__gte=1,
                    )
                    & models.Q(
                        weekday__lte=7,
                    )
                ),
                name="att_sched_day_weekday_range",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    minimum_work_minutes__lte=1440,
                ),
                name="att_sched_day_minwork_max",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    expected_work_minutes__lte=1440,
                ),
                name="att_sched_day_expected_max",
            ),
        )

        indexes = (
            models.Index(
                fields=(
                    "schedule",
                    "weekday",
                    "is_working_day",
                ),
                name="att_sched_day_work_idx",
            ),
            models.Index(
                fields=(
                    "requires_attendance",
                    "is_active",
                ),
                name="att_sched_day_att_active_idx",
            ),
        )

    def __str__(self):
        return (
            f"{self.schedule.name} - "
            f"{self.get_weekday_display()}"
        )

    @property
    def effective_entry_tolerance_minutes(self):
        if self.entry_tolerance_minutes is not None:
            return self.entry_tolerance_minutes

        return (
            self.schedule
            .default_entry_tolerance_minutes
        )

    @property
    def effective_early_departure_tolerance_minutes(
        self,
    ):
        if (
            self.early_departure_tolerance_minutes
            is not None
        ):
            return (
                self
                .early_departure_tolerance_minutes
            )

        return (
            self.schedule
            .default_early_departure_tolerance_minutes
        )

    @property
    def scheduled_break_minutes(self):
        if (
            not self.break_enabled
            or not self.break_start_time
            or not self.break_end_time
        ):
            return 0

        start_datetime = datetime.combine(
            timezone.localdate(),
            self.break_start_time,
        )

        end_datetime = datetime.combine(
            timezone.localdate(),
            self.break_end_time,
        )

        if self.break_end_next_day:
            end_datetime += timedelta(days=1)

        elif end_datetime <= start_datetime:
            end_datetime += timedelta(days=1)

        return max(
            0,
            int(
                (
                    end_datetime
                    - start_datetime
                ).total_seconds()
                // 60
            ),
        )

    @property
    def scheduled_shift_minutes(self):
        if (
            not self.is_working_day
            or not self.entry_time
            or not self.exit_time
        ):
            return 0

        start_datetime = datetime.combine(
            timezone.localdate(),
            self.entry_time,
        )

        end_datetime = datetime.combine(
            timezone.localdate(),
            self.exit_time,
        )

        if self.exit_next_day:
            end_datetime += timedelta(days=1)

        elif end_datetime <= start_datetime:
            end_datetime += timedelta(days=1)

        return max(
            0,
            int(
                (
                    end_datetime
                    - start_datetime
                ).total_seconds()
                // 60
            ),
        )

    @property
    def scheduled_work_minutes(self):
        if self.expected_work_minutes:
            return self.expected_work_minutes

        shift_minutes = (
            self.scheduled_shift_minutes
        )

        if (
            not self.break_enabled
            or self.paid_break
        ):
            return shift_minutes

        return max(
            0,
            shift_minutes
            - self.scheduled_break_minutes,
        )

    def clean(self):
        super().clean()

        errors = {}

        if self.is_working_day:
            if not self.entry_time:
                errors["entry_time"] = (
                    "Debes indicar la hora de ingreso."
                )

            if not self.exit_time:
                errors["exit_time"] = (
                    "Debes indicar la hora de salida."
                )

        else:
            if self.entry_time or self.exit_time:
                errors["is_working_day"] = (
                    "Un día no laborable no debe tener "
                    "hora de ingreso ni salida."
                )

            if self.break_enabled:
                errors["break_enabled"] = (
                    "Un día no laborable no puede tener "
                    "refrigerio."
                )

        if (
            self.exit_next_day
            and not self.schedule.allows_overnight_shift
        ):
            errors["exit_next_day"] = (
                "El horario no permite turnos que terminen "
                "al día siguiente."
            )

        if self.break_enabled:
            if not self.break_start_time:
                errors["break_start_time"] = (
                    "Debes indicar el inicio del refrigerio."
                )

            if not self.break_end_time:
                errors["break_end_time"] = (
                    "Debes indicar el fin del refrigerio."
                )

        else:
            if (
                self.break_start_time
                or self.break_end_time
            ):
                errors["break_enabled"] = (
                    "Desactiva las horas de refrigerio cuando "
                    "el día no tiene refrigerio."
                )

        if (
            self.break_end_next_day
            and not self.exit_next_day
        ):
            errors["break_end_next_day"] = (
                "El refrigerio no puede terminar al día siguiente "
                "si la jornada termina el mismo día."
            )

        if (
            self.entry_tolerance_minutes is not None
            and self.entry_tolerance_minutes > 180
        ):
            errors["entry_tolerance_minutes"] = (
                "La tolerancia de ingreso no puede superar "
                "180 minutos."
            )

        if (
            self.early_departure_tolerance_minutes
            is not None
            and self.early_departure_tolerance_minutes
            > 180
        ):
            errors[
                "early_departure_tolerance_minutes"
            ] = (
                "La tolerancia de salida no puede superar "
                "180 minutos."
            )

        if (
            self.is_working_day
            and self.entry_time
            and self.exit_time
        ):
            shift_minutes = (
                self.scheduled_shift_minutes
            )

            if shift_minutes > 1440:
                errors["exit_time"] = (
                    "La jornada no puede superar 24 horas."
                )

            if (
                self.break_enabled
                and self.scheduled_break_minutes
                >= shift_minutes
            ):
                errors["break_end_time"] = (
                    "El refrigerio debe ser menor que la "
                    "duración total de la jornada."
                )

            if (
                self.expected_work_minutes
                and self.expected_work_minutes
                > shift_minutes
            ):
                errors["expected_work_minutes"] = (
                    "Los minutos esperados no pueden superar "
                    "la duración total de la jornada."
                )

            if (
                self.minimum_work_minutes
                and self.minimum_work_minutes
                > self.scheduled_work_minutes
            ):
                errors["minimum_work_minutes"] = (
                    "El mínimo de trabajo no puede superar "
                    "los minutos programados."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def archive(self, user=None, reason=""):
        self.is_active = False
        self.archived_at = timezone.now()
        self.archived_by = user
        self.archived_reason = reason
        self.updated_by = user

        self.save(
            update_fields=[
                "is_active",
                "archived_at",
                "archived_by",
                "archived_reason",
                "updated_by",
                "updated_at",
            ]
        )

    def restore(self, user=None):
        self.is_active = True
        self.archived_at = None
        self.archived_by = None
        self.archived_reason = ""
        self.updated_by = user

        self.save(
            update_fields=[
                "is_active",
                "archived_at",
                "archived_by",
                "archived_reason",
                "updated_by",
                "updated_at",
            ]
        )