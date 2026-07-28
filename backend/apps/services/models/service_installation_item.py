# -*- coding: utf-8 -*-
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import ServicesBaseModel
from .service_order import ServiceOrder
from .service_part_request_item import ServicePartRequestItem
from .service_part_transfer import ServicePartTransfer


class ServiceInstallationItem(ServicesBaseModel):
    class Result(models.TextChoices):
        PENDING = "pending", "Pendiente"
        INSTALLED = "installed", "Instalado"
        PARTIALLY_INSTALLED = (
            "partially_installed",
            "Instalado parcialmente",
        )
        NOT_INSTALLED = "not_installed", "No instalado"
        RETURNED = "returned", "Devuelto"
        DAMAGED = "damaged", "Dañado"
        NOT_COMPATIBLE = "not_compatible", "No compatible"
        REQUIRES_REVIEW = (
            "requires_review",
            "Requiere revisión",
        )

    class MeterType(models.TextChoices):
        TOTAL = "total", "Contador total"
        BLACK = "black", "Contador blanco y negro"
        COLOR = "color", "Contador color"
        SCAN = "scan", "Contador escáner"
        NONE = "none", "No aplica"

    service_order = models.ForeignKey(
        ServiceOrder,
        on_delete=models.PROTECT,
        related_name="installation_items",
        verbose_name="OS de instalación",
    )

    part_request_item = models.ForeignKey(
        ServicePartRequestItem,
        on_delete=models.PROTECT,
        related_name="installation_items",
        verbose_name="Detalle del pedido",
    )

    transfer = models.OneToOneField(
        ServicePartTransfer,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="installation_item",
        verbose_name="Transferencia asociada",
    )

    planned_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1.00"),
        verbose_name="Cantidad programada",
    )

    installed_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Cantidad instalada",
    )

    returned_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Cantidad devuelta",
    )

    result = models.CharField(
        max_length=30,
        choices=Result.choices,
        default=Result.PENDING,
        db_index=True,
        verbose_name="Resultado",
    )

    installed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="service_installation_items_installed",
        verbose_name="Técnico instalador",
    )

    installed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de instalación",
    )

    meter_type = models.CharField(
        max_length=20,
        choices=MeterType.choices,
        default=MeterType.NONE,
        db_index=True,
        verbose_name="Contador de referencia",
    )

    total_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador total",
    )

    black_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador blanco y negro",
    )

    color_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador color",
    )

    scan_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador escáner",
    )

    reference_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador usado como referencia",
    )

    removed_item_condition = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Estado de la pieza retirada",
    )

    installation_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones de instalación",
    )

    non_installation_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de no instalación",
    )

    evidence_notes = models.TextField(
        blank=True,
        verbose_name="Observaciones de evidencias",
    )

    history_generated = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Historial generado",
    )

    class Meta:
        ordering = (
            "created_at",
        )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "service_order",
                    "part_request_item",
                ],
                name="unique_svc_install_item",
            )
        ]
        indexes = [
            models.Index(
                fields=[
                    "service_order",
                    "result",
                ],
                name="svc_inst_order_res_idx",
            ),
            models.Index(
                fields=[
                    "part_request_item",
                    "result",
                ],
                name="svc_inst_part_res_idx",
            ),
            models.Index(
                fields=[
                    "installed_by",
                    "installed_at",
                ],
                name="svc_inst_user_date_idx",
            ),
            models.Index(
                fields=[
                    "history_generated",
                    "result",
                ],
                name="svc_inst_hist_res_idx",
            ),
        ]
        verbose_name = "Ítem de instalación"
        verbose_name_plural = "Ítems de instalación"

    def __str__(self):
        return (
            f"{self.service_order.code} · "
            f"{self.part_request_item.display_name}"
        )

    @staticmethod
    def _clean_text(value):
        return str(value or "").strip()

    def clean(self):
        super().clean()

        self.removed_item_condition = self._clean_text(
            self.removed_item_condition
        )

        self.installation_notes = self._clean_text(
            self.installation_notes
        )

        self.non_installation_reason = self._clean_text(
            self.non_installation_reason
        )

        self.evidence_notes = self._clean_text(
            self.evidence_notes
        )

        if (
            self.planned_quantity is None
            or self.planned_quantity <= 0
        ):
            raise ValidationError(
                {
                    "planned_quantity": (
                        "La cantidad programada debe "
                        "ser mayor que cero."
                    )
                }
            )

        if (
            self.installed_quantity is None
            or self.installed_quantity < 0
        ):
            raise ValidationError(
                {
                    "installed_quantity": (
                        "La cantidad instalada no puede "
                        "ser negativa."
                    )
                }
            )

        if (
            self.returned_quantity is None
            or self.returned_quantity < 0
        ):
            raise ValidationError(
                {
                    "returned_quantity": (
                        "La cantidad devuelta no puede "
                        "ser negativa."
                    )
                }
            )

        if (
            self.installed_quantity
            + self.returned_quantity
            > self.planned_quantity
        ):
            raise ValidationError(
                {
                    "installed_quantity": (
                        "La suma instalada y devuelta no puede "
                        "superar la cantidad programada."
                    )
                }
            )

        request = self.part_request_item.request

        if (
            request.installation_service_order_id
            and request.installation_service_order_id
            != self.service_order_id
        ):
            raise ValidationError(
                {
                    "service_order": (
                        "La OS no coincide con la OS de "
                        "instalación vinculada al pedido."
                    )
                }
            )

        if (
            self.transfer_id
            and self.transfer.part_request_item_id
            != self.part_request_item_id
        ):
            raise ValidationError(
                {
                    "transfer": (
                        "La transferencia pertenece a otro "
                        "detalle del pedido."
                    )
                }
            )

        if (
            self.result
            == self.Result.INSTALLED
            and self.installed_quantity
            != self.planned_quantity
        ):
            raise ValidationError(
                {
                    "installed_quantity": (
                        "Para marcar como instalado, la cantidad "
                        "instalada debe coincidir con la programada."
                    )
                }
            )

        if (
            self.result
            == self.Result.PARTIALLY_INSTALLED
            and (
                self.installed_quantity <= 0
                or self.installed_quantity
                >= self.planned_quantity
            )
        ):
            raise ValidationError(
                {
                    "installed_quantity": (
                        "La instalación parcial debe ser mayor "
                        "que cero y menor que la programada."
                    )
                }
            )

        non_installed_results = {
            self.Result.NOT_INSTALLED,
            self.Result.RETURNED,
            self.Result.DAMAGED,
            self.Result.NOT_COMPATIBLE,
            self.Result.REQUIRES_REVIEW,
        }

        if (
            self.result in non_installed_results
            and not self.non_installation_reason
        ):
            raise ValidationError(
                {
                    "non_installation_reason": (
                        "Debe indicar el motivo por el que "
                        "no se completó la instalación."
                    )
                }
            )

        installed_results = {
            self.Result.INSTALLED,
            self.Result.PARTIALLY_INSTALLED,
        }

        if (
            self.result in installed_results
            and not self.installed_by_id
        ):
            raise ValidationError(
                {
                    "installed_by": (
                        "Debe registrar el técnico instalador."
                    )
                }
            )

        if (
            self.result in installed_results
            and not self.installed_at
        ):
            raise ValidationError(
                {
                    "installed_at": (
                        "Debe registrar la fecha de instalación."
                    )
                }
            )

        meter_map = {
            self.MeterType.TOTAL: self.total_meter,
            self.MeterType.BLACK: self.black_meter,
            self.MeterType.COLOR: self.color_meter,
            self.MeterType.SCAN: self.scan_meter,
        }

        if (
            self.meter_type != self.MeterType.NONE
            and meter_map.get(self.meter_type) is None
        ):
            raise ValidationError(
                {
                    "meter_type": (
                        "Debe registrar el contador seleccionado "
                        "como referencia."
                    )
                }
            )

        expected_reference = meter_map.get(
            self.meter_type
        )

        if (
            self.meter_type != self.MeterType.NONE
            and self.reference_meter is not None
            and self.reference_meter != expected_reference
        ):
            raise ValidationError(
                {
                    "reference_meter": (
                        "El contador de referencia no coincide "
                        "con el tipo seleccionado."
                    )
                }
            )

    def save(self, *args, **kwargs):
        installed_results = {
            self.Result.INSTALLED,
            self.Result.PARTIALLY_INSTALLED,
        }

        if (
            self.result in installed_results
            and not self.installed_at
        ):
            self.installed_at = timezone.now()

        meter_map = {
            self.MeterType.TOTAL: self.total_meter,
            self.MeterType.BLACK: self.black_meter,
            self.MeterType.COLOR: self.color_meter,
            self.MeterType.SCAN: self.scan_meter,
        }

        if self.meter_type == self.MeterType.NONE:
            self.reference_meter = None
        else:
            self.reference_meter = meter_map.get(
                self.meter_type
            )

        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )
