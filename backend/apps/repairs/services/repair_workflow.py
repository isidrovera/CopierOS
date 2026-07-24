# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import (
    Repair,
    RepairAssignment,
    RepairStatusHistory,
)
from .repair_code import generate_repair_code


STATUS_TIMESTAMP_FIELDS = {
    Repair.Status.ASSIGNED: "assigned_at",
    Repair.Status.UNDER_REVIEW: "review_started_at",
    Repair.Status.IN_REPAIR: "repair_started_at",
    Repair.Status.TESTING: "testing_started_at",
    Repair.Status.COMPLETED: "completed_at",
    Repair.Status.DELIVERED: "delivered_at",
    Repair.Status.CANCELLED: "cancelled_at",
}


ALLOWED_STATUS_TRANSITIONS = {
    Repair.Status.PENDING: {
        Repair.Status.ASSIGNED,
        Repair.Status.CANCELLED,
    },
    Repair.Status.ASSIGNED: {
        Repair.Status.UNDER_REVIEW,
        Repair.Status.CANCELLED,
    },
    Repair.Status.UNDER_REVIEW: {
        Repair.Status.WAITING_PARTS,
        Repair.Status.IN_REPAIR,
        Repair.Status.TESTING,
        Repair.Status.CANCELLED,
    },
    Repair.Status.WAITING_PARTS: {
        Repair.Status.UNDER_REVIEW,
        Repair.Status.IN_REPAIR,
        Repair.Status.CANCELLED,
    },
    Repair.Status.IN_REPAIR: {
        Repair.Status.WAITING_PARTS,
        Repair.Status.TESTING,
        Repair.Status.CANCELLED,
    },
    Repair.Status.TESTING: {
        Repair.Status.IN_REPAIR,
        Repair.Status.WAITING_PARTS,
        Repair.Status.COMPLETED,
        Repair.Status.CANCELLED,
    },
    Repair.Status.COMPLETED: {
        Repair.Status.DELIVERED,
        Repair.Status.IN_REPAIR,
    },
    Repair.Status.DELIVERED: set(),
    Repair.Status.CANCELLED: set(),
}


def normalize_text(value):
    return str(
        value or ""
    ).strip()


def get_status_timestamp(repair):
    field_name = STATUS_TIMESTAMP_FIELDS.get(
        repair.status
    )

    if not field_name:
        return (
            repair.requested_at
            or repair.created_at
        )

    return (
        getattr(
            repair,
            field_name,
            None,
        )
        or repair.updated_at
        or repair.created_at
    )


def calculate_duration_minutes(
    started_at,
    ended_at,
):
    if not started_at or not ended_at:
        return None

    duration = ended_at - started_at

    return max(
        int(
            duration.total_seconds()
            // 60
        ),
        0,
    )


def validate_status_transition(
    repair,
    new_status,
):
    valid_status_values = {
        choice[0]
        for choice in Repair.Status.choices
    }

    if new_status not in valid_status_values:
        raise ValidationError(
            {
                "status": (
                    "El estado seleccionado no es válido."
                )
            }
        )

    if repair.status == new_status:
        raise ValidationError(
            {
                "status": (
                    "La reparación ya se encuentra "
                    "en este estado."
                )
            }
        )

    allowed_statuses = (
        ALLOWED_STATUS_TRANSITIONS.get(
            repair.status,
            set(),
        )
    )

    if new_status not in allowed_statuses:
        status_labels = dict(
            Repair.Status.choices
        )

        raise ValidationError(
            {
                "status": (
                    "No se permite cambiar la reparación "
                    f"de {repair.get_status_display()} "
                    f"a {status_labels.get(new_status, new_status)}."
                )
            }
        )


def validate_repair_closure(repair):
    errors = {}

    if not repair.checklist_completed:
        errors["checklist_completed"] = (
            "La lista de revisión debe estar completa."
        )

    if not repair.tests_completed:
        errors["tests_completed"] = (
            "Las pruebas obligatorias deben estar completas."
        )

    if not repair.minimum_photos_completed:
        errors["minimum_photos_completed"] = (
            "Las fotografías mínimas deben estar completas."
        )

    if (
        repair.final_condition
        == Repair.FinalCondition.NOT_DEFINED
    ):
        errors["final_condition"] = (
            "Debes indicar la condición final del equipo."
        )

    if not normalize_text(
        repair.work_summary
    ):
        errors["work_summary"] = (
            "Debes registrar el resumen del trabajo realizado."
        )

    if errors:
        raise ValidationError(errors)


