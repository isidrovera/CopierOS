# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from .base import EquipmentBaseModel
from .brand import EquipmentBrand
from .equipment_family import EquipmentFamily
from .equipment_type import EquipmentType


equipment_model_code_validator = RegexValidator(
    regex=r"^[A-Z0-9_-]+$",
    message=(
        "El código solo puede contener letras mayúsculas, "
        "números, guiones y guiones bajos."
    ),
)


class EquipmentModel(EquipmentBaseModel):
    """
    Catálogo de modelos de equipos.

    Un modelo pertenece a una marca y a un tipo de equipo.

    Ejemplos:

    - Canon iR-ADV C5535i III.
    - Ricoh IM C6000.
    - Konica Minolta bizhub C450i.
    - Riso ComColor GD9630.
    - HP DesignJet T830.

    Este modelo contiene las características generales del modelo
    comercial. Los datos físicos particulares, como serie, contador,
    precio o cliente, se registrarán posteriormente en Equipment.
    """

    class ColorMode(models.TextChoices):
        MONOCHROME = (
            "monochrome",
            "Blanco y negro",
        )
        COLOR = (
            "color",
            "Color",
        )
        MIXED = (
            "mixed",
            "Disponible en color o blanco y negro",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )

    class Technology(models.TextChoices):
        LASER = (
            "laser",
            "Láser",
        )
        INKJET = (
            "inkjet",
            "Inyección de tinta",
        )
        DIGITAL_DUPLICATION = (
            "digital_duplication",
            "Duplicación digital",
        )
        THERMAL = (
            "thermal",
            "Térmica",
        )
        LED = (
            "led",
            "LED",
        )
        OTHER = (
            "other",
            "Otra",
        )
        NOT_DEFINED = (
            "not_defined",
            "No definida",
        )

    class MaximumPaperSize(models.TextChoices):
        A4 = (
            "a4",
            "A4",
        )
        A3 = (
            "a3",
            "A3",
        )
        SRA3 = (
            "sra3",
            "SRA3",
        )
        A2 = (
            "a2",
            "A2",
        )
        A1 = (
            "a1",
            "A1",
        )
        A0 = (
            "a0",
            "A0",
        )
        LARGE_FORMAT = (
            "large_format",
            "Gran formato",
        )
        CONTINUOUS = (
            "continuous",
            "Papel continuo",
        )
        OTHER = (
            "other",
            "Otro",
        )
        NOT_DEFINED = (
            "not_defined",
            "No definido",
        )

    code = models.CharField(
        max_length=80,
        unique=True,
        db_index=True,
        validators=[
            equipment_model_code_validator,
        ],
        verbose_name="Código",
        help_text=(
            "Código interno único del modelo. "
            "Ejemplo: CANON_IR_ADV_C5535I_III."
        ),
    )

    brand = models.ForeignKey(
        EquipmentBrand,
        on_delete=models.PROTECT,
        related_name="equipment_models",
        verbose_name="Marca",
    )

    equipment_type = models.ForeignKey(
        EquipmentType,
        on_delete=models.PROTECT,
        related_name="equipment_models",
        verbose_name="Tipo de equipo",
    )

    name = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Modelo",
        help_text=(
            "Nombre del modelo según el fabricante. "
            "Ejemplo: iR-ADV C5535i III."
        ),
    )

    commercial_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre comercial",
        help_text=(
            "Nombre comercial completo cuando sea diferente "
            "al nombre del modelo."
        ),
    )

    family = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Familia",
        help_text=(
            "Familia o serie comercial a la que pertenece el modelo. "
            "Ejemplo: iR-ADV C5500 Series."
        ),
    )

    equipment_family = models.ForeignKey(
        EquipmentFamily,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="equipment_models",
        verbose_name="Familia de equipos",
        help_text=(
            "Familia controlada utilizada para definir compatibilidad "
            "de unidades, subpartes, accesorios, tóners y repuestos."
        ),
    )

    manufacturer_reference = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Referencia del fabricante",
        help_text=(
            "Código, referencia o número de producto utilizado "
            "por el fabricante."
        ),
    )

    color_mode = models.CharField(
        max_length=30,
        choices=ColorMode.choices,
        default=ColorMode.NOT_APPLICABLE,
        db_index=True,
        verbose_name="Capacidad de color",
    )

    technology = models.CharField(
        max_length=30,
        choices=Technology.choices,
        default=Technology.NOT_DEFINED,
        db_index=True,
        verbose_name="Tecnología",
    )

    maximum_paper_size = models.CharField(
        max_length=30,
        choices=MaximumPaperSize.choices,
        default=MaximumPaperSize.NOT_DEFINED,
        db_index=True,
        verbose_name="Formato máximo de papel",
    )

    is_multifunction = models.BooleanField(
        default=False,
        verbose_name="Es multifuncional",
        help_text=(
            "Indica si el modelo combina dos o más funciones, "
            "por ejemplo impresión, copia y escaneo."
        ),
    )

    supports_printing = models.BooleanField(
        default=True,
        verbose_name="Permite impresión",
    )

    supports_copying = models.BooleanField(
        default=True,
        verbose_name="Permite copia",
    )

    supports_scanning = models.BooleanField(
        default=True,
        verbose_name="Permite escaneo",
    )

    supports_fax = models.BooleanField(
        default=False,
        verbose_name="Permite fax",
    )

    supports_network = models.BooleanField(
        default=True,
        verbose_name="Permite conexión de red",
    )

    supports_duplex = models.BooleanField(
        default=True,
        verbose_name="Permite dúplex",
    )

    supports_accessories = models.BooleanField(
        default=True,
        verbose_name="Permite accesorios",
        help_text=(
            "Indica si este modelo puede tener finalizadores, "
            "alimentadores, bandejas u otros accesorios."
        ),
    )

    supports_technical_units = models.BooleanField(
        default=True,
        verbose_name="Permite unidades técnicas",
        help_text=(
            "Indica si se controlarán unidades internas como "
            "imagen, revelado, fusor o transferencia."
        ),
    )

    has_total_meter = models.BooleanField(
        default=True,
        verbose_name="Tiene contador total",
    )

    has_black_meter = models.BooleanField(
        default=True,
        verbose_name="Tiene contador blanco y negro",
    )

    has_color_meter = models.BooleanField(
        default=False,
        verbose_name="Tiene contador color",
    )

    has_scan_meter = models.BooleanField(
        default=False,
        verbose_name="Tiene contador de escaneo",
    )

    image = models.ImageField(
        upload_to="equipment/models/",
        null=True,
        blank=True,
        verbose_name="Imagen referencial",
    )

    technical_notes = models.TextField(
        blank=True,
        verbose_name="Notas técnicas",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activo",
        help_text=(
            "Los modelos inactivos no deben mostrarse para "
            "registrar nuevos equipos."
        ),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Orden de visualización",
    )

    class Meta:
        verbose_name = "Modelo de equipo"
        verbose_name_plural = "Modelos de equipos"
        ordering = (
            "brand__name",
            "display_order",
            "name",
        )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "brand",
                    "name",
                ],
                name="unique_equipment_model_brand_name",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "brand",
                    "is_active",
                ],
                name="equip_model_brand_active_idx",
            ),
            models.Index(
                fields=[
                    "equipment_type",
                    "is_active",
                ],
                name="equip_model_type_active_idx",
            ),
            models.Index(
                fields=[
                    "family",
                    "is_active",
                ],
                name="equip_model_family_active_idx",
            ),
            models.Index(
                fields=[
                    "equipment_family",
                    "is_active",
                ],
                name="equip_model_eq_family_idx",
            ),
        ]

    def __str__(self):
        return f"{self.brand.name} {self.name}"

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

        self.commercial_name = str(
            self.commercial_name or ""
        ).strip()

        self.family = str(
            self.family or ""
        ).strip()

        self.manufacturer_reference = str(
            self.manufacturer_reference or ""
        ).strip()

        self.technical_notes = str(
            self.technical_notes or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        if not self.code:
            raise ValidationError(
                {
                    "code": (
                        "El código del modelo de equipo "
                        "es obligatorio."
                    ),
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": (
                        "El nombre del modelo de equipo "
                        "es obligatorio."
                    ),
                }
            )

        if not self.brand_id:
            raise ValidationError(
                {
                    "brand": "La marca es obligatoria.",
                }
            )

        if not self.equipment_type_id:
            raise ValidationError(
                {
                    "equipment_type": (
                        "El tipo de equipo es obligatorio."
                    ),
                }
            )

        if self.equipment_family_id:
            if (
                self.equipment_family.brand_id
                != self.brand_id
            ):
                raise ValidationError(
                    {
                        "equipment_family": (
                            "La familia seleccionada no pertenece "
                            "a la marca del modelo."
                        ),
                    }
                )

            if (
                self.equipment_family.equipment_type_id
                != self.equipment_type_id
            ):
                raise ValidationError(
                    {
                        "equipment_family": (
                            "La familia seleccionada no pertenece "
                            "al tipo de equipo del modelo."
                        ),
                    }
                )

        duplicate_code = EquipmentModel.objects.filter(
            code__iexact=self.code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe un modelo de equipo registrado "
                        "con este código."
                    ),
                }
            )

        if self.brand_id and self.name:
            duplicate_model = EquipmentModel.objects.filter(
                brand_id=self.brand_id,
                name__iexact=self.name,
            ).exclude(
                pk=self.pk,
            )

            if duplicate_model.exists():
                raise ValidationError(
                    {
                        "name": (
                            "Ya existe este modelo registrado "
                            "para la marca seleccionada."
                        ),
                    }
                )

        if (
            self.color_mode == self.ColorMode.MONOCHROME
            and self.has_color_meter
        ):
            raise ValidationError(
                {
                    "has_color_meter": (
                        "Un modelo blanco y negro no puede tener "
                        "contador de color."
                    ),
                }
            )

        if (
            self.color_mode == self.ColorMode.COLOR
            and not self.has_color_meter
        ):
            raise ValidationError(
                {
                    "has_color_meter": (
                        "Un modelo de color debe permitir registrar "
                        "un contador de color."
                    ),
                }
            )

        if (
            not self.supports_scanning
            and self.has_scan_meter
        ):
            raise ValidationError(
                {
                    "has_scan_meter": (
                        "No se puede habilitar el contador de escaneo "
                        "si el modelo no permite escanear."
                    ),
                }
            )

        if (
            not self.supports_accessories
            and self.supports_technical_units
        ):
            pass

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

        self.commercial_name = str(
            self.commercial_name or ""
        ).strip()

        self.family = str(
            self.family or ""
        ).strip()

        self.manufacturer_reference = str(
            self.manufacturer_reference or ""
        ).strip()

        self.technical_notes = str(
            self.technical_notes or ""
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
        Al archivar el modelo también se marca como inactivo.
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
        Al restaurar el modelo vuelve a quedar activo.
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