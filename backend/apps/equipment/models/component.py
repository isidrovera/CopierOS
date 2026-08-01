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
    Catálogo técnico descriptivo de componentes de equipos.

    Permite registrar:

    - Unidades técnicas completas.
    - Subpartes de una unidad.
    - Repuestos independientes.
    - Accesorios.
    - Tóners.
    - Consumibles.

    Cada componente puede tener:

    - Código interno.
    - Código original del fabricante.
    - Código alternativo.
    - Color.
    - Duración estimada.
    - Componente principal.
    - Imagen y notas técnicas.

    Este modelo no controla stock, cantidades, precios,
    almacenes ni movimientos de inventario.
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
            "Sin duración definida",
        )
        DATE = (
            "date",
            "Duración por tiempo",
        )
        METER = (
            "meter",
            "Duración por contador",
        )
        DATE_AND_METER = (
            "date_and_meter",
            "Duración por tiempo y contador",
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
            "Relaciona una subparte con la unidad o componente "
            "principal al que pertenece. Por ejemplo, un rodillo "
            "de presión dentro de una unidad fusora."
        ),
    )

    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        validators=[
            component_code_validator,
        ],
        verbose_name="Código interno",
        help_text=(
            "Código interno único utilizado por el sistema. "
            "Ejemplo: FUSER_UNIT, PRESSURE_ROLLER o TONER_BLACK."
        ),
    )

    name = models.CharField(
        max_length=180,
        db_index=True,
        verbose_name="Nombre",
        help_text="Nombre visible del componente técnico.",
    )

    manufacturer_code = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Código del fabricante",
        help_text=(
            "Código original, part number o referencia oficial "
            "proporcionada por el fabricante."
        ),
    )

    alternative_code = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Código alternativo",
        help_text=(
            "Código compatible, equivalente o alternativo utilizado "
            "por otro fabricante o proveedor."
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
        verbose_name="Tipo de duración estimada",
    )

    expected_life_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración estimada por contador",
        help_text=(
            "Cantidad estimada de copias, impresiones, escaneos "
            "o ciclos que debería durar el componente."
        ),
    )

    expected_life_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración estimada en días",
        help_text=(
            "Cantidad estimada de días de duración cuando el fabricante "
            "o la experiencia técnica proporciona esta información."
        ),
    )

    life_reference = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Referencia de duración",
        help_text=(
            "Fuente o referencia utilizada para establecer la duración. "
            "Por ejemplo: manual del fabricante, ficha técnica o "
            "experiencia del taller."
        ),
    )

    requires_individual_serial = models.BooleanField(
        default=False,
        verbose_name="Permite registrar serie individual",
        help_text=(
            "Indica si una unidad física o accesorio puede identificarse "
            "mediante su propio número de serie."
        ),
    )

    is_consumable = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Es consumible",
        help_text=(
            "Indica si el componente se consume normalmente durante "
            "el funcionamiento, por ejemplo tóner o tinta."
        ),
    )

    is_reusable = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Es reutilizable",
        help_text=(
            "Indica si el componente puede retirarse, repararse "
            "y volver a utilizarse."
        ),
    )

    can_be_repaired = models.BooleanField(
        default=False,
        verbose_name="Puede repararse",
        help_text=(
            "Indica si el componente puede ser reparado "
            "o reacondicionado."
        ),
    )

    requires_removed_part_tracking = models.BooleanField(
        default=False,
        verbose_name="Controlar componente retirado",
        help_text=(
            "Indica si debe registrarse el destino de la unidad "
            "o pieza retirada durante una reparación o servicio."
        ),
    )

    unit_of_measure = models.CharField(
        max_length=30,
        default="unit",
        verbose_name="Unidad de medida",
        help_text=(
            "Unidad descriptiva. Ejemplo: unit, kit, bottle, "
            "kilogram o meter."
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
            "Los componentes inactivos no deben mostrarse en nuevos "
            "registros, pero se conservan en el historial."
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
            models.Index(
                fields=[
                    "manufacturer_code",
                    "is_active",
                ],
                name="eq_comp_mfr_code_idx",
            ),
        ]

    def __str__(self):
        component_name = self.name

        if self.color != self.Color.NOT_APPLICABLE:
            component_name = (
                f"{component_name} - "
                f"{self.get_color_display()}"
            )

        if self.manufacturer_code:
            component_name = (
                f"{component_name} "
                f"[{self.manufacturer_code}]"
            )

        return component_name

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

        self.life_reference = str(
            self.life_reference or ""
        ).strip()

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
                        "El código interno del componente "
                        "es obligatorio."
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
                        "con este código interno."
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
                self.component_type.category
                != ComponentType.Category.SUBPART
            ):
                raise ValidationError(
                    {
                        "parent_component": (
                            "Solo una subparte puede relacionarse "
                            "con un componente principal."
                        ),
                    }
                )

            parent = self.parent_component

            while parent is not None:
                if parent.pk == self.pk:
                    raise ValidationError(
                        {
                            "parent_component": (
                                "La relación entre componentes "
                                "genera una referencia circular."
                            ),
                        }
                    )

                parent = parent.parent_component

        elif (
            self.component_type_id
            and self.component_type.category
            == ComponentType.Category.SUBPART
        ):
            raise ValidationError(
                {
                    "parent_component": (
                        "Debe seleccionar el componente principal "
                        "al que pertenece esta subparte."
                    ),
                }
            )

        if (
            self.component_type_id
            and self.component_type.requires_color
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
            self.component_type_id
            and not self.component_type.requires_color
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
                        "Debe indicar la duración estimada "
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
                        "Debe indicar la duración estimada "
                        "en días."
                    ),
                }
            )

        if (
            self.condition_control
            == self.ConditionControl.NONE
            and (
                self.expected_life_meter is not None
                or self.expected_life_days is not None
            )
        ):
            raise ValidationError(
                {
                    "condition_control": (
                        "Debe seleccionar el tipo de duración "
                        "cuando registra una duración estimada."
                    ),
                }
            )

        if (
            self.condition_control
            == self.ConditionControl.DATE
            and self.expected_life_meter is not None
        ):
            raise ValidationError(
                {
                    "expected_life_meter": (
                        "No debe registrar duración por contador "
                        "cuando el control es únicamente por tiempo."
                    ),
                }
            )

        if (
            self.condition_control
            == self.ConditionControl.METER
            and self.expected_life_days is not None
        ):
            raise ValidationError(
                {
                    "expected_life_days": (
                        "No debe registrar duración por días "
                        "cuando el control es únicamente por contador."
                    ),
                }
            )

        if (
            self.requires_individual_serial
            and self.component_type_id
            and not self.component_type.requires_serial_number
        ):
            raise ValidationError(
                {
                    "requires_individual_serial": (
                        "El tipo de componente seleccionado no permite "
                        "registrar un número de serie individual."
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
        Normaliza y valida el componente antes de guardarlo.
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

        self.life_reference = str(
            self.life_reference or ""
        ).strip()

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
        Archiva el componente y lo marca como inactivo.
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
        Restaura el componente y lo vuelve a marcar como activo.
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