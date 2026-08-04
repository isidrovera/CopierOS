# -*- coding: utf-8 -*-

from apps.monitoring.models import (
    DeviceProfileAssignment,
    SNMPProfile,
    SNMPProfileMetric,
    SNMPProfileTest,
    SNMPProfileTestMetric,
)
from apps.monitoring.serializers import (
    DeviceProfileAssignmentSerializer,
    SNMPProfileMetricSerializer,
    SNMPProfileSerializer,
    SNMPProfileTestMetricSerializer,
    SNMPProfileTestSerializer,
)
from .common import MonitoringAdminModelViewSet


class SNMPProfileViewSet(
    MonitoringAdminModelViewSet
):
    queryset = SNMPProfile.objects.all()
    serializer_class = SNMPProfileSerializer


class SNMPProfileMetricViewSet(
    MonitoringAdminModelViewSet
):
    queryset = (
        SNMPProfileMetric.objects
        .select_related(
            "profile",
        )
        .all()
    )
    serializer_class = SNMPProfileMetricSerializer


class DeviceProfileAssignmentViewSet(
    MonitoringAdminModelViewSet
):
    queryset = (
        DeviceProfileAssignment.objects
        .select_related(
            "device",
            "profile",
            "customer",
            "branch",
            "agent",
        )
        .all()
    )
    serializer_class = (
        DeviceProfileAssignmentSerializer
    )


class SNMPProfileTestViewSet(
    MonitoringAdminModelViewSet
):
    queryset = SNMPProfileTest.objects.all()
    serializer_class = SNMPProfileTestSerializer


class SNMPProfileTestMetricViewSet(
    MonitoringAdminModelViewSet
):
    queryset = SNMPProfileTestMetric.objects.all()
    serializer_class = (
        SNMPProfileTestMetricSerializer
    )
