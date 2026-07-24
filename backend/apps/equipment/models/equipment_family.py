# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from .base import EquipmentBaseModel
from .brand import EquipmentBrand
from .equipment_type import EquipmentType


equipment_family_code_validator = RegexValidator(
    regex=r"^[A-Z0-9_-]+$",
    message=(
        "El código solo puede contener letras mayúsculas, "
        "números, guiones y guiones bajos."
    ),
)


class EquipmentFamily(EquipmentBaseModel):
    """
    Catálogo de familias de modelos de equipos.

    Una familia agrupa modelos que comparten características,
    unidades técnicas, subpartes, accesorios, tóners o repuestos.

    Ejemplos:

    - Canon iR-ADV C5500 Series.
    - Ricoh MP C3004 Series.
    - Ricoh IM 350 / IM 430.
    - Konica Minolta bizhub C250i Series.

    La compatibilidad podrá definirse posteriormente:

    - Para toda la familia.
    - Para modelos específicos dentro de la familia.
    - Por color o posición del componente.
    """

    code = models.CharField(
        max_length=80,
        unique=True,
        db_index=True,
        validators=[
            equipment_family_code_validator,
        ],
        verbose_name="Código",
        help_text=(
            "Código interno único de la familia. "
            "Ejemplo: CANON_IR_ADV_C5500_SERIES."
        ),
    )

    brand = models.ForeignKey(
        EquipmentBrand,
        on_delete=models.PROTECT,
        related_name="equipment_families",
        verbose_name="Marca",
    )

    equipment_type = models.ForeignKey(
        EquipmentType,
        on_delete=models.PROTECT,
        related_name="equipment_families",
        verbose_name="Tipo de equipo",
    )

    name = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Familia",
        help_text=(
            "Nombre visible de la familia de modelos. "
            "Ejemplo: iR-ADV C5500 Series."
        ),
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text=(
            "Información general sobre los modelos incluidos "
            "en esta familia."
        ),
    )

    technical_notes = models.TextField(
        blank=True,
        verbose_name="Notas técnicas",
        help_text=(
            "Observaciones técnicas sobre compatibilidades, "
            "variaciones o restricciones de la familia."
        ),
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activa",
        help_text=(
            "Las familias inactivas no deben mostrarse para "
            "nuevos registros, pero se conservan en los modelos "
            "existentes."
        ),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Orden de visualización",
    )

    class Meta:
        verbose_name = "Familia de equipos"
        verbose_name_plural = "Familias de equipos"
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
                name="unique_equipment_family_brand_name",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "brand",
                    "is_active",
                ],
                name="equip_family_brand_active_idx",
            ),
            models.Index(
                fields=[
                    "equipment_type",
                    "is_active",
                ],
                name="equip_family_type_active_idx",
            ),
            models.Index(
                fields=[
                    "is_active",
                    "display_order",
                ],
                name="equip_family_active_order_idx",
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
                        "El código de la familia de equipos "
                        "es obligatorio."
                    ),
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": (
                        "El nombre de la familia de equipos "
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

        duplicate_code = EquipmentFamily.objects.filter(
            code__iexact=self.code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe una familia de equipos "
                        "registrada con este código."
                    ),
                }
            )

        if self.brand_id and self.name:
            duplicate_family = EquipmentFamily.objects.filter(
                brand_id=self.brand_id,
                name__iexact=self.name,
            ).exclude(
                pk=self.pk,
            )

            if duplicate_family.exists():
                raise ValidationError(
                    {
                        "name": (
                            "Ya existe esta familia registrada "
                            "para la marca seleccionada."
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
        Al archivar la familia también se marca como inactiva.
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
        Al restaurar la familia vuelve a quedar activa.
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