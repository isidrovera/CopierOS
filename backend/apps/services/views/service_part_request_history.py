# -*- coding: utf-8 -*-
from rest_framework import viewsets

from apps.services.models import ServicePartRequestStatusHistory
from apps.services.serializers import ServicePartRequestStatusHistorySerializer


class ServicePartRequestStatusHistoryViewSet(viewsets.ModelViewSet):
    queryset = ServicePartRequestStatusHistory.objects.none()
    serializer_class = ServicePartRequestStatusHistorySerializer

    def get_queryset(self):
        queryset = (
            ServicePartRequestStatusHistory.objects
            .select_related(
                "request",
                "changed_by"
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
            "action"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                action=value,
            )

        value = self.request.query_params.get(
            "new_status"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                new_status=value,
            )

        return queryset.order_by(
            "-created_at",
        )
