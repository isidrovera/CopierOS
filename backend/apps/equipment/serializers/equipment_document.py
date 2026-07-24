# -*- coding: utf-8 -*-
import os

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers

from ..models import EquipmentDocument
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class EquipmentDocumentListSerializer(
    serializers.ModelSerializer
):
    """
    Serializer reducido para listar documentos
    relacionados con equipos.
    """

    equipment_internal_code = serializers.CharField(
        source="equipment.internal_code",
        read_only=True,
    )

    equipment_serial_number = serializers.CharField(
        source="equipment.serial_number",
        read_only=True,
    )

    equipment_model_name = serializers.CharField(
        source="equipment.equipment_model.name",
        read_only=True,
    )

    equipment_brand_name = serializers.CharField(
        source="equipment.equipment_model.brand.name",
        read_only=True,
    )

    document_type_name = serializers.CharField(
        source="get_document_type_display",
        read_only=True,
    )

    reference_type_name = serializers.CharField(
        source="get_reference_type_display",
        read_only=True,
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
        model = EquipmentDocument

        fields = (
            "id",
            "equipment",
            "equipment_internal_code",
            "equipment_serial_number",
            "equipment_model_name",
            "equipment_brand_name",
            "document_type",
            "document_type_name",
            "title",
            "document_number",
            "document_date",
            "expiration_date",
            "file",
            "original_filename",
            "file_extension",
            "file_size",
            "reference_type",
            "reference_type_name",
            "reference_number",
            "uploaded_by",
            "uploaded_by_name",
            "is_primary",
            "is_confidential",
            "is_verified",
            "verified_by",
            "verified_by_name",
            "verified_at",
            "is_active",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class EquipmentDocumentDetailSerializer(
    serializers.ModelSerializer
):
    """
    Serializer completo de un documento relacionado
    con una máquina.
    """

    equipment_internal_code = serializers.CharField(
        source="equipment.internal_code",
        read_only=True,
    )

    equipment_serial_number = serializers.CharField(
        source="equipment.serial_number",
        read_only=True,
    )

    equipment_model_name = serializers.CharField(
        source="equipment.equipment_model.name",
        read_only=True,
    )

    equipment_model_code = serializers.CharField(
        source="equipment.equipment_model.code",
        read_only=True,
    )

    equipment_brand_name = serializers.CharField(
        source="equipment.equipment_model.brand.name",
        read_only=True,
    )

    document_type_name = serializers.CharField(
        source="get_document_type_display",
        read_only=True,
    )

    reference_type_name = serializers.CharField(
        source="get_reference_type_display",
        read_only=True,
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
        model = EquipmentDocument

        fields = (
            "id",
            "equipment",
            "equipment_internal_code",
            "equipment_serial_number",
            "equipment_model_name",
            "equipment_model_code",
            "equipment_brand_name",
            "document_type",
            "document_type_name",
            "title",
            "document_number",
            "document_date",
            "expiration_date",
            "file",
            "original_filename",
            "file_extension",
            "file_size",
            "reference_type",
            "reference_type_name",
            "reference_id",
            "reference_number",
            "uploaded_by",
            "uploaded_by_name",
            "is_primary",
            "is_confidential",
            "is_verified",
            "verified_by",
            "verified_by_name",
            "verified_at",
            "description",
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
            "equipment_internal_code",
            "equipment_serial_number",
            "equipment_model_name",
            "equipment_model_code",
            "equipment_brand_name",
            "document_type_name",
            "reference_type_name",
            "original_filename",
            "file_extension",
            "file_size",
            "uploaded_by_name",
            "verified_by_name",
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


class EquipmentDocumentCreateUpdateSerializer(
    serializers.ModelSerializer
):
    """
    Creación y modificación de documentos de equipos.
    """

    class Meta:
        model = EquipmentDocument

        fields = (
            "equipment",
            "document_type",
            "title",
            "document_number",
            "document_date",
            "expiration_date",
            "file",
            "reference_type",
            "reference_id",
            "reference_number",
            "uploaded_by",
            "is_primary",
            "is_confidential",
            "is_verified",
            "verified_by",
            "verified_at",
            "description",
            "notes",
            "is_active",
        )

        extra_kwargs = {
            "file": {
                "required": False,
            },
        }

    def validate_equipment(self, value):
        """
        Impide asociar documentos a equipos archivados.
        """

        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes registrar documentos en un equipo archivado."
            )

        return value

    def validate_title(self, value):
        title = str(
            value or ""
        ).strip()

        if not title:
            raise serializers.ValidationError(
                "El título del documento es obligatorio."
            )

        return title

    def validate_document_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_reference_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_description(self, value):
        return str(
            value or ""
        ).strip()

    def validate_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate_file(self, value):
        """
        Valida extensión y tamaño del archivo.

        Se admiten documentos e imágenes habituales del módulo.
        """

        if value is None:
            return value

        allowed_extensions = {
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
        }

        filename = str(
            getattr(
                value,
                "name",
                "",
            )
            or ""
        )

        extension = os.path.splitext(
            filename
        )[1].lower()

        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                (
                    "Formato de archivo no permitido. "
                    "Se admiten PDF, JPG, JPEG, PNG, WEBP, "
                    "DOC, DOCX, XLS y XLSX."
                )
            )

        max_size = 20 * 1024 * 1024

        file_size = getattr(
            value,
            "size",
            0,
        )

        if file_size and file_size > max_size:
            raise serializers.ValidationError(
                "El archivo no puede superar los 20 MB."
            )

        return value

    def validate(self, attrs):
        """
        Valida fechas, referencias, archivo, verificación
        y condición de documento principal.
        """

        instance = self.instance

        values = {}

        if instance:
            for field in self.Meta.fields:
                values[field] = getattr(
                    instance,
                    field,
                    None,
                )

        values.update(attrs)

        equipment = values.get(
            "equipment"
        )

        document_type = values.get(
            "document_type"
        )

        file = values.get(
            "file"
        )

        document_date = values.get(
            "document_date"
        )

        expiration_date = values.get(
            "expiration_date"
        )

        reference_type = values.get(
            "reference_type"
        )

        reference_id = values.get(
            "reference_id"
        )

        reference_number = str(
            values.get(
                "reference_number",
                "",
            )
            or ""
        ).strip()

        is_primary = values.get(
            "is_primary",
            False,
        )

        is_verified = values.get(
            "is_verified",
            False,
        )

        verified_by = values.get(
            "verified_by"
        )

        verified_at = values.get(
            "verified_at"
        )

        if not equipment:
            raise serializers.ValidationError(
                {
                    "equipment": (
                        "Debes seleccionar el equipo relacionado."
                    )
                }
            )

        if not instance and not file:
            raise serializers.ValidationError(
                {
                    "file": (
                        "Debes seleccionar el archivo del documento."
                    )
                }
            )

        if (
            instance
            and not file
            and not instance.file
        ):
            raise serializers.ValidationError(
                {
                    "file": (
                        "Debes seleccionar el archivo del documento."
                    )
                }
            )

        if (
            document_date
            and expiration_date
            and expiration_date < document_date
        ):
            raise serializers.ValidationError(
                {
                    "expiration_date": (
                        "La fecha de vencimiento no puede ser "
                        "anterior a la fecha del documento."
                    )
                }
            )

        if (
            reference_type
            != EquipmentDocument.ReferenceType.NONE
            and not reference_id
            and not reference_number
        ):
            raise serializers.ValidationError(
                {
                    "reference_number": (
                        "Debes indicar el ID o número del proceso "
                        "relacionado."
                    )
                }
            )

        if (
            reference_type
            == EquipmentDocument.ReferenceType.NONE
            and reference_id
        ):
            raise serializers.ValidationError(
                {
                    "reference_type": (
                        "Debes seleccionar el tipo de proceso "
                        "antes de registrar un ID relacionado."
                    )
                }
            )

        if (
            reference_type
            == EquipmentDocument.ReferenceType.NONE
            and reference_number
        ):
            raise serializers.ValidationError(
                {
                    "reference_type": (
                        "Debes seleccionar el tipo de proceso "
                        "antes de registrar un número relacionado."
                    )
                }
            )

        if is_verified and not verified_by:
            actor = get_authenticated_user(
                self
            )

            if actor:
                attrs["verified_by"] = actor
                verified_by = actor

        if is_verified and not verified_at:
            from django.utils import timezone

            attrs["verified_at"] = timezone.now()
            verified_at = attrs["verified_at"]

        if (
            not is_verified
            and verified_by
        ):
            raise serializers.ValidationError(
                {
                    "verified_by": (
                        "No puedes indicar un verificador si "
                        "el documento no está marcado como verificado."
                    )
                }
            )

        if (
            not is_verified
            and verified_at
        ):
            raise serializers.ValidationError(
                {
                    "verified_at": (
                        "No puedes indicar una fecha de verificación "
                        "si el documento no está marcado como verificado."
                    )
                }
            )

        if (
            is_primary
            and equipment
            and document_type
        ):
            queryset = EquipmentDocument.objects.filter(
                equipment=equipment,
                document_type=document_type,
                is_primary=True,
                archived_at__isnull=True,
            )

            if instance:
                queryset = queryset.exclude(
                    pk=instance.pk,
                )

            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "is_primary": (
                            "Ya existe un documento principal activo "
                            "de este tipo para el equipo."
                        )
                    }
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """
        Crea el documento registrando auditoría.
        """

        actor = get_authenticated_user(
            self
        )

        if (
            not validated_data.get(
                "uploaded_by"
            )
            and actor
        ):
            validated_data[
                "uploaded_by"
            ] = actor

        document = EquipmentDocument(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            document.full_clean()
            document.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return document

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        """
        Actualiza el documento registrando auditoría.
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


class VerifyEquipmentDocumentSerializer(
    serializers.Serializer
):
    """
    Datos para verificar un documento.
    """

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=3000,
    )


class RemoveEquipmentDocumentVerificationSerializer(
    serializers.Serializer
):
    """
    Datos para retirar la verificación de un documento.
    """

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=3000,
    )


class ArchiveEquipmentDocumentSerializer(
    serializers.Serializer
):
    """
    Datos requeridos para archivar un documento.
    """

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )