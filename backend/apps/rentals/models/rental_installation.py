# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RentalsBaseModel
from .rental_assignment import RentalAssignment


class RentalInstallation(RentalsBaseModel):
    """
    Instalación de un equipo alquilado por ANDES.

    Registra:

    - Asignación relacionada.
    - Técnico responsable.
    - Programación.
    - Inicio y finalización.
    - Ubicación dentro de la sede.
    - Configuración de red.
    - Contadores registrados durante la instalación.
    - Resultado de las pruebas.
    - Observaciones.
    - Conformidad del cliente.

    Las evidencias fotográficas y lecturas históricas se manejarán
    posteriormente desde sus modelos especializados.
    """

    class Status(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        SCHEDULED = (
            "scheduled",
            "Programada",
        )
        ASSIGNED = (
            "assigned",
            "Técnico asignado",
        )
        IN_TRANSIT = (
            "in_transit",
            "En traslado",
        )
        IN_PROGRESS = (
            "in_progress",
            "En instalación",
        )
        COMPLETED = (
            "completed",
            "Finalizada",
        )
        OBSERVED = (
            "observed",
            "Observada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )

    class Result(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        INSTALLED = (
            "installed",
            "Instalada correctamente",
        )
        INSTALLED_WITH_OBSERVATIONS = (
            "installed_with_observations",
            "Instalada con observaciones",
        )
        NOT_INSTALLED = (
            "not_installed",
            "No instalada",
        )
        REQUIRES_TECHNICAL_REVIEW = (
            "requires_technical_review",
            "Requiere revisión técnica",
        )
        REQUIRES_REPLACEMENT = (
            "requires_replacement",
            "Requiere reemplazo",
        )

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código de instalación",
    )

    rental_assignment = models.ForeignKey(
        RentalAssignment,
        on_delete=models.PROTECT,
        related_name="installations",
        verbose_name="Asignación de alquiler",
    )

    assigned_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rental_installations_assigned",
        verbose_name="Técnico asignado",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
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

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Inicio de instalación",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fin de instalación",
    )

    site_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ubicación dentro de la sede",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP",
    )

    hostname = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nombre de red",
    )

    network_notes = models.TextField(
        blank=True,
        verbose_name="Configuración de red",
    )

    driver_installed = models.BooleanField(
        default=False,
        verbose_name="Driver instalado",
    )

    printing_test_passed = models.BooleanField(
        default=False,
        verbose_name="Prueba de impresión aprobada",
    )

    copying_test_passed = models.BooleanField(
        default=False,
        verbose_name="Prueba de copia aprobada",
    )

    scanning_test_passed = models.BooleanField(
        default=False,
        verbose_name="Prueba de escaneo aprobada",
    )

    duplex_test_passed = models.BooleanField(
        default=False,
        verbose_name="Prueba dúplex aprobada",
    )

    adf_test_passed = models.BooleanField(
        default=False,
        verbose_name="Prueba de ADF aprobada",
    )

    initial_total_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador total inicial",
    )

    initial_black_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador blanco y negro inicial",
    )

    initial_color_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador color inicial",
    )

    customer_representative_name = models.CharField(
        max_length=180,
        blank=True,
        verbose_name="Representante del cliente",
    )

    customer_conformity = models.BooleanField(
        default=False,
        verbose_name="Conformidad del cliente",
    )

    technical_observations = models.TextField(
        blank=True,
        verbose_name="Observaciones técnicas",
    )

    customer_observations = models.TextField(
        blank=True,
        verbose_name="Observaciones del cliente",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    class Meta:
        verbose_name = "Instalación de equipo alquilado"
        verbose_name_plural = "Instalaciones de equipos alquilados"
        ordering = (
            "-requested_at",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "rental_assignment",
                    "status",
                ],
                name="rent_install_assign_status_idx",
            ),
            models.Index(
                fields=[
                    "assigned_technician",
                    "status",
                ],
                name="rent_install_tech_status_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "scheduled_at",
                ],
                name="rent_install_status_date_idx",
            ),
            models.Index(
                fields=[
                    "result",
                    "completed_at",
                ],
                name="rent_install_result_date_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.code} - "
            f"{self.rental_assignment.rental_equipment}"
        )

    def clean(self):
        super().clean()

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.site_location = str(
            self.site_location or ""
        ).strip()

        self.hostname = str(
            self.hostname or ""
        ).strip()

        self.network_notes = str(
            self.network_notes or ""
        ).strip()

        self.customer_representative_name = str(
            self.customer_representative_name or ""
        ).strip()

        self.technical_observations = str(
            self.technical_observations or ""
        ).strip()

        self.customer_observations = str(
            self.customer_observations or ""
        ).strip()

        self.cancellation_reason = str(
            self.cancellation_reason or ""
        ).strip()

        if not self.code:
            raise ValidationError(
                {
                    "code": (
                        "El código de instalación es obligatorio."
                    ),
                }
            )

        if not self.rental_assignment_id:
            raise ValidationError(
                {
                    "rental_assignment": (
                        "La asignación de alquiler es obligatoria."
                    ),
                }
            )

        duplicate_code = RentalInstallation.objects.filter(
            code__iexact=self.code,
        ).exclude(
            pk=self.pk,
        )

        if duplicate_code.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe una instalación registrada "
                        "con este código."
                    ),
                }
            )

        allowed_assignment_statuses = [
            RentalAssignment.Status.RESERVED,
            RentalAssignment.Status.INSTALLATION_PENDING,
            RentalAssignment.Status.INSTALLED,
            RentalAssignment.Status.ACTIVE,
        ]

        if (
            self.rental_assignment_id
            and self.rental_assignment.status
            not in allowed_assignment_statuses
        ):
            raise ValidationError(
                {
                    "rental_assignment": (
                        "La asignación seleccionada no se encuentra "
                        "disponible para instalación."
                    ),
                }
            )

        if self.status in [
            self.Status.ASSIGNED,
            self.Status.IN_TRANSIT,
            self.Status.IN_PROGRESS,
            self.Status.COMPLETED,
            self.Status.OBSERVED,
        ]:
            if not self.assigned_technician_id:
                raise ValidationError(
                    {
                        "assigned_technician": (
                            "Debe asignar un técnico."
                        ),
                    }
                )

        if self.status == self.Status.IN_PROGRESS:
            if not self.started_at:
                self.started_at = timezone.now()

        if self.status == self.Status.COMPLETED:
            if self.result == self.Result.PENDING:
                raise ValidationError(
                    {
                        "result": (
                            "Debe indicar el resultado "
                            "de la instalación."
                        ),
                    }
                )

            if not self.started_at:
                raise ValidationError(
                    {
                        "started_at": (
                            "Debe iniciar la instalación antes "
                            "de finalizarla."
                        ),
                    }
                )

            if not self.completed_at:
                self.completed_at = timezone.now()

        if self.status == self.Status.CANCELLED:
            if not self.cancellation_reason:
                raise ValidationError(
                    {
                        "cancellation_reason": (
                            "Debe indicar el motivo de cancelación."
                        ),
                    }
                )

        if (
            self.started_at
            and self.completed_at
            and self.completed_at < self.started_at
        ):
            raise ValidationError(
                {
                    "completed_at": (
                        "La fecha de finalización no puede ser "
                        "anterior al inicio."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        self.code = str(
            self.code or ""
        ).strip().upper()

        self.site_location = str(
            self.site_location or ""
        ).strip()

        self.hostname = str(
            self.hostname or ""
        ).strip()

        self.network_notes = str(
            self.network_notes or ""
        ).strip()

        self.customer_representative_name = str(
            self.customer_representative_name or ""
        ).strip()

        self.technical_observations = str(
            self.technical_observations or ""
        ).strip()

        self.customer_observations = str(
            self.customer_observations or ""
        ).strip()

        self.cancellation_reason = str(
            self.cancellation_reason or ""
        ).strip()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )