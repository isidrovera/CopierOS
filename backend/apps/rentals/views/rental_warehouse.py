# -*- coding: utf-8 -*-
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.rentals.models import RentalWarehouse
from apps.rentals.serializers import (
    RentalWarehouseListSerializer,
    RentalWarehouseSerializer,
)


class RentalWarehouseViewSet(viewsets.ModelViewSet):
    """
    API para administrar los almacenes de alquiler de ANDES.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    queryset = RentalWarehouse.objects.all()

    def get_queryset(self):
        queryset = (
            RentalWarehouse.objects
            .select_related(
                "created_by",
                "updated_by",
                "archived_by",
            )
            .order_by(
                "display_order",
                "name",
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
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(address__icontains=search)
                | Q(description__icontains=search)
            )

        is_active = (
            self.request.query_params.get(
                "is_active",
                "",
            )
            .strip()
            .lower()
        )

        if is_active in [
            "1",
            "true",
            "yes",
            "si",
            "sí",
        ]:
            queryset = queryset.filter(
                is_active=True,
            )

        elif is_active in [
            "0",
            "false",
            "no",
        ]:
            queryset = queryset.filter(
                is_active=False,
            )

        allows_entries = (
            self.request.query_params.get(
                "allows_entries",
                "",
            )
            .strip()
            .lower()
        )

        if allows_entries in [
            "1",
            "true",
            "yes",
            "si",
            "sí",
        ]:
            queryset = queryset.filter(
                allows_entries=True,
            )

        elif allows_entries in [
            "0",
            "false",
            "no",
        ]:
            queryset = queryset.filter(
                allows_entries=False,
            )

        allows_dispatches = (
            self.request.query_params.get(
                "allows_dispatches",
                "",
            )
            .strip()
            .lower()
        )

        if allows_dispatches in [
            "1",
            "true",
            "yes",
            "si",
            "sí",
        ]:
            queryset = queryset.filter(
                allows_dispatches=True,
            )

        elif allows_dispatches in [
            "0",
            "false",
            "no",
        ]:
            queryset = queryset.filter(
                allows_dispatches=False,
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RentalWarehouseListSerializer

        return RentalWarehouseSerializer

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
        warehouse = self.get_object()

        if warehouse.archived_at:
            return Response(
                {
                    "detail": (
                        "El almacén ya se encuentra archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        active_equipment = warehouse.equipment.filter(
            archived_at__isnull=True,
        ).exists()

        if active_equipment:
            return Response(
                {
                    "detail": (
                        "No se puede archivar el almacén porque "
                        "tiene equipos asociados."
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

        warehouse.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Almacén archivado correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="archive",
    )
    def archive_warehouse(self, request, pk=None):
        warehouse = self.get_object()

        if warehouse.archived_at:
            return Response(
                {
                    "detail": (
                        "El almacén ya se encuentra archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        active_equipment = warehouse.equipment.filter(
            archived_at__isnull=True,
        ).exists()

        if active_equipment:
            return Response(
                {
                    "detail": (
                        "No se puede archivar el almacén porque "
                        "tiene equipos asociados."
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

        warehouse.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Almacén archivado correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
    )
    def restore_warehouse(self, request, pk=None):
        warehouse = (
            RentalWarehouse.objects
            .filter(
                pk=pk,
            )
            .first()
        )

        if not warehouse:
            return Response(
                {
                    "detail": (
                        "Almacén no encontrado."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not warehouse.archived_at:
            return Response(
                {
                    "detail": (
                        "El almacén no se encuentra archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        warehouse.restore(
            user=request.user,
        )

        serializer = RentalWarehouseSerializer(
            warehouse,
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
        url_path="active",
    )
    def active_warehouses(self, request):
        queryset = (
            RentalWarehouse.objects
            .filter(
                archived_at__isnull=True,
                is_active=True,
            )
            .order_by(
                "display_order",
                "name",
            )
        )

        serializer = RentalWarehouseListSerializer(
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