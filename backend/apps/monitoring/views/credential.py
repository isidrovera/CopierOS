# -*- coding: utf-8 -*-

from apps.monitoring.models import SNMPCredential
from apps.monitoring.serializers import (
    SNMPCredentialSerializer,
)
from .common import MonitoringAdminModelViewSet


class SNMPCredentialViewSet(
    MonitoringAdminModelViewSet
):
    queryset = (
        SNMPCredential.objects
        .select_related(
            "customer",
            "branch",
            "agent",
            "network",
        )
        .all()
    )
    serializer_class = SNMPCredentialSerializer
