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

from ..models import EquipmentDocument
from ..serializers import (
    ArchiveEquipmentDocumentSerializer,
    EquipmentDocumentCreateUpdateSerializer,
    EquipmentDocumentDetailSerializer,
    EquipmentDocumentListSerializer,
    RemoveEquipmentDocumentVerificationSerializer,
    VerifyEquipmentDocumentSerializer,
)
from .equipment_type import parse_boolean_query_param


class EquipmentDocumentListCreateView(
    ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            EquipmentDocument.objects
            .select_related(
                "equipment",
                "equipment__equipment_model",
                "equipment__equipment_model__brand",
                "uploaded_by",
                "verified_by",
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
                    title__icontains=search,
                )
                | Q(
                    document_number__icontains=search,
                )
                | Q(
                    reference_number__icontains=search,
                )
                | Q(
                    original_filename__icontains=search,
                )
                | Q(
                    description__icontains=search,
                )
                | Q(
                    notes__icontains=search,
                )
                | Q(
                    equipment__internal_code__icontains=search,
                )
                | Q(
                    equipment__serial_number__icontains=search,
                )
                | Q(
                    equipment__equipment_model__name__icontains=search,
                )
                | Q(
                    equipment__equipment_model__brand__name__icontains=search,
                )
            )

        equipment_id = str(
            self.request.query_params.get(
                "equipment",
                "",
            )
        ).strip()

        if equipment_id:
            queryset = queryset.filter(
                equipment_id=equipment_id,
            )

        document_type = str(
            self.request.query_params.get(
                "document_type",
                "",
            )
        ).strip()

        if document_type:
            queryset = queryset.filter(
                document_type=document_type,
            )

        reference_type = str(
            self.request.query_params.get(
                "reference_type",
                "",
            )
        ).strip()

        if reference_type:
            queryset = queryset.filter(
                reference_type=reference_type,
            )

        reference_id = str(
            self.request.query_params.get(
                "reference_id",
                "",
            )
        ).strip()

        if reference_id:
            queryset = queryset.filter(
                reference_id=reference_id,
            )

        uploaded_by_id = str(
            self.request.query_params.get(
                "uploaded_by",
                "",
            )
        ).strip()

        if uploaded_by_id:
            queryset = queryset.filter(
                uploaded_by_id=uploaded_by_id,
            )

        verified_by_id = str(
            self.request.query_params.get(
                "verified_by",
                "",
            )
        ).strip()

        if verified_by_id:
            queryset = queryset.filter(
                verified_by_id=verified_by_id,
            )

        is_primary = parse_boolean_query_param(
            self.request.query_params.get(
                "is_primary"
            )
        )

        if is_primary is not None:
            queryset = queryset.filter(
                is_primary=is_primary,
            )

        is_confidential = parse_boolean_query_param(
            self.request.query_params.get(
                "is_confidential"
            )
        )

        if is_confidential is not None:
            queryset = queryset.filter(
                is_confidential=is_confidential,
            )

        is_verified = parse_boolean_query_param(
            self.request.query_params.get(
                "is_verified"
            )
        )

        if is_verified is not None:
            queryset = queryset.filter(
                is_verified=is_verified,
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

        document_from = str(
            self.request.query_params.get(
                "document_from",
                "",
            )
        ).strip()

        if document_from:
            queryset = queryset.filter(
                document_date__gte=document_from,
            )

        document_to = str(
            self.request.query_params.get(
                "document_to",
                "",
            )
        ).strip()

        if document_to:
            queryset = queryset.filter(
                document_date__lte=document_to,
            )

        expiration_from = str(
            self.request.query_params.get(
                "expiration_from",
                "",
            )
        ).strip()

        if expiration_from:
            queryset = queryset.filter(
                expiration_date__gte=expiration_from,
            )

        expiration_to = str(
            self.request.query_params.get(
                "expiration_to",
                "",
            )
        ).strip()

        if expiration_to:
            queryset = queryset.filter(
                expiration_date__lte=expiration_to,
            )

        return queryset.order_by(
            "-document_date",
            "-created_at",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return (
                EquipmentDocumentCreateUpdateSerializer
            )

        return EquipmentDocumentListSerializer

    @transaction.atomic
    def perform_create(
        self,
        serializer,
    ):
        serializer.save()


class EquipmentDocumentDetailUpdateView(
    RetrieveUpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            EquipmentDocument.objects
            .select_related(
                "equipment",
                "equipment__equipment_model",
                "equipment__equipment_model__brand",
                "uploaded_by",
                "verified_by",
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
                EquipmentDocumentCreateUpdateSerializer
            )

        return EquipmentDocumentDetailSerializer

    @transaction.atomic
    def perform_update(
        self,
        serializer,
    ):
        serializer.save()


class VerifyEquipmentDocumentView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        document_id,
    ):
        document = EquipmentDocument.objects.filter(
            id=document_id,
        ).first()

        if not document:
            return Response(
                {
                    "detail": (
                        "Documento de equipo no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if document.is_archived:
            return Response(
                {
                    "detail": (
                        "No puedes verificar un documento archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if document.is_verified:
            return Response(
                {
                    "detail": (
                        "El documento ya se encuentra verificado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = VerifyEquipmentDocumentSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        notes = str(
            serializer.validated_data.get(
                "notes",
                "",
            )
            or ""
        ).strip()

        if notes:
            document.notes = notes

        document.verify(
            user=request.user,
            save=False,
        )

        document.save()

        return Response(
            {
                "detail": (
                    "Documento verificado correctamente."
                ),
                "is_verified": document.is_verified,
                "verified_by": document.verified_by_id,
                "verified_at": document.verified_at,
            },
            status=status.HTTP_200_OK,
        )


class RemoveEquipmentDocumentVerificationView(
    APIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        document_id,
    ):
        document = EquipmentDocument.objects.filter(
            id=document_id,
        ).first()

        if not document:
            return Response(
                {
                    "detail": (
                        "Documento de equipo no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if document.is_archived:
            return Response(
                {
                    "detail": (
                        "No puedes modificar un documento archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not document.is_verified:
            return Response(
                {
                    "detail": (
                        "El documento no se encuentra verificado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            RemoveEquipmentDocumentVerificationSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        reason = str(
            serializer.validated_data.get(
                "reason",
                "",
            )
            or ""
        ).strip()

        if reason:
            document.notes = reason

        document.remove_verification(
            user=request.user,
            save=False,
        )

        document.save()

        return Response(
            {
                "detail": (
                    "Verificación retirada correctamente."
                ),
                "is_verified": document.is_verified,
                "verified_by": document.verified_by_id,
                "verified_at": document.verified_at,
            },
            status=status.HTTP_200_OK,
        )


class ArchiveEquipmentDocumentView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        document_id,
    ):
        document = EquipmentDocument.objects.filter(
            id=document_id,
        ).first()

        if not document:
            return Response(
                {
                    "detail": (
                        "Documento de equipo no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if document.is_archived:
            return Response(
                {
                    "detail": (
                        "El documento ya se encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            ArchiveEquipmentDocumentSerializer(
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

        document.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Documento archivado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestoreEquipmentDocumentView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        document_id,
    ):
        document = EquipmentDocument.objects.filter(
            id=document_id,
        ).first()

        if not document:
            return Response(
                {
                    "detail": (
                        "Documento de equipo no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not document.is_archived:
            return Response(
                {
                    "detail": (
                        "El documento no se encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        document.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Documento restaurado correctamente."
                ),
                "is_primary": document.is_primary,
            },
            status=status.HTTP_200_OK,
        )