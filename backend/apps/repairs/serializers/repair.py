# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from ..models import Repair
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


User = get_user_model()


class RepairListSerializer(serializers.ModelSerializer):
    equipment_name = serializers.SerializerMethodField()

    equipment_serial_number = serializers.CharField(
        source="equipment.serial_number",
        read_only=True,
    )

    equipment_internal_code = serializers.CharField(
        source="equipment.internal_code",
        read_only=True,
        allow_null=True,
    )

    equipment_brand_name = serializers.CharField(
        source="equipment.equipment_model.brand.name",
        read_only=True,
        allow_null=True,
    )

    brand_name = serializers.CharField(
        source="equipment.equipment_model.brand.name",
        read_only=True,
        allow_null=True,
    )

    equipment_model_name = serializers.CharField(
        source="equipment.equipment_model.name",
        read_only=True,
        allow_null=True,
    )

    model_name = serializers.CharField(
        source="equipment.equipment_model.name",
        read_only=True,
        allow_null=True,
    )

    equipment_type_name = serializers.CharField(
        source="equipment.equipment_model.equipment_type.name",
        read_only=True,
        allow_null=True,
    )

    assigned_technician_name = serializers.SerializerMethodField()

    repair_type_name = serializers.CharField(
        source="get_repair_type_display",
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    priority_name = serializers.CharField(
        source="get_priority_display",
        read_only=True,
    )

    final_condition_name = serializers.CharField(
        source="get_final_condition_display",
        read_only=True,
    )

    photo_count = serializers.SerializerMethodField()
    checklist_count = serializers.SerializerMethodField()
    test_count = serializers.SerializerMethodField()
    diagnosis_count = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = Repair

        fields = (
            "id",
            "code",
            "equipment",
            "equipment_name",
            "equipment_serial_number",
            "equipment_internal_code",
            "equipment_brand_name",
            "brand_name",
            "equipment_model_name",
            "model_name",
            "equipment_type_name",
            "repair_type",
            "repair_type_name",
            "status",
            "status_name",
            "priority",
            "priority_name",
            "is_active",
            "assigned_technician",
            "assigned_technician_name",
            "requested_at",
            "assigned_at",
            "review_started_at",
            "repair_started_at",
            "testing_started_at",
            "completed_at",
            "delivered_at",
            "reported_problem",
            "requires_parts",
            "requires_external_service",
            "requires_follow_up",
            "final_condition",
            "final_condition_name",
            "minimum_photos_required",
            "minimum_photos_completed",
            "checklist_completed",
            "tests_completed",
            "snmp_validation_completed",
            "photo_count",
            "checklist_count",
            "test_count",
            "diagnosis_count",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_equipment_name(self, obj):
        equipment = obj.equipment

        if not equipment:
            return "Equipo sin identificar"

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

        brand_name = str(
            getattr(
                brand,
                "name",
                "",
            )
            or ""
        ).strip()

        model_name = str(
            getattr(
                equipment_model,
                "name",
                "",
            )
            or ""
        ).strip()

        complete_name = " ".join(
            value
            for value in (
                brand_name,
                model_name,
            )
            if value
        ).strip()

        return (
            complete_name
            or str(equipment)
            or "Equipo sin identificar"
        )

    def get_assigned_technician_name(self, obj):
        technician = obj.assigned_technician

        if not technician:
            return None

        full_name = str(
            technician.get_full_name()
            or ""
        ).strip()

        return (
            full_name
            or technician.email
            or technician.username
        )

    def get_photo_count(self, obj):
        annotated_count = getattr(
            obj,
            "total_photos",
            None,
        )

        if annotated_count is not None:
            return annotated_count

        return obj.photos.filter(
            archived_at__isnull=True,
        ).count()

    def get_checklist_count(self, obj):
        return obj.checklists.filter(
            archived_at__isnull=True,
        ).count()

    def get_test_count(self, obj):
        annotated_count = getattr(
            obj,
            "total_tests",
            None,
        )

        if annotated_count is not None:
            return annotated_count

        return obj.tests.filter(
            archived_at__isnull=True,
        ).count()

    def get_diagnosis_count(self, obj):
        annotated_count = getattr(
            obj,
            "total_diagnoses",
            None,
        )

        if annotated_count is not None:
            return annotated_count

        return obj.diagnoses.filter(
            archived_at__isnull=True,
        ).count()


class RepairDetailSerializer(serializers.ModelSerializer):
    equipment_name = serializers.SerializerMethodField()

    equipment_serial_number = serializers.CharField(
        source="equipment.serial_number",
        read_only=True,
    )

    equipment_internal_code = serializers.CharField(
        source="equipment.internal_code",
        read_only=True,
        allow_null=True,
    )

    equipment_brand_name = serializers.CharField(
        source="equipment.equipment_model.brand.name",
        read_only=True,
        allow_null=True,
    )

    brand_name = serializers.CharField(
        source="equipment.equipment_model.brand.name",
        read_only=True,
        allow_null=True,
    )

    equipment_model_name = serializers.CharField(
        source="equipment.equipment_model.name",
        read_only=True,
        allow_null=True,
    )

    model_name = serializers.CharField(
        source="equipment.equipment_model.name",
        read_only=True,
        allow_null=True,
    )

    equipment_type_name = serializers.CharField(
        source="equipment.equipment_model.equipment_type.name",
        read_only=True,
        allow_null=True,
    )

    requested_by_name = serializers.SerializerMethodField()
    assigned_technician_name = serializers.SerializerMethodField()
    assigned_by_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    archived_by_name = serializers.SerializerMethodField()

    repair_type_name = serializers.CharField(
        source="get_repair_type_display",
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    priority_name = serializers.CharField(
        source="get_priority_display",
        read_only=True,
    )

    final_condition_name = serializers.CharField(
        source="get_final_condition_display",
        read_only=True,
    )

    photo_count = serializers.SerializerMethodField()
    checklist_count = serializers.SerializerMethodField()
    test_count = serializers.SerializerMethodField()
    diagnosis_count = serializers.SerializerMethodField()
    component_count = serializers.SerializerMethodField()
    assignment_count = serializers.SerializerMethodField()
    snmp_validation_count = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = Repair

        fields = (
            "id",
            "code",
            "equipment",
            "equipment_name",
            "equipment_serial_number",
            "equipment_internal_code",
            "equipment_brand_name",
            "brand_name",
            "equipment_model_name",
            "model_name",
            "equipment_type_name",
            "repair_type",
            "repair_type_name",
            "status",
            "status_name",
            "priority",
            "priority_name",
            "is_active",
            "requested_by",
            "requested_by_name",
            "assigned_technician",
            "assigned_technician_name",
            "assigned_by",
            "assigned_by_name",
            "requested_at",
            "assigned_at",
            "review_started_at",
            "repair_started_at",
            "testing_started_at",
            "completed_at",
            "delivered_at",
            "cancelled_at",
            "reported_problem",
            "initial_observations",
            "work_summary",
            "pending_work",
            "final_condition",
            "final_condition_name",
            "final_observations",
            "requires_parts",
            "requires_external_service",
            "requires_follow_up",
            "follow_up_date",
            "minimum_photos_required",
            "minimum_photos_completed",
            "checklist_completed",
            "tests_completed",
            "snmp_validation_completed",
            "closure_notes",
            "photo_count",
            "checklist_count",
            "test_count",
            "diagnosis_count",
            "component_count",
            "assignment_count",
            "snmp_validation_count",
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

    def get_equipment_name(self, obj):
        equipment = obj.equipment

        if not equipment:
            return "Equipo sin identificar"

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

        brand_name = str(
            getattr(
                brand,
                "name",
                "",
            )
            or ""
        ).strip()

        model_name = str(
            getattr(
                equipment_model,
                "name",
                "",
            )
            or ""
        ).strip()

        complete_name = " ".join(
            value
            for value in (
                brand_name,
                model_name,
            )
            if value
        ).strip()

        return (
            complete_name
            or str(equipment)
            or "Equipo sin identificar"
        )

    def get_user_name(self, user):
        if not user:
            return None

        full_name = str(
            user.get_full_name()
            or ""
        ).strip()

        return (
            full_name
            or user.email
            or user.username
        )

    def get_requested_by_name(self, obj):
        return self.get_user_name(
            obj.requested_by
        )

    def get_assigned_technician_name(self, obj):
        return self.get_user_name(
            obj.assigned_technician
        )

    def get_assigned_by_name(self, obj):
        return self.get_user_name(
            obj.assigned_by
        )

    def get_created_by_name(self, obj):
        return self.get_user_name(
            obj.created_by
        )

    def get_updated_by_name(self, obj):
        return self.get_user_name(
            obj.updated_by
        )

    def get_archived_by_name(self, obj):
        return self.get_user_name(
            obj.archived_by
        )

    def get_photo_count(self, obj):
        annotated_count = getattr(
            obj,
            "total_photos",
            None,
        )

        if annotated_count is not None:
            return annotated_count

        return obj.photos.filter(
            archived_at__isnull=True,
        ).count()

    def get_checklist_count(self, obj):
        return obj.checklists.filter(
            archived_at__isnull=True,
        ).count()

    def get_test_count(self, obj):
        annotated_count = getattr(
            obj,
            "total_tests",
            None,
        )

        if annotated_count is not None:
            return annotated_count

        return obj.tests.filter(
            archived_at__isnull=True,
        ).count()

    def get_diagnosis_count(self, obj):
        annotated_count = getattr(
            obj,
            "total_diagnoses",
            None,
        )

        if annotated_count is not None:
            return annotated_count

        return obj.diagnoses.filter(
            archived_at__isnull=True,
        ).count()

    def get_component_count(self, obj):
        return obj.repair_components.filter(
            archived_at__isnull=True,
        ).count()

    def get_assignment_count(self, obj):
        return obj.assignments.filter(
            archived_at__isnull=True,
        ).count()

    def get_snmp_validation_count(self, obj):
        return obj.snmp_validations.filter(
            archived_at__isnull=True,
        ).count()


class RepairCreateUpdateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=50,
    )

    class Meta:
        model = Repair

        fields = (
            "id",
            "code",
            "equipment",
            "repair_type",
            "priority",
            "reported_problem",
            "initial_observations",
            "work_summary",
            "pending_work",
            "final_condition",
            "final_observations",
            "requires_parts",
            "requires_external_service",
            "requires_follow_up",
            "follow_up_date",
            "minimum_photos_required",
            "closure_notes",
        )

        read_only_fields = (
            "id",
        )

    def validate_code(self, value):
        code = str(
            value or ""
        ).strip().upper()

        if not code:
            return code

        queryset = Repair.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una reparación con este código."
            )

        return code

    def validate_equipment(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes crear una reparación para un equipo archivado."
            )

        return value

    def validate_reported_problem(self, value):
        return str(
            value or ""
        ).strip()

    def validate_initial_observations(self, value):
        return str(
            value or ""
        ).strip()

    def validate_work_summary(self, value):
        return str(
            value or ""
        ).strip()

    def validate_pending_work(self, value):
        return str(
            value or ""
        ).strip()

    def validate_final_observations(self, value):
        return str(
            value or ""
        ).strip()

    def validate_closure_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate(self, attrs):
        instance = self.instance

        equipment = attrs.get(
            "equipment",
            getattr(
                instance,
                "equipment",
                None,
            ),
        )

        requires_follow_up = attrs.get(
            "requires_follow_up",
            getattr(
                instance,
                "requires_follow_up",
                False,
            ),
        )

        follow_up_date = attrs.get(
            "follow_up_date",
            getattr(
                instance,
                "follow_up_date",
                None,
            ),
        )

        minimum_photos_required = attrs.get(
            "minimum_photos_required",
            getattr(
                instance,
                "minimum_photos_required",
                10,
            ),
        )

        if not equipment:
            raise serializers.ValidationError(
                {
                    "equipment": (
                        "Debes seleccionar un equipo."
                    )
                }
            )

        active_repairs = Repair.objects.filter(
            equipment=equipment,
            is_active=True,
            archived_at__isnull=True,
        )

        if instance:
            active_repairs = active_repairs.exclude(
                pk=instance.pk,
            )

        if active_repairs.exists():
            raise serializers.ValidationError(
                {
                    "equipment": (
                        "Este equipo ya tiene una reparación activa."
                    )
                }
            )

        if requires_follow_up and not follow_up_date:
            raise serializers.ValidationError(
                {
                    "follow_up_date": (
                        "Debes indicar la fecha de seguimiento."
                    )
                }
            )

        if not requires_follow_up and follow_up_date:
            raise serializers.ValidationError(
                {
                    "follow_up_date": (
                        "No debes indicar una fecha si el seguimiento "
                        "no está habilitado."
                    )
                }
            )

        if minimum_photos_required < 1:
            raise serializers.ValidationError(
                {
                    "minimum_photos_required": (
                        "Debe requerirse al menos una fotografía."
                    )
                }
            )

        return attrs

    def generate_repair_code(self):
        current_year = timezone.localdate().year

        last_repair = (
            Repair.objects.filter(
                code__startswith=f"REP-{current_year}-",
            )
            .order_by("-code")
            .first()
        )

        next_number = 1

        if last_repair:
            try:
                next_number = (
                    int(
                        last_repair.code.split("-")[-1]
                    )
                    + 1
                )
            except (
                TypeError,
                ValueError,
                IndexError,
            ):
                next_number = (
                    Repair.objects.filter(
                        code__startswith=(
                            f"REP-{current_year}-"
                        ),
                    ).count()
                    + 1
                )

        return (
            f"REP-{current_year}-"
            f"{next_number:06d}"
        )

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        code = str(
            validated_data.pop(
                "code",
                "",
            )
            or ""
        ).strip().upper()

        if not code:
            code = self.generate_repair_code()

            while Repair.objects.filter(
                code__iexact=code,
            ).exists():
                parts = code.split("-")
                number = int(parts[-1]) + 1

                code = (
                    f"REP-{parts[1]}-"
                    f"{number:06d}"
                )

        repair = Repair(
            code=code,
            requested_by=actor,
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            repair.full_clean()
            repair.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return repair

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


class RepairStatusChangeSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Repair.Status.choices,
    )

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2000,
    )

    observations = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    final_condition = serializers.ChoiceField(
        choices=Repair.FinalCondition.choices,
        required=False,
    )

    work_summary = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    final_observations = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    closure_notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def validate(self, attrs):
        repair = self.context.get(
            "repair"
        )

        if not repair:
            raise serializers.ValidationError(
                "No se encontró la reparación."
            )

        new_status = attrs["status"]

        if new_status == repair.status:
            raise serializers.ValidationError(
                {
                    "status": (
                        "La reparación ya se encuentra "
                        "en este estado."
                    )
                }
            )

        if new_status == Repair.Status.ASSIGNED:
            if not repair.assigned_technician_id:
                raise serializers.ValidationError(
                    {
                        "status": (
                            "Debes asignar un técnico antes "
                            "de cambiar a estado asignada."
                        )
                    }
                )

        if new_status in (
            Repair.Status.COMPLETED,
            Repair.Status.DELIVERED,
        ):
            final_condition = attrs.get(
                "final_condition",
                repair.final_condition,
            )

            if (
                final_condition
                == Repair.FinalCondition.NOT_DEFINED
            ):
                raise serializers.ValidationError(
                    {
                        "final_condition": (
                            "Debes indicar la condición final."
                        )
                    }
                )

            if not repair.checklist_completed:
                raise serializers.ValidationError(
                    {
                        "status": (
                            "La lista de revisión debe estar completa."
                        )
                    }
                )

            if not repair.tests_completed:
                raise serializers.ValidationError(
                    {
                        "status": (
                            "Las pruebas obligatorias deben estar completas."
                        )
                    }
                )

            if not repair.minimum_photos_completed:
                raise serializers.ValidationError(
                    {
                        "status": (
                            "Las fotografías mínimas deben estar completas."
                        )
                    }
                )

        return attrs


class RepairAssignmentActionSerializer(serializers.Serializer):
    technician = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(
            is_active=True,
        ),
    )

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2000,
    )


class ArchiveRepairSerializer(serializers.Serializer):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )