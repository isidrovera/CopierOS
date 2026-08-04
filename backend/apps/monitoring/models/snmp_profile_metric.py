# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from .base import MonitoringBaseModel


class SNMPProfileMetric(MonitoringBaseModel):
    """
    Define cómo consultar, interpretar y normalizar una métrica SNMP.

    Cada métrica pertenece a un perfil y puede generar información
    de identidad, contadores, consumibles, componentes, bandejas,
    accesorios, alertas, trabajos o datos originales.
    """

    class MetricCategory(models.TextChoices):
        IDENTITY = (
            "identity",
            "Identidad",
        )
        NETWORK = (
            "network",
            "Red",
        )
        STATUS = (
            "status",
            "Estado",
        )
        COUNTER = (
            "counter",
            "Contador",
        )
        CONSUMABLE = (
            "consumable",
            "Consumible",
        )
        COMPONENT = (
            "component",
            "Componente",
        )
        TRAY = (
            "tray",
            "Bandeja",
        )
        ACCESSORY = (
            "accessory",
            "Accesorio",
        )
        ALERT = (
            "alert",
            "Alerta",
        )
        JOB = (
            "job",
            "Trabajo",
        )
        FIRMWARE = (
            "firmware",
            "Firmware",
        )
        RAW = (
            "raw",
            "Dato original",
        )
        OTHER = (
            "other",
            "Otro",
        )

    class QueryType(models.TextChoices):
        GET = (
            "get",
            "GET",
        )
        GET_NEXT = (
            "get_next",
            "GETNEXT",
        )
        GET_BULK = (
            "get_bulk",
            "GETBULK",
        )
        WALK = (
            "walk",
            "WALK",
        )
        TABLE = (
            "table",
            "Tabla",
        )
        CALCULATED = (
            "calculated",
            "Calculada",
        )

    class ValueType(models.TextChoices):
        AUTO = (
            "auto",
            "Automático",
        )
        INTEGER = (
            "integer",
            "Entero",
        )
        DECIMAL = (
            "decimal",
            "Decimal",
        )
        STRING = (
            "string",
            "Texto",
        )
        BOOLEAN = (
            "boolean",
            "Booleano",
        )
        TIMETICKS = (
            "timeticks",
            "TimeTicks",
        )
        IP_ADDRESS = (
            "ip_address",
            "Dirección IP",
        )
        MAC_ADDRESS = (
            "mac_address",
            "Dirección MAC",
        )
        OBJECT_IDENTIFIER = (
            "object_identifier",
            "OID",
        )
        HEXADECIMAL = (
            "hexadecimal",
            "Hexadecimal",
        )
        DATETIME = (
            "datetime",
            "Fecha y hora",
        )
        PERCENTAGE = (
            "percentage",
            "Porcentaje",
        )
        STATUS_CODE = (
            "status_code",
            "Código de estado",
        )
        JSON = (
            "json",
            "JSON",
        )

    class DestinationModel(models.TextChoices):
        DEVICE = (
            "device",
            "Dispositivo monitoreado",
        )
        SNAPSHOT = (
            "snapshot",
            "Captura",
        )
        COUNTER = (
            "counter",
            "Lectura de contador",
        )
        CONSUMABLE = (
            "consumable",
            "Lectura de consumible",
        )
        COMPONENT = (
            "component",
            "Lectura de componente",
        )
        TRAY = (
            "tray",
            "Lectura de bandeja",
        )
        ACCESSORY = (
            "accessory",
            "Lectura de accesorio",
        )
        ALERT = (
            "alert",
            "Alerta",
        )
        JOB = (
            "job",
            "Lectura de trabajo",
        )
        RAW_OID = (
            "raw_oid",
            "Lectura OID original",
        )
        IGNORE = (
            "ignore",
            "Ignorar",
        )

    class IndexStrategy(models.TextChoices):
        NONE = (
            "none",
            "Sin índice",
        )
        OID_SUFFIX = (
            "oid_suffix",
            "Sufijo del OID",
        )
        LAST_NUMBER = (
            "last_number",
            "Último número",
        )
        FIXED_LENGTH = (
            "fixed_length",
            "Longitud fija",
        )
        RELATED_TABLE = (
            "related_table",
            "Tabla relacionada",
        )
        REGEX = (
            "regex",
            "Expresión regular",
        )
        CUSTOM = (
            "custom",
            "Personalizada",
        )

    class MissingValueBehavior(models.TextChoices):
        IGNORE = (
            "ignore",
            "Ignorar",
        )
        NULL = (
            "null",
            "Guardar nulo",
        )
        ZERO = (
            "zero",
            "Usar cero",
        )
        DEFAULT = (
            "default",
            "Usar valor predeterminado",
        )
        ERROR = (
            "error",
            "Generar error",
        )

    profile = models.ForeignKey(
        "monitoring.SNMPProfile",
        on_delete=models.CASCADE,
        related_name="metrics",
        verbose_name="Perfil SNMP",
    )

    code = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Código",
        help_text=(
            "Código estable dentro del perfil. "
            "Ejemplo: TONER_BLACK_LEVEL."
        ),
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Nombre",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    category = models.CharField(
        max_length=30,
        choices=MetricCategory.choices,
        default=MetricCategory.RAW,
        db_index=True,
        verbose_name="Categoría",
    )

    query_type = models.CharField(
        max_length=20,
        choices=QueryType.choices,
        default=QueryType.GET,
        db_index=True,
        verbose_name="Tipo de consulta",
    )

    destination_model = models.CharField(
        max_length=30,
        choices=DestinationModel.choices,
        default=DestinationModel.RAW_OID,
        db_index=True,
        verbose_name="Destino",
    )

    destination_field = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Campo de destino",
        help_text=(
            "Campo normalizado que recibirá el valor. "
            "Ejemplo: raw_serial_number, percentage o total_meter."
        ),
    )

    normalized_metric_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código normalizado",
        help_text=(
            "Código usado en las tablas históricas. "
            "Ejemplo: TOTAL, TONER_BLACK o FUSER_UNIT."
        ),
    )

    normalized_metric_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre normalizado",
    )

    oid = models.CharField(
        max_length=500,
        blank=True,
        db_index=True,
        verbose_name="OID",
    )

    base_oid = models.CharField(
        max_length=500,
        blank=True,
        db_index=True,
        verbose_name="OID base",
    )

    fallback_oids = models.JSONField(
        default=list,
        blank=True,
        verbose_name="OID alternativos",
        help_text=(
            "Se consultan en orden cuando el OID principal "
            "no devuelve un valor válido."
        ),
    )

    dependency_codes = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Métricas requeridas",
        help_text=(
            "Códigos de otras métricas necesarias antes de "
            "procesar esta métrica."
        ),
    )

    table_group = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Grupo de tabla",
        help_text=(
            "Agrupa columnas SNMP que comparten el mismo índice."
        ),
    )

    table_key = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Clave de tabla",
    )

    index_strategy = models.CharField(
        max_length=30,
        choices=IndexStrategy.choices,
        default=IndexStrategy.NONE,
        verbose_name="Estrategia de índice",
    )

    fixed_index_length = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Longitud fija del índice",
    )

    index_regex = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Expresión regular del índice",
    )

    related_index_metric_code = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Métrica del índice relacionado",
    )

    value_type = models.CharField(
        max_length=30,
        choices=ValueType.choices,
        default=ValueType.AUTO,
        db_index=True,
        verbose_name="Tipo de valor",
    )

    unit = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Unidad",
    )

    scale_multiplier = models.DecimalField(
        max_digits=30,
        decimal_places=10,
        default=Decimal("1"),
        verbose_name="Multiplicador",
    )

    scale_divisor = models.DecimalField(
        max_digits=30,
        decimal_places=10,
        default=Decimal("1"),
        verbose_name="Divisor",
    )

    value_offset = models.DecimalField(
        max_digits=30,
        decimal_places=10,
        default=Decimal("0"),
        verbose_name="Desplazamiento",
    )

    decimal_places = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Cantidad de decimales",
    )

    minimum_value = models.DecimalField(
        max_digits=40,
        decimal_places=10,
        null=True,
        blank=True,
        verbose_name="Valor mínimo permitido",
    )

    maximum_value = models.DecimalField(
        max_digits=40,
        decimal_places=10,
        null=True,
        blank=True,
        verbose_name="Valor máximo permitido",
    )

    percentage_inverted = models.BooleanField(
        default=False,
        verbose_name="Porcentaje invertido",
        help_text=(
            "Convierte porcentaje utilizado en porcentaje restante."
        ),
    )

    maximum_value_metric_code = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Métrica de capacidad máxima",
    )

    status_metric_code = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Métrica de estado relacionada",
    )

    name_metric_code = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Métrica de nombre relacionada",
    )

    serial_metric_code = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Métrica de serie relacionada",
    )

    color_metric_code = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Métrica de color relacionada",
    )

    quantity_metric_code = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Métrica de cantidad relacionada",
    )

    calculation_expression = models.TextField(
        blank=True,
        verbose_name="Expresión de cálculo",
        help_text=(
            "Expresión controlada que será evaluada por el "
            "procesador, nunca directamente con eval()."
        ),
    )

    extraction_regex = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Expresión regular de extracción",
    )

    extraction_group = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Grupo de extracción",
    )

    text_prefix_to_remove = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Prefijo a eliminar",
    )

    text_suffix_to_remove = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Sufijo a eliminar",
    )

    value_map = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Mapa de valores",
        help_text=(
            "Relaciona valores originales con valores normalizados."
        ),
    )

    special_values = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Valores especiales",
        help_text=(
            "Ejemplo: -1=otro, -2=desconocido, -3=no disponible."
        ),
    )

    ignored_values = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Valores ignorados",
    )

    valid_values = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Valores permitidos",
    )

    missing_value_behavior = models.CharField(
        max_length=20,
        choices=MissingValueBehavior.choices,
        default=MissingValueBehavior.IGNORE,
        verbose_name="Comportamiento sin valor",
    )

    default_value = models.TextField(
        blank=True,
        verbose_name="Valor predeterminado",
    )

    empty_string_is_null = models.BooleanField(
        default=True,
        verbose_name="Texto vacío equivale a nulo",
    )

    zero_is_null = models.BooleanField(
        default=False,
        verbose_name="Cero equivale a nulo",
    )

    negative_is_special = models.BooleanField(
        default=True,
        verbose_name="Negativos son valores especiales",
    )

    required = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Obligatoria",
    )

    enabled = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Habilitada",
    )

    visible_in_reports = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Visible en reportes",
    )

    store_raw_value = models.BooleanField(
        default=True,
        verbose_name="Guardar valor original",
    )

    store_when_unchanged = models.BooleanField(
        default=True,
        verbose_name="Guardar aunque no cambie",
    )

    create_alert_on_error = models.BooleanField(
        default=False,
        verbose_name="Crear alerta por error",
    )

    poll_interval_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Intervalo específico",
        help_text=(
            "Si está vacío, usa el intervalo de la categoría "
            "configurado en el perfil."
        ),
    )

    timeout_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo de espera específico",
    )

    retry_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Reintentos específicos",
    )

    priority = models.PositiveIntegerField(
        default=100,
        db_index=True,
        verbose_name="Orden de procesamiento",
    )

    confidence_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("100.00"),
        verbose_name="Confianza",
    )

    parser_options = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Opciones del parser",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Métrica de perfil SNMP"
        verbose_name_plural = "Métricas de perfiles SNMP"
        ordering = (
            "profile",
            "priority",
            "code",
        )
        indexes = [
            models.Index(
                fields=[
                    "profile",
                    "category",
                    "enabled",
                ],
                name="mon_metric_profile_cat_idx",
            ),
            models.Index(
                fields=[
                    "profile",
                    "query_type",
                    "priority",
                ],
                name="mon_metric_profile_query_idx",
            ),
            models.Index(
                fields=[
                    "oid",
                    "enabled",
                ],
                name="mon_metric_oid_enabled_idx",
            ),
            models.Index(
                fields=[
                    "destination_model",
                    "normalized_metric_code",
                ],
                name="mon_metric_destination_idx",
            ),
            models.Index(
                fields=[
                    "table_group",
                    "priority",
                ],
                name="mon_metric_table_group_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "profile",
                    "code",
                ],
                condition=models.Q(
                    archived_at__isnull=True,
                ),
                name="unique_active_profile_metric",
            ),
        ]

    def __str__(self):
        return (
            f"{self.profile.code} - "
            f"{self.code}"
        )

    def normalize_numeric_value(self, value):
        """
        Aplica multiplicador, divisor, desplazamiento e inversión.

        La interpretación completa se realizará en el servicio de
        procesamiento; este método concentra la operación básica.
        """

        if value is None:
            return None

        decimal_value = Decimal(
            str(value)
        )

        if self.scale_divisor == 0:
            raise ValidationError(
                "El divisor de escala no puede ser cero."
            )

        normalized = (
            decimal_value
            * self.scale_multiplier
            / self.scale_divisor
        )

        normalized += self.value_offset

        if self.percentage_inverted:
            normalized = (
                Decimal("100")
                - normalized
            )

        if self.decimal_places is not None:
            exponent = Decimal(
                "1"
            ).scaleb(
                -self.decimal_places
            )

            normalized = normalized.quantize(
                exponent
            )

        return normalized

    def map_value(self, value):
        """
        Traduce valores enumerados conservando el valor original
        cuando no exista una equivalencia.
        """

        key = str(
            value
        ).strip()

        if key in self.value_map:
            return self.value_map[key]

        return value

    def is_ignored_value(self, value):
        normalized = str(
            value
        ).strip()

        return any(
            normalized == str(item).strip()
            for item in self.ignored_values
        )

    def is_special_value(self, value):
        normalized = str(
            value
        ).strip()

        return normalized in {
            str(key).strip()
            for key in self.special_values.keys()
        }

    def get_special_value_meaning(self, value):
        normalized = str(
            value
        ).strip()

        for key, meaning in self.special_values.items():
            if str(key).strip() == normalized:
                return meaning

        return None

    def clean(self):
        super().clean()

        text_fields = [
            "code",
            "name",
            "description",
            "destination_field",
            "normalized_metric_code",
            "normalized_metric_name",
            "oid",
            "base_oid",
            "table_group",
            "table_key",
            "index_regex",
            "related_index_metric_code",
            "unit",
            "maximum_value_metric_code",
            "status_metric_code",
            "name_metric_code",
            "serial_metric_code",
            "color_metric_code",
            "quantity_metric_code",
            "calculation_expression",
            "extraction_regex",
            "extraction_group",
            "text_prefix_to_remove",
            "text_suffix_to_remove",
            "default_value",
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

        upper_fields = [
            "code",
            "normalized_metric_code",
            "table_group",
            "table_key",
            "related_index_metric_code",
            "maximum_value_metric_code",
            "status_metric_code",
            "name_metric_code",
            "serial_metric_code",
            "color_metric_code",
            "quantity_metric_code",
        ]

        for field_name in upper_fields:
            setattr(
                self,
                field_name,
                getattr(
                    self,
                    field_name,
                    "",
                ).upper(),
            )

        self.oid = self.oid.strip(".")
        self.base_oid = self.base_oid.strip(".")

        if not self.profile_id:
            raise ValidationError(
                {
                    "profile": (
                        "El perfil SNMP es obligatorio."
                    ),
                }
            )

        if not self.code:
            raise ValidationError(
                {
                    "code": (
                        "El código de la métrica es obligatorio."
                    ),
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": (
                        "El nombre de la métrica es obligatorio."
                    ),
                }
            )

        if (
            self.query_type != self.QueryType.CALCULATED
            and not self.oid
            and not self.fallback_oids
        ):
            raise ValidationError(
                {
                    "oid": (
                        "Debe configurar un OID principal "
                        "o al menos un OID alternativo."
                    ),
                }
            )

        if (
            self.query_type == self.QueryType.CALCULATED
            and not self.calculation_expression
        ):
            raise ValidationError(
                {
                    "calculation_expression": (
                        "Una métrica calculada requiere "
                        "una expresión."
                    ),
                }
            )

        if self.scale_divisor == 0:
            raise ValidationError(
                {
                    "scale_divisor": (
                        "El divisor no puede ser cero."
                    ),
                }
            )

        if (
            self.minimum_value is not None
            and self.maximum_value is not None
            and self.minimum_value > self.maximum_value
        ):
            raise ValidationError(
                {
                    "maximum_value": (
                        "El valor máximo no puede ser menor "
                        "que el valor mínimo."
                    ),
                }
            )

        if (
            self.confidence_percent < 0
            or self.confidence_percent > 100
        ):
            raise ValidationError(
                {
                    "confidence_percent": (
                        "La confianza debe estar entre 0 y 100."
                    ),
                }
            )

        if (
            self.poll_interval_seconds is not None
            and self.poll_interval_seconds < 10
        ):
            raise ValidationError(
                {
                    "poll_interval_seconds": (
                        "El intervalo específico debe ser "
                        "como mínimo de diez segundos."
                    ),
                }
            )

        if (
            self.timeout_seconds is not None
            and self.timeout_seconds < 1
        ):
            raise ValidationError(
                {
                    "timeout_seconds": (
                        "El tiempo de espera debe ser "
                        "como mínimo un segundo."
                    ),
                }
            )

        table_queries = {
            self.QueryType.TABLE,
            self.QueryType.WALK,
            self.QueryType.GET_BULK,
        }

        if (
            self.index_strategy
            != self.IndexStrategy.NONE
            and self.query_type not in table_queries
        ):
            raise ValidationError(
                {
                    "index_strategy": (
                        "La estrategia de índice solo aplica "
                        "a consultas de tabla o recorrido."
                    ),
                }
            )

        if (
            self.index_strategy
            == self.IndexStrategy.FIXED_LENGTH
            and not self.fixed_index_length
        ):
            raise ValidationError(
                {
                    "fixed_index_length": (
                        "Debe indicar la longitud fija del índice."
                    ),
                }
            )

        if (
            self.index_strategy
            == self.IndexStrategy.REGEX
            and not self.index_regex
        ):
            raise ValidationError(
                {
                    "index_regex": (
                        "Debe indicar la expresión regular "
                        "del índice."
                    ),
                }
            )

        if (
            self.index_strategy
            == self.IndexStrategy.RELATED_TABLE
            and not self.related_index_metric_code
        ):
            raise ValidationError(
                {
                    "related_index_metric_code": (
                        "Debe indicar la métrica que define "
                        "el índice relacionado."
                    ),
                }
            )

        if (
            self.missing_value_behavior
            == self.MissingValueBehavior.DEFAULT
            and not self.default_value
        ):
            raise ValidationError(
                {
                    "default_value": (
                        "Debe indicar el valor predeterminado."
                    ),
                }
            )

        destination_requires_code = {
            self.DestinationModel.COUNTER,
            self.DestinationModel.CONSUMABLE,
            self.DestinationModel.COMPONENT,
            self.DestinationModel.TRAY,
            self.DestinationModel.ACCESSORY,
            self.DestinationModel.ALERT,
            self.DestinationModel.JOB,
        }

        if (
            self.destination_model
            in destination_requires_code
            and not self.normalized_metric_code
        ):
            raise ValidationError(
                {
                    "normalized_metric_code": (
                        "El destino seleccionado requiere "
                        "un código normalizado."
                    ),
                }
            )

        field_destinations = {
            self.DestinationModel.DEVICE,
            self.DestinationModel.SNAPSHOT,
        }

        if (
            self.destination_model in field_destinations
            and not self.destination_field
        ):
            raise ValidationError(
                {
                    "destination_field": (
                        "Debe indicar el campo de destino."
                    ),
                }
            )

        if not isinstance(
            self.value_map,
            dict,
        ):
            raise ValidationError(
                {
                    "value_map": (
                        "El mapa de valores debe ser un objeto."
                    ),
                }
            )

        if not isinstance(
            self.special_values,
            dict,
        ):
            raise ValidationError(
                {
                    "special_values": (
                        "Los valores especiales deben ser "
                        "un objeto."
                    ),
                }
            )

        list_fields = [
            "fallback_oids",
            "dependency_codes",
            "ignored_values",
            "valid_values",
        ]

        for field_name in list_fields:
            if not isinstance(
                getattr(
                    self,
                    field_name,
                ),
                list,
            ):
                raise ValidationError(
                    {
                        field_name: (
                            "Este campo debe ser una lista."
                        ),
                    }
                )

        own_code = self.code.upper()

        dependencies = {
            str(code).strip().upper()
            for code in self.dependency_codes
            if str(code).strip()
        }

        if own_code in dependencies:
            raise ValidationError(
                {
                    "dependency_codes": (
                        "Una métrica no puede depender de sí misma."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        self.code = str(
            self.code or ""
        ).strip().upper()

        self.normalized_metric_code = str(
            self.normalized_metric_code or ""
        ).strip().upper()

        self.table_group = str(
            self.table_group or ""
        ).strip().upper()

        self.table_key = str(
            self.table_key or ""
        ).strip().upper()

        self.oid = str(
            self.oid or ""
        ).strip().strip(".")

        self.base_oid = str(
            self.base_oid or ""
        ).strip().strip(".")

        self.fallback_oids = [
            str(oid).strip().strip(".")
            for oid in (
                self.fallback_oids
                or []
            )
            if str(oid).strip()
        ]

        self.dependency_codes = [
            str(code).strip().upper()
            for code in (
                self.dependency_codes
                or []
            )
            if str(code).strip()
        ]

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )