# -*- coding: utf-8 -*-
import hashlib
import json
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class AgentLog(MonitoringBaseModel):
    """
    Registro técnico enviado por un agente de monitoreo.

    Permite conservar eventos de ejecución relacionados con:

    - Descubrimiento de redes.
    - Consultas SNMP.
    - Procesamiento de capturas.
    - Sincronización con Copier OS.
    - Ejecución de órdenes.
    - Cola local.
    - Base de datos local.
    - Actualización del agente.
    - Errores y excepciones.

    No debe almacenar comunidades SNMP, contraseñas,
    tokens completos ni otras credenciales sensibles.
    """

    class Level(models.TextChoices):
        DEBUG = (
            "debug",
            "Debug",
        )
        INFO = (
            "info",
            "Información",
        )
        NOTICE = (
            "notice",
            "Aviso",
        )
        WARNING = (
            "warning",
            "Advertencia",
        )
        ERROR = (
            "error",
            "Error",
        )
        CRITICAL = (
            "critical",
            "Crítico",
        )

    class SourceType(models.TextChoices):
        AGENT = (
            "agent",
            "Agente",
        )
        SYSTEM = (
            "system",
            "Sistema",
        )
        SERVICE = (
            "service",
            "Servicio interno",
        )
        WORKER = (
            "worker",
            "Worker",
        )
        SCHEDULER = (
            "scheduler",
            "Programador",
        )
        API = (
            "api",
            "API",
        )

    class LogCategory(models.TextChoices):
        STARTUP = (
            "startup",
            "Inicio",
        )
        SHUTDOWN = (
            "shutdown",
            "Cierre",
        )
        REGISTRATION = (
            "registration",
            "Registro",
        )
        AUTHENTICATION = (
            "authentication",
            "Autenticación",
        )
        HEARTBEAT = (
            "heartbeat",
            "Heartbeat",
        )
        SYNCHRONIZATION = (
            "synchronization",
            "Sincronización",
        )
        CONFIGURATION = (
            "configuration",
            "Configuración",
        )
        COMMAND = (
            "command",
            "Orden",
        )
        DISCOVERY = (
            "discovery",
            "Descubrimiento",
        )
        NETWORK = (
            "network",
            "Red",
        )
        SNMP = (
            "snmp",
            "SNMP",
        )
        DEVICE = (
            "device",
            "Dispositivo",
        )
        SNAPSHOT = (
            "snapshot",
            "Captura",
        )
        PROFILE = (
            "profile",
            "Perfil SNMP",
        )
        QUEUE = (
            "queue",
            "Cola local",
        )
        DATABASE = (
            "database",
            "Base de datos",
        )
        STORAGE = (
            "storage",
            "Almacenamiento",
        )
        UPDATE = (
            "update",
            "Actualización",
        )
        SECURITY = (
            "security",
            "Seguridad",
        )
        PERFORMANCE = (
            "performance",
            "Rendimiento",
        )
        OTHER = (
            "other",
            "Otro",
        )

    class ProcessingStatus(models.TextChoices):
        RECEIVED = (
            "received",
            "Recibido",
        )
        REVIEWED = (
            "reviewed",
            "Revisado",
        )
        IGNORED = (
            "ignored",
            "Ignorado",
        )
        ESCALATED = (
            "escalated",
            "Escalado",
        )
        RESOLVED = (
            "resolved",
            "Resuelto",
        )

    log_uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="UUID del log",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        on_delete=models.PROTECT,
        related_name="technical_logs",
        verbose_name="Agente",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_agent_logs",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_agent_logs",
        verbose_name="Sede",
    )

    sync = models.ForeignKey(
        "monitoring.AgentSync",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="technical_logs",
        verbose_name="Sincronización",
    )

    command = models.ForeignKey(
        "monitoring.AgentCommand",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="technical_logs",
        verbose_name="Orden",
    )

    discovery = models.ForeignKey(
        "monitoring.MonitoringDiscovery",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="technical_logs",
        verbose_name="Descubrimiento",
    )

    network = models.ForeignKey(
        "monitoring.MonitoringNetwork",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="technical_logs",
        verbose_name="Red",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="technical_logs",
        verbose_name="Dispositivo",
    )

    snapshot = models.ForeignKey(
        "monitoring.DeviceSnapshot",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="technical_logs",
        verbose_name="Captura",
    )

    profile = models.ForeignKey(
        "monitoring.SNMPProfile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="technical_logs",
        verbose_name="Perfil SNMP",
    )

    agent_log_id = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Identificador generado por el agente",
        help_text=(
            "Permite evitar duplicados cuando el agente "
            "reenvía registros."
        ),
    )

    batch_id = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Lote de logs",
    )

    correlation_id = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Identificador de correlación",
        help_text=(
            "Relaciona logs producidos por una misma operación."
        ),
    )

    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.INFO,
        db_index=True,
        verbose_name="Nivel",
    )

    source_type = models.CharField(
        max_length=20,
        choices=SourceType.choices,
        default=SourceType.AGENT,
        db_index=True,
        verbose_name="Origen",
    )

    category = models.CharField(
        max_length=30,
        choices=LogCategory.choices,
        default=LogCategory.OTHER,
        db_index=True,
        verbose_name="Categoría",
    )

    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.RECEIVED,
        db_index=True,
        verbose_name="Estado de revisión",
    )

    module_name = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Módulo",
    )

    logger_name = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Logger",
    )

    function_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Función",
    )

    process_name = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Proceso",
    )

    process_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="ID de proceso",
    )

    thread_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Hilo",
    )

    thread_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="ID de hilo",
    )

    worker_name = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Worker",
    )

    message = models.TextField(
        verbose_name="Mensaje",
    )

    message_hash = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        editable=False,
        verbose_name="Huella del mensaje",
    )

    exception_type = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Tipo de excepción",
    )

    exception_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de excepción",
    )

    traceback = models.TextField(
        blank=True,
        verbose_name="Traceback",
    )

    error_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de error",
    )

    occurred_at = models.DateTimeField(
        db_index=True,
        verbose_name="Fecha del evento",
    )

    received_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de recepción",
    )

    agent_datetime = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha informada por el agente",
    )

    duration_ms = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración relacionada",
    )

    retry_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Número de reintento",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        protocol="both",
        unpack_ipv4=True,
        db_index=True,
        verbose_name="Dirección IP relacionada",
    )

    snmp_port = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Puerto SNMP",
    )

    oid = models.CharField(
        max_length=500,
        blank=True,
        db_index=True,
        verbose_name="OID relacionado",
    )

    metric_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de métrica",
    )

    queue_name = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Nombre de cola",
    )

    queue_item_id = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Elemento de cola",
    )

    request_method = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Método HTTP",
    )

    request_path = models.CharField(
        max_length=1000,
        blank=True,
        db_index=True,
        verbose_name="Ruta solicitada",
    )

    response_status_code = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Estado HTTP",
    )

    context = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Contexto",
    )

    environment = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Entorno",
    )

    performance_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos de rendimiento",
    )

    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Etiquetas",
    )

    contains_sensitive_data = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Contiene información sensible",
    )

    was_sanitized = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Contenido depurado",
    )

    requires_review = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere revisión",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de revisión",
    )

    reviewed_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_monitoring_agent_logs",
        verbose_name="Revisado por",
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de resolución",
    )

    resolved_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_monitoring_agent_logs",
        verbose_name="Resuelto por",
    )

    resolution_notes = models.TextField(
        blank=True,
        verbose_name="Notas de resolución",
    )

    occurrence_count = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad de ocurrencias",
    )

    first_occurrence_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Primera ocurrencia",
    )

    last_occurrence_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Última ocurrencia",
    )

    duplicate_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="duplicate_logs",
        verbose_name="Duplicado de",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Log técnico de agente"
        verbose_name_plural = "Logs técnicos de agentes"
        ordering = (
            "-occurred_at",
            "-received_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "agent",
                    "level",
                    "occurred_at",
                ],
                name="mon_alog_agent_level_idx",
            ),
            models.Index(
                fields=[
                    "customer",
                    "category",
                    "occurred_at",
                ],
                name="mon_alog_customer_cat_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "level",
                    "occurred_at",
                ],
                name="mon_alog_device_level_idx",
            ),
            models.Index(
                fields=[
                    "command",
                    "occurred_at",
                ],
                name="mon_alog_command_date_idx",
            ),
            models.Index(
                fields=[
                    "sync",
                    "occurred_at",
                ],
                name="mon_alog_sync_date_idx",
            ),
            models.Index(
                fields=[
                    "error_code",
                    "exception_type",
                    "occurred_at",
                ],
                name="mon_alog_error_type_idx",
            ),
            models.Index(
                fields=[
                    "requires_review",
                    "processing_status",
                    "occurred_at",
                ],
                name="mon_alog_review_status_idx",
            ),
            models.Index(
                fields=[
                    "message_hash",
                    "agent",
                    "occurred_at",
                ],
                name="mon_alog_hash_agent_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "agent",
                    "agent_log_id",
                ],
                condition=models.Q(
                    agent_log_id__gt="",
                ),
                name="unique_agent_log_id",
            ),
        ]

    def __str__(self):
        return (
            f"{self.agent} - "
            f"{self.get_level_display()} - "
            f"{self.message[:80]}"
        )

    def calculate_message_hash(self):
        normalized_context = json.dumps(
            self.context or {},
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        )

        values = [
            str(self.agent_id or ""),
            str(self.level or ""),
            str(self.category or ""),
            str(self.module_name or "").strip(),
            str(self.error_code or "").strip().upper(),
            str(self.exception_type or "").strip(),
            str(self.message or "").strip(),
            normalized_context,
        ]

        return hashlib.sha256(
            "|".join(values).encode("utf-8")
        ).hexdigest()

    def apply_review_requirement(self):
        self.requires_review = self.level in {
            self.Level.ERROR,
            self.Level.CRITICAL,
        }

        if self.category == self.LogCategory.SECURITY:
            self.requires_review = True

        if self.exception_type or self.traceback:
            self.requires_review = True

    def register_duplicate(
        self,
        duplicate_log,
    ):
        if duplicate_log.agent_id != self.agent_id:
            raise ValidationError(
                "El log original pertenece a otro agente."
            )

        duplicate_log.occurrence_count += 1
        duplicate_log.last_occurrence_at = max(
            self.occurred_at,
            duplicate_log.last_occurrence_at
            or duplicate_log.occurred_at,
        )

        duplicate_log.save(
            update_fields=[
                "occurrence_count",
                "last_occurrence_at",
                "updated_at",
            ]
        )

        self.duplicate_of = duplicate_log
        self.processing_status = (
            self.ProcessingStatus.IGNORED
        )

        self.save(
            update_fields=[
                "duplicate_of",
                "processing_status",
                "updated_at",
            ]
        )

    def mark_reviewed(
        self,
        *,
        user,
        notes="",
    ):
        self.processing_status = (
            self.ProcessingStatus.REVIEWED
        )
        self.reviewed_at = timezone.now()
        self.reviewed_by = user

        if notes:
            self.notes = str(
                notes
            ).strip()

        self.save(
            update_fields=[
                "processing_status",
                "reviewed_at",
                "reviewed_by",
                "notes",
                "updated_at",
            ]
        )

    def mark_escalated(
        self,
        *,
        user=None,
        notes="",
    ):
        self.processing_status = (
            self.ProcessingStatus.ESCALATED
        )
        self.requires_review = True
        self.reviewed_at = timezone.now()
        self.reviewed_by = user

        if notes:
            self.notes = str(
                notes
            ).strip()

        self.save(
            update_fields=[
                "processing_status",
                "requires_review",
                "reviewed_at",
                "reviewed_by",
                "notes",
                "updated_at",
            ]
        )

    def resolve(
        self,
        *,
        user,
        notes,
    ):
        self.processing_status = (
            self.ProcessingStatus.RESOLVED
        )
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.resolution_notes = str(
            notes or ""
        ).strip()

        self.save(
            update_fields=[
                "processing_status",
                "resolved_at",
                "resolved_by",
                "resolution_notes",
                "updated_at",
            ]
        )

    def mark_ignored(
        self,
        *,
        notes="",
    ):
        self.processing_status = (
            self.ProcessingStatus.IGNORED
        )

        if notes:
            self.notes = str(
                notes
            ).strip()

        self.save(
            update_fields=[
                "processing_status",
                "notes",
                "updated_at",
            ]
        )

    def clean(self):
        super().clean()

        text_fields = [
            "agent_log_id",
            "batch_id",
            "correlation_id",
            "module_name",
            "logger_name",
            "function_name",
            "process_name",
            "thread_name",
            "worker_name",
            "message",
            "exception_type",
            "exception_message",
            "traceback",
            "error_code",
            "oid",
            "metric_code",
            "queue_name",
            "queue_item_id",
            "request_method",
            "request_path",
            "resolution_notes",
            "notes",
        ]

        for field_name in text_fields:
            value = getattr(
                self,
                field_name,
                "",
            )

            setattr(
                self,
                field_name,
                str(value or "").strip(),
            )

        self.error_code = self.error_code.upper()
        self.metric_code = self.metric_code.upper()
        self.request_method = self.request_method.upper()
        self.oid = self.oid.strip(".")

        if not self.agent_id:
            raise ValidationError(
                {
                    "agent": "El agente es obligatorio.",
                }
            )

        if not self.message:
            raise ValidationError(
                {
                    "message": (
                        "El mensaje del log es obligatorio."
                    ),
                }
            )

        if not self.occurred_at:
            raise ValidationError(
                {
                    "occurred_at": (
                        "La fecha del evento es obligatoria."
                    ),
                }
            )

        if self.agent.customer_id != self.customer_id:
            raise ValidationError(
                {
                    "customer": (
                        "El cliente no coincide con el agente."
                    ),
                }
            )

        if (
            self.branch_id
            and self.branch.partner_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "branch": (
                        "La sede no pertenece al cliente."
                    ),
                }
            )

        related_agent_objects = [
            (
                "sync",
                self.sync,
            ),
            (
                "command",
                self.command,
            ),
            (
                "discovery",
                self.discovery,
            ),
            (
                "network",
                self.network,
            ),
            (
                "device",
                self.device,
            ),
        ]

        for field_name, related_object in related_agent_objects:
            if (
                related_object is not None
                and related_object.agent_id != self.agent_id
            ):
                raise ValidationError(
                    {
                        field_name: (
                            "El registro relacionado pertenece "
                            "a otro agente."
                        ),
                    }
                )

        if (
            self.snapshot_id
            and self.snapshot.device.agent_id
            != self.agent_id
        ):
            raise ValidationError(
                {
                    "snapshot": (
                        "La captura pertenece a otro agente."
                    ),
                }
            )

        if (
            self.profile_id
            and not self.profile.applies_to_scope(
                customer=self.customer,
                branch=self.branch,
                agent=self.agent,
                device=self.device,
            )
        ):
            raise ValidationError(
                {
                    "profile": (
                        "El perfil no corresponde al alcance "
                        "del log."
                    ),
                }
            )

        if (
            self.snmp_port is not None
            and (
                self.snmp_port < 1
                or self.snmp_port > 65535
            )
        ):
            raise ValidationError(
                {
                    "snmp_port": (
                        "El puerto SNMP debe estar "
                        "entre 1 y 65535."
                    ),
                }
            )

        if (
            self.agent_datetime
            and self.agent_datetime
            > self.received_at
            + timezone.timedelta(minutes=10)
        ):
            raise ValidationError(
                {
                    "agent_datetime": (
                        "La fecha del agente está "
                        "demasiado adelantada."
                    ),
                }
            )

        if (
            self.reviewed_at
            and self.reviewed_at < self.received_at
        ):
            raise ValidationError(
                {
                    "reviewed_at": (
                        "La revisión no puede ser anterior "
                        "a la recepción."
                    ),
                }
            )

        if (
            self.resolved_at
            and self.resolved_at < self.received_at
        ):
            raise ValidationError(
                {
                    "resolved_at": (
                        "La resolución no puede ser anterior "
                        "a la recepción."
                    ),
                }
            )

        if (
            self.processing_status
            == self.ProcessingStatus.RESOLVED
            and not self.resolved_at
        ):
            raise ValidationError(
                {
                    "resolved_at": (
                        "Un log resuelto requiere "
                        "fecha de resolución."
                    ),
                }
            )

        if (
            self.processing_status
            == self.ProcessingStatus.RESOLVED
            and not self.resolution_notes
        ):
            raise ValidationError(
                {
                    "resolution_notes": (
                        "Debe indicar cómo se resolvió."
                    ),
                }
            )

        if (
            self.duplicate_of_id
            and self.duplicate_of_id == self.id
        ):
            raise ValidationError(
                {
                    "duplicate_of": (
                        "Un log no puede ser duplicado "
                        "de sí mismo."
                    ),
                }
            )

        dict_fields = [
            "context",
            "environment",
            "performance_data",
        ]

        for field_name in dict_fields:
            if not isinstance(
                getattr(
                    self,
                    field_name,
                ),
                dict,
            ):
                raise ValidationError(
                    {
                        field_name: (
                            "Este campo debe ser un objeto."
                        ),
                    }
                )

        if not isinstance(
            self.tags,
            list,
        ):
            raise ValidationError(
                {
                    "tags": (
                        "Las etiquetas deben ser una lista."
                    ),
                }
            )

        self.first_occurrence_at = (
            self.first_occurrence_at
            or self.occurred_at
        )

        self.last_occurrence_at = (
            self.last_occurrence_at
            or self.occurred_at
        )

        if (
            self.last_occurrence_at
            < self.first_occurrence_at
        ):
            raise ValidationError(
                {
                    "last_occurrence_at": (
                        "La última ocurrencia no puede ser "
                        "anterior a la primera."
                    ),
                }
            )

        self.apply_review_requirement()
        self.message_hash = self.calculate_message_hash()

    def save(self, *args, **kwargs):
        if self.agent_id:
            self.customer = self.agent.customer
            self.branch = self.agent.branch

        if not self.occurred_at:
            self.occurred_at = (
                self.agent_datetime
                or timezone.now()
            )

        self.agent_log_id = str(
            self.agent_log_id or ""
        ).strip()

        self.batch_id = str(
            self.batch_id or ""
        ).strip()

        self.correlation_id = str(
            self.correlation_id or ""
        ).strip()

        self.error_code = str(
            self.error_code or ""
        ).strip().upper()

        self.metric_code = str(
            self.metric_code or ""
        ).strip().upper()

        self.oid = str(
            self.oid or ""
        ).strip().strip(".")

        self.apply_review_requirement()
        self.message_hash = self.calculate_message_hash()
        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )

    def archive(
        self,
        user=None,
        reason="",
        save=True,
    ):
        raise ValidationError(
            "Los logs técnicos históricos no pueden archivarse."
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        raise ValidationError(
            "Los logs técnicos históricos no pueden restaurarse."
        )