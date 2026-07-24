# -*- coding: utf-8 -*-
from django.db.models import (
    Count,
    Prefetch,
    Q,
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

from ..models import (
    Repair,
    RepairAssignment,
    RepairChecklist,
    RepairDiagnosis,
    RepairPhoto,
    RepairSNMPValidation,
    RepairTest,
)
from ..serializers import (
    ArchiveRepairSerializer,
    RepairAssignmentActionSerializer,
    RepairCreateUpdateSerializer,
    RepairDetailSerializer,
    RepairListSerializer,
    RepairStatusChangeSerializer,
)
from ..services import (
    assign_repair,
    cancel_repair,
    change_repair_status,
    reopen_completed_repair,
)
from .common import (
    django_validation_error_response,
    get_authenticated_actor,
    get_boolean_query_param,
)


class RepairViewSet(viewsets.ModelViewSet):
    permission_classes = (
        IsAuthenticated,
    )

    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    search_fields = (
        "code",
        "equipment__serial_number",
        "equipment__internal_code",
        "equipment__equipment_model__name",
        "equipment__equipment_model__commercial_name",
        "equipment__equipment_model__brand__name",
        "reported_problem",
        "initial_observations",
        "work_summary",
        "assigned_technician__first_name",
        "assigned_technician__last_name",
        "assigned_technician__email",
    )

    ordering_fields = (
        "code",
        "requested_at",
        "assigned_at",
        "repair_started_at",
        "completed_at",
        "delivered_at",
        "created_at",
        "updated_at",
        "priority",
        "status",
    )

    ordering = (
        "-created_at",
    )

    def get_queryset(self):
        queryset = (
            Repair.objects
            .select_related(
                "equipment",
                "equipment__equipment_model",
                "equipment__equipment_model__brand",
                "equipment__equipment_model__equipment_type",
                "requested_by",
                "assigned_technician",
                "assigned_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .prefetch_related(
                Prefetch(
                    "assignments",
                    queryset=(
                        RepairAssignment.objects
                        .select_related(
                            "technician",
                            "assigned_by",
                        )
                        .order_by(
                            "-assigned_at"
                        )
                    ),
                ),
                Prefetch(
                    "diagnoses",
                    queryset=(
                        RepairDiagnosis.objects
                        .select_related(
                            "technician",
                            "confirmed_by",
                        )
                        .order_by(
                            "-is_main_diagnosis",
                            "-diagnosed_at",
                        )
                    ),
                ),
                Prefetch(
                    "checklists",
                    queryset=(
                        RepairChecklist.objects
                        .prefetch_related(
                            "items",
                        )
                        .order_by(
                            "-is_main_checklist",
                            "created_at",
                        )
                    ),
                ),
                Prefetch(
                    "photos",
                    queryset=(
                        RepairPhoto.objects
                        .select_related(
                            "checklist_item",
                            "taken_by",
                            "uploaded_by",
                            "verified_by",
                        )
                        .order_by(
                            "display_order",
                            "created_at",
                        )
                    ),
                ),
                Prefetch(
                    "tests",
                    queryset=(
                        RepairTest.objects
                        .select_related(
                            "tested_by",
                        )
                        .order_by(
                            "display_order",
                            "created_at",
                        )
                    ),
                ),
                Prefetch(
                    "snmp_validations",
                    queryset=(
                        RepairSNMPValidation.objects
                        .order_by(
                            "-created_at"
                        )
                    ),
                ),
            )
            .annotate(
                total_photos=Count(
                    "photos",
                    filter=Q(
                        photos__archived_at__isnull=True,
                    ),
                    distinct=True,
                ),
                total_tests=Count(
                    "tests",
                    filter=Q(
                        tests__archived_at__isnull=True,
                    ),
                    distinct=True,
                ),
                total_diagnoses=Count(
                    "diagnoses",
                    filter=Q(
                        diagnoses__archived_at__isnull=True,
                    ),
                    distinct=True,
                ),
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

        equipment_id = self.request.query_params.get(
            "equipment"
        )

        if equipment_id:
            queryset = queryset.filter(
                equipment_id=equipment_id,
            )

        technician_id = (
            self.request.query_params.get(
                "assigned_technician"
            )
            or self.request.query_params.get(
                "technician"
            )
        )

        if technician_id:
            queryset = queryset.filter(
                assigned_technician_id=technician_id,
            )

        requested_by_id = self.request.query_params.get(
            "requested_by"
        )

        if requested_by_id:
            queryset = queryset.filter(
                requested_by_id=requested_by_id,
            )

        repair_type = self.request.query_params.get(
            "repair_type"
        )

        if repair_type:
            queryset = queryset.filter(
                repair_type=repair_type,
            )

        repair_status = self.request.query_params.get(
            "status"
        )

        if repair_status:
            statuses = [
                value.strip()
                for value in repair_status.split(",")
                if value.strip()
            ]

            if statuses:
                queryset = queryset.filter(
                    status__in=statuses,
                )

        priority = self.request.query_params.get(
            "priority"
        )

        if priority:
            priorities = [
                value.strip()
                for value in priority.split(",")
                if value.strip()
            ]

            if priorities:
                queryset = queryset.filter(
                    priority__in=priorities,
                )

        is_active = get_boolean_query_param(
            self.request,
            "is_active",
            None,
        )

        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active,
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

        requires_follow_up = (
            get_boolean_query_param(
                self.request,
                "requires_follow_up",
                None,
            )
        )

        if requires_follow_up is not None:
            queryset = queryset.filter(
                requires_follow_up=requires_follow_up,
            )

        requested_from = self.request.query_params.get(
            "requested_from"
        )

        if requested_from:
            queryset = queryset.filter(
                requested_at__date__gte=requested_from,
            )

        requested_to = self.request.query_params.get(
            "requested_to"
        )

        if requested_to:
            queryset = queryset.filter(
                requested_at__date__lte=requested_to,
            )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return RepairListSerializer

        if self.action in (
            "create",
            "update",
            "partial_update",
        ):
            return RepairCreateUpdateSerializer

        return RepairDetailSerializer

    def perform_destroy(self, instance):
        actor = get_authenticated_actor(
            self.request
        )

        instance.archive(
            user=actor,
            reason="Archivado desde la API.",
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="assign",
    )
    def assign(self, request, pk=None):
        repair = self.get_object()

        serializer = (
            RepairAssignmentActionSerializer(
                data=request.data,
                context={
                    "request": request,
                    "repair": repair,
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
            assign_repair(
                repair=repair,
                technician=(
                    serializer.validated_data[
                        "technician"
                    ]
                ),
                actor=actor,
                reason=(
                    serializer.validated_data.get(
                        "reason",
                        "",
                    )
                ),
            )
        except Exception as exception:
            from django.core.exceptions import (
                ValidationError as DjangoValidationError,
            )

            if isinstance(
                exception,
                DjangoValidationError,
            ):
                return django_validation_error_response(
                    exception
                )

            raise

        repair.refresh_from_db()

        return Response(
            RepairDetailSerializer(
                repair,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="change-status",
    )
    def change_status(self, request, pk=None):
        repair = self.get_object()

        serializer = RepairStatusChangeSerializer(
            data=request.data,
            context={
                "request": request,
                "repair": repair,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        validated_data = serializer.validated_data

        editable_fields = (
            "final_condition",
            "work_summary",
            "final_observations",
            "closure_notes",
        )

        changed_fields = []

        for field_name in editable_fields:
            if field_name in validated_data:
                setattr(
                    repair,
                    field_name,
                    validated_data[field_name],
                )

                changed_fields.append(
                    field_name
                )

        if changed_fields:
            repair.updated_by = actor

            changed_fields.extend(
                (
                    "updated_by",
                    "updated_at",
                )
            )

            repair.full_clean()

            repair.save(
                update_fields=changed_fields,
            )

        try:
            repair = change_repair_status(
                repair=repair,
                new_status=(
                    validated_data["status"]
                ),
                actor=actor,
                reason=validated_data.get(
                    "reason",
                    "",
                ),
                observations=validated_data.get(
                    "observations",
                    "",
                ),
                source="api",
            )
        except Exception as exception:
            from django.core.exceptions import (
                ValidationError as DjangoValidationError,
            )

            if isinstance(
                exception,
                DjangoValidationError,
            ):
                return django_validation_error_response(
                    exception
                )

            raise

        return Response(
            RepairDetailSerializer(
                repair,
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
        repair = self.get_object()

        reason = str(
            request.data.get(
                "reason",
                "",
            )
            or ""
        ).strip()

        actor = get_authenticated_actor(
            request
        )

        try:
            repair = cancel_repair(
                repair=repair,
                actor=actor,
                reason=reason,
            )
        except Exception as exception:
            from django.core.exceptions import (
                ValidationError as DjangoValidationError,
            )

            if isinstance(
                exception,
                DjangoValidationError,
            ):
                return django_validation_error_response(
                    exception
                )

            raise

        return Response(
            RepairDetailSerializer(
                repair,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="reopen",
    )
    def reopen(self, request, pk=None):
        repair = self.get_object()

        reason = str(
            request.data.get(
                "reason",
                "",
            )
            or ""
        ).strip()

        actor = get_authenticated_actor(
            request
        )

        try:
            repair = reopen_completed_repair(
                repair=repair,
                actor=actor,
                reason=reason,
            )
        except Exception as exception:
            from django.core.exceptions import (
                ValidationError as DjangoValidationError,
            )

            if isinstance(
                exception,
                DjangoValidationError,
            ):
                return django_validation_error_response(
                    exception
                )

            raise

        return Response(
            RepairDetailSerializer(
                repair,
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
        repair = get_object_or_404(
            Repair.objects.all(),
            pk=pk,
        )

        serializer = ArchiveRepairSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True
        )

        if repair.archived_at is not None:
            return Response(
                {
                    "detail": (
                        "La reparación ya se encuentra archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if repair.is_active:
            return Response(
                {
                    "detail": (
                        "No puedes archivar una reparación activa."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        actor = get_authenticated_actor(
            request
        )

        repair.archive(
            user=actor,
            reason=serializer.validated_data.get(
                "reason",
                "",
            ),
        )

        return Response(
            RepairDetailSerializer(
                repair,
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
        repair = get_object_or_404(
            Repair.objects.all(),
            pk=pk,
        )

        if repair.archived_at is None:
            return Response(
                {
                    "detail": (
                        "La reparación no se encuentra archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        active_repair_exists = (
            Repair.objects.filter(
                equipment=repair.equipment,
                is_active=True,
                archived_at__isnull=True,
            )
            .exclude(
                pk=repair.pk,
            )
            .exists()
        )

        if active_repair_exists:
            return Response(
                {
                    "equipment": (
                        "El equipo ya tiene otra reparación activa."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        actor = get_authenticated_actor(
            request
        )

        repair.restore(
            user=actor,
        )

        return Response(
            RepairDetailSerializer(
                repair,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=("get",),
        url_path="active-by-equipment",
    )
    def active_by_equipment(self, request):
        equipment_id = request.query_params.get(
            "equipment"
        )

        if not equipment_id:
            return Response(
                {
                    "equipment": (
                        "Debes indicar el ID del equipo."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        repair = (
            self.get_queryset()
            .filter(
                equipment_id=equipment_id,
                is_active=True,
                archived_at__isnull=True,
            )
            .first()
        )

        if not repair:
            return Response(
                {
                    "detail": (
                        "El equipo no tiene una reparación activa."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            RepairDetailSerializer(
                repair,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )