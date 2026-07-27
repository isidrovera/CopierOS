# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.equipment.models import Equipment

from .base import RentalsBaseModel
from .rental_warehouse import RentalWarehouse


class RentalEquipment(RentalsBaseModel):
    """
    Representa una máquina administrada por ANDES para alquiler
    o para servicios técnicos.

    El equipo físico principal continúa registrado en Equipment.

    Este modelo agrega la información operativa correspondiente
    a ANDES:

    - Procedencia del equipo.
    - Estado dentro del almacén de alquiler.
    - Estado de preparación.
    - Disponibilidad para alquiler.
    - Almacén y ubicación actual.
    - Fecha de ingreso a ANDES.
    - Equipo propio o propiedad de cliente externo.
    """

    class EquipmentPurpose(models.TextChoices):
        RENTAL = (
            "rental",
            "Equipo para alquiler",
        )
        CUSTOMER_SERVICE = (
            "customer_service",
            "Equipo de cliente para servicios",
        )

    class AcquisitionSource(models.TextChoices):
        CORAPSAC = (
            "corapsac",
            "Compra a CORAPSAC",
        )
        EXTERNAL_SUPPLIER = (
            "external_supplier",
            "Compra a proveedor externo",
        )
        CUSTOMER_OWNED = (
            "customer_owned",
            "Propiedad de cliente",
        )
        INTERNAL_TRANSFER = (
            "internal_transfer",
            "Transferencia interna",
        )
        OTHER = (
            "other",
            "Otra procedencia",
        )

    class OperationalStatus(models.TextChoices):
        RECEIVED = (
            "received",
            "Ingresada",
        )
        IN_WAREHOUSE = (
            "in_warehouse",
            "En almacén",
        )
        PENDING_PREPARATION = (
            "pending_preparation",
            "Pendiente de preparación",
        )
        IN_PREPARATION = (
            "in_preparation",
            "En preparación",
        )
        READY_FOR_RENTAL = (
            "ready_for_rental",
            "Lista para alquiler",
        )
        RESERVED = (
            "reserved",
            "Reservada",
        )
        ASSIGNED = (
            "assigned",
            "Asignada",
        )
        INSTALLATION_PENDING = (
            "installation_pending",
            "Pendiente de instalación",
        )
        INSTALLED = (
            "installed",
            "Instalada",
        )
        RENTED = (
            "rented",
            "Alquilada",
        )
        REMOVAL_PENDING = (
            "removal_pending",
            "Pendiente de retiro",
        )
        REMOVED = (
            "removed",
            "Retirada",
        )
        RETURNED_TO_WAREHOUSE = (
            "returned_to_warehouse",
            "Retornada a almacén",
        )
        WITH_PROBLEMS = (
            "with_problems",
            "Con problemas",
        )
        FOR_PARTS = (
            "for_parts",
            "Para partes",
        )
        OUT_OF_SERVICE = (
            "out_of_service",
            "Fuera de servicio",
        )

    equipment = models.OneToOneField(
        Equipment,
        on_delete=models.PROTECT,
        related_name="rental_profile",
        verbose_name="Equipo",
    )

    purpose = models.CharField(
        max_length=30,
        choices=EquipmentPurpose.choices,
        default=EquipmentPurpose.RENTAL,
        db_index=True,
        verbose_name="Finalidad",
    )

    acquisition_source = models.CharField(
        max_length=30,
        choices=AcquisitionSource.choices,
        db_index=True,
        verbose_name="Procedencia",
    )

    supplier = models.ForeignKey(
        "partners.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rental_equipment_supplied",
        verbose_name="Proveedor",
    )

    owner_customer = models.ForeignKey(
        "partners.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="owned_service_equipment",
        verbose_name="Cliente propietario",
        help_text=(
            "Se utiliza cuando el equipo pertenece a un cliente "
            "externo y solo está registrado para servicios técnicos."
        ),
    )

    warehouse = models.ForeignKey(
        RentalWarehouse,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="equipment",
        verbose_name="Almacén actual",
    )

    warehouse_location = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Ubicación dentro del almacén",
    )

    operational_status = models.CharField(
        max_length=40,
        choices=OperationalStatus.choices,
        default=OperationalStatus.RECEIVED,
        db_index=True,
        verbose_name="Estado operativo",
    )

    entry_date = models.DateField(
        default=timezone.localdate,
        db_index=True,
        verbose_name="Fecha de ingreso",
    )

    acquisition_document = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Documento de adquisición",
    )

    acquisition_reference = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Referencia de adquisición",
    )

    is_available_for_rental = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Disponible para alquiler",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Equipo de alquiler"
        verbose_name_plural = "Equipos de alquiler"
        ordering = (
            "-entry_date",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "purpose",
                    "operational_status",
                ],
                name="rent_equip_purpose_status_idx",
            ),
            models.Index(
                fields=[
                    "warehouse",
                    "operational_status",
                ],
                name="rent_eq_warehouse_st_idx",
            ),
            models.Index(
                fields=[
                    "is_available_for_rental",
                    "operational_status",
                ],
                name="rent_equip_available_idx",
            ),
        ]

    def __str__(self):
        return str(self.equipment)

    def clean(self):
        super().clean()

        self.warehouse_location = str(
            self.warehouse_location or ""
        ).strip()

        self.acquisition_document = str(
            self.acquisition_document or ""
        ).strip()

        self.acquisition_reference = str(
            self.acquisition_reference or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        if not self.equipment_id:
            raise ValidationError(
                {
                    "equipment": "El equipo es obligatorio.",
                }
            )

        if (
            self.purpose
            == self.EquipmentPurpose.CUSTOMER_SERVICE
            and not self.owner_customer_id
        ):
            raise ValidationError(
                {
                    "owner_customer": (
                        "Debe indicar el cliente propietario "
                        "del equipo."
                    ),
                }
            )

        if (
            self.purpose
            == self.EquipmentPurpose.RENTAL
            and self.owner_customer_id
        ):
            raise ValidationError(
                {
                    "owner_customer": (
                        "Un equipo propio para alquiler no debe "
                        "tener cliente propietario."
                    ),
                }
            )

        if (
            self.acquisition_source
            == self.AcquisitionSource.CUSTOMER_OWNED
            and not self.owner_customer_id
        ):
            raise ValidationError(
                {
                    "owner_customer": (
                        "Debe indicar el propietario del equipo."
                    ),
                }
            )

        if (
            self.acquisition_source
            in [
                self.AcquisitionSource.CORAPSAC,
                self.AcquisitionSource.EXTERNAL_SUPPLIER,
            ]
            and not self.supplier_id
        ):
            raise ValidationError(
                {
                    "supplier": (
                        "Debe indicar el proveedor del equipo."
                    ),
                }
            )

        rental_only_statuses = [
            self.OperationalStatus.READY_FOR_RENTAL,
            self.OperationalStatus.RESERVED,
            self.OperationalStatus.ASSIGNED,
            self.OperationalStatus.INSTALLATION_PENDING,
            self.OperationalStatus.INSTALLED,
            self.OperationalStatus.RENTED,
            self.OperationalStatus.REMOVAL_PENDING,
            self.OperationalStatus.REMOVED,
            self.OperationalStatus.RETURNED_TO_WAREHOUSE,
        ]

        if (
            self.purpose
            == self.EquipmentPurpose.CUSTOMER_SERVICE
            and self.operational_status in rental_only_statuses
        ):
            raise ValidationError(
                {
                    "operational_status": (
                        "Los equipos de clientes externos no pueden "
                        "usar estados del proceso de alquiler."
                    ),
                }
            )

        if self.is_available_for_rental:
            if self.purpose != self.EquipmentPurpose.RENTAL:
                raise ValidationError(
                    {
                        "is_available_for_rental": (
                            "Solo los equipos propios para alquiler "
                            "pueden estar disponibles."
                        ),
                    }
                )

            if (
                self.operational_status
                != self.OperationalStatus.READY_FOR_RENTAL
            ):
                raise ValidationError(
                    {
                        "is_available_for_rental": (
                            "El equipo debe estar en estado "
                            "'Lista para alquiler'."
                        ),
                    }
                )

        unavailable_statuses = [
            self.OperationalStatus.RENTED,
            self.OperationalStatus.WITH_PROBLEMS,
            self.OperationalStatus.FOR_PARTS,
            self.OperationalStatus.OUT_OF_SERVICE,
            self.OperationalStatus.REMOVAL_PENDING,
        ]

        if self.operational_status in unavailable_statuses:
            self.is_available_for_rental = False

        warehouse_required_statuses = [
            self.OperationalStatus.RECEIVED,
            self.OperationalStatus.IN_WAREHOUSE,
            self.OperationalStatus.PENDING_PREPARATION,
            self.OperationalStatus.IN_PREPARATION,
            self.OperationalStatus.READY_FOR_RENTAL,
            self.OperationalStatus.RETURNED_TO_WAREHOUSE,
            self.OperationalStatus.WITH_PROBLEMS,
            self.OperationalStatus.FOR_PARTS,
        ]

        if (
            self.purpose == self.EquipmentPurpose.RENTAL
            and self.operational_status in warehouse_required_statuses
            and not self.warehouse_id
        ):
            raise ValidationError(
                {
                    "warehouse": (
                        "Debe indicar el almacén actual del equipo."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        self.warehouse_location = str(
            self.warehouse_location or ""
        ).strip()

        self.acquisition_document = str(
            self.acquisition_document or ""
        ).strip()

        self.acquisition_reference = str(
            self.acquisition_reference or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )