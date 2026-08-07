# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from apps.attendance.models import AttendanceCorrection


class AttendanceCorrectionSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source="employee_profile.user.full_name",
        read_only=True,
    )

    correction_type_display = serializers.CharField(
        source="get_correction_type_display",
        read_only=True,
    )

    target_type_display = serializers.CharField(
        source="get_target_type_display",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    requested_by_type_display = serializers.CharField(
        source="get_requested_by_type_display",
        read_only=True,
    )

    required_approval_level_display = serializers.CharField(
        source="get_required_approval_level_display",
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    is_pending = serializers.BooleanField(
        read_only=True,
    )

    is_approved = serializers.BooleanField(
        read_only=True,
    )

    can_be_applied = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = AttendanceCorrection

        fields = (
            "id",
            "correction_number",
            "employee_profile",
            "employee_name",
            "attendance_record",
            "daily_attendance",
            "generated_record",
            "correction_type",
            "correction_type_display",
            "target_type",
            "target_type_display",
            "status",
            "status_display",
            "requested_by_type",
            "requested_by_type_display",
            "required_approval_level",
            "required_approval_level_display",
            "correction_date",
            "reason",
            "employee_explanation",
            "supervisor_observation",
            "human_resources_observation",
            "management_observation",
            "previous_values",
            "requested_values",
            "approved_values",
            "application_result",
            "supporting_document",
            "supporting_document_name",
            "supporting_document_type",
            "supporting_document_size",
            "requires_document",
            "affects_attendance",
            "affects_payroll",
            "affects_evaluation",
            "requires_daily_recalculation",
            "requested_at",
            "requested_by",
            "supervisor_reviewed_at",
            "supervisor_reviewed_by",
            "human_resources_reviewed_at",
            "human_resources_reviewed_by",
            "management_reviewed_at",
            "management_reviewed_by",
            "approved_at",
            "approved_by",
            "approval_observation",
            "rejected_at",
            "rejected_by",
            "rejection_reason",
            "applied_at",
            "applied_by",
            "application_error",
            "cancelled_at",
            "cancelled_by",
            "cancellation_reason",
            "closed_at",
            "closed_by",
            "notes",
            "is_pending",
            "is_approved",
            "can_be_applied",
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
            "generated_record",
            "previous_values",
            "approved_values",
            "application_result",
            "requested_at",
            "requested_by",
            "supervisor_reviewed_at",
            "supervisor_reviewed_by",
            "human_resources_reviewed_at",
            "human_resources_reviewed_by",
            "management_reviewed_at",
            "management_reviewed_by",
            "approved_at",
            "approved_by",
            "approval_observation",
            "rejected_at",
            "rejected_by",
            "rejection_reason",
            "applied_at",
            "applied_by",
            "application_error",
            "cancelled_at",
            "cancelled_by",
            "cancellation_reason",
            "closed_at",
            "closed_by",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

    def validate_correction_number(self, value):
        value = str(value or "").strip().upper()

        queryset = AttendanceCorrection.objects.filter(
            correction_number__iexact=value,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una corrección con este número."
            )

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        instance = self.instance

        employee_profile = attrs.get(
            "employee_profile",
            getattr(instance, "employee_profile", None),
        )

        attendance_record = attrs.get(
            "attendance_record",
            getattr(instance, "attendance_record", None),
        )

        daily_attendance = attrs.get(
            "daily_attendance",
            getattr(instance, "daily_attendance", None),
        )

        correction_date = attrs.get(
            "correction_date",
            getattr(instance, "correction_date", None),
        )

        target_type = attrs.get(
            "target_type",
            getattr(instance, "target_type", None),
        )

        correction_type = attrs.get(
            "correction_type",
            getattr(instance, "correction_type", None),
        )

        requires_document = attrs.get(
            "requires_document",
            getattr(instance, "requires_document", False),
        )

        supporting_document = attrs.get(
            "supporting_document",
            getattr(instance, "supporting_document", None),
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
            attendance_record
            and correction_date
            and attendance_record.local_date != correction_date
        ):
            raise serializers.ValidationError(
                {
                    "correction_date": (
                        "La fecha debe coincidir con la marcación."
                    )
                }
            )

        if (
            daily_attendance
            and correction_date
            and daily_attendance.date != correction_date
        ):
            raise serializers.ValidationError(
                {
                    "correction_date": (
                        "La fecha debe coincidir con "
                        "la asistencia diaria."
                    )
                }
            )

        missing_types = (
            AttendanceCorrection.CorrectionType.MISSING_CLOCK_IN,
            AttendanceCorrection.CorrectionType.MISSING_CLOCK_OUT,
            AttendanceCorrection.CorrectionType.MISSING_BREAK_START,
            AttendanceCorrection.CorrectionType.MISSING_BREAK_END,
        )

        if (
            target_type
            == AttendanceCorrection.TargetType.ATTENDANCE_RECORD
            and not attendance_record
            and correction_type not in missing_types
        ):
            raise serializers.ValidationError(
                {
                    "attendance_record": (
                        "Debes seleccionar la marcación "
                        "que será corregida."
                    )
                }
            )

        if (
            target_type
            == AttendanceCorrection.TargetType.DAILY_ATTENDANCE
            and not daily_attendance
        ):
            raise serializers.ValidationError(
                {
                    "daily_attendance": (
                        "Debes seleccionar la asistencia diaria."
                    )
                }
            )

        if (
            target_type == AttendanceCorrection.TargetType.BOTH
            and (
                not attendance_record
                or not daily_attendance
            )
        ):
            raise serializers.ValidationError(
                {
                    "target_type": (
                        "La corrección combinada requiere "
                        "marcación y asistencia diaria."
                    )
                }
            )

        if (
            requires_document
            and not supporting_document
            and not instance
        ):
            raise serializers.ValidationError(
                {
                    "supporting_document": (
                        "Debes adjuntar el documento sustentatorio."
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

    def update(self, instance, validated_data):
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