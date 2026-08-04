# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .base import MonitoringBaseModel


class MonitoringDataRetentionPolicy(MonitoringBaseModel):
    class Scope(models.TextChoices):
        GLOBAL = 'global', 'Global'
        CUSTOMER = 'customer', 'Cliente'
        BRANCH = 'branch', 'Sede'
        AGENT = 'agent', 'Agente'
        DEVICE = 'device', 'Dispositivo'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        ACTIVE = 'active', 'Activa'
        PAUSED = 'paused', 'Pausada'
        DISABLED = 'disabled', 'Deshabilitada'

    class Action(models.TextChoices):
        DELETE = 'delete', 'Eliminar'
        ARCHIVE = 'archive', 'Archivar'
        ANONYMIZE = 'anonymize', 'Anonimizar'
        COMPRESS = 'compress', 'Comprimir'
        KEEP = 'keep', 'Conservar'

    code = models.CharField(max_length=150, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scope = models.CharField(max_length=20, choices=Scope.choices, default=Scope.GLOBAL, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    priority = models.PositiveIntegerField(default=100, db_index=True)
    customer = models.ForeignKey('partners.Partner', null=True, blank=True, on_delete=models.PROTECT, related_name='monitoring_retention_policies')
    branch = models.ForeignKey('partners.PartnerBranch', null=True, blank=True, on_delete=models.PROTECT, related_name='monitoring_retention_policies')
    agent = models.ForeignKey('monitoring.MonitoringAgent', null=True, blank=True, on_delete=models.PROTECT, related_name='retention_policies')
    device = models.ForeignKey('monitoring.MonitoredDevice', null=True, blank=True, on_delete=models.PROTECT, related_name='retention_policies')
    snapshots_days = models.PositiveIntegerField(default=1095)
    counters_days = models.PositiveIntegerField(default=1825)
    consumables_days = models.PositiveIntegerField(default=1095)
    components_days = models.PositiveIntegerField(default=1095)
    trays_days = models.PositiveIntegerField(default=365)
    accessories_days = models.PositiveIntegerField(default=1095)
    alerts_days = models.PositiveIntegerField(default=1825)
    jobs_days = models.PositiveIntegerField(default=180)
    raw_oids_days = models.PositiveIntegerField(default=90)
    discoveries_days = models.PositiveIntegerField(default=365)
    events_days = models.PositiveIntegerField(default=1825)
    agent_syncs_days = models.PositiveIntegerField(default=365)
    agent_logs_days = models.PositiveIntegerField(default=180)
    command_logs_days = models.PositiveIntegerField(default=365)
    notification_instances_days = models.PositiveIntegerField(default=730)
    notification_deliveries_days = models.PositiveIntegerField(default=365)
    report_executions_days = models.PositiveIntegerField(default=730)
    ingestion_batches_days = models.PositiveIntegerField(default=180)
    profile_tests_days = models.PositiveIntegerField(default=365)
    historical_action = models.CharField(max_length=20, choices=Action.choices, default=Action.DELETE)
    raw_data_action = models.CharField(max_length=20, choices=Action.choices, default=Action.DELETE)
    job_data_action = models.CharField(max_length=20, choices=Action.choices, default=Action.ANONYMIZE)
    preserve_records_with_open_alerts = models.BooleanField(default=True)
    preserve_acknowledged_events = models.BooleanField(default=True)
    preserve_manual_records = models.BooleanField(default=True)
    preserve_report_files = models.BooleanField(default=True)
    legal_hold = models.BooleanField(default=False, db_index=True)
    legal_hold_reason = models.TextField(blank=True)
    run_interval_hours = models.PositiveIntegerField(default=24)
    batch_size = models.PositiveIntegerField(default=1000)
    dry_run = models.BooleanField(default=False)
    last_run_at = models.DateTimeField(null=True, blank=True, db_index=True)
    next_run_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_failure_at = models.DateTimeField(null=True, blank=True)
    deleted_record_count = models.PositiveBigIntegerField(default=0)
    archived_record_count = models.PositiveBigIntegerField(default=0)
    anonymized_record_count = models.PositiveBigIntegerField(default=0)
    last_error_message = models.TextField(blank=True)
    retention_options = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='created_monitoring_retention_policies')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ('priority', 'name')
        indexes = [
            models.Index(fields=['status', 'next_run_at', 'priority'], name='mon_retention_next_idx'),
            models.Index(fields=['customer', 'scope', 'status'], name='mon_retention_customer_idx'),
            models.Index(fields=['agent', 'status'], name='mon_retention_agent_idx'),
            models.Index(fields=['legal_hold', 'status'], name='mon_retention_hold_idx'),
        ]
        constraints = [models.UniqueConstraint(fields=['scope', 'customer', 'branch', 'agent', 'device'], condition=Q(status='active', archived_at__isnull=True), name='unique_active_retention_policy')]

    def __str__(self):
        return f'{self.code} - {self.name}'

    def get_cutoff(self, field_name, reference_at=None):
        return (reference_at or timezone.now()) - timezone.timedelta(days=getattr(self, field_name))

    def calculate_next_run(self, reference_at=None):
        if self.status != self.Status.ACTIVE:
            return None
        return (reference_at or timezone.now()) + timezone.timedelta(hours=self.run_interval_hours)

    def register_result(self, *, deleted=0, archived=0, anonymized=0, successful=True, error_message=''):
        now = timezone.now()
        self.last_run_at = now
        if successful:
            self.deleted_record_count += max(int(deleted or 0), 0)
            self.archived_record_count += max(int(archived or 0), 0)
            self.anonymized_record_count += max(int(anonymized or 0), 0)
            self.last_success_at = now
            self.last_error_message = ''
        else:
            self.last_failure_at = now
            self.last_error_message = str(error_message or '').strip()
        self.next_run_at = self.calculate_next_run(now)
        self.save()

    def applies_to(self, *, customer=None, branch=None, agent=None, device=None):
        mapping = {
            self.Scope.GLOBAL: True,
            self.Scope.CUSTOMER: customer is not None and self.customer_id == customer.id,
            self.Scope.BRANCH: branch is not None and self.branch_id == branch.id,
            self.Scope.AGENT: agent is not None and self.agent_id == agent.id,
            self.Scope.DEVICE: device is not None and self.device_id == device.id,
        }
        return bool(mapping.get(self.scope))

    def clean(self):
        super().clean()
        self.code = str(self.code or '').strip().upper()
        self.name = str(self.name or '').strip()
        self.legal_hold_reason = str(self.legal_hold_reason or '').strip()
        self.last_error_message = str(self.last_error_message or '').strip()
        if not self.code:
            raise ValidationError({'code': 'El código es obligatorio.'})
        if not self.name:
            raise ValidationError({'name': 'El nombre es obligatorio.'})
        required = {self.Scope.GLOBAL: None, self.Scope.CUSTOMER: 'customer', self.Scope.BRANCH: 'branch', self.Scope.AGENT: 'agent', self.Scope.DEVICE: 'device'}[self.scope]
        if required and not getattr(self, f'{required}_id'):
            raise ValidationError({required: 'Este campo es obligatorio para el alcance.'})
        if self.branch_id and self.branch.partner_id != self.customer_id:
            raise ValidationError({'branch': 'La sede no pertenece al cliente.'})
        if self.agent_id and self.customer_id and self.agent.customer_id != self.customer_id:
            raise ValidationError({'agent': 'El agente no pertenece al cliente.'})
        if self.device_id:
            if self.customer_id and self.device.customer_id != self.customer_id:
                raise ValidationError({'device': 'El dispositivo no pertenece al cliente.'})
            if self.agent_id and self.device.agent_id != self.agent_id:
                raise ValidationError({'device': 'El dispositivo no pertenece al agente.'})
        if self.legal_hold and not self.legal_hold_reason:
            raise ValidationError({'legal_hold_reason': 'Debe indicar el motivo.'})
        for field in ('snapshots_days', 'counters_days', 'consumables_days', 'components_days', 'trays_days', 'accessories_days', 'alerts_days', 'jobs_days', 'raw_oids_days', 'discoveries_days', 'events_days', 'agent_syncs_days', 'agent_logs_days', 'command_logs_days', 'notification_instances_days', 'notification_deliveries_days', 'report_executions_days', 'ingestion_batches_days', 'profile_tests_days'):
            if getattr(self, field) < 1:
                raise ValidationError({field: 'La retención mínima es un día.'})
        if self.run_interval_hours < 1:
            raise ValidationError({'run_interval_hours': 'Debe ser mayor que cero.'})
        if self.batch_size < 1:
            raise ValidationError({'batch_size': 'Debe ser mayor que cero.'})
        if not isinstance(self.retention_options, dict):
            raise ValidationError({'retention_options': 'Debe ser un objeto.'})

    def save(self, *args, **kwargs):
        self.code = str(self.code or '').strip().upper()
        if self.status == self.Status.ACTIVE and self.next_run_at is None:
            self.next_run_at = self.calculate_next_run()
        self.full_clean()
        return super().save(*args, **kwargs)
