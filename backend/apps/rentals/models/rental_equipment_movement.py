# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RentalsBaseModel
from .rental_equipment import RentalEquipment
from .rental_warehouse import RentalWarehouse


class RentalEquipmentMovement(RentalsBaseModel):
    """
    Historial de movimientos de una máquina dentro de ANDES.

    Registra:

    - Ingreso inicial.
    - Cambio de almacén.
    - Inicio y finalización de preparación.
    - Disponibilidad para alquiler.
    - Asignación a cliente.
    - Instalación.
    - Alquiler.
    - Retiro.
    - Retorno a almacén.
    - Equipo con problemas.
    - Equipo destinado a partes.
    - Baja o reactivación.

    Este modelo conserva la trazabilidad operativa del equipo
    dentro del proceso de alquiler.

    No reemplaza las órdenes de servicio, instalaciones,
    retiros ni asignaciones a clientes.
    """

    class MovementType(models.TextChoices):
        INITIAL_ENTRY = (
            "initial_entry",
            "Ingreso inicial",
        )
        WAREHOUSE_ENTRY = (
            "warehouse_entry",
            "Ingreso a almacén",
        )
        WAREHOUSE_TRANSFER = (
            "warehouse_transfer",
            "Traslado entre almacenes",
        )
        LOCATION_CHANGE = (
            "location_change",
            "Cambio de ubicación",
        )
        PREPARATION_PENDING = (
            "preparation_pending",
            "Pendiente de preparación",
        )
        PREPARATION_STARTED = (
            "preparation_started",
            "Inicio de preparación",
        )
        PREPARATION_COMPLETED = (
            "preparation_completed",
            "Preparación finalizada",
        )
        READY_FOR_RENTAL = (
            "ready_for_rental",
            "Disponible para alquiler",
        )
        RESERVED = (
            "reserved",
            "Reserva",
        )
        RESERVATION_CANCELLED = (
            "reservation_cancelled",
            "Cancelación de reserva",
        )
        CUSTOMER_ASSIGNED = (
            "customer_assigned",
            "Asignación a cliente",
        )
        INSTALLATION_PENDING = (
            "installation_pending",
            "Pendiente de instalación",
        )
        INSTALLED = (
            "installed",
            "Instalación",
        )
        RENTED = (
            "rented",
            "Inicio de alquiler",
        )
        REMOVAL_PENDING = (
            "removal_pending",
            "Pendiente de retiro",
        )
        REMOVED = (
            "removed",
            "Retiro",
        )
        RETURNED_TO_WAREHOUSE = (
            "returned_to_warehouse",
            "Retorno a almacén",
        )
        PROBLEM_REPORTED = (
            "problem_reported",
            "Problema reportado",
        )
        MARKED_FOR_PARTS = (
            "marked_for_parts",
            "Destinada a partes",
        )
        OUT_OF_SERVICE = (
            "out_of_service",
            "Fuera de servicio",
        )
        REACTIVATED = (
            "reactivated",
            "Reactivación",
        )
        ARCHIVED = (
            "archived",
            "Archivado",
        )
        RESTORED = (
            "restored",
            "Restaurado",
        )
        OTHER = (
            "other",
            "Otro movimiento",
        )

    class ReferenceType(models.TextChoices):
        MANUAL = (
            "manual",
            "Registro manual",
        )
        PURCHASE = (
            "purchase",
            "Compra",
        )
        TRANSFER = (
            "transfer",
            "Transferencia",
        )
        PREPARATION = (
            "preparation",
            "Preparación para alquiler",
        )
        CUSTOMER_ASSIGNMENT = (
            "customer_assignment",
            "Asignación a cliente",
        )
        INSTALLATION = (
            "installation",
            "Instalación",
        )
        SERVICE_ORDER = (
            "service_order",
            "Orden de servicio",
        )
        REMOVAL = (
            "removal",
            "Retiro",
        )
        RETURN = (
            "return",
            "Retorno",
        )
        OTHER = (
            "other",
            "Otro proceso",
        )

    rental_equipment = models.ForeignKey(
        RentalEquipment,
        on_delete=models.PROTECT,
        related_name="movements",
        verbose_name="Equipo de alquiler",
    )

    movement_type = models.CharField(
        max_length=40,
        choices=MovementType.choices,
        db_index=True,
        verbose_name="Tipo de movimiento",
    )

    previous_status = models.CharField(
        max_length=40,
        choices=RentalEquipment.OperationalStatus.choices,
        blank=True,
        db_index=True,
        verbose_name="Estado anterior",
    )

    new_status = models.CharField(
        max_length=40,
        choices=RentalEquipment.OperationalStatus.choices,
        blank=True,
        db_index=True,
        verbose_name="Estado nuevo",
    )

    source_warehouse = models.ForeignKey(
        RentalWarehouse,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="outgoing_equipment_movements",
        verbose_name="Almacén de origen",
    )

    destination_warehouse = models.ForeignKey(
        RentalWarehouse,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="incoming_equipment_movements",
        verbose_name="Almacén de destino",
    )

    source_location = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Ubicación anterior",
    )

    destination_location = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Ubicación nueva",
    )

    reference_type = models.CharField(
        max_length=40,
        choices=ReferenceType.choices,
        default=ReferenceType.MANUAL,
        db_index=True,
        verbose_name="Tipo de referencia",
    )

    reference_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID de referencia",
    )

    reference_number = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Número de referencia",
    )

    document_number = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Número de documento",
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
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha del movimiento",
    )

    class Meta:
        verbose_name = "Movimiento de equipo de alquiler"
        verbose_name_plural = "Movimientos de equipos de alquiler"
        ordering = (
            "-occurred_at",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "rental_equipment",
                    "occurred_at",
                ],
                name="rent_eq_mov_equipment_date_idx",
            ),
            models.Index(
                fields=[
                    "movement_type",
                    "occurred_at",
                ],
                name="rent_eq_mov_type_date_idx",
            ),
            models.Index(
                fields=[
                    "new_status",
                    "occurred_at",
                ],
                name="rent_eq_mov_status_date_idx",
            ),
            models.Index(
                fields=[
                    "reference_type",
                    "reference_id",
                ],
                name="rent_eq_mov_reference_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.rental_equipment} - "
            f"{self.get_movement_type_display()}"
        )

    def clean(self):
        super().clean()

        self.source_location = str(
            self.source_location or ""
        ).strip()

        self.destination_location = str(
            self.destination_location or ""
        ).strip()

        self.reference_number = str(
            self.reference_number or ""
        ).strip()

        self.document_number = str(
            self.document_number or ""
        ).strip()

        self.reason = str(
            self.reason or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        if not self.rental_equipment_id:
            raise ValidationError(
                {
                    "rental_equipment": (
                        "El equipo de alquiler es obligatorio."
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

        if (
            self.previous_status
            and self.new_status
            and self.previous_status == self.new_status
            and self.movement_type
            not in [
                self.MovementType.LOCATION_CHANGE,
                self.MovementType.WAREHOUSE_TRANSFER,
                self.MovementType.OTHER,
            ]
        ):
            raise ValidationError(
                {
                    "new_status": (
                        "El estado nuevo debe ser diferente "
                        "al estado anterior."
                    ),
                }
            )

        if (
            self.movement_type
            == self.MovementType.WAREHOUSE_TRANSFER
        ):
            if not self.destination_warehouse_id:
                raise ValidationError(
                    {
                        "destination_warehouse": (
                            "Debe indicar el almacén de destino."
                        ),
                    }
                )

            if (
                self.source_warehouse_id
                and self.source_warehouse_id
                == self.destination_warehouse_id
            ):
                raise ValidationError(
                    {
                        "destination_warehouse": (
                            "El almacén de destino debe ser "
                            "diferente al almacén de origen."
                        ),
                    }
                )

        warehouse_entry_movements = [
            self.MovementType.INITIAL_ENTRY,
            self.MovementType.WAREHOUSE_ENTRY,
            self.MovementType.RETURNED_TO_WAREHOUSE,
        ]

        if (
            self.movement_type in warehouse_entry_movements
            and not self.destination_warehouse_id
        ):
            raise ValidationError(
                {
                    "destination_warehouse": (
                        "Debe indicar el almacén de destino."
                    ),
                }
            )

        if (
            self.reference_type
            != self.ReferenceType.MANUAL
            and not self.reference_id
            and not self.reference_number
        ):
            raise ValidationError(
                {
                    "reference_id": (
                        "Debe indicar el registro o número "
                        "del proceso relacionado."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        self.source_location = str(
            self.source_location or ""
        ).strip()

        self.destination_location = str(
            self.destination_location or ""
        ).strip()

        self.reference_number = str(
            self.reference_number or ""
        ).strip()

        self.document_number = str(
            self.document_number or ""
        ).strip()

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