# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone

from apps.equipment.models import EquipmentComponent

from .base import ServicesBaseModel
from .service_order import ServiceOrder


class ServiceChecklist(ServicesBaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        IN_PROGRESS = "in_progress", "En proceso"
        COMPLETED = "completed", "Completada"
        CANCELLED = "cancelled", "Cancelada"

    service_order = models.OneToOneField(
        ServiceOrder,
        on_delete=models.CASCADE,
        related_name="checklist",
        verbose_name="Orden de servicio",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_checklists_started",
        verbose_name="Iniciado por",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de inicio",
    )

    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_checklists_completed",
        verbose_name="Completado por",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de finalización",
    )

    observations = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        ordering = (
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "status",
                    "created_at",
                ],
                name="svc_check_status_idx",
            ),
        ]
        verbose_name = "Checklist de servicio"
        verbose_name_plural = "Checklists de servicios"

    def __str__(self):
        return (
            f"{self.service_order.code} · "
            f"{self.get_status_display()}"
        )

    def clean(self):
        super().clean()

        self.observations = str(
            self.observations or "",
        ).strip()

        if self.status == self.Status.COMPLETED:
            if not self.completed_by_id:
                raise ValidationError(
                    {
                        "completed_by": (
                            "Debe registrar quién completó "
                            "el checklist."
                        )
                    }
                )

            if not self.completed_at:
                raise ValidationError(
                    {
                        "completed_at": (
                            "Debe registrar cuándo se completó "
                            "el checklist."
                        )
                    }
                )

            if self.items.filter(
                archived_at__isnull=True,
                is_required=True,
                status=ServiceChecklistItem.Status.PENDING,
            ).exists():
                raise ValidationError(
                    {
                        "status": (
                            "Existen componentes obligatorios "
                            "pendientes."
                        )
                    }
                )

    def save(self, *args, **kwargs):
        now = timezone.now()

        if (
            self.status == self.Status.IN_PROGRESS
            and not self.started_at
        ):
            self.started_at = now

        if (
            self.status == self.Status.COMPLETED
            and not self.completed_at
        ):
            self.completed_at = now

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )


class ServiceChecklistItem(ServicesBaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        OK = "ok", "Correcto"
        OBSERVED = (
            "observed",
            "Regular / observado",
        )
        FAILED = "failed", "Requiere cambio"
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )

    checklist = models.ForeignKey(
        ServiceChecklist,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Checklist",
    )

    source_component = models.ForeignKey(
        EquipmentComponent,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="service_checklist_items",
        verbose_name="Componente del catálogo",
    )

    source_component_id_snapshot = models.UUIDField(
        null=True,
        blank=True,
        verbose_name="ID histórico del componente",
    )

    component_code = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Código del componente",
    )

    component_name = models.CharField(
        max_length=200,
        verbose_name="Nombre del componente",
    )

    component_color = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Color",
    )

    component_type_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Tipo de componente",
    )

    category = models.CharField(
        max_length=30,
        default="component",
        db_index=True,
        verbose_name="Categoría",
    )

    position = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Posición",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    is_required = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Obligatorio",
    )

    observation = models.TextField(
        blank=True,
        verbose_name="Observación",
    )

    consumable_present = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Consumible presente",
    )

    consumable_level_percent = (
        models.PositiveSmallIntegerField(
            null=True,
            blank=True,
            validators=[
                MinValueValidator(0),
                MaxValueValidator(100),
            ],
            verbose_name="Nivel del consumible",
        )
    )

    checked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_checklist_items_checked",
        verbose_name="Revisado por",
    )

    checked_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de revisión",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Orden de visualización",
    )

    class Meta:
        ordering = (
            "display_order",
            "component_name",
        )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "checklist",
                    "component_code",
                    "position",
                ],
                name="unique_svc_check_component",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "checklist",
                    "status",
                ],
                name="svc_check_item_st_idx",
            ),
            models.Index(
                fields=[
                    "category",
                    "status",
                ],
                name="svc_check_cat_st_idx",
            ),
        ]
        verbose_name = "Ítem de checklist"
        verbose_name_plural = "Ítems de checklist"

    def __str__(self):
        return (
            f"{self.checklist.service_order.code} · "
            f"{self.component_name}"
        )

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    @property
    def has_active_part_requests(self):
        return self.part_request_items.filter(
            archived_at__isnull=True,
        ).exists()

    def clean(self):
        super().clean()

        self.component_code = self._clean_text(
            self.component_code,
        ).upper()

        self.component_name = self._clean_text(
            self.component_name,
        )

        self.component_color = self._clean_text(
            self.component_color,
        ).lower()

        self.component_type_name = self._clean_text(
            self.component_type_name,
        )

        self.category = (
            self._clean_text(
                self.category,
            ).lower()
            or "component"
        )

        self.position = self._clean_text(
            self.position,
        ).lower()

        self.observation = self._clean_text(
            self.observation,
        )

        if not self.component_code:
            raise ValidationError(
                {
                    "component_code": (
                        "El código es obligatorio."
                    )
                }
            )

        if not self.component_name:
            raise ValidationError(
                {
                    "component_name": (
                        "El nombre es obligatorio."
                    )
                }
            )

        if (
            self.status != self.Status.PENDING
            and not self.checked_by_id
        ):
            raise ValidationError(
                {
                    "checked_by": (
                        "Debe registrar el técnico "
                        "que revisó el componente."
                    )
                }
            )

        if (
            self.status != self.Status.PENDING
            and not self.checked_at
        ):
            raise ValidationError(
                {
                    "checked_at": (
                        "Debe registrar la fecha "
                        "de revisión."
                    )
                }
            )

        if (
            self.status == self.Status.FAILED
            and not self.observation
        ):
            raise ValidationError(
                {
                    "observation": (
                        "Debe describir la falla."
                    )
                }
            )

        if (
            self.status != self.Status.FAILED
            and self.pk
            and self.has_active_part_requests
        ):
            raise ValidationError(
                {
                    "status": (
                        "No puede retirar el estado "
                        "'Requiere cambio' mientras existan "
                        "artículos activos vinculados al pedido."
                    )
                }
            )

        if (
            self.consumable_present is False
            and self.consumable_level_percent is not None
        ):
            raise ValidationError(
                {
                    "consumable_level_percent": (
                        "Un consumible no presente no puede "
                        "tener porcentaje registrado."
                    )
                }
            )

    def save(self, *args, **kwargs):
        if self.source_component_id:
            component = self.source_component

            self.source_component_id_snapshot = (
                self.source_component_id_snapshot
                or component.id
            )

            self.component_code = (
                self.component_code
                or component.code
            )

            self.component_name = (
                self.component_name
                or component.name
            )

            self.component_color = (
                self.component_color
                or component.color
            )

            self.component_type_name = (
                self.component_type_name
                or str(component.component_type)
            )

        if (
            self.status != self.Status.PENDING
            and not self.checked_at
        ):
            self.checked_at = timezone.now()

        if self.consumable_present is False:
            self.consumable_level_percent = None

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )
