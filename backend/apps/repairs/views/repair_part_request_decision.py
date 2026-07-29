# -*- coding: utf-8 -*-
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from ..models.repair_part_request_decision import RepairPartRequestDecision
from ..serializers.repair_part_request_decision import (
    RepairPartRequestDecisionCreateSerializer,
    RepairPartRequestDecisionDetailSerializer,
    RepairPartRequestDecisionListSerializer,
)
from .common import get_boolean_query_param


class RepairPartRequestDecisionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ("get", "post", "head", "options")
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = (
        "request__code",
        "request__repair__code",
        "reason",
        "information_required",
        "decided_by__first_name",
        "decided_by__last_name",
        "decided_by__email",
    )
    ordering_fields = (
        "decision",
        "decided_at",
        "approved_quantity",
        "created_at",
    )
    ordering = ("-decided_at",)

    def get_queryset(self):
        queryset = (
            RepairPartRequestDecision.objects
            .select_related(
                "request",
                "request__repair",
                "item",
                "decided_by",
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
            "decision": "decision",
            "decided_by": "decided_by_id",
            "is_final": "is_final",
        }

        for query_param, field_name in filters_map.items():
            value = self.request.query_params.get(query_param)
            if value is not None and value != "":
                queryset = queryset.filter(**{field_name: value})

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairPartRequestDecisionListSerializer
        if self.action == "create":
            return RepairPartRequestDecisionCreateSerializer
        return RepairPartRequestDecisionDetailSerializer
