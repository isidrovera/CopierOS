# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import (
    Repair,
    RepairTest,
)


def normalize_text(value):
    return str(
        value or ""
    ).strip()


def append_notes(
    current_value,
    new_value,
):
    current_text = normalize_text(
        current_value
    )

    new_text = normalize_text(
        new_value
    )

    if not new_text:
        return current_text

    if not current_text:
        return new_text

    timestamp = timezone.localtime().strftime(
        "%d/%m/%Y %H:%M"
    )

    return (
        f"{current_text}\n"
        f"[{timestamp}] {new_text}"
    )


def validate_test_available(
    repair_test,
):
    if repair_test.archived_at is not None:
        raise ValidationError(
            "La prueba se encuentra archivada."
        )

    if not repair_test.repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )


def update_repair_test_state(
    repair,
    actor=None,
):
    required_tests = RepairTest.objects.filter(
        repair=repair,
        is_required=True,
        archived_at__isnull=True,
    )

    if not required_tests.exists():
        completed = False
    else:
        incomplete_tests = required_tests.exclude(
            status=RepairTest.Status.COMPLETED,
        )

        failed_tests = required_tests.filter(
            result=RepairTest.Result.FAILED,
        )

        pending_results = required_tests.filter(
            result=RepairTest.Result.PENDING,
        )

        completed = not (
            incomplete_tests.exists()
            or failed_tests.exists()
            or pending_results.exists()
        )

    if repair.tests_completed != completed:
        repair.tests_completed = completed

        if actor:
            repair.updated_by = actor

        repair.save(
            update_fields=[
                "tests_completed",
                "updated_by",
                "updated_at",
            ]
        )

    return completed


@transaction.atomic
def create_repair_test(
    *,
    repair,
    test_type,
    name,
    actor=None,
    description="",
    instructions="",
    is_required=True,
    expected_value="",
    minimum_value=None,
    maximum_value=None,
    unit="",
    display_order=0,
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

    if not repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )

    test_name = normalize_text(
        name
    )

    if not test_name:
        raise ValidationError(
            {
                "name": (
                    "El nombre de la prueba es obligatorio."
                )
            }
        )

    if (
        minimum_value is not None
        and maximum_value is not None
        and minimum_value > maximum_value
    ):
        raise ValidationError(
            {
                "minimum_value": (
                    "El valor mínimo no puede ser mayor "
                    "que el valor máximo."
                )
            }
        )

    repair_test = RepairTest(
        repair=repair,
        test_type=test_type,
        name=test_name,
        description=normalize_text(
            description
        ),
        instructions=normalize_text(
            instructions
        ),
        status=RepairTest.Status.PENDING,
        result=RepairTest.Result.PENDING,
        is_required=is_required,
        expected_value=normalize_text(
            expected_value
        ),
        minimum_value=minimum_value,
        maximum_value=maximum_value,
        unit=normalize_text(
            unit
        ),
        display_order=display_order,
        created_by=actor,
        updated_by=actor,
    )

    repair_test.full_clean()
    repair_test.save()

    update_repair_test_state(
        repair,
        actor,
    )

    return repair_test


@transaction.atomic
def perform_repair_test(
    *,
    repair_test,
    result,
    actor=None,
    result_value="",
    observations="",
    failure_reason="",
):
    repair_test = (
        RepairTest.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=repair_test.pk)
    )

    validate_test_available(
        repair_test
    )

    if result == RepairTest.Result.PENDING:
        raise ValidationError(
            {
                "result": (
                    "Debes registrar un resultado definitivo."
                )
            }
        )

    result_value_text = normalize_text(
        result_value
    )

    observations_text = normalize_text(
        observations
    )

    failure_reason_text = normalize_text(
        failure_reason
    )

    if (
        result == RepairTest.Result.FAILED
        and not failure_reason_text
    ):
        raise ValidationError(
            {
                "failure_reason": (
                    "Debes indicar el motivo de la falla."
                )
            }
        )

    if (
        result != RepairTest.Result.FAILED
        and failure_reason_text
    ):
        raise ValidationError(
            {
                "failure_reason": (
                    "El motivo de falla solo corresponde "
                    "a una prueba fallida."
                )
            }
        )

    repair_test.status = (
        RepairTest.Status.COMPLETED
    )
    repair_test.result = result
    repair_test.result_value = (
        result_value_text
    )
    repair_test.observations = (
        observations_text
    )
    repair_test.failure_reason = (
        failure_reason_text
    )
    repair_test.performed_by = actor
    repair_test.performed_at = timezone.now()

    repair_test.is_verified = False
    repair_test.verified_by = None
    repair_test.verified_at = None
    repair_test.verification_notes = ""

    repair_test.updated_by = actor

    repair_test.full_clean()
    repair_test.save()

    update_repair_test_state(
        repair_test.repair,
        actor,
    )

    return repair_test


@transaction.atomic
def verify_repair_test(
    *,
    repair_test,
    actor=None,
    verification_notes="",
):
    repair_test = (
        RepairTest.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=repair_test.pk)
    )

    validate_test_available(
        repair_test
    )

    if (
        repair_test.status
        != RepairTest.Status.COMPLETED
    ):
        raise ValidationError(
            {
                "status": (
                    "La prueba debe estar completada "
                    "antes de verificarse."
                )
            }
        )

    if (
        repair_test.result
        == RepairTest.Result.PENDING
    ):
        raise ValidationError(
            {
                "result": (
                    "La prueba todavía no tiene "
                    "un resultado definitivo."
                )
            }
        )

    if repair_test.is_verified:
        raise ValidationError(
            "La prueba ya se encuentra verificada."
        )

    repair_test.is_verified = True
    repair_test.verified_by = actor
    repair_test.verified_at = timezone.now()
    repair_test.verification_notes = (
        normalize_text(
            verification_notes
        )
    )
    repair_test.updated_by = actor

    repair_test.full_clean()
    repair_test.save()

    update_repair_test_state(
        repair_test.repair,
        actor,
    )

    return repair_test


@transaction.atomic
def remove_repair_test_verification(
    *,
    repair_test,
    actor=None,
    reason="",
):
    verification_reason = normalize_text(
        reason
    )

    if not verification_reason:
        raise ValidationError(
            {
                "reason": (
                    "El motivo para retirar la verificación "
                    "es obligatorio."
                )
            }
        )

    repair_test = (
        RepairTest.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=repair_test.pk)
    )

    validate_test_available(
        repair_test
    )

    if not repair_test.is_verified:
        raise ValidationError(
            "La prueba no se encuentra verificada."
        )

    repair_test.is_verified = False
    repair_test.verified_by = None
    repair_test.verified_at = None
    repair_test.verification_notes = append_notes(
        repair_test.verification_notes,
        (
            "Verificación retirada: "
            f"{verification_reason}"
        ),
    )
    repair_test.updated_by = actor

    repair_test.full_clean()
    repair_test.save()

    update_repair_test_state(
        repair_test.repair,
        actor,
    )

    return repair_test


@transaction.atomic
def reset_repair_test(
    *,
    repair_test,
    actor=None,
    reason="",
):
    reset_reason = normalize_text(
        reason
    )

    if not reset_reason:
        raise ValidationError(
            {
                "reason": (
                    "El motivo para reiniciar la prueba "
                    "es obligatorio."
                )
            }
        )

    repair_test = (
        RepairTest.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=repair_test.pk)
    )

    validate_test_available(
        repair_test
    )

    if (
        repair_test.status
        == RepairTest.Status.PENDING
        and repair_test.result
        == RepairTest.Result.PENDING
    ):
        raise ValidationError(
            "La prueba ya se encuentra pendiente."
        )

    repair_test.observations = append_notes(
        repair_test.observations,
        (
            "Prueba reiniciada: "
            f"{reset_reason}"
        ),
    )

    repair_test.status = (
        RepairTest.Status.PENDING
    )
    repair_test.result = (
        RepairTest.Result.PENDING
    )
    repair_test.result_value = ""
    repair_test.failure_reason = ""

    repair_test.performed_by = None
    repair_test.performed_at = None

    repair_test.is_verified = False
    repair_test.verified_by = None
    repair_test.verified_at = None
    repair_test.verification_notes = ""

    repair_test.updated_by = actor

    repair_test.full_clean()
    repair_test.save()

    update_repair_test_state(
        repair_test.repair,
        actor,
    )

    return repair_test


@transaction.atomic
def archive_repair_test(
    *,
    repair_test,
    actor=None,
    reason="",
):
    repair_test = (
        RepairTest.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=repair_test.pk)
    )

    if repair_test.archived_at is not None:
        raise ValidationError(
            "La prueba ya se encuentra archivada."
        )

    repair = repair_test.repair

    repair_test.archive(
        user=actor,
        reason=normalize_text(
            reason
        ),
    )

    update_repair_test_state(
        repair,
        actor,
    )

    return repair_test


@transaction.atomic
def restore_repair_test(
    *,
    repair_test,
    actor=None,
):
    repair_test = (
        RepairTest.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=repair_test.pk)
    )

    if repair_test.archived_at is None:
        raise ValidationError(
            "La prueba no se encuentra archivada."
        )

    if not repair_test.repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )

    repair = repair_test.repair

    repair_test.restore(
        user=actor,
    )

    update_repair_test_state(
        repair,
        actor,
    )

    return repair_test