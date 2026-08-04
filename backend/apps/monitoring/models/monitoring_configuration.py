# -*- coding: utf-8 -*-
import hashlib
import json

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .base import MonitoringBaseModel


class MonitoringConfiguration(MonitoringBaseModel):
    class Scope(models.TextChoices):
        GLOBAL = 'global', 'Global'
        CUSTOMER = 'customer', 'Cliente'
        BRANCH = 'branch', 'Sede'
        AGENT = 'agent', 'Agente'
        NETWORK = 'network', 'Red'
        DEVICE = 'device', 'Dispositivo'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        ACTIVE = 'active', 'Activa'
        DISABLED = 'disabled', 'Deshabilitada'
        DEPRECATED = 'deprecated', 'Obsoleta'

    code = models.CharField(max_length=150, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scope = models.CharField(max_length=20, choices=Scope.choices, default=Scope.GLOBAL, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    priority = models.PositiveIntegerField(default=100, db_index=True)
    version = models.PositiveBigIntegerField(default=1, db_index=True)
    customer = models.ForeignKey('partners.Partner', null=True, blank=True, on_delete=models.PROTECT, related_name='monitoring_configurations')
    branch = models.ForeignKey('partners.PartnerBranch', null=True, blank=True, on_delete=models.PROTECT, related_name='monitoring_configurations')
    agent = models.ForeignKey('monitoring.MonitoringAgent', null=True, blank=True, on_delete=models.PROTECT, related_name='monitoring_configurations')
    network = models.ForeignKey('monitoring.MonitoringNetwork', null=True, blank=True, on_delete=models.PROTECT, related_name='monitoring_configurations')
    device = models.ForeignKey('monitoring.MonitoredDevice', null=True, blank=True, on_delete=models.PROTECT, related_name='monitoring_configurations')

    heartbeat_interval_seconds = models.PositiveIntegerField(default=300)
    full_sync_interval_seconds = models.PositiveIntegerField(default=900)
    configuration_refresh_interval_seconds = models.PositiveIntegerField(default=900)
    command_poll_interval_seconds = models.PositiveIntegerField(default=60)
    offline_threshold_seconds = models.PositiveIntegerField(default=900)
    discovery_enabled = models.BooleanField(default=True)
    discovery_interval_seconds = models.PositiveIntegerField(default=21600)
    discovery_timeout_seconds = models.PositiveIntegerField(default=2)
    discovery_worker_count = models.PositiveIntegerField(default=20)
    max_hosts_per_discovery = models.PositiveIntegerField(default=4096)
    counter_poll_interval_seconds = models.PositiveIntegerField(default=3600)
    consumable_poll_interval_seconds = models.PositiveIntegerField(default=1800)
    component_poll_interval_seconds = models.PositiveIntegerField(default=21600)
    alert_poll_interval_seconds = models.PositiveIntegerField(default=300)
    job_poll_interval_seconds = models.PositiveIntegerField(default=60)
    inventory_poll_interval_seconds = models.PositiveIntegerField(default=86400)
    raw_walk_interval_seconds = models.PositiveIntegerField(default=604800)
    snmp_timeout_seconds = models.PositiveIntegerField(default=5)
    snmp_retry_count = models.PositiveIntegerField(default=1)
    snmp_max_repetitions = models.PositiveIntegerField(default=25)
    max_concurrent_device_polls = models.PositiveIntegerField(default=10)
    ingestion_batch_size = models.PositiveIntegerField(default=100)
    max_upload_size_bytes = models.PositiveBigIntegerField(default=52428800)
    max_pending_local_items = models.PositiveBigIntegerField(default=100000)
    local_storage_limit_bytes = models.PositiveBigIntegerField(default=5368709120)
    compress_payloads = models.BooleanField(default=True)
    store_raw_oids = models.BooleanField(default=True)
    store_unknown_oids = models.BooleanField(default=True)
    store_unchanged_readings = models.BooleanField(default=True)
    allow_job_collection = models.BooleanField(default=False)
    anonymize_job_data = models.BooleanField(default=True)
    notification_evaluation_interval_seconds = models.PositiveIntegerField(default=300)
    report_scheduler_interval_seconds = models.PositiveIntegerField(default=300)
    business_timezone = models.CharField(max_length=100, default='America/Lima')
    respect_business_hours = models.BooleanField(default=True)
    business_hours = models.JSONField(default=dict, blank=True)
    holiday_calendar = models.JSONField(default=list, blank=True)
    agent_options = models.JSONField(default=dict, blank=True)
    discovery_options = models.JSONField(default=dict, blank=True)
    polling_options = models.JSONField(default=dict, blank=True)
    ingestion_options = models.JSONField(default=dict, blank=True)
    notification_options = models.JSONField(default=dict, blank=True)
    report_options = models.JSONField(default=dict, blank=True)
    checksum = models.CharField(max_length=64, blank=True, editable=False, db_index=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    deprecated_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='created_monitoring_configurations')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ('priority', '-version')
        indexes = [
            models.Index(fields=['status', 'scope', 'priority'], name='mon_config_scope_idx'),
            models.Index(fields=['customer', 'branch', 'status'], name='mon_config_customer_idx'),
            models.Index(fields=['agent', 'network', 'status'], name='mon_config_agent_idx'),
            models.Index(fields=['device', 'status', 'priority'], name='mon_config_device_idx'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['code', 'version', 'customer', 'branch', 'agent', 'network', 'device'], condition=Q(archived_at__isnull=True), name='unique_monitoring_config_version'),
            models.UniqueConstraint(fields=['scope', 'customer', 'branch', 'agent', 'network', 'device'], condition=Q(status='active', archived_at__isnull=True), name='unique_active_monitoring_config'),
        ]

    def __str__(self):
        return f'{self.code} v{self.version}'

    def as_payload(self):
        return {
            'code': self.code,
            'version': self.version,
            'scope': self.scope,
            'heartbeat_interval_seconds': self.heartbeat_interval_seconds,
            'full_sync_interval_seconds': self.full_sync_interval_seconds,
            'configuration_refresh_interval_seconds': self.configuration_refresh_interval_seconds,
            'command_poll_interval_seconds': self.command_poll_interval_seconds,
            'offline_threshold_seconds': self.offline_threshold_seconds,
            'discovery': {
                'enabled': self.discovery_enabled,
                'interval_seconds': self.discovery_interval_seconds,
                'timeout_seconds': self.discovery_timeout_seconds,
                'worker_count': self.discovery_worker_count,
                'max_hosts': self.max_hosts_per_discovery,
                **(self.discovery_options or {}),
            },
            'polling': {
                'counter_interval_seconds': self.counter_poll_interval_seconds,
                'consumable_interval_seconds': self.consumable_poll_interval_seconds,
                'component_interval_seconds': self.component_poll_interval_seconds,
                'alert_interval_seconds': self.alert_poll_interval_seconds,
                'job_interval_seconds': self.job_poll_interval_seconds,
                'inventory_interval_seconds': self.inventory_poll_interval_seconds,
                'raw_walk_interval_seconds': self.raw_walk_interval_seconds,
                'snmp_timeout_seconds': self.snmp_timeout_seconds,
                'snmp_retry_count': self.snmp_retry_count,
                'snmp_max_repetitions': self.snmp_max_repetitions,
                'max_concurrent_device_polls': self.max_concurrent_device_polls,
                **(self.polling_options or {}),
            },
            'ingestion': {
                'batch_size': self.ingestion_batch_size,
                'max_upload_size_bytes': self.max_upload_size_bytes,
                'max_pending_local_items': self.max_pending_local_items,
                'local_storage_limit_bytes': self.local_storage_limit_bytes,
                'compress_payloads': self.compress_payloads,
                **(self.ingestion_options or {}),
            },
            'privacy': {
                'store_raw_oids': self.store_raw_oids,
                'store_unknown_oids': self.store_unknown_oids,
                'store_unchanged_readings': self.store_unchanged_readings,
                'allow_job_collection': self.allow_job_collection,
                'anonymize_job_data': self.anonymize_job_data,
            },
            'business': {
                'timezone': self.business_timezone,
                'respect_business_hours': self.respect_business_hours,
                'hours': self.business_hours,
                'holidays': self.holiday_calendar,
            },
            'agent_options': self.agent_options,
            'notification_options': self.notification_options,
            'report_options': self.report_options,
        }

    def calculate_checksum(self):
        raw = json.dumps(self.as_payload(), sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def activate(self):
        self.status = self.Status.ACTIVE
        self.activated_at = timezone.now()
        self.deprecated_at = None
        self.save()

    def deprecate(self):
        self.status = self.Status.DEPRECATED
        self.deprecated_at = timezone.now()
        self.save()

    def applies_to(self, *, customer=None, branch=None, agent=None, network=None, device=None):
        mapping = {
            self.Scope.GLOBAL: True,
            self.Scope.CUSTOMER: customer is not None and self.customer_id == customer.id,
            self.Scope.BRANCH: branch is not None and self.branch_id == branch.id,
            self.Scope.AGENT: agent is not None and self.agent_id == agent.id,
            self.Scope.NETWORK: network is not None and self.network_id == network.id,
            self.Scope.DEVICE: device is not None and self.device_id == device.id,
        }
        return bool(mapping.get(self.scope))

    def clean(self):
        super().clean()
        self.code = str(self.code or '').strip().upper()
        self.name = str(self.name or '').strip()
        if not self.code:
            raise ValidationError({'code': 'El código es obligatorio.'})
        if not self.name:
            raise ValidationError({'name': 'El nombre es obligatorio.'})
        required = {self.Scope.GLOBAL: None, self.Scope.CUSTOMER: 'customer', self.Scope.BRANCH: 'branch', self.Scope.AGENT: 'agent', self.Scope.NETWORK: 'network', self.Scope.DEVICE: 'device'}[self.scope]
        if required and not getattr(self, f'{required}_id'):
            raise ValidationError({required: 'Este campo es obligatorio para el alcance.'})
        if self.branch_id and self.branch.partner_id != self.customer_id:
            raise ValidationError({'branch': 'La sede no pertenece al cliente.'})
        if self.agent_id and self.customer_id and self.agent.customer_id != self.customer_id:
            raise ValidationError({'agent': 'El agente no pertenece al cliente.'})
        if self.network_id and self.agent_id and self.network.agent_id != self.agent_id:
            raise ValidationError({'network': 'La red no pertenece al agente.'})
        if self.device_id:
            if self.customer_id and self.device.customer_id != self.customer_id:
                raise ValidationError({'device': 'El dispositivo no pertenece al cliente.'})
            if self.agent_id and self.device.agent_id != self.agent_id:
                raise ValidationError({'device': 'El dispositivo no pertenece al agente.'})
        for field in ('heartbeat_interval_seconds', 'full_sync_interval_seconds', 'configuration_refresh_interval_seconds', 'command_poll_interval_seconds', 'offline_threshold_seconds', 'discovery_interval_seconds', 'discovery_timeout_seconds', 'counter_poll_interval_seconds', 'consumable_poll_interval_seconds', 'component_poll_interval_seconds', 'alert_poll_interval_seconds', 'job_poll_interval_seconds', 'inventory_poll_interval_seconds', 'raw_walk_interval_seconds', 'snmp_timeout_seconds', 'notification_evaluation_interval_seconds', 'report_scheduler_interval_seconds'):
            if getattr(self, field) < 1:
                raise ValidationError({field: 'Debe ser mayor que cero.'})
        if self.max_concurrent_device_polls < 1:
            raise ValidationError({'max_concurrent_device_polls': 'Debe ser mayor que cero.'})
        if self.ingestion_batch_size < 1:
            raise ValidationError({'ingestion_batch_size': 'Debe ser mayor que cero.'})
        for field in ('business_hours', 'agent_options', 'discovery_options', 'polling_options', 'ingestion_options', 'notification_options', 'report_options'):
            if not isinstance(getattr(self, field), dict):
                raise ValidationError({field: 'Debe ser un objeto.'})
        if not isinstance(self.holiday_calendar, list):
            raise ValidationError({'holiday_calendar': 'Debe ser una lista.'})
        self.checksum = self.calculate_checksum()

    def save(self, *args, **kwargs):
        self.code = str(self.code or '').strip().upper()
        self.checksum = self.calculate_checksum()
        self.full_clean()
        return super().save(*args, **kwargs)
