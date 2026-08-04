# -*- coding: utf-8 -*-
from apps.monitoring.models import MonitoringDiscovery, DiscoveryHost
from .common import MonitoringModelSerializer
class MonitoringDiscoverySerializer(MonitoringModelSerializer):
    class Meta: model=MonitoringDiscovery; fields="__all__"
class DiscoveryHostSerializer(MonitoringModelSerializer):
    class Meta: model=DiscoveryHost; fields="__all__"
