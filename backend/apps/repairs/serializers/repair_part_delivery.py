# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models.repair_part_delivery import RepairPartDelivery
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class RepairPartDeliveryListSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="item.request.code",
        read_only=True,
    )
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    prepared_by_name = serializers.CharField(
        source="prepared_by.full_name",
        read_only=True,
        allow_null=True,
    )
    delivered_by_name = serializers.CharField(
        source="delivered_by.full_name",
        read_only=True,
        allow_null=True,
    )
    delivered_to_name = serializers.CharField(
        source="delivered_to.full_name",
        read_only=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartDelivery
        fields = (
            "id",
            "item",
            "request_code",
            "status",
            "status_name",
            "prepared_by",
            "prepared_by_name",
            "prepared_at",
            "delivered_by",
            "delivered_by_name",
            "delivered_to",
            "delivered_to_name",
            "delivered_at",
            "confirmed_by",
            "confirmed_at",
            "quantity",
            "received_quantity",
            "delivery_document",
            "is_archived",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class RepairPartDeliveryDetailSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartDelivery
        fields = "__all__"
        read_only_fields = (
            "id",
            "prepared_by",
            "prepared_at",
            "delivered_by",
            "delivered_at",
            "confirmed_by",
            "confirmed_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "created_at",
            "updated_at",
        )


class RepairPartDeliveryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairPartDelivery
        fields = (
            "item",
            "quantity",
            "delivery_document",
            "notes",
        )

    def create(self, validated_data):
        actor = get_authenticated_user(self)
        instance = RepairPartDelivery(
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


class RepairPartDeliveryPrepareSerializer(serializers.Serializer):
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class RepairPartDeliveryDeliverSerializer(serializers.Serializer):
    delivered_to = serializers.PrimaryKeyRelatedField(
        queryset=__import__(
            "django.contrib.auth",
            fromlist=["get_user_model"],
        ).get_user_model().objects.all()
    )
    quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    delivery_document = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class RepairPartDeliveryReceiveSerializer(serializers.Serializer):
    received_quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )
