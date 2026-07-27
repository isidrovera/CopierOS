# -*- coding: utf-8 -*-
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.rentals.models import RentalReplacement
from apps.rentals.serializers import (
    RentalReplacementListSerializer,
    RentalReplacementSerializer,
)


class RentalReplacementViewSet(viewsets.ModelViewSet):
    """
    API para administrar reemplazos de equipos alquilados.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    queryset = RentalReplacement.objects.all()

    def get_queryset(self):
        queryset = (
            RentalReplacement.objects
            .select_related(
                "rental_assignment",
                "rental_assignment__contract",
                "rental_assignment__customer",
                "rental_assignment__branch",
                "rental_assignment__contact",
                "outgoing_equipment",
                "outgoing_equipment__equipment",
                "outgoing_equipment__equipment__equipment_model",
                "outgoing_equipment__equipment__equipment_model__brand",
                "incoming_equipment",
                "incoming_equipment__equipment",
                "incoming_equipment__equipment__equipment_model",
                "incoming_equipment__equipment__equipment_model__brand",
                "approved_by",
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
                | Q(rental_assignment__code__icontains=search)
                | Q(
                    rental_assignment__contract__code__icontains=search
                )
                | Q(
                    rental_assignment__contract__contract_number__icontains=search
                )
                | Q(
                    rental_assignment__customer__legal_name__icontains=search
                )
                | Q(
                    rental_assignment__customer__trade_name__icontains=search
                )
                | Q(
                    outgoing_equipment__equipment__serial_number__icontains=search
                )
                | Q(
                    outgoing_equipment__equipment__internal_code__icontains=search
                )
                | Q(
                    outgoing_equipment__equipment__equipment_model__name__icontains=search
                )
                | Q(
                    outgoing_equipment__equipment__equipment_model__brand__name__icontains=search
                )
                | Q(
                    incoming_equipment__equipment__serial_number__icontains=search
                )
                | Q(
                    incoming_equipment__equipment__internal_code__icontains=search
                )
                | Q(
                    incoming_equipment__equipment__equipment_model__name__icontains=search
                )
                | Q(
                    incoming_equipment__equipment__equipment_model__brand__name__icontains=search
                )
                | Q(reason_detail__icontains=search)
                | Q(customer_representative_name__icontains=search)
                | Q(technical_observations__icontains=search)
                | Q(customer_observations__icontains=search)
                | Q(rejection_reason__icontains=search)
                | Q(cancellation_reason__icontains=search)
            ).distinct()

        rental_assignment_id = str(
            self.request.query_params.get(
                "rental_assignment",
                "",
            )
            or ""
        ).strip()

        if rental_assignment_id:
            queryset = queryset.filter(
                rental_assignment_id=rental_assignment_id,
            )

        contract_id = str(
            self.request.query_params.get(
                "contract",
                "",
            )
            or ""
        ).strip()

        if contract_id:
            queryset = queryset.filter(
                rental_assignment__contract_id=contract_id,
            )

        customer_id = str(
            self.request.query_params.get(
                "customer",
                "",
            )
            or ""
        ).strip()

        if customer_id:
            queryset = queryset.filter(
                rental_assignment__customer_id=customer_id,
            )

        branch_id = str(
            self.request.query_params.get(
                "branch",
                "",
            )
            or ""
        ).strip()

        if branch_id:
            queryset = queryset.filter(
                rental_assignment__branch_id=branch_id,
            )

        outgoing_equipment_id = str(
            self.request.query_params.get(
                "outgoing_equipment",
                "",
            )
            or ""
        ).strip()

        if outgoing_equipment_id:
            queryset = queryset.filter(
                outgoing_equipment_id=outgoing_equipment_id,
            )

        incoming_equipment_id = str(
            self.request.query_params.get(
                "incoming_equipment",
                "",
            )
            or ""
        ).strip()

        if incoming_equipment_id:
            queryset = queryset.filter(
                incoming_equipment_id=incoming_equipment_id,
            )

        replacement_type = str(
            self.request.query_params.get(
                "replacement_type",
                "",
            )
            or ""
        ).strip()

        if replacement_type:
            queryset = queryset.filter(
                replacement_type=replacement_type,
            )

        replacement_reason = str(
            self.request.query_params.get(
                "reason",
                "",
            )
            or ""
        ).strip()

        if replacement_reason:
            queryset = queryset.filter(
                reason=replacement_reason,
            )

        replacement_status = str(
            self.request.query_params.get(
                "status",
                "",
            )
            or ""
        ).strip()

        if replacement_status:
            queryset = queryset.filter(
                status=replacement_status,
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

        approved_by_id = str(
            self.request.query_params.get(
                "approved_by",
                "",
            )
            or ""
        ).strip()

        if approved_by_id:
            queryset = queryset.filter(
                approved_by_id=approved_by_id,
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

        requested_from = str(
            self.request.query_params.get(
                "requested_from",
                "",
            )
            or ""
        ).strip()

        if requested_from:
            queryset = queryset.filter(
                requested_at__date__gte=requested_from,
            )

        requested_to = str(
            self.request.query_params.get(
                "requested_to",
                "",
            )
            or ""
        ).strip()

        if requested_to:
            queryset = queryset.filter(
                requested_at__date__lte=requested_to,
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
                scheduled_at__date__gte=scheduled_from,
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
                scheduled_at__date__lte=scheduled_to,
            )

        completed_from = str(
            self.request.query_params.get(
                "completed_from",
                "",
            )
            or ""
        ).strip()

        if completed_from:
            queryset = queryset.filter(
                completed_at__date__gte=completed_from,
            )

        completed_to = str(
            self.request.query_params.get(
                "completed_to",
                "",
            )
            or ""
        ).strip()

        if completed_to:
            queryset = queryset.filter(
                completed_at__date__lte=completed_to,
            )

        customer_conformity = str(
            self.request.query_params.get(
                "customer_conformity",
                "",
            )
            or ""
        ).strip().lower()

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
            return RentalReplacementListSerializer

        return RentalReplacementSerializer

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
        replacement = self.get_object()

        if replacement.archived_at:
            return Response(
                {
                    "detail": (
                        "El reemplazo ya se encuentra archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if replacement.status in [
            RentalReplacement.Status.IN_TRANSIT,
            RentalReplacement.Status.IN_PROGRESS,
        ]:
            return Response(
                {
                    "detail": (
                        "No se puede archivar un reemplazo "
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

        replacement.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Reemplazo archivado correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="archive",
    )
    def archive_replacement(self, request, pk=None):
        return self.destroy(
            request,
            pk=pk,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
    )
    def restore_replacement(self, request, pk=None):
        replacement = (
            RentalReplacement.objects
            .filter(
                pk=pk,
            )
            .first()
        )

        if not replacement:
            return Response(
                {
                    "detail": (
                        "Reemplazo no encontrado."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not replacement.archived_at:
            return Response(
                {
                    "detail": (
                        "El reemplazo no se encuentra archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        replacement.restore(
            user=request.user,
        )

        serializer = RentalReplacementSerializer(
            replacement,
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
    def active_replacements(self, request):
        queryset = (
            self.get_queryset()
            .filter(
                status__in=[
                    RentalReplacement.Status.REQUESTED,
                    RentalReplacement.Status.APPROVED,
                    RentalReplacement.Status.SCHEDULED,
                    RentalReplacement.Status.ASSIGNED,
                    RentalReplacement.Status.IN_TRANSIT,
                    RentalReplacement.Status.IN_PROGRESS,
                    RentalReplacement.Status.OBSERVED,
                ],
            )
            .order_by(
                "scheduled_at",
                "requested_at",
            )
        )

        serializer = RentalReplacementListSerializer(
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
        rental_assignment_id = str(
            request.query_params.get(
                "rental_assignment",
                "",
            )
            or ""
        ).strip()

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

        serializer = RentalReplacementListSerializer(
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
                Q(
                    outgoing_equipment_id=rental_equipment_id,
                )
                | Q(
                    incoming_equipment_id=rental_equipment_id,
                )
            )
            .order_by(
                "-requested_at",
                "-created_at",
            )
        )

        serializer = RentalReplacementListSerializer(
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
        technician_id = str(
            request.query_params.get(
                "assigned_technician",
                "",
            )
            or ""
        ).strip()

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
                    RentalReplacement.Status.SCHEDULED,
                    RentalReplacement.Status.ASSIGNED,
                    RentalReplacement.Status.IN_TRANSIT,
                    RentalReplacement.Status.IN_PROGRESS,
                    RentalReplacement.Status.OBSERVED,
                ],
            )
            .order_by(
                "scheduled_at",
                "requested_at",
            )
        )

        serializer = RentalReplacementListSerializer(
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