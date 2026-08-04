# -*- coding: utf-8 -*-
from apps.monitoring.models import SNMPProfile, SNMPProfileMetric, DeviceProfileAssignment, SNMPProfileTest, SNMPProfileTestMetric
from .common import MonitoringModelSerializer
class SNMPProfileSerializer(MonitoringModelSerializer):
    class Meta: model=SNMPProfile; fields="__all__"
class SNMPProfileMetricSerializer(MonitoringModelSerializer):
    class Meta: model=SNMPProfileMetric; fields="__all__"
class DeviceProfileAssignmentSerializer(MonitoringModelSerializer):
    class Meta: model=DeviceProfileAssignment; fields="__all__"
class SNMPProfileTestSerializer(MonitoringModelSerializer):
    class Meta: model=SNMPProfileTest; fields="__all__"
class SNMPProfileTestMetricSerializer(MonitoringModelSerializer):
    class Meta: model=SNMPProfileTestMetric; fields="__all__"
