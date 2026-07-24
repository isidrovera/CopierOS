# -*- coding: utf-8 -*-
import os
import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from .base import EquipmentBaseModel
from .equipment_model import EquipmentModel
from .import_batch import ImportBatch


def equipment_photo_path(instance, filename):
    """
    Guarda las fotografías organizadas por equipo.

    Ejemplo:

    equipment/machines/<uuid>/main.jpg
    """

    extension = os.path.splitext(
        filename
    )[1].lower() or ".jpg"

    equipment_id = instance.id or uuid.uuid4()

    return (
        f"equipment/machines/"
        f"{equipment_id}/main{extension}"
    )


class Equipment(EquipmentBaseModel):
    """
    Representa una máquina física individual.

    Cada equipo tiene:

    - Marca y modelo mediante EquipmentModel.
    - Número de serie único.
    - Código interno.
    - Importación o lote de procedencia.
    - Datos de compra.
    - Datos de venta cuando corresponda.
    - Contadores actuales.
    - Estado técnico.
    - Estado logístico o comercial.
    - Disponibilidad calculada.
    - Cliente y sucursal cuando se separa, vende o entrega.

    Las reparaciones, contratos, accesorios, unidades técnicas,
    movimientos y lecturas históricas se relacionarán mediante
    modelos independientes.
    """

    class PhysicalCondition(models.TextChoices):
        NEW = (
            "new",
            "Nueva",
        )
        USED = (
            "used",
            "Usada",
        )
        RECONDITIONED = (
            "reconditioned",
            "Reacondicionada",
        )
        TRADE_IN = (
            "trade_in",
            "Recibida en parte de pago",
        )
        THIRD_PARTY = (
            "third_party",
            "Propiedad de tercero",
        )
        OTHER = (
            "other",
            "Otra",
        )

    class OwnershipType(models.TextChoices):
        OWN = (
            "own",
            "Propiedad de la empresa",
        )
        CUSTOMER = (
            "customer",
            "Propiedad de cliente",
        )
        SUPPLIER = (
            "supplier",
            "Propiedad de proveedor",
        )
        THIRD_PARTY = (
            "third_party",
            "Propiedad de tercero",
        )
        OTHER = (
            "other",
            "Otra",
        )

    class TechnicalStatus(models.TextChoices):
        UNREVIEWED = (
            "unreviewed",
            "Sin revisar",
        )
        FOR_REVIEW = (
            "for_review",
            "Para revisión",
        )
        IN_REVIEW = (
            "in_review",
            "En revisión",
        )
        COMPLETED = (
            "completed",
            "Finalizada",
        )
        WITH_PROBLEMS = (
            "with_problems",
            "Con problemas",
        )
        FOR_PARTS = (
            "for_parts",
            "De partes",
        )

    class CommercialStatus(models.TextChoices):
        WAREHOUSE = (
            "warehouse",
            "En almacén",
        )
        RESERVED = (
            "reserved",
            "Separada",
        )
        SOLD = (
            "sold",
            "Vendida",
        )
        DELIVERY_PREPARATION = (
            "delivery_preparation",
            "En preparación de entrega",
        )
        IN_TRANSIT = (
            "in_transit",
            "En tránsito",
        )
        DELIVERED = (
            "delivered",
            "Entregada",
        )
        CONTRACT_ASSIGNED = (
            "contract_assigned",
            "Asignada a contrato",
        )
        INSTALLED = (
            "installed",
            "Instalada",
        )
        RETURN_PROCESS = (
            "return_process",
            "En proceso de retorno",
        )
        RETURNED = (
            "returned",
            "Retornada a almacén",
        )
        TEMPORARY_LOAN = (
            "temporary_loan",
            "Préstamo temporal",
        )
        DEMONSTRATION = (
            "demonstration",
            "Demostración",
        )
        REPLACEMENT = (
            "replacement",
            "Equipo de reemplazo",
        )
        OUT_OF_SERVICE = (
            "out_of_service",
            "Fuera de servicio",
        )
        DISPOSED = (
            "disposed",
            "De baja",
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

    class MeterSource(models.TextChoices):
        MANUAL = (
            "manual",
            "Ingreso manual",
        )
        DOWNLOAD = (
            "download",
            "Registro de descarga",
        )
        MOBILE_APP = (
            "mobile_app",
            "Aplicación móvil",
        )
        SNMP = (
            "snmp",
            "Lectura SNMP",
        )
        REPAIR = (
            "repair",
            "Reparación",
        )
        INSTALLATION = (
            "installation",
            "Instalación",
        )
        REMOVAL = (
            "removal",
            "Retiro",
        )
        DELIVERY = (
            "delivery",
            "Entrega",
        )
        OTHER = (
            "other",
            "Otra fuente",
        )

    internal_code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código interno",
        help_text=(
            "Código único generado o asignado por la empresa. "
            "Ejemplo: EQ-2026-000001."
        ),
    )

    serial_number = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        verbose_name="Número de serie",
        help_text=(
            "Número de serie físico del fabricante. "
            "No puede repetirse."
        ),
    )

    equipment_model = models.ForeignKey(
        EquipmentModel,
        on_delete=models.PROTECT,
        related_name="equipment_units",
        verbose_name="Modelo",
    )

    import_batch = models.ForeignKey(
        ImportBatch,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="equipment_units",
        verbose_name="Importación o lote",
        help_text=(
            "Importación, compra o lote mediante el cual "
            "ingresó el equipo."
        ),
    )

    ownership_type = models.CharField(
        max_length=20,
        choices=OwnershipType.choices,
        default=OwnershipType.OWN,
        db_index=True,
        verbose_name="Tipo de propiedad",
    )

    physical_condition = models.CharField(
        max_length=20,
        choices=PhysicalCondition.choices,
        default=PhysicalCondition.USED,
        db_index=True,
        verbose_name="Condición física de ingreso",
    )

    supplier = models.ForeignKey(
        "partners.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="supplied_equipment",
        verbose_name="Proveedor",
        help_text=(
            "Proveedor directo de esta máquina. "
            "Puede heredarse conceptualmente del lote, pero se "
            "guarda para identificar casos especiales."
        ),
    )

    owner_partner = models.ForeignKey(
        "partners.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="owned_external_equipment",
        verbose_name="Propietario externo",
        help_text=(
            "Se utiliza cuando el equipo pertenece a un cliente, "
            "proveedor o tercero."
        ),
    )

    customer = models.ForeignKey(
        "partners.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="assigned_equipment",
        verbose_name="Cliente relacionado",
        help_text=(
            "Cliente para el cual el equipo fue separado, vendido, "
            "entregado o asignado."
        ),
    )

    customer_branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="assigned_equipment",
        verbose_name="Sucursal del cliente",
        help_text=(
            "Sucursal, obra, proyecto o local al cual se encuentra "
            "relacionado el equipo."
        ),
    )

    advisor = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="commercial_equipment",
        verbose_name="Asesor comercial",
    )

    import_reference = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Referencia de importación",
        help_text=(
            "Referencia adicional de importación específica "
            "para esta máquina."
        ),
    )

    purchase_invoice_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Factura o invoice de compra",
    )

    purchase_invoice_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de factura de compra",
    )

    purchase_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de compra",
    )

    unloading_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha y hora de descarga",
        help_text=(
            "Fecha y hora en que la serie fue registrada "
            "durante la descarga."
        ),
    )

    unloading_registered_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="unloaded_equipment",
        verbose_name="Registrado en descarga por",
    )

    purchase_currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
        default=Currency.USD,
        verbose_name="Moneda de compra",
    )

    purchase_price = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            ),
        ],
        verbose_name="Precio de compra",
    )

    allocated_import_cost = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            ),
        ],
        verbose_name="Costo de importación asignado",
        help_text=(
            "Parte del flete, seguro, aduanas, impuestos u otros "
            "costos asignados específicamente a esta máquina."
        ),
    )

    total_acquisition_cost = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            ),
        ],
        verbose_name="Costo total de adquisición",
        help_text=(
            "Suma del precio de compra y el costo de importación "
            "asignado."
        ),
    )

    sale_currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
        default=Currency.PEN,
        verbose_name="Moneda de venta",
    )

    sale_price = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00")
            ),
        ],
        verbose_name="Precio de venta",
    )

    sale_invoice_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Factura de venta",
    )

    sale_invoice_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de factura de venta",
    )

    reservation_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de separación",
    )

    reservation_expiration_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Vencimiento de separación",
    )

    sale_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de venta",
    )

    delivery_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha real de entrega",
    )

    technical_status = models.CharField(
        max_length=30,
        choices=TechnicalStatus.choices,
        default=TechnicalStatus.UNREVIEWED,
        db_index=True,
        verbose_name="Estado técnico",
    )

    commercial_status = models.CharField(
        max_length=30,
        choices=CommercialStatus.choices,
        default=CommercialStatus.WAREHOUSE,
        db_index=True,
        verbose_name="Estado logístico o comercial",
    )

    is_available = models.BooleanField(
        default=True,
        db_index=True,
        editable=False,
        verbose_name="Disponible",
        help_text=(
            "Se calcula automáticamente según el estado técnico, "
            "comercial y el archivado del equipo."
        ),
    )

    technical_status_reason = models.TextField(
        blank=True,
        verbose_name="Motivo del estado técnico",
        help_text=(
            "Es obligatorio cuando el equipo tiene problemas "
            "o se destina a partes."
        ),
    )

    commercial_status_reason = models.TextField(
        blank=True,
        verbose_name="Motivo del estado comercial",
    )

    warehouse_location = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
        verbose_name="Ubicación actual",
        help_text=(
            "Almacén, zona, nivel, pasillo, taller u otra "
            "ubicación interna."
        ),
    )

    position_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Referencia de ubicación",
        help_text=(
            "Fila, estante, espacio, zona u otra referencia "
            "para ubicar físicamente el equipo."
        ),
    )

    initial_total_meter = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Contador total de ingreso",
    )

    initial_black_meter = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Contador B/N de ingreso",
    )

    initial_color_meter = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Contador color de ingreso",
    )

    initial_scan_meter = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Contador de escaneo de ingreso",
    )

    current_total_meter = models.PositiveBigIntegerField(
        default=0,
        db_index=True,
        verbose_name="Contador total actual",
    )

    current_black_meter = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Contador B/N actual",
    )

    current_color_meter = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Contador color actual",
    )

    current_scan_meter = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Contador de escaneo actual",
    )

    last_meter_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de última lectura",
    )

    last_meter_source = models.CharField(
        max_length=20,
        choices=MeterSource.choices,
        default=MeterSource.MANUAL,
        verbose_name="Fuente de última lectura",
    )

    hostname = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Nombre de red",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        protocol="both",
        unpack_ipv4=True,
        db_index=True,
        verbose_name="Dirección IP",
    )

    mac_address = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Dirección MAC",
    )

    asset_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Código patrimonial",
    )

    firmware_version = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Versión de firmware",
    )

    main_photo = models.ImageField(
        upload_to=equipment_photo_path,
        null=True,
        blank=True,
        verbose_name="Fotografía principal",
    )

    accessories_description = models.TextField(
        blank=True,
        verbose_name="Configuración recibida",
        help_text=(
            "Descripción inicial de accesorios recibidos. "
            "Posteriormente los accesorios se controlarán mediante "
            "inventario serializado independiente."
        ),
    )

    unloading_observations = models.TextField(
        blank=True,
        verbose_name="Observaciones de descarga",
    )

    technical_notes = models.TextField(
        blank=True,
        verbose_name="Notas técnicas",
    )

    commercial_notes = models.TextField(
        blank=True,
        verbose_name="Notas comerciales",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones generales",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activo",
    )

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = (
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "technical_status",
                    "commercial_status",
                ],
                name="equip_technical_commercial_idx",
            ),
            models.Index(
                fields=[
                    "is_available",
                    "is_active",
                ],
                name="equip_available_active_idx",
            ),
            models.Index(
                fields=[
                    "equipment_model",
                    "technical_status",
                ],
                name="equip_model_technical_idx",
            ),
            models.Index(
                fields=[
                    "customer",
                    "commercial_status",
                ],
                name="equip_customer_commercial_idx",
            ),
            models.Index(
                fields=[
                    "import_batch",
                    "unloading_date",
                ],
                name="equip_batch_unloading_idx",
            ),
            models.Index(
                fields=[
                    "warehouse_location",
                    "is_available",
                ],
                name="equip_location_available_idx",
            ),
        ]

    def __str__(self):
        model_name = ""

        if self.equipment_model_id:
            model_name = str(
                self.equipment_model
            ).strip()

        if model_name:
            return (
                f"{model_name} - "
                f"{self.serial_number}"
            )

        return self.serial_number

    @classmethod
    def generate_internal_code(cls):
        """
        Genera un código interno correlativo por año.

        Ejemplo:

        EQ-2026-000001
        """

        year = timezone.localdate().year
        prefix = f"EQ-{year}-"

        last_code = (
            cls.objects.filter(
                internal_code__startswith=prefix,
            )
            .order_by(
                "-internal_code",
            )
            .values_list(
                "internal_code",
                flat=True,
            )
            .first()
        )

        next_number = 1

        if last_code:
            try:
                next_number = (
                    int(
                        last_code.replace(
                            prefix,
                            "",
                            1,
                        )
                    )
                    + 1
                )
            except (
                TypeError,
                ValueError,
            ):
                next_number = 1

        while True:
            internal_code = (
                f"{prefix}"
                f"{next_number:06d}"
            )

            if not cls.objects.filter(
                internal_code=internal_code,
            ).exists():
                return internal_code

            next_number += 1

    def calculate_availability(self):
        """
        Determina automáticamente la disponibilidad comercial.

        Los estados Sin revisar, Para revisión, En revisión y
        Finalizada pueden seguir disponibles para ventas.

        El equipo no está disponible cuando:

        - Está archivado o inactivo.
        - Tiene problemas o está destinado a partes.
        - Tiene cliente o sucursal asignados.
        - Está separado, vendido, entregado o fuera del almacén.
        """

        unavailable_technical_statuses = {
            self.TechnicalStatus.WITH_PROBLEMS,
            self.TechnicalStatus.FOR_PARTS,
        }

        unavailable_commercial_statuses = {
            self.CommercialStatus.RESERVED,
            self.CommercialStatus.SOLD,
            self.CommercialStatus.DELIVERY_PREPARATION,
            self.CommercialStatus.IN_TRANSIT,
            self.CommercialStatus.DELIVERED,
            self.CommercialStatus.CONTRACT_ASSIGNED,
            self.CommercialStatus.INSTALLED,
            self.CommercialStatus.RETURN_PROCESS,
            self.CommercialStatus.TEMPORARY_LOAN,
            self.CommercialStatus.DEMONSTRATION,
            self.CommercialStatus.REPLACEMENT,
            self.CommercialStatus.OUT_OF_SERVICE,
            self.CommercialStatus.DISPOSED,
        }

        if self.archived_at is not None:
            return False

        if not self.is_active:
            return False

        if (
            self.technical_status
            in unavailable_technical_statuses
        ):
            return False

        if (
            self.commercial_status
            in unavailable_commercial_statuses
        ):
            return False

        if self.customer_id:
            return False

        if self.customer_branch_id:
            return False

        return True

    def clean(self):
        """
        Normaliza y valida la información del equipo.
        """

        super().clean()

        text_fields = [
            "internal_code",
            "serial_number",
            "import_reference",
            "purchase_invoice_number",
            "sale_invoice_number",
            "technical_status_reason",
            "commercial_status_reason",
            "warehouse_location",
            "position_reference",
            "hostname",
            "mac_address",
            "asset_number",
            "firmware_version",
            "accessories_description",
            "unloading_observations",
            "technical_notes",
            "commercial_notes",
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
                str(
                    value or ""
                ).strip(),
            )

        self.internal_code = self.internal_code.upper()
        self.serial_number = self.serial_number.upper()
        self.mac_address = self.mac_address.upper()
        self.asset_number = self.asset_number.upper()

        if not self.internal_code:
            raise ValidationError(
                {
                    "internal_code": (
                        "El código interno del equipo es obligatorio."
                    ),
                }
            )

        if not self.serial_number:
            raise ValidationError(
                {
                    "serial_number": (
                        "El número de serie del equipo es obligatorio."
                    ),
                }
            )

        if not self.equipment_model_id:
            raise ValidationError(
                {
                    "equipment_model": (
                        "El modelo del equipo es obligatorio."
                    ),
                }
            )

        duplicate_code = Equipment.objects.filter(
            internal_code__iexact=self.internal_code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "internal_code": (
                        "Ya existe un equipo registrado con este "
                        "código interno."
                    ),
                }
            )

        duplicate_serial = Equipment.objects.filter(
            serial_number__iexact=self.serial_number,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_serial.exists():
            raise ValidationError(
                {
                    "serial_number": (
                        "Ya existe un equipo registrado con este "
                        "número de serie."
                    ),
                }
            )

        warehouse_statuses = {
            self.CommercialStatus.WAREHOUSE,
            self.CommercialStatus.RETURNED,
        }

        if (
            self.customer_id
            and self.commercial_status in warehouse_statuses
        ):
            self.commercial_status = (
                self.CommercialStatus.RESERVED
            )

            if not self.reservation_date:
                self.reservation_date = timezone.now()

        if (
            not self.customer_id
            and self.commercial_status
            == self.CommercialStatus.RESERVED
        ):
            self.commercial_status = (
                self.CommercialStatus.WAREHOUSE
            )
            self.customer_branch = None
            self.advisor = None
            self.reservation_date = None
            self.reservation_expiration_date = None

        if (
            self.customer_branch_id
            and not self.customer_id
        ):
            raise ValidationError(
                {
                    "customer": (
                        "Debe seleccionar el cliente antes de "
                        "seleccionar una sucursal."
                    ),
                }
            )

        if (
            self.customer_branch_id
            and self.customer_id
            and self.customer_branch.partner_id != self.customer_id
        ):
            raise ValidationError(
                {
                    "customer_branch": (
                        "La sucursal seleccionada no pertenece "
                        "al cliente indicado."
                    ),
                }
            )

        external_ownership_types = {
            self.OwnershipType.CUSTOMER,
            self.OwnershipType.SUPPLIER,
            self.OwnershipType.THIRD_PARTY,
            self.OwnershipType.OTHER,
        }

        if (
            self.ownership_type in external_ownership_types
            and not self.owner_partner_id
        ):
            raise ValidationError(
                {
                    "owner_partner": (
                        "Debe indicar el propietario cuando el equipo "
                        "no pertenece a la empresa."
                    ),
                }
            )

        if (
            self.ownership_type == self.OwnershipType.OWN
            and self.owner_partner_id
        ):
            raise ValidationError(
                {
                    "owner_partner": (
                        "Un equipo propio no debe tener un propietario "
                        "externo."
                    ),
                }
            )

        statuses_requiring_customer = {
            self.CommercialStatus.RESERVED,
            self.CommercialStatus.SOLD,
            self.CommercialStatus.DELIVERY_PREPARATION,
            self.CommercialStatus.IN_TRANSIT,
            self.CommercialStatus.DELIVERED,
            self.CommercialStatus.CONTRACT_ASSIGNED,
            self.CommercialStatus.INSTALLED,
            self.CommercialStatus.TEMPORARY_LOAN,
            self.CommercialStatus.DEMONSTRATION,
            self.CommercialStatus.REPLACEMENT,
        }

        if (
            self.commercial_status in statuses_requiring_customer
            and not self.customer_id
        ):
            raise ValidationError(
                {
                    "customer": (
                        "El estado comercial seleccionado requiere "
                        "un cliente."
                    ),
                }
            )

        if (
            self.commercial_status == self.CommercialStatus.RESERVED
            and not self.reservation_date
        ):
            raise ValidationError(
                {
                    "reservation_date": (
                        "Una máquina separada debe registrar la fecha "
                        "de separación."
                    ),
                }
            )

        if (
            self.reservation_expiration_date
            and not self.reservation_date
        ):
            raise ValidationError(
                {
                    "reservation_date": (
                        "Debe registrar la fecha de separación antes "
                        "de indicar su vencimiento."
                    ),
                }
            )

        if (
            self.reservation_date
            and self.reservation_expiration_date
            and self.reservation_expiration_date
            < self.reservation_date
        ):
            raise ValidationError(
                {
                    "reservation_expiration_date": (
                        "El vencimiento de la separación no puede ser "
                        "anterior a la fecha de separación."
                    ),
                }
            )

        sold_statuses = {
            self.CommercialStatus.SOLD,
            self.CommercialStatus.DELIVERY_PREPARATION,
            self.CommercialStatus.IN_TRANSIT,
            self.CommercialStatus.DELIVERED,
        }

        if (
            self.commercial_status in sold_statuses
            and not self.sale_date
        ):
            raise ValidationError(
                {
                    "sale_date": (
                        "Una máquina vendida o en proceso de entrega "
                        "debe registrar la fecha de venta."
                    ),
                }
            )

        if (
            self.commercial_status == self.CommercialStatus.DELIVERED
            and not self.delivery_date
        ):
            raise ValidationError(
                {
                    "delivery_date": (
                        "Una máquina entregada debe registrar la "
                        "fecha real de entrega."
                    ),
                }
            )

        if (
            self.sale_invoice_date
            and self.sale_date
            and self.sale_invoice_date < self.sale_date
        ):
            raise ValidationError(
                {
                    "sale_invoice_date": (
                        "La fecha de factura de venta no puede ser "
                        "anterior a la fecha de venta."
                    ),
                }
            )

        if (
            self.purchase_invoice_date
            and self.purchase_date
            and self.purchase_invoice_date > self.purchase_date
        ):
            raise ValidationError(
                {
                    "purchase_invoice_date": (
                        "La fecha de factura de compra no puede ser "
                        "posterior a la fecha de compra."
                    ),
                }
            )

        problem_statuses = {
            self.TechnicalStatus.WITH_PROBLEMS,
            self.TechnicalStatus.FOR_PARTS,
        }

        if (
            self.technical_status in problem_statuses
            and not self.technical_status_reason
        ):
            raise ValidationError(
                {
                    "technical_status_reason": (
                        "Debe indicar el motivo cuando el equipo tiene "
                        "problemas o se destina a partes."
                    ),
                }
            )

        if (
            self.current_total_meter
            < self.initial_total_meter
        ):
            raise ValidationError(
                {
                    "current_total_meter": (
                        "El contador total actual no puede ser menor "
                        "que el contador total de ingreso."
                    ),
                }
            )

        if (
            self.current_black_meter
            < self.initial_black_meter
        ):
            raise ValidationError(
                {
                    "current_black_meter": (
                        "El contador B/N actual no puede ser menor "
                        "que el contador B/N de ingreso."
                    ),
                }
            )

        if (
            self.current_color_meter
            < self.initial_color_meter
        ):
            raise ValidationError(
                {
                    "current_color_meter": (
                        "El contador color actual no puede ser menor "
                        "que el contador color de ingreso."
                    ),
                }
            )

        if (
            self.current_scan_meter
            < self.initial_scan_meter
        ):
            raise ValidationError(
                {
                    "current_scan_meter": (
                        "El contador de escaneo actual no puede ser "
                        "menor que el contador de ingreso."
                    ),
                }
            )

        if self.equipment_model_id:
            if (
                self.equipment_model.color_mode
                == EquipmentModel.ColorMode.MONOCHROME
                and self.current_color_meter > 0
            ):
                raise ValidationError(
                    {
                        "current_color_meter": (
                            "Un equipo blanco y negro no puede tener "
                            "contador de color."
                        ),
                    }
                )

            if (
                not self.equipment_model.has_scan_meter
                and self.current_scan_meter > 0
            ):
                raise ValidationError(
                    {
                        "current_scan_meter": (
                            "El modelo seleccionado no utiliza "
                            "contador de escaneo."
                        ),
                    }
                )

        self.total_acquisition_cost = (
            Decimal(
                self.purchase_price or 0
            )
            + Decimal(
                self.allocated_import_cost or 0
            )
        )

        self.is_available = self.calculate_availability()

    def save(self, *args, **kwargs):
        """
        Normaliza, calcula disponibilidad y valida antes de guardar.
        """

        if self.pk:
            original_internal_code = (
                Equipment.objects.filter(
                    pk=self.pk,
                )
                .values_list(
                    "internal_code",
                    flat=True,
                )
                .first()
            )

            if original_internal_code:
                self.internal_code = (
                    original_internal_code
                )

        if not self.internal_code:
            self.internal_code = (
                self.generate_internal_code()
            )

        self.internal_code = str(
            self.internal_code or ""
        ).strip().upper()

        self.serial_number = str(
            self.serial_number or ""
        ).strip().upper()

        self.mac_address = str(
            self.mac_address or ""
        ).strip().upper()

        self.asset_number = str(
            self.asset_number or ""
        ).strip().upper()

        self.total_acquisition_cost = (
            Decimal(
                self.purchase_price or 0
            )
            + Decimal(
                self.allocated_import_cost or 0
            )
        )

        self.is_available = self.calculate_availability()

        self.full_clean()

        update_fields = kwargs.get(
            "update_fields"
        )

        if update_fields is not None:
            update_fields = set(
                update_fields
            )

            update_fields.update(
                {
                    "total_acquisition_cost",
                    "is_available",
                }
            )

            kwargs["update_fields"] = list(
                update_fields
            )

        return super().save(
            *args,
            **kwargs,
        )

    def register_initial_meters_as_current(self):
        """
        Copia los contadores iniciales como contadores actuales.

        Se utilizará al registrar por primera vez una máquina
        durante la descarga.
        """

        self.current_total_meter = self.initial_total_meter
        self.current_black_meter = self.initial_black_meter
        self.current_color_meter = self.initial_color_meter
        self.current_scan_meter = self.initial_scan_meter
        self.last_meter_date = timezone.now()
        self.last_meter_source = self.MeterSource.DOWNLOAD

    def archive(
        self,
        user=None,
        reason="",
        save=True,
    ):
        """
        Archiva el equipo, lo desactiva y lo marca como no disponible.
        """

        self.is_active = False
        self.is_available = False

        if not save:
            return super().archive(
                user=user,
                reason=reason,
                save=False,
            )

        self.archived_at = timezone.now()
        self.archived_by = user
        self.archived_reason = str(
            reason or ""
        ).strip()

        if user:
            self.updated_by = user

        self.save(
            update_fields=[
                "is_active",
                "is_available",
                "archived_at",
                "archived_by",
                "archived_reason",
                "updated_by",
                "updated_at",
            ]
        )

        return self

    def restore(
        self,
        user=None,
        save=True,
    ):
        """
        Restaura el equipo y recalcula su disponibilidad.
        """

        self.archived_at = None
        self.archived_by = None
        self.archived_reason = ""
        self.is_active = True

        if user:
            self.updated_by = user

        self.is_available = self.calculate_availability()

        if not save:
            return self

        self.save(
            update_fields=[
                "archived_at",
                "archived_by",
                "archived_reason",
                "is_active",
                "is_available",
                "updated_by",
                "updated_at",
            ]
        )

        return self