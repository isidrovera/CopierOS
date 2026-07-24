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

from ..models import EquipmentFamily
from ..serializers import (
    ArchiveEquipmentFamilySerializer,
    EquipmentFamilyCreateUpdateSerializer,
    EquipmentFamilyDetailSerializer,
    EquipmentFamilyListSerializer,
)
from .equipment_type import parse_boolean_query_param


class EquipmentFamilyListCreateView(
    ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            EquipmentFamily.objects
            .select_related(
                "brand",
                "equipment_type",
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
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(technical_notes__icontains=search)
                | Q(brand__name__icontains=search)
                | Q(equipment_type__name__icontains=search)
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
            "brand__name",
            "display_order",
            "name",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return EquipmentFamilyCreateUpdateSerializer

        return EquipmentFamilyListSerializer

    @transaction.atomic
    def perform_create(
        self,
        serializer,
    ):
        serializer.save()


class EquipmentFamilyDetailUpdateView(
    RetrieveUpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            EquipmentFamily.objects
            .select_related(
                "brand",
                "equipment_type",
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
            return EquipmentFamilyCreateUpdateSerializer

        return EquipmentFamilyDetailSerializer

    @transaction.atomic
    def perform_update(
        self,
        serializer,
    ):
        serializer.save()


class ArchiveEquipmentFamilyView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        equipment_family_id,
    ):
        equipment_family = (
            EquipmentFamily.objects.filter(
                id=equipment_family_id,
            )
            .first()
        )

        if not equipment_family:
            return Response(
                {
                    "detail": (
                        "Familia de equipos no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if equipment_family.is_archived:
            return Response(
                {
                    "detail": (
                        "La familia ya se encuentra archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ArchiveEquipmentFamilySerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        equipment_family.archive(
            user=request.user,
            reason=serializer.validated_data.get(
                "reason",
                "",
            ),
        )

        return Response(
            {
                "detail": (
                    "Familia archivada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestoreEquipmentFamilyView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        equipment_family_id,
    ):
        equipment_family = (
            EquipmentFamily.objects.filter(
                id=equipment_family_id,
            )
            .first()
        )

        if not equipment_family:
            return Response(
                {
                    "detail": (
                        "Familia de equipos no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not equipment_family.is_archived:
            return Response(
                {
                    "detail": (
                        "La familia no se encuentra archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        equipment_family.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Familia restaurada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )