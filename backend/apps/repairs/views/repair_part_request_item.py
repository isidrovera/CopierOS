# -*- coding: utf-8 -*-
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models.repair_part_request_item import RepairPartRequestItem
from ..serializers.repair_part_request_item import (
    ArchiveRepairPartRequestItemSerializer,
    RepairPartRequestItemCreateUpdateSerializer,
    RepairPartRequestItemDetailSerializer,
    RepairPartRequestItemListSerializer,
)
from ..services.repair_part_request_item import (
    archive_repair_part_request_item,
    restore_repair_part_request_item,
)
from .common import get_authenticated_actor, get_boolean_query_param


class RepairPartRequestItemViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = (
        "request__code",
        "request__repair__code",
        "component__code",
        "component__name",
        "custom_code",
        "custom_name",
        "technical_reason",
    )
    ordering_fields = (
        "status",
        "urgency",
        "requested_quantity",
        "approved_quantity",
        "created_at",
        "updated_at",
    )
    ordering = ("created_at",)

    def get_queryset(self):
        queryset = (
            RepairPartRequestItem.objects
            .select_related(
                "request",
                "request__repair",
                "request__repair__equipment",
                "checklist_item",
                "component",
                "inventory",
                "donor_equipment",
                "donor_rental_equipment",
                "requested_by",
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
            "request": "request_id",
            "repair": "request__repair_id",
            "status": "status",
            "urgency": "urgency",
            "approval_route": "approval_route",
            "source_type": "source_type",
            "component": "component_id",
            "requested_by": "requested_by_id",
        }

        for query_param, field_name in filters_map.items():
            value = self.request.query_params.get(query_param)
            if value:
                queryset = queryset.filter(**{field_name: value})

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairPartRequestItemListSerializer

        if self.action in {
            "create",
            "update",
            "partial_update",
        }:
            return RepairPartRequestItemCreateUpdateSerializer

        return RepairPartRequestItemDetailSerializer

    def perform_destroy(self, instance):
        archive_repair_part_request_item(
            item=instance,
            actor=get_authenticated_actor(self.request),
            reason="Archivado desde la API.",
        )

    @action(detail=True, methods=("post",), url_path="archive")
    def archive(self, request, pk=None):
        instance = self.get_object()
        serializer = ArchiveRepairPartRequestItemSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        instance = archive_repair_part_request_item(
            item=instance,
            actor=get_authenticated_actor(request),
            reason=serializer.validated_data["reason"],
        )

        return Response(
            RepairPartRequestItemDetailSerializer(
                instance,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=("post",), url_path="restore")
    def restore(self, request, pk=None):
        instance = RepairPartRequestItem.objects.get(pk=pk)

        instance = restore_repair_part_request_item(
            item=instance,
            actor=get_authenticated_actor(request),
        )

        return Response(
            RepairPartRequestItemDetailSerializer(
                instance,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )
