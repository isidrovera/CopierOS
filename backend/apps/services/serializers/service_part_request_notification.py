# -*- coding: utf-8 -*-
from django.utils import timezone
from rest_framework import serializers

from apps.services.models import ServicePartRequestNotification

from .workflow_common import FullCleanModelSerializerMixin


class ServicePartRequestNotificationSerializer(
    FullCleanModelSerializerMixin,
    serializers.ModelSerializer,
):
    notification_type_display = serializers.CharField(
        source="get_notification_type_display",
        read_only=True,
    )
    channel_display = serializers.CharField(
        source="get_channel_display",
        read_only=True,
    )
    delivery_status_display = serializers.CharField(
        source="get_delivery_status_display",
        read_only=True,
    )
    request_code = serializers.CharField(
        source="request.code",
        read_only=True,
    )
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServicePartRequestNotification
        fields = "__all__"
        read_only_fields = (
            "sent_at",
            "delivered_at",
            "read_at",
            "failed_at",
            "retry_count",
            "created_by",
            "updated_by",
            "archived_by",
            "archived_at",
            "archived_reason",
        )


class MarkServicePartRequestNotificationReadSerializer(
    serializers.Serializer
):
    def update(self, instance, validated_data):
        if (
            instance.delivery_status
            != ServicePartRequestNotification.DeliveryStatus.READ
        ):
            instance.delivery_status = (
                ServicePartRequestNotification
                .DeliveryStatus
                .READ
            )
            instance.read_at = timezone.now()
            instance.save(
                update_fields=(
                    "delivery_status",
                    "read_at",
                    "delivered_at",
                    "sent_at",
                    "updated_at",
                )
            )

        return instance

    def create(self, validated_data):
        raise NotImplementedError
