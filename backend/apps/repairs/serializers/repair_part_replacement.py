# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models.repair_part_replacement import RepairPartReplacement
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class RepairPartReplacementListSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="item.request.code",
        read_only=True,
    )
    replacement_type_name = serializers.CharField(
        source="get_replacement_type_display",
        read_only=True,
    )
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    source_equipment_code = serializers.CharField(
        source="source_equipment.internal_code",
        read_only=True,
        allow_null=True,
    )
    source_equipment_serial = serializers.CharField(
        source="source_equipment.serial_number",
        read_only=True,
        allow_null=True,
    )
    responsible_user_name = serializers.CharField(
        source="responsible_user.full_name",
        read_only=True,
        allow_null=True,
    )
    completed_by_name = serializers.CharField(
        source="completed_by.full_name",
        read_only=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartReplacement
        fields = (
            "id",
            "item",
            "request_code",
            "replacement_type",
            "replacement_type_name",
            "status",
            "status_name",
            "source_equipment",
            "source_equipment_code",
            "source_equipment_serial",
            "replacement_serial_number",
            "responsible_user",
            "responsible_user_name",
            "due_at",
            "received_at",
            "completed_at",
            "completed_by",
            "completed_by_name",
            "external_reference",
            "notes",
            "is_archived",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class RepairPartReplacementDetailSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="item.request.code",
        read_only=True,
    )
    replacement_type_name = serializers.CharField(
        source="get_replacement_type_display",
        read_only=True,
    )
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    source_equipment_code = serializers.CharField(
        source="source_equipment.internal_code",
        read_only=True,
        allow_null=True,
    )
    source_equipment_serial = serializers.CharField(
        source="source_equipment.serial_number",
        read_only=True,
        allow_null=True,
    )
    responsible_user_name = serializers.CharField(
        source="responsible_user.full_name",
        read_only=True,
        allow_null=True,
    )
    completed_by_name = serializers.CharField(
        source="completed_by.full_name",
        read_only=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartReplacement
        fields = (
            "id",
            "item",
            "request_code",
            "replacement_type",
            "replacement_type_name",
            "status",
            "status_name",
            "source_equipment",
            "source_equipment_code",
            "source_equipment_serial",
            "replacement_serial_number",
            "responsible_user",
            "responsible_user_name",
            "due_at",
            "received_at",
            "completed_at",
            "completed_by",
            "completed_by_name",
            "external_reference",
            "notes",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "is_archived",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "request_code",
            "replacement_type_name",
            "status_name",
            "source_equipment_code",
            "source_equipment_serial",
            "responsible_user_name",
            "received_at",
            "completed_at",
            "completed_by",
            "completed_by_name",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "is_archived",
            "created_at",
            "updated_at",
        )


class RepairPartReplacementCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairPartReplacement
        fields = (
            "item",
            "replacement_type",
            "status",
            "source_equipment",
            "replacement_serial_number",
            "responsible_user",
            "due_at",
            "external_reference",
            "notes",
        )

    def create(self, validated_data):
        actor = get_authenticated_user(self)
        instance = RepairPartReplacement(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            instance.save()
        except DjangoValidationError as exception:
            raise serializers.ValidationError(
                convert_django_validation_error(exception)
            ) from exception

        return instance

    def update(self, instance, validated_data):
        actor = get_authenticated_user(self)

        for field_name, value in validated_data.items():
            setattr(instance, field_name, value)

        if actor:
            instance.updated_by = actor

        try:
            instance.save()
        except DjangoValidationError as exception:
            raise serializers.ValidationError(
                convert_django_validation_error(exception)
            ) from exception

        return instance


class RepairPartReplacementCompleteSerializer(serializers.Serializer):
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )
