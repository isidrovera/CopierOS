# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path



def health(request):
    """
    Endpoint básico para comprobar que el backend
    de Copier OS está funcionando.
    """

    return JsonResponse(
        {
            "status": "ok",
            "sistema": "Copier OS",
            "backend": "Django",
        }
    )


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "api/health/",
        health,
        name="health",
    ),
    path(
        "api/users/",
        include("apps.users.urls"),
    ),
    path(
        "api/partners/",
        include("apps.partners.urls"),
    ),
    path(
        "api/equipment/",
        include("apps.equipment.urls"),
    ),
    path(
        "api/repairs/",
        include("apps.repairs.urls"),
    ),
    path(
        "api/rentals/",
        include("apps.rentals.urls"),
    ),
    path(
        "api/services/",
        include("apps.services.urls"),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )