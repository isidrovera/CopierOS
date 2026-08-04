# -*- coding: utf-8 -*-

from apps.monitoring.models import (
    DevicePollingState,
    MonitoredDevice,
)
from apps.monitoring.serializers import (
    DevicePollingStateSerializer,
    MonitoredDeviceSerializer,
)
from .common import MonitoringAdminModelViewSet


class MonitoredDeviceViewSet(
    MonitoringAdminModelViewSet
):
    queryset = (
        MonitoredDevice.objects
        .select_related(
            "customer",
            "branch",
            "agent",
            "network",
            "snmp_credential",
            "equipment",
            "suggested_equipment",
        )
        .all()
    )
    serializer_class = MonitoredDeviceSerializer


class DevicePollingStateViewSet(
    MonitoringAdminModelViewSet
):
    queryset = (
        DevicePollingState.objects
        .select_related(
            "device",
        )
        .all()
    )
    serializer_class = DevicePollingStateSerializer
