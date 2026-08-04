# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from .base import MonitoringBaseModel


class ComponentReading(MonitoringBaseModel):
    """
    Lectura histórica de una unidad o componente técnico.

    Permite registrar componentes conocidos y también componentes
    todavía no identificados dentro del catálogo de Copier OS.
    """

    class ComponentCategory(models.TextChoices):
        IMAGING_UNIT = (
            "imaging_unit",
            "Unidad de imagen",
        )
        DRUM = (
            "drum",
            "Tambor",
        )
        DEVELOPER = (
            "developer",
            "Revelador",
        )
        FUSER = (
            "fuser",
            "Unidad fusora",
        )
        TRANSFER = (
            "transfer",
            "Transferencia",
        )
        CLEANING = (
            "cleaning",
            "Limpieza",
        )
        FEED = (
            "feed",
            "Alimentación de papel",
        )
        ADF = (
            "adf",
            "Alimentador de documentos",
        )
        SCANNER = (
            "scanner",
            "Escáner",
        )
        LASER = (
            "laser",
            "Unidad láser",
        )
        CORONA = (
            "corona",
            "Corona",
        )
        FILTER = (
            "filter",
            "Filtro",
        )
        MAINTENANCE_KIT = (
            "maintenance_kit",
            "Kit de mantenimiento",
        )
        OTHER = (
            "other",
            "Otro",
        )
        UNKNOWN = (
            "unknown",
            "Sin identificar",
        )

    class Color(models.TextChoices):
        BLACK = (
            "black",
            "Negro",
        )
        CYAN = (
            "cyan",
            "Cyan",
        )
        MAGENTA = (
            "magenta",
            "Magenta",
        )
        YELLOW = (
            "yellow",
            "Amarillo",
        )
        COLOR = (
            "color",
            "Color",
        )
        MONOCHROME = (
            "monochrome",
            "Blanco y negro",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )
        UNKNOWN = (
            "unknown",
            "No identificado",
        )

    class Status(models.TextChoices):
        UNKNOWN = (
            "unknown",
            "Desconocido",
        )
        NORMAL = (
            "normal",
            "Normal",
        )
        WARNING = (
            "warning",
            "Advertencia",
        )
        LOW = (
            "low",
            "Vida útil baja",
        )
        VERY_LOW = (
            "very_low",
            "Vida útil muy baja",
        )
        REPLACEMENT_REQUIRED = (
            "replacement_required",
            "Requiere reemplazo",
        )
        MISSING = (
            "missing",
            "No instalado",
        )
        ERROR = (
            "error",
            "Con error",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )

    class ValueMeaning(models.TextChoices):
        PERCENT_REMAINING = (
            "percent_remaining",
            "Porcentaje restante",
        )
        PERCENT_USED = (
            "percent_used",
            "Porcentaje utilizado",
        )
        CURRENT_LIFE = (
            "current_life",
            "Vida actual",
        )
        REMAINING_LIFE = (
            "remaining_life",
            "Vida restante",
        )
        CYCLE_COUNT = (
            "cycle_count",
            "Cantidad de ciclos",
        )
        STATUS_CODE = (
            "status_code",
            "Código de estado",
        )
        SPECIAL_VALUE = (
            "special_value",
            "Valor especial",
        )
        UNKNOWN = (
            "unknown",
            "Interpretación desconocida",
        )

    snapshot = models.ForeignKey(
        "monitoring.DeviceSnapshot",
        on_delete=models.PROTECT,
        related_name="component_readings",
        verbose_name="Captura",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        on_delete=models.PROTECT,
        related_name="component_readings",
        verbose_name="Dispositivo",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_component_readings",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_component_readings",
        verbose_name="Sede",
    )

    equipment_component = models.ForeignKey(
        "equipment.EquipmentComponent",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_readings",
        verbose_name="Componente de Copier OS",
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
            "Ejemplo: DRUM_BLACK, DEVELOPER_CYAN, "
            "FUSER_UNIT o TRANSFER_BELT."
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
    )

    component_category = models.CharField(
        max_length=40,
        choices=ComponentCategory.choices,
        default=ComponentCategory.UNKNOWN,
        db_index=True,
        verbose_name="Categoría",
    )

    color = models.CharField(
        max_length=30,
        choices=Color.choices,
        default=Color.NOT_APPLICABLE,
        db_index=True,
        verbose_name="Color",
    )

    status = models.CharField(
        max_length=40,
        choices=Status.choices,
        default=Status.UNKNOWN,
        db_index=True,
        verbose_name="Estado",
    )

    value_meaning = models.CharField(
        max_length=40,
        choices=ValueMeaning.choices,
        default=ValueMeaning.UNKNOWN,
        db_index=True,
        verbose_name="Interpretación",
    )

    reported_value = models.DecimalField(
        max_digits=24,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Valor reportado",
    )

    maximum_value = models.DecimalField(
        max_digits=24,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Valor máximo",
    )

    percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Porcentaje normalizado",
    )

    previous_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Porcentaje anterior",
    )

    delta_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Variación porcentual",
    )

    cycle_count = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Cantidad de ciclos",
    )

    expected_life_cycles = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Vida útil esperada",
    )

    remaining_cycles = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Ciclos restantes estimados",
    )

    is_present = models.BooleanField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Componente instalado",
    )

    replacement_required = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere reemplazo",
    )

    manufacturer_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código del fabricante",
    )

    serial_number = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Serie del componente",
    )

    installed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de instalación reportada",
    )

    estimated_replacement_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha estimada de reemplazo",
    )

    special_value_code = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Código especial",
    )

    special_value_meaning = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Significado del valor especial",
    )

    unit = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Unidad",
    )

    oid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="OID del valor",
    )

    maximum_value_oid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="OID del valor máximo",
    )

    status_oid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="OID de estado",
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

    raw_maximum_value = models.TextField(
        blank=True,
        verbose_name="Valor máximo original",
    )

    profile_metric_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Métrica del perfil",
    )

    confidence_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("100.00"),
        verbose_name="Confianza",
    )

    is_visible_in_reports = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Visible en reportes",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Lectura de componente"
        verbose_name_plural = "Lecturas de componentes"
        ordering = (
            "-captured_at",
            "metric_code",
        )
        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "captured_at",
                    "component_category",
                ],
                name="mon_comp_customer_date_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "metric_code",
                    "captured_at",
                ],
                name="mon_comp_device_metric_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "captured_at",
                ],
                name="mon_comp_status_date_idx",
            ),
            models.Index(
                fields=[
                    "replacement_required",
                    "captured_at",
                ],
                name="mon_comp_replace_date_idx",
            ),
            models.Index(
                fields=[
                    "equipment_component",
                    "captured_at",
                ],
                name="mon_comp_catalog_date_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "snapshot",
                    "metric_code",
                    "oid",
                    "oid_index",
                ],
                name="unique_snapshot_component",
            ),
        ]

    def __str__(self):
        value = (
            f"{self.percentage}%"
            if self.percentage is not None
            else self.raw_value
        )

        return (
            f"{self.device} - "
            f"{self.metric_name}: "
            f"{value}"
        )

    def calculate_percentage(self):
        if self.reported_value is None:
            return

        if self.reported_value < 0:
            self.special_value_code = int(
                self.reported_value
            )
            self.value_meaning = (
                self.ValueMeaning.SPECIAL_VALUE
            )
            self.percentage = None
            return

        if (
            self.maximum_value is None
            or self.maximum_value <= 0
        ):
            return

        percentage = (
            self.reported_value
            / self.maximum_value
        ) * Decimal("100")

        if (
            self.value_meaning
            == self.ValueMeaning.PERCENT_USED
        ):
            percentage = (
                Decimal("100") - percentage
            )

        self.percentage = max(
            Decimal("0"),
            min(
                percentage,
                Decimal("100"),
            ),
        )

    def calculate_remaining_cycles(self):
        if (
            self.expected_life_cycles is None
            or self.cycle_count is None
        ):
            self.remaining_cycles = None
            return

        self.remaining_cycles = (
            self.expected_life_cycles
            - self.cycle_count
        )

    def calculate_status(self):
        if self.is_present is False:
            self.status = self.Status.MISSING
            return

        if self.replacement_required:
            self.status = (
                self.Status.REPLACEMENT_REQUIRED
            )
            return

        if self.percentage is None:
            return

        if self.percentage <= Decimal("0"):
            self.status = (
                self.Status.REPLACEMENT_REQUIRED
            )
            self.replacement_required = True
        elif self.percentage <= Decimal("5"):
            self.status = self.Status.VERY_LOW
        elif self.percentage <= Decimal("20"):
            self.status = self.Status.LOW
        elif self.percentage <= Decimal("35"):
            self.status = self.Status.WARNING
        else:
            self.status = self.Status.NORMAL

    def validate_against_previous(self):
        previous = (
            ComponentReading.objects
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
            self.previous_percentage = None
            self.delta_percentage = None
            return

        self.previous_percentage = (
            previous.percentage
        )

        if (
            self.percentage is not None
            and previous.percentage is not None
        ):
            self.delta_percentage = (
                self.percentage
                - previous.percentage
            )

    def clean(self):
        super().clean()

        text_fields = [
            "metric_code",
            "metric_name",
            "raw_name",
            "manufacturer_code",
            "serial_number",
            "special_value_meaning",
            "unit",
            "oid",
            "maximum_value_oid",
            "status_oid",
            "oid_index",
            "raw_value",
            "raw_maximum_value",
            "profile_metric_code",
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
        self.manufacturer_code = (
            self.manufacturer_code.upper()
        )
        self.serial_number = self.serial_number.upper()

        if not self.snapshot_id:
            raise ValidationError(
                {
                    "snapshot": "La captura es obligatoria.",
                }
            )

        if not self.metric_code:
            raise ValidationError(
                {
                    "metric_code": (
                        "El código del componente es obligatorio."
                    ),
                }
            )

        if not self.metric_name:
            raise ValidationError(
                {
                    "metric_name": (
                        "El nombre del componente es obligatorio."
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

        if self.percentage is not None:
            if (
                self.percentage < 0
                or self.percentage > 100
            ):
                raise ValidationError(
                    {
                        "percentage": (
                            "El porcentaje debe estar "
                            "entre 0 y 100."
                        ),
                    }
                )

        if (
            self.maximum_value is not None
            and self.maximum_value < 0
        ):
            raise ValidationError(
                {
                    "maximum_value": (
                        "El valor máximo no puede ser negativo."
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
                        "La confianza debe estar "
                        "entre 0 y 100."
                    ),
                }
            )

        if (
            self.status
            == self.Status.REPLACEMENT_REQUIRED
        ):
            self.replacement_required = True

    def save(self, *args, **kwargs):
        if self.snapshot_id:
            self.device = self.snapshot.device
            self.customer = self.snapshot.customer
            self.branch = self.snapshot.branch
            self.captured_at = self.snapshot.captured_at

        self.metric_code = str(
            self.metric_code or ""
        ).strip().upper()

        self.calculate_percentage()
        self.calculate_remaining_cycles()
        self.calculate_status()
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