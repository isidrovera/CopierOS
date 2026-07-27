# -*- coding: utf-8 -*-
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.rentals.models import (
    RentalAssignment,
    RentalContract,
)
from apps.rentals.serializers import (
    RentalContractListSerializer,
    RentalContractSerializer,
)


class RentalContractViewSet(viewsets.ModelViewSet):
    """
    API para administrar contratos de alquiler.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    queryset = RentalContract.objects.all()

    def get_queryset(self):
        queryset = (
            RentalContract.objects
            .select_related(
                "customer",
                "main_branch",
                "main_contact",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .prefetch_related(
                "assignments",
            )
            .order_by(
                "-created_at",
            )
        )

        include_archived = (
            str(
                self.request.query_params.get(
                    "include_archived",
                    "",
                )
                or ""
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

        search = str(
            self.request.query_params.get(
                "search",
                "",
            )
            or ""
        ).strip()

        if search:
            queryset = queryset.filter(
                Q(code__icontains=search)
                | Q(contract_number__icontains=search)
                | Q(customer__legal_name__icontains=search)
                | Q(customer__trade_name__icontains=search)
                | Q(external_reference__icontains=search)
                | Q(service_conditions__icontains=search)
                | Q(customer_requirements__icontains=search)
                | Q(notes__icontains=search)
            ).distinct()

        customer_id = str(
            self.request.query_params.get(
                "customer",
                "",
            )
            or ""
        ).strip()

        if customer_id:
            queryset = queryset.filter(
                customer_id=customer_id,
            )

        main_branch_id = str(
            self.request.query_params.get(
                "main_branch",
                "",
            )
            or ""
        ).strip()

        if main_branch_id:
            queryset = queryset.filter(
                main_branch_id=main_branch_id,
            )

        contract_type = str(
            self.request.query_params.get(
                "contract_type",
                "",
            )
            or ""
        ).strip()

        if contract_type:
            queryset = queryset.filter(
                contract_type=contract_type,
            )

        contract_status = str(
            self.request.query_params.get(
                "status",
                "",
            )
            or ""
        ).strip()

        if contract_status:
            queryset = queryset.filter(
                status=contract_status,
            )

        start_date_from = str(
            self.request.query_params.get(
                "start_date_from",
                "",
            )
            or ""
        ).strip()

        if start_date_from:
            queryset = queryset.filter(
                start_date__gte=start_date_from,
            )

        start_date_to = str(
            self.request.query_params.get(
                "start_date_to",
                "",
            )
            or ""
        ).strip()

        if start_date_to:
            queryset = queryset.filter(
                start_date__lte=start_date_to,
            )

        end_date_from = str(
            self.request.query_params.get(
                "end_date_from",
                "",
            )
            or ""
        ).strip()

        if end_date_from:
            queryset = queryset.filter(
                end_date__gte=end_date_from,
            )

        end_date_to = str(
            self.request.query_params.get(
                "end_date_to",
                "",
            )
            or ""
        ).strip()

        if end_date_to:
            queryset = queryset.filter(
                end_date__lte=end_date_to,
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RentalContractListSerializer

        return RentalContractSerializer

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
        contract = self.get_object()

        if contract.archived_at:
            return Response(
                {
                    "detail": (
                        "El contrato ya se encuentra archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        active_assignments = contract.assignments.filter(
            archived_at__isnull=True,
            status__in=[
                RentalAssignment.Status.RESERVED,
                RentalAssignment.Status.INSTALLATION_PENDING,
                RentalAssignment.Status.INSTALLED,
                RentalAssignment.Status.ACTIVE,
                RentalAssignment.Status.REMOVAL_PENDING,
            ],
        ).exists()

        if active_assignments:
            return Response(
                {
                    "detail": (
                        "No se puede archivar el contrato porque "
                        "tiene equipos asignados activos."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = str(
            request.data.get(
                "reason",
                "",
            )
            or ""
        ).strip()

        if not reason:
            return Response(
                {
                    "detail": (
                        "Debe indicar el motivo de archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        contract.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Contrato archivado correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="archive",
    )
    def archive_contract(self, request, pk=None):
        return self.destroy(
            request,
            pk=pk,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
    )
    def restore_contract(self, request, pk=None):
        contract = (
            RentalContract.objects
            .filter(
                pk=pk,
            )
            .first()
        )

        if not contract:
            return Response(
                {
                    "detail": (
                        "Contrato no encontrado."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not contract.archived_at:
            return Response(
                {
                    "detail": (
                        "El contrato no se encuentra archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        contract.restore(
            user=request.user,
        )

        serializer = RentalContractSerializer(
            contract,
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
    def active_contracts(self, request):
        queryset = (
            self.get_queryset()
            .filter(
                status=RentalContract.Status.ACTIVE,
            )
            .order_by(
                "customer",
                "start_date",
            )
        )

        serializer = RentalContractListSerializer(
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
        url_path="expiring",
    )
    def expiring_contracts(self, request):
        days_value = str(
            request.query_params.get(
                "days",
                "30",
            )
            or "30"
        ).strip()

        try:
            days = int(days_value)
        except (TypeError, ValueError):
            return Response(
                {
                    "detail": (
                        "El número de días debe ser válido."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if days < 1:
            return Response(
                {
                    "detail": (
                        "El número de días debe ser mayor que cero."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = timezone.localdate()
        limit_date = today + timedelta(
            days=days,
        )

        queryset = (
            self.get_queryset()
            .filter(
                status=RentalContract.Status.ACTIVE,
                end_date__isnull=False,
                end_date__gte=today,
                end_date__lte=limit_date,
            )
            .order_by(
                "end_date",
            )
        )

        serializer = RentalContractListSerializer(
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
        detail=True,
        methods=["get"],
        url_path="assignments",
    )
    def contract_assignments(self, request, pk=None):
        contract = self.get_object()

        assignments = (
            contract.assignments
            .filter(
                archived_at__isnull=True,
            )
            .select_related(
                "rental_equipment",
                "rental_equipment__equipment",
                "customer",
                "branch",
                "contact",
            )
            .order_by(
                "-assigned_at",
                "-created_at",
            )
        )

        from apps.rentals.serializers import (
            RentalAssignmentListSerializer,
        )

        serializer = RentalAssignmentListSerializer(
            assignments,
            many=True,
            context={
                "request": request,
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )