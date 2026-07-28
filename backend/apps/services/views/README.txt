COPIER OS - VIEWS DEL FLUJO DE PEDIDOS DE REPUESTOS

Copiar los archivos .py en:

backend/apps/services/views/

El archivo __init__.py del ZIP exporta únicamente las vistas nuevas.
Debe combinarse con las importaciones que ya tenga el __init__.py actual
del módulo services.

No ejecutar migraciones por estos archivos.

El siguiente bloque debe integrar:
- urls.py
- permisos por área y rol
- servicios transaccionales de cambio de estado
- creación automática de la OS de instalación
