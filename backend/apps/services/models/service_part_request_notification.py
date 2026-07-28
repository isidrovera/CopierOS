# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import ServicesBaseModel
from .service_part_request import ServicePartRequest
from .service_part_request_item import ServicePartRequestItem


class ServicePartRequestNotification(ServicesBaseModel):
    class NotificationType(models.TextChoices):
        REQUEST_CREATED = (
            "request_created",
            "Pedido creado",
        )
        REQUEST_SUBMITTED = (
            "request_submitted",
            "Pedido enviado",
        )
        REVIEW_REQUIRED = (
            "review_required",
            "Revisión requerida",
        )
        INFORMATION_REQUIRED = (
            "information_required",
            "Información requerida",
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
        STOCK_REVIEW_REQUIRED = (
            "stock_review_required",
            "Revisión de stock requerida",
        )
        STOCK_AVAILABLE = (
            "stock_available",
            "Stock disponible",
        )
        STOCK_PARTIAL = (
            "stock_partial",
            "Stock parcial",
        )
        OUT_OF_STOCK = (
            "out_of_stock",
            "Sin stock",
        )
        LOGISTICS_PREPARATION = (
            "logistics_preparation",
            "Preparación logística",
        )
        READY_FOR_INSTALLATION = (
            "ready_for_installation",
            "Listo para instalación",
        )
        INSTALLATION_ORDER_CREATED = (
            "installation_order_created",
            "OS de instalación creada",
        )
        TECHNICIAN_ASSIGNED = (
            "technician_assigned",
            "Técnico asignado",
        )
        TRANSFER_ASSIGNED = (
            "transfer_assigned",
            "Transferencia asignada",
        )
        TRANSFER_RECEIVED = (
            "transfer_received",
            "Parte recibida",
        )
        INSTALLATION_COMPLETED = (
            "installation_completed",
            "Instalación completada",
        )
        REQUEST_CANCELLED = (
            "request_cancelled",
            "Pedido cancelado",
        )
        COMMENT_MENTION = (
            "comment_mention",
            "Mención en comentario",
        )
        DUE_DATE_WARNING = (
            "due_date_warning",
            "Alerta de vencimiento",
        )
        GENERAL = "general", "Notificación general"

    class Channel(models.TextChoices):
        IN_APP = "in_app", "Dentro del sistema"
        EMAIL = "email", "Correo electrónico"
        PUSH = "push", "Notificación móvil"

    class DeliveryStatus(models.TextChoices):
        PENDING = "pending", "Pendiente"
        SENT = "sent", "Enviada"
        DELIVERED = "delivered", "Entregada"
        READ = "read", "Leída"
        FAILED = "failed", "Fallida"
        CANCELLED = "cancelled", "Cancelada"

    request = models.ForeignKey(
        ServicePartRequest,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Pedido",
    )

    request_item = models.ForeignKey(
        ServicePartRequestItem,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Detalle del pedido",
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_part_request_notifications",
        verbose_name="Destinatario",
    )

    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
        db_index=True,
        verbose_name="Tipo de notificación",
    )

    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        default=Channel.IN_APP,
        db_index=True,
        verbose_name="Canal",
    )

    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
        db_index=True,
        verbose_name="Estado de entrega",
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Título",
    )

    message = models.TextField(
        verbose_name="Mensaje",
    )

    action_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Ruta de acción",
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha programada",
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de envío",
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de entrega",
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de lectura",
    )

    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de fallo",
    )

    failure_reason = models.TextField(
        blank=True,
        verbose_name="Motivo del fallo",
    )

    retry_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Cantidad de reintentos",
    )

    external_reference = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
        verbose_name="Referencia externa",
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
                    "recipient",
                    "delivery_status",
                    "created_at",
                ],
                name="svc_pr_not_rec_st_idx",
            ),
            models.Index(
                fields=[
                    "request",
                    "notification_type",
                ],
                name="svc_pr_not_req_type_idx",
            ),
            models.Index(
                fields=[
                    "channel",
                    "delivery_status",
                    "scheduled_at",
                ],
                name="svc_pr_not_chan_st_idx",
            ),
            models.Index(
                fields=[
                    "request_item",
                    "notification_type",
                ],
                name="svc_pr_not_item_idx",
            ),
        ]
        verbose_name = "Notificación del pedido"
        verbose_name_plural = "Notificaciones de pedidos"

    def __str__(self):
        return (
            f"{self.request.code} · "
            f"{self.recipient} · "
            f"{self.title}"
        )

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    def clean(self):
        super().clean()

        self.title = self._clean_text(
            self.title
        )

        self.message = self._clean_text(
            self.message
        )

        self.action_url = self._clean_text(
            self.action_url
        )

        self.failure_reason = self._clean_text(
            self.failure_reason
        )

        self.external_reference = self._clean_text(
            self.external_reference
        )

        if not self.title:
            raise ValidationError(
                {
                    "title": (
                        "Debe indicar el título "
                        "de la notificación."
                    )
                }
            )

        if not self.message:
            raise ValidationError(
                {
                    "message": (
                        "Debe indicar el mensaje "
                        "de la notificación."
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
            self.delivery_status
            == self.DeliveryStatus.FAILED
            and not self.failure_reason
        ):
            raise ValidationError(
                {
                    "failure_reason": (
                        "Debe indicar el motivo del fallo."
                    )
                }
            )

        if (
            self.delivery_status
            == self.DeliveryStatus.READ
            and not self.read_at
        ):
            raise ValidationError(
                {
                    "read_at": (
                        "Debe registrar la fecha de lectura."
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
            self.delivery_status
            == self.DeliveryStatus.SENT
            and not self.sent_at
        ):
            self.sent_at = now

        if (
            self.delivery_status
            == self.DeliveryStatus.DELIVERED
            and not self.delivered_at
        ):
            self.delivered_at = now

        if (
            self.delivery_status
            == self.DeliveryStatus.READ
        ):
            if not self.read_at:
                self.read_at = now

            if not self.delivered_at:
                self.delivered_at = self.read_at

            if not self.sent_at:
                self.sent_at = self.read_at

        if (
            self.delivery_status
            == self.DeliveryStatus.FAILED
            and not self.failed_at
        ):
            self.failed_at = now

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )
