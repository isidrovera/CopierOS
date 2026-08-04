# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from .base import MonitoringBaseModel


class AccessoryReading(MonitoringBaseModel):
    """
    Lectura histórica de un accesorio detectado en el equipo.

    Permite registrar accesorios internos o externos como:

    - ADF o RADF.
    - Unidad dúplex.
    - Finalizadores.
    - Perforadores.
    - Unidad booklet.
    - Bandejas adicionales.
    - Alimentadores de gran capacidad.
    - Fax.
    - Disco duro.
    - Memoria.
    - Wi-Fi.
    - Lector de tarjetas.
    - Controlador Fiery.
    - PostScript.
    """

    class AccessoryType(models.TextChoices):
        ADF = (
            "adf",
            "ADF",
        )
        RADF = (
            "radf",
            "RADF",
        )
        DUPLEX = (
            "duplex",
            "Unidad dúplex",
        )
        FINISHER = (
            "finisher",
            "Finalizador",
        )
        STAPLER = (
            "stapler",
            "Engrapador",
        )
        PUNCH = (
            "punch",
            "Perforador",
        )
        BOOKLET = (
            "booklet",
            "Unidad booklet",
        )
        FOLDER = (
            "folder",
            "Plegadora",
        )
        EXTRA_TRAY = (
            "extra_tray",
            "Bandeja adicional",
        )
        LARGE_CAPACITY_TRAY = (
            "large_capacity_tray",
            "Alimentador de gran capacidad",
        )
        PEDESTAL = (
            "pedestal",
            "Pedestal",
        )
        PAPER_DECK = (
            "paper_deck",
            "Paper deck",
        )
        FAX = (
            "fax",
            "Fax",
        )
        HARD_DISK = (
            "hard_disk",
            "Disco duro",
        )
        MEMORY = (
            "memory",
            "Memoria",
        )
        WIFI = (
            "wifi",
            "Wi-Fi",
        )
        NETWORK_INTERFACE = (
            "network_interface",
            "Interfaz de red",
        )
        CARD_READER = (
            "card_reader",
            "Lector de tarjetas",
        )
        FIERY = (
            "fiery",
            "Controlador Fiery",
        )
        POSTSCRIPT = (
            "postscript",
            "PostScript",
        )
        TRANSPORT_UNIT = (
            "transport_unit",
            "Unidad de transporte",
        )
        OUTPUT_TRAY = (
            "output_tray",
            "Bandeja de salida",
        )
        OTHER = (
            "other",
            "Otro accesorio",
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
        INSTALLED = (
            "installed",
            "Instalado",
        )
        OPERATIONAL = (
            "operational",
            "Operativo",
        )
        WARNING = (
            "warning",
            "Con advertencia",
        )
        ERROR = (
            "error",
            "Con error",
        )
        DISABLED = (
            "disabled",
            "Deshabilitado",
        )
        MISSING = (
            "missing",
            "No instalado",
        )
        NOT_SUPPORTED = (
            "not_supported",
            "No compatible",
        )

    snapshot = models.ForeignKey(
        "monitoring.DeviceSnapshot",
        on_delete=models.PROTECT,
        related_name="accessory_readings",
        verbose_name="Captura",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        on_delete=models.PROTECT,
        related_name="accessory_readings",
        verbose_name="Dispositivo",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_accessory_readings",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_accessory_readings",
        verbose_name="Sede",
    )

    equipment_component = models.ForeignKey(
        "equipment.EquipmentComponent",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_accessory_readings",
        verbose_name="Accesorio de Copier OS",
    )

    captured_at = models.DateTimeField(
        db_index=True,
        verbose_name="Fecha de lectura",
    )

    accessory_code = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Código normalizado",
        help_text=(
            "Ejemplo: FINISHER_1, ADF, DUPLEX_UNIT "
            "o LARGE_CAPACITY_TRAY."
        ),
    )

    accessory_name = models.CharField(
        max_length=255,
        verbose_name="Nombre normalizado",
    )

    raw_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre original",
    )

    accessory_type = models.CharField(
        max_length=40,
        choices=AccessoryType.choices,
        default=AccessoryType.UNKNOWN,
        db_index=True,
        verbose_name="Tipo de accesorio",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.UNKNOWN,
        db_index=True,
        verbose_name="Estado",
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad detectada",
    )

    is_installed = models.BooleanField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Instalado",
    )

    is_operational = models.BooleanField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Operativo",
    )

    is_enabled = models.BooleanField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Habilitado",
    )

    manufacturer_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Fabricante",
    )

    model_name = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Modelo del accesorio",
    )

    product_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de producto",
    )

    serial_number = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Número de serie",
    )

    firmware_version = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Versión de firmware",
    )

    capacity_value = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Capacidad reportada",
    )

    capacity_unit = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Unidad de capacidad",
        help_text=(
            "Ejemplo: sheets, MB, GB, slots o trays."
        ),
    )

    memory_size_mb = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Memoria en MB",
    )

    storage_size_mb = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Almacenamiento en MB",
    )

    supported_paper_size = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Formato de papel compatible",
    )

    output_capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Capacidad de salida",
    )

    staple_capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Capacidad de grapas",
    )

    punch_hole_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Cantidad de perforaciones",
    )

    installed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de instalación reportada",
    )

    oid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="OID principal",
    )

    status_oid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="OID de estado",
    )

    quantity_oid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="OID de cantidad",
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
        verbose_name = "Lectura de accesorio"
        verbose_name_plural = "Lecturas de accesorios"
        ordering = (
            "-captured_at",
            "accessory_code",
        )
        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "captured_at",
                    "accessory_type",
                ],
                name="mon_acc_customer_date_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "accessory_code",
                    "captured_at",
                ],
                name="mon_acc_device_code_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "captured_at",
                ],
                name="mon_acc_status_date_idx",
            ),
            models.Index(
                fields=[
                    "is_installed",
                    "is_operational",
                    "captured_at",
                ],
                name="mon_acc_installed_date_idx",
            ),
            models.Index(
                fields=[
                    "equipment_component",
                    "captured_at",
                ],
                name="mon_acc_catalog_date_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "snapshot",
                    "accessory_code",
                    "oid_index",
                    "serial_number",
                ],
                name="unique_snapshot_accessory",
            ),
        ]

    def __str__(self):
        return (
            f"{self.device} - "
            f"{self.accessory_name} - "
            f"{self.quantity}"
        )

    def calculate_status(self):
        if self.is_installed is False:
            self.status = self.Status.MISSING
            return

        if self.is_enabled is False:
            self.status = self.Status.DISABLED
            return

        if self.is_operational is False:
            self.status = self.Status.ERROR
            return

        if (
            self.is_installed is True
            and self.is_operational is True
        ):
            self.status = self.Status.OPERATIONAL
            return

        if self.is_installed is True:
            self.status = self.Status.INSTALLED

    def clean(self):
        super().clean()

        text_fields = [
            "accessory_code",
            "accessory_name",
            "raw_name",
            "manufacturer_name",
            "model_name",
            "product_code",
            "serial_number",
            "firmware_version",
            "capacity_unit",
            "supported_paper_size",
            "oid",
            "status_oid",
            "quantity_oid",
            "oid_index",
            "raw_value",
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

        self.accessory_code = self.accessory_code.upper()
        self.product_code = self.product_code.upper()
        self.serial_number = self.serial_number.upper()
        self.supported_paper_size = (
            self.supported_paper_size.upper()
        )

        if not self.snapshot_id:
            raise ValidationError(
                {
                    "snapshot": "La captura es obligatoria.",
                }
            )

        if not self.accessory_code:
            raise ValidationError(
                {
                    "accessory_code": (
                        "El código del accesorio es obligatorio."
                    ),
                }
            )

        if not self.accessory_name:
            raise ValidationError(
                {
                    "accessory_name": (
                        "El nombre del accesorio es obligatorio."
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

        if self.quantity < 1:
            raise ValidationError(
                {
                    "quantity": (
                        "La cantidad debe ser como mínimo uno."
                    ),
                }
            )

        if (
            self.capacity_value is not None
            and self.capacity_value < 0
        ):
            raise ValidationError(
                {
                    "capacity_value": (
                        "La capacidad no puede ser negativa."
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

    def save(self, *args, **kwargs):
        if self.snapshot_id:
            self.device = self.snapshot.device
            self.customer = self.snapshot.customer
            self.branch = self.snapshot.branch
            self.captured_at = self.snapshot.captured_at

        self.accessory_code = str(
            self.accessory_code or ""
        ).strip().upper()

        self.product_code = str(
            self.product_code or ""
        ).strip().upper()

        self.serial_number = str(
            self.serial_number or ""
        ).strip().upper()

        self.calculate_status()
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