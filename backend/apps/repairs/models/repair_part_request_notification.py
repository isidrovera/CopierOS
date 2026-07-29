# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base import RepairBaseModel
from .repair_part_request import RepairPartRequest
from .repair_part_request_item import RepairPartRequestItem


class RepairPartRequestNotification(RepairBaseModel):
    class Channel(models.TextChoices):
        IN_APP = "in_app", "Dentro del sistema"
        EMAIL = "email", "Correo electrónico"
        PUSH = "push", "Notificación push"

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        SENT = "sent", "Enviada"
        DELIVERED = "delivered", "Entregada"
        READ = "read", "Leída"
        FAILED = "failed", "Fallida"
        CANCELLED = "cancelled", "Cancelada"

    request = models.ForeignKey(
        RepairPartRequest,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Solicitud",
    )
    item = models.ForeignKey(
        RepairPartRequestItem,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Ítem",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="repair_part_request_notifications",
        verbose_name="Destinatario",
    )
    event = models.CharField(
        max_length=80,
        db_index=True,
        verbose_name="Evento",
    )
    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        default=Channel.IN_APP,
        db_index=True,
        verbose_name="Canal",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Título",
    )
    message = models.TextField(
        verbose_name="Mensaje",
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
        verbose_name="Fecha de entrega",
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de lectura",
    )
    failure_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de fallo",
    )
    payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos adicionales",
    )

    class Meta:
        verbose_name = "Notificación de solicitud de parte"
        verbose_name_plural = "Notificaciones de solicitudes de partes"
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=["recipient", "status", "created_at"],
                name="rep_part_notif_user_idx",
            ),
            models.Index(
                fields=["event", "created_at"],
                name="rep_part_notif_event_idx",
            ),
        ]

    def __str__(self):
        return f"{self.recipient} - {self.title}"

    def clean(self):
        super().clean()
        self.event = str(self.event or "").strip().lower()
        self.title = str(self.title or "").strip()
        self.message = str(self.message or "").strip()
        self.failure_reason = str(self.failure_reason or "").strip()

        if not self.event:
            raise ValidationError({"event": "El evento es obligatorio."})

        if not self.title:
            raise ValidationError({"title": "El título es obligatorio."})

        if not self.message:
            raise ValidationError({"message": "El mensaje es obligatorio."})

        if self.item_id and self.item.request_id != self.request_id:
            raise ValidationError(
                {"item": "El ítem no pertenece a la solicitud."}
            )

        if self.status == self.Status.FAILED and not self.failure_reason:
            raise ValidationError(
                {"failure_reason": "Debe indicar el motivo del fallo."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
