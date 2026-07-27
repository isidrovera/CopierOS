# -*- coding: utf-8 -*-
from django.contrib import admin

from apps.rentals.models import (
    RentalAssignment,
    RentalContract,
    RentalDocument,
    RentalEquipment,
    RentalEquipmentMovement,
    RentalInstallation,
    RentalPreparation,
    RentalRemoval,
    RentalReplacement,
    RentalWarehouse,
)


@admin.register(RentalWarehouse)
class RentalWarehouseAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name",
        "is_active",
        "allows_entries",
        "allows_dispatches",
        "display_order",
        "archived_at",
    ]

    list_filter = [
        "is_active",
        "allows_entries",
        "allows_dispatches",
        "archived_at",
    ]

    search_fields = [
        "code",
        "name",
        "address",
    ]

    ordering = [
        "display_order",
        "name",
    ]


@admin.register(RentalEquipment)
class RentalEquipmentAdmin(admin.ModelAdmin):
    list_display = [
        "equipment",
        "purpose",
        "acquisition_source",
        "warehouse",
        "operational_status",
        "is_available_for_rental",
        "entry_date",
        "archived_at",
    ]

    list_filter = [
        "purpose",
        "acquisition_source",
        "operational_status",
        "is_available_for_rental",
        "warehouse",
        "archived_at",
    ]

    search_fields = [
        "equipment__serial_number",
        "equipment__internal_code",
        "acquisition_document",
        "acquisition_reference",
    ]

    autocomplete_fields = [
        "equipment",
        "supplier",
        "owner_customer",
        "warehouse",
    ]

    ordering = [
        "-created_at",
    ]


@admin.register(RentalEquipmentMovement)
class RentalEquipmentMovementAdmin(admin.ModelAdmin):
    list_display = [
        "rental_equipment",
        "movement_type",
        "previous_status",
        "new_status",
        "source_warehouse",
        "destination_warehouse",
        "occurred_at",
        "archived_at",
    ]

    list_filter = [
        "movement_type",
        "previous_status",
        "new_status",
        "reference_type",
        "source_warehouse",
        "destination_warehouse",
        "archived_at",
    ]

    search_fields = [
        "rental_equipment__equipment__serial_number",
        "reference_number",
        "document_number",
        "reason",
    ]

    autocomplete_fields = [
        "rental_equipment",
        "source_warehouse",
        "destination_warehouse",
    ]

    ordering = [
        "-occurred_at",
        "-created_at",
    ]


@admin.register(RentalPreparation)
class RentalPreparationAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "rental_equipment",
        "status",
        "result",
        "assigned_technician",
        "scheduled_date",
        "completed_at",
        "archived_at",
    ]

    list_filter = [
        "status",
        "result",
        "scheduled_date",
        "archived_at",
    ]

    search_fields = [
        "code",
        "rental_equipment__equipment__serial_number",
        "request_reason",
        "technical_observations",
    ]

    autocomplete_fields = [
        "rental_equipment",
        "assigned_technician",
    ]

    ordering = [
        "-requested_at",
        "-created_at",
    ]


@admin.register(RentalContract)
class RentalContractAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "contract_number",
        "customer",
        "contract_type",
        "status",
        "start_date",
        "end_date",
        "archived_at",
    ]

    list_filter = [
        "contract_type",
        "status",
        "start_date",
        "end_date",
        "archived_at",
    ]

    search_fields = [
        "code",
        "contract_number",
        "customer__legal_name",
        "customer__trade_name",
        "external_reference",
    ]

    autocomplete_fields = [
        "customer",
        "main_branch",
        "main_contact",
    ]

    ordering = [
        "-created_at",
    ]


@admin.register(RentalAssignment)
class RentalAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "contract",
        "rental_equipment",
        "customer",
        "branch",
        "status",
        "assigned_at",
        "scheduled_installation_date",
        "archived_at",
    ]

    list_filter = [
        "contract",
        "status",
        "assigned_at",
        "scheduled_installation_date",
        "archived_at",
    ]

    search_fields = [
        "code",
        "contract__code",
        "contract__contract_number",
        "rental_equipment__equipment__serial_number",
        "customer__legal_name",
        "customer__trade_name",
        "site_location",
    ]

    autocomplete_fields = [
        "contract",
        "rental_equipment",
        "customer",
        "branch",
        "contact",
    ]

    ordering = [
        "-assigned_at",
        "-created_at",
    ]


@admin.register(RentalInstallation)
class RentalInstallationAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "rental_assignment",
        "assigned_technician",
        "status",
        "result",
        "scheduled_at",
        "completed_at",
        "customer_conformity",
        "archived_at",
    ]

    list_filter = [
        "status",
        "result",
        "customer_conformity",
        "scheduled_at",
        "archived_at",
    ]

    search_fields = [
        "code",
        "rental_assignment__code",
        "rental_assignment__contract__code",
        "rental_assignment__rental_equipment__equipment__serial_number",
        "site_location",
        "ip_address",
        "hostname",
    ]

    autocomplete_fields = [
        "rental_assignment",
        "assigned_technician",
    ]

    ordering = [
        "-requested_at",
        "-created_at",
    ]


@admin.register(RentalRemoval)
class RentalRemovalAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "rental_assignment",
        "removal_type",
        "assigned_technician",
        "status",
        "result",
        "destination_warehouse",
        "scheduled_at",
        "completed_at",
        "archived_at",
    ]

    list_filter = [
        "removal_type",
        "status",
        "result",
        "destination_warehouse",
        "scheduled_at",
        "archived_at",
    ]

    search_fields = [
        "code",
        "rental_assignment__code",
        "rental_assignment__contract__code",
        "rental_assignment__rental_equipment__equipment__serial_number",
        "removal_reason",
        "equipment_condition",
    ]

    autocomplete_fields = [
        "rental_assignment",
        "assigned_technician",
        "destination_warehouse",
    ]

    ordering = [
        "-requested_at",
        "-created_at",
    ]


@admin.register(RentalReplacement)
class RentalReplacementAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "rental_assignment",
        "outgoing_equipment",
        "incoming_equipment",
        "replacement_type",
        "reason",
        "status",
        "result",
        "scheduled_at",
        "completed_at",
        "archived_at",
    ]

    list_filter = [
        "replacement_type",
        "reason",
        "status",
        "result",
        "scheduled_at",
        "archived_at",
    ]

    search_fields = [
        "code",
        "rental_assignment__code",
        "rental_assignment__contract__code",
        "outgoing_equipment__equipment__serial_number",
        "incoming_equipment__equipment__serial_number",
        "reason_detail",
    ]

    autocomplete_fields = [
        "rental_assignment",
        "outgoing_equipment",
        "incoming_equipment",
        "approved_by",
        "assigned_technician",
    ]

    ordering = [
        "-requested_at",
        "-created_at",
    ]


@admin.register(RentalDocument)
class RentalDocumentAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "document_type",
        "document_number",
        "rental_equipment",
        "contract",
        "assignment",
        "issued_date",
        "is_verified",
        "archived_at",
    ]

    list_filter = [
        "document_type",
        "is_verified",
        "issued_date",
        "archived_at",
    ]

    search_fields = [
        "title",
        "document_number",
        "description",
        "rental_equipment__equipment__serial_number",
        "contract__code",
        "assignment__code",
        "assignment__contract__code",
    ]

    autocomplete_fields = [
        "rental_equipment",
        "preparation",
        "contract",
        "assignment",
        "installation",
        "removal",
        "replacement",
    ]

    ordering = [
        "-issued_date",
        "-created_at",
    ]