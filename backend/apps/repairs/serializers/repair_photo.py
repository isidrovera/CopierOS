# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from ..models import RepairPhoto
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class RepairPhotoListSerializer(
    serializers.ModelSerializer
):
    repair_code = serializers.CharField(
        source="repair.code",
        read_only=True,
    )

    equipment_id = serializers.UUIDField(
        source="repair.equipment_id",
        read_only=True,
    )

    equipment_serial_number = serializers.CharField(
        source="repair.equipment.serial_number",
        read_only=True,
    )

    checklist_item_name = serializers.CharField(
        source="checklist_item.name",
        read_only=True,
        allow_null=True,
    )

    category_name = serializers.CharField(
        source="get_category_display",
        read_only=True,
    )

    stage_name = serializers.CharField(
        source="get_stage_display",
        read_only=True,
    )

    taken_by_name = serializers.CharField(
        source="taken_by.full_name",
        read_only=True,
        allow_null=True,
    )

    uploaded_by_name = serializers.CharField(
        source="uploaded_by.full_name",
        read_only=True,
        allow_null=True,
    )

    verified_by_name = serializers.CharField(
        source="verified_by.full_name",
        read_only=True,
        allow_null=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPhoto

        fields = (
            "id",
            "repair",
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "checklist_item",
            "checklist_item_name",
            "image",
            "original_filename",
            "category",
            "category_name",
            "stage",
            "stage_name",
            "title",
            "description",
            "taken_by",
            "taken_by_name",
            "taken_at",
            "uploaded_by",
            "uploaded_by_name",
            "uploaded_at",
            "is_required",
            "counts_for_minimum",
            "is_verified",
            "verified_by",
            "verified_by_name",
            "verified_at",
            "display_order",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class RepairPhotoDetailSerializer(
    serializers.ModelSerializer
):
    repair_code = serializers.CharField(
        source="repair.code",
        read_only=True,
    )

    equipment_id = serializers.UUIDField(
        source="repair.equipment_id",
        read_only=True,
    )

    equipment_serial_number = serializers.CharField(
        source="repair.equipment.serial_number",
        read_only=True,
    )

    checklist_item_name = serializers.CharField(
        source="checklist_item.name",
        read_only=True,
        allow_null=True,
    )

    category_name = serializers.CharField(
        source="get_category_display",
        read_only=True,
    )

    stage_name = serializers.CharField(
        source="get_stage_display",
        read_only=True,
    )

    taken_by_name = serializers.CharField(
        source="taken_by.full_name",
        read_only=True,
        allow_null=True,
    )

    uploaded_by_name = serializers.CharField(
        source="uploaded_by.full_name",
        read_only=True,
        allow_null=True,
    )

    verified_by_name = serializers.CharField(
        source="verified_by.full_name",
        read_only=True,
        allow_null=True,
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

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPhoto

        fields = (
            "id",
            "repair",
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "checklist_item",
            "checklist_item_name",
            "image",
            "original_filename",
            "category",
            "category_name",
            "stage",
            "stage_name",
            "title",
            "description",
            "taken_by",
            "taken_by_name",
            "taken_at",
            "uploaded_by",
            "uploaded_by_name",
            "uploaded_at",
            "is_required",
            "counts_for_minimum",
            "is_verified",
            "verified_by",
            "verified_by_name",
            "verified_at",
            "verification_notes",
            "latitude",
            "longitude",
            "file_size",
            "mime_type",
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

        read_only_fields = fields


class RepairPhotoCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = RepairPhoto

        fields = (
            "repair",
            "checklist_item",
            "image",
            "category",
            "stage",
            "title",
            "description",
            "taken_at",
            "is_required",
            "counts_for_minimum",
            "latitude",
            "longitude",
            "display_order",
        )

    def validate_repair(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes agregar fotografías a una reparación archivada."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes agregar fotografías a una reparación inactiva."
            )

        return value

    def validate_title(self, value):
        return str(
            value or ""
        ).strip()

    def validate_description(self, value):
        return str(
            value or ""
        ).strip()

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                "La fotografía es obligatoria."
            )

        content_type = str(
            getattr(
                value,
                "content_type",
                "",
            )
            or ""
        ).lower()

        allowed_types = {
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/webp",
        }

        if (
            content_type
            and content_type not in allowed_types
        ):
            raise serializers.ValidationError(
                "Solo se permiten imágenes JPG, PNG o WEBP."
            )

        maximum_size = 10 * 1024 * 1024

        if value.size > maximum_size:
            raise serializers.ValidationError(
                "La fotografía no puede superar los 10 MB."
            )

        return value

    def validate(self, attrs):
        instance = self.instance

        repair = attrs.get(
            "repair",
            getattr(
                instance,
                "repair",
                None,
            ),
        )

        checklist_item = attrs.get(
            "checklist_item",
            getattr(
                instance,
                "checklist_item",
                None,
            ),
        )

        is_required = attrs.get(
            "is_required",
            getattr(
                instance,
                "is_required",
                False,
            ),
        )

        counts_for_minimum = attrs.get(
            "counts_for_minimum",
            getattr(
                instance,
                "counts_for_minimum",
                True,
            ),
        )

        latitude = attrs.get(
            "latitude",
            getattr(
                instance,
                "latitude",
                None,
            ),
        )

        longitude = attrs.get(
            "longitude",
            getattr(
                instance,
                "longitude",
                None,
            ),
        )

        if not repair:
            raise serializers.ValidationError(
                {
                    "repair": (
                        "Debes seleccionar una reparación."
                    )
                }
            )

        if checklist_item:
            if (
                checklist_item.checklist.repair_id
                != repair.id
            ):
                raise serializers.ValidationError(
                    {
                        "checklist_item": (
                            "El punto de revisión no pertenece "
                            "a la reparación seleccionada."
                        )
                    }
                )

        if is_required and not counts_for_minimum:
            raise serializers.ValidationError(
                {
                    "counts_for_minimum": (
                        "Una fotografía obligatoria debe "
                        "contabilizar para el mínimo."
                    )
                }
            )

        if latitude is not None:
            if latitude < -90 or latitude > 90:
                raise serializers.ValidationError(
                    {
                        "latitude": (
                            "La latitud debe estar entre -90 y 90."
                        )
                    }
                )

        if longitude is not None:
            if longitude < -180 or longitude > 180:
                raise serializers.ValidationError(
                    {
                        "longitude": (
                            "La longitud debe estar entre -180 y 180."
                        )
                    }
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        image = validated_data.get(
            "image"
        )

        original_filename = ""

        if image:
            original_filename = str(
                getattr(
                    image,
                    "name",
                    "",
                )
                or ""
            ).strip()

        repair_photo = RepairPhoto(
            original_filename=original_filename,
            taken_by=actor,
            uploaded_by=actor,
            uploaded_at=timezone.now(),
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            repair_photo.full_clean()
            repair_photo.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return repair_photo

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

        image = validated_data.get(
            "image"
        )

        if image:
            instance.original_filename = str(
                getattr(
                    image,
                    "name",
                    "",
                )
                or ""
            ).strip()

            instance.uploaded_by = actor
            instance.uploaded_at = timezone.now()

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


class VerifyRepairPhotoSerializer(
    serializers.Serializer
):
    verification_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate(self, attrs):
        photo = self.context.get(
            "photo"
        )

        if not photo:
            raise serializers.ValidationError(
                "No se encontró la fotografía."
            )

        if photo.is_archived:
            raise serializers.ValidationError(
                "La fotografía está archivada."
            )

        if photo.is_verified:
            raise serializers.ValidationError(
                "La fotografía ya se encuentra verificada."
            )

        return attrs


class RemoveRepairPhotoVerificationSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate(self, attrs):
        photo = self.context.get(
            "photo"
        )

        if not photo:
            raise serializers.ValidationError(
                "No se encontró la fotografía."
            )

        if photo.is_archived:
            raise serializers.ValidationError(
                "La fotografía está archivada."
            )

        if not photo.is_verified:
            raise serializers.ValidationError(
                "La fotografía no se encuentra verificada."
            )

        return attrs


class ArchiveRepairPhotoSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )