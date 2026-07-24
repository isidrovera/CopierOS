# -*- coding: utf-8 -*-
from decimal import Decimal

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.equipment.models import (
    ComponentInventory,
    EquipmentComponent,
)

from ..models import RepairComponent
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class RepairComponentListSerializer(
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

    component_name = serializers.CharField(
        source="component.name",
        read_only=True,
    )

    component_code = serializers.CharField(
        source="component.code",
        read_only=True,
    )

    component_color = serializers.CharField(
        source="component.color",
        read_only=True,
    )

    component_color_name = serializers.CharField(
        source="component.get_color_display",
        read_only=True,
    )

    inventory_internal_code = serializers.CharField(
        source="inventory.internal_code",
        read_only=True,
        allow_null=True,
    )

    inventory_serial_number = serializers.CharField(
        source="inventory.serial_number",
        read_only=True,
        allow_null=True,
    )

    movement_type_name = serializers.CharField(
        source="get_movement_type_display",
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    removed_component_name = serializers.CharField(
        source="removed_component.name",
        read_only=True,
        allow_null=True,
    )

    removed_part_disposition_name = serializers.CharField(
        source="get_removed_part_disposition_display",
        read_only=True,
    )

    total_cost = serializers.DecimalField(
        max_digits=16,
        decimal_places=2,
        read_only=True,
        allow_null=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairComponent

        fields = (
            "id",
            "repair",
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "component",
            "component_name",
            "component_code",
            "component_color",
            "component_color_name",
            "inventory",
            "inventory_internal_code",
            "inventory_serial_number",
            "movement_type",
            "movement_type_name",
            "status",
            "status_name",
            "quantity",
            "reserved_quantity",
            "delivered_quantity",
            "installed_quantity",
            "returned_quantity",
            "consumed_quantity",
            "removed_component",
            "removed_component_name",
            "removed_serial_number",
            "removed_part_disposition",
            "removed_part_disposition_name",
            "unit_cost",
            "total_cost",
            "requested_at",
            "reserved_at",
            "delivered_at",
            "installed_at",
            "removed_at",
            "returned_at",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class RepairComponentDetailSerializer(
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

    component_name = serializers.CharField(
        source="component.name",
        read_only=True,
    )

    component_code = serializers.CharField(
        source="component.code",
        read_only=True,
    )

    component_type_name = serializers.CharField(
        source="component.component_type.name",
        read_only=True,
    )

    component_color_name = serializers.CharField(
        source="component.get_color_display",
        read_only=True,
    )

    inventory_internal_code = serializers.CharField(
        source="inventory.internal_code",
        read_only=True,
        allow_null=True,
    )

    inventory_serial_number = serializers.CharField(
        source="inventory.serial_number",
        read_only=True,
        allow_null=True,
    )

    inventory_available_quantity = serializers.DecimalField(
        source="inventory.available_quantity",
        max_digits=12,
        decimal_places=2,
        read_only=True,
        allow_null=True,
    )

    removed_component_name = serializers.CharField(
        source="removed_component.name",
        read_only=True,
        allow_null=True,
    )

    removed_component_code = serializers.CharField(
        source="removed_component.code",
        read_only=True,
        allow_null=True,
    )

    removed_inventory_internal_code = serializers.CharField(
        source="removed_inventory.internal_code",
        read_only=True,
        allow_null=True,
    )

    movement_type_name = serializers.CharField(
        source="get_movement_type_display",
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    removed_part_disposition_name = serializers.CharField(
        source="get_removed_part_disposition_display",
        read_only=True,
    )

    requested_by_name = serializers.CharField(
        source="requested_by.full_name",
        read_only=True,
        allow_null=True,
    )

    reserved_by_name = serializers.CharField(
        source="reserved_by.full_name",
        read_only=True,
        allow_null=True,
    )

    delivered_by_name = serializers.CharField(
        source="delivered_by.full_name",
        read_only=True,
        allow_null=True,
    )

    installed_by_name = serializers.CharField(
        source="installed_by.full_name",
        read_only=True,
        allow_null=True,
    )

    removed_by_name = serializers.CharField(
        source="removed_by.full_name",
        read_only=True,
        allow_null=True,
    )

    returned_by_name = serializers.CharField(
        source="returned_by.full_name",
        read_only=True,
        allow_null=True,
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

    total_cost = serializers.DecimalField(
        max_digits=16,
        decimal_places=2,
        read_only=True,
        allow_null=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairComponent

        fields = (
            "id",
            "repair",
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "component",
            "component_name",
            "component_code",
            "component_type_name",
            "component_color_name",
            "inventory",
            "inventory_internal_code",
            "inventory_serial_number",
            "inventory_available_quantity",
            "movement_type",
            "movement_type_name",
            "status",
            "status_name",
            "quantity",
            "reserved_quantity",
            "delivered_quantity",
            "installed_quantity",
            "returned_quantity",
            "consumed_quantity",
            "removed_component",
            "removed_component_name",
            "removed_component_code",
            "removed_inventory",
            "removed_inventory_internal_code",
            "removed_serial_number",
            "removed_part_disposition",
            "removed_part_disposition_name",
            "requested_by",
            "requested_by_name",
            "requested_at",
            "reserved_by",
            "reserved_by_name",
            "reserved_at",
            "delivered_by",
            "delivered_by_name",
            "delivered_at",
            "installed_by",
            "installed_by_name",
            "installed_at",
            "removed_by",
            "removed_by_name",
            "removed_at",
            "returned_by",
            "returned_by_name",
            "returned_at",
            "unit_cost",
            "total_cost",
            "notes",
            "removed_part_notes",
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

        read_only_fields = fields


class RepairComponentCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = RepairComponent

        fields = (
            "repair",
            "component",
            "inventory",
            "quantity",
            "removed_component",
            "removed_inventory",
            "removed_serial_number",
            "removed_part_disposition",
            "unit_cost",
            "notes",
            "removed_part_notes",
        )

    def validate_repair(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes registrar componentes en una reparación archivada."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes registrar componentes en una reparación inactiva."
            )

        return value

    def validate_component(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "El componente seleccionado está archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "El componente seleccionado está inactivo."
            )

        return value

    def validate_inventory(self, value):
        if value is None:
            return value

        if value.archived_at is not None:
            raise serializers.ValidationError(
                "El registro de inventario está archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "El registro de inventario está inactivo."
            )

        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "La cantidad debe ser mayor que cero."
            )

        return value

    def validate_removed_serial_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate_removed_part_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate(self, attrs):
        instance = self.instance

        component = attrs.get(
            "component",
            getattr(
                instance,
                "component",
                None,
            ),
        )

        inventory = attrs.get(
            "inventory",
            getattr(
                instance,
                "inventory",
                None,
            ),
        )

        quantity = attrs.get(
            "quantity",
            getattr(
                instance,
                "quantity",
                Decimal("1.00"),
            ),
        )

        removed_component = attrs.get(
            "removed_component",
            getattr(
                instance,
                "removed_component",
                None,
            ),
        )

        removed_inventory = attrs.get(
            "removed_inventory",
            getattr(
                instance,
                "removed_inventory",
                None,
            ),
        )

        removed_part_disposition = attrs.get(
            "removed_part_disposition",
            getattr(
                instance,
                "removed_part_disposition",
                RepairComponent.RemovedPartDisposition.NOT_APPLICABLE,
            ),
        )

        if not component:
            raise serializers.ValidationError(
                {
                    "component": (
                        "Debes seleccionar un componente."
                    )
                }
            )

        if inventory:
            if inventory.component_id != component.id:
                raise serializers.ValidationError(
                    {
                        "inventory": (
                            "El inventario no corresponde "
                            "al componente seleccionado."
                        )
                    }
                )

            if inventory.available_quantity < quantity:
                raise serializers.ValidationError(
                    {
                        "quantity": (
                            "La cantidad solicitada supera "
                            "la existencia disponible."
                        )
                    }
                )

        if (
            component.requires_individual_serial
            and quantity != Decimal("1")
        ):
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "Los componentes serializados deben "
                        "registrarse con cantidad igual a uno."
                    )
                }
            )

        if removed_inventory and removed_component:
            if (
                removed_inventory.component_id
                != removed_component.id
            ):
                raise serializers.ValidationError(
                    {
                        "removed_inventory": (
                            "El inventario retirado no corresponde "
                            "al componente retirado."
                        )
                    }
                )

        if (
            removed_part_disposition
            != RepairComponent.RemovedPartDisposition.NOT_APPLICABLE
            and not removed_component
        ):
            raise serializers.ValidationError(
                {
                    "removed_component": (
                        "Debes indicar el componente retirado."
                    )
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        repair_component = RepairComponent(
            movement_type=RepairComponent.MovementType.REQUIRED,
            status=RepairComponent.Status.PENDING,
            requested_by=actor,
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            repair_component.full_clean()
            repair_component.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return repair_component

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        actor = get_authenticated_user(
            self
        )

        if instance.status not in (
            RepairComponent.Status.PENDING,
            RepairComponent.Status.REQUESTED,
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "Solo pueden modificarse componentes "
                        "pendientes o solicitados."
                    )
                }
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


class RequestRepairComponentSerializer(
    serializers.Serializer
):
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate(self, attrs):
        repair_component = self.context.get(
            "repair_component"
        )

        if not repair_component:
            raise serializers.ValidationError(
                "No se encontró el componente de reparación."
            )

        if repair_component.is_archived:
            raise serializers.ValidationError(
                "El componente de reparación está archivado."
            )

        if repair_component.status != RepairComponent.Status.PENDING:
            raise serializers.ValidationError(
                {
                    "status": (
                        "Solo un componente pendiente puede solicitarse."
                    )
                }
            )

        return attrs


class ReserveRepairComponentSerializer(
    serializers.Serializer
):
    inventory = serializers.PrimaryKeyRelatedField(
        queryset=ComponentInventory.objects.filter(
            archived_at__isnull=True,
            is_active=True,
        ),
    )

    quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate(self, attrs):
        repair_component = self.context.get(
            "repair_component"
        )

        if not repair_component:
            raise serializers.ValidationError(
                "No se encontró el componente de reparación."
            )

        if repair_component.is_archived:
            raise serializers.ValidationError(
                "El componente de reparación está archivado."
            )

        if repair_component.status not in (
            RepairComponent.Status.PENDING,
            RepairComponent.Status.REQUESTED,
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "El componente no puede reservarse "
                        "desde su estado actual."
                    )
                }
            )

        inventory = attrs["inventory"]
        quantity = attrs["quantity"]

        if (
            inventory.component_id
            != repair_component.component_id
        ):
            raise serializers.ValidationError(
                {
                    "inventory": (
                        "El inventario no corresponde al componente."
                    )
                }
            )

        if quantity > repair_component.quantity:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "La cantidad reservada no puede superar "
                        "la cantidad solicitada."
                    )
                }
            )

        if inventory.available_quantity < quantity:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "No existe suficiente cantidad disponible."
                    )
                }
            )

        if (
            repair_component.component.requires_individual_serial
            and quantity != Decimal("1")
        ):
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "Un componente serializado debe reservarse "
                        "con cantidad igual a uno."
                    )
                }
            )

        return attrs


