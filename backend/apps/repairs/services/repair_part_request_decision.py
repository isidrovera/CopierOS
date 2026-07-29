# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models.repair_part_request import RepairPartRequest
from ..models.repair_part_request_decision import RepairPartRequestDecision
from ..models.repair_part_request_item import RepairPartRequestItem
from .repair_part_request_history import create_part_request_history


@transaction.atomic
def decide_repair_part_request_item(
    *,
    request_instance,
    actor,
    decision,
    item=None,
    approved_quantity=0,
    reason="",
    information_required="",
    is_final=True,
):
    if item and item.request_id != request_instance.id:
        raise ValidationError(
            "El ítem no pertenece a la solicitud."
        )

    target_quantity = (
        item.requested_quantity
        if item
        else sum(
            request_instance.items.filter(
                archived_at__isnull=True,
            ).values_list(
                "requested_quantity",
                flat=True,
            )
        )
    )

    previous_decision = ""
    if item:
        previous = item.decisions.order_by("-decided_at").first()
        previous_decision = previous.decision if previous else ""

    decision_instance = RepairPartRequestDecision.objects.create(
        request=request_instance,
        item=item,
        decision=decision,
        requested_quantity=target_quantity,
        approved_quantity=approved_quantity,
        decided_by=actor,
        reason=reason,
        information_required=information_required,
        previous_decision=previous_decision,
        is_final=is_final,
        created_by=actor,
        updated_by=actor,
    )

    if item:
        previous_status = item.status

        if decision == RepairPartRequestDecision.Decision.APPROVED:
            item.status = RepairPartRequestItem.Status.APPROVED
            item.approved_quantity = approved_quantity
        elif (
            decision
            == RepairPartRequestDecision.Decision.PARTIALLY_APPROVED
        ):
            item.status = RepairPartRequestItem.Status.PARTIALLY_APPROVED
            item.approved_quantity = approved_quantity
        elif decision == RepairPartRequestDecision.Decision.REJECTED:
            item.status = RepairPartRequestItem.Status.REJECTED
            item.approved_quantity = 0
        elif (
            decision
            == RepairPartRequestDecision.Decision.INFORMATION_REQUIRED
        ):
            item.status = RepairPartRequestItem.Status.INFORMATION_REQUESTED

        item.management_notes = reason or information_required
        item.updated_by = actor
        item.save(
            update_fields=[
                "status",
                "approved_quantity",
                "management_notes",
                "updated_by",
                "updated_at",
            ]
        )

        create_part_request_history(
            request_instance=request_instance,
            item=item,
            actor=actor,
            event="management_decision",
            previous_status=previous_status,
            new_status=item.status,
            comment=reason or information_required,
            source="api",
            metadata={
                "decision": decision,
                "approved_quantity": str(approved_quantity),
            },
        )

    active_items = request_instance.items.filter(
        archived_at__isnull=True,
    )

    if active_items.filter(
        status=RepairPartRequestItem.Status.INFORMATION_REQUESTED,
    ).exists():
        request_instance.status = RepairPartRequest.Status.IN_REVIEW
        request_instance.current_responsible_area = (
            RepairPartRequest.ResponsibleArea.TECHNICAL
        )
    elif active_items.exclude(
        status=RepairPartRequestItem.Status.REJECTED,
    ).filter(
        status__in={
            RepairPartRequestItem.Status.APPROVED,
            RepairPartRequestItem.Status.PARTIALLY_APPROVED,
        }
    ).exists():
        if active_items.filter(
            status=RepairPartRequestItem.Status.REJECTED,
        ).exists():
            request_instance.status = (
                RepairPartRequest.Status.PARTIALLY_APPROVED
            )
        else:
            request_instance.status = RepairPartRequest.Status.APPROVED

        request_instance.current_responsible_area = (
            RepairPartRequest.ResponsibleArea.LOGISTICS
        )
        request_instance.approved_by = actor
        request_instance.approved_at = timezone.now()
    elif active_items.filter(
        status=RepairPartRequestItem.Status.REJECTED,
    ).count() == active_items.count():
        request_instance.status = RepairPartRequest.Status.REJECTED
        request_instance.current_responsible_area = (
            RepairPartRequest.ResponsibleArea.CLOSED
        )
        request_instance.rejected_by = actor
        request_instance.rejected_at = timezone.now()
        request_instance.rejection_reason = reason

    request_instance.updated_by = actor
    request_instance.save()

    return decision_instance
