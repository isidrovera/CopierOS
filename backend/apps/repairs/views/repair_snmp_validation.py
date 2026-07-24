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

from ..models import RepairSNMPValidation
from ..serializers import (
    ArchiveRepairSNMPValidationSerializer,
    CompleteRepairSNMPValidationSerializer,
    FailRepairSNMPValidationSerializer,
    RecalculateSNMPMatchesSerializer,
    RepairSNMPValidationCreateUpdateSerializer,
    RepairSNMPValidationDetailSerializer,
    RepairSNMPValidationListSerializer,
    StartRepairSNMPValidationSerializer,
)
from ..services import (
    archive_snmp_validation,
    complete_snmp_validation,
    create_snmp_validation,
    fail_snmp_validation,
    recalculate_snmp_matches,
    restore_snmp_validation,
    start_snmp_validation,
)
from .common import (
    django_validation_error_response,
    get_authenticated_actor,
    get_boolean_query_param,
)


class RepairSNMPValidationViewSet(
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
        "host",
        "system_name",
        "device_description",
        "device_serial_number",
        "detected_brand",
        "detected_model",
        "error_message",
        "observations",
    )

    ordering_fields = (
        "host",
        "port",
        "status",
        "started_at",
        "completed_at",
        "validated_at",
        "is_successful",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    def get_queryset(self):
        queryset = (
            RepairSNMPValidation.objects
            .select_related(
                "repair",
                "repair__equipment",
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

        host = self.request.query_params.get(
            "host"
        )

        if host:
            queryset = queryset.filter(
                host__icontains=host,
            )

        validation_status = (
            self.request.query_params.get(
                "status"
            )
        )

        if validation_status:
            statuses = [
                value.strip()
                for value in validation_status.split(",")
                if value.strip()
            ]

            if statuses:
                queryset = queryset.filter(
                    status__in=statuses,
                )

        is_successful = get_boolean_query_param(
            self.request,
            "is_successful",
            None,
        )

        if is_successful is not None:
            queryset = queryset.filter(
                is_successful=is_successful,
            )

        serial_matches = get_boolean_query_param(
            self.request,
            "serial_matches",
            None,
        )

        if serial_matches is not None:
            queryset = queryset.filter(
                serial_matches=serial_matches,
            )

        brand_matches = get_boolean_query_param(
            self.request,
            "brand_matches",
            None,
        )

        if brand_matches is not None:
            queryset = queryset.filter(
                brand_matches=brand_matches,
            )

        model_matches = get_boolean_query_param(
            self.request,
            "model_matches",
            None,
        )

        if model_matches is not None:
            queryset = queryset.filter(
                model_matches=model_matches,
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairSNMPValidationListSerializer

        if self.action in (
            "create",
            "update",
            "partial_update",
        ):
            return (
                RepairSNMPValidationCreateUpdateSerializer
            )

        return RepairSNMPValidationDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = (
            RepairSNMPValidationCreateUpdateSerializer(
                data=request.data,
                context={
                    "request": request,
                },
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        validated_data = dict(
            serializer.validated_data
        )

        repair = validated_data.pop(
            "repair"
        )

        allowed_fields = {
            "host",
            "port",
            "community",
            "version",
            "timeout",
            "retries",
            "observations",
        }

        service_data = {
            key: value
            for key, value in validated_data.items()
            if key in allowed_fields
        }

        try:
            validation = create_snmp_validation(
                repair=repair,
                actor=actor,
                **service_data,
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairSNMPValidationDetailSerializer(
                validation,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_201_CREATED,
        )

    def perform_destroy(self, instance):
        actor = get_authenticated_actor(
            self.request
        )

        try:
            archive_snmp_validation(
                validation=instance,
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
        url_path="start",
    )
    def start(self, request, pk=None):
        validation = self.get_object()

        serializer = StartRepairSNMPValidationSerializer(
            data=request.data,
            context={
                "request": request,
                "snmp_validation": validation,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            validation = start_snmp_validation(
                validation=validation,
                actor=actor,
                host=serializer.validated_data.get(
                    "host"
                ),
                port=serializer.validated_data.get(
                    "port"
                ),
                community=serializer.validated_data.get(
                    "community"
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairSNMPValidationDetailSerializer(
                validation,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="complete",
    )
    def complete(self, request, pk=None):
        validation = self.get_object()

        serializer = (
            CompleteRepairSNMPValidationSerializer(
                data=request.data,
                context={
                    "request": request,
                    "snmp_validation": validation,
                },
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            validation = complete_snmp_validation(
                validation=validation,
                actor=actor,
                raw_data=serializer.validated_data.get(
                    "raw_data"
                ),
                observations=(
                    serializer.validated_data.get(
                        "observations",
                        "",
                    )
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairSNMPValidationDetailSerializer(
                validation,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="fail",
    )
    def fail(self, request, pk=None):
        validation = self.get_object()

        serializer = FailRepairSNMPValidationSerializer(
            data=request.data,
            context={
                "request": request,
                "snmp_validation": validation,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            validation = fail_snmp_validation(
                validation=validation,
                actor=actor,
                error_message=(
                    serializer.validated_data[
                        "error_message"
                    ]
                ),
                observations=(
                    serializer.validated_data.get(
                        "observations",
                        "",
                    )
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairSNMPValidationDetailSerializer(
                validation,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="recalculate-matches",
    )
    def recalculate_matches(
        self,
        request,
        pk=None,
    ):
        validation = self.get_object()

        serializer = RecalculateSNMPMatchesSerializer(
            data=request.data,
            context={
                "request": request,
                "snmp_validation": validation,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            validation = recalculate_snmp_matches(
                validation=validation,
                actor=actor,
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairSNMPValidationDetailSerializer(
                validation,
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
        validation = get_object_or_404(
            RepairSNMPValidation.objects.all(),
            pk=pk,
        )

        serializer = (
            ArchiveRepairSNMPValidationSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            validation = archive_snmp_validation(
                validation=validation,
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
            RepairSNMPValidationDetailSerializer(
                validation,
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
        validation = get_object_or_404(
            RepairSNMPValidation.objects.all(),
            pk=pk,
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            validation = restore_snmp_validation(
                validation=validation,
                actor=actor,
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairSNMPValidationDetailSerializer(
                validation,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )