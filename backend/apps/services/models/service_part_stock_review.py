# -*- coding: utf-8 -*-
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import ServicesBaseModel
from .service_part_request import ServicePartRequest
from .service_part_request_item import ServicePartRequestItem
from .service_reusable_part import ServiceReusablePart


class ServicePartStockReview(ServicesBaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        AVAILABLE = "available", "Disponible"
        PARTIAL = "partial", "Disponible parcialmente"
        OUT_OF_STOCK = "out_of_stock", "Sin stock"
        REUSABLE_AVAILABLE = (
            "reusable_available",
            "Parte reutilizable disponible",
        )
        DONOR_EQUIPMENT_AVAILABLE = (
            "donor_equipment_available",
            "Equipo donante disponible",
        )
        PURCHASE_REQUIRED = (
            "purchase_required",
            "Requiere compra",
        )
        EXTERNAL_REPAIR_REQUIRED = (
            "external_repair_required",
            "Requiere reparación externa",
        )
        CANCELLED = "cancelled", "Cancelado"

    request = models.ForeignKey(
        ServicePartRequest,
        on_delete=models.CASCADE,
        related_name="stock_reviews",
        verbose_name="Pedido",
    )

    request_item = models.OneToOneField(
        ServicePartRequestItem,
        on_delete=models.CASCADE,
        related_name="stock_review",
        verbose_name="Detalle del pedido",
    )

    status = models.CharField(
        max_length=40,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado de disponibilidad",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_stock_reviews",
        verbose_name="Revisado por",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de revisión",
    )

    requested_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1.00"),
        verbose_name="Cantidad solicitada",
    )

    available_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Cantidad disponible",
    )

    reserved_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Cantidad reservada",
    )

    reusable_part = models.ForeignKey(
        ServiceReusablePart,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="stock_reviews",
        verbose_name="Parte reutilizable seleccionada",
    )

    expected_available_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha estimada de disponibilidad",
    )

    purchase_reference = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Referencia de compra",
    )

    warehouse_location = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
        verbose_name="Ubicación en almacén",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        ordering = (
            "-reviewed_at",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "request",
                    "status",
                ],
                name="svc_stock_req_st_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "expected_available_at",
                ],
                name="svc_stock_st_eta_idx",
            ),
            models.Index(
                fields=[
                    "reviewed_by",
                    "reviewed_at",
                ],
                name="svc_stock_user_date_idx",
            ),
            models.Index(
                fields=[
                    "reusable_part",
                    "status",
                ],
                name="svc_stock_reuse_st_idx",
            ),
        ]
        verbose_name = "Revisión de stock"
        verbose_name_plural = "Revisiones de stock"

    def __str__(self):
        return (
            f"{self.request.code} · "
            f"{self.request_item.display_name} · "
            f"{self.get_status_display()}"
        )

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    def clean(self):
        super().clean()

        self.purchase_reference = self._clean_text(
            self.purchase_reference
        )

        self.warehouse_location = self._clean_text(
            self.warehouse_location
        )

        self.notes = self._clean_text(
            self.notes
        )

        if self.request_item.request_id != self.request_id:
            raise ValidationError(
                {
                    "request_item": (
                        "El detalle seleccionado pertenece "
                        "a otro pedido."
                    )
                }
            )

        if (
            self.requested_quantity is None
            or self.requested_quantity <= 0
        ):
            raise ValidationError(
                {
                    "requested_quantity": (
                        "La cantidad solicitada debe "
                        "ser mayor que cero."
                    )
                }
            )

        if (
            self.available_quantity is None
            or self.available_quantity < 0
        ):
            raise ValidationError(
                {
                    "available_quantity": (
                        "La cantidad disponible no puede "
                        "ser negativa."
                    )
                }
            )

        if (
            self.reserved_quantity is None
            or self.reserved_quantity < 0
        ):
            raise ValidationError(
                {
                    "reserved_quantity": (
                        "La cantidad reservada no puede "
                        "ser negativa."
                    )
                }
            )

        if self.reserved_quantity > self.available_quantity:
            raise ValidationError(
                {
                    "reserved_quantity": (
                        "La cantidad reservada no puede "
                        "superar la disponible."
                    )
                }
            )

        if self.available_quantity > self.requested_quantity:
            raise ValidationError(
                {
                    "available_quantity": (
                        "La cantidad disponible no puede "
                        "superar la solicitada."
                    )
                }
            )

        if (
            self.status == self.Status.AVAILABLE
            and self.available_quantity
            < self.requested_quantity
        ):
            raise ValidationError(
                {
                    "available_quantity": (
                        "Para marcar como disponible, la "
                        "cantidad debe cubrir lo solicitado."
                    )
                }
            )

        if (
            self.status == self.Status.PARTIAL
            and (
                self.available_quantity <= 0
                or self.available_quantity
                >= self.requested_quantity
            )
        ):
            raise ValidationError(
                {
                    "available_quantity": (
                        "La disponibilidad parcial debe ser "
                        "mayor que cero y menor que la solicitada."
                    )
                }
            )

        if (
            self.status == self.Status.OUT_OF_STOCK
            and self.available_quantity != 0
        ):
            raise ValidationError(
                {
                    "available_quantity": (
                        "Un artículo sin stock debe tener "
                        "cantidad disponible igual a cero."
                    )
                }
            )

        reusable_statuses = {
            self.Status.REUSABLE_AVAILABLE,
            self.Status.DONOR_EQUIPMENT_AVAILABLE,
        }

        if (
            self.status in reusable_statuses
            and not self.reusable_part_id
        ):
            raise ValidationError(
                {
                    "reusable_part": (
                        "Debe seleccionar la parte reutilizable "
                        "o proveniente de equipo donante."
                    )
                }
            )

        if (
            self.reusable_part_id
            and self.reusable_part.status
            not in {
                ServiceReusablePart.Status.AVAILABLE,
                ServiceReusablePart.Status.RESERVED,
                ServiceReusablePart.Status.PENDING_REMOVAL,
            }
        ):
            raise ValidationError(
                {
                    "reusable_part": (
                        "La parte seleccionada no está "
                        "disponible para este proceso."
                    )
                }
            )

        if (
            self.status == self.Status.PURCHASE_REQUIRED
            and not self.expected_available_at
            and not self.purchase_reference
        ):
            raise ValidationError(
                {
                    "expected_available_at": (
                        "Indique la fecha estimada o la "
                        "referencia de compra."
                    )
                }
            )

        statuses_requiring_review = {
            self.Status.AVAILABLE,
            self.Status.PARTIAL,
            self.Status.OUT_OF_STOCK,
            self.Status.REUSABLE_AVAILABLE,
            self.Status.DONOR_EQUIPMENT_AVAILABLE,
            self.Status.PURCHASE_REQUIRED,
            self.Status.EXTERNAL_REPAIR_REQUIRED,
            self.Status.CANCELLED,
        }

        if (
            self.status in statuses_requiring_review
            and not self.reviewed_by_id
        ):
            raise ValidationError(
                {
                    "reviewed_by": (
                        "Debe registrar quién realizó "
                        "la revisión de disponibilidad."
                    )
                }
            )

        if (
            self.status
            in {
                self.Status.OUT_OF_STOCK,
                self.Status.CANCELLED,
                self.Status.EXTERNAL_REPAIR_REQUIRED,
            }
            and not self.notes
        ):
            raise ValidationError(
                {
                    "notes": (
                        "Este estado requiere una observación."
                    )
                }
            )

    def save(self, *args, **kwargs):
        if (
            self.status != self.Status.PENDING
            and not self.reviewed_at
        ):
            self.reviewed_at = timezone.now()

        if (
            not self.requested_quantity
            and self.request_item_id
        ):
            self.requested_quantity = (
                self.request_item.requested_quantity
            )

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )
