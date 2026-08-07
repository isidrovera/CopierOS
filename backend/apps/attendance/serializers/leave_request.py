# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from apps.attendance.models import LeaveRequest


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source="employee_profile.user.full_name",
        read_only=True,
    )

    leave_type_display = serializers.CharField(
        source="get_leave_type_display",
        read_only=True,
    )

    duration_type_display = serializers.CharField(
        source="get_duration_type_display",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    payment_type_display = serializers.CharField(
        source="get_payment_type_display",
        read_only=True,
    )

    required_approval_level_display = serializers.CharField(
        source="get_required_approval_level_display",
        read_only=True,
    )

    destination_location_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    is_approved = serializers.BooleanField(
        read_only=True,
    )

    is_pending = serializers.BooleanField(
        read_only=True,
    )

    is_active_for_today = serializers.BooleanField(
        read_only=True,
    )

    compensation_pending_minutes = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = LeaveRequest

        fields = (
            "id",
            "request_number",
            "employee_profile",
            "employee_name",
            "leave_type",
            "leave_type_display",
            "duration_type",
            "duration_type_display",
            "status",
            "status_display",
            "payment_type",
            "payment_type_display",
            "required_approval_level",
            "required_approval_level_display",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "total_calendar_days",
            "total_working_days",
            "total_requested_minutes",
            "total_approved_minutes",
            "reason",
            "destination",
            "destination_location",
            "destination_location_name",
            "contact_phone",
            "emergency_contact",
            "affects_attendance",
            "affects_payroll",
            "affects_evaluation",
            "generates_attendance_justification",
            "requires_compensation",
            "compensation_minutes",
            "compensation_due_date",
            "compensation_completed_minutes",
            "compensation_completed_at",
            "compensation_pending_minutes",
            "supporting_document",
            "supporting_document_name",
            "supporting_document_type",
            "supporting_document_size",
            "medical_certificate_number",
            "medical_provider",
            "diagnosis_reference",
            "vacation_period_year",
            "requested_at",
            "requested_by",
            "supervisor_reviewed_at",
            "supervisor_reviewed_by",
            "supervisor_observation",
            "human_resources_reviewed_at",
            "human_resources_reviewed_by",
            "human_resources_observation",
            "management_reviewed_at",
            "management_reviewed_by",
            "management_observation",
            "approved_at",
            "approved_by",
            "approval_observation",
            "rejected_at",
            "rejected_by",
            "rejection_reason",
            "cancelled_at",
            "cancelled_by",
            "cancellation_reason",
            "completed_at",
            "completed_by",
            "closed_at",
            "closed_by",
            "notes",
            "is_approved",
            "is_pending",
            "is_active_for_today",
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
            "total_calendar_days",
            "requested_at",
            "requested_by",
            "supervisor_reviewed_at",
            "supervisor_reviewed_by",
            "supervisor_observation",
            "human_resources_reviewed_at",
            "human_resources_reviewed_by",
            "human_resources_observation",
            "management_reviewed_at",
            "management_reviewed_by",
            "management_observation",
            "approved_at",
            "approved_by",
            "approval_observation",
            "rejected_at",
            "rejected_by",
            "rejection_reason",
            "cancelled_at",
            "cancelled_by",
            "cancellation_reason",
            "completed_at",
            "completed_by",
            "closed_at",
            "closed_by",
            "compensation_completed_at",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

    def get_destination_location_name(self, obj):
        if not obj.destination_location_id:
            return None

        return obj.destination_location.name

    def validate_request_number(self, value):
        value = str(value or "").strip().upper()

        if not value:
            raise serializers.ValidationError(
                "Debes indicar el número de solicitud."
            )

        queryset = LeaveRequest.objects.filter(
            request_number__iexact=value,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una solicitud con este número."
            )

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        instance = self.instance

        employee_profile = attrs.get(
            "employee_profile",
            getattr(instance, "employee_profile", None),
        )

        start_date = attrs.get(
            "start_date",
            getattr(instance, "start_date", None),
        )

        end_date = attrs.get(
            "end_date",
            getattr(instance, "end_date", None),
        )

        start_time = attrs.get(
            "start_time",
            getattr(instance, "start_time", None),
        )

        end_time = attrs.get(
            "end_time",
            getattr(instance, "end_time", None),
        )

        duration_type = attrs.get(
            "duration_type",
            getattr(
                instance,
                "duration_type",
                LeaveRequest.DurationType.FULL_DAY,
            ),
        )

        leave_type = attrs.get(
            "leave_type",
            getattr(instance, "leave_type", None),
        )

        destination = attrs.get(
            "destination",
            getattr(instance, "destination", ""),
        )

        destination_location = attrs.get(
            "destination_location",
            getattr(instance, "destination_location", None),
        )

        requires_compensation = attrs.get(
            "requires_compensation",
            getattr(instance, "requires_compensation", False),
        )

        compensation_minutes = attrs.get(
            "compensation_minutes",
            getattr(instance, "compensation_minutes", 0),
        )

        total_requested_minutes = attrs.get(
            "total_requested_minutes",
            getattr(instance, "total_requested_minutes", 0),
        )

        total_approved_minutes = attrs.get(
            "total_approved_minutes",
            getattr(instance, "total_approved_minutes", 0),
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
            start_date
            and end_date
            and end_date < start_date
        ):
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "La fecha final no puede ser anterior "
                        "a la fecha inicial."
                    )
                }
            )

        if duration_type == LeaveRequest.DurationType.HOURS:
            if not start_time:
                raise serializers.ValidationError(
                    {"start_time": "Debes indicar la hora inicial."}
                )

            if not end_time:
                raise serializers.ValidationError(
                    {"end_time": "Debes indicar la hora final."}
                )

            if (
                start_date
                and end_date
                and start_date != end_date
            ):
                raise serializers.ValidationError(
                    {
                        "end_date": (
                            "Un permiso por horas debe iniciar "
                            "y terminar el mismo día."
                        )
                    }
                )

            if (
                start_time
                and end_time
                and end_time <= start_time
            ):
                raise serializers.ValidationError(
                    {
                        "end_time": (
                            "La hora final debe ser posterior "
                            "a la hora inicial."
                        )
                    }
                )

        if (
            duration_type
            in (
                LeaveRequest.DurationType.HALF_DAY_MORNING,
                LeaveRequest.DurationType.HALF_DAY_AFTERNOON,
            )
            and start_date
            and end_date
            and start_date != end_date
        ):
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "Una media jornada debe corresponder "
                        "a un solo día."
                    )
                }
            )

        if total_approved_minutes > total_requested_minutes:
            raise serializers.ValidationError(
                {
                    "total_approved_minutes": (
                        "Los minutos aprobados no pueden superar "
                        "los minutos solicitados."
                    )
                }
            )

        if (
            requires_compensation
            and compensation_minutes <= 0
        ):
            raise serializers.ValidationError(
                {
                    "compensation_minutes": (
                        "Debes indicar los minutos "
                        "que deben compensarse."
                    )
                }
            )

        if (
            not requires_compensation
            and compensation_minutes
        ):
            raise serializers.ValidationError(
                {
                    "compensation_minutes": (
                        "Los minutos de compensación deben ser cero."
                    )
                }
            )

        if (
            leave_type
            in (
                LeaveRequest.LeaveType.SERVICE_COMMISSION,
                LeaveRequest.LeaveType.REMOTE_WORK,
            )
            and not str(destination or "").strip()
            and not destination_location
        ):
            raise serializers.ValidationError(
                {
                    "destination": (
                        "Debes indicar el destino o ubicación."
                    )
                }
            )

        if (
            leave_type == LeaveRequest.LeaveType.VACATION
            and not attrs.get(
                "vacation_period_year",
                getattr(instance, "vacation_period_year", None),
            )
        ):
            raise serializers.ValidationError(
                {
                    "vacation_period_year": (
                        "Debes indicar el periodo vacacional."
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