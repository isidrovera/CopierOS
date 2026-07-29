# -*- coding: utf-8 -*-
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from ..models.repair_part_source import RepairPartSource
from ..serializers.repair_part_source import (
    RepairPartSourceCreateUpdateSerializer,
    RepairPartSourceDetailSerializer,
    RepairPartSourceListSerializer,
)
from .common import get_boolean_query_param


class RepairPartSourceViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = (
        "item__request__code",
        "item__component__name",
        "item__custom_name",
        "inventory__internal_code",
        "inventory__serial_number",
        "donor_equipment__internal_code",
        "donor_equipment__serial_number",
        "supplier_name",
        "purchase_reference",
        "warehouse_location",
        "justification",
    )
    ordering_fields = (
        "source_type",
        "available_quantity",
        "reserved_quantity",
        "is_confirmed",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)

    def get_queryset(self):
        queryset = (
            RepairPartSource.objects
            .select_related(
                "item",
                "item__request",
                "item__component",
                "inventory",
                "rental_warehouse",
                "donor_equipment",
                "donor_rental_equipment",
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
            "source_type": "source_type",
            "inventory": "inventory_id",
            "donor_equipment": "donor_equipment_id",
            "rental_warehouse": "rental_warehouse_id",
            "is_confirmed": "is_confirmed",
        }

        for query_param, field_name in filters_map.items():
            value = self.request.query_params.get(query_param)
            if value is not None and value != "":
                queryset = queryset.filter(**{field_name: value})

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RepairPartSourceListSerializer
        if self.action in {
            "create",
            "update",
            "partial_update",
        }:
            return RepairPartSourceCreateUpdateSerializer
        return RepairPartSourceDetailSerializer
