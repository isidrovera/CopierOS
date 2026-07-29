# -*- coding: utf-8 -*-
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.equipment.models import (
    ComponentInventory,
    Equipment,
    EquipmentComponent,
)
from apps.rentals.models import RentalEquipment

from .base import RepairBaseModel
from .repair_checklist import RepairChecklistItem
from .repair_part_request import RepairPartRequest


class RepairPartRequestItem(RepairBaseModel):
    class ItemType(models.TextChoices):
        SPARE_PART = "spare_part", "Repuesto"
        ACCESSORY = "accessory", "Accesorio"
        UNIT = "unit", "Unidad completa"
        SUBPART = "subpart", "Subparte"
        CONSUMABLE = "consumable", "Consumible"
        TONER = "toner", "Tóner"
        HDD = "hdd", "Disco duro"
        POWER_CABLE = "power_cable", "Cable de poder"
        BASE_WHEEL = "base_wheel", "Rueda de base"
        COVER = "cover", "Tapa"
        PANEL = "panel", "Panel"
        OTHER = "other", "Otro"

    class RequestOrigin(models.TextChoices):
        CHECKLIST = "checklist", "Checklist"
        DIAGNOSIS = "diagnosis", "Diagnóstico"
        EXTERNAL_INSPECTION = "external_inspection", "Inspección externa"
        MISSING_ACCESSORY = "missing_accessory", "Accesorio faltante"
        MANUAL = "manual", "Solicitud manual"
        AREA_MANAGER = "area_manager", "Decisión del jefe de área"
        TECHNICAL_TEST = "technical_test", "Prueba técnica"

    class ApprovalRoute(models.TextChoices):
        DIRECT_MANAGEMENT = "direct_management", "Directa a gerencia"
        AREA_MANAGER_REVIEW = (
            "area_manager_review",
            "Revisión previa del jefe de área",
        )

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        REQUESTED = "requested", "Solicitado"
        PENDING_AREA_REVIEW = (
            "pending_area_review",
            "Pendiente de revisión del jefe",
        )
        SOURCE_EVALUATION = "source_evaluation", "Origen en evaluación"
        PENDING_MANAGEMENT = "pending_management", "Pendiente de gerencia"
        INFORMATION_REQUESTED = (
            "information_requested",
            "Información solicitada",
        )
        APPROVED = "approved", "Aprobado"
        PARTIALLY_APPROVED = (
            "partially_approved",
            "Aprobado parcialmente",
        )
        REJECTED = "rejected", "Rechazado"
        PENDING_RESERVATION = "pending_reservation", "Pendiente de reserva"
        PENDING_PURCHASE = "pending_purchase", "Pendiente de compra"
        PENDING_EXTERNAL_REPAIR = (
            "pending_external_repair",
            "Pendiente de reparación externa",
        )
        PENDING_WITHDRAWAL = (
            "pending_withdrawal",
            "Pendiente de autorización de retiro",
        )
        AUTHORIZED_FOR_WITHDRAWAL = (
            "authorized_for_withdrawal",
            "Autorizado para retiro",
        )
        WITHDRAWN = "withdrawn", "Retirado"
        PENDING_LOGISTICS = "pending_logistics", "Pendiente de logística"
        PREPARED = "prepared", "Preparado"
        DELIVERED = "delivered", "Entregado"
        RECEIVED = "received", "Recibido por técnico"
        INSTALLED = "installed", "Instalado"
        PENDING_RETURN = "pending_return", "Pendiente de devolución"
        PENDING_REPLACEMENT = (
            "pending_replacement",
            "Pendiente de reposición",
        )
        COMPLETED = "completed", "Finalizado"
        CANCELLED = "cancelled", "Cancelado"

    class Urgency(models.TextChoices):
        NORMAL = "normal", "Normal"
        HIGH = "high", "Alta"
        CRITICAL = "critical", "Crítica"

    class SourceType(models.TextChoices):
        PENDING = "pending", "Pendiente de definir"
        COMPONENT_STOCK = "component_stock", "Almacén de repuestos"
        RENTAL_WAREHOUSE = (
            "rental_warehouse",
            "Almacén de equipos de alquiler",
        )
        DONOR_FOR_PARTS = "donor_for_parts", "Máquina para partes"
        DONOR_WITH_PROBLEMS = (
            "donor_with_problems",
            "Máquina con problemas",
        )
        DONOR_OPERATIONAL = "donor_operational", "Máquina operativa"
        EXTERNAL_PURCHASE = "external_purchase", "Compra externa"
        EXTERNAL_REPAIR = "external_repair", "Reparación externa"
        NOT_AVAILABLE = "not_available", "Sin disponibilidad"

    class ControlType(models.TextChoices):
        NONE = "none", "Sin control posterior"
        RETURN_DAMAGED = "return_damaged", "Devolver parte dañada"
        REPLACEMENT_REQUIRED = (
            "replacement_required",
            "Reposición obligatoria",
        )
        TEMPORARY_LOAN = "temporary_loan", "Préstamo temporal"

    request = models.ForeignKey(
        RepairPartRequest,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Solicitud",
    )
    checklist_item = models.ForeignKey(
        RepairChecklistItem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="part_request_items",
        verbose_name="Ítem de checklist",
    )
    component = models.ForeignKey(
        EquipmentComponent,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="repair_part_request_items",
        verbose_name="Componente",
    )
    inventory = models.ForeignKey(
        ComponentInventory,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="repair_part_request_items",
        verbose_name="Inventario seleccionado",
    )
    donor_equipment = models.ForeignKey(
        Equipment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="donated_repair_parts",
        verbose_name="Equipo donante",
    )
    donor_rental_equipment = models.ForeignKey(
        RentalEquipment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="donated_repair_parts",
        verbose_name="Equipo de alquiler donante",
    )
    item_type = models.CharField(
        max_length=30,
        choices=ItemType.choices,
        default=ItemType.SPARE_PART,
        db_index=True,
        verbose_name="Tipo de artículo",
    )
    request_origin = models.CharField(
        max_length=30,
        choices=RequestOrigin.choices,
        default=RequestOrigin.MANUAL,
        db_index=True,
        verbose_name="Origen de la solicitud",
    )
    approval_route = models.CharField(
        max_length=40,
        choices=ApprovalRoute.choices,
        default=ApprovalRoute.AREA_MANAGER_REVIEW,
        db_index=True,
        verbose_name="Ruta de aprobación",
    )
    status = models.CharField(
        max_length=40,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )
    urgency = models.CharField(
        max_length=20,
        choices=Urgency.choices,
        default=Urgency.NORMAL,
        db_index=True,
        verbose_name="Urgencia",
    )
    source_type = models.CharField(
        max_length=40,
        choices=SourceType.choices,
        default=SourceType.PENDING,
        db_index=True,
        verbose_name="Origen de abastecimiento",
    )
    control_type = models.CharField(
        max_length=40,
        choices=ControlType.choices,
        default=ControlType.NONE,
        db_index=True,
        verbose_name="Control posterior",
    )
    custom_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre libre",
    )
    custom_code = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Código libre",
    )
    custom_description = models.TextField(
        blank=True,
        verbose_name="Descripción libre",
    )
    requested_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=1,
        verbose_name="Cantidad solicitada",
    )
    approved_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad aprobada",
    )
    reserved_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad reservada",
    )
    delivered_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad entregada",
    )
    received_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad recibida",
    )
    installed_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad instalada",
    )
    returned_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad devuelta",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="repair_part_items_requested",
        verbose_name="Solicitado por",
    )
    technical_reason = models.TextField(
        verbose_name="Motivo técnico",
    )
    area_manager_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones del jefe de área",
    )
    management_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones de gerencia",
    )
    logistics_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones de logística",
    )
    purchase_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones de compra",
    )
    requires_replacement = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere reposición",
    )
    requires_damaged_part_return = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere devolución de parte dañada",
    )

    class Meta:
        verbose_name = "Ítem de solicitud de partes"
        verbose_name_plural = "Ítems de solicitudes de partes"
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=["request", "status"], name="rep_part_item_status_idx"),
            models.Index(
                fields=["approval_route", "status"],
                name="rep_part_item_route_idx",
            ),
            models.Index(
                fields=["source_type", "status"],
                name="rep_part_item_source_idx",
            ),
            models.Index(
                fields=["component", "status"],
                name="rep_part_item_comp_idx",
            ),
        ]

    def __str__(self):
        name = self.component.name if self.component_id else self.custom_name
        return f"{self.request.code} - {name}"

    def clean(self):
        super().clean()
        self.custom_name = str(self.custom_name or "").strip()
        self.custom_code = str(self.custom_code or "").strip().upper()
        self.custom_description = str(self.custom_description or "").strip()
        self.technical_reason = str(self.technical_reason or "").strip()
        self.area_manager_notes = str(self.area_manager_notes or "").strip()
        self.management_notes = str(self.management_notes or "").strip()
        self.logistics_notes = str(self.logistics_notes or "").strip()
        self.purchase_notes = str(self.purchase_notes or "").strip()

        if not self.request_id:
            raise ValidationError({"request": "La solicitud es obligatoria."})

        if not self.component_id and not self.custom_name:
            raise ValidationError(
                {
                    "custom_name": (
                        "Debe seleccionar un componente o registrar un nombre libre."
                    )
                }
            )

        if self.component_id and self.custom_name:
            raise ValidationError(
                {
                    "custom_name": (
                        "No debe registrar un nombre libre cuando ya seleccionó "
                        "un componente."
                    )
                }
            )

        if not self.requested_by_id:
            raise ValidationError(
                {"requested_by": "El usuario solicitante es obligatorio."}
            )

        if not self.technical_reason:
            raise ValidationError(
                {"technical_reason": "El motivo técnico es obligatorio."}
            )

        quantity_fields = (
            "requested_quantity",
            "approved_quantity",
            "reserved_quantity",
            "delivered_quantity",
            "received_quantity",
            "installed_quantity",
            "returned_quantity",
        )

        for field_name in quantity_fields:
            value = getattr(self, field_name)
            if value is None or value < Decimal("0"):
                raise ValidationError(
                    {field_name: "La cantidad no puede ser negativa."}
                )

        if self.requested_quantity <= Decimal("0"):
            raise ValidationError(
                {
                    "requested_quantity": (
                        "La cantidad solicitada debe ser mayor que cero."
                    )
                }
            )

        if self.approved_quantity > self.requested_quantity:
            raise ValidationError(
                {
                    "approved_quantity": (
                        "La cantidad aprobada no puede superar la solicitada."
                    )
                }
            )

        if self.reserved_quantity > self.approved_quantity:
            raise ValidationError(
                {
                    "reserved_quantity": (
                        "La cantidad reservada no puede superar la aprobada."
                    )
                }
            )

        if self.delivered_quantity > self.approved_quantity:
            raise ValidationError(
                {
                    "delivered_quantity": (
                        "La cantidad entregada no puede superar la aprobada."
                    )
                }
            )

        if self.received_quantity > self.delivered_quantity:
            raise ValidationError(
                {
                    "received_quantity": (
                        "La cantidad recibida no puede superar la entregada."
                    )
                }
            )

        if self.installed_quantity > self.received_quantity:
            raise ValidationError(
                {
                    "installed_quantity": (
                        "La cantidad instalada no puede superar la recibida."
                    )
                }
            )

        donor_sources = {
            self.SourceType.DONOR_FOR_PARTS,
            self.SourceType.DONOR_WITH_PROBLEMS,
            self.SourceType.DONOR_OPERATIONAL,
        }

        if self.source_type in donor_sources and not self.donor_equipment_id:
            raise ValidationError(
                {"donor_equipment": "Debe seleccionar el equipo donante."}
            )

        if (
            self.source_type == self.SourceType.COMPONENT_STOCK
            and not self.inventory_id
        ):
            raise ValidationError(
                {"inventory": "Debe seleccionar el registro de inventario."}
            )

        if (
            self.donor_rental_equipment_id
            and self.donor_equipment_id
            and self.donor_rental_equipment.equipment_id
            != self.donor_equipment_id
        ):
            raise ValidationError(
                {
                    "donor_rental_equipment": (
                        "El perfil de alquiler no corresponde al equipo donante."
                    )
                }
            )

        self.requires_replacement = (
            self.control_type == self.ControlType.REPLACEMENT_REQUIRED
        )
        self.requires_damaged_part_return = (
            self.control_type == self.ControlType.RETURN_DAMAGED
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
