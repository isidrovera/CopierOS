# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.rentals.models import (
    RentalAssignment,
    RentalEquipment,
    RentalRemoval,
)


class RentalRemovalSerializer(serializers.ModelSerializer):
    """
    Serializer principal para retiros de equipos
    alquilados por ANDES.
    """

    assignment_code = serializers.SerializerMethodField()

    rental_equipment = serializers.SerializerMethodField()
    rental_equipment_display = serializers.SerializerMethodField()

    equipment_serial_number = serializers.SerializerMethodField()
    equipment_internal_code = serializers.SerializerMethodField()
    equipment_brand_name = serializers.SerializerMethodField()
    equipment_model_name = serializers.SerializerMethodField()

    customer = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    branch = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    contact_name = serializers.SerializerMethodField()

    assigned_technician_name = serializers.SerializerMethodField()
    destination_warehouse_name = serializers.SerializerMethodField()

    removal_type_display = serializers.CharField(
        source="get_removal_type_display",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    result_display = serializers.CharField(
        source="get_result_display",
        read_only=True,
    )

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    archived_by_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RentalRemoval
        fields = [
            "id",
            "code",
            "rental_assignment",
            "assignment_code",
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
            "removal_type",
            "removal_type_display",
            "assigned_technician",
            "assigned_technician_name",
            "destination_warehouse",
            "destination_warehouse_name",
            "destination_location",
            "status",
            "status_display",
            "result",
            "result_display",
            "requested_at",
            "scheduled_at",
            "started_at",
            "completed_at",
            "removal_reason",
            "equipment_condition",
            "accessories_received",
            "missing_accessories",
            "final_total_meter",
            "final_black_meter",
            "final_color_meter",
            "customer_representative_name",
            "customer_conformity",
            "technical_observations",
            "customer_observations",
            "cancellation_reason",
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
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        ]

    def get_assignment_code(self, obj):
        if not obj.rental_assignment:
            return ""

        return obj.rental_assignment.code

    def get_rental_equipment(self, obj):
        if not obj.rental_assignment:
            return None

        return obj.rental_assignment.rental_equipment_id

    def get_rental_equipment_display(self, obj):
        if not obj.rental_assignment:
            return ""

        return str(
            obj.rental_assignment.rental_equipment
        )

    def get_equipment_serial_number(self, obj):
        equipment = self._get_equipment(obj)

        return getattr(
            equipment,
            "serial_number",
            "",
        )

    def get_equipment_internal_code(self, obj):
        equipment = self._get_equipment(obj)

        return getattr(
            equipment,
            "internal_code",
            "",
        )

    def get_equipment_brand_name(self, obj):
        equipment = self._get_equipment(obj)

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
        equipment = self._get_equipment(obj)

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

    def get_customer(self, obj):
        if not obj.rental_assignment:
            return None

        return obj.rental_assignment.customer_id

    def get_customer_name(self, obj):
        if not obj.rental_assignment:
            return ""

        return str(
            obj.rental_assignment.customer
        )

    def get_branch(self, obj):
        if not obj.rental_assignment:
            return None

        return obj.rental_assignment.branch_id

    def get_branch_name(self, obj):
        if not obj.rental_assignment:
            return ""

        return str(
            obj.rental_assignment.branch
        )

    def get_contact(self, obj):
        if not obj.rental_assignment:
            return None

        return obj.rental_assignment.contact_id

    def get_contact_name(self, obj):
        if (
            not obj.rental_assignment
            or not obj.rental_assignment.contact
        ):
            return ""

        return str(
            obj.rental_assignment.contact
        )

    def get_assigned_technician_name(self, obj):
        if not obj.assigned_technician:
            return ""

        return (
            obj.assigned_technician.get_full_name()
            or obj.assigned_technician.username
        )

    def get_destination_warehouse_name(self, obj):
        if not obj.destination_warehouse:
            return ""

        return obj.destination_warehouse.name

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

    def _get_equipment(self, obj):
        if not obj.rental_assignment:
            return None

        rental_equipment = (
            obj.rental_assignment.rental_equipment
        )

        return getattr(
            rental_equipment,
            "equipment",
            None,
        )

    def validate_code(self, value):
        code = str(
            value or ""
        ).strip().upper()

        if not code:
            raise serializers.ValidationError(
                "El código de retiro es obligatorio."
            )

        queryset = RentalRemoval.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un retiro con este código."
            )

        return code

    def validate_rental_assignment(self, value):
        if value.archived_at:
            raise serializers.ValidationError(
                "La asignación seleccionada está archivada."
            )

        allowed_statuses = [
            RentalAssignment.Status.INSTALLED,
            RentalAssignment.Status.ACTIVE,
            RentalAssignment.Status.REMOVAL_PENDING,
        ]

        if value.status not in allowed_statuses:
            raise serializers.ValidationError(
                "La asignación seleccionada no está disponible "
                "para retiro."
            )

        active_removal = RentalRemoval.objects.filter(
            rental_assignment=value,
            status__in=[
                RentalRemoval.Status.REQUESTED,
                RentalRemoval.Status.SCHEDULED,
                RentalRemoval.Status.ASSIGNED,
                RentalRemoval.Status.IN_TRANSIT,
                RentalRemoval.Status.IN_PROGRESS,
                RentalRemoval.Status.OBSERVED,
            ],
            archived_at__isnull=True,
        )

        if self.instance:
            active_removal = active_removal.exclude(
                pk=self.instance.pk,
            )

        if active_removal.exists():
            raise serializers.ValidationError(
                "La asignación ya tiene un retiro activo."
            )

        return value

    def validate_assigned_technician(self, value):
        if not value:
            return value

        if not value.is_active:
            raise serializers.ValidationError(
                "El técnico seleccionado está inactivo."
            )

        return value

    def validate_destination_warehouse(self, value):
        if not value:
            return value

        if value.archived_at:
            raise serializers.ValidationError(
                "El almacén de destino está archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "El almacén de destino está inactivo."
            )

        if not value.allows_entries:
            raise serializers.ValidationError(
                "El almacén de destino no permite ingresos."
            )

        return value

    def validate(self, attrs):
        instance = self.instance

        rental_assignment = attrs.get(
            "rental_assignment",
            getattr(
                instance,
                "rental_assignment",
                None,
            ),
        )

        assigned_technician = attrs.get(
            "assigned_technician",
            getattr(
                instance,
                "assigned_technician",
                None,
            ),
        )

        destination_warehouse = attrs.get(
            "destination_warehouse",
            getattr(
                instance,
                "destination_warehouse",
                None,
            ),
        )

        status = attrs.get(
            "status",
            getattr(
                instance,
                "status",
                RentalRemoval.Status.DRAFT,
            ),
        )

        result = attrs.get(
            "result",
            getattr(
                instance,
                "result",
                RentalRemoval.Result.PENDING,
            ),
        )

        scheduled_at = attrs.get(
            "scheduled_at",
            getattr(
                instance,
                "scheduled_at",
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

        if not rental_assignment:
            raise serializers.ValidationError(
                {
                    "rental_assignment": (
                        "La asignación de alquiler es obligatoria."
                    ),
                }
            )

        if not removal_reason:
            raise serializers.ValidationError(
                {
                    "removal_reason": (
                        "El motivo del retiro es obligatorio."
                    ),
                }
            )

        technician_required_statuses = [
            RentalRemoval.Status.ASSIGNED,
            RentalRemoval.Status.IN_TRANSIT,
            RentalRemoval.Status.IN_PROGRESS,
            RentalRemoval.Status.COMPLETED,
            RentalRemoval.Status.OBSERVED,
        ]

        if (
            status in technician_required_statuses
            and not assigned_technician
        ):
            raise serializers.ValidationError(
                {
                    "assigned_technician": (
                        "Debe asignar un técnico."
                    ),
                }
            )

        if (
            status == RentalRemoval.Status.SCHEDULED
            and not scheduled_at
        ):
            raise serializers.ValidationError(
                {
                    "scheduled_at": (
                        "Debe indicar la fecha programada."
                    ),
                }
            )

        if status == RentalRemoval.Status.COMPLETED:
            if result == RentalRemoval.Result.PENDING:
                raise serializers.ValidationError(
                    {
                        "result": (
                            "Debe indicar el resultado del retiro."
                        ),
                    }
                )

            warehouse_results = [
                RentalRemoval.Result.RETURNED_TO_WAREHOUSE,
                RentalRemoval.Result.SENT_TO_REVIEW,
                RentalRemoval.Result.WITH_PROBLEMS,
                RentalRemoval.Result.FOR_PARTS,
            ]

            if (
                result in warehouse_results
                and not destination_warehouse
            ):
                raise serializers.ValidationError(
                    {
                        "destination_warehouse": (
                            "Debe indicar el almacén de destino."
                        ),
                    }
                )

        if (
            status == RentalRemoval.Status.CANCELLED
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

        removal = super().create(
            validated_data
        )

        assignment = removal.rental_assignment
        rental_equipment = assignment.rental_equipment

        if removal.status in [
            RentalRemoval.Status.REQUESTED,
            RentalRemoval.Status.SCHEDULED,
            RentalRemoval.Status.ASSIGNED,
            RentalRemoval.Status.IN_TRANSIT,
            RentalRemoval.Status.IN_PROGRESS,
        ]:
            assignment.status = (
                RentalAssignment.Status.REMOVAL_PENDING
            )

            assignment.removal_requested_at = (
                removal.requested_at
            )

            assignment.removal_reason = (
                removal.removal_reason
            )

            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .REMOVAL_PENDING
            )

            rental_equipment.is_available_for_rental = False

        assignment.updated_by = user
        rental_equipment.updated_by = user

        assignment.save(
            update_fields=[
                "status",
                "removal_requested_at",
                "removal_reason",
                "updated_by",
                "updated_at",
            ]
        )

        rental_equipment.save(
            update_fields=[
                "operational_status",
                "is_available_for_rental",
                "updated_by",
                "updated_at",
            ]
        )

        return removal

    def update(self, instance, validated_data):
        request = self.context.get("request")

        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["updated_by"] = user

        removal = super().update(
            instance,
            validated_data,
        )

        assignment = removal.rental_assignment
        rental_equipment = assignment.rental_equipment

        if removal.status in [
            RentalRemoval.Status.REQUESTED,
            RentalRemoval.Status.SCHEDULED,
            RentalRemoval.Status.ASSIGNED,
            RentalRemoval.Status.IN_TRANSIT,
            RentalRemoval.Status.IN_PROGRESS,
            RentalRemoval.Status.OBSERVED,
        ]:
            assignment.status = (
                RentalAssignment.Status.REMOVAL_PENDING
            )

            assignment.removal_requested_at = (
                removal.requested_at
            )

            assignment.removal_reason = (
                removal.removal_reason
            )

            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .REMOVAL_PENDING
            )

            rental_equipment.is_available_for_rental = False

        elif removal.status == RentalRemoval.Status.COMPLETED:
            assignment.status = (
                RentalAssignment.Status.REMOVED
            )

            assignment.removed_at = (
                removal.completed_at
            )

            assignment.removal_reason = (
                removal.removal_reason
            )

            rental_equipment.warehouse = (
                removal.destination_warehouse
            )

            rental_equipment.warehouse_location = (
                removal.destination_location
            )

            rental_equipment.is_available_for_rental = False

            if (
                removal.result
                == RentalRemoval.Result.RETURNED_TO_WAREHOUSE
            ):
                rental_equipment.operational_status = (
                    RentalEquipment
                    .OperationalStatus
                    .RETURNED_TO_WAREHOUSE
                )

            elif (
                removal.result
                == RentalRemoval.Result.SENT_TO_REVIEW
            ):
                rental_equipment.operational_status = (
                    RentalEquipment
                    .OperationalStatus
                    .PENDING_PREPARATION
                )

            elif (
                removal.result
                == RentalRemoval.Result.WITH_PROBLEMS
            ):
                rental_equipment.operational_status = (
                    RentalEquipment
                    .OperationalStatus
                    .WITH_PROBLEMS
                )

            elif (
                removal.result
                == RentalRemoval.Result.FOR_PARTS
            ):
                rental_equipment.operational_status = (
                    RentalEquipment
                    .OperationalStatus
                    .FOR_PARTS
                )

            elif (
                removal.result
                == RentalRemoval.Result.RELOCATED
            ):
                rental_equipment.operational_status = (
                    RentalEquipment
                    .OperationalStatus
                    .INSTALLATION_PENDING
                )

            else:
                rental_equipment.operational_status = (
                    RentalEquipment
                    .OperationalStatus
                    .REMOVED
                )

        elif removal.status == RentalRemoval.Status.CANCELLED:
            assignment.status = RentalAssignment.Status.ACTIVE
            assignment.removal_requested_at = None
            assignment.removal_reason = ""

            rental_equipment.operational_status = (
                RentalEquipment.OperationalStatus.RENTED
            )

            rental_equipment.is_available_for_rental = False

        assignment.updated_by = user
        rental_equipment.updated_by = user

        assignment_update_fields = [
            "status",
            "removal_requested_at",
            "removal_reason",
            "updated_by",
            "updated_at",
        ]

        if assignment.removed_at:
            assignment_update_fields.append(
                "removed_at"
            )

        assignment.save(
            update_fields=list(
                dict.fromkeys(
                    assignment_update_fields
                )
            )
        )

        rental_equipment.save(
            update_fields=[
                "operational_status",
                "warehouse",
                "warehouse_location",
                "is_available_for_rental",
                "updated_by",
                "updated_at",
            ]
        )

        return removal


class RentalRemovalListSerializer(
    RentalRemovalSerializer
):
    """
    Serializer compacto para listados de retiros.
    """

    class Meta(RentalRemovalSerializer.Meta):
        fields = [
            "id",
            "code",
            "rental_assignment",
            "assignment_code",
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
            "removal_type",
            "removal_type_display",
            "assigned_technician",
            "assigned_technician_name",
            "destination_warehouse",
            "destination_warehouse_name",
            "status",
            "status_display",
            "result",
            "result_display",
            "requested_at",
            "scheduled_at",
            "started_at",
            "completed_at",
            "customer_conformity",
            "archived_at",
            "is_archived",
        ]