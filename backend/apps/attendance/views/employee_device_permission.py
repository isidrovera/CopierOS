# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.attendance.models import EmployeeDevicePermission
from apps.attendance.serializers.employee_device_permission import (
    EmployeeDevicePermissionSerializer,
)


class EmployeeDevicePermissionViewSet(ModelViewSet):
    serializer_class = EmployeeDevicePermissionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            EmployeeDevicePermission.objects
            .select_related(
                "employee_profile",
                "employee_profile__user",
                "device",
                "activated_by",
                "suspended_by",
                "revoked_by",
                "finished_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .all()
        )

        params = self.request.query_params

        archived = params.get("archived")
        employee_profile = params.get("employee_profile")
        device = params.get("device")
        status_value = params.get("status")
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

        if device:
            queryset = queryset.filter(
                device_id=device,
            )

        if status_value:
            queryset = queryset.filter(
                status=status_value,
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
                    device__code__icontains=search
                )
                | Q(
                    device__name__icontains=search
                )
            )

        return queryset.order_by(
            "employee_profile",
            "device",
            "-effective_from",
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
    def activate_permission(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.activate(
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
        url_path="suspend",
    )
    def suspend_permission(self, request, pk=None):
        instance = self.get_object()

        reason = str(
            request.data.get("reason", "") or ""
        ).strip()

        try:
            instance.suspend(
                user=request.user,
                reason=reason,
            )
        except DjangoValidationError as exc:
            return self._error(exc)

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="resume",
    )
    def resume_permission(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.resume(
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
        url_path="finish",
    )
    def finish_permission(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.finish(
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
        url_path="revoke",
    )
    def revoke_permission(self, request, pk=None):
        instance = self.get_object()

        reason = str(
            request.data.get("reason", "") or ""
        ).strip()

        try:
            instance.revoke(
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
                    "Permiso archivado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore_permission(self, request, pk=None):
        try:
            instance = (
                EmployeeDevicePermission.objects
                .select_related(
                    "employee_profile",
                    "employee_profile__user",
                    "device",
                )
                .get(pk=pk)
            )
        except EmployeeDevicePermission.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Permiso no encontrado."
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
        url_path="current",
    )
    def current_permissions(self, request):
        today = timezone.localdate()

        queryset = (
            self.get_queryset()
            .filter(
                status=(
                    EmployeeDevicePermission
                    .PermissionStatus.ACTIVE
                ),
                effective_from__lte=today,
            )
            .filter(
                Q(effective_until__isnull=True)
                | Q(effective_until__gte=today)
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