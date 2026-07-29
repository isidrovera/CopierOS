# -*- coding: utf-8 -*-
from rest_framework import filters, parsers, viewsets
from rest_framework.permissions import IsAuthenticated

from ..models.repair_part_request_attachment import (
    RepairPartRequestAttachment,
)
from ..serializers.repair_part_request_attachment import (
    RepairPartRequestAttachmentCreateSerializer,
    RepairPartRequestAttachmentDetailSerializer,
    RepairPartRequestAttachmentListSerializer,
)
from .common import get_boolean_query_param


class RepairPartRequestAttachmentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    parser_classes = (
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    )
    http_method_names = (
        "get",
        "post",
        "delete",
        "head",
        "options",
    )
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = (
        "request__code",
        "original_filename",
        "title",
        "description",
        "uploaded_by__first_name",
        "uploaded_by__last_name",
        "uploaded_by__email",
    )
    ordering_fields = (
        "attachment_type",
        "file_size",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)

    def get_queryset(self):
        queryset = (
            RepairPartRequestAttachment.objects
            .select_related(
                "request",
                "item",
                "uploaded_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
        )

        if not get_boolean_query_param(
            self.request,
            "include_archived",
            False,
        ):
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        filters_map = {
            "request": "request_id",
            "item": "item_id",
            "attachment_type": "attachment_type",
            "uploaded_by": "uploaded_by_id",
        }

        for query_param, field_name in filters_map.items():
            value = self.request.query_params.get(query_param)
            if value:
                queryset = queryset.filter(**{field_name: value})

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairPartRequestAttachmentListSerializer
        if self.action == "create":
            return RepairPartRequestAttachmentCreateSerializer
        return RepairPartRequestAttachmentDetailSerializer

    def perform_destroy(self, instance):
        instance.archive(
            user=self.request.user,
            reason="Adjunto archivado desde la API.",
        )
