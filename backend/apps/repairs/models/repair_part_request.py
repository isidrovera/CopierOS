# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RepairBaseModel
from .repair import Repair


class RepairPartRequest(RepairBaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        SUBMITTED = "submitted", "Enviada"
        IN_REVIEW = "in_review", "En revisión"
        PARTIALLY_APPROVED = "partially_approved", "Parcialmente aprobada"
        APPROVED = "approved", "Aprobada"
        PARTIALLY_ATTENDED = "partially_attended", "Parcialmente atendida"
        ATTENDED = "attended", "Atendida"
        REJECTED = "rejected", "Rechazada"
        CANCELLED = "cancelled", "Cancelada"
        CLOSED = "closed", "Cerrada"

    class Priority(models.TextChoices):
        LOW = "low", "Baja"
        NORMAL = "normal", "Normal"
        HIGH = "high", "Alta"
        URGENT = "urgent", "Urgente"
        CRITICAL = "critical", "Crítica"

    class ResponsibleArea(models.TextChoices):
        TECHNICAL = "technical", "Técnica"
        AREA_MANAGER = "area_manager", "Jefe de área"
        MANAGEMENT = "management", "Gerencia"
        WAREHOUSE = "warehouse", "Almacén"
        LOGISTICS = "logistics", "Logística"
        PURCHASING = "purchasing", "Compras"
        CLOSED = "closed", "Cerrada"

    repair = models.ForeignKey(
        Repair,
        on_delete=models.CASCADE,
        related_name="part_requests",
        verbose_name="Reparación",
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Código de solicitud",
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
    current_responsible_area = models.CharField(
        max_length=30,
        choices=ResponsibleArea.choices,
        default=ResponsibleArea.TECHNICAL,
        db_index=True,
        verbose_name="Área responsable actual",
    )
    current_responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="responsible_repair_part_requests",
        verbose_name="Responsable actual",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="repair_part_requests_created",
        verbose_name="Solicitado por",
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_part_requests_submitted",
        verbose_name="Enviado por",
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de envío",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_part_requests_approved",
        verbose_name="Aprobado por",
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de aprobación",
    )
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_part_requests_rejected",
        verbose_name="Rechazado por",
    )
    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de rechazo",
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de rechazo",
    )
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_part_requests_closed",
        verbose_name="Cerrado por",
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de cierre",
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Título",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )
    technical_justification = models.TextField(
        blank=True,
        verbose_name="Justificación técnica",
    )
    general_observations = models.TextField(
        blank=True,
        verbose_name="Observaciones generales",
    )
    requires_management_approval = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Requiere aprobación de gerencia",
    )
    has_pending_replacements = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Tiene reposiciones pendientes",
    )

    class Meta:
        verbose_name = "Solicitud de partes para reparación"
        verbose_name_plural = "Solicitudes de partes para reparaciones"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["repair", "status"], name="rep_part_req_status_idx"),
            models.Index(
                fields=["current_responsible_area", "status"],
                name="rep_part_req_area_idx",
            ),
            models.Index(
                fields=["requested_by", "created_at"],
                name="rep_part_req_user_idx",
            ),
            models.Index(
                fields=["priority", "status"],
                name="rep_part_req_priority_idx",
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.repair.code}"

    def clean(self):
        super().clean()
        self.code = str(self.code or "").strip().upper()
        self.title = str(self.title or "").strip()
        self.description = str(self.description or "").strip()
        self.technical_justification = str(
            self.technical_justification or ""
        ).strip()
        self.general_observations = str(
            self.general_observations or ""
        ).strip()
        self.rejection_reason = str(self.rejection_reason or "").strip()

        if not self.repair_id:
            raise ValidationError({"repair": "La reparación es obligatoria."})

        if not self.requested_by_id:
            raise ValidationError(
                {"requested_by": "El usuario solicitante es obligatorio."}
            )

        if self.status == self.Status.REJECTED and not self.rejection_reason:
            raise ValidationError(
                {"rejection_reason": "Debe indicar el motivo del rechazo."}
            )

        if self.status == self.Status.SUBMITTED and not self.submitted_at:
            self.submitted_at = timezone.now()

        if self.status in {
            self.Status.APPROVED,
            self.Status.PARTIALLY_APPROVED,
        } and not self.approved_at:
            self.approved_at = timezone.now()

        if self.status == self.Status.REJECTED and not self.rejected_at:
            self.rejected_at = timezone.now()

        if self.status == self.Status.CLOSED and not self.closed_at:
            self.closed_at = timezone.now()

    def save(self, *args, **kwargs):
        if not self.code:
            year = timezone.localdate().year
            prefix = f"RPR-{year}-"
            last_code = (
                RepairPartRequest.objects.filter(code__startswith=prefix)
                .order_by("-code")
                .values_list("code", flat=True)
                .first()
            )
            sequence = 1
            if last_code:
                try:
                    sequence = int(last_code.rsplit("-", 1)[-1]) + 1
                except (TypeError, ValueError):
                    sequence = 1
            self.code = f"{prefix}{sequence:06d}"

        self.full_clean()
        return super().save(*args, **kwargs)
