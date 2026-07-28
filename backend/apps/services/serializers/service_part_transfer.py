# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.services.models import ServicePartTransfer

from .workflow_common import FullCleanModelSerializerMixin


class ServicePartTransferSerializer(
    FullCleanModelSerializerMixin,
    serializers.ModelSerializer,
):
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
        allow_blank=True,
    )
    removal_condition_display = serializers.CharField(
        source="get_removal_condition_display",
        read_only=True,
        allow_blank=True,
    )
    reception_condition_display = serializers.CharField(
        source="get_reception_condition_display",
        read_only=True,
        allow_blank=True,
    )
    item_display_name = serializers.CharField(
        source="part_request_item.display_name",
        read_only=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServicePartTransfer
        fields = "__all__"
        read_only_fields = (

            "created_by",
            "updated_by",
            "archived_by",
            "archived_at",
            "archived_reason",
        )
