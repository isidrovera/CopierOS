# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q

from .base import PartnerBaseModel
from .branch import PartnerBranch
from .partner import Partner


phone_validator = RegexValidator(
    regex=r"^\+?[0-9\s\-()]{6,25}$",
    message="Ingresa un número telefónico válido.",
)


class PartnerContact(PartnerBaseModel):
    """
    Persona de contacto vinculada con un cliente, proveedor
    o distribuidor.

    Un contacto puede cumplir varias funciones al mismo tiempo,
    por ejemplo:

    - Contacto principal.
    - Representante legal.
    - Responsable de facturación.
    - Responsable técnico.
    - Responsable de contadores.
    - Responsable de cobranzas.
    - Responsable de logística.
    """

    DOCUMENT_DNI = "dni"
    DOCUMENT_FOREIGN_ID = "foreign_id"
    DOCUMENT_PASSPORT = "passport"
    DOCUMENT_OTHER = "other"

    DOCUMENT_TYPE_CHOICES = (
        (
            DOCUMENT_DNI,
            "DNI",
        ),
        (
            DOCUMENT_FOREIGN_ID,
            "Documento de identidad extranjero",
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

    AREA_MANAGEMENT = "management"
    AREA_ADMINISTRATION = "administration"
    AREA_ACCOUNTING = "accounting"
    AREA_BILLING = "billing"
    AREA_TREASURY = "treasury"
    AREA_COLLECTIONS = "collections"
    AREA_PURCHASING = "purchasing"
    AREA_LOGISTICS = "logistics"
    AREA_SYSTEMS = "systems"
    AREA_TECHNICAL = "technical"
    AREA_OPERATIONS = "operations"
    AREA_HUMAN_RESOURCES = "human_resources"
    AREA_LEGAL = "legal"
    AREA_COMMERCIAL = "commercial"
    AREA_OTHER = "other"

    AREA_CHOICES = (
        (
            AREA_MANAGEMENT,
            "Gerencia",
        ),
        (
            AREA_ADMINISTRATION,
            "Administración",
        ),
        (
            AREA_ACCOUNTING,
            "Contabilidad",
        ),
        (
            AREA_BILLING,
            "Facturación",
        ),
        (
            AREA_TREASURY,
            "Tesorería",
        ),
        (
            AREA_COLLECTIONS,
            "Cobranzas",
        ),
        (
            AREA_PURCHASING,
            "Compras",
        ),
        (
            AREA_LOGISTICS,
            "Logística",
        ),
        (
            AREA_SYSTEMS,
            "Sistemas",
        ),
        (
            AREA_TECHNICAL,
            "Área técnica",
        ),
        (
            AREA_OPERATIONS,
            "Operaciones",
        ),
        (
            AREA_HUMAN_RESOURCES,
            "Recursos humanos",
        ),
        (
            AREA_LEGAL,
            "Área legal",
        ),
        (
            AREA_COMMERCIAL,
            "Área comercial",
        ),
        (
            AREA_OTHER,
            "Otra área",
        ),
    )

    partner = models.ForeignKey(
        Partner,
        on_delete=models.PROTECT,
        related_name="contacts",
        verbose_name="Cliente, proveedor o distribuidor",
    )

    branch = models.ForeignKey(
        PartnerBranch,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="contacts",
        verbose_name="Sucursal o sede",
        help_text=(
            "Puede dejarse vacío cuando el contacto "
            "corresponde a toda la empresa."
        ),
    )

    document_type = models.CharField(
        max_length=30,
        choices=DOCUMENT_TYPE_CHOICES,
        blank=True,
        verbose_name="Tipo de documento",
    )

    document_number = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Número de documento",
    )

    first_names = models.CharField(
        max_length=150,
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

    job_title = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Cargo",
        help_text=(
            "Ejemplo: jefe de sistemas, administradora "
            "o asistente de logística."
        ),
    )

    area = models.CharField(
        max_length=30,
        choices=AREA_CHOICES,
        default=AREA_OTHER,
        db_index=True,
        verbose_name="Área",
    )

    primary_email = models.EmailField(
        blank=True,
        db_index=True,
        verbose_name="Correo principal",
    )

    secondary_email = models.EmailField(
        blank=True,
        verbose_name="Correo secundario",
    )

    work_phone = models.CharField(
        max_length=25,
        blank=True,
        validators=[
            phone_validator,
        ],
        verbose_name="Teléfono de trabajo",
    )

    work_extension = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Anexo",
    )

    primary_mobile = models.CharField(
        max_length=25,
        blank=True,
        validators=[
            phone_validator,
        ],
        verbose_name="Celular principal",
    )

    secondary_mobile = models.CharField(
        max_length=25,
        blank=True,
        validators=[
            phone_validator,
        ],
        verbose_name="Celular secundario",
    )

    whatsapp_number = models.CharField(
        max_length=25,
        blank=True,
        validators=[
            phone_validator,
        ],
        verbose_name="Número de WhatsApp",
    )

    has_whatsapp = models.BooleanField(
        default=False,
        verbose_name="Tiene WhatsApp",
    )

    is_primary = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Contacto principal",
        help_text=(
            "Solo puede existir un contacto principal "
            "activo por tercero."
        ),
    )

    is_legal_representative = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Representante legal",
    )

    is_branch_manager = models.BooleanField(
        default=False,
        verbose_name="Responsable de sede",
    )

    receives_contracts = models.BooleanField(
        default=False,
        verbose_name="Recibe contratos",
    )

    receives_billing = models.BooleanField(
        default=False,
        verbose_name="Recibe facturación",
    )

    receives_collections = models.BooleanField(
        default=False,
        verbose_name="Recibe cobranzas",
    )

    receives_purchase_orders = models.BooleanField(
        default=False,
        verbose_name="Recibe órdenes de compra",
    )

    receives_delivery_documents = models.BooleanField(
        default=False,
        verbose_name="Recibe guías y documentos de entrega",
    )

    receives_meter_requests = models.BooleanField(
        default=False,
        verbose_name="Recibe solicitudes de contadores",
    )

    receives_service_notifications = models.BooleanField(
        default=False,
        verbose_name="Recibe notificaciones de servicio",
    )

    receives_incident_notifications = models.BooleanField(
        default=False,
        verbose_name="Recibe notificaciones de incidencias",
    )

    receives_commercial_notifications = models.BooleanField(
        default=False,
        verbose_name="Recibe comunicaciones comerciales",
    )

    can_authorize_equipment_entry = models.BooleanField(
        default=False,
        verbose_name="Autoriza ingreso de equipos",
    )

    can_authorize_equipment_removal = models.BooleanField(
        default=False,
        verbose_name="Autoriza retiro de equipos",
    )

    can_sign_documents = models.BooleanField(
        default=False,
        verbose_name="Puede firmar documentos",
    )

    preferred_contact_method = models.CharField(
        max_length=20,
        choices=(
            (
                "email",
                "Correo electrónico",
            ),
            (
                "phone",
                "Teléfono",
            ),
            (
                "mobile",
                "Celular",
            ),
            (
                "whatsapp",
                "WhatsApp",
            ),
        ),
        default="email",
        verbose_name="Medio de contacto preferido",
    )

    contact_schedule = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Horario de contacto",
        help_text=(
            "Ejemplo: lunes a viernes de 09:00 a 17:00."
        ),
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
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"

        ordering = (
            "partner",
            "-is_primary",
            "first_names",
            "paternal_last_name",
        )

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "partner",
                ],
                condition=Q(
                    is_primary=True,
                    is_active=True,
                    archived_at__isnull=True,
                ),
                name="partners_unique_primary_contact",
            ),
            models.UniqueConstraint(
                fields=[
                    "partner",
                    "document_type",
                    "document_number",
                ],
                condition=(
                    ~Q(document_type="")
                    & ~Q(document_number="")
                ),
                name="partners_unique_contact_document",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "partner",
                    "is_active",
                ],
                name="partners_contact_active_idx",
            ),
            models.Index(
                fields=[
                    "partner",
                    "area",
                ],
                name="partners_contact_area_idx",
            ),
            models.Index(
                fields=[
                    "branch",
                    "is_active",
                ],
                name="partners_contact_branch_idx",
            ),
            models.Index(
                fields=[
                    "receives_billing",
                    "is_active",
                ],
                name="partners_contact_billing_idx",
            ),
            models.Index(
                fields=[
                    "receives_service_notifications",
                    "is_active",
                ],
                name="partners_contact_service_idx",
            ),
        ]

    def clean(self):
        """
        Valida la coherencia y pertenencia del contacto.
        """

        super().clean()

        errors = {}

        self.document_number = str(
            self.document_number or ""
        ).replace(" ", "").strip().upper()

        self.first_names = str(
            self.first_names or ""
        ).strip()

        self.paternal_last_name = str(
            self.paternal_last_name or ""
        ).strip()

        self.maternal_last_name = str(
            self.maternal_last_name or ""
        ).strip()

        self.job_title = str(
            self.job_title or ""
        ).strip()

        self.primary_email = str(
            self.primary_email or ""
        ).strip().lower()

        self.secondary_email = str(
            self.secondary_email or ""
        ).strip().lower()

        self.work_extension = str(
            self.work_extension or ""
        ).strip()

        self.contact_schedule = str(
            self.contact_schedule or ""
        ).strip()

        if not self.first_names:
            errors["first_names"] = (
                "Debes ingresar los nombres del contacto."
            )

        if (
            self.document_type
            and not self.document_number
        ):
            errors["document_number"] = (
                "Debes ingresar el número de documento."
            )

        if (
            self.document_number
            and not self.document_type
        ):
            errors["document_type"] = (
                "Debes seleccionar el tipo de documento."
            )

        if self.document_type == self.DOCUMENT_DNI:
            if (
                not self.document_number.isdigit()
                or len(self.document_number) != 8
            ):
                errors["document_number"] = (
                    "El DNI debe contener exactamente "
                    "8 números."
                )

        if (
            self.branch_id
            and self.partner_id
            and self.branch.partner_id
            != self.partner_id
        ):
            errors["branch"] = (
                "La sede seleccionada no pertenece "
                "al tercero indicado."
            )

        if (
            self.is_branch_manager
            and not self.branch_id
        ):
            errors["branch"] = (
                "Para marcarlo como responsable de sede "
                "debes seleccionar una sucursal."
            )

        if (
            self.has_whatsapp
            and not self.whatsapp_number
        ):
            errors["whatsapp_number"] = (
                "Debes ingresar el número de WhatsApp."
            )

        if (
            self.whatsapp_number
            and not self.has_whatsapp
        ):
            self.has_whatsapp = True

        if (
            self.preferred_contact_method == "email"
            and not self.primary_email
        ):
            errors["primary_email"] = (
                "Debes ingresar un correo principal "
                "para usarlo como medio preferido."
            )

        if (
            self.preferred_contact_method == "phone"
            and not self.work_phone
        ):
            errors["work_phone"] = (
                "Debes ingresar un teléfono de trabajo "
                "para usarlo como medio preferido."
            )

        if (
            self.preferred_contact_method == "mobile"
            and not self.primary_mobile
        ):
            errors["primary_mobile"] = (
                "Debes ingresar un celular principal "
                "para usarlo como medio preferido."
            )

        if (
            self.preferred_contact_method == "whatsapp"
            and not self.whatsapp_number
        ):
            errors["whatsapp_number"] = (
                "Debes ingresar un número de WhatsApp "
                "para usarlo como medio preferido."
            )

        requires_email = any(
            (
                self.receives_contracts,
                self.receives_billing,
                self.receives_collections,
                self.receives_purchase_orders,
                self.receives_delivery_documents,
                self.receives_meter_requests,
                self.receives_service_notifications,
                self.receives_incident_notifications,
                self.receives_commercial_notifications,
            )
        )

        if (
            requires_email
            and not self.primary_email
        ):
            errors["primary_email"] = (
                "Este contacto recibe comunicaciones, "
                "por lo que debe tener un correo principal."
            )

        if (
            self.partner_id
            and self.is_primary
            and self.is_active
            and not self.archived_at
        ):
            duplicated_primary = (
                PartnerContact.objects.filter(
                    partner_id=self.partner_id,
                    is_primary=True,
                    is_active=True,
                    archived_at__isnull=True,
                )
                .exclude(
                    pk=self.pk,
                )
                .exists()
            )

            if duplicated_primary:
                errors["is_primary"] = (
                    "Este tercero ya tiene un contacto "
                    "principal activo."
                )

        if errors:
            raise ValidationError(errors)

    @property
    def full_name(self):
        """
        Devuelve el nombre completo del contacto.
        """

        return " ".join(
            value
            for value in (
                self.first_names,
                self.paternal_last_name,
                self.maternal_last_name,
            )
            if value
        ).strip()

    @property
    def display_name(self):
        """
        Devuelve el nombre mostrado en listas y selectores.
        """

        name = self.full_name

        if self.job_title:
            return (
                f"{name} - {self.job_title}"
            )

        return name

    @property
    def effective_branch(self):
        """
        Devuelve la sede del contacto cuando está asignada.
        """

        return self.branch

    @property
    def notification_roles(self):
        """
        Devuelve las funciones de notificación habilitadas.
        """

        roles = []

        if self.receives_contracts:
            roles.append("Contratos")

        if self.receives_billing:
            roles.append("Facturación")

        if self.receives_collections:
            roles.append("Cobranzas")

        if self.receives_purchase_orders:
            roles.append("Órdenes de compra")

        if self.receives_delivery_documents:
            roles.append("Guías y entregas")

        if self.receives_meter_requests:
            roles.append("Contadores")

        if self.receives_service_notifications:
            roles.append("Servicio técnico")

        if self.receives_incident_notifications:
            roles.append("Incidencias")

        if self.receives_commercial_notifications:
            roles.append("Comercial")

        return roles

    @property
    def available_email(self):
        """
        Devuelve el primer correo disponible.
        """

        return (
            self.primary_email
            or self.secondary_email
            or ""
        )

    @property
    def available_phone(self):
        """
        Devuelve el primer teléfono disponible.
        """

        return (
            self.primary_mobile
            or self.whatsapp_number
            or self.work_phone
            or self.secondary_mobile
            or ""
        )

    def save(
        self,
        *args,
        **kwargs,
    ):
        """
        Normaliza y valida el contacto antes de guardar.
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
        Archiva el contacto y lo marca como inactivo.
        """

        self.is_active = False
        self.is_primary = False

        super().archive(
            user=user,
            reason=reason,
            save=False,
        )

        if save:
            self.save(
                update_fields=[
                    "is_active",
                    "is_primary",
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
        Restaura el contacto.

        No lo establece automáticamente como contacto principal,
        porque podría existir otro contacto principal activo.
        """

        self.is_active = True
        self.is_primary = False

        super().restore(
            user=user,
            save=False,
        )

        if save:
            self.save(
                update_fields=[
                    "is_active",
                    "is_primary",
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
            f"{self.display_name} - "
            f"{self.partner.display_name}"
        )