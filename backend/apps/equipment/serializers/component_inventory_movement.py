# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from ..models import ComponentInventoryMovement
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class ComponentInventoryMovementListSerializer(
    serializers.ModelSerializer
):
    inventory_code = serializers.CharField(
        source="inventory.internal_code",
        read_only=True,
    )

    component_name = serializers.CharField(
        source="inventory.component.name",
        read_only=True,
    )

    component_code = serializers.CharField(
        source="inventory.component.code",
        read_only=True,
    )

    movement_type_name = serializers.CharField(
        source="get_movement_type_display",
        read_only=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.full_name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = ComponentInventoryMovement

        fields = (
            "id",
            "inventory",
            "inventory_code",
            "component_name",
            "component_code",
            "movement_type",
            "movement_type_name",
            "quantity",
            "quantity_before",
            "quantity_after",
            "reserved_before",
            "reserved_after",
            "source_warehouse",
            "destination_warehouse",
            "reference_type",
            "reference_id",
            "document_number",
            "meter_value",
            "occurred_at",
            "created_by",
            "created_by_name",
            "created_at",
        )

        read_only_fields = fields


class ComponentInventoryMovementDetailSerializer(
    serializers.ModelSerializer
):
    inventory_code = serializers.CharField(
        source="inventory.internal_code",
        read_only=True,
    )

    component_name = serializers.CharField(
        source="inventory.component.name",
        read_only=True,
    )

    component_code = serializers.CharField(
        source="inventory.component.code",
        read_only=True,
    )

    movement_type_name = serializers.CharField(
        source="get_movement_type_display",
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

    class Meta:
        model = ComponentInventoryMovement

        fields = (
            "id",
            "inventory",
            "inventory_code",
            "component_name",
            "component_code",
            "movement_type",
            "movement_type_name",
            "quantity",
            "quantity_before",
            "quantity_after",
            "reserved_before",
            "reserved_after",
            "source_warehouse",
            "source_location",
            "destination_warehouse",
            "destination_location",
            "reference_type",
            "reference_id",
            "document_number",
            "meter_value",
            "reason",
            "notes",
            "occurred_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class ComponentInventoryMovementCreateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = ComponentInventoryMovement

        fields = (
            "inventory",
            "movement_type",
            "quantity",
            "quantity_before",
            "quantity_after",
            "reserved_before",
            "reserved_after",
            "source_warehouse",
            "source_location",
            "destination_warehouse",
            "destination_location",
            "reference_type",
            "reference_id",
            "document_number",
            "meter_value",
            "reason",
            "notes",
            "occurred_at",
        )

        read_only_fields = (
            "quantity_before",
            "quantity_after",
            "reserved_before",
            "reserved_after",
        )

    def validate_source_warehouse(self, value):
        return str(
            value or ""
        ).strip()

    def validate_source_location(self, value):
        return str(
            value or ""
        ).strip()

    def validate_destination_warehouse(self, value):
        return str(
            value or ""
        ).strip()

    def validate_destination_location(self, value):
        return str(
            value or ""
        ).strip()

    def validate_reference_type(self, value):
        return str(
            value or ""
        ).strip().lower()

    def validate_document_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_reason(self, value):
        return str(
            value or ""
        ).strip()

    def validate_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate_inventory(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un inventario archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar un inventario inactivo."
            )

        return value

    def validate(self, attrs):
        inventory = attrs.get(
            "inventory"
        )

        movement_type = attrs.get(
            "movement_type"
        )

        quantity = attrs.get(
            "quantity"
        )

        reference_type = str(
            attrs.get(
                "reference_type",
                "",
            ) or ""
        ).strip()

        reference_id = attrs.get(
            "reference_id"
        )

        destination_warehouse = str(
            attrs.get(
                "destination_warehouse",
                "",
            ) or ""
        ).strip()

        if not inventory:
            raise serializers.ValidationError(
                {
                    "inventory": (
                        "Debes seleccionar un registro "
                        "de inventario."
                    )
                }
            )

        if quantity is None or quantity <= 0:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "La cantidad debe ser mayor que cero."
                    )
                }
            )

        if reference_id and not reference_type:
            raise serializers.ValidationError(
                {
                    "reference_type": (
                        "Debes indicar el tipo de referencia."
                    )
                }
            )

        if reference_type and not reference_id:
            raise serializers.ValidationError(
                {
                    "reference_id": (
                        "Debes indicar el ID de referencia."
                    )
                }
            )

        if (
            movement_type
            == ComponentInventoryMovement.MovementType.TRANSFER
            and not destination_warehouse
        ):
            raise serializers.ValidationError(
                {
                    "destination_warehouse": (
                        "Debes indicar el almacén de destino."
                    )
                }
            )

        available_quantity = (
            inventory.quantity
            - inventory.reserved_quantity
        )

        if movement_type in (
            ComponentInventoryMovement.MovementType.DELIVERY,
            ComponentInventoryMovement.MovementType.INSTALLATION,
            ComponentInventoryMovement.MovementType.ADJUSTMENT_OUT,
            ComponentInventoryMovement.MovementType.DISCARD,
        ):
            if quantity > available_quantity:
                raise serializers.ValidationError(
                    {
                        "quantity": (
                            "La cantidad supera las existencias "
                            "disponibles."
                        )
                    }
                )

        if (
            movement_type
            == ComponentInventoryMovement.MovementType.RESERVATION
            and quantity > available_quantity
        ):
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "La cantidad supera las existencias "
                        "disponibles para reservar."
                    )
                }
            )

        if (
            movement_type
            == ComponentInventoryMovement.MovementType.RESERVATION_RELEASE
            and quantity > inventory.reserved_quantity
        ):
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "La cantidad supera la reserva existente."
                    )
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        inventory = validated_data[
            "inventory"
        ]

        movement_type = validated_data[
            "movement_type"
        ]

        quantity = validated_data[
            "quantity"
        ]

        quantity_before = inventory.quantity
        reserved_before = inventory.reserved_quantity

        quantity_after = quantity_before
        reserved_after = reserved_before

        if movement_type in (
            ComponentInventoryMovement.MovementType.ENTRY,
            ComponentInventoryMovement.MovementType.RETURN,
            ComponentInventoryMovement.MovementType.ADJUSTMENT_IN,
        ):
            quantity_after = (
                quantity_before + quantity
            )

        elif movement_type in (
            ComponentInventoryMovement.MovementType.DELIVERY,
            ComponentInventoryMovement.MovementType.INSTALLATION,
            ComponentInventoryMovement.MovementType.ADJUSTMENT_OUT,
            ComponentInventoryMovement.MovementType.DISCARD,
        ):
            quantity_after = (
                quantity_before - quantity
            )

        elif (
            movement_type
            == ComponentInventoryMovement.MovementType.RESERVATION
        ):
            reserved_after = (
                reserved_before + quantity
            )

        elif (
            movement_type
            == ComponentInventoryMovement.MovementType.RESERVATION_RELEASE
        ):
            reserved_after = (
                reserved_before - quantity
            )

        movement = ComponentInventoryMovement(
            created_by=actor,
            updated_by=actor,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            reserved_before=reserved_before,
            reserved_after=reserved_after,
            occurred_at=validated_data.pop(
                "occurred_at",
                timezone.now(),
            ),
            **validated_data,
        )

        try:
            movement.full_clean()
            movement.save()

            inventory.quantity = quantity_after
            inventory.reserved_quantity = reserved_after

            if (
                inventory.available_quantity > 0
                and inventory.is_active
            ):
                inventory.status = (
                    inventory.Status.AVAILABLE
                )
            elif inventory.reserved_quantity > 0:
                inventory.status = (
                    inventory.Status.RESERVED
                )
            else:
                inventory.status = (
                    inventory.Status.NOT_AVAILABLE
                )

            if actor:
                inventory.updated_by = actor

            inventory.full_clean()
            inventory.save()

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return movement