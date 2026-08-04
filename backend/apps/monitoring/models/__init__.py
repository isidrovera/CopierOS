# -*- coding: utf-8 -*-
"""Modelos del módulo de monitoreo de Copier OS."""

# Base
from .base import MonitoringBaseModel

# Instalación, agentes y redes
from .installation_token import MonitoringInstallationToken
from .agent import MonitoringAgent
from .network import MonitoringNetwork
from .network_exclusion import MonitoringNetworkExclusion
from .snmp_credential import SNMPCredential

# Descubrimiento y dispositivos
from .discovery import MonitoringDiscovery
from .discovery_host import DiscoveryHost
from .monitored_device import MonitoredDevice

# Capturas y lecturas históricas
from .device_snapshot import DeviceSnapshot
from .counter_reading import CounterReading
from .consumable_reading import ConsumableReading
from .component_reading import ComponentReading
from .tray_reading import TrayReading
from .accessory_reading import AccessoryReading
from .device_alert import DeviceAlert
from .job_reading import JobReading
from .raw_oid_reading import RawOIDReading
from .device_event import DeviceEvent

# Perfiles SNMP y validación
from .snmp_profile import SNMPProfile
from .snmp_profile_metric import SNMPProfileMetric
from .device_profile_assignment import DeviceProfileAssignment
from .profile_test import SNMPProfileTest
from .profile_test_metric import SNMPProfileTestMetric

# Órdenes, sincronización y diagnóstico del agente
from .agent_command import AgentCommand
from .agent_command_log import AgentCommandLog
from .agent_sync import AgentSync
from .agent_log import AgentLog

# Notificaciones
from .notification_rule import MonitoringNotificationRule
from .notification_instance import MonitoringNotificationInstance
from .notification_delivery import MonitoringNotificationDelivery

# Reportes
from .report_schedule import MonitoringReportSchedule
from .report_execution import MonitoringReportExecution

# Configuración, planificación, recepción y retención
from .monitoring_configuration import MonitoringConfiguration
from .agent_configuration_version import AgentConfigurationVersion
from .device_polling_state import DevicePollingState
from .monitoring_ingestion_batch import MonitoringIngestionBatch
from .data_retention_policy import MonitoringDataRetentionPolicy


__all__ = [
    # Base
    "MonitoringBaseModel",

    # Instalación, agentes y redes
    "MonitoringInstallationToken",
    "MonitoringAgent",
    "MonitoringNetwork",
    "MonitoringNetworkExclusion",
    "SNMPCredential",

    # Descubrimiento y dispositivos
    "MonitoringDiscovery",
    "DiscoveryHost",
    "MonitoredDevice",

    # Capturas y lecturas
    "DeviceSnapshot",
    "CounterReading",
    "ConsumableReading",
    "ComponentReading",
    "TrayReading",
    "AccessoryReading",
    "DeviceAlert",
    "JobReading",
    "RawOIDReading",
    "DeviceEvent",

    # Perfiles SNMP
    "SNMPProfile",
    "SNMPProfileMetric",
    "DeviceProfileAssignment",
    "SNMPProfileTest",
    "SNMPProfileTestMetric",

    # Agente
    "AgentCommand",
    "AgentCommandLog",
    "AgentSync",
    "AgentLog",

    # Notificaciones
    "MonitoringNotificationRule",
    "MonitoringNotificationInstance",
    "MonitoringNotificationDelivery",

    # Reportes
    "MonitoringReportSchedule",
    "MonitoringReportExecution",

    # Configuración y procesamiento
    "MonitoringConfiguration",
    "AgentConfigurationVersion",
    "DevicePollingState",
    "MonitoringIngestionBatch",
    "MonitoringDataRetentionPolicy",
]
