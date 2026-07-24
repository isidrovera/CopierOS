# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import EquipmentBaseModel
from .component_inventory import ComponentInventory
from .equipment import Equipment


class EquipmentComponentAssignment(EquipmentBaseModel):
    """
    Historial de componentes instalados en un equipo.

    Permite registrar:

    - Unidades técnicas.
    - Subpartes.
    - Accesorios.
    - Tóners.
    - Repuestos.

    Conserva el contador de instalación y retiro, así como
    el destino del componente retirado.
    """

    class Status(models.TextChoices):
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
            "Devuelto al almacén",
        )
        DISCARDED = (
            "discarded",
            "Desechado",
        )
        CANCELLED = (
            "cancelled",
            "Cancelado",
        )

    class RemovedDisposition(models.TextChoices):
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )
        RETURN_TO_STOCK = (
            "return_to_stock",
            "Retornar al inventario",
        )
        SEND_TO_REPAIR = (
            "send_to_repair",
            "Enviar a reparación",
        )
        RECOVERABLE = (
            "recoverable",
            "Recuperable",
        )
        FOR_PARTS = (
            "for_parts",
            "Para partes",
        )
        DISCARD = (
            "discard",
            "Desechar",
        )
        CUSTOMER_RETURN = (
            "customer_return",
            "Entregar al cliente",
        )

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="component_assignments",
        verbose_name="Equipo",
    )

    inventory = models.ForeignKey(
        ComponentInventory,
        on_delete=models.PROTECT,
        related_name="equipment_assignments",
        verbose_name="Componente de inventario",
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=1,
        verbose_name="Cantidad",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.RESERVED,
        db_index=True,
        verbose_name="Estado",
    )

    position = models.CharField(
        max_length=80,
        blank=True,
        db_index=True,
        verbose_name="Color o posición",
        help_text=(
            "Ejemplo: negro, cyan, magenta, amarillo, "
            "superior, inferior o principal."
        ),
    )

    installed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de instalación",
    )

    installation_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador de instalación",
    )

    removed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de retiro",
    )

    removal_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador de retiro",
    )

    removed_disposition = models.CharField(
        max_length=40,
        choices=RemovedDisposition.choices,
        default=RemovedDisposition.NOT_APPLICABLE,
        db_index=True,
        verbose_name="Destino del componente retirado",
    )

    reference_type = models.CharField(
        max_length=80,
        blank=True,
        db_index=True,
        verbose_name="Tipo de referencia",
        help_text=(
            "Proceso relacionado, por ejemplo reparación, "
            "servicio técnico o entrega."
        ),
    )

    reference_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID de referencia",
    )

    installation_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones de instalación",
    )

    removal_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones de retiro",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activo",
        help_text=(
            "Indica si el componente continúa instalado "
            "o asignado al equipo."
        ),
    )

    class Meta:
        verbose_name = "Componente asignado al equipo"
        verbose_name_plural = "Componentes asignados a equipos"
        ordering = (
            "-installed_at",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "equipment",
                    "is_active",
                ],
                name="equip_comp_assign_active_idx",
            ),
            models.Index(
                fields=[
                    "inventory",
                    "status",
                ],
                name="eq_comp_asg_inv_idx",
            ),
            models.Index(
                fields=[
                    "reference_type",
                    "reference_id",
                ],
                name="equip_comp_assign_ref_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "installed_at",
                ],
                name="equip_comp_assign_status_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.equipment} - "
            f"{self.inventory.component}"
        )

    def clean(self):
        """
        Normaliza y valida la asignación.
        """

        super().clean()

        self.position = str(
            self.position or ""
        ).strip().lower()

        self.reference_type = str(
            self.reference_type or ""
        ).strip().lower()

        self.installation_notes = str(
            self.installation_notes or ""
        ).strip()

        self.removal_notes = str(
            self.removal_notes or ""
        ).strip()

        if not self.equipment_id:
            raise ValidationError(
                {
                    "equipment": (
                        "El equipo es obligatorio."
                    ),
                }
            )

        if not self.inventory_id:
            raise ValidationError(
                {
                    "inventory": (
                        "El componente de inventario es obligatorio."
                    ),
                }
            )

        if self.quantity is None or self.quantity <= 0:
            raise ValidationError(
                {
                    "quantity": (
                        "La cantidad debe ser mayor que cero."
                    ),
                }
            )

        if (
            self.inventory_id
            and self.quantity > self.inventory.quantity
        ):
            raise ValidationError(
                {
                    "quantity": (
                        "La cantidad supera las existencias "
                        "del registro de inventario."
                    ),
                }
            )

        if (
            self.inventory_id
            and self.inventory.serial_number
            and self.quantity != 1
        ):
            raise ValidationError(
                {
                    "quantity": (
                        "Un componente controlado por serie "
                        "debe asignarse con cantidad igual a uno."
                    ),
                }
            )

        if (
            self.status == self.Status.INSTALLED
            and not self.installed_at
        ):
            raise ValidationError(
                {
                    "installed_at": (
                        "Debe registrar la fecha de instalación."
                    ),
                }
            )

        if (
            self.status
            in [
                self.Status.REMOVED,
                self.Status.RETURNED,
                self.Status.DISCARDED,
            ]
            and not self.removed_at
        ):
            raise ValidationError(
                {
                    "removed_at": (
                        "Debe registrar la fecha de retiro."
                    ),
                }
            )

        if (
            self.removed_at
            and self.installed_at
            and self.removed_at < self.installed_at
        ):
            raise ValidationError(
                {
                    "removed_at": (
                        "La fecha de retiro no puede ser anterior "
                        "a la fecha de instalación."
                    ),
                }
            )

        if (
            self.removal_meter is not None
            and self.installation_meter is not None
            and self.removal_meter < self.installation_meter
        ):
            raise ValidationError(
                {
                    "removal_meter": (
                        "El contador de retiro no puede ser menor "
                        "que el contador de instalación."
                    ),
                }
            )

        if (
            self.removed_at
            and self.removed_disposition
            == self.RemovedDisposition.NOT_APPLICABLE
        ):
            raise ValidationError(
                {
                    "removed_disposition": (
                        "Debe indicar el destino del componente retirado."
                    ),
                }
            )

        if (
            not self.removed_at
            and self.removed_disposition
            != self.RemovedDisposition.NOT_APPLICABLE
        ):
            raise ValidationError(
                {
                    "removed_disposition": (
                        "No puede indicar un destino si el componente "
                        "todavía no fue retirado."
                    ),
                }
            )

        if self.reference_id and not self.reference_type:
            raise ValidationError(
                {
                    "reference_type": (
                        "Debe indicar el tipo de referencia."
                    ),
                }
            )

        if self.reference_type and not self.reference_id:
            raise ValidationError(
                {
                    "reference_id": (
                        "Debe indicar el ID de referencia."
                    ),
                }
            )

        if self.status == self.Status.INSTALLED:
            duplicate_active = (
                EquipmentComponentAssignment.objects.filter(
                    equipment_id=self.equipment_id,
                    inventory_id=self.inventory_id,
                    status=self.Status.INSTALLED,
                    is_active=True,
                )
                .exclude(pk=self.pk)
            )

            if duplicate_active.exists():
                raise ValidationError(
                    {
                        "inventory": (
                            "Este componente ya figura instalado "
                            "en el equipo."
                        ),
                    }
                )

    def save(self, *args, **kwargs):
        """
        Normaliza y valida antes de guardar.
        """

        self.position = str(
            self.position or ""
        ).strip().lower()

        self.reference_type = str(
            self.reference_type or ""
        ).strip().lower()

        self.installation_notes = str(
            self.installation_notes or ""
        ).strip()

        self.removal_notes = str(
            self.removal_notes or ""
        ).strip()

        if (
            self.status == self.Status.INSTALLED
            and not self.installed_at
        ):
            self.installed_at = timezone.now()

        if self.status in [
            self.Status.REMOVED,
            self.Status.RETURNED,
            self.Status.DISCARDED,
            self.Status.CANCELLED,
        ]:
            self.is_active = False

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )