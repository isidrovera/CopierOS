# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from apps.attendance.models import AttendanceIncident


class AttendanceIncidentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source="employee_profile.user.full_name",
        read_only=True,
    )

    incident_type_display = serializers.CharField(
        source="get_incident_type_display",
        read_only=True,
    )

    severity_display = serializers.CharField(
        source="get_severity_display",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    responsibility_type_display = serializers.CharField(
        source="get_responsibility_type_display",
        read_only=True,
    )

    resolution_type_display = serializers.CharField(
        source="get_resolution_type_display",
        read_only=True,
    )

    impact_type_display = serializers.CharField(
        source="get_impact_type_display",
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    is_open = serializers.BooleanField(
        read_only=True,
    )

    is_resolved = serializers.BooleanField(
        read_only=True,
    )

    justification_is_overdue = serializers.BooleanField(
        read_only=True,
    )

    remaining_unjustified_minutes = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = AttendanceIncident

        fields = (
            "id",
            "employee_profile",
            "employee_name",
            "daily_attendance",
            "attendance_record",
            "incident_type",
            "incident_type_display",
            "severity",
            "severity_display",
            "status",
            "status_display",
            "responsibility_type",
            "responsibility_type_display",
            "impact_type",
            "impact_type_display",
            "incident_date",
            "detected_at",
            "title",
            "description",
            "detected_value",
            "expected_value",
            "affected_minutes",
            "deductible_minutes",
            "justified_minutes",
            "remaining_unjustified_minutes",
            "evaluation_penalty_points",
            "affects_attendance",
            "affects_payroll",
            "affects_evaluation",
            "automatically_generated",
            "generation_rule",
            "generation_data",
            "requires_employee_explanation",
            "employee_explanation",
            "employee_explained_at",
            "employee_explanation_ip",
            "employee_accepts_incident",
            "justification_requested",
            "justification_requested_at",
            "justification_requested_by",
            "justification_due_at",
            "justification_is_overdue",
            "justification_text",
            "justification_submitted_at",
            "justification_document",
            "justification_document_name",
            "justification_document_type",
            "justification_document_size",
            "justification_reviewed_at",
            "justification_reviewed_by",
            "justification_review_notes",
            "resolution_type",
            "resolution_type_display",
            "resolution_notes",
            "resolved_at",
            "resolved_by",
            "closed_at",
            "closed_by",
            "cancelled_at",
            "cancelled_by",
            "cancellation_reason",
            "notes",
            "is_open",
            "is_resolved",
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
            "status",
            "employee_explanation",
            "employee_explained_at",
            "employee_explanation_ip",
            "employee_accepts_incident",
            "justification_requested",
            "justification_requested_at",
            "justification_requested_by",
            "justification_submitted_at",
            "justification_reviewed_at",
            "justification_reviewed_by",
            "justification_review_notes",
            "resolution_type",
            "resolution_notes",
            "resolved_at",
            "resolved_by",
            "closed_at",
            "closed_by",
            "cancelled_at",
            "cancelled_by",
            "cancellation_reason",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)

        instance = self.instance

        employee_profile = attrs.get(
            "employee_profile",
            getattr(instance, "employee_profile", None),
        )

        daily_attendance = attrs.get(
            "daily_attendance",
            getattr(instance, "daily_attendance", None),
        )

        attendance_record = attrs.get(
            "attendance_record",
            getattr(instance, "attendance_record", None),
        )

        incident_date = attrs.get(
            "incident_date",
            getattr(instance, "incident_date", None),
        )

        affected_minutes = attrs.get(
            "affected_minutes",
            getattr(instance, "affected_minutes", 0),
        )

        deductible_minutes = attrs.get(
            "deductible_minutes",
            getattr(instance, "deductible_minutes", 0),
        )

        justified_minutes = attrs.get(
            "justified_minutes",
            getattr(instance, "justified_minutes", 0),
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
            daily_attendance
            and employee_profile
            and daily_attendance.employee_profile_id
            != employee_profile.id
        ):
            raise serializers.ValidationError(
                {
                    "daily_attendance": (
                        "La asistencia diaria no corresponde "
                        "al trabajador."
                    )
                }
            )

        if (
            daily_attendance
            and incident_date
            and daily_attendance.date != incident_date
        ):
            raise serializers.ValidationError(
                {
                    "incident_date": (
                        "La fecha de la incidencia debe coincidir "
                        "con la asistencia diaria."
                    )
                }
            )

        if (
            attendance_record
            and employee_profile
            and attendance_record.employee_profile_id
            != employee_profile.id
        ):
            raise serializers.ValidationError(
                {
                    "attendance_record": (
                        "La marcación no corresponde al trabajador."
                    )
                }
            )

        if (
            attendance_record
            and incident_date
            and attendance_record.local_date != incident_date
        ):
            raise serializers.ValidationError(
                {
                    "incident_date": (
                        "La fecha de la incidencia debe coincidir "
                        "con la marcación."
                    )
                }
            )

        if justified_minutes > affected_minutes:
            raise serializers.ValidationError(
                {
                    "justified_minutes": (
                        "Los minutos justificados no pueden superar "
                        "los minutos afectados."
                    )
                }
            )

        if deductible_minutes > affected_minutes:
            raise serializers.ValidationError(
                {
                    "deductible_minutes": (
                        "Los minutos descontables no pueden superar "
                        "los minutos afectados."
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        try:
            return super().create(validated_data)
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