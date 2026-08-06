# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class HolidayCalendar(models.Model):
    """
    Calendario laboral aplicable a una empresa, sede o grupo.

    Permite manejar:

    - Feriados nacionales del Perú.
    - Feriados regionales o locales.
    - Días no laborables.
    - Días compensables.
    - Cierres internos.
    - Jornadas especiales.
    """

    class CalendarType(models.TextChoices):
        NATIONAL = (
            "national",
            "Calendario nacional",
        )
        COMPANY = (
            "company",
            "Calendario de empresa",
        )
        REGIONAL = (
            "regional",
            "Calendario regional",
        )
        LOCATION = (
            "location",
            "Calendario por ubicación",
        )
        SPECIAL = (
            "special",
            "Calendario especial",
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

    calendar_type = models.CharField(
        max_length=20,
        choices=CalendarType.choices,
        default=CalendarType.NATIONAL,
        db_index=True,
        verbose_name="Tipo de calendario",
    )

    country_code = models.CharField(
        max_length=2,
        default="PE",
        db_index=True,
        verbose_name="Código de país",
    )

    region = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Departamento",
    )

    province = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Provincia",
    )

    district = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Distrito",
    )

    work_location = models.ForeignKey(
        "attendance.WorkLocation",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="holiday_calendars",
        verbose_name="Ubicación de trabajo",
    )

    effective_from = models.DateField(
        db_index=True,
        verbose_name="Vigente desde",
    )

    effective_until = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Vigente hasta",
    )

    is_default = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Calendario predeterminado",
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
        related_name="attendance_holiday_calendars_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_holiday_calendars_updated",
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
        related_name="attendance_holiday_calendars_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Calendario laboral"
        verbose_name_plural = "Calendarios laborales"

        ordering = (
            "-is_default",
            "name",
        )

        indexes = (
            models.Index(
                fields=(
                    "calendar_type",
                    "is_active",
                ),
                name="att_hcal_type_active_idx",
            ),
            models.Index(
                fields=(
                    "country_code",
                    "region",
                    "province",
                    "district",
                ),
                name="att_hcal_geo_idx",
            ),
            models.Index(
                fields=(
                    "effective_from",
                    "effective_until",
                ),
                name="att_hcal_effective_idx",
            ),
            models.Index(
                fields=(
                    "work_location",
                    "is_default",
                ),
                name="att_hcal_location_def_idx",
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
            self.calendar_type
            == self.CalendarType.LOCATION
            and not self.work_location_id
        ):
            errors["work_location"] = (
                "Un calendario por ubicación debe estar "
                "vinculado a una ubicación de trabajo."
            )

        if (
            self.work_location_id
            and self.work_location.archived_at
        ):
            errors["work_location"] = (
                "La ubicación de trabajo está archivada."
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


class HolidayCalendarDay(models.Model):
    """
    Día especial dentro de un calendario laboral.
    """

    class DayType(models.TextChoices):
        NATIONAL_HOLIDAY = (
            "national_holiday",
            "Feriado nacional",
        )
        REGIONAL_HOLIDAY = (
            "regional_holiday",
            "Feriado regional",
        )
        LOCAL_HOLIDAY = (
            "local_holiday",
            "Feriado local",
        )
        NON_WORKING_DAY = (
            "non_working_day",
            "Día no laborable",
        )
        COMPENSABLE_DAY = (
            "compensable_day",
            "Día compensable",
        )
        COMPANY_CLOSURE = (
            "company_closure",
            "Cierre de empresa",
        )
        SPECIAL_WORKDAY = (
            "special_workday",
            "Jornada laboral especial",
        )
        ELECTION_DAY = (
            "election_day",
            "Jornada electoral",
        )
        OTHER = (
            "other",
            "Otro",
        )

    class CompensationMode(models.TextChoices):
        NONE = (
            "none",
            "No requiere compensación",
        )
        HOURS = (
            "hours",
            "Compensación por horas",
        )
        FULL_DAY = (
            "full_day",
            "Compensación por día completo",
        )
        SUBSTITUTE_REST = (
            "substitute_rest",
            "Descanso sustitutorio",
        )
        COMPANY_AGREEMENT = (
            "company_agreement",
            "Según acuerdo con la empresa",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    calendar = models.ForeignKey(
        HolidayCalendar,
        on_delete=models.CASCADE,
        related_name="days",
        verbose_name="Calendario",
    )

    date = models.DateField(
        db_index=True,
        verbose_name="Fecha",
    )

    name = models.CharField(
        max_length=200,
        verbose_name="Nombre",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    day_type = models.CharField(
        max_length=30,
        choices=DayType.choices,
        default=DayType.NATIONAL_HOLIDAY,
        db_index=True,
        verbose_name="Tipo de día",
    )

    is_working_day = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Es día laborable",
    )

    is_paid = models.BooleanField(
        default=True,
        verbose_name="Es remunerado",
    )

    requires_compensation = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere compensación",
    )

    compensation_mode = models.CharField(
        max_length=30,
        choices=CompensationMode.choices,
        default=CompensationMode.NONE,
        verbose_name="Forma de compensación",
    )

    compensation_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos a compensar",
    )

    substitute_rest_required = models.BooleanField(
        default=False,
        verbose_name="Requiere descanso sustitutorio",
    )

    special_entry_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora especial de ingreso",
    )

    special_exit_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora especial de salida",
    )

    special_break_minutes = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Refrigerio especial en minutos",
    )

    applies_to_private_sector = models.BooleanField(
        default=True,
        verbose_name="Aplica al sector privado",
    )

    legal_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Referencia legal",
    )

    source_url = models.URLField(
        blank=True,
        verbose_name="Fuente oficial",
    )

    notes = models.TextField(
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
        related_name="attendance_holiday_days_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_holiday_days_updated",
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
        related_name="attendance_holiday_days_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Día de calendario laboral"
        verbose_name_plural = "Días de calendarios laborales"

        ordering = (
            "date",
            "name",
        )

        constraints = (
            models.UniqueConstraint(
                fields=(
                    "calendar",
                    "date",
                ),
                condition=models.Q(
                    archived_at__isnull=True,
                ),
                name="att_hcal_day_unique_active",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    compensation_minutes__lte=1440,
                ),
                name="att_hcal_comp_min_max",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        special_break_minutes__isnull=True,
                    )
                    | models.Q(
                        special_break_minutes__lte=300,
                    )
                ),
                name="att_hcal_break_max",
            ),
        )

        indexes = (
            models.Index(
                fields=(
                    "calendar",
                    "date",
                    "is_active",
                ),
                name="att_hcal_day_date_idx",
            ),
            models.Index(
                fields=(
                    "day_type",
                    "requires_compensation",
                ),
                name="att_hcal_day_type_comp_idx",
            ),
            models.Index(
                fields=(
                    "is_working_day",
                    "is_paid",
                ),
                name="att_hcal_day_work_paid_idx",
            ),
        )

    def __str__(self):
        return f"{self.date} - {self.name}"

    @property
    def is_archived(self):
        return self.archived_at is not None

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.calendar_id
            and self.date < self.calendar.effective_from
        ):
            errors["date"] = (
                "La fecha no puede ser anterior al inicio "
                "del calendario."
            )

        if (
            self.calendar_id
            and self.calendar.effective_until
            and self.date > self.calendar.effective_until
        ):
            errors["date"] = (
                "La fecha no puede ser posterior al fin "
                "del calendario."
            )

        if (
            self.requires_compensation
            and self.compensation_mode
            == self.CompensationMode.NONE
        ):
            errors["compensation_mode"] = (
                "Debes indicar cómo se realizará la compensación."
            )

        if (
            not self.requires_compensation
            and self.compensation_mode
            != self.CompensationMode.NONE
        ):
            errors["compensation_mode"] = (
                "No debes configurar una compensación cuando "
                "el día no la requiere."
            )

        if (
            self.compensation_mode
            == self.CompensationMode.HOURS
            and self.compensation_minutes <= 0
        ):
            errors["compensation_minutes"] = (
                "Debes indicar los minutos que deben compensarse."
            )

        if (
            self.compensation_mode
            != self.CompensationMode.HOURS
            and self.compensation_minutes
        ):
            errors["compensation_minutes"] = (
                "Los minutos solo corresponden a una "
                "compensación por horas."
            )

        if (
            self.substitute_rest_required
            and self.compensation_mode
            != self.CompensationMode.SUBSTITUTE_REST
        ):
            errors["compensation_mode"] = (
                "Selecciona descanso sustitutorio como "
                "forma de compensación."
            )

        has_special_times = (
            self.special_entry_time
            or self.special_exit_time
        )

        if (
            self.is_working_day
            and has_special_times
            and (
                not self.special_entry_time
                or not self.special_exit_time
            )
        ):
            errors["special_entry_time"] = (
                "Debes indicar tanto la hora de ingreso como "
                "la hora de salida especial."
            )

        if (
            not self.is_working_day
            and has_special_times
        ):
            errors["is_working_day"] = (
                "Un día no laborable no debe tener horario especial."
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