# -*- coding: utf-8 -*-
import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import EquipmentBaseModel
from .equipment import Equipment


def equipment_document_path(instance, filename):
    """
    Guarda los documentos organizados por equipo.

    Ejemplo:

    equipment/machines/<uuid-equipo>/documents/<uuid-documento>.pdf
    """

    extension = os.path.splitext(
        filename
    )[1].lower()

    document_id = instance.id or uuid.uuid4()

    equipment_id = (
        instance.equipment_id
        if instance.equipment_id
        else "unassigned"
    )

    return (
        f"equipment/machines/"
        f"{equipment_id}/documents/"
        f"{document_id}{extension}"
    )


class EquipmentDocument(EquipmentBaseModel):
    """
    Documento relacionado con una máquina.

    Permite almacenar archivos como:

    - Invoice.
    - Factura de compra.
    - Factura de venta.
    - Guía de remisión.
    - Acta de entrega.
    - Acta de instalación.
    - Informe técnico.
    - Manual.
    - Ficha técnica.
    - Certificado.
    - Garantía.
    - Fotografías complementarias.
    - Documentos de importación.
    - Otros archivos.

    El documento puede estar relacionado con un proceso futuro
    mediante reference_type, reference_id y reference_number.
    """

    class DocumentType(models.TextChoices):
        PURCHASE_INVOICE = (
            "purchase_invoice",
            "Factura o invoice de compra",
        )
        SALE_INVOICE = (
            "sale_invoice",
            "Factura de venta",
        )
        IMPORT_DOCUMENT = (
            "import_document",
            "Documento de importación",
        )
        CUSTOMS_DOCUMENT = (
            "customs_document",
            "Documento aduanero",
        )
        PACKING_LIST = (
            "packing_list",
            "Lista de empaque",
        )
        SHIPPING_DOCUMENT = (
            "shipping_document",
            "Documento de transporte",
        )
        DELIVERY_NOTE = (
            "delivery_note",
            "Guía de remisión",
        )
        DELIVERY_CERTIFICATE = (
            "delivery_certificate",
            "Acta de entrega",
        )
        INSTALLATION_CERTIFICATE = (
            "installation_certificate",
            "Acta de instalación",
        )
        REMOVAL_CERTIFICATE = (
            "removal_certificate",
            "Acta de retiro",
        )
        TECHNICAL_REPORT = (
            "technical_report",
            "Informe técnico",
        )
        REPAIR_REPORT = (
            "repair_report",
            "Informe de reparación",
        )
        TECHNICAL_SHEET = (
            "technical_sheet",
            "Ficha técnica",
        )
        USER_MANUAL = (
            "user_manual",
            "Manual de usuario",
        )
        SERVICE_MANUAL = (
            "service_manual",
            "Manual de servicio",
        )
        WARRANTY = (
            "warranty",
            "Garantía",
        )
        CERTIFICATE = (
            "certificate",
            "Certificado",
        )
        CONTRACT = (
            "contract",
            "Contrato",
        )
        QUOTATION = (
            "quotation",
            "Cotización",
        )
        PURCHASE_ORDER = (
            "purchase_order",
            "Orden de compra",
        )
        PHOTO = (
            "photo",
            "Fotografía",
        )
        OTHER = (
            "other",
            "Otro documento",
        )

    class ReferenceType(models.TextChoices):
        NONE = (
            "none",
            "Sin referencia",
        )
        IMPORT_BATCH = (
            "import_batch",
            "Importación o lote",
        )
        UNLOADING = (
            "unloading",
            "Descarga",
        )
        PURCHASE = (
            "purchase",
            "Compra",
        )
        SALE = (
            "sale",
            "Venta",
        )
        RESERVATION = (
            "reservation",
            "Separación",
        )
        DELIVERY = (
            "delivery",
            "Entrega",
        )
        INSTALLATION = (
            "installation",
            "Instalación",
        )
        REMOVAL = (
            "removal",
            "Retiro",
        )
        CONTRACT = (
            "contract",
            "Contrato",
        )
        REPAIR = (
            "repair",
            "Reparación",
        )
        MOVEMENT = (
            "movement",
            "Movimiento",
        )
        OTHER = (
            "other",
            "Otro proceso",
        )

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="documents",
        verbose_name="Equipo",
    )

    document_type = models.CharField(
        max_length=40,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
        db_index=True,
        verbose_name="Tipo de documento",
    )

    title = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="Título",
        help_text=(
            "Nombre visible que permitirá identificar el documento."
        ),
    )

    document_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Número de documento",
        help_text=(
            "Número de factura, guía, acta, certificado "
            "u otra referencia documental."
        ),
    )

    document_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha del documento",
    )

    expiration_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de vencimiento",
        help_text=(
            "Se utiliza para garantías, certificados "
            "u otros documentos con vigencia."
        ),
    )

    file = models.FileField(
        upload_to=equipment_document_path,
        verbose_name="Archivo",
    )

    original_filename = models.CharField(
        max_length=255,
        blank=True,
        editable=False,
        verbose_name="Nombre original del archivo",
    )

    file_extension = models.CharField(
        max_length=20,
        blank=True,
        editable=False,
        verbose_name="Extensión",
    )

    file_size = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Tamaño del archivo",
        help_text="Tamaño almacenado en bytes.",
    )

    reference_type = models.CharField(
        max_length=30,
        choices=ReferenceType.choices,
        default=ReferenceType.NONE,
        db_index=True,
        verbose_name="Proceso relacionado",
    )

    reference_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID del registro relacionado",
        help_text=(
            "UUID de la reparación, contrato, entrega, venta "
            "u otro proceso relacionado."
        ),
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Número de referencia",
        help_text=(
            "Número visible del proceso relacionado. "
            "Ejemplo: REP-000125, CONT-000054 o GUIA-001256."
        ),
    )

    uploaded_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_equipment_documents",
        verbose_name="Subido por",
    )

    is_primary = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Documento principal",
        help_text=(
            "Permite destacar un documento principal "
            "dentro de su tipo."
        ),
    )

    is_confidential = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Confidencial",
        help_text=(
            "Indica que el archivo contiene información "
            "de acceso restringido."
        ),
    )

    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Verificado",
        help_text=(
            "Indica que el documento fue revisado y confirmado."
        ),
    )

    verified_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="verified_equipment_documents",
        verbose_name="Verificado por",
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de verificación",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activo",
    )

    class Meta:
        verbose_name = "Documento de equipo"
        verbose_name_plural = "Documentos de equipos"
        ordering = (
            "-document_date",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "equipment",
                    "document_type",
                ],
                name="equip_doc_equipment_type_idx",
            ),
            models.Index(
                fields=[
                    "equipment",
                    "document_date",
                ],
                name="equip_doc_equipment_date_idx",
            ),
            models.Index(
                fields=[
                    "reference_type",
                    "reference_id",
                ],
                name="equip_doc_reference_idx",
            ),
            models.Index(
                fields=[
                    "document_type",
                    "is_active",
                ],
                name="equip_doc_type_active_idx",
            ),
            models.Index(
                fields=[
                    "is_verified",
                    "is_active",
                ],
                name="equip_doc_verified_active_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "equipment",
                    "document_type",
                ],
                condition=models.Q(
                    is_primary=True,
                    archived_at__isnull=True,
                ),
                name="unique_primary_equipment_document_type",
            ),
        ]

    def __str__(self):
        equipment_text = ""

        if self.equipment_id:
            equipment_text = str(
                self.equipment
            ).strip()

        if equipment_text:
            return f"{self.title} - {equipment_text}"

        return self.title

    def clean(self):
        """
        Normaliza y valida el documento.
        """

        super().clean()

        self.title = str(
            self.title or ""
        ).strip()

        self.document_number = str(
            self.document_number or ""
        ).strip().upper()

        self.reference_number = str(
            self.reference_number or ""
        ).strip().upper()

        self.description = str(
            self.description or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        if not self.equipment_id:
            raise ValidationError(
                {
                    "equipment": (
                        "Debe seleccionar el equipo relacionado."
                    ),
                }
            )

        if not self.title:
            raise ValidationError(
                {
                    "title": (
                        "El título del documento es obligatorio."
                    ),
                }
            )

        if not self.file:
            raise ValidationError(
                {
                    "file": (
                        "Debe seleccionar un archivo."
                    ),
                }
            )

        if (
            self.document_date
            and self.expiration_date
            and self.expiration_date < self.document_date
        ):
            raise ValidationError(
                {
                    "expiration_date": (
                        "La fecha de vencimiento no puede ser "
                        "anterior a la fecha del documento."
                    ),
                }
            )

        if (
            self.reference_type != self.ReferenceType.NONE
            and not self.reference_id
            and not self.reference_number
        ):
            raise ValidationError(
                {
                    "reference_number": (
                        "Debe indicar el ID o número del proceso "
                        "relacionado."
                    ),
                }
            )

        if (
            self.reference_type == self.ReferenceType.NONE
            and self.reference_id
        ):
            raise ValidationError(
                {
                    "reference_type": (
                        "Debe seleccionar el tipo de proceso "
                        "relacionado."
                    ),
                }
            )

        if (
            self.reference_type == self.ReferenceType.NONE
            and self.reference_number
        ):
            raise ValidationError(
                {
                    "reference_type": (
                        "Debe seleccionar el tipo de proceso "
                        "relacionado."
                    ),
                }
            )

        if (
            self.is_verified
            and not self.verified_by_id
        ):
            raise ValidationError(
                {
                    "verified_by": (
                        "Debe indicar quién verificó el documento."
                    ),
                }
            )

        if (
            self.is_verified
            and not self.verified_at
        ):
            raise ValidationError(
                {
                    "verified_at": (
                        "Debe registrar la fecha de verificación."
                    ),
                }
            )

        if (
            not self.is_verified
            and self.verified_by_id
        ):
            raise ValidationError(
                {
                    "verified_by": (
                        "No puede indicar un verificador si el "
                        "documento no está marcado como verificado."
                    ),
                }
            )

        if (
            not self.is_verified
            and self.verified_at
        ):
            raise ValidationError(
                {
                    "verified_at": (
                        "No puede indicar una fecha de verificación "
                        "si el documento no está marcado como verificado."
                    ),
                }
            )

        if self.is_primary and self.equipment_id:
            duplicate_primary = EquipmentDocument.objects.filter(
                equipment_id=self.equipment_id,
                document_type=self.document_type,
                is_primary=True,
                archived_at__isnull=True,
            ).exclude(
                pk=self.pk,
            )

            if duplicate_primary.exists():
                raise ValidationError(
                    {
                        "is_primary": (
                            "Ya existe un documento principal activo "
                            "de este tipo para el equipo."
                        ),
                    }
                )

    def save(self, *args, **kwargs):
        """
        Normaliza, obtiene metadatos y valida antes de guardar.
        """

        self.title = str(
            self.title or ""
        ).strip()

        self.document_number = str(
            self.document_number or ""
        ).strip().upper()

        self.reference_number = str(
            self.reference_number or ""
        ).strip().upper()

        self.description = str(
            self.description or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        if self.file:
            uploaded_file = self.file

            original_name = os.path.basename(
                uploaded_file.name or ""
            )

            extension = os.path.splitext(
                original_name
            )[1].lower()

            self.original_filename = original_name
            self.file_extension = extension

            file_size = getattr(
                uploaded_file,
                "size",
                None,
            )

            if file_size is not None:
                self.file_size = file_size

        self.full_clean()

        update_fields = kwargs.get(
            "update_fields"
        )

        if update_fields is not None:
            update_fields = set(
                update_fields
            )

            update_fields.update(
                {
                    "original_filename",
                    "file_extension",
                    "file_size",
                }
            )

            kwargs["update_fields"] = list(
                update_fields
            )

        return super().save(
            *args,
            **kwargs,
        )

    def verify(
        self,
        user,
        save=True,
    ):
        """
        Marca el documento como revisado y confirmado.
        """

        if user is None:
            raise ValidationError(
                {
                    "verified_by": (
                        "Debe indicar el usuario que verifica "
                        "el documento."
                    ),
                }
            )

        self.is_verified = True
        self.verified_by = user
        self.verified_at = timezone.now()
        self.updated_by = user

        if save:
            self.save(
                update_fields=[
                    "is_verified",
                    "verified_by",
                    "verified_at",
                    "updated_by",
                    "updated_at",
                ]
            )

        return self

    def remove_verification(
        self,
        user=None,
        save=True,
    ):
        """
        Retira la verificación del documento.
        """

        self.is_verified = False
        self.verified_by = None
        self.verified_at = None

        if user:
            self.updated_by = user

        if save:
            self.save(
                update_fields=[
                    "is_verified",
                    "verified_by",
                    "verified_at",
                    "updated_by",
                    "updated_at",
                ]
            )

        return self

    def archive(
        self,
        user=None,
        reason="",
        save=True,
    ):
        """
        Archiva el documento y lo marca como inactivo.

        Si era el documento principal de su tipo, deja de ser principal.
        """

        self.is_active = False
        self.is_primary = False

        if not save:
            return super().archive(
                user=user,
                reason=reason,
                save=False,
            )

        self.archived_at = timezone.now()
        self.archived_by = user
        self.archived_reason = str(
            reason or ""
        ).strip()

        if user:
            self.updated_by = user

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
        Restaura el documento.

        No recupera automáticamente la condición de documento principal,
        para evitar conflictos con otro documento principal vigente.
        """

        self.archived_at = None
        self.archived_by = None
        self.archived_reason = ""
        self.is_active = True
        self.is_primary = False

        if user:
            self.updated_by = user

        if not save:
            return self

        self.save(
            update_fields=[
                "archived_at",
                "archived_by",
                "archived_reason",
                "is_active",
                "is_primary",
                "updated_by",
                "updated_at",
            ]
        )

        return self