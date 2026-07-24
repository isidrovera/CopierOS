# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models import Q

from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import ComponentInventory
from ..serializers import (
    ArchiveComponentInventorySerializer,
    ComponentInventoryCreateUpdateSerializer,
    ComponentInventoryDetailSerializer,
    ComponentInventoryListSerializer,
)
from .equipment_type import parse_boolean_query_param


class ComponentInventoryListCreateView(
    ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            ComponentInventory.objects
            .select_related(
                "component",
                "component__component_type",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .all()
        )

        include_archived = parse_boolean_query_param(
            self.request.query_params.get(
                "include_archived"
            )
        )

        if include_archived is not True:
            queryset = queryset.filter(
                archived_at__isnull=True,
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
                    internal_code__icontains=search,
                )
                | Q(
                    serial_number__icontains=search,
                )
                | Q(
                    lot_number__icontains=search,
                )
                | Q(
                    warehouse__icontains=search,
                )
                | Q(
                    location__icontains=search,
                )
                | Q(
                    supplier_name__icontains=search,
                )
                | Q(
                    component__code__icontains=search,
                )
                | Q(
                    component__name__icontains=search,
                )
                | Q(
                    component__manufacturer_code__icontains=search,
                )
            )

        component_id = str(
            self.request.query_params.get(
                "component",
                "",
            )
        ).strip()

        if component_id:
            queryset = queryset.filter(
                component_id=component_id,
            )

        component_type_id = str(
            self.request.query_params.get(
                "component_type",
                "",
            )
        ).strip()

        if component_type_id:
            queryset = queryset.filter(
                component__component_type_id=component_type_id,
            )

        category = str(
            self.request.query_params.get(
                "category",
                "",
            )
        ).strip()

        if category:
            queryset = queryset.filter(
                component__component_type__category=category,
            )

        color = str(
            self.request.query_params.get(
                "color",
                "",
            )
        ).strip()

        if color:
            queryset = queryset.filter(
                component__color=color,
            )

        condition = str(
            self.request.query_params.get(
                "condition",
                "",
            )
        ).strip()

        if condition:
            queryset = queryset.filter(
                condition=condition,
            )

        inventory_status = str(
            self.request.query_params.get(
                "status",
                "",
            )
        ).strip()

        if inventory_status:
            queryset = queryset.filter(
                status=inventory_status,
            )

        warehouse = str(
            self.request.query_params.get(
                "warehouse",
                "",
            )
        ).strip()

        if warehouse:
            queryset = queryset.filter(
                warehouse__iexact=warehouse,
            )

        has_stock = parse_boolean_query_param(
            self.request.query_params.get(
                "has_stock"
            )
        )

        if has_stock is True:
            queryset = queryset.filter(
                quantity__gt=0,
            )

        if has_stock is False:
            queryset = queryset.filter(
                quantity__lte=0,
            )

        is_active = parse_boolean_query_param(
            self.request.query_params.get(
                "is_active"
            )
        )

        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active,
            )

        return queryset.order_by(
            "component__name",
            "internal_code",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ComponentInventoryCreateUpdateSerializer

        return ComponentInventoryListSerializer

    @transaction.atomic
    def perform_create(
        self,
        serializer,
    ):
        serializer.save()


class ComponentInventoryDetailUpdateView(
    RetrieveUpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            ComponentInventory.objects
            .select_related(
                "component",
                "component__component_type",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .all()
        )

    def get_serializer_class(self):
        if self.request.method in (
            "PUT",
            "PATCH",
        ):
            return ComponentInventoryCreateUpdateSerializer

        return ComponentInventoryDetailSerializer

    @transaction.atomic
    def perform_update(
        self,
        serializer,
    ):
        serializer.save()


class ArchiveComponentInventoryView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        inventory_id,
    ):
        inventory = (
            ComponentInventory.objects.filter(
                id=inventory_id,
            )
            .first()
        )

        if not inventory:
            return Response(
                {
                    "detail": (
                        "Registro de inventario no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if inventory.is_archived:
            return Response(
                {
                    "detail": (
                        "El registro de inventario ya se "
                        "encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ArchiveComponentInventorySerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        inventory.archive(
            user=request.user,
            reason=serializer.validated_data.get(
                "reason",
                "",
            ),
        )

        return Response(
            {
                "detail": (
                    "Registro de inventario archivado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestoreComponentInventoryView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        inventory_id,
    ):
        inventory = (
            ComponentInventory.objects.filter(
                id=inventory_id,
            )
            .first()
        )

        if not inventory:
            return Response(
                {
                    "detail": (
                        "Registro de inventario no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not inventory.is_archived:
            return Response(
                {
                    "detail": (
                        "El registro de inventario no se "
                        "encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        inventory.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Registro de inventario restaurado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )