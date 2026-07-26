# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RentalsBaseModel
from .rental_assignment import RentalAssignment
from .rental_equipment import RentalEquipment


class RentalReplacement(RentalsBaseModel):
    """
    Reemplazo de un equipo alquilado por ANDES.

    Registra:

    - Asignación activa afectada.
    - Equipo retirado.
    - Equipo entregado como reemplazo.
    - Motivo del cambio.
    - Técnico responsable.
    - Fechas de programación y ejecución.
    - Contadores de ambos equipos.
    - Resultado del reemplazo.
    - Observaciones técnicas y del cliente.

    El historial de lecturas se registrará mediante el modelo
    especializado de contadores por equipo.
    """

    class ReplacementType(models.TextChoices):
        TEMPORARY = (
            "temporary",
            "Reemplazo temporal",
        )
        PERMANENT = (
            "permanent",
            "Reemplazo permanente",
        )
        EMERGENCY = (
            "emergency",
            "Reemplazo de emergencia",
        )

    class Reason(models.TextChoices):
        TECHNICAL_FAILURE = (
            "technical_failure",
            "Falla técnica",
        )
        REQUIRES_WORKSHOP = (
            "requires_workshop",
            "Requiere ingreso a taller",
        )
        PARTS_UNAVAILABLE = (
            "parts_unavailable",
            "Repuestos no disponibles",
        )
        REPEATED_FAILURES = (
            "repeated_failures",
            "Fallas repetitivas",
        )
        CAPACITY_CHANGE = (
            "capacity_change",
            "Cambio de capacidad",
        )
        MODEL_CHANGE = (
            "model_change",
            "Cambio de modelo",
        )
        CUSTOMER_REQUEST = (
            "customer_request",
            "Solicitud del cliente",
        )
        CONTRACT_CHANGE = (
            "contract_change",
            "Cambio de contrato",
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
        APPROVED = (
            "approved",
            "Aprobado",
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
            "En reemplazo",
        )
        COMPLETED = (
            "completed",
            "Finalizado",
        )
        OBSERVED = (
            "observed",
            "Observado",
        )
        REJECTED = (
            "rejected",
            "Rechazado",
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
        REPLACED = (
            "replaced",
            "Equipo reemplazado",
        )
        REPLACED_WITH_OBSERVATIONS = (
            "replaced_with_observations",
            "Reemplazado con observaciones",
        )
        NOT_REPLACED = (
            "not_replaced",
            "No reemplazado",
        )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código de reemplazo",
    )

    rental_assignment = models.ForeignKey(
        RentalAssignment,
        on_delete=models.PROTECT,
        related_name="replacements",
        verbose_name="Asignación afectada",
    )

    outgoing_equipment = models.ForeignKey(
        RentalEquipment,
        on_delete=models.PROTECT,
        related_name="replacement_departures",
        verbose_name="Equipo retirado",
    )

    incoming_equipment = models.ForeignKey(
        RentalEquipment,
        on_delete=models.PROTECT,
        related_name="replacement_entries",
        verbose_name="Equipo de reemplazo",
    )

    replacement_type = models.CharField(
        max_length=30,
        choices=ReplacementType.choices,
        default=ReplacementType.TEMPORARY,
        db_index=True,
        verbose_name="Tipo de reemplazo",
    )

    reason = models.CharField(
        max_length=40,
        choices=Reason.choices,
        default=Reason.TECHNICAL_FAILURE,
        db_index=True,
        verbose_name="Motivo",
    )

    reason_detail = models.TextField(
        blank=True,
        verbose_name="Detalle del motivo",
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

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rental_replacements_approved",
        verbose_name="Aprobado por",
    )

    assigned_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rental_replacements_assigned",
        verbose_name="Técnico asignado",
    )

    requested_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de solicitud",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de aprobación",
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
        verbose_name="Inicio del reemplazo",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fin del reemplazo",
    )

    outgoing_total_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador total del equipo retirado",
    )

    outgoing_black_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador blanco y negro del equipo retirado",
    )

    outgoing_color_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador color del equipo retirado",
    )

    incoming_total_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador total del equipo de reemplazo",
    )

    incoming_black_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador blanco y negro del equipo de reemplazo",
    )

    incoming_color_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador color del equipo de reemplazo",
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

    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de rechazo",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    class Meta:
        verbose_name = "Reemplazo de equipo alquilado"
        verbose_name_plural = "Reemplazos de equipos alquilados"
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
                name="rent_repl_assign_status_idx",
            ),
            models.Index(
                fields=[
                    "outgoing_equipment",
                    "status",
                ],
                name="rent_repl_out_status_idx",
            ),
            models.Index(
                fields=[
                    "incoming_equipment",
                    "status",
                ],
                name="rent_repl_in_status_idx",
            ),
            models.Index(
                fields=[
                    "assigned_technician",
                    "status",
                ],
                name="rent_repl_tech_status_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "scheduled_at",
                ],
                name="rent_repl_status_date_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.code} - "
            f"{self.outgoing_equipment} por "
            f"{self.incoming_equipment}"
        )

    def clean(self):
        super().clean()

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.reason_detail = str(
            self.reason_detail or ""
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

        self.rejection_reason = str(
            self.rejection_reason or ""
        ).strip()

        self.cancellation_reason = str(
            self.cancellation_reason or ""
        ).strip()

        if not self.code:
            raise ValidationError(
                {
                    "code": (
                        "El código de reemplazo es obligatorio."
                    ),
                }
            )

        if not self.rental_assignment_id:
            raise ValidationError(
                {
                    "rental_assignment": (
                        "La asignación afectada es obligatoria."
                    ),
                }
            )

        if not self.outgoing_equipment_id:
            raise ValidationError(
                {
                    "outgoing_equipment": (
                        "El equipo retirado es obligatorio."
                    ),
                }
            )

        if not self.incoming_equipment_id:
            raise ValidationError(
                {
                    "incoming_equipment": (
                        "El equipo de reemplazo es obligatorio."
                    ),
                }
            )

        if (
            self.outgoing_equipment_id
            and self.incoming_equipment_id
            and self.outgoing_equipment_id
            == self.incoming_equipment_id
        ):
            raise ValidationError(
                {
                    "incoming_equipment": (
                        "El equipo de reemplazo debe ser diferente "
                        "al equipo retirado."
                    ),
                }
            )

        if (
            self.rental_assignment_id
            and self.outgoing_equipment_id
            and self.rental_assignment.rental_equipment_id
            != self.outgoing_equipment_id
        ):
            raise ValidationError(
                {
                    "outgoing_equipment": (
                        "El equipo retirado no corresponde "
                        "a la asignación seleccionada."
                    ),
                }
            )

        if (
            self.incoming_equipment_id
            and self.incoming_equipment.purpose
            != RentalEquipment.EquipmentPurpose.RENTAL
        ):
            raise ValidationError(
                {
                    "incoming_equipment": (
                        "El equipo de reemplazo debe estar destinado "
                        "al alquiler."
                    ),
                }
            )

        if (
            self.incoming_equipment_id
            and self.incoming_equipment.operational_status
            not in [
                RentalEquipment.OperationalStatus.READY_FOR_RENTAL,
                RentalEquipment.OperationalStatus.RESERVED,
            ]
        ):
            raise ValidationError(
                {
                    "incoming_equipment": (
                        "El equipo de reemplazo debe estar listo "
                        "para alquiler o reservado."
                    ),
                }
            )

        duplicate_code = RentalReplacement.objects.filter(
            code__iexact=self.code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe un reemplazo registrado "
                        "con este código."
                    ),
                }
            )

        active_statuses = [
            self.Status.REQUESTED,
            self.Status.APPROVED,
            self.Status.SCHEDULED,
            self.Status.ASSIGNED,
            self.Status.IN_TRANSIT,
            self.Status.IN_PROGRESS,
        ]

        if self.status in active_statuses:
            existing_replacement = RentalReplacement.objects.filter(
                rental_assignment_id=self.rental_assignment_id,
                status__in=active_statuses,
                archived_at__isnull=True,
            ).exclude(
                pk=self.pk,
            )

            if existing_replacement.exists():
                raise ValidationError(
                    {
                        "rental_assignment": (
                            "La asignación ya tiene un reemplazo "
                            "activo."
                        ),
                    }
                )

        if self.status == self.Status.APPROVED:
            if not self.approved_by_id:
                raise ValidationError(
                    {
                        "approved_by": (
                            "Debe indicar quién aprobó el reemplazo."
                        ),
                    }
                )

            if not self.approved_at:
                self.approved_at = timezone.now()

        technician_required_statuses = [
            self.Status.ASSIGNED,
            self.Status.IN_TRANSIT,
            self.Status.IN_PROGRESS,
            self.Status.COMPLETED,
            self.Status.OBSERVED,
        ]

        if (
            self.status in technician_required_statuses
            and not self.assigned_technician_id
        ):
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
                            "Debe indicar el resultado "
                            "del reemplazo."
                        ),
                    }
                )

            if not self.started_at:
                raise ValidationError(
                    {
                        "started_at": (
                            "Debe iniciar el reemplazo antes "
                            "de finalizarlo."
                        ),
                    }
                )

            if not self.completed_at:
                self.completed_at = timezone.now()

        if self.status == self.Status.REJECTED:
            if not self.rejection_reason:
                raise ValidationError(
                    {
                        "rejection_reason": (
                            "Debe indicar el motivo del rechazo."
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

        self.reason_detail = str(
            self.reason_detail or ""
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

        self.rejection_reason = str(
            self.rejection_reason or ""
        ).strip()

        self.cancellation_reason = str(
            self.cancellation_reason or ""
        ).strip()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )