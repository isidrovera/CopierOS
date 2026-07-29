# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models.repair_part_replacement import RepairPartReplacement
from ..models.repair_part_request_item import RepairPartRequestItem
from .repair_part_request_history import create_part_request_history


@transaction.atomic
def complete_repair_part_replacement(
    *,
    replacement,
    actor,
    notes="",
):
    if replacement.status in {
        RepairPartReplacement.Status.NOT_APPLICABLE,
        RepairPartReplacement.Status.CANCELLED,
        RepairPartReplacement.Status.COMPLETED,
    }:
        raise ValidationError(
            "La reposición no puede completarse en su estado actual."
        )

    if (
        replacement.replacement_type
        == RepairPartReplacement.ReplacementType.EQUIVALENT_PART
        and not replacement.replacement_inventory_id
    ):
        raise ValidationError(
            "Debe indicar el componente usado para la reposición."
        )

    item = replacement.item
    previous_status = item.status

    replacement.status = RepairPartReplacement.Status.COMPLETED
    replacement.completed_by = actor
    replacement.completed_at = timezone.now()
    replacement.notes = (
        f"{replacement.notes}\n{notes}".strip()
    )
    replacement.updated_by = actor
    replacement.save()

    item.status = RepairPartRequestItem.Status.COMPLETED
    item.updated_by = actor
    item.save(
        update_fields=[
            "status",
            "updated_by",
            "updated_at",
        ]
    )

    request_instance = item.request
    request_instance.has_pending_replacements = (
        request_instance.items.filter(
            replacement__isnull=False,
        )
        .exclude(
            replacement__status=(
                RepairPartReplacement.Status.COMPLETED
            )
        )
        .exists()
    )
    request_instance.updated_by = actor
    request_instance.save(
        update_fields=[
            "has_pending_replacements",
            "updated_by",
            "updated_at",
        ]
    )

    create_part_request_history(
        request_instance=request_instance,
        item=item,
        actor=actor,
        event="replacement_completed",
        previous_status=previous_status,
        new_status=item.status,
        comment=notes,
        source="api",
    )

    return replacement
