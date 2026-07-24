# -*- coding: utf-8 -*-
import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


def user_photo_path(instance, filename):
    """
    Guarda las fotografías organizadas por usuario.

    Ejemplo:
    users/550e8400-e29b-41d4-a716-446655440000/profile.jpg
    """
    extension = os.path.splitext(filename)[1].lower() or ".jpg"

    return f"users/{instance.id}/profile{extension}"


dni_validator = RegexValidator(
    regex=r"^\d{8}$",
    message="El DNI debe contener exactamente 8 números.",
)

phone_validator = RegexValidator(
    regex=r"^\+?[0-9\s\-()]{6,20}$",
    message="Ingresa un número telefónico válido.",
)


class User(AbstractUser):
    """
    Usuario principal de Copier OS.

    Permite:
    - Inicio de sesión por correo.
    - Registro manual o mediante consulta de DNI.
    - Datos personales y laborales.
    - Activación, desactivación y archivado lógico.
    - Control de cambio obligatorio de contraseña.
    """

    REGISTRATION_SOURCE_MANUAL = "manual"
    REGISTRATION_SOURCE_DNI = "dni"

    REGISTRATION_SOURCE_CHOICES = (
        (
            REGISTRATION_SOURCE_MANUAL,
            "Registro manual",
        ),
        (
            REGISTRATION_SOURCE_DNI,
            "Consulta por DNI",
        ),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    email = models.EmailField(
        unique=True,
        db_index=True,
        verbose_name="Correo electrónico",
    )

    dni = models.CharField(
        max_length=8,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        validators=[dni_validator],
        verbose_name="DNI",
    )

    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nombres",
    )

    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Apellidos",
    )

    paternal_last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Apellido paterno",
    )

    maternal_last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Apellido materno",
    )

    photo = models.ImageField(
        upload_to=user_photo_path,
        null=True,
        blank=True,
        verbose_name="Fotografía",
    )

    personal_phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[phone_validator],
        verbose_name="Celular personal",
    )

    work_phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[phone_validator],
        verbose_name="Teléfono de trabajo",
    )

    work_extension = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Anexo",
    )

    job_title = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Cargo",
    )

    department_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Área o departamento",
    )

    company_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Empresa",
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Dirección",
    )

    ubigeo = models.CharField(
        max_length=6,
        blank=True,
        verbose_name="Ubigeo",
    )

    district = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Distrito",
    )

    province = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Provincia",
    )

    region = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Departamento",
    )

    registration_source = models.CharField(
        max_length=20,
        choices=REGISTRATION_SOURCE_CHOICES,
        default=REGISTRATION_SOURCE_MANUAL,
        verbose_name="Origen del registro",
    )

    dni_data_verified = models.BooleanField(
        default=False,
        verbose_name="Datos de DNI consultados",
    )

    dni_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de consulta de DNI",
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name="Usuario verificado",
    )

    email_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Correo verificado el",
    )

    must_change_password = models.BooleanField(
        default=True,
        verbose_name="Debe cambiar contraseña",
    )

    password_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Contraseña cambiada el",
    )

    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Intentos fallidos",
    )

    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Bloqueado hasta",
    )

    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Archivado el",
    )

    archived_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de archivado",
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
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users_created",
        verbose_name="Creado por",
    )

    updated_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users_updated",
        verbose_name="Actualizado por",
    )

    archived_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users_archived",
        verbose_name="Archivado por",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = (
            "first_name",
            "paternal_last_name",
            "maternal_last_name",
            "email",
        )

    def __str__(self):
        return self.full_name or self.email

    @property
    def full_name(self):
        names = [
            self.first_name,
            self.paternal_last_name,
            self.maternal_last_name,
        ]

        full_name = " ".join(
            value.strip()
            for value in names
            if value and value.strip()
        )

        return full_name or self.username or self.email

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def is_locked(self):
        if not self.locked_until:
            return False

        return self.locked_until > timezone.now()

    def mark_dni_as_verified(self):
        self.dni_data_verified = True
        self.dni_verified_at = timezone.now()
        self.registration_source = self.REGISTRATION_SOURCE_DNI

    def register_failed_login(self):
        self.failed_login_attempts += 1

    def reset_failed_login(self):
        self.failed_login_attempts = 0
        self.locked_until = None

    def archive(self, user=None, reason=""):
        """
        Desactiva y archiva el usuario sin borrar su historial.
        """
        self.is_active = False
        self.archived_at = timezone.now()
        self.archived_by = user
        self.archived_reason = reason

    def restore(self, user=None):
        """
        Restaura un usuario archivado.
        """
        self.is_active = True
        self.archived_at = None
        self.archived_by = None
        self.archived_reason = ""
        self.updated_by = user

    def set_new_password(
        self,
        raw_password,
        force_change=False,
    ):
        """
        Cambia la contraseña usando el hash seguro de Django.
        """
        self.set_password(raw_password)
        self.password_changed_at = timezone.now()
        self.must_change_password = force_change