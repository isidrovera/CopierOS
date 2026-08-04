# -*- coding: utf-8 -*-

import hashlib
import hmac
import secrets

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class MonitoringInstallationToken(MonitoringBaseModel):
    """
    Token utilizado para registrar agentes de monitoreo.

    El token determina:

    - Cliente.
    - Sede.
    - Cantidad de agentes permitidos.
    - Fecha de vencimiento.
    - Si puede seguir utilizándose.

    El token completo no se almacena en la base de datos.
    Solo se conserva su hash y un prefijo identificador.
    """

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_installation_tokens",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_installation_tokens",
        verbose_name="Sede",
        help_text=(
            "Cuando se deja vacío, el token puede utilizarse "
            "para registrar un agente del cliente y posteriormente "
            "asignarle una sede."
        ),
    )

    name = models.CharField(
        max_length=150,
        verbose_name="Nombre del token",
        help_text=(
            "Nombre administrativo. Ejemplo: "
            "Agente sede principal Lima."
        ),
    )

    token_prefix = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False,
        verbose_name="Prefijo del token",
    )

    token_hash = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        verbose_name="Hash del token",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de vencimiento",
        help_text=(
            "Si se deja vacío, el token no vence automáticamente."
        ),
    )

    maximum_uses = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad máxima de usos",
        help_text=(
            "Cantidad máxima de agentes que pueden registrarse "
            "utilizando este token."
        ),
    )

    used_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Cantidad de usos",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activo",
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

    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Último uso",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Token de instalación de monitoreo"
        verbose_name_plural = "Tokens de instalación de monitoreo"

        ordering = (
            "-created_at",
        )

        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "branch",
                    "is_active",
                ],
                name="mon_token_customer_branch_idx",
            ),
            models.Index(
                fields=[
                    "expires_at",
                    "is_active",
                ],
                name="mon_token_exp_active_idx",
            ),
        ]

    def __str__(self):
        location = self.customer

        if self.branch_id:
            location = (
                f"{self.customer} - "
                f"{self.branch}"
            )

        return (
            f"{self.name} - "
            f"{location}"
        )

    @staticmethod
    def hash_token(raw_token):
        """
        Genera el hash SHA-256 del token recibido.
        """

        value = str(
            raw_token or ""
        ).strip()

        return hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()

    @classmethod
    def generate_token_value(cls):
        """
        Genera un token nuevo y suficientemente seguro.

        Ejemplo:

        cpos_inst_ab12cd34_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        """

        while True:
            prefix_random = secrets.token_hex(4)

            token_prefix = (
                f"cpos_inst_{prefix_random}"
            )

            exists = cls.objects.filter(
                token_prefix=token_prefix,
            ).exists()

            if not exists:
                break

        secret_part = secrets.token_urlsafe(
            32
        )

        raw_token = (
            f"{token_prefix}_{secret_part}"
        )

        token_hash = cls.hash_token(
            raw_token
        )

        return (
            raw_token,
            token_prefix,
            token_hash,
        )

    @classmethod
    def create_token(
        cls,
        *,
        customer,
        branch=None,
        name,
        expires_at=None,
        maximum_uses=1,
        user=None,
        notes="",
    ):
        """
        Crea el token y devuelve:

        - Registro creado.
        - Token completo para mostrar una sola vez.

        El parámetro user se mantiene por compatibilidad con llamadas
        existentes, aunque el modelo base actual no contiene campos
        created_by ni updated_by.
        """

        raw_token, token_prefix, token_hash = (
            cls.generate_token_value()
        )

        instance = cls(
            customer=customer,
            branch=branch,
            name=name,
            token_prefix=token_prefix,
            token_hash=token_hash,
            expires_at=expires_at,
            maximum_uses=maximum_uses,
            notes=notes,
        )

        instance.save()

        return (
            instance,
            raw_token,
        )

    @property
    def is_expired(self):
        if not self.expires_at:
            return False

        return (
            timezone.now()
            >= self.expires_at
        )

    @property
    def has_available_uses(self):
        return (
            self.used_count
            < self.maximum_uses
        )

    @property
    def can_be_used(self):
        """
        Indica si el token puede registrar un agente.
        """

        if self.archived_at is not None:
            return False

        if not self.is_active:
            return False

        if self.revoked_at is not None:
            return False

        if self.is_expired:
            return False

        if not self.has_available_uses:
            return False

        return True

    def matches(self, raw_token):
        """
        Compara el token recibido con el hash almacenado.
        """

        received_hash = self.hash_token(
            raw_token
        )

        return hmac.compare_digest(
            self.token_hash,
            received_hash,
        )

    @classmethod
    def validate_raw_token(
        cls,
        raw_token,
    ):
        """
        Busca y valida un token recibido por el instalador.

        Devuelve el registro válido o genera ValidationError.
        """

        raw_value = str(
            raw_token or ""
        ).strip()

        if not raw_value:
            raise ValidationError(
                "El token de instalación es obligatorio."
            )

        parts = raw_value.split(
            "_",
            3,
        )

        if len(parts) < 4:
            raise ValidationError(
                "El formato del token de instalación no es válido."
            )

        token_prefix = "_".join(
            parts[:3]
        )

        instance = (
            cls.objects
            .select_related(
                "customer",
                "branch",
            )
            .filter(
                token_prefix=token_prefix,
                archived_at__isnull=True,
            )
            .first()
        )

        if not instance:
            raise ValidationError(
                "El token de instalación no existe."
            )

        if not instance.matches(
            raw_value
        ):
            raise ValidationError(
                "El token de instalación no es válido."
            )

        if not instance.is_active:
            raise ValidationError(
                "El token de instalación está desactivado."
            )

        if instance.revoked_at is not None:
            raise ValidationError(
                "El token de instalación fue revocado."
            )

        if instance.is_expired:
            raise ValidationError(
                "El token de instalación ha vencido."
            )

        if not instance.has_available_uses:
            raise ValidationError(
                "El token de instalación ya alcanzó "
                "su cantidad máxima de usos."
            )

        return instance

    def register_use(self):
        """
        Registra un uso válido del token.

        Debe ejecutarse dentro de una transacción cuando se cree
        el agente para impedir registros duplicados simultáneos.
        """

        if not self.can_be_used:
            raise ValidationError(
                "El token ya no puede utilizarse."
            )

        self.used_count += 1
        self.last_used_at = timezone.now()

        if (
            self.used_count
            >= self.maximum_uses
        ):
            self.is_active = False

        self.save(
            update_fields=[
                "used_count",
                "last_used_at",
                "is_active",
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
        Revoca definitivamente el token.

        El parámetro user se mantiene por compatibilidad, aunque el
        modelo base actual no contiene el campo updated_by.
        """

        if self.revoked_at is not None:
            return self

        self.is_active = False
        self.revoked_at = timezone.now()
        self.revoked_reason = str(
            reason or ""
        ).strip()

        self.save(
            update_fields=[
                "is_active",
                "revoked_at",
                "revoked_reason",
                "updated_at",
            ]
        )

        return self

    def clean(self):
        super().clean()

        self.name = str(
            self.name or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        self.revoked_reason = str(
            self.revoked_reason or ""
        ).strip()

        if not self.customer_id:
            raise ValidationError(
                {
                    "customer": (
                        "El cliente del token es obligatorio."
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

        if not self.name:
            raise ValidationError(
                {
                    "name": (
                        "El nombre del token es obligatorio."
                    ),
                }
            )

        if self.maximum_uses < 1:
            raise ValidationError(
                {
                    "maximum_uses": (
                        "La cantidad máxima de usos debe ser "
                        "como mínimo uno."
                    ),
                }
            )

        if (
            self.used_count
            > self.maximum_uses
        ):
            raise ValidationError(
                {
                    "used_count": (
                        "La cantidad utilizada no puede superar "
                        "la cantidad máxima permitida."
                    ),
                }
            )

        if (
            self.expires_at
            and self.pk is None
            and self.expires_at
            <= timezone.now()
        ):
            raise ValidationError(
                {
                    "expires_at": (
                        "La fecha de vencimiento debe ser futura."
                    ),
                }
            )

    def save(
        self,
        *args,
        **kwargs,
    ):
        self.name = str(
            self.name or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        self.revoked_reason = str(
            self.revoked_reason or ""
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
        self.is_active = False

        if save:
            self.save(
                update_fields=[
                    "is_active",
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
        if self.revoked_at is not None:
            raise ValidationError(
                "Un token revocado no puede restaurarse."
            )

        if self.is_expired:
            raise ValidationError(
                "Un token vencido no puede restaurarse."
            )

        if not self.has_available_uses:
            raise ValidationError(
                "El token ya alcanzó su cantidad máxima de usos."
            )

        self.is_active = True

        if save:
            self.save(
                update_fields=[
                    "is_active",
                    "updated_at",
                ]
            )

        return super().restore(
            user=user,
            save=save,
        )