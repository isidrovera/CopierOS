# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base import ServicesBaseModel
from .service_order import ServiceOrder


class ServiceAssignmentHistory(ServicesBaseModel):
    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="assignment_history",
    )
    previous_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="previous_service_assignments",
    )
    new_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="new_service_assignments",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_assignment_changes",
    )
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["service_order", "created_at"], name="svc_asg_order_date_idx"),
            models.Index(fields=["new_technician", "created_at"], name="svc_asg_tech_date_idx"),
        ]

    def clean(self):
        super().clean()
        self.reason = str(self.reason or "").strip()
        if self.previous_technician_id == self.new_technician_id:
            raise ValidationError({"new_technician": "El técnico debe ser diferente."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class ServiceStatusHistory(ServicesBaseModel):
    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    previous_status = models.CharField(max_length=30, blank=True)
    new_status = models.CharField(
        max_length=30,
        choices=ServiceOrder.Status.choices,
        db_index=True,
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_status_changes",
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    source = models.CharField(max_length=30, default="web", db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["service_order", "created_at"], name="svc_hist_order_date_idx"),
            models.Index(fields=["new_status", "created_at"], name="svc_hist_status_date_idx"),
        ]

    def save(self, *args, **kwargs):
        self.previous_status = str(self.previous_status or "").strip()
        self.source = str(self.source or "").strip().lower()
        self.notes = str(self.notes or "").strip()
        self.full_clean()
        return super().save(*args, **kwargs)
