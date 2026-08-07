# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.attendance.models import LeaveRequest
from apps.attendance.serializers.leave_request import (
    LeaveRequestSerializer,
)


class LeaveRequestViewSet(ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            LeaveRequest.objects
            .select_related(
                "employee_profile",
                "employee_profile__user",
                "destination_location",
                "requested_by",
                "supervisor_reviewed_by",
                "human_resources_reviewed_by",
                "management_reviewed_by",
                "approved_by",
                "rejected_by",
                "cancelled_by",
                "completed_by",
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
        leave_type = params.get("leave_type")
        duration_type = params.get("duration_type")
        status_value = params.get("status")
        payment_type = params.get("payment_type")
        approval_level = params.get(
            "required_approval_level"
        )
        start_date = params.get("start_date")
        end_date = params.get("end_date")

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

        if leave_type:
            queryset = queryset.filter(
                leave_type=leave_type,
            )

        if duration_type:
            queryset = queryset.filter(
                duration_type=duration_type,
            )

        if status_value:
            queryset = queryset.filter(
                status=status_value,
            )

        if payment_type:
            queryset = queryset.filter(
                payment_type=payment_type,
            )

        if approval_level:
            queryset = queryset.filter(
                required_approval_level=approval_level,
            )

        if start_date:
            queryset = queryset.filter(
                end_date__gte=start_date,
            )

        if end_date:
            queryset = queryset.filter(
                start_date__lte=end_date,
            )

        return queryset.order_by(
            "-start_date",
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
    def submit_request(self, request, pk=None):
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
    def reject_request(self, request, pk=None):
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
        url_path="cancel",
    )
    def cancel_request(self, request, pk=None):
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
        url_path="start",
    )
    def start_request(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.start(
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
        url_path="complete",
    )
    def complete_request(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.complete(
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
        url_path="register-compensation",
    )
    def register_compensation(self, request, pk=None):
        instance = self.get_object()

        try:
            minutes = int(
                request.data.get(
                    "minutes",
                    0,
                )
            )

            instance.register_compensation(
                minutes=minutes,
                user=request.user,
            )
        except (ValueError, TypeError):
            return Response(
                {
                    "minutes": (
                        "Debes indicar una cantidad válida."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
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
    def close_request(self, request, pk=None):
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
                    "Solicitud archivada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore_request(self, request, pk=None):
        try:
            instance = LeaveRequest.objects.get(
                pk=pk
            )
        except LeaveRequest.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Solicitud no encontrada."
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