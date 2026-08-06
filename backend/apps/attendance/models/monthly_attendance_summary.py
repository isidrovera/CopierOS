# -*- coding: utf-8 -*-

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .employee_profile import EmployeeProfile


class MonthlyAttendanceSummary(models.Model):
    """
    Consolidado mensual de asistencia y tiempo operativo.

    Resume por trabajador:

    - Días laborables.
    - Días asistidos.
    - Ausencias.
    - Tardanzas.
    - Salidas anticipadas.
    - Permisos.
    - Vacaciones.
    - Descansos médicos.
    - Horas programadas.
    - Horas trabajadas.
    - Horas extras.
    - Tiempo operativo.
    - Tiempo administrativo.
    - Tiempo sin clasificar.
    - Esperas internas y externas.
    - Demoras atribuibles al trabajador.
    - Incidencias justificadas y no justificadas.
    - Indicadores para evaluación de personal.

    Este modelo guarda una fotografía del cierre mensual.
    Los cálculos deberán realizarse desde un servicio específico.
    """

    class Status(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        PROCESSING = (
            "processing",
            "Procesando",
        )
        PROCESSED = (
            "processed",
            "Procesado",
        )
        REVIEW_REQUIRED = (
            "review_required",
            "Requiere revisión",
        )
        APPROVED = (
            "approved",
            "Aprobado",
        )
        CLOSED = (
            "closed",
            "Cerrado",
        )
        ERROR = (
            "error",
            "Error",
        )
        REOPENED = (
            "reopened",
            "Reabierto",
        )

    class EvaluationStatus(models.TextChoices):
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )
        PENDING = (
            "pending",
            "Pendiente",
        )
        READY = (
            "ready",
            "Listo para evaluación",
        )
        EXPORTED = (
            "exported",
            "Exportado a evaluación",
        )
        EVALUATED = (
            "evaluated",
            "Evaluado",
        )
        EXCLUDED = (
            "excluded",
            "Excluido",
        )

    class AttendanceRating(models.TextChoices):
        EXCELLENT = (
            "excellent",
            "Excelente",
        )
        GOOD = (
            "good",
            "Bueno",
        )
        REGULAR = (
            "regular",
            "Regular",
        )
        DEFICIENT = (
            "deficient",
            "Deficiente",
        )
        CRITICAL = (
            "critical",
            "Crítico",
        )
        NOT_CALCULATED = (
            "not_calculated",
            "No calculado",
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
        related_name="monthly_attendance_summaries",
        verbose_name="Perfil laboral",
    )

    year = models.PositiveSmallIntegerField(
        db_index=True,
        verbose_name="Año",
    )

    month = models.PositiveSmallIntegerField(
        db_index=True,
        verbose_name="Mes",
    )

    period_start = models.DateField(
        db_index=True,
        verbose_name="Inicio del periodo",
    )

    period_end = models.DateField(
        db_index=True,
        verbose_name="Fin del periodo",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    evaluation_status = models.CharField(
        max_length=30,
        choices=EvaluationStatus.choices,
        default=EvaluationStatus.PENDING,
        db_index=True,
        verbose_name="Estado para evaluación",
    )

    attendance_rating = models.CharField(
        max_length=30,
        choices=AttendanceRating.choices,
        default=AttendanceRating.NOT_CALCULATED,
        db_index=True,
        verbose_name="Calificación de asistencia",
    )

    scheduled_calendar_days = models.PositiveIntegerField(
        default=0,
        verbose_name="Días calendario del periodo",
    )

    scheduled_working_days = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Días laborables programados",
    )

    attendance_required_days = models.PositiveIntegerField(
        default=0,
        verbose_name="Días con asistencia requerida",
    )

    present_days = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        db_index=True,
        verbose_name="Días asistidos",
    )

    present_with_incidents_days = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Días asistidos con incidencias",
    )

    absent_days = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        db_index=True,
        verbose_name="Días de ausencia",
    )

    justified_absence_days = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Días de ausencia justificada",
    )

    unjustified_absence_days = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        db_index=True,
        verbose_name="Días de ausencia injustificada",
    )

    vacation_days = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Días de vacaciones",
    )

    medical_leave_days = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Días de descanso médico",
    )

    paid_leave_days = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Días de licencia con goce",
    )

    unpaid_leave_days = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Días de licencia sin goce",
    )

    service_commission_days = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Días de comisión de servicio",
    )

    remote_work_days = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Días de trabajo remoto",
    )

    holiday_days = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Días feriados",
    )

    non_working_days = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Días no laborables",
    )

    rest_days = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Días de descanso",
    )

    late_days = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Días con tardanza",
    )

    early_departure_days = models.PositiveIntegerField(
        default=0,
        verbose_name="Días con salida anticipada",
    )

    incomplete_clocking_days = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Días con marcaciones incompletas",
    )

    location_incident_days = models.PositiveIntegerField(
        default=0,
        verbose_name="Días con incidencias de ubicación",
    )

    device_incident_days = models.PositiveIntegerField(
        default=0,
        verbose_name="Días con incidencias de dispositivo",
    )

    scheduled_work_minutes = models.PositiveBigIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos programados",
    )

    gross_presence_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos totales de presencia",
    )

    effective_work_minutes = models.PositiveBigIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos efectivos trabajados",
    )

    scheduled_break_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos de refrigerio programados",
    )

    valid_break_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos válidos de refrigerio",
    )

    excess_break_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos de exceso de refrigerio",
    )

    late_minutes = models.PositiveBigIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos de tardanza",
    )

    early_departure_minutes = models.PositiveBigIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos de salida anticipada",
    )

    missing_work_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos faltantes de jornada",
    )

    overtime_minutes = models.PositiveBigIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos de horas extras",
    )

    approved_overtime_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos extra aprobados",
    )

    unapproved_overtime_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos extra no aprobados",
    )

    compensation_required_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos por compensar",
    )

    compensation_completed_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos compensados",
    )

    compensation_pending_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos pendientes de compensación",
    )

    operational_work_minutes = models.PositiveBigIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos de trabajo operativo",
    )

    administrative_work_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos de trabajo administrativo",
    )

    unclassified_work_minutes = models.PositiveBigIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos de trabajo sin clasificar",
    )

    travel_minutes = models.PositiveBigIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos de traslado",
    )

    diagnosis_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos de diagnóstico",
    )

    execution_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos de ejecución",
    )

    testing_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos de pruebas",
    )

    documentation_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos de documentación",
    )

    pause_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Minutos de pausa",
    )

    internal_waiting_minutes = models.PositiveBigIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos de espera interna",
    )

    external_waiting_minutes = models.PositiveBigIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos de espera externa",
    )

    technician_delay_minutes = models.PositiveBigIntegerField(
        default=0,
        db_index=True,
        verbose_name="Demora atribuible al trabajador",
    )

    company_delay_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Demora atribuible a la empresa",
    )

    client_delay_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Demora atribuible al cliente",
    )

    supplier_delay_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Demora atribuible al proveedor",
    )

    external_delay_minutes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Demora por causas externas",
    )

    operational_sessions_count = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Cantidad de sesiones operativas",
    )

    completed_operational_sessions = models.PositiveIntegerField(
        default=0,
        verbose_name="Sesiones operativas finalizadas",
    )

    cancelled_operational_sessions = models.PositiveIntegerField(
        default=0,
        verbose_name="Sesiones operativas canceladas",
    )

    rejected_operational_sessions = models.PositiveIntegerField(
        default=0,
        verbose_name="Sesiones operativas rechazadas",
    )

    pending_operational_sessions = models.PositiveIntegerField(
        default=0,
        verbose_name="Sesiones operativas pendientes",
    )

    successful_operational_sessions = models.PositiveIntegerField(
        default=0,
        verbose_name="Sesiones finalizadas correctamente",
    )

    partial_operational_sessions = models.PositiveIntegerField(
        default=0,
        verbose_name="Sesiones finalizadas parcialmente",
    )

    repair_sessions_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Sesiones de reparación",
    )

    technical_service_sessions_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Sesiones de servicio técnico",
    )

    installation_sessions_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Sesiones de instalación",
    )

    preparation_sessions_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Sesiones de preparación",
    )

    incident_count = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Cantidad total de incidencias",
    )

    open_incident_count = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Incidencias abiertas",
    )

    justified_incident_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Incidencias justificadas",
    )

    unjustified_incident_count = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Incidencias no justificadas",
    )

    corrected_incident_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Incidencias corregidas",
    )

    dismissed_incident_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Incidencias descartadas",
    )

    employee_responsibility_incident_count = (
        models.PositiveIntegerField(
            default=0,
            verbose_name=(
                "Incidencias atribuibles al trabajador"
            ),
        )
    )

    external_responsibility_incident_count = (
        models.PositiveIntegerField(
            default=0,
            verbose_name=(
                "Incidencias por responsabilidad externa"
            ),
        )
    )

    attendance_correction_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Correcciones de asistencia",
    )

    manual_clocking_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Marcaciones manuales",
    )

    observed_clocking_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Marcaciones observadas",
    )

    rejected_clocking_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Marcaciones rechazadas",
    )

    attendance_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        db_index=True,
        verbose_name="Porcentaje de asistencia",
    )

    punctuality_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        db_index=True,
        verbose_name="Porcentaje de puntualidad",
    )

    schedule_compliance_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Cumplimiento de jornada",
    )

    operational_time_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        db_index=True,
        verbose_name="Porcentaje de tiempo operativo",
    )

    classified_time_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Porcentaje de tiempo clasificado",
    )

    operational_completion_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        db_index=True,
        verbose_name="Porcentaje de sesiones completadas",
    )

    operational_success_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Porcentaje de sesiones exitosas",
    )

    technician_delay_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        db_index=True,
        verbose_name="Porcentaje de demora atribuible",
    )

    attendance_score = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        db_index=True,
        verbose_name="Puntaje de asistencia",
    )

    punctuality_score = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Puntaje de puntualidad",
    )

    schedule_compliance_score = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Puntaje de cumplimiento de jornada",
    )

    productivity_time_score = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Puntaje de tiempo productivo",
    )

    incident_score = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="Puntaje de incidencias",
    )

    total_attendance_evaluation_score = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        db_index=True,
        verbose_name="Puntaje total para evaluación",
    )

    incident_penalty_points = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=0,
        verbose_name="Penalización por incidencias",
    )

    manual_adjustment_points = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=0,
        verbose_name="Ajuste manual de puntaje",
    )

    final_evaluation_points = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=0,
        db_index=True,
        verbose_name="Puntaje final de asistencia",
    )

    included_in_evaluation = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Incluido en evaluación",
    )

    exclusion_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de exclusión",
    )

    requires_review = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere revisión",
    )

    review_reasons = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Motivos de revisión",
    )

    calculation_details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Detalle del cálculo",
    )

    calculation_version = models.PositiveIntegerField(
        default=1,
        verbose_name="Versión de cálculo",
    )

    processing_started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Procesamiento iniciado el",
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Procesado el",
    )

    processing_error = models.TextField(
        blank=True,
        verbose_name="Error de procesamiento",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Revisado el",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monthly_attendance_summaries_reviewed",
        verbose_name="Revisado por",
    )

    review_observation = models.TextField(
        blank=True,
        verbose_name="Observación de revisión",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Aprobado el",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monthly_attendance_summaries_approved",
        verbose_name="Aprobado por",
    )

    approval_observation = models.TextField(
        blank=True,
        verbose_name="Observación de aprobación",
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Cerrado el",
    )

    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monthly_attendance_summaries_closed",
        verbose_name="Cerrado por",
    )

    reopened_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Reabierto el",
    )

    reopened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monthly_attendance_summaries_reopened",
        verbose_name="Reabierto por",
    )

    reopen_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de reapertura",
    )

    exported_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Exportado a evaluación el",
    )

    exported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monthly_attendance_summaries_exported",
        verbose_name="Exportado por",
    )

    evaluation_reference = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Referencia de evaluación",
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
        related_name="monthly_attendance_summaries_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monthly_attendance_summaries_updated",
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
        related_name="monthly_attendance_summaries_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Resumen mensual de asistencia"
        verbose_name_plural = "Resúmenes mensuales de asistencia"

        ordering = (
            "-year",
            "-month",
            "employee_profile",
        )

        constraints = (
            models.UniqueConstraint(
                fields=(
                    "employee_profile",
                    "year",
                    "month",
                ),
                condition=models.Q(
                    archived_at__isnull=True,
                ),
                name="att_month_emp_period_unique",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        month__gte=1,
                    )
                    & models.Q(
                        month__lte=12,
                    )
                ),
                name="att_month_month_range",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    approved_overtime_minutes__lte=models.F(
                        "overtime_minutes"
                    ),
                ),
                name="att_month_approved_ot_lte",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    compensation_completed_minutes__lte=models.F(
                        "compensation_required_minutes"
                    ),
                ),
                name="att_month_comp_done_lte",
            ),
        )

        indexes = (
            models.Index(
                fields=(
                    "employee_profile",
                    "year",
                    "month",
                    "status",
                ),
                name="att_month_emp_period_idx",
            ),
            models.Index(
                fields=(
                    "year",
                    "month",
                    "status",
                ),
                name="att_month_period_status_idx",
            ),
            models.Index(
                fields=(
                    "evaluation_status",
                    "included_in_evaluation",
                ),
                name="att_month_eval_include_idx",
            ),
            models.Index(
                fields=(
                    "attendance_percentage",
                    "punctuality_percentage",
                ),
                name="att_month_att_punct_idx",
            ),
            models.Index(
                fields=(
                    "operational_time_percentage",
                    "operational_completion_percentage",
                ),
                name="att_month_oper_comp_idx",
            ),
            models.Index(
                fields=(
                    "late_days",
                    "unjustified_absence_days",
                ),
                name="att_month_late_abs_idx",
            ),
            models.Index(
                fields=(
                    "incident_count",
                    "unjustified_incident_count",
                ),
                name="att_month_incidents_idx",
            ),
            models.Index(
                fields=(
                    "technician_delay_minutes",
                    "external_waiting_minutes",
                ),
                name="att_month_delay_wait_idx",
            ),
            models.Index(
                fields=(
                    "requires_review",
                    "status",
                ),
                name="att_month_review_status_idx",
            ),
            models.Index(
                fields=(
                    "final_evaluation_points",
                    "included_in_evaluation",
                ),
                name="att_month_final_eval_idx",
            ),
        )

    def __str__(self):
        return (
            f"{self.employee_profile.user.full_name} - "
            f"{self.month:02d}/{self.year}"
        )

    @property
    def employee(self):
        return self.employee_profile.user

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_closed(self):
        return self.status == self.Status.CLOSED

    @property
    def period_label(self):
        return f"{self.month:02d}/{self.year}"

    @property
    def scheduled_work_hours(self):
        return round(
            self.scheduled_work_minutes / 60,
            2,
        )

    @property
    def effective_work_hours(self):
        return round(
            self.effective_work_minutes / 60,
            2,
        )

    @property
    def operational_work_hours(self):
        return round(
            self.operational_work_minutes / 60,
            2,
        )

    @property
    def overtime_hours(self):
        return round(
            self.overtime_minutes / 60,
            2,
        )

    @property
    def attendance_deficit_minutes(self):
        return max(
            0,
            self.scheduled_work_minutes
            - self.effective_work_minutes,
        )

    @property
    def non_technician_delay_minutes(self):
        return (
            self.company_delay_minutes
            + self.client_delay_minutes
            + self.supplier_delay_minutes
            + self.external_delay_minutes
        )

    @property
    def total_delay_minutes(self):
        return (
            self.technician_delay_minutes
            + self.non_technician_delay_minutes
        )

    @property
    def evaluated_operational_minutes(self):
        return max(
            0,
            self.operational_work_minutes
            - self.technician_delay_minutes,
        )

    @property
    def has_pending_incidents(self):
        return self.open_incident_count > 0

    @property
    def can_be_closed(self):
        return (
            self.status
            in (
                self.Status.PROCESSED,
                self.Status.APPROVED,
            )
            and not self.requires_review
            and not self.has_pending_incidents
        )

    def calculate_basic_percentages(self):
        if self.attendance_required_days > 0:
            attended_days = (
                self.present_days
                + self.present_with_incidents_days
                + self.justified_absence_days
                + self.vacation_days
                + self.medical_leave_days
                + self.paid_leave_days
                + self.service_commission_days
                + self.remote_work_days
            )

            attendance_percentage = (
                attended_days
                / Decimal(
                    self.attendance_required_days
                )
            ) * Decimal("100")

            self.attendance_percentage = min(
                Decimal("100"),
                max(
                    Decimal("0"),
                    attendance_percentage,
                ),
            )

            punctual_days = max(
                Decimal("0"),
                self.present_days
                + self.present_with_incidents_days
                - Decimal(self.late_days),
            )

            total_present_days = (
                self.present_days
                + self.present_with_incidents_days
            )

            if total_present_days > 0:
                punctuality_percentage = (
                    punctual_days
                    / total_present_days
                ) * Decimal("100")
            else:
                punctuality_percentage = Decimal("0")

            self.punctuality_percentage = min(
                Decimal("100"),
                max(
                    Decimal("0"),
                    punctuality_percentage,
                ),
            )

        else:
            self.attendance_percentage = Decimal("100")
            self.punctuality_percentage = Decimal("100")

        if self.scheduled_work_minutes > 0:
            schedule_percentage = (
                Decimal(self.effective_work_minutes)
                / Decimal(self.scheduled_work_minutes)
            ) * Decimal("100")

            self.schedule_compliance_percentage = min(
                Decimal("100"),
                max(
                    Decimal("0"),
                    schedule_percentage,
                ),
            )
        else:
            self.schedule_compliance_percentage = Decimal("100")

        if self.effective_work_minutes > 0:
            operational_percentage = (
                Decimal(self.operational_work_minutes)
                / Decimal(self.effective_work_minutes)
            ) * Decimal("100")

            classified_minutes = (
                self.operational_work_minutes
                + self.administrative_work_minutes
            )

            classified_percentage = (
                Decimal(classified_minutes)
                / Decimal(self.effective_work_minutes)
            ) * Decimal("100")

            self.operational_time_percentage = min(
                Decimal("100"),
                max(
                    Decimal("0"),
                    operational_percentage,
                ),
            )

            self.classified_time_percentage = min(
                Decimal("100"),
                max(
                    Decimal("0"),
                    classified_percentage,
                ),
            )

        else:
            self.operational_time_percentage = Decimal("0")
            self.classified_time_percentage = Decimal("0")

        if self.operational_sessions_count > 0:
            completion_percentage = (
                Decimal(
                    self.completed_operational_sessions
                )
                / Decimal(
                    self.operational_sessions_count
                )
            ) * Decimal("100")

            self.operational_completion_percentage = min(
                Decimal("100"),
                max(
                    Decimal("0"),
                    completion_percentage,
                ),
            )

        else:
            self.operational_completion_percentage = Decimal("0")

        if self.completed_operational_sessions > 0:
            success_percentage = (
                Decimal(
                    self.successful_operational_sessions
                )
                / Decimal(
                    self.completed_operational_sessions
                )
            ) * Decimal("100")

            self.operational_success_percentage = min(
                Decimal("100"),
                max(
                    Decimal("0"),
                    success_percentage,
                ),
            )

        else:
            self.operational_success_percentage = Decimal("0")

        if self.operational_work_minutes > 0:
            delay_percentage = (
                Decimal(self.technician_delay_minutes)
                / Decimal(self.operational_work_minutes)
            ) * Decimal("100")

            self.technician_delay_percentage = min(
                Decimal("100"),
                max(
                    Decimal("0"),
                    delay_percentage,
                ),
            )

        else:
            self.technician_delay_percentage = Decimal("0")

        self.unapproved_overtime_minutes = max(
            0,
            self.overtime_minutes
            - self.approved_overtime_minutes,
        )

        self.compensation_pending_minutes = max(
            0,
            self.compensation_required_minutes
            - self.compensation_completed_minutes,
        )

    def calculate_rating(self):
        score = self.final_evaluation_points

        if score >= Decimal("90"):
            self.attendance_rating = (
                self.AttendanceRating.EXCELLENT
            )

        elif score >= Decimal("75"):
            self.attendance_rating = (
                self.AttendanceRating.GOOD
            )

        elif score >= Decimal("60"):
            self.attendance_rating = (
                self.AttendanceRating.REGULAR
            )

        elif score >= Decimal("40"):
            self.attendance_rating = (
                self.AttendanceRating.DEFICIENT
            )

        else:
            self.attendance_rating = (
                self.AttendanceRating.CRITICAL
            )

        return self.attendance_rating

    def calculate_final_points(self):
        base_score = (
            self.attendance_score
            + self.punctuality_score
            + self.schedule_compliance_score
            + self.productivity_time_score
            + self.incident_score
        )

        self.total_attendance_evaluation_score = max(
            Decimal("0"),
            base_score,
        )

        final_points = (
            self.total_attendance_evaluation_score
            - self.incident_penalty_points
            + self.manual_adjustment_points
        )

        self.final_evaluation_points = max(
            Decimal("0"),
            final_points,
        )

        self.calculate_rating()

        return self.final_evaluation_points

    def update_review_reasons(self):
        reasons = []

        if self.open_incident_count > 0:
            reasons.append(
                "Existen incidencias abiertas."
            )

        if self.incomplete_clocking_days > 0:
            reasons.append(
                "Existen días con marcaciones incompletas."
            )

        if self.unclassified_work_minutes > 0:
            reasons.append(
                "Existe tiempo trabajado sin clasificar."
            )

        if self.compensation_pending_minutes > 0:
            reasons.append(
                "Existe tiempo pendiente de compensación."
            )

        if self.observed_clocking_count > 0:
            reasons.append(
                "Existen marcaciones observadas."
            )

        if self.rejected_clocking_count > 0:
            reasons.append(
                "Existen marcaciones rechazadas."
            )

        if self.processing_error.strip():
            reasons.append(
                "Existe un error de procesamiento."
            )

        self.review_reasons = reasons
        self.requires_review = bool(reasons)

        return reasons

    def prepare_for_evaluation(self):
        if not self.included_in_evaluation:
            self.evaluation_status = (
                self.EvaluationStatus.EXCLUDED
            )

            return self.evaluation_status

        if self.requires_review:
            self.evaluation_status = (
                self.EvaluationStatus.PENDING
            )

            return self.evaluation_status

        if self.status not in (
            self.Status.PROCESSED,
            self.Status.APPROVED,
            self.Status.CLOSED,
        ):
            self.evaluation_status = (
                self.EvaluationStatus.PENDING
            )

            return self.evaluation_status

        self.evaluation_status = (
            self.EvaluationStatus.READY
        )

        return self.evaluation_status

    def recalculate_indicators(self):
        if self.is_closed:
            raise ValidationError(
                "No puedes recalcular un resumen cerrado."
            )

        self.status = self.Status.PROCESSING
        self.processing_started_at = timezone.now()
        self.processing_error = ""

        try:
            self.calculate_basic_percentages()
            self.calculate_final_points()
            self.update_review_reasons()
            self.prepare_for_evaluation()

            if self.requires_review:
                self.status = self.Status.REVIEW_REQUIRED
            else:
                self.status = self.Status.PROCESSED

            self.processed_at = timezone.now()
            self.calculation_version += 1

        except Exception as exception:
            self.status = self.Status.ERROR
            self.processing_error = str(exception)
            self.processed_at = timezone.now()

            raise

        finally:
            self.save()

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

        if self.month < 1 or self.month > 12:
            errors["month"] = (
                "El mes debe estar entre 1 y 12."
            )

        if self.period_end < self.period_start:
            errors["period_end"] = (
                "La fecha final no puede ser anterior "
                "a la fecha inicial."
            )

        if (
            self.period_start.year != self.year
            or self.period_start.month != self.month
        ):
            errors["period_start"] = (
                "El inicio del periodo debe corresponder "
                "al año y mes seleccionados."
            )

        if (
            self.period_end.year != self.year
            or self.period_end.month != self.month
        ):
            errors["period_end"] = (
                "El fin del periodo debe corresponder "
                "al año y mes seleccionados."
            )

        if (
            self.approved_overtime_minutes
            > self.overtime_minutes
        ):
            errors["approved_overtime_minutes"] = (
                "Las horas extras aprobadas no pueden superar "
                "las horas extras calculadas."
            )

        if (
            self.compensation_completed_minutes
            > self.compensation_required_minutes
        ):
            errors["compensation_completed_minutes"] = (
                "Los minutos compensados no pueden superar "
                "los minutos requeridos."
            )

        if (
            self.completed_operational_sessions
            > self.operational_sessions_count
        ):
            errors["completed_operational_sessions"] = (
                "Las sesiones finalizadas no pueden superar "
                "el total de sesiones."
            )

        if (
            self.successful_operational_sessions
            > self.completed_operational_sessions
        ):
            errors["successful_operational_sessions"] = (
                "Las sesiones exitosas no pueden superar "
                "las sesiones finalizadas."
            )

        if (
            self.justified_incident_count
            + self.unjustified_incident_count
            + self.corrected_incident_count
            + self.dismissed_incident_count
            > self.incident_count
        ):
            errors["incident_count"] = (
                "La clasificación de incidencias supera "
                "el total registrado."
            )

        percentage_fields = (
            "attendance_percentage",
            "punctuality_percentage",
            "schedule_compliance_percentage",
            "operational_time_percentage",
            "classified_time_percentage",
            "operational_completion_percentage",
            "operational_success_percentage",
            "technician_delay_percentage",
        )

        for field_name in percentage_fields:
            value = getattr(
                self,
                field_name,
            )

            if value < 0 or value > 100:
                errors[field_name] = (
                    "El porcentaje debe estar entre 0 y 100."
                )

        if (
            self.status == self.Status.ERROR
            and not self.processing_error.strip()
        ):
            errors["processing_error"] = (
                "Un resumen con error debe registrar "
                "el detalle del problema."
            )

        if (
            self.status == self.Status.APPROVED
            and not self.approved_at
        ):
            errors["approved_at"] = (
                "Un resumen aprobado debe tener "
                "fecha de aprobación."
            )

        if (
            self.status == self.Status.CLOSED
            and not self.closed_at
        ):
            errors["closed_at"] = (
                "Un resumen cerrado debe tener fecha de cierre."
            )

        if (
            self.status == self.Status.REOPENED
            and not self.reopen_reason.strip()
        ):
            errors["reopen_reason"] = (
                "Debes indicar el motivo de reapertura."
            )

        if (
            not self.included_in_evaluation
            and not self.exclusion_reason.strip()
        ):
            errors["exclusion_reason"] = (
                "Debes indicar por qué se excluye "
                "de la evaluación."
            )

        if (
            self.evaluation_status
            == self.EvaluationStatus.EXPORTED
            and not self.exported_at
        ):
            errors["exported_at"] = (
                "Un resumen exportado debe tener fecha "
                "de exportación."
            )

        if (
            self.requires_review
            and not self.review_reasons
        ):
            errors["review_reasons"] = (
                "Debes registrar los motivos de revisión."
            )

        if (
            self.reviewed_at
            and not self.reviewed_by_id
        ):
            errors["reviewed_by"] = (
                "Debes indicar quién revisó el resumen."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def mark_reviewed(
        self,
        user,
        observation="",
    ):
        if self.status not in (
            self.Status.REVIEW_REQUIRED,
            self.Status.PROCESSED,
            self.Status.REOPENED,
        ):
            raise ValidationError(
                "El resumen no está disponible para revisión."
            )

        self.reviewed_at = timezone.now()
        self.reviewed_by = user
        self.review_observation = str(
            observation or ""
        ).strip()
        self.updated_by = user

        self.save(
            update_fields=[
                "reviewed_at",
                "reviewed_by",
                "review_observation",
                "updated_by",
                "updated_at",
            ]
        )

    def approve(
        self,
        user,
        observation="",
    ):
        if self.status not in (
            self.Status.PROCESSED,
            self.Status.REVIEW_REQUIRED,
            self.Status.REOPENED,
        ):
            raise ValidationError(
                "Solo puedes aprobar un resumen procesado "
                "o revisado."
            )

        if self.requires_review and not self.reviewed_at:
            raise ValidationError(
                "Debes revisar el resumen antes de aprobarlo."
            )

        if self.open_incident_count > 0:
            raise ValidationError(
                "No puedes aprobar el resumen mientras existan "
                "incidencias abiertas."
            )

        self.status = self.Status.APPROVED
        self.approved_at = timezone.now()
        self.approved_by = user
        self.approval_observation = str(
            observation or ""
        ).strip()
        self.requires_review = False
        self.review_reasons = []
        self.updated_by = user

        self.prepare_for_evaluation()

        self.save(
            update_fields=[
                "status",
                "approved_at",
                "approved_by",
                "approval_observation",
                "requires_review",
                "review_reasons",
                "evaluation_status",
                "updated_by",
                "updated_at",
            ]
        )

    def close(
        self,
        user,
        observation="",
    ):
        if self.status != self.Status.APPROVED:
            raise ValidationError(
                "Solo puedes cerrar un resumen aprobado."
            )

        if self.open_incident_count > 0:
            raise ValidationError(
                "No puedes cerrar el resumen mientras existan "
                "incidencias abiertas."
            )

        if self.compensation_pending_minutes > 0:
            raise ValidationError(
                "No puedes cerrar el resumen mientras exista "
                "compensación pendiente."
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
                "Solo puedes reabrir un resumen cerrado."
            )

        self.status = self.Status.REOPENED
        self.reopened_at = timezone.now()
        self.reopened_by = user
        self.reopen_reason = reason
        self.closed_at = None
        self.closed_by = None
        self.requires_review = True

        review_reasons = list(
            self.review_reasons or []
        )

        review_reasons.append(
            f"Resumen reabierto: {reason}"
        )

        self.review_reasons = review_reasons
        self.evaluation_status = (
            self.EvaluationStatus.PENDING
        )
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "reopened_at",
                "reopened_by",
                "reopen_reason",
                "closed_at",
                "closed_by",
                "requires_review",
                "review_reasons",
                "evaluation_status",
                "updated_by",
                "updated_at",
            ]
        )

    def mark_exported(
        self,
        user=None,
        reference="",
    ):
        if self.status not in (
            self.Status.APPROVED,
            self.Status.CLOSED,
        ):
            raise ValidationError(
                "Solo puedes exportar un resumen aprobado "
                "o cerrado."
            )

        if not self.included_in_evaluation:
            raise ValidationError(
                "El trabajador está excluido de la evaluación."
            )

        self.evaluation_status = (
            self.EvaluationStatus.EXPORTED
        )
        self.exported_at = timezone.now()
        self.exported_by = user
        self.evaluation_reference = str(
            reference or ""
        ).strip()
        self.updated_by = user

        self.save(
            update_fields=[
                "evaluation_status",
                "exported_at",
                "exported_by",
                "evaluation_reference",
                "updated_by",
                "updated_at",
            ]
        )

    def mark_evaluated(
        self,
        user=None,
        reference="",
    ):
        if self.evaluation_status not in (
            self.EvaluationStatus.READY,
            self.EvaluationStatus.EXPORTED,
        ):
            raise ValidationError(
                "El resumen no está listo para marcarse "
                "como evaluado."
            )

        self.evaluation_status = (
            self.EvaluationStatus.EVALUATED
        )

        if reference:
            self.evaluation_reference = str(
                reference
            ).strip()

        self.updated_by = user

        self.save(
            update_fields=[
                "evaluation_status",
                "evaluation_reference",
                "updated_by",
                "updated_at",
            ]
        )

    def exclude_from_evaluation(
        self,
        user,
        reason,
    ):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de exclusión."
            )

        if self.evaluation_status == (
            self.EvaluationStatus.EVALUATED
        ):
            raise ValidationError(
                "No puedes excluir un resumen ya evaluado."
            )

        self.included_in_evaluation = False
        self.exclusion_reason = reason
        self.evaluation_status = (
            self.EvaluationStatus.EXCLUDED
        )
        self.updated_by = user

        self.save(
            update_fields=[
                "included_in_evaluation",
                "exclusion_reason",
                "evaluation_status",
                "updated_by",
                "updated_at",
            ]
        )

    def include_in_staff_evaluation(
        self,
        user=None,
    ):
        if not self.employee_profile.include_in_staff_evaluation:
            raise ValidationError(
                "El perfil laboral está excluido de las "
                "evaluaciones de personal."
            )

        self.included_in_evaluation = True
        self.exclusion_reason = ""
        self.updated_by = user

        self.prepare_for_evaluation()

        self.save(
            update_fields=[
                "included_in_evaluation",
                "exclusion_reason",
                "evaluation_status",
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
            self.Status.PROCESSING,
            self.Status.APPROVED,
            self.Status.CLOSED,
        ):
            raise ValidationError(
                "No puedes archivar un resumen procesándose, "
                "aprobado o cerrado."
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