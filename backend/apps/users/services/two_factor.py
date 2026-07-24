# -*- coding: utf-8 -*-
import base64
import hashlib
import io
import secrets

import pyotp
import qrcode

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from ..models import (
    RecoveryCode,
    UserSecuritySettings,
)


TOTP_ISSUER = "Copier OS"
RECOVERY_CODE_COUNT = 10


class TwoFactorConfigurationError(Exception):
    """
    Error de configuración del servicio 2FA.
    """


class TwoFactorValidationError(Exception):
    """
    Error durante la validación de un código 2FA.
    """


def get_encryption_key():
    """
    Obtiene una clave Fernet estable.

    En producción debe definirse TWO_FACTOR_ENCRYPTION_KEY
    mediante una variable de entorno.

    Mientras se desarrolla, deriva una clave desde SECRET_KEY.
    """

    configured_key = getattr(
        settings,
        "TWO_FACTOR_ENCRYPTION_KEY",
        "",
    )

    if configured_key:
        if isinstance(configured_key, str):
            configured_key = configured_key.encode("utf-8")

        try:
            Fernet(configured_key)
        except (ValueError, TypeError) as exc:
            raise TwoFactorConfigurationError(
                "TWO_FACTOR_ENCRYPTION_KEY no es una clave Fernet válida."
            ) from exc

        return configured_key

    secret_key = getattr(
        settings,
        "SECRET_KEY",
        "",
    )

    if not secret_key:
        raise TwoFactorConfigurationError(
            "No existe SECRET_KEY para proteger el secreto TOTP."
        )

    digest = hashlib.sha256(
        secret_key.encode("utf-8")
    ).digest()

    return base64.urlsafe_b64encode(digest)


def get_fernet():
    """
    Devuelve el cifrador utilizado para proteger secretos TOTP.
    """

    return Fernet(get_encryption_key())


def encrypt_secret(secret):
    """
    Cifra un secreto TOTP antes de guardarlo.
    """

    if not secret:
        raise TwoFactorConfigurationError(
            "No se puede cifrar un secreto vacío."
        )

    return get_fernet().encrypt(
        secret.encode("utf-8")
    ).decode("utf-8")


def decrypt_secret(encrypted_secret):
    """
    Descifra un secreto TOTP almacenado.
    """

    if not encrypted_secret:
        raise TwoFactorConfigurationError(
            "El usuario no tiene un secreto TOTP configurado."
        )

    try:
        return get_fernet().decrypt(
            encrypted_secret.encode("utf-8")
        ).decode("utf-8")
    except InvalidToken as exc:
        raise TwoFactorConfigurationError(
            "No se pudo descifrar el secreto TOTP."
        ) from exc


def generate_totp_secret():
    """
    Genera un secreto Base32 para una aplicación autenticadora.
    """

    return pyotp.random_base32()


def build_totp_uri(user, secret):
    """
    Genera la URI otpauth que escaneará la aplicación autenticadora.
    """

    account_name = (
        user.email
        or user.username
        or str(user.id)
    )

    return pyotp.TOTP(secret).provisioning_uri(
        name=account_name,
        issuer_name=TOTP_ISSUER,
    )


def build_qr_code_data_uri(provisioning_uri):
    """
    Convierte la URI TOTP en una imagen PNG codificada como data URI.
    """

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )

    qr.add_data(provisioning_uri)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    encoded_image = base64.b64encode(
        buffer.getvalue()
    ).decode("ascii")

    return f"data:image/png;base64,{encoded_image}"


def normalize_totp_code(code):
    """
    Normaliza y valida el formato básico de un código TOTP.
    """

    normalized = str(code or "").replace(" ", "").strip()

    if not normalized.isdigit() or len(normalized) != 6:
        raise TwoFactorValidationError(
            "El código debe contener exactamente 6 números."
        )

    return normalized


def verify_totp_secret(secret, code):
    """
    Valida un código TOTP.

    valid_window=1 permite una diferencia aproximada de un intervalo
    antes o después para tolerar pequeños desfases de hora.
    """

    normalized_code = normalize_totp_code(code)

    return pyotp.TOTP(secret).verify(
        normalized_code,
        valid_window=1,
    )


def verify_user_totp(user, code):
    """
    Valida el código TOTP de un usuario con 2FA confirmado.
    """

    security = UserSecuritySettings.objects.filter(
        user=user,
    ).first()

    if not security:
        raise TwoFactorValidationError(
            "El usuario no tiene configuración de seguridad."
        )

    if not security.two_factor_enabled:
        raise TwoFactorValidationError(
            "La autenticación en dos factores no está activa."
        )

    if (
        security.two_factor_method
        != UserSecuritySettings.TWO_FACTOR_TOTP
    ):
        raise TwoFactorValidationError(
            "El método 2FA configurado no es una aplicación autenticadora."
        )

    secret = decrypt_secret(
        security.totp_secret
    )

    return verify_totp_secret(
        secret,
        code,
    )


@transaction.atomic
def begin_totp_setup(user):
    """
    Inicia la configuración TOTP.

    Guarda un secreto cifrado pendiente de confirmación, pero todavía
    no activa el doble factor.
    """

    security, _ = UserSecuritySettings.objects.get_or_create(
        user=user,
    )

    secret = generate_totp_secret()

    security.totp_secret = encrypt_secret(secret)
    security.two_factor_enabled = False
    security.two_factor_method = (
        UserSecuritySettings.TWO_FACTOR_NONE
    )
    security.require_two_factor_for_login = False
    security.totp_confirmed_at = None

    security.save(
        update_fields=[
            "totp_secret",
            "two_factor_enabled",
            "two_factor_method",
            "require_two_factor_for_login",
            "totp_confirmed_at",
            "updated_at",
        ]
    )

    provisioning_uri = build_totp_uri(
        user,
        secret,
    )

    return {
        "secret": secret,
        "provisioning_uri": provisioning_uri,
        "qr_code": build_qr_code_data_uri(
            provisioning_uri
        ),
    }


@transaction.atomic
def confirm_totp_setup(user, code):
    """
    Confirma el primer código y activa definitivamente el 2FA.
    """

    security = UserSecuritySettings.objects.select_for_update().filter(
        user=user,
    ).first()

    if not security or not security.totp_secret:
        raise TwoFactorValidationError(
            "Primero debes iniciar la configuración del autenticador."
        )

    secret = decrypt_secret(
        security.totp_secret
    )

    if not verify_totp_secret(secret, code):
        raise TwoFactorValidationError(
            "El código ingresado es incorrecto o ya venció."
        )

    security.two_factor_enabled = True
    security.two_factor_method = (
        UserSecuritySettings.TWO_FACTOR_TOTP
    )
    security.require_two_factor_for_login = True
    security.totp_confirmed_at = timezone.now()

    security.save(
        update_fields=[
            "two_factor_enabled",
            "two_factor_method",
            "require_two_factor_for_login",
            "totp_confirmed_at",
            "updated_at",
        ]
    )

    recovery_codes = generate_recovery_codes(
        user
    )

    return {
        "security": security,
        "recovery_codes": recovery_codes,
    }


@transaction.atomic
def generate_recovery_codes(
    user,
    count=RECOVERY_CODE_COUNT,
):
    """
    Elimina códigos anteriores y crea códigos nuevos de un solo uso.

    Solo el hash se guarda en la base de datos.
    Los códigos originales se devuelven una única vez.
    """

    if count < 1 or count > 20:
        raise TwoFactorConfigurationError(
            "La cantidad de códigos debe estar entre 1 y 20."
        )

    RecoveryCode.objects.filter(
        user=user,
    ).delete()

    raw_codes = []

    for _ in range(count):
        raw_code = format_recovery_code(
            secrets.token_hex(5).upper()
        )

        RecoveryCode.objects.create(
            user=user,
            code_hash=RecoveryCode.hash_code(
                normalize_recovery_code(raw_code)
            ),
        )

        raw_codes.append(raw_code)

    security, _ = UserSecuritySettings.objects.get_or_create(
        user=user,
    )

    security.recovery_codes_generated_at = (
        timezone.now()
    )

    security.save(
        update_fields=[
            "recovery_codes_generated_at",
            "updated_at",
        ]
    )

    return raw_codes


def format_recovery_code(raw_code):
    """
    Presenta el código en dos bloques para facilitar su lectura.
    """

    normalized = normalize_recovery_code(
        raw_code
    )

    midpoint = len(normalized) // 2

    return (
        f"{normalized[:midpoint]}-"
        f"{normalized[midpoint:]}"
    )


def normalize_recovery_code(raw_code):
    """
    Quita espacios y guiones antes de verificar el código.
    """

    return (
        str(raw_code or "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .upper()
    )


@transaction.atomic
def verify_recovery_code(user, raw_code):
    """
    Comprueba un código de recuperación y lo marca como usado.
    """

    normalized = normalize_recovery_code(
        raw_code
    )

    if not normalized:
        return False

    code_hash = RecoveryCode.hash_code(
        normalized
    )

    recovery_code = (
        RecoveryCode.objects
        .select_for_update()
        .filter(
            user=user,
            code_hash=code_hash,
            used_at__isnull=True,
        )
        .first()
    )

    if not recovery_code:
        return False

    if not recovery_code.verify(
        normalized
    ):
        return False

    recovery_code.mark_as_used()

    return True


@transaction.atomic
def disable_two_factor(user):
    """
    Desactiva 2FA y elimina códigos de recuperación existentes.
    """

    security, _ = UserSecuritySettings.objects.get_or_create(
        user=user,
    )

    security.disable_two_factor()

    security.save(
        update_fields=[
            "two_factor_enabled",
            "two_factor_method",
            "require_two_factor_for_login",
            "totp_secret",
            "totp_confirmed_at",
            "updated_at",
        ]
    )

    RecoveryCode.objects.filter(
        user=user,
    ).delete()

    return security


def get_two_factor_status(user):
    """
    Devuelve el estado de seguridad que puede mostrar el frontend.
    """

    security, _ = UserSecuritySettings.objects.get_or_create(
        user=user,
    )

    active_recovery_codes = RecoveryCode.objects.filter(
        user=user,
        used_at__isnull=True,
    ).count()

    active_passkeys = user.passkeys.filter(
        is_active=True,
    ).count()

    return {
        "two_factor_enabled": (
            security.two_factor_enabled
        ),
        "two_factor_method": (
            security.two_factor_method
        ),
        "require_two_factor_for_login": (
            security.require_two_factor_for_login
        ),
        "allow_password_login": (
            security.allow_password_login
        ),
        "allow_passkey_login": (
            security.allow_passkey_login
        ),
        "totp_confirmed_at": (
            security.totp_confirmed_at
        ),
        "recovery_codes_available": (
            active_recovery_codes
        ),
        "passkeys_registered": (
            active_passkeys
        ),
    }