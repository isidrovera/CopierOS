# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    Repair,
    RepairAssignment,
    RepairChecklist,
    RepairChecklistItem,
    RepairComponent,
    RepairDiagnosis,
    RepairPhoto,
    RepairSNMPValidation,
    RepairStatusHistory,
    RepairTest,
    RepairPartRequest,
    RepairPartRequestItem,
    RepairPartRequestReview,
    RepairPartRequestDecision,
    RepairPartSource,
    RepairPartWithdrawal,
    RepairPartDelivery,
    RepairPartReplacement,
    RepairPartRequestHistory,
    RepairPartRequestComment,
    RepairPartRequestAttachment,
    RepairPartRequestNotification,
)


def model_field_names(model):
    """
    Devuelve los nombres de los campos reales del modelo.

    Permite configurar el administrador sin utilizar campos
    que todavía no existen en algunos modelos.
    """

    return {
        field.name
        for field in model._meta.get_fields()
    }


def existing_fields(
    model,
    *field_names,
):
    """
    Devuelve solamente los campos existentes en el modelo.
    """

    available_fields = model_field_names(
        model
    )

    return tuple(
        field_name
        for field_name in field_names
        if field_name in available_fields
    )


@admin.register(Repair)
class RepairAdmin(admin.ModelAdmin):
    list_display = existing_fields(
        Repair,
        "code",
        "equipment",
        "repair_type",
        "status",
        "priority",
        "assigned_technician",
        "is_active",
        "requested_at",
        "completed_at",
        "created_at",
    )

    list_filter = existing_fields(
        Repair,
        "repair_type",
        "status",
        "priority",
        "is_active",
        "requires_parts",
        "requires_external_service",
        "requires_follow_up",
        "archived_at",
    )

    search_fields = existing_fields(
        Repair,
        "code",
        "reported_problem",
        "initial_observations",
        "work_summary",
        "pending_work",
        "final_observations",
        "closure_notes",
    )

    readonly_fields = existing_fields(
        Repair,
        "id",
        "created_at",
        "updated_at",
        "archived_at",
    )

    ordering = existing_fields(
        Repair,
        "-created_at",
    )


@admin.register(RepairAssignment)
class RepairAssignmentAdmin(admin.ModelAdmin):
    list_display = existing_fields(
        RepairAssignment,
        "repair",
        "technician",
        "status",
        "is_active",
        "assigned_by",
        "assigned_at",
        "started_at",
        "ended_at",
        "created_at",
    )

    list_filter = existing_fields(
        RepairAssignment,
        "status",
        "is_active",
        "archived_at",
    )

    search_fields = existing_fields(
        RepairAssignment,
        "assignment_reason",
        "technician_observations",
        "completion_notes",
        "reassignment_reason",
        "rejection_reason",
        "cancellation_reason",
    )

    readonly_fields = existing_fields(
        RepairAssignment,
        "id",
        "created_at",
        "updated_at",
        "archived_at",
    )

    ordering = existing_fields(
        RepairAssignment,
        "-assigned_at",
        "-created_at",
    )


@admin.register(RepairStatusHistory)
class RepairStatusHistoryAdmin(
    admin.ModelAdmin
):
    list_display = existing_fields(
        RepairStatusHistory,
        "repair",
        "previous_status",
        "new_status",
        "changed_by",
        "changed_at",
        "duration_minutes",
        "changed_automatically",
        "source",
        "created_at",
    )

    list_filter = existing_fields(
        RepairStatusHistory,
        "previous_status",
        "new_status",
        "changed_automatically",
        "source",
        "archived_at",
    )

    search_fields = existing_fields(
        RepairStatusHistory,
        "reason",
        "observations",
        "source",
    )

    readonly_fields = existing_fields(
        RepairStatusHistory,
        "id",
        "created_at",
        "updated_at",
        "archived_at",
    )

    ordering = existing_fields(
        RepairStatusHistory,
        "-changed_at",
        "-created_at",
    )


@admin.register(RepairDiagnosis)
class RepairDiagnosisAdmin(admin.ModelAdmin):
    list_display = existing_fields(
        RepairDiagnosis,
        "repair",
        "diagnosis_type",
        "severity",
        "repairability",
        "technician",
        "is_main_diagnosis",
        "is_confirmed",
        "diagnosed_at",
        "created_at",
    )

    list_filter = existing_fields(
        RepairDiagnosis,
        "diagnosis_type",
        "severity",
        "repairability",
        "is_main_diagnosis",
        "is_confirmed",
        "requires_parts",
        "requires_external_service",
        "requires_additional_testing",
        "requires_disassembly",
        "archived_at",
    )

    search_fields = existing_fields(
        RepairDiagnosis,
        "reported_symptoms",
        "observed_symptoms",
        "probable_cause",
        "confirmed_cause",
        "technical_diagnosis",
        "recommended_work",
        "required_parts_description",
        "observations",
    )

    readonly_fields = existing_fields(
        RepairDiagnosis,
        "id",
        "created_at",
        "updated_at",
        "archived_at",
    )

    ordering = existing_fields(
        RepairDiagnosis,
        "-diagnosed_at",
        "-created_at",
    )


class RepairChecklistItemInline(
    admin.TabularInline
):
    model = RepairChecklistItem
    extra = 0

    fields = existing_fields(
        RepairChecklistItem,
        "code",
        "name",
        "category",
        "status",
        "is_required",
        "requires_photo",
        "requires_observation",
        "checked_by",
        "checked_at",
        "display_order",
    )

    readonly_fields = existing_fields(
        RepairChecklistItem,
        "checked_by",
        "checked_at",
        "created_at",
        "updated_at",
    )

    ordering = existing_fields(
        RepairChecklistItem,
        "display_order",
        "created_at",
    )


@admin.register(RepairChecklist)
class RepairChecklistAdmin(admin.ModelAdmin):
    list_display = existing_fields(
        RepairChecklist,
        "repair",
        "name",
        "status",
        "is_main_checklist",
        "started_by",
        "started_at",
        "completed_by",
        "completed_at",
        "created_at",
    )

    list_filter = existing_fields(
        RepairChecklist,
        "status",
        "is_main_checklist",
        "archived_at",
    )

    search_fields = existing_fields(
        RepairChecklist,
        "name",
        "description",
        "observations",
    )

    readonly_fields = existing_fields(
        RepairChecklist,
        "id",
        "created_at",
        "updated_at",
        "archived_at",
    )

    inlines = (
        RepairChecklistItemInline,
    )

    ordering = existing_fields(
        RepairChecklist,
        "-created_at",
    )


@admin.register(RepairChecklistItem)
class RepairChecklistItemAdmin(
    admin.ModelAdmin
):
    list_display = existing_fields(
        RepairChecklistItem,
        "checklist",
        "code",
        "name",
        "category",
        "status",
        "is_required",
        "requires_photo",
        "checked_by",
        "checked_at",
        "display_order",
        "created_at",
    )

    list_filter = existing_fields(
        RepairChecklistItem,
        "category",
        "status",
        "is_required",
        "requires_photo",
        "requires_observation",
        "archived_at",
    )

    search_fields = existing_fields(
        RepairChecklistItem,
        "code",
        "name",
        "description",
        "instructions",
        "observation",
    )

    readonly_fields = existing_fields(
        RepairChecklistItem,
        "id",
        "created_at",
        "updated_at",
        "archived_at",
    )

    ordering = existing_fields(
        RepairChecklistItem,
        "display_order",
        "created_at",
    )


@admin.register(RepairComponent)
class RepairComponentAdmin(admin.ModelAdmin):
    list_display = existing_fields(
        RepairComponent,
        "repair",
        "component",
        "status",
        "movement_type",
        "quantity",
        "reserved_quantity",
        "delivered_quantity",
        "installed_quantity",
        "returned_quantity",
        "consumed_quantity",
        "created_at",
    )

    list_filter = existing_fields(
        RepairComponent,
        "status",
        "movement_type",
        "removed_part_disposition",
        "archived_at",
    )

    search_fields = existing_fields(
        RepairComponent,
        "removed_serial_number",
        "notes",
        "removed_part_notes",
    )

    readonly_fields = existing_fields(
        RepairComponent,
        "id",
        "created_at",
        "updated_at",
        "archived_at",
    )

    ordering = existing_fields(
        RepairComponent,
        "-created_at",
    )


@admin.register(RepairPhoto)
class RepairPhotoAdmin(admin.ModelAdmin):
    list_display = existing_fields(
        RepairPhoto,
        "repair",
        "title",
        "category",
        "stage",
        "is_required",
        "counts_for_minimum",
        "is_verified",
        "taken_by",
        "taken_at",
        "created_at",
    )

    list_filter = existing_fields(
        RepairPhoto,
        "category",
        "stage",
        "is_required",
        "counts_for_minimum",
        "is_verified",
        "archived_at",
    )

    search_fields = existing_fields(
        RepairPhoto,
        "original_filename",
        "title",
        "description",
        "verification_notes",
        "mime_type",
    )

    readonly_fields = existing_fields(
        RepairPhoto,
        "id",
        "original_filename",
        "file_size",
        "mime_type",
        "created_at",
        "updated_at",
        "archived_at",
    )

    ordering = existing_fields(
        RepairPhoto,
        "display_order",
        "created_at",
    )


@admin.register(RepairTest)
class RepairTestAdmin(admin.ModelAdmin):
    list_display = existing_fields(
        RepairTest,
        "repair",
        "name",
        "test_type",
        "status",
        "result",
        "is_required",
        "tested_by",
        "performed_by",
        "tested_at",
        "performed_at",
        "is_verified",
        "created_at",
    )

    list_filter = existing_fields(
        RepairTest,
        "test_type",
        "status",
        "result",
        "is_required",
        "is_verified",
        "archived_at",
    )

    search_fields = existing_fields(
        RepairTest,
        "name",
        "description",
        "instructions",
        "result_value",
        "expected_value",
        "unit",
        "observations",
        "failure_reason",
        "verification_notes",
    )

    readonly_fields = existing_fields(
        RepairTest,
        "id",
        "created_at",
        "updated_at",
        "archived_at",
    )

    ordering = existing_fields(
        RepairTest,
        "display_order",
        "created_at",
    )


@admin.register(RepairSNMPValidation)
class RepairSNMPValidationAdmin(
    admin.ModelAdmin
):
    list_display = existing_fields(
        RepairSNMPValidation,
        "repair",
        "ip_address",
        "host",
        "port",
        "status",
        "success",
        "is_successful",
        "serial_matches",
        "brand_matches",
        "model_matches",
        "validated_by",
        "validated_at",
        "started_at",
        "completed_at",
        "created_at",
    )

    list_filter = existing_fields(
        RepairSNMPValidation,
        "status",
        "success",
        "is_successful",
        "serial_matches",
        "brand_matches",
        "model_matches",
        "archived_at",
    )

    search_fields = existing_fields(
        RepairSNMPValidation,
        "ip_address",
        "host",
        "system_name",
        "device_description",
        "device_serial_number",
        "detected_serial_number",
        "detected_brand",
        "detected_model",
        "error_message",
        "observations",
    )

    readonly_fields = existing_fields(
        RepairSNMPValidation,
        "id",
        "created_at",
        "updated_at",
        "archived_at",
    )

    ordering = existing_fields(
        RepairSNMPValidation,
        "-created_at",
    )

NEW_REPAIR_PART_MODELS = (
    RepairPartRequest, RepairPartRequestItem, RepairPartRequestReview,
    RepairPartRequestDecision, RepairPartSource, RepairPartWithdrawal,
    RepairPartDelivery, RepairPartReplacement, RepairPartRequestHistory,
    RepairPartRequestComment, RepairPartRequestAttachment,
    RepairPartRequestNotification,
)

for model in NEW_REPAIR_PART_MODELS:
    admin.site.register(
        model,
        type(
            f"{model.__name__}Admin",
            (admin.ModelAdmin,),
            {
                "readonly_fields": existing_fields(
                    model, "id", "created_at", "updated_at", "archived_at"
                ),
                "ordering": existing_fields(model, "-created_at"),
            },
        ),
    )
