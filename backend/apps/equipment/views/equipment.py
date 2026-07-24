# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.partners.models import (
    Partner,
    PartnerBranch,
)
from apps.users.models import User

from ..models import Equipment
from ..serializers import (
    ArchiveEquipmentSerializer,
    ChangeEquipmentCommercialStatusSerializer,
    ChangeEquipmentTechnicalStatusSerializer,
    EquipmentCreateUpdateSerializer,
    EquipmentDetailSerializer,
    EquipmentListSerializer,
    RegisterInitialEquipmentMetersSerializer,
)
from .equipment_type import parse_boolean_query_param


class EquipmentListCreateView(
    ListCreateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            Equipment.objects
            .select_related(
                "equipment_model",
                "equipment_model__brand",
                "equipment_model__equipment_type",
                "import_batch",
                "supplier",
                "owner_partner",
                "customer",
                "customer_branch",
                "advisor",
                "unloading_registered_by",
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
                    internal_code__icontains=search,
                )
                | Q(
                    serial_number__icontains=search,
                )
                | Q(
                    equipment_model__name__icontains=search,
                )
                | Q(
                    equipment_model__commercial_name__icontains=search,
                )
                | Q(
                    equipment_model__family__icontains=search,
                )
                | Q(
                    equipment_model__brand__name__icontains=search,
                )
                | Q(
                    import_reference__icontains=search,
                )
                | Q(
                    purchase_invoice_number__icontains=search,
                )
                | Q(
                    sale_invoice_number__icontains=search,
                )
                | Q(
                    warehouse_location__icontains=search,
                )
                | Q(
                    position_reference__icontains=search,
                )
                | Q(
                    hostname__icontains=search,
                )
                | Q(
                    ip_address__icontains=search,
                )
                | Q(
                    mac_address__icontains=search,
                )
                | Q(
                    asset_number__icontains=search,
                )
                | Q(
                    customer__legal_name__icontains=search,
                )
                | Q(
                    customer__trade_name__icontains=search,
                )
                | Q(
                    customer__document_number__icontains=search,
                )
            ).distinct()

        equipment_model_id = str(
            self.request.query_params.get(
                "equipment_model",
                "",
            )
        ).strip()

        if equipment_model_id:
            queryset = queryset.filter(
                equipment_model_id=equipment_model_id,
            )

        brand_id = str(
            self.request.query_params.get(
                "brand",
                "",
            )
        ).strip()

        if brand_id:
            queryset = queryset.filter(
                equipment_model__brand_id=brand_id,
            )

        equipment_type_id = str(
            self.request.query_params.get(
                "equipment_type",
                "",
            )
        ).strip()

        if equipment_type_id:
            queryset = queryset.filter(
                equipment_model__equipment_type_id=(
                    equipment_type_id
                ),
            )

        import_batch_id = str(
            self.request.query_params.get(
                "import_batch",
                "",
            )
        ).strip()

        if import_batch_id:
            queryset = queryset.filter(
                import_batch_id=import_batch_id,
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

        owner_partner_id = str(
            self.request.query_params.get(
                "owner_partner",
                "",
            )
        ).strip()

        if owner_partner_id:
            queryset = queryset.filter(
                owner_partner_id=owner_partner_id,
            )

        customer_id = str(
            self.request.query_params.get(
                "customer",
                "",
            )
        ).strip()

        if customer_id:
            queryset = queryset.filter(
                customer_id=customer_id,
            )

        customer_branch_id = str(
            self.request.query_params.get(
                "customer_branch",
                "",
            )
        ).strip()

        if customer_branch_id:
            queryset = queryset.filter(
                customer_branch_id=customer_branch_id,
            )

        advisor_id = str(
            self.request.query_params.get(
                "advisor",
                "",
            )
        ).strip()

        if advisor_id:
            queryset = queryset.filter(
                advisor_id=advisor_id,
            )

        ownership_type = str(
            self.request.query_params.get(
                "ownership_type",
                "",
            )
        ).strip()

        if ownership_type:
            queryset = queryset.filter(
                ownership_type=ownership_type,
            )

        physical_condition = str(
            self.request.query_params.get(
                "physical_condition",
                "",
            )
        ).strip()

        if physical_condition:
            queryset = queryset.filter(
                physical_condition=physical_condition,
            )

        technical_status = str(
            self.request.query_params.get(
                "technical_status",
                "",
            )
        ).strip()

        if technical_status:
            queryset = queryset.filter(
                technical_status=technical_status,
            )

        commercial_status = str(
            self.request.query_params.get(
                "commercial_status",
                "",
            )
        ).strip()

        if commercial_status:
            queryset = queryset.filter(
                commercial_status=commercial_status,
            )

        warehouse_location = str(
            self.request.query_params.get(
                "warehouse_location",
                "",
            )
        ).strip()

        if warehouse_location:
            queryset = queryset.filter(
                warehouse_location__icontains=warehouse_location,
            )

        color_mode = str(
            self.request.query_params.get(
                "color_mode",
                "",
            )
        ).strip()

        if color_mode:
            queryset = queryset.filter(
                equipment_model__color_mode=color_mode,
            )

        is_available = parse_boolean_query_param(
            self.request.query_params.get(
                "is_available"
            )
        )

        if is_available is not None:
            queryset = queryset.filter(
                is_available=is_available,
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
            "-created_at",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return EquipmentCreateUpdateSerializer

        return EquipmentListSerializer

    @transaction.atomic
    def perform_create(
        self,
        serializer,
    ):
        serializer.save()


class EquipmentDetailUpdateView(
    RetrieveUpdateAPIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            Equipment.objects
            .select_related(
                "equipment_model",
                "equipment_model__brand",
                "equipment_model__equipment_type",
                "import_batch",
                "supplier",
                "owner_partner",
                "customer",
                "customer_branch",
                "advisor",
                "unloading_registered_by",
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
            return EquipmentCreateUpdateSerializer

        return EquipmentDetailSerializer

    @transaction.atomic
    def perform_update(
        self,
        serializer,
    ):
        serializer.save()


class ChangeEquipmentTechnicalStatusView(
    APIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        equipment_id,
    ):
        equipment = Equipment.objects.filter(
            id=equipment_id,
        ).first()

        if not equipment:
            return Response(
                {
                    "detail": (
                        "Equipo no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if equipment.is_archived:
            return Response(
                {
                    "detail": (
                        "No puedes cambiar el estado "
                        "de un equipo archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            ChangeEquipmentTechnicalStatusSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        new_status = serializer.validated_data[
            "technical_status"
        ]

        reason = str(
            serializer.validated_data.get(
                "reason",
                "",
            )
            or ""
        ).strip()

        if equipment.technical_status == new_status:
            return Response(
                {
                    "detail": (
                        "El equipo ya tiene el estado "
                        "técnico indicado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        equipment.technical_status = new_status
        equipment.technical_status_reason = reason
        equipment.updated_by = request.user

        try:
            equipment.full_clean()
            equipment.save()
        except DjangoValidationError as exc:
            return Response(
                getattr(
                    exc,
                    "message_dict",
                    {
                        "detail": exc.messages,
                    },
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": (
                    "Estado técnico actualizado correctamente."
                ),
                "technical_status": (
                    equipment.technical_status
                ),
                "technical_status_name": (
                    equipment.get_technical_status_display()
                ),
                "is_available": equipment.is_available,
            },
            status=status.HTTP_200_OK,
        )


class ChangeEquipmentCommercialStatusView(
    APIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        equipment_id,
    ):
        equipment = Equipment.objects.filter(
            id=equipment_id,
        ).first()

        if not equipment:
            return Response(
                {
                    "detail": (
                        "Equipo no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if equipment.is_archived:
            return Response(
                {
                    "detail": (
                        "No puedes cambiar el estado "
                        "de un equipo archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            ChangeEquipmentCommercialStatusSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        new_status = serializer.validated_data[
            "commercial_status"
        ]

        customer_id = serializer.validated_data.get(
            "customer"
        )

        customer_branch_id = (
            serializer.validated_data.get(
                "customer_branch"
            )
        )

        advisor_id = serializer.validated_data.get(
            "advisor"
        )

        reason = str(
            serializer.validated_data.get(
                "reason",
                "",
            )
            or ""
        ).strip()

        customer = equipment.customer
        customer_branch = equipment.customer_branch
        advisor = equipment.advisor

        if customer_id is not None:
            customer = Partner.objects.filter(
                id=customer_id,
                archived_at__isnull=True,
                is_active=True,
            ).first()

            if not customer:
                return Response(
                    {
                        "customer": (
                            "Cliente no encontrado, inactivo "
                            "o archivado."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if customer_branch_id is not None:
            customer_branch = (
                PartnerBranch.objects.filter(
                    id=customer_branch_id,
                    archived_at__isnull=True,
                    is_active=True,
                )
                .first()
            )

            if not customer_branch:
                return Response(
                    {
                        "customer_branch": (
                            "Sucursal no encontrada, inactiva "
                            "o archivada."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if advisor_id is not None:
            advisor = User.objects.filter(
                id=advisor_id,
                is_active=True,
            ).first()

            if not advisor:
                return Response(
                    {
                        "advisor": (
                            "Asesor no encontrado o inactivo."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        equipment.commercial_status = new_status
        equipment.commercial_status_reason = reason
        equipment.customer = customer
        equipment.customer_branch = customer_branch
        equipment.advisor = advisor
        equipment.updated_by = request.user

        if (
            new_status
            == Equipment.CommercialStatus.RESERVED
            and not equipment.reservation_date
        ):
            equipment.reservation_date = timezone.now()

        statuses_without_customer = {
            Equipment.CommercialStatus.WAREHOUSE,
            Equipment.CommercialStatus.RETURNED,
        }

        if new_status in statuses_without_customer:
            equipment.customer = None
            equipment.customer_branch = None
            equipment.advisor = None
            equipment.reservation_date = None
            equipment.reservation_expiration_date = None

        try:
            equipment.full_clean()
            equipment.save()
        except DjangoValidationError as exc:
            return Response(
                getattr(
                    exc,
                    "message_dict",
                    {
                        "detail": exc.messages,
                    },
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": (
                    "Estado comercial actualizado correctamente."
                ),
                "commercial_status": (
                    equipment.commercial_status
                ),
                "commercial_status_name": (
                    equipment.get_commercial_status_display()
                ),
                "customer": equipment.customer_id,
                "customer_branch": (
                    equipment.customer_branch_id
                ),
                "advisor": equipment.advisor_id,
                "is_available": equipment.is_available,
            },
            status=status.HTTP_200_OK,
        )


class RegisterInitialEquipmentMetersView(
    APIView
):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        equipment_id,
    ):
        equipment = Equipment.objects.filter(
            id=equipment_id,
        ).select_related(
            "equipment_model",
        ).first()

        if not equipment:
            return Response(
                {
                    "detail": (
                        "Equipo no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if equipment.is_archived:
            return Response(
                {
                    "detail": (
                        "No puedes registrar contadores "
                        "en un equipo archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            RegisterInitialEquipmentMetersSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        total_meter = serializer.validated_data.get(
            "initial_total_meter",
            0,
        )

        black_meter = serializer.validated_data.get(
            "initial_black_meter",
            0,
        )

        color_meter = serializer.validated_data.get(
            "initial_color_meter",
            0,
        )

        scan_meter = serializer.validated_data.get(
            "initial_scan_meter",
            0,
        )

        notes = str(
            serializer.validated_data.get(
                "notes",
                "",
            )
            or ""
        ).strip()

        if (
            not equipment.equipment_model.has_color_meter
            and color_meter > 0
        ):
            return Response(
                {
                    "initial_color_meter": (
                        "El modelo seleccionado no utiliza "
                        "contador de color."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            not equipment.equipment_model.has_scan_meter
            and scan_meter > 0
        ):
            return Response(
                {
                    "initial_scan_meter": (
                        "El modelo seleccionado no utiliza "
                        "contador de escaneo."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        equipment.initial_total_meter = total_meter
        equipment.initial_black_meter = black_meter
        equipment.initial_color_meter = color_meter
        equipment.initial_scan_meter = scan_meter

        equipment.register_initial_meters_as_current()

        equipment.unloading_registered_by = request.user
        equipment.updated_by = request.user

        if not equipment.unloading_date:
            equipment.unloading_date = timezone.now()

        if notes:
            equipment.unloading_observations = notes

        try:
            equipment.full_clean()
            equipment.save()
        except DjangoValidationError as exc:
            return Response(
                getattr(
                    exc,
                    "message_dict",
                    {
                        "detail": exc.messages,
                    },
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": (
                    "Contadores iniciales registrados "
                    "correctamente."
                ),
                "initial_total_meter": (
                    equipment.initial_total_meter
                ),
                "initial_black_meter": (
                    equipment.initial_black_meter
                ),
                "initial_color_meter": (
                    equipment.initial_color_meter
                ),
                "initial_scan_meter": (
                    equipment.initial_scan_meter
                ),
                "last_meter_date": (
                    equipment.last_meter_date
                ),
                "last_meter_source": (
                    equipment.last_meter_source
                ),
            },
            status=status.HTTP_200_OK,
        )


class ArchiveEquipmentView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        equipment_id,
    ):
        equipment = Equipment.objects.filter(
            id=equipment_id,
        ).first()

        if not equipment:
            return Response(
                {
                    "detail": (
                        "Equipo no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if equipment.is_archived:
            return Response(
                {
                    "detail": (
                        "El equipo ya se encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ArchiveEquipmentSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        reason = serializer.validated_data.get(
            "reason",
            "",
        )

        equipment.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Equipo archivado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestoreEquipmentView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        equipment_id,
    ):
        equipment = Equipment.objects.filter(
            id=equipment_id,
        ).first()

        if not equipment:
            return Response(
                {
                    "detail": (
                        "Equipo no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not equipment.is_archived:
            return Response(
                {
                    "detail": (
                        "El equipo no se encuentra archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        equipment.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Equipo restaurado correctamente."
                ),
                "is_available": equipment.is_available,
            },
            status=status.HTTP_200_OK,
        )