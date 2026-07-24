# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from rest_framework import status
from rest_framework.response import Response


def convert_django_validation_error(
    exception,
):
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


def django_validation_error_response(
    exception,
):
    return Response(
        convert_django_validation_error(
            exception
        ),
        status=status.HTTP_400_BAD_REQUEST,
    )


def execute_service_action(
    *,
    service,
    success_serializer,
    serializer_context=None,
    **service_kwargs,
):
    try:
        instance = service(
            **service_kwargs
        )
    except DjangoValidationError as exception:
        return django_validation_error_response(
            exception
        )

    serializer = success_serializer(
        instance,
        context=serializer_context or {},
    )

    return Response(
        serializer.data,
        status=status.HTTP_200_OK,
    )


def get_boolean_query_param(
    request,
    parameter_name,
    default=None,
):
    raw_value = request.query_params.get(
        parameter_name
    )

    if raw_value is None:
        return default

    normalized_value = str(
        raw_value
    ).strip().lower()

    if normalized_value in {
        "1",
        "true",
        "yes",
        "si",
        "sí",
    }:
        return True

    if normalized_value in {
        "0",
        "false",
        "no",
    }:
        return False

    return default


def get_authenticated_actor(
    request,
):
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