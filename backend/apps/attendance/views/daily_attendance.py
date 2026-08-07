# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.attendance.models import DailyAttendance
from apps.attendance.serializers.daily_attendance import (
    DailyAttendanceSerializer,
)


class DailyAttendanceViewSet(ModelViewSet):
    serializer_class = DailyAttendanceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            DailyAttendance.objects
            .select_related(
                "employee_profile",
                "employee_profile__user",
                "schedule_assignment",
                "schedule_day",
                "calendar_assignment",
                "holiday_day",
                "primary_location",
                "reviewed_by",
                "approved_by",
                "closed_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .all()
        )

        params = self.request.query_params

        archived = params.get("archived")
        employee_profile = params.get("employee_profile")
        attendance_status = params.get("attendance_status")
        processing_status = params.get("processing_status")
        date = params.get("date")
        requires_review = params.get("requires_review")

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

        if attendance_status:
            queryset = queryset.filter(
                attendance_status=attendance_status,
            )

        if processing_status:
            queryset = queryset.filter(
                processing_status=processing_status,
            )

        if date:
            queryset = queryset.filter(
                date=date,
            )

        if requires_review in ("true", "false"):
            queryset = queryset.filter(
                requires_review=(
                    requires_review == "true"
                ),
            )

        return queryset.order_by(
            "-date",
            "employee_profile",
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
        url_path="recalculate",
    )
    def recalculate(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.recalculate()
        except (DjangoValidationError, Exception) as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="review",
    )
    def review(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.mark_reviewed(
                user=request.user,
                observation=str(
                    request.data.get(
                        "observation",
                        "",
                    )
                    or ""
                ).strip(),
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="approve",
    )
    def approve(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.approve(
                user=request.user,
                observation=str(
                    request.data.get(
                        "observation",
                        "",
                    )
                    or ""
                ).strip(),
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="close",
    )
    def close(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.close(
                user=request.user,
                observation=str(
                    request.data.get(
                        "observation",
                        "",
                    )
                    or ""
                ).strip(),
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="reopen",
    )
    def reopen(self, request, pk=None):
        instance = self.get_object()

        reason = str(
            request.data.get("reason", "") or ""
        ).strip()

        try:
            instance.reopen(
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

        reason = str(
            request.data.get("reason", "") or ""
        ).strip()

        try:
            instance.archive(
                user=request.user,
                reason=reason,
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            {
                "detail": (
                    "Asistencia diaria archivada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore(self, request, pk=None):
        try:
            instance = DailyAttendance.objects.get(
                pk=pk
            )
        except DailyAttendance.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Asistencia diaria no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.restore(
            user=request.user,
        )

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=False,
        methods=("get",),
        url_path="review-required",
    )
    def review_required(self, request):
        queryset = self.get_queryset().filter(
            requires_review=True,
        )

        return self._serialize_queryset(
            queryset
        )

    def _serialize_queryset(
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