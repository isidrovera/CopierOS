# -*- coding: utf-8 -*-

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.monitoring.permissions import (
    IsMonitoringAdministrator,
)
from apps.monitoring.serializers import (
    ArchiveActionSerializer,
)


class MonitoringAdminModelViewSet(ModelViewSet):
    """
    ViewSet base para mantenimiento administrativo.
    """

    permission_classes = [
        IsMonitoringAdministrator,
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        if hasattr(
            queryset.model,
            "archived_at",
        ):
            include_archived = (
                str(
                    self.request.query_params.get(
                        "include_archived",
                        "",
                    )
                ).lower()
                in {
                    "1",
                    "true",
                    "yes",
                    "si",
                    "sí",
                }
            )

            if not include_archived:
                queryset = queryset.filter(
                    archived_at__isnull=True,
                )

        return queryset

    @action(
        detail=True,
        methods=["post"],
        url_path="archive",
    )
    def archive_record(
        self,
        request,
        pk=None,
    ):
        instance = self.get_object()

        serializer = ArchiveActionSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        if not hasattr(
            instance,
            "archive",
        ):
            return Response(
                {
                    "detail": (
                        "Este registro no admite archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.archive(
            user=request.user,
            reason=serializer.validated_data.get(
                "reason",
                "",
            ),
        )

        return Response(
            self.get_serializer(
                instance
            ).data
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
    )
    def restore_record(
        self,
        request,
        pk=None,
    ):
        instance = self.get_object()

        if not hasattr(
            instance,
            "restore",
        ):
            return Response(
                {
                    "detail": (
                        "Este registro no admite restauración."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.restore(
            user=request.user,
        )

        return Response(
            self.get_serializer(
                instance
            ).data
        )
