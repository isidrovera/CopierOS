# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models.repair_part_source import RepairPartSource
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class RepairPartSourceListSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="item.request.code",
        read_only=True,
    )
    source_type_name = serializers.CharField(
        source="get_source_type_display",
        read_only=True,
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
    rental_warehouse_name = serializers.CharField(
        source="rental_warehouse.name",
        read_only=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartSource
        fields = (
            "id",
            "item",
            "request_code",
            "source_type",
            "source_type_name",
            "component_serial_number",
            "rental_warehouse",
            "rental_warehouse_name",
            "donor_equipment",
            "donor_equipment_code",
            "donor_equipment_serial",
            "donor_rental_equipment",
            "supplier_name",
            "purchase_reference",
            "available_quantity",
            "reserved_quantity",
            "warehouse_location",
            "justification",
            "is_confirmed",
            "is_archived",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class RepairPartSourceDetailSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="item.request.code",
        read_only=True,
    )
    source_type_name = serializers.CharField(
        source="get_source_type_display",
        read_only=True,
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
    rental_warehouse_name = serializers.CharField(
        source="rental_warehouse.name",
        read_only=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartSource
        fields = (
            "id",
            "item",
            "request_code",
            "source_type",
            "source_type_name",
            "component_serial_number",
            "rental_warehouse",
            "rental_warehouse_name",
            "donor_equipment",
            "donor_equipment_code",
            "donor_equipment_serial",
            "donor_rental_equipment",
            "supplier_name",
            "purchase_reference",
            "available_quantity",
            "reserved_quantity",
            "warehouse_location",
            "justification",
            "is_confirmed",
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
            "source_type_name",
            "donor_equipment_code",
            "donor_equipment_serial",
            "rental_warehouse_name",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "is_archived",
            "created_at",
            "updated_at",
        )


class RepairPartSourceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairPartSource
        fields = (
            "item",
            "source_type",
            "component_serial_number",
            "rental_warehouse",
            "donor_equipment",
            "donor_rental_equipment",
            "supplier_name",
            "purchase_reference",
            "available_quantity",
            "reserved_quantity",
            "warehouse_location",
            "justification",
            "is_confirmed",
        )

    def create(self, validated_data):
        actor = get_authenticated_user(self)
        instance = RepairPartSource(
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
