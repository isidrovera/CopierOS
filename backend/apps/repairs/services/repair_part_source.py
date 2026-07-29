# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction

from ..models.repair_part_request_item import RepairPartRequestItem
from ..models.repair_part_source import RepairPartSource
from .repair_part_request_history import create_part_request_history


@transaction.atomic
def confirm_repair_part_source(
    *,
    source,
    actor,
):
    if source.is_confirmed:
        raise ValidationError(
            "El origen ya está confirmado."
        )

    item = source.item
    previous_status = item.status

    source.is_confirmed = True
    source.updated_by = actor
    source.save(
        update_fields=[
            "is_confirmed",
            "updated_by",
            "updated_at",
        ]
    )

    item.source_type = source.source_type
    item.inventory = source.inventory
    item.donor_equipment = source.donor_equipment
    item.donor_rental_equipment = source.donor_rental_equipment

    if source.source_type == RepairPartSource.SourceType.EXTERNAL_PURCHASE:
        item.status = RepairPartRequestItem.Status.PENDING_PURCHASE
    elif source.source_type == RepairPartSource.SourceType.EXTERNAL_REPAIR:
        item.status = RepairPartRequestItem.Status.PENDING_EXTERNAL_REPAIR
    elif source.source_type in {
        RepairPartSource.SourceType.DONOR_FOR_PARTS,
        RepairPartSource.SourceType.DONOR_WITH_PROBLEMS,
        RepairPartSource.SourceType.DONOR_OPERATIONAL,
    }:
        item.status = RepairPartRequestItem.Status.PENDING_WITHDRAWAL
    elif source.source_type == RepairPartSource.SourceType.NOT_AVAILABLE:
        item.status = RepairPartRequestItem.Status.REJECTED
    else:
        item.status = RepairPartRequestItem.Status.PENDING_RESERVATION

    item.updated_by = actor
    item.save(
        update_fields=[
            "source_type",
            "inventory",
            "donor_equipment",
            "donor_rental_equipment",
            "status",
            "updated_by",
            "updated_at",
        ]
    )

    create_part_request_history(
        request_instance=item.request,
        item=item,
        actor=actor,
        event="source_confirmed",
        previous_status=previous_status,
        new_status=item.status,
        source="api",
        metadata={"source_type": source.source_type},
    )

    return source
