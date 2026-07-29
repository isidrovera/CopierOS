# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base import RepairBaseModel
from .repair_part_request import RepairPartRequest
from .repair_part_request_item import RepairPartRequestItem


class RepairPartRequestComment(RepairBaseModel):
    class CommentType(models.TextChoices):
        GENERAL = "general", "General"
        TECHNICAL = "technical", "Técnico"
        AREA_MANAGER = "area_manager", "Jefe de área"
        MANAGEMENT = "management", "Gerencia"
        WAREHOUSE = "warehouse", "Almacén"
        LOGISTICS = "logistics", "Logística"
        PURCHASING = "purchasing", "Compras"
        INFORMATION_REQUEST = (
            "information_request",
            "Solicitud de información",
        )
        INFORMATION_RESPONSE = (
            "information_response",
            "Respuesta de información",
        )
        INTERNAL_NOTE = "internal_note", "Nota interna"

    request = models.ForeignKey(
        RepairPartRequest,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Solicitud",
    )
    item = models.ForeignKey(
        RepairPartRequestItem,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Ítem",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name="Comentario padre",
    )
    comment_type = models.CharField(
        max_length=40,
        choices=CommentType.choices,
        default=CommentType.GENERAL,
        db_index=True,
        verbose_name="Tipo",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="repair_part_request_comments",
        verbose_name="Autor",
    )
    text = models.TextField(
        verbose_name="Comentario",
    )
    is_internal = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Comentario interno",
    )
    mentioned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="repair_part_request_comment_mentions",
        verbose_name="Usuarios mencionados",
    )

    class Meta:
        verbose_name = "Comentario de solicitud de parte"
        verbose_name_plural = "Comentarios de solicitudes de partes"
        ordering = ("created_at",)

    def __str__(self):
        return f"{self.request.code} - {self.author}"

    def clean(self):
        super().clean()
        self.text = str(self.text or "").strip()

        if not self.text:
            raise ValidationError({"text": "El comentario es obligatorio."})

        if self.item_id and self.item.request_id != self.request_id:
            raise ValidationError(
                {"item": "El ítem no pertenece a la solicitud."}
            )

        if self.parent_id and self.parent.request_id != self.request_id:
            raise ValidationError(
                {"parent": "El comentario padre no pertenece a la solicitud."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
