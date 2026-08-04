# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.monitoring.authentication import (
    MonitoringAgentCredentialAuthentication,
)
from apps.monitoring.models import MonitoringAgent
from apps.monitoring.permissions import (
    IsMonitoringAgent,
)
from apps.monitoring.serializers import (
    MonitoringAgentHeartbeatSerializer,
    MonitoringAgentRegistrationSerializer,
    MonitoringAgentSerializer,
)
from .common import MonitoringAdminModelViewSet


class MonitoringAgentViewSet(
    MonitoringAdminModelViewSet
):
    queryset = (
        MonitoringAgent.objects
        .select_related(
            "customer",
            "branch",
            "installation_token",
        )
        .all()
    )
    serializer_class = MonitoringAgentSerializer


class MonitoringAgentRegistrationAPIView(
    APIView
):
    authentication_classes = []
    permission_classes = [
        AllowAny,
    ]

    def post(
        self,
        request,
        *args,
        **kwargs,
    ):
        serializer = (
            MonitoringAgentRegistrationSerializer(
                data=request.data,
                context={
                    "request": request,
                },
            )
        )
        serializer.is_valid(
            raise_exception=True,
        )
        agent = serializer.save()

        return Response(
            serializer.to_representation(
                agent
            ),
            status=status.HTTP_201_CREATED,
        )


class MonitoringAgentHeartbeatAPIView(
    APIView
):
    authentication_classes = [
        MonitoringAgentCredentialAuthentication,
    ]
    permission_classes = [
        IsMonitoringAgent,
    ]

    def post(
        self,
        request,
        *args,
        **kwargs,
    ):
        agent = request.user.agent

        serializer = MonitoringAgentHeartbeatSerializer(
            instance=agent,
            data=request.data,
            partial=True,
            context={
                "request": request,
            },
        )
        serializer.is_valid(
            raise_exception=True,
        )
        agent = serializer.save()

        return Response(
            {
                "message": (
                    "Heartbeat registrado correctamente."
                ),
                "agent": MonitoringAgentSerializer(
                    agent,
                    context={
                        "request": request,
                    },
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class MonitoringAgentAuthenticationTestAPIView(
    APIView
):
    authentication_classes = [
        MonitoringAgentCredentialAuthentication,
    ]
    permission_classes = [
        IsMonitoringAgent,
    ]

    def get(
        self,
        request,
        *args,
        **kwargs,
    ):
        return Response(
            {
                "authenticated": True,
                "agent": MonitoringAgentSerializer(
                    request.user.agent,
                    context={
                        "request": request,
                    },
                ).data,
            }
        )
