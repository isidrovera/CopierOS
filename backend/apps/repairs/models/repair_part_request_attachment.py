# -*- coding: utf-8 -*-
import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base import RepairBaseModel
from .repair_part_request import RepairPartRequest
from .repair_part_request_item import RepairPartRequestItem


def repair_part_attachment_path(instance, filename):
    extension = os.path.splitext(filename)[1].lower()
    request_code = str(instance.request.code or instance.request_id)
    return (
        f"repairs/part-requests/{request_code}/"
        f"{uuid.uuid4().hex}{extension}"
    )


class RepairPartRequestAttachment(RepairBaseModel):
    class AttachmentType(models.TextChoices):
        GENERAL = "general", "General"
        TECHNICAL_EVIDENCE = "technical_evidence", "Evidencia técnica"
        DONOR_EQUIPMENT = "donor_equipment", "Equipo donante"
        STOCK_EVIDENCE = "stock_evidence", "Evidencia de stock"
        QUOTATION = "quotation", "Cotización"
        PURCHASE_DOCUMENT = "purchase_document", "Documento de compra"
        WITHDRAWAL_EVIDENCE = "withdrawal_evidence", "Evidencia de retiro"
        DELIVERY_EVIDENCE = "delivery_evidence", "Evidencia de entrega"
        REPLACEMENT_EVIDENCE = (
            "replacement_evidence",
            "Evidencia de reposición",
        )
        OTHER = "other", "Otro"

    request = models.ForeignKey(
        RepairPartRequest,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Solicitud",
    )
    item = models.ForeignKey(
        RepairPartRequestItem,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Ítem",
    )
    attachment_type = models.CharField(
        max_length=40,
        choices=AttachmentType.choices,
        default=AttachmentType.GENERAL,
        db_index=True,
        verbose_name="Tipo",
    )
    file = models.FileField(
        upload_to=repair_part_attachment_path,
        verbose_name="Archivo",
    )
    original_filename = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre original",
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Título",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )
    file_size = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Tamaño del archivo",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="repair_part_request_attachments",
        verbose_name="Subido por",
    )

    class Meta:
        verbose_name = "Adjunto de solicitud de parte"
        verbose_name_plural = "Adjuntos de solicitudes de partes"
        ordering = ("-created_at",)

    def __str__(self):
        return self.title or self.original_filename or str(self.file)

    def clean(self):
        super().clean()
        self.original_filename = str(self.original_filename or "").strip()
        self.title = str(self.title or "").strip()
        self.description = str(self.description or "").strip()

        if self.item_id and self.item.request_id != self.request_id:
            raise ValidationError(
                {"item": "El ítem no pertenece a la solicitud."}
            )

        if self.file:
            if not self.original_filename:
                self.original_filename = os.path.basename(self.file.name)
            try:
                self.file_size = self.file.size
            except (AttributeError, OSError):
                pass

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
