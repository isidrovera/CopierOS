# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RepairBaseModel
from .repair_part_request_item import RepairPartRequestItem


class RepairPartDelivery(RepairBaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        PREPARING = "preparing", "En preparación"
        READY = "ready", "Listo para entrega"
        DELIVERED = "delivered", "Entregado"
        RECEIVED = "received", "Recibido"
        PARTIALLY_RECEIVED = "partially_received", "Recibido parcialmente"
        RETURNED = "returned", "Devuelto"
        CANCELLED = "cancelled", "Cancelado"

    item = models.ForeignKey(
        RepairPartRequestItem,
        on_delete=models.CASCADE,
        related_name="deliveries",
        verbose_name="Ítem solicitado",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )
    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_part_deliveries_prepared",
        verbose_name="Preparado por",
    )
    prepared_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de preparación",
    )
    delivered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_part_deliveries_made",
        verbose_name="Entregado por",
    )
    delivered_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_part_deliveries_received",
        verbose_name="Entregado a",
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de entrega",
    )
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_part_delivery_confirmations",
        verbose_name="Confirmado por",
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de confirmación",
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=1,
        verbose_name="Cantidad entregada",
    )
    received_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad recibida",
    )
    delivery_document = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Documento de entrega",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Entrega de parte para reparación"
        verbose_name_plural = "Entregas de partes para reparaciones"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["item", "status"], name="rep_part_delivery_status_idx"),
        ]

    def __str__(self):
        return f"{self.item} - {self.get_status_display()}"

    def clean(self):
        super().clean()
        self.delivery_document = str(self.delivery_document or "").strip().upper()
        self.notes = str(self.notes or "").strip()

        if self.quantity <= 0:
            raise ValidationError(
                {"quantity": "La cantidad entregada debe ser mayor que cero."}
            )

        if self.received_quantity < 0:
            raise ValidationError(
                {"received_quantity": "La cantidad recibida no puede ser negativa."}
            )

        if self.received_quantity > self.quantity:
            raise ValidationError(
                {
                    "received_quantity": (
                        "La cantidad recibida no puede superar la entregada."
                    )
                }
            )

        if self.status == self.Status.PREPARING and not self.prepared_by_id:
            raise ValidationError(
                {"prepared_by": "Debe indicar quién prepara la entrega."}
            )

        if self.status == self.Status.DELIVERED:
            if not self.delivered_by_id or not self.delivered_to_id:
                raise ValidationError(
                    {
                        "delivered_to": (
                            "Debe indicar quién entrega y quién recibe."
                        )
                    }
                )
            if not self.delivered_at:
                self.delivered_at = timezone.now()

        if self.status in {
            self.Status.RECEIVED,
            self.Status.PARTIALLY_RECEIVED,
        }:
            if not self.confirmed_by_id:
                raise ValidationError(
                    {"confirmed_by": "Debe confirmar la recepción."}
                )
            if not self.confirmed_at:
                self.confirmed_at = timezone.now()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
