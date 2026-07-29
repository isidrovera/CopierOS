# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models.repair_part_request_review import RepairPartRequestReview
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class RepairPartRequestReviewListSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="item.request.code",
        read_only=True,
    )
    item_name = serializers.SerializerMethodField()
    result_name = serializers.CharField(
        source="get_result_display",
        read_only=True,
    )
    reviewed_by_name = serializers.CharField(
        source="reviewed_by.full_name",
        read_only=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartRequestReview
        fields = (
            "id",
            "item",
            "request_code",
            "item_name",
            "result",
            "result_name",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "proposed_quantity",
            "requires_management_approval",
            "requires_replacement",
            "is_current",
            "is_archived",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_item_name(self, obj):
        if obj.item.component_id:
            return obj.item.component.name
        return obj.item.custom_name


class RepairPartRequestReviewDetailSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="item.request.code",
        read_only=True,
    )
    reviewed_by_name = serializers.CharField(
        source="reviewed_by.full_name",
        read_only=True,
    )
    result_name = serializers.CharField(
        source="get_result_display",
        read_only=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartRequestReview
        fields = "__all__"
        read_only_fields = (
            "id",
            "reviewed_by",
            "reviewed_at",
            "is_current",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "created_at",
            "updated_at",
        )


class RepairPartRequestReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairPartRequestReview
        fields = (
            "item",
            "result",
            "justification",
            "requires_management_approval",
            "requires_replacement",
            "proposed_quantity",
        )

    def validate_item(self, value):
        if value.status not in {
            value.Status.PENDING_AREA_REVIEW,
            value.Status.SOURCE_EVALUATION,
            value.Status.INFORMATION_REQUESTED,
        }:
            raise serializers.ValidationError(
                "El ítem no está pendiente de revisión del jefe."
            )
        return value

    def create(self, validated_data):
        actor = get_authenticated_user(self)
        instance = RepairPartRequestReview(
            reviewed_by=actor,
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
