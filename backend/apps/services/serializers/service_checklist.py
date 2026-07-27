# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from rest_framework import serializers

from apps.services.models import (
    ServiceChecklist,
    ServiceChecklistItem,
    ServicePartRequest,
    ServicePartRequestItem,
)


class ServiceChecklistPartItemSerializer(
    serializers.ModelSerializer
):
    urgency_display = serializers.CharField(
        source="get_urgency_display",
        read_only=True,
    )

    source_component_name = serializers.CharField(
        source="source_component.name",
        read_only=True,
        allow_null=True,
    )

    source_component_code = serializers.CharField(
        source="source_component.code",
        read_only=True,
        allow_null=True,
    )

    source_component_color = serializers.CharField(
        source="source_component.color",
        read_only=True,
        allow_null=True,
    )

    source_component_color_display = (
        serializers.CharField(
            source=(
                "source_component."
                "get_color_display"
            ),
            read_only=True,
            allow_null=True,
        )
    )

    source_component_image = (
        serializers.ImageField(
            source="source_component.image",
            read_only=True,
            allow_null=True,
        )
    )

    class Meta:
        model = ServicePartRequestItem

        fields = (
            "id",
            "request",
            "checklist_item",
            "source_component",
            "source_component_name",
            "source_component_code",
            "source_component_color",
            "source_component_color_display",
            "source_component_image",
            "source_component_id_snapshot",
            "parent_component_name",
            "component_code",
            "component_name",
            "manufacturer_code",
            "color",
            "quantity",
            "unit_of_measure",
            "urgency",
            "urgency_display",
            "reason",
            "notes",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class ServiceChecklistItemSerializer(
    serializers.ModelSerializer
):
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    checked_by_display = (
        serializers.SerializerMethodField()
    )

    source_component_display = (
        serializers.SerializerMethodField()
    )

    can_select_subparts = (
        serializers.SerializerMethodField()
    )

    selected_subparts = (
        serializers.SerializerMethodField()
    )

    selected_subparts_count = (
        serializers.SerializerMethodField()
    )

    selected_quantity_total = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = ServiceChecklistItem

        fields = (
            "id",
            "checklist",
            "source_component",
            "source_component_display",
            "source_component_id_snapshot",
            "component_code",
            "component_name",
            "component_color",
            "component_type_name",
            "category",
            "position",
            "status",
            "status_display",
            "is_required",
            "observation",
            "consumable_present",
            "consumable_level_percent",
            "checked_by",
            "checked_by_display",
            "checked_at",
            "display_order",
            "can_select_subparts",
            "selected_subparts",
            "selected_subparts_count",
            "selected_quantity_total",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

        read_only_fields = (
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "source_component_id_snapshot",
            "component_code",
            "component_name",
            "component_color",
            "component_type_name",
            "source_component_display",
            "status_display",
            "checked_by_display",
            "can_select_subparts",
            "selected_subparts",
            "selected_subparts_count",
            "selected_quantity_total",
        )

    def get_checked_by_display(
        self,
        obj,
    ):
        if not obj.checked_by:
            return ""

        return (
            obj.checked_by
            .get_full_name()
            .strip()
            or obj.checked_by
            .get_username()
        )

    def get_source_component_display(
        self,
        obj,
    ):
        if obj.source_component:
            return str(
                obj.source_component
            )

        return obj.component_name

    def get_can_select_subparts(
        self,
        obj,
    ):
        return bool(
            obj.source_component_id
            and obj.status
            == ServiceChecklistItem.Status.FAILED
        )

    def _get_active_part_items(
        self,
        obj,
    ):
        prefetched_items = getattr(
            obj,
            "_prefetched_objects_cache",
            {},
        ).get(
            "part_request_items"
        )

        if prefetched_items is not None:
            return [
                item
                for item in prefetched_items
                if item.archived_at is None
            ]

        return list(
            obj.part_request_items
            .select_related(
                "source_component",
            )
            .filter(
                archived_at__isnull=True,
            )
            .order_by(
                "created_at",
            )
        )

    def get_selected_subparts(
        self,
        obj,
    ):
        items = self._get_active_part_items(
            obj,
        )

        return (
            ServiceChecklistPartItemSerializer(
                items,
                many=True,
                context=self.context,
            ).data
        )

    def get_selected_subparts_count(
        self,
        obj,
    ):
        return len(
            self._get_active_part_items(
                obj,
            )
        )

    def get_selected_quantity_total(
        self,
        obj,
    ):
        total = sum(
            (
                item.quantity
                for item in (
                    self._get_active_part_items(
                        obj,
                    )
                )
            ),
            start=0,
        )

        return str(total)

    def validate_status(
        self,
        value,
    ):
        if value not in dict(
            ServiceChecklistItem
            .Status
            .choices
        ):
            raise serializers.ValidationError(
                "El estado seleccionado no es válido."
            )

        return value

    def validate_consumable_level_percent(
        self,
        value,
    ):
        if value is None:
            return value

        if value < 0 or value > 100:
            raise serializers.ValidationError(
                (
                    "El nivel del consumible debe "
                    "estar entre 0 y 100."
                )
            )

        return value

    def validate(
        self,
        attrs,
    ):
        instance = self.instance

        status_value = attrs.get(
            "status",
            (
                instance.status
                if instance
                else (
                    ServiceChecklistItem
                    .Status
                    .PENDING
                )
            ),
        )

        observation = str(
            attrs.get(
                "observation",
                (
                    instance.observation
                    if instance
                    else ""
                ),
            )
            or ""
        ).strip()

        checked_by = attrs.get(
            "checked_by",
            (
                instance.checked_by
                if instance
                else None
            ),
        )

        checked_at = attrs.get(
            "checked_at",
            (
                instance.checked_at
                if instance
                else None
            ),
        )

        if (
            status_value
            != ServiceChecklistItem.Status.PENDING
            and (
                not checked_by
                or not checked_at
            )
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "Debe registrar técnico "
                        "y fecha de revisión."
                    )
                }
            )

        if (
            status_value
            == ServiceChecklistItem.Status.FAILED
            and not observation
        ):
            raise serializers.ValidationError(
                {
                    "observation": (
                        "Debe describir la falla "
                        "cuando el componente "
                        "requiere cambio."
                    )
                }
            )

        attrs["observation"] = observation

        return attrs

    def update(
        self,
        instance,
        validated_data,
    ):
        request = self.context.get(
            "request"
        )

        user = (
            request.user
            if request
            else None
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


class ServiceChecklistSerializer(
    serializers.ModelSerializer
):
    items = ServiceChecklistItemSerializer(
        many=True,
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    service_order_code = serializers.CharField(
        source="service_order.code",
        read_only=True,
    )

    service_order_status = serializers.CharField(
        source="service_order.status",
        read_only=True,
    )

    service_order_status_display = (
        serializers.CharField(
            source=(
                "service_order."
                "get_status_display"
            ),
            read_only=True,
        )
    )

    total_items = (
        serializers.SerializerMethodField()
    )

    pending_items = (
        serializers.SerializerMethodField()
    )

    failed_items = (
        serializers.SerializerMethodField()
    )

    completed_items = (
        serializers.SerializerMethodField()
    )

    completion_percent = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = ServiceChecklist

        fields = (
            "id",
            "service_order",
            "service_order_code",
            "service_order_status",
            "service_order_status_display",
            "status",
            "status_display",
            "started_by",
            "started_at",
            "completed_by",
            "completed_at",
            "observations",
            "items",
            "total_items",
            "pending_items",
            "failed_items",
            "completed_items",
            "completion_percent",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

        read_only_fields = (
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "service_order_code",
            "service_order_status",
            "service_order_status_display",
            "status_display",
            "items",
            "total_items",
            "pending_items",
            "failed_items",
            "completed_items",
            "completion_percent",
        )

    def _get_active_items(
        self,
        obj,
    ):
        prefetched_items = getattr(
            obj,
            "_prefetched_objects_cache",
            {},
        ).get(
            "items"
        )

        if prefetched_items is not None:
            return [
                item
                for item in prefetched_items
                if item.archived_at is None
            ]

        return list(
            obj.items.filter(
                archived_at__isnull=True,
            )
        )

    def get_total_items(
        self,
        obj,
    ):
        return len(
            self._get_active_items(
                obj,
            )
        )

    def get_pending_items(
        self,
        obj,
    ):
        return sum(
            1
            for item in self._get_active_items(
                obj,
            )
            if (
                item.status
                == ServiceChecklistItem
                .Status
                .PENDING
            )
        )

    def get_failed_items(
        self,
        obj,
    ):
        return sum(
            1
            for item in self._get_active_items(
                obj,
            )
            if (
                item.status
                == ServiceChecklistItem
                .Status
                .FAILED
            )
        )

    def get_completed_items(
        self,
        obj,
    ):
        return sum(
            1
            for item in self._get_active_items(
                obj,
            )
            if (
                item.status
                != ServiceChecklistItem
                .Status
                .PENDING
            )
        )

    def get_completion_percent(
        self,
        obj,
    ):
        total = self.get_total_items(
            obj,
        )

        if total <= 0:
            return 0

        completed = self.get_completed_items(
            obj,
        )

        return round(
            (
                completed
                / total
            )
            * 100,
            2,
        )

    def validate(
        self,
        attrs,
    ):
        instance = self.instance

        status_value = attrs.get(
            "status",
            (
                instance.status
                if instance
                else (
                    ServiceChecklist
                    .Status
                    .PENDING
                )
            ),
        )

        completed_by = attrs.get(
            "completed_by",
            (
                instance.completed_by
                if instance
                else None
            ),
        )

        completed_at = attrs.get(
            "completed_at",
            (
                instance.completed_at
                if instance
                else None
            ),
        )

        if (
            status_value
            == ServiceChecklist.Status.COMPLETED
            and (
                not completed_by
                or not completed_at
            )
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "Debe registrar quién "
                        "y cuándo completó "
                        "el checklist."
                    )
                }
            )

        return attrs

    def update(
        self,
        instance,
        validated_data,
    ):
        request = self.context.get(
            "request"
        )

        user = (
            request.user
            if request
            else None
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


class ServicePartRequestItemSerializer(
    serializers.ModelSerializer
):
    urgency_display = serializers.CharField(
        source="get_urgency_display",
        read_only=True,
    )

    checklist_component_name = (
        serializers.CharField(
            source=(
                "checklist_item."
                "component_name"
            ),
            read_only=True,
            allow_null=True,
        )
    )

    source_component_name = (
        serializers.CharField(
            source="source_component.name",
            read_only=True,
            allow_null=True,
        )
    )

    source_component_image = (
        serializers.ImageField(
            source="source_component.image",
            read_only=True,
            allow_null=True,
        )
    )

    class Meta:
        model = ServicePartRequestItem

        fields = (
            "id",
            "request",
            "checklist_item",
            "checklist_component_name",
            "source_component",
            "source_component_name",
            "source_component_image",
            "source_component_id_snapshot",
            "parent_component_name",
            "component_code",
            "component_name",
            "manufacturer_code",
            "color",
            "quantity",
            "unit_of_measure",
            "urgency",
            "urgency_display",
            "reason",
            "notes",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

        read_only_fields = (
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "source_component_id_snapshot",
            "parent_component_name",
            "component_code",
            "component_name",
            "manufacturer_code",
            "color",
            "unit_of_measure",
            "checklist_component_name",
            "source_component_name",
            "source_component_image",
            "urgency_display",
        )

    def validate_quantity(
        self,
        value,
    ):
        if value is None or value <= 0:
            raise serializers.ValidationError(
                (
                    "La cantidad debe ser "
                    "mayor que cero."
                )
            )

        return value

    def validate_reason(
        self,
        value,
    ):
        reason = str(
            value or "",
        ).strip()

        if not reason:
            raise serializers.ValidationError(
                "Debe indicar el motivo."
            )

        return reason

    def validate(
        self,
        attrs,
    ):
        instance = self.instance

        part_request = attrs.get(
            "request",
            (
                instance.request
                if instance
                else None
            ),
        )

        checklist_item = attrs.get(
            "checklist_item",
            (
                instance.checklist_item
                if instance
                else None
            ),
        )

        source_component = attrs.get(
            "source_component",
            (
                instance.source_component
                if instance
                else None
            ),
        )

        if (
            checklist_item
            and part_request
            and (
                checklist_item
                .checklist
                .service_order_id
                != part_request.service_order_id
            )
        ):
            raise serializers.ValidationError(
                {
                    "checklist_item": (
                        "El ítem del checklist "
                        "pertenece a otra orden "
                        "de servicio."
                    )
                }
            )

        if (
            checklist_item
            and source_component
            and source_component.parent_component_id
            != checklist_item.source_component_id
        ):
            raise serializers.ValidationError(
                {
                    "source_component": (
                        "La subparte no pertenece "
                        "al componente principal "
                        "del checklist."
                    )
                }
            )

        return attrs

    def create(
        self,
        validated_data,
    ):
        request = self.context.get(
            "request"
        )

        user = (
            request.user
            if request
            else None
        )

        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        try:
            return super().create(
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

    def update(
        self,
        instance,
        validated_data,
    ):
        request = self.context.get(
            "request"
        )

        user = (
            request.user
            if request
            else None
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


class ServicePartRequestSerializer(
    serializers.ModelSerializer
):
    items = ServicePartRequestItemSerializer(
        many=True,
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    service_order_code = serializers.CharField(
        source="service_order.code",
        read_only=True,
    )

    requested_by_display = (
        serializers.SerializerMethodField()
    )

    items_count = (
        serializers.SerializerMethodField()
    )

    quantity_total = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = ServicePartRequest

        fields = (
            "id",
            "service_order",
            "service_order_code",
            "status",
            "status_display",
            "requested_by",
            "requested_by_display",
            "requested_at",
            "notes",
            "items",
            "items_count",
            "quantity_total",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        )

        read_only_fields = (
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
            "service_order_code",
            "status_display",
            "requested_by_display",
            "items",
            "items_count",
            "quantity_total",
        )

    def get_requested_by_display(
        self,
        obj,
    ):
        if not obj.requested_by:
            return ""

        return (
            obj.requested_by
            .get_full_name()
            .strip()
            or obj.requested_by
            .get_username()
        )

    def _get_active_items(
        self,
        obj,
    ):
        prefetched_items = getattr(
            obj,
            "_prefetched_objects_cache",
            {},
        ).get(
            "items"
        )

        if prefetched_items is not None:
            return [
                item
                for item in prefetched_items
                if item.archived_at is None
            ]

        return list(
            obj.items.filter(
                archived_at__isnull=True,
            )
        )

    def get_items_count(
        self,
        obj,
    ):
        return len(
            self._get_active_items(
                obj,
            )
        )

    def get_quantity_total(
        self,
        obj,
    ):
        total = sum(
            (
                item.quantity
                for item in (
                    self._get_active_items(
                        obj,
                    )
                )
            ),
            start=0,
        )

        return str(total)

    def update(
        self,
        instance,
        validated_data,
    ):
        request = self.context.get(
            "request"
        )

        user = (
            request.user
            if request
            else None
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