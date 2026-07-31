# Copier OS

Estructura inicial:

- `backend/`: Django y API.
- `frontend/`: Vue 3 con Vite.
- `docker-compose.yml`: PostgreSQL.
- `iniciar-backend.bat`: inicia Django.
- `iniciar-frontend.bat`: inicia Vue.

## Primera ejecución

1. Confirma que PostgreSQL está corriendo.
2. Abre `iniciar-backend.bat`.
3. Abre `iniciar-frontend.bat` en otra ventana.
4. Visita `http://localhost:5173`.

Backend: `http://127.0.0.1:8000`
Frontend: `http://localhost:5173`
Ejecutar servidor: .\.venv\Scripts\python.exe manage.py runserver