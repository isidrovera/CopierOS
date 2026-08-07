# -*- coding: utf-8 -*-

from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from django.utils.html import format_html

from .models import (
    AttendanceAuditLog,
    AttendanceCorrection,
    AttendanceDevice,
    AttendanceExportBatch,
    AttendanceExportItem,
    AttendanceImportBatch,
    AttendanceImportItem,
    AttendanceIncident,
    AttendanceNotification,
    AttendancePolicy,
    AttendanceProcessingItem,
    AttendanceProcessingRun,
    AttendanceRecord,
    AttendanceReport,
    AttendanceReportDelivery,
    AttendanceReportSchedule,
    DailyAttendance,
    EmployeeCalendarAssignment,
    EmployeeDevicePermission,
    EmployeePolicyAssignment,
    EmployeeProfile,
    EmployeeScheduleAssignment,
    HolidayCalendar,
    LeaveRequest,
    MonthlyAttendanceSummary,
    OperationalWorkEvent,
    OperationalWorkSession,
    OvertimeRequest,
    WorkLocation,
    WorkSchedule,
)


class ArchiveAdminMixin:
    actions = ("archive_selected", "restore_selected")

    @admin.action(description="Archivar registros seleccionados")
    def archive_selected(self, request, queryset):
        archived_count = 0
        skipped_count = 0

        for instance in queryset:
            method = getattr(instance, "archive", None)
            if not callable(method):
                skipped_count += 1
                continue

            try:
                method(
                    user=request.user,
                    reason="Archivado desde el panel de administración.",
                )
                archived_count += 1
            except Exception:
                skipped_count += 1

        if archived_count:
            self.message_user(
                request,
                f"{archived_count} registro(s) archivado(s).",
            )

        if skipped_count:
            self.message_user(
                request,
                f"{skipped_count} registro(s) no pudieron archivarse.",
                level="WARNING",
            )

    @admin.action(description="Restaurar registros seleccionados")
    def restore_selected(self, request, queryset):
        restored_count = 0
        skipped_count = 0

        for instance in queryset:
            method = getattr(instance, "restore", None)
            if not callable(method):
                skipped_count += 1
                continue

            try:
                method(user=request.user)
                restored_count += 1
            except Exception:
                skipped_count += 1

        if restored_count:
            self.message_user(
                request,
                f"{restored_count} registro(s) restaurado(s).",
            )

        if skipped_count:
            self.message_user(
                request,
                f"{skipped_count} registro(s) no pudieron restaurarse.",
                level="WARNING",
            )


class ReadOnlyAuditAdminMixin:
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class StatusBadgeAdminMixin:
    @admin.display(description="Estado")
    def status_badge(self, obj):
        status = getattr(obj, "status", "")
        display_method = getattr(obj, "get_status_display", None)
        label = display_method() if callable(display_method) else status

        colors = {
            "draft": "#6b7280",
            "pending": "#d97706",
            "pending_validation": "#d97706",
            "pending_import": "#d97706",
            "pending_review": "#d97706",
            "queued": "#2563eb",
            "scheduled": "#2563eb",
            "processing": "#2563eb",
            "running": "#2563eb",
            "validating": "#2563eb",
            "importing": "#2563eb",
            "delivering": "#2563eb",
            "active": "#059669",
            "validated": "#059669",
            "valid": "#059669",
            "completed": "#059669",
            "delivered": "#059669",
            "read": "#059669",
            "downloaded": "#059669",
            "imported": "#059669",
            "exported": "#059669",
            "approved": "#059669",
            "success": "#059669",
            "closed": "#059669",
            "validated_with_warnings": "#ca8a04",
            "valid_with_warnings": "#ca8a04",
            "partially_completed": "#ca8a04",
            "exported_with_warnings": "#ca8a04",
            "success_with_warnings": "#ca8a04",
            "paused": "#7c3aed",
            "rejected": "#dc2626",
            "failed": "#dc2626",
            "error": "#dc2626",
            "invalid": "#dc2626",
            "delivery_failed": "#dc2626",
            "cancelled": "#4b5563",
            "disabled": "#4b5563",
            "expired": "#4b5563",
            "archived": "#4b5563",
            "rolled_back": "#7c3aed",
            "skipped": "#6b7280",
            "unchanged": "#6b7280",
        }

        return format_html(
            '<span style="display:inline-block;padding:3px 8px;'
            'border-radius:10px;background:{};color:#fff;'
            'font-size:11px;font-weight:600;">{}</span>',
            colors.get(status, "#374151"),
            label,
        )


class DynamicAttendanceAdmin(ArchiveAdminMixin, admin.ModelAdmin):
    list_per_page = 50
    save_on_top = True

    preferred_list_fields = (
        "id",
        "code",
        "name",
        "title",
        "employee_code",
        "batch_number",
        "report_number",
        "request_number",
        "correction_number",
        "session_number",
        "run_number",
        "employee_profile",
        "status",
        "date",
        "record_date",
        "incident_date",
        "overtime_date",
        "start_date",
        "end_date",
        "started_at",
        "finished_at",
        "occurred_at",
        "created_at",
        "updated_at",
    )

    preferred_filter_fields = (
        "status",
        "is_active",
        "requires_review",
        "is_duplicate",
        "dry_run",
        "record_type",
        "source_type",
        "item_type",
        "result_type",
        "process_type",
        "trigger_type",
        "scope_type",
        "report_type",
        "file_format",
        "generation_source",
        "created_at",
        "updated_at",
        "archived_at",
    )

    preferred_search_fields = (
        "code",
        "name",
        "title",
        "description",
        "employee_code",
        "batch_number",
        "report_number",
        "request_number",
        "correction_number",
        "session_number",
        "run_number",
        "external_reference",
        "object_id",
        "object_model",
        "error_code",
        "error_message",
    )

    preferred_readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    def _concrete_field_names(self):
        return {
            field.name
            for field in self.model._meta.get_fields()
            if getattr(field, "concrete", False)
        }

    def _existing_fields(self, candidates):
        names = self._concrete_field_names()
        return [name for name in candidates if name in names]

    def get_list_display(self, request):
        fields = self._existing_fields(self.preferred_list_fields)
        if not fields:
            return (self.model._meta.pk.name,)
        return tuple(fields[:8])

    def get_list_filter(self, request):
        return tuple(self._existing_fields(self.preferred_filter_fields))

    def get_search_fields(self, request):
        result = []

        for name in self.preferred_search_fields:
            try:
                field = self.model._meta.get_field(name)
            except FieldDoesNotExist:
                continue

            if field.get_internal_type() in (
                "CharField",
                "TextField",
                "EmailField",
                "SlugField",
                "UUIDField",
            ):
                result.append(name)

        return tuple(result)

    def get_readonly_fields(self, request, obj=None):
        return tuple(self._existing_fields(self.preferred_readonly_fields))

    def get_list_select_related(self, request):
        relations = []

        for field in self.model._meta.get_fields():
            if (
                getattr(field, "concrete", False)
                and getattr(field, "many_to_one", False)
                and not getattr(field, "auto_created", False)
            ):
                relations.append(field.name)

        return tuple(relations[:6])


class DynamicStatusAttendanceAdmin(
    StatusBadgeAdminMixin,
    DynamicAttendanceAdmin,
):
    def get_list_display(self, request):
        fields = list(super().get_list_display(request))

        if "status" in fields:
            fields[fields.index("status")] = "status_badge"

        return tuple(fields)


class DynamicReadOnlyAttendanceAdmin(
    ReadOnlyAuditAdminMixin,
    DynamicAttendanceAdmin,
):
    actions = ()


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(DynamicAttendanceAdmin):
    pass


@admin.register(WorkLocation)
class WorkLocationAdmin(DynamicAttendanceAdmin):
    pass


@admin.register(WorkSchedule)
class WorkScheduleAdmin(DynamicAttendanceAdmin):
    pass


@admin.register(EmployeeScheduleAssignment)
class EmployeeScheduleAssignmentAdmin(DynamicAttendanceAdmin):
    pass


@admin.register(HolidayCalendar)
class HolidayCalendarAdmin(DynamicAttendanceAdmin):
    pass


@admin.register(EmployeeCalendarAssignment)
class EmployeeCalendarAssignmentAdmin(DynamicAttendanceAdmin):
    pass


@admin.register(AttendanceDevice)
class AttendanceDeviceAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(EmployeeDevicePermission)
class EmployeeDevicePermissionAdmin(DynamicAttendanceAdmin):
    pass


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(DynamicAttendanceAdmin):
    pass


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(AttendanceIncident)
class AttendanceIncidentAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(LeaveRequest)
class LeaveRequestAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(AttendanceCorrection)
class AttendanceCorrectionAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(OperationalWorkSession)
class OperationalWorkSessionAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(OperationalWorkEvent)
class OperationalWorkEventAdmin(DynamicAttendanceAdmin):
    pass


@admin.register(AttendanceAuditLog)
class AttendanceAuditLogAdmin(DynamicReadOnlyAttendanceAdmin):
    pass


@admin.register(MonthlyAttendanceSummary)
class MonthlyAttendanceSummaryAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(AttendancePolicy)
class AttendancePolicyAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(EmployeePolicyAssignment)
class EmployeePolicyAssignmentAdmin(DynamicAttendanceAdmin):
    pass


@admin.register(OvertimeRequest)
class OvertimeRequestAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(AttendanceNotification)
class AttendanceNotificationAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(AttendanceReport)
class AttendanceReportAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(AttendanceReportSchedule)
class AttendanceReportScheduleAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(AttendanceReportDelivery)
class AttendanceReportDeliveryAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(AttendanceProcessingRun)
class AttendanceProcessingRunAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(AttendanceProcessingItem)
class AttendanceProcessingItemAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(AttendanceImportBatch)
class AttendanceImportBatchAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(AttendanceImportItem)
class AttendanceImportItemAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(AttendanceExportBatch)
class AttendanceExportBatchAdmin(DynamicStatusAttendanceAdmin):
    pass


@admin.register(AttendanceExportItem)
class AttendanceExportItemAdmin(DynamicStatusAttendanceAdmin):
    pass
