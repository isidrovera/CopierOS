# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.attendance.models import AttendanceCorrection
from apps.attendance.serializers.attendance_correction import (
    AttendanceCorrectionSerializer,
)


class AttendanceCorrectionViewSet(ModelViewSet):
    serializer_class = AttendanceCorrectionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            AttendanceCorrection.objects
            .select_related(
                "employee_profile",
                "employee_profile__user",
                "attendance_record",
                "daily_attendance",
                "generated_record",
                "requested_by",
                "supervisor_reviewed_by",
                "human_resources_reviewed_by",
                "management_reviewed_by",
                "approved_by",
                "rejected_by",
                "applied_by",
                "cancelled_by",
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
        correction_type = params.get("correction_type")
        target_type = params.get("target_type")
        status_value = params.get("status")
        correction_date = params.get("correction_date")

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

        if correction_type:
            queryset = queryset.filter(
                correction_type=correction_type,
            )

        if target_type:
            queryset = queryset.filter(
                target_type=target_type,
            )

        if status_value:
            queryset = queryset.filter(
                status=status_value,
            )

        if correction_date:
            queryset = queryset.filter(
                correction_date=correction_date,
            )

        return queryset.order_by(
            "-correction_date",
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
        url_path="submit",
    )
    def submit_correction(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.submit(
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
        url_path="supervisor-approve",
    )
    def supervisor_approve(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.supervisor_approve(
                user=request.user,
                observation=request.data.get(
                    "observation",
                    "",
                ),
                approved_values=request.data.get(
                    "approved_values"
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
        url_path="hr-approve",
    )
    def human_resources_approve(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.human_resources_approve(
                user=request.user,
                observation=request.data.get(
                    "observation",
                    "",
                ),
                approved_values=request.data.get(
                    "approved_values"
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
        url_path="management-approve",
    )
    def management_approve(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.management_approve(
                user=request.user,
                observation=request.data.get(
                    "observation",
                    "",
                ),
                approved_values=request.data.get(
                    "approved_values"
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
        url_path="reject",
    )
    def reject_correction(self, request, pk=None):
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
        url_path="mark-applied",
    )
    def mark_applied(self, request, pk=None):
        instance = self.get_object()

        generated_record = None
        generated_record_id = request.data.get(
            "generated_record"
        )

        if generated_record_id:
            try:
                generated_record = (
                    instance._meta.get_field(
                        "generated_record"
                    ).remote_field.model.objects.get(
                        pk=generated_record_id
                    )
                )
            except Exception:
                return Response(
                    {
                        "generated_record": (
                            "Marcación generada no encontrada."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            instance.mark_applied(
                user=request.user,
                result=request.data.get(
                    "result",
                    {},
                ),
                generated_record=generated_record,
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="application-error",
    )
    def application_error(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.mark_application_error(
                error=request.data.get(
                    "error",
                    "",
                ),
                user=request.user,
                result=request.data.get(
                    "result",
                    {},
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
        url_path="retry-application",
    )
    def retry_application(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.retry_application(
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
        url_path="cancel",
    )
    def cancel_correction(self, request, pk=None):
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
        url_path="close",
    )
    def close_correction(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.close(
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
                    "Corrección archivada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore_correction(self, request, pk=None):
        try:
            instance = AttendanceCorrection.objects.get(
                pk=pk
            )
        except AttendanceCorrection.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Corrección no encontrada."
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