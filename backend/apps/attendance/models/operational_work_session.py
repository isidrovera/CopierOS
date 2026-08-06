# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
)
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .attendance_device import AttendanceDevice
from .daily_attendance import DailyAttendance
from .employee_profile import EmployeeProfile
from .work_location import WorkLocation


class OperationalWorkSession(models.Model):
    """
    Sesión de trabajo operativo realizada por un trabajador.

    Permite medir tiempos vinculados a:

    - Reparaciones de taller.
    - Órdenes de servicio técnico.
    - Instalaciones.
    - Preparaciones.
    - Traslados.
    - Evaluaciones de equipos.
    - Actividades internas.
    - Otras tareas operativas.

    La relación con el documento operativo se implementa mediante
    ContentType para no duplicar campos por cada módulo.

    Ejemplos de objetos vinculados:

    - repairs.Repair
    - services.ServiceOrder
    - rentals.RentalPreparation
    - rentals.RentalInstallation
    """

    class SessionType(models.TextChoices):
        REPAIR = (
            "repair",
            "Reparación",
        )
        TECHNICAL_SERVICE = (
            "technical_service",
            "Servicio técnico",
        )
        INSTALLATION = (
            "installation",
            "Instalación",
        )
        PREPARATION = (
            "preparation",
            "Preparación",
        )
        EVALUATION = (
            "evaluation",
            "Evaluación",
        )
        DELIVERY = (
            "delivery",
            "Entrega",
        )
        PICKUP = (
            "pickup",
            "Recojo",
        )
        TRANSFER = (
            "transfer",
            "Traslado",
        )
        INVENTORY = (
            "inventory",
            "Inventario",
        )
        TRAINING = (
            "training",
            "Capacitación",
        )
        INTERNAL_TASK = (
            "internal_task",
            "Actividad interna",
        )
        ADMINISTRATIVE = (
            "administrative",
            "Actividad administrativa",
        )
        OTHER = (
            "other",
            "Otra actividad",
        )

    class Status(models.TextChoices):
        ASSIGNED = (
            "assigned",
            "Asignada",
        )
        ACCEPTED = (
            "accepted",
            "Aceptada",
        )
        IN_PROGRESS = (
            "in_progress",
            "En ejecución",
        )
        PAUSED = (
            "paused",
            "Pausada",
        )
        WAITING = (
            "waiting",
            "En espera",
        )
        COMPLETED = (
            "completed",
            "Finalizada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )
        REJECTED = (
            "rejected",
            "Rechazada",
        )

    class CurrentStage(models.TextChoices):
        ASSIGNMENT = (
            "assignment",
            "Asignación",
        )
        ACCEPTANCE = (
            "acceptance",
            "Aceptación",
        )
        PREPARATION = (
            "preparation",
            "Preparación",
        )
        TRAVEL_TO_CLIENT = (
            "travel_to_client",
            "Traslado hacia cliente",
        )
        ARRIVAL_AT_CLIENT = (
            "arrival_at_client",
            "Llegada al cliente",
        )
        DIAGNOSIS = (
            "diagnosis",
            "Diagnóstico",
        )
        EXECUTION = (
            "execution",
            "Ejecución del trabajo",
        )
        TESTING = (
            "testing",
            "Pruebas",
        )
        CUSTOMER_VALIDATION = (
            "customer_validation",
            "Validación del cliente",
        )
        DOCUMENTATION = (
            "documentation",
            "Documentación",
        )
        TRAVEL_RETURN = (
            "travel_return",
            "Traslado de retorno",
        )
        WAITING_PART = (
            "waiting_part",
            "Espera de repuesto",
        )
        WAITING_APPROVAL = (
            "waiting_approval",
            "Espera de aprobación",
        )
        WAITING_CUSTOMER = (
            "waiting_customer",
            "Espera del cliente",
        )
        WAITING_EQUIPMENT = (
            "waiting_equipment",
            "Espera de equipo",
        )
        WAITING_INFORMATION = (
            "waiting_information",
            "Espera de información",
        )
        INTERNAL_PAUSE = (
            "internal_pause",
            "Pausa interna",
        )
        COMPLETION = (
            "completion",
            "Finalización",
        )
        OTHER = (
            "other",
            "Otra etapa",
        )

    class Priority(models.TextChoices):
        LOW = (
            "low",
            "Baja",
        )
        NORMAL = (
            "normal",
            "Normal",
        )
        HIGH = (
            "high",
            "Alta",
        )
        URGENT = (
            "urgent",
            "Urgente",
        )
        CRITICAL = (
            "critical",
            "Crítica",
        )

    class CompletionResult(models.TextChoices):
        SUCCESS = (
            "success",
            "Completada correctamente",
        )
        PARTIAL = (
            "partial",
            "Completada parcialmente",
        )
        PENDING_PART = (
            "pending_part",
            "Pendiente por repuesto",
        )
        PENDING_APPROVAL = (
            "pending_approval",
            "Pendiente de aprobación",
        )
        PENDING_CUSTOMER = (
            "pending_customer",
            "Pendiente del cliente",
        )
        EQUIPMENT_UNAVAILABLE = (
            "equipment_unavailable",
            "Equipo no disponible",
        )
        NO_FAULT_FOUND = (
            "no_fault_found",
            "No se encontró falla",
        )
        RESCHEDULED = (
            "rescheduled",
            "Reprogramada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )
        OTHER = (
            "other",
            "Otro resultado",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    session_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Número de sesión",
    )

    employee_profile = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.PROTECT,
        related_name="operational_work_sessions",
        verbose_name="Perfil laboral",
    )

    daily_attendance = models.ForeignKey(
        DailyAttendance,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="operational_work_sessions",
        verbose_name="Asistencia diaria",
    )

    session_type = models.CharField(
        max_length=30,
        choices=SessionType.choices,
        db_index=True,
        verbose_name="Tipo de sesión",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ASSIGNED,
        db_index=True,
        verbose_name="Estado",
    )

    current_stage = models.CharField(
        max_length=30,
        choices=CurrentStage.choices,
        default=CurrentStage.ASSIGNMENT,
        db_index=True,
        verbose_name="Etapa actual",
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
        db_index=True,
        verbose_name="Prioridad",
    )

    target_content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_operational_sessions",
        verbose_name="Tipo de documento relacionado",
    )

    target_object_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID del documento relacionado",
    )

    target_object = GenericForeignKey(
        "target_content_type",
        "target_object_id",
    )

    external_reference = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Referencia externa",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Título",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    work_location = models.ForeignKey(
        WorkLocation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="operational_work_sessions",
        verbose_name="Ubicación de trabajo",
    )

    device = models.ForeignKey(
        AttendanceDevice,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="operational_work_sessions",
        verbose_name="Dispositivo",
    )

    assigned_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Asignada el",
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="operational_work_sessions_assigned",
        verbose_name="Asignada por",
    )

    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Aceptada el",
    )

    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Rechazada el",
    )

    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de rechazo",
    )

    scheduled_start_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Inicio programado",
    )

    scheduled_end_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fin programado",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Iniciada el",
    )

    last_resumed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última reanudación",
    )

    paused_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Pausada el",
    )

    waiting_started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Espera iniciada el",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Finalizada el",
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
        related_name="operational_work_sessions_cancelled",
        verbose_name="Cancelada por",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    total_elapsed_minutes = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos transcurridos",
    )

    effective_work_minutes = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos efectivos",
    )

    pause_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos de pausa",
    )

    external_waiting_minutes = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos de espera externa",
    )

    internal_waiting_minutes = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos de espera interna",
    )

    travel_minutes = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos de traslado",
    )

    diagnosis_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos de diagnóstico",
    )

    execution_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos de ejecución",
    )

    testing_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos de pruebas",
    )

    documentation_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos de documentación",
    )

    unclassified_minutes = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Minutos sin clasificar",
    )

    expected_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutos esperados",
    )

    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Porcentaje de avance",
    )

    completion_result = models.CharField(
        max_length=30,
        choices=CompletionResult.choices,
        blank=True,
        db_index=True,
        verbose_name="Resultado",
    )

    technician_responsible_delay_minutes = (
        models.PositiveIntegerField(
            default=0,
            db_index=True,
            verbose_name=(
                "Minutos de demora atribuibles al trabajador"
            ),
        )
    )

    company_responsible_delay_minutes = (
        models.PositiveIntegerField(
            default=0,
            verbose_name=(
                "Minutos de demora atribuibles a la empresa"
            ),
        )
    )

    client_responsible_delay_minutes = (
        models.PositiveIntegerField(
            default=0,
            verbose_name=(
                "Minutos de demora atribuibles al cliente"
            ),
        )
    )

    supplier_responsible_delay_minutes = (
        models.PositiveIntegerField(
            default=0,
            verbose_name=(
                "Minutos de demora atribuibles al proveedor"
            ),
        )
    )

    external_responsible_delay_minutes = (
        models.PositiveIntegerField(
            default=0,
            verbose_name="Minutos de demora por causa externa",
        )
    )

    affects_productivity = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Afecta productividad",
    )

    include_in_evaluation = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Incluir en evaluación",
    )

    requires_review = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere revisión",
    )

    review_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de revisión",
    )

    employee_observation = models.TextField(
        blank=True,
        verbose_name="Observación del trabajador",
    )

    supervisor_observation = models.TextField(
        blank=True,
        verbose_name="Observación del supervisor",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Revisada el",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="operational_work_sessions_reviewed",
        verbose_name="Revisada por",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos adicionales",
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
        related_name="operational_work_sessions_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="operational_work_sessions_updated",
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
        related_name="operational_work_sessions_archived",
        verbose_name="Archivada por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Sesión de trabajo operativo"
        verbose_name_plural = "Sesiones de trabajo operativo"

        ordering = (
            "-assigned_at",
            "-created_at",
        )

        indexes = (
            models.Index(
                fields=(
                    "employee_profile",
                    "status",
                    "assigned_at",
                ),
                name="att_ops_emp_status_asg_idx",
            ),
            models.Index(
                fields=(
                    "daily_attendance",
                    "status",
                ),
                name="att_ops_daily_status_idx",
            ),
            models.Index(
                fields=(
                    "session_type",
                    "current_stage",
                    "status",
                ),
                name="att_ops_type_stage_idx",
            ),
            models.Index(
                fields=(
                    "target_content_type",
                    "target_object_id",
                ),
                name="att_ops_target_idx",
            ),
            models.Index(
                fields=(
                    "work_location",
                    "status",
                ),
                name="att_ops_location_status_idx",
            ),
            models.Index(
                fields=(
                    "started_at",
                    "completed_at",
                ),
                name="att_ops_start_end_idx",
            ),
            models.Index(
                fields=(
                    "effective_work_minutes",
                    "external_waiting_minutes",
                ),
                name="att_ops_work_wait_idx",
            ),
            models.Index(
                fields=(
                    "technician_responsible_delay_minutes",
                    "include_in_evaluation",
                ),
                name="att_ops_tech_eval_idx",
            ),
            models.Index(
                fields=(
                    "requires_review",
                    "status",
                ),
                name="att_ops_review_status_idx",
            ),
        )

        constraints = (
            models.CheckConstraint(
                condition=(
                    models.Q(
                        completion_percentage__gte=0,
                    )
                    & models.Q(
                        completion_percentage__lte=100,
                    )
                ),
                name="att_ops_completion_range",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    effective_work_minutes__lte=models.F(
                        "total_elapsed_minutes"
                    ),
                ),
                name="att_ops_effective_lte_elapsed",
            ),
        )

    def __str__(self):
        return (
            f"{self.session_number} - "
            f"{self.employee_profile.user.full_name} - "
            f"{self.title}"
        )

    @property
    def employee(self):
        return self.employee_profile.user

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_active(self):
        return self.status in (
            self.Status.ACCEPTED,
            self.Status.IN_PROGRESS,
            self.Status.PAUSED,
            self.Status.WAITING,
        )

    @property
    def total_delay_minutes(self):
        return (
            self.technician_responsible_delay_minutes
            + self.company_responsible_delay_minutes
            + self.client_responsible_delay_minutes
            + self.supplier_responsible_delay_minutes
            + self.external_responsible_delay_minutes
        )

    @property
    def non_technician_delay_minutes(self):
        return (
            self.company_responsible_delay_minutes
            + self.client_responsible_delay_minutes
            + self.supplier_responsible_delay_minutes
            + self.external_responsible_delay_minutes
        )

    @property
    def productivity_minutes(self):
        return max(
            0,
            self.effective_work_minutes
            - self.technician_responsible_delay_minutes,
        )

    @property
    def efficiency_percentage(self):
        if self.expected_minutes <= 0:
            return 0

        adjusted_minutes = max(
            0,
            self.total_elapsed_minutes
            - self.non_technician_delay_minutes,
        )

        if adjusted_minutes <= 0:
            return 100

        value = (
            self.expected_minutes
            / adjusted_minutes
        ) * 100

        return round(
            min(
                100,
                max(
                    0,
                    value,
                ),
            ),
            2,
        )

    def calculate_total_elapsed_minutes(self):
        if not self.started_at:
            self.total_elapsed_minutes = 0
            return 0

        end_at = self.completed_at or timezone.now()

        if end_at <= self.started_at:
            self.total_elapsed_minutes = 0
            return 0

        self.total_elapsed_minutes = int(
            (
                end_at - self.started_at
            ).total_seconds()
            // 60
        )

        return self.total_elapsed_minutes

    def calculate_effective_work_minutes(self):
        elapsed_minutes = (
            self.calculate_total_elapsed_minutes()
        )

        non_work_minutes = (
            self.pause_minutes
            + self.external_waiting_minutes
            + self.internal_waiting_minutes
        )

        self.effective_work_minutes = max(
            0,
            elapsed_minutes - non_work_minutes,
        )

        return self.effective_work_minutes

    def calculate_unclassified_minutes(self):
        classified_minutes = (
            self.travel_minutes
            + self.diagnosis_minutes
            + self.execution_minutes
            + self.testing_minutes
            + self.documentation_minutes
        )

        self.unclassified_minutes = max(
            0,
            self.effective_work_minutes
            - classified_minutes,
        )

        return self.unclassified_minutes

    def recalculate_times(self):
        self.calculate_effective_work_minutes()
        self.calculate_unclassified_minutes()

        self.save(
            update_fields=[
                "total_elapsed_minutes",
                "effective_work_minutes",
                "unclassified_minutes",
                "updated_at",
            ]
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
            self.employee_profile_id
            and not self.employee_profile.track_operational_time
        ):
            errors["employee_profile"] = (
                "El trabajador no tiene habilitado el "
                "control de tiempo operativo."
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
            self.work_location_id
            and self.work_location.archived_at
        ):
            errors["work_location"] = (
                "La ubicación de trabajo está archivada."
            )

        if (
            self.work_location_id
            and not self.work_location.is_active
        ):
            errors["work_location"] = (
                "La ubicación de trabajo está inactiva."
            )

        if (
            self.device_id
            and not self.device.is_active
        ):
            errors["device"] = (
                "El dispositivo está inactivo."
            )

        if bool(
            self.target_content_type_id
        ) != bool(
            self.target_object_id
        ):
            errors["target_object_id"] = (
                "Debes registrar tanto el tipo como el ID "
                "del documento relacionado."
            )

        if (
            self.scheduled_start_at
            and self.scheduled_end_at
            and self.scheduled_end_at
            <= self.scheduled_start_at
        ):
            errors["scheduled_end_at"] = (
                "El fin programado debe ser posterior "
                "al inicio programado."
            )

        if (
            self.started_at
            and self.completed_at
            and self.completed_at <= self.started_at
        ):
            errors["completed_at"] = (
                "La finalización debe ser posterior al inicio."
            )

        if (
            self.accepted_at
            and self.accepted_at < self.assigned_at
        ):
            errors["accepted_at"] = (
                "La aceptación no puede ser anterior "
                "a la asignación."
            )

        if (
            self.started_at
            and self.accepted_at
            and self.started_at < self.accepted_at
        ):
            errors["started_at"] = (
                "El inicio no puede ser anterior "
                "a la aceptación."
            )

        if (
            self.status == self.Status.REJECTED
            and not self.rejection_reason.strip()
        ):
            errors["rejection_reason"] = (
                "Debes indicar el motivo de rechazo."
            )

        if (
            self.status == self.Status.IN_PROGRESS
            and not self.started_at
        ):
            errors["started_at"] = (
                "Una sesión en ejecución debe tener "
                "fecha de inicio."
            )

        if (
            self.status == self.Status.PAUSED
            and not self.paused_at
        ):
            errors["paused_at"] = (
                "Una sesión pausada debe tener fecha de pausa."
            )

        if (
            self.status == self.Status.WAITING
            and not self.waiting_started_at
        ):
            errors["waiting_started_at"] = (
                "Una sesión en espera debe tener fecha "
                "de inicio de espera."
            )

        if (
            self.status == self.Status.COMPLETED
            and not self.completed_at
        ):
            errors["completed_at"] = (
                "Una sesión finalizada debe tener "
                "fecha de finalización."
            )

        if (
            self.status == self.Status.COMPLETED
            and not self.completion_result
        ):
            errors["completion_result"] = (
                "Debes indicar el resultado de la sesión."
            )

        if (
            self.status == self.Status.CANCELLED
            and not self.cancellation_reason.strip()
        ):
            errors["cancellation_reason"] = (
                "Debes indicar el motivo de cancelación."
            )

        classified_minutes = (
            self.travel_minutes
            + self.diagnosis_minutes
            + self.execution_minutes
            + self.testing_minutes
            + self.documentation_minutes
        )

        if classified_minutes > self.effective_work_minutes:
            errors["effective_work_minutes"] = (
                "Los tiempos clasificados no pueden superar "
                "el tiempo efectivo."
            )

        if self.effective_work_minutes > self.total_elapsed_minutes:
            errors["effective_work_minutes"] = (
                "El tiempo efectivo no puede superar "
                "el tiempo transcurrido."
            )

        if (
            self.total_delay_minutes
            > self.total_elapsed_minutes
            and self.total_elapsed_minutes > 0
        ):
            errors[
                "technician_responsible_delay_minutes"
            ] = (
                "La suma de demoras no puede superar "
                "el tiempo transcurrido."
            )

        if (
            self.requires_review
            and not self.review_reason.strip()
        ):
            errors["review_reason"] = (
                "Debes indicar el motivo de revisión."
            )

        if (
            self.reviewed_at
            and not self.reviewed_by_id
        ):
            errors["reviewed_by"] = (
                "Debes indicar quién revisó la sesión."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def accept(self, user=None):
        if self.status != self.Status.ASSIGNED:
            raise ValidationError(
                "Solo puedes aceptar una sesión asignada."
            )

        self.status = self.Status.ACCEPTED
        self.current_stage = self.CurrentStage.ACCEPTANCE
        self.accepted_at = timezone.now()
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "current_stage",
                "accepted_at",
                "updated_by",
                "updated_at",
            ]
        )

    def reject(
        self,
        user=None,
        reason="",
    ):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de rechazo."
            )

        if self.status != self.Status.ASSIGNED:
            raise ValidationError(
                "Solo puedes rechazar una sesión asignada."
            )

        self.status = self.Status.REJECTED
        self.rejected_at = timezone.now()
        self.rejection_reason = reason
        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "rejected_at",
                "rejection_reason",
                "updated_by",
                "updated_at",
            ]
        )

    def start(
        self,
        user=None,
        stage=None,
    ):
        if self.status not in (
            self.Status.ACCEPTED,
            self.Status.PAUSED,
            self.Status.WAITING,
        ):
            raise ValidationError(
                "La sesión no puede iniciarse o reanudarse "
                "desde su estado actual."
            )

        now = timezone.now()

        if not self.started_at:
            self.started_at = now

        self.last_resumed_at = now
        self.paused_at = None
        self.waiting_started_at = None
        self.status = self.Status.IN_PROGRESS

        self.current_stage = (
            stage
            or self.CurrentStage.EXECUTION
        )

        self.updated_by = user

        self.save(
            update_fields=[
                "started_at",
                "last_resumed_at",
                "paused_at",
                "waiting_started_at",
                "status",
                "current_stage",
                "updated_by",
                "updated_at",
            ]
        )

    def pause(
        self,
        user=None,
        stage=None,
        reason="",
    ):
        if self.status != self.Status.IN_PROGRESS:
            raise ValidationError(
                "Solo puedes pausar una sesión en ejecución."
            )

        self.recalculate_times()

        self.status = self.Status.PAUSED
        self.paused_at = timezone.now()
        self.current_stage = (
            stage
            or self.CurrentStage.INTERNAL_PAUSE
        )

        if reason:
            self.employee_observation = str(
                reason
            ).strip()

        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "paused_at",
                "current_stage",
                "employee_observation",
                "updated_by",
                "updated_at",
            ]
        )

    def start_waiting(
        self,
        stage,
        user=None,
        reason="",
    ):
        allowed_stages = (
            self.CurrentStage.WAITING_PART,
            self.CurrentStage.WAITING_APPROVAL,
            self.CurrentStage.WAITING_CUSTOMER,
            self.CurrentStage.WAITING_EQUIPMENT,
            self.CurrentStage.WAITING_INFORMATION,
        )

        if stage not in allowed_stages:
            raise ValidationError(
                "La etapa indicada no corresponde a una espera."
            )

        if self.status != self.Status.IN_PROGRESS:
            raise ValidationError(
                "Solo puedes iniciar una espera desde "
                "una sesión en ejecución."
            )

        self.recalculate_times()

        self.status = self.Status.WAITING
        self.current_stage = stage
        self.waiting_started_at = timezone.now()

        if reason:
            self.employee_observation = str(
                reason
            ).strip()

        self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "current_stage",
                "waiting_started_at",
                "employee_observation",
                "updated_by",
                "updated_at",
            ]
        )

    def complete(
        self,
        user=None,
        result=CompletionResult.SUCCESS,
        completion_percentage=100,
        observation="",
    ):
        if self.status not in (
            self.Status.IN_PROGRESS,
            self.Status.PAUSED,
            self.Status.WAITING,
        ):
            raise ValidationError(
                "La sesión no puede finalizarse desde "
                "su estado actual."
            )

        if completion_percentage < 0 or completion_percentage > 100:
            raise ValidationError(
                "El porcentaje debe estar entre 0 y 100."
            )

        self.completed_at = timezone.now()
        self.status = self.Status.COMPLETED
        self.current_stage = self.CurrentStage.COMPLETION
        self.completion_result = result
        self.completion_percentage = completion_percentage
        self.paused_at = None
        self.waiting_started_at = None

        if observation:
            self.employee_observation = str(
                observation
            ).strip()

        self.updated_by = user

        self.calculate_effective_work_minutes()
        self.calculate_unclassified_minutes()

        self.save()

    def cancel(
        self,
        user=None,
        reason="",
    ):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de cancelación."
            )

        if self.status in (
            self.Status.COMPLETED,
            self.Status.CANCELLED,
            self.Status.REJECTED,
        ):
            raise ValidationError(
                "La sesión ya no puede cancelarse."
            )

        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancelled_by = user
        self.cancellation_reason = reason
        self.updated_by = user

        if self.started_at:
            self.calculate_effective_work_minutes()
            self.calculate_unclassified_minutes()

        self.save()

    def mark_reviewed(
        self,
        user,
        observation="",
    ):
        self.reviewed_at = timezone.now()
        self.reviewed_by = user
        self.supervisor_observation = str(
            observation or ""
        ).strip()
        self.requires_review = False
        self.review_reason = ""
        self.updated_by = user

        self.save(
            update_fields=[
                "reviewed_at",
                "reviewed_by",
                "supervisor_observation",
                "requires_review",
                "review_reason",
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

        if self.is_active:
            raise ValidationError(
                "No puedes archivar una sesión activa."
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