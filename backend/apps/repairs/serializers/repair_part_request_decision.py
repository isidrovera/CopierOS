# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models.repair_part_request_decision import RepairPartRequestDecision
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class RepairPartRequestDecisionListSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="request.code",
        read_only=True,
    )
    decision_name = serializers.CharField(
        source="get_decision_display",
        read_only=True,
    )
    decided_by_name = serializers.CharField(
        source="decided_by.full_name",
        read_only=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartRequestDecision
        fields = (
            "id",
            "request",
            "request_code",
            "item",
            "decision",
            "decision_name",
            "requested_quantity",
            "approved_quantity",
            "decided_by",
            "decided_by_name",
            "decided_at",
            "reason",
            "information_required",
            "is_final",
            "is_archived",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class RepairPartRequestDecisionDetailSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="request.code",
        read_only=True,
    )
    decision_name = serializers.CharField(
        source="get_decision_display",
        read_only=True,
    )
    decided_by_name = serializers.CharField(
        source="decided_by.full_name",
        read_only=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartRequestDecision
        fields = "__all__"
        read_only_fields = (
            "id",
            "decided_by",
            "decided_at",
            "previous_decision",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "created_at",
            "updated_at",
        )


class RepairPartRequestDecisionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairPartRequestDecision
        fields = (
            "request",
            "item",
            "decision",
            "requested_quantity",
            "approved_quantity",
            "reason",
            "information_required",
            "is_final",
        )

    def validate(self, attrs):
        request = attrs["request"]
        item = attrs.get("item")

        if item and item.request_id != request.id:
            raise serializers.ValidationError(
                {"item": "El ítem no pertenece a la solicitud."}
            )

        if item:
            attrs["requested_quantity"] = item.requested_quantity

        return attrs

    def create(self, validated_data):
        actor = get_authenticated_user(self)
        instance = RepairPartRequestDecision(
            decided_by=actor,
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
