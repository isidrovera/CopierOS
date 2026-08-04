# Modelos pendientes desde report_schedule.py

Archivos incluidos:

1. report_schedule.py
2. report_execution.py
3. monitoring_configuration.py
4. agent_configuration_version.py
5. device_polling_state.py
6. monitoring_ingestion_batch.py
7. data_retention_policy.py
8. __init__.py parcial

Copiar los siete modelos dentro de:

backend/apps/monitoring/models/

El __init__.py incluido solo contiene los siete modelos nuevos. Debe fusionarse con el __init__.py que ya importa los modelos anteriores.

Después ejecutar:

python manage.py makemigrations monitoring
python manage.py check
python manage.py migrate

Antes de migrar, revisar que PartnerBranch use el campo `partner`, y que MonitoringAgent, MonitoringNetwork y MonitoredDevice tengan las relaciones `customer`, `branch`, `agent` y `network` usadas en los modelos.
