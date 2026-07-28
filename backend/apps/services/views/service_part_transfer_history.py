# -*- coding: utf-8 -*-
from rest_framework import viewsets

from apps.services.models import ServicePartTransferHistory
from apps.services.serializers import ServicePartTransferHistorySerializer


class ServicePartTransferHistoryViewSet(viewsets.ModelViewSet):
    queryset = ServicePartTransferHistory.objects.none()
    serializer_class = ServicePartTransferHistorySerializer

    def get_queryset(self):
        queryset = (
            ServicePartTransferHistory.objects
            .select_related(
                "transfer",
                "performed_by",
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
            "transfer"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                transfer_id=value,
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
