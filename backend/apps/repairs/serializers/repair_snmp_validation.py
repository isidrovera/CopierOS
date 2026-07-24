# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from ..models import RepairSNMPValidation
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


def get_model_field_names(model):
    return tuple(
        field.name
        for field in model._meta.fields
    )


class RepairSNMPValidationListSerializer(
    serializers.ModelSerializer
):
    repair_code = serializers.CharField(
        source="repair.code",
        read_only=True,
    )

    equipment_id = serializers.UUIDField(
        source="repair.equipment_id",
        read_only=True,
    )

    equipment_serial_number = serializers.CharField(
        source="repair.equipment.serial_number",
        read_only=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.full_name",
        read_only=True,
        allow_null=True,
    )

    updated_by_name = serializers.CharField(
        source="updated_by.full_name",
        read_only=True,
        allow_null=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairSNMPValidation

        fields = (
            *get_model_field_names(
                RepairSNMPValidation
            ),
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "created_by_name",
            "updated_by_name",
            "is_archived",
        )

        read_only_fields = fields


class RepairSNMPValidationDetailSerializer(
    serializers.ModelSerializer
):
    repair_code = serializers.CharField(
        source="repair.code",
        read_only=True,
    )

    equipment_id = serializers.UUIDField(
        source="repair.equipment_id",
        read_only=True,
    )

    equipment_serial_number = serializers.CharField(
        source="repair.equipment.serial_number",
        read_only=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.full_name",
        read_only=True,
        allow_null=True,
    )

    updated_by_name = serializers.CharField(
        source="updated_by.full_name",
        read_only=True,
        allow_null=True,
    )

    archived_by_name = serializers.CharField(
        source="archived_by.full_name",
        read_only=True,
        allow_null=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairSNMPValidation

        fields = (
            *get_model_field_names(
                RepairSNMPValidation
            ),
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "created_by_name",
            "updated_by_name",
            "archived_by_name",
            "is_archived",
        )

        read_only_fields = fields


class RepairSNMPValidationCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = RepairSNMPValidation

        fields = "__all__"

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

        extra_kwargs = {
            "community": {
                "write_only": True,
                "required": False,
                "allow_blank": True,
            },
        }

    def validate_repair(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes validar una reparación archivada."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes validar una reparación inactiva."
            )

        return value

    def validate_host(self, value):
        host = str(
            value or ""
        ).strip()

        if not host:
            raise serializers.ValidationError(
                "La dirección IP o nombre del equipo es obligatorio."
            )

        return host

    def validate_community(self, value):
        return str(
            value or ""
        ).strip()

    def validate_port(self, value):
        if value < 1 or value > 65535:
            raise serializers.ValidationError(
                "El puerto debe estar entre 1 y 65535."
            )

        return value

    def validate(self, attrs):
        instance = self.instance

        repair = attrs.get(
            "repair",
            getattr(
                instance,
                "repair",
                None,
            ),
        )

        if not repair:
            raise serializers.ValidationError(
                {
                    "repair": (
                        "Debes seleccionar una reparación."
                    )
                }
            )

        queryset = (
            RepairSNMPValidation.objects.filter(
                repair=repair,
                archived_at__isnull=True,
            )
        )

        if instance:
            queryset = queryset.exclude(
                pk=instance.pk,
            )

        active_statuses = []

        status_field = (
            RepairSNMPValidation._meta.get_field(
                "status"
            )
            if any(
                field.name == "status"
                for field in RepairSNMPValidation._meta.fields
            )
            else None
        )

        if status_field:
            choice_values = {
                str(choice[0]).lower()
                for choice in status_field.choices
            }

            for possible_status in (
                "pending",
                "in_progress",
                "processing",
                "running",
            ):
                if possible_status in choice_values:
                    active_statuses.append(
                        possible_status
                    )

        if active_statuses:
            queryset = queryset.filter(
                status__in=active_statuses,
            )

            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "repair": (
                            "La reparación ya tiene una "
                            "validación SNMP pendiente o en proceso."
                        )
                    }
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        validation = RepairSNMPValidation(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            validation.full_clean()
            validation.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return validation

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        actor = get_authenticated_user(
            self
        )

        for field, value in validated_data.items():
            setattr(
                instance,
                field,
                value,
            )

        if actor:
            instance.updated_by = actor

        try:
            instance.full_clean()
            instance.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return instance


class StartRepairSNMPValidationSerializer(
    serializers.Serializer
):
    host = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )

    port = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=65535,
    )

    community = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
        write_only=True,
    )

    def validate(self, attrs):
        validation = self.context.get(
            "snmp_validation"
        )

        if not validation:
            raise serializers.ValidationError(
                "No se encontró la validación SNMP."
            )

        if validation.is_archived:
            raise serializers.ValidationError(
                "La validación SNMP está archivada."
            )

        if not validation.repair.is_active:
            raise serializers.ValidationError(
                "La reparación ya no está activa."
            )

        if hasattr(
            validation,
            "completed_at",
        ) and validation.completed_at:
            raise serializers.ValidationError(
                "La validación SNMP ya fue completada."
            )

        attrs["host"] = str(
            attrs.get(
                "host",
                getattr(
                    validation,
                    "host",
                    "",
                ),
            )
            or ""
        ).strip()

        attrs["community"] = str(
            attrs.get(
                "community",
                getattr(
                    validation,
                    "community",
                    "",
                ),
            )
            or ""
        ).strip()

        if not attrs["host"]:
            raise serializers.ValidationError(
                {
                    "host": (
                        "Debes indicar la dirección IP "
                        "o nombre del equipo."
                    )
                }
            )

        return attrs


class CompleteRepairSNMPValidationSerializer(
    serializers.Serializer
):
    raw_data = serializers.JSONField(
        required=False,
    )

    observations = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=10000,
    )

    def validate(self, attrs):
        validation = self.context.get(
            "snmp_validation"
        )

        if not validation:
            raise serializers.ValidationError(
                "No se encontró la validación SNMP."
            )

        if validation.is_archived:
            raise serializers.ValidationError(
                "La validación SNMP está archivada."
            )

        if hasattr(
            validation,
            "completed_at",
        ) and validation.completed_at:
            raise serializers.ValidationError(
                "La validación SNMP ya fue completada."
            )

        return attrs


class FailRepairSNMPValidationSerializer(
    serializers.Serializer
):
    error_message = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=10000,
    )

    observations = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=10000,
    )

    def validate_error_message(self, value):
        error_message = str(
            value or ""
        ).strip()

        if not error_message:
            raise serializers.ValidationError(
                "Debes indicar el error de la validación."
            )

        return error_message

    def validate(self, attrs):
        validation = self.context.get(
            "snmp_validation"
        )

        if not validation:
            raise serializers.ValidationError(
                "No se encontró la validación SNMP."
            )

        if validation.is_archived:
            raise serializers.ValidationError(
                "La validación SNMP está archivada."
            )

        return attrs


class RecalculateSNMPMatchesSerializer(
    serializers.Serializer
):
    def validate(self, attrs):
        validation = self.context.get(
            "snmp_validation"
        )

        if not validation:
            raise serializers.ValidationError(
                "No se encontró la validación SNMP."
            )

        if validation.is_archived:
            raise serializers.ValidationError(
                "La validación SNMP está archivada."
            )

        if not hasattr(
            validation,
            "calculate_matches",
        ):
            raise serializers.ValidationError(
                "El modelo no permite recalcular las coincidencias."
            )

        return attrs


class ArchiveRepairSNMPValidationSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )