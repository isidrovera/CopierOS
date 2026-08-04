# -*- coding: utf-8 -*-
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class AgentSync(MonitoringBaseModel):
    """
    Historial de sincronización entre un agente y Copier OS.

    Registra cada comunicación del agente con el servidor:

    - Heartbeat.
    - Solicitud de configuración.
    - Descarga de órdenes.
    - Envío de capturas.
    - Envío de descubrimientos.
    - Resultados de órdenes.
    - Estado de la cola local.
    - Uso de CPU, memoria y disco.
    - Estado de servicios internos.
    - Errores de comunicación y procesamiento.
    """

    class SyncType(models.TextChoices):
        HEARTBEAT = (
            "heartbeat",
            "Heartbeat",
        )
        FULL_SYNC = (
            "full_sync",
            "Sincronización completa",
        )
        CONFIGURATION = (
            "configuration",
            "Configuración",
        )
        COMMANDS = (
            "commands",
            "Órdenes",
        )
        SNAPSHOTS = (
            "snapshots",
            "Capturas",
        )
        DISCOVERIES = (
            "discoveries",
            "Descubrimientos",
        )
        RESULTS = (
            "results",
            "Resultados",
        )
        EVENTS = (
            "events",
            "Eventos",
        )
        DIAGNOSTIC = (
            "diagnostic",
            "Diagnóstico",
        )
        REGISTRATION = (
            "registration",
            "Registro inicial",
        )

    class Status(models.TextChoices):
        RECEIVED = (
            "received",
            "Recibida",
        )
        PROCESSING = (
            "processing",
            "Procesando",
        )
        COMPLETED = (
            "completed",
            "Completada",
        )
        PARTIAL = (
            "partial",
            "Parcial",
        )
        FAILED = (
            "failed",
            "Fallida",
        )
        REJECTED = (
            "rejected",
            "Rechazada",
        )

    class ConnectionType(models.TextChoices):
        LAN = (
            "lan",
            "LAN",
        )
        WIFI = (
            "wifi",
            "Wi-Fi",
        )
        MOBILE = (
            "mobile",
            "Datos móviles",
        )
        VPN = (
            "vpn",
            "VPN",
        )
        PROXY = (
            "proxy",
            "Proxy",
        )
        UNKNOWN = (
            "unknown",
            "Desconocida",
        )

    sync_uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="UUID de sincronización",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        on_delete=models.PROTECT,
        related_name="syncs",
        verbose_name="Agente",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_agent_syncs",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_agent_syncs",
        verbose_name="Sede",
    )

    sync_type = models.CharField(
        max_length=30,
        choices=SyncType.choices,
        default=SyncType.HEARTBEAT,
        db_index=True,
        verbose_name="Tipo de sincronización",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECEIVED,
        db_index=True,
        verbose_name="Estado",
    )

    agent_sync_id = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Identificador generado por el agente",
        help_text=(
            "Permite evitar registros duplicados cuando el agente "
            "reintenta una sincronización."
        ),
    )

    request_id = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Identificador de solicitud",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de inicio",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de finalización",
    )

    received_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de recepción",
    )

    duration_ms = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración en milisegundos",
    )

    agent_datetime = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha y hora del agente",
    )

    clock_difference_seconds = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Diferencia de reloj",
    )

    agent_version = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Versión del agente",
    )

    operating_system = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Sistema operativo",
    )

    operating_system_version = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Versión del sistema operativo",
    )

    architecture = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Arquitectura",
    )

    hostname = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Hostname del agente",
    )

    local_ip_addresses = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Direcciones IP locales",
    )

    public_ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        protocol="both",
        unpack_ipv4=True,
        db_index=True,
        verbose_name="Dirección IP pública",
    )

    mac_addresses = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Direcciones MAC",
    )

    connection_type = models.CharField(
        max_length=20,
        choices=ConnectionType.choices,
        default=ConnectionType.UNKNOWN,
        verbose_name="Tipo de conexión",
    )

    configuration_version_requested = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Versión solicitada",
    )

    configuration_version_received = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Versión entregada",
    )

    configuration_changed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Configuración modificada",
    )

    configuration_checksum = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        verbose_name="Checksum de configuración",
    )

    commands_requested = models.PositiveIntegerField(
        default=0,
        verbose_name="Órdenes solicitadas",
    )

    commands_delivered = models.PositiveIntegerField(
        default=0,
        verbose_name="Órdenes entregadas",
    )

    command_results_received = models.PositiveIntegerField(
        default=0,
        verbose_name="Resultados de órdenes recibidos",
    )

    pending_command_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Órdenes pendientes",
    )

    running_command_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Órdenes en ejecución",
    )

    snapshots_received = models.PositiveIntegerField(
        default=0,
        verbose_name="Capturas recibidas",
    )

    snapshots_accepted = models.PositiveIntegerField(
        default=0,
        verbose_name="Capturas aceptadas",
    )

    snapshots_rejected = models.PositiveIntegerField(
        default=0,
        verbose_name="Capturas rechazadas",
    )

    snapshots_pending_local = models.PositiveIntegerField(
        default=0,
        verbose_name="Capturas pendientes en el agente",
    )

    discoveries_received = models.PositiveIntegerField(
        default=0,
        verbose_name="Descubrimientos recibidos",
    )

    discoveries_accepted = models.PositiveIntegerField(
        default=0,
        verbose_name="Descubrimientos aceptados",
    )

    discoveries_rejected = models.PositiveIntegerField(
        default=0,
        verbose_name="Descubrimientos rechazados",
    )

    events_received = models.PositiveIntegerField(
        default=0,
        verbose_name="Eventos recibidos",
    )

    alerts_received = models.PositiveIntegerField(
        default=0,
        verbose_name="Alertas recibidas",
    )

    raw_oid_reading_count = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Lecturas OID recibidas",
    )

    uploaded_bytes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Bytes enviados",
    )

    downloaded_bytes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Bytes recibidos",
    )

    request_payload_size_bytes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Tamaño de solicitud",
    )

    response_payload_size_bytes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Tamaño de respuesta",
    )

    local_queue_item_count = models.PositiveBigIntegerField(
        default=0,
        db_index=True,
        verbose_name="Elementos en cola local",
    )

    local_queue_oldest_item_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Elemento más antiguo en cola",
    )

    local_queue_size_bytes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Tamaño de cola local",
    )

    local_database_size_bytes = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Tamaño de base local",
    )

    local_available_storage_bytes = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Espacio local disponible",
    )

    cpu_usage_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Uso de CPU",
    )

    memory_usage_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Uso de memoria",
    )

    memory_used_bytes = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Memoria utilizada",
    )

    memory_total_bytes = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Memoria total",
    )

    disk_usage_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Uso de disco",
    )

    process_uptime_seconds = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo activo del proceso",
    )

    system_uptime_seconds = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo activo del sistema",
    )

    active_worker_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Procesos activos",
    )

    busy_worker_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Procesos ocupados",
    )

    monitored_network_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Redes monitoreadas",
    )

    monitored_device_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Dispositivos monitoreados",
    )

    online_device_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Dispositivos conectados",
    )

    offline_device_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Dispositivos desconectados",
    )

    service_status = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Estado de servicios",
        help_text=(
            "Estado del scheduler, descubrimiento, monitoreo, "
            "cola, almacenamiento y sincronización."
        ),
    )

    queue_status = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Detalle de colas",
    )

    resource_status = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Detalle de recursos",
    )

    configuration_response = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Configuración entregada",
    )

    commands_response = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Órdenes entregadas",
        help_text=(
            "No debe guardar secretos SNMP directamente."
        ),
    )

    acknowledgements = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Confirmaciones recibidas",
    )

    rejected_items = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Elementos rechazados",
    )

    warnings = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Advertencias",
    )

    error_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de error",
    )

    error_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de error",
    )

    error_details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Detalle del error",
    )

    remote_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        protocol="both",
        unpack_ipv4=True,
        db_index=True,
        verbose_name="Dirección remota",
    )

    user_agent = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="User-Agent",
    )

    api_version = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Versión de API",
    )

    authentication_successful = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Autenticación correcta",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Sincronización de agente"
        verbose_name_plural = "Sincronizaciones de agentes"
        ordering = (
            "-received_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "agent",
                    "received_at",
                    "status",
                ],
                name="mon_sync_agent_date_idx",
            ),
            models.Index(
                fields=[
                    "customer",
                    "sync_type",
                    "received_at",
                ],
                name="mon_sync_customer_type_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "authentication_successful",
                    "received_at",
                ],
                name="mon_sync_status_auth_idx",
            ),
            models.Index(
                fields=[
                    "local_queue_item_count",
                    "received_at",
                ],
                name="mon_sync_queue_date_idx",
            ),
            models.Index(
                fields=[
                    "configuration_changed",
                    "received_at",
                ],
                name="mon_sync_config_date_idx",
            ),
            models.Index(
                fields=[
                    "error_code",
                    "received_at",
                ],
                name="mon_sync_error_date_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "agent",
                    "agent_sync_id",
                ],
                name="unique_agent_sync_id",
            ),
        ]

    def __str__(self):
        return (
            f"{self.agent} - "
            f"{self.get_sync_type_display()} - "
            f"{self.get_status_display()}"
        )

    def calculate_duration(self):
        if self.started_at and self.completed_at:
            milliseconds = (
                self.completed_at - self.started_at
            ).total_seconds() * 1000

            self.duration_ms = max(
                int(milliseconds),
                0,
            )

    def calculate_clock_difference(self):
        if not self.agent_datetime:
            self.clock_difference_seconds = None
            return

        reference_time = (
            self.started_at
            or self.received_at
            or timezone.now()
        )

        difference = (
            self.agent_datetime - reference_time
        ).total_seconds()

        self.clock_difference_seconds = int(
            difference
        )

    def mark_processing(self):
        if self.status != self.Status.RECEIVED:
            raise ValidationError(
                "Solo una sincronización recibida puede procesarse."
            )

        self.status = self.Status.PROCESSING
        self.started_at = self.started_at or timezone.now()
        self.error_code = ""
        self.error_message = ""
        self.error_details = {}

        self.save(
            update_fields=[
                "status",
                "started_at",
                "error_code",
                "error_message",
                "error_details",
                "updated_at",
            ]
        )

    def mark_completed(
        self,
        *,
        partial=False,
        configuration_response=None,
        commands_response=None,
        acknowledgements=None,
        rejected_items=None,
        warnings=None,
    ):
        self.status = (
            self.Status.PARTIAL
            if partial
            else self.Status.COMPLETED
        )

        self.completed_at = timezone.now()
        self.error_code = ""
        self.error_message = ""
        self.error_details = {}

        if configuration_response is not None:
            self.configuration_response = configuration_response

        if commands_response is not None:
            self.commands_response = commands_response

        if acknowledgements is not None:
            self.acknowledgements = acknowledgements

        if rejected_items is not None:
            self.rejected_items = rejected_items

        if warnings is not None:
            self.warnings = warnings

        self.calculate_duration()

        self.save()

        self.agent.register_heartbeat(
            agent_version=self.agent_version,
            hostname=self.hostname,
            local_ip_addresses=self.local_ip_addresses,
            mac_addresses=self.mac_addresses,
        )

        return self

    def mark_failed(
        self,
        *,
        error_message,
        error_code="",
        error_details=None,
        rejected=False,
    ):
        self.status = (
            self.Status.REJECTED
            if rejected
            else self.Status.FAILED
        )

        self.completed_at = timezone.now()
        self.error_code = str(
            error_code or ""
        ).strip().upper()

        self.error_message = str(
            error_message or ""
        ).strip()

        if error_details is not None:
            self.error_details = error_details

        self.calculate_duration()
        self.save()

        return self

    def update_resource_status(
        self,
        *,
        cpu_usage_percent=None,
        memory_usage_percent=None,
        memory_used_bytes=None,
        memory_total_bytes=None,
        disk_usage_percent=None,
        local_available_storage_bytes=None,
        process_uptime_seconds=None,
        system_uptime_seconds=None,
        active_worker_count=None,
        busy_worker_count=None,
        service_status=None,
        queue_status=None,
        resource_status=None,
    ):
        if cpu_usage_percent is not None:
            self.cpu_usage_percent = cpu_usage_percent

        if memory_usage_percent is not None:
            self.memory_usage_percent = memory_usage_percent

        if memory_used_bytes is not None:
            self.memory_used_bytes = memory_used_bytes

        if memory_total_bytes is not None:
            self.memory_total_bytes = memory_total_bytes

        if disk_usage_percent is not None:
            self.disk_usage_percent = disk_usage_percent

        if local_available_storage_bytes is not None:
            self.local_available_storage_bytes = (
                local_available_storage_bytes
            )

        if process_uptime_seconds is not None:
            self.process_uptime_seconds = process_uptime_seconds

        if system_uptime_seconds is not None:
            self.system_uptime_seconds = system_uptime_seconds

        if active_worker_count is not None:
            self.active_worker_count = active_worker_count

        if busy_worker_count is not None:
            self.busy_worker_count = busy_worker_count

        if service_status is not None:
            self.service_status = service_status

        if queue_status is not None:
            self.queue_status = queue_status

        if resource_status is not None:
            self.resource_status = resource_status

        self.save()

    def clean(self):
        super().clean()

        text_fields = [
            "agent_sync_id",
            "request_id",
            "agent_version",
            "operating_system",
            "operating_system_version",
            "architecture",
            "hostname",
            "configuration_checksum",
            "error_code",
            "error_message",
            "user_agent",
            "api_version",
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

        if not self.agent_id:
            raise ValidationError(
                {
                    "agent": "El agente es obligatorio.",
                }
            )

        if not self.agent_sync_id:
            raise ValidationError(
                {
                    "agent_sync_id": (
                        "El identificador de sincronización "
                        "es obligatorio."
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

        if (
            self.completed_at
            and self.started_at
            and self.completed_at < self.started_at
        ):
            raise ValidationError(
                {
                    "completed_at": (
                        "La finalización no puede ser anterior "
                        "al inicio."
                    ),
                }
            )

        percentage_fields = [
            "cpu_usage_percent",
            "memory_usage_percent",
            "disk_usage_percent",
        ]

        for field_name in percentage_fields:
            value = getattr(
                self,
                field_name,
            )

            if value is not None and (
                value < 0
                or value > 100
            ):
                raise ValidationError(
                    {
                        field_name: (
                            "El porcentaje debe estar "
                            "entre 0 y 100."
                        ),
                    }
                )

        if (
            self.busy_worker_count
            > self.active_worker_count
        ):
            raise ValidationError(
                {
                    "busy_worker_count": (
                        "Los procesos ocupados no pueden superar "
                        "los procesos activos."
                    ),
                }
            )

        if (
            self.memory_used_bytes is not None
            and self.memory_total_bytes is not None
            and self.memory_used_bytes
            > self.memory_total_bytes
        ):
            raise ValidationError(
                {
                    "memory_used_bytes": (
                        "La memoria utilizada no puede superar "
                        "la memoria total."
                    ),
                }
            )

        if (
            self.snapshots_accepted
            + self.snapshots_rejected
            > self.snapshots_received
        ):
            raise ValidationError(
                {
                    "snapshots_received": (
                        "Las capturas aceptadas y rechazadas "
                        "no pueden superar las recibidas."
                    ),
                }
            )

        if (
            self.discoveries_accepted
            + self.discoveries_rejected
            > self.discoveries_received
        ):
            raise ValidationError(
                {
                    "discoveries_received": (
                        "Los descubrimientos aceptados y rechazados "
                        "no pueden superar los recibidos."
                    ),
                }
            )

        if (
            self.commands_delivered
            > self.commands_requested
            and self.commands_requested > 0
        ):
            raise ValidationError(
                {
                    "commands_delivered": (
                        "Las órdenes entregadas no pueden superar "
                        "las solicitadas."
                    ),
                }
            )

        if (
            self.status in {
                self.Status.FAILED,
                self.Status.REJECTED,
            }
            and not self.error_message
        ):
            raise ValidationError(
                {
                    "error_message": (
                        "Una sincronización fallida debe registrar "
                        "el error."
                    ),
                }
            )

        list_fields = [
            "local_ip_addresses",
            "mac_addresses",
            "commands_response",
            "acknowledgements",
            "rejected_items",
            "warnings",
        ]

        for field_name in list_fields:
            if not isinstance(
                getattr(
                    self,
                    field_name,
                ),
                list,
            ):
                raise ValidationError(
                    {
                        field_name: (
                            "Este campo debe ser una lista."
                        ),
                    }
                )

        dict_fields = [
            "service_status",
            "queue_status",
            "resource_status",
            "configuration_response",
            "error_details",
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

        self.calculate_duration()
        self.calculate_clock_difference()

    def save(self, *args, **kwargs):
        if self.agent_id:
            self.customer = self.agent.customer
            self.branch = self.agent.branch

        self.agent_sync_id = str(
            self.agent_sync_id or ""
        ).strip()

        self.request_id = str(
            self.request_id or ""
        ).strip()

        self.agent_version = str(
            self.agent_version or ""
        ).strip()

        self.hostname = str(
            self.hostname or ""
        ).strip()

        self.error_code = str(
            self.error_code or ""
        ).strip().upper()

        self.calculate_duration()
        self.calculate_clock_difference()
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
            "Las sincronizaciones históricas no pueden archivarse."
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        raise ValidationError(
            "Las sincronizaciones históricas no pueden restaurarse."
        )