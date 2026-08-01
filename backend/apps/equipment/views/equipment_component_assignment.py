# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models import Q

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated

from ..models import EquipmentComponentAssignment
from ..serializers import (
    EquipmentComponentAssignmentCreateUpdateSerializer,
    EquipmentComponentAssignmentDetailSerializer,
    EquipmentComponentAssignmentListSerializer,
)
from .equipment_type import parse_boolean_query_param


class EquipmentComponentAssignmentListCreateView(
    ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            EquipmentComponentAssignment.objects
            .select_related(
                "equipment",
                "equipment__equipment_model",
                "equipment__equipment_model__brand",
                "equipment__equipment_model__equipment_family",
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
                    equipment__serial_number__icontains=search,
                )
                | Q(
                    equipment__internal_code__icontains=search,
                )
                | Q(
                    equipment__equipment_model__name__icontains=search,
                )
                | Q(
                    equipment__equipment_model__code__icontains=search,
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
                | Q(
                    component__alternative_code__icontains=search,
                )
                | Q(
                    serial_number__icontains=search,
                )
                | Q(
                    position__icontains=search,
                )
                | Q(
                    installation_notes__icontains=search,
                )
                | Q(
                    removal_notes__icontains=search,
                )
            )

        equipment_id = str(
            self.request.query_params.get(
                "equipment",
                "",
            )
        ).strip()

        if equipment_id:
            queryset = queryset.filter(
                equipment_id=equipment_id,
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
                component__component_type_id=(
                    component_type_id
                ),
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

        serial_number = str(
            self.request.query_params.get(
                "serial_number",
                "",
            )
        ).strip()

        if serial_number:
            queryset = queryset.filter(
                serial_number__icontains=serial_number,
            )

        assignment_status = str(
            self.request.query_params.get(
                "status",
                "",
            )
        ).strip()

        if assignment_status:
            queryset = queryset.filter(
                status=assignment_status,
            )

        position = str(
            self.request.query_params.get(
                "position",
                "",
            )
        ).strip().lower()

        if position:
            queryset = queryset.filter(
                position=position,
            )

        reference_type = str(
            self.request.query_params.get(
                "reference_type",
                "",
            )
        ).strip().lower()

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
            "-installed_at",
            "-created_at",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return (
                EquipmentComponentAssignmentCreateUpdateSerializer
            )

        return EquipmentComponentAssignmentListSerializer

    @transaction.atomic
    def perform_create(
        self,
        serializer,
    ):
        serializer.save()


class EquipmentComponentAssignmentDetailUpdateView(
    RetrieveUpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            EquipmentComponentAssignment.objects
            .select_related(
                "equipment",
                "equipment__equipment_model",
                "equipment__equipment_model__brand",
                "equipment__equipment_model__equipment_family",
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
            return (
                EquipmentComponentAssignmentCreateUpdateSerializer
            )

        return EquipmentComponentAssignmentDetailSerializer

    @transaction.atomic
    def perform_update(
        self,
        serializer,
    ):
        serializer.save()
