# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.services.models import ServicePartStockReviewHistory

from .workflow_common import FullCleanModelSerializerMixin


class ServicePartStockReviewHistorySerializer(
    FullCleanModelSerializerMixin,
    serializers.ModelSerializer,
):
    event_display = serializers.CharField(
        source="get_event_display",
        read_only=True,
        allow_blank=True,
    )
    previous_status_display = serializers.CharField(
        source="get_previous_status_display",
        read_only=True,
        allow_blank=True,
    )
    new_status_display = serializers.CharField(
        source="get_new_status_display",
        read_only=True,
        allow_blank=True,
    )
    stock_review_display = serializers.CharField(
        source="stock_review.request_item.display_name",
        read_only=True,
        allow_null=True,
    )
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServicePartStockReviewHistory
        fields = "__all__"
        read_only_fields = (

            "created_by",
            "updated_by",
            "archived_by",
            "archived_at",
            "archived_reason",
        )