class DeliverRepairComponentSerializer(
    serializers.Serializer
):
    quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate(self, attrs):
        repair_component = self.context.get(
            "repair_component"
        )

        if not repair_component:
            raise serializers.ValidationError(
                "No se encontró el componente de reparación."
            )

        if repair_component.status != RepairComponent.Status.RESERVED:
            raise serializers.ValidationError(
                {
                    "status": (
                        "Solo un componente reservado puede entregarse."
                    )
                }
            )

        quantity = attrs["quantity"]

        if quantity > repair_component.reserved_quantity:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "La cantidad entregada no puede superar "
                        "la cantidad reservada."
                    )
                }
            )

        return attrs


class InstallRepairComponentSerializer(
    serializers.Serializer
):
    quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    removed_component = serializers.PrimaryKeyRelatedField(
        queryset=EquipmentComponent.objects.filter(
            archived_at__isnull=True,
            is_active=True,
        ),
        required=False,
        allow_null=True,
    )

    removed_inventory = serializers.PrimaryKeyRelatedField(
        queryset=ComponentInventory.objects.filter(
            archived_at__isnull=True,
            is_active=True,
        ),
        required=False,
        allow_null=True,
    )

    removed_serial_number = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
    )

    removed_part_disposition = serializers.ChoiceField(
        choices=RepairComponent.RemovedPartDisposition.choices,
        required=False,
    )

    removed_part_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate(self, attrs):
        repair_component = self.context.get(
            "repair_component"
        )

        if not repair_component:
            raise serializers.ValidationError(
                "No se encontró el componente de reparación."
            )

        if repair_component.status not in (
            RepairComponent.Status.RESERVED,
            RepairComponent.Status.DELIVERED,
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "El componente debe estar reservado "
                        "o entregado antes de instalarse."
                    )
                }
            )

        quantity = attrs["quantity"]

        available_quantity = (
            repair_component.delivered_quantity
            or repair_component.reserved_quantity
        )

        if quantity > available_quantity:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "La cantidad instalada supera "
                        "la cantidad disponible."
                    )
                }
            )

        removed_component = attrs.get(
            "removed_component"
        )

        removed_inventory = attrs.get(
            "removed_inventory"
        )

        disposition = attrs.get(
            "removed_part_disposition",
            RepairComponent.RemovedPartDisposition.NOT_APPLICABLE,
        )

        if (
            repair_component.component
            .requires_removed_part_tracking
            and not removed_component
        ):
            raise serializers.ValidationError(
                {
                    "removed_component": (
                        "Debes registrar el componente retirado."
                    )
                }
            )

        if (
            removed_component
            and disposition
            == RepairComponent.RemovedPartDisposition.NOT_APPLICABLE
        ):
            raise serializers.ValidationError(
                {
                    "removed_part_disposition": (
                        "Debes indicar el destino de la pieza retirada."
                    )
                }
            )

        if removed_inventory and removed_component:
            if (
                removed_inventory.component_id
                != removed_component.id
            ):
                raise serializers.ValidationError(
                    {
                        "removed_inventory": (
                            "El inventario retirado no corresponde "
                            "al componente retirado."
                        )
                    }
                )

        return attrs


class ReturnRepairComponentSerializer(
    serializers.Serializer
):
    quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate(self, attrs):
        repair_component = self.context.get(
            "repair_component"
        )

        if not repair_component:
            raise serializers.ValidationError(
                "No se encontró el componente de reparación."
            )

        if repair_component.status not in (
            RepairComponent.Status.RESERVED,
            RepairComponent.Status.DELIVERED,
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "El componente no puede retornarse "
                        "desde su estado actual."
                    )
                }
            )

        quantity = attrs["quantity"]

        returnable_quantity = (
            repair_component.delivered_quantity
            or repair_component.reserved_quantity
        )

        if quantity > returnable_quantity:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "La cantidad retornada supera "
                        "la cantidad disponible."
                    )
                }
            )

        return attrs


class ConsumeRepairComponentSerializer(
    serializers.Serializer
):
    quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    removed_component = serializers.PrimaryKeyRelatedField(
        queryset=EquipmentComponent.objects.filter(
            archived_at__isnull=True,
            is_active=True,
        ),
        required=False,
        allow_null=True,
    )

    removed_part_disposition = serializers.ChoiceField(
        choices=RepairComponent.RemovedPartDisposition.choices,
        required=False,
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate(self, attrs):
        repair_component = self.context.get(
            "repair_component"
        )

        if not repair_component:
            raise serializers.ValidationError(
                "No se encontró el componente de reparación."
            )

        if repair_component.status not in (
            RepairComponent.Status.RESERVED,
            RepairComponent.Status.DELIVERED,
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "El componente debe estar reservado "
                        "o entregado antes de consumirse."
                    )
                }
            )

        quantity = attrs["quantity"]

        available_quantity = (
            repair_component.delivered_quantity
            or repair_component.reserved_quantity
        )

        if quantity > available_quantity:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "La cantidad consumida supera "
                        "la cantidad disponible."
                    )
                }
            )

        if (
            repair_component.component
            .requires_removed_part_tracking
            and not attrs.get("removed_component")
        ):
            raise serializers.ValidationError(
                {
                    "removed_component": (
                        "Debes registrar la pieza retirada."
                    )
                }
            )

        return attrs


class CancelRepairComponentSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        max_length=5000,
    )

    def validate_reason(self, value):
        reason = str(
            value or ""
        ).strip()

        if not reason:
            raise serializers.ValidationError(
                "El motivo de cancelación es obligatorio."
            )

        return reason

    def validate(self, attrs):
        repair_component = self.context.get(
            "repair_component"
        )

        if not repair_component:
            raise serializers.ValidationError(
                "No se encontró el componente de reparación."
            )

        if repair_component.status in (
            RepairComponent.Status.INSTALLED,
            RepairComponent.Status.CONSUMED,
            RepairComponent.Status.RETURNED,
            RepairComponent.Status.DISCARDED,
            RepairComponent.Status.CANCELLED,
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "El componente ya no puede cancelarse."
                    )
                }
            )

        return attrs


class ArchiveRepairComponentSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )