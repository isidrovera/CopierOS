# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import RepairStatusHistory


class RepairStatusHistoryListSerializer(
    serializers.ModelSerializer
):
    repair_code = serializers.CharField(
        source="repair.code",
        read_only=True,
    )

    equipment_id = serializers.UUIDField(
        source="repair.equipment_id",
        read_only=True,
    )

    equipment_serial_number = serializers.CharField(
        source="repair.equipment.serial_number",
        read_only=True,
    )

    previous_status_name = serializers.CharField(
        source="get_previous_status_display",
        read_only=True,
        allow_null=True,
    )

    new_status_name = serializers.CharField(
        source="get_new_status_display",
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
        model = RepairStatusHistory

        fields = (
            "id",
            "repair",
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "previous_status",
            "previous_status_name",
            "new_status",
            "new_status_name",
            "changed_by",
            "changed_by_name",
            "changed_at",
            "previous_status_started_at",
            "duration_minutes",
            "reason",
            "observations",
            "changed_automatically",
            "source",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class RepairStatusHistoryDetailSerializer(
    serializers.ModelSerializer
):
    repair_code = serializers.CharField(
        source="repair.code",
        read_only=True,
    )

    equipment_id = serializers.UUIDField(
        source="repair.equipment_id",
        read_only=True,
    )

    equipment_serial_number = serializers.CharField(
        source="repair.equipment.serial_number",
        read_only=True,
    )

    previous_status_name = serializers.CharField(
        source="get_previous_status_display",
        read_only=True,
        allow_null=True,
    )

    new_status_name = serializers.CharField(
        source="get_new_status_display",
        read_only=True,
    )

    changed_by_name = serializers.CharField(
        source="changed_by.full_name",
        read_only=True,
        allow_null=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.full_name",
        read_only=True,
        allow_null=True,
    )

    updated_by_name = serializers.CharField(
        source="updated_by.full_name",
        read_only=True,
        allow_null=True,
    )

    archived_by_name = serializers.CharField(
        source="archived_by.full_name",
        read_only=True,
        allow_null=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairStatusHistory

        fields = (
            "id",
            "repair",
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "previous_status",
            "previous_status_name",
            "new_status",
            "new_status_name",
            "changed_by",
            "changed_by_name",
            "changed_at",
            "previous_status_started_at",
            "duration_minutes",
            "reason",
            "observations",
            "changed_automatically",
            "source",
            "is_archived",
            "archived_at",
            "archived_reason",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_by",
            "archived_by_name",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields