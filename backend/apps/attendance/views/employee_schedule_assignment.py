# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.attendance.models import (
    EmployeeScheduleAssignment,
)

from apps.attendance.serializers.employee_schedule_assignment import (
    EmployeeScheduleAssignmentSerializer,
)


class EmployeeScheduleAssignmentViewSet(
    ModelViewSet
):
    """
    API de asignaciones de horarios.

    Incluye:

    - CRUD.
    - Activar.
    - Finalizar.
    - Cancelar.
    - Archivar.
    - Restaurar.
    - Consultar asignaciones vigentes.
    """

    serializer_class = (
        EmployeeScheduleAssignmentSerializer
    )

    permission_classes = (
        IsAuthenticated,
    )

    http_method_names = (
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
    )

    def get_queryset(self):
        queryset = (
            EmployeeScheduleAssignment.objects
            .select_related(
                "employee_profile",
                "employee_profile__user",
                "schedule",
                "primary_location",
                "activated_by",
                "cancelled_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .prefetch_related(
                "allowed_locations",
            )
            .all()
        )

        params = self.request.query_params

        archived = params.get(
            "archived"
        )

        employee_profile = params.get(
            "employee_profile"
        )

        schedule = params.get(
            "schedule"
        )

        assignment_type = params.get(
            "assignment_type"
        )

        status_value = params.get(
            "status"
        )

        primary_location = params.get(
            "primary_location"
        )

        attendance_required = params.get(
            "attendance_required"
        )

        operational_time_required = params.get(
            "operational_time_required"
        )

        location_required = params.get(
            "location_required"
        )

        search = str(
            params.get(
                "search",
                "",
            )
            or ""
        ).strip()

        if archived == "true":
            queryset = queryset.filter(
                archived_at__isnull=False,
            )

        elif archived == "all":
            pass

        else:
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        if employee_profile:
            queryset = queryset.filter(
                employee_profile_id=employee_profile,
            )

        if schedule:
            queryset = queryset.filter(
                schedule_id=schedule,
            )

        if assignment_type:
            queryset = queryset.filter(
                assignment_type=assignment_type,
            )

        if status_value:
            queryset = queryset.filter(
                status=status_value,
            )

        if primary_location:
            queryset = queryset.filter(
                primary_location_id=primary_location,
            )

        if attendance_required in (
            "true",
            "false",
        ):
            queryset = queryset.filter(
                attendance_required=(
                    attendance_required == "true"
                )
            )

        if operational_time_required in (
            "true",
            "false",
        ):
            queryset = queryset.filter(
                operational_time_required=(
                    operational_time_required
                    == "true"
                )
            )

        if location_required in (
            "true",
            "false",
        ):
            queryset = queryset.filter(
                location_required=(
                    location_required == "true"
                )
            )

        if search:
            queryset = queryset.filter(
                Q(
                    employee_profile__employee_code__icontains=search
                )
                | Q(
                    employee_profile__user__first_name__icontains=search
                )
                | Q(
                    employee_profile__user__paternal_last_name__icontains=search
                )
                | Q(
                    employee_profile__user__maternal_last_name__icontains=search
                )
                | Q(
                    schedule__code__icontains=search
                )
                | Q(
                    schedule__name__icontains=search
                )
                | Q(
                    notes__icontains=search
                )
            )

        return queryset.order_by(
            "-effective_from",
            "-created_at",
        )

    def perform_create(
        self,
        serializer,
    ):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(
        self,
        serializer,
    ):
        serializer.save(
            updated_by=self.request.user,
        )

    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):
        instance = self.get_object()

        reason = str(
            request.data.get(
                "reason",
                "Archivado desde la API.",
            )
            or ""
        ).strip()

        try:
            instance.archive(
                user=request.user,
                reason=reason,
            )

        except DjangoValidationError as exc:
            return self._validation_error_response(
                exc
            )

        return Response(
            {
                "detail": (
                    "Asignación archivada "
                    "correctamente."
                ),
                "id": str(instance.id),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="activate",
    )
    def activate_assignment(
        self,
        request,
        pk=None,
    ):
        instance = self.get_object()

        try:
            instance.activate(
                user=request.user,
            )

        except DjangoValidationError as exc:
            return self._validation_error_response(
                exc
            )

        serializer = self.get_serializer(
            instance
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="finish",
    )
    def finish_assignment(
        self,
        request,
        pk=None,
    ):
        instance = self.get_object()

        try:
            instance.finish(
                user=request.user,
            )

        except DjangoValidationError as exc:
            return self._validation_error_response(
                exc
            )

        serializer = self.get_serializer(
            instance
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="cancel",
    )
    def cancel_assignment(
        self,
        request,
        pk=None,
    ):
        instance = self.get_object()

        reason = str(
            request.data.get(
                "reason",
                "",
            )
            or ""
        ).strip()

        if not reason:
            return Response(
                {
                    "reason": (
                        "Debes indicar el motivo "
                        "de cancelación."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            instance.cancel(
                user=request.user,
                reason=reason,
            )

        except DjangoValidationError as exc:
            return self._validation_error_response(
                exc
            )

        serializer = self.get_serializer(
            instance
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="archive",
    )
    def archive_assignment(
        self,
        request,
        pk=None,
    ):
        instance = self.get_object()

        if instance.archived_at:
            return Response(
                {
                    "detail": (
                        "La asignación ya está archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = str(
            request.data.get(
                "reason",
                "",
            )
            or ""
        ).strip()

        if not reason:
            return Response(
                {
                    "reason": (
                        "Debes indicar el motivo "
                        "de archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            instance.archive(
                user=request.user,
                reason=reason,
            )

        except DjangoValidationError as exc:
            return self._validation_error_response(
                exc
            )

        serializer = self.get_serializer(
            instance
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore_assignment(
        self,
        request,
        pk=None,
    ):
        try:
            instance = (
                EmployeeScheduleAssignment.objects
                .select_related(
                    "employee_profile",
                    "employee_profile__user",
                    "schedule",
                    "primary_location",
                )
                .prefetch_related(
                    "allowed_locations",
                )
                .get(
                    pk=pk
                )
            )

        except EmployeeScheduleAssignment.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Asignación no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not instance.archived_at:
            return Response(
                {
                    "detail": (
                        "La asignación no está archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            instance.restore(
                user=request.user,
            )

        except DjangoValidationError as exc:
            return self._validation_error_response(
                exc
            )

        serializer = self.get_serializer(
            instance
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=("get",),
        url_path="current",
    )
    def current_assignments(
        self,
        request,
    ):
        today = timezone.localdate()

        queryset = (
            self.get_queryset()
            .filter(
                archived_at__isnull=True,
                status=(
                    EmployeeScheduleAssignment
                    .AssignmentStatus.ACTIVE
                ),
                effective_from__lte=today,
            )
            .filter(
                Q(
                    effective_until__isnull=True
                )
                | Q(
                    effective_until__gte=today
                )
            )
        )

        return self._paginated_response(
            queryset
        )

    @action(
        detail=False,
        methods=("get",),
        url_path="scheduled",
    )
    def scheduled_assignments(
        self,
        request,
    ):
        queryset = (
            self.get_queryset()
            .filter(
                status=(
                    EmployeeScheduleAssignment
                    .AssignmentStatus.SCHEDULED
                ),
            )
        )

        return self._paginated_response(
            queryset
        )

    @action(
        detail=False,
        methods=("get",),
        url_path="archived",
    )
    def archived_assignments(
        self,
        request,
    ):
        queryset = (
            EmployeeScheduleAssignment.objects
            .select_related(
                "employee_profile",
                "employee_profile__user",
                "schedule",
                "primary_location",
            )
            .prefetch_related(
                "allowed_locations",
            )
            .filter(
                archived_at__isnull=False,
            )
            .order_by(
                "-archived_at",
            )
        )

        return self._paginated_response(
            queryset
        )

    def _paginated_response(
        self,
        queryset,
    ):
        page = self.paginate_queryset(
            queryset
        )

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )

            return self.get_paginated_response(
                serializer.data
            )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data
        )

    def _validation_error_response(
        self,
        exc,
    ):
        if hasattr(
            exc,
            "message_dict",
        ):
            data = exc.message_dict

        elif hasattr(
            exc,
            "messages",
        ):
            data = {
                "detail": exc.messages
            }

        else:
            data = {
                "detail": str(exc)
            }

        return Response(
            data,
            status=status.HTTP_400_BAD_REQUEST,
        )