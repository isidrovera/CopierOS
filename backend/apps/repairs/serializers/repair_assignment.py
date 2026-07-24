# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from ..models import (
    Repair,
    RepairAssignment,
)
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)
from django.contrib.auth import get_user_model
User = get_user_model()

class RepairAssignmentListSerializer(
    serializers.ModelSerializer
):
    repair_code = serializers.CharField(
        source="repair.code",
        read_only=True,
    )

    equipment_id = serializers.UUIDField(
        source="repair.equipment_id",
        read_only=True,
    )

    equipment_serial_number = serializers.CharField(
        source="repair.equipment.serial_number",
        read_only=True,
    )

    technician_name = serializers.CharField(
        source="technician.full_name",
        read_only=True,
    )

    assigned_by_name = serializers.CharField(
        source="assigned_by.full_name",
        read_only=True,
        allow_null=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairAssignment

        fields = (
            "id",
            "repair",
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "technician",
            "technician_name",
            "assigned_by",
            "assigned_by_name",
            "status",
            "status_name",
            "is_active",
            "assigned_at",
            "accepted_at",
            "started_at",
            "ended_at",
            "reassigned_at",
            "rejected_at",
            "cancelled_at",
            "assignment_reason",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class RepairAssignmentDetailSerializer(
    serializers.ModelSerializer
):
    repair_code = serializers.CharField(
        source="repair.code",
        read_only=True,
    )

    equipment_id = serializers.UUIDField(
        source="repair.equipment_id",
        read_only=True,
    )

    equipment_serial_number = serializers.CharField(
        source="repair.equipment.serial_number",
        read_only=True,
    )

    technician_name = serializers.CharField(
        source="technician.full_name",
        read_only=True,
    )

    assigned_by_name = serializers.CharField(
        source="assigned_by.full_name",
        read_only=True,
        allow_null=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.full_name",
        read_only=True,
        allow_null=True,
    )

    updated_by_name = serializers.CharField(
        source="updated_by.full_name",
        read_only=True,
        allow_null=True,
    )

    archived_by_name = serializers.CharField(
        source="archived_by.full_name",
        read_only=True,
        allow_null=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairAssignment

        fields = (
            "id",
            "repair",
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "technician",
            "technician_name",
            "assigned_by",
            "assigned_by_name",
            "status",
            "status_name",
            "is_active",
            "assigned_at",
            "accepted_at",
            "started_at",
            "ended_at",
            "reassigned_at",
            "rejected_at",
            "cancelled_at",
            "assignment_reason",
            "technician_observations",
            "completion_notes",
            "reassignment_reason",
            "rejection_reason",
            "cancellation_reason",
            "is_archived",
            "archived_at",
            "archived_reason",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_by",
            "archived_by_name",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class RepairAssignmentCreateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = RepairAssignment

        fields = (
            "repair",
            "technician",
            "assignment_reason",
        )

    def validate_repair(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes asignar una reparación archivada."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes asignar una reparación inactiva."
            )

        if value.status in (
            Repair.Status.COMPLETED,
            Repair.Status.DELIVERED,
            Repair.Status.CANCELLED,
        ):
            raise serializers.ValidationError(
                "La reparación ya se encuentra cerrada."
            )

        return value

    def validate_technician(self, value):
        if not value.is_active:
            raise serializers.ValidationError(
                "El técnico seleccionado está inactivo."
            )

        return value

    def validate_assignment_reason(self, value):
        return str(
            value or ""
        ).strip()

    def validate(self, attrs):
        repair = attrs.get(
            "repair"
        )

        technician = attrs.get(
            "technician"
        )

        if not repair:
            raise serializers.ValidationError(
                {
                    "repair": (
                        "Debes seleccionar una reparación."
                    )
                }
            )

        if not technician:
            raise serializers.ValidationError(
                {
                    "technician": (
                        "Debes seleccionar un técnico."
                    )
                }
            )

        active_assignment = (
            RepairAssignment.objects.filter(
                repair=repair,
                is_active=True,
                archived_at__isnull=True,
            )
        )

        if active_assignment.exists():
            raise serializers.ValidationError(
                {
                    "repair": (
                        "La reparación ya tiene una "
                        "asignación activa."
                    )
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        assignment = RepairAssignment(
            assigned_by=actor,
            created_by=actor,
            updated_by=actor,
            status=RepairAssignment.Status.ASSIGNED,
            is_active=True,
            assigned_at=timezone.now(),
            **validated_data,
        )

        try:
            assignment.full_clean()
            assignment.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return assignment


class RepairAssignmentUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = RepairAssignment

        fields = (
            "assignment_reason",
            "technician_observations",
            "completion_notes",
        )

    def validate_assignment_reason(self, value):
        return str(
            value or ""
        ).strip()

    def validate_technician_observations(self, value):
        return str(
            value or ""
        ).strip()

    def validate_completion_notes(self, value):
        return str(
            value or ""
        ).strip()

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        actor = get_authenticated_user(
            self
        )

        for field, value in validated_data.items():
            setattr(
                instance,
                field,
                value,
            )

        if actor:
            instance.updated_by = actor

        try:
            instance.full_clean()
            instance.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return instance


class RepairAssignmentAcceptSerializer(
    serializers.Serializer
):
    observations = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate(self, attrs):
        assignment = self.context.get(
            "assignment"
        )

        if not assignment:
            raise serializers.ValidationError(
                "No se encontró la asignación."
            )

        if assignment.is_archived:
            raise serializers.ValidationError(
                "La asignación se encuentra archivada."
            )

        if not assignment.is_active:
            raise serializers.ValidationError(
                "La asignación ya no está activa."
            )

        if assignment.status != RepairAssignment.Status.ASSIGNED:
            raise serializers.ValidationError(
                {
                    "status": (
                        "Solo una asignación pendiente puede aceptarse."
                    )
                }
            )

        return attrs


class RepairAssignmentStartSerializer(
    serializers.Serializer
):
    observations = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate(self, attrs):
        assignment = self.context.get(
            "assignment"
        )

        if not assignment:
            raise serializers.ValidationError(
                "No se encontró la asignación."
            )

        if assignment.is_archived:
            raise serializers.ValidationError(
                "La asignación se encuentra archivada."
            )

        if not assignment.is_active:
            raise serializers.ValidationError(
                "La asignación ya no está activa."
            )

        if assignment.status not in (
            RepairAssignment.Status.ASSIGNED,
            RepairAssignment.Status.ACCEPTED,
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "La asignación no puede iniciarse "
                        "desde su estado actual."
                    )
                }
            )

        return attrs


class RepairAssignmentCompleteSerializer(
    serializers.Serializer
):
    completion_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate(self, attrs):
        assignment = self.context.get(
            "assignment"
        )

        if not assignment:
            raise serializers.ValidationError(
                "No se encontró la asignación."
            )

        if assignment.is_archived:
            raise serializers.ValidationError(
                "La asignación se encuentra archivada."
            )

        if not assignment.is_active:
            raise serializers.ValidationError(
                "La asignación ya no está activa."
            )

        if assignment.status not in (
            RepairAssignment.Status.ACCEPTED,
            RepairAssignment.Status.IN_PROGRESS,
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "La asignación no puede completarse "
                        "desde su estado actual."
                    )
                }
            )

        return attrs


class RepairAssignmentReassignSerializer(
    serializers.Serializer
):
    technician = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(
            is_active=True,
        ),
    )

    reason = serializers.CharField(
        max_length=5000,
    )

    assignment_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate_reason(self, value):
        reason = str(
            value or ""
        ).strip()

        if not reason:
            raise serializers.ValidationError(
                "El motivo de reasignación es obligatorio."
            )

        return reason

    def validate_assignment_reason(self, value):
        return str(
            value or ""
        ).strip()

    def validate(self, attrs):
        assignment = self.context.get(
            "assignment"
        )

        if not assignment:
            raise serializers.ValidationError(
                "No se encontró la asignación."
            )

        if assignment.is_archived:
            raise serializers.ValidationError(
                "La asignación se encuentra archivada."
            )

        if not assignment.is_active:
            raise serializers.ValidationError(
                "La asignación ya no está activa."
            )

        technician = attrs.get(
            "technician"
        )

        if technician.id == assignment.technician_id:
            raise serializers.ValidationError(
                {
                    "technician": (
                        "Debes seleccionar un técnico diferente."
                    )
                }
            )

        return attrs


class RepairAssignmentRejectSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        max_length=5000,
    )

    observations = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate_reason(self, value):
        reason = str(
            value or ""
        ).strip()

        if not reason:
            raise serializers.ValidationError(
                "El motivo del rechazo es obligatorio."
            )

        return reason

    def validate(self, attrs):
        assignment = self.context.get(
            "assignment"
        )

        if not assignment:
            raise serializers.ValidationError(
                "No se encontró la asignación."
            )

        if assignment.is_archived:
            raise serializers.ValidationError(
                "La asignación se encuentra archivada."
            )

        if not assignment.is_active:
            raise serializers.ValidationError(
                "La asignación ya no está activa."
            )

        if assignment.status not in (
            RepairAssignment.Status.ASSIGNED,
            RepairAssignment.Status.ACCEPTED,
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "La asignación no puede rechazarse "
                        "desde su estado actual."
                    )
                }
            )

        return attrs


class RepairAssignmentCancelSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        max_length=5000,
    )

    def validate_reason(self, value):
        reason = str(
            value or ""
        ).strip()

        if not reason:
            raise serializers.ValidationError(
                "El motivo de cancelación es obligatorio."
            )

        return reason

    def validate(self, attrs):
        assignment = self.context.get(
            "assignment"
        )

        if not assignment:
            raise serializers.ValidationError(
                "No se encontró la asignación."
            )

        if assignment.is_archived:
            raise serializers.ValidationError(
                "La asignación se encuentra archivada."
            )

        if not assignment.is_active:
            raise serializers.ValidationError(
                "La asignación ya no está activa."
            )

        return attrs


class ArchiveRepairAssignmentSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )