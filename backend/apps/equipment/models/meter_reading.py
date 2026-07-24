# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .base import EquipmentBaseModel
from .equipment import Equipment


class MeterReading(EquipmentBaseModel):
    """
    Registra el historial de contadores de una máquina.

    Cada lectura conserva:

    - Fecha y hora de lectura.
    - Contador total.
    - Contador blanco y negro.
    - Contador color.
    - Contador de escaneo.
    - Fuente de la lectura.
    - Usuario responsable.
    - Proceso relacionado.
    - Evidencia u observaciones.

    Este modelo conserva el historial completo. Los campos de contador
    actual del modelo Equipment se utilizan únicamente para consultas
    rápidas y deben actualizarse a partir de estas lecturas.
    """

    class Source(models.TextChoices):
        MANUAL = (
            "manual",
            "Ingreso manual",
        )
        UNLOADING = (
            "unloading",
            "Descarga",
        )
        MOBILE_APP = (
            "mobile_app",
            "Aplicación móvil",
        )
        SNMP = (
            "snmp",
            "Lectura SNMP",
        )
        REPAIR_ENTRY = (
            "repair_entry",
            "Ingreso a reparación",
        )
        REPAIR_EXIT = (
            "repair_exit",
            "Salida de reparación",
        )
        INSTALLATION = (
            "installation",
            "Instalación",
        )
        REMOVAL = (
            "removal",
            "Retiro",
        )
        DELIVERY = (
            "delivery",
            "Entrega",
        )
        RETURN = (
            "return",
            "Retorno",
        )
        CONTRACT = (
            "contract",
            "Contrato",
        )
        IMPORTED = (
            "imported",
            "Importada desde otro sistema",
        )
        SYSTEM = (
            "system",
            "Generada por el sistema",
        )
        OTHER = (
            "other",
            "Otra fuente",
        )

    class ReadingType(models.TextChoices):
        NORMAL = (
            "normal",
            "Lectura normal",
        )
        INITIAL = (
            "initial",
            "Lectura inicial",
        )
        CORRECTION = (
            "correction",
            "Corrección",
        )
        RESET = (
            "reset",
            "Reinicio o cambio de contador",
        )
        ESTIMATED = (
            "estimated",
            "Lectura estimada",
        )

    class ReferenceType(models.TextChoices):
        NONE = (
            "none",
            "Sin referencia",
        )
        UNLOADING = (
            "unloading",
            "Descarga",
        )
        REPAIR = (
            "repair",
            "Reparación",
        )
        DELIVERY = (
            "delivery",
            "Entrega",
        )
        INSTALLATION = (
            "installation",
            "Instalación",
        )
        REMOVAL = (
            "removal",
            "Retiro",
        )
        CONTRACT = (
            "contract",
            "Contrato",
        )
        MOVEMENT = (
            "movement",
            "Movimiento de equipo",
        )
        MOBILE_APP = (
            "mobile_app",
            "Aplicación móvil",
        )
        SNMP_AGENT = (
            "snmp_agent",
            "Agente SNMP",
        )
        OTHER = (
            "other",
            "Otro proceso",
        )

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="meter_readings",
        verbose_name="Equipo",
    )

    reading_date = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Fecha y hora de lectura",
        help_text=(
            "Fecha y hora en la que fueron obtenidos los contadores."
        ),
    )

    reading_type = models.CharField(
        max_length=20,
        choices=ReadingType.choices,
        default=ReadingType.NORMAL,
        db_index=True,
        verbose_name="Tipo de lectura",
    )

    source = models.CharField(
        max_length=30,
        choices=Source.choices,
        default=Source.MANUAL,
        db_index=True,
        verbose_name="Fuente",
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
        verbose_name="Contador de escaneo",
    )

    previous_total_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Contador total anterior",
    )

    previous_black_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Contador B/N anterior",
    )

    previous_color_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Contador color anterior",
    )

    previous_scan_meter = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Contador de escaneo anterior",
    )

    total_difference = models.BigIntegerField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Diferencia total",
    )

    black_difference = models.BigIntegerField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Diferencia B/N",
    )

    color_difference = models.BigIntegerField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Diferencia color",
    )

    scan_difference = models.BigIntegerField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Diferencia de escaneo",
    )

    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="registered_equipment_meter_readings",
        verbose_name="Registrado por",
    )

    reference_type = models.CharField(
        max_length=30,
        choices=ReferenceType.choices,
        default=ReferenceType.NONE,
        db_index=True,
        verbose_name="Proceso relacionado",
    )

    reference_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID del registro relacionado",
        help_text=(
            "UUID de la reparación, instalación, entrega, contrato "
            "u otro registro que originó la lectura."
        ),
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Número de referencia",
        help_text=(
            "Número visible del proceso relacionado. "
            "Ejemplo: REP-000125 o CONT-000054."
        ),
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        protocol="both",
        unpack_ipv4=True,
        verbose_name="Dirección IP consultada",
    )

    device_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha reportada por el equipo",
        help_text=(
            "Fecha y hora entregada por el dispositivo o agente "
            "que obtuvo la lectura."
        ),
    )

    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Lectura verificada",
        help_text=(
            "Indica que la lectura fue revisada y confirmada "
            "por un usuario autorizado."
        ),
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="verified_equipment_meter_readings",
        verbose_name="Verificada por",
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de verificación",
    )

    is_applied_to_equipment = models.BooleanField(
        default=False,
        db_index=True,
        editable=False,
        verbose_name="Aplicada al equipo",
        help_text=(
            "Indica si esta lectura ya actualizó los contadores "
            "actuales de la ficha del equipo."
        ),
    )

    correction_reason = models.TextField(
        blank=True,
        verbose_name="Motivo de corrección o reinicio",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Lectura de contador"
        verbose_name_plural = "Lecturas de contadores"
        ordering = (
            "-reading_date",
            "-created_at",
        )
        indexes = [
            models.Index(
                fields=[
                    "equipment",
                    "reading_date",
                ],
                name="equip_meter_equipment_date_idx",
            ),
            models.Index(
                fields=[
                    "equipment",
                    "source",
                ],
                name="eq_meter_equip_source",
            ),
            models.Index(
                fields=[
                    "source",
                    "reading_date",
                ],
                name="equip_meter_source_date_idx",
            ),
            models.Index(
                fields=[
                    "reference_type",
                    "reference_id",
                ],
                name="equip_meter_reference_idx",
            ),
            models.Index(
                fields=[
                    "is_verified",
                    "reading_date",
                ],
                name="equip_meter_verified_date_idx",
            ),
            models.Index(
                fields=[
                    "is_applied_to_equipment",
                    "reading_date",
                ],
                name="equip_meter_applied_date_idx",
            ),
        ]

    def __str__(self):
        equipment_text = ""

        if self.equipment_id:
            equipment_text = str(
                self.equipment
            ).strip()

        date_text = ""

        if self.reading_date:
            date_text = timezone.localtime(
                self.reading_date
            ).strftime(
                "%d/%m/%Y %H:%M"
            )

        if equipment_text and date_text:
            return f"{equipment_text} - {date_text}"

        if equipment_text:
            return equipment_text

        return "Lectura de contador"

    def get_previous_reading(self):
        """
        Obtiene la lectura inmediatamente anterior del mismo equipo.

        Las lecturas de corrección y reinicio también pueden ser tomadas
        como referencia, porque representan el último valor confirmado
        dentro de la secuencia histórica.
        """

        if not self.equipment_id or not self.reading_date:
            return None

        previous_readings = MeterReading.objects.filter(
            equipment_id=self.equipment_id,
            reading_date__lt=self.reading_date,
        )

        if self.pk:
            previous_readings = previous_readings.exclude(
                pk=self.pk,
            )

        return previous_readings.order_by(
            "-reading_date",
            "-created_at",
        ).first()

    def calculate_differences(self):
        """
        Calcula las diferencias respecto de la lectura anterior.

        En una lectura de reinicio se permite que los nuevos valores sean
        menores. En ese caso, la diferencia puede quedar negativa para
        dejar evidencia del cambio de contador.
        """

        previous_reading = self.get_previous_reading()

        if previous_reading:
            self.previous_total_meter = previous_reading.total_meter
            self.previous_black_meter = previous_reading.black_meter
            self.previous_color_meter = previous_reading.color_meter
            self.previous_scan_meter = previous_reading.scan_meter
        elif self.equipment_id:
            self.previous_total_meter = (
                self.equipment.initial_total_meter
            )
            self.previous_black_meter = (
                self.equipment.initial_black_meter
            )
            self.previous_color_meter = (
                self.equipment.initial_color_meter
            )
            self.previous_scan_meter = (
                self.equipment.initial_scan_meter
            )
        else:
            self.previous_total_meter = None
            self.previous_black_meter = None
            self.previous_color_meter = None
            self.previous_scan_meter = None

        self.total_difference = self._calculate_difference(
            current_value=self.total_meter,
            previous_value=self.previous_total_meter,
        )

        self.black_difference = self._calculate_difference(
            current_value=self.black_meter,
            previous_value=self.previous_black_meter,
        )

        self.color_difference = self._calculate_difference(
            current_value=self.color_meter,
            previous_value=self.previous_color_meter,
        )

        self.scan_difference = self._calculate_difference(
            current_value=self.scan_meter,
            previous_value=self.previous_scan_meter,
        )

    @staticmethod
    def _calculate_difference(
        current_value,
        previous_value,
    ):
        """
        Calcula la diferencia cuando ambos valores están disponibles.
        """

        if current_value is None or previous_value is None:
            return None

        return int(current_value) - int(previous_value)

    def clean(self):
        """
        Normaliza y valida la lectura antes de guardarla.
        """

        super().clean()

        self.reference_number = str(
            self.reference_number or ""
        ).strip().upper()

        self.correction_reason = str(
            self.correction_reason or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        if not self.equipment_id:
            raise ValidationError(
                {
                    "equipment": (
                        "Debe seleccionar el equipo al que pertenece "
                        "la lectura."
                    ),
                }
            )

        if not self.reading_date:
            raise ValidationError(
                {
                    "reading_date": (
                        "Debe registrar la fecha y hora de la lectura."
                    ),
                }
            )

        meter_values = [
            self.total_meter,
            self.black_meter,
            self.color_meter,
            self.scan_meter,
        ]

        if all(
            value is None
            for value in meter_values
        ):
            raise ValidationError(
                {
                    "total_meter": (
                        "Debe registrar al menos uno de los contadores."
                    ),
                }
            )

        if (
            self.reference_type != self.ReferenceType.NONE
            and not self.reference_id
            and not self.reference_number
        ):
            raise ValidationError(
                {
                    "reference_number": (
                        "Debe indicar el ID o número del proceso "
                        "relacionado."
                    ),
                }
            )

        if (
            self.reference_type == self.ReferenceType.NONE
            and self.reference_id
        ):
            raise ValidationError(
                {
                    "reference_type": (
                        "Debe seleccionar el tipo de proceso relacionado."
                    ),
                }
            )

        special_reading_types = {
            self.ReadingType.CORRECTION,
            self.ReadingType.RESET,
        }

        if (
            self.reading_type in special_reading_types
            and not self.correction_reason
        ):
            raise ValidationError(
                {
                    "correction_reason": (
                        "Debe indicar el motivo de la corrección "
                        "o reinicio del contador."
                    ),
                }
            )

        if (
            self.is_verified
            and not self.verified_by_id
        ):
            raise ValidationError(
                {
                    "verified_by": (
                        "Debe indicar quién verificó la lectura."
                    ),
                }
            )

        if (
            self.is_verified
            and not self.verified_at
        ):
            raise ValidationError(
                {
                    "verified_at": (
                        "Debe registrar la fecha de verificación."
                    ),
                }
            )

        if (
            not self.is_verified
            and self.verified_by_id
        ):
            raise ValidationError(
                {
                    "verified_by": (
                        "No puede registrar un usuario verificador "
                        "si la lectura no está marcada como verificada."
                    ),
                }
            )

        if (
            not self.is_verified
            and self.verified_at
        ):
            raise ValidationError(
                {
                    "verified_at": (
                        "No puede registrar una fecha de verificación "
                        "si la lectura no está marcada como verificada."
                    ),
                }
            )

        if self.equipment_id:
            model = self.equipment.equipment_model

            if (
                self.color_meter is not None
                and model.color_mode
                == model.ColorMode.MONOCHROME
                and self.color_meter > 0
            ):
                raise ValidationError(
                    {
                        "color_meter": (
                            "El modelo seleccionado es blanco y negro "
                            "y no puede registrar contador color."
                        ),
                    }
                )

            if (
                self.scan_meter is not None
                and not model.has_scan_meter
                and self.scan_meter > 0
            ):
                raise ValidationError(
                    {
                        "scan_meter": (
                            "El modelo seleccionado no utiliza "
                            "contador de escaneo."
                        ),
                    }
                )

        self.calculate_differences()

        if self.reading_type != self.ReadingType.RESET:
            if (
                self.total_difference is not None
                and self.total_difference < 0
            ):
                raise ValidationError(
                    {
                        "total_meter": (
                            "El contador total no puede ser menor que "
                            "la lectura anterior. Utilice el tipo "
                            "'Reinicio o cambio de contador' cuando "
                            "corresponda."
                        ),
                    }
                )

            if (
                self.black_difference is not None
                and self.black_difference < 0
            ):
                raise ValidationError(
                    {
                        "black_meter": (
                            "El contador blanco y negro no puede ser "
                            "menor que la lectura anterior."
                        ),
                    }
                )

            if (
                self.color_difference is not None
                and self.color_difference < 0
            ):
                raise ValidationError(
                    {
                        "color_meter": (
                            "El contador color no puede ser menor que "
                            "la lectura anterior."
                        ),
                    }
                )

            if (
                self.scan_difference is not None
                and self.scan_difference < 0
            ):
                raise ValidationError(
                    {
                        "scan_meter": (
                            "El contador de escaneo no puede ser menor "
                            "que la lectura anterior."
                        ),
                    }
                )

    def save(self, *args, **kwargs):
        """
        Normaliza, calcula diferencias y valida la lectura.
        """

        self.reference_number = str(
            self.reference_number or ""
        ).strip().upper()

        self.correction_reason = str(
            self.correction_reason or ""
        ).strip()

        self.notes = str(
            self.notes or ""
        ).strip()

        self.calculate_differences()
        self.full_clean()

        update_fields = kwargs.get(
            "update_fields"
        )

        if update_fields is not None:
            update_fields = set(
                update_fields
            )

            update_fields.update(
                {
                    "previous_total_meter",
                    "previous_black_meter",
                    "previous_color_meter",
                    "previous_scan_meter",
                    "total_difference",
                    "black_difference",
                    "color_difference",
                    "scan_difference",
                }
            )

            kwargs["update_fields"] = list(
                update_fields
            )

        return super().save(
            *args,
            **kwargs,
        )

    def verify(
        self,
        user,
        save=True,
    ):
        """
        Marca la lectura como revisada y confirmada.
        """

        if user is None:
            raise ValidationError(
                {
                    "verified_by": (
                        "Debe indicar el usuario que verifica "
                        "la lectura."
                    ),
                }
            )

        self.is_verified = True
        self.verified_by = user
        self.verified_at = timezone.now()
        self.updated_by = user

        if save:
            self.save(
                update_fields=[
                    "is_verified",
                    "verified_by",
                    "verified_at",
                    "updated_by",
                    "updated_at",
                ]
            )

        return self

    def apply_to_equipment(
        self,
        user=None,
        save=True,
    ):
        """
        Actualiza los contadores actuales de la ficha del equipo.

        Solo modifica los contadores que estén presentes en la lectura.
        Los valores nulos no reemplazan los contadores actuales.

        Esta función debe ejecutarse desde el serializer, servicio o flujo
        que confirme la lectura.
        """

        if not self.equipment_id:
            raise ValidationError(
                {
                    "equipment": (
                        "La lectura no tiene un equipo relacionado."
                    ),
                }
            )

        equipment = self.equipment

        if self.total_meter is not None:
            equipment.current_total_meter = self.total_meter

        if self.black_meter is not None:
            equipment.current_black_meter = self.black_meter

        if self.color_meter is not None:
            equipment.current_color_meter = self.color_meter

        if self.scan_meter is not None:
            equipment.current_scan_meter = self.scan_meter

        equipment.last_meter_date = self.reading_date
        equipment.last_meter_source = (
            self._get_equipment_meter_source()
        )

        if user:
            equipment.updated_by = user

        if save:
            equipment.save(
                update_fields=[
                    "current_total_meter",
                    "current_black_meter",
                    "current_color_meter",
                    "current_scan_meter",
                    "last_meter_date",
                    "last_meter_source",
                    "updated_by",
                    "updated_at",
                ]
            )

            self.is_applied_to_equipment = True

            if user:
                self.updated_by = user

            self.save(
                update_fields=[
                    "is_applied_to_equipment",
                    "updated_by",
                    "updated_at",
                ]
            )
        else:
            self.is_applied_to_equipment = True

        return equipment

    def _get_equipment_meter_source(self):
        """
        Convierte la fuente de MeterReading al choice utilizado
        en Equipment.
        """

        source_mapping = {
            self.Source.MANUAL: Equipment.MeterSource.MANUAL,
            self.Source.UNLOADING: Equipment.MeterSource.DOWNLOAD,
            self.Source.MOBILE_APP: Equipment.MeterSource.MOBILE_APP,
            self.Source.SNMP: Equipment.MeterSource.SNMP,
            self.Source.REPAIR_ENTRY: Equipment.MeterSource.REPAIR,
            self.Source.REPAIR_EXIT: Equipment.MeterSource.REPAIR,
            self.Source.INSTALLATION: Equipment.MeterSource.INSTALLATION,
            self.Source.REMOVAL: Equipment.MeterSource.REMOVAL,
            self.Source.DELIVERY: Equipment.MeterSource.DELIVERY,
            self.Source.RETURN: Equipment.MeterSource.REMOVAL,
            self.Source.CONTRACT: Equipment.MeterSource.MANUAL,
            self.Source.IMPORTED: Equipment.MeterSource.OTHER,
            self.Source.SYSTEM: Equipment.MeterSource.OTHER,
            self.Source.OTHER: Equipment.MeterSource.OTHER,
        }

        return source_mapping.get(
            self.source,
            Equipment.MeterSource.OTHER,
        )