def create_status_history(
    *,
    repair,
    previous_status,
    new_status,
    actor=None,
    changed_at=None,
    previous_status_started_at=None,
    reason="",
    observations="",
    source="manual",
    changed_automatically=False,
):
    changed_at = (
        changed_at
        or timezone.now()
    )

    history = RepairStatusHistory(
        repair=repair,
        previous_status=previous_status,
        new_status=new_status,
        changed_by=actor,
        changed_at=changed_at,
        previous_status_started_at=(
            previous_status_started_at
        ),
        duration_minutes=(
            calculate_duration_minutes(
                previous_status_started_at,
                changed_at,
            )
        ),
        reason=normalize_text(
            reason
        ),
        observations=normalize_text(
            observations
        ),
        changed_automatically=(
            changed_automatically
        ),
        source=normalize_text(
            source
        ) or "manual",
        created_by=actor,
        updated_by=actor,
    )

    history.full_clean()
    history.save()

    return history


@transaction.atomic
def create_repair(
    *,
    equipment,
    actor=None,
    code="",
    repair_type=None,
    priority=None,
    reported_problem="",
    initial_observations="",
    minimum_photos_required=10,
):
    active_repair = (
        Repair.objects
        .select_for_update()
        .filter(
            equipment=equipment,
            is_active=True,
            archived_at__isnull=True,
        )
        .first()
    )

    if active_repair:
        raise ValidationError(
            {
                "equipment": (
                    "El equipo ya tiene una reparación activa."
                )
            }
        )

    repair_code = normalize_text(
        code
    ).upper()

    if not repair_code:
        repair_code = generate_repair_code()

    repair = Repair(
        code=repair_code,
        equipment=equipment,
        repair_type=(
            repair_type
            or Repair.RepairType.INITIAL_REVIEW
        ),
        priority=(
            priority
            or Repair.Priority.NORMAL
        ),
        status=Repair.Status.PENDING,
        is_active=True,
        requested_by=actor,
        requested_at=timezone.now(),
        reported_problem=normalize_text(
            reported_problem
        ),
        initial_observations=normalize_text(
            initial_observations
        ),
        minimum_photos_required=(
            minimum_photos_required
        ),
        created_by=actor,
        updated_by=actor,
    )

    repair.full_clean()
    repair.save()

    create_status_history(
        repair=repair,
        previous_status="",
        new_status=Repair.Status.PENDING,
        actor=actor,
        changed_at=repair.requested_at,
        previous_status_started_at=None,
        reason="Creación de la reparación.",
        observations="",
        source="system",
        changed_automatically=True,
    )

    return repair


