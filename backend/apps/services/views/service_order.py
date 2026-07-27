# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.equipment.models import MeterReading
from apps.rentals.models import (
    RentalAssignment,
    RentalEquipment,
)
from apps.services.domain import (
    assign_technician,
    build_order_snapshot,
    change_service_status,
    create_service_checklist,
    validate_service_order_closure,
)
from apps.services.models import (
    ServiceMeterReading,
    ServiceOrder,
    ServiceTrackingSession,
)
from apps.services.serializers import (
    ServiceOrderListSerializer,
    ServiceOrderSerializer,
    ServiceTrackingSessionSerializer,
)

from .base import ArchiveRestoreMixin


RENTAL_SERVICE_ASSIGNMENT_STATUSES = (
    RentalAssignment.Status.INSTALLED,
    RentalAssignment.Status.ACTIVE,
    RentalAssignment.Status.REMOVAL_PENDING,
)


class ServiceOrderViewSet(
    ArchiveRestoreMixin,
    viewsets.ModelViewSet,
):
    permission_classes = [
        IsAuthenticated,
    ]

    queryset = (
        ServiceOrder.objects
        .select_related(
            "equipment",
            "equipment__equipment_model",
            "equipment__equipment_model__brand",
            "equipment__equipment_model__equipment_family",
            "assigned_technician",
            "assigned_by",
        )
        .all()
    )

    filterset_fields = (
        "service_origin",
        "status",
        "priority",
        "service_type",
        "result",
        "equipment",
        "assigned_technician",
        "requires_return_visit",
    )

    search_fields = (
        "code",
        "equipment_serial_number",
        "equipment_internal_code",
        "equipment_brand_name",
        "equipment_model_name",
        "customer_name",
        "customer_trade_name",
        "customer_document_number",
        "branch_name",
        "address",
        "contact_name",
        "contact_phone",
        "contract_reference",
        "rental_assignment_reference",
    )

    ordering_fields = (
        "requested_at",
        "scheduled_at",
        "assigned_at",
        "closed_at",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-requested_at",
        "-created_at",
    )

    def get_serializer_class(self):
        if self.action == "list":
            return ServiceOrderListSerializer

        return ServiceOrderSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        archived = str(
            self.request.query_params.get(
                "archived",
                "",
            )
            or ""
        ).strip().lower()

        if archived == "true":
            queryset = queryset.filter(
                archived_at__isnull=False,
            )

        elif archived != "all":
            queryset = queryset.filter(
                archived_at__isnull=True,
            )

        service_origin = str(
            self.request.query_params.get(
                "service_origin",
                "",
            )
            or ""
        ).strip()

        if service_origin:
            queryset = queryset.filter(
                service_origin=service_origin,
            )

        return queryset

    @staticmethod
    def _clean(value):
        return str(value or "").strip()

    @staticmethod
    def _equipment_information(equipment):
        equipment_model = getattr(
            equipment,
            "equipment_model",
            None,
        )

        brand = getattr(
            equipment_model,
            "brand",
            None,
        )

        equipment_family = getattr(
            equipment_model,
            "equipment_family",
            None,
        )

        family_name = (
            str(equipment_family)
            if equipment_family
            else str(
                getattr(
                    equipment_model,
                    "family",
                    "",
                )
                or ""
            ).strip()
        )

        return {
            "id": equipment.id,
            "equipment": equipment.id,
            "serial_number": (
                str(
                    getattr(
                        equipment,
                        "serial_number",
                        "",
                    )
                    or ""
                ).strip()
            ),
            "internal_code": (
                str(
                    getattr(
                        equipment,
                        "internal_code",
                        "",
                    )
                    or ""
                ).strip()
            ),
            "brand_name": (
                str(
                    getattr(
                        brand,
                        "name",
                        "",
                    )
                    or ""
                ).strip()
            ),
            "model_name": (
                str(
                    getattr(
                        equipment_model,
                        "name",
                        "",
                    )
                    or ""
                ).strip()
            ),
            "family_name": family_name,
            "technical_status": getattr(
                equipment,
                "technical_status",
                "",
            ),
            "technical_status_display": (
                equipment.get_technical_status_display()
                if hasattr(
                    equipment,
                    "get_technical_status_display",
                )
                else ""
            ),
            "commercial_status": getattr(
                equipment,
                "commercial_status",
                "",
            ),
            "commercial_status_display": (
                equipment.get_commercial_status_display()
                if hasattr(
                    equipment,
                    "get_commercial_status_display",
                )
                else ""
            ),
            "is_active": getattr(
                equipment,
                "is_active",
                True,
            ),
            "is_archived": bool(
                getattr(
                    equipment,
                    "archived_at",
                    None,
                )
            ),
        }

    @staticmethod
    def _build_option_label(
        equipment_data,
        customer_name="",
        branch_name="",
    ):
        brand_model = " ".join(
            value
            for value in (
                equipment_data.get(
                    "brand_name",
                    "",
                ),
                equipment_data.get(
                    "model_name",
                    "",
                ),
            )
            if value
        ).strip()

        identifier = (
            equipment_data.get(
                "serial_number",
                "",
            )
            or equipment_data.get(
                "internal_code",
                "",
            )
            or "Sin identificación"
        )

        parts = [
            identifier,
            brand_model,
            customer_name,
            branch_name,
        ]

        return " · ".join(
            value
            for value in parts
            if value
        )

    def _get_rental_equipment_options(
        self,
        search="",
    ):
        queryset = (
            RentalAssignment.objects
            .select_related(
                "contract",
                "rental_equipment",
                "rental_equipment__equipment",
                "rental_equipment__equipment__equipment_model",
                "rental_equipment__equipment__equipment_model__brand",
                (
                    "rental_equipment__equipment__"
                    "equipment_model__equipment_family"
                ),
                "customer",
                "branch",
                "contact",
            )
            .filter(
                status__in=(
                    RENTAL_SERVICE_ASSIGNMENT_STATUSES
                ),
                archived_at__isnull=True,
                rental_equipment__archived_at__isnull=True,
                rental_equipment__purpose=(
                    RentalEquipment
                    .EquipmentPurpose
                    .RENTAL
                ),
                rental_equipment__equipment__archived_at__isnull=True,
            )
            .order_by(
                "customer__legal_name",
                "branch__name",
                (
                    "rental_equipment__equipment__"
                    "equipment_model__brand__name"
                ),
                (
                    "rental_equipment__equipment__"
                    "equipment_model__name"
                ),
                (
                    "rental_equipment__equipment__"
                    "serial_number"
                ),
            )
        )

        if search:
            queryset = queryset.filter(
                Q(
                    rental_equipment__equipment__serial_number__icontains=search,
                )
                | Q(
                    rental_equipment__equipment__internal_code__icontains=search,
                )
                | Q(
                    rental_equipment__equipment__equipment_model__name__icontains=search,
                )
                | Q(
                    rental_equipment__equipment__equipment_model__brand__name__icontains=search,
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
                | Q(
                    branch__name__icontains=search,
                )
                | Q(
                    branch__address__icontains=search,
                )
                | Q(
                    contract__code__icontains=search,
                )
                | Q(
                    contract__contract_number__icontains=search,
                )
                | Q(
                    code__icontains=search,
                )
            ).distinct()

        options = []
        used_equipment = set()

        for assignment in queryset[:100]:
            rental_equipment = (
                assignment.rental_equipment
            )

            equipment = (
                rental_equipment.equipment
            )

            if equipment.id in used_equipment:
                continue

            used_equipment.add(
                equipment.id
            )

            snapshot = build_order_snapshot(
                equipment=equipment,
                service_origin=(
                    ServiceOrder
                    .ServiceOrigin
                    .RENTAL
                ),
            )

            equipment_data = (
                self._equipment_information(
                    equipment
                )
            )

            customer_name = (
                snapshot.get(
                    "customer_name",
                    "",
                )
            )

            branch_name = (
                snapshot.get(
                    "branch_name",
                    "",
                )
            )

            options.append(
                {
                    **equipment_data,
                    "service_origin": (
                        ServiceOrder
                        .ServiceOrigin
                        .RENTAL
                    ),
                    "service_origin_display": (
                        ServiceOrder
                        .ServiceOrigin
                        .RENTAL
                        .label
                    ),
                    "rental_equipment": (
                        rental_equipment.id
                    ),
                    "rental_assignment": (
                        assignment.id
                    ),
                    "rental_assignment_code": (
                        assignment.code
                    ),
                    "rental_status": (
                        assignment.status
                    ),
                    "rental_status_display": (
                        assignment
                        .get_status_display()
                    ),
                    "label": (
                        self._build_option_label(
                            equipment_data,
                            customer_name,
                            branch_name,
                        )
                    ),
                    "snapshot": snapshot,
                }
            )

        return options

    def _get_external_equipment_options(
        self,
        search="",
    ):
        queryset = (
            RentalEquipment.objects
            .select_related(
                "equipment",
                "equipment__equipment_model",
                "equipment__equipment_model__brand",
                (
                    "equipment__equipment_model__"
                    "equipment_family"
                ),
                "owner_customer",
            )
            .filter(
                purpose=(
                    RentalEquipment
                    .EquipmentPurpose
                    .CUSTOMER_SERVICE
                ),
                archived_at__isnull=True,
                equipment__archived_at__isnull=True,
            )
            .order_by(
                "owner_customer__legal_name",
                "equipment__equipment_model__brand__name",
                "equipment__equipment_model__name",
                "equipment__serial_number",
            )
        )

        if search:
            queryset = queryset.filter(
                Q(
                    equipment__serial_number__icontains=search,
                )
                | Q(
                    equipment__internal_code__icontains=search,
                )
                | Q(
                    equipment__equipment_model__name__icontains=search,
                )
                | Q(
                    equipment__equipment_model__brand__name__icontains=search,
                )
                | Q(
                    owner_customer__legal_name__icontains=search,
                )
                | Q(
                    owner_customer__trade_name__icontains=search,
                )
                | Q(
                    owner_customer__document_number__icontains=search,
                )
                | Q(
                    acquisition_document__icontains=search,
                )
                | Q(
                    acquisition_reference__icontains=search,
                )
                | Q(
                    notes__icontains=search,
                )
            ).distinct()

        options = []

        for rental_equipment in queryset[:100]:
            equipment = rental_equipment.equipment

            snapshot = build_order_snapshot(
                equipment=equipment,
                service_origin=(
                    ServiceOrder
                    .ServiceOrigin
                    .EXTERNAL
                ),
            )

            equipment_data = (
                self._equipment_information(
                    equipment
                )
            )

            owner_customer = (
                rental_equipment.owner_customer
            )

            owner_customer_name = ""

            if owner_customer:
                owner_customer_name = (
                    self._clean(
                        getattr(
                            owner_customer,
                            "legal_name",
                            "",
                        )
                    )
                    or self._clean(
                        getattr(
                            owner_customer,
                            "trade_name",
                            "",
                        )
                    )
                    or self._clean(
                        owner_customer
                    )
                )

            customer_name = (
                snapshot.get(
                    "customer_name",
                    "",
                )
                or owner_customer_name
            )

            branch_name = snapshot.get(
                "branch_name",
                "",
            )

            if (
                not snapshot.get(
                    "customer_name",
                    "",
                )
                and owner_customer
            ):
                snapshot.update(
                    {
                        "customer_code": (
                            self._clean(
                                getattr(
                                    owner_customer,
                                    "code",
                                    "",
                                )
                            )
                        ),
                        "customer_document_type": (
                            self._clean(
                                getattr(
                                    owner_customer,
                                    "document_type",
                                    "",
                                )
                            )
                        ),
                        "customer_document_number": (
                            self._clean(
                                getattr(
                                    owner_customer,
                                    "document_number",
                                    "",
                                )
                            )
                        ),
                        "customer_name": (
                            owner_customer_name
                        ),
                        "customer_trade_name": (
                            self._clean(
                                getattr(
                                    owner_customer,
                                    "trade_name",
                                    "",
                                )
                            )
                        ),
                    }
                )

            options.append(
                {
                    **equipment_data,
                    "service_origin": (
                        ServiceOrder
                        .ServiceOrigin
                        .EXTERNAL
                    ),
                    "service_origin_display": (
                        ServiceOrder
                        .ServiceOrigin
                        .EXTERNAL
                        .label
                    ),
                    "rental_equipment": (
                        rental_equipment.id
                    ),
                    "rental_purpose": (
                        rental_equipment.purpose
                    ),
                    "rental_purpose_display": (
                        rental_equipment
                        .get_purpose_display()
                    ),
                    "owner_customer": (
                        rental_equipment
                        .owner_customer_id
                    ),
                    "owner_customer_name": (
                        owner_customer_name
                    ),
                    "label": (
                        self._build_option_label(
                            equipment_data,
                            customer_name,
                            branch_name,
                        )
                    ),
                    "snapshot": snapshot,
                }
            )

        return options

    @action(
        detail=False,
        methods=["get"],
        url_path="equipment-options",
    )
    def equipment_options(
        self,
        request,
    ):
        service_origin = self._clean(
            request.query_params.get(
                "service_origin",
                "",
            )
        )

        search = self._clean(
            request.query_params.get(
                "search",
                "",
            )
        )

        if service_origin not in dict(
            ServiceOrder.ServiceOrigin.choices
        ):
            return Response(
                {
                    "service_origin": (
                        "Debe indicar un origen válido: "
                        "rental o external."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        if (
            service_origin
            == ServiceOrder.ServiceOrigin.RENTAL
        ):
            options = (
                self._get_rental_equipment_options(
                    search=search,
                )
            )

        else:
            options = (
                self._get_external_equipment_options(
                    search=search,
                )
            )

        return Response(
            {
                "service_origin": service_origin,
                "count": len(options),
                "results": options,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="equipment-snapshot",
    )
    def equipment_snapshot(
        self,
        request,
    ):
        equipment_id = self._clean(
            request.query_params.get(
                "equipment",
                "",
            )
        )

        service_origin = self._clean(
            request.query_params.get(
                "service_origin",
                "",
            )
        )

        if not equipment_id:
            return Response(
                {
                    "equipment": (
                        "Debe indicar la máquina."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        if service_origin not in dict(
            ServiceOrder.ServiceOrigin.choices
        ):
            return Response(
                {
                    "service_origin": (
                        "Debe indicar un origen válido."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        from apps.equipment.models import Equipment

        try:
            equipment = (
                Equipment.objects
                .select_related(
                    "equipment_model",
                    "equipment_model__brand",
                    (
                        "equipment_model__"
                        "equipment_family"
                    ),
                )
                .get(
                    pk=equipment_id,
                    archived_at__isnull=True,
                )
            )

        except Equipment.DoesNotExist:
            return Response(
                {
                    "equipment": (
                        "La máquina no existe "
                        "o está archivada."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        snapshot = build_order_snapshot(
            equipment=equipment,
            service_origin=service_origin,
        )

        if (
            service_origin
            == ServiceOrder.ServiceOrigin.RENTAL
            and not snapshot
        ):
            return Response(
                {
                    "equipment": (
                        "La máquina no tiene una "
                        "asignación de alquiler vigente."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        equipment_data = (
            self._equipment_information(
                equipment
            )
        )

        return Response(
            {
                **equipment_data,
                "service_origin": service_origin,
                "snapshot": snapshot,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="load-current-snapshot",
    )
    def load_current_snapshot(
        self,
        request,
        pk=None,
    ):
        order = self.get_object()

        if order.status not in {
            ServiceOrder.Status.DRAFT,
            ServiceOrder.Status.PENDING_ASSIGNMENT,
        }:
            return Response(
                {
                    "detail": (
                        "Solo se puede recargar "
                        "la información en una OS "
                        "en borrador o pendiente "
                        "de asignación."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        snapshot = build_order_snapshot(
            equipment=order.equipment,
            service_origin=(
                order.service_origin
            ),
        )

        if (
            order.service_origin
            == ServiceOrder.ServiceOrigin.RENTAL
            and not snapshot
        ):
            return Response(
                {
                    "detail": (
                        "La serie no tiene una "
                        "asignación de alquiler vigente."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        if (
            order.service_origin
            == ServiceOrder.ServiceOrigin.EXTERNAL
            and not snapshot
        ):
            return Response(
                {
                    "detail": (
                        "No se encontraron datos actuales "
                        "del cliente para la máquina externa."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        for field_name, value in snapshot.items():
            setattr(
                order,
                field_name,
                value,
            )

        order.updated_by = request.user
        order.save()

        return Response(
            self.get_serializer(
                order
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
    )
    def assign(
        self,
        request,
        pk=None,
    ):
        order = self.get_object()

        technician_id = request.data.get(
            "technician"
        )

        if not technician_id:
            return Response(
                {
                    "technician": (
                        "Debe indicar el técnico."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        User = get_user_model()

        try:
            technician = User.objects.get(
                pk=technician_id,
                is_active=True,
            )

            order = assign_technician(
                service_order=order,
                technician=technician,
                assigned_by=request.user,
                reason=request.data.get(
                    "reason",
                    "",
                ),
            )

        except User.DoesNotExist:
            return Response(
                {
                    "technician": (
                        "El técnico no existe "
                        "o está inactivo."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        except DjangoValidationError as exc:
            return Response(
                getattr(
                    exc,
                    "message_dict",
                    {
                        "detail": exc.messages,
                    },
                ),
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        return Response(
            self.get_serializer(
                order
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="change-status",
    )
    def change_status(
        self,
        request,
        pk=None,
    ):
        order = self.get_object()

        new_status = request.data.get(
            "status"
        )

        if new_status not in dict(
            ServiceOrder.Status.choices
        ):
            return Response(
                {
                    "status": (
                        "El estado no es válido."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        if (
            new_status
            == ServiceOrder.Status.CLOSED
            and order.status
            not in {
                ServiceOrder.Status.REQUIRES_RETURN,
                ServiceOrder.Status.FAILED_VISIT,
            }
        ):
            try:
                validate_service_order_closure(
                    order
                )

            except DjangoValidationError as exc:
                return Response(
                    getattr(
                        exc,
                        "message_dict",
                        {
                            "detail": exc.messages,
                        },
                    ),
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

        try:
            order = change_service_status(
                service_order=order,
                new_status=new_status,
                user=request.user,
                latitude=request.data.get(
                    "latitude"
                ),
                longitude=request.data.get(
                    "longitude"
                ),
                source=request.data.get(
                    "source",
                    "web",
                ),
                notes=request.data.get(
                    "notes",
                    "",
                ),
            )

        except DjangoValidationError as exc:
            return Response(
                getattr(
                    exc,
                    "message_dict",
                    {
                        "detail": exc.messages,
                    },
                ),
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        return Response(
            self.get_serializer(
                order
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="generate-checklist",
    )
    def generate_checklist(
        self,
        request,
        pk=None,
    ):
        order = self.get_object()

        checklist = create_service_checklist(
            order,
            request.user,
        )

        from apps.services.serializers import (
            ServiceChecklistSerializer,
        )

        serializer = (
            ServiceChecklistSerializer(
                checklist,
                context={
                    "request": request,
                },
            )
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="start-tracking",
    )
    def start_tracking(
        self,
        request,
        pk=None,
    ):
        order = self.get_object()

        if not order.assigned_technician_id:
            return Response(
                {
                    "detail": (
                        "La OS no tiene "
                        "técnico asignado."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        if (
            request.user
            != order.assigned_technician
            and not request.user.is_staff
        ):
            return Response(
                {
                    "detail": (
                        "Solo el técnico asignado "
                        "puede iniciar la ruta."
                    )
                },
                status=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        active_session_exists = (
            order.tracking_sessions
            .filter(
                status=(
                    ServiceTrackingSession
                    .Status
                    .ACTIVE
                ),
                archived_at__isnull=True,
            )
            .exists()
        )

        if active_session_exists:
            return Response(
                {
                    "detail": (
                        "La OS ya tiene "
                        "una sesión activa."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        session = (
            ServiceTrackingSession.objects
            .create(
                service_order=order,
                technician=(
                    order.assigned_technician
                ),
                started_at=timezone.now(),
                start_latitude=(
                    request.data.get(
                        "latitude"
                    )
                ),
                start_longitude=(
                    request.data.get(
                        "longitude"
                    )
                ),
                created_by=request.user,
                updated_by=request.user,
            )
        )

        return Response(
            ServiceTrackingSessionSerializer(
                session,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="stop-tracking",
    )
    def stop_tracking(
        self,
        request,
        pk=None,
    ):
        order = self.get_object()

        session = (
            order.tracking_sessions
            .filter(
                status=(
                    ServiceTrackingSession
                    .Status
                    .ACTIVE
                ),
                archived_at__isnull=True,
            )
            .order_by(
                "-started_at"
            )
            .first()
        )

        if not session:
            return Response(
                {
                    "detail": (
                        "No existe una "
                        "sesión activa."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        if (
            request.user
            != session.technician
            and not request.user.is_staff
        ):
            return Response(
                {
                    "detail": (
                        "Solo el técnico de la sesión "
                        "puede detener el tracking."
                    )
                },
                status=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        session.status = (
            ServiceTrackingSession
            .Status
            .COMPLETED
        )

        session.ended_at = timezone.now()

        session.end_latitude = (
            request.data.get(
                "latitude"
            )
        )

        session.end_longitude = (
            request.data.get(
                "longitude"
            )
        )

        session.close_reason = (
            request.data.get(
                "reason",
                "",
            )
        )

        session.updated_by = request.user
        session.save()

        return Response(
            ServiceTrackingSessionSerializer(
                session,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="apply-meter-reading",
    )
    @transaction.atomic
    def apply_meter_reading(
        self,
        request,
        pk=None,
    ):
        order = self.get_object()

        try:
            service_reading = (
                order.meter_reading
            )

        except ServiceMeterReading.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "La OS no tiene "
                        "contadores registrados."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        if (
            service_reading
            .applied_to_equipment_history
        ):
            return Response(
                {
                    "detail": (
                        "Los contadores "
                        "ya fueron aplicados."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        use_final = (
            service_reading.final_reading_at
            is not None
        )

        reading = MeterReading.objects.create(
            equipment=order.equipment,
            reading_date=(
                service_reading.final_reading_at
                if use_final
                else service_reading.initial_reading_at
            )
            or timezone.now(),
            reading_type=(
                MeterReading
                .ReadingType
                .NORMAL
            ),
            source=(
                MeterReading
                .Source
                .MOBILE_APP
            ),
            total_meter=(
                service_reading.final_total_meter
                if use_final
                else service_reading.initial_total_meter
            ),
            black_meter=(
                service_reading.final_black_meter
                if use_final
                else service_reading.initial_black_meter
            ),
            color_meter=(
                service_reading.final_color_meter
                if use_final
                else service_reading.initial_color_meter
            ),
            scan_meter=(
                service_reading.final_scan_meter
                if use_final
                else service_reading.initial_scan_meter
            ),
            registered_by=request.user,
            reference_type=(
                MeterReading
                .ReferenceType
                .MOBILE_APP
            ),
            reference_id=order.id,
            reference_number=order.code,
            created_by=request.user,
            updated_by=request.user,
        )

        service_reading.applied_to_equipment_history = True
        service_reading.updated_by = request.user

        service_reading.save(
            update_fields=[
                "applied_to_equipment_history",
                "updated_by",
                "updated_at",
            ]
        )

        return Response(
            {
                "detail": (
                    "Lectura aplicada al "
                    "historial del equipo."
                ),
                "meter_reading_id": reading.id,
            },
            status=status.HTTP_200_OK,
        )