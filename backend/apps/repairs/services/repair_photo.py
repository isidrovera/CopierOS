# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import (
    Repair,
    RepairPhoto,
)


def normalize_text(value):
    return str(
        value or ""
    ).strip()


def update_repair_photo_state(
    repair,
    actor=None,
):
    minimum_required = (
        repair.minimum_photos_required
        or 0
    )

    photo_count = (
        RepairPhoto.objects.filter(
            repair=repair,
            archived_at__isnull=True,
            counts_for_minimum=True,
        ).count()
    )

    required_photos = (
        RepairPhoto.objects.filter(
            repair=repair,
            archived_at__isnull=True,
            is_required=True,
        )
    )

    required_photos_completed = not (
        required_photos.filter(
            is_verified=False,
        ).exists()
    )

    minimum_completed = (
        photo_count >= minimum_required
        and required_photos_completed
    )

    if (
        repair.minimum_photos_completed
        != minimum_completed
    ):
        repair.minimum_photos_completed = (
            minimum_completed
        )

        if actor:
            repair.updated_by = actor

        repair.save(
            update_fields=[
                "minimum_photos_completed",
                "updated_by",
                "updated_at",
            ]
        )

    return minimum_completed


def validate_photo_available(
    photo,
):
    if photo.archived_at is not None:
        raise ValidationError(
            "La fotografía está archivada."
        )


@transaction.atomic
def create_repair_photo(
    *,
    repair,
    image,
    actor=None,
    checklist_item=None,
    category=None,
    stage=None,
    title="",
    description="",
    taken_at=None,
    is_required=False,
    counts_for_minimum=True,
    latitude=None,
    longitude=None,
    display_order=0,
):
    repair = (
        Repair.objects
        .select_for_update()
        .get(pk=repair.pk)
    )

    if repair.archived_at is not None:
        raise ValidationError(
            "La reparación está archivada."
        )

    if not repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )

    if not image:
        raise ValidationError(
            {
                "image": (
                    "La fotografía es obligatoria."
                )
            }
        )

    if checklist_item:
        if (
            checklist_item.checklist.repair_id
            != repair.id
        ):
            raise ValidationError(
                {
                    "checklist_item": (
                        "El punto de revisión no pertenece "
                        "a la reparación."
                    )
                }
            )

    if is_required and not counts_for_minimum:
        raise ValidationError(
            {
                "counts_for_minimum": (
                    "Una fotografía obligatoria debe "
                    "contabilizar para el mínimo."
                )
            }
        )

    if latitude is not None:
        if latitude < -90 or latitude > 90:
            raise ValidationError(
                {
                    "latitude": (
                        "La latitud debe estar entre -90 y 90."
                    )
                }
            )

    if longitude is not None:
        if longitude < -180 or longitude > 180:
            raise ValidationError(
                {
                    "longitude": (
                        "La longitud debe estar entre -180 y 180."
                    )
                }
            )

    original_filename = normalize_text(
        getattr(
            image,
            "name",
            "",
        )
    )

    mime_type = normalize_text(
        getattr(
            image,
            "content_type",
            "",
        )
    )

    file_size = getattr(
        image,
        "size",
        None,
    )

    photo = RepairPhoto(
        repair=repair,
        checklist_item=checklist_item,
        image=image,
        original_filename=original_filename,
        category=(
            category
            or RepairPhoto.Category.GENERAL
        ),
        stage=(
            stage
            or RepairPhoto.Stage.DURING
        ),
        title=normalize_text(
            title
        ),
        description=normalize_text(
            description
        ),
        taken_by=actor,
        taken_at=(
            taken_at
            or timezone.now()
        ),
        uploaded_by=actor,
        uploaded_at=timezone.now(),
        is_required=is_required,
        counts_for_minimum=counts_for_minimum,
        latitude=latitude,
        longitude=longitude,
        file_size=file_size,
        mime_type=mime_type,
        display_order=display_order,
        created_by=actor,
        updated_by=actor,
    )

    photo.full_clean()
    photo.save()

    update_repair_photo_state(
        repair,
        actor,
    )

    return photo


@transaction.atomic
def verify_repair_photo(
    *,
    photo,
    actor=None,
    verification_notes="",
):
    photo = (
        RepairPhoto.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=photo.pk)
    )

    validate_photo_available(
        photo
    )

    if photo.is_verified:
        raise ValidationError(
            "La fotografía ya se encuentra verificada."
        )

    photo.is_verified = True
    photo.verified_by = actor
    photo.verified_at = timezone.now()
    photo.verification_notes = normalize_text(
        verification_notes
    )
    photo.updated_by = actor

    photo.full_clean()
    photo.save()

    update_repair_photo_state(
        photo.repair,
        actor,
    )

    return photo


@transaction.atomic
def remove_photo_verification(
    *,
    photo,
    actor=None,
    reason="",
):
    photo = (
        RepairPhoto.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=photo.pk)
    )

    validate_photo_available(
        photo
    )

    if not photo.is_verified:
        raise ValidationError(
            "La fotografía no se encuentra verificada."
        )

    reason_text = normalize_text(
        reason
    )

    photo.is_verified = False
    photo.verified_by = None
    photo.verified_at = None

    if reason_text:
        current_notes = normalize_text(
            photo.verification_notes
        )

        photo.verification_notes = (
            f"{current_notes}\n"
            f"Verificación retirada: {reason_text}"
        ).strip()

    photo.updated_by = actor

    photo.full_clean()
    photo.save()

    update_repair_photo_state(
        photo.repair,
        actor,
    )

    return photo


@transaction.atomic
def archive_repair_photo(
    *,
    photo,
    actor=None,
    reason="",
):
    photo = (
        RepairPhoto.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=photo.pk)
    )

    if photo.archived_at is not None:
        raise ValidationError(
            "La fotografía ya se encuentra archivada."
        )

    repair = photo.repair

    photo.archive(
        user=actor,
        reason=normalize_text(
            reason
        ),
    )

    update_repair_photo_state(
        repair,
        actor,
    )

    return photo


@transaction.atomic
def restore_repair_photo(
    *,
    photo,
    actor=None,
):
    photo = (
        RepairPhoto.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=photo.pk)
    )

    if photo.archived_at is None:
        raise ValidationError(
            "La fotografía no se encuentra archivada."
        )

    if not photo.repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )

    repair = photo.repair

    photo.restore(
        user=actor,
    )

    update_repair_photo_state(
        repair,
        actor,
    )

    return photo