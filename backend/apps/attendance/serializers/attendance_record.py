# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from apps.attendance.models import AttendanceRecord


class AttendanceRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source="employee_profile.user.full_name",
        read_only=True,
    )

    record_type_display = serializers.CharField(
        source="get_record_type_display",
        read_only=True,
    )

    source_type_display = serializers.CharField(
        source="get_source_type_display",
        read_only=True,
    )

    validation_status_display = serializers.CharField(
        source="get_validation_status_display",
        read_only=True,
    )

    location_status_display = serializers.CharField(
        source="get_location_status_display",
        read_only=True,
    )

    sync_status_display = serializers.CharField(
        source="get_sync_status_display",
        read_only=True,
    )

    device_name = serializers.SerializerMethodField()
    work_location_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    has_coordinates = serializers.BooleanField(
        read_only=True,
    )

    is_valid = serializers.BooleanField(
        read_only=True,
    )

    is_offline_record = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = AttendanceRecord

        fields = (
            "id",
            "employee_profile",
            "employee_name",
            "record_type",
            "record_type_display",
            "source_type",
            "source_type_display",
            "occurred_at",
            "local_date",
            "local_time",
            "timezone_name",
            "server_received_at",
            "device_reported_at",
            "device",
            "device_name",
            "device_permission",
            "work_location",
            "work_location_name",
            "latitude",
            "longitude",
            "has_coordinates",
            "location_accuracy_meters",
            "altitude_meters",
            "distance_to_location_meters",
            "location_status",
            "location_status_display",
            "location_validated_at",
            "photo",
            "public_ip_address",
            "local_ip_address",
            "user_agent",
            "app_version",
            "device_identifier",
            "sync_status",
            "sync_status_display",
            "offline_created_at",
            "synchronized_at",
            "external_reference",
            "idempotency_key",
            "observation",
            "employee_note",
            "validation_status",
            "validation_status_display",
            "validation_message",
            "requires_review",
            "review_reason",
            "reviewed_at",
            "reviewed_by",
            "rejection_reason",
            "corrected_record",
            "is_manual",
            "manual_reason",
            "registered_by",
            "is_valid",
            "is_offline_record",
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
            "local_date",
            "local_time",
            "server_received_at",
            "distance_to_location_meters",
            "location_validated_at",
            "validation_status",
            "validation_message",
            "requires_review",
            "review_reason",
            "reviewed_at",
            "reviewed_by",
            "rejection_reason",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

    def get_device_name(self, obj):
        if not obj.device_id:
            return None

        return obj.device.name

    def get_work_location_name(self, obj):
        if not obj.work_location_id:
            return None

        return obj.work_location.name

    def validate_latitude(self, value):
        if value is not None and not (
            -90 <= value <= 90
        ):
            raise serializers.ValidationError(
                "La latitud debe estar entre -90 y 90."
            )

        return value

    def validate_longitude(self, value):
        if value is not None and not (
            -180 <= value <= 180
        ):
            raise serializers.ValidationError(
                "La longitud debe estar entre -180 y 180."
            )

        return value

    def validate_location_accuracy_meters(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "La precisión no puede ser negativa."
            )

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        instance = self.instance

        employee_profile = attrs.get(
            "employee_profile",
            getattr(instance, "employee_profile", None),
        )

        source_type = attrs.get(
            "source_type",
            getattr(
                instance,
                "source_type",
                AttendanceRecord.SourceType.WEB,
            ),
        )

        device = attrs.get(
            "device",
            getattr(instance, "device", None),
        )

        device_permission = attrs.get(
            "device_permission",
            getattr(instance, "device_permission", None),
        )

        work_location = attrs.get(
            "work_location",
            getattr(instance, "work_location", None),
        )

        latitude = attrs.get(
            "latitude",
            getattr(instance, "latitude", None),
        )

        longitude = attrs.get(
            "longitude",
            getattr(instance, "longitude", None),
        )

        is_manual = attrs.get(
            "is_manual",
            getattr(instance, "is_manual", False),
        )

        manual_reason = attrs.get(
            "manual_reason",
            getattr(instance, "manual_reason", ""),
        )

        registered_by = attrs.get(
            "registered_by",
            getattr(instance, "registered_by", None),
        )

        sync_status = attrs.get(
            "sync_status",
            getattr(
                instance,
                "sync_status",
                AttendanceRecord.SyncStatus.ONLINE,
            ),
        )

        offline_created_at = attrs.get(
            "offline_created_at",
            getattr(instance, "offline_created_at", None),
        )

        synchronized_at = attrs.get(
            "synchronized_at",
            getattr(instance, "synchronized_at", None),
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

            if (
                not employee_profile.attendance_enabled
                and source_type
                not in (
                    AttendanceRecord.SourceType.SYSTEM,
                    AttendanceRecord.SourceType.MANUAL,
                )
            ):
                raise serializers.ValidationError(
                    {
                        "employee_profile": (
                            "El trabajador no tiene habilitado "
                            "el control de asistencia."
                        )
                    }
                )

        if device_permission:
            if (
                device
                and device_permission.device_id != device.id
            ):
                raise serializers.ValidationError(
                    {
                        "device_permission": (
                            "El permiso no corresponde "
                            "al dispositivo."
                        )
                    }
                )

            if (
                employee_profile
                and device_permission.employee_profile_id
                != employee_profile.id
            ):
                raise serializers.ValidationError(
                    {
                        "device_permission": (
                            "El permiso no corresponde "
                            "al trabajador."
                        )
                    }
                )

        if (
            device
            and source_type
            in (
                AttendanceRecord.SourceType.FIXED_DEVICE,
                AttendanceRecord.SourceType.MOBILE,
                AttendanceRecord.SourceType.WEB,
                AttendanceRecord.SourceType.QR,
            )
            and not device.can_clock
        ):
            raise serializers.ValidationError(
                {
                    "device": (
                        "El dispositivo no está habilitado "
                        "para registrar asistencia."
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

        if latitude is None and longitude is not None:
            raise serializers.ValidationError(
                {
                    "latitude": (
                        "Debes indicar la latitud junto "
                        "con la longitud."
                    )
                }
            )

        if longitude is None and latitude is not None:
            raise serializers.ValidationError(
                {
                    "longitude": (
                        "Debes indicar la longitud junto "
                        "con la latitud."
                    )
                }
            )

        if (
            source_type
            == AttendanceRecord.SourceType.MANUAL
            and not is_manual
        ):
            raise serializers.ValidationError(
                {
                    "is_manual": (
                        "Una marcación manual debe "
                        "identificarse como tal."
                    )
                }
            )

        if (
            is_manual
            and not str(manual_reason or "").strip()
        ):
            raise serializers.ValidationError(
                {
                    "manual_reason": (
                        "Debes indicar el motivo "
                        "del registro manual."
                    )
                }
            )

        if is_manual and not registered_by:
            raise serializers.ValidationError(
                {
                    "registered_by": (
                        "Debes indicar quién registró "
                        "la marcación manual."
                    )
                }
            )

        if (
            sync_status
            == AttendanceRecord.SyncStatus.OFFLINE_PENDING
            and not offline_created_at
        ):
            raise serializers.ValidationError(
                {
                    "offline_created_at": (
                        "Debes indicar cuándo se creó "
                        "la marcación sin conexión."
                    )
                }
            )

        if (
            sync_status
            == AttendanceRecord.SyncStatus.OFFLINE_SYNCED
            and not synchronized_at
        ):
            raise serializers.ValidationError(
                {
                    "synchronized_at": (
                        "Debes indicar cuándo se sincronizó "
                        "la marcación."
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")

        if (
            validated_data.get("is_manual")
            and request
            and not validated_data.get("registered_by")
        ):
            validated_data["registered_by"] = request.user

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