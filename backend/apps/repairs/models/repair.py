# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.equipment.models import Equipment

from .base import RepairBaseModel


class Repair(RepairBaseModel):
    """
    Reparación principal de una máquina.

    Una máquina puede tener varias reparaciones históricas,
    pero solo una reparación activa al mismo tiempo.

    La condición técnica de la reparación no impide que el
    equipo sea vendido o separado comercialmente.
    """

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        ASSIGNED = (
            "assigned",
            "Asignada",
        )
        UNDER_REVIEW = (
            "under_review",
            "En revisión",
        )
        WAITING_PARTS = (
            "waiting_parts",
            "Esperando repuestos",
        )
        IN_REPAIR = (
            "in_repair",
            "En reparación",
        )
        TESTING = (
            "testing",
            "En pruebas",
        )
        COMPLETED = (
            "completed",
            "Finalizada",
        )
        DELIVERED = (
            "delivered",
            "Entregada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )

    class Priority(models.TextChoices):
        LOW = (
            "low",
            "Baja",
        )
        NORMAL = (
            "normal",
            "Normal",
        )
        HIGH = (
            "high",
            "Alta",
        )
        URGENT = (
            "urgent",
            "Urgente",
        )

    class RepairType(models.TextChoices):
        INITIAL_REVIEW = (
            "initial_review",
            "Revisión inicial",
        )
        PREVENTIVE = (
            "preventive",
            "Mantenimiento preventivo",
        )
        CORRECTIVE = (
            "corrective",
            "Mantenimiento correctivo",
        )
        RECONDITIONING = (
            "reconditioning",
            "Reacondicionamiento",
        )
        WARRANTY = (
            "warranty",
            "Garantía",
        )
        RETURN_REVIEW = (
            "return_review",
            "Revisión por devolución",
        )
        OTHER = (
            "other",
            "Otro",
        )

    class FinalCondition(models.TextChoices):
        NOT_DEFINED = (
            "not_defined",
            "No definida",
        )
        OPERATIONAL = (
            "operational",
            "Operativa",
        )
        OPERATIONAL_WITH_OBSERVATIONS = (
            "operational_with_observations",
            "Operativa con observaciones",
        )
        REQUIRES_PARTS = (
            "requires_parts",
            "Requiere repuestos",
        )
        NOT_REPAIRABLE = (
            "not_repairable",
            "No reparable",
        )
        FOR_PARTS = (
            "for_parts",
            "Para repuestos",
        )

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="repairs",
        verbose_name="Equipo",
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código de reparación",
        help_text=(
            "Código interno único de la reparación. "
            "Se genera automáticamente si no se proporciona."
        ),
    )

    repair_type = models.CharField(
        max_length=40,
        choices=RepairType.choices,
        default=RepairType.INITIAL_REVIEW,
        db_index=True,
        verbose_name="Tipo de reparación",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
        db_index=True,
        verbose_name="Prioridad",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Reparación activa",
        help_text=(
            "Indica que la reparación continúa abierta. "
            "Solo puede existir una reparación activa por equipo."
        ),
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="requested_repairs",
        verbose_name="Solicitada por",
    )

    assigned_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_repairs",
        verbose_name="Técnico asignado",
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repairs_assigned_by",
        verbose_name="Asignada por",
    )

    requested_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de solicitud",
    )

    assigned_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de asignación",
    )

    review_started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Inicio de revisión",
    )

    repair_started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Inicio de reparación",
    )

    testing_started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Inicio de pruebas",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de finalización",
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de entrega",
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de cancelación",
    )

    reported_problem = models.TextField(
        blank=True,
        verbose_name="Problema reportado",
        help_text=(
            "Descripción inicial del problema o motivo "
            "por el cual la máquina ingresa a revisión."
        ),
    )

    initial_observations = models.TextField(
        blank=True,
        verbose_name="Observaciones iniciales",
    )

    work_summary = models.TextField(
        blank=True,
        verbose_name="Resumen del trabajo realizado",
    )

    pending_work = models.TextField(
        blank=True,
        verbose_name="Trabajo pendiente",
    )

    final_condition = models.CharField(
        max_length=40,
        choices=FinalCondition.choices,
        default=FinalCondition.NOT_DEFINED,
        db_index=True,
        verbose_name="Condición final",
    )

    final_observations = models.TextField(
        blank=True,
        verbose_name="Observaciones finales",
    )

    requires_parts = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere repuestos",
    )

    requires_external_service = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere servicio externo",
    )

    requires_follow_up = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere seguimiento",
    )

    follow_up_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de seguimiento",
    )

    minimum_photos_required = models.PositiveSmallIntegerField(
        default=10,
        verbose_name="Cantidad mínima de fotografías",
    )

    minimum_photos_completed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Fotografías mínimas completadas",
    )

    checklist_completed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Lista de revisión completada",
    )

    tests_completed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Pruebas completadas",
    )

    snmp_validation_completed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Validación SNMP completada",
    )

    closure_notes = models.TextField(
        blank=True,
        verbose_name="Notas de cierre",
    )

    class Meta:
        verbose_name = "Reparación"
        verbose_name_plural = "Reparaciones"
        ordering = (
            "-requested_at",
            "-created_at",
        )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "equipment",
                ],
                condition=Q(
                    is_active=True,
                    archived_at__isnull=True,
                ),
                name="unique_active_repair_equipment",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "equipment",
                    "status",
                ],
                name="repair_equipment_status_idx",
            ),
            models.Index(
                fields=[
                    "assigned_technician",
                    "status",
                ],
                name="repair_technician_status_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "priority",
                ],
                name="repair_status_priority_idx",
            ),
            models.Index(
                fields=[
                    "is_active",
                    "status",
                ],
                name="repair_active_status_idx",
            ),
            models.Index(
                fields=[
                    "requested_at",
                    "status",
                ],
                name="repair_requested_status_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.code} - "
            f"{self.equipment}"
        )

    def clean(self):
        """
        Normaliza y valida la reparación.
        """

        super().clean()

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.reported_problem = str(
            self.reported_problem or ""
        ).strip()

        self.initial_observations = str(
            self.initial_observations or ""
        ).strip()

        self.work_summary = str(
            self.work_summary or ""
        ).strip()

        self.pending_work = str(
            self.pending_work or ""
        ).strip()

        self.final_observations = str(
            self.final_observations or ""
        ).strip()

        self.closure_notes = str(
            self.closure_notes or ""
        ).strip()

        if not self.equipment_id:
            raise ValidationError(
                {
                    "equipment": (
                        "El equipo es obligatorio."
                    ),
                }
            )

        if not self.code:
            raise ValidationError(
                {
                    "code": (
                        "El código de reparación es obligatorio."
                    ),
                }
            )

        duplicate_code = Repair.objects.filter(
            code__iexact=self.code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe una reparación registrada "
                        "con este código."
                    ),
                }
            )

        if self.is_active and self.equipment_id:
            active_repair = Repair.objects.filter(
                equipment_id=self.equipment_id,
                is_active=True,
                archived_at__isnull=True,
            ).exclude(
                pk=self.pk,
            )

            if active_repair.exists():
                raise ValidationError(
                    {
                        "equipment": (
                            "Este equipo ya tiene una reparación "
                            "activa."
                        ),
                    }
                )

        if (
            self.assigned_technician_id
            and not self.assigned_at
        ):
            raise ValidationError(
                {
                    "assigned_at": (
                        "Debe indicar la fecha de asignación "
                        "del técnico."
                    ),
                }
            )

        if (
            self.status == self.Status.ASSIGNED
            and not self.assigned_technician_id
        ):
            raise ValidationError(
                {
                    "assigned_technician": (
                        "Debe asignar un técnico para colocar "
                        "la reparación en estado asignada."
                    ),
                }
            )

        if (
            self.status == self.Status.UNDER_REVIEW
            and not self.review_started_at
        ):
            raise ValidationError(
                {
                    "review_started_at": (
                        "Debe registrar el inicio de la revisión."
                    ),
                }
            )

        if (
            self.status == self.Status.IN_REPAIR
            and not self.repair_started_at
        ):
            raise ValidationError(
                {
                    "repair_started_at": (
                        "Debe registrar el inicio de la reparación."
                    ),
                }
            )

        if (
            self.status == self.Status.TESTING
            and not self.testing_started_at
        ):
            raise ValidationError(
                {
                    "testing_started_at": (
                        "Debe registrar el inicio de las pruebas."
                    ),
                }
            )

        if self.status == self.Status.COMPLETED:
            if not self.completed_at:
                raise ValidationError(
                    {
                        "completed_at": (
                            "Debe registrar la fecha de finalización."
                        ),
                    }
                )

            if (
                self.final_condition
                == self.FinalCondition.NOT_DEFINED
            ):
                raise ValidationError(
                    {
                        "final_condition": (
                            "Debe indicar la condición final "
                            "del equipo."
                        ),
                    }
                )

        if (
            self.status == self.Status.DELIVERED
            and not self.delivered_at
        ):
            raise ValidationError(
                {
                    "delivered_at": (
                        "Debe registrar la fecha de entrega."
                    ),
                }
            )

        if (
            self.status == self.Status.CANCELLED
            and not self.cancelled_at
        ):
            raise ValidationError(
                {
                    "cancelled_at": (
                        "Debe registrar la fecha de cancelación."
                    ),
                }
            )

        if (
            self.requires_follow_up
            and not self.follow_up_date
        ):
            raise ValidationError(
                {
                    "follow_up_date": (
                        "Debe indicar la fecha de seguimiento."
                    ),
                }
            )

        if (
            not self.requires_follow_up
            and self.follow_up_date
        ):
            raise ValidationError(
                {
                    "follow_up_date": (
                        "No debe indicar una fecha de seguimiento "
                        "si el seguimiento no está habilitado."
                    ),
                }
            )

        if self.minimum_photos_required < 1:
            raise ValidationError(
                {
                    "minimum_photos_required": (
                        "Debe requerirse al menos una fotografía."
                    ),
                }
            )

        if self.status in [
            self.Status.COMPLETED,
            self.Status.DELIVERED,
        ]:
            if not self.checklist_completed:
                raise ValidationError(
                    {
                        "checklist_completed": (
                            "No puede finalizar la reparación "
                            "sin completar la lista de revisión."
                        ),
                    }
                )

            if not self.tests_completed:
                raise ValidationError(
                    {
                        "tests_completed": (
                            "No puede finalizar la reparación "
                            "sin completar las pruebas."
                        ),
                    }
                )

            if not self.minimum_photos_completed:
                raise ValidationError(
                    {
                        "minimum_photos_completed": (
                            "No puede finalizar la reparación "
                            "sin completar las fotografías mínimas."
                        ),
                    }
                )

    def save(self, *args, **kwargs):
        """
        Normaliza y valida antes de guardar.
        """

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.reported_problem = str(
            self.reported_problem or ""
        ).strip()

        self.initial_observations = str(
            self.initial_observations or ""
        ).strip()

        self.work_summary = str(
            self.work_summary or ""
        ).strip()

        self.pending_work = str(
            self.pending_work or ""
        ).strip()

        self.final_observations = str(
            self.final_observations or ""
        ).strip()

        self.closure_notes = str(
            self.closure_notes or ""
        ).strip()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )

    def archive(
        self,
        user=None,
        reason="",
        save=True,
    ):
        """
        Archiva la reparación y la marca como inactiva.
        """

        self.is_active = False

        if save:
            self.save(
                update_fields=[
                    "is_active",
                    "updated_at",
                ]
            )

        return super().archive(
            user=user,
            reason=reason,
            save=save,
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        """
        Restaura la reparación.

        Si el equipo ya tiene otra reparación activa,
        la reparación se restaura como inactiva.
        """

        another_active_repair = Repair.objects.filter(
            equipment_id=self.equipment_id,
            is_active=True,
            archived_at__isnull=True,
        ).exclude(
            pk=self.pk,
        ).exists()

        self.is_active = not another_active_repair

        if save:
            self.save(
                update_fields=[
                    "is_active",
                    "updated_at",
                ]
            )

        return super().restore(
            user=user,
            save=save,
        )