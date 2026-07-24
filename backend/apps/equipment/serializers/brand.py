# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers

from ..models import EquipmentBrand
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class EquipmentBrandListSerializer(
    serializers.ModelSerializer
):
    """
    Serializer reducido para listar marcas de equipos.
    """

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    models_count = serializers.SerializerMethodField()

    class Meta:
        model = EquipmentBrand

        fields = (
            "id",
            "code",
            "name",
            "legal_name",
            "country_code",
            "country_name",
            "website",
            "logo",
            "is_active",
            "display_order",
            "is_archived",
            "models_count",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_models_count(self, obj):
        """
        Cuenta los modelos activos y no archivados
        registrados para la marca.
        """

        return obj.equipment_models.filter(
            archived_at__isnull=True,
        ).count()


class EquipmentBrandDetailSerializer(
    serializers.ModelSerializer
):
    """
    Serializer completo de una marca de equipos.
    """

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    models_count = serializers.SerializerMethodField()

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
        model = EquipmentBrand

        fields = (
            "id",
            "code",
            "name",
            "legal_name",
            "country_code",
            "country_name",
            "website",
            "description",
            "logo",
            "is_active",
            "display_order",
            "models_count",
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
            "models_count",
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

    def get_models_count(self, obj):
        """
        Cuenta los modelos activos y no archivados
        registrados para la marca.
        """

        return obj.equipment_models.filter(
            archived_at__isnull=True,
        ).count()


class EquipmentBrandCreateUpdateSerializer(
    serializers.ModelSerializer
):
    """
    Creación y modificación de marcas de equipos.
    """

    class Meta:
        model = EquipmentBrand

        fields = (
            "code",
            "name",
            "legal_name",
            "country_code",
            "country_name",
            "website",
            "description",
            "logo",
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
                "El código de la marca es obligatorio."
            )

        queryset = EquipmentBrand.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una marca con este código."
            )

        return code

    def validate_name(self, value):
        """
        Normaliza y valida el nombre de la marca.
        """

        name = str(
            value or ""
        ).strip()

        if not name:
            raise serializers.ValidationError(
                "El nombre de la marca es obligatorio."
            )

        queryset = EquipmentBrand.objects.filter(
            name__iexact=name,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una marca con este nombre."
            )

        return name

    def validate_legal_name(self, value):
        return str(
            value or ""
        ).strip()

    def validate_country_code(self, value):
        """
        Normaliza y valida el código de país.

        El campo puede quedar vacío.
        """

        country_code = str(
            value or ""
        ).strip().upper()

        if not country_code:
            return ""

        if len(country_code) != 2:
            raise serializers.ValidationError(
                "El código del país debe contener "
                "exactamente dos letras."
            )

        if not country_code.isalpha():
            raise serializers.ValidationError(
                "El código del país solo puede contener letras."
            )

        return country_code

    def validate_country_name(self, value):
        return str(
            value or ""
        ).strip()

    def validate_website(self, value):
        return str(
            value or ""
        ).strip()

    def validate_description(self, value):
        return str(
            value or ""
        ).strip()

    @transaction.atomic
    def create(self, validated_data):
        """
        Crea la marca registrando auditoría.
        """

        actor = get_authenticated_user(
            self
        )

        brand = EquipmentBrand(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            brand.full_clean()
            brand.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return brand

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        """
        Actualiza la marca registrando auditoría.
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


class ArchiveEquipmentBrandSerializer(
    serializers.Serializer
):
    """
    Datos requeridos para archivar una marca.
    """

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )