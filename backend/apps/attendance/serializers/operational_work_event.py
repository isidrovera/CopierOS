# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from apps.attendance.models import OperationalWorkEvent


class OperationalWorkEventSerializer(serializers.ModelSerializer):
    session_number = serializers.CharField(
        source="session.session_number",
        read_only=True,
    )

    employee_name = serializers.CharField(
        source="session.employee_profile.user.full_name",
        read_only=True,
    )

    event_type_display = serializers.CharField(
        source="get_event_type_display",
        read_only=True,
    )

    time_category_display = serializers.CharField(
        source="get_time_category_display",
        read_only=True,
    )

    responsibility_type_display = serializers.CharField(
        source="get_responsibility_type_display",
        read_only=True,
    )

    validation_status_display = serializers.CharField(
        source="get_validation_status_display",
        read_only=True,
    )

    work_location_name = serializers.SerializerMethodField()
    device_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    has_coordinates = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = OperationalWorkEvent

        fields = (
            "id",
            "session",
            "session_number",
            "employee_name",
            "event_type",
            "event_type_display",
            "time_category",
            "time_category_display",
            "responsibility_type",
            "responsibility_type_display",
            "validation_status",
            "validation_status_display",
            "occurred_at",
            "local_date",
            "local_time",
            "timezone_name",
            "previous_status",
            "new_status",
            "previous_stage",
            "new_stage",
            "duration_minutes",
            "started_interval_at",
            "ended_interval_at",
            "title",
            "description",
            "reason",
            "work_location",
            "work_location_name",
            "device",
            "device_name",
            "latitude",
            "longitude",
            "has_coordinates",
            "location_accuracy_meters",
            "distance_to_location_meters",
            "public_ip_address",
            "local_ip_address",
            "user_agent",
            "source",
            "external_reference",
            "idempotency_key",
            "metadata",
            "requires_review",
            "review_reason",
            "reviewed_at",
            "reviewed_by",
            "corrected_event",
            "is_archived",
            "created_at",
            "created_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

        read_only_fields = (
            "id",
            "local_date",
            "local_time",
            "duration_minutes",
            "validation_status",
            "requires_review",
            "review_reason",
            "reviewed_at",
            "reviewed_by",
            "corrected_event",
            "created_at",
            "created_by",
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

    def validate_location_accuracy_meters(
        self,
        value,
    ):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "La precisión no puede ser negativa."
            )

        return value

    def validate_distance_to_location_meters(
        self,
        value,
    ):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "La distancia no puede ser negativa."
            )

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        instance = self.instance

        session = attrs.get(
            "session",
            getattr(instance, "session", None),
        )

        work_location = attrs.get(
            "work_location",
            getattr(instance, "work_location", None),
        )

        device = attrs.get(
            "device",
            getattr(instance, "device", None),
        )

        started_interval_at = attrs.get(
            "started_interval_at",
            getattr(instance, "started_interval_at", None),
        )

        ended_interval_at = attrs.get(
            "ended_interval_at",
            getattr(instance, "ended_interval_at", None),
        )

        occurred_at = attrs.get(
            "occurred_at",
            getattr(instance, "occurred_at", None),
        )

        previous_status = attrs.get(
            "previous_status",
            getattr(instance, "previous_status", ""),
        )

        new_status = attrs.get(
            "new_status",
            getattr(instance, "new_status", ""),
        )

        previous_stage = attrs.get(
            "previous_stage",
            getattr(instance, "previous_stage", ""),
        )

        new_stage = attrs.get(
            "new_stage",
            getattr(instance, "new_stage", ""),
        )

        latitude = attrs.get(
            "latitude",
            getattr(instance, "latitude", None),
        )

        longitude = attrs.get(
            "longitude",
            getattr(instance, "longitude", None),
        )

        event_type = attrs.get(
            "event_type",
            getattr(instance, "event_type", None),
        )

        time_category = attrs.get(
            "time_category",
            getattr(
                instance,
                "time_category",
                OperationalWorkEvent.TimeCategory.NONE,
            ),
        )

        responsibility_type = attrs.get(
            "responsibility_type",
            getattr(
                instance,
                "responsibility_type",
                OperationalWorkEvent
                .ResponsibilityType.NOT_APPLICABLE,
            ),
        )

        requires_review = attrs.get(
            "requires_review",
            getattr(instance, "requires_review", False),
        )

        review_reason = attrs.get(
            "review_reason",
            getattr(instance, "review_reason", ""),
        )

        if session and session.archived_at:
            raise serializers.ValidationError(
                {
                    "session": (
                        "La sesión operativa está archivada."
                    )
                }
            )

        if work_location:
            if work_location.archived_at:
                raise serializers.ValidationError(
                    {
                        "work_location": (
                            "La ubicación está archivada."
                        )
                    }
                )

            if not work_location.is_active:
                raise serializers.ValidationError(
                    {
                        "work_location": (
                            "La ubicación está inactiva."
                        )
                    }
                )

        if device:
            if device.archived_at:
                raise serializers.ValidationError(
                    {
                        "device": (
                            "El dispositivo está archivado."
                        )
                    }
                )

            if not device.is_active:
                raise serializers.ValidationError(
                    {
                        "device": (
                            "El dispositivo está inactivo."
                        )
                    }
                )

        if (
            ended_interval_at
            and not started_interval_at
        ):
            raise serializers.ValidationError(
                {
                    "started_interval_at": (
                        "Debes indicar el inicio del intervalo."
                    )
                }
            )

        if (
            started_interval_at
            and ended_interval_at
            and ended_interval_at <= started_interval_at
        ):
            raise serializers.ValidationError(
                {
                    "ended_interval_at": (
                        "El fin del intervalo debe ser posterior "
                        "al inicio."
                    )
                }
            )

        if (
            session
            and occurred_at
            and occurred_at < session.assigned_at
        ):
            raise serializers.ValidationError(
                {
                    "occurred_at": (
                        "El evento no puede ocurrir antes "
                        "de la asignación de la sesión."
                    )
                }
            )

        session_model = (
            OperationalWorkEvent
            ._meta
            .get_field("session")
            .remote_field
            .model
        )

        if (
            previous_status
            and previous_status
            not in session_model.Status.values
        ):
            raise serializers.ValidationError(
                {
                    "previous_status": (
                        "El estado anterior no es válido."
                    )
                }
            )

        if (
            new_status
            and new_status
            not in session_model.Status.values
        ):
            raise serializers.ValidationError(
                {
                    "new_status": (
                        "El nuevo estado no es válido."
                    )
                }
            )

        if (
            previous_stage
            and previous_stage
            not in session_model.CurrentStage.values
        ):
            raise serializers.ValidationError(
                {
                    "previous_stage": (
                        "La etapa anterior no es válida."
                    )
                }
            )

        if (
            new_stage
            and new_stage
            not in session_model.CurrentStage.values
        ):
            raise serializers.ValidationError(
                {
                    "new_stage": (
                        "La nueva etapa no es válida."
                    )
                }
            )

        if latitude is None and longitude is not None:
            raise serializers.ValidationError(
                {
                    "latitude": (
                        "Debes registrar la latitud junto "
                        "con la longitud."
                    )
                }
            )

        if longitude is None and latitude is not None:
            raise serializers.ValidationError(
                {
                    "longitude": (
                        "Debes registrar la longitud junto "
                        "con la latitud."
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

        if (
            event_type
            in (
                OperationalWorkEvent.EventType.WAITING_STARTED,
                OperationalWorkEvent.EventType.WAITING_ENDED,
            )
            and time_category
            not in (
                OperationalWorkEvent.TimeCategory.INTERNAL_WAITING,
                OperationalWorkEvent.TimeCategory.EXTERNAL_WAITING,
            )
        ):
            raise serializers.ValidationError(
                {
                    "time_category": (
                        "Un evento de espera debe clasificarse "
                        "como espera interna o externa."
                    )
                }
            )

        if (
            time_category
            == OperationalWorkEvent.TimeCategory.EXTERNAL_WAITING
            and responsibility_type
            == OperationalWorkEvent.ResponsibilityType.EMPLOYEE
        ):
            raise serializers.ValidationError(
                {
                    "responsibility_type": (
                        "Una espera externa no debe atribuirse "
                        "completamente al trabajador."
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