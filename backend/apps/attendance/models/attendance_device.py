# -*- coding: utf-8 -*-

import hashlib
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .work_location import WorkLocation


class AttendanceDevice(models.Model):
    """
    Dispositivo autorizado para registrar asistencia.

    Puede representar:

    - Tablet compartida del taller.
    - Computadora de ventas.
    - Equipo fijo de recepción.
    - Teléfono corporativo.
    - Navegador autorizado.
    - Terminal de marcación.
    """

    class DeviceType(models.TextChoices):
        TABLET = (
            "tablet",
            "Tablet",
        )
        DESKTOP = (
            "desktop",
            "Computadora de escritorio",
        )
        LAPTOP = (
            "laptop",
            "Laptop",
        )
        MOBILE = (
            "mobile",
            "Teléfono móvil",
        )
        TERMINAL = (
            "terminal",
            "Terminal de asistencia",
        )
        BROWSER = (
            "browser",
            "Navegador autorizado",
        )
        OTHER = (
            "other",
            "Otro",
        )

    class OwnershipType(models.TextChoices):
        COMPANY = (
            "company",
            "Propiedad de la empresa",
        )
        EMPLOYEE = (
            "employee",
            "Propiedad del trabajador",
        )
        CLIENT = (
            "client",
            "Propiedad del cliente",
        )
        SHARED = (
            "shared",
            "Dispositivo compartido",
        )
        OTHER = (
            "other",
            "Otro",
        )

    class RegistrationStatus(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        APPROVED = (
            "approved",
            "Aprobado",
        )
        REJECTED = (
            "rejected",
            "Rechazado",
        )
        BLOCKED = (
            "blocked",
            "Bloqueado",
        )
        REVOKED = (
            "revoked",
            "Revocado",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código",
    )

    name = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Nombre",
    )

    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.TABLET,
        db_index=True,
        verbose_name="Tipo de dispositivo",
    )

    ownership_type = models.CharField(
        max_length=20,
        choices=OwnershipType.choices,
        default=OwnershipType.COMPANY,
        db_index=True,
        verbose_name="Propiedad",
    )

    registration_status = models.CharField(
        max_length=20,
        choices=RegistrationStatus.choices,
        default=RegistrationStatus.PENDING,
        db_index=True,
        verbose_name="Estado de registro",
    )

    work_location = models.ForeignKey(
        WorkLocation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="attendance_devices",
        verbose_name="Ubicación asignada",
    )

    assigned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_attendance_devices",
        verbose_name="Usuario asignado",
    )

    device_identifier = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="Identificador del dispositivo",
        help_text=(
            "Identificador generado por la aplicación, navegador "
            "o terminal."
        ),
    )

    device_identifier_hash = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="Hash del identificador",
    )

    hardware_serial = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Serie del equipo",
    )

    manufacturer = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Fabricante",
    )

    model_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Modelo",
    )

    operating_system = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Sistema operativo",
    )

    operating_system_version = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Versión del sistema operativo",
    )

    browser_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Navegador",
    )

    browser_version = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Versión del navegador",
    )

    app_version = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Versión de la aplicación",
    )

    local_ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP local",
    )

    last_public_ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Última dirección IP pública",
    )

    mac_address = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Dirección MAC",
    )

    allows_attendance_clocking = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Permite marcar asistencia",
    )

    allows_break_clocking = models.BooleanField(
        default=True,
        verbose_name="Permite marcar refrigerio",
    )

    allows_operational_clocking = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Permite registrar actividad operativa",
    )

    allows_multiple_users = models.BooleanField(
        default=False,
        verbose_name="Permite varios usuarios",
        help_text=(
            "Debe activarse para tablets o terminales compartidos."
        ),
    )

    requires_user_authentication = models.BooleanField(
        default=True,
        verbose_name="Requiere autenticación del usuario",
    )

    requires_pin = models.BooleanField(
        default=False,
        verbose_name="Requiere PIN",
    )

    requires_photo = models.BooleanField(
        default=False,
        verbose_name="Requiere fotografía",
    )

    requires_location = models.BooleanField(
        default=False,
        verbose_name="Requiere ubicación",
    )

    restrict_to_assigned_location = models.BooleanField(
        default=True,
        verbose_name="Restringir a ubicación asignada",
    )

    allow_offline_clocking = models.BooleanField(
        default=False,
        verbose_name="Permitir marcación sin conexión",
    )

    maximum_offline_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Máximo de minutos sin conexión",
    )

    clocking_token_hash = models.CharField(
        max_length=128,
        blank=True,
        editable=False,
        verbose_name="Hash del token de marcación",
    )

    token_created_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Token creado el",
    )

    token_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Token vence el",
    )

    last_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Última conexión",
    )

    last_clocking_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Última marcación",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Aprobado el",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_devices_approved",
        verbose_name="Aprobado por",
    )

    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Rechazado el",
    )

    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_devices_rejected",
        verbose_name="Rechazado por",
    )

    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de rechazo",
    )

    blocked_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Bloqueado el",
    )

    blocked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_devices_blocked",
        verbose_name="Bloqueado por",
    )

    blocked_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de bloqueo",
    )

    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Revocado el",
    )

    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_devices_revoked",
        verbose_name="Revocado por",
    )

    revocation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de revocación",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activo",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Creado el",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        db_index=True,
        verbose_name="Actualizado el",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_devices_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_devices_updated",
        verbose_name="Actualizado por",
    )

    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Archivado el",
    )

    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attendance_devices_archived",
        verbose_name="Archivado por",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
    )

    class Meta:
        verbose_name = "Dispositivo de asistencia"
        verbose_name_plural = "Dispositivos de asistencia"

        ordering = (
            "name",
            "code",
        )

        indexes = (
            models.Index(
                fields=(
                    "registration_status",
                    "is_active",
                ),
                name="att_dev_status_active_idx",
            ),
            models.Index(
                fields=(
                    "work_location",
                    "device_type",
                ),
                name="att_dev_location_type_idx",
            ),
            models.Index(
                fields=(
                    "assigned_user",
                    "registration_status",
                ),
                name="att_dev_user_status_idx",
            ),
            models.Index(
                fields=(
                    "allows_attendance_clocking",
                    "allows_operational_clocking",
                ),
                name="att_dev_att_oper_idx",
            ),
            models.Index(
                fields=(
                    "last_seen_at",
                    "last_clocking_at",
                ),
                name="att_dev_seen_clock_idx",
            ),
            models.Index(
                fields=(
                    "token_expires_at",
                    "is_active",
                ),
                name="att_dev_token_active_idx",
            ),
        )

        constraints = (
            models.CheckConstraint(
                condition=models.Q(
                    maximum_offline_minutes__lte=10080,
                ),
                name="att_dev_offline_max_week",
            ),
        )

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_approved(self):
        return (
            self.registration_status
            == self.RegistrationStatus.APPROVED
        )

    @property
    def is_blocked(self):
        return (
            self.registration_status
            == self.RegistrationStatus.BLOCKED
        )

    @property
    def is_revoked(self):
        return (
            self.registration_status
            == self.RegistrationStatus.REVOKED
        )

    @property
    def token_is_valid(self):
        if not self.clocking_token_hash:
            return False

        if (
            self.token_expires_at
            and self.token_expires_at <= timezone.now()
        ):
            return False

        return True

    @property
    def can_clock(self):
        return (
            self.is_active
            and self.archived_at is None
            and self.is_approved
            and not self.is_blocked
            and not self.is_revoked
            and self.allows_attendance_clocking
        )

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.work_location_id
            and self.work_location.archived_at
        ):
            errors["work_location"] = (
                "La ubicación asignada está archivada."
            )

        if (
            self.work_location_id
            and not self.work_location.is_active
        ):
            errors["work_location"] = (
                "La ubicación asignada está inactiva."
            )

        if (
            self.restrict_to_assigned_location
            and not self.work_location_id
        ):
            errors["work_location"] = (
                "Debes asignar una ubicación cuando el dispositivo "
                "está restringido a una sede."
            )

        if (
            self.assigned_user_id
            and self.allows_multiple_users
        ):
            errors["assigned_user"] = (
                "Un dispositivo compartido no debe estar asignado "
                "a un solo usuario."
            )

        if (
            not self.allows_multiple_users
            and not self.assigned_user_id
            and self.ownership_type
            == self.OwnershipType.EMPLOYEE
        ):
            errors["assigned_user"] = (
                "Un dispositivo personal debe estar asignado "
                "a un usuario."
            )

        if (
            self.allow_offline_clocking
            and self.maximum_offline_minutes <= 0
        ):
            errors["maximum_offline_minutes"] = (
                "Debes indicar cuánto tiempo se permite marcar "
                "sin conexión."
            )

        if (
            not self.allow_offline_clocking
            and self.maximum_offline_minutes
        ):
            errors["maximum_offline_minutes"] = (
                "Los minutos sin conexión deben ser cero cuando "
                "la marcación offline está desactivada."
            )

        if (
            self.requires_location
            and self.work_location_id
            and not self.work_location.has_coordinates
        ):
            errors["work_location"] = (
                "La ubicación asignada no tiene coordenadas "
                "configuradas."
            )

        if (
            self.registration_status
            == self.RegistrationStatus.APPROVED
            and not self.approved_at
        ):
            errors["approved_at"] = (
                "Un dispositivo aprobado debe tener fecha "
                "de aprobación."
            )

        if (
            self.registration_status
            == self.RegistrationStatus.REJECTED
            and not self.rejection_reason.strip()
        ):
            errors["rejection_reason"] = (
                "Debes indicar el motivo de rechazo."
            )

        if (
            self.registration_status
            == self.RegistrationStatus.BLOCKED
            and not self.blocked_reason.strip()
        ):
            errors["blocked_reason"] = (
                "Debes indicar el motivo de bloqueo."
            )

        if (
            self.registration_status
            == self.RegistrationStatus.REVOKED
            and not self.revocation_reason.strip()
        ):
            errors["revocation_reason"] = (
                "Debes indicar el motivo de revocación."
            )

        if (
            self.token_expires_at
            and not self.token_created_at
        ):
            errors["token_created_at"] = (
                "Debes registrar la fecha de creación del token."
            )

        if (
            self.token_expires_at
            and self.token_created_at
            and self.token_expires_at
            <= self.token_created_at
        ):
            errors["token_expires_at"] = (
                "La fecha de vencimiento debe ser posterior "
                "a la creación del token."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.device_identifier = str(
            self.device_identifier or ""
        ).strip()

        if self.device_identifier:
            self.device_identifier_hash = (
                hashlib.sha256(
                    self.device_identifier.encode(
                        "utf-8"
                    )
                ).hexdigest()
            )

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def approve(self, user=None):
        if self.archived_at is not None:
            raise ValidationError(
                "No puedes aprobar un dispositivo archivado."
            )

        if (
            self.registration_status
            == self.RegistrationStatus.REVOKED
        ):
            raise ValidationError(
                "No puedes aprobar un dispositivo revocado."
            )

        self.registration_status = (
            self.RegistrationStatus.APPROVED
        )

        self.approved_at = timezone.now()
        self.approved_by = user

        self.rejected_at = None
        self.rejected_by = None
        self.rejection_reason = ""

        self.blocked_at = None
        self.blocked_by = None
        self.blocked_reason = ""

        self.updated_by = user
        self.is_active = True

        self.save(
            update_fields=[
                "registration_status",
                "approved_at",
                "approved_by",
                "rejected_at",
                "rejected_by",
                "rejection_reason",
                "blocked_at",
                "blocked_by",
                "blocked_reason",
                "updated_by",
                "is_active",
                "device_identifier_hash",
                "updated_at",
            ]
        )

    def reject(self, user=None, reason=""):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de rechazo."
            )

        self.registration_status = (
            self.RegistrationStatus.REJECTED
        )

        self.rejected_at = timezone.now()
        self.rejected_by = user
        self.rejection_reason = reason
        self.updated_by = user

        self.save(
            update_fields=[
                "registration_status",
                "rejected_at",
                "rejected_by",
                "rejection_reason",
                "updated_by",
                "device_identifier_hash",
                "updated_at",
            ]
        )

    def block(self, user=None, reason=""):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de bloqueo."
            )

        self.registration_status = (
            self.RegistrationStatus.BLOCKED
        )

        self.blocked_at = timezone.now()
        self.blocked_by = user
        self.blocked_reason = reason
        self.updated_by = user

        self.save(
            update_fields=[
                "registration_status",
                "blocked_at",
                "blocked_by",
                "blocked_reason",
                "updated_by",
                "device_identifier_hash",
                "updated_at",
            ]
        )

    def unblock(self, user=None):
        if (
            self.registration_status
            != self.RegistrationStatus.BLOCKED
        ):
            raise ValidationError(
                "El dispositivo no está bloqueado."
            )

        self.registration_status = (
            self.RegistrationStatus.APPROVED
        )

        self.blocked_at = None
        self.blocked_by = None
        self.blocked_reason = ""

        self.approved_at = timezone.now()
        self.approved_by = user
        self.updated_by = user
        self.is_active = True

        self.save(
            update_fields=[
                "registration_status",
                "blocked_at",
                "blocked_by",
                "blocked_reason",
                "approved_at",
                "approved_by",
                "updated_by",
                "is_active",
                "device_identifier_hash",
                "updated_at",
            ]
        )

    def revoke(self, user=None, reason=""):
        reason = str(
            reason or ""
        ).strip()

        if not reason:
            raise ValidationError(
                "Debes indicar el motivo de revocación."
            )

        self.registration_status = (
            self.RegistrationStatus.REVOKED
        )

        self.revoked_at = timezone.now()
        self.revoked_by = user
        self.revocation_reason = reason

        self.is_active = False
        self.clocking_token_hash = ""
        self.token_created_at = None
        self.token_expires_at = None
        self.updated_by = user

        self.save(
            update_fields=[
                "registration_status",
                "revoked_at",
                "revoked_by",
                "revocation_reason",
                "is_active",
                "clocking_token_hash",
                "token_created_at",
                "token_expires_at",
                "updated_by",
                "device_identifier_hash",
                "updated_at",
            ]
        )

    def register_seen(
        self,
        public_ip_address=None,
    ):
        self.last_seen_at = timezone.now()

        update_fields = [
            "last_seen_at",
            "device_identifier_hash",
            "updated_at",
        ]

        if public_ip_address:
            self.last_public_ip_address = (
                public_ip_address
            )

            update_fields.append(
                "last_public_ip_address"
            )

        self.save(
            update_fields=update_fields
        )

    def register_clocking(self):
        self.last_clocking_at = timezone.now()

        self.save(
            update_fields=[
                "last_clocking_at",
                "device_identifier_hash",
                "updated_at",
            ]
        )

    def archive(self, user=None, reason=""):
        self.is_active = False
        self.archived_at = timezone.now()
        self.archived_by = user
        self.archived_reason = reason
        self.updated_by = user

        self.save(
            update_fields=[
                "is_active",
                "archived_at",
                "archived_by",
                "archived_reason",
                "updated_by",
                "device_identifier_hash",
                "updated_at",
            ]
        )

    def restore(self, user=None):
        self.archived_at = None
        self.archived_by = None
        self.archived_reason = ""
        self.updated_by = user

        if (
            self.registration_status
            == self.RegistrationStatus.APPROVED
        ):
            self.is_active = True

        self.save(
            update_fields=[
                "archived_at",
                "archived_by",
                "archived_reason",
                "updated_by",
                "is_active",
                "device_identifier_hash",
                "updated_at",
            ]
        )