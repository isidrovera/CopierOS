COPIER OS - SERIALIZERS DEL FLUJO DE PEDIDOS DE REPUESTOS

Copiar los archivos .py dentro de:

backend/apps/services/serializers/

IMPORTANTE:
1. Este paquete contiene únicamente los serializers nuevos y el __init__.py
   actualizado para exportarlos.
2. Mantener el archivo existente:
   backend/apps/services/serializers/common.py
3. No ejecutar migraciones por agregar serializers.
4. Después de copiar, ejecutar:
   python manage.py check
5. Las vistas y URLs se integrarán en el siguiente bloque.
