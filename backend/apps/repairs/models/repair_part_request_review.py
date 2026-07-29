# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RepairBaseModel
from .repair_part_request_item import RepairPartRequestItem


class RepairPartRequestReview(RepairBaseModel):
    class Result(models.TextChoices):
        PENDING = "pending", "Pendiente"
        STOCK = "stock", "Disponible en almacén"
        RENTAL_WAREHOUSE = "rental_warehouse", "Almacén de alquiler"
        DONOR_FOR_PARTS = "donor_for_parts", "Máquina para partes"
        DONOR_WITH_PROBLEMS = "donor_with_problems", "Máquina con problemas"
        DONOR_OPERATIONAL = "donor_operational", "Máquina operativa"
        PURCHASE = "purchase", "Compra externa"
        EXTERNAL_REPAIR = "external_repair", "Reparación externa"
        NOT_AVAILABLE = "not_available", "Sin disponibilidad"
        INFORMATION_REQUIRED = (
            "information_required",
            "Información requerida",
        )

    item = models.ForeignKey(
        RepairPartRequestItem,
        on_delete=models.CASCADE,
        related_name="area_reviews",
        verbose_name="Ítem solicitado",
    )
    result = models.CharField(
        max_length=40,
        choices=Result.choices,
        default=Result.PENDING,
        db_index=True,
        verbose_name="Resultado",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="repair_part_reviews",
        verbose_name="Revisado por",
    )
    reviewed_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de revisión",
    )
    justification = models.TextField(
        blank=True,
        verbose_name="Justificación",
    )
    requires_management_approval = models.BooleanField(
        default=True,
        verbose_name="Requiere aprobación de gerencia",
    )
    requires_replacement = models.BooleanField(
        default=False,
        verbose_name="Requiere reposición",
    )
    proposed_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Cantidad propuesta",
    )
    is_current = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Revisión vigente",
    )

    class Meta:
        verbose_name = "Revisión de solicitud de parte"
        verbose_name_plural = "Revisiones de solicitudes de partes"
        ordering = ("-reviewed_at", "-created_at")
        indexes = [
            models.Index(fields=["item", "is_current"], name="rep_part_review_current_idx"),
            models.Index(fields=["result", "reviewed_at"], name="rep_part_review_result_idx"),
        ]

    def __str__(self):
        return f"{self.item} - {self.get_result_display()}"

    def clean(self):
        super().clean()
        self.justification = str(self.justification or "").strip()

        if not self.item_id:
            raise ValidationError({"item": "El ítem es obligatorio."})

        if not self.reviewed_by_id:
            raise ValidationError(
                {"reviewed_by": "El usuario revisor es obligatorio."}
            )

        if self.proposed_quantity < 0:
            raise ValidationError(
                {"proposed_quantity": "La cantidad propuesta no puede ser negativa."}
            )

        if (
            self.item_id
            and self.proposed_quantity > self.item.requested_quantity
        ):
            raise ValidationError(
                {
                    "proposed_quantity": (
                        "La cantidad propuesta no puede superar la solicitada."
                    )
                }
            )

        if self.result != self.Result.PENDING and not self.justification:
            raise ValidationError(
                {"justification": "Debe registrar la justificación de la revisión."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.is_current and self.item_id:
            RepairPartRequestReview.objects.filter(
                item_id=self.item_id,
                is_current=True,
            ).exclude(pk=self.pk).update(is_current=False)
        return super().save(*args, **kwargs)
