# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import EquipmentBaseModel
from .component import EquipmentComponent
from .equipment import Equipment


class EquipmentComponentAssignment(EquipmentBaseModel):
    """
    Historial descriptivo de componentes instalados en un equipo.

    Permite registrar:

    - Unidades técnicas completas.
    - Subpartes reemplazadas.
    - Repuestos.
    - Accesorios.
    - Tóners.
    - Consumibles.

    Este modelo no controla stock, almacenes, costos, precios
    ni movimientos de inventario.

    Conserva:

    - Componente instalado.
    - Serie individual cuando corresponda.
    - Posición o color.
    - Fecha y contador de instalación.
    - Fecha y contador de retiro.
    - Destino del componente retirado.
    - Reparación, servicio o proceso relacionado.
    """

    class Status(models.TextChoices):
        INSTALLED = (
            "installed",
            "Instalado",
        )
        REMOVED = (
            "removed",
            "Retirado",
        )
        SENT_TO_REPAIR = (
            "sent_to_repair",
            "Enviado a reparación",
        )
        REPAIRED = (
            "repaired",
            "Reparado",
        )
        RECOVERABLE = (
            "recoverable",
            "Recuperable",
        )
        FOR_PARTS = (
            "for_parts",
            "Para partes",
        )
        DISCARDED = (
            "discarded",
            "Desechado",
        )
        RETURNED_TO_CUSTOMER = (
            "returned_to_customer",
            "Entregado al cliente",
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
        KEEP_FOR_REUSE = (
            "keep_for_reuse",
            "Conservar para reutilización",
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
            "Utilizar para partes",
        )
        DISCARD = (
            "discard",
            "Desechar",
        )
        CUSTOMER_RETURN = (
            "customer_return",
            "Entregar al cliente",
        )
        OTHER = (
            "other",
            "Otro destino",
        )

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="component_assignments",
        verbose_name="Equipo",
    )

    component = models.ForeignKey(
        EquipmentComponent,
        on_delete=models.PROTECT,
        related_name="equipment_assignments",
        verbose_name="Componente",
        help_text=(
            "Unidad, subparte, repuesto, accesorio, tóner "
            "o consumible relacionado con el equipo."
        ),
    )

    serial_number = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Número de serie del componente",
        help_text=(
            "Serie individual del accesorio o unidad física "
            "cuando el fabricante la proporciona."
        ),
    )

    position = models.CharField(
        max_length=80,
        blank=True,
        db_index=True,
        verbose_name="Color o posición",
        help_text=(
            "Ejemplo: black, cyan, magenta, yellow, "
            "superior, inferior, principal o bandeja 1."
        ),
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.INSTALLED,
        db_index=True,
        verbose_name="Estado",
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
        help_text=(
            "Contador del equipo cuando se instaló "
            "el componente."
        ),
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
        help_text=(
            "Contador del equipo cuando se retiró "
            "el componente."
        ),
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
            "Proceso relacionado. Ejemplo: reparación, "
            "servicio técnico, instalación o retiro."
        ),
    )

    reference_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID de referencia",
        help_text=(
            "Identificador de la reparación, servicio "
            "u otro proceso relacionado."
        ),
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
        verbose_name="Continúa instalado",
        help_text=(
            "Indica si el componente continúa instalado "
            "actualmente en el equipo."
        ),
    )

    class Meta:
        verbose_name = "Componente asignado al equipo"
        verbose_name_plural = "Componentes asignados a equipos"

        ordering = (
            "-installed_at",
            "-created_at",
        )

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "equipment",
                    "component",
                    "position",
                ],
                condition=models.Q(
                    is_active=True,
                    status="installed",
                ),
                name="unique_active_component_position",
            ),
            models.UniqueConstraint(
                fields=[
                    "component",
                    "serial_number",
                ],
                condition=~models.Q(
                    serial_number="",
                ),
                name="unique_assigned_component_serial",
            ),
        ]

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
                    "component",
                    "status",
                ],
                name="eq_comp_asg_component_idx",
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
            models.Index(
                fields=[
                    "serial_number",
                ],
                name="equip_comp_asg_serial_idx",
            ),
        ]

    def __str__(self):
        assignment_name = (
            f"{self.equipment} - "
            f"{self.component}"
        )

        if self.position:
            assignment_name = (
                f"{assignment_name} - "
                f"{self.position}"
            )

        if self.serial_number:
            assignment_name = (
                f"{assignment_name} "
                f"[{self.serial_number}]"
            )

        return assignment_name

    def clean(self):
        """
        Normaliza y valida la asignación del componente.
        """

        super().clean()

        self.serial_number = str(
            self.serial_number or ""
        ).strip().upper()

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

        if not self.component_id:
            raise ValidationError(
                {
                    "component": (
                        "El componente es obligatorio."
                    ),
                }
            )

        if (
            self.component_id
            and self.component.requires_individual_serial
            and not self.serial_number
        ):
            raise ValidationError(
                {
                    "serial_number": (
                        "Este componente requiere registrar "
                        "un número de serie individual."
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

        removed_statuses = [
            self.Status.REMOVED,
            self.Status.SENT_TO_REPAIR,
            self.Status.REPAIRED,
            self.Status.RECOVERABLE,
            self.Status.FOR_PARTS,
            self.Status.DISCARDED,
            self.Status.RETURNED_TO_CUSTOMER,
        ]

        if (
            self.status in removed_statuses
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
            and not self.installed_at
        ):
            raise ValidationError(
                {
                    "installed_at": (
                        "Debe registrar la fecha de instalación "
                        "antes de registrar el retiro."
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
                        "Debe indicar el destino del componente "
                        "retirado."
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
                        "No puede indicar un destino mientras "
                        "el componente continúe instalado."
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
                        "Debe indicar el ID del registro relacionado."
                    ),
                }
            )

        if (
            self.status == self.Status.INSTALLED
            and not self.is_active
        ):
            raise ValidationError(
                {
                    "is_active": (
                        "Un componente instalado debe permanecer activo."
                    ),
                }
            )

        if (
            self.status != self.Status.INSTALLED
            and self.is_active
        ):
            raise ValidationError(
                {
                    "is_active": (
                        "Solo un componente instalado puede permanecer "
                        "marcado como activo."
                    ),
                }
            )

        if (
            self.status == self.Status.INSTALLED
            and self.equipment_id
            and self.component_id
        ):
            duplicate_active = (
                EquipmentComponentAssignment.objects.filter(
                    equipment_id=self.equipment_id,
                    component_id=self.component_id,
                    position__iexact=self.position,
                    status=self.Status.INSTALLED,
                    is_active=True,
                )
                .exclude(pk=self.pk)
            )

            if duplicate_active.exists():
                raise ValidationError(
                    {
                        "component": (
                            "Este componente ya figura instalado "
                            "en la misma posición del equipo."
                        ),
                    }
                )

        if self.component_id and self.serial_number:
            duplicate_serial = (
                EquipmentComponentAssignment.objects.filter(
                    component_id=self.component_id,
                    serial_number__iexact=self.serial_number,
                )
                .exclude(pk=self.pk)
            )

            if duplicate_serial.exists():
                raise ValidationError(
                    {
                        "serial_number": (
                            "Esta serie ya fue registrada para "
                            "el componente seleccionado."
                        ),
                    }
                )

    def save(self, *args, **kwargs):
        """
        Normaliza y valida antes de guardar.
        """

        self.serial_number = str(
            self.serial_number or ""
        ).strip().upper()

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

        if self.status == self.Status.INSTALLED:
            self.is_active = True
            self.removed_at = None
            self.removal_meter = None
            self.removed_disposition = (
                self.RemovedDisposition.NOT_APPLICABLE
            )

        if self.status in [
            self.Status.REMOVED,
            self.Status.SENT_TO_REPAIR,
            self.Status.REPAIRED,
            self.Status.RECOVERABLE,
            self.Status.FOR_PARTS,
            self.Status.DISCARDED,
            self.Status.RETURNED_TO_CUSTOMER,
            self.Status.CANCELLED,
        ]:
            self.is_active = False

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )

    def remove(
        self,
        disposition,
        removal_meter=None,
        notes="",
        removed_at=None,
        save=True,
    ):
        """
        Marca el componente como retirado del equipo.
        """

        self.status = self.Status.REMOVED
        self.is_active = False
        self.removed_at = removed_at or timezone.now()
        self.removal_meter = removal_meter
        self.removed_disposition = disposition
        self.removal_notes = str(
            notes or ""
        ).strip()

        if save:
            self.save()

        return self