# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

class MonitoringModelSerializer(serializers.ModelSerializer):
    def _save_instance(self, instance):
        try:
            instance.full_clean()
            instance.save()
        except DjangoValidationError as exc:
            detail = getattr(exc, "message_dict", None) or {"detail": exc.messages}
            raise serializers.ValidationError(detail) from exc
        return instance

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        return self._save_instance(instance)

    def update(self, instance, validated_data):
        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)
        return self._save_instance(instance)

class ArchiveActionSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default="")
