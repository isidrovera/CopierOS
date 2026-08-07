# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from apps.attendance.models import EmployeeCalendarAssignment


class EmployeeCalendarAssignmentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source="employee_profile.user.full_name",
        read_only=True,
    )

    calendar_name = serializers.CharField(
        source="calendar.name",
        read_only=True,
    )

    assignment_type_display = serializers.CharField(
        source="get_assignment_type_display",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    is_current = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = EmployeeCalendarAssignment

        fields = (
            "id",
            "employee_profile",
            "employee_name",
            "calendar",
            "calendar_name",
            "assignment_type",
            "assignment_type_display",
            "status",
            "status_display",
            "effective_from",
            "effective_until",
            "priority",
            "apply_national_holidays",
            "apply_regional_holidays",
            "apply_local_holidays",
            "apply_non_working_days",
            "apply_company_closures",
            "apply_special_workdays",
            "override_default_calendar",
            "notes",
            "activated_at",
            "activated_by",
            "finished_at",
            "finished_by",
            "cancelled_at",
            "cancelled_by",
            "cancellation_reason",
            "is_current",
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
            "activated_at",
            "activated_by",
            "finished_at",
            "finished_by",
            "cancelled_at",
            "cancelled_by",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

    def validate_priority(self, value):
        if value > 1000:
            raise serializers.ValidationError(
                "La prioridad no puede superar 1000."
            )

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        instance = self.instance

        employee_profile = attrs.get(
            "employee_profile",
            getattr(instance, "employee_profile", None),
        )

        calendar = attrs.get(
            "calendar",
            getattr(instance, "calendar", None),
        )

        assignment_type = attrs.get(
            "assignment_type",
            getattr(
                instance,
                "assignment_type",
                EmployeeCalendarAssignment.AssignmentType.NATIONAL,
            ),
        )

        effective_from = attrs.get(
            "effective_from",
            getattr(instance, "effective_from", None),
        )

        effective_until = attrs.get(
            "effective_until",
            getattr(instance, "effective_until", None),
        )

        status_value = attrs.get(
            "status",
            getattr(
                instance,
                "status",
                EmployeeCalendarAssignment.Status.DRAFT,
            ),
        )

        cancellation_reason = attrs.get(
            "cancellation_reason",
            getattr(instance, "cancellation_reason", ""),
        )

        apply_flags = (
            attrs.get(
                "apply_national_holidays",
                getattr(instance, "apply_national_holidays", True),
            ),
            attrs.get(
                "apply_regional_holidays",
                getattr(instance, "apply_regional_holidays", True),
            ),
            attrs.get(
                "apply_local_holidays",
                getattr(instance, "apply_local_holidays", True),
            ),
            attrs.get(
                "apply_non_working_days",
                getattr(instance, "apply_non_working_days", True),
            ),
            attrs.get(
                "apply_company_closures",
                getattr(instance, "apply_company_closures", True),
            ),
            attrs.get(
                "apply_special_workdays",
                getattr(instance, "apply_special_workdays", True),
            ),
        )

        if (
            effective_from
            and effective_until
            and effective_until < effective_from
        ):
            raise serializers.ValidationError(
                {
                    "effective_until": (
                        "La fecha final no puede ser anterior "
                        "a la fecha inicial."
                    )
                }
            )

        if (
            assignment_type
            == EmployeeCalendarAssignment.AssignmentType.TEMPORARY
            and not effective_until
        ):
            raise serializers.ValidationError(
                {
                    "effective_until": (
                        "Una asignación temporal debe tener "
                        "fecha de finalización."
                    )
                }
            )

        if employee_profile and employee_profile.archived_at:
            raise serializers.ValidationError(
                {
                    "employee_profile": (
                        "No puedes asignar un calendario a "
                        "un perfil laboral archivado."
                    )
                }
            )

        if calendar:
            if calendar.archived_at:
                raise serializers.ValidationError(
                    {
                        "calendar": (
                            "No puedes asignar un calendario archivado."
                        )
                    }
                )

            if not calendar.is_active:
                raise serializers.ValidationError(
                    {
                        "calendar": (
                            "No puedes asignar un calendario inactivo."
                        )
                    }
                )

            if (
                effective_from
                and effective_from < calendar.effective_from
            ):
                raise serializers.ValidationError(
                    {
                        "effective_from": (
                            "La asignación no puede iniciar antes "
                            "de la vigencia del calendario."
                        )
                    }
                )

            if (
                calendar.effective_until
                and (
                    not effective_until
                    or effective_until > calendar.effective_until
                )
            ):
                raise serializers.ValidationError(
                    {
                        "effective_until": (
                            "La asignación no puede superar "
                            "la fecha final del calendario."
                        )
                    }
                )

        if not any(apply_flags):
            raise serializers.ValidationError(
                {
                    "apply_national_holidays": (
                        "Debes seleccionar al menos un tipo "
                        "de día para aplicar."
                    )
                }
            )

        if (
            status_value
            == EmployeeCalendarAssignment.Status.CANCELLED
            and not str(cancellation_reason or "").strip()
        ):
            raise serializers.ValidationError(
                {
                    "cancellation_reason": (
                        "Debes indicar el motivo de cancelación."
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