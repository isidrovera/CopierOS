# -*- coding: utf-8 -*-
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class ServicesBaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_updated",
    )

    archived_at = models.DateTimeField(null=True, blank=True, db_index=True)
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_archived",
    )
    archived_reason = models.TextField(blank=True)

    class Meta:
        abstract = True

    @property
    def is_archived(self):
        return self.archived_at is not None

    def archive(self, user=None, reason="", save=True):
        self.archived_at = timezone.now()
        self.archived_by = user
        self.archived_reason = str(reason or "").strip()
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

    def restore(self, user=None, save=True):
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
