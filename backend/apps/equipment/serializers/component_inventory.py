# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers

from ..models import ComponentInventory
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class ComponentInventoryListSerializer(
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

    color = serializers.CharField(
        source="component.color",
        read_only=True,
    )

    color_name = serializers.CharField(
        source="component.get_color_display",
        read_only=True,
    )

    condition_name = serializers.CharField(
        source="get_condition_display",
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    available_quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = ComponentInventory

        fields = (
            "id",
            "component",
            "component_name",
            "component_code",
            "component_type_name",
            "component_category",
            "color",
            "color_name",
            "internal_code",
            "serial_number",
            "lot_number",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "condition",
            "condition_name",
            "status",
            "status_name",
            "warehouse",
            "location",
            "supplier_name",
            "purchase_cost",
            "acquisition_date",
            "initial_meter",
            "is_active",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class ComponentInventoryDetailSerializer(
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

    color = serializers.CharField(
        source="component.color",
        read_only=True,
    )

    color_name = serializers.CharField(
        source="component.get_color_display",
        read_only=True,
    )

    condition_name = serializers.CharField(
        source="get_condition_display",
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    available_quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
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
        model = ComponentInventory

        fields = (
            "id",
            "component",
            "component_name",
            "component_code",
            "component_type_name",
            "component_category",
            "color",
            "color_name",
            "internal_code",
            "serial_number",
            "lot_number",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "condition",
            "condition_name",
            "status",
            "status_name",
            "warehouse",
            "location",
            "supplier_name",
            "purchase_cost",
            "acquisition_date",
            "initial_meter",
            "notes",
            "is_active",
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
            "color",
            "color_name",
            "condition_name",
            "status_name",
            "available_quantity",
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


class ComponentInventoryCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = ComponentInventory

        fields = (
            "component",
            "internal_code",
            "serial_number",
            "lot_number",
            "quantity",
            "reserved_quantity",
            "condition",
            "status",
            "warehouse",
            "location",
            "supplier_name",
            "purchase_cost",
            "acquisition_date",
            "initial_meter",
            "notes",
            "is_active",
        )

    def validate_internal_code(self, value):
        internal_code = str(
            value or ""
        ).strip().upper()

        if not internal_code:
            raise serializers.ValidationError(
                "El código interno es obligatorio."
            )

        queryset = ComponentInventory.objects.filter(
            internal_code__iexact=internal_code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un registro con este código interno."
            )

        return internal_code

    def validate_serial_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_lot_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_warehouse(self, value):
        return str(
            value or ""
        ).strip()

    def validate_location(self, value):
        return str(
            value or ""
        ).strip()

    def validate_supplier_name(self, value):
        return str(
            value or ""
        ).strip()

    def validate_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate_component(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un componente archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar un componente inactivo."
            )

        if not value.component_type.controls_stock:
            raise serializers.ValidationError(
                "Este tipo de componente no controla inventario."
            )

        return value

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

        serial_number = attrs.get(
            "serial_number",
            getattr(
                instance,
                "serial_number",
                "",
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

        reserved_quantity = attrs.get(
            "reserved_quantity",
            getattr(
                instance,
                "reserved_quantity",
                0,
            ),
        )

        status = attrs.get(
            "status",
            getattr(
                instance,
                "status",
                ComponentInventory.Status.AVAILABLE,
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

        if quantity is None or quantity <= 0:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "La cantidad debe ser mayor que cero."
                    )
                }
            )

        if reserved_quantity < 0:
            raise serializers.ValidationError(
                {
                    "reserved_quantity": (
                        "La cantidad reservada no puede ser negativa."
                    )
                }
            )

        if reserved_quantity > quantity:
            raise serializers.ValidationError(
                {
                    "reserved_quantity": (
                        "La cantidad reservada no puede superar "
                        "la cantidad existente."
                    )
                }
            )

        normalized_serial = str(
            serial_number or ""
        ).strip().upper()

        if (
            component.requires_individual_serial
            and not normalized_serial
        ):
            raise serializers.ValidationError(
                {
                    "serial_number": (
                        "Este componente requiere número de serie."
                    )
                }
            )

        if normalized_serial and quantity != 1:
            raise serializers.ValidationError(
                {
                    "quantity": (
                        "Un componente con serie debe tener "
                        "cantidad igual a uno."
                    )
                }
            )

        if normalized_serial:
            queryset = ComponentInventory.objects.filter(
                component=component,
                serial_number__iexact=normalized_serial,
            )

            if instance:
                queryset = queryset.exclude(
                    pk=instance.pk,
                )

            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "serial_number": (
                            "Esta serie ya está registrada "
                            "para el componente."
                        )
                    }
                )

        available_quantity = quantity - reserved_quantity

        if (
            status == ComponentInventory.Status.AVAILABLE
            and available_quantity <= 0
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "No puede estar disponible porque "
                        "no tiene cantidad libre."
                    )
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        inventory = ComponentInventory(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            inventory.full_clean()
            inventory.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return inventory

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


class ArchiveComponentInventorySerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )