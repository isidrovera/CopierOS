# -*- coding: utf-8 -*-
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class DevicePollingState(MonitoringBaseModel):
    class PollType(models.TextChoices):
        IDENTITY = 'identity', 'Identidad'
        COUNTERS = 'counters', 'Contadores'
        CONSUMABLES = 'consumables', 'Consumibles'
        COMPONENTS = 'components', 'Componentes'
        TRAYS = 'trays', 'Bandejas'
        ACCESSORIES = 'accessories', 'Accesorios'
        ALERTS = 'alerts', 'Alertas'
        JOBS = 'jobs', 'Trabajos'
        INVENTORY = 'inventory', 'Inventario'
        RAW_WALK = 'raw_walk', 'WALK completo'
        PROFILE_VALIDATION = 'profile_validation', 'Validación de perfil'

    class Status(models.TextChoices):
        IDLE = 'idle', 'En espera'
        DUE = 'due', 'Pendiente'
        QUEUED = 'queued', 'En cola'
        RUNNING = 'running', 'En ejecución'
        BACKOFF = 'backoff', 'En espera por error'
        PAUSED = 'paused', 'Pausado'
        DISABLED = 'disabled', 'Deshabilitado'

    device = models.ForeignKey('monitoring.MonitoredDevice', on_delete=models.PROTECT, related_name='polling_states')
    agent = models.ForeignKey('monitoring.MonitoringAgent', on_delete=models.PROTECT, related_name='device_polling_states')
    customer = models.ForeignKey('partners.Partner', on_delete=models.PROTECT, related_name='monitoring_device_polling_states')
    branch = models.ForeignKey('partners.PartnerBranch', null=True, blank=True, on_delete=models.PROTECT, related_name='monitoring_device_polling_states')
    network = models.ForeignKey('monitoring.MonitoringNetwork', null=True, blank=True, on_delete=models.PROTECT, related_name='device_polling_states')
    profile_assignment = models.ForeignKey('monitoring.DeviceProfileAssignment', null=True, blank=True, on_delete=models.PROTECT, related_name='polling_states')
    last_command = models.ForeignKey('monitoring.AgentCommand', null=True, blank=True, on_delete=models.PROTECT, related_name='polling_states')
    poll_type = models.CharField(max_length=30, choices=PollType.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IDLE, db_index=True)
    interval_seconds = models.PositiveIntegerField(default=3600)
    priority = models.PositiveIntegerField(default=100, db_index=True)
    next_poll_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_scheduled_at = models.DateTimeField(null=True, blank=True)
    last_started_at = models.DateTimeField(null=True, blank=True)
    last_completed_at = models.DateTimeField(null=True, blank=True)
    last_success_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_failure_at = models.DateTimeField(null=True, blank=True)
    last_duration_ms = models.PositiveBigIntegerField(null=True, blank=True)
    average_duration_ms = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    successful_poll_count = models.PositiveBigIntegerField(default=0)
    failed_poll_count = models.PositiveBigIntegerField(default=0)
    consecutive_failure_count = models.PositiveIntegerField(default=0)
    maximum_consecutive_failures = models.PositiveIntegerField(default=5)
    backoff_seconds = models.PositiveIntegerField(default=60)
    maximum_backoff_seconds = models.PositiveIntegerField(default=3600)
    current_backoff_seconds = models.PositiveIntegerField(default=0)
    lock_token = models.UUIDField(null=True, blank=True, editable=False, db_index=True)
    lock_expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    queued_at = models.DateTimeField(null=True, blank=True)
    enabled = models.BooleanField(default=True, db_index=True)
    pause_reason = models.TextField(blank=True)
    last_error_code = models.CharField(max_length=150, blank=True, db_index=True)
    last_error_message = models.TextField(blank=True)
    state_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ('next_poll_at', 'priority')
        indexes = [
            models.Index(fields=['agent', 'status', 'next_poll_at', 'priority'], name='mon_poll_agent_queue_idx'),
            models.Index(fields=['device', 'poll_type', 'status'], name='mon_poll_device_type_idx'),
            models.Index(fields=['status', 'lock_expires_at'], name='mon_poll_lock_idx'),
        ]
        constraints = [models.UniqueConstraint(fields=['device', 'poll_type'], condition=models.Q(archived_at__isnull=True), name='unique_device_polling_type')]

    def __str__(self):
        return f'{self.device} - {self.get_poll_type_display()}'

    def is_due(self, now=None):
        now = now or timezone.now()
        if not self.enabled or self.status in {self.Status.PAUSED, self.Status.DISABLED}:
            return False
        if self.lock_expires_at and self.lock_expires_at > now:
            return False
        return self.next_poll_at <= now

    def schedule_next(self, reference_at=None):
        reference_at = reference_at or timezone.now()
        self.next_poll_at = reference_at + timezone.timedelta(seconds=self.interval_seconds)
        self.last_scheduled_at = reference_at
        if self.enabled:
            self.status = self.Status.IDLE

    def queue(self):
        if not self.is_due():
            raise ValidationError('La consulta no está disponible.')
        self.status = self.Status.QUEUED
        self.queued_at = timezone.now()
        self.save()

    def start(self, lock_seconds=600):
        if self.status not in {self.Status.DUE, self.Status.QUEUED, self.Status.IDLE, self.Status.BACKOFF}:
            raise ValidationError('La consulta no puede iniciarse.')
        if not self.enabled:
            raise ValidationError('La consulta está deshabilitada.')
        now = timezone.now()
        self.status = self.Status.RUNNING
        self.last_started_at = now
        self.lock_token = uuid.uuid4()
        self.lock_expires_at = now + timezone.timedelta(seconds=max(int(lock_seconds or 600), 30))
        self.save()
        return self.lock_token

    def validate_lock(self, lock_token):
        if not self.lock_token:
            raise ValidationError('No existe un bloqueo activo.')
        try:
            supplied = uuid.UUID(str(lock_token))
        except (TypeError, ValueError, AttributeError) as exc:
            raise ValidationError('El token no es válido.') from exc
        if supplied != self.lock_token:
            raise ValidationError('El token no coincide.')
        if self.lock_expires_at and self.lock_expires_at <= timezone.now():
            raise ValidationError('El bloqueo expiró.')

    def complete_success(self, *, lock_token, duration_ms=None, state_data=None):
        self.validate_lock(lock_token)
        now = timezone.now()
        self.successful_poll_count += 1
        self.consecutive_failure_count = 0
        self.current_backoff_seconds = 0
        self.last_completed_at = now
        self.last_success_at = now
        self.last_duration_ms = duration_ms
        self.last_error_code = ''
        self.last_error_message = ''
        self.lock_token = None
        self.lock_expires_at = None
        if state_data is not None:
            self.state_data = state_data
        if duration_ms is not None:
            total = self.successful_poll_count + self.failed_poll_count
            previous = self.average_duration_ms or 0
            self.average_duration_ms = ((previous * (total - 1)) + duration_ms) / total
        self.schedule_next(now)
        self.save()

    def complete_failure(self, *, lock_token, error_message, error_code='', duration_ms=None):
        self.validate_lock(lock_token)
        now = timezone.now()
        self.failed_poll_count += 1
        self.consecutive_failure_count += 1
        self.last_completed_at = now
        self.last_failure_at = now
        self.last_duration_ms = duration_ms
        self.last_error_code = str(error_code or '').strip().upper()
        self.last_error_message = str(error_message or '').strip()
        self.lock_token = None
        self.lock_expires_at = None
        calculated = self.backoff_seconds * (2 ** max(self.consecutive_failure_count - 1, 0))
        self.current_backoff_seconds = min(calculated, self.maximum_backoff_seconds)
        self.next_poll_at = now + timezone.timedelta(seconds=self.current_backoff_seconds)
        if self.consecutive_failure_count >= self.maximum_consecutive_failures:
            self.status = self.Status.PAUSED
            self.pause_reason = 'Se alcanzó el máximo de fallos consecutivos.'
            self.enabled = False
        else:
            self.status = self.Status.BACKOFF
        self.save()

    def pause(self, reason):
        self.status = self.Status.PAUSED
        self.enabled = False
        self.pause_reason = str(reason or '').strip()
        self.lock_token = None
        self.lock_expires_at = None
        self.save()

    def resume(self, next_poll_at=None):
        self.enabled = True
        self.status = self.Status.IDLE
        self.pause_reason = ''
        self.consecutive_failure_count = 0
        self.current_backoff_seconds = 0
        self.next_poll_at = next_poll_at or timezone.now()
        self.save()

    def clean(self):
        super().clean()
        if not self.device_id:
            raise ValidationError({'device': 'El dispositivo es obligatorio.'})
        if self.device.agent_id != self.agent_id:
            raise ValidationError({'agent': 'El agente no coincide con el dispositivo.'})
        if self.device.customer_id != self.customer_id:
            raise ValidationError({'customer': 'El cliente no coincide con el dispositivo.'})
        if self.branch_id and self.branch.partner_id != self.customer_id:
            raise ValidationError({'branch': 'La sede no pertenece al cliente.'})
        if self.network_id and self.network.agent_id != self.agent_id:
            raise ValidationError({'network': 'La red no pertenece al agente.'})
        if self.profile_assignment_id and self.profile_assignment.device_id != self.device_id:
            raise ValidationError({'profile_assignment': 'No pertenece al dispositivo.'})
        if self.last_command_id and self.last_command.agent_id != self.agent_id:
            raise ValidationError({'last_command': 'La orden pertenece a otro agente.'})
        if self.interval_seconds < 10:
            raise ValidationError({'interval_seconds': 'El intervalo mínimo es 10 segundos.'})
        if self.maximum_consecutive_failures < 1:
            raise ValidationError({'maximum_consecutive_failures': 'Debe ser mayor que cero.'})
        if self.maximum_backoff_seconds < self.backoff_seconds:
            raise ValidationError({'maximum_backoff_seconds': 'No puede ser menor que la espera inicial.'})
        if self.status == self.Status.RUNNING and not self.lock_token:
            raise ValidationError({'lock_token': 'Una consulta en ejecución requiere bloqueo.'})
        if not isinstance(self.state_data, dict):
            raise ValidationError({'state_data': 'Debe ser un objeto.'})

    def save(self, *args, **kwargs):
        if self.device_id:
            self.agent = self.device.agent
            self.customer = self.device.customer
            self.branch = self.device.branch
            self.network = self.device.network
        self.last_error_code = str(self.last_error_code or '').strip().upper()
        self.full_clean()
        return super().save(*args, **kwargs)
