# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers

from apps.equipment.models import (
    ComponentType,
    EquipmentComponent,
)

from ..models import (
    RepairChecklist,
    RepairChecklistItem,
)
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


def build_absolute_file_url(
    serializer,
    file_field,
):
    if not file_field:
        return None

    try:
        file_url = file_field.url
    except (
        AttributeError,
        ValueError,
    ):
        return None

    request = serializer.context.get(
        "request"
    )

    if request:
        return request.build_absolute_uri(
            file_url
        )

    return file_url


class RepairChecklistSubcomponentSerializer(
    serializers.ModelSerializer
):
    component_type_name = serializers.CharField(
        source="component_type.name",
        read_only=True,
    )

    component_category = serializers.CharField(
        source="component_type.category",
        read_only=True,
    )

    component_category_name = serializers.CharField(
        source="component_type.get_category_display",
        read_only=True,
    )

    parent_component_name = serializers.CharField(
        source="parent_component.name",
        read_only=True,
        allow_null=True,
    )

    color_name = serializers.CharField(
        source="get_color_display",
        read_only=True,
    )

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = EquipmentComponent

        fields = (
            "id",
            "parent_component",
            "parent_component_name",
            "component_type",
            "component_type_name",
            "component_category",
            "component_category_name",
            "code",
            "name",
            "manufacturer_code",
            "alternative_code",
            "color",
            "color_name",
            "description",
            "technical_notes",
            "image",
            "image_url",
            "is_active",
            "display_order",
        )

        read_only_fields = fields

    def get_image_url(self, obj):
        return build_absolute_file_url(
            self,
            obj.image,
        )


