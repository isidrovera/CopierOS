# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base import PartnerBaseModel
from .partner import Partner


class DocumentLookupLog(PartnerBaseModel):
    """
    Historial de consultas de DNI y RUC realizadas desde Copier OS.

    Guarda la respuesta original de la API para fines de:

    - Auditoría.
    - Diagnóstico.
    - Seguimiento de errores.
    - Verificación de datos utilizados.
    - Control de consultas realizadas por usuario.

    Este modelo no almacena claves ni tokens de acceso.
    """

    DOCUMENT_DNI = "dni"
    DOCUMENT_RUC = "ruc"

    DOCUMENT_TYPE_CHOICES = (
        (
            DOCUMENT_DNI,
            "DNI",
        ),
        (
            DOCUMENT_RUC,
            "RUC",
        ),
    )

    PROVIDER_SUNAT_API = "sunat_api"
    PROVIDER_MANUAL = "manual"
    PROVIDER_OTHER = "other"

    PROVIDER_CHOICES = (
        (
            PROVIDER_SUNAT_API,
            "API de consulta SUNAT",
        ),
        (
            PROVIDER_MANUAL,
            "Consulta manual",
        ),
        (
            PROVIDER_OTHER,
            "Otro proveedor",
        ),
    )

    STATUS_SUCCESS = "success"
    STATUS_NOT_FOUND = "not_found"
    STATUS_VALIDATION_ERROR = "validation_error"
    STATUS_PROVIDER_ERROR = "provider_error"
    STATUS_CONNECTION_ERROR = "connection_error"
    STATUS_TIMEOUT = "timeout"
    STATUS_UNKNOWN_ERROR = "unknown_error"

    STATUS_CHOICES = (
        (
            STATUS_SUCCESS,
            "Consulta exitosa",
        ),
        (
            STATUS_NOT_FOUND,
            "Documento no encontrado",
        ),
        (
            STATUS_VALIDATION_ERROR,
            "Documento inválido",
        ),
        (
            STATUS_PROVIDER_ERROR,
            "Error del proveedor",
        ),
        (
            STATUS_CONNECTION_ERROR,
            "Error de conexión",
        ),
        (
            STATUS_TIMEOUT,
            "Tiempo de espera agotado",
        ),
        (
            STATUS_UNKNOWN_ERROR,
            "Error desconocido",
        ),
    )

    ACTION_LOOKUP = "lookup"
    ACTION_CREATED_PARTNER = "created_partner"
    ACTION_UPDATED_PARTNER = "updated_partner"
    ACTION_NOT_APPLIED = "not_applied"

    RESULT_ACTION_CHOICES = (
        (
            ACTION_LOOKUP,
            "Solo consulta",
        ),
        (
            ACTION_CREATED_PARTNER,
            "Se creó un tercero",
        ),
        (
            ACTION_UPDATED_PARTNER,
            "Se actualizó un tercero",
        ),
        (
            ACTION_NOT_APPLIED,
            "Datos no aplicados",
        ),
    )

    document_type = models.CharField(
        max_length=10,
        choices=DOCUMENT_TYPE_CHOICES,
        db_index=True,
        verbose_name="Tipo de documento",
    )

    document_number = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name="Número de documento",
    )

    provider = models.CharField(
        max_length=30,
        choices=PROVIDER_CHOICES,
        default=PROVIDER_SUNAT_API,
        db_index=True,
        verbose_name="Proveedor de consulta",
    )

    provider_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nombre del proveedor",
        help_text=(
            "Nombre comercial o técnico del servicio consultado."
        ),
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="partner_document_lookups",
        verbose_name="Consultado por",
    )

    partner = models.ForeignKey(
        Partner,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="document_lookups",
        verbose_name="Tercero relacionado",
        help_text=(
            "Se completa cuando la consulta se utiliza "
            "para crear o actualizar un tercero."
        ),
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_SUCCESS,
        db_index=True,
        verbose_name="Resultado",
    )

    result_action = models.CharField(
        max_length=30,
        choices=RESULT_ACTION_CHOICES,
        default=ACTION_LOOKUP,
        db_index=True,
        verbose_name="Acción realizada",
    )

    http_status_code = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Código HTTP",
    )

    is_successful = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Consulta exitosa",
    )

    response_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Respuesta de la API",
        help_text=(
            "Copia de la respuesta recibida desde el proveedor."
        ),
    )

    normalized_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos normalizados",
        help_text=(
            "Datos transformados al formato utilizado por Copier OS."
        ),
    )

    request_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos de solicitud",
        help_text=(
            "Información no sensible utilizada para la consulta."
        ),
    )

    error_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de error",
    )

    response_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo de respuesta en milisegundos",
    )

    cache_used = models.BooleanField(
        default=False,
        verbose_name="Respuesta obtenida desde caché",
    )

    provider_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de actualización del proveedor",
        help_text=(
            "Fecha informada por el proveedor para sus datos."
        ),
    )

    applied_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de aplicación de los datos",
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

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Consulta de documento"
        verbose_name_plural = "Consultas de documentos"

        ordering = (
            "-created_at",
        )

        indexes = [
            models.Index(
                fields=[
                    "document_type",
                    "document_number",
                    "created_at",
                ],
                name="partners_lookup_document_idx",
            ),
            models.Index(
                fields=[
                    "requested_by",
                    "created_at",
                ],
                name="partners_lookup_user_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "created_at",
                ],
                name="partners_lookup_status_idx",
            ),
            models.Index(
                fields=[
                    "partner",
                    "created_at",
                ],
                name="partners_lookup_partner_idx",
            ),
            models.Index(
                fields=[
                    "provider",
                    "http_status_code",
                ],
                name="partners_lookup_provider_idx",
            ),
        ]

    def clean(self):
        """
        Valida y normaliza la información de la consulta.
        """

        super().clean()

        errors = {}

        self.document_number = str(
            self.document_number or ""
        ).replace(" ", "").strip()

        self.provider_name = str(
            self.provider_name or ""
        ).strip()

        self.error_message = str(
            self.error_message or ""
        ).strip()

        if not self.document_type:
            errors["document_type"] = (
                "Debes indicar el tipo de documento."
            )

        if not self.document_number:
            errors["document_number"] = (
                "Debes ingresar el número de documento."
            )

        if self.document_type == self.DOCUMENT_DNI:
            if (
                not self.document_number.isdigit()
                or len(self.document_number) != 8
            ):
                errors["document_number"] = (
                    "El DNI debe contener exactamente "
                    "8 números."
                )

        if self.document_type == self.DOCUMENT_RUC:
            if (
                not self.document_number.isdigit()
                or len(self.document_number) != 11
            ):
                errors["document_number"] = (
                    "El RUC debe contener exactamente "
                    "11 números."
                )

            elif not Partner.is_valid_peruvian_ruc(
                self.document_number
            ):
                errors["document_number"] = (
                    "El RUC no supera la validación "
                    "del dígito verificador."
                )

        if (
            self.is_successful
            and self.status != self.STATUS_SUCCESS
        ):
            errors["status"] = (
                "Una consulta exitosa debe tener "
                "el estado de consulta exitosa."
            )

        if (
            self.status == self.STATUS_SUCCESS
            and not self.is_successful
        ):
            errors["is_successful"] = (
                "El estado exitoso debe marcar la "
                "consulta como exitosa."
            )

        if (
            not self.is_successful
            and not self.error_message
            and self.status
            not in (
                self.STATUS_NOT_FOUND,
                self.STATUS_VALIDATION_ERROR,
            )
        ):
            errors["error_message"] = (
                "Debes guardar el mensaje del error recibido."
            )

        if (
            self.result_action
            in (
                self.ACTION_CREATED_PARTNER,
                self.ACTION_UPDATED_PARTNER,
            )
            and not self.partner_id
        ):
            errors["partner"] = (
                "Debes indicar el tercero creado o actualizado."
            )

        if (
            self.partner_id
            and self.document_number
            and self.partner.document_number
            != self.document_number
        ):
            errors["partner"] = (
                "El documento del tercero relacionado "
                "no coincide con el documento consultado."
            )

        if errors:
            raise ValidationError(errors)

    @property
    def display_document(self):
        """
        Devuelve el documento listo para mostrar.
        """

        document_name = self.get_document_type_display()

        return (
            f"{document_name} "
            f"{self.document_number}"
        )

    @property
    def has_response(self):
        """
        Indica si se guardó una respuesta del proveedor.
        """

        return bool(
            self.response_data
        )

    @property
    def was_applied(self):
        """
        Indica si la consulta creó o actualizó un tercero.
        """

        return self.result_action in (
            self.ACTION_CREATED_PARTNER,
            self.ACTION_UPDATED_PARTNER,
        )

    def save(
        self,
        *args,
        **kwargs,
    ):
        """
        Normaliza y valida el registro antes de guardarlo.
        """

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )

    def __str__(self):
        return (
            f"{self.display_document} - "
            f"{self.get_status_display()}"
        )