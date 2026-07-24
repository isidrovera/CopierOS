# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from ..models import RepairDiagnosis
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class RepairDiagnosisListSerializer(
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
        allow_null=True,
    )

    diagnosis_type_name = serializers.CharField(
        source="get_diagnosis_type_display",
        read_only=True,
    )

    severity_name = serializers.CharField(
        source="get_severity_display",
        read_only=True,
    )

    repairability_name = serializers.CharField(
        source="get_repairability_display",
        read_only=True,
    )

    confirmed_by_name = serializers.CharField(
        source="confirmed_by.full_name",
        read_only=True,
        allow_null=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairDiagnosis

        fields = (
            "id",
            "repair",
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "technician",
            "technician_name",
            "diagnosis_type",
            "diagnosis_type_name",
            "severity",
            "severity_name",
            "repairability",
            "repairability_name",
            "diagnosed_at",
            "technical_diagnosis",
            "requires_parts",
            "requires_external_service",
            "requires_additional_testing",
            "requires_disassembly",
            "is_main_diagnosis",
            "is_confirmed",
            "confirmed_by",
            "confirmed_by_name",
            "confirmed_at",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class RepairDiagnosisDetailSerializer(
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
        allow_null=True,
    )

    diagnosis_type_name = serializers.CharField(
        source="get_diagnosis_type_display",
        read_only=True,
    )

    severity_name = serializers.CharField(
        source="get_severity_display",
        read_only=True,
    )

    repairability_name = serializers.CharField(
        source="get_repairability_display",
        read_only=True,
    )

    confirmed_by_name = serializers.CharField(
        source="confirmed_by.full_name",
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

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairDiagnosis

        fields = (
            "id",
            "repair",
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "technician",
            "technician_name",
            "diagnosis_type",
            "diagnosis_type_name",
            "severity",
            "severity_name",
            "repairability",
            "repairability_name",
            "diagnosed_at",
            "reported_symptoms",
            "observed_symptoms",
            "probable_cause",
            "confirmed_cause",
            "technical_diagnosis",
            "recommended_work",
            "required_parts_description",
            "estimated_work_hours",
            "estimated_parts_cost",
            "estimated_external_cost",
            "requires_parts",
            "requires_external_service",
            "requires_additional_testing",
            "requires_disassembly",
            "is_main_diagnosis",
            "is_confirmed",
            "confirmed_by",
            "confirmed_by_name",
            "confirmed_at",
            "observations",
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


class RepairDiagnosisCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = RepairDiagnosis

        fields = (
            "repair",
            "diagnosis_type",
            "severity",
            "repairability",
            "diagnosed_at",
            "reported_symptoms",
            "observed_symptoms",
            "probable_cause",
            "confirmed_cause",
            "technical_diagnosis",
            "recommended_work",
            "required_parts_description",
            "estimated_work_hours",
            "estimated_parts_cost",
            "estimated_external_cost",
            "requires_parts",
            "requires_external_service",
            "requires_additional_testing",
            "requires_disassembly",
            "is_main_diagnosis",
            "observations",
        )

    def validate_repair(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes registrar diagnósticos en una reparación archivada."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes registrar diagnósticos en una reparación inactiva."
            )

        return value

    def validate_reported_symptoms(self, value):
        return str(
            value or ""
        ).strip()

    def validate_observed_symptoms(self, value):
        return str(
            value or ""
        ).strip()

    def validate_probable_cause(self, value):
        return str(
            value or ""
        ).strip()

    def validate_confirmed_cause(self, value):
        return str(
            value or ""
        ).strip()

    def validate_technical_diagnosis(self, value):
        diagnosis = str(
            value or ""
        ).strip()

        if not diagnosis:
            raise serializers.ValidationError(
                "El diagnóstico técnico es obligatorio."
            )

        return diagnosis

    def validate_recommended_work(self, value):
        return str(
            value or ""
        ).strip()

    def validate_required_parts_description(self, value):
        return str(
            value or ""
        ).strip()

    def validate_observations(self, value):
        return str(
            value or ""
        ).strip()

    def validate(self, attrs):
        instance = self.instance

        repair = attrs.get(
            "repair",
            getattr(
                instance,
                "repair",
                None,
            ),
        )

        is_main_diagnosis = attrs.get(
            "is_main_diagnosis",
            getattr(
                instance,
                "is_main_diagnosis",
                False,
            ),
        )

        requires_parts = attrs.get(
            "requires_parts",
            getattr(
                instance,
                "requires_parts",
                False,
            ),
        )

        required_parts_description = attrs.get(
            "required_parts_description",
            getattr(
                instance,
                "required_parts_description",
                "",
            ),
        )

        repairability = attrs.get(
            "repairability",
            getattr(
                instance,
                "repairability",
                RepairDiagnosis.Repairability.PENDING,
            ),
        )

        requires_external_service = attrs.get(
            "requires_external_service",
            getattr(
                instance,
                "requires_external_service",
                False,
            ),
        )

        if not repair:
            raise serializers.ValidationError(
                {
                    "repair": (
                        "Debes seleccionar una reparación."
                    )
                }
            )

        if is_main_diagnosis:
            queryset = RepairDiagnosis.objects.filter(
                repair=repair,
                is_main_diagnosis=True,
                archived_at__isnull=True,
            )

            if instance:
                queryset = queryset.exclude(
                    pk=instance.pk,
                )

            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "is_main_diagnosis": (
                            "La reparación ya tiene un "
                            "diagnóstico principal."
                        )
                    }
                )

        if (
            requires_parts
            and not str(
                required_parts_description or ""
            ).strip()
        ):
            raise serializers.ValidationError(
                {
                    "required_parts_description": (
                        "Debes indicar los repuestos requeridos."
                    )
                }
            )

        if (
            not requires_parts
            and str(
                required_parts_description or ""
            ).strip()
        ):
            raise serializers.ValidationError(
                {
                    "required_parts_description": (
                        "No debes indicar repuestos si no "
                        "son requeridos."
                    )
                }
            )

        if (
            repairability
            == RepairDiagnosis.Repairability.REPAIRABLE_WITH_PARTS
            and not requires_parts
        ):
            raise serializers.ValidationError(
                {
                    "requires_parts": (
                        "Debes marcar que requiere repuestos."
                    )
                }
            )

        if (
            repairability
            == (
                RepairDiagnosis.Repairability
                .REPAIRABLE_WITH_EXTERNAL_SERVICE
            )
            and not requires_external_service
        ):
            raise serializers.ValidationError(
                {
                    "requires_external_service": (
                        "Debes marcar que requiere servicio externo."
                    )
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        diagnosis = RepairDiagnosis(
            technician=actor,
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            diagnosis.full_clean()
            diagnosis.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return diagnosis

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


class ConfirmRepairDiagnosisSerializer(
    serializers.Serializer
):
    confirmed_cause = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    observations = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate(self, attrs):
        diagnosis = self.context.get(
            "diagnosis"
        )

        if not diagnosis:
            raise serializers.ValidationError(
                "No se encontró el diagnóstico."
            )

        if diagnosis.is_archived:
            raise serializers.ValidationError(
                "El diagnóstico se encuentra archivado."
            )

        if diagnosis.is_confirmed:
            raise serializers.ValidationError(
                "El diagnóstico ya se encuentra confirmado."
            )

        return attrs


class SetMainRepairDiagnosisSerializer(
    serializers.Serializer
):
    def validate(self, attrs):
        diagnosis = self.context.get(
            "diagnosis"
        )

        if not diagnosis:
            raise serializers.ValidationError(
                "No se encontró el diagnóstico."
            )

        if diagnosis.is_archived:
            raise serializers.ValidationError(
                "El diagnóstico se encuentra archivado."
            )

        if diagnosis.is_main_diagnosis:
            raise serializers.ValidationError(
                "El diagnóstico ya es el principal."
            )

        return attrs


class ArchiveRepairDiagnosisSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )