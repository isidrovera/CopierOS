# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError

from ..models.repair_part_request import RepairPartRequest


def archive_repair_part_request_item(
    *,
    item,
    actor,
    reason,
):
    if item.request.status != RepairPartRequest.Status.DRAFT:
        raise ValidationError(
            "Solo puedes archivar ítems de una solicitud en borrador."
        )

    item.archive(
        user=actor,
        reason=reason,
    )
    return item


def restore_repair_part_request_item(
    *,
    item,
    actor,
):
    if item.request.status != RepairPartRequest.Status.DRAFT:
        raise ValidationError(
            "Solo puedes restaurar ítems de una solicitud en borrador."
        )

    item.restore(
        user=actor,
    )
    return item
