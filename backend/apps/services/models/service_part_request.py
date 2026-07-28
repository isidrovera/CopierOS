# -*- coding: utf-8 -*-
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.utils import timezone

from .base import ServicesBaseModel
from .service_order import ServiceOrder


class ServicePartRequest(ServicesBaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        SUBMITTED_TO_MANAGEMENT = "submitted_to_management", "Enviado a gerencia"
        MANAGEMENT_REVIEW = "management_review", "En evaluación por gerencia"
        INFORMATION_REQUESTED = "information_requested", "Información solicitada"
        INFORMATION_ANSWERED = "information_answered", "Información respondida"
        MANAGEMENT_REASSESSMENT = "management_reassessment", "Reevaluación de gerencia"
        APPROVED = "approved", "Aprobado por gerencia"
        REJECTED = "rejected", "Rechazado por gerencia"
        PENDING_STOCK_REVIEW = "pending_stock_review", "Pendiente de confirmar stock"
        STOCK_CONFIRMED = "stock_confirmed", "Stock confirmado"
        PARTIAL_STOCK = "partial_stock", "Stock parcial"
        OUT_OF_STOCK = "out_of_stock", "Sin stock"
        PENDING_LOGISTICS = "pending_logistics", "Pendiente de logística"
        PREPARING = "preparing", "En preparación"
        READY_FOR_INSTALLATION = "ready_for_installation", "Listo para instalación"
        INSTALLATION_ORDER_CREATED = "installation_order_created", "OS de instalación creada"
        DELIVERED = "delivered", "Entregado"
        CANCELLED = "cancelled", "Cancelado"

    class ResponsibleArea(models.TextChoices):
        TECHNICAL = "technical", "Taller / Técnico"
        MANAGEMENT = "management", "Gerencia"
        SALES = "sales", "Ventas"
        LOGISTICS = "logistics", "Logística"
        INSTALLATION = "installation", "Instalación"
        CLOSED = "closed", "Finalizado"

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        blank=True,
        editable=False,
        verbose_name="Número de pedido",
    )

    service_order = models.OneToOneField(
        ServiceOrder,
        on_delete=models.PROTECT,
        related_name="part_request",
        verbose_name="OS de origen",
    )

    installation_service_order = models.OneToOneField(
        ServiceOrder,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="source_part_request",
        verbose_name="OS de instalación",
    )

    status = models.CharField(
        max_length=40,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    current_responsible_area = models.CharField(
        max_length=30,
        choices=ResponsibleArea.choices,
        default=ResponsibleArea.TECHNICAL,
        db_index=True,
        verbose_name="Área responsable actual",
    )

    current_responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="current_service_part_requests",
        verbose_name="Responsable actual",
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_requests_created",
        verbose_name="Solicitado por",
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_requests_submitted",
        verbose_name="Enviado por",
    )

    management_reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_requests_management_reviewed",
        verbose_name="Revisado por gerencia",
    )

    stock_reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_requests_stock_reviewed",
        verbose_name="Stock revisado por",
    )

    logistics_prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_requests_logistics_prepared",
        verbose_name="Preparado por logística",
    )

    requested_at = models.DateTimeField(null=True, blank=True, db_index=True)
    submitted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    management_reviewed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    information_requested_at = models.DateTimeField(null=True, blank=True)
    information_answered_at = models.DateTimeField(null=True, blank=True)
    stock_reviewed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    logistics_ready_at = models.DateTimeField(null=True, blank=True, db_index=True)
    delivered_at = models.DateTimeField(null=True, blank=True, db_index=True)
    closed_at = models.DateTimeField(null=True, blank=True, db_index=True)

    management_notes = models.TextField(blank=True)
    stock_notes = models.TextField(blank=True)
    logistics_notes = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["status", "requested_at"], name="svc_parts_status_idx"),
            models.Index(fields=["current_responsible_area", "status"], name="svc_parts_area_st_idx"),
            models.Index(fields=["service_order", "status"], name="svc_parts_order_st_idx"),
        ]
        verbose_name = "Pedido de repuestos"
        verbose_name_plural = "Pedidos de repuestos"

    def __str__(self):
        return self.code or f"Pedido {self.pk}"

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    @classmethod
    def _build_code(cls, year, sequence):
        return f"PED-{year}-{sequence:06d}"

    @classmethod
    def _next_sequence(cls, year):
        prefix = f"PED-{year}-"
        last_code = (
            cls.objects.filter(code__startswith=prefix)
            .order_by("-code")
            .values_list("code", flat=True)
            .first()
        )

        if not last_code:
            return 1

        match = re.fullmatch(rf"{re.escape(prefix)}(\d+)", last_code)
        return int(match.group(1)) + 1 if match else 1

    def _assign_automatic_code(self):
        year = timezone.localdate().year
        self.code = self._build_code(year, self._next_sequence(year))

    def clean(self):
        super().clean()

        self.management_notes = self._clean_text(self.management_notes)
        self.stock_notes = self._clean_text(self.stock_notes)
        self.logistics_notes = self._clean_text(self.logistics_notes)
        self.notes = self._clean_text(self.notes)

        if (
            self.installation_service_order_id
            and self.installation_service_order_id == self.service_order_id
        ):
            raise ValidationError(
                {
                    "installation_service_order": (
                        "La OS de instalación debe ser diferente de la OS que originó el pedido."
                    )
                }
            )

        if self.status == self.Status.SUBMITTED_TO_MANAGEMENT and not self.submitted_at:
            raise ValidationError({"submitted_at": "Debe registrar la fecha de envío a gerencia."})

        if self.status == self.Status.INFORMATION_REQUESTED and not self.information_requested_at:
            raise ValidationError(
                {"information_requested_at": "Debe registrar la fecha de la solicitud de información."}
            )

        if self.status == self.Status.INFORMATION_ANSWERED and not self.information_answered_at:
            raise ValidationError({"information_answered_at": "Debe registrar la fecha de respuesta."})

        if self.status == self.Status.READY_FOR_INSTALLATION and not self.logistics_ready_at:
            raise ValidationError({"logistics_ready_at": "Debe registrar cuándo quedó listo el pedido."})

        if (
            self.status == self.Status.INSTALLATION_ORDER_CREATED
            and not self.installation_service_order_id
        ):
            raise ValidationError(
                {"installation_service_order": "Debe existir una OS de instalación."}
            )

    def save(self, *args, **kwargs):
        creating = self._state.adding

        if not self.requested_at:
            self.requested_at = timezone.now()

        if self.status == self.Status.SUBMITTED_TO_MANAGEMENT and not self.submitted_at:
            self.submitted_at = timezone.now()

        if self.status == self.Status.INFORMATION_REQUESTED and not self.information_requested_at:
            self.information_requested_at = timezone.now()

        if self.status == self.Status.INFORMATION_ANSWERED and not self.information_answered_at:
            self.information_answered_at = timezone.now()

        if self.status == self.Status.READY_FOR_INSTALLATION and not self.logistics_ready_at:
            self.logistics_ready_at = timezone.now()

        if self.status == self.Status.DELIVERED and not self.delivered_at:
            self.delivered_at = timezone.now()

        if not self.code:
            self._assign_automatic_code()

        self.full_clean()

        if not creating:
            return super().save(*args, **kwargs)

        for _attempt in range(5):
            try:
                with transaction.atomic():
                    return super().save(*args, **kwargs)
            except IntegrityError:
                self.code = ""
                self._assign_automatic_code()

        raise IntegrityError("No se pudo generar un número único para el pedido.")
