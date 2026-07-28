# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.equipment.models import Equipment

from .base import ServicesBaseModel
from .service_part_request_item import ServicePartRequestItem
from .service_reusable_part import ServiceReusablePart


class ServicePartTransfer(ServicesBaseModel):
    class Status(models.TextChoices):
        PENDING_DECISION = (
            "pending_decision",
            "Pendiente de decisión",
        )
        APPROVED = "approved", "Aprobado"
        ASSIGNED_FOR_REMOVAL = (
            "assigned_for_removal",
            "Retiro asignado",
        )
        REMOVED = "removed", "Retirado"
        IN_TRANSIT = "in_transit", "En traslado"
        PENDING_RECEPTION = (
            "pending_reception",
            "Pendiente de recepción",
        )
        RECEIVED = "received", "Recibido"
        READY_FOR_INSTALLATION = (
            "ready_for_installation",
            "Listo para instalación",
        )
        INSTALLED = "installed", "Instalado"
        RETURNED = "returned", "Devuelto"
        REJECTED = "rejected", "Rechazado"
        CANCELLED = "cancelled", "Cancelado"

    class RemovalCondition(models.TextChoices):
        OPERATIONAL = "operational", "Operativo"
        OPERATIONAL_WITH_NOTES = (
            "operational_with_notes",
            "Operativo con observaciones",
        )
        TO_REVIEW = "to_review", "Por revisar"
        REPAIRED = "repaired", "Reparado"
        DEFECTIVE = "defective", "Defectuoso"
        INCOMPLETE = "incomplete", "Incompleto"
        NOT_USABLE = "not_usable", "No utilizable"

    part_request_item = models.OneToOneField(
        ServicePartRequestItem,
        on_delete=models.CASCADE,
        related_name="transfer",
        verbose_name="Detalle del pedido",
    )

    reusable_part = models.ForeignKey(
        ServiceReusablePart,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="transfers",
        verbose_name="Parte reutilizable",
    )

    source_equipment = models.ForeignKey(
        Equipment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="service_part_transfers_out",
        verbose_name="Equipo de origen",
    )

    destination_equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="service_part_transfers_in",
        verbose_name="Equipo de destino",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING_DECISION,
        db_index=True,
        verbose_name="Estado",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_transfers_approved",
        verbose_name="Aprobado por",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de aprobación",
    )

    removal_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="service_part_transfers_to_remove",
        verbose_name="Técnico de retiro",
    )

    removal_scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha programada de retiro",
    )

    removed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de retiro",
    )

    removal_condition = models.CharField(
        max_length=30,
        choices=RemovalCondition.choices,
        blank=True,
        db_index=True,
        verbose_name="Estado al retirar",
    )

    removal_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones del retiro",
    )

    reception_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="service_part_transfers_to_receive",
        verbose_name="Técnico de recepción y reposición",
    )

    reception_scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha programada de recepción",
    )

    received_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de recepción",
    )

    reception_condition = models.CharField(
        max_length=30,
        choices=RemovalCondition.choices,
        blank=True,
        db_index=True,
        verbose_name="Estado al recibir",
    )

    reception_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones de recepción",
    )

    handed_over_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_transfers_handed_over",
        verbose_name="Entregado por",
    )

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_transfers_received",
        verbose_name="Recibido por",
    )

    current_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_transfers_in_custody",
        verbose_name="Responsable actual",
    )

    current_location = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
        verbose_name="Ubicación actual",
    )

    installed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de instalación",
    )

    installed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_part_transfers_installed",
        verbose_name="Instalado por",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones generales",
    )

    class Meta:
        ordering = (
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "status",
                    "created_at",
                ],
                name="svc_transfer_st_date_idx",
            ),
            models.Index(
                fields=[
                    "source_equipment",
                    "status",
                ],
                name="svc_transfer_src_st_idx",
            ),
            models.Index(
                fields=[
                    "destination_equipment",
                    "status",
                ],
                name="svc_transfer_dst_st_idx",
            ),
            models.Index(
                fields=[
                    "removal_technician",
                    "status",
                ],
                name="svc_transfer_rem_st_idx",
            ),
            models.Index(
                fields=[
                    "reception_technician",
                    "status",
                ],
                name="svc_transfer_rec_st_idx",
            ),
            models.Index(
                fields=[
                    "current_holder",
                    "status",
                ],
                name="svc_transfer_hold_st_idx",
            ),
        ]
        verbose_name = "Transferencia de parte"
        verbose_name_plural = "Transferencias de partes"

    def __str__(self):
        return (
            f"{self.part_request_item.display_name} · "
            f"{self.get_status_display()}"
        )

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    def clean(self):
        super().clean()

        self.removal_notes = self._clean_text(
            self.removal_notes
        )
        self.reception_notes = self._clean_text(
            self.reception_notes
        )
        self.current_location = self._clean_text(
            self.current_location
        )
        self.notes = self._clean_text(
            self.notes
        )

        if (
            self.source_equipment_id
            and self.destination_equipment_id
            and self.source_equipment_id
            == self.destination_equipment_id
        ):
            raise ValidationError(
                {
                    "destination_equipment": (
                        "El equipo de destino debe ser "
                        "diferente del equipo de origen."
                    )
                }
            )

        request_order_equipment_id = (
            self.part_request_item
            .request
            .service_order
            .equipment_id
        )

        if (
            self.destination_equipment_id
            != request_order_equipment_id
        ):
            raise ValidationError(
                {
                    "destination_equipment": (
                        "El equipo de destino debe coincidir "
                        "con el equipo de la OS que originó "
                        "el pedido."
                    )
                }
            )

        if (
            self.reusable_part_id
            and self.source_equipment_id
            and self.reusable_part.source_equipment_id
            and self.reusable_part.source_equipment_id
            != self.source_equipment_id
        ):
            raise ValidationError(
                {
                    "source_equipment": (
                        "El equipo de origen no coincide con "
                        "la procedencia registrada de la parte."
                    )
                }
            )

        statuses_requiring_approval = {
            self.Status.APPROVED,
            self.Status.ASSIGNED_FOR_REMOVAL,
            self.Status.REMOVED,
            self.Status.IN_TRANSIT,
            self.Status.PENDING_RECEPTION,
            self.Status.RECEIVED,
            self.Status.READY_FOR_INSTALLATION,
            self.Status.INSTALLED,
        }

        if (
            self.status in statuses_requiring_approval
            and not self.approved_by_id
        ):
            raise ValidationError(
                {
                    "approved_by": (
                        "Debe registrar quién aprobó "
                        "la transferencia."
                    )
                }
            )

        statuses_requiring_removal_technician = {
            self.Status.ASSIGNED_FOR_REMOVAL,
            self.Status.REMOVED,
            self.Status.IN_TRANSIT,
            self.Status.PENDING_RECEPTION,
            self.Status.RECEIVED,
            self.Status.READY_FOR_INSTALLATION,
            self.Status.INSTALLED,
        }

        if (
            self.status in statuses_requiring_removal_technician
            and not self.removal_technician_id
        ):
            raise ValidationError(
                {
                    "removal_technician": (
                        "Debe asignar un técnico de retiro."
                    )
                }
            )

        statuses_requiring_reception_technician = {
            self.Status.PENDING_RECEPTION,
            self.Status.RECEIVED,
            self.Status.READY_FOR_INSTALLATION,
            self.Status.INSTALLED,
        }

        if (
            self.status in statuses_requiring_reception_technician
            and not self.reception_technician_id
        ):
            raise ValidationError(
                {
                    "reception_technician": (
                        "Debe asignar un técnico de recepción "
                        "y reposición."
                    )
                }
            )

        if (
            self.status
            in {
                self.Status.REMOVED,
                self.Status.IN_TRANSIT,
                self.Status.PENDING_RECEPTION,
                self.Status.RECEIVED,
                self.Status.READY_FOR_INSTALLATION,
                self.Status.INSTALLED,
            }
            and not self.removed_at
        ):
            raise ValidationError(
                {
                    "removed_at": (
                        "Debe registrar la fecha de retiro."
                    )
                }
            )

        if (
            self.status
            in {
                self.Status.RECEIVED,
                self.Status.READY_FOR_INSTALLATION,
                self.Status.INSTALLED,
            }
            and not self.received_at
        ):
            raise ValidationError(
                {
                    "received_at": (
                        "Debe registrar la fecha de recepción."
                    )
                }
            )

        if (
            self.status == self.Status.INSTALLED
            and not self.installed_at
        ):
            raise ValidationError(
                {
                    "installed_at": (
                        "Debe registrar la fecha de instalación."
                    )
                }
            )

        if (
            self.status == self.Status.INSTALLED
            and not self.installed_by_id
        ):
            raise ValidationError(
                {
                    "installed_by": (
                        "Debe registrar quién realizó "
                        "la instalación."
                    )
                }
            )

        if (
            self.status == self.Status.IN_CUSTODY
            if hasattr(self.Status, "IN_CUSTODY")
            else False
        ):
            if not self.current_holder_id:
                raise ValidationError(
                    {
                        "current_holder": (
                            "Debe registrar quién tiene "
                            "la parte."
                        )
                    }
                )

    def save(self, *args, **kwargs):
        now = timezone.now()

        if (
            self.status
            == self.Status.APPROVED
            and not self.approved_at
        ):
            self.approved_at = now

        if (
            self.status
            == self.Status.REMOVED
            and not self.removed_at
        ):
            self.removed_at = now

        if (
            self.status
            == self.Status.RECEIVED
            and not self.received_at
        ):
            self.received_at = now

        if (
            self.status
            == self.Status.INSTALLED
            and not self.installed_at
        ):
            self.installed_at = now

        if (
            self.status
            in {
                self.Status.REMOVED,
                self.Status.IN_TRANSIT,
                self.Status.PENDING_RECEPTION,
            }
            and not self.current_holder_id
            and self.removal_technician_id
        ):
            self.current_holder = self.removal_technician

        if (
            self.status
            in {
                self.Status.RECEIVED,
                self.Status.READY_FOR_INSTALLATION,
            }
            and not self.current_holder_id
            and self.reception_technician_id
        ):
            self.current_holder = self.reception_technician

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )
