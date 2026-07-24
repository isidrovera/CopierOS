# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import (
    Repair,
    RepairAssignment,
)
from .repair_workflow import change_repair_status


def normalize_text(value):
    return str(
        value or ""
    ).strip()


def validate_assignment_available(
    assignment,
):
    if assignment.archived_at is not None:
        raise ValidationError(
            "La asignación se encuentra archivada."
        )

    if not assignment.is_active:
        raise ValidationError(
            "La asignación ya no está activa."
        )

    if assignment.repair.archived_at is not None:
        raise ValidationError(
            "La reparación se encuentra archivada."
        )

    if not assignment.repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )


@transaction.atomic
def create_repair_assignment(
    *,
    repair,
    technician,
    actor=None,
    assignment_reason="",
):
    repair = (
        Repair.objects
        .select_for_update()
        .get(pk=repair.pk)
    )

    if repair.archived_at is not None:
        raise ValidationError(
            "La reparación se encuentra archivada."
        )

    if not repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )

    if not technician.is_active:
        raise ValidationError(
            {
                "technician": (
                    "El técnico seleccionado está inactivo."
                )
            }
        )

    active_assignment = (
        RepairAssignment.objects
        .select_for_update()
        .filter(
            repair=repair,
            is_active=True,
            archived_at__isnull=True,
        )
        .first()
    )

    if active_assignment:
        raise ValidationError(
            {
                "repair": (
                    "La reparación ya tiene una "
                    "asignación activa."
                )
            }
        )

    now = timezone.now()

    assignment = RepairAssignment(
        repair=repair,
        technician=technician,
        assigned_by=actor,
        status=RepairAssignment.Status.ASSIGNED,
        is_active=True,
        assigned_at=now,
        assignment_reason=normalize_text(
            assignment_reason
        ),
        created_by=actor,
        updated_by=actor,
    )

    assignment.full_clean()
    assignment.save()

    repair.assigned_technician = technician
    repair.assigned_by = actor
    repair.assigned_at = now
    repair.updated_by = actor

    if repair.status == Repair.Status.PENDING:
        repair.full_clean()
        repair.save()

        change_repair_status(
            repair=repair,
            new_status=Repair.Status.ASSIGNED,
            actor=actor,
            reason="Asignación de técnico.",
            observations=assignment.assignment_reason,
            source="assignment",
        )
    else:
        repair.full_clean()
        repair.save()

    return assignment


@transaction.atomic
def accept_repair_assignment(
    *,
    assignment,
    actor=None,
    observations="",
):
    assignment = (
        RepairAssignment.objects
        .select_for_update()
        .select_related(
            "repair",
            "technician",
        )
        .get(pk=assignment.pk)
    )

    validate_assignment_available(
        assignment
    )

    if (
        assignment.status
        != RepairAssignment.Status.ASSIGNED
    ):
        raise ValidationError(
            {
                "status": (
                    "Solo una asignación pendiente "
                    "puede aceptarse."
                )
            }
        )

    if (
        actor
        and actor.id != assignment.technician_id
        and not actor.is_staff
        and not actor.is_superuser
    ):
        raise ValidationError(
            "Solo el técnico asignado puede aceptar la tarea."
        )

    assignment.status = (
        RepairAssignment.Status.ACCEPTED
    )
    assignment.accepted_at = timezone.now()
    assignment.technician_observations = normalize_text(
        observations
    )
    assignment.updated_by = actor

    assignment.full_clean()
    assignment.save()

    return assignment


@transaction.atomic
def start_repair_assignment(
    *,
    assignment,
    actor=None,
    observations="",
):
    assignment = (
        RepairAssignment.objects
        .select_for_update()
        .select_related(
            "repair",
            "technician",
        )
        .get(pk=assignment.pk)
    )

    validate_assignment_available(
        assignment
    )

    if assignment.status not in (
        RepairAssignment.Status.ASSIGNED,
        RepairAssignment.Status.ACCEPTED,
    ):
        raise ValidationError(
            {
                "status": (
                    "La asignación no puede iniciarse "
                    "desde su estado actual."
                )
            }
        )

    if (
        actor
        and actor.id != assignment.technician_id
        and not actor.is_staff
        and not actor.is_superuser
    ):
        raise ValidationError(
            "Solo el técnico asignado puede iniciar la tarea."
        )

    now = timezone.now()

    assignment.status = (
        RepairAssignment.Status.IN_PROGRESS
    )
    assignment.started_at = now

    observation_text = normalize_text(
        observations
    )

    if observation_text:
        current_observations = normalize_text(
            assignment.technician_observations
        )

        assignment.technician_observations = (
            f"{current_observations}\n"
            f"{observation_text}"
        ).strip()

    assignment.updated_by = actor
    assignment.full_clean()
    assignment.save()

    repair = assignment.repair

    if repair.status == Repair.Status.ASSIGNED:
        change_repair_status(
            repair=repair,
            new_status=Repair.Status.IN_REVIEW,
            actor=actor,
            reason="Inicio de la revisión técnica.",
            observations=observation_text,
            source="assignment",
        )

    return assignment


@transaction.atomic
def complete_repair_assignment(
    *,
    assignment,
    actor=None,
    completion_notes="",
):
    assignment = (
        RepairAssignment.objects
        .select_for_update()
        .select_related(
            "repair",
            "technician",
        )
        .get(pk=assignment.pk)
    )

    validate_assignment_available(
        assignment
    )

    if assignment.status not in (
        RepairAssignment.Status.ACCEPTED,
        RepairAssignment.Status.IN_PROGRESS,
    ):
        raise ValidationError(
            {
                "status": (
                    "La asignación no puede completarse "
                    "desde su estado actual."
                )
            }
        )

    if (
        actor
        and actor.id != assignment.technician_id
        and not actor.is_staff
        and not actor.is_superuser
    ):
        raise ValidationError(
            "Solo el técnico asignado puede completar la tarea."
        )

    now = timezone.now()

    assignment.status = (
        RepairAssignment.Status.COMPLETED
    )
    assignment.is_active = False
    assignment.ended_at = now
    assignment.completion_notes = normalize_text(
        completion_notes
    )
    assignment.updated_by = actor

    assignment.full_clean()
    assignment.save()

    return assignment


@transaction.atomic
def reassign_repair_assignment(
    *,
    assignment,
    technician,
    actor=None,
    reason="",
    assignment_reason="",
):
    reassignment_reason = normalize_text(
        reason
    )

    if not reassignment_reason:
        raise ValidationError(
            {
                "reason": (
                    "El motivo de reasignación es obligatorio."
                )
            }
        )

    assignment = (
        RepairAssignment.objects
        .select_for_update()
        .select_related(
            "repair",
            "technician",
        )
        .get(pk=assignment.pk)
    )

    validate_assignment_available(
        assignment
    )

    if not technician.is_active:
        raise ValidationError(
            {
                "technician": (
                    "El técnico seleccionado está inactivo."
                )
            }
        )

    if technician.id == assignment.technician_id:
        raise ValidationError(
            {
                "technician": (
                    "Debes seleccionar un técnico diferente."
                )
            }
        )

    now = timezone.now()

    assignment.status = (
        RepairAssignment.Status.REASSIGNED
    )
    assignment.is_active = False
    assignment.reassigned_at = now
    assignment.ended_at = now
    assignment.reassignment_reason = (
        reassignment_reason
    )
    assignment.updated_by = actor

    assignment.full_clean()
    assignment.save()

    new_assignment = RepairAssignment(
        repair=assignment.repair,
        technician=technician,
        assigned_by=actor,
        status=RepairAssignment.Status.ASSIGNED,
        is_active=True,
        assigned_at=now,
        assignment_reason=(
            normalize_text(
                assignment_reason
            )
            or reassignment_reason
        ),
        created_by=actor,
        updated_by=actor,
    )

    new_assignment.full_clean()
    new_assignment.save()

    repair = assignment.repair
    repair.assigned_technician = technician
    repair.assigned_by = actor
    repair.assigned_at = now
    repair.updated_by = actor

    repair.full_clean()
    repair.save()

    return new_assignment


@transaction.atomic
def reject_repair_assignment(
    *,
    assignment,
    actor=None,
    reason="",
    observations="",
):
    rejection_reason = normalize_text(
        reason
    )

    if not rejection_reason:
        raise ValidationError(
            {
                "reason": (
                    "El motivo del rechazo es obligatorio."
                )
            }
        )

    assignment = (
        RepairAssignment.objects
        .select_for_update()
        .select_related(
            "repair",
            "technician",
        )
        .get(pk=assignment.pk)
    )

    validate_assignment_available(
        assignment
    )

    if assignment.status not in (
        RepairAssignment.Status.ASSIGNED,
        RepairAssignment.Status.ACCEPTED,
    ):
        raise ValidationError(
            {
                "status": (
                    "La asignación no puede rechazarse "
                    "desde su estado actual."
                )
            }
        )

    if (
        actor
        and actor.id != assignment.technician_id
        and not actor.is_staff
        and not actor.is_superuser
    ):
        raise ValidationError(
            "Solo el técnico asignado puede rechazar la tarea."
        )

    now = timezone.now()

    assignment.status = (
        RepairAssignment.Status.REJECTED
    )
    assignment.is_active = False
    assignment.rejected_at = now
    assignment.ended_at = now
    assignment.rejection_reason = (
        rejection_reason
    )

    observation_text = normalize_text(
        observations
    )

    if observation_text:
        assignment.technician_observations = (
            observation_text
        )

    assignment.updated_by = actor
    assignment.full_clean()
    assignment.save()

    repair = assignment.repair
    repair.assigned_technician = None
    repair.assigned_by = None
    repair.assigned_at = None
    repair.updated_by = actor

    repair.full_clean()
    repair.save()

    return assignment


@transaction.atomic
def cancel_repair_assignment(
    *,
    assignment,
    actor=None,
    reason="",
):
    cancellation_reason = normalize_text(
        reason
    )

    if not cancellation_reason:
        raise ValidationError(
            {
                "reason": (
                    "El motivo de cancelación es obligatorio."
                )
            }
        )

    assignment = (
        RepairAssignment.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=assignment.pk)
    )

    validate_assignment_available(
        assignment
    )

    now = timezone.now()

    assignment.status = (
        RepairAssignment.Status.CANCELLED
    )
    assignment.is_active = False
    assignment.cancelled_at = now
    assignment.ended_at = now
    assignment.cancellation_reason = (
        cancellation_reason
    )
    assignment.updated_by = actor

    assignment.full_clean()
    assignment.save()

    repair = assignment.repair

    if (
        repair.assigned_technician_id
        == assignment.technician_id
    ):
        repair.assigned_technician = None
        repair.assigned_by = None
        repair.assigned_at = None
        repair.updated_by = actor

        repair.full_clean()
        repair.save()

    return assignment


@transaction.atomic
def archive_repair_assignment(
    *,
    assignment,
    actor=None,
    reason="",
):
    assignment = (
        RepairAssignment.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=assignment.pk)
    )

    if assignment.archived_at is not None:
        raise ValidationError(
            "La asignación ya se encuentra archivada."
        )

    if assignment.is_active:
        raise ValidationError(
            "No puedes archivar una asignación activa."
        )

    assignment.archive(
        user=actor,
        reason=normalize_text(
            reason
        ),
    )

    return assignment


@transaction.atomic
def restore_repair_assignment(
    *,
    assignment,
    actor=None,
):
    assignment = (
        RepairAssignment.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=assignment.pk)
    )

    if assignment.archived_at is None:
        raise ValidationError(
            "La asignación no se encuentra archivada."
        )

    assignment.restore(
        user=actor,
    )

    return assignment