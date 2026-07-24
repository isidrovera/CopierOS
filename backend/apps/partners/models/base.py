# -*- coding: utf-8 -*-
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class PartnerBaseModel(models.Model):
    """
    Modelo base abstracto para los registros del módulo partners.

    Incluye:

    - UUID como clave primaria.
    - Fecha de creación y modificación.
    - Usuario creador y modificador.
    - Archivado lógico.
    - Usuario, fecha y motivo del archivado.

    Al ser abstracto, Django no creará una tabla independiente
    para este modelo.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Fecha de creación",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        db_index=True,
        verbose_name="Fecha de modificación",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_updated",
        verbose_name="Modificado por",
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
        related_name="%(app_label)s_%(class)s_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo del archivado",
    )

    class Meta:
        abstract = True
        ordering = (
            "-created_at",
        )

    @property
    def is_archived(self):
        """
        Indica si el registro se encuentra archivado.
        """

        return self.archived_at is not None

    def archive(
        self,
        user=None,
        reason="",
        save=True,
    ):
        """
        Archiva lógicamente el registro.

        No elimina información de la base de datos.
        """

        if self.archived_at is not None:
            return self

        self.archived_at = timezone.now()
        self.archived_by = user
        self.archived_reason = str(
            reason or ""
        ).strip()

        if user:
            self.updated_by = user

        if save:
            self.save(
                update_fields=[
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                    "updated_by",
                    "updated_at",
                ]
            )

        return self

    def restore(
        self,
        user=None,
        save=True,
    ):
        """
        Restaura un registro previamente archivado.
        """

        self.archived_at = None
        self.archived_by = None
        self.archived_reason = ""

        if user:
            self.updated_by = user

        if save:
            self.save(
                update_fields=[
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                    "updated_by",
                    "updated_at",
                ]
            )

        return self