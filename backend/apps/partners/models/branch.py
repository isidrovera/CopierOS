# -*- coding: utf-8 -*-
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models
from django.db.models import Q

from .base import PartnerBaseModel
from .partner import Partner


phone_validator = RegexValidator(
    regex=r"^\+?[0-9\s\-()]{6,25}$",
    message="Ingresa un número telefónico válido.",
)


class PartnerBranch(PartnerBaseModel):
    """
    Sucursal, sede, oficina, almacén, proyecto u otra ubicación
    perteneciente a un cliente, proveedor o distribuidor.

    Una misma empresa puede tener varias sedes y cada una puede
    utilizarse posteriormente en contratos, instalaciones,
    servicios técnicos, entregas y facturación.
    """

    TYPE_MAIN = "main"
    TYPE_BRANCH = "branch"
    TYPE_OFFICE = "office"
    TYPE_WAREHOUSE = "warehouse"
    TYPE_PROJECT = "project"
    TYPE_WORKSITE = "worksite"
    TYPE_STORE = "store"
    TYPE_PLANT = "plant"
    TYPE_WORKSHOP = "workshop"
    TYPE_OTHER = "other"

    BRANCH_TYPE_CHOICES = (
        (
            TYPE_MAIN,
            "Sede principal",
        ),
        (
            TYPE_BRANCH,
            "Sucursal",
        ),
        (
            TYPE_OFFICE,
            "Oficina",
        ),
        (
            TYPE_WAREHOUSE,
            "Almacén",
        ),
        (
            TYPE_PROJECT,
            "Proyecto",
        ),
        (
            TYPE_WORKSITE,
            "Obra",
        ),
        (
            TYPE_STORE,
            "Local",
        ),
        (
            TYPE_PLANT,
            "Planta",
        ),
        (
            TYPE_WORKSHOP,
            "Taller",
        ),
        (
            TYPE_OTHER,
            "Otro",
        ),
    )

    partner = models.ForeignKey(
        Partner,
        on_delete=models.PROTECT,
        related_name="branches",
        verbose_name="Cliente, proveedor o distribuidor",
    )

    code = models.CharField(
        max_length=30,
        blank=True,
        db_index=True,
        verbose_name="Código de sede",
        help_text=(
            "Código interno utilizado para identificar la sede."
        ),
    )

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="Nombre de la sede",
        help_text=(
            "Ejemplo: Sede principal, Proyecto Ica "
            "o Almacén Callao."
        ),
    )

    branch_type = models.CharField(
        max_length=30,
        choices=BRANCH_TYPE_CHOICES,
        default=TYPE_BRANCH,
        db_index=True,
        verbose_name="Tipo de sede",
    )

    is_main = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Sede principal",
    )

    is_fiscal = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Dirección fiscal",
        help_text=(
            "Indica si esta ubicación representa "
            "el domicilio fiscal del tercero."
        ),
    )

    allows_equipment_installation = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Permite instalación de equipos",
        help_text=(
            "Permite seleccionar esta sede en contratos "
            "e instalaciones de equipos."
        ),
    )

    allows_deliveries = models.BooleanField(
        default=True,
        verbose_name="Permite entregas",
    )

    advisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_partner_branches",
        verbose_name="Asesora responsable de la sede",
        help_text=(
            "Si se deja vacío, se utilizará la asesora "
            "principal del cliente."
        ),
    )

    country_code = models.CharField(
        max_length=2,
        default="PE",
        db_index=True,
        verbose_name="Código del país",
        help_text=(
            "Código ISO de dos letras. Por ejemplo: PE o US."
        ),
    )

    country_name = models.CharField(
        max_length=100,
        default="Perú",
        verbose_name="País",
    )

    address = models.TextField(
        verbose_name="Dirección completa",
    )

    address_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Referencia",
    )

    ubigeo = models.CharField(
        max_length=10,
        blank=True,
        db_index=True,
        verbose_name="Ubigeo",
    )

    road_type = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Tipo de vía",
    )

    road_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre de vía",
    )

    zone_code = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Código de zona",
    )

    zone_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tipo o nombre de zona",
    )

    address_number = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Número",
    )

    interior = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Interior",
    )

    lot = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Lote",
    )

    apartment = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Departamento del inmueble",
    )

    block = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Manzana",
    )

    kilometer = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Kilómetro",
    )

    district = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Distrito o ciudad",
    )

    province = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Provincia o condado",
    )

    region = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Departamento, región o estado",
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Código postal",
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(
                Decimal("-90"),
            ),
            MaxValueValidator(
                Decimal("90"),
            ),
        ],
        verbose_name="Latitud",
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(
                Decimal("-180"),
            ),
            MaxValueValidator(
                Decimal("180"),
            ),
        ],
        verbose_name="Longitud",
    )

    general_phone = models.CharField(
        max_length=25,
        blank=True,
        validators=[
            phone_validator,
        ],
        verbose_name="Teléfono de la sede",
    )

    mobile_phone = models.CharField(
        max_length=25,
        blank=True,
        validators=[
            phone_validator,
        ],
        verbose_name="Celular de la sede",
    )

    general_email = models.EmailField(
        blank=True,
        verbose_name="Correo de la sede",
    )

    operating_hours = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Horario de atención",
        help_text=(
            "Ejemplo: lunes a viernes de 08:00 a 17:00."
        ),
    )

    access_instructions = models.TextField(
        blank=True,
        verbose_name="Indicaciones de acceso",
        help_text=(
            "Requisitos de ingreso, puertas de acceso, "
            "personas de autorización u otras indicaciones."
        ),
    )

    installation_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones para instalaciones",
        help_text=(
            "Información útil para instalar o retirar equipos."
        ),
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de inicio",
        help_text=(
            "Puede utilizarse en proyectos, obras "
            "o sedes temporales."
        ),
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de finalización",
        help_text=(
            "Puede utilizarse en proyectos, obras "
            "o sedes temporales."
        ),
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activa",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Sucursal o sede"
        verbose_name_plural = "Sucursales y sedes"

        ordering = (
            "partner",
            "-is_main",
            "name",
        )

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "partner",
                    "code",
                ],
                condition=~Q(code=""),
                name="partners_unique_branch_code",
            ),
            models.UniqueConstraint(
                fields=[
                    "partner",
                ],
                condition=Q(
                    is_main=True,
                    archived_at__isnull=True,
                ),
                name="partners_unique_main_branch",
            ),
            models.UniqueConstraint(
                fields=[
                    "partner",
                ],
                condition=Q(
                    is_fiscal=True,
                    archived_at__isnull=True,
                ),
                name="partners_unique_fiscal_branch",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "partner",
                    "is_active",
                ],
                name="partners_branch_active_idx",
            ),
            models.Index(
                fields=[
                    "partner",
                    "branch_type",
                ],
                name="partners_branch_type_idx",
            ),
            models.Index(
                fields=[
                    "district",
                    "province",
                    "region",
                ],
                name="partners_branch_location_idx",
            ),
            models.Index(
                fields=[
                    "allows_equipment_installation",
                    "is_active",
                ],
                name="partners_branch_install_idx",
            ),
        ]

    def clean(self):
        """
        Valida la información y coherencia de la sede.
        """

        super().clean()

        errors = {}

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.name = str(
            self.name or ""
        ).strip()

        self.country_code = str(
            self.country_code or ""
        ).strip().upper()

        self.country_name = str(
            self.country_name or ""
        ).strip()

        self.address = str(
            self.address or ""
        ).strip()

        self.general_email = str(
            self.general_email or ""
        ).strip().lower()

        if not self.name:
            errors["name"] = (
                "Debes ingresar el nombre de la sede."
            )

        if not self.country_code:
            errors["country_code"] = (
                "Debes seleccionar el país."
            )

        if len(self.country_code) != 2:
            errors["country_code"] = (
                "El código del país debe contener "
                "exactamente dos letras."
            )

        if not self.country_name:
            errors["country_name"] = (
                "Debes ingresar el nombre del país."
            )

        if not self.address:
            errors["address"] = (
                "Debes ingresar la dirección de la sede."
            )

        if (
            self.country_code == "PE"
            and self.ubigeo
            and (
                not self.ubigeo.isdigit()
                or len(self.ubigeo) != 6
            )
        ):
            errors["ubigeo"] = (
                "El ubigeo peruano debe contener "
                "exactamente 6 números."
            )

        if (
            self.end_date
            and self.start_date
            and self.end_date < self.start_date
        ):
            errors["end_date"] = (
                "La fecha de finalización no puede ser "
                "anterior a la fecha de inicio."
            )

        if self.branch_type == self.TYPE_MAIN:
            self.is_main = True

        if self.is_main:
            self.branch_type = self.TYPE_MAIN

        if (
            self.partner_id
            and self.is_main
        ):
            duplicated_main = (
                PartnerBranch.objects.filter(
                    partner_id=self.partner_id,
                    is_main=True,
                    archived_at__isnull=True,
                )
                .exclude(
                    pk=self.pk,
                )
                .exists()
            )

            if duplicated_main:
                errors["is_main"] = (
                    "Este tercero ya tiene una sede principal."
                )

        if (
            self.partner_id
            and self.is_fiscal
        ):
            duplicated_fiscal = (
                PartnerBranch.objects.filter(
                    partner_id=self.partner_id,
                    is_fiscal=True,
                    archived_at__isnull=True,
                )
                .exclude(
                    pk=self.pk,
                )
                .exists()
            )

            if duplicated_fiscal:
                errors["is_fiscal"] = (
                    "Este tercero ya tiene una dirección fiscal."
                )

        if errors:
            raise ValidationError(errors)

    @property
    def effective_advisor(self):
        """
        Devuelve la responsable asignada a la sede.

        Si la sede no tiene una responsable propia,
        utiliza la asesora principal del tercero.
        """

        return (
            self.advisor
            or self.partner.advisor
        )

    @property
    def display_name(self):
        """
        Devuelve el nombre completo para listas y selectores.
        """

        return (
            f"{self.partner.display_name} - {self.name}"
        )

    @property
    def is_temporary(self):
        """
        Indica si corresponde a una ubicación temporal.
        """

        return self.branch_type in (
            self.TYPE_PROJECT,
            self.TYPE_WORKSITE,
        )

    @property
    def coordinates(self):
        """
        Devuelve las coordenadas cuando ambas están disponibles.
        """

        if (
            self.latitude is None
            or self.longitude is None
        ):
            return None

        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    def save(
        self,
        *args,
        **kwargs,
    ):
        """
        Normaliza y valida la sede antes de guardarla.
        """

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
        Archiva la sede y la marca como inactiva.
        """

        self.is_active = False

        super().archive(
            user=user,
            reason=reason,
            save=False,
        )

        if save:
            self.save(
                update_fields=[
                    "is_active",
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                    "updated_by",
                    "updated_at",
                ]
            )

        return self

    def restore(
        self,
        user=None,
        save=True,
    ):
        """
        Restaura la sede y la marca como activa.
        """

        self.is_active = True

        super().restore(
            user=user,
            save=False,
        )

        if save:
            self.save(
                update_fields=[
                    "is_active",
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                    "updated_by",
                    "updated_at",
                ]
            )

        return self

    def __str__(self):
        return self.display_name