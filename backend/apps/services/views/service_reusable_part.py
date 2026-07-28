# -*- coding: utf-8 -*-
from rest_framework import viewsets

from apps.services.models import ServiceReusablePart
from apps.services.serializers import ServiceReusablePartSerializer


class ServiceReusablePartViewSet(viewsets.ModelViewSet):
    queryset = ServiceReusablePart.objects.none()
    serializer_class = ServiceReusablePartSerializer

    def get_queryset(self):
        queryset = (
            ServiceReusablePart.objects
            .select_related(
                "component",
                "source_equipment",
                "current_equipment",
                "evaluated_by",
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
            "status"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                status=value,
            )

        value = self.request.query_params.get(
            "condition"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                condition=value,
            )

        value = self.request.query_params.get(
            "component"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                component_id=value,
            )

        value = self.request.query_params.get(
            "source_equipment"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                source_equipment_id=value,
            )

        return queryset.order_by(
            "code",
        )
