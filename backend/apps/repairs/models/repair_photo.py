# -*- coding: utf-8 -*-
import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RepairBaseModel
from .repair import Repair
from .repair_checklist import RepairChecklistItem


def repair_photo_path(instance, filename):
    """
    Organiza las fotografías por reparación y categoría.

    Ejemplo:
    repairs/REP-2026-000001/before/uuid.jpg
    """

    extension = os.path.splitext(
        filename
    )[1].lower() or ".jpg"

    repair_code = str(
        instance.repair.code or instance.repair_id
    ).strip()

    category = str(
        instance.category or "other"
    ).strip().lower()

    unique_name = (
        f"{uuid.uuid4().hex}{extension}"
    )

    return (
        f"repairs/{repair_code}/"
        f"{category}/{unique_name}"
    )


class RepairPhoto(RepairBaseModel):
    """
    Evidencia fotográfica de una reparación.

    Permite registrar fotografías:

    - Antes de iniciar la revisión.
    - Durante el desmontaje.
    - De fallas o daños.
    - De componentes retirados.
    - De componentes instalados.
    - Durante la limpieza.
    - Durante las pruebas.
    - Al finalizar la reparación.

    Las fotografías obligatorias se contabilizan para validar
    la cantidad mínima requerida antes del cierre.
    """

    class Category(models.TextChoices):
        BEFORE = (
            "before",
            "Antes de la reparación",
        )
        EXTERNAL_CONDITION = (
            "external_condition",
            "Condición externa",
        )
        SERIAL_PLATE = (
            "serial_plate",
            "Placa y número de serie",
        )
        INITIAL_METER = (
            "initial_meter",
            "Contador inicial",
        )
        DAMAGE = (
            "damage",
            "Daño o falla",
        )
        DISASSEMBLY = (
            "disassembly",
            "Desmontaje",
        )
        DIRTY_CONDITION = (
            "dirty_condition",
            "Condición de suciedad",
        )
        CLEANING = (
            "cleaning",
            "Proceso de limpieza",
        )
        REMOVED_COMPONENT = (
            "removed_component",
            "Componente retirado",
        )
        INSTALLED_COMPONENT = (
            "installed_component",
            "Componente instalado",
        )
        REPAIR_PROCESS = (
            "repair_process",
            "Proceso de reparación",
        )
        TEST = (
            "test",
            "Prueba técnica",
        )
        PRINT_SAMPLE = (
            "print_sample",
            "Muestra de impresión",
        )
        FINAL_METER = (
            "final_meter",
            "Contador final",
        )
        AFTER = (
            "after",
            "Después de la reparación",
        )
        OTHER = (
            "other",
            "Otra evidencia",
        )

    class Stage(models.TextChoices):
        RECEPTION = (
            "reception",
            "Recepción",
        )
        REVIEW = (
            "review",
            "Revisión",
        )
        DIAGNOSIS = (
            "diagnosis",
            "Diagnóstico",
        )
        REPAIR = (
            "repair",
            "Reparación",
        )
        TESTING = (
            "testing",
            "Pruebas",
        )
        COMPLETION = (
            "completion",
            "Finalización",
        )
        DELIVERY = (
            "delivery",
            "Entrega",
        )

    repair = models.ForeignKey(
        Repair,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="Reparación",
    )

    checklist_item = models.ForeignKey(
        RepairChecklistItem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="photos",
        verbose_name="Punto de revisión",
        help_text=(
            "Punto de la lista de revisión relacionado "
            "con esta fotografía."
        ),
    )

    image = models.ImageField(
        upload_to=repair_photo_path,
        verbose_name="Fotografía",
    )

    original_filename = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre original del archivo",
    )

    category = models.CharField(
        max_length=40,
        choices=Category.choices,
        default=Category.OTHER,
        db_index=True,
        verbose_name="Categoría",
    )

    stage = models.CharField(
        max_length=30,
        choices=Stage.choices,
        default=Stage.REVIEW,
        db_index=True,
        verbose_name="Etapa",
    )

    title = models.CharField(
        max_length=180,
        blank=True,
        verbose_name="Título",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    taken_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_photos_taken",
        verbose_name="Tomada por",
    )

    taken_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de la fotografía",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_photos_uploaded",
        verbose_name="Subida por",
    )

    uploaded_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha de carga",
    )

    is_required = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Fotografía obligatoria",
        help_text=(
            "Indica si esta fotografía forma parte "
            "de las evidencias obligatorias."
        ),
    )

    counts_for_minimum = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Contabiliza para el mínimo",
        help_text=(
            "Indica si la fotografía cuenta para alcanzar "
            "la cantidad mínima requerida."
        ),
    )

    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Fotografía verificada",
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_photos_verified",
        verbose_name="Verificada por",
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de verificación",
    )

    verification_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones de verificación",
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Latitud",
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Longitud",
    )

    file_size = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Tamaño del archivo",
    )

    mime_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tipo MIME",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Orden de visualización",
    )

    class Meta:
        verbose_name = "Fotografía de reparación"
        verbose_name_plural = "Fotografías de reparaciones"
        ordering = (
            "display_order",
            "taken_at",
            "created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "repair",
                    "category",
                ],
                name="repair_photo_category_idx",
            ),
            models.Index(
                fields=[
                    "repair",
                    "stage",
                ],
                name="repair_photo_stage_idx",
            ),
            models.Index(
                fields=[
                    "repair",
                    "counts_for_minimum",
                ],
                name="repair_photo_minimum_idx",
            ),
            models.Index(
                fields=[
                    "is_required",
                    "is_verified",
                ],
                name="repair_photo_verify_idx",
            ),
            models.Index(
                fields=[
                    "taken_by",
                    "taken_at",
                ],
                name="repair_photo_user_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.repair.code} - "
            f"{self.get_category_display()}"
        )

    def clean(self):
        """
        Normaliza y valida la evidencia fotográfica.
        """

        super().clean()

        self.original_filename = str(
            self.original_filename or ""
        ).strip()

        self.title = str(
            self.title or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        self.verification_notes = str(
            self.verification_notes or ""
        ).strip()

        self.mime_type = str(
            self.mime_type or ""
        ).strip().lower()

        if not self.repair_id:
            raise ValidationError(
                {
                    "repair": (
                        "La reparación es obligatoria."
                    ),
                }
            )

        if not self.image:
            raise ValidationError(
                {
                    "image": (
                        "La fotografía es obligatoria."
                    ),
                }
            )

        if self.checklist_item_id:
            if (
                self.checklist_item.checklist.repair_id
                != self.repair_id
            ):
                raise ValidationError(
                    {
                        "checklist_item": (
                            "El punto de revisión no pertenece "
                            "a esta reparación."
                        ),
                    }
                )

        if (
            self.is_required
            and not self.counts_for_minimum
        ):
            raise ValidationError(
                {
                    "counts_for_minimum": (
                        "Una fotografía obligatoria debe "
                        "contabilizar para el mínimo requerido."
                    ),
                }
            )

        if self.is_verified:
            if not self.verified_by_id:
                raise ValidationError(
                    {
                        "verified_by": (
                            "Debe indicar quién verificó "
                            "la fotografía."
                        ),
                    }
                )

            if not self.verified_at:
                raise ValidationError(
                    {
                        "verified_at": (
                            "Debe registrar la fecha "
                            "de verificación."
                        ),
                    }
                )

        if not self.is_verified:
            if self.verified_by_id or self.verified_at:
                raise ValidationError(
                    {
                        "is_verified": (
                            "No debe registrar datos de verificación "
                            "si la fotografía no está verificada."
                        ),
                    }
                )

            if self.verification_notes:
                raise ValidationError(
                    {
                        "verification_notes": (
                            "No debe registrar observaciones de "
                            "verificación si no fue verificada."
                        ),
                    }
                )

        if (
            self.verified_at
            and self.verified_at < self.uploaded_at
        ):
            raise ValidationError(
                {
                    "verified_at": (
                        "La fecha de verificación no puede ser "
                        "anterior a la fecha de carga."
                    ),
                }
            )

        if self.latitude is not None:
            if self.latitude < -90 or self.latitude > 90:
                raise ValidationError(
                    {
                        "latitude": (
                            "La latitud debe estar entre -90 y 90."
                        ),
                    }
                )

        if self.longitude is not None:
            if self.longitude < -180 or self.longitude > 180:
                raise ValidationError(
                    {
                        "longitude": (
                            "La longitud debe estar entre -180 y 180."
                        ),
                    }
                )

    def save(self, *args, **kwargs):
        """
        Normaliza, valida y actualiza el control de fotografías.
        """

        self.original_filename = str(
            self.original_filename or ""
        ).strip()

        self.title = str(
            self.title or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        self.verification_notes = str(
            self.verification_notes or ""
        ).strip()

        self.mime_type = str(
            self.mime_type or ""
        ).strip().lower()

        if self.image:
            if not self.original_filename:
                self.original_filename = os.path.basename(
                    self.image.name
                )

            if not self.file_size:
                try:
                    self.file_size = self.image.size
                except (AttributeError, OSError, ValueError):
                    self.file_size = None

        self.full_clean()

        result = super().save(
            *args,
            **kwargs,
        )

        self.update_repair_photo_status()

        return result

    def delete(self, *args, **kwargs):
        """
        Elimina la fotografía y recalcula el mínimo requerido.
        """

        repair = self.repair

        result = super().delete(
            *args,
            **kwargs,
        )

        self.update_repair_photo_status(
            repair=repair,
        )

        return result

    def archive(
        self,
        user=None,
        reason="",
        save=True,
    ):
        """
        Archiva la fotografía y recalcula el mínimo.
        """

        result = super().archive(
            user=user,
            reason=reason,
            save=save,
        )

        self.update_repair_photo_status()

        return result

    def restore(
        self,
        user=None,
        save=True,
    ):
        """
        Restaura la fotografía y recalcula el mínimo.
        """

        result = super().restore(
            user=user,
            save=save,
        )

        self.update_repair_photo_status()

        return result

    def update_repair_photo_status(
        self,
        repair=None,
    ):
        """
        Actualiza el indicador de fotografías mínimas
        completadas en la reparación.
        """

        repair = repair or self.repair

        photo_count = repair.photos.filter(
            archived_at__isnull=True,
            counts_for_minimum=True,
        ).count()

        completed = (
            photo_count
            >= repair.minimum_photos_required
        )

        if (
            repair.minimum_photos_completed
            != completed
        ):
            repair.minimum_photos_completed = completed

            repair.save(
                update_fields=[
                    "minimum_photos_completed",
                    "updated_at",
                ]
            )