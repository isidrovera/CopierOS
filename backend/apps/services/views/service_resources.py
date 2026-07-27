# -*- coding: utf-8 -*-
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.equipment.models import (
    ComponentCompatibility,
    EquipmentComponent,
)
from apps.services.models import (
    ServiceAssignmentHistory,
    ServiceChecklist,
    ServiceChecklistItem,
    ServiceEvidence,
    ServiceMeterReading,
    ServicePartRequest,
    ServicePartRequestItem,
    ServiceStatusHistory,
    ServiceTrackingPoint,
    ServiceTrackingSession,
)
from apps.services.serializers import (
    ServiceAssignmentHistorySerializer,
    ServiceChecklistItemSerializer,
    ServiceChecklistSerializer,
    ServiceEvidenceSerializer,
    ServiceMeterReadingSerializer,
    ServicePartRequestItemSerializer,
    ServicePartRequestSerializer,
    ServiceStatusHistorySerializer,
    ServiceTrackingPointSerializer,
    ServiceTrackingSessionSerializer,
)

from .base import ArchiveRestoreMixin


class ActiveRecordsMixin:
    def get_queryset(self):
        queryset = super().get_queryset()

        archived = str(
            self.request.query_params.get(
                "archived",
                "",
            )
            or ""
        ).strip().lower()

        if archived == "true":
            return queryset.filter(
                archived_at__isnull=False,
            )

        if archived == "all":
            return queryset

        return queryset.filter(
            archived_at__isnull=True,
        )


class ServiceAssignmentHistoryViewSet(
    ActiveRecordsMixin,
    viewsets.ReadOnlyModelViewSet,
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        ServiceAssignmentHistorySerializer
    )

    queryset = (
        ServiceAssignmentHistory.objects
        .select_related(
            "service_order",
            "previous_technician",
            "new_technician",
            "assigned_by",
        )
    )

    filterset_fields = (
        "service_order",
        "previous_technician",
        "new_technician",
    )

    ordering = (
        "-created_at",
    )


class ServiceStatusHistoryViewSet(
    ActiveRecordsMixin,
    viewsets.ReadOnlyModelViewSet,
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        ServiceStatusHistorySerializer
    )

    queryset = (
        ServiceStatusHistory.objects
        .select_related(
            "service_order",
            "changed_by",
        )
    )

    filterset_fields = (
        "service_order",
        "new_status",
        "changed_by",
        "source",
    )

    ordering = (
        "-created_at",
    )


class ServiceTrackingSessionViewSet(
    ArchiveRestoreMixin,
    ActiveRecordsMixin,
    viewsets.ModelViewSet,
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        ServiceTrackingSessionSerializer
    )

    queryset = (
        ServiceTrackingSession.objects
        .select_related(
            "service_order",
            "technician",
        )
    )

    filterset_fields = (
        "service_order",
        "technician",
        "status",
    )

    ordering = (
        "-started_at",
    )


class ServiceTrackingPointViewSet(
    ActiveRecordsMixin,
    viewsets.ModelViewSet,
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        ServiceTrackingPointSerializer
    )

    queryset = (
        ServiceTrackingPoint.objects
        .select_related(
            "tracking_session",
            "service_order",
            "technician",
        )
    )

    http_method_names = (
        "get",
        "post",
        "head",
        "options",
    )

    filterset_fields = (
        "tracking_session",
        "service_order",
        "technician",
        "event_type",
        "is_mock_location",
        "is_offline_capture",
    )

    ordering_fields = (
        "device_recorded_at",
        "server_received_at",
        "sequence_number",
    )

    ordering = (
        "device_recorded_at",
        "sequence_number",
    )

    @action(
        detail=False,
        methods=[
            "post",
        ],
        url_path="bulk",
    )
    def bulk_create(
        self,
        request,
    ):
        points = request.data

        if not isinstance(
            points,
            list,
        ):
            return Response(
                {
                    "detail": (
                        "Debe enviar una lista "
                        "de puntos GPS."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        if len(points) > 500:
            return Response(
                {
                    "detail": (
                        "Máximo 500 puntos "
                        "por envío."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        serializer = self.get_serializer(
            data=points,
            many=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ServiceChecklistViewSet(
    ArchiveRestoreMixin,
    ActiveRecordsMixin,
    viewsets.ModelViewSet,
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        ServiceChecklistSerializer
    )

    queryset = (
        ServiceChecklist.objects
        .prefetch_related(
            "items",
            "items__checked_by",
            "items__part_request_items",
            "items__part_request_items__source_component",
        )
        .select_related(
            "service_order",
        )
    )

    filterset_fields = (
        "service_order",
        "status",
    )

    ordering = (
        "-created_at",
    )


class ServiceChecklistItemViewSet(
    ArchiveRestoreMixin,
    ActiveRecordsMixin,
    viewsets.ModelViewSet,
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        ServiceChecklistItemSerializer
    )

    queryset = (
        ServiceChecklistItem.objects
        .select_related(
            "checklist",
            "checklist__service_order",
            "checklist__service_order__equipment",
            (
                "checklist__service_order__equipment__"
                "equipment_model"
            ),
            (
                "checklist__service_order__equipment__"
                "equipment_model__equipment_family"
            ),
            "source_component",
            "checked_by",
        )
        .prefetch_related(
            "part_request_items",
            "part_request_items__source_component",
        )
    )

    filterset_fields = (
        "checklist",
        "status",
        "category",
        "position",
        "is_required",
    )

    search_fields = (
        "component_code",
        "component_name",
        "observation",
    )

    ordering = (
        "display_order",
        "component_name",
    )

    @staticmethod
    def _clean_text(value):
        return str(
            value or "",
        ).strip()

    @staticmethod
    def _decimal_quantity(value):
        try:
            quantity = Decimal(
                str(value),
            )
        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "La cantidad no es válida."
            ) from exc

        if quantity <= 0:
            raise ValueError(
                "La cantidad debe ser mayor que cero."
            )

        return quantity

    @staticmethod
    def _image_url(
        request,
        component,
    ):
        image = getattr(
            component,
            "image",
            None,
        )

        if not image:
            return None

        try:
            image_url = image.url
        except ValueError:
            return None

        if request:
            return request.build_absolute_uri(
                image_url,
            )

        return image_url

    def _compatible_subpart_queryset(
        self,
        item,
    ):
        if not item.source_component_id:
            return (
                ComponentCompatibility.objects
                .none()
            )

        service_order = (
            item.checklist.service_order
        )

        equipment = (
            service_order.equipment
        )

        equipment_model = (
            equipment.equipment_model
        )

        equipment_family_id = getattr(
            equipment_model,
            "equipment_family_id",
            None,
        )

        target_filter = Q(
            equipment_model_id=(
                equipment_model.id
            ),
        )

        if equipment_family_id:
            target_filter |= Q(
                equipment_family_id=(
                    equipment_family_id
                ),
            )

        return (
            ComponentCompatibility.objects
            .select_related(
                "component",
                "component__component_type",
                "component__parent_component",
                "equipment_model",
                "equipment_family",
            )
            .filter(
                target_filter,
                archived_at__isnull=True,
                is_active=True,
                component__archived_at__isnull=True,
                component__is_active=True,
                component__parent_component_id=(
                    item.source_component_id
                ),
            )
            .order_by(
                "-is_preferred",
                "display_order",
                "component__display_order",
                "component__name",
            )
        )

    def _selected_compatibilities(
        self,
        item,
    ):
        selected = {}

        queryset = (
            self._compatible_subpart_queryset(
                item,
            )
        )

        for compatibility in queryset:
            key = (
                compatibility.component_id,
                compatibility.position,
            )

            current = selected.get(
                key,
            )

            if current is None:
                selected[key] = compatibility
                continue

            current_is_model = bool(
                current.equipment_model_id
            )

            new_is_model = bool(
                compatibility.equipment_model_id
            )

            if (
                new_is_model
                and not current_is_model
            ):
                selected[key] = compatibility
                continue

            if (
                new_is_model
                == current_is_model
                and compatibility.is_preferred
                and not current.is_preferred
            ):
                selected[key] = compatibility

        return list(
            selected.values(),
        )

    def _current_request_items_map(
        self,
        item,
    ):
        current_items = (
            ServicePartRequestItem.objects
            .select_related(
                "source_component",
                "request",
            )
            .filter(
                checklist_item=item,
                archived_at__isnull=True,
            )
            .order_by(
                "created_at",
            )
        )

        return {
            str(
                request_item.source_component_id
            ): request_item
            for request_item in current_items
            if request_item.source_component_id
        }

    def _serialize_compatible_subparts(
        self,
        item,
        request,
    ):
        current_items = (
            self._current_request_items_map(
                item,
            )
        )

        results = []

        for compatibility in (
            self._selected_compatibilities(
                item,
            )
        ):
            component = (
                compatibility.component
            )

            current_item = current_items.get(
                str(component.id),
            )

            results.append(
                {
                    "id": str(component.id),
                    "component": str(
                        component.id
                    ),
                    "compatibility": str(
                        compatibility.id
                    ),
                    "parent_component": str(
                        component.parent_component_id
                    ),
                    "parent_component_name": (
                        str(
                            component.parent_component
                        )
                        if component.parent_component_id
                        else ""
                    ),
                    "component_type": str(
                        component.component_type_id
                    ),
                    "component_type_name": str(
                        component.component_type
                    ),
                    "code": component.code,
                    "name": component.name,
                    "manufacturer_code": (
                        component.manufacturer_code
                    ),
                    "alternative_code": (
                        component.alternative_code
                    ),
                    "color": component.color,
                    "color_display": (
                        component.get_color_display()
                    ),
                    "unit_of_measure": (
                        component.unit_of_measure
                    ),
                    "position": (
                        compatibility.position
                    ),
                    "position_display": (
                        compatibility
                        .get_position_display()
                    ),
                    "compatibility_type": (
                        compatibility
                        .compatibility_type
                    ),
                    "compatibility_type_display": (
                        compatibility
                        .get_compatibility_type_display()
                    ),
                    "manufacturer_reference": (
                        compatibility
                        .manufacturer_reference
                    ),
                    "requires_adjustment": (
                        compatibility
                        .requires_adjustment
                    ),
                    "adjustment_instructions": (
                        compatibility
                        .adjustment_instructions
                    ),
                    "is_preferred": (
                        compatibility.is_preferred
                    ),
                    "image": self._image_url(
                        request,
                        component,
                    ),
                    "selected": bool(
                        current_item
                    ),
                    "request_item": (
                        str(current_item.id)
                        if current_item
                        else None
                    ),
                    "quantity": (
                        str(current_item.quantity)
                        if current_item
                        else "1.00"
                    ),
                    "urgency": (
                        current_item.urgency
                        if current_item
                        else (
                            ServicePartRequestItem
                            .Urgency
                            .NORMAL
                        )
                    ),
                    "reason": (
                        current_item.reason
                        if current_item
                        else item.observation
                    ),
                    "notes": (
                        current_item.notes
                        if current_item
                        else ""
                    ),
                }
            )

        return results

    @staticmethod
    def _delete_linked_request_items(
        item,
    ):
        request_ids = list(
            ServicePartRequestItem.objects
            .filter(
                checklist_item=item,
            )
            .values_list(
                "request_id",
                flat=True,
            )
            .distinct()
        )

        ServicePartRequestItem.objects.filter(
            checklist_item=item,
        ).delete()

        for request_id in request_ids:
            part_request = (
                ServicePartRequest.objects
                .filter(
                    id=request_id,
                )
                .first()
            )

            if not part_request:
                continue

            has_items = (
                part_request.items
                .filter(
                    archived_at__isnull=True,
                )
                .exists()
            )

            if (
                not has_items
                and part_request.status
                == ServicePartRequest.Status.DRAFT
            ):
                part_request.delete()

    @staticmethod
    def _get_or_create_part_request(
        service_order,
        user,
    ):
        part_request = (
            ServicePartRequest.objects
            .filter(
                service_order=service_order,
            )
            .first()
        )

        if part_request:
            if (
                part_request.status
                != ServicePartRequest.Status.DRAFT
            ):
                raise ValueError(
                    (
                        "El pedido de repuestos ya no está "
                        "en borrador y no puede modificarse "
                        "desde el checklist."
                    )
                )

            part_request.updated_by = user
            part_request.save(
                update_fields=[
                    "updated_by",
                    "updated_at",
                ]
            )

            return part_request

        return ServicePartRequest.objects.create(
            service_order=service_order,
            status=(
                ServicePartRequest.Status.DRAFT
            ),
            requested_by=user,
            created_by=user,
            updated_by=user,
        )

    def _validate_subparts_payload(
        self,
        item,
        subparts,
    ):
        if not isinstance(
            subparts,
            list,
        ):
            raise ValueError(
                (
                    "Las subpartes deben enviarse "
                    "como una lista."
                )
            )

        if not subparts:
            raise ValueError(
                (
                    "Debe seleccionar al menos una "
                    "subparte cuando el componente "
                    "requiere cambio."
                )
            )

        compatible_components = {
            str(
                compatibility.component_id
            ): compatibility
            for compatibility in (
                self._selected_compatibilities(
                    item,
                )
            )
        }

        if not compatible_components:
            raise ValueError(
                (
                    "No existen subpartes compatibles "
                    "configuradas para este componente "
                    "y modelo de equipo."
                )
            )

        valid_urgencies = dict(
            ServicePartRequestItem
            .Urgency
            .choices
        )

        normalized = []
        used_components = set()

        for index, row in enumerate(
            subparts,
            start=1,
        ):
            if not isinstance(
                row,
                dict,
            ):
                raise ValueError(
                    (
                        f"La subparte número {index} "
                        "no tiene un formato válido."
                    )
                )

            component_id = self._clean_text(
                row.get(
                    "component",
                    row.get(
                        "id",
                        "",
                    ),
                )
            )

            if not component_id:
                raise ValueError(
                    (
                        f"Debe indicar la subparte "
                        f"número {index}."
                    )
                )

            compatibility = (
                compatible_components.get(
                    component_id,
                )
            )

            if not compatibility:
                raise ValueError(
                    (
                        "Una de las subpartes seleccionadas "
                        "no es compatible con el componente, "
                        "modelo o familia de la máquina."
                    )
                )

            if component_id in used_components:
                raise ValueError(
                    (
                        "No puede seleccionar la misma "
                        "subparte más de una vez."
                    )
                )

            used_components.add(
                component_id,
            )

            quantity = self._decimal_quantity(
                row.get(
                    "quantity",
                    1,
                )
            )

            urgency = self._clean_text(
                row.get(
                    "urgency",
                    (
                        ServicePartRequestItem
                        .Urgency
                        .NORMAL
                    ),
                )
            ).lower()

            if urgency not in valid_urgencies:
                raise ValueError(
                    (
                        "La urgencia seleccionada "
                        "no es válida."
                    )
                )

            reason = self._clean_text(
                row.get(
                    "reason",
                    item.observation,
                )
            )

            if not reason:
                raise ValueError(
                    (
                        "Debe indicar el motivo para "
                        "cada subparte solicitada."
                    )
                )

            notes = self._clean_text(
                row.get(
                    "notes",
                    "",
                )
            )

            normalized.append(
                {
                    "compatibility": (
                        compatibility
                    ),
                    "component": (
                        compatibility.component
                    ),
                    "quantity": quantity,
                    "urgency": urgency,
                    "reason": reason,
                    "notes": notes,
                }
            )

        return normalized

    @action(
        detail=True,
        methods=[
            "get",
        ],
        url_path="compatible-subparts",
    )
    def compatible_subparts(
        self,
        request,
        pk=None,
    ):
        item = self.get_object()

        return Response(
            {
                "checklist_item": str(
                    item.id
                ),
                "source_component": (
                    str(item.source_component_id)
                    if item.source_component_id
                    else None
                ),
                "source_component_name": (
                    item.component_name
                ),
                "status": item.status,
                "status_display": (
                    item.get_status_display()
                ),
                "results": (
                    self
                    ._serialize_compatible_subparts(
                        item,
                        request,
                    )
                ),
            },
            status=status.HTTP_200_OK,
        )

    @transaction.atomic
    @action(
        detail=True,
        methods=[
            "post",
        ],
    )
    def check(
        self,
        request,
        pk=None,
    ):
        item = self.get_object()

        new_status = self._clean_text(
            request.data.get(
                "status",
                "",
            )
        ).lower()

        valid_statuses = dict(
            ServiceChecklistItem
            .Status
            .choices
        )

        if new_status not in valid_statuses:
            return Response(
                {
                    "status": (
                        "El estado seleccionado "
                        "no es válido."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        observation = self._clean_text(
            request.data.get(
                "observation",
                item.observation,
            )
        )

        if (
            new_status
            == ServiceChecklistItem.Status.FAILED
            and not observation
        ):
            return Response(
                {
                    "observation": (
                        "Debe describir la falla "
                        "cuando el componente requiere cambio."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        normalized_subparts = []

        if (
            new_status
            == ServiceChecklistItem.Status.FAILED
        ):
            try:
                normalized_subparts = (
                    self._validate_subparts_payload(
                        item=item,
                        subparts=request.data.get(
                            "subparts",
                            [],
                        ),
                    )
                )
            except ValueError as exc:
                return Response(
                    {
                        "subparts": str(exc),
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

        serializer = self.get_serializer(
            item,
            data={
                "status": new_status,
                "observation": observation,
                "consumable_present": (
                    request.data.get(
                        "consumable_present",
                        item.consumable_present,
                    )
                ),
                "consumable_level_percent": (
                    request.data.get(
                        "consumable_level_percent",
                        (
                            item
                            .consumable_level_percent
                        ),
                    )
                ),
                "checked_by": request.user.pk,
                "checked_at": timezone.now(),
            },
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        item = serializer.save()

        if (
            new_status
            != ServiceChecklistItem.Status.FAILED
        ):
            self._delete_linked_request_items(
                item,
            )

            return Response(
                {
                    "item": (
                        self.get_serializer(
                            item,
                        ).data
                    ),
                    "part_request": None,
                    "part_request_items": [],
                    "compatible_subparts": (
                        self
                        ._serialize_compatible_subparts(
                            item,
                            request,
                        )
                    ),
                },
                status=status.HTTP_200_OK,
            )

        try:
            part_request = (
                self._get_or_create_part_request(
                    service_order=(
                        item
                        .checklist
                        .service_order
                    ),
                    user=request.user,
                )
            )
        except ValueError as exc:
            transaction.set_rollback(
                True,
            )

            return Response(
                {
                    "part_request": str(exc),
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        self._delete_linked_request_items(
            item,
        )

        created_items = []

        for subpart_data in normalized_subparts:
            component = (
                subpart_data["component"]
            )

            request_item = (
                ServicePartRequestItem.objects
                .create(
                    request=part_request,
                    checklist_item=item,
                    source_component=component,
                    source_component_id_snapshot=(
                        component.id
                    ),
                    parent_component_name=(
                        item.component_name
                    ),
                    component_code=(
                        component.code
                    ),
                    component_name=(
                        component.name
                    ),
                    manufacturer_code=(
                        component.manufacturer_code
                    ),
                    color=component.color,
                    quantity=(
                        subpart_data["quantity"]
                    ),
                    unit_of_measure=(
                        component.unit_of_measure
                    ),
                    urgency=(
                        subpart_data["urgency"]
                    ),
                    reason=(
                        subpart_data["reason"]
                    ),
                    notes=(
                        subpart_data["notes"]
                    ),
                    created_by=request.user,
                    updated_by=request.user,
                )
            )

            created_items.append(
                request_item,
            )

        part_request.updated_by = (
            request.user
        )

        part_request.save(
            update_fields=[
                "updated_by",
                "updated_at",
            ]
        )

        return Response(
            {
                "item": (
                    self.get_serializer(
                        item,
                    ).data
                ),
                "part_request": (
                    ServicePartRequestSerializer(
                        part_request,
                        context={
                            "request": request,
                        },
                    ).data
                ),
                "part_request_items": (
                    ServicePartRequestItemSerializer(
                        created_items,
                        many=True,
                        context={
                            "request": request,
                        },
                    ).data
                ),
                "compatible_subparts": (
                    self
                    ._serialize_compatible_subparts(
                        item,
                        request,
                    )
                ),
            },
            status=status.HTTP_200_OK,
        )


class ServicePartRequestViewSet(
    ArchiveRestoreMixin,
    ActiveRecordsMixin,
    viewsets.ModelViewSet,
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        ServicePartRequestSerializer
    )

    queryset = (
        ServicePartRequest.objects
        .prefetch_related(
            "items",
            "items__source_component",
            "items__checklist_item",
        )
        .select_related(
            "service_order",
            "requested_by",
        )
    )

    filterset_fields = (
        "service_order",
        "status",
        "requested_by",
    )

    ordering = (
        "-created_at",
    )


class ServicePartRequestItemViewSet(
    ArchiveRestoreMixin,
    ActiveRecordsMixin,
    viewsets.ModelViewSet,
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        ServicePartRequestItemSerializer
    )

    queryset = (
        ServicePartRequestItem.objects
        .select_related(
            "request",
            "request__service_order",
            "checklist_item",
            "source_component",
            "source_component__parent_component",
        )
    )

    filterset_fields = (
        "request",
        "checklist_item",
        "source_component",
        "urgency",
    )

    search_fields = (
        "component_code",
        "component_name",
        "manufacturer_code",
        "reason",
    )

    ordering = (
        "created_at",
    )


class ServiceEvidenceViewSet(
    ArchiveRestoreMixin,
    ActiveRecordsMixin,
    viewsets.ModelViewSet,
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        ServiceEvidenceSerializer
    )

    queryset = (
        ServiceEvidence.objects
        .select_related(
            "service_order",
            "captured_by",
        )
    )

    filterset_fields = (
        "service_order",
        "stage",
        "captured_by",
        "is_mock_location",
    )

    ordering = (
        "stage",
        "sequence",
        "captured_at",
    )


class ServiceMeterReadingViewSet(
    ArchiveRestoreMixin,
    ActiveRecordsMixin,
    viewsets.ModelViewSet,
):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        ServiceMeterReadingSerializer
    )

    queryset = (
        ServiceMeterReading.objects
        .select_related(
            "service_order",
            "service_order__equipment",
            (
                "service_order__equipment__"
                "equipment_model"
            ),
        )
    )

    filterset_fields = (
        "service_order",
        "applied_to_equipment_history",
    )

    ordering = (
        "-created_at",
    )