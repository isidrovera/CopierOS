# -*- coding: utf-8 -*-
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from ..models.repair_part_request_review import RepairPartRequestReview
from ..serializers.repair_part_request_review import (
    RepairPartRequestReviewCreateSerializer,
    RepairPartRequestReviewDetailSerializer,
    RepairPartRequestReviewListSerializer,
)
from .common import get_boolean_query_param


class RepairPartRequestReviewViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ("get", "post", "head", "options")
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = (
        "item__request__code",
        "item__component__name",
        "item__custom_name",
        "justification",
        "reviewed_by__first_name",
        "reviewed_by__last_name",
        "reviewed_by__email",
    )
    ordering_fields = (
        "reviewed_at",
        "result",
        "proposed_quantity",
        "created_at",
    )
    ordering = ("-reviewed_at",)

    def get_queryset(self):
        queryset = (
            RepairPartRequestReview.objects
            .select_related(
                "item",
                "item__request",
                "item__component",
                "reviewed_by",
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
            "item": "item_id",
            "request": "item__request_id",
            "result": "result",
            "reviewed_by": "reviewed_by_id",
            "is_current": "is_current",
        }

        for query_param, field_name in filters_map.items():
            value = self.request.query_params.get(query_param)
            if value is not None and value != "":
                queryset = queryset.filter(**{field_name: value})

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairPartRequestReviewListSerializer
        if self.action == "create":
            return RepairPartRequestReviewCreateSerializer
        return RepairPartRequestReviewDetailSerializer
