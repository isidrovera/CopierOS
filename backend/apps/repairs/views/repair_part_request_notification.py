# -*- coding: utf-8 -*-
from django.utils import timezone
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models.repair_part_request_notification import (
    RepairPartRequestNotification,
)
from ..serializers.repair_part_request_notification import (
    RepairPartRequestNotificationDetailSerializer,
    RepairPartRequestNotificationListSerializer,
    RepairPartRequestNotificationMarkReadSerializer,
)
from .common import get_boolean_query_param


class RepairPartRequestNotificationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = (
        "request__code",
        "event",
        "title",
        "message",
    )
    ordering_fields = (
        "status",
        "sent_at",
        "delivered_at",
        "read_at",
        "created_at",
    )
    ordering = ("-created_at",)

    def get_queryset(self):
        queryset = (
            RepairPartRequestNotification.objects
            .select_related(
                "request",
                "item",
                "recipient",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .filter(recipient=self.request.user)
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
            "event": "event",
            "channel": "channel",
            "status": "status",
        }

        for query_param, field_name in filters_map.items():
            value = self.request.query_params.get(query_param)
            if value:
                queryset = queryset.filter(**{field_name: value})

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairPartRequestNotificationListSerializer
        return RepairPartRequestNotificationDetailSerializer

    @action(detail=True, methods=("post",), url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        serializer = RepairPartRequestNotificationMarkReadSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        notification.status = notification.Status.READ
        notification.read_at = timezone.now()
        notification.updated_by = request.user
        notification.save(
            update_fields=[
                "status",
                "read_at",
                "updated_by",
                "updated_at",
            ]
        )

        return Response(
            RepairPartRequestNotificationDetailSerializer(
                notification,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )
