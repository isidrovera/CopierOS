# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models import Q

from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import ImportBatch
from ..serializers import (
    ArchiveImportBatchSerializer,
    ChangeImportBatchStatusSerializer,
    ImportBatchCreateUpdateSerializer,
    ImportBatchDetailSerializer,
    ImportBatchListSerializer,
)
from .equipment_type import parse_boolean_query_param


class ImportBatchListCreateView(
    ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            ImportBatch.objects
            .select_related(
                "supplier",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .all()
        )

        include_archived = parse_boolean_query_param(
            self.request.query_params.get(
                "include_archived"
            )
        )

        if include_archived is not True:
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        search = str(
            self.request.query_params.get(
                "search",
                "",
            )
        ).strip()

        if search:
            queryset = queryset.filter(
                Q(
                    code__icontains=search,
                )
                | Q(
                    import_number__icontains=search,
                )
                | Q(
                    purchase_order_number__icontains=search,
                )
                | Q(
                    invoice_number__icontains=search,
                )
                | Q(
                    container_number__icontains=search,
                )
                | Q(
                    transport_reference__icontains=search,
                )
                | Q(
                    supplier__legal_name__icontains=search,
                )
                | Q(
                    supplier__trade_name__icontains=search,
                )
                | Q(
                    supplier__document_number__icontains=search,
                )
            )

        supplier_id = str(
            self.request.query_params.get(
                "supplier",
                "",
            )
        ).strip()

        if supplier_id:
            queryset = queryset.filter(
                supplier_id=supplier_id,
            )

        purchase_type = str(
            self.request.query_params.get(
                "purchase_type",
                "",
            )
        ).strip()

        if purchase_type:
            queryset = queryset.filter(
                purchase_type=purchase_type,
            )

        batch_status = str(
            self.request.query_params.get(
                "status",
                "",
            )
        ).strip()

        if batch_status:
            queryset = queryset.filter(
                status=batch_status,
            )

        currency = str(
            self.request.query_params.get(
                "currency",
                "",
            )
        ).strip().upper()

        if currency:
            queryset = queryset.filter(
                currency=currency,
            )

        origin_country_code = str(
            self.request.query_params.get(
                "origin_country_code",
                "",
            )
        ).strip().upper()

        if origin_country_code:
            queryset = queryset.filter(
                origin_country_code=origin_country_code,
            )

        container_number = str(
            self.request.query_params.get(
                "container_number",
                "",
            )
        ).strip()

        if container_number:
            queryset = queryset.filter(
                container_number__icontains=container_number,
            )

        is_active = parse_boolean_query_param(
            self.request.query_params.get(
                "is_active"
            )
        )

        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active,
            )

        return queryset.order_by(
            "-purchase_date",
            "-created_at",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return (
                ImportBatchCreateUpdateSerializer
            )

        return ImportBatchListSerializer

    @transaction.atomic
    def perform_create(
        self,
        serializer,
    ):
        serializer.save()


class ImportBatchDetailUpdateView(
    RetrieveUpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            ImportBatch.objects
            .select_related(
                "supplier",
                "created_by",
                "updated_by",
                "archived_by",
            )
            .all()
        )

    def get_serializer_class(self):
        if self.request.method in (
            "PUT",
            "PATCH",
        ):
            return (
                ImportBatchCreateUpdateSerializer
            )

        return ImportBatchDetailSerializer

    @transaction.atomic
    def perform_update(
        self,
        serializer,
    ):
        serializer.save()


class ChangeImportBatchStatusView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        import_batch_id,
    ):
        import_batch = (
            ImportBatch.objects.filter(
                id=import_batch_id,
            )
            .first()
        )

        if not import_batch:
            return Response(
                {
                    "detail": (
                        "Importación o lote no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if import_batch.is_archived:
            return Response(
                {
                    "detail": (
                        "No puedes cambiar el estado "
                        "de un lote archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            ChangeImportBatchStatusSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        new_status = serializer.validated_data[
            "status"
        ]

        notes = str(
            serializer.validated_data.get(
                "notes",
                "",
            )
            or ""
        ).strip()

        if import_batch.status == new_status:
            return Response(
                {
                    "detail": (
                        "El lote ya tiene el estado indicado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        import_batch.status = new_status

        if notes:
            import_batch.notes = notes

        import_batch.updated_by = request.user
        import_batch.full_clean()
        import_batch.save()

        return Response(
            {
                "detail": (
                    "Estado del lote actualizado correctamente."
                ),
                "status": import_batch.status,
                "status_name": import_batch.get_status_display(),
            },
            status=status.HTTP_200_OK,
        )


class ArchiveImportBatchView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        import_batch_id,
    ):
        import_batch = (
            ImportBatch.objects.filter(
                id=import_batch_id,
            )
            .first()
        )

        if not import_batch:
            return Response(
                {
                    "detail": (
                        "Importación o lote no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if import_batch.is_archived:
            return Response(
                {
                    "detail": (
                        "El lote ya se encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            ArchiveImportBatchSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        reason = serializer.validated_data.get(
            "reason",
            "",
        )

        import_batch.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Importación o lote archivado "
                    "correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestoreImportBatchView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        import_batch_id,
    ):
        import_batch = (
            ImportBatch.objects.filter(
                id=import_batch_id,
            )
            .first()
        )

        if not import_batch:
            return Response(
                {
                    "detail": (
                        "Importación o lote no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not import_batch.is_archived:
            return Response(
                {
                    "detail": (
                        "El lote no se encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        import_batch.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Importación o lote restaurado "
                    "correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )