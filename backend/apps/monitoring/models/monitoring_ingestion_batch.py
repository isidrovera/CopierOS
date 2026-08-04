# -*- coding: utf-8 -*-
import hashlib
import json
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class MonitoringIngestionBatch(MonitoringBaseModel):
    class BatchType(models.TextChoices):
        SNAPSHOTS = 'snapshots', 'Capturas'
        DISCOVERIES = 'discoveries', 'Descubrimientos'
        COMMAND_RESULTS = 'command_results', 'Resultados de órdenes'
        AGENT_LOGS = 'agent_logs', 'Logs del agente'
        EVENTS = 'events', 'Eventos'
        PROFILE_TESTS = 'profile_tests', 'Pruebas de perfiles'
        MIXED = 'mixed', 'Mixto'

    class Status(models.TextChoices):
        RECEIVED = 'received', 'Recibido'
        VALIDATING = 'validating', 'Validando'
        PROCESSING = 'processing', 'Procesando'
        COMPLETED = 'completed', 'Completado'
        PARTIAL = 'partial', 'Parcial'
        FAILED = 'failed', 'Fallido'
        REJECTED = 'rejected', 'Rechazado'
        DUPLICATE = 'duplicate', 'Duplicado'

    batch_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    agent = models.ForeignKey('monitoring.MonitoringAgent', on_delete=models.PROTECT, related_name='ingestion_batches')
    customer = models.ForeignKey('partners.Partner', on_delete=models.PROTECT, related_name='monitoring_ingestion_batches')
    branch = models.ForeignKey('partners.PartnerBranch', null=True, blank=True, on_delete=models.PROTECT, related_name='monitoring_ingestion_batches')
    sync = models.ForeignKey('monitoring.AgentSync', null=True, blank=True, on_delete=models.PROTECT, related_name='ingestion_batches')
    duplicate_of = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, related_name='duplicate_batches')
    agent_batch_id = models.CharField(max_length=150, db_index=True)
    idempotency_key = models.CharField(max_length=150, db_index=True)
    batch_type = models.CharField(max_length=30, choices=BatchType.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEIVED, db_index=True)
    schema_version = models.CharField(max_length=50, blank=True)
    agent_version = models.CharField(max_length=50, blank=True)
    item_count = models.PositiveIntegerField(default=0)
    validated_count = models.PositiveIntegerField(default=0)
    accepted_count = models.PositiveIntegerField(default=0)
    rejected_count = models.PositiveIntegerField(default=0)
    duplicate_count = models.PositiveIntegerField(default=0)
    warning_count = models.PositiveIntegerField(default=0)
    payload_checksum = models.CharField(max_length=64, blank=True, db_index=True)
    payload_size_bytes = models.PositiveBigIntegerField(default=0)
    compressed = models.BooleanField(default=False)
    compression_type = models.CharField(max_length=30, blank=True)
    received_at = models.DateTimeField(default=timezone.now, db_index=True)
    validation_started_at = models.DateTimeField(null=True, blank=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    duration_ms = models.PositiveBigIntegerField(null=True, blank=True)
    validation_duration_ms = models.PositiveBigIntegerField(null=True, blank=True)
    processing_duration_ms = models.PositiveBigIntegerField(null=True, blank=True)
    payload_summary = models.JSONField(default=dict, blank=True)
    accepted_items = models.JSONField(default=list, blank=True)
    rejected_items = models.JSONField(default=list, blank=True)
    duplicate_items = models.JSONField(default=list, blank=True)
    warnings = models.JSONField(default=list, blank=True)
    processing_result = models.JSONField(default=dict, blank=True)
    error_code = models.CharField(max_length=150, blank=True, db_index=True)
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    acknowledgement_payload = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ('-received_at',)
        indexes = [
            models.Index(fields=['agent', 'status', 'received_at'], name='mon_ingest_agent_idx'),
            models.Index(fields=['customer', 'batch_type', 'received_at'], name='mon_ingest_customer_idx'),
            models.Index(fields=['idempotency_key', 'agent'], name='mon_ingest_idempotency_idx'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['agent', 'idempotency_key'], name='unique_agent_ingestion_idempotency'),
            models.UniqueConstraint(fields=['agent', 'agent_batch_id'], name='unique_agent_ingestion_batch'),
        ]

    def __str__(self):
        return f'{self.agent} - {self.agent_batch_id}'

    @staticmethod
    def calculate_payload_checksum(payload):
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':'), default=str)
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def calculate_durations(self):
        if self.received_at and self.completed_at:
            self.duration_ms = max(int((self.completed_at - self.received_at).total_seconds() * 1000), 0)
        if self.validation_started_at and self.processing_started_at:
            self.validation_duration_ms = max(int((self.processing_started_at - self.validation_started_at).total_seconds() * 1000), 0)
        if self.processing_started_at and self.completed_at:
            self.processing_duration_ms = max(int((self.completed_at - self.processing_started_at).total_seconds() * 1000), 0)

    def begin_validation(self):
        if self.status != self.Status.RECEIVED:
            raise ValidationError('El lote no está disponible para validación.')
        self.status = self.Status.VALIDATING
        self.validation_started_at = timezone.now()
        self.save()

    def begin_processing(self):
        if self.status not in {self.Status.RECEIVED, self.Status.VALIDATING}:
            raise ValidationError('El lote no está disponible para procesamiento.')
        self.status = self.Status.PROCESSING
        self.processing_started_at = timezone.now()
        self.save()

    def complete(self, *, accepted_items=None, rejected_items=None, duplicate_items=None, warnings=None, processing_result=None):
        self.accepted_items = accepted_items or []
        self.rejected_items = rejected_items or []
        self.duplicate_items = duplicate_items or []
        self.warnings = warnings or []
        self.accepted_count = len(self.accepted_items)
        self.rejected_count = len(self.rejected_items)
        self.duplicate_count = len(self.duplicate_items)
        self.warning_count = len(self.warnings)
        self.validated_count = self.accepted_count + self.rejected_count + self.duplicate_count
        self.processing_result = processing_result or {}
        self.completed_at = timezone.now()
        if self.rejected_count and self.accepted_count:
            self.status = self.Status.PARTIAL
        elif self.rejected_count and not self.accepted_count:
            self.status = self.Status.REJECTED
        else:
            self.status = self.Status.COMPLETED
        self.acknowledgement_payload = {
            'batch_id': self.agent_batch_id,
            'status': self.status,
            'accepted_count': self.accepted_count,
            'rejected_count': self.rejected_count,
            'duplicate_count': self.duplicate_count,
            'rejected_items': self.rejected_items,
        }
        self.calculate_durations()
        self.save()

    def fail(self, error_message, error_code='', error_details=None):
        self.status = self.Status.FAILED
        self.completed_at = timezone.now()
        self.error_code = str(error_code or '').strip().upper()
        self.error_message = str(error_message or '').strip()
        self.error_details = error_details or {}
        self.acknowledgement_payload = {'batch_id': self.agent_batch_id, 'status': self.status, 'error_code': self.error_code, 'error_message': self.error_message}
        self.calculate_durations()
        self.save()

    def mark_duplicate(self, original_batch):
        if original_batch.agent_id != self.agent_id:
            raise ValidationError('El lote original pertenece a otro agente.')
        self.status = self.Status.DUPLICATE
        self.duplicate_of = original_batch
        self.completed_at = timezone.now()
        self.acknowledgement_payload = dict(original_batch.acknowledgement_payload or {})
        self.acknowledgement_payload['duplicate'] = True
        self.calculate_durations()
        self.save()

    def clean(self):
        super().clean()
        self.agent_batch_id = str(self.agent_batch_id or '').strip()
        self.idempotency_key = str(self.idempotency_key or '').strip()
        self.payload_checksum = str(self.payload_checksum or '').strip().lower()
        self.error_code = str(self.error_code or '').strip().upper()
        if not self.agent_id:
            raise ValidationError({'agent': 'El agente es obligatorio.'})
        if not self.agent_batch_id:
            raise ValidationError({'agent_batch_id': 'Es obligatorio.'})
        if not self.idempotency_key:
            raise ValidationError({'idempotency_key': 'Es obligatoria.'})
        if self.agent.customer_id != self.customer_id:
            raise ValidationError({'customer': 'El cliente no coincide con el agente.'})
        if self.branch_id and self.branch.partner_id != self.customer_id:
            raise ValidationError({'branch': 'La sede no pertenece al cliente.'})
        if self.sync_id and self.sync.agent_id != self.agent_id:
            raise ValidationError({'sync': 'La sincronización pertenece a otro agente.'})
        if self.duplicate_of_id:
            if self.duplicate_of_id == self.id:
                raise ValidationError({'duplicate_of': 'No puede duplicarse a sí mismo.'})
            if self.duplicate_of.agent_id != self.agent_id:
                raise ValidationError({'duplicate_of': 'Pertenece a otro agente.'})
        result_sum = self.accepted_count + self.rejected_count + self.duplicate_count
        if result_sum > self.item_count:
            raise ValidationError({'item_count': 'La suma de resultados supera el total.'})
        if self.validated_count > self.item_count:
            raise ValidationError({'validated_count': 'No puede superar el total.'})
        if self.status == self.Status.FAILED and not self.error_message:
            raise ValidationError({'error_message': 'Debe registrar el error.'})
        if self.compressed and not self.compression_type:
            raise ValidationError({'compression_type': 'Debe indicar la compresión.'})
        for field in ('payload_summary', 'processing_result', 'error_details', 'acknowledgement_payload'):
            if not isinstance(getattr(self, field), dict):
                raise ValidationError({field: 'Debe ser un objeto.'})
        for field in ('accepted_items', 'rejected_items', 'duplicate_items', 'warnings'):
            if not isinstance(getattr(self, field), list):
                raise ValidationError({field: 'Debe ser una lista.'})
        self.calculate_durations()

    def save(self, *args, **kwargs):
        if self.agent_id:
            self.customer = self.agent.customer
            self.branch = self.agent.branch
        self.agent_batch_id = str(self.agent_batch_id or '').strip()
        self.idempotency_key = str(self.idempotency_key or '').strip()
        self.payload_checksum = str(self.payload_checksum or '').strip().lower()
        self.error_code = str(self.error_code or '').strip().upper()
        self.calculate_durations()
        self.full_clean()
        return super().save(*args, **kwargs)

    def archive(self, user=None, reason='', save=True):
        raise ValidationError('Los lotes históricos no pueden archivarse.')

    def restore(self, user=None, save=True):
        raise ValidationError('Los lotes históricos no pueden restaurarse.')
