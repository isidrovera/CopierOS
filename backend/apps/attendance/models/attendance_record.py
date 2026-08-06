# -*- coding: utf-8 -*-

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .attendance_device import AttendanceDevice
from .employee_device_permission import (
    EmployeeDevicePermission,
)
from .employee_profile import EmployeeProfile
from .work_location import WorkLocation


class AttendanceRecord(models.Model):
    """
    Marcación real realizada por un trabajador.

    Registra:

    - Entrada.
    - Salida.
    - Inicio de refrigerio.
    - Fin de refrigerio.
    - Inicio o fin de comisión.
    - Marcaciones manuales.
    - Ubicación.
    - Dispositivo.
    - Precisión del GPS.
    - Validaciones y observaciones.
    """

    class RecordType(models.TextChoices):
        CLOCK_IN = (
            "clock_in",
            "Entrada",
        )
        CLOCK_OUT = (
            "clock_out",
            "Salida",
        )
        BREAK_START = (
            "break_start",
            "Inicio de refrigerio",
        )
        BREAK_END = (
            "break_end",
            "Fin de refrigerio",
        )
        FIELD_WORK_START = (
            "field_work_start",
            "Inicio de trabajo de campo",
        )
        FIELD_WORK_END = (
            "field_work_end",
            "Fin de trabajo de campo",
        )
        REMOTE_WORK_START = (
            "remote_work_start",
            "Inicio de trabajo remoto",
        )
        REMOTE_WORK_END = (
            "remote_work_end",
            "Fin de trabajo remoto",
        )
        COMMISSION_START = (
            "commission_start",
            "Inicio de comisión",
        )
        COMMISSION_END = (
            "commission_end",
            "Fin de comisión",
        )
        MANUAL_ENTRY = (
            "manual_entry",
            "Marcación manual",
        )
        OTHER = (
            "other",
            "Otra marcación",
        )

    class SourceType(models.TextChoices):
        FIXED_DEVICE = (
            "fixed_device",
            "Dispositivo fijo",
        )
        WEB = (
            "web",
            "Navegador web",
        )
        MOBILE = (
            "mobile",
            "Aplicación móvil",
        )
        QR = (
            "qr",
            "Código QR",
        )
        SERVICE_ORDER = (
            "service_order",
            "Orden de servicio",
        )
        REPAIR = (
            "repair",
            "Reparación",
        )
        MANUAL = (
            "manual",
            "Registro manual",
        )
        IMPORT = (
            "import",
            "Importación",
        )
        SYSTEM = (
            "system",
            "Generado por el sistema",
        )

    class ValidationStatus(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente de validación",
        )
        VALID = (
            "valid",
            "Válida",
        )
        OBSERVED = (
            "observed",
            "Observada",
        )
        REJECTED = (
            "rejected",
            "Rechazada",
        )
        CORRECTED = (
            "corrected",
            "Corregida",
        )
        CANCELLED = (
            "cancelled",
            "Anulada",
        )

    class LocationStatus(models.TextChoices):
        NOT_REQUIRED = (
            "not_required",
            "No requerida",
        )
        PENDING = (
            "pending",
            "Pendiente",
        )
        VALID = (
            "valid",
            "Ubicación válida",
        )
        OUTSIDE_GEOFENCE = (
            "outside_geofence",
            "Fuera de geocerca",
        )
        LOW_ACCURACY = (
            "low_accuracy",
            "Precisión insuficiente",
        )
        MISSING = (
            "missing",
            "Sin ubicación",
        )
        INVALID = (
            "invalid",
            "Ubicación inválida",
        )

    class SyncStatus(models.TextChoices):
        ONLINE = (
            "online",
            "Registrada en línea",
        )
        OFFLINE_PENDING = (
            "offline_pending",
            "Pendiente de sincronización",
        )
        OFFLINE_SYNCED = (
            "offline_synced",
            "Sincronizada",
        )
        SYNC_ERROR = (
            "sync_error",
            "Error de sincronización",
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
        related_name="attendance_records",
        verbose_name="Perfil laboral",
    )

    record_type = models.CharField(
        max_length=30,
        choices=RecordType.choices,
        db_index=True,
        verbose_name="Tipo de marcación",
    )

    source_type = models.CharField(
        max_length=30,
        choices=SourceType.choices,
        default=SourceType.WEB,
        db_index=True,
        verbose_name="Origen",
    )

    occurred_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha y hora real",
    )

    local_date = models.DateField(
        db_index=True,
        editable=False,
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

    server_received_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Recibida por el servidor",
    )

    device_reported_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Hora reportada por el dispositivo",
    )

    device = models.ForeignKey(
        AttendanceDevice,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_records",
        verbose_name="Dispositivo",
    )

    device_permission = models.ForeignKey(
        EmployeeDevicePermission,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_records",
        verbose_name="Permiso de dispositivo",
    )

    work_location = models.ForeignKey(
        WorkLocation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_records",
        verbose_name="Ubicación de trabajo",
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

    altitude_meters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Altitud en metros",
    )

    distance_to_location_meters = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Distancia a ubicación autorizada",
    )

    location_status = models.CharField(
        max_length=30,
        choices=LocationStatus.choices,
        default=LocationStatus.NOT_REQUIRED,
        db_index=True,
        verbose_name="Estado de ubicación",
    )

    location_validated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ubicación validada el",
    )

    qr_value_hash = models.CharField(
        max_length=128,
        blank=True,
        editable=False,
        verbose_name="Hash del código QR",
    )

    photo = models.ImageField(
        upload_to="attendance/records/%Y/%m/%d/",
        null=True,
        blank=True,
        verbose_name="Fotografía",
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

    app_version = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Versión de aplicación",
    )

    device_identifier = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Identificador reportado",
    )

    sync_status = models.CharField(
        max_length=30,
        choices=SyncStatus.choices,
        default=SyncStatus.ONLINE,
        db_index=True,
        verbose_name="Estado de sincronización",
    )

    offline_created_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Creada sin conexión el",
    )

    synchronized_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Sincronizada el",
    )

    external_reference = models.CharField(
        max_length=255,
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

    observation = models.TextField(
        blank=True,
        verbose_name="Observación",
    )

    employee_note = models.TextField(
        blank=True,
        verbose_name="Comentario del trabajador",
    )

    validation_status = models.CharField(
        max_length=20,
        choices=ValidationStatus.choices,
        default=ValidationStatus.PENDING,
        db_index=True,
        verbose_name="Estado de validación",
    )

    validation_message = models.TextField(
        blank=True,
        verbose_name="Resultado de validación",
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
        verbose_name="Revisada el",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_records_reviewed",
        verbose_name="Revisada por",
    )

    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de rechazo",
    )

    corrected_record = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="correction_records",
        verbose_name="Marcación corregida",
    )

    is_manual = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Registro manual",
    )

    manual_reason = models.TextField(
        blank=True,
        verbose_name="Motivo del registro manual",
    )

    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_records_registered",
        verbose_name="Registrada por",
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
        related_name="attendance_records_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_records_updated",
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
        related_name="attendance_records_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Marcación de asistencia"
        verbose_name_plural = "Marcaciones de asistencia"

        ordering = (
            "-occurred_at",
            "-created_at",
        )

        indexes = (
            models.Index(
                fields=(
                    "employee_profile",
                    "local_date",
                    "occurred_at",
                ),
                name="att_rec_emp_date_time_idx",
            ),
            models.Index(
                fields=(
                    "record_type",
                    "validation_status",
                ),
                name="att_rec_type_valid_idx",
            ),
            models.Index(
                fields=(
                    "device",
                    "occurred_at",
                ),
                name="att_rec_device_time_idx",
            ),
            models.Index(
                fields=(
                    "work_location",
                    "location_status",
                ),
                name="att_rec_location_status_idx",
            ),
            models.Index(
                fields=(
                    "requires_review",
                    "validation_status",
                ),
                name="att_rec_review_valid_idx",
            ),
            models.Index(
                fields=(
                    "source_type",
                    "sync_status",
                ),
                name="att_rec_source_sync_idx",
            ),
            models.Index(
                fields=(
                    "is_manual",
                    "local_date",
                ),
                name="att_rec_manual_date_idx",
            ),
            models.Index(
                fields=(
                    "external_reference",
                    "occurred_at",
                ),
                name="att_rec_external_time_idx",
            ),
        )

        constraints = (
            models.CheckConstraint(
                condition=(
                    models.Q(
                        latitude__isnull=True,
                    )
                    | (
                        models.Q(
                            latitude__gte=Decimal("-90"),
                        )
                        & models.Q(
                            latitude__lte=Decimal("90"),
                        )
                    )
                ),
                name="att_rec_latitude_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        longitude__isnull=True,
                    )
                    | (
                        models.Q(
                            longitude__gte=Decimal("-180"),
                        )
                        & models.Q(
                            longitude__lte=Decimal("180"),
                        )
                    )
                ),
                name="att_rec_longitude_range",
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
                name="att_rec_accuracy_positive",
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
                name="att_rec_distance_positive",
            ),
        )

    def __str__(self):
        return (
            f"{self.employee_profile.user.full_name} - "
            f"{self.get_record_type_display()} - "
            f"{self.occurred_at}"
        )

    @property
    def employee(self):
        return self.employee_profile.user

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def has_coordinates(self):
        return (
            self.latitude is not None
            and self.longitude is not None
        )

    @property
    def is_valid(self):
        return (
            self.validation_status
            == self.ValidationStatus.VALID
            and self.archived_at is None
        )

    @property
    def is_offline_record(self):
        return self.sync_status in (
            self.SyncStatus.OFFLINE_PENDING,
            self.SyncStatus.OFFLINE_SYNCED,
            self.SyncStatus.SYNC_ERROR,
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
            and not self.employee_profile.attendance_enabled
            and self.source_type
            not in (
                self.SourceType.SYSTEM,
                self.SourceType.MANUAL,
            )
        ):
            errors["employee_profile"] = (
                "El trabajador no tiene habilitado el "
                "control de asistencia."
            )

        if (
            self.device_permission_id
            and self.device_id
            and self.device_permission.device_id
            != self.device_id
        ):
            errors["device_permission"] = (
                "El permiso no corresponde al dispositivo."
            )

        if (
            self.device_permission_id
            and self.employee_profile_id
            and self.device_permission.employee_profile_id
            != self.employee_profile_id
        ):
            errors["device_permission"] = (
                "El permiso no corresponde al trabajador."
            )

        if (
            self.device_id
            and self.source_type
            in (
                self.SourceType.FIXED_DEVICE,
                self.SourceType.MOBILE,
                self.SourceType.WEB,
                self.SourceType.QR,
            )
            and not self.device.can_clock
        ):
            errors["device"] = (
                "El dispositivo no está habilitado para "
                "registrar asistencia."
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
            self.latitude is None
            and self.longitude is not None
        ):
            errors["latitude"] = (
                "Debes indicar la latitud junto con la longitud."
            )

        if (
            self.longitude is None
            and self.latitude is not None
        ):
            errors["longitude"] = (
                "Debes indicar la longitud junto con la latitud."
            )

        if (
            self.location_status
            == self.LocationStatus.VALID
            and not self.has_coordinates
            and self.work_location_id
            and self.work_location.verification_mode
            != self.work_location.VerificationMode.NONE
        ):
            errors["location_status"] = (
                "No puedes validar la ubicación sin coordenadas."
            )

        if (
            self.is_manual
            and not self.manual_reason.strip()
        ):
            errors["manual_reason"] = (
                "Debes indicar el motivo del registro manual."
            )

        if (
            self.source_type == self.SourceType.MANUAL
            and not self.is_manual
        ):
            errors["is_manual"] = (
                "Una marcación manual debe identificarse como tal."
            )

        if (
            self.is_manual
            and not self.registered_by_id
        ):
            errors["registered_by"] = (
                "Debes indicar quién registró la marcación manual."
            )

        if (
            self.validation_status
            == self.ValidationStatus.REJECTED
            and not self.rejection_reason.strip()
        ):
            errors["rejection_reason"] = (
                "Debes indicar el motivo de rechazo."
            )

        if (
            self.validation_status
            == self.ValidationStatus.CORRECTED
            and not self.corrected_record_id
        ):
            errors["corrected_record"] = (
                "Debes indicar qué marcación fue corregida."
            )

        if (
            self.corrected_record_id
            and self.corrected_record_id == self.id
        ):
            errors["corrected_record"] = (
                "Una marcación no puede corregirse a sí misma."
            )

        if (
            self.requires_review
            and not self.review_reason.strip()
        ):
            errors["review_reason"] = (
                "Debes indicar por qué requiere revisión."
            )

        if (
            self.reviewed_at
            and not self.reviewed_by_id
        ):
            errors["reviewed_by"] = (
                "Debes indicar quién revisó la marcación."
            )

        if (
            self.sync_status
            == self.SyncStatus.OFFLINE_PENDING
            and not self.offline_created_at
        ):
            errors["offline_created_at"] = (
                "Debes indicar cuándo se creó la marcación "
                "sin conexión."
            )

        if (
            self.sync_status
            == self.SyncStatus.OFFLINE_SYNCED
            and not self.synchronized_at
        ):
            errors["synchronized_at"] = (
                "Debes indicar cuándo se sincronizó la marcación."
            )

        if (
            self.device_reported_at
            and self.server_received_at
            and self.device_reported_at
            > self.server_received_at
            + timezone.timedelta(minutes=10)
        ):
            errors["device_reported_at"] = (
                "La hora reportada por el dispositivo está "
                "demasiado adelantada."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        local_datetime = timezone.localtime(
            self.occurred_at
        )

        self.local_date = local_datetime.date()
        self.local_time = local_datetime.time()

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def mark_valid(
        self,
        user=None,
        message="",
    ):
        self.validation_status = (
            self.ValidationStatus.VALID
        )

        self.validation_message = str(
            message or ""
        ).strip()

        self.requires_review = False
        self.review_reason = ""
        self.reviewed_at = timezone.now()
        self.reviewed_by = user
        self.updated_by = user

        self.save(
            update_fields=[
                "validation_status",
                "validation_message",
                "requires_review",
                "review_reason",
                "reviewed_at",
                "reviewed_by",
                "updated_by",
                "local_date",
                "local_time",
                "updated_at",
            ]
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

        self.validation_message = reason
        self.requires_review = True
        self.review_reason = reason
        self.reviewed_at = timezone.now()
        self.reviewed_by = user
        self.updated_by = user

        self.save(
            update_fields=[
                "validation_status",
                "validation_message",
                "requires_review",
                "review_reason",
                "reviewed_at",
                "reviewed_by",
                "updated_by",
                "local_date",
                "local_time",
                "updated_at",
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

        self.rejection_reason = reason
        self.validation_message = reason
        self.requires_review = False
        self.review_reason = ""
        self.reviewed_at = timezone.now()
        self.reviewed_by = user
        self.updated_by = user

        self.save(
            update_fields=[
                "validation_status",
                "rejection_reason",
                "validation_message",
                "requires_review",
                "review_reason",
                "reviewed_at",
                "reviewed_by",
                "updated_by",
                "local_date",
                "local_time",
                "updated_at",
            ]
        )

    def mark_location_valid(
        self,
        distance_meters=None,
    ):
        self.location_status = (
            self.LocationStatus.VALID
        )

        self.distance_to_location_meters = (
            distance_meters
        )

        self.location_validated_at = timezone.now()

        self.save(
            update_fields=[
                "location_status",
                "distance_to_location_meters",
                "location_validated_at",
                "local_date",
                "local_time",
                "updated_at",
            ]
        )

    def mark_location_invalid(
        self,
        status,
        reason="",
        distance_meters=None,
    ):
        allowed_statuses = (
            self.LocationStatus.OUTSIDE_GEOFENCE,
            self.LocationStatus.LOW_ACCURACY,
            self.LocationStatus.MISSING,
            self.LocationStatus.INVALID,
        )

        if status not in allowed_statuses:
            raise ValidationError(
                "Estado de ubicación inválido."
            )

        self.location_status = status
        self.distance_to_location_meters = (
            distance_meters
        )

        self.location_validated_at = timezone.now()
        self.requires_review = True
        self.review_reason = str(
            reason or ""
        ).strip()
        self.validation_status = (
            self.ValidationStatus.OBSERVED
        )

        self.save(
            update_fields=[
                "location_status",
                "distance_to_location_meters",
                "location_validated_at",
                "requires_review",
                "review_reason",
                "validation_status",
                "local_date",
                "local_time",
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
                "local_date",
                "local_time",
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
                "local_date",
                "local_time",
                "updated_at",
            ]
        )