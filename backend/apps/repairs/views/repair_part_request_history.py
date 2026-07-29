# -*- coding: utf-8 -*-
from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from ..models.repair_part_request_history import RepairPartRequestHistory
from ..serializers.repair_part_request_history import (
    RepairPartRequestHistoryDetailSerializer,
    RepairPartRequestHistoryListSerializer,
)
from .common import get_boolean_query_param


class RepairPartRequestHistoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = (
        "request__code",
        "event",
        "comment",
        "source",
        "changed_by__first_name",
        "changed_by__last_name",
        "changed_by__email",
    )
    ordering_fields = (
        "changed_at",
        "event",
        "previous_status",
        "new_status",
        "created_at",
    )
    ordering = ("-changed_at",)

    def get_queryset(self):
        queryset = (
            RepairPartRequestHistory.objects
            .select_related(
                "request",
                "item",
                "changed_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
        )

        if not get_boolean_query_param(
            self.request,
            "include_archived",
            False,
        ):
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        filters_map = {
            "request": "request_id",
            "item": "item_id",
            "event": "event",
            "changed_by": "changed_by_id",
            "source": "source",
        }

        for query_param, field_name in filters_map.items():
            value = self.request.query_params.get(query_param)
            if value:
                queryset = queryset.filter(**{field_name: value})

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairPartRequestHistoryListSerializer
        return RepairPartRequestHistoryDetailSerializer
