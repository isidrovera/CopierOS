# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models.repair_part_request_item import RepairPartRequestItem
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class RepairPartRequestItemListSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="request.code",
        read_only=True,
    )
    repair_id = serializers.UUIDField(
        source="request.repair_id",
        read_only=True,
    )
    repair_code = serializers.CharField(
        source="request.repair.code",
        read_only=True,
    )
    component_name = serializers.CharField(
        source="component.name",
        read_only=True,
        allow_null=True,
    )
    component_code = serializers.CharField(
        source="component.code",
        read_only=True,
        allow_null=True,
    )
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    item_type_name = serializers.CharField(
        source="get_item_type_display",
        read_only=True,
    )
    approval_route_name = serializers.CharField(
        source="get_approval_route_display",
        read_only=True,
    )
    source_type_name = serializers.CharField(
        source="get_source_type_display",
        read_only=True,
    )
    control_type_name = serializers.CharField(
        source="get_control_type_display",
        read_only=True,
    )
    requested_by_name = serializers.CharField(
        source="requested_by.full_name",
        read_only=True,
    )
    display_name = serializers.SerializerMethodField()
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartRequestItem
        fields = (
            "id",
            "request",
            "request_code",
            "repair_id",
            "repair_code",
            "checklist_item",
            "component",
            "component_name",
            "component_code",
            "custom_name",
            "custom_code",
            "display_name",
            "item_type",
            "item_type_name",
            "request_origin",
            "approval_route",
            "approval_route_name",
            "status",
            "status_name",
            "urgency",
            "source_type",
            "source_type_name",
            "control_type",
            "control_type_name",
            "requested_quantity",
            "approved_quantity",
            "reserved_quantity",
            "delivered_quantity",
            "received_quantity",
            "installed_quantity",
            "returned_quantity",
            "requested_by",
            "requested_by_name",
            "requires_replacement",
            "requires_damaged_part_return",
            "is_archived",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_display_name(self, obj):
        if obj.component_id:
            return obj.component.name
        return obj.custom_name


class RepairPartRequestItemDetailSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="request.code",
        read_only=True,
    )
    repair_code = serializers.CharField(
        source="request.repair.code",
        read_only=True,
    )
    component_name = serializers.CharField(
        source="component.name",
        read_only=True,
        allow_null=True,
    )
    component_code = serializers.CharField(
        source="component.code",
        read_only=True,
        allow_null=True,
    )
    inventory_code = serializers.CharField(
        source="inventory.internal_code",
        read_only=True,
        allow_null=True,
    )
    inventory_serial = serializers.CharField(
        source="inventory.serial_number",
        read_only=True,
        allow_null=True,
    )
    donor_equipment_code = serializers.CharField(
        source="donor_equipment.internal_code",
        read_only=True,
        allow_null=True,
    )
    donor_equipment_serial = serializers.CharField(
        source="donor_equipment.serial_number",
        read_only=True,
        allow_null=True,
    )
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    item_type_name = serializers.CharField(
        source="get_item_type_display",
        read_only=True,
    )
    request_origin_name = serializers.CharField(
        source="get_request_origin_display",
        read_only=True,
    )
    approval_route_name = serializers.CharField(
        source="get_approval_route_display",
        read_only=True,
    )
    urgency_name = serializers.CharField(
        source="get_urgency_display",
        read_only=True,
    )
    source_type_name = serializers.CharField(
        source="get_source_type_display",
        read_only=True,
    )
    control_type_name = serializers.CharField(
        source="get_control_type_display",
        read_only=True,
    )
    requested_by_name = serializers.CharField(
        source="requested_by.full_name",
        read_only=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartRequestItem
        fields = "__all__"
        read_only_fields = (
            "id",
            "requested_by",
            "approved_quantity",
            "reserved_quantity",
            "delivered_quantity",
            "received_quantity",
            "installed_quantity",
            "returned_quantity",
            "requires_replacement",
            "requires_damaged_part_return",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "created_at",
            "updated_at",
        )


class RepairPartRequestItemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairPartRequestItem
        fields = (
            "id",
            "request",
            "checklist_item",
            "component",
            "item_type",
            "request_origin",
            "approval_route",
            "urgency",
            "control_type",
            "custom_name",
            "custom_code",
            "custom_description",
            "requested_quantity",
            "technical_reason",
        )
        read_only_fields = ("id",)

    def validate_request(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "La solicitud está archivada."
            )
        if value.status != value.Status.DRAFT:
            raise serializers.ValidationError(
                "Solo puedes agregar ítems a una solicitud en borrador."
            )
        return value

    def validate(self, attrs):
        request = attrs.get(
            "request",
            getattr(self.instance, "request", None),
        )
        checklist_item = attrs.get(
            "checklist_item",
            getattr(self.instance, "checklist_item", None),
        )

        if (
            checklist_item
            and request
            and checklist_item.checklist.repair_id != request.repair_id
        ):
            raise serializers.ValidationError(
                {
                    "checklist_item": (
                        "El ítem de checklist no pertenece a la reparación."
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        actor = get_authenticated_user(self)
        instance = RepairPartRequestItem(
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
        if instance.request.status != instance.request.Status.DRAFT:
            raise serializers.ValidationError(
                "Solo puedes editar ítems de una solicitud en borrador."
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


class ArchiveRepairPartRequestItemSerializer(serializers.Serializer):
    reason = serializers.CharField()
