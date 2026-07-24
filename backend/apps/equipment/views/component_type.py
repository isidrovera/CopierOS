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

from ..models import ComponentType
from ..serializers import (
    ArchiveComponentTypeSerializer,
    ComponentTypeCreateUpdateSerializer,
    ComponentTypeDetailSerializer,
    ComponentTypeListSerializer,
)
from .equipment_type import parse_boolean_query_param


class ComponentTypeListCreateView(
    ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            ComponentType.objects
            .select_related(
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
                    code__icontains=search,
                )
                | Q(
                    name__icontains=search,
                )
                | Q(
                    description__icontains=search,
                )
            )

        category = str(
            self.request.query_params.get(
                "category",
                "",
            )
        ).strip()

        if category:
            queryset = queryset.filter(
                category=category,
            )

        requires_color = parse_boolean_query_param(
            self.request.query_params.get(
                "requires_color"
            )
        )

        if requires_color is not None:
            queryset = queryset.filter(
                requires_color=requires_color,
            )

        requires_serial_number = (
            parse_boolean_query_param(
                self.request.query_params.get(
                    "requires_serial_number"
                )
            )
        )

        if requires_serial_number is not None:
            queryset = queryset.filter(
                requires_serial_number=(
                    requires_serial_number
                ),
            )

        requires_meter = parse_boolean_query_param(
            self.request.query_params.get(
                "requires_meter"
            )
        )

        if requires_meter is not None:
            queryset = queryset.filter(
                requires_meter=requires_meter,
            )

        controls_stock = parse_boolean_query_param(
            self.request.query_params.get(
                "controls_stock"
            )
        )

        if controls_stock is not None:
            queryset = queryset.filter(
                controls_stock=controls_stock,
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
            "display_order",
            "name",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ComponentTypeCreateUpdateSerializer

        return ComponentTypeListSerializer

    @transaction.atomic
    def perform_create(
        self,
        serializer,
    ):
        serializer.save()


class ComponentTypeDetailUpdateView(
    RetrieveUpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            ComponentType.objects
            .select_related(
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
            return ComponentTypeCreateUpdateSerializer

        return ComponentTypeDetailSerializer

    @transaction.atomic
    def perform_update(
        self,
        serializer,
    ):
        serializer.save()


class ArchiveComponentTypeView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        component_type_id,
    ):
        component_type = (
            ComponentType.objects.filter(
                id=component_type_id,
            )
            .first()
        )

        if not component_type:
            return Response(
                {
                    "detail": (
                        "Tipo de componente no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if component_type.is_archived:
            return Response(
                {
                    "detail": (
                        "El tipo de componente ya se "
                        "encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ArchiveComponentTypeSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        component_type.archive(
            user=request.user,
            reason=serializer.validated_data.get(
                "reason",
                "",
            ),
        )

        return Response(
            {
                "detail": (
                    "Tipo de componente archivado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestoreComponentTypeView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        component_type_id,
    ):
        component_type = (
            ComponentType.objects.filter(
                id=component_type_id,
            )
            .first()
        )

        if not component_type:
            return Response(
                {
                    "detail": (
                        "Tipo de componente no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not component_type.is_archived:
            return Response(
                {
                    "detail": (
                        "El tipo de componente no se "
                        "encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        component_type.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Tipo de componente restaurado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )