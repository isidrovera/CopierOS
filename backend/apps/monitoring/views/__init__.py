# -*- coding: utf-8 -*-

from .installation_token import (
    MonitoringInstallationTokenViewSet,
)
from .agent import (
    MonitoringAgentAuthenticationTestAPIView,
    MonitoringAgentHeartbeatAPIView,
    MonitoringAgentRegistrationAPIView,
    MonitoringAgentViewSet,
)
from .configuration import (
    MonitoringAgentConfigurationAPIView,
)
from .network import (
    MonitoringNetworkExclusionViewSet,
    MonitoringNetworkViewSet,
)
from .credential import SNMPCredentialViewSet
from .device import (
    DevicePollingStateViewSet,
    MonitoredDeviceViewSet,
)
from .readings import (
    AccessoryReadingViewSet,
    ComponentReadingViewSet,
    ConsumableReadingViewSet,
    CounterReadingViewSet,
    DeviceAlertViewSet,
    DeviceSnapshotViewSet,
    JobReadingViewSet,
    RawOIDReadingViewSet,
    SnapshotIngestionAPIView,
    TrayReadingViewSet,
)
from .discovery import (
    DiscoveryHostViewSet,
    MonitoringDiscoveryViewSet,
)
from .profiles import (
    DeviceProfileAssignmentViewSet,
    SNMPProfileMetricViewSet,
    SNMPProfileTestMetricViewSet,
    SNMPProfileTestViewSet,
    SNMPProfileViewSet,
)
from .agent_operations import (
    AgentCommandLogViewSet,
    AgentCommandViewSet,
    AgentLogViewSet,
    AgentSyncViewSet,
    DeviceEventViewSet,
)
from .notifications import (
    MonitoringNotificationDeliveryViewSet,
    MonitoringNotificationInstanceViewSet,
    MonitoringNotificationRuleViewSet,
    MonitoringReportExecutionViewSet,
    MonitoringReportScheduleViewSet,
)
from .system import (
    AgentConfigurationVersionViewSet,
    MonitoringConfigurationViewSet,
    MonitoringDataRetentionPolicyViewSet,
    MonitoringIngestionBatchViewSet,
)


__all__ = [
    "MonitoringInstallationTokenViewSet",

    "MonitoringAgentViewSet",
    "MonitoringAgentRegistrationAPIView",
    "MonitoringAgentHeartbeatAPIView",
    "MonitoringAgentAuthenticationTestAPIView",
    "MonitoringAgentConfigurationAPIView",

    "MonitoringNetworkViewSet",
    "MonitoringNetworkExclusionViewSet",
    "SNMPCredentialViewSet",

    "MonitoredDeviceViewSet",
    "DevicePollingStateViewSet",

    "DeviceSnapshotViewSet",
    "CounterReadingViewSet",
    "ConsumableReadingViewSet",
    "ComponentReadingViewSet",
    "TrayReadingViewSet",
    "AccessoryReadingViewSet",
    "DeviceAlertViewSet",
    "JobReadingViewSet",
    "RawOIDReadingViewSet",
    "SnapshotIngestionAPIView",

    "MonitoringDiscoveryViewSet",
    "DiscoveryHostViewSet",

    "SNMPProfileViewSet",
    "SNMPProfileMetricViewSet",
    "DeviceProfileAssignmentViewSet",
    "SNMPProfileTestViewSet",
    "SNMPProfileTestMetricViewSet",

    "DeviceEventViewSet",
    "AgentCommandViewSet",
    "AgentCommandLogViewSet",
    "AgentSyncViewSet",
    "AgentLogViewSet",

    "MonitoringNotificationRuleViewSet",
    "MonitoringNotificationInstanceViewSet",
    "MonitoringNotificationDeliveryViewSet",
    "MonitoringReportScheduleViewSet",
    "MonitoringReportExecutionViewSet",

    "MonitoringConfigurationViewSet",
    "AgentConfigurationVersionViewSet",
    "MonitoringIngestionBatchViewSet",
    "MonitoringDataRetentionPolicyViewSet",
]
