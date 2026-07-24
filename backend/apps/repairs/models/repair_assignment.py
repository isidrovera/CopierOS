# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .base import RepairBaseModel
from .repair import Repair


class RepairAssignment(RepairBaseModel):
    """
    Historial de asignaciones de técnicos a una reparación.

    Permite conservar todas las reasignaciones realizadas durante
    una reparación, manteniendo únicamente una asignación activa.

    La asignación principal también puede reflejarse en el campo
    assigned_technician del modelo Repair.
    """

    class Status(models.TextChoices):
        ASSIGNED = (
            "assigned",
            "Asignada",
        )
        ACCEPTED = (
            "accepted",
            "Aceptada",
        )
        IN_PROGRESS = (
            "in_progress",
            "En progreso",
        )
        COMPLETED = (
            "completed",
            "Completada",
        )
        REASSIGNED = (
            "reassigned",
            "Reasignada",
        )
        REJECTED = (
            "rejected",
            "Rechazada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )

    repair = models.ForeignKey(
        Repair,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="Reparación",
    )

    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="repair_assignment_history",
        verbose_name="Técnico",
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_assignments_created",
        verbose_name="Asignado por",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.ASSIGNED,
        db_index=True,
        verbose_name="Estado",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Asignación activa",
        help_text=(
            "Solo puede existir una asignación activa por reparación."
        ),
    )

    assigned_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de asignación",
    )

    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de aceptación",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de inicio",
    )

    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de finalización",
    )

    reassigned_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de reasignación",
    )

    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de rechazo",
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de cancelación",
    )

    assignment_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de asignación",
    )

    technician_observations = models.TextField(
        blank=True,
        verbose_name="Observaciones del técnico",
    )

    completion_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones de finalización",
    )

    reassignment_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de reasignación",
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
        verbose_name = "Asignación de reparación"
        verbose_name_plural = "Asignaciones de reparaciones"
        ordering = (
            "-is_active",
            "-assigned_at",
            "-created_at",
        )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "repair",
                ],
                condition=Q(
                    is_active=True,
                    archived_at__isnull=True,
                ),
                name="unique_active_repair_assign",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "repair",
                    "is_active",
                ],
                name="repair_assign_active_idx",
            ),
            models.Index(
                fields=[
                    "technician",
                    "status",
                ],
                name="repair_assign_tech_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "assigned_at",
                ],
                name="repair_assign_status_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.repair.code} - "
            f"{self.technician}"
        )

    def clean(self):
        """
        Normaliza y valida la asignación.
        """

        super().clean()

        self.assignment_reason = str(
            self.assignment_reason or ""
        ).strip()

        self.technician_observations = str(
            self.technician_observations or ""
        ).strip()

        self.completion_notes = str(
            self.completion_notes or ""
        ).strip()

        self.reassignment_reason = str(
            self.reassignment_reason or ""
        ).strip()

        self.rejection_reason = str(
            self.rejection_reason or ""
        ).strip()

        self.cancellation_reason = str(
            self.cancellation_reason or ""
        ).strip()

        if not self.repair_id:
            raise ValidationError(
                {
                    "repair": (
                        "La reparación es obligatoria."
                    ),
                }
            )

        if not self.technician_id:
            raise ValidationError(
                {
                    "technician": (
                        "El técnico es obligatorio."
                    ),
                }
            )

        if (
            self.repair_id
            and not self.repair.is_active
            and self.is_active
        ):
            raise ValidationError(
                {
                    "is_active": (
                        "No puede existir una asignación activa "
                        "para una reparación cerrada o inactiva."
                    ),
                }
            )

        if self.is_active and self.repair_id:
            active_assignment = (
                RepairAssignment.objects.filter(
                    repair_id=self.repair_id,
                    is_active=True,
                    archived_at__isnull=True,
                )
                .exclude(
                    pk=self.pk,
                )
            )

            if active_assignment.exists():
                raise ValidationError(
                    {
                        "repair": (
                            "La reparación ya tiene una asignación "
                            "activa."
                        ),
                    }
                )

        if (
            self.status == self.Status.ACCEPTED
            and not self.accepted_at
        ):
            raise ValidationError(
                {
                    "accepted_at": (
                        "Debe registrar la fecha de aceptación."
                    ),
                }
            )

        if (
            self.status == self.Status.IN_PROGRESS
            and not self.started_at
        ):
            raise ValidationError(
                {
                    "started_at": (
                        "Debe registrar la fecha de inicio."
                    ),
                }
            )

        if self.status == self.Status.COMPLETED:
            if not self.ended_at:
                raise ValidationError(
                    {
                        "ended_at": (
                            "Debe registrar la fecha de finalización."
                        ),
                    }
                )

            if self.is_active:
                raise ValidationError(
                    {
                        "is_active": (
                            "Una asignación completada no puede "
                            "permanecer activa."
                        ),
                    }
                )

        if self.status == self.Status.REASSIGNED:
            if not self.reassigned_at:
                raise ValidationError(
                    {
                        "reassigned_at": (
                            "Debe registrar la fecha de reasignación."
                        ),
                    }
                )

            if not self.reassignment_reason:
                raise ValidationError(
                    {
                        "reassignment_reason": (
                            "Debe indicar el motivo de reasignación."
                        ),
                    }
                )

            if self.is_active:
                raise ValidationError(
                    {
                        "is_active": (
                            "Una asignación reasignada no puede "
                            "permanecer activa."
                        ),
                    }
                )

        if self.status == self.Status.REJECTED:
            if not self.rejected_at:
                raise ValidationError(
                    {
                        "rejected_at": (
                            "Debe registrar la fecha de rechazo."
                        ),
                    }
                )

            if not self.rejection_reason:
                raise ValidationError(
                    {
                        "rejection_reason": (
                            "Debe indicar el motivo del rechazo."
                        ),
                    }
                )

            if self.is_active:
                raise ValidationError(
                    {
                        "is_active": (
                            "Una asignación rechazada no puede "
                            "permanecer activa."
                        ),
                    }
                )

        if self.status == self.Status.CANCELLED:
            if not self.cancelled_at:
                raise ValidationError(
                    {
                        "cancelled_at": (
                            "Debe registrar la fecha de cancelación."
                        ),
                    }
                )

            if not self.cancellation_reason:
                raise ValidationError(
                    {
                        "cancellation_reason": (
                            "Debe indicar el motivo de cancelación."
                        ),
                    }
                )

            if self.is_active:
                raise ValidationError(
                    {
                        "is_active": (
                            "Una asignación cancelada no puede "
                            "permanecer activa."
                        ),
                    }
                )

        if (
            self.accepted_at
            and self.accepted_at < self.assigned_at
        ):
            raise ValidationError(
                {
                    "accepted_at": (
                        "La fecha de aceptación no puede ser anterior "
                        "a la fecha de asignación."
                    ),
                }
            )

        if (
            self.started_at
            and self.started_at < self.assigned_at
        ):
            raise ValidationError(
                {
                    "started_at": (
                        "La fecha de inicio no puede ser anterior "
                        "a la fecha de asignación."
                    ),
                }
            )

        if (
            self.ended_at
            and self.started_at
            and self.ended_at < self.started_at
        ):
            raise ValidationError(
                {
                    "ended_at": (
                        "La fecha de finalización no puede ser "
                        "anterior a la fecha de inicio."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        """
        Normaliza, valida y sincroniza la asignación principal.
        """

        self.assignment_reason = str(
            self.assignment_reason or ""
        ).strip()

        self.technician_observations = str(
            self.technician_observations or ""
        ).strip()

        self.completion_notes = str(
            self.completion_notes or ""
        ).strip()

        self.reassignment_reason = str(
            self.reassignment_reason or ""
        ).strip()

        self.rejection_reason = str(
            self.rejection_reason or ""
        ).strip()

        self.cancellation_reason = str(
            self.cancellation_reason or ""
        ).strip()

        self.full_clean()

        result = super().save(
            *args,
            **kwargs,
        )

        if self.is_active and self.repair_id:
            repair = self.repair

            fields_to_update = []

            if (
                repair.assigned_technician_id
                != self.technician_id
            ):
                repair.assigned_technician = self.technician
                fields_to_update.append(
                    "assigned_technician"
                )

            if repair.assigned_by_id != self.assigned_by_id:
                repair.assigned_by = self.assigned_by
                fields_to_update.append(
                    "assigned_by"
                )

            if repair.assigned_at != self.assigned_at:
                repair.assigned_at = self.assigned_at
                fields_to_update.append(
                    "assigned_at"
                )

            if repair.status == Repair.Status.PENDING:
                repair.status = Repair.Status.ASSIGNED
                fields_to_update.append(
                    "status"
                )

            if fields_to_update:
                fields_to_update.append(
                    "updated_at"
                )

                repair.save(
                    update_fields=fields_to_update,
                )

        return result

    def archive(
        self,
        user=None,
        reason="",
        save=True,
    ):
        """
        Archiva la asignación y la marca como inactiva.
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
        Restaura la asignación.

        Si ya existe otra asignación activa para la reparación,
        esta asignación se restaura como inactiva.
        """

        another_active_assignment = (
            RepairAssignment.objects.filter(
                repair_id=self.repair_id,
                is_active=True,
                archived_at__isnull=True,
            )
            .exclude(
                pk=self.pk,
            )
            .exists()
        )

        self.is_active = not another_active_assignment

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