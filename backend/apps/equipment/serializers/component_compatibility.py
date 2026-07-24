# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers

from ..models import (
    ComponentCompatibility,
    EquipmentComponent,
)
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class ComponentCompatibilityListSerializer(
    serializers.ModelSerializer
):
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

    equipment_family_name = serializers.CharField(
        source="equipment_family.name",
        read_only=True,
        allow_null=True,
    )

    equipment_model_name = serializers.CharField(
        source="equipment_model.name",
        read_only=True,
        allow_null=True,
    )

    brand_name = serializers.SerializerMethodField()

    compatibility_type_name = serializers.CharField(
        source="get_compatibility_type_display",
        read_only=True,
    )

    position_name = serializers.CharField(
        source="get_position_display",
        read_only=True,
    )

    target_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = ComponentCompatibility

        fields = (
            "id",
            "component",
            "component_name",
            "component_code",
            "component_color",
            "component_color_name",
            "equipment_family",
            "equipment_family_name",
            "equipment_model",
            "equipment_model_name",
            "brand_name",
            "target_name",
            "compatibility_type",
            "compatibility_type_name",
            "position",
            "position_name",
            "manufacturer_reference",
            "requires_adjustment",
            "is_preferred",
            "is_active",
            "display_order",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_brand_name(self, obj):
        if obj.equipment_model_id:
            return obj.equipment_model.brand.name

        if obj.equipment_family_id:
            return obj.equipment_family.brand.name

        return ""

    def get_target_name(self, obj):
        if obj.equipment_model_id:
            return str(
                obj.equipment_model
            )

        if obj.equipment_family_id:
            return str(
                obj.equipment_family
            )

        return ""


class ComponentCompatibilityDetailSerializer(
    serializers.ModelSerializer
):
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

    component_color = serializers.CharField(
        source="component.color",
        read_only=True,
    )

    component_color_name = serializers.CharField(
        source="component.get_color_display",
        read_only=True,
    )

    equipment_family_name = serializers.CharField(
        source="equipment_family.name",
        read_only=True,
        allow_null=True,
    )

    equipment_model_name = serializers.CharField(
        source="equipment_model.name",
        read_only=True,
        allow_null=True,
    )

    brand_name = serializers.SerializerMethodField()

    equipment_type_name = serializers.SerializerMethodField()

    target_name = serializers.SerializerMethodField()

    compatibility_type_name = serializers.CharField(
        source="get_compatibility_type_display",
        read_only=True,
    )

    position_name = serializers.CharField(
        source="get_position_display",
        read_only=True,
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
        model = ComponentCompatibility

        fields = (
            "id",
            "component",
            "component_name",
            "component_code",
            "component_type_name",
            "component_color",
            "component_color_name",
            "equipment_family",
            "equipment_family_name",
            "equipment_model",
            "equipment_model_name",
            "brand_name",
            "equipment_type_name",
            "target_name",
            "compatibility_type",
            "compatibility_type_name",
            "position",
            "position_name",
            "manufacturer_reference",
            "requires_adjustment",
            "adjustment_instructions",
            "is_preferred",
            "technical_notes",
            "is_active",
            "display_order",
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
            "component_name",
            "component_code",
            "component_type_name",
            "component_color",
            "component_color_name",
            "equipment_family_name",
            "equipment_model_name",
            "brand_name",
            "equipment_type_name",
            "target_name",
            "compatibility_type_name",
            "position_name",
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

    def get_brand_name(self, obj):
        if obj.equipment_model_id:
            return obj.equipment_model.brand.name

        if obj.equipment_family_id:
            return obj.equipment_family.brand.name

        return ""

    def get_equipment_type_name(self, obj):
        if obj.equipment_model_id:
            return obj.equipment_model.equipment_type.name

        if obj.equipment_family_id:
            return obj.equipment_family.equipment_type.name

        return ""

    def get_target_name(self, obj):
        if obj.equipment_model_id:
            return str(
                obj.equipment_model
            )

        if obj.equipment_family_id:
            return str(
                obj.equipment_family
            )

        return ""


class ComponentCompatibilityCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = ComponentCompatibility

        fields = (
            "component",
            "equipment_family",
            "equipment_model",
            "compatibility_type",
            "position",
            "manufacturer_reference",
            "requires_adjustment",
            "adjustment_instructions",
            "is_preferred",
            "technical_notes",
            "is_active",
            "display_order",
        )

    def validate_component(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un componente archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar un componente inactivo."
            )

        return value

    def validate_equipment_family(self, value):
        if value is None:
            return value

        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar una familia archivada."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar una familia inactiva."
            )

        return value

    def validate_equipment_model(self, value):
        if value is None:
            return value

        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un modelo archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar un modelo inactivo."
            )

        return value

    def validate_manufacturer_reference(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_adjustment_instructions(self, value):
        return str(
            value or ""
        ).strip()

    def validate_technical_notes(self, value):
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

        equipment_family = attrs.get(
            "equipment_family",
            getattr(
                instance,
                "equipment_family",
                None,
            ),
        )

        equipment_model = attrs.get(
            "equipment_model",
            getattr(
                instance,
                "equipment_model",
                None,
            ),
        )

        position = attrs.get(
            "position",
            getattr(
                instance,
                "position",
                ComponentCompatibility.Position.NOT_APPLICABLE,
            ),
        )

        requires_adjustment = attrs.get(
            "requires_adjustment",
            getattr(
                instance,
                "requires_adjustment",
                False,
            ),
        )

        adjustment_instructions = attrs.get(
            "adjustment_instructions",
            getattr(
                instance,
                "adjustment_instructions",
                "",
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

        if not equipment_family and not equipment_model:
            raise serializers.ValidationError(
                {
                    "equipment_family": (
                        "Debes seleccionar una familia o "
                        "un modelo de equipo."
                    ),
                    "equipment_model": (
                        "Debes seleccionar una familia o "
                        "un modelo de equipo."
                    ),
                }
            )

        if equipment_family and equipment_model:
            raise serializers.ValidationError(
                {
                    "equipment_family": (
                        "Selecciona únicamente una familia "
                        "o un modelo específico."
                    ),
                    "equipment_model": (
                        "Selecciona únicamente una familia "
                        "o un modelo específico."
                    ),
                }
            )

        if (
            requires_adjustment
            and not str(
                adjustment_instructions or ""
            ).strip()
        ):
            raise serializers.ValidationError(
                {
                    "adjustment_instructions": (
                        "Debes indicar las instrucciones "
                        "de adaptación."
                    )
                }
            )

        if (
            not requires_adjustment
            and str(
                adjustment_instructions or ""
            ).strip()
        ):
            raise serializers.ValidationError(
                {
                    "adjustment_instructions": (
                        "No debes registrar instrucciones "
                        "si no requiere adaptación."
                    )
                }
            )

        if component:
            color_position_map = {
                EquipmentComponent.Color.BLACK: (
                    ComponentCompatibility.Position.BLACK
                ),
                EquipmentComponent.Color.CYAN: (
                    ComponentCompatibility.Position.CYAN
                ),
                EquipmentComponent.Color.MAGENTA: (
                    ComponentCompatibility.Position.MAGENTA
                ),
                EquipmentComponent.Color.YELLOW: (
                    ComponentCompatibility.Position.YELLOW
                ),
                EquipmentComponent.Color.COLOR: (
                    ComponentCompatibility.Position.COLOR
                ),
                EquipmentComponent.Color.MONOCHROME: (
                    ComponentCompatibility.Position.MONOCHROME
                ),
            }

            expected_position = color_position_map.get(
                component.color
            )

            if (
                expected_position
                and position != expected_position
            ):
                raise serializers.ValidationError(
                    {
                        "position": (
                            "La posición no coincide con "
                            "el color del componente."
                        )
                    }
                )

        queryset = ComponentCompatibility.objects.filter(
            component=component,
            equipment_family=equipment_family,
            equipment_model=equipment_model,
            position=position,
        )

        if instance:
            queryset = queryset.exclude(
                pk=instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                {
                    "component": (
                        "Esta compatibilidad ya está registrada."
                    )
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        compatibility = ComponentCompatibility(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            compatibility.full_clean()
            compatibility.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return compatibility

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


class ArchiveComponentCompatibilitySerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )