# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models

from .base import EquipmentBaseModel
from .component import EquipmentComponent
from .equipment_family import EquipmentFamily
from .equipment_model import EquipmentModel


class ComponentCompatibility(EquipmentBaseModel):
    """
    Define la compatibilidad de un componente con una familia
    o con un modelo específico de equipo.

    La compatibilidad puede aplicarse:

    - A todos los modelos de una familia.
    - Únicamente a un modelo específico.
    - A una posición o color determinado.
    - Como compatibilidad principal o alternativa.

    Ejemplos:

    - Cilindro compatible con toda la familia Ricoh MP C3004.
    - Fusor compatible únicamente con Canon iR-ADV C5535i III.
    - Unidad de imagen cyan compatible con una familia determinada.
    """

    class CompatibilityType(models.TextChoices):
        ORIGINAL = (
            "original",
            "Original",
        )
        COMPATIBLE = (
            "compatible",
            "Compatible",
        )
        ALTERNATIVE = (
            "alternative",
            "Alternativa",
        )
        ADAPTED = (
            "adapted",
            "Adaptada",
        )

    class Position(models.TextChoices):
        BLACK = (
            "black",
            "Negro",
        )
        CYAN = (
            "cyan",
            "Cyan",
        )
        MAGENTA = (
            "magenta",
            "Magenta",
        )
        YELLOW = (
            "yellow",
            "Amarillo",
        )
        COLOR = (
            "color",
            "Color genérico",
        )
        MONOCHROME = (
            "monochrome",
            "Blanco y negro",
        )
        LEFT = (
            "left",
            "Izquierda",
        )
        RIGHT = (
            "right",
            "Derecha",
        )
        UPPER = (
            "upper",
            "Superior",
        )
        LOWER = (
            "lower",
            "Inferior",
        )
        FRONT = (
            "front",
            "Frontal",
        )
        REAR = (
            "rear",
            "Posterior",
        )
        MAIN = (
            "main",
            "Principal",
        )
        SECONDARY = (
            "secondary",
            "Secundaria",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )

    component = models.ForeignKey(
        EquipmentComponent,
        on_delete=models.PROTECT,
        related_name="compatibilities",
        verbose_name="Componente",
    )

    equipment_family = models.ForeignKey(
        EquipmentFamily,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="component_compatibilities",
        verbose_name="Familia de equipos",
        help_text=(
            "Familia completa con la que el componente "
            "es compatible."
        ),
    )

    equipment_model = models.ForeignKey(
        EquipmentModel,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="component_compatibilities",
        verbose_name="Modelo de equipo",
        help_text=(
            "Modelo específico con el que el componente "
            "es compatible."
        ),
    )

    compatibility_type = models.CharField(
        max_length=30,
        choices=CompatibilityType.choices,
        default=CompatibilityType.COMPATIBLE,
        db_index=True,
        verbose_name="Tipo de compatibilidad",
    )

    position = models.CharField(
        max_length=30,
        choices=Position.choices,
        default=Position.NOT_APPLICABLE,
        db_index=True,
        verbose_name="Color o posición",
        help_text=(
            "Color, ubicación o posición en la que se utiliza "
            "el componente dentro del equipo."
        ),
    )

    manufacturer_reference = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Referencia del fabricante",
        help_text=(
            "Código o referencia particular para esta "
            "compatibilidad."
        ),
    )

    requires_adjustment = models.BooleanField(
        default=False,
        verbose_name="Requiere adaptación",
        help_text=(
            "Indica si el componente necesita modificación, "
            "configuración o adaptación antes de instalarse."
        ),
    )

    adjustment_instructions = models.TextField(
        blank=True,
        verbose_name="Instrucciones de adaptación",
    )

    is_preferred = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Compatibilidad preferida",
        help_text=(
            "Indica que esta opción debe mostrarse primero "
            "al técnico."
        ),
    )

    technical_notes = models.TextField(
        blank=True,
        verbose_name="Notas técnicas",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activa",
        help_text=(
            "Las compatibilidades inactivas no deben mostrarse "
            "para nuevas reparaciones."
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
            "-is_preferred",
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
                name="unique_component_compatibility_target",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "component",
                    "is_active",
                ],
                name="equip_comp_compat_active_idx",
            ),
            models.Index(
                fields=[
                    "equipment_family",
                    "is_active",
                ],
                name="equip_comp_family_active_idx",
            ),
            models.Index(
                fields=[
                    "equipment_model",
                    "is_active",
                ],
                name="equip_comp_model_active_idx",
            ),
            models.Index(
                fields=[
                    "position",
                    "is_active",
                ],
                name="equip_comp_position_active_idx",
            ),
            models.Index(
                fields=[
                    "is_preferred",
                    "is_active",
                ],
                name="equip_comp_preferred_idx",
            ),
        ]

    def __str__(self):
        target = ""

        if self.equipment_model_id:
            target = str(self.equipment_model)
        elif self.equipment_family_id:
            target = str(self.equipment_family)

        if self.position != self.Position.NOT_APPLICABLE:
            return (
                f"{self.component} - {target} - "
                f"{self.get_position_display()}"
            )

        return f"{self.component} - {target}"

    def clean(self):
        """
        Normaliza y valida los datos antes de guardar.
        """

        super().clean()

        self.manufacturer_reference = str(
            self.manufacturer_reference or ""
        ).strip().upper()

        self.adjustment_instructions = str(
            self.adjustment_instructions or ""
        ).strip()

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

        if (
            not self.equipment_family_id
            and not self.equipment_model_id
        ):
            raise ValidationError(
                {
                    "equipment_family": (
                        "Debe seleccionar una familia o un "
                        "modelo de equipo."
                    ),
                    "equipment_model": (
                        "Debe seleccionar una familia o un "
                        "modelo de equipo."
                    ),
                }
            )

        if (
            self.equipment_family_id
            and self.equipment_model_id
        ):
            raise ValidationError(
                {
                    "equipment_family": (
                        "Seleccione únicamente una familia "
                        "o un modelo específico."
                    ),
                    "equipment_model": (
                        "Seleccione únicamente una familia "
                        "o un modelo específico."
                    ),
                }
            )

        if (
            self.requires_adjustment
            and not self.adjustment_instructions
        ):
            raise ValidationError(
                {
                    "adjustment_instructions": (
                        "Debe indicar las instrucciones de "
                        "adaptación del componente."
                    ),
                }
            )

        if (
            not self.requires_adjustment
            and self.adjustment_instructions
        ):
            raise ValidationError(
                {
                    "adjustment_instructions": (
                        "No debe registrar instrucciones si el "
                        "componente no requiere adaptación."
                    ),
                }
            )

        if self.equipment_model_id:
            if (
                self.equipment_model.equipment_family_id
                and self.equipment_family_id
                and self.equipment_model.equipment_family_id
                != self.equipment_family_id
            ):
                raise ValidationError(
                    {
                        "equipment_model": (
                            "El modelo no pertenece a la familia "
                            "seleccionada."
                        ),
                    }
                )

        if (
            self.position
            in [
                self.Position.BLACK,
                self.Position.CYAN,
                self.Position.MAGENTA,
                self.Position.YELLOW,
                self.Position.COLOR,
                self.Position.MONOCHROME,
            ]
            and self.component.color
            != EquipmentComponent.Color.NOT_APPLICABLE
        ):
            component_color_map = {
                EquipmentComponent.Color.BLACK: self.Position.BLACK,
                EquipmentComponent.Color.CYAN: self.Position.CYAN,
                EquipmentComponent.Color.MAGENTA: self.Position.MAGENTA,
                EquipmentComponent.Color.YELLOW: self.Position.YELLOW,
                EquipmentComponent.Color.COLOR: self.Position.COLOR,
                EquipmentComponent.Color.MONOCHROME: (
                    self.Position.MONOCHROME
                ),
            }

            expected_position = component_color_map.get(
                self.component.color
            )

            if expected_position and self.position != expected_position:
                raise ValidationError(
                    {
                        "position": (
                            "El color o posición no coincide con "
                            "el color definido en el componente."
                        ),
                    }
                )

        duplicate_compatibility = (
            ComponentCompatibility.objects.filter(
                component_id=self.component_id,
                equipment_family_id=self.equipment_family_id,
                equipment_model_id=self.equipment_model_id,
                position=self.position,
            ).exclude(
                pk=self.pk,
            )
        )

        if duplicate_compatibility.exists():
            raise ValidationError(
                {
                    "component": (
                        "Esta compatibilidad ya está registrada."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        """
        Normaliza y valida el registro antes de guardar.
        """

        self.manufacturer_reference = str(
            self.manufacturer_reference or ""
        ).strip().upper()

        self.adjustment_instructions = str(
            self.adjustment_instructions or ""
        ).strip()

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
        Al archivar la compatibilidad también se marca inactiva.
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
        Al restaurar la compatibilidad vuelve a quedar activa.
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