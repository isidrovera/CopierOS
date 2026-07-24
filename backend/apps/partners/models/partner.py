# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q

from .base import PartnerBaseModel


document_number_validator = RegexValidator(
    regex=r"^[A-Za-z0-9.\-_/]+$",
    message=(
        "El número de documento solo puede contener letras, "
        "números, puntos, guiones, barras o guion bajo."
    ),
)

phone_validator = RegexValidator(
    regex=r"^\+?[0-9\s\-()]{6,25}$",
    message="Ingresa un número telefónico válido.",
)

country_code_validator = RegexValidator(
    regex=r"^[A-Z]{2}$",
    message=(
        "El código del país debe contener exactamente "
        "dos letras mayúsculas."
    ),
)


class Partner(PartnerBaseModel):
    """
    Persona o empresa relacionada comercialmente con Copier OS.

    Un mismo registro puede cumplir uno o varios roles:

    - Cliente de alquiler.
    - Cliente de venta.
    - Cliente de servicio técnico.
    - Proveedor.
    - Distribuidor.

    También admite entidades nacionales y extranjeras.
    """

    PERSON_NATURAL = "natural"
    PERSON_LEGAL = "legal"

    PERSON_TYPE_CHOICES = (
        (
            PERSON_NATURAL,
            "Persona natural",
        ),
        (
            PERSON_LEGAL,
            "Persona jurídica",
        ),
    )

    DOCUMENT_DNI = "dni"
    DOCUMENT_RUC = "ruc"
    DOCUMENT_FOREIGN_ID = "foreign_id"
    DOCUMENT_EIN = "ein"
    DOCUMENT_TAX_ID = "tax_id"
    DOCUMENT_REGISTRATION = "registration"
    DOCUMENT_PASSPORT = "passport"
    DOCUMENT_OTHER = "other"

    DOCUMENT_TYPE_CHOICES = (
        (
            DOCUMENT_DNI,
            "DNI",
        ),
        (
            DOCUMENT_RUC,
            "RUC",
        ),
        (
            DOCUMENT_FOREIGN_ID,
            "Documento de identidad extranjero",
        ),
        (
            DOCUMENT_EIN,
            "EIN",
        ),
        (
            DOCUMENT_TAX_ID,
            "Tax ID",
        ),
        (
            DOCUMENT_REGISTRATION,
            "Número de registro empresarial",
        ),
        (
            DOCUMENT_PASSPORT,
            "Pasaporte",
        ),
        (
            DOCUMENT_OTHER,
            "Otro documento",
        ),
    )

    CLASSIFICATION_CORPORATE = "corporate"
    CLASSIFICATION_SMALL_BUSINESS = "small_business"
    CLASSIFICATION_GOVERNMENT = "government"
    CLASSIFICATION_EDUCATION = "education"
    CLASSIFICATION_HEALTH = "health"
    CLASSIFICATION_INDEPENDENT = "independent"
    CLASSIFICATION_OTHER = "other"

    CLASSIFICATION_CHOICES = (
        (
            CLASSIFICATION_CORPORATE,
            "Corporativo",
        ),
        (
            CLASSIFICATION_SMALL_BUSINESS,
            "Pequeña y mediana empresa",
        ),
        (
            CLASSIFICATION_GOVERNMENT,
            "Entidad pública",
        ),
        (
            CLASSIFICATION_EDUCATION,
            "Institución educativa",
        ),
        (
            CLASSIFICATION_HEALTH,
            "Institución de salud",
        ),
        (
            CLASSIFICATION_INDEPENDENT,
            "Independiente",
        ),
        (
            CLASSIFICATION_OTHER,
            "Otro",
        ),
    )

    CURRENCY_PEN = "PEN"
    CURRENCY_USD = "USD"
    CURRENCY_EUR = "EUR"
    CURRENCY_OTHER = "OTHER"

    CURRENCY_CHOICES = (
        (
            CURRENCY_PEN,
            "Soles",
        ),
        (
            CURRENCY_USD,
            "Dólares estadounidenses",
        ),
        (
            CURRENCY_EUR,
            "Euros",
        ),
        (
            CURRENCY_OTHER,
            "Otra moneda",
        ),
    )

    DOCUMENT_SOURCE_MANUAL = "manual"
    DOCUMENT_SOURCE_SUNAT = "sunat"
    DOCUMENT_SOURCE_OTHER = "other"

    DOCUMENT_SOURCE_CHOICES = (
        (
            DOCUMENT_SOURCE_MANUAL,
            "Registro manual",
        ),
        (
            DOCUMENT_SOURCE_SUNAT,
            "Consulta SUNAT",
        ),
        (
            DOCUMENT_SOURCE_OTHER,
            "Otra fuente",
        ),
    )

    code = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Código interno",
        help_text=(
            "Código interno generado o asignado al tercero."
        ),
    )

    person_type = models.CharField(
        max_length=20,
        choices=PERSON_TYPE_CHOICES,
        default=PERSON_LEGAL,
        db_index=True,
        verbose_name="Tipo de persona",
    )

    country_code = models.CharField(
        max_length=2,
        default="PE",
        validators=[
            country_code_validator,
        ],
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

    document_type = models.CharField(
        max_length=30,
        choices=DOCUMENT_TYPE_CHOICES,
        db_index=True,
        verbose_name="Tipo de documento",
    )

    document_number = models.CharField(
        max_length=50,
        validators=[
            document_number_validator,
        ],
        db_index=True,
        verbose_name="Número de documento",
    )

    legal_name = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Razón social",
    )

    trade_name = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Nombre comercial",
    )

    first_names = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nombres",
    )

    paternal_last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Apellido paterno",
    )

    maternal_last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Apellido materno",
    )

    classification = models.CharField(
        max_length=30,
        choices=CLASSIFICATION_CHOICES,
        default=CLASSIFICATION_OTHER,
        db_index=True,
        verbose_name="Clasificación",
    )

    is_rental_customer = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Cliente de alquiler",
    )

    is_sales_customer = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Cliente de venta",
    )

    is_service_customer = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Cliente de servicio técnico",
    )

    is_supplier = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Proveedor",
    )

    is_distributor = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Distribuidor",
    )

    advisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_partners",
        verbose_name="Asesora o responsable comercial",
    )

    purchasing_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="managed_supplier_partners",
        verbose_name="Responsable de compras",
    )

    general_phone = models.CharField(
        max_length=25,
        blank=True,
        validators=[
            phone_validator,
        ],
        verbose_name="Teléfono general",
    )

    mobile_phone = models.CharField(
        max_length=25,
        blank=True,
        validators=[
            phone_validator,
        ],
        verbose_name="Celular general",
    )

    general_email = models.EmailField(
        blank=True,
        verbose_name="Correo general",
    )

    billing_email = models.EmailField(
        blank=True,
        verbose_name="Correo de facturación",
    )

    website = models.URLField(
        max_length=255,
        blank=True,
        verbose_name="Página web",
    )

    fiscal_address = models.TextField(
        blank=True,
        verbose_name="Dirección fiscal",
    )

    address_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Referencia de dirección",
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
        verbose_name="Número de inmueble",
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
        verbose_name="Departamento de inmueble",
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

    sunat_status = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Estado SUNAT",
    )

    sunat_condition = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Condición SUNAT",
    )

    taxpayer_type = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Tipo de contribuyente",
    )

    economic_activity = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Actividad económica",
    )

    employee_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Número de trabajadores",
    )

    billing_type = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Tipo de facturación SUNAT",
    )

    accounting_type = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Tipo de contabilidad",
    )

    foreign_trade = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Comercio exterior",
    )

    is_withholding_agent = models.BooleanField(
        default=False,
        verbose_name="Es agente de retención",
    )

    document_source = models.CharField(
        max_length=20,
        choices=DOCUMENT_SOURCE_CHOICES,
        default=DOCUMENT_SOURCE_MANUAL,
        verbose_name="Origen de los datos",
    )

    document_verified = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Documento verificado",
    )

    document_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de verificación",
    )

    last_document_lookup_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última consulta del documento",
    )

    preferred_currency = models.CharField(
        max_length=10,
        choices=CURRENCY_CHOICES,
        default=CURRENCY_PEN,
        verbose_name="Moneda preferida",
    )

    preferred_language = models.CharField(
        max_length=10,
        default="es",
        verbose_name="Idioma preferido",
    )

    payment_terms = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Condición de pago",
    )

    credit_days = models.PositiveIntegerField(
        default=0,
        verbose_name="Días de crédito",
    )

    credit_limit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Límite de crédito",
    )

    requires_purchase_order = models.BooleanField(
        default=False,
        verbose_name="Requiere orden de compra",
    )

    requires_service_conformity = models.BooleanField(
        default=False,
        verbose_name="Requiere conformidad de servicio",
    )

    requires_delivery_guide = models.BooleanField(
        default=False,
        verbose_name="Requiere guía de remisión",
    )

    is_commercially_blocked = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Bloqueado comercialmente",
    )

    commercial_block_reason = models.TextField(
        blank=True,
        verbose_name="Motivo del bloqueo comercial",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activo",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Cliente, proveedor o distribuidor"
        verbose_name_plural = (
            "Clientes, proveedores y distribuidores"
        )

        ordering = (
            "legal_name",
            "trade_name",
            "first_names",
            "document_number",
        )

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "country_code",
                    "document_type",
                    "document_number",
                ],
                condition=~Q(document_number=""),
                name="partners_unique_document",
            ),
            models.CheckConstraint(
                condition=(
                    Q(is_rental_customer=True)
                    | Q(is_sales_customer=True)
                    | Q(is_service_customer=True)
                    | Q(is_supplier=True)
                    | Q(is_distributor=True)
                ),
                name="partners_requires_role",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "country_code",
                    "document_number",
                ],
                name="partners_country_doc_idx",
            ),
            models.Index(
                fields=[
                    "is_active",
                    "archived_at",
                ],
                name="partners_active_archive_idx",
            ),
            models.Index(
                fields=[
                    "advisor",
                    "is_active",
                ],
                name="partners_advisor_active_idx",
            ),
            models.Index(
                fields=[
                    "sunat_status",
                    "sunat_condition",
                ],
                name="partners_sunat_status_idx",
            ),
        ]

    def clean(self):
        """
        Valida la coherencia de los datos del tercero.
        """

        super().clean()

        errors = {}

        self.country_code = str(
            self.country_code or ""
        ).strip().upper()

        self.country_name = str(
            self.country_name or ""
        ).strip()

        self.document_number = str(
            self.document_number or ""
        ).replace(" ", "").strip().upper()

        self.legal_name = str(
            self.legal_name or ""
        ).strip()

        self.trade_name = str(
            self.trade_name or ""
        ).strip()

        self.first_names = str(
            self.first_names or ""
        ).strip()

        self.paternal_last_name = str(
            self.paternal_last_name or ""
        ).strip()

        self.maternal_last_name = str(
            self.maternal_last_name or ""
        ).strip()

        self.general_email = str(
            self.general_email or ""
        ).strip().lower()

        self.billing_email = str(
            self.billing_email or ""
        ).strip().lower()

        if not self.country_code:
            errors["country_code"] = (
                "Debes seleccionar el país."
            )

        if not self.country_name:
            errors["country_name"] = (
                "Debes ingresar el nombre del país."
            )

        if not self.document_type:
            errors["document_type"] = (
                "Debes seleccionar el tipo de documento."
            )

        if not self.document_number:
            errors["document_number"] = (
                "Debes ingresar el número de documento."
            )

        if self.country_code == "PE":
            self._validate_peruvian_document(
                errors
            )
        else:
            self._validate_foreign_document(
                errors
            )

        if self.person_type == self.PERSON_LEGAL:
            if not self.legal_name:
                errors["legal_name"] = (
                    "La razón social es obligatoria "
                    "para una persona jurídica."
                )

        if self.person_type == self.PERSON_NATURAL:
            if not self.first_names:
                errors["first_names"] = (
                    "Los nombres son obligatorios "
                    "para una persona natural."
                )

            if not self.paternal_last_name:
                errors["paternal_last_name"] = (
                    "El apellido paterno es obligatorio "
                    "para una persona natural."
                )

        if not self.has_commercial_role:
            errors["is_rental_customer"] = (
                "Debes seleccionar al menos un tipo: "
                "cliente, proveedor o distribuidor."
            )

        if (
            self.requires_advisor
            and not self.advisor
        ):
            errors["advisor"] = (
                "Debes asignar una asesora o responsable "
                "comercial a este cliente."
            )

        if (
            self.is_supplier
            and not self.requires_advisor
            and not self.purchasing_manager
        ):
            errors["purchasing_manager"] = (
                "Debes asignar un responsable de compras "
                "al proveedor."
            )

        if (
            self.is_commercially_blocked
            and not self.commercial_block_reason
        ):
            errors["commercial_block_reason"] = (
                "Debes indicar el motivo del bloqueo comercial."
            )

        if errors:
            raise ValidationError(errors)

    def _validate_peruvian_document(
        self,
        errors,
    ):
        """
        Valida documentos utilizados en Perú.
        """

        if self.document_type == self.DOCUMENT_DNI:
            if (
                not self.document_number.isdigit()
                or len(self.document_number) != 8
            ):
                errors["document_number"] = (
                    "El DNI debe contener exactamente "
                    "8 números."
                )

            if self.person_type != self.PERSON_NATURAL:
                errors["person_type"] = (
                    "Un registro con DNI debe ser "
                    "una persona natural."
                )

        elif self.document_type == self.DOCUMENT_RUC:
            if (
                not self.document_number.isdigit()
                or len(self.document_number) != 11
            ):
                errors["document_number"] = (
                    "El RUC debe contener exactamente "
                    "11 números."
                )

            elif not self.is_valid_peruvian_ruc(
                self.document_number
            ):
                errors["document_number"] = (
                    "El número de RUC no supera la "
                    "validación del dígito verificador."
                )

        elif self.document_type in (
            self.DOCUMENT_EIN,
            self.DOCUMENT_TAX_ID,
            self.DOCUMENT_REGISTRATION,
        ):
            errors["document_type"] = (
                "El tipo de documento seleccionado "
                "corresponde a una entidad extranjera."
            )

    def _validate_foreign_document(
        self,
        errors,
    ):
        """
        Valida documentos de entidades extranjeras.
        """

        if self.document_type in (
            self.DOCUMENT_DNI,
            self.DOCUMENT_RUC,
        ):
            errors["document_type"] = (
                "Para una entidad extranjera selecciona "
                "EIN, Tax ID, registro empresarial, "
                "pasaporte u otro documento."
            )

    @staticmethod
    def is_valid_peruvian_ruc(
        ruc,
    ):
        """
        Comprueba el dígito verificador de un RUC peruano.
        """

        value = str(ruc or "").strip()

        if (
            len(value) != 11
            or not value.isdigit()
        ):
            return False

        factors = (
            5,
            4,
            3,
            2,
            7,
            6,
            5,
            4,
            3,
            2,
        )

        total = sum(
            int(digit) * factor
            for digit, factor in zip(
                value[:10],
                factors,
            )
        )

        remainder = total % 11
        verifier = 11 - remainder

        if verifier == 10:
            verifier = 0
        elif verifier == 11:
            verifier = 1

        return verifier == int(
            value[-1]
        )

    @property
    def is_foreign(self):
        """
        Indica si el tercero pertenece a otro país.
        """

        return self.country_code != "PE"

    @property
    def has_commercial_role(self):
        """
        Indica si tiene al menos un tipo comercial.
        """

        return any(
            (
                self.is_rental_customer,
                self.is_sales_customer,
                self.is_service_customer,
                self.is_supplier,
                self.is_distributor,
            )
        )

    @property
    def requires_advisor(self):
        """
        Indica si debe tener asesora comercial.
        """

        return any(
            (
                self.is_rental_customer,
                self.is_sales_customer,
                self.is_service_customer,
                self.is_distributor,
            )
        )

    @property
    def display_name(self):
        """
        Devuelve el nombre que debe mostrarse en el sistema.
        """

        if self.person_type == self.PERSON_LEGAL:
            return (
                self.trade_name
                or self.legal_name
                or self.document_number
            )

        full_name = " ".join(
            value
            for value in (
                self.first_names,
                self.paternal_last_name,
                self.maternal_last_name,
            )
            if value
        ).strip()

        return (
            full_name
            or self.legal_name
            or self.document_number
        )

    @property
    def commercial_roles(self):
        """
        Devuelve los tipos comerciales activos.
        """

        roles = []

        if self.is_rental_customer:
            roles.append(
                "Cliente de alquiler"
            )

        if self.is_sales_customer:
            roles.append(
                "Cliente de venta"
            )

        if self.is_service_customer:
            roles.append(
                "Cliente de servicio técnico"
            )

        if self.is_supplier:
            roles.append(
                "Proveedor"
            )

        if self.is_distributor:
            roles.append(
                "Distribuidor"
            )

        return roles

    def save(
        self,
        *args,
        **kwargs,
    ):
        """
        Normaliza y valida los datos antes de guardar.
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
        Archiva el tercero y lo marca como inactivo.
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
        Restaura el tercero y lo marca como activo.
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
        return (
            f"{self.display_name} "
            f"({self.document_number})"
        )