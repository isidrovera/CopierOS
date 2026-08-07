# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from apps.attendance.models import EmployeeProfile


class EmployeeProfileSerializer(serializers.ModelSerializer):
    """
    Serializer principal del perfil laboral.

    Maneja la configuración de:

    - Estado y régimen laboral.
    - Modalidad de trabajo.
    - Control de asistencia.
    - Métodos permitidos de marcación.
    - Control de tiempo operativo.
    - Evaluación del personal.
    - Tolerancias.
    - Jornada semanal.
    - Jefe inmediato.
    - Vigencia.
    """

    user_full_name = serializers.CharField(
        source="user.full_name",
        read_only=True,
    )

    manager_full_name = serializers.SerializerMethodField()

    employment_status_display = serializers.CharField(
        source="get_employment_status_display",
        read_only=True,
    )

    employment_regime_display = serializers.CharField(
        source="get_employment_regime_display",
        read_only=True,
    )

    work_mode_display = serializers.CharField(
        source="get_work_mode_display",
        read_only=True,
    )

    attendance_mode_display = serializers.CharField(
        source="get_attendance_mode_display",
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    is_current = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = EmployeeProfile

        fields = (
            "id",
            "user",
            "user_full_name",
            "employee_code",
            "employment_status",
            "employment_status_display",
            "employment_regime",
            "employment_regime_display",
            "work_mode",
            "work_mode_display",
            "hire_date",
            "termination_date",
            "attendance_enabled",
            "attendance_mode",
            "attendance_mode_display",
            "requires_location",
            "requires_photo",
            "can_clock_from_company",
            "can_clock_from_client",
            "can_clock_remotely",
            "can_clock_from_service_order",
            "allow_fixed_device",
            "allow_web",
            "allow_mobile",
            "allow_qr",
            "track_operational_time",
            "include_in_staff_evaluation",
            "include_attendance_in_evaluation",
            "include_productivity_in_evaluation",
            "default_break_minutes",
            "entry_tolerance_minutes",
            "early_departure_tolerance_minutes",
            "weekly_hours",
            "overtime_requires_approval",
            "manager",
            "manager_full_name",
            "notes",
            "effective_from",
            "effective_until",
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
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

    def get_manager_full_name(self, obj):
        if not obj.manager_id:
            return None

        return obj.manager.full_name

    def validate_employee_code(self, value):
        if value is None:
            return value

        value = str(value).strip()

        if not value:
            return None

        queryset = EmployeeProfile.objects.filter(
            employee_code__iexact=value,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un trabajador con este código."
            )

        return value.upper()

    def validate(self, attrs):
        attrs = super().validate(attrs)

        instance = self.instance

        user = attrs.get(
            "user",
            getattr(instance, "user", None),
        )

        manager = attrs.get(
            "manager",
            getattr(instance, "manager", None),
        )

        hire_date = attrs.get(
            "hire_date",
            getattr(instance, "hire_date", None),
        )

        termination_date = attrs.get(
            "termination_date",
            getattr(instance, "termination_date", None),
        )

        effective_from = attrs.get(
            "effective_from",
            getattr(instance, "effective_from", None),
        )

        effective_until = attrs.get(
            "effective_until",
            getattr(instance, "effective_until", None),
        )

        employment_status = attrs.get(
            "employment_status",
            getattr(
                instance,
                "employment_status",
                EmployeeProfile.EmploymentStatus.ACTIVE,
            ),
        )

        attendance_enabled = attrs.get(
            "attendance_enabled",
            getattr(
                instance,
                "attendance_enabled",
                True,
            ),
        )

        attendance_mode = attrs.get(
            "attendance_mode",
            getattr(
                instance,
                "attendance_mode",
                EmployeeProfile.AttendanceMode.MULTIPLE,
            ),
        )

        track_operational_time = attrs.get(
            "track_operational_time",
            getattr(
                instance,
                "track_operational_time",
                False,
            ),
        )

        if (
            user
            and manager
            and user.pk == manager.pk
        ):
            raise serializers.ValidationError(
                {
                    "manager": (
                        "El usuario no puede ser "
                        "su propio jefe inmediato."
                    )
                }
            )

        if (
            hire_date
            and termination_date
            and termination_date < hire_date
        ):
            raise serializers.ValidationError(
                {
                    "termination_date": (
                        "La fecha de cese no puede ser anterior "
                        "a la fecha de ingreso."
                    )
                }
            )

        if (
            effective_from
            and effective_until
            and effective_until < effective_from
        ):
            raise serializers.ValidationError(
                {
                    "effective_until": (
                        "La fecha final de vigencia no puede ser "
                        "anterior a la fecha inicial."
                    )
                }
            )

        if (
            employment_status
            == EmployeeProfile.EmploymentStatus.TERMINATED
            and not termination_date
        ):
            raise serializers.ValidationError(
                {
                    "termination_date": (
                        "Debes indicar la fecha de cese."
                    )
                }
            )

        if (
            attendance_enabled
            and attendance_mode
            == EmployeeProfile.AttendanceMode.NONE
        ):
            raise serializers.ValidationError(
                {
                    "attendance_mode": (
                        "Selecciona un método de asistencia "
                        "o desactiva el control de asistencia."
                    )
                }
            )

        if (
            not attendance_enabled
            and track_operational_time
        ):
            raise serializers.ValidationError(
                {
                    "track_operational_time": (
                        "No puedes controlar tiempos operativos "
                        "si el control de asistencia "
                        "está desactivado."
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