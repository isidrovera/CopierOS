# -*- coding: utf-8 -*-
import hashlib
import secrets

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class MonitoredDevice(MonitoringBaseModel):
    """
    Dispositivo descubierto y monitoreado por un agente.

    Puede existir sin estar vinculado inicialmente a Equipment.
    Una vez identificada la serie o validado manualmente, se
    relaciona con la máquina física registrada en Copier OS.
    """

    class DeviceStatus(models.TextChoices):
        DISCOVERED = (
            "discovered",
            "Descubierto",
        )
        IDENTIFYING = (
            "identifying",
            "Identificando",
        )
        ACTIVE = (
            "active",
            "Activo",
        )
        OFFLINE = (
            "offline",
            "Sin conexión",
        )
        WARNING = (
            "warning",
            "Con advertencias",
        )
        ERROR = (
            "error",
            "Con error",
        )
        BLOCKED = (
            "blocked",
            "Bloqueado",
        )
        IGNORED = (
            "ignored",
            "Ignorado",
        )
        REPLACED = (
            "replaced",
            "Reemplazado",
        )

    class OperationalStatus(models.TextChoices):
        UNKNOWN = (
            "unknown",
            "Desconocido",
        )
        READY = (
            "ready",
            "Listo",
        )
        PRINTING = (
            "printing",
            "Imprimiendo",
        )
        COPYING = (
            "copying",
            "Copiando",
        )
        SCANNING = (
            "scanning",
            "Escaneando",
        )
        FAXING = (
            "faxing",
            "Transmitiendo fax",
        )
        WARMING_UP = (
            "warming_up",
            "Calentando",
        )
        ENERGY_SAVING = (
            "energy_saving",
            "Ahorro de energía",
        )
        MAINTENANCE = (
            "maintenance",
            "En mantenimiento",
        )
        WARNING = (
            "warning",
            "Con advertencia",
        )
        ERROR = (
            "error",
            "Con error",
        )
        BLOCKED = (
            "blocked",
            "Operación bloqueada",
        )
        OFFLINE = (
            "offline",
            "Sin conexión",
        )

    class IdentificationStatus(models.TextChoices):
        UNKNOWN = (
            "unknown",
            "No identificado",
        )
        PARTIAL = (
            "partial",
            "Identificación parcial",
        )
        AUTOMATIC = (
            "automatic",
            "Identificado automáticamente",
        )
        MANUAL = (
            "manual",
            "Identificado manualmente",
        )
        CONFLICT = (
            "conflict",
            "Identificación en conflicto",
        )

    class LinkStatus(models.TextChoices):
        UNLINKED = (
            "unlinked",
            "Sin vincular",
        )
        SUGGESTED = (
            "suggested",
            "Vinculación sugerida",
        )
        LINKED_AUTOMATIC = (
            "linked_automatic",
            "Vinculado automáticamente",
        )
        LINKED_MANUAL = (
            "linked_manual",
            "Vinculado manualmente",
        )
        CONFLICT = (
            "conflict",
            "Conflicto de vinculación",
        )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitored_devices",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitored_devices",
        verbose_name="Sede",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        on_delete=models.PROTECT,
        related_name="monitored_devices",
        verbose_name="Agente",
    )

    network = models.ForeignKey(
        "monitoring.MonitoringNetwork",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitored_devices",
        verbose_name="Red",
    )

    snmp_credential = models.ForeignKey(
        "monitoring.SNMPCredential",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitored_devices",
        verbose_name="Credencial SNMP válida",
    )

    equipment = models.OneToOneField(
        "equipment.Equipment",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_device",
        verbose_name="Equipo vinculado",
    )

    suggested_equipment = models.ForeignKey(
        "equipment.Equipment",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="suggested_monitoring_devices",
        verbose_name="Equipo sugerido",
    )

    detected_brand = models.ForeignKey(
        "equipment.EquipmentBrand",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="detected_monitoring_devices",
        verbose_name="Marca detectada",
    )

    detected_model = models.ForeignKey(
        "equipment.EquipmentModel",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="detected_monitoring_devices",
        verbose_name="Modelo detectado",
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False,
        verbose_name="Código",
    )

    device_key = models.CharField(
        max_length=80,
        unique=True,
        db_index=True,
        editable=False,
        verbose_name="Clave permanente del dispositivo",
    )

    identity_fingerprint = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        editable=False,
        verbose_name="Huella de identidad",
    )

    status = models.CharField(
        max_length=30,
        choices=DeviceStatus.choices,
        default=DeviceStatus.DISCOVERED,
        db_index=True,
        verbose_name="Estado de monitoreo",
    )

    operational_status = models.CharField(
        max_length=30,
        choices=OperationalStatus.choices,
        default=OperationalStatus.UNKNOWN,
        db_index=True,
        verbose_name="Estado operativo",
    )

    identification_status = models.CharField(
        max_length=30,
        choices=IdentificationStatus.choices,
        default=IdentificationStatus.UNKNOWN,
        db_index=True,
        verbose_name="Estado de identificación",
    )

    link_status = models.CharField(
        max_length=30,
        choices=LinkStatus.choices,
        default=LinkStatus.UNLINKED,
        db_index=True,
        verbose_name="Estado de vinculación",
    )

    ip_address = models.GenericIPAddressField(
        protocol="both",
        unpack_ipv4=True,
        db_index=True,
        verbose_name="Dirección IP",
    )

    snmp_port = models.PositiveIntegerField(
        default=161,
        verbose_name="Puerto SNMP",
    )

    snmp_version = models.CharField(
        max_length=10,
        blank=True,
        db_index=True,
        verbose_name="Versión SNMP detectada",
    )

    mac_address = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Dirección MAC",
    )

    hostname = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Hostname",
    )

    dns_name = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Nombre DNS",
    )

    sys_name = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
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

    sys_contact = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Contacto SNMP",
    )

    enterprise_number = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Número enterprise",
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

    product_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de producto",
    )

    asset_number = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código patrimonial reportado",
    )

    firmware_version = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Firmware principal",
    )

    controller_firmware_version = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Firmware del controlador",
    )

    engine_firmware_version = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Firmware del motor",
    )

    scanner_firmware_version = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Firmware del escáner",
    )

    device_uptime_seconds = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo encendido en segundos",
    )

    device_datetime = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha y hora del dispositivo",
    )

    timezone_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Zona horaria reportada",
    )

    site_location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Ubicación administrativa",
        help_text=(
            "Piso, oficina, área o punto exacto de instalación."
        ),
    )

    is_color = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Equipo color",
    )

    is_multifunction = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Equipo multifunción",
    )

    supports_printing = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Permite impresión",
    )

    supports_copying = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Permite copia",
    )

    supports_scanning = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Permite escaneo",
    )

    supports_fax = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Permite fax",
    )

    supports_duplex = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Permite dúplex",
    )

    supports_job_monitoring = models.BooleanField(
        default=False,
        verbose_name="Permite monitoreo de trabajos",
    )

    supports_component_monitoring = models.BooleanField(
        default=False,
        verbose_name="Permite monitoreo de unidades",
    )

    supports_accessory_inventory = models.BooleanField(
        default=False,
        verbose_name="Permite inventario de accesorios",
    )

    active_alert_count = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Alertas activas",
    )

    critical_alert_count = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Alertas críticas",
    )

    current_total_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Contador total actual",
    )

    current_black_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador B/N actual",
    )

    current_color_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador color actual",
    )

    current_scan_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador de escaneo actual",
    )

    discovered_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de descubrimiento",
    )

    first_successful_snmp_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Primera respuesta SNMP",
    )

    last_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Última conexión",
    )

    last_snmp_success_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Última respuesta SNMP",
    )

    last_snmp_failure_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último error SNMP",
    )

    last_inventory_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último inventario completo",
    )

    last_snapshot_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Última captura histórica",
    )

    last_ip_change_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último cambio de IP",
    )

    last_firmware_change_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último cambio de firmware",
    )

    consecutive_failure_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Errores consecutivos",
    )

    last_error_message = models.TextField(
        blank=True,
        verbose_name="Último error",
    )

    monitoring_enabled = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Monitoreo habilitado",
    )

    inventory_enabled = models.BooleanField(
        default=True,
        verbose_name="Inventario habilitado",
    )

    alert_monitoring_enabled = models.BooleanField(
        default=True,
        verbose_name="Alertas habilitadas",
    )

    job_monitoring_enabled = models.BooleanField(
        default=False,
        verbose_name="Trabajos habilitados",
    )

    is_confirmed_printer = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Confirmado como impresora",
    )

    is_ignored = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Ignorado",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Dispositivo monitoreado"
        verbose_name_plural = "Dispositivos monitoreados"
        ordering = (
            "customer",
            "branch",
            "ip_address",
        )
        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "branch",
                    "status",
                ],
                name="mon_dev_customer_status_idx",
            ),
            models.Index(
                fields=[
                    "agent",
                    "network",
                    "status",
                ],
                name="mon_dev_agent_network_idx",
            ),
            models.Index(
                fields=[
                    "raw_serial_number",
                    "mac_address",
                ],
                name="mon_dev_serial_mac_idx",
            ),
            models.Index(
                fields=[
                    "operational_status",
                    "last_seen_at",
                ],
                name="mon_dev_operational_seen_idx",
            ),
            models.Index(
                fields=[
                    "monitoring_enabled",
                    "last_snapshot_at",
                ],
                name="mon_dev_monitor_snapshot_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "agent",
                    "ip_address",
                    "snmp_port",
                ],
                condition=models.Q(
                    archived_at__isnull=True,
                    is_ignored=False,
                ),
                name="unique_active_agent_device_ip",
            ),
        ]

    def __str__(self):
        identity = (
            self.raw_model_name
            or self.sys_name
            or self.hostname
            or str(self.ip_address)
        )

        return (
            f"{self.code} - "
            f"{identity}"
        )

    @classmethod
    def generate_code(cls):
        while True:
            code = (
                f"DEV-"
                f"{secrets.token_hex(5).upper()}"
            )

            if not cls.objects.filter(
                code=code,
            ).exists():
                return code

    @classmethod
    def generate_device_key(cls):
        while True:
            key = (
                f"cpos_device_"
                f"{secrets.token_urlsafe(24)}"
            )

            if not cls.objects.filter(
                device_key=key,
            ).exists():
                return key

    def calculate_identity_fingerprint(self):
        """
        Crea una huella para sugerir coincidencias.

        La huella no reemplaza la validación manual porque algunos
        fabricantes no publican la serie o cambian sus valores.
        """

        values = [
            str(self.customer_id or ""),
            str(self.raw_serial_number or "").strip().upper(),
            str(self.mac_address or "").strip().upper(),
            str(self.sys_object_id or "").strip(),
            str(self.raw_model_name or "").strip().upper(),
        ]

        if not any(values[1:]):
            return ""

        return hashlib.sha256(
            "|".join(values).encode("utf-8")
        ).hexdigest()

    def refresh_identity_fingerprint(self):
        self.identity_fingerprint = (
            self.calculate_identity_fingerprint()
        )

    def register_snmp_success(
        self,
        *,
        credential=None,
        operational_status=None,
    ):
        now = timezone.now()

        self.last_seen_at = now
        self.last_snmp_success_at = now
        self.consecutive_failure_count = 0
        self.last_error_message = ""

        if not self.first_successful_snmp_at:
            self.first_successful_snmp_at = now

        if credential:
            self.snmp_credential = credential
            self.snmp_version = credential.snmp_version
            self.snmp_port = credential.port

        if operational_status:
            self.operational_status = operational_status

        if self.status in {
            self.DeviceStatus.DISCOVERED,
            self.DeviceStatus.IDENTIFYING,
            self.DeviceStatus.OFFLINE,
            self.DeviceStatus.ERROR,
        }:
            self.status = self.DeviceStatus.ACTIVE

        self.save(
            update_fields=[
                "last_seen_at",
                "last_snmp_success_at",
                "first_successful_snmp_at",
                "consecutive_failure_count",
                "last_error_message",
                "snmp_credential",
                "snmp_version",
                "snmp_port",
                "operational_status",
                "status",
                "updated_at",
            ]
        )

    def register_snmp_failure(
        self,
        error_message,
        *,
        offline_after_failures=3,
    ):
        self.last_snmp_failure_at = timezone.now()
        self.consecutive_failure_count += 1
        self.last_error_message = str(
            error_message or ""
        ).strip()

        if (
            self.consecutive_failure_count
            >= offline_after_failures
        ):
            self.status = self.DeviceStatus.OFFLINE
            self.operational_status = (
                self.OperationalStatus.OFFLINE
            )

        self.save(
            update_fields=[
                "last_snmp_failure_at",
                "consecutive_failure_count",
                "last_error_message",
                "status",
                "operational_status",
                "updated_at",
            ]
        )

    def link_equipment(
        self,
        equipment,
        *,
        automatic=False,
        user=None,
    ):
        if equipment.customer_id:
            if equipment.customer_id != self.customer_id:
                raise ValidationError(
                    "El equipo pertenece a otro cliente."
                )

        if equipment.customer_branch_id:
            if (
                self.branch_id
                and equipment.customer_branch_id
                != self.branch_id
            ):
                raise ValidationError(
                    "El equipo pertenece a otra sede."
                )

        existing = MonitoredDevice.objects.filter(
            equipment=equipment,
            archived_at__isnull=True,
        ).exclude(
            pk=self.pk,
        )

        if existing.exists():
            raise ValidationError(
                "El equipo ya está vinculado a otro "
                "dispositivo monitoreado."
            )

        self.equipment = equipment
        self.suggested_equipment = None
        self.link_status = (
            self.LinkStatus.LINKED_AUTOMATIC
            if automatic
            else self.LinkStatus.LINKED_MANUAL
        )

        if user:
            self.updated_by = user

        self.save(
            update_fields=[
                "equipment",
                "suggested_equipment",
                "link_status",
                "updated_by",
                "updated_at",
            ]
        )

    def unlink_equipment(
        self,
        *,
        user=None,
    ):
        self.equipment = None
        self.link_status = self.LinkStatus.UNLINKED

        if user:
            self.updated_by = user

        self.save(
            update_fields=[
                "equipment",
                "link_status",
                "updated_by",
                "updated_at",
            ]
        )

    def clean(self):
        super().clean()

        text_fields = [
            "code",
            "device_key",
            "mac_address",
            "hostname",
            "dns_name",
            "sys_name",
            "sys_description",
            "sys_object_id",
            "sys_location",
            "sys_contact",
            "raw_brand_name",
            "raw_model_name",
            "raw_serial_number",
            "product_code",
            "asset_number",
            "firmware_version",
            "controller_firmware_version",
            "engine_firmware_version",
            "scanner_firmware_version",
            "timezone_name",
            "site_location",
            "snmp_version",
            "last_error_message",
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

        self.code = self.code.upper()
        self.mac_address = self.mac_address.upper()
        self.raw_serial_number = (
            self.raw_serial_number.upper()
        )
        self.asset_number = self.asset_number.upper()

        if not self.customer_id:
            raise ValidationError(
                {
                    "customer": "El cliente es obligatorio.",
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
            self.agent_id
            and self.agent.customer_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "agent": (
                        "El agente no pertenece al cliente."
                    ),
                }
            )

        if (
            self.network_id
            and self.network.agent_id
            != self.agent_id
        ):
            raise ValidationError(
                {
                    "network": (
                        "La red no pertenece al agente."
                    ),
                }
            )

        if (
            self.snmp_credential_id
            and self.snmp_credential.customer_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "snmp_credential": (
                        "La credencial no pertenece al cliente."
                    ),
                }
            )

        if (
            self.equipment_id
            and self.equipment.customer_id
            and self.equipment.customer_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "equipment": (
                        "El equipo vinculado pertenece "
                        "a otro cliente."
                    ),
                }
            )

        if self.snmp_port < 1 or self.snmp_port > 65535:
            raise ValidationError(
                {
                    "snmp_port": (
                        "El puerto SNMP debe estar "
                        "entre 1 y 65535."
                    ),
                }
            )

        if self.is_ignored:
            self.status = self.DeviceStatus.IGNORED
            self.monitoring_enabled = False
            self.inventory_enabled = False
            self.alert_monitoring_enabled = False
            self.job_monitoring_enabled = False

        self.refresh_identity_fingerprint()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()

        if not self.device_key:
            self.device_key = (
                self.generate_device_key()
            )

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.mac_address = str(
            self.mac_address or ""
        ).strip().upper()

        self.raw_serial_number = str(
            self.raw_serial_number or ""
        ).strip().upper()

        self.asset_number = str(
            self.asset_number or ""
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
        self.monitoring_enabled = False
        self.inventory_enabled = False
        self.alert_monitoring_enabled = False
        self.job_monitoring_enabled = False

        if save:
            self.save(
                update_fields=[
                    "monitoring_enabled",
                    "inventory_enabled",
                    "alert_monitoring_enabled",
                    "job_monitoring_enabled",
                    "updated_at",
                ]
            )

        return super().archive(
            user=user,
            reason=reason,
            save=save,
        )