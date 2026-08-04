# -*- coding: utf-8 -*-
from apps.monitoring.models import MonitoringNotificationRule, MonitoringNotificationInstance, MonitoringNotificationDelivery, MonitoringReportSchedule, MonitoringReportExecution
from .common import MonitoringModelSerializer
class MonitoringNotificationRuleSerializer(MonitoringModelSerializer):
    class Meta: model=MonitoringNotificationRule; fields="__all__"
class MonitoringNotificationInstanceSerializer(MonitoringModelSerializer):
    class Meta: model=MonitoringNotificationInstance; fields="__all__"
class MonitoringNotificationDeliverySerializer(MonitoringModelSerializer):
    class Meta: model=MonitoringNotificationDelivery; fields="__all__"
class MonitoringReportScheduleSerializer(MonitoringModelSerializer):
    class Meta: model=MonitoringReportSchedule; fields="__all__"
class MonitoringReportExecutionSerializer(MonitoringModelSerializer):
    class Meta: model=MonitoringReportExecution; fields="__all__"
