# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.services.models import EquipmentInstalledItem

from .workflow_common import FullCleanModelSerializerMixin


class EquipmentInstalledItemSerializer(
    FullCleanModelSerializerMixin,
    serializers.ModelSerializer,
):
    item_type_display = serializers.CharField(
        source="get_item_type_display",
        read_only=True,
        allow_blank=True,
    )
    origin_type_display = serializers.CharField(
        source="get_origin_type_display",
        read_only=True,
        allow_blank=True,
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
        allow_blank=True,
    )
    meter_type_display = serializers.CharField(
        source="get_meter_type_display",
        read_only=True,
        allow_blank=True,
    )
    equipment_display = serializers.CharField(
        source="equipment.serial_number",
        read_only=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = EquipmentInstalledItem
        fields = "__all__"
        read_only_fields = (

            "created_by",
            "updated_by",
            "archived_by",
            "archived_at",
            "archived_reason",
        )
