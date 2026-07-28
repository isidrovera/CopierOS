# -*- coding: utf-8 -*-
from rest_framework import viewsets

from apps.services.models import ServicePartRequestInformation
from apps.services.serializers import ServicePartRequestInformationSerializer


class ServicePartRequestInformationViewSet(viewsets.ModelViewSet):
    queryset = ServicePartRequestInformation.objects.none()
    serializer_class = ServicePartRequestInformationSerializer

    def get_queryset(self):
        queryset = (
            ServicePartRequestInformation.objects
            .select_related(
                "request",
                "requested_by",
                "requested_to_user",
                "answered_by",
                "closed_by"
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
            "status"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                status=value,
            )

        value = self.request.query_params.get(
            "requested_to_area"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                requested_to_area=value,
            )

        return queryset.order_by(
            "-created_at",
        )
