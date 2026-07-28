# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    EquipmentInstalledItem,
    ServiceAssignmentHistory,
    ServiceChecklist,
    ServiceChecklistItem,
    ServiceEvidence,
    ServiceInstallationItem,
    ServiceMeterReading,
    ServiceOrder,
    ServicePartRequest,
    ServicePartRequestAttachment,
    ServicePartRequestComment,
    ServicePartRequestDecision,
    ServicePartRequestInformation,
    ServicePartRequestItem,
    ServicePartRequestNotification,
    ServicePartRequestStatusHistory,
    ServicePartStockReview,
    ServicePartStockReviewHistory,
    ServicePartTransfer,
    ServicePartTransferHistory,
    ServiceReusablePart,
    ServiceReusablePartHistory,
    ServiceStatusHistory,
    ServiceTrackingPoint,
    ServiceTrackingSession,
)


@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "equipment_serial_number",
        "customer_name",
        "assigned_technician",
        "status",
        "priority",
        "scheduled_at",
    )
    list_filter = (
        "status",
        "priority",
        "service_type",
    )
    search_fields = (
        "code",
        "equipment_serial_number",
        "customer_name",
        "customer_document_number",
        "address",
    )
    autocomplete_fields = (
        "equipment",
        "assigned_technician",
        "assigned_by",
    )


@admin.register(ServicePartRequest)
class ServicePartRequestAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "service_order",
        "status",
        "current_responsible_area",
        "current_responsible_user",
        "requested_at",
    )
    list_filter = (
        "status",
        "current_responsible_area",
        "archived_at",
    )
    search_fields = (
        "code",
        "service_order__code",
        "service_order__equipment_serial_number",
    )


@admin.register(ServicePartRequestItem)
class ServicePartRequestItemAdmin(admin.ModelAdmin):
    list_display = (
        "request",
        "display_name",
        "item_type",
        "requested_quantity",
        "approved_quantity",
        "management_decision",
        "supply_method",
    )
    list_filter = (
        "item_type",
        "urgency",
        "management_decision",
        "supply_method",
        "archived_at",
    )
    search_fields = (
        "request__code",
        "component_code",
        "component_name",
        "custom_code",
        "custom_name",
    )


@admin.register(ServiceReusablePart)
class ServiceReusablePartAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "component",
        "serial_number",
        "condition",
        "status",
        "origin_type",
        "location_name",
    )
    list_filter = (
        "condition",
        "status",
        "origin_type",
        "archived_at",
    )
    search_fields = (
        "code",
        "serial_number",
        "component__code",
        "component__name",
        "location_name",
    )


@admin.register(ServicePartTransfer)
class ServicePartTransferAdmin(admin.ModelAdmin):
    list_display = (
        "part_request_item",
        "source_equipment",
        "destination_equipment",
        "status",
        "removal_technician",
        "reception_technician",
    )
    list_filter = (
        "status",
        "removal_condition",
        "reception_condition",
        "archived_at",
    )


@admin.register(ServiceInstallationItem)
class ServiceInstallationItemAdmin(admin.ModelAdmin):
    list_display = (
        "service_order",
        "part_request_item",
        "planned_quantity",
        "installed_quantity",
        "result",
        "installed_by",
        "installed_at",
    )
    list_filter = (
        "result",
        "meter_type",
        "history_generated",
        "archived_at",
    )


@admin.register(EquipmentInstalledItem)
class EquipmentInstalledItemAdmin(admin.ModelAdmin):
    list_display = (
        "equipment",
        "item_name",
        "item_type",
        "origin_type",
        "status",
        "installed_by",
        "installed_at",
        "reference_meter",
        "meter_difference",
    )
    list_filter = (
        "item_type",
        "origin_type",
        "status",
        "meter_type",
        "color",
        "installed_at",
    )
    search_fields = (
        "equipment__serial_number",
        "equipment__internal_code",
        "item_code",
        "item_name",
        "manufacturer_code",
        "serial_number",
        "part_request__code",
        "service_order__code",
    )
    date_hierarchy = "installed_at"


admin.site.register(ServiceAssignmentHistory)
admin.site.register(ServiceStatusHistory)
admin.site.register(ServiceTrackingSession)
admin.site.register(ServiceTrackingPoint)
admin.site.register(ServiceChecklist)
admin.site.register(ServiceChecklistItem)
admin.site.register(ServiceEvidence)
admin.site.register(ServiceMeterReading)
admin.site.register(ServicePartRequestStatusHistory)
admin.site.register(ServicePartRequestInformation)
admin.site.register(ServicePartRequestDecision)
admin.site.register(ServicePartRequestAttachment)
admin.site.register(ServicePartRequestComment)
admin.site.register(ServicePartRequestNotification)
admin.site.register(ServicePartStockReview)
admin.site.register(ServicePartStockReviewHistory)
admin.site.register(ServiceReusablePartHistory)
admin.site.register(ServicePartTransferHistory)
