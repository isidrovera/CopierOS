# -*- coding: utf-8 -*-

from apps.monitoring.models import (
    MonitoringNotificationDelivery,
    MonitoringNotificationInstance,
    MonitoringNotificationRule,
    MonitoringReportExecution,
    MonitoringReportSchedule,
)
from apps.monitoring.serializers import (
    MonitoringNotificationDeliverySerializer,
    MonitoringNotificationInstanceSerializer,
    MonitoringNotificationRuleSerializer,
    MonitoringReportExecutionSerializer,
    MonitoringReportScheduleSerializer,
)
from .common import MonitoringAdminModelViewSet


class MonitoringNotificationRuleViewSet(
    MonitoringAdminModelViewSet
):
    queryset = MonitoringNotificationRule.objects.all()
    serializer_class = (
        MonitoringNotificationRuleSerializer
    )


class MonitoringNotificationInstanceViewSet(
    MonitoringAdminModelViewSet
):
    queryset = MonitoringNotificationInstance.objects.all()
    serializer_class = (
        MonitoringNotificationInstanceSerializer
    )


class MonitoringNotificationDeliveryViewSet(
    MonitoringAdminModelViewSet
):
    queryset = MonitoringNotificationDelivery.objects.all()
    serializer_class = (
        MonitoringNotificationDeliverySerializer
    )


class MonitoringReportScheduleViewSet(
    MonitoringAdminModelViewSet
):
    queryset = MonitoringReportSchedule.objects.all()
    serializer_class = (
        MonitoringReportScheduleSerializer
    )


class MonitoringReportExecutionViewSet(
    MonitoringAdminModelViewSet
):
    queryset = MonitoringReportExecution.objects.all()
    serializer_class = (
        MonitoringReportExecutionSerializer
    )
