# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    ComponentCompatibility,
    ComponentType,
    Equipment,
    EquipmentBrand,
    EquipmentComponent,
    EquipmentComponentAssignment,
    EquipmentDocument,
    EquipmentFamily,
    EquipmentModel,
    EquipmentMovement,
    EquipmentType,
    ImportBatch,
    MeterReading,
)


@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    """
    Administración del catálogo de tipos de equipos.
    """

    list_display = (
        "code",
        "name",
        "requires_color_definition",
        "requires_meter",
        "allows_accessories",
        "is_active",
        "display_order",
        "is_archived_display",
    )

    list_filter = (
        "requires_color_definition",
        "requires_meter",
        "allows_accessories",
        "is_active",
        "archived_at",
    )

    search_fields = (
        "code",
        "name",
        "description",
    )

    ordering = (
        "display_order",
        "name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "archived_at",
        "archived_by",
    )

    fieldsets = (
        (
            "Información principal",
            {
                "fields": (
                    "id",
                    "code",
                    "name",
                    "description",
                )
            },
        ),
        (
            "Comportamiento",
            {
                "fields": (
                    "requires_color_definition",
                    "requires_meter",
                    "allows_accessories",
                    "is_active",
                    "display_order",
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
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                ),
            },
        ),
    )

    @admin.display(
        boolean=True,
        description="Archivado",
    )
    def is_archived_display(self, obj):
        return obj.is_archived


@admin.register(EquipmentBrand)
class EquipmentBrandAdmin(admin.ModelAdmin):
    """
    Administración de marcas de equipos.
    """

    list_display = (
        "code",
        "name",
        "country_code",
        "country_name",
        "is_active",
        "display_order",
        "is_archived_display",
    )

    list_filter = (
        "is_active",
        "country_code",
        "archived_at",
    )

    search_fields = (
        "code",
        "name",
        "legal_name",
        "country_name",
    )

    ordering = (
        "display_order",
        "name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "archived_at",
        "archived_by",
    )

    fieldsets = (
        (
            "Información principal",
            {
                "fields": (
                    "id",
                    "code",
                    "name",
                    "legal_name",
                    "description",
                    "logo",
                )
            },
        ),
        (
            "Procedencia",
            {
                "fields": (
                    "country_code",
                    "country_name",
                    "website",
                )
            },
        ),
        (
            "Configuración",
            {
                "fields": (
                    "is_active",
                    "display_order",
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
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                ),
            },
        ),
    )

    @admin.display(
        boolean=True,
        description="Archivada",
    )
    def is_archived_display(self, obj):
        return obj.is_archived


@admin.register(EquipmentFamily)
class EquipmentFamilyAdmin(admin.ModelAdmin):
    """
    Administración de familias técnicas de equipos.
    """

    list_display = (
        "code",
        "brand",
        "name",
        "equipment_type",
        "is_active",
        "display_order",
        "is_archived_display",
    )

    list_filter = (
        "brand",
        "equipment_type",
        "is_active",
        "archived_at",
    )

    search_fields = (
        "code",
        "name",
        "brand__name",
        "equipment_type__name",
        "description",
        "technical_notes",
    )

    autocomplete_fields = (
        "brand",
        "equipment_type",
    )

    ordering = (
        "brand__name",
        "display_order",
        "name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "archived_at",
        "archived_by",
    )

    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "id",
                    "code",
                    "brand",
                    "equipment_type",
                    "name",
                )
            },
        ),
        (
            "Información técnica",
            {
                "fields": (
                    "description",
                    "technical_notes",
                )
            },
        ),
        (
            "Configuración",
            {
                "fields": (
                    "is_active",
                    "display_order",
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
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                ),
            },
        ),
    )

    @admin.display(
        boolean=True,
        description="Archivada",
    )
    def is_archived_display(self, obj):
        return obj.is_archived


@admin.register(EquipmentModel)
class EquipmentModelAdmin(admin.ModelAdmin):
    """
    Administración del catálogo de modelos.
    """

    list_display = (
        "code",
        "brand",
        "name",
        "equipment_type",
        "equipment_family",
        "color_mode",
        "technology",
        "maximum_paper_size",
        "is_active",
        "is_archived_display",
    )

    list_filter = (
        "brand",
        "equipment_type",
        "equipment_family",
        "color_mode",
        "technology",
        "maximum_paper_size",
        "is_multifunction",
        "supports_accessories",
        "supports_technical_units",
        "is_active",
        "archived_at",
    )

    search_fields = (
        "code",
        "name",
        "commercial_name",
        "family",
        "equipment_family__code",
        "equipment_family__name",
        "manufacturer_reference",
        "brand__name",
    )

    autocomplete_fields = (
        "brand",
        "equipment_type",
        "equipment_family",
    )

    ordering = (
        "brand__name",
        "display_order",
        "name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "archived_at",
        "archived_by",
    )

    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "id",
                    "code",
                    "brand",
                    "equipment_type",
                    "name",
                    "commercial_name",
                    "family",
                    "equipment_family",
                    "manufacturer_reference",
                    "image",
                )
            },
        ),
        (
            "Características generales",
            {
                "fields": (
                    "color_mode",
                    "technology",
                    "maximum_paper_size",
                    "is_multifunction",
                )
            },
        ),
        (
            "Funciones",
            {
                "fields": (
                    "supports_printing",
                    "supports_copying",
                    "supports_scanning",
                    "supports_fax",
                    "supports_network",
                    "supports_duplex",
                )
            },
        ),
        (
            "Accesorios y unidades",
            {
                "fields": (
                    "supports_accessories",
                    "supports_technical_units",
                )
            },
        ),
        (
            "Contadores",
            {
                "fields": (
                    "has_total_meter",
                    "has_black_meter",
                    "has_color_meter",
                    "has_scan_meter",
                )
            },
        ),
        (
            "Notas",
            {
                "fields": (
                    "technical_notes",
                    "description",
                )
            },
        ),
        (
            "Configuración",
            {
                "fields": (
                    "is_active",
                    "display_order",
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
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                ),
            },
        ),
    )

    @admin.display(
        boolean=True,
        description="Archivado",
    )
    def is_archived_display(self, obj):
        return obj.is_archived


@admin.register(ComponentType)
class ComponentTypeAdmin(admin.ModelAdmin):
    """
    Administración de tipos de componentes técnicos.
    """

    list_display = (
        "code",
        "name",
        "category",
        "requires_color",
        "requires_serial_number",
        "requires_meter",
        "is_active",
        "display_order",
        "is_archived_display",
    )

    list_filter = (
        "category",
        "requires_color",
        "requires_serial_number",
        "requires_meter",
        "is_active",
        "archived_at",
    )

    search_fields = (
        "code",
        "name",
        "description",
    )

    ordering = (
        "display_order",
        "name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "archived_at",
        "archived_by",
    )

    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "id",
                    "code",
                    "name",
                    "category",
                    "description",
                )
            },
        ),
        (
            "Comportamiento técnico",
            {
                "fields": (
                    "requires_color",
                    "requires_serial_number",
                    "requires_meter",
                )
            },
        ),
        (
            "Configuración",
            {
                "fields": (
                    "is_active",
                    "display_order",
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
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                ),
            },
        ),
    )

    @admin.display(
        boolean=True,
        description="Archivado",
    )
    def is_archived_display(self, obj):
        return obj.is_archived


@admin.register(EquipmentComponent)
class EquipmentComponentAdmin(admin.ModelAdmin):
    """
    Administración del catálogo técnico de componentes.
    """

    list_display = (
        "code",
        "name",
        "component_type",
        "parent_component",
        "color",
        "manufacturer_code",
        "condition_control",
        "expected_life_meter",
        "expected_life_days",
        "is_active",
        "is_archived_display",
    )

    list_filter = (
        "component_type",
        "component_type__category",
        "color",
        "condition_control",
        "requires_individual_serial",
        "is_consumable",
        "is_reusable",
        "can_be_repaired",
        "requires_removed_part_tracking",
        "is_active",
        "archived_at",
    )

    search_fields = (
        "code",
        "name",
        "manufacturer_code",
        "alternative_code",
        "parent_component__code",
        "parent_component__name",
        "description",
        "technical_notes",
    )

    autocomplete_fields = (
        "component_type",
        "parent_component",
    )

    ordering = (
        "component_type__display_order",
        "display_order",
        "name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "archived_at",
        "archived_by",
    )

    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "id",
                    "component_type",
                    "parent_component",
                    "code",
                    "name",
                    "image",
                )
            },
        ),
        (
            "Códigos técnicos",
            {
                "fields": (
                    "manufacturer_code",
                    "alternative_code",
                )
            },
        ),
        (
            "Características",
            {
                "fields": (
                    "color",
                    "unit_of_measure",
                    "requires_individual_serial",
                    "is_consumable",
                    "is_reusable",
                    "can_be_repaired",
                    "requires_removed_part_tracking",
                )
            },
        ),
        (
            "Duración estimada",
            {
                "fields": (
                    "condition_control",
                    "expected_life_meter",
                    "expected_life_days",
                    "life_reference",
                )
            },
        ),
        (
            "Información técnica",
            {
                "fields": (
                    "description",
                    "technical_notes",
                )
            },
        ),
        (
            "Configuración",
            {
                "fields": (
                    "is_active",
                    "display_order",
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
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                ),
            },
        ),
    )

    @admin.display(
        boolean=True,
        description="Archivado",
    )
    def is_archived_display(self, obj):
        return obj.is_archived


