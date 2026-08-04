# -*- coding: utf-8 -*-
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class MonitoringReportExecution(MonitoringBaseModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        RUNNING = 'running', 'En ejecución'
        GENERATING = 'generating', 'Generando archivo'
        DELIVERING = 'delivering', 'Entregando'
        COMPLETED = 'completed', 'Completada'
        PARTIAL = 'partial', 'Parcial'
        FAILED = 'failed', 'Fallida'
        CANCELLED = 'cancelled', 'Cancelada'
        EXPIRED = 'expired', 'Expirada'

    execution_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    schedule = models.ForeignKey('monitoring.MonitoringReportSchedule', on_delete=models.PROTECT, related_name='executions')
    customer = models.ForeignKey('partners.Partner', null=True, blank=True, on_delete=models.PROTECT, related_name='monitoring_report_executions')
    branch = models.ForeignKey('partners.PartnerBranch', null=True, blank=True, on_delete=models.PROTECT, related_name='monitoring_report_executions')
    agent = models.ForeignKey('monitoring.MonitoringAgent', null=True, blank=True, on_delete=models.PROTECT, related_name='report_executions')
    device = models.ForeignKey('monitoring.MonitoredDevice', null=True, blank=True, on_delete=models.PROTECT, related_name='report_executions')
    schedule_code = models.CharField(max_length=150, editable=False, db_index=True)
    report_type = models.CharField(max_length=40, editable=False, db_index=True)
    output_format = models.CharField(max_length=10, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    period_start = models.DateTimeField(db_index=True)
    period_end = models.DateTimeField(db_index=True)
    requested_at = models.DateTimeField(default=timezone.now, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True, db_index=True)
    generation_completed_at = models.DateTimeField(null=True, blank=True)
    delivery_started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    duration_ms = models.PositiveBigIntegerField(null=True, blank=True)
    generation_duration_ms = models.PositiveBigIntegerField(null=True, blank=True)
    delivery_duration_ms = models.PositiveBigIntegerField(null=True, blank=True)
    total_device_count = models.PositiveIntegerField(default=0)
    processed_device_count = models.PositiveIntegerField(default=0)
    failed_device_count = models.PositiveIntegerField(default=0)
    row_count = models.PositiveBigIntegerField(default=0)
    warning_count = models.PositiveIntegerField(default=0)
    filename = models.CharField(max_length=500, blank=True)
    file = models.FileField(upload_to='monitoring/reports/%Y/%m/', null=True, blank=True)
    file_size_bytes = models.PositiveBigIntegerField(null=True, blank=True)
    file_checksum = models.CharField(max_length=64, blank=True, db_index=True)
    mime_type = models.CharField(max_length=150, blank=True)
    storage_key = models.CharField(max_length=1000, blank=True, db_index=True)
    requested_by = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='requested_monitoring_reports')
    filters_snapshot = models.JSONField(default=dict, blank=True)
    columns_snapshot = models.JSONField(default=list, blank=True)
    grouping_snapshot = models.JSONField(default=list, blank=True)
    sorting_snapshot = models.JSONField(default=list, blank=True)
    options_snapshot = models.JSONField(default=dict, blank=True)
    delivery_channels = models.JSONField(default=list, blank=True)
    resolved_recipients = models.JSONField(default=list, blank=True)
    delivery_results = models.JSONField(default=dict, blank=True)
    delivered_channel_count = models.PositiveIntegerField(default=0)
    failed_channel_count = models.PositiveIntegerField(default=0)
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    progress_data = models.JSONField(default=dict, blank=True)
    warnings = models.JSONField(default=list, blank=True)
    error_code = models.CharField(max_length=150, blank=True, db_index=True)
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    cancellation_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ('-requested_at',)
        indexes = [
            models.Index(fields=['schedule', 'status', 'requested_at'], name='mon_rexec_schedule_idx'),
            models.Index(fields=['customer', 'report_type', 'period_start'], name='mon_rexec_customer_idx'),
            models.Index(fields=['status', 'requested_at'], name='mon_rexec_status_idx'),
        ]

    def __str__(self):
        return f'{self.schedule_code} - {self.period_start:%Y-%m-%d}'

    def calculate_durations(self):
        if self.started_at and self.completed_at:
            self.duration_ms = max(int((self.completed_at - self.started_at).total_seconds() * 1000), 0)
        if self.started_at and self.generation_completed_at:
            self.generation_duration_ms = max(int((self.generation_completed_at - self.started_at).total_seconds() * 1000), 0)
        if self.delivery_started_at and self.completed_at:
            self.delivery_duration_ms = max(int((self.completed_at - self.delivery_started_at).total_seconds() * 1000), 0)

    def begin(self):
        if self.status != self.Status.PENDING:
            raise ValidationError('La ejecución no está pendiente.')
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.progress_percent = 0
        self.error_code = ''
        self.error_message = ''
        self.error_details = {}
        self.save()

    def register_progress(self, progress_percent, progress_data=None):
        if self.status not in {self.Status.RUNNING, self.Status.GENERATING, self.Status.DELIVERING}:
            raise ValidationError('La ejecución no admite progreso.')
        self.progress_percent = progress_percent
        if progress_data is not None:
            self.progress_data = progress_data
        self.save()

    def mark_generating(self):
        if self.status not in {self.Status.RUNNING, self.Status.GENERATING}:
            raise ValidationError('La ejecución no puede generar el archivo.')
        self.status = self.Status.GENERATING
        self.save(update_fields=['status', 'updated_at'])

    def register_file(self, *, filename, file=None, file_size_bytes=None, file_checksum='', mime_type='', storage_key='', row_count=0):
        if self.status not in {self.Status.RUNNING, self.Status.GENERATING}:
            raise ValidationError('La ejecución no está generando.')
        self.filename = str(filename or '').strip()
        self.file = file
        self.file_size_bytes = file_size_bytes
        self.file_checksum = str(file_checksum or '').strip().lower()
        self.mime_type = str(mime_type or '').strip()
        self.storage_key = str(storage_key or '').strip()
        self.row_count = max(int(row_count or 0), 0)
        self.generation_completed_at = timezone.now()
        self.progress_percent = 80
        self.save()

    def mark_delivering(self):
        if not self.filename and not self.file and not self.storage_key:
            raise ValidationError('No existe archivo para entregar.')
        self.status = self.Status.DELIVERING
        self.delivery_started_at = timezone.now()
        self.progress_percent = 85
        self.save()

    def complete(self, delivery_results=None, partial=False):
        if self.status not in {self.Status.RUNNING, self.Status.GENERATING, self.Status.DELIVERING}:
            raise ValidationError('La ejecución no puede completarse.')
        if delivery_results is not None:
            self.delivery_results = delivery_results
        self.status = self.Status.PARTIAL if partial else self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.progress_percent = 100
        self.error_code = ''
        self.error_message = ''
        self.error_details = {}
        self.calculate_durations()
        self.save()
        self.schedule.register_execution(successful=not partial, executed_at=self.completed_at)

    def fail(self, error_message, error_code='', error_details=None):
        if self.status in {self.Status.COMPLETED, self.Status.PARTIAL, self.Status.CANCELLED, self.Status.EXPIRED}:
            raise ValidationError('La ejecución ya finalizó.')
        self.status = self.Status.FAILED
        self.completed_at = timezone.now()
        self.error_code = str(error_code or '').strip().upper()
        self.error_message = str(error_message or '').strip()
        self.error_details = error_details or {}
        self.calculate_durations()
        self.save()
        self.schedule.register_execution(successful=False, executed_at=self.completed_at, error_message=self.error_message)

    def cancel(self, reason):
        if self.status in {self.Status.COMPLETED, self.Status.PARTIAL, self.Status.FAILED, self.Status.CANCELLED, self.Status.EXPIRED}:
            raise ValidationError('La ejecución ya finalizó.')
        self.status = self.Status.CANCELLED
        self.completed_at = timezone.now()
        self.cancellation_reason = str(reason or '').strip()
        self.calculate_durations()
        self.save()

    def clean(self):
        super().clean()
        if not self.schedule_id:
            raise ValidationError({'schedule': 'La programación es obligatoria.'})
        if self.period_end <= self.period_start:
            raise ValidationError({'period_end': 'Debe ser posterior al inicio.'})
        if self.progress_percent < 0 or self.progress_percent > 100:
            raise ValidationError({'progress_percent': 'Debe estar entre 0 y 100.'})
        if self.processed_device_count > self.total_device_count:
            raise ValidationError({'processed_device_count': 'No puede superar el total.'})
        if self.failed_device_count > self.processed_device_count:
            raise ValidationError({'failed_device_count': 'No puede superar los procesados.'})
        if self.completed_at and self.started_at and self.completed_at < self.started_at:
            raise ValidationError({'completed_at': 'No puede ser anterior al inicio.'})
        if self.status == self.Status.COMPLETED and self.progress_percent != 100:
            raise ValidationError({'progress_percent': 'Una ejecución completada debe estar al 100%.'})
        if self.status == self.Status.FAILED and not self.error_message:
            raise ValidationError({'error_message': 'Debe registrar el error.'})
        if self.status == self.Status.CANCELLED and not self.cancellation_reason:
            raise ValidationError({'cancellation_reason': 'Debe indicar el motivo.'})
        for field in ('filters_snapshot', 'options_snapshot', 'delivery_results', 'progress_data', 'error_details'):
            if not isinstance(getattr(self, field), dict):
                raise ValidationError({field: 'Debe ser un objeto.'})
        for field in ('columns_snapshot', 'grouping_snapshot', 'sorting_snapshot', 'delivery_channels', 'resolved_recipients', 'warnings'):
            if not isinstance(getattr(self, field), list):
                raise ValidationError({field: 'Debe ser una lista.'})
        self.calculate_durations()

    def save(self, *args, **kwargs):
        if self.schedule_id:
            self.schedule_code = self.schedule.code
            self.report_type = self.schedule.report_type
            self.output_format = self.schedule.output_format
            self.customer = self.schedule.customer
            self.branch = self.schedule.branch
            self.agent = self.schedule.agent
            self.device = self.schedule.device
            if not self.filters_snapshot:
                self.filters_snapshot = dict(self.schedule.filters or {})
            if not self.columns_snapshot:
                self.columns_snapshot = list(self.schedule.columns or [])
            if not self.grouping_snapshot:
                self.grouping_snapshot = list(self.schedule.grouping or [])
            if not self.sorting_snapshot:
                self.sorting_snapshot = list(self.schedule.sorting or [])
            if not self.options_snapshot:
                self.options_snapshot = dict(self.schedule.report_options or {})
            if not self.delivery_channels:
                self.delivery_channels = list(self.schedule.delivery_channels or [])
        self.schedule_code = str(self.schedule_code or '').strip().upper()
        self.error_code = str(self.error_code or '').strip().upper()
        self.calculate_durations()
        self.full_clean()
        return super().save(*args, **kwargs)

    def archive(self, user=None, reason='', save=True):
        raise ValidationError('Las ejecuciones históricas no pueden archivarse.')

    def restore(self, user=None, save=True):
        raise ValidationError('Las ejecuciones históricas no pueden restaurarse.')
