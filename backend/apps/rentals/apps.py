# -*- coding: utf-8 -*-
from django.apps import AppConfig


class RentalsConfig(AppConfig):
    """
    Configuración del módulo de alquileres y servicios técnicos
    de ANDES.

    Este módulo administrará:

    - Almacenes de máquinas destinadas a alquiler.
    - Ingreso de equipos comprados a CORAPSAC.
    - Ingreso de equipos comprados a proveedores externos.
    - Preparación técnica de equipos para alquiler.
    - Máquinas disponibles para alquiler.
    - Máquinas con problemas.
    - Máquinas destinadas a partes.
    - Máquinas retiradas de clientes.
    - Asignación de equipos a clientes, sedes y contactos.
    - Instalaciones.
    - Retiros, reemplazos y retornos.
    - Órdenes de servicio técnico.
    - Servicios de máquinas alquiladas por ANDES.
    - Servicios de máquinas propiedad de clientes externos.
    - Diagnósticos técnicos por orden de servicio.
    - Checklist técnico por orden de servicio.
    - Evidencias fotográficas por orden de servicio.
    - Solicitudes de repuestos desde órdenes de servicio.
    - Historial de repuestos por equipo.
    - Lecturas de contadores por equipo.
    - Validación de contadores contra lecturas anteriores.
    - Historial técnico y operativo de cada equipo.

    Los precios y el stock de repuestos no serán administrados
    en este módulo, porque se controlan mediante otro software.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.rentals"
    verbose_name = "Alquileres y servicios técnicos"