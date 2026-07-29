# -*- coding: utf-8 -*-
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models.repair_part_replacement import RepairPartReplacement
from ..serializers.repair_part_replacement import (
    RepairPartReplacementCompleteSerializer,
    RepairPartReplacementCreateUpdateSerializer,
    RepairPartReplacementDetailSerializer,
    RepairPartReplacementListSerializer,
)
from ..services.repair_part_replacement import (
    complete_repair_part_replacement,
)
from .common import get_authenticated_actor, get_boolean_query_param


class RepairPartReplacementViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = (
        "item__request__code",
        "item__component__name",
        "item__custom_name",
        "source_equipment__internal_code",
        "source_equipment__serial_number",
        "external_reference",
        "notes",
    )
    ordering_fields = (
        "status",
        "replacement_type",
        "due_at",
        "received_at",
        "completed_at",
        "created_at",
    )
    ordering = ("-created_at",)

    def get_queryset(self):
        queryset = (
            RepairPartReplacement.objects
            .select_related(
                "item",
                "item__request",
                "item__component",
                "source_equipment",
                "replacement_inventory",
                "responsible_user",
                "completed_by",
                "created_by",
                "updated_by",
                "archived_by",
            )
        )

        if not get_boolean_query_param(
            self.request,
            "include_archived",
            False,
        ):
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        filters_map = {
            "item": "item_id",
            "request": "item__request_id",
            "status": "status",
            "replacement_type": "replacement_type",
            "source_equipment": "source_equipment_id",
            "responsible_user": "responsible_user_id",
        }

        for query_param, field_name in filters_map.items():
            value = self.request.query_params.get(query_param)
            if value:
                queryset = queryset.filter(**{field_name: value})

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairPartReplacementListSerializer
        if self.action in {
            "create",
            "update",
            "partial_update",
        }:
            return RepairPartReplacementCreateUpdateSerializer
        return RepairPartReplacementDetailSerializer

    @action(detail=True, methods=("post",), url_path="complete")
    def complete(self, request, pk=None):
        instance = self.get_object()
        serializer = RepairPartReplacementCompleteSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        instance = complete_repair_part_replacement(
            replacement=instance,
            actor=get_authenticated_actor(request),
            notes=serializer.validated_data.get("notes", ""),
        )

        return Response(
            RepairPartReplacementDetailSerializer(
                instance,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )
