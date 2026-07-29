# -*- coding: utf-8 -*-
from ..models.repair_part_request_notification import (
    RepairPartRequestNotification,
)


def create_part_request_notification(
    *,
    request_instance,
    recipient,
    event,
    title,
    message,
    actor=None,
    item=None,
    channel=RepairPartRequestNotification.Channel.IN_APP,
    payload=None,
):
    return RepairPartRequestNotification.objects.create(
        request=request_instance,
        item=item,
        recipient=recipient,
        event=event,
        channel=channel,
        title=title,
        message=message,
        payload=payload or {},
        created_by=actor,
        updated_by=actor,
    )
