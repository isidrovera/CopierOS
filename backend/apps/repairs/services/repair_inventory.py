# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.equipment.models import ComponentInventory

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
                )
            }
        ) from exc

    if quantity <= ZERO:
        raise ValidationError(
            {
                "quantity": (
                    "La cantidad debe ser mayor que cero."
                )
            }
        )

    return quantity


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


def validate_inventory_component(
    repair_component,
    inventory,
):
    if inventory.archived_at is not None:
        raise ValidationError(
            {
                "inventory": (
                    "El registro de inventario está archivado."
                )
            }
        )

    if not inventory.is_active:
        raise ValidationError(
            {
                "inventory": (
                    "El registro de inventario está inactivo."
                )
            }
        )

    if (
        inventory.component_id
        != repair_component.component_id
    ):
        raise ValidationError(
            {
                "inventory": (
                    "El inventario no corresponde al "
                    "componente solicitado."
                )
            }
        )


def validate_serialized_quantity(
    repair_component,
    quantity,
):
    if (
        repair_component.component
        .requires_individual_serial
        and quantity != Decimal("1.00")
    ):
        raise ValidationError(
            {
                "quantity": (
                    "Los componentes serializados deben "
                    "manejarse con cantidad igual a uno."
                )
            }
        )


def save_inventory(
    inventory,
    actor=None,
):
    if actor:
        inventory.updated_by = actor

    inventory.full_clean()
    inventory.save()


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
                )
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
    inventory,
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

    inventory = (
        ComponentInventory.objects
        .select_for_update()
        .select_related(
            "component",
        )
        .get(pk=inventory.pk)
    )

    validate_repair_component_active(
        repair_component
    )

    validate_inventory_component(
        repair_component,
        inventory,
    )

    quantity = normalize_quantity(
        quantity
    )

    validate_serialized_quantity(
        repair_component,
        quantity,
    )

    if repair_component.status not in (
        RepairComponent.Status.PENDING,
        RepairComponent.Status.REQUESTED,
    ):
        raise ValidationError(
            {
                "status": (
                    "El componente no puede reservarse "
                    "desde su estado actual."
                )
            }
        )

    if quantity > repair_component.quantity:
        raise ValidationError(
            {
                "quantity": (
                    "La cantidad reservada no puede superar "
                    "la cantidad solicitada."
                )
            }
        )

    if inventory.available_quantity < quantity:
        raise ValidationError(
            {
                "quantity": (
                    "No existe suficiente stock disponible."
                )
            }
        )

    inventory.available_quantity -= quantity
    inventory.reserved_quantity += quantity

    save_inventory(
        inventory,
        actor,
    )

    repair_component.inventory = inventory
    repair_component.status = (
        RepairComponent.Status.RESERVED
    )
    repair_component.movement_type = (
        RepairComponent.MovementType.RESERVED
    )
    repair_component.reserved_quantity = quantity
    repair_component.reserved_by = actor
    repair_component.reserved_at = timezone.now()

    if (
        repair_component.unit_cost is None
        and inventory.unit_cost is not None
    ):
        repair_component.unit_cost = (
            inventory.unit_cost
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
            "inventory",
        )
        .get(pk=repair_component.pk)
    )

    validate_repair_component_active(
        repair_component
    )

    if not repair_component.inventory_id:
        raise ValidationError(
            {
                "inventory": (
                    "El componente no tiene inventario reservado."
                )
            }
        )

    if (
        repair_component.status
        != RepairComponent.Status.RESERVED
    ):
        raise ValidationError(
            {
                "status": (
                    "Solo un componente reservado "
                    "puede entregarse."
                )
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
                    "la cantidad reservada pendiente."
                )
            }
        )

    inventory = (
        ComponentInventory.objects
        .select_for_update()
        .get(
            pk=repair_component.inventory_id
        )
    )

    if inventory.reserved_quantity < quantity:
        raise ValidationError(
            {
                "quantity": (
                    "El inventario no tiene suficiente "
                    "cantidad reservada."
                )
            }
        )

    inventory.reserved_quantity -= quantity

    save_inventory(
        inventory,
        actor,
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
    removed_inventory=None,
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
            "inventory",
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
                    "El componente debe estar reservado "
                    "o entregado antes de instalarse."
                )
            }
        )

    quantity = normalize_quantity(
        quantity
    )

    validate_serialized_quantity(
        repair_component,
        quantity,
    )

    available_to_install = (
        repair_component.delivered_quantity
        - repair_component.installed_quantity
        - repair_component.returned_quantity
        - repair_component.consumed_quantity
    )

    if available_to_install <= ZERO:
        available_to_install = (
            repair_component.reserved_quantity
            - repair_component.installed_quantity
            - repair_component.returned_quantity
            - repair_component.consumed_quantity
        )

    if quantity > available_to_install:
        raise ValidationError(
            {
                "quantity": (
                    "La cantidad instalada supera "
                    "la cantidad disponible."
                )
            }
        )

    if (
        repair_component.component
        .requires_removed_part_tracking
        and not removed_component
    ):
        raise ValidationError(
            {
                "removed_component": (
                    "Debes registrar el componente retirado."
                )
            }
        )

    if removed_inventory and removed_component:
        if (
            removed_inventory.component_id
            != removed_component.id
        ):
            raise ValidationError(
                {
                    "removed_inventory": (
                        "El inventario retirado no corresponde "
                        "al componente retirado."
                    )
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
                )
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

    repair_component.removed_component = (
        removed_component
    )
    repair_component.removed_inventory = (
        removed_inventory
    )
    repair_component.removed_serial_number = str(
        removed_serial_number or ""
    ).strip().upper()
    repair_component.removed_part_disposition = (
        disposition
    )
    repair_component.removed_part_notes = (
        append_notes(
            repair_component.removed_part_notes,
            removed_part_notes,
        )
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
    removed_part_disposition=None,
    notes="",
):
    repair_component = (
        RepairComponent.objects
        .select_for_update()
        .select_related(
            "repair",
            "component",
            "inventory",
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
                    "El componente debe estar reservado "
                    "o entregado antes de consumirse."
                )
            }
        )

    quantity = normalize_quantity(
        quantity
    )

    available_to_consume = (
        repair_component.delivered_quantity
        - repair_component.installed_quantity
        - repair_component.returned_quantity
        - repair_component.consumed_quantity
    )

    if available_to_consume <= ZERO:
        available_to_consume = (
            repair_component.reserved_quantity
            - repair_component.installed_quantity
            - repair_component.returned_quantity
            - repair_component.consumed_quantity
        )

    if quantity > available_to_consume:
        raise ValidationError(
            {
                "quantity": (
                    "La cantidad consumida supera "
                    "la cantidad disponible."
                )
            }
        )

    if (
        repair_component.component
        .requires_removed_part_tracking
        and not removed_component
    ):
        raise ValidationError(
            {
                "removed_component": (
                    "Debes registrar la pieza retirada."
                )
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
        repair_component.removed_component = (
            removed_component
        )
        repair_component.removed_by = actor
        repair_component.removed_at = timezone.now()
        repair_component.removed_part_disposition = (
            removed_part_disposition
            or (
                RepairComponent
                .RemovedPartDisposition
                .DISCARDED
            )
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
            "inventory",
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
                )
            }
        )

    if not repair_component.inventory_id:
        raise ValidationError(
            {
                "inventory": (
                    "El componente no tiene inventario asociado."
                )
            }
        )

    quantity = normalize_quantity(
        quantity
    )

    available_to_return = (
        repair_component.reserved_quantity
        + repair_component.delivered_quantity
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
                )
            }
        )

    inventory = (
        ComponentInventory.objects
        .select_for_update()
        .get(
            pk=repair_component.inventory_id
        )
    )

    reserved_pending = max(
        repair_component.reserved_quantity
        - repair_component.delivered_quantity,
        ZERO,
    )

    returned_from_reserved = min(
        quantity,
        reserved_pending,
    )

    if returned_from_reserved > ZERO:
        if (
            inventory.reserved_quantity
            < returned_from_reserved
        ):
            raise ValidationError(
                {
                    "quantity": (
                        "El inventario reservado no coincide "
                        "con la devolución."
                    )
                }
            )

        inventory.reserved_quantity -= (
            returned_from_reserved
        )

    inventory.available_quantity += quantity

    save_inventory(
        inventory,
        actor,
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
                )
            }
        )

    repair_component = (
        RepairComponent.objects
        .select_for_update()
        .select_related(
            "repair",
            "component",
            "inventory",
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
                )
            }
        )

    if (
        repair_component.inventory_id
        and repair_component.reserved_quantity > ZERO
    ):
        inventory = (
            ComponentInventory.objects
            .select_for_update()
            .get(
                pk=repair_component.inventory_id
            )
        )

        pending_reserved = max(
            repair_component.reserved_quantity
            - repair_component.delivered_quantity
            - repair_component.returned_quantity,
            ZERO,
        )

        if pending_reserved > ZERO:
            if (
                inventory.reserved_quantity
                < pending_reserved
            ):
                raise ValidationError(
                    {
                        "inventory": (
                            "La reserva del inventario no coincide "
                            "con la solicitud."
                        )
                    }
                )

            inventory.reserved_quantity -= (
                pending_reserved
            )
            inventory.available_quantity += (
                pending_reserved
            )

            save_inventory(
                inventory,
                actor,
            )

    repair_component.status = (
        RepairComponent.Status.CANCELLED
    )
    repair_component.movement_type = (
        RepairComponent.MovementType.CANCELLED
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