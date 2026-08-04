# -*- coding: utf-8 -*-
import hashlib

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class DeviceAlert(MonitoringBaseModel):
    """
    Alerta histórica detectada mediante SNMP.

    Conserva tanto la clasificación normalizada de Copier OS
    como el mensaje y código original publicado por el fabricante.

    Una misma alerta puede aparecer en varias capturas, pero debe
    mantenerse como un solo evento mientras continúe activa.
    """

    class Category(models.TextChoices):
        PAPER = (
            "paper",
            "Papel",
        )
        JAM = (
            "jam",
            "Atasco",
        )
        TONER = (
            "toner",
            "Tóner",
        )
        CONSUMABLE = (
            "consumable",
            "Consumible",
        )
        COMPONENT = (
            "component",
            "Unidad o componente",
        )
        TRAY = (
            "tray",
            "Bandeja",
        )
        DOOR = (
            "door",
            "Puerta o cubierta",
        )
        FINISHER = (
            "finisher",
            "Finalizador",
        )
        SCANNER = (
            "scanner",
            "Escáner",
        )
        PRINTER = (
            "printer",
            "Impresión",
        )
        FAX = (
            "fax",
            "Fax",
        )
        NETWORK = (
            "network",
            "Red",
        )
        SECURITY = (
            "security",
            "Seguridad",
        )
        MAINTENANCE = (
            "maintenance",
            "Mantenimiento",
        )
        SERVICE = (
            "service",
            "Servicio técnico",
        )
        SYSTEM = (
            "system",
            "Sistema",
        )
        OTHER = (
            "other",
            "Otra",
        )
        UNKNOWN = (
            "unknown",
            "Sin clasificar",
        )

    class Severity(models.TextChoices):
        INFO = (
            "info",
            "Informativa",
        )
        WARNING = (
            "warning",
            "Advertencia",
        )
        ERROR = (
            "error",
            "Error",
        )
        CRITICAL = (
            "critical",
            "Crítica",
        )
        UNKNOWN = (
            "unknown",
            "Desconocida",
        )

    class Status(models.TextChoices):
        ACTIVE = (
            "active",
            "Activa",
        )
        ACKNOWLEDGED = (
            "acknowledged",
            "Reconocida",
        )
        RESOLVED = (
            "resolved",
            "Resuelta",
        )
        CLOSED_AUTOMATIC = (
            "closed_automatic",
            "Cerrada automáticamente",
        )
        CLOSED_MANUAL = (
            "closed_manual",
            "Cerrada manualmente",
        )
        IGNORED = (
            "ignored",
            "Ignorada",
        )

    class SourceType(models.TextChoices):
        STANDARD_MIB = (
            "standard_mib",
            "MIB estándar",
        )
        VENDOR_MIB = (
            "vendor_mib",
            "MIB del fabricante",
        )
        STATUS_DERIVED = (
            "status_derived",
            "Derivada del estado",
        )
        AGENT = (
            "agent",
            "Detectada por el agente",
        )
        MANUAL = (
            "manual",
            "Registro manual",
        )
        UNKNOWN = (
            "unknown",
            "Origen desconocido",
        )

    snapshot = models.ForeignKey(
        "monitoring.DeviceSnapshot",
        on_delete=models.PROTECT,
        related_name="alert_readings",
        verbose_name="Captura de detección",
    )

    last_snapshot = models.ForeignKey(
        "monitoring.DeviceSnapshot",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="last_observed_alerts",
        verbose_name="Última captura observada",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        on_delete=models.PROTECT,
        related_name="alerts",
        verbose_name="Dispositivo",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_alerts",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_alerts",
        verbose_name="Sede",
    )

    equipment_component = models.ForeignKey(
        "equipment.EquipmentComponent",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_alerts",
        verbose_name="Componente relacionado",
    )

    alert_key = models.CharField(
        max_length=64,
        db_index=True,
        editable=False,
        verbose_name="Clave de alerta",
        help_text=(
            "Identifica el mismo evento entre capturas sucesivas."
        ),
    )

    normalized_code = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name="Código normalizado",
        help_text=(
            "Ejemplo: PAPER_JAM, TONER_LOW, "
            "FUSER_REPLACEMENT o SERVICE_CALL."
        ),
    )

    normalized_message = models.CharField(
        max_length=500,
        verbose_name="Mensaje normalizado",
    )

    raw_code = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Código original",
    )

    raw_message = models.TextField(
        blank=True,
        verbose_name="Mensaje original",
    )

    raw_description = models.TextField(
        blank=True,
        verbose_name="Descripción original",
    )

    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.UNKNOWN,
        db_index=True,
        verbose_name="Categoría",
    )

    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.UNKNOWN,
        db_index=True,
        verbose_name="Severidad",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        verbose_name="Estado",
    )

    source_type = models.CharField(
        max_length=30,
        choices=SourceType.choices,
        default=SourceType.UNKNOWN,
        db_index=True,
        verbose_name="Origen",
    )

    component_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código del componente",
    )

    component_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Componente afectado",
    )

    location_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de ubicación",
    )

    location_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Ubicación del problema",
        help_text=(
            "Ejemplo: Bandeja 2, ADF, fusor, dúplex "
            "o salida del finalizador."
        ),
    )

    service_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de servicio",
    )

    vendor_severity_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Severidad original",
    )

    occurred_at = models.DateTimeField(
        db_index=True,
        verbose_name="Fecha de inicio",
    )

    first_detected_at = models.DateTimeField(
        db_index=True,
        verbose_name="Primera detección",
    )

    last_detected_at = models.DateTimeField(
        db_index=True,
        verbose_name="Última detección",
    )

    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de reconocimiento",
    )

    acknowledged_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acknowledged_monitoring_alerts",
        verbose_name="Reconocida por",
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de resolución",
    )

    resolved_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_monitoring_alerts",
        verbose_name="Resuelta por",
    )

    resolution_notes = models.TextField(
        blank=True,
        verbose_name="Notas de resolución",
    )

    occurrence_count = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad de apariciones",
    )

    duration_seconds = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración en segundos",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Activa",
    )

    blocks_printing = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Bloquea impresión",
    )

    blocks_copying = models.BooleanField(
        default=False,
        verbose_name="Bloquea copia",
    )

    blocks_scanning = models.BooleanField(
        default=False,
        verbose_name="Bloquea escaneo",
    )

    requires_user_action = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere acción del usuario",
    )

    requires_technical_visit = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere visita técnica",
    )

    service_order_created = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Servicio generado",
    )

    service_order_reference = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Referencia de servicio",
    )

    notification_sent = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Notificación enviada",
    )

    notification_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de notificación",
    )

    oid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="OID principal",
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

    profile_metric_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Métrica del perfil",
    )

    extra_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Información adicional",
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
        verbose_name = "Alerta de dispositivo"
        verbose_name_plural = "Alertas de dispositivos"
        ordering = (
            "-is_active",
            "-severity",
            "-last_detected_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "is_active",
                    "severity",
                ],
                name="mon_alert_customer_active_idx",
            ),
            models.Index(
                fields=[
                    "branch",
                    "occurred_at",
                ],
                name="mon_alert_branch_date_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "is_active",
                    "last_detected_at",
                ],
                name="mon_alert_device_active_idx",
            ),
            models.Index(
                fields=[
                    "category",
                    "severity",
                    "occurred_at",
                ],
                name="mon_alert_category_date_idx",
            ),
            models.Index(
                fields=[
                    "requires_technical_visit",
                    "service_order_created",
                    "is_active",
                ],
                name="mon_alert_service_idx",
            ),
            models.Index(
                fields=[
                    "service_code",
                    "occurred_at",
                ],
                name="mon_alert_service_code_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "device",
                    "alert_key",
                ],
                condition=models.Q(
                    is_active=True,
                ),
                name="unique_active_device_alert",
            ),
        ]

    def __str__(self):
        return (
            f"{self.device} - "
            f"{self.normalized_message}"
        )

    def calculate_alert_key(self):
        """
        Genera una clave estable para reconocer la misma alerta
        en capturas sucesivas.
        """

        values = [
            str(self.device_id or ""),
            str(self.normalized_code or "").strip().upper(),
            str(self.raw_code or "").strip().upper(),
            str(self.component_code or "").strip().upper(),
            str(self.location_code or "").strip().upper(),
            str(self.service_code or "").strip().upper(),
            str(self.oid_index or "").strip(),
        ]

        return hashlib.sha256(
            "|".join(values).encode("utf-8")
        ).hexdigest()

    def register_reappearance(
        self,
        *,
        snapshot,
        detected_at=None,
        raw_message="",
        raw_value="",
    ):
        """
        Actualiza una alerta que continúa activa.
        """

        detected_at = (
            detected_at
            or snapshot.captured_at
            or timezone.now()
        )

        self.last_snapshot = snapshot
        self.last_detected_at = detected_at
        self.occurrence_count += 1
        self.is_active = True

        if raw_message:
            self.raw_message = str(
                raw_message
            ).strip()

        if raw_value:
            self.raw_value = str(
                raw_value
            ).strip()

        if self.occurred_at:
            duration = (
                detected_at - self.occurred_at
            ).total_seconds()

            self.duration_seconds = max(
                int(duration),
                0,
            )

        self.save(
            update_fields=[
                "last_snapshot",
                "last_detected_at",
                "occurrence_count",
                "is_active",
                "raw_message",
                "raw_value",
                "duration_seconds",
                "updated_at",
            ]
        )

    def acknowledge(
        self,
        *,
        user,
        notes="",
    ):
        if not self.is_active:
            raise ValidationError(
                "Una alerta cerrada no puede reconocerse."
            )

        self.status = self.Status.ACKNOWLEDGED
        self.acknowledged_at = timezone.now()
        self.acknowledged_by = user

        if notes:
            self.notes = str(
                notes
            ).strip()

        self.save(
            update_fields=[
                "status",
                "acknowledged_at",
                "acknowledged_by",
                "notes",
                "updated_at",
            ]
        )

    def resolve(
        self,
        *,
        user=None,
        notes="",
        automatic=False,
        resolved_at=None,
    ):
        """
        Cierra la alerta conservando todo su historial.
        """

        if not self.is_active:
            return self

        resolved_at = (
            resolved_at
            or timezone.now()
        )

        self.is_active = False
        self.resolved_at = resolved_at
        self.resolved_by = user
        self.resolution_notes = str(
            notes or ""
        ).strip()

        self.status = (
            self.Status.CLOSED_AUTOMATIC
            if automatic
            else self.Status.CLOSED_MANUAL
        )

        if self.occurred_at:
            duration = (
                resolved_at - self.occurred_at
            ).total_seconds()

            self.duration_seconds = max(
                int(duration),
                0,
            )

        self.save(
            update_fields=[
                "is_active",
                "status",
                "resolved_at",
                "resolved_by",
                "resolution_notes",
                "duration_seconds",
                "updated_at",
            ]
        )

        return self

    def mark_service_created(
        self,
        reference,
    ):
        self.service_order_created = True
        self.service_order_reference = str(
            reference or ""
        ).strip()

        self.save(
            update_fields=[
                "service_order_created",
                "service_order_reference",
                "updated_at",
            ]
        )

    def mark_notification_sent(self):
        self.notification_sent = True
        self.notification_sent_at = timezone.now()

        self.save(
            update_fields=[
                "notification_sent",
                "notification_sent_at",
                "updated_at",
            ]
        )

    def clean(self):
        super().clean()

        text_fields = [
            "normalized_code",
            "normalized_message",
            "raw_code",
            "raw_message",
            "raw_description",
            "component_code",
            "component_name",
            "location_code",
            "location_name",
            "service_code",
            "vendor_severity_code",
            "resolution_notes",
            "service_order_reference",
            "oid",
            "oid_index",
            "raw_value",
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

        self.normalized_code = (
            self.normalized_code.upper()
        )

        self.raw_code = self.raw_code.upper()
        self.component_code = (
            self.component_code.upper()
        )
        self.location_code = (
            self.location_code.upper()
        )
        self.service_code = (
            self.service_code.upper()
        )

        if not self.snapshot_id:
            raise ValidationError(
                {
                    "snapshot": (
                        "La captura inicial es obligatoria."
                    ),
                }
            )

        if not self.device_id:
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo es obligatorio."
                    ),
                }
            )

        if not self.normalized_code:
            raise ValidationError(
                {
                    "normalized_code": (
                        "El código normalizado es obligatorio."
                    ),
                }
            )

        if not self.normalized_message:
            raise ValidationError(
                {
                    "normalized_message": (
                        "El mensaje normalizado es obligatorio."
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

        if not self.occurred_at:
            raise ValidationError(
                {
                    "occurred_at": (
                        "La fecha de inicio es obligatoria."
                    ),
                }
            )

        if not self.first_detected_at:
            raise ValidationError(
                {
                    "first_detected_at": (
                        "La primera detección es obligatoria."
                    ),
                }
            )

        if not self.last_detected_at:
            raise ValidationError(
                {
                    "last_detected_at": (
                        "La última detección es obligatoria."
                    ),
                }
            )

        if self.last_detected_at < self.first_detected_at:
            raise ValidationError(
                {
                    "last_detected_at": (
                        "La última detección no puede ser anterior "
                        "a la primera."
                    ),
                }
            )

        if (
            self.resolved_at
            and self.resolved_at < self.occurred_at
        ):
            raise ValidationError(
                {
                    "resolved_at": (
                        "La resolución no puede ser anterior "
                        "al inicio de la alerta."
                    ),
                }
            )

        if not self.is_active and not self.resolved_at:
            raise ValidationError(
                {
                    "resolved_at": (
                        "Una alerta cerrada debe registrar "
                        "su fecha de resolución."
                    ),
                }
            )

        if (
            self.requires_technical_visit
            and self.severity == self.Severity.INFO
        ):
            self.severity = self.Severity.WARNING

        self.alert_key = self.calculate_alert_key()

    def save(self, *args, **kwargs):
        if self.snapshot_id:
            self.device = self.snapshot.device
            self.customer = self.snapshot.customer
            self.branch = self.snapshot.branch

            if not self.last_snapshot_id:
                self.last_snapshot = self.snapshot

            if not self.occurred_at:
                self.occurred_at = (
                    self.snapshot.captured_at
                )

            if not self.first_detected_at:
                self.first_detected_at = (
                    self.snapshot.captured_at
                )

            if not self.last_detected_at:
                self.last_detected_at = (
                    self.snapshot.captured_at
                )

        self.normalized_code = str(
            self.normalized_code or ""
        ).strip().upper()

        self.raw_code = str(
            self.raw_code or ""
        ).strip().upper()

        self.component_code = str(
            self.component_code or ""
        ).strip().upper()

        self.location_code = str(
            self.location_code or ""
        ).strip().upper()

        self.service_code = str(
            self.service_code or ""
        ).strip().upper()

        self.alert_key = self.calculate_alert_key()

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
            "Las alertas históricas no pueden archivarse."
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        raise ValidationError(
            "Las alertas históricas no pueden restaurarse."
        )