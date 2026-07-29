# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RepairBaseModel
from .repair_part_request import RepairPartRequest
from .repair_part_request_item import RepairPartRequestItem


class RepairPartRequestDecision(RepairBaseModel):
    class Decision(models.TextChoices):
        PENDING = "pending", "Pendiente"
        APPROVED = "approved", "Aprobado"
        PARTIALLY_APPROVED = "partially_approved", "Aprobado parcialmente"
        REJECTED = "rejected", "Rechazado"
        INFORMATION_REQUIRED = (
            "information_required",
            "Información requerida",
        )

    request = models.ForeignKey(
        RepairPartRequest,
        on_delete=models.CASCADE,
        related_name="decisions",
        verbose_name="Solicitud",
    )
    item = models.ForeignKey(
        RepairPartRequestItem,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="decisions",
        verbose_name="Ítem",
    )
    decision = models.CharField(
        max_length=30,
        choices=Decision.choices,
        default=Decision.PENDING,
        db_index=True,
        verbose_name="Decisión",
    )
    requested_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad solicitada",
    )
    approved_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad aprobada",
    )
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="repair_part_decisions",
        verbose_name="Decidido por",
    )
    decided_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de decisión",
    )
    reason = models.TextField(
        blank=True,
        verbose_name="Motivo",
    )
    information_required = models.TextField(
        blank=True,
        verbose_name="Información requerida",
    )
    previous_decision = models.CharField(
        max_length=30,
        choices=Decision.choices,
        blank=True,
        verbose_name="Decisión anterior",
    )
    is_final = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Decisión final",
    )

    class Meta:
        verbose_name = "Decisión de solicitud de parte"
        verbose_name_plural = "Decisiones de solicitudes de partes"
        ordering = ("-decided_at", "-created_at")
        indexes = [
            models.Index(fields=["request", "decision"], name="rep_part_dec_req_idx"),
            models.Index(fields=["item", "decision"], name="rep_part_dec_item_idx"),
        ]

    def __str__(self):
        target = self.item or self.request
        return f"{target} - {self.get_decision_display()}"

    def clean(self):
        super().clean()
        self.reason = str(self.reason or "").strip()
        self.information_required = str(
            self.information_required or ""
        ).strip()

        if not self.request_id:
            raise ValidationError({"request": "La solicitud es obligatoria."})

        if self.item_id and self.item.request_id != self.request_id:
            raise ValidationError(
                {"item": "El ítem no pertenece a la solicitud indicada."}
            )

        if not self.decided_by_id:
            raise ValidationError(
                {"decided_by": "El usuario que decide es obligatorio."}
            )

        if self.requested_quantity < 0 or self.approved_quantity < 0:
            raise ValidationError(
                {"approved_quantity": "Las cantidades no pueden ser negativas."}
            )

        if self.approved_quantity > self.requested_quantity:
            raise ValidationError(
                {
                    "approved_quantity": (
                        "La cantidad aprobada no puede superar la solicitada."
                    )
                }
            )

        if self.decision == self.Decision.APPROVED:
            if self.approved_quantity != self.requested_quantity:
                raise ValidationError(
                    {
                        "approved_quantity": (
                            "Una aprobación total debe aprobar toda la cantidad."
                        )
                    }
                )

        if self.decision == self.Decision.PARTIALLY_APPROVED:
            if not (
                0 < self.approved_quantity < self.requested_quantity
            ):
                raise ValidationError(
                    {
                        "approved_quantity": (
                            "La aprobación parcial debe ser mayor que cero "
                            "y menor que la solicitada."
                        )
                    }
                )

        if self.decision == self.Decision.REJECTED and not self.reason:
            raise ValidationError(
                {"reason": "Debe indicar el motivo del rechazo."}
            )

        if (
            self.decision == self.Decision.INFORMATION_REQUIRED
            and not self.information_required
        ):
            raise ValidationError(
                {
                    "information_required": (
                        "Debe indicar la información requerida."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
