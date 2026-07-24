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

from ..models import EquipmentType
from ..serializers import (
    ArchiveEquipmentTypeSerializer,
    EquipmentTypeCreateUpdateSerializer,
    EquipmentTypeDetailSerializer,
    EquipmentTypeListSerializer,
)


def parse_boolean_query_param(value):
    """
    Convierte un parámetro de consulta en booleano.

    Devuelve:

    - True.
    - False.
    - None cuando el valor no es reconocido.
    """

    if value is None:
        return None

    normalized = str(
        value
    ).strip().lower()

    if normalized in (
        "1",
        "true",
        "yes",
        "si",
        "sí",
    ):
        return True

    if normalized in (
        "0",
        "false",
        "no",
    ):
        return False

    return None


class EquipmentTypeListCreateView(
    ListCreateAPIView
):
    """
    Lista y crea tipos de equipos.

    GET:
        Lista los tipos de equipos no archivados
        de manera predeterminada.

    POST:
        Crea un nuevo tipo de equipo.

    Parámetros disponibles:

        ?search=<texto>
        ?is_active=true
        ?requires_meter=true
        ?requires_color_definition=true
        ?allows_accessories=true
        ?include_archived=true
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            EquipmentType.objects
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

        is_active = parse_boolean_query_param(
            self.request.query_params.get(
                "is_active"
            )
        )

        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active,
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

        requires_color_definition = (
            parse_boolean_query_param(
                self.request.query_params.get(
                    "requires_color_definition"
                )
            )
        )

        if requires_color_definition is not None:
            queryset = queryset.filter(
                requires_color_definition=(
                    requires_color_definition
                ),
            )

        allows_accessories = (
            parse_boolean_query_param(
                self.request.query_params.get(
                    "allows_accessories"
                )
            )
        )

        if allows_accessories is not None:
            queryset = queryset.filter(
                allows_accessories=allows_accessories,
            )

        return queryset.order_by(
            "display_order",
            "name",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return (
                EquipmentTypeCreateUpdateSerializer
            )

        return EquipmentTypeListSerializer

    @transaction.atomic
    def perform_create(
        self,
        serializer,
    ):
        serializer.save()


class EquipmentTypeDetailUpdateView(
    RetrieveUpdateAPIView
):
    """
    Consulta y modifica un tipo de equipo.

    GET:
        Devuelve el detalle completo.

    PUT/PATCH:
        Modifica el tipo de equipo.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            EquipmentType.objects
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
                EquipmentTypeCreateUpdateSerializer
            )

        return EquipmentTypeDetailSerializer

    @transaction.atomic
    def perform_update(
        self,
        serializer,
    ):
        serializer.save()


class ArchiveEquipmentTypeView(APIView):
    """
    Archiva un tipo de equipo sin eliminarlo físicamente.

    Al archivarlo también queda inactivo.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        equipment_type_id,
    ):
        equipment_type = (
            EquipmentType.objects.filter(
                id=equipment_type_id,
            )
            .first()
        )

        if not equipment_type:
            return Response(
                {
                    "detail": (
                        "Tipo de equipo no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if equipment_type.is_archived:
            return Response(
                {
                    "detail": (
                        "El tipo de equipo ya se encuentra "
                        "archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            ArchiveEquipmentTypeSerializer(
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

        equipment_type.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Tipo de equipo archivado "
                    "correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestoreEquipmentTypeView(APIView):
    """
    Restaura un tipo de equipo archivado.

    Al restaurarlo también vuelve a quedar activo.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        equipment_type_id,
    ):
        equipment_type = (
            EquipmentType.objects.filter(
                id=equipment_type_id,
            )
            .first()
        )

        if not equipment_type:
            return Response(
                {
                    "detail": (
                        "Tipo de equipo no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not equipment_type.is_archived:
            return Response(
                {
                    "detail": (
                        "El tipo de equipo no se encuentra "
                        "archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        equipment_type.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Tipo de equipo restaurado "
                    "correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )