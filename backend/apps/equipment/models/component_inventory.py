# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models

from .base import EquipmentBaseModel
from .component import EquipmentComponent


class ComponentInventory(EquipmentBaseModel):
    """
    Inventario físico de componentes técnicos.

    Permite controlar existencias de:

    - Unidades técnicas.
    - Subpartes.
    - Accesorios.
    - Tóners.
    - Repuestos.

    Los componentes con serie propia se registran individualmente.
    Los componentes sin serie pueden manejarse mediante cantidades.
    """

    class Condition(models.TextChoices):
        NEW = (
            "new",
            "Nuevo",
        )
        USED = (
            "used",
            "Usado",
        )
        REFURBISHED = (
            "refurbished",
            "Reacondicionado",
        )
        REPAIRED = (
            "repaired",
            "Reparado",
        )
        DAMAGED = (
            "damaged",
            "Dañado",
        )
        FOR_PARTS = (
            "for_parts",
            "Para partes",
        )

    class Status(models.TextChoices):
        AVAILABLE = (
            "available",
            "Disponible",
        )
        RESERVED = (
            "reserved",
            "Reservado",
        )
        DELIVERED = (
            "delivered",
            "Entregado",
        )
        INSTALLED = (
            "installed",
            "Instalado",
        )
        UNDER_REPAIR = (
            "under_repair",
            "En reparación",
        )
        RETURNED = (
            "returned",
            "Retornado",
        )
        DISCARDED = (
            "discarded",
            "Desechado",
        )
        NOT_AVAILABLE = (
            "not_available",
            "No disponible",
        )

    component = models.ForeignKey(
        EquipmentComponent,
        on_delete=models.PROTECT,
        related_name="inventory_records",
        verbose_name="Componente",
    )

    internal_code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Código interno",
        help_text=(
            "Código único del registro de inventario."
        ),
    )

    serial_number = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Número de serie",
        help_text=(
            "Serie individual del componente cuando corresponda."
        ),
    )

    lot_number = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Número de lote",
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=1,
        verbose_name="Cantidad",
    )

    reserved_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad reservada",
    )

    condition = models.CharField(
        max_length=30,
        choices=Condition.choices,
        default=Condition.NEW,
        db_index=True,
        verbose_name="Condición",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.AVAILABLE,
        db_index=True,
        verbose_name="Estado",
    )

    warehouse = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Almacén",
    )

    location = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Ubicación",
        help_text=(
            "Estante, zona, caja o posición física."
        ),
    )

    supplier_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Proveedor",
    )

    purchase_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Costo de compra",
    )

    acquisition_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de adquisición",
    )

    initial_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador inicial",
        help_text=(
            "Contador acumulado previo del componente usado "
            "o reacondicionado."
        ),
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activo",
    )

    class Meta:
        verbose_name = "Inventario de componente"
        verbose_name_plural = "Inventario de componentes"
        ordering = (
            "component__name",
            "internal_code",
        )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "component",
                    "serial_number",
                ],
                condition=~models.Q(serial_number=""),
                name="unique_component_inventory_serial",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "component",
                    "status",
                ],
                name="equip_inv_component_status_idx",
            ),
            models.Index(
                fields=[
                    "condition",
                    "status",
                ],
                name="equip_inv_condition_status_idx",
            ),
            models.Index(
                fields=[
                    "warehouse",
                    "status",
                ],
                name="equip_inv_warehouse_status_idx",
            ),
            models.Index(
                fields=[
                    "is_active",
                    "status",
                ],
                name="equip_inv_active_status_idx",
            ),
        ]

    def __str__(self):
        if self.serial_number:
            return (
                f"{self.component} - "
                f"{self.serial_number}"
            )

        return (
            f"{self.component} - "
            f"{self.internal_code}"
        )

    @property
    def available_quantity(self):
        """
        Cantidad disponible después de descontar reservas.
        """

        return self.quantity - self.reserved_quantity

    def clean(self):
        """
        Normaliza y valida el inventario.
        """

        super().clean()

        self.internal_code = str(
            self.internal_code or ""
        ).strip().upper()

        self.serial_number = str(
            self.serial_number or ""
        ).strip().upper()

        self.lot_number = str(
            self.lot_number or ""
        ).strip().upper()

        self.warehouse = str(
            self.warehouse or ""
        ).strip()

        self.location = str(
            self.location or ""
        ).strip()

        self.supplier_name = str(
            self.supplier_name or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        if not self.component_id:
            raise ValidationError(
                {
                    "component": (
                        "El componente es obligatorio."
                    ),
                }
            )

        if not self.internal_code:
            raise ValidationError(
                {
                    "internal_code": (
                        "El código interno es obligatorio."
                    ),
                }
            )

        if self.quantity <= 0:
            raise ValidationError(
                {
                    "quantity": (
                        "La cantidad debe ser mayor que cero."
                    ),
                }
            )

        if self.reserved_quantity < 0:
            raise ValidationError(
                {
                    "reserved_quantity": (
                        "La cantidad reservada no puede ser negativa."
                    ),
                }
            )

        if self.reserved_quantity > self.quantity:
            raise ValidationError(
                {
                    "reserved_quantity": (
                        "La cantidad reservada no puede superar "
                        "la cantidad existente."
                    ),
                }
            )

        if (
            self.component.requires_individual_serial
            and not self.serial_number
        ):
            raise ValidationError(
                {
                    "serial_number": (
                        "Este componente requiere número de serie."
                    ),
                }
            )

        if self.serial_number and self.quantity != 1:
            raise ValidationError(
                {
                    "quantity": (
                        "Un componente controlado por serie debe "
                        "tener cantidad igual a uno."
                    ),
                }
            )

        if (
            self.status == self.Status.AVAILABLE
            and self.available_quantity <= 0
        ):
            raise ValidationError(
                {
                    "status": (
                        "No puede marcarse como disponible porque "
                        "no tiene cantidad libre."
                    ),
                }
            )

        duplicate_code = ComponentInventory.objects.filter(
            internal_code__iexact=self.internal_code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "internal_code": (
                        "Ya existe un registro de inventario "
                        "con este código interno."
                    ),
                }
            )

        if self.component_id and self.serial_number:
            duplicate_serial = ComponentInventory.objects.filter(
                component_id=self.component_id,
                serial_number__iexact=self.serial_number,
            ).exclude(
                pk=self.pk,
            )

            if duplicate_serial.exists():
                raise ValidationError(
                    {
                        "serial_number": (
                            "Esta serie ya está registrada para "
                            "el componente seleccionado."
                        ),
                    }
                )

    def save(self, *args, **kwargs):
        """
        Normaliza y valida antes de guardar.
        """

        self.internal_code = str(
            self.internal_code or ""
        ).strip().upper()

        self.serial_number = str(
            self.serial_number or ""
        ).strip().upper()

        self.lot_number = str(
            self.lot_number or ""
        ).strip().upper()

        self.warehouse = str(
            self.warehouse or ""
        ).strip()

        self.location = str(
            self.location or ""
        ).strip()

        self.supplier_name = str(
            self.supplier_name or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )

    def archive(
        self,
        user=None,
        reason="",
        save=True,
    ):
        self.is_active = False
        self.status = self.Status.NOT_AVAILABLE

        if save:
            self.save(
                update_fields=[
                    "is_active",
                    "status",
                    "updated_at",
                ]
            )

        return super().archive(
            user=user,
            reason=reason,
            save=save,
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        self.is_active = True

        if self.available_quantity > 0:
            self.status = self.Status.AVAILABLE
        else:
            self.status = self.Status.NOT_AVAILABLE

        if save:
            self.save(
                update_fields=[
                    "is_active",
                    "status",
                    "updated_at",
                ]
            )

        return super().restore(
            user=user,
            save=save,
        )