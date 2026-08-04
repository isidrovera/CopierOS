# -*- coding: utf-8 -*-
import hashlib
import json
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class AgentConfigurationVersion(MonitoringBaseModel):
    class Status(models.TextChoices):
        GENERATED = 'generated', 'Generada'
        PENDING_DELIVERY = 'pending_delivery', 'Pendiente de entrega'
        DELIVERED = 'delivered', 'Entregada'
        DOWNLOADED = 'downloaded', 'Descargada'
        APPLIED = 'applied', 'Aplicada'
        REJECTED = 'rejected', 'Rechazada'
        FAILED = 'failed', 'Fallida'
        SUPERSEDED = 'superseded', 'Reemplazada'

    configuration_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    agent = models.ForeignKey('monitoring.MonitoringAgent', on_delete=models.PROTECT, related_name='configuration_versions')
    customer = models.ForeignKey('partners.Partner', on_delete=models.PROTECT, related_name='monitoring_agent_configuration_versions')
    branch = models.ForeignKey('partners.PartnerBranch', null=True, blank=True, on_delete=models.PROTECT, related_name='monitoring_agent_configuration_versions')
    base_configuration = models.ForeignKey('monitoring.MonitoringConfiguration', null=True, blank=True, on_delete=models.PROTECT, related_name='agent_versions')
    previous_version = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, related_name='next_versions')
    version = models.PositiveBigIntegerField(db_index=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.GENERATED, db_index=True)
    checksum = models.CharField(max_length=64, db_index=True, editable=False)
    payload = models.JSONField(default=dict)
    payload_size_bytes = models.PositiveBigIntegerField(default=0)
    changed_sections = models.JSONField(default=list, blank=True)
    generation_context = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField(default=timezone.now, db_index=True)
    delivered_at = models.DateTimeField(null=True, blank=True, db_index=True)
    downloaded_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(null=True, blank=True, db_index=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    superseded_at = models.DateTimeField(null=True, blank=True)
    agent_version = models.CharField(max_length=50, blank=True)
    agent_reported_checksum = models.CharField(max_length=64, blank=True, db_index=True)
    application_successful = models.BooleanField(null=True, blank=True, db_index=True)
    application_details = models.JSONField(default=dict, blank=True)
    error_code = models.CharField(max_length=150, blank=True, db_index=True)
    error_message = models.TextField(blank=True)
    generated_by = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='generated_agent_configurations')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ('-version',)
        indexes = [
            models.Index(fields=['agent', 'version', 'status'], name='mon_aconfig_agent_ver_idx'),
            models.Index(fields=['agent', 'status', 'generated_at'], name='mon_aconfig_status_idx'),
            models.Index(fields=['checksum', 'status'], name='mon_aconfig_checksum_idx'),
        ]
        constraints = [models.UniqueConstraint(fields=['agent', 'version'], name='unique_agent_configuration_version')]

    def __str__(self):
        return f'{self.agent} - v{self.version}'

    @staticmethod
    def serialize_payload(payload):
        return json.dumps(payload or {}, sort_keys=True, ensure_ascii=False, separators=(',', ':'), default=str)

    def calculate_checksum(self):
        return hashlib.sha256(self.serialize_payload(self.payload).encode('utf-8')).hexdigest()

    def calculate_payload_size(self):
        return len(self.serialize_payload(self.payload).encode('utf-8'))

    def mark_pending_delivery(self):
        if self.status != self.Status.GENERATED:
            raise ValidationError('Solo una configuración generada puede quedar pendiente.')
        self.status = self.Status.PENDING_DELIVERY
        self.save(update_fields=['status', 'updated_at'])

    def mark_delivered(self):
        if self.status not in {self.Status.GENERATED, self.Status.PENDING_DELIVERY, self.Status.DELIVERED}:
            raise ValidationError('La configuración no puede entregarse.')
        self.status = self.Status.DELIVERED
        self.delivered_at = timezone.now()
        self.save()

    def mark_downloaded(self, agent_version=''):
        if self.status not in {self.Status.DELIVERED, self.Status.DOWNLOADED}:
            raise ValidationError('La configuración debe haberse entregado.')
        self.status = self.Status.DOWNLOADED
        self.downloaded_at = timezone.now()
        self.agent_version = str(agent_version or '').strip()
        self.save()

    def confirm_applied(self, *, agent_reported_checksum, application_details=None, agent_version=''):
        supplied = str(agent_reported_checksum or '').strip().lower()
        self.agent_reported_checksum = supplied
        self.application_details = application_details or {}
        self.agent_version = str(agent_version or '').strip()
        if supplied != self.checksum:
            self.status = self.Status.FAILED
            self.application_successful = False
            self.error_code = 'CONFIG_CHECKSUM_MISMATCH'
            self.error_message = 'El checksum aplicado por el agente no coincide.'
            self.save()
            return False
        self.status = self.Status.APPLIED
        self.applied_at = timezone.now()
        self.application_successful = True
        self.error_code = ''
        self.error_message = ''
        self.save()
        return True

    def reject(self, error_message, error_code='', details=None):
        self.status = self.Status.REJECTED
        self.rejected_at = timezone.now()
        self.application_successful = False
        self.error_code = str(error_code or '').strip().upper()
        self.error_message = str(error_message or '').strip()
        self.application_details = details or {}
        self.save()

    def supersede(self):
        if self.status == self.Status.APPLIED:
            self.status = self.Status.SUPERSEDED
            self.superseded_at = timezone.now()
            self.save()

    def clean(self):
        super().clean()
        if not self.agent_id:
            raise ValidationError({'agent': 'El agente es obligatorio.'})
        if self.agent.customer_id != self.customer_id:
            raise ValidationError({'customer': 'El cliente no coincide con el agente.'})
        if self.branch_id and self.branch.partner_id != self.customer_id:
            raise ValidationError({'branch': 'La sede no pertenece al cliente.'})
        if self.base_configuration_id and not self.base_configuration.applies_to(customer=self.customer, branch=self.branch, agent=self.agent):
            raise ValidationError({'base_configuration': 'La configuración base no aplica al agente.'})
        if self.previous_version_id:
            if self.previous_version.agent_id != self.agent_id:
                raise ValidationError({'previous_version': 'Pertenece a otro agente.'})
            if self.previous_version.version >= self.version:
                raise ValidationError({'previous_version': 'Debe tener una versión menor.'})
        if not isinstance(self.payload, dict):
            raise ValidationError({'payload': 'Debe ser un objeto.'})
        if not isinstance(self.changed_sections, list):
            raise ValidationError({'changed_sections': 'Debe ser una lista.'})
        if not isinstance(self.generation_context, dict):
            raise ValidationError({'generation_context': 'Debe ser un objeto.'})
        if not isinstance(self.application_details, dict):
            raise ValidationError({'application_details': 'Debe ser un objeto.'})
        if self.status == self.Status.APPLIED and (not self.applied_at or not self.application_successful):
            raise ValidationError('Una configuración aplicada requiere fecha y resultado correcto.')
        if self.status in {self.Status.FAILED, self.Status.REJECTED} and not self.error_message:
            raise ValidationError({'error_message': 'Debe registrar el error.'})
        self.checksum = self.calculate_checksum()
        self.payload_size_bytes = self.calculate_payload_size()

    def save(self, *args, **kwargs):
        if self.agent_id:
            self.customer = self.agent.customer
            self.branch = self.agent.branch
        self.error_code = str(self.error_code or '').strip().upper()
        self.agent_reported_checksum = str(self.agent_reported_checksum or '').strip().lower()
        self.checksum = self.calculate_checksum()
        self.payload_size_bytes = self.calculate_payload_size()
        self.full_clean()
        return super().save(*args, **kwargs)

    def archive(self, user=None, reason='', save=True):
        raise ValidationError('Las versiones históricas no pueden archivarse.')

    def restore(self, user=None, save=True):
        raise ValidationError('Las versiones históricas no pueden restaurarse.')
