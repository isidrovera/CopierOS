# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RentalsBaseModel
from .rental_equipment import RentalEquipment


class RentalAssignment(RentalsBaseModel):
    """
    Asignación de una máquina de ANDES a un cliente.

    Relaciona el equipo con:

    - Cliente.
    - Sede.
    - Contacto.
    - Fecha de asignación.
    - Instalación.
    - Retiro.
    - Ubicación física dentro de la sede.

    Conserva el historial de asignaciones sin reemplazar
    las órdenes de instalación, retiro o servicio técnico.
    """

    class Status(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        RESERVED = (
            "reserved",
            "Reservada",
        )
        INSTALLATION_PENDING = (
            "installation_pending",
            "Pendiente de instalación",
        )
        INSTALLED = (
            "installed",
            "Instalada",
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
            "Retirada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código de asignación",
    )

    rental_equipment = models.ForeignKey(
        RentalEquipment,
        on_delete=models.PROTECT,
        related_name="rental_assignments",
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
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rental_assignments",
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
        db_index=True,
        verbose_name="Fecha de instalación",
    )

    removal_requested_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de solicitud de retiro",
    )

    removed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de retiro",
    )

    site_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ubicación dentro de la sede",
        help_text=(
            "Ejemplo: recepción, segundo piso, administración "
            "o área de operaciones."
        ),
    )

    installation_notes = models.TextField(
        blank=True,
        verbose_name="Indicaciones de instalación",
    )

    removal_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de retiro",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Asignación de equipo de alquiler"
        verbose_name_plural = "Asignaciones de equipos de alquiler"
        ordering = (
            "-assigned_at",
            "-created_at",
        )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "rental_equipment",
                ],
                condition=models.Q(
                    status__in=[
                        "reserved",
                        "installation_pending",
                        "installed",
                        "active",
                        "removal_pending",
                    ],
                    archived_at__isnull=True,
                ),
                name="unique_active_rental_equipment_assignment",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "status",
                ],
                name="rent_assign_customer_status_idx",
            ),
            models.Index(
                fields=[
                    "branch",
                    "status",
                ],
                name="rent_assign_branch_status_idx",
            ),
            models.Index(
                fields=[
                    "rental_equipment",
                    "status",
                ],
                name="rent_assign_equipment_status_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "scheduled_installation_date",
                ],
                name="rent_assign_status_install_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.code} - "
            f"{self.rental_equipment} - "
            f"{self.customer}"
        )

    def clean(self):
        super().clean()

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.site_location = str(
            self.site_location or ""
        ).strip()

        self.installation_notes = str(
            self.installation_notes or ""
        ).strip()

        self.removal_reason = str(
            self.removal_reason or ""
        ).strip()

        self.cancellation_reason = str(
            self.cancellation_reason or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        if not self.code:
            raise ValidationError(
                {
                    "code": (
                        "El código de asignación es obligatorio."
                    ),
                }
            )

        if not self.rental_equipment_id:
            raise ValidationError(
                {
                    "rental_equipment": (
                        "El equipo de alquiler es obligatorio."
                    ),
                }
            )

        if not self.customer_id:
            raise ValidationError(
                {
                    "customer": "El cliente es obligatorio.",
                }
            )

        if not self.branch_id:
            raise ValidationError(
                {
                    "branch": "La sede es obligatoria.",
                }
            )

        if (
            self.rental_equipment_id
            and self.rental_equipment.purpose
            != RentalEquipment.EquipmentPurpose.RENTAL
        ):
            raise ValidationError(
                {
                    "rental_equipment": (
                        "Solo los equipos destinados a alquiler "
                        "pueden asignarse a clientes."
                    ),
                }
            )

        if (
            self.branch_id
            and self.customer_id
            and self.branch.partner_id != self.customer_id
        ):
            raise ValidationError(
                {
                    "branch": (
                        "La sede seleccionada no pertenece "
                        "al cliente."
                    ),
                }
            )

        if (
            self.contact_id
            and self.customer_id
            and self.contact.partner_id != self.customer_id
        ):
            raise ValidationError(
                {
                    "contact": (
                        "El contacto seleccionado no pertenece "
                        "al cliente."
                    ),
                }
            )

        if (
            self.contact_id
            and self.contact.branch_id
            and self.contact.branch_id != self.branch_id
        ):
            raise ValidationError(
                {
                    "contact": (
                        "El contacto seleccionado pertenece "
                        "a otra sede."
                    ),
                }
            )

        duplicate_code = RentalAssignment.objects.filter(
            code__iexact=self.code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe una asignación registrada "
                        "con este código."
                    ),
                }
            )

        active_statuses = [
            self.Status.RESERVED,
            self.Status.INSTALLATION_PENDING,
            self.Status.INSTALLED,
            self.Status.ACTIVE,
            self.Status.REMOVAL_PENDING,
        ]

        if self.status in active_statuses:
            active_assignment = RentalAssignment.objects.filter(
                rental_equipment_id=self.rental_equipment_id,
                status__in=active_statuses,
                archived_at__isnull=True,
            ).exclude(
                pk=self.pk,
            )

            if active_assignment.exists():
                raise ValidationError(
                    {
                        "rental_equipment": (
                            "El equipo ya tiene una asignación "
                            "activa."
                        ),
                    }
                )

        if self.status == self.Status.INSTALLED:
            if not self.installed_at:
                self.installed_at = timezone.now()

        if self.status == self.Status.ACTIVE:
            if not self.installed_at:
                raise ValidationError(
                    {
                        "installed_at": (
                            "Debe registrar la instalación antes "
                            "de activar el alquiler."
                        ),
                    }
                )

        if self.status == self.Status.REMOVAL_PENDING:
            if not self.removal_requested_at:
                self.removal_requested_at = timezone.now()

            if not self.removal_reason:
                raise ValidationError(
                    {
                        "removal_reason": (
                            "Debe indicar el motivo del retiro."
                        ),
                    }
                )

        if self.status == self.Status.REMOVED:
            if not self.removed_at:
                self.removed_at = timezone.now()

            if not self.removal_reason:
                raise ValidationError(
                    {
                        "removal_reason": (
                            "Debe indicar el motivo del retiro."
                        ),
                    }
                )

        if self.status == self.Status.CANCELLED:
            if not self.cancellation_reason:
                raise ValidationError(
                    {
                        "cancellation_reason": (
                            "Debe indicar el motivo de cancelación."
                        ),
                    }
                )

        if (
            self.installed_at
            and self.removed_at
            and self.removed_at < self.installed_at
        ):
            raise ValidationError(
                {
                    "removed_at": (
                        "La fecha de retiro no puede ser anterior "
                        "a la instalación."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        self.code = str(
            self.code or ""
        ).strip().upper()

        self.site_location = str(
            self.site_location or ""
        ).strip()

        self.installation_notes = str(
            self.installation_notes or ""
        ).strip()

        self.removal_reason = str(
            self.removal_reason or ""
        ).strip()

        self.cancellation_reason = str(
            self.cancellation_reason or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )