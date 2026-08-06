# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .employee_profile import EmployeeProfile
from .work_location import WorkLocation


class LeaveRequest(models.Model):
    """
    Solicitud o registro de ausencia justificada.

    Permite manejar:

    - Permisos personales.
    - Permisos por horas.
    - Vacaciones.
    - Descansos médicos.
    - Licencias con o sin goce.
    - Comisión de servicio.
    - Trabajo remoto autorizado.
    - Compensaciones.
    - Ausencias justificadas.

    Conserva el flujo de solicitud, revisión, aprobación,
    rechazo, cancelación y cierre.
    """

    class LeaveType(models.TextChoices):
        PERSONAL_PERMISSION = (
            "personal_permission",
            "Permiso personal",
        )
        MEDICAL_APPOINTMENT = (
            "medical_appointment",
            "Cita médica",
        )
        MEDICAL_LEAVE = (
            "medical_leave",
            "Descanso médico",
        )
        VACATION = (
            "vacation",
            "Vacaciones",
        )
        PAID_LEAVE = (
            "paid_leave",
            "Licencia con goce",
        )
        UNPAID_LEAVE = (
            "unpaid_leave",
            "Licencia sin goce",
        )
        MATERNITY_LEAVE = (
            "maternity_leave",
            "Licencia por maternidad",
        )
        PATERNITY_LEAVE = (
            "paternity_leave",
            "Licencia por paternidad",
        )
        BEREAVEMENT_LEAVE = (
            "bereavement_leave",
            "Licencia por fallecimiento",
        )
        FAMILY_EMERGENCY = (
            "family_emergency",
            "Emergencia familiar",
        )
        STUDY_LEAVE = (
            "study_leave",
            "Permiso por estudios",
        )
        SERVICE_COMMISSION = (
            "service_commission",
            "Comisión de servicio",
        )
        REMOTE_WORK = (
            "remote_work",
            "Trabajo remoto autorizado",
        )
        COMPENSATORY_REST = (
            "compensatory_rest",
            "Descanso compensatorio",
        )
        WORK_ACCIDENT = (
            "work_accident",
            "Accidente de trabajo",
        )
        SICKNESS = (
            "sickness",
            "Enfermedad",
        )
        UNION_LEAVE = (
            "union_leave",
            "Licencia sindical",
        )
        JUDICIAL_SUMMONS = (
            "judicial_summons",
            "Citación judicial",
        )
        ELECTION_DUTY = (
            "election_duty",
            "Deber electoral",
        )
        JUSTIFIED_ABSENCE = (
            "justified_absence",
            "Ausencia justificada",
        )
        OTHER = (
            "other",
            "Otro",
        )

    class DurationType(models.TextChoices):
        FULL_DAY = (
            "full_day",
            "Día completo",
        )
        MULTIPLE_DAYS = (
            "multiple_days",
            "Varios días",
        )
        HOURS = (
            "hours",
            "Por horas",
        )
        HALF_DAY_MORNING = (
            "half_day_morning",
            "Media jornada de mañana",
        )
        HALF_DAY_AFTERNOON = (
            "half_day_afternoon",
            "Media jornada de tarde",
        )

    class RequestStatus(models.TextChoices):
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
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )
        IN_PROGRESS = (
            "in_progress",
            "En curso",
        )
        COMPLETED = (
            "completed",
            "Completada",
        )
        CLOSED = (
            "closed",
            "Cerrada",
        )

    class PaymentType(models.TextChoices):
        PAID = (
            "paid",
            "Con goce de haber",
        )
        UNPAID = (
            "unpaid",
            "Sin goce de haber",
        )
        PARTIALLY_PAID = (
            "partially_paid",
            "Pago parcial",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
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
            "Aprobación automática",
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
        related_name="leave_requests",
        verbose_name="Perfil laboral",
    )

    leave_type = models.CharField(
        max_length=40,
        choices=LeaveType.choices,
        db_index=True,
        verbose_name="Tipo de permiso o licencia",
    )

    duration_type = models.CharField(
        max_length=30,
        choices=DurationType.choices,
        default=DurationType.FULL_DAY,
        db_index=True,
        verbose_name="Tipo de duración",
    )

    status = models.CharField(
        max_length=30,
        choices=RequestStatus.choices,
        default=RequestStatus.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    payment_type = models.CharField(
        max_length=30,
        choices=PaymentType.choices,
        default=PaymentType.PAID,
        db_index=True,
        verbose_name="Condición de pago",
    )

    required_approval_level = models.CharField(
        max_length=30,
        choices=ApprovalLevel.choices,
        default=ApprovalLevel.SUPERVISOR,
        db_index=True,
        verbose_name="Nivel de aprobación requerido",
    )

    start_date = models.DateField(
        db_index=True,
        verbose_name="Fecha inicial",
    )

    end_date = models.DateField(
        db_index=True,
        verbose_name="Fecha final",
    )

    start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora inicial",
    )

    end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora final",
    )

    total_calendar_days = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Días calendario",
    )

    total_working_days = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Días laborables",
    )

    total_requested_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos solicitados",
    )

    total_approved_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos aprobados",
    )

    reason = models.TextField(
        verbose_name="Motivo",
    )

    destination = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Destino",
        help_text=(
            "Aplica principalmente para comisión de servicio "
            "o trabajo remoto."
        ),
    )

    destination_location = models.ForeignKey(
        WorkLocation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="leave_requests",
        verbose_name="Ubicación de destino",
    )

    contact_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Teléfono de contacto",
    )

    emergency_contact = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Contacto de emergencia",
    )

    affects_attendance = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Afecta asistencia",
    )

    affects_payroll = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Afecta planilla",
    )

    affects_evaluation = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Afecta evaluación",
    )

    generates_attendance_justification = models.BooleanField(
        default=True,
        verbose_name="Genera justificación de asistencia",
    )

    requires_compensation = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere compensación",
    )

    compensation_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos a compensar",
    )

    compensation_due_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha límite de compensación",
    )

    compensation_completed_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos compensados",
    )

    compensation_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Compensación completada el",
    )

    supporting_document = models.FileField(
        upload_to="attendance/leaves/%Y/%m/",
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

    medical_certificate_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Número de certificado médico",
    )

    medical_provider = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Centro o profesional médico",
    )

    diagnosis_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Referencia médica",
        help_text=(
            "Evita registrar información clínica innecesaria. "
            "Debe usarse solo cuando sea indispensable."
        ),
    )

    vacation_period_year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Año del periodo vacacional",
    )

    requested_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Presentada el",
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_leave_requests_submitted",
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
        related_name="attendance_leave_requests_supervised",
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
        related_name="attendance_leave_requests_hr_reviewed",
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
        related_name="attendance_leave_requests_management_reviewed",
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
        related_name="attendance_leave_requests_approved",
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
        related_name="attendance_leave_requests_rejected",
        verbose_name="Rechazada por",
    )

    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de rechazo",
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
        related_name="attendance_leave_requests_cancelled",
        verbose_name="Cancelada por",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Completada el",
    )

    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_leave_requests_completed",
        verbose_name="Completada por",
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
        related_name="attendance_leave_requests_closed",
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
        related_name="attendance_leave_requests_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_leave_requests_updated",
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
        related_name="attendance_leave_requests_archived",
        verbose_name="Archivada por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Solicitud de permiso o licencia"
        verbose_name_plural = "Solicitudes de permisos y licencias"

        ordering = (
            "-start_date",
            "-created_at",
        )

        indexes = (
            models.Index(
                fields=(
                    "employee_profile",
                    "status",
                    "start_date",
                ),
                name="att_leave_emp_status_start_idx",
            ),
            models.Index(
                fields=(
                    "leave_type",
                    "status",
                ),
                name="att_leave_type_status_idx",
            ),
            models.Index(
                fields=(
                    "start_date",
                    "end_date",
                ),
                name="att_leave_date_range_idx",
            ),
            models.Index(
                fields=(
                    "required_approval_level",
                    "status",
                ),
                name="att_leave_approval_status_idx",
            ),
            models.Index(
                fields=(
                    "affects_attendance",
                    "affects_payroll",
                    "affects_evaluation",
                ),
                name="att_leave_impacts_idx",
            ),
            models.Index(
                fields=(
                    "requires_compensation",
                    "compensation_due_date",
                ),
                name="att_leave_comp_due_idx",
            ),
            models.Index(
                fields=(
                    "vacation_period_year",
                    "leave_type",
                ),
                name="att_leave_vac_period_idx",
            ),
        )

        constraints = (
            models.CheckConstraint(
                condition=models.Q(
                    total_approved_minutes__lte=models.F(
                        "total_requested_minutes"
                    ),
                ),
                name="att_leave_approved_lte_requested",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    compensation_completed_minutes__lte=models.F(
                        "compensation_minutes"
                    ),
                ),
                name="att_leave_comp_done_lte_total",
            ),
        )

    def __str__(self):
        return (
            f"{self.request_number} - "
            f"{self.employee_profile.user.full_name} - "
            f"{self.get_leave_type_display()}"
        )

    @property
    def employee(self):
        return self.employee_profile.user

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_approved(self):
        return self.status in (
            self.RequestStatus.APPROVED,
            self.RequestStatus.PARTIALLY_APPROVED,
            self.RequestStatus.IN_PROGRESS,
            self.RequestStatus.COMPLETED,
            self.RequestStatus.CLOSED,
        )

    @property
    def is_pending(self):
        return self.status in (
            self.RequestStatus.SUBMITTED,
            self.RequestStatus.PENDING_SUPERVISOR,
            self.RequestStatus.PENDING_HUMAN_RESOURCES,
            self.RequestStatus.PENDING_MANAGEMENT,
        )

    @property
    def is_active_for_today(self):
        today = timezone.localdate()

        return (
            self.is_approved
            and self.start_date <= today <= self.end_date
            and self.archived_at is None
        )

    @property
    def compensation_pending_minutes(self):
        return max(
            0,
            self.compensation_minutes
            - self.compensation_completed_minutes,
        )

    def calculate_calendar_days(self):
        if not self.start_date or not self.end_date:
            self.total_calendar_days = 0
            return 0

        self.total_calendar_days = (
            self.end_date - self.start_date
        ).days + 1

        return self.total_calendar_days

    def overlaps_with_existing_request(self):
        queryset = (
            LeaveRequest.objects
            .filter(
                employee_profile=self.employee_profile,
                archived_at__isnull=True,
            )
            .exclude(
                pk=self.pk,
            )
            .exclude(
                status__in=(
                    self.RequestStatus.DRAFT,
                    self.RequestStatus.REJECTED,
                    self.RequestStatus.CANCELLED,
                ),
            )
            .filter(
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
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
            self.end_date
            and self.start_date
            and self.end_date < self.start_date
        ):
            errors["end_date"] = (
                "La fecha final no puede ser anterior "
                "a la fecha inicial."
            )

        hourly_duration_types = (
            self.DurationType.HOURS,
            self.DurationType.HALF_DAY_MORNING,
            self.DurationType.HALF_DAY_AFTERNOON,
        )

        if self.duration_type == self.DurationType.HOURS:
            if not self.start_time:
                errors["start_time"] = (
                    "Debes indicar la hora inicial."
                )

            if not self.end_time:
                errors["end_time"] = (
                    "Debes indicar la hora final."
                )

            if (
                self.start_date
                and self.end_date
                and self.start_date != self.end_date
            ):
                errors["end_date"] = (
                    "Un permiso por horas debe iniciar y "
                    "terminar el mismo día."
                )

            if (
                self.start_time
                and self.end_time
                and self.end_time <= self.start_time
            ):
                errors["end_time"] = (
                    "La hora final debe ser posterior "
                    "a la hora inicial."
                )

        elif self.duration_type not in hourly_duration_types:
            if self.start_time or self.end_time:
                errors["start_time"] = (
                    "No debes registrar horas para una solicitud "
                    "por día completo."
                )

        if (
            self.duration_type
            in (
                self.DurationType.HALF_DAY_MORNING,
                self.DurationType.HALF_DAY_AFTERNOON,
            )
            and self.start_date != self.end_date
        ):
            errors["end_date"] = (
                "Una solicitud de media jornada debe "
                "corresponder a un solo día."
            )

        if (
            self.total_approved_minutes
            > self.total_requested_minutes
        ):
            errors["total_approved_minutes"] = (
                "Los minutos aprobados no pueden superar "
                "los minutos solicitados."
            )

        if (
            self.requires_compensation
            and self.compensation_minutes <= 0
        ):
            errors["compensation_minutes"] = (
                "Debes indicar los minutos que deben compensarse."
            )

        if (
            not self.requires_compensation
            and self.compensation_minutes
        ):
            errors["compensation_minutes"] = (
                "Los minutos de compensación deben ser cero "
                "cuando no se requiere compensación."
            )

        if (
            self.compensation_completed_minutes
            > self.compensation_minutes
        ):
            errors["compensation_completed_minutes"] = (
                "Los minutos compensados no pueden superar "
                "los minutos pendientes."
            )

        if (
            self.compensation_due_date
            and not self.requires_compensation
        ):
            errors["requires_compensation"] = (
                "No puedes definir una fecha límite sin "
                "requerir compensación."
            )

        if (
            self.destination_location_id
            and self.destination_location.archived_at
        ):
            errors["destination_location"] = (
                "La ubicación de destino está archivada."
            )

        if (
            self.destination_location_id
            and not self.destination_location.is_active
        ):
            errors["destination_location"] = (
                "La ubicación de destino está inactiva."
            )

        if (
            self.leave_type
            == self.LeaveType.SERVICE_COMMISSION
            and not self.destination.strip()
            and not self.destination_location_id
        ):
            errors["destination"] = (
                "Debes indicar el destino de la comisión."
            )

        if (
            self.leave_type
            == self.LeaveType.REMOTE_WORK
            and not self.destination.strip()
            and not self.destination_location_id
        ):
            errors["destination"] = (
                "Debes indicar desde dónde se realizará "
                "el trabajo remoto."
            )

        if (
            self.leave_type
            == self.LeaveType.MEDICAL_LEAVE
            and not self.supporting_document
            and self.status
            in (
                self.RequestStatus.SUBMITTED,
                self.RequestStatus.PENDING_SUPERVISOR,
                self.RequestStatus.PENDING_HUMAN_RESOURCES,
                self.RequestStatus.PENDING_MANAGEMENT,
                self.RequestStatus.APPROVED,
            )
        ):
            errors["supporting_document"] = (
                "El descanso médico debe tener un documento "
                "sustentatorio."
            )

        if (
            self.leave_type == self.LeaveType.VACATION
            and not self.vacation_period_year
        ):
            errors["vacation_period_year"] = (
                "Debes indicar el periodo vacacional."
            )

        if (
            self.status
            in (
                self.RequestStatus.SUBMITTED,
                self.RequestStatus.PENDING_SUPERVISOR,
                self.RequestStatus.PENDING_HUMAN_RESOURCES,
                self.RequestStatus.PENDING_MANAGEMENT,
                self.RequestStatus.APPROVED,
                self.RequestStatus.PARTIALLY_APPROVED,
            )
            and self.employee_profile_id
            and self.start_date
            and self.end_date
            and self.overlaps_with_existing_request()
        ):
            errors["start_date"] = (
                "El trabajador ya tiene otra solicitud vigente "
                "durante esas fechas."
            )

        if (
            self.status == self.RequestStatus.REJECTED
            and not self.rejection_reason.strip()
        ):
            errors["rejection_reason"] = (
                "Debes indicar el motivo de rechazo."
            )

        if (
            self.status == self.RequestStatus.CANCELLED
            and not self.cancellation_reason.strip()
        ):
            errors["cancellation_reason"] = (
                "Debes indicar el motivo de cancelación."
            )

        if (
            self.status
            in (
                self.RequestStatus.APPROVED,
                self.RequestStatus.PARTIALLY_APPROVED,
            )
            and not self.approved_at
        ):
            errors["approved_at"] = (
                "Una solicitud aprobada debe tener "
                "fecha de aprobación."
            )

        if (
            self.status == self.RequestStatus.COMPLETED
            and not self.completed_at
        ):
            errors["completed_at"] = (
                "Una solicitud completada debe tener "
                "fecha de finalización."
            )

        if (
            self.status == self.RequestStatus.CLOSED
            and not self.closed_at
        ):
            errors["closed_at"] = (
                "Una solicitud cerrada debe tener "
                "fecha de cierre."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.calculate_calendar_days()
        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def submit(self, user=None):
        if self.status != self.RequestStatus.DRAFT:
            raise ValidationError(
                "Solo puedes presentar una solicitud en borrador."
            )

        if self.overlaps_with_existing_request():
            raise ValidationError(
                "Ya existe otra solicitud vigente durante "
                "las mismas fechas."
            )

        self.status = (
            self.RequestStatus.PENDING_SUPERVISOR
        )
        self.requested_at = timezone.now()
        self.requested_by = user
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "requested_at",
                "requested_by",
                "updated_by",
                "total_calendar_days",
                "updated_at",
            ]
        )

    def supervisor_approve(
        self,
        user,
        observation="",
    ):
        if self.status != (
            self.RequestStatus.PENDING_SUPERVISOR
        ):
            raise ValidationError(
                "La solicitud no está pendiente del supervisor."
            )

        self.supervisor_reviewed_at = timezone.now()
        self.supervisor_reviewed_by = user
        self.supervisor_observation = str(
            observation or ""
        ).strip()
        self.updated_by = user

        if (
            self.required_approval_level
            == self.ApprovalLevel.SUPERVISOR
        ):
            self._approve_internal(
                user=user,
                observation=observation,
            )

            return

        if (
            self.required_approval_level
            == self.ApprovalLevel.HUMAN_RESOURCES
        ):
            self.status = (
                self.RequestStatus
                .PENDING_HUMAN_RESOURCES
            )

        elif (
            self.required_approval_level
            == self.ApprovalLevel.MANAGEMENT
        ):
            self.status = (
                self.RequestStatus.PENDING_MANAGEMENT
            )

        else:
            self._approve_internal(
                user=user,
                observation=observation,
            )

            return

        self.save(
            update_fields=[
                "status",
                "supervisor_reviewed_at",
                "supervisor_reviewed_by",
                "supervisor_observation",
                "updated_by",
                "total_calendar_days",
                "updated_at",
            ]
        )

    def human_resources_approve(
        self,
        user,
        observation="",
    ):
        if self.status != (
            self.RequestStatus.PENDING_HUMAN_RESOURCES
        ):
            raise ValidationError(
                "La solicitud no está pendiente de "
                "recursos humanos."
            )

        self.human_resources_reviewed_at = timezone.now()
        self.human_resources_reviewed_by = user
        self.human_resources_observation = str(
            observation or ""
        ).strip()

        self._approve_internal(
            user=user,
            observation=observation,
        )

    def management_approve(
        self,
        user,
        observation="",
    ):
        if self.status != (
            self.RequestStatus.PENDING_MANAGEMENT
        ):
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
        )

    def _approve_internal(
        self,
        user,
        observation="",
        approved_minutes=None,
    ):
        if approved_minutes is None:
            approved_minutes = self.total_requested_minutes

        if approved_minutes > self.total_requested_minutes:
            raise ValidationError(
                "Los minutos aprobados no pueden superar "
                "los solicitados."
            )

        if approved_minutes < self.total_requested_minutes:
            self.status = (
                self.RequestStatus.PARTIALLY_APPROVED
            )
        else:
            self.status = self.RequestStatus.APPROVED

        self.total_approved_minutes = approved_minutes
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

        if self.status in (
            self.RequestStatus.APPROVED,
            self.RequestStatus.PARTIALLY_APPROVED,
            self.RequestStatus.IN_PROGRESS,
            self.RequestStatus.COMPLETED,
            self.RequestStatus.CLOSED,
            self.RequestStatus.CANCELLED,
        ):
            raise ValidationError(
                "La solicitud ya no puede rechazarse."
            )

        self.status = self.RequestStatus.REJECTED
        self.rejected_at = timezone.now()
        self.rejected_by = user
        self.rejection_reason = reason
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "rejected_at",
                "rejected_by",
                "rejection_reason",
                "updated_by",
                "total_calendar_days",
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

        if self.status in (
            self.RequestStatus.COMPLETED,
            self.RequestStatus.CLOSED,
            self.RequestStatus.REJECTED,
            self.RequestStatus.CANCELLED,
        ):
            raise ValidationError(
                "La solicitud ya no puede cancelarse."
            )

        self.status = self.RequestStatus.CANCELLED
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
                "total_calendar_days",
                "updated_at",
            ]
        )

    def start(self, user=None):
        if self.status not in (
            self.RequestStatus.APPROVED,
            self.RequestStatus.PARTIALLY_APPROVED,
        ):
            raise ValidationError(
                "Solo puedes iniciar una solicitud aprobada."
            )

        self.status = self.RequestStatus.IN_PROGRESS
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "updated_by",
                "total_calendar_days",
                "updated_at",
            ]
        )

    def complete(self, user=None):
        if self.status not in (
            self.RequestStatus.APPROVED,
            self.RequestStatus.PARTIALLY_APPROVED,
            self.RequestStatus.IN_PROGRESS,
        ):
            raise ValidationError(
                "La solicitud no puede completarse."
            )

        self.status = self.RequestStatus.COMPLETED
        self.completed_at = timezone.now()
        self.completed_by = user
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "completed_at",
                "completed_by",
                "updated_by",
                "total_calendar_days",
                "updated_at",
            ]
        )

    def register_compensation(
        self,
        minutes,
        user=None,
    ):
        if not self.requires_compensation:
            raise ValidationError(
                "Esta solicitud no requiere compensación."
            )

        if minutes <= 0:
            raise ValidationError(
                "Los minutos compensados deben ser mayores a cero."
            )

        new_total = (
            self.compensation_completed_minutes
            + minutes
        )

        if new_total > self.compensation_minutes:
            raise ValidationError(
                "La compensación supera los minutos pendientes."
            )

        self.compensation_completed_minutes = new_total
        self.updated_by = user

        if (
            self.compensation_completed_minutes
            == self.compensation_minutes
        ):
            self.compensation_completed_at = timezone.now()

        self.save(
            update_fields=[
                "compensation_completed_minutes",
                "compensation_completed_at",
                "updated_by",
                "total_calendar_days",
                "updated_at",
            ]
        )

    def close(
        self,
        user,
        observation="",
    ):
        if self.status != self.RequestStatus.COMPLETED:
            raise ValidationError(
                "Solo puedes cerrar una solicitud completada."
            )

        if (
            self.requires_compensation
            and self.compensation_pending_minutes > 0
        ):
            raise ValidationError(
                "No puedes cerrar la solicitud mientras exista "
                "tiempo pendiente de compensación."
            )

        self.status = self.RequestStatus.CLOSED
        self.closed_at = timezone.now()
        self.closed_by = user

        if observation:
            self.notes = str(
                observation
            ).strip()

        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "closed_at",
                "closed_by",
                "notes",
                "updated_by",
                "total_calendar_days",
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

        if self.is_pending:
            raise ValidationError(
                "No puedes archivar una solicitud pendiente."
            )

        if self.status == self.RequestStatus.IN_PROGRESS:
            raise ValidationError(
                "No puedes archivar una solicitud en curso."
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
                "total_calendar_days",
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
                "total_calendar_days",
                "updated_at",
            ]
        )