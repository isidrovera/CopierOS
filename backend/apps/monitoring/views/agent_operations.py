# -*- coding: utf-8 -*-

from apps.monitoring.models import (
    AgentCommand,
    AgentCommandLog,
    AgentLog,
    AgentSync,
    DeviceEvent,
)
from apps.monitoring.serializers import (
    AgentCommandLogSerializer,
    AgentCommandSerializer,
    AgentLogSerializer,
    AgentSyncSerializer,
    DeviceEventSerializer,
)
from .common import MonitoringAdminModelViewSet


class DeviceEventViewSet(
    MonitoringAdminModelViewSet
):
    queryset = DeviceEvent.objects.all()
    serializer_class = DeviceEventSerializer


class AgentCommandViewSet(
    MonitoringAdminModelViewSet
):
    queryset = AgentCommand.objects.all()
    serializer_class = AgentCommandSerializer


class AgentCommandLogViewSet(
    MonitoringAdminModelViewSet
):
    queryset = AgentCommandLog.objects.all()
    serializer_class = AgentCommandLogSerializer


class AgentSyncViewSet(
    MonitoringAdminModelViewSet
):
    queryset = AgentSync.objects.all()
    serializer_class = AgentSyncSerializer


class AgentLogViewSet(
    MonitoringAdminModelViewSet
):
    queryset = AgentLog.objects.all()
    serializer_class = AgentLogSerializer
