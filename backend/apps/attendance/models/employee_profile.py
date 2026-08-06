# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class EmployeeProfile(models.Model):
    """
    Configuración laboral y de asistencia de un usuario.

    No reemplaza al modelo User. Mantiene las reglas específicas
    para asistencia, horarios, ubicación, refrigerio y evaluación.
    """

    class EmploymentStatus(models.TextChoices):
        ACTIVE = (
            "active",
            "Activo",
        )
        VACATION = (
            "vacation",
            "De vacaciones",
        )
        LEAVE = (
            "leave",
            "Con licencia",
        )
        SUSPENDED = (
            "suspended",
            "Suspendido",
        )
        TERMINATED = (
            "terminated",
            "Cesado",
        )

    class EmploymentRegime(models.TextChoices):
        GENERAL_PRIVATE = (
            "general_private",
            "Régimen general privado",
        )
        MICRO_ENTERPRISE = (
            "micro_enterprise",
            "Microempresa",
        )
        SMALL_ENTERPRISE = (
            "small_enterprise",
            "Pequeña empresa",
        )
        PART_TIME = (
            "part_time",
            "Tiempo parcial",
        )
        INTERN = (
            "intern",
            "Practicante",
        )
        EXTERNAL = (
            "external",
            "Personal externo",
        )
        OTHER = (
            "other",
            "Otro",
        )

    class AttendanceMode(models.TextChoices):
        NONE = (
            "none",
            "Sin control de asistencia",
        )
        FIXED_DEVICE = (
            "fixed_device",
            "Dispositivo fijo",
        )
        WEB = (
            "web",
            "Navegador web",
        )
        MOBILE = (
            "mobile",
            "Aplicación móvil",
        )
        QR = (
            "qr",
            "Código QR",
        )
        MULTIPLE = (
            "multiple",
            "Varios métodos",
        )

    class WorkMode(models.TextChoices):
        ON_SITE = (
            "on_site",
            "Presencial",
        )
        FIELD = (
            "field",
            "Trabajo de campo",
        )
        REMOTE = (
            "remote",
            "Trabajo remoto",
        )
        HYBRID = (
            "hybrid",
            "Híbrido",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="employee_profile",
        verbose_name="Usuario",
    )

    employee_code = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Código de trabajador",
    )

    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE,
        db_index=True,
        verbose_name="Estado laboral",
    )

    employment_regime = models.CharField(
        max_length=30,
        choices=EmploymentRegime.choices,
        default=EmploymentRegime.GENERAL_PRIVATE,
        db_index=True,
        verbose_name="Régimen laboral",
    )

    work_mode = models.CharField(
        max_length=20,
        choices=WorkMode.choices,
        default=WorkMode.ON_SITE,
        db_index=True,
        verbose_name="Modalidad de trabajo",
    )

    hire_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de ingreso",
    )

    termination_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de cese",
    )

    attendance_enabled = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Control de asistencia activo",
    )

    attendance_mode = models.CharField(
        max_length=20,
        choices=AttendanceMode.choices,
        default=AttendanceMode.MULTIPLE,
        db_index=True,
        verbose_name="Método de asistencia",
    )

    requires_location = models.BooleanField(
        default=False,
        verbose_name="Requiere ubicación",
    )

    requires_photo = models.BooleanField(
        default=False,
        verbose_name="Requiere fotografía",
    )

    can_clock_from_company = models.BooleanField(
        default=True,
        verbose_name="Puede marcar desde la empresa",
    )

    can_clock_from_client = models.BooleanField(
        default=False,
        verbose_name="Puede marcar desde clientes",
    )

    can_clock_remotely = models.BooleanField(
        default=False,
        verbose_name="Puede marcar remotamente",
    )

    can_clock_from_service_order = models.BooleanField(
        default=False,
        verbose_name="Puede marcar desde una orden de servicio",
    )

    allow_fixed_device = models.BooleanField(
        default=True,
        verbose_name="Permitir dispositivo fijo",
    )

    allow_web = models.BooleanField(
        default=True,
        verbose_name="Permitir navegador web",
    )

    allow_mobile = models.BooleanField(
        default=False,
        verbose_name="Permitir aplicación móvil",
    )

    allow_qr = models.BooleanField(
        default=False,
        verbose_name="Permitir código QR",
    )

    track_operational_time = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Controlar tiempo operativo",
        help_text=(
            "Registra tiempos de reparaciones, servicios y "
            "otras actividades asignadas."
        ),
    )

    include_in_staff_evaluation = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Incluir en evaluaciones",
    )

    include_attendance_in_evaluation = models.BooleanField(
        default=True,
        verbose_name="Incluir asistencia en evaluación",
    )

    include_productivity_in_evaluation = models.BooleanField(
        default=True,
        verbose_name="Incluir productividad en evaluación",
    )

    default_break_minutes = models.PositiveSmallIntegerField(
        default=60,
        verbose_name="Minutos de refrigerio",
    )

    entry_tolerance_minutes = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Tolerancia de ingreso en minutos",
    )

    early_departure_tolerance_minutes = (
        models.PositiveSmallIntegerField(
            default=0,
            verbose_name=(
                "Tolerancia de salida anticipada en minutos"
            ),
        )
    )

    weekly_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=48,
        verbose_name="Horas semanales",
    )

    overtime_requires_approval = models.BooleanField(
        default=True,
        verbose_name="Horas extras requieren aprobación",
    )

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="managed_employee_profiles",
        verbose_name="Jefe inmediato",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
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
        related_name="employee_profiles_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="employee_profiles_updated",
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
        related_name="employee_profiles_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Perfil laboral"
        verbose_name_plural = "Perfiles laborales"

        ordering = (
            "user__first_name",
            "user__paternal_last_name",
            "user__maternal_last_name",
        )

        indexes = (
            models.Index(
                fields=(
                    "employment_status",
                    "attendance_enabled",
                ),
                name="att_prof_status_enabled_idx",
            ),
            models.Index(
                fields=(
                    "work_mode",
                    "attendance_mode",
                ),
                name="att_prof_work_attmode_idx",
            ),
            models.Index(
                fields=(
                    "track_operational_time",
                    "include_in_staff_evaluation",
                ),
                name="att_prof_oper_eval_idx",
            ),
            models.Index(
                fields=(
                    "effective_from",
                    "effective_until",
                ),
                name="att_prof_effective_idx",
            ),
        )

        constraints = (
            models.CheckConstraint(
                condition=models.Q(
                    default_break_minutes__lte=300,
                ),
                name="att_prof_break_max_300",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    entry_tolerance_minutes__lte=180,
                ),
                name="att_prof_entry_tol_max_180",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    early_departure_tolerance_minutes__lte=180,
                ),
                name="att_prof_exit_tol_max_180",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    weekly_hours__gte=0,
                )
                & models.Q(
                    weekly_hours__lte=168,
                ),
                name="att_prof_weekly_hours_range",
            ),
        )

    def __str__(self):
        return (
            f"{self.user.full_name} - "
            f"{self.get_employment_status_display()}"
        )

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_current(self):
        today = timezone.localdate()

        if self.archived_at is not None:
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
            self.termination_date
            and self.hire_date
            and self.termination_date < self.hire_date
        ):
            errors["termination_date"] = (
                "La fecha de cese no puede ser anterior "
                "a la fecha de ingreso."
            )

        if (
            self.effective_until
            and self.effective_until < self.effective_from
        ):
            errors["effective_until"] = (
                "La fecha final de vigencia no puede ser "
                "anterior a la fecha inicial."
            )

        if (
            self.manager_id
            and self.manager_id == self.user_id
        ):
            errors["manager"] = (
                "El usuario no puede ser su propio jefe inmediato."
            )

        if (
            self.employment_status
            == self.EmploymentStatus.TERMINATED
            and not self.termination_date
        ):
            errors["termination_date"] = (
                "Debes indicar la fecha de cese."
            )

        if (
            self.attendance_enabled
            and self.attendance_mode
            == self.AttendanceMode.NONE
        ):
            errors["attendance_mode"] = (
                "Selecciona un método de asistencia o desactiva "
                "el control de asistencia."
            )

        if (
            not self.attendance_enabled
            and self.track_operational_time
        ):
            errors["track_operational_time"] = (
                "No puedes controlar tiempos operativos si el "
                "control de asistencia está desactivado."
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