# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.rentals.models import (
    RentalAssignment,
    RentalEquipment,
)


class RentalAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer principal para asignaciones de equipos
    de alquiler a clientes, sedes y contactos.
    """

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

    customer_name = serializers.SerializerMethodField()
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
        model = RentalAssignment
        fields = [
            "id",
            "code",
            "rental_equipment",
            "rental_equipment_display",
            "equipment_serial_number",
            "equipment_internal_code",
            "equipment_brand_name",
            "equipment_model_name",
            "customer",
            "customer_name",
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

    def get_customer_name(self, obj):
        if not obj.customer:
            return ""

        return str(obj.customer)

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

    def validate_code(self, value):
        code = str(
            value or ""
        ).strip().upper()

        if not code:
            raise serializers.ValidationError(
                "El código de asignación es obligatorio."
            )

        queryset = RentalAssignment.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una asignación con este código."
            )

        return code

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
                "pueden asignarse a clientes."
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

    def validate_customer(self, value):
        if value.archived_at:
            raise serializers.ValidationError(
                "El cliente seleccionado está archivado."
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

        rental_equipment = attrs.get(
            "rental_equipment",
            getattr(
                instance,
                "rental_equipment",
                None,
            ),
        )

        customer = attrs.get(
            "customer",
            getattr(
                instance,
                "customer",
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
                RentalAssignment.Status.DRAFT,
            ),
        )

        installed_at = getattr(
            instance,
            "installed_at",
            None,
        )

        removed_at = getattr(
            instance,
            "removed_at",
            None,
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

        if not rental_equipment:
            raise serializers.ValidationError(
                {
                    "rental_equipment": (
                        "El equipo de alquiler es obligatorio."
                    ),
                }
            )

        if not customer:
            raise serializers.ValidationError(
                {
                    "customer": (
                        "El cliente es obligatorio."
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

        if branch.partner_id != customer.id:
            raise serializers.ValidationError(
                {
                    "branch": (
                        "La sede seleccionada no pertenece "
                        "al cliente."
                    ),
                }
            )

        if (
            contact
            and contact.partner_id != customer.id
        ):
            raise serializers.ValidationError(
                {
                    "contact": (
                        "El contacto seleccionado no pertenece "
                        "al cliente."
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
            RentalAssignment.Status.RESERVED,
            RentalAssignment.Status.INSTALLATION_PENDING,
            RentalAssignment.Status.INSTALLED,
            RentalAssignment.Status.ACTIVE,
            RentalAssignment.Status.REMOVAL_PENDING,
        ]

        if status in active_statuses:
            active_assignment = RentalAssignment.objects.filter(
                rental_equipment=rental_equipment,
                status__in=active_statuses,
                archived_at__isnull=True,
            )

            if instance:
                active_assignment = active_assignment.exclude(
                    pk=instance.pk,
                )

            if active_assignment.exists():
                raise serializers.ValidationError(
                    {
                        "rental_equipment": (
                            "El equipo ya tiene una asignación activa."
                        ),
                    }
                )

        if (
            status == RentalAssignment.Status.ACTIVE
            and not installed_at
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "Debe instalar el equipo antes de activar "
                        "el alquiler."
                    ),
                }
            )

        if (
            status == RentalAssignment.Status.REMOVAL_PENDING
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
            status == RentalAssignment.Status.REMOVED
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
            status == RentalAssignment.Status.CANCELLED
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

        assignment = super().create(
            validated_data
        )

        rental_equipment = assignment.rental_equipment

        if assignment.status == RentalAssignment.Status.RESERVED:
            rental_equipment.operational_status = (
                RentalEquipment.OperationalStatus.RESERVED
            )

        elif (
            assignment.status
            == RentalAssignment.Status.INSTALLATION_PENDING
        ):
            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .INSTALLATION_PENDING
            )

        else:
            rental_equipment.operational_status = (
                RentalEquipment.OperationalStatus.ASSIGNED
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

        return assignment

    def update(self, instance, validated_data):
        request = self.context.get("request")

        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["updated_by"] = user

        assignment = super().update(
            instance,
            validated_data,
        )

        rental_equipment = assignment.rental_equipment

        if assignment.status == RentalAssignment.Status.RESERVED:
            rental_equipment.operational_status = (
                RentalEquipment.OperationalStatus.RESERVED
            )

        elif (
            assignment.status
            == RentalAssignment.Status.INSTALLATION_PENDING
        ):
            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .INSTALLATION_PENDING
            )

        elif assignment.status == RentalAssignment.Status.INSTALLED:
            rental_equipment.operational_status = (
                RentalEquipment.OperationalStatus.INSTALLED
            )

        elif assignment.status == RentalAssignment.Status.ACTIVE:
            rental_equipment.operational_status = (
                RentalEquipment.OperationalStatus.RENTED
            )

        elif (
            assignment.status
            == RentalAssignment.Status.REMOVAL_PENDING
        ):
            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .REMOVAL_PENDING
            )

        elif assignment.status == RentalAssignment.Status.REMOVED:
            rental_equipment.operational_status = (
                RentalEquipment.OperationalStatus.REMOVED
            )

        elif assignment.status == RentalAssignment.Status.CANCELLED:
            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .READY_FOR_RENTAL
            )
            rental_equipment.is_available_for_rental = True

        if assignment.status != RentalAssignment.Status.CANCELLED:
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

        return assignment


class RentalAssignmentListSerializer(
    RentalAssignmentSerializer
):
    """
    Serializer compacto para listados de asignaciones.
    """

    class Meta(RentalAssignmentSerializer.Meta):
        fields = [
            "id",
            "code",
            "rental_equipment",
            "rental_equipment_display",
            "equipment_serial_number",
            "equipment_internal_code",
            "equipment_brand_name",
            "equipment_model_name",
            "customer",
            "customer_name",
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