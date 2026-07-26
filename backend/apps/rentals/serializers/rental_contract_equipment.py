# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.rentals.models import (
    RentalContract,
    RentalContractEquipment,
    RentalEquipment,
)


class RentalContractEquipmentSerializer(
    serializers.ModelSerializer
):
    """
    Serializer principal para equipos vinculados
    a contratos de alquiler.
    """

    contract_code = serializers.SerializerMethodField()
    contract_number = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()

    rental_equipment_display = (
        serializers.SerializerMethodField()
    )

    equipment_serial_number = (
        serializers.SerializerMethodField()
    )

    equipment_internal_code = (
        serializers.SerializerMethodField()
    )

    equipment_brand_name = serializers.SerializerMethodField()
    equipment_model_name = serializers.SerializerMethodField()

    branch_name = serializers.SerializerMethodField()
    contact_name = serializers.SerializerMethodField()

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    archived_by_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RentalContractEquipment
        fields = [
            "id",
            "contract",
            "contract_code",
            "contract_number",
            "customer_name",
            "rental_equipment",
            "rental_equipment_display",
            "equipment_serial_number",
            "equipment_internal_code",
            "equipment_brand_name",
            "equipment_model_name",
            "branch",
            "branch_name",
            "contact",
            "contact_name",
            "status",
            "status_display",
            "assigned_at",
            "scheduled_installation_date",
            "installed_at",
            "removal_requested_at",
            "removed_at",
            "site_location",
            "installation_notes",
            "removal_reason",
            "cancellation_reason",
            "notes",
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
            "installed_at",
            "removal_requested_at",
            "removed_at",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        ]

    def get_contract_code(self, obj):
        if not obj.contract:
            return ""

        return obj.contract.code

    def get_contract_number(self, obj):
        if not obj.contract:
            return ""

        return obj.contract.contract_number

    def get_customer_name(self, obj):
        if not obj.contract:
            return ""

        return str(obj.contract.customer)

    def get_rental_equipment_display(self, obj):
        return str(obj.rental_equipment)

    def get_equipment_serial_number(self, obj):
        equipment = getattr(
            obj.rental_equipment,
            "equipment",
            None,
        )

        return getattr(
            equipment,
            "serial_number",
            "",
        )

    def get_equipment_internal_code(self, obj):
        equipment = getattr(
            obj.rental_equipment,
            "equipment",
            None,
        )

        return getattr(
            equipment,
            "internal_code",
            "",
        )

    def get_equipment_brand_name(self, obj):
        equipment = getattr(
            obj.rental_equipment,
            "equipment",
            None,
        )

        equipment_model = getattr(
            equipment,
            "equipment_model",
            None,
        )

        brand = getattr(
            equipment_model,
            "brand",
            None,
        )

        return getattr(
            brand,
            "name",
            "",
        )

    def get_equipment_model_name(self, obj):
        equipment = getattr(
            obj.rental_equipment,
            "equipment",
            None,
        )

        equipment_model = getattr(
            equipment,
            "equipment_model",
            None,
        )

        return getattr(
            equipment_model,
            "name",
            "",
        )

    def get_branch_name(self, obj):
        if not obj.branch:
            return ""

        return str(obj.branch)

    def get_contact_name(self, obj):
        if not obj.contact:
            return ""

        return str(obj.contact)

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

    def validate_contract(self, value):
        if value.archived_at:
            raise serializers.ValidationError(
                "El contrato seleccionado está archivado."
            )

        if value.status not in [
            RentalContract.Status.APPROVED,
            RentalContract.Status.ACTIVE,
        ]:
            raise serializers.ValidationError(
                "El contrato debe estar aprobado o activo."
            )

        return value

    def validate_rental_equipment(self, value):
        if value.archived_at:
            raise serializers.ValidationError(
                "El equipo seleccionado está archivado."
            )

        if (
            value.purpose
            != RentalEquipment.EquipmentPurpose.RENTAL
        ):
            raise serializers.ValidationError(
                "Solo los equipos destinados a alquiler "
                "pueden vincularse a contratos."
            )

        allowed_statuses = [
            RentalEquipment.OperationalStatus.READY_FOR_RENTAL,
            RentalEquipment.OperationalStatus.RESERVED,
        ]

        if value.operational_status not in allowed_statuses:
            raise serializers.ValidationError(
                "El equipo debe estar listo para alquiler "
                "o reservado."
            )

        return value

    def validate_branch(self, value):
        if value.archived_at:
            raise serializers.ValidationError(
                "La sede seleccionada está archivada."
            )

        return value

    def validate_contact(self, value):
        if value and value.archived_at:
            raise serializers.ValidationError(
                "El contacto seleccionado está archivado."
            )

        return value

    def validate(self, attrs):
        instance = self.instance

        contract = attrs.get(
            "contract",
            getattr(
                instance,
                "contract",
                None,
            ),
        )

        rental_equipment = attrs.get(
            "rental_equipment",
            getattr(
                instance,
                "rental_equipment",
                None,
            ),
        )

        branch = attrs.get(
            "branch",
            getattr(
                instance,
                "branch",
                None,
            ),
        )

        contact = attrs.get(
            "contact",
            getattr(
                instance,
                "contact",
                None,
            ),
        )

        status = attrs.get(
            "status",
            getattr(
                instance,
                "status",
                RentalContractEquipment.Status.DRAFT,
            ),
        )

        installed_at = attrs.get(
            "installed_at",
            getattr(
                instance,
                "installed_at",
                None,
            ),
        )

        removed_at = attrs.get(
            "removed_at",
            getattr(
                instance,
                "removed_at",
                None,
            ),
        )

        removal_reason = str(
            attrs.get(
                "removal_reason",
                getattr(
                    instance,
                    "removal_reason",
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

        if not contract:
            raise serializers.ValidationError(
                {
                    "contract": (
                        "El contrato es obligatorio."
                    ),
                }
            )

        if not rental_equipment:
            raise serializers.ValidationError(
                {
                    "rental_equipment": (
                        "El equipo de alquiler es obligatorio."
                    ),
                }
            )

        if not branch:
            raise serializers.ValidationError(
                {
                    "branch": (
                        "La sede es obligatoria."
                    ),
                }
            )

        if branch.partner_id != contract.customer_id:
            raise serializers.ValidationError(
                {
                    "branch": (
                        "La sede seleccionada no pertenece "
                        "al cliente del contrato."
                    ),
                }
            )

        if (
            contact
            and contact.partner_id
            != contract.customer_id
        ):
            raise serializers.ValidationError(
                {
                    "contact": (
                        "El contacto seleccionado no pertenece "
                        "al cliente del contrato."
                    ),
                }
            )

        if (
            contact
            and contact.branch_id
            and contact.branch_id != branch.id
        ):
            raise serializers.ValidationError(
                {
                    "contact": (
                        "El contacto seleccionado pertenece "
                        "a otra sede."
                    ),
                }
            )

        active_statuses = [
            RentalContractEquipment.Status.RESERVED,
            (
                RentalContractEquipment
                .Status
                .INSTALLATION_PENDING
            ),
            RentalContractEquipment.Status.INSTALLED,
            RentalContractEquipment.Status.ACTIVE,
            (
                RentalContractEquipment
                .Status
                .REMOVAL_PENDING
            ),
        ]

        if status in active_statuses:
            active_relation = (
                RentalContractEquipment.objects.filter(
                    rental_equipment=rental_equipment,
                    status__in=active_statuses,
                    archived_at__isnull=True,
                )
            )

            if instance:
                active_relation = active_relation.exclude(
                    pk=instance.pk,
                )

            if active_relation.exists():
                raise serializers.ValidationError(
                    {
                        "rental_equipment": (
                            "El equipo ya está asignado "
                            "a un contrato activo."
                        ),
                    }
                )

        if (
            status == RentalContractEquipment.Status.ACTIVE
            and not installed_at
        ):
            raise serializers.ValidationError(
                {
                    "installed_at": (
                        "Debe registrar la instalación antes "
                        "de activar el alquiler."
                    ),
                }
            )

        if (
            status
            == RentalContractEquipment.Status.REMOVAL_PENDING
            and not removal_reason
        ):
            raise serializers.ValidationError(
                {
                    "removal_reason": (
                        "Debe indicar el motivo del retiro."
                    ),
                }
            )

        if (
            status == RentalContractEquipment.Status.REMOVED
            and not removal_reason
        ):
            raise serializers.ValidationError(
                {
                    "removal_reason": (
                        "Debe indicar el motivo del retiro."
                    ),
                }
            )

        if (
            status == RentalContractEquipment.Status.CANCELLED
            and not cancellation_reason
        ):
            raise serializers.ValidationError(
                {
                    "cancellation_reason": (
                        "Debe indicar el motivo de cancelación."
                    ),
                }
            )

        if (
            installed_at
            and removed_at
            and removed_at < installed_at
        ):
            raise serializers.ValidationError(
                {
                    "removed_at": (
                        "La fecha de retiro no puede ser "
                        "anterior a la instalación."
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

        relation = super().create(
            validated_data
        )

        rental_equipment = relation.rental_equipment

        if relation.status == self.Meta.model.Status.RESERVED:
            rental_equipment.operational_status = (
                RentalEquipment.OperationalStatus.RESERVED
            )

        elif (
            relation.status
            == self.Meta.model.Status.INSTALLATION_PENDING
        ):
            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .INSTALLATION_PENDING
            )

        rental_equipment.is_available_for_rental = False
        rental_equipment.updated_by = user

        rental_equipment.save(
            update_fields=[
                "operational_status",
                "is_available_for_rental",
                "updated_by",
                "updated_at",
            ]
        )

        return relation

    def update(self, instance, validated_data):
        request = self.context.get("request")

        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["updated_by"] = user

        relation = super().update(
            instance,
            validated_data,
        )

        rental_equipment = relation.rental_equipment

        if relation.status == relation.Status.RESERVED:
            rental_equipment.operational_status = (
                RentalEquipment.OperationalStatus.RESERVED
            )

        elif (
            relation.status
            == relation.Status.INSTALLATION_PENDING
        ):
            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .INSTALLATION_PENDING
            )

        elif relation.status == relation.Status.INSTALLED:
            rental_equipment.operational_status = (
                RentalEquipment.OperationalStatus.INSTALLED
            )

        elif relation.status == relation.Status.ACTIVE:
            rental_equipment.operational_status = (
                RentalEquipment.OperationalStatus.RENTED
            )

        elif (
            relation.status
            == relation.Status.REMOVAL_PENDING
        ):
            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .REMOVAL_PENDING
            )

        elif relation.status == relation.Status.REMOVED:
            rental_equipment.operational_status = (
                RentalEquipment.OperationalStatus.REMOVED
            )

        elif relation.status == relation.Status.CANCELLED:
            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .READY_FOR_RENTAL
            )
            rental_equipment.is_available_for_rental = True

        if relation.status != relation.Status.CANCELLED:
            rental_equipment.is_available_for_rental = False

        rental_equipment.updated_by = user

        rental_equipment.save(
            update_fields=[
                "operational_status",
                "is_available_for_rental",
                "updated_by",
                "updated_at",
            ]
        )

        return relation


class RentalContractEquipmentListSerializer(
    RentalContractEquipmentSerializer
):
    """
    Serializer compacto para equipos de contratos.
    """

    class Meta(
        RentalContractEquipmentSerializer.Meta
    ):
        fields = [
            "id",
            "contract",
            "contract_code",
            "contract_number",
            "customer_name",
            "rental_equipment",
            "rental_equipment_display",
            "equipment_serial_number",
            "equipment_internal_code",
            "equipment_brand_name",
            "equipment_model_name",
            "branch",
            "branch_name",
            "contact",
            "contact_name",
            "status",
            "status_display",
            "assigned_at",
            "scheduled_installation_date",
            "installed_at",
            "removal_requested_at",
            "removed_at",
            "archived_at",
            "is_archived",
        ]