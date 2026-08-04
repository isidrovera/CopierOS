# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from .base import MonitoringBaseModel


class ConsumableReading(MonitoringBaseModel):
    """
    Lectura histórica de un consumible detectado por SNMP.

    Permite registrar:

    - Tóner negro, cyan, magenta y amarillo.
    - Botella de residuos.
    - Grapas.
    - Aceite.
    - Web de limpieza.
    - Kits de mantenimiento.
    - Otros consumibles publicados por el fabricante.

    Conserva el valor original incluso cuando todavía
    no se conoce su interpretación exacta.
    """

    class ConsumableType(models.TextChoices):
        TONER = (
            "toner",
            "Tóner",
        )
        INK = (
            "ink",
            "Tinta",
        )
        WASTE_TONER = (
            "waste_toner",
            "Depósito de residuos",
        )
        STAPLE = (
            "staple",
            "Grapas",
        )
        OIL = (
            "oil",
            "Aceite",
        )
        CLEANING_WEB = (
            "cleaning_web",
            "Web de limpieza",
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
        LIGHT_CYAN = (
            "light_cyan",
            "Cyan claro",
        )
        LIGHT_MAGENTA = (
            "light_magenta",
            "Magenta claro",
        )
        GRAY = (
            "gray",
            "Gris",
        )
        WHITE = (
            "white",
            "Blanco",
        )
        CLEAR = (
            "clear",
            "Transparente",
        )
        MULTICOLOR = (
            "multicolor",
            "Multicolor",
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
        LOW = (
            "low",
            "Bajo",
        )
        VERY_LOW = (
            "very_low",
            "Muy bajo",
        )
        EMPTY = (
            "empty",
            "Vacío",
        )
        MISSING = (
            "missing",
            "No instalado",
        )
        REPLACEMENT_REQUIRED = (
            "replacement_required",
            "Requiere cambio",
        )
        INVALID = (
            "invalid",
            "No reconocido",
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
        CURRENT_CAPACITY = (
            "current_capacity",
            "Capacidad actual",
        )
        REMAINING_UNITS = (
            "remaining_units",
            "Unidades restantes",
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
        related_name="consumable_readings",
        verbose_name="Captura",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        on_delete=models.PROTECT,
        related_name="consumable_readings",
        verbose_name="Dispositivo",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_consumable_readings",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_consumable_readings",
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
            "Ejemplo: TONER_BLACK, TONER_CYAN "
            "o WASTE_TONER."
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

    consumable_type = models.CharField(
        max_length=40,
        choices=ConsumableType.choices,
        default=ConsumableType.UNKNOWN,
        db_index=True,
        verbose_name="Tipo de consumible",
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
        verbose_name="Interpretación del valor",
    )

    current_level = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Nivel actual reportado",
    )

    maximum_capacity = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Capacidad máxima",
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

    is_present = models.BooleanField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Consumible instalado",
    )

    is_original = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Consumible original",
    )

    cartridge_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código del cartucho",
    )

    cartridge_serial = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Serie del cartucho",
    )

    manufacturer_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Fabricante reportado",
    )

    estimated_yield = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Rendimiento estimado",
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
        verbose_name="Cambio estimado",
    )

    replacement_required = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere reemplazo",
    )

    special_value_code = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Código especial reportado",
        help_text=(
            "Conserva valores como -1, -2 o -3 cuando "
            "el fabricante utiliza códigos especiales."
        ),
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

    maximum_capacity_oid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="OID de capacidad máxima",
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

    raw_maximum_capacity = models.TextField(
        blank=True,
        verbose_name="Capacidad original",
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
        verbose_name = "Lectura de consumible"
        verbose_name_plural = "Lecturas de consumibles"
        ordering = (
            "-captured_at",
            "metric_code",
        )
        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "captured_at",
                    "consumable_type",
                ],
                name="mon_cons_customer_date_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "metric_code",
                    "captured_at",
                ],
                name="mon_cons_device_metric_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "captured_at",
                ],
                name="mon_cons_status_date_idx",
            ),
            models.Index(
                fields=[
                    "replacement_required",
                    "captured_at",
                ],
                name="mon_cons_replace_date_idx",
            ),
            models.Index(
                fields=[
                    "color",
                    "consumable_type",
                    "captured_at",
                ],
                name="mon_cons_color_type_idx",
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
                name="unique_snapshot_consumable",
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
        """
        Normaliza el porcentaje cuando el fabricante publica
        nivel actual y capacidad máxima.

        Los valores negativos nunca se convierten directamente
        en porcentaje.
        """

        if self.current_level is None:
            return

        if self.current_level < 0:
            self.special_value_code = int(
                self.current_level
            )
            self.value_meaning = (
                self.ValueMeaning.SPECIAL_VALUE
            )
            self.percentage = None
            return

        if (
            self.maximum_capacity is None
            or self.maximum_capacity <= 0
        ):
            return

        calculated = (
            self.current_level
            / self.maximum_capacity
        ) * Decimal("100")

        self.percentage = max(
            Decimal("0"),
            min(
                calculated,
                Decimal("100"),
            ),
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
            self.status = self.Status.EMPTY
        elif self.percentage <= Decimal("5"):
            self.status = self.Status.VERY_LOW
        elif self.percentage <= Decimal("20"):
            self.status = self.Status.LOW
        else:
            self.status = self.Status.NORMAL

    def validate_against_previous(self):
        previous = (
            ConsumableReading.objects
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
            "cartridge_code",
            "cartridge_serial",
            "manufacturer_name",
            "special_value_meaning",
            "unit",
            "oid",
            "maximum_capacity_oid",
            "status_oid",
            "oid_index",
            "raw_value",
            "raw_maximum_capacity",
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
        self.cartridge_code = self.cartridge_code.upper()
        self.cartridge_serial = self.cartridge_serial.upper()

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
                        "El código del consumible es obligatorio."
                    ),
                }
            )

        if not self.metric_name:
            raise ValidationError(
                {
                    "metric_name": (
                        "El nombre del consumible es obligatorio."
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
            self.maximum_capacity is not None
            and self.maximum_capacity < 0
        ):
            raise ValidationError(
                {
                    "maximum_capacity": (
                        "La capacidad máxima no puede ser negativa."
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
            in {
                self.Status.EMPTY,
                self.Status.REPLACEMENT_REQUIRED,
            }
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