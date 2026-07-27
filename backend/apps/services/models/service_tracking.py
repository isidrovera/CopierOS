# -*- coding: utf-8 -*-
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .base import ServicesBaseModel
from .service_order import ServiceOrder


class ServiceTrackingSession(ServicesBaseModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Activa"
        COMPLETED = "completed", "Completada"
        CANCELLED = "cancelled", "Cancelada"
        INTERRUPTED = "interrupted", "Interrumpida"

    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="tracking_sessions",
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="service_tracking_sessions",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    started_at = models.DateTimeField(db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True, db_index=True)

    start_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    start_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    end_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    end_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    total_distance_meters = models.PositiveBigIntegerField(default=0)
    moving_seconds = models.PositiveBigIntegerField(default=0)
    stopped_seconds = models.PositiveBigIntegerField(default=0)
    delay_seconds = models.PositiveBigIntegerField(default=0)
    deviation_seconds = models.PositiveBigIntegerField(default=0)
    arrived_geofence_at = models.DateTimeField(null=True, blank=True)
    close_reason = models.TextField(blank=True)

    class Meta:
        ordering = ("-started_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["service_order"],
                condition=models.Q(status="active", archived_at__isnull=True),
                name="unique_active_svc_tracking",
            )
        ]
        indexes = [
            models.Index(fields=["service_order", "status"], name="svc_track_order_st_idx"),
            models.Index(fields=["technician", "status"], name="svc_track_tech_st_idx"),
        ]

    def clean(self):
        super().clean()
        self.close_reason = str(self.close_reason or "").strip()

        if self.service_order_id and self.technician_id:
            assigned_id = self.service_order.assigned_technician_id
            if assigned_id and assigned_id != self.technician_id:
                raise ValidationError(
                    {"technician": "El tracking debe pertenecer al técnico de la OS."}
                )

        if self.ended_at and self.ended_at < self.started_at:
            raise ValidationError({"ended_at": "La fecha final es inválida."})

        if self.status != self.Status.ACTIVE and not self.ended_at:
            raise ValidationError({"ended_at": "La sesión cerrada requiere fecha final."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class ServiceTrackingPoint(ServicesBaseModel):
    class EventType(models.TextChoices):
        PERIODIC = "periodic", "Periódico"
        ROUTE_START = "route_start", "Inicio de ruta"
        GEOFENCE_ENTRY = "geofence_entry", "Ingreso a geocerca"
        ARRIVAL = "arrival", "Llegada"
        SERVICE_START = "service_start", "Inicio de servicio"
        SERVICE_END = "service_end", "Fin de servicio"
        ROUTE_END = "route_end", "Fin de ruta"
        DEVIATION = "deviation", "Posible desvío"

    tracking_session = models.ForeignKey(
        ServiceTrackingSession,
        on_delete=models.CASCADE,
        related_name="points",
    )
    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="tracking_points",
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="service_tracking_points",
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        validators=[MinValueValidator(Decimal("-90")), MaxValueValidator(Decimal("90"))],
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        validators=[MinValueValidator(Decimal("-180")), MaxValueValidator(Decimal("180"))],
    )
    accuracy_meters = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    altitude_meters = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    speed_mps = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    heading_degrees = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    device_recorded_at = models.DateTimeField(db_index=True)
    server_received_at = models.DateTimeField(auto_now_add=True, db_index=True)
    battery_percent = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices,
        default=EventType.PERIODIC,
        db_index=True,
    )
    is_mock_location = models.BooleanField(default=False, db_index=True)
    is_offline_capture = models.BooleanField(default=False, db_index=True)
    sequence_number = models.PositiveBigIntegerField()
    device_id = models.CharField(max_length=150, db_index=True)
    app_version = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ("device_recorded_at", "sequence_number")
        constraints = [
            models.UniqueConstraint(
                fields=["tracking_session", "sequence_number"],
                name="unique_svc_track_sequence",
            )
        ]
        indexes = [
            models.Index(fields=["service_order", "device_recorded_at"], name="svc_point_order_date_idx"),
            models.Index(fields=["tracking_session", "device_recorded_at"], name="svc_point_sess_date_idx"),
            models.Index(fields=["is_mock_location", "device_recorded_at"], name="svc_point_mock_date_idx"),
        ]

    def clean(self):
        super().clean()
        self.device_id = str(self.device_id or "").strip()
        self.app_version = str(self.app_version or "").strip()

        if self.tracking_session_id:
            if self.service_order_id != self.tracking_session.service_order_id:
                raise ValidationError({"service_order": "La OS no corresponde a la sesión."})
            if self.technician_id != self.tracking_session.technician_id:
                raise ValidationError({"technician": "El técnico no corresponde a la sesión."})

        if self.accuracy_meters is not None and self.accuracy_meters < 0:
            raise ValidationError({"accuracy_meters": "La precisión no puede ser negativa."})

        if self.speed_mps is not None and self.speed_mps < 0:
            raise ValidationError({"speed_mps": "La velocidad no puede ser negativa."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
