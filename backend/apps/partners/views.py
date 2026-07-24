# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models import Q

from rest_framework import status
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    DocumentLookupLog,
    Partner,
    PartnerBranch,
    PartnerContact,
)
from .serializers import (
    ArchivePartnerBranchSerializer,
    ArchivePartnerContactSerializer,
    ArchivePartnerSerializer,
    DocumentLookupLogSerializer,
    PartnerBranchCreateUpdateSerializer,
    PartnerBranchDetailSerializer,
    PartnerBranchListSerializer,
    PartnerContactCreateUpdateSerializer,
    PartnerContactDetailSerializer,
    PartnerContactListSerializer,
    PartnerCreateUpdateSerializer,
    PartnerDetailSerializer,
    PartnerListSerializer,
)


def parse_boolean_query_param(value):
    """
    Convierte un parámetro de consulta en booleano.

    Devuelve:
    - True
    - False
    - None cuando no se reconoce el valor
    """

    if value is None:
        return None

    normalized = str(value).strip().lower()

    if normalized in (
        "1",
        "true",
        "yes",
        "si",
        "sí",
    ):
        return True

    if normalized in (
        "0",
        "false",
        "no",
    ):
        return False

    return None


class PartnerListCreateView(ListCreateAPIView):
    """
    Lista y crea clientes, proveedores y distribuidores.

    GET:
        Lista terceros activos por defecto.

    POST:
        Crea un tercero.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            Partner.objects
            .select_related(
                "advisor",
                "purchasing_manager",
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
                archived_at__isnull=True
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
                    code__icontains=search
                )
                | Q(
                    document_number__icontains=search
                )
                | Q(
                    legal_name__icontains=search
                )
                | Q(
                    trade_name__icontains=search
                )
                | Q(
                    first_names__icontains=search
                )
                | Q(
                    paternal_last_name__icontains=search
                )
                | Q(
                    maternal_last_name__icontains=search
                )
                | Q(
                    general_email__icontains=search
                )
                | Q(
                    billing_email__icontains=search
                )
                | Q(
                    general_phone__icontains=search
                )
                | Q(
                    mobile_phone__icontains=search
                )
                | Q(
                    contacts__first_names__icontains=search
                )
                | Q(
                    contacts__paternal_last_name__icontains=search
                )
                | Q(
                    contacts__maternal_last_name__icontains=search
                )
                | Q(
                    contacts__primary_email__icontains=search
                )
                | Q(
                    contacts__primary_mobile__icontains=search
                )
            ).distinct()

        country_code = str(
            self.request.query_params.get(
                "country_code",
                "",
            )
        ).strip().upper()

        if country_code:
            queryset = queryset.filter(
                country_code=country_code
            )

        document_type = str(
            self.request.query_params.get(
                "document_type",
                "",
            )
        ).strip()

        if document_type:
            queryset = queryset.filter(
                document_type=document_type
            )

        person_type = str(
            self.request.query_params.get(
                "person_type",
                "",
            )
        ).strip()

        if person_type:
            queryset = queryset.filter(
                person_type=person_type
            )

        classification = str(
            self.request.query_params.get(
                "classification",
                "",
            )
        ).strip()

        if classification:
            queryset = queryset.filter(
                classification=classification
            )

        advisor_id = str(
            self.request.query_params.get(
                "advisor",
                "",
            )
        ).strip()

        if advisor_id:
            queryset = queryset.filter(
                advisor_id=advisor_id
            )

        purchasing_manager_id = str(
            self.request.query_params.get(
                "purchasing_manager",
                "",
            )
        ).strip()

        if purchasing_manager_id:
            queryset = queryset.filter(
                purchasing_manager_id=(
                    purchasing_manager_id
                )
            )

        role = str(
            self.request.query_params.get(
                "role",
                "",
            )
        ).strip().lower()

        role_filters = {
            "rental_customer": (
                "is_rental_customer"
            ),
            "sales_customer": (
                "is_sales_customer"
            ),
            "service_customer": (
                "is_service_customer"
            ),
            "supplier": "is_supplier",
            "distributor": "is_distributor",
        }

        role_field = role_filters.get(role)

        if role_field:
            queryset = queryset.filter(
                **{
                    role_field: True,
                }
            )

        is_active = parse_boolean_query_param(
            self.request.query_params.get(
                "is_active"
            )
        )

        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active
            )

        is_commercially_blocked = (
            parse_boolean_query_param(
                self.request.query_params.get(
                    "is_commercially_blocked"
                )
            )
        )

        if is_commercially_blocked is not None:
            queryset = queryset.filter(
                is_commercially_blocked=(
                    is_commercially_blocked
                )
            )

        document_verified = (
            parse_boolean_query_param(
                self.request.query_params.get(
                    "document_verified"
                )
            )
        )

        if document_verified is not None:
            queryset = queryset.filter(
                document_verified=document_verified
            )

        return queryset.order_by(
            "legal_name",
            "trade_name",
            "first_names",
            "document_number",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PartnerCreateUpdateSerializer

        return PartnerListSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()


class PartnerDetailUpdateView(
    RetrieveUpdateAPIView
):
    """
    Consulta y modifica un tercero.

    GET:
        Devuelve el detalle completo.

    PUT/PATCH:
        Actualiza el tercero.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            Partner.objects
            .select_related(
                "advisor",
                "purchasing_manager",
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
            return PartnerCreateUpdateSerializer

        return PartnerDetailSerializer

    @transaction.atomic
    def perform_update(self, serializer):
        serializer.save()


class ArchivePartnerView(APIView):
    """
    Archiva un tercero sin eliminarlo físicamente.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        partner_id,
    ):
        partner = Partner.objects.filter(
            id=partner_id
        ).first()

        if not partner:
            return Response(
                {
                    "detail": (
                        "Cliente, proveedor o "
                        "distribuidor no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if partner.is_archived:
            return Response(
                {
                    "detail": (
                        "El registro ya se encuentra "
                        "archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ArchivePartnerSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        reason = serializer.validated_data.get(
            "reason",
            "",
        )

        partner.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Registro archivado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestorePartnerView(APIView):
    """
    Restaura un tercero archivado.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        partner_id,
    ):
        partner = Partner.objects.filter(
            id=partner_id
        ).first()

        if not partner:
            return Response(
                {
                    "detail": (
                        "Cliente, proveedor o "
                        "distribuidor no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not partner.is_archived:
            return Response(
                {
                    "detail": (
                        "El registro no se encuentra "
                        "archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        partner.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Registro restaurado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class PartnerBranchListCreateView(
    ListCreateAPIView
):
    """
    Lista y crea sedes o sucursales.

    Puede filtrarse por tercero mediante:

        ?partner=<uuid>
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            PartnerBranch.objects
            .select_related(
                "partner",
                "advisor",
                "partner__advisor",
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
                archived_at__isnull=True
            )

        partner_id = str(
            self.request.query_params.get(
                "partner",
                "",
            )
        ).strip()

        if partner_id:
            queryset = queryset.filter(
                partner_id=partner_id
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
                    name__icontains=search
                )
                | Q(
                    code__icontains=search
                )
                | Q(
                    address__icontains=search
                )
                | Q(
                    district__icontains=search
                )
                | Q(
                    province__icontains=search
                )
                | Q(
                    region__icontains=search
                )
                | Q(
                    partner__legal_name__icontains=search
                )
                | Q(
                    partner__trade_name__icontains=search
                )
                | Q(
                    partner__document_number__icontains=search
                )
            )

        branch_type = str(
            self.request.query_params.get(
                "branch_type",
                "",
            )
        ).strip()

        if branch_type:
            queryset = queryset.filter(
                branch_type=branch_type
            )

        is_main = parse_boolean_query_param(
            self.request.query_params.get(
                "is_main"
            )
        )

        if is_main is not None:
            queryset = queryset.filter(
                is_main=is_main
            )

        is_fiscal = parse_boolean_query_param(
            self.request.query_params.get(
                "is_fiscal"
            )
        )

        if is_fiscal is not None:
            queryset = queryset.filter(
                is_fiscal=is_fiscal
            )

        allows_equipment_installation = (
            parse_boolean_query_param(
                self.request.query_params.get(
                    "allows_equipment_installation"
                )
            )
        )

        if (
            allows_equipment_installation
            is not None
        ):
            queryset = queryset.filter(
                allows_equipment_installation=(
                    allows_equipment_installation
                )
            )

        is_active = parse_boolean_query_param(
            self.request.query_params.get(
                "is_active"
            )
        )

        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active
            )

        return queryset.order_by(
            "partner__legal_name",
            "partner__trade_name",
            "-is_main",
            "name",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return (
                PartnerBranchCreateUpdateSerializer
            )

        return PartnerBranchListSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()


class PartnerBranchDetailUpdateView(
    RetrieveUpdateAPIView
):
    """
    Consulta y modifica una sede.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            PartnerBranch.objects
            .select_related(
                "partner",
                "advisor",
                "partner__advisor",
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
                PartnerBranchCreateUpdateSerializer
            )

        return PartnerBranchDetailSerializer

    @transaction.atomic
    def perform_update(self, serializer):
        serializer.save()


class ArchivePartnerBranchView(APIView):
    """
    Archiva una sede o sucursal.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        branch_id,
    ):
        branch = PartnerBranch.objects.filter(
            id=branch_id
        ).first()

        if not branch:
            return Response(
                {
                    "detail": (
                        "Sucursal o sede no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if branch.is_archived:
            return Response(
                {
                    "detail": (
                        "La sede ya se encuentra archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            ArchivePartnerBranchSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        reason = serializer.validated_data.get(
            "reason",
            "",
        )

        branch.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Sucursal archivada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestorePartnerBranchView(APIView):
    """
    Restaura una sede archivada.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        branch_id,
    ):
        branch = PartnerBranch.objects.filter(
            id=branch_id
        ).first()

        if not branch:
            return Response(
                {
                    "detail": (
                        "Sucursal o sede no encontrada."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not branch.is_archived:
            return Response(
                {
                    "detail": (
                        "La sede no se encuentra archivada."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        branch.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Sucursal restaurada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class PartnerContactListCreateView(
    ListCreateAPIView
):
    """
    Lista y crea contactos.

    Puede filtrarse por:

        ?partner=<uuid>
        ?branch=<uuid>
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            PartnerContact.objects
            .select_related(
                "partner",
                "branch",
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
                archived_at__isnull=True
            )

        partner_id = str(
            self.request.query_params.get(
                "partner",
                "",
            )
        ).strip()

        if partner_id:
            queryset = queryset.filter(
                partner_id=partner_id
            )

        branch_id = str(
            self.request.query_params.get(
                "branch",
                "",
            )
        ).strip()

        if branch_id:
            queryset = queryset.filter(
                branch_id=branch_id
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
                    first_names__icontains=search
                )
                | Q(
                    paternal_last_name__icontains=search
                )
                | Q(
                    maternal_last_name__icontains=search
                )
                | Q(
                    job_title__icontains=search
                )
                | Q(
                    primary_email__icontains=search
                )
                | Q(
                    secondary_email__icontains=search
                )
                | Q(
                    primary_mobile__icontains=search
                )
                | Q(
                    secondary_mobile__icontains=search
                )
                | Q(
                    whatsapp_number__icontains=search
                )
                | Q(
                    document_number__icontains=search
                )
                | Q(
                    partner__legal_name__icontains=search
                )
                | Q(
                    partner__trade_name__icontains=search
                )
                | Q(
                    partner__document_number__icontains=search
                )
            )

        area = str(
            self.request.query_params.get(
                "area",
                "",
            )
        ).strip()

        if area:
            queryset = queryset.filter(
                area=area
            )

        is_primary = parse_boolean_query_param(
            self.request.query_params.get(
                "is_primary"
            )
        )

        if is_primary is not None:
            queryset = queryset.filter(
                is_primary=is_primary
            )

        is_active = parse_boolean_query_param(
            self.request.query_params.get(
                "is_active"
            )
        )

        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active
            )

        receives_billing = (
            parse_boolean_query_param(
                self.request.query_params.get(
                    "receives_billing"
                )
            )
        )

        if receives_billing is not None:
            queryset = queryset.filter(
                receives_billing=receives_billing
            )

        receives_meter_requests = (
            parse_boolean_query_param(
                self.request.query_params.get(
                    "receives_meter_requests"
                )
            )
        )

        if receives_meter_requests is not None:
            queryset = queryset.filter(
                receives_meter_requests=(
                    receives_meter_requests
                )
            )

        receives_service_notifications = (
            parse_boolean_query_param(
                self.request.query_params.get(
                    "receives_service_notifications"
                )
            )
        )

        if (
            receives_service_notifications
            is not None
        ):
            queryset = queryset.filter(
                receives_service_notifications=(
                    receives_service_notifications
                )
            )

        return queryset.order_by(
            "partner__legal_name",
            "partner__trade_name",
            "-is_primary",
            "first_names",
            "paternal_last_name",
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return (
                PartnerContactCreateUpdateSerializer
            )

        return PartnerContactListSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()


class PartnerContactDetailUpdateView(
    RetrieveUpdateAPIView
):
    """
    Consulta y modifica un contacto.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    lookup_field = "id"

    def get_queryset(self):
        return (
            PartnerContact.objects
            .select_related(
                "partner",
                "branch",
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
                PartnerContactCreateUpdateSerializer
            )

        return PartnerContactDetailSerializer

    @transaction.atomic
    def perform_update(self, serializer):
        serializer.save()


class ArchivePartnerContactView(APIView):
    """
    Archiva un contacto.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        contact_id,
    ):
        contact = PartnerContact.objects.filter(
            id=contact_id
        ).first()

        if not contact:
            return Response(
                {
                    "detail": (
                        "Contacto no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if contact.is_archived:
            return Response(
                {
                    "detail": (
                        "El contacto ya se encuentra "
                        "archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            ArchivePartnerContactSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        reason = serializer.validated_data.get(
            "reason",
            "",
        )

        contact.archive(
            user=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Contacto archivado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class RestorePartnerContactView(APIView):
    """
    Restaura un contacto archivado.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        contact_id,
    ):
        contact = PartnerContact.objects.filter(
            id=contact_id
        ).first()

        if not contact:
            return Response(
                {
                    "detail": (
                        "Contacto no encontrado."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not contact.is_archived:
            return Response(
                {
                    "detail": (
                        "El contacto no se encuentra "
                        "archivado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        contact.restore(
            user=request.user,
        )

        return Response(
            {
                "detail": (
                    "Contacto restaurado correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


class DocumentLookupLogListView(ListAPIView):
    """
    Lista el historial de consultas DNI y RUC.

    Este endpoint es de solo lectura.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        DocumentLookupLogSerializer
    )

    def get_queryset(self):
        queryset = (
            DocumentLookupLog.objects
            .select_related(
                "requested_by",
                "partner",
                "created_by",
                "updated_by",
            )
            .all()
        )

        document_type = str(
            self.request.query_params.get(
                "document_type",
                "",
            )
        ).strip()

        if document_type:
            queryset = queryset.filter(
                document_type=document_type
            )

        document_number = str(
            self.request.query_params.get(
                "document_number",
                "",
            )
        ).replace(
            " ",
            "",
        ).strip()

        if document_number:
            queryset = queryset.filter(
                document_number=document_number
            )

        status_value = str(
            self.request.query_params.get(
                "status",
                "",
            )
        ).strip()

        if status_value:
            queryset = queryset.filter(
                status=status_value
            )

        provider = str(
            self.request.query_params.get(
                "provider",
                "",
            )
        ).strip()

        if provider:
            queryset = queryset.filter(
                provider=provider
            )

        requested_by = str(
            self.request.query_params.get(
                "requested_by",
                "",
            )
        ).strip()

        if requested_by:
            queryset = queryset.filter(
                requested_by_id=requested_by
            )

        partner_id = str(
            self.request.query_params.get(
                "partner",
                "",
            )
        ).strip()

        if partner_id:
            queryset = queryset.filter(
                partner_id=partner_id
            )

        is_successful = parse_boolean_query_param(
            self.request.query_params.get(
                "is_successful"
            )
        )

        if is_successful is not None:
            queryset = queryset.filter(
                is_successful=is_successful
            )

        return queryset.order_by(
            "-created_at"
        )