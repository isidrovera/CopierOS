# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.services.models import ServicePartRequest

from .workflow_common import (
    FullCleanModelSerializerMixin,
    UserDisplayMixin,
)


class ServicePartRequestListSerializer(
    UserDisplayMixin,
    serializers.ModelSerializer,
):
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    current_responsible_area_display = serializers.CharField(
        source="get_current_responsible_area_display",
        read_only=True,
    )
    service_order_code = serializers.CharField(
        source="service_order.code",
        read_only=True,
    )
    installation_service_order_code = serializers.CharField(
        source="installation_service_order.code",
        read_only=True,
        allow_null=True,
    )
    requested_by_display = serializers.SerializerMethodField()
    current_responsible_user_display = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServicePartRequest
        fields = (
            "id",
            "code",
            "service_order",
            "service_order_code",
            "installation_service_order",
            "installation_service_order_code",
            "status",
            "status_display",
            "current_responsible_area",
            "current_responsible_area_display",
            "current_responsible_user",
            "current_responsible_user_display",
            "requested_by",
            "requested_by_display",
            "requested_at",
            "submitted_at",
            "item_count",
            "is_archived",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_requested_by_display(self, obj):
        return self.user_display(obj.requested_by)

    def get_current_responsible_user_display(self, obj):
        return self.user_display(obj.current_responsible_user)

    def get_item_count(self, obj):
        value = getattr(obj, "item_count", None)

        if value is not None:
            return value

        return obj.items.filter(
            archived_at__isnull=True,
        ).count()


class ServicePartRequestSerializer(
    FullCleanModelSerializerMixin,
    UserDisplayMixin,
    serializers.ModelSerializer,
):
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    current_responsible_area_display = serializers.CharField(
        source="get_current_responsible_area_display",
        read_only=True,
    )
    requested_by_display = serializers.SerializerMethodField()
    submitted_by_display = serializers.SerializerMethodField()
    management_reviewed_by_display = serializers.SerializerMethodField()
    stock_reviewed_by_display = serializers.SerializerMethodField()
    logistics_prepared_by_display = serializers.SerializerMethodField()
    current_responsible_user_display = serializers.SerializerMethodField()
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServicePartRequest
        fields = "__all__"
        read_only_fields = (
            "code",
            "requested_by",
            "submitted_by",
            "management_reviewed_by",
            "stock_reviewed_by",
            "logistics_prepared_by",
            "requested_at",
            "submitted_at",
            "management_reviewed_at",
            "information_requested_at",
            "information_answered_at",
            "stock_reviewed_at",
            "logistics_ready_at",
            "delivered_at",
            "closed_at",
            "created_by",
            "updated_by",
            "archived_by",
            "archived_at",
            "archived_reason",
        )

    def get_requested_by_display(self, obj):
        return self.user_display(obj.requested_by)

    def get_submitted_by_display(self, obj):
        return self.user_display(obj.submitted_by)

    def get_management_reviewed_by_display(self, obj):
        return self.user_display(obj.management_reviewed_by)

    def get_stock_reviewed_by_display(self, obj):
        return self.user_display(obj.stock_reviewed_by)

    def get_logistics_prepared_by_display(self, obj):
        return self.user_display(obj.logistics_prepared_by)

    def get_current_responsible_user_display(self, obj):
        return self.user_display(obj.current_responsible_user)

    def create(self, validated_data):
        user = self._authenticated_user()

        if user:
            validated_data["requested_by"] = user

        return super().create(validated_data)


class ServicePartRequestStatusChangeSerializer(
    serializers.Serializer
):
    status = serializers.ChoiceField(
        choices=ServicePartRequest.Status.choices,
    )
    current_responsible_area = serializers.ChoiceField(
        choices=ServicePartRequest.ResponsibleArea.choices,
        required=False,
    )
    current_responsible_user = serializers.PrimaryKeyRelatedField(
        queryset=(
            ServicePartRequest._meta
            .get_field("current_responsible_user")
            .remote_field.model.objects.all()
        ),
        required=False,
        allow_null=True,
    )
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class ArchiveServicePartRequestSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        max_length=500,
        allow_blank=False,
    )
