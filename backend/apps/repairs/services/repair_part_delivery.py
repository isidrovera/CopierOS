# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models.repair_part_delivery import RepairPartDelivery
from ..models.repair_part_request_item import RepairPartRequestItem
from .repair_part_request_history import create_part_request_history


@transaction.atomic
def prepare_repair_part_delivery(
    *,
    delivery,
    actor,
    notes="",
):
    if delivery.status not in {
        RepairPartDelivery.Status.PENDING,
        RepairPartDelivery.Status.PREPARING,
    }:
        raise ValidationError(
            "La entrega no puede prepararse en su estado actual."
        )

    item = delivery.item
    previous_status = item.status

    delivery.status = RepairPartDelivery.Status.READY
    delivery.prepared_by = actor
    delivery.prepared_at = timezone.now()
    delivery.notes = notes
    delivery.updated_by = actor
    delivery.save()

    item.status = RepairPartRequestItem.Status.PREPARED
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
        event="delivery_prepared",
        previous_status=previous_status,
        new_status=item.status,
        comment=notes,
        source="api",
    )

    return delivery


@transaction.atomic
def deliver_repair_part(
    *,
    delivery,
    actor,
    delivered_to,
    quantity,
    delivery_document="",
    notes="",
):
    if delivery.status != RepairPartDelivery.Status.READY:
        raise ValidationError(
            "La entrega debe estar preparada."
        )

    if quantity <= 0:
        raise ValidationError(
            "La cantidad debe ser mayor que cero."
        )

    item = delivery.item

    if quantity > item.approved_quantity:
        raise ValidationError(
            "La cantidad entregada supera la cantidad aprobada."
        )

    previous_status = item.status

    delivery.status = RepairPartDelivery.Status.DELIVERED
    delivery.delivered_by = actor
    delivery.delivered_to = delivered_to
    delivery.delivered_at = timezone.now()
    delivery.quantity = quantity
    delivery.delivery_document = delivery_document
    delivery.notes = notes
    delivery.updated_by = actor
    delivery.save()

    item.status = RepairPartRequestItem.Status.DELIVERED
    item.delivered_quantity = quantity
    item.updated_by = actor
    item.save(
        update_fields=[
            "status",
            "delivered_quantity",
            "updated_by",
            "updated_at",
        ]
    )

    create_part_request_history(
        request_instance=item.request,
        item=item,
        actor=actor,
        event="part_delivered",
        previous_status=previous_status,
        new_status=item.status,
        comment=notes,
        source="api",
        metadata={"quantity": str(quantity)},
    )

    return delivery


@transaction.atomic
def receive_repair_part_delivery(
    *,
    delivery,
    actor,
    received_quantity,
    notes="",
):
    if delivery.status != RepairPartDelivery.Status.DELIVERED:
        raise ValidationError(
            "La parte todavía no ha sido entregada."
        )

    if received_quantity <= 0:
        raise ValidationError(
            "La cantidad recibida debe ser mayor que cero."
        )

    if received_quantity > delivery.quantity:
        raise ValidationError(
            "La cantidad recibida supera la cantidad entregada."
        )

    item = delivery.item
    previous_status = item.status

    delivery.received_quantity = received_quantity
    delivery.confirmed_by = actor
    delivery.confirmed_at = timezone.now()
    delivery.status = (
        RepairPartDelivery.Status.RECEIVED
        if received_quantity == delivery.quantity
        else RepairPartDelivery.Status.PARTIALLY_RECEIVED
    )
    delivery.notes = f"{delivery.notes}\n{notes}".strip()
    delivery.updated_by = actor
    delivery.save()

    item.received_quantity = (
        item.received_quantity + received_quantity
    )
    item.status = RepairPartRequestItem.Status.RECEIVED
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
        event="delivery_received",
        previous_status=previous_status,
        new_status=item.status,
        comment=notes,
        source="api",
        metadata={"received_quantity": str(received_quantity)},
    )

    return delivery
