# -*- coding: utf-8 -*-
from rest_framework import (
    filters,
    mixins,
    viewsets,
)
from rest_framework.permissions import IsAuthenticated

from ..models import RepairStatusHistory
from ..serializers import (
    RepairStatusHistoryDetailSerializer,
    RepairStatusHistoryListSerializer,
)
from .common import get_boolean_query_param


class RepairStatusHistoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (
        IsAuthenticated,
    )

    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    search_fields = (
        "repair__code",
        "repair__equipment__serial_number",
        "reason",
        "observations",
        "source",
        "changed_by__first_name",
        "changed_by__last_name",
        "changed_by__email",
    )

    ordering_fields = (
        "changed_at",
        "previous_status",
        "new_status",
        "duration_minutes",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-changed_at",
        "-created_at",
    )

    def get_queryset(self):
        queryset = (
            RepairStatusHistory.objects
            .select_related(
                "repair",
                "repair__equipment",
                "changed_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
        )

        include_archived = get_boolean_query_param(
            self.request,
            "include_archived",
            False,
        )

        if not include_archived:
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        repair_id = self.request.query_params.get(
            "repair"
        )

        if repair_id:
            queryset = queryset.filter(
                repair_id=repair_id,
            )

        equipment_id = self.request.query_params.get(
            "equipment"
        )

        if equipment_id:
            queryset = queryset.filter(
                repair__equipment_id=equipment_id,
            )

        changed_by_id = self.request.query_params.get(
            "changed_by"
        )

        if changed_by_id:
            queryset = queryset.filter(
                changed_by_id=changed_by_id,
            )

        previous_status = (
            self.request.query_params.get(
                "previous_status"
            )
        )

        if previous_status:
            previous_statuses = [
                value.strip()
                for value in previous_status.split(",")
                if value.strip()
            ]

            if previous_statuses:
                queryset = queryset.filter(
                    previous_status__in=previous_statuses,
                )

        new_status = self.request.query_params.get(
            "new_status"
        )

        if new_status:
            new_statuses = [
                value.strip()
                for value in new_status.split(",")
                if value.strip()
            ]

            if new_statuses:
                queryset = queryset.filter(
                    new_status__in=new_statuses,
                )

        changed_automatically = (
            get_boolean_query_param(
                self.request,
                "changed_automatically",
                None,
            )
        )

        if changed_automatically is not None:
            queryset = queryset.filter(
                changed_automatically=(
                    changed_automatically
                ),
            )

        source = self.request.query_params.get(
            "source"
        )

        if source:
            sources = [
                value.strip()
                for value in source.split(",")
                if value.strip()
            ]

            if sources:
                queryset = queryset.filter(
                    source__in=sources,
                )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairStatusHistoryListSerializer

        return RepairStatusHistoryDetailSerializer