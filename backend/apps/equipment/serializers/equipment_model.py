# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers

from ..models import (
    EquipmentBrand,
    EquipmentModel,
    EquipmentType,
)
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class EquipmentModelListSerializer(
    serializers.ModelSerializer
):
    """
    Serializer reducido para listar modelos de equipos.
    """

    brand_name = serializers.CharField(
        source="brand.name",
        read_only=True,
    )

    equipment_type_name = serializers.CharField(
        source="equipment_type.name",
        read_only=True,
    )

    equipment_family_name = serializers.CharField(
        source="equipment_family.name",
        read_only=True,
        allow_null=True,
    )

    equipment_family_code = serializers.CharField(
        source="equipment_family.code",
        read_only=True,
        allow_null=True,
    )

    color_mode_name = serializers.CharField(
        source="get_color_mode_display",
        read_only=True,
    )

    technology_name = serializers.CharField(
        source="get_technology_display",
        read_only=True,
    )

    maximum_paper_size_name = serializers.CharField(
        source="get_maximum_paper_size_display",
        read_only=True,
    )

    equipment_count = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = EquipmentModel

        fields = (
            "id",
            "code",
            "brand",
            "brand_name",
            "equipment_type",
            "equipment_type_name",
            "name",
            "commercial_name",
            "family",
            "equipment_family",
            "equipment_family_name",
            "equipment_family_code",
            "manufacturer_reference",
            "color_mode",
            "color_mode_name",
            "technology",
            "technology_name",
            "maximum_paper_size",
            "maximum_paper_size_name",
            "is_multifunction",
            "supports_printing",
            "supports_copying",
            "supports_scanning",
            "supports_fax",
            "supports_network",
            "supports_duplex",
            "supports_accessories",
            "supports_technical_units",
            "has_total_meter",
            "has_black_meter",
            "has_color_meter",
            "has_scan_meter",
            "image",
            "is_active",
            "display_order",
            "equipment_count",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_equipment_count(self, obj):
        """
        Cuenta las máquinas no archivadas registradas
        con este modelo.
        """

        return obj.equipment_units.filter(
            archived_at__isnull=True,
        ).count()


class EquipmentModelDetailSerializer(
    serializers.ModelSerializer
):
    """
    Serializer completo de un modelo de equipo.
    """

    brand_name = serializers.CharField(
        source="brand.name",
        read_only=True,
    )

    brand_code = serializers.CharField(
        source="brand.code",
        read_only=True,
    )

    equipment_type_name = serializers.CharField(
        source="equipment_type.name",
        read_only=True,
    )

    equipment_type_code = serializers.CharField(
        source="equipment_type.code",
        read_only=True,
    )

    equipment_family_name = serializers.CharField(
        source="equipment_family.name",
        read_only=True,
        allow_null=True,
    )

    equipment_family_code = serializers.CharField(
        source="equipment_family.code",
        read_only=True,
        allow_null=True,
    )

    color_mode_name = serializers.CharField(
        source="get_color_mode_display",
        read_only=True,
    )

    technology_name = serializers.CharField(
        source="get_technology_display",
        read_only=True,
    )

    maximum_paper_size_name = serializers.CharField(
        source="get_maximum_paper_size_display",
        read_only=True,
    )

    equipment_count = serializers.SerializerMethodField()

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
        model = EquipmentModel

        fields = (
            "id",
            "code",
            "brand",
            "brand_name",
            "brand_code",
            "equipment_type",
            "equipment_type_name",
            "equipment_type_code",
            "name",
            "commercial_name",
            "family",
            "equipment_family",
            "equipment_family_name",
            "equipment_family_code",
            "manufacturer_reference",
            "color_mode",
            "color_mode_name",
            "technology",
            "technology_name",
            "maximum_paper_size",
            "maximum_paper_size_name",
            "is_multifunction",
            "supports_printing",
            "supports_copying",
            "supports_scanning",
            "supports_fax",
            "supports_network",
            "supports_duplex",
            "supports_accessories",
            "supports_technical_units",
            "has_total_meter",
            "has_black_meter",
            "has_color_meter",
            "has_scan_meter",
            "image",
            "technical_notes",
            "description",
            "is_active",
            "display_order",
            "equipment_count",
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
            "brand_code",
            "equipment_type_name",
            "equipment_type_code",
            "equipment_family_name",
            "equipment_family_code",
            "color_mode_name",
            "technology_name",
            "maximum_paper_size_name",
            "equipment_count",
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

    def get_equipment_count(self, obj):
        """
        Cuenta las máquinas no archivadas registradas
        con este modelo.
        """

        return obj.equipment_units.filter(
            archived_at__isnull=True,
        ).count()


class EquipmentModelCreateUpdateSerializer(
    serializers.ModelSerializer
):
    """
    Creación y modificación de modelos de equipos.
    """

    class Meta:
        model = EquipmentModel

        fields = (
            "code",
            "brand",
            "equipment_type",
            "name",
            "commercial_name",
            "family",
            "equipment_family",
            "manufacturer_reference",
            "color_mode",
            "technology",
            "maximum_paper_size",
            "is_multifunction",
            "supports_printing",
            "supports_copying",
            "supports_scanning",
            "supports_fax",
            "supports_network",
            "supports_duplex",
            "supports_accessories",
            "supports_technical_units",
            "has_total_meter",
            "has_black_meter",
            "has_color_meter",
            "has_scan_meter",
            "image",
            "technical_notes",
            "description",
            "is_active",
            "display_order",
        )

    def validate_code(self, value):
        """
        Normaliza y valida el código interno del modelo.
        """

        code = str(
            value or ""
        ).strip().upper()

        if not code:
            raise serializers.ValidationError(
                "El código del modelo es obligatorio."
            )

        queryset = EquipmentModel.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un modelo de equipo con este código."
            )

        return code

    def validate_name(self, value):
        """
        Normaliza el nombre del modelo.
        """

        name = str(
            value or ""
        ).strip()

        if not name:
            raise serializers.ValidationError(
                "El nombre del modelo es obligatorio."
            )

        return name

    def validate_commercial_name(self, value):
        return str(
            value or ""
        ).strip()

    def validate_family(self, value):
        return str(
            value or ""
        ).strip()

    def validate_equipment_family(self, value):
        """
        Impide seleccionar una familia archivada o inactiva.
        """

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

    def validate_manufacturer_reference(self, value):
        return str(
            value or ""
        ).strip()

    def validate_technical_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate_description(self, value):
        return str(
            value or ""
        ).strip()

    def validate_brand(self, value):
        """
        Impide seleccionar una marca archivada o inactiva
        para nuevos registros.
        """

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
        """
        Impide seleccionar un tipo archivado o inactivo
        para nuevos registros.
        """

        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un tipo de equipo archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar un tipo de equipo inactivo."
            )

        return value

    def validate(self, attrs):
        """
        Valida relaciones y características funcionales
        del modelo de equipo.
        """

        instance = self.instance

        brand = attrs.get(
            "brand",
            getattr(
                instance,
                "brand",
                None,
            ),
        )

        equipment_type = attrs.get(
            "equipment_type",
            getattr(
                instance,
                "equipment_type",
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

        name = attrs.get(
            "name",
            getattr(
                instance,
                "name",
                "",
            ),
        )

        color_mode = attrs.get(
            "color_mode",
            getattr(
                instance,
                "color_mode",
                EquipmentModel.ColorMode.NOT_APPLICABLE,
            ),
        )

        supports_scanning = attrs.get(
            "supports_scanning",
            getattr(
                instance,
                "supports_scanning",
                True,
            ),
        )

        supports_accessories = attrs.get(
            "supports_accessories",
            getattr(
                instance,
                "supports_accessories",
                True,
            ),
        )

        has_total_meter = attrs.get(
            "has_total_meter",
            getattr(
                instance,
                "has_total_meter",
                True,
            ),
        )

        has_black_meter = attrs.get(
            "has_black_meter",
            getattr(
                instance,
                "has_black_meter",
                True,
            ),
        )

        has_color_meter = attrs.get(
            "has_color_meter",
            getattr(
                instance,
                "has_color_meter",
                False,
            ),
        )

        has_scan_meter = attrs.get(
            "has_scan_meter",
            getattr(
                instance,
                "has_scan_meter",
                False,
            ),
        )

        if not brand:
            raise serializers.ValidationError(
                {
                    "brand": (
                        "Debes seleccionar una marca."
                    )
                }
            )

        if not equipment_type:
            raise serializers.ValidationError(
                {
                    "equipment_type": (
                        "Debes seleccionar un tipo de equipo."
                    )
                }
            )

        if equipment_family:
            if equipment_family.brand_id != brand.id:
                raise serializers.ValidationError(
                    {
                        "equipment_family": (
                            "La familia seleccionada no pertenece "
                            "a la marca del modelo."
                        )
                    }
                )

            if (
                equipment_family.equipment_type_id
                != equipment_type.id
            ):
                raise serializers.ValidationError(
                    {
                        "equipment_family": (
                            "La familia seleccionada no pertenece "
                            "al tipo de equipo indicado."
                        )
                    }
                )

        normalized_name = str(
            name or ""
        ).strip()

        if brand and normalized_name:
            queryset = EquipmentModel.objects.filter(
                brand=brand,
                name__iexact=normalized_name,
            )

            if instance:
                queryset = queryset.exclude(
                    pk=instance.pk,
                )

            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "name": (
                            "Ya existe este modelo para la "
                            "marca seleccionada."
                        )
                    }
                )

        if (
            color_mode
            == EquipmentModel.ColorMode.MONOCHROME
            and has_color_meter
        ):
            raise serializers.ValidationError(
                {
                    "has_color_meter": (
                        "Un modelo blanco y negro no puede "
                        "tener contador de color."
                    )
                }
            )

        if (
            color_mode
            == EquipmentModel.ColorMode.COLOR
            and not has_color_meter
        ):
            raise serializers.ValidationError(
                {
                    "has_color_meter": (
                        "Un modelo de color debe permitir "
                        "registrar contador de color."
                    )
                }
            )

        if (
            not supports_scanning
            and has_scan_meter
        ):
            raise serializers.ValidationError(
                {
                    "has_scan_meter": (
                        "No puedes habilitar el contador "
                        "de escaneo si el modelo no permite escanear."
                    )
                }
            )

        if (
            equipment_type
            and not equipment_type.requires_meter
            and any(
                (
                    has_total_meter,
                    has_black_meter,
                    has_color_meter,
                    has_scan_meter,
                )
            )
        ):
            raise serializers.ValidationError(
                {
                    "has_total_meter": (
                        "El tipo de equipo seleccionado no "
                        "requiere contadores."
                    )
                }
            )

        if (
            equipment_type
            and not equipment_type.allows_accessories
            and supports_accessories
        ):
            raise serializers.ValidationError(
                {
                    "supports_accessories": (
                        "El tipo de equipo seleccionado no "
                        "permite accesorios."
                    )
                }
            )

        if (
            equipment_type
            and equipment_type.requires_color_definition
            and color_mode
            == EquipmentModel.ColorMode.NOT_APPLICABLE
        ):
            raise serializers.ValidationError(
                {
                    "color_mode": (
                        "Debes definir si el modelo es "
                        "blanco y negro o color."
                    )
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """
        Crea el modelo de equipo registrando auditoría.
        """

        actor = get_authenticated_user(
            self
        )

        equipment_model = EquipmentModel(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            equipment_model.full_clean()
            equipment_model.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return equipment_model

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        """
        Actualiza el modelo de equipo registrando auditoría.
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


class ArchiveEquipmentModelSerializer(
    serializers.Serializer
):
    """
    Datos requeridos para archivar un modelo de equipo.
    """

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )