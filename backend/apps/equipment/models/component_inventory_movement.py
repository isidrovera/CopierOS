# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from .base import EquipmentBaseModel
from .component_inventory import ComponentInventory


class ComponentInventoryMovement(EquipmentBaseModel):
    """
    Historial de movimientos del inventario de componentes.

    Registra:

    - Ingresos.
    - Reservas.
    - Liberación de reservas.
    - Entregas.
    - Instalaciones.
    - Retornos.
    - Ajustes.
    - Traslados.
    - Desechos.

    Posteriormente podrá relacionarse con una reparación,
    un equipo, un técnico o un documento de almacén.
    """

    class MovementType(models.TextChoices):
        ENTRY = (
            "entry",
            "Ingreso",
        )
        RESERVATION = (
            "reservation",
            "Reserva",
        )
        RESERVATION_RELEASE = (
            "reservation_release",
            "Liberación de reserva",
        )
        DELIVERY = (
            "delivery",
            "Entrega",
        )
        INSTALLATION = (
            "installation",
            "Instalación",
        )
        RETURN = (
            "return",
            "Retorno",
        )
        ADJUSTMENT_IN = (
            "adjustment_in",
            "Ajuste de entrada",
        )
        ADJUSTMENT_OUT = (
            "adjustment_out",
            "Ajuste de salida",
        )
        TRANSFER = (
            "transfer",
            "Traslado",
        )
        DISCARD = (
            "discard",
            "Desecho",
        )

    inventory = models.ForeignKey(
        ComponentInventory,
        on_delete=models.PROTECT,
        related_name="movements",
        verbose_name="Registro de inventario",
    )

    movement_type = models.CharField(
        max_length=40,
        choices=MovementType.choices,
        db_index=True,
        verbose_name="Tipo de movimiento",
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Cantidad",
    )

    quantity_before = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad anterior",
    )

    quantity_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad posterior",
    )

    reserved_before = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad reservada anterior",
    )

    reserved_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad reservada posterior",
    )

    source_warehouse = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Almacén de origen",
    )

    source_location = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Ubicación de origen",
    )

    destination_warehouse = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Almacén de destino",
    )

    destination_location = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Ubicación de destino",
    )

    reference_type = models.CharField(
        max_length=80,
        blank=True,
        db_index=True,
        verbose_name="Tipo de referencia",
        help_text=(
            "Tipo de documento o proceso relacionado. "
            "Ejemplo: reparación, compra, ajuste o traslado."
        ),
    )

    reference_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID de referencia",
        help_text=(
            "Identificador del registro relacionado con el movimiento."
        ),
    )

    document_number = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Número de documento",
    )

    meter_value = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador del equipo",
        help_text=(
            "Contador registrado cuando el componente fue "
            "instalado o retirado."
        ),
    )

    reason = models.TextField(
        blank=True,
        verbose_name="Motivo",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    occurred_at = models.DateTimeField(
        db_index=True,
        verbose_name="Fecha del movimiento",
    )

    class Meta:
        verbose_name = "Movimiento de inventario de componente"
        verbose_name_plural = "Movimientos de inventario de componentes"
        ordering = (
            "-occurred_at",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "inventory",
                    "occurred_at",
                ],
                name="equip_inv_mov_item_date_idx",
            ),
            models.Index(
                fields=[
                    "movement_type",
                    "occurred_at",
                ],
                name="equip_inv_mov_type_date_idx",
            ),
            models.Index(
                fields=[
                    "reference_type",
                    "reference_id",
                ],
                name="equip_inv_mov_reference_idx",
            ),
            models.Index(
                fields=[
                    "document_number",
                ],
                name="equip_inv_mov_document_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_movement_type_display()} - "
            f"{self.inventory} - {self.quantity}"
        )

    def clean(self):
        """
        Normaliza y valida el movimiento.
        """

        super().clean()

        self.source_warehouse = str(
            self.source_warehouse or ""
        ).strip()

        self.source_location = str(
            self.source_location or ""
        ).strip()

        self.destination_warehouse = str(
            self.destination_warehouse or ""
        ).strip()

        self.destination_location = str(
            self.destination_location or ""
        ).strip()

        self.reference_type = str(
            self.reference_type or ""
        ).strip().lower()

        self.document_number = str(
            self.document_number or ""
        ).strip().upper()

        self.reason = str(
            self.reason or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        if not self.inventory_id:
            raise ValidationError(
                {
                    "inventory": (
                        "El registro de inventario es obligatorio."
                    ),
                }
            )

        if not self.movement_type:
            raise ValidationError(
                {
                    "movement_type": (
                        "El tipo de movimiento es obligatorio."
                    ),
                }
            )

        if self.quantity is None or self.quantity <= Decimal("0"):
            raise ValidationError(
                {
                    "quantity": (
                        "La cantidad del movimiento debe ser "
                        "mayor que cero."
                    ),
                }
            )

        if self.quantity_before < Decimal("0"):
            raise ValidationError(
                {
                    "quantity_before": (
                        "La cantidad anterior no puede ser negativa."
                    ),
                }
            )

        if self.quantity_after < Decimal("0"):
            raise ValidationError(
                {
                    "quantity_after": (
                        "La cantidad posterior no puede ser negativa."
                    ),
                }
            )

        if self.reserved_before < Decimal("0"):
            raise ValidationError(
                {
                    "reserved_before": (
                        "La cantidad reservada anterior no puede "
                        "ser negativa."
                    ),
                }
            )

        if self.reserved_after < Decimal("0"):
            raise ValidationError(
                {
                    "reserved_after": (
                        "La cantidad reservada posterior no puede "
                        "ser negativa."
                    ),
                }
            )

        if self.reserved_after > self.quantity_after:
            raise ValidationError(
                {
                    "reserved_after": (
                        "La cantidad reservada posterior no puede "
                        "superar la cantidad posterior."
                    ),
                }
            )

        if (
            self.movement_type == self.MovementType.TRANSFER
            and not self.destination_warehouse
        ):
            raise ValidationError(
                {
                    "destination_warehouse": (
                        "Debe indicar el almacén de destino "
                        "para realizar un traslado."
                    ),
                }
            )

        if (
            self.reference_id
            and not self.reference_type
        ):
            raise ValidationError(
                {
                    "reference_type": (
                        "Debe indicar el tipo de referencia cuando "
                        "se registra un ID relacionado."
                    ),
                }
            )

        if (
            self.reference_type
            and not self.reference_id
        ):
            raise ValidationError(
                {
                    "reference_id": (
                        "Debe indicar el ID relacionado cuando "
                        "se registra un tipo de referencia."
                    ),
                }
            )

        if (
            self.movement_type
            in [
                self.MovementType.INSTALLATION,
                self.MovementType.DELIVERY,
                self.MovementType.DISCARD,
                self.MovementType.ADJUSTMENT_OUT,
            ]
            and self.quantity_after >= self.quantity_before
        ):
            raise ValidationError(
                {
                    "quantity_after": (
                        "Este tipo de movimiento debe reducir "
                        "la cantidad existente."
                    ),
                }
            )

        if (
            self.movement_type
            in [
                self.MovementType.ENTRY,
                self.MovementType.RETURN,
                self.MovementType.ADJUSTMENT_IN,
            ]
            and self.quantity_after <= self.quantity_before
        ):
            raise ValidationError(
                {
                    "quantity_after": (
                        "Este tipo de movimiento debe aumentar "
                        "la cantidad existente."
                    ),
                }
            )

        if (
            self.movement_type
            == self.MovementType.RESERVATION
            and self.reserved_after <= self.reserved_before
        ):
            raise ValidationError(
                {
                    "reserved_after": (
                        "Una reserva debe aumentar la cantidad "
                        "reservada."
                    ),
                }
            )

        if (
            self.movement_type
            == self.MovementType.RESERVATION_RELEASE
            and self.reserved_after >= self.reserved_before
        ):
            raise ValidationError(
                {
                    "reserved_after": (
                        "La liberación debe reducir la cantidad "
                        "reservada."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        """
        Normaliza y valida antes de guardar.
        """

        self.source_warehouse = str(
            self.source_warehouse or ""
        ).strip()

        self.source_location = str(
            self.source_location or ""
        ).strip()

        self.destination_warehouse = str(
            self.destination_warehouse or ""
        ).strip()

        self.destination_location = str(
            self.destination_location or ""
        ).strip()

        self.reference_type = str(
            self.reference_type or ""
        ).strip().lower()

        self.document_number = str(
            self.document_number or ""
        ).strip().upper()

        self.reason = str(
            self.reason or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )