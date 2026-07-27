# -*- coding: utf-8 -*-
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "solo-desarrollo-cambiar",
)

DEBUG = (
    os.getenv(
        "DJANGO_DEBUG",
        "True",
    ).lower()
    == "true"
)

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",

    "apps.users.apps.UsersConfig",
    "apps.partners.apps.PartnersConfig",
    "apps.equipment.apps.EquipmentConfig",
    "apps.repairs.apps.RepairsConfig",
    "apps.rentals.apps.RentalsConfig",
    "apps.services.apps.ServicesConfig",
]


AUTH_USER_MODEL = "users.User"


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends.django.DjangoTemplates"
        ),
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                (
                    "django.template.context_processors.request"
                ),
                (
                    "django.contrib.auth.context_processors.auth"
                ),
                (
                    "django.contrib.messages.context_processors.messages"
                ),
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": (
            "django.db.backends.postgresql"
        ),
        "NAME": os.getenv(
            "DB_NAME",
            "copieros",
        ),
        "USER": os.getenv(
            "DB_USER",
            "copieros",
        ),
        "PASSWORD": os.getenv(
            "DB_PASSWORD",
            "copieros_dev_password",
        ),
        "HOST": os.getenv(
            "DB_HOST",
            "127.0.0.1",
        ),
        "PORT": os.getenv(
            "DB_PORT",
            "5432",
        ),
    }
}


AUTH_PASSWORD_VALIDATORS = []


LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True


STATIC_URL = "static/"


MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)


CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        (
            "rest_framework.authentication."
            "TokenAuthentication"
        ),
    ],
}