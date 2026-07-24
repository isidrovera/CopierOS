# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from .base import EquipmentBaseModel


equipment_type_code_validator = RegexValidator(
    regex=r"^[A-Z0-9_]+$",
    message=(
        "El código solo puede contener letras mayúsculas, "
        "números y guiones bajos."
    ),
)


class EquipmentType(EquipmentBaseModel):
    """
    Catálogo de tipos de equipos.

    Ejemplos:

    - Fotocopiadora.
    - Impresora.
    - Multifuncional.
    - Duplicadora.
    - Plotter.
    - Escáner.
    - Impresora de producción.
    - Otro.

    Este catálogo permite agregar nuevos tipos sin modificar
    directamente el código del sistema.
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        validators=[
            equipment_type_code_validator,
        ],
        verbose_name="Código",
        help_text=(
            "Código interno único. "
            "Ejemplo: PHOTOCOPIER, PRINTER o PLOTTER."
        ),
    )

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Nombre",
        help_text="Nombre visible del tipo de equipo.",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    requires_color_definition = models.BooleanField(
        default=True,
        verbose_name="Requiere definir capacidad de color",
        help_text=(
            "Indica si al registrar un equipo de este tipo "
            "se debe especificar si es monocromático o color."
        ),
    )

    requires_meter = models.BooleanField(
        default=True,
        verbose_name="Requiere contador",
        help_text=(
            "Indica si los equipos de este tipo manejan "
            "lecturas de contador."
        ),
    )

    allows_accessories = models.BooleanField(
        default=True,
        verbose_name="Permite accesorios",
        help_text=(
            "Indica si este tipo de equipo puede tener accesorios "
            "o unidades técnicas asignadas."
        ),
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activo",
        help_text=(
            "Los tipos inactivos no deben mostrarse para nuevos equipos, "
            "pero se conservan en los registros existentes."
        ),
    )

    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Orden de visualización",
    )

    class Meta:
        verbose_name = "Tipo de equipo"
        verbose_name_plural = "Tipos de equipos"
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
                name="equip_type_active_order_idx",
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
                    "code": "El código del tipo de equipo es obligatorio.",
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": "El nombre del tipo de equipo es obligatorio.",
                }
            )

        duplicate_code = EquipmentType.objects.filter(
            code__iexact=self.code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe un tipo de equipo registrado "
                        "con este código."
                    ),
                }
            )

        duplicate_name = EquipmentType.objects.filter(
            name__iexact=self.name,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_name.exists():
            raise ValidationError(
                {
                    "name": (
                        "Ya existe un tipo de equipo registrado "
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