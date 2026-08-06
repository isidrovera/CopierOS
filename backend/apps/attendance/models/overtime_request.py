# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .daily_attendance import DailyAttendance
from .employee_profile import EmployeeProfile
from .employee_schedule_assignment import (
    EmployeeScheduleAssignment,
)
from .work_location import WorkLocation


class OvertimeRequest(models.Model):
    """
    Solicitud, autorización y cierre de horas extras.

    Permite registrar:

    - Horas extras programadas previamente.
    - Horas extras solicitadas por el trabajador.
    - Horas extras solicitadas por un supervisor.
    - Trabajo extraordinario por emergencia.
    - Trabajo en feriados o días de descanso.
    - Minutos solicitados.
    - Minutos autorizados.
    - Minutos realmente trabajados.
    - Minutos finalmente aprobados.
    - Compensación con pago o descanso.
    - Revisión por supervisor, recursos humanos o gerencia.

    La solicitud no reemplaza las marcaciones de asistencia.
    Los minutos trabajados deben contrastarse con la asistencia
    diaria antes de cerrar la solicitud.
    """

    class OvertimeType(models.TextChoices):
        BEFORE_SHIFT = (
            "before_shift",
            "Antes de la jornada",
        )
        AFTER_SHIFT = (
            "after_shift",
            "Después de la jornada",
        )
        REST_DAY = (
            "rest_day",
            "Día de descanso",
        )
        HOLIDAY = (
            "holiday",
            "Feriado",
        )
        NIGHT_WORK = (
            "night_work",
            "Trabajo nocturno",
        )
        EMERGENCY = (
            "emergency",
            "Emergencia",
        )
        SERVICE_COMMISSION = (
            "service_commission",
            "Comisión de servicio",
        )
        OPERATIONAL_CONTINUITY = (
            "operational_continuity",
            "Continuidad operativa",
        )
        INVENTORY = (
            "inventory",
            "Inventario",
        )
        CLOSING_ACTIVITY = (
            "closing_activity",
            "Actividad de cierre",
        )
        SPECIAL_PROJECT = (
            "special_project",
            "Proyecto especial",
        )
        OTHER = (
            "other",
            "Otro",
        )

    class RequestOrigin(models.TextChoices):
        EMPLOYEE = (
            "employee",
            "Solicitada por el trabajador",
        )
        SUPERVISOR = (
            "supervisor",
            "Solicitada por el supervisor",
        )
        HUMAN_RESOURCES = (
            "human_resources",
            "Solicitada por recursos humanos",
        )
        MANAGEMENT = (
            "management",
            "Solicitada por gerencia",
        )
        SYSTEM = (
            "system",
            "Generada por el sistema",
        )

    class Status(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        SUBMITTED = (
            "submitted",
            "Presentada",
        )
        PENDING_SUPERVISOR = (
            "pending_supervisor",
            "Pendiente del supervisor",
        )
        PENDING_HUMAN_RESOURCES = (
            "pending_human_resources",
            "Pendiente de recursos humanos",
        )
        PENDING_MANAGEMENT = (
            "pending_management",
            "Pendiente de gerencia",
        )
        APPROVED = (
            "approved",
            "Aprobada",
        )
        PARTIALLY_APPROVED = (
            "partially_approved",
            "Aprobada parcialmente",
        )
        REJECTED = (
            "rejected",
            "Rechazada",
        )
        IN_PROGRESS = (
            "in_progress",
            "En ejecución",
        )
        WORKED = (
            "worked",
            "Trabajo realizado",
        )
        UNDER_REVIEW = (
            "under_review",
            "En revisión",
        )
        VERIFIED = (
            "verified",
            "Verificada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )
        CLOSED = (
            "closed",
            "Cerrada",
        )

    class ApprovalLevel(models.TextChoices):
        SUPERVISOR = (
            "supervisor",
            "Supervisor",
        )
        HUMAN_RESOURCES = (
            "human_resources",
            "Recursos humanos",
        )
        MANAGEMENT = (
            "management",
            "Gerencia",
        )
        AUTOMATIC = (
            "automatic",
            "Automática",
        )

    class CompensationType(models.TextChoices):
        PAYMENT = (
            "payment",
            "Pago de horas extras",
        )
        COMPENSATORY_REST = (
            "compensatory_rest",
            "Descanso compensatorio",
        )
        MIXED = (
            "mixed",
            "Pago y descanso",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )

    class VerificationResult(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        MATCHED = (
            "matched",
            "Coincide con asistencia",
        )
        PARTIAL = (
            "partial",
            "Coincidencia parcial",
        )
        EXCEEDED = (
            "exceeded",
            "Superó lo autorizado",
        )
        INSUFFICIENT = (
            "insufficient",
            "Trabajó menos de lo autorizado",
        )
        NO_ATTENDANCE = (
            "no_attendance",
            "Sin asistencia registrada",
        )
        MANUAL_REVIEW = (
            "manual_review",
            "Revisión manual",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    request_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Número de solicitud",
    )

    employee_profile = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.PROTECT,
        related_name="overtime_requests",
        verbose_name="Perfil laboral",
    )

    daily_attendance = models.ForeignKey(
        DailyAttendance,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="overtime_requests",
        verbose_name="Asistencia diaria",
    )

    schedule_assignment = models.ForeignKey(
        EmployeeScheduleAssignment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="overtime_requests",
        verbose_name="Asignación de horario",
    )

    work_location = models.ForeignKey(
        WorkLocation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="overtime_requests",
        verbose_name="Ubicación de trabajo",
    )

    overtime_type = models.CharField(
        max_length=30,
        choices=OvertimeType.choices,
        db_index=True,
        verbose_name="Tipo de horas extras",
    )

    request_origin = models.CharField(
        max_length=30,
        choices=RequestOrigin.choices,
        default=RequestOrigin.EMPLOYEE,
        db_index=True,
        verbose_name="Origen de solicitud",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    required_approval_level = models.CharField(
        max_length=30,
        choices=ApprovalLevel.choices,
        default=ApprovalLevel.SUPERVISOR,
        db_index=True,
        verbose_name="Nivel de aprobación requerido",
    )

    compensation_type = models.CharField(
        max_length=30,
        choices=CompensationType.choices,
        default=CompensationType.PAYMENT,
        db_index=True,
        verbose_name="Tipo de compensación",
    )

    verification_result = models.CharField(
        max_length=30,
        choices=VerificationResult.choices,
        default=VerificationResult.PENDING,
        db_index=True,
        verbose_name="Resultado de verificación",
    )

    overtime_date = models.DateField(
        db_index=True,
        verbose_name="Fecha de horas extras",
    )

    requested_start_at = models.DateTimeField(
        db_index=True,
        verbose_name="Inicio solicitado",
    )

    requested_end_at = models.DateTimeField(
        db_index=True,
        verbose_name="Fin solicitado",
    )

    requested_minutes = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Minutos solicitados",
    )

    authorized_start_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Inicio autorizado",
    )

    authorized_end_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fin autorizado",
    )

    authorized_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos autorizados",
    )

    actual_start_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Inicio real",
    )

    actual_end_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fin real",
    )

    actual_worked_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos realmente trabajados",
    )

    attendance_detected_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos detectados en asistencia",
    )

    approved_minutes = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos finalmente aprobados",
    )

    payable_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos pagables",
    )

    compensatory_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos de descanso compensatorio",
    )

    excess_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos trabajados en exceso",
    )

    rejected_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos no aprobados",
    )

    reason = models.TextField(
        verbose_name="Motivo",
    )

    planned_activity = models.TextField(
        verbose_name="Actividad programada",
    )

    work_result = models.TextField(
        blank=True,
        verbose_name="Resultado del trabajo",
    )

    operational_reference = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Referencia operativa",
        help_text=(
            "Puede registrar el número de reparación, servicio, "
            "instalación, inventario u otra actividad relacionada."
        ),
    )

    is_emergency = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Trabajo de emergencia",
    )

    was_previously_authorized = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Autorizada antes de ejecutarse",
    )

    requires_post_work_approval = models.BooleanField(
        default=False,
        verbose_name="Requiere aprobación posterior",
    )

    affects_payroll = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Afecta planilla",
    )

    affects_evaluation = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Afecta evaluación",
    )

    include_in_monthly_summary = models.BooleanField(
        default=True,
        verbose_name="Incluir en resumen mensual",
    )

    supporting_document = models.FileField(
        upload_to="attendance/overtime/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Documento sustentatorio",
    )

    supporting_document_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre del documento",
    )

    supporting_document_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tipo de documento",
    )

    supporting_document_size = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Tamaño del documento",
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Presentada el",
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_overtime_requests_submitted",
        verbose_name="Presentada por",
    )

    supervisor_reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Revisada por supervisor el",
    )

    supervisor_reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_overtime_supervisor_reviewed",
        verbose_name="Revisada por supervisor",
    )

    supervisor_observation = models.TextField(
        blank=True,
        verbose_name="Observación del supervisor",
    )

    human_resources_reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Revisada por recursos humanos el",
    )

    human_resources_reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_overtime_hr_reviewed",
        verbose_name="Revisada por recursos humanos",
    )

    human_resources_observation = models.TextField(
        blank=True,
        verbose_name="Observación de recursos humanos",
    )

    management_reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Revisada por gerencia el",
    )

    management_reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_overtime_management_reviewed",
        verbose_name="Revisada por gerencia",
    )

    management_observation = models.TextField(
        blank=True,
        verbose_name="Observación de gerencia",
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
        related_name="attendance_overtime_requests_approved",
        verbose_name="Aprobada por",
    )

    approval_observation = models.TextField(
        blank=True,
        verbose_name="Observación de aprobación",
    )

    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Rechazada el",
    )

    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_overtime_requests_rejected",
        verbose_name="Rechazada por",
    )

    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de rechazo",
    )

    work_registered_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Trabajo registrado el",
    )

    work_registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_overtime_work_registered",
        verbose_name="Trabajo registrado por",
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Verificada el",
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_overtime_requests_verified",
        verbose_name="Verificada por",
    )

    verification_observation = models.TextField(
        blank=True,
        verbose_name="Observación de verificación",
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
        related_name="attendance_overtime_requests_cancelled",
        verbose_name="Cancelada por",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Cerrada el",
    )

    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_overtime_requests_closed",
        verbose_name="Cerrada por",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones internas",
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
        related_name="attendance_overtime_requests_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_overtime_requests_updated",
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
        related_name="attendance_overtime_requests_archived",
        verbose_name="Archivada por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Solicitud de horas extras"
        verbose_name_plural = "Solicitudes de horas extras"

        ordering = (
            "-overtime_date",
            "-created_at",
        )

        indexes = (
            models.Index(
                fields=(
                    "employee_profile",
                    "overtime_date",
                    "status",
                ),
                name="att_ot_emp_date_status_idx",
            ),
            models.Index(
                fields=(
                    "daily_attendance",
                    "status",
                ),
                name="att_ot_daily_status_idx",
            ),
            models.Index(
                fields=(
                    "overtime_type",
                    "status",
                    "overtime_date",
                ),
                name="att_ot_type_status_idx",
            ),
            models.Index(
                fields=(
                    "required_approval_level",
                    "status",
                ),
                name="att_ot_approval_status_idx",
            ),
            models.Index(
                fields=(
                    "compensation_type",
                    "affects_payroll",
                ),
                name="att_ot_comp_payroll_idx",
            ),
            models.Index(
                fields=(
                    "verification_result",
                    "status",
                ),
                name="att_ot_verify_status_idx",
            ),
            models.Index(
                fields=(
                    "is_emergency",
                    "was_previously_authorized",
                ),
                name="att_ot_emergency_auth_idx",
            ),
            models.Index(
                fields=(
                    "requested_start_at",
                    "requested_end_at",
                ),
                name="att_ot_requested_range_idx",
            ),
            models.Index(
                fields=(
                    "authorized_start_at",
                    "authorized_end_at",
                ),
                name="att_ot_authorized_range_idx",
            ),
            models.Index(
                fields=(
                    "approved_minutes",
                    "overtime_date",
                ),
                name="att_ot_approved_date_idx",
            ),
        )

        constraints = (
            models.CheckConstraint(
                condition=models.Q(
                    authorized_minutes__lte=models.F(
                        "requested_minutes"
                    ),
                ),
                name="att_ot_authorized_lte_requested",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    approved_minutes__lte=models.F(
                        "actual_worked_minutes"
                    ),
                ),
                name="att_ot_approved_lte_actual",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    payable_minutes__lte=models.F(
                        "approved_minutes"
                    ),
                ),
                name="att_ot_payable_lte_approved",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    compensatory_minutes__lte=models.F(
                        "approved_minutes"
                    ),
                ),
                name="att_ot_comp_lte_approved",
            ),
        )

    def __str__(self):
        return (
            f"{self.request_number} - "
            f"{self.employee_profile.user.full_name} - "
            f"{self.overtime_date}"
        )

    @property
    def employee(self):
        return self.employee_profile.user

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_pending(self):
        return self.status in (
            self.Status.SUBMITTED,
            self.Status.PENDING_SUPERVISOR,
            self.Status.PENDING_HUMAN_RESOURCES,
            self.Status.PENDING_MANAGEMENT,
            self.Status.UNDER_REVIEW,
        )

    @property
    def is_authorized(self):
        return self.status in (
            self.Status.APPROVED,
            self.Status.PARTIALLY_APPROVED,
            self.Status.IN_PROGRESS,
            self.Status.WORKED,
            self.Status.UNDER_REVIEW,
            self.Status.VERIFIED,
            self.Status.CLOSED,
        )

    @property
    def is_closed(self):
        return self.status == self.Status.CLOSED

    @property
    def requested_hours(self):
        return round(
            self.requested_minutes / 60,
            2,
        )

    @property
    def authorized_hours(self):
        return round(
            self.authorized_minutes / 60,
            2,
        )

    @property
    def actual_worked_hours(self):
        return round(
            self.actual_worked_minutes / 60,
            2,
        )

    @property
    def approved_hours(self):
        return round(
            self.approved_minutes / 60,
            2,
        )

    def calculate_requested_minutes(self):
        if (
            not self.requested_start_at
            or not self.requested_end_at
            or self.requested_end_at
            <= self.requested_start_at
        ):
            self.requested_minutes = 0
            return 0

        self.requested_minutes = int(
            (
                self.requested_end_at
                - self.requested_start_at
            ).total_seconds()
            // 60
        )

        return self.requested_minutes

    def calculate_authorized_minutes(self):
        if (
            not self.authorized_start_at
            or not self.authorized_end_at
            or self.authorized_end_at
            <= self.authorized_start_at
        ):
            self.authorized_minutes = 0
            return 0

        self.authorized_minutes = int(
            (
                self.authorized_end_at
                - self.authorized_start_at
            ).total_seconds()
            // 60
        )

        return self.authorized_minutes

    def calculate_actual_worked_minutes(self):
        if (
            not self.actual_start_at
            or not self.actual_end_at
            or self.actual_end_at
            <= self.actual_start_at
        ):
            self.actual_worked_minutes = 0
            return 0

        self.actual_worked_minutes = int(
            (
                self.actual_end_at
                - self.actual_start_at
            ).total_seconds()
            // 60
        )

        return self.actual_worked_minutes

    def calculate_verification_result(self):
        if self.attendance_detected_minutes <= 0:
            self.verification_result = (
                self.VerificationResult.NO_ATTENDANCE
            )
            return self.verification_result

        if self.authorized_minutes <= 0:
            self.verification_result = (
                self.VerificationResult.MANUAL_REVIEW
            )
            return self.verification_result

        if (
            self.attendance_detected_minutes
            == self.authorized_minutes
        ):
            self.verification_result = (
                self.VerificationResult.MATCHED
            )

        elif (
            self.attendance_detected_minutes
            > self.authorized_minutes
        ):
            self.verification_result = (
                self.VerificationResult.EXCEEDED
            )

        elif (
            self.attendance_detected_minutes
            < self.authorized_minutes
        ):
            self.verification_result = (
                self.VerificationResult.INSUFFICIENT
            )

        else:
            self.verification_result = (
                self.VerificationResult.PARTIAL
            )

        return self.verification_result

    def calculate_result_minutes(self):
        self.excess_minutes = max(
            0,
            self.actual_worked_minutes
            - self.authorized_minutes,
        )

        self.rejected_minutes = max(
            0,
            self.actual_worked_minutes
            - self.approved_minutes,
        )

        if self.compensation_type == (
            self.CompensationType.PAYMENT
        ):
            self.payable_minutes = self.approved_minutes
            self.compensatory_minutes = 0

        elif self.compensation_type == (
            self.CompensationType.COMPENSATORY_REST
        ):
            self.payable_minutes = 0
            self.compensatory_minutes = (
                self.approved_minutes
            )

        elif self.compensation_type == (
            self.CompensationType.NOT_APPLICABLE
        ):
            self.payable_minutes = 0
            self.compensatory_minutes = 0

    def overlaps_existing_request(self):
        queryset = (
            OvertimeRequest.objects
            .filter(
                employee_profile=self.employee_profile,
                overtime_date=self.overtime_date,
                archived_at__isnull=True,
            )
            .exclude(
                pk=self.pk,
            )
            .exclude(
                status__in=(
                    self.Status.DRAFT,
                    self.Status.REJECTED,
                    self.Status.CANCELLED,
                    self.Status.CLOSED,
                ),
            )
            .filter(
                requested_start_at__lt=self.requested_end_at,
                requested_end_at__gt=self.requested_start_at,
            )
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
            self.daily_attendance_id
            and self.daily_attendance.employee_profile_id
            != self.employee_profile_id
        ):
            errors["daily_attendance"] = (
                "La asistencia diaria no corresponde "
                "al trabajador."
            )

        if (
            self.daily_attendance_id
            and self.daily_attendance.date
            != self.overtime_date
        ):
            errors["daily_attendance"] = (
                "La asistencia diaria no corresponde "
                "a la fecha de horas extras."
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
            self.work_location_id
            and (
                self.work_location.archived_at
                or not self.work_location.is_active
            )
        ):
            errors["work_location"] = (
                "La ubicación de trabajo no está disponible."
            )

        if (
            self.requested_end_at
            <= self.requested_start_at
        ):
            errors["requested_end_at"] = (
                "El fin solicitado debe ser posterior "
                "al inicio solicitado."
            )

        if (
            self.requested_start_at.date()
            != self.overtime_date
            and self.requested_end_at.date()
            != self.overtime_date
        ):
            errors["overtime_date"] = (
                "La fecha debe coincidir con el inicio "
                "o el fin solicitado."
            )

        if (
            self.authorized_start_at
            and not self.authorized_end_at
        ):
            errors["authorized_end_at"] = (
                "Debes indicar el fin autorizado."
            )

        if (
            self.authorized_end_at
            and not self.authorized_start_at
        ):
            errors["authorized_start_at"] = (
                "Debes indicar el inicio autorizado."
            )

        if (
            self.authorized_start_at
            and self.authorized_end_at
            and self.authorized_end_at
            <= self.authorized_start_at
        ):
            errors["authorized_end_at"] = (
                "El fin autorizado debe ser posterior "
                "al inicio autorizado."
            )

        if (
            self.actual_start_at
            and not self.actual_end_at
            and self.status
            in (
                self.Status.WORKED,
                self.Status.UNDER_REVIEW,
                self.Status.VERIFIED,
                self.Status.CLOSED,
            )
        ):
            errors["actual_end_at"] = (
                "Debes indicar el fin real del trabajo."
            )

        if (
            self.actual_end_at
            and not self.actual_start_at
        ):
            errors["actual_start_at"] = (
                "Debes indicar el inicio real del trabajo."
            )

        if (
            self.actual_start_at
            and self.actual_end_at
            and self.actual_end_at
            <= self.actual_start_at
        ):
            errors["actual_end_at"] = (
                "El fin real debe ser posterior al inicio real."
            )

        if self.authorized_minutes > self.requested_minutes:
            errors["authorized_minutes"] = (
                "Los minutos autorizados no pueden superar "
                "los solicitados."
            )

        if self.approved_minutes > self.actual_worked_minutes:
            errors["approved_minutes"] = (
                "Los minutos aprobados no pueden superar "
                "los realmente trabajados."
            )

        if self.payable_minutes > self.approved_minutes:
            errors["payable_minutes"] = (
                "Los minutos pagables no pueden superar "
                "los aprobados."
            )

        if (
            self.compensatory_minutes
            > self.approved_minutes
        ):
            errors["compensatory_minutes"] = (
                "Los minutos compensatorios no pueden superar "
                "los aprobados."
            )

        if (
            self.compensation_type
            == self.CompensationType.MIXED
            and (
                self.payable_minutes
                + self.compensatory_minutes
                != self.approved_minutes
            )
        ):
            errors["payable_minutes"] = (
                "En una compensación mixta, la suma de minutos "
                "pagables y compensatorios debe coincidir "
                "con los minutos aprobados."
            )

        if (
            self.compensation_type
            == self.CompensationType.PAYMENT
            and self.compensatory_minutes
        ):
            errors["compensatory_minutes"] = (
                "Una compensación por pago no debe generar "
                "descanso compensatorio."
            )

        if (
            self.compensation_type
            == self.CompensationType.COMPENSATORY_REST
            and self.payable_minutes
        ):
            errors["payable_minutes"] = (
                "Un descanso compensatorio no debe generar "
                "minutos pagables."
            )

        if (
            self.employee_profile_id
            and self.overtime_date
            and self.requested_start_at
            and self.requested_end_at
            and self.status
            not in (
                self.Status.DRAFT,
                self.Status.REJECTED,
                self.Status.CANCELLED,
                self.Status.CLOSED,
            )
            and self.overlaps_existing_request()
        ):
            errors["requested_start_at"] = (
                "Ya existe otra solicitud de horas extras "
                "que se cruza con este horario."
            )

        if (
            not self.was_previously_authorized
            and not self.is_emergency
            and not self.requires_post_work_approval
        ):
            errors["requires_post_work_approval"] = (
                "Las horas no autorizadas previamente deben "
                "requerir aprobación posterior."
            )

        if (
            self.status
            in (
                self.Status.APPROVED,
                self.Status.PARTIALLY_APPROVED,
                self.Status.IN_PROGRESS,
                self.Status.WORKED,
                self.Status.UNDER_REVIEW,
                self.Status.VERIFIED,
                self.Status.CLOSED,
            )
            and not self.approved_at
        ):
            errors["approved_at"] = (
                "La solicitud autorizada debe tener "
                "fecha de aprobación."
            )

        if (
            self.status == self.Status.REJECTED
            and not self.rejection_reason.strip()
        ):
            errors["rejection_reason"] = (
                "Debes indicar el motivo de rechazo."
            )

        if (
            self.status == self.Status.WORKED
            and not self.work_registered_at
        ):
            errors["work_registered_at"] = (
                "Debes registrar cuándo se informó "
                "el trabajo realizado."
            )

        if (
            self.status == self.Status.VERIFIED
            and not self.verified_at
        ):
            errors["verified_at"] = (
                "Una solicitud verificada debe tener "
                "fecha de verificación."
            )

        if (
            self.status == self.Status.CANCELLED
            and not self.cancellation_reason.strip()
        ):
            errors["cancellation_reason"] = (
                "Debes indicar el motivo de cancelación."
            )

        if (
            self.status == self.Status.CLOSED
            and not self.closed_at
        ):
            errors["closed_at"] = (
                "Una solicitud cerrada debe tener "
                "fecha de cierre."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.calculate_requested_minutes()

        if (
            self.authorized_start_at
            and self.authorized_end_at
        ):
            self.calculate_authorized_minutes()

        if self.actual_start_at and self.actual_end_at:
            self.calculate_actual_worked_minutes()

        self.calculate_result_minutes()
        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def submit(self, user=None):
        if self.status != self.Status.DRAFT:
            raise ValidationError(
                "Solo puedes presentar una solicitud "
                "en borrador."
            )

        if self.overlaps_existing_request():
            raise ValidationError(
                "Existe otra solicitud que se cruza "
                "con el horario indicado."
            )

        self.submitted_at = timezone.now()
        self.submitted_by = user
        self.updated_by = user

        if (
            self.required_approval_level
            == self.ApprovalLevel.SUPERVISOR
        ):
            self.status = self.Status.PENDING_SUPERVISOR

        elif (
            self.required_approval_level
            == self.ApprovalLevel.HUMAN_RESOURCES
        ):
            self.status = (
                self.Status.PENDING_HUMAN_RESOURCES
            )

        elif (
            self.required_approval_level
            == self.ApprovalLevel.MANAGEMENT
        ):
            self.status = self.Status.PENDING_MANAGEMENT

        else:
            self._approve_internal(
                user=user,
                observation=(
                    "Aprobación automática."
                ),
            )
            return

        self.save()

    def supervisor_approve(
        self,
        user,
        observation="",
        authorized_start_at=None,
        authorized_end_at=None,
    ):
        if self.status != self.Status.PENDING_SUPERVISOR:
            raise ValidationError(
                "La solicitud no está pendiente "
                "del supervisor."
            )

        self.supervisor_reviewed_at = timezone.now()
        self.supervisor_reviewed_by = user
        self.supervisor_observation = str(
            observation or ""
        ).strip()

        self._approve_internal(
            user=user,
            observation=observation,
            authorized_start_at=authorized_start_at,
            authorized_end_at=authorized_end_at,
        )

    def human_resources_approve(
        self,
        user,
        observation="",
        authorized_start_at=None,
        authorized_end_at=None,
    ):
        if (
            self.status
            != self.Status.PENDING_HUMAN_RESOURCES
        ):
            raise ValidationError(
                "La solicitud no está pendiente "
                "de recursos humanos."
            )

        self.human_resources_reviewed_at = timezone.now()
        self.human_resources_reviewed_by = user
        self.human_resources_observation = str(
            observation or ""
        ).strip()

        self._approve_internal(
            user=user,
            observation=observation,
            authorized_start_at=authorized_start_at,
            authorized_end_at=authorized_end_at,
        )

    def management_approve(
        self,
        user,
        observation="",
        authorized_start_at=None,
        authorized_end_at=None,
    ):
        if self.status != self.Status.PENDING_MANAGEMENT:
            raise ValidationError(
                "La solicitud no está pendiente de gerencia."
            )

        self.management_reviewed_at = timezone.now()
        self.management_reviewed_by = user
        self.management_observation = str(
            observation or ""
        ).strip()

        self._approve_internal(
            user=user,
            observation=observation,
            authorized_start_at=authorized_start_at,
            authorized_end_at=authorized_end_at,
        )

    def _approve_internal(
        self,
        user,
        observation="",
        authorized_start_at=None,
        authorized_end_at=None,
    ):
        authorized_start_at = (
            authorized_start_at
            or self.requested_start_at
        )

        authorized_end_at = (
            authorized_end_at
            or self.requested_end_at
        )

        if authorized_end_at <= authorized_start_at:
            raise ValidationError(
                "El fin autorizado debe ser posterior "
                "al inicio autorizado."
            )

        authorized_minutes = int(
            (
                authorized_end_at
                - authorized_start_at
            ).total_seconds()
            // 60
        )

        if authorized_minutes > self.requested_minutes:
            raise ValidationError(
                "No puedes autorizar más minutos "
                "de los solicitados."
            )

        self.authorized_start_at = authorized_start_at
        self.authorized_end_at = authorized_end_at
        self.authorized_minutes = authorized_minutes

        if authorized_minutes < self.requested_minutes:
            self.status = self.Status.PARTIALLY_APPROVED
        else:
            self.status = self.Status.APPROVED

        self.approved_at = timezone.now()
        self.approved_by = user
        self.approval_observation = str(
            observation or ""
        ).strip()
        self.updated_by = user

        self.save()

    def reject(
        self,
        user,
        reason,
    ):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de rechazo."
            )

        if not self.is_pending:
            raise ValidationError(
                "Solo puedes rechazar una solicitud pendiente."
            )

        self.status = self.Status.REJECTED
        self.rejected_at = timezone.now()
        self.rejected_by = user
        self.rejection_reason = reason
        self.updated_by = user

        self.save()

    def start(self, user=None):
        if self.status not in (
            self.Status.APPROVED,
            self.Status.PARTIALLY_APPROVED,
        ):
            raise ValidationError(
                "Solo puedes iniciar horas extras autorizadas."
            )

        self.status = self.Status.IN_PROGRESS

        if not self.actual_start_at:
            self.actual_start_at = timezone.now()

        self.updated_by = user

        self.save()

    def register_worked_time(
        self,
        *,
        actual_start_at,
        actual_end_at,
        user=None,
        work_result="",
    ):
        if self.status not in (
            self.Status.APPROVED,
            self.Status.PARTIALLY_APPROVED,
            self.Status.IN_PROGRESS,
        ):
            raise ValidationError(
                "La solicitud no admite registro "
                "de trabajo realizado."
            )

        if actual_end_at <= actual_start_at:
            raise ValidationError(
                "El fin real debe ser posterior al inicio real."
            )

        self.actual_start_at = actual_start_at
        self.actual_end_at = actual_end_at
        self.calculate_actual_worked_minutes()

        self.status = self.Status.WORKED
        self.work_result = str(
            work_result or ""
        ).strip()
        self.work_registered_at = timezone.now()
        self.work_registered_by = user
        self.updated_by = user

        self.save()

    def send_to_review(self, user=None):
        if self.status != self.Status.WORKED:
            raise ValidationError(
                "Solo puedes revisar horas extras "
                "con trabajo registrado."
            )

        self.status = self.Status.UNDER_REVIEW
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "updated_by",
                "updated_at",
            ]
        )

    def verify(
        self,
        *,
        user,
        attendance_detected_minutes,
        approved_minutes=None,
        payable_minutes=None,
        compensatory_minutes=None,
        observation="",
    ):
        if self.status not in (
            self.Status.WORKED,
            self.Status.UNDER_REVIEW,
        ):
            raise ValidationError(
                "La solicitud no está disponible "
                "para verificación."
            )

        if attendance_detected_minutes < 0:
            raise ValidationError(
                "Los minutos detectados no pueden ser negativos."
            )

        self.attendance_detected_minutes = (
            attendance_detected_minutes
        )

        if approved_minutes is None:
            approved_minutes = min(
                self.actual_worked_minutes,
                self.authorized_minutes,
                attendance_detected_minutes,
            )

        if approved_minutes > self.actual_worked_minutes:
            raise ValidationError(
                "Los minutos aprobados no pueden superar "
                "los realmente trabajados."
            )

        if approved_minutes > attendance_detected_minutes:
            raise ValidationError(
                "Los minutos aprobados no pueden superar "
                "los detectados en asistencia."
            )

        self.approved_minutes = approved_minutes

        if self.compensation_type == (
            self.CompensationType.MIXED
        ):
            payable_minutes = payable_minutes or 0
            compensatory_minutes = compensatory_minutes or 0

            if (
                payable_minutes
                + compensatory_minutes
                != approved_minutes
            ):
                raise ValidationError(
                    "La suma pagable y compensatoria debe "
                    "coincidir con los minutos aprobados."
                )

            self.payable_minutes = payable_minutes
            self.compensatory_minutes = (
                compensatory_minutes
            )

        else:
            self.calculate_result_minutes()

        self.calculate_verification_result()
        self.calculate_result_minutes()

        self.status = self.Status.VERIFIED
        self.verified_at = timezone.now()
        self.verified_by = user
        self.verification_observation = str(
            observation or ""
        ).strip()
        self.updated_by = user

        self.save()

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
            self.Status.REJECTED,
            self.Status.CANCELLED,
            self.Status.VERIFIED,
            self.Status.CLOSED,
        ):
            raise ValidationError(
                "La solicitud ya no puede cancelarse."
            )

        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancelled_by = user
        self.cancellation_reason = reason
        self.updated_by = user

        self.save()

    def close(
        self,
        user,
        observation="",
    ):
        if self.status != self.Status.VERIFIED:
            raise ValidationError(
                "Solo puedes cerrar una solicitud verificada."
            )

        self.status = self.Status.CLOSED
        self.closed_at = timezone.now()
        self.closed_by = user

        if observation:
            self.notes = str(
                observation
            ).strip()

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
            self.Status.PENDING_SUPERVISOR,
            self.Status.PENDING_HUMAN_RESOURCES,
            self.Status.PENDING_MANAGEMENT,
            self.Status.APPROVED,
            self.Status.PARTIALLY_APPROVED,
            self.Status.IN_PROGRESS,
            self.Status.WORKED,
            self.Status.UNDER_REVIEW,
        ):
            raise ValidationError(
                "No puedes archivar una solicitud pendiente "
                "o en proceso."
            )

        self.archived_at = timezone.now()
        self.archived_by = user
        self.archived_reason = reason
        self.updated_by = user

        self.save()

    def restore(self, user=None):
        self.archived_at = None
        self.archived_by = None
        self.archived_reason = ""
        self.updated_by = user

        self.save()