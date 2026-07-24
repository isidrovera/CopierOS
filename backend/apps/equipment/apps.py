# -*- coding: utf-8 -*-
from django.apps import AppConfig


class EquipmentConfig(AppConfig):
    """
    Configuración de la aplicación de equipos.

    Esta aplicación administrará:

    - Tipos de equipos.
    - Marcas.
    - Modelos.
    - Máquinas físicas por número de serie.
    - Importaciones y lotes.
    - Costos de compra e ingreso.
    - Estados técnicos.
    - Estados comerciales y logísticos.
    - Disponibilidad.
    - Historial de movimientos.
    - Lecturas de contadores.
    - Documentos relacionados con los equipos.

    Los accesorios, unidades técnicas, reparaciones y contratos
    se manejarán posteriormente en módulos independientes,
    relacionados con los equipos mediante sus UUID.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.equipment"
    verbose_name = "Equipos y máquinas"