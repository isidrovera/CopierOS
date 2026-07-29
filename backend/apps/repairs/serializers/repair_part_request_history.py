# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models.repair_part_request_history import RepairPartRequestHistory


class RepairPartRequestHistoryListSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="request.code",
        read_only=True,
    )
    changed_by_name = serializers.CharField(
        source="changed_by.full_name",
        read_only=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartRequestHistory
        fields = (
            "id",
            "request",
            "request_code",
            "item",
            "event",
            "previous_status",
            "new_status",
            "previous_area",
            "new_area",
            "changed_by",
            "changed_by_name",
            "changed_at",
            "comment",
            "source",
            "metadata",
            "is_archived",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class RepairPartRequestHistoryDetailSerializer(
    RepairPartRequestHistoryListSerializer
):
    pass
