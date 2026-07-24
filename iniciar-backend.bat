@echo off
cd /d "%~dp0backend"

if not exist ".venv" (
    py -m venv .venv
)

call .venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
