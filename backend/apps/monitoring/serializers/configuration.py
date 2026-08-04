# -*- coding: utf-8 -*-
from apps.monitoring.models import MonitoringConfiguration, AgentConfigurationVersion, MonitoringIngestionBatch, MonitoringDataRetentionPolicy
from .common import MonitoringModelSerializer
class MonitoringConfigurationSerializer(MonitoringModelSerializer):
    class Meta: model=MonitoringConfiguration; fields="__all__"
class AgentConfigurationVersionSerializer(MonitoringModelSerializer):
    class Meta: model=AgentConfigurationVersion; fields="__all__"
class MonitoringIngestionBatchSerializer(MonitoringModelSerializer):
    class Meta: model=MonitoringIngestionBatch; fields="__all__"
class MonitoringDataRetentionPolicySerializer(MonitoringModelSerializer):
    class Meta: model=MonitoringDataRetentionPolicy; fields="__all__"