class RepairChecklistItemComponentMixin:
    def get_component_type(self, obj):
        component = getattr(
            obj,
            "component",
            None,
        )

        if not component:
            return None

        return component.component_type_id

    def get_component_type_name(self, obj):
        component = getattr(
            obj,
            "component",
            None,
        )

        if not component:
            return None

        component_type = getattr(
            component,
            "component_type",
            None,
        )

        if not component_type:
            return None

        return component_type.name

    def get_component_category(self, obj):
        component = getattr(
            obj,
            "component",
            None,
        )

        if not component:
            return None

        component_type = getattr(
            component,
            "component_type",
            None,
        )

        if not component_type:
            return None

        return component_type.category

    def get_component_category_name(self, obj):
        component = getattr(
            obj,
            "component",
            None,
        )

        if not component:
            return None

        component_type = getattr(
            component,
            "component_type",
            None,
        )

        if not component_type:
            return None

        return component_type.get_category_display()

    def get_component_color(self, obj):
        component = getattr(
            obj,
            "component",
            None,
        )

        if not component:
            return None

        return component.color

    def get_component_color_name(self, obj):
        component = getattr(
            obj,
            "component",
            None,
        )

        if not component:
            return None

        return component.get_color_display()

    def get_component_image(self, obj):
        component = getattr(
            obj,
            "component",
            None,
        )

        if not component:
            return None

        return build_absolute_file_url(
            self,
            component.image,
        )

    def get_is_component_item(self, obj):
        return bool(
            getattr(
                obj,
                "component_id",
                None,
            )
        )

    def get_is_technical_unit(self, obj):
        return (
            self.get_component_category(
                obj
            )
            == ComponentType.Category.TECHNICAL_UNIT
        )

    def get_is_accessory(self, obj):
        return (
            self.get_component_category(
                obj
            )
            == ComponentType.Category.ACCESSORY
        )

    def get_commercial_status(self, obj):
        if not self.get_is_technical_unit(
            obj
        ):
            return None

        status_map = {
            RepairChecklistItem.Status.PENDING: (
                "pending"
            ),
            RepairChecklistItem.Status.OK: (
                "new"
            ),
            RepairChecklistItem.Status.OBSERVED: (
                "worn"
            ),
            RepairChecklistItem.Status.FAILED: (
                "requires_change"
            ),
            RepairChecklistItem.Status.NOT_APPLICABLE: (
                "not_applicable"
            ),
        }

        return status_map.get(
            obj.status
        )

    def get_commercial_status_name(self, obj):
        status_names = {
            "pending": "Pendiente",
            "new": "Nuevo",
            "worn": "Desgastado",
            "requires_change": (
                "Requiere cambio"
            ),
            "not_applicable": "No aplica",
        }

        return status_names.get(
            self.get_commercial_status(
                obj
            )
        )

    def get_subcomponents(self, obj):
        component = getattr(
            obj,
            "component",
            None,
        )

        if not component:
            return []

        if not self.get_is_technical_unit(
            obj
        ):
            return []

        subcomponents = (
            component.subcomponents
            .filter(
                archived_at__isnull=True,
                is_active=True,
                component_type__archived_at__isnull=True,
                component_type__is_active=True,
                component_type__category__in=(
                    ComponentType.Category.SUBPART,
                    ComponentType.Category.SPARE_PART,
                ),
            )
            .select_related(
                "component_type",
                "parent_component",
            )
            .order_by(
                "display_order",
                "name",
            )
        )

        return (
            RepairChecklistSubcomponentSerializer(
                subcomponents,
                many=True,
                context=self.context,
            ).data
        )

    def get_subcomponent_count(self, obj):
        component = getattr(
            obj,
            "component",
            None,
        )

        if not component:
            return 0

        if not self.get_is_technical_unit(
            obj
        ):
            return 0

        return (
            component.subcomponents
            .filter(
                archived_at__isnull=True,
                is_active=True,
                component_type__archived_at__isnull=True,
                component_type__is_active=True,
                component_type__category__in=(
                    ComponentType.Category.SUBPART,
                    ComponentType.Category.SPARE_PART,
                ),
            )
            .count()
        )

    def get_selected_subcomponents(self, obj):
        selected_subcomponents = (
            obj.selected_subcomponents
            .filter(
                archived_at__isnull=True,
                is_active=True,
            )
            .select_related(
                "component_type",
                "parent_component",
            )
            .order_by(
                "display_order",
                "name",
            )
        )

        return (
            RepairChecklistSubcomponentSerializer(
                selected_subcomponents,
                many=True,
                context=self.context,
            ).data
        )

    def get_selected_subcomponent_ids(self, obj):
        return [
            str(component_id)
            for component_id
            in obj.selected_subcomponents.filter(
                archived_at__isnull=True,
                is_active=True,
            ).values_list(
                "id",
                flat=True,
            )
        ]


