COPIER OS - LÓGICA DE NEGOCIO PARA PEDIDOS DE REPUESTOS

Copiar la carpeta services dentro de:

backend/apps/services/services/

Archivos incluidos:
- workflow_utils.py
- part_notification_service.py
- part_request_workflow.py
- part_stock_workflow.py
- part_transfer_workflow.py
- part_installation_workflow.py
- __init__.py

Flujos cubiertos:
- envío a gerencia;
- evaluación;
- solicitud y respuesta de información;
- reevaluación;
- aprobación total, parcial o rechazo;
- revisión y reserva de stock;
- partes reutilizables y equipo donante;
- preparación logística;
- cadena de custodia;
- retiro y recepción;
- creación automática de OS de instalación;
- instalación por artículo;
- historial real por equipo y contador;
- cierre del pedido;
- notificaciones internas.

No modificar todavía urls.py, admin.py ni views existentes.
Esos archivos se integrarán en el siguiente bloque.
