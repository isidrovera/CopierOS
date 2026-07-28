# -*- coding: utf-8 -*-
from rest_framework import viewsets

from apps.services.models import ServicePartRequestComment
from apps.services.serializers import ServicePartRequestCommentSerializer


class ServicePartRequestCommentViewSet(viewsets.ModelViewSet):
    queryset = ServicePartRequestComment.objects.none()
    serializer_class = ServicePartRequestCommentSerializer

    def get_queryset(self):
        queryset = (
            ServicePartRequestComment.objects
            .select_related(
                "request",
                "request_item",
                "author",
                "parent"
            )
        )

        queryset = queryset.prefetch_related(
            "mentioned_users",
            "replies",
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
            "comment_type"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                comment_type=value,
            )

        value = self.request.query_params.get(
            "author"
        )

        if value not in (None, ""):
            queryset = queryset.filter(
                author_id=value,
            )

        return queryset.order_by(
            "created_at",
        )
