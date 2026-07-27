# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.services.models import (
    ServiceEvidence,
    ServiceMeterReading,
)


class ServiceEvidenceSerializer(serializers.ModelSerializer):
    stage_display = serializers.CharField(
        source="get_stage_display",
        read_only=True,
    )

    class Meta:
        model = ServiceEvidence
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        if user and not validated_data.get("captured_by"):
            validated_data["captured_by"] = user

        try:
            return super().create(validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                getattr(exc, "message_dict", {"detail": exc.messages})
            ) from exc


class ServiceMeterReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMeterReading
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "applied_to_equipment_history",
        )

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        try:
            return super().create(validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                getattr(exc, "message_dict", {"detail": exc.messages})
            ) from exc

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        validated_data["updated_by"] = user

        try:
            return super().update(instance, validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                getattr(exc, "message_dict", {"detail": exc.messages})
            ) from exc
