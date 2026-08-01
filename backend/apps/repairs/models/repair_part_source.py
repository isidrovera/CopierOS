# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models

from apps.equipment.models import Equipment
from apps.rentals.models import (
    RentalEquipment,
    RentalWarehouse,
)

from .base import RepairBaseModel
from .repair_part_request_item import RepairPartRequestItem


class RepairPartSource(RepairBaseModel):
    class SourceType(models.TextChoices):
        COMPONENT_STOCK = (
            "component_stock",
            "Repuesto disponible",
        )
        RENTAL_WAREHOUSE = (
            "rental_warehouse",
            "Almacén de alquiler",
        )
        DONOR_FOR_PARTS = (
            "donor_for_parts",
            "Máquina para partes",
        )
        DONOR_WITH_PROBLEMS = (
            "donor_with_problems",
            "Máquina con problemas",
        )
        DONOR_OPERATIONAL = (
            "donor_operational",
            "Máquina operativa",
        )
        EXTERNAL_PURCHASE = (
            "external_purchase",
            "Compra externa",
        )
        EXTERNAL_REPAIR = (
            "external_repair",
            "Reparación externa",
        )
        NOT_AVAILABLE = (
            "not_available",
            "Sin disponibilidad",
        )

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

    component_serial_number = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Serie del componente",
        help_text=(
            "Serie física del componente seleccionado, "
            "cuando corresponda."
        ),
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
        verbose_name="Cantidad preparada",
    )

    warehouse_location = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Ubicación referencial",
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
        verbose_name_plural = (
            "Orígenes de partes para reparaciones"
        )
        ordering = (
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "source_type",
                    "is_confirmed",
                ],
                name="rep_part_source_type_idx",
            ),
            models.Index(
                fields=[
                    "component_serial_number",
                    "is_confirmed",
                ],
                name="rep_part_source_serial_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.item} - "
            f"{self.get_source_type_display()}"
        )

    def clean(self):
        super().clean()

        self.component_serial_number = str(
            self.component_serial_number or ""
        ).strip().upper()

        self.supplier_name = str(
            self.supplier_name or ""
        ).strip()

        self.purchase_reference = str(
            self.purchase_reference or ""
        ).strip().upper()

        self.warehouse_location = str(
            self.warehouse_location or ""
        ).strip()

        self.justification = str(
            self.justification or ""
        ).strip()

        if not self.item_id:
            raise ValidationError(
                {
                    "item": (
                        "El ítem solicitado es obligatorio."
                    ),
                }
            )

        if (
            self.available_quantity < 0
            or self.reserved_quantity < 0
        ):
            raise ValidationError(
                {
                    "available_quantity": (
                        "Las cantidades no pueden ser negativas."
                    ),
                }
            )

        if self.reserved_quantity > self.available_quantity:
            raise ValidationError(
                {
                    "reserved_quantity": (
                        "La cantidad preparada no puede superar "
                        "la cantidad disponible."
                    ),
                }
            )

        if (
            self.source_type
            == self.SourceType.COMPONENT_STOCK
            and self.item.component_id
            and self.item.component.requires_individual_serial
            and not self.component_serial_number
        ):
            raise ValidationError(
                {
                    "component_serial_number": (
                        "Debe registrar la serie física "
                        "del componente."
                    ),
                }
            )

        donor_types = {
            self.SourceType.DONOR_FOR_PARTS,
            self.SourceType.DONOR_WITH_PROBLEMS,
            self.SourceType.DONOR_OPERATIONAL,
        }

        if (
            self.source_type in donor_types
            and not self.donor_equipment_id
        ):
            raise ValidationError(
                {
                    "donor_equipment": (
                        "Debe seleccionar el equipo donante."
                    ),
                }
            )

        if (
            self.source_type not in donor_types
            and self.donor_equipment_id
        ):
            raise ValidationError(
                {
                    "donor_equipment": (
                        "El equipo donante solo corresponde "
                        "a un origen de máquina donante."
                    ),
                }
            )

        if (
            self.source_type
            == self.SourceType.RENTAL_WAREHOUSE
            and not self.rental_warehouse_id
        ):
            raise ValidationError(
                {
                    "rental_warehouse": (
                        "Debe seleccionar el almacén de alquiler."
                    ),
                }
            )

        if (
            self.source_type
            != self.SourceType.RENTAL_WAREHOUSE
            and self.rental_warehouse_id
        ):
            raise ValidationError(
                {
                    "rental_warehouse": (
                        "El almacén de alquiler solo corresponde "
                        "al origen de almacén de alquiler."
                    ),
                }
            )

        if (
            self.source_type
            == self.SourceType.EXTERNAL_PURCHASE
            and not self.supplier_name
            and not self.purchase_reference
        ):
            raise ValidationError(
                {
                    "supplier_name": (
                        "Debe indicar el proveedor o la "
                        "referencia de compra."
                    ),
                }
            )

        if (
            self.donor_rental_equipment_id
            and not self.donor_equipment_id
        ):
            raise ValidationError(
                {
                    "donor_equipment": (
                        "Debe seleccionar el equipo relacionado "
                        "con el perfil de alquiler."
                    ),
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
                        "El perfil de alquiler no corresponde "
                        "al equipo donante."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        self.component_serial_number = str(
            self.component_serial_number or ""
        ).strip().upper()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )