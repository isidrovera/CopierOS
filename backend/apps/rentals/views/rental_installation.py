# -*- coding: utf-8 -*-
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.rentals.models import RentalInstallation
from apps.rentals.serializers import (
    RentalInstallationListSerializer,
    RentalInstallationSerializer,
)


class RentalInstallationViewSet(viewsets.ModelViewSet):
    """
    API para administrar instalaciones de equipos alquilados.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    queryset = RentalInstallation.objects.all()

    def get_queryset(self):
        queryset = (
            RentalInstallation.objects
            .select_related(
                "rental_assignment",
                "rental_assignment__rental_equipment",
                "rental_assignment__rental_equipment__equipment",
                (
                    "rental_assignment__rental_equipment__"
                    "equipment__equipment_model"
                ),
                (
                    "rental_assignment__rental_equipment__"
                    "equipment__equipment_model__brand"
                ),
                "rental_assignment__customer",
                "rental_assignment__branch",
                "rental_assignment__contact",
                "assigned_technician",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .order_by(
                "-requested_at",
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
                | Q(
                    rental_assignment__code__icontains=search,
                )
                | Q(
                    rental_assignment__customer__
                    legal_name__icontains=search,
                )
                | Q(
                    rental_assignment__customer__
                    trade_name__icontains=search,
                )
                | Q(
                    rental_assignment__rental_equipment__
                    equipment__serial_number__icontains=search,
                )
                | Q(
                    rental_assignment__rental_equipment__
                    equipment__internal_code__icontains=search,
                )
                | Q(
                    rental_assignment__rental_equipment__
                    equipment__equipment_model__
                    name__icontains=search,
                )
                | Q(
                    rental_assignment__rental_equipment__
                    equipment__equipment_model__brand__
                    name__icontains=search,
                )
                | Q(site_location__icontains=search)
                | Q(ip_address__icontains=search)
                | Q(hostname__icontains=search)
                | Q(
                    customer_representative_name__icontains=search,
                )
                | Q(
                    technical_observations__icontains=search,
                )
                | Q(
                    customer_observations__icontains=search,
                )
            ).distinct()

        rental_assignment_id = (
            self.request.query_params.get(
                "rental_assignment",
                "",
            )
            .strip()
        )

        if rental_assignment_id:
            queryset = queryset.filter(
                rental_assignment_id=rental_assignment_id,
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
                rental_assignment__rental_equipment_id=(
                    rental_equipment_id
                ),
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
                rental_assignment__customer_id=customer_id,
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
                rental_assignment__branch_id=branch_id,
            )

        technician_id = (
            self.request.query_params.get(
                "assigned_technician",
                "",
            )
            .strip()
        )

        if technician_id:
            queryset = queryset.filter(
                assigned_technician_id=technician_id,
            )

        installation_status = (
            self.request.query_params.get(
                "status",
                "",
            )
            .strip()
        )

        if installation_status:
            queryset = queryset.filter(
                status=installation_status,
            )

        result = (
            self.request.query_params.get(
                "result",
                "",
            )
            .strip()
        )

        if result:
            queryset = queryset.filter(
                result=result,
            )

        scheduled_from = (
            self.request.query_params.get(
                "scheduled_from",
                "",
            )
            .strip()
        )

        if scheduled_from:
            queryset = queryset.filter(
                scheduled_at__date__gte=scheduled_from,
            )

        scheduled_to = (
            self.request.query_params.get(
                "scheduled_to",
                "",
            )
            .strip()
        )

        if scheduled_to:
            queryset = queryset.filter(
                scheduled_at__date__lte=scheduled_to,
            )

        completed_from = (
            self.request.query_params.get(
                "completed_from",
                "",
            )
            .strip()
        )

        if completed_from:
            queryset = queryset.filter(
                completed_at__date__gte=completed_from,
            )

        completed_to = (
            self.request.query_params.get(
                "completed_to",
                "",
            )
            .strip()
        )

        if completed_to:
            queryset = queryset.filter(
                completed_at__date__lte=completed_to,
            )

        customer_conformity = (
            self.request.query_params.get(
                "customer_conformity",
                "",
            )
            .strip()
            .lower()
        )

        if customer_conformity in [
            "1",
            "true",
            "yes",
            "si",
            "sí",
        ]:
            queryset = queryset.filter(
                customer_conformity=True,
            )

        elif customer_conformity in [
            "0",
            "false",
            "no",
        ]:
            queryset = queryset.filter(
                customer_conformity=False,
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RentalInstallationListSerializer

        return RentalInstallationSerializer

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
        installation = self.get_object()

        if installation.archived_at:
            return Response(
                {
                    "detail": (
                        "La instalación ya se encuentra archivada."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if installation.status in [
            RentalInstallation.Status.IN_TRANSIT,
            RentalInstallation.Status.IN_PROGRESS,
        ]:
            return Response(
                {
                    "detail": (
                        "No se puede archivar una instalación "
                        "que se encuentra en proceso."
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

        installation.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Instalación archivada correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="archive",
    )
    def archive_installation(self, request, pk=None):
        installation = self.get_object()

        if installation.archived_at:
            return Response(
                {
                    "detail": (
                        "La instalación ya se encuentra archivada."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if installation.status in [
            RentalInstallation.Status.IN_TRANSIT,
            RentalInstallation.Status.IN_PROGRESS,
        ]:
            return Response(
                {
                    "detail": (
                        "No se puede archivar una instalación "
                        "que se encuentra en proceso."
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

        installation.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Instalación archivada correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
    )
    def restore_installation(self, request, pk=None):
        installation = (
            RentalInstallation.objects
            .filter(
                pk=pk,
            )
            .first()
        )

        if not installation:
            return Response(
                {
                    "detail": (
                        "Instalación no encontrada."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not installation.archived_at:
            return Response(
                {
                    "detail": (
                        "La instalación no se encuentra archivada."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        installation.restore(
            user=request.user,
        )

        serializer = RentalInstallationSerializer(
            installation,
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
    def active_installations(self, request):
        queryset = (
            self.get_queryset()
            .filter(
                status__in=[
                    RentalInstallation.Status.SCHEDULED,
                    RentalInstallation.Status.ASSIGNED,
                    RentalInstallation.Status.IN_TRANSIT,
                    RentalInstallation.Status.IN_PROGRESS,
                    RentalInstallation.Status.OBSERVED,
                ],
            )
            .order_by(
                "scheduled_at",
                "requested_at",
            )
        )

        serializer = RentalInstallationListSerializer(
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
        url_path="assignment-history",
    )
    def assignment_history(self, request):
        rental_assignment_id = (
            request.query_params.get(
                "rental_assignment",
                "",
            )
            .strip()
        )

        if not rental_assignment_id:
            return Response(
                {
                    "detail": (
                        "Debe indicar la asignación de alquiler."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = (
            self.get_queryset()
            .filter(
                rental_assignment_id=rental_assignment_id,
            )
            .order_by(
                "-requested_at",
                "-created_at",
            )
        )

        serializer = RentalInstallationListSerializer(
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
        url_path="technician-schedule",
    )
    def technician_schedule(self, request):
        technician_id = (
            request.query_params.get(
                "assigned_technician",
                "",
            )
            .strip()
        )

        if not technician_id:
            return Response(
                {
                    "detail": (
                        "Debe indicar el técnico."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = (
            self.get_queryset()
            .filter(
                assigned_technician_id=technician_id,
                status__in=[
                    RentalInstallation.Status.SCHEDULED,
                    RentalInstallation.Status.ASSIGNED,
                    RentalInstallation.Status.IN_TRANSIT,
                    RentalInstallation.Status.IN_PROGRESS,
                    RentalInstallation.Status.OBSERVED,
                ],
            )
            .order_by(
                "scheduled_at",
                "requested_at",
            )
        )

        serializer = RentalInstallationListSerializer(
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