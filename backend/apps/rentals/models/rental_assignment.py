# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone

from apps.rentals.models.base import RentalsBaseModel


class RentalAssignment(RentalsBaseModel):
    """
    Asignación de un equipo de alquiler a un contrato,
    cliente, sede y contacto.

    Esta es la fuente principal para conocer:
    - Qué equipo está asignado.
    - A qué contrato pertenece.
    - En qué cliente y sede se encuentra.
    - Su estado de instalación o retiro.
    """

    class Status(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        RESERVED = (
            "reserved",
            "Reservado",
        )
        INSTALLATION_PENDING = (
            "installation_pending",
            "Pendiente de instalación",
        )
        INSTALLED = (
            "installed",
            "Instalado",
        )
        ACTIVE = (
            "active",
            "Alquiler activo",
        )
        REMOVAL_PENDING = (
            "removal_pending",
            "Pendiente de retiro",
        )
        REMOVED = (
            "removed",
            "Retirado",
        )
        CANCELLED = (
            "cancelled",
            "Cancelado",
        )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código",
    )

    contract = models.ForeignKey(
        "rentals.RentalContract",
        on_delete=models.PROTECT,
        related_name="assignments",
        verbose_name="Contrato",
    )

    rental_equipment = models.ForeignKey(
        "rentals.RentalEquipment",
        on_delete=models.PROTECT,
        related_name="assignments",
        verbose_name="Equipo de alquiler",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="rental_assignments",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        on_delete=models.PROTECT,
        related_name="rental_assignments",
        verbose_name="Sede",
    )

    contact = models.ForeignKey(
        "partners.PartnerContact",
        on_delete=models.PROTECT,
        related_name="rental_assignments",
        null=True,
        blank=True,
        verbose_name="Contacto",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    assigned_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de asignación",
    )

    scheduled_installation_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha programada de instalación",
    )

    installed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de instalación",
    )

    removal_requested_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de solicitud de retiro",
    )

    removed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de retiro",
    )

    site_location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Ubicación del equipo en la sede",
    )

    installation_notes = models.TextField(
        blank=True,
        verbose_name="Indicaciones de instalación",
    )

    removal_reason = models.TextField(
        blank=True,
        verbose_name="Motivo del retiro",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Notas",
    )

    class Meta:
        verbose_name = "Asignación de alquiler"
        verbose_name_plural = "Asignaciones de alquiler"
        ordering = [
            "-assigned_at",
            "-created_at",
        ]
        indexes = [
            models.Index(
                fields=[
                    "contract",
                    "status",
                ],
                name="rent_asg_contract_st_idx",
            ),
            models.Index(
                fields=[
                    "rental_equipment",
                    "status",
                ],
                name="rent_asg_equipment_st_idx",
            ),
            models.Index(
                fields=[
                    "customer",
                    "branch",
                    "status",
                ],
                name="rent_asg_customer_st_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "rental_equipment",
                ],
                condition=models.Q(
                    archived_at__isnull=True,
                    status__in=[
                        "reserved",
                        "installation_pending",
                        "installed",
                        "active",
                        "removal_pending",
                    ],
                ),
                name="unique_active_rental_assignment",
            ),
        ]

    def __str__(self):
        return (
            f"{self.code} - "
            f"{self.rental_equipment} - "
            f"{self.customer}"
        )