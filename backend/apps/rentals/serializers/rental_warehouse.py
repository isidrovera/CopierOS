# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.rentals.models import RentalWarehouse


class RentalWarehouseSerializer(serializers.ModelSerializer):
    """
    Serializer principal de almacenes de alquiler de ANDES.
    """

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    archived_by_name = serializers.SerializerMethodField()

    equipment_count = serializers.SerializerMethodField()
    available_equipment_count = serializers.SerializerMethodField()
    preparation_equipment_count = serializers.SerializerMethodField()
    problem_equipment_count = serializers.SerializerMethodField()
    parts_equipment_count = serializers.SerializerMethodField()

    class Meta:
        model = RentalWarehouse
        fields = [
            "id",
            "code",
            "name",
            "address",
            "description",
            "is_active",
            "allows_entries",
            "allows_dispatches",
            "display_order",
            "notes",
            "equipment_count",
            "available_equipment_count",
            "preparation_equipment_count",
            "problem_equipment_count",
            "parts_equipment_count",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_at",
            "archived_by",
            "archived_by_name",
            "archived_reason",
            "is_archived",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        ]

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return ""

        return (
            obj.created_by.get_full_name()
            or obj.created_by.username
        )

    def get_updated_by_name(self, obj):
        if not obj.updated_by:
            return ""

        return (
            obj.updated_by.get_full_name()
            or obj.updated_by.username
        )

    def get_archived_by_name(self, obj):
        if not obj.archived_by:
            return ""

        return (
            obj.archived_by.get_full_name()
            or obj.archived_by.username
        )

    def get_equipment_count(self, obj):
        return obj.equipment.filter(
            archived_at__isnull=True,
        ).count()

    def get_available_equipment_count(self, obj):
        return obj.equipment.filter(
            archived_at__isnull=True,
            is_available_for_rental=True,
        ).count()

    def get_preparation_equipment_count(self, obj):
        return obj.equipment.filter(
            archived_at__isnull=True,
            operational_status__in=[
                "pending_preparation",
                "in_preparation",
            ],
        ).count()

    def get_problem_equipment_count(self, obj):
        return obj.equipment.filter(
            archived_at__isnull=True,
            operational_status="with_problems",
        ).count()

    def get_parts_equipment_count(self, obj):
        return obj.equipment.filter(
            archived_at__isnull=True,
            operational_status="for_parts",
        ).count()

    def validate_code(self, value):
        code = str(
            value or ""
        ).strip().upper()

        if not code:
            raise serializers.ValidationError(
                "El código del almacén es obligatorio."
            )

        queryset = RentalWarehouse.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un almacén registrado con este código."
            )

        return code

    def validate_name(self, value):
        name = str(
            value or ""
        ).strip()

        if not name:
            raise serializers.ValidationError(
                "El nombre del almacén es obligatorio."
            )

        queryset = RentalWarehouse.objects.filter(
            name__iexact=name,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un almacén registrado con este nombre."
            )

        return name

    def validate(self, attrs):
        is_active = attrs.get(
            "is_active",
            getattr(
                self.instance,
                "is_active",
                True,
            ),
        )

        allows_entries = attrs.get(
            "allows_entries",
            getattr(
                self.instance,
                "allows_entries",
                True,
            ),
        )

        allows_dispatches = attrs.get(
            "allows_dispatches",
            getattr(
                self.instance,
                "allows_dispatches",
                True,
            ),
        )

        if not is_active and (
            allows_entries or allows_dispatches
        ):
            attrs["allows_entries"] = False
            attrs["allows_dispatches"] = False

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(
            validated_data
        )

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["updated_by"] = user

        return super().update(
            instance,
            validated_data,
        )


class RentalWarehouseListSerializer(
    RentalWarehouseSerializer
):
    """
    Serializer compacto para listados de almacenes.
    """

    class Meta(RentalWarehouseSerializer.Meta):
        fields = [
            "id",
            "code",
            "name",
            "address",
            "is_active",
            "allows_entries",
            "allows_dispatches",
            "display_order",
            "equipment_count",
            "available_equipment_count",
            "preparation_equipment_count",
            "problem_equipment_count",
            "parts_equipment_count",
            "archived_at",
            "is_archived",
        ]