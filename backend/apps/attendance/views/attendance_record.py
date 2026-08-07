# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.attendance.models import AttendanceRecord
from apps.attendance.serializers.attendance_record import (
    AttendanceRecordSerializer,
)


class AttendanceRecordViewSet(ModelViewSet):
    serializer_class = AttendanceRecordSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            AttendanceRecord.objects
            .select_related(
                "employee_profile",
                "employee_profile__user",
                "device",
                "device_permission",
                "work_location",
                "reviewed_by",
                "corrected_record",
                "registered_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .all()
        )

        params = self.request.query_params

        archived = params.get("archived")
        employee_profile = params.get("employee_profile")
        record_type = params.get("record_type")
        source_type = params.get("source_type")
        validation_status = params.get("validation_status")
        location_status = params.get("location_status")
        sync_status = params.get("sync_status")
        device = params.get("device")
        work_location = params.get("work_location")
        local_date = params.get("local_date")
        requires_review = params.get("requires_review")
        is_manual = params.get("is_manual")
        search = str(
            params.get("search", "") or ""
        ).strip()

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

        if record_type:
            queryset = queryset.filter(
                record_type=record_type,
            )

        if source_type:
            queryset = queryset.filter(
                source_type=source_type,
            )

        if validation_status:
            queryset = queryset.filter(
                validation_status=validation_status,
            )

        if location_status:
            queryset = queryset.filter(
                location_status=location_status,
            )

        if sync_status:
            queryset = queryset.filter(
                sync_status=sync_status,
            )

        if device:
            queryset = queryset.filter(
                device_id=device,
            )

        if work_location:
            queryset = queryset.filter(
                work_location_id=work_location,
            )

        if local_date:
            queryset = queryset.filter(
                local_date=local_date,
            )

        if requires_review in ("true", "false"):
            queryset = queryset.filter(
                requires_review=(
                    requires_review == "true"
                ),
            )

        if is_manual in ("true", "false"):
            queryset = queryset.filter(
                is_manual=(is_manual == "true"),
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
                    observation__icontains=search
                )
                | Q(
                    employee_note__icontains=search
                )
                | Q(
                    external_reference__icontains=search
                )
            )

        return queryset.order_by(
            "-occurred_at",
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
        url_path="mark-valid",
    )
    def mark_valid(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.mark_valid(
                user=request.user,
                message=str(
                    request.data.get("message", "") or ""
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
        url_path="observe",
    )
    def observe_record(self, request, pk=None):
        instance = self.get_object()

        reason = str(
            request.data.get("reason", "") or ""
        ).strip()

        try:
            instance.mark_observed(
                reason=reason,
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
    def reject_record(self, request, pk=None):
        instance = self.get_object()

        reason = str(
            request.data.get("reason", "") or ""
        ).strip()

        try:
            instance.reject(
                reason=reason,
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
        url_path="location-valid",
    )
    def location_valid(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.mark_location_valid(
                distance_meters=request.data.get(
                    "distance_meters"
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
        url_path="location-invalid",
    )
    def location_invalid(self, request, pk=None):
        instance = self.get_object()

        location_status = request.data.get(
            "status"
        )

        reason = str(
            request.data.get("reason", "") or ""
        ).strip()

        distance = request.data.get(
            "distance_meters"
        )

        try:
            instance.mark_location_invalid(
                status=location_status,
                reason=reason,
                distance_meters=distance,
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
                    "Marcación archivada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore_record(self, request, pk=None):
        try:
            instance = AttendanceRecord.objects.get(
                pk=pk
            )
        except AttendanceRecord.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Marcación no encontrada."
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