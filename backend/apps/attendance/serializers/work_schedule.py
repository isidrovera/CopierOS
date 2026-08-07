# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from apps.attendance.models.work_schedule import (
    WorkSchedule,
    WorkScheduleDay,
)


class WorkScheduleDaySerializer(serializers.ModelSerializer):
    """
    Configuración diaria de un horario laboral.
    """

    weekday_display = serializers.CharField(
        source="get_weekday_display",
        read_only=True,
    )

    schedule_name = serializers.CharField(
        source="schedule.name",
        read_only=True,
    )

    effective_entry_tolerance_minutes = serializers.IntegerField(
        read_only=True,
    )

    effective_early_departure_tolerance_minutes = serializers.IntegerField(
        read_only=True,
    )

    scheduled_break_minutes = serializers.IntegerField(
        read_only=True,
    )

    scheduled_shift_minutes = serializers.IntegerField(
        read_only=True,
    )

    scheduled_work_minutes = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = WorkScheduleDay

        fields = (
            "id",
            "schedule",
            "schedule_name",
            "weekday",
            "weekday_display",
            "is_working_day",
            "entry_time",
            "exit_time",
            "exit_next_day",
            "break_enabled",
            "break_start_time",
            "break_end_time",
            "break_end_next_day",
            "paid_break",
            "entry_tolerance_minutes",
            "effective_entry_tolerance_minutes",
            "early_departure_tolerance_minutes",
            "effective_early_departure_tolerance_minutes",
            "minimum_work_minutes",
            "expected_work_minutes",
            "scheduled_break_minutes",
            "scheduled_shift_minutes",
            "scheduled_work_minutes",
            "allows_overtime",
            "requires_attendance",
            "notes",
            "is_active",
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

    def validate_weekday(self, value):
        if value < 1 or value > 7:
            raise serializers.ValidationError(
                "El día de la semana debe estar entre 1 y 7."
            )

        return value

    def validate_entry_tolerance_minutes(self, value):
        if value is not None and value > 180:
            raise serializers.ValidationError(
                "La tolerancia de ingreso no puede superar "
                "180 minutos."
            )

        return value

    def validate_early_departure_tolerance_minutes(
        self,
        value,
    ):
        if value is not None and value > 180:
            raise serializers.ValidationError(
                "La tolerancia de salida no puede superar "
                "180 minutos."
            )

        return value

    def validate_minimum_work_minutes(self, value):
        if value > 1440:
            raise serializers.ValidationError(
                "El mínimo de trabajo no puede superar "
                "1440 minutos."
            )

        return value

    def validate_expected_work_minutes(self, value):
        if value > 1440:
            raise serializers.ValidationError(
                "Los minutos esperados no pueden superar "
                "1440 minutos."
            )

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        instance = self.instance

        schedule = attrs.get(
            "schedule",
            getattr(instance, "schedule", None),
        )

        weekday = attrs.get(
            "weekday",
            getattr(instance, "weekday", None),
        )

        is_working_day = attrs.get(
            "is_working_day",
            getattr(instance, "is_working_day", True),
        )

        entry_time = attrs.get(
            "entry_time",
            getattr(instance, "entry_time", None),
        )

        exit_time = attrs.get(
            "exit_time",
            getattr(instance, "exit_time", None),
        )

        exit_next_day = attrs.get(
            "exit_next_day",
            getattr(instance, "exit_next_day", False),
        )

        break_enabled = attrs.get(
            "break_enabled",
            getattr(instance, "break_enabled", True),
        )

        break_start_time = attrs.get(
            "break_start_time",
            getattr(instance, "break_start_time", None),
        )

        break_end_time = attrs.get(
            "break_end_time",
            getattr(instance, "break_end_time", None),
        )

        break_end_next_day = attrs.get(
            "break_end_next_day",
            getattr(instance, "break_end_next_day", False),
        )

        if schedule and weekday:
            queryset = WorkScheduleDay.objects.filter(
                schedule=schedule,
                weekday=weekday,
                archived_at__isnull=True,
            )

            if instance:
                queryset = queryset.exclude(
                    pk=instance.pk,
                )

            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "weekday": (
                            "Ya existe una configuración activa "
                            "para este día en el horario."
                        )
                    }
                )

        if is_working_day:
            if not entry_time:
                raise serializers.ValidationError(
                    {
                        "entry_time": (
                            "Debes indicar la hora de ingreso."
                        )
                    }
                )

            if not exit_time:
                raise serializers.ValidationError(
                    {
                        "exit_time": (
                            "Debes indicar la hora de salida."
                        )
                    }
                )

        else:
            if entry_time or exit_time:
                raise serializers.ValidationError(
                    {
                        "is_working_day": (
                            "Un día no laborable no debe tener "
                            "hora de ingreso ni salida."
                        )
                    }
                )

            if break_enabled:
                raise serializers.ValidationError(
                    {
                        "break_enabled": (
                            "Un día no laborable no puede "
                            "tener refrigerio."
                        )
                    }
                )

        if (
            exit_next_day
            and schedule
            and not schedule.allows_overnight_shift
        ):
            raise serializers.ValidationError(
                {
                    "exit_next_day": (
                        "El horario no permite turnos que "
                        "terminen al día siguiente."
                    )
                }
            )

        if break_enabled:
            if not break_start_time:
                raise serializers.ValidationError(
                    {
                        "break_start_time": (
                            "Debes indicar el inicio "
                            "del refrigerio."
                        )
                    }
                )

            if not break_end_time:
                raise serializers.ValidationError(
                    {
                        "break_end_time": (
                            "Debes indicar el fin "
                            "del refrigerio."
                        )
                    }
                )

        else:
            if break_start_time or break_end_time:
                raise serializers.ValidationError(
                    {
                        "break_enabled": (
                            "Desactiva las horas de refrigerio "
                            "cuando el día no tiene refrigerio."
                        )
                    }
                )

        if (
            break_end_next_day
            and not exit_next_day
        ):
            raise serializers.ValidationError(
                {
                    "break_end_next_day": (
                        "El refrigerio no puede terminar al día "
                        "siguiente si la jornada termina "
                        "el mismo día."
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


class WorkScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer principal de horarios laborales.
    """

    schedule_type_display = serializers.CharField(
        source="get_schedule_type_display",
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    is_current = serializers.BooleanField(
        read_only=True,
    )

    calculated_weekly_minutes = serializers.IntegerField(
        read_only=True,
    )

    days = WorkScheduleDaySerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = WorkSchedule

        fields = (
            "id",
            "code",
            "name",
            "description",
            "schedule_type",
            "schedule_type_display",
            "timezone_name",
            "weekly_hours",
            "calculated_weekly_minutes",
            "default_entry_tolerance_minutes",
            "default_early_departure_tolerance_minutes",
            "minimum_overtime_minutes",
            "allows_early_clock_in",
            "maximum_early_clock_in_minutes",
            "allows_late_clock_out",
            "maximum_late_clock_out_minutes",
            "automatically_deduct_break",
            "requires_break_clocking",
            "allows_split_shift",
            "allows_overnight_shift",
            "effective_from",
            "effective_until",
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

    def validate_code(self, value):
        value = str(
            value or ""
        ).strip().upper()

        if not value:
            raise serializers.ValidationError(
                "Debes indicar el código del horario."
            )

        queryset = WorkSchedule.objects.filter(
            code__iexact=value,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un horario con este código."
            )

        return value

    def validate_name(self, value):
        value = str(
            value or ""
        ).strip()

        if not value:
            raise serializers.ValidationError(
                "Debes indicar el nombre del horario."
            )

        return value

    def validate_weekly_hours(self, value):
        if value < 0 or value > 168:
            raise serializers.ValidationError(
                "Las horas semanales deben estar "
                "entre 0 y 168."
            )

        return value

    def validate_default_entry_tolerance_minutes(
        self,
        value,
    ):
        if value > 180:
            raise serializers.ValidationError(
                "La tolerancia de ingreso no puede "
                "superar 180 minutos."
            )

        return value

    def validate_default_early_departure_tolerance_minutes(
        self,
        value,
    ):
        if value > 180:
            raise serializers.ValidationError(
                "La tolerancia de salida no puede "
                "superar 180 minutos."
            )

        return value

    def validate_maximum_early_clock_in_minutes(
        self,
        value,
    ):
        if value > 720:
            raise serializers.ValidationError(
                "El máximo de anticipación no puede "
                "superar 720 minutos."
            )

        return value

    def validate_maximum_late_clock_out_minutes(
        self,
        value,
    ):
        if value > 1440:
            raise serializers.ValidationError(
                "El máximo posterior a la salida no puede "
                "superar 1440 minutos."
            )

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        instance = self.instance

        effective_from = attrs.get(
            "effective_from",
            getattr(instance, "effective_from", None),
        )

        effective_until = attrs.get(
            "effective_until",
            getattr(instance, "effective_until", None),
        )

        automatically_deduct_break = attrs.get(
            "automatically_deduct_break",
            getattr(
                instance,
                "automatically_deduct_break",
                False,
            ),
        )

        requires_break_clocking = attrs.get(
            "requires_break_clocking",
            getattr(
                instance,
                "requires_break_clocking",
                True,
            ),
        )

        allows_early_clock_in = attrs.get(
            "allows_early_clock_in",
            getattr(
                instance,
                "allows_early_clock_in",
                True,
            ),
        )

        maximum_early_clock_in_minutes = attrs.get(
            "maximum_early_clock_in_minutes",
            getattr(
                instance,
                "maximum_early_clock_in_minutes",
                120,
            ),
        )

        allows_late_clock_out = attrs.get(
            "allows_late_clock_out",
            getattr(
                instance,
                "allows_late_clock_out",
                True,
            ),
        )

        maximum_late_clock_out_minutes = attrs.get(
            "maximum_late_clock_out_minutes",
            getattr(
                instance,
                "maximum_late_clock_out_minutes",
                240,
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
            automatically_deduct_break
            and requires_break_clocking
        ):
            raise serializers.ValidationError(
                {
                    "automatically_deduct_break": (
                        "No puedes descontar automáticamente "
                        "el refrigerio y exigir su marcación "
                        "al mismo tiempo."
                    )
                }
            )

        if (
            not allows_early_clock_in
            and maximum_early_clock_in_minutes
        ):
            raise serializers.ValidationError(
                {
                    "maximum_early_clock_in_minutes": (
                        "Debe ser cero cuando no se permite "
                        "marcar antes."
                    )
                }
            )

        if (
            not allows_late_clock_out
            and maximum_late_clock_out_minutes
        ):
            raise serializers.ValidationError(
                {
                    "maximum_late_clock_out_minutes": (
                        "Debe ser cero cuando no se permite "
                        "marcar después de la salida."
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