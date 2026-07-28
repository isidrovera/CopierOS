# -*- coding: utf-8 -*-
from rest_framework import viewsets

from apps.services.models import ServicePartRequestDecision
from apps.services.serializers import ServicePartRequestDecisionSerializer


class ServicePartRequestDecisionViewSet(viewsets.ModelViewSet):
    queryset = ServicePartRequestDecision.objects.none()
    serializer_class = ServicePartRequestDecisionSerializer

    def get_queryset(self):
        queryset = (
            ServicePartRequestDecision.objects
            .select_related(
                "request",
                "request_item",
                "decided_by",
                "previous_decision"
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
            "decision"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                decision=value,
            )

        value = self.request.query_params.get(
            "is_final"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                is_final=value,
            )

        return queryset.order_by(
            "-created_at",
        )
