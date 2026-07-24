# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import RepairBaseModel
from .repair import Repair


class RepairTest(RepairBaseModel):
    """
    Prueba técnica realizada durante una reparación.

    Permite registrar pruebas de:

    - Encendido.
    - Impresión.
    - Copia.
    - Escaneo.
    - Alimentación de papel.
    - Dúplex.
    - Red.
    - Calidad de imagen.
    - Accesorios.
    - Contadores.
    - Estabilidad general.

    Una reparación puede tener varias pruebas, conservando
    el historial completo de resultados.
    """

    class TestType(models.TextChoices):
        POWER_ON = (
            "power_on",
            "Encendido",
        )
        PRINT_BLACK = (
            "print_black",
            "Impresión blanco y negro",
        )
        PRINT_COLOR = (
            "print_color",
            "Impresión color",
        )
        COPY_BLACK = (
            "copy_black",
            "Copia blanco y negro",
        )
        COPY_COLOR = (
            "copy_color",
            "Copia color",
        )
        SCAN = (
            "scan",
            "Escaneo",
        )
        PAPER_FEED = (
            "paper_feed",
            "Alimentación de papel",
        )
        DUPLEX = (
            "duplex",
            "Impresión dúplex",
        )
        ADF = (
            "adf",
            "Alimentador de documentos",
        )
        NETWORK = (
            "network",
            "Conectividad de red",
        )
        USB = (
            "usb",
            "Conectividad USB",
        )
        IMAGE_QUALITY = (
            "image_quality",
            "Calidad de imagen",
        )
        REGISTRATION = (
            "registration",
            "Registro y alineación",
        )
        COLOR_CALIBRATION = (
            "color_calibration",
            "Calibración de color",
        )
        FUSER = (
            "fuser",
            "Unidad de fusor",
        )
        FINISHER = (
            "finisher",
            "Finalizador",
        )
        PAPER_DECK = (
            "paper_deck",
            "Banco de papel",
        )
        METER = (
            "meter",
            "Contadores",
        )
        ERROR_CODES = (
            "error_codes",
            "Códigos de error",
        )
        STABILITY = (
            "stability",
            "Estabilidad general",
        )
        OTHER = (
            "other",
            "Otra prueba",
        )

    class Result(models.TextChoices):
        PENDING = (
            "pending",
            "Pendiente",
        )
        PASSED = (
            "passed",
            "Aprobada",
        )
        PASSED_WITH_OBSERVATIONS = (
            "passed_with_observations",
            "Aprobada con observaciones",
        )
        FAILED = (
            "failed",
            "Fallida",
        )
        NOT_APPLICABLE = (
            "not_applicable",
            "No aplica",
        )

    class Stage(models.TextChoices):
        INITIAL = (
            "initial",
            "Prueba inicial",
        )
        DURING_REPAIR = (
            "during_repair",
            "Durante la reparación",
        )
        FINAL = (
            "final",
            "Prueba final",
        )
        DELIVERY = (
            "delivery",
            "Prueba de entrega",
        )

    repair = models.ForeignKey(
        Repair,
        on_delete=models.CASCADE,
        related_name="tests",
        verbose_name="Reparación",
    )

    test_type = models.CharField(
        max_length=40,
        choices=TestType.choices,
        db_index=True,
        verbose_name="Tipo de prueba",
    )

    stage = models.CharField(
        max_length=30,
        choices=Stage.choices,
        default=Stage.FINAL,
        db_index=True,
        verbose_name="Etapa",
    )

    name = models.CharField(
        max_length=200,
        verbose_name="Nombre de la prueba",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )

    instructions = models.TextField(
        blank=True,
        verbose_name="Instrucciones",
    )

    result = models.CharField(
        max_length=40,
        choices=Result.choices,
        default=Result.PENDING,
        db_index=True,
        verbose_name="Resultado",
    )

    is_required = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Prueba obligatoria",
    )

    requires_photo = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere fotografía",
    )

    requires_print_sample = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere muestra de impresión",
    )

    tested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="repair_tests_performed",
        verbose_name="Realizada por",
    )

    tested_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Fecha de prueba",
    )

    initial_meter_total = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador total inicial",
    )

    final_meter_total = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador total final",
    )

    initial_meter_black = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador blanco y negro inicial",
    )

    final_meter_black = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador blanco y negro final",
    )

    initial_meter_color = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador color inicial",
    )

    final_meter_color = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Contador color final",
    )

    pages_tested = models.PositiveIntegerField(
        default=0,
        verbose_name="Páginas probadas",
    )

    error_code = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Código de error",
    )

    measured_value = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Valor medido",
    )

    expected_value = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Valor esperado",
    )

    measurement_unit = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Unidad de medida",
    )

    observations = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    failure_description = models.TextField(
        blank=True,
        verbose_name="Descripción de la falla",
    )

    corrective_action = models.TextField(
        blank=True,
        verbose_name="Acción correctiva",
    )

    retest_required = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Requiere nueva prueba",
    )

    retest_of = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="retests",
        verbose_name="Prueba anterior",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Orden",
    )

    class Meta:
        verbose_name = "Prueba de reparación"
        verbose_name_plural = "Pruebas de reparaciones"
        ordering = (
            "display_order",
            "test_type",
            "tested_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "repair",
                    "result",
                ],
                name="repair_test_result_idx",
            ),
            models.Index(
                fields=[
                    "repair",
                    "test_type",
                ],
                name="repair_test_type_idx",
            ),
            models.Index(
                fields=[
                    "repair",
                    "stage",
                ],
                name="repair_test_stage_idx",
            ),
            models.Index(
                fields=[
                    "is_required",
                    "result",
                ],
                name="repair_test_required_idx",
            ),
            models.Index(
                fields=[
                    "tested_by",
                    "tested_at",
                ],
                name="repair_test_user_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.repair.code} - "
            f"{self.name}"
        )

    @property
    def printed_pages_difference(self):
        """
        Calcula la diferencia entre los contadores totales.
        """

        if (
            self.initial_meter_total is None
            or self.final_meter_total is None
        ):
            return None

        return (
            self.final_meter_total
            - self.initial_meter_total
        )

    def clean(self):
        """
        Normaliza y valida la prueba técnica.
        """

        super().clean()

        self.name = str(
            self.name or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        self.instructions = str(
            self.instructions or ""
        ).strip()

        self.error_code = str(
            self.error_code or ""
        ).strip().upper()

        self.measurement_unit = str(
            self.measurement_unit or ""
        ).strip().lower()

        self.observations = str(
            self.observations or ""
        ).strip()

        self.failure_description = str(
            self.failure_description or ""
        ).strip()

        self.corrective_action = str(
            self.corrective_action or ""
        ).strip()

        if not self.repair_id:
            raise ValidationError(
                {
                    "repair": (
                        "La reparación es obligatoria."
                    ),
                }
            )

        if not self.test_type:
            raise ValidationError(
                {
                    "test_type": (
                        "El tipo de prueba es obligatorio."
                    ),
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name": (
                        "El nombre de la prueba es obligatorio."
                    ),
                }
            )

        if self.result == self.Result.PENDING:
            if self.tested_at:
                raise ValidationError(
                    {
                        "tested_at": (
                            "Una prueba pendiente no debe tener "
                            "fecha de ejecución."
                        ),
                    }
                )

            if self.tested_by_id:
                raise ValidationError(
                    {
                        "tested_by": (
                            "Una prueba pendiente no debe tener "
                            "un técnico registrado."
                        ),
                    }
                )

        if self.result != self.Result.PENDING:
            if not self.tested_at:
                raise ValidationError(
                    {
                        "tested_at": (
                            "Debe registrar la fecha de la prueba."
                        ),
                    }
                )

            if not self.tested_by_id:
                raise ValidationError(
                    {
                        "tested_by": (
                            "Debe indicar quién realizó la prueba."
                        ),
                    }
                )

        if self.result == self.Result.FAILED:
            if not self.failure_description:
                raise ValidationError(
                    {
                        "failure_description": (
                            "Debe describir la falla encontrada."
                        ),
                    }
                )

            if not self.retest_required:
                raise ValidationError(
                    {
                        "retest_required": (
                            "Una prueba fallida debe requerir "
                            "una nueva prueba."
                        ),
                    }
                )

        if (
            self.result
            == self.Result.PASSED_WITH_OBSERVATIONS
            and not self.observations
        ):
            raise ValidationError(
                {
                    "observations": (
                        "Debe registrar las observaciones "
                        "de la prueba."
                    ),
                }
            )

        if (
            self.result == self.Result.NOT_APPLICABLE
            and self.is_required
            and not self.observations
        ):
            raise ValidationError(
                {
                    "observations": (
                        "Debe indicar por qué la prueba "
                        "obligatoria no aplica."
                    ),
                }
            )

        if self.retest_of_id:
            if self.retest_of_id == self.pk:
                raise ValidationError(
                    {
                        "retest_of": (
                            "Una prueba no puede referenciarse "
                            "a sí misma."
                        ),
                    }
                )

            if self.retest_of.repair_id != self.repair_id:
                raise ValidationError(
                    {
                        "retest_of": (
                            "La prueba anterior no pertenece "
                            "a esta reparación."
                        ),
                    }
                )

            if (
                self.retest_of.test_type
                != self.test_type
            ):
                raise ValidationError(
                    {
                        "retest_of": (
                            "La nueva prueba debe ser del mismo "
                            "tipo que la prueba anterior."
                        ),
                    }
                )

        meter_pairs = [
            (
                "final_meter_total",
                self.initial_meter_total,
                self.final_meter_total,
            ),
            (
                "final_meter_black",
                self.initial_meter_black,
                self.final_meter_black,
            ),
            (
                "final_meter_color",
                self.initial_meter_color,
                self.final_meter_color,
            ),
        ]

        for field_name, initial_value, final_value in meter_pairs:
            if (
                initial_value is not None
                and final_value is not None
                and final_value < initial_value
            ):
                raise ValidationError(
                    {
                        field_name: (
                            "El contador final no puede ser menor "
                            "que el contador inicial."
                        ),
                    }
                )

        if (
            self.measured_value is not None
            and not self.measurement_unit
        ):
            raise ValidationError(
                {
                    "measurement_unit": (
                        "Debe indicar la unidad de medida."
                    ),
                }
            )

        if (
            self.expected_value is not None
            and not self.measurement_unit
        ):
            raise ValidationError(
                {
                    "measurement_unit": (
                        "Debe indicar la unidad de medida."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        """
        Normaliza, valida y actualiza el estado de pruebas.
        """

        self.name = str(
            self.name or ""
        ).strip()

        self.description = str(
            self.description or ""
        ).strip()

        self.instructions = str(
            self.instructions or ""
        ).strip()

        self.error_code = str(
            self.error_code or ""
        ).strip().upper()

        self.measurement_unit = str(
            self.measurement_unit or ""
        ).strip().lower()

        self.observations = str(
            self.observations or ""
        ).strip()

        self.failure_description = str(
            self.failure_description or ""
        ).strip()

        self.corrective_action = str(
            self.corrective_action or ""
        ).strip()

        if (
            self.result != self.Result.PENDING
            and not self.tested_at
        ):
            self.tested_at = timezone.now()

        self.full_clean()

        result = super().save(
            *args,
            **kwargs,
        )

        self.update_repair_test_status()

        return result

    def delete(self, *args, **kwargs):
        """
        Elimina la prueba y recalcula el estado de pruebas.
        """

        repair = self.repair

        result = super().delete(
            *args,
            **kwargs,
        )

        self.update_repair_test_status(
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
        Archiva la prueba y recalcula el estado.
        """

        result = super().archive(
            user=user,
            reason=reason,
            save=save,
        )

        self.update_repair_test_status()

        return result

    def restore(
        self,
        user=None,
        save=True,
    ):
        """
        Restaura la prueba y recalcula el estado.
        """

        result = super().restore(
            user=user,
            save=save,
        )

        self.update_repair_test_status()

        return result

    def update_repair_test_status(
        self,
        repair=None,
    ):
        """
        Marca las pruebas como completadas cuando no existen
        pruebas obligatorias pendientes o fallidas.
        """

        repair = repair or self.repair

        required_tests = repair.tests.filter(
            archived_at__isnull=True,
            is_required=True,
        )

        completed = (
            required_tests.exists()
            and not required_tests.filter(
                result__in=[
                    self.Result.PENDING,
                    self.Result.FAILED,
                ]
            ).exists()
        )

        if repair.tests_completed != completed:
            repair.tests_completed = completed

            repair.save(
                update_fields=[
                    "tests_completed",
                    "updated_at",
                ]
            )