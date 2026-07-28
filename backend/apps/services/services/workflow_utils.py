# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError


def authenticated_user(user):
    if user and getattr(user, "is_authenticated", False):
        return user
    return None


def set_audit(instance, user, creating=False):
    user = authenticated_user(user)

    if not user:
        return instance

    if creating and hasattr(instance, "created_by_id"):
        instance.created_by = user

    if hasattr(instance, "updated_by_id"):
        instance.updated_by = user

    return instance


def save_validated(instance, user=None, creating=False):
    set_audit(
        instance=instance,
        user=user,
        creating=creating,
    )
    instance.full_clean()
    instance.save()
    return instance


def model_field_names(model):
    return {
        field.name
        for field in model._meta.get_fields()
        if getattr(field, "concrete", False)
    }


def copy_existing_fields(source, destination_model, field_names):
    destination_fields = model_field_names(destination_model)
    values = {}

    for field_name in field_names:
        if (
            field_name in destination_fields
            and hasattr(source, field_name)
        ):
            values[field_name] = getattr(
                source,
                field_name,
            )

    return values


def require(condition, message, field=None):
    if condition:
        return

    if field:
        raise ValidationError({field: message})

    raise ValidationError(message)
