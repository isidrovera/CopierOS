# -*- coding: utf-8 -*-
from .repair_part_request import RepairPartRequest


def create_part_request_history(
    *,
    request_instance,
    actor=None,
    event,
    item=None,
    previous_status="",
    new_status="",
    previous_area="",
    new_area="",
    comment="",
    source="system",
    metadata=None,
):
    from ..models.repair_part_request_history import (
        RepairPartRequestHistory,
    )

    return RepairPartRequestHistory.objects.create(
        request=request_instance,
        item=item,
        event=event,
        previous_status=previous_status,
        new_status=new_status,
        previous_area=previous_area,
        new_area=new_area,
        changed_by=actor,
        comment=comment,
        source=source,
        metadata=metadata or {},
        created_by=actor,
        updated_by=actor,
    )
