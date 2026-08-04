from django.contrib import admin

from .models import (
    MonitoringAgent,
    MonitoringNetwork,
    SNMPCredential,
    MonitoredDevice,
    SNMPProfile,
    DeviceProfileAssignment,
    DeviceSnapshot,
    CounterReading,
    ConsumableReading,
    DeviceAlert,
    AgentCommand,
    AgentSync,
    MonitoringNotificationRule,
    MonitoringNotificationInstance,
    MonitoringReportSchedule,
)


admin.site.register(MonitoringAgent)
admin.site.register(MonitoringNetwork)
admin.site.register(SNMPCredential)
admin.site.register(MonitoredDevice)
admin.site.register(SNMPProfile)
admin.site.register(DeviceProfileAssignment)
admin.site.register(DeviceSnapshot)
admin.site.register(CounterReading)
admin.site.register(ConsumableReading)
admin.site.register(DeviceAlert)
admin.site.register(AgentCommand)
admin.site.register(AgentSync)
admin.site.register(MonitoringNotificationRule)
admin.site.register(MonitoringNotificationInstance)
admin.site.register(MonitoringReportSchedule)