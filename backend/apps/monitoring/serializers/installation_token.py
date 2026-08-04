# -*- coding: utf-8 -*-

from django.utils import timezone

from rest_framework import serializers

from apps.monitoring.models import (
    MonitoringInstallationToken,
)

from .common import MonitoringModelSerializer


class MonitoringInstallationTokenSerializer(
    MonitoringModelSerializer
):
    is_expired = serializers.BooleanField(
        read_only=True,
    )

    has_available_uses = serializers.BooleanField(
        read_only=True,
    )

    can_be_used = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = MonitoringInstallationToken

        exclude = (
            "token_hash",
        )

        read_only_fields = (
            "id",
            "token_prefix",
            "used_count",
            "revoked_at",
            "revoked_reason",
            "last_used_at",
            "created_at",
            "updated_at",
            "archived_at",
            "archived_by",
            "archive_reason",
        )


class MonitoringInstallationTokenCreateSerializer(
    serializers.Serializer
):
    customer = serializers.PrimaryKeyRelatedField(
        queryset=(
            MonitoringInstallationToken
            ._meta
            .get_field(
                "customer"
            )
            .remote_field
            .model
            .objects
            .all()
        ),
    )

    branch = serializers.PrimaryKeyRelatedField(
        queryset=(
            MonitoringInstallationToken
            ._meta
            .get_field(
                "branch"
            )
            .remote_field
            .model
            .objects
            .all()
        ),
        required=False,
        allow_null=True,
    )

    name = serializers.CharField(
        max_length=150,
    )

    expires_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    maximum_uses = serializers.IntegerField(
        min_value=1,
        default=1,
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    def validate_expires_at(
        self,
        value,
    ):
        if (
            value
            and value <= timezone.now()
        ):
            raise serializers.ValidationError(
                "La fecha de vencimiento debe ser futura."
            )

        return value

    def validate(
        self,
        attrs,
    ):
        customer = attrs[
            "customer"
        ]

        branch = attrs.get(
            "branch"
        )

        if (
            branch
            and branch.partner_id != customer.id
        ):
            raise serializers.ValidationError(
                {
                    "branch": (
                        "La sede seleccionada no pertenece "
                        "al cliente indicado."
                    ),
                }
            )

        return attrs

    def create(
        self,
        validated_data,
    ):
        request = self.context.get(
            "request"
        )

        user = None

        if (
            request
            and request.user
            and request.user.is_authenticated
        ):
            user = request.user

        instance, raw_token = (
            MonitoringInstallationToken
            .create_token(
                user=user,
                **validated_data,
            )
        )

        instance.raw_token = raw_token

        return instance

    def to_representation(
        self,
        instance,
    ):
        data = (
            MonitoringInstallationTokenSerializer(
                instance,
                context=self.context,
            ).data
        )

        data["token"] = getattr(
            instance,
            "raw_token",
            None,
        )

        data["warning"] = (
            "El token completo se muestra una sola vez. "
            "Guárdalo de forma segura."
        )

        return data


class MonitoringInstallationTokenValidateSerializer(
    serializers.Serializer
):
    token = serializers.CharField(
        write_only=True,
        trim_whitespace=True,
    )

    def validate_token(
        self,
        value,
    ):
        try:
            return (
                MonitoringInstallationToken
                .validate_raw_token(
                    value
                )
            )

        except Exception as exc:
            messages = getattr(
                exc,
                "messages",
                [
                    str(exc),
                ],
            )

            raise serializers.ValidationError(
                messages
            ) from exc

    def to_representation(
        self,
        instance,
    ):
        token = self.validated_data[
            "token"
        ]

        return (
            MonitoringInstallationTokenSerializer(
                token,
                context=self.context,
            ).data
        )