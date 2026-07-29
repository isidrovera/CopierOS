# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models

from apps.equipment.models import ComponentInventory, Equipment
from apps.rentals.models import RentalEquipment, RentalWarehouse

from .base import RepairBaseModel
from .repair_part_request_item import RepairPartRequestItem


class RepairPartSource(RepairBaseModel):
    class SourceType(models.TextChoices):
        COMPONENT_STOCK = "component_stock", "Almacén de repuestos"
        RENTAL_WAREHOUSE = "rental_warehouse", "Almacén de alquiler"
        DONOR_FOR_PARTS = "donor_for_parts", "Máquina para partes"
        DONOR_WITH_PROBLEMS = "donor_with_problems", "Máquina con problemas"
        DONOR_OPERATIONAL = "donor_operational", "Máquina operativa"
        EXTERNAL_PURCHASE = "external_purchase", "Compra externa"
        EXTERNAL_REPAIR = "external_repair", "Reparación externa"
        NOT_AVAILABLE = "not_available", "Sin disponibilidad"

    item = models.OneToOneField(
        RepairPartRequestItem,
        on_delete=models.CASCADE,
        related_name="selected_source",
        verbose_name="Ítem solicitado",
    )
    source_type = models.CharField(
        max_length=40,
        choices=SourceType.choices,
        db_index=True,
        verbose_name="Tipo de origen",
    )
    inventory = models.ForeignKey(
        ComponentInventory,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="repair_part_sources",
        verbose_name="Inventario",
    )
    rental_warehouse = models.ForeignKey(
        RentalWarehouse,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="repair_part_sources",
        verbose_name="Almacén de alquiler",
    )
    donor_equipment = models.ForeignKey(
        Equipment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="repair_part_sources",
        verbose_name="Equipo donante",
    )
    donor_rental_equipment = models.ForeignKey(
        RentalEquipment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="repair_part_sources",
        verbose_name="Perfil de alquiler donante",
    )
    supplier_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Proveedor",
    )
    purchase_reference = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Referencia de compra",
    )
    available_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad disponible",
    )
    reserved_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad reservada",
    )
    warehouse_location = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Ubicación",
    )
    justification = models.TextField(
        blank=True,
        verbose_name="Justificación",
    )
    is_confirmed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Origen confirmado",
    )

    class Meta:
        verbose_name = "Origen de parte para reparación"
        verbose_name_plural = "Orígenes de partes para reparaciones"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.item} - {self.get_source_type_display()}"

    def clean(self):
        super().clean()
        self.supplier_name = str(self.supplier_name or "").strip()
        self.purchase_reference = str(self.purchase_reference or "").strip()
        self.warehouse_location = str(self.warehouse_location or "").strip()
        self.justification = str(self.justification or "").strip()

        if self.available_quantity < 0 or self.reserved_quantity < 0:
            raise ValidationError(
                {"available_quantity": "Las cantidades no pueden ser negativas."}
            )

        if self.reserved_quantity > self.available_quantity:
            raise ValidationError(
                {
                    "reserved_quantity": (
                        "La cantidad reservada no puede superar la disponible."
                    )
                }
            )

        if (
            self.source_type == self.SourceType.COMPONENT_STOCK
            and not self.inventory_id
        ):
            raise ValidationError(
                {"inventory": "Debe seleccionar el inventario."}
            )

        donor_types = {
            self.SourceType.DONOR_FOR_PARTS,
            self.SourceType.DONOR_WITH_PROBLEMS,
            self.SourceType.DONOR_OPERATIONAL,
        }
        if self.source_type in donor_types and not self.donor_equipment_id:
            raise ValidationError(
                {"donor_equipment": "Debe seleccionar el equipo donante."}
            )

        if (
            self.source_type == self.SourceType.RENTAL_WAREHOUSE
            and not self.rental_warehouse_id
        ):
            raise ValidationError(
                {"rental_warehouse": "Debe seleccionar el almacén."}
            )

        if (
            self.source_type == self.SourceType.EXTERNAL_PURCHASE
            and not self.supplier_name
            and not self.purchase_reference
        ):
            raise ValidationError(
                {
                    "supplier_name": (
                        "Debe indicar proveedor o referencia de compra."
                    )
                }
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

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
