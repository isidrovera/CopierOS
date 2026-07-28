# -*- coding: utf-8 -*-
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.utils import timezone

from apps.equipment.models import Equipment, EquipmentComponent

from .base import ServicesBaseModel


class ServiceReusablePart(ServicesBaseModel):
    class Condition(models.TextChoices):
        NEW = "new", "Nuevo"
        USED_OPERATIONAL = (
            "used_operational",
            "Usado operativo",
        )
        USED_WITH_NOTES = (
            "used_with_notes",
            "Usado con observaciones",
        )
        REPAIRED = "repaired", "Reparado"
        TO_REVIEW = "to_review", "Por revisar"
        DEFECTIVE = "defective", "Defectuoso"
        INCOMPLETE = "incomplete", "Incompleto"
        NOT_USABLE = "not_usable", "No utilizable"

    class Status(models.TextChoices):
        AVAILABLE = "available", "Disponible"
        RESERVED = "reserved", "Reservado"
        PENDING_REMOVAL = (
            "pending_removal",
            "Pendiente de retiro",
        )
        IN_CUSTODY = "in_custody", "En custodia"
        PENDING_RECEPTION = (
            "pending_reception",
            "Pendiente de recepción",
        )
        READY_FOR_INSTALLATION = (
            "ready_for_installation",
            "Listo para instalación",
        )
        INSTALLED = "installed", "Instalado"
        RETURNED = "returned", "Devuelto"
        LOST = "lost", "No localizado"
        DISCARDED = "discarded", "Descartado"

    class OriginType(models.TextChoices):
        WAREHOUSE = "warehouse", "Almacén"
        DONOR_EQUIPMENT = (
            "donor_equipment",
            "Equipo donante",
        )
        PURCHASE = "purchase", "Compra"
        REPAIRED = "repaired", "Reparado"
        RETURNED = "returned", "Devuelto"
        OTHER = "other", "Otro"

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        blank=True,
        editable=False,
        verbose_name="Código de unidad física",
    )

    component = models.ForeignKey(
        EquipmentComponent,
        on_delete=models.PROTECT,
        related_name="reusable_service_parts",
        verbose_name="Parte o unidad",
    )

    serial_number = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Número de serie",
    )

    condition = models.CharField(
        max_length=30,
        choices=Condition.choices,
        default=Condition.TO_REVIEW,
        db_index=True,
        verbose_name="Condición",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.AVAILABLE,
        db_index=True,
        verbose_name="Estado",
    )

    origin_type = models.CharField(
        max_length=30,
        choices=OriginType.choices,
        default=OriginType.WAREHOUSE,
        db_index=True,
        verbose_name="Origen",
    )

    source_equipment = models.ForeignKey(
        Equipment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="reusable_parts_removed",
        verbose_name="Equipo de origen",
    )

    current_equipment = models.ForeignKey(
        Equipment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="reusable_parts_installed",
        verbose_name="Equipo actual",
    )

    location_name = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
        verbose_name="Ubicación actual",
    )

    shelf_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Estante o referencia",
    )

    acquired_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de ingreso",
    )

    removed_from_source_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de retiro del equipo origen",
    )

    installed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de instalación",
    )

    evaluated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_reusable_parts_evaluated",
        verbose_name="Evaluado por",
    )

    evaluated_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de evaluación",
    )

    current_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_reusable_parts_in_custody",
        verbose_name="Responsable actual",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        ordering = (
            "component__name",
            "code",
        )
        indexes = [
            models.Index(
                fields=[
                    "component",
                    "status",
                ],
                name="svc_reuse_comp_st_idx",
            ),
            models.Index(
                fields=[
                    "source_equipment",
                    "status",
                ],
                name="svc_reuse_src_st_idx",
            ),
            models.Index(
                fields=[
                    "current_equipment",
                    "status",
                ],
                name="svc_reuse_cur_st_idx",
            ),
            models.Index(
                fields=[
                    "condition",
                    "status",
                ],
                name="svc_reuse_cond_st_idx",
            ),
            models.Index(
                fields=[
                    "current_holder",
                    "status",
                ],
                name="svc_reuse_hold_st_idx",
            ),
        ]
        verbose_name = "Parte reutilizable"
        verbose_name_plural = "Partes reutilizables"

    def __str__(self):
        return (
            f"{self.code} · "
            f"{self.component}"
        )

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    @classmethod
    def _build_code(cls, year, sequence):
        return f"PRU-{year}-{sequence:06d}"

    @classmethod
    def _next_sequence(cls, year):
        prefix = f"PRU-{year}-"

        last_code = (
            cls.objects
            .filter(
                code__startswith=prefix,
            )
            .order_by(
                "-code",
            )
            .values_list(
                "code",
                flat=True,
            )
            .first()
        )

        if not last_code:
            return 1

        match = re.fullmatch(
            rf"{re.escape(prefix)}(\d+)",
            last_code,
        )

        if not match:
            return 1

        return int(match.group(1)) + 1

    def _assign_automatic_code(self):
        year = timezone.localdate().year

        self.code = self._build_code(
            year,
            self._next_sequence(year),
        )

    def clean(self):
        super().clean()

        self.serial_number = self._clean_text(
            self.serial_number
        )

        self.location_name = self._clean_text(
            self.location_name
        )

        self.shelf_reference = self._clean_text(
            self.shelf_reference
        )

        self.notes = self._clean_text(
            self.notes
        )

        if (
            self.origin_type
            == self.OriginType.DONOR_EQUIPMENT
            and not self.source_equipment_id
        ):
            raise ValidationError(
                {
                    "source_equipment": (
                        "Debe indicar el equipo de origen."
                    )
                }
            )

        if (
            self.current_equipment_id
            and self.source_equipment_id
            and self.current_equipment_id
            == self.source_equipment_id
            and self.status
            == self.Status.INSTALLED
        ):
            raise ValidationError(
                {
                    "current_equipment": (
                        "El equipo actual debe ser diferente "
                        "del equipo de origen."
                    )
                }
            )

        if (
            self.status
            == self.Status.INSTALLED
            and not self.current_equipment_id
        ):
            raise ValidationError(
                {
                    "current_equipment": (
                        "Una parte instalada debe indicar "
                        "el equipo donde quedó instalada."
                    )
                }
            )

        if (
            self.status
            == self.Status.INSTALLED
            and not self.installed_at
        ):
            raise ValidationError(
                {
                    "installed_at": (
                        "Debe registrar la fecha de instalación."
                    )
                }
            )

        if (
            self.status
            == self.Status.IN_CUSTODY
            and not self.current_holder_id
        ):
            raise ValidationError(
                {
                    "current_holder": (
                        "Debe indicar quién tiene la parte."
                    )
                }
            )

        if (
            self.condition
            in {
                self.Condition.DEFECTIVE,
                self.Condition.INCOMPLETE,
                self.Condition.NOT_USABLE,
            }
            and self.status
            in {
                self.Status.AVAILABLE,
                self.Status.READY_FOR_INSTALLATION,
            }
        ):
            raise ValidationError(
                {
                    "status": (
                        "Una parte defectuosa, incompleta o no "
                        "utilizable no puede estar disponible "
                        "para instalación."
                    )
                }
            )

    def save(self, *args, **kwargs):
        creating = self._state.adding

        if not self.acquired_at:
            self.acquired_at = timezone.now()

        if (
            self.status
            == self.Status.INSTALLED
            and not self.installed_at
        ):
            self.installed_at = timezone.now()

        if not self.code:
            self._assign_automatic_code()

        self.full_clean()

        if not creating:
            return super().save(
                *args,
                **kwargs,
            )

        for _attempt in range(5):
            try:
                with transaction.atomic():
                    return super().save(
                        *args,
                        **kwargs,
                    )

            except IntegrityError:
                self.code = ""
                self._assign_automatic_code()

        raise IntegrityError(
            "No se pudo generar un código único "
            "para la parte reutilizable."
        )
