# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers

from ..models import (
    Equipment,
    MeterReading,
)
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class MeterReadingListSerializer(
    serializers.ModelSerializer
):
    """
    Serializer reducido para listar lecturas de contadores.
    """

    equipment_internal_code = serializers.CharField(
        source="equipment.internal_code",
        read_only=True,
    )

    equipment_serial_number = serializers.CharField(
        source="equipment.serial_number",
        read_only=True,
    )

    equipment_model_name = serializers.CharField(
        source="equipment.equipment_model.name",
        read_only=True,
    )

    equipment_brand_name = serializers.CharField(
        source="equipment.equipment_model.brand.name",
        read_only=True,
    )

    reading_type_name = serializers.CharField(
        source="get_reading_type_display",
        read_only=True,
    )

    source_name = serializers.CharField(
        source="get_source_display",
        read_only=True,
    )

    reference_type_name = serializers.CharField(
        source="get_reference_type_display",
        read_only=True,
    )

    registered_by_name = serializers.CharField(
        source="registered_by.full_name",
        read_only=True,
        allow_null=True,
    )

    verified_by_name = serializers.CharField(
        source="verified_by.full_name",
        read_only=True,
        allow_null=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = MeterReading

        fields = (
            "id",
            "equipment",
            "equipment_internal_code",
            "equipment_serial_number",
            "equipment_model_name",
            "equipment_brand_name",
            "reading_date",
            "reading_type",
            "reading_type_name",
            "source",
            "source_name",
            "total_meter",
            "black_meter",
            "color_meter",
            "scan_meter",
            "previous_total_meter",
            "previous_black_meter",
            "previous_color_meter",
            "previous_scan_meter",
            "total_difference",
            "black_difference",
            "color_difference",
            "scan_difference",
            "registered_by",
            "registered_by_name",
            "reference_type",
            "reference_type_name",
            "reference_number",
            "is_verified",
            "verified_by",
            "verified_by_name",
            "verified_at",
            "is_applied_to_equipment",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class MeterReadingDetailSerializer(
    serializers.ModelSerializer
):
    """
    Serializer completo de una lectura de contador.
    """

    equipment_internal_code = serializers.CharField(
        source="equipment.internal_code",
        read_only=True,
    )

    equipment_serial_number = serializers.CharField(
        source="equipment.serial_number",
        read_only=True,
    )

    equipment_model_name = serializers.CharField(
        source="equipment.equipment_model.name",
        read_only=True,
    )

    equipment_model_code = serializers.CharField(
        source="equipment.equipment_model.code",
        read_only=True,
    )

    equipment_brand_name = serializers.CharField(
        source="equipment.equipment_model.brand.name",
        read_only=True,
    )

    equipment_color_mode = serializers.CharField(
        source="equipment.equipment_model.color_mode",
        read_only=True,
    )

    equipment_color_mode_name = serializers.CharField(
        source=(
            "equipment.equipment_model."
            "get_color_mode_display"
        ),
        read_only=True,
    )

    reading_type_name = serializers.CharField(
        source="get_reading_type_display",
        read_only=True,
    )

    source_name = serializers.CharField(
        source="get_source_display",
        read_only=True,
    )

    reference_type_name = serializers.CharField(
        source="get_reference_type_display",
        read_only=True,
    )

    registered_by_name = serializers.CharField(
        source="registered_by.full_name",
        read_only=True,
        allow_null=True,
    )

    verified_by_name = serializers.CharField(
        source="verified_by.full_name",
        read_only=True,
        allow_null=True,
    )

    is_archived = serializers.BooleanField(
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

    class Meta:
        model = MeterReading

        fields = (
            "id",
            "equipment",
            "equipment_internal_code",
            "equipment_serial_number",
            "equipment_model_name",
            "equipment_model_code",
            "equipment_brand_name",
            "equipment_color_mode",
            "equipment_color_mode_name",
            "reading_date",
            "reading_type",
            "reading_type_name",
            "source",
            "source_name",
            "total_meter",
            "black_meter",
            "color_meter",
            "scan_meter",
            "previous_total_meter",
            "previous_black_meter",
            "previous_color_meter",
            "previous_scan_meter",
            "total_difference",
            "black_difference",
            "color_difference",
            "scan_difference",
            "registered_by",
            "registered_by_name",
            "reference_type",
            "reference_type_name",
            "reference_id",
            "reference_number",
            "ip_address",
            "device_timestamp",
            "is_verified",
            "verified_by",
            "verified_by_name",
            "verified_at",
            "is_applied_to_equipment",
            "correction_reason",
            "notes",
            "is_archived",
            "archived_at",
            "archived_reason",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_by",
            "archived_by_name",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "equipment_internal_code",
            "equipment_serial_number",
            "equipment_model_name",
            "equipment_model_code",
            "equipment_brand_name",
            "equipment_color_mode",
            "equipment_color_mode_name",
            "reading_type_name",
            "source_name",
            "reference_type_name",
            "previous_total_meter",
            "previous_black_meter",
            "previous_color_meter",
            "previous_scan_meter",
            "total_difference",
            "black_difference",
            "color_difference",
            "scan_difference",
            "registered_by_name",
            "verified_by_name",
            "is_applied_to_equipment",
            "is_archived",
            "archived_at",
            "archived_reason",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_by",
            "archived_by_name",
            "created_at",
            "updated_at",
        )


class MeterReadingCreateUpdateSerializer(
    serializers.ModelSerializer
):
    """
    Creación y modificación de lecturas de contadores.

    La lectura no actualiza automáticamente la ficha del equipo.

    Después de validar la lectura deberá ejecutarse una acción
    específica para aplicarla al equipo.
    """

    class Meta:
        model = MeterReading

        fields = (
            "equipment",
            "reading_date",
            "reading_type",
            "source",
            "total_meter",
            "black_meter",
            "color_meter",
            "scan_meter",
            "registered_by",
            "reference_type",
            "reference_id",
            "reference_number",
            "ip_address",
            "device_timestamp",
            "is_verified",
            "verified_by",
            "verified_at",
            "correction_reason",
            "notes",
        )

    def validate_equipment(self, value):
        """
        Impide registrar lecturas para equipos archivados
        o inactivos.
        """

        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes registrar lecturas en un equipo archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes registrar lecturas en un equipo inactivo."
            )

        return value

    def validate_reference_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_correction_reason(self, value):
        return str(
            value or ""
        ).strip()

    def validate_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate(self, attrs):
        """
        Valida la coherencia de la lectura, el equipo,
        los contadores y la referencia relacionada.
        """

        instance = self.instance

        values = {}

        if instance:
            for field in self.Meta.fields:
                values[field] = getattr(
                    instance,
                    field,
                    None,
                )

        values.update(attrs)

        equipment = values.get(
            "equipment"
        )

        reading_date = values.get(
            "reading_date"
        )

        reading_type = values.get(
            "reading_type"
        )

        source = values.get(
            "source"
        )

        total_meter = values.get(
            "total_meter"
        )

        black_meter = values.get(
            "black_meter"
        )

        color_meter = values.get(
            "color_meter"
        )

        scan_meter = values.get(
            "scan_meter"
        )

        reference_type = values.get(
            "reference_type"
        )

        reference_id = values.get(
            "reference_id"
        )

        reference_number = str(
            values.get(
                "reference_number",
                "",
            )
            or ""
        ).strip()

        is_verified = values.get(
            "is_verified",
            False,
        )

        verified_by = values.get(
            "verified_by"
        )

        verified_at = values.get(
            "verified_at"
        )

        correction_reason = str(
            values.get(
                "correction_reason",
                "",
            )
            or ""
        ).strip()

        meter_values = (
            total_meter,
            black_meter,
            color_meter,
            scan_meter,
        )

        if not equipment:
            raise serializers.ValidationError(
                {
                    "equipment": (
                        "Debes seleccionar el equipo relacionado."
                    )
                }
            )

        if not reading_date:
            raise serializers.ValidationError(
                {
                    "reading_date": (
                        "Debes registrar la fecha y hora "
                        "de la lectura."
                    )
                }
            )

        if all(
            value is None
            for value in meter_values
        ):
            raise serializers.ValidationError(
                {
                    "total_meter": (
                        "Debes registrar al menos uno "
                        "de los contadores."
                    )
                }
            )

        if (
            reference_type
            != MeterReading.ReferenceType.NONE
            and not reference_id
            and not reference_number
        ):
            raise serializers.ValidationError(
                {
                    "reference_number": (
                        "Debes indicar el ID o número del proceso "
                        "relacionado."
                    )
                }
            )

        if (
            reference_type
            == MeterReading.ReferenceType.NONE
            and reference_id
        ):
            raise serializers.ValidationError(
                {
                    "reference_type": (
                        "Debes seleccionar el tipo de proceso "
                        "antes de registrar un ID relacionado."
                    )
                }
            )

        if (
            reference_type
            == MeterReading.ReferenceType.NONE
            and reference_number
        ):
            raise serializers.ValidationError(
                {
                    "reference_type": (
                        "Debes seleccionar el tipo de proceso "
                        "antes de registrar un número relacionado."
                    )
                }
            )

        special_reading_types = {
            MeterReading.ReadingType.CORRECTION,
            MeterReading.ReadingType.RESET,
        }

        if (
            reading_type in special_reading_types
            and not correction_reason
        ):
            raise serializers.ValidationError(
                {
                    "correction_reason": (
                        "Debes indicar el motivo de la corrección "
                        "o reinicio del contador."
                    )
                }
            )

        if (
            reading_type
            not in special_reading_types
            and correction_reason
        ):
            raise serializers.ValidationError(
                {
                    "correction_reason": (
                        "El motivo de corrección solo corresponde "
                        "a lecturas de corrección o reinicio."
                    )
                }
            )

        if (
            is_verified
            and not verified_by
        ):
            actor = get_authenticated_user(
                self
            )

            if actor:
                attrs["verified_by"] = actor
                verified_by = actor

        if (
            is_verified
            and not verified_at
        ):
            from django.utils import timezone

            attrs["verified_at"] = timezone.now()
            verified_at = attrs["verified_at"]

        if (
            not is_verified
            and verified_by
        ):
            raise serializers.ValidationError(
                {
                    "verified_by": (
                        "No puedes indicar un verificador si "
                        "la lectura no está marcada como verificada."
                    )
                }
            )

        if (
            not is_verified
            and verified_at
        ):
            raise serializers.ValidationError(
                {
                    "verified_at": (
                        "No puedes indicar una fecha de verificación "
                        "si la lectura no está marcada como verificada."
                    )
                }
            )

        if equipment:
            equipment_model = equipment.equipment_model

            if (
                color_meter is not None
                and color_meter > 0
                and not equipment_model.has_color_meter
            ):
                raise serializers.ValidationError(
                    {
                        "color_meter": (
                            "El modelo seleccionado no utiliza "
                            "contador de color."
                        )
                    }
                )

            if (
                equipment_model.color_mode
                == EquipmentModel.ColorMode.MONOCHROME
                and color_meter is not None
                and color_meter > 0
            ):
                raise serializers.ValidationError(
                    {
                        "color_meter": (
                            "Un equipo blanco y negro no puede "
                            "registrar contador de color."
                        )
                    }
                )

            if (
                scan_meter is not None
                and scan_meter > 0
                and not equipment_model.has_scan_meter
            ):
                raise serializers.ValidationError(
                    {
                        "scan_meter": (
                            "El modelo seleccionado no utiliza "
                            "contador de escaneo."
                        )
                    }
                )

            previous_reading = (
                MeterReading.objects.filter(
                    equipment=equipment,
                    reading_date__lt=reading_date,
                )
            )

            if instance:
                previous_reading = previous_reading.exclude(
                    pk=instance.pk,
                )

            previous_reading = previous_reading.order_by(
                "-reading_date",
                "-created_at",
            ).first()

            if previous_reading:
                previous_values = {
                    "total_meter": previous_reading.total_meter,
                    "black_meter": previous_reading.black_meter,
                    "color_meter": previous_reading.color_meter,
                    "scan_meter": previous_reading.scan_meter,
                }
            else:
                previous_values = {
                    "total_meter": equipment.initial_total_meter,
                    "black_meter": equipment.initial_black_meter,
                    "color_meter": equipment.initial_color_meter,
                    "scan_meter": equipment.initial_scan_meter,
                }

            current_values = {
                "total_meter": total_meter,
                "black_meter": black_meter,
                "color_meter": color_meter,
                "scan_meter": scan_meter,
            }

            if reading_type != MeterReading.ReadingType.RESET:
                error_messages = {
                    "total_meter": (
                        "El contador total no puede ser menor "
                        "que la lectura anterior."
                    ),
                    "black_meter": (
                        "El contador B/N no puede ser menor "
                        "que la lectura anterior."
                    ),
                    "color_meter": (
                        "El contador color no puede ser menor "
                        "que la lectura anterior."
                    ),
                    "scan_meter": (
                        "El contador de escaneo no puede ser menor "
                        "que la lectura anterior."
                    ),
                }

                for field_name, current_value in current_values.items():
                    previous_value = previous_values.get(
                        field_name
                    )

                    if (
                        current_value is not None
                        and previous_value is not None
                        and current_value < previous_value
                    ):
                        raise serializers.ValidationError(
                            {
                                field_name: (
                                    error_messages[field_name]
                                )
                            }
                        )

            if (
                source == MeterReading.Source.SNMP
                and not values.get("ip_address")
                and not equipment.ip_address
            ):
                raise serializers.ValidationError(
                    {
                        "ip_address": (
                            "Una lectura SNMP debe registrar "
                            "la dirección IP consultada o el equipo "
                            "debe tener una IP configurada."
                        )
                    }
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """
        Crea la lectura registrando auditoría.

        El usuario autenticado se utiliza como responsable
        cuando no fue enviado explícitamente.
        """

        actor = get_authenticated_user(
            self
        )

        if (
            not validated_data.get(
                "registered_by"
            )
            and actor
        ):
            validated_data[
                "registered_by"
            ] = actor

        reading = MeterReading(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            reading.full_clean()
            reading.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return reading

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        """
        Actualiza la lectura registrando auditoría.

        Una lectura que ya fue aplicada al equipo no debe
        modificarse desde este serializer.
        """

        if instance.is_applied_to_equipment:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "No puedes modificar una lectura que ya "
                        "fue aplicada a los contadores del equipo."
                    )
                }
            )

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


class VerifyMeterReadingSerializer(
    serializers.Serializer
):
    """
    Datos para verificar una lectura.
    """

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=3000,
    )


class ApplyMeterReadingSerializer(
    serializers.Serializer
):
    """
    Confirmación para aplicar una lectura a la ficha del equipo.
    """

    confirm = serializers.BooleanField(
        required=True,
    )

    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError(
                "Debes confirmar la aplicación de la lectura."
            )

        return value


class ArchiveMeterReadingSerializer(
    serializers.Serializer
):
    """
    Datos requeridos para archivar una lectura.
    """

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )