# -*- coding: utf-8 -*-
from rest_framework import serializers
from apps.monitoring.models import MonitoredDevice, DevicePollingState
from .common import MonitoringModelSerializer

class MonitoredDeviceSerializer(MonitoringModelSerializer):
    status_display=serializers.CharField(source="get_status_display",read_only=True)
    operational_status_display=serializers.CharField(source="get_operational_status_display",read_only=True)
    identification_status_display=serializers.CharField(source="get_identification_status_display",read_only=True)
    link_status_display=serializers.CharField(source="get_link_status_display",read_only=True)
    class Meta:
        model=MonitoredDevice; fields="__all__"
        read_only_fields=("id","code","device_key","identity_fingerprint","active_alert_count","critical_alert_count","current_total_meter","current_black_meter","current_color_meter","current_scan_meter","discovered_at","first_successful_snmp_at","last_seen_at","last_snmp_success_at","last_snmp_failure_at","last_inventory_at","last_snapshot_at","last_ip_change_at","last_firmware_change_at","consecutive_failure_count","last_error_message","created_at","updated_at","archived_at","archived_by","archive_reason")

class DevicePollingStateSerializer(MonitoringModelSerializer):
    class Meta: model=DevicePollingState; fields="__all__"
