# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import EquipmentBaseModel
from .equipment import Equipment


class EquipmentMovement(EquipmentBaseModel):
    """
    Registra el historial operativo, físico, técnico y comercial
    de una máquina.

    Cada movimiento conserva información sobre:

    - Tipo de operación realizada.
    - Estado técnico anterior y nuevo.
    - Estado comercial anterior y nuevo.
    - Ubicación anterior y nueva.
    - Cliente y sucursal anteriores.
    - Cliente y sucursal nuevos.
    - Usuario responsable.
    - Fecha real del movimiento.
    - Documento o proceso que originó el cambio.

    Este historial permitirá conocer todo el recorrido de una máquina
    desde su descarga hasta su venta, entrega, instalación, retorno
    o baja.

    Los movimientos no sustituyen a los modelos especializados de:

    - Reparaciones.
    - Contratos.
    - Entregas.
    - Separaciones.
    - Lecturas de contadores.

    Solamente conservan la trazabilidad general del equipo.
    """

    class MovementType(models.TextChoices):
        REGISTRATION = (
            "registration",
            "Registro inicial",
        )
        UNLOADING = (
            "unloading",
            "Descarga",
        )
        WAREHOUSE_ENTRY = (
            "warehouse_entry",
            "Ingreso a almacén",
        )
        LOCATION_CHANGE = (
            "location_change",
            "Cambio de ubicación",
        )
        SENT_FOR_REVIEW = (
            "sent_for_review",
            "Envío para revisión",
        )
        REVIEW_STARTED = (
            "review_started",
            "Inicio de revisión",
        )
        REVIEW_COMPLETED = (
            "review_completed",
            "Revisión finalizada",
        )
        PROBLEM_REPORTED = (
            "problem_reported",
            "Problema reportado",
        )
        MARKED_FOR_PARTS = (
            "marked_for_parts",
            "Destinada a partes",
        )
        RESERVED = (
            "reserved",
            "Separación",
        )
        RESERVATION_RELEASED = (
            "reservation_released",
            "Liberación de separación",
        )
        SOLD = (
            "sold",
            "Venta",
        )
        DELIVERY_PREPARATION = (
            "delivery_preparation",
            "Preparación de entrega",
        )
        DISPATCHED = (
            "dispatched",
            "Salida para entrega",
        )
        DELIVERED = (
            "delivered",
            "Entrega",
        )
        CONTRACT_ASSIGNED = (
            "contract_assigned",
            "Asignación a contrato",
        )
        INSTALLED = (
            "installed",
            "Instalación",
        )
        REMOVAL_STARTED = (
            "removal_started",
            "Inicio de retiro",
        )
        REMOVED = (
            "removed",
            "Retiro",
        )
        RETURNED_TO_WAREHOUSE = (
            "returned_to_warehouse",
            "Retorno a almacén",
        )
        TEMPORARY_LOAN = (
            "temporary_loan",
            "Préstamo temporal",
        )
        DEMONSTRATION = (
            "demonstration",
            "Demostración",
        )
        REPLACEMENT_ASSIGNED = (
            "replacement_assigned",
            "Asignación como reemplazo",
        )
        SENT_TO_SUPPLIER = (
            "sent_to_supplier",
            "Envío a proveedor",
        )
        RECEIVED_FROM_SUPPLIER = (
            "received_from_supplier",
            "Recepción desde proveedor",
        )
        OWNERSHIP_CHANGE = (
            "ownership_change",
            "Cambio de propiedad",
        )
        OUT_OF_SERVICE = (
            "out_of_service",
            "Fuera de servicio",
        )
        REACTIVATED = (
            "reactivated",
            "Reactivación",
        )
        DISPOSED = (
            "disposed",
            "Baja del equipo",
        )
        ARCHIVED = (
            "archived",
            "Archivado",
        )
        RESTORED = (
            "restored",
            "Restaurado",
        )
        OTHER = (
            "other",
            "Otro movimiento",
        )

    class ReferenceType(models.TextChoices):
        MANUAL = (
            "manual",
            "Registro manual",
        )
        IMPORT_BATCH = (
            "import_batch",
            "Importación o lote",
        )
        DOWNLOAD = (
            "download",
            "Descarga",
        )
        RESERVATION = (
            "reservation",
            "Separación",
        )
        SALE = (
            "sale",
            "Venta",
        )
        DELIVERY = (
            "delivery",
            "Entrega",
        )
        CONTRACT = (
            "contract",
            "Contrato",
        )
        INSTALLATION = (
            "installation",
            "Instalación",
        )
        REMOVAL = (
            "removal",
            "Retiro",
        )
        REPAIR = (
            "repair",
            "Reparación",
        )
        TRANSFER = (
            "transfer",
            "Traslado",
        )
        MOBILE_APP = (
            "mobile_app",
            "Aplicación móvil",
        )
        SYSTEM = (
            "system",
            "Generado por el sistema",
        )
        OTHER = (
            "other",
            "Otro origen",
        )

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="movements",
        verbose_name="Equipo",
    )

    movement_type = models.CharField(
        max_length=40,
        choices=MovementType.choices,
        db_index=True,
        verbose_name="Tipo de movimiento",
    )

    occurred_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha y hora del movimiento",
        help_text=(
            "Fecha real en la que ocurrió la operación. "
            "Puede ser diferente de la fecha de creación del registro."
        ),
    )

    responsible_user = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="responsible_equipment_movements",
        verbose_name="Responsable del movimiento",
        help_text=(
            "Usuario que realizó o confirmó físicamente "
            "el movimiento."
        ),
    )

    previous_technical_status = models.CharField(
        max_length=30,
        choices=Equipment.TechnicalStatus.choices,
        blank=True,
        db_index=True,
        verbose_name="Estado técnico anterior",
    )

    new_technical_status = models.CharField(
        max_length=30,
        choices=Equipment.TechnicalStatus.choices,
        blank=True,
        db_index=True,
        verbose_name="Nuevo estado técnico",
    )

    previous_commercial_status = models.CharField(
        max_length=30,
        choices=Equipment.CommercialStatus.choices,
        blank=True,
        db_index=True,
        verbose_name="Estado comercial anterior",
    )

    new_commercial_status = models.CharField(
        max_length=30,
        choices=Equipment.CommercialStatus.choices,
        blank=True,
        db_index=True,
        verbose_name="Nuevo estado comercial",
    )

    previous_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ubicación anterior",
    )

    new_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nueva ubicación",
    )

    previous_position_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Referencia anterior de ubicación",
    )

    new_position_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nueva referencia de ubicación",
    )

    previous_customer = models.ForeignKey(
        "partners.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="previous_equipment_movements",
        verbose_name="Cliente anterior",
    )

    new_customer = models.ForeignKey(
        "partners.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="new_equipment_movements",
        verbose_name="Nuevo cliente",
    )

    previous_customer_branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="previous_equipment_movements",
        verbose_name="Sucursal anterior",
    )

    new_customer_branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="new_equipment_movements",
        verbose_name="Nueva sucursal",
    )

    previous_owner = models.ForeignKey(
        "partners.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="previous_owned_equipment_movements",
        verbose_name="Propietario anterior",
    )

    new_owner = models.ForeignKey(
        "partners.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="new_owned_equipment_movements",
        verbose_name="Nuevo propietario",
    )

    previous_advisor = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="previous_advisor_equipment_movements",
        verbose_name="Asesor anterior",
    )

    new_advisor = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="new_advisor_equipment_movements",
        verbose_name="Nuevo asesor",
    )

    reference_type = models.CharField(
        max_length=30,
        choices=ReferenceType.choices,
        default=ReferenceType.MANUAL,
        db_index=True,
        verbose_name="Origen del movimiento",
    )

    reference_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID del registro relacionado",
        help_text=(
            "UUID del contrato, reparación, entrega, separación "
            "u otro registro que originó el movimiento."
        ),
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Número de referencia",
        help_text=(
            "Número visible del documento o proceso relacionado. "
            "Ejemplo: REP-000125, CONT-000054 o GUIA-001256."
        ),
    )

    document_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Número de documento",
        help_text=(
            "Factura, guía de remisión, acta, orden, "
            "invoice u otro documento."
        ),
    )

    total_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador total",
        help_text=(
            "Contador total de la máquina al momento "
            "del movimiento."
        ),
    )

    black_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador blanco y negro",
    )

    color_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador color",
    )

    scan_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador de escaneo",
    )

    reason = models.TextField(
        blank=True,
        verbose_name="Motivo",
        help_text=(
            "Motivo que originó el movimiento o cambio de estado."
        ),
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    is_system_generated = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Generado automáticamente",
        help_text=(
            "Indica que el movimiento fue creado automáticamente "
            "por una operación del sistema."
        ),
    )

    class Meta:
        verbose_name = "Movimiento de equipo"
        verbose_name_plural = "Movimientos de equipos"
        ordering = (
            "-occurred_at",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "equipment",
                    "occurred_at",
                ],
                name="equip_move_equipment_date_idx",
            ),
            models.Index(
                fields=[
                    "equipment",
                    "movement_type",
                ],
                name="equip_move_equipment_type_idx",
            ),
            models.Index(
                fields=[
                    "movement_type",
                    "occurred_at",
                ],
                name="equip_move_type_date_idx",
            ),
            models.Index(
                fields=[
                    "reference_type",
                    "reference_id",
                ],
                name="equip_move_reference_idx",
            ),
            models.Index(
                fields=[
                    "new_customer",
                    "occurred_at",
                ],
                name="equip_move_customer_date_idx",
            ),
        ]

    def __str__(self):
        equipment_text = ""

        if self.equipment_id:
            equipment_text = str(
                self.equipment
            ).strip()

        movement_text = self.get_movement_type_display()

        if equipment_text:
            return (
                f"{movement_text} - "
                f"{equipment_text}"
            )

        return movement_text

    def clean(self):
        """
        Normaliza y valida el movimiento.
        """

        super().clean()

        text_fields = [
            "previous_location",
            "new_location",
            "previous_position_reference",
            "new_position_reference",
            "reference_number",
            "document_number",
            "reason",
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

        self.reference_number = self.reference_number.upper()
        self.document_number = self.document_number.upper()

        if not self.equipment_id:
            raise ValidationError(
                {
                    "equipment": (
                        "Debe seleccionar el equipo relacionado "
                        "con el movimiento."
                    ),
                }
            )

        if not self.movement_type:
            raise ValidationError(
                {
                    "movement_type": (
                        "Debe seleccionar el tipo de movimiento."
                    ),
                }
            )

        if not self.occurred_at:
            raise ValidationError(
                {
                    "occurred_at": (
                        "Debe registrar la fecha y hora "
                        "del movimiento."
                    ),
                }
            )

        if (
            self.previous_customer_branch_id
            and not self.previous_customer_id
        ):
            raise ValidationError(
                {
                    "previous_customer": (
                        "Debe indicar el cliente anterior cuando "
                        "se registra una sucursal anterior."
                    ),
                }
            )

        if (
            self.previous_customer_branch_id
            and self.previous_customer_id
            and self.previous_customer_branch.partner_id
            != self.previous_customer_id
        ):
            raise ValidationError(
                {
                    "previous_customer_branch": (
                        "La sucursal anterior no pertenece "
                        "al cliente anterior seleccionado."
                    ),
                }
            )

        if (
            self.new_customer_branch_id
            and not self.new_customer_id
        ):
            raise ValidationError(
                {
                    "new_customer": (
                        "Debe indicar el nuevo cliente cuando "
                        "se registra una nueva sucursal."
                    ),
                }
            )

        if (
            self.new_customer_branch_id
            and self.new_customer_id
            and self.new_customer_branch.partner_id
            != self.new_customer_id
        ):
            raise ValidationError(
                {
                    "new_customer_branch": (
                        "La nueva sucursal no pertenece "
                        "al nuevo cliente seleccionado."
                    ),
                }
            )

        movements_requiring_customer = {
            self.MovementType.RESERVED,
            self.MovementType.SOLD,
            self.MovementType.DELIVERY_PREPARATION,
            self.MovementType.DISPATCHED,
            self.MovementType.DELIVERED,
            self.MovementType.CONTRACT_ASSIGNED,
            self.MovementType.INSTALLED,
            self.MovementType.TEMPORARY_LOAN,
            self.MovementType.DEMONSTRATION,
            self.MovementType.REPLACEMENT_ASSIGNED,
        }

        if (
            self.movement_type in movements_requiring_customer
            and not self.new_customer_id
        ):
            raise ValidationError(
                {
                    "new_customer": (
                        "Este tipo de movimiento requiere indicar "
                        "el cliente relacionado."
                    ),
                }
            )

        movements_requiring_reason = {
            self.MovementType.PROBLEM_REPORTED,
            self.MovementType.MARKED_FOR_PARTS,
            self.MovementType.RESERVATION_RELEASED,
            self.MovementType.OWNERSHIP_CHANGE,
            self.MovementType.OUT_OF_SERVICE,
            self.MovementType.DISPOSED,
            self.MovementType.ARCHIVED,
            self.MovementType.OTHER,
        }

        if (
            self.movement_type in movements_requiring_reason
            and not self.reason
        ):
            raise ValidationError(
                {
                    "reason": (
                        "Debe indicar el motivo para este "
                        "tipo de movimiento."
                    ),
                }
            )

        if (
            self.reference_type == self.ReferenceType.SYSTEM
            and not self.is_system_generated
        ):
            raise ValidationError(
                {
                    "is_system_generated": (
                        "Un movimiento con origen sistema debe "
                        "marcarse como generado automáticamente."
                    ),
                }
            )

        if (
            self.previous_technical_status
            and self.new_technical_status
            and self.previous_technical_status
            == self.new_technical_status
        ):
            raise ValidationError(
                {
                    "new_technical_status": (
                        "El nuevo estado técnico debe ser diferente "
                        "del estado técnico anterior."
                    ),
                }
            )

        if (
            self.previous_commercial_status
            and self.new_commercial_status
            and self.previous_commercial_status
            == self.new_commercial_status
        ):
            raise ValidationError(
                {
                    "new_commercial_status": (
                        "El nuevo estado comercial debe ser diferente "
                        "del estado comercial anterior."
                    ),
                }
            )

        if self.equipment_id:
            if (
                self.total_meter is not None
                and self.total_meter
                < self.equipment.initial_total_meter
            ):
                raise ValidationError(
                    {
                        "total_meter": (
                            "El contador total del movimiento no puede "
                            "ser menor que el contador de ingreso."
                        ),
                    }
                )

            if (
                self.black_meter is not None
                and self.black_meter
                < self.equipment.initial_black_meter
            ):
                raise ValidationError(
                    {
                        "black_meter": (
                            "El contador blanco y negro del movimiento "
                            "no puede ser menor que el contador de ingreso."
                        ),
                    }
                )

            if (
                self.color_meter is not None
                and self.color_meter
                < self.equipment.initial_color_meter
            ):
                raise ValidationError(
                    {
                        "color_meter": (
                            "El contador color del movimiento no puede "
                            "ser menor que el contador de ingreso."
                        ),
                    }
                )

            if (
                self.scan_meter is not None
                and self.scan_meter
                < self.equipment.initial_scan_meter
            ):
                raise ValidationError(
                    {
                        "scan_meter": (
                            "El contador de escaneo del movimiento no "
                            "puede ser menor que el contador de ingreso."
                        ),
                    }
                )

    def save(self, *args, **kwargs):
        """
        Normaliza y valida el movimiento antes de guardarlo.
        """

        self.previous_location = str(
            self.previous_location or ""
        ).strip()

        self.new_location = str(
            self.new_location or ""
        ).strip()

        self.previous_position_reference = str(
            self.previous_position_reference or ""
        ).strip()

        self.new_position_reference = str(
            self.new_position_reference or ""
        ).strip()

        self.reference_number = str(
            self.reference_number or ""
        ).strip().upper()

        self.document_number = str(
            self.document_number or ""
        ).strip().upper()

        self.reason = str(
            self.reason or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )