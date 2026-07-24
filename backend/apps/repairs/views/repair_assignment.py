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

from ..models import RepairAssignment
from ..serializers import (
    ArchiveRepairAssignmentSerializer,
    RepairAssignmentAcceptSerializer,
    RepairAssignmentCancelSerializer,
    RepairAssignmentCompleteSerializer,
    RepairAssignmentCreateSerializer,
    RepairAssignmentDetailSerializer,
    RepairAssignmentListSerializer,
    RepairAssignmentReassignSerializer,
    RepairAssignmentRejectSerializer,
    RepairAssignmentStartSerializer,
    RepairAssignmentUpdateSerializer,
)
from ..services import (
    accept_repair_assignment,
    archive_repair_assignment,
    cancel_repair_assignment,
    complete_repair_assignment,
    create_repair_assignment,
    reassign_repair_assignment,
    reject_repair_assignment,
    restore_repair_assignment,
    start_repair_assignment,
)
from .common import (
    django_validation_error_response,
    get_authenticated_actor,
    get_boolean_query_param,
)


class RepairAssignmentViewSet(
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
        "assignment_reason",
        "technician_observations",
        "completion_notes",
        "reassignment_reason",
        "rejection_reason",
        "cancellation_reason",
    )

    ordering_fields = (
        "assigned_at",
        "accepted_at",
        "started_at",
        "ended_at",
        "reassigned_at",
        "rejected_at",
        "cancelled_at",
        "created_at",
        "updated_at",
        "status",
        "is_active",
    )

    ordering = (
        "-assigned_at",
        "-created_at",
    )

    def get_queryset(self):
        queryset = (
            RepairAssignment.objects
            .select_related(
                "repair",
                "repair__equipment",
                "technician",
                "assigned_by",
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

        technician_id = self.request.query_params.get(
            "technician"
        )

        if technician_id:
            queryset = queryset.filter(
                technician_id=technician_id,
            )

        assignment_status = (
            self.request.query_params.get(
                "status"
            )
        )

        if assignment_status:
            statuses = [
                value.strip()
                for value in assignment_status.split(",")
                if value.strip()
            ]

            if statuses:
                queryset = queryset.filter(
                    status__in=statuses,
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

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairAssignmentListSerializer

        if self.action == "create":
            return RepairAssignmentCreateSerializer

        if self.action in (
            "update",
            "partial_update",
        ):
            return RepairAssignmentUpdateSerializer

        return RepairAssignmentDetailSerializer

    def perform_create(self, serializer):
        actor = get_authenticated_actor(
            self.request
        )

        try:
            self.created_assignment = (
                create_repair_assignment(
                    repair=(
                        serializer.validated_data[
                            "repair"
                        ]
                    ),
                    technician=(
                        serializer.validated_data[
                            "technician"
                        ]
                    ),
                    actor=actor,
                    assignment_reason=(
                        serializer.validated_data.get(
                            "assignment_reason",
                            "",
                        )
                    ),
                )
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True
        )

        self.perform_create(
            serializer
        )

        response_serializer = (
            RepairAssignmentDetailSerializer(
                self.created_assignment,
                context={
                    "request": request,
                },
            )
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def perform_destroy(self, instance):
        actor = get_authenticated_actor(
            self.request
        )

        archive_repair_assignment(
            assignment=instance,
            actor=actor,
            reason="Archivado desde la API.",
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="accept",
    )
    def accept(self, request, pk=None):
        assignment = self.get_object()

        serializer = RepairAssignmentAcceptSerializer(
            data=request.data,
            context={
                "request": request,
                "assignment": assignment,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            assignment = accept_repair_assignment(
                assignment=assignment,
                actor=actor,
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
            RepairAssignmentDetailSerializer(
                assignment,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="start",
    )
    def start(self, request, pk=None):
        assignment = self.get_object()

        serializer = RepairAssignmentStartSerializer(
            data=request.data,
            context={
                "request": request,
                "assignment": assignment,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            assignment = start_repair_assignment(
                assignment=assignment,
                actor=actor,
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
            RepairAssignmentDetailSerializer(
                assignment,
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
        assignment = self.get_object()

        serializer = RepairAssignmentCompleteSerializer(
            data=request.data,
            context={
                "request": request,
                "assignment": assignment,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            assignment = complete_repair_assignment(
                assignment=assignment,
                actor=actor,
                completion_notes=(
                    serializer.validated_data.get(
                        "completion_notes",
                        "",
                    )
                ),
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairAssignmentDetailSerializer(
                assignment,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="reassign",
    )
    def reassign(self, request, pk=None):
        assignment = self.get_object()

        serializer = RepairAssignmentReassignSerializer(
            data=request.data,
            context={
                "request": request,
                "assignment": assignment,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            new_assignment = (
                reassign_repair_assignment(
                    assignment=assignment,
                    technician=(
                        serializer.validated_data[
                            "technician"
                        ]
                    ),
                    actor=actor,
                    reason=(
                        serializer.validated_data[
                            "reason"
                        ]
                    ),
                    assignment_reason=(
                        serializer.validated_data.get(
                            "assignment_reason",
                            "",
                        )
                    ),
                )
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairAssignmentDetailSerializer(
                new_assignment,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="reject",
    )
    def reject(self, request, pk=None):
        assignment = self.get_object()

        serializer = RepairAssignmentRejectSerializer(
            data=request.data,
            context={
                "request": request,
                "assignment": assignment,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            assignment = reject_repair_assignment(
                assignment=assignment,
                actor=actor,
                reason=(
                    serializer.validated_data[
                        "reason"
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
            RepairAssignmentDetailSerializer(
                assignment,
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
        assignment = self.get_object()

        serializer = RepairAssignmentCancelSerializer(
            data=request.data,
            context={
                "request": request,
                "assignment": assignment,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            assignment = cancel_repair_assignment(
                assignment=assignment,
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
            RepairAssignmentDetailSerializer(
                assignment,
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
        assignment = get_object_or_404(
            RepairAssignment.objects.all(),
            pk=pk,
        )

        serializer = (
            ArchiveRepairAssignmentSerializer(
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
            assignment = archive_repair_assignment(
                assignment=assignment,
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
            RepairAssignmentDetailSerializer(
                assignment,
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
        assignment = get_object_or_404(
            RepairAssignment.objects.all(),
            pk=pk,
        )

        actor = get_authenticated_actor(
            request
        )

        try:
            assignment = restore_repair_assignment(
                assignment=assignment,
                actor=actor,
            )
        except DjangoValidationError as exception:
            return django_validation_error_response(
                exception
            )

        return Response(
            RepairAssignmentDetailSerializer(
                assignment,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )