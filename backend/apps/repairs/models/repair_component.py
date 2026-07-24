# -*- coding: utf-8 -*-
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.equipment.models import (
    ComponentInventory,
    EquipmentComponent,
)

from .base import RepairBaseModel
from .repair import Repair


class RepairComponent(RepairBaseModel):
    """
    Componente, repuesto o consumible utilizado en una reparación.

    Permite registrar:

    - Componentes diagnosticados.
    - Componentes solicitados.
    - Reservas de inventario.
    - Componentes instalados.
    - Componentes retirados.
    - Consumo de repuestos y consumibles.
    - Devoluciones al inventario.
    """

    class MovementType(models.TextChoices):
        REQUIRED = (
            "required",
            "Requerido",
        )
        RESERVED = (
            "reserved",
            "Reservado",
        )
        DELIVERED = (
            "delivered",
            "Entregado al técnico",
        )
        INSTALLED = (
            "installed",
            "Instalado",
        )
        REMOVED = (
            "removed",
            "Retirado",
        )
        RETURNED = (
            "returned",
            "Retornado al inventario",
        )
        CONSUMED = (
            "consumed",
            "Consumido",
        )
        DISCARDED = (
            "discarded",
            "Desechado",
        )

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        REQUESTED = (
            "requested",
            "Solicitado",
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
        REMOVED = (
            "removed",
            "Retirado",
        )
        RETURNED = (
            "returned",
            "Retornado",
        )
        CONSUMED = (
            "consumed",
            "Consumido",
        )
        DISCARDED = (
            "discarded",
            "Desechado",
        )
        CANCELLED = (
            "cancelled",
            "Cancelado",
        )

    class RemovedPartDisposition(models.TextChoices):
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )
        PENDING = (
            "pending",
            "Pendiente de definir",
        )
        RETURN_TO_STOCK = (
            "return_to_stock",
            "Retornar al inventario",
        )
        SEND_TO_REPAIR = (
            "send_to_repair",
            "Enviar a reparación",
        )
        RECOVER_PARTS = (
            "recover_parts",
            "Recuperar partes",
        )
        RETURN_TO_SUPPLIER = (
            "return_to_supplier",
            "Devolver al proveedor",
        )
        DISCARD = (
            "discard",
            "Desechar",
        )

    repair = models.ForeignKey(
        Repair,
        on_delete=models.CASCADE,
        related_name="repair_components",
        verbose_name="Reparación",
    )

    component = models.ForeignKey(
        EquipmentComponent,
        on_delete=models.PROTECT,
        related_name="repair_usages",
        verbose_name="Componente",
    )

    inventory = models.ForeignKey(
        ComponentInventory,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="repair_usages",
        verbose_name="Registro de inventario",
        help_text=(
            "Registro físico o lote de inventario utilizado "
            "en la reparación."
        ),
    )

    movement_type = models.CharField(
        max_length=30,
        choices=MovementType.choices,
        default=MovementType.REQUIRED,
        db_index=True,
        verbose_name="Tipo de movimiento",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
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

    delivered_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad entregada",
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
        verbose_name="Cantidad retornada",
    )

    consumed_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad consumida",
    )

    removed_component = models.ForeignKey(
        EquipmentComponent,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="removed_from_repairs",
        verbose_name="Componente retirado",
    )

    removed_inventory = models.ForeignKey(
        ComponentInventory,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="removed_from_repair_usages",
        verbose_name="Inventario del componente retirado",
    )

    removed_serial_number = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Serie del componente retirado",
    )

    removed_part_disposition = models.CharField(
        max_length=40,
        choices=RemovedPartDisposition.choices,
        default=RemovedPartDisposition.NOT_APPLICABLE,
        db_index=True,
        verbose_name="Destino del componente retirado",
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="requested_repair_components",
        verbose_name="Solicitado por",
    )

    requested_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de solicitud",
    )

    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reserved_repair_components",
        verbose_name="Reservado por",
    )

    reserved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de reserva",
    )

    delivered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="delivered_repair_components",
        verbose_name="Entregado por",
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de entrega",
    )

    installed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="installed_repair_components",
        verbose_name="Instalado por",
    )

    installed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de instalación",
    )

    removed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="removed_repair_components",
        verbose_name="Retirado por",
    )

    removed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de retiro",
    )

    returned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="returned_repair_components",
        verbose_name="Retornado por",
    )

    returned_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de retorno",
    )

    unit_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Costo unitario",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    removed_part_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones del componente retirado",
    )

    class Meta:
        verbose_name = "Componente de reparación"
        verbose_name_plural = "Componentes de reparaciones"
        ordering = (
            "component__display_order",
            "component__name",
            "created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "repair",
                    "status",
                ],
                name="repair_comp_status_idx",
            ),
            models.Index(
                fields=[
                    "component",
                    "status",
                ],
                name="repair_comp_item_idx",
            ),
            models.Index(
                fields=[
                    "inventory",
                    "status",
                ],
                name="repair_comp_inv_idx",
            ),
            models.Index(
                fields=[
                    "movement_type",
                    "status",
                ],
                name="repair_comp_move_idx",
            ),
            models.Index(
                fields=[
                    "removed_part_disposition",
                    "status",
                ],
                name="repair_comp_removed_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.repair.code} - "
            f"{self.component}"
        )

    @property
    def total_cost(self):
        if self.unit_cost is None:
            return None

        return self.unit_cost * self.quantity

    def clean(self):
        """
        Normaliza y valida el componente utilizado.
        """

        super().clean()

        self.removed_serial_number = str(
            self.removed_serial_number or ""
        ).strip().upper()

        self.notes = str(
            self.notes or ""
        ).strip()

        self.removed_part_notes = str(
            self.removed_part_notes or ""
        ).strip()

        if not self.repair_id:
            raise ValidationError(
                {
                    "repair": (
                        "La reparación es obligatoria."
                    ),
                }
            )

        if not self.component_id:
            raise ValidationError(
                {
                    "component": (
                        "El componente es obligatorio."
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

        quantity_fields = {
            "reserved_quantity": self.reserved_quantity,
            "delivered_quantity": self.delivered_quantity,
            "installed_quantity": self.installed_quantity,
            "returned_quantity": self.returned_quantity,
            "consumed_quantity": self.consumed_quantity,
        }

        for field_name, value in quantity_fields.items():
            if value < 0:
                raise ValidationError(
                    {
                        field_name: (
                            "La cantidad no puede ser negativa."
                        ),
                    }
                )

            if value > self.quantity:
                raise ValidationError(
                    {
                        field_name: (
                            "La cantidad no puede superar "
                            "la cantidad solicitada."
                        ),
                    }
                )

        if (
            self.installed_quantity
            + self.returned_quantity
            + self.consumed_quantity
            > self.quantity
        ):
            raise ValidationError(
                {
                    "installed_quantity": (
                        "La suma instalada, retornada y consumida "
                        "no puede superar la cantidad solicitada."
                    ),
                }
            )

        if self.inventory_id:
            if self.inventory.component_id != self.component_id:
                raise ValidationError(
                    {
                        "inventory": (
                            "El registro de inventario no corresponde "
                            "al componente seleccionado."
                        ),
                    }
                )

            if not self.inventory.is_active:
                raise ValidationError(
                    {
                        "inventory": (
                            "El registro de inventario está inactivo."
                        ),
                    }
                )

            if (
                self.component.requires_individual_serial
                and self.quantity != Decimal("1")
            ):
                raise ValidationError(
                    {
                        "quantity": (
                            "Un componente controlado por serie debe "
                            "utilizar cantidad igual a uno."
                        ),
                    }
                )

        if (
            self.component.requires_individual_serial
            and self.status
            in [
                self.Status.RESERVED,
                self.Status.DELIVERED,
                self.Status.INSTALLED,
                self.Status.CONSUMED,
            ]
            and not self.inventory_id
        ):
            raise ValidationError(
                {
                    "inventory": (
                        "Debe seleccionar el registro serializado "
                        "del componente."
                    ),
                }
            )

        if self.status == self.Status.REQUESTED:
            if not self.requested_at:
                raise ValidationError(
                    {
                        "requested_at": (
                            "Debe registrar la fecha de solicitud."
                        ),
                    }
                )

        if self.status == self.Status.RESERVED:
            if not self.inventory_id:
                raise ValidationError(
                    {
                        "inventory": (
                            "Debe seleccionar el inventario reservado."
                        ),
                    }
                )

            if not self.reserved_at:
                raise ValidationError(
                    {
                        "reserved_at": (
                            "Debe registrar la fecha de reserva."
                        ),
                    }
                )

            if self.reserved_quantity <= 0:
                raise ValidationError(
                    {
                        "reserved_quantity": (
                            "Debe indicar la cantidad reservada."
                        ),
                    }
                )

        if self.status == self.Status.DELIVERED:
            if not self.delivered_at:
                raise ValidationError(
                    {
                        "delivered_at": (
                            "Debe registrar la fecha de entrega."
                        ),
                    }
                )

            if self.delivered_quantity <= 0:
                raise ValidationError(
                    {
                        "delivered_quantity": (
                            "Debe indicar la cantidad entregada."
                        ),
                    }
                )

        if self.status == self.Status.INSTALLED:
            if not self.installed_at:
                raise ValidationError(
                    {
                        "installed_at": (
                            "Debe registrar la fecha de instalación."
                        ),
                    }
                )

            if self.installed_quantity <= 0:
                raise ValidationError(
                    {
                        "installed_quantity": (
                            "Debe indicar la cantidad instalada."
                        ),
                    }
                )

        if self.status == self.Status.REMOVED:
            if not self.removed_component_id:
                raise ValidationError(
                    {
                        "removed_component": (
                            "Debe indicar el componente retirado."
                        ),
                    }
                )

            if not self.removed_at:
                raise ValidationError(
                    {
                        "removed_at": (
                            "Debe registrar la fecha de retiro."
                        ),
                    }
                )

            if (
                self.removed_part_disposition
                == self.RemovedPartDisposition.NOT_APPLICABLE
            ):
                raise ValidationError(
                    {
                        "removed_part_disposition": (
                            "Debe indicar el destino del componente "
                            "retirado."
                        ),
                    }
                )

        if self.status == self.Status.RETURNED:
            if not self.returned_at:
                raise ValidationError(
                    {
                        "returned_at": (
                            "Debe registrar la fecha de retorno."
                        ),
                    }
                )

            if self.returned_quantity <= 0:
                raise ValidationError(
                    {
                        "returned_quantity": (
                            "Debe indicar la cantidad retornada."
                        ),
                    }
                )

        if self.status == self.Status.CONSUMED:
            if self.consumed_quantity <= 0:
                raise ValidationError(
                    {
                        "consumed_quantity": (
                            "Debe indicar la cantidad consumida."
                        ),
                    }
                )

        if (
            self.component.requires_removed_part_tracking
            and self.status
            in [
                self.Status.INSTALLED,
                self.Status.CONSUMED,
            ]
            and not self.removed_component_id
        ):
            raise ValidationError(
                {
                    "removed_component": (
                        "Este componente requiere registrar "
                        "la pieza retirada."
                    ),
                }
            )

        if self.removed_inventory_id:
            if (
                self.removed_component_id
                and self.removed_inventory.component_id
                != self.removed_component_id
            ):
                raise ValidationError(
                    {
                        "removed_inventory": (
                            "El inventario retirado no corresponde "
                            "al componente indicado."
                        ),
                    }
                )

        if (
            self.removed_part_disposition
            != self.RemovedPartDisposition.NOT_APPLICABLE
            and not self.removed_component_id
        ):
            raise ValidationError(
                {
                    "removed_component": (
                        "Debe indicar el componente retirado."
                    ),
                }
            )

        if self.unit_cost is not None and self.unit_cost < 0:
            raise ValidationError(
                {
                    "unit_cost": (
                        "El costo unitario no puede ser negativo."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        """
        Normaliza y valida el registro.
        """

        self.removed_serial_number = str(
            self.removed_serial_number or ""
        ).strip().upper()

        self.notes = str(
            self.notes or ""
        ).strip()

        self.removed_part_notes = str(
            self.removed_part_notes or ""
        ).strip()

        if (
            self.status == self.Status.REQUESTED
            and not self.requested_at
        ):
            self.requested_at = timezone.now()

        if (
            self.status == self.Status.RESERVED
            and not self.reserved_at
        ):
            self.reserved_at = timezone.now()

        if (
            self.status == self.Status.DELIVERED
            and not self.delivered_at
        ):
            self.delivered_at = timezone.now()

        if (
            self.status == self.Status.INSTALLED
            and not self.installed_at
        ):
            self.installed_at = timezone.now()

        if (
            self.status == self.Status.REMOVED
            and not self.removed_at
        ):
            self.removed_at = timezone.now()

        if (
            self.status == self.Status.RETURNED
            and not self.returned_at
        ):
            self.returned_at = timezone.now()

        if (
            self.inventory_id
            and self.unit_cost is None
        ):
            self.unit_cost = self.inventory.purchase_cost

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )