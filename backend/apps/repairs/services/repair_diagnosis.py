# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import (
    Repair,
    RepairDiagnosis,
)


def normalize_text(value):
    return str(
        value or ""
    ).strip()


def validate_diagnosis_available(
    diagnosis,
):
    if diagnosis.archived_at is not None:
        raise ValidationError(
            "El diagnóstico se encuentra archivado."
        )

    if not diagnosis.repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )


def update_repair_requirements(
    repair,
    actor=None,
):
    diagnoses = RepairDiagnosis.objects.filter(
        repair=repair,
        archived_at__isnull=True,
    )

    requires_parts = diagnoses.filter(
        requires_parts=True,
    ).exists()

    requires_external_service = diagnoses.filter(
        requires_external_service=True,
    ).exists()

    changed_fields = []

    if repair.requires_parts != requires_parts:
        repair.requires_parts = requires_parts
        changed_fields.append(
            "requires_parts"
        )

    if (
        repair.requires_external_service
        != requires_external_service
    ):
        repair.requires_external_service = (
            requires_external_service
        )
        changed_fields.append(
            "requires_external_service"
        )

    if actor and changed_fields:
        repair.updated_by = actor
        changed_fields.append(
            "updated_by"
        )

    if changed_fields:
        changed_fields.append(
            "updated_at"
        )

        repair.save(
            update_fields=changed_fields,
        )

    return repair


@transaction.atomic
def create_repair_diagnosis(
    *,
    repair,
    technical_diagnosis,
    actor=None,
    diagnosis_type=None,
    severity=None,
    repairability=None,
    reported_symptoms="",
    observed_symptoms="",
    probable_cause="",
    confirmed_cause="",
    recommended_work="",
    required_parts_description="",
    estimated_work_hours=None,
    estimated_parts_cost=None,
    estimated_external_cost=None,
    requires_parts=False,
    requires_external_service=False,
    requires_additional_testing=False,
    requires_disassembly=False,
    is_main_diagnosis=False,
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

    technical_diagnosis_text = normalize_text(
        technical_diagnosis
    )

    if not technical_diagnosis_text:
        raise ValidationError(
            {
                "technical_diagnosis": (
                    "El diagnóstico técnico es obligatorio."
                )
            }
        )

    required_parts_text = normalize_text(
        required_parts_description
    )

    if (
        requires_parts
        and not required_parts_text
    ):
        raise ValidationError(
            {
                "required_parts_description": (
                    "Debes indicar los repuestos requeridos."
                )
            }
        )

    if (
        not requires_parts
        and required_parts_text
    ):
        raise ValidationError(
            {
                "required_parts_description": (
                    "No debes registrar repuestos si "
                    "no son requeridos."
                )
            }
        )

    repairability_value = (
        repairability
        or RepairDiagnosis.Repairability.PENDING
    )

    if (
        repairability_value
        == (
            RepairDiagnosis
            .Repairability
            .REPAIRABLE_WITH_PARTS
        )
        and not requires_parts
    ):
        raise ValidationError(
            {
                "requires_parts": (
                    "Debes indicar que requiere repuestos."
                )
            }
        )

    if (
        repairability_value
        == (
            RepairDiagnosis
            .Repairability
            .REPAIRABLE_WITH_EXTERNAL_SERVICE
        )
        and not requires_external_service
    ):
        raise ValidationError(
            {
                "requires_external_service": (
                    "Debes indicar que requiere "
                    "servicio externo."
                )
            }
        )

    if is_main_diagnosis:
        existing_main = (
            RepairDiagnosis.objects
            .select_for_update()
            .filter(
                repair=repair,
                is_main_diagnosis=True,
                archived_at__isnull=True,
            )
            .first()
        )

        if existing_main:
            raise ValidationError(
                {
                    "is_main_diagnosis": (
                        "La reparación ya tiene un "
                        "diagnóstico principal."
                    )
                }
            )

    diagnosis = RepairDiagnosis(
        repair=repair,
        technician=actor,
        diagnosis_type=(
            diagnosis_type
            or RepairDiagnosis.DiagnosisType.INITIAL
        ),
        severity=(
            severity
            or RepairDiagnosis.Severity.MEDIUM
        ),
        repairability=repairability_value,
        diagnosed_at=timezone.now(),
        reported_symptoms=normalize_text(
            reported_symptoms
        ),
        observed_symptoms=normalize_text(
            observed_symptoms
        ),
        probable_cause=normalize_text(
            probable_cause
        ),
        confirmed_cause=normalize_text(
            confirmed_cause
        ),
        technical_diagnosis=(
            technical_diagnosis_text
        ),
        recommended_work=normalize_text(
            recommended_work
        ),
        required_parts_description=(
            required_parts_text
        ),
        estimated_work_hours=(
            estimated_work_hours
        ),
        estimated_parts_cost=(
            estimated_parts_cost
        ),
        estimated_external_cost=(
            estimated_external_cost
        ),
        requires_parts=requires_parts,
        requires_external_service=(
            requires_external_service
        ),
        requires_additional_testing=(
            requires_additional_testing
        ),
        requires_disassembly=(
            requires_disassembly
        ),
        is_main_diagnosis=is_main_diagnosis,
        is_confirmed=False,
        observations=normalize_text(
            observations
        ),
        created_by=actor,
        updated_by=actor,
    )

    diagnosis.full_clean()
    diagnosis.save()

    update_repair_requirements(
        repair,
        actor,
    )

    return diagnosis


@transaction.atomic
def confirm_repair_diagnosis(
    *,
    diagnosis,
    actor=None,
    confirmed_cause="",
    observations="",
):
    diagnosis = (
        RepairDiagnosis.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=diagnosis.pk)
    )

    validate_diagnosis_available(
        diagnosis
    )

    if diagnosis.is_confirmed:
        raise ValidationError(
            "El diagnóstico ya se encuentra confirmado."
        )

    confirmed_cause_text = normalize_text(
        confirmed_cause
    )

    observations_text = normalize_text(
        observations
    )

    if confirmed_cause_text:
        diagnosis.confirmed_cause = (
            confirmed_cause_text
        )

    if observations_text:
        current_observations = normalize_text(
            diagnosis.observations
        )

        diagnosis.observations = (
            f"{current_observations}\n"
            f"{observations_text}"
        ).strip()

    diagnosis.is_confirmed = True
    diagnosis.confirmed_by = actor
    diagnosis.confirmed_at = timezone.now()
    diagnosis.updated_by = actor

    diagnosis.full_clean()
    diagnosis.save()

    update_repair_requirements(
        diagnosis.repair,
        actor,
    )

    return diagnosis


@transaction.atomic
def set_main_repair_diagnosis(
    *,
    diagnosis,
    actor=None,
):
    diagnosis = (
        RepairDiagnosis.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=diagnosis.pk)
    )

    validate_diagnosis_available(
        diagnosis
    )

    if diagnosis.is_main_diagnosis:
        raise ValidationError(
            "El diagnóstico ya es el principal."
        )

    current_main = (
        RepairDiagnosis.objects
        .select_for_update()
        .filter(
            repair=diagnosis.repair,
            is_main_diagnosis=True,
            archived_at__isnull=True,
        )
        .exclude(
            pk=diagnosis.pk,
        )
        .first()
    )

    if current_main:
        current_main.is_main_diagnosis = False
        current_main.updated_by = actor
        current_main.full_clean()
        current_main.save()

    diagnosis.is_main_diagnosis = True
    diagnosis.updated_by = actor
    diagnosis.full_clean()
    diagnosis.save()

    return diagnosis


@transaction.atomic
def update_repair_diagnosis(
    *,
    diagnosis,
    actor=None,
    **changes,
):
    diagnosis = (
        RepairDiagnosis.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=diagnosis.pk)
    )

    validate_diagnosis_available(
        diagnosis
    )

    protected_fields = {
        "id",
        "repair",
        "repair_id",
        "technician",
        "technician_id",
        "is_confirmed",
        "confirmed_by",
        "confirmed_by_id",
        "confirmed_at",
        "created_by",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
        "archived_reason",
    }

    for field_name, value in changes.items():
        if field_name in protected_fields:
            continue

        if not hasattr(
            diagnosis,
            field_name,
        ):
            continue

        if field_name in {
            "reported_symptoms",
            "observed_symptoms",
            "probable_cause",
            "confirmed_cause",
            "technical_diagnosis",
            "recommended_work",
            "required_parts_description",
            "observations",
        }:
            value = normalize_text(
                value
            )

        setattr(
            diagnosis,
            field_name,
            value,
        )

    if not normalize_text(
        diagnosis.technical_diagnosis
    ):
        raise ValidationError(
            {
                "technical_diagnosis": (
                    "El diagnóstico técnico es obligatorio."
                )
            }
        )

    if (
        diagnosis.requires_parts
        and not normalize_text(
            diagnosis.required_parts_description
        )
    ):
        raise ValidationError(
            {
                "required_parts_description": (
                    "Debes indicar los repuestos requeridos."
                )
            }
        )

    if (
        diagnosis.is_main_diagnosis
        and RepairDiagnosis.objects.filter(
            repair=diagnosis.repair,
            is_main_diagnosis=True,
            archived_at__isnull=True,
        )
        .exclude(
            pk=diagnosis.pk,
        )
        .exists()
    ):
        raise ValidationError(
            {
                "is_main_diagnosis": (
                    "La reparación ya tiene un "
                    "diagnóstico principal."
                )
            }
        )

    diagnosis.updated_by = actor
    diagnosis.full_clean()
    diagnosis.save()

    update_repair_requirements(
        diagnosis.repair,
        actor,
    )

    return diagnosis


@transaction.atomic
def archive_repair_diagnosis(
    *,
    diagnosis,
    actor=None,
    reason="",
):
    diagnosis = (
        RepairDiagnosis.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=diagnosis.pk)
    )

    if diagnosis.archived_at is not None:
        raise ValidationError(
            "El diagnóstico ya se encuentra archivado."
        )

    repair = diagnosis.repair

    diagnosis.archive(
        user=actor,
        reason=normalize_text(
            reason
        ),
    )

    update_repair_requirements(
        repair,
        actor,
    )

    return diagnosis


@transaction.atomic
def restore_repair_diagnosis(
    *,
    diagnosis,
    actor=None,
):
    diagnosis = (
        RepairDiagnosis.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=diagnosis.pk)
    )

    if diagnosis.archived_at is None:
        raise ValidationError(
            "El diagnóstico no se encuentra archivado."
        )

    if not diagnosis.repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )

    if (
        diagnosis.is_main_diagnosis
        and RepairDiagnosis.objects.filter(
            repair=diagnosis.repair,
            is_main_diagnosis=True,
            archived_at__isnull=True,
        )
        .exclude(
            pk=diagnosis.pk,
        )
        .exists()
    ):
        diagnosis.is_main_diagnosis = False

    repair = diagnosis.repair

    diagnosis.restore(
        user=actor,
        save=False,
    )

    diagnosis.full_clean()
    diagnosis.save()

    update_repair_requirements(
        repair,
        actor,
    )

    return diagnosis