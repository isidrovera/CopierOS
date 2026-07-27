# -*- coding: utf-8 -*-
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.rentals.models import RentalDocument
from apps.rentals.serializers import (
    RentalDocumentListSerializer,
    RentalDocumentSerializer,
)


class RentalDocumentViewSet(viewsets.ModelViewSet):
    """
    API para administrar documentos relacionados
    con los equipos y procesos de alquiler.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    queryset = RentalDocument.objects.all()

    def get_queryset(self):
        queryset = (
            RentalDocument.objects
            .select_related(
                "rental_equipment",
                "rental_equipment__equipment",
                "rental_equipment__equipment__equipment_model",
                "rental_equipment__equipment__equipment_model__brand",
                "preparation",
                "contract",
                "contract__customer",
                "assignment",
                "assignment__contract",
                "assignment__customer",
                "assignment__branch",
                "installation",
                "removal",
                "replacement",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .order_by(
                "-issued_date",
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
                Q(title__icontains=search)
                | Q(document_number__icontains=search)
                | Q(description__icontains=search)
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
                | Q(preparation__code__icontains=search)
                | Q(contract__code__icontains=search)
                | Q(contract__contract_number__icontains=search)
                | Q(contract__customer__legal_name__icontains=search)
                | Q(contract__customer__trade_name__icontains=search)
                | Q(assignment__code__icontains=search)
                | Q(assignment__contract__code__icontains=search)
                | Q(installation__code__icontains=search)
                | Q(removal__code__icontains=search)
                | Q(replacement__code__icontains=search)
                | Q(notes__icontains=search)
            ).distinct()

        document_type = str(
            self.request.query_params.get(
                "document_type",
                "",
            )
            or ""
        ).strip()

        if document_type:
            queryset = queryset.filter(
                document_type=document_type,
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

        preparation_id = str(
            self.request.query_params.get(
                "preparation",
                "",
            )
            or ""
        ).strip()

        if preparation_id:
            queryset = queryset.filter(
                preparation_id=preparation_id,
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
                Q(contract_id=contract_id)
                | Q(assignment__contract_id=contract_id)
            )

        assignment_id = str(
            self.request.query_params.get(
                "assignment",
                "",
            )
            or ""
        ).strip()

        if assignment_id:
            queryset = queryset.filter(
                assignment_id=assignment_id,
            )

        installation_id = str(
            self.request.query_params.get(
                "installation",
                "",
            )
            or ""
        ).strip()

        if installation_id:
            queryset = queryset.filter(
                installation_id=installation_id,
            )

        removal_id = str(
            self.request.query_params.get(
                "removal",
                "",
            )
            or ""
        ).strip()

        if removal_id:
            queryset = queryset.filter(
                removal_id=removal_id,
            )

        replacement_id = str(
            self.request.query_params.get(
                "replacement",
                "",
            )
            or ""
        ).strip()

        if replacement_id:
            queryset = queryset.filter(
                replacement_id=replacement_id,
            )

        issued_from = str(
            self.request.query_params.get(
                "issued_from",
                "",
            )
            or ""
        ).strip()

        if issued_from:
            queryset = queryset.filter(
                issued_date__gte=issued_from,
            )

        issued_to = str(
            self.request.query_params.get(
                "issued_to",
                "",
            )
            or ""
        ).strip()

        if issued_to:
            queryset = queryset.filter(
                issued_date__lte=issued_to,
            )

        is_verified = str(
            self.request.query_params.get(
                "is_verified",
                "",
            )
            or ""
        ).strip().lower()

        if is_verified in [
            "1",
            "true",
            "yes",
            "si",
            "sí",
        ]:
            queryset = queryset.filter(
                is_verified=True,
            )

        elif is_verified in [
            "0",
            "false",
            "no",
        ]:
            queryset = queryset.filter(
                is_verified=False,
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RentalDocumentListSerializer

        return RentalDocumentSerializer

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
        document = self.get_object()

        if document.archived_at:
            return Response(
                {
                    "detail": (
                        "El documento ya se encuentra archivado."
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

        document.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Documento archivado correctamente."
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="archive",
    )
    def archive_document(self, request, pk=None):
        return self.destroy(
            request,
            pk=pk,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="restore",
    )
    def restore_document(self, request, pk=None):
        document = (
            RentalDocument.objects
            .filter(
                pk=pk,
            )
            .first()
        )

        if not document:
            return Response(
                {
                    "detail": (
                        "Documento no encontrado."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not document.archived_at:
            return Response(
                {
                    "detail": (
                        "El documento no se encuentra archivado."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        document.restore(
            user=request.user,
        )

        serializer = RentalDocumentSerializer(
            document,
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
        url_path="equipment-documents",
    )
    def equipment_documents(self, request):
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
                "-issued_date",
                "-created_at",
            )
        )

        serializer = RentalDocumentListSerializer(
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
        url_path="contract-documents",
    )
    def contract_documents(self, request):
        contract_id = str(
            request.query_params.get(
                "contract",
                "",
            )
            or ""
        ).strip()

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
                Q(contract_id=contract_id)
                | Q(assignment__contract_id=contract_id)
            )
            .order_by(
                "-issued_date",
                "-created_at",
            )
        )

        serializer = RentalDocumentListSerializer(
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
        url_path="assignment-documents",
    )
    def assignment_documents(self, request):
        assignment_id = str(
            request.query_params.get(
                "assignment",
                "",
            )
            or ""
        ).strip()

        if not assignment_id:
            return Response(
                {
                    "detail": (
                        "Debe indicar la asignación."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = (
            self.get_queryset()
            .filter(
                assignment_id=assignment_id,
            )
            .order_by(
                "-issued_date",
                "-created_at",
            )
        )

        serializer = RentalDocumentListSerializer(
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