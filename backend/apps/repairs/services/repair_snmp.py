# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import (
    Repair,
    RepairSNMPValidation,
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


def model_has_field(
    model,
    field_name,
):
    return any(
        field.name == field_name
        for field in model._meta.fields
    )


def set_if_field_exists(
    instance,
    field_name,
    value,
):
    if model_has_field(
        instance.__class__,
        field_name,
    ):
        setattr(
            instance,
            field_name,
            value,
        )


def get_status_value(
    possible_values,
):
    if not model_has_field(
        RepairSNMPValidation,
        "status",
    ):
        return None

    status_field = (
        RepairSNMPValidation._meta.get_field(
            "status"
        )
    )

    available_values = {
        str(choice[0]).lower(): choice[0]
        for choice in status_field.choices
    }

    for value in possible_values:
        normalized_value = str(
            value
        ).lower()

        if normalized_value in available_values:
            return available_values[
                normalized_value
            ]

    return None


def validate_snmp_available(
    validation,
):
    if validation.archived_at is not None:
        raise ValidationError(
            "La validación SNMP está archivada."
        )

    if not validation.repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )


def update_repair_snmp_state(
    repair,
    actor=None,
):
    validations = (
        RepairSNMPValidation.objects.filter(
            repair=repair,
            archived_at__isnull=True,
        )
    )

    completed = False

    if model_has_field(
        RepairSNMPValidation,
        "is_successful",
    ):
        completed = validations.filter(
            is_successful=True,
        ).exists()

    elif model_has_field(
        RepairSNMPValidation,
        "success",
    ):
        completed = validations.filter(
            success=True,
        ).exists()

    elif model_has_field(
        RepairSNMPValidation,
        "completed_at",
    ):
        completed = validations.filter(
            completed_at__isnull=False,
        ).exists()

    elif model_has_field(
        RepairSNMPValidation,
        "status",
    ):
        completed_status = get_status_value(
            (
                "completed",
                "success",
                "successful",
                "passed",
                "finished",
            )
        )

        if completed_status is not None:
            completed = validations.filter(
                status=completed_status,
            ).exists()

    if (
        repair.snmp_validation_completed
        != completed
    ):
        repair.snmp_validation_completed = (
            completed
        )

        if actor:
            repair.updated_by = actor

        repair.save(
            update_fields=[
                "snmp_validation_completed",
                "updated_by",
                "updated_at",
            ]
        )

    return completed


@transaction.atomic
def create_snmp_validation(
    *,
    repair,
    actor=None,
    host="",
    port=161,
    community="public",
    version=None,
    timeout=None,
    retries=None,
    observations="",
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

    host_value = normalize_text(
        host
    )

    if not host_value:
        raise ValidationError(
            {
                "host": (
                    "La dirección IP o nombre "
                    "del equipo es obligatorio."
                )
            }
        )

    if port < 1 or port > 65535:
        raise ValidationError(
            {
                "port": (
                    "El puerto debe estar entre "
                    "1 y 65535."
                )
            }
        )

    validation_data = {
        "repair": repair,
        "host": host_value,
        "port": port,
        "community": normalize_text(
            community
        ),
        "created_by": actor,
        "updated_by": actor,
    }

    if version is not None:
        validation_data["version"] = version

    if timeout is not None:
        validation_data["timeout"] = timeout

    if retries is not None:
        validation_data["retries"] = retries

    validation = RepairSNMPValidation(
        **validation_data
    )

    set_if_field_exists(
        validation,
        "observations",
        normalize_text(
            observations
        ),
    )

    pending_status = get_status_value(
        (
            "pending",
            "created",
            "queued",
        )
    )

    if pending_status is not None:
        validation.status = pending_status

    set_if_field_exists(
        validation,
        "is_successful",
        False,
    )

    set_if_field_exists(
        validation,
        "success",
        False,
    )

    validation.full_clean()
    validation.save()

    update_repair_snmp_state(
        repair,
        actor,
    )

    return validation


@transaction.atomic
def start_snmp_validation(
    *,
    validation,
    actor=None,
    host=None,
    port=None,
    community=None,
):
    validation = (
        RepairSNMPValidation.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=validation.pk)
    )

    validate_snmp_available(
        validation
    )

    if (
        model_has_field(
            RepairSNMPValidation,
            "completed_at",
        )
        and validation.completed_at
    ):
        raise ValidationError(
            "La validación SNMP ya fue completada."
        )

    if host is not None:
        host_value = normalize_text(
            host
        )

        if not host_value:
            raise ValidationError(
                {
                    "host": (
                        "La dirección IP o nombre "
                        "del equipo es obligatorio."
                    )
                }
            )

        validation.host = host_value

    if port is not None:
        if port < 1 or port > 65535:
            raise ValidationError(
                {
                    "port": (
                        "El puerto debe estar entre "
                        "1 y 65535."
                    )
                }
            )

        validation.port = port

    if community is not None:
        validation.community = normalize_text(
            community
        )

    if not normalize_text(
        getattr(
            validation,
            "host",
            "",
        )
    ):
        raise ValidationError(
            {
                "host": (
                    "Debes indicar la dirección IP "
                    "o nombre del equipo."
                )
            }
        )

    running_status = get_status_value(
        (
            "in_progress",
            "processing",
            "running",
            "started",
        )
    )

    if running_status is not None:
        validation.status = running_status

    now = timezone.now()

    set_if_field_exists(
        validation,
        "started_at",
        now,
    )

    set_if_field_exists(
        validation,
        "last_attempt_at",
        now,
    )

    set_if_field_exists(
        validation,
        "error_message",
        "",
    )

    set_if_field_exists(
        validation,
        "completed_at",
        None,
    )

    set_if_field_exists(
        validation,
        "is_successful",
        False,
    )

    set_if_field_exists(
        validation,
        "success",
        False,
    )

    validation.updated_by = actor

    validation.full_clean()
    validation.save()

    update_repair_snmp_state(
        validation.repair,
        actor,
    )

    return validation


@transaction.atomic
def complete_snmp_validation(
    *,
    validation,
    actor=None,
    raw_data=None,
    observations="",
):
    validation = (
        RepairSNMPValidation.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=validation.pk)
    )

    validate_snmp_available(
        validation
    )

    if (
        model_has_field(
            RepairSNMPValidation,
            "completed_at",
        )
        and validation.completed_at
    ):
        raise ValidationError(
            "La validación SNMP ya fue completada."
        )

    now = timezone.now()

    completed_status = get_status_value(
        (
            "completed",
            "success",
            "successful",
            "passed",
            "finished",
        )
    )

    if completed_status is not None:
        validation.status = completed_status

    set_if_field_exists(
        validation,
        "completed_at",
        now,
    )

    set_if_field_exists(
        validation,
        "validated_at",
        now,
    )

    set_if_field_exists(
        validation,
        "is_successful",
        True,
    )

    set_if_field_exists(
        validation,
        "success",
        True,
    )

    set_if_field_exists(
        validation,
        "error_message",
        "",
    )

    if raw_data is not None:
        set_if_field_exists(
            validation,
            "raw_data",
            raw_data,
        )

        set_if_field_exists(
            validation,
            "response_data",
            raw_data,
        )

        set_if_field_exists(
            validation,
            "snmp_data",
            raw_data,
        )

    observations_text = normalize_text(
        observations
    )

    if observations_text:
        current_observations = getattr(
            validation,
            "observations",
            "",
        )

        set_if_field_exists(
            validation,
            "observations",
            append_notes(
                current_observations,
                observations_text,
            ),
        )

    if hasattr(
        validation,
        "calculate_matches",
    ):
        validation.calculate_matches()

    validation.updated_by = actor

    validation.full_clean()
    validation.save()

    update_repair_snmp_state(
        validation.repair,
        actor,
    )

    return validation


@transaction.atomic
def fail_snmp_validation(
    *,
    validation,
    error_message,
    actor=None,
    observations="",
):
    validation = (
        RepairSNMPValidation.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=validation.pk)
    )

    validate_snmp_available(
        validation
    )

    error_text = normalize_text(
        error_message
    )

    if not error_text:
        raise ValidationError(
            {
                "error_message": (
                    "Debes indicar el error "
                    "de la validación."
                )
            }
        )

    failed_status = get_status_value(
        (
            "failed",
            "error",
            "unsuccessful",
        )
    )

    if failed_status is not None:
        validation.status = failed_status

    now = timezone.now()

    set_if_field_exists(
        validation,
        "completed_at",
        now,
    )

    set_if_field_exists(
        validation,
        "last_attempt_at",
        now,
    )

    set_if_field_exists(
        validation,
        "is_successful",
        False,
    )

    set_if_field_exists(
        validation,
        "success",
        False,
    )

    set_if_field_exists(
        validation,
        "error_message",
        error_text,
    )

    observations_text = normalize_text(
        observations
    )

    if observations_text:
        current_observations = getattr(
            validation,
            "observations",
            "",
        )

        set_if_field_exists(
            validation,
            "observations",
            append_notes(
                current_observations,
                observations_text,
            ),
        )

    validation.updated_by = actor

    validation.full_clean()
    validation.save()

    update_repair_snmp_state(
        validation.repair,
        actor,
    )

    return validation


@transaction.atomic
def recalculate_snmp_matches(
    *,
    validation,
    actor=None,
):
    validation = (
        RepairSNMPValidation.objects
        .select_for_update()
        .select_related(
            "repair",
            "repair__equipment",
        )
        .get(pk=validation.pk)
    )

    if validation.archived_at is not None:
        raise ValidationError(
            "La validación SNMP está archivada."
        )

    if not hasattr(
        validation,
        "calculate_matches",
    ):
        raise ValidationError(
            "El modelo no permite recalcular coincidencias."
        )

    validation.calculate_matches()
    validation.updated_by = actor

    validation.full_clean()
    validation.save()

    update_repair_snmp_state(
        validation.repair,
        actor,
    )

    return validation


@transaction.atomic
def reset_snmp_validation(
    *,
    validation,
    actor=None,
    reason="",
):
    validation = (
        RepairSNMPValidation.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=validation.pk)
    )

    validate_snmp_available(
        validation
    )

    reason_text = normalize_text(
        reason
    )

    if not reason_text:
        raise ValidationError(
            {
                "reason": (
                    "El motivo para reiniciar "
                    "la validación es obligatorio."
                )
            }
        )

    pending_status = get_status_value(
        (
            "pending",
            "created",
            "queued",
        )
    )

    if pending_status is not None:
        validation.status = pending_status

    set_if_field_exists(
        validation,
        "started_at",
        None,
    )

    set_if_field_exists(
        validation,
        "completed_at",
        None,
    )

    set_if_field_exists(
        validation,
        "validated_at",
        None,
    )

    set_if_field_exists(
        validation,
        "is_successful",
        False,
    )

    set_if_field_exists(
        validation,
        "success",
        False,
    )

    set_if_field_exists(
        validation,
        "error_message",
        "",
    )

    current_observations = getattr(
        validation,
        "observations",
        "",
    )

    set_if_field_exists(
        validation,
        "observations",
        append_notes(
            current_observations,
            (
                "Validación reiniciada: "
                f"{reason_text}"
            ),
        ),
    )

    validation.updated_by = actor

    validation.full_clean()
    validation.save()

    update_repair_snmp_state(
        validation.repair,
        actor,
    )

    return validation


@transaction.atomic
def archive_snmp_validation(
    *,
    validation,
    actor=None,
    reason="",
):
    validation = (
        RepairSNMPValidation.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=validation.pk)
    )

    if validation.archived_at is not None:
        raise ValidationError(
            "La validación SNMP ya está archivada."
        )

    repair = validation.repair

    validation.archive(
        user=actor,
        reason=normalize_text(
            reason
        ),
    )

    update_repair_snmp_state(
        repair,
        actor,
    )

    return validation


@transaction.atomic
def restore_snmp_validation(
    *,
    validation,
    actor=None,
):
    validation = (
        RepairSNMPValidation.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=validation.pk)
    )

    if validation.archived_at is None:
        raise ValidationError(
            "La validación SNMP no está archivada."
        )

    if not validation.repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )

    repair = validation.repair

    validation.restore(
        user=actor,
    )

    update_repair_snmp_state(
        repair,
        actor,
    )

    return validation