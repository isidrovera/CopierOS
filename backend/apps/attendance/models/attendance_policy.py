# -*- coding: utf-8 -*-

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .work_location import WorkLocation
from .work_schedule import WorkSchedule


class AttendancePolicy(models.Model):
    """
    Política configurable para asistencia y productividad.

    Define reglas generales o específicas para:

    - Empresa.
    - Área.
    - Cargo.
    - Horario.
    - Ubicación.
    - Trabajador.

    La política no registra marcaciones. Determina cómo deben
    validarse, procesarse y evaluarse.
    """

    class PolicyScope(models.TextChoices):
        GLOBAL = (
            "global",
            "Política global",
        )
        COMPANY = (
            "company",
            "Por empresa",
        )
        DEPARTMENT = (
            "department",
            "Por área",
        )
        JOB_TITLE = (
            "job_title",
            "Por cargo",
        )
        SCHEDULE = (
            "schedule",
            "Por horario",
        )
        LOCATION = (
            "location",
            "Por ubicación",
        )
        EMPLOYEE = (
            "employee",
            "Por trabajador",
        )
        SPECIAL = (
            "special",
            "Especial",
        )

    class RoundingMode(models.TextChoices):
        NONE = (
            "none",
            "Sin redondeo",
        )
        DOWN = (
            "down",
            "Redondear hacia abajo",
        )
        UP = (
            "up",
            "Redondear hacia arriba",
        )
        NEAREST = (
            "nearest",
            "Redondear al intervalo más cercano",
        )

    class MissingClockingAction(models.TextChoices):
        REVIEW = (
            "review",
            "Enviar a revisión",
        )
        MARK_ABSENCE = (
            "mark_absence",
            "Marcar ausencia",
        )
        USE_SCHEDULE = (
            "use_schedule",
            "Usar horario programado",
        )
        USE_FIRST_LAST_RECORD = (
            "use_first_last_record",
            "Usar primera y última marcación",
        )
        REQUIRE_CORRECTION = (
            "require_correction",
            "Exigir corrección",
        )
        IGNORE = (
            "ignore",
            "Ignorar",
        )

    class OvertimeMode(models.TextChoices):
        DISABLED = (
            "disabled",
            "No registrar horas extras",
        )
        AUTOMATIC = (
            "automatic",
            "Registrar automáticamente",
        )
        REQUIRE_APPROVAL = (
            "require_approval",
            "Requiere aprobación",
        )
        SCHEDULED_ONLY = (
            "scheduled_only",
            "Solo horas extras programadas",
        )

    class EvaluationMode(models.TextChoices):
        DISABLED = (
            "disabled",
            "No evaluar asistencia",
        )
        INFORMATIONAL = (
            "informational",
            "Solo informativa",
        )
        SCORE = (
            "score",
            "Generar puntaje",
        )
        PENALTY = (
            "penalty",
            "Aplicar penalizaciones",
        )
        SCORE_AND_PENALTY = (
            "score_and_penalty",
            "Puntaje y penalizaciones",
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

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código",
    )

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="Nombre",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    scope = models.CharField(
        max_length=20,
        choices=PolicyScope.choices,
        default=PolicyScope.GLOBAL,
        db_index=True,
        verbose_name="Alcance",
    )

    priority = models.PositiveSmallIntegerField(
        default=100,
        db_index=True,
        verbose_name="Prioridad",
        help_text=(
            "Un valor menor tiene mayor prioridad cuando "
            "varias políticas son aplicables."
        ),
    )

    company_name = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
        verbose_name="Empresa",
    )

    department_name = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Área o departamento",
    )

    job_title = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Cargo",
    )

    schedule = models.ForeignKey(
        WorkSchedule,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_policies",
        verbose_name="Horario",
    )

    work_location = models.ForeignKey(
        WorkLocation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_policies",
        verbose_name="Ubicación",
    )

    employee_profile = models.ForeignKey(
        "attendance.EmployeeProfile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_policies",
        verbose_name="Perfil laboral",
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

    is_default = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Política predeterminada",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activa",
    )

    attendance_enabled = models.BooleanField(
        default=True,
        verbose_name="Control de asistencia habilitado",
    )

    require_clock_in = models.BooleanField(
        default=True,
        verbose_name="Requerir entrada",
    )

    require_clock_out = models.BooleanField(
        default=True,
        verbose_name="Requerir salida",
    )

    require_break_start = models.BooleanField(
        default=True,
        verbose_name="Requerir inicio de refrigerio",
    )

    require_break_end = models.BooleanField(
        default=True,
        verbose_name="Requerir fin de refrigerio",
    )

    allow_multiple_clock_ins = models.BooleanField(
        default=False,
        verbose_name="Permitir varias entradas",
    )

    allow_multiple_clock_outs = models.BooleanField(
        default=False,
        verbose_name="Permitir varias salidas",
    )

    maximum_daily_clockings = models.PositiveSmallIntegerField(
        default=20,
        verbose_name="Máximo de marcaciones diarias",
    )

    minimum_seconds_between_clockings = (
        models.PositiveIntegerField(
            default=30,
            verbose_name="Segundos mínimos entre marcaciones",
        )
    )

    entry_tolerance_minutes = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Tolerancia de ingreso",
    )

    early_departure_tolerance_minutes = (
        models.PositiveSmallIntegerField(
            default=0,
            verbose_name="Tolerancia de salida anticipada",
        )
    )

    maximum_late_minutes_without_review = (
        models.PositiveSmallIntegerField(
            default=0,
            verbose_name=(
                "Tardanza máxima sin revisión"
            ),
        )
    )

    maximum_early_departure_minutes_without_review = (
        models.PositiveSmallIntegerField(
            default=0,
            verbose_name=(
                "Salida anticipada máxima sin revisión"
            ),
        )
    )

    grace_period_after_schedule_minutes = (
        models.PositiveSmallIntegerField(
            default=240,
            verbose_name=(
                "Plazo posterior al horario para marcar salida"
            ),
        )
    )

    allow_early_clock_in = models.BooleanField(
        default=True,
        verbose_name="Permitir ingreso anticipado",
    )

    maximum_early_clock_in_minutes = (
        models.PositiveSmallIntegerField(
            default=120,
            verbose_name=(
                "Máximo de anticipación para marcar"
            ),
        )
    )

    allow_clock_out_after_midnight = models.BooleanField(
        default=False,
        verbose_name="Permitir salida después de medianoche",
    )

    missing_clock_in_action = models.CharField(
        max_length=30,
        choices=MissingClockingAction.choices,
        default=MissingClockingAction.REQUIRE_CORRECTION,
        verbose_name="Acción por entrada faltante",
    )

    missing_clock_out_action = models.CharField(
        max_length=30,
        choices=MissingClockingAction.choices,
        default=MissingClockingAction.REQUIRE_CORRECTION,
        verbose_name="Acción por salida faltante",
    )

    missing_break_action = models.CharField(
        max_length=30,
        choices=MissingClockingAction.choices,
        default=MissingClockingAction.REVIEW,
        verbose_name="Acción por refrigerio incompleto",
    )

    break_enabled = models.BooleanField(
        default=True,
        verbose_name="Refrigerio habilitado",
    )

    scheduled_break_minutes = models.PositiveSmallIntegerField(
        default=60,
        verbose_name="Minutos programados de refrigerio",
    )

    minimum_break_minutes = models.PositiveSmallIntegerField(
        default=30,
        verbose_name="Mínimo de refrigerio",
    )

    maximum_break_minutes = models.PositiveSmallIntegerField(
        default=90,
        verbose_name="Máximo de refrigerio",
    )

    break_tolerance_minutes = models.PositiveSmallIntegerField(
        default=5,
        verbose_name="Tolerancia de refrigerio",
    )

    automatically_deduct_break = models.BooleanField(
        default=False,
        verbose_name="Descontar refrigerio automáticamente",
    )

    paid_break = models.BooleanField(
        default=False,
        verbose_name="Refrigerio remunerado",
    )

    require_location = models.BooleanField(
        default=False,
        verbose_name="Requerir ubicación",
    )

    validate_geofence = models.BooleanField(
        default=False,
        verbose_name="Validar geocerca",
    )

    allow_outside_geofence = models.BooleanField(
        default=False,
        verbose_name="Permitir marcación fuera de geocerca",
    )

    outside_geofence_requires_review = models.BooleanField(
        default=True,
        verbose_name=(
            "Marcación fuera de geocerca requiere revisión"
        ),
    )

    maximum_gps_accuracy_meters = models.PositiveIntegerField(
        default=100,
        verbose_name="Precisión máxima aceptada del GPS",
    )

    allow_missing_gps_when_unavailable = models.BooleanField(
        default=False,
        verbose_name=(
            "Permitir ausencia de GPS cuando no esté disponible"
        ),
    )

    require_photo = models.BooleanField(
        default=False,
        verbose_name="Requerir fotografía",
    )

    photo_required_for_clock_in = models.BooleanField(
        default=False,
        verbose_name="Fotografía obligatoria al ingresar",
    )

    photo_required_for_clock_out = models.BooleanField(
        default=False,
        verbose_name="Fotografía obligatoria al salir",
    )

    require_authorized_device = models.BooleanField(
        default=True,
        verbose_name="Requerir dispositivo autorizado",
    )

    allow_shared_devices = models.BooleanField(
        default=True,
        verbose_name="Permitir dispositivos compartidos",
    )

    require_pin_on_shared_device = models.BooleanField(
        default=True,
        verbose_name="Requerir PIN en dispositivo compartido",
    )

    allow_web_clocking = models.BooleanField(
        default=True,
        verbose_name="Permitir marcación web",
    )

    allow_mobile_clocking = models.BooleanField(
        default=False,
        verbose_name="Permitir marcación móvil",
    )

    allow_qr_clocking = models.BooleanField(
        default=False,
        verbose_name="Permitir marcación por QR",
    )

    allow_offline_clocking = models.BooleanField(
        default=False,
        verbose_name="Permitir marcación sin conexión",
    )

    maximum_offline_delay_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Demora máxima de sincronización offline",
    )

    offline_clocking_requires_review = models.BooleanField(
        default=True,
        verbose_name="Marcación offline requiere revisión",
    )

    rounding_enabled = models.BooleanField(
        default=False,
        verbose_name="Aplicar redondeo de tiempo",
    )

    rounding_mode = models.CharField(
        max_length=20,
        choices=RoundingMode.choices,
        default=RoundingMode.NONE,
        verbose_name="Modo de redondeo",
    )

    rounding_interval_minutes = models.PositiveSmallIntegerField(
        default=5,
        verbose_name="Intervalo de redondeo",
    )

    overtime_mode = models.CharField(
        max_length=30,
        choices=OvertimeMode.choices,
        default=OvertimeMode.REQUIRE_APPROVAL,
        db_index=True,
        verbose_name="Control de horas extras",
    )

    minimum_overtime_minutes = models.PositiveSmallIntegerField(
        default=30,
        verbose_name="Mínimo para considerar horas extras",
    )

    maximum_daily_overtime_minutes = models.PositiveIntegerField(
        default=240,
        verbose_name="Máximo diario de horas extras",
    )

    maximum_monthly_overtime_minutes = models.PositiveIntegerField(
        default=3600,
        verbose_name="Máximo mensual de horas extras",
    )

    overtime_approval_level = models.CharField(
        max_length=30,
        choices=ApprovalLevel.choices,
        default=ApprovalLevel.SUPERVISOR,
        verbose_name="Aprobación de horas extras",
    )

    operational_time_enabled = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Control de tiempo operativo",
    )

    require_operational_session = models.BooleanField(
        default=False,
        verbose_name="Requerir sesión operativa",
    )

    maximum_unclassified_minutes_per_day = (
        models.PositiveIntegerField(
            default=480,
            verbose_name=(
                "Máximo diario de tiempo sin clasificar"
            ),
        )
    )

    unclassified_time_requires_review = models.BooleanField(
        default=True,
        verbose_name="Tiempo sin clasificar requiere revisión",
    )

    allow_parallel_operational_sessions = models.BooleanField(
        default=False,
        verbose_name=(
            "Permitir sesiones operativas simultáneas"
        ),
    )

    include_travel_as_productive_time = models.BooleanField(
        default=True,
        verbose_name=(
            "Considerar traslado como tiempo productivo"
        ),
    )

    include_documentation_as_productive_time = (
        models.BooleanField(
            default=True,
            verbose_name=(
                "Considerar documentación como tiempo productivo"
            ),
        )
    )

    include_external_waiting_as_productive_time = (
        models.BooleanField(
            default=False,
            verbose_name=(
                "Considerar espera externa como tiempo productivo"
            ),
        )
    )

    external_waiting_affects_employee = models.BooleanField(
        default=False,
        verbose_name=(
            "Espera externa afecta evaluación del trabajador"
        ),
    )

    company_delay_affects_employee = models.BooleanField(
        default=False,
        verbose_name=(
            "Demora de empresa afecta evaluación del trabajador"
        ),
    )

    client_delay_affects_employee = models.BooleanField(
        default=False,
        verbose_name=(
            "Demora de cliente afecta evaluación del trabajador"
        ),
    )

    supplier_delay_affects_employee = models.BooleanField(
        default=False,
        verbose_name=(
            "Demora de proveedor afecta evaluación del trabajador"
        ),
    )

    evaluation_mode = models.CharField(
        max_length=30,
        choices=EvaluationMode.choices,
        default=EvaluationMode.SCORE_AND_PENALTY,
        db_index=True,
        verbose_name="Modo de evaluación",
    )

    attendance_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("25.00"),
        verbose_name="Peso de asistencia",
    )

    punctuality_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("20.00"),
        verbose_name="Peso de puntualidad",
    )

    schedule_compliance_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("20.00"),
        verbose_name="Peso de cumplimiento de horario",
    )

    productivity_time_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("25.00"),
        verbose_name="Peso de tiempo productivo",
    )

    incident_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10.00"),
        verbose_name="Peso de incidencias",
    )

    late_incident_penalty_points = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal("1.00"),
        verbose_name="Penalización por tardanza",
    )

    unjustified_absence_penalty_points = (
        models.DecimalField(
            max_digits=7,
            decimal_places=2,
            default=Decimal("10.00"),
            verbose_name=(
                "Penalización por ausencia injustificada"
            ),
        )
    )

    incomplete_clocking_penalty_points = (
        models.DecimalField(
            max_digits=7,
            decimal_places=2,
            default=Decimal("1.00"),
            verbose_name=(
                "Penalización por marcación incompleta"
            ),
        )
    )

    early_departure_penalty_points = (
        models.DecimalField(
            max_digits=7,
            decimal_places=2,
            default=Decimal("1.00"),
            verbose_name=(
                "Penalización por salida anticipada"
            ),
        )
    )

    unauthorized_location_penalty_points = (
        models.DecimalField(
            max_digits=7,
            decimal_places=2,
            default=Decimal("1.00"),
            verbose_name=(
                "Penalización por ubicación no autorizada"
            ),
        )
    )

    unauthorized_device_penalty_points = (
        models.DecimalField(
            max_digits=7,
            decimal_places=2,
            default=Decimal("1.00"),
            verbose_name=(
                "Penalización por dispositivo no autorizado"
            ),
        )
    )

    technician_delay_penalty_per_hour = (
        models.DecimalField(
            max_digits=7,
            decimal_places=2,
            default=Decimal("1.00"),
            verbose_name=(
                "Penalización por hora de demora atribuible"
            ),
        )
    )

    maximum_monthly_penalty_points = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal("100.00"),
        verbose_name="Penalización mensual máxima",
    )

    automatically_generate_incidents = models.BooleanField(
        default=True,
        verbose_name="Generar incidencias automáticamente",
    )

    generate_late_incident = models.BooleanField(
        default=True,
        verbose_name="Generar incidencia por tardanza",
    )

    generate_absence_incident = models.BooleanField(
        default=True,
        verbose_name="Generar incidencia por ausencia",
    )

    generate_early_departure_incident = models.BooleanField(
        default=True,
        verbose_name="Generar incidencia por salida anticipada",
    )

    generate_missing_clocking_incident = models.BooleanField(
        default=True,
        verbose_name="Generar incidencia por marcación faltante",
    )

    generate_excess_break_incident = models.BooleanField(
        default=True,
        verbose_name="Generar incidencia por exceso de refrigerio",
    )

    generate_location_incident = models.BooleanField(
        default=True,
        verbose_name="Generar incidencia de ubicación",
    )

    generate_device_incident = models.BooleanField(
        default=True,
        verbose_name="Generar incidencia de dispositivo",
    )

    generate_unclassified_time_incident = models.BooleanField(
        default=True,
        verbose_name=(
            "Generar incidencia por tiempo sin clasificar"
        ),
    )

    incident_justification_hours = models.PositiveSmallIntegerField(
        default=24,
        verbose_name="Horas para presentar justificación",
    )

    correction_approval_level = models.CharField(
        max_length=30,
        choices=ApprovalLevel.choices,
        default=ApprovalLevel.SUPERVISOR,
        verbose_name="Aprobación de correcciones",
    )

    leave_approval_level = models.CharField(
        max_length=30,
        choices=ApprovalLevel.choices,
        default=ApprovalLevel.SUPERVISOR,
        verbose_name="Aprobación de permisos",
    )

    require_supporting_document_for_medical_leave = (
        models.BooleanField(
            default=True,
            verbose_name=(
                "Requerir sustento para descanso médico"
            ),
        )
    )

    require_supporting_document_for_correction = (
        models.BooleanField(
            default=False,
            verbose_name=(
                "Requerir sustento para correcciones"
            ),
        )
    )

    close_daily_attendance_automatically = (
        models.BooleanField(
            default=False,
            verbose_name=(
                "Cerrar asistencia diaria automáticamente"
            ),
        )
    )

    daily_closure_delay_hours = models.PositiveSmallIntegerField(
        default=24,
        verbose_name="Horas para cierre diario",
    )

    close_monthly_summary_automatically = (
        models.BooleanField(
            default=False,
            verbose_name=(
                "Cerrar resumen mensual automáticamente"
            ),
        )
    )

    monthly_closure_day = models.PositiveSmallIntegerField(
        default=5,
        verbose_name="Día de cierre mensual",
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
        related_name="attendance_policies_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_policies_updated",
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
        related_name="attendance_policies_archived",
        verbose_name="Archivada por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Política de asistencia"
        verbose_name_plural = "Políticas de asistencia"

        ordering = (
            "priority",
            "name",
        )

        indexes = (
            models.Index(
                fields=(
                    "scope",
                    "is_active",
                    "priority",
                ),
                name="att_pol_scope_active_idx",
            ),
            models.Index(
                fields=(
                    "company_name",
                    "department_name",
                    "job_title",
                ),
                name="att_pol_org_scope_idx",
            ),
            models.Index(
                fields=(
                    "schedule",
                    "work_location",
                ),
                name="att_pol_sched_loc_idx",
            ),
            models.Index(
                fields=(
                    "employee_profile",
                    "is_active",
                ),
                name="att_pol_employee_active_idx",
            ),
            models.Index(
                fields=(
                    "effective_from",
                    "effective_until",
                ),
                name="att_pol_effective_idx",
            ),
            models.Index(
                fields=(
                    "operational_time_enabled",
                    "evaluation_mode",
                ),
                name="att_pol_oper_eval_idx",
            ),
            models.Index(
                fields=(
                    "automatically_generate_incidents",
                    "is_active",
                ),
                name="att_pol_auto_inc_idx",
            ),
            models.Index(
                fields=(
                    "overtime_mode",
                    "overtime_approval_level",
                ),
                name="att_pol_overtime_idx",
            ),
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
                name="att_pol_priority_range",
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
                name="att_pol_clockings_range",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    entry_tolerance_minutes__lte=180,
                ),
                name="att_pol_entry_tol_max",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    early_departure_tolerance_minutes__lte=180,
                ),
                name="att_pol_exit_tol_max",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    maximum_break_minutes__lte=300,
                ),
                name="att_pol_break_max",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        monthly_closure_day__gte=1,
                    )
                    & models.Q(
                        monthly_closure_day__lte=28,
                    )
                ),
                name="att_pol_month_close_range",
            ),
        )

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_current(self):
        today = timezone.localdate()

        if self.archived_at is not None:
            return False

        if not self.is_active:
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
    def evaluation_weight_total(self):
        return (
            self.attendance_weight
            + self.punctuality_weight
            + self.schedule_compliance_weight
            + self.productivity_time_weight
            + self.incident_weight
        )

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

        scope_requirements = {
            self.PolicyScope.COMPANY: (
                "company_name",
                self.company_name,
                "Debes indicar la empresa.",
            ),
            self.PolicyScope.DEPARTMENT: (
                "department_name",
                self.department_name,
                "Debes indicar el área o departamento.",
            ),
            self.PolicyScope.JOB_TITLE: (
                "job_title",
                self.job_title,
                "Debes indicar el cargo.",
            ),
            self.PolicyScope.SCHEDULE: (
                "schedule",
                self.schedule_id,
                "Debes seleccionar el horario.",
            ),
            self.PolicyScope.LOCATION: (
                "work_location",
                self.work_location_id,
                "Debes seleccionar la ubicación.",
            ),
            self.PolicyScope.EMPLOYEE: (
                "employee_profile",
                self.employee_profile_id,
                "Debes seleccionar el trabajador.",
            ),
        }

        requirement = scope_requirements.get(
            self.scope
        )

        if requirement:
            field_name, field_value, message = requirement

            if not field_value:
                errors[field_name] = message

        if (
            self.schedule_id
            and (
                not self.schedule.is_active
                or self.schedule.archived_at
            )
        ):
            errors["schedule"] = (
                "El horario seleccionado no está activo."
            )

        if (
            self.work_location_id
            and (
                not self.work_location.is_active
                or self.work_location.archived_at
            )
        ):
            errors["work_location"] = (
                "La ubicación seleccionada no está activa."
            )

        if (
            self.employee_profile_id
            and self.employee_profile.archived_at
        ):
            errors["employee_profile"] = (
                "El perfil laboral está archivado."
            )

        if (
            self.break_enabled
            and self.minimum_break_minutes
            > self.scheduled_break_minutes
        ):
            errors["minimum_break_minutes"] = (
                "El refrigerio mínimo no puede superar "
                "el tiempo programado."
            )

        if (
            self.break_enabled
            and self.maximum_break_minutes
            < self.scheduled_break_minutes
        ):
            errors["maximum_break_minutes"] = (
                "El refrigerio máximo no puede ser menor "
                "que el programado."
            )

        if (
            not self.break_enabled
            and any(
                (
                    self.require_break_start,
                    self.require_break_end,
                    self.automatically_deduct_break,
                )
            )
        ):
            errors["break_enabled"] = (
                "No puedes exigir o descontar refrigerio "
                "cuando está desactivado."
            )

        if (
            self.automatically_deduct_break
            and (
                self.require_break_start
                or self.require_break_end
            )
        ):
            errors["automatically_deduct_break"] = (
                "No puedes descontar automáticamente y exigir "
                "marcaciones de refrigerio al mismo tiempo."
            )

        if (
            self.validate_geofence
            and not self.require_location
        ):
            errors["require_location"] = (
                "Debes requerir ubicación para validar geocerca."
            )

        if (
            self.photo_required_for_clock_in
            or self.photo_required_for_clock_out
        ) and not self.require_photo:
            errors["require_photo"] = (
                "Debes activar el requerimiento de fotografía."
            )

        if (
            self.require_pin_on_shared_device
            and not self.allow_shared_devices
        ):
            errors["allow_shared_devices"] = (
                "No puedes exigir PIN si no se permiten "
                "dispositivos compartidos."
            )

        if (
            self.allow_offline_clocking
            and self.maximum_offline_delay_minutes <= 0
        ):
            errors["maximum_offline_delay_minutes"] = (
                "Debes indicar el máximo retraso offline."
            )

        if (
            not self.allow_offline_clocking
            and self.maximum_offline_delay_minutes
        ):
            errors["maximum_offline_delay_minutes"] = (
                "El retraso offline debe ser cero cuando "
                "la función está desactivada."
            )

        if (
            self.rounding_enabled
            and self.rounding_mode
            == self.RoundingMode.NONE
        ):
            errors["rounding_mode"] = (
                "Debes seleccionar un modo de redondeo."
            )

        if (
            not self.rounding_enabled
            and self.rounding_mode
            != self.RoundingMode.NONE
        ):
            errors["rounding_mode"] = (
                "El modo debe ser sin redondeo cuando "
                "la función está desactivada."
            )

        if (
            self.rounding_enabled
            and self.rounding_interval_minutes <= 0
        ):
            errors["rounding_interval_minutes"] = (
                "El intervalo debe ser mayor a cero."
            )

        if (
            self.overtime_mode
            == self.OvertimeMode.DISABLED
            and self.minimum_overtime_minutes
        ):
            errors["minimum_overtime_minutes"] = (
                "El mínimo debe ser cero cuando las horas "
                "extras están desactivadas."
            )

        if (
            self.maximum_daily_overtime_minutes
            > self.maximum_monthly_overtime_minutes
        ):
            errors["maximum_daily_overtime_minutes"] = (
                "El máximo diario no puede superar "
                "el máximo mensual."
            )

        if (
            self.require_operational_session
            and not self.operational_time_enabled
        ):
            errors["operational_time_enabled"] = (
                "Debes activar el control de tiempo operativo."
            )

        if (
            self.evaluation_mode
            != self.EvaluationMode.DISABLED
            and self.evaluation_weight_total
            != Decimal("100.00")
        ):
            errors["attendance_weight"] = (
                "La suma de ponderaciones debe ser exactamente 100."
            )

        penalty_fields = (
            "late_incident_penalty_points",
            "unjustified_absence_penalty_points",
            "incomplete_clocking_penalty_points",
            "early_departure_penalty_points",
            "unauthorized_location_penalty_points",
            "unauthorized_device_penalty_points",
            "technician_delay_penalty_per_hour",
            "maximum_monthly_penalty_points",
        )

        for field_name in penalty_fields:
            if getattr(self, field_name) < 0:
                errors[field_name] = (
                    "El valor no puede ser negativo."
                )

        if (
            self.close_daily_attendance_automatically
            and self.daily_closure_delay_hours <= 0
        ):
            errors["daily_closure_delay_hours"] = (
                "Debes indicar el plazo de cierre diario."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(
            *args,
            **kwargs,
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

        self.is_active = False
        self.archived_at = timezone.now()
        self.archived_by = user
        self.archived_reason = reason
        self.updated_by = user

        self.save(
            update_fields=[
                "is_active",
                "archived_at",
                "archived_by",
                "archived_reason",
                "updated_by",
                "updated_at",
            ]
        )

    def restore(self, user=None):
        self.is_active = True
        self.archived_at = None
        self.archived_by = None
        self.archived_reason = ""
        self.updated_by = user

        self.save(
            update_fields=[
                "is_active",
                "archived_at",
                "archived_by",
                "archived_reason",
                "updated_by",
                "updated_at",
            ]
        )