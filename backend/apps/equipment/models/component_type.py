# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from .base import EquipmentBaseModel


component_type_code_validator = RegexValidator(
    regex=r"^[A-Z0-9_-]+$",
    message=(
        "El código solo puede contener letras mayúsculas, "
        "números, guiones y guiones bajos."
    ),
)


class ComponentType(EquipmentBaseModel):
    """
    Catálogo de tipos de componentes técnicos.

    Permite clasificar los elementos utilizados durante la revisión,
    reparación, mantenimiento y preparación de un equipo.

    Ejemplos:

    - Unidad técnica.
    - Subparte.
    - Accesorio.
    - Tóner.
    - Repuesto.

    Posteriormente estos tipos serán utilizados por el catálogo de
    componentes, las compatibilidades y el inventario.
    """

    class Category(models.TextChoices):
        TECHNICAL_UNIT = (
            "technical_unit",
            "Unidad técnica",
        )
        SUBPART = (
            "subpart",
            "Subparte",
        )
        ACCESSORY = (
            "accessory",
            "Accesorio",
        )
        TONER = (
            "toner",
            "Tóner",
        )
        SPARE_PART = (
            "spare_part",
            "Repuesto",
        )

    code = models.CharField(
        max_length=60,
        unique=True,
        db_index=True,
        validators=[
            component_type_code_validator,
        ],
        verbose_name="Código",
        help_text=(
            "Código interno único del tipo de componente. "
            "Ejemplo: TECHNICAL_UNIT, SUBPART o TONER."
        ),
    )

    name = models.CharField(
        max_length=120,
        unique=True,
        db_index=True,
        verbose_name="Nombre",
        help_text=(
            "Nombre visible del tipo de componente."
        ),
    )

    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        db_index=True,
        verbose_name="Categoría",
        help_text=(
            "Clasificación principal del componente."
        ),
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    requires_color = models.BooleanField(
        default=False,
        verbose_name="Requiere color",
        help_text=(
            "Indica si los componentes de este tipo deben identificar "
            "color, por ejemplo negro, cyan, magenta o amarillo."
        ),
    )

    requires_serial_number = models.BooleanField(
        default=False,
        verbose_name="Requiere número de serie",
        help_text=(
            "Indica si los componentes de este tipo pueden controlarse "
            "individualmente mediante número de serie."
        ),
    )

    requires_meter = models.BooleanField(
        default=False,
        verbose_name="Requiere contador",
        help_text=(
            "Indica si debe registrarse el contador del equipo cuando "
            "se instala o retira un componente de este tipo."
        ),
    )

    controls_stock = models.BooleanField(
        default=True,
        verbose_name="Controla existencias",
        help_text=(
            "Indica si los componentes de este tipo deben administrarse "
            "mediante inventario."
        ),
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activo",
        help_text=(
            "Los tipos inactivos no deben mostrarse para nuevos "
            "componentes, pero se conservan en los registros existentes."
        ),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Orden de visualización",
    )

    class Meta:
        verbose_name = "Tipo de componente"
        verbose_name_plural = "Tipos de componentes"
        ordering = (
            "display_order",
            "name",
        )
        indexes = [
            models.Index(
                fields=[
                    "category",
                    "is_active",
                ],
                name="equip_comp_type_cat_active_idx",
            ),
            models.Index(
                fields=[
                    "is_active",
                    "display_order",
                ],
                name="eq_comp_type_order_idx",
            ),
        ]

    def __str__(self):
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

        self.description = str(
            self.description or ""
        ).strip()

        if not self.code:
            raise ValidationError(
                {
                    "code": (
                        "El código del tipo de componente "
                        "es obligatorio."
                    ),
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": (
                        "El nombre del tipo de componente "
                        "es obligatorio."
                    ),
                }
            )

        if not self.category:
            raise ValidationError(
                {
                    "category": (
                        "La categoría del tipo de componente "
                        "es obligatoria."
                    ),
                }
            )

        duplicate_code = ComponentType.objects.filter(
            code__iexact=self.code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe un tipo de componente "
                        "registrado con este código."
                    ),
                }
            )

        duplicate_name = ComponentType.objects.filter(
            name__iexact=self.name,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_name.exists():
            raise ValidationError(
                {
                    "name": (
                        "Ya existe un tipo de componente "
                        "registrado con este nombre."
                    ),
                }
            )

        if (
            self.category == self.Category.TONER
            and not self.requires_color
        ):
            raise ValidationError(
                {
                    "requires_color": (
                        "El tipo de componente tóner debe "
                        "identificar el color."
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

        self.description = str(
            self.description or ""
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
        Al archivar el tipo también se marca como inactivo.
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
        Al restaurar el tipo vuelve a quedar activo.
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