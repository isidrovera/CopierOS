# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from .base import MonitoringBaseModel


class TrayReading(MonitoringBaseModel):
    """
    Lectura histórica de una bandeja o fuente de papel.

    Conserva capacidad, cantidad actual, tipo y tamaño de papel,
    estado físico y valores originales publicados por SNMP.
    """

    class TrayType(models.TextChoices):
        CASSETTE = (
            "cassette",
            "Casetera",
        )
        BYPASS = (
            "bypass",
            "Bandeja bypass",
        )
        LARGE_CAPACITY = (
            "large_capacity",
            "Gran capacidad",
        )
        MANUAL = (
            "manual",
            "Alimentación manual",
        )
        ENVELOPE = (
            "envelope",
            "Sobres",
        )
        ROLL = (
            "roll",
            "Rollo",
        )
        EXTERNAL = (
            "external",
            "Bandeja externa",
        )
        OTHER = (
            "other",
            "Otra",
        )
        UNKNOWN = (
            "unknown",
            "Sin identificar",
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
            "Papel bajo",
        )
        EMPTY = (
            "empty",
            "Vacía",
        )
        OPEN = (
            "open",
            "Abierta",
        )
        MISSING = (
            "missing",
            "No instalada",
        )
        WRONG_SIZE = (
            "wrong_size",
            "Tamaño incorrecto",
        )
        WRONG_TYPE = (
            "wrong_type",
            "Tipo incorrecto",
        )
        FEED_ERROR = (
            "feed_error",
            "Error de alimentación",
        )
        JAMMED = (
            "jammed",
            "Papel atascado",
        )
        OFFLINE = (
            "offline",
            "Fuera de servicio",
        )
        ERROR = (
            "error",
            "Con error",
        )

    snapshot = models.ForeignKey(
        "monitoring.DeviceSnapshot",
        on_delete=models.PROTECT,
        related_name="tray_readings",
        verbose_name="Captura",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        on_delete=models.PROTECT,
        related_name="tray_readings",
        verbose_name="Dispositivo",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_tray_readings",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_tray_readings",
        verbose_name="Sede",
    )

    captured_at = models.DateTimeField(
        db_index=True,
        verbose_name="Fecha de lectura",
    )

    tray_code = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Código normalizado",
        help_text=(
            "Ejemplo: TRAY_1, TRAY_2, BYPASS "
            "o LARGE_CAPACITY_TRAY."
        ),
    )

    tray_name = models.CharField(
        max_length=255,
        verbose_name="Nombre normalizado",
    )

    raw_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre original",
    )

    tray_type = models.CharField(
        max_length=30,
        choices=TrayType.choices,
        default=TrayType.UNKNOWN,
        db_index=True,
        verbose_name="Tipo de bandeja",
    )

    tray_index = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Índice de bandeja",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.UNKNOWN,
        db_index=True,
        verbose_name="Estado",
    )

    paper_size = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Tamaño de papel",
    )

    paper_width_mm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Ancho del papel en milímetros",
    )

    paper_height_mm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Alto del papel en milímetros",
    )

    paper_type = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Tipo de papel",
    )

    paper_color = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Color del papel",
    )

    paper_weight_gsm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Gramaje del papel",
    )

    current_level = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Cantidad actual",
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
        verbose_name="Porcentaje disponible",
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
        verbose_name="Bandeja instalada",
    )

    is_open = models.BooleanField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Bandeja abierta",
    )

    is_empty = models.BooleanField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Bandeja vacía",
    )

    is_low = models.BooleanField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Papel bajo",
    )

    has_feed_error = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Error de alimentación",
    )

    has_wrong_size = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Tamaño incorrecto",
    )

    has_wrong_type = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Tipo incorrecto",
    )

    has_jam = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Atasco relacionado",
    )

    unit = models.CharField(
        max_length=50,
        default="sheets",
        verbose_name="Unidad",
    )

    level_oid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="OID de nivel",
    )

    capacity_oid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="OID de capacidad",
    )

    status_oid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="OID de estado",
    )

    paper_size_oid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="OID de tamaño",
    )

    paper_type_oid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="OID de tipo de papel",
    )

    oid_index = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Índice OID",
    )

    raw_level_value = models.TextField(
        blank=True,
        verbose_name="Nivel original",
    )

    raw_capacity_value = models.TextField(
        blank=True,
        verbose_name="Capacidad original",
    )

    raw_status_value = models.TextField(
        blank=True,
        verbose_name="Estado original",
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
        verbose_name = "Lectura de bandeja"
        verbose_name_plural = "Lecturas de bandejas"
        ordering = (
            "-captured_at",
            "tray_code",
        )
        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "captured_at",
                    "status",
                ],
                name="mon_tray_customer_date_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "tray_code",
                    "captured_at",
                ],
                name="mon_tray_device_code_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "captured_at",
                ],
                name="mon_tray_status_date_idx",
            ),
            models.Index(
                fields=[
                    "is_empty",
                    "is_low",
                    "captured_at",
                ],
                name="mon_tray_level_date_idx",
            ),
            models.Index(
                fields=[
                    "has_feed_error",
                    "has_jam",
                    "captured_at",
                ],
                name="mon_tray_error_date_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "snapshot",
                    "tray_code",
                    "oid_index",
                ],
                name="unique_snapshot_tray",
            ),
        ]

    def __str__(self):
        value = (
            f"{self.percentage}%"
            if self.percentage is not None
            else self.raw_level_value
        )

        return (
            f"{self.device} - "
            f"{self.tray_name}: "
            f"{value}"
        )

    def calculate_percentage(self):
        if self.current_level is None:
            return

        if (
            self.current_level < 0
            or self.maximum_capacity is None
            or self.maximum_capacity <= 0
        ):
            self.percentage = None
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

        if self.has_jam:
            self.status = self.Status.JAMMED
            return

        if self.has_feed_error:
            self.status = self.Status.FEED_ERROR
            return

        if self.has_wrong_size:
            self.status = self.Status.WRONG_SIZE
            return

        if self.has_wrong_type:
            self.status = self.Status.WRONG_TYPE
            return

        if self.is_open is True:
            self.status = self.Status.OPEN
            return

        if self.is_empty is True:
            self.status = self.Status.EMPTY
            return

        if self.is_low is True:
            self.status = self.Status.LOW
            return

        if self.percentage is not None:
            if self.percentage <= Decimal("0"):
                self.status = self.Status.EMPTY
                self.is_empty = True
            elif self.percentage <= Decimal("20"):
                self.status = self.Status.LOW
                self.is_low = True
            else:
                self.status = self.Status.NORMAL

    def validate_against_previous(self):
        previous = (
            TrayReading.objects
            .filter(
                device=self.device,
                tray_code=self.tray_code,
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

        self.previous_percentage = previous.percentage

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
            "tray_code",
            "tray_name",
            "raw_name",
            "tray_index",
            "paper_size",
            "paper_type",
            "paper_color",
            "unit",
            "level_oid",
            "capacity_oid",
            "status_oid",
            "paper_size_oid",
            "paper_type_oid",
            "oid_index",
            "raw_level_value",
            "raw_capacity_value",
            "raw_status_value",
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

        self.tray_code = self.tray_code.upper()
        self.paper_size = self.paper_size.upper()

        if not self.snapshot_id:
            raise ValidationError(
                {
                    "snapshot": "La captura es obligatoria.",
                }
            )

        if not self.tray_code:
            raise ValidationError(
                {
                    "tray_code": (
                        "El código de la bandeja es obligatorio."
                    ),
                }
            )

        if not self.tray_name:
            raise ValidationError(
                {
                    "tray_name": (
                        "El nombre de la bandeja es obligatorio."
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

        if (
            self.current_level is not None
            and self.current_level < 0
        ):
            self.percentage = None

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
            self.paper_weight_gsm is not None
            and self.paper_weight_gsm <= 0
        ):
            raise ValidationError(
                {
                    "paper_weight_gsm": (
                        "El gramaje debe ser mayor que cero."
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

    def save(self, *args, **kwargs):
        if self.snapshot_id:
            self.device = self.snapshot.device
            self.customer = self.snapshot.customer
            self.branch = self.snapshot.branch
            self.captured_at = self.snapshot.captured_at

        self.tray_code = str(
            self.tray_code or ""
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