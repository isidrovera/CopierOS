# -*- coding: utf-8 -*-
import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from .base import ServicesBaseModel
from .service_order import ServiceOrder


def service_evidence_path(instance, filename):
    extension = os.path.splitext(filename)[1].lower() or ".jpg"
    evidence_id = instance.id or uuid.uuid4()
    order_id = instance.service_order_id or "unassigned"
    return f"services/orders/{order_id}/evidence/{instance.stage}/{evidence_id}{extension}"


class ServiceEvidence(ServicesBaseModel):
    class Stage(models.TextChoices):
        BEFORE = "before", "Antes"
        AFTER = "after", "Después"
        GENERAL = "general", "General"
        METER = "meter", "Contador"
        PART = "part", "Repuesto"

    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="evidences",
    )
    stage = models.CharField(max_length=20, choices=Stage.choices, db_index=True)
    file = models.ImageField(upload_to=service_evidence_path)
    captured_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_evidences",
    )
    captured_at = models.DateTimeField(db_index=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    accuracy_meters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    device_id = models.CharField(max_length=150, blank=True, db_index=True)
    is_mock_location = models.BooleanField(default=False, db_index=True)
    sequence = models.PositiveSmallIntegerField(default=1)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("stage", "sequence", "captured_at")
        constraints = [
            models.UniqueConstraint(
                fields=["service_order", "stage", "sequence"],
                name="unique_svc_evidence_seq",
            )
        ]
        indexes = [
            models.Index(fields=["service_order", "stage"], name="svc_evid_order_stage_idx"),
            models.Index(fields=["captured_by", "captured_at"], name="svc_evid_user_date_idx"),
        ]

    def save(self, *args, **kwargs):
        self.device_id = str(self.device_id or "").strip()
        self.notes = str(self.notes or "").strip()
        self.full_clean()
        return super().save(*args, **kwargs)


class ServiceMeterReading(ServicesBaseModel):
    service_order = models.OneToOneField(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="meter_reading",
    )

    initial_total_meter = models.PositiveBigIntegerField(null=True, blank=True)
    initial_black_meter = models.PositiveBigIntegerField(null=True, blank=True)
    initial_color_meter = models.PositiveBigIntegerField(null=True, blank=True)
    initial_scan_meter = models.PositiveBigIntegerField(null=True, blank=True)

    final_total_meter = models.PositiveBigIntegerField(null=True, blank=True)
    final_black_meter = models.PositiveBigIntegerField(null=True, blank=True)
    final_color_meter = models.PositiveBigIntegerField(null=True, blank=True)
    final_scan_meter = models.PositiveBigIntegerField(null=True, blank=True)

    initial_reading_at = models.DateTimeField(null=True, blank=True)
    final_reading_at = models.DateTimeField(null=True, blank=True)
    initial_unavailable_reason = models.TextField(blank=True)
    final_unavailable_reason = models.TextField(blank=True)
    applied_to_equipment_history = models.BooleanField(default=False, db_index=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["applied_to_equipment_history", "created_at"],
                name="svc_meter_applied_idx",
            )
        ]

    def clean(self):
        super().clean()

        self.initial_unavailable_reason = str(self.initial_unavailable_reason or "").strip()
        self.final_unavailable_reason = str(self.final_unavailable_reason or "").strip()

        initial_values = (
            self.initial_total_meter,
            self.initial_black_meter,
            self.initial_color_meter,
            self.initial_scan_meter,
        )
        final_values = (
            self.final_total_meter,
            self.final_black_meter,
            self.final_color_meter,
            self.final_scan_meter,
        )

        if all(value is None for value in initial_values) and not self.initial_unavailable_reason:
            raise ValidationError(
                {"initial_unavailable_reason": "Registre un contador inicial o el motivo."}
            )

        if self.final_reading_at and all(value is None for value in final_values):
            if not self.final_unavailable_reason:
                raise ValidationError(
                    {"final_unavailable_reason": "Registre un contador final o el motivo."}
                )

        pairs = (
            ("final_total_meter", self.initial_total_meter, self.final_total_meter),
            ("final_black_meter", self.initial_black_meter, self.final_black_meter),
            ("final_color_meter", self.initial_color_meter, self.final_color_meter),
            ("final_scan_meter", self.initial_scan_meter, self.final_scan_meter),
        )

        for field_name, initial, final in pairs:
            if initial is not None and final is not None and final < initial:
                raise ValidationError(
                    {field_name: "El contador final no puede ser menor al inicial."}
                )

        if self.initial_reading_at and self.final_reading_at:
            if self.final_reading_at < self.initial_reading_at:
                raise ValidationError(
                    {"final_reading_at": "La fecha final no puede ser anterior."}
                )

        model = self.service_order.equipment.equipment_model

        if not getattr(model, "has_color_meter", False):
            color_values = [
                value
                for value in (self.initial_color_meter, self.final_color_meter)
                if value is not None
            ]
            if any(value > 0 for value in color_values):
                raise ValidationError(
                    {"final_color_meter": "Este modelo no usa contador color."}
                )

        if not getattr(model, "has_scan_meter", False):
            scan_values = [
                value
                for value in (self.initial_scan_meter, self.final_scan_meter)
                if value is not None
            ]
            if any(value > 0 for value in scan_values):
                raise ValidationError(
                    {"final_scan_meter": "Este modelo no usa contador escáner."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
