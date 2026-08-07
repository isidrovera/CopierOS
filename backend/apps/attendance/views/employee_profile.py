# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.attendance.models import EmployeeProfile
from apps.attendance.serializers.employee_profile import (
    EmployeeProfileSerializer,
)


class EmployeeProfileViewSet(ModelViewSet):
    """
    API de perfiles laborales.

    Permite:

    - Listar perfiles.
    - Consultar un perfil.
    - Crear perfiles.
    - Actualizar perfiles.
    - Archivar.
    - Restaurar.
    - Consultar únicamente perfiles vigentes.
    - Consultar perfiles archivados.
    """

    serializer_class = EmployeeProfileSerializer
    permission_classes = (
        IsAuthenticated,
    )

    http_method_names = (
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
    )

    def get_queryset(self):
        queryset = (
            EmployeeProfile.objects
            .select_related(
                "user",
                "manager",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .all()
        )

        params = self.request.query_params

        archived = params.get(
            "archived"
        )

        employment_status = params.get(
            "employment_status"
        )

        employment_regime = params.get(
            "employment_regime"
        )

        work_mode = params.get(
            "work_mode"
        )

        attendance_mode = params.get(
            "attendance_mode"
        )

        attendance_enabled = params.get(
            "attendance_enabled"
        )

        track_operational_time = params.get(
            "track_operational_time"
        )

        include_in_evaluation = params.get(
            "include_in_staff_evaluation"
        )

        manager = params.get(
            "manager"
        )

        search = params.get(
            "search",
            "",
        ).strip()

        if archived == "true":
            queryset = queryset.filter(
                archived_at__isnull=False,
            )
        elif archived == "all":
            pass
        else:
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        if employment_status:
            queryset = queryset.filter(
                employment_status=employment_status,
            )

        if employment_regime:
            queryset = queryset.filter(
                employment_regime=employment_regime,
            )

        if work_mode:
            queryset = queryset.filter(
                work_mode=work_mode,
            )

        if attendance_mode:
            queryset = queryset.filter(
                attendance_mode=attendance_mode,
            )

        if attendance_enabled in (
            "true",
            "false",
        ):
            queryset = queryset.filter(
                attendance_enabled=(
                    attendance_enabled == "true"
                )
            )

        if track_operational_time in (
            "true",
            "false",
        ):
            queryset = queryset.filter(
                track_operational_time=(
                    track_operational_time
                    == "true"
                )
            )

        if include_in_evaluation in (
            "true",
            "false",
        ):
            queryset = queryset.filter(
                include_in_staff_evaluation=(
                    include_in_evaluation
                    == "true"
                )
            )

        if manager:
            queryset = queryset.filter(
                manager_id=manager,
            )

        if search:
            queryset = queryset.filter(
                Q(
                    employee_code__icontains=search
                )
                | Q(
                    user__username__icontains=search
                )
                | Q(
                    user__first_name__icontains=search
                )
                | Q(
                    user__paternal_last_name__icontains=search
                )
                | Q(
                    user__maternal_last_name__icontains=search
                )
                | Q(
                    user__email__icontains=search
                )
            )

        return queryset.order_by(
            "user__first_name",
            "user__paternal_last_name",
            "user__maternal_last_name",
        )

    def perform_create(
        self,
        serializer,
    ):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(
        self,
        serializer,
    ):
        serializer.save(
            updated_by=self.request.user,
        )

    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        DELETE no elimina físicamente.

        Archiva el perfil laboral para conservar
        historial y trazabilidad.
        """

        instance = self.get_object()

        if instance.archived_at:
            return Response(
                {
                    "detail": (
                        "El perfil laboral "
                        "ya está archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = str(
            request.data.get(
                "reason",
                "Archivado desde la API.",
            )
            or ""
        ).strip()

        instance.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Perfil laboral archivado "
                    "correctamente."
                ),
                "id": str(instance.id),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="archive",
    )
    def archive_profile(
        self,
        request,
        pk=None,
    ):
        instance = self.get_object()

        if instance.archived_at:
            return Response(
                {
                    "detail": (
                        "El perfil laboral "
                        "ya está archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = str(
            request.data.get(
                "reason",
                "",
            )
            or ""
        ).strip()

        if not reason:
            return Response(
                {
                    "reason": (
                        "Debes indicar el motivo "
                        "de archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.archive(
            user=request.user,
            reason=reason,
        )

        serializer = self.get_serializer(
            instance
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore_profile(
        self,
        request,
        pk=None,
    ):
        queryset = (
            EmployeeProfile.objects
            .select_related(
                "user",
                "manager",
                "created_by",
                "updated_by",
                "archived_by",
            )
        )

        try:
            instance = queryset.get(
                pk=pk
            )
        except EmployeeProfile.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Perfil laboral no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not instance.archived_at:
            return Response(
                {
                    "detail": (
                        "El perfil laboral "
                        "no está archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.restore(
            user=request.user,
        )

        serializer = self.get_serializer(
            instance
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=("get",),
        url_path="current",
    )
    def current_profiles(
        self,
        request,
    ):
        today = timezone.localdate()

        queryset = (
            self.get_queryset()
            .filter(
                archived_at__isnull=True,
                effective_from__lte=today,
            )
            .filter(
                Q(
                    effective_until__isnull=True
                )
                | Q(
                    effective_until__gte=today
                )
            )
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

    @action(
        detail=False,
        methods=("get",),
        url_path="archived",
    )
    def archived_profiles(
        self,
        request,
    ):
        queryset = (
            EmployeeProfile.objects
            .select_related(
                "user",
                "manager",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .filter(
                archived_at__isnull=False,
            )
            .order_by(
                "-archived_at",
            )
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