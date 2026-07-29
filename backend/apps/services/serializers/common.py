# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from rest_framework import serializers


def convert_django_validation_error(exc):
    """
    Convierte un ValidationError de Django en un formato
    compatible con Django REST Framework.
    """

    if hasattr(exc, "message_dict"):
        return exc.message_dict

    if hasattr(exc, "messages"):
        return {
            "detail": exc.messages,
        }

    return {
        "detail": str(exc),
    }


def get_authenticated_user(serializer):
    """
    Obtiene el usuario autenticado desde el contexto
    del serializer.
    """

    request = serializer.context.get("request")

    if (
        request
        and getattr(request, "user", None)
        and request.user.is_authenticated
    ):
        return request.user

    return None


def raise_drf_validation_error(exc):
    """
    Convierte y lanza un ValidationError de Django
    como ValidationError de DRF.
    """

    if not isinstance(exc, DjangoValidationError):
        raise exc

    raise serializers.ValidationError(
        convert_django_validation_error(exc)
    ) from exc