# -*- coding: utf-8 -*-

from apps.monitoring.models import (
    DiscoveryHost,
    MonitoringDiscovery,
)
from apps.monitoring.serializers import (
    DiscoveryHostSerializer,
    MonitoringDiscoverySerializer,
)
from .common import MonitoringAdminModelViewSet


class MonitoringDiscoveryViewSet(
    MonitoringAdminModelViewSet
):
    queryset = MonitoringDiscovery.objects.all()
    serializer_class = MonitoringDiscoverySerializer


class DiscoveryHostViewSet(
    MonitoringAdminModelViewSet
):
    queryset = DiscoveryHost.objects.all()
    serializer_class = DiscoveryHostSerializer