@transaction.atomic
def assign_repair(
    *,
    repair,
    technician,
    actor=None,
    reason="",
):
    repair = (
        Repair.objects
        .select_for_update()
        .select_related(
            "assigned_technician",
        )
        .get(pk=repair.pk)
    )

    if repair.archived_at is not None:
        raise ValidationError(
            "La reparación está archivada."
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

    if repair.status in (
        Repair.Status.COMPLETED,
        Repair.Status.DELIVERED,
        Repair.Status.CANCELLED,
    ):
        raise ValidationError(
            {
                "status": (
                    "No se puede asignar un técnico "
                    "a una reparación cerrada."
                )
            }
        )

    current_assignment = (
        RepairAssignment.objects
        .select_for_update()
        .filter(
            repair=repair,
            is_active=True,
            archived_at__isnull=True,
        )
        .first()
    )

    now = timezone.now()
    reason_text = normalize_text(
        reason
    )

    if current_assignment:
        if (
            current_assignment.technician_id
            == technician.id
        ):
            raise ValidationError(
                {
                    "technician": (
                        "La reparación ya está asignada "
                        "a este técnico."
                    )
                }
            )

        current_assignment.status = (
            RepairAssignment.Status.REASSIGNED
        )
        current_assignment.is_active = False
        current_assignment.reassigned_at = now
        current_assignment.ended_at = now
        current_assignment.reassignment_reason = (
            reason_text
        )
        current_assignment.updated_by = actor

        current_assignment.full_clean()
        current_assignment.save()

    assignment = RepairAssignment(
        repair=repair,
        technician=technician,
        assigned_by=actor,
        status=RepairAssignment.Status.ASSIGNED,
        is_active=True,
        assigned_at=now,
        assignment_reason=reason_text,
        created_by=actor,
        updated_by=actor,
    )

    assignment.full_clean()
    assignment.save()

    repair.assigned_technician = technician
    repair.assigned_by = actor
    repair.assigned_at = now
    repair.updated_by = actor

    repair.full_clean()
    repair.save()

    if repair.status == Repair.Status.PENDING:
        repair = change_repair_status(
            repair=repair,
            new_status=Repair.Status.ASSIGNED,
            actor=actor,
            reason="Asignación de técnico.",
            observations=reason_text,
            source="assignment",
        )

    return assignment


@transaction.atomic
def change_repair_status(
    *,
    repair,
    new_status,
    actor=None,
    reason="",
    observations="",
    source="manual",
    changed_automatically=False,
):
    repair = (
        Repair.objects
        .select_for_update()
        .get(pk=repair.pk)
    )

    if repair.archived_at is not None:
        raise ValidationError(
            "La reparación está archivada."
        )

    if (
        not repair.is_active
        and repair.status
        not in (
            Repair.Status.COMPLETED,
        )
    ):
        raise ValidationError(
            "La reparación ya no está activa."
        )

    validate_status_transition(
        repair,
        new_status,
    )

    statuses_requiring_technician = (
        Repair.Status.ASSIGNED,
        Repair.Status.UNDER_REVIEW,
        Repair.Status.WAITING_PARTS,
        Repair.Status.IN_REPAIR,
        Repair.Status.TESTING,
    )

    if (
        new_status
        in statuses_requiring_technician
        and not repair.assigned_technician_id
    ):
        raise ValidationError(
            {
                "assigned_technician": (
                    "Debes asignar un técnico antes "
                    "de continuar."
                )
            }
        )

    if new_status in (
        Repair.Status.COMPLETED,
        Repair.Status.DELIVERED,
    ):
        validate_repair_closure(
            repair
        )

    now = timezone.now()
    previous_status = repair.status
    previous_started_at = (
        get_status_timestamp(
            repair
        )
    )

    repair.status = new_status
    repair.updated_by = actor

    timestamp_field = (
        STATUS_TIMESTAMP_FIELDS.get(
            new_status
        )
    )

    if timestamp_field:
        setattr(
            repair,
            timestamp_field,
            now,
        )

    if new_status in (
        Repair.Status.DELIVERED,
        Repair.Status.CANCELLED,
    ):
        repair.is_active = False
    else:
        repair.is_active = True

    repair.full_clean()
    repair.save()

    create_status_history(
        repair=repair,
        previous_status=previous_status,
        new_status=new_status,
        actor=actor,
        changed_at=now,
        previous_status_started_at=(
            previous_started_at
        ),
        reason=reason,
        observations=observations,
        source=source,
        changed_automatically=(
            changed_automatically
        ),
    )

    return repair


@transaction.atomic
def cancel_repair(
    *,
    repair,
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

    repair = (
        Repair.objects
        .select_for_update()
        .get(pk=repair.pk)
    )

    if repair.archived_at is not None:
        raise ValidationError(
            "La reparación está archivada."
        )

    if not repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )

    if repair.status in (
        Repair.Status.DELIVERED,
        Repair.Status.CANCELLED,
    ):
        raise ValidationError(
            {
                "status": (
                    "La reparación ya está cerrada."
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

    now = timezone.now()

    if active_assignment:
        active_assignment.status = (
            RepairAssignment.Status.CANCELLED
        )
        active_assignment.is_active = False
        active_assignment.cancelled_at = now
        active_assignment.ended_at = now
        active_assignment.cancellation_reason = (
            cancellation_reason
        )
        active_assignment.updated_by = actor

        active_assignment.full_clean()
        active_assignment.save()

    return change_repair_status(
        repair=repair,
        new_status=Repair.Status.CANCELLED,
        actor=actor,
        reason=cancellation_reason,
        observations="",
        source="cancellation",
    )


@transaction.atomic
def reopen_completed_repair(
    *,
    repair,
    actor=None,
    reason="",
):
    reopening_reason = normalize_text(
        reason
    )

    if not reopening_reason:
        raise ValidationError(
            {
                "reason": (
                    "El motivo de reapertura es obligatorio."
                )
            }
        )

    repair = (
        Repair.objects
        .select_for_update()
        .get(pk=repair.pk)
    )

    if repair.archived_at is not None:
        raise ValidationError(
            "La reparación está archivada."
        )

    if repair.status != Repair.Status.COMPLETED:
        raise ValidationError(
            {
                "status": (
                    "Solo puede reabrirse una reparación "
                    "finalizada y no entregada."
                )
            }
        )

    repair.is_active = True
    repair.updated_by = actor

    repair.full_clean()
    repair.save()

    return change_repair_status(
        repair=repair,
        new_status=Repair.Status.IN_REPAIR,
        actor=actor,
        reason=reopening_reason,
        observations="",
        source="reopening",
    )