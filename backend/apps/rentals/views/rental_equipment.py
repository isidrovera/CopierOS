# -*- coding: utf-8 -*-
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.rentals.models import RentalEquipment
from apps.rentals.serializers import (
    RentalEquipmentListSerializer,
    RentalEquipmentSerializer,
)


class RentalEquipmentViewSet(viewsets.ModelViewSet):
    """
    API para administrar la flota de alquiler de ANDES.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    queryset = RentalEquipment.objects.all()

    def get_queryset(self):
        queryset = (
            RentalEquipment.objects
            .select_related(
                "equipment",
                "equipment__equipment_model",
                "equipment__equipment_model__brand",
                "supplier",
                "owner_customer",
                "warehouse",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .order_by(
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
                    equipment__serial_number__icontains=search,
                )
                | Q(
                    equipment__internal_code__icontains=search,
                )
                | Q(
                    equipment__equipment_model__name__icontains=search,
                )
                | Q(
                    equipment__equipment_model__brand__name__icontains=search,
                )
                | Q(
                    acquisition_document__icontains=search,
                )
                | Q(
                    acquisition_reference__icontains=search,
                )
                | Q(
                    warehouse_location__icontains=search,
                )
                | Q(
                    notes__icontains=search,
                )
            )

        purpose = (
            self.request.query_params.get(
                "purpose",
                "",
            )
            .strip()
        )

        if purpose:
            queryset = queryset.filter(
                purpose=purpose,
            )

        acquisition_source = (
            self.request.query_params.get(
                "acquisition_source",
                "",
            )
            .strip()
        )

        if acquisition_source:
            queryset = queryset.filter(
                acquisition_source=acquisition_source,
            )

        operational_status = (
            self.request.query_params.get(
                "operational_status",
                "",
            )
            .strip()
        )

        if operational_status:
            queryset = queryset.filter(
                operational_status=operational_status,
            )

        warehouse_id = (
            self.request.query_params.get(
                "warehouse",
                "",
            )
            .strip()
        )

        if warehouse_id:
            queryset = queryset.filter(
                warehouse_id=warehouse_id,
            )

        supplier_id = (
            self.request.query_params.get(
                "supplier",
                "",
            )
            .strip()
        )

        if supplier_id:
            queryset = queryset.filter(
                supplier_id=supplier_id,
            )

        owner_customer_id = (
            self.request.query_params.get(
                "owner_customer",
                "",
            )
            .strip()
        )

        if owner_customer_id:
            queryset = queryset.filter(
                owner_customer_id=owner_customer_id,
            )

        available = (
            self.request.query_params.get(
                "is_available_for_rental",
                "",
            )
            .strip()
            .lower()
        )

        if available in [
            "1",
            "true",
            "yes",
            "si",
            "sí",
        ]:
            queryset = queryset.filter(
                is_available_for_rental=True,
            )

        elif available in [
            "0",
            "false",
            "no",
        ]:
            queryset = queryset.filter(
                is_available_for_rental=False,
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RentalEquipmentListSerializer

        return RentalEquipmentSerializer

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
        rental_equipment = self.get_object()

        if rental_equipment.archived_at:
            return Response(
                {
                    "detail": (
                        "El equipo ya se encuentra archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        active_assignments = rental_equipment.assignments.filter(
            archived_at__isnull=True,
            status__in=[
                "reserved",
                "installation_pending",
                "installed",
                "active",
                "removal_pending",
            ],
        ).exists()

        if active_assignments:
            return Response(
                {
                    "detail": (
                        "No se puede archivar el equipo porque "
                        "tiene una asignación activa."
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

        rental_equipment.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Equipo archivado correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="archive",
    )
    def archive_equipment(self, request, pk=None):
        rental_equipment = self.get_object()

        if rental_equipment.archived_at:
            return Response(
                {
                    "detail": (
                        "El equipo ya se encuentra archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        active_assignments = rental_equipment.assignments.filter(
            archived_at__isnull=True,
            status__in=[
                "reserved",
                "installation_pending",
                "installed",
                "active",
                "removal_pending",
            ],
        ).exists()

        if active_assignments:
            return Response(
                {
                    "detail": (
                        "No se puede archivar el equipo porque "
                        "tiene una asignación activa."
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

        rental_equipment.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Equipo archivado correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
    )
    def restore_equipment(self, request, pk=None):
        rental_equipment = (
            RentalEquipment.objects
            .filter(
                pk=pk,
            )
            .first()
        )

        if not rental_equipment:
            return Response(
                {
                    "detail": (
                        "Equipo no encontrado."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not rental_equipment.archived_at:
            return Response(
                {
                    "detail": (
                        "El equipo no se encuentra archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        rental_equipment.restore(
            user=request.user,
        )

        serializer = RentalEquipmentSerializer(
            rental_equipment,
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
        url_path="available",
    )
    def available_equipment(self, request):
        queryset = (
            self.get_queryset()
            .filter(
                purpose=RentalEquipment.EquipmentPurpose.RENTAL,
                operational_status=(
                    RentalEquipment
                    .OperationalStatus
                    .READY_FOR_RENTAL
                ),
                is_available_for_rental=True,
            )
            .order_by(
                "equipment__equipment_model__brand__name",
                "equipment__equipment_model__name",
                "equipment__serial_number",
            )
        )

        serializer = RentalEquipmentListSerializer(
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

    @action(
        detail=False,
        methods=["get"],
        url_path="fleet-summary",
    )
    def fleet_summary(self, request):
        queryset = RentalEquipment.objects.filter(
            archived_at__isnull=True,
            purpose=RentalEquipment.EquipmentPurpose.RENTAL,
        )

        summary = {
            "total": queryset.count(),
            "available": queryset.filter(
                is_available_for_rental=True,
            ).count(),
            "in_warehouse": queryset.filter(
                operational_status=(
                    RentalEquipment
                    .OperationalStatus
                    .IN_WAREHOUSE
                ),
            ).count(),
            "pending_preparation": queryset.filter(
                operational_status=(
                    RentalEquipment
                    .OperationalStatus
                    .PENDING_PREPARATION
                ),
            ).count(),
            "in_preparation": queryset.filter(
                operational_status=(
                    RentalEquipment
                    .OperationalStatus
                    .IN_PREPARATION
                ),
            ).count(),
            "ready_for_rental": queryset.filter(
                operational_status=(
                    RentalEquipment
                    .OperationalStatus
                    .READY_FOR_RENTAL
                ),
            ).count(),
            "reserved": queryset.filter(
                operational_status=(
                    RentalEquipment
                    .OperationalStatus
                    .RESERVED
                ),
            ).count(),
            "installation_pending": queryset.filter(
                operational_status=(
                    RentalEquipment
                    .OperationalStatus
                    .INSTALLATION_PENDING
                ),
            ).count(),
            "rented": queryset.filter(
                operational_status=(
                    RentalEquipment
                    .OperationalStatus
                    .RENTED
                ),
            ).count(),
            "removal_pending": queryset.filter(
                operational_status=(
                    RentalEquipment
                    .OperationalStatus
                    .REMOVAL_PENDING
                ),
            ).count(),
            "with_problems": queryset.filter(
                operational_status=(
                    RentalEquipment
                    .OperationalStatus
                    .WITH_PROBLEMS
                ),
            ).count(),
            "for_parts": queryset.filter(
                operational_status=(
                    RentalEquipment
                    .OperationalStatus
                    .FOR_PARTS
                ),
            ).count(),
            "out_of_service": queryset.filter(
                operational_status=(
                    RentalEquipment
                    .OperationalStatus
                    .OUT_OF_SERVICE
                ),
            ).count(),
        }

        return Response(
            summary,
            status=status.HTTP_200_OK,
        )