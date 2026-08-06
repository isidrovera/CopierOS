# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .attendance_device import AttendanceDevice
from .operational_work_session import OperationalWorkSession
from .work_location import WorkLocation


class OperationalWorkEvent(models.Model):
    """
    Evento histórico de una sesión de trabajo operativo.

    Cada cambio importante de una sesión debe generar un evento:

    - Asignación.
    - Aceptación.
    - Rechazo.
    - Inicio.
    - Cambio de etapa.
    - Inicio de traslado.
    - Llegada al cliente.
    - Inicio de diagnóstico.
    - Inicio de ejecución.
    - Inicio de pruebas.
    - Inicio de documentación.
    - Inicio de pausa.
    - Reanudación.
    - Inicio de espera.
    - Fin de espera.
    - Finalización.
    - Cancelación.
    - Corrección manual.

    Este historial no debe eliminarse ni reemplazarse.
    """

    class EventType(models.TextChoices):
        ASSIGNED = (
            "assigned",
            "Sesión asignada",
        )
        ACCEPTED = (
            "accepted",
            "Sesión aceptada",
        )
        REJECTED = (
            "rejected",
            "Sesión rechazada",
        )
        STARTED = (
            "started",
            "Sesión iniciada",
        )
        STAGE_CHANGED = (
            "stage_changed",
            "Cambio de etapa",
        )
        TRAVEL_STARTED = (
            "travel_started",
            "Traslado iniciado",
        )
        ARRIVED_AT_CLIENT = (
            "arrived_at_client",
            "Llegada al cliente",
        )
        DIAGNOSIS_STARTED = (
            "diagnosis_started",
            "Diagnóstico iniciado",
        )
        EXECUTION_STARTED = (
            "execution_started",
            "Ejecución iniciada",
        )
        TESTING_STARTED = (
            "testing_started",
            "Pruebas iniciadas",
        )
        CUSTOMER_VALIDATION_STARTED = (
            "customer_validation_started",
            "Validación del cliente iniciada",
        )
        DOCUMENTATION_STARTED = (
            "documentation_started",
            "Documentación iniciada",
        )
        RETURN_TRAVEL_STARTED = (
            "return_travel_started",
            "Retorno iniciado",
        )
        PAUSED = (
            "paused",
            "Sesión pausada",
        )
        RESUMED = (
            "resumed",
            "Sesión reanudada",
        )
        WAITING_STARTED = (
            "waiting_started",
            "Espera iniciada",
        )
        WAITING_ENDED = (
            "waiting_ended",
            "Espera finalizada",
        )
        COMPLETED = (
            "completed",
            "Sesión finalizada",
        )
        CANCELLED = (
            "cancelled",
            "Sesión cancelada",
        )
        REVIEW_REQUESTED = (
            "review_requested",
            "Revisión solicitada",
        )
        REVIEWED = (
            "reviewed",
            "Sesión revisada",
        )
        MANUAL_CORRECTION = (
            "manual_correction",
            "Corrección manual",
        )
        LOCATION_UPDATED = (
            "location_updated",
            "Ubicación actualizada",
        )
        DEVICE_CHANGED = (
            "device_changed",
            "Dispositivo cambiado",
        )
        OTHER = (
            "other",
            "Otro evento",
        )

    class TimeCategory(models.TextChoices):
        NONE = (
            "none",
            "Sin categoría de tiempo",
        )
        EFFECTIVE_WORK = (
            "effective_work",
            "Trabajo efectivo",
        )
        TRAVEL = (
            "travel",
            "Traslado",
        )
        DIAGNOSIS = (
            "diagnosis",
            "Diagnóstico",
        )
        EXECUTION = (
            "execution",
            "Ejecución",
        )
        TESTING = (
            "testing",
            "Pruebas",
        )
        DOCUMENTATION = (
            "documentation",
            "Documentación",
        )
        PAUSE = (
            "pause",
            "Pausa",
        )
        INTERNAL_WAITING = (
            "internal_waiting",
            "Espera interna",
        )
        EXTERNAL_WAITING = (
            "external_waiting",
            "Espera externa",
        )
        ADMINISTRATIVE = (
            "administrative",
            "Actividad administrativa",
        )
        OTHER = (
            "other",
            "Otra categoría",
        )

    class ResponsibilityType(models.TextChoices):
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )
        EMPLOYEE = (
            "employee",
            "Trabajador",
        )
        COMPANY = (
            "company",
            "Empresa",
        )
        CLIENT = (
            "client",
            "Cliente",
        )
        SUPPLIER = (
            "supplier",
            "Proveedor",
        )
        TRANSPORT = (
            "transport",
            "Transporte",
        )
        SYSTEM = (
            "system",
            "Sistema",
        )
        DEVICE = (
            "device",
            "Dispositivo",
        )
        EXTERNAL = (
            "external",
            "Causa externa",
        )
        SHARED = (
            "shared",
            "Responsabilidad compartida",
        )
        UNDETERMINED = (
            "undetermined",
            "Por determinar",
        )

    class ValidationStatus(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        VALID = (
            "valid",
            "Válido",
        )
        OBSERVED = (
            "observed",
            "Observado",
        )
        REJECTED = (
            "rejected",
            "Rechazado",
        )
        CORRECTED = (
            "corrected",
            "Corregido",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    session = models.ForeignKey(
        OperationalWorkSession,
        on_delete=models.PROTECT,
        related_name="events",
        verbose_name="Sesión operativa",
    )

    event_type = models.CharField(
        max_length=40,
        choices=EventType.choices,
        db_index=True,
        verbose_name="Tipo de evento",
    )

    time_category = models.CharField(
        max_length=30,
        choices=TimeCategory.choices,
        default=TimeCategory.NONE,
        db_index=True,
        verbose_name="Categoría de tiempo",
    )

    responsibility_type = models.CharField(
        max_length=30,
        choices=ResponsibilityType.choices,
        default=ResponsibilityType.NOT_APPLICABLE,
        db_index=True,
        verbose_name="Responsabilidad",
    )

    validation_status = models.CharField(
        max_length=20,
        choices=ValidationStatus.choices,
        default=ValidationStatus.VALID,
        db_index=True,
        verbose_name="Estado de validación",
    )

    occurred_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha y hora",
    )

    local_date = models.DateField(
        editable=False,
        db_index=True,
        verbose_name="Fecha local",
    )

    local_time = models.TimeField(
        editable=False,
        verbose_name="Hora local",
    )

    timezone_name = models.CharField(
        max_length=100,
        default="America/Lima",
        verbose_name="Zona horaria",
    )

    previous_status = models.CharField(
        max_length=30,
        blank=True,
        db_index=True,
        verbose_name="Estado anterior",
    )

    new_status = models.CharField(
        max_length=30,
        blank=True,
        db_index=True,
        verbose_name="Nuevo estado",
    )

    previous_stage = models.CharField(
        max_length=40,
        blank=True,
        db_index=True,
        verbose_name="Etapa anterior",
    )

    new_stage = models.CharField(
        max_length=40,
        blank=True,
        db_index=True,
        verbose_name="Nueva etapa",
    )

    duration_minutes = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Duración en minutos",
        help_text=(
            "Duración calculada del intervalo que termina "
            "con este evento."
        ),
    )

    started_interval_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Inicio del intervalo",
    )

    ended_interval_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fin del intervalo",
    )

    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Título",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    reason = models.TextField(
        blank=True,
        verbose_name="Motivo",
    )

    work_location = models.ForeignKey(
        WorkLocation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="operational_work_events",
        verbose_name="Ubicación de trabajo",
    )

    device = models.ForeignKey(
        AttendanceDevice,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="operational_work_events",
        verbose_name="Dispositivo",
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Latitud",
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Longitud",
    )

    location_accuracy_meters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Precisión de ubicación en metros",
    )

    distance_to_location_meters = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Distancia a ubicación en metros",
    )

    public_ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP pública",
    )

    local_ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP local",
    )

    user_agent = models.TextField(
        blank=True,
        verbose_name="Agente del navegador",
    )

    source = models.CharField(
        max_length=50,
        default="system",
        db_index=True,
        verbose_name="Origen",
    )

    external_reference = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Referencia externa",
    )

    idempotency_key = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Clave de idempotencia",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos adicionales",
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
        related_name="operational_work_events_reviewed",
        verbose_name="Revisado por",
    )

    corrected_event = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="correction_events",
        verbose_name="Evento corregido",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Creado el",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="operational_work_events_created",
        verbose_name="Creado por",
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
        related_name="operational_work_events_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Evento de trabajo operativo"
        verbose_name_plural = "Eventos de trabajo operativo"

        ordering = (
            "occurred_at",
            "created_at",
        )

        indexes = (
            models.Index(
                fields=(
                    "session",
                    "occurred_at",
                    "event_type",
                ),
                name="att_opevt_sess_time_type_idx",
            ),
            models.Index(
                fields=(
                    "event_type",
                    "validation_status",
                ),
                name="att_opevt_type_valid_idx",
            ),
            models.Index(
                fields=(
                    "time_category",
                    "responsibility_type",
                ),
                name="att_opevt_time_resp_idx",
            ),
            models.Index(
                fields=(
                    "local_date",
                    "event_type",
                ),
                name="att_opevt_date_type_idx",
            ),
            models.Index(
                fields=(
                    "work_location",
                    "occurred_at",
                ),
                name="att_opevt_location_time_idx",
            ),
            models.Index(
                fields=(
                    "device",
                    "occurred_at",
                ),
                name="att_opevt_device_time_idx",
            ),
            models.Index(
                fields=(
                    "requires_review",
                    "validation_status",
                ),
                name="att_opevt_review_valid_idx",
            ),
            models.Index(
                fields=(
                    "previous_status",
                    "new_status",
                ),
                name="att_opevt_status_change_idx",
            ),
            models.Index(
                fields=(
                    "previous_stage",
                    "new_stage",
                ),
                name="att_opevt_stage_change_idx",
            ),
            models.Index(
                fields=(
                    "external_reference",
                    "occurred_at",
                ),
                name="att_opevt_external_time_idx",
            ),
        )

        constraints = (
            models.CheckConstraint(
                condition=models.Q(
                    duration_minutes__gte=0,
                ),
                name="att_opevt_duration_positive",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        location_accuracy_meters__isnull=True,
                    )
                    | models.Q(
                        location_accuracy_meters__gte=0,
                    )
                ),
                name="att_opevt_accuracy_positive",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        distance_to_location_meters__isnull=True,
                    )
                    | models.Q(
                        distance_to_location_meters__gte=0,
                    )
                ),
                name="att_opevt_distance_positive",
            ),
        )

    def __str__(self):
        return (
            f"{self.session.session_number} - "
            f"{self.get_event_type_display()} - "
            f"{self.occurred_at}"
        )

    @property
    def employee_profile(self):
        return self.session.employee_profile

    @property
    def employee(self):
        return self.session.employee_profile.user

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def has_coordinates(self):
        return (
            self.latitude is not None
            and self.longitude is not None
        )

    def calculate_duration(self):
        if (
            not self.started_interval_at
            or not self.ended_interval_at
        ):
            self.duration_minutes = 0
            return 0

        if self.ended_interval_at <= self.started_interval_at:
            self.duration_minutes = 0
            return 0

        self.duration_minutes = int(
            (
                self.ended_interval_at
                - self.started_interval_at
            ).total_seconds()
            // 60
        )

        return self.duration_minutes

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.session_id
            and self.session.archived_at
        ):
            errors["session"] = (
                "La sesión operativa está archivada."
            )

        if (
            self.work_location_id
            and self.work_location.archived_at
        ):
            errors["work_location"] = (
                "La ubicación está archivada."
            )

        if (
            self.work_location_id
            and not self.work_location.is_active
        ):
            errors["work_location"] = (
                "La ubicación está inactiva."
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
            self.started_interval_at
            and not self.ended_interval_at
            and self.duration_minutes
        ):
            errors["duration_minutes"] = (
                "No puedes registrar duración sin finalizar "
                "el intervalo."
            )

        if (
            self.ended_interval_at
            and not self.started_interval_at
        ):
            errors["started_interval_at"] = (
                "Debes indicar el inicio del intervalo."
            )

        if (
            self.started_interval_at
            and self.ended_interval_at
            and self.ended_interval_at
            <= self.started_interval_at
        ):
            errors["ended_interval_at"] = (
                "El fin del intervalo debe ser posterior "
                "al inicio."
            )

        if (
            self.occurred_at
            and self.session_id
            and self.occurred_at < self.session.assigned_at
        ):
            errors["occurred_at"] = (
                "El evento no puede ocurrir antes de "
                "la asignación de la sesión."
            )

        if (
            self.previous_status
            and self.previous_status
            not in OperationalWorkSession.Status.values
        ):
            errors["previous_status"] = (
                "El estado anterior no es válido."
            )

        if (
            self.new_status
            and self.new_status
            not in OperationalWorkSession.Status.values
        ):
            errors["new_status"] = (
                "El nuevo estado no es válido."
            )

        if (
            self.previous_stage
            and self.previous_stage
            not in OperationalWorkSession.CurrentStage.values
        ):
            errors["previous_stage"] = (
                "La etapa anterior no es válida."
            )

        if (
            self.new_stage
            and self.new_stage
            not in OperationalWorkSession.CurrentStage.values
        ):
            errors["new_stage"] = (
                "La nueva etapa no es válida."
            )

        if (
            self.latitude is None
            and self.longitude is not None
        ):
            errors["latitude"] = (
                "Debes registrar la latitud junto "
                "con la longitud."
            )

        if (
            self.longitude is None
            and self.latitude is not None
        ):
            errors["longitude"] = (
                "Debes registrar la longitud junto "
                "con la latitud."
            )

        if (
            self.latitude is not None
            and not (
                -90 <= self.latitude <= 90
            )
        ):
            errors["latitude"] = (
                "La latitud debe estar entre -90 y 90."
            )

        if (
            self.longitude is not None
            and not (
                -180 <= self.longitude <= 180
            )
        ):
            errors["longitude"] = (
                "La longitud debe estar entre -180 y 180."
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
                "Debes indicar quién revisó el evento."
            )

        if (
            self.validation_status
            == self.ValidationStatus.CORRECTED
            and not self.corrected_event_id
        ):
            errors["corrected_event"] = (
                "Debes indicar el evento corregido."
            )

        if (
            self.corrected_event_id
            and self.corrected_event_id == self.id
        ):
            errors["corrected_event"] = (
                "Un evento no puede corregirse a sí mismo."
            )

        if (
            self.corrected_event_id
            and self.corrected_event.session_id
            != self.session_id
        ):
            errors["corrected_event"] = (
                "El evento corregido debe pertenecer "
                "a la misma sesión."
            )

        if (
            self.event_type
            in (
                self.EventType.WAITING_STARTED,
                self.EventType.WAITING_ENDED,
            )
            and self.time_category
            not in (
                self.TimeCategory.INTERNAL_WAITING,
                self.TimeCategory.EXTERNAL_WAITING,
            )
        ):
            errors["time_category"] = (
                "Un evento de espera debe clasificarse "
                "como espera interna o externa."
            )

        if (
            self.time_category
            == self.TimeCategory.EXTERNAL_WAITING
            and self.responsibility_type
            == self.ResponsibilityType.EMPLOYEE
        ):
            errors["responsibility_type"] = (
                "Una espera externa no debe atribuirse "
                "completamente al trabajador."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        local_datetime = timezone.localtime(
            self.occurred_at
        )

        self.local_date = local_datetime.date()
        self.local_time = local_datetime.time()

        if (
            self.started_interval_at
            and self.ended_interval_at
        ):
            self.calculate_duration()

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def mark_observed(
        self,
        reason,
        user=None,
    ):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de observación."
            )

        self.validation_status = (
            self.ValidationStatus.OBSERVED
        )
        self.requires_review = True
        self.review_reason = reason

        self.save(
            update_fields=[
                "validation_status",
                "requires_review",
                "review_reason",
                "local_date",
                "local_time",
            ]
        )

    def mark_valid(
        self,
        user=None,
    ):
        self.validation_status = (
            self.ValidationStatus.VALID
        )
        self.requires_review = False
        self.review_reason = ""
        self.reviewed_at = timezone.now()
        self.reviewed_by = user

        self.save(
            update_fields=[
                "validation_status",
                "requires_review",
                "review_reason",
                "reviewed_at",
                "reviewed_by",
                "local_date",
                "local_time",
            ]
        )

    def reject(
        self,
        reason,
        user=None,
    ):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de rechazo."
            )

        self.validation_status = (
            self.ValidationStatus.REJECTED
        )
        self.requires_review = False
        self.review_reason = reason
        self.reviewed_at = timezone.now()
        self.reviewed_by = user

        self.save(
            update_fields=[
                "validation_status",
                "requires_review",
                "review_reason",
                "reviewed_at",
                "reviewed_by",
                "local_date",
                "local_time",
            ]
        )

    def mark_corrected(
        self,
        corrected_event,
        user=None,
        reason="",
    ):
        if not corrected_event:
            raise ValidationError(
                "Debes indicar el evento corregido."
            )

        if corrected_event.session_id != self.session_id:
            raise ValidationError(
                "El evento corregido no pertenece "
                "a la misma sesión."
            )

        self.validation_status = (
            self.ValidationStatus.CORRECTED
        )
        self.corrected_event = corrected_event
        self.requires_review = False
        self.review_reason = str(
            reason or ""
        ).strip()
        self.reviewed_at = timezone.now()
        self.reviewed_by = user

        self.save(
            update_fields=[
                "validation_status",
                "corrected_event",
                "requires_review",
                "review_reason",
                "reviewed_at",
                "reviewed_by",
                "local_date",
                "local_time",
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

        self.archived_at = timezone.now()
        self.archived_by = user
        self.archived_reason = reason

        self.save(
            update_fields=[
                "archived_at",
                "archived_by",
                "archived_reason",
                "local_date",
                "local_time",
            ]
        )

    def restore(self, user=None):
        self.archived_at = None
        self.archived_by = None
        self.archived_reason = ""

        self.save(
            update_fields=[
                "archived_at",
                "archived_by",
                "archived_reason",
                "local_date",
                "local_time",
            ]
        )