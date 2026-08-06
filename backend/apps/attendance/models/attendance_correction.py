# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .attendance_record import AttendanceRecord
from .daily_attendance import DailyAttendance
from .employee_profile import EmployeeProfile


class AttendanceCorrection(models.Model):
    """
    Solicitud y auditoría de correcciones de asistencia.

    Nunca modifica silenciosamente una marcación original.

    Permite solicitar correcciones sobre:

    - Hora de entrada.
    - Hora de salida.
    - Inicio o fin de refrigerio.
    - Tipo de marcación.
    - Ubicación.
    - Dispositivo.
    - Estado de validación.
    - Consolidado diario.
    - Minutos trabajados.
    - Tardanza.
    - Salida anticipada.
    - Horas extras.
    - Estado de asistencia.

    Al aprobarse, debe generarse una nueva marcación correctiva
    o actualizarse el consolidado mediante un servicio controlado,
    conservando siempre el valor anterior y el valor aprobado.
    """

    class CorrectionType(models.TextChoices):
        RECORD_DATETIME = (
            "record_datetime",
            "Fecha u hora de marcación",
        )
        RECORD_TYPE = (
            "record_type",
            "Tipo de marcación",
        )
        RECORD_LOCATION = (
            "record_location",
            "Ubicación de marcación",
        )
        RECORD_DEVICE = (
            "record_device",
            "Dispositivo de marcación",
        )
        RECORD_VALIDATION = (
            "record_validation",
            "Validación de marcación",
        )
        MISSING_CLOCK_IN = (
            "missing_clock_in",
            "Agregar entrada faltante",
        )
        MISSING_CLOCK_OUT = (
            "missing_clock_out",
            "Agregar salida faltante",
        )
        MISSING_BREAK_START = (
            "missing_break_start",
            "Agregar inicio de refrigerio",
        )
        MISSING_BREAK_END = (
            "missing_break_end",
            "Agregar fin de refrigerio",
        )
        REMOVE_DUPLICATE = (
            "remove_duplicate",
            "Anular marcación duplicada",
        )
        DAILY_STATUS = (
            "daily_status",
            "Estado de asistencia diaria",
        )
        WORKED_MINUTES = (
            "worked_minutes",
            "Minutos trabajados",
        )
        BREAK_MINUTES = (
            "break_minutes",
            "Minutos de refrigerio",
        )
        LATE_MINUTES = (
            "late_minutes",
            "Minutos de tardanza",
        )
        EARLY_DEPARTURE_MINUTES = (
            "early_departure_minutes",
            "Minutos de salida anticipada",
        )
        OVERTIME_MINUTES = (
            "overtime_minutes",
            "Minutos de horas extras",
        )
        OPERATIONAL_MINUTES = (
            "operational_minutes",
            "Minutos operativos",
        )
        SCHEDULE_ASSIGNMENT = (
            "schedule_assignment",
            "Asignación de horario",
        )
        HOLIDAY_OR_LEAVE = (
            "holiday_or_leave",
            "Feriado, permiso o licencia",
        )
        OTHER = (
            "other",
            "Otra corrección",
        )

    class TargetType(models.TextChoices):
        ATTENDANCE_RECORD = (
            "attendance_record",
            "Marcación de asistencia",
        )
        DAILY_ATTENDANCE = (
            "daily_attendance",
            "Asistencia diaria",
        )
        BOTH = (
            "both",
            "Marcación y asistencia diaria",
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
        APPLIED = (
            "applied",
            "Aplicada",
        )
        APPLICATION_ERROR = (
            "application_error",
            "Error al aplicar",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )
        CLOSED = (
            "closed",
            "Cerrada",
        )

    class RequestedByType(models.TextChoices):
        EMPLOYEE = (
            "employee",
            "Trabajador",
        )
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
        SYSTEM = (
            "system",
            "Sistema",
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

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    correction_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Número de corrección",
    )

    employee_profile = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.PROTECT,
        related_name="attendance_corrections",
        verbose_name="Perfil laboral",
    )

    attendance_record = models.ForeignKey(
        AttendanceRecord,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="correction_requests",
        verbose_name="Marcación original",
    )

    daily_attendance = models.ForeignKey(
        DailyAttendance,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="correction_requests",
        verbose_name="Asistencia diaria",
    )

    generated_record = models.ForeignKey(
        AttendanceRecord,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="generated_by_corrections",
        verbose_name="Marcación correctiva generada",
    )

    correction_type = models.CharField(
        max_length=40,
        choices=CorrectionType.choices,
        db_index=True,
        verbose_name="Tipo de corrección",
    )

    target_type = models.CharField(
        max_length=30,
        choices=TargetType.choices,
        db_index=True,
        verbose_name="Objeto de corrección",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    requested_by_type = models.CharField(
        max_length=30,
        choices=RequestedByType.choices,
        default=RequestedByType.EMPLOYEE,
        db_index=True,
        verbose_name="Solicitada por tipo",
    )

    required_approval_level = models.CharField(
        max_length=30,
        choices=ApprovalLevel.choices,
        default=ApprovalLevel.SUPERVISOR,
        db_index=True,
        verbose_name="Nivel de aprobación requerido",
    )

    correction_date = models.DateField(
        db_index=True,
        verbose_name="Fecha afectada",
    )

    reason = models.TextField(
        verbose_name="Motivo de corrección",
    )

    employee_explanation = models.TextField(
        blank=True,
        verbose_name="Explicación del trabajador",
    )

    supervisor_observation = models.TextField(
        blank=True,
        verbose_name="Observación del supervisor",
    )

    human_resources_observation = models.TextField(
        blank=True,
        verbose_name="Observación de recursos humanos",
    )

    management_observation = models.TextField(
        blank=True,
        verbose_name="Observación de gerencia",
    )

    previous_values = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Valores anteriores",
        help_text=(
            "Copia inmutable de los valores existentes al momento "
            "de presentar la corrección."
        ),
    )

    requested_values = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Valores solicitados",
    )

    approved_values = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Valores aprobados",
    )

    application_result = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resultado de aplicación",
    )

    supporting_document = models.FileField(
        upload_to="attendance/corrections/%Y/%m/",
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

    requires_document = models.BooleanField(
        default=False,
        verbose_name="Requiere documento sustentatorio",
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

    requires_daily_recalculation = models.BooleanField(
        default=True,
        verbose_name="Requiere recalcular asistencia diaria",
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
        related_name="attendance_corrections_requested",
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
        related_name="attendance_corrections_supervisor_reviewed",
        verbose_name="Revisada por supervisor",
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
        related_name="attendance_corrections_hr_reviewed",
        verbose_name="Revisada por recursos humanos",
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
        related_name="attendance_corrections_management_reviewed",
        verbose_name="Revisada por gerencia",
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
        related_name="attendance_corrections_approved",
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
        related_name="attendance_corrections_rejected",
        verbose_name="Rechazada por",
    )

    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de rechazo",
    )

    applied_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Aplicada el",
    )

    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_corrections_applied",
        verbose_name="Aplicada por",
    )

    application_error = models.TextField(
        blank=True,
        verbose_name="Error de aplicación",
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
        related_name="attendance_corrections_cancelled",
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
        related_name="attendance_corrections_closed",
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
        related_name="attendance_corrections_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_corrections_updated",
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
        related_name="attendance_corrections_archived",
        verbose_name="Archivada por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Corrección de asistencia"
        verbose_name_plural = "Correcciones de asistencia"

        ordering = (
            "-correction_date",
            "-created_at",
        )

        indexes = (
            models.Index(
                fields=(
                    "employee_profile",
                    "correction_date",
                    "status",
                ),
                name="att_corr_emp_date_status_idx",
            ),
            models.Index(
                fields=(
                    "attendance_record",
                    "status",
                ),
                name="att_corr_record_status_idx",
            ),
            models.Index(
                fields=(
                    "daily_attendance",
                    "status",
                ),
                name="att_corr_daily_status_idx",
            ),
            models.Index(
                fields=(
                    "correction_type",
                    "target_type",
                ),
                name="att_corr_type_target_idx",
            ),
            models.Index(
                fields=(
                    "required_approval_level",
                    "status",
                ),
                name="att_corr_approval_status_idx",
            ),
            models.Index(
                fields=(
                    "affects_attendance",
                    "affects_payroll",
                    "affects_evaluation",
                ),
                name="att_corr_impacts_idx",
            ),
            models.Index(
                fields=(
                    "requested_at",
                    "approved_at",
                    "applied_at",
                ),
                name="att_corr_flow_dates_idx",
            ),
        )

        constraints = (
            models.UniqueConstraint(
                fields=(
                    "attendance_record",
                ),
                condition=(
                    models.Q(
                        archived_at__isnull=True,
                    )
                    & models.Q(
                        status__in=(
                            "submitted",
                            "pending_supervisor",
                            "pending_human_resources",
                            "pending_management",
                            "approved",
                            "partially_approved",
                        ),
                    )
                    & models.Q(
                        attendance_record__isnull=False,
                    )
                ),
                name="att_corr_one_open_per_record",
            ),
        )

    def __str__(self):
        return (
            f"{self.correction_number} - "
            f"{self.employee_profile.user.full_name} - "
            f"{self.get_correction_type_display()}"
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
        )

    @property
    def is_approved(self):
        return self.status in (
            self.Status.APPROVED,
            self.Status.PARTIALLY_APPROVED,
        )

    @property
    def can_be_applied(self):
        return (
            self.is_approved
            and self.archived_at is None
            and not self.applied_at
        )

    def capture_previous_values(self):
        """
        Captura los valores actuales antes de presentar la solicitud.

        Esta función no aplica cambios. Solo conserva una fotografía
        de auditoría del estado anterior.
        """

        values = {}

        if self.attendance_record_id:
            record = self.attendance_record

            values["attendance_record"] = {
                "id": str(record.id),
                "record_type": record.record_type,
                "occurred_at": (
                    record.occurred_at.isoformat()
                    if record.occurred_at
                    else None
                ),
                "local_date": (
                    record.local_date.isoformat()
                    if record.local_date
                    else None
                ),
                "local_time": (
                    record.local_time.isoformat()
                    if record.local_time
                    else None
                ),
                "source_type": record.source_type,
                "validation_status": (
                    record.validation_status
                ),
                "location_status": record.location_status,
                "work_location_id": (
                    str(record.work_location_id)
                    if record.work_location_id
                    else None
                ),
                "device_id": (
                    str(record.device_id)
                    if record.device_id
                    else None
                ),
                "latitude": (
                    str(record.latitude)
                    if record.latitude is not None
                    else None
                ),
                "longitude": (
                    str(record.longitude)
                    if record.longitude is not None
                    else None
                ),
                "observation": record.observation,
                "archived_at": (
                    record.archived_at.isoformat()
                    if record.archived_at
                    else None
                ),
            }

        if self.daily_attendance_id:
            daily = self.daily_attendance

            values["daily_attendance"] = {
                "id": str(daily.id),
                "date": (
                    daily.date.isoformat()
                    if daily.date
                    else None
                ),
                "attendance_status": (
                    daily.attendance_status
                ),
                "processing_status": (
                    daily.processing_status
                ),
                "first_clock_in_at": (
                    daily.first_clock_in_at.isoformat()
                    if daily.first_clock_in_at
                    else None
                ),
                "last_clock_out_at": (
                    daily.last_clock_out_at.isoformat()
                    if daily.last_clock_out_at
                    else None
                ),
                "first_break_start_at": (
                    daily.first_break_start_at.isoformat()
                    if daily.first_break_start_at
                    else None
                ),
                "last_break_end_at": (
                    daily.last_break_end_at.isoformat()
                    if daily.last_break_end_at
                    else None
                ),
                "effective_work_minutes": (
                    daily.effective_work_minutes
                ),
                "valid_break_minutes": (
                    daily.valid_break_minutes
                ),
                "late_minutes": daily.late_minutes,
                "early_departure_minutes": (
                    daily.early_departure_minutes
                ),
                "overtime_minutes": (
                    daily.overtime_minutes
                ),
                "operational_work_minutes": (
                    daily.operational_work_minutes
                ),
                "requires_review": daily.requires_review,
                "review_reasons": (
                    daily.review_reasons
                ),
            }

        self.previous_values = values

        return values

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
            self.attendance_record_id
            and self.attendance_record.employee_profile_id
            != self.employee_profile_id
        ):
            errors["attendance_record"] = (
                "La marcación no corresponde al trabajador."
            )

        if (
            self.daily_attendance_id
            and self.daily_attendance.employee_profile_id
            != self.employee_profile_id
        ):
            errors["daily_attendance"] = (
                "La asistencia diaria no corresponde al trabajador."
            )

        if (
            self.attendance_record_id
            and self.attendance_record.local_date
            != self.correction_date
        ):
            errors["correction_date"] = (
                "La fecha de corrección debe coincidir con "
                "la fecha de la marcación."
            )

        if (
            self.daily_attendance_id
            and self.daily_attendance.date
            != self.correction_date
        ):
            errors["correction_date"] = (
                "La fecha de corrección debe coincidir con "
                "la asistencia diaria."
            )

        if (
            self.target_type
            == self.TargetType.ATTENDANCE_RECORD
            and not self.attendance_record_id
            and self.correction_type
            not in (
                self.CorrectionType.MISSING_CLOCK_IN,
                self.CorrectionType.MISSING_CLOCK_OUT,
                self.CorrectionType.MISSING_BREAK_START,
                self.CorrectionType.MISSING_BREAK_END,
            )
        ):
            errors["attendance_record"] = (
                "Debes seleccionar la marcación que será corregida."
            )

        if (
            self.target_type
            == self.TargetType.DAILY_ATTENDANCE
            and not self.daily_attendance_id
        ):
            errors["daily_attendance"] = (
                "Debes seleccionar la asistencia diaria."
            )

        if (
            self.target_type == self.TargetType.BOTH
            and (
                not self.attendance_record_id
                or not self.daily_attendance_id
            )
        ):
            errors["target_type"] = (
                "Una corrección combinada requiere la marcación "
                "y la asistencia diaria."
            )

        if (
            not self.attendance_record_id
            and not self.daily_attendance_id
        ):
            missing_record_types = (
                self.CorrectionType.MISSING_CLOCK_IN,
                self.CorrectionType.MISSING_CLOCK_OUT,
                self.CorrectionType.MISSING_BREAK_START,
                self.CorrectionType.MISSING_BREAK_END,
            )

            if self.correction_type not in missing_record_types:
                errors["attendance_record"] = (
                    "Debes vincular una marcación o una "
                    "asistencia diaria."
                )

        if (
            self.generated_record_id
            and self.generated_record.employee_profile_id
            != self.employee_profile_id
        ):
            errors["generated_record"] = (
                "La marcación generada no corresponde "
                "al trabajador."
            )

        if (
            self.generated_record_id
            and self.status
            not in (
                self.Status.APPLIED,
                self.Status.CLOSED,
            )
        ):
            errors["generated_record"] = (
                "Solo una corrección aplicada puede tener "
                "una marcación correctiva generada."
            )

        if (
            self.requires_document
            and not self.supporting_document
            and self.status != self.Status.DRAFT
        ):
            errors["supporting_document"] = (
                "Debes adjuntar el documento sustentatorio."
            )

        if (
            self.status != self.Status.DRAFT
            and not self.requested_values
        ):
            errors["requested_values"] = (
                "Debes indicar los valores solicitados."
            )

        if (
            self.status
            in (
                self.Status.APPROVED,
                self.Status.PARTIALLY_APPROVED,
                self.Status.APPLIED,
                self.Status.CLOSED,
            )
            and not self.approved_values
        ):
            errors["approved_values"] = (
                "Una corrección aprobada debe indicar "
                "los valores autorizados."
            )

        if (
            self.status
            in (
                self.Status.SUBMITTED,
                self.Status.PENDING_SUPERVISOR,
                self.Status.PENDING_HUMAN_RESOURCES,
                self.Status.PENDING_MANAGEMENT,
            )
            and not self.requested_at
        ):
            errors["requested_at"] = (
                "Una corrección presentada debe tener "
                "fecha de presentación."
            )

        if (
            self.status
            in (
                self.Status.APPROVED,
                self.Status.PARTIALLY_APPROVED,
            )
            and not self.approved_at
        ):
            errors["approved_at"] = (
                "Una corrección aprobada debe tener "
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
            self.status == self.Status.APPLIED
            and not self.applied_at
        ):
            errors["applied_at"] = (
                "Una corrección aplicada debe tener "
                "fecha de aplicación."
            )

        if (
            self.status == self.Status.APPLICATION_ERROR
            and not self.application_error.strip()
        ):
            errors["application_error"] = (
                "Debes registrar el error de aplicación."
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
                "Una corrección cerrada debe tener fecha de cierre."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def submit(self, user=None):
        if self.status != self.Status.DRAFT:
            raise ValidationError(
                "Solo puedes presentar una corrección en borrador."
            )

        if not self.requested_values:
            raise ValidationError(
                "Debes indicar los valores solicitados."
            )

        self.capture_previous_values()

        self.requested_at = timezone.now()
        self.requested_by = user
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

        else:
            self.status = self.Status.PENDING_MANAGEMENT

        self.save(
            update_fields=[
                "previous_values",
                "requested_at",
                "requested_by",
                "updated_by",
                "status",
                "updated_at",
            ]
        )

    def supervisor_approve(
        self,
        user,
        observation="",
        approved_values=None,
    ):
        if self.status != self.Status.PENDING_SUPERVISOR:
            raise ValidationError(
                "La corrección no está pendiente del supervisor."
            )

        self.supervisor_reviewed_at = timezone.now()
        self.supervisor_reviewed_by = user
        self.supervisor_observation = str(
            observation or ""
        ).strip()
        self.updated_by = user

        self._approve_internal(
            user=user,
            observation=observation,
            approved_values=approved_values,
        )

    def human_resources_approve(
        self,
        user,
        observation="",
        approved_values=None,
    ):
        if (
            self.status
            != self.Status.PENDING_HUMAN_RESOURCES
        ):
            raise ValidationError(
                "La corrección no está pendiente de "
                "recursos humanos."
            )

        self.human_resources_reviewed_at = timezone.now()
        self.human_resources_reviewed_by = user
        self.human_resources_observation = str(
            observation or ""
        ).strip()
        self.updated_by = user

        self._approve_internal(
            user=user,
            observation=observation,
            approved_values=approved_values,
        )

    def management_approve(
        self,
        user,
        observation="",
        approved_values=None,
    ):
        if self.status != self.Status.PENDING_MANAGEMENT:
            raise ValidationError(
                "La corrección no está pendiente de gerencia."
            )

        self.management_reviewed_at = timezone.now()
        self.management_reviewed_by = user
        self.management_observation = str(
            observation or ""
        ).strip()
        self.updated_by = user

        self._approve_internal(
            user=user,
            observation=observation,
            approved_values=approved_values,
        )

    def _approve_internal(
        self,
        user,
        observation="",
        approved_values=None,
    ):
        approved_values = (
            approved_values
            if approved_values is not None
            else self.requested_values
        )

        if not approved_values:
            raise ValidationError(
                "Debes indicar los valores aprobados."
            )

        self.approved_values = approved_values
        self.approved_at = timezone.now()
        self.approved_by = user
        self.approval_observation = str(
            observation or ""
        ).strip()
        self.updated_by = user

        if approved_values == self.requested_values:
            self.status = self.Status.APPROVED
        else:
            self.status = self.Status.PARTIALLY_APPROVED

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
                "Solo puedes rechazar una corrección pendiente."
            )

        self.status = self.Status.REJECTED
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
                "updated_at",
            ]
        )

    def mark_applied(
        self,
        user,
        result=None,
        generated_record=None,
    ):
        if not self.can_be_applied:
            raise ValidationError(
                "La corrección no está aprobada o ya fue aplicada."
            )

        if (
            generated_record
            and generated_record.employee_profile_id
            != self.employee_profile_id
        ):
            raise ValidationError(
                "La marcación generada no corresponde "
                "al trabajador."
            )

        self.status = self.Status.APPLIED
        self.applied_at = timezone.now()
        self.applied_by = user
        self.application_result = result or {}
        self.generated_record = generated_record
        self.application_error = ""
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "applied_at",
                "applied_by",
                "application_result",
                "generated_record",
                "application_error",
                "updated_by",
                "updated_at",
            ]
        )

    def mark_application_error(
        self,
        error,
        user=None,
        result=None,
    ):
        error = str(
            error or ""
        ).strip()

        if not error:
            raise ValidationError(
                "Debes indicar el error de aplicación."
            )

        if not self.is_approved:
            raise ValidationError(
                "Solo una corrección aprobada puede registrar "
                "un error de aplicación."
            )

        self.status = self.Status.APPLICATION_ERROR
        self.application_error = error
        self.application_result = result or {}
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "application_error",
                "application_result",
                "updated_by",
                "updated_at",
            ]
        )

    def retry_application(self, user=None):
        if self.status != self.Status.APPLICATION_ERROR:
            raise ValidationError(
                "La corrección no tiene un error de aplicación."
            )

        self.status = self.Status.APPROVED
        self.application_error = ""
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "application_error",
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

        if self.status in (
            self.Status.APPLIED,
            self.Status.CLOSED,
            self.Status.REJECTED,
            self.Status.CANCELLED,
        ):
            raise ValidationError(
                "La corrección ya no puede cancelarse."
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

    def close(
        self,
        user,
        observation="",
    ):
        if self.status != self.Status.APPLIED:
            raise ValidationError(
                "Solo puedes cerrar una corrección aplicada."
            )

        self.status = self.Status.CLOSED
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

        if self.is_pending or self.is_approved:
            raise ValidationError(
                "No puedes archivar una corrección pendiente "
                "o aprobada sin aplicar."
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