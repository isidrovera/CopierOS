# -*- coding: utf-8 -*-
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import models

from .base import MonitoringBaseModel


class SNMPProfileTestMetric(MonitoringBaseModel):
    """
    Resultado histórico de una métrica individual durante
    una prueba de perfil SNMP.

    Conserva:

    - Métrica evaluada.
    - OID principal o alternativo utilizado.
    - Valor original recibido.
    - Valor interpretado.
    - Tiempo de respuesta.
    - Compatibilidad.
    - Resultado de validación.
    - Error producido.
    """

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        SUCCESS = (
            "success",
            "Correcta",
        )
        EMPTY = (
            "empty",
            "Sin valor",
        )
        UNSUPPORTED = (
            "unsupported",
            "No compatible",
        )
        TIMEOUT = (
            "timeout",
            "Tiempo agotado",
        )
        AUTHENTICATION_ERROR = (
            "authentication_error",
            "Error de autenticación",
        )
        PARSE_ERROR = (
            "parse_error",
            "Error de interpretación",
        )
        VALIDATION_ERROR = (
            "validation_error",
            "Error de validación",
        )
        DEPENDENCY_ERROR = (
            "dependency_error",
            "Error de dependencia",
        )
        ERROR = (
            "error",
            "Con error",
        )
        SKIPPED = (
            "skipped",
            "Omitida",
        )

    class CompatibilityStatus(models.TextChoices):
        UNKNOWN = (
            "unknown",
            "Desconocida",
        )
        COMPATIBLE = (
            "compatible",
            "Compatible",
        )
        PARTIAL = (
            "partial",
            "Compatibilidad parcial",
        )
        INCOMPATIBLE = (
            "incompatible",
            "No compatible",
        )
        NOT_TESTED = (
            "not_tested",
            "No evaluada",
        )

    class ValidationStatus(models.TextChoices):
        NOT_VALIDATED = (
            "not_validated",
            "Sin validar",
        )
        VALID = (
            "valid",
            "Válida",
        )
        INVALID_TYPE = (
            "invalid_type",
            "Tipo inválido",
        )
        OUT_OF_RANGE = (
            "out_of_range",
            "Fuera de rango",
        )
        INVALID_ENUM = (
            "invalid_enum",
            "Valor no permitido",
        )
        REQUIRED_EMPTY = (
            "required_empty",
            "Métrica obligatoria vacía",
        )
        SPECIAL_VALUE = (
            "special_value",
            "Valor especial",
        )
        IGNORED_VALUE = (
            "ignored_value",
            "Valor ignorado",
        )
        PARSE_ERROR = (
            "parse_error",
            "Error de interpretación",
        )

    profile_test = models.ForeignKey(
        "monitoring.SNMPProfileTest",
        on_delete=models.PROTECT,
        related_name="metric_test_results",
        verbose_name="Prueba de perfil",
    )

    metric = models.ForeignKey(
        "monitoring.SNMPProfileMetric",
        on_delete=models.PROTECT,
        related_name="test_results",
        verbose_name="Métrica",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        on_delete=models.PROTECT,
        related_name="profile_metric_tests",
        verbose_name="Dispositivo",
    )

    profile = models.ForeignKey(
        "monitoring.SNMPProfile",
        on_delete=models.PROTECT,
        related_name="metric_test_results",
        verbose_name="Perfil",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_profile_metric_tests",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_profile_metric_tests",
        verbose_name="Sede",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        on_delete=models.PROTECT,
        related_name="profile_metric_tests",
        verbose_name="Agente",
    )

    metric_code = models.CharField(
        max_length=150,
        db_index=True,
        editable=False,
        verbose_name="Código de métrica",
    )

    metric_name = models.CharField(
        max_length=255,
        editable=False,
        verbose_name="Nombre de métrica",
    )

    metric_category = models.CharField(
        max_length=30,
        db_index=True,
        editable=False,
        verbose_name="Categoría",
    )

    destination_model = models.CharField(
        max_length=30,
        db_index=True,
        editable=False,
        verbose_name="Destino",
    )

    normalized_metric_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        editable=False,
        verbose_name="Código normalizado",
    )

    required = models.BooleanField(
        default=False,
        db_index=True,
        editable=False,
        verbose_name="Métrica obligatoria",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    compatibility_status = models.CharField(
        max_length=30,
        choices=CompatibilityStatus.choices,
        default=CompatibilityStatus.UNKNOWN,
        db_index=True,
        verbose_name="Compatibilidad",
    )

    validation_status = models.CharField(
        max_length=30,
        choices=ValidationStatus.choices,
        default=ValidationStatus.NOT_VALIDATED,
        db_index=True,
        verbose_name="Validación",
    )

    attempted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de consulta",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de finalización",
    )

    response_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo de respuesta",
    )

    retry_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Reintentos realizados",
    )

    requested_oid = models.CharField(
        max_length=500,
        blank=True,
        db_index=True,
        verbose_name="OID solicitado",
    )

    responded_oid = models.CharField(
        max_length=500,
        blank=True,
        db_index=True,
        verbose_name="OID respondido",
    )

    oid_index = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Índice OID",
    )

    used_fallback_oid = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Usó OID alternativo",
    )

    fallback_position = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Posición del OID alternativo",
    )

    snmp_value_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Tipo SNMP recibido",
    )

    expected_value_type = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Tipo esperado",
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
        decimal_places=10,
        null=True,
        blank=True,
        verbose_name="Valor numérico original",
    )

    normalized_numeric_value = models.DecimalField(
        max_digits=40,
        decimal_places=10,
        null=True,
        blank=True,
        verbose_name="Valor numérico normalizado",
    )

    integer_value = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Valor entero",
    )

    boolean_value = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Valor booleano",
    )

    mapped_value = models.TextField(
        blank=True,
        verbose_name="Valor mapeado",
    )

    special_value_code = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Código especial",
    )

    special_value_meaning = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Significado especial",
    )

    dependency_values = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Valores de dependencias",
    )

    calculation_inputs = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Entradas de cálculo",
    )

    calculation_result = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resultado del cálculo",
    )

    parser_details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Detalle de interpretación",
    )

    validation_details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Detalle de validación",
    )

    error_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de error",
    )

    error_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de error",
    )

    warning_messages = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Advertencias",
    )

    confidence_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Confianza",
    )

    is_successful = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Resultado correcto",
    )

    is_empty = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Sin valor",
    )

    is_supported = models.BooleanField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Métrica compatible",
    )

    was_parsed = models.BooleanField(
        default=False,
        verbose_name="Valor interpretado",
    )

    was_validated = models.BooleanField(
        default=False,
        verbose_name="Valor validado",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Resultado de métrica de perfil"
        verbose_name_plural = "Resultados de métricas de perfiles"
        ordering = (
            "profile_test",
            "metric__priority",
            "metric_code",
        )
        indexes = [
            models.Index(
                fields=[
                    "profile_test",
                    "status",
                ],
                name="mon_ptmetric_test_status_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "metric_code",
                    "created_at",
                ],
                name="mon_ptmetric_device_code_idx",
            ),
            models.Index(
                fields=[
                    "profile",
                    "metric_category",
                    "status",
                ],
                name="mon_ptmetric_profile_cat_idx",
            ),
            models.Index(
                fields=[
                    "compatibility_status",
                    "validation_status",
                ],
                name="mon_ptmetric_validation_idx",
            ),
            models.Index(
                fields=[
                    "requested_oid",
                    "status",
                ],
                name="mon_ptmetric_oid_status_idx",
            ),
            models.Index(
                fields=[
                    "required",
                    "is_successful",
                    "status",
                ],
                name="mon_ptmetric_required_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "profile_test",
                    "metric",
                    "oid_index",
                ],
                name="unique_profile_test_metric_index",
            ),
        ]

    def __str__(self):
        return (
            f"{self.profile_test} - "
            f"{self.metric_code} - "
            f"{self.get_status_display()}"
        )

    def parse_numeric_value(self):
        value = str(
            self.raw_value or ""
        ).strip()

        if not value:
            self.numeric_value = None
            self.normalized_numeric_value = None
            self.integer_value = None
            return

        try:
            self.numeric_value = Decimal(value)

            self.normalized_numeric_value = (
                self.metric.normalize_numeric_value(
                    self.numeric_value
                )
            )

            if (
                self.normalized_numeric_value
                == self.normalized_numeric_value.to_integral_value()
            ):
                self.integer_value = int(
                    self.normalized_numeric_value
                )
            else:
                self.integer_value = None

            self.was_parsed = True

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ) as exc:
            self.status = self.Status.PARSE_ERROR
            self.validation_status = (
                self.ValidationStatus.PARSE_ERROR
            )
            self.error_code = "NUMERIC_PARSE_ERROR"
            self.error_message = str(exc)
            self.was_parsed = False

    def parse_boolean_value(self):
        value = str(
            self.raw_value or ""
        ).strip().lower()

        truthy_values = {
            "1",
            "true",
            "yes",
            "on",
            "enabled",
            "active",
        }

        falsy_values = {
            "0",
            "false",
            "no",
            "off",
            "disabled",
            "inactive",
        }

        if value in truthy_values:
            self.boolean_value = True
            self.was_parsed = True
            return

        if value in falsy_values:
            self.boolean_value = False
            self.was_parsed = True
            return

        self.status = self.Status.PARSE_ERROR
        self.validation_status = (
            self.ValidationStatus.PARSE_ERROR
        )
        self.error_code = "BOOLEAN_PARSE_ERROR"
        self.error_message = (
            "El valor no puede interpretarse como booleano."
        )
        self.was_parsed = False

    def parse_value(self):
        self.text_value = ""
        self.numeric_value = None
        self.normalized_numeric_value = None
        self.integer_value = None
        self.boolean_value = None
        self.mapped_value = ""
        self.special_value_code = ""
        self.special_value_meaning = ""

        value = str(
            self.raw_value or ""
        ).strip()

        self.display_value = (
            self.display_value
            or value
        )

        if not value:
            self.is_empty = True
            self.was_parsed = False
            return

        self.is_empty = False

        if self.metric.is_ignored_value(value):
            self.validation_status = (
                self.ValidationStatus.IGNORED_VALUE
            )
            self.status = self.Status.SKIPPED
            self.was_parsed = True
            return

        if self.metric.is_special_value(value):
            self.special_value_code = value
            self.special_value_meaning = str(
                self.metric.get_special_value_meaning(
                    value
                )
                or ""
            )

            self.validation_status = (
                self.ValidationStatus.SPECIAL_VALUE
            )
            self.was_parsed = True
            return

        numeric_types = {
            self.metric.ValueType.INTEGER,
            self.metric.ValueType.DECIMAL,
            self.metric.ValueType.TIMETICKS,
            self.metric.ValueType.PERCENTAGE,
            self.metric.ValueType.STATUS_CODE,
        }

        if self.metric.value_type in numeric_types:
            self.parse_numeric_value()

        elif (
            self.metric.value_type
            == self.metric.ValueType.BOOLEAN
        ):
            self.parse_boolean_value()

        else:
            self.text_value = value
            self.was_parsed = True

        if self.was_parsed:
            mapped = self.metric.map_value(
                self.normalized_numeric_value
                if self.normalized_numeric_value is not None
                else (
                    self.boolean_value
                    if self.boolean_value is not None
                    else self.text_value
                )
            )

            self.mapped_value = str(
                mapped
            ).strip()

    def validate_value(self):
        if self.status in {
            self.Status.PARSE_ERROR,
            self.Status.ERROR,
            self.Status.TIMEOUT,
            self.Status.AUTHENTICATION_ERROR,
            self.Status.DEPENDENCY_ERROR,
        }:
            self.was_validated = False
            return

        if self.is_empty:
            self.was_validated = True

            if self.required:
                self.status = self.Status.EMPTY
                self.validation_status = (
                    self.ValidationStatus.REQUIRED_EMPTY
                )
                self.is_successful = False
            else:
                self.status = self.Status.EMPTY
                self.validation_status = (
                    self.ValidationStatus.VALID
                )
                self.is_successful = True

            return

        if self.validation_status in {
            self.ValidationStatus.SPECIAL_VALUE,
            self.ValidationStatus.IGNORED_VALUE,
        }:
            self.was_validated = True
            self.is_successful = (
                self.validation_status
                == self.ValidationStatus.SPECIAL_VALUE
            )
            return

        value = (
            self.normalized_numeric_value
            if self.normalized_numeric_value is not None
            else (
                self.boolean_value
                if self.boolean_value is not None
                else (
                    self.mapped_value
                    or self.text_value
                )
            )
        )

        if (
            self.normalized_numeric_value is not None
            and self.metric.minimum_value is not None
            and self.normalized_numeric_value
            < self.metric.minimum_value
        ):
            self.status = self.Status.VALIDATION_ERROR
            self.validation_status = (
                self.ValidationStatus.OUT_OF_RANGE
            )
            self.is_successful = False
            self.was_validated = True
            return

        if (
            self.normalized_numeric_value is not None
            and self.metric.maximum_value is not None
            and self.normalized_numeric_value
            > self.metric.maximum_value
        ):
            self.status = self.Status.VALIDATION_ERROR
            self.validation_status = (
                self.ValidationStatus.OUT_OF_RANGE
            )
            self.is_successful = False
            self.was_validated = True
            return

        if self.metric.valid_values:
            valid_values = {
                str(item).strip()
                for item in self.metric.valid_values
            }

            if str(value).strip() not in valid_values:
                self.status = self.Status.VALIDATION_ERROR
                self.validation_status = (
                    self.ValidationStatus.INVALID_ENUM
                )
                self.is_successful = False
                self.was_validated = True
                return

        self.status = self.Status.SUCCESS
        self.validation_status = (
            self.ValidationStatus.VALID
        )
        self.is_successful = True
        self.was_validated = True

    def calculate_compatibility(self):
        if self.status == self.Status.SUCCESS:
            self.compatibility_status = (
                self.CompatibilityStatus.COMPATIBLE
            )
            self.is_supported = True
            return

        if self.status == self.Status.EMPTY:
            self.compatibility_status = (
                self.CompatibilityStatus.PARTIAL
            )
            self.is_supported = True
            return

        if self.status == self.Status.UNSUPPORTED:
            self.compatibility_status = (
                self.CompatibilityStatus.INCOMPATIBLE
            )
            self.is_supported = False
            return

        if self.status == self.Status.SKIPPED:
            self.compatibility_status = (
                self.CompatibilityStatus.NOT_TESTED
            )
            self.is_supported = None
            return

        self.compatibility_status = (
            self.CompatibilityStatus.UNKNOWN
        )

    def calculate_confidence(self):
        if self.status == self.Status.SUCCESS:
            self.confidence_percent = (
                self.metric.confidence_percent
            )
            return

        if self.status == self.Status.EMPTY:
            self.confidence_percent = Decimal("50.00")
            return

        if self.status == self.Status.UNSUPPORTED:
            self.confidence_percent = Decimal("0.00")
            return

        if self.status == self.Status.SKIPPED:
            self.confidence_percent = Decimal("0.00")
            return

        self.confidence_percent = Decimal("0.00")

    def register_success(
        self,
        *,
        raw_value,
        requested_oid,
        responded_oid="",
        oid_index="",
        response_time_ms=None,
        snmp_value_type="",
        used_fallback_oid=False,
        fallback_position=None,
        completed_at=None,
    ):
        self.raw_value = str(
            raw_value
            if raw_value is not None
            else ""
        )

        self.requested_oid = str(
            requested_oid or ""
        ).strip().strip(".")

        self.responded_oid = str(
            responded_oid or requested_oid or ""
        ).strip().strip(".")

        self.oid_index = str(
            oid_index or ""
        ).strip()

        self.response_time_ms = response_time_ms
        self.snmp_value_type = str(
            snmp_value_type or ""
        ).strip()

        self.used_fallback_oid = bool(
            used_fallback_oid
        )
        self.fallback_position = fallback_position
        self.completed_at = completed_at

        self.error_code = ""
        self.error_message = ""

        self.parse_value()
        self.validate_value()
        self.calculate_compatibility()
        self.calculate_confidence()

        self.save()

        return self.is_successful

    def register_error(
        self,
        *,
        status,
        error_message,
        error_code="",
        requested_oid="",
        response_time_ms=None,
        completed_at=None,
    ):
        allowed_statuses = {
            self.Status.UNSUPPORTED,
            self.Status.TIMEOUT,
            self.Status.AUTHENTICATION_ERROR,
            self.Status.PARSE_ERROR,
            self.Status.VALIDATION_ERROR,
            self.Status.DEPENDENCY_ERROR,
            self.Status.ERROR,
        }

        if status not in allowed_statuses:
            raise ValidationError(
                "El estado indicado no representa un error."
            )

        self.status = status
        self.requested_oid = str(
            requested_oid or ""
        ).strip().strip(".")

        self.response_time_ms = response_time_ms
        self.completed_at = completed_at
        self.error_code = str(
            error_code or ""
        ).strip().upper()

        self.error_message = str(
            error_message or ""
        ).strip()

        self.is_successful = False
        self.was_validated = False

        self.calculate_compatibility()
        self.calculate_confidence()
        self.save()

    def clean(self):
        super().clean()

        text_fields = [
            "metric_code",
            "metric_name",
            "metric_category",
            "destination_model",
            "normalized_metric_code",
            "requested_oid",
            "responded_oid",
            "oid_index",
            "snmp_value_type",
            "expected_value_type",
            "raw_value",
            "display_value",
            "text_value",
            "mapped_value",
            "special_value_code",
            "special_value_meaning",
            "error_code",
            "error_message",
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

        self.metric_code = self.metric_code.upper()
        self.normalized_metric_code = (
            self.normalized_metric_code.upper()
        )
        self.requested_oid = self.requested_oid.strip(".")
        self.responded_oid = self.responded_oid.strip(".")
        self.error_code = self.error_code.upper()

        if not self.profile_test_id:
            raise ValidationError(
                {
                    "profile_test": (
                        "La prueba de perfil es obligatoria."
                    ),
                }
            )

        if not self.metric_id:
            raise ValidationError(
                {
                    "metric": (
                        "La métrica es obligatoria."
                    ),
                }
            )

        if (
            self.metric.profile_id
            != self.profile_test.profile_id
        ):
            raise ValidationError(
                {
                    "metric": (
                        "La métrica no pertenece al perfil "
                        "que está siendo probado."
                    ),
                }
            )

        if (
            self.profile_test.device_id
            != self.device_id
        ):
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo no coincide con la prueba."
                    ),
                }
            )

        if (
            self.profile_test.profile_id
            != self.profile_id
        ):
            raise ValidationError(
                {
                    "profile": (
                        "El perfil no coincide con la prueba."
                    ),
                }
            )

        if (
            self.profile_test.customer_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "customer": (
                        "El cliente no coincide con la prueba."
                    ),
                }
            )

        if (
            self.profile_test.agent_id
            != self.agent_id
        ):
            raise ValidationError(
                {
                    "agent": (
                        "El agente no coincide con la prueba."
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

        if (
            self.completed_at
            and self.attempted_at
            and self.completed_at < self.attempted_at
        ):
            raise ValidationError(
                {
                    "completed_at": (
                        "La finalización no puede ser anterior "
                        "al inicio de la consulta."
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
            self.used_fallback_oid
            and self.fallback_position is None
        ):
            raise ValidationError(
                {
                    "fallback_position": (
                        "Debe indicar la posición del OID "
                        "alternativo utilizado."
                    ),
                }
            )

        if (
            not self.used_fallback_oid
            and self.fallback_position is not None
        ):
            raise ValidationError(
                {
                    "fallback_position": (
                        "No debe indicar una posición si no se "
                        "utilizó un OID alternativo."
                    ),
                }
            )

        if (
            self.status == self.Status.SUCCESS
            and not self.was_validated
        ):
            raise ValidationError(
                {
                    "was_validated": (
                        "Una métrica correcta debe estar validada."
                    ),
                }
            )

        if (
            self.status == self.Status.SUCCESS
            and not self.is_successful
        ):
            raise ValidationError(
                {
                    "is_successful": (
                        "El resultado correcto debe marcarse "
                        "como exitoso."
                    ),
                }
            )

        if not isinstance(
            self.dependency_values,
            dict,
        ):
            raise ValidationError(
                {
                    "dependency_values": (
                        "Los valores de dependencias deben "
                        "ser un objeto."
                    ),
                }
            )

        if not isinstance(
            self.calculation_inputs,
            dict,
        ):
            raise ValidationError(
                {
                    "calculation_inputs": (
                        "Las entradas de cálculo deben "
                        "ser un objeto."
                    ),
                }
            )

        if not isinstance(
            self.calculation_result,
            dict,
        ):
            raise ValidationError(
                {
                    "calculation_result": (
                        "El resultado del cálculo debe "
                        "ser un objeto."
                    ),
                }
            )

        if not isinstance(
            self.parser_details,
            dict,
        ):
            raise ValidationError(
                {
                    "parser_details": (
                        "El detalle del parser debe "
                        "ser un objeto."
                    ),
                }
            )

        if not isinstance(
            self.validation_details,
            dict,
        ):
            raise ValidationError(
                {
                    "validation_details": (
                        "El detalle de validación debe "
                        "ser un objeto."
                    ),
                }
            )

        if not isinstance(
            self.warning_messages,
            list,
        ):
            raise ValidationError(
                {
                    "warning_messages": (
                        "Las advertencias deben ser una lista."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        if self.profile_test_id:
            self.device = self.profile_test.device
            self.profile = self.profile_test.profile
            self.customer = self.profile_test.customer
            self.branch = self.profile_test.branch
            self.agent = self.profile_test.agent

        if self.metric_id:
            self.metric_code = self.metric.code
            self.metric_name = self.metric.name
            self.metric_category = self.metric.category
            self.destination_model = (
                self.metric.destination_model
            )
            self.normalized_metric_code = (
                self.metric.normalized_metric_code
            )
            self.required = self.metric.required
            self.expected_value_type = (
                self.metric.value_type
            )

            if not self.requested_oid:
                self.requested_oid = self.metric.oid

        self.metric_code = str(
            self.metric_code or ""
        ).strip().upper()

        self.normalized_metric_code = str(
            self.normalized_metric_code or ""
        ).strip().upper()

        self.requested_oid = str(
            self.requested_oid or ""
        ).strip().strip(".")

        self.responded_oid = str(
            self.responded_oid or ""
        ).strip().strip(".")

        self.calculate_compatibility()
        self.calculate_confidence()
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
            "Los resultados históricos de métricas "
            "no pueden archivarse."
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        raise ValidationError(
            "Los resultados históricos de métricas "
            "no pueden restaurarse."
        )