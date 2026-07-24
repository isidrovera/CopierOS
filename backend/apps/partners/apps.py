# -*- coding: utf-8 -*-
from django.apps import AppConfig


class PartnersConfig(AppConfig):
    """
    Configuración de la aplicación de terceros comerciales.

    Esta aplicación administrará en un solo módulo:

    - Clientes de alquiler.
    - Clientes de venta.
    - Clientes de servicio técnico.
    - Proveedores nacionales.
    - Proveedores extranjeros.
    - Distribuidores.
    - Empresas que cumplan varios roles simultáneamente.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.partners"
    verbose_name = "Clientes, proveedores y distribuidores"