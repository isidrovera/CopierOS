# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base import ServicesBaseModel
from .service_part_request import ServicePartRequest


class ServicePartRequestStatusHistory(ServicesBaseModel):
    class Action(models.TextChoices):
        CREATED = "created", "Pedido creado"
        SUBMITTED = "submitted", "Enviado a gerencia"
        REVIEW_STARTED = "review_started", "Revisión iniciada"
        INFORMATION_REQUESTED = (
            "information_requested",
            "Información solicitada",
        )
        INFORMATION_ANSWERED = (
            "information_answered",
            "Información respondida",
        )
        APPROVED = "approved", "Pedido aprobado"
        PARTIALLY_APPROVED = (
            "partially_approved",
            "Pedido aprobado parcialmente",
        )
        REJECTED = "rejected", "Pedido rechazado"
        STOCK_REVIEWED = (
            "stock_reviewed",
            "Stock revisado",
        )
        STOCK_CONFIRMED = (
            "stock_confirmed",
            "Stock confirmado",
        )
        PARTIAL_STOCK = (
            "partial_stock",
            "Stock parcial",
        )
        OUT_OF_STOCK = (
            "out_of_stock",
            "Sin stock",
        )
        SENT_TO_LOGISTICS = (
            "sent_to_logistics",
            "Enviado a logística",
        )
        PREPARATION_STARTED = (
            "preparation_started",
            "Preparación iniciada",
        )
        READY_FOR_INSTALLATION = (
            "ready_for_installation",
            "Listo para instalación",
        )
        INSTALLATION_ORDER_CREATED = (
            "installation_order_created",
            "OS de instalación creada",
        )
        DELIVERED = "delivered", "Pedido entregado"
        CANCELLED = "cancelled", "Pedido cancelado"
        RESPONSIBLE_CHANGED = (
            "responsible_changed",
            "Responsable cambiado",
        )
        NOTE_ADDED = "note_added", "Observación registrada"

    request = models.ForeignKey(
        ServicePartRequest,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="Pedido",
    )

    previous_status = models.CharField(
        max_length=40,
        choices=ServicePartRequest.Status.choices,
        blank=True,
        db_index=True,
        verbose_name="Estado anterior",
    )

    new_status = models.CharField(
        max_length=40,
        choices=ServicePartRequest.Status.choices,
        db_index=True,
        verbose_name="Estado nuevo",
    )

    action = models.CharField(
        max_length=40,
        choices=Action.choices,
        db_index=True,
        verbose_name="Acción",
    )

    responsible_area = models.CharField(
        max_length=30,
        choices=ServicePartRequest.ResponsibleArea.choices,
        blank=True,
        db_index=True,
        verbose_name="Área responsable",
    )

    previous_responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="previous_service_part_request_responsibilities",
        verbose_name="Responsable anterior",
    )

    new_responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="new_service_part_request_responsibilities",
        verbose_name="Responsable nuevo",
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_request_status_changes",
        verbose_name="Registrado por",
    )

    source = models.CharField(
        max_length=30,
        default="web",
        db_index=True,
        verbose_name="Origen",
    )

    comment = models.TextField(
        blank=True,
        verbose_name="Comentario",
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
                    "request",
                    "created_at",
                ],
                name="svc_pr_hist_req_date_idx",
            ),
            models.Index(
                fields=[
                    "new_status",
                    "created_at",
                ],
                name="svc_pr_hist_st_date_idx",
            ),
            models.Index(
                fields=[
                    "responsible_area",
                    "created_at",
                ],
                name="svc_pr_hist_area_idx",
            ),
            models.Index(
                fields=[
                    "changed_by",
                    "created_at",
                ],
                name="svc_pr_hist_user_idx",
            ),
        ]
        verbose_name = "Historial del pedido"
        verbose_name_plural = "Historiales de pedidos"

    def __str__(self):
        return (
            f"{self.request.code} · "
            f"{self.get_action_display()}"
        )

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    def clean(self):
        super().clean()

        self.source = (
            self._clean_text(
                self.source
            ).lower()
            or "web"
        )

        self.comment = self._clean_text(
            self.comment
        )

        if (
            self.previous_status
            and self.previous_status
            == self.new_status
            and self.action
            not in {
                self.Action.RESPONSIBLE_CHANGED,
                self.Action.NOTE_ADDED,
            }
        ):
            raise ValidationError(
                {
                    "new_status": (
                        "El nuevo estado debe ser diferente "
                        "del estado anterior."
                    )
                }
            )

        if (
            self.action
            == self.Action.RESPONSIBLE_CHANGED
            and self.previous_responsible_user_id
            == self.new_responsible_user_id
        ):
            raise ValidationError(
                {
                    "new_responsible_user": (
                        "El nuevo responsable debe ser "
                        "diferente del anterior."
                    )
                }
            )

        actions_requiring_comment = {
            self.Action.INFORMATION_REQUESTED,
            self.Action.INFORMATION_ANSWERED,
            self.Action.REJECTED,
            self.Action.CANCELLED,
            self.Action.OUT_OF_STOCK,
        }

        if (
            self.action in actions_requiring_comment
            and not self.comment
        ):
            raise ValidationError(
                {
                    "comment": (
                        "Esta acción requiere una observación."
                    )
                }
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

    def save(self, *args, **kwargs):
        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )
