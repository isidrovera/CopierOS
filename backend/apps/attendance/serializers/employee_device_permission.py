# -*- coding: utf-8 -*-

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from apps.attendance.models import EmployeeDevicePermission


class EmployeeDevicePermissionSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source="employee_profile.user.full_name",
        read_only=True,
    )

    device_name = serializers.CharField(
        source="device.name",
        read_only=True,
    )

    device_code = serializers.CharField(
        source="device.code",
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

    can_be_used = serializers.BooleanField(
        read_only=True,
    )

    pin = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
        min_length=4,
        max_length=20,
    )

    class Meta:
        model = EmployeeDevicePermission

        fields = (
            "id",
            "employee_profile",
            "employee_name",
            "device",
            "device_code",
            "device_name",
            "status",
            "status_display",
            "effective_from",
            "effective_until",
            "allow_attendance_clocking",
            "allow_break_clocking",
            "allow_operational_clocking",
            "allow_company_clocking",
            "allow_client_clocking",
            "allow_remote_clocking",
            "allow_service_order_clocking",
            "requires_pin",
            "pin",
            "requires_photo",
            "requires_location",
            "maximum_daily_clockings",
            "minimum_seconds_between_clockings",
            "notes",
            "activated_at",
            "activated_by",
            "suspended_at",
            "suspended_by",
            "suspension_reason",
            "revoked_at",
            "revoked_by",
            "revocation_reason",
            "finished_at",
            "finished_by",
            "last_used_at",
            "is_current",
            "can_be_used",
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
            "activated_at",
            "activated_by",
            "suspended_at",
            "suspended_by",
            "suspension_reason",
            "revoked_at",
            "revoked_by",
            "revocation_reason",
            "finished_at",
            "finished_by",
            "last_used_at",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

    def validate_maximum_daily_clockings(self, value):
        if value < 1 or value > 200:
            raise serializers.ValidationError(
                "El máximo diario debe estar entre 1 y 200."
            )

        return value

    def validate_minimum_seconds_between_clockings(
        self,
        value,
    ):
        if value < 0 or value > 3600:
            raise serializers.ValidationError(
                "El intervalo debe estar entre 0 y 3600 segundos."
            )

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        instance = self.instance

        employee_profile = attrs.get(
            "employee_profile",
            getattr(instance, "employee_profile", None),
        )

        device = attrs.get(
            "device",
            getattr(instance, "device", None),
        )

        effective_from = attrs.get(
            "effective_from",
            getattr(instance, "effective_from", None),
        )

        effective_until = attrs.get(
            "effective_until",
            getattr(instance, "effective_until", None),
        )

        allow_attendance = attrs.get(
            "allow_attendance_clocking",
            getattr(instance, "allow_attendance_clocking", True),
        )

        allow_break = attrs.get(
            "allow_break_clocking",
            getattr(instance, "allow_break_clocking", True),
        )

        allow_operational = attrs.get(
            "allow_operational_clocking",
            getattr(instance, "allow_operational_clocking", False),
        )

        requires_pin = attrs.get(
            "requires_pin",
            getattr(instance, "requires_pin", False),
        )

        pin = attrs.get("pin")

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

        if employee_profile and employee_profile.archived_at:
            raise serializers.ValidationError(
                {
                    "employee_profile": (
                        "El perfil laboral está archivado."
                    )
                }
            )

        if device:
            if device.archived_at:
                raise serializers.ValidationError(
                    {"device": "El dispositivo está archivado."}
                )

            if not device.is_active:
                raise serializers.ValidationError(
                    {"device": "El dispositivo está inactivo."}
                )

            if (
                not device.allows_multiple_users
                and device.assigned_user_id
                and employee_profile
                and device.assigned_user_id
                != employee_profile.user_id
            ):
                raise serializers.ValidationError(
                    {
                        "device": (
                            "El dispositivo está asignado "
                            "a otro usuario."
                        )
                    }
                )

            if (
                allow_attendance
                and not device.allows_attendance_clocking
            ):
                raise serializers.ValidationError(
                    {
                        "allow_attendance_clocking": (
                            "El dispositivo no permite asistencia."
                        )
                    }
                )

            if (
                allow_break
                and not device.allows_break_clocking
            ):
                raise serializers.ValidationError(
                    {
                        "allow_break_clocking": (
                            "El dispositivo no permite refrigerio."
                        )
                    }
                )

            if (
                allow_operational
                and not device.allows_operational_clocking
            ):
                raise serializers.ValidationError(
                    {
                        "allow_operational_clocking": (
                            "El dispositivo no permite "
                            "tiempos operativos."
                        )
                    }
                )

        if (
            allow_operational
            and employee_profile
            and not employee_profile.track_operational_time
        ):
            raise serializers.ValidationError(
                {
                    "allow_operational_clocking": (
                        "El perfil laboral no tiene habilitado "
                        "el control de tiempo operativo."
                    )
                }
            )

        if not any(
            (
                allow_attendance,
                allow_break,
                allow_operational,
            )
        ):
            raise serializers.ValidationError(
                {
                    "allow_attendance_clocking": (
                        "Debes habilitar al menos "
                        "un tipo de marcación."
                    )
                }
            )

        existing_pin = bool(
            instance and instance.pin_hash
        )

        if (
            requires_pin
            and not pin
            and not existing_pin
        ):
            raise serializers.ValidationError(
                {
                    "pin": (
                        "Debes configurar un PIN "
                        "para este permiso."
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        pin = validated_data.pop(
            "pin",
            None,
        )

        if pin:
            validated_data["pin_hash"] = make_password(
                pin
            )

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
        pin = validated_data.pop(
            "pin",
            None,
        )

        if pin:
            validated_data["pin_hash"] = make_password(
                pin
            )

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