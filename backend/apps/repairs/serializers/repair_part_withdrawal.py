# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models.repair_part_withdrawal import RepairPartWithdrawal
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class RepairPartWithdrawalListSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="item.request.code",
        read_only=True,
    )
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    authorized_person_name = serializers.CharField(
        source="authorized_person.full_name",
        read_only=True,
        allow_null=True,
    )
    authorized_by_name = serializers.CharField(
        source="authorized_by.full_name",
        read_only=True,
        allow_null=True,
    )
    withdrawn_by_name = serializers.CharField(
        source="withdrawn_by.full_name",
        read_only=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartWithdrawal
        fields = (
            "id",
            "item",
            "request_code",
            "source",
            "status",
            "status_name",
            "authorized_person",
            "authorized_person_name",
            "authorized_by",
            "authorized_by_name",
            "authorized_at",
            "valid_until",
            "withdrawn_by",
            "withdrawn_by_name",
            "withdrawn_at",
            "received_by",
            "received_at",
            "quantity",
            "is_archived",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class RepairPartWithdrawalDetailSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartWithdrawal
        fields = "__all__"
        read_only_fields = (
            "id",
            "authorized_by",
            "authorized_at",
            "withdrawn_by",
            "withdrawn_at",
            "received_by",
            "received_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "created_at",
            "updated_at",
        )


class RepairPartWithdrawalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairPartWithdrawal
        fields = (
            "item",
            "source",
            "quantity",
            "authorization_notes",
        )

    def create(self, validated_data):
        actor = get_authenticated_user(self)
        instance = RepairPartWithdrawal(
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


class RepairPartWithdrawalAuthorizeSerializer(serializers.Serializer):
    authorized_person = serializers.PrimaryKeyRelatedField(
        queryset=__import__(
            "django.contrib.auth",
            fromlist=["get_user_model"],
        ).get_user_model().objects.all()
    )
    valid_until = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class RepairPartWithdrawalConfirmSerializer(serializers.Serializer):
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class RepairPartWithdrawalReceiveSerializer(serializers.Serializer):
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )
