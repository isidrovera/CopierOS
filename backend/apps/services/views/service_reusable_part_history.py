# -*- coding: utf-8 -*-
from rest_framework import viewsets

from apps.services.models import ServiceReusablePartHistory
from apps.services.serializers import ServiceReusablePartHistorySerializer


class ServiceReusablePartHistoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceReusablePartHistory.objects.none()
    serializer_class = ServiceReusablePartHistorySerializer

    def get_queryset(self):
        queryset = (
            ServiceReusablePartHistory.objects
            .select_related(
                "reusable_part",
                "performed_by",
                "previous_equipment",
                "new_equipment",
                "previous_holder",
                "new_holder"
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
            "reusable_part"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                reusable_part_id=value,
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
