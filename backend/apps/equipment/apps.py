# -*- coding: utf-8 -*-
from django.apps import AppConfig


class EquipmentConfig(AppConfig):
    """
    Configuración de la aplicación de equipos.

    Esta aplicación administra:

    - Tipos de equipos.
    - Marcas.
    - Familias técnicas.
    - Modelos.
    - Máquinas físicas por número de serie.
    - Importaciones y lotes.
    - Costos de compra e ingreso de equipos.
    - Estados técnicos.
    - Estados comerciales y logísticos.
    - Disponibilidad.
    - Historial de movimientos.
    - Lecturas de contadores.
    - Documentos relacionados con equipos.
    - Tipos de componentes.
    - Unidades técnicas.
    - Subpartes y repuestos.
    - Tóners y consumibles.
    - Accesorios con serie individual.
    - Compatibilidades por familia o modelo.
    - Historial de componentes instalados y retirados.

    El catálogo de componentes es descriptivo y técnico.
    No administra stock, almacenes, cantidades ni precios
    de componentes.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.equipment"
    verbose_name = "Equipos y máquinas"