# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.rentals.models import (
    RentalEquipment,
    RentalEquipmentMovement,
    RentalWarehouse,
)


class RentalEquipmentMovementSerializer(
    serializers.ModelSerializer
):
    """
    Serializer principal para movimientos de equipos
    dentro de la flota de ANDES.
    """

    rental_equipment_display = (
        serializers.SerializerMethodField()
    )

    equipment_serial_number = (
        serializers.SerializerMethodField()
    )

    equipment_model_name = serializers.SerializerMethodField()

    movement_type_display = serializers.CharField(
        source="get_movement_type_display",
        read_only=True,
    )

    previous_status_display = (
        serializers.SerializerMethodField()
    )

    new_status_display = serializers.SerializerMethodField()

    source_warehouse_name = (
        serializers.SerializerMethodField()
    )

    destination_warehouse_name = (
        serializers.SerializerMethodField()
    )

    reference_type_display = serializers.CharField(
        source="get_reference_type_display",
        read_only=True,
    )

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    archived_by_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RentalEquipmentMovement
        fields = [
            "id",
            "rental_equipment",
            "rental_equipment_display",
            "equipment_serial_number",
            "equipment_model_name",
            "movement_type",
            "movement_type_display",
            "previous_status",
            "previous_status_display",
            "new_status",
            "new_status_display",
            "source_warehouse",
            "source_warehouse_name",
            "destination_warehouse",
            "destination_warehouse_name",
            "source_location",
            "destination_location",
            "reference_type",
            "reference_type_display",
            "reference_id",
            "reference_number",
            "document_number",
            "reason",
            "notes",
            "occurred_at",
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

    def get_previous_status_display(self, obj):
        if not obj.previous_status:
            return ""

        return dict(
            RentalEquipment.OperationalStatus.choices
        ).get(
            obj.previous_status,
            obj.previous_status,
        )

    def get_new_status_display(self, obj):
        if not obj.new_status:
            return ""

        return dict(
            RentalEquipment.OperationalStatus.choices
        ).get(
            obj.new_status,
            obj.new_status,
        )

    def get_source_warehouse_name(self, obj):
        if not obj.source_warehouse:
            return ""

        return obj.source_warehouse.name

    def get_destination_warehouse_name(self, obj):
        if not obj.destination_warehouse:
            return ""

        return obj.destination_warehouse.name

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

    def validate_rental_equipment(self, value):
        if value.archived_at:
            raise serializers.ValidationError(
                "El equipo seleccionado está archivado."
            )

        return value

    def validate_source_warehouse(self, value):
        if not value:
            return value

        if value.archived_at:
            raise serializers.ValidationError(
                "El almacén de origen está archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "El almacén de origen está inactivo."
            )

        return value

    def validate_destination_warehouse(self, value):
        if not value:
            return value

        if value.archived_at:
            raise serializers.ValidationError(
                "El almacén de destino está archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "El almacén de destino está inactivo."
            )

        if not value.allows_entries:
            raise serializers.ValidationError(
                "El almacén de destino no permite ingresos."
            )

        return value

    def validate(self, attrs):
        instance = self.instance

        rental_equipment = attrs.get(
            "rental_equipment",
            getattr(
                instance,
                "rental_equipment",
                None,
            ),
        )

        movement_type = attrs.get(
            "movement_type",
            getattr(
                instance,
                "movement_type",
                None,
            ),
        )

        previous_status = attrs.get(
            "previous_status",
            getattr(
                instance,
                "previous_status",
                "",
            ),
        )

        new_status = attrs.get(
            "new_status",
            getattr(
                instance,
                "new_status",
                "",
            ),
        )

        source_warehouse = attrs.get(
            "source_warehouse",
            getattr(
                instance,
                "source_warehouse",
                None,
            ),
        )

        destination_warehouse = attrs.get(
            "destination_warehouse",
            getattr(
                instance,
                "destination_warehouse",
                None,
            ),
        )

        reference_type = attrs.get(
            "reference_type",
            getattr(
                instance,
                "reference_type",
                RentalEquipmentMovement.ReferenceType.MANUAL,
            ),
        )

        reference_id = attrs.get(
            "reference_id",
            getattr(
                instance,
                "reference_id",
                None,
            ),
        )

        reference_number = str(
            attrs.get(
                "reference_number",
                getattr(
                    instance,
                    "reference_number",
                    "",
                ),
            )
            or ""
        ).strip()

        if not rental_equipment:
            raise serializers.ValidationError(
                {
                    "rental_equipment": (
                        "El equipo de alquiler es obligatorio."
                    ),
                }
            )

        if not movement_type:
            raise serializers.ValidationError(
                {
                    "movement_type": (
                        "El tipo de movimiento es obligatorio."
                    ),
                }
            )

        if (
            previous_status
            and new_status
            and previous_status == new_status
            and movement_type
            not in [
                RentalEquipmentMovement.MovementType.LOCATION_CHANGE,
                RentalEquipmentMovement.MovementType.WAREHOUSE_TRANSFER,
                RentalEquipmentMovement.MovementType.OTHER,
            ]
        ):
            raise serializers.ValidationError(
                {
                    "new_status": (
                        "El estado nuevo debe ser diferente "
                        "al estado anterior."
                    ),
                }
            )

        if (
            movement_type
            == RentalEquipmentMovement.MovementType.WAREHOUSE_TRANSFER
        ):
            if not destination_warehouse:
                raise serializers.ValidationError(
                    {
                        "destination_warehouse": (
                            "Debe indicar el almacén de destino."
                        ),
                    }
                )

            if (
                source_warehouse
                and source_warehouse.pk
                == destination_warehouse.pk
            ):
                raise serializers.ValidationError(
                    {
                        "destination_warehouse": (
                            "El almacén de destino debe ser "
                            "diferente al almacén de origen."
                        ),
                    }
                )

        warehouse_entry_movements = [
            RentalEquipmentMovement.MovementType.INITIAL_ENTRY,
            RentalEquipmentMovement.MovementType.WAREHOUSE_ENTRY,
            (
                RentalEquipmentMovement
                .MovementType
                .RETURNED_TO_WAREHOUSE
            ),
        ]

        if (
            movement_type in warehouse_entry_movements
            and not destination_warehouse
        ):
            raise serializers.ValidationError(
                {
                    "destination_warehouse": (
                        "Debe indicar el almacén de destino."
                    ),
                }
            )

        if (
            reference_type
            != RentalEquipmentMovement.ReferenceType.MANUAL
            and not reference_id
            and not reference_number
        ):
            raise serializers.ValidationError(
                {
                    "reference_id": (
                        "Debe indicar el registro o número "
                        "del proceso relacionado."
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

        rental_equipment = validated_data[
            "rental_equipment"
        ]

        if not validated_data.get(
            "previous_status"
        ):
            validated_data["previous_status"] = (
                rental_equipment.operational_status
            )

        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        movement = super().create(
            validated_data
        )

        update_fields = []

        if movement.new_status:
            rental_equipment.operational_status = (
                movement.new_status
            )
            update_fields.append(
                "operational_status"
            )

        if movement.destination_warehouse_id:
            rental_equipment.warehouse = (
                movement.destination_warehouse
            )
            update_fields.append(
                "warehouse"
            )

        if movement.destination_location:
            rental_equipment.warehouse_location = (
                movement.destination_location
            )
            update_fields.append(
                "warehouse_location"
            )

        unavailable_statuses = [
            RentalEquipment.OperationalStatus.RENTED,
            RentalEquipment.OperationalStatus.REMOVAL_PENDING,
            RentalEquipment.OperationalStatus.WITH_PROBLEMS,
            RentalEquipment.OperationalStatus.FOR_PARTS,
            RentalEquipment.OperationalStatus.OUT_OF_SERVICE,
        ]

        if (
            rental_equipment.operational_status
            in unavailable_statuses
        ):
            rental_equipment.is_available_for_rental = False
            update_fields.append(
                "is_available_for_rental"
            )

        if (
            rental_equipment.operational_status
            == RentalEquipment
            .OperationalStatus
            .READY_FOR_RENTAL
        ):
            rental_equipment.is_available_for_rental = True
            update_fields.append(
                "is_available_for_rental"
            )

        if user:
            rental_equipment.updated_by = user
            update_fields.append(
                "updated_by"
            )

        if update_fields:
            update_fields.append(
                "updated_at"
            )

            rental_equipment.save(
                update_fields=list(
                    dict.fromkeys(
                        update_fields
                    )
                )
            )

        return movement

    def update(self, instance, validated_data):
        request = self.context.get("request")

        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["updated_by"] = user

        return super().update(
            instance,
            validated_data,
        )


class RentalEquipmentMovementListSerializer(
    RentalEquipmentMovementSerializer
):
    """
    Serializer compacto para el historial de movimientos.
    """

    class Meta(
        RentalEquipmentMovementSerializer.Meta
    ):
        fields = [
            "id",
            "rental_equipment",
            "rental_equipment_display",
            "equipment_serial_number",
            "equipment_model_name",
            "movement_type",
            "movement_type_display",
            "previous_status",
            "previous_status_display",
            "new_status",
            "new_status_display",
            "source_warehouse",
            "source_warehouse_name",
            "destination_warehouse",
            "destination_warehouse_name",
            "reference_type",
            "reference_type_display",
            "reference_number",
            "occurred_at",
            "created_by",
            "created_by_name",
            "archived_at",
            "is_archived",
        ]