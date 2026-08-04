# -*- coding: utf-8 -*-

from apps.monitoring.models import (
    AgentConfigurationVersion,
    MonitoringConfiguration,
    MonitoringDataRetentionPolicy,
    MonitoringIngestionBatch,
)
from apps.monitoring.serializers import (
    AgentConfigurationVersionSerializer,
    MonitoringConfigurationSerializer,
    MonitoringDataRetentionPolicySerializer,
    MonitoringIngestionBatchSerializer,
)
from .common import MonitoringAdminModelViewSet


class MonitoringConfigurationViewSet(
    MonitoringAdminModelViewSet
):
    queryset = MonitoringConfiguration.objects.all()
    serializer_class = MonitoringConfigurationSerializer


class AgentConfigurationVersionViewSet(
    MonitoringAdminModelViewSet
):
    queryset = AgentConfigurationVersion.objects.all()
    serializer_class = (
        AgentConfigurationVersionSerializer
    )


class MonitoringIngestionBatchViewSet(
    MonitoringAdminModelViewSet
):
    queryset = MonitoringIngestionBatch.objects.all()
    serializer_class = (
        MonitoringIngestionBatchSerializer
    )


class MonitoringDataRetentionPolicyViewSet(
    MonitoringAdminModelViewSet
):
    queryset = MonitoringDataRetentionPolicy.objects.all()
    serializer_class = (
        MonitoringDataRetentionPolicySerializer
    )
