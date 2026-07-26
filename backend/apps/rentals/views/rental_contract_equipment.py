# -*- coding: utf-8 -*-
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.rentals.models import RentalContractEquipment
from apps.rentals.serializers import (
    RentalContractEquipmentListSerializer,
    RentalContractEquipmentSerializer,
)


class RentalContractEquipmentViewSet(viewsets.ModelViewSet):
    """
    API para administrar los equipos vinculados
    a contratos de alquiler.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    queryset = RentalContractEquipment.objects.all()

    def get_queryset(self):
        queryset = (
            RentalContractEquipment.objects
            .select_related(
                "contract",
                "contract__customer",
                "rental_equipment",
                "rental_equipment__equipment",
                "rental_equipment__equipment__equipment_model",
                (
                    "rental_equipment__equipment__"
                    "equipment_model__brand"
                ),
                "branch",
                "contact",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .order_by(
                "-assigned_at",
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
                Q(contract__code__icontains=search)
                | Q(
                    contract__contract_number__icontains=search,
                )
                | Q(
                    contract__customer__legal_name__icontains=search,
                )
                | Q(
                    contract__customer__trade_name__icontains=search,
                )
                | Q(
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
                    site_location__icontains=search,
                )
                | Q(
                    installation_notes__icontains=search,
                )
                | Q(
                    removal_reason__icontains=search,
                )
                | Q(
                    notes__icontains=search,
                )
            ).distinct()

        contract_id = (
            self.request.query_params.get(
                "contract",
                "",
            )
            .strip()
        )

        if contract_id:
            queryset = queryset.filter(
                contract_id=contract_id,
            )

        customer_id = (
            self.request.query_params.get(
                "customer",
                "",
            )
            .strip()
        )

        if customer_id:
            queryset = queryset.filter(
                contract__customer_id=customer_id,
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

        branch_id = (
            self.request.query_params.get(
                "branch",
                "",
            )
            .strip()
        )

        if branch_id:
            queryset = queryset.filter(
                branch_id=branch_id,
            )

        contact_id = (
            self.request.query_params.get(
                "contact",
                "",
            )
            .strip()
        )

        if contact_id:
            queryset = queryset.filter(
                contact_id=contact_id,
            )

        relation_status = (
            self.request.query_params.get(
                "status",
                "",
            )
            .strip()
        )

        if relation_status:
            queryset = queryset.filter(
                status=relation_status,
            )

        assigned_from = (
            self.request.query_params.get(
                "assigned_from",
                "",
            )
            .strip()
        )

        if assigned_from:
            queryset = queryset.filter(
                assigned_at__date__gte=assigned_from,
            )

        assigned_to = (
            self.request.query_params.get(
                "assigned_to",
                "",
            )
            .strip()
        )

        if assigned_to:
            queryset = queryset.filter(
                assigned_at__date__lte=assigned_to,
            )

        installation_from = (
            self.request.query_params.get(
                "installation_from",
                "",
            )
            .strip()
        )

        if installation_from:
            queryset = queryset.filter(
                scheduled_installation_date__gte=(
                    installation_from
                ),
            )

        installation_to = (
            self.request.query_params.get(
                "installation_to",
                "",
            )
            .strip()
        )

        if installation_to:
            queryset = queryset.filter(
                scheduled_installation_date__lte=(
                    installation_to
                ),
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RentalContractEquipmentListSerializer

        return RentalContractEquipmentSerializer

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
        contract_equipment = self.get_object()

        if contract_equipment.archived_at:
            return Response(
                {
                    "detail": (
                        "La relación ya se encuentra archivada."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if contract_equipment.status in [
            RentalContractEquipment.Status.INSTALLED,
            RentalContractEquipment.Status.ACTIVE,
            RentalContractEquipment.Status.REMOVAL_PENDING,
        ]:
            return Response(
                {
                    "detail": (
                        "No se puede archivar un equipo instalado, "
                        "activo o pendiente de retiro."
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

        contract_equipment.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Equipo del contrato archivado correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="archive",
    )
    def archive_contract_equipment(self, request, pk=None):
        contract_equipment = self.get_object()

        if contract_equipment.archived_at:
            return Response(
                {
                    "detail": (
                        "La relación ya se encuentra archivada."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if contract_equipment.status in [
            RentalContractEquipment.Status.INSTALLED,
            RentalContractEquipment.Status.ACTIVE,
            RentalContractEquipment.Status.REMOVAL_PENDING,
        ]:
            return Response(
                {
                    "detail": (
                        "No se puede archivar un equipo instalado, "
                        "activo o pendiente de retiro."
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

        contract_equipment.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Equipo del contrato archivado correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
    )
    def restore_contract_equipment(self, request, pk=None):
        contract_equipment = (
            RentalContractEquipment.objects
            .filter(
                pk=pk,
            )
            .first()
        )

        if not contract_equipment:
            return Response(
                {
                    "detail": (
                        "Equipo del contrato no encontrado."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not contract_equipment.archived_at:
            return Response(
                {
                    "detail": (
                        "La relación no se encuentra archivada."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        contract_equipment.restore(
            user=request.user,
        )

        serializer = RentalContractEquipmentSerializer(
            contract_equipment,
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
    def active_contract_equipment(self, request):
        queryset = (
            self.get_queryset()
            .filter(
                status__in=[
                    RentalContractEquipment.Status.RESERVED,
                    (
                        RentalContractEquipment
                        .Status
                        .INSTALLATION_PENDING
                    ),
                    RentalContractEquipment.Status.INSTALLED,
                    RentalContractEquipment.Status.ACTIVE,
                    (
                        RentalContractEquipment
                        .Status
                        .REMOVAL_PENDING
                    ),
                ],
            )
            .order_by(
                "scheduled_installation_date",
                "-assigned_at",
            )
        )

        serializer = RentalContractEquipmentListSerializer(
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
        url_path="contract-history",
    )
    def contract_history(self, request):
        contract_id = (
            request.query_params.get(
                "contract",
                "",
            )
            .strip()
        )

        if not contract_id:
            return Response(
                {
                    "detail": (
                        "Debe indicar el contrato."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = (
            self.get_queryset()
            .filter(
                contract_id=contract_id,
            )
            .order_by(
                "-assigned_at",
                "-created_at",
            )
        )

        serializer = RentalContractEquipmentListSerializer(
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
                "-assigned_at",
                "-created_at",
            )
        )

        serializer = RentalContractEquipmentListSerializer(
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