@admin.register(ComponentCompatibility)
class ComponentCompatibilityAdmin(admin.ModelAdmin):
    """
    Administración de compatibilidades de componentes.
    """

    list_display = (
        "component",
        "equipment_family",
        "equipment_model",
        "position",
        "manufacturer_code_override",
        "expected_life_meter_override",
        "expected_life_days_override",
        "is_required",
        "is_active",
        "is_archived_display",
    )

    list_filter = (
        "equipment_family__brand",
        "equipment_family",
        "equipment_model",
        "component__component_type",
        "component__color",
        "is_required",
        "is_active",
        "archived_at",
    )

    search_fields = (
        "component__code",
        "component__name",
        "component__manufacturer_code",
        "component__alternative_code",
        "manufacturer_code_override",
        "equipment_family__code",
        "equipment_family__name",
        "equipment_model__code",
        "equipment_model__name",
        "position",
        "technical_notes",
    )

    autocomplete_fields = (
        "component",
        "equipment_family",
        "equipment_model",
    )

    ordering = (
        "equipment_family__brand__name",
        "equipment_family__name",
        "display_order",
        "component__name",
    )

    readonly_fields = (
        "id",
        "effective_manufacturer_code",
        "effective_expected_life_meter",
        "effective_expected_life_days",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "archived_at",
        "archived_by",
    )

    fieldsets = (
        (
            "Compatibilidad",
            {
                "fields": (
                    "id",
                    "component",
                    "equipment_family",
                    "equipment_model",
                    "position",
                )
            },
        ),
        (
            "Información específica",
            {
                "fields": (
                    "manufacturer_code_override",
                    "expected_life_meter_override",
                    "expected_life_days_override",
                    "technical_notes",
                )
            },
        ),
        (
            "Valores aplicables",
            {
                "classes": (
                    "collapse",
                ),
                "fields": (
                    "effective_manufacturer_code",
                    "effective_expected_life_meter",
                    "effective_expected_life_days",
                ),
            },
        ),
        (
            "Configuración",
            {
                "fields": (
                    "is_required",
                    "is_active",
                    "display_order",
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
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                ),
            },
        ),
    )

    @admin.display(
        boolean=True,
        description="Archivada",
    )
    def is_archived_display(self, obj):
        return obj.is_archived


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    """
    Administración de importaciones y lotes.
    """

    list_display = (
        "code",
        "supplier",
        "purchase_type",
        "invoice_number",
        "purchase_date",
        "arrival_date",
        "expected_quantity",
        "declared_quantity",
        "currency",
        "total_cost",
        "status",
        "is_active",
    )

    list_filter = (
        "purchase_type",
        "currency",
        "status",
        "is_active",
        "purchase_date",
        "arrival_date",
        "archived_at",
    )

    search_fields = (
        "code",
        "supplier__legal_name",
        "supplier__trade_name",
        "supplier__document_number",
        "import_number",
        "purchase_order_number",
        "invoice_number",
        "container_number",
        "transport_reference",
    )

    autocomplete_fields = (
        "supplier",
    )

    readonly_fields = (
        "id",
        "total_cost",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "purchase_date"

    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "id",
                    "code",
                    "purchase_type",
                    "supplier",
                    "status",
                    "is_active",
                )
            },
        ),
        (
            "Documentos",
            {
                "fields": (
                    "import_number",
                    "purchase_order_number",
                    "invoice_number",
                    "invoice_date",
                    "purchase_date",
                )
            },
        ),
        (
            "Transporte y llegada",
            {
                "fields": (
                    "estimated_arrival_date",
                    "arrival_date",
                    "unloading_start_date",
                    "unloading_end_date",
                    "origin_country_code",
                    "origin_country_name",
                    "origin_port",
                    "destination_port",
                    "container_number",
                    "transport_reference",
                    "warehouse_location",
                )
            },
        ),
        (
            "Cantidades",
            {
                "fields": (
                    "expected_quantity",
                    "declared_quantity",
                )
            },
        ),
        (
            "Costos",
            {
                "fields": (
                    "currency",
                    "exchange_rate",
                    "equipment_subtotal",
                    "freight_cost",
                    "insurance_cost",
                    "customs_cost",
                    "tax_cost",
                    "other_costs",
                    "total_cost",
                )
            },
        ),
        (
            "Observaciones",
            {
                "fields": (
                    "unloading_notes",
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
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                ),
            },
        ),
    )


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """
    Administración de máquinas físicas.
    """

    list_display = (
        "internal_code",
        "serial_number",
        "equipment_model",
        "technical_status",
        "commercial_status",
        "is_available",
        "customer",
        "warehouse_location",
        "current_total_meter",
        "is_active",
    )

    list_filter = (
        "equipment_model__brand",
        "equipment_model__equipment_type",
        "equipment_model__equipment_family",
        "ownership_type",
        "physical_condition",
        "technical_status",
        "commercial_status",
        "is_available",
        "is_active",
        "purchase_currency",
        "sale_currency",
        "archived_at",
    )

    search_fields = (
        "internal_code",
        "serial_number",
        "equipment_model__name",
        "equipment_model__brand__name",
        "equipment_model__equipment_family__name",
        "customer__legal_name",
        "customer__trade_name",
        "customer__document_number",
        "supplier__legal_name",
        "supplier__trade_name",
        "purchase_invoice_number",
        "sale_invoice_number",
        "asset_number",
        "hostname",
        "ip_address",
        "mac_address",
    )

    autocomplete_fields = (
        "equipment_model",
        "import_batch",
        "supplier",
        "owner_partner",
        "customer",
        "customer_branch",
        "advisor",
        "unloading_registered_by",
    )

    readonly_fields = (
        "id",
        "is_available",
        "total_acquisition_cost",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "unloading_date"

    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "id",
                    "internal_code",
                    "serial_number",
                    "equipment_model",
                    "main_photo",
                    "asset_number",
                )
            },
        ),
        (
            "Propiedad y procedencia",
            {
                "fields": (
                    "ownership_type",
                    "physical_condition",
                    "import_batch",
                    "supplier",
                    "owner_partner",
                    "import_reference",
                )
            },
        ),
        (
            "Compra e importación",
            {
                "fields": (
                    "purchase_invoice_number",
                    "purchase_invoice_date",
                    "purchase_date",
                    "unloading_date",
                    "unloading_registered_by",
                    "purchase_currency",
                    "purchase_price",
                    "allocated_import_cost",
                    "total_acquisition_cost",
                )
            },
        ),
        (
            "Cliente y venta",
            {
                "fields": (
                    "customer",
                    "customer_branch",
                    "advisor",
                    "sale_currency",
                    "sale_price",
                    "sale_invoice_number",
                    "sale_invoice_date",
                    "reservation_date",
                    "reservation_expiration_date",
                    "sale_date",
                    "delivery_date",
                )
            },
        ),
        (
            "Estados",
            {
                "fields": (
                    "technical_status",
                    "technical_status_reason",
                    "commercial_status",
                    "commercial_status_reason",
                    "is_available",
                    "is_active",
                )
            },
        ),
        (
            "Ubicación",
            {
                "fields": (
                    "warehouse_location",
                    "position_reference",
                )
            },
        ),
        (
            "Contadores de ingreso",
            {
                "fields": (
                    "initial_total_meter",
                    "initial_black_meter",
                    "initial_color_meter",
                    "initial_scan_meter",
                )
            },
        ),
        (
            "Contadores actuales",
            {
                "fields": (
                    "current_total_meter",
                    "current_black_meter",
                    "current_color_meter",
                    "current_scan_meter",
                    "last_meter_date",
                    "last_meter_source",
                )
            },
        ),
        (
            "Red y sistema",
            {
                "fields": (
                    "hostname",
                    "ip_address",
                    "mac_address",
                    "firmware_version",
                )
            },
        ),
        (
            "Configuración recibida y notas",
            {
                "fields": (
                    "accessories_description",
                    "unloading_observations",
                    "technical_notes",
                    "commercial_notes",
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
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                ),
            },
        ),
    )


@admin.register(EquipmentComponentAssignment)
class EquipmentComponentAssignmentAdmin(admin.ModelAdmin):
    """
    Administración del historial de componentes instalados.
    """

    list_display = (
        "equipment",
        "component",
        "serial_number",
        "position",
        "status",
        "installed_at",
        "installation_meter",
        "removed_at",
        "removal_meter",
        "removed_disposition",
        "is_active",
    )

    list_filter = (
        "component__component_type",
        "component__component_type__category",
        "component__color",
        "status",
        "removed_disposition",
        "is_active",
        "installed_at",
        "removed_at",
        "archived_at",
    )

    search_fields = (
        "equipment__internal_code",
        "equipment__serial_number",
        "equipment__equipment_model__name",
        "component__code",
        "component__name",
        "component__manufacturer_code",
        "component__alternative_code",
        "serial_number",
        "position",
        "reference_type",
        "installation_notes",
        "removal_notes",
    )

    autocomplete_fields = (
        "equipment",
        "component",
    )

    ordering = (
        "-installed_at",
        "-created_at",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "archived_at",
        "archived_by",
    )

    fieldsets = (
        (
            "Asignación",
            {
                "fields": (
                    "id",
                    "equipment",
                    "component",
                    "serial_number",
                    "position",
                    "status",
                    "is_active",
                )
            },
        ),
        (
            "Instalación",
            {
                "fields": (
                    "installed_at",
                    "installation_meter",
                    "installation_notes",
                )
            },
        ),
        (
            "Retiro",
            {
                "fields": (
                    "removed_at",
                    "removal_meter",
                    "removed_disposition",
                    "removal_notes",
                )
            },
        ),
        (
            "Referencia",
            {
                "fields": (
                    "reference_type",
                    "reference_id",
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
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                    "archived_at",
                    "archived_by",
                    "archived_reason",
                ),
            },
        ),
    )


@admin.register(EquipmentMovement)
class EquipmentMovementAdmin(admin.ModelAdmin):
    """
    Administración del historial de movimientos.
    """

    list_display = (
        "equipment",
        "movement_type",
        "occurred_at",
        "responsible_user",
        "previous_technical_status",
        "new_technical_status",
        "previous_commercial_status",
        "new_commercial_status",
        "new_customer",
        "is_system_generated",
    )

    list_filter = (
        "movement_type",
        "reference_type",
        "is_system_generated",
        "occurred_at",
    )

    search_fields = (
        "equipment__internal_code",
        "equipment__serial_number",
        "reference_number",
        "document_number",
        "reason",
        "notes",
        "new_customer__legal_name",
        "new_customer__trade_name",
    )

    autocomplete_fields = (
        "equipment",
        "responsible_user",
        "previous_customer",
        "new_customer",
        "previous_customer_branch",
        "new_customer_branch",
        "previous_owner",
        "new_owner",
        "previous_advisor",
        "new_advisor",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "occurred_at"


@admin.register(MeterReading)
class MeterReadingAdmin(admin.ModelAdmin):
    """
    Administración de lecturas de contadores.
    """

    list_display = (
        "equipment",
        "reading_date",
        "reading_type",
        "source",
        "total_meter",
        "black_meter",
        "color_meter",
        "total_difference",
        "is_verified",
        "is_applied_to_equipment",
    )

    list_filter = (
        "reading_type",
        "source",
        "reference_type",
        "is_verified",
        "is_applied_to_equipment",
        "reading_date",
    )

    search_fields = (
        "equipment__internal_code",
        "equipment__serial_number",
        "reference_number",
        "ip_address",
        "notes",
    )

    autocomplete_fields = (
        "equipment",
        "registered_by",
        "verified_by",
    )

    readonly_fields = (
        "id",
        "previous_total_meter",
        "previous_black_meter",
        "previous_color_meter",
        "previous_scan_meter",
        "total_difference",
        "black_difference",
        "color_difference",
        "scan_difference",
        "is_applied_to_equipment",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "reading_date"


@admin.register(EquipmentDocument)
class EquipmentDocumentAdmin(admin.ModelAdmin):
    """
    Administración de documentos relacionados con equipos.
    """

    list_display = (
        "title",
        "equipment",
        "document_type",
        "document_number",
        "document_date",
        "reference_type",
        "is_primary",
        "is_verified",
        "is_active",
    )

    list_filter = (
        "document_type",
        "reference_type",
        "is_primary",
        "is_confidential",
        "is_verified",
        "is_active",
        "document_date",
        "archived_at",
    )

    search_fields = (
        "title",
        "document_number",
        "reference_number",
        "equipment__internal_code",
        "equipment__serial_number",
        "description",
        "notes",
    )

    autocomplete_fields = (
        "equipment",
        "uploaded_by",
        "verified_by",
    )

    readonly_fields = (
        "id",
        "original_filename",
        "file_extension",
        "file_size",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "document_date"