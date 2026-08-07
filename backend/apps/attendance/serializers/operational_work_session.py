# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from apps.attendance.models import OperationalWorkSession


class OperationalWorkSessionSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source="employee_profile.user.full_name",
        read_only=True,
    )

    session_type_display = serializers.CharField(
        source="get_session_type_display",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    current_stage_display = serializers.CharField(
        source="get_current_stage_display",
        read_only=True,
    )

    priority_display = serializers.CharField(
        source="get_priority_display",
        read_only=True,
    )

    completion_result_display = serializers.CharField(
        source="get_completion_result_display",
        read_only=True,
    )

    work_location_name = serializers.SerializerMethodField()
    device_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    is_active = serializers.BooleanField(
        read_only=True,
    )

    total_delay_minutes = serializers.IntegerField(
        read_only=True,
    )

    non_technician_delay_minutes = serializers.IntegerField(
        read_only=True,
    )

    productivity_minutes = serializers.IntegerField(
        read_only=True,
    )

    efficiency_percentage = serializers.FloatField(
        read_only=True,
    )

    class Meta:
        model = OperationalWorkSession

        fields = (
            "id",
            "session_number",
            "employee_profile",
            "employee_name",
            "daily_attendance",
            "session_type",
            "session_type_display",
            "status",
            "status_display",
            "current_stage",
            "current_stage_display",
            "priority",
            "priority_display",
            "target_content_type",
            "target_object_id",
            "external_reference",
            "title",
            "description",
            "work_location",
            "work_location_name",
            "device",
            "device_name",
            "assigned_at",
            "assigned_by",
            "accepted_at",
            "rejected_at",
            "rejection_reason",
            "scheduled_start_at",
            "scheduled_end_at",
            "started_at",
            "last_resumed_at",
            "paused_at",
            "waiting_started_at",
            "completed_at",
            "cancelled_at",
            "cancelled_by",
            "cancellation_reason",
            "total_elapsed_minutes",
            "effective_work_minutes",
            "pause_minutes",
            "external_waiting_minutes",
            "internal_waiting_minutes",
            "travel_minutes",
            "diagnosis_minutes",
            "execution_minutes",
            "testing_minutes",
            "documentation_minutes",
            "unclassified_minutes",
            "expected_minutes",
            "completion_percentage",
            "completion_result",
            "completion_result_display",
            "technician_responsible_delay_minutes",
            "company_responsible_delay_minutes",
            "client_responsible_delay_minutes",
            "supplier_responsible_delay_minutes",
            "external_responsible_delay_minutes",
            "total_delay_minutes",
            "non_technician_delay_minutes",
            "productivity_minutes",
            "efficiency_percentage",
            "affects_productivity",
            "include_in_evaluation",
            "requires_review",
            "review_reason",
            "employee_observation",
            "supervisor_observation",
            "reviewed_at",
            "reviewed_by",
            "metadata",
            "is_active",
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
            "current_stage",
            "accepted_at",
            "rejected_at",
            "rejection_reason",
            "started_at",
            "last_resumed_at",
            "paused_at",
            "waiting_started_at",
            "completed_at",
            "cancelled_at",
            "cancelled_by",
            "cancellation_reason",
            "total_elapsed_minutes",
            "effective_work_minutes",
            "unclassified_minutes",
            "reviewed_at",
            "reviewed_by",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

    def get_work_location_name(self, obj):
        if not obj.work_location_id:
            return None

        return obj.work_location.name

    def get_device_name(self, obj):
        if not obj.device_id:
            return None

        return obj.device.name

    def validate_session_number(self, value):
        value = str(value or "").strip().upper()

        queryset = OperationalWorkSession.objects.filter(
            session_number__iexact=value,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una sesión con este número."
            )

        return value

    def validate_completion_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "El porcentaje debe estar entre 0 y 100."
            )

        return value

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

        work_location = attrs.get(
            "work_location",
            getattr(instance, "work_location", None),
        )

        device = attrs.get(
            "device",
            getattr(instance, "device", None),
        )

        target_content_type = attrs.get(
            "target_content_type",
            getattr(instance, "target_content_type", None),
        )

        target_object_id = attrs.get(
            "target_object_id",
            getattr(instance, "target_object_id", None),
        )

        scheduled_start_at = attrs.get(
            "scheduled_start_at",
            getattr(instance, "scheduled_start_at", None),
        )

        scheduled_end_at = attrs.get(
            "scheduled_end_at",
            getattr(instance, "scheduled_end_at", None),
        )

        requires_review = attrs.get(
            "requires_review",
            getattr(instance, "requires_review", False),
        )

        review_reason = attrs.get(
            "review_reason",
            getattr(instance, "review_reason", ""),
        )

        if employee_profile:
            if employee_profile.archived_at:
                raise serializers.ValidationError(
                    {
                        "employee_profile": (
                            "El perfil laboral está archivado."
                        )
                    }
                )

            if not employee_profile.track_operational_time:
                raise serializers.ValidationError(
                    {
                        "employee_profile": (
                            "El trabajador no tiene habilitado "
                            "el control de tiempo operativo."
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

        if work_location:
            if work_location.archived_at:
                raise serializers.ValidationError(
                    {
                        "work_location": (
                            "La ubicación de trabajo está archivada."
                        )
                    }
                )

            if not work_location.is_active:
                raise serializers.ValidationError(
                    {
                        "work_location": (
                            "La ubicación de trabajo está inactiva."
                        )
                    }
                )

        if device and not device.is_active:
            raise serializers.ValidationError(
                {
                    "device": (
                        "El dispositivo está inactivo."
                    )
                }
            )

        if bool(target_content_type) != bool(target_object_id):
            raise serializers.ValidationError(
                {
                    "target_object_id": (
                        "Debes registrar tanto el tipo como "
                        "el ID del documento relacionado."
                    )
                }
            )

        if (
            scheduled_start_at
            and scheduled_end_at
            and scheduled_end_at <= scheduled_start_at
        ):
            raise serializers.ValidationError(
                {
                    "scheduled_end_at": (
                        "El fin programado debe ser posterior "
                        "al inicio programado."
                    )
                }
            )

        if (
            requires_review
            and not str(review_reason or "").strip()
        ):
            raise serializers.ValidationError(
                {
                    "review_reason": (
                        "Debes indicar el motivo de revisión."
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