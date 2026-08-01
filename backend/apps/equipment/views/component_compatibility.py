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

from ..models import ComponentCompatibility
from ..serializers import (
    ArchiveComponentCompatibilitySerializer,
    ComponentCompatibilityCreateUpdateSerializer,
    ComponentCompatibilityDetailSerializer,
    ComponentCompatibilityListSerializer,
)
from .equipment_type import parse_boolean_query_param


class ComponentCompatibilityListCreateView(
    ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            ComponentCompatibility.objects
            .select_related(
                "component",
                "component__component_type",
                "equipment_family",
                "equipment_family__brand",
                "equipment_family__equipment_type",
                "equipment_model",
                "equipment_model__brand",
                "equipment_model__equipment_type",
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
                    manufacturer_code_override__icontains=search,
                )
                | Q(
                    technical_notes__icontains=search,
                )
                | Q(
                    equipment_family__name__icontains=search,
                )
                | Q(
                    equipment_family__code__icontains=search,
                )
                | Q(
                    equipment_model__name__icontains=search,
                )
                | Q(
                    equipment_model__code__icontains=search,
                )
                | Q(
                    equipment_family__brand__name__icontains=search,
                )
                | Q(
                    equipment_model__brand__name__icontains=search,
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

        equipment_family_id = str(
            self.request.query_params.get(
                "equipment_family",
                "",
            )
        ).strip()

        if equipment_family_id:
            queryset = queryset.filter(
                equipment_family_id=equipment_family_id,
            )

        equipment_model_id = str(
            self.request.query_params.get(
                "equipment_model",
                "",
            )
        ).strip()

        if equipment_model_id:
            queryset = queryset.filter(
                equipment_model_id=equipment_model_id,
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

        brand_id = str(
            self.request.query_params.get(
                "brand",
                "",
            )
        ).strip()

        if brand_id:
            queryset = queryset.filter(
                equipment_family__brand_id=brand_id,
            )

        equipment_type_id = str(
            self.request.query_params.get(
                "equipment_type",
                "",
            )
        ).strip()

        if equipment_type_id:
            queryset = queryset.filter(
                equipment_family__equipment_type_id=(
                    equipment_type_id
                ),
            )

        is_required = parse_boolean_query_param(
            self.request.query_params.get(
                "is_required"
            )
        )

        if is_required is not None:
            queryset = queryset.filter(
                is_required=is_required,
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
            "equipment_family__brand__name",
            "equipment_family__name",
            "display_order",
            "component__name",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return (
                ComponentCompatibilityCreateUpdateSerializer
            )

        return ComponentCompatibilityListSerializer

    @transaction.atomic
    def perform_create(
        self,
        serializer,
    ):
        serializer.save()


class ComponentCompatibilityDetailUpdateView(
    RetrieveUpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            ComponentCompatibility.objects
            .select_related(
                "component",
                "component__component_type",
                "equipment_family",
                "equipment_family__brand",
                "equipment_family__equipment_type",
                "equipment_model",
                "equipment_model__brand",
                "equipment_model__equipment_type",
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
                ComponentCompatibilityCreateUpdateSerializer
            )

        return ComponentCompatibilityDetailSerializer

    @transaction.atomic
    def perform_update(
        self,
        serializer,
    ):
        serializer.save()


class ArchiveComponentCompatibilityView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        compatibility_id,
    ):
        compatibility = (
            ComponentCompatibility.objects.filter(
                id=compatibility_id,
            )
            .first()
        )

        if not compatibility:
            return Response(
                {
                    "detail": (
                        "Compatibilidad no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if compatibility.is_archived:
            return Response(
                {
                    "detail": (
                        "La compatibilidad ya se encuentra "
                        "archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            ArchiveComponentCompatibilitySerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        compatibility.archive(
            user=request.user,
            reason=serializer.validated_data.get(
                "reason",
                "",
            ),
        )

        return Response(
            {
                "detail": (
                    "Compatibilidad archivada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestoreComponentCompatibilityView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        compatibility_id,
    ):
        compatibility = (
            ComponentCompatibility.objects.filter(
                id=compatibility_id,
            )
            .first()
        )

        if not compatibility:
            return Response(
                {
                    "detail": (
                        "Compatibilidad no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not compatibility.is_archived:
            return Response(
                {
                    "detail": (
                        "La compatibilidad no se encuentra "
                        "archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        compatibility.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Compatibilidad restaurada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )