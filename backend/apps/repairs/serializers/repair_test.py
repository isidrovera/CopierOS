# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers

from ..models import RepairTest
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class RepairTestListSerializer(
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

    test_type_name = serializers.CharField(
        source="get_test_type_display",
        read_only=True,
    )

    stage_name = serializers.CharField(
        source="get_stage_display",
        read_only=True,
    )

    result_name = serializers.CharField(
        source="get_result_display",
        read_only=True,
    )

    tested_by_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairTest

        fields = (
            "id",
            "repair",
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "test_type",
            "test_type_name",
            "stage",
            "stage_name",
            "name",
            "result",
            "result_name",
            "is_required",
            "requires_photo",
            "requires_print_sample",
            "tested_by",
            "tested_by_name",
            "tested_at",
            "pages_tested",
            "error_code",
            "retest_required",
            "retest_of",
            "display_order",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_tested_by_name(self, obj):
        user = obj.tested_by

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


class RepairTestDetailSerializer(
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

    test_type_name = serializers.CharField(
        source="get_test_type_display",
        read_only=True,
    )

    stage_name = serializers.CharField(
        source="get_stage_display",
        read_only=True,
    )

    result_name = serializers.CharField(
        source="get_result_display",
        read_only=True,
    )

    tested_by_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    archived_by_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    printed_pages_difference = serializers.IntegerField(
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = RepairTest

        fields = (
            "id",
            "repair",
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "test_type",
            "test_type_name",
            "stage",
            "stage_name",
            "name",
            "description",
            "instructions",
            "result",
            "result_name",
            "is_required",
            "requires_photo",
            "requires_print_sample",
            "tested_by",
            "tested_by_name",
            "tested_at",
            "initial_meter_total",
            "final_meter_total",
            "initial_meter_black",
            "final_meter_black",
            "initial_meter_color",
            "final_meter_color",
            "printed_pages_difference",
            "pages_tested",
            "error_code",
            "measured_value",
            "expected_value",
            "measurement_unit",
            "observations",
            "failure_description",
            "corrective_action",
            "retest_required",
            "retest_of",
            "display_order",
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

    def get_tested_by_name(self, obj):
        return self.get_user_name(
            obj.tested_by
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


class RepairTestCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = RepairTest

        fields = (
            "id",
            "repair",
            "test_type",
            "stage",
            "name",
            "description",
            "instructions",
            "is_required",
            "requires_photo",
            "requires_print_sample",
            "initial_meter_total",
            "initial_meter_black",
            "initial_meter_color",
            "expected_value",
            "measurement_unit",
            "retest_of",
            "display_order",
        )

        read_only_fields = (
            "id",
        )

    def validate_repair(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes crear pruebas para una reparación archivada."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes crear pruebas para una reparación inactiva."
            )

        return value

    def validate_name(self, value):
        name = str(
            value or ""
        ).strip()

        if not name:
            raise serializers.ValidationError(
                "El nombre de la prueba es obligatorio."
            )

        return name

    def validate_description(self, value):
        return str(
            value or ""
        ).strip()

    def validate_instructions(self, value):
        return str(
            value or ""
        ).strip()

    def validate_measurement_unit(self, value):
        return str(
            value or ""
        ).strip().lower()

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

        test_type = attrs.get(
            "test_type",
            getattr(
                instance,
                "test_type",
                None,
            ),
        )

        retest_of = attrs.get(
            "retest_of",
            getattr(
                instance,
                "retest_of",
                None,
            ),
        )

        expected_value = attrs.get(
            "expected_value",
            getattr(
                instance,
                "expected_value",
                None,
            ),
        )

        measurement_unit = str(
            attrs.get(
                "measurement_unit",
                getattr(
                    instance,
                    "measurement_unit",
                    "",
                ),
            )
            or ""
        ).strip()

        if (
            expected_value is not None
            and not measurement_unit
        ):
            raise serializers.ValidationError(
                {
                    "measurement_unit": (
                        "Debes indicar la unidad de medida "
                        "cuando registras un valor esperado."
                    )
                }
            )

        if retest_of:
            if (
                repair
                and retest_of.repair_id
                != repair.id
            ):
                raise serializers.ValidationError(
                    {
                        "retest_of": (
                            "La prueba anterior no pertenece "
                            "a esta reparación."
                        )
                    }
                )

            if (
                test_type
                and retest_of.test_type
                != test_type
            ):
                raise serializers.ValidationError(
                    {
                        "retest_of": (
                            "La nueva prueba debe ser del mismo "
                            "tipo que la prueba anterior."
                        )
                    }
                )

            if (
                instance
                and retest_of.pk
                == instance.pk
            ):
                raise serializers.ValidationError(
                    {
                        "retest_of": (
                            "Una prueba no puede referenciarse "
                            "a sí misma."
                        )
                    }
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        repair_test = RepairTest(
            result=RepairTest.Result.PENDING,
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            repair_test.full_clean()
            repair_test.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return repair_test

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        actor = get_authenticated_user(
            self
        )

        if (
            instance.result
            != RepairTest.Result.PENDING
        ):
            raise serializers.ValidationError(
                {
                    "result": (
                        "No puedes modificar la configuración "
                        "de una prueba ya ejecutada."
                    )
                }
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


class PerformRepairTestSerializer(
    serializers.Serializer
):
    result = serializers.ChoiceField(
        choices=RepairTest.Result.choices,
    )

    measured_value = serializers.DecimalField(
        required=False,
        allow_null=True,
        max_digits=14,
        decimal_places=4,
    )

    measurement_unit = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=50,
    )

    initial_meter_total = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
    )

    final_meter_total = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
    )

    initial_meter_black = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
    )

    final_meter_black = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
    )

    initial_meter_color = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
    )

    final_meter_color = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
    )

    pages_tested = serializers.IntegerField(
        required=False,
        min_value=0,
        default=0,
    )

    error_code = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )

    observations = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    failure_description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    corrective_action = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    retest_required = serializers.BooleanField(
        required=False,
        default=False,
    )

    def validate(self, attrs):
        repair_test = self.context.get(
            "repair_test"
        )

        if not repair_test:
            raise serializers.ValidationError(
                "No se encontró la prueba."
            )

        if repair_test.is_archived:
            raise serializers.ValidationError(
                "La prueba se encuentra archivada."
            )

        if not repair_test.repair.is_active:
            raise serializers.ValidationError(
                "La reparación ya no está activa."
            )

        result = attrs["result"]

        if result == RepairTest.Result.PENDING:
            raise serializers.ValidationError(
                {
                    "result": (
                        "Debes registrar un resultado definitivo."
                    )
                }
            )

        observations = str(
            attrs.get(
                "observations",
                "",
            )
            or ""
        ).strip()

        failure_description = str(
            attrs.get(
                "failure_description",
                "",
            )
            or ""
        ).strip()

        corrective_action = str(
            attrs.get(
                "corrective_action",
                "",
            )
            or ""
        ).strip()

        error_code = str(
            attrs.get(
                "error_code",
                "",
            )
            or ""
        ).strip().upper()

        measurement_unit = str(
            attrs.get(
                "measurement_unit",
                repair_test.measurement_unit,
            )
            or ""
        ).strip().lower()

        measured_value = attrs.get(
            "measured_value",
            None,
        )

        retest_required = attrs.get(
            "retest_required",
            False,
        )

        if (
            measured_value is not None
            and not measurement_unit
        ):
            raise serializers.ValidationError(
                {
                    "measurement_unit": (
                        "Debes indicar la unidad de medida."
                    )
                }
            )

        if (
            result == RepairTest.Result.FAILED
            and not failure_description
        ):
            raise serializers.ValidationError(
                {
                    "failure_description": (
                        "Debes describir la falla encontrada."
                    )
                }
            )

        if (
            result == RepairTest.Result.FAILED
            and not retest_required
        ):
            raise serializers.ValidationError(
                {
                    "retest_required": (
                        "Una prueba fallida debe requerir "
                        "una nueva prueba."
                    )
                }
            )

        if (
            result
            == RepairTest.Result.PASSED_WITH_OBSERVATIONS
            and not observations
        ):
            raise serializers.ValidationError(
                {
                    "observations": (
                        "Debes registrar las observaciones "
                        "de la prueba."
                    )
                }
            )

        if (
            result == RepairTest.Result.NOT_APPLICABLE
            and repair_test.is_required
            and not observations
        ):
            raise serializers.ValidationError(
                {
                    "observations": (
                        "Debes indicar por qué la prueba "
                        "obligatoria no aplica."
                    )
                }
            )

        meter_pairs = (
            (
                "final_meter_total",
                attrs.get(
                    "initial_meter_total",
                    repair_test.initial_meter_total,
                ),
                attrs.get(
                    "final_meter_total",
                    repair_test.final_meter_total,
                ),
            ),
            (
                "final_meter_black",
                attrs.get(
                    "initial_meter_black",
                    repair_test.initial_meter_black,
                ),
                attrs.get(
                    "final_meter_black",
                    repair_test.final_meter_black,
                ),
            ),
            (
                "final_meter_color",
                attrs.get(
                    "initial_meter_color",
                    repair_test.initial_meter_color,
                ),
                attrs.get(
                    "final_meter_color",
                    repair_test.final_meter_color,
                ),
            ),
        )

        for (
            field_name,
            initial_value,
            final_value,
        ) in meter_pairs:
            if (
                initial_value is not None
                and final_value is not None
                and final_value < initial_value
            ):
                raise serializers.ValidationError(
                    {
                        field_name: (
                            "El contador final no puede ser menor "
                            "que el contador inicial."
                        )
                    }
                )

        attrs["observations"] = observations
        attrs["failure_description"] = failure_description
        attrs["corrective_action"] = corrective_action
        attrs["error_code"] = error_code
        attrs["measurement_unit"] = measurement_unit

        return attrs


class ResetRepairTestSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=5000,
    )

    def validate_reason(self, value):
        reason = str(
            value or ""
        ).strip()

        if not reason:
            raise serializers.ValidationError(
                "El motivo para reiniciar la prueba es obligatorio."
            )

        return reason

    def validate(self, attrs):
        repair_test = self.context.get(
            "repair_test"
        )

        if not repair_test:
            raise serializers.ValidationError(
                "No se encontró la prueba."
            )

        if repair_test.is_archived:
            raise serializers.ValidationError(
                "La prueba se encuentra archivada."
            )

        if (
            repair_test.result
            == RepairTest.Result.PENDING
        ):
            raise serializers.ValidationError(
                "La prueba ya se encuentra pendiente."
            )

        return attrs


class ArchiveRepairTestSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )