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

from ..models import MeterReading
from ..serializers import (
    ApplyMeterReadingSerializer,
    ArchiveMeterReadingSerializer,
    MeterReadingCreateUpdateSerializer,
    MeterReadingDetailSerializer,
    MeterReadingListSerializer,
    VerifyMeterReadingSerializer,
)
from .equipment_type import parse_boolean_query_param


class MeterReadingListCreateView(
    ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            MeterReading.objects
            .select_related(
                "equipment",
                "equipment__equipment_model",
                "equipment__equipment_model__brand",
                "registered_by",
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
                | Q(
                    reference_number__icontains=search,
                )
                | Q(
                    ip_address__icontains=search,
                )
                | Q(
                    correction_reason__icontains=search,
                )
                | Q(
                    notes__icontains=search,
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

        reading_type = str(
            self.request.query_params.get(
                "reading_type",
                "",
            )
        ).strip()

        if reading_type:
            queryset = queryset.filter(
                reading_type=reading_type,
            )

        source = str(
            self.request.query_params.get(
                "source",
                "",
            )
        ).strip()

        if source:
            queryset = queryset.filter(
                source=source,
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

        registered_by_id = str(
            self.request.query_params.get(
                "registered_by",
                "",
            )
        ).strip()

        if registered_by_id:
            queryset = queryset.filter(
                registered_by_id=registered_by_id,
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

        is_verified = parse_boolean_query_param(
            self.request.query_params.get(
                "is_verified"
            )
        )

        if is_verified is not None:
            queryset = queryset.filter(
                is_verified=is_verified,
            )

        is_applied_to_equipment = (
            parse_boolean_query_param(
                self.request.query_params.get(
                    "is_applied_to_equipment"
                )
            )
        )

        if is_applied_to_equipment is not None:
            queryset = queryset.filter(
                is_applied_to_equipment=(
                    is_applied_to_equipment
                ),
            )

        reading_from = str(
            self.request.query_params.get(
                "reading_from",
                "",
            )
        ).strip()

        if reading_from:
            queryset = queryset.filter(
                reading_date__date__gte=reading_from,
            )

        reading_to = str(
            self.request.query_params.get(
                "reading_to",
                "",
            )
        ).strip()

        if reading_to:
            queryset = queryset.filter(
                reading_date__date__lte=reading_to,
            )

        return queryset.order_by(
            "-reading_date",
            "-created_at",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return (
                MeterReadingCreateUpdateSerializer
            )

        return MeterReadingListSerializer

    @transaction.atomic
    def perform_create(
        self,
        serializer,
    ):
        serializer.save()


class MeterReadingDetailUpdateView(
    RetrieveUpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            MeterReading.objects
            .select_related(
                "equipment",
                "equipment__equipment_model",
                "equipment__equipment_model__brand",
                "registered_by",
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
                MeterReadingCreateUpdateSerializer
            )

        return MeterReadingDetailSerializer

    @transaction.atomic
    def perform_update(
        self,
        serializer,
    ):
        serializer.save()


class VerifyMeterReadingView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        reading_id,
    ):
        reading = MeterReading.objects.filter(
            id=reading_id,
        ).first()

        if not reading:
            return Response(
                {
                    "detail": (
                        "Lectura de contador no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if reading.is_archived:
            return Response(
                {
                    "detail": (
                        "No puedes verificar una lectura archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if reading.is_verified:
            return Response(
                {
                    "detail": (
                        "La lectura ya se encuentra verificada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = VerifyMeterReadingSerializer(
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
            reading.notes = notes

        reading.verify(
            user=request.user,
            save=False,
        )

        reading.save()

        return Response(
            {
                "detail": (
                    "Lectura verificada correctamente."
                ),
                "is_verified": reading.is_verified,
                "verified_by": reading.verified_by_id,
                "verified_at": reading.verified_at,
            },
            status=status.HTTP_200_OK,
        )


class ApplyMeterReadingView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        reading_id,
    ):
        reading = (
            MeterReading.objects
            .select_related(
                "equipment",
                "equipment__equipment_model",
            )
            .filter(
                id=reading_id,
            )
            .first()
        )

        if not reading:
            return Response(
                {
                    "detail": (
                        "Lectura de contador no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if reading.is_archived:
            return Response(
                {
                    "detail": (
                        "No puedes aplicar una lectura archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if reading.is_applied_to_equipment:
            return Response(
                {
                    "detail": (
                        "La lectura ya fue aplicada al equipo."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ApplyMeterReadingSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        equipment = reading.apply_to_equipment(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Lectura aplicada al equipo correctamente."
                ),
                "equipment": equipment.id,
                "current_total_meter": (
                    equipment.current_total_meter
                ),
                "current_black_meter": (
                    equipment.current_black_meter
                ),
                "current_color_meter": (
                    equipment.current_color_meter
                ),
                "current_scan_meter": (
                    equipment.current_scan_meter
                ),
                "last_meter_date": (
                    equipment.last_meter_date
                ),
                "last_meter_source": (
                    equipment.last_meter_source
                ),
                "is_applied_to_equipment": (
                    reading.is_applied_to_equipment
                ),
            },
            status=status.HTTP_200_OK,
        )


class ArchiveMeterReadingView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        reading_id,
    ):
        reading = MeterReading.objects.filter(
            id=reading_id,
        ).first()

        if not reading:
            return Response(
                {
                    "detail": (
                        "Lectura de contador no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if reading.is_archived:
            return Response(
                {
                    "detail": (
                        "La lectura ya se encuentra archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if reading.is_applied_to_equipment:
            return Response(
                {
                    "detail": (
                        "No puedes archivar una lectura que ya "
                        "fue aplicada al equipo."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ArchiveMeterReadingSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        reason = serializer.validated_data.get(
            "reason",
            "",
        )

        reading.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Lectura archivada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestoreMeterReadingView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        reading_id,
    ):
        reading = MeterReading.objects.filter(
            id=reading_id,
        ).first()

        if not reading:
            return Response(
                {
                    "detail": (
                        "Lectura de contador no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not reading.is_archived:
            return Response(
                {
                    "detail": (
                        "La lectura no se encuentra archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reading.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Lectura restaurada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )