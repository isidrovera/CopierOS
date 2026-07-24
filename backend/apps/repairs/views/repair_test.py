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

from ..models import RepairTest
from ..serializers import (
    ArchiveRepairTestSerializer,
    PerformRepairTestSerializer,
    RepairTestCreateUpdateSerializer,
    RepairTestDetailSerializer,
    RepairTestListSerializer,
    ResetRepairTestSerializer,
)
from ..services import (
    archive_repair_test,
    create_repair_test,
    perform_repair_test,
    reset_repair_test,
    restore_repair_test,
)
from .common import (
    django_validation_error_response,
    get_authenticated_actor,
    get_boolean_query_param,
)


class RepairTestViewSet(
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
        "name",
        "description",
        "instructions",
        "error_code",
        "measurement_unit",
        "observations",
        "failure_description",
        "corrective_action",
        "tested_by__first_name",
        "tested_by__last_name",
        "tested_by__email",
    )

    ordering_fields = (
        "test_type",
        "stage",
        "name",
        "result",
        "is_required",
        "requires_photo",
        "requires_print_sample",
        "tested_at",
        "pages_tested",
        "retest_required",
        "display_order",
        "created_at",
        "updated_at",
    )

    ordering = (
        "display_order",
        "created_at",
    )

    def get_queryset(self):
        queryset = (
            RepairTest.objects
            .select_related(
                "repair",
                "repair__equipment",
                "tested_by",
                "retest_of",
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

        test_type = self.request.query_params.get(
            "test_type"
        )

        if test_type:
            test_types = [
                value.strip()
                for value in test_type.split(",")
                if value.strip()
            ]

            if test_types:
                queryset = queryset.filter(
                    test_type__in=test_types,
                )

        stage = self.request.query_params.get(
            "stage"
        )

        if stage:
            stages = [
                value.strip()
                for value in stage.split(",")
                if value.strip()
            ]

            if stages:
                queryset = queryset.filter(
                    stage__in=stages,
                )

        result = self.request.query_params.get(
            "result"
        )

        if result:
            results = [
                value.strip()
                for value in result.split(",")
                if value.strip()
            ]

            if results:
                queryset = queryset.filter(
                    result__in=results,
                )

        tested_by_id = self.request.query_params.get(
            "tested_by"
        )

        if tested_by_id:
            queryset = queryset.filter(
                tested_by_id=tested_by_id,
            )

        is_required = get_boolean_query_param(
            self.request,
            "is_required",
            None,
        )

        if is_required is not None:
            queryset = queryset.filter(
                is_required=is_required,
            )

        requires_photo = get_boolean_query_param(
            self.request,
            "requires_photo",
            None,
        )

        if requires_photo is not None:
            queryset = queryset.filter(
                requires_photo=requires_photo,
            )

        requires_print_sample = (
            get_boolean_query_param(
                self.request,
                "requires_print_sample",
                None,
            )
        )

        if requires_print_sample is not None:
            queryset = queryset.filter(
                requires_print_sample=(
                    requires_print_sample
                ),
            )

        retest_required = get_boolean_query_param(
            self.request,
            "retest_required",
            None,
        )

        if retest_required is not None:
            queryset = queryset.filter(
                retest_required=retest_required,
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairTestListSerializer

        if self.action in (
            "create",
            "update",
            "partial_update",
        ):
            return RepairTestCreateUpdateSerializer

        return RepairTestDetailSerializer

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):
        serializer = RepairTestCreateUpdateSerializer(
            data=request.data,
            context={
                "request": request,
            },
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

        try:
            repair_test = create_repair_test(
                repair=repair,
                actor=actor,
                **validated_data,
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairTestDetailSerializer(
                repair_test,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_201_CREATED,
        )

    def perform_destroy(
        self,
        instance,
    ):
        actor = get_authenticated_actor(
            self.request
        )

        try:
            archive_repair_test(
                repair_test=instance,
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
        url_path="perform",
    )
    def perform(
        self,
        request,
        pk=None,
    ):
        repair_test = self.get_object()

        serializer = PerformRepairTestSerializer(
            data=request.data,
            context={
                "request": request,
                "repair_test": repair_test,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            repair_test = perform_repair_test(
                repair_test=repair_test,
                result=(
                    serializer.validated_data[
                        "result"
                    ]
                ),
                actor=actor,
                measured_value=(
                    serializer.validated_data.get(
                        "measured_value",
                        None,
                    )
                ),
                measurement_unit=(
                    serializer.validated_data.get(
                        "measurement_unit",
                        "",
                    )
                ),
                initial_meter_total=(
                    serializer.validated_data.get(
                        "initial_meter_total",
                        None,
                    )
                ),
                final_meter_total=(
                    serializer.validated_data.get(
                        "final_meter_total",
                        None,
                    )
                ),
                initial_meter_black=(
                    serializer.validated_data.get(
                        "initial_meter_black",
                        None,
                    )
                ),
                final_meter_black=(
                    serializer.validated_data.get(
                        "final_meter_black",
                        None,
                    )
                ),
                initial_meter_color=(
                    serializer.validated_data.get(
                        "initial_meter_color",
                        None,
                    )
                ),
                final_meter_color=(
                    serializer.validated_data.get(
                        "final_meter_color",
                        None,
                    )
                ),
                pages_tested=(
                    serializer.validated_data.get(
                        "pages_tested",
                        0,
                    )
                ),
                error_code=(
                    serializer.validated_data.get(
                        "error_code",
                        "",
                    )
                ),
                observations=(
                    serializer.validated_data.get(
                        "observations",
                        "",
                    )
                ),
                failure_description=(
                    serializer.validated_data.get(
                        "failure_description",
                        "",
                    )
                ),
                corrective_action=(
                    serializer.validated_data.get(
                        "corrective_action",
                        "",
                    )
                ),
                retest_required=(
                    serializer.validated_data.get(
                        "retest_required",
                        False,
                    )
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairTestDetailSerializer(
                repair_test,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="reset",
    )
    def reset(
        self,
        request,
        pk=None,
    ):
        repair_test = self.get_object()

        serializer = ResetRepairTestSerializer(
            data=request.data,
            context={
                "request": request,
                "repair_test": repair_test,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            repair_test = reset_repair_test(
                repair_test=repair_test,
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
            RepairTestDetailSerializer(
                repair_test,
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
    def archive(
        self,
        request,
        pk=None,
    ):
        repair_test = get_object_or_404(
            RepairTest.objects.all(),
            pk=pk,
        )

        serializer = ArchiveRepairTestSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            repair_test = archive_repair_test(
                repair_test=repair_test,
                actor=actor,
                reason=(
                    serializer.validated_data.get(
                        "reason",
                        "",
                    )
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairTestDetailSerializer(
                repair_test,
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
    def restore(
        self,
        request,
        pk=None,
    ):
        repair_test = get_object_or_404(
            RepairTest.objects.all(),
            pk=pk,
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            repair_test = restore_repair_test(
                repair_test=repair_test,
                actor=actor,
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairTestDetailSerializer(
                repair_test,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )