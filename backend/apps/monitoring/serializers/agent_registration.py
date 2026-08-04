# -*- coding: utf-8 -*-

from rest_framework import serializers

from apps.monitoring.models import MonitoringAgent


class MonitoringAgentRegistrationSerializer(
    serializers.Serializer
):
    installation_token = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        write_only=True,
    )

    device_identifier = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=255,
    )

    name = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=150,
    )

    hostname = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        max_length=150,
        default="",
    )

    operating_system = serializers.ChoiceField(
        required=False,
        choices=MonitoringAgent.OperatingSystem.choices,
        default=MonitoringAgent.OperatingSystem.UNKNOWN,
    )

    operating_system_version = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        max_length=150,
        default="",
    )

    architecture = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        max_length=50,
        default="",
    )

    agent_version = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        max_length=50,
        default="",
    )

    local_ip_address = serializers.IPAddressField(
        required=False,
        allow_null=True,
        protocol="both",
        default=None,
    )

    mac_address = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        max_length=50,
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
        normalized_value = str(
            value or ""
        ).strip()

        if len(normalized_value) < 8:
            raise serializers.ValidationError(
                "El identificador de instalación debe tener "
                "como mínimo ocho caracteres."
            )

        return normalized_value

    def validate_name(
        self,
        value,
    ):
        normalized_value = str(
            value or ""
        ).strip()

        if not normalized_value:
            raise serializers.ValidationError(
                "El nombre del agente es obligatorio."
            )

        return normalized_value

    def validate_mac_address(
        self,
        value,
    ):
        return str(
            value or ""
        ).strip().upper()