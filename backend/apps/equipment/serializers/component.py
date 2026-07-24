# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers

from ..models import (
    ComponentType,
    EquipmentComponent,
)
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class EquipmentComponentListSerializer(
    serializers.ModelSerializer
):
    component_type_name = serializers.CharField(
        source="component_type.name",
        read_only=True,
    )

    category = serializers.CharField(
        source="component_type.category",
        read_only=True,
    )

    category_name = serializers.CharField(
        source="component_type.get_category_display",
        read_only=True,
    )

    parent_component_name = serializers.CharField(
        source="parent_component.name",
        read_only=True,
        allow_null=True,
    )

    color_name = serializers.CharField(
        source="get_color_display",
        read_only=True,
    )

    condition_control_name = serializers.CharField(
        source="get_condition_control_display",
        read_only=True,
    )

    compatibility_count = serializers.SerializerMethodField()

    inventory_count = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = EquipmentComponent

        fields = (
            "id",
            "component_type",
            "component_type_name",
            "category",
            "category_name",
            "parent_component",
            "parent_component_name",
            "code",
            "name",
            "manufacturer_code",
            "alternative_code",
            "color",
            "color_name",
            "condition_control",
            "condition_control_name",
            "expected_life_meter",
            "expected_life_days",
            "requires_individual_serial",
            "is_consumable",
            "is_reusable",
            "can_be_repaired",
            "requires_removed_part_tracking",
            "unit_of_measure",
            "image",
            "is_active",
            "display_order",
            "compatibility_count",
            "inventory_count",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_compatibility_count(self, obj):
        return obj.compatibilities.filter(
            archived_at__isnull=True,
        ).count()

    def get_inventory_count(self, obj):
        return obj.inventory_records.filter(
            archived_at__isnull=True,
        ).count()


class EquipmentComponentDetailSerializer(
    serializers.ModelSerializer
):
    component_type_name = serializers.CharField(
        source="component_type.name",
        read_only=True,
    )

    category = serializers.CharField(
        source="component_type.category",
        read_only=True,
    )

    category_name = serializers.CharField(
        source="component_type.get_category_display",
        read_only=True,
    )

    parent_component_name = serializers.CharField(
        source="parent_component.name",
        read_only=True,
        allow_null=True,
    )

    color_name = serializers.CharField(
        source="get_color_display",
        read_only=True,
    )

    condition_control_name = serializers.CharField(
        source="get_condition_control_display",
        read_only=True,
    )

    compatibility_count = serializers.SerializerMethodField()

    inventory_count = serializers.SerializerMethodField()

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
        model = EquipmentComponent

        fields = (
            "id",
            "component_type",
            "component_type_name",
            "category",
            "category_name",
            "parent_component",
            "parent_component_name",
            "code",
            "name",
            "manufacturer_code",
            "alternative_code",
            "color",
            "color_name",
            "condition_control",
            "condition_control_name",
            "expected_life_meter",
            "expected_life_days",
            "requires_individual_serial",
            "is_consumable",
            "is_reusable",
            "can_be_repaired",
            "requires_removed_part_tracking",
            "unit_of_measure",
            "description",
            "technical_notes",
            "image",
            "is_active",
            "display_order",
            "compatibility_count",
            "inventory_count",
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
            "component_type_name",
            "category",
            "category_name",
            "parent_component_name",
            "color_name",
            "condition_control_name",
            "compatibility_count",
            "inventory_count",
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

    def get_compatibility_count(self, obj):
        return obj.compatibilities.filter(
            archived_at__isnull=True,
        ).count()

    def get_inventory_count(self, obj):
        return obj.inventory_records.filter(
            archived_at__isnull=True,
        ).count()


class EquipmentComponentCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = EquipmentComponent

        fields = (
            "component_type",
            "parent_component",
            "code",
            "name",
            "manufacturer_code",
            "alternative_code",
            "color",
            "condition_control",
            "expected_life_meter",
            "expected_life_days",
            "requires_individual_serial",
            "is_consumable",
            "is_reusable",
            "can_be_repaired",
            "requires_removed_part_tracking",
            "unit_of_measure",
            "description",
            "technical_notes",
            "image",
            "is_active",
            "display_order",
        )

    def validate_code(self, value):
        code = str(
            value or ""
        ).strip().upper()

        if not code:
            raise serializers.ValidationError(
                "El código del componente es obligatorio."
            )

        queryset = EquipmentComponent.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un componente con este código."
            )

        return code

    def validate_name(self, value):
        name = str(
            value or ""
        ).strip()

        if not name:
            raise serializers.ValidationError(
                "El nombre del componente es obligatorio."
            )

        return name

    def validate_manufacturer_code(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_alternative_code(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_unit_of_measure(self, value):
        unit = str(
            value or ""
        ).strip().lower()

        if not unit:
            raise serializers.ValidationError(
                "La unidad de medida es obligatoria."
            )

        return unit

    def validate_description(self, value):
        return str(
            value or ""
        ).strip()

    def validate_technical_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate_component_type(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un tipo archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar un tipo inactivo."
            )

        return value

    def validate_parent_component(self, value):
        if value is None:
            return value

        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un componente principal archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar un componente principal inactivo."
            )

        return value

    def validate(self, attrs):
        instance = self.instance

        component_type = attrs.get(
            "component_type",
            getattr(
                instance,
                "component_type",
                None,
            ),
        )

        parent_component = attrs.get(
            "parent_component",
            getattr(
                instance,
                "parent_component",
                None,
            ),
        )

        name = attrs.get(
            "name",
            getattr(
                instance,
                "name",
                "",
            ),
        )

        color = attrs.get(
            "color",
            getattr(
                instance,
                "color",
                EquipmentComponent.Color.NOT_APPLICABLE,
            ),
        )

        condition_control = attrs.get(
            "condition_control",
            getattr(
                instance,
                "condition_control",
                EquipmentComponent.ConditionControl.NONE,
            ),
        )

        expected_life_meter = attrs.get(
            "expected_life_meter",
            getattr(
                instance,
                "expected_life_meter",
                None,
            ),
        )

        expected_life_days = attrs.get(
            "expected_life_days",
            getattr(
                instance,
                "expected_life_days",
                None,
            ),
        )

        requires_individual_serial = attrs.get(
            "requires_individual_serial",
            getattr(
                instance,
                "requires_individual_serial",
                False,
            ),
        )

        is_consumable = attrs.get(
            "is_consumable",
            getattr(
                instance,
                "is_consumable",
                False,
            ),
        )

        is_reusable = attrs.get(
            "is_reusable",
            getattr(
                instance,
                "is_reusable",
                False,
            ),
        )

        can_be_repaired = attrs.get(
            "can_be_repaired",
            getattr(
                instance,
                "can_be_repaired",
                False,
            ),
        )

        if not component_type:
            raise serializers.ValidationError(
                {
                    "component_type": (
                        "Debes seleccionar un tipo de componente."
                    )
                }
            )

        queryset = EquipmentComponent.objects.filter(
            component_type=component_type,
            name__iexact=str(name or "").strip(),
            color=color,
        )

        if instance:
            queryset = queryset.exclude(
                pk=instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                {
                    "name": (
                        "Ya existe un componente con este nombre, "
                        "tipo y color."
                    )
                }
            )

        if parent_component:
            if instance and parent_component.pk == instance.pk:
                raise serializers.ValidationError(
                    {
                        "parent_component": (
                            "Un componente no puede ser su propio "
                            "componente principal."
                        )
                    }
                )

            if (
                component_type.category
                != ComponentType.Category.SUBPART
            ):
                raise serializers.ValidationError(
                    {
                        "parent_component": (
                            "Solo una subparte puede tener un "
                            "componente principal."
                        )
                    }
                )

        if (
            component_type.requires_color
            and color == EquipmentComponent.Color.NOT_APPLICABLE
        ):
            raise serializers.ValidationError(
                {
                    "color": (
                        "Este tipo de componente requiere color."
                    )
                }
            )

        if (
            not component_type.requires_color
            and color != EquipmentComponent.Color.NOT_APPLICABLE
        ):
            raise serializers.ValidationError(
                {
                    "color": (
                        "Este tipo de componente no requiere color."
                    )
                }
            )

        if (
            condition_control
            in (
                EquipmentComponent.ConditionControl.METER,
                EquipmentComponent.ConditionControl.DATE_AND_METER,
            )
            and not expected_life_meter
        ):
            raise serializers.ValidationError(
                {
                    "expected_life_meter": (
                        "Debes indicar la vida útil por contador."
                    )
                }
            )

        if (
            condition_control
            in (
                EquipmentComponent.ConditionControl.DATE,
                EquipmentComponent.ConditionControl.DATE_AND_METER,
            )
            and not expected_life_days
        ):
            raise serializers.ValidationError(
                {
                    "expected_life_days": (
                        "Debes indicar la vida útil en días."
                    )
                }
            )

        if (
            requires_individual_serial
            and not component_type.requires_serial_number
        ):
            raise serializers.ValidationError(
                {
                    "requires_individual_serial": (
                        "El tipo seleccionado no permite "
                        "control por serie."
                    )
                }
            )

        if is_consumable and is_reusable:
            raise serializers.ValidationError(
                {
                    "is_reusable": (
                        "Un consumible no puede ser reutilizable."
                    )
                }
            )

        if can_be_repaired and not is_reusable:
            raise serializers.ValidationError(
                {
                    "can_be_repaired": (
                        "Para reparar el componente debe ser reutilizable."
                    )
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        component = EquipmentComponent(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            component.full_clean()
            component.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return component

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


class ArchiveEquipmentComponentSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )