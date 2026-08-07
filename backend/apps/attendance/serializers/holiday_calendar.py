# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from apps.attendance.models.holiday_calendar import (
    HolidayCalendar,
    HolidayCalendarDay,
)


class HolidayCalendarDaySerializer(serializers.ModelSerializer):
    day_type_display = serializers.CharField(
        source="get_day_type_display",
        read_only=True,
    )

    compensation_mode_display = serializers.CharField(
        source="get_compensation_mode_display",
        read_only=True,
    )

    calendar_name = serializers.CharField(
        source="calendar.name",
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = HolidayCalendarDay

        fields = (
            "id",
            "calendar",
            "calendar_name",
            "date",
            "name",
            "description",
            "day_type",
            "day_type_display",
            "is_working_day",
            "is_paid",
            "requires_compensation",
            "compensation_mode",
            "compensation_mode_display",
            "compensation_minutes",
            "substitute_rest_required",
            "special_entry_time",
            "special_exit_time",
            "special_break_minutes",
            "applies_to_private_sector",
            "legal_reference",
            "source_url",
            "notes",
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
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

    def validate_compensation_minutes(self, value):
        if value > 1440:
            raise serializers.ValidationError(
                "Los minutos de compensación no pueden superar 1440."
            )

        return value

    def validate_special_break_minutes(self, value):
        if value is not None and value > 300:
            raise serializers.ValidationError(
                "El refrigerio especial no puede superar 300 minutos."
            )

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        instance = self.instance

        calendar = attrs.get(
            "calendar",
            getattr(instance, "calendar", None),
        )

        date = attrs.get(
            "date",
            getattr(instance, "date", None),
        )

        requires_compensation = attrs.get(
            "requires_compensation",
            getattr(instance, "requires_compensation", False),
        )

        compensation_mode = attrs.get(
            "compensation_mode",
            getattr(
                instance,
                "compensation_mode",
                HolidayCalendarDay.CompensationMode.NONE,
            ),
        )

        compensation_minutes = attrs.get(
            "compensation_minutes",
            getattr(instance, "compensation_minutes", 0),
        )

        substitute_rest_required = attrs.get(
            "substitute_rest_required",
            getattr(instance, "substitute_rest_required", False),
        )

        is_working_day = attrs.get(
            "is_working_day",
            getattr(instance, "is_working_day", False),
        )

        special_entry_time = attrs.get(
            "special_entry_time",
            getattr(instance, "special_entry_time", None),
        )

        special_exit_time = attrs.get(
            "special_exit_time",
            getattr(instance, "special_exit_time", None),
        )

        if calendar and date:
            if date < calendar.effective_from:
                raise serializers.ValidationError(
                    {
                        "date": (
                            "La fecha no puede ser anterior "
                            "al inicio del calendario."
                        )
                    }
                )

            if (
                calendar.effective_until
                and date > calendar.effective_until
            ):
                raise serializers.ValidationError(
                    {
                        "date": (
                            "La fecha no puede ser posterior "
                            "al fin del calendario."
                        )
                    }
                )

            queryset = HolidayCalendarDay.objects.filter(
                calendar=calendar,
                date=date,
                archived_at__isnull=True,
            )

            if instance:
                queryset = queryset.exclude(pk=instance.pk)

            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "date": (
                            "Ya existe un día activo para esta "
                            "fecha en el calendario."
                        )
                    }
                )

        if (
            requires_compensation
            and compensation_mode
            == HolidayCalendarDay.CompensationMode.NONE
        ):
            raise serializers.ValidationError(
                {
                    "compensation_mode": (
                        "Debes indicar cómo se realizará "
                        "la compensación."
                    )
                }
            )

        if (
            not requires_compensation
            and compensation_mode
            != HolidayCalendarDay.CompensationMode.NONE
        ):
            raise serializers.ValidationError(
                {
                    "compensation_mode": (
                        "No debes configurar compensación "
                        "cuando el día no la requiere."
                    )
                }
            )

        if (
            compensation_mode
            == HolidayCalendarDay.CompensationMode.HOURS
            and compensation_minutes <= 0
        ):
            raise serializers.ValidationError(
                {
                    "compensation_minutes": (
                        "Debes indicar los minutos a compensar."
                    )
                }
            )

        if (
            compensation_mode
            != HolidayCalendarDay.CompensationMode.HOURS
            and compensation_minutes
        ):
            raise serializers.ValidationError(
                {
                    "compensation_minutes": (
                        "Los minutos solo corresponden "
                        "a compensación por horas."
                    )
                }
            )

        if (
            substitute_rest_required
            and compensation_mode
            != HolidayCalendarDay.CompensationMode.SUBSTITUTE_REST
        ):
            raise serializers.ValidationError(
                {
                    "compensation_mode": (
                        "Selecciona descanso sustitutorio "
                        "como forma de compensación."
                    )
                }
            )

        has_special_times = (
            special_entry_time
            or special_exit_time
        )

        if (
            is_working_day
            and has_special_times
            and (
                not special_entry_time
                or not special_exit_time
            )
        ):
            raise serializers.ValidationError(
                {
                    "special_entry_time": (
                        "Debes indicar hora de ingreso y salida especial."
                    )
                }
            )

        if (
            not is_working_day
            and has_special_times
        ):
            raise serializers.ValidationError(
                {
                    "is_working_day": (
                        "Un día no laborable no debe tener horario especial."
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


class HolidayCalendarSerializer(serializers.ModelSerializer):
    calendar_type_display = serializers.CharField(
        source="get_calendar_type_display",
        read_only=True,
    )

    work_location_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    is_current = serializers.BooleanField(
        read_only=True,
    )

    days = HolidayCalendarDaySerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = HolidayCalendar

        fields = (
            "id",
            "code",
            "name",
            "description",
            "calendar_type",
            "calendar_type_display",
            "country_code",
            "region",
            "province",
            "district",
            "work_location",
            "work_location_name",
            "effective_from",
            "effective_until",
            "is_default",
            "is_active",
            "is_current",
            "is_archived",
            "days",
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

    def get_work_location_name(self, obj):
        if not obj.work_location_id:
            return None

        return obj.work_location.name

    def validate_code(self, value):
        value = str(value or "").strip().upper()

        queryset = HolidayCalendar.objects.filter(
            code__iexact=value,
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un calendario con este código."
            )

        return value

    def validate_country_code(self, value):
        value = str(value or "").strip().upper()

        if len(value) != 2:
            raise serializers.ValidationError(
                "El código de país debe tener 2 caracteres."
            )

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        instance = self.instance

        calendar_type = attrs.get(
            "calendar_type",
            getattr(
                instance,
                "calendar_type",
                HolidayCalendar.CalendarType.NATIONAL,
            ),
        )

        work_location = attrs.get(
            "work_location",
            getattr(instance, "work_location", None),
        )

        effective_from = attrs.get(
            "effective_from",
            getattr(instance, "effective_from", None),
        )

        effective_until = attrs.get(
            "effective_until",
            getattr(instance, "effective_until", None),
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
            calendar_type
            == HolidayCalendar.CalendarType.LOCATION
            and not work_location
        ):
            raise serializers.ValidationError(
                {
                    "work_location": (
                        "Un calendario por ubicación debe estar "
                        "vinculado a una ubicación."
                    )
                }
            )

        if (
            work_location
            and work_location.archived_at
        ):
            raise serializers.ValidationError(
                {
                    "work_location": (
                        "La ubicación de trabajo está archivada."
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