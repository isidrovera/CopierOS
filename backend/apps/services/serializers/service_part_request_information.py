# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.services.models import ServicePartRequestInformation

from .workflow_common import FullCleanModelSerializerMixin


class ServicePartRequestInformationSerializer(
    FullCleanModelSerializerMixin,
    serializers.ModelSerializer,
):
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
        allow_blank=True,
    )
    requested_to_area_display = serializers.CharField(
        source="get_requested_to_area_display",
        read_only=True,
        allow_blank=True,
    )
    request_code = serializers.CharField(
        source="request.code",
        read_only=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServicePartRequestInformation
        fields = "__all__"
        read_only_fields = (

            "created_by",
            "updated_by",
            "archived_by",
            "archived_at",
            "archived_reason",
        )
