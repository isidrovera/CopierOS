# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RentalsBaseModel
from .rental_assignment import RentalAssignment
from .rental_warehouse import RentalWarehouse


class RentalRemoval(RentalsBaseModel):
    """
    Retiro de un equipo alquilado por ANDES.

    Registra:

    - Asignación relacionada.
    - Motivo del retiro.
    - Técnico responsable.
    - Programación.
    - Inicio y finalización.
    - Estado encontrado.
    - Contadores de retiro.
    - Almacén de retorno.
    - Resultado del retiro.
    - Observaciones del técnico y del cliente.

    Las evidencias fotográficas se manejarán posteriormente
    mediante el módulo especializado correspondiente.
    """

    class RemovalType(models.TextChoices):
        CONTRACT_END = (
            "contract_end",
            "Fin de contrato",
        )
        CUSTOMER_REQUEST = (
            "customer_request",
            "Solicitud del cliente",
        )
        PAYMENT_ISSUE = (
            "payment_issue",
            "Problema de pago",
        )
        EQUIPMENT_PROBLEM = (
            "equipment_problem",
            "Problema del equipo",
        )
        EQUIPMENT_REPLACEMENT = (
            "equipment_replacement",
            "Reemplazo de equipo",
        )
        RELOCATION = (
            "relocation",
            "Reubicación",
        )
        TEMPORARY_REMOVAL = (
            "temporary_removal",
            "Retiro temporal",
        )
        COMPANY_DECISION = (
            "company_decision",
            "Decisión de la empresa",
        )
        OTHER = (
            "other",
            "Otro motivo",
        )

    class Status(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        REQUESTED = (
            "requested",
            "Solicitado",
        )
        SCHEDULED = (
            "scheduled",
            "Programado",
        )
        ASSIGNED = (
            "assigned",
            "Técnico asignado",
        )
        IN_TRANSIT = (
            "in_transit",
            "En traslado",
        )
        IN_PROGRESS = (
            "in_progress",
            "En retiro",
        )
        COMPLETED = (
            "completed",
            "Finalizado",
        )
        OBSERVED = (
            "observed",
            "Observado",
        )
        CANCELLED = (
            "cancelled",
            "Cancelado",
        )

    class Result(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        RETURNED_TO_WAREHOUSE = (
            "returned_to_warehouse",
            "Retornado a almacén",
        )
        SENT_TO_REVIEW = (
            "sent_to_review",
            "Enviado a revisión",
        )
        WITH_PROBLEMS = (
            "with_problems",
            "Con problemas",
        )
        FOR_PARTS = (
            "for_parts",
            "Para partes",
        )
        RELOCATED = (
            "relocated",
            "Reubicado",
        )
        NOT_REMOVED = (
            "not_removed",
            "No retirado",
        )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código de retiro",
    )

    rental_assignment = models.ForeignKey(
        RentalAssignment,
        on_delete=models.PROTECT,
        related_name="removals",
        verbose_name="Asignación de alquiler",
    )

    removal_type = models.CharField(
        max_length=40,
        choices=RemovalType.choices,
        default=RemovalType.CUSTOMER_REQUEST,
        db_index=True,
        verbose_name="Tipo de retiro",
    )

    assigned_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rental_removals_assigned",
        verbose_name="Técnico asignado",
    )

    destination_warehouse = models.ForeignKey(
        RentalWarehouse,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rental_removals_received",
        verbose_name="Almacén de destino",
    )

    destination_location = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Ubicación en almacén",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    result = models.CharField(
        max_length=40,
        choices=Result.choices,
        default=Result.PENDING,
        db_index=True,
        verbose_name="Resultado",
    )

    requested_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de solicitud",
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha programada",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Inicio del retiro",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fin del retiro",
    )

    removal_reason = models.TextField(
        verbose_name="Motivo del retiro",
    )

    equipment_condition = models.TextField(
        blank=True,
        verbose_name="Estado encontrado del equipo",
    )

    accessories_received = models.TextField(
        blank=True,
        verbose_name="Accesorios recibidos",
    )

    missing_accessories = models.TextField(
        blank=True,
        verbose_name="Accesorios faltantes",
    )

    final_total_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador total de retiro",
    )

    final_black_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador blanco y negro de retiro",
    )

    final_color_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador color de retiro",
    )

    customer_representative_name = models.CharField(
        max_length=180,
        blank=True,
        verbose_name="Representante del cliente",
    )

    customer_conformity = models.BooleanField(
        default=False,
        verbose_name="Conformidad del cliente",
    )

    technical_observations = models.TextField(
        blank=True,
        verbose_name="Observaciones técnicas",
    )

    customer_observations = models.TextField(
        blank=True,
        verbose_name="Observaciones del cliente",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    class Meta:
        verbose_name = "Retiro de equipo alquilado"
        verbose_name_plural = "Retiros de equipos alquilados"
        ordering = (
            "-requested_at",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "rental_assignment",
                    "status",
                ],
                name="rent_remove_assign_status_idx",
            ),
            models.Index(
                fields=[
                    "assigned_technician",
                    "status",
                ],
                name="rent_remove_tech_status_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "scheduled_at",
                ],
                name="rent_remove_status_date_idx",
            ),
            models.Index(
                fields=[
                    "result",
                    "completed_at",
                ],
                name="rent_remove_result_date_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.code} - "
            f"{self.rental_assignment.rental_equipment}"
        )

    def clean(self):
        super().clean()

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.destination_location = str(
            self.destination_location or ""
        ).strip()

        self.removal_reason = str(
            self.removal_reason or ""
        ).strip()

        self.equipment_condition = str(
            self.equipment_condition or ""
        ).strip()

        self.accessories_received = str(
            self.accessories_received or ""
        ).strip()

        self.missing_accessories = str(
            self.missing_accessories or ""
        ).strip()

        self.customer_representative_name = str(
            self.customer_representative_name or ""
        ).strip()

        self.technical_observations = str(
            self.technical_observations or ""
        ).strip()

        self.customer_observations = str(
            self.customer_observations or ""
        ).strip()

        self.cancellation_reason = str(
            self.cancellation_reason or ""
        ).strip()

        if not self.code:
            raise ValidationError(
                {
                    "code": (
                        "El código de retiro es obligatorio."
                    ),
                }
            )

        if not self.rental_assignment_id:
            raise ValidationError(
                {
                    "rental_assignment": (
                        "La asignación de alquiler es obligatoria."
                    ),
                }
            )

        if not self.removal_reason:
            raise ValidationError(
                {
                    "removal_reason": (
                        "El motivo del retiro es obligatorio."
                    ),
                }
            )

        duplicate_code = RentalRemoval.objects.filter(
            code__iexact=self.code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe un retiro registrado "
                        "con este código."
                    ),
                }
            )

        allowed_assignment_statuses = [
            RentalAssignment.Status.INSTALLED,
            RentalAssignment.Status.ACTIVE,
            RentalAssignment.Status.REMOVAL_PENDING,
        ]

        if (
            self.rental_assignment_id
            and self.rental_assignment.status
            not in allowed_assignment_statuses
        ):
            raise ValidationError(
                {
                    "rental_assignment": (
                        "La asignación seleccionada no se encuentra "
                        "disponible para retiro."
                    ),
                }
            )

        if self.status in [
            self.Status.ASSIGNED,
            self.Status.IN_TRANSIT,
            self.Status.IN_PROGRESS,
            self.Status.COMPLETED,
            self.Status.OBSERVED,
        ]:
            if not self.assigned_technician_id:
                raise ValidationError(
                    {
                        "assigned_technician": (
                            "Debe asignar un técnico."
                        ),
                    }
                )

        if self.status == self.Status.IN_PROGRESS:
            if not self.started_at:
                self.started_at = timezone.now()

        if self.status == self.Status.COMPLETED:
            if self.result == self.Result.PENDING:
                raise ValidationError(
                    {
                        "result": (
                            "Debe indicar el resultado del retiro."
                        ),
                    }
                )

            if not self.started_at:
                raise ValidationError(
                    {
                        "started_at": (
                            "Debe iniciar el retiro antes "
                            "de finalizarlo."
                        ),
                    }
                )

            warehouse_results = [
                self.Result.RETURNED_TO_WAREHOUSE,
                self.Result.SENT_TO_REVIEW,
                self.Result.WITH_PROBLEMS,
                self.Result.FOR_PARTS,
            ]

            if (
                self.result in warehouse_results
                and not self.destination_warehouse_id
            ):
                raise ValidationError(
                    {
                        "destination_warehouse": (
                            "Debe indicar el almacén de destino."
                        ),
                    }
                )

            if not self.completed_at:
                self.completed_at = timezone.now()

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
            self.started_at
            and self.completed_at
            and self.completed_at < self.started_at
        ):
            raise ValidationError(
                {
                    "completed_at": (
                        "La fecha de finalización no puede ser "
                        "anterior al inicio."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        self.code = str(
            self.code or ""
        ).strip().upper()

        self.destination_location = str(
            self.destination_location or ""
        ).strip()

        self.removal_reason = str(
            self.removal_reason or ""
        ).strip()

        self.equipment_condition = str(
            self.equipment_condition or ""
        ).strip()

        self.accessories_received = str(
            self.accessories_received or ""
        ).strip()

        self.missing_accessories = str(
            self.missing_accessories or ""
        ).strip()

        self.customer_representative_name = str(
            self.customer_representative_name or ""
        ).strip()

        self.technical_observations = str(
            self.technical_observations or ""
        ).strip()

        self.customer_observations = str(
            self.customer_observations or ""
        ).strip()

        self.cancellation_reason = str(
            self.cancellation_reason or ""
        ).strip()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )