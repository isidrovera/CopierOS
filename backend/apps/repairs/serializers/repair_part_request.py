# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models.repair_part_request import RepairPartRequest
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class RepairPartRequestListSerializer(serializers.ModelSerializer):
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
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    priority_name = serializers.CharField(
        source="get_priority_display",
        read_only=True,
    )
    responsible_area_name = serializers.CharField(
        source="get_current_responsible_area_display",
        read_only=True,
    )
    requested_by_name = serializers.CharField(
        source="requested_by.full_name",
        read_only=True,
    )
    current_responsible_user_name = serializers.CharField(
        source="current_responsible_user.full_name",
        read_only=True,
        allow_null=True,
    )
    total_items = serializers.IntegerField(
        source="items.count",
        read_only=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartRequest
        fields = (
            "id",
            "repair",
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "code",
            "title",
            "status",
            "status_name",
            "priority",
            "priority_name",
            "current_responsible_area",
            "responsible_area_name",
            "current_responsible_user",
            "current_responsible_user_name",
            "requested_by",
            "requested_by_name",
            "submitted_at",
            "approved_at",
            "rejected_at",
            "closed_at",
            "requires_management_approval",
            "has_pending_replacements",
            "total_items",
            "is_archived",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class RepairPartRequestDetailSerializer(serializers.ModelSerializer):
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
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    priority_name = serializers.CharField(
        source="get_priority_display",
        read_only=True,
    )
    responsible_area_name = serializers.CharField(
        source="get_current_responsible_area_display",
        read_only=True,
    )
    requested_by_name = serializers.CharField(
        source="requested_by.full_name",
        read_only=True,
    )
    current_responsible_user_name = serializers.CharField(
        source="current_responsible_user.full_name",
        read_only=True,
        allow_null=True,
    )
    submitted_by_name = serializers.CharField(
        source="submitted_by.full_name",
        read_only=True,
        allow_null=True,
    )
    approved_by_name = serializers.CharField(
        source="approved_by.full_name",
        read_only=True,
        allow_null=True,
    )
    rejected_by_name = serializers.CharField(
        source="rejected_by.full_name",
        read_only=True,
        allow_null=True,
    )
    closed_by_name = serializers.CharField(
        source="closed_by.full_name",
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
        model = RepairPartRequest
        fields = "__all__"
        read_only_fields = (
            "id",
            "code",
            "requested_by",
            "submitted_by",
            "submitted_at",
            "approved_by",
            "approved_at",
            "rejected_by",
            "rejected_at",
            "closed_by",
            "closed_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "created_at",
            "updated_at",
        )


class RepairPartRequestCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairPartRequest
        fields = (
            "id",
            "repair",
            "title",
            "description",
            "technical_justification",
            "general_observations",
            "priority",
            "requires_management_approval",
            "current_responsible_user",
        )
        read_only_fields = ("id",)

    def validate_repair(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes crear una solicitud en una reparación archivada."
            )
        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes crear una solicitud en una reparación inactiva."
            )
        return value

    def create(self, validated_data):
        actor = get_authenticated_user(self)
        instance = RepairPartRequest(
            requested_by=actor,
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
        if instance.status != RepairPartRequest.Status.DRAFT:
            raise serializers.ValidationError(
                "Solo puedes editar una solicitud en borrador."
            )

        actor = get_authenticated_user(self)

        for field_name, value in validated_data.items():
            setattr(instance, field_name, value)

        instance.updated_by = actor

        try:
            instance.save()
        except DjangoValidationError as exception:
            raise serializers.ValidationError(
                convert_django_validation_error(exception)
            ) from exception

        return instance


class RepairPartRequestSubmitSerializer(serializers.Serializer):
    observations = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class RepairPartRequestCancelSerializer(serializers.Serializer):
    reason = serializers.CharField()


class RepairPartRequestCloseSerializer(serializers.Serializer):
    observations = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class ArchiveRepairPartRequestSerializer(serializers.Serializer):
    reason = serializers.CharField()
