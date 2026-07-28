# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.services.models import ServiceInstallationItem

from .workflow_common import FullCleanModelSerializerMixin


class ServiceInstallationItemSerializer(
    FullCleanModelSerializerMixin,
    serializers.ModelSerializer,
):
    result_display = serializers.CharField(
        source="get_result_display",
        read_only=True,
        allow_blank=True,
    )
    meter_type_display = serializers.CharField(
        source="get_meter_type_display",
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
        model = ServiceInstallationItem
        fields = "__all__"
        read_only_fields = (

            "created_by",
            "updated_by",
            "archived_by",
            "archived_at",
            "archived_reason",
        )
