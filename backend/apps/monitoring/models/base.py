# -*- coding: utf-8 -*-
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class MonitoringBaseModel(models.Model):
    """
    Modelo base abstracto para todos los modelos del módulo monitoring.

    Incluye:

    - UUID público.
    - Fechas de creación y actualización.
    - Archivado lógico.
    - Usuario que archivó el registro.
    - Motivo de archivado.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Fecha de creación",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización",
    )

    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de archivado",
    )

    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_archived_records",
        verbose_name="Archivado por",
    )

    archive_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        abstract = True
        ordering = ("-created_at",)

    @property
    def is_archived(self):
        return self.archived_at is not None

    def archive(
        self,
        user=None,
        reason="",
        save=True,
    ):
        if self.archived_at:
            return self

        self.archived_at = timezone.now()
        self.archived_by = user
        self.archive_reason = str(
            reason or ""
        ).strip()

        if save:
            self.save(
                update_fields=[
                    "archived_at",
                    "archived_by",
                    "archive_reason",
                    "updated_at",
                ]
            )

        return self

    def restore(
        self,
        user=None,
        save=True,
    ):
        if not self.archived_at:
            return self

        self.archived_at = None
        self.archived_by = None
        self.archive_reason = ""

        if save:
            self.save(
                update_fields=[
                    "archived_at",
                    "archived_by",
                    "archive_reason",
                    "updated_at",
                ]
            )

        return self

    def clean(self):
        super().clean()

        self.archive_reason = str(
            self.archive_reason or ""
        ).strip()

        if self.archived_by_id and not self.archived_at:
            raise ValidationError(
                {
                    "archived_by": (
                        "No puede existir un usuario de archivado "
                        "sin fecha de archivado."
                    ),
                }
            )

        if self.archive_reason and not self.archived_at:
            raise ValidationError(
                {
                    "archive_reason": (
                        "No puede existir un motivo de archivado "
                        "sin fecha de archivado."
                    ),
                }
            )