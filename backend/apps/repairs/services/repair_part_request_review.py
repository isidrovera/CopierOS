# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction

from ..models.repair_part_request import RepairPartRequest
from ..models.repair_part_request_item import RepairPartRequestItem
from ..models.repair_part_request_review import RepairPartRequestReview
from .repair_part_request_history import create_part_request_history


@transaction.atomic
def review_repair_part_request_item(
    *,
    item,
    actor,
    result,
    justification,
    proposed_quantity=0,
    requires_management_approval=True,
    requires_replacement=False,
):
    if item.status not in {
        RepairPartRequestItem.Status.PENDING_AREA_REVIEW,
        RepairPartRequestItem.Status.SOURCE_EVALUATION,
        RepairPartRequestItem.Status.INFORMATION_REQUESTED,
    }:
        raise ValidationError(
            "El ítem no está pendiente de revisión."
        )

    previous_status = item.status

    review = RepairPartRequestReview.objects.create(
        item=item,
        result=result,
        reviewed_by=actor,
        justification=justification,
        proposed_quantity=proposed_quantity,
        requires_management_approval=requires_management_approval,
        requires_replacement=requires_replacement,
        created_by=actor,
        updated_by=actor,
    )

    if result == RepairPartRequestReview.Result.INFORMATION_REQUIRED:
        item.status = RepairPartRequestItem.Status.INFORMATION_REQUESTED
    elif result == RepairPartRequestReview.Result.NOT_AVAILABLE:
        item.status = RepairPartRequestItem.Status.REJECTED
    elif requires_management_approval:
        item.status = RepairPartRequestItem.Status.PENDING_MANAGEMENT
    elif result == RepairPartRequestReview.Result.PURCHASE:
        item.status = RepairPartRequestItem.Status.PENDING_PURCHASE
    elif result == RepairPartRequestReview.Result.EXTERNAL_REPAIR:
        item.status = RepairPartRequestItem.Status.PENDING_EXTERNAL_REPAIR
    else:
        item.status = RepairPartRequestItem.Status.PENDING_RESERVATION

    item.area_manager_notes = justification
    item.requires_replacement = requires_replacement
    item.updated_by = actor
    item.save(
        update_fields=[
            "status",
            "area_manager_notes",
            "requires_replacement",
            "updated_by",
            "updated_at",
        ]
    )

    request_instance = item.request
    request_instance.status = RepairPartRequest.Status.IN_REVIEW
    request_instance.current_responsible_area = (
        RepairPartRequest.ResponsibleArea.MANAGEMENT
        if requires_management_approval
        else RepairPartRequest.ResponsibleArea.LOGISTICS
    )
    request_instance.updated_by = actor
    request_instance.save(
        update_fields=[
            "status",
            "current_responsible_area",
            "updated_by",
            "updated_at",
        ]
    )

    create_part_request_history(
        request_instance=request_instance,
        item=item,
        actor=actor,
        event="area_reviewed",
        previous_status=previous_status,
        new_status=item.status,
        comment=justification,
        source="api",
        metadata={"result": result},
    )

    return review
