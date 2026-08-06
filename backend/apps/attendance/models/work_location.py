# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class WorkLocation(models.Model):
    """
    Lugar autorizado para marcaciones y actividades operativas.

    Puede representar:

    - Oficina.
    - Taller.
    - Almacén.
    - Sede propia.
    - Sede de cliente.
    - Punto temporal.
    - Lugar de trabajo remoto autorizado.
    """

    class LocationType(models.TextChoices):
        COMPANY = (
            "company",
            "Sede de la empresa",
        )
        OFFICE = (
            "office",
            "Oficina",
        )
        WORKSHOP = (
            "workshop",
            "Taller",
        )
        WAREHOUSE = (
            "warehouse",
            "Almacén",
        )
        CLIENT = (
            "client",
            "Sede de cliente",
        )
        SERVICE_POINT = (
            "service_point",
            "Punto de servicio",
        )
        REMOTE = (
            "remote",
            "Trabajo remoto",
        )
        TEMPORARY = (
            "temporary",
            "Ubicación temporal",
        )
        OTHER = (
            "other",
            "Otro",
        )

    class VerificationMode(models.TextChoices):
        NONE = (
            "none",
            "Sin validación geográfica",
        )
        GEOLOCATION = (
            "geolocation",
            "Ubicación GPS",
        )
        QR = (
            "qr",
            "Código QR",
        )
        DEVICE = (
            "device",
            "Dispositivo autorizado",
        )
        GEOLOCATION_AND_QR = (
            "geolocation_and_qr",
            "Ubicación GPS y QR",
        )
        GEOLOCATION_OR_QR = (
            "geolocation_or_qr",
            "Ubicación GPS o QR",
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

    location_type = models.CharField(
        max_length=30,
        choices=LocationType.choices,
        default=LocationType.COMPANY,
        db_index=True,
        verbose_name="Tipo de ubicación",
    )

    company_name = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
        verbose_name="Empresa",
    )

    partner = models.ForeignKey(
        "partners.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_work_locations",
        verbose_name="Cliente o empresa relacionada",
    )

    partner_branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_work_locations",
        verbose_name="Sede relacionada",
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Dirección",
    )

    reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Referencia",
    )

    ubigeo = models.CharField(
        max_length=6,
        blank=True,
        db_index=True,
        verbose_name="Ubigeo",
    )

    district = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Distrito",
    )

    province = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Provincia",
    )

    region = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Departamento",
    )

    country_code = models.CharField(
        max_length=2,
        default="PE",
        db_index=True,
        verbose_name="Código de país",
    )

    timezone_name = models.CharField(
        max_length=100,
        default="America/Lima",
        verbose_name="Zona horaria",
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

    geofence_radius_meters = models.PositiveIntegerField(
        default=150,
        verbose_name="Radio permitido en metros",
    )

    maximum_location_accuracy_meters = (
        models.PositiveIntegerField(
            default=100,
            verbose_name=(
                "Precisión máxima aceptada del GPS en metros"
            ),
        )
    )

    verification_mode = models.CharField(
        max_length=30,
        choices=VerificationMode.choices,
        default=VerificationMode.GEOLOCATION,
        db_index=True,
        verbose_name="Método de validación",
    )

    qr_code_value = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Valor del código QR",
    )

    allows_attendance = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Permite marcar asistencia",
    )

    allows_break_clocking = models.BooleanField(
        default=True,
        verbose_name="Permite marcar refrigerio",
    )

    allows_operational_activity = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Permite actividad operativa",
    )

    allows_service_arrival = models.BooleanField(
        default=False,
        verbose_name="Permite registrar llegada a servicio",
    )

    allows_service_completion = models.BooleanField(
        default=False,
        verbose_name="Permite finalizar servicios",
    )

    requires_photo = models.BooleanField(
        default=False,
        verbose_name="Requiere fotografía",
    )

    requires_observation = models.BooleanField(
        default=False,
        verbose_name="Requiere observación",
    )

    is_temporary = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Ubicación temporal",
    )

    valid_from = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Válida desde",
    )

    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Válida hasta",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activa",
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
        related_name="attendance_work_locations_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_work_locations_updated",
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
        related_name="attendance_work_locations_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Ubicación de trabajo"
        verbose_name_plural = "Ubicaciones de trabajo"

        ordering = (
            "name",
            "code",
        )

        indexes = (
            models.Index(
                fields=(
                    "location_type",
                    "is_active",
                ),
                name="att_loc_type_active_idx",
            ),
            models.Index(
                fields=(
                    "partner",
                    "partner_branch",
                ),
                name="att_loc_partner_branch_idx",
            ),
            models.Index(
                fields=(
                    "allows_attendance",
                    "allows_operational_activity",
                ),
                name="att_loc_att_oper_idx",
            ),
            models.Index(
                fields=(
                    "is_temporary",
                    "valid_from",
                    "valid_until",
                ),
                name="att_loc_temp_valid_idx",
            ),
            models.Index(
                fields=(
                    "region",
                    "province",
                    "district",
                ),
                name="att_loc_geo_area_idx",
            ),
        )

        constraints = (
            models.CheckConstraint(
                condition=(
                    models.Q(
                        geofence_radius_meters__gte=10,
                    )
                    & models.Q(
                        geofence_radius_meters__lte=10000,
                    )
                ),
                name="att_loc_radius_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        maximum_location_accuracy_meters__gte=1,
                    )
                    & models.Q(
                        maximum_location_accuracy_meters__lte=5000,
                    )
                ),
                name="att_loc_accuracy_range",
            ),
        )

    def __str__(self):
        return f"{self.code} - {self.name}"

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
    def is_currently_valid(self):
        now = timezone.now()

        if self.archived_at is not None:
            return False

        if not self.is_active:
            return False

        if (
            self.valid_from
            and self.valid_from > now
        ):
            return False

        if (
            self.valid_until
            and self.valid_until < now
        ):
            return False

        return True

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.partner_branch_id
            and not self.partner_id
        ):
            errors["partner"] = (
                "Debes seleccionar el cliente o empresa "
                "relacionada con la sede."
            )

        if (
            self.partner_branch_id
            and self.partner_id
            and self.partner_branch.partner_id
            != self.partner_id
        ):
            errors["partner_branch"] = (
                "La sede seleccionada no pertenece al cliente "
                "indicado."
            )

        if (
            self.location_type
            == self.LocationType.CLIENT
            and not self.partner_id
        ):
            errors["partner"] = (
                "Una ubicación de cliente debe estar vinculada "
                "a un cliente."
            )

        requires_geolocation = (
            self.verification_mode
            in (
                self.VerificationMode.GEOLOCATION,
                self.VerificationMode.GEOLOCATION_AND_QR,
                self.VerificationMode.GEOLOCATION_OR_QR,
            )
        )

        if (
            requires_geolocation
            and not self.has_coordinates
        ):
            errors["latitude"] = (
                "Debes registrar latitud y longitud para usar "
                "validación geográfica."
            )

        requires_qr = (
            self.verification_mode
            in (
                self.VerificationMode.QR,
                self.VerificationMode.GEOLOCATION_AND_QR,
                self.VerificationMode.GEOLOCATION_OR_QR,
            )
        )

        if (
            requires_qr
            and not self.qr_code_value
        ):
            errors["qr_code_value"] = (
                "Debes registrar el valor del código QR."
            )

        if (
            self.valid_until
            and self.valid_from
            and self.valid_until < self.valid_from
        ):
            errors["valid_until"] = (
                "La fecha final no puede ser anterior a la "
                "fecha inicial."
            )

        if (
            self.is_temporary
            and not self.valid_until
        ):
            errors["valid_until"] = (
                "Una ubicación temporal debe tener fecha final."
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

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def archive(self, user=None, reason=""):
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