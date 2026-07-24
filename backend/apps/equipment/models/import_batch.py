# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from .base import EquipmentBaseModel


class ImportBatch(EquipmentBaseModel):
    """
    Representa una importación, lote de compra o ingreso principal
    de equipos.

    Este registro agrupa las máquinas que llegan bajo una misma
    importación, invoice, factura o proceso de compra.

    Posteriormente, cada equipo físico podrá relacionarse con este
    lote mediante el modelo Equipment.

    Ejemplos:

    - Importación marítima de 80 fotocopiadoras.
    - Compra local de 10 impresoras.
    - Ingreso de equipos recibidos de un proveedor.
    - Lote de máquinas usadas adquiridas en el extranjero.
    """

    class Status(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        CONFIRMED = (
            "confirmed",
            "Confirmada",
        )
        IN_TRANSIT = (
            "in_transit",
            "En tránsito",
        )
        RECEIVING = (
            "receiving",
            "En descarga",
        )
        COMPLETED = (
            "completed",
            "Completada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )

    class PurchaseType(models.TextChoices):
        IMPORT = (
            "import",
            "Importación",
        )
        LOCAL_PURCHASE = (
            "local_purchase",
            "Compra local",
        )
        THIRD_PARTY = (
            "third_party",
            "Equipo de tercero",
        )
        TRADE_IN = (
            "trade_in",
            "Recibido en parte de pago",
        )
        TRANSFER = (
            "transfer",
            "Transferencia entre empresas",
        )
        OTHER = (
            "other",
            "Otro",
        )

    class Currency(models.TextChoices):
        PEN = (
            "PEN",
            "Soles",
        )
        USD = (
            "USD",
            "Dólares estadounidenses",
        )
        EUR = (
            "EUR",
            "Euros",
        )
        OTHER = (
            "OTHER",
            "Otra moneda",
        )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código del lote",
        help_text=(
            "Código interno único de la importación o lote. "
            "Ejemplo: IMP-2026-0001."
        ),
    )

    purchase_type = models.CharField(
        max_length=30,
        choices=PurchaseType.choices,
        default=PurchaseType.IMPORT,
        db_index=True,
        verbose_name="Tipo de ingreso",
    )

    supplier = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="equipment_import_batches",
        verbose_name="Proveedor",
        help_text=(
            "Proveedor, empresa o tercero del que proceden "
            "los equipos."
        ),
    )

    import_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Número de importación",
        help_text=(
            "Número de importación, declaración, expediente "
            "o referencia aduanera."
        ),
    )

    purchase_order_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Orden de compra",
    )

    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Número de invoice o factura",
    )

    invoice_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de invoice o factura",
    )

    purchase_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de compra",
    )

    estimated_arrival_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha estimada de llegada",
    )

    arrival_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha real de llegada",
    )

    unloading_start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio de descarga",
    )

    unloading_end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin de descarga",
    )

    origin_country_code = models.CharField(
        max_length=2,
        blank=True,
        verbose_name="Código del país de origen",
        help_text=(
            "Código ISO de dos letras. "
            "Ejemplo: JP, US o CN."
        ),
    )

    origin_country_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="País de origen",
    )

    origin_port = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Puerto o lugar de origen",
    )

    destination_port = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Puerto o lugar de destino",
    )

    container_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Número de contenedor",
    )

    transport_reference = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Referencia de transporte",
        help_text=(
            "Número de conocimiento de embarque, guía, "
            "BL, tracking u otra referencia."
        ),
    )

    warehouse_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ubicación de recepción",
        help_text=(
            "Almacén, local o lugar donde se descargaron "
            "los equipos."
        ),
    )

    expected_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad esperada",
        help_text=(
            "Cantidad de equipos que deberían recibirse "
            "en este lote."
        ),
    )

    declared_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad declarada",
        help_text=(
            "Cantidad indicada en la invoice, factura "
            "o documentación de compra."
        ),
    )

    currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
        default=Currency.USD,
        db_index=True,
        verbose_name="Moneda",
    )

    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal("1.000000"),
        validators=[
            MinValueValidator(
                Decimal("0.000001")
            ),
        ],
        verbose_name="Tipo de cambio",
        help_text=(
            "Tipo de cambio utilizado para convertir el costo "
            "a la moneda local cuando corresponda."
        ),
    )

    equipment_subtotal = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            ),
        ],
        verbose_name="Subtotal de equipos",
    )

    freight_cost = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            ),
        ],
        verbose_name="Costo de flete",
    )

    insurance_cost = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            ),
        ],
        verbose_name="Costo de seguro",
    )

    customs_cost = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            ),
        ],
        verbose_name="Costos aduaneros",
    )

    tax_cost = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            ),
        ],
        verbose_name="Impuestos",
    )

    other_costs = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            ),
        ],
        verbose_name="Otros costos",
    )

    total_cost = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            ),
        ],
        verbose_name="Costo total",
        help_text=(
            "Suma de equipos, flete, seguro, aduanas, "
            "impuestos y otros costos."
        ),
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activo",
    )

    unloading_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones de descarga",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones generales",
    )

    class Meta:
        verbose_name = "Importación o lote"
        verbose_name_plural = "Importaciones y lotes"
        ordering = (
            "-purchase_date",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "supplier",
                    "status",
                ],
                name="eq_batch_supplier_status",
            ),
            models.Index(
                fields=[
                    "purchase_type",
                    "status",
                ],
                name="equip_batch_type_status_idx",
            ),
            models.Index(
                fields=[
                    "arrival_date",
                    "status",
                ],
                name="equip_batch_arrival_status_idx",
            ),
        ]

    def __str__(self):
        supplier_name = ""

        if self.supplier_id:
            supplier_name = str(
                self.supplier
            ).strip()

        if supplier_name:
            return f"{self.code} - {supplier_name}"

        return self.code

    def clean(self):
        """
        Normaliza y valida los datos de la importación o lote.
        """

        super().clean()

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.import_number = str(
            self.import_number or ""
        ).strip()

        self.purchase_order_number = str(
            self.purchase_order_number or ""
        ).strip()

        self.invoice_number = str(
            self.invoice_number or ""
        ).strip()

        self.origin_country_code = str(
            self.origin_country_code or ""
        ).strip().upper()

        self.origin_country_name = str(
            self.origin_country_name or ""
        ).strip()

        self.origin_port = str(
            self.origin_port or ""
        ).strip()

        self.destination_port = str(
            self.destination_port or ""
        ).strip()

        self.container_number = str(
            self.container_number or ""
        ).strip().upper()

        self.transport_reference = str(
            self.transport_reference or ""
        ).strip()

        self.warehouse_location = str(
            self.warehouse_location or ""
        ).strip()

        self.unloading_notes = str(
            self.unloading_notes or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        if not self.code:
            raise ValidationError(
                {
                    "code": (
                        "El código de la importación o lote "
                        "es obligatorio."
                    ),
                }
            )

        if not self.supplier_id:
            raise ValidationError(
                {
                    "supplier": "El proveedor es obligatorio.",
                }
            )

        if (
            self.origin_country_code
            and len(self.origin_country_code) != 2
        ):
            raise ValidationError(
                {
                    "origin_country_code": (
                        "El código del país de origen debe contener "
                        "exactamente dos letras."
                    ),
                }
            )

        if (
            self.origin_country_code
            and not self.origin_country_code.isalpha()
        ):
            raise ValidationError(
                {
                    "origin_country_code": (
                        "El código del país de origen solo puede "
                        "contener letras."
                    ),
                }
            )

        if (
            self.purchase_date
            and self.invoice_date
            and self.invoice_date > self.purchase_date
        ):
            raise ValidationError(
                {
                    "invoice_date": (
                        "La fecha de la invoice o factura no puede "
                        "ser posterior a la fecha de compra."
                    ),
                }
            )

        if (
            self.estimated_arrival_date
            and self.purchase_date
            and self.estimated_arrival_date < self.purchase_date
        ):
            raise ValidationError(
                {
                    "estimated_arrival_date": (
                        "La fecha estimada de llegada no puede ser "
                        "anterior a la fecha de compra."
                    ),
                }
            )

        if (
            self.arrival_date
            and self.purchase_date
            and self.arrival_date < self.purchase_date
        ):
            raise ValidationError(
                {
                    "arrival_date": (
                        "La fecha real de llegada no puede ser "
                        "anterior a la fecha de compra."
                    ),
                }
            )

        if (
            self.unloading_start_date
            and self.unloading_end_date
            and self.unloading_end_date < self.unloading_start_date
        ):
            raise ValidationError(
                {
                    "unloading_end_date": (
                        "La fecha de finalización de la descarga "
                        "no puede ser anterior a su inicio."
                    ),
                }
            )

        if (
            self.status == self.Status.COMPLETED
            and not self.arrival_date
        ):
            raise ValidationError(
                {
                    "arrival_date": (
                        "Una importación completada debe tener "
                        "una fecha real de llegada."
                    ),
                }
            )

        if (
            self.status == self.Status.COMPLETED
            and not self.unloading_end_date
        ):
            raise ValidationError(
                {
                    "unloading_end_date": (
                        "Una importación completada debe registrar "
                        "la fecha de finalización de la descarga."
                    ),
                }
            )

        if (
            self.expected_quantity
            and self.declared_quantity
            and self.expected_quantity != self.declared_quantity
        ):
            if not self.notes:
                raise ValidationError(
                    {
                        "notes": (
                            "Cuando la cantidad esperada y la cantidad "
                            "declarada son diferentes, debe registrar "
                            "una observación."
                        ),
                    }
                )

        duplicate_code = ImportBatch.objects.filter(
            code__iexact=self.code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe una importación o lote registrado "
                        "con este código."
                    ),
                }
            )

        calculated_total = (
            Decimal(
                self.equipment_subtotal or 0
            )
            + Decimal(
                self.freight_cost or 0
            )
            + Decimal(
                self.insurance_cost or 0
            )
            + Decimal(
                self.customs_cost or 0
            )
            + Decimal(
                self.tax_cost or 0
            )
            + Decimal(
                self.other_costs or 0
            )
        )

        self.total_cost = calculated_total

    def save(self, *args, **kwargs):
        """
        Normaliza, calcula y valida el lote antes de guardarlo.
        """

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.import_number = str(
            self.import_number or ""
        ).strip()

        self.purchase_order_number = str(
            self.purchase_order_number or ""
        ).strip()

        self.invoice_number = str(
            self.invoice_number or ""
        ).strip()

        self.origin_country_code = str(
            self.origin_country_code or ""
        ).strip().upper()

        self.origin_country_name = str(
            self.origin_country_name or ""
        ).strip()

        self.origin_port = str(
            self.origin_port or ""
        ).strip()

        self.destination_port = str(
            self.destination_port or ""
        ).strip()

        self.container_number = str(
            self.container_number or ""
        ).strip().upper()

        self.transport_reference = str(
            self.transport_reference or ""
        ).strip()

        self.warehouse_location = str(
            self.warehouse_location or ""
        ).strip()

        self.unloading_notes = str(
            self.unloading_notes or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        self.total_cost = (
            Decimal(
                self.equipment_subtotal or 0
            )
            + Decimal(
                self.freight_cost or 0
            )
            + Decimal(
                self.insurance_cost or 0
            )
            + Decimal(
                self.customs_cost or 0
            )
            + Decimal(
                self.tax_cost or 0
            )
            + Decimal(
                self.other_costs or 0
            )
        )

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
        """
        Archiva el lote y lo marca como inactivo.

        No se cambia automáticamente su estado operativo porque
        un lote completado puede archivarse únicamente para
        ocultarlo de las operaciones habituales.
        """

        self.is_active = False

        if save:
            self.save(
                update_fields=[
                    "is_active",
                    "updated_at",
                ]
            )

        return super().archive(
            user=user,
            reason=reason,
            save=save,
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        """
        Restaura el lote y vuelve a marcarlo como activo.
        """

        self.is_active = True

        if save:
            self.save(
                update_fields=[
                    "is_active",
                    "updated_at",
                ]
            )

        return super().restore(
            user=user,
            save=save,
        )