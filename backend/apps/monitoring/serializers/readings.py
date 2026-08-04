# -*- coding: utf-8 -*-

from rest_framework import serializers

from apps.monitoring.models import (
    AccessoryReading,
    ComponentReading,
    ConsumableReading,
    CounterReading,
    DeviceAlert,
    DeviceSnapshot,
    JobReading,
    MonitoredDevice,
    RawOIDReading,
    TrayReading,
)

from .common import MonitoringModelSerializer


class ChoiceDisplayMixin:
    """
    Agrega campos legibles para los valores definidos mediante choices.

    Ejemplo:

    status = "normal"
    status_display = "Normal"
    """

    display_fields = ()

    def get_fields(self):
        fields = super().get_fields()

        for field_name in self.display_fields:
            display_name = (
                f"{field_name}_display"
            )

            if display_name not in fields:
                fields[display_name] = (
                    serializers.CharField(
                        source=(
                            f"get_{field_name}_display"
                        ),
                        read_only=True,
                    )
                )

        return fields


class DeviceSnapshotSerializer(
    ChoiceDisplayMixin,
    MonitoringModelSerializer,
):
    display_fields = (
        "snapshot_type",
        "processing_status",
        "connection_status",
    )

    device_code = serializers.CharField(
        source="device.code",
        read_only=True,
    )

    device_name = serializers.SerializerMethodField()

    customer_name = serializers.SerializerMethodField()

    branch_name = serializers.SerializerMethodField()

    agent_code = serializers.CharField(
        source="agent.code",
        read_only=True,
    )

    class Meta:
        model = DeviceSnapshot
        fields = "__all__"

        read_only_fields = (
            "id",
            "customer",
            "branch",
            "agent",
            "network",
            "received_at",
            "processing_started_at",
            "processed_at",
            "counter_reading_count",
            "consumable_reading_count",
            "component_reading_count",
            "tray_reading_count",
            "accessory_reading_count",
            "job_reading_count",
            "raw_oid_count",
            "unknown_oid_count",
            "is_historical",
            "created_at",
            "updated_at",
            "archived_at",
            "archived_by",
            "archive_reason",
        )

    def get_device_name(
        self,
        obj,
    ):
        return (
            obj.device.raw_model_name
            or obj.device.sys_name
            or obj.device.hostname
            or str(obj.device.ip_address)
        )

    def get_customer_name(
        self,
        obj,
    ):
        customer = obj.customer

        return (
            getattr(
                customer,
                "trade_name",
                "",
            )
            or getattr(
                customer,
                "legal_name",
                "",
            )
            or str(customer)
        )

    def get_branch_name(
        self,
        obj,
    ):
        if not obj.branch:
            return ""

        return (
            getattr(
                obj.branch,
                "name",
                "",
            )
            or str(obj.branch)
        )


class CounterReadingSerializer(
    ChoiceDisplayMixin,
    MonitoringModelSerializer,
):
    display_fields = (
        "category",
        "function_type",
        "color_mode",
        "sides_mode",
        "value_source",
        "validation_status",
    )

    device_code = serializers.CharField(
        source="device.code",
        read_only=True,
    )

    class Meta:
        model = CounterReading
        fields = "__all__"

        read_only_fields = (
            "id",
            "integer_value",
            "previous_value",
            "delta_value",
            "created_at",
            "updated_at",
            "archived_at",
            "archived_by",
            "archive_reason",
        )


class ConsumableReadingSerializer(
    ChoiceDisplayMixin,
    MonitoringModelSerializer,
):
    display_fields = (
        "consumable_type",
        "color",
        "status",
        "value_meaning",
    )

    device_code = serializers.CharField(
        source="device.code",
        read_only=True,
    )

    class Meta:
        model = ConsumableReading
        fields = "__all__"

        read_only_fields = (
            "id",
            "previous_percentage",
            "delta_percentage",
            "created_at",
            "updated_at",
            "archived_at",
            "archived_by",
            "archive_reason",
        )


class ComponentReadingSerializer(
    ChoiceDisplayMixin,
    MonitoringModelSerializer,
):
    display_fields = (
        "component_category",
        "color",
        "status",
        "value_meaning",
    )

    device_code = serializers.CharField(
        source="device.code",
        read_only=True,
    )

    class Meta:
        model = ComponentReading
        fields = "__all__"

        read_only_fields = (
            "id",
            "previous_percentage",
            "delta_percentage",
            "remaining_cycles",
            "created_at",
            "updated_at",
            "archived_at",
            "archived_by",
            "archive_reason",
        )


class TrayReadingSerializer(
    ChoiceDisplayMixin,
    MonitoringModelSerializer,
):
    display_fields = (
        "tray_type",
        "status",
    )

    device_code = serializers.CharField(
        source="device.code",
        read_only=True,
    )

    class Meta:
        model = TrayReading
        fields = "__all__"

        read_only_fields = (
            "id",
            "previous_percentage",
            "delta_percentage",
            "created_at",
            "updated_at",
            "archived_at",
            "archived_by",
            "archive_reason",
        )


class AccessoryReadingSerializer(
    ChoiceDisplayMixin,
    MonitoringModelSerializer,
):
    display_fields = (
        "accessory_type",
        "status",
    )

    device_code = serializers.CharField(
        source="device.code",
        read_only=True,
    )

    class Meta:
        model = AccessoryReading
        fields = "__all__"

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "archived_at",
            "archived_by",
            "archive_reason",
        )


class DeviceAlertSerializer(
    ChoiceDisplayMixin,
    MonitoringModelSerializer,
):
    display_fields = (
        "category",
        "severity",
        "status",
        "source_type",
    )

    device_code = serializers.CharField(
        source="device.code",
        read_only=True,
    )

    acknowledged_by_name = (
        serializers.SerializerMethodField()
    )

    resolved_by_name = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = DeviceAlert
        fields = "__all__"

        read_only_fields = (
            "id",
            "alert_key",
            "acknowledged_at",
            "acknowledged_by",
            "resolved_at",
            "resolved_by",
            "duration_seconds",
            "occurrence_count",
            "created_at",
            "updated_at",
            "archived_at",
            "archived_by",
            "archive_reason",
        )

    def get_acknowledged_by_name(
        self,
        obj,
    ):
        if not obj.acknowledged_by:
            return ""

        return (
            getattr(
                obj.acknowledged_by,
                "full_name",
                "",
            )
            or getattr(
                obj.acknowledged_by,
                "email",
                "",
            )
            or str(obj.acknowledged_by)
        )

    def get_resolved_by_name(
        self,
        obj,
    ):
        if not obj.resolved_by:
            return ""

        return (
            getattr(
                obj.resolved_by,
                "full_name",
                "",
            )
            or getattr(
                obj.resolved_by,
                "email",
                "",
            )
            or str(obj.resolved_by)
        )


class JobReadingSerializer(
    MonitoringModelSerializer
):
    class Meta:
        model = JobReading
        fields = "__all__"


class RawOIDReadingSerializer(
    MonitoringModelSerializer
):
    class Meta:
        model = RawOIDReading
        fields = "__all__"


class SnapshotIngestionSerializer(
    serializers.Serializer
):
    """
    Sobre completo recibido desde el agente de monitoreo.

    Se usan diccionarios porque la captura todavía no existe
    cuando se valida inicialmente el contenido recibido.
    """

    snapshot = serializers.DictField()

    counters = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    consumables = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    components = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    trays = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    accessories = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    alerts = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    jobs = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    raw_oids = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )


class ManualSnapshotCreateSerializer(
    serializers.Serializer
):
    """
    Registra una captura manual con contadores, consumibles,
    componentes, bandejas, accesorios y alertas.
    """

    device = serializers.PrimaryKeyRelatedField(
        queryset=MonitoredDevice.objects.filter(
            archived_at__isnull=True,
        ),
    )

    captured_at = serializers.DateTimeField(
        required=False,
    )

    connection_status = serializers.ChoiceField(
        choices=(
            DeviceSnapshot.ConnectionStatus.choices
        ),
        default=(
            DeviceSnapshot.ConnectionStatus.ONLINE
        ),
    )

    operational_status = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        write_only=True,
    )

    total_meter = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
    )

    black_meter = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
    )

    color_meter = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
    )

    scan_meter = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
    )

    counters = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    consumables = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    components = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    trays = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    accessories = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    alerts = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    def validate_device(
        self,
        device,
    ):
        if device.archived_at:
            raise serializers.ValidationError(
                (
                    "No se puede registrar una lectura "
                    "en un dispositivo archivado."
                )
            )

        if not device.agent_id:
            raise serializers.ValidationError(
                (
                    "El dispositivo debe tener "
                    "un agente asignado."
                )
            )

        return device


class AlertActionSerializer(
    serializers.Serializer
):
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )