# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RentalsBaseModel
from .rental_equipment import RentalEquipment


class RentalPreparation(RentalsBaseModel):
    """
    Orden de preparación de una máquina para alquiler.

    Permite controlar el proceso desde que el equipo ingresa
    al almacén de ANDES hasta que queda listo para ser alquilado.

    El checklist técnico, fotografías, diagnósticos y solicitudes
    de repuestos podrán relacionarse con esta preparación mediante
    los modelos correspondientes.
    """

    class Status(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        PENDING = (
            "pending",
            "Pendiente",
        )
        IN_PROGRESS = (
            "in_progress",
            "En preparación",
        )
        WAITING_PARTS = (
            "waiting_parts",
            "Esperando repuestos",
        )
        OBSERVED = (
            "observed",
            "Observada",
        )
        COMPLETED = (
            "completed",
            "Finalizada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )

    class Result(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        READY_FOR_RENTAL = (
            "ready_for_rental",
            "Lista para alquiler",
        )
        REQUIRES_REPAIR = (
            "requires_repair",
            "Requiere reparación",
        )
        REQUIRES_PARTS = (
            "requires_parts",
            "Requiere repuestos",
        )
        WITH_PROBLEMS = (
            "with_problems",
            "Con problemas",
        )
        FOR_PARTS = (
            "for_parts",
            "Para partes",
        )
        NOT_APPROVED = (
            "not_approved",
            "No aprobada",
        )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código de preparación",
        help_text=(
            "Código interno único de la orden de preparación."
        ),
    )

    rental_equipment = models.ForeignKey(
        RentalEquipment,
        on_delete=models.PROTECT,
        related_name="preparations",
        verbose_name="Equipo de alquiler",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    result = models.CharField(
        max_length=30,
        choices=Result.choices,
        default=Result.PENDING,
        db_index=True,
        verbose_name="Resultado",
    )

    assigned_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rental_preparations_assigned",
        verbose_name="Técnico asignado",
    )

    requested_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de solicitud",
    )

    scheduled_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha programada",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de inicio",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de finalización",
    )

    initial_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador inicial",
    )

    final_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador final",
    )

    request_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de preparación",
    )

    technical_observations = models.TextField(
        blank=True,
        verbose_name="Observaciones técnicas",
    )

    completion_notes = models.TextField(
        blank=True,
        verbose_name="Notas de finalización",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    class Meta:
        verbose_name = "Preparación para alquiler"
        verbose_name_plural = "Preparaciones para alquiler"
        ordering = (
            "-requested_at",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "rental_equipment",
                    "status",
                ],
                name="rent_prep_equipment_status_idx",
            ),
            models.Index(
                fields=[
                    "assigned_technician",
                    "status",
                ],
                name="rent_prep_tech_st_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "scheduled_date",
                ],
                name="rent_prep_status_date_idx",
            ),
            models.Index(
                fields=[
                    "result",
                    "completed_at",
                ],
                name="rent_prep_result_date_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.code} - "
            f"{self.rental_equipment}"
        )

    def clean(self):
        super().clean()

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.request_reason = str(
            self.request_reason or ""
        ).strip()

        self.technical_observations = str(
            self.technical_observations or ""
        ).strip()

        self.completion_notes = str(
            self.completion_notes or ""
        ).strip()

        self.cancellation_reason = str(
            self.cancellation_reason or ""
        ).strip()

        if not self.code:
            raise ValidationError(
                {
                    "code": (
                        "El código de preparación es obligatorio."
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

        duplicate_code = RentalPreparation.objects.filter(
            code__iexact=self.code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe una preparación registrada "
                        "con este código."
                    ),
                }
            )

        if (
            self.initial_meter is not None
            and self.final_meter is not None
            and self.final_meter < self.initial_meter
        ):
            raise ValidationError(
                {
                    "final_meter": (
                        "El contador final no puede ser menor "
                        "que el contador inicial."
                    ),
                }
            )

        if self.status == self.Status.IN_PROGRESS:
            if not self.assigned_technician_id:
                raise ValidationError(
                    {
                        "assigned_technician": (
                            "Debe asignar un técnico antes de "
                            "iniciar la preparación."
                        ),
                    }
                )

            if not self.started_at:
                self.started_at = timezone.now()

        if self.status == self.Status.COMPLETED:
            if self.result == self.Result.PENDING:
                raise ValidationError(
                    {
                        "result": (
                            "Debe indicar el resultado de "
                            "la preparación."
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
            self.status != self.Status.COMPLETED
            and self.completed_at
        ):
            raise ValidationError(
                {
                    "completed_at": (
                        "Solo una preparación finalizada puede "
                        "tener fecha de finalización."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        self.code = str(
            self.code or ""
        ).strip().upper()

        self.request_reason = str(
            self.request_reason or ""
        ).strip()

        self.technical_observations = str(
            self.technical_observations or ""
        ).strip()

        self.completion_notes = str(
            self.completion_notes or ""
        ).strip()

        self.cancellation_reason = str(
            self.cancellation_reason or ""
        ).strip()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )