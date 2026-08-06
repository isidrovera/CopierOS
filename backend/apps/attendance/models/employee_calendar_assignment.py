# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .employee_profile import EmployeeProfile
from .holiday_calendar import HolidayCalendar


class EmployeeCalendarAssignment(models.Model):
    """
    Asigna un calendario laboral a un trabajador.

    Permite conservar el historial cuando el trabajador:

    - Cambia de empresa.
    - Cambia de sede.
    - Cambia de ciudad.
    - Usa un calendario especial.
    - Tiene excepciones temporales.
    """

    class AssignmentType(models.TextChoices):
        NATIONAL = (
            "national",
            "Calendario nacional",
        )
        COMPANY = (
            "company",
            "Calendario de empresa",
        )
        LOCATION = (
            "location",
            "Calendario de ubicación",
        )
        TEMPORARY = (
            "temporary",
            "Asignación temporal",
        )
        SPECIAL = (
            "special",
            "Asignación especial",
        )

    class Status(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        SCHEDULED = (
            "scheduled",
            "Programada",
        )
        ACTIVE = (
            "active",
            "Activa",
        )
        FINISHED = (
            "finished",
            "Finalizada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
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
        related_name="calendar_assignments",
        verbose_name="Perfil laboral",
    )

    calendar = models.ForeignKey(
        HolidayCalendar,
        on_delete=models.PROTECT,
        related_name="employee_assignments",
        verbose_name="Calendario laboral",
    )

    assignment_type = models.CharField(
        max_length=20,
        choices=AssignmentType.choices,
        default=AssignmentType.NATIONAL,
        db_index=True,
        verbose_name="Tipo de asignación",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
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

    priority = models.PositiveSmallIntegerField(
        default=100,
        db_index=True,
        verbose_name="Prioridad",
        help_text=(
            "Un valor menor tiene mayor prioridad cuando existen "
            "varios calendarios aplicables."
        ),
    )

    apply_national_holidays = models.BooleanField(
        default=True,
        verbose_name="Aplicar feriados nacionales",
    )

    apply_regional_holidays = models.BooleanField(
        default=True,
        verbose_name="Aplicar feriados regionales",
    )

    apply_local_holidays = models.BooleanField(
        default=True,
        verbose_name="Aplicar feriados locales",
    )

    apply_non_working_days = models.BooleanField(
        default=True,
        verbose_name="Aplicar días no laborables",
    )

    apply_company_closures = models.BooleanField(
        default=True,
        verbose_name="Aplicar cierres de empresa",
    )

    apply_special_workdays = models.BooleanField(
        default=True,
        verbose_name="Aplicar jornadas especiales",
    )

    override_default_calendar = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Reemplazar calendario predeterminado",
        help_text=(
            "Cuando está activo, este calendario reemplaza otros "
            "calendarios de menor prioridad."
        ),
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
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
        related_name="attendance_calendar_assignments_activated",
        verbose_name="Activada por",
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Finalizada el",
    )

    finished_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_calendar_assignments_finished",
        verbose_name="Finalizada por",
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
        related_name="attendance_calendar_assignments_cancelled",
        verbose_name="Cancelada por",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
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
        related_name="attendance_calendar_assignments_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_calendar_assignments_updated",
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
        related_name="attendance_calendar_assignments_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Asignación de calendario laboral"
        verbose_name_plural = (
            "Asignaciones de calendarios laborales"
        )

        ordering = (
            "priority",
            "-effective_from",
            "-created_at",
        )

        indexes = (
            models.Index(
                fields=(
                    "employee_profile",
                    "status",
                    "effective_from",
                ),
                name="att_calasg_emp_status_idx",
            ),
            models.Index(
                fields=(
                    "calendar",
                    "status",
                ),
                name="att_calasg_cal_status_idx",
            ),
            models.Index(
                fields=(
                    "effective_from",
                    "effective_until",
                ),
                name="att_calasg_effective_idx",
            ),
            models.Index(
                fields=(
                    "priority",
                    "override_default_calendar",
                ),
                name="att_calasg_priority_idx",
            ),
        )

        constraints = (
            models.CheckConstraint(
                condition=models.Q(
                    priority__lte=1000,
                ),
                name="att_calasg_priority_max",
            ),
        )

    def __str__(self):
        return (
            f"{self.employee_profile.user.full_name} - "
            f"{self.calendar.name}"
        )

    @property
    def employee(self):
        return self.employee_profile.user

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_current(self):
        today = timezone.localdate()

        if self.archived_at is not None:
            return False

        if self.status != self.Status.ACTIVE:
            return False

        if self.effective_from > today:
            return False

        if (
            self.effective_until
            and self.effective_until < today
        ):
            return False

        return True

    def overlaps_with_existing_assignment(self):
        queryset = (
            EmployeeCalendarAssignment.objects
            .filter(
                employee_profile=self.employee_profile,
                archived_at__isnull=True,
            )
            .exclude(
                pk=self.pk,
            )
            .exclude(
                status__in=(
                    self.Status.CANCELLED,
                    self.Status.FINISHED,
                ),
            )
        )

        if self.effective_until:
            queryset = queryset.filter(
                effective_from__lte=self.effective_until,
            )

        queryset = queryset.filter(
            models.Q(
                effective_until__isnull=True,
            )
            | models.Q(
                effective_until__gte=self.effective_from,
            )
        )

        if self.override_default_calendar:
            queryset = queryset.filter(
                override_default_calendar=True,
            )

        return queryset.exists()

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
            self.assignment_type
            == self.AssignmentType.TEMPORARY
            and not self.effective_until
        ):
            errors["effective_until"] = (
                "Una asignación temporal debe tener "
                "fecha de finalización."
            )

        if (
            self.employee_profile_id
            and self.employee_profile.archived_at
        ):
            errors["employee_profile"] = (
                "No puedes asignar un calendario a un "
                "perfil laboral archivado."
            )

        if (
            self.calendar_id
            and self.calendar.archived_at
        ):
            errors["calendar"] = (
                "No puedes asignar un calendario archivado."
            )

        if (
            self.calendar_id
            and not self.calendar.is_active
        ):
            errors["calendar"] = (
                "No puedes asignar un calendario inactivo."
            )

        if (
            self.calendar_id
            and self.effective_from
            < self.calendar.effective_from
        ):
            errors["effective_from"] = (
                "La asignación no puede iniciar antes de la "
                "vigencia del calendario."
            )

        if (
            self.calendar_id
            and self.calendar.effective_until
            and (
                not self.effective_until
                or self.effective_until
                > self.calendar.effective_until
            )
        ):
            errors["effective_until"] = (
                "La asignación no puede superar la fecha final "
                "del calendario."
            )

        if not any(
            (
                self.apply_national_holidays,
                self.apply_regional_holidays,
                self.apply_local_holidays,
                self.apply_non_working_days,
                self.apply_company_closures,
                self.apply_special_workdays,
            )
        ):
            errors["apply_national_holidays"] = (
                "Debes seleccionar al menos un tipo de día "
                "para aplicar."
            )

        if (
            self.status
            in (
                self.Status.SCHEDULED,
                self.Status.ACTIVE,
            )
            and self.employee_profile_id
            and self.calendar_id
            and self.effective_from
            and self.overlaps_with_existing_assignment()
        ):
            errors["effective_from"] = (
                "El trabajador ya tiene otra asignación que "
                "reemplaza el calendario predeterminado durante "
                "esas fechas."
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
        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def activate(self, user=None):
        if self.archived_at is not None:
            raise ValidationError(
                "No puedes activar una asignación archivada."
            )

        if self.status == self.Status.CANCELLED:
            raise ValidationError(
                "No puedes activar una asignación cancelada."
            )

        if self.overlaps_with_existing_assignment():
            raise ValidationError(
                "Existe otra asignación de calendario incompatible "
                "durante las mismas fechas."
            )

        today = timezone.localdate()

        if self.effective_from > today:
            self.status = self.Status.SCHEDULED
        else:
            self.status = self.Status.ACTIVE

        self.activated_at = timezone.now()
        self.activated_by = user
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "activated_at",
                "activated_by",
                "updated_by",
                "updated_at",
            ]
        )

    def finish(self, user=None):
        if self.status == self.Status.CANCELLED:
            raise ValidationError(
                "Una asignación cancelada no puede finalizarse."
            )

        if self.status == self.Status.FINISHED:
            return

        today = timezone.localdate()

        if (
            not self.effective_until
            or self.effective_until > today
        ):
            self.effective_until = today

        self.status = self.Status.FINISHED
        self.finished_at = timezone.now()
        self.finished_by = user
        self.updated_by = user

        self.save(
            update_fields=[
                "effective_until",
                "status",
                "finished_at",
                "finished_by",
                "updated_by",
                "updated_at",
            ]
        )

    def cancel(self, user=None, reason=""):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de cancelación."
            )

        if self.status == self.Status.FINISHED:
            raise ValidationError(
                "Una asignación finalizada no puede cancelarse."
            )

        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancelled_by = user
        self.cancellation_reason = reason
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "cancelled_at",
                "cancelled_by",
                "cancellation_reason",
                "updated_by",
                "updated_at",
            ]
        )

    def archive(self, user=None, reason=""):
        if self.status == self.Status.ACTIVE:
            raise ValidationError(
                "No puedes archivar una asignación activa. "
                "Primero debes finalizarla o cancelarla."
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