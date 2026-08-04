# -*- coding: utf-8 -*-
import hashlib
import json
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class DeviceEvent(MonitoringBaseModel):
    """
    Evento histórico generado al detectar un cambio relevante
    entre capturas de un dispositivo.

    Ejemplos:

    - Equipo conectado o desconectado.
    - Cambio de dirección IP.
    - Cambio de firmware.
    - Cambio de serie, modelo o identidad.
    - Cambio de perfil SNMP.
    - Cambio de estado operativo.
    - Instalación o retiro de accesorios.
    - Reemplazo de consumibles o componentes.
    - Reinicio del equipo.
    - Reinicio o disminución de contadores.
    """

    class EventCategory(models.TextChoices):
        CONNECTIVITY = (
            "connectivity",
            "Conectividad",
        )
        NETWORK = (
            "network",
            "Red",
        )
        IDENTITY = (
            "identity",
            "Identidad",
        )
        FIRMWARE = (
            "firmware",
            "Firmware",
        )
        PROFILE = (
            "profile",
            "Perfil SNMP",
        )
        STATUS = (
            "status",
            "Estado operativo",
        )
        COUNTER = (
            "counter",
            "Contador",
        )
        CONSUMABLE = (
            "consumable",
            "Consumible",
        )
        COMPONENT = (
            "component",
            "Componente",
        )
        ACCESSORY = (
            "accessory",
            "Accesorio",
        )
        TRAY = (
            "tray",
            "Bandeja",
        )
        ALERT = (
            "alert",
            "Alerta",
        )
        JOB = (
            "job",
            "Trabajo",
        )
        CONFIGURATION = (
            "configuration",
            "Configuración",
        )
        AGENT = (
            "agent",
            "Agente",
        )
        OTHER = (
            "other",
            "Otro",
        )

    class EventType(models.TextChoices):
        DEVICE_ONLINE = (
            "device_online",
            "Dispositivo conectado",
        )
        DEVICE_OFFLINE = (
            "device_offline",
            "Dispositivo desconectado",
        )
        DEVICE_RESTORED = (
            "device_restored",
            "Conexión restablecida",
        )
        IP_CHANGED = (
            "ip_changed",
            "Dirección IP modificada",
        )
        MAC_CHANGED = (
            "mac_changed",
            "Dirección MAC modificada",
        )
        HOSTNAME_CHANGED = (
            "hostname_changed",
            "Hostname modificado",
        )
        LOCATION_CHANGED = (
            "location_changed",
            "Ubicación modificada",
        )
        SERIAL_CHANGED = (
            "serial_changed",
            "Serie modificada",
        )
        MODEL_CHANGED = (
            "model_changed",
            "Modelo modificado",
        )
        BRAND_CHANGED = (
            "brand_changed",
            "Marca modificada",
        )
        SYS_OBJECT_ID_CHANGED = (
            "sys_object_id_changed",
            "SysObjectID modificado",
        )
        FIRMWARE_CHANGED = (
            "firmware_changed",
            "Firmware modificado",
        )
        PROFILE_ASSIGNED = (
            "profile_assigned",
            "Perfil asignado",
        )
        PROFILE_CHANGED = (
            "profile_changed",
            "Perfil modificado",
        )
        PROFILE_REMOVED = (
            "profile_removed",
            "Perfil retirado",
        )
        OPERATIONAL_STATUS_CHANGED = (
            "operational_status_changed",
            "Estado operativo modificado",
        )
        DEVICE_RESTARTED = (
            "device_restarted",
            "Dispositivo reiniciado",
        )
        COUNTER_INCREASED = (
            "counter_increased",
            "Contador incrementado",
        )
        COUNTER_DECREASED = (
            "counter_decreased",
            "Contador disminuido",
        )
        COUNTER_RESET = (
            "counter_reset",
            "Contador reiniciado",
        )
        CONSUMABLE_LEVEL_CHANGED = (
            "consumable_level_changed",
            "Nivel de consumible modificado",
        )
        CONSUMABLE_LOW = (
            "consumable_low",
            "Consumible bajo",
        )
        CONSUMABLE_EMPTY = (
            "consumable_empty",
            "Consumible vacío",
        )
        CONSUMABLE_REPLACED = (
            "consumable_replaced",
            "Consumible reemplazado",
        )
        COMPONENT_LEVEL_CHANGED = (
            "component_level_changed",
            "Vida de componente modificada",
        )
        COMPONENT_LOW = (
            "component_low",
            "Componente con vida baja",
        )
        COMPONENT_REPLACED = (
            "component_replaced",
            "Componente reemplazado",
        )
        ACCESSORY_INSTALLED = (
            "accessory_installed",
            "Accesorio instalado",
        )
        ACCESSORY_REMOVED = (
            "accessory_removed",
            "Accesorio retirado",
        )
        ACCESSORY_STATUS_CHANGED = (
            "accessory_status_changed",
            "Estado de accesorio modificado",
        )
        TRAY_STATUS_CHANGED = (
            "tray_status_changed",
            "Estado de bandeja modificado",
        )
        ALERT_OPENED = (
            "alert_opened",
            "Alerta iniciada",
        )
        ALERT_RESOLVED = (
            "alert_resolved",
            "Alerta resuelta",
        )
        CONFIGURATION_CHANGED = (
            "configuration_changed",
            "Configuración modificada",
        )
        AGENT_CHANGED = (
            "agent_changed",
            "Agente modificado",
        )
        EQUIPMENT_LINKED = (
            "equipment_linked",
            "Equipo vinculado",
        )
        EQUIPMENT_UNLINKED = (
            "equipment_unlinked",
            "Equipo desvinculado",
        )
        CUSTOM = (
            "custom",
            "Evento personalizado",
        )

    class Severity(models.TextChoices):
        INFO = (
            "info",
            "Informativa",
        )
        NOTICE = (
            "notice",
            "Aviso",
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

    class SourceType(models.TextChoices):
        SNAPSHOT_COMPARISON = (
            "snapshot_comparison",
            "Comparación de capturas",
        )
        DISCOVERY = (
            "discovery",
            "Descubrimiento",
        )
        ALERT = (
            "alert",
            "Alerta",
        )
        PROFILE_ASSIGNMENT = (
            "profile_assignment",
            "Asignación de perfil",
        )
        AGENT = (
            "agent",
            "Agente",
        )
        MANUAL = (
            "manual",
            "Manual",
        )
        SYSTEM = (
            "system",
            "Sistema",
        )

    class ProcessingStatus(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        PROCESSED = (
            "processed",
            "Procesado",
        )
        NOTIFIED = (
            "notified",
            "Notificado",
        )
        IGNORED = (
            "ignored",
            "Ignorado",
        )
        ERROR = (
            "error",
            "Con error",
        )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        on_delete=models.PROTECT,
        related_name="events",
        verbose_name="Dispositivo",
    )

    snapshot = models.ForeignKey(
        "monitoring.DeviceSnapshot",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="device_events",
        verbose_name="Captura actual",
    )

    previous_snapshot = models.ForeignKey(
        "monitoring.DeviceSnapshot",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="subsequent_device_events",
        verbose_name="Captura anterior",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        on_delete=models.PROTECT,
        related_name="monitoring_device_events",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_device_events",
        verbose_name="Sede",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        on_delete=models.PROTECT,
        related_name="device_events",
        verbose_name="Agente",
    )

    alert = models.ForeignKey(
        "monitoring.DeviceAlert",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="device_events",
        verbose_name="Alerta relacionada",
    )

    profile_assignment = models.ForeignKey(
        "monitoring.DeviceProfileAssignment",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="device_events",
        verbose_name="Asignación de perfil relacionada",
    )

    event_key = models.CharField(
        max_length=64,
        db_index=True,
        editable=False,
        verbose_name="Clave del evento",
    )

    category = models.CharField(
        max_length=30,
        choices=EventCategory.choices,
        default=EventCategory.OTHER,
        db_index=True,
        verbose_name="Categoría",
    )

    event_type = models.CharField(
        max_length=50,
        choices=EventType.choices,
        db_index=True,
        verbose_name="Tipo de evento",
    )

    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.INFO,
        db_index=True,
        verbose_name="Severidad",
    )

    source_type = models.CharField(
        max_length=30,
        choices=SourceType.choices,
        default=SourceType.SNAPSHOT_COMPARISON,
        db_index=True,
        verbose_name="Origen",
    )

    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
        db_index=True,
        verbose_name="Estado de procesamiento",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Título",
    )

    message = models.TextField(
        verbose_name="Mensaje",
    )

    metric_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de métrica",
    )

    entity_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de entidad",
        help_text=(
            "Identificador del contador, consumible, componente, "
            "bandeja, accesorio o alerta relacionada."
        ),
    )

    entity_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre de entidad",
    )

    field_name = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Campo modificado",
    )

    old_value = models.TextField(
        blank=True,
        verbose_name="Valor anterior",
    )

    new_value = models.TextField(
        blank=True,
        verbose_name="Valor nuevo",
    )

    old_numeric_value = models.DecimalField(
        max_digits=40,
        decimal_places=10,
        null=True,
        blank=True,
        verbose_name="Valor numérico anterior",
    )

    new_numeric_value = models.DecimalField(
        max_digits=40,
        decimal_places=10,
        null=True,
        blank=True,
        verbose_name="Valor numérico nuevo",
    )

    delta_numeric_value = models.DecimalField(
        max_digits=40,
        decimal_places=10,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Variación numérica",
    )

    old_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Porcentaje anterior",
    )

    new_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Porcentaje nuevo",
    )

    delta_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Variación porcentual",
    )

    occurred_at = models.DateTimeField(
        db_index=True,
        verbose_name="Fecha del evento",
    )

    detected_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de detección",
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de procesamiento",
    )

    notified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de notificación",
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
        related_name="acknowledged_device_events",
        verbose_name="Reconocido por",
    )

    requires_notification = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere notificación",
    )

    notification_sent = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Notificación enviada",
    )

    requires_user_action = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere acción del usuario",
    )

    requires_technical_action = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere acción técnica",
    )

    creates_alert = models.BooleanField(
        default=False,
        verbose_name="Genera alerta",
    )

    is_acknowledged = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Reconocido",
    )

    is_duplicate = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Evento duplicado",
    )

    duplicate_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="duplicate_events",
        verbose_name="Duplicado de",
    )

    confidence_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("100.00"),
        verbose_name="Confianza",
    )

    comparison_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos de comparación",
    )

    source_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos de origen",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos",
    )

    error_message = models.TextField(
        blank=True,
        verbose_name="Error de procesamiento",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Evento de dispositivo"
        verbose_name_plural = "Eventos de dispositivos"
        ordering = (
            "-occurred_at",
            "-detected_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "device",
                    "occurred_at",
                    "event_type",
                ],
                name="mon_event_device_date_idx",
            ),
            models.Index(
                fields=[
                    "customer",
                    "category",
                    "occurred_at",
                ],
                name="mon_event_customer_cat_idx",
            ),
            models.Index(
                fields=[
                    "branch",
                    "severity",
                    "occurred_at",
                ],
                name="mon_event_branch_severity_idx",
            ),
            models.Index(
                fields=[
                    "processing_status",
                    "requires_notification",
                    "detected_at",
                ],
                name="mon_event_processing_idx",
            ),
            models.Index(
                fields=[
                    "entity_code",
                    "metric_code",
                    "occurred_at",
                ],
                name="mon_event_entity_metric_idx",
            ),
            models.Index(
                fields=[
                    "requires_technical_action",
                    "severity",
                    "occurred_at",
                ],
                name="mon_event_technical_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "device",
                    "snapshot",
                    "event_key",
                ],
                condition=models.Q(
                    snapshot__isnull=False,
                ),
                name="unique_snapshot_device_event",
            ),
        ]

    def __str__(self):
        return (
            f"{self.device} - "
            f"{self.title}"
        )

    @staticmethod
    def normalize_hash_value(value):
        if value is None:
            return ""

        if isinstance(
            value,
            (
                dict,
                list,
                tuple,
            ),
        ):
            return json.dumps(
                value,
                sort_keys=True,
                ensure_ascii=False,
                default=str,
            )

        return str(value).strip()

    def calculate_event_key(self):
        values = [
            str(self.device_id or ""),
            str(self.event_type or ""),
            str(self.metric_code or "").strip().upper(),
            str(self.entity_code or "").strip().upper(),
            str(self.field_name or "").strip(),
            self.normalize_hash_value(self.old_value),
            self.normalize_hash_value(self.new_value),
            str(self.occurred_at or ""),
        ]

        return hashlib.sha256(
            "|".join(values).encode("utf-8")
        ).hexdigest()

    def calculate_deltas(self):
        if (
            self.old_numeric_value is not None
            and self.new_numeric_value is not None
        ):
            self.delta_numeric_value = (
                self.new_numeric_value
                - self.old_numeric_value
            )
        else:
            self.delta_numeric_value = None

        if (
            self.old_percentage is not None
            and self.new_percentage is not None
        ):
            self.delta_percentage = (
                self.new_percentage
                - self.old_percentage
            )
        else:
            self.delta_percentage = None

    def acknowledge(
        self,
        *,
        user,
        notes="",
    ):
        self.is_acknowledged = True
        self.acknowledged_at = timezone.now()
        self.acknowledged_by = user

        if notes:
            self.notes = str(
                notes
            ).strip()

        self.save(
            update_fields=[
                "is_acknowledged",
                "acknowledged_at",
                "acknowledged_by",
                "notes",
                "updated_at",
            ]
        )

    def mark_processed(self):
        self.processing_status = (
            self.ProcessingStatus.PROCESSED
        )
        self.processed_at = timezone.now()
        self.error_message = ""

        self.save(
            update_fields=[
                "processing_status",
                "processed_at",
                "error_message",
                "updated_at",
            ]
        )

    def mark_notified(self):
        self.processing_status = (
            self.ProcessingStatus.NOTIFIED
        )
        self.notification_sent = True
        self.notified_at = timezone.now()

        self.save(
            update_fields=[
                "processing_status",
                "notification_sent",
                "notified_at",
                "updated_at",
            ]
        )

    def mark_ignored(
        self,
        reason="",
    ):
        self.processing_status = (
            self.ProcessingStatus.IGNORED
        )

        if reason:
            self.notes = str(
                reason
            ).strip()

        self.save(
            update_fields=[
                "processing_status",
                "notes",
                "updated_at",
            ]
        )

    def mark_error(
        self,
        error_message,
    ):
        self.processing_status = (
            self.ProcessingStatus.ERROR
        )
        self.error_message = str(
            error_message or ""
        ).strip()

        self.save(
            update_fields=[
                "processing_status",
                "error_message",
                "updated_at",
            ]
        )

    def mark_duplicate(
        self,
        original_event,
    ):
        if original_event.device_id != self.device_id:
            raise ValidationError(
                "El evento original pertenece a otro dispositivo."
            )

        self.is_duplicate = True
        self.duplicate_of = original_event
        self.processing_status = (
            self.ProcessingStatus.IGNORED
        )

        self.save(
            update_fields=[
                "is_duplicate",
                "duplicate_of",
                "processing_status",
                "updated_at",
            ]
        )

    def clean(self):
        super().clean()

        text_fields = [
            "title",
            "message",
            "metric_code",
            "entity_code",
            "entity_name",
            "field_name",
            "old_value",
            "new_value",
            "error_message",
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

        self.metric_code = self.metric_code.upper()
        self.entity_code = self.entity_code.upper()

        if not self.device_id:
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo es obligatorio."
                    ),
                }
            )

        if not self.event_type:
            raise ValidationError(
                {
                    "event_type": (
                        "El tipo de evento es obligatorio."
                    ),
                }
            )

        if not self.title:
            raise ValidationError(
                {
                    "title": (
                        "El título del evento es obligatorio."
                    ),
                }
            )

        if not self.message:
            raise ValidationError(
                {
                    "message": (
                        "El mensaje del evento es obligatorio."
                    ),
                }
            )

        if not self.occurred_at:
            raise ValidationError(
                {
                    "occurred_at": (
                        "La fecha del evento es obligatoria."
                    ),
                }
            )

        if self.device.customer_id != self.customer_id:
            raise ValidationError(
                {
                    "customer": (
                        "El cliente no coincide con el dispositivo."
                    ),
                }
            )

        if self.device.agent_id != self.agent_id:
            raise ValidationError(
                {
                    "agent": (
                        "El agente no coincide con el dispositivo."
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
            self.snapshot_id
            and self.snapshot.device_id
            != self.device_id
        ):
            raise ValidationError(
                {
                    "snapshot": (
                        "La captura no pertenece al dispositivo."
                    ),
                }
            )

        if (
            self.previous_snapshot_id
            and self.previous_snapshot.device_id
            != self.device_id
        ):
            raise ValidationError(
                {
                    "previous_snapshot": (
                        "La captura anterior no pertenece "
                        "al dispositivo."
                    ),
                }
            )

        if (
            self.snapshot_id
            and self.previous_snapshot_id
            and self.previous_snapshot.captured_at
            > self.snapshot.captured_at
        ):
            raise ValidationError(
                {
                    "previous_snapshot": (
                        "La captura anterior no puede ser posterior "
                        "a la captura actual."
                    ),
                }
            )

        if (
            self.alert_id
            and self.alert.device_id
            != self.device_id
        ):
            raise ValidationError(
                {
                    "alert": (
                        "La alerta no pertenece al dispositivo."
                    ),
                }
            )

        if (
            self.profile_assignment_id
            and self.profile_assignment.device_id
            != self.device_id
        ):
            raise ValidationError(
                {
                    "profile_assignment": (
                        "La asignación de perfil no pertenece "
                        "al dispositivo."
                    ),
                }
            )

        if (
            self.duplicate_of_id
            and self.duplicate_of_id == self.id
        ):
            raise ValidationError(
                {
                    "duplicate_of": (
                        "Un evento no puede ser duplicado "
                        "de sí mismo."
                    ),
                }
            )

        if (
            self.is_duplicate
            and not self.duplicate_of_id
        ):
            raise ValidationError(
                {
                    "duplicate_of": (
                        "Debe indicar el evento original."
                    ),
                }
            )

        if (
            not self.is_duplicate
            and self.duplicate_of_id
        ):
            raise ValidationError(
                {
                    "is_duplicate": (
                        "Debe marcar el evento como duplicado."
                    ),
                }
            )

        percentage_fields = [
            "old_percentage",
            "new_percentage",
            "confidence_percent",
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

        if (
            self.notification_sent
            and not self.notified_at
        ):
            raise ValidationError(
                {
                    "notified_at": (
                        "Debe registrar la fecha de notificación."
                    ),
                }
            )

        if (
            self.is_acknowledged
            and not self.acknowledged_at
        ):
            raise ValidationError(
                {
                    "acknowledged_at": (
                        "Debe registrar la fecha de reconocimiento."
                    ),
                }
            )

        if not isinstance(
            self.comparison_data,
            dict,
        ):
            raise ValidationError(
                {
                    "comparison_data": (
                        "Los datos de comparación deben "
                        "ser un objeto."
                    ),
                }
            )

        if not isinstance(
            self.source_data,
            dict,
        ):
            raise ValidationError(
                {
                    "source_data": (
                        "Los datos de origen deben ser un objeto."
                    ),
                }
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValidationError(
                {
                    "metadata": (
                        "Los metadatos deben ser un objeto."
                    ),
                }
            )

        self.calculate_deltas()
        self.event_key = self.calculate_event_key()

    def save(self, *args, **kwargs):
        if self.device_id:
            self.customer = self.device.customer
            self.branch = self.device.branch
            self.agent = self.device.agent

        if self.snapshot_id and not self.occurred_at:
            self.occurred_at = self.snapshot.captured_at

        self.metric_code = str(
            self.metric_code or ""
        ).strip().upper()

        self.entity_code = str(
            self.entity_code or ""
        ).strip().upper()

        self.calculate_deltas()
        self.event_key = self.calculate_event_key()
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
            "Los eventos históricos no pueden archivarse."
        )

    def restore(
        self,
        user=None,
        save=True,
    ):
        raise ValidationError(
            "Los eventos históricos no pueden restaurarse."
        )