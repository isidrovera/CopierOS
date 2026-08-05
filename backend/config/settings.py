# -*- coding: utf-8 -*-

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent


# En desarrollo carga:
# backend/.env
#
# En Dokploy, las variables configuradas en Environment
# tendrán prioridad sobre este archivo.
load_dotenv(
    dotenv_path=BASE_DIR / ".env",
)


def env_bool(
    name: str,
    default: bool = False,
) -> bool:
    """
    Convierte una variable de entorno a booleano.
    """

    value = os.getenv(
        name,
        str(default),
    )

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def env_list(
    name: str,
    default: str = "",
) -> list[str]:
    """
    Convierte una variable separada por comas en una lista.

    Ejemplo:
    DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,api.example.com
    """

    value = os.getenv(
        name,
        default,
    )

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


DEBUG = env_bool(
    "DJANGO_DEBUG",
    True,
)


SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "solo-desarrollo-cambiar",
)


if not DEBUG and SECRET_KEY == "solo-desarrollo-cambiar":
    raise RuntimeError(
        "DJANGO_SECRET_KEY debe configurarse en producción."
    )


# Clave Fernet utilizada para cifrar credenciales SNMP.
COPIEROS_MONITORING_ENCRYPTION_KEY = os.getenv(
    "COPIEROS_MONITORING_ENCRYPTION_KEY",
    "",
)


ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost",
)


CSRF_TRUSTED_ORIGINS = env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "",
)


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
    "apps.monitoring.apps.MonitoringConfig",
]


AUTH_USER_MODEL = "users.User"


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise debe estar inmediatamente después
    # de SecurityMiddleware.
    "whitenoise.middleware.WhiteNoiseMiddleware",

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

ASGI_APPLICATION = "config.asgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
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
        "CONN_MAX_AGE": int(
            os.getenv(
                "DB_CONN_MAX_AGE",
                "60",
            )
        ),
        "OPTIONS": {
            "connect_timeout": int(
                os.getenv(
                    "DB_CONNECT_TIMEOUT",
                    "10",
                )
            ),
        },
    }
}


AUTH_PASSWORD_VALIDATORS = []


LANGUAGE_CODE = "es-pe"

TIME_ZONE = "America/Lima"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


STORAGES = {
    "default": {
        "BACKEND": (
            "django.core.files.storage."
            "FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    (
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    ),
)


CORS_ALLOW_CREDENTIALS = env_bool(
    "CORS_ALLOW_CREDENTIALS",
    True,
)


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        (
            "rest_framework.authentication."
            "TokenAuthentication"
        ),
    ],
}


# Nginx Proxy Manager enviará esta cabecera cuando
# el acceso público utilice HTTPS.
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)


USE_X_FORWARDED_HOST = True


SESSION_COOKIE_SECURE = env_bool(
    "DJANGO_SESSION_COOKIE_SECURE",
    not DEBUG,
)


CSRF_COOKIE_SECURE = env_bool(
    "DJANGO_CSRF_COOKIE_SECURE",
    not DEBUG,
)


SECURE_SSL_REDIRECT = env_bool(
    "DJANGO_SECURE_SSL_REDIRECT",
    False,
)


SECURE_CONTENT_TYPE_NOSNIFF = True


X_FRAME_OPTIONS = "DENY"