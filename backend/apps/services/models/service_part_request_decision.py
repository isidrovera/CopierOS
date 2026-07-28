# -*- coding: utf-8 -*-
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import ServicesBaseModel
from .service_part_request import ServicePartRequest
from .service_part_request_item import ServicePartRequestItem


class ServicePartRequestDecision(ServicesBaseModel):
    class Decision(models.TextChoices):
        PENDING = "pending", "Pendiente"
        APPROVED = "approved", "Aprobado"
        PARTIALLY_APPROVED = (
            "partially_approved",
            "Aprobado parcialmente",
        )
        REJECTED = "rejected", "Rechazado"
        INFORMATION_REQUIRED = (
            "information_required",
            "Requiere información",
        )

    request = models.ForeignKey(
        ServicePartRequest,
        on_delete=models.CASCADE,
        related_name="management_decisions",
        verbose_name="Pedido",
    )

    request_item = models.ForeignKey(
        ServicePartRequestItem,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="management_decisions",
        verbose_name="Detalle del pedido",
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
        null=True,
        blank=True,
        verbose_name="Cantidad solicitada",
    )

    approved_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cantidad aprobada",
    )

    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_request_decisions",
        verbose_name="Decidido por",
    )

    decided_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de decisión",
    )

    reason = models.TextField(
        blank=True,
        verbose_name="Motivo de la decisión",
    )

    information_required = models.TextField(
        blank=True,
        verbose_name="Información requerida",
    )

    previous_decision = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reassessments",
        verbose_name="Decisión anterior",
    )

    is_final = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Decisión final",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos adicionales",
    )

    class Meta:
        ordering = (
            "-decided_at",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "request",
                    "decision",
                ],
                name="svc_pr_dec_req_dec_idx",
            ),
            models.Index(
                fields=[
                    "request_item",
                    "decision",
                ],
                name="svc_pr_dec_item_idx",
            ),
            models.Index(
                fields=[
                    "decided_by",
                    "decided_at",
                ],
                name="svc_pr_dec_user_idx",
            ),
            models.Index(
                fields=[
                    "is_final",
                    "decision",
                ],
                name="svc_pr_dec_final_idx",
            ),
        ]
        verbose_name = "Decisión de pedido"
        verbose_name_plural = "Decisiones de pedidos"

    def __str__(self):
        target = (
            self.request_item.display_name
            if self.request_item_id
            else self.request.code
        )

        return (
            f"{target} · "
            f"{self.get_decision_display()}"
        )

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    def clean(self):
        super().clean()

        self.reason = self._clean_text(
            self.reason
        )

        self.information_required = self._clean_text(
            self.information_required
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

        if (
            self.request_item_id
            and self.requested_quantity is None
        ):
            self.requested_quantity = (
                self.request_item.requested_quantity
            )

        if (
            self.requested_quantity is not None
            and self.requested_quantity <= 0
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
            self.approved_quantity is not None
            and self.approved_quantity < 0
        ):
            raise ValidationError(
                {
                    "approved_quantity": (
                        "La cantidad aprobada no puede "
                        "ser negativa."
                    )
                }
            )

        if (
            self.requested_quantity is not None
            and self.approved_quantity is not None
            and self.approved_quantity
            > self.requested_quantity
        ):
            raise ValidationError(
                {
                    "approved_quantity": (
                        "La cantidad aprobada no puede "
                        "superar la solicitada."
                    )
                }
            )

        if (
            self.decision == self.Decision.APPROVED
            and self.requested_quantity is not None
            and self.approved_quantity
            != self.requested_quantity
        ):
            raise ValidationError(
                {
                    "approved_quantity": (
                        "Una aprobación total debe aprobar "
                        "toda la cantidad solicitada."
                    )
                }
            )

        if (
            self.decision
            == self.Decision.PARTIALLY_APPROVED
            and (
                self.approved_quantity is None
                or self.approved_quantity <= 0
                or (
                    self.requested_quantity is not None
                    and self.approved_quantity
                    >= self.requested_quantity
                )
            )
        ):
            raise ValidationError(
                {
                    "approved_quantity": (
                        "La aprobación parcial debe ser mayor "
                        "que cero y menor que la solicitada."
                    )
                }
            )

        if (
            self.decision == self.Decision.REJECTED
            and not self.reason
        ):
            raise ValidationError(
                {
                    "reason": (
                        "Debe indicar el motivo del rechazo."
                    )
                }
            )

        if (
            self.decision
            == self.Decision.INFORMATION_REQUIRED
            and not self.information_required
        ):
            raise ValidationError(
                {
                    "information_required": (
                        "Debe indicar la información requerida."
                    )
                }
            )

        if (
            self.decision != self.Decision.PENDING
            and not self.decided_by_id
        ):
            raise ValidationError(
                {
                    "decided_by": (
                        "Debe registrar quién tomó la decisión."
                    )
                }
            )

        if (
            self.previous_decision_id
            and self.previous_decision.request_id
            != self.request_id
        ):
            raise ValidationError(
                {
                    "previous_decision": (
                        "La decisión anterior pertenece "
                        "a otro pedido."
                    )
                }
            )

        if (
            self.previous_decision_id
            and self.previous_decision_id == self.pk
        ):
            raise ValidationError(
                {
                    "previous_decision": (
                        "Una decisión no puede referenciarse "
                        "a sí misma."
                    )
                }
            )

    def save(self, *args, **kwargs):
        if (
            self.decision != self.Decision.PENDING
            and not self.decided_at
        ):
            self.decided_at = timezone.now()

        if (
            self.request_item_id
            and self.requested_quantity is None
        ):
            self.requested_quantity = (
                self.request_item.requested_quantity
            )

        if (
            self.decision == self.Decision.APPROVED
            and self.requested_quantity is not None
            and self.approved_quantity is None
        ):
            self.approved_quantity = Decimal(
                self.requested_quantity
            )

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )
