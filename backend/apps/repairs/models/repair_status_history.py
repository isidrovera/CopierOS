# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RepairBaseModel
from .repair import Repair


class RepairStatusHistory(RepairBaseModel):
    """
    Historial de cambios de estado de una reparación.

    Cada registro conserva:

    - Estado anterior.
    - Estado nuevo.
    - Usuario responsable.
    - Fecha del cambio.
    - Motivo y observaciones.
    - Tiempo transcurrido en el estado anterior.
    """

    repair = models.ForeignKey(
        Repair,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="Reparación",
    )

    previous_status = models.CharField(
        max_length=30,
        choices=Repair.Status.choices,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Estado anterior",
        help_text=(
            "Puede estar vacío cuando corresponde al "
            "registro inicial de la reparación."
        ),
    )

    new_status = models.CharField(
        max_length=30,
        choices=Repair.Status.choices,
        db_index=True,
        verbose_name="Nuevo estado",
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_status_changes",
        verbose_name="Cambiado por",
    )

    changed_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha del cambio",
    )

    previous_status_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio del estado anterior",
    )

    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración en minutos",
        help_text=(
            "Tiempo que la reparación permaneció "
            "en el estado anterior."
        ),
    )

    reason = models.TextField(
        blank=True,
        verbose_name="Motivo del cambio",
    )

    observations = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    changed_automatically = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Cambio automático",
        help_text=(
            "Indica si el cambio fue realizado automáticamente "
            "por una regla del sistema."
        ),
    )

    source = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Origen del cambio",
        help_text=(
            "Ejemplo: reparación, asignación, prueba, cierre, "
            "inventario o proceso automático."
        ),
    )

    class Meta:
        verbose_name = "Historial de estado de reparación"
        verbose_name_plural = (
            "Historiales de estados de reparaciones"
        )
        ordering = (
            "-changed_at",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "repair",
                    "changed_at",
                ],
                name="repair_status_date_idx",
            ),
            models.Index(
                fields=[
                    "repair",
                    "new_status",
                ],
                name="repair_status_new_idx",
            ),
            models.Index(
                fields=[
                    "changed_by",
                    "changed_at",
                ],
                name="repair_status_user_idx",
            ),
            models.Index(
                fields=[
                    "changed_automatically",
                    "changed_at",
                ],
                name="repair_status_auto_idx",
            ),
        ]

    def __str__(self):
        previous_status = (
            self.get_previous_status_display()
            if self.previous_status
            else "Inicio"
        )

        return (
            f"{self.repair.code}: "
            f"{previous_status} → "
            f"{self.get_new_status_display()}"
        )

    def clean(self):
        """
        Normaliza y valida el historial de estado.
        """

        super().clean()

        self.reason = str(
            self.reason or ""
        ).strip()

        self.observations = str(
            self.observations or ""
        ).strip()

        self.source = str(
            self.source or ""
        ).strip().lower()

        if not self.repair_id:
            raise ValidationError(
                {
                    "repair": (
                        "La reparación es obligatoria."
                    ),
                }
            )

        if not self.new_status:
            raise ValidationError(
                {
                    "new_status": (
                        "El nuevo estado es obligatorio."
                    ),
                }
            )

        if (
            self.previous_status
            and self.previous_status == self.new_status
        ):
            raise ValidationError(
                {
                    "new_status": (
                        "El nuevo estado debe ser diferente "
                        "del estado anterior."
                    ),
                }
            )

        if (
            self.previous_status_started_at
            and self.changed_at
            and self.previous_status_started_at
            > self.changed_at
        ):
            raise ValidationError(
                {
                    "previous_status_started_at": (
                        "El inicio del estado anterior no puede "
                        "ser posterior a la fecha del cambio."
                    ),
                }
            )

        if (
            self.duration_minutes is not None
            and not self.previous_status
        ):
            raise ValidationError(
                {
                    "duration_minutes": (
                        "No corresponde registrar duración "
                        "cuando no existe un estado anterior."
                    ),
                }
            )

        if (
            self.changed_automatically
            and not self.source
        ):
            raise ValidationError(
                {
                    "source": (
                        "Debe indicar el origen del cambio automático."
                    ),
                }
            )

    def calculate_duration(self):
        """
        Calcula la duración del estado anterior en minutos.
        """

        if (
            not self.previous_status_started_at
            or not self.changed_at
        ):
            self.duration_minutes = None
            return None

        duration = (
            self.changed_at
            - self.previous_status_started_at
        )

        total_minutes = max(
            int(
                duration.total_seconds() // 60
            ),
            0,
        )

        self.duration_minutes = total_minutes

        return total_minutes

    def save(self, *args, **kwargs):
        """
        Normaliza, calcula duración y valida antes de guardar.
        """

        self.reason = str(
            self.reason or ""
        ).strip()

        self.observations = str(
            self.observations or ""
        ).strip()

        self.source = str(
            self.source or ""
        ).strip().lower()

        if self.previous_status_started_at:
            self.calculate_duration()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )