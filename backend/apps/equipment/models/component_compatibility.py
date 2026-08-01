# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models

from .base import EquipmentBaseModel
from .component import EquipmentComponent
from .equipment_family import EquipmentFamily
from .equipment_model import EquipmentModel


class ComponentCompatibility(EquipmentBaseModel):
    """
    Define la compatibilidad técnica de un componente.

    La compatibilidad puede establecerse:

    - Para todos los modelos de una familia.
    - Para un modelo específico.
    - Para una posición o color determinado.

    Este modelo es únicamente descriptivo.

    No controla:

    - Stock.
    - Cantidades.
    - Precios.
    - Costos.
    - Almacenes.
    - Reservas.
    """

    component = models.ForeignKey(
        EquipmentComponent,
        on_delete=models.PROTECT,
        related_name="compatibilities",
        verbose_name="Componente",
    )

    equipment_family = models.ForeignKey(
        EquipmentFamily,
        on_delete=models.PROTECT,
        related_name="component_compatibilities",
        verbose_name="Familia de equipos",
        help_text=(
            "Familia para la cual el componente es compatible."
        ),
    )

    equipment_model = models.ForeignKey(
        EquipmentModel,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="component_compatibilities",
        verbose_name="Modelo específico",
        help_text=(
            "Solo debe seleccionarse cuando la compatibilidad "
            "aplica a un modelo específico dentro de la familia."
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

    manufacturer_code_override = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Código específico para esta compatibilidad",
        help_text=(
            "Código de fabricante utilizado específicamente "
            "para esta familia o modelo cuando sea diferente "
            "al código general del componente."
        ),
    )

    expected_life_meter_override = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración específica por contador",
        help_text=(
            "Duración estimada específica para esta familia "
            "o modelo. Si queda vacío se utiliza la duración "
            "general del componente."
        ),
    )

    expected_life_days_override = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración específica en días",
        help_text=(
            "Duración estimada específica para esta familia "
            "o modelo. Si queda vacío se utiliza la duración "
            "general del componente."
        ),
    )

    technical_notes = models.TextField(
        blank=True,
        verbose_name="Notas técnicas",
        help_text=(
            "Observaciones, restricciones o diferencias "
            "de instalación para esta familia o modelo."
        ),
    )

    is_required = models.BooleanField(
        default=False,
        verbose_name="Componente habitual u obligatorio",
        help_text=(
            "Indica si normalmente el equipo utiliza "
            "este componente."
        ),
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activa",
        help_text=(
            "Las compatibilidades inactivas no deben utilizarse "
            "en nuevos registros, pero se conservan en el historial."
        ),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Orden de visualización",
    )

    class Meta:
        verbose_name = "Compatibilidad de componente"
        verbose_name_plural = "Compatibilidades de componentes"

        ordering = (
            "equipment_family__brand__name",
            "equipment_family__name",
            "display_order",
            "component__name",
        )

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "component",
                    "equipment_family",
                    "equipment_model",
                    "position",
                ],
                name="unique_component_family_model_position",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "equipment_family",
                    "is_active",
                ],
                name="comp_compat_family_active_idx",
            ),
            models.Index(
                fields=[
                    "equipment_model",
                    "is_active",
                ],
                name="comp_compat_model_active_idx",
            ),
            models.Index(
                fields=[
                    "component",
                    "is_active",
                ],
                name="comp_compat_component_idx",
            ),
            models.Index(
                fields=[
                    "position",
                    "is_active",
                ],
                name="comp_compat_position_idx",
            ),
        ]

    def __str__(self):
        compatibility_name = (
            f"{self.component} - "
            f"{self.equipment_family}"
        )

        if self.equipment_model_id:
            compatibility_name = (
                f"{compatibility_name} - "
                f"{self.equipment_model.name}"
            )

        if self.position:
            compatibility_name = (
                f"{compatibility_name} - "
                f"{self.position}"
            )

        return compatibility_name

    @property
    def effective_manufacturer_code(self):
        """
        Devuelve el código específico de la compatibilidad.

        Si no existe, utiliza el código general del componente.
        """

        return (
            self.manufacturer_code_override
            or self.component.manufacturer_code
        )

    @property
    def effective_expected_life_meter(self):
        """
        Devuelve la duración por contador aplicable.
        """

        if self.expected_life_meter_override is not None:
            return self.expected_life_meter_override

        return self.component.expected_life_meter

    @property
    def effective_expected_life_days(self):
        """
        Devuelve la duración en días aplicable.
        """

        if self.expected_life_days_override is not None:
            return self.expected_life_days_override

        return self.component.expected_life_days

    def clean(self):
        """
        Normaliza y valida la compatibilidad.
        """

        super().clean()

        self.position = str(
            self.position or ""
        ).strip().lower()

        self.manufacturer_code_override = str(
            self.manufacturer_code_override or ""
        ).strip().upper()

        self.technical_notes = str(
            self.technical_notes or ""
        ).strip()

        if not self.component_id:
            raise ValidationError(
                {
                    "component": (
                        "El componente es obligatorio."
                    ),
                }
            )

        if not self.equipment_family_id:
            raise ValidationError(
                {
                    "equipment_family": (
                        "La familia de equipos es obligatoria."
                    ),
                }
            )

        if self.equipment_model_id:
            if not self.equipment_model.equipment_family_id:
                raise ValidationError(
                    {
                        "equipment_model": (
                            "El modelo seleccionado no tiene "
                            "una familia de equipos asignada."
                        ),
                    }
                )

            if (
                self.equipment_model.equipment_family_id
                != self.equipment_family_id
            ):
                raise ValidationError(
                    {
                        "equipment_model": (
                            "El modelo seleccionado no pertenece "
                            "a la familia indicada."
                        ),
                    }
                )

        if (
            self.component_id
            and self.component.color
            != EquipmentComponent.Color.NOT_APPLICABLE
            and not self.position
        ):
            self.position = self.component.color

        duplicate_compatibility = (
            ComponentCompatibility.objects.filter(
                component_id=self.component_id,
                equipment_family_id=self.equipment_family_id,
                equipment_model_id=self.equipment_model_id,
                position__iexact=self.position,
            )
            .exclude(pk=self.pk)
        )

        if duplicate_compatibility.exists():
            raise ValidationError(
                {
                    "component": (
                        "Esta compatibilidad ya se encuentra "
                        "registrada para la familia, modelo "
                        "y posición seleccionados."
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

        self.manufacturer_code_override = str(
            self.manufacturer_code_override or ""
        ).strip().upper()

        self.technical_notes = str(
            self.technical_notes or ""
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
        """
        Archiva la compatibilidad.
        """

        self.is_active = False

        if save:
            self.save(
                update_fields=[
                    "is_active",
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
        """
        Restaura la compatibilidad.
        """

        self.is_active = True

        if save:
            self.save(
                update_fields=[
                    "is_active",
                    "updated_at",
                ]
            )

        return super().restore(
            user=user,
            save=save,
        )