# -*- coding: utf-8 -*-

from django.contrib import admin
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
    """
    Acciones comunes para los modelos que manejan archivado.
    """

    actions = (
        "archive_selected",
        "restore_selected",
    )

    @admin.action(
        description="Archivar registros seleccionados",
    )
    def archive_selected(
        self,
        request,
        queryset,
    ):
        archived_count = 0
        skipped_count = 0

        for instance in queryset:
            if not hasattr(instance, "archive"):
                skipped_count += 1
                continue

            try:
                instance.archive(
                    user=request.user,
                    reason=(
                        "Archivado desde el panel "
                        "de administración."
                    ),
                )
                archived_count += 1
            except Exception:
                skipped_count += 1

        if archived_count:
            self.message_user(
                request,
                (
                    f"{archived_count} registro(s) "
                    "archivado(s)."
                ),
            )

        if skipped_count:
            self.message_user(
                request,
                (
                    f"{skipped_count} registro(s) no pudieron "
                    "archivarse."
                ),
                level="WARNING",
            )

    @admin.action(
        description="Restaurar registros seleccionados",
    )
    def restore_selected(
        self,
        request,
        queryset,
    ):
        restored_count = 0
        skipped_count = 0

        for instance in queryset:
            if not hasattr(instance, "restore"):
                skipped_count += 1
                continue

            try:
                instance.restore(
                    user=request.user,
                )
                restored_count += 1
            except Exception:
                skipped_count += 1

        if restored_count:
            self.message_user(
                request,
                (
                    f"{restored_count} registro(s) "
                    "restaurado(s)."
                ),
            )

        if skipped_count:
            self.message_user(
                request,
                (
                    f"{skipped_count} registro(s) no pudieron "
                    "restaurarse."
                ),
                level="WARNING",
            )


class ReadOnlyAuditAdminMixin:
    """
    Evita modificar registros históricos desde el administrador.
    """

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False


class StatusColorAdminMixin:
    """
    Muestra el estado con una etiqueta visual.
    """

    status_field_name = "status"

    @admin.display(
        description="Estado",
        ordering="status",
    )
    def status_badge(
        self,
        obj,
    ):
        status = getattr(
            obj,
            self.status_field_name,
            "",
        )

        label_method = getattr(
            obj,
            f"get_{self.status_field_name}_display",
            None,
        )

        label = (
            label_method()
            if callable(label_method)
            else status
        )

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

        color = colors.get(
            status,
            "#374151",
        )

        return format_html(
            (
                '<span style="'
                "display:inline-block;"
                "padding:3px 8px;"
                "border-radius:10px;"
                "background:{};"
                "color:#fff;"
                "font-size:11px;"
                'font-weight:600;">'
                "{}"
                "</span>"
            ),
            color,
            label,
        )


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "employee_code",
        "user",
        "company_name",
        "department_name",
        "job_title",
        "employment_status",
        "is_active",
        "created_at",
    )

    list_filter = (
        "employment_status",
        "is_active",
        "company_name",
        "department_name",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "employee_code",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "company_name",
        "department_name",
        "job_title",
    )

    autocomplete_fields = (
        "user",
        "supervisor",
        "default_work_location",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    ordering = (
        "employee_code",
    )

    list_select_related = (
        "user",
        "supervisor",
        "default_work_location",
    )


@admin.register(WorkLocation)
class WorkLocationAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name",
        "location_type",
        "company_name",
        "is_active",
        "requires_geolocation",
        "created_at",
    )

    list_filter = (
        "location_type",
        "is_active",
        "requires_geolocation",
        "company_name",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "code",
        "name",
        "company_name",
        "address",
        "city",
        "district",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    ordering = (
        "name",
    )


@admin.register(WorkSchedule)
class WorkScheduleAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name",
        "schedule_type",
        "timezone_name",
        "is_active",
        "created_at",
    )

    list_filter = (
        "schedule_type",
        "is_active",
        "timezone_name",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "code",
        "name",
        "description",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    ordering = (
        "name",
    )


@admin.register(EmployeeScheduleAssignment)
class EmployeeScheduleAssignmentAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "employee_profile",
        "work_schedule",
        "start_date",
        "end_date",
        "priority",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "priority",
        "start_date",
        "end_date",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "employee_profile__employee_code",
        "employee_profile__user__first_name",
        "employee_profile__user__last_name",
        "work_schedule__code",
        "work_schedule__name",
    )

    autocomplete_fields = (
        "employee_profile",
        "work_schedule",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "start_date"

    list_select_related = (
        "employee_profile",
        "work_schedule",
    )


@admin.register(HolidayCalendar)
class HolidayCalendarAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "name",
        "calendar_type",
        "year",
        "country_code",
        "is_active",
        "created_at",
    )

    list_filter = (
        "calendar_type",
        "year",
        "country_code",
        "is_active",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "name",
        "description",
        "country_code",
        "region_name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    ordering = (
        "-year",
        "name",
    )


@admin.register(EmployeeCalendarAssignment)
class EmployeeCalendarAssignmentAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "employee_profile",
        "holiday_calendar",
        "start_date",
        "end_date",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "start_date",
        "end_date",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "employee_profile__employee_code",
        "employee_profile__user__first_name",
        "employee_profile__user__last_name",
        "holiday_calendar__name",
    )

    autocomplete_fields = (
        "employee_profile",
        "holiday_calendar",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    list_select_related = (
        "employee_profile",
        "holiday_calendar",
    )


@admin.register(AttendanceDevice)
class AttendanceDeviceAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name",
        "device_type",
        "work_location",
        "status_badge",
        "is_active",
        "last_seen_at",
    )

    list_filter = (
        "device_type",
        "status",
        "is_active",
        "work_location",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "code",
        "name",
        "serial_number",
        "manufacturer",
        "model_name",
        "ip_address",
        "hostname",
    )

    autocomplete_fields = (
        "work_location",
    )

    readonly_fields = (
        "id",
        "last_seen_at",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    list_select_related = (
        "work_location",
    )


@admin.register(EmployeeDevicePermission)
class EmployeeDevicePermissionAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "employee_profile",
        "attendance_device",
        "permission_type",
        "start_at",
        "end_at",
        "is_active",
        "created_at",
    )

    list_filter = (
        "permission_type",
        "is_active",
        "start_at",
        "end_at",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "employee_profile__employee_code",
        "employee_profile__user__first_name",
        "employee_profile__user__last_name",
        "attendance_device__code",
        "attendance_device__name",
    )

    autocomplete_fields = (
        "employee_profile",
        "attendance_device",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    list_select_related = (
        "employee_profile",
        "attendance_device",
    )


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "employee_profile",
        "recorded_at",
        "record_type",
        "source_type",
        "attendance_device",
        "is_valid",
        "requires_review",
    )

    list_filter = (
        "record_type",
        "source_type",
        "is_valid",
        "requires_review",
        "recorded_at",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "employee_profile__employee_code",
        "employee_profile__user__first_name",
        "employee_profile__user__last_name",
        "attendance_device__code",
        "external_reference",
        "device_record_id",
    )

    autocomplete_fields = (
        "employee_profile",
        "attendance_device",
        "work_location",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "recorded_at"

    list_select_related = (
        "employee_profile",
        "attendance_device",
        "work_location",
    )


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "employee_profile",
        "date",
        "status_badge",
        "scheduled_minutes",
        "worked_minutes",
        "late_minutes",
        "overtime_minutes",
        "is_closed",
    )

    list_filter = (
        "status",
        "is_closed",
        "date",
        "work_location",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "employee_profile__employee_code",
        "employee_profile__user__first_name",
        "employee_profile__user__last_name",
    )

    autocomplete_fields = (
        "employee_profile",
        "work_schedule",
        "work_location",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "date"

    list_select_related = (
        "employee_profile",
        "work_schedule",
        "work_location",
    )


@admin.register(AttendanceIncident)
class AttendanceIncidentAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "incident_number",
        "employee_profile",
        "incident_type",
        "incident_date",
        "status_badge",
        "severity",
        "requires_review",
    )

    list_filter = (
        "incident_type",
        "status",
        "severity",
        "requires_review",
        "incident_date",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "incident_number",
        "employee_profile__employee_code",
        "employee_profile__user__first_name",
        "employee_profile__user__last_name",
        "description",
    )

    autocomplete_fields = (
        "employee_profile",
        "daily_attendance",
        "attendance_record",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "incident_date"

    list_select_related = (
        "employee_profile",
        "daily_attendance",
        "attendance_record",
    )


@admin.register(LeaveRequest)
class LeaveRequestAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "request_number",
        "employee_profile",
        "leave_type",
        "start_date",
        "end_date",
        "status_badge",
        "requested_at",
    )

    list_filter = (
        "leave_type",
        "status",
        "start_date",
        "end_date",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "request_number",
        "employee_profile__employee_code",
        "employee_profile__user__first_name",
        "employee_profile__user__last_name",
        "reason",
    )

    autocomplete_fields = (
        "employee_profile",
    )

    readonly_fields = (
        "id",
        "requested_at",
        "approved_at",
        "rejected_at",
        "cancelled_at",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "start_date"

    list_select_related = (
        "employee_profile",
    )


@admin.register(AttendanceCorrection)
class AttendanceCorrectionAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "correction_number",
        "employee_profile",
        "correction_type",
        "correction_date",
        "status_badge",
        "requested_at",
    )

    list_filter = (
        "correction_type",
        "status",
        "correction_date",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "correction_number",
        "employee_profile__employee_code",
        "employee_profile__user__first_name",
        "employee_profile__user__last_name",
        "reason",
    )

    autocomplete_fields = (
        "employee_profile",
        "attendance_record",
        "daily_attendance",
    )

    readonly_fields = (
        "id",
        "requested_at",
        "approved_at",
        "rejected_at",
        "applied_at",
        "cancelled_at",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "correction_date"

    list_select_related = (
        "employee_profile",
        "attendance_record",
        "daily_attendance",
    )


@admin.register(OperationalWorkSession)
class OperationalWorkSessionAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "session_number",
        "employee_profile",
        "session_type",
        "started_at",
        "finished_at",
        "status_badge",
        "productive_minutes",
    )

    list_filter = (
        "session_type",
        "status",
        "started_at",
        "work_location",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "session_number",
        "employee_profile__employee_code",
        "employee_profile__user__first_name",
        "employee_profile__user__last_name",
        "title",
        "external_reference",
    )

    autocomplete_fields = (
        "employee_profile",
        "work_location",
        "daily_attendance",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "started_at"

    list_select_related = (
        "employee_profile",
        "work_location",
        "daily_attendance",
    )


@admin.register(OperationalWorkEvent)
class OperationalWorkEventAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "operational_session",
        "event_type",
        "occurred_at",
        "duration_minutes",
        "is_productive",
        "requires_review",
    )

    list_filter = (
        "event_type",
        "is_productive",
        "requires_review",
        "occurred_at",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "operational_session__session_number",
        "description",
        "external_reference",
    )

    autocomplete_fields = (
        "operational_session",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "occurred_at"

    list_select_related = (
        "operational_session",
    )


@admin.register(AttendanceAuditLog)
class AttendanceAuditLogAdmin(
    ReadOnlyAuditAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "occurred_at",
        "action_type",
        "user",
        "employee_profile",
        "object_model",
        "object_id",
        "success",
        "requires_review",
    )

    list_filter = (
        "action_type",
        "success",
        "requires_review",
        "occurred_at",
        "object_model",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "employee_profile__employee_code",
        "object_model",
        "object_id",
        "description",
        "ip_address",
        "correlation_id",
    )

    readonly_fields = (
        "id",
        "occurred_at",
        "created_at",
    )

    date_hierarchy = "occurred_at"

    list_select_related = (
        "user",
        "employee_profile",
        "content_type",
    )


@admin.register(MonthlyAttendanceSummary)
class MonthlyAttendanceSummaryAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "employee_profile",
        "year",
        "month",
        "status_badge",
        "scheduled_days",
        "worked_days",
        "absence_days",
        "late_minutes",
        "overtime_minutes",
        "is_closed",
    )

    list_filter = (
        "status",
        "year",
        "month",
        "is_closed",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "employee_profile__employee_code",
        "employee_profile__user__first_name",
        "employee_profile__user__last_name",
    )

    autocomplete_fields = (
        "employee_profile",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    list_select_related = (
        "employee_profile",
    )


@admin.register(AttendancePolicy)
class AttendancePolicyAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name",
        "policy_type",
        "status_badge",
        "effective_from",
        "effective_until",
        "priority",
    )

    list_filter = (
        "policy_type",
        "status",
        "effective_from",
        "effective_until",
        "priority",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "code",
        "name",
        "description",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    ordering = (
        "-priority",
        "name",
    )


@admin.register(EmployeePolicyAssignment)
class EmployeePolicyAssignmentAdmin(
    ArchiveAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "employee_profile",
        "attendance_policy",
        "start_date",
        "end_date",
        "priority",
        "is_active",
    )

    list_filter = (
        "is_active",
        "priority",
        "start_date",
        "end_date",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "employee_profile__employee_code",
        "employee_profile__user__first_name",
        "employee_profile__user__last_name",
        "attendance_policy__code",
        "attendance_policy__name",
    )

    autocomplete_fields = (
        "employee_profile",
        "attendance_policy",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    list_select_related = (
        "employee_profile",
        "attendance_policy",
    )


@admin.register(OvertimeRequest)
class OvertimeRequestAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "request_number",
        "employee_profile",
        "overtime_type",
        "overtime_date",
        "requested_minutes",
        "approved_minutes",
        "status_badge",
    )

    list_filter = (
        "overtime_type",
        "status",
        "overtime_date",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "request_number",
        "employee_profile__employee_code",
        "employee_profile__user__first_name",
        "employee_profile__user__last_name",
        "reason",
    )

    autocomplete_fields = (
        "employee_profile",
        "daily_attendance",
    )

    readonly_fields = (
        "id",
        "requested_at",
        "approved_at",
        "rejected_at",
        "cancelled_at",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "overtime_date"

    list_select_related = (
        "employee_profile",
        "daily_attendance",
    )


@admin.register(AttendanceNotification)
class AttendanceNotificationAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "title",
        "notification_type",
        "recipient_type",
        "recipient_user",
        "priority",
        "status_badge",
        "scheduled_at",
        "sent_at",
    )

    list_filter = (
        "notification_type",
        "recipient_type",
        "priority",
        "status",
        "requires_action",
        "scheduled_at",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "title",
        "message",
        "recipient_user__username",
        "recipient_user__first_name",
        "recipient_user__last_name",
        "deduplication_key",
        "batch_key",
        "correlation_id",
    )

    autocomplete_fields = (
        "recipient_user",
        "employee_profile",
    )

    readonly_fields = (
        "id",
        "processing_started_at",
        "sent_at",
        "delivered_at",
        "read_at",
        "failed_at",
        "cancelled_at",
        "expired_at",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "created_at"

    list_select_related = (
        "recipient_user",
        "employee_profile",
        "content_type",
    )


@admin.register(AttendanceReport)
class AttendanceReportAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "report_number",
        "name",
        "report_type",
        "file_format",
        "start_date",
        "end_date",
        "status_badge",
        "requested_by",
        "created_at",
    )

    list_filter = (
        "report_type",
        "period_type",
        "file_format",
        "status",
        "generation_source",
        "start_date",
        "end_date",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "report_number",
        "name",
        "description",
        "requested_by__username",
        "requested_by__first_name",
        "requested_by__last_name",
        "checksum",
    )

    autocomplete_fields = (
        "requested_by",
        "created_by",
        "updated_by",
        "cancelled_by",
        "archived_by",
    )

    filter_horizontal = (
        "employee_profiles",
        "work_locations",
        "work_schedules",
        "allowed_users",
    )

    readonly_fields = (
        "id",
        "requested_at",
        "queued_at",
        "processing_started_at",
        "processing_finished_at",
        "first_downloaded_at",
        "last_downloaded_at",
        "created_at",
        "updated_at",
        "archived_at",
        "archived_by",
    )

    date_hierarchy = "created_at"

    list_select_related = (
        "requested_by",
        "created_by",
    )


@admin.register(AttendanceReportSchedule)
class AttendanceReportScheduleAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "code",
        "name",
        "report_type",
        "frequency",
        "period_mode",
        "status_badge",
        "next_execution_at",
        "last_success_at",
    )

    list_filter = (
        "frequency",
        "period_mode",
        "report_type",
        "file_format",
        "status",
        "delivery_mode",
        "next_execution_at",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "code",
        "name",
        "description",
        "cron_expression",
        "last_error",
    )

    filter_horizontal = (
        "employee_profiles",
        "work_locations",
        "work_schedules",
        "recipient_users",
    )

    autocomplete_fields = (
        "last_report",
        "current_report",
        "created_by",
        "updated_by",
        "activated_by",
        "paused_by",
        "resumed_by",
        "cancelled_by",
        "archived_by",
    )

    readonly_fields = (
        "id",
        "activated_at",
        "paused_at",
        "resumed_at",
        "last_execution_started_at",
        "last_execution_finished_at",
        "last_success_at",
        "last_failure_at",
        "completed_at",
        "cancelled_at",
        "created_at",
        "updated_at",
        "archived_at",
    )

    date_hierarchy = "created_at"


@admin.register(AttendanceReportDelivery)
class AttendanceReportDeliveryAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "report",
        "recipient_name",
        "recipient_email",
        "delivery_channel",
        "status_badge",
        "sent_at",
        "delivered_at",
        "download_count",
    )

    list_filter = (
        "recipient_type",
        "delivery_channel",
        "status",
        "failure_type",
        "scheduled_at",
        "sent_at",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "report__report_number",
        "recipient_name",
        "recipient_email",
        "recipient_phone",
        "provider_message_id",
        "deduplication_key",
        "batch_key",
        "correlation_id",
    )

    autocomplete_fields = (
        "report",
        "report_schedule",
        "recipient_user",
        "employee_profile",
        "cancelled_by",
        "created_by",
        "updated_by",
        "archived_by",
    )

    readonly_fields = (
        "id",
        "download_token",
        "processing_started_at",
        "sent_at",
        "delivered_at",
        "first_read_at",
        "last_read_at",
        "first_downloaded_at",
        "last_downloaded_at",
        "failed_at",
        "cancelled_at",
        "created_at",
        "updated_at",
        "archived_at",
    )

    date_hierarchy = "created_at"

    list_select_related = (
        "report",
        "report_schedule",
        "recipient_user",
        "employee_profile",
    )


@admin.register(AttendanceProcessingRun)
class AttendanceProcessingRunAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "run_number",
        "process_type",
        "scope_type",
        "status_badge",
        "progress_percentage",
        "processed_records",
        "total_records",
        "requested_at",
    )

    list_filter = (
        "process_type",
        "status",
        "trigger_type",
        "scope_type",
        "result_type",
        "requested_at",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "run_number",
        "title",
        "description",
        "task_id",
        "worker_name",
        "queue_name",
        "batch_key",
        "correlation_id",
        "error_code",
        "error_message",
    )

    autocomplete_fields = (
        "employee_profile",
        "work_location",
        "requested_by",
        "parent_run",
        "retry_of",
        "cancel_requested_by",
        "created_by",
        "updated_by",
        "archived_by",
    )

    readonly_fields = (
        "id",
        "queued_at",
        "started_at",
        "heartbeat_at",
        "finished_at",
        "cancel_requested_at",
        "cancelled_at",
        "created_at",
        "updated_at",
        "archived_at",
    )

    date_hierarchy = "requested_at"

    list_select_related = (
        "employee_profile",
        "work_location",
        "requested_by",
    )


@admin.register(AttendanceProcessingItem)
class AttendanceProcessingItemAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "processing_run",
        "sequence_number",
        "item_type",
        "action_type",
        "status_badge",
        "result_type",
        "employee_profile",
        "requires_review",
    )

    list_filter = (
        "item_type",
        "action_type",
        "status",
        "result_type",
        "error_category",
        "requires_review",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "processing_run__run_number",
        "object_model",
        "object_id",
        "object_representation",
        "external_reference",
        "error_code",
        "error_message",
    )

    autocomplete_fields = (
        "processing_run",
        "employee_profile",
        "content_type",
        "retry_of",
        "parent_item",
        "reviewed_by",
        "rolled_back_by",
        "created_by",
        "updated_by",
        "archived_by",
    )

    readonly_fields = (
        "id",
        "started_at",
        "finished_at",
        "duration_milliseconds",
        "reviewed_at",
        "rolled_back_at",
        "created_at",
        "updated_at",
        "archived_at",
    )

    list_select_related = (
        "processing_run",
        "employee_profile",
        "content_type",
    )


@admin.register(AttendanceImportBatch)
class AttendanceImportBatchAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "batch_number",
        "name",
        "import_type",
        "source_type",
        "status_badge",
        "progress_percentage",
        "processed_rows",
        "total_rows",
        "created_at",
    )

    list_filter = (
        "import_type",
        "source_type",
        "status",
        "dry_run",
        "allow_updates",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "batch_number",
        "name",
        "description",
        "original_file_name",
        "file_checksum",
        "source_system",
        "source_reference",
        "external_batch_id",
        "error_code",
        "error_message",
    )

    autocomplete_fields = (
        "attendance_device",
        "processing_run",
        "uploaded_by",
        "validated_by",
        "imported_by",
        "reviewed_by",
        "approved_by",
        "cancel_requested_by",
        "cancelled_by",
        "rolled_back_by",
        "created_by",
        "updated_by",
        "archived_by",
    )

    readonly_fields = (
        "id",
        "uploaded_at",
        "validation_started_at",
        "validation_finished_at",
        "import_started_at",
        "import_finished_at",
        "reviewed_at",
        "approved_at",
        "cancel_requested_at",
        "cancelled_at",
        "rollback_started_at",
        "rolled_back_at",
        "created_at",
        "updated_at",
        "archived_at",
    )

    date_hierarchy = "created_at"


@admin.register(AttendanceImportItem)
class AttendanceImportItemAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "import_batch",
        "sequence_number",
        "source_row_number",
        "item_type",
        "status_badge",
        "validation_result",
        "import_result",
        "employee_profile",
        "requires_review",
    )

    list_filter = (
        "item_type",
        "status",
        "validation_result",
        "import_result",
        "employee_match_result",
        "device_match_result",
        "is_duplicate",
        "requires_review",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "import_batch__batch_number",
        "employee_match_value",
        "device_match_value",
        "external_reference",
        "device_record_id",
        "source_checksum",
        "error_code",
        "error_message",
    )

    autocomplete_fields = (
        "import_batch",
        "employee_profile",
        "attendance_device",
        "duplicate_of_item",
        "duplicate_content_type",
        "result_content_type",
        "attendance_record",
        "daily_attendance",
        "reviewed_by",
        "approved_by",
        "rejected_by",
        "retry_of",
        "rolled_back_by",
        "created_by",
        "updated_by",
        "archived_by",
    )

    readonly_fields = (
        "id",
        "parsing_started_at",
        "validation_started_at",
        "validation_finished_at",
        "import_started_at",
        "import_finished_at",
        "processing_duration_milliseconds",
        "reviewed_at",
        "approved_at",
        "rejected_at",
        "rolled_back_at",
        "created_at",
        "updated_at",
        "archived_at",
    )

    list_select_related = (
        "import_batch",
        "employee_profile",
        "attendance_device",
    )


@admin.register(AttendanceExportBatch)
class AttendanceExportBatchAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "batch_number",
        "name",
        "export_type",
        "destination_type",
        "file_format",
        "status_badge",
        "progress_percentage",
        "exported_records",
        "created_at",
    )

    list_filter = (
        "export_type",
        "destination_type",
        "file_format",
        "compression_type",
        "status",
        "generation_source",
        "sensitive_data_mode",
        "password_protected",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "batch_number",
        "name",
        "description",
        "result_file_name",
        "result_checksum",
        "destination_reference",
        "external_delivery_id",
        "error_code",
        "error_message",
    )

    filter_horizontal = (
        "employee_profiles",
        "work_locations",
        "work_schedules",
    )

    autocomplete_fields = (
        "processing_run",
        "report",
        "requested_by",
        "last_downloaded_by",
        "cancel_requested_by",
        "cancelled_by",
        "created_by",
        "updated_by",
        "archived_by",
    )

    readonly_fields = (
        "id",
        "download_token",
        "requested_at",
        "queued_at",
        "processing_started_at",
        "processing_finished_at",
        "first_downloaded_at",
        "last_downloaded_at",
        "delivery_started_at",
        "delivered_at",
        "cancel_requested_at",
        "cancelled_at",
        "created_at",
        "updated_at",
        "archived_at",
    )

    date_hierarchy = "created_at"


@admin.register(AttendanceExportItem)
class AttendanceExportItemAdmin(
    ArchiveAdminMixin,
    StatusColorAdminMixin,
    admin.ModelAdmin,
):
    list_display = (
        "export_batch",
        "sequence_number",
        "output_row_number",
        "item_type",
        "status_badge",
        "result_type",
        "employee_profile",
        "has_sensitive_data",
        "requires_review",
    )

    list_filter = (
        "item_type",
        "status",
        "result_type",
        "has_sensitive_data",
        "sensitive_data_masked",
        "error_category",
        "requires_review",
        "created_at",
        "archived_at",
    )

    search_fields = (
        "export_batch__batch_number",
        "object_model",
        "object_id",
        "object_representation",
        "external_reference",
        "source_checksum",
        "exported_checksum",
        "error_code",
        "error_message",
    )

    autocomplete_fields = (
        "export_batch",
        "employee_profile",
        "content_type",
        "reviewed_by",
        "retry_of",
        "parent_item",
        "created_by",
        "updated_by",
        "archived_by",
    )

    readonly_fields = (
        "id",
        "processing_started_at",
        "processing_finished_at",
        "processing_duration_milliseconds",
        "reviewed_at",
        "created_at",
        "updated_at",
        "archived_at",
    )

    list_select_related = (
        "export_batch",
        "employee_profile",
        "content_type",
    )