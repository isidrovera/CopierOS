# -*- coding: utf-8 -*-
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.equipment.models import Equipment, EquipmentComponent

from .base import ServicesBaseModel
from .service_installation_item import ServiceInstallationItem
from .service_order import ServiceOrder
from .service_part_request import ServicePartRequest
from .service_part_request_item import ServicePartRequestItem
from .service_reusable_part import ServiceReusablePart


class EquipmentInstalledItem(ServicesBaseModel):
    class ItemType(models.TextChoices):
        SPARE_PART = "spare_part", "Repuesto técnico"
        CONSUMABLE = "consumable", "Consumible"
        TONER = "toner", "Tóner"
        UNIT = "unit", "Unidad"
        PART = "part", "Parte"
        ACCESSORY = "accessory", "Accesorio"
        EXTERNAL_ITEM = "external_item", "Artículo externo"
        OTHER = "other", "Otro"

    class OriginType(models.TextChoices):
        STOCK = "stock", "Stock de almacén"
        REUSABLE_PART = "reusable_part", "Parte reutilizable"
        DONOR_EQUIPMENT = "donor_equipment", "Equipo donante"
        PURCHASE = "purchase", "Compra"
        EXTERNAL_REPAIR = "external_repair", "Reparación externa"
        OTHER = "other", "Otro"

    class Status(models.TextChoices):
        INSTALLED = "installed", "Instalado"
        REMOVED = "removed", "Retirado"
        REPLACED = "replaced", "Reemplazado"
        RETURNED = "returned", "Devuelto"
        DISCARDED = "discarded", "Descartado"

    class MeterType(models.TextChoices):
        TOTAL = "total", "Contador total"
        BLACK = "black", "Contador blanco y negro"
        COLOR = "color", "Contador color"
        SCAN = "scan", "Contador escáner"
        NONE = "none", "No aplica"

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="installed_item_history",
        verbose_name="Equipo",
    )

    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.PROTECT,
        related_name="installed_item_history",
        verbose_name="OS de instalación",
    )

    part_request = models.ForeignKey(
        ServicePartRequest,
        on_delete=models.PROTECT,
        related_name="installed_item_history",
        verbose_name="Pedido",
    )

    part_request_item = models.ForeignKey(
        ServicePartRequestItem,
        on_delete=models.PROTECT,
        related_name="installed_item_history",
        verbose_name="Detalle del pedido",
    )

    installation_item = models.OneToOneField(
        ServiceInstallationItem,
        on_delete=models.PROTECT,
        related_name="installed_item_history",
        verbose_name="Ítem de instalación",
    )

    reusable_part = models.ForeignKey(
        ServiceReusablePart,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="installation_history",
        verbose_name="Parte reutilizable",
    )

    component = models.ForeignKey(
        EquipmentComponent,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="installed_equipment_history",
        verbose_name="Componente del catálogo",
    )

    component_id_snapshot = models.UUIDField(
        null=True,
        blank=True,
        verbose_name="ID histórico del componente",
    )

    item_type = models.CharField(
        max_length=30,
        choices=ItemType.choices,
        db_index=True,
        verbose_name="Tipo de artículo",
    )

    origin_type = models.CharField(
        max_length=30,
        choices=OriginType.choices,
        db_index=True,
        verbose_name="Origen",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INSTALLED,
        db_index=True,
        verbose_name="Estado",
    )

    item_code = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Código histórico",
    )

    item_name = models.CharField(
        max_length=200,
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

    serial_number = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Serie de la parte",
    )

    quantity_installed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1.00"),
        verbose_name="Cantidad instalada",
    )

    unit_of_measure = models.CharField(
        max_length=30,
        default="unit",
        verbose_name="Unidad de medida",
    )

    installed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="equipment_items_installed",
        verbose_name="Instalado por",
    )

    installed_at = models.DateTimeField(
        db_index=True,
        verbose_name="Fecha de instalación",
    )

    source_equipment = models.ForeignKey(
        Equipment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="donated_installed_items",
        verbose_name="Equipo de procedencia",
    )

    meter_type = models.CharField(
        max_length=20,
        choices=MeterType.choices,
        default=MeterType.NONE,
        db_index=True,
        verbose_name="Tipo de contador",
    )

    total_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador total",
    )

    black_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador blanco y negro",
    )

    color_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador color",
    )

    scan_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador escáner",
    )

    reference_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Contador de referencia",
    )

    previous_installation = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replacement_records",
        verbose_name="Instalación anterior",
    )

    previous_reference_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador anterior",
    )

    meter_difference = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Duración por contador",
    )

    previous_installed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha del cambio anterior",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        ordering = (
            "-installed_at",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "equipment",
                    "component",
                    "color",
                    "installed_at",
                ],
                name="svc_inst_hist_lookup_idx",
            ),
            models.Index(
                fields=[
                    "equipment",
                    "item_code",
                    "installed_at",
                ],
                name="svc_inst_hist_code_idx",
            ),
            models.Index(
                fields=[
                    "item_type",
                    "installed_at",
                ],
                name="svc_inst_hist_type_idx",
            ),
            models.Index(
                fields=[
                    "meter_type",
                    "reference_meter",
                ],
                name="svc_inst_hist_meter_idx",
            ),
            models.Index(
                fields=[
                    "source_equipment",
                    "installed_at",
                ],
                name="svc_inst_hist_source_idx",
            ),
        ]
        verbose_name = "Artículo instalado en equipo"
        verbose_name_plural = "Historial de artículos instalados"

    def __str__(self):
        return (
            f"{self.equipment} · "
            f"{self.item_name}"
        )

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    def clean(self):
        super().clean()

        self.item_code = self._clean_text(
            self.item_code
        ).upper()

        self.item_name = self._clean_text(
            self.item_name
        )

        self.manufacturer_code = self._clean_text(
            self.manufacturer_code
        )

        self.color = self._clean_text(
            self.color
        ).lower()

        self.serial_number = self._clean_text(
            self.serial_number
        )

        self.unit_of_measure = (
            self._clean_text(
                self.unit_of_measure
            )
            or "unit"
        )

        self.notes = self._clean_text(
            self.notes
        )

        if not self.item_name:
            raise ValidationError(
                {
                    "item_name": (
                        "El nombre histórico es obligatorio."
                    )
                }
            )

        if (
            self.quantity_installed is None
            or self.quantity_installed <= 0
        ):
            raise ValidationError(
                {
                    "quantity_installed": (
                        "La cantidad instalada debe "
                        "ser mayor que cero."
                    )
                }
            )

        if (
            self.installation_item.service_order_id
            != self.service_order_id
        ):
            raise ValidationError(
                {
                    "service_order": (
                        "La OS no coincide con el ítem "
                        "de instalación."
                    )
                }
            )

        if (
            self.installation_item.part_request_item_id
            != self.part_request_item_id
        ):
            raise ValidationError(
                {
                    "part_request_item": (
                        "El detalle del pedido no coincide "
                        "con el ítem de instalación."
                    )
                }
            )

        if (
            self.part_request_item.request_id
            != self.part_request_id
        ):
            raise ValidationError(
                {
                    "part_request": (
                        "El pedido no coincide con su detalle."
                    )
                }
            )

        if (
            self.part_request.service_order.equipment_id
            != self.equipment_id
        ):
            raise ValidationError(
                {
                    "equipment": (
                        "El equipo debe coincidir con la OS "
                        "que originó el pedido."
                    )
                }
            )

        meter_map = {
            self.MeterType.TOTAL: self.total_meter,
            self.MeterType.BLACK: self.black_meter,
            self.MeterType.COLOR: self.color_meter,
            self.MeterType.SCAN: self.scan_meter,
        }

        if (
            self.meter_type != self.MeterType.NONE
            and meter_map.get(self.meter_type) is None
        ):
            raise ValidationError(
                {
                    "meter_type": (
                        "Debe registrar el contador "
                        "seleccionado como referencia."
                    )
                }
            )

        if (
            self.previous_reference_meter is not None
            and self.reference_meter is not None
            and self.reference_meter
            < self.previous_reference_meter
        ):
            raise ValidationError(
                {
                    "reference_meter": (
                        "El contador actual no puede ser menor "
                        "que el contador del cambio anterior."
                    )
                }
            )

    def _load_previous_installation(self):
        queryset = (
            type(self).objects
            .filter(
                equipment_id=self.equipment_id,
                status=self.Status.INSTALLED,
                archived_at__isnull=True,
            )
            .exclude(
                pk=self.pk,
            )
        )

        if self.component_id:
            queryset = queryset.filter(
                component_id=self.component_id,
                color=self.color,
            )
        else:
            queryset = queryset.filter(
                item_code=self.item_code,
                color=self.color,
            )

        return queryset.order_by(
            "-installed_at",
            "-created_at",
        ).first()

    def save(self, *args, **kwargs):
        if self.component_id:
            component = self.component

            self.component_id_snapshot = (
                self.component_id_snapshot
                or component.id
            )

            self.item_code = (
                self.item_code
                or component.code
            )

            self.item_name = (
                self.item_name
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

        meter_map = {
            self.MeterType.TOTAL: self.total_meter,
            self.MeterType.BLACK: self.black_meter,
            self.MeterType.COLOR: self.color_meter,
            self.MeterType.SCAN: self.scan_meter,
        }

        if self.meter_type == self.MeterType.NONE:
            self.reference_meter = None
        else:
            self.reference_meter = meter_map.get(
                self.meter_type
            )

        previous = self._load_previous_installation()

        if previous:
            self.previous_installation = previous
            self.previous_reference_meter = (
                previous.reference_meter
            )
            self.previous_installed_at = (
                previous.installed_at
            )

            if (
                self.reference_meter is not None
                and previous.reference_meter is not None
            ):
                self.meter_difference = (
                    self.reference_meter
                    - previous.reference_meter
                )
            else:
                self.meter_difference = None
        else:
            self.previous_installation = None
            self.previous_reference_meter = None
            self.previous_installed_at = None
            self.meter_difference = None

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )
