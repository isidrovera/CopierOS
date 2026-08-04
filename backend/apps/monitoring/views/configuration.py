# -*- coding: utf-8 -*-

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.monitoring.authentication import (
    MonitoringAgentCredentialAuthentication,
)
from apps.monitoring.models import (
    AgentConfigurationVersion,
    DeviceProfileAssignment,
    MonitoringConfiguration,
    MonitoringNetwork,
    SNMPCredential,
)
from apps.monitoring.permissions import (
    IsMonitoringAgent,
)
from apps.monitoring.serializers import (
    AgentConfigurationVersionSerializer,
    DeviceProfileAssignmentSerializer,
    MonitoringConfigurationSerializer,
    MonitoringNetworkSerializer,
    SNMPCredentialSerializer,
)


class MonitoringAgentConfigurationAPIView(
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
        agent = request.user.agent

        networks = (
            MonitoringNetwork.objects
            .filter(
                agent=agent,
                archived_at__isnull=True,
                is_enabled=True,
            )
            .order_by(
                "priority",
                "name",
            )
        )

        credentials = (
            SNMPCredential.objects
            .filter(
                agent=agent,
                archived_at__isnull=True,
                is_enabled=True,
            )
            .order_by(
                "priority",
                "name",
            )
        )

        assignments = (
            DeviceProfileAssignment.objects
            .select_related(
                "device",
                "profile",
            )
            .filter(
                agent=agent,
                archived_at__isnull=True,
                is_current=True,
            )
        )

        global_configuration = (
            MonitoringConfiguration.objects
            .filter(
                archived_at__isnull=True,
            )
            .order_by(
                "-updated_at",
            )
            .first()
        )

        latest_version = (
            AgentConfigurationVersion.objects
            .filter(
                agent=agent,
                archived_at__isnull=True,
            )
            .order_by(
                "-created_at",
            )
            .first()
        )

        agent.last_configuration_sync_at = (
            agent.last_seen_at
        )
        agent.save(
            update_fields=[
                "last_configuration_sync_at",
                "updated_at",
            ]
        )

        return Response(
            {
                "agent_id": str(
                    agent.id
                ),
                "agent_code": agent.code,
                "configuration_version": (
                    agent.configuration_version
                ),
                "intervals": {
                    "heartbeat_seconds": (
                        agent
                        .heartbeat_interval_seconds
                    ),
                    "discovery_minutes": (
                        agent
                        .discovery_interval_minutes
                    ),
                    "monitoring_minutes": (
                        agent
                        .monitoring_interval_minutes
                    ),
                    "full_inventory_hours": (
                        agent
                        .full_inventory_interval_hours
                    ),
                },
                "networks": MonitoringNetworkSerializer(
                    networks,
                    many=True,
                    context={
                        "request": request,
                    },
                ).data,
                "credentials": SNMPCredentialSerializer(
                    credentials,
                    many=True,
                    context={
                        "request": request,
                    },
                ).data,
                "profile_assignments": (
                    DeviceProfileAssignmentSerializer(
                        assignments,
                        many=True,
                        context={
                            "request": request,
                        },
                    ).data
                ),
                "global_configuration": (
                    MonitoringConfigurationSerializer(
                        global_configuration,
                        context={
                            "request": request,
                        },
                    ).data
                    if global_configuration
                    else None
                ),
                "latest_configuration_version": (
                    AgentConfigurationVersionSerializer(
                        latest_version,
                        context={
                            "request": request,
                        },
                    ).data
                    if latest_version
                    else None
                ),
            }
        )
