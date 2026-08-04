# -*- coding: utf-8 -*-

import uuid

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.monitoring.authentication import (
    MonitoringAgentCredentialAuthentication,
)

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

from apps.monitoring.permissions import (
    IsMonitoringAgent,
)

from apps.monitoring.serializers import (
    AccessoryReadingSerializer,
    ComponentReadingSerializer,
    ConsumableReadingSerializer,
    CounterReadingSerializer,
    DeviceAlertSerializer,
    DeviceSnapshotSerializer,
    JobReadingSerializer,
    RawOIDReadingSerializer,
    SnapshotIngestionSerializer,
    TrayReadingSerializer,
)

from apps.monitoring.serializers.readings import (
    AlertActionSerializer,
    ManualSnapshotCreateSerializer,
)

from .common import MonitoringAdminModelViewSet


def parse_bool(
    value,
):
    if value is None:
        return None

    text = str(
        value
    ).strip().lower()

    if text in {
        "1",
        "true",
        "yes",
        "si",
        "sí",
    }:
        return True

    if text in {
        "0",
        "false",
        "no",
    }:
        return False

    return None


def django_validation_response(
    exception,
):
    detail = (
        getattr(
            exception,
            "message_dict",
            None,
        )
        or {
            "detail": getattr(
                exception,
                "messages",
                [
                    str(exception),
                ],
            ),
        }
    )

    return Response(
        detail,
        status=status.HTTP_400_BAD_REQUEST,
    )


def filter_common(
    queryset,
    request,
):
    device_id = str(
        request.query_params.get(
            "device",
            "",
        )
    ).strip()

    if device_id:
        queryset = queryset.filter(
            device_id=device_id,
        )

    customer_id = str(
        request.query_params.get(
            "customer",
            "",
        )
    ).strip()

    if customer_id:
        queryset = queryset.filter(
            customer_id=customer_id,
        )

    branch_id = str(
        request.query_params.get(
            "branch",
            "",
        )
    ).strip()

    if branch_id:
        queryset = queryset.filter(
            branch_id=branch_id,
        )

    snapshot_id = str(
        request.query_params.get(
            "snapshot",
            "",
        )
    ).strip()

    if (
        snapshot_id
        and hasattr(
            queryset.model,
            "snapshot_id",
        )
    ):
        queryset = queryset.filter(
            snapshot_id=snapshot_id,
        )

    return queryset


def latest_rows(
    queryset,
    field_name,
):
    seen = set()
    result = []

    for item in queryset.order_by(
        field_name,
        "-captured_at",
    ):
        key = getattr(
            item,
            field_name,
            None,
        )

        if key in seen:
            continue

        seen.add(key)
        result.append(item)

    return result


class HistoricalReadingViewSet(
    MonitoringAdminModelViewSet
):
    """
    Base para los registros históricos.

    Las lecturas automáticas no pueden modificarse.

    Las lecturas manuales pueden editarse, pero no
    eliminarse físicamente.
    """

    def update(
        self,
        request,
        *args,
        **kwargs,
    ):
        instance = self.get_object()

        snapshot = getattr(
            instance,
            "snapshot",
            None,
        )

        if (
            snapshot
            and snapshot.snapshot_type
            != DeviceSnapshot.SnapshotType.MANUAL
        ):
            return Response(
                {
                    "detail": (
                        "Solo se pueden modificar registros "
                        "creados mediante una captura manual."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().update(
            request,
            *args,
            **kwargs,
        )

    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):
        return Response(
            {
                "detail": (
                    "Las lecturas históricas no pueden "
                    "eliminarse. Registra una nueva captura "
                    "manual para corregir la información."
                ),
            },
            status=(
                status.HTTP_405_METHOD_NOT_ALLOWED
            ),
        )


class DeviceSnapshotViewSet(
    HistoricalReadingViewSet
):
    queryset = (
        DeviceSnapshot.objects
        .select_related(
            "device",
            "customer",
            "branch",
            "agent",
            "network",
            "credential",
        )
        .all()
    )

    serializer_class = (
        DeviceSnapshotSerializer
    )

    def get_queryset(
        self,
    ):
        queryset = filter_common(
            super().get_queryset(),
            self.request,
        )

        for field_name in (
            "snapshot_type",
            "processing_status",
            "connection_status",
        ):
            value = str(
                self.request.query_params.get(
                    field_name,
                    "",
                )
            ).strip()

            if value:
                queryset = queryset.filter(
                    **{
                        field_name: value,
                    }
                )

        return queryset

    @action(
        detail=False,
        methods=[
            "post",
        ],
        url_path="manual",
    )
    def manual(
        self,
        request,
    ):
        serializer = (
            ManualSnapshotCreateSerializer(
                data=request.data,
                context={
                    "request": request,
                },
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        data = serializer.validated_data

        device = data[
            "device"
        ]

        captured_at = data.get(
            "captured_at",
            timezone.now(),
        )

        with transaction.atomic():
            snapshot = (
                DeviceSnapshot.objects.create(
                    device=device,
                    credential=(
                        device.snmp_credential
                    ),
                    snapshot_type=(
                        DeviceSnapshot
                        .SnapshotType
                        .MANUAL
                    ),
                    processing_status=(
                        DeviceSnapshot
                        .ProcessingStatus
                        .PROCESSING
                    ),
                    connection_status=data.get(
                        "connection_status",
                        (
                            DeviceSnapshot
                            .ConnectionStatus
                            .ONLINE
                        ),
                    ),
                    captured_at=captured_at,
                    processing_started_at=(
                        timezone.now()
                    ),
                    agent_snapshot_id=(
                        f"manual-"
                        f"{uuid.uuid4().hex}"
                    ),
                    configuration_version=1,
                    ip_address=(
                        device.ip_address
                    ),
                    mac_address=(
                        device.mac_address
                    ),
                    hostname=(
                        device.hostname
                    ),
                    sys_name=(
                        device.sys_name
                    ),
                    sys_description=(
                        device.sys_description
                    ),
                    sys_object_id=(
                        device.sys_object_id
                    ),
                    sys_location=(
                        device.sys_location
                    ),
                    raw_brand_name=(
                        device.raw_brand_name
                    ),
                    raw_model_name=(
                        device.raw_model_name
                    ),
                    raw_serial_number=(
                        device.raw_serial_number
                    ),
                    firmware_version=(
                        device.firmware_version
                    ),
                    operational_status=(
                        data.get(
                            "operational_status",
                            "",
                        )
                    ),
                    total_meter=data.get(
                        "total_meter",
                    ),
                    black_meter=data.get(
                        "black_meter",
                    ),
                    color_meter=data.get(
                        "color_meter",
                    ),
                    scan_meter=data.get(
                        "scan_meter",
                    ),
                    raw_payload={
                        "source": "manual",
                        "notes": data.get(
                            "notes",
                            "",
                        ),
                        "created_by": str(
                            request.user.pk
                        ),
                    },
                    normalized_payload={},
                )
            )

            serializer_map = {
                "counters": (
                    CounterReadingSerializer
                ),
                "consumables": (
                    ConsumableReadingSerializer
                ),
                "components": (
                    ComponentReadingSerializer
                ),
                "trays": (
                    TrayReadingSerializer
                ),
                "accessories": (
                    AccessoryReadingSerializer
                ),
                "alerts": (
                    DeviceAlertSerializer
                ),
            }

            created_counts = {
                key: 0
                for key in serializer_map
            }

            for (
                key,
                serializer_class,
            ) in serializer_map.items():
                rows = data.get(
                    key,
                    [],
                )

                for raw_row in rows:
                    row = dict(
                        raw_row
                    )

                    row[
                        "snapshot"
                    ] = str(
                        snapshot.pk
                    )

                    row[
                        "device"
                    ] = str(
                        device.pk
                    )

                    row[
                        "customer"
                    ] = str(
                        device.customer_id
                    )

                    row[
                        "branch"
                    ] = (
                        str(
                            device.branch_id
                        )
                        if device.branch_id
                        else None
                    )

                    if key == "alerts":
                        row.setdefault(
                            "source_type",
                            (
                                DeviceAlert
                                .SourceType
                                .MANUAL
                            ),
                        )

                        row.setdefault(
                            "status",
                            (
                                DeviceAlert
                                .Status
                                .ACTIVE
                            ),
                        )

                        row.setdefault(
                            "is_active",
                            True,
                        )

                        row.setdefault(
                            "occurred_at",
                            captured_at,
                        )

                        row.setdefault(
                            "first_detected_at",
                            captured_at,
                        )

                        row.setdefault(
                            "last_detected_at",
                            captured_at,
                        )

                        row.setdefault(
                            "last_snapshot",
                            str(
                                snapshot.pk
                            ),
                        )

                    else:
                        row[
                            "captured_at"
                        ] = captured_at

                    child_serializer = (
                        serializer_class(
                            data=row,
                            context={
                                "request": (
                                    request
                                ),
                            },
                        )
                    )

                    child_serializer.is_valid(
                        raise_exception=True,
                    )

                    try:
                        child_serializer.save()

                    except (
                        DjangoValidationError
                    ) as exception:
                        transaction.set_rollback(
                            True
                        )

                        return (
                            django_validation_response(
                                exception
                            )
                        )

                    created_counts[
                        key
                    ] += 1

            snapshot.counter_reading_count = (
                created_counts[
                    "counters"
                ]
            )

            snapshot.consumable_reading_count = (
                created_counts[
                    "consumables"
                ]
            )

            snapshot.component_reading_count = (
                created_counts[
                    "components"
                ]
            )

            snapshot.tray_reading_count = (
                created_counts[
                    "trays"
                ]
            )

            snapshot.accessory_reading_count = (
                created_counts[
                    "accessories"
                ]
            )

            snapshot.active_alert_count = (
                device.alerts.filter(
                    is_active=True,
                ).count()
            )

            snapshot.critical_alert_count = (
                device.alerts.filter(
                    is_active=True,
                    severity=(
                        DeviceAlert
                        .Severity
                        .CRITICAL
                    ),
                ).count()
            )

            snapshot.processing_status = (
                DeviceSnapshot
                .ProcessingStatus
                .COMPLETED
            )

            snapshot.processed_at = (
                timezone.now()
            )

            snapshot.save()

            device.last_snapshot_at = (
                captured_at
            )

            device.last_seen_at = (
                captured_at
            )

            device.consecutive_failure_count = 0

            device.last_error_message = ""

            if (
                snapshot.total_meter
                is not None
            ):
                device.current_total_meter = (
                    snapshot.total_meter
                )

            if (
                snapshot.black_meter
                is not None
            ):
                device.current_black_meter = (
                    snapshot.black_meter
                )

            if (
                snapshot.color_meter
                is not None
            ):
                device.current_color_meter = (
                    snapshot.color_meter
                )

            if (
                snapshot.scan_meter
                is not None
            ):
                device.current_scan_meter = (
                    snapshot.scan_meter
                )

            device.active_alert_count = (
                device.alerts.filter(
                    is_active=True,
                ).count()
            )

            device.critical_alert_count = (
                device.alerts.filter(
                    is_active=True,
                    severity=(
                        DeviceAlert
                        .Severity
                        .CRITICAL
                    ),
                ).count()
            )

            device.save()

        return Response(
            {
                "message": (
                    "Lectura manual registrada "
                    "correctamente."
                ),
                "snapshot": (
                    DeviceSnapshotSerializer(
                        snapshot,
                        context={
                            "request": request,
                        },
                    ).data
                ),
                "created": created_counts,
            },
            status=status.HTTP_201_CREATED,
        )


class CounterReadingViewSet(
    HistoricalReadingViewSet
):
    queryset = (
        CounterReading.objects
        .select_related(
            "snapshot",
            "device",
            "customer",
            "branch",
        )
        .all()
    )

    serializer_class = (
        CounterReadingSerializer
    )

    def get_queryset(
        self,
    ):
        queryset = filter_common(
            super().get_queryset(),
            self.request,
        )

        metric_code = str(
            self.request.query_params.get(
                "metric_code",
                "",
            )
        ).strip()

        if metric_code:
            queryset = queryset.filter(
                metric_code__iexact=(
                    metric_code
                ),
            )

        category = str(
            self.request.query_params.get(
                "category",
                "",
            )
        ).strip()

        if category:
            queryset = queryset.filter(
                category=category,
            )

        return queryset


class ConsumableReadingViewSet(
    HistoricalReadingViewSet
):
    queryset = (
        ConsumableReading.objects
        .select_related(
            "snapshot",
            "device",
            "customer",
            "branch",
        )
        .all()
    )

    serializer_class = (
        ConsumableReadingSerializer
    )

    def get_queryset(
        self,
    ):
        queryset = filter_common(
            super().get_queryset(),
            self.request,
        )

        for field_name in (
            "consumable_type",
            "color",
            "status",
        ):
            value = str(
                self.request.query_params.get(
                    field_name,
                    "",
                )
            ).strip()

            if value:
                queryset = queryset.filter(
                    **{
                        field_name: value,
                    }
                )

        replacement_required = (
            parse_bool(
                self.request.query_params.get(
                    "replacement_required",
                )
            )
        )

        if (
            replacement_required
            is not None
        ):
            queryset = queryset.filter(
                replacement_required=(
                    replacement_required
                ),
            )

        return queryset

    def list(
        self,
        request,
        *args,
        **kwargs,
    ):
        queryset = self.filter_queryset(
            self.get_queryset()
        )

        latest = parse_bool(
            request.query_params.get(
                "latest",
            )
        )

        if latest:
            rows = latest_rows(
                queryset,
                "metric_code",
            )

            return Response(
                self.get_serializer(
                    rows,
                    many=True,
                ).data
            )

        return super().list(
            request,
            *args,
            **kwargs,
        )


class ComponentReadingViewSet(
    HistoricalReadingViewSet
):
    queryset = (
        ComponentReading.objects
        .select_related(
            "snapshot",
            "device",
            "customer",
            "branch",
            "equipment_component",
        )
        .all()
    )

    serializer_class = (
        ComponentReadingSerializer
    )

    def get_queryset(
        self,
    ):
        queryset = filter_common(
            super().get_queryset(),
            self.request,
        )

        for field_name in (
            "component_category",
            "color",
            "status",
        ):
            value = str(
                self.request.query_params.get(
                    field_name,
                    "",
                )
            ).strip()

            if value:
                queryset = queryset.filter(
                    **{
                        field_name: value,
                    }
                )

        return queryset

    def list(
        self,
        request,
        *args,
        **kwargs,
    ):
        queryset = self.filter_queryset(
            self.get_queryset()
        )

        latest = parse_bool(
            request.query_params.get(
                "latest",
            )
        )

        if latest:
            rows = latest_rows(
                queryset,
                "metric_code",
            )

            return Response(
                self.get_serializer(
                    rows,
                    many=True,
                ).data
            )

        return super().list(
            request,
            *args,
            **kwargs,
        )


class TrayReadingViewSet(
    HistoricalReadingViewSet
):
    queryset = (
        TrayReading.objects
        .select_related(
            "snapshot",
            "device",
            "customer",
            "branch",
        )
        .all()
    )

    serializer_class = (
        TrayReadingSerializer
    )

    def get_queryset(
        self,
    ):
        queryset = filter_common(
            super().get_queryset(),
            self.request,
        )

        status_value = str(
            self.request.query_params.get(
                "status",
                "",
            )
        ).strip()

        if status_value:
            queryset = queryset.filter(
                status=status_value,
            )

        return queryset

    def list(
        self,
        request,
        *args,
        **kwargs,
    ):
        queryset = self.filter_queryset(
            self.get_queryset()
        )

        latest = parse_bool(
            request.query_params.get(
                "latest",
            )
        )

        if latest:
            rows = latest_rows(
                queryset,
                "tray_code",
            )

            return Response(
                self.get_serializer(
                    rows,
                    many=True,
                ).data
            )

        return super().list(
            request,
            *args,
            **kwargs,
        )


class AccessoryReadingViewSet(
    HistoricalReadingViewSet
):
    queryset = (
        AccessoryReading.objects
        .select_related(
            "snapshot",
            "device",
            "customer",
            "branch",
            "equipment_component",
        )
        .all()
    )

    serializer_class = (
        AccessoryReadingSerializer
    )

    def get_queryset(
        self,
    ):
        queryset = filter_common(
            super().get_queryset(),
            self.request,
        )

        status_value = str(
            self.request.query_params.get(
                "status",
                "",
            )
        ).strip()

        if status_value:
            queryset = queryset.filter(
                status=status_value,
            )

        return queryset

    def list(
        self,
        request,
        *args,
        **kwargs,
    ):
        queryset = self.filter_queryset(
            self.get_queryset()
        )

        latest = parse_bool(
            request.query_params.get(
                "latest",
            )
        )

        if latest:
            rows = latest_rows(
                queryset,
                "accessory_code",
            )

            return Response(
                self.get_serializer(
                    rows,
                    many=True,
                ).data
            )

        return super().list(
            request,
            *args,
            **kwargs,
        )


class DeviceAlertViewSet(
    HistoricalReadingViewSet
):
    queryset = (
        DeviceAlert.objects
        .select_related(
            "snapshot",
            "last_snapshot",
            "device",
            "customer",
            "branch",
            "equipment_component",
            "acknowledged_by",
            "resolved_by",
        )
        .all()
    )

    serializer_class = (
        DeviceAlertSerializer
    )

    def get_queryset(
        self,
    ):
        queryset = filter_common(
            super().get_queryset(),
            self.request,
        )

        for field_name in (
            "category",
            "severity",
            "status",
        ):
            value = str(
                self.request.query_params.get(
                    field_name,
                    "",
                )
            ).strip()

            if value:
                queryset = queryset.filter(
                    **{
                        field_name: value,
                    }
                )

        is_active = parse_bool(
            self.request.query_params.get(
                "is_active",
            )
        )

        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active,
            )

        search = str(
            self.request.query_params.get(
                "search",
                "",
            )
        ).strip()

        if search:
            queryset = queryset.filter(
                Q(
                    normalized_code__icontains=(
                        search
                    ),
                )
                | Q(
                    normalized_message__icontains=(
                        search
                    ),
                )
                | Q(
                    raw_code__icontains=(
                        search
                    ),
                )
                | Q(
                    raw_message__icontains=(
                        search
                    ),
                )
                | Q(
                    service_code__icontains=(
                        search
                    ),
                )
                | Q(
                    location_name__icontains=(
                        search
                    ),
                )
            )

        return queryset

    @action(
        detail=True,
        methods=[
            "post",
        ],
        url_path="acknowledge",
    )
    def acknowledge_alert(
        self,
        request,
        pk=None,
    ):
        alert = self.get_object()

        serializer = AlertActionSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            alert.acknowledge(
                user=request.user,
                notes=(
                    serializer
                    .validated_data
                    .get(
                        "notes",
                        "",
                    )
                ),
            )

        except (
            DjangoValidationError
        ) as exception:
            return (
                django_validation_response(
                    exception
                )
            )

        return Response(
            self.get_serializer(
                alert
            ).data
        )

    @action(
        detail=True,
        methods=[
            "post",
        ],
        url_path="resolve",
    )
    def resolve_alert(
        self,
        request,
        pk=None,
    ):
        alert = self.get_object()

        serializer = AlertActionSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            alert.resolve(
                user=request.user,
                notes=(
                    serializer
                    .validated_data
                    .get(
                        "notes",
                        "",
                    )
                ),
                automatic=False,
            )

        except (
            DjangoValidationError
        ) as exception:
            return (
                django_validation_response(
                    exception
                )
            )

        alert.device.active_alert_count = (
            alert.device.alerts.filter(
                is_active=True,
            ).count()
        )

        alert.device.critical_alert_count = (
            alert.device.alerts.filter(
                is_active=True,
                severity=(
                    DeviceAlert
                    .Severity
                    .CRITICAL
                ),
            ).count()
        )

        alert.device.save(
            update_fields=[
                "active_alert_count",
                "critical_alert_count",
                "updated_at",
            ]
        )

        return Response(
            self.get_serializer(
                alert
            ).data
        )


class JobReadingViewSet(
    HistoricalReadingViewSet
):
    queryset = (
        JobReading.objects.all()
    )

    serializer_class = (
        JobReadingSerializer
    )

    def get_queryset(
        self,
    ):
        return filter_common(
            super().get_queryset(),
            self.request,
        )


class RawOIDReadingViewSet(
    HistoricalReadingViewSet
):
    queryset = (
        RawOIDReading.objects.all()
    )

    serializer_class = (
        RawOIDReadingSerializer
    )

    def get_queryset(
        self,
    ):
        return filter_common(
            super().get_queryset(),
            self.request,
        )


class SnapshotIngestionAPIView(
    APIView
):
    authentication_classes = [
        MonitoringAgentCredentialAuthentication,
    ]

    permission_classes = [
        IsMonitoringAgent,
    ]

    serializer_map = {
        "counters": (
            CounterReadingSerializer
        ),
        "consumables": (
            ConsumableReadingSerializer
        ),
        "components": (
            ComponentReadingSerializer
        ),
        "trays": (
            TrayReadingSerializer
        ),
        "accessories": (
            AccessoryReadingSerializer
        ),
        "alerts": (
            DeviceAlertSerializer
        ),
        "jobs": (
            JobReadingSerializer
        ),
        "raw_oids": (
            RawOIDReadingSerializer
        ),
    }

    def post(
        self,
        request,
        *args,
        **kwargs,
    ):
        envelope = (
            SnapshotIngestionSerializer(
                data=request.data,
                context={
                    "request": request,
                },
            )
        )

        envelope.is_valid(
            raise_exception=True,
        )

        agent = request.user.agent

        validated = (
            envelope.validated_data
        )

        snapshot_data = dict(
            validated[
                "snapshot"
            ]
        )

        device_id = snapshot_data.get(
            "device"
        )

        try:
            device = (
                MonitoredDevice.objects.get(
                    pk=device_id,
                )
            )

        except (
            MonitoredDevice.DoesNotExist
        ):
            return Response(
                {
                    "detail": (
                        "El dispositivo indicado "
                        "no existe."
                    ),
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        if device.agent_id != agent.id:
            return Response(
                {
                    "detail": (
                        "El dispositivo no pertenece "
                        "al agente autenticado."
                    ),
                },
                status=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        agent_snapshot_id = str(
            snapshot_data.get(
                "agent_snapshot_id",
                "",
            )
            or ""
        ).strip()

        if agent_snapshot_id:
            existing = (
                DeviceSnapshot.objects
                .filter(
                    agent=agent,
                    agent_snapshot_id=(
                        agent_snapshot_id
                    ),
                )
                .first()
            )

            if existing:
                return Response(
                    {
                        "message": (
                            "La captura ya había "
                            "sido recibida."
                        ),
                        "duplicate": True,
                        "snapshot": (
                            DeviceSnapshotSerializer(
                                existing,
                                context={
                                    "request": (
                                        request
                                    ),
                                },
                            ).data
                        ),
                    },
                    status=status.HTTP_200_OK,
                )

        captured_at = snapshot_data.get(
            "captured_at",
            timezone.now(),
        )

        with transaction.atomic():
            snapshot = (
                DeviceSnapshot.objects.create(
                    device=device,
                    credential=(
                        device.snmp_credential
                    ),
                    snapshot_type=(
                        snapshot_data.get(
                            "snapshot_type",
                            (
                                DeviceSnapshot
                                .SnapshotType
                                .MONITORING
                            ),
                        )
                    ),
                    processing_status=(
                        DeviceSnapshot
                        .ProcessingStatus
                        .PROCESSING
                    ),
                    connection_status=(
                        snapshot_data.get(
                            "connection_status",
                            (
                                DeviceSnapshot
                                .ConnectionStatus
                                .UNKNOWN
                            ),
                        )
                    ),
                    captured_at=captured_at,
                    processing_started_at=(
                        timezone.now()
                    ),
                    agent_snapshot_id=(
                        agent_snapshot_id
                        or (
                            f"agent-"
                            f"{uuid.uuid4().hex}"
                        )
                    ),
                    sequence_number=(
                        snapshot_data.get(
                            "sequence_number",
                        )
                    ),
                    configuration_version=(
                        snapshot_data.get(
                            "configuration_version",
                            1,
                        )
                    ),
                    profile_version=(
                        snapshot_data.get(
                            "profile_version",
                            "",
                        )
                    ),
                    ip_address=(
                        snapshot_data.get(
                            "ip_address",
                            device.ip_address,
                        )
                    ),
                    mac_address=(
                        snapshot_data.get(
                            "mac_address",
                            device.mac_address,
                        )
                    ),
                    hostname=(
                        snapshot_data.get(
                            "hostname",
                            device.hostname,
                        )
                    ),
                    sys_name=(
                        snapshot_data.get(
                            "sys_name",
                            device.sys_name,
                        )
                    ),
                    sys_description=(
                        snapshot_data.get(
                            "sys_description",
                            (
                                device
                                .sys_description
                            ),
                        )
                    ),
                    sys_object_id=(
                        snapshot_data.get(
                            "sys_object_id",
                            device.sys_object_id,
                        )
                    ),
                    sys_location=(
                        snapshot_data.get(
                            "sys_location",
                            device.sys_location,
                        )
                    ),
                    raw_brand_name=(
                        snapshot_data.get(
                            "raw_brand_name",
                            (
                                device
                                .raw_brand_name
                            ),
                        )
                    ),
                    raw_model_name=(
                        snapshot_data.get(
                            "raw_model_name",
                            (
                                device
                                .raw_model_name
                            ),
                        )
                    ),
                    raw_serial_number=(
                        snapshot_data.get(
                            "raw_serial_number",
                            (
                                device
                                .raw_serial_number
                            ),
                        )
                    ),
                    firmware_version=(
                        snapshot_data.get(
                            "firmware_version",
                            (
                                device
                                .firmware_version
                            ),
                        )
                    ),
                    operational_status=(
                        snapshot_data.get(
                            "operational_status",
                            "",
                        )
                    ),
                    printer_status=(
                        snapshot_data.get(
                            "printer_status",
                            "",
                        )
                    ),
                    scanner_status=(
                        snapshot_data.get(
                            "scanner_status",
                            "",
                        )
                    ),
                    fax_status=(
                        snapshot_data.get(
                            "fax_status",
                            "",
                        )
                    ),
                    paper_status=(
                        snapshot_data.get(
                            "paper_status",
                            "",
                        )
                    ),
                    consumable_status=(
                        snapshot_data.get(
                            "consumable_status",
                            "",
                        )
                    ),
                    maintenance_status=(
                        snapshot_data.get(
                            "maintenance_status",
                            "",
                        )
                    ),
                    network_status=(
                        snapshot_data.get(
                            "network_status",
                            "",
                        )
                    ),
                    response_time_ms=(
                        snapshot_data.get(
                            "response_time_ms",
                        )
                    ),
                    total_meter=(
                        snapshot_data.get(
                            "total_meter",
                        )
                    ),
                    black_meter=(
                        snapshot_data.get(
                            "black_meter",
                        )
                    ),
                    color_meter=(
                        snapshot_data.get(
                            "color_meter",
                        )
                    ),
                    scan_meter=(
                        snapshot_data.get(
                            "scan_meter",
                        )
                    ),
                    raw_payload=(
                        snapshot_data.get(
                            "raw_payload",
                            {},
                        )
                    ),
                    normalized_payload=(
                        snapshot_data.get(
                            "normalized_payload",
                            {},
                        )
                    ),
                    is_complete_inventory=(
                        snapshot_data.get(
                            "is_complete_inventory",
                            False,
                        )
                    ),
                )
            )

            created_counts = {
                key: 0
                for key in self.serializer_map
            }

            for (
                key,
                serializer_class,
            ) in self.serializer_map.items():
                rows = validated.get(
                    key,
                    [],
                )

                for raw_row in rows:
                    row = dict(
                        raw_row
                    )

                    row[
                        "snapshot"
                    ] = str(
                        snapshot.pk
                    )

                    row[
                        "device"
                    ] = str(
                        device.pk
                    )

                    row[
                        "customer"
                    ] = str(
                        device.customer_id
                    )

                    row[
                        "branch"
                    ] = (
                        str(
                            device.branch_id
                        )
                        if device.branch_id
                        else None
                    )

                    if key == "alerts":
                        row.setdefault(
                            "last_snapshot",
                            str(
                                snapshot.pk
                            ),
                        )

                        row.setdefault(
                            "occurred_at",
                            captured_at,
                        )

                        row.setdefault(
                            "first_detected_at",
                            captured_at,
                        )

                        row.setdefault(
                            "last_detected_at",
                            captured_at,
                        )

                    else:
                        row[
                            "captured_at"
                        ] = captured_at

                    child_serializer = (
                        serializer_class(
                            data=row,
                            context={
                                "request": (
                                    request
                                ),
                            },
                        )
                    )

                    child_serializer.is_valid(
                        raise_exception=True,
                    )

                    child_serializer.save()

                    created_counts[
                        key
                    ] += 1

            snapshot.counter_reading_count = (
                created_counts[
                    "counters"
                ]
            )

            snapshot.consumable_reading_count = (
                created_counts[
                    "consumables"
                ]
            )

            snapshot.component_reading_count = (
                created_counts[
                    "components"
                ]
            )

            snapshot.tray_reading_count = (
                created_counts[
                    "trays"
                ]
            )

            snapshot.accessory_reading_count = (
                created_counts[
                    "accessories"
                ]
            )

            snapshot.job_reading_count = (
                created_counts[
                    "jobs"
                ]
            )

            snapshot.raw_oid_count = (
                created_counts[
                    "raw_oids"
                ]
            )

            snapshot.processing_status = (
                DeviceSnapshot
                .ProcessingStatus
                .COMPLETED
            )

            snapshot.processed_at = (
                timezone.now()
            )

            snapshot.save()

            device.last_snapshot_at = (
                captured_at
            )

            device.last_seen_at = (
                captured_at
            )

            device.last_snmp_success_at = (
                captured_at
            )

            device.consecutive_failure_count = 0

            device.last_error_message = ""

            if (
                snapshot.total_meter
                is not None
            ):
                device.current_total_meter = (
                    snapshot.total_meter
                )

            if (
                snapshot.black_meter
                is not None
            ):
                device.current_black_meter = (
                    snapshot.black_meter
                )

            if (
                snapshot.color_meter
                is not None
            ):
                device.current_color_meter = (
                    snapshot.color_meter
                )

            if (
                snapshot.scan_meter
                is not None
            ):
                device.current_scan_meter = (
                    snapshot.scan_meter
                )

            device.active_alert_count = (
                device.alerts.filter(
                    is_active=True,
                ).count()
            )

            device.critical_alert_count = (
                device.alerts.filter(
                    is_active=True,
                    severity=(
                        DeviceAlert
                        .Severity
                        .CRITICAL
                    ),
                ).count()
            )

            device.save()

            agent.register_successful_sync()

        return Response(
            {
                "message": (
                    "Captura procesada "
                    "correctamente."
                ),
                "duplicate": False,
                "snapshot": (
                    DeviceSnapshotSerializer(
                        snapshot,
                        context={
                            "request": request,
                        },
                    ).data
                ),
                "created": created_counts,
            },
            status=status.HTTP_201_CREATED,
        )