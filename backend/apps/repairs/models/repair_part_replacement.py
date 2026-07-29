# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.equipment.models import ComponentInventory, Equipment

from .base import RepairBaseModel
from .repair_part_request_item import RepairPartRequestItem


class RepairPartReplacement(RepairBaseModel):
    class ReplacementType(models.TextChoices):
        NONE = "none", "No aplica"
        EQUIVALENT_PART = "equivalent_part", "Reponer parte equivalente"
        DAMAGED_PART_RETURN = "damaged_part_return", "Devolver parte dañada"
        TEMPORARY_LOAN = "temporary_loan", "Préstamo temporal"
        EXTERNAL_PURCHASE = "external_purchase", "Reposición por compra"
        EXTERNAL_REPAIR = "external_repair", "Reposición por reparación externa"

    class Status(models.TextChoices):
        NOT_APPLICABLE = "not_applicable", "No aplica"
        PENDING = "pending", "Pendiente"
        IN_PURCHASE = "in_purchase", "En compra"
        IN_EXTERNAL_REPAIR = "in_external_repair", "En reparación externa"
        RECEIVED = "received", "Recibida"
        INSTALLED_AT_SOURCE = (
            "installed_at_source",
            "Instalada en equipo de origen",
        )
        RETURNED_TO_WAREHOUSE = (
            "returned_to_warehouse",
            "Devuelta a almacén",
        )
        OVERDUE = "overdue", "Vencida"
        CANCELLED = "cancelled", "Cancelada"
        COMPLETED = "completed", "Completada"

    item = models.OneToOneField(
        RepairPartRequestItem,
        on_delete=models.CASCADE,
        related_name="replacement",
        verbose_name="Ítem solicitado",
    )
    replacement_type = models.CharField(
        max_length=40,
        choices=ReplacementType.choices,
        default=ReplacementType.NONE,
        db_index=True,
        verbose_name="Tipo de reposición",
    )
    status = models.CharField(
        max_length=40,
        choices=Status.choices,
        default=Status.NOT_APPLICABLE,
        db_index=True,
        verbose_name="Estado",
    )
    source_equipment = models.ForeignKey(
        Equipment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="repair_part_replacements_due",
        verbose_name="Equipo de origen",
    )
    replacement_inventory = models.ForeignKey(
        ComponentInventory,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="repair_part_replacements",
        verbose_name="Inventario de reposición",
    )
    responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_part_replacements_responsible",
        verbose_name="Responsable",
    )
    due_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha límite",
    )
    received_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de recepción",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de finalización",
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_part_replacements_completed",
        verbose_name="Finalizado por",
    )
    external_reference = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Referencia externa",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Reposición de parte para reparación"
        verbose_name_plural = "Reposiciones de partes para reparaciones"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["status", "due_at"], name="rep_part_repl_due_idx"),
            models.Index(fields=["source_equipment", "status"], name="rep_part_repl_source_idx"),
        ]

    def __str__(self):
        return f"{self.item} - {self.get_status_display()}"

    def clean(self):
        super().clean()
        self.external_reference = str(self.external_reference or "").strip()
        self.notes = str(self.notes or "").strip()

        if self.replacement_type != self.ReplacementType.NONE:
            if not self.source_equipment_id:
                raise ValidationError(
                    {"source_equipment": "Debe indicar el equipo de origen."}
                )

        if self.status == self.Status.RECEIVED and not self.received_at:
            self.received_at = timezone.now()

        if self.status == self.Status.COMPLETED:
            if not self.completed_by_id:
                raise ValidationError(
                    {"completed_by": "Debe indicar quién completó la reposición."}
                )
            if not self.completed_at:
                self.completed_at = timezone.now()

        if (
            self.status == self.Status.IN_PURCHASE
            and not self.external_reference
        ):
            raise ValidationError(
                {
                    "external_reference": (
                        "Debe indicar la referencia de compra."
                    )
                }
            )

        if (
            self.status == self.Status.IN_EXTERNAL_REPAIR
            and not self.external_reference
        ):
            raise ValidationError(
                {
                    "external_reference": (
                        "Debe indicar la referencia de reparación externa."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
