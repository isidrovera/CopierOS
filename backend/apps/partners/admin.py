# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    DocumentLookupLog,
    Partner,
    PartnerBranch,
    PartnerContact,
)


class PartnerBranchInline(admin.TabularInline):
    """
    Permite visualizar las sedes directamente
    dentro del tercero.
    """

    model = PartnerBranch
    extra = 0
    fields = (
        "name",
        "branch_type",
        "district",
        "province",
        "region",
        "is_main",
        "is_fiscal",
        "allows_equipment_installation",
        "is_active",
    )

    readonly_fields = ()
    show_change_link = True


class PartnerContactInline(admin.TabularInline):
    """
    Permite visualizar los contactos directamente
    dentro del tercero.
    """

    model = PartnerContact
    extra = 0
    fields = (
        "first_names",
        "paternal_last_name",
        "job_title",
        "area",
        "primary_email",
        "primary_mobile",
        "is_primary",
        "is_active",
    )

    readonly_fields = ()
    show_change_link = True


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    """
    Administración principal de clientes,
    proveedores y distribuidores.
    """

    list_display = (
        "display_name_admin",
        "document_display_admin",
        "country_code",
        "commercial_roles_admin",
        "advisor",
        "is_active",
        "is_archived_admin",
        "created_at",
    )

    list_filter = (
        "person_type",
        "country_code",
        "document_type",
        "classification",
        "is_rental_customer",
        "is_sales_customer",
        "is_service_customer",
        "is_supplier",
        "is_distributor",
        "is_active",
        "is_commercially_blocked",
        "document_verified",
        "sunat_status",
        "sunat_condition",
        "created_at",
    )

    search_fields = (
        "code",
        "document_number",
        "legal_name",
        "trade_name",
        "first_names",
        "paternal_last_name",
        "maternal_last_name",
        "general_email",
        "billing_email",
        "general_phone",
        "mobile_phone",
    )

    autocomplete_fields = (
        "advisor",
        "purchasing_manager",
        "created_by",
        "updated_by",
        "archived_by",
    )

    readonly_fields = (
        "id",
        "display_name_admin",
        "commercial_roles_admin",
        "is_archived_admin",
        "created_at",
        "updated_at",
        "document_verified_at",
        "last_document_lookup_at",
        "archived_at",
    )

    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "id",
                    "code",
                    "person_type",
                    "country_code",
                    "country_name",
                    "document_type",
                    "document_number",
                    "document_source",
                    "document_verified",
                    "document_verified_at",
                    "last_document_lookup_at",
                )
            },
        ),
        (
            "Nombre",
            {
                "fields": (
                    "legal_name",
                    "trade_name",
                    "first_names",
                    "paternal_last_name",
                    "maternal_last_name",
                    "display_name_admin",
                )
            },
        ),
        (
            "Tipos comerciales",
            {
                "fields": (
                    "is_rental_customer",
                    "is_sales_customer",
                    "is_service_customer",
                    "is_supplier",
                    "is_distributor",
                    "commercial_roles_admin",
                )
            },
        ),
        (
            "Responsables",
            {
                "fields": (
                    "advisor",
                    "purchasing_manager",
                )
            },
        ),
        (
            "Clasificación y condiciones",
            {
                "fields": (
                    "classification",
                    "preferred_currency",
                    "preferred_language",
                    "payment_terms",
                    "credit_days",
                    "credit_limit",
                    "requires_purchase_order",
                    "requires_service_conformity",
                    "requires_delivery_guide",
                )
            },
        ),
        (
            "Contacto general",
            {
                "fields": (
                    "general_phone",
                    "mobile_phone",
                    "general_email",
                    "billing_email",
                    "website",
                )
            },
        ),
        (
            "Dirección fiscal",
            {
                "fields": (
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
                )
            },
        ),
        (
            "Información SUNAT",
            {
                "classes": (
                    "collapse",
                ),
                "fields": (
                    "sunat_status",
                    "sunat_condition",
                    "taxpayer_type",
                    "economic_activity",
                    "employee_count",
                    "billing_type",
                    "accounting_type",
                    "foreign_trade",
                    "is_withholding_agent",
                ),
            },
        ),
        (
            "Estado comercial",
            {
                "fields": (
                    "is_active",
                    "is_commercially_blocked",
                    "commercial_block_reason",
                    "notes",
                )
            },
        ),
        (
            "Auditoría",
            {
                "classes": (
                    "collapse",
                ),
                "fields": (
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                    "is_archived_admin",
                ),
            },
        ),
    )

    inlines = (
        PartnerBranchInline,
        PartnerContactInline,
    )

    ordering = (
        "legal_name",
        "trade_name",
        "first_names",
    )

    list_per_page = 50

    @admin.display(
        description="Nombre",
        ordering="legal_name",
    )
    def display_name_admin(self, obj):
        if not obj:
            return ""

        return obj.display_name

    @admin.display(
        description="Documento",
        ordering="document_number",
    )
    def document_display_admin(self, obj):
        return (
            f"{obj.get_document_type_display()} "
            f"{obj.document_number}"
        )

    @admin.display(
        description="Tipos",
    )
    def commercial_roles_admin(self, obj):
        if not obj:
            return ""

        return ", ".join(
            obj.commercial_roles
        )

    @admin.display(
        description="Archivado",
        boolean=True,
    )
    def is_archived_admin(self, obj):
        if not obj:
            return False

        return obj.is_archived


