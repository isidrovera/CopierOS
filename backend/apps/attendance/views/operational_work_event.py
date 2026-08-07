# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.attendance.models import OperationalWorkEvent
from apps.attendance.serializers.operational_work_event import (
    OperationalWorkEventSerializer,
)


class OperationalWorkEventViewSet(ModelViewSet):
    serializer_class = OperationalWorkEventSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            OperationalWorkEvent.objects
            .select_related(
                "session",
                "session__employee_profile",
                "session__employee_profile__user",
                "work_location",
                "device",
                "reviewed_by",
                "corrected_event",
                "created_by",
                "archived_by",
            )
            .all()
        )

        params = self.request.query_params

        archived = params.get("archived")
        session = params.get("session")
        event_type = params.get("event_type")
        time_category = params.get("time_category")
        responsibility_type = params.get(
            "responsibility_type"
        )
        validation_status = params.get(
            "validation_status"
        )
        local_date = params.get("local_date")
        requires_review = params.get(
            "requires_review"
        )
        work_location = params.get(
            "work_location"
        )
        device = params.get("device")

        if archived == "true":
            queryset = queryset.filter(
                archived_at__isnull=False,
            )
        elif archived != "all":
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        if session:
            queryset = queryset.filter(
                session_id=session,
            )

        if event_type:
            queryset = queryset.filter(
                event_type=event_type,
            )

        if time_category:
            queryset = queryset.filter(
                time_category=time_category,
            )

        if responsibility_type:
            queryset = queryset.filter(
                responsibility_type=responsibility_type,
            )

        if validation_status:
            queryset = queryset.filter(
                validation_status=validation_status,
            )

        if local_date:
            queryset = queryset.filter(
                local_date=local_date,
            )

        if work_location:
            queryset = queryset.filter(
                work_location_id=work_location,
            )

        if device:
            queryset = queryset.filter(
                device_id=device,
            )

        if requires_review in ("true", "false"):
            queryset = queryset.filter(
                requires_review=(
                    requires_review == "true"
                ),
            )

        return queryset.order_by(
            "occurred_at",
            "created_at",
        )

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="observe",
    )
    def observe_event(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.mark_observed(
                reason=request.data.get(
                    "reason",
                    "",
                ),
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
        url_path="mark-valid",
    )
    def mark_valid(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.mark_valid(
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
    def reject_event(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.reject(
                reason=request.data.get(
                    "reason",
                    "",
                ),
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
        url_path="mark-corrected",
    )
    def mark_corrected(self, request, pk=None):
        instance = self.get_object()

        corrected_event_id = request.data.get(
            "corrected_event"
        )

        try:
            corrected_event = (
                OperationalWorkEvent.objects.get(
                    pk=corrected_event_id
                )
            )
        except OperationalWorkEvent.DoesNotExist:
            return Response(
                {
                    "corrected_event": (
                        "Evento corregido no encontrado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            instance.mark_corrected(
                corrected_event=corrected_event,
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
                    "Evento archivado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore_event(self, request, pk=None):
        try:
            instance = OperationalWorkEvent.objects.get(
                pk=pk
            )
        except OperationalWorkEvent.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Evento no encontrado."
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

    @action(
        detail=False,
        methods=("get",),
        url_path="review-required",
    )
    def review_required(self, request):
        queryset = self.get_queryset().filter(
            requires_review=True,
        )

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