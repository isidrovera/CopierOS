# -*- coding: utf-8 -*-
from rest_framework import viewsets

from apps.services.models import ServicePartStockReview
from apps.services.serializers import ServicePartStockReviewSerializer


class ServicePartStockReviewViewSet(viewsets.ModelViewSet):
    queryset = ServicePartStockReview.objects.none()
    serializer_class = ServicePartStockReviewSerializer

    def get_queryset(self):
        queryset = (
            ServicePartStockReview.objects
            .select_related(
                "request",
                "request_item",
                "reviewed_by",
                "reusable_part"
            )
        )

        include_archived = (
            self.request.query_params
            .get("include_archived", "")
            .strip()
            .lower()
            in {"1", "true", "yes"}
        )

        if not include_archived:
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        value = self.request.query_params.get(
            "request"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                request_id=value,
            )

        value = self.request.query_params.get(
            "request_item"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                request_item_id=value,
            )

        value = self.request.query_params.get(
            "status"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                status=value,
            )

        return queryset.order_by(
            "-created_at",
        )