@admin.register(PartnerBranch)
class PartnerBranchAdmin(admin.ModelAdmin):
    """
    Administración de sedes y sucursales.
    """

    list_display = (
        "name",
        "partner",
        "branch_type",
        "district",
        "province",
        "region",
        "is_main",
        "is_fiscal",
        "allows_equipment_installation",
        "is_active",
    )

    list_filter = (
        "branch_type",
        "country_code",
        "is_main",
        "is_fiscal",
        "allows_equipment_installation",
        "allows_deliveries",
        "is_active",
        "region",
        "province",
        "district",
    )

    search_fields = (
        "name",
        "code",
        "partner__legal_name",
        "partner__trade_name",
        "partner__document_number",
        "address",
        "district",
        "province",
        "region",
    )

    autocomplete_fields = (
        "partner",
        "advisor",
        "created_by",
        "updated_by",
        "archived_by",
    )

    readonly_fields = (
        "id",
        "display_name_admin",
        "effective_advisor_admin",
        "created_at",
        "updated_at",
        "archived_at",
    )

    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "id",
                    "partner",
                    "code",
                    "name",
                    "branch_type",
                    "is_main",
                    "is_fiscal",
                    "display_name_admin",
                )
            },
        ),
        (
            "Operación",
            {
                "fields": (
                    "allows_equipment_installation",
                    "allows_deliveries",
                    "advisor",
                    "effective_advisor_admin",
                    "operating_hours",
                    "access_instructions",
                    "installation_notes",
                    "start_date",
                    "end_date",
                )
            },
        ),
        (
            "Dirección",
            {
                "fields": (
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
                )
            },
        ),
        (
            "Ubicación geográfica",
            {
                "fields": (
                    "latitude",
                    "longitude",
                )
            },
        ),
        (
            "Contacto de sede",
            {
                "fields": (
                    "general_phone",
                    "mobile_phone",
                    "general_email",
                )
            },
        ),
        (
            "Estado",
            {
                "fields": (
                    "is_active",
                    "notes",
                )
            },
        ),
        (
            "Auditoría",
            {
                "classes": (
                    "collapse",
                ),
                "fields": (
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                ),
            },
        ),
    )

    @admin.display(
        description="Nombre completo",
    )
    def display_name_admin(self, obj):
        if not obj:
            return ""

        return obj.display_name

    @admin.display(
        description="Responsable efectiva",
    )
    def effective_advisor_admin(self, obj):
        if not obj:
            return ""

        return obj.effective_advisor


@admin.register(PartnerContact)
class PartnerContactAdmin(admin.ModelAdmin):
    """
    Administración de contactos.
    """

    list_display = (
        "full_name_admin",
        "partner",
        "branch",
        "job_title",
        "area",
        "primary_email",
        "primary_mobile",
        "is_primary",
        "is_active",
    )

    list_filter = (
        "area",
        "is_primary",
        "is_legal_representative",
        "is_branch_manager",
        "receives_contracts",
        "receives_billing",
        "receives_collections",
        "receives_meter_requests",
        "receives_service_notifications",
        "receives_incident_notifications",
        "is_active",
    )

    search_fields = (
        "first_names",
        "paternal_last_name",
        "maternal_last_name",
        "document_number",
        "job_title",
        "primary_email",
        "secondary_email",
        "primary_mobile",
        "secondary_mobile",
        "whatsapp_number",
        "partner__legal_name",
        "partner__trade_name",
        "partner__document_number",
    )

    autocomplete_fields = (
        "partner",
        "branch",
        "created_by",
        "updated_by",
        "archived_by",
    )

    readonly_fields = (
        "id",
        "full_name_admin",
        "notification_roles_admin",
        "created_at",
        "updated_at",
        "archived_at",
    )

    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "id",
                    "partner",
                    "branch",
                    "document_type",
                    "document_number",
                    "first_names",
                    "paternal_last_name",
                    "maternal_last_name",
                    "full_name_admin",
                    "job_title",
                    "area",
                )
            },
        ),
        (
            "Contacto",
            {
                "fields": (
                    "primary_email",
                    "secondary_email",
                    "work_phone",
                    "work_extension",
                    "primary_mobile",
                    "secondary_mobile",
                    "has_whatsapp",
                    "whatsapp_number",
                    "preferred_contact_method",
                    "contact_schedule",
                )
            },
        ),
        (
            "Responsabilidades",
            {
                "fields": (
                    "is_primary",
                    "is_legal_representative",
                    "is_branch_manager",
                    "can_authorize_equipment_entry",
                    "can_authorize_equipment_removal",
                    "can_sign_documents",
                )
            },
        ),
        (
            "Notificaciones",
            {
                "fields": (
                    "receives_contracts",
                    "receives_billing",
                    "receives_collections",
                    "receives_purchase_orders",
                    "receives_delivery_documents",
                    "receives_meter_requests",
                    "receives_service_notifications",
                    "receives_incident_notifications",
                    "receives_commercial_notifications",
                    "notification_roles_admin",
                )
            },
        ),
        (
            "Estado",
            {
                "fields": (
                    "is_active",
                    "notes",
                )
            },
        ),
        (
            "Auditoría",
            {
                "classes": (
                    "collapse",
                ),
                "fields": (
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                ),
            },
        ),
    )

    @admin.display(
        description="Nombre completo",
        ordering="first_names",
    )
    def full_name_admin(self, obj):
        if not obj:
            return ""

        return obj.full_name

    @admin.display(
        description="Notificaciones",
    )
    def notification_roles_admin(self, obj):
        if not obj:
            return ""

        return ", ".join(
            obj.notification_roles
        )


@admin.register(DocumentLookupLog)
class DocumentLookupLogAdmin(admin.ModelAdmin):
    """
    Historial de consultas DNI y RUC.
    """

    list_display = (
        "document_display_admin",
        "provider",
        "status",
        "http_status_code",
        "is_successful",
        "requested_by",
        "partner",
        "created_at",
    )

    list_filter = (
        "document_type",
        "provider",
        "status",
        "result_action",
        "http_status_code",
        "is_successful",
        "cache_used",
        "created_at",
    )

    search_fields = (
        "document_number",
        "provider_name",
        "error_message",
        "partner__legal_name",
        "partner__trade_name",
        "partner__document_number",
        "requested_by__email",
    )

    autocomplete_fields = (
        "requested_by",
        "partner",
        "created_by",
        "updated_by",
        "archived_by",
    )

    readonly_fields = (
        "id",
        "document_display_admin",
        "document_type",
        "document_number",
        "provider",
        "provider_name",
        "requested_by",
        "partner",
        "status",
        "result_action",
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
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Consulta",
            {
                "fields": (
                    "id",
                    "document_display_admin",
                    "document_type",
                    "document_number",
                    "provider",
                    "provider_name",
                    "requested_by",
                    "partner",
                )
            },
        ),
        (
            "Resultado",
            {
                "fields": (
                    "status",
                    "result_action",
                    "http_status_code",
                    "is_successful",
                    "response_time_ms",
                    "cache_used",
                    "provider_updated_at",
                    "applied_at",
                    "error_message",
                )
            },
        ),
        (
            "Información recibida",
            {
                "classes": (
                    "collapse",
                ),
                "fields": (
                    "request_data",
                    "response_data",
                    "normalized_data",
                ),
            },
        ),
        (
            "Solicitud",
            {
                "classes": (
                    "collapse",
                ),
                "fields": (
                    "ip_address",
                    "user_agent",
                    "notes",
                ),
            },
        ),
        (
            "Auditoría",
            {
                "classes": (
                    "collapse",
                ),
                "fields": (
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 100

    def has_add_permission(
        self,
        request,
    ):
        """
        Los registros se crearán desde el servicio de consulta.
        """

        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        """
        El historial no debe modificarse desde Admin.
        """

        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        """
        El historial no debe eliminarse desde Admin.
        """

        return False

    @admin.display(
        description="Documento",
        ordering="document_number",
    )
    def document_display_admin(self, obj):
        if not obj:
            return ""

        return obj.display_document