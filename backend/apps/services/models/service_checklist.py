# -*- coding: utf-8 -*-
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.equipment.models import EquipmentComponent

from .base import ServicesBaseModel
from .service_order import ServiceOrder


class ServiceChecklist(ServicesBaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        IN_PROGRESS = "in_progress", "En proceso"
        COMPLETED = "completed", "Completada"
        CANCELLED = "cancelled", "Cancelada"

    service_order = models.OneToOneField(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="checklist",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_checklists_started",
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_checklists_completed",
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    observations = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["status", "created_at"], name="svc_check_status_idx")]

    def clean(self):
        super().clean()
        self.observations = str(self.observations or "").strip()
        if self.status == self.Status.COMPLETED:
            if not self.completed_by_id or not self.completed_at:
                raise ValidationError({"status": "Debe registrar quién y cuándo completó."})
            if self.items.filter(archived_at__isnull=True, is_required=True, status="pending").exists():
                raise ValidationError({"status": "Existen componentes obligatorios pendientes."})

    def save(self, *args, **kwargs):
        if self.status == self.Status.IN_PROGRESS and not self.started_at:
            self.started_at = timezone.now()
        self.full_clean()
        return super().save(*args, **kwargs)


class ServiceChecklistItem(ServicesBaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        OK = "ok", "Correcto"
        OBSERVED = "observed", "Regular / observado"
        FAILED = "failed", "Requiere cambio"
        NOT_APPLICABLE = "not_applicable", "No aplica"

    checklist = models.ForeignKey(ServiceChecklist, on_delete=models.CASCADE, related_name="items")
    source_component = models.ForeignKey(
        EquipmentComponent,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="service_checklist_items",
    )

    source_component_id_snapshot = models.UUIDField(null=True, blank=True)
    component_code = models.CharField(max_length=100, db_index=True)
    component_name = models.CharField(max_length=200)
    component_color = models.CharField(max_length=30, blank=True)
    component_type_name = models.CharField(max_length=150, blank=True)
    category = models.CharField(max_length=30, default="component", db_index=True)
    position = models.CharField(max_length=30, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    is_required = models.BooleanField(default=True, db_index=True)
    observation = models.TextField(blank=True)
    consumable_present = models.BooleanField(null=True, blank=True)
    consumable_level_percent = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    checked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_checklist_items_checked",
    )
    checked_at = models.DateTimeField(null=True, blank=True, db_index=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ("display_order", "component_name")
        constraints = [
            models.UniqueConstraint(
                fields=["checklist", "component_code", "position"],
                name="unique_svc_check_component",
            )
        ]
        indexes = [
            models.Index(fields=["checklist", "status"], name="svc_check_item_st_idx"),
            models.Index(fields=["category", "status"], name="svc_check_cat_st_idx"),
        ]

    def clean(self):
        super().clean()
        self.component_code = str(self.component_code or "").strip().upper()
        self.component_name = str(self.component_name or "").strip()
        self.component_color = str(self.component_color or "").strip()
        self.component_type_name = str(self.component_type_name or "").strip()
        self.category = str(self.category or "").strip().lower()
        self.position = str(self.position or "").strip().lower()
        self.observation = str(self.observation or "").strip()

        if not self.component_code:
            raise ValidationError({"component_code": "El código es obligatorio."})
        if not self.component_name:
            raise ValidationError({"component_name": "El nombre es obligatorio."})
        if self.status != self.Status.PENDING and (not self.checked_by_id or not self.checked_at):
            raise ValidationError({"status": "Debe registrar técnico y fecha."})
        if self.status == self.Status.FAILED and not self.observation:
            raise ValidationError({"observation": "Debe describir la falla."})

    def save(self, *args, **kwargs):
        if self.source_component_id:
            component = self.source_component
            self.source_component_id_snapshot = self.source_component_id_snapshot or component.id
            self.component_code = self.component_code or component.code
            self.component_name = self.component_name or component.name
            self.component_color = self.component_color or component.color
            self.component_type_name = self.component_type_name or str(component.component_type)
        self.full_clean()
        return super().save(*args, **kwargs)


class ServicePartRequest(ServicesBaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        REQUESTED = "requested", "Solicitado"
        REVIEWED = "reviewed", "Revisado"
        APPROVED = "approved", "Aprobado"
        PARTIAL = "partial", "Parcial"
        DELIVERED = "delivered", "Entregado"
        CANCELLED = "cancelled", "Cancelado"

    service_order = models.OneToOneField(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="part_request",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_requests",
    )
    requested_at = models.DateTimeField(null=True, blank=True, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["status", "requested_at"], name="svc_parts_status_idx")]

    def save(self, *args, **kwargs):
        self.notes = str(self.notes or "").strip()
        if self.status == self.Status.REQUESTED and not self.requested_at:
            self.requested_at = timezone.now()
        self.full_clean()
        return super().save(*args, **kwargs)


class ServicePartRequestItem(ServicesBaseModel):
    class Urgency(models.TextChoices):
        NORMAL = "normal", "Normal"
        HIGH = "high", "Alta"
        CRITICAL = "critical", "Crítica"

    request = models.ForeignKey(ServicePartRequest, on_delete=models.CASCADE, related_name="items")
    checklist_item = models.ForeignKey(
        ServiceChecklistItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="part_request_items",
    )
    source_component = models.ForeignKey(
        EquipmentComponent,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="service_part_requests",
    )

    source_component_id_snapshot = models.UUIDField(null=True, blank=True)
    parent_component_name = models.CharField(max_length=200, blank=True)
    component_code = models.CharField(max_length=100, db_index=True)
    component_name = models.CharField(max_length=200)
    manufacturer_code = models.CharField(max_length=120, blank=True)
    color = models.CharField(max_length=30, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("1.00"))
    unit_of_measure = models.CharField(max_length=30, default="unit")
    urgency = models.CharField(max_length=20, choices=Urgency.choices, default=Urgency.NORMAL, db_index=True)
    reason = models.TextField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=["request", "urgency"], name="svc_part_req_urg_idx"),
            models.Index(fields=["component_code"], name="svc_part_code_idx"),
        ]

    def clean(self):
        super().clean()
        self.component_code = str(self.component_code or "").strip().upper()
        self.component_name = str(self.component_name or "").strip()
        self.reason = str(self.reason or "").strip()
        self.notes = str(self.notes or "").strip()
        if self.quantity is None or self.quantity <= 0:
            raise ValidationError({"quantity": "La cantidad debe ser mayor que cero."})
        if not self.component_code or not self.component_name:
            raise ValidationError({"component_name": "El repuesto histórico es obligatorio."})
        if not self.reason:
            raise ValidationError({"reason": "Debe indicar el motivo."})
        if self.checklist_item_id:
            if self.checklist_item.checklist.service_order_id != self.request.service_order_id:
                raise ValidationError({"checklist_item": "El ítem pertenece a otra OS."})

    def save(self, *args, **kwargs):
        if self.source_component_id:
            c = self.source_component
            self.source_component_id_snapshot = self.source_component_id_snapshot or c.id
            self.component_code = self.component_code or c.code
            self.component_name = self.component_name or c.name
            self.manufacturer_code = self.manufacturer_code or c.manufacturer_code
            self.color = self.color or c.color
            self.unit_of_measure = self.unit_of_measure or c.unit_of_measure
            if not self.parent_component_name and c.parent_component_id:
                self.parent_component_name = str(c.parent_component)
        self.full_clean()
        return super().save(*args, **kwargs)
