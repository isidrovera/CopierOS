# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from ..models import (
    ComponentCompatibility,
    EquipmentComponentAssignment,
)
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class EquipmentComponentAssignmentListSerializer(
    serializers.ModelSerializer
):
    equipment_internal_code = serializers.CharField(
        source="equipment.internal_code",
        read_only=True,
    )

    equipment_serial = serializers.CharField(
        source="equipment.serial_number",
        read_only=True,
    )

    equipment_model_name = serializers.CharField(
        source="equipment.equipment_model.name",
        read_only=True,
    )

    equipment_family_name = serializers.CharField(
        source="equipment.equipment_model.equipment_family.name",
        read_only=True,
        allow_null=True,
    )

    component_name = serializers.CharField(
        source="component.name",
        read_only=True,
    )

    component_code = serializers.CharField(
        source="component.code",
        read_only=True,
    )

    component_type_name = serializers.CharField(
        source="component.component_type.name",
        read_only=True,
    )

    component_category = serializers.CharField(
        source="component.component_type.category",
        read_only=True,
    )

    component_category_name = serializers.CharField(
        source="component.component_type.get_category_display",
        read_only=True,
    )

    component_color = serializers.CharField(
        source="component.color",
        read_only=True,
    )

    component_color_name = serializers.CharField(
        source="component.get_color_display",
        read_only=True,
    )

    manufacturer_code = serializers.CharField(
        source="component.manufacturer_code",
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    removed_disposition_name = serializers.CharField(
        source="get_removed_disposition_display",
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = EquipmentComponentAssignment

        fields = (
            "id",
            "equipment",
            "equipment_internal_code",
            "equipment_serial",
            "equipment_model_name",
            "equipment_family_name",
            "component",
            "component_name",
            "component_code",
            "component_type_name",
            "component_category",
            "component_category_name",
            "component_color",
            "component_color_name",
            "manufacturer_code",
            "serial_number",
            "status",
            "status_name",
            "position",
            "installed_at",
            "installation_meter",
            "removed_at",
            "removal_meter",
            "removed_disposition",
            "removed_disposition_name",
            "reference_type",
            "reference_id",
            "is_active",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class EquipmentComponentAssignmentDetailSerializer(
    serializers.ModelSerializer
):
    equipment_internal_code = serializers.CharField(
        source="equipment.internal_code",
        read_only=True,
    )

    equipment_serial = serializers.CharField(
        source="equipment.serial_number",
        read_only=True,
    )

    equipment_model_name = serializers.CharField(
        source="equipment.equipment_model.name",
        read_only=True,
    )

    equipment_model_code = serializers.CharField(
        source="equipment.equipment_model.code",
        read_only=True,
    )

    equipment_family_name = serializers.CharField(
        source="equipment.equipment_model.equipment_family.name",
        read_only=True,
        allow_null=True,
    )

    equipment_family_code = serializers.CharField(
        source="equipment.equipment_model.equipment_family.code",
        read_only=True,
        allow_null=True,
    )

    component_name = serializers.CharField(
        source="component.name",
        read_only=True,
    )

    component_code = serializers.CharField(
        source="component.code",
        read_only=True,
    )

    component_type_name = serializers.CharField(
        source="component.component_type.name",
        read_only=True,
    )

    component_category = serializers.CharField(
        source="component.component_type.category",
        read_only=True,
    )

    component_category_name = serializers.CharField(
        source="component.component_type.get_category_display",
        read_only=True,
    )

    component_color = serializers.CharField(
        source="component.color",
        read_only=True,
    )

    component_color_name = serializers.CharField(
        source="component.get_color_display",
        read_only=True,
    )

    manufacturer_code = serializers.CharField(
        source="component.manufacturer_code",
        read_only=True,
    )

    alternative_code = serializers.CharField(
        source="component.alternative_code",
        read_only=True,
    )

    expected_life_meter = serializers.IntegerField(
        source="component.expected_life_meter",
        read_only=True,
        allow_null=True,
    )

    expected_life_days = serializers.IntegerField(
        source="component.expected_life_days",
        read_only=True,
        allow_null=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    removed_disposition_name = serializers.CharField(
        source="get_removed_disposition_display",
        read_only=True,
    )

    estimated_usage = serializers.SerializerMethodField()

    estimated_remaining_life = serializers.SerializerMethodField()

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

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = EquipmentComponentAssignment

        fields = (
            "id",
            "equipment",
            "equipment_internal_code",
            "equipment_serial",
            "equipment_model_name",
            "equipment_model_code",
            "equipment_family_name",
            "equipment_family_code",
            "component",
            "component_name",
            "component_code",
            "component_type_name",
            "component_category",
            "component_category_name",
            "component_color",
            "component_color_name",
            "manufacturer_code",
            "alternative_code",
            "expected_life_meter",
            "expected_life_days",
            "serial_number",
            "status",
            "status_name",
            "position",
            "installed_at",
            "installation_meter",
            "removed_at",
            "removal_meter",
            "estimated_usage",
            "estimated_remaining_life",
            "removed_disposition",
            "removed_disposition_name",
            "reference_type",
            "reference_id",
            "installation_notes",
            "removal_notes",
            "is_active",
            "is_archived",
            "archived_at",
            "archived_reason",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_estimated_usage(self, obj):
        if obj.installation_meter is None:
            return None

        current_meter = obj.removal_meter

        if current_meter is None:
            current_meter = obj.equipment.current_total_meter

        if current_meter is None:
            return None

        if current_meter < obj.installation_meter:
            return None

        return current_meter - obj.installation_meter

    def get_estimated_remaining_life(self, obj):
        expected_life = obj.component.expected_life_meter

        if expected_life is None:
            return None

        usage = self.get_estimated_usage(
            obj
        )

        if usage is None:
            return None

        return max(
            expected_life - usage,
            0,
        )


class EquipmentComponentAssignmentCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = EquipmentComponentAssignment

        fields = (
            "equipment",
            "component",
            "serial_number",
            "status",
            "position",
            "installed_at",
            "installation_meter",
            "removed_at",
            "removal_meter",
            "removed_disposition",
            "reference_type",
            "reference_id",
            "installation_notes",
            "removal_notes",
            "is_active",
        )

    def validate_equipment(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un equipo archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar un equipo inactivo."
            )

        return value

    def validate_component(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un componente archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar un componente inactivo."
            )

        return value

    def validate_serial_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_position(self, value):
        return str(
            value or ""
        ).strip().lower()

    def validate_reference_type(self, value):
        return str(
            value or ""
        ).strip().lower()

    def validate_installation_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate_removal_notes(self, value):
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

        component = attrs.get(
            "component",
            getattr(
                instance,
                "component",
                None,
            ),
        )

        serial_number = str(
            attrs.get(
                "serial_number",
                getattr(
                    instance,
                    "serial_number",
                    "",
                ),
            )
            or ""
        ).strip().upper()

        position = str(
            attrs.get(
                "position",
                getattr(
                    instance,
                    "position",
                    "",
                ),
            )
            or ""
        ).strip().lower()

        status = attrs.get(
            "status",
            getattr(
                instance,
                "status",
                EquipmentComponentAssignment.Status.INSTALLED,
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

        installation_meter = attrs.get(
            "installation_meter",
            getattr(
                instance,
                "installation_meter",
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

        removal_meter = attrs.get(
            "removal_meter",
            getattr(
                instance,
                "removal_meter",
                None,
            ),
        )

        removed_disposition = attrs.get(
            "removed_disposition",
            getattr(
                instance,
                "removed_disposition",
                (
                    EquipmentComponentAssignment
                    .RemovedDisposition
                    .NOT_APPLICABLE
                ),
            ),
        )

        reference_type = str(
            attrs.get(
                "reference_type",
                getattr(
                    instance,
                    "reference_type",
                    "",
                ),
            )
            or ""
        ).strip().lower()

        reference_id = attrs.get(
            "reference_id",
            getattr(
                instance,
                "reference_id",
                None,
            ),
        )

        is_active = attrs.get(
            "is_active",
            getattr(
                instance,
                "is_active",
                True,
            ),
        )

        if not equipment:
            raise serializers.ValidationError(
                {
                    "equipment": (
                        "Debes seleccionar un equipo."
                    ),
                }
            )

        if not component:
            raise serializers.ValidationError(
                {
                    "component": (
                        "Debes seleccionar un componente."
                    ),
                }
            )

        equipment_family = (
            equipment
            .equipment_model
            .equipment_family
        )

        if not equipment_family:
            raise serializers.ValidationError(
                {
                    "equipment": (
                        "El modelo del equipo no tiene una "
                        "familia técnica asignada."
                    ),
                }
            )

        compatibility_queryset = (
            ComponentCompatibility.objects.filter(
                component=component,
                equipment_family=equipment_family,
                is_active=True,
                archived_at__isnull=True,
            )
        )

        model_specific_compatibility = (
            compatibility_queryset.filter(
                equipment_model=equipment.equipment_model,
            )
        )

        family_compatibility = (
            compatibility_queryset.filter(
                equipment_model__isnull=True,
            )
        )

        if not (
            model_specific_compatibility.exists()
            or family_compatibility.exists()
        ):
            raise serializers.ValidationError(
                {
                    "component": (
                        "El componente no es compatible con la "
                        "familia o modelo del equipo seleccionado."
                    ),
                }
            )

        if (
            component.requires_individual_serial
            and not serial_number
        ):
            raise serializers.ValidationError(
                {
                    "serial_number": (
                        "Este componente requiere registrar "
                        "un número de serie."
                    ),
                }
            )

        if (
            component.color
            != component.Color.NOT_APPLICABLE
        ):
            if not position:
                position = component.color
                attrs["position"] = position

            elif position != component.color:
                raise serializers.ValidationError(
                    {
                        "position": (
                            "La posición o color no coincide "
                            "con el color del componente."
                        ),
                    }
                )

        if (
            status
            == EquipmentComponentAssignment.Status.INSTALLED
            and not installed_at
        ):
            attrs["installed_at"] = timezone.now()
            installed_at = attrs["installed_at"]

        removed_statuses = (
            EquipmentComponentAssignment.Status.REMOVED,
            EquipmentComponentAssignment.Status.SENT_TO_REPAIR,
            EquipmentComponentAssignment.Status.REPAIRED,
            EquipmentComponentAssignment.Status.RECOVERABLE,
            EquipmentComponentAssignment.Status.FOR_PARTS,
            EquipmentComponentAssignment.Status.DISCARDED,
            (
                EquipmentComponentAssignment
                .Status
                .RETURNED_TO_CUSTOMER
            ),
        )

        if (
            status in removed_statuses
            and not removed_at
        ):
            attrs["removed_at"] = timezone.now()
            removed_at = attrs["removed_at"]

        if (
            removed_at
            and not installed_at
        ):
            raise serializers.ValidationError(
                {
                    "installed_at": (
                        "Debes registrar la fecha de instalación "
                        "antes de registrar el retiro."
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
                        "La fecha de retiro no puede ser anterior "
                        "a la fecha de instalación."
                    ),
                }
            )

        if (
            installation_meter is not None
            and removal_meter is not None
            and removal_meter < installation_meter
        ):
            raise serializers.ValidationError(
                {
                    "removal_meter": (
                        "El contador de retiro no puede ser menor "
                        "que el contador de instalación."
                    ),
                }
            )

        if (
            installation_meter is not None
            and equipment.current_total_meter is not None
            and installation_meter > equipment.current_total_meter
        ):
            raise serializers.ValidationError(
                {
                    "installation_meter": (
                        "El contador de instalación no puede ser "
                        "mayor que el contador actual del equipo."
                    ),
                }
            )

        if (
            removed_at
            and removed_disposition
            == (
                EquipmentComponentAssignment
                .RemovedDisposition
                .NOT_APPLICABLE
            )
        ):
            raise serializers.ValidationError(
                {
                    "removed_disposition": (
                        "Debes indicar el destino del "
                        "componente retirado."
                    ),
                }
            )

        if (
            not removed_at
            and removed_disposition
            != (
                EquipmentComponentAssignment
                .RemovedDisposition
                .NOT_APPLICABLE
            )
        ):
            raise serializers.ValidationError(
                {
                    "removed_disposition": (
                        "No puedes indicar un destino mientras "
                        "el componente continúe instalado."
                    ),
                }
            )

        if reference_id and not reference_type:
            raise serializers.ValidationError(
                {
                    "reference_type": (
                        "Debes indicar el tipo de referencia."
                    ),
                }
            )

        if reference_type and not reference_id:
            raise serializers.ValidationError(
                {
                    "reference_id": (
                        "Debes indicar el ID del registro relacionado."
                    ),
                }
            )

        if (
            status
            == EquipmentComponentAssignment.Status.INSTALLED
            and not is_active
        ):
            attrs["is_active"] = True

        if (
            status
            != EquipmentComponentAssignment.Status.INSTALLED
            and is_active
        ):
            attrs["is_active"] = False

        if (
            status
            == EquipmentComponentAssignment.Status.INSTALLED
        ):
            duplicate_queryset = (
                EquipmentComponentAssignment.objects.filter(
                    equipment=equipment,
                    component=component,
                    position__iexact=position,
                    status=(
                        EquipmentComponentAssignment
                        .Status
                        .INSTALLED
                    ),
                    is_active=True,
                )
            )

            if instance:
                duplicate_queryset = duplicate_queryset.exclude(
                    pk=instance.pk,
                )

            if duplicate_queryset.exists():
                raise serializers.ValidationError(
                    {
                        "component": (
                            "Este componente ya figura instalado "
                            "en la misma posición del equipo."
                        ),
                    }
                )

        if serial_number:
            serial_queryset = (
                EquipmentComponentAssignment.objects.filter(
                    component=component,
                    serial_number__iexact=serial_number,
                )
            )

            if instance:
                serial_queryset = serial_queryset.exclude(
                    pk=instance.pk,
                )

            if serial_queryset.exists():
                raise serializers.ValidationError(
                    {
                        "serial_number": (
                            "Esta serie ya fue registrada para "
                            "el componente seleccionado."
                        ),
                    }
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        assignment = EquipmentComponentAssignment(
            created_by=actor,
            updated_by=actor,
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


class RemoveEquipmentComponentAssignmentSerializer(
    serializers.Serializer
):
    removed_disposition = serializers.ChoiceField(
        choices=(
            EquipmentComponentAssignment
            .RemovedDisposition
            .choices
        ),
    )

    removal_meter = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
    )

    removed_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    removal_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate_removed_disposition(self, value):
        if (
            value
            == (
                EquipmentComponentAssignment
                .RemovedDisposition
                .NOT_APPLICABLE
            )
        ):
            raise serializers.ValidationError(
                "Debes indicar el destino del componente retirado."
            )

        return value

    def validate_removal_notes(self, value):
        return str(
            value or ""
        ).strip()


class ArchiveEquipmentComponentAssignmentSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )