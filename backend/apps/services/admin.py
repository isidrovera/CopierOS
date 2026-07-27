# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    ServiceAssignmentHistory,
    ServiceChecklist,
    ServiceChecklistItem,
    ServiceEvidence,
    ServiceMeterReading,
    ServiceOrder,
    ServicePartRequest,
    ServicePartRequestItem,
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
    list_filter = ("status", "priority", "service_type")
    search_fields = (
        "code",
        "equipment_serial_number",
        "customer_name",
        "customer_document_number",
        "address",
    )
    autocomplete_fields = ("equipment", "assigned_technician", "assigned_by")


admin.site.register(ServiceAssignmentHistory)
admin.site.register(ServiceStatusHistory)
admin.site.register(ServiceTrackingSession)
admin.site.register(ServiceTrackingPoint)
admin.site.register(ServiceChecklist)
admin.site.register(ServiceChecklistItem)
admin.site.register(ServicePartRequest)
admin.site.register(ServicePartRequestItem)
admin.site.register(ServiceEvidence)
admin.site.register(ServiceMeterReading)
