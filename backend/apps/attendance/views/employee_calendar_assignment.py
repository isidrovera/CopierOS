# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.attendance.models import EmployeeCalendarAssignment
from apps.attendance.serializers.employee_calendar_assignment import (
    EmployeeCalendarAssignmentSerializer,
)


class EmployeeCalendarAssignmentViewSet(ModelViewSet):
    serializer_class = EmployeeCalendarAssignmentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            EmployeeCalendarAssignment.objects
            .select_related(
                "employee_profile",
                "employee_profile__user",
                "calendar",
                "activated_by",
                "finished_by",
                "cancelled_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .all()
        )

        params = self.request.query_params

        archived = params.get("archived")
        employee_profile = params.get("employee_profile")
        calendar = params.get("calendar")
        assignment_type = params.get("assignment_type")
        status_value = params.get("status")
        override_default = params.get("override_default_calendar")
        search = str(params.get("search", "") or "").strip()

        if archived == "true":
            queryset = queryset.filter(
                archived_at__isnull=False,
            )
        elif archived != "all":
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        if employee_profile:
            queryset = queryset.filter(
                employee_profile_id=employee_profile,
            )

        if calendar:
            queryset = queryset.filter(
                calendar_id=calendar,
            )

        if assignment_type:
            queryset = queryset.filter(
                assignment_type=assignment_type,
            )

        if status_value:
            queryset = queryset.filter(
                status=status_value,
            )

        if override_default in ("true", "false"):
            queryset = queryset.filter(
                override_default_calendar=(
                    override_default == "true"
                ),
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
                    calendar__code__icontains=search
                )
                | Q(
                    calendar__name__icontains=search
                )
            )

        return queryset.order_by(
            "priority",
            "-effective_from",
            "-created_at",
        )

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="activate",
    )
    def activate_assignment(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.activate(user=request.user)
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="finish",
    )
    def finish_assignment(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.finish(user=request.user)
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="cancel",
    )
    def cancel_assignment(self, request, pk=None):
        instance = self.get_object()

        reason = str(
            request.data.get("reason", "") or ""
        ).strip()

        try:
            instance.cancel(
                user=request.user,
                reason=reason,
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            instance.archive(
                user=request.user,
                reason=str(
                    request.data.get(
                        "reason",
                        "Archivado desde la API.",
                    )
                    or ""
                ).strip(),
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            {
                "detail": (
                    "Asignación archivada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore_assignment(self, request, pk=None):
        try:
            instance = (
                EmployeeCalendarAssignment.objects
                .select_related(
                    "employee_profile",
                    "calendar",
                )
                .get(pk=pk)
            )
        except EmployeeCalendarAssignment.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Asignación no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.restore(user=request.user)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=False,
        methods=("get",),
        url_path="current",
    )
    def current_assignments(self, request):
        today = timezone.localdate()

        queryset = (
            self.get_queryset()
            .filter(
                status=EmployeeCalendarAssignment.Status.ACTIVE,
                effective_from__lte=today,
            )
            .filter(
                Q(effective_until__isnull=True)
                | Q(effective_until__gte=today)
            )
        )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    def _error(self, exc):
        if hasattr(exc, "message_dict"):
            data = exc.message_dict
        else:
            data = {
                "detail": getattr(
                    exc,
                    "messages",
                    [str(exc)],
                )
            }

        return Response(
            data,
            status=status.HTTP_400_BAD_REQUEST,
        )