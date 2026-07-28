# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.services.models import ServicePartRequestStatusHistory

from .workflow_common import FullCleanModelSerializerMixin


class ServicePartRequestStatusHistorySerializer(
    FullCleanModelSerializerMixin,
    serializers.ModelSerializer,
):
    status_display = serializers.CharField(
        source="get_new_status_display",
        read_only=True,
        allow_blank=True,
    )
    action_display = serializers.CharField(
        source="get_action_display",
        read_only=True,
        allow_blank=True,
    )
    responsible_area_display = serializers.CharField(
        source="get_responsible_area_display",
        read_only=True,
        allow_blank=True,
    )
    request_code = serializers.CharField(
        source="request.code",
        read_only=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServicePartRequestStatusHistory
        fields = "__all__"
        read_only_fields = (

            "created_by",
            "updated_by",
            "archived_by",
            "archived_at",
            "archived_reason",
        )
