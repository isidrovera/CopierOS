# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RentalsBaseModel
from .rental_contract import RentalContract
from .rental_equipment import RentalEquipment


class RentalContractEquipment(RentalsBaseModel):
    """
    Vincula una máquina de alquiler con un contrato de ANDES.

    Conserva:

    - Contrato.
    - Equipo asignado.
    - Sede.
    - Contacto.
    - Estado de la relación.
    - Fecha de asignación.
    - Fecha de instalación.
    - Fecha de retiro.
    - Ubicación dentro de la sede.

    La instalación, retiro y reemplazo se manejan mediante
    sus modelos especializados.
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
        REPLACED = (
            "replaced",
            "Reemplazada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )

    contract = models.ForeignKey(
        RentalContract,
        on_delete=models.PROTECT,
        related_name="contract_equipment",
        verbose_name="Contrato",
    )

    rental_equipment = models.ForeignKey(
        RentalEquipment,
        on_delete=models.PROTECT,
        related_name="contract_relations",
        verbose_name="Equipo de alquiler",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        on_delete=models.PROTECT,
        related_name="rental_contract_equipment",
        verbose_name="Sede",
    )

    contact = models.ForeignKey(
        "partners.PartnerContact",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rental_contract_equipment",
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
        verbose_name = "Equipo asignado a contrato"
        verbose_name_plural = "Equipos asignados a contratos"
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
                name="unique_active_rental_contract_equipment",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "contract",
                    "status",
                ],
                name="rent_contract_eq_contract_idx",
            ),
            models.Index(
                fields=[
                    "rental_equipment",
                    "status",
                ],
                name="rent_contract_eq_equipment_idx",
            ),
            models.Index(
                fields=[
                    "branch",
                    "status",
                ],
                name="rent_contract_eq_branch_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "scheduled_installation_date",
                ],
                name="rent_contract_eq_install_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.contract.code} - "
            f"{self.rental_equipment}"
        )

    def clean(self):
        super().clean()

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

        if not self.contract_id:
            raise ValidationError(
                {
                    "contract": (
                        "El contrato es obligatorio."
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

        if not self.branch_id:
            raise ValidationError(
                {
                    "branch": (
                        "La sede es obligatoria."
                    ),
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
                        "pueden asignarse a contratos."
                    ),
                }
            )

        if (
            self.contract_id
            and self.branch_id
            and self.branch.partner_id
            != self.contract.customer_id
        ):
            raise ValidationError(
                {
                    "branch": (
                        "La sede seleccionada no pertenece "
                        "al cliente del contrato."
                    ),
                }
            )

        if (
            self.contract_id
            and self.contact_id
            and self.contact.partner_id
            != self.contract.customer_id
        ):
            raise ValidationError(
                {
                    "contact": (
                        "El contacto seleccionado no pertenece "
                        "al cliente del contrato."
                    ),
                }
            )

        if (
            self.contact_id
            and self.contact.branch_id
            and self.contact.branch_id
            != self.branch_id
        ):
            raise ValidationError(
                {
                    "contact": (
                        "El contacto seleccionado pertenece "
                        "a otra sede."
                    ),
                }
            )

        allowed_contract_statuses = [
            RentalContract.Status.APPROVED,
            RentalContract.Status.ACTIVE,
        ]

        if (
            self.status
            not in [
                self.Status.DRAFT,
                self.Status.CANCELLED,
            ]
            and self.contract.status
            not in allowed_contract_statuses
        ):
            raise ValidationError(
                {
                    "contract": (
                        "El contrato debe estar aprobado o activo "
                        "para asignar equipos."
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
            active_relation = RentalContractEquipment.objects.filter(
                rental_equipment_id=self.rental_equipment_id,
                status__in=active_statuses,
                archived_at__isnull=True,
            ).exclude(
                pk=self.pk,
            )

            if active_relation.exists():
                raise ValidationError(
                    {
                        "rental_equipment": (
                            "El equipo ya se encuentra asignado "
                            "a un contrato activo."
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
            if not self.removal_reason:
                raise ValidationError(
                    {
                        "removal_reason": (
                            "Debe indicar el motivo del retiro."
                        ),
                    }
                )

            if not self.removal_requested_at:
                self.removal_requested_at = timezone.now()

        if self.status == self.Status.REMOVED:
            if not self.removal_reason:
                raise ValidationError(
                    {
                        "removal_reason": (
                            "Debe indicar el motivo del retiro."
                        ),
                    }
                )

            if not self.removed_at:
                self.removed_at = timezone.now()

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