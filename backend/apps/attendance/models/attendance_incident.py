# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .attendance_record import AttendanceRecord
from .daily_attendance import DailyAttendance
from .employee_profile import EmployeeProfile


class AttendanceIncident(models.Model):
    """
    Incidencia relacionada con la asistencia de un trabajador.

    Permite registrar y revisar:

    - Tardanzas.
    - Ausencias.
    - Salidas anticipadas.
    - Marcaciones incompletas.
    - Exceso de refrigerio.
    - Problemas de ubicación.
    - Uso de dispositivos no autorizados.
    - Marcaciones duplicadas.
    - Diferencias de horario.
    - Justificaciones y documentos.
    - Responsabilidad del trabajador o causas externas.
    """

    class IncidentType(models.TextChoices):
        LATE_ARRIVAL = (
            "late_arrival",
            "Tardanza",
        )
        ABSENCE = (
            "absence",
            "Ausencia",
        )
        EARLY_DEPARTURE = (
            "early_departure",
            "Salida anticipada",
        )
        MISSING_CLOCK_IN = (
            "missing_clock_in",
            "Falta marcación de entrada",
        )
        MISSING_CLOCK_OUT = (
            "missing_clock_out",
            "Falta marcación de salida",
        )
        MISSING_BREAK_START = (
            "missing_break_start",
            "Falta inicio de refrigerio",
        )
        MISSING_BREAK_END = (
            "missing_break_end",
            "Falta fin de refrigerio",
        )
        EXCESS_BREAK = (
            "excess_break",
            "Exceso de refrigerio",
        )
        DUPLICATE_CLOCKING = (
            "duplicate_clocking",
            "Marcación duplicada",
        )
        INVALID_SEQUENCE = (
            "invalid_sequence",
            "Secuencia de marcación inválida",
        )
        OUTSIDE_GEOFENCE = (
            "outside_geofence",
            "Marcación fuera de geocerca",
        )
        LOW_LOCATION_ACCURACY = (
            "low_location_accuracy",
            "Precisión de ubicación insuficiente",
        )
        MISSING_LOCATION = (
            "missing_location",
            "Ubicación no registrada",
        )
        UNAUTHORIZED_LOCATION = (
            "unauthorized_location",
            "Ubicación no autorizada",
        )
        UNAUTHORIZED_DEVICE = (
            "unauthorized_device",
            "Dispositivo no autorizado",
        )
        DEVICE_BLOCKED = (
            "device_blocked",
            "Dispositivo bloqueado",
        )
        DEVICE_TIME_DIFFERENCE = (
            "device_time_difference",
            "Diferencia de hora del dispositivo",
        )
        OFFLINE_CLOCKING = (
            "offline_clocking",
            "Marcación sin conexión",
        )
        OFFLINE_SYNC_DELAY = (
            "offline_sync_delay",
            "Demora en sincronización",
        )
        MANUAL_CLOCKING = (
            "manual_clocking",
            "Marcación manual",
        )
        SCHEDULE_MISMATCH = (
            "schedule_mismatch",
            "Diferencia con el horario",
        )
        INSUFFICIENT_WORK_TIME = (
            "insufficient_work_time",
            "Tiempo trabajado insuficiente",
        )
        UNCLASSIFIED_TIME = (
            "unclassified_time",
            "Tiempo sin clasificar",
        )
        OVERTIME_WITHOUT_APPROVAL = (
            "overtime_without_approval",
            "Horas extras sin aprobación",
        )
        PHOTO_MISSING = (
            "photo_missing",
            "Fotografía no registrada",
        )
        PHOTO_REVIEW = (
            "photo_review",
            "Fotografía requiere revisión",
        )
        OTHER = (
            "other",
            "Otra incidencia",
        )

    class Severity(models.TextChoices):
        INFORMATION = (
            "information",
            "Informativa",
        )
        LOW = (
            "low",
            "Baja",
        )
        MEDIUM = (
            "medium",
            "Media",
        )
        HIGH = (
            "high",
            "Alta",
        )
        CRITICAL = (
            "critical",
            "Crítica",
        )

    class Status(models.TextChoices):
        OPEN = (
            "open",
            "Abierta",
        )
        PENDING_EMPLOYEE = (
            "pending_employee",
            "Pendiente del trabajador",
        )
        PENDING_SUPERVISOR = (
            "pending_supervisor",
            "Pendiente del supervisor",
        )
        UNDER_REVIEW = (
            "under_review",
            "En revisión",
        )
        JUSTIFIED = (
            "justified",
            "Justificada",
        )
        NOT_JUSTIFIED = (
            "not_justified",
            "No justificada",
        )
        CORRECTED = (
            "corrected",
            "Corregida",
        )
        DISMISSED = (
            "dismissed",
            "Descartada",
        )
        CLOSED = (
            "closed",
            "Cerrada",
        )
        CANCELLED = (
            "cancelled",
            "Anulada",
        )

    class ResponsibilityType(models.TextChoices):
        UNDETERMINED = (
            "undetermined",
            "Por determinar",
        )
        EMPLOYEE = (
            "employee",
            "Responsabilidad del trabajador",
        )
        COMPANY = (
            "company",
            "Responsabilidad de la empresa",
        )
        CLIENT = (
            "client",
            "Responsabilidad del cliente",
        )
        TRANSPORT = (
            "transport",
            "Problema de transporte",
        )
        SYSTEM = (
            "system",
            "Problema del sistema",
        )
        DEVICE = (
            "device",
            "Problema del dispositivo",
        )
        EXTERNAL = (
            "external",
            "Causa externa",
        )
        FORCE_MAJEURE = (
            "force_majeure",
            "Fuerza mayor",
        )
        SHARED = (
            "shared",
            "Responsabilidad compartida",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )

    class ResolutionType(models.TextChoices):
        NONE = (
            "none",
            "Sin resolución",
        )
        JUSTIFICATION_ACCEPTED = (
            "justification_accepted",
            "Justificación aceptada",
        )
        JUSTIFICATION_REJECTED = (
            "justification_rejected",
            "Justificación rechazada",
        )
        RECORD_CORRECTED = (
            "record_corrected",
            "Marcación corregida",
        )
        SCHEDULE_CORRECTED = (
            "schedule_corrected",
            "Horario corregido",
        )
        PERMISSION_REGISTERED = (
            "permission_registered",
            "Permiso registrado",
        )
        VACATION_REGISTERED = (
            "vacation_registered",
            "Vacaciones registradas",
        )
        LEAVE_REGISTERED = (
            "leave_registered",
            "Licencia registrada",
        )
        DEVICE_AUTHORIZED = (
            "device_authorized",
            "Dispositivo autorizado",
        )
        LOCATION_AUTHORIZED = (
            "location_authorized",
            "Ubicación autorizada",
        )
        NO_ACTION_REQUIRED = (
            "no_action_required",
            "No requiere acción",
        )
        DISCIPLINARY_ACTION = (
            "disciplinary_action",
            "Acción disciplinaria",
        )
        OTHER = (
            "other",
            "Otra resolución",
        )

    class ImpactType(models.TextChoices):
        NONE = (
            "none",
            "Sin impacto",
        )
        ATTENDANCE = (
            "attendance",
            "Afecta asistencia",
        )
        PAYROLL = (
            "payroll",
            "Afecta planilla",
        )
        EVALUATION = (
            "evaluation",
            "Afecta evaluación",
        )
        ATTENDANCE_AND_EVALUATION = (
            "attendance_and_evaluation",
            "Afecta asistencia y evaluación",
        )
        PAYROLL_AND_EVALUATION = (
            "payroll_and_evaluation",
            "Afecta planilla y evaluación",
        )
        ALL = (
            "all",
            "Afecta asistencia, planilla y evaluación",
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
        related_name="attendance_incidents",
        verbose_name="Perfil laboral",
    )

    daily_attendance = models.ForeignKey(
        DailyAttendance,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="incidents",
        verbose_name="Asistencia diaria",
    )

    attendance_record = models.ForeignKey(
        AttendanceRecord,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="incidents",
        verbose_name="Marcación relacionada",
    )

    incident_type = models.CharField(
        max_length=40,
        choices=IncidentType.choices,
        db_index=True,
        verbose_name="Tipo de incidencia",
    )

    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.MEDIUM,
        db_index=True,
        verbose_name="Severidad",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
        verbose_name="Estado",
    )

    responsibility_type = models.CharField(
        max_length=30,
        choices=ResponsibilityType.choices,
        default=ResponsibilityType.UNDETERMINED,
        db_index=True,
        verbose_name="Responsabilidad",
    )

    impact_type = models.CharField(
        max_length=40,
        choices=ImpactType.choices,
        default=ImpactType.ATTENDANCE,
        db_index=True,
        verbose_name="Impacto",
    )

    incident_date = models.DateField(
        db_index=True,
        verbose_name="Fecha de incidencia",
    )

    detected_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Detectada el",
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Título",
    )

    description = models.TextField(
        verbose_name="Descripción",
    )

    detected_value = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Valor detectado",
    )

    expected_value = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Valor esperado",
    )

    affected_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos afectados",
    )

    deductible_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos descontables",
    )

    justified_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos justificados",
    )

    evaluation_penalty_points = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Puntos de penalización",
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

    automatically_generated = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Generada automáticamente",
    )

    generation_rule = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Regla de generación",
    )

    generation_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos de generación",
    )

    requires_employee_explanation = models.BooleanField(
        default=False,
        verbose_name="Requiere explicación del trabajador",
    )

    employee_explanation = models.TextField(
        blank=True,
        verbose_name="Explicación del trabajador",
    )

    employee_explained_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Explicada por el trabajador el",
    )

    employee_explanation_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP de explicación del trabajador",
    )

    employee_accepts_incident = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Trabajador acepta la incidencia",
    )

    justification_requested = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Justificación solicitada",
    )

    justification_requested_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Justificación solicitada el",
    )

    justification_requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_justifications_requested",
        verbose_name="Justificación solicitada por",
    )

    justification_due_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Plazo para justificar",
    )

    justification_text = models.TextField(
        blank=True,
        verbose_name="Justificación",
    )

    justification_submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Justificación presentada el",
    )

    justification_document = models.FileField(
        upload_to="attendance/incidents/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Documento sustentatorio",
    )

    justification_document_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre del documento",
    )

    justification_document_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tipo de documento",
    )

    justification_document_size = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Tamaño del documento",
    )

    justification_reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Justificación revisada el",
    )

    justification_reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_justifications_reviewed",
        verbose_name="Justificación revisada por",
    )

    justification_review_notes = models.TextField(
        blank=True,
        verbose_name="Observación de justificación",
    )

    resolution_type = models.CharField(
        max_length=40,
        choices=ResolutionType.choices,
        default=ResolutionType.NONE,
        db_index=True,
        verbose_name="Tipo de resolución",
    )

    resolution_notes = models.TextField(
        blank=True,
        verbose_name="Resolución",
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Resuelta el",
    )

    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_incidents_resolved",
        verbose_name="Resuelta por",
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
        related_name="attendance_incidents_closed",
        verbose_name="Cerrada por",
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Anulada el",
    )

    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_incidents_cancelled",
        verbose_name="Anulada por",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de anulación",
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
        related_name="attendance_incidents_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_incidents_updated",
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
        related_name="attendance_incidents_archived",
        verbose_name="Archivada por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Incidencia de asistencia"
        verbose_name_plural = "Incidencias de asistencia"

        ordering = (
            "-incident_date",
            "-detected_at",
        )

        indexes = (
            models.Index(
                fields=(
                    "employee_profile",
                    "incident_date",
                    "status",
                ),
                name="att_inc_emp_date_status_idx",
            ),
            models.Index(
                fields=(
                    "daily_attendance",
                    "incident_type",
                ),
                name="att_inc_daily_type_idx",
            ),
            models.Index(
                fields=(
                    "attendance_record",
                    "status",
                ),
                name="att_inc_record_status_idx",
            ),
            models.Index(
                fields=(
                    "severity",
                    "status",
                    "incident_date",
                ),
                name="att_inc_sev_status_date_idx",
            ),
            models.Index(
                fields=(
                    "responsibility_type",
                    "affects_evaluation",
                ),
                name="att_inc_resp_eval_idx",
            ),
            models.Index(
                fields=(
                    "affects_payroll",
                    "affects_attendance",
                    "incident_date",
                ),
                name="att_inc_pay_att_date_idx",
            ),
            models.Index(
                fields=(
                    "justification_requested",
                    "justification_due_at",
                    "status",
                ),
                name="att_inc_just_due_status_idx",
            ),
            models.Index(
                fields=(
                    "automatically_generated",
                    "generation_rule",
                ),
                name="att_inc_auto_rule_idx",
            ),
        )

        constraints = (
            models.CheckConstraint(
                condition=models.Q(
                    justified_minutes__lte=models.F(
                        "affected_minutes"
                    ),
                ),
                name="att_inc_justified_lte_affected",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    deductible_minutes__lte=models.F(
                        "affected_minutes"
                    ),
                ),
                name="att_inc_deduct_lte_affected",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    evaluation_penalty_points__gte=0,
                ),
                name="att_inc_penalty_positive",
            ),
        )

    def __str__(self):
        return (
            f"{self.employee_profile.user.full_name} - "
            f"{self.get_incident_type_display()} - "
            f"{self.incident_date}"
        )

    @property
    def employee(self):
        return self.employee_profile.user

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_open(self):
        return self.status in (
            self.Status.OPEN,
            self.Status.PENDING_EMPLOYEE,
            self.Status.PENDING_SUPERVISOR,
            self.Status.UNDER_REVIEW,
        )

    @property
    def is_resolved(self):
        return self.status in (
            self.Status.JUSTIFIED,
            self.Status.NOT_JUSTIFIED,
            self.Status.CORRECTED,
            self.Status.DISMISSED,
            self.Status.CLOSED,
        )

    @property
    def justification_is_overdue(self):
        if not self.justification_due_at:
            return False

        if self.justification_submitted_at:
            return False

        return (
            self.justification_due_at
            < timezone.now()
        )

    @property
    def remaining_unjustified_minutes(self):
        return max(
            0,
            self.affected_minutes
            - self.justified_minutes,
        )

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
            != self.incident_date
        ):
            errors["incident_date"] = (
                "La fecha de la incidencia debe coincidir "
                "con la asistencia diaria."
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
            self.attendance_record_id
            and self.attendance_record.local_date
            != self.incident_date
        ):
            errors["incident_date"] = (
                "La fecha de la incidencia debe coincidir "
                "con la marcación."
            )

        if (
            self.justified_minutes
            > self.affected_minutes
        ):
            errors["justified_minutes"] = (
                "Los minutos justificados no pueden superar "
                "los minutos afectados."
            )

        if (
            self.deductible_minutes
            > self.affected_minutes
        ):
            errors["deductible_minutes"] = (
                "Los minutos descontables no pueden superar "
                "los minutos afectados."
            )

        if (
            self.requires_employee_explanation
            and self.status
            == self.Status.PENDING_EMPLOYEE
            and self.employee_explanation.strip()
        ):
            errors["status"] = (
                "La incidencia no debe permanecer pendiente "
                "del trabajador si ya presentó una explicación."
            )

        if (
            self.employee_explained_at
            and not self.employee_explanation.strip()
        ):
            errors["employee_explanation"] = (
                "Debes registrar la explicación del trabajador."
            )

        if (
            self.justification_requested
            and not self.justification_requested_at
        ):
            errors["justification_requested_at"] = (
                "Debes indicar cuándo se solicitó "
                "la justificación."
            )

        if (
            self.justification_due_at
            and not self.justification_requested
        ):
            errors["justification_requested"] = (
                "No puedes definir un plazo sin solicitar "
                "una justificación."
            )

        if (
            self.justification_due_at
            and self.justification_requested_at
            and self.justification_due_at
            <= self.justification_requested_at
        ):
            errors["justification_due_at"] = (
                "El plazo debe ser posterior a la fecha "
                "de solicitud."
            )

        if (
            self.justification_submitted_at
            and not self.justification_text.strip()
            and not self.justification_document
        ):
            errors["justification_text"] = (
                "Debes registrar una justificación o adjuntar "
                "un documento."
            )

        if (
            self.justification_reviewed_at
            and not self.justification_reviewed_by_id
        ):
            errors["justification_reviewed_by"] = (
                "Debes indicar quién revisó la justificación."
            )

        if (
            self.status
            == self.Status.JUSTIFIED
            and self.resolution_type
            != self.ResolutionType.JUSTIFICATION_ACCEPTED
        ):
            errors["resolution_type"] = (
                "Una incidencia justificada debe tener como "
                "resolución la aceptación de justificación."
            )

        if (
            self.status
            == self.Status.NOT_JUSTIFIED
            and self.resolution_type
            != self.ResolutionType.JUSTIFICATION_REJECTED
        ):
            errors["resolution_type"] = (
                "Una incidencia no justificada debe indicar "
                "que la justificación fue rechazada."
            )

        if (
            self.status
            == self.Status.CORRECTED
            and self.resolution_type
            not in (
                self.ResolutionType.RECORD_CORRECTED,
                self.ResolutionType.SCHEDULE_CORRECTED,
                self.ResolutionType.PERMISSION_REGISTERED,
                self.ResolutionType.VACATION_REGISTERED,
                self.ResolutionType.LEAVE_REGISTERED,
                self.ResolutionType.DEVICE_AUTHORIZED,
                self.ResolutionType.LOCATION_AUTHORIZED,
                self.ResolutionType.OTHER,
            )
        ):
            errors["resolution_type"] = (
                "Selecciona una resolución compatible "
                "con una incidencia corregida."
            )

        if (
            self.resolved_at
            and not self.resolved_by_id
        ):
            errors["resolved_by"] = (
                "Debes indicar quién resolvió la incidencia."
            )

        if (
            self.status == self.Status.CLOSED
            and not self.closed_at
        ):
            errors["closed_at"] = (
                "Una incidencia cerrada debe tener fecha "
                "de cierre."
            )

        if (
            self.status == self.Status.CANCELLED
            and not self.cancellation_reason.strip()
        ):
            errors["cancellation_reason"] = (
                "Debes indicar el motivo de anulación."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def request_employee_explanation(
        self,
        user=None,
        due_at=None,
    ):
        if not self.is_open:
            raise ValidationError(
                "Solo puedes solicitar explicación en una "
                "incidencia abierta."
            )

        self.requires_employee_explanation = True
        self.justification_requested = True
        self.justification_requested_at = timezone.now()
        self.justification_requested_by = user
        self.justification_due_at = due_at
        self.status = self.Status.PENDING_EMPLOYEE
        self.updated_by = user

        self.save(
            update_fields=[
                "requires_employee_explanation",
                "justification_requested",
                "justification_requested_at",
                "justification_requested_by",
                "justification_due_at",
                "status",
                "updated_by",
                "updated_at",
            ]
        )

    def submit_employee_explanation(
        self,
        explanation,
        accepts_incident=None,
        ip_address=None,
    ):
        explanation = str(
            explanation or ""
        ).strip()

        if not explanation:
            raise ValidationError(
                "Debes ingresar la explicación del trabajador."
            )

        if self.status not in (
            self.Status.OPEN,
            self.Status.PENDING_EMPLOYEE,
        ):
            raise ValidationError(
                "La incidencia no admite una nueva explicación."
            )

        self.employee_explanation = explanation
        self.employee_explained_at = timezone.now()
        self.employee_accepts_incident = accepts_incident
        self.employee_explanation_ip = ip_address
        self.justification_text = explanation
        self.justification_submitted_at = timezone.now()
        self.status = self.Status.PENDING_SUPERVISOR

        self.save(
            update_fields=[
                "employee_explanation",
                "employee_explained_at",
                "employee_accepts_incident",
                "employee_explanation_ip",
                "justification_text",
                "justification_submitted_at",
                "status",
                "updated_at",
            ]
        )

    def start_review(self, user=None):
        if self.status not in (
            self.Status.OPEN,
            self.Status.PENDING_SUPERVISOR,
            self.Status.PENDING_EMPLOYEE,
        ):
            raise ValidationError(
                "La incidencia no puede pasar a revisión."
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

    def accept_justification(
        self,
        user,
        notes="",
        justified_minutes=None,
        responsibility_type=None,
    ):
        if self.status in (
            self.Status.CLOSED,
            self.Status.CANCELLED,
        ):
            raise ValidationError(
                "No puedes resolver una incidencia cerrada "
                "o anulada."
            )

        if justified_minutes is None:
            justified_minutes = self.affected_minutes

        if justified_minutes > self.affected_minutes:
            raise ValidationError(
                "Los minutos justificados no pueden superar "
                "los minutos afectados."
            )

        self.justified_minutes = justified_minutes
        self.deductible_minutes = max(
            0,
            self.affected_minutes - justified_minutes,
        )

        self.status = self.Status.JUSTIFIED
        self.resolution_type = (
            self.ResolutionType.JUSTIFICATION_ACCEPTED
        )
        self.resolution_notes = str(
            notes or ""
        ).strip()

        if responsibility_type:
            self.responsibility_type = responsibility_type
        elif (
            self.responsibility_type
            == self.ResponsibilityType.UNDETERMINED
        ):
            self.responsibility_type = (
                self.ResponsibilityType.NOT_APPLICABLE
            )

        self.affects_payroll = False
        self.affects_evaluation = False
        self.evaluation_penalty_points = 0

        self.justification_reviewed_at = timezone.now()
        self.justification_reviewed_by = user
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.updated_by = user

        self.save(
            update_fields=[
                "justified_minutes",
                "deductible_minutes",
                "status",
                "resolution_type",
                "resolution_notes",
                "responsibility_type",
                "affects_payroll",
                "affects_evaluation",
                "evaluation_penalty_points",
                "justification_reviewed_at",
                "justification_reviewed_by",
                "resolved_at",
                "resolved_by",
                "updated_by",
                "updated_at",
            ]
        )

    def reject_justification(
        self,
        user,
        notes,
        deductible_minutes=None,
        penalty_points=0,
    ):
        notes = str(
            notes or ""
        ).strip()

        if not notes:
            raise ValidationError(
                "Debes indicar por qué se rechaza "
                "la justificación."
            )

        if self.status in (
            self.Status.CLOSED,
            self.Status.CANCELLED,
        ):
            raise ValidationError(
                "No puedes resolver una incidencia cerrada "
                "o anulada."
            )

        if deductible_minutes is None:
            deductible_minutes = (
                self.affected_minutes
            )

        if deductible_minutes > self.affected_minutes:
            raise ValidationError(
                "Los minutos descontables no pueden superar "
                "los minutos afectados."
            )

        self.status = self.Status.NOT_JUSTIFIED
        self.resolution_type = (
            self.ResolutionType.JUSTIFICATION_REJECTED
        )
        self.resolution_notes = notes
        self.justification_review_notes = notes

        self.justified_minutes = max(
            0,
            self.affected_minutes - deductible_minutes,
        )
        self.deductible_minutes = deductible_minutes

        self.responsibility_type = (
            self.ResponsibilityType.EMPLOYEE
        )

        self.evaluation_penalty_points = (
            penalty_points
        )

        self.justification_reviewed_at = timezone.now()
        self.justification_reviewed_by = user
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "resolution_type",
                "resolution_notes",
                "justification_review_notes",
                "justified_minutes",
                "deductible_minutes",
                "responsibility_type",
                "evaluation_penalty_points",
                "justification_reviewed_at",
                "justification_reviewed_by",
                "resolved_at",
                "resolved_by",
                "updated_by",
                "updated_at",
            ]
        )

    def mark_corrected(
        self,
        user,
        resolution_type,
        notes="",
    ):
        allowed_resolutions = (
            self.ResolutionType.RECORD_CORRECTED,
            self.ResolutionType.SCHEDULE_CORRECTED,
            self.ResolutionType.PERMISSION_REGISTERED,
            self.ResolutionType.VACATION_REGISTERED,
            self.ResolutionType.LEAVE_REGISTERED,
            self.ResolutionType.DEVICE_AUTHORIZED,
            self.ResolutionType.LOCATION_AUTHORIZED,
            self.ResolutionType.OTHER,
        )

        if resolution_type not in allowed_resolutions:
            raise ValidationError(
                "Tipo de resolución inválido para una "
                "incidencia corregida."
            )

        self.status = self.Status.CORRECTED
        self.resolution_type = resolution_type
        self.resolution_notes = str(
            notes or ""
        ).strip()
        self.justified_minutes = self.affected_minutes
        self.deductible_minutes = 0
        self.affects_payroll = False
        self.affects_evaluation = False
        self.evaluation_penalty_points = 0
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "resolution_type",
                "resolution_notes",
                "justified_minutes",
                "deductible_minutes",
                "affects_payroll",
                "affects_evaluation",
                "evaluation_penalty_points",
                "resolved_at",
                "resolved_by",
                "updated_by",
                "updated_at",
            ]
        )

    def dismiss(
        self,
        user,
        notes="",
    ):
        self.status = self.Status.DISMISSED
        self.resolution_type = (
            self.ResolutionType.NO_ACTION_REQUIRED
        )
        self.resolution_notes = str(
            notes or ""
        ).strip()
        self.justified_minutes = self.affected_minutes
        self.deductible_minutes = 0
        self.affects_payroll = False
        self.affects_evaluation = False
        self.evaluation_penalty_points = 0
        self.responsibility_type = (
            self.ResponsibilityType.NOT_APPLICABLE
        )
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "resolution_type",
                "resolution_notes",
                "justified_minutes",
                "deductible_minutes",
                "affects_payroll",
                "affects_evaluation",
                "evaluation_penalty_points",
                "responsibility_type",
                "resolved_at",
                "resolved_by",
                "updated_by",
                "updated_at",
            ]
        )

    def close(
        self,
        user,
        notes="",
    ):
        if self.status not in (
            self.Status.JUSTIFIED,
            self.Status.NOT_JUSTIFIED,
            self.Status.CORRECTED,
            self.Status.DISMISSED,
        ):
            raise ValidationError(
                "Solo puedes cerrar una incidencia resuelta."
            )

        self.status = self.Status.CLOSED
        self.closed_at = timezone.now()
        self.closed_by = user

        if notes:
            self.notes = str(
                notes
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

    def reopen(
        self,
        user,
        reason,
    ):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de reapertura."
            )

        if self.status != self.Status.CLOSED:
            raise ValidationError(
                "La incidencia no está cerrada."
            )

        self.status = self.Status.UNDER_REVIEW
        self.closed_at = None
        self.closed_by = None
        self.resolution_notes = (
            f"{self.resolution_notes}\n"
            f"Reabierta: {reason}"
        ).strip()
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "closed_at",
                "closed_by",
                "resolution_notes",
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
                "Debes indicar el motivo de anulación."
            )

        if self.status == self.Status.CLOSED:
            raise ValidationError(
                "No puedes anular una incidencia cerrada."
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

        if self.is_open:
            raise ValidationError(
                "No puedes archivar una incidencia abierta."
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