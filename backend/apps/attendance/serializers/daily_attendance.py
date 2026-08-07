# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from apps.attendance.models import DailyAttendance


class DailyAttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source="employee_profile.user.full_name",
        read_only=True,
    )

    attendance_status_display = serializers.CharField(
        source="get_attendance_status_display",
        read_only=True,
    )

    processing_status_display = serializers.CharField(
        source="get_processing_status_display",
        read_only=True,
    )

    day_source_display = serializers.CharField(
        source="get_day_source_display",
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    is_closed = serializers.BooleanField(
        read_only=True,
    )

    has_clock_in = serializers.BooleanField(
        read_only=True,
    )

    has_clock_out = serializers.BooleanField(
        read_only=True,
    )

    has_complete_presence = serializers.BooleanField(
        read_only=True,
    )

    worked_hours = serializers.FloatField(
        read_only=True,
    )

    operational_hours = serializers.FloatField(
        read_only=True,
    )

    overtime_hours = serializers.FloatField(
        read_only=True,
    )

    attendance_percentage = serializers.FloatField(
        read_only=True,
    )

    productivity_time_percentage = serializers.FloatField(
        read_only=True,
    )

    class Meta:
        model = DailyAttendance

        fields = (
            "id",
            "employee_profile",
            "employee_name",
            "date",
            "attendance_status",
            "attendance_status_display",
            "processing_status",
            "processing_status_display",
            "day_source",
            "day_source_display",
            "schedule_assignment",
            "schedule_day",
            "calendar_assignment",
            "holiday_day",
            "primary_location",
            "is_scheduled_working_day",
            "attendance_required",
            "scheduled_entry_at",
            "scheduled_exit_at",
            "scheduled_break_start_at",
            "scheduled_break_end_at",
            "scheduled_shift_minutes",
            "scheduled_break_minutes",
            "scheduled_work_minutes",
            "first_clock_in_at",
            "last_clock_out_at",
            "first_break_start_at",
            "last_break_end_at",
            "first_field_work_start_at",
            "last_field_work_end_at",
            "first_remote_work_start_at",
            "last_remote_work_end_at",
            "gross_presence_minutes",
            "valid_break_minutes",
            "excess_break_minutes",
            "effective_work_minutes",
            "operational_work_minutes",
            "administrative_work_minutes",
            "unclassified_minutes",
            "late_minutes",
            "early_departure_minutes",
            "missing_work_minutes",
            "overtime_minutes",
            "approved_overtime_minutes",
            "compensation_minutes",
            "attendance_record_count",
            "valid_record_count",
            "observed_record_count",
            "rejected_record_count",
            "manual_record_count",
            "incomplete_clocking",
            "missing_clock_in",
            "missing_clock_out",
            "missing_break_start",
            "missing_break_end",
            "location_incident",
            "device_incident",
            "schedule_incident",
            "requires_review",
            "review_reasons",
            "employee_explanation",
            "supervisor_observation",
            "reviewed_at",
            "reviewed_by",
            "approved_at",
            "approved_by",
            "closed_at",
            "closed_by",
            "processing_error",
            "last_processed_at",
            "calculation_version",
            "notes",
            "is_closed",
            "has_clock_in",
            "has_clock_out",
            "has_complete_presence",
            "worked_hours",
            "operational_hours",
            "overtime_hours",
            "attendance_percentage",
            "productivity_time_percentage",
            "is_archived",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

        read_only_fields = (
            "id",
            "attendance_status",
            "processing_status",
            "scheduled_entry_at",
            "scheduled_exit_at",
            "scheduled_break_start_at",
            "scheduled_break_end_at",
            "scheduled_shift_minutes",
            "scheduled_break_minutes",
            "scheduled_work_minutes",
            "gross_presence_minutes",
            "effective_work_minutes",
            "unclassified_minutes",
            "late_minutes",
            "early_departure_minutes",
            "missing_work_minutes",
            "overtime_minutes",
            "incomplete_clocking",
            "missing_clock_in",
            "missing_clock_out",
            "missing_break_start",
            "missing_break_end",
            "requires_review",
            "review_reasons",
            "reviewed_at",
            "reviewed_by",
            "approved_at",
            "approved_by",
            "closed_at",
            "closed_by",
            "processing_error",
            "last_processed_at",
            "calculation_version",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

    def validate_approved_overtime_minutes(
        self,
        value,
    ):
        overtime_minutes = (
            self.initial_data.get("overtime_minutes")
        )

        if overtime_minutes is None and self.instance:
            overtime_minutes = self.instance.overtime_minutes

        if (
            overtime_minutes is not None
            and value > int(overtime_minutes)
        ):
            raise serializers.ValidationError(
                "Los minutos extra aprobados no pueden superar "
                "las horas extras calculadas."
            )

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        instance = self.instance

        employee_profile = attrs.get(
            "employee_profile",
            getattr(instance, "employee_profile", None),
        )

        schedule_assignment = attrs.get(
            "schedule_assignment",
            getattr(instance, "schedule_assignment", None),
        )

        schedule_day = attrs.get(
            "schedule_day",
            getattr(instance, "schedule_day", None),
        )

        calendar_assignment = attrs.get(
            "calendar_assignment",
            getattr(instance, "calendar_assignment", None),
        )

        holiday_day = attrs.get(
            "holiday_day",
            getattr(instance, "holiday_day", None),
        )

        first_clock_in_at = attrs.get(
            "first_clock_in_at",
            getattr(instance, "first_clock_in_at", None),
        )

        last_clock_out_at = attrs.get(
            "last_clock_out_at",
            getattr(instance, "last_clock_out_at", None),
        )

        first_break_start_at = attrs.get(
            "first_break_start_at",
            getattr(instance, "first_break_start_at", None),
        )

        last_break_end_at = attrs.get(
            "last_break_end_at",
            getattr(instance, "last_break_end_at", None),
        )

        operational_work_minutes = attrs.get(
            "operational_work_minutes",
            getattr(instance, "operational_work_minutes", 0),
        )

        administrative_work_minutes = attrs.get(
            "administrative_work_minutes",
            getattr(instance, "administrative_work_minutes", 0),
        )

        effective_work_minutes = (
            getattr(instance, "effective_work_minutes", 0)
            if instance
            else 0
        )

        approved_overtime_minutes = attrs.get(
            "approved_overtime_minutes",
            getattr(instance, "approved_overtime_minutes", 0),
        )

        overtime_minutes = (
            getattr(instance, "overtime_minutes", 0)
            if instance
            else 0
        )

        if employee_profile and employee_profile.archived_at:
            raise serializers.ValidationError(
                {
                    "employee_profile": (
                        "El perfil laboral está archivado."
                    )
                }
            )

        if (
            schedule_assignment
            and employee_profile
            and schedule_assignment.employee_profile_id
            != employee_profile.id
        ):
            raise serializers.ValidationError(
                {
                    "schedule_assignment": (
                        "La asignación de horario no corresponde "
                        "al trabajador."
                    )
                }
            )

        if (
            calendar_assignment
            and employee_profile
            and calendar_assignment.employee_profile_id
            != employee_profile.id
        ):
            raise serializers.ValidationError(
                {
                    "calendar_assignment": (
                        "La asignación de calendario no corresponde "
                        "al trabajador."
                    )
                }
            )

        if (
            schedule_day
            and schedule_assignment
            and schedule_day.schedule_id
            != schedule_assignment.schedule_id
        ):
            raise serializers.ValidationError(
                {
                    "schedule_day": (
                        "El día no pertenece al horario asignado."
                    )
                }
            )

        if (
            holiday_day
            and calendar_assignment
            and holiday_day.calendar_id
            != calendar_assignment.calendar_id
        ):
            raise serializers.ValidationError(
                {
                    "holiday_day": (
                        "El día especial no pertenece "
                        "al calendario asignado."
                    )
                }
            )

        if (
            first_clock_in_at
            and last_clock_out_at
            and last_clock_out_at <= first_clock_in_at
        ):
            raise serializers.ValidationError(
                {
                    "last_clock_out_at": (
                        "La salida debe ser posterior a la entrada."
                    )
                }
            )

        if (
            first_break_start_at
            and last_break_end_at
            and last_break_end_at <= first_break_start_at
        ):
            raise serializers.ValidationError(
                {
                    "last_break_end_at": (
                        "El fin de refrigerio debe ser posterior "
                        "al inicio."
                    )
                }
            )

        if approved_overtime_minutes > overtime_minutes:
            raise serializers.ValidationError(
                {
                    "approved_overtime_minutes": (
                        "Los minutos extra aprobados no pueden "
                        "superar las horas extras calculadas."
                    )
                }
            )

        if (
            operational_work_minutes
            + administrative_work_minutes
            > effective_work_minutes
        ):
            raise serializers.ValidationError(
                {
                    "operational_work_minutes": (
                        "Los minutos clasificados no pueden superar "
                        "el tiempo efectivo trabajado."
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        try:
            return super().create(
                validated_data
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            ) from exc

    def update(
        self,
        instance,
        validated_data,
    ):
        try:
            return super().update(
                instance,
                validated_data,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            ) from exc