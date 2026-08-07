# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.attendance.models.holiday_calendar import (
    HolidayCalendar,
    HolidayCalendarDay,
)

from apps.attendance.serializers.holiday_calendar import (
    HolidayCalendarDaySerializer,
    HolidayCalendarSerializer,
)


class HolidayCalendarViewSet(ModelViewSet):
    serializer_class = HolidayCalendarSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            HolidayCalendar.objects
            .select_related(
                "work_location",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .prefetch_related("days")
        )

        params = self.request.query_params

        archived = params.get("archived")
        calendar_type = params.get("calendar_type")
        work_location = params.get("work_location")
        is_active = params.get("is_active")
        is_default = params.get("is_default")
        search = str(params.get("search", "") or "").strip()

        if archived == "true":
            queryset = queryset.filter(
                archived_at__isnull=False,
            )
        elif archived != "all":
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        if calendar_type:
            queryset = queryset.filter(
                calendar_type=calendar_type,
            )

        if work_location:
            queryset = queryset.filter(
                work_location_id=work_location,
            )

        if is_active in ("true", "false"):
            queryset = queryset.filter(
                is_active=(is_active == "true"),
            )

        if is_default in ("true", "false"):
            queryset = queryset.filter(
                is_default=(is_default == "true"),
            )

        if search:
            queryset = queryset.filter(
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(region__icontains=search)
                | Q(province__icontains=search)
                | Q(district__icontains=search)
            )

        return queryset.order_by(
            "-is_default",
            "name",
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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

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

        return Response(
            {"detail": "Calendario archivado correctamente."},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore_calendar(self, request, pk=None):
        instance = HolidayCalendar.objects.get(pk=pk)

        instance.restore(
            user=request.user,
        )

        return Response(
            self.get_serializer(instance).data
        )

    @action(
        detail=False,
        methods=("get",),
        url_path="current",
    )
    def current_calendars(self, request):
        today = timezone.localdate()

        queryset = (
            self.get_queryset()
            .filter(
                is_active=True,
                effective_from__lte=today,
            )
            .filter(
                Q(effective_until__isnull=True)
                | Q(effective_until__gte=today)
            )
        )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    @action(
        detail=True,
        methods=("get",),
        url_path="days",
    )
    def calendar_days(self, request, pk=None):
        calendar = self.get_object()

        queryset = calendar.days.filter(
            archived_at__isnull=True,
        ).order_by("date")

        serializer = HolidayCalendarDaySerializer(
            queryset,
            many=True,
            context=self.get_serializer_context(),
        )

        return Response(serializer.data)


class HolidayCalendarDayViewSet(ModelViewSet):
    serializer_class = HolidayCalendarDaySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            HolidayCalendarDay.objects
            .select_related(
                "calendar",
                "created_by",
                "updated_by",
                "archived_by",
            )
        )

        params = self.request.query_params

        archived = params.get("archived")
        calendar = params.get("calendar")
        day_type = params.get("day_type")
        year = params.get("year")
        month = params.get("month")

        if archived == "true":
            queryset = queryset.filter(
                archived_at__isnull=False,
            )
        elif archived != "all":
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        if calendar:
            queryset = queryset.filter(
                calendar_id=calendar,
            )

        if day_type:
            queryset = queryset.filter(
                day_type=day_type,
            )

        if year:
            queryset = queryset.filter(
                date__year=year,
            )

        if month:
            queryset = queryset.filter(
                date__month=month,
            )

        return queryset.order_by("date")

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

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

        return Response(
            {"detail": "Día archivado correctamente."},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("post",),
        url_path="restore",
    )
    def restore_day(self, request, pk=None):
        instance = HolidayCalendarDay.objects.get(
            pk=pk
        )

        instance.restore(
            user=request.user,
        )

        return Response(
            self.get_serializer(instance).data
        )