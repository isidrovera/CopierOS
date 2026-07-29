# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RepairBaseModel
from .repair_part_request_item import RepairPartRequestItem
from .repair_part_source import RepairPartSource


class RepairPartWithdrawal(RepairBaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        AUTHORIZED = "authorized", "Autorizado"
        IN_PROGRESS = "in_progress", "Retiro en proceso"
        WITHDRAWN = "withdrawn", "Retirado"
        RECEIVED = "received", "Recibido"
        REJECTED = "rejected", "Rechazado"
        CANCELLED = "cancelled", "Cancelado"

    item = models.OneToOneField(
        RepairPartRequestItem,
        on_delete=models.CASCADE,
        related_name="withdrawal",
        verbose_name="Ítem solicitado",
    )
    source = models.ForeignKey(
        RepairPartSource,
        on_delete=models.PROTECT,
        related_name="withdrawals",
        verbose_name="Origen",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )
    authorized_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="authorized_repair_part_withdrawals",
        verbose_name="Persona autorizada",
    )
    authorized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_part_withdrawals_authorized",
        verbose_name="Autorizado por",
    )
    authorized_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de autorización",
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Válido hasta",
    )
    withdrawn_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_parts_withdrawn",
        verbose_name="Retirado por",
    )
    withdrawn_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de retiro",
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_part_withdrawals_received",
        verbose_name="Recibido por",
    )
    received_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de recepción",
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=1,
        verbose_name="Cantidad",
    )
    authorization_notes = models.TextField(
        blank=True,
        verbose_name="Condiciones de autorización",
    )
    withdrawal_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones del retiro",
    )

    class Meta:
        verbose_name = "Retiro de parte para reparación"
        verbose_name_plural = "Retiros de partes para reparaciones"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.item} - {self.get_status_display()}"

    def clean(self):
        super().clean()
        self.authorization_notes = str(
            self.authorization_notes or ""
        ).strip()
        self.withdrawal_notes = str(self.withdrawal_notes or "").strip()

        if self.quantity <= 0:
            raise ValidationError(
                {"quantity": "La cantidad debe ser mayor que cero."}
            )

        if self.source_id and self.item_id and self.source.item_id != self.item_id:
            raise ValidationError(
                {"source": "El origen no corresponde al ítem."}
            )

        if self.status == self.Status.AUTHORIZED:
            if not self.authorized_person_id or not self.authorized_by_id:
                raise ValidationError(
                    {
                        "authorized_person": (
                            "Debe indicar la persona autorizada y quién autoriza."
                        )
                    }
                )
            if not self.authorized_at:
                self.authorized_at = timezone.now()

        if self.status == self.Status.WITHDRAWN:
            if not self.withdrawn_by_id:
                raise ValidationError(
                    {"withdrawn_by": "Debe indicar quién retiró la parte."}
                )
            if not self.withdrawn_at:
                self.withdrawn_at = timezone.now()

        if self.status == self.Status.RECEIVED:
            if not self.received_by_id:
                raise ValidationError(
                    {"received_by": "Debe indicar quién recibió la parte."}
                )
            if not self.received_at:
                self.received_at = timezone.now()

        if self.valid_until and self.authorized_at:
            if self.valid_until < self.authorized_at:
                raise ValidationError(
                    {"valid_until": "La vigencia no puede ser anterior a la autorización."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
