# -*- coding: utf-8 -*-
import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models

from .base import RentalsBaseModel
from .rental_assignment import RentalAssignment
from .rental_contract import RentalContract
from .rental_equipment import RentalEquipment
from .rental_installation import RentalInstallation
from .rental_preparation import RentalPreparation
from .rental_removal import RentalRemoval
from .rental_replacement import RentalReplacement


def rental_document_path(instance, filename):
    """
    Guarda los documentos del módulo de alquileres.

    Ejemplo:

    rentals/documents/<uuid-documento>.pdf
    """

    extension = os.path.splitext(
        filename
    )[1].lower()

    document_id = instance.id or uuid.uuid4()

    return (
        f"rentals/documents/"
        f"{document_id}{extension}"
    )


class RentalDocument(RentalsBaseModel):
    """
    Documento relacionado con la administración de alquileres.

    Puede vincularse con:

    - Equipo de alquiler.
    - Preparación para alquiler.
    - Contrato.
    - Asignación.
    - Instalación.
    - Retiro.
    - Reemplazo.

    Las evidencias fotográficas de servicios técnicos no se
    administran aquí. Se manejarán posteriormente dentro del
    módulo de órdenes de servicio.
    """

    class DocumentType(models.TextChoices):
        PURCHASE_INVOICE = (
            "purchase_invoice",
            "Factura de compra",
        )
        INTERNAL_PURCHASE = (
            "internal_purchase",
            "Compra a empresa relacionada",
        )
        DELIVERY_NOTE = (
            "delivery_note",
            "Guía de remisión",
        )
        CONTRACT = (
            "contract",
            "Contrato",
        )
        CONTRACT_ANNEX = (
            "contract_annex",
            "Anexo de contrato",
        )
        PREPARATION_REPORT = (
            "preparation_report",
            "Informe de preparación",
        )
        ASSIGNMENT_DOCUMENT = (
            "assignment_document",
            "Documento de asignación",
        )
        INSTALLATION_CERTIFICATE = (
            "installation_certificate",
            "Acta de instalación",
        )
        REMOVAL_CERTIFICATE = (
            "removal_certificate",
            "Acta de retiro",
        )
        REPLACEMENT_CERTIFICATE = (
            "replacement_certificate",
            "Acta de reemplazo",
        )
        CUSTOMER_CONFORMITY = (
            "customer_conformity",
            "Conformidad del cliente",
        )
        TECHNICAL_REPORT = (
            "technical_report",
            "Informe técnico",
        )
        OTHER = (
            "other",
            "Otro documento",
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
    )

    document_number = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Número de documento",
    )

    rental_equipment = models.ForeignKey(
        RentalEquipment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rental_documents",
        verbose_name="Equipo de alquiler",
    )

    preparation = models.ForeignKey(
        RentalPreparation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="documents",
        verbose_name="Preparación",
    )

    contract = models.ForeignKey(
        RentalContract,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="documents",
        verbose_name="Contrato",
    )

    assignment = models.ForeignKey(
        RentalAssignment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="documents",
        verbose_name="Asignación",
    )

    installation = models.ForeignKey(
        RentalInstallation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="documents",
        verbose_name="Instalación",
    )

    removal = models.ForeignKey(
        RentalRemoval,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="documents",
        verbose_name="Retiro",
    )

    replacement = models.ForeignKey(
        RentalReplacement,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="documents",
        verbose_name="Reemplazo",
    )

    file = models.FileField(
        upload_to=rental_document_path,
        verbose_name="Archivo",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    issued_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha del documento",
    )

    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Verificado",
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de verificación",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Documento de alquiler"
        verbose_name_plural = "Documentos de alquiler"
        ordering = (
            "-issued_date",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "rental_equipment",
                    "document_type",
                ],
                name="rent_doc_equipment_type_idx",
            ),
            models.Index(
                fields=[
                    "contract",
                    "document_type",
                ],
                name="rent_doc_contract_type_idx",
            ),
            models.Index(
                fields=[
                    "document_type",
                    "issued_date",
                ],
                name="rent_doc_type_date_idx",
            ),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()

        self.title = str(
            self.title or ""
        ).strip()

        self.document_number = str(
            self.document_number or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        if not self.title:
            raise ValidationError(
                {
                    "title": (
                        "El título del documento es obligatorio."
                    ),
                }
            )

        related_records = [
            self.rental_equipment_id,
            self.preparation_id,
            self.contract_id,
            self.assignment_id,
            self.installation_id,
            self.removal_id,
            self.replacement_id,
        ]

        if not any(related_records):
            raise ValidationError(
                {
                    "rental_equipment": (
                        "El documento debe relacionarse al menos "
                        "con un proceso o equipo de alquiler."
                    ),
                }
            )

        if (
            self.preparation_id
            and self.rental_equipment_id
            and self.preparation.rental_equipment_id
            != self.rental_equipment_id
        ):
            raise ValidationError(
                {
                    "preparation": (
                        "La preparación no pertenece al equipo "
                        "seleccionado."
                    ),
                }
            )

        if (
            self.assignment_id
            and self.rental_equipment_id
            and self.assignment.rental_equipment_id
            != self.rental_equipment_id
        ):
            raise ValidationError(
                {
                    "assignment": (
                        "La asignación no pertenece al equipo "
                        "seleccionado."
                    ),
                }
            )

        if (
            self.installation_id
            and self.assignment_id
            and self.installation.rental_assignment_id
            != self.assignment_id
        ):
            raise ValidationError(
                {
                    "installation": (
                        "La instalación no pertenece a la "
                        "asignación seleccionada."
                    ),
                }
            )

        if (
            self.removal_id
            and self.assignment_id
            and self.removal.rental_assignment_id
            != self.assignment_id
        ):
            raise ValidationError(
                {
                    "removal": (
                        "El retiro no pertenece a la "
                        "asignación seleccionada."
                    ),
                }
            )

        if (
            self.replacement_id
            and self.assignment_id
            and self.replacement.rental_assignment_id
            != self.assignment_id
        ):
            raise ValidationError(
                {
                    "replacement": (
                        "El reemplazo no pertenece a la "
                        "asignación seleccionada."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        self.title = str(
            self.title or ""
        ).strip()

        self.document_number = str(
            self.document_number or ""
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