# -*- coding: utf-8 -*-
from rest_framework import viewsets

from apps.services.models import ServiceInstallationItem
from apps.services.serializers import ServiceInstallationItemSerializer


class ServiceInstallationItemViewSet(viewsets.ModelViewSet):
    queryset = ServiceInstallationItem.objects.none()
    serializer_class = ServiceInstallationItemSerializer

    def get_queryset(self):
        queryset = (
            ServiceInstallationItem.objects
            .select_related(
                "service_order",
                "part_request_item",
                "transfer",
                "installed_by"
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
            "service_order"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                service_order_id=value,
            )

        value = self.request.query_params.get(
            "request_item"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                part_request_item_id=value,
            )

        value = self.request.query_params.get(
            "result"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                result=value,
            )

        return queryset.order_by(
            "created_at",
        )
