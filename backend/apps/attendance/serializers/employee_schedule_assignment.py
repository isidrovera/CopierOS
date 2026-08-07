# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from apps.attendance.models import EmployeeScheduleAssignment


class EmployeeScheduleAssignmentSerializer(
    serializers.ModelSerializer
):
    """
    Serializer de asignaciones de horarios laborales.
    """

    employee_name = serializers.CharField(
        source="employee_profile.user.full_name",
        read_only=True,
    )

    schedule_name = serializers.CharField(
        source="schedule.name",
        read_only=True,
    )

    schedule_code = serializers.CharField(
        source="schedule.code",
        read_only=True,
    )

    primary_location_name = serializers.SerializerMethodField()

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

    effective_entry_tolerance_minutes = serializers.IntegerField(
        read_only=True,
    )

    effective_early_departure_tolerance_minutes = (
        serializers.IntegerField(
            read_only=True,
        )
    )

    effective_break_minutes = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = EmployeeScheduleAssignment

        fields = (
            "id",
            "employee_profile",
            "employee_name",
            "schedule",
            "schedule_code",
            "schedule_name",
            "assignment_type",
            "assignment_type_display",
            "status",
            "status_display",
            "primary_location",
            "primary_location_name",
            "allowed_locations",
            "effective_from",
            "effective_until",
            "attendance_required",
            "operational_time_required",
            "location_required",
            "photo_required",
            "allow_company_clocking",
            "allow_client_clocking",
            "allow_remote_clocking",
            "allow_service_order_clocking",
            "override_entry_tolerance",
            "entry_tolerance_minutes",
            "effective_entry_tolerance_minutes",
            "override_early_departure_tolerance",
            "early_departure_tolerance_minutes",
            "effective_early_departure_tolerance_minutes",
            "override_break_minutes",
            "break_minutes",
            "effective_break_minutes",
            "notes",
            "activated_at",
            "activated_by",
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

    def get_primary_location_name(
        self,
        obj,
    ):
        if not obj.primary_location_id:
            return None

        return obj.primary_location.name

    def validate_entry_tolerance_minutes(
        self,
        value,
    ):
        if value is not None and value > 180:
            raise serializers.ValidationError(
                "La tolerancia de ingreso no puede "
                "superar 180 minutos."
            )

        return value

    def validate_early_departure_tolerance_minutes(
        self,
        value,
    ):
        if value is not None and value > 180:
            raise serializers.ValidationError(
                "La tolerancia de salida no puede "
                "superar 180 minutos."
            )

        return value

    def validate_break_minutes(
        self,
        value,
    ):
        if value is not None and value > 300:
            raise serializers.ValidationError(
                "Los minutos de refrigerio no pueden "
                "superar 300 minutos."
            )

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        instance = self.instance

        employee_profile = attrs.get(
            "employee_profile",
            getattr(
                instance,
                "employee_profile",
                None,
            ),
        )

        schedule = attrs.get(
            "schedule",
            getattr(
                instance,
                "schedule",
                None,
            ),
        )

        assignment_type = attrs.get(
            "assignment_type",
            getattr(
                instance,
                "assignment_type",
                (
                    EmployeeScheduleAssignment
                    .AssignmentType.PERMANENT
                ),
            ),
        )

        status_value = attrs.get(
            "status",
            getattr(
                instance,
                "status",
                (
                    EmployeeScheduleAssignment
                    .AssignmentStatus.DRAFT
                ),
            ),
        )

        primary_location = attrs.get(
            "primary_location",
            getattr(
                instance,
                "primary_location",
                None,
            ),
        )

        effective_from = attrs.get(
            "effective_from",
            getattr(
                instance,
                "effective_from",
                None,
            ),
        )

        effective_until = attrs.get(
            "effective_until",
            getattr(
                instance,
                "effective_until",
                None,
            ),
        )

        attendance_required = attrs.get(
            "attendance_required",
            getattr(
                instance,
                "attendance_required",
                True,
            ),
        )

        operational_time_required = attrs.get(
            "operational_time_required",
            getattr(
                instance,
                "operational_time_required",
                False,
            ),
        )

        location_required = attrs.get(
            "location_required",
            getattr(
                instance,
                "location_required",
                False,
            ),
        )

        override_entry_tolerance = attrs.get(
            "override_entry_tolerance",
            getattr(
                instance,
                "override_entry_tolerance",
                False,
            ),
        )

        entry_tolerance_minutes = attrs.get(
            "entry_tolerance_minutes",
            getattr(
                instance,
                "entry_tolerance_minutes",
                None,
            ),
        )

        override_early_departure_tolerance = attrs.get(
            "override_early_departure_tolerance",
            getattr(
                instance,
                "override_early_departure_tolerance",
                False,
            ),
        )

        early_departure_tolerance_minutes = attrs.get(
            "early_departure_tolerance_minutes",
            getattr(
                instance,
                "early_departure_tolerance_minutes",
                None,
            ),
        )

        override_break_minutes = attrs.get(
            "override_break_minutes",
            getattr(
                instance,
                "override_break_minutes",
                False,
            ),
        )

        break_minutes = attrs.get(
            "break_minutes",
            getattr(
                instance,
                "break_minutes",
                None,
            ),
        )

        cancellation_reason = attrs.get(
            "cancellation_reason",
            getattr(
                instance,
                "cancellation_reason",
                "",
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
            == (
                EmployeeScheduleAssignment
                .AssignmentType.TEMPORARY
            )
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

        if (
            employee_profile
            and employee_profile.archived_at
        ):
            raise serializers.ValidationError(
                {
                    "employee_profile": (
                        "No puedes asignar un horario a un "
                        "perfil laboral archivado."
                    )
                }
            )

        if schedule:
            if not schedule.is_active:
                raise serializers.ValidationError(
                    {
                        "schedule": (
                            "No puedes asignar un horario "
                            "inactivo."
                        )
                    }
                )

            if schedule.archived_at:
                raise serializers.ValidationError(
                    {
                        "schedule": (
                            "No puedes asignar un horario "
                            "archivado."
                        )
                    }
                )

        if primary_location:
            if not primary_location.is_active:
                raise serializers.ValidationError(
                    {
                        "primary_location": (
                            "La ubicación principal está "
                            "inactiva."
                        )
                    }
                )

            if primary_location.archived_at:
                raise serializers.ValidationError(
                    {
                        "primary_location": (
                            "La ubicación principal está "
                            "archivada."
                        )
                    }
                )

        if (
            location_required
            and not primary_location
            and not instance
        ):
            raise serializers.ValidationError(
                {
                    "primary_location": (
                        "Debes indicar una ubicación principal "
                        "cuando la marcación requiere ubicación."
                    )
                }
            )

        if (
            override_entry_tolerance
            and entry_tolerance_minutes is None
        ):
            raise serializers.ValidationError(
                {
                    "entry_tolerance_minutes": (
                        "Debes indicar la tolerancia "
                        "de ingreso."
                    )
                }
            )

        if (
            not override_entry_tolerance
            and entry_tolerance_minutes is not None
        ):
            raise serializers.ValidationError(
                {
                    "entry_tolerance_minutes": (
                        "Activa la modificación de tolerancia "
                        "antes de ingresar un valor."
                    )
                }
            )

        if (
            override_early_departure_tolerance
            and early_departure_tolerance_minutes
            is None
        ):
            raise serializers.ValidationError(
                {
                    "early_departure_tolerance_minutes": (
                        "Debes indicar la tolerancia "
                        "de salida."
                    )
                }
            )

        if (
            not override_early_departure_tolerance
            and early_departure_tolerance_minutes
            is not None
        ):
            raise serializers.ValidationError(
                {
                    "early_departure_tolerance_minutes": (
                        "Activa la modificación de tolerancia "
                        "antes de ingresar un valor."
                    )
                }
            )

        if (
            override_break_minutes
            and break_minutes is None
        ):
            raise serializers.ValidationError(
                {
                    "break_minutes": (
                        "Debes indicar los minutos "
                        "de refrigerio."
                    )
                }
            )

        if (
            not override_break_minutes
            and break_minutes is not None
        ):
            raise serializers.ValidationError(
                {
                    "break_minutes": (
                        "Activa la modificación del refrigerio "
                        "antes de ingresar un valor."
                    )
                }
            )

        if (
            operational_time_required
            and employee_profile
            and not employee_profile.track_operational_time
        ):
            raise serializers.ValidationError(
                {
                    "operational_time_required": (
                        "El perfil laboral no tiene habilitado "
                        "el control de tiempo operativo."
                    )
                }
            )

        if (
            attendance_required
            and employee_profile
            and not employee_profile.attendance_enabled
        ):
            raise serializers.ValidationError(
                {
                    "attendance_required": (
                        "El perfil laboral no tiene habilitado "
                        "el control de asistencia."
                    )
                }
            )

        if (
            status_value
            == (
                EmployeeScheduleAssignment
                .AssignmentStatus.CANCELLED
            )
            and not str(
                cancellation_reason or ""
            ).strip()
        ):
            raise serializers.ValidationError(
                {
                    "cancellation_reason": (
                        "Debes indicar el motivo "
                        "de cancelación."
                    )
                }
            )

        return attrs

    def validate_allowed_locations(
        self,
        value,
    ):
        for location in value:
            if not location.is_active:
                raise serializers.ValidationError(
                    (
                        f"La ubicación '{location}' "
                        "está inactiva."
                    )
                )

            if location.archived_at:
                raise serializers.ValidationError(
                    (
                        f"La ubicación '{location}' "
                        "está archivada."
                    )
                )

        return value

    def create(
        self,
        validated_data,
    ):
        try:
            return super().create(
                validated_data
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(
                    exc,
                    "message_dict",
                )
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
                if hasattr(
                    exc,
                    "message_dict",
                )
                else exc.messages
            ) from exc