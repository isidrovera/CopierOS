# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers

from ..models import EquipmentFamily
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class EquipmentFamilyListSerializer(
    serializers.ModelSerializer
):
    brand_name = serializers.CharField(
        source="brand.name",
        read_only=True,
    )

    equipment_type_name = serializers.CharField(
        source="equipment_type.name",
        read_only=True,
    )

    model_count = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = EquipmentFamily

        fields = (
            "id",
            "code",
            "brand",
            "brand_name",
            "equipment_type",
            "equipment_type_name",
            "name",
            "description",
            "technical_notes",
            "is_active",
            "display_order",
            "model_count",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_model_count(self, obj):
        return obj.equipment_models.filter(
            archived_at__isnull=True,
        ).count()


class EquipmentFamilyDetailSerializer(
    serializers.ModelSerializer
):
    brand_name = serializers.CharField(
        source="brand.name",
        read_only=True,
    )

    equipment_type_name = serializers.CharField(
        source="equipment_type.name",
        read_only=True,
    )

    model_count = serializers.SerializerMethodField()

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
        model = EquipmentFamily

        fields = (
            "id",
            "code",
            "brand",
            "brand_name",
            "equipment_type",
            "equipment_type_name",
            "name",
            "description",
            "technical_notes",
            "is_active",
            "display_order",
            "model_count",
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
            "brand_name",
            "equipment_type_name",
            "model_count",
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

    def get_model_count(self, obj):
        return obj.equipment_models.filter(
            archived_at__isnull=True,
        ).count()


class EquipmentFamilyCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = EquipmentFamily

        fields = (
            "code",
            "brand",
            "equipment_type",
            "name",
            "description",
            "technical_notes",
            "is_active",
            "display_order",
        )

    def validate_code(self, value):
        code = str(
            value or ""
        ).strip().upper()

        if not code:
            raise serializers.ValidationError(
                "El código de la familia es obligatorio."
            )

        queryset = EquipmentFamily.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una familia con este código."
            )

        return code

    def validate_name(self, value):
        name = str(
            value or ""
        ).strip()

        if not name:
            raise serializers.ValidationError(
                "El nombre de la familia es obligatorio."
            )

        return name

    def validate_description(self, value):
        return str(
            value or ""
        ).strip()

    def validate_technical_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate_brand(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar una marca archivada."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar una marca inactiva."
            )

        return value

    def validate_equipment_type(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un tipo archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar un tipo inactivo."
            )

        return value

    def validate(self, attrs):
        instance = self.instance

        brand = attrs.get(
            "brand",
            getattr(
                instance,
                "brand",
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

        if brand and name:
            queryset = EquipmentFamily.objects.filter(
                brand=brand,
                name__iexact=str(name).strip(),
            )

            if instance:
                queryset = queryset.exclude(
                    pk=instance.pk,
                )

            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "name": (
                            "Ya existe esta familia para "
                            "la marca seleccionada."
                        )
                    }
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        family = EquipmentFamily(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            family.full_clean()
            family.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return family

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


class ArchiveEquipmentFamilySerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )