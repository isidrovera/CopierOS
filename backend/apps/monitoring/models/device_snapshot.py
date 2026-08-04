# -*- coding: utf-8 -*-
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class DeviceSnapshot(MonitoringBaseModel):
    """
    Cabecera histórica de una lectura realizada a un dispositivo.

    Cada snapshot representa el estado completo del equipo en una
    fecha y hora determinada.

    No debe modificarse después de quedar procesado porque sirve
    como respaldo para reportes diarios, semanales, mensuales,
    anuales y rangos personalizados.
    """

    class SnapshotType(models.TextChoices):
        DISCOVERY = (
            "discovery",
            "Descubrimiento",
        )
        MONITORING = (
            "monitoring",
            "Monitoreo periódico",
        )
        FULL_INVENTORY = (
            "full_inventory",
            "Inventario completo",
        )
        DIAGNOSTIC = (
            "diagnostic",
            "Diagnóstico",
        )
        MANUAL = (
            "manual",
            "Lectura manual",
        )
        EVENT = (
            "event",
            "Lectura por evento",
        )

    class ProcessingStatus(models.TextChoices):
        RECEIVED = (
            "received",
            "Recibido",
        )
        PROCESSING = (
            "processing",
            "Procesando",
        )
        COMPLETED = (
            "completed",
            "Completado",
        )
        PARTIAL = (
            "partial",
            "Completado parcialmente",
        )
        ERROR = (
            "error",
            "Con error",
        )
        REJECTED = (
            "rejected",
            "Rechazado",
        )

    class ConnectionStatus(models.TextChoices):
        ONLINE = (
            "online",
            "En línea",
        )
        OFFLINE = (
            "offline",
            "Sin conexión",
        )
        TIMEOUT = (
            "timeout",
            "Tiempo de espera agotado",
        )
        AUTHENTICATION_ERROR = (
            "authentication_error",
            "Error de autenticación",
        )
        NETWORK_ERROR = (
            "network_error",
            "Error de red",
        )
        SNMP_ERROR = (
            "snmp_error",
            "Error SNMP",
        )
        UNKNOWN = (
            "unknown",
            "Desconocido",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        on_delete=models.PROTECT,
        related_name="snapshots",
        verbose_name="Dispositivo",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_snapshots",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_snapshots",
        verbose_name="Sede",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        on_delete=models.PROTECT,
        related_name="snapshots",
        verbose_name="Agente",
    )

    network = models.ForeignKey(
        "monitoring.MonitoringNetwork",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="snapshots",
        verbose_name="Red",
    )

    credential = models.ForeignKey(
        "monitoring.SNMPCredential",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="snapshots",
        verbose_name="Credencial SNMP utilizada",
    )

    snapshot_type = models.CharField(
        max_length=30,
        choices=SnapshotType.choices,
        default=SnapshotType.MONITORING,
        db_index=True,
        verbose_name="Tipo de captura",
    )

    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.RECEIVED,
        db_index=True,
        verbose_name="Estado de procesamiento",
    )

    connection_status = models.CharField(
        max_length=30,
        choices=ConnectionStatus.choices,
        default=ConnectionStatus.UNKNOWN,
        db_index=True,
        verbose_name="Estado de conexión",
    )

    captured_at = models.DateTimeField(
        db_index=True,
        verbose_name="Fecha y hora de captura",
    )

    received_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de recepción",
    )

    processing_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio de procesamiento",
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fin de procesamiento",
    )

    agent_snapshot_id = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Identificador generado por el agente",
        help_text=(
            "Permite evitar el registro duplicado de una captura "
            "reenviada desde la cola local."
        ),
    )

    sequence_number = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Número de secuencia del agente",
    )

    configuration_version = models.PositiveBigIntegerField(
        default=1,
        verbose_name="Versión de configuración del agente",
    )

    profile_version = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Versión del perfil SNMP",
    )

    ip_address = models.GenericIPAddressField(
        protocol="both",
        unpack_ipv4=True,
        db_index=True,
        verbose_name="Dirección IP durante la captura",
    )

    mac_address = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Dirección MAC durante la captura",
    )

    hostname = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Hostname durante la captura",
    )

    sys_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre SNMP",
    )

    sys_description = models.TextField(
        blank=True,
        verbose_name="Descripción SNMP",
    )

    sys_object_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="SysObjectID",
    )

    sys_location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Ubicación SNMP",
    )

    raw_brand_name = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Marca reportada",
    )

    raw_model_name = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Modelo reportado",
    )

    raw_serial_number = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Serie reportada",
    )

    firmware_version = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Firmware reportado",
    )

    operational_status = models.CharField(
        max_length=30,
        blank=True,
        db_index=True,
        verbose_name="Estado operativo",
    )

    printer_status = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Estado de impresión",
    )

    scanner_status = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Estado del escáner",
    )

    fax_status = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Estado del fax",
    )

    paper_status = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Estado de papel",
    )

    consumable_status = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Estado de consumibles",
    )

    maintenance_status = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Estado de mantenimiento",
    )

    network_status = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Estado de red",
    )

    device_uptime_seconds = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo encendido",
    )

    response_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo de respuesta en milisegundos",
    )

    total_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Contador total",
    )

    black_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador blanco y negro",
    )

    color_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador color",
    )

    scan_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador de escaneo",
    )

    active_alert_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Alertas activas",
    )

    critical_alert_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Alertas críticas",
    )

    counter_reading_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Contadores registrados",
    )

    consumable_reading_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Consumibles registrados",
    )

    component_reading_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Unidades registradas",
    )

    tray_reading_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Bandejas registradas",
    )

    accessory_reading_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Accesorios registrados",
    )

    job_reading_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Trabajos registrados",
    )

    raw_oid_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad de OID recibidos",
    )

    unknown_oid_count = models.PositiveIntegerField(
        default=0,
        verbose_name="OID no identificados",
    )

    raw_payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Información original recibida",
        help_text=(
            "Conserva la estructura original enviada por el agente "
            "para auditoría y reprocesamiento."
        ),
    )

    normalized_payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Información normalizada",
    )

    processing_error = models.TextField(
        blank=True,
        verbose_name="Error de procesamiento",
    )

    is_complete_inventory = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Inventario completo",
    )

    is_historical = models.BooleanField(
        default=True,
        editable=False,
        verbose_name="Registro histórico",
    )

    class Meta:
        verbose_name = "Captura de dispositivo"
        verbose_name_plural = "Capturas de dispositivos"
        ordering = (
            "-captured_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "captured_at",
                ],
                name="mon_snap_customer_date_idx",
            ),
            models.Index(
                fields=[
                    "branch",
                    "captured_at",
                ],
                name="mon_snap_branch_date_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "captured_at",
                ],
                name="mon_snap_device_date_idx",
            ),
            models.Index(
                fields=[
                    "snapshot_type",
                    "captured_at",
                ],
                name="mon_snap_type_date_idx",
            ),
            models.Index(
                fields=[
                    "processing_status",
                    "received_at",
                ],
                name="mon_snap_processing_idx",
            ),
            models.Index(
                fields=[
                    "operational_status",
                    "captured_at",
                ],
                name="mon_snap_operational_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "agent",
                    "agent_snapshot_id",
                ],
                name="unique_agent_snapshot_id",
            ),
        ]

    def __str__(self):
        return (
            f"{self.device} - "
            f"{self.captured_at:%Y-%m-%d %H:%M:%S}"
        )

    def mark_processing(self):
        if self.processing_status != self.ProcessingStatus.RECEIVED:
            raise ValidationError(
                "Solo una captura recibida puede iniciar "
                "su procesamiento."
            )

        self.processing_status = self.ProcessingStatus.PROCESSING
        self.processing_started_at = timezone.now()
        self.processing_error = ""

        self.save(
            update_fields=[
                "processing_status",
                "processing_started_at",
                "processing_error",
                "updated_at",
            ]
        )

    def mark_completed(
        self,
        *,
        partial=False,
        processing_error="",
    ):
        self.processing_status = (
            self.ProcessingStatus.PARTIAL
            if partial
            else self.ProcessingStatus.COMPLETED
        )

        self.processed_at = timezone.now()
        self.processing_error = str(
            processing_error or ""
        ).strip()

        self.save(
            update_fields=[
                "processing_status",
                "processed_at",
                "processing_error",
                "updated_at",
            ]
        )

    def mark_error(
        self,
        error_message,
    ):
        self.processing_status = self.ProcessingStatus.ERROR
        self.processed_at = timezone.now()
        self.processing_error = str(
            error_message or ""
        ).strip()

        self.save(
            update_fields=[
                "processing_status",
                "processed_at",
                "processing_error",
                "updated_at",
            ]
        )

    def refresh_related_counts(self):
        """
        Actualiza las cantidades de registros relacionados.

        Se ejecutará después de guardar los detalles de la captura.
        """

        self.counter_reading_count = (
            self.counter_readings.count()
        )

        self.consumable_reading_count = (
            self.consumable_readings.count()
        )

        self.component_reading_count = (
            self.component_readings.count()
        )

        self.tray_reading_count = (
            self.tray_readings.count()
        )

        self.accessory_reading_count = (
            self.accessory_readings.count()
        )

        self.job_reading_count = (
            self.job_readings.count()
        )

        self.active_alert_count = (
            self.alert_readings.filter(
                is_active=True,
            ).count()
        )

        self.critical_alert_count = (
            self.alert_readings.filter(
                is_active=True,
                severity="critical",
            ).count()
        )

        self.save(
            update_fields=[
                "counter_reading_count",
                "consumable_reading_count",
                "component_reading_count",
                "tray_reading_count",
                "accessory_reading_count",
                "job_reading_count",
                "active_alert_count",
                "critical_alert_count",
                "updated_at",
            ]
        )

    def clean(self):
        super().clean()

        text_fields = [
            "agent_snapshot_id",
            "profile_version",
            "mac_address",
            "hostname",
            "sys_name",
            "sys_description",
            "sys_object_id",
            "sys_location",
            "raw_brand_name",
            "raw_model_name",
            "raw_serial_number",
            "firmware_version",
            "operational_status",
            "printer_status",
            "scanner_status",
            "fax_status",
            "paper_status",
            "consumable_status",
            "maintenance_status",
            "network_status",
            "processing_error",
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

        self.mac_address = self.mac_address.upper()
        self.raw_serial_number = self.raw_serial_number.upper()

        if not self.device_id:
            raise ValidationError(
                {
                    "device": "El dispositivo es obligatorio.",
                }
            )

        if not self.customer_id:
            raise ValidationError(
                {
                    "customer": "El cliente es obligatorio.",
                }
            )

        if not self.agent_id:
            raise ValidationError(
                {
                    "agent": "El agente es obligatorio.",
                }
            )

        if self.device.customer_id != self.customer_id:
            raise ValidationError(
                {
                    "customer": (
                        "El cliente no coincide con el dispositivo."
                    ),
                }
            )

        if self.device.agent_id != self.agent_id:
            raise ValidationError(
                {
                    "agent": (
                        "El agente no coincide con el dispositivo."
                    ),
                }
            )

        if (
            self.branch_id
            and self.branch.partner_id != self.customer_id
        ):
            raise ValidationError(
                {
                    "branch": (
                        "La sede no pertenece al cliente."
                    ),
                }
            )

        if (
            self.network_id
            and self.network.agent_id != self.agent_id
        ):
            raise ValidationError(
                {
                    "network": (
                        "La red no pertenece al agente."
                    ),
                }
            )

        if (
            self.credential_id
            and self.credential.customer_id != self.customer_id
        ):
            raise ValidationError(
                {
                    "credential": (
                        "La credencial no pertenece al cliente."
                    ),
                }
            )

        if not self.agent_snapshot_id:
            raise ValidationError(
                {
                    "agent_snapshot_id": (
                        "El identificador de captura es obligatorio."
                    ),
                }
            )

        if not self.captured_at:
            raise ValidationError(
                {
                    "captured_at": (
                        "La fecha de captura es obligatoria."
                    ),
                }
            )

        if (
            self.processing_started_at
            and self.processing_started_at < self.received_at
        ):
            raise ValidationError(
                {
                    "processing_started_at": (
                        "El procesamiento no puede comenzar antes "
                        "de recibir la captura."
                    ),
                }
            )

        if (
            self.processed_at
            and self.processing_started_at
            and self.processed_at < self.processing_started_at
        ):
            raise ValidationError(
                {
                    "processed_at": (
                        "La finalización no puede ser anterior "
                        "al inicio del procesamiento."
                    ),
                }
            )

        if self.response_time_ms is not None:
            if self.response_time_ms > 600000:
                raise ValidationError(
                    {
                        "response_time_ms": (
                            "El tiempo de respuesta no puede superar "
                            "los diez minutos."
                        ),
                    }
                )

    def save(self, *args, **kwargs):
        if self.device_id:
            self.customer = self.device.customer
            self.branch = self.device.branch
            self.agent = self.device.agent
            self.network = self.device.network

            if not self.ip_address:
                self.ip_address = self.device.ip_address

        self.agent_snapshot_id = str(
            self.agent_snapshot_id or ""
        ).strip()

        self.mac_address = str(
            self.mac_address or ""
        ).strip().upper()

        self.raw_serial_number = str(
            self.raw_serial_number or ""
        ).strip().upper()

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
            "Las capturas históricas no pueden archivarse."
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        raise ValidationError(
            "Las capturas históricas no pueden restaurarse."
        )