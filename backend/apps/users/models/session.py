# -*- coding: utf-8 -*-
import hashlib
import secrets
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class UserSession(models.Model):
    """
    Sesión activa de un usuario.

    Permite:
    - Registrar desde qué dispositivo inició sesión.
    - Revocar sesiones individualmente.
    - Cerrar todas las sesiones de un usuario.
    - Controlar expiración y último uso.
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
        related_name="active_sessions",
        verbose_name="Usuario",
    )

    token_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name="Hash del token",
    )

    refresh_token_hash = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        verbose_name="Hash del token de renovación",
    )

    device_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Dispositivo",
    )

    device_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Tipo de dispositivo",
    )

    operating_system = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Sistema operativo",
    )

    browser = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Navegador",
    )

    user_agent = models.TextField(
        blank=True,
        verbose_name="User-Agent",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP",
    )

    location_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Ubicación aproximada",
    )

    is_current = models.BooleanField(
        default=False,
        verbose_name="Sesión actual",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activa",
    )

    authenticated_with_password = models.BooleanField(
        default=True,
        verbose_name="Autenticada con contraseña",
    )

    authenticated_with_two_factor = models.BooleanField(
        default=False,
        verbose_name="Autenticada con 2FA",
    )

    authenticated_with_passkey = models.BooleanField(
        default=False,
        verbose_name="Autenticada con passkey",
    )

    two_factor_method = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Método de segundo factor",
    )

    expires_at = models.DateTimeField(
        verbose_name="Expira el",
    )

    last_activity_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Última actividad",
    )

    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Revocada el",
    )

    revoked_reason = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Motivo de revocación",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Creada el",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizada el",
    )

    class Meta:
        verbose_name = "Sesión de usuario"
        verbose_name_plural = "Sesiones de usuario"
        ordering = ("-last_activity_at",)
        indexes = [
            models.Index(
                fields=[
                    "user",
                    "is_active",
                ],
                name="users_session_active_idx",
            ),
            models.Index(
                fields=[
                    "user",
                    "expires_at",
                ],
                name="users_session_exp_idx",
            ),
        ]

    def __str__(self):
        device = self.device_name or self.browser or "Dispositivo"

        return f"{self.user} - {device}"

    @staticmethod
    def hash_token(raw_token):
        """
        Genera un hash SHA-256 para no guardar tokens reales.
        """
        return hashlib.sha256(
            raw_token.encode("utf-8")
        ).hexdigest()

    @classmethod
    def generate_token(cls):
        """
        Genera un token aleatorio seguro.
        """
        return secrets.token_urlsafe(48)

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self):
        return (
            self.is_active
            and not self.is_expired
            and self.revoked_at is None
        )

    def verify_token(self, raw_token):
        """
        Compara el token recibido con el hash almacenado.
        """
        return secrets.compare_digest(
            self.token_hash,
            self.hash_token(raw_token),
        )

    def verify_refresh_token(self, raw_token):
        if not self.refresh_token_hash:
            return False

        return secrets.compare_digest(
            self.refresh_token_hash,
            self.hash_token(raw_token),
        )

    def register_activity(self):
        """
        Actualiza la última actividad de la sesión.
        """
        self.last_activity_at = timezone.now()

        self.save(
            update_fields=[
                "last_activity_at",
                "updated_at",
            ]
        )

    def revoke(self, reason=""):
        """
        Revoca la sesión y evita que vuelva a utilizarse.
        """
        self.is_active = False
        self.is_current = False
        self.revoked_at = timezone.now()
        self.revoked_reason = reason

        self.save(
            update_fields=[
                "is_active",
                "is_current",
                "revoked_at",
                "revoked_reason",
                "updated_at",
            ]
        )

    @classmethod
    def revoke_all_for_user(
        cls,
        user,
        reason="Cierre de todas las sesiones",
        exclude_session=None,
    ):
        """
        Revoca todas las sesiones activas del usuario.

        Puede excluir la sesión actual.
        """
        sessions = cls.objects.filter(
            user=user,
            is_active=True,
        )

        if exclude_session:
            sessions = sessions.exclude(
                id=exclude_session.id,
            )

        now = timezone.now()

        return sessions.update(
            is_active=False,
            is_current=False,
            revoked_at=now,
            revoked_reason=reason,
            updated_at=now,
        )


class LoginAttempt(models.Model):
    """
    Registro de intentos de inicio de sesión.

    Guarda tanto intentos exitosos como fallidos.
    """

    RESULT_SUCCESS = "success"
    RESULT_FAILED = "failed"
    RESULT_LOCKED = "locked"
    RESULT_TWO_FACTOR_REQUIRED = "2fa_required"

    RESULT_CHOICES = (
        (
            RESULT_SUCCESS,
            "Exitoso",
        ),
        (
            RESULT_FAILED,
            "Fallido",
        ),
        (
            RESULT_LOCKED,
            "Usuario bloqueado",
        ),
        (
            RESULT_TWO_FACTOR_REQUIRED,
            "Segundo factor requerido",
        ),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="login_attempts",
        verbose_name="Usuario",
    )

    email_entered = models.EmailField(
        blank=True,
        db_index=True,
        verbose_name="Correo ingresado",
    )

    result = models.CharField(
        max_length=30,
        choices=RESULT_CHOICES,
        db_index=True,
        verbose_name="Resultado",
    )

    failure_reason = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Motivo del fallo",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Dirección IP",
    )

    user_agent = models.TextField(
        blank=True,
        verbose_name="User-Agent",
    )

    device_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Dispositivo",
    )

    browser = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Navegador",
    )

    operating_system = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Sistema operativo",
    )

    attempted_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Intentado el",
    )

    class Meta:
        verbose_name = "Intento de inicio de sesión"
        verbose_name_plural = "Intentos de inicio de sesión"
        ordering = ("-attempted_at",)
        indexes = [
            models.Index(
                fields=[
                    "email_entered",
                    "attempted_at",
                ],
                name="users_login_email_idx",
            ),
            models.Index(
                fields=[
                    "ip_address",
                    "attempted_at",
                ],
                name="users_login_ip_idx",
            ),
        ]

    def __str__(self):
        email = self.email_entered or "Sin correo"

        return f"{email} - {self.get_result_display()}"


class PasswordResetToken(models.Model):
    """
    Token temporal para recuperar la contraseña.

    El token real nunca se guarda, solo su hash.
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
        related_name="password_reset_tokens",
        verbose_name="Usuario",
    )

    token_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name="Hash del token",
    )

    expires_at = models.DateTimeField(
        db_index=True,
        verbose_name="Expira el",
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Usado el",
    )

    requested_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP de solicitud",
    )

    user_agent = models.TextField(
        blank=True,
        verbose_name="User-Agent",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado el",
    )

    class Meta:
        verbose_name = "Token de recuperación de contraseña"
        verbose_name_plural = (
            "Tokens de recuperación de contraseña"
        )
        ordering = ("-created_at",)

    def __str__(self):
        return f"Recuperación de contraseña de {self.user}"

    @staticmethod
    def hash_token(raw_token):
        return hashlib.sha256(
            raw_token.encode("utf-8")
        ).hexdigest()

    @classmethod
    def create_token(
        cls,
        user,
        expires_at,
        requested_ip=None,
        user_agent="",
    ):
        raw_token = secrets.token_urlsafe(48)

        instance = cls.objects.create(
            user=user,
            token_hash=cls.hash_token(raw_token),
            expires_at=expires_at,
            requested_ip=requested_ip,
            user_agent=user_agent,
        )

        return instance, raw_token

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_used(self):
        return self.used_at is not None

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired

    def verify(self, raw_token):
        if not self.is_valid:
            return False

        return secrets.compare_digest(
            self.token_hash,
            self.hash_token(raw_token),
        )

    def mark_as_used(self):
        self.used_at = timezone.now()

        self.save(
            update_fields=[
                "used_at",
            ]
        )


class PasswordHistory(models.Model):
    """
    Historial de contraseñas anteriores.

    Permite impedir que el usuario reutilice una contraseña
    reciente.
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
        related_name="password_history",
        verbose_name="Usuario",
    )

    password_hash = models.CharField(
        max_length=255,
        verbose_name="Hash de contraseña",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Creado el",
    )

    class Meta:
        verbose_name = "Historial de contraseña"
        verbose_name_plural = "Historial de contraseñas"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Contraseña anterior de {self.user}"