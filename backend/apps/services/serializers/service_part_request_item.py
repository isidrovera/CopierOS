# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.services.models import ServicePartRequestItem

from .workflow_common import FullCleanModelSerializerMixin


class ServicePartRequestItemListSerializer(
    serializers.ModelSerializer
):
    display_name = serializers.CharField(read_only=True)
    item_type_display = serializers.CharField(
        source="get_item_type_display",
        read_only=True,
    )
    urgency_display = serializers.CharField(
        source="get_urgency_display",
        read_only=True,
    )
    management_decision_display = serializers.CharField(
        source="get_management_decision_display",
        read_only=True,
    )
    supply_method_display = serializers.CharField(
        source="get_supply_method_display",
        read_only=True,
    )
    request_code = serializers.CharField(
        source="request.code",
        read_only=True,
    )

    class Meta:
        model = ServicePartRequestItem
        fields = (
            "id",
            "request",
            "request_code",
            "checklist_item",
            "source_component",
            "display_name",
            "item_type",
            "item_type_display",
            "component_code",
            "component_name",
            "manufacturer_code",
            "color",
            "custom_name",
            "custom_code",
            "requested_quantity",
            "approved_quantity",
            "stock_confirmed_quantity",
            "delivered_quantity",
            "unit_of_measure",
            "urgency",
            "urgency_display",
            "management_decision",
            "management_decision_display",
            "supply_method",
            "supply_method_display",
            "reason",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ServicePartRequestItemSerializer(
    FullCleanModelSerializerMixin,
    serializers.ModelSerializer,
):
    display_name = serializers.CharField(read_only=True)
    item_type_display = serializers.CharField(
        source="get_item_type_display",
        read_only=True,
    )
    urgency_display = serializers.CharField(
        source="get_urgency_display",
        read_only=True,
    )
    management_decision_display = serializers.CharField(
        source="get_management_decision_display",
        read_only=True,
    )
    supply_method_display = serializers.CharField(
        source="get_supply_method_display",
        read_only=True,
    )
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServicePartRequestItem
        fields = "__all__"
        read_only_fields = (
            "source_component_id_snapshot",
            "component_code",
            "component_name",
            "manufacturer_code",
            "color",
            "parent_component_name",
            "created_by",
            "updated_by",
            "archived_by",
            "archived_at",
            "archived_reason",
        )

    def validate(self, attrs):
        request_object = attrs.get(
            "request",
            getattr(self.instance, "request", None),
        )
        checklist_item = attrs.get(
            "checklist_item",
            getattr(self.instance, "checklist_item", None),
        )

        if (
            request_object
            and checklist_item
            and checklist_item.checklist.service_order_id
            != request_object.service_order_id
        ):
            raise serializers.ValidationError(
                {
                    "checklist_item": (
                        "El ítem del checklist pertenece "
                        "a otra orden de servicio."
                    )
                }
            )

        return attrs


class ServicePartRequestItemDecisionSerializer(
    serializers.Serializer
):
    management_decision = serializers.ChoiceField(
        choices=ServicePartRequestItem.ManagementDecision.choices,
    )
    approved_quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    management_notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class ServicePartRequestItemSupplySerializer(
    serializers.Serializer
):
    supply_method = serializers.ChoiceField(
        choices=ServicePartRequestItem.SupplyMethod.choices,
    )
    stock_confirmed_quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    stock_notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )
