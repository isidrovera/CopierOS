# -*- coding: utf-8 -*-
import hashlib
import secrets
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class UserSecuritySettings(models.Model):
    """
    Configuración de seguridad del usuario.

    Centraliza:
    - Autenticación en dos factores.
    - Confirmación de correo.
    - Política de bloqueo.
    - Preferencia de método de acceso.
    """

    TWO_FACTOR_NONE = "none"
    TWO_FACTOR_TOTP = "totp"
    TWO_FACTOR_EMAIL = "email"

    TWO_FACTOR_CHOICES = (
        (
            TWO_FACTOR_NONE,
            "Sin autenticación en dos factores",
        ),
        (
            TWO_FACTOR_TOTP,
            "Aplicación autenticadora",
        ),
        (
            TWO_FACTOR_EMAIL,
            "Código por correo",
        ),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="security_settings",
        verbose_name="Usuario",
    )

    two_factor_enabled = models.BooleanField(
        default=False,
        verbose_name="Autenticación en dos factores activa",
    )

    two_factor_method = models.CharField(
        max_length=20,
        choices=TWO_FACTOR_CHOICES,
        default=TWO_FACTOR_NONE,
        verbose_name="Método de autenticación en dos factores",
    )

    totp_secret = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Secreto TOTP",
        help_text=(
            "Debe almacenarse cifrado antes de usarlo "
            "en producción."
        ),
    )

    totp_confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="TOTP confirmado el",
    )

    require_two_factor_for_login = models.BooleanField(
        default=False,
        verbose_name="Exigir 2FA para iniciar sesión",
    )

    allow_password_login = models.BooleanField(
        default=True,
        verbose_name="Permitir acceso con contraseña",
    )

    allow_passkey_login = models.BooleanField(
        default=True,
        verbose_name="Permitir acceso con passkey",
    )

    recovery_codes_generated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Códigos de recuperación generados el",
    )

    last_security_review_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última revisión de seguridad",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado el",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizado el",
    )

    class Meta:
        verbose_name = "Configuración de seguridad"
        verbose_name_plural = "Configuraciones de seguridad"

    def __str__(self):
        return f"Seguridad de {self.user}"

    def enable_totp(self, secret):
        self.totp_secret = secret
        self.two_factor_enabled = True
        self.two_factor_method = self.TWO_FACTOR_TOTP
        self.require_two_factor_for_login = True
        self.totp_confirmed_at = timezone.now()

    def disable_two_factor(self):
        self.two_factor_enabled = False
        self.two_factor_method = self.TWO_FACTOR_NONE
        self.require_two_factor_for_login = False
        self.totp_secret = ""
        self.totp_confirmed_at = None


class RecoveryCode(models.Model):
    """
    Código de recuperación de un solo uso.

    El código real no se guarda. Solo se almacena su hash.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recovery_codes",
        verbose_name="Usuario",
    )

    code_hash = models.CharField(
        max_length=64,
        db_index=True,
        verbose_name="Hash del código",
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Usado el",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado el",
    )

    class Meta:
        verbose_name = "Código de recuperación"
        verbose_name_plural = "Códigos de recuperación"
        ordering = ("-created_at",)

    def __str__(self):
        status = "usado" if self.used_at else "disponible"

        return f"Código de {self.user} - {status}"

    @staticmethod
    def hash_code(raw_code):
        return hashlib.sha256(
            raw_code.encode("utf-8")
        ).hexdigest()

    @classmethod
    def create_code(cls, user):
        raw_code = secrets.token_hex(5).upper()

        recovery_code = cls.objects.create(
            user=user,
            code_hash=cls.hash_code(raw_code),
        )

        return recovery_code, raw_code

    def verify(self, raw_code):
        if self.used_at:
            return False

        return secrets.compare_digest(
            self.code_hash,
            self.hash_code(raw_code),
        )

    def mark_as_used(self):
        self.used_at = timezone.now()
        self.save(
            update_fields=[
                "used_at",
            ]
        )


class PasskeyCredential(models.Model):
    """
    Credencial WebAuthn o passkey registrada por un usuario.

    Nunca se almacena una clave privada. Solo se guarda la
    clave pública y los datos necesarios para verificarla.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="passkeys",
        verbose_name="Usuario",
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Nombre del dispositivo",
    )

    credential_id = models.TextField(
        unique=True,
        verbose_name="ID de credencial",
    )

    public_key = models.TextField(
        verbose_name="Clave pública",
    )

    sign_count = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Contador de firmas",
    )

    transports = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Transportes",
    )

    device_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Tipo de dispositivo",
    )

    backed_up = models.BooleanField(
        default=False,
        verbose_name="Credencial respaldada",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Activa",
    )

    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último uso",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creada el",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizada el",
    )

    class Meta:
        verbose_name = "Passkey"
        verbose_name_plural = "Passkeys"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} - {self.user}"

    def mark_as_used(self, sign_count=None):
        self.last_used_at = timezone.now()

        update_fields = [
            "last_used_at",
        ]

        if sign_count is not None:
            self.sign_count = sign_count
            update_fields.append("sign_count")

        self.save(update_fields=update_fields)

    def revoke(self):
        self.is_active = False
        self.save(
            update_fields=[
                "is_active",
            ]
        )


class EmailVerificationCode(models.Model):
    """
    Código temporal para verificar el correo electrónico.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verification_codes",
        verbose_name="Usuario",
    )

    code_hash = models.CharField(
        max_length=64,
        db_index=True,
        verbose_name="Hash del código",
    )

    expires_at = models.DateTimeField(
        verbose_name="Expira el",
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Usado el",
    )

    attempts = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Intentos",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado el",
    )

    class Meta:
        verbose_name = "Código de verificación de correo"
        verbose_name_plural = (
            "Códigos de verificación de correo"
        )
        ordering = ("-created_at",)

    def __str__(self):
        return f"Verificación de correo de {self.user}"

    @staticmethod
    def hash_code(raw_code):
        return hashlib.sha256(
            raw_code.encode("utf-8")
        ).hexdigest()

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_used(self):
        return self.used_at is not None

    def verify(self, raw_code):
        if self.is_used or self.is_expired:
            return False

        self.attempts += 1
        self.save(
            update_fields=[
                "attempts",
            ]
        )

        return secrets.compare_digest(
            self.code_hash,
            self.hash_code(raw_code),
        )

    def mark_as_used(self):
        self.used_at = timezone.now()
        self.save(
            update_fields=[
                "used_at",
            ]
        )