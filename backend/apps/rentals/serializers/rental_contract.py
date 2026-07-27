# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.rentals.models import (
    RentalAssignment,
    RentalContract,
)


class RentalContractSerializer(serializers.ModelSerializer):
    """
    Serializer principal para contratos de alquiler.
    """

    customer_name = serializers.SerializerMethodField()
    main_branch_name = serializers.SerializerMethodField()
    main_contact_name = serializers.SerializerMethodField()

    contract_type_display = serializers.CharField(
        source="get_contract_type_display",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    equipment_count = serializers.SerializerMethodField()
    active_equipment_count = serializers.SerializerMethodField()

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    archived_by_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RentalContract
        fields = [
            "id",
            "code",
            "contract_number",
            "customer",
            "customer_name",
            "main_branch",
            "main_branch_name",
            "main_contact",
            "main_contact_name",
            "contract_type",
            "contract_type_display",
            "status",
            "status_display",
            "start_date",
            "end_date",
            "approved_at",
            "activated_at",
            "suspended_at",
            "terminated_at",
            "external_reference",
            "service_conditions",
            "customer_requirements",
            "suspension_reason",
            "termination_reason",
            "cancellation_reason",
            "notes",
            "equipment_count",
            "active_equipment_count",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_at",
            "archived_by",
            "archived_by_name",
            "archived_reason",
            "is_archived",
        ]
        read_only_fields = [
            "id",
            "approved_at",
            "activated_at",
            "suspended_at",
            "terminated_at",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        ]

    def get_customer_name(self, obj):
        if not obj.customer:
            return ""

        return str(obj.customer)

    def get_main_branch_name(self, obj):
        if not obj.main_branch:
            return ""

        return str(obj.main_branch)

    def get_main_contact_name(self, obj):
        if not obj.main_contact:
            return ""

        return str(obj.main_contact)

    def get_equipment_count(self, obj):
        return obj.assignments.filter(
            archived_at__isnull=True,
        ).count()

    def get_active_equipment_count(self, obj):
        return obj.assignments.filter(
            archived_at__isnull=True,
            status__in=[
                RentalAssignment.Status.RESERVED,
                RentalAssignment.Status.INSTALLATION_PENDING,
                RentalAssignment.Status.INSTALLED,
                RentalAssignment.Status.ACTIVE,
                RentalAssignment.Status.REMOVAL_PENDING,
            ],
        ).count()

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return ""

        return (
            obj.created_by.get_full_name()
            or obj.created_by.username
        )

    def get_updated_by_name(self, obj):
        if not obj.updated_by:
            return ""

        return (
            obj.updated_by.get_full_name()
            or obj.updated_by.username
        )

    def get_archived_by_name(self, obj):
        if not obj.archived_by:
            return ""

        return (
            obj.archived_by.get_full_name()
            or obj.archived_by.username
        )

    def validate_code(self, value):
        code = str(value or "").strip().upper()

        if not code:
            raise serializers.ValidationError(
                "El código del contrato es obligatorio."
            )

        queryset = RentalContract.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un contrato con este código."
            )

        return code

    def validate_contract_number(self, value):
        contract_number = str(value or "").strip()

        if not contract_number:
            return ""

        queryset = RentalContract.objects.filter(
            contract_number__iexact=contract_number,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un contrato con este número."
            )

        return contract_number

    def validate_customer(self, value):
        if value.archived_at:
            raise serializers.ValidationError(
                "El cliente seleccionado está archivado."
            )

        return value

    def validate_main_branch(self, value):
        if value and value.archived_at:
            raise serializers.ValidationError(
                "La sede seleccionada está archivada."
            )

        return value

    def validate_main_contact(self, value):
        if value and value.archived_at:
            raise serializers.ValidationError(
                "El contacto seleccionado está archivado."
            )

        return value

    def validate(self, attrs):
        instance = self.instance

        customer = attrs.get(
            "customer",
            getattr(
                instance,
                "customer",
                None,
            ),
        )

        main_branch = attrs.get(
            "main_branch",
            getattr(
                instance,
                "main_branch",
                None,
            ),
        )

        main_contact = attrs.get(
            "main_contact",
            getattr(
                instance,
                "main_contact",
                None,
            ),
        )

        contract_type = attrs.get(
            "contract_type",
            getattr(
                instance,
                "contract_type",
                RentalContract.ContractType.FIXED_TERM,
            ),
        )

        status_value = attrs.get(
            "status",
            getattr(
                instance,
                "status",
                RentalContract.Status.DRAFT,
            ),
        )

        start_date = attrs.get(
            "start_date",
            getattr(
                instance,
                "start_date",
                None,
            ),
        )

        end_date = attrs.get(
            "end_date",
            getattr(
                instance,
                "end_date",
                None,
            ),
        )

        suspension_reason = str(
            attrs.get(
                "suspension_reason",
                getattr(
                    instance,
                    "suspension_reason",
                    "",
                ),
            )
            or ""
        ).strip()

        termination_reason = str(
            attrs.get(
                "termination_reason",
                getattr(
                    instance,
                    "termination_reason",
                    "",
                ),
            )
            or ""
        ).strip()

        cancellation_reason = str(
            attrs.get(
                "cancellation_reason",
                getattr(
                    instance,
                    "cancellation_reason",
                    "",
                ),
            )
            or ""
        ).strip()

        if not customer:
            raise serializers.ValidationError(
                {
                    "customer": (
                        "El cliente es obligatorio."
                    ),
                }
            )

        if (
            main_branch
            and main_branch.partner_id != customer.id
        ):
            raise serializers.ValidationError(
                {
                    "main_branch": (
                        "La sede seleccionada no pertenece "
                        "al cliente."
                    ),
                }
            )

        if (
            main_contact
            and main_contact.partner_id != customer.id
        ):
            raise serializers.ValidationError(
                {
                    "main_contact": (
                        "El contacto seleccionado no pertenece "
                        "al cliente."
                    ),
                }
            )

        if (
            main_contact
            and main_contact.branch_id
            and main_branch
            and main_contact.branch_id != main_branch.id
        ):
            raise serializers.ValidationError(
                {
                    "main_contact": (
                        "El contacto seleccionado pertenece "
                        "a otra sede."
                    ),
                }
            )

        if (
            start_date
            and end_date
            and end_date < start_date
        ):
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "La fecha de finalización no puede ser "
                        "anterior a la fecha de inicio."
                    ),
                }
            )

        if (
            contract_type
            == RentalContract.ContractType.FIXED_TERM
            and status_value
            in [
                RentalContract.Status.APPROVED,
                RentalContract.Status.ACTIVE,
            ]
            and not end_date
        ):
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "Los contratos de plazo determinado deben "
                        "tener fecha de finalización."
                    ),
                }
            )

        if (
            status_value == RentalContract.Status.ACTIVE
            and not start_date
        ):
            raise serializers.ValidationError(
                {
                    "start_date": (
                        "Debe indicar la fecha de inicio."
                    ),
                }
            )

        if (
            status_value == RentalContract.Status.SUSPENDED
            and not suspension_reason
        ):
            raise serializers.ValidationError(
                {
                    "suspension_reason": (
                        "Debe indicar el motivo de suspensión."
                    ),
                }
            )

        if (
            status_value == RentalContract.Status.TERMINATED
            and not termination_reason
        ):
            raise serializers.ValidationError(
                {
                    "termination_reason": (
                        "Debe indicar el motivo de finalización."
                    ),
                }
            )

        if (
            status_value == RentalContract.Status.CANCELLED
            and not cancellation_reason
        ):
            raise serializers.ValidationError(
                {
                    "cancellation_reason": (
                        "Debe indicar el motivo de cancelación."
                    ),
                }
            )

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")

        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(
            validated_data
        )

    def update(self, instance, validated_data):
        request = self.context.get("request")

        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["updated_by"] = user

        return super().update(
            instance,
            validated_data,
        )


class RentalContractListSerializer(
    RentalContractSerializer
):
    """
    Serializer compacto para listados de contratos.
    """

    class Meta(RentalContractSerializer.Meta):
        fields = [
            "id",
            "code",
            "contract_number",
            "customer",
            "customer_name",
            "main_branch",
            "main_branch_name",
            "contract_type",
            "contract_type_display",
            "status",
            "status_display",
            "start_date",
            "end_date",
            "equipment_count",
            "active_equipment_count",
            "archived_at",
            "is_archived",
        ]