# -*- coding: utf-8 -*-

from apps.monitoring.models import (
    MonitoringNetwork,
    MonitoringNetworkExclusion,
)
from apps.monitoring.serializers import (
    MonitoringNetworkExclusionSerializer,
    MonitoringNetworkSerializer,
)
from .common import MonitoringAdminModelViewSet


class MonitoringNetworkViewSet(
    MonitoringAdminModelViewSet
):
    queryset = (
        MonitoringNetwork.objects
        .select_related(
            "agent",
        )
        .all()
    )
    serializer_class = MonitoringNetworkSerializer


class MonitoringNetworkExclusionViewSet(
    MonitoringAdminModelViewSet
):
    queryset = (
        MonitoringNetworkExclusion.objects
        .select_related(
            "network",
        )
        .all()
    )
    serializer_class = (
        MonitoringNetworkExclusionSerializer
    )
