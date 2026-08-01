# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers

from ..models import ComponentType
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class ComponentTypeListSerializer(
    serializers.ModelSerializer
):
    category_name = serializers.CharField(
        source="get_category_display",
        read_only=True,
    )

    component_count = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = ComponentType

        fields = (
            "id",
            "code",
            "name",
            "category",
            "category_name",
            "description",
            "requires_color",
            "requires_serial_number",
            "requires_meter",
            "is_active",
            "display_order",
            "component_count",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_component_count(self, obj):
        return obj.components.filter(
            archived_at__isnull=True,
        ).count()


class ComponentTypeDetailSerializer(
    serializers.ModelSerializer
):
    category_name = serializers.CharField(
        source="get_category_display",
        read_only=True,
    )

    component_count = serializers.SerializerMethodField()

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
        model = ComponentType

        fields = (
            "id",
            "code",
            "name",
            "category",
            "category_name",
            "description",
            "requires_color",
            "requires_serial_number",
            "requires_meter",
            "is_active",
            "display_order",
            "component_count",
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
            "category_name",
            "component_count",
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

    def get_component_count(self, obj):
        return obj.components.filter(
            archived_at__isnull=True,
        ).count()


class ComponentTypeCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = ComponentType

        fields = (
            "code",
            "name",
            "category",
            "description",
            "requires_color",
            "requires_serial_number",
            "requires_meter",
            "is_active",
            "display_order",
        )

    def validate_code(self, value):
        code = str(
            value or ""
        ).strip().upper()

        if not code:
            raise serializers.ValidationError(
                "El código del tipo de componente es obligatorio."
            )

        queryset = ComponentType.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un tipo de componente con este código."
            )

        return code

    def validate_name(self, value):
        name = str(
            value or ""
        ).strip()

        if not name:
            raise serializers.ValidationError(
                "El nombre del tipo de componente es obligatorio."
            )

        queryset = ComponentType.objects.filter(
            name__iexact=name,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un tipo de componente con este nombre."
            )

        return name

    def validate_description(self, value):
        return str(
            value or ""
        ).strip()

    def validate(self, attrs):
        instance = self.instance

        category = attrs.get(
            "category",
            getattr(
                instance,
                "category",
                None,
            ),
        )

        requires_color = attrs.get(
            "requires_color",
            getattr(
                instance,
                "requires_color",
                False,
            ),
        )

        requires_serial_number = attrs.get(
            "requires_serial_number",
            getattr(
                instance,
                "requires_serial_number",
                False,
            ),
        )

        requires_meter = attrs.get(
            "requires_meter",
            getattr(
                instance,
                "requires_meter",
                False,
            ),
        )

        if (
            category == ComponentType.Category.TONER
            and not requires_color
        ):
            raise serializers.ValidationError(
                {
                    "requires_color": (
                        "El tipo tóner debe requerir color."
                    ),
                }
            )

        if (
            category == ComponentType.Category.SUBPART
            and requires_serial_number
        ):
            raise serializers.ValidationError(
                {
                    "requires_serial_number": (
                        "Una subparte normalmente no debe exigir "
                        "un número de serie individual."
                    ),
                }
            )

        if (
            category == ComponentType.Category.TONER
            and requires_serial_number
        ):
            raise serializers.ValidationError(
                {
                    "requires_serial_number": (
                        "Un tóner no debe exigir un número "
                        "de serie individual."
                    ),
                }
            )

        if (
            category == ComponentType.Category.CONSUMABLE
            and requires_serial_number
        ):
            raise serializers.ValidationError(
                {
                    "requires_serial_number": (
                        "Un consumible no debe exigir un número "
                        "de serie individual."
                    ),
                }
            )

        if (
            category
            in (
                ComponentType.Category.UNIT,
                ComponentType.Category.SUBPART,
                ComponentType.Category.TONER,
                ComponentType.Category.CONSUMABLE,
            )
            and not requires_meter
        ):
            raise serializers.ValidationError(
                {
                    "requires_meter": (
                        "Este tipo debe permitir registrar duración "
                        "estimada mediante contador."
                    ),
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        component_type = ComponentType(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            component_type.full_clean()
            component_type.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return component_type

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


class ArchiveComponentTypeSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )