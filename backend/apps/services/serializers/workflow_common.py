# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


def user_display(user):
    if not user:
        return None

    full_name = str(user.get_full_name() or "").strip()

    return (
        full_name
        or getattr(user, "email", "")
        or user.get_username()
    )


def absolute_file_url(serializer, file_field):
    if not file_field:
        return None

    try:
        url = file_field.url
    except (AttributeError, ValueError):
        return None

    request = serializer.context.get("request")

    if request:
        return request.build_absolute_uri(url)

    return url


class FullCleanModelSerializerMixin:
    """
    Aplica auditoría y ejecuta full_clean() antes de guardar.
    Los errores de modelos Django se convierten a errores DRF.
    """

    audit_created_by = True
    audit_updated_by = True

    def _authenticated_user(self):
        return get_authenticated_user(self)

    def _apply_create_audit(self, instance):
        user = self._authenticated_user()

        if not user:
            return

        if (
            self.audit_created_by
            and hasattr(instance, "created_by_id")
            and not instance.created_by_id
        ):
            instance.created_by = user

        if (
            self.audit_updated_by
            and hasattr(instance, "updated_by_id")
        ):
            instance.updated_by = user

    def _apply_update_audit(self, instance):
        user = self._authenticated_user()

        if (
            user
            and self.audit_updated_by
            and hasattr(instance, "updated_by_id")
        ):
            instance.updated_by = user

    def _save_instance(self, instance):
        try:
            instance.full_clean()
            instance.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(exc)
            ) from exc

        return instance

    @transaction.atomic
    def create(self, validated_data):
        many_to_many = {}

        for field in list(validated_data):
            model_field = self.Meta.model._meta.get_field(field)

            if model_field.many_to_many:
                many_to_many[field] = validated_data.pop(field)

        instance = self.Meta.model(**validated_data)
        self._apply_create_audit(instance)
        self._save_instance(instance)

        for field, values in many_to_many.items():
            getattr(instance, field).set(values)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        many_to_many = {}

        for field, value in list(validated_data.items()):
            model_field = self.Meta.model._meta.get_field(field)

            if model_field.many_to_many:
                many_to_many[field] = validated_data.pop(field)
                continue

            setattr(instance, field, value)

        self._apply_update_audit(instance)
        self._save_instance(instance)

        for field, values in many_to_many.items():
            getattr(instance, field).set(values)

        return instance


class UserDisplayMixin:
    user_display = staticmethod(user_display)
