# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from .models import (
    DocumentLookupLog,
    Partner,
    PartnerBranch,
    PartnerContact,
)


def convert_django_validation_error(exc):
    """
    Convierte un ValidationError de Django en un formato
    compatible con Django REST Framework.
    """

    if hasattr(exc, "message_dict"):
        return exc.message_dict

    if hasattr(exc, "messages"):
        return {
            "detail": exc.messages
        }

    return {
        "detail": str(exc)
    }


def get_authenticated_user(serializer):
    """
    Obtiene el usuario autenticado desde el contexto
    del serializer.
    """

    request = serializer.context.get("request")

    if (
        request
        and request.user
        and request.user.is_authenticated
    ):
        return request.user

    return None


class PartnerListSerializer(serializers.ModelSerializer):
    """
    Serializer reducido para listar clientes, proveedores
    y distribuidores.
    """

    display_name = serializers.CharField(
        read_only=True,
    )

    commercial_roles = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )

    document_type_name = serializers.CharField(
        source="get_document_type_display",
        read_only=True,
    )

    person_type_name = serializers.CharField(
        source="get_person_type_display",
        read_only=True,
    )

    classification_name = serializers.CharField(
        source="get_classification_display",
        read_only=True,
    )

    advisor_name = serializers.CharField(
        source="advisor.full_name",
        read_only=True,
        allow_null=True,
    )

    purchasing_manager_name = serializers.CharField(
        source="purchasing_manager.full_name",
        read_only=True,
        allow_null=True,
    )

    is_foreign = serializers.BooleanField(
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    branches_count = serializers.SerializerMethodField()
    contacts_count = serializers.SerializerMethodField()

    class Meta:
        model = Partner

        fields = (
            "id",
            "code",
            "display_name",
            "person_type",
            "person_type_name",
            "country_code",
            "country_name",
            "is_foreign",
            "document_type",
            "document_type_name",
            "document_number",
            "legal_name",
            "trade_name",
            "first_names",
            "paternal_last_name",
            "maternal_last_name",
            "classification",
            "classification_name",
            "commercial_roles",
            "is_rental_customer",
            "is_sales_customer",
            "is_service_customer",
            "is_supplier",
            "is_distributor",
            "advisor",
            "advisor_name",
            "purchasing_manager",
            "purchasing_manager_name",
            "general_phone",
            "mobile_phone",
            "general_email",
            "sunat_status",
            "sunat_condition",
            "document_verified",
            "preferred_currency",
            "is_commercially_blocked",
            "is_active",
            "is_archived",
            "branches_count",
            "contacts_count",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_branches_count(self, obj):
        return obj.branches.filter(
            archived_at__isnull=True,
        ).count()

    def get_contacts_count(self, obj):
        return obj.contacts.filter(
            archived_at__isnull=True,
        ).count()


class PartnerDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo de un cliente, proveedor
    o distribuidor.
    """

    display_name = serializers.CharField(
        read_only=True,
    )

    commercial_roles = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )

    has_commercial_role = serializers.BooleanField(
        read_only=True,
    )

    requires_advisor = serializers.BooleanField(
        read_only=True,
    )

    is_foreign = serializers.BooleanField(
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    person_type_name = serializers.CharField(
        source="get_person_type_display",
        read_only=True,
    )

    document_type_name = serializers.CharField(
        source="get_document_type_display",
        read_only=True,
    )

    classification_name = serializers.CharField(
        source="get_classification_display",
        read_only=True,
    )

    preferred_currency_name = serializers.CharField(
        source="get_preferred_currency_display",
        read_only=True,
    )

    document_source_name = serializers.CharField(
        source="get_document_source_display",
        read_only=True,
    )

    advisor_name = serializers.CharField(
        source="advisor.full_name",
        read_only=True,
        allow_null=True,
    )

    purchasing_manager_name = serializers.CharField(
        source="purchasing_manager.full_name",
        read_only=True,
        allow_null=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.full_name",
        read_only=True,
        allow_null=True,
    )

    updated_by_name = serializers.CharField(
        source="updated_by.full_name",
        read_only=True,
        allow_null=True,
    )

    archived_by_name = serializers.CharField(
        source="archived_by.full_name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Partner

        fields = (
            "id",
            "code",
            "person_type",
            "person_type_name",
            "country_code",
            "country_name",
            "is_foreign",
            "document_type",
            "document_type_name",
            "document_number",
            "legal_name",
            "trade_name",
            "first_names",
            "paternal_last_name",
            "maternal_last_name",
            "display_name",
            "classification",
            "classification_name",
            "is_rental_customer",
            "is_sales_customer",
            "is_service_customer",
            "is_supplier",
            "is_distributor",
            "commercial_roles",
            "has_commercial_role",
            "requires_advisor",
            "advisor",
            "advisor_name",
            "purchasing_manager",
            "purchasing_manager_name",
            "general_phone",
            "mobile_phone",
            "general_email",
            "billing_email",
            "website",
            "fiscal_address",
            "address_reference",
            "ubigeo",
            "road_type",
            "road_name",
            "zone_code",
            "zone_type",
            "address_number",
            "interior",
            "lot",
            "apartment",
            "block",
            "kilometer",
            "district",
            "province",
            "region",
            "postal_code",
            "sunat_status",
            "sunat_condition",
            "taxpayer_type",
            "economic_activity",
            "employee_count",
            "billing_type",
            "accounting_type",
            "foreign_trade",
            "is_withholding_agent",
            "document_source",
            "document_source_name",
            "document_verified",
            "document_verified_at",
            "last_document_lookup_at",
            "preferred_currency",
            "preferred_currency_name",
            "preferred_language",
            "payment_terms",
            "credit_days",
            "credit_limit",
            "requires_purchase_order",
            "requires_service_conformity",
            "requires_delivery_guide",
            "is_commercially_blocked",
            "commercial_block_reason",
            "is_active",
            "notes",
            "is_archived",
            "archived_at",
            "archived_reason",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_by",
            "archived_by_name",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "display_name",
            "commercial_roles",
            "has_commercial_role",
            "requires_advisor",
            "is_foreign",
            "person_type_name",
            "document_type_name",
            "classification_name",
            "preferred_currency_name",
            "document_source_name",
            "document_verified_at",
            "last_document_lookup_at",
            "is_archived",
            "archived_at",
            "archived_reason",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_by",
            "archived_by_name",
            "created_at",
            "updated_at",
        )


class PartnerCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Creación y modificación de clientes, proveedores
    y distribuidores.
    """

    class Meta:
        model = Partner

        fields = (
            "code",
            "person_type",
            "country_code",
            "country_name",
            "document_type",
            "document_number",
            "legal_name",
            "trade_name",
            "first_names",
            "paternal_last_name",
            "maternal_last_name",
            "classification",
            "is_rental_customer",
            "is_sales_customer",
            "is_service_customer",
            "is_supplier",
            "is_distributor",
            "advisor",
            "purchasing_manager",
            "general_phone",
            "mobile_phone",
            "general_email",
            "billing_email",
            "website",
            "fiscal_address",
            "address_reference",
            "ubigeo",
            "road_type",
            "road_name",
            "zone_code",
            "zone_type",
            "address_number",
            "interior",
            "lot",
            "apartment",
            "block",
            "kilometer",
            "district",
            "province",
            "region",
            "postal_code",
            "sunat_status",
            "sunat_condition",
            "taxpayer_type",
            "economic_activity",
            "employee_count",
            "billing_type",
            "accounting_type",
            "foreign_trade",
            "is_withholding_agent",
            "document_source",
            "document_verified",
            "preferred_currency",
            "preferred_language",
            "payment_terms",
            "credit_days",
            "credit_limit",
            "requires_purchase_order",
            "requires_service_conformity",
            "requires_delivery_guide",
            "is_commercially_blocked",
            "commercial_block_reason",
            "is_active",
            "notes",
        )

    def validate_code(self, value):
        code = str(
            value or ""
        ).strip().upper()

        if not code:
            return None

        queryset = Partner.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un tercero con este código interno."
            )

        return code

    def validate_document_number(self, value):
        return str(
            value or ""
        ).replace(
            " ",
            "",
        ).strip().upper()

    def validate_country_code(self, value):
        country_code = str(
            value or ""
        ).strip().upper()

        if len(country_code) != 2:
            raise serializers.ValidationError(
                "El código del país debe contener "
                "exactamente dos letras."
            )

        return country_code

    def validate_general_email(self, value):
        return str(
            value or ""
        ).strip().lower()

    def validate_billing_email(self, value):
        return str(
            value or ""
        ).strip().lower()

    def validate(self, attrs):
        instance = self.instance

        values = {}

        if instance:
            for field in self.Meta.fields:
                values[field] = getattr(
                    instance,
                    field,
                    None,
                )

        values.update(attrs)

        has_role = any(
            (
                values.get(
                    "is_rental_customer",
                    False,
                ),
                values.get(
                    "is_sales_customer",
                    False,
                ),
                values.get(
                    "is_service_customer",
                    False,
                ),
                values.get(
                    "is_supplier",
                    False,
                ),
                values.get(
                    "is_distributor",
                    False,
                ),
            )
        )

        if not has_role:
            raise serializers.ValidationError(
                {
                    "roles": (
                        "Debes seleccionar al menos un tipo: "
                        "cliente, proveedor o distribuidor."
                    )
                }
            )

        requires_advisor = any(
            (
                values.get(
                    "is_rental_customer",
                    False,
                ),
                values.get(
                    "is_sales_customer",
                    False,
                ),
                values.get(
                    "is_service_customer",
                    False,
                ),
                values.get(
                    "is_distributor",
                    False,
                ),
            )
        )

        if (
            requires_advisor
            and not values.get("advisor")
        ):
            raise serializers.ValidationError(
                {
                    "advisor": (
                        "Debes asignar una asesora o "
                        "responsable comercial."
                    )
                }
            )

        is_supplier_only = (
            values.get(
                "is_supplier",
                False,
            )
            and not requires_advisor
        )

        if (
            is_supplier_only
            and not values.get(
                "purchasing_manager"
            )
        ):
            raise serializers.ValidationError(
                {
                    "purchasing_manager": (
                        "Debes asignar un responsable "
                        "de compras al proveedor."
                    )
                }
            )

        country_code = str(
            values.get(
                "country_code",
                "",
            )
            or ""
        ).strip().upper()

        document_type = values.get(
            "document_type"
        )

        if (
            country_code == "PE"
            and document_type
            in (
                Partner.DOCUMENT_EIN,
                Partner.DOCUMENT_TAX_ID,
                Partner.DOCUMENT_REGISTRATION,
            )
        ):
            raise serializers.ValidationError(
                {
                    "document_type": (
                        "Ese tipo de documento corresponde "
                        "a una entidad extranjera."
                    )
                }
            )

        if (
            country_code != "PE"
            and document_type
            in (
                Partner.DOCUMENT_DNI,
                Partner.DOCUMENT_RUC,
            )
        ):
            raise serializers.ValidationError(
                {
                    "document_type": (
                        "Para una entidad extranjera selecciona "
                        "EIN, Tax ID, registro empresarial, "
                        "pasaporte u otro documento."
                    )
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(self)

        partner = Partner(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            partner.full_clean()
            partner.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return partner

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        actor = get_authenticated_user(self)

        for field, value in validated_data.items():
            setattr(
                instance,
                field,
                value,
            )

        if actor:
            instance.updated_by = actor

        try:
            instance.full_clean()
            instance.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return instance


class ArchivePartnerSerializer(serializers.Serializer):
    """
    Motivo utilizado para archivar un tercero.
    """

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )


class PartnerBranchListSerializer(serializers.ModelSerializer):
    """
    Serializer reducido de sucursales y sedes.
    """

    partner_name = serializers.CharField(
        source="partner.display_name",
        read_only=True,
    )

    branch_type_name = serializers.CharField(
        source="get_branch_type_display",
        read_only=True,
    )

    display_name = serializers.CharField(
        read_only=True,
    )

    is_temporary = serializers.BooleanField(
        read_only=True,
    )

    effective_advisor_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = PartnerBranch

        fields = (
            "id",
            "partner",
            "partner_name",
            "code",
            "name",
            "display_name",
            "branch_type",
            "branch_type_name",
            "is_main",
            "is_fiscal",
            "is_temporary",
            "allows_equipment_installation",
            "allows_deliveries",
            "advisor",
            "effective_advisor_name",
            "country_code",
            "country_name",
            "address",
            "district",
            "province",
            "region",
            "general_phone",
            "mobile_phone",
            "general_email",
            "start_date",
            "end_date",
            "is_active",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_effective_advisor_name(self, obj):
        advisor = obj.effective_advisor

        if not advisor:
            return None

        return advisor.full_name


class PartnerBranchDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo de una sucursal o sede.
    """

    partner_name = serializers.CharField(
        source="partner.display_name",
        read_only=True,
    )

    branch_type_name = serializers.CharField(
        source="get_branch_type_display",
        read_only=True,
    )

    display_name = serializers.CharField(
        read_only=True,
    )

    is_temporary = serializers.BooleanField(
        read_only=True,
    )

    coordinates = serializers.JSONField(
        read_only=True,
    )

    effective_advisor_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.full_name",
        read_only=True,
        allow_null=True,
    )

    updated_by_name = serializers.CharField(
        source="updated_by.full_name",
        read_only=True,
        allow_null=True,
    )

    archived_by_name = serializers.CharField(
        source="archived_by.full_name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = PartnerBranch

        fields = (
            "id",
            "partner",
            "partner_name",
            "code",
            "name",
            "display_name",
            "branch_type",
            "branch_type_name",
            "is_main",
            "is_fiscal",
            "is_temporary",
            "allows_equipment_installation",
            "allows_deliveries",
            "advisor",
            "effective_advisor_name",
            "country_code",
            "country_name",
            "address",
            "address_reference",
            "ubigeo",
            "road_type",
            "road_name",
            "zone_code",
            "zone_type",
            "address_number",
            "interior",
            "lot",
            "apartment",
            "block",
            "kilometer",
            "district",
            "province",
            "region",
            "postal_code",
            "latitude",
            "longitude",
            "coordinates",
            "general_phone",
            "mobile_phone",
            "general_email",
            "operating_hours",
            "access_instructions",
            "installation_notes",
            "start_date",
            "end_date",
            "is_active",
            "notes",
            "is_archived",
            "archived_at",
            "archived_reason",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_by",
            "archived_by_name",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "partner_name",
            "display_name",
            "branch_type_name",
            "is_temporary",
            "coordinates",
            "effective_advisor_name",
            "is_archived",
            "archived_at",
            "archived_reason",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_by",
            "archived_by_name",
            "created_at",
            "updated_at",
        )

    def get_effective_advisor_name(self, obj):
        advisor = obj.effective_advisor

        if not advisor:
            return None

        return advisor.full_name


class PartnerBranchCreateUpdateSerializer(
    serializers.ModelSerializer
):
    """
    Creación y modificación de sucursales.
    """

    class Meta:
        model = PartnerBranch

        fields = (
            "partner",
            "code",
            "name",
            "branch_type",
            "is_main",
            "is_fiscal",
            "allows_equipment_installation",
            "allows_deliveries",
            "advisor",
            "country_code",
            "country_name",
            "address",
            "address_reference",
            "ubigeo",
            "road_type",
            "road_name",
            "zone_code",
            "zone_type",
            "address_number",
            "interior",
            "lot",
            "apartment",
            "block",
            "kilometer",
            "district",
            "province",
            "region",
            "postal_code",
            "latitude",
            "longitude",
            "general_phone",
            "mobile_phone",
            "general_email",
            "operating_hours",
            "access_instructions",
            "installation_notes",
            "start_date",
            "end_date",
            "is_active",
            "notes",
        )

    def validate_code(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_country_code(self, value):
        country_code = str(
            value or ""
        ).strip().upper()

        if len(country_code) != 2:
            raise serializers.ValidationError(
                "El código del país debe contener "
                "exactamente dos letras."
            )

        return country_code

    def validate_general_email(self, value):
        return str(
            value or ""
        ).strip().lower()

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(self)

        branch = PartnerBranch(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            branch.full_clean()
            branch.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return branch

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        actor = get_authenticated_user(self)

        for field, value in validated_data.items():
            setattr(
                instance,
                field,
                value,
            )

        if actor:
            instance.updated_by = actor

        try:
            instance.full_clean()
            instance.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return instance


class ArchivePartnerBranchSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )


class PartnerContactListSerializer(
    serializers.ModelSerializer
):
    """
    Serializer reducido de contactos.
    """

    partner_name = serializers.CharField(
        source="partner.display_name",
        read_only=True,
    )

    branch_name = serializers.CharField(
        source="branch.name",
        read_only=True,
        allow_null=True,
    )

    full_name = serializers.CharField(
        read_only=True,
    )

    display_name = serializers.CharField(
        read_only=True,
    )

    area_name = serializers.CharField(
        source="get_area_display",
        read_only=True,
    )

    notification_roles = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )

    available_email = serializers.CharField(
        read_only=True,
    )

    available_phone = serializers.CharField(
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = PartnerContact

        fields = (
            "id",
            "partner",
            "partner_name",
            "branch",
            "branch_name",
            "full_name",
            "display_name",
            "job_title",
            "area",
            "area_name",
            "primary_email",
            "primary_mobile",
            "whatsapp_number",
            "has_whatsapp",
            "is_primary",
            "is_legal_representative",
            "is_branch_manager",
            "notification_roles",
            "available_email",
            "available_phone",
            "is_active",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class PartnerContactDetailSerializer(
    serializers.ModelSerializer
):
    """
    Serializer completo de un contacto.
    """

    partner_name = serializers.CharField(
        source="partner.display_name",
        read_only=True,
    )

    branch_name = serializers.CharField(
        source="branch.name",
        read_only=True,
        allow_null=True,
    )

    full_name = serializers.CharField(
        read_only=True,
    )

    display_name = serializers.CharField(
        read_only=True,
    )

    area_name = serializers.CharField(
        source="get_area_display",
        read_only=True,
    )

    document_type_name = serializers.CharField(
        source="get_document_type_display",
        read_only=True,
    )

    preferred_contact_method_name = serializers.CharField(
        source="get_preferred_contact_method_display",
        read_only=True,
    )

    notification_roles = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )

    available_email = serializers.CharField(
        read_only=True,
    )

    available_phone = serializers.CharField(
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.full_name",
        read_only=True,
        allow_null=True,
    )

    updated_by_name = serializers.CharField(
        source="updated_by.full_name",
        read_only=True,
        allow_null=True,
    )

    archived_by_name = serializers.CharField(
        source="archived_by.full_name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = PartnerContact

        fields = (
            "id",
            "partner",
            "partner_name",
            "branch",
            "branch_name",
            "document_type",
            "document_type_name",
            "document_number",
            "first_names",
            "paternal_last_name",
            "maternal_last_name",
            "full_name",
            "display_name",
            "job_title",
            "area",
            "area_name",
            "primary_email",
            "secondary_email",
            "work_phone",
            "work_extension",
            "primary_mobile",
            "secondary_mobile",
            "whatsapp_number",
            "has_whatsapp",
            "is_primary",
            "is_legal_representative",
            "is_branch_manager",
            "receives_contracts",
            "receives_billing",
            "receives_collections",
            "receives_purchase_orders",
            "receives_delivery_documents",
            "receives_meter_requests",
            "receives_service_notifications",
            "receives_incident_notifications",
            "receives_commercial_notifications",
            "can_authorize_equipment_entry",
            "can_authorize_equipment_removal",
            "can_sign_documents",
            "preferred_contact_method",
            "preferred_contact_method_name",
            "contact_schedule",
            "notification_roles",
            "available_email",
            "available_phone",
            "is_active",
            "notes",
            "is_archived",
            "archived_at",
            "archived_reason",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_by",
            "archived_by_name",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "partner_name",
            "branch_name",
            "document_type_name",
            "full_name",
            "display_name",
            "area_name",
            "preferred_contact_method_name",
            "notification_roles",
            "available_email",
            "available_phone",
            "is_archived",
            "archived_at",
            "archived_reason",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_by",
            "archived_by_name",
            "created_at",
            "updated_at",
        )


class PartnerContactCreateUpdateSerializer(
    serializers.ModelSerializer
):
    """
    Creación y modificación de contactos.
    """

    class Meta:
        model = PartnerContact

        fields = (
            "partner",
            "branch",
            "document_type",
            "document_number",
            "first_names",
            "paternal_last_name",
            "maternal_last_name",
            "job_title",
            "area",
            "primary_email",
            "secondary_email",
            "work_phone",
            "work_extension",
            "primary_mobile",
            "secondary_mobile",
            "whatsapp_number",
            "has_whatsapp",
            "is_primary",
            "is_legal_representative",
            "is_branch_manager",
            "receives_contracts",
            "receives_billing",
            "receives_collections",
            "receives_purchase_orders",
            "receives_delivery_documents",
            "receives_meter_requests",
            "receives_service_notifications",
            "receives_incident_notifications",
            "receives_commercial_notifications",
            "can_authorize_equipment_entry",
            "can_authorize_equipment_removal",
            "can_sign_documents",
            "preferred_contact_method",
            "contact_schedule",
            "is_active",
            "notes",
        )

    def validate_document_number(self, value):
        return str(
            value or ""
        ).replace(
            " ",
            "",
        ).strip().upper()

    def validate_primary_email(self, value):
        return str(
            value or ""
        ).strip().lower()

    def validate_secondary_email(self, value):
        return str(
            value or ""
        ).strip().lower()

    def validate(self, attrs):
        instance = self.instance

        partner = attrs.get(
            "partner",
            getattr(
                instance,
                "partner",
                None,
            ),
        )

        branch = attrs.get(
            "branch",
            getattr(
                instance,
                "branch",
                None,
            ),
        )

        if (
            branch
            and partner
            and branch.partner_id != partner.id
        ):
            raise serializers.ValidationError(
                {
                    "branch": (
                        "La sede seleccionada no pertenece "
                        "al tercero indicado."
                    )
                }
            )

        is_branch_manager = attrs.get(
            "is_branch_manager",
            getattr(
                instance,
                "is_branch_manager",
                False,
            ),
        )

        if (
            is_branch_manager
            and not branch
        ):
            raise serializers.ValidationError(
                {
                    "branch": (
                        "Para marcarlo como responsable "
                        "de sede debes seleccionar una sede."
                    )
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(self)

        contact = PartnerContact(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            contact.full_clean()
            contact.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return contact

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        actor = get_authenticated_user(self)

        for field, value in validated_data.items():
            setattr(
                instance,
                field,
                value,
            )

        if actor:
            instance.updated_by = actor

        try:
            instance.full_clean()
            instance.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return instance


class ArchivePartnerContactSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )


class DocumentLookupLogSerializer(
    serializers.ModelSerializer
):
    """
    Serializer de solo lectura para el historial
    de consultas de documentos.
    """

    display_document = serializers.CharField(
        read_only=True,
    )

    document_type_name = serializers.CharField(
        source="get_document_type_display",
        read_only=True,
    )

    provider_name_display = serializers.CharField(
        source="get_provider_display",
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    result_action_name = serializers.CharField(
        source="get_result_action_display",
        read_only=True,
    )

    requested_by_name = serializers.CharField(
        source="requested_by.full_name",
        read_only=True,
        allow_null=True,
    )

    partner_name = serializers.CharField(
        source="partner.display_name",
        read_only=True,
        allow_null=True,
    )

    has_response = serializers.BooleanField(
        read_only=True,
    )

    was_applied = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = DocumentLookupLog

        fields = (
            "id",
            "document_type",
            "document_type_name",
            "document_number",
            "display_document",
            "provider",
            "provider_name",
            "provider_name_display",
            "requested_by",
            "requested_by_name",
            "partner",
            "partner_name",
            "status",
            "status_name",
            "result_action",
            "result_action_name",
            "http_status_code",
            "is_successful",
            "response_data",
            "normalized_data",
            "request_data",
            "error_message",
            "response_time_ms",
            "cache_used",
            "provider_updated_at",
            "applied_at",
            "ip_address",
            "user_agent",
            "notes",
            "has_response",
            "was_applied",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class DocumentLookupRequestSerializer(
    serializers.Serializer
):
    """
    Datos recibidos para iniciar una consulta de DNI o RUC.

    El servicio externo se implementará en el siguiente archivo.
    """

    document_type = serializers.ChoiceField(
        choices=DocumentLookupLog.DOCUMENT_TYPE_CHOICES,
    )

    document_number = serializers.CharField(
        required=True,
        trim_whitespace=True,
        max_length=20,
    )

    def validate_document_number(self, value):
        document_number = str(
            value or ""
        ).replace(
            " ",
            "",
        ).strip()

        if not document_number.isdigit():
            raise serializers.ValidationError(
                "El documento debe contener únicamente números."
            )

        return document_number

    def validate(self, attrs):
        document_type = attrs[
            "document_type"
        ]

        document_number = attrs[
            "document_number"
        ]

        if (
            document_type
            == DocumentLookupLog.DOCUMENT_DNI
            and len(document_number) != 8
        ):
            raise serializers.ValidationError(
                {
                    "document_number": (
                        "El DNI debe contener exactamente "
                        "8 números."
                    )
                }
            )

        if (
            document_type
            == DocumentLookupLog.DOCUMENT_RUC
        ):
            if len(document_number) != 11:
                raise serializers.ValidationError(
                    {
                        "document_number": (
                            "El RUC debe contener exactamente "
                            "11 números."
                        )
                    }
                )

            if not Partner.is_valid_peruvian_ruc(
                document_number
            ):
                raise serializers.ValidationError(
                    {
                        "document_number": (
                            "El RUC no supera la validación "
                            "del dígito verificador."
                        )
                    }
                )

        return attrs