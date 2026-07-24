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

from ..models import EquipmentBrand
from ..serializers import (
    ArchiveEquipmentBrandSerializer,
    EquipmentBrandCreateUpdateSerializer,
    EquipmentBrandDetailSerializer,
    EquipmentBrandListSerializer,
)
from .equipment_type import parse_boolean_query_param


class EquipmentBrandListCreateView(
    ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            EquipmentBrand.objects
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
                    legal_name__icontains=search,
                )
                | Q(
                    country_name__icontains=search,
                )
                | Q(
                    description__icontains=search,
                )
            )

        country_code = str(
            self.request.query_params.get(
                "country_code",
                "",
            )
        ).strip().upper()

        if country_code:
            queryset = queryset.filter(
                country_code=country_code,
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
            return (
                EquipmentBrandCreateUpdateSerializer
            )

        return EquipmentBrandListSerializer

    @transaction.atomic
    def perform_create(
        self,
        serializer,
    ):
        serializer.save()


class EquipmentBrandDetailUpdateView(
    RetrieveUpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            EquipmentBrand.objects
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
            return (
                EquipmentBrandCreateUpdateSerializer
            )

        return EquipmentBrandDetailSerializer

    @transaction.atomic
    def perform_update(
        self,
        serializer,
    ):
        serializer.save()


class ArchiveEquipmentBrandView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        brand_id,
    ):
        brand = EquipmentBrand.objects.filter(
            id=brand_id,
        ).first()

        if not brand:
            return Response(
                {
                    "detail": (
                        "Marca de equipo no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if brand.is_archived:
            return Response(
                {
                    "detail": (
                        "La marca ya se encuentra archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            ArchiveEquipmentBrandSerializer(
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

        brand.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Marca archivada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestoreEquipmentBrandView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        brand_id,
    ):
        brand = EquipmentBrand.objects.filter(
            id=brand_id,
        ).first()

        if not brand:
            return Response(
                {
                    "detail": (
                        "Marca de equipo no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not brand.is_archived:
            return Response(
                {
                    "detail": (
                        "La marca no se encuentra archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        brand.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Marca restaurada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )