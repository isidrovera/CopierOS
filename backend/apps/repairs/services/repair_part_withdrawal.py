# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models.repair_part_request_item import RepairPartRequestItem
from ..models.repair_part_withdrawal import RepairPartWithdrawal
from .repair_part_request_history import create_part_request_history


@transaction.atomic
def authorize_repair_part_withdrawal(
    *,
    withdrawal,
    actor,
    authorized_person,
    valid_until=None,
    notes="",
):
    if withdrawal.status not in {
        RepairPartWithdrawal.Status.PENDING,
        RepairPartWithdrawal.Status.REJECTED,
    }:
        raise ValidationError(
            "El retiro no está pendiente de autorización."
        )

    item = withdrawal.item
    previous_status = item.status

    withdrawal.status = RepairPartWithdrawal.Status.AUTHORIZED
    withdrawal.authorized_person = authorized_person
    withdrawal.authorized_by = actor
    withdrawal.authorized_at = timezone.now()
    withdrawal.valid_until = valid_until
    withdrawal.authorization_notes = notes
    withdrawal.updated_by = actor
    withdrawal.save()

    item.status = (
        RepairPartRequestItem.Status.AUTHORIZED_FOR_WITHDRAWAL
    )
    item.updated_by = actor
    item.save(
        update_fields=[
            "status",
            "updated_by",
            "updated_at",
        ]
    )

    create_part_request_history(
        request_instance=item.request,
        item=item,
        actor=actor,
        event="withdrawal_authorized",
        previous_status=previous_status,
        new_status=item.status,
        comment=notes,
        source="api",
    )

    return withdrawal


@transaction.atomic
def confirm_repair_part_withdrawal(
    *,
    withdrawal,
    actor,
    notes="",
):
    if withdrawal.status != RepairPartWithdrawal.Status.AUTHORIZED:
        raise ValidationError(
            "El retiro debe estar autorizado."
        )

    if (
        withdrawal.authorized_person_id
        and withdrawal.authorized_person_id != actor.id
    ):
        raise ValidationError(
            "El usuario no está autorizado para retirar esta parte."
        )

    if withdrawal.valid_until and withdrawal.valid_until < timezone.now():
        raise ValidationError(
            "La autorización de retiro ha vencido."
        )

    item = withdrawal.item
    previous_status = item.status

    withdrawal.status = RepairPartWithdrawal.Status.WITHDRAWN
    withdrawal.withdrawn_by = actor
    withdrawal.withdrawn_at = timezone.now()
    withdrawal.withdrawal_notes = notes
    withdrawal.updated_by = actor
    withdrawal.save()

    item.status = RepairPartRequestItem.Status.WITHDRAWN
    item.updated_by = actor
    item.save(
        update_fields=[
            "status",
            "updated_by",
            "updated_at",
        ]
    )

    create_part_request_history(
        request_instance=item.request,
        item=item,
        actor=actor,
        event="part_withdrawn",
        previous_status=previous_status,
        new_status=item.status,
        comment=notes,
        source="api",
    )

    return withdrawal


@transaction.atomic
def receive_repair_part_withdrawal(
    *,
    withdrawal,
    actor,
    notes="",
):
    if withdrawal.status != RepairPartWithdrawal.Status.WITHDRAWN:
        raise ValidationError(
            "La parte todavía no ha sido retirada."
        )

    item = withdrawal.item
    previous_status = item.status

    withdrawal.status = RepairPartWithdrawal.Status.RECEIVED
    withdrawal.received_by = actor
    withdrawal.received_at = timezone.now()
    withdrawal.withdrawal_notes = (
        f"{withdrawal.withdrawal_notes}\n{notes}".strip()
    )
    withdrawal.updated_by = actor
    withdrawal.save()

    item.status = RepairPartRequestItem.Status.RECEIVED
    item.received_quantity = withdrawal.quantity
    item.updated_by = actor
    item.save(
        update_fields=[
            "status",
            "received_quantity",
            "updated_by",
            "updated_at",
        ]
    )

    create_part_request_history(
        request_instance=item.request,
        item=item,
        actor=actor,
        event="withdrawal_received",
        previous_status=previous_status,
        new_status=item.status,
        comment=notes,
        source="api",
    )

    return withdrawal
