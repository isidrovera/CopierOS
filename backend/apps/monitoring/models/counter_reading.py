# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from .base import MonitoringBaseModel


class CounterReading(MonitoringBaseModel):
    """
    Lectura histórica de un contador individual.

    Permite registrar cualquier contador publicado por el equipo,
    incluso cuando todavía no exista una clasificación definitiva.

    Ejemplos:

    - Total general.
    - Total B/N.
    - Total color.
    - Copias.
    - Impresiones.
    - Escaneos.
    - Fax.
    - Dúplex.
    - Tamaños de papel.
    - Contadores por función, usuario o departamento.
    """

    class Category(models.TextChoices):
        TOTAL = (
            "total",
            "Total general",
        )
        PRINT = (
            "print",
            "Impresión",
        )
        COPY = (
            "copy",
            "Copia",
        )
        SCAN = (
            "scan",
            "Escaneo",
        )
        FAX = (
            "fax",
            "Fax",
        )
        DUPLEX = (
            "duplex",
            "Dúplex",
        )
        SIMPLEX = (
            "simplex",
            "Simplex",
        )
        PAPER_SIZE = (
            "paper_size",
            "Formato de papel",
        )
        JOB = (
            "job",
            "Trabajo",
        )
        USER = (
            "user",
            "Usuario",
        )
        DEPARTMENT = (
            "department",
            "Departamento",
        )
        MAINTENANCE = (
            "maintenance",
            "Mantenimiento",
        )
        JAM = (
            "jam",
            "Atascos",
        )
        OTHER = (
            "other",
            "Otro",
        )
        UNKNOWN = (
            "unknown",
            "Sin clasificar",
        )

    class FunctionType(models.TextChoices):
        ALL = (
            "all",
            "Todas las funciones",
        )
        PRINT = (
            "print",
            "Impresión",
        )
        COPY = (
            "copy",
            "Copia",
        )
        SCAN = (
            "scan",
            "Escaneo",
        )
        FAX = (
            "fax",
            "Fax",
        )
        RECEIVE = (
            "receive",
            "Recepción",
        )
        SEND = (
            "send",
            "Envío",
        )
        UNKNOWN = (
            "unknown",
            "No identificado",
        )

    class ColorMode(models.TextChoices):
        ALL = (
            "all",
            "Todos",
        )
        BLACK = (
            "black",
            "Blanco y negro",
        )
        COLOR = (
            "color",
            "Color",
        )
        SINGLE_COLOR = (
            "single_color",
            "Un color",
        )
        TWO_COLOR = (
            "two_color",
            "Dos colores",
        )
        UNKNOWN = (
            "unknown",
            "No identificado",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )

    class SidesMode(models.TextChoices):
        ALL = (
            "all",
            "Todos",
        )
        SIMPLEX = (
            "simplex",
            "Una cara",
        )
        DUPLEX = (
            "duplex",
            "Doble cara",
        )
        UNKNOWN = (
            "unknown",
            "No identificado",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )

    class ValueSource(models.TextChoices):
        DIRECT = (
            "direct",
            "Lectura directa",
        )
        CALCULATED = (
            "calculated",
            "Calculado",
        )
        DERIVED = (
            "derived",
            "Derivado",
        )
        MANUAL = (
            "manual",
            "Manual",
        )
        UNKNOWN = (
            "unknown",
            "No identificado",
        )

    class ValidationStatus(models.TextChoices):
        VALID = (
            "valid",
            "Válido",
        )
        SUSPECTED = (
            "suspected",
            "Sospechoso",
        )
        RESET_DETECTED = (
            "reset_detected",
            "Posible reinicio",
        )
        DECREASE_DETECTED = (
            "decrease_detected",
            "Disminución detectada",
        )
        OUT_OF_RANGE = (
            "out_of_range",
            "Fuera de rango",
        )
        UNKNOWN = (
            "unknown",
            "Sin validar",
        )

    snapshot = models.ForeignKey(
        "monitoring.DeviceSnapshot",
        on_delete=models.PROTECT,
        related_name="counter_readings",
        verbose_name="Captura",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        on_delete=models.PROTECT,
        related_name="counter_readings",
        verbose_name="Dispositivo",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_counter_readings",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_counter_readings",
        verbose_name="Sede",
    )

    captured_at = models.DateTimeField(
        db_index=True,
        verbose_name="Fecha de lectura",
    )

    metric_code = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Código normalizado",
        help_text=(
            "Identificador estable del contador. "
            "Ejemplo: TOTAL, PRINT_COLOR o SCAN_TOTAL."
        ),
    )

    metric_name = models.CharField(
        max_length=255,
        verbose_name="Nombre normalizado",
    )

    raw_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre original",
        help_text=(
            "Nombre exacto publicado por el fabricante."
        ),
    )

    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.UNKNOWN,
        db_index=True,
        verbose_name="Categoría",
    )

    function_type = models.CharField(
        max_length=30,
        choices=FunctionType.choices,
        default=FunctionType.UNKNOWN,
        db_index=True,
        verbose_name="Función",
    )

    color_mode = models.CharField(
        max_length=30,
        choices=ColorMode.choices,
        default=ColorMode.NOT_APPLICABLE,
        db_index=True,
        verbose_name="Modo de color",
    )

    sides_mode = models.CharField(
        max_length=30,
        choices=SidesMode.choices,
        default=SidesMode.NOT_APPLICABLE,
        db_index=True,
        verbose_name="Caras",
    )

    paper_size = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Formato de papel",
    )

    media_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tipo de soporte",
    )

    department_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de departamento",
    )

    user_identifier = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Identificador de usuario",
    )

    numeric_value = models.DecimalField(
        max_digits=30,
        decimal_places=4,
        verbose_name="Valor numérico",
    )

    integer_value = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Valor entero",
        help_text=(
            "Se utiliza para consultas rápidas cuando el contador "
            "no contiene decimales."
        ),
    )

    previous_value = models.DecimalField(
        max_digits=30,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Valor anterior",
    )

    delta_value = models.DecimalField(
        max_digits=30,
        decimal_places=4,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Variación",
    )

    unit = models.CharField(
        max_length=50,
        default="count",
        verbose_name="Unidad",
        help_text=(
            "Ejemplo: count, pages, sheets, jobs o cycles."
        ),
    )

    value_source = models.CharField(
        max_length=20,
        choices=ValueSource.choices,
        default=ValueSource.DIRECT,
        db_index=True,
        verbose_name="Fuente del valor",
    )

    validation_status = models.CharField(
        max_length=30,
        choices=ValidationStatus.choices,
        default=ValidationStatus.UNKNOWN,
        db_index=True,
        verbose_name="Validación",
    )

    confidence_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("100.00"),
        verbose_name="Confianza",
    )

    oid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="OID",
    )

    oid_index = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Índice OID",
    )

    raw_value = models.TextField(
        blank=True,
        verbose_name="Valor original",
    )

    profile_metric_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Métrica del perfil",
    )

    calculation_formula = models.TextField(
        blank=True,
        verbose_name="Fórmula aplicada",
    )

    calculation_inputs = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Valores usados en el cálculo",
    )

    is_primary = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Contador principal",
    )

    is_visible_in_reports = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Visible en reportes",
    )

    is_personal_data = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Contiene información personal",
        help_text=(
            "Debe activarse para contadores asociados a usuarios."
        ),
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Lectura de contador"
        verbose_name_plural = "Lecturas de contadores"
        ordering = (
            "-captured_at",
            "metric_code",
        )
        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "captured_at",
                    "metric_code",
                ],
                name="mon_count_customer_date_idx",
            ),
            models.Index(
                fields=[
                    "branch",
                    "captured_at",
                    "metric_code",
                ],
                name="mon_count_branch_date_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "metric_code",
                    "captured_at",
                ],
                name="mon_count_device_metric_idx",
            ),
            models.Index(
                fields=[
                    "category",
                    "function_type",
                    "captured_at",
                ],
                name="mon_count_category_func_idx",
            ),
            models.Index(
                fields=[
                    "validation_status",
                    "captured_at",
                ],
                name="mon_count_validation_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "snapshot",
                    "metric_code",
                    "oid",
                    "oid_index",
                    "user_identifier",
                    "department_code",
                ],
                name="unique_snapshot_counter_metric",
            ),
        ]

    def __str__(self):
        return (
            f"{self.device} - "
            f"{self.metric_name}: "
            f"{self.numeric_value}"
        )

    def calculate_delta(self):
        if self.previous_value is None:
            self.delta_value = None
            return

        self.delta_value = (
            self.numeric_value
            - self.previous_value
        )

        if self.delta_value < 0:
            self.validation_status = (
                self.ValidationStatus.DECREASE_DETECTED
            )

    def validate_against_previous(self):
        """
        Busca la lectura anterior de la misma métrica
        y calcula la variación.
        """

        previous = (
            CounterReading.objects
            .filter(
                device=self.device,
                metric_code=self.metric_code,
                captured_at__lt=self.captured_at,
            )
            .exclude(
                pk=self.pk,
            )
            .order_by(
                "-captured_at",
            )
            .first()
        )

        if not previous:
            self.previous_value = None
            self.delta_value = None

            if (
                self.validation_status
                == self.ValidationStatus.UNKNOWN
            ):
                self.validation_status = (
                    self.ValidationStatus.VALID
                )

            return

        self.previous_value = previous.numeric_value
        self.calculate_delta()

        if (
            self.delta_value is not None
            and self.delta_value >= 0
            and self.validation_status
            == self.ValidationStatus.UNKNOWN
        ):
            self.validation_status = (
                self.ValidationStatus.VALID
            )

    def clean(self):
        super().clean()

        text_fields = [
            "metric_code",
            "metric_name",
            "raw_name",
            "paper_size",
            "media_type",
            "department_code",
            "user_identifier",
            "unit",
            "oid",
            "oid_index",
            "raw_value",
            "profile_metric_code",
            "calculation_formula",
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
        self.paper_size = self.paper_size.upper()

        if not self.snapshot_id:
            raise ValidationError(
                {
                    "snapshot": (
                        "La captura es obligatoria."
                    ),
                }
            )

        if not self.device_id:
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo es obligatorio."
                    ),
                }
            )

        if not self.customer_id:
            raise ValidationError(
                {
                    "customer": (
                        "El cliente es obligatorio."
                    ),
                }
            )

        if not self.metric_code:
            raise ValidationError(
                {
                    "metric_code": (
                        "El código del contador es obligatorio."
                    ),
                }
            )

        if not self.metric_name:
            raise ValidationError(
                {
                    "metric_name": (
                        "El nombre del contador es obligatorio."
                    ),
                }
            )

        if self.snapshot.device_id != self.device_id:
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo no coincide con la captura."
                    ),
                }
            )

        if self.snapshot.customer_id != self.customer_id:
            raise ValidationError(
                {
                    "customer": (
                        "El cliente no coincide con la captura."
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

        if self.confidence_percent < 0:
            raise ValidationError(
                {
                    "confidence_percent": (
                        "La confianza no puede ser negativa."
                    ),
                }
            )

        if self.confidence_percent > 100:
            raise ValidationError(
                {
                    "confidence_percent": (
                        "La confianza no puede superar 100."
                    ),
                }
            )

        if self.numeric_value == self.numeric_value.to_integral_value():
            self.integer_value = int(
                self.numeric_value
            )
        else:
            self.integer_value = None

        if self.user_identifier:
            self.is_personal_data = True

    def save(self, *args, **kwargs):
        if self.snapshot_id:
            self.device = self.snapshot.device
            self.customer = self.snapshot.customer
            self.branch = self.snapshot.branch
            self.captured_at = self.snapshot.captured_at

        self.metric_code = str(
            self.metric_code or ""
        ).strip().upper()

        self.metric_name = str(
            self.metric_name or ""
        ).strip()

        self.validate_against_previous()
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
            "Las lecturas históricas no pueden archivarse."
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        raise ValidationError(
            "Las lecturas históricas no pueden restaurarse."
        )