# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RentalsBaseModel


class RentalContract(RentalsBaseModel):
    """
    Contrato de alquiler administrado por ANDES.

    El contrato relaciona:

    - Cliente.
    - Sede principal.
    - Contacto responsable.
    - Fecha de inicio.
    - Fecha de finalización.
    - Estado contractual.
    - Número y documento de referencia.
    - Condiciones generales del servicio.

    Las máquinas se vinculan al contrato mediante las asignaciones
    de alquiler correspondientes.

    Este modelo no administra precios, facturación ni cobranzas.
    """

    class Status(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        PENDING_APPROVAL = (
            "pending_approval",
            "Pendiente de aprobación",
        )
        APPROVED = (
            "approved",
            "Aprobado",
        )
        ACTIVE = (
            "active",
            "Activo",
        )
        SUSPENDED = (
            "suspended",
            "Suspendido",
        )
        EXPIRED = (
            "expired",
            "Vencido",
        )
        TERMINATED = (
            "terminated",
            "Finalizado",
        )
        CANCELLED = (
            "cancelled",
            "Cancelado",
        )

    class ContractType(models.TextChoices):
        FIXED_TERM = (
            "fixed_term",
            "Plazo determinado",
        )
        OPEN_ENDED = (
            "open_ended",
            "Plazo indeterminado",
        )
        TEMPORARY = (
            "temporary",
            "Temporal",
        )
        DEMONSTRATION = (
            "demonstration",
            "Demostración",
        )
        OTHER = (
            "other",
            "Otro",
        )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código de contrato",
    )

    contract_number = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        verbose_name="Número de contrato",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="rental_contracts",
        verbose_name="Cliente",
    )

    main_branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="main_rental_contracts",
        verbose_name="Sede principal",
    )

    main_contact = models.ForeignKey(
        "partners.PartnerContact",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="main_rental_contracts",
        verbose_name="Contacto principal",
    )

    contract_type = models.CharField(
        max_length=30,
        choices=ContractType.choices,
        default=ContractType.FIXED_TERM,
        db_index=True,
        verbose_name="Tipo de contrato",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de inicio",
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de finalización",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de aprobación",
    )

    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de activación",
    )

    suspended_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de suspensión",
    )

    terminated_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de finalización",
    )

    external_reference = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Referencia externa",
    )

    service_conditions = models.TextField(
        blank=True,
        verbose_name="Condiciones del servicio",
    )

    customer_requirements = models.TextField(
        blank=True,
        verbose_name="Requerimientos del cliente",
    )

    suspension_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de suspensión",
    )

    termination_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de finalización",
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
        verbose_name = "Contrato de alquiler"
        verbose_name_plural = "Contratos de alquiler"
        ordering = (
            "-start_date",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "status",
                ],
                name="rent_ctr_customer_st_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "start_date",
                ],
                name="rent_contract_status_start_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "end_date",
                ],
                name="rent_contract_status_end_idx",
            ),
            models.Index(
                fields=[
                    "contract_type",
                    "status",
                ],
                name="rent_contract_type_status_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.code} - "
            f"{self.customer}"
        )

    def clean(self):
        super().clean()

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.contract_number = str(
            self.contract_number or ""
        ).strip()

        self.external_reference = str(
            self.external_reference or ""
        ).strip()

        self.service_conditions = str(
            self.service_conditions or ""
        ).strip()

        self.customer_requirements = str(
            self.customer_requirements or ""
        ).strip()

        self.suspension_reason = str(
            self.suspension_reason or ""
        ).strip()

        self.termination_reason = str(
            self.termination_reason or ""
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
                        "El código del contrato es obligatorio."
                    ),
                }
            )

        if not self.customer_id:
            raise ValidationError(
                {
                    "customer": (
                        "El cliente es obligatorio."
                    ),
                }
            )

        duplicate_code = RentalContract.objects.filter(
            code__iexact=self.code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe un contrato registrado "
                        "con este código."
                    ),
                }
            )

        if self.contract_number:
            duplicate_number = RentalContract.objects.filter(
                contract_number__iexact=self.contract_number,
            ).exclude(
                pk=self.pk,
            )

            if duplicate_number.exists():
                raise ValidationError(
                    {
                        "contract_number": (
                            "Ya existe un contrato registrado "
                            "con este número."
                        ),
                    }
                )

        if (
            self.main_branch_id
            and self.main_branch.partner_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "main_branch": (
                        "La sede seleccionada no pertenece "
                        "al cliente."
                    ),
                }
            )

        if (
            self.main_contact_id
            and self.main_contact.partner_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "main_contact": (
                        "El contacto seleccionado no pertenece "
                        "al cliente."
                    ),
                }
            )

        if (
            self.main_contact_id
            and self.main_contact.branch_id
            and self.main_branch_id
            and self.main_contact.branch_id
            != self.main_branch_id
        ):
            raise ValidationError(
                {
                    "main_contact": (
                        "El contacto seleccionado pertenece "
                        "a otra sede."
                    ),
                }
            )

        if (
            self.start_date
            and self.end_date
            and self.end_date < self.start_date
        ):
            raise ValidationError(
                {
                    "end_date": (
                        "La fecha de finalización no puede ser "
                        "anterior a la fecha de inicio."
                    ),
                }
            )

        if (
            self.contract_type
            == self.ContractType.FIXED_TERM
            and self.status
            in [
                self.Status.APPROVED,
                self.Status.ACTIVE,
            ]
            and not self.end_date
        ):
            raise ValidationError(
                {
                    "end_date": (
                        "Los contratos de plazo determinado deben "
                        "tener una fecha de finalización."
                    ),
                }
            )

        if self.status == self.Status.APPROVED:
            if not self.approved_at:
                self.approved_at = timezone.now()

        if self.status == self.Status.ACTIVE:
            if not self.start_date:
                raise ValidationError(
                    {
                        "start_date": (
                            "Debe indicar la fecha de inicio "
                            "del contrato."
                        ),
                    }
                )

            if not self.approved_at:
                raise ValidationError(
                    {
                        "approved_at": (
                            "El contrato debe aprobarse antes "
                            "de activarse."
                        ),
                    }
                )

            if not self.activated_at:
                self.activated_at = timezone.now()

        if self.status == self.Status.SUSPENDED:
            if not self.suspension_reason:
                raise ValidationError(
                    {
                        "suspension_reason": (
                            "Debe indicar el motivo "
                            "de suspensión."
                        ),
                    }
                )

            if not self.suspended_at:
                self.suspended_at = timezone.now()

        if self.status == self.Status.TERMINATED:
            if not self.termination_reason:
                raise ValidationError(
                    {
                        "termination_reason": (
                            "Debe indicar el motivo "
                            "de finalización."
                        ),
                    }
                )

            if not self.terminated_at:
                self.terminated_at = timezone.now()

        if self.status == self.Status.CANCELLED:
            if not self.cancellation_reason:
                raise ValidationError(
                    {
                        "cancellation_reason": (
                            "Debe indicar el motivo "
                            "de cancelación."
                        ),
                    }
                )

    def save(self, *args, **kwargs):
        self.code = str(
            self.code or ""
        ).strip().upper()

        self.contract_number = str(
            self.contract_number or ""
        ).strip()

        self.external_reference = str(
            self.external_reference or ""
        ).strip()

        self.service_conditions = str(
            self.service_conditions or ""
        ).strip()

        self.customer_requirements = str(
            self.customer_requirements or ""
        ).strip()

        self.suspension_reason = str(
            self.suspension_reason or ""
        ).strip()

        self.termination_reason = str(
            self.termination_reason or ""
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