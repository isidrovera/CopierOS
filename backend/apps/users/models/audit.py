# -*- coding: utf-8 -*-
import uuid

from django.conf import settings
from django.db import models


class UserAuditLog(models.Model):
    """
    Registro de auditoría para acciones relacionadas con usuarios.

    Permite saber:
    - Quién realizó una acción.
    - Sobre qué usuario se realizó.
    - Qué operación se ejecutó.
    - Desde qué IP y dispositivo.
    - Qué datos cambiaron.
    """

    ACTION_CREATE = "create"
    ACTION_UPDATE = "update"
    ACTION_ARCHIVE = "archive"
    ACTION_RESTORE = "restore"
    ACTION_DELETE = "delete"
    ACTION_PASSWORD_CHANGE = "password_change"
    ACTION_PASSWORD_RESET = "password_reset"
    ACTION_LOGIN = "login"
    ACTION_LOGOUT = "logout"
    ACTION_LOGIN_FAILED = "login_failed"
    ACTION_ACTIVATE = "activate"
    ACTION_DEACTIVATE = "deactivate"
    ACTION_EMAIL_VERIFY = "email_verify"
    ACTION_TWO_FACTOR_ENABLE = "two_factor_enable"
    ACTION_TWO_FACTOR_DISABLE = "two_factor_disable"
    ACTION_PASSKEY_REGISTER = "passkey_register"
    ACTION_PASSKEY_REVOKE = "passkey_revoke"
    ACTION_SESSION_REVOKE = "session_revoke"
    ACTION_DNI_LOOKUP = "dni_lookup"

    ACTION_CHOICES = (
        (ACTION_CREATE, "Creación"),
        (ACTION_UPDATE, "Modificación"),
        (ACTION_ARCHIVE, "Archivado"),
        (ACTION_RESTORE, "Restauración"),
        (ACTION_DELETE, "Eliminación"),
        (
            ACTION_PASSWORD_CHANGE,
            "Cambio de contraseña",
        ),
        (
            ACTION_PASSWORD_RESET,
            "Restablecimiento de contraseña",
        ),
        (ACTION_LOGIN, "Inicio de sesión"),
        (ACTION_LOGOUT, "Cierre de sesión"),
        (
            ACTION_LOGIN_FAILED,
            "Inicio de sesión fallido",
        ),
        (ACTION_ACTIVATE, "Activación"),
        (ACTION_DEACTIVATE, "Desactivación"),
        (
            ACTION_EMAIL_VERIFY,
            "Verificación de correo",
        ),
        (
            ACTION_TWO_FACTOR_ENABLE,
            "Activación de 2FA",
        ),
        (
            ACTION_TWO_FACTOR_DISABLE,
            "Desactivación de 2FA",
        ),
        (
            ACTION_PASSKEY_REGISTER,
            "Registro de passkey",
        ),
        (
            ACTION_PASSKEY_REVOKE,
            "Revocación de passkey",
        ),
        (
            ACTION_SESSION_REVOKE,
            "Revocación de sesión",
        ),
        (
            ACTION_DNI_LOOKUP,
            "Consulta de DNI",
        ),
    )

    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = (
        (
            STATUS_SUCCESS,
            "Exitoso",
        ),
        (
            STATUS_FAILED,
            "Fallido",
        ),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_audit_actions",
        verbose_name="Usuario que realizó la acción",
    )

    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_audit_events",
        verbose_name="Usuario afectado",
    )

    action = models.CharField(
        max_length=40,
        choices=ACTION_CHOICES,
        db_index=True,
        verbose_name="Acción",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SUCCESS,
        db_index=True,
        verbose_name="Estado",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    changed_fields = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Campos modificados",
        help_text=(
            "Guarda los valores anteriores y nuevos "
            "de los campos modificados."
        ),
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos adicionales",
    )

    error_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de error",
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

    request_method = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Método HTTP",
    )

    request_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Ruta solicitada",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Registrado el",
    )

    class Meta:
        verbose_name = "Auditoría de usuario"
        verbose_name_plural = "Auditorías de usuarios"
        ordering = (
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "actor",
                    "created_at",
                ],
                name="users_audit_actor_idx",
            ),
            models.Index(
                fields=[
                    "target_user",
                    "created_at",
                ],
                name="users_audit_target_idx",
            ),
            models.Index(
                fields=[
                    "action",
                    "status",
                ],
                name="users_audit_action_idx",
            ),
        ]

    def __str__(self):
        actor = self.actor or "Sistema"
        target = self.target_user or "Sin usuario"

        return (
            f"{actor} - "
            f"{self.get_action_display()} - "
            f"{target}"
        )


class UserDataAccessLog(models.Model):
    """
    Registro de acceso a datos sensibles.

    Se usa para controlar quién consultó información como:
    - DNI.
    - Dirección.
    - Teléfonos.
    - Datos personales.
    """

    DATA_DNI = "dni"
    DATA_PERSONAL = "personal"
    DATA_CONTACT = "contact"
    DATA_ADDRESS = "address"
    DATA_SECURITY = "security"

    DATA_TYPE_CHOICES = (
        (
            DATA_DNI,
            "DNI",
        ),
        (
            DATA_PERSONAL,
            "Datos personales",
        ),
        (
            DATA_CONTACT,
            "Datos de contacto",
        ),
        (
            DATA_ADDRESS,
            "Dirección",
        ),
        (
            DATA_SECURITY,
            "Datos de seguridad",
        ),
    )

    ACCESS_VIEW = "view"
    ACCESS_EXPORT = "export"
    ACCESS_LOOKUP = "lookup"

    ACCESS_TYPE_CHOICES = (
        (
            ACCESS_VIEW,
            "Visualización",
        ),
        (
            ACCESS_EXPORT,
            "Exportación",
        ),
        (
            ACCESS_LOOKUP,
            "Consulta externa",
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
        related_name="sensitive_data_accesses",
        verbose_name="Usuario que accedió",
    )

    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sensitive_data_views",
        verbose_name="Usuario consultado",
    )

    data_type = models.CharField(
        max_length=30,
        choices=DATA_TYPE_CHOICES,
        db_index=True,
        verbose_name="Tipo de dato",
    )

    access_type = models.CharField(
        max_length=20,
        choices=ACCESS_TYPE_CHOICES,
        db_index=True,
        verbose_name="Tipo de acceso",
    )

    purpose = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Motivo del acceso",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP",
    )

    request_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Ruta solicitada",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Accedido el",
    )

    class Meta:
        verbose_name = "Acceso a dato sensible"
        verbose_name_plural = "Accesos a datos sensibles"
        ordering = (
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "user",
                    "created_at",
                ],
                name="users_data_access_idx",
            ),
            models.Index(
                fields=[
                    "target_user",
                    "data_type",
                ],
                name="users_data_target_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user or 'Sistema'} - "
            f"{self.get_data_type_display()}"
        )