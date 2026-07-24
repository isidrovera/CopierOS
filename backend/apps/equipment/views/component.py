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

from ..models import EquipmentComponent
from ..serializers import (
    ArchiveEquipmentComponentSerializer,
    EquipmentComponentCreateUpdateSerializer,
    EquipmentComponentDetailSerializer,
    EquipmentComponentListSerializer,
)
from .equipment_type import parse_boolean_query_param


class EquipmentComponentListCreateView(
    ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            EquipmentComponent.objects
            .select_related(
                "component_type",
                "parent_component",
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
                    manufacturer_code__icontains=search,
                )
                | Q(
                    alternative_code__icontains=search,
                )
                | Q(
                    description__icontains=search,
                )
                | Q(
                    technical_notes__icontains=search,
                )
                | Q(
                    component_type__name__icontains=search,
                )
                | Q(
                    parent_component__name__icontains=search,
                )
            )

        component_type_id = str(
            self.request.query_params.get(
                "component_type",
                "",
            )
        ).strip()

        if component_type_id:
            queryset = queryset.filter(
                component_type_id=component_type_id,
            )

        category = str(
            self.request.query_params.get(
                "category",
                "",
            )
        ).strip()

        if category:
            queryset = queryset.filter(
                component_type__category=category,
            )

        parent_component_id = str(
            self.request.query_params.get(
                "parent_component",
                "",
            )
        ).strip()

        if parent_component_id:
            queryset = queryset.filter(
                parent_component_id=parent_component_id,
            )

        color = str(
            self.request.query_params.get(
                "color",
                "",
            )
        ).strip()

        if color:
            queryset = queryset.filter(
                color=color,
            )

        condition_control = str(
            self.request.query_params.get(
                "condition_control",
                "",
            )
        ).strip()

        if condition_control:
            queryset = queryset.filter(
                condition_control=condition_control,
            )

        is_consumable = parse_boolean_query_param(
            self.request.query_params.get(
                "is_consumable"
            )
        )

        if is_consumable is not None:
            queryset = queryset.filter(
                is_consumable=is_consumable,
            )

        is_reusable = parse_boolean_query_param(
            self.request.query_params.get(
                "is_reusable"
            )
        )

        if is_reusable is not None:
            queryset = queryset.filter(
                is_reusable=is_reusable,
            )

        can_be_repaired = parse_boolean_query_param(
            self.request.query_params.get(
                "can_be_repaired"
            )
        )

        if can_be_repaired is not None:
            queryset = queryset.filter(
                can_be_repaired=can_be_repaired,
            )

        requires_individual_serial = (
            parse_boolean_query_param(
                self.request.query_params.get(
                    "requires_individual_serial"
                )
            )
        )

        if requires_individual_serial is not None:
            queryset = queryset.filter(
                requires_individual_serial=(
                    requires_individual_serial
                ),
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
            "component_type__display_order",
            "display_order",
            "name",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return EquipmentComponentCreateUpdateSerializer

        return EquipmentComponentListSerializer

    @transaction.atomic
    def perform_create(
        self,
        serializer,
    ):
        serializer.save()


class EquipmentComponentDetailUpdateView(
    RetrieveUpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            EquipmentComponent.objects
            .select_related(
                "component_type",
                "parent_component",
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
            return EquipmentComponentCreateUpdateSerializer

        return EquipmentComponentDetailSerializer

    @transaction.atomic
    def perform_update(
        self,
        serializer,
    ):
        serializer.save()


class ArchiveEquipmentComponentView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        component_id,
    ):
        component = (
            EquipmentComponent.objects.filter(
                id=component_id,
            )
            .first()
        )

        if not component:
            return Response(
                {
                    "detail": (
                        "Componente no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if component.is_archived:
            return Response(
                {
                    "detail": (
                        "El componente ya se encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ArchiveEquipmentComponentSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        component.archive(
            user=request.user,
            reason=serializer.validated_data.get(
                "reason",
                "",
            ),
        )

        return Response(
            {
                "detail": (
                    "Componente archivado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestoreEquipmentComponentView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        component_id,
    ):
        component = (
            EquipmentComponent.objects.filter(
                id=component_id,
            )
            .first()
        )

        if not component:
            return Response(
                {
                    "detail": (
                        "Componente no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not component.is_archived:
            return Response(
                {
                    "detail": (
                        "El componente no se encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        component.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Componente restaurado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )