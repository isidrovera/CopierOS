# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.services.models import ServicePartRequestAttachment

from .workflow_common import (
    FullCleanModelSerializerMixin,
    absolute_file_url,
)


class ServicePartRequestAttachmentSerializer(
    FullCleanModelSerializerMixin,
    serializers.ModelSerializer,
):
    attachment_type_display = serializers.CharField(
        source="get_attachment_type_display",
        read_only=True,
    )
    file_url = serializers.SerializerMethodField()
    request_code = serializers.CharField(
        source="request.code",
        read_only=True,
    )
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServicePartRequestAttachment
        fields = "__all__"
        read_only_fields = (
            "original_filename",
            "file_size",
            "uploaded_by",
            "created_by",
            "updated_by",
            "archived_by",
            "archived_at",
            "archived_reason",
        )

    def get_file_url(self, obj):
        return absolute_file_url(self, obj.file)

    def create(self, validated_data):
        user = self._authenticated_user()

        if user:
            validated_data["uploaded_by"] = user

        return super().create(validated_data)
