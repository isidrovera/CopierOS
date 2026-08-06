# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .employee_profile import EmployeeProfile
from .work_location import WorkLocation
from .work_schedule import WorkSchedule


class EmployeeScheduleAssignment(models.Model):
    """
    Asigna un horario laboral a un trabajador durante un periodo.

    Permite:

    - Cambiar horarios sin perder el historial.
    - Asignar horarios temporales.
    - Definir una sede principal.
    - Autorizar varias ubicaciones de marcación.
    - Aplicar tolerancias particulares.
    - Suspender temporalmente la obligación de asistencia.
    """

    class AssignmentType(models.TextChoices):
        PERMANENT = (
            "permanent",
            "Permanente",
        )
        TEMPORARY = (
            "temporary",
            "Temporal",
        )
        REPLACEMENT = (
            "replacement",
            "Reemplazo",
        )
        ROTATION = (
            "rotation",
            "Rotación",
        )
        SPECIAL = (
            "special",
            "Especial",
        )

    class AssignmentStatus(models.TextChoices):
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
        related_name="schedule_assignments",
        verbose_name="Perfil laboral",
    )

    schedule = models.ForeignKey(
        WorkSchedule,
        on_delete=models.PROTECT,
        related_name="employee_assignments",
        verbose_name="Horario",
    )

    assignment_type = models.CharField(
        max_length=20,
        choices=AssignmentType.choices,
        default=AssignmentType.PERMANENT,
        db_index=True,
        verbose_name="Tipo de asignación",
    )

    status = models.CharField(
        max_length=20,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    primary_location = models.ForeignKey(
        WorkLocation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="primary_schedule_assignments",
        verbose_name="Ubicación principal",
    )

    allowed_locations = models.ManyToManyField(
        WorkLocation,
        blank=True,
        related_name="allowed_schedule_assignments",
        verbose_name="Ubicaciones autorizadas",
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

    attendance_required = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Requiere asistencia",
    )

    operational_time_required = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere control de tiempo operativo",
    )

    location_required = models.BooleanField(
        default=False,
        verbose_name="Requiere ubicación",
    )

    photo_required = models.BooleanField(
        default=False,
        verbose_name="Requiere fotografía",
    )

    allow_company_clocking = models.BooleanField(
        default=True,
        verbose_name="Permitir marcación en la empresa",
    )

    allow_client_clocking = models.BooleanField(
        default=False,
        verbose_name="Permitir marcación en clientes",
    )

    allow_remote_clocking = models.BooleanField(
        default=False,
        verbose_name="Permitir marcación remota",
    )

    allow_service_order_clocking = models.BooleanField(
        default=False,
        verbose_name="Permitir marcación desde servicios",
    )

    override_entry_tolerance = models.BooleanField(
        default=False,
        verbose_name="Modificar tolerancia de ingreso",
    )

    entry_tolerance_minutes = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Tolerancia de ingreso",
    )

    override_early_departure_tolerance = models.BooleanField(
        default=False,
        verbose_name="Modificar tolerancia de salida",
    )

    early_departure_tolerance_minutes = (
        models.PositiveSmallIntegerField(
            null=True,
            blank=True,
            verbose_name="Tolerancia de salida anticipada",
        )
    )

    override_break_minutes = models.BooleanField(
        default=False,
        verbose_name="Modificar minutos de refrigerio",
    )

    break_minutes = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Minutos de refrigerio",
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
        related_name="attendance_schedule_assignments_activated",
        verbose_name="Activada por",
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
        related_name="attendance_schedule_assignments_cancelled",
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
        related_name="attendance_schedule_assignments_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_schedule_assignments_updated",
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
        related_name="attendance_schedule_assignments_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Asignación de horario"
        verbose_name_plural = "Asignaciones de horarios"

        ordering = (
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
                name="att_asg_emp_status_from_idx",
            ),
            models.Index(
                fields=(
                    "schedule",
                    "status",
                ),
                name="att_asg_sched_status_idx",
            ),
            models.Index(
                fields=(
                    "primary_location",
                    "status",
                ),
                name="att_asg_location_status_idx",
            ),
            models.Index(
                fields=(
                    "effective_from",
                    "effective_until",
                ),
                name="att_asg_effective_idx",
            ),
            models.Index(
                fields=(
                    "attendance_required",
                    "operational_time_required",
                ),
                name="att_asg_att_oper_idx",
            ),
        )

        constraints = (
            models.CheckConstraint(
                condition=(
                    models.Q(
                        entry_tolerance_minutes__isnull=True,
                    )
                    | models.Q(
                        entry_tolerance_minutes__lte=180,
                    )
                ),
                name="att_asg_entry_tol_max_180",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        early_departure_tolerance_minutes__isnull=True,
                    )
                    | models.Q(
                        early_departure_tolerance_minutes__lte=180,
                    )
                ),
                name="att_asg_exit_tol_max_180",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        break_minutes__isnull=True,
                    )
                    | models.Q(
                        break_minutes__lte=300,
                    )
                ),
                name="att_asg_break_max_300",
            ),
        )

    def __str__(self):
        return (
            f"{self.employee_profile.user.full_name} - "
            f"{self.schedule.name}"
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

        if self.status != self.AssignmentStatus.ACTIVE:
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
    def effective_entry_tolerance_minutes(self):
        if (
            self.override_entry_tolerance
            and self.entry_tolerance_minutes is not None
        ):
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
            self.override_early_departure_tolerance
            and self.early_departure_tolerance_minutes
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
    def effective_break_minutes(self):
        if (
            self.override_break_minutes
            and self.break_minutes is not None
        ):
            return self.break_minutes

        return (
            self.employee_profile
            .default_break_minutes
        )

    def overlaps_with_existing_assignment(self):
        queryset = (
            EmployeeScheduleAssignment.objects
            .filter(
                employee_profile=self.employee_profile,
                archived_at__isnull=True,
            )
            .exclude(
                pk=self.pk,
            )
            .exclude(
                status__in=(
                    self.AssignmentStatus.CANCELLED,
                    self.AssignmentStatus.FINISHED,
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
                "No puedes asignar un horario a un "
                "perfil laboral archivado."
            )

        if (
            self.schedule_id
            and not self.schedule.is_active
        ):
            errors["schedule"] = (
                "No puedes asignar un horario inactivo."
            )

        if (
            self.schedule_id
            and self.schedule.archived_at
        ):
            errors["schedule"] = (
                "No puedes asignar un horario archivado."
            )

        if (
            self.primary_location_id
            and not self.primary_location.is_active
        ):
            errors["primary_location"] = (
                "La ubicación principal está inactiva."
            )

        if (
            self.primary_location_id
            and self.primary_location.archived_at
        ):
            errors["primary_location"] = (
                "La ubicación principal está archivada."
            )

        if (
            self.location_required
            and not self.primary_location_id
            and not self.pk
        ):
            errors["primary_location"] = (
                "Debes indicar una ubicación principal "
                "cuando la marcación requiere ubicación."
            )

        if (
            self.override_entry_tolerance
            and self.entry_tolerance_minutes is None
        ):
            errors["entry_tolerance_minutes"] = (
                "Debes indicar la tolerancia de ingreso."
            )

        if (
            not self.override_entry_tolerance
            and self.entry_tolerance_minutes is not None
        ):
            errors["entry_tolerance_minutes"] = (
                "Activa la modificación de tolerancia "
                "antes de ingresar un valor."
            )

        if (
            self.override_early_departure_tolerance
            and self.early_departure_tolerance_minutes
            is None
        ):
            errors[
                "early_departure_tolerance_minutes"
            ] = (
                "Debes indicar la tolerancia de salida."
            )

        if (
            not self.override_early_departure_tolerance
            and self.early_departure_tolerance_minutes
            is not None
        ):
            errors[
                "early_departure_tolerance_minutes"
            ] = (
                "Activa la modificación de tolerancia "
                "antes de ingresar un valor."
            )

        if (
            self.override_break_minutes
            and self.break_minutes is None
        ):
            errors["break_minutes"] = (
                "Debes indicar los minutos de refrigerio."
            )

        if (
            not self.override_break_minutes
            and self.break_minutes is not None
        ):
            errors["break_minutes"] = (
                "Activa la modificación del refrigerio "
                "antes de ingresar un valor."
            )

        if (
            self.operational_time_required
            and not self.employee_profile
            .track_operational_time
        ):
            errors["operational_time_required"] = (
                "El perfil laboral no tiene habilitado el "
                "control de tiempo operativo."
            )

        if (
            self.attendance_required
            and not self.employee_profile
            .attendance_enabled
        ):
            errors["attendance_required"] = (
                "El perfil laboral no tiene habilitado el "
                "control de asistencia."
            )

        if (
            self.status
            in (
                self.AssignmentStatus.SCHEDULED,
                self.AssignmentStatus.ACTIVE,
            )
            and self.employee_profile_id
            and self.effective_from
            and self.overlaps_with_existing_assignment()
        ):
            errors["effective_from"] = (
                "El trabajador ya tiene otra asignación "
                "de horario vigente en esas fechas."
            )

        if (
            self.status
            == self.AssignmentStatus.CANCELLED
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

        if self.status == self.AssignmentStatus.CANCELLED:
            raise ValidationError(
                "No puedes activar una asignación cancelada."
            )

        if self.overlaps_with_existing_assignment():
            raise ValidationError(
                "El trabajador ya tiene otra asignación "
                "vigente en las mismas fechas."
            )

        today = timezone.localdate()

        if self.effective_from > today:
            self.status = self.AssignmentStatus.SCHEDULED
        else:
            self.status = self.AssignmentStatus.ACTIVE

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
        if self.status == self.AssignmentStatus.CANCELLED:
            raise ValidationError(
                "Una asignación cancelada no puede finalizarse."
            )

        if self.status == self.AssignmentStatus.FINISHED:
            return

        today = timezone.localdate()

        if (
            not self.effective_until
            or self.effective_until > today
        ):
            self.effective_until = today

        self.status = self.AssignmentStatus.FINISHED
        self.updated_by = user

        self.save(
            update_fields=[
                "effective_until",
                "status",
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

        if self.status == self.AssignmentStatus.FINISHED:
            raise ValidationError(
                "Una asignación finalizada no puede cancelarse."
            )

        self.status = self.AssignmentStatus.CANCELLED
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
        if self.status == self.AssignmentStatus.ACTIVE:
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