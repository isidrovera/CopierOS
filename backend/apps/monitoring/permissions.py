# -*- coding: utf-8 -*-

from rest_framework.permissions import BasePermission


class IsMonitoringAgent(BasePermission):
    """
    Permite acceso únicamente a solicitudes autenticadas
    mediante MonitoringAgentCredentialAuthentication.
    """

    message = "Se requiere una credencial válida de agente."

    def has_permission(self, request, view):
        user = getattr(
            request,
            "user",
            None,
        )

        return bool(
            user
            and getattr(
                user,
                "is_authenticated",
                False,
            )
            and getattr(
                user,
                "agent",
                None,
            )
        )


class IsMonitoringAdministrator(BasePermission):
    """
    Permite acceso a usuarios administrativos autenticados.
    """

    message = "Se requieren permisos administrativos."

    def has_permission(self, request, view):
        user = getattr(
            request,
            "user",
            None,
        )

        return bool(
            user
            and getattr(
                user,
                "is_authenticated",
                False,
            )
            and (
                getattr(
                    user,
                    "is_staff",
                    False,
                )
                or getattr(
                    user,
                    "is_superuser",
                    False,
                )
            )
        )
