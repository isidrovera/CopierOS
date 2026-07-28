# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base import ServicesBaseModel
from .service_part_stock_review import ServicePartStockReview


class ServicePartStockReviewHistory(ServicesBaseModel):
    class Event(models.TextChoices):
        CREATED = "created", "Revisión creada"
        REVIEW_STARTED = "review_started", "Revisión iniciada"
        AVAILABLE = "available", "Stock disponible"
        PARTIAL = "partial", "Stock parcial"
        OUT_OF_STOCK = "out_of_stock", "Sin stock"
        REUSABLE_SELECTED = (
            "reusable_selected",
            "Parte reutilizable seleccionada",
        )
        DONOR_EQUIPMENT_SELECTED = (
            "donor_equipment_selected",
            "Equipo donante seleccionado",
        )
        PURCHASE_REQUIRED = (
            "purchase_required",
            "Compra requerida",
        )
        EXTERNAL_REPAIR_REQUIRED = (
            "external_repair_required",
            "Reparación externa requerida",
        )
        QUANTITY_UPDATED = (
            "quantity_updated",
            "Cantidad actualizada",
        )
        RESERVATION_UPDATED = (
            "reservation_updated",
            "Reserva actualizada",
        )
        LOCATION_UPDATED = (
            "location_updated",
            "Ubicación actualizada",
        )
        EXPECTED_DATE_UPDATED = (
            "expected_date_updated",
            "Fecha estimada actualizada",
        )
        CANCELLED = "cancelled", "Revisión cancelada"
        NOTE_ADDED = "note_added", "Observación registrada"

    stock_review = models.ForeignKey(
        ServicePartStockReview,
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name="Revisión de stock",
    )

    event = models.CharField(
        max_length=40,
        choices=Event.choices,
        db_index=True,
        verbose_name="Evento",
    )

    previous_status = models.CharField(
        max_length=40,
        choices=ServicePartStockReview.Status.choices,
        blank=True,
        db_index=True,
        verbose_name="Estado anterior",
    )

    new_status = models.CharField(
        max_length=40,
        choices=ServicePartStockReview.Status.choices,
        blank=True,
        db_index=True,
        verbose_name="Estado nuevo",
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_stock_review_events",
        verbose_name="Registrado por",
    )

    previous_available_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cantidad disponible anterior",
    )

    new_available_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cantidad disponible nueva",
    )

    previous_reserved_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cantidad reservada anterior",
    )

    new_reserved_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cantidad reservada nueva",
    )

    previous_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ubicación anterior",
    )

    new_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ubicación nueva",
    )

    previous_expected_available_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha estimada anterior",
    )

    new_expected_available_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha estimada nueva",
    )

    source = models.CharField(
        max_length=30,
        default="web",
        db_index=True,
        verbose_name="Origen",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
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
                    "stock_review",
                    "created_at",
                ],
                name="svc_stock_hist_rev_idx",
            ),
            models.Index(
                fields=[
                    "event",
                    "created_at",
                ],
                name="svc_stock_hist_event_idx",
            ),
            models.Index(
                fields=[
                    "new_status",
                    "created_at",
                ],
                name="svc_stock_hist_status_idx",
            ),
            models.Index(
                fields=[
                    "performed_by",
                    "created_at",
                ],
                name="svc_stock_hist_user_idx",
            ),
        ]
        verbose_name = "Historial de revisión de stock"
        verbose_name_plural = "Historiales de revisiones de stock"

    def __str__(self):
        return (
            f"{self.stock_review} · "
            f"{self.get_event_display()}"
        )

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    def clean(self):
        super().clean()

        self.previous_location = self._clean_text(
            self.previous_location
        )

        self.new_location = self._clean_text(
            self.new_location
        )

        self.source = (
            self._clean_text(
                self.source
            ).lower()
            or "web"
        )

        self.notes = self._clean_text(
            self.notes
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

        status_events = {
            self.Event.AVAILABLE,
            self.Event.PARTIAL,
            self.Event.OUT_OF_STOCK,
            self.Event.REUSABLE_SELECTED,
            self.Event.DONOR_EQUIPMENT_SELECTED,
            self.Event.PURCHASE_REQUIRED,
            self.Event.EXTERNAL_REPAIR_REQUIRED,
            self.Event.CANCELLED,
        }

        if (
            self.event in status_events
            and not self.new_status
        ):
            raise ValidationError(
                {
                    "new_status": (
                        "Este evento requiere registrar "
                        "el nuevo estado."
                    )
                }
            )

        if (
            self.previous_status
            and self.new_status
            and self.previous_status
            == self.new_status
            and self.event in status_events
        ):
            raise ValidationError(
                {
                    "new_status": (
                        "El nuevo estado debe ser diferente "
                        "del anterior."
                    )
                }
            )

        if (
            self.event == self.Event.QUANTITY_UPDATED
            and self.previous_available_quantity
            == self.new_available_quantity
        ):
            raise ValidationError(
                {
                    "new_available_quantity": (
                        "La nueva cantidad disponible debe ser "
                        "diferente de la anterior."
                    )
                }
            )

        if (
            self.event == self.Event.RESERVATION_UPDATED
            and self.previous_reserved_quantity
            == self.new_reserved_quantity
        ):
            raise ValidationError(
                {
                    "new_reserved_quantity": (
                        "La nueva cantidad reservada debe ser "
                        "diferente de la anterior."
                    )
                }
            )

        if (
            self.event == self.Event.LOCATION_UPDATED
            and self.previous_location == self.new_location
        ):
            raise ValidationError(
                {
                    "new_location": (
                        "La nueva ubicación debe ser "
                        "diferente de la anterior."
                    )
                }
            )

        if (
            self.event == self.Event.EXPECTED_DATE_UPDATED
            and self.previous_expected_available_at
            == self.new_expected_available_at
        ):
            raise ValidationError(
                {
                    "new_expected_available_at": (
                        "La nueva fecha estimada debe ser "
                        "diferente de la anterior."
                    )
                }
            )

        events_requiring_notes = {
            self.Event.OUT_OF_STOCK,
            self.Event.PURCHASE_REQUIRED,
            self.Event.EXTERNAL_REPAIR_REQUIRED,
            self.Event.CANCELLED,
        }

        if (
            self.event in events_requiring_notes
            and not self.notes
        ):
            raise ValidationError(
                {
                    "notes": (
                        "Este evento requiere una observación."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )
