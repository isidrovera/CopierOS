# -*- coding: utf-8 -*-
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from ..models.repair_part_request_comment import RepairPartRequestComment
from ..serializers.repair_part_request_comment import (
    RepairPartRequestCommentCreateSerializer,
    RepairPartRequestCommentDetailSerializer,
    RepairPartRequestCommentListSerializer,
)
from .common import get_boolean_query_param


class RepairPartRequestCommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
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
        "text",
        "author__first_name",
        "author__last_name",
        "author__email",
    )
    ordering_fields = (
        "comment_type",
        "is_internal",
        "created_at",
        "updated_at",
    )
    ordering = ("created_at",)

    def get_queryset(self):
        queryset = (
            RepairPartRequestComment.objects
            .select_related(
                "request",
                "item",
                "parent",
                "author",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .prefetch_related("mentioned_users")
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
            "author": "author_id",
            "comment_type": "comment_type",
            "is_internal": "is_internal",
        }

        for query_param, field_name in filters_map.items():
            value = self.request.query_params.get(query_param)
            if value is not None and value != "":
                queryset = queryset.filter(**{field_name: value})

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairPartRequestCommentListSerializer
        if self.action == "create":
            return RepairPartRequestCommentCreateSerializer
        return RepairPartRequestCommentDetailSerializer

    def perform_destroy(self, instance):
        instance.archive(
            user=self.request.user,
            reason="Comentario archivado desde la API.",
        )
