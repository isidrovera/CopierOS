# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from .base import RentalsBaseModel


warehouse_code_validator = RegexValidator(
    regex=r"^[A-Z0-9_-]+$",
    message=(
        "El código solo puede contener letras mayúsculas, "
        "números, guiones y guiones bajos."
    ),
)


class RentalWarehouse(RentalsBaseModel):
    """
    Almacén físico de máquinas administradas por ANDES.

    Los almacenes permiten identificar dónde se encuentra
    cada máquina antes, durante o después de un alquiler.

    Ejemplos:

    - Almacén principal.
    - Zona de ingreso.
    - Zona de preparación.
    - Máquinas listas para alquiler.
    - Máquinas retiradas.
    - Máquinas con problemas.
    - Máquinas destinadas a partes.

    Este modelo controla almacenes de máquinas.

    No administra almacenes, precios ni stock de repuestos.
    """

    code = models.CharField(
        max_length=60,
        unique=True,
        db_index=True,
        validators=[
            warehouse_code_validator,
        ],
        verbose_name="Código",
        help_text=(
            "Código interno único del almacén. "
            "Ejemplo: ANDES_MAIN o ANDES_PREPARATION."
        ),
    )

    name = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        verbose_name="Nombre",
    )

    address = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Dirección",
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
            "Los almacenes inactivos no deben utilizarse "
            "para nuevos ingresos o movimientos."
        ),
    )

    allows_entries = models.BooleanField(
        default=True,
        verbose_name="Permite ingresos",
    )

    allows_dispatches = models.BooleanField(
        default=True,
        verbose_name="Permite salidas",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Orden de visualización",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Almacén de alquiler"
        verbose_name_plural = "Almacenes de alquiler"
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
                name="rent_warehouse_active_idx",
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.name = str(
            self.name or ""
        ).strip()

        self.address = str(
            self.address or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        if not self.code:
            raise ValidationError(
                {
                    "code": (
                        "El código del almacén es obligatorio."
                    ),
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": (
                        "El nombre del almacén es obligatorio."
                    ),
                }
            )

        duplicate_code = RentalWarehouse.objects.filter(
            code__iexact=self.code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe un almacén registrado "
                        "con este código."
                    ),
                }
            )

        duplicate_name = RentalWarehouse.objects.filter(
            name__iexact=self.name,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_name.exists():
            raise ValidationError(
                {
                    "name": (
                        "Ya existe un almacén registrado "
                        "con este nombre."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        self.code = str(
            self.code or ""
        ).strip().upper()

        self.name = str(
            self.name or ""
        ).strip()

        self.address = str(
            self.address or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )