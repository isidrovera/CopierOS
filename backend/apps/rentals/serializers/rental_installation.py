# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.rentals.models import (
    RentalAssignment,
    RentalEquipment,
    RentalInstallation,
)


class RentalInstallationSerializer(serializers.ModelSerializer):
    """
    Serializer principal para instalaciones de equipos
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
        model = RentalInstallation
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
            "assigned_technician",
            "assigned_technician_name",
            "status",
            "status_display",
            "result",
            "result_display",
            "requested_at",
            "scheduled_at",
            "started_at",
            "completed_at",
            "site_location",
            "ip_address",
            "hostname",
            "network_notes",
            "driver_installed",
            "printing_test_passed",
            "copying_test_passed",
            "scanning_test_passed",
            "duplex_test_passed",
            "adf_test_passed",
            "initial_total_meter",
            "initial_black_meter",
            "initial_color_meter",
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
                "El código de instalación es obligatorio."
            )

        queryset = RentalInstallation.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una instalación con este código."
            )

        return code

    def validate_rental_assignment(self, value):
        if value.archived_at:
            raise serializers.ValidationError(
                "La asignación seleccionada está archivada."
            )

        allowed_statuses = [
            RentalAssignment.Status.RESERVED,
            RentalAssignment.Status.INSTALLATION_PENDING,
            RentalAssignment.Status.INSTALLED,
            RentalAssignment.Status.ACTIVE,
        ]

        if value.status not in allowed_statuses:
            raise serializers.ValidationError(
                "La asignación seleccionada no está disponible "
                "para instalación."
            )

        active_installation = RentalInstallation.objects.filter(
            rental_assignment=value,
            status__in=[
                RentalInstallation.Status.SCHEDULED,
                RentalInstallation.Status.ASSIGNED,
                RentalInstallation.Status.IN_TRANSIT,
                RentalInstallation.Status.IN_PROGRESS,
                RentalInstallation.Status.OBSERVED,
            ],
            archived_at__isnull=True,
        )

        if self.instance:
            active_installation = active_installation.exclude(
                pk=self.instance.pk,
            )

        if active_installation.exists():
            raise serializers.ValidationError(
                "La asignación ya tiene una instalación activa."
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

        status = attrs.get(
            "status",
            getattr(
                instance,
                "status",
                RentalInstallation.Status.DRAFT,
            ),
        )

        result = attrs.get(
            "result",
            getattr(
                instance,
                "result",
                RentalInstallation.Result.PENDING,
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

        initial_total_meter = attrs.get(
            "initial_total_meter",
            getattr(
                instance,
                "initial_total_meter",
                None,
            ),
        )

        initial_black_meter = attrs.get(
            "initial_black_meter",
            getattr(
                instance,
                "initial_black_meter",
                None,
            ),
        )

        initial_color_meter = attrs.get(
            "initial_color_meter",
            getattr(
                instance,
                "initial_color_meter",
                None,
            ),
        )

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

        technician_required_statuses = [
            RentalInstallation.Status.ASSIGNED,
            RentalInstallation.Status.IN_TRANSIT,
            RentalInstallation.Status.IN_PROGRESS,
            RentalInstallation.Status.COMPLETED,
            RentalInstallation.Status.OBSERVED,
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
            status == RentalInstallation.Status.SCHEDULED
            and not scheduled_at
        ):
            raise serializers.ValidationError(
                {
                    "scheduled_at": (
                        "Debe indicar la fecha programada."
                    ),
                }
            )

        if status == RentalInstallation.Status.COMPLETED:
            if result == RentalInstallation.Result.PENDING:
                raise serializers.ValidationError(
                    {
                        "result": (
                            "Debe indicar el resultado "
                            "de la instalación."
                        ),
                    }
                )

            if (
                initial_total_meter is None
                and initial_black_meter is None
                and initial_color_meter is None
            ):
                raise serializers.ValidationError(
                    {
                        "initial_total_meter": (
                            "Debe registrar al menos un contador "
                            "durante la instalación."
                        ),
                    }
                )

        if (
            status == RentalInstallation.Status.CANCELLED
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

        installation = super().create(
            validated_data
        )

        assignment = installation.rental_assignment
        rental_equipment = assignment.rental_equipment

        if installation.status in [
            RentalInstallation.Status.SCHEDULED,
            RentalInstallation.Status.ASSIGNED,
            RentalInstallation.Status.IN_TRANSIT,
        ]:
            assignment.status = (
                RentalAssignment.Status.INSTALLATION_PENDING
            )

            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .INSTALLATION_PENDING
            )

        elif (
            installation.status
            == RentalInstallation.Status.IN_PROGRESS
        ):
            assignment.status = (
                RentalAssignment.Status.INSTALLATION_PENDING
            )

            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .INSTALLATION_PENDING
            )

        assignment.updated_by = user
        rental_equipment.updated_by = user
        rental_equipment.is_available_for_rental = False

        assignment.save(
            update_fields=[
                "status",
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

        return installation

    def update(self, instance, validated_data):
        request = self.context.get("request")

        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["updated_by"] = user

        installation = super().update(
            instance,
            validated_data,
        )

        assignment = installation.rental_assignment
        rental_equipment = assignment.rental_equipment

        if installation.status in [
            RentalInstallation.Status.SCHEDULED,
            RentalInstallation.Status.ASSIGNED,
            RentalInstallation.Status.IN_TRANSIT,
            RentalInstallation.Status.IN_PROGRESS,
        ]:
            assignment.status = (
                RentalAssignment.Status.INSTALLATION_PENDING
            )

            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .INSTALLATION_PENDING
            )

            rental_equipment.is_available_for_rental = False

        elif (
            installation.status
            == RentalInstallation.Status.COMPLETED
        ):
            if installation.result in [
                RentalInstallation.Result.INSTALLED,
                (
                    RentalInstallation
                    .Result
                    .INSTALLED_WITH_OBSERVATIONS
                ),
            ]:
                assignment.status = (
                    RentalAssignment.Status.ACTIVE
                )

                assignment.installed_at = (
                    installation.completed_at
                )

                rental_equipment.operational_status = (
                    RentalEquipment.OperationalStatus.RENTED
                )

                rental_equipment.warehouse = None
                rental_equipment.warehouse_location = ""
                rental_equipment.is_available_for_rental = False

            elif (
                installation.result
                == RentalInstallation
                .Result
                .REQUIRES_REPLACEMENT
            ):
                assignment.status = (
                    RentalAssignment.Status.INSTALLATION_PENDING
                )

                rental_equipment.operational_status = (
                    RentalEquipment
                    .OperationalStatus
                    .WITH_PROBLEMS
                )

                rental_equipment.is_available_for_rental = False

            else:
                assignment.status = (
                    RentalAssignment.Status.INSTALLATION_PENDING
                )

                rental_equipment.operational_status = (
                    RentalEquipment
                    .OperationalStatus
                    .WITH_PROBLEMS
                )

                rental_equipment.is_available_for_rental = False

        elif (
            installation.status
            == RentalInstallation.Status.OBSERVED
        ):
            assignment.status = (
                RentalAssignment.Status.INSTALLATION_PENDING
            )

            rental_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .WITH_PROBLEMS
            )

            rental_equipment.is_available_for_rental = False

        elif (
            installation.status
            == RentalInstallation.Status.CANCELLED
        ):
            assignment.status = (
                RentalAssignment.Status.RESERVED
            )

            rental_equipment.operational_status = (
                RentalEquipment.OperationalStatus.RESERVED
            )

            rental_equipment.is_available_for_rental = False

        assignment.updated_by = user
        rental_equipment.updated_by = user

        assignment_update_fields = [
            "status",
            "updated_by",
            "updated_at",
        ]

        if assignment.installed_at:
            assignment_update_fields.append(
                "installed_at"
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

        return installation


class RentalInstallationListSerializer(
    RentalInstallationSerializer
):
    """
    Serializer compacto para listados de instalaciones.
    """

    class Meta(RentalInstallationSerializer.Meta):
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
            "assigned_technician",
            "assigned_technician_name",
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