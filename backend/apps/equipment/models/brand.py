# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from .base import EquipmentBaseModel


brand_code_validator = RegexValidator(
    regex=r"^[A-Z0-9_]+$",
    message=(
        "El código solo puede contener letras mayúsculas, "
        "números y guiones bajos."
    ),
)


class EquipmentBrand(EquipmentBaseModel):
    """
    Catálogo de marcas de equipos.

    Ejemplos:

    - Canon.
    - Ricoh.
    - Konica Minolta.
    - Kyocera.
    - Xerox.
    - Sharp.
    - Riso.
    - HP.
    - Epson.

    La marca será utilizada posteriormente por:

    - Modelos de equipos.
    - Máquinas.
    - Accesorios.
    - Unidades técnicas.
    - Compatibilidades.
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        validators=[
            brand_code_validator,
        ],
        verbose_name="Código",
        help_text=(
            "Código interno único de la marca. "
            "Ejemplo: CANON, RICOH o KONICA_MINOLTA."
        ),
    )

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Nombre",
        help_text="Nombre comercial visible de la marca.",
    )

    legal_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Razón social del fabricante",
        help_text=(
            "Nombre legal o corporativo del fabricante, "
            "si se requiere."
        ),
    )

    country_code = models.CharField(
        max_length=2,
        blank=True,
        verbose_name="Código de país",
        help_text=(
            "Código ISO de dos letras del país de origen. "
            "Ejemplo: JP, US o DE."
        ),
    )

    country_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="País de origen",
    )

    website = models.URLField(
        blank=True,
        verbose_name="Sitio web",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    logo = models.ImageField(
        upload_to="equipment/brands/",
        null=True,
        blank=True,
        verbose_name="Logotipo",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activa",
        help_text=(
            "Las marcas inactivas no deben mostrarse para nuevos "
            "registros, pero se conservan en los equipos existentes."
        ),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Orden de visualización",
    )

    class Meta:
        verbose_name = "Marca de equipo"
        verbose_name_plural = "Marcas de equipos"
        ordering = (
            "display_order",
            "name",
        )
        indexes = [
            models.Index(
                fields=[
                    "is_active",
                    "display_order",
                ],
                name="equip_brand_active_order_idx",
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

        self.legal_name = str(
            self.legal_name or ""
        ).strip()

        self.country_code = str(
            self.country_code or ""
        ).strip().upper()

        self.country_name = str(
            self.country_name or ""
        ).strip()

        self.website = str(
            self.website or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        if not self.code:
            raise ValidationError(
                {
                    "code": "El código de la marca es obligatorio.",
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": "El nombre de la marca es obligatorio.",
                }
            )

        if self.country_code and len(self.country_code) != 2:
            raise ValidationError(
                {
                    "country_code": (
                        "El código de país debe contener exactamente "
                        "dos letras."
                    ),
                }
            )

        if self.country_code and not self.country_code.isalpha():
            raise ValidationError(
                {
                    "country_code": (
                        "El código de país solo puede contener letras."
                    ),
                }
            )

        duplicate_code = EquipmentBrand.objects.filter(
            code__iexact=self.code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe una marca registrada "
                        "con este código."
                    ),
                }
            )

        duplicate_name = EquipmentBrand.objects.filter(
            name__iexact=self.name,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_name.exists():
            raise ValidationError(
                {
                    "name": (
                        "Ya existe una marca registrada "
                        "con este nombre."
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

        self.legal_name = str(
            self.legal_name or ""
        ).strip()

        self.country_code = str(
            self.country_code or ""
        ).strip().upper()

        self.country_name = str(
            self.country_name or ""
        ).strip()

        self.website = str(
            self.website or ""
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
        Al archivar la marca también se marca como inactiva.
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
        Al restaurar la marca vuelve a quedar activa.
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