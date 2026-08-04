# -*- coding: utf-8 -*-

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)

from rest_framework import serializers

from apps.monitoring.models import (
    SNMPCredential,
)


class SNMPCredentialSerializer(
    serializers.ModelSerializer
):
    community = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        trim_whitespace=False,
    )

    auth_password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        trim_whitespace=False,
    )

    privacy_password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        trim_whitespace=False,
    )

    has_community = serializers.SerializerMethodField()

    has_auth_password = serializers.SerializerMethodField()

    has_privacy_password = serializers.SerializerMethodField()

    class Meta:
        model = SNMPCredential

        exclude = (
            "encrypted_community",
            "encrypted_auth_password",
            "encrypted_privacy_password",
        )

        read_only_fields = (
            "id",
            "successful_device_count",
            "failed_attempt_count",
            "last_success_at",
            "last_failure_at",
            "last_failure_message",
            "secret_fingerprint",
            "created_at",
            "updated_at",
            "archived_at",
            "archived_by",
            "archive_reason",
        )

    def get_has_community(
        self,
        obj,
    ):
        return bool(
            obj.encrypted_community
        )

    def get_has_auth_password(
        self,
        obj,
    ):
        return bool(
            obj.encrypted_auth_password
        )

    def get_has_privacy_password(
        self,
        obj,
    ):
        return bool(
            obj.encrypted_privacy_password
        )

    def validate(
        self,
        attrs,
    ):
        snmp_version = attrs.get(
            "snmp_version",
            getattr(
                self.instance,
                "snmp_version",
                None,
            ),
        )

        security_level = attrs.get(
            "security_level",
            getattr(
                self.instance,
                "security_level",
                "no_auth_no_priv",
            ),
        )

        community = attrs.get(
            "community"
        )

        auth_password = attrs.get(
            "auth_password"
        )

        privacy_password = attrs.get(
            "privacy_password"
        )

        has_current_community = bool(
            getattr(
                self.instance,
                "encrypted_community",
                "",
            )
        )

        has_current_auth_password = bool(
            getattr(
                self.instance,
                "encrypted_auth_password",
                "",
            )
        )

        has_current_privacy_password = bool(
            getattr(
                self.instance,
                "encrypted_privacy_password",
                "",
            )
        )

        if (
            snmp_version in (
                "1",
                "2c",
            )
            and not community
            and not has_current_community
        ):
            raise serializers.ValidationError(
                {
                    "community": (
                        "La comunidad SNMP es obligatoria "
                        "para SNMP v1 y v2c."
                    ),
                }
            )

        if (
            snmp_version == "3"
            and security_level in (
                "auth_no_priv",
                "auth_priv",
            )
            and not auth_password
            and not has_current_auth_password
        ):
            raise serializers.ValidationError(
                {
                    "auth_password": (
                        "La clave de autenticación es obligatoria "
                        "para el nivel de seguridad seleccionado."
                    ),
                }
            )

        if (
            snmp_version == "3"
            and security_level == "auth_priv"
            and not privacy_password
            and not has_current_privacy_password
        ):
            raise serializers.ValidationError(
                {
                    "privacy_password": (
                        "La clave de privacidad es obligatoria "
                        "para el nivel authPriv."
                    ),
                }
            )

        return attrs

    def create(
        self,
        validated_data,
    ):
        community = validated_data.pop(
            "community",
            None,
        )

        auth_password = validated_data.pop(
            "auth_password",
            None,
        )

        privacy_password = validated_data.pop(
            "privacy_password",
            None,
        )

        instance = SNMPCredential(
            **validated_data
        )

        if community is not None:
            instance.set_community(
                community
            )

        if auth_password is not None:
            instance.set_auth_password(
                auth_password
            )

        if privacy_password is not None:
            instance.set_privacy_password(
                privacy_password
            )

        try:
            instance.full_clean()
            instance.save()

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

        return instance

    def update(
        self,
        instance,
        validated_data,
    ):
        community = validated_data.pop(
            "community",
            None,
        )

        auth_password = validated_data.pop(
            "auth_password",
            None,
        )

        privacy_password = validated_data.pop(
            "privacy_password",
            None,
        )

        for field_name, value in validated_data.items():
            setattr(
                instance,
                field_name,
                value,
            )

        if community is not None:
            instance.set_community(
                community
            )

        if auth_password is not None:
            instance.set_auth_password(
                auth_password
            )

        if privacy_password is not None:
            instance.set_privacy_password(
                privacy_password
            )

        try:
            instance.full_clean()
            instance.save()

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

        return instance