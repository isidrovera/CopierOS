# -*- coding: utf-8 -*-
import hashlib
import os

from cryptography.fernet import (
    Fernet,
    InvalidToken,
)
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base import MonitoringBaseModel


class SNMPCredential(MonitoringBaseModel):
    """
    Credencial utilizada por los agentes para consultar
    dispositivos mediante SNMP.

    Puede aplicarse a:

    - Todo un cliente.
    - Una sede.
    - Un agente específico.
    - Una red específica.

    Las comunidades y contraseñas se almacenan cifradas.
    """

    class SNMPVersion(models.TextChoices):
        V1 = (
            "1",
            "SNMP v1",
        )
        V2C = (
            "2c",
            "SNMP v2c",
        )
        V3 = (
            "3",
            "SNMP v3",
        )

    class SecurityLevel(models.TextChoices):
        NO_AUTH_NO_PRIV = (
            "no_auth_no_priv",
            "Sin autenticación ni privacidad",
        )
        AUTH_NO_PRIV = (
            "auth_no_priv",
            "Con autenticación sin privacidad",
        )
        AUTH_PRIV = (
            "auth_priv",
            "Con autenticación y privacidad",
        )

    class AuthProtocol(models.TextChoices):
        NONE = (
            "none",
            "No aplica",
        )
        MD5 = (
            "md5",
            "MD5",
        )
        SHA = (
            "sha",
            "SHA",
        )
        SHA224 = (
            "sha224",
            "SHA-224",
        )
        SHA256 = (
            "sha256",
            "SHA-256",
        )
        SHA384 = (
            "sha384",
            "SHA-384",
        )
        SHA512 = (
            "sha512",
            "SHA-512",
        )

    class PrivacyProtocol(models.TextChoices):
        NONE = (
            "none",
            "No aplica",
        )
        DES = (
            "des",
            "DES",
        )
        AES128 = (
            "aes128",
            "AES-128",
        )
        AES192 = (
            "aes192",
            "AES-192",
        )
        AES256 = (
            "aes256",
            "AES-256",
        )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="snmp_credentials",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="snmp_credentials",
        verbose_name="Sede",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="snmp_credentials",
        verbose_name="Agente",
    )

    network = models.ForeignKey(
        "monitoring.MonitoringNetwork",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="snmp_credentials",
        verbose_name="Red",
    )

    name = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Nombre",
        help_text=(
            "Ejemplo: SNMP público sede principal."
        ),
    )

    snmp_version = models.CharField(
        max_length=5,
        choices=SNMPVersion.choices,
        default=SNMPVersion.V2C,
        db_index=True,
        verbose_name="Versión SNMP",
    )

    port = models.PositiveIntegerField(
        default=161,
        verbose_name="Puerto SNMP",
    )

    encrypted_community = models.TextField(
        blank=True,
        editable=False,
        verbose_name="Comunidad cifrada",
    )

    username = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Usuario SNMP v3",
    )

    security_level = models.CharField(
        max_length=30,
        choices=SecurityLevel.choices,
        default=SecurityLevel.NO_AUTH_NO_PRIV,
        verbose_name="Nivel de seguridad",
    )

    auth_protocol = models.CharField(
        max_length=20,
        choices=AuthProtocol.choices,
        default=AuthProtocol.NONE,
        verbose_name="Protocolo de autenticación",
    )

    encrypted_auth_password = models.TextField(
        blank=True,
        editable=False,
        verbose_name="Clave de autenticación cifrada",
    )

    privacy_protocol = models.CharField(
        max_length=20,
        choices=PrivacyProtocol.choices,
        default=PrivacyProtocol.NONE,
        verbose_name="Protocolo de privacidad",
    )

    encrypted_privacy_password = models.TextField(
        blank=True,
        editable=False,
        verbose_name="Clave de privacidad cifrada",
    )

    context_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Contexto SNMP v3",
    )

    context_engine_id = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Engine ID de contexto",
    )

    timeout_seconds = models.PositiveIntegerField(
        default=3,
        verbose_name="Tiempo de espera",
    )

    retry_count = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad de reintentos",
    )

    priority = models.PositiveIntegerField(
        default=100,
        db_index=True,
        verbose_name="Prioridad",
        help_text=(
            "Las credenciales con menor valor se prueban primero."
        ),
    )

    is_default = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Credencial predeterminada",
    )

    is_enabled = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Habilitada",
    )

    successful_device_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Equipos consultados correctamente",
    )

    failed_attempt_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Intentos fallidos",
    )

    last_success_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último uso correcto",
    )

    last_failure_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último error",
    )

    last_failure_message = models.TextField(
        blank=True,
        verbose_name="Descripción del último error",
    )

    secret_fingerprint = models.CharField(
        max_length=64,
        blank=True,
        editable=False,
        db_index=True,
        verbose_name="Huella de la credencial",
        help_text=(
            "Permite detectar credenciales repetidas "
            "sin revelar sus valores."
        ),
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Credencial SNMP"
        verbose_name_plural = "Credenciales SNMP"
        ordering = (
            "customer",
            "branch",
            "priority",
            "name",
        )
        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "branch",
                    "is_enabled",
                ],
                name="mon_snmp_customer_branch_idx",
            ),
            models.Index(
                fields=[
                    "agent",
                    "network",
                    "priority",
                ],
                name="mon_snmp_agent_network_idx",
            ),
            models.Index(
                fields=[
                    "snmp_version",
                    "is_enabled",
                    "priority",
                ],
                name="mon_snmp_version_enabled_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "customer",
                    "name",
                ],
                condition=models.Q(
                    archived_at__isnull=True,
                ),
                name="unique_customer_snmp_name",
            ),
        ]

    def __str__(self):
        return (
            f"{self.customer} - "
            f"{self.name} - "
            f"SNMP {self.snmp_version}"
        )

    @staticmethod
    def get_cipher():
        """
        Obtiene la clave Fernet desde una variable de entorno.

        La variable debe llamarse:

        COPIEROS_MONITORING_ENCRYPTION_KEY
        """

        encryption_key = os.getenv(
            "COPIEROS_MONITORING_ENCRYPTION_KEY",
            "",
        ).strip()

        if not encryption_key:
            raise ValidationError(
                "No se configuró la clave de cifrado "
                "del módulo de monitoreo."
            )

        try:
            return Fernet(
                encryption_key.encode("utf-8")
            )
        except (
            TypeError,
            ValueError,
        ):
            raise ValidationError(
                "La clave de cifrado del módulo "
                "de monitoreo no es válida."
            )

    @classmethod
    def encrypt_secret(
        cls,
        value,
    ):
        raw_value = str(
            value or ""
        )

        if not raw_value:
            return ""

        cipher = cls.get_cipher()

        return cipher.encrypt(
            raw_value.encode("utf-8")
        ).decode("utf-8")

    @classmethod
    def decrypt_secret(
        cls,
        encrypted_value,
    ):
        value = str(
            encrypted_value or ""
        ).strip()

        if not value:
            return ""

        cipher = cls.get_cipher()

        try:
            return cipher.decrypt(
                value.encode("utf-8")
            ).decode("utf-8")
        except InvalidToken:
            raise ValidationError(
                "No se pudo descifrar la credencial SNMP."
            )

    @staticmethod
    def calculate_fingerprint(
        *,
        snmp_version,
        community="",
        username="",
        auth_password="",
        privacy_password="",
    ):
        value = "|".join(
            [
                str(snmp_version or ""),
                str(community or ""),
                str(username or ""),
                str(auth_password or ""),
                str(privacy_password or ""),
            ]
        )

        return hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()

    def set_community(
        self,
        value,
    ):
        community = str(
            value or ""
        )

        self.encrypted_community = (
            self.encrypt_secret(
                community
            )
        )

        self.refresh_fingerprint(
            community=community,
        )

    def get_community(self):
        return self.decrypt_secret(
            self.encrypted_community
        )

    def set_auth_password(
        self,
        value,
    ):
        auth_password = str(
            value or ""
        )

        self.encrypted_auth_password = (
            self.encrypt_secret(
                auth_password
            )
        )

        self.refresh_fingerprint(
            auth_password=auth_password,
        )

    def get_auth_password(self):
        return self.decrypt_secret(
            self.encrypted_auth_password
        )

    def set_privacy_password(
        self,
        value,
    ):
        privacy_password = str(
            value or ""
        )

        self.encrypted_privacy_password = (
            self.encrypt_secret(
                privacy_password
            )
        )

        self.refresh_fingerprint(
            privacy_password=privacy_password,
        )

    def get_privacy_password(self):
        return self.decrypt_secret(
            self.encrypted_privacy_password
        )

    def refresh_fingerprint(
        self,
        *,
        community=None,
        auth_password=None,
        privacy_password=None,
    ):
        if community is None:
            community = self.get_community()

        if auth_password is None:
            auth_password = self.get_auth_password()

        if privacy_password is None:
            privacy_password = (
                self.get_privacy_password()
            )

        self.secret_fingerprint = (
            self.calculate_fingerprint(
                snmp_version=self.snmp_version,
                community=community,
                username=self.username,
                auth_password=auth_password,
                privacy_password=privacy_password,
            )
        )

    def get_agent_payload(self):
        """
        Devuelve la configuración necesaria para el agente.

        Este método solo debe utilizarse después de autenticar
        correctamente al agente.
        """

        payload = {
            "id": str(self.id),
            "name": self.name,
            "version": self.snmp_version,
            "port": self.port,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
            "priority": self.priority,
        }

        if self.snmp_version in {
            self.SNMPVersion.V1,
            self.SNMPVersion.V2C,
        }:
            payload["community"] = (
                self.get_community()
            )

        if self.snmp_version == self.SNMPVersion.V3:
            payload.update(
                {
                    "username": self.username,
                    "security_level": (
                        self.security_level
                    ),
                    "auth_protocol": (
                        self.auth_protocol
                    ),
                    "auth_password": (
                        self.get_auth_password()
                    ),
                    "privacy_protocol": (
                        self.privacy_protocol
                    ),
                    "privacy_password": (
                        self.get_privacy_password()
                    ),
                    "context_name": self.context_name,
                    "context_engine_id": (
                        self.context_engine_id
                    ),
                }
            )

        return payload

    def clean(self):
        super().clean()

        text_fields = [
            "name",
            "username",
            "context_name",
            "context_engine_id",
            "last_failure_message",
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

        if not self.customer_id:
            raise ValidationError(
                {
                    "customer": (
                        "El cliente es obligatorio."
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
            and self.network.agent.customer_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "network": (
                        "La red no pertenece al cliente."
                    ),
                }
            )

        if (
            self.network_id
            and self.agent_id
            and self.network.agent_id
            != self.agent_id
        ):
            raise ValidationError(
                {
                    "network": (
                        "La red no pertenece al agente seleccionado."
                    ),
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": (
                        "El nombre de la credencial es obligatorio."
                    ),
                }
            )

        if self.port < 1 or self.port > 65535:
            raise ValidationError(
                {
                    "port": (
                        "El puerto debe estar entre 1 y 65535."
                    ),
                }
            )

        if self.timeout_seconds < 1:
            raise ValidationError(
                {
                    "timeout_seconds": (
                        "El tiempo de espera debe ser "
                        "como mínimo un segundo."
                    ),
                }
            )

        if self.retry_count > 10:
            raise ValidationError(
                {
                    "retry_count": (
                        "La cantidad de reintentos no puede "
                        "superar diez."
                    ),
                }
            )

        if self.snmp_version in {
            self.SNMPVersion.V1,
            self.SNMPVersion.V2C,
        }:
            if not self.encrypted_community:
                raise ValidationError(
                    {
                        "encrypted_community": (
                            "La comunidad SNMP es obligatoria."
                        ),
                    }
                )

            self.username = ""
            self.security_level = (
                self.SecurityLevel.NO_AUTH_NO_PRIV
            )
            self.auth_protocol = (
                self.AuthProtocol.NONE
            )
            self.encrypted_auth_password = ""
            self.privacy_protocol = (
                self.PrivacyProtocol.NONE
            )
            self.encrypted_privacy_password = ""
            self.context_name = ""
            self.context_engine_id = ""

        if self.snmp_version == self.SNMPVersion.V3:
            self.encrypted_community = ""

            if not self.username:
                raise ValidationError(
                    {
                        "username": (
                            "El usuario SNMP v3 es obligatorio."
                        ),
                    }
                )

            if (
                self.security_level
                == self.SecurityLevel.NO_AUTH_NO_PRIV
            ):
                self.auth_protocol = (
                    self.AuthProtocol.NONE
                )
                self.encrypted_auth_password = ""
                self.privacy_protocol = (
                    self.PrivacyProtocol.NONE
                )
                self.encrypted_privacy_password = ""

            if (
                self.security_level
                == self.SecurityLevel.AUTH_NO_PRIV
            ):
                if (
                    self.auth_protocol
                    == self.AuthProtocol.NONE
                ):
                    raise ValidationError(
                        {
                            "auth_protocol": (
                                "Debe seleccionar un protocolo "
                                "de autenticación."
                            ),
                        }
                    )

                if not self.encrypted_auth_password:
                    raise ValidationError(
                        {
                            "encrypted_auth_password": (
                                "La clave de autenticación "
                                "es obligatoria."
                            ),
                        }
                    )

                self.privacy_protocol = (
                    self.PrivacyProtocol.NONE
                )
                self.encrypted_privacy_password = ""

            if (
                self.security_level
                == self.SecurityLevel.AUTH_PRIV
            ):
                if (
                    self.auth_protocol
                    == self.AuthProtocol.NONE
                ):
                    raise ValidationError(
                        {
                            "auth_protocol": (
                                "Debe seleccionar un protocolo "
                                "de autenticación."
                            ),
                        }
                    )

                if not self.encrypted_auth_password:
                    raise ValidationError(
                        {
                            "encrypted_auth_password": (
                                "La clave de autenticación "
                                "es obligatoria."
                            ),
                        }
                    )

                if (
                    self.privacy_protocol
                    == self.PrivacyProtocol.NONE
                ):
                    raise ValidationError(
                        {
                            "privacy_protocol": (
                                "Debe seleccionar un protocolo "
                                "de privacidad."
                            ),
                        }
                    )

                if not self.encrypted_privacy_password:
                    raise ValidationError(
                        {
                            "encrypted_privacy_password": (
                                "La clave de privacidad "
                                "es obligatoria."
                            ),
                        }
                    )

    def save(self, *args, **kwargs):
        self.name = str(
            self.name or ""
        ).strip()

        self.username = str(
            self.username or ""
        ).strip()

        self.context_name = str(
            self.context_name or ""
        ).strip()

        self.context_engine_id = str(
            self.context_engine_id or ""
        ).strip()

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
        self.is_enabled = False

        if save:
            self.save(
                update_fields=[
                    "is_enabled",
                    "updated_at",
                ]
            )

        return super().archive(
            user=user,
            reason=reason,
            save=save,
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        self.is_enabled = True

        if save:
            self.save(
                update_fields=[
                    "is_enabled",
                    "updated_at",
                ]
            )

        return super().restore(
            user=user,
            save=save,
        )