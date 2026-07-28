# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from apps.equipment.models import EquipmentComponent

from .base import ServicesBaseModel
from .service_checklist import ServiceChecklistItem
from .service_part_request import ServicePartRequest


class ServicePartRequestItem(ServicesBaseModel):
    class ItemType(models.TextChoices):
        SPARE_PART = "spare_part", "Repuesto técnico"
        CONSUMABLE = "consumable", "Consumible"
        TONER = "toner", "Tóner"
        UNIT = "unit", "Unidad"
        PART = "part", "Parte"
        ACCESSORY = "accessory", "Accesorio"
        EXTERNAL_ITEM = "external_item", "Artículo externo"
        OTHER = "other", "Otro"

    class Urgency(models.TextChoices):
        NORMAL = "normal", "Normal"
        HIGH = "high", "Alta"
        CRITICAL = "critical", "Crítica"

    class ManagementDecision(models.TextChoices):
        PENDING = "pending", "Pendiente"
        APPROVED = "approved", "Aprobado"
        PARTIAL = "partial", "Aprobado parcialmente"
        REJECTED = "rejected", "Rechazado"
        INFORMATION_REQUIRED = (
            "information_required",
            "Requiere información",
        )

    class SupplyMethod(models.TextChoices):
        PENDING = "pending", "Pendiente de definir"
        STOCK = "stock", "Stock de almacén"
        REUSABLE_PART = "reusable_part", "Parte reutilizable"
        DONOR_EQUIPMENT = "donor_equipment", "Equipo donante"
        PURCHASE = "purchase", "Compra"
        EXTERNAL_REPAIR = "external_repair", "Reparación externa"
        NOT_AVAILABLE = "not_available", "No disponible"

    request = models.ForeignKey(
        ServicePartRequest,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Pedido",
    )

    checklist_item = models.ForeignKey(
        ServiceChecklistItem,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="part_request_items",
        verbose_name="Ítem del checklist",
    )

    source_component = models.ForeignKey(
        EquipmentComponent,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="service_part_request_items",
        verbose_name="Componente del catálogo",
    )

    item_type = models.CharField(
        max_length=30,
        choices=ItemType.choices,
        default=ItemType.SPARE_PART,
        db_index=True,
        verbose_name="Tipo de artículo",
    )

    source_component_id_snapshot = models.UUIDField(
        null=True,
        blank=True,
        verbose_name="ID histórico del componente",
    )

    parent_component_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Unidad o componente principal",
    )

    component_code = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Código histórico",
    )

    component_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre histórico",
    )

    manufacturer_code = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Código del fabricante",
    )

    color = models.CharField(
        max_length=30,
        blank=True,
        db_index=True,
        verbose_name="Color",
    )

    custom_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre del artículo libre",
    )

    custom_code = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Código del artículo libre",
    )

    custom_description = models.TextField(
        blank=True,
        verbose_name="Descripción del artículo libre",
    )

    requested_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1.00"),
        verbose_name="Cantidad solicitada",
    )

    approved_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cantidad aprobada",
    )

    stock_confirmed_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cantidad confirmada en stock",
    )

    delivered_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cantidad entregada",
    )

    unit_of_measure = models.CharField(
        max_length=30,
        default="unit",
        verbose_name="Unidad de medida",
    )

    urgency = models.CharField(
        max_length=20,
        choices=Urgency.choices,
        default=Urgency.NORMAL,
        db_index=True,
        verbose_name="Urgencia",
    )

    management_decision = models.CharField(
        max_length=30,
        choices=ManagementDecision.choices,
        default=ManagementDecision.PENDING,
        db_index=True,
        verbose_name="Decisión de gerencia",
    )

    supply_method = models.CharField(
        max_length=30,
        choices=SupplyMethod.choices,
        default=SupplyMethod.PENDING,
        db_index=True,
        verbose_name="Forma de abastecimiento",
    )

    reason = models.TextField(
        verbose_name="Motivo técnico",
    )

    management_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones de gerencia",
    )

    stock_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones de stock",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones generales",
    )

    class Meta:
        ordering = (
            "created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "request",
                    "urgency",
                ],
                name="svc_part_req_urg_idx",
            ),
            models.Index(
                fields=[
                    "component_code",
                ],
                name="svc_part_code_idx",
            ),
            models.Index(
                fields=[
                    "item_type",
                    "management_decision",
                ],
                name="svc_part_type_dec_idx",
            ),
            models.Index(
                fields=[
                    "supply_method",
                    "management_decision",
                ],
                name="svc_part_supply_dec_idx",
            ),
        ]
        verbose_name = "Detalle del pedido"
        verbose_name_plural = "Detalles del pedido"

    def __str__(self):
        return (
            self.display_name
            or f"Detalle {self.pk}"
        )

    @property
    def display_name(self):
        return (
            self.component_name
            or self.custom_name
            or ""
        )

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    def clean(self):
        super().clean()

        self.component_code = self._clean_text(
            self.component_code
        ).upper()

        self.component_name = self._clean_text(
            self.component_name
        )

        self.manufacturer_code = self._clean_text(
            self.manufacturer_code
        )

        self.color = self._clean_text(
            self.color
        ).lower()

        self.custom_name = self._clean_text(
            self.custom_name
        )

        self.custom_code = self._clean_text(
            self.custom_code
        ).upper()

        self.custom_description = self._clean_text(
            self.custom_description
        )

        self.parent_component_name = self._clean_text(
            self.parent_component_name
        )

        self.unit_of_measure = (
            self._clean_text(
                self.unit_of_measure
            )
            or "unit"
        )

        self.reason = self._clean_text(
            self.reason
        )

        self.management_notes = self._clean_text(
            self.management_notes
        )

        self.stock_notes = self._clean_text(
            self.stock_notes
        )

        self.notes = self._clean_text(
            self.notes
        )

        if (
            self.requested_quantity is None
            or self.requested_quantity <= 0
        ):
            raise ValidationError(
                {
                    "requested_quantity": (
                        "La cantidad solicitada debe "
                        "ser mayor que cero."
                    )
                }
            )

        quantity_fields = (
            "approved_quantity",
            "stock_confirmed_quantity",
            "delivered_quantity",
        )

        for field_name in quantity_fields:
            value = getattr(
                self,
                field_name,
            )

            if value is not None and value < 0:
                raise ValidationError(
                    {
                        field_name: (
                            "La cantidad no puede ser negativa."
                        )
                    }
                )

        if (
            self.approved_quantity is not None
            and self.approved_quantity
            > self.requested_quantity
        ):
            raise ValidationError(
                {
                    "approved_quantity": (
                        "La cantidad aprobada no puede "
                        "superar la solicitada."
                    )
                }
            )

        if (
            self.stock_confirmed_quantity is not None
            and self.approved_quantity is not None
            and self.stock_confirmed_quantity
            > self.approved_quantity
        ):
            raise ValidationError(
                {
                    "stock_confirmed_quantity": (
                        "La cantidad confirmada no puede "
                        "superar la aprobada."
                    )
                }
            )

        if (
            self.delivered_quantity is not None
            and self.stock_confirmed_quantity is not None
            and self.delivered_quantity
            > self.stock_confirmed_quantity
        ):
            raise ValidationError(
                {
                    "delivered_quantity": (
                        "La cantidad entregada no puede "
                        "superar la confirmada."
                    )
                }
            )

        has_catalog_item = bool(
            self.source_component_id
        )

        has_custom_item = bool(
            self.custom_name
        )

        if not has_catalog_item and not has_custom_item:
            raise ValidationError(
                {
                    "source_component": (
                        "Seleccione un artículo del catálogo "
                        "o registre un artículo libre."
                    )
                }
            )

        if has_catalog_item and has_custom_item:
            raise ValidationError(
                {
                    "custom_name": (
                        "No registre un artículo libre cuando "
                        "ya seleccionó un componente del catálogo."
                    )
                }
            )

        if not self.reason:
            raise ValidationError(
                {
                    "reason": (
                        "Debe indicar el motivo de la solicitud."
                    )
                }
            )

        if self.checklist_item_id:
            checklist_order_id = (
                self.checklist_item
                .checklist
                .service_order_id
            )

            if (
                checklist_order_id
                != self.request.service_order_id
            ):
                raise ValidationError(
                    {
                        "checklist_item": (
                            "El ítem del checklist pertenece "
                            "a otra orden de servicio."
                        )
                    }
                )

        if (
            self.management_decision
            == self.ManagementDecision.REJECTED
            and not self.management_notes
        ):
            raise ValidationError(
                {
                    "management_notes": (
                        "Gerencia debe indicar el motivo "
                        "del rechazo."
                    )
                }
            )

        if (
            self.management_decision
            == self.ManagementDecision.INFORMATION_REQUIRED
            and not self.management_notes
        ):
            raise ValidationError(
                {
                    "management_notes": (
                        "Gerencia debe indicar qué "
                        "información necesita."
                    )
                }
            )

    def save(self, *args, **kwargs):
        if self.source_component_id:
            component = self.source_component

            self.source_component_id_snapshot = (
                self.source_component_id_snapshot
                or component.id
            )

            self.component_code = (
                self.component_code
                or component.code
            )

            self.component_name = (
                self.component_name
                or component.name
            )

            self.manufacturer_code = (
                self.manufacturer_code
                or component.manufacturer_code
            )

            self.color = (
                self.color
                or component.color
            )

            self.unit_of_measure = (
                self.unit_of_measure
                or component.unit_of_measure
            )

            if (
                not self.parent_component_name
                and component.parent_component_id
            ):
                self.parent_component_name = str(
                    component.parent_component
                )

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )
