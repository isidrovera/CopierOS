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

    component_type_name = serializers.CharField(
        source="component.component_type.name",
        read_only=True,
    )

    component_category = serializers.CharField(
        source="component.component_type.category",
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
    )

    equipment_family_code = serializers.CharField(
        source="equipment_family.code",
        read_only=True,
    )

    equipment_model_name = serializers.CharField(
        source="equipment_model.name",
        read_only=True,
        allow_null=True,
    )

    equipment_model_code = serializers.CharField(
        source="equipment_model.code",
        read_only=True,
        allow_null=True,
    )

    brand_name = serializers.CharField(
        source="equipment_family.brand.name",
        read_only=True,
    )

    equipment_type_name = serializers.CharField(
        source="equipment_family.equipment_type.name",
        read_only=True,
    )

    effective_manufacturer_code = serializers.CharField(
        read_only=True,
    )

    effective_expected_life_meter = serializers.IntegerField(
        read_only=True,
        allow_null=True,
    )

    effective_expected_life_days = serializers.IntegerField(
        read_only=True,
        allow_null=True,
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
            "component_type_name",
            "component_category",
            "component_color",
            "component_color_name",
            "equipment_family",
            "equipment_family_name",
            "equipment_family_code",
            "equipment_model",
            "equipment_model_name",
            "equipment_model_code",
            "brand_name",
            "equipment_type_name",
            "target_name",
            "position",
            "manufacturer_code_override",
            "effective_manufacturer_code",
            "expected_life_meter_override",
            "effective_expected_life_meter",
            "expected_life_days_override",
            "effective_expected_life_days",
            "is_required",
            "is_active",
            "display_order",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_target_name(self, obj):
        if obj.equipment_model_id:
            return str(
                obj.equipment_model
            )

        return str(
            obj.equipment_family
        )


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

    component_category = serializers.CharField(
        source="component.component_type.category",
        read_only=True,
    )

    component_category_name = serializers.CharField(
        source=(
            "component.component_type."
            "get_category_display"
        ),
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

    component_manufacturer_code = serializers.CharField(
        source="component.manufacturer_code",
        read_only=True,
    )

    component_expected_life_meter = serializers.IntegerField(
        source="component.expected_life_meter",
        read_only=True,
        allow_null=True,
    )

    component_expected_life_days = serializers.IntegerField(
        source="component.expected_life_days",
        read_only=True,
        allow_null=True,
    )

    equipment_family_name = serializers.CharField(
        source="equipment_family.name",
        read_only=True,
    )

    equipment_family_code = serializers.CharField(
        source="equipment_family.code",
        read_only=True,
    )

    equipment_model_name = serializers.CharField(
        source="equipment_model.name",
        read_only=True,
        allow_null=True,
    )

    equipment_model_code = serializers.CharField(
        source="equipment_model.code",
        read_only=True,
        allow_null=True,
    )

    brand_name = serializers.CharField(
        source="equipment_family.brand.name",
        read_only=True,
    )

    equipment_type_name = serializers.CharField(
        source="equipment_family.equipment_type.name",
        read_only=True,
    )

    effective_manufacturer_code = serializers.CharField(
        read_only=True,
    )

    effective_expected_life_meter = serializers.IntegerField(
        read_only=True,
        allow_null=True,
    )

    effective_expected_life_days = serializers.IntegerField(
        read_only=True,
        allow_null=True,
    )

    target_name = serializers.SerializerMethodField()

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
            "component_category",
            "component_category_name",
            "component_color",
            "component_color_name",
            "component_manufacturer_code",
            "component_expected_life_meter",
            "component_expected_life_days",
            "equipment_family",
            "equipment_family_name",
            "equipment_family_code",
            "equipment_model",
            "equipment_model_name",
            "equipment_model_code",
            "brand_name",
            "equipment_type_name",
            "target_name",
            "position",
            "manufacturer_code_override",
            "effective_manufacturer_code",
            "expected_life_meter_override",
            "effective_expected_life_meter",
            "expected_life_days_override",
            "effective_expected_life_days",
            "technical_notes",
            "is_required",
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
            "component_category",
            "component_category_name",
            "component_color",
            "component_color_name",
            "component_manufacturer_code",
            "component_expected_life_meter",
            "component_expected_life_days",
            "equipment_family_name",
            "equipment_family_code",
            "equipment_model_name",
            "equipment_model_code",
            "brand_name",
            "equipment_type_name",
            "target_name",
            "effective_manufacturer_code",
            "effective_expected_life_meter",
            "effective_expected_life_days",
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

    def get_target_name(self, obj):
        if obj.equipment_model_id:
            return str(
                obj.equipment_model
            )

        return str(
            obj.equipment_family
        )


class ComponentCompatibilityCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = ComponentCompatibility

        fields = (
            "component",
            "equipment_family",
            "equipment_model",
            "position",
            "manufacturer_code_override",
            "expected_life_meter_override",
            "expected_life_days_override",
            "technical_notes",
            "is_required",
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

    def validate_position(self, value):
        return str(
            value or ""
        ).strip().lower()

    def validate_manufacturer_code_override(self, value):
        return str(
            value or ""
        ).strip().upper()

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

        position = str(
            attrs.get(
                "position",
                getattr(
                    instance,
                    "position",
                    "",
                ),
            )
            or ""
        ).strip().lower()

        manufacturer_code_override = str(
            attrs.get(
                "manufacturer_code_override",
                getattr(
                    instance,
                    "manufacturer_code_override",
                    "",
                ),
            )
            or ""
        ).strip().upper()

        expected_life_meter_override = attrs.get(
            "expected_life_meter_override",
            getattr(
                instance,
                "expected_life_meter_override",
                None,
            ),
        )

        expected_life_days_override = attrs.get(
            "expected_life_days_override",
            getattr(
                instance,
                "expected_life_days_override",
                None,
            ),
        )

        if not component:
            raise serializers.ValidationError(
                {
                    "component": (
                        "Debes seleccionar un componente."
                    ),
                }
            )

        if not equipment_family:
            raise serializers.ValidationError(
                {
                    "equipment_family": (
                        "Debes seleccionar una familia de equipos."
                    ),
                }
            )

        if equipment_model:
            if not equipment_model.equipment_family_id:
                raise serializers.ValidationError(
                    {
                        "equipment_model": (
                            "El modelo seleccionado no tiene una "
                            "familia de equipos asignada."
                        ),
                    }
                )

            if (
                equipment_model.equipment_family_id
                != equipment_family.id
            ):
                raise serializers.ValidationError(
                    {
                        "equipment_model": (
                            "El modelo seleccionado no pertenece "
                            "a la familia indicada."
                        ),
                    }
                )

            if equipment_model.brand_id != equipment_family.brand_id:
                raise serializers.ValidationError(
                    {
                        "equipment_model": (
                            "La marca del modelo no coincide "
                            "con la marca de la familia."
                        ),
                    }
                )

            if (
                equipment_model.equipment_type_id
                != equipment_family.equipment_type_id
            ):
                raise serializers.ValidationError(
                    {
                        "equipment_model": (
                            "El tipo del modelo no coincide "
                            "con el tipo de la familia."
                        ),
                    }
                )

        if (
            component.color
            != EquipmentComponent.Color.NOT_APPLICABLE
            and not position
        ):
            position = component.color
            attrs["position"] = position

        if (
            component.color
            != EquipmentComponent.Color.NOT_APPLICABLE
            and position
            and position != component.color
        ):
            raise serializers.ValidationError(
                {
                    "position": (
                        "La posición o color no coincide "
                        "con el color del componente."
                    ),
                }
            )

        if (
            expected_life_meter_override is not None
            and expected_life_meter_override <= 0
        ):
            raise serializers.ValidationError(
                {
                    "expected_life_meter_override": (
                        "La duración específica por contador "
                        "debe ser mayor que cero."
                    ),
                }
            )

        if (
            expected_life_days_override is not None
            and expected_life_days_override <= 0
        ):
            raise serializers.ValidationError(
                {
                    "expected_life_days_override": (
                        "La duración específica en días "
                        "debe ser mayor que cero."
                    ),
                }
            )

        if (
            manufacturer_code_override
            and component.manufacturer_code
            and manufacturer_code_override
            == component.manufacturer_code
        ):
            attrs["manufacturer_code_override"] = ""

        duplicate_queryset = (
            ComponentCompatibility.objects.filter(
                component=component,
                equipment_family=equipment_family,
                equipment_model=equipment_model,
                position__iexact=position,
            )
        )

        if instance:
            duplicate_queryset = duplicate_queryset.exclude(
                pk=instance.pk,
            )

        if duplicate_queryset.exists():
            raise serializers.ValidationError(
                {
                    "component": (
                        "Esta compatibilidad ya está registrada "
                        "para la familia, modelo y posición."
                    ),
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