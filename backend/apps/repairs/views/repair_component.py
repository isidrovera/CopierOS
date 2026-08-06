# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.shortcuts import get_object_or_404
from rest_framework import (
    filters,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import RepairComponent
from ..serializers import (
    ArchiveRepairComponentSerializer,
    CancelRepairComponentSerializer,
    ConsumeRepairComponentSerializer,
    DeliverRepairComponentSerializer,
    InstallRepairComponentSerializer,
    RepairComponentCreateUpdateSerializer,
    RepairComponentDetailSerializer,
    RepairComponentListSerializer,
    RequestRepairComponentSerializer,
    ReserveRepairComponentSerializer,
    ReturnRepairComponentSerializer,
)
from ..services import (
    archive_repair_component,
    cancel_component_request,
    consume_component,
    deliver_component,
    install_component,
    request_component,
    reserve_component,
    restore_repair_component,
    return_component,
)
from .common import (
    django_validation_error_response,
    get_authenticated_actor,
    get_boolean_query_param,
)


class RepairComponentViewSet(
    viewsets.ModelViewSet
):
    permission_classes = (
        IsAuthenticated,
    )

    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    search_fields = (
        "repair__code",
        "repair__equipment__serial_number",
        "component__code",
        "component__name",
        "component__component_type__name",
        "inventory__internal_code",
        "inventory__serial_number",
        "removed_component__code",
        "removed_component__name",
        "removed_serial_number",
        "notes",
        "removed_part_notes",
    )

    ordering_fields = (
        "status",
        "movement_type",
        "quantity",
        "requested_at",
        "reserved_at",
        "delivered_at",
        "installed_at",
        "removed_at",
        "returned_at",
        "unit_cost",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    def get_queryset(self):
        queryset = (
            RepairComponent.objects
            .select_related(
                "repair",
                "repair__equipment",
                "component",
                "component__component_type",
                "removed_component",
                "requested_by",
                "reserved_by",
                "delivered_by",
                "installed_by",
                "removed_by",
                "returned_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
        )

        include_archived = get_boolean_query_param(
            self.request,
            "include_archived",
            False,
        )

        if not include_archived:
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        repair_id = self.request.query_params.get(
            "repair"
        )

        if repair_id:
            queryset = queryset.filter(
                repair_id=repair_id,
            )

        equipment_id = self.request.query_params.get(
            "equipment"
        )

        if equipment_id:
            queryset = queryset.filter(
                repair__equipment_id=equipment_id,
            )

        component_id = self.request.query_params.get(
            "component"
        )

        if component_id:
            queryset = queryset.filter(
                component_id=component_id,
            )

        inventory_id = self.request.query_params.get(
            "inventory"
        )

        if inventory_id:
            queryset = queryset.filter(
                inventory_id=inventory_id,
            )

        movement_type = self.request.query_params.get(
            "movement_type"
        )

        if movement_type:
            movement_types = [
                value.strip()
                for value in movement_type.split(",")
                if value.strip()
            ]

            if movement_types:
                queryset = queryset.filter(
                    movement_type__in=movement_types,
                )

        component_status = (
            self.request.query_params.get(
                "status"
            )
        )

        if component_status:
            statuses = [
                value.strip()
                for value in component_status.split(",")
                if value.strip()
            ]

            if statuses:
                queryset = queryset.filter(
                    status__in=statuses,
                )

        has_inventory = get_boolean_query_param(
            self.request,
            "has_inventory",
            None,
        )

        if has_inventory is True:
            queryset = queryset.filter(
                inventory__isnull=False,
            )

        elif has_inventory is False:
            queryset = queryset.filter(
                inventory__isnull=True,
            )

        has_removed_component = (
            get_boolean_query_param(
                self.request,
                "has_removed_component",
                None,
            )
        )

        if has_removed_component is True:
            queryset = queryset.filter(
                removed_component__isnull=False,
            )

        elif has_removed_component is False:
            queryset = queryset.filter(
                removed_component__isnull=True,
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairComponentListSerializer

        if self.action in (
            "create",
            "update",
            "partial_update",
        ):
            return RepairComponentCreateUpdateSerializer

        return RepairComponentDetailSerializer

    def perform_destroy(self, instance):
        actor = get_authenticated_actor(
            self.request
        )

        try:
            archive_repair_component(
                repair_component=instance,
                actor=actor,
                reason="Archivado desde la API.",
            )
        except DjangoValidationError as exception:
            from rest_framework.exceptions import (
                ValidationError as DRFValidationError,
            )

            if hasattr(
                exception,
                "message_dict",
            ):
                raise DRFValidationError(
                    exception.message_dict
                ) from exception

            raise DRFValidationError(
                exception.messages
            ) from exception

    @action(
        detail=True,
        methods=("post",),
        url_path="request-component",
    )
    def request_component_action(
        self,
        request,
        pk=None,
    ):
        repair_component = self.get_object()

        serializer = RequestRepairComponentSerializer(
            data=request.data,
            context={
                "request": request,
                "repair_component": repair_component,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            repair_component = request_component(
                repair_component=repair_component,
                actor=actor,
                notes=serializer.validated_data.get(
                    "notes",
                    "",
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairComponentDetailSerializer(
                repair_component,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="reserve",
    )
    def reserve(self, request, pk=None):
        repair_component = self.get_object()

        serializer = ReserveRepairComponentSerializer(
            data=request.data,
            context={
                "request": request,
                "repair_component": repair_component,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            repair_component = reserve_component(
                repair_component=repair_component,
                inventory=(
                    serializer.validated_data[
                        "inventory"
                    ]
                ),
                quantity=(
                    serializer.validated_data[
                        "quantity"
                    ]
                ),
                actor=actor,
                notes=serializer.validated_data.get(
                    "notes",
                    "",
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairComponentDetailSerializer(
                repair_component,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="deliver",
    )
    def deliver(self, request, pk=None):
        repair_component = self.get_object()

        serializer = DeliverRepairComponentSerializer(
            data=request.data,
            context={
                "request": request,
                "repair_component": repair_component,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            repair_component = deliver_component(
                repair_component=repair_component,
                quantity=(
                    serializer.validated_data[
                        "quantity"
                    ]
                ),
                actor=actor,
                notes=serializer.validated_data.get(
                    "notes",
                    "",
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairComponentDetailSerializer(
                repair_component,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="install",
    )
    def install(self, request, pk=None):
        repair_component = self.get_object()

        serializer = InstallRepairComponentSerializer(
            data=request.data,
            context={
                "request": request,
                "repair_component": repair_component,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            repair_component = install_component(
                repair_component=repair_component,
                quantity=(
                    serializer.validated_data[
                        "quantity"
                    ]
                ),
                actor=actor,
                removed_component=(
                    serializer.validated_data.get(
                        "removed_component"
                    )
                ),
                removed_inventory=(
                    serializer.validated_data.get(
                        "removed_inventory"
                    )
                ),
                removed_serial_number=(
                    serializer.validated_data.get(
                        "removed_serial_number",
                        "",
                    )
                ),
                removed_part_disposition=(
                    serializer.validated_data.get(
                        "removed_part_disposition"
                    )
                ),
                removed_part_notes=(
                    serializer.validated_data.get(
                        "removed_part_notes",
                        "",
                    )
                ),
                notes=serializer.validated_data.get(
                    "notes",
                    "",
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairComponentDetailSerializer(
                repair_component,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="consume",
    )
    def consume(self, request, pk=None):
        repair_component = self.get_object()

        serializer = ConsumeRepairComponentSerializer(
            data=request.data,
            context={
                "request": request,
                "repair_component": repair_component,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            repair_component = consume_component(
                repair_component=repair_component,
                quantity=(
                    serializer.validated_data[
                        "quantity"
                    ]
                ),
                actor=actor,
                removed_component=(
                    serializer.validated_data.get(
                        "removed_component"
                    )
                ),
                removed_part_disposition=(
                    serializer.validated_data.get(
                        "removed_part_disposition"
                    )
                ),
                notes=serializer.validated_data.get(
                    "notes",
                    "",
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairComponentDetailSerializer(
                repair_component,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="return",
    )
    def return_component_action(
        self,
        request,
        pk=None,
    ):
        repair_component = self.get_object()

        serializer = ReturnRepairComponentSerializer(
            data=request.data,
            context={
                "request": request,
                "repair_component": repair_component,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            repair_component = return_component(
                repair_component=repair_component,
                quantity=(
                    serializer.validated_data[
                        "quantity"
                    ]
                ),
                actor=actor,
                notes=serializer.validated_data.get(
                    "notes",
                    "",
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairComponentDetailSerializer(
                repair_component,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="cancel",
    )
    def cancel(self, request, pk=None):
        repair_component = self.get_object()

        serializer = CancelRepairComponentSerializer(
            data=request.data,
            context={
                "request": request,
                "repair_component": repair_component,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            repair_component = cancel_component_request(
                repair_component=repair_component,
                actor=actor,
                reason=(
                    serializer.validated_data[
                        "reason"
                    ]
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairComponentDetailSerializer(
                repair_component,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="archive",
    )
    def archive(self, request, pk=None):
        repair_component = get_object_or_404(
            RepairComponent.objects.all(),
            pk=pk,
        )

        serializer = ArchiveRepairComponentSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            repair_component = archive_repair_component(
                repair_component=repair_component,
                actor=actor,
                reason=serializer.validated_data.get(
                    "reason",
                    "",
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairComponentDetailSerializer(
                repair_component,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore(self, request, pk=None):
        repair_component = get_object_or_404(
            RepairComponent.objects.all(),
            pk=pk,
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            repair_component = restore_repair_component(
                repair_component=repair_component,
                actor=actor,
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairComponentDetailSerializer(
                repair_component,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )