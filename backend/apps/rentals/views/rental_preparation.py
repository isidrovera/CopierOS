# -*- coding: utf-8 -*-
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.rentals.models import RentalPreparation
from apps.rentals.serializers import (
    RentalPreparationListSerializer,
    RentalPreparationSerializer,
)


class RentalPreparationViewSet(viewsets.ModelViewSet):
    """
    API para administrar la preparación de equipos
    antes de ser entregados en alquiler.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    queryset = RentalPreparation.objects.all()

    def get_queryset(self):
        queryset = (
            RentalPreparation.objects
            .select_related(
                "rental_equipment",
                "rental_equipment__equipment",
                "rental_equipment__equipment__equipment_model",
                "rental_equipment__equipment__equipment_model__brand",
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
                | Q(
                    rental_equipment__equipment__serial_number__icontains=search
                )
                | Q(
                    rental_equipment__equipment__internal_code__icontains=search
                )
                | Q(
                    rental_equipment__equipment__equipment_model__name__icontains=search
                )
                | Q(
                    rental_equipment__equipment__equipment_model__brand__name__icontains=search
                )
                | Q(request_reason__icontains=search)
                | Q(technical_observations__icontains=search)
                | Q(completion_notes__icontains=search)
            )

        rental_equipment_id = str(
            self.request.query_params.get(
                "rental_equipment",
                "",
            )
            or ""
        ).strip()

        if rental_equipment_id:
            queryset = queryset.filter(
                rental_equipment_id=rental_equipment_id,
            )

        status_value = str(
            self.request.query_params.get(
                "status",
                "",
            )
            or ""
        ).strip()

        if status_value:
            queryset = queryset.filter(
                status=status_value,
            )

        result = str(
            self.request.query_params.get(
                "result",
                "",
            )
            or ""
        ).strip()

        if result:
            queryset = queryset.filter(
                result=result,
            )

        technician_id = str(
            self.request.query_params.get(
                "assigned_technician",
                "",
            )
            or ""
        ).strip()

        if technician_id:
            queryset = queryset.filter(
                assigned_technician_id=technician_id,
            )

        scheduled_from = str(
            self.request.query_params.get(
                "scheduled_from",
                "",
            )
            or ""
        ).strip()

        if scheduled_from:
            queryset = queryset.filter(
                scheduled_date__gte=scheduled_from,
            )

        scheduled_to = str(
            self.request.query_params.get(
                "scheduled_to",
                "",
            )
            or ""
        ).strip()

        if scheduled_to:
            queryset = queryset.filter(
                scheduled_date__lte=scheduled_to,
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RentalPreparationListSerializer

        return RentalPreparationSerializer

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
        preparation = self.get_object()

        if preparation.archived_at:
            return Response(
                {
                    "detail": (
                        "La preparación ya se encuentra archivada."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if preparation.status in [
            RentalPreparation.Status.IN_PROGRESS,
            RentalPreparation.Status.WAITING_PARTS,
        ]:
            return Response(
                {
                    "detail": (
                        "No se puede archivar una preparación "
                        "que se encuentra en proceso."
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

        preparation.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Preparación archivada correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="archive",
    )
    def archive_preparation(self, request, pk=None):
        return self.destroy(
            request,
            pk=pk,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
    )
    def restore_preparation(self, request, pk=None):
        preparation = (
            RentalPreparation.objects
            .filter(
                pk=pk,
            )
            .first()
        )

        if not preparation:
            return Response(
                {
                    "detail": (
                        "Preparación no encontrada."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not preparation.archived_at:
            return Response(
                {
                    "detail": (
                        "La preparación no se encuentra archivada."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        preparation.restore(
            user=request.user,
        )

        serializer = RentalPreparationSerializer(
            preparation,
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
    def active_preparations(self, request):
        queryset = (
            self.get_queryset()
            .filter(
                status__in=[
                    RentalPreparation.Status.PENDING,
                    RentalPreparation.Status.IN_PROGRESS,
                    RentalPreparation.Status.WAITING_PARTS,
                    RentalPreparation.Status.OBSERVED,
                ],
            )
            .order_by(
                "scheduled_date",
                "requested_at",
            )
        )

        serializer = RentalPreparationListSerializer(
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
        rental_equipment_id = str(
            request.query_params.get(
                "rental_equipment",
                "",
            )
            or ""
        ).strip()

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
                "-requested_at",
                "-created_at",
            )
        )

        serializer = RentalPreparationListSerializer(
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