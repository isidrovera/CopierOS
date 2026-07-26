# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.rentals.models import (
    RentalEquipment,
    RentalPreparation,
)


class RentalPreparationSerializer(serializers.ModelSerializer):
    """
    Serializer principal para preparaciones de equipos
    antes de su alquiler.
    """

    rental_equipment_display = (
        serializers.SerializerMethodField()
    )

    equipment_serial_number = (
        serializers.SerializerMethodField()
    )

    equipment_internal_code = (
        serializers.SerializerMethodField()
    )

    equipment_brand_name = serializers.SerializerMethodField()
    equipment_model_name = serializers.SerializerMethodField()

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    result_display = serializers.CharField(
        source="get_result_display",
        read_only=True,
    )

    assigned_technician_name = (
        serializers.SerializerMethodField()
    )

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    archived_by_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RentalPreparation
        fields = [
            "id",
            "code",
            "rental_equipment",
            "rental_equipment_display",
            "equipment_serial_number",
            "equipment_internal_code",
            "equipment_brand_name",
            "equipment_model_name",
            "status",
            "status_display",
            "result",
            "result_display",
            "assigned_technician",
            "assigned_technician_name",
            "requested_at",
            "scheduled_date",
            "started_at",
            "completed_at",
            "initial_meter",
            "final_meter",
            "request_reason",
            "technical_observations",
            "completion_notes",
            "cancellation_reason",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_at",
            "archived_by",
            "archived_by_name",
            "archived_reason",
            "is_archived",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        ]

    def get_rental_equipment_display(self, obj):
        return str(obj.rental_equipment)

    def get_equipment_serial_number(self, obj):
        equipment = getattr(
            obj.rental_equipment,
            "equipment",
            None,
        )

        return getattr(
            equipment,
            "serial_number",
            "",
        )

    def get_equipment_internal_code(self, obj):
        equipment = getattr(
            obj.rental_equipment,
            "equipment",
            None,
        )

        return getattr(
            equipment,
            "internal_code",
            "",
        )

    def get_equipment_brand_name(self, obj):
        equipment = getattr(
            obj.rental_equipment,
            "equipment",
            None,
        )

        equipment_model = getattr(
            equipment,
            "equipment_model",
            None,
        )

        brand = getattr(
            equipment_model,
            "brand",
            None,
        )

        return getattr(
            brand,
            "name",
            "",
        )

    def get_equipment_model_name(self, obj):
        equipment = getattr(
            obj.rental_equipment,
            "equipment",
            None,
        )

        equipment_model = getattr(
            equipment,
            "equipment_model",
            None,
        )

        return getattr(
            equipment_model,
            "name",
            "",
        )

    def get_assigned_technician_name(self, obj):
        if not obj.assigned_technician:
            return ""

        return (
            obj.assigned_technician.get_full_name()
            or obj.assigned_technician.username
        )

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return ""

        return (
            obj.created_by.get_full_name()
            or obj.created_by.username
        )

    def get_updated_by_name(self, obj):
        if not obj.updated_by:
            return ""

        return (
            obj.updated_by.get_full_name()
            or obj.updated_by.username
        )

    def get_archived_by_name(self, obj):
        if not obj.archived_by:
            return ""

        return (
            obj.archived_by.get_full_name()
            or obj.archived_by.username
        )

    def validate_code(self, value):
        code = str(
            value or ""
        ).strip().upper()

        if not code:
            raise serializers.ValidationError(
                "El código de preparación es obligatorio."
            )

        queryset = RentalPreparation.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una preparación con este código."
            )

        return code

    def validate_rental_equipment(self, value):
        if value.archived_at:
            raise serializers.ValidationError(
                "El equipo seleccionado está archivado."
            )

        if (
            value.purpose
            != RentalEquipment.EquipmentPurpose.RENTAL
        ):
            raise serializers.ValidationError(
                "Solo los equipos de alquiler pueden prepararse."
            )

        invalid_statuses = [
            RentalEquipment.OperationalStatus.RESERVED,
            RentalEquipment.OperationalStatus.ASSIGNED,
            (
                RentalEquipment
                .OperationalStatus
                .INSTALLATION_PENDING
            ),
            RentalEquipment.OperationalStatus.INSTALLED,
            RentalEquipment.OperationalStatus.RENTED,
            (
                RentalEquipment
                .OperationalStatus
                .REMOVAL_PENDING
            ),
            RentalEquipment.OperationalStatus.REMOVED,
            RentalEquipment.OperationalStatus.OUT_OF_SERVICE,
            RentalEquipment.OperationalStatus.FOR_PARTS,
        ]

        if value.operational_status in invalid_statuses:
            raise serializers.ValidationError(
                "El estado actual del equipo no permite "
                "crear una preparación."
            )

        active_preparation = RentalPreparation.objects.filter(
            rental_equipment=value,
            status__in=[
                RentalPreparation.Status.PENDING,
                RentalPreparation.Status.IN_PROGRESS,
                RentalPreparation.Status.WAITING_PARTS,
                RentalPreparation.Status.OBSERVED,
            ],
            archived_at__isnull=True,
        )

        if self.instance:
            active_preparation = active_preparation.exclude(
                pk=self.instance.pk,
            )

        if active_preparation.exists():
            raise serializers.ValidationError(
                "El equipo ya tiene una preparación activa."
            )

        return value

    def validate_assigned_technician(self, value):
        if not value:
            return value

        if not value.is_active:
            raise serializers.ValidationError(
                "El técnico seleccionado está inactivo."
            )

        return value

    def validate(self, attrs):
        instance = self.instance

        status = attrs.get(
            "status",
            getattr(
                instance,
                "status",
                RentalPreparation.Status.DRAFT,
            ),
        )

        result = attrs.get(
            "result",
            getattr(
                instance,
                "result",
                RentalPreparation.Result.PENDING,
            ),
        )

        assigned_technician = attrs.get(
            "assigned_technician",
            getattr(
                instance,
                "assigned_technician",
                None,
            ),
        )

        initial_meter = attrs.get(
            "initial_meter",
            getattr(
                instance,
                "initial_meter",
                None,
            ),
        )

        final_meter = attrs.get(
            "final_meter",
            getattr(
                instance,
                "final_meter",
                None,
            ),
        )

        cancellation_reason = str(
            attrs.get(
                "cancellation_reason",
                getattr(
                    instance,
                    "cancellation_reason",
                    "",
                ),
            )
            or ""
        ).strip()

        if (
            initial_meter is not None
            and final_meter is not None
            and final_meter < initial_meter
        ):
            raise serializers.ValidationError(
                {
                    "final_meter": (
                        "El contador final no puede ser menor "
                        "que el contador inicial."
                    ),
                }
            )

        if (
            status
            == RentalPreparation.Status.IN_PROGRESS
            and not assigned_technician
        ):
            raise serializers.ValidationError(
                {
                    "assigned_technician": (
                        "Debe asignar un técnico antes "
                        "de iniciar la preparación."
                    ),
                }
            )

        if status == RentalPreparation.Status.COMPLETED:
            if result == RentalPreparation.Result.PENDING:
                raise serializers.ValidationError(
                    {
                        "result": (
                            "Debe indicar el resultado "
                            "de la preparación."
                        ),
                    }
                )

            if not assigned_technician:
                raise serializers.ValidationError(
                    {
                        "assigned_technician": (
                            "La preparación debe tener "
                            "un técnico asignado."
                        ),
                    }
                )

        if (
            status
            == RentalPreparation.Status.CANCELLED
            and not cancellation_reason
        ):
            raise serializers.ValidationError(
                {
                    "cancellation_reason": (
                        "Debe indicar el motivo de cancelación."
                    ),
                }
            )

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")

        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        preparation = super().create(
            validated_data
        )

        rental_equipment = preparation.rental_equipment

        if preparation.status in [
            RentalPreparation.Status.PENDING,
            RentalPreparation.Status.DRAFT,
        ]:
            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .PENDING_PREPARATION
            )

        elif (
            preparation.status
            == RentalPreparation.Status.IN_PROGRESS
        ):
            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .IN_PREPARATION
            )

        rental_equipment.is_available_for_rental = False
        rental_equipment.updated_by = user

        rental_equipment.save(
            update_fields=[
                "operational_status",
                "is_available_for_rental",
                "updated_by",
                "updated_at",
            ]
        )

        return preparation

    def update(self, instance, validated_data):
        request = self.context.get("request")

        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["updated_by"] = user

        preparation = super().update(
            instance,
            validated_data,
        )

        rental_equipment = preparation.rental_equipment

        if (
            preparation.status
            == RentalPreparation.Status.IN_PROGRESS
        ):
            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .IN_PREPARATION
            )
            rental_equipment.is_available_for_rental = False

        elif (
            preparation.status
            == RentalPreparation.Status.WAITING_PARTS
        ):
            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .WITH_PROBLEMS
            )
            rental_equipment.is_available_for_rental = False

        elif (
            preparation.status
            == RentalPreparation.Status.OBSERVED
        ):
            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .WITH_PROBLEMS
            )
            rental_equipment.is_available_for_rental = False

        elif (
            preparation.status
            == RentalPreparation.Status.COMPLETED
        ):
            if (
                preparation.result
                == RentalPreparation
                .Result
                .READY_FOR_RENTAL
            ):
                rental_equipment.operational_status = (
                    RentalEquipment
                    .OperationalStatus
                    .READY_FOR_RENTAL
                )
                rental_equipment.is_available_for_rental = True

            elif (
                preparation.result
                == RentalPreparation.Result.FOR_PARTS
            ):
                rental_equipment.operational_status = (
                    RentalEquipment
                    .OperationalStatus
                    .FOR_PARTS
                )
                rental_equipment.is_available_for_rental = False

            else:
                rental_equipment.operational_status = (
                    RentalEquipment
                    .OperationalStatus
                    .WITH_PROBLEMS
                )
                rental_equipment.is_available_for_rental = False

        elif (
            preparation.status
            == RentalPreparation.Status.CANCELLED
        ):
            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .IN_WAREHOUSE
            )
            rental_equipment.is_available_for_rental = False

        rental_equipment.updated_by = user

        rental_equipment.save(
            update_fields=[
                "operational_status",
                "is_available_for_rental",
                "updated_by",
                "updated_at",
            ]
        )

        return preparation


class RentalPreparationListSerializer(
    RentalPreparationSerializer
):
    """
    Serializer compacto para listar preparaciones.
    """

    class Meta(RentalPreparationSerializer.Meta):
        fields = [
            "id",
            "code",
            "rental_equipment",
            "rental_equipment_display",
            "equipment_serial_number",
            "equipment_internal_code",
            "equipment_brand_name",
            "equipment_model_name",
            "status",
            "status_display",
            "result",
            "result_display",
            "assigned_technician",
            "assigned_technician_name",
            "requested_at",
            "scheduled_date",
            "started_at",
            "completed_at",
            "initial_meter",
            "final_meter",
            "archived_at",
            "is_archived",
        ]