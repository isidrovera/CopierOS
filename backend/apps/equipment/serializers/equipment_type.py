# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers

from ..models import EquipmentType
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class EquipmentTypeListSerializer(
    serializers.ModelSerializer
):
    """
    Serializer reducido para listar tipos de equipos.
    """

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = EquipmentType

        fields = (
            "id",
            "code",
            "name",
            "description",
            "requires_color_definition",
            "requires_meter",
            "allows_accessories",
            "is_active",
            "display_order",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class EquipmentTypeDetailSerializer(
    serializers.ModelSerializer
):
    """
    Serializer completo de un tipo de equipo.
    """

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
        model = EquipmentType

        fields = (
            "id",
            "code",
            "name",
            "description",
            "requires_color_definition",
            "requires_meter",
            "allows_accessories",
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


class EquipmentTypeCreateUpdateSerializer(
    serializers.ModelSerializer
):
    """
    Creación y modificación de tipos de equipos.
    """

    class Meta:
        model = EquipmentType

        fields = (
            "code",
            "name",
            "description",
            "requires_color_definition",
            "requires_meter",
            "allows_accessories",
            "is_active",
            "display_order",
        )

    def validate_code(self, value):
        """
        Normaliza y valida el código interno.
        """

        code = str(
            value or ""
        ).strip().upper()

        if not code:
            raise serializers.ValidationError(
                "El código del tipo de equipo es obligatorio."
            )

        queryset = EquipmentType.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un tipo de equipo con este código."
            )

        return code

    def validate_name(self, value):
        """
        Normaliza y valida el nombre.
        """

        name = str(
            value or ""
        ).strip()

        if not name:
            raise serializers.ValidationError(
                "El nombre del tipo de equipo es obligatorio."
            )

        queryset = EquipmentType.objects.filter(
            name__iexact=name,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un tipo de equipo con este nombre."
            )

        return name

    def validate_description(self, value):
        return str(
            value or ""
        ).strip()

    @transaction.atomic
    def create(self, validated_data):
        """
        Crea el tipo de equipo registrando auditoría.
        """

        actor = get_authenticated_user(
            self
        )

        equipment_type = EquipmentType(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            equipment_type.full_clean()
            equipment_type.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return equipment_type

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        """
        Actualiza el tipo de equipo registrando auditoría.
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


class ArchiveEquipmentTypeSerializer(
    serializers.Serializer
):
    """
    Datos requeridos para archivar un tipo de equipo.
    """

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )