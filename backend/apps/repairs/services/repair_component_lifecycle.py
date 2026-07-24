# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import RepairComponent


def normalize_text(value):
    return str(
        value or ""
    ).strip()


@transaction.atomic
def archive_repair_component(
    *,
    repair_component,
    actor=None,
    reason="",
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
            "El componente de reparación ya está archivado."
        )

    if repair_component.status in (
        RepairComponent.Status.RESERVED,
        RepairComponent.Status.DELIVERED,
    ):
        raise ValidationError(
            {
                "status": (
                    "No puedes archivar un componente "
                    "con stock reservado o entregado. "
                    "Primero debes devolverlo o cancelarlo."
                )
            }
        )

    if repair_component.status not in (
        RepairComponent.Status.PENDING,
        RepairComponent.Status.REQUESTED,
        RepairComponent.Status.INSTALLED,
        RepairComponent.Status.CONSUMED,
        RepairComponent.Status.RETURNED,
        RepairComponent.Status.DISCARDED,
        RepairComponent.Status.CANCELLED,
    ):
        raise ValidationError(
            {
                "status": (
                    "El componente no puede archivarse "
                    "desde su estado actual."
                )
            }
        )

    repair_component.archive(
        user=actor,
        reason=normalize_text(
            reason
        ),
    )

    return repair_component


@transaction.atomic
def restore_repair_component(
    *,
    repair_component,
    actor=None,
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

    if repair_component.archived_at is None:
        raise ValidationError(
            "El componente de reparación no está archivado."
        )

    if repair_component.repair.archived_at is not None:
        raise ValidationError(
            "La reparación se encuentra archivada."
        )

    if not repair_component.repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )

    if repair_component.component.archived_at is not None:
        raise ValidationError(
            {
                "component": (
                    "El componente técnico está archivado."
                )
            }
        )

    if not repair_component.component.is_active:
        raise ValidationError(
            {
                "component": (
                    "El componente técnico está inactivo."
                )
            }
        )

    if repair_component.inventory_id:
        inventory = repair_component.inventory

        if inventory.archived_at is not None:
            raise ValidationError(
                {
                    "inventory": (
                        "El inventario asociado está archivado."
                    )
                }
            )

        if not inventory.is_active:
            raise ValidationError(
                {
                    "inventory": (
                        "El inventario asociado está inactivo."
                    )
                }
            )

    repair_component.restore(
        user=actor,
    )

    return repair_component