# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from rest_framework import serializers

from apps.services.domain import build_order_snapshot
from apps.services.models import ServiceOrder


class ServiceOrderSerializer(serializers.ModelSerializer):
    equipment_display = serializers.SerializerMethodField()
    technician_display = serializers.SerializerMethodField()

    service_origin_display = serializers.CharField(
        source="get_service_origin_display",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    priority_display = serializers.CharField(
        source="get_priority_display",
        read_only=True,
    )

    service_type_display = serializers.CharField(
        source="get_service_type_display",
        read_only=True,
    )

    result_display = serializers.CharField(
        source="get_result_display",
        read_only=True,
    )

    class Meta:
        model = ServiceOrder
        fields = "__all__"

        read_only_fields = (
            "code",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "assigned_at",
            "accepted_at",
            "route_started_at",
            "arrived_at",
            "service_started_at",
            "technician_completed_at",
            "closed_at",
            "equipment_internal_code",
            "equipment_serial_number",
            "equipment_brand_name",
            "equipment_model_name",
            "equipment_family_name",
            "contract_reference",
            "rental_assignment_reference",
        )

    def get_equipment_display(self, obj):
        return str(obj.equipment)

    def get_technician_display(self, obj):
        if not obj.assigned_technician_id:
            return ""

        technician = obj.assigned_technician
        full_name = technician.get_full_name().strip()

        return (
            full_name
            or technician.get_username()
        )

    def _get_instance_value(
        self,
        field_name,
        default=None,
    ):
        if not self.instance:
            return default

        return getattr(
            self.instance,
            field_name,
            default,
        )

    def _apply_snapshot(
        self,
        attrs,
        snapshot,
        overwrite=False,
    ):
        for field_name, value in snapshot.items():
            current_value = attrs.get(
                field_name,
                self._get_instance_value(
                    field_name,
                    None,
                ),
            )

            should_apply = (
                overwrite
                or current_value in (
                    None,
                    "",
                )
            )

            if should_apply:
                attrs[field_name] = value

        return attrs

    def _validate_rental_origin(
        self,
        equipment,
        snapshot,
    ):
        if snapshot:
            return

        raise serializers.ValidationError(
            {
                "equipment": (
                    "La máquina seleccionada no tiene una "
                    "asignación vigente de alquiler instalada "
                    "o activa."
                )
            }
        )

    def _validate_external_origin(
        self,
        attrs,
        snapshot,
    ):
        customer_name = str(
            attrs.get(
                "customer_name",
                self._get_instance_value(
                    "customer_name",
                    "",
                ),
            )
            or ""
        ).strip()

        address = str(
            attrs.get(
                "address",
                self._get_instance_value(
                    "address",
                    "",
                ),
            )
            or ""
        ).strip()

        if not customer_name:
            raise serializers.ValidationError(
                {
                    "customer_name": (
                        "La máquina externa no tiene un "
                        "cliente asignado. Selecciona o registra "
                        "el cliente de la atención."
                    )
                }
            )

        if not address:
            raise serializers.ValidationError(
                {
                    "address": (
                        "La máquina externa no tiene una "
                        "dirección asignada. Selecciona una sede "
                        "o registra la dirección de atención."
                    )
                }
            )

    def validate_equipment(self, equipment):
        if equipment.archived_at:
            raise serializers.ValidationError(
                "La máquina seleccionada está archivada."
            )

        if not getattr(
            equipment,
            "is_active",
            True,
        ):
            raise serializers.ValidationError(
                "La máquina seleccionada está inactiva."
            )

        return equipment

    def validate_assigned_technician(
        self,
        technician,
    ):
        if not technician:
            return technician

        if not technician.is_active:
            raise serializers.ValidationError(
                "El técnico seleccionado está inactivo."
            )

        if getattr(
            technician,
            "archived_at",
            None,
        ):
            raise serializers.ValidationError(
                "El técnico seleccionado está archivado."
            )

        return technician

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

        service_origin = attrs.get(
            "service_origin",
            getattr(
                instance,
                "service_origin",
                ServiceOrder.ServiceOrigin.RENTAL,
            ),
        )

        if not equipment:
            raise serializers.ValidationError(
                {
                    "equipment": (
                        "Debe seleccionar una máquina."
                    )
                }
            )

        if service_origin not in dict(
            ServiceOrder.ServiceOrigin.choices
        ):
            raise serializers.ValidationError(
                {
                    "service_origin": (
                        "El origen de la atención "
                        "no es válido."
                    )
                }
            )

        equipment_changed = bool(
            instance
            and equipment.pk
            != instance.equipment_id
        )

        origin_changed = bool(
            instance
            and service_origin
            != instance.service_origin
        )

        should_reload_snapshot = (
            not instance
            or equipment_changed
            or origin_changed
        )

        snapshot = build_order_snapshot(
            equipment=equipment,
            service_origin=service_origin,
        )

        if (
            service_origin
            == ServiceOrder.ServiceOrigin.RENTAL
        ):
            self._validate_rental_origin(
                equipment,
                snapshot,
            )

            attrs = self._apply_snapshot(
                attrs=attrs,
                snapshot=snapshot,
                overwrite=should_reload_snapshot,
            )

        elif (
            service_origin
            == ServiceOrder.ServiceOrigin.EXTERNAL
        ):
            attrs = self._apply_snapshot(
                attrs=attrs,
                snapshot=snapshot,
                overwrite=should_reload_snapshot,
            )

            self._validate_external_origin(
                attrs=attrs,
                snapshot=snapshot,
            )

        reported_problem = str(
            attrs.get(
                "reported_problem",
                getattr(
                    instance,
                    "reported_problem",
                    "",
                ),
            )
            or ""
        ).strip()

        if not reported_problem:
            raise serializers.ValidationError(
                {
                    "reported_problem": (
                        "Debe registrar el problema reportado."
                    )
                }
            )

        assigned_technician = attrs.get(
            "assigned_technician",
            getattr(
                instance,
                "assigned_technician",
                None,
            ),
        )

        status_value = attrs.get(
            "status",
            getattr(
                instance,
                "status",
                ServiceOrder.Status.DRAFT,
            ),
        )

        requires_technician = (
            status_value
            not in {
                ServiceOrder.Status.DRAFT,
                ServiceOrder.Status.PENDING_ASSIGNMENT,
                ServiceOrder.Status.CANCELLED,
            }
        )

        if (
            requires_technician
            and not assigned_technician
        ):
            raise serializers.ValidationError(
                {
                    "assigned_technician": (
                        "El estado seleccionado requiere "
                        "un técnico asignado."
                    )
                }
            )

        if (
            service_origin
            == ServiceOrder.ServiceOrigin.EXTERNAL
        ):
            attrs["contract_reference"] = ""
            attrs["rental_assignment_reference"] = ""

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")

        user = (
            request.user
            if request
            else None
        )

        validated_data.pop(
            "code",
            None,
        )

        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        try:
            return super().create(
                validated_data
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                getattr(
                    exc,
                    "message_dict",
                    {
                        "detail": exc.messages,
                    },
                )
            ) from exc

    def update(
        self,
        instance,
        validated_data,
    ):
        request = self.context.get("request")

        user = (
            request.user
            if request
            else None
        )

        validated_data.pop(
            "code",
            None,
        )

        validated_data["updated_by"] = user

        try:
            return super().update(
                instance,
                validated_data,
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                getattr(
                    exc,
                    "message_dict",
                    {
                        "detail": exc.messages,
                    },
                )
            ) from exc


class ServiceOrderListSerializer(
    ServiceOrderSerializer
):
    class Meta(
        ServiceOrderSerializer.Meta
    ):
        fields = (
            "id",
            "code",
            "service_origin",
            "service_origin_display",
            "equipment",
            "equipment_display",
            "equipment_serial_number",
            "equipment_internal_code",
            "equipment_brand_name",
            "equipment_model_name",
            "customer_name",
            "customer_trade_name",
            "branch_name",
            "address",
            "contact_name",
            "contact_phone",
            "contract_reference",
            "assigned_technician",
            "technician_display",
            "status",
            "status_display",
            "priority",
            "priority_display",
            "service_type",
            "service_type_display",
            "result",
            "result_display",
            "requested_at",
            "scheduled_at",
            "requires_return_visit",
            "archived_at",
        )