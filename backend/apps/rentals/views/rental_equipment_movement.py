# -*- coding: utf-8 -*-
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.rentals.models import RentalEquipmentMovement
from apps.rentals.serializers import (
    RentalEquipmentMovementListSerializer,
    RentalEquipmentMovementSerializer,
)


class RentalEquipmentMovementViewSet(viewsets.ModelViewSet):
    """
    API para consultar y registrar movimientos
    de los equipos de alquiler de ANDES.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    queryset = RentalEquipmentMovement.objects.all()

    def get_queryset(self):
        queryset = (
            RentalEquipmentMovement.objects
            .select_related(
                "rental_equipment",
                "rental_equipment__equipment",
                "rental_equipment__equipment__equipment_model",
                (
                    "rental_equipment__equipment__"
                    "equipment_model__brand"
                ),
                "source_warehouse",
                "destination_warehouse",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .order_by(
                "-occurred_at",
                "-created_at",
            )
        )

        include_archived = (
            self.request.query_params.get(
                "include_archived",
                "",
            )
            .strip()
            .lower()
            in [
                "1",
                "true",
                "yes",
                "si",
                "sí",
            ]
        )

        if not include_archived:
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        search = (
            self.request.query_params.get(
                "search",
                "",
            )
            .strip()
        )

        if search:
            queryset = queryset.filter(
                Q(
                    rental_equipment__equipment__
                    serial_number__icontains=search,
                )
                | Q(
                    rental_equipment__equipment__
                    internal_code__icontains=search,
                )
                | Q(
                    rental_equipment__equipment__
                    equipment_model__name__icontains=search,
                )
                | Q(
                    rental_equipment__equipment__
                    equipment_model__brand__
                    name__icontains=search,
                )
                | Q(
                    reference_number__icontains=search,
                )
                | Q(
                    document_number__icontains=search,
                )
                | Q(
                    source_location__icontains=search,
                )
                | Q(
                    destination_location__icontains=search,
                )
                | Q(
                    reason__icontains=search,
                )
                | Q(
                    notes__icontains=search,
                )
            )

        rental_equipment_id = (
            self.request.query_params.get(
                "rental_equipment",
                "",
            )
            .strip()
        )

        if rental_equipment_id:
            queryset = queryset.filter(
                rental_equipment_id=rental_equipment_id,
            )

        movement_type = (
            self.request.query_params.get(
                "movement_type",
                "",
            )
            .strip()
        )

        if movement_type:
            queryset = queryset.filter(
                movement_type=movement_type,
            )

        previous_status = (
            self.request.query_params.get(
                "previous_status",
                "",
            )
            .strip()
        )

        if previous_status:
            queryset = queryset.filter(
                previous_status=previous_status,
            )

        new_status = (
            self.request.query_params.get(
                "new_status",
                "",
            )
            .strip()
        )

        if new_status:
            queryset = queryset.filter(
                new_status=new_status,
            )

        source_warehouse_id = (
            self.request.query_params.get(
                "source_warehouse",
                "",
            )
            .strip()
        )

        if source_warehouse_id:
            queryset = queryset.filter(
                source_warehouse_id=source_warehouse_id,
            )

        destination_warehouse_id = (
            self.request.query_params.get(
                "destination_warehouse",
                "",
            )
            .strip()
        )

        if destination_warehouse_id:
            queryset = queryset.filter(
                destination_warehouse_id=(
                    destination_warehouse_id
                ),
            )

        reference_type = (
            self.request.query_params.get(
                "reference_type",
                "",
            )
            .strip()
        )

        if reference_type:
            queryset = queryset.filter(
                reference_type=reference_type,
            )

        occurred_from = (
            self.request.query_params.get(
                "occurred_from",
                "",
            )
            .strip()
        )

        if occurred_from:
            queryset = queryset.filter(
                occurred_at__date__gte=occurred_from,
            )

        occurred_to = (
            self.request.query_params.get(
                "occurred_to",
                "",
            )
            .strip()
        )

        if occurred_to:
            queryset = queryset.filter(
                occurred_at__date__lte=occurred_to,
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RentalEquipmentMovementListSerializer

        return RentalEquipmentMovementSerializer

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user,
        )

    def destroy(self, request, *args, **kwargs):
        movement = self.get_object()

        if movement.archived_at:
            return Response(
                {
                    "detail": (
                        "El movimiento ya se encuentra archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = (
            request.data.get(
                "reason",
                "",
            )
            .strip()
        )

        if not reason:
            return Response(
                {
                    "detail": (
                        "Debe indicar el motivo de archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        movement.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Movimiento archivado correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="archive",
    )
    def archive_movement(self, request, pk=None):
        movement = self.get_object()

        if movement.archived_at:
            return Response(
                {
                    "detail": (
                        "El movimiento ya se encuentra archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = (
            request.data.get(
                "reason",
                "",
            )
            .strip()
        )

        if not reason:
            return Response(
                {
                    "detail": (
                        "Debe indicar el motivo de archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        movement.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Movimiento archivado correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
    )
    def restore_movement(self, request, pk=None):
        movement = (
            RentalEquipmentMovement.objects
            .filter(
                pk=pk,
            )
            .first()
        )

        if not movement:
            return Response(
                {
                    "detail": (
                        "Movimiento no encontrado."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not movement.archived_at:
            return Response(
                {
                    "detail": (
                        "El movimiento no se encuentra archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        movement.restore(
            user=request.user,
        )

        serializer = RentalEquipmentMovementSerializer(
            movement,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="equipment-history",
    )
    def equipment_history(self, request):
        rental_equipment_id = (
            request.query_params.get(
                "rental_equipment",
                "",
            )
            .strip()
        )

        if not rental_equipment_id:
            return Response(
                {
                    "detail": (
                        "Debe indicar el equipo de alquiler."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = (
            self.get_queryset()
            .filter(
                rental_equipment_id=rental_equipment_id,
            )
            .order_by(
                "-occurred_at",
                "-created_at",
            )
        )

        serializer = RentalEquipmentMovementListSerializer(
            queryset,
            many=True,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )