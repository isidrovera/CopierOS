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

from ..models import EquipmentModel
from ..serializers import (
    ArchiveEquipmentModelSerializer,
    EquipmentModelCreateUpdateSerializer,
    EquipmentModelDetailSerializer,
    EquipmentModelListSerializer,
)
from .equipment_type import parse_boolean_query_param


class EquipmentModelListCreateView(
    ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            EquipmentModel.objects
            .select_related(
                "brand",
                "equipment_type",
                "equipment_family",
                "equipment_family__brand",
                "equipment_family__equipment_type",
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
                    commercial_name__icontains=search,
                )
                | Q(
                    family__icontains=search,
                )
                | Q(
                    equipment_family__code__icontains=search,
                )
                | Q(
                    equipment_family__name__icontains=search,
                )
                | Q(
                    manufacturer_reference__icontains=search,
                )
                | Q(
                    brand__name__icontains=search,
                )
                | Q(
                    equipment_type__name__icontains=search,
                )
            )

        brand_id = str(
            self.request.query_params.get(
                "brand",
                "",
            )
        ).strip()

        if brand_id:
            queryset = queryset.filter(
                brand_id=brand_id,
            )

        equipment_type_id = str(
            self.request.query_params.get(
                "equipment_type",
                "",
            )
        ).strip()

        if equipment_type_id:
            queryset = queryset.filter(
                equipment_type_id=equipment_type_id,
            )

        family = str(
            self.request.query_params.get(
                "family",
                "",
            )
        ).strip()

        if family:
            queryset = queryset.filter(
                family__icontains=family,
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

        color_mode = str(
            self.request.query_params.get(
                "color_mode",
                "",
            )
        ).strip()

        if color_mode:
            queryset = queryset.filter(
                color_mode=color_mode,
            )

        technology = str(
            self.request.query_params.get(
                "technology",
                "",
            )
        ).strip()

        if technology:
            queryset = queryset.filter(
                technology=technology,
            )

        maximum_paper_size = str(
            self.request.query_params.get(
                "maximum_paper_size",
                "",
            )
        ).strip()

        if maximum_paper_size:
            queryset = queryset.filter(
                maximum_paper_size=maximum_paper_size,
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

        is_multifunction = parse_boolean_query_param(
            self.request.query_params.get(
                "is_multifunction"
            )
        )

        if is_multifunction is not None:
            queryset = queryset.filter(
                is_multifunction=is_multifunction,
            )

        supports_printing = parse_boolean_query_param(
            self.request.query_params.get(
                "supports_printing"
            )
        )

        if supports_printing is not None:
            queryset = queryset.filter(
                supports_printing=supports_printing,
            )

        supports_copying = parse_boolean_query_param(
            self.request.query_params.get(
                "supports_copying"
            )
        )

        if supports_copying is not None:
            queryset = queryset.filter(
                supports_copying=supports_copying,
            )

        supports_scanning = parse_boolean_query_param(
            self.request.query_params.get(
                "supports_scanning"
            )
        )

        if supports_scanning is not None:
            queryset = queryset.filter(
                supports_scanning=supports_scanning,
            )

        supports_fax = parse_boolean_query_param(
            self.request.query_params.get(
                "supports_fax"
            )
        )

        if supports_fax is not None:
            queryset = queryset.filter(
                supports_fax=supports_fax,
            )

        supports_network = parse_boolean_query_param(
            self.request.query_params.get(
                "supports_network"
            )
        )

        if supports_network is not None:
            queryset = queryset.filter(
                supports_network=supports_network,
            )

        supports_duplex = parse_boolean_query_param(
            self.request.query_params.get(
                "supports_duplex"
            )
        )

        if supports_duplex is not None:
            queryset = queryset.filter(
                supports_duplex=supports_duplex,
            )

        supports_accessories = parse_boolean_query_param(
            self.request.query_params.get(
                "supports_accessories"
            )
        )

        if supports_accessories is not None:
            queryset = queryset.filter(
                supports_accessories=supports_accessories,
            )

        supports_technical_units = (
            parse_boolean_query_param(
                self.request.query_params.get(
                    "supports_technical_units"
                )
            )
        )

        if supports_technical_units is not None:
            queryset = queryset.filter(
                supports_technical_units=(
                    supports_technical_units
                ),
            )

        return queryset.order_by(
            "brand__name",
            "display_order",
            "name",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return (
                EquipmentModelCreateUpdateSerializer
            )

        return EquipmentModelListSerializer

    @transaction.atomic
    def perform_create(
        self,
        serializer,
    ):
        serializer.save()


class EquipmentModelDetailUpdateView(
    RetrieveUpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            EquipmentModel.objects
            .select_related(
                "brand",
                "equipment_type",
                "equipment_family",
                "equipment_family__brand",
                "equipment_family__equipment_type",
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
                EquipmentModelCreateUpdateSerializer
            )

        return EquipmentModelDetailSerializer

    @transaction.atomic
    def perform_update(
        self,
        serializer,
    ):
        serializer.save()


class ArchiveEquipmentModelView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        equipment_model_id,
    ):
        equipment_model = (
            EquipmentModel.objects.filter(
                id=equipment_model_id,
            )
            .first()
        )

        if not equipment_model:
            return Response(
                {
                    "detail": (
                        "Modelo de equipo no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if equipment_model.is_archived:
            return Response(
                {
                    "detail": (
                        "El modelo ya se encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            ArchiveEquipmentModelSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        reason = serializer.validated_data.get(
            "reason",
            "",
        )

        equipment_model.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Modelo archivado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestoreEquipmentModelView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        equipment_model_id,
    ):
        equipment_model = (
            EquipmentModel.objects.filter(
                id=equipment_model_id,
            )
            .first()
        )

        if not equipment_model:
            return Response(
                {
                    "detail": (
                        "Modelo de equipo no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not equipment_model.is_archived:
            return Response(
                {
                    "detail": (
                        "El modelo no se encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        equipment_model.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Modelo restaurado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )