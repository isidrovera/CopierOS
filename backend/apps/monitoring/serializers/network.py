# -*- coding: utf-8 -*-
import ipaddress
from rest_framework import serializers
from apps.monitoring.models import MonitoringNetwork, MonitoringNetworkExclusion
from .common import MonitoringModelSerializer

class MonitoringNetworkSerializer(MonitoringModelSerializer):
    class Meta:
        model=MonitoringNetwork; fields="__all__"
        read_only_fields=("id","scan_network_address","scan_broadcast_address","last_discovery_status","last_discovery_started_at","last_discovery_completed_at","last_discovery_error","last_scanned_host_count","last_responding_host_count","last_snmp_device_count","next_discovery_at","created_at","updated_at","archived_at","archived_by","archive_reason")
    def validate_cidr(self,value):
        try: return str(ipaddress.ip_network(value,strict=False))
        except ValueError as exc: raise serializers.ValidationError("La red CIDR no es válida.") from exc

class MonitoringNetworkExclusionSerializer(MonitoringModelSerializer):
    class Meta: model=MonitoringNetworkExclusion; fields="__all__"
