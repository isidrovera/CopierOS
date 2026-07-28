# -*- coding: utf-8 -*-
from rest_framework import viewsets

from apps.services.models import ServicePartStockReviewHistory
from apps.services.serializers import ServicePartStockReviewHistorySerializer


class ServicePartStockReviewHistoryViewSet(viewsets.ModelViewSet):
    queryset = ServicePartStockReviewHistory.objects.none()
    serializer_class = ServicePartStockReviewHistorySerializer

    def get_queryset(self):
        queryset = (
            ServicePartStockReviewHistory.objects
            .select_related(
                "stock_review",
                "performed_by"
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
            "stock_review"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                stock_review_id=value,
            )

        value = self.request.query_params.get(
            "event"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                event=value,
            )

        return queryset.order_by(
            "-created_at",
        )
