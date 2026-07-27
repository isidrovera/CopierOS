# -*- coding: utf-8 -*-
from django.apps import AppConfig


class RentalsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.rentals"
    verbose_name = "Administración de alquileres"

    def ready(self):
        """
        Inicialización del módulo de alquileres.

        Este módulo administra:
        - Almacenes de ANDES.
        - Equipos destinados al alquiler.
        - Ingresos y movimientos internos.
        - Preparación de equipos.
        - Contratos de alquiler.
        - Asignaciones a clientes y sedes.
        - Instalaciones.
        - Retiros.
        - Reemplazos.
        - Documentos relacionados.

        Las órdenes de servicio, evidencias técnicas,
        solicitudes de repuestos y atenciones de campo
        se administrarán en apps.services.
        """
        return None