# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.utils import timezone

from .base import RepairBaseModel
from .repair_part_request import RepairPartRequest
from .repair_part_request_item import RepairPartRequestItem


class RepairPartRequestHistory(RepairBaseModel):
    request = models.ForeignKey(
        RepairPartRequest,
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name="Solicitud",
    )
    item = models.ForeignKey(
        RepairPartRequestItem,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name="Ítem",
    )
    event = models.CharField(
        max_length=80,
        db_index=True,
        verbose_name="Evento",
    )
    previous_status = models.CharField(
        max_length=40,
        blank=True,
        db_index=True,
        verbose_name="Estado anterior",
    )
    new_status = models.CharField(
        max_length=40,
        blank=True,
        db_index=True,
        verbose_name="Estado nuevo",
    )
    previous_area = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Área anterior",
    )
    new_area = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Área nueva",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_part_request_history_changes",
        verbose_name="Cambiado por",
    )
    changed_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha del cambio",
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Comentario",
    )
    source = models.CharField(
        max_length=80,
        blank=True,
        db_index=True,
        verbose_name="Origen",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos adicionales",
    )

    class Meta:
        verbose_name = "Historial de solicitud de parte"
        verbose_name_plural = "Historiales de solicitudes de partes"
        ordering = ("-changed_at", "-created_at")
        indexes = [
            models.Index(fields=["request", "changed_at"], name="rep_part_hist_req_idx"),
            models.Index(fields=["item", "changed_at"], name="rep_part_hist_item_idx"),
            models.Index(fields=["event", "changed_at"], name="rep_part_hist_event_idx"),
        ]

    def __str__(self):
        return f"{self.request.code} - {self.event}"

    def save(self, *args, **kwargs):
        self.event = str(self.event or "").strip().lower()
        self.previous_status = str(self.previous_status or "").strip().lower()
        self.new_status = str(self.new_status or "").strip().lower()
        self.previous_area = str(self.previous_area or "").strip().lower()
        self.new_area = str(self.new_area or "").strip().lower()
        self.comment = str(self.comment or "").strip()
        self.source = str(self.source or "").strip().lower()
        return super().save(*args, **kwargs)
