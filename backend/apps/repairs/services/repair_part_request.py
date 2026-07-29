# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models.repair_part_request import RepairPartRequest
from ..models.repair_part_request_item import RepairPartRequestItem
from .repair_part_request_history import create_part_request_history


@transaction.atomic
def submit_repair_part_request(
    *,
    request_instance,
    actor,
    observations="",
):
    if request_instance.status != RepairPartRequest.Status.DRAFT:
        raise ValidationError(
            "Solo puedes enviar una solicitud en borrador."
        )

    active_items = request_instance.items.filter(
        archived_at__isnull=True,
    )

    if not active_items.exists():
        raise ValidationError(
            "La solicitud debe contener al menos un ítem."
        )

    previous_status = request_instance.status
    previous_area = request_instance.current_responsible_area

    request_instance.status = RepairPartRequest.Status.SUBMITTED
    request_instance.submitted_by = actor
    request_instance.submitted_at = timezone.now()
    request_instance.updated_by = actor

    direct_management = not active_items.filter(
        approval_route=(
            RepairPartRequestItem.ApprovalRoute.AREA_MANAGER_REVIEW
        )
    ).exists()

    if direct_management:
        request_instance.current_responsible_area = (
            RepairPartRequest.ResponsibleArea.MANAGEMENT
        )
        active_items.update(
            status=RepairPartRequestItem.Status.PENDING_MANAGEMENT,
            updated_by=actor,
        )
    else:
        request_instance.current_responsible_area = (
            RepairPartRequest.ResponsibleArea.AREA_MANAGER
        )
        for item in active_items:
            if (
                item.approval_route
                == RepairPartRequestItem.ApprovalRoute.DIRECT_MANAGEMENT
            ):
                item.status = (
                    RepairPartRequestItem.Status.PENDING_MANAGEMENT
                )
            else:
                item.status = (
                    RepairPartRequestItem.Status.PENDING_AREA_REVIEW
                )
            item.updated_by = actor
            item.save(
                update_fields=[
                    "status",
                    "updated_by",
                    "updated_at",
                ]
            )

    request_instance.save(
        update_fields=[
            "status",
            "submitted_by",
            "submitted_at",
            "current_responsible_area",
            "updated_by",
            "updated_at",
        ]
    )

    create_part_request_history(
        request_instance=request_instance,
        actor=actor,
        event="submitted",
        previous_status=previous_status,
        new_status=request_instance.status,
        previous_area=previous_area,
        new_area=request_instance.current_responsible_area,
        comment=observations,
        source="api",
    )

    return request_instance


@transaction.atomic
def cancel_repair_part_request(
    *,
    request_instance,
    actor,
    reason,
):
    if request_instance.status in {
        RepairPartRequest.Status.CANCELLED,
        RepairPartRequest.Status.CLOSED,
    }:
        raise ValidationError(
            "La solicitud ya está cancelada o cerrada."
        )

    previous_status = request_instance.status
    previous_area = request_instance.current_responsible_area

    request_instance.status = RepairPartRequest.Status.CANCELLED
    request_instance.current_responsible_area = (
        RepairPartRequest.ResponsibleArea.CLOSED
    )
    request_instance.general_observations = (
        f"{request_instance.general_observations}\n{reason}".strip()
    )
    request_instance.updated_by = actor
    request_instance.save(
        update_fields=[
            "status",
            "current_responsible_area",
            "general_observations",
            "updated_by",
            "updated_at",
        ]
    )

    request_instance.items.filter(
        archived_at__isnull=True,
    ).exclude(
        status=RepairPartRequestItem.Status.COMPLETED,
    ).update(
        status=RepairPartRequestItem.Status.CANCELLED,
        updated_by=actor,
    )

    create_part_request_history(
        request_instance=request_instance,
        actor=actor,
        event="cancelled",
        previous_status=previous_status,
        new_status=request_instance.status,
        previous_area=previous_area,
        new_area=request_instance.current_responsible_area,
        comment=reason,
        source="api",
    )

    return request_instance


@transaction.atomic
def close_repair_part_request(
    *,
    request_instance,
    actor,
    observations="",
):
    pending_items = request_instance.items.filter(
        archived_at__isnull=True,
    ).exclude(
        status__in={
            RepairPartRequestItem.Status.COMPLETED,
            RepairPartRequestItem.Status.REJECTED,
            RepairPartRequestItem.Status.CANCELLED,
        }
    )

    if pending_items.exists():
        raise ValidationError(
            "No puedes cerrar la solicitud mientras existan ítems pendientes."
        )

    previous_status = request_instance.status
    previous_area = request_instance.current_responsible_area

    request_instance.status = RepairPartRequest.Status.CLOSED
    request_instance.current_responsible_area = (
        RepairPartRequest.ResponsibleArea.CLOSED
    )
    request_instance.closed_by = actor
    request_instance.closed_at = timezone.now()
    request_instance.general_observations = (
        f"{request_instance.general_observations}\n{observations}".strip()
    )
    request_instance.updated_by = actor
    request_instance.save(
        update_fields=[
            "status",
            "current_responsible_area",
            "closed_by",
            "closed_at",
            "general_observations",
            "updated_by",
            "updated_at",
        ]
    )

    create_part_request_history(
        request_instance=request_instance,
        actor=actor,
        event="closed",
        previous_status=previous_status,
        new_status=request_instance.status,
        previous_area=previous_area,
        new_area=request_instance.current_responsible_area,
        comment=observations,
        source="api",
    )

    return request_instance


def archive_repair_part_request(
    *,
    request_instance,
    actor,
    reason,
):
    if request_instance.status not in {
        RepairPartRequest.Status.DRAFT,
        RepairPartRequest.Status.CANCELLED,
        RepairPartRequest.Status.CLOSED,
    }:
        raise ValidationError(
            "Solo puedes archivar solicitudes en borrador, canceladas o cerradas."
        )

    request_instance.archive(
        user=actor,
        reason=reason,
    )
    return request_instance


def restore_repair_part_request(
    *,
    request_instance,
    actor,
):
    request_instance.restore(
        user=actor,
    )
    return request_instance
