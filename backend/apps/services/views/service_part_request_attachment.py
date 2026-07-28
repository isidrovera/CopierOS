# -*- coding: utf-8 -*-
from rest_framework import viewsets

from apps.services.models import ServicePartRequestAttachment
from apps.services.serializers import ServicePartRequestAttachmentSerializer


class ServicePartRequestAttachmentViewSet(viewsets.ModelViewSet):
    queryset = ServicePartRequestAttachment.objects.none()
    serializer_class = ServicePartRequestAttachmentSerializer

    def get_queryset(self):
        queryset = (
            ServicePartRequestAttachment.objects
            .select_related(
                "request",
                "request_item",
                "uploaded_by"
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
            "attachment_type"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                attachment_type=value,
            )

        return queryset.order_by(
            "-created_at",
        )
