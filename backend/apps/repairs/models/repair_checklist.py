# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone

from apps.equipment.models import (
    EquipmentComponent,
)

from .base import RepairBaseModel
from .repair import Repair


class RepairChecklist(RepairBaseModel):
    """
    Lista principal de revisión técnica de una reparación.

    Cada reparación puede manejar varias listas de revisión,
    aunque normalmente una será la principal y obligatoria
    para permitir el cierre.
    """

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        IN_PROGRESS = (
            "in_progress",
            "En proceso",
        )
        COMPLETED = (
            "completed",
            "Completada",
        )
        CANCELLED = (
            "cancelled",
            "Cancelada",
        )

    repair = models.ForeignKey(
        Repair,
        on_delete=models.CASCADE,
        related_name="checklists",
        verbose_name="Reparación",
    )

    name = models.CharField(
        max_length=180,
        default="Lista de revisión técnica",
        verbose_name="Nombre",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Estado",
    )

    is_main_checklist = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Lista principal",
    )

    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_checklists_started",
        verbose_name="Iniciada por",
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
        related_name="repair_checklists_completed",
        verbose_name="Completada por",
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
        verbose_name = "Lista de revisión"
        verbose_name_plural = "Listas de revisión"
        ordering = (
            "-is_main_checklist",
            "-created_at",
        )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "repair",
                ],
                condition=models.Q(
                    is_main_checklist=True,
                    archived_at__isnull=True,
                ),
                name="unique_main_repair_checklist",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "repair",
                    "status",
                ],
                name="repair_check_status_idx",
            ),
            models.Index(
                fields=[
                    "is_main_checklist",
                    "status",
                ],
                name="repair_check_main_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.repair.code} - "
            f"{self.name}"
        )

    def clean(self):
        """
        Normaliza y valida la lista de revisión.
        """

        super().clean()

        self.name = str(
            self.name or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        self.observations = str(
            self.observations or ""
        ).strip()

        if not self.repair_id:
            raise ValidationError(
                {
                    "repair": (
                        "La reparación es obligatoria."
                    ),
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": (
                        "El nombre de la lista es obligatorio."
                    ),
                }
            )

        if self.is_main_checklist and self.repair_id:
            existing_main = RepairChecklist.objects.filter(
                repair_id=self.repair_id,
                is_main_checklist=True,
                archived_at__isnull=True,
            ).exclude(
                pk=self.pk,
            )

            if existing_main.exists():
                raise ValidationError(
                    {
                        "is_main_checklist": (
                            "La reparación ya tiene una "
                            "lista principal."
                        ),
                    }
                )

        if self.status == self.Status.IN_PROGRESS:
            if not self.started_at:
                raise ValidationError(
                    {
                        "started_at": (
                            "Debe registrar la fecha de inicio."
                        ),
                    }
                )

        if self.status == self.Status.COMPLETED:
            if not self.completed_at:
                raise ValidationError(
                    {
                        "completed_at": (
                            "Debe registrar la fecha de finalización."
                        ),
                    }
                )

            if not self.completed_by_id:
                raise ValidationError(
                    {
                        "completed_by": (
                            "Debe indicar quién completó la lista."
                        ),
                    }
                )

            pending_items = self.items.filter(
                archived_at__isnull=True,
                is_required=True,
            ).exclude(
                status__in=[
                    RepairChecklistItem.Status.OK,
                    RepairChecklistItem.Status.NOT_APPLICABLE,
                ]
            )

            if pending_items.exists():
                raise ValidationError(
                    {
                        "status": (
                            "No puede completar la lista mientras "
                            "existan puntos obligatorios pendientes."
                        ),
                    }
                )

        if (
            self.started_at
            and self.completed_at
            and self.completed_at < self.started_at
        ):
            raise ValidationError(
                {
                    "completed_at": (
                        "La fecha de finalización no puede ser "
                        "anterior a la fecha de inicio."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        """
        Normaliza, valida y sincroniza la reparación.
        """

        self.name = str(
            self.name or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        self.observations = str(
            self.observations or ""
        ).strip()

        self.full_clean()

        result = super().save(
            *args,
            **kwargs,
        )

        if self.is_main_checklist and self.repair_id:
            checklist_completed = (
                self.status
                == self.Status.COMPLETED
            )

            if (
                self.repair.checklist_completed
                != checklist_completed
            ):
                self.repair.checklist_completed = (
                    checklist_completed
                )

                self.repair.save(
                    update_fields=[
                        "checklist_completed",
                        "updated_at",
                    ]
                )

        return result


class RepairChecklistItem(RepairBaseModel):
    """
    Punto individual de revisión técnica.

    Puede representar:

    - Una revisión general.
    - Una unidad técnica completa.
    - Un accesorio.
    - Un consumible como tóner o tinta.

    Las subpartes no se crean como tarjetas principales.
    Solo se relacionan con una unidad principal cuando
    requieren cambio.
    """

    class Category(models.TextChoices):
        GENERAL = (
            "general",
            "Revisión general",
        )
        EXTERNAL = (
            "external",
            "Condición externa",
        )
        CLEANING = (
            "cleaning",
            "Limpieza",
        )
        PAPER_FEED = (
            "paper_feed",
            "Alimentación de papel",
        )
        PRINT_QUALITY = (
            "print_quality",
            "Calidad de impresión",
        )
        SCANNING = (
            "scanning",
            "Escaneo",
        )
        NETWORK = (
            "network",
            "Red y conectividad",
        )
        ELECTRICAL = (
            "electrical",
            "Sistema eléctrico",
        )
        MECHANICAL = (
            "mechanical",
            "Sistema mecánico",
        )
        COMPONENT = (
            "component",
            "Componente técnico",
        )
        ACCESSORY = (
            "accessory",
            "Accesorio",
        )
        SAFETY = (
            "safety",
            "Seguridad",
        )
        OTHER = (
            "other",
            "Otro",
        )

    class Status(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        OK = (
            "ok",
            "Correcto",
        )
        OBSERVED = (
            "observed",
            "Con observaciones",
        )
        FAILED = (
            "failed",
            "Falla",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )

    checklist = models.ForeignKey(
        RepairChecklist,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Lista de revisión",
    )

    component = models.ForeignKey(
        EquipmentComponent,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="repair_checklist_items",
        verbose_name="Componente",
    )

    selected_subcomponents = models.ManyToManyField(
        EquipmentComponent,
        blank=True,
        related_name=(
            "selected_in_repair_checklist_items"
        ),
        verbose_name="Subpartes seleccionadas",
        help_text=(
            "Subpartes de la unidad principal que requieren "
            "cambio. Solo se utiliza cuando la unidad está "
            "marcada con falla."
        ),
    )

    code = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Código",
    )

    name = models.CharField(
        max_length=200,
        verbose_name="Punto de revisión",
    )

    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.GENERAL,
        db_index=True,
        verbose_name="Categoría",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    instructions = models.TextField(
        blank=True,
        verbose_name="Instrucciones",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Resultado",
    )

    is_required = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Obligatorio",
    )

    requires_photo = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere fotografía",
    )

    requires_observation = models.BooleanField(
        default=False,
        verbose_name="Requiere observación",
    )

    observation = models.TextField(
        blank=True,
        verbose_name="Observación",
    )

    consumable_present = models.BooleanField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Consumible instalado",
        help_text=(
            "Indica si el tóner, botella o cartucho se "
            "encuentra instalado. False significa sin botella "
            "o cartucho. Se deja vacío para componentes que "
            "no son consumibles."
        ),
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
            help_text=(
                "Nivel actual del tóner o tinta entre "
                "0 y 100 por ciento."
            ),
        )
    )

    checked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_checklist_items_checked",
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
        verbose_name="Orden",
    )

    class Meta:
        verbose_name = "Punto de revisión"
        verbose_name_plural = "Puntos de revisión"
        ordering = (
            "display_order",
            "name",
        )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "checklist",
                    "code",
                ],
                name="unique_repair_check_item_code",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "checklist",
                    "status",
                ],
                name="repair_check_item_status_idx",
            ),
            models.Index(
                fields=[
                    "component",
                    "status",
                ],
                name="repair_check_component_idx",
            ),
            models.Index(
                fields=[
                    "category",
                    "status",
                ],
                name="repair_check_category_idx",
            ),
            models.Index(
                fields=[
                    "is_required",
                    "status",
                ],
                name="repair_check_required_idx",
            ),
            models.Index(
                fields=[
                    "consumable_present",
                    "consumable_level_percent",
                ],
                name="repair_check_consumable_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.checklist.repair.code} - "
            f"{self.name}"
        )

    def is_primary_consumable(self):
        """
        Indica si el punto representa un consumible principal.

        Las subpartes nunca manejan nivel de tóner o tinta.
        """

        if not self.component_id:
            return False

        component = self.component

        return bool(
            component.is_consumable
            and not component.parent_component_id
        )

    def clean(self):
        """
        Normaliza y valida el punto de revisión.
        """

        super().clean()

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.name = str(
            self.name or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        self.instructions = str(
            self.instructions or ""
        ).strip()

        self.observation = str(
            self.observation or ""
        ).strip()

        if not self.checklist_id:
            raise ValidationError(
                {
                    "checklist": (
                        "La lista de revisión es obligatoria."
                    ),
                }
            )

        if not self.code:
            raise ValidationError(
                {
                    "code": (
                        "El código del punto es obligatorio."
                    ),
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": (
                        "El nombre del punto es obligatorio."
                    ),
                }
            )

        duplicate_item = (
            RepairChecklistItem.objects.filter(
                checklist_id=self.checklist_id,
                code__iexact=self.code,
            )
            .exclude(
                pk=self.pk,
            )
        )

        if duplicate_item.exists():
            raise ValidationError(
                {
                    "code": (
                        "Ya existe un punto con este código "
                        "en la lista."
                    ),
                }
            )

        if (
            self.category
            in [
                self.Category.COMPONENT,
                self.Category.ACCESSORY,
            ]
            and not self.component_id
        ):
            raise ValidationError(
                {
                    "component": (
                        "Debe seleccionar el componente "
                        "relacionado."
                    ),
                }
            )

        if (
            self.component_id
            and self.category
            not in [
                self.Category.COMPONENT,
                self.Category.ACCESSORY,
            ]
        ):
            raise ValidationError(
                {
                    "category": (
                        "Los puntos vinculados a componentes "
                        "deben usar la categoría componente "
                        "o accesorio."
                    ),
                }
            )

        if (
            self.component_id
            and self.component.parent_component_id
        ):
            raise ValidationError(
                {
                    "component": (
                        "Las subpartes no pueden registrarse "
                        "como puntos principales del checklist."
                    ),
                }
            )

        if (
            self.status == self.Status.PENDING
            and self.checked_at
        ):
            raise ValidationError(
                {
                    "checked_at": (
                        "Un punto pendiente no debe tener "
                        "fecha de revisión."
                    ),
                }
            )

        if self.status != self.Status.PENDING:
            if not self.checked_at:
                raise ValidationError(
                    {
                        "checked_at": (
                            "Debe registrar la fecha "
                            "de revisión."
                        ),
                    }
                )

            if not self.checked_by_id:
                raise ValidationError(
                    {
                        "checked_by": (
                            "Debe indicar quién realizó "
                            "la revisión."
                        ),
                    }
                )

        if (
            self.requires_observation
            and self.status
            in [
                self.Status.OBSERVED,
                self.Status.FAILED,
            ]
            and not self.observation
        ):
            raise ValidationError(
                {
                    "observation": (
                        "Debe registrar una observación."
                    ),
                }
            )

        if (
            self.status == self.Status.FAILED
            and not self.observation
        ):
            raise ValidationError(
                {
                    "observation": (
                        "Debe describir la falla encontrada."
                    ),
                }
            )

        if (
            self.status
            == self.Status.NOT_APPLICABLE
            and self.is_required
            and not self.observation
        ):
            raise ValidationError(
                {
                    "observation": (
                        "Debe indicar por qué el punto "
                        "obligatorio no aplica."
                    ),
                }
            )

        primary_consumable = (
            self.is_primary_consumable()
        )

        if not primary_consumable:
            if self.consumable_present is not None:
                raise ValidationError(
                    {
                        "consumable_present": (
                            "Este campo solo se utiliza para "
                            "tóner, tinta o consumibles "
                            "principales."
                        ),
                    }
                )

            if (
                self.consumable_level_percent
                is not None
            ):
                raise ValidationError(
                    {
                        "consumable_level_percent": (
                            "El nivel solo se registra para "
                            "tóner, tinta o consumibles "
                            "principales."
                        ),
                    }
                )

        if primary_consumable:
            if (
                self.status
                != self.Status.PENDING
                and self.consumable_present
                is None
            ):
                raise ValidationError(
                    {
                        "consumable_present": (
                            "Debes indicar si el tóner, "
                            "botella o cartucho está instalado."
                        ),
                    }
                )

            if self.consumable_present is False:
                if (
                    self.consumable_level_percent
                    is not None
                ):
                    raise ValidationError(
                        {
                            "consumable_level_percent": (
                                "Un consumible sin botella "
                                "o cartucho no puede tener "
                                "un porcentaje registrado."
                            ),
                        }
                    )

            if self.consumable_present is True:
                if (
                    self.status
                    != self.Status.PENDING
                    and self.consumable_level_percent
                    is None
                ):
                    raise ValidationError(
                        {
                            "consumable_level_percent": (
                                "Debes registrar el nivel "
                                "del consumible."
                            ),
                        }
                    )

                if (
                    self.consumable_level_percent
                    is not None
                    and not (
                        0
                        <= self.consumable_level_percent
                        <= 100
                    )
                ):
                    raise ValidationError(
                        {
                            "consumable_level_percent": (
                                "El nivel debe estar entre "
                                "0 y 100."
                            ),
                        }
                    )

    def save(self, *args, **kwargs):
        """
        Normaliza y valida el punto de revisión.
        """

        self.code = str(
            self.code or ""
        ).strip().upper()

        self.name = str(
            self.name or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        self.instructions = str(
            self.instructions or ""
        ).strip()

        self.observation = str(
            self.observation or ""
        ).strip()

        if (
            self.status != self.Status.PENDING
            and not self.checked_at
        ):
            self.checked_at = timezone.now()

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )