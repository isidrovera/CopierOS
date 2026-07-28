# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import ServicesBaseModel
from .service_part_request import ServicePartRequest


class ServicePartRequestInformation(ServicesBaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente de respuesta"
        ANSWERED = "answered", "Respondida"
        CLOSED = "closed", "Cerrada"
        CANCELLED = "cancelled", "Cancelada"

    class ResponsibleArea(models.TextChoices):
        TECHNICAL = "technical", "Taller / Técnico"
        SALES = "sales", "Ventas"
        LOGISTICS = "logistics", "Logística"
        MANAGEMENT = "management", "Gerencia"
        OTHER = "other", "Otro"

    request = models.ForeignKey(
        ServicePartRequest,
        on_delete=models.CASCADE,
        related_name="information_requests",
        verbose_name="Pedido",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_information_requested",
        verbose_name="Solicitado por",
    )

    requested_to_area = models.CharField(
        max_length=30,
        choices=ResponsibleArea.choices,
        db_index=True,
        verbose_name="Área responsable de responder",
    )

    requested_to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_information_assigned",
        verbose_name="Usuario responsable de responder",
    )

    question = models.TextField(
        verbose_name="Información solicitada",
    )

    response = models.TextField(
        blank=True,
        verbose_name="Respuesta",
    )

    requested_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de solicitud",
    )

    due_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha límite",
    )

    answered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_information_answered",
        verbose_name="Respondido por",
    )

    answered_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de respuesta",
    )

    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_information_closed",
        verbose_name="Cerrado por",
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de cierre",
    )

    closure_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones de cierre",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos adicionales",
    )

    class Meta:
        ordering = (
            "-requested_at",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "request",
                    "status",
                ],
                name="svc_pr_info_req_st_idx",
            ),
            models.Index(
                fields=[
                    "requested_to_area",
                    "status",
                ],
                name="svc_pr_info_area_st_idx",
            ),
            models.Index(
                fields=[
                    "requested_to_user",
                    "status",
                ],
                name="svc_pr_info_user_st_idx",
            ),
            models.Index(
                fields=[
                    "due_at",
                    "status",
                ],
                name="svc_pr_info_due_st_idx",
            ),
        ]
        verbose_name = "Solicitud de información del pedido"
        verbose_name_plural = "Solicitudes de información de pedidos"

    def __str__(self):
        return (
            f"{self.request.code} · "
            f"{self.get_status_display()}"
        )

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    def clean(self):
        super().clean()

        self.question = self._clean_text(
            self.question
        )

        self.response = self._clean_text(
            self.response
        )

        self.closure_notes = self._clean_text(
            self.closure_notes
        )

        if not self.question:
            raise ValidationError(
                {
                    "question": (
                        "Debe indicar la información "
                        "que se está solicitando."
                    )
                }
            )

        if (
            self.due_at
            and self.requested_at
            and self.due_at < self.requested_at
        ):
            raise ValidationError(
                {
                    "due_at": (
                        "La fecha límite no puede ser "
                        "anterior a la fecha de solicitud."
                    )
                }
            )

        if (
            self.status
            == self.Status.ANSWERED
            and not self.response
        ):
            raise ValidationError(
                {
                    "response": (
                        "Debe registrar la respuesta."
                    )
                }
            )

        if (
            self.status
            == self.Status.ANSWERED
            and not self.answered_by_id
        ):
            raise ValidationError(
                {
                    "answered_by": (
                        "Debe registrar quién respondió."
                    )
                }
            )

        if (
            self.status
            == self.Status.CLOSED
            and not self.closed_by_id
        ):
            raise ValidationError(
                {
                    "closed_by": (
                        "Debe registrar quién cerró "
                        "la solicitud."
                    )
                }
            )

        if (
            self.status
            == self.Status.CANCELLED
            and not self.closure_notes
        ):
            raise ValidationError(
                {
                    "closure_notes": (
                        "Debe indicar el motivo de la cancelación."
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
        now = timezone.now()

        if (
            self.status
            == self.Status.ANSWERED
            and not self.answered_at
        ):
            self.answered_at = now

        if (
            self.status
            in {
                self.Status.CLOSED,
                self.Status.CANCELLED,
            }
            and not self.closed_at
        ):
            self.closed_at = now

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )
