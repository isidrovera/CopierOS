# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class DeviceProfileAssignment(MonitoringBaseModel):
    """
    Historial de asignación de perfiles SNMP a dispositivos.

    Permite conocer:

    - Qué perfil se aplicó.
    - Qué versión y revisión se utilizaron.
    - Cómo se seleccionó.
    - Qué condiciones coincidieron.
    - Qué puntaje obtuvo.
    - Cuándo comenzó y terminó la asignación.
    - Si fue automática o manual.
    - Por qué fue reemplazada o descartada.
    """

    class AssignmentType(models.TextChoices):
        AUTOMATIC = (
            "automatic",
            "Automática",
        )
        MANUAL = (
            "manual",
            "Manual",
        )
        FALLBACK = (
            "fallback",
            "Perfil alternativo",
        )
        DEFAULT = (
            "default",
            "Perfil predeterminado",
        )
        TEST = (
            "test",
            "Asignación de prueba",
        )

    class Status(models.TextChoices):
        CANDIDATE = (
            "candidate",
            "Candidato",
        )
        TESTING = (
            "testing",
            "En pruebas",
        )
        ACTIVE = (
            "active",
            "Activo",
        )
        REJECTED = (
            "rejected",
            "Rechazado",
        )
        REPLACED = (
            "replaced",
            "Reemplazado",
        )
        EXPIRED = (
            "expired",
            "Expirado",
        )
        FAILED = (
            "failed",
            "Con error",
        )

    class MatchMethod(models.TextChoices):
        MANUAL = (
            "manual",
            "Asignación manual",
        )
        DEVICE_OVERRIDE = (
            "device_override",
            "Regla del dispositivo",
        )
        SYS_OBJECT_ID = (
            "sys_object_id",
            "SysObjectID exacto",
        )
        SYS_OBJECT_PREFIX = (
            "sys_object_prefix",
            "Prefijo SysObjectID",
        )
        EQUIPMENT_MODEL = (
            "equipment_model",
            "Modelo de equipo",
        )
        FAMILY = (
            "family",
            "Familia",
        )
        BRAND = (
            "brand",
            "Marca",
        )
        ENTERPRISE = (
            "enterprise",
            "Enterprise",
        )
        FIRMWARE = (
            "firmware",
            "Firmware",
        )
        DESCRIPTION = (
            "description",
            "Descripción SNMP",
        )
        COMBINED = (
            "combined",
            "Coincidencia combinada",
        )
        DEFAULT = (
            "default",
            "Perfil predeterminado",
        )
        FALLBACK = (
            "fallback",
            "Perfil alternativo",
        )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        on_delete=models.PROTECT,
        related_name="profile_assignments",
        verbose_name="Dispositivo",
    )

    profile = models.ForeignKey(
        "monitoring.SNMPProfile",
        on_delete=models.PROTECT,
        related_name="device_assignments",
        verbose_name="Perfil SNMP",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_profile_assignments",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_profile_assignments",
        verbose_name="Sede",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        on_delete=models.PROTECT,
        related_name="device_profile_assignments",
        verbose_name="Agente",
    )

    assignment_type = models.CharField(
        max_length=20,
        choices=AssignmentType.choices,
        default=AssignmentType.AUTOMATIC,
        db_index=True,
        verbose_name="Tipo de asignación",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CANDIDATE,
        db_index=True,
        verbose_name="Estado",
    )

    match_method = models.CharField(
        max_length=30,
        choices=MatchMethod.choices,
        default=MatchMethod.COMBINED,
        db_index=True,
        verbose_name="Método de coincidencia",
    )

    profile_code = models.CharField(
        max_length=150,
        db_index=True,
        editable=False,
        verbose_name="Código del perfil aplicado",
    )

    profile_version = models.CharField(
        max_length=50,
        db_index=True,
        editable=False,
        verbose_name="Versión aplicada",
    )

    profile_revision = models.PositiveIntegerField(
        default=1,
        editable=False,
        verbose_name="Revisión aplicada",
    )

    profile_checksum = models.CharField(
        max_length=64,
        blank=True,
        editable=False,
        verbose_name="Checksum aplicado",
    )

    priority_at_assignment = models.PositiveIntegerField(
        default=100,
        verbose_name="Prioridad aplicada",
    )

    specificity_score = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Puntaje de especificidad",
    )

    match_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        db_index=True,
        verbose_name="Puntaje de coincidencia",
    )

    confidence_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        db_index=True,
        verbose_name="Confianza",
    )

    matched_conditions = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Condiciones coincidentes",
        help_text=(
            "Lista de reglas que coincidieron durante "
            "la selección del perfil."
        ),
    )

    failed_conditions = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Condiciones no coincidentes",
    )

    selection_details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Detalle de selección",
    )

    tested_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas probadas",
    )

    successful_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas correctas",
    )

    failed_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas con error",
    )

    required_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas obligatorias",
    )

    successful_required_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas obligatorias correctas",
    )

    test_success_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Resultado de prueba",
    )

    assigned_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de asignación",
    )

    testing_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio de prueba",
    )

    testing_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin de prueba",
    )

    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de activación",
    )

    deactivated_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de desactivación",
    )

    last_successful_use_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último uso correcto",
    )

    last_failed_use_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último uso con error",
    )

    consecutive_failure_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Errores consecutivos",
    )

    total_successful_uses = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Usos correctos",
    )

    total_failed_uses = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Usos con error",
    )

    is_current = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Asignación actual",
    )

    is_locked = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Asignación bloqueada",
        help_text=(
            "Una asignación bloqueada no puede reemplazarse "
            "automáticamente."
        ),
    )

    assigned_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_monitoring_profiles",
        verbose_name="Asignado por",
    )

    deactivated_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deactivated_monitoring_profiles",
        verbose_name="Desactivado por",
    )

    assignment_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de asignación",
    )

    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de rechazo",
    )

    deactivation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de desactivación",
    )

    last_error_message = models.TextField(
        blank=True,
        verbose_name="Último error",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Asignación de perfil SNMP"
        verbose_name_plural = "Asignaciones de perfiles SNMP"
        ordering = (
            "-is_current",
            "-assigned_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "device",
                    "is_current",
                    "status",
                ],
                name="mon_assign_device_current_idx",
            ),
            models.Index(
                fields=[
                    "profile",
                    "status",
                    "assigned_at",
                ],
                name="mon_assign_profile_status_idx",
            ),
            models.Index(
                fields=[
                    "customer",
                    "branch",
                    "assigned_at",
                ],
                name="mon_assign_customer_date_idx",
            ),
            models.Index(
                fields=[
                    "match_method",
                    "confidence_percent",
                ],
                name="mon_assign_match_conf_idx",
            ),
            models.Index(
                fields=[
                    "is_locked",
                    "is_current",
                ],
                name="mon_assign_locked_current_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "device",
                ],
                condition=models.Q(
                    is_current=True,
                    archived_at__isnull=True,
                ),
                name="unique_current_profile_per_device",
            ),
        ]

    def __str__(self):
        return (
            f"{self.device} - "
            f"{self.profile_code} "
            f"v{self.profile_version}"
        )

    def calculate_test_success_percent(self):
        if self.tested_metric_count <= 0:
            self.test_success_percent = None
            return

        self.test_success_percent = (
            Decimal(self.successful_metric_count)
            / Decimal(self.tested_metric_count)
            * Decimal("100")
        ).quantize(
            Decimal("0.01")
        )

    def required_metrics_passed(self):
        if self.required_metric_count == 0:
            return True

        return (
            self.successful_required_metric_count
            >= self.required_metric_count
        )

    def begin_testing(self):
        if self.status not in {
            self.Status.CANDIDATE,
            self.Status.FAILED,
        }:
            raise ValidationError(
                "Esta asignación no puede iniciar pruebas."
            )

        self.status = self.Status.TESTING
        self.testing_started_at = timezone.now()
        self.testing_completed_at = None
        self.last_error_message = ""

        self.save(
            update_fields=[
                "status",
                "testing_started_at",
                "testing_completed_at",
                "last_error_message",
                "updated_at",
            ]
        )

    def complete_testing(
        self,
        *,
        tested_metric_count,
        successful_metric_count,
        failed_metric_count,
        required_metric_count=0,
        successful_required_metric_count=0,
        minimum_success_percent=Decimal("70.00"),
    ):
        self.tested_metric_count = max(
            int(tested_metric_count or 0),
            0,
        )
        self.successful_metric_count = max(
            int(successful_metric_count or 0),
            0,
        )
        self.failed_metric_count = max(
            int(failed_metric_count or 0),
            0,
        )
        self.required_metric_count = max(
            int(required_metric_count or 0),
            0,
        )
        self.successful_required_metric_count = max(
            int(successful_required_metric_count or 0),
            0,
        )

        self.testing_completed_at = timezone.now()
        self.calculate_test_success_percent()

        success_percent = (
            self.test_success_percent
            if self.test_success_percent is not None
            else Decimal("0")
        )

        test_passed = (
            success_percent >= Decimal(
                str(minimum_success_percent)
            )
            and self.required_metrics_passed()
        )

        self.status = (
            self.Status.CANDIDATE
            if test_passed
            else self.Status.FAILED
        )

        self.save(
            update_fields=[
                "tested_metric_count",
                "successful_metric_count",
                "failed_metric_count",
                "required_metric_count",
                "successful_required_metric_count",
                "testing_completed_at",
                "test_success_percent",
                "status",
                "updated_at",
            ]
        )

        return test_passed

    def activate(
        self,
        *,
        user=None,
        reason="",
        force=False,
    ):
        if self.status not in {
            self.Status.CANDIDATE,
            self.Status.TESTING,
            self.Status.FAILED,
        }:
            raise ValidationError(
                "Esta asignación no puede activarse."
            )

        current_assignment = (
            DeviceProfileAssignment.objects
            .filter(
                device=self.device,
                is_current=True,
                archived_at__isnull=True,
            )
            .exclude(
                pk=self.pk,
            )
            .select_for_update()
            .first()
        )

        if current_assignment:
            if current_assignment.is_locked and not force:
                raise ValidationError(
                    "La asignación actual está bloqueada."
                )

            current_assignment.is_current = False
            current_assignment.status = (
                self.Status.REPLACED
            )
            current_assignment.deactivated_at = (
                timezone.now()
            )
            current_assignment.deactivated_by = user
            current_assignment.deactivation_reason = (
                str(
                    reason
                    or (
                        "Reemplazada por una nueva "
                        "asignación de perfil."
                    )
                ).strip()
            )

            current_assignment.save(
                update_fields=[
                    "is_current",
                    "status",
                    "deactivated_at",
                    "deactivated_by",
                    "deactivation_reason",
                    "updated_at",
                ]
            )

        self.status = self.Status.ACTIVE
        self.is_current = True
        self.activated_at = timezone.now()
        self.deactivated_at = None
        self.deactivated_by = None
        self.deactivation_reason = ""

        if user and not self.assigned_by_id:
            self.assigned_by = user

        if reason:
            self.assignment_reason = str(
                reason
            ).strip()

        self.save(
            update_fields=[
                "status",
                "is_current",
                "activated_at",
                "deactivated_at",
                "deactivated_by",
                "deactivation_reason",
                "assigned_by",
                "assignment_reason",
                "updated_at",
            ]
        )

        return self

    def reject(
        self,
        *,
        reason,
        user=None,
    ):
        if self.is_current:
            raise ValidationError(
                "La asignación actual no puede rechazarse."
            )

        self.status = self.Status.REJECTED
        self.rejection_reason = str(
            reason or ""
        ).strip()

        self.deactivated_at = timezone.now()
        self.deactivated_by = user

        self.save(
            update_fields=[
                "status",
                "rejection_reason",
                "deactivated_at",
                "deactivated_by",
                "updated_at",
            ]
        )

    def deactivate(
        self,
        *,
        reason,
        user=None,
        status=None,
    ):
        if not self.is_current:
            return self

        self.is_current = False
        self.status = (
            status
            or self.Status.REPLACED
        )
        self.deactivated_at = timezone.now()
        self.deactivated_by = user
        self.deactivation_reason = str(
            reason or ""
        ).strip()

        self.save(
            update_fields=[
                "is_current",
                "status",
                "deactivated_at",
                "deactivated_by",
                "deactivation_reason",
                "updated_at",
            ]
        )

        return self

    def register_successful_use(self):
        self.total_successful_uses += 1
        self.consecutive_failure_count = 0
        self.last_successful_use_at = timezone.now()
        self.last_error_message = ""

        self.save(
            update_fields=[
                "total_successful_uses",
                "consecutive_failure_count",
                "last_successful_use_at",
                "last_error_message",
                "updated_at",
            ]
        )

    def register_failed_use(
        self,
        error_message,
    ):
        self.total_failed_uses += 1
        self.consecutive_failure_count += 1
        self.last_failed_use_at = timezone.now()
        self.last_error_message = str(
            error_message or ""
        ).strip()

        self.save(
            update_fields=[
                "total_failed_uses",
                "consecutive_failure_count",
                "last_failed_use_at",
                "last_error_message",
                "updated_at",
            ]
        )

    def clean(self):
        super().clean()

        text_fields = [
            "profile_code",
            "profile_version",
            "profile_checksum",
            "assignment_reason",
            "rejection_reason",
            "deactivation_reason",
            "last_error_message",
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

        self.profile_code = self.profile_code.upper()

        if not self.device_id:
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo es obligatorio."
                    ),
                }
            )

        if not self.profile_id:
            raise ValidationError(
                {
                    "profile": (
                        "El perfil SNMP es obligatorio."
                    ),
                }
            )

        if self.device.customer_id != self.customer_id:
            raise ValidationError(
                {
                    "customer": (
                        "El cliente no coincide con "
                        "el dispositivo."
                    ),
                }
            )

        if self.device.agent_id != self.agent_id:
            raise ValidationError(
                {
                    "agent": (
                        "El agente no coincide con "
                        "el dispositivo."
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

        if not self.profile.applies_to_scope(
            customer=self.customer,
            branch=self.branch,
            agent=self.agent,
            device=self.device,
        ):
            raise ValidationError(
                {
                    "profile": (
                        "El perfil no aplica al alcance "
                        "del dispositivo."
                    ),
                }
            )

        if self.match_score < 0:
            raise ValidationError(
                {
                    "match_score": (
                        "El puntaje no puede ser negativo."
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

        if self.successful_metric_count > self.tested_metric_count:
            raise ValidationError(
                {
                    "successful_metric_count": (
                        "Las métricas correctas no pueden superar "
                        "las métricas probadas."
                    ),
                }
            )

        if self.failed_metric_count > self.tested_metric_count:
            raise ValidationError(
                {
                    "failed_metric_count": (
                        "Las métricas con error no pueden superar "
                        "las métricas probadas."
                    ),
                }
            )

        if (
            self.successful_metric_count
            + self.failed_metric_count
            > self.tested_metric_count
        ):
            raise ValidationError(
                {
                    "tested_metric_count": (
                        "La suma de resultados no puede superar "
                        "las métricas probadas."
                    ),
                }
            )

        if (
            self.successful_required_metric_count
            > self.required_metric_count
        ):
            raise ValidationError(
                {
                    "successful_required_metric_count": (
                        "Las métricas obligatorias correctas "
                        "no pueden superar el total obligatorio."
                    ),
                }
            )

        if self.is_current:
            if self.status != self.Status.ACTIVE:
                raise ValidationError(
                    {
                        "status": (
                            "La asignación actual debe estar activa."
                        ),
                    }
                )

            if not self.activated_at:
                raise ValidationError(
                    {
                        "activated_at": (
                            "La asignación actual requiere "
                            "fecha de activación."
                        ),
                    }
                )

        if (
            self.deactivated_at
            and self.activated_at
            and self.deactivated_at < self.activated_at
        ):
            raise ValidationError(
                {
                    "deactivated_at": (
                        "La desactivación no puede ser anterior "
                        "a la activación."
                    ),
                }
            )

        if not isinstance(
            self.matched_conditions,
            list,
        ):
            raise ValidationError(
                {
                    "matched_conditions": (
                        "Las condiciones coincidentes deben "
                        "ser una lista."
                    ),
                }
            )

        if not isinstance(
            self.failed_conditions,
            list,
        ):
            raise ValidationError(
                {
                    "failed_conditions": (
                        "Las condiciones fallidas deben "
                        "ser una lista."
                    ),
                }
            )

        if not isinstance(
            self.selection_details,
            dict,
        ):
            raise ValidationError(
                {
                    "selection_details": (
                        "El detalle de selección debe "
                        "ser un objeto."
                    ),
                }
            )

        self.calculate_test_success_percent()

    def save(self, *args, **kwargs):
        if self.device_id:
            self.customer = self.device.customer
            self.branch = self.device.branch
            self.agent = self.device.agent

        if self.profile_id:
            self.profile_code = self.profile.code
            self.profile_version = self.profile.version
            self.profile_revision = self.profile.revision
            self.profile_checksum = self.profile.checksum
            self.priority_at_assignment = self.profile.priority

            if not self.specificity_score:
                self.specificity_score = (
                    self.profile.get_specificity_score()
                )

        self.profile_code = str(
            self.profile_code or ""
        ).strip().upper()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )