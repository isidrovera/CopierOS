# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from .base import MonitoringBaseModel


class SNMPProfile(MonitoringBaseModel):
    """
    Perfil SNMP para identificar, consultar y normalizar dispositivos.

    Un perfil puede aplicarse por:

    - Fabricante.
    - Marca registrada en Copier OS.
    - Familia de equipos.
    - Modelo específico.
    - SysObjectID exacto o por prefijo.
    - Número enterprise.
    - Versión o patrón de firmware.
    - Cliente, sede, agente o dispositivo específico.

    La selección definitiva debe realizarse en una capa de servicio
    respetando prioridad, alcance y coincidencia.
    """

    class Scope(models.TextChoices):
        GLOBAL = (
            "global",
            "Global",
        )
        CUSTOMER = (
            "customer",
            "Cliente",
        )
        BRANCH = (
            "branch",
            "Sede",
        )
        AGENT = (
            "agent",
            "Agente",
        )
        DEVICE = (
            "device",
            "Dispositivo",
        )

    class MatchMode(models.TextChoices):
        GENERIC = (
            "generic",
            "Genérico",
        )
        ENTERPRISE = (
            "enterprise",
            "Enterprise",
        )
        BRAND = (
            "brand",
            "Marca",
        )
        FAMILY = (
            "family",
            "Familia",
        )
        MODEL = (
            "model",
            "Modelo",
        )
        SYS_OBJECT_ID = (
            "sys_object_id",
            "SysObjectID",
        )
        FIRMWARE = (
            "firmware",
            "Firmware",
        )
        COMBINED = (
            "combined",
            "Combinado",
        )
        MANUAL = (
            "manual",
            "Asignación manual",
        )

    class Status(models.TextChoices):
        DRAFT = (
            "draft",
            "Borrador",
        )
        TESTING = (
            "testing",
            "En pruebas",
        )
        ACTIVE = (
            "active",
            "Activo",
        )
        DEPRECATED = (
            "deprecated",
            "Obsoleto",
        )
        DISABLED = (
            "disabled",
            "Deshabilitado",
        )

    code = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        verbose_name="Código",
        help_text=(
            "Identificador estable del perfil. "
            "Ejemplo: RICOH_MP_C3004_SERIES."
        ),
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Nombre",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    version = models.CharField(
        max_length=50,
        default="1.0.0",
        db_index=True,
        verbose_name="Versión",
    )

    revision = models.PositiveIntegerField(
        default=1,
        verbose_name="Revisión",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Estado",
    )

    scope = models.CharField(
        max_length=20,
        choices=Scope.choices,
        default=Scope.GLOBAL,
        db_index=True,
        verbose_name="Alcance",
    )

    match_mode = models.CharField(
        max_length=30,
        choices=MatchMode.choices,
        default=MatchMode.GENERIC,
        db_index=True,
        verbose_name="Tipo de coincidencia",
    )

    priority = models.PositiveIntegerField(
        default=100,
        db_index=True,
        verbose_name="Prioridad",
        help_text=(
            "Un valor menor tiene mayor prioridad."
        ),
    )

    customer = models.ForeignKey(
        "partners.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_snmp_profiles",
        verbose_name="Cliente",
    )

    branch = models.ForeignKey(
        "partners.PartnerBranch",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_snmp_profiles",
        verbose_name="Sede",
    )

    agent = models.ForeignKey(
        "monitoring.MonitoringAgent",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="snmp_profiles",
        verbose_name="Agente",
    )

    device = models.ForeignKey(
        "monitoring.MonitoredDevice",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="assigned_snmp_profiles",
        verbose_name="Dispositivo",
    )

    equipment_brand = models.ForeignKey(
        "equipment.EquipmentBrand",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_snmp_profiles",
        verbose_name="Marca",
    )

    equipment_model = models.ForeignKey(
        "equipment.EquipmentModel",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_snmp_profiles",
        verbose_name="Modelo",
    )

    family_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Código de familia",
        help_text=(
            "Agrupa modelos que comparten la misma estructura SNMP."
        ),
    )

    manufacturer_name = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Fabricante",
    )

    enterprise_number = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Número enterprise",
    )

    sys_object_id = models.CharField(
        max_length=500,
        blank=True,
        db_index=True,
        verbose_name="SysObjectID exacto",
    )

    sys_object_id_prefix = models.CharField(
        max_length=500,
        blank=True,
        db_index=True,
        verbose_name="Prefijo SysObjectID",
    )

    sys_description_contains = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Texto en SysDescription",
    )

    sys_name_contains = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Texto en SysName",
    )

    model_name_contains = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Texto en modelo",
    )

    model_name_regex = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Expresión regular de modelo",
    )

    firmware_minimum = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Firmware mínimo",
    )

    firmware_maximum = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Firmware máximo",
    )

    firmware_contains = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Texto en firmware",
    )

    firmware_regex = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Expresión regular de firmware",
    )

    excluded_firmware_patterns = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Firmware excluido",
    )

    supported_snmp_versions = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Versiones SNMP compatibles",
        help_text=(
            'Ejemplo: ["2c", "3"].'
        ),
    )

    preferred_snmp_version = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Versión SNMP preferida",
    )

    default_snmp_port = models.PositiveIntegerField(
        default=161,
        verbose_name="Puerto SNMP predeterminado",
    )

    request_timeout_seconds = models.PositiveIntegerField(
        default=5,
        verbose_name="Tiempo de espera",
    )

    request_retry_count = models.PositiveIntegerField(
        default=1,
        verbose_name="Reintentos",
    )

    max_repetitions = models.PositiveIntegerField(
        default=25,
        verbose_name="Máximo de repeticiones",
        help_text=(
            "Valor utilizado en SNMP GETBULK."
        ),
    )

    use_bulk_requests = models.BooleanField(
        default=True,
        verbose_name="Usar GETBULK",
    )

    allow_walk = models.BooleanField(
        default=True,
        verbose_name="Permitir WALK",
    )

    discovery_oids = models.JSONField(
        default=list,
        blank=True,
        verbose_name="OID de descubrimiento",
        help_text=(
            "OID mínimos usados para identificar el equipo."
        ),
    )

    identity_oids = models.JSONField(
        default=list,
        blank=True,
        verbose_name="OID de identidad",
    )

    monitoring_oids = models.JSONField(
        default=list,
        blank=True,
        verbose_name="OID de monitoreo rápido",
    )

    inventory_oids = models.JSONField(
        default=list,
        blank=True,
        verbose_name="OID de inventario completo",
    )

    walk_roots = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Raíces WALK",
    )

    excluded_oid_roots = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Raíces OID excluidas",
    )

    counter_poll_interval_seconds = models.PositiveIntegerField(
        default=3600,
        verbose_name="Intervalo de contadores",
    )

    consumable_poll_interval_seconds = models.PositiveIntegerField(
        default=1800,
        verbose_name="Intervalo de consumibles",
    )

    component_poll_interval_seconds = models.PositiveIntegerField(
        default=21600,
        verbose_name="Intervalo de componentes",
    )

    alert_poll_interval_seconds = models.PositiveIntegerField(
        default=300,
        verbose_name="Intervalo de alertas",
    )

    job_poll_interval_seconds = models.PositiveIntegerField(
        default=60,
        verbose_name="Intervalo de trabajos",
    )

    inventory_poll_interval_seconds = models.PositiveIntegerField(
        default=86400,
        verbose_name="Intervalo de inventario completo",
    )

    supports_color = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Soporta color",
    )

    supports_counters = models.BooleanField(
        default=True,
        verbose_name="Soporta contadores",
    )

    supports_consumables = models.BooleanField(
        default=True,
        verbose_name="Soporta consumibles",
    )

    supports_components = models.BooleanField(
        default=False,
        verbose_name="Soporta componentes",
    )

    supports_trays = models.BooleanField(
        default=True,
        verbose_name="Soporta bandejas",
    )

    supports_accessories = models.BooleanField(
        default=False,
        verbose_name="Soporta accesorios",
    )

    supports_alerts = models.BooleanField(
        default=True,
        verbose_name="Soporta alertas",
    )

    supports_jobs = models.BooleanField(
        default=False,
        verbose_name="Soporta trabajos",
    )

    supports_firmware = models.BooleanField(
        default=True,
        verbose_name="Soporta lectura de firmware",
    )

    supports_raw_walk = models.BooleanField(
        default=True,
        verbose_name="Permite conservar WALK original",
    )

    store_unknown_oids = models.BooleanField(
        default=True,
        verbose_name="Guardar OID desconocidos",
    )

    store_all_raw_oids = models.BooleanField(
        default=False,
        verbose_name="Guardar todos los OID",
    )

    job_privacy_mode = models.CharField(
        max_length=20,
        choices=[
            (
                "full",
                "Información completa",
            ),
            (
                "anonymized",
                "Información anonimizada",
            ),
            (
                "omitted",
                "Información omitida",
            ),
        ],
        default="omitted",
        verbose_name="Privacidad de trabajos",
    )

    parsing_options = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Opciones de interpretación",
        help_text=(
            "Configuración adicional para conversiones, tablas, "
            "índices y valores especiales."
        ),
    )

    profile_metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos",
    )

    checksum = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        editable=False,
        verbose_name="Checksum",
    )

    tested_device_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Dispositivos probados",
    )

    successful_device_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Dispositivos correctos",
    )

    failed_device_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Dispositivos con error",
    )

    last_tested_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última prueba",
    )

    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de activación",
    )

    deprecated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de obsolescencia",
    )

    is_default = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Perfil predeterminado",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Perfil SNMP"
        verbose_name_plural = "Perfiles SNMP"
        ordering = (
            "priority",
            "code",
        )
        indexes = [
            models.Index(
                fields=[
                    "status",
                    "scope",
                    "priority",
                ],
                name="mon_profile_status_scope_idx",
            ),
            models.Index(
                fields=[
                    "enterprise_number",
                    "sys_object_id",
                ],
                name="mon_profile_enterprise_oid_idx",
            ),
            models.Index(
                fields=[
                    "equipment_brand",
                    "family_code",
                    "priority",
                ],
                name="mon_profile_brand_family_idx",
            ),
            models.Index(
                fields=[
                    "equipment_model",
                    "status",
                ],
                name="mon_profile_model_status_idx",
            ),
            models.Index(
                fields=[
                    "customer",
                    "branch",
                    "status",
                ],
                name="mon_profile_customer_scope_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "status",
                    "priority",
                ],
                name="mon_profile_device_status_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "customer",
                    "branch",
                    "agent",
                    "device",
                    "code",
                    "version",
                ],
                condition=Q(
                    archived_at__isnull=True,
                ),
                name="unique_active_snmp_profile_version",
            ),
            models.UniqueConstraint(
                fields=[
                    "scope",
                ],
                condition=Q(
                    is_default=True,
                    status="active",
                    archived_at__isnull=True,
                ),
                name="unique_default_profile_per_scope",
            ),
        ]

    def __str__(self):
        return (
            f"{self.code} "
            f"v{self.version}"
        )

    def get_specificity_score(self):
        """
        Devuelve un puntaje orientativo de especificidad.

        El selector podrá combinarlo con la prioridad.
        """

        score = 0

        if self.scope == self.Scope.CUSTOMER:
            score += 100
        elif self.scope == self.Scope.BRANCH:
            score += 200
        elif self.scope == self.Scope.AGENT:
            score += 300
        elif self.scope == self.Scope.DEVICE:
            score += 500

        if self.enterprise_number:
            score += 20

        if self.equipment_brand_id:
            score += 30

        if self.family_code:
            score += 50

        if self.equipment_model_id:
            score += 100

        if self.sys_object_id_prefix:
            score += 80

        if self.sys_object_id:
            score += 150

        if self.model_name_contains:
            score += 20

        if self.model_name_regex:
            score += 40

        if self.firmware_contains:
            score += 20

        if self.firmware_regex:
            score += 40

        if self.firmware_minimum or self.firmware_maximum:
            score += 30

        return score

    def applies_to_scope(
        self,
        *,
        customer=None,
        branch=None,
        agent=None,
        device=None,
    ):
        if self.scope == self.Scope.GLOBAL:
            return True

        if self.scope == self.Scope.CUSTOMER:
            return (
                customer is not None
                and self.customer_id == customer.id
            )

        if self.scope == self.Scope.BRANCH:
            return (
                branch is not None
                and self.branch_id == branch.id
            )

        if self.scope == self.Scope.AGENT:
            return (
                agent is not None
                and self.agent_id == agent.id
            )

        if self.scope == self.Scope.DEVICE:
            return (
                device is not None
                and self.device_id == device.id
            )

        return False

    def register_test_result(
        self,
        *,
        successful,
        tested_at=None,
    ):
        from django.utils import timezone

        self.tested_device_count += 1

        if successful:
            self.successful_device_count += 1
        else:
            self.failed_device_count += 1

        self.last_tested_at = (
            tested_at
            or timezone.now()
        )

        self.save(
            update_fields=[
                "tested_device_count",
                "successful_device_count",
                "failed_device_count",
                "last_tested_at",
                "updated_at",
            ]
        )

    def activate(self):
        from django.utils import timezone

        self.status = self.Status.ACTIVE
        self.activated_at = timezone.now()
        self.deprecated_at = None

        self.save(
            update_fields=[
                "status",
                "activated_at",
                "deprecated_at",
                "updated_at",
            ]
        )

    def deprecate(self):
        from django.utils import timezone

        self.status = self.Status.DEPRECATED
        self.deprecated_at = timezone.now()
        self.is_default = False

        self.save(
            update_fields=[
                "status",
                "deprecated_at",
                "is_default",
                "updated_at",
            ]
        )

    def clean(self):
        super().clean()

        text_fields = [
            "code",
            "name",
            "description",
            "version",
            "family_code",
            "manufacturer_name",
            "sys_object_id",
            "sys_object_id_prefix",
            "sys_description_contains",
            "sys_name_contains",
            "model_name_contains",
            "model_name_regex",
            "firmware_minimum",
            "firmware_maximum",
            "firmware_contains",
            "firmware_regex",
            "preferred_snmp_version",
            "checksum",
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
        self.family_code = self.family_code.upper()
        self.sys_object_id = self.sys_object_id.strip(".")
        self.sys_object_id_prefix = (
            self.sys_object_id_prefix.strip(".")
        )

        if not self.code:
            raise ValidationError(
                {
                    "code": (
                        "El código del perfil es obligatorio."
                    ),
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": (
                        "El nombre del perfil es obligatorio."
                    ),
                }
            )

        if not self.version:
            raise ValidationError(
                {
                    "version": (
                        "La versión del perfil es obligatoria."
                    ),
                }
            )

        if self.default_snmp_port < 1:
            raise ValidationError(
                {
                    "default_snmp_port": (
                        "El puerto debe ser mayor que cero."
                    ),
                }
            )

        if self.default_snmp_port > 65535:
            raise ValidationError(
                {
                    "default_snmp_port": (
                        "El puerto no puede superar 65535."
                    ),
                }
            )

        if self.request_timeout_seconds < 1:
            raise ValidationError(
                {
                    "request_timeout_seconds": (
                        "El tiempo de espera debe ser "
                        "como mínimo un segundo."
                    ),
                }
            )

        if self.max_repetitions < 1:
            raise ValidationError(
                {
                    "max_repetitions": (
                        "El máximo de repeticiones debe "
                        "ser mayor que cero."
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

        required_scope_fields = {
            self.Scope.GLOBAL: None,
            self.Scope.CUSTOMER: "customer",
            self.Scope.BRANCH: "branch",
            self.Scope.AGENT: "agent",
            self.Scope.DEVICE: "device",
        }

        required_field = required_scope_fields.get(
            self.scope
        )

        if required_field and not getattr(
            self,
            f"{required_field}_id",
        ):
            raise ValidationError(
                {
                    required_field: (
                        "Este campo es obligatorio para "
                        "el alcance seleccionado."
                    ),
                }
            )

        if self.scope == self.Scope.GLOBAL:
            if any(
                [
                    self.customer_id,
                    self.branch_id,
                    self.agent_id,
                    self.device_id,
                ]
            ):
                raise ValidationError(
                    "Un perfil global no puede estar limitado "
                    "a cliente, sede, agente o dispositivo."
                )

        if self.scope == self.Scope.CUSTOMER:
            if any(
                [
                    self.branch_id,
                    self.agent_id,
                    self.device_id,
                ]
            ):
                raise ValidationError(
                    "Un perfil de cliente no puede fijar sede, "
                    "agente o dispositivo."
                )

        if self.scope == self.Scope.BRANCH:
            if not self.customer_id:
                raise ValidationError(
                    {
                        "customer": (
                            "La sede requiere un cliente."
                        ),
                    }
                )

            if any(
                [
                    self.agent_id,
                    self.device_id,
                ]
            ):
                raise ValidationError(
                    "Un perfil de sede no puede fijar agente "
                    "o dispositivo."
                )

        if self.scope == self.Scope.AGENT:
            if not self.customer_id:
                raise ValidationError(
                    {
                        "customer": (
                            "El agente requiere un cliente."
                        ),
                    }
                )

            if self.device_id:
                raise ValidationError(
                    "Un perfil de agente no puede fijar "
                    "un dispositivo."
                )

        if self.scope == self.Scope.DEVICE:
            if not self.customer_id:
                raise ValidationError(
                    {
                        "customer": (
                            "El dispositivo requiere un cliente."
                        ),
                    }
                )

        if (
            self.sys_object_id
            and self.sys_object_id_prefix
            and not self.sys_object_id.startswith(
                self.sys_object_id_prefix
            )
        ):
            raise ValidationError(
                {
                    "sys_object_id_prefix": (
                        "El SysObjectID exacto no coincide "
                        "con el prefijo configurado."
                    ),
                }
            )

        allowed_snmp_versions = {
            "1",
            "2",
            "2c",
            "3",
        }

        invalid_versions = [
            version
            for version in self.supported_snmp_versions
            if str(version).lower()
            not in allowed_snmp_versions
        ]

        if invalid_versions:
            raise ValidationError(
                {
                    "supported_snmp_versions": (
                        "Existen versiones SNMP no válidas."
                    ),
                }
            )

        if (
            self.preferred_snmp_version
            and self.supported_snmp_versions
            and self.preferred_snmp_version
            not in self.supported_snmp_versions
        ):
            raise ValidationError(
                {
                    "preferred_snmp_version": (
                        "La versión preferida debe estar dentro "
                        "de las versiones compatibles."
                    ),
                }
            )

        if self.is_default:
            if self.status != self.Status.ACTIVE:
                raise ValidationError(
                    {
                        "is_default": (
                            "Solo un perfil activo puede ser "
                            "predeterminado."
                        ),
                    }
                )

        match_fields = [
            self.enterprise_number,
            self.equipment_brand_id,
            self.equipment_model_id,
            self.family_code,
            self.sys_object_id,
            self.sys_object_id_prefix,
            self.sys_description_contains,
            self.model_name_contains,
            self.model_name_regex,
            self.firmware_contains,
            self.firmware_regex,
            self.device_id,
        ]

        if (
            self.match_mode != self.MatchMode.GENERIC
            and not any(match_fields)
        ):
            raise ValidationError(
                "El perfil requiere al menos una condición "
                "de coincidencia."
            )

    def save(self, *args, **kwargs):
        self.code = str(
            self.code or ""
        ).strip().upper()

        self.family_code = str(
            self.family_code or ""
        ).strip().upper()

        self.sys_object_id = str(
            self.sys_object_id or ""
        ).strip().strip(".")

        self.sys_object_id_prefix = str(
            self.sys_object_id_prefix or ""
        ).strip().strip(".")

        self.supported_snmp_versions = [
            str(version).strip().lower()
            for version in (
                self.supported_snmp_versions
                or []
            )
            if str(version).strip()
        ]

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )