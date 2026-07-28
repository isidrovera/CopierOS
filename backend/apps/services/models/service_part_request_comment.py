# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base import ServicesBaseModel
from .service_part_request import ServicePartRequest
from .service_part_request_item import ServicePartRequestItem


class ServicePartRequestComment(ServicesBaseModel):
    class CommentType(models.TextChoices):
        GENERAL = "general", "Comentario general"
        TECHNICAL = "technical", "Comentario técnico"
        MANAGEMENT = "management", "Comentario de gerencia"
        SALES = "sales", "Comentario de ventas"
        LOGISTICS = "logistics", "Comentario de logística"
        STOCK = "stock", "Comentario de almacén"
        INFORMATION_REQUEST = (
            "information_request",
            "Solicitud de información",
        )
        INFORMATION_RESPONSE = (
            "information_response",
            "Respuesta de información",
        )
        DECISION = "decision", "Comentario de decisión"
        INSTALLATION = "installation", "Comentario de instalación"
        INTERNAL_NOTE = "internal_note", "Nota interna"

    request = models.ForeignKey(
        ServicePartRequest,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Pedido",
    )

    request_item = models.ForeignKey(
        ServicePartRequestItem,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Detalle del pedido",
    )

    comment_type = models.CharField(
        max_length=40,
        choices=CommentType.choices,
        default=CommentType.GENERAL,
        db_index=True,
        verbose_name="Tipo de comentario",
    )

    message = models.TextField(
        verbose_name="Comentario",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_request_comments",
        verbose_name="Autor",
    )

    mentioned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="mentioned_service_part_request_comments",
        verbose_name="Usuarios mencionados",
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name="Comentario respondido",
    )

    is_internal = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Uso interno",
    )

    is_edited = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Editado",
    )

    edited_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de edición",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos adicionales",
    )

    class Meta:
        ordering = (
            "created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "request",
                    "created_at",
                ],
                name="svc_pr_com_req_date_idx",
            ),
            models.Index(
                fields=[
                    "request_item",
                    "created_at",
                ],
                name="svc_pr_com_item_date_idx",
            ),
            models.Index(
                fields=[
                    "comment_type",
                    "created_at",
                ],
                name="svc_pr_com_type_date_idx",
            ),
            models.Index(
                fields=[
                    "author",
                    "created_at",
                ],
                name="svc_pr_com_author_idx",
            ),
            models.Index(
                fields=[
                    "is_internal",
                    "created_at",
                ],
                name="svc_pr_com_internal_idx",
            ),
        ]
        verbose_name = "Comentario del pedido"
        verbose_name_plural = "Comentarios de pedidos"

    def __str__(self):
        author_name = (
            self.author.get_full_name()
            if self.author_id and self.author.get_full_name()
            else (
                self.author.get_username()
                if self.author_id
                else "Sistema"
            )
        )

        return (
            f"{self.request.code} · "
            f"{author_name}"
        )

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    def clean(self):
        super().clean()

        self.message = self._clean_text(
            self.message
        )

        if not self.message:
            raise ValidationError(
                {
                    "message": (
                        "Debe escribir un comentario."
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

        if self.parent_id:
            if self.parent_id == self.pk:
                raise ValidationError(
                    {
                        "parent": (
                            "Un comentario no puede responderse "
                            "a sí mismo."
                        )
                    }
                )

            if self.parent.request_id != self.request_id:
                raise ValidationError(
                    {
                        "parent": (
                            "El comentario respondido pertenece "
                            "a otro pedido."
                        )
                    }
                )

            if (
                self.request_item_id
                and self.parent.request_item_id
                and self.parent.request_item_id
                != self.request_item_id
            ):
                raise ValidationError(
                    {
                        "parent": (
                            "El comentario respondido pertenece "
                            "a otro detalle del pedido."
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
