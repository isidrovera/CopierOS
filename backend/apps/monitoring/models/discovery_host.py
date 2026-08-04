# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models

from .base import MonitoringBaseModel


class DiscoveryHost(MonitoringBaseModel):
    """
    Resultado histórico del análisis de una dirección IP durante
    una ejecución de descubrimiento.

    Conserva cada host consultado, incluso cuando:

    - No respondió.
    - Fue excluido.
    - Respondió a red, pero no a SNMP.
    - La credencial SNMP fue incorrecta.
    - Se detectó un dispositivo que no era impresora.
    - Se encontró o actualizó un dispositivo monitoreado.
    """

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        EXCLUDED = (
            "excluded",
            "Excluido",
        )
        UNREACHABLE = (
            "unreachable",
            "Sin respuesta",
        )
        REACHABLE = (
            "reachable",
            "Con respuesta",
        )
        SNMP_RESPONDED = (
            "snmp_responded",
            "Respondió por SNMP",
        )
        IDENTIFIED = (
            "identified",
            "Identificado",
        )
        NOT_PRINTER = (
            "not_printer",
            "No es impresora",
        )
        AUTHENTICATION_ERROR = (
            "authentication_error",
            "Error de autenticación",
        )
        TIMEOUT = (
            "timeout",
            "Tiempo de espera agotado",
        )
        NETWORK_ERROR = (
            "network_error",
            "Error de red",
        )
        ERROR = (
            "error",
            "Con error",
        )

    class DetectionType(models.TextChoices):
        UNKNOWN = (
            "unknown",
            "Desconocido",
        )
        PRINTER = (
            "printer",
            "Impresora",
        )
        MULTIFUNCTION = (
            "multifunction",
            "Multifuncional",
        )
        SCANNER = (
            "scanner",
            "Escáner",
        )
        FAX = (
            "fax",
            "Fax",
        )
        PRINT_SERVER = (
            "print_server",
            "Servidor de impresión",
        )
        NETWORK_DEVICE = (
            "network_device",
            "Dispositivo de red",
        )
        COMPUTER = (
            "computer",
            "Computadora",
        )
        SERVER = (
            "server",
            "Servidor",
        )
        OTHER = (
            "other",
            "Otro",
        )

    class DeviceAction(models.TextChoices):
        NONE = (
            "none",
            "Sin acción",
        )
        CREATED = (
            "created",
            "Dispositivo creado",
        )
        UPDATED = (
            "updated",
            "Dispositivo actualizado",
        )
        REACTIVATED = (
            "reactivated",
            "Dispositivo reactivado",
        )
        DUPLICATE = (
            "duplicate",
            "Posible duplicado",
        )
        IGNORED = (
            "ignored",
            "Ignorado",
        )

    discovery = models.ForeignKey(
        "monitoring.MonitoringDiscovery",
        on_delete=models.PROTECT,
        related_name="hosts",
        verbose_name="Descubrimiento",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        on_delete=models.PROTECT,
        related_name="discovery_hosts",
        verbose_name="Agente",
    )

    network = models.ForeignKey(
        "monitoring.MonitoringNetwork",
        on_delete=models.PROTECT,
        related_name="discovery_hosts",
        verbose_name="Red",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_discovery_hosts",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_discovery_hosts",
        verbose_name="Sede",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="discovery_results",
        verbose_name="Dispositivo identificado",
    )

    successful_credential = models.ForeignKey(
        "monitoring.SNMPCredential",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="successful_discovery_hosts",
        verbose_name="Credencial correcta",
    )

    ip_address = models.GenericIPAddressField(
        protocol="both",
        unpack_ipv4=True,
        db_index=True,
        verbose_name="Dirección IP",
    )

    status = models.CharField(
        max_length=40,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    detection_type = models.CharField(
        max_length=30,
        choices=DetectionType.choices,
        default=DetectionType.UNKNOWN,
        db_index=True,
        verbose_name="Tipo detectado",
    )

    device_action = models.CharField(
        max_length=20,
        choices=DeviceAction.choices,
        default=DeviceAction.NONE,
        db_index=True,
        verbose_name="Acción realizada",
    )

    is_excluded = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Host excluido",
    )

    exclusion_reason = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Motivo de exclusión",
    )

    network_reachable = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Respondió en red",
    )

    ping_attempted = models.BooleanField(
        default=False,
        verbose_name="Ping intentado",
    )

    ping_successful = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Ping correcto",
    )

    ping_response_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo de ping en milisegundos",
    )

    tcp_probe_attempted = models.BooleanField(
        default=False,
        verbose_name="Prueba TCP realizada",
    )

    open_tcp_ports = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Puertos TCP abiertos",
    )

    snmp_attempted = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="SNMP intentado",
    )

    snmp_responded = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Respondió por SNMP",
    )

    snmp_port = models.PositiveIntegerField(
        default=161,
        verbose_name="Puerto SNMP",
    )

    snmp_version = models.CharField(
        max_length=10,
        blank=True,
        db_index=True,
        verbose_name="Versión SNMP",
    )

    snmp_response_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo SNMP en milisegundos",
    )

    credential_attempt_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Credenciales probadas",
    )

    credential_attempts = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Resultado de credenciales",
        help_text=(
            "Solo debe almacenar identificadores, versiones, "
            "tiempos y resultados. Nunca secretos SNMP."
        ),
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

    mac_address = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Dirección MAC",
    )

    mac_vendor = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Fabricante de la MAC",
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

    enterprise_number = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Número enterprise",
    )

    detected_brand = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Marca detectada",
    )

    detected_model = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Modelo detectado",
    )

    detected_serial_number = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Serie detectada",
    )

    detected_firmware = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Firmware detectado",
    )

    is_printer_candidate = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Candidato a impresora",
    )

    is_confirmed_printer = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Impresora confirmada",
    )

    printer_confidence_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Confianza de identificación",
    )

    printer_detection_reasons = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Razones de identificación",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio de consulta",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin de consulta",
    )

    duration_ms = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración en milisegundos",
    )

    timeout_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Tiempos de espera agotados",
    )

    authentication_error_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Errores de autenticación",
    )

    network_error_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Errores de red",
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

    raw_identification = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Identificación original",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Host de descubrimiento"
        verbose_name_plural = "Hosts de descubrimiento"
        ordering = (
            "ip_address",
        )
        indexes = [
            models.Index(
                fields=[
                    "discovery",
                    "status",
                ],
                name="mon_host_disc_status_idx",
            ),
            models.Index(
                fields=[
                    "customer",
                    "ip_address",
                    "created_at",
                ],
                name="mon_host_customer_ip_idx",
            ),
            models.Index(
                fields=[
                    "network",
                    "snmp_responded",
                    "created_at",
                ],
                name="mon_host_network_snmp_idx",
            ),
            models.Index(
                fields=[
                    "is_confirmed_printer",
                    "device_action",
                    "created_at",
                ],
                name="mon_host_printer_action_idx",
            ),
            models.Index(
                fields=[
                    "sys_object_id",
                    "enterprise_number",
                ],
                name="mon_host_identity_idx",
            ),
            models.Index(
                fields=[
                    "detected_serial_number",
                    "mac_address",
                ],
                name="mon_host_serial_mac_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "discovery",
                    "ip_address",
                ],
                name="unique_discovery_host_ip",
            ),
        ]

    def __str__(self):
        return (
            f"{self.discovery} - "
            f"{self.ip_address} - "
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

    def mark_excluded(
        self,
        reason="",
    ):
        self.is_excluded = True
        self.status = self.Status.EXCLUDED
        self.exclusion_reason = str(
            reason or ""
        ).strip()

        self.network_reachable = False
        self.snmp_attempted = False
        self.snmp_responded = False

        self.save(
            update_fields=[
                "is_excluded",
                "status",
                "exclusion_reason",
                "network_reachable",
                "snmp_attempted",
                "snmp_responded",
                "updated_at",
            ]
        )

    def register_network_result(
        self,
        *,
        reachable,
        ping_attempted=False,
        ping_successful=False,
        ping_response_time_ms=None,
        tcp_probe_attempted=False,
        open_tcp_ports=None,
    ):
        self.network_reachable = bool(reachable)
        self.ping_attempted = bool(ping_attempted)
        self.ping_successful = bool(ping_successful)
        self.ping_response_time_ms = ping_response_time_ms
        self.tcp_probe_attempted = bool(tcp_probe_attempted)

        if open_tcp_ports is not None:
            self.open_tcp_ports = open_tcp_ports

        self.status = (
            self.Status.REACHABLE
            if self.network_reachable
            else self.Status.UNREACHABLE
        )

        self.save(
            update_fields=[
                "network_reachable",
                "ping_attempted",
                "ping_successful",
                "ping_response_time_ms",
                "tcp_probe_attempted",
                "open_tcp_ports",
                "status",
                "updated_at",
            ]
        )

    def register_snmp_success(
        self,
        *,
        credential,
        snmp_version,
        snmp_port=161,
        response_time_ms=None,
        identification=None,
    ):
        self.snmp_attempted = True
        self.snmp_responded = True
        self.network_reachable = True
        self.status = self.Status.SNMP_RESPONDED

        self.successful_credential = credential
        self.snmp_version = str(
            snmp_version or ""
        ).strip()

        self.snmp_port = int(
            snmp_port or 161
        )

        self.snmp_response_time_ms = response_time_ms

        if identification:
            self.apply_identification(
                identification
            )

        self.save()

    def register_snmp_failure(
        self,
        *,
        status,
        error_code="",
        error_message="",
        response_time_ms=None,
    ):
        allowed_statuses = {
            self.Status.AUTHENTICATION_ERROR,
            self.Status.TIMEOUT,
            self.Status.NETWORK_ERROR,
            self.Status.ERROR,
        }

        if status not in allowed_statuses:
            raise ValidationError(
                "El estado indicado no representa un error SNMP."
            )

        self.snmp_attempted = True
        self.snmp_responded = False
        self.status = status
        self.snmp_response_time_ms = response_time_ms
        self.error_code = str(
            error_code or ""
        ).strip().upper()

        self.error_message = str(
            error_message or ""
        ).strip()

        if status == self.Status.AUTHENTICATION_ERROR:
            self.authentication_error_count += 1
        elif status == self.Status.TIMEOUT:
            self.timeout_count += 1
        elif status == self.Status.NETWORK_ERROR:
            self.network_error_count += 1

        self.save()

    def apply_identification(
        self,
        data,
    ):
        """
        Copia solamente campos permitidos desde la respuesta
        de identificación enviada por el agente.
        """

        data = data or {}

        field_map = {
            "hostname": "hostname",
            "dns_name": "dns_name",
            "mac_address": "mac_address",
            "mac_vendor": "mac_vendor",
            "sys_name": "sys_name",
            "sys_description": "sys_description",
            "sys_object_id": "sys_object_id",
            "sys_location": "sys_location",
            "enterprise_number": "enterprise_number",
            "brand": "detected_brand",
            "model": "detected_model",
            "serial_number": "detected_serial_number",
            "firmware": "detected_firmware",
            "detection_type": "detection_type",
            "is_printer_candidate": "is_printer_candidate",
            "is_confirmed_printer": "is_confirmed_printer",
            "printer_confidence_percent": (
                "printer_confidence_percent"
            ),
            "printer_detection_reasons": (
                "printer_detection_reasons"
            ),
        }

        for source_name, field_name in field_map.items():
            if source_name in data:
                setattr(
                    self,
                    field_name,
                    data[source_name],
                )

        self.raw_identification = data

        if self.is_confirmed_printer:
            self.status = self.Status.IDENTIFIED
        elif self.snmp_responded:
            self.status = self.Status.NOT_PRINTER

    def link_device(
        self,
        device,
        *,
        action,
    ):
        if device.agent_id != self.agent_id:
            raise ValidationError(
                "El dispositivo pertenece a otro agente."
            )

        if device.customer_id != self.customer_id:
            raise ValidationError(
                "El dispositivo pertenece a otro cliente."
            )

        self.device = device
        self.device_action = action

        if device.is_confirmed_printer:
            self.is_confirmed_printer = True
            self.is_printer_candidate = True
            self.status = self.Status.IDENTIFIED

        self.save(
            update_fields=[
                "device",
                "device_action",
                "is_confirmed_printer",
                "is_printer_candidate",
                "status",
                "updated_at",
            ]
        )

    def clean(self):
        super().clean()

        text_fields = [
            "exclusion_reason",
            "snmp_version",
            "hostname",
            "dns_name",
            "mac_address",
            "mac_vendor",
            "sys_name",
            "sys_description",
            "sys_object_id",
            "sys_location",
            "detected_brand",
            "detected_model",
            "detected_serial_number",
            "detected_firmware",
            "error_code",
            "error_message",
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

        self.mac_address = self.mac_address.upper()
        self.detected_serial_number = (
            self.detected_serial_number.upper()
        )
        self.error_code = self.error_code.upper()

        if not self.discovery_id:
            raise ValidationError(
                {
                    "discovery": (
                        "El descubrimiento es obligatorio."
                    ),
                }
            )

        if self.discovery.agent_id != self.agent_id:
            raise ValidationError(
                {
                    "agent": (
                        "El agente no coincide con "
                        "el descubrimiento."
                    ),
                }
            )

        if self.discovery.network_id != self.network_id:
            raise ValidationError(
                {
                    "network": (
                        "La red no coincide con "
                        "el descubrimiento."
                    ),
                }
            )

        if self.discovery.customer_id != self.customer_id:
            raise ValidationError(
                {
                    "customer": (
                        "El cliente no coincide con "
                        "el descubrimiento."
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
            self.successful_credential_id
            and self.successful_credential.customer_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "successful_credential": (
                        "La credencial no pertenece al cliente."
                    ),
                }
            )

        if (
            self.device_id
            and self.device.agent_id
            != self.agent_id
        ):
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo no pertenece al agente."
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

        if (
            self.printer_confidence_percent is not None
            and (
                self.printer_confidence_percent < 0
                or self.printer_confidence_percent > 100
            )
        ):
            raise ValidationError(
                {
                    "printer_confidence_percent": (
                        "La confianza debe estar "
                        "entre 0 y 100."
                    ),
                }
            )

        if self.is_excluded:
            self.status = self.Status.EXCLUDED
            self.snmp_attempted = False
            self.snmp_responded = False

        if self.snmp_responded:
            self.snmp_attempted = True
            self.network_reachable = True

        if self.is_confirmed_printer:
            self.is_printer_candidate = True

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

    def save(self, *args, **kwargs):
        if self.discovery_id:
            self.agent = self.discovery.agent
            self.network = self.discovery.network
            self.customer = self.discovery.customer
            self.branch = self.discovery.branch

        self.mac_address = str(
            self.mac_address or ""
        ).strip().upper()

        self.detected_serial_number = str(
            self.detected_serial_number or ""
        ).strip().upper()

        self.calculate_duration()
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
            "Los resultados históricos de descubrimiento "
            "no pueden archivarse."
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        raise ValidationError(
            "Los resultados históricos de descubrimiento "
            "no pueden restaurarse."
        )