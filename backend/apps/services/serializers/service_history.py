# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.services.models import (
    ServiceAssignmentHistory,
    ServiceStatusHistory,
)


class ServiceAssignmentHistorySerializer(serializers.ModelSerializer):
    previous_technician_display = serializers.SerializerMethodField()
    new_technician_display = serializers.SerializerMethodField()
    assigned_by_display = serializers.SerializerMethodField()

    class Meta:
        model = ServiceAssignmentHistory
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

    @staticmethod
    def _user_display(user):
        if not user:
            return ""
        return user.get_full_name().strip() or user.get_username()

    def get_previous_technician_display(self, obj):
        return self._user_display(obj.previous_technician)

    def get_new_technician_display(self, obj):
        return self._user_display(obj.new_technician)

    def get_assigned_by_display(self, obj):
        return self._user_display(obj.assigned_by)


class ServiceStatusHistorySerializer(serializers.ModelSerializer):
    new_status_display = serializers.CharField(
        source="get_new_status_display",
        read_only=True,
    )
    changed_by_display = serializers.SerializerMethodField()

    class Meta:
        model = ServiceStatusHistory
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

    def get_changed_by_display(self, obj):
        if not obj.changed_by:
            return ""
        return (
            obj.changed_by.get_full_name().strip()
            or obj.changed_by.get_username()
        )
