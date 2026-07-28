# -*- coding: utf-8 -*-
import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base import ServicesBaseModel
from .service_part_request import ServicePartRequest
from .service_part_request_item import ServicePartRequestItem


def service_part_request_attachment_path(instance, filename):
    extension = os.path.splitext(filename)[1].lower()
    safe_name = f"{uuid.uuid4().hex}{extension}"

    request_code = (
        instance.request.code
        if instance.request_id and instance.request.code
        else "pending"
    )

    return (
        f"services/part_requests/"
        f"{request_code}/attachments/{safe_name}"
    )


class ServicePartRequestAttachment(ServicesBaseModel):
    class AttachmentType(models.TextChoices):
        GENERAL = "general", "General"
        TECHNICAL_EVIDENCE = (
            "technical_evidence",
            "Evidencia técnica",
        )
        QUOTATION = "quotation", "Cotización"
        PURCHASE_DOCUMENT = (
            "purchase_document",
            "Documento de compra",
        )
        STOCK_EVIDENCE = (
            "stock_evidence",
            "Evidencia de stock",
        )
        DONOR_EQUIPMENT = (
            "donor_equipment",
            "Equipo donante",
        )
        REUSABLE_PART = (
            "reusable_part",
            "Parte reutilizable",
        )
        MANAGEMENT_SUPPORT = (
            "management_support",
            "Sustento para gerencia",
        )
        SALES_RESPONSE = (
            "sales_response",
            "Respuesta de ventas",
        )
        LOGISTICS_EVIDENCE = (
            "logistics_evidence",
            "Evidencia de logística",
        )
        INSTALLATION_SUPPORT = (
            "installation_support",
            "Sustento de instalación",
        )
        OTHER = "other", "Otro"

    request = models.ForeignKey(
        ServicePartRequest,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Pedido",
    )

    request_item = models.ForeignKey(
        ServicePartRequestItem,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Detalle del pedido",
    )

    attachment_type = models.CharField(
        max_length=40,
        choices=AttachmentType.choices,
        default=AttachmentType.GENERAL,
        db_index=True,
        verbose_name="Tipo de adjunto",
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Título",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    file = models.FileField(
        upload_to=service_part_request_attachment_path,
        max_length=500,
        verbose_name="Archivo",
    )

    original_filename = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre original",
    )

    mime_type = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Tipo MIME",
    )

    file_size = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Tamaño del archivo",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_request_attachments",
        verbose_name="Subido por",
    )

    is_internal = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Uso interno",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos adicionales",
    )

    class Meta:
        ordering = (
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "request",
                    "attachment_type",
                ],
                name="svc_pr_att_req_type_idx",
            ),
            models.Index(
                fields=[
                    "request_item",
                    "attachment_type",
                ],
                name="svc_pr_att_item_type_idx",
            ),
            models.Index(
                fields=[
                    "uploaded_by",
                    "created_at",
                ],
                name="svc_pr_att_user_date_idx",
            ),
            models.Index(
                fields=[
                    "is_internal",
                    "created_at",
                ],
                name="svc_pr_att_internal_idx",
            ),
        ]
        verbose_name = "Adjunto del pedido"
        verbose_name_plural = "Adjuntos de pedidos"

    def __str__(self):
        return (
            f"{self.request.code} · "
            f"{self.title}"
        )

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    def clean(self):
        super().clean()

        self.title = self._clean_text(
            self.title
        )

        self.description = self._clean_text(
            self.description
        )

        self.original_filename = self._clean_text(
            self.original_filename
        )

        self.mime_type = self._clean_text(
            self.mime_type
        ).lower()

        if not self.title:
            raise ValidationError(
                {
                    "title": (
                        "Debe indicar un título para el adjunto."
                    )
                }
            )

        if not self.file:
            raise ValidationError(
                {
                    "file": (
                        "Debe adjuntar un archivo."
                    )
                }
            )

        if (
            self.request_item_id
            and self.request_item.request_id
            != self.request_id
        ):
            raise ValidationError(
                {
                    "request_item": (
                        "El detalle seleccionado pertenece "
                        "a otro pedido."
                    )
                }
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValidationError(
                {
                    "metadata": (
                        "Los datos adicionales deben tener "
                        "formato de objeto."
                    )
                }
            )

        if (
            self.file_size is not None
            and self.file_size <= 0
        ):
            raise ValidationError(
                {
                    "file_size": (
                        "El tamaño del archivo debe "
                        "ser mayor que cero."
                    )
                }
            )

    def save(self, *args, **kwargs):
        if self.file:
            if not self.original_filename:
                self.original_filename = os.path.basename(
                    self.file.name
                )

            if self.file_size is None:
                try:
                    self.file_size = self.file.size
                except (AttributeError, OSError, ValueError):
                    self.file_size = None

            if not self.title:
                self.title = self.original_filename

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )
