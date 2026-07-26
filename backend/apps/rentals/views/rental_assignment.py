# -*- coding: utf-8 -*-
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.rentals.models import RentalAssignment
from apps.rentals.serializers import (
    RentalAssignmentListSerializer,
    RentalAssignmentSerializer,
)


class RentalAssignmentViewSet(viewsets.ModelViewSet):
    """
    API para administrar asignaciones de equipos
    de alquiler a clientes y sedes.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    queryset = RentalAssignment.objects.all()

    def get_queryset(self):
        queryset = (
            RentalAssignment.objects
            .select_related(
                "rental_equipment",
                "rental_equipment__equipment",
                "rental_equipment__equipment__equipment_model",
                (
                    "rental_equipment__equipment__"
                    "equipment_model__brand"
                ),
                "customer",
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
                Q(code__icontains=search)
                | Q(customer__legal_name__icontains=search)
                | Q(customer__trade_name__icontains=search)
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
                | Q(site_location__icontains=search)
                | Q(installation_notes__icontains=search)
                | Q(removal_reason__icontains=search)
                | Q(notes__icontains=search)
            ).distinct()

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

        customer_id = (
            self.request.query_params.get(
                "customer",
                "",
            )
            .strip()
        )

        if customer_id:
            queryset = queryset.filter(
                customer_id=customer_id,
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

        assignment_status = (
            self.request.query_params.get(
                "status",
                "",
            )
            .strip()
        )

        if assignment_status:
            queryset = queryset.filter(
                status=assignment_status,
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
            return RentalAssignmentListSerializer

        return RentalAssignmentSerializer

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
        assignment = self.get_object()

        if assignment.archived_at:
            return Response(
                {
                    "detail": (
                        "La asignación ya se encuentra archivada."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if assignment.status in [
            RentalAssignment.Status.INSTALLED,
            RentalAssignment.Status.ACTIVE,
            RentalAssignment.Status.REMOVAL_PENDING,
        ]:
            return Response(
                {
                    "detail": (
                        "No se puede archivar una asignación "
                        "instalada, activa o pendiente de retiro."
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

        assignment.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Asignación archivada correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="archive",
    )
    def archive_assignment(self, request, pk=None):
        assignment = self.get_object()

        if assignment.archived_at:
            return Response(
                {
                    "detail": (
                        "La asignación ya se encuentra archivada."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if assignment.status in [
            RentalAssignment.Status.INSTALLED,
            RentalAssignment.Status.ACTIVE,
            RentalAssignment.Status.REMOVAL_PENDING,
        ]:
            return Response(
                {
                    "detail": (
                        "No se puede archivar una asignación "
                        "instalada, activa o pendiente de retiro."
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

        assignment.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Asignación archivada correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
    )
    def restore_assignment(self, request, pk=None):
        assignment = (
            RentalAssignment.objects
            .filter(
                pk=pk,
            )
            .first()
        )

        if not assignment:
            return Response(
                {
                    "detail": (
                        "Asignación no encontrada."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not assignment.archived_at:
            return Response(
                {
                    "detail": (
                        "La asignación no se encuentra archivada."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        assignment.restore(
            user=request.user,
        )

        serializer = RentalAssignmentSerializer(
            assignment,
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
    def active_assignments(self, request):
        queryset = (
            self.get_queryset()
            .filter(
                status__in=[
                    RentalAssignment.Status.RESERVED,
                    RentalAssignment.Status.INSTALLATION_PENDING,
                    RentalAssignment.Status.INSTALLED,
                    RentalAssignment.Status.ACTIVE,
                    RentalAssignment.Status.REMOVAL_PENDING,
                ],
            )
            .order_by(
                "scheduled_installation_date",
                "-assigned_at",
            )
        )

        serializer = RentalAssignmentListSerializer(
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
        url_path="customer-equipment",
    )
    def customer_equipment(self, request):
        customer_id = (
            request.query_params.get(
                "customer",
                "",
            )
            .strip()
        )

        if not customer_id:
            return Response(
                {
                    "detail": (
                        "Debe indicar el cliente."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = (
            self.get_queryset()
            .filter(
                customer_id=customer_id,
            )
            .order_by(
                "-assigned_at",
                "-created_at",
            )
        )

        serializer = RentalAssignmentListSerializer(
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

        serializer = RentalAssignmentListSerializer(
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