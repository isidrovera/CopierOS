# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models.repair_part_request_notification import (
    RepairPartRequestNotification,
)


class RepairPartRequestNotificationListSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="request.code",
        read_only=True,
    )
    recipient_name = serializers.CharField(
        source="recipient.full_name",
        read_only=True,
    )
    channel_name = serializers.CharField(
        source="get_channel_display",
        read_only=True,
    )
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartRequestNotification
        fields = (
            "id",
            "request",
            "request_code",
            "item",
            "recipient",
            "recipient_name",
            "event",
            "channel",
            "channel_name",
            "status",
            "status_name",
            "title",
            "message",
            "sent_at",
            "delivered_at",
            "read_at",
            "failure_reason",
            "payload",
            "is_archived",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class RepairPartRequestNotificationDetailSerializer(
    RepairPartRequestNotificationListSerializer
):
    pass


class RepairPartRequestNotificationMarkReadSerializer(serializers.Serializer):
    pass
