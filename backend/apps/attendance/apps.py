# -*- coding: utf-8 -*-

from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    """
    Configuración principal del módulo de asistencia.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.attendance"
    label = "attendance"
    verbose_name = "Asistencia y control operativo"

    def ready(self):
        """
        Punto de inicialización del módulo.

        Aquí se importarán las señales cuando sean creadas.
        La importación se mantiene dentro de ready() para evitar
        cargas prematuras y dependencias circulares.
        """

        try:
            from . import signals  # noqa: F401
        except ImportError:
            # Durante la creación inicial del módulo puede que
            # signals.py todavía no exista.
            pass