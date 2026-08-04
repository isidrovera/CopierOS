# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import MonitoringBaseModel


class MonitoringNotificationRule(MonitoringBaseModel):
    """
    Regla configurable para generar notificaciones a partir de eventos,
    alertas y condiciones del módulo de monitoreo.

    Ejemplos:

    - Dispositivo desconectado por varios minutos.
    - Tóner por debajo del porcentaje configurado.
    - Componente próximo a agotarse.
    - Alerta crítica reportada por el equipo.
    - Agente sin sincronización.
    - Cola local acumulada.
    - Fallos consecutivos de consultas SNMP.
    - Poco espacio disponible en el agente.
    """

    class RuleType(models.TextChoices):
        DEVICE_OFFLINE = (
            "device_offline",
            "Dispositivo desconectado",
        )
        DEVICE_ONLINE = (
            "device_online",
            "Dispositivo conectado",
        )
        DEVICE_STATUS = (
            "device_status",
            "Estado del dispositivo",
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
        COMPONENT_LOW = (
            "component_low",
            "Componente con vida baja",
        )
        COMPONENT_REPLACED = (
            "component_replaced",
            "Componente reemplazado",
        )
        DEVICE_ALERT = (
            "device_alert",
            "Alerta del dispositivo",
        )
        COUNTER_THRESHOLD = (
            "counter_threshold",
            "Umbral de contador",
        )
        COUNTER_DECREASED = (
            "counter_decreased",
            "Contador disminuido",
        )
        FIRMWARE_CHANGED = (
            "firmware_changed",
            "Firmware modificado",
        )
        PROFILE_CHANGED = (
            "profile_changed",
            "Perfil SNMP modificado",
        )
        ACCESSORY_CHANGED = (
            "accessory_changed",
            "Accesorio modificado",
        )
        AGENT_OFFLINE = (
            "agent_offline",
            "Agente desconectado",
        )
        AGENT_ERROR = (
            "agent_error",
            "Error del agente",
        )
        AGENT_RESOURCE = (
            "agent_resource",
            "Recursos del agente",
        )
        LOCAL_QUEUE = (
            "local_queue",
            "Cola local acumulada",
        )
        COMMAND_FAILED = (
            "command_failed",
            "Orden del agente fallida",
        )
        SYNC_FAILED = (
            "sync_failed",
            "Sincronización fallida",
        )
        DISCOVERY_FAILED = (
            "discovery_failed",
            "Descubrimiento fallido",
        )
        CUSTOM_EVENT = (
            "custom_event",
            "Evento personalizado",
        )

    class Status(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        ACTIVE = (
            "active",
            "Activa",
        )
        PAUSED = (
            "paused",
            "Pausada",
        )
        DISABLED = (
            "disabled",
            "Deshabilitada",
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

    class ConditionOperator(models.TextChoices):
        EQUALS = (
            "equals",
            "Igual a",
        )
        NOT_EQUALS = (
            "not_equals",
            "Diferente de",
        )
        GREATER_THAN = (
            "greater_than",
            "Mayor que",
        )
        GREATER_THAN_OR_EQUAL = (
            "greater_than_or_equal",
            "Mayor o igual que",
        )
        LESS_THAN = (
            "less_than",
            "Menor que",
        )
        LESS_THAN_OR_EQUAL = (
            "less_than_or_equal",
            "Menor o igual que",
        )
        CONTAINS = (
            "contains",
            "Contiene",
        )
        NOT_CONTAINS = (
            "not_contains",
            "No contiene",
        )
        IN = (
            "in",
            "Está dentro de",
        )
        NOT_IN = (
            "not_in",
            "No está dentro de",
        )
        CHANGED = (
            "changed",
            "Cambió",
        )
        EXISTS = (
            "exists",
            "Existe",
        )
        NOT_EXISTS = (
            "not_exists",
            "No existe",
        )

    class Channel(models.TextChoices):
        IN_APP = (
            "in_app",
            "Copier OS",
        )
        EMAIL = (
            "email",
            "Correo electrónico",
        )
        PUSH = (
            "push",
            "Notificación push",
        )
        WEBHOOK = (
            "webhook",
            "Webhook",
        )

    class RecipientType(models.TextChoices):
        USERS = (
            "users",
            "Usuarios específicos",
        )
        ROLES = (
            "roles",
            "Roles",
        )
        CUSTOMER_ADVISOR = (
            "customer_advisor",
            "Asesora del cliente",
        )
        WORKSHOP_MANAGER = (
            "workshop_manager",
            "Jefe de taller",
        )
        SERVICE_MANAGER = (
            "service_manager",
            "Jefe de servicios",
        )
        TECHNICIAN = (
            "technician",
            "Técnico asignado",
        )
        CUSTOMER_CONTACTS = (
            "customer_contacts",
            "Contactos del cliente",
        )
        CUSTOM_EMAILS = (
            "custom_emails",
            "Correos personalizados",
        )

    class RepeatMode(models.TextChoices):
        ONCE = (
            "once",
            "Una sola vez",
        )
        ON_CHANGE = (
            "on_change",
            "Cuando cambie",
        )
        WHILE_ACTIVE = (
            "while_active",
            "Mientras continúe activa",
        )
        UNTIL_ACKNOWLEDGED = (
            "until_acknowledged",
            "Hasta ser reconocida",
        )
        UNTIL_RESOLVED = (
            "until_resolved",
            "Hasta ser resuelta",
        )

    code = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        verbose_name="Código",
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Nombre",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    rule_type = models.CharField(
        max_length=40,
        choices=RuleType.choices,
        db_index=True,
        verbose_name="Tipo de regla",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.WARNING,
        db_index=True,
        verbose_name="Severidad",
    )

    priority = models.PositiveIntegerField(
        default=100,
        db_index=True,
        verbose_name="Prioridad",
        help_text="Un valor menor tiene mayor prioridad.",
    )

    customer = models.ForeignKey(
        "partners.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_notification_rules",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_notification_rules",
        verbose_name="Sede",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="notification_rules",
        verbose_name="Agente",
    )

    network = models.ForeignKey(
        "monitoring.MonitoringNetwork",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="notification_rules",
        verbose_name="Red",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="notification_rules",
        verbose_name="Dispositivo",
    )

    equipment_brand = models.ForeignKey(
        "equipment.EquipmentBrand",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_notification_rules",
        verbose_name="Marca",
    )

    equipment_model = models.ForeignKey(
        "equipment.EquipmentModel",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_notification_rules",
        verbose_name="Modelo",
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
            "Código del consumible, componente, contador, "
            "alerta o accesorio evaluado."
        ),
    )

    event_types = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Tipos de evento",
    )

    alert_codes = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Códigos de alerta",
    )

    alert_severities = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Severidades de alerta",
    )

    condition_field = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Campo a evaluar",
    )

    condition_operator = models.CharField(
        max_length=30,
        choices=ConditionOperator.choices,
        default=ConditionOperator.EQUALS,
        verbose_name="Operador",
    )

    condition_value = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Valor de condición",
    )

    secondary_conditions = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Condiciones adicionales",
        help_text=(
            "Lista de condiciones combinadas por la capa de servicio."
        ),
    )

    numeric_threshold = models.DecimalField(
        max_digits=40,
        decimal_places=10,
        null=True,
        blank=True,
        verbose_name="Umbral numérico",
    )

    percentage_threshold = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Umbral porcentual",
    )

    duration_threshold_seconds = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración mínima",
        help_text=(
            "Tiempo que debe mantenerse la condición antes "
            "de generar la notificación."
        ),
    )

    occurrence_threshold = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad mínima de ocurrencias",
    )

    occurrence_window_seconds = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Ventana de ocurrencias",
    )

    consecutive_failure_threshold = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Fallos consecutivos",
    )

    offline_threshold_seconds = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Tiempo desconectado",
    )

    queue_item_threshold = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Cantidad máxima en cola",
    )

    queue_age_threshold_seconds = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Antigüedad máxima de cola",
    )

    storage_available_threshold_bytes = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Espacio mínimo disponible",
    )

    cpu_threshold_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Umbral de CPU",
    )

    memory_threshold_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Umbral de memoria",
    )

    disk_threshold_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Umbral de disco",
    )

    channels = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Canales",
        help_text=(
            'Ejemplo: ["in_app", "email"].'
        ),
    )

    recipient_types = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Tipos de destinatario",
    )

    recipient_users = models.ManyToManyField(
        "users.User",
        blank=True,
        related_name="monitoring_notification_rules",
        verbose_name="Usuarios destinatarios",
    )

    recipient_role_codes = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Roles destinatarios",
    )

    recipient_emails = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Correos adicionales",
    )

    recipient_contact_types = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Tipos de contacto del cliente",
    )

    email_subject_template = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Asunto del correo",
    )

    title_template = models.CharField(
        max_length=500,
        verbose_name="Plantilla del título",
    )

    message_template = models.TextField(
        verbose_name="Plantilla del mensaje",
    )

    action_url_template = models.CharField(
        max_length=1000,
        blank=True,
        verbose_name="Enlace de acción",
    )

    webhook_url = models.URLField(
        max_length=1000,
        blank=True,
        verbose_name="URL de webhook",
    )

    webhook_headers = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Cabeceras de webhook",
        help_text=(
            "No deben guardarse tokens o secretos sin cifrar."
        ),
    )

    repeat_mode = models.CharField(
        max_length=30,
        choices=RepeatMode.choices,
        default=RepeatMode.ON_CHANGE,
        verbose_name="Modo de repetición",
    )

    cooldown_seconds = models.PositiveBigIntegerField(
        default=3600,
        verbose_name="Tiempo entre notificaciones",
    )

    repeat_interval_seconds = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Intervalo de repetición",
    )

    maximum_notifications = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Máximo de notificaciones",
    )

    auto_resolve = models.BooleanField(
        default=True,
        verbose_name="Resolver automáticamente",
    )

    require_acknowledgement = models.BooleanField(
        default=False,
        verbose_name="Requiere reconocimiento",
    )

    create_device_event = models.BooleanField(
        default=True,
        verbose_name="Crear evento de dispositivo",
    )

    create_device_alert = models.BooleanField(
        default=False,
        verbose_name="Crear alerta interna",
    )

    notify_on_resolution = models.BooleanField(
        default=False,
        verbose_name="Notificar resolución",
    )

    resolution_title_template = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Título de resolución",
    )

    resolution_message_template = models.TextField(
        blank=True,
        verbose_name="Mensaje de resolución",
    )

    active_days = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Días activos",
        help_text=(
            "Valores ISO: 1 para lunes y 7 para domingo. "
            "Lista vacía significa todos los días."
        ),
    )

    active_time_start = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora de inicio",
    )

    active_time_end = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora de fin",
    )

    respect_business_hours = models.BooleanField(
        default=True,
        verbose_name="Respetar horario laboral",
    )

    notify_outside_business_hours = models.BooleanField(
        default=False,
        verbose_name="Notificar fuera de horario",
    )

    notify_on_weekends = models.BooleanField(
        default=False,
        verbose_name="Notificar fines de semana",
    )

    timezone_name = models.CharField(
        max_length=100,
        default="America/Lima",
        verbose_name="Zona horaria",
    )

    suppress_when_no_customer = models.BooleanField(
        default=True,
        verbose_name="No notificar sin cliente",
    )

    minimum_device_age_seconds = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Antigüedad mínima del dispositivo",
        help_text=(
            "Evita alertas inmediatas sobre dispositivos "
            "recién descubiertos."
        ),
    )

    evaluation_interval_seconds = models.PositiveIntegerField(
        default=300,
        verbose_name="Intervalo de evaluación",
    )

    last_evaluated_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Última evaluación",
    )

    last_triggered_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Última activación",
    )

    trigger_count = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Cantidad de activaciones",
    )

    notification_count = models.PositiveBigIntegerField(
        default=0,
        verbose_name="Notificaciones generadas",
    )

    last_error_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha del último error",
    )

    last_error_message = models.TextField(
        blank=True,
        verbose_name="Último error",
    )

    condition_config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Configuración de condición",
    )

    notification_config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Configuración de notificación",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Regla de notificación de monitoreo"
        verbose_name_plural = "Reglas de notificación de monitoreo"
        ordering = (
            "priority",
            "name",
        )
        indexes = [
            models.Index(
                fields=[
                    "status",
                    "rule_type",
                    "priority",
                ],
                name="mon_nrule_status_type_idx",
            ),
            models.Index(
                fields=[
                    "customer",
                    "branch",
                    "status",
                ],
                name="mon_nrule_customer_idx",
            ),
            models.Index(
                fields=[
                    "agent",
                    "status",
                    "rule_type",
                ],
                name="mon_nrule_agent_type_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "status",
                    "priority",
                ],
                name="mon_nrule_device_idx",
            ),
            models.Index(
                fields=[
                    "metric_code",
                    "entity_code",
                    "status",
                ],
                name="mon_nrule_metric_entity_idx",
            ),
            models.Index(
                fields=[
                    "last_evaluated_at",
                    "status",
                ],
                name="mon_nrule_evaluation_idx",
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def is_active_now(
        self,
        *,
        current_datetime=None,
    ):
        """
        Determina si la regla puede evaluarse en el momento indicado.

        La validación completa del horario laboral deberá realizarse
        desde un servicio que conozca el calendario de la empresa.
        """

        if self.status != self.Status.ACTIVE:
            return False

        current_datetime = (
            current_datetime
            or timezone.localtime()
        )

        weekday = current_datetime.isoweekday()

        if self.active_days:
            allowed_days = {
                int(day)
                for day in self.active_days
            }

            if weekday not in allowed_days:
                return False

        if (
            not self.notify_on_weekends
            and weekday in {
                6,
                7,
            }
        ):
            return False

        current_time = current_datetime.time()

        if (
            self.active_time_start
            and self.active_time_end
        ):
            if (
                self.active_time_start
                <= self.active_time_end
            ):
                if not (
                    self.active_time_start
                    <= current_time
                    <= self.active_time_end
                ):
                    return False
            else:
                if not (
                    current_time
                    >= self.active_time_start
                    or current_time
                    <= self.active_time_end
                ):
                    return False

        return True

    def can_trigger(
        self,
        *,
        current_datetime=None,
    ):
        current_datetime = (
            current_datetime
            or timezone.now()
        )

        if not self.is_active_now(
            current_datetime=timezone.localtime(
                current_datetime
            ),
        ):
            return False

        if not self.last_triggered_at:
            return True

        elapsed_seconds = (
            current_datetime
            - self.last_triggered_at
        ).total_seconds()

        return elapsed_seconds >= self.cooldown_seconds

    def register_evaluation(self):
        self.last_evaluated_at = timezone.now()

        self.save(
            update_fields=[
                "last_evaluated_at",
                "updated_at",
            ]
        )

    def register_trigger(
        self,
        *,
        notification_count=1,
    ):
        now = timezone.now()

        self.last_evaluated_at = now
        self.last_triggered_at = now
        self.trigger_count += 1
        self.notification_count += max(
            int(notification_count or 0),
            0,
        )
        self.last_error_at = None
        self.last_error_message = ""

        self.save(
            update_fields=[
                "last_evaluated_at",
                "last_triggered_at",
                "trigger_count",
                "notification_count",
                "last_error_at",
                "last_error_message",
                "updated_at",
            ]
        )

    def register_error(
        self,
        error_message,
    ):
        self.last_evaluated_at = timezone.now()
        self.last_error_at = self.last_evaluated_at
        self.last_error_message = str(
            error_message or ""
        ).strip()

        self.save(
            update_fields=[
                "last_evaluated_at",
                "last_error_at",
                "last_error_message",
                "updated_at",
            ]
        )

    def activate(self):
        self.status = self.Status.ACTIVE
        self.last_error_at = None
        self.last_error_message = ""

        self.save(
            update_fields=[
                "status",
                "last_error_at",
                "last_error_message",
                "updated_at",
            ]
        )

    def pause(self):
        self.status = self.Status.PAUSED

        self.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    def disable(self):
        self.status = self.Status.DISABLED

        self.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    def clean(self):
        super().clean()

        text_fields = [
            "code",
            "name",
            "description",
            "metric_code",
            "entity_code",
            "condition_field",
            "email_subject_template",
            "title_template",
            "message_template",
            "action_url_template",
            "webhook_url",
            "resolution_title_template",
            "resolution_message_template",
            "timezone_name",
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

        self.code = self.code.upper()
        self.metric_code = self.metric_code.upper()
        self.entity_code = self.entity_code.upper()

        if not self.code:
            raise ValidationError(
                {
                    "code": "El código es obligatorio.",
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": "El nombre es obligatorio.",
                }
            )

        if not self.title_template:
            raise ValidationError(
                {
                    "title_template": (
                        "La plantilla del título es obligatoria."
                    ),
                }
            )

        if not self.message_template:
            raise ValidationError(
                {
                    "message_template": (
                        "La plantilla del mensaje es obligatoria."
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
            self.agent_id
            and self.customer_id
            and self.agent.customer_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "agent": (
                        "El agente no pertenece al cliente."
                    ),
                }
            )

        if (
            self.network_id
            and self.agent_id
            and self.network.agent_id
            != self.agent_id
        ):
            raise ValidationError(
                {
                    "network": (
                        "La red no pertenece al agente."
                    ),
                }
            )

        if (
            self.device_id
            and self.customer_id
            and self.device.customer_id
            != self.customer_id
        ):
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo no pertenece al cliente."
                    ),
                }
            )

        if (
            self.device_id
            and self.agent_id
            and self.device.agent_id
            != self.agent_id
        ):
            raise ValidationError(
                {
                    "device": (
                        "El dispositivo no pertenece al agente."
                    ),
                }
            )

        percentage_fields = [
            "percentage_threshold",
            "cpu_threshold_percent",
            "memory_threshold_percent",
            "disk_threshold_percent",
        ]

        for field_name in percentage_fields:
            value = getattr(
                self,
                field_name,
            )

            if value is not None and (
                value < Decimal("0")
                or value > Decimal("100")
            ):
                raise ValidationError(
                    {
                        field_name: (
                            "El porcentaje debe estar "
                            "entre 0 y 100."
                        ),
                    }
                )

        if self.occurrence_threshold < 1:
            raise ValidationError(
                {
                    "occurrence_threshold": (
                        "Debe requerirse al menos una ocurrencia."
                    ),
                }
            )

        if self.evaluation_interval_seconds < 30:
            raise ValidationError(
                {
                    "evaluation_interval_seconds": (
                        "El intervalo de evaluación debe ser "
                        "como mínimo de 30 segundos."
                    ),
                }
            )

        if (
            self.repeat_mode
            in {
                self.RepeatMode.WHILE_ACTIVE,
                self.RepeatMode.UNTIL_ACKNOWLEDGED,
                self.RepeatMode.UNTIL_RESOLVED,
            }
            and not self.repeat_interval_seconds
        ):
            raise ValidationError(
                {
                    "repeat_interval_seconds": (
                        "El modo de repetición seleccionado "
                        "requiere un intervalo."
                    ),
                }
            )

        allowed_channels = {
            choice[0]
            for choice in self.Channel.choices
        }

        invalid_channels = [
            channel
            for channel in self.channels
            if channel not in allowed_channels
        ]

        if invalid_channels:
            raise ValidationError(
                {
                    "channels": (
                        "Existen canales de notificación no válidos."
                    ),
                }
            )

        if not self.channels:
            raise ValidationError(
                {
                    "channels": (
                        "Debe seleccionar al menos un canal."
                    ),
                }
            )

        if (
            self.Channel.EMAIL in self.channels
            and not self.email_subject_template
        ):
            raise ValidationError(
                {
                    "email_subject_template": (
                        "El correo requiere una plantilla de asunto."
                    ),
                }
            )

        if (
            self.Channel.WEBHOOK in self.channels
            and not self.webhook_url
        ):
            raise ValidationError(
                {
                    "webhook_url": (
                        "El canal webhook requiere una URL."
                    ),
                }
            )

        allowed_recipient_types = {
            choice[0]
            for choice in self.RecipientType.choices
        }

        invalid_recipient_types = [
            recipient_type
            for recipient_type in self.recipient_types
            if recipient_type not in allowed_recipient_types
        ]

        if invalid_recipient_types:
            raise ValidationError(
                {
                    "recipient_types": (
                        "Existen tipos de destinatario no válidos."
                    ),
                }
            )

        if (
            self.RecipientType.CUSTOM_EMAILS
            in self.recipient_types
            and not self.recipient_emails
        ):
            raise ValidationError(
                {
                    "recipient_emails": (
                        "Debe registrar al menos un correo "
                        "personalizado."
                    ),
                }
            )

        if (
            self.active_time_start
            and not self.active_time_end
        ):
            raise ValidationError(
                {
                    "active_time_end": (
                        "Debe indicar la hora final."
                    ),
                }
            )

        if (
            self.active_time_end
            and not self.active_time_start
        ):
            raise ValidationError(
                {
                    "active_time_start": (
                        "Debe indicar la hora inicial."
                    ),
                }
            )

        invalid_days = [
            day
            for day in self.active_days
            if not str(day).isdigit()
            or int(day) < 1
            or int(day) > 7
        ]

        if invalid_days:
            raise ValidationError(
                {
                    "active_days": (
                        "Los días deben estar entre 1 y 7."
                    ),
                }
            )

        list_fields = [
            "event_types",
            "alert_codes",
            "alert_severities",
            "secondary_conditions",
            "channels",
            "recipient_types",
            "recipient_role_codes",
            "recipient_emails",
            "recipient_contact_types",
            "active_days",
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

        dict_fields = [
            "webhook_headers",
            "condition_config",
            "notification_config",
            "metadata",
        ]

        for field_name in dict_fields:
            if not isinstance(
                getattr(
                    self,
                    field_name,
                ),
                dict,
            ):
                raise ValidationError(
                    {
                        field_name: (
                            "Este campo debe ser un objeto."
                        ),
                    }
                )

        rule_requirements = {
            self.RuleType.DEVICE_OFFLINE: (
                "offline_threshold_seconds",
                self.offline_threshold_seconds,
            ),
            self.RuleType.CONSUMABLE_LOW: (
                "percentage_threshold",
                self.percentage_threshold,
            ),
            self.RuleType.COMPONENT_LOW: (
                "percentage_threshold",
                self.percentage_threshold,
            ),
            self.RuleType.COUNTER_THRESHOLD: (
                "numeric_threshold",
                self.numeric_threshold,
            ),
            self.RuleType.LOCAL_QUEUE: (
                "queue_item_threshold",
                self.queue_item_threshold,
            ),
        }

        requirement = rule_requirements.get(
            self.rule_type
        )

        if requirement:
            field_name, value = requirement

            if value is None:
                raise ValidationError(
                    {
                        field_name: (
                            "Este campo es obligatorio para "
                            "el tipo de regla seleccionado."
                        ),
                    }
                )

    def save(self, *args, **kwargs):
        self.code = str(
            self.code or ""
        ).strip().upper()

        self.metric_code = str(
            self.metric_code or ""
        ).strip().upper()

        self.entity_code = str(
            self.entity_code or ""
        ).strip().upper()

        self.channels = [
            str(channel).strip().lower()
            for channel in (
                self.channels
                or []
            )
            if str(channel).strip()
        ]

        self.recipient_types = [
            str(recipient_type).strip().lower()
            for recipient_type in (
                self.recipient_types
                or []
            )
            if str(recipient_type).strip()
        ]

        self.active_days = [
            int(day)
            for day in (
                self.active_days
                or []
            )
            if str(day).isdigit()
        ]

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )