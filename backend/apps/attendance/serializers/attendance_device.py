# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from apps.attendance.models import AttendanceDevice


class AttendanceDeviceSerializer(serializers.ModelSerializer):
    device_type_display = serializers.CharField(
        source="get_device_type_display",
        read_only=True,
    )

    ownership_type_display = serializers.CharField(
        source="get_ownership_type_display",
        read_only=True,
    )

    registration_status_display = serializers.CharField(
        source="get_registration_status_display",
        read_only=True,
    )

    work_location_name = serializers.SerializerMethodField()
    assigned_user_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    is_approved = serializers.BooleanField(
        read_only=True,
    )

    is_blocked = serializers.BooleanField(
        read_only=True,
    )

    is_revoked = serializers.BooleanField(
        read_only=True,
    )

    token_is_valid = serializers.BooleanField(
        read_only=True,
    )

    can_clock = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = AttendanceDevice

        fields = (
            "id",
            "code",
            "name",
            "device_type",
            "device_type_display",
            "ownership_type",
            "ownership_type_display",
            "registration_status",
            "registration_status_display",
            "work_location",
            "work_location_name",
            "assigned_user",
            "assigned_user_name",
            "device_identifier",
            "hardware_serial",
            "manufacturer",
            "model_name",
            "operating_system",
            "operating_system_version",
            "browser_name",
            "browser_version",
            "app_version",
            "local_ip_address",
            "last_public_ip_address",
            "mac_address",
            "allows_attendance_clocking",
            "allows_break_clocking",
            "allows_operational_clocking",
            "allows_multiple_users",
            "requires_user_authentication",
            "requires_pin",
            "requires_photo",
            "requires_location",
            "restrict_to_assigned_location",
            "allow_offline_clocking",
            "maximum_offline_minutes",
            "token_created_at",
            "token_expires_at",
            "token_is_valid",
            "last_seen_at",
            "last_clocking_at",
            "approved_at",
            "approved_by",
            "rejected_at",
            "rejected_by",
            "rejection_reason",
            "blocked_at",
            "blocked_by",
            "blocked_reason",
            "revoked_at",
            "revoked_by",
            "revocation_reason",
            "is_active",
            "is_approved",
            "is_blocked",
            "is_revoked",
            "can_clock",
            "notes",
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
            "registration_status",
            "last_public_ip_address",
            "token_created_at",
            "token_expires_at",
            "last_seen_at",
            "last_clocking_at",
            "approved_at",
            "approved_by",
            "rejected_at",
            "rejected_by",
            "rejection_reason",
            "blocked_at",
            "blocked_by",
            "blocked_reason",
            "revoked_at",
            "revoked_by",
            "revocation_reason",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

        extra_kwargs = {
            "device_identifier": {
                "write_only": True,
            },
        }

    def get_work_location_name(self, obj):
        if not obj.work_location_id:
            return None

        return obj.work_location.name

    def get_assigned_user_name(self, obj):
        if not obj.assigned_user_id:
            return None

        return obj.assigned_user.full_name

    def validate_code(self, value):
        value = str(value or "").strip().upper()

        if not value:
            raise serializers.ValidationError(
                "Debes indicar el código del dispositivo."
            )

        queryset = AttendanceDevice.objects.filter(
            code__iexact=value,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un dispositivo con este código."
            )

        return value

    def validate_device_identifier(self, value):
        value = str(value or "").strip()

        if not value:
            raise serializers.ValidationError(
                "Debes indicar el identificador del dispositivo."
            )

        queryset = AttendanceDevice.objects.filter(
            device_identifier=value,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Este identificador ya está registrado."
            )

        return value

    def validate_maximum_offline_minutes(self, value):
        if value > 10080:
            raise serializers.ValidationError(
                "El máximo sin conexión no puede superar 10080 minutos."
            )

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        instance = self.instance

        work_location = attrs.get(
            "work_location",
            getattr(instance, "work_location", None),
        )

        assigned_user = attrs.get(
            "assigned_user",
            getattr(instance, "assigned_user", None),
        )

        ownership_type = attrs.get(
            "ownership_type",
            getattr(
                instance,
                "ownership_type",
                AttendanceDevice.OwnershipType.COMPANY,
            ),
        )

        allows_multiple_users = attrs.get(
            "allows_multiple_users",
            getattr(instance, "allows_multiple_users", False),
        )

        requires_location = attrs.get(
            "requires_location",
            getattr(instance, "requires_location", False),
        )

        restrict_to_assigned_location = attrs.get(
            "restrict_to_assigned_location",
            getattr(
                instance,
                "restrict_to_assigned_location",
                True,
            ),
        )

        allow_offline_clocking = attrs.get(
            "allow_offline_clocking",
            getattr(instance, "allow_offline_clocking", False),
        )

        maximum_offline_minutes = attrs.get(
            "maximum_offline_minutes",
            getattr(instance, "maximum_offline_minutes", 0),
        )

        if work_location:
            if work_location.archived_at:
                raise serializers.ValidationError(
                    {
                        "work_location": (
                            "La ubicación asignada está archivada."
                        )
                    }
                )

            if not work_location.is_active:
                raise serializers.ValidationError(
                    {
                        "work_location": (
                            "La ubicación asignada está inactiva."
                        )
                    }
                )

        if (
            restrict_to_assigned_location
            and not work_location
        ):
            raise serializers.ValidationError(
                {
                    "work_location": (
                        "Debes asignar una ubicación cuando el "
                        "dispositivo está restringido a una sede."
                    )
                }
            )

        if (
            assigned_user
            and allows_multiple_users
        ):
            raise serializers.ValidationError(
                {
                    "assigned_user": (
                        "Un dispositivo compartido no debe estar "
                        "asignado a un solo usuario."
                    )
                }
            )

        if (
            not allows_multiple_users
            and not assigned_user
            and ownership_type
            == AttendanceDevice.OwnershipType.EMPLOYEE
        ):
            raise serializers.ValidationError(
                {
                    "assigned_user": (
                        "Un dispositivo personal debe estar "
                        "asignado a un usuario."
                    )
                }
            )

        if (
            allow_offline_clocking
            and maximum_offline_minutes <= 0
        ):
            raise serializers.ValidationError(
                {
                    "maximum_offline_minutes": (
                        "Debes indicar cuánto tiempo se permite "
                        "marcar sin conexión."
                    )
                }
            )

        if (
            not allow_offline_clocking
            and maximum_offline_minutes
        ):
            raise serializers.ValidationError(
                {
                    "maximum_offline_minutes": (
                        "Los minutos sin conexión deben ser cero "
                        "cuando la marcación offline está desactivada."
                    )
                }
            )

        if (
            requires_location
            and work_location
            and not work_location.has_coordinates
        ):
            raise serializers.ValidationError(
                {
                    "work_location": (
                        "La ubicación asignada no tiene "
                        "coordenadas configuradas."
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