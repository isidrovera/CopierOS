# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from .base import EquipmentBaseModel
from .component_type import ComponentType


component_code_validator = RegexValidator(
    regex=r"^[A-Z0-9_-]+$",
    message=(
        "El código solo puede contener letras mayúsculas, "
        "números, guiones y guiones bajos."
    ),
)


class EquipmentComponent(EquipmentBaseModel):
    """
    Catálogo principal de componentes técnicos.

    Permite registrar:

    - Unidades técnicas.
    - Subpartes.
    - Accesorios.
    - Tóners.
    - Repuestos.

    Este catálogo representa el componente técnico general.
    La compatibilidad con familias y modelos se definirá en
    modelos separados.

    Ejemplos:

    - Unidad de imagen.
    - Unidad de fusor.
    - Unidad de transferencia.
    - Cilindro.
    - Cuchilla de limpieza.
    - Rodillo de presión.
    - Finalizador.
    - Tóner.
    """

    class Color(models.TextChoices):
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
        MULTICOLOR = (
            "multicolor",
            "Multicolor",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )

    class ConditionControl(models.TextChoices):
        NONE = (
            "none",
            "Sin control especial",
        )
        DATE = (
            "date",
            "Control por fecha",
        )
        METER = (
            "meter",
            "Control por contador",
        )
        DATE_AND_METER = (
            "date_and_meter",
            "Control por fecha y contador",
        )

    component_type = models.ForeignKey(
        ComponentType,
        on_delete=models.PROTECT,
        related_name="components",
        verbose_name="Tipo de componente",
    )

    parent_component = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="subcomponents",
        verbose_name="Componente principal",
        help_text=(
            "Se utiliza para relacionar una subparte con su unidad "
            "principal. Ejemplo: cilindro dentro de una unidad de imagen."
        ),
    )

    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        validators=[
            component_code_validator,
        ],
        verbose_name="Código",
        help_text=(
            "Código interno único del componente. "
            "Ejemplo: IMAGE_UNIT, DRUM o FUSER_PRESSURE_ROLLER."
        ),
    )

    name = models.CharField(
        max_length=180,
        db_index=True,
        verbose_name="Nombre",
        help_text="Nombre visible del componente.",
    )

    manufacturer_code = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Código del fabricante",
        help_text=(
            "Código original, part number o referencia utilizada "
            "por el fabricante."
        ),
    )

    alternative_code = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Código alternativo",
        help_text=(
            "Código alternativo utilizado por proveedores "
            "o fabricantes compatibles."
        ),
    )

    color = models.CharField(
        max_length=30,
        choices=Color.choices,
        default=Color.NOT_APPLICABLE,
        db_index=True,
        verbose_name="Color",
    )

    condition_control = models.CharField(
        max_length=30,
        choices=ConditionControl.choices,
        default=ConditionControl.NONE,
        db_index=True,
        verbose_name="Control de vida útil",
    )

    expected_life_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Vida útil estimada por contador",
        help_text=(
            "Cantidad estimada de impresiones, copias o ciclos "
            "que debería durar el componente."
        ),
    )

    expected_life_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Vida útil estimada en días",
    )

    requires_individual_serial = models.BooleanField(
        default=False,
        verbose_name="Requiere serie individual",
        help_text=(
            "Indica si cada unidad física debe manejarse mediante "
            "un número de serie propio."
        ),
    )

    is_consumable = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Es consumible",
        help_text=(
            "Indica si normalmente se consume y no retorna "
            "al inventario después de instalarse."
        ),
    )

    is_reusable = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Es reutilizable",
        help_text=(
            "Indica si puede retirarse, repararse y volver "
            "a utilizarse."
        ),
    )

    can_be_repaired = models.BooleanField(
        default=False,
        verbose_name="Puede repararse",
        help_text=(
            "Indica si el componente puede ingresar nuevamente "
            "al taller para reparación o reacondicionamiento."
        ),
    )

    requires_removed_part_tracking = models.BooleanField(
        default=False,
        verbose_name="Controlar componente retirado",
        help_text=(
            "Obliga a registrar qué ocurrió con la pieza retirada: "
            "desecho, devolución, reparación o recuperación."
        ),
    )

    unit_of_measure = models.CharField(
        max_length=30,
        default="unit",
        verbose_name="Unidad de medida",
        help_text=(
            "Ejemplo: unit, kit, bottle, kilogram o meter."
        ),
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    technical_notes = models.TextField(
        blank=True,
        verbose_name="Notas técnicas",
    )

    image = models.ImageField(
        upload_to="equipment/components/",
        null=True,
        blank=True,
        verbose_name="Imagen referencial",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activo",
        help_text=(
            "Los componentes inactivos no deben mostrarse para "
            "nuevos registros, pero se conservan en el historial."
        ),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Orden de visualización",
    )

    class Meta:
        verbose_name = "Componente de equipo"
        verbose_name_plural = "Componentes de equipos"
        ordering = (
            "component_type__display_order",
            "display_order",
            "name",
        )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "component_type",
                    "name",
                    "color",
                ],
                name="unique_component_type_name_color",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "component_type",
                    "is_active",
                ],
                name="eq_comp_type_idx",
            ),
            models.Index(
                fields=[
                    "parent_component",
                    "is_active",
                ],
                name="eq_comp_parent_idx",
            ),
            models.Index(
                fields=[
                    "color",
                    "is_active",
                ],
                name="eq_comp_color_idx",
            ),
            models.Index(
                fields=[
                    "is_consumable",
                    "is_active",
                ],
                name="eq_comp_consum_idx",
            ),
        ]

    def __str__(self):
        if self.color != self.Color.NOT_APPLICABLE:
            return f"{self.name} - {self.get_color_display()}"

        return self.name

    def clean(self):
        """
        Normaliza y valida los datos antes de guardar.
        """

        super().clean()

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.name = str(
            self.name or ""
        ).strip()

        self.manufacturer_code = str(
            self.manufacturer_code or ""
        ).strip().upper()

        self.alternative_code = str(
            self.alternative_code or ""
        ).strip().upper()

        self.unit_of_measure = str(
            self.unit_of_measure or ""
        ).strip().lower()

        self.description = str(
            self.description or ""
        ).strip()

        self.technical_notes = str(
            self.technical_notes or ""
        ).strip()

        if not self.code:
            raise ValidationError(
                {
                    "code": (
                        "El código del componente es obligatorio."
                    ),
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": (
                        "El nombre del componente es obligatorio."
                    ),
                }
            )

        if not self.component_type_id:
            raise ValidationError(
                {
                    "component_type": (
                        "El tipo de componente es obligatorio."
                    ),
                }
            )

        if not self.unit_of_measure:
            raise ValidationError(
                {
                    "unit_of_measure": (
                        "La unidad de medida es obligatoria."
                    ),
                }
            )

        duplicate_code = EquipmentComponent.objects.filter(
            code__iexact=self.code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe un componente registrado "
                        "con este código."
                    ),
                }
            )

        if self.component_type_id and self.name:
            duplicate_component = EquipmentComponent.objects.filter(
                component_type_id=self.component_type_id,
                name__iexact=self.name,
                color=self.color,
            ).exclude(
                pk=self.pk,
            )

            if duplicate_component.exists():
                raise ValidationError(
                    {
                        "name": (
                            "Ya existe un componente con este nombre, "
                            "tipo y color."
                        ),
                    }
                )

        if self.parent_component_id:
            if self.parent_component_id == self.pk:
                raise ValidationError(
                    {
                        "parent_component": (
                            "Un componente no puede ser su propio "
                            "componente principal."
                        ),
                    }
                )

            if (
                self.parent_component.parent_component_id
                == self.pk
            ):
                raise ValidationError(
                    {
                        "parent_component": (
                            "La relación entre componentes genera "
                            "una referencia circular."
                        ),
                    }
                )

            if (
                self.component_type.category
                != ComponentType.Category.SUBPART
            ):
                raise ValidationError(
                    {
                        "parent_component": (
                            "Solo las subpartes pueden relacionarse "
                            "con un componente principal."
                        ),
                    }
                )

        if (
            self.component_type.requires_color
            and self.color == self.Color.NOT_APPLICABLE
        ):
            raise ValidationError(
                {
                    "color": (
                        "Este tipo de componente requiere indicar "
                        "un color."
                    ),
                }
            )

        if (
            not self.component_type.requires_color
            and self.color != self.Color.NOT_APPLICABLE
        ):
            raise ValidationError(
                {
                    "color": (
                        "Este tipo de componente no requiere color."
                    ),
                }
            )

        if (
            self.condition_control
            in [
                self.ConditionControl.METER,
                self.ConditionControl.DATE_AND_METER,
            ]
            and not self.expected_life_meter
        ):
            raise ValidationError(
                {
                    "expected_life_meter": (
                        "Debe indicar la vida útil estimada "
                        "por contador."
                    ),
                }
            )

        if (
            self.condition_control
            in [
                self.ConditionControl.DATE,
                self.ConditionControl.DATE_AND_METER,
            ]
            and not self.expected_life_days
        ):
            raise ValidationError(
                {
                    "expected_life_days": (
                        "Debe indicar la vida útil estimada "
                        "en días."
                    ),
                }
            )

        if (
            self.requires_individual_serial
            and not self.component_type.requires_serial_number
        ):
            raise ValidationError(
                {
                    "requires_individual_serial": (
                        "El tipo de componente seleccionado no permite "
                        "control mediante número de serie."
                    ),
                }
            )

        if self.is_consumable and self.is_reusable:
            raise ValidationError(
                {
                    "is_reusable": (
                        "Un componente consumible no puede marcarse "
                        "también como reutilizable."
                    ),
                }
            )

        if self.can_be_repaired and not self.is_reusable:
            raise ValidationError(
                {
                    "can_be_repaired": (
                        "Para permitir reparación, el componente debe "
                        "estar marcado como reutilizable."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        """
        Normaliza y valida el registro antes de guardarlo.
        """

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.name = str(
            self.name or ""
        ).strip()

        self.manufacturer_code = str(
            self.manufacturer_code or ""
        ).strip().upper()

        self.alternative_code = str(
            self.alternative_code or ""
        ).strip().upper()

        self.unit_of_measure = str(
            self.unit_of_measure or ""
        ).strip().lower()

        self.description = str(
            self.description or ""
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
        Al archivar el componente también se marca como inactivo.
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
        Al restaurar el componente vuelve a quedar activo.
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