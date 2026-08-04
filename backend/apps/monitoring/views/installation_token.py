# -*- coding: utf-8 -*-

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.monitoring.models import (
    MonitoringInstallationToken,
)
from apps.monitoring.serializers import (
    MonitoringInstallationTokenCreateSerializer,
    MonitoringInstallationTokenSerializer,
)
from .common import MonitoringAdminModelViewSet


class MonitoringInstallationTokenViewSet(
    MonitoringAdminModelViewSet
):
    queryset = (
        MonitoringInstallationToken.objects
        .select_related(
            "customer",
            "branch",
        )
        .all()
    )

    serializer_class = (
        MonitoringInstallationTokenSerializer
    )

    def get_serializer_class(self):
        if self.action == "create":
            return (
                MonitoringInstallationTokenCreateSerializer
            )

        return (
            MonitoringInstallationTokenSerializer
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="revoke",
    )
    def revoke_token(
        self,
        request,
        pk=None,
    ):
        token = self.get_object()

        reason = str(
            request.data.get(
                "reason",
                "",
            )
            or ""
        ).strip()

        token.revoke(
            reason=reason,
            user=request.user,
        )

        return Response(
            MonitoringInstallationTokenSerializer(
                token,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_200_OK,
        )
