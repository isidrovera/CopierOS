# -*- coding: utf-8 -*-
from django.utils import timezone
from rest_framework import serializers

from apps.rentals.models import RentalDocument


class RentalDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer principal para documentos del módulo rentals.
    """

    document_type_display = serializers.CharField(
        source="get_document_type_display",
        read_only=True,
    )

    rental_equipment_display = (
        serializers.SerializerMethodField()
    )

    preparation_code = serializers.SerializerMethodField()
    contract_code = serializers.SerializerMethodField()
    assignment_code = serializers.SerializerMethodField()
    installation_code = serializers.SerializerMethodField()
    removal_code = serializers.SerializerMethodField()
    replacement_code = serializers.SerializerMethodField()

    file_url = serializers.SerializerMethodField()

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    archived_by_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RentalDocument
        fields = [
            "id",
            "document_type",
            "document_type_display",
            "title",
            "document_number",
            "rental_equipment",
            "rental_equipment_display",
            "preparation",
            "preparation_code",
            "contract",
            "contract_code",
            "assignment",
            "assignment_code",
            "installation",
            "installation_code",
            "removal",
            "removal_code",
            "replacement",
            "replacement_code",
            "file",
            "file_url",
            "description",
            "issued_date",
            "is_verified",
            "verified_at",
            "notes",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_at",
            "archived_by",
            "archived_by_name",
            "archived_reason",
            "is_archived",
        ]
        read_only_fields = [
            "id",
            "verified_at",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        ]

    def get_rental_equipment_display(self, obj):
        if not obj.rental_equipment:
            return ""

        return str(obj.rental_equipment)

    def get_preparation_code(self, obj):
        if not obj.preparation:
            return ""

        return obj.preparation.code

    def get_contract_code(self, obj):
        if not obj.contract:
            return ""

        return obj.contract.code

    def get_assignment_code(self, obj):
        if not obj.assignment:
            return ""

        return obj.assignment.code

    def get_installation_code(self, obj):
        if not obj.installation:
            return ""

        return obj.installation.code

    def get_removal_code(self, obj):
        if not obj.removal:
            return ""

        return obj.removal.code

    def get_replacement_code(self, obj):
        if not obj.replacement:
            return ""

        return obj.replacement.code

    def get_file_url(self, obj):
        if not obj.file:
            return ""

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(
                obj.file.url
            )

        return obj.file.url

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return ""

        return (
            obj.created_by.get_full_name()
            or obj.created_by.username
        )

    def get_updated_by_name(self, obj):
        if not obj.updated_by:
            return ""

        return (
            obj.updated_by.get_full_name()
            or obj.updated_by.username
        )

    def get_archived_by_name(self, obj):
        if not obj.archived_by:
            return ""

        return (
            obj.archived_by.get_full_name()
            or obj.archived_by.username
        )

    def validate_title(self, value):
        title = str(
            value or ""
        ).strip()

        if not title:
            raise serializers.ValidationError(
                "El título del documento es obligatorio."
            )

        return title

    def validate_file(self, value):
        if not value:
            raise serializers.ValidationError(
                "El archivo es obligatorio."
            )

        max_size = 20 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(
                "El archivo no puede superar los 20 MB."
            )

        return value

    def validate(self, attrs):
        instance = self.instance

        rental_equipment = attrs.get(
            "rental_equipment",
            getattr(
                instance,
                "rental_equipment",
                None,
            ),
        )

        preparation = attrs.get(
            "preparation",
            getattr(
                instance,
                "preparation",
                None,
            ),
        )

        contract = attrs.get(
            "contract",
            getattr(
                instance,
                "contract",
                None,
            ),
        )

        assignment = attrs.get(
            "assignment",
            getattr(
                instance,
                "assignment",
                None,
            ),
        )

        installation = attrs.get(
            "installation",
            getattr(
                instance,
                "installation",
                None,
            ),
        )

        removal = attrs.get(
            "removal",
            getattr(
                instance,
                "removal",
                None,
            ),
        )

        replacement = attrs.get(
            "replacement",
            getattr(
                instance,
                "replacement",
                None,
            ),
        )

        is_verified = attrs.get(
            "is_verified",
            getattr(
                instance,
                "is_verified",
                False,
            ),
        )

        related_records = [
            rental_equipment,
            preparation,
            contract,
            assignment,
            installation,
            removal,
            replacement,
        ]

        if not any(related_records):
            raise serializers.ValidationError(
                {
                    "rental_equipment": (
                        "El documento debe relacionarse con "
                        "un equipo o proceso de alquiler."
                    ),
                }
            )

        if (
            preparation
            and rental_equipment
            and preparation.rental_equipment_id
            != rental_equipment.id
        ):
            raise serializers.ValidationError(
                {
                    "preparation": (
                        "La preparación no pertenece "
                        "al equipo seleccionado."
                    ),
                }
            )

        if (
            assignment
            and rental_equipment
            and assignment.rental_equipment_id
            != rental_equipment.id
        ):
            raise serializers.ValidationError(
                {
                    "assignment": (
                        "La asignación no pertenece "
                        "al equipo seleccionado."
                    ),
                }
            )

        if (
            installation
            and assignment
            and installation.rental_assignment_id
            != assignment.id
        ):
            raise serializers.ValidationError(
                {
                    "installation": (
                        "La instalación no pertenece "
                        "a la asignación seleccionada."
                    ),
                }
            )

        if (
            removal
            and assignment
            and removal.rental_assignment_id
            != assignment.id
        ):
            raise serializers.ValidationError(
                {
                    "removal": (
                        "El retiro no pertenece "
                        "a la asignación seleccionada."
                    ),
                }
            )

        if (
            replacement
            and assignment
            and replacement.rental_assignment_id
            != assignment.id
        ):
            raise serializers.ValidationError(
                {
                    "replacement": (
                        "El reemplazo no pertenece "
                        "a la asignación seleccionada."
                    ),
                }
            )

        if is_verified:
            attrs["verified_at"] = (
                getattr(
                    instance,
                    "verified_at",
                    None,
                )
                or timezone.now()
            )
        else:
            attrs["verified_at"] = None

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")

        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(
            validated_data
        )

    def update(self, instance, validated_data):
        request = self.context.get("request")

        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["updated_by"] = user

        return super().update(
            instance,
            validated_data,
        )


class RentalDocumentListSerializer(
    RentalDocumentSerializer
):
    """
    Serializer compacto para listados de documentos.
    """

    class Meta(RentalDocumentSerializer.Meta):
        fields = [
            "id",
            "document_type",
            "document_type_display",
            "title",
            "document_number",
            "rental_equipment",
            "rental_equipment_display",
            "preparation",
            "preparation_code",
            "contract",
            "contract_code",
            "assignment",
            "assignment_code",
            "installation",
            "installation_code",
            "removal",
            "removal_code",
            "replacement",
            "replacement_code",
            "file_url",
            "issued_date",
            "is_verified",
            "verified_at",
            "created_at",
            "archived_at",
            "is_archived",
        ]