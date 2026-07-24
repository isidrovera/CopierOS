# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from rest_framework import serializers


def convert_django_validation_error(exc):
    """
    Convierte un ValidationError de Django en un formato
    compatible con Django REST Framework.

    Permite conservar los errores asociados a campos específicos
    cuando el modelo utiliza full_clean().
    """

    if hasattr(
        exc,
        "message_dict",
    ):
        return exc.message_dict

    if hasattr(
        exc,
        "messages",
    ):
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

    Retorna None cuando:

    - No existe request en el contexto.
    - El usuario no está autenticado.
    """

    request = serializer.context.get(
        "request"
    )

    if (
        request
        and request.user
        and request.user.is_authenticated
    ):
        return request.user

    return None


def raise_drf_validation_error(exc):
    """
    Convierte y lanza directamente un ValidationError
    de Django como ValidationError de DRF.

    Esta función reduce la repetición en los métodos
    create() y update() de los serializers.
    """

    if not isinstance(
        exc,
        DjangoValidationError,
    ):
        raise exc

    raise serializers.ValidationError(
        convert_django_validation_error(
            exc
        )
    ) from exc