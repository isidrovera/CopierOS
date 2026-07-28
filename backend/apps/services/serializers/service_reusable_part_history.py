# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.services.models import ServiceReusablePartHistory

from .workflow_common import FullCleanModelSerializerMixin


class ServiceReusablePartHistorySerializer(
    FullCleanModelSerializerMixin,
    serializers.ModelSerializer,
):
    event_display = serializers.CharField(
        source="get_event_display",
        read_only=True,
        allow_blank=True,
    )
    previous_status_display = serializers.CharField(
        source="get_previous_status_display",
        read_only=True,
        allow_blank=True,
    )
    new_status_display = serializers.CharField(
        source="get_new_status_display",
        read_only=True,
        allow_blank=True,
    )
    previous_condition_display = serializers.CharField(
        source="get_previous_condition_display",
        read_only=True,
        allow_blank=True,
    )
    new_condition_display = serializers.CharField(
        source="get_new_condition_display",
        read_only=True,
        allow_blank=True,
    )
    reusable_part_code = serializers.CharField(
        source="reusable_part.code",
        read_only=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServiceReusablePartHistory
        fields = "__all__"
        read_only_fields = (

            "created_by",
            "updated_by",
            "archived_by",
            "archived_at",
            "archived_reason",
        )
