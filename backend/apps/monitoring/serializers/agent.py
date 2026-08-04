# -*- coding: utf-8 -*-

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction

from rest_framework import serializers

from apps.monitoring.models import (
    MonitoringAgent,
    MonitoringInstallationToken,
)

from .common import MonitoringModelSerializer


class MonitoringAgentSerializer(
    MonitoringModelSerializer
):
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    operating_system_display = serializers.CharField(
        source="get_operating_system_display",
        read_only=True,
    )

    class Meta:
        model = MonitoringAgent

        exclude = (
            "credential_hash",
        )

        read_only_fields = (
            "id",
            "code",
            "credential_prefix",
            "registered_at",
            "activated_at",
            "last_seen_at",
            "last_successful_sync_at",
            "last_error_at",
            "revoked_at",
            "revoked_reason",
            "created_at",
            "updated_at",
            "archived_at",
            "archived_by",
            "archive_reason",
        )


class MonitoringAgentRegistrationSerializer(
    serializers.Serializer
):
    installation_token = serializers.CharField(
        write_only=True,
        trim_whitespace=True,
    )

    device_identifier = serializers.CharField(
        max_length=255,
    )

    name = serializers.CharField(
        max_length=150,
    )

    hostname = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        default="",
    )

    operating_system = serializers.ChoiceField(
        choices=MonitoringAgent.OperatingSystem.choices,
        required=False,
        default=MonitoringAgent.OperatingSystem.UNKNOWN,
    )

    operating_system_version = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        default="",
    )

    architecture = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        default="",
    )

    agent_version = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        default="",
    )

    local_ip_address = serializers.IPAddressField(
        protocol="both",
        required=False,
        allow_null=True,
        default=None,
    )

    mac_address = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        default="",
    )

    server_base_url = serializers.URLField(
        required=False,
        allow_blank=True,
        default="",
    )

    def validate_device_identifier(
        self,
        value,
    ):
        value = str(
            value or ""
        ).strip()

        if len(value) < 8:
            raise serializers.ValidationError(
                "El identificador debe tener como mínimo ocho caracteres."
            )

        return value

    def create(
        self,
        validated_data,
    ):
        raw_token = validated_data.pop(
            "installation_token"
        )

        try:
            validated_token = (
                MonitoringInstallationToken
                .validate_raw_token(
                    raw_token
                )
            )

            with transaction.atomic():
                installation_token = (
                    MonitoringInstallationToken
                    .objects
                    .select_for_update()
                    .select_related(
                        "customer",
                        "branch",
                    )
                    .get(
                        pk=validated_token.pk
                    )
                )

                if not installation_token.matches(
                    raw_token
                ):
                    raise DjangoValidationError(
                        "El token de instalación no es válido."
                    )

                if not installation_token.can_be_used:
                    raise DjangoValidationError(
                        "El token de instalación ya no puede utilizarse."
                    )

                agent, raw_credential = (
                    MonitoringAgent.register_agent(
                        installation_token=installation_token,
                        **validated_data,
                    )
                )

        except MonitoringInstallationToken.DoesNotExist as exc:
            raise serializers.ValidationError(
                {
                    "installation_token": (
                        "El token de instalación no existe."
                    ),
                }
            ) from exc

        except DjangoValidationError as exc:
            detail = (
                getattr(
                    exc,
                    "message_dict",
                    None,
                )
                or {
                    "detail": exc.messages,
                }
            )

            raise serializers.ValidationError(
                detail
            ) from exc

        agent.raw_credential = raw_credential

        return agent

    def to_representation(
        self,
        instance,
    ):
        return {
            "message": (
                "Agente registrado correctamente."
            ),
            "agent": MonitoringAgentSerializer(
                instance,
                context=self.context,
            ).data,
            "credential": getattr(
                instance,
                "raw_credential",
                None,
            ),
            "credential_prefix": (
                instance.credential_prefix
            ),
            "warning": (
                "La credencial completa se muestra una sola vez."
            ),
        }


class MonitoringAgentHeartbeatSerializer(
    serializers.Serializer
):
    agent_version = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        default="",
    )

    hostname = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        default="",
    )

    local_ip_address = serializers.IPAddressField(
        protocol="both",
        required=False,
        allow_null=True,
    )

    public_ip_address = serializers.IPAddressField(
        protocol="both",
        required=False,
        allow_null=True,
    )

    last_error_message = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    def update(
        self,
        instance,
        validated_data,
    ):
        instance.register_heartbeat(
            **validated_data
        )

        return instance


class MonitoringAgentCredentialSerializer(
    serializers.Serializer
):
    credential = serializers.CharField(
        write_only=True,
        trim_whitespace=True,
    )

    def validate_credential(
        self,
        value,
    ):
        try:
            return (
                MonitoringAgent
                .authenticate_credential(
                    value
                )
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.messages
            ) from exc