# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import RepairComponent


ZERO = Decimal("0.00")


def normalize_quantity(value):
    try:
        quantity = Decimal(str(value))
    except (
        TypeError,
        ValueError,
        ArithmeticError,
    ) as exc:
        raise ValidationError(
            {
                "quantity": (
                    "La cantidad ingresada no es válida."
                ),
            }
        ) from exc

    if quantity <= ZERO:
        raise ValidationError(
            {
                "quantity": (
                    "La cantidad debe ser mayor que cero."
                ),
            }
        )

    return quantity


def normalize_serial_number(value):
    return str(
        value or ""
    ).strip().upper()


def append_notes(
    current_notes,
    new_notes,
):
    current_text = str(
        current_notes or ""
    ).strip()

    new_text = str(
        new_notes or ""
    ).strip()

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


def validate_repair_component_active(
    repair_component,
):
    if repair_component.archived_at is not None:
        raise ValidationError(
            "El componente de reparación está archivado."
        )

    if not repair_component.repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )


def validate_serialized_quantity(
    repair_component,
    quantity,
):
    if (
        repair_component.component.requires_individual_serial
        and quantity != Decimal("1.00")
    ):
        raise ValidationError(
            {
                "quantity": (
                    "Los componentes serializados deben "
                    "manejarse con cantidad igual a uno."
                ),
            }
        )


def validate_component_serial(
    repair_component,
    serial_number,
):
    if (
        repair_component.component.requires_individual_serial
        and not serial_number
    ):
        raise ValidationError(
            {
                "serial_number": (
                    "Debe registrar la serie física "
                    "del componente."
                ),
            }
        )


def save_repair_component(
    repair_component,
    actor=None,
):
    if actor:
        repair_component.updated_by = actor

    repair_component.full_clean()
    repair_component.save()


@transaction.atomic
def request_component(
    *,
    repair_component,
    actor=None,
    notes="",
):
    repair_component = (
        RepairComponent.objects
        .select_for_update()
        .select_related(
            "repair",
            "component",
        )
        .get(pk=repair_component.pk)
    )

    validate_repair_component_active(
        repair_component
    )

    if (
        repair_component.status
        != RepairComponent.Status.PENDING
    ):
        raise ValidationError(
            {
                "status": (
                    "Solo un componente pendiente "
                    "puede solicitarse."
                ),
            }
        )

    repair_component.status = (
        RepairComponent.Status.REQUESTED
    )
    repair_component.movement_type = (
        RepairComponent.MovementType.REQUIRED
    )
    repair_component.requested_by = actor
    repair_component.requested_at = timezone.now()
    repair_component.notes = append_notes(
        repair_component.notes,
        notes,
    )

    save_repair_component(
        repair_component,
        actor,
    )

    return repair_component


@transaction.atomic
def reserve_component(
    *,
    repair_component,
    quantity,
    serial_number="",
    actor=None,
    notes="",
):
    repair_component = (
        RepairComponent.objects
        .select_for_update()
        .select_related(
            "repair",
            "component",
        )
        .get(pk=repair_component.pk)
    )

    validate_repair_component_active(
        repair_component
    )

    quantity = normalize_quantity(
        quantity
    )

    serial_number = normalize_serial_number(
        serial_number
    )

    validate_serialized_quantity(
        repair_component,
        quantity,
    )

    validate_component_serial(
        repair_component,
        serial_number,
    )

    if repair_component.status not in (
        RepairComponent.Status.PENDING,
        RepairComponent.Status.REQUESTED,
    ):
        raise ValidationError(
            {
                "status": (
                    "El componente no puede prepararse "
                    "desde su estado actual."
                ),
            }
        )

    if quantity > repair_component.quantity:
        raise ValidationError(
            {
                "quantity": (
                    "La cantidad preparada no puede superar "
                    "la cantidad solicitada."
                ),
            }
        )

    repair_component.serial_number = serial_number
    repair_component.status = (
        RepairComponent.Status.RESERVED
    )
    repair_component.movement_type = (
        RepairComponent.MovementType.RESERVED
    )
    repair_component.reserved_quantity = quantity
    repair_component.reserved_by = actor
    repair_component.reserved_at = timezone.now()
    repair_component.notes = append_notes(
        repair_component.notes,
        notes,
    )

    save_repair_component(
        repair_component,
        actor,
    )

    return repair_component


@transaction.atomic
def deliver_component(
    *,
    repair_component,
    quantity,
    actor=None,
    notes="",
):
    repair_component = (
        RepairComponent.objects
        .select_for_update()
        .select_related(
            "repair",
            "component",
        )
        .get(pk=repair_component.pk)
    )

    validate_repair_component_active(
        repair_component
    )

    if (
        repair_component.status
        != RepairComponent.Status.RESERVED
    ):
        raise ValidationError(
            {
                "status": (
                    "Solo un componente preparado "
                    "puede entregarse."
                ),
            }
        )

    quantity = normalize_quantity(
        quantity
    )

    pending_reserved = (
        repair_component.reserved_quantity
        - repair_component.delivered_quantity
    )

    if quantity > pending_reserved:
        raise ValidationError(
            {
                "quantity": (
                    "La cantidad entregada supera "
                    "la cantidad preparada pendiente."
                ),
            }
        )

    repair_component.delivered_quantity += quantity
    repair_component.status = (
        RepairComponent.Status.DELIVERED
    )
    repair_component.movement_type = (
        RepairComponent.MovementType.DELIVERED
    )
    repair_component.delivered_by = actor
    repair_component.delivered_at = timezone.now()
    repair_component.notes = append_notes(
        repair_component.notes,
        notes,
    )

    save_repair_component(
        repair_component,
        actor,
    )

    return repair_component


@transaction.atomic
def install_component(
    *,
    repair_component,
    quantity,
    actor=None,
    removed_component=None,
    removed_serial_number="",
    removed_part_disposition=None,
    removed_part_notes="",
    notes="",
):
    repair_component = (
        RepairComponent.objects
        .select_for_update()
        .select_related(
            "repair",
            "component",
        )
        .get(pk=repair_component.pk)
    )

    validate_repair_component_active(
        repair_component
    )

    if repair_component.status not in (
        RepairComponent.Status.RESERVED,
        RepairComponent.Status.DELIVERED,
    ):
        raise ValidationError(
            {
                "status": (
                    "El componente debe estar preparado "
                    "o entregado antes de instalarse."
                ),
            }
        )

    quantity = normalize_quantity(
        quantity
    )

    validate_serialized_quantity(
        repair_component,
        quantity,
    )

    delivered_available = (
        repair_component.delivered_quantity
        - repair_component.installed_quantity
        - repair_component.returned_quantity
        - repair_component.consumed_quantity
    )

    reserved_available = (
        repair_component.reserved_quantity
        - repair_component.installed_quantity
        - repair_component.returned_quantity
        - repair_component.consumed_quantity
    )

    available_to_install = (
        delivered_available
        if delivered_available > ZERO
        else reserved_available
    )

    if quantity > available_to_install:
        raise ValidationError(
            {
                "quantity": (
                    "La cantidad instalada supera "
                    "la cantidad disponible."
                ),
            }
        )

    removed_serial_number = normalize_serial_number(
        removed_serial_number
    )

    if (
        repair_component.component.requires_removed_part_tracking
        and not removed_component
    ):
        raise ValidationError(
            {
                "removed_component": (
                    "Debes registrar el componente retirado."
                ),
            }
        )

    if (
        removed_component
        and removed_component.requires_individual_serial
        and not removed_serial_number
    ):
        raise ValidationError(
            {
                "removed_serial_number": (
                    "Debes registrar la serie del "
                    "componente retirado."
                ),
            }
        )

    disposition = (
        removed_part_disposition
        or (
            RepairComponent
            .RemovedPartDisposition
            .NOT_APPLICABLE
        )
    )

    if (
        removed_component
        and disposition
        == (
            RepairComponent
            .RemovedPartDisposition
            .NOT_APPLICABLE
        )
    ):
        raise ValidationError(
            {
                "removed_part_disposition": (
                    "Debes indicar el destino "
                    "del componente retirado."
                ),
            }
        )

    repair_component.installed_quantity += quantity
    repair_component.status = (
        RepairComponent.Status.INSTALLED
    )
    repair_component.movement_type = (
        RepairComponent.MovementType.INSTALLED
    )
    repair_component.installed_by = actor
    repair_component.installed_at = timezone.now()

    repair_component.removed_component = removed_component
    repair_component.removed_serial_number = (
        removed_serial_number
    )
    repair_component.removed_part_disposition = (
        disposition
    )
    repair_component.removed_part_notes = append_notes(
        repair_component.removed_part_notes,
        removed_part_notes,
    )

    if removed_component:
        repair_component.removed_by = actor
        repair_component.removed_at = timezone.now()

    repair_component.notes = append_notes(
        repair_component.notes,
        notes,
    )

    save_repair_component(
        repair_component,
        actor,
    )

    return repair_component


@transaction.atomic
def consume_component(
    *,
    repair_component,
    quantity,
    actor=None,
    removed_component=None,
    removed_serial_number="",
    removed_part_disposition=None,
    notes="",
):
    repair_component = (
        RepairComponent.objects
        .select_for_update()
        .select_related(
            "repair",
            "component",
        )
        .get(pk=repair_component.pk)
    )

    validate_repair_component_active(
        repair_component
    )

    if repair_component.status not in (
        RepairComponent.Status.RESERVED,
        RepairComponent.Status.DELIVERED,
    ):
        raise ValidationError(
            {
                "status": (
                    "El componente debe estar preparado "
                    "o entregado antes de consumirse."
                ),
            }
        )

    quantity = normalize_quantity(
        quantity
    )

    delivered_available = (
        repair_component.delivered_quantity
        - repair_component.installed_quantity
        - repair_component.returned_quantity
        - repair_component.consumed_quantity
    )

    reserved_available = (
        repair_component.reserved_quantity
        - repair_component.installed_quantity
        - repair_component.returned_quantity
        - repair_component.consumed_quantity
    )

    available_to_consume = (
        delivered_available
        if delivered_available > ZERO
        else reserved_available
    )

    if quantity > available_to_consume:
        raise ValidationError(
            {
                "quantity": (
                    "La cantidad consumida supera "
                    "la cantidad disponible."
                ),
            }
        )

    if (
        repair_component.component.requires_removed_part_tracking
        and not removed_component
    ):
        raise ValidationError(
            {
                "removed_component": (
                    "Debes registrar la pieza retirada."
                ),
            }
        )

    removed_serial_number = normalize_serial_number(
        removed_serial_number
    )

    if (
        removed_component
        and removed_component.requires_individual_serial
        and not removed_serial_number
    ):
        raise ValidationError(
            {
                "removed_serial_number": (
                    "Debes registrar la serie de la "
                    "pieza retirada."
                ),
            }
        )

    repair_component.consumed_quantity += quantity
    repair_component.status = (
        RepairComponent.Status.CONSUMED
    )
    repair_component.movement_type = (
        RepairComponent.MovementType.CONSUMED
    )
    repair_component.installed_by = actor
    repair_component.installed_at = timezone.now()

    if removed_component:
        repair_component.removed_component = removed_component
        repair_component.removed_serial_number = (
            removed_serial_number
        )
        repair_component.removed_by = actor
        repair_component.removed_at = timezone.now()
        repair_component.removed_part_disposition = (
            removed_part_disposition
            or RepairComponent.RemovedPartDisposition.DISCARD
        )

    repair_component.notes = append_notes(
        repair_component.notes,
        notes,
    )

    save_repair_component(
        repair_component,
        actor,
    )

    return repair_component


@transaction.atomic
def return_component(
    *,
    repair_component,
    quantity,
    actor=None,
    notes="",
):
    repair_component = (
        RepairComponent.objects
        .select_for_update()
        .select_related(
            "repair",
            "component",
        )
        .get(pk=repair_component.pk)
    )

    if repair_component.archived_at is not None:
        raise ValidationError(
            "El componente de reparación está archivado."
        )

    if repair_component.status not in (
        RepairComponent.Status.RESERVED,
        RepairComponent.Status.DELIVERED,
    ):
        raise ValidationError(
            {
                "status": (
                    "El componente no puede devolverse "
                    "desde su estado actual."
                ),
            }
        )

    quantity = normalize_quantity(
        quantity
    )

    available_to_return = (
        max(
            repair_component.delivered_quantity,
            repair_component.reserved_quantity,
        )
        - repair_component.installed_quantity
        - repair_component.consumed_quantity
        - repair_component.returned_quantity
    )

    if quantity > available_to_return:
        raise ValidationError(
            {
                "quantity": (
                    "La cantidad devuelta supera "
                    "la cantidad disponible."
                ),
            }
        )

    repair_component.returned_quantity += quantity
    repair_component.status = (
        RepairComponent.Status.RETURNED
    )
    repair_component.movement_type = (
        RepairComponent.MovementType.RETURNED
    )
    repair_component.returned_by = actor
    repair_component.returned_at = timezone.now()
    repair_component.notes = append_notes(
        repair_component.notes,
        notes,
    )

    save_repair_component(
        repair_component,
        actor,
    )

    return repair_component


@transaction.atomic
def cancel_component_request(
    *,
    repair_component,
    actor=None,
    reason="",
):
    cancellation_reason = str(
        reason or ""
    ).strip()

    if not cancellation_reason:
        raise ValidationError(
            {
                "reason": (
                    "El motivo de cancelación es obligatorio."
                ),
            }
        )

    repair_component = (
        RepairComponent.objects
        .select_for_update()
        .select_related(
            "repair",
            "component",
        )
        .get(pk=repair_component.pk)
    )

    if repair_component.status in (
        RepairComponent.Status.INSTALLED,
        RepairComponent.Status.CONSUMED,
        RepairComponent.Status.RETURNED,
        RepairComponent.Status.DISCARDED,
        RepairComponent.Status.CANCELLED,
    ):
        raise ValidationError(
            {
                "status": (
                    "El componente ya no puede cancelarse."
                ),
            }
        )

    repair_component.status = (
        RepairComponent.Status.CANCELLED
    )
    repair_component.notes = append_notes(
        repair_component.notes,
        cancellation_reason,
    )

    save_repair_component(
        repair_component,
        actor,
    )

    return repair_component