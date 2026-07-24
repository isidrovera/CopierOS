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

from ..models import EquipmentMovement
from ..serializers import (
    ArchiveEquipmentMovementSerializer,
    EquipmentMovementCreateUpdateSerializer,
    EquipmentMovementDetailSerializer,
    EquipmentMovementListSerializer,
)
from .equipment_type import parse_boolean_query_param


class EquipmentMovementListCreateView(
    ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            EquipmentMovement.objects
            .select_related(
                "equipment",
                "equipment__equipment_model",
                "equipment__equipment_model__brand",
                "responsible_user",
                "previous_customer",
                "new_customer",
                "previous_customer_branch",
                "new_customer_branch",
                "previous_owner",
                "new_owner",
                "previous_advisor",
                "new_advisor",
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
                    equipment__internal_code__icontains=search,
                )
                | Q(
                    equipment__serial_number__icontains=search,
                )
                | Q(
                    equipment__equipment_model__name__icontains=search,
                )
                | Q(
                    equipment__equipment_model__brand__name__icontains=search,
                )
                | Q(
                    previous_location__icontains=search,
                )
                | Q(
                    new_location__icontains=search,
                )
                | Q(
                    reference_number__icontains=search,
                )
                | Q(
                    document_number__icontains=search,
                )
                | Q(
                    reason__icontains=search,
                )
                | Q(
                    notes__icontains=search,
                )
                | Q(
                    previous_customer__legal_name__icontains=search,
                )
                | Q(
                    previous_customer__trade_name__icontains=search,
                )
                | Q(
                    new_customer__legal_name__icontains=search,
                )
                | Q(
                    new_customer__trade_name__icontains=search,
                )
            ).distinct()

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

        responsible_user_id = str(
            self.request.query_params.get(
                "responsible_user",
                "",
            )
        ).strip()

        if responsible_user_id:
            queryset = queryset.filter(
                responsible_user_id=responsible_user_id,
            )

        previous_customer_id = str(
            self.request.query_params.get(
                "previous_customer",
                "",
            )
        ).strip()

        if previous_customer_id:
            queryset = queryset.filter(
                previous_customer_id=previous_customer_id,
            )

        new_customer_id = str(
            self.request.query_params.get(
                "new_customer",
                "",
            )
        ).strip()

        if new_customer_id:
            queryset = queryset.filter(
                new_customer_id=new_customer_id,
            )

        previous_customer_branch_id = str(
            self.request.query_params.get(
                "previous_customer_branch",
                "",
            )
        ).strip()

        if previous_customer_branch_id:
            queryset = queryset.filter(
                previous_customer_branch_id=(
                    previous_customer_branch_id
                ),
            )

        new_customer_branch_id = str(
            self.request.query_params.get(
                "new_customer_branch",
                "",
            )
        ).strip()

        if new_customer_branch_id:
            queryset = queryset.filter(
                new_customer_branch_id=(
                    new_customer_branch_id
                ),
            )

        previous_technical_status = str(
            self.request.query_params.get(
                "previous_technical_status",
                "",
            )
        ).strip()

        if previous_technical_status:
            queryset = queryset.filter(
                previous_technical_status=(
                    previous_technical_status
                ),
            )

        new_technical_status = str(
            self.request.query_params.get(
                "new_technical_status",
                "",
            )
        ).strip()

        if new_technical_status:
            queryset = queryset.filter(
                new_technical_status=new_technical_status,
            )

        previous_commercial_status = str(
            self.request.query_params.get(
                "previous_commercial_status",
                "",
            )
        ).strip()

        if previous_commercial_status:
            queryset = queryset.filter(
                previous_commercial_status=(
                    previous_commercial_status
                ),
            )

        new_commercial_status = str(
            self.request.query_params.get(
                "new_commercial_status",
                "",
            )
        ).strip()

        if new_commercial_status:
            queryset = queryset.filter(
                new_commercial_status=new_commercial_status,
            )

        is_system_generated = parse_boolean_query_param(
            self.request.query_params.get(
                "is_system_generated"
            )
        )

        if is_system_generated is not None:
            queryset = queryset.filter(
                is_system_generated=is_system_generated,
            )

        occurred_from = str(
            self.request.query_params.get(
                "occurred_from",
                "",
            )
        ).strip()

        if occurred_from:
            queryset = queryset.filter(
                occurred_at__date__gte=occurred_from,
            )

        occurred_to = str(
            self.request.query_params.get(
                "occurred_to",
                "",
            )
        ).strip()

        if occurred_to:
            queryset = queryset.filter(
                occurred_at__date__lte=occurred_to,
            )

        return queryset.order_by(
            "-occurred_at",
            "-created_at",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return (
                EquipmentMovementCreateUpdateSerializer
            )

        return EquipmentMovementListSerializer

    @transaction.atomic
    def perform_create(
        self,
        serializer,
    ):
        serializer.save()


class EquipmentMovementDetailUpdateView(
    RetrieveUpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            EquipmentMovement.objects
            .select_related(
                "equipment",
                "equipment__equipment_model",
                "equipment__equipment_model__brand",
                "responsible_user",
                "previous_customer",
                "new_customer",
                "previous_customer_branch",
                "new_customer_branch",
                "previous_owner",
                "new_owner",
                "previous_advisor",
                "new_advisor",
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
                EquipmentMovementCreateUpdateSerializer
            )

        return EquipmentMovementDetailSerializer

    @transaction.atomic
    def perform_update(
        self,
        serializer,
    ):
        serializer.save()


class ArchiveEquipmentMovementView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        movement_id,
    ):
        movement = (
            EquipmentMovement.objects.filter(
                id=movement_id,
            )
            .first()
        )

        if not movement:
            return Response(
                {
                    "detail": (
                        "Movimiento de equipo no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if movement.is_archived:
            return Response(
                {
                    "detail": (
                        "El movimiento ya se encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            ArchiveEquipmentMovementSerializer(
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

        movement.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Movimiento archivado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestoreEquipmentMovementView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        movement_id,
    ):
        movement = (
            EquipmentMovement.objects.filter(
                id=movement_id,
            )
            .first()
        )

        if not movement:
            return Response(
                {
                    "detail": (
                        "Movimiento de equipo no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not movement.is_archived:
            return Response(
                {
                    "detail": (
                        "El movimiento no se encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        movement.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Movimiento restaurado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )