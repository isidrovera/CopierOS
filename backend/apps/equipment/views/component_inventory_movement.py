# -*- coding: utf-8 -*-
from django.db.models import Q

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated

from ..models import ComponentInventoryMovement
from ..serializers import (
    ComponentInventoryMovementCreateSerializer,
    ComponentInventoryMovementDetailSerializer,
    ComponentInventoryMovementListSerializer,
)


class ComponentInventoryMovementListCreateView(
    ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            ComponentInventoryMovement.objects
            .select_related(
                "inventory",
                "inventory__component",
                "inventory__component__component_type",
                "created_by",
                "updated_by",
            )
            .all()
        )

        search = str(
            self.request.query_params.get(
                "search",
                "",
            )
        ).strip()

        if search:
            queryset = queryset.filter(
                Q(
                    inventory__internal_code__icontains=search,
                )
                | Q(
                    inventory__serial_number__icontains=search,
                )
                | Q(
                    inventory__component__code__icontains=search,
                )
                | Q(
                    inventory__component__name__icontains=search,
                )
                | Q(
                    document_number__icontains=search,
                )
                | Q(
                    reference_type__icontains=search,
                )
                | Q(
                    reason__icontains=search,
                )
                | Q(
                    notes__icontains=search,
                )
            )

        inventory_id = str(
            self.request.query_params.get(
                "inventory",
                "",
            )
        ).strip()

        if inventory_id:
            queryset = queryset.filter(
                inventory_id=inventory_id,
            )

        component_id = str(
            self.request.query_params.get(
                "component",
                "",
            )
        ).strip()

        if component_id:
            queryset = queryset.filter(
                inventory__component_id=component_id,
            )

        movement_type = str(
            self.request.query_params.get(
                "movement_type",
                "",
            )
        ).strip()

        if movement_type:
            queryset = queryset.filter(
                movement_type=movement_type,
            )

        reference_type = str(
            self.request.query_params.get(
                "reference_type",
                "",
            )
        ).strip()

        if reference_type:
            queryset = queryset.filter(
                reference_type=reference_type,
            )

        reference_id = str(
            self.request.query_params.get(
                "reference_id",
                "",
            )
        ).strip()

        if reference_id:
            queryset = queryset.filter(
                reference_id=reference_id,
            )

        document_number = str(
            self.request.query_params.get(
                "document_number",
                "",
            )
        ).strip()

        if document_number:
            queryset = queryset.filter(
                document_number__icontains=document_number,
            )

        date_from = str(
            self.request.query_params.get(
                "date_from",
                "",
            )
        ).strip()

        if date_from:
            queryset = queryset.filter(
                occurred_at__date__gte=date_from,
            )

        date_to = str(
            self.request.query_params.get(
                "date_to",
                "",
            )
        ).strip()

        if date_to:
            queryset = queryset.filter(
                occurred_at__date__lte=date_to,
            )

        return queryset.order_by(
            "-occurred_at",
            "-created_at",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ComponentInventoryMovementCreateSerializer

        return ComponentInventoryMovementListSerializer


class ComponentInventoryMovementDetailView(
    RetrieveAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    serializer_class = (
        ComponentInventoryMovementDetailSerializer
    )

    def get_queryset(self):
        return (
            ComponentInventoryMovement.objects
            .select_related(
                "inventory",
                "inventory__component",
                "inventory__component__component_type",
                "created_by",
                "updated_by",
            )
            .all()
        )