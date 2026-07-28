# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.services.models import ServiceReusablePart

from .workflow_common import FullCleanModelSerializerMixin


class ServiceReusablePartSerializer(
    FullCleanModelSerializerMixin,
    serializers.ModelSerializer,
):
    condition_display = serializers.CharField(
        source="get_condition_display",
        read_only=True,
        allow_blank=True,
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
        allow_blank=True,
    )
    origin_type_display = serializers.CharField(
        source="get_origin_type_display",
        read_only=True,
        allow_blank=True,
    )
    component_name = serializers.CharField(
        source="component.name",
        read_only=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServiceReusablePart
        fields = "__all__"
        read_only_fields = (
            "code",
            "created_by",
            "updated_by",
            "archived_by",
            "archived_at",
            "archived_reason",
        )
