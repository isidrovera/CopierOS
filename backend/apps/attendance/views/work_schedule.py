# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.attendance.models.work_schedule import (
    WorkSchedule,
    WorkScheduleDay,
)

from apps.attendance.serializers.work_schedule import (
    WorkScheduleDaySerializer,
    WorkScheduleSerializer,
)


class WorkScheduleViewSet(ModelViewSet):
    """
    API de horarios laborales.
    """

    serializer_class = WorkScheduleSerializer

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
            WorkSchedule.objects
            .prefetch_related(
                "days",
            )
            .select_related(
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

        schedule_type = params.get(
            "schedule_type"
        )

        is_active = params.get(
            "is_active"
        )

        allows_overnight_shift = params.get(
            "allows_overnight_shift"
        )

        requires_break_clocking = params.get(
            "requires_break_clocking"
        )

        search = str(
            params.get(
                "search",
                "",
            )
            or ""
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

        if schedule_type:
            queryset = queryset.filter(
                schedule_type=schedule_type,
            )

        if is_active in (
            "true",
            "false",
        ):
            queryset = queryset.filter(
                is_active=(
                    is_active == "true"
                )
            )

        if allows_overnight_shift in (
            "true",
            "false",
        ):
            queryset = queryset.filter(
                allows_overnight_shift=(
                    allows_overnight_shift == "true"
                )
            )

        if requires_break_clocking in (
            "true",
            "false",
        ):
            queryset = queryset.filter(
                requires_break_clocking=(
                    requires_break_clocking == "true"
                )
            )

        if search:
            queryset = queryset.filter(
                Q(
                    code__icontains=search
                )
                | Q(
                    name__icontains=search
                )
                | Q(
                    description__icontains=search
                )
            )

        return queryset.order_by(
            "name",
            "code",
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
        instance = self.get_object()

        if instance.archived_at:
            return Response(
                {
                    "detail": (
                        "El horario ya está archivado."
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
                    "Horario archivado correctamente."
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
    def archive_schedule(
        self,
        request,
        pk=None,
    ):
        instance = self.get_object()

        if instance.archived_at:
            return Response(
                {
                    "detail": (
                        "El horario ya está archivado."
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
    def restore_schedule(
        self,
        request,
        pk=None,
    ):
        try:
            instance = (
                WorkSchedule.objects
                .prefetch_related(
                    "days",
                )
                .get(
                    pk=pk
                )
            )
        except WorkSchedule.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Horario no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not instance.archived_at:
            return Response(
                {
                    "detail": (
                        "El horario no está archivado."
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
    def current_schedules(
        self,
        request,
    ):
        today = timezone.localdate()

        queryset = (
            WorkSchedule.objects
            .prefetch_related(
                "days",
            )
            .filter(
                archived_at__isnull=True,
                is_active=True,
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
            .order_by(
                "name",
                "code",
            )
        )

        return self._paginated_response(
            queryset
        )

    @action(
        detail=True,
        methods=("get",),
        url_path="days",
    )
    def schedule_days(
        self,
        request,
        pk=None,
    ):
        schedule = self.get_object()

        queryset = (
            schedule.days
            .filter(
                archived_at__isnull=True,
            )
            .order_by(
                "weekday",
            )
        )

        serializer = WorkScheduleDaySerializer(
            queryset,
            many=True,
            context=self.get_serializer_context(),
        )

        return Response(
            serializer.data
        )

    @action(
        detail=False,
        methods=("get",),
        url_path="archived",
    )
    def archived_schedules(
        self,
        request,
    ):
        queryset = (
            WorkSchedule.objects
            .prefetch_related(
                "days",
            )
            .filter(
                archived_at__isnull=False,
            )
            .order_by(
                "-archived_at",
            )
        )

        return self._paginated_response(
            queryset
        )

    def _paginated_response(
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


class WorkScheduleDayViewSet(ModelViewSet):
    """
    API de días de horarios laborales.
    """

    serializer_class = WorkScheduleDaySerializer

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
            WorkScheduleDay.objects
            .select_related(
                "schedule",
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

        schedule = params.get(
            "schedule"
        )

        weekday = params.get(
            "weekday"
        )

        is_working_day = params.get(
            "is_working_day"
        )

        is_active = params.get(
            "is_active"
        )

        requires_attendance = params.get(
            "requires_attendance"
        )

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

        if schedule:
            queryset = queryset.filter(
                schedule_id=schedule,
            )

        if weekday:
            queryset = queryset.filter(
                weekday=weekday,
            )

        if is_working_day in (
            "true",
            "false",
        ):
            queryset = queryset.filter(
                is_working_day=(
                    is_working_day == "true"
                )
            )

        if is_active in (
            "true",
            "false",
        ):
            queryset = queryset.filter(
                is_active=(
                    is_active == "true"
                )
            )

        if requires_attendance in (
            "true",
            "false",
        ):
            queryset = queryset.filter(
                requires_attendance=(
                    requires_attendance == "true"
                )
            )

        return queryset.order_by(
            "schedule",
            "weekday",
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
        instance = self.get_object()

        if instance.archived_at:
            return Response(
                {
                    "detail": (
                        "El día del horario "
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
                    "Día del horario archivado "
                    "correctamente."
                ),
                "id": str(instance.id),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore_day(
        self,
        request,
        pk=None,
    ):
        try:
            instance = (
                WorkScheduleDay.objects
                .select_related(
                    "schedule",
                )
                .get(
                    pk=pk
                )
            )
        except WorkScheduleDay.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "Día del horario no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not instance.archived_at:
            return Response(
                {
                    "detail": (
                        "El día del horario "
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