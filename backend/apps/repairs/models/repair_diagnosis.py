# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RepairBaseModel
from .repair import Repair


class RepairDiagnosis(RepairBaseModel):
    """
    Diagnóstico técnico realizado durante una reparación.

    Permite registrar varios diagnósticos en una misma reparación,
    conservando el historial de revisiones y dejando uno como
    diagnóstico principal o definitivo.
    """

    class DiagnosisType(models.TextChoices):
        INITIAL = (
            "initial",
            "Diagnóstico inicial",
        )
        PRELIMINARY = (
            "preliminary",
            "Diagnóstico preliminar",
        )
        TECHNICAL = (
            "technical",
            "Diagnóstico técnico",
        )
        FINAL = (
            "final",
            "Diagnóstico final",
        )
        SECOND_OPINION = (
            "second_opinion",
            "Segunda opinión",
        )

    class Severity(models.TextChoices):
        LOW = (
            "low",
            "Baja",
        )
        MEDIUM = (
            "medium",
            "Media",
        )
        HIGH = (
            "high",
            "Alta",
        )
        CRITICAL = (
            "critical",
            "Crítica",
        )

    class Repairability(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente de determinar",
        )
        REPAIRABLE = (
            "repairable",
            "Reparable",
        )
        REPAIRABLE_WITH_PARTS = (
            "repairable_with_parts",
            "Reparable con repuestos",
        )
        REPAIRABLE_WITH_EXTERNAL_SERVICE = (
            "repairable_external",
            "Reparable con servicio externo",
        )
        NOT_REPAIRABLE = (
            "not_repairable",
            "No reparable",
        )
        FOR_PARTS = (
            "for_parts",
            "Solo para repuestos",
        )

    repair = models.ForeignKey(
        Repair,
        on_delete=models.CASCADE,
        related_name="diagnoses",
        verbose_name="Reparación",
    )

    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_diagnoses",
        verbose_name="Técnico",
    )

    diagnosis_type = models.CharField(
        max_length=30,
        choices=DiagnosisType.choices,
        default=DiagnosisType.TECHNICAL,
        db_index=True,
        verbose_name="Tipo de diagnóstico",
    )

    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.MEDIUM,
        db_index=True,
        verbose_name="Severidad",
    )

    repairability = models.CharField(
        max_length=40,
        choices=Repairability.choices,
        default=Repairability.PENDING,
        db_index=True,
        verbose_name="Reparabilidad",
    )

    diagnosed_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha del diagnóstico",
    )

    reported_symptoms = models.TextField(
        blank=True,
        verbose_name="Síntomas reportados",
        help_text=(
            "Síntomas observados o comunicados antes "
            "de realizar el diagnóstico."
        ),
    )

    observed_symptoms = models.TextField(
        blank=True,
        verbose_name="Síntomas observados",
        help_text=(
            "Problemas comprobados directamente por el técnico."
        ),
    )

    probable_cause = models.TextField(
        blank=True,
        verbose_name="Causa probable",
    )

    confirmed_cause = models.TextField(
        blank=True,
        verbose_name="Causa confirmada",
    )

    technical_diagnosis = models.TextField(
        verbose_name="Diagnóstico técnico",
    )

    recommended_work = models.TextField(
        blank=True,
        verbose_name="Trabajo recomendado",
    )

    required_parts_description = models.TextField(
        blank=True,
        verbose_name="Repuestos requeridos",
    )

    estimated_work_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horas estimadas de trabajo",
    )

    estimated_parts_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Costo estimado de repuestos",
    )

    estimated_external_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Costo externo estimado",
    )

    requires_parts = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere repuestos",
    )

    requires_external_service = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere servicio externo",
    )

    requires_additional_testing = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere pruebas adicionales",
    )

    requires_disassembly = models.BooleanField(
        default=False,
        verbose_name="Requiere desmontaje",
    )

    is_main_diagnosis = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Diagnóstico principal",
        help_text=(
            "Solo debe existir un diagnóstico principal "
            "por reparación."
        ),
    )

    is_confirmed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Diagnóstico confirmado",
    )

    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="confirmed_repair_diagnoses",
        verbose_name="Confirmado por",
    )

    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de confirmación",
    )

    observations = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Diagnóstico de reparación"
        verbose_name_plural = "Diagnósticos de reparaciones"
        ordering = (
            "-is_main_diagnosis",
            "-diagnosed_at",
            "-created_at",
        )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "repair",
                ],
                condition=models.Q(
                    is_main_diagnosis=True,
                    archived_at__isnull=True,
                ),
                name="unique_main_repair_diagnosis",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "repair",
                    "diagnosed_at",
                ],
                name="repair_diag_date_idx",
            ),
            models.Index(
                fields=[
                    "technician",
                    "diagnosed_at",
                ],
                name="repair_diag_tech_idx",
            ),
            models.Index(
                fields=[
                    "repairability",
                    "severity",
                ],
                name="repair_diag_result_idx",
            ),
            models.Index(
                fields=[
                    "is_main_diagnosis",
                    "is_confirmed",
                ],
                name="repair_diag_main_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.repair.code} - "
            f"{self.get_diagnosis_type_display()}"
        )

    def clean(self):
        """
        Normaliza y valida el diagnóstico.
        """

        super().clean()

        self.reported_symptoms = str(
            self.reported_symptoms or ""
        ).strip()

        self.observed_symptoms = str(
            self.observed_symptoms or ""
        ).strip()

        self.probable_cause = str(
            self.probable_cause or ""
        ).strip()

        self.confirmed_cause = str(
            self.confirmed_cause or ""
        ).strip()

        self.technical_diagnosis = str(
            self.technical_diagnosis or ""
        ).strip()

        self.recommended_work = str(
            self.recommended_work or ""
        ).strip()

        self.required_parts_description = str(
            self.required_parts_description or ""
        ).strip()

        self.observations = str(
            self.observations or ""
        ).strip()

        if not self.repair_id:
            raise ValidationError(
                {
                    "repair": (
                        "La reparación es obligatoria."
                    ),
                }
            )

        if not self.technical_diagnosis:
            raise ValidationError(
                {
                    "technical_diagnosis": (
                        "El diagnóstico técnico es obligatorio."
                    ),
                }
            )

        if self.is_main_diagnosis and self.repair_id:
            existing_main = RepairDiagnosis.objects.filter(
                repair_id=self.repair_id,
                is_main_diagnosis=True,
                archived_at__isnull=True,
            ).exclude(
                pk=self.pk,
            )

            if existing_main.exists():
                raise ValidationError(
                    {
                        "is_main_diagnosis": (
                            "La reparación ya tiene un "
                            "diagnóstico principal."
                        ),
                    }
                )

        if (
            self.requires_parts
            and not self.required_parts_description
        ):
            raise ValidationError(
                {
                    "required_parts_description": (
                        "Debe indicar los repuestos requeridos."
                    ),
                }
            )

        if (
            not self.requires_parts
            and self.required_parts_description
        ):
            raise ValidationError(
                {
                    "required_parts_description": (
                        "No debe indicar repuestos si el diagnóstico "
                        "no requiere repuestos."
                    ),
                }
            )

        if (
            self.repairability
            == self.Repairability.REPAIRABLE_WITH_PARTS
            and not self.requires_parts
        ):
            raise ValidationError(
                {
                    "requires_parts": (
                        "Debe marcar que requiere repuestos."
                    ),
                }
            )

        if (
            self.repairability
            == self.Repairability.REPAIRABLE_WITH_EXTERNAL_SERVICE
            and not self.requires_external_service
        ):
            raise ValidationError(
                {
                    "requires_external_service": (
                        "Debe marcar que requiere servicio externo."
                    ),
                }
            )

        if self.estimated_work_hours is not None:
            if self.estimated_work_hours <= 0:
                raise ValidationError(
                    {
                        "estimated_work_hours": (
                            "Las horas estimadas deben ser "
                            "mayores que cero."
                        ),
                    }
                )

        if self.estimated_parts_cost is not None:
            if self.estimated_parts_cost < 0:
                raise ValidationError(
                    {
                        "estimated_parts_cost": (
                            "El costo estimado de repuestos "
                            "no puede ser negativo."
                        ),
                    }
                )

        if self.estimated_external_cost is not None:
            if self.estimated_external_cost < 0:
                raise ValidationError(
                    {
                        "estimated_external_cost": (
                            "El costo externo estimado "
                            "no puede ser negativo."
                        ),
                    }
                )

        if self.is_confirmed:
            if not self.confirmed_by_id:
                raise ValidationError(
                    {
                        "confirmed_by": (
                            "Debe indicar quién confirmó "
                            "el diagnóstico."
                        ),
                    }
                )

            if not self.confirmed_at:
                raise ValidationError(
                    {
                        "confirmed_at": (
                            "Debe registrar la fecha "
                            "de confirmación."
                        ),
                    }
                )

        if not self.is_confirmed:
            if self.confirmed_by_id or self.confirmed_at:
                raise ValidationError(
                    {
                        "is_confirmed": (
                            "No debe registrar datos de confirmación "
                            "si el diagnóstico no está confirmado."
                        ),
                    }
                )

        if (
            self.confirmed_at
            and self.confirmed_at < self.diagnosed_at
        ):
            raise ValidationError(
                {
                    "confirmed_at": (
                        "La fecha de confirmación no puede ser "
                        "anterior al diagnóstico."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        """
        Normaliza, valida y sincroniza el diagnóstico principal.
        """

        self.reported_symptoms = str(
            self.reported_symptoms or ""
        ).strip()

        self.observed_symptoms = str(
            self.observed_symptoms or ""
        ).strip()

        self.probable_cause = str(
            self.probable_cause or ""
        ).strip()

        self.confirmed_cause = str(
            self.confirmed_cause or ""
        ).strip()

        self.technical_diagnosis = str(
            self.technical_diagnosis or ""
        ).strip()

        self.recommended_work = str(
            self.recommended_work or ""
        ).strip()

        self.required_parts_description = str(
            self.required_parts_description or ""
        ).strip()

        self.observations = str(
            self.observations or ""
        ).strip()

        self.full_clean()

        result = super().save(
            *args,
            **kwargs,
        )

        if self.is_main_diagnosis and self.repair_id:
            repair = self.repair
            fields_to_update = []

            if repair.requires_parts != self.requires_parts:
                repair.requires_parts = self.requires_parts
                fields_to_update.append(
                    "requires_parts"
                )

            if (
                repair.requires_external_service
                != self.requires_external_service
            ):
                repair.requires_external_service = (
                    self.requires_external_service
                )
                fields_to_update.append(
                    "requires_external_service"
                )

            if fields_to_update:
                fields_to_update.append(
                    "updated_at"
                )

                repair.save(
                    update_fields=fields_to_update,
                )

        return result