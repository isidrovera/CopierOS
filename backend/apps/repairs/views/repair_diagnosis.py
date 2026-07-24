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

from ..models import RepairDiagnosis
from ..serializers import (
    ArchiveRepairDiagnosisSerializer,
    ConfirmRepairDiagnosisSerializer,
    RepairDiagnosisCreateUpdateSerializer,
    RepairDiagnosisDetailSerializer,
    RepairDiagnosisListSerializer,
    SetMainRepairDiagnosisSerializer,
)
from ..services import (
    archive_repair_diagnosis,
    confirm_repair_diagnosis,
    create_repair_diagnosis,
    restore_repair_diagnosis,
    set_main_repair_diagnosis,
    update_repair_diagnosis,
)
from .common import (
    django_validation_error_response,
    get_authenticated_actor,
    get_boolean_query_param,
)


class RepairDiagnosisViewSet(
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
        "technician__first_name",
        "technician__last_name",
        "technician__email",
        "reported_symptoms",
        "observed_symptoms",
        "probable_cause",
        "confirmed_cause",
        "technical_diagnosis",
        "recommended_work",
        "required_parts_description",
        "observations",
    )

    ordering_fields = (
        "diagnosed_at",
        "diagnosis_type",
        "severity",
        "repairability",
        "is_main_diagnosis",
        "is_confirmed",
        "confirmed_at",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-is_main_diagnosis",
        "-diagnosed_at",
        "-created_at",
    )

    def get_queryset(self):
        queryset = (
            RepairDiagnosis.objects
            .select_related(
                "repair",
                "repair__equipment",
                "technician",
                "confirmed_by",
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

        technician_id = self.request.query_params.get(
            "technician"
        )

        if technician_id:
            queryset = queryset.filter(
                technician_id=technician_id,
            )

        diagnosis_type = (
            self.request.query_params.get(
                "diagnosis_type"
            )
        )

        if diagnosis_type:
            values = [
                value.strip()
                for value in diagnosis_type.split(",")
                if value.strip()
            ]

            if values:
                queryset = queryset.filter(
                    diagnosis_type__in=values,
                )

        severity = self.request.query_params.get(
            "severity"
        )

        if severity:
            values = [
                value.strip()
                for value in severity.split(",")
                if value.strip()
            ]

            if values:
                queryset = queryset.filter(
                    severity__in=values,
                )

        repairability = (
            self.request.query_params.get(
                "repairability"
            )
        )

        if repairability:
            values = [
                value.strip()
                for value in repairability.split(",")
                if value.strip()
            ]

            if values:
                queryset = queryset.filter(
                    repairability__in=values,
                )

        is_main_diagnosis = (
            get_boolean_query_param(
                self.request,
                "is_main_diagnosis",
                None,
            )
        )

        if is_main_diagnosis is not None:
            queryset = queryset.filter(
                is_main_diagnosis=(
                    is_main_diagnosis
                ),
            )

        is_confirmed = get_boolean_query_param(
            self.request,
            "is_confirmed",
            None,
        )

        if is_confirmed is not None:
            queryset = queryset.filter(
                is_confirmed=is_confirmed,
            )

        requires_parts = get_boolean_query_param(
            self.request,
            "requires_parts",
            None,
        )

        if requires_parts is not None:
            queryset = queryset.filter(
                requires_parts=requires_parts,
            )

        requires_external_service = (
            get_boolean_query_param(
                self.request,
                "requires_external_service",
                None,
            )
        )

        if requires_external_service is not None:
            queryset = queryset.filter(
                requires_external_service=(
                    requires_external_service
                ),
            )

        requires_additional_testing = (
            get_boolean_query_param(
                self.request,
                "requires_additional_testing",
                None,
            )
        )

        if requires_additional_testing is not None:
            queryset = queryset.filter(
                requires_additional_testing=(
                    requires_additional_testing
                ),
            )

        requires_disassembly = (
            get_boolean_query_param(
                self.request,
                "requires_disassembly",
                None,
            )
        )

        if requires_disassembly is not None:
            queryset = queryset.filter(
                requires_disassembly=(
                    requires_disassembly
                ),
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairDiagnosisListSerializer

        if self.action in (
            "create",
            "update",
            "partial_update",
        ):
            return RepairDiagnosisCreateUpdateSerializer

        return RepairDiagnosisDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = (
            RepairDiagnosisCreateUpdateSerializer(
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

        try:
            diagnosis = create_repair_diagnosis(
                repair=repair,
                actor=actor,
                **validated_data,
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairDiagnosisDetailSerializer(
                diagnosis,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop(
            "partial",
            False,
        )

        diagnosis = self.get_object()

        serializer = (
            RepairDiagnosisCreateUpdateSerializer(
                diagnosis,
                data=request.data,
                partial=partial,
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

        validated_data.pop(
            "repair",
            None,
        )

        try:
            diagnosis = update_repair_diagnosis(
                diagnosis=diagnosis,
                actor=actor,
                **validated_data,
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairDiagnosisDetailSerializer(
                diagnosis,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    def partial_update(
        self,
        request,
        *args,
        **kwargs,
    ):
        kwargs["partial"] = True

        return self.update(
            request,
            *args,
            **kwargs,
        )

    def perform_destroy(self, instance):
        actor = get_authenticated_actor(
            self.request
        )

        archive_repair_diagnosis(
            diagnosis=instance,
            actor=actor,
            reason="Archivado desde la API.",
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="confirm",
    )
    def confirm(self, request, pk=None):
        diagnosis = self.get_object()

        serializer = (
            ConfirmRepairDiagnosisSerializer(
                data=request.data,
                context={
                    "request": request,
                    "diagnosis": diagnosis,
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
            diagnosis = confirm_repair_diagnosis(
                diagnosis=diagnosis,
                actor=actor,
                confirmed_cause=(
                    serializer.validated_data.get(
                        "confirmed_cause",
                        "",
                    )
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
            RepairDiagnosisDetailSerializer(
                diagnosis,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="set-main",
    )
    def set_main(self, request, pk=None):
        diagnosis = self.get_object()

        serializer = (
            SetMainRepairDiagnosisSerializer(
                data=request.data,
                context={
                    "request": request,
                    "diagnosis": diagnosis,
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
            diagnosis = set_main_repair_diagnosis(
                diagnosis=diagnosis,
                actor=actor,
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairDiagnosisDetailSerializer(
                diagnosis,
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
        diagnosis = get_object_or_404(
            RepairDiagnosis.objects.all(),
            pk=pk,
        )

        serializer = (
            ArchiveRepairDiagnosisSerializer(
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
            diagnosis = archive_repair_diagnosis(
                diagnosis=diagnosis,
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
            RepairDiagnosisDetailSerializer(
                diagnosis,
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
        diagnosis = get_object_or_404(
            RepairDiagnosis.objects.all(),
            pk=pk,
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            diagnosis = restore_repair_diagnosis(
                diagnosis=diagnosis,
                actor=actor,
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairDiagnosisDetailSerializer(
                diagnosis,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )