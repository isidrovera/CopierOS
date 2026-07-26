# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.rentals.models import (
    RentalAssignment,
    RentalEquipment,
    RentalReplacement,
)


class RentalReplacementSerializer(serializers.ModelSerializer):
    """
    Serializer principal para reemplazos de equipos
    alquilados por ANDES.
    """

    assignment_code = serializers.SerializerMethodField()

    customer = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    branch = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    contact_name = serializers.SerializerMethodField()

    outgoing_equipment_display = (
        serializers.SerializerMethodField()
    )
    outgoing_serial_number = serializers.SerializerMethodField()
    outgoing_internal_code = serializers.SerializerMethodField()
    outgoing_brand_name = serializers.SerializerMethodField()
    outgoing_model_name = serializers.SerializerMethodField()

    incoming_equipment_display = (
        serializers.SerializerMethodField()
    )
    incoming_serial_number = serializers.SerializerMethodField()
    incoming_internal_code = serializers.SerializerMethodField()
    incoming_brand_name = serializers.SerializerMethodField()
    incoming_model_name = serializers.SerializerMethodField()

    replacement_type_display = serializers.CharField(
        source="get_replacement_type_display",
        read_only=True,
    )

    reason_display = serializers.CharField(
        source="get_reason_display",
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

    approved_by_name = serializers.SerializerMethodField()
    assigned_technician_name = serializers.SerializerMethodField()

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    archived_by_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RentalReplacement
        fields = [
            "id",
            "code",
            "rental_assignment",
            "assignment_code",
            "customer",
            "customer_name",
            "branch",
            "branch_name",
            "contact",
            "contact_name",
            "outgoing_equipment",
            "outgoing_equipment_display",
            "outgoing_serial_number",
            "outgoing_internal_code",
            "outgoing_brand_name",
            "outgoing_model_name",
            "incoming_equipment",
            "incoming_equipment_display",
            "incoming_serial_number",
            "incoming_internal_code",
            "incoming_brand_name",
            "incoming_model_name",
            "replacement_type",
            "replacement_type_display",
            "reason",
            "reason_display",
            "reason_detail",
            "status",
            "status_display",
            "result",
            "result_display",
            "approved_by",
            "approved_by_name",
            "assigned_technician",
            "assigned_technician_name",
            "requested_at",
            "approved_at",
            "scheduled_at",
            "started_at",
            "completed_at",
            "outgoing_total_meter",
            "outgoing_black_meter",
            "outgoing_color_meter",
            "incoming_total_meter",
            "incoming_black_meter",
            "incoming_color_meter",
            "customer_representative_name",
            "customer_conformity",
            "technical_observations",
            "customer_observations",
            "rejection_reason",
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
            "approved_at",
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

    def get_outgoing_equipment_display(self, obj):
        return str(
            obj.outgoing_equipment
        )

    def get_outgoing_serial_number(self, obj):
        equipment = getattr(
            obj.outgoing_equipment,
            "equipment",
            None,
        )

        return getattr(
            equipment,
            "serial_number",
            "",
        )

    def get_outgoing_internal_code(self, obj):
        equipment = getattr(
            obj.outgoing_equipment,
            "equipment",
            None,
        )

        return getattr(
            equipment,
            "internal_code",
            "",
        )

    def get_outgoing_brand_name(self, obj):
        return self._get_brand_name(
            obj.outgoing_equipment
        )

    def get_outgoing_model_name(self, obj):
        return self._get_model_name(
            obj.outgoing_equipment
        )

    def get_incoming_equipment_display(self, obj):
        return str(
            obj.incoming_equipment
        )

    def get_incoming_serial_number(self, obj):
        equipment = getattr(
            obj.incoming_equipment,
            "equipment",
            None,
        )

        return getattr(
            equipment,
            "serial_number",
            "",
        )

    def get_incoming_internal_code(self, obj):
        equipment = getattr(
            obj.incoming_equipment,
            "equipment",
            None,
        )

        return getattr(
            equipment,
            "internal_code",
            "",
        )

    def get_incoming_brand_name(self, obj):
        return self._get_brand_name(
            obj.incoming_equipment
        )

    def get_incoming_model_name(self, obj):
        return self._get_model_name(
            obj.incoming_equipment
        )

    def get_approved_by_name(self, obj):
        if not obj.approved_by:
            return ""

        return (
            obj.approved_by.get_full_name()
            or obj.approved_by.username
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

    def _get_brand_name(self, rental_equipment):
        equipment = getattr(
            rental_equipment,
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

    def _get_model_name(self, rental_equipment):
        equipment = getattr(
            rental_equipment,
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

    def validate_code(self, value):
        code = str(
            value or ""
        ).strip().upper()

        if not code:
            raise serializers.ValidationError(
                "El código de reemplazo es obligatorio."
            )

        queryset = RentalReplacement.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un reemplazo con este código."
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
                "para reemplazo."
            )

        active_replacement = RentalReplacement.objects.filter(
            rental_assignment=value,
            status__in=[
                RentalReplacement.Status.REQUESTED,
                RentalReplacement.Status.APPROVED,
                RentalReplacement.Status.SCHEDULED,
                RentalReplacement.Status.ASSIGNED,
                RentalReplacement.Status.IN_TRANSIT,
                RentalReplacement.Status.IN_PROGRESS,
                RentalReplacement.Status.OBSERVED,
            ],
            archived_at__isnull=True,
        )

        if self.instance:
            active_replacement = active_replacement.exclude(
                pk=self.instance.pk,
            )

        if active_replacement.exists():
            raise serializers.ValidationError(
                "La asignación ya tiene un reemplazo activo."
            )

        return value

    def validate_outgoing_equipment(self, value):
        if value.archived_at:
            raise serializers.ValidationError(
                "El equipo retirado está archivado."
            )

        return value

    def validate_incoming_equipment(self, value):
        if value.archived_at:
            raise serializers.ValidationError(
                "El equipo de reemplazo está archivado."
            )

        if (
            value.purpose
            != RentalEquipment.EquipmentPurpose.RENTAL
        ):
            raise serializers.ValidationError(
                "El equipo de reemplazo debe estar destinado "
                "al alquiler."
            )

        allowed_statuses = [
            RentalEquipment.OperationalStatus.READY_FOR_RENTAL,
            RentalEquipment.OperationalStatus.RESERVED,
        ]

        if value.operational_status not in allowed_statuses:
            raise serializers.ValidationError(
                "El equipo de reemplazo debe estar listo "
                "para alquiler o reservado."
            )

        return value

    def validate_approved_by(self, value):
        if value and not value.is_active:
            raise serializers.ValidationError(
                "El usuario aprobador está inactivo."
            )

        return value

    def validate_assigned_technician(self, value):
        if value and not value.is_active:
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

        outgoing_equipment = attrs.get(
            "outgoing_equipment",
            getattr(
                instance,
                "outgoing_equipment",
                None,
            ),
        )

        incoming_equipment = attrs.get(
            "incoming_equipment",
            getattr(
                instance,
                "incoming_equipment",
                None,
            ),
        )

        status = attrs.get(
            "status",
            getattr(
                instance,
                "status",
                RentalReplacement.Status.DRAFT,
            ),
        )

        result = attrs.get(
            "result",
            getattr(
                instance,
                "result",
                RentalReplacement.Result.PENDING,
            ),
        )

        approved_by = attrs.get(
            "approved_by",
            getattr(
                instance,
                "approved_by",
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

        scheduled_at = attrs.get(
            "scheduled_at",
            getattr(
                instance,
                "scheduled_at",
                None,
            ),
        )

        rejection_reason = str(
            attrs.get(
                "rejection_reason",
                getattr(
                    instance,
                    "rejection_reason",
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
                        "La asignación afectada es obligatoria."
                    ),
                }
            )

        if not outgoing_equipment:
            raise serializers.ValidationError(
                {
                    "outgoing_equipment": (
                        "El equipo retirado es obligatorio."
                    ),
                }
            )

        if not incoming_equipment:
            raise serializers.ValidationError(
                {
                    "incoming_equipment": (
                        "El equipo de reemplazo es obligatorio."
                    ),
                }
            )

        if outgoing_equipment.id == incoming_equipment.id:
            raise serializers.ValidationError(
                {
                    "incoming_equipment": (
                        "El equipo de reemplazo debe ser diferente."
                    ),
                }
            )

        if (
            rental_assignment.rental_equipment_id
            != outgoing_equipment.id
        ):
            raise serializers.ValidationError(
                {
                    "outgoing_equipment": (
                        "El equipo retirado no corresponde "
                        "a la asignación."
                    ),
                }
            )

        if (
            status == RentalReplacement.Status.APPROVED
            and not approved_by
        ):
            raise serializers.ValidationError(
                {
                    "approved_by": (
                        "Debe indicar quién aprobó el reemplazo."
                    ),
                }
            )

        if (
            status == RentalReplacement.Status.SCHEDULED
            and not scheduled_at
        ):
            raise serializers.ValidationError(
                {
                    "scheduled_at": (
                        "Debe indicar la fecha programada."
                    ),
                }
            )

        technician_required_statuses = [
            RentalReplacement.Status.ASSIGNED,
            RentalReplacement.Status.IN_TRANSIT,
            RentalReplacement.Status.IN_PROGRESS,
            RentalReplacement.Status.COMPLETED,
            RentalReplacement.Status.OBSERVED,
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

        if status == RentalReplacement.Status.COMPLETED:
            if result == RentalReplacement.Result.PENDING:
                raise serializers.ValidationError(
                    {
                        "result": (
                            "Debe indicar el resultado "
                            "del reemplazo."
                        ),
                    }
                )

        if (
            status == RentalReplacement.Status.REJECTED
            and not rejection_reason
        ):
            raise serializers.ValidationError(
                {
                    "rejection_reason": (
                        "Debe indicar el motivo del rechazo."
                    ),
                }
            )

        if (
            status == RentalReplacement.Status.CANCELLED
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

        replacement = super().create(
            validated_data
        )

        incoming_equipment = replacement.incoming_equipment

        if replacement.status in [
            RentalReplacement.Status.REQUESTED,
            RentalReplacement.Status.APPROVED,
            RentalReplacement.Status.SCHEDULED,
            RentalReplacement.Status.ASSIGNED,
            RentalReplacement.Status.IN_TRANSIT,
            RentalReplacement.Status.IN_PROGRESS,
        ]:
            incoming_equipment.operational_status = (
                RentalEquipment.OperationalStatus.RESERVED
            )

            incoming_equipment.is_available_for_rental = False
            incoming_equipment.updated_by = user

            incoming_equipment.save(
                update_fields=[
                    "operational_status",
                    "is_available_for_rental",
                    "updated_by",
                    "updated_at",
                ]
            )

        return replacement

    def update(self, instance, validated_data):
        request = self.context.get("request")

        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["updated_by"] = user

        replacement = super().update(
            instance,
            validated_data,
        )

        assignment = replacement.rental_assignment
        outgoing_equipment = replacement.outgoing_equipment
        incoming_equipment = replacement.incoming_equipment

        if replacement.status in [
            RentalReplacement.Status.REQUESTED,
            RentalReplacement.Status.APPROVED,
            RentalReplacement.Status.SCHEDULED,
            RentalReplacement.Status.ASSIGNED,
            RentalReplacement.Status.IN_TRANSIT,
            RentalReplacement.Status.IN_PROGRESS,
            RentalReplacement.Status.OBSERVED,
        ]:
            incoming_equipment.operational_status = (
                RentalEquipment.OperationalStatus.RESERVED
            )

            incoming_equipment.is_available_for_rental = False

        elif (
            replacement.status
            == RentalReplacement.Status.COMPLETED
        ):
            if replacement.result in [
                RentalReplacement.Result.REPLACED,
                (
                    RentalReplacement
                    .Result
                    .REPLACED_WITH_OBSERVATIONS
                ),
            ]:
                assignment.rental_equipment = incoming_equipment
                assignment.status = RentalAssignment.Status.ACTIVE
                assignment.updated_by = user

                outgoing_equipment.operational_status = (
                    RentalEquipment
                    .OperationalStatus
                    .WITH_PROBLEMS
                )

                outgoing_equipment.is_available_for_rental = False

                incoming_equipment.operational_status = (
                    RentalEquipment.OperationalStatus.RENTED
                )

                incoming_equipment.warehouse = None
                incoming_equipment.warehouse_location = ""
                incoming_equipment.is_available_for_rental = False

                assignment.save(
                    update_fields=[
                        "rental_equipment",
                        "status",
                        "updated_by",
                        "updated_at",
                    ]
                )

        elif (
            replacement.status
            in [
                RentalReplacement.Status.REJECTED,
                RentalReplacement.Status.CANCELLED,
            ]
        ):
            incoming_equipment.operational_status = (
                RentalEquipment
                .OperationalStatus
                .READY_FOR_RENTAL
            )

            incoming_equipment.is_available_for_rental = True

        outgoing_equipment.updated_by = user
        incoming_equipment.updated_by = user

        outgoing_equipment.save(
            update_fields=[
                "operational_status",
                "is_available_for_rental",
                "updated_by",
                "updated_at",
            ]
        )

        incoming_equipment.save(
            update_fields=[
                "operational_status",
                "warehouse",
                "warehouse_location",
                "is_available_for_rental",
                "updated_by",
                "updated_at",
            ]
        )

        return replacement


class RentalReplacementListSerializer(
    RentalReplacementSerializer
):
    """
    Serializer compacto para listados de reemplazos.
    """

    class Meta(RentalReplacementSerializer.Meta):
        fields = [
            "id",
            "code",
            "rental_assignment",
            "assignment_code",
            "customer",
            "customer_name",
            "branch",
            "branch_name",
            "outgoing_equipment",
            "outgoing_equipment_display",
            "outgoing_serial_number",
            "outgoing_brand_name",
            "outgoing_model_name",
            "incoming_equipment",
            "incoming_equipment_display",
            "incoming_serial_number",
            "incoming_brand_name",
            "incoming_model_name",
            "replacement_type",
            "replacement_type_display",
            "reason",
            "reason_display",
            "status",
            "status_display",
            "result",
            "result_display",
            "assigned_technician",
            "assigned_technician_name",
            "requested_at",
            "scheduled_at",
            "completed_at",
            "archived_at",
            "is_archived",
        ]