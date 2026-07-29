# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models.repair_part_request_attachment import RepairPartRequestAttachment
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class RepairPartRequestAttachmentListSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="request.code",
        read_only=True,
    )
    attachment_type_name = serializers.CharField(
        source="get_attachment_type_display",
        read_only=True,
    )
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.full_name",
        read_only=True,
    )
    file_url = serializers.SerializerMethodField()
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartRequestAttachment
        fields = (
            "id",
            "request",
            "request_code",
            "item",
            "attachment_type",
            "attachment_type_name",
            "file",
            "file_url",
            "original_filename",
            "title",
            "description",
            "file_size",
            "uploaded_by",
            "uploaded_by_name",
            "is_archived",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_file_url(self, obj):
        if not obj.file:
            return None

        try:
            url = obj.file.url
        except (AttributeError, ValueError):
            return None

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(url)

        return url


class RepairPartRequestAttachmentDetailSerializer(
    RepairPartRequestAttachmentListSerializer
):
    pass


class RepairPartRequestAttachmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairPartRequestAttachment
        fields = (
            "request",
            "item",
            "attachment_type",
            "file",
            "title",
            "description",
        )

    def create(self, validated_data):
        actor = get_authenticated_user(self)
        instance = RepairPartRequestAttachment(
            uploaded_by=actor,
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            instance.save()
        except DjangoValidationError as exception:
            raise serializers.ValidationError(
                convert_django_validation_error(exception)
            ) from exception

        return instance


class ArchiveRepairPartRequestAttachmentSerializer(serializers.Serializer):
    reason = serializers.CharField()
