# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.attendance.models import AttendanceIncident
from apps.attendance.serializers.attendance_incident import (
    AttendanceIncidentSerializer,
)


class AttendanceIncidentViewSet(ModelViewSet):
    serializer_class = AttendanceIncidentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            AttendanceIncident.objects
            .select_related(
                "employee_profile",
                "employee_profile__user",
                "daily_attendance",
                "attendance_record",
                "justification_requested_by",
                "justification_reviewed_by",
                "resolved_by",
                "closed_by",
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
        incident_type = params.get("incident_type")
        severity = params.get("severity")
        status_value = params.get("status")
        incident_date = params.get("incident_date")
        affects_payroll = params.get("affects_payroll")
        affects_evaluation = params.get("affects_evaluation")

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

        if incident_type:
            queryset = queryset.filter(
                incident_type=incident_type,
            )

        if severity:
            queryset = queryset.filter(
                severity=severity,
            )

        if status_value:
            queryset = queryset.filter(
                status=status_value,
            )

        if incident_date:
            queryset = queryset.filter(
                incident_date=incident_date,
            )

        if affects_payroll in ("true", "false"):
            queryset = queryset.filter(
                affects_payroll=(
                    affects_payroll == "true"
                ),
            )

        if affects_evaluation in ("true", "false"):
            queryset = queryset.filter(
                affects_evaluation=(
                    affects_evaluation == "true"
                ),
            )

        return queryset.order_by(
            "-incident_date",
            "-detected_at",
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
        url_path="request-explanation",
    )
    def request_explanation(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.request_employee_explanation(
                user=request.user,
                due_at=request.data.get("due_at"),
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="submit-explanation",
    )
    def submit_explanation(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.submit_employee_explanation(
                explanation=request.data.get(
                    "explanation",
                    "",
                ),
                accepts_incident=request.data.get(
                    "accepts_incident"
                ),
                ip_address=request.META.get(
                    "REMOTE_ADDR"
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
        url_path="start-review",
    )
    def start_review(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.start_review(
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
        url_path="accept-justification",
    )
    def accept_justification(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.accept_justification(
                user=request.user,
                notes=request.data.get(
                    "notes",
                    "",
                ),
                justified_minutes=request.data.get(
                    "justified_minutes"
                ),
                responsibility_type=request.data.get(
                    "responsibility_type"
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
        url_path="reject-justification",
    )
    def reject_justification(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.reject_justification(
                user=request.user,
                notes=request.data.get(
                    "notes",
                    "",
                ),
                deductible_minutes=request.data.get(
                    "deductible_minutes"
                ),
                penalty_points=request.data.get(
                    "penalty_points",
                    0,
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
        url_path="mark-corrected",
    )
    def mark_corrected(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.mark_corrected(
                user=request.user,
                resolution_type=request.data.get(
                    "resolution_type"
                ),
                notes=request.data.get(
                    "notes",
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
        url_path="dismiss",
    )
    def dismiss_incident(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.dismiss(
                user=request.user,
                notes=request.data.get(
                    "notes",
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
    def close_incident(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.close(
                user=request.user,
                notes=request.data.get(
                    "notes",
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
        url_path="reopen",
    )
    def reopen_incident(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.reopen(
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
    def cancel_incident(self, request, pk=None):
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
                    "Incidencia archivada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore_incident(self, request, pk=None):
        try:
            instance = AttendanceIncident.objects.get(
                pk=pk
            )
        except AttendanceIncident.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Incidencia no encontrada."
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
        url_path="open",
    )
    def open_incidents(self, request):
        queryset = self.get_queryset().filter(
            status__in=(
                AttendanceIncident.Status.OPEN,
                AttendanceIncident.Status.PENDING_EMPLOYEE,
                AttendanceIncident.Status.PENDING_SUPERVISOR,
                AttendanceIncident.Status.UNDER_REVIEW,
            )
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