# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base import ServicesBaseModel
from .service_part_transfer import ServicePartTransfer


class ServicePartTransferHistory(ServicesBaseModel):
    class Event(models.TextChoices):
        CREATED = "created", "Transferencia creada"
        APPROVED = "approved", "Transferencia aprobada"
        REMOVAL_ASSIGNED = (
            "removal_assigned",
            "Técnico de retiro asignado",
        )
        RECEPTION_ASSIGNED = (
            "reception_assigned",
            "Técnico de recepción asignado",
        )
        REMOVAL_SCHEDULED = (
            "removal_scheduled",
            "Retiro programado",
        )
        RECEPTION_SCHEDULED = (
            "reception_scheduled",
            "Recepción programada",
        )
        REMOVED = "removed", "Parte retirada"
        HANDED_OVER = "handed_over", "Parte entregada"
        IN_TRANSIT = "in_transit", "Parte en traslado"
        RECEIVED = "received", "Parte recibida"
        READY_FOR_INSTALLATION = (
            "ready_for_installation",
            "Lista para instalación",
        )
        INSTALLED = "installed", "Parte instalada"
        RETURNED = "returned", "Parte devuelta"
        REJECTED = "rejected", "Transferencia rechazada"
        CANCELLED = "cancelled", "Transferencia cancelada"
        HOLDER_CHANGED = (
            "holder_changed",
            "Responsable de custodia cambiado",
        )
        LOCATION_CHANGED = (
            "location_changed",
            "Ubicación actualizada",
        )
        CONDITION_UPDATED = (
            "condition_updated",
            "Estado de la parte actualizado",
        )
        NOTE_ADDED = "note_added", "Observación registrada"

    transfer = models.ForeignKey(
        ServicePartTransfer,
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name="Transferencia",
    )

    event = models.CharField(
        max_length=40,
        choices=Event.choices,
        db_index=True,
        verbose_name="Evento",
    )

    previous_status = models.CharField(
        max_length=30,
        choices=ServicePartTransfer.Status.choices,
        blank=True,
        db_index=True,
        verbose_name="Estado anterior",
    )

    new_status = models.CharField(
        max_length=30,
        choices=ServicePartTransfer.Status.choices,
        blank=True,
        db_index=True,
        verbose_name="Estado nuevo",
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_transfer_events",
        verbose_name="Registrado por",
    )

    previous_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="previous_service_part_transfer_custody",
        verbose_name="Responsable anterior",
    )

    new_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="new_service_part_transfer_custody",
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

    previous_condition = models.CharField(
        max_length=30,
        choices=ServicePartTransfer.RemovalCondition.choices,
        blank=True,
        verbose_name="Condición anterior",
    )

    new_condition = models.CharField(
        max_length=30,
        choices=ServicePartTransfer.RemovalCondition.choices,
        blank=True,
        verbose_name="Condición nueva",
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
                    "transfer",
                    "created_at",
                ],
                name="svc_tr_hist_tr_date_idx",
            ),
            models.Index(
                fields=[
                    "event",
                    "created_at",
                ],
                name="svc_tr_hist_ev_date_idx",
            ),
            models.Index(
                fields=[
                    "performed_by",
                    "created_at",
                ],
                name="svc_tr_hist_user_idx",
            ),
            models.Index(
                fields=[
                    "new_status",
                    "created_at",
                ],
                name="svc_tr_hist_st_idx",
            ),
        ]
        verbose_name = "Historial de transferencia"
        verbose_name_plural = "Historiales de transferencias"

    def __str__(self):
        return (
            f"{self.transfer} · "
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

        status_events = {
            self.Event.APPROVED,
            self.Event.REMOVED,
            self.Event.IN_TRANSIT,
            self.Event.RECEIVED,
            self.Event.READY_FOR_INSTALLATION,
            self.Event.INSTALLED,
            self.Event.RETURNED,
            self.Event.REJECTED,
            self.Event.CANCELLED,
        }

        if (
            self.event in status_events
            and not self.new_status
        ):
            raise ValidationError(
                {
                    "new_status": (
                        "Este evento requiere registrar "
                        "el nuevo estado."
                    )
                }
            )

        if (
            self.previous_status
            and self.new_status
            and self.previous_status
            == self.new_status
            and self.event in status_events
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
            self.event
            == self.Event.HOLDER_CHANGED
            and self.previous_holder_id
            == self.new_holder_id
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
            self.event
            == self.Event.LOCATION_CHANGED
            and self.previous_location
            == self.new_location
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
            self.event
            == self.Event.CONDITION_UPDATED
            and self.previous_condition
            == self.new_condition
        ):
            raise ValidationError(
                {
                    "new_condition": (
                        "La nueva condición debe ser "
                        "diferente de la anterior."
                    )
                }
            )

        events_requiring_notes = {
            self.Event.REJECTED,
            self.Event.CANCELLED,
            self.Event.RETURNED,
            self.Event.CONDITION_UPDATED,
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
