# -*- coding: utf-8 -*-

from dataclasses import dataclass

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import authentication
from rest_framework import exceptions

from apps.monitoring.models import MonitoringAgent


@dataclass
class MonitoringAgentPrincipal:
    """
    Principal autenticado que representa a un agente de monitoreo.

    No reemplaza al modelo de usuario de Django. Solo permite que DRF
    trate la credencial del agente como una identidad autenticada.
    """

    agent: MonitoringAgent

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def pk(self):
        return self.agent.pk

    @property
    def id(self):
        return self.agent.id

    def __str__(self):
        return str(self.agent)


class MonitoringAgentCredentialAuthentication(
    authentication.BaseAuthentication
):
    """
    Autenticación para agentes.

    Formas admitidas:

    Authorization: Agent <credencial>
    X-Agent-Credential: <credencial>
    """

    keyword = "Agent"
    header_name = "HTTP_X_AGENT_CREDENTIAL"

    def authenticate(self, request):
        raw_credential = self._get_raw_credential(request)

        if not raw_credential:
            return None

        try:
            agent = MonitoringAgent.authenticate_credential(
                raw_credential
            )
        except DjangoValidationError as exc:
            message = (
                exc.messages[0]
                if getattr(exc, "messages", None)
                else str(exc)
            )
            raise exceptions.AuthenticationFailed(
                message
            ) from exc

        principal = MonitoringAgentPrincipal(
            agent=agent,
        )

        return (
            principal,
            raw_credential,
        )

    def authenticate_header(self, request):
        return self.keyword

    def _get_raw_credential(self, request):
        custom_header = str(
            request.META.get(
                self.header_name,
                "",
            )
            or ""
        ).strip()

        if custom_header:
            return custom_header

        authorization = authentication.get_authorization_header(
            request
        ).decode("utf-8").strip()

        if not authorization:
            return ""

        parts = authorization.split(
            None,
            1,
        )

        if len(parts) != 2:
            return ""

        keyword, credential = parts

        if keyword.lower() != self.keyword.lower():
            return ""

        return credential.strip()
