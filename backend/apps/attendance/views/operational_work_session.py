# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.attendance.models import OperationalWorkSession
from apps.attendance.serializers.operational_work_session import (
    OperationalWorkSessionSerializer,
)


class OperationalWorkSessionViewSet(ModelViewSet):
    serializer_class = OperationalWorkSessionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            OperationalWorkSession.objects
            .select_related(
                "employee_profile",
                "employee_profile__user",
                "daily_attendance",
                "target_content_type",
                "work_location",
                "device",
                "assigned_by",
                "cancelled_by",
                "reviewed_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .all()
        )

        params = self.request.query_params

        archived = params.get("archived")
        employee_profile = params.get("employee_profile")
        daily_attendance = params.get("daily_attendance")
        session_type = params.get("session_type")
        status_value = params.get("status")
        current_stage = params.get("current_stage")
        priority = params.get("priority")
        requires_review = params.get("requires_review")
        work_location = params.get("work_location")

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

        if daily_attendance:
            queryset = queryset.filter(
                daily_attendance_id=daily_attendance,
            )

        if session_type:
            queryset = queryset.filter(
                session_type=session_type,
            )

        if status_value:
            queryset = queryset.filter(
                status=status_value,
            )

        if current_stage:
            queryset = queryset.filter(
                current_stage=current_stage,
            )

        if priority:
            queryset = queryset.filter(
                priority=priority,
            )

        if work_location:
            queryset = queryset.filter(
                work_location_id=work_location,
            )

        if requires_review in ("true", "false"):
            queryset = queryset.filter(
                requires_review=(
                    requires_review == "true"
                ),
            )

        return queryset.order_by(
            "-assigned_at",
            "-created_at",
        )

    def perform_create(self, serializer):
        serializer.save(
            assigned_by=self.request.user,
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
        url_path="accept",
    )
    def accept_session(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.accept(
                user=request.user,
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="reject",
    )
    def reject_session(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.reject(
                user=request.user,
                reason=request.data.get(
                    "reason",
                    "",
                ),
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="start",
    )
    def start_session(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.start(
                user=request.user,
                stage=request.data.get(
                    "stage"
                ),
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="pause",
    )
    def pause_session(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.pause(
                user=request.user,
                stage=request.data.get(
                    "stage"
                ),
                reason=request.data.get(
                    "reason",
                    "",
                ),
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="waiting",
    )
    def start_waiting(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.start_waiting(
                stage=request.data.get(
                    "stage"
                ),
                user=request.user,
                reason=request.data.get(
                    "reason",
                    "",
                ),
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="complete",
    )
    def complete_session(self, request, pk=None):
        instance = self.get_object()

        try:
            completion_percentage = request.data.get(
                "completion_percentage",
                100,
            )

            instance.complete(
                user=request.user,
                result=request.data.get(
                    "result",
                    OperationalWorkSession
                    .CompletionResult.SUCCESS,
                ),
                completion_percentage=completion_percentage,
                observation=request.data.get(
                    "observation",
                    "",
                ),
            )
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
    def cancel_session(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.cancel(
                user=request.user,
                reason=request.data.get(
                    "reason",
                    "",
                ),
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="review",
    )
    def review_session(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.mark_reviewed(
                user=request.user,
                observation=request.data.get(
                    "observation",
                    "",
                ),
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="recalculate-times",
    )
    def recalculate_times(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.recalculate_times()
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
                reason=request.data.get(
                    "reason",
                    "",
                ),
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            {
                "detail": (
                    "Sesión archivada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore_session(self, request, pk=None):
        try:
            instance = OperationalWorkSession.objects.get(
                pk=pk
            )
        except OperationalWorkSession.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Sesión no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            instance.restore(
                user=request.user,
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

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