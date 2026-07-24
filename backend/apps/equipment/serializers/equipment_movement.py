# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers

from ..models import (
    Equipment,
    EquipmentMovement,
)
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class EquipmentMovementListSerializer(
    serializers.ModelSerializer
):
    """
    Serializer reducido para listar movimientos de equipos.
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

    movement_type_name = serializers.CharField(
        source="get_movement_type_display",
        read_only=True,
    )

    reference_type_name = serializers.CharField(
        source="get_reference_type_display",
        read_only=True,
    )

    previous_technical_status_name = serializers.SerializerMethodField()

    new_technical_status_name = serializers.SerializerMethodField()

    previous_commercial_status_name = serializers.SerializerMethodField()

    new_commercial_status_name = serializers.SerializerMethodField()

    responsible_user_name = serializers.CharField(
        source="responsible_user.full_name",
        read_only=True,
        allow_null=True,
    )

    previous_customer_name = serializers.CharField(
        source="previous_customer.display_name",
        read_only=True,
        allow_null=True,
    )

    new_customer_name = serializers.CharField(
        source="new_customer.display_name",
        read_only=True,
        allow_null=True,
    )

    new_customer_branch_name = serializers.CharField(
        source="new_customer_branch.name",
        read_only=True,
        allow_null=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = EquipmentMovement

        fields = (
            "id",
            "equipment",
            "equipment_internal_code",
            "equipment_serial_number",
            "equipment_model_name",
            "equipment_brand_name",
            "movement_type",
            "movement_type_name",
            "occurred_at",
            "responsible_user",
            "responsible_user_name",
            "previous_technical_status",
            "previous_technical_status_name",
            "new_technical_status",
            "new_technical_status_name",
            "previous_commercial_status",
            "previous_commercial_status_name",
            "new_commercial_status",
            "new_commercial_status_name",
            "previous_location",
            "new_location",
            "previous_customer",
            "previous_customer_name",
            "new_customer",
            "new_customer_name",
            "new_customer_branch",
            "new_customer_branch_name",
            "reference_type",
            "reference_type_name",
            "reference_number",
            "document_number",
            "reason",
            "is_system_generated",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_previous_technical_status_name(self, obj):
        if not obj.previous_technical_status:
            return None

        return dict(
            Equipment.TechnicalStatus.choices
        ).get(
            obj.previous_technical_status
        )

    def get_new_technical_status_name(self, obj):
        if not obj.new_technical_status:
            return None

        return dict(
            Equipment.TechnicalStatus.choices
        ).get(
            obj.new_technical_status
        )

    def get_previous_commercial_status_name(self, obj):
        if not obj.previous_commercial_status:
            return None

        return dict(
            Equipment.CommercialStatus.choices
        ).get(
            obj.previous_commercial_status
        )

    def get_new_commercial_status_name(self, obj):
        if not obj.new_commercial_status:
            return None

        return dict(
            Equipment.CommercialStatus.choices
        ).get(
            obj.new_commercial_status
        )


class EquipmentMovementDetailSerializer(
    serializers.ModelSerializer
):
    """
    Serializer completo de un movimiento de equipo.
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

    movement_type_name = serializers.CharField(
        source="get_movement_type_display",
        read_only=True,
    )

    reference_type_name = serializers.CharField(
        source="get_reference_type_display",
        read_only=True,
    )

    previous_technical_status_name = serializers.SerializerMethodField()

    new_technical_status_name = serializers.SerializerMethodField()

    previous_commercial_status_name = serializers.SerializerMethodField()

    new_commercial_status_name = serializers.SerializerMethodField()

    responsible_user_name = serializers.CharField(
        source="responsible_user.full_name",
        read_only=True,
        allow_null=True,
    )

    previous_customer_name = serializers.CharField(
        source="previous_customer.display_name",
        read_only=True,
        allow_null=True,
    )

    new_customer_name = serializers.CharField(
        source="new_customer.display_name",
        read_only=True,
        allow_null=True,
    )

    previous_customer_branch_name = serializers.CharField(
        source="previous_customer_branch.name",
        read_only=True,
        allow_null=True,
    )

    new_customer_branch_name = serializers.CharField(
        source="new_customer_branch.name",
        read_only=True,
        allow_null=True,
    )

    previous_owner_name = serializers.CharField(
        source="previous_owner.display_name",
        read_only=True,
        allow_null=True,
    )

    new_owner_name = serializers.CharField(
        source="new_owner.display_name",
        read_only=True,
        allow_null=True,
    )

    previous_advisor_name = serializers.CharField(
        source="previous_advisor.full_name",
        read_only=True,
        allow_null=True,
    )

    new_advisor_name = serializers.CharField(
        source="new_advisor.full_name",
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
        model = EquipmentMovement

        fields = (
            "id",
            "equipment",
            "equipment_internal_code",
            "equipment_serial_number",
            "equipment_model_name",
            "equipment_brand_name",
            "movement_type",
            "movement_type_name",
            "occurred_at",
            "responsible_user",
            "responsible_user_name",
            "previous_technical_status",
            "previous_technical_status_name",
            "new_technical_status",
            "new_technical_status_name",
            "previous_commercial_status",
            "previous_commercial_status_name",
            "new_commercial_status",
            "new_commercial_status_name",
            "previous_location",
            "new_location",
            "previous_position_reference",
            "new_position_reference",
            "previous_customer",
            "previous_customer_name",
            "new_customer",
            "new_customer_name",
            "previous_customer_branch",
            "previous_customer_branch_name",
            "new_customer_branch",
            "new_customer_branch_name",
            "previous_owner",
            "previous_owner_name",
            "new_owner",
            "new_owner_name",
            "previous_advisor",
            "previous_advisor_name",
            "new_advisor",
            "new_advisor_name",
            "reference_type",
            "reference_type_name",
            "reference_id",
            "reference_number",
            "document_number",
            "total_meter",
            "black_meter",
            "color_meter",
            "scan_meter",
            "reason",
            "notes",
            "is_system_generated",
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
            "equipment_brand_name",
            "movement_type_name",
            "reference_type_name",
            "previous_technical_status_name",
            "new_technical_status_name",
            "previous_commercial_status_name",
            "new_commercial_status_name",
            "responsible_user_name",
            "previous_customer_name",
            "new_customer_name",
            "previous_customer_branch_name",
            "new_customer_branch_name",
            "previous_owner_name",
            "new_owner_name",
            "previous_advisor_name",
            "new_advisor_name",
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

    def get_previous_technical_status_name(self, obj):
        if not obj.previous_technical_status:
            return None

        return dict(
            Equipment.TechnicalStatus.choices
        ).get(
            obj.previous_technical_status
        )

    def get_new_technical_status_name(self, obj):
        if not obj.new_technical_status:
            return None

        return dict(
            Equipment.TechnicalStatus.choices
        ).get(
            obj.new_technical_status
        )

    def get_previous_commercial_status_name(self, obj):
        if not obj.previous_commercial_status:
            return None

        return dict(
            Equipment.CommercialStatus.choices
        ).get(
            obj.previous_commercial_status
        )

    def get_new_commercial_status_name(self, obj):
        if not obj.new_commercial_status:
            return None

        return dict(
            Equipment.CommercialStatus.choices
        ).get(
            obj.new_commercial_status
        )


class EquipmentMovementCreateUpdateSerializer(
    serializers.ModelSerializer
):
    """
    Creación y modificación de movimientos de equipos.

    Este serializer registra la trazabilidad, pero no cambia
    automáticamente la ficha principal del equipo.

    Los cambios automáticos del equipo se realizarán posteriormente
    desde servicios específicos de estados, entregas, contratos,
    reparaciones y traslados.
    """

    class Meta:
        model = EquipmentMovement

        fields = (
            "equipment",
            "movement_type",
            "occurred_at",
            "responsible_user",
            "previous_technical_status",
            "new_technical_status",
            "previous_commercial_status",
            "new_commercial_status",
            "previous_location",
            "new_location",
            "previous_position_reference",
            "new_position_reference",
            "previous_customer",
            "new_customer",
            "previous_customer_branch",
            "new_customer_branch",
            "previous_owner",
            "new_owner",
            "previous_advisor",
            "new_advisor",
            "reference_type",
            "reference_id",
            "reference_number",
            "document_number",
            "total_meter",
            "black_meter",
            "color_meter",
            "scan_meter",
            "reason",
            "notes",
            "is_system_generated",
        )

    def validate_equipment(self, value):
        """
        Impide registrar movimientos en equipos archivados.
        """

        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes registrar movimientos en un equipo archivado."
            )

        return value

    def validate_reference_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_document_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_previous_location(self, value):
        return str(
            value or ""
        ).strip()

    def validate_new_location(self, value):
        return str(
            value or ""
        ).strip()

    def validate_previous_position_reference(self, value):
        return str(
            value or ""
        ).strip()

    def validate_new_position_reference(self, value):
        return str(
            value or ""
        ).strip()

    def validate_reason(self, value):
        return str(
            value or ""
        ).strip()

    def validate_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate(self, attrs):
        """
        Valida coherencia entre equipo, clientes, sucursales,
        estados, ubicaciones y contadores.
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

        movement_type = values.get(
            "movement_type"
        )

        responsible_user = values.get(
            "responsible_user"
        )

        previous_technical_status = values.get(
            "previous_technical_status"
        )

        new_technical_status = values.get(
            "new_technical_status"
        )

        previous_commercial_status = values.get(
            "previous_commercial_status"
        )

        new_commercial_status = values.get(
            "new_commercial_status"
        )

        previous_location = str(
            values.get(
                "previous_location",
                "",
            )
            or ""
        ).strip()

        new_location = str(
            values.get(
                "new_location",
                "",
            )
            or ""
        ).strip()

        previous_customer = values.get(
            "previous_customer"
        )

        new_customer = values.get(
            "new_customer"
        )

        previous_customer_branch = values.get(
            "previous_customer_branch"
        )

        new_customer_branch = values.get(
            "new_customer_branch"
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

        reason = str(
            values.get(
                "reason",
                "",
            )
            or ""
        ).strip()

        is_system_generated = values.get(
            "is_system_generated",
            False,
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

        if not equipment:
            raise serializers.ValidationError(
                {
                    "equipment": (
                        "Debes seleccionar el equipo relacionado."
                    )
                }
            )

        if not movement_type:
            raise serializers.ValidationError(
                {
                    "movement_type": (
                        "Debes seleccionar el tipo de movimiento."
                    )
                }
            )

        if (
            previous_customer_branch
            and not previous_customer
        ):
            raise serializers.ValidationError(
                {
                    "previous_customer": (
                        "Debes indicar el cliente anterior cuando "
                        "registras una sucursal anterior."
                    )
                }
            )

        if (
            previous_customer_branch
            and previous_customer
            and previous_customer_branch.partner_id
            != previous_customer.id
        ):
            raise serializers.ValidationError(
                {
                    "previous_customer_branch": (
                        "La sucursal anterior no pertenece "
                        "al cliente anterior seleccionado."
                    )
                }
            )

        if (
            new_customer_branch
            and not new_customer
        ):
            raise serializers.ValidationError(
                {
                    "new_customer": (
                        "Debes indicar el nuevo cliente cuando "
                        "registras una nueva sucursal."
                    )
                }
            )

        if (
            new_customer_branch
            and new_customer
            and new_customer_branch.partner_id
            != new_customer.id
        ):
            raise serializers.ValidationError(
                {
                    "new_customer_branch": (
                        "La nueva sucursal no pertenece "
                        "al nuevo cliente seleccionado."
                    )
                }
            )

        movements_requiring_customer = {
            EquipmentMovement.MovementType.RESERVED,
            EquipmentMovement.MovementType.SOLD,
            EquipmentMovement.MovementType.DELIVERY_PREPARATION,
            EquipmentMovement.MovementType.DISPATCHED,
            EquipmentMovement.MovementType.DELIVERED,
            EquipmentMovement.MovementType.CONTRACT_ASSIGNED,
            EquipmentMovement.MovementType.INSTALLED,
            EquipmentMovement.MovementType.TEMPORARY_LOAN,
            EquipmentMovement.MovementType.DEMONSTRATION,
            EquipmentMovement.MovementType.REPLACEMENT_ASSIGNED,
        }

        if (
            movement_type in movements_requiring_customer
            and not new_customer
        ):
            raise serializers.ValidationError(
                {
                    "new_customer": (
                        "Este tipo de movimiento requiere "
                        "un cliente relacionado."
                    )
                }
            )

        movements_requiring_location = {
            EquipmentMovement.MovementType.UNLOADING,
            EquipmentMovement.MovementType.WAREHOUSE_ENTRY,
            EquipmentMovement.MovementType.LOCATION_CHANGE,
            EquipmentMovement.MovementType.DELIVERED,
            EquipmentMovement.MovementType.INSTALLED,
            EquipmentMovement.MovementType.RETURNED_TO_WAREHOUSE,
        }

        if (
            movement_type in movements_requiring_location
            and not new_location
        ):
            raise serializers.ValidationError(
                {
                    "new_location": (
                        "Este tipo de movimiento requiere "
                        "registrar la nueva ubicación."
                    )
                }
            )

        if (
            movement_type
            == EquipmentMovement.MovementType.LOCATION_CHANGE
            and previous_location
            and new_location
            and previous_location == new_location
        ):
            raise serializers.ValidationError(
                {
                    "new_location": (
                        "La nueva ubicación debe ser diferente "
                        "de la ubicación anterior."
                    )
                }
            )

        movements_requiring_reason = {
            EquipmentMovement.MovementType.PROBLEM_REPORTED,
            EquipmentMovement.MovementType.MARKED_FOR_PARTS,
            EquipmentMovement.MovementType.RESERVATION_RELEASED,
            EquipmentMovement.MovementType.OWNERSHIP_CHANGE,
            EquipmentMovement.MovementType.OUT_OF_SERVICE,
            EquipmentMovement.MovementType.DISPOSED,
            EquipmentMovement.MovementType.ARCHIVED,
            EquipmentMovement.MovementType.OTHER,
        }

        if (
            movement_type in movements_requiring_reason
            and not reason
        ):
            raise serializers.ValidationError(
                {
                    "reason": (
                        "Debes indicar el motivo para este "
                        "tipo de movimiento."
                    )
                }
            )

        if (
            previous_technical_status
            and new_technical_status
            and previous_technical_status
            == new_technical_status
        ):
            raise serializers.ValidationError(
                {
                    "new_technical_status": (
                        "El nuevo estado técnico debe ser diferente "
                        "del estado técnico anterior."
                    )
                }
            )

        if (
            previous_commercial_status
            and new_commercial_status
            and previous_commercial_status
            == new_commercial_status
        ):
            raise serializers.ValidationError(
                {
                    "new_commercial_status": (
                        "El nuevo estado comercial debe ser diferente "
                        "del estado comercial anterior."
                    )
                }
            )

        if (
            reference_type
            == EquipmentMovement.ReferenceType.SYSTEM
            and not is_system_generated
        ):
            raise serializers.ValidationError(
                {
                    "is_system_generated": (
                        "Un movimiento con origen sistema debe "
                        "marcarse como generado automáticamente."
                    )
                }
            )

        if (
            reference_type
            != EquipmentMovement.ReferenceType.MANUAL
            and not reference_id
            and not reference_number
        ):
            raise serializers.ValidationError(
                {
                    "reference_number": (
                        "Debes indicar el ID o número del proceso "
                        "que originó el movimiento."
                    )
                }
            )

        if (
            reference_type
            == EquipmentMovement.ReferenceType.MANUAL
            and reference_id
        ):
            raise serializers.ValidationError(
                {
                    "reference_type": (
                        "Selecciona un origen relacionado antes "
                        "de registrar un ID de referencia."
                    )
                }
            )

        if (
            is_system_generated
            and not responsible_user
        ):
            actor = get_authenticated_user(
                self
            )

            if actor:
                attrs["responsible_user"] = actor

        if equipment:
            meter_fields = (
                (
                    "total_meter",
                    total_meter,
                    equipment.initial_total_meter,
                ),
                (
                    "black_meter",
                    black_meter,
                    equipment.initial_black_meter,
                ),
                (
                    "color_meter",
                    color_meter,
                    equipment.initial_color_meter,
                ),
                (
                    "scan_meter",
                    scan_meter,
                    equipment.initial_scan_meter,
                ),
            )

            for (
                field_name,
                current_value,
                initial_value,
            ) in meter_fields:
                if (
                    current_value is not None
                    and current_value < initial_value
                ):
                    raise serializers.ValidationError(
                        {
                            field_name: (
                                "El contador del movimiento no puede "
                                "ser menor que el contador de ingreso."
                            )
                        }
                    )

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

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """
        Crea el movimiento registrando auditoría.
        """

        actor = get_authenticated_user(
            self
        )

        if (
            not validated_data.get(
                "responsible_user"
            )
            and actor
        ):
            validated_data[
                "responsible_user"
            ] = actor

        movement = EquipmentMovement(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            movement.full_clean()
            movement.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return movement

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        """
        Actualiza el movimiento registrando auditoría.
        """

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


class ArchiveEquipmentMovementSerializer(
    serializers.Serializer
):
    """
    Datos requeridos para archivar un movimiento.
    """

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )