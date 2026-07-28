# -*- coding: utf-8 -*-
from rest_framework import viewsets

from apps.services.models import EquipmentInstalledItem
from apps.services.serializers import EquipmentInstalledItemSerializer


class EquipmentInstalledItemViewSet(viewsets.ModelViewSet):
    queryset = EquipmentInstalledItem.objects.none()
    serializer_class = EquipmentInstalledItemSerializer

    def get_queryset(self):
        queryset = (
            EquipmentInstalledItem.objects
            .select_related(
                "equipment",
                "service_order",
                "part_request",
                "part_request_item",
                "installation_item",
                "reusable_part",
                "component",
                "installed_by",
                "source_equipment",
                "previous_installation"
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
            "equipment"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                equipment_id=value,
            )

        value = self.request.query_params.get(
            "component"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                component_id=value,
            )

        value = self.request.query_params.get(
            "item_type"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                item_type=value,
            )

        value = self.request.query_params.get(
            "status"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                status=value,
            )

        return queryset.order_by(
            "-installed_at",
        )