class RepairChecklistItemListSerializer(
    RepairChecklistItemComponentMixin,
    serializers.ModelSerializer,
):
    component_name = serializers.CharField(
        source="component.name",
        read_only=True,
        allow_null=True,
    )

    component_code = serializers.CharField(
        source="component.code",
        read_only=True,
        allow_null=True,
    )

    component_type = serializers.SerializerMethodField()

    component_type_name = serializers.SerializerMethodField()

    component_category = serializers.SerializerMethodField()

    component_category_name = serializers.SerializerMethodField()

    component_color = serializers.SerializerMethodField()

    component_color_name = serializers.SerializerMethodField()

    component_image = serializers.SerializerMethodField()

    is_component_item = serializers.SerializerMethodField()

    is_technical_unit = serializers.SerializerMethodField()

    is_accessory = serializers.SerializerMethodField()

    commercial_status = serializers.SerializerMethodField()

    commercial_status_name = serializers.SerializerMethodField()

    subcomponents = serializers.SerializerMethodField()

    subcomponent_count = serializers.SerializerMethodField()

    selected_subcomponents = serializers.SerializerMethodField()

    selected_subcomponent_ids = serializers.SerializerMethodField()

    category_name = serializers.CharField(
        source="get_category_display",
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    checked_by_name = serializers.CharField(
        source="checked_by.full_name",
        read_only=True,
        allow_null=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairChecklistItem

        fields = (
            "id",
            "checklist",
            "component",
            "component_name",
            "component_code",
            "component_type",
            "component_type_name",
            "component_category",
            "component_category_name",
            "component_color",
            "component_color_name",
            "component_image",
            "is_component_item",
            "is_technical_unit",
            "is_accessory",
            "commercial_status",
            "commercial_status_name",
            "subcomponents",
            "subcomponent_count",
            "selected_subcomponents",
            "selected_subcomponent_ids",
            "code",
            "name",
            "category",
            "category_name",
            "status",
            "status_name",
            "is_required",
            "requires_photo",
            "requires_observation",
            "observation",
            "checked_by",
            "checked_by_name",
            "checked_at",
            "display_order",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class RepairChecklistItemDetailSerializer(
    RepairChecklistItemComponentMixin,
    serializers.ModelSerializer,
):
    repair_id = serializers.UUIDField(
        source="checklist.repair_id",
        read_only=True,
    )

    repair_code = serializers.CharField(
        source="checklist.repair.code",
        read_only=True,
    )

    component_name = serializers.CharField(
        source="component.name",
        read_only=True,
        allow_null=True,
    )

    component_code = serializers.CharField(
        source="component.code",
        read_only=True,
        allow_null=True,
    )

    component_type = serializers.SerializerMethodField()

    component_type_name = serializers.SerializerMethodField()

    component_category = serializers.SerializerMethodField()

    component_category_name = serializers.SerializerMethodField()

    component_color = serializers.SerializerMethodField()

    component_color_name = serializers.SerializerMethodField()

    component_image = serializers.SerializerMethodField()

    is_component_item = serializers.SerializerMethodField()

    is_technical_unit = serializers.SerializerMethodField()

    is_accessory = serializers.SerializerMethodField()

    commercial_status = serializers.SerializerMethodField()

    commercial_status_name = serializers.SerializerMethodField()

    subcomponents = serializers.SerializerMethodField()

    subcomponent_count = serializers.SerializerMethodField()

    selected_subcomponents = serializers.SerializerMethodField()

    selected_subcomponent_ids = serializers.SerializerMethodField()

    category_name = serializers.CharField(
        source="get_category_display",
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    checked_by_name = serializers.CharField(
        source="checked_by.full_name",
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
        model = RepairChecklistItem

        fields = (
            "id",
            "checklist",
            "repair_id",
            "repair_code",
            "component",
            "component_name",
            "component_code",
            "component_type",
            "component_type_name",
            "component_category",
            "component_category_name",
            "component_color",
            "component_color_name",
            "component_image",
            "is_component_item",
            "is_technical_unit",
            "is_accessory",
            "commercial_status",
            "commercial_status_name",
            "subcomponents",
            "subcomponent_count",
            "selected_subcomponents",
            "selected_subcomponent_ids",
            "code",
            "name",
            "category",
            "category_name",
            "description",
            "instructions",
            "status",
            "status_name",
            "is_required",
            "requires_photo",
            "requires_observation",
            "observation",
            "checked_by",
            "checked_by_name",
            "checked_at",
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


class RepairChecklistListSerializer(
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

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    started_by_name = serializers.CharField(
        source="started_by.full_name",
        read_only=True,
        allow_null=True,
    )

    completed_by_name = serializers.CharField(
        source="completed_by.full_name",
        read_only=True,
        allow_null=True,
    )

    item_count = serializers.SerializerMethodField()

    required_item_count = serializers.SerializerMethodField()

    completed_item_count = serializers.SerializerMethodField()

    pending_item_count = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairChecklist

        fields = (
            "id",
            "repair",
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "name",
            "status",
            "status_name",
            "is_main_checklist",
            "started_by",
            "started_by_name",
            "started_at",
            "completed_by",
            "completed_by_name",
            "completed_at",
            "item_count",
            "required_item_count",
            "completed_item_count",
            "pending_item_count",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_item_count(self, obj):
        return obj.items.filter(
            archived_at__isnull=True,
        ).count()

    def get_required_item_count(self, obj):
        return obj.items.filter(
            archived_at__isnull=True,
            is_required=True,
        ).count()

    def get_completed_item_count(self, obj):
        return obj.items.filter(
            archived_at__isnull=True,
            status__in=[
                RepairChecklistItem.Status.OK,
                RepairChecklistItem.Status.OBSERVED,
                RepairChecklistItem.Status.NOT_APPLICABLE,
            ],
        ).count()

    def get_pending_item_count(self, obj):
        return obj.items.filter(
            archived_at__isnull=True,
            status__in=[
                RepairChecklistItem.Status.PENDING,
                RepairChecklistItem.Status.FAILED,
            ],
        ).count()


class RepairChecklistDetailSerializer(
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

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    started_by_name = serializers.CharField(
        source="started_by.full_name",
        read_only=True,
        allow_null=True,
    )

    completed_by_name = serializers.CharField(
        source="completed_by.full_name",
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

    items = RepairChecklistItemListSerializer(
        many=True,
        read_only=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = RepairChecklist

        fields = (
            "id",
            "repair",
            "repair_code",
            "equipment_id",
            "equipment_serial_number",
            "name",
            "description",
            "status",
            "status_name",
            "is_main_checklist",
            "started_by",
            "started_by_name",
            "started_at",
            "completed_by",
            "completed_by_name",
            "completed_at",
            "observations",
            "items",
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


class RepairChecklistCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = RepairChecklist

        fields = (
            "repair",
            "name",
            "description",
            "is_main_checklist",
            "observations",
        )

    def validate_repair(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes crear una lista para una "
                "reparación archivada."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes crear una lista para una "
                "reparación inactiva."
            )

        return value

    def validate_name(self, value):
        name = str(
            value or ""
        ).strip()

        if not name:
            raise serializers.ValidationError(
                "El nombre de la lista es obligatorio."
            )

        return name

    def validate_description(self, value):
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

        is_main_checklist = attrs.get(
            "is_main_checklist",
            getattr(
                instance,
                "is_main_checklist",
                True,
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

        if is_main_checklist:
            queryset = RepairChecklist.objects.filter(
                repair=repair,
                is_main_checklist=True,
                archived_at__isnull=True,
            )

            if instance:
                queryset = queryset.exclude(
                    pk=instance.pk,
                )

            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "is_main_checklist": (
                            "La reparación ya tiene una "
                            "lista principal."
                        )
                    }
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        checklist = RepairChecklist(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            checklist.full_clean()
            checklist.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return checklist

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


class RepairChecklistItemCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = RepairChecklistItem

        fields = (
            "checklist",
            "component",
            "code",
            "name",
            "category",
            "description",
            "instructions",
            "is_required",
            "requires_photo",
            "requires_observation",
            "display_order",
        )

    def validate_checklist(self, value):
        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes agregar puntos a una "
                "lista archivada."
            )

        if (
            value.status
            == RepairChecklist.Status.COMPLETED
        ):
            raise serializers.ValidationError(
                "No puedes modificar una lista completada."
            )

        if not value.repair.is_active:
            raise serializers.ValidationError(
                "La reparación ya no está activa."
            )

        return value

    def validate_component(self, value):
        if value is None:
            return value

        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un componente archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar un componente inactivo."
            )

        return value

    def validate_code(self, value):
        code = str(
            value or ""
        ).strip().upper()

        if not code:
            raise serializers.ValidationError(
                "El código del punto es obligatorio."
            )

        return code

    def validate_name(self, value):
        name = str(
            value or ""
        ).strip()

        if not name:
            raise serializers.ValidationError(
                "El nombre del punto es obligatorio."
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

    def validate(self, attrs):
        instance = self.instance

        checklist = attrs.get(
            "checklist",
            getattr(
                instance,
                "checklist",
                None,
            ),
        )

        code = attrs.get(
            "code",
            getattr(
                instance,
                "code",
                "",
            ),
        )

        category = attrs.get(
            "category",
            getattr(
                instance,
                "category",
                RepairChecklistItem.Category.GENERAL,
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

        if checklist and code:
            queryset = RepairChecklistItem.objects.filter(
                checklist=checklist,
                code__iexact=code,
            )

            if instance:
                queryset = queryset.exclude(
                    pk=instance.pk,
                )

            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "code": (
                            "Ya existe un punto con este código "
                            "en la lista."
                        )
                    }
                )

        component_categories = (
            RepairChecklistItem.Category.COMPONENT,
            RepairChecklistItem.Category.ACCESSORY,
        )

        if (
            category in component_categories
            and not component
        ):
            raise serializers.ValidationError(
                {
                    "component": (
                        "Debes seleccionar un componente."
                    )
                }
            )

        if (
            component
            and category not in component_categories
        ):
            raise serializers.ValidationError(
                {
                    "category": (
                        "Los puntos vinculados a componentes "
                        "deben usar la categoría componente "
                        "o accesorio."
                    )
                }
            )

        if component:
            component_type = getattr(
                component,
                "component_type",
                None,
            )

            if not component_type:
                raise serializers.ValidationError(
                    {
                        "component": (
                            "El componente no tiene un tipo "
                            "configurado."
                        )
                    }
                )

            if (
                component.parent_component_id
                and component_type.category
                in (
                    ComponentType.Category.SUBPART,
                    ComponentType.Category.SPARE_PART,
                )
            ):
                raise serializers.ValidationError(
                    {
                        "component": (
                            "Las subpartes no deben crearse "
                            "como puntos principales del checklist."
                        )
                    }
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = get_authenticated_user(
            self
        )

        item = RepairChecklistItem(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            item.full_clean()
            item.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return item

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


class StartRepairChecklistSerializer(
    serializers.Serializer
):
    observations = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate(self, attrs):
        checklist = self.context.get(
            "checklist"
        )

        if not checklist:
            raise serializers.ValidationError(
                "No se encontró la lista de revisión."
            )

        if checklist.is_archived:
            raise serializers.ValidationError(
                "La lista se encuentra archivada."
            )

        if (
            checklist.status
            != RepairChecklist.Status.PENDING
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "Solo una lista pendiente puede iniciarse."
                    )
                }
            )

        return attrs


class CompleteRepairChecklistSerializer(
    serializers.Serializer
):
    observations = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    def validate(self, attrs):
        checklist = self.context.get(
            "checklist"
        )

        if not checklist:
            raise serializers.ValidationError(
                "No se encontró la lista de revisión."
            )

        if checklist.is_archived:
            raise serializers.ValidationError(
                "La lista se encuentra archivada."
            )

        pending_items = (
            checklist.items.filter(
                archived_at__isnull=True,
                is_required=True,
            )
            .exclude(
                status__in=[
                    RepairChecklistItem.Status.OK,
                    RepairChecklistItem.Status.NOT_APPLICABLE,
                ]
            )
        )

        if pending_items.exists():
            raise serializers.ValidationError(
                {
                    "status": (
                        "Existen puntos obligatorios pendientes, "
                        "observados o con falla."
                    )
                }
            )

        return attrs


class ReviewRepairChecklistItemSerializer(
    serializers.Serializer
):
    status = serializers.ChoiceField(
        choices=RepairChecklistItem.Status.choices,
    )

    observation = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )

    selected_subcomponents = (
        serializers.PrimaryKeyRelatedField(
            many=True,
            required=False,
            queryset=EquipmentComponent.objects.filter(
                archived_at__isnull=True,
                is_active=True,
            ),
        )
    )

    def validate(self, attrs):
        item = self.context.get(
            "item"
        )

        if not item:
            raise serializers.ValidationError(
                "No se encontró el punto de revisión."
            )

        if item.is_archived:
            raise serializers.ValidationError(
                "El punto de revisión está archivado."
            )

        if (
            item.checklist.status
            == RepairChecklist.Status.COMPLETED
        ):
            raise serializers.ValidationError(
                "La lista ya se encuentra completada."
            )

        status = attrs["status"]

        if (
            status
            == RepairChecklistItem.Status.PENDING
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "La revisión debe registrar "
                        "un resultado."
                    )
                }
            )

        observation = str(
            attrs.get(
                "observation",
                "",
            )
            or ""
        ).strip()

        selected_subcomponents = attrs.get(
            "selected_subcomponents",
            [],
        )

        component = getattr(
            item,
            "component",
            None,
        )

        component_type = getattr(
            component,
            "component_type",
            None,
        )

        is_technical_unit = bool(
            component_type
            and component_type.category
            == ComponentType.Category.TECHNICAL_UNIT
        )

        if (
            selected_subcomponents
            and not is_technical_unit
        ):
            raise serializers.ValidationError(
                {
                    "selected_subcomponents": (
                        "Solo las unidades técnicas pueden "
                        "tener subpartes seleccionadas."
                    )
                }
            )

        invalid_subcomponents = []

        if component:
            for subcomponent in selected_subcomponents:
                if (
                    subcomponent.parent_component_id
                    != component.id
                ):
                    invalid_subcomponents.append(
                        subcomponent.name
                    )

                    continue

                subcomponent_type = getattr(
                    subcomponent,
                    "component_type",
                    None,
                )

                if (
                    not subcomponent_type
                    or subcomponent_type.category
                    not in (
                        ComponentType.Category.SUBPART,
                        ComponentType.Category.SPARE_PART,
                    )
                ):
                    invalid_subcomponents.append(
                        subcomponent.name
                    )

        if invalid_subcomponents:
            raise serializers.ValidationError(
                {
                    "selected_subcomponents": (
                        "Las siguientes subpartes no pertenecen "
                        "a la unidad seleccionada: "
                        + ", ".join(
                            invalid_subcomponents
                        )
                    )
                }
            )

        if (
            is_technical_unit
            and status
            == RepairChecklistItem.Status.FAILED
            and not selected_subcomponents
        ):
            raise serializers.ValidationError(
                {
                    "selected_subcomponents": (
                        "Selecciona al menos una subparte "
                        "que requiera cambio."
                    )
                }
            )

        if (
            status
            != RepairChecklistItem.Status.FAILED
            and selected_subcomponents
        ):
            raise serializers.ValidationError(
                {
                    "selected_subcomponents": (
                        "Las subpartes solo se seleccionan "
                        "cuando la unidad requiere cambio."
                    )
                }
            )

        if (
            status
            == RepairChecklistItem.Status.FAILED
            and not observation
        ):
            raise serializers.ValidationError(
                {
                    "observation": (
                        "Debes describir la falla encontrada."
                    )
                }
            )

        if (
            status
            == RepairChecklistItem.Status.NOT_APPLICABLE
            and item.is_required
            and not observation
        ):
            raise serializers.ValidationError(
                {
                    "observation": (
                        "Debes indicar por qué el punto "
                        "no aplica."
                    )
                }
            )

        if (
            item.requires_observation
            and status in (
                RepairChecklistItem.Status.OBSERVED,
                RepairChecklistItem.Status.FAILED,
            )
            and not observation
        ):
            raise serializers.ValidationError(
                {
                    "observation": (
                        "Debes registrar una observación."
                    )
                }
            )

        attrs["observation"] = observation
        attrs["selected_subcomponents"] = (
            selected_subcomponents
        )

        return attrs


class ArchiveRepairChecklistSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )


class ArchiveRepairChecklistItemSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )