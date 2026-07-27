# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.services.models import (
    ServiceTrackingPoint,
    ServiceTrackingSession,
)


class ServiceTrackingSessionSerializer(serializers.ModelSerializer):
    technician_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = ServiceTrackingSession
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "total_distance_meters",
            "moving_seconds",
            "stopped_seconds",
            "delay_seconds",
            "deviation_seconds",
        )

    def get_technician_display(self, obj):
        return (
            obj.technician.get_full_name().strip()
            or obj.technician.get_username()
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


class ServiceTrackingPointSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(
        source="get_event_type_display",
        read_only=True,
    )

    class Meta:
        model = ServiceTrackingPoint
        fields = "__all__"
        read_only_fields = (
            "server_received_at",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

    def validate(self, attrs):
        request = self.context.get("request")
        session = attrs.get("tracking_session")
        order = attrs.get("service_order")
        technician = attrs.get("technician")

        if session:
            attrs["service_order"] = session.service_order
            attrs["technician"] = session.technician

        if request and request.user and technician:
            if request.user != technician and not request.user.is_staff:
                raise serializers.ValidationError(
                    {"technician": "No puede enviar GPS de otro técnico."}
                )

        return attrs

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
