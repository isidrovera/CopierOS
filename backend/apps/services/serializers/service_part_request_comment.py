# -*- coding: utf-8 -*-
from django.utils import timezone
from rest_framework import serializers

from apps.services.models import ServicePartRequestComment

from .workflow_common import (
    FullCleanModelSerializerMixin,
    UserDisplayMixin,
)


class ServicePartRequestCommentSerializer(
    FullCleanModelSerializerMixin,
    UserDisplayMixin,
    serializers.ModelSerializer,
):
    comment_type_display = serializers.CharField(
        source="get_comment_type_display",
        read_only=True,
    )
    author_display = serializers.SerializerMethodField()
    mentioned_users_display = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServicePartRequestComment
        fields = "__all__"
        read_only_fields = (
            "author",
            "is_edited",
            "edited_at",
            "created_by",
            "updated_by",
            "archived_by",
            "archived_at",
            "archived_reason",
        )

    def get_author_display(self, obj):
        return self.user_display(obj.author)

    def get_mentioned_users_display(self, obj):
        return [
            {
                "id": str(user.pk),
                "name": self.user_display(user),
            }
            for user in obj.mentioned_users.all()
        ]

    def get_replies_count(self, obj):
        return obj.replies.filter(
            archived_at__isnull=True,
        ).count()

    def create(self, validated_data):
        user = self._authenticated_user()

        if user:
            validated_data["author"] = user

        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.is_edited = True
        instance.edited_at = timezone.now()

        return super().update(instance, validated_data)
