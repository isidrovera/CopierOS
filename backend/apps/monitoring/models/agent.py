# -*- coding: utf-8 -*-
import hashlib
import hmac
import secrets

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class MonitoringAgent(MonitoringBaseModel):
    """
    Agente instalado dentro de la red de un cliente.

    El agente:

    - Se registra usando un token de instalación.
    - Pertenece a un cliente y opcionalmente a una sede.
    - Recibe una credencial permanente propia.
    - Descubre y monitorea varias redes autorizadas.
    - Envía lecturas, alertas e inventario al servidor.
    """

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente de activación",
        )
        ACTIVE = (
            "active",
            "Activo",
        )
        OFFLINE = (
            "offline",
            "Sin conexión",
        )
        SUSPENDED = (
            "suspended",
            "Suspendido",
        )
        REVOKED = (
            "revoked",
            "Revocado",
        )
        ERROR = (
            "error",
            "Con error",
        )

    class OperatingSystem(models.TextChoices):
        WINDOWS = (
            "windows",
            "Windows",
        )
        LINUX = (
            "linux",
            "Linux",
        )
        MACOS = (
            "macos",
            "macOS",
        )
        OTHER = (
            "other",
            "Otro",
        )
        UNKNOWN = (
            "unknown",
            "No identificado",
        )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_agents",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_agents",
        verbose_name="Sede",
    )

    installation_token = models.ForeignKey(
        "monitoring.MonitoringInstallationToken",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="registered_agents",
        verbose_name="Token de instalación utilizado",
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False,
        verbose_name="Código del agente",
    )

    name = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Nombre del agente",
        help_text=(
            "Ejemplo: Agente sede principal Lima."
        ),
    )

    device_identifier = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name="Identificador de instalación",
        help_text=(
            "Identificador único generado por la instalación "
            "del agente en el equipo local."
        ),
    )

    credential_prefix = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        editable=False,
        verbose_name="Prefijo de credencial",
    )

    credential_hash = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        verbose_name="Hash de credencial",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    operating_system = models.CharField(
        max_length=20,
        choices=OperatingSystem.choices,
        default=OperatingSystem.UNKNOWN,
        db_index=True,
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
        help_text="Ejemplo: x86_64, amd64 o arm64.",
    )

    hostname = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Hostname del equipo agente",
    )

    agent_version = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Versión del agente",
    )

    local_ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        protocol="both",
        unpack_ipv4=True,
        db_index=True,
        verbose_name="IP local principal",
    )

    public_ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        protocol="both",
        unpack_ipv4=True,
        db_index=True,
        verbose_name="IP pública observada",
    )

    mac_address = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Dirección MAC del agente",
    )

    timezone_name = models.CharField(
        max_length=100,
        default="America/Lima",
        verbose_name="Zona horaria",
    )

    server_base_url = models.URLField(
        blank=True,
        verbose_name="Servidor asignado",
        help_text=(
            "Dirección del servidor Copier OS al cual "
            "el agente debe enviar información."
        ),
    )

    heartbeat_interval_seconds = models.PositiveIntegerField(
        default=60,
        verbose_name="Intervalo de conexión",
        help_text=(
            "Frecuencia en segundos con la que el agente "
            "informa que continúa operativo."
        ),
    )

    discovery_interval_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name="Intervalo de descubrimiento",
    )

    monitoring_interval_minutes = models.PositiveIntegerField(
        default=5,
        verbose_name="Intervalo de monitoreo",
    )

    full_inventory_interval_hours = models.PositiveIntegerField(
        default=24,
        verbose_name="Intervalo de inventario completo",
    )

    configuration_version = models.PositiveBigIntegerField(
        default=1,
        verbose_name="Versión de configuración",
    )

    last_configuration_sync_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última sincronización de configuración",
    )

    registered_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de registro",
    )

    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de activación",
    )

    last_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Última conexión",
    )

    last_successful_sync_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último envío correcto",
    )

    last_error_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha del último error",
    )

    last_error_message = models.TextField(
        blank=True,
        verbose_name="Último error",
    )

    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        editable=False,
        verbose_name="Fecha de revocación",
    )

    revoked_reason = models.TextField(
        blank=True,
        editable=False,
        verbose_name="Motivo de revocación",
    )

    supports_snmp_v1 = models.BooleanField(
        default=True,
        verbose_name="Permite SNMP v1",
    )

    supports_snmp_v2c = models.BooleanField(
        default=True,
        verbose_name="Permite SNMP v2c",
    )

    supports_snmp_v3 = models.BooleanField(
        default=False,
        verbose_name="Permite SNMP v3",
    )

    supports_websocket = models.BooleanField(
        default=False,
        verbose_name="Permite WebSocket",
    )

    supports_local_queue = models.BooleanField(
        default=True,
        verbose_name="Permite cola local",
    )

    is_enabled = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Habilitado",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Agente de monitoreo"
        verbose_name_plural = "Agentes de monitoreo"
        ordering = (
            "customer",
            "branch",
            "name",
        )
        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "branch",
                    "status",
                ],
                name="mon_agent_customer_branch_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "last_seen_at",
                ],
                name="mon_agent_status_seen_idx",
            ),
            models.Index(
                fields=[
                    "is_enabled",
                    "status",
                ],
                name="mon_agent_enabled_status_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "customer",
                    "device_identifier",
                ],
                condition=models.Q(
                    archived_at__isnull=True,
                ),
                name="unique_customer_agent_device",
            ),
        ]

    def __str__(self):
        location = str(
            self.customer
        )

        if self.branch_id:
            location = (
                f"{location} - "
                f"{self.branch}"
            )

        return (
            f"{self.code} - "
            f"{self.name} - "
            f"{location}"
        )

    @staticmethod
    def hash_credential(raw_credential):
        value = str(
            raw_credential or ""
        ).strip()

        return hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()

    @classmethod
    def generate_agent_code(cls):
        while True:
            code = (
                f"AGT-"
                f"{secrets.token_hex(5).upper()}"
            )

            if not cls.objects.filter(
                code=code,
            ).exists():
                return code

    @classmethod
    def generate_credential_value(cls):
        while True:
            credential_prefix = (
                f"cpos_agent_"
                f"{secrets.token_hex(4)}"
            )

            if not cls.objects.filter(
                credential_prefix=credential_prefix,
            ).exists():
                break

        secret_part = secrets.token_urlsafe(
            40
        )

        raw_credential = (
            f"{credential_prefix}_"
            f"{secret_part}"
        )

        return (
            raw_credential,
            credential_prefix,
            cls.hash_credential(
                raw_credential
            ),
        )

    @classmethod
    def register_agent(
        cls,
        *,
        installation_token,
        device_identifier,
        name,
        hostname="",
        operating_system=OperatingSystem.UNKNOWN,
        operating_system_version="",
        architecture="",
        agent_version="",
        local_ip_address=None,
        mac_address="",
        server_base_url="",
    ):
        """
        Registra un agente usando un token previamente validado.

        Devuelve:

        - Agente creado.
        - Credencial completa que se muestra una sola vez.
        """

        if not installation_token.can_be_used:
            raise ValidationError(
                "El token de instalación no puede utilizarse."
            )

        existing_agent = cls.objects.filter(
            customer=installation_token.customer,
            device_identifier__iexact=str(
                device_identifier or ""
            ).strip(),
            archived_at__isnull=True,
        ).first()

        if existing_agent:
            raise ValidationError(
                "Esta instalación ya tiene un agente registrado."
            )

        (
            raw_credential,
            credential_prefix,
            credential_hash,
        ) = cls.generate_credential_value()

        agent = cls(
            customer=installation_token.customer,
            branch=installation_token.branch,
            installation_token=installation_token,
            code=cls.generate_agent_code(),
            name=name,
            device_identifier=device_identifier,
            credential_prefix=credential_prefix,
            credential_hash=credential_hash,
            status=cls.Status.ACTIVE,
            hostname=hostname,
            operating_system=operating_system,
            operating_system_version=(
                operating_system_version
            ),
            architecture=architecture,
            agent_version=agent_version,
            local_ip_address=local_ip_address,
            mac_address=mac_address,
            server_base_url=server_base_url,
            activated_at=timezone.now(),
            last_seen_at=timezone.now(),
        )

        agent.save()

        installation_token.register_use()

        return agent, raw_credential

    @classmethod
    def authenticate_credential(
        cls,
        raw_credential,
    ):
        """
        Valida la credencial enviada por un agente.
        """

        raw_value = str(
            raw_credential or ""
        ).strip()

        if not raw_value:
            raise ValidationError(
                "La credencial del agente es obligatoria."
            )

        parts = raw_value.split(
            "_",
            3,
        )

        if len(parts) < 4:
            raise ValidationError(
                "El formato de la credencial no es válido."
            )

        credential_prefix = "_".join(
            parts[:3]
        )

        agent = cls.objects.filter(
            credential_prefix=credential_prefix,
            archived_at__isnull=True,
        ).first()

        if not agent:
            raise ValidationError(
                "La credencial del agente no existe."
            )

        received_hash = cls.hash_credential(
            raw_value
        )

        if not hmac.compare_digest(
            agent.credential_hash,
            received_hash,
        ):
            raise ValidationError(
                "La credencial del agente no es válida."
            )

        if not agent.is_enabled:
            raise ValidationError(
                "El agente está deshabilitado."
            )

        if agent.status == cls.Status.SUSPENDED:
            raise ValidationError(
                "El agente está suspendido."
            )

        if (
            agent.status == cls.Status.REVOKED
            or agent.revoked_at is not None
        ):
            raise ValidationError(
                "La credencial del agente fue revocada."
            )

        return agent

    def rotate_credential(
        self,
        *,
        user=None,
    ):
        """
        Revoca la credencial anterior y genera una nueva.
        """

        (
            raw_credential,
            credential_prefix,
            credential_hash,
        ) = self.generate_credential_value()

        self.credential_prefix = (
            credential_prefix
        )
        self.credential_hash = (
            credential_hash
        )
        self.configuration_version += 1

        if user:
            self.updated_by = user

        self.save(
            update_fields=[
                "credential_prefix",
                "credential_hash",
                "configuration_version",
                "updated_by",
                "updated_at",
            ]
        )

        return raw_credential

    def register_heartbeat(
        self,
        *,
        agent_version="",
        hostname="",
        local_ip_address=None,
        public_ip_address=None,
        last_error_message="",
    ):
        """
        Actualiza la información básica enviada
        en cada heartbeat.
        """

        self.last_seen_at = timezone.now()

        if self.status in {
            self.Status.PENDING,
            self.Status.OFFLINE,
            self.Status.ERROR,
        }:
            self.status = self.Status.ACTIVE

        if agent_version:
            self.agent_version = str(
                agent_version
            ).strip()

        if hostname:
            self.hostname = str(
                hostname
            ).strip()

        if local_ip_address:
            self.local_ip_address = (
                local_ip_address
            )

        if public_ip_address:
            self.public_ip_address = (
                public_ip_address
            )

        if last_error_message:
            self.last_error_at = timezone.now()
            self.last_error_message = str(
                last_error_message
            ).strip()
        else:
            self.last_error_message = ""

        self.save(
            update_fields=[
                "last_seen_at",
                "status",
                "agent_version",
                "hostname",
                "local_ip_address",
                "public_ip_address",
                "last_error_at",
                "last_error_message",
                "updated_at",
            ]
        )

    def register_successful_sync(self):
        self.last_successful_sync_at = (
            timezone.now()
        )

        self.last_error_message = ""

        self.save(
            update_fields=[
                "last_successful_sync_at",
                "last_error_message",
                "updated_at",
            ]
        )

    def revoke(
        self,
        *,
        reason="",
        user=None,
    ):
        """
        Revoca permanentemente el acceso del agente.
        """

        if self.revoked_at is not None:
            return self

        self.status = self.Status.REVOKED
        self.is_enabled = False
        self.revoked_at = timezone.now()
        self.revoked_reason = str(
            reason or ""
        ).strip()

        if user:
            self.updated_by = user

        self.save(
            update_fields=[
                "status",
                "is_enabled",
                "revoked_at",
                "revoked_reason",
                "updated_by",
                "updated_at",
            ]
        )

        return self

    def clean(self):
        super().clean()

        text_fields = [
            "code",
            "name",
            "device_identifier",
            "operating_system_version",
            "architecture",
            "hostname",
            "agent_version",
            "mac_address",
            "timezone_name",
            "server_base_url",
            "last_error_message",
            "revoked_reason",
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
                str(
                    value or ""
                ).strip(),
            )

        self.code = self.code.upper()
        self.mac_address = (
            self.mac_address.upper()
        )

        if not self.customer_id:
            raise ValidationError(
                {
                    "customer": (
                        "El cliente del agente es obligatorio."
                    ),
                }
            )

        if (
            self.branch_id
            and self.customer_id
            and self.branch.partner_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "branch": (
                        "La sede seleccionada no pertenece "
                        "al cliente indicado."
                    ),
                }
            )

        if (
            self.installation_token_id
            and self.customer_id
            and self.installation_token.customer_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "installation_token": (
                        "El token no pertenece al cliente "
                        "del agente."
                    ),
                }
            )

        if (
            self.installation_token_id
            and self.branch_id
            and self.installation_token.branch_id
            and self.installation_token.branch_id
            != self.branch_id
        ):
            raise ValidationError(
                {
                    "branch": (
                        "La sede del agente no coincide "
                        "con la sede del token."
                    ),
                }
            )

        if not self.code:
            raise ValidationError(
                {
                    "code": (
                        "El código del agente es obligatorio."
                    ),
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": (
                        "El nombre del agente es obligatorio."
                    ),
                }
            )

        if not self.device_identifier:
            raise ValidationError(
                {
                    "device_identifier": (
                        "El identificador de instalación "
                        "es obligatorio."
                    ),
                }
            )

        if self.heartbeat_interval_seconds < 30:
            raise ValidationError(
                {
                    "heartbeat_interval_seconds": (
                        "El intervalo mínimo de conexión "
                        "es de 30 segundos."
                    ),
                }
            )

        if self.discovery_interval_minutes < 1:
            raise ValidationError(
                {
                    "discovery_interval_minutes": (
                        "El intervalo de descubrimiento "
                        "debe ser como mínimo un minuto."
                    ),
                }
            )

        if self.monitoring_interval_minutes < 1:
            raise ValidationError(
                {
                    "monitoring_interval_minutes": (
                        "El intervalo de monitoreo debe ser "
                        "como mínimo un minuto."
                    ),
                }
            )

        if self.full_inventory_interval_hours < 1:
            raise ValidationError(
                {
                    "full_inventory_interval_hours": (
                        "El inventario completo debe ejecutarse "
                        "como mínimo cada hora."
                    ),
                }
            )

        if (
            self.status == self.Status.REVOKED
            and self.revoked_at is None
        ):
            raise ValidationError(
                {
                    "revoked_at": (
                        "Un agente revocado debe registrar "
                        "la fecha de revocación."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = (
                self.generate_agent_code()
            )

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.name = str(
            self.name or ""
        ).strip()

        self.device_identifier = str(
            self.device_identifier or ""
        ).strip()

        self.hostname = str(
            self.hostname or ""
        ).strip()

        self.mac_address = str(
            self.mac_address or ""
        ).strip().upper()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )