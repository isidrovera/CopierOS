# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class SNMPProfileTest(MonitoringBaseModel):
    """
    Ejecución histórica de prueba de un perfil SNMP sobre
    un dispositivo monitoreado.

    Permite verificar el perfil antes de activarlo y conservar:

    - Perfil, versión y revisión probadas.
    - Credencial SNMP utilizada.
    - Métricas consultadas.
    - Métricas correctas, vacías y fallidas.
    - OID que respondieron.
    - OID no compatibles.
    - Tiempos de respuesta.
    - Cobertura por categoría.
    - Resultado final.
    """

    class TestType(models.TextChoices):
        AUTOMATIC_SELECTION = (
            "automatic_selection",
            "Selección automática",
        )
        MANUAL = (
            "manual",
            "Prueba manual",
        )
        PROFILE_UPDATE = (
            "profile_update",
            "Actualización de perfil",
        )
        FIRMWARE_CHANGE = (
            "firmware_change",
            "Cambio de firmware",
        )
        DIAGNOSTIC = (
            "diagnostic",
            "Diagnóstico",
        )
        PERIODIC_VALIDATION = (
            "periodic_validation",
            "Validación periódica",
        )

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        RUNNING = (
            "running",
            "En ejecución",
        )
        COMPLETED = (
            "completed",
            "Completada",
        )
        PARTIAL = (
            "partial",
            "Parcial",
        )
        FAILED = (
            "failed",
            "Fallida",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )

    class Result(models.TextChoices):
        UNKNOWN = (
            "unknown",
            "Sin resultado",
        )
        PASSED = (
            "passed",
            "Aprobado",
        )
        PASSED_WITH_WARNINGS = (
            "passed_with_warnings",
            "Aprobado con advertencias",
        )
        FAILED_REQUIRED_METRICS = (
            "failed_required_metrics",
            "Fallaron métricas obligatorias",
        )
        FAILED_LOW_COVERAGE = (
            "failed_low_coverage",
            "Cobertura insuficiente",
        )
        FAILED_CONNECTION = (
            "failed_connection",
            "Error de conexión",
        )
        FAILED_AUTHENTICATION = (
            "failed_authentication",
            "Error de autenticación",
        )
        FAILED_PROFILE = (
            "failed_profile",
            "Perfil incompatible",
        )
        CANCELLED = (
            "cancelled",
            "Cancelado",
        )

    class ConnectionStatus(models.TextChoices):
        UNKNOWN = (
            "unknown",
            "Desconocido",
        )
        SUCCESS = (
            "success",
            "Correcto",
        )
        TIMEOUT = (
            "timeout",
            "Tiempo agotado",
        )
        AUTHENTICATION_ERROR = (
            "authentication_error",
            "Error de autenticación",
        )
        NETWORK_ERROR = (
            "network_error",
            "Error de red",
        )
        SNMP_ERROR = (
            "snmp_error",
            "Error SNMP",
        )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        on_delete=models.PROTECT,
        related_name="profile_tests",
        verbose_name="Dispositivo",
    )

    profile = models.ForeignKey(
        "monitoring.SNMPProfile",
        on_delete=models.PROTECT,
        related_name="tests",
        verbose_name="Perfil SNMP",
    )

    assignment = models.ForeignKey(
        "monitoring.DeviceProfileAssignment",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="tests",
        verbose_name="Asignación evaluada",
    )

    credential = models.ForeignKey(
        "monitoring.SNMPCredential",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="profile_tests",
        verbose_name="Credencial utilizada",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_profile_tests",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_profile_tests",
        verbose_name="Sede",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        on_delete=models.PROTECT,
        related_name="profile_tests",
        verbose_name="Agente",
    )

    test_type = models.CharField(
        max_length=30,
        choices=TestType.choices,
        default=TestType.AUTOMATIC_SELECTION,
        db_index=True,
        verbose_name="Tipo de prueba",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    result = models.CharField(
        max_length=40,
        choices=Result.choices,
        default=Result.UNKNOWN,
        db_index=True,
        verbose_name="Resultado",
    )

    connection_status = models.CharField(
        max_length=30,
        choices=ConnectionStatus.choices,
        default=ConnectionStatus.UNKNOWN,
        db_index=True,
        verbose_name="Estado de conexión",
    )

    agent_test_id = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Identificador generado por el agente",
    )

    profile_code = models.CharField(
        max_length=150,
        db_index=True,
        editable=False,
        verbose_name="Código del perfil",
    )

    profile_version = models.CharField(
        max_length=50,
        db_index=True,
        editable=False,
        verbose_name="Versión probada",
    )

    profile_revision = models.PositiveIntegerField(
        default=1,
        editable=False,
        verbose_name="Revisión probada",
    )

    profile_checksum = models.CharField(
        max_length=64,
        blank=True,
        editable=False,
        verbose_name="Checksum probado",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de inicio",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de finalización",
    )

    received_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de recepción",
    )

    duration_ms = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración en milisegundos",
    )

    ip_address = models.GenericIPAddressField(
        protocol="both",
        unpack_ipv4=True,
        db_index=True,
        verbose_name="Dirección IP probada",
    )

    snmp_port = models.PositiveIntegerField(
        default=161,
        verbose_name="Puerto SNMP",
    )

    snmp_version = models.CharField(
        max_length=10,
        blank=True,
        db_index=True,
        verbose_name="Versión SNMP",
    )

    response_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo de respuesta inicial",
    )

    total_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Total de métricas",
    )

    enabled_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas habilitadas",
    )

    tested_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas probadas",
    )

    successful_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas correctas",
    )

    empty_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas sin valor",
    )

    unsupported_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas no compatibles",
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

    failed_required_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas obligatorias fallidas",
    )

    identity_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas de identidad correctas",
    )

    counter_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas de contadores correctas",
    )

    consumable_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas de consumibles correctas",
    )

    component_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas de componentes correctas",
    )

    tray_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas de bandejas correctas",
    )

    accessory_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas de accesorios correctas",
    )

    alert_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas de alertas correctas",
    )

    job_metric_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Métricas de trabajos correctas",
    )

    coverage_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Cobertura general",
    )

    required_coverage_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cobertura obligatoria",
    )

    average_response_time_ms = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Tiempo promedio de respuesta",
    )

    minimum_response_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo mínimo de respuesta",
    )

    maximum_response_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo máximo de respuesta",
    )

    timeout_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Tiempos agotados",
    )

    authentication_error_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Errores de autenticación",
    )

    parse_error_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Errores de interpretación",
    )

    validation_error_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Errores de validación",
    )

    oid_requested_count = models.PositiveIntegerField(
        default=0,
        verbose_name="OID solicitados",
    )

    oid_responded_count = models.PositiveIntegerField(
        default=0,
        verbose_name="OID respondidos",
    )

    unknown_oid_count = models.PositiveIntegerField(
        default=0,
        verbose_name="OID desconocidos",
    )

    required_metrics_passed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Métricas obligatorias aprobadas",
    )

    identity_confirmed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Identidad confirmada",
    )

    serial_number_confirmed = models.BooleanField(
        default=False,
        verbose_name="Serie confirmada",
    )

    model_confirmed = models.BooleanField(
        default=False,
        verbose_name="Modelo confirmado",
    )

    firmware_supported = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Firmware compatible",
    )

    recommended_for_activation = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Recomendado para activación",
    )

    minimum_coverage_required = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("70.00"),
        verbose_name="Cobertura mínima requerida",
    )

    minimum_required_coverage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("100.00"),
        verbose_name="Cobertura obligatoria mínima",
    )

    metric_results = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Resultados por métrica",
        help_text=(
            "Resumen recibido desde el agente. No debe incluir "
            "credenciales ni secretos SNMP."
        ),
    )

    category_summary = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Resumen por categoría",
    )

    successful_oids = models.JSONField(
        default=list,
        blank=True,
        verbose_name="OID correctos",
    )

    failed_oids = models.JSONField(
        default=list,
        blank=True,
        verbose_name="OID fallidos",
    )

    unsupported_oids = models.JSONField(
        default=list,
        blank=True,
        verbose_name="OID no compatibles",
    )

    unknown_oids = models.JSONField(
        default=list,
        blank=True,
        verbose_name="OID desconocidos",
    )

    detected_identity = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Identidad detectada",
    )

    error_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de error",
    )

    error_message = models.TextField(
        blank=True,
        verbose_name="Mensaje de error",
    )

    warning_messages = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Advertencias",
    )

    cancellation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de cancelación",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Prueba de perfil SNMP"
        verbose_name_plural = "Pruebas de perfiles SNMP"
        ordering = (
            "-received_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "device",
                    "profile",
                    "started_at",
                ],
                name="mon_ptest_device_profile_idx",
            ),
            models.Index(
                fields=[
                    "customer",
                    "result",
                    "received_at",
                ],
                name="mon_ptest_customer_result_idx",
            ),
            models.Index(
                fields=[
                    "profile",
                    "recommended_for_activation",
                    "coverage_percent",
                ],
                name="mon_ptest_prof_rec_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "connection_status",
                    "received_at",
                ],
                name="mon_ptest_stat_conn_idx",
            ),
            models.Index(
                fields=[
                    "required_metrics_passed",
                    "identity_confirmed",
                    "coverage_percent",
                ],
                name="mon_ptest_validation_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "agent",
                    "agent_test_id",
                ],
                name="unique_agent_profile_test",
            ),
        ]

    def __str__(self):
        return (
            f"{self.device} - "
            f"{self.profile_code} "
            f"v{self.profile_version} - "
            f"{self.get_result_display()}"
        )

    def calculate_duration(self):
        if self.started_at and self.completed_at:
            milliseconds = (
                self.completed_at - self.started_at
            ).total_seconds() * 1000

            self.duration_ms = max(
                int(milliseconds),
                0,
            )

    def calculate_coverage(self):
        if self.tested_metric_count > 0:
            self.coverage_percent = (
                Decimal(self.successful_metric_count)
                / Decimal(self.tested_metric_count)
                * Decimal("100")
            ).quantize(
                Decimal("0.01")
            )
        else:
            self.coverage_percent = None

        if self.required_metric_count > 0:
            self.required_coverage_percent = (
                Decimal(
                    self.successful_required_metric_count
                )
                / Decimal(self.required_metric_count)
                * Decimal("100")
            ).quantize(
                Decimal("0.01")
            )
        else:
            self.required_coverage_percent = Decimal("100.00")

        self.required_metrics_passed = (
            self.required_coverage_percent
            >= self.minimum_required_coverage
        )

    def calculate_result(self):
        self.recommended_for_activation = False

        if self.status == self.Status.CANCELLED:
            self.result = self.Result.CANCELLED
            return

        if (
            self.connection_status
            == self.ConnectionStatus.AUTHENTICATION_ERROR
        ):
            self.result = self.Result.FAILED_AUTHENTICATION
            return

        if self.connection_status in {
            self.ConnectionStatus.TIMEOUT,
            self.ConnectionStatus.NETWORK_ERROR,
            self.ConnectionStatus.SNMP_ERROR,
        }:
            self.result = self.Result.FAILED_CONNECTION
            return

        if not self.required_metrics_passed:
            self.result = (
                self.Result.FAILED_REQUIRED_METRICS
            )
            return

        coverage = (
            self.coverage_percent
            if self.coverage_percent is not None
            else Decimal("0")
        )

        if coverage < self.minimum_coverage_required:
            self.result = self.Result.FAILED_LOW_COVERAGE
            return

        if not self.identity_confirmed:
            self.result = self.Result.FAILED_PROFILE
            return

        has_warnings = bool(
            self.warning_messages
            or self.empty_metric_count
            or self.unsupported_metric_count
            or self.parse_error_count
            or self.validation_error_count
        )

        self.result = (
            self.Result.PASSED_WITH_WARNINGS
            if has_warnings
            else self.Result.PASSED
        )

        self.recommended_for_activation = True

    def begin(self):
        if self.status not in {
            self.Status.PENDING,
            self.Status.FAILED,
        }:
            raise ValidationError(
                "Esta prueba no puede volver a iniciarse."
            )

        self.status = self.Status.RUNNING
        self.result = self.Result.UNKNOWN
        self.started_at = timezone.now()
        self.completed_at = None
        self.duration_ms = None
        self.error_code = ""
        self.error_message = ""
        self.cancellation_reason = ""

        self.save(
            update_fields=[
                "status",
                "result",
                "started_at",
                "completed_at",
                "duration_ms",
                "error_code",
                "error_message",
                "cancellation_reason",
                "updated_at",
            ]
        )

    def complete(
        self,
        *,
        connection_status,
        tested_metric_count,
        successful_metric_count,
        empty_metric_count=0,
        unsupported_metric_count=0,
        failed_metric_count=0,
        required_metric_count=0,
        successful_required_metric_count=0,
        identity_confirmed=False,
        serial_number_confirmed=False,
        model_confirmed=False,
        firmware_supported=None,
        metric_results=None,
        category_summary=None,
        successful_oids=None,
        failed_oids=None,
        unsupported_oids=None,
        unknown_oids=None,
        detected_identity=None,
        warning_messages=None,
        partial=False,
    ):
        self.connection_status = connection_status

        self.tested_metric_count = max(
            int(tested_metric_count or 0),
            0,
        )
        self.successful_metric_count = max(
            int(successful_metric_count or 0),
            0,
        )
        self.empty_metric_count = max(
            int(empty_metric_count or 0),
            0,
        )
        self.unsupported_metric_count = max(
            int(unsupported_metric_count or 0),
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

        self.failed_required_metric_count = max(
            self.required_metric_count
            - self.successful_required_metric_count,
            0,
        )

        self.identity_confirmed = bool(
            identity_confirmed
        )
        self.serial_number_confirmed = bool(
            serial_number_confirmed
        )
        self.model_confirmed = bool(
            model_confirmed
        )
        self.firmware_supported = firmware_supported

        if metric_results is not None:
            self.metric_results = metric_results

        if category_summary is not None:
            self.category_summary = category_summary

        if successful_oids is not None:
            self.successful_oids = successful_oids

        if failed_oids is not None:
            self.failed_oids = failed_oids

        if unsupported_oids is not None:
            self.unsupported_oids = unsupported_oids

        if unknown_oids is not None:
            self.unknown_oids = unknown_oids

        if detected_identity is not None:
            self.detected_identity = detected_identity

        if warning_messages is not None:
            self.warning_messages = warning_messages

        self.completed_at = timezone.now()
        self.status = (
            self.Status.PARTIAL
            if partial
            else self.Status.COMPLETED
        )

        self.calculate_duration()
        self.calculate_coverage()
        self.calculate_result()

        if self.result in {
            self.Result.FAILED_REQUIRED_METRICS,
            self.Result.FAILED_LOW_COVERAGE,
            self.Result.FAILED_CONNECTION,
            self.Result.FAILED_AUTHENTICATION,
            self.Result.FAILED_PROFILE,
        }:
            self.status = self.Status.FAILED

        self.save()

        if self.assignment_id:
            self.assignment.complete_testing(
                tested_metric_count=self.tested_metric_count,
                successful_metric_count=(
                    self.successful_metric_count
                ),
                failed_metric_count=self.failed_metric_count,
                required_metric_count=(
                    self.required_metric_count
                ),
                successful_required_metric_count=(
                    self.successful_required_metric_count
                ),
                minimum_success_percent=(
                    self.minimum_coverage_required
                ),
            )

        self.profile.register_test_result(
            successful=self.recommended_for_activation,
            tested_at=self.completed_at,
        )

        return self.recommended_for_activation

    def fail(
        self,
        *,
        connection_status,
        error_message,
        error_code="",
    ):
        self.status = self.Status.FAILED
        self.connection_status = connection_status
        self.completed_at = timezone.now()
        self.error_code = str(
            error_code or ""
        ).strip().upper()
        self.error_message = str(
            error_message or ""
        ).strip()

        self.calculate_duration()
        self.calculate_coverage()
        self.calculate_result()

        self.save()

        self.profile.register_test_result(
            successful=False,
            tested_at=self.completed_at,
        )

        if self.assignment_id:
            self.assignment.register_failed_use(
                self.error_message
            )

    def cancel(
        self,
        reason,
    ):
        if self.status in {
            self.Status.COMPLETED,
            self.Status.FAILED,
            self.Status.CANCELLED,
        }:
            raise ValidationError(
                "Esta prueba ya finalizó."
            )

        self.status = self.Status.CANCELLED
        self.result = self.Result.CANCELLED
        self.completed_at = timezone.now()
        self.cancellation_reason = str(
            reason or ""
        ).strip()

        self.calculate_duration()
        self.save()

    def clean(self):
        super().clean()

        text_fields = [
            "agent_test_id",
            "profile_code",
            "profile_version",
            "profile_checksum",
            "snmp_version",
            "error_code",
            "error_message",
            "cancellation_reason",
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

        self.agent_test_id = self.agent_test_id.strip()
        self.profile_code = self.profile_code.upper()
        self.error_code = self.error_code.upper()

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
                        "El perfil es obligatorio."
                    ),
                }
            )

        if not self.agent_test_id:
            raise ValidationError(
                {
                    "agent_test_id": (
                        "El identificador de prueba "
                        "es obligatorio."
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

        if (
            self.credential_id
            and self.credential.customer_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "credential": (
                        "La credencial no pertenece al cliente."
                    ),
                }
            )

        if (
            self.assignment_id
            and self.assignment.device_id
            != self.device_id
        ):
            raise ValidationError(
                {
                    "assignment": (
                        "La asignación no pertenece "
                        "al dispositivo."
                    ),
                }
            )

        if (
            self.assignment_id
            and self.assignment.profile_id
            != self.profile_id
        ):
            raise ValidationError(
                {
                    "assignment": (
                        "La asignación utiliza otro perfil."
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

        if self.snmp_port < 1 or self.snmp_port > 65535:
            raise ValidationError(
                {
                    "snmp_port": (
                        "El puerto SNMP debe estar "
                        "entre 1 y 65535."
                    ),
                }
            )

        percentage_fields = [
            "coverage_percent",
            "required_coverage_percent",
            "minimum_coverage_required",
            "minimum_required_coverage",
        ]

        for field_name in percentage_fields:
            value = getattr(
                self,
                field_name,
            )

            if value is not None and (
                value < 0
                or value > 100
            ):
                raise ValidationError(
                    {
                        field_name: (
                            "El porcentaje debe estar "
                            "entre 0 y 100."
                        ),
                    }
                )

        result_counts = (
            self.successful_metric_count
            + self.empty_metric_count
            + self.unsupported_metric_count
            + self.failed_metric_count
        )

        if result_counts > self.tested_metric_count:
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
                        "no pueden superar el total."
                    ),
                }
            )

        if (
            self.failed_required_metric_count
            > self.required_metric_count
        ):
            raise ValidationError(
                {
                    "failed_required_metric_count": (
                        "Las métricas obligatorias fallidas "
                        "no pueden superar el total."
                    ),
                }
            )

        if (
            self.completed_at
            and self.started_at
            and self.completed_at < self.started_at
        ):
            raise ValidationError(
                {
                    "completed_at": (
                        "La finalización no puede ser anterior "
                        "al inicio."
                    ),
                }
            )

        if (
            self.status == self.Status.CANCELLED
            and not self.cancellation_reason
        ):
            raise ValidationError(
                {
                    "cancellation_reason": (
                        "Debe indicar el motivo de cancelación."
                    ),
                }
            )

        if (
            self.status == self.Status.FAILED
            and self.result == self.Result.UNKNOWN
        ):
            raise ValidationError(
                {
                    "result": (
                        "Una prueba fallida requiere "
                        "un resultado definido."
                    ),
                }
            )

        list_fields = [
            "metric_results",
            "successful_oids",
            "failed_oids",
            "unsupported_oids",
            "unknown_oids",
            "warning_messages",
        ]

        for field_name in list_fields:
            if not isinstance(
                getattr(
                    self,
                    field_name,
                ),
                list,
            ):
                raise ValidationError(
                    {
                        field_name: (
                            "Este campo debe ser una lista."
                        ),
                    }
                )

        if not isinstance(
            self.category_summary,
            dict,
        ):
            raise ValidationError(
                {
                    "category_summary": (
                        "El resumen por categoría debe "
                        "ser un objeto."
                    ),
                }
            )

        if not isinstance(
            self.detected_identity,
            dict,
        ):
            raise ValidationError(
                {
                    "detected_identity": (
                        "La identidad detectada debe "
                        "ser un objeto."
                    ),
                }
            )

        self.calculate_duration()
        self.calculate_coverage()

    def save(self, *args, **kwargs):
        if self.device_id:
            self.customer = self.device.customer
            self.branch = self.device.branch
            self.agent = self.device.agent
            self.ip_address = self.device.ip_address
            self.snmp_port = self.device.snmp_port

        if self.profile_id:
            self.profile_code = self.profile.code
            self.profile_version = self.profile.version
            self.profile_revision = self.profile.revision
            self.profile_checksum = self.profile.checksum

            if not self.enabled_metric_count:
                self.enabled_metric_count = (
                    self.profile.metrics.filter(
                        enabled=True,
                        archived_at__isnull=True,
                    ).count()
                )

            if not self.total_metric_count:
                self.total_metric_count = (
                    self.profile.metrics.filter(
                        archived_at__isnull=True,
                    ).count()
                )

        if self.credential_id:
            self.snmp_version = (
                self.credential.snmp_version
            )
            self.snmp_port = self.credential.port

        self.agent_test_id = str(
            self.agent_test_id or ""
        ).strip()

        self.profile_code = str(
            self.profile_code or ""
        ).strip().upper()

        self.calculate_duration()
        self.calculate_coverage()
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
            "Las pruebas históricas de perfiles "
            "no pueden archivarse."
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        raise ValidationError(
            "Las pruebas históricas de perfiles "
            "no pueden restaurarse."
        )