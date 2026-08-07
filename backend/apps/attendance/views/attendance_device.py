# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.attendance.models import AttendanceDevice
from apps.attendance.serializers.attendance_device import (
    AttendanceDeviceSerializer,
)


class AttendanceDeviceViewSet(ModelViewSet):
    serializer_class = AttendanceDeviceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            AttendanceDevice.objects
            .select_related(
                "work_location",
                "assigned_user",
                "approved_by",
                "rejected_by",
                "blocked_by",
                "revoked_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .all()
        )

        params = self.request.query_params

        archived = params.get("archived")
        device_type = params.get("device_type")
        ownership_type = params.get("ownership_type")
        registration_status = params.get(
            "registration_status"
        )
        work_location = params.get("work_location")
        assigned_user = params.get("assigned_user")
        is_active = params.get("is_active")
        search = str(params.get("search", "") or "").strip()

        if archived == "true":
            queryset = queryset.filter(
                archived_at__isnull=False,
            )
        elif archived != "all":
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        if device_type:
            queryset = queryset.filter(
                device_type=device_type,
            )

        if ownership_type:
            queryset = queryset.filter(
                ownership_type=ownership_type,
            )

        if registration_status:
            queryset = queryset.filter(
                registration_status=registration_status,
            )

        if work_location:
            queryset = queryset.filter(
                work_location_id=work_location,
            )

        if assigned_user:
            queryset = queryset.filter(
                assigned_user_id=assigned_user,
            )

        if is_active in ("true", "false"):
            queryset = queryset.filter(
                is_active=(is_active == "true"),
            )

        if search:
            queryset = queryset.filter(
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(hardware_serial__icontains=search)
                | Q(manufacturer__icontains=search)
                | Q(model_name__icontains=search)
                | Q(mac_address__icontains=search)
            )

        return queryset.order_by(
            "name",
            "code",
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
        url_path="approve",
    )
    def approve_device(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.approve(
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
    def reject_device(self, request, pk=None):
        instance = self.get_object()

        reason = str(
            request.data.get("reason", "") or ""
        ).strip()

        try:
            instance.reject(
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
        url_path="block",
    )
    def block_device(self, request, pk=None):
        instance = self.get_object()

        reason = str(
            request.data.get("reason", "") or ""
        ).strip()

        try:
            instance.block(
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
        url_path="unblock",
    )
    def unblock_device(self, request, pk=None):
        instance = self.get_object()

        try:
            instance.unblock(
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
    def revoke_device(self, request, pk=None):
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
                    "Dispositivo archivado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore_device(self, request, pk=None):
        try:
            instance = AttendanceDevice.objects.get(
                pk=pk
            )
        except AttendanceDevice.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Dispositivo no encontrado."
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
        url_path="approved",
    )
    def approved_devices(self, request):
        queryset = self.get_queryset().filter(
            registration_status=(
                AttendanceDevice
                .RegistrationStatus.APPROVED
            ),
        )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    @action(
        detail=False,
        methods=("get",),
        url_path="clocking-enabled",
    )
    def clocking_enabled_devices(self, request):
        queryset = self.get_queryset().filter(
            registration_status=(
                AttendanceDevice
                .RegistrationStatus.APPROVED
            ),
            is_active=True,
            allows_attendance_clocking=True,
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