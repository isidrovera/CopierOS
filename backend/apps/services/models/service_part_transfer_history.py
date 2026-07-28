# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.equipment.models import Equipment

from .base import ServicesBaseModel
from .service_reusable_part import ServiceReusablePart


class ServiceReusablePartHistory(ServicesBaseModel):
    class Event(models.TextChoices):
        CREATED = "created", "Parte registrada"
        EVALUATED = "evaluated", "Parte evaluada"
        RESERVED = "reserved", "Parte reservada"
        REMOVAL_PENDING = (
            "removal_pending",
            "Pendiente de retiro",
        )
        REMOVED = "removed", "Parte retirada"
        CUSTODY_ASSIGNED = (
            "custody_assigned",
            "Custodia asignada",
        )
        LOCATION_CHANGED = (
            "location_changed",
            "Ubicación actualizada",
        )
        CONDITION_CHANGED = (
            "condition_changed",
            "Condición actualizada",
        )
        STATUS_CHANGED = (
            "status_changed",
            "Estado actualizado",
        )
        RECEIVED = "received", "Parte recibida"
        READY_FOR_INSTALLATION = (
            "ready_for_installation",
            "Lista para instalación",
        )
        INSTALLED = "installed", "Parte instalada"
        RETURNED = "returned", "Parte devuelta"
        LOST = "lost", "Parte no localizada"
        DISCARDED = "discarded", "Parte descartada"
        NOTE_ADDED = "note_added", "Observación registrada"

    reusable_part = models.ForeignKey(
        ServiceReusablePart,
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name="Parte reutilizable",
    )

    event = models.CharField(
        max_length=40,
        choices=Event.choices,
        db_index=True,
        verbose_name="Evento",
    )

    previous_status = models.CharField(
        max_length=30,
        choices=ServiceReusablePart.Status.choices,
        blank=True,
        db_index=True,
        verbose_name="Estado anterior",
    )

    new_status = models.CharField(
        max_length=30,
        choices=ServiceReusablePart.Status.choices,
        blank=True,
        db_index=True,
        verbose_name="Estado nuevo",
    )

    previous_condition = models.CharField(
        max_length=30,
        choices=ServiceReusablePart.Condition.choices,
        blank=True,
        verbose_name="Condición anterior",
    )

    new_condition = models.CharField(
        max_length=30,
        choices=ServiceReusablePart.Condition.choices,
        blank=True,
        verbose_name="Condición nueva",
    )

    previous_equipment = models.ForeignKey(
        Equipment,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="previous_reusable_part_history",
        verbose_name="Equipo anterior",
    )

    new_equipment = models.ForeignKey(
        Equipment,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="new_reusable_part_history",
        verbose_name="Equipo nuevo",
    )

    previous_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="previous_reusable_part_custody",
        verbose_name="Responsable anterior",
    )

    new_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="new_reusable_part_custody",
        verbose_name="Responsable nuevo",
    )

    previous_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ubicación anterior",
    )

    new_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ubicación nueva",
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_reusable_part_events",
        verbose_name="Registrado por",
    )

    source = models.CharField(
        max_length=30,
        default="web",
        db_index=True,
        verbose_name="Origen",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
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
                    "reusable_part",
                    "created_at",
                ],
                name="svc_reuse_hist_part_idx",
            ),
            models.Index(
                fields=[
                    "event",
                    "created_at",
                ],
                name="svc_reuse_hist_event_idx",
            ),
            models.Index(
                fields=[
                    "new_status",
                    "created_at",
                ],
                name="svc_reuse_hist_status_idx",
            ),
            models.Index(
                fields=[
                    "performed_by",
                    "created_at",
                ],
                name="svc_reuse_hist_user_idx",
            ),
        ]
        verbose_name = "Historial de parte reutilizable"
        verbose_name_plural = "Historiales de partes reutilizables"

    def __str__(self):
        return (
            f"{self.reusable_part.code} · "
            f"{self.get_event_display()}"
        )

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    def clean(self):
        super().clean()

        self.previous_location = self._clean_text(
            self.previous_location
        )

        self.new_location = self._clean_text(
            self.new_location
        )

        self.source = (
            self._clean_text(
                self.source
            ).lower()
            or "web"
        )

        self.notes = self._clean_text(
            self.notes
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
            self.event == self.Event.STATUS_CHANGED
            and self.previous_status == self.new_status
        ):
            raise ValidationError(
                {
                    "new_status": (
                        "El nuevo estado debe ser diferente "
                        "del anterior."
                    )
                }
            )

        if (
            self.event == self.Event.CONDITION_CHANGED
            and self.previous_condition == self.new_condition
        ):
            raise ValidationError(
                {
                    "new_condition": (
                        "La nueva condición debe ser diferente "
                        "de la anterior."
                    )
                }
            )

        if (
            self.event == self.Event.CUSTODY_ASSIGNED
            and self.previous_holder_id == self.new_holder_id
        ):
            raise ValidationError(
                {
                    "new_holder": (
                        "El nuevo responsable debe ser "
                        "diferente del anterior."
                    )
                }
            )

        if (
            self.event == self.Event.LOCATION_CHANGED
            and self.previous_location == self.new_location
        ):
            raise ValidationError(
                {
                    "new_location": (
                        "La nueva ubicación debe ser "
                        "diferente de la anterior."
                    )
                }
            )

        if (
            self.event == self.Event.INSTALLED
            and not self.new_equipment_id
        ):
            raise ValidationError(
                {
                    "new_equipment": (
                        "Debe indicar el equipo donde "
                        "quedó instalada la parte."
                    )
                }
            )

        events_requiring_notes = {
            self.Event.LOST,
            self.Event.DISCARDED,
            self.Event.RETURNED,
            self.Event.CONDITION_CHANGED,
        }

        if (
            self.event in events_requiring_notes
            and not self.notes
        ):
            raise ValidationError(
                {
                    "notes": (
                        "Este evento requiere una observación."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )
