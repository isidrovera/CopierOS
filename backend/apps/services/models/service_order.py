# -*- coding: utf-8 -*-
import re
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import IntegrityError, models, transaction
from django.utils import timezone

from apps.equipment.models import Equipment

from .base import ServicesBaseModel


class ServiceOrder(ServicesBaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        PENDING_ASSIGNMENT = (
            "pending_assignment",
            "Pendiente de asignación",
        )
        ASSIGNED = "assigned", "Asignada"
        ACCEPTED = "accepted", "Aceptada por técnico"
        EN_ROUTE = "en_route", "Técnico en ruta"
        ON_SITE = "on_site", "Técnico en ubicación"
        IN_PROGRESS = "in_progress", "En proceso"
        PENDING_PARTS = (
            "pending_parts",
            "Pendiente de repuestos",
        )
        REQUIRES_RETURN = (
            "requires_return",
            "Requiere nueva visita",
        )
        TECHNICIAN_COMPLETED = (
            "technician_completed",
            "Finalizada por técnico",
        )
        PENDING_CONFORMITY = (
            "pending_conformity",
            "Pendiente de conformidad",
        )
        CLOSED = "closed", "Cerrada"
        RESCHEDULED = "rescheduled", "Reprogramada"
        FAILED_VISIT = (
            "failed_visit",
            "Visita no realizada",
        )
        CANCELLED = "cancelled", "Cancelada"

    class Priority(models.TextChoices):
        LOW = "low", "Baja"
        NORMAL = "normal", "Normal"
        HIGH = "high", "Alta"
        URGENT = "urgent", "Urgente"

    class ServiceOrigin(models.TextChoices):
        RENTAL = (
            "rental",
            "Alquiler Andes",
        )
        EXTERNAL = (
            "external",
            "Alquiler o equipo externo",
        )

    class ServiceType(models.TextChoices):
        PREVENTIVE = "preventive", "Preventivo"
        CORRECTIVE = "corrective", "Correctivo"
        NETWORK = "network", "Red y configuración"
        METER_READING = (
            "meter_reading",
            "Lectura de contadores",
        )
        INSPECTION = "inspection", "Inspección"
        OTHER = "other", "Otro"

    class Result(models.TextChoices):
        PENDING = "pending", "Pendiente"
        OPERATIONAL = "operational", "Operativa"
        OPERATIONAL_WITH_NOTES = (
            "operational_with_notes",
            "Operativa con observaciones",
        )
        PENDING_PARTS = (
            "pending_parts",
            "Pendiente de repuestos",
        )
        REQUIRES_RETURN = (
            "requires_return",
            "Requiere nueva visita",
        )
        NOT_REPAIRED = "not_repaired", "No reparada"
        NOT_ATTENDED = "not_attended", "No atendida"

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        blank=True,
        editable=False,
        verbose_name="Número de OS",
    )

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="service_orders",
        verbose_name="Equipo",
    )

    assigned_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="assigned_service_orders",
        verbose_name="Técnico responsable",
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_orders_assigned",
        verbose_name="Asignado por",
    )

    service_origin = models.CharField(
        max_length=20,
        choices=ServiceOrigin.choices,
        default=ServiceOrigin.RENTAL,
        db_index=True,
        verbose_name="Origen de la atención",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
        db_index=True,
        verbose_name="Prioridad",
    )

    service_type = models.CharField(
        max_length=40,
        choices=ServiceType.choices,
        default=ServiceType.CORRECTIVE,
        db_index=True,
        verbose_name="Tipo de servicio",
    )

    result = models.CharField(
        max_length=40,
        choices=Result.choices,
        default=Result.PENDING,
        db_index=True,
        verbose_name="Resultado",
    )

    requested_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de solicitud",
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha programada",
    )

    assigned_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de asignación",
    )

    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de aceptación",
    )

    route_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio de ruta",
    )

    arrived_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de llegada",
    )

    service_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio del servicio",
    )

    technician_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Finalización del técnico",
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de cierre",
    )

    equipment_internal_code = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Código interno histórico",
    )

    equipment_serial_number = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Serie histórica",
    )

    equipment_brand_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Marca histórica",
    )

    equipment_model_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Modelo histórico",
    )

    equipment_family_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Familia histórica",
    )

    customer_code = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Código del cliente",
    )

    customer_document_type = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Tipo de documento",
    )

    customer_document_number = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Número de documento",
    )

    customer_name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name="Cliente histórico",
    )

    customer_trade_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre comercial",
    )

    branch_name = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
        verbose_name="Sede histórica",
    )

    address = models.TextField(
        verbose_name="Dirección histórica",
    )

    address_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Referencia de dirección",
    )

    district = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Distrito",
    )

    province = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Provincia",
    )

    region = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Región",
    )

    destination_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("-90")),
            MaxValueValidator(Decimal("90")),
        ],
        verbose_name="Latitud del destino",
    )

    destination_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("-180")),
            MaxValueValidator(Decimal("180")),
        ],
        verbose_name="Longitud del destino",
    )

    geofence_radius_meters = models.PositiveIntegerField(
        default=150,
        verbose_name="Radio de geocerca",
    )

    site_location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Ubicación dentro de la sede",
    )

    contact_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Contacto histórico",
    )

    contact_job_title = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Cargo del contacto",
    )

    contact_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Teléfono del contacto",
    )

    contact_email = models.EmailField(
        blank=True,
        verbose_name="Correo del contacto",
    )

    contract_reference = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Referencia del contrato",
    )

    rental_assignment_reference = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Referencia de asignación",
    )

    reported_problem = models.TextField(
        verbose_name="Problema reportado",
    )

    diagnosis = models.TextField(
        blank=True,
        verbose_name="Diagnóstico",
    )

    work_performed = models.TextField(
        blank=True,
        verbose_name="Trabajo realizado",
    )

    technician_observations = models.TextField(
        blank=True,
        verbose_name="Observaciones del técnico",
    )

    closure_observations = models.TextField(
        blank=True,
        verbose_name="Observaciones de cierre",
    )

    requires_return_visit = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere nueva visita",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    failed_visit_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de visita no realizada",
    )

    class Meta:
        verbose_name = "Orden de servicio"
        verbose_name_plural = "Órdenes de servicio"
        ordering = (
            "-requested_at",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "equipment",
                    "status",
                ],
                name="svc_order_equip_st_idx",
            ),
            models.Index(
                fields=[
                    "assigned_technician",
                    "status",
                ],
                name="svc_order_tech_st_idx",
            ),
            models.Index(
                fields=[
                    "scheduled_at",
                    "status",
                ],
                name="svc_order_sched_st_idx",
            ),
            models.Index(
                fields=[
                    "customer_name",
                    "status",
                ],
                name="svc_order_cust_st_idx",
            ),
            models.Index(
                fields=[
                    "service_origin",
                    "status",
                ],
                name="svc_order_origin_st_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.code} - "
            f"{self.equipment_serial_number}"
        )

    @classmethod
    def _get_next_code(cls, year):
        prefix = f"OS-{year}-"

        latest_code = (
            cls.objects
            .select_for_update()
            .filter(
                code__startswith=prefix,
            )
            .order_by("-code")
            .values_list(
                "code",
                flat=True,
            )
            .first()
        )

        next_number = 1

        if latest_code:
            match = re.search(
                r"(\d+)$",
                latest_code,
            )

            if match:
                next_number = (
                    int(match.group(1)) + 1
                )

        return (
            f"{prefix}"
            f"{next_number:06d}"
        )

    def _get_code_year(self):
        reference_date = (
            self.requested_at
            or timezone.now()
        )

        if timezone.is_aware(reference_date):
            reference_date = timezone.localtime(
                reference_date
            )

        return reference_date.year

    def _normalize_text_fields(self):
        text_fields = (
            "code",
            "equipment_internal_code",
            "equipment_serial_number",
            "equipment_brand_name",
            "equipment_model_name",
            "equipment_family_name",
            "customer_code",
            "customer_document_type",
            "customer_document_number",
            "customer_name",
            "customer_trade_name",
            "branch_name",
            "address",
            "address_reference",
            "district",
            "province",
            "region",
            "site_location",
            "contact_name",
            "contact_job_title",
            "contact_phone",
            "contact_email",
            "contract_reference",
            "rental_assignment_reference",
            "reported_problem",
            "diagnosis",
            "work_performed",
            "technician_observations",
            "closure_observations",
            "cancellation_reason",
            "failed_visit_reason",
        )

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

        self.code = self.code.upper()
        self.equipment_serial_number = (
            self.equipment_serial_number.upper()
        )

    def _load_equipment_snapshot(self):
        if not self.equipment_id:
            return

        equipment = self.equipment
        equipment_model = equipment.equipment_model

        if not self.equipment_internal_code:
            self.equipment_internal_code = (
                equipment.internal_code
            )

        if not self.equipment_serial_number:
            self.equipment_serial_number = (
                equipment.serial_number
            )

        if not self.equipment_model_name:
            self.equipment_model_name = str(
                equipment_model
            )

        if (
            not self.equipment_brand_name
            and equipment_model.brand_id
        ):
            self.equipment_brand_name = str(
                equipment_model.brand
            )

        if not self.equipment_family_name:
            equipment_family = getattr(
                equipment_model,
                "equipment_family",
                None,
            )

            if equipment_family:
                self.equipment_family_name = str(
                    equipment_family
                )
            else:
                self.equipment_family_name = str(
                    getattr(
                        equipment_model,
                        "family",
                        "",
                    )
                    or ""
                ).strip()

    def clean(self):
        super().clean()

        self._normalize_text_fields()

        if not self.equipment_id:
            raise ValidationError(
                {
                    "equipment": (
                        "La máquina es obligatoria."
                    )
                }
            )

        if self.service_origin not in dict(
            self.ServiceOrigin.choices
        ):
            raise ValidationError(
                {
                    "service_origin": (
                        "El origen de la atención "
                        "no es válido."
                    )
                }
            )

        if not self.equipment_serial_number:
            raise ValidationError(
                {
                    "equipment_serial_number": (
                        "La serie histórica es obligatoria."
                    )
                }
            )

        if not self.customer_name:
            raise ValidationError(
                {
                    "customer_name": (
                        "El cliente histórico es obligatorio."
                    )
                }
            )

        if not self.address:
            raise ValidationError(
                {
                    "address": (
                        "La dirección histórica es obligatoria."
                    )
                }
            )

        if not self.reported_problem:
            raise ValidationError(
                {
                    "reported_problem": (
                        "El problema reportado es obligatorio."
                    )
                }
            )

        requires_technician = (
            self.status
            not in {
                self.Status.DRAFT,
                self.Status.PENDING_ASSIGNMENT,
                self.Status.CANCELLED,
            }
        )

        if (
            requires_technician
            and not self.assigned_technician_id
        ):
            raise ValidationError(
                {
                    "assigned_technician": (
                        "La OS requiere un técnico."
                    )
                }
            )

        if (
            self.assigned_technician_id
            and not self.assigned_at
        ):
            raise ValidationError(
                {
                    "assigned_at": (
                        "Debe registrar la fecha "
                        "de asignación."
                    )
                }
            )

        if (
            self.status == self.Status.CANCELLED
            and not self.cancellation_reason
        ):
            raise ValidationError(
                {
                    "cancellation_reason": (
                        "Debe indicar el motivo."
                    )
                }
            )

        if (
            self.status == self.Status.FAILED_VISIT
            and not self.failed_visit_reason
        ):
            raise ValidationError(
                {
                    "failed_visit_reason": (
                        "Debe indicar el motivo."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self._load_equipment_snapshot()

        if (
            self.assigned_technician_id
            and not self.assigned_at
        ):
            self.assigned_at = timezone.now()

        if self.code:
            self.full_clean()

            return super().save(
                *args,
                **kwargs,
            )

        code_year = self._get_code_year()

        for attempt in range(5):
            try:
                with transaction.atomic():
                    self.code = self._get_next_code(
                        code_year
                    )

                    self.full_clean()

                    return super().save(
                        *args,
                        **kwargs,
                    )

            except IntegrityError:
                duplicated_code = (
                    self.__class__.objects
                    .filter(
                        code=self.code,
                    )
                    .exists()
                )

                if not duplicated_code:
                    raise

                self.code = ""

                if attempt == 4:
                    raise ValidationError(
                        {
                            "code": (
                                "No se pudo generar "
                                "el número de OS. "
                                "Intenta nuevamente."
                            )
                        }
                    )