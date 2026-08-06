# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .attendance_policy import AttendancePolicy
from .employee_profile import EmployeeProfile


class EmployeePolicyAssignment(models.Model):
    """
    Asignación formal de una política de asistencia a un trabajador.

    Permite:

    - Asignar una política específica.
    - Mantener historial de vigencia.
    - Definir prioridades.
    - Aplicar excepciones temporales.
    - Suspender o finalizar una asignación.
    - Conservar la política utilizada en cada periodo.
    """

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
        SUSPENDED = (
            "suspended",
            "Suspendida",
        )
        EXPIRED = (
            "expired",
            "Vencida",
        )
        TERMINATED = (
            "terminated",
            "Finalizada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )

    class AssignmentReason(models.TextChoices):
        DEFAULT = (
            "default",
            "Política predeterminada",
        )
        EMPLOYMENT_START = (
            "employment_start",
            "Inicio laboral",
        )
        POSITION_CHANGE = (
            "position_change",
            "Cambio de cargo",
        )
        DEPARTMENT_CHANGE = (
            "department_change",
            "Cambio de área",
        )
        LOCATION_CHANGE = (
            "location_change",
            "Cambio de ubicación",
        )
        SCHEDULE_CHANGE = (
            "schedule_change",
            "Cambio de horario",
        )
        WORK_MODE_CHANGE = (
            "work_mode_change",
            "Cambio de modalidad de trabajo",
        )
        TEMPORARY_EXCEPTION = (
            "temporary_exception",
            "Excepción temporal",
        )
        DISCIPLINARY_MEASURE = (
            "disciplinary_measure",
            "Medida disciplinaria",
        )
        MEDICAL_ADAPTATION = (
            "medical_adaptation",
            "Adaptación laboral",
        )
        MANAGEMENT_DECISION = (
            "management_decision",
            "Decisión de gerencia",
        )
        MIGRATION = (
            "migration",
            "Migración de datos",
        )
        OTHER = (
            "other",
            "Otro motivo",
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
        related_name="policy_assignments",
        verbose_name="Perfil laboral",
    )

    policy = models.ForeignKey(
        AttendancePolicy,
        on_delete=models.PROTECT,
        related_name="employee_assignments",
        verbose_name="Política de asistencia",
    )

    status = models.CharField(
        max_length=20,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    assignment_reason = models.CharField(
        max_length=30,
        choices=AssignmentReason.choices,
        default=AssignmentReason.DEFAULT,
        db_index=True,
        verbose_name="Motivo de asignación",
    )

    priority = models.PositiveSmallIntegerField(
        default=100,
        db_index=True,
        verbose_name="Prioridad",
        help_text=(
            "Un valor menor tiene mayor prioridad. "
            "La asignación del trabajador tiene prioridad "
            "sobre políticas generales."
        ),
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

    is_primary = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Asignación principal",
    )

    is_temporary = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Asignación temporal",
    )

    overrides_automatic_selection = models.BooleanField(
        default=True,
        verbose_name="Reemplaza selección automática",
        help_text=(
            "Cuando está activo, esta asignación prevalece "
            "sobre políticas por empresa, área, cargo, "
            "horario o ubicación."
        ),
    )

    apply_to_attendance = models.BooleanField(
        default=True,
        verbose_name="Aplicar a asistencia",
    )

    apply_to_operational_time = models.BooleanField(
        default=True,
        verbose_name="Aplicar a tiempo operativo",
    )

    apply_to_incidents = models.BooleanField(
        default=True,
        verbose_name="Aplicar a incidencias",
    )

    apply_to_evaluation = models.BooleanField(
        default=True,
        verbose_name="Aplicar a evaluación",
    )

    exception_settings = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Configuración excepcional",
        help_text=(
            "Permite sobrescribir valores puntuales de la política "
            "sin modificar la política original."
        ),
    )

    reason_detail = models.TextField(
        blank=True,
        verbose_name="Detalle del motivo",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Aprobada el",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_policy_assignments_approved",
        verbose_name="Aprobada por",
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
        related_name="attendance_policy_assignments_activated",
        verbose_name="Activada por",
    )

    suspended_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Suspendida el",
    )

    suspended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_policy_assignments_suspended",
        verbose_name="Suspendida por",
    )

    suspension_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de suspensión",
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
        related_name="attendance_policy_assignments_resumed",
        verbose_name="Reanudada por",
    )

    terminated_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Finalizada el",
    )

    terminated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_policy_assignments_terminated",
        verbose_name="Finalizada por",
    )

    termination_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de finalización",
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
        related_name="attendance_policy_assignments_cancelled",
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
        related_name="attendance_policy_assignments_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_policy_assignments_updated",
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
        related_name="attendance_policy_assignments_archived",
        verbose_name="Archivada por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Asignación de política de asistencia"
        verbose_name_plural = (
            "Asignaciones de políticas de asistencia"
        )

        ordering = (
            "priority",
            "-effective_from",
            "employee_profile",
        )

        constraints = (
            models.CheckConstraint(
                condition=(
                    models.Q(
                        priority__gte=1,
                    )
                    & models.Q(
                        priority__lte=1000,
                    )
                ),
                name="att_pol_asg_priority_range",
            ),
            models.UniqueConstraint(
                fields=(
                    "employee_profile",
                    "policy",
                    "effective_from",
                ),
                condition=models.Q(
                    archived_at__isnull=True,
                ),
                name="att_pol_asg_emp_pol_start_unique",
            ),
        )

        indexes = (
            models.Index(
                fields=(
                    "employee_profile",
                    "status",
                    "effective_from",
                ),
                name="att_pol_asg_emp_status_idx",
            ),
            models.Index(
                fields=(
                    "policy",
                    "status",
                    "effective_from",
                ),
                name="att_pol_asg_policy_status_idx",
            ),
            models.Index(
                fields=(
                    "effective_from",
                    "effective_until",
                    "status",
                ),
                name="att_pol_asg_effective_idx",
            ),
            models.Index(
                fields=(
                    "employee_profile",
                    "is_primary",
                    "priority",
                ),
                name="att_pol_asg_primary_idx",
            ),
            models.Index(
                fields=(
                    "is_temporary",
                    "effective_until",
                    "status",
                ),
                name="att_pol_asg_temp_end_idx",
            ),
            models.Index(
                fields=(
                    "apply_to_attendance",
                    "apply_to_operational_time",
                    "apply_to_evaluation",
                ),
                name="att_pol_asg_apply_idx",
            ),
            models.Index(
                fields=(
                    "assignment_reason",
                    "status",
                ),
                name="att_pol_asg_reason_idx",
            ),
        )

    def __str__(self):
        return (
            f"{self.employee_profile.user.full_name} - "
            f"{self.policy.name} - "
            f"{self.get_status_display()}"
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
    def has_expired(self):
        return (
            self.effective_until is not None
            and self.effective_until
            < timezone.localdate()
        )

    @property
    def effective_settings(self):
        """
        Devuelve la configuración excepcional.

        La combinación completa con la política debe hacerse
        desde un servicio para controlar qué campos pueden
        sobrescribirse.
        """

        return dict(
            self.exception_settings or {}
        )

    def overlaps_existing_assignment(self):
        queryset = (
            EmployeePolicyAssignment.objects
            .filter(
                employee_profile=self.employee_profile,
                archived_at__isnull=True,
                status__in=(
                    self.AssignmentStatus.SCHEDULED,
                    self.AssignmentStatus.ACTIVE,
                    self.AssignmentStatus.SUSPENDED,
                ),
            )
            .exclude(
                pk=self.pk,
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

        if self.is_primary:
            queryset = queryset.filter(
                is_primary=True,
            )

        return queryset.exists()

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
            self.policy_id
            and self.policy.archived_at
        ):
            errors["policy"] = (
                "La política está archivada."
            )

        if (
            self.policy_id
            and not self.policy.is_active
            and self.status
            in (
                self.AssignmentStatus.SCHEDULED,
                self.AssignmentStatus.ACTIVE,
            )
        ):
            errors["policy"] = (
                "No puedes activar una política inactiva."
            )

        if (
            self.effective_until
            and self.effective_until < self.effective_from
        ):
            errors["effective_until"] = (
                "La fecha final no puede ser anterior "
                "a la fecha inicial."
            )

        if (
            self.is_temporary
            and not self.effective_until
        ):
            errors["effective_until"] = (
                "Una asignación temporal debe tener "
                "fecha de finalización."
            )

        if (
            not self.is_temporary
            and self.assignment_reason
            == self.AssignmentReason.TEMPORARY_EXCEPTION
        ):
            errors["is_temporary"] = (
                "Una excepción temporal debe identificarse "
                "como asignación temporal."
            )

        if (
            self.assignment_reason
            not in (
                self.AssignmentReason.DEFAULT,
                self.AssignmentReason.EMPLOYMENT_START,
            )
            and not self.reason_detail.strip()
        ):
            errors["reason_detail"] = (
                "Debes explicar el motivo de la asignación."
            )

        if not any(
            (
                self.apply_to_attendance,
                self.apply_to_operational_time,
                self.apply_to_incidents,
                self.apply_to_evaluation,
            )
        ):
            errors["apply_to_attendance"] = (
                "La asignación debe aplicarse al menos "
                "a un proceso."
            )

        if not isinstance(
            self.exception_settings,
            dict,
        ):
            errors["exception_settings"] = (
                "La configuración excepcional debe ser "
                "un objeto JSON."
            )

        if (
            self.status
            in (
                self.AssignmentStatus.SCHEDULED,
                self.AssignmentStatus.ACTIVE,
                self.AssignmentStatus.SUSPENDED,
            )
            and self.employee_profile_id
            and self.effective_from
            and self.overlaps_existing_assignment()
        ):
            errors["effective_from"] = (
                "El trabajador ya tiene otra asignación "
                "principal vigente durante ese periodo."
            )

        if (
            self.status == self.AssignmentStatus.ACTIVE
            and not self.activated_at
        ):
            errors["activated_at"] = (
                "Una asignación activa debe tener "
                "fecha de activación."
            )

        if (
            self.status == self.AssignmentStatus.SUSPENDED
            and not self.suspended_at
        ):
            errors["suspended_at"] = (
                "Una asignación suspendida debe tener "
                "fecha de suspensión."
            )

        if (
            self.status == self.AssignmentStatus.SUSPENDED
            and not self.suspension_reason.strip()
        ):
            errors["suspension_reason"] = (
                "Debes indicar el motivo de suspensión."
            )

        if (
            self.status == self.AssignmentStatus.TERMINATED
            and not self.terminated_at
        ):
            errors["terminated_at"] = (
                "Una asignación finalizada debe tener "
                "fecha de finalización."
            )

        if (
            self.status == self.AssignmentStatus.TERMINATED
            and not self.termination_reason.strip()
        ):
            errors["termination_reason"] = (
                "Debes indicar el motivo de finalización."
            )

        if (
            self.status == self.AssignmentStatus.CANCELLED
            and not self.cancelled_at
        ):
            errors["cancelled_at"] = (
                "Una asignación cancelada debe tener "
                "fecha de cancelación."
            )

        if (
            self.status == self.AssignmentStatus.CANCELLED
            and not self.cancellation_reason.strip()
        ):
            errors["cancellation_reason"] = (
                "Debes indicar el motivo de cancelación."
            )

        if (
            self.approved_at
            and not self.approved_by_id
        ):
            errors["approved_by"] = (
                "Debes indicar quién aprobó la asignación."
            )

        if (
            self.activated_at
            and not self.activated_by_id
        ):
            errors["activated_by"] = (
                "Debes indicar quién activó la asignación."
            )

        if (
            self.suspended_at
            and not self.suspended_by_id
        ):
            errors["suspended_by"] = (
                "Debes indicar quién suspendió la asignación."
            )

        if (
            self.resumed_at
            and not self.resumed_by_id
        ):
            errors["resumed_by"] = (
                "Debes indicar quién reanudó la asignación."
            )

        if (
            self.terminated_at
            and not self.terminated_by_id
        ):
            errors["terminated_by"] = (
                "Debes indicar quién finalizó la asignación."
            )

        if (
            self.cancelled_at
            and not self.cancelled_by_id
        ):
            errors["cancelled_by"] = (
                "Debes indicar quién canceló la asignación."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if (
            self.status == self.AssignmentStatus.SCHEDULED
            and self.effective_from <= timezone.localdate()
            and not self.activated_at
        ):
            self.status = self.AssignmentStatus.ACTIVE
            self.activated_at = timezone.now()

        if (
            self.status
            in (
                self.AssignmentStatus.SCHEDULED,
                self.AssignmentStatus.ACTIVE,
                self.AssignmentStatus.SUSPENDED,
            )
            and self.has_expired
        ):
            self.status = self.AssignmentStatus.EXPIRED

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def schedule(
        self,
        user=None,
    ):
        if self.status != self.AssignmentStatus.DRAFT:
            raise ValidationError(
                "Solo puedes programar una asignación "
                "en borrador."
            )

        if self.overlaps_existing_assignment():
            raise ValidationError(
                "Ya existe otra asignación principal vigente "
                "durante ese periodo."
            )

        self.approved_at = timezone.now()
        self.approved_by = user
        self.updated_by = user

        if self.effective_from <= timezone.localdate():
            self.status = self.AssignmentStatus.ACTIVE
            self.activated_at = timezone.now()
            self.activated_by = user

        else:
            self.status = self.AssignmentStatus.SCHEDULED

        self.save()

    def activate(
        self,
        user=None,
    ):
        if self.status not in (
            self.AssignmentStatus.DRAFT,
            self.AssignmentStatus.SCHEDULED,
            self.AssignmentStatus.SUSPENDED,
        ):
            raise ValidationError(
                "La asignación no puede activarse "
                "desde su estado actual."
            )

        if self.has_expired:
            raise ValidationError(
                "No puedes activar una asignación vencida."
            )

        if not self.policy.is_current:
            raise ValidationError(
                "La política no se encuentra vigente."
            )

        if self.overlaps_existing_assignment():
            raise ValidationError(
                "Ya existe otra asignación principal vigente "
                "durante ese periodo."
            )

        now = timezone.now()

        if not self.approved_at:
            self.approved_at = now
            self.approved_by = user

        self.status = self.AssignmentStatus.ACTIVE
        self.activated_at = now
        self.activated_by = user
        self.suspended_at = None
        self.suspended_by = None
        self.suspension_reason = ""

        if self.resumed_at is None:
            self.resumed_at = now
            self.resumed_by = user

        self.updated_by = user

        self.save()

    def suspend(
        self,
        user,
        reason,
    ):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de suspensión."
            )

        if self.status != self.AssignmentStatus.ACTIVE:
            raise ValidationError(
                "Solo puedes suspender una asignación activa."
            )

        self.status = self.AssignmentStatus.SUSPENDED
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

    def resume(
        self,
        user=None,
    ):
        if self.status != self.AssignmentStatus.SUSPENDED:
            raise ValidationError(
                "Solo puedes reanudar una asignación suspendida."
            )

        if self.has_expired:
            raise ValidationError(
                "No puedes reanudar una asignación vencida."
            )

        if self.overlaps_existing_assignment():
            raise ValidationError(
                "Existe otra asignación principal vigente "
                "durante ese periodo."
            )

        self.status = self.AssignmentStatus.ACTIVE
        self.resumed_at = timezone.now()
        self.resumed_by = user
        self.suspended_at = None
        self.suspended_by = None
        self.suspension_reason = ""
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "resumed_at",
                "resumed_by",
                "suspended_at",
                "suspended_by",
                "suspension_reason",
                "updated_by",
                "updated_at",
            ]
        )

    def terminate(
        self,
        user,
        reason,
        effective_until=None,
    ):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de finalización."
            )

        if self.status in (
            self.AssignmentStatus.TERMINATED,
            self.AssignmentStatus.CANCELLED,
            self.AssignmentStatus.EXPIRED,
        ):
            raise ValidationError(
                "La asignación ya no puede finalizarse."
            )

        end_date = (
            effective_until
            or timezone.localdate()
        )

        if end_date < self.effective_from:
            raise ValidationError(
                "La fecha de finalización no puede ser anterior "
                "al inicio de vigencia."
            )

        self.status = self.AssignmentStatus.TERMINATED
        self.effective_until = end_date
        self.terminated_at = timezone.now()
        self.terminated_by = user
        self.termination_reason = reason
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "effective_until",
                "terminated_at",
                "terminated_by",
                "termination_reason",
                "updated_by",
                "updated_at",
            ]
        )

    def expire(
        self,
        user=None,
    ):
        if not self.has_expired:
            raise ValidationError(
                "La asignación todavía no ha vencido."
            )

        if self.status in (
            self.AssignmentStatus.TERMINATED,
            self.AssignmentStatus.CANCELLED,
        ):
            raise ValidationError(
                "La asignación ya fue finalizada o cancelada."
            )

        self.status = self.AssignmentStatus.EXPIRED
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "updated_by",
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

        if self.status not in (
            self.AssignmentStatus.DRAFT,
            self.AssignmentStatus.SCHEDULED,
        ):
            raise ValidationError(
                "Solo puedes cancelar una asignación "
                "en borrador o programada."
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
            self.AssignmentStatus.ACTIVE,
            self.AssignmentStatus.SCHEDULED,
            self.AssignmentStatus.SUSPENDED,
        ):
            raise ValidationError(
                "No puedes archivar una asignación vigente, "
                "programada o suspendida."
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