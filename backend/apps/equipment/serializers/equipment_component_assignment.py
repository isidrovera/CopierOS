# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from ..models import EquipmentComponentAssignment
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class EquipmentComponentAssignmentListSerializer(
    serializers.ModelSerializer
):
    equipment_serial = serializers.CharField(
        source="equipment.serial_number",
        read_only=True,
    )

    equipment_model_name = serializers.CharField(
        source="equipment.equipment_model.name",
        read_only=True,
    )

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

    component_color = serializers.CharField(
        source="inventory.component.color",
        read_only=True,
    )

    component_color_name = serializers.CharField(
        source="inventory.component.get_color_display",
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    removed_disposition_name = serializers.CharField(
        source="get_removed_disposition_display",
        read_only=True,
    )

    class Meta:
        model = EquipmentComponentAssignment

        fields = (
            "id",
            "equipment",
            "equipment_serial",
            "equipment_model_name",
            "inventory",
            "inventory_code",
            "component_name",
            "component_code",
            "component_color",
            "component_color_name",
            "quantity",
            "status",
            "status_name",
            "position",
            "installed_at",
            "installation_meter",
            "removed_at",
            "removal_meter",
            "removed_disposition",
            "removed_disposition_name",
            "reference_type",
            "reference_id",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class EquipmentComponentAssignmentDetailSerializer(
    serializers.ModelSerializer
):
    equipment_serial = serializers.CharField(
        source="equipment.serial_number",
        read_only=True,
    )

    equipment_model_name = serializers.CharField(
        source="equipment.equipment_model.name",
        read_only=True,
    )

    inventory_code = serializers.CharField(
        source="inventory.internal_code",
        read_only=True,
    )

    inventory_serial = serializers.CharField(
        source="inventory.serial_number",
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

    component_type_name = serializers.CharField(
        source="inventory.component.component_type.name",
        read_only=True,
    )

    component_color = serializers.CharField(
        source="inventory.component.color",
        read_only=True,
    )

    component_color_name = serializers.CharField(
        source="inventory.component.get_color_display",
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    removed_disposition_name = serializers.CharField(
        source="get_removed_disposition_display",
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
        model = EquipmentComponentAssignment

        fields = (
            "id",
            "equipment",
            "equipment_serial",
            "equipment_model_name",
            "inventory",
            "inventory_code",
            "inventory_serial",
            "component_name",
            "component_code",
            "component_type_name",
            "component_color",
            "component_color_name",
            "quantity",
            "status",
            "status_name",
            "position",
            "installed_at",
            "installation_meter",
            "removed_at",
            "removal_meter",
            "removed_disposition",
            "removed_disposition_name",
            "reference_type",
            "reference_id",
            "installation_notes",
            "removal_notes",
            "is_active",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class EquipmentComponentAssignmentCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = EquipmentComponentAssignment

        fields = (
            "equipment",
            "inventory",
            "quantity",
            "status",
            "position",
            "installed_at",
            "installation_meter",
            "removed_at",
            "removal_meter",
            "removed_disposition",
            "reference_type",
            "reference_id",
            "installation_notes",
            "removal_notes",
            "is_active",
        )

    def validate_position(self, value):
        return str(
            value or ""
        ).strip().lower()

    def validate_reference_type(self, value):
        return str(
            value or ""
        ).strip().lower()

    def validate_installation_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate_removal_notes(self, value):
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

    def validate_equipment(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un equipo archivado."
            )

        return value

    def validate(self, attrs):
        instance = self.instance

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
                None,
            ),
        )

        status = attrs.get(
            "status",
            getattr(
                instance,
                "status",
                EquipmentComponentAssignment.Status.RESERVED,
            ),
        )

        installed_at = attrs.get(
            "installed_at",
            getattr(
                instance,
                "installed_at",
                None,
            ),
        )

        installation_meter = attrs.get(
            "installation_meter",
            getattr(
                instance,
                "installation_meter",
                None,
            ),
        )

        removed_at = attrs.get(
            "removed_at",
            getattr(
                instance,
                "removed_at",
                None,
            ),
        )

        removal_meter = attrs.get(
            "removal_meter",
            getattr(
                instance,
                "removal_meter",
                None,
            ),
        )

        removed_disposition = attrs.get(
            "removed_disposition",
            getattr(
                instance,
                "removed_disposition",
                EquipmentComponentAssignment.RemovedDisposition.NOT_APPLICABLE,
            ),
        )

        reference_type = str(
            attrs.get(
                "reference_type",
                getattr(
                    instance,
                    "reference_type",
                    "",
                ),
            ) or ""
        ).strip()

        reference_id = attrs.get(
            "reference_id",
            getattr(
                instance,
                "reference_id",
                None,
            ),
        )

        if not inventory:
            raise serializers.ValidationError(
                {
                    "inventory": (
                        "Debes seleccionar un componente "
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

        if quantity > inventory.available_quantity:
            if not instance or inventory.pk != instance.inventory_id:
                raise serializers.ValidationError(
                    {
                        "quantity": (
                            "La cantidad supera las existencias "
                            "disponibles."
                        )
                    }
                )

        if inventory.serial_number and quantity != 1:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "Un componente con serie debe asignarse "
                        "con cantidad igual a uno."
                    )
                }
            )

        if (
            status
            == EquipmentComponentAssignment.Status.INSTALLED
            and not installed_at
        ):
            attrs["installed_at"] = timezone.now()

        if (
            status
            in (
                EquipmentComponentAssignment.Status.REMOVED,
                EquipmentComponentAssignment.Status.RETURNED,
                EquipmentComponentAssignment.Status.DISCARDED,
            )
            and not removed_at
        ):
            attrs["removed_at"] = timezone.now()
            removed_at = attrs["removed_at"]

        if (
            installed_at
            and removed_at
            and removed_at < installed_at
        ):
            raise serializers.ValidationError(
                {
                    "removed_at": (
                        "La fecha de retiro no puede ser anterior "
                        "a la fecha de instalación."
                    )
                }
            )

        if (
            installation_meter is not None
            and removal_meter is not None
            and removal_meter < installation_meter
        ):
            raise serializers.ValidationError(
                {
                    "removal_meter": (
                        "El contador de retiro no puede ser menor "
                        "que el contador de instalación."
                    )
                }
            )

        if (
            removed_at
            and removed_disposition
            == EquipmentComponentAssignment.RemovedDisposition.NOT_APPLICABLE
        ):
            raise serializers.ValidationError(
                {
                    "removed_disposition": (
                        "Debes indicar el destino del "
                        "componente retirado."
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

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        assignment = EquipmentComponentAssignment(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            assignment.full_clean()
            assignment.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return assignment

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