# -*- coding: utf-8 -*-
import ipaddress

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RepairBaseModel
from .repair import Repair


class RepairSNMPValidation(RepairBaseModel):
    """
    Validación SNMP realizada durante una reparación.

    Permite comparar los datos detectados por red con los datos
    registrados en el sistema, incluyendo:

    - Dirección IP.
    - Marca.
    - Modelo.
    - Número de serie.
    - Nombre del sistema.
    - Contadores.
    - Estado de comunicación.
    """

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        CONNECTING = (
            "connecting",
            "Conectando",
        )
        SUCCESS = (
            "success",
            "Validación correcta",
        )
        SUCCESS_WITH_OBSERVATIONS = (
            "success_with_observations",
            "Correcta con observaciones",
        )
        FAILED = (
            "failed",
            "Fallida",
        )
        NOT_SUPPORTED = (
            "not_supported",
            "SNMP no soportado",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )

    class SNMPVersion(models.TextChoices):
        V1 = (
            "v1",
            "SNMP v1",
        )
        V2C = (
            "v2c",
            "SNMP v2c",
        )
        V3 = (
            "v3",
            "SNMP v3",
        )

    repair = models.ForeignKey(
        Repair,
        on_delete=models.CASCADE,
        related_name="snmp_validations",
        verbose_name="Reparación",
    )

    status = models.CharField(
        max_length=40,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    snmp_version = models.CharField(
        max_length=10,
        choices=SNMPVersion.choices,
        default=SNMPVersion.V2C,
        db_index=True,
        verbose_name="Versión SNMP",
    )

    ip_address = models.GenericIPAddressField(
        protocol="both",
        unpack_ipv4=True,
        db_index=True,
        verbose_name="Dirección IP",
    )

    port = models.PositiveIntegerField(
        default=161,
        verbose_name="Puerto SNMP",
    )

    community = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Comunidad SNMP",
        help_text=(
            "No debe mostrarse en respuestas públicas "
            "ni informes técnicos."
        ),
    )

    detected_manufacturer = models.CharField(
        max_length=180,
        blank=True,
        db_index=True,
        verbose_name="Fabricante detectado",
    )

    detected_model = models.CharField(
        max_length=180,
        blank=True,
        db_index=True,
        verbose_name="Modelo detectado",
    )

    detected_serial_number = models.CharField(
        max_length=180,
        blank=True,
        db_index=True,
        verbose_name="Serie detectada",
    )

    detected_system_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre del sistema",
    )

    detected_hostname = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre de host",
    )

    detected_firmware = models.CharField(
        max_length=180,
        blank=True,
        verbose_name="Firmware detectado",
    )

    detected_mac_address = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Dirección MAC",
    )

    detected_total_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador total detectado",
    )

    detected_black_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador blanco y negro detectado",
    )

    detected_color_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador color detectado",
    )

    detected_scan_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador de escaneo detectado",
    )

    manufacturer_matches = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Coincide fabricante",
    )

    model_matches = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Coincide modelo",
    )

    serial_number_matches = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Coincide número de serie",
    )

    communication_successful = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Comunicación correcta",
    )

    response_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo de respuesta en milisegundos",
    )

    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_snmp_validations",
        verbose_name="Validado por",
    )

    validated_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de validación",
    )

    error_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de error",
    )

    observations = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    raw_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos SNMP sin procesar",
        help_text=(
            "Datos técnicos obtenidos durante la consulta SNMP. "
            "No deben incluir credenciales."
        ),
    )

    is_required = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Validación obligatoria",
    )

    class Meta:
        verbose_name = "Validación SNMP de reparación"
        verbose_name_plural = "Validaciones SNMP de reparaciones"
        ordering = (
            "-validated_at",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "repair",
                    "status",
                ],
                name="repair_snmp_status_idx",
            ),
            models.Index(
                fields=[
                    "ip_address",
                    "validated_at",
                ],
                name="repair_snmp_ip_idx",
            ),
            models.Index(
                fields=[
                    "serial_number_matches",
                    "model_matches",
                ],
                name="repair_snmp_match_idx",
            ),
            models.Index(
                fields=[
                    "communication_successful",
                    "status",
                ],
                name="repair_snmp_comm_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.repair.code} - "
            f"{self.ip_address}"
        )

    def clean(self):
        """
        Normaliza y valida la información SNMP.
        """

        super().clean()

        self.community = str(
            self.community or ""
        ).strip()

        self.detected_manufacturer = str(
            self.detected_manufacturer or ""
        ).strip()

        self.detected_model = str(
            self.detected_model or ""
        ).strip()

        self.detected_serial_number = str(
            self.detected_serial_number or ""
        ).strip().upper()

        self.detected_system_name = str(
            self.detected_system_name or ""
        ).strip()

        self.detected_hostname = str(
            self.detected_hostname or ""
        ).strip()

        self.detected_firmware = str(
            self.detected_firmware or ""
        ).strip()

        self.detected_mac_address = str(
            self.detected_mac_address or ""
        ).strip().upper()

        self.error_message = str(
            self.error_message or ""
        ).strip()

        self.observations = str(
            self.observations or ""
        ).strip()

        if not self.repair_id:
            raise ValidationError(
                {
                    "repair": (
                        "La reparación es obligatoria."
                    ),
                }
            )

        if not self.ip_address:
            raise ValidationError(
                {
                    "ip_address": (
                        "La dirección IP es obligatoria."
                    ),
                }
            )

        try:
            ipaddress.ip_address(
                str(self.ip_address)
            )
        except ValueError as exc:
            raise ValidationError(
                {
                    "ip_address": (
                        "La dirección IP no es válida."
                    ),
                }
            ) from exc

        if self.port < 1 or self.port > 65535:
            raise ValidationError(
                {
                    "port": (
                        "El puerto debe estar entre 1 y 65535."
                    ),
                }
            )

        if (
            self.snmp_version
            in [
                self.SNMPVersion.V1,
                self.SNMPVersion.V2C,
            ]
            and not self.community
        ):
            raise ValidationError(
                {
                    "community": (
                        "Debe indicar la comunidad SNMP."
                    ),
                }
            )

        if self.status == self.Status.PENDING:
            if self.validated_at:
                raise ValidationError(
                    {
                        "validated_at": (
                            "Una validación pendiente no debe tener "
                            "fecha de validación."
                        ),
                    }
                )

            if self.validated_by_id:
                raise ValidationError(
                    {
                        "validated_by": (
                            "Una validación pendiente no debe tener "
                            "usuario validador."
                        ),
                    }
                )

        if self.status in [
            self.Status.SUCCESS,
            self.Status.SUCCESS_WITH_OBSERVATIONS,
            self.Status.FAILED,
            self.Status.NOT_SUPPORTED,
            self.Status.NOT_APPLICABLE,
        ]:
            if not self.validated_at:
                raise ValidationError(
                    {
                        "validated_at": (
                            "Debe registrar la fecha de validación."
                        ),
                    }
                )

            if not self.validated_by_id:
                raise ValidationError(
                    {
                        "validated_by": (
                            "Debe indicar quién realizó "
                            "la validación."
                        ),
                    }
                )

        if self.status == self.Status.SUCCESS:
            if not self.communication_successful:
                raise ValidationError(
                    {
                        "communication_successful": (
                            "Una validación correcta debe tener "
                            "comunicación SNMP exitosa."
                        ),
                    }
                )

            if not self.model_matches:
                raise ValidationError(
                    {
                        "model_matches": (
                            "El modelo detectado debe coincidir."
                        ),
                    }
                )

            if not self.serial_number_matches:
                raise ValidationError(
                    {
                        "serial_number_matches": (
                            "La serie detectada debe coincidir."
                        ),
                    }
                )

        if (
            self.status
            == self.Status.SUCCESS_WITH_OBSERVATIONS
            and not self.observations
        ):
            raise ValidationError(
                {
                    "observations": (
                        "Debe registrar las observaciones "
                        "de la validación."
                    ),
                }
            )

        if self.status == self.Status.FAILED:
            if not self.error_message:
                raise ValidationError(
                    {
                        "error_message": (
                            "Debe registrar el error de la consulta."
                        ),
                    }
                )

        if (
            self.communication_successful
            and self.error_message
        ):
            raise ValidationError(
                {
                    "error_message": (
                        "No debe registrar un error cuando "
                        "la comunicación fue exitosa."
                    ),
                }
            )

        if (
            not self.communication_successful
            and self.status
            in [
                self.Status.SUCCESS,
                self.Status.SUCCESS_WITH_OBSERVATIONS,
            ]
        ):
            raise ValidationError(
                {
                    "communication_successful": (
                        "La comunicación debe ser exitosa "
                        "para aprobar la validación."
                    ),
                }
            )

        meter_values = [
            self.detected_total_meter,
            self.detected_black_meter,
            self.detected_color_meter,
            self.detected_scan_meter,
        ]

        if any(
            value is not None and value < 0
            for value in meter_values
        ):
            raise ValidationError(
                {
                    "detected_total_meter": (
                        "Los contadores detectados no pueden "
                        "ser negativos."
                    ),
                }
            )

    def calculate_matches(self):
        """
        Compara los datos detectados con la máquina registrada.
        """

        equipment = self.repair.equipment

        registered_brand = str(
            getattr(
                getattr(
                    equipment,
                    "brand",
                    None,
                ),
                "name",
                "",
            )
            or ""
        ).strip().lower()

        registered_model = str(
            getattr(
                getattr(
                    equipment,
                    "equipment_model",
                    None,
                ),
                "name",
                "",
            )
            or ""
        ).strip().lower()

        registered_serial = str(
            getattr(
                equipment,
                "serial_number",
                "",
            )
            or ""
        ).strip().upper()

        detected_manufacturer = str(
            self.detected_manufacturer or ""
        ).strip().lower()

        detected_model = str(
            self.detected_model or ""
        ).strip().lower()

        detected_serial = str(
            self.detected_serial_number or ""
        ).strip().upper()

        self.manufacturer_matches = bool(
            registered_brand
            and detected_manufacturer
            and (
                registered_brand
                in detected_manufacturer
                or detected_manufacturer
                in registered_brand
            )
        )

        self.model_matches = bool(
            registered_model
            and detected_model
            and (
                registered_model
                in detected_model
                or detected_model
                in registered_model
            )
        )

        self.serial_number_matches = bool(
            registered_serial
            and detected_serial
            and registered_serial == detected_serial
        )

    def save(self, *args, **kwargs):
        """
        Normaliza, compara datos y actualiza la reparación.
        """

        self.community = str(
            self.community or ""
        ).strip()

        self.detected_manufacturer = str(
            self.detected_manufacturer or ""
        ).strip()

        self.detected_model = str(
            self.detected_model or ""
        ).strip()

        self.detected_serial_number = str(
            self.detected_serial_number or ""
        ).strip().upper()

        self.detected_system_name = str(
            self.detected_system_name or ""
        ).strip()

        self.detected_hostname = str(
            self.detected_hostname or ""
        ).strip()

        self.detected_firmware = str(
            self.detected_firmware or ""
        ).strip()

        self.detected_mac_address = str(
            self.detected_mac_address or ""
        ).strip().upper()

        self.error_message = str(
            self.error_message or ""
        ).strip()

        self.observations = str(
            self.observations or ""
        ).strip()

        if (
            self.status
            not in [
                self.Status.PENDING,
                self.Status.CONNECTING,
            ]
            and not self.validated_at
        ):
            self.validated_at = timezone.now()

        if self.communication_successful:
            self.calculate_matches()

        self.full_clean()

        result = super().save(
            *args,
            **kwargs,
        )

        self.update_repair_snmp_status()

        return result

    def delete(self, *args, **kwargs):
        """
        Elimina la validación y recalcula el estado SNMP.
        """

        repair = self.repair

        result = super().delete(
            *args,
            **kwargs,
        )

        self.update_repair_snmp_status(
            repair=repair,
        )

        return result

    def archive(
        self,
        user=None,
        reason="",
        save=True,
    ):
        """
        Archiva la validación y recalcula el estado.
        """

        result = super().archive(
            user=user,
            reason=reason,
            save=save,
        )

        self.update_repair_snmp_status()

        return result

    def restore(
        self,
        user=None,
        save=True,
    ):
        """
        Restaura la validación y recalcula el estado.
        """

        result = super().restore(
            user=user,
            save=save,
        )

        self.update_repair_snmp_status()

        return result

    def update_repair_snmp_status(
        self,
        repair=None,
    ):
        """
        Marca la validación SNMP como completada cuando existe
        al menos una validación obligatoria aprobada.
        """

        repair = repair or self.repair

        required_validations = (
            repair.snmp_validations.filter(
                archived_at__isnull=True,
                is_required=True,
            )
        )

        completed = (
            required_validations.exists()
            and required_validations.filter(
                status__in=[
                    self.Status.SUCCESS,
                    self.Status.SUCCESS_WITH_OBSERVATIONS,
                    self.Status.NOT_SUPPORTED,
                    self.Status.NOT_APPLICABLE,
                ]
            ).exists()
            and not required_validations.filter(
                status__in=[
                    self.Status.PENDING,
                    self.Status.CONNECTING,
                    self.Status.FAILED,
                ]
            ).exists()
        )

        if (
            repair.snmp_validation_completed
            != completed
        ):
            repair.snmp_validation_completed = completed

            repair.save(
                update_fields=[
                    "snmp_validation_completed",
                    "updated_at",
                ]
            )