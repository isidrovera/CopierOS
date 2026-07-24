# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)


def get_authenticated_user(serializer):
    """
    Obtiene el usuario autenticado desde el contexto
    del serializer.
    """

    request = serializer.context.get(
        "request"
    )

    if not request:
        return None

    user = getattr(
        request,
        "user",
        None,
    )

    if not user:
        return None

    if not user.is_authenticated:
        return None

    return user


def convert_django_validation_error(exception):
    """
    Convierte ValidationError de Django en una estructura
    compatible con los serializers de Django REST Framework.
    """

    if hasattr(
        exception,
        "message_dict",
    ):
        return exception.message_dict

    if hasattr(
        exception,
        "messages",
    ):
        return {
            "detail": exception.messages,
        }

    return {
        "detail": [
            str(exception),
        ],
    }


def validate_model_instance(instance):
    """
    Ejecuta full_clean sobre una instancia y devuelve
    los errores en formato compatible con DRF.
    """

    try:
        instance.full_clean()
    except DjangoValidationError as exception:
        return convert_django_validation_error(
            exception
        )

    return None