# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .attendance_device import AttendanceDevice
from .employee_profile import EmployeeProfile


class EmployeeDevicePermission(models.Model):
    """
    Autoriza a un trabajador a utilizar un dispositivo de asistencia.

    Permite controlar:

    - Qué usuarios pueden marcar en una tablet compartida.
    - Qué usuario puede usar un dispositivo personal.
    - Marcación de asistencia.
    - Marcación de refrigerio.
    - Registro de tiempos operativos.
    - Fechas de vigencia.
    - Bloqueo individual sin desactivar el dispositivo completo.
    """

    class PermissionStatus(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        SCHEDULED = (
            "scheduled",
            "Programado",
        )
        ACTIVE = (
            "active",
            "Activo",
        )
        SUSPENDED = (
            "suspended",
            "Suspendido",
        )
        FINISHED = (
            "finished",
            "Finalizado",
        )
        REVOKED = (
            "revoked",
            "Revocado",
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
        related_name="device_permissions",
        verbose_name="Perfil laboral",
    )

    device = models.ForeignKey(
        AttendanceDevice,
        on_delete=models.PROTECT,
        related_name="employee_permissions",
        verbose_name="Dispositivo",
    )

    status = models.CharField(
        max_length=20,
        choices=PermissionStatus.choices,
        default=PermissionStatus.DRAFT,
        db_index=True,
        verbose_name="Estado",
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

    allow_attendance_clocking = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Permitir asistencia",
    )

    allow_break_clocking = models.BooleanField(
        default=True,
        verbose_name="Permitir refrigerio",
    )

    allow_operational_clocking = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Permitir actividad operativa",
    )

    allow_company_clocking = models.BooleanField(
        default=True,
        verbose_name="Permitir marcación en empresa",
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

    requires_pin = models.BooleanField(
        default=False,
        verbose_name="Requiere PIN",
    )

    pin_hash = models.CharField(
        max_length=128,
        blank=True,
        editable=False,
        verbose_name="Hash del PIN",
    )

    requires_photo = models.BooleanField(
        default=False,
        verbose_name="Requiere fotografía",
    )

    requires_location = models.BooleanField(
        default=False,
        verbose_name="Requiere ubicación",
    )

    maximum_daily_clockings = models.PositiveSmallIntegerField(
        default=20,
        verbose_name="Máximo de marcaciones por día",
    )

    minimum_seconds_between_clockings = (
        models.PositiveIntegerField(
            default=30,
            verbose_name=(
                "Segundos mínimos entre marcaciones"
            ),
        )
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Activado el",
    )

    activated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_device_permissions_activated",
        verbose_name="Activado por",
    )

    suspended_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Suspendido el",
    )

    suspended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_device_permissions_suspended",
        verbose_name="Suspendido por",
    )

    suspension_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de suspensión",
    )

    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Revocado el",
    )

    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_device_permissions_revoked",
        verbose_name="Revocado por",
    )

    revocation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de revocación",
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Finalizado el",
    )

    finished_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_device_permissions_finished",
        verbose_name="Finalizado por",
    )

    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Último uso",
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
        related_name="attendance_device_permissions_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_device_permissions_updated",
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
        related_name="attendance_device_permissions_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Permiso de dispositivo"
        verbose_name_plural = "Permisos de dispositivos"

        ordering = (
            "employee_profile",
            "device",
            "-effective_from",
        )

        indexes = (
            models.Index(
                fields=(
                    "employee_profile",
                    "status",
                ),
                name="att_devperm_emp_status_idx",
            ),
            models.Index(
                fields=(
                    "device",
                    "status",
                ),
                name="att_devperm_dev_status_idx",
            ),
            models.Index(
                fields=(
                    "effective_from",
                    "effective_until",
                ),
                name="att_devperm_effective_idx",
            ),
            models.Index(
                fields=(
                    "allow_attendance_clocking",
                    "allow_operational_clocking",
                ),
                name="att_devperm_att_oper_idx",
            ),
            models.Index(
                fields=(
                    "last_used_at",
                    "status",
                ),
                name="att_devperm_used_status_idx",
            ),
        )

        constraints = (
            models.UniqueConstraint(
                fields=(
                    "employee_profile",
                    "device",
                    "effective_from",
                ),
                condition=models.Q(
                    archived_at__isnull=True,
                ),
                name="att_devperm_unique_active",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        maximum_daily_clockings__gte=1,
                    )
                    & models.Q(
                        maximum_daily_clockings__lte=200,
                    )
                ),
                name="att_devperm_daily_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        minimum_seconds_between_clockings__gte=0,
                    )
                    & models.Q(
                        minimum_seconds_between_clockings__lte=3600,
                    )
                ),
                name="att_devperm_interval_range",
            ),
        )

    def __str__(self):
        return (
            f"{self.employee_profile.user.full_name} - "
            f"{self.device.name}"
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

        if self.status != self.PermissionStatus.ACTIVE:
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
    def can_be_used(self):
        return (
            self.is_current
            and self.device.can_clock
            and self.employee_profile.attendance_enabled
            and self.employee_profile.employment_status
            == self.employee_profile.EmploymentStatus.ACTIVE
        )

    def overlaps_with_existing_permission(self):
        queryset = (
            EmployeeDevicePermission.objects
            .filter(
                employee_profile=self.employee_profile,
                device=self.device,
                archived_at__isnull=True,
            )
            .exclude(
                pk=self.pk,
            )
            .exclude(
                status__in=(
                    self.PermissionStatus.FINISHED,
                    self.PermissionStatus.REVOKED,
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
            self.employee_profile_id
            and self.employee_profile.archived_at
        ):
            errors["employee_profile"] = (
                "El perfil laboral está archivado."
            )

        if (
            self.device_id
            and self.device.archived_at
        ):
            errors["device"] = (
                "El dispositivo está archivado."
            )

        if (
            self.device_id
            and not self.device.is_active
        ):
            errors["device"] = (
                "El dispositivo está inactivo."
            )

        if (
            self.device_id
            and not self.device.allows_multiple_users
            and self.device.assigned_user_id
            and self.employee_profile_id
            and self.device.assigned_user_id
            != self.employee_profile.user_id
        ):
            errors["device"] = (
                "El dispositivo está asignado a otro usuario."
            )

        if (
            self.allow_attendance_clocking
            and self.device_id
            and not self.device.allows_attendance_clocking
        ):
            errors["allow_attendance_clocking"] = (
                "El dispositivo no permite asistencia."
            )

        if (
            self.allow_break_clocking
            and self.device_id
            and not self.device.allows_break_clocking
        ):
            errors["allow_break_clocking"] = (
                "El dispositivo no permite refrigerio."
            )

        if (
            self.allow_operational_clocking
            and self.device_id
            and not self.device.allows_operational_clocking
        ):
            errors["allow_operational_clocking"] = (
                "El dispositivo no permite tiempos operativos."
            )

        if (
            self.allow_operational_clocking
            and self.employee_profile_id
            and not self.employee_profile.track_operational_time
        ):
            errors["allow_operational_clocking"] = (
                "El perfil laboral no tiene habilitado "
                "el control de tiempo operativo."
            )

        if (
            self.requires_location
            and self.device_id
            and not self.device.requires_location
            and not self.device.work_location_id
        ):
            errors["requires_location"] = (
                "El dispositivo no tiene ubicación configurada."
            )

        if (
            self.requires_pin
            and not self.pin_hash
            and self.pk
        ):
            errors["pin_hash"] = (
                "Debes configurar un PIN para este permiso."
            )

        if (
            self.status
            in (
                self.PermissionStatus.SCHEDULED,
                self.PermissionStatus.ACTIVE,
            )
            and self.employee_profile_id
            and self.device_id
            and self.effective_from
            and self.overlaps_with_existing_permission()
        ):
            errors["effective_from"] = (
                "Ya existe un permiso vigente para este "
                "trabajador y dispositivo."
            )

        if (
            self.status
            == self.PermissionStatus.SUSPENDED
            and not self.suspension_reason.strip()
        ):
            errors["suspension_reason"] = (
                "Debes indicar el motivo de suspensión."
            )

        if (
            self.status
            == self.PermissionStatus.REVOKED
            and not self.revocation_reason.strip()
        ):
            errors["revocation_reason"] = (
                "Debes indicar el motivo de revocación."
            )

        if not any(
            (
                self.allow_attendance_clocking,
                self.allow_break_clocking,
                self.allow_operational_clocking,
            )
        ):
            errors["allow_attendance_clocking"] = (
                "Debes habilitar al menos un tipo de marcación."
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
                "No puedes activar un permiso archivado."
            )

        if self.status == self.PermissionStatus.REVOKED:
            raise ValidationError(
                "No puedes activar un permiso revocado."
            )

        if self.overlaps_with_existing_permission():
            raise ValidationError(
                "Ya existe otro permiso vigente para el "
                "mismo trabajador y dispositivo."
            )

        today = timezone.localdate()

        if self.effective_from > today:
            self.status = (
                self.PermissionStatus.SCHEDULED
            )
        else:
            self.status = (
                self.PermissionStatus.ACTIVE
            )

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

    def suspend(self, user=None, reason=""):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de suspensión."
            )

        if self.status != self.PermissionStatus.ACTIVE:
            raise ValidationError(
                "Solo puedes suspender un permiso activo."
            )

        self.status = (
            self.PermissionStatus.SUSPENDED
        )

        self.suspended_at = timezone.now()
        self.suspended_by = user
        self.suspension_reason = reason
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "suspended_at",
                "suspended_by",
                "suspension_reason",
                "updated_by",
                "updated_at",
            ]
        )

    def resume(self, user=None):
        if self.status != self.PermissionStatus.SUSPENDED:
            raise ValidationError(
                "El permiso no está suspendido."
            )

        if (
            self.effective_until
            and self.effective_until
            < timezone.localdate()
        ):
            raise ValidationError(
                "El permiso ya terminó por fecha."
            )

        self.status = (
            self.PermissionStatus.ACTIVE
        )

        self.suspended_at = None
        self.suspended_by = None
        self.suspension_reason = ""
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "suspended_at",
                "suspended_by",
                "suspension_reason",
                "updated_by",
                "updated_at",
            ]
        )

    def finish(self, user=None):
        if self.status == self.PermissionStatus.REVOKED:
            raise ValidationError(
                "Un permiso revocado no puede finalizarse."
            )

        if self.status == self.PermissionStatus.FINISHED:
            return

        today = timezone.localdate()

        if (
            not self.effective_until
            or self.effective_until > today
        ):
            self.effective_until = today

        self.status = (
            self.PermissionStatus.FINISHED
        )

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

    def revoke(self, user=None, reason=""):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de revocación."
            )

        if self.status == self.PermissionStatus.FINISHED:
            raise ValidationError(
                "Un permiso finalizado no puede revocarse."
            )

        self.status = (
            self.PermissionStatus.REVOKED
        )

        self.revoked_at = timezone.now()
        self.revoked_by = user
        self.revocation_reason = reason
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "revoked_at",
                "revoked_by",
                "revocation_reason",
                "updated_by",
                "updated_at",
            ]
        )

    def register_use(self):
        self.last_used_at = timezone.now()

        self.save(
            update_fields=[
                "last_used_at",
                "updated_at",
            ]
        )

    def archive(self, user=None, reason=""):
        if self.status == self.PermissionStatus.ACTIVE:
            raise ValidationError(
                "No puedes archivar un permiso activo."
            )

        self.archived_at = timezone.now()
        self.archived_by = user
        self.archived_reason = str(
            reason or ""
        ).strip()
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