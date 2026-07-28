# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.services.models import ServicePartRequestDecision

from .workflow_common import FullCleanModelSerializerMixin


class ServicePartRequestDecisionSerializer(
    FullCleanModelSerializerMixin,
    serializers.ModelSerializer,
):
    decision_display = serializers.CharField(
        source="get_decision_display",
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
        model = ServicePartRequestDecision
        fields = "__all__"
        read_only_fields = (

            "created_by",
            "updated_by",
            "archived_by",
            "archived_at",
            "archived_reason",
        )
