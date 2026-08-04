# -*- coding: utf-8 -*-
from apps.monitoring.models import DeviceEvent, AgentCommand, AgentCommandLog, AgentSync, AgentLog
from .common import MonitoringModelSerializer
class DeviceEventSerializer(MonitoringModelSerializer):
    class Meta: model=DeviceEvent; fields="__all__"
class AgentCommandSerializer(MonitoringModelSerializer):
    class Meta: model=AgentCommand; fields="__all__"
class AgentCommandLogSerializer(MonitoringModelSerializer):
    class Meta: model=AgentCommandLog; fields="__all__"
class AgentSyncSerializer(MonitoringModelSerializer):
    class Meta: model=AgentSync; fields="__all__"
class AgentLogSerializer(MonitoringModelSerializer):
    class Meta: model=AgentLog; fields="__all__"
