# -*- coding: utf-8 -*-
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.services.models import ServicePartRequestNotification
from apps.services.serializers import (
    MarkServicePartRequestNotificationReadSerializer,
    ServicePartRequestNotificationSerializer,
)


class ServicePartRequestNotificationViewSet(
    viewsets.ModelViewSet
):
    queryset = ServicePartRequestNotification.objects.none()
    serializer_class = (
        ServicePartRequestNotificationSerializer
    )

    def get_queryset(self):
        queryset = (
            ServicePartRequestNotification.objects
            .select_related(
                "request",
                "request_item",
                "recipient",
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

        mine = str(
            self.request.query_params.get("mine", "")
        ).strip().lower()

        if (
            mine in {"1", "true", "yes"}
            and self.request.user.is_authenticated
        ):
            queryset = queryset.filter(
                recipient=self.request.user,
            )

        for query_name, field_name in (
            ("request", "request_id"),
            ("recipient", "recipient_id"),
            ("delivery_status", "delivery_status"),
            ("channel", "channel"),
            ("notification_type", "notification_type"),
        ):
            value = self.request.query_params.get(
                query_name
            )

            if value not in (None, ""):
                queryset = queryset.filter(
                    **{field_name: value}
                )

        return queryset.order_by(
            "-created_at",
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="mark-read",
    )
    def mark_read(self, request, pk=None):
        notification = self.get_object()

        if (
            request.user.is_authenticated
            and notification.recipient_id
            != request.user.id
            and not request.user.is_staff
        ):
            return Response(
                {
                    "detail": (
                        "No puede marcar como leída "
                        "una notificación de otro usuario."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = (
            MarkServicePartRequestNotificationReadSerializer(
                notification,
                data={},
                context=self.get_serializer_context(),
            )
        )
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()

        return Response(
            ServicePartRequestNotificationSerializer(
                notification,
                context=self.get_serializer_context(),
            ).data
        )
