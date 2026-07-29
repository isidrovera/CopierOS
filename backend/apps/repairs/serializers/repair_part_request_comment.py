# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models.repair_part_request_comment import RepairPartRequestComment
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class RepairPartRequestCommentListSerializer(serializers.ModelSerializer):
    request_code = serializers.CharField(
        source="request.code",
        read_only=True,
    )
    comment_type_name = serializers.CharField(
        source="get_comment_type_display",
        read_only=True,
    )
    author_name = serializers.CharField(
        source="author.full_name",
        read_only=True,
    )
    mentioned_user_names = serializers.SerializerMethodField()
    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairPartRequestComment
        fields = (
            "id",
            "request",
            "request_code",
            "item",
            "parent",
            "comment_type",
            "comment_type_name",
            "author",
            "author_name",
            "text",
            "is_internal",
            "mentioned_users",
            "mentioned_user_names",
            "is_archived",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_mentioned_user_names(self, obj):
        return [user.full_name for user in obj.mentioned_users.all()]


class RepairPartRequestCommentDetailSerializer(
    RepairPartRequestCommentListSerializer
):
    pass


class RepairPartRequestCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairPartRequestComment
        fields = (
            "request",
            "item",
            "parent",
            "comment_type",
            "text",
            "is_internal",
            "mentioned_users",
        )

    def create(self, validated_data):
        actor = get_authenticated_user(self)
        mentioned_users = validated_data.pop("mentioned_users", [])

        instance = RepairPartRequestComment(
            author=actor,
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            instance.save()
            instance.mentioned_users.set(mentioned_users)
        except DjangoValidationError as exception:
            raise serializers.ValidationError(
                convert_django_validation_error(exception)
            ) from exception

        return instance


class ArchiveRepairPartRequestCommentSerializer(serializers.Serializer):
    reason = serializers.CharField()
