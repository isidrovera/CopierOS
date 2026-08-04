# -*- coding: utf-8 -*-
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import models

from .base import MonitoringBaseModel


class RawOIDReading(MonitoringBaseModel):
    """
    Lectura histórica original de un OID SNMP.

    Conserva todos los valores recibidos desde el agente,
    incluyendo OID todavía desconocidos o no clasificados.

    Esto permite:

    - Reprocesar capturas antiguas.
    - Crear nuevos perfiles SNMP.
    - Detectar cambios de firmware.
    - Analizar nuevos modelos.
    - Conservar evidencia técnica completa.
    """

    class ValueType(models.TextChoices):
        INTEGER = (
            "integer",
            "Entero",
        )
        UNSIGNED = (
            "unsigned",
            "Entero sin signo",
        )
        COUNTER32 = (
            "counter32",
            "Counter32",
        )
        COUNTER64 = (
            "counter64",
            "Counter64",
        )
        GAUGE = (
            "gauge",
            "Gauge",
        )
        TIMETICKS = (
            "timeticks",
            "TimeTicks",
        )
        DECIMAL = (
            "decimal",
            "Decimal",
        )
        STRING = (
            "string",
            "Texto",
        )
        OCTET_STRING = (
            "octet_string",
            "Octet String",
        )
        HEX_STRING = (
            "hex_string",
            "Cadena hexadecimal",
        )
        OBJECT_IDENTIFIER = (
            "object_identifier",
            "Identificador OID",
        )
        IP_ADDRESS = (
            "ip_address",
            "Dirección IP",
        )
        BOOLEAN = (
            "boolean",
            "Booleano",
        )
        NULL = (
            "null",
            "Nulo",
        )
        NO_SUCH_OBJECT = (
            "no_such_object",
            "No existe el objeto",
        )
        NO_SUCH_INSTANCE = (
            "no_such_instance",
            "No existe la instancia",
        )
        END_OF_MIB = (
            "end_of_mib",
            "Fin de MIB",
        )
        UNKNOWN = (
            "unknown",
            "Tipo desconocido",
        )

    class MappingStatus(models.TextChoices):
        UNKNOWN = (
            "unknown",
            "Sin identificar",
        )
        IDENTIFIED = (
            "identified",
            "Identificado",
        )
        MAPPED = (
            "mapped",
            "Mapeado",
        )
        IGNORED = (
            "ignored",
            "Ignorado",
        )
        INVALID = (
            "invalid",
            "Inválido",
        )
        REVIEW_REQUIRED = (
            "review_required",
            "Requiere revisión",
        )

    class ReadStatus(models.TextChoices):
        SUCCESS = (
            "success",
            "Correcto",
        )
        PARTIAL = (
            "partial",
            "Parcial",
        )
        TIMEOUT = (
            "timeout",
            "Tiempo agotado",
        )
        ACCESS_DENIED = (
            "access_denied",
            "Acceso denegado",
        )
        NOT_SUPPORTED = (
            "not_supported",
            "No soportado",
        )
        PARSE_ERROR = (
            "parse_error",
            "Error de interpretación",
        )
        ERROR = (
            "error",
            "Error",
        )

    snapshot = models.ForeignKey(
        "monitoring.DeviceSnapshot",
        on_delete=models.PROTECT,
        related_name="raw_oid_readings",
        verbose_name="Captura",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        on_delete=models.PROTECT,
        related_name="raw_oid_readings",
        verbose_name="Dispositivo",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_raw_oid_readings",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_raw_oid_readings",
        verbose_name="Sede",
    )

    captured_at = models.DateTimeField(
        db_index=True,
        verbose_name="Fecha de lectura",
    )

    oid = models.CharField(
        max_length=500,
        db_index=True,
        verbose_name="OID completo",
    )

    base_oid = models.CharField(
        max_length=500,
        blank=True,
        db_index=True,
        verbose_name="OID base",
        help_text=(
            "OID sin el índice de tabla cuando este "
            "pueda determinarse."
        ),
    )

    oid_index = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Índice OID",
    )

    mib_name = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Nombre MIB",
    )

    symbol_name = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Nombre simbólico",
    )

    enterprise_number = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Número enterprise",
    )

    value_type = models.CharField(
        max_length=30,
        choices=ValueType.choices,
        default=ValueType.UNKNOWN,
        db_index=True,
        verbose_name="Tipo de valor",
    )

    raw_value = models.TextField(
        blank=True,
        verbose_name="Valor original",
    )

    display_value = models.TextField(
        blank=True,
        verbose_name="Valor visible",
    )

    text_value = models.TextField(
        blank=True,
        verbose_name="Valor de texto",
    )

    numeric_value = models.DecimalField(
        max_digits=40,
        decimal_places=8,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Valor numérico",
    )

    integer_value = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Valor entero",
    )

    boolean_value = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Valor booleano",
    )

    ip_address_value = models.GenericIPAddressField(
        null=True,
        blank=True,
        protocol="both",
        unpack_ipv4=True,
        db_index=True,
        verbose_name="Valor IP",
    )

    object_identifier_value = models.CharField(
        max_length=500,
        blank=True,
        db_index=True,
        verbose_name="Valor OID",
    )

    hexadecimal_value = models.TextField(
        blank=True,
        verbose_name="Valor hexadecimal",
    )

    base64_value = models.TextField(
        blank=True,
        verbose_name="Valor binario Base64",
    )

    timeticks_value = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="TimeTicks original",
    )

    timeticks_seconds = models.DecimalField(
        max_digits=30,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="TimeTicks en segundos",
    )

    read_status = models.CharField(
        max_length=30,
        choices=ReadStatus.choices,
        default=ReadStatus.SUCCESS,
        db_index=True,
        verbose_name="Estado de lectura",
    )

    mapping_status = models.CharField(
        max_length=30,
        choices=MappingStatus.choices,
        default=MappingStatus.UNKNOWN,
        db_index=True,
        verbose_name="Estado de identificación",
    )

    mapped_metric_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Métrica asignada",
    )

    mapped_category = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Categoría asignada",
    )

    profile_metric_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Métrica del perfil",
    )

    profile_version = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Versión del perfil",
    )

    is_known = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="OID conocido",
    )

    is_unknown = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="OID desconocido",
    )

    is_vendor_specific = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="OID específico del fabricante",
    )

    is_sensitive = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Dato sensible",
    )

    is_visible_in_diagnostics = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Visible en diagnóstico",
    )

    read_error_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de error",
    )

    read_error_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de error",
    )

    extra_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Información adicional",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Lectura OID original"
        verbose_name_plural = "Lecturas OID originales"
        ordering = (
            "-captured_at",
            "oid",
        )
        indexes = [
            models.Index(
                fields=[
                    "device",
                    "oid",
                    "captured_at",
                ],
                name="mon_oid_device_oid_idx",
            ),
            models.Index(
                fields=[
                    "customer",
                    "captured_at",
                    "is_unknown",
                ],
                name="mon_oid_customer_unknown_idx",
            ),
            models.Index(
                fields=[
                    "enterprise_number",
                    "is_unknown",
                    "captured_at",
                ],
                name="mon_oid_enterprise_idx",
            ),
            models.Index(
                fields=[
                    "mapping_status",
                    "captured_at",
                ],
                name="mon_oid_mapping_date_idx",
            ),
            models.Index(
                fields=[
                    "profile_metric_code",
                    "captured_at",
                ],
                name="mon_oid_profile_metric_idx",
            ),
            models.Index(
                fields=[
                    "read_status",
                    "captured_at",
                ],
                name="mon_oid_read_status_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "snapshot",
                    "oid",
                ],
                name="unique_snapshot_oid",
            ),
        ]

    def __str__(self):
        return (
            f"{self.device} - "
            f"{self.oid} = "
            f"{self.display_value or self.raw_value}"
        )

    def parse_value(self):
        """
        Intenta guardar el valor recibido en columnas apropiadas.

        El valor original nunca se elimina aunque no pueda
        interpretarse.
        """

        self.text_value = ""
        self.numeric_value = None
        self.integer_value = None
        self.boolean_value = None
        self.ip_address_value = None
        self.object_identifier_value = ""
        self.hexadecimal_value = ""
        self.timeticks_value = None
        self.timeticks_seconds = None

        value = str(
            self.raw_value or ""
        ).strip()

        if not self.display_value:
            self.display_value = value

        if self.value_type in {
            self.ValueType.INTEGER,
            self.ValueType.UNSIGNED,
            self.ValueType.COUNTER32,
            self.ValueType.COUNTER64,
            self.ValueType.GAUGE,
        }:
            try:
                decimal_value = Decimal(value)

                self.numeric_value = decimal_value

                if decimal_value == decimal_value.to_integral_value():
                    self.integer_value = int(decimal_value)
            except (
                InvalidOperation,
                TypeError,
                ValueError,
            ):
                self.read_status = self.ReadStatus.PARSE_ERROR

        elif self.value_type == self.ValueType.DECIMAL:
            try:
                self.numeric_value = Decimal(value)
            except (
                InvalidOperation,
                TypeError,
                ValueError,
            ):
                self.read_status = self.ReadStatus.PARSE_ERROR

        elif self.value_type == self.ValueType.BOOLEAN:
            normalized = value.lower()

            if normalized in {
                "1",
                "true",
                "yes",
                "on",
            }:
                self.boolean_value = True
            elif normalized in {
                "0",
                "false",
                "no",
                "off",
            }:
                self.boolean_value = False
            else:
                self.read_status = self.ReadStatus.PARSE_ERROR

        elif self.value_type == self.ValueType.IP_ADDRESS:
            self.ip_address_value = value or None

        elif (
            self.value_type
            == self.ValueType.OBJECT_IDENTIFIER
        ):
            self.object_identifier_value = value

        elif self.value_type == self.ValueType.HEX_STRING:
            self.hexadecimal_value = value

        elif self.value_type == self.ValueType.TIMETICKS:
            try:
                ticks = int(
                    Decimal(value)
                )

                self.timeticks_value = max(
                    ticks,
                    0,
                )

                self.timeticks_seconds = (
                    Decimal(self.timeticks_value)
                    / Decimal("100")
                )
            except (
                InvalidOperation,
                TypeError,
                ValueError,
            ):
                self.read_status = self.ReadStatus.PARSE_ERROR

        elif self.value_type in {
            self.ValueType.STRING,
            self.ValueType.OCTET_STRING,
            self.ValueType.UNKNOWN,
        }:
            self.text_value = value

    def mark_mapped(
        self,
        *,
        metric_code,
        category="",
        profile_metric_code="",
        profile_version="",
    ):
        self.mapping_status = self.MappingStatus.MAPPED
        self.mapped_metric_code = str(
            metric_code or ""
        ).strip().upper()

        self.mapped_category = str(
            category or ""
        ).strip().lower()

        self.profile_metric_code = str(
            profile_metric_code or ""
        ).strip().upper()

        self.profile_version = str(
            profile_version or ""
        ).strip()

        self.is_known = True
        self.is_unknown = False

        self.save(
            update_fields=[
                "mapping_status",
                "mapped_metric_code",
                "mapped_category",
                "profile_metric_code",
                "profile_version",
                "is_known",
                "is_unknown",
                "updated_at",
            ]
        )

    def mark_review_required(
        self,
        notes="",
    ):
        self.mapping_status = (
            self.MappingStatus.REVIEW_REQUIRED
        )

        self.is_known = False
        self.is_unknown = True

        if notes:
            self.notes = str(
                notes
            ).strip()

        self.save(
            update_fields=[
                "mapping_status",
                "is_known",
                "is_unknown",
                "notes",
                "updated_at",
            ]
        )

    def clean(self):
        super().clean()

        text_fields = [
            "oid",
            "base_oid",
            "oid_index",
            "mib_name",
            "symbol_name",
            "raw_value",
            "display_value",
            "text_value",
            "object_identifier_value",
            "hexadecimal_value",
            "base64_value",
            "mapped_metric_code",
            "mapped_category",
            "profile_metric_code",
            "profile_version",
            "read_error_code",
            "read_error_message",
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
                str(value or "").strip(),
            )

        self.oid = self.oid.strip(".")
        self.base_oid = self.base_oid.strip(".")
        self.object_identifier_value = (
            self.object_identifier_value.strip(".")
        )

        self.mapped_metric_code = (
            self.mapped_metric_code.upper()
        )

        self.profile_metric_code = (
            self.profile_metric_code.upper()
        )

        self.read_error_code = (
            self.read_error_code.upper()
        )

        if not self.snapshot_id:
            raise ValidationError(
                {
                    "snapshot": (
                        "La captura es obligatoria."
                    ),
                }
            )

        if not self.oid:
            raise ValidationError(
                {
                    "oid": (
                        "El OID es obligatorio."
                    ),
                }
            )

        oid_parts = self.oid.split(".")

        if not all(
            part.isdigit()
            for part in oid_parts
            if part
        ):
            raise ValidationError(
                {
                    "oid": (
                        "El OID debe contener únicamente "
                        "números separados por puntos."
                    ),
                }
            )

        if self.snapshot.device_id != self.device_id:
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo no coincide "
                        "con la captura."
                    ),
                }
            )

        if self.snapshot.customer_id != self.customer_id:
            raise ValidationError(
                {
                    "customer": (
                        "El cliente no coincide "
                        "con la captura."
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

        if self.is_known:
            self.is_unknown = False

        if self.mapping_status in {
            self.MappingStatus.IDENTIFIED,
            self.MappingStatus.MAPPED,
        }:
            self.is_known = True
            self.is_unknown = False

        if (
            self.mapping_status
            == self.MappingStatus.UNKNOWN
        ):
            self.is_known = False
            self.is_unknown = True

        if (
            self.read_status != self.ReadStatus.SUCCESS
            and not self.read_error_message
        ):
            self.read_error_message = (
                "La lectura SNMP no se completó correctamente."
            )

    def save(self, *args, **kwargs):
        if self.snapshot_id:
            self.device = self.snapshot.device
            self.customer = self.snapshot.customer
            self.branch = self.snapshot.branch
            self.captured_at = self.snapshot.captured_at

        self.oid = str(
            self.oid or ""
        ).strip().strip(".")

        self.base_oid = str(
            self.base_oid or ""
        ).strip().strip(".")

        self.parse_value()
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
        raise ValidationError(
            "Las lecturas OID históricas no pueden archivarse."
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        raise ValidationError(
            "Las lecturas OID históricas no pueden restaurarse."
        )