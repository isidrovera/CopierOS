# -*- coding: utf-8 -*-
from rest_framework import viewsets

from apps.services.models import ServicePartTransfer
from apps.services.serializers import ServicePartTransferSerializer


class ServicePartTransferViewSet(viewsets.ModelViewSet):
    queryset = ServicePartTransfer.objects.none()
    serializer_class = ServicePartTransferSerializer

    def get_queryset(self):
        queryset = (
            ServicePartTransfer.objects
            .select_related(
                "part_request_item",
                "reusable_part",
                "source_equipment",
                "destination_equipment",
                "removal_technician",
                "reception_technician",
                "current_holder"
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
            "request_item"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                part_request_item_id=value,
            )

        value = self.request.query_params.get(
            "status"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                status=value,
            )

        value = self.request.query_params.get(
            "removal_technician"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                removal_technician_id=value,
            )

        value = self.request.query_params.get(
            "reception_technician"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                reception_technician_id=value,
            )

        return queryset.order_by(
            "-created_at",
        )
