# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from ..models import (
    Equipment,
    EquipmentModel,
)
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class EquipmentListSerializer(
    serializers.ModelSerializer
):
    """
    Serializer reducido para listar máquinas físicas.
    """

    model_name = serializers.CharField(
        source="equipment_model.name",
        read_only=True,
    )

    model_full_name = serializers.CharField(
        source="equipment_model.__str__",
        read_only=True,
    )

    brand = serializers.UUIDField(
        source="equipment_model.brand_id",
        read_only=True,
    )

    brand_name = serializers.CharField(
        source="equipment_model.brand.name",
        read_only=True,
    )

    equipment_type = serializers.UUIDField(
        source="equipment_model.equipment_type_id",
        read_only=True,
    )

    equipment_type_name = serializers.CharField(
        source="equipment_model.equipment_type.name",
        read_only=True,
    )

    color_mode = serializers.CharField(
        source="equipment_model.color_mode",
        read_only=True,
    )

    color_mode_name = serializers.CharField(
        source="equipment_model.get_color_mode_display",
        read_only=True,
    )

    technical_status_name = serializers.CharField(
        source="get_technical_status_display",
        read_only=True,
    )

    commercial_status_name = serializers.CharField(
        source="get_commercial_status_display",
        read_only=True,
    )

    ownership_type_name = serializers.CharField(
        source="get_ownership_type_display",
        read_only=True,
    )

    physical_condition_name = serializers.CharField(
        source="get_physical_condition_display",
        read_only=True,
    )

    supplier_name = serializers.CharField(
        source="supplier.display_name",
        read_only=True,
        allow_null=True,
    )

    customer_name = serializers.CharField(
        source="customer.display_name",
        read_only=True,
        allow_null=True,
    )

    customer_branch_name = serializers.CharField(
        source="customer_branch.name",
        read_only=True,
        allow_null=True,
    )

    advisor_name = serializers.CharField(
        source="advisor.full_name",
        read_only=True,
        allow_null=True,
    )

    import_batch_code = serializers.CharField(
        source="import_batch.code",
        read_only=True,
        allow_null=True,
    )

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = Equipment

        fields = (
            "id",
            "internal_code",
            "serial_number",
            "equipment_model",
            "model_name",
            "model_full_name",
            "brand",
            "brand_name",
            "equipment_type",
            "equipment_type_name",
            "color_mode",
            "color_mode_name",
            "import_batch",
            "import_batch_code",
            "ownership_type",
            "ownership_type_name",
            "physical_condition",
            "physical_condition_name",
            "supplier",
            "supplier_name",
            "customer",
            "customer_name",
            "customer_branch",
            "customer_branch_name",
            "advisor",
            "advisor_name",
            "technical_status",
            "technical_status_name",
            "commercial_status",
            "commercial_status_name",
            "is_available",
            "warehouse_location",
            "position_reference",
            "current_total_meter",
            "current_black_meter",
            "current_color_meter",
            "current_scan_meter",
            "last_meter_date",
            "purchase_currency",
            "purchase_price",
            "sale_currency",
            "sale_price",
            "unloading_date",
            "main_photo",
            "is_active",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class EquipmentDetailSerializer(
    serializers.ModelSerializer
):
    """
    Serializer completo de una máquina física.
    """

    model_name = serializers.CharField(
        source="equipment_model.name",
        read_only=True,
    )

    model_code = serializers.CharField(
        source="equipment_model.code",
        read_only=True,
    )

    model_full_name = serializers.CharField(
        source="equipment_model.__str__",
        read_only=True,
    )

    brand = serializers.UUIDField(
        source="equipment_model.brand_id",
        read_only=True,
    )

    brand_name = serializers.CharField(
        source="equipment_model.brand.name",
        read_only=True,
    )

    brand_code = serializers.CharField(
        source="equipment_model.brand.code",
        read_only=True,
    )

    equipment_type = serializers.UUIDField(
        source="equipment_model.equipment_type_id",
        read_only=True,
    )

    equipment_type_name = serializers.CharField(
        source="equipment_model.equipment_type.name",
        read_only=True,
    )

    equipment_type_code = serializers.CharField(
        source="equipment_model.equipment_type.code",
        read_only=True,
    )

    model_family = serializers.CharField(
        source="equipment_model.family",
        read_only=True,
    )

    model_color_mode = serializers.CharField(
        source="equipment_model.color_mode",
        read_only=True,
    )

    model_color_mode_name = serializers.CharField(
        source="equipment_model.get_color_mode_display",
        read_only=True,
    )

    model_technology = serializers.CharField(
        source="equipment_model.technology",
        read_only=True,
    )

    model_technology_name = serializers.CharField(
        source="equipment_model.get_technology_display",
        read_only=True,
    )

    model_maximum_paper_size = serializers.CharField(
        source="equipment_model.maximum_paper_size",
        read_only=True,
    )

    model_maximum_paper_size_name = serializers.CharField(
        source="equipment_model.get_maximum_paper_size_display",
        read_only=True,
    )

    ownership_type_name = serializers.CharField(
        source="get_ownership_type_display",
        read_only=True,
    )

    physical_condition_name = serializers.CharField(
        source="get_physical_condition_display",
        read_only=True,
    )

    technical_status_name = serializers.CharField(
        source="get_technical_status_display",
        read_only=True,
    )

    commercial_status_name = serializers.CharField(
        source="get_commercial_status_display",
        read_only=True,
    )

    purchase_currency_name = serializers.CharField(
        source="get_purchase_currency_display",
        read_only=True,
    )

    sale_currency_name = serializers.CharField(
        source="get_sale_currency_display",
        read_only=True,
    )

    last_meter_source_name = serializers.CharField(
        source="get_last_meter_source_display",
        read_only=True,
    )

    import_batch_code = serializers.CharField(
        source="import_batch.code",
        read_only=True,
        allow_null=True,
    )

    supplier_name = serializers.CharField(
        source="supplier.display_name",
        read_only=True,
        allow_null=True,
    )

    supplier_document_number = serializers.CharField(
        source="supplier.document_number",
        read_only=True,
        allow_null=True,
    )

    owner_partner_name = serializers.CharField(
        source="owner_partner.display_name",
        read_only=True,
        allow_null=True,
    )

    customer_name = serializers.CharField(
        source="customer.display_name",
        read_only=True,
        allow_null=True,
    )

    customer_document_number = serializers.CharField(
        source="customer.document_number",
        read_only=True,
        allow_null=True,
    )

    customer_branch_name = serializers.CharField(
        source="customer_branch.name",
        read_only=True,
        allow_null=True,
    )

    advisor_name = serializers.CharField(
        source="advisor.full_name",
        read_only=True,
        allow_null=True,
    )

    unloading_registered_by_name = serializers.CharField(
        source="unloading_registered_by.full_name",
        read_only=True,
        allow_null=True,
    )

    movements_count = serializers.SerializerMethodField()

    meter_readings_count = serializers.SerializerMethodField()

    documents_count = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
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

    class Meta:
        model = Equipment

        fields = (
            "id",
            "internal_code",
            "serial_number",
            "equipment_model",
            "model_name",
            "model_code",
            "model_full_name",
            "brand",
            "brand_name",
            "brand_code",
            "equipment_type",
            "equipment_type_name",
            "equipment_type_code",
            "model_family",
            "model_color_mode",
            "model_color_mode_name",
            "model_technology",
            "model_technology_name",
            "model_maximum_paper_size",
            "model_maximum_paper_size_name",
            "import_batch",
            "import_batch_code",
            "ownership_type",
            "ownership_type_name",
            "physical_condition",
            "physical_condition_name",
            "supplier",
            "supplier_name",
            "supplier_document_number",
            "owner_partner",
            "owner_partner_name",
            "customer",
            "customer_name",
            "customer_document_number",
            "customer_branch",
            "customer_branch_name",
            "advisor",
            "advisor_name",
            "import_reference",
            "purchase_invoice_number",
            "purchase_invoice_date",
            "purchase_date",
            "unloading_date",
            "unloading_registered_by",
            "unloading_registered_by_name",
            "purchase_currency",
            "purchase_currency_name",
            "purchase_price",
            "allocated_import_cost",
            "total_acquisition_cost",
            "sale_currency",
            "sale_currency_name",
            "sale_price",
            "sale_invoice_number",
            "sale_invoice_date",
            "reservation_date",
            "reservation_expiration_date",
            "sale_date",
            "delivery_date",
            "technical_status",
            "technical_status_name",
            "technical_status_reason",
            "commercial_status",
            "commercial_status_name",
            "commercial_status_reason",
            "is_available",
            "warehouse_location",
            "position_reference",
            "initial_total_meter",
            "initial_black_meter",
            "initial_color_meter",
            "initial_scan_meter",
            "current_total_meter",
            "current_black_meter",
            "current_color_meter",
            "current_scan_meter",
            "last_meter_date",
            "last_meter_source",
            "last_meter_source_name",
            "hostname",
            "ip_address",
            "mac_address",
            "asset_number",
            "firmware_version",
            "main_photo",
            "accessories_description",
            "unloading_observations",
            "technical_notes",
            "commercial_notes",
            "notes",
            "is_active",
            "movements_count",
            "meter_readings_count",
            "documents_count",
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

        read_only_fields = (
            "id",
            "model_name",
            "model_code",
            "model_full_name",
            "brand",
            "brand_name",
            "brand_code",
            "equipment_type",
            "equipment_type_name",
            "equipment_type_code",
            "model_family",
            "model_color_mode",
            "model_color_mode_name",
            "model_technology",
            "model_technology_name",
            "model_maximum_paper_size",
            "model_maximum_paper_size_name",
            "ownership_type_name",
            "physical_condition_name",
            "technical_status_name",
            "commercial_status_name",
            "purchase_currency_name",
            "sale_currency_name",
            "last_meter_source_name",
            "import_batch_code",
            "supplier_name",
            "supplier_document_number",
            "owner_partner_name",
            "customer_name",
            "customer_document_number",
            "customer_branch_name",
            "advisor_name",
            "unloading_registered_by_name",
            "total_acquisition_cost",
            "is_available",
            "movements_count",
            "meter_readings_count",
            "documents_count",
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

    def get_movements_count(self, obj):
        return obj.movements.filter(
            archived_at__isnull=True,
        ).count()

    def get_meter_readings_count(self, obj):
        return obj.meter_readings.filter(
            archived_at__isnull=True,
        ).count()

    def get_documents_count(self, obj):
        return obj.documents.filter(
            archived_at__isnull=True,
        ).count()


class EquipmentCreateUpdateSerializer(
    serializers.ModelSerializer
):
    """
    Creación y modificación de máquinas físicas.
    """

    class Meta:
        model = Equipment

        fields = (
            "internal_code",
            "serial_number",
            "equipment_model",
            "import_batch",
            "ownership_type",
            "physical_condition",
            "supplier",
            "owner_partner",
            "customer",
            "customer_branch",
            "advisor",
            "import_reference",
            "purchase_invoice_number",
            "purchase_invoice_date",
            "purchase_date",
            "unloading_date",
            "unloading_registered_by",
            "purchase_currency",
            "purchase_price",
            "allocated_import_cost",
            "sale_currency",
            "sale_price",
            "sale_invoice_number",
            "sale_invoice_date",
            "reservation_date",
            "reservation_expiration_date",
            "sale_date",
            "delivery_date",
            "technical_status",
            "technical_status_reason",
            "commercial_status",
            "commercial_status_reason",
            "warehouse_location",
            "position_reference",
            "initial_total_meter",
            "initial_black_meter",
            "initial_color_meter",
            "initial_scan_meter",
            "current_total_meter",
            "current_black_meter",
            "current_color_meter",
            "current_scan_meter",
            "last_meter_date",
            "last_meter_source",
            "hostname",
            "ip_address",
            "mac_address",
            "asset_number",
            "firmware_version",
            "main_photo",
            "accessories_description",
            "unloading_observations",
            "technical_notes",
            "commercial_notes",
            "notes",
            "is_active",
        )

        read_only_fields = (
            "internal_code",
        )

    def validate_serial_number(self, value):
        """
        Normaliza y valida el número de serie.
        """

        serial_number = str(
            value or ""
        ).strip().upper()

        if not serial_number:
            raise serializers.ValidationError(
                "El número de serie es obligatorio."
            )

        queryset = Equipment.objects.filter(
            serial_number__iexact=serial_number,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un equipo con este número de serie."
            )

        return serial_number

    def validate_equipment_model(self, value):
        """
        Impide utilizar modelos archivados o inactivos.
        """

        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un modelo archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar un modelo inactivo."
            )

        return value

    def validate_import_batch(self, value):
        """
        Valida el lote cuando fue seleccionado.
        """

        if value is None:
            return value

        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un lote archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar un lote inactivo."
            )

        if value.status == value.Status.CANCELLED:
            raise serializers.ValidationError(
                "No puedes registrar equipos en un lote cancelado."
            )

        return value

    def validate_supplier(self, value):
        """
        Valida el proveedor cuando fue seleccionado.
        """

        if value is None:
            return value

        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un proveedor archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar un proveedor inactivo."
            )

        if not value.is_supplier:
            raise serializers.ValidationError(
                "El tercero seleccionado no está marcado como proveedor."
            )

        return value

    def validate_customer(self, value):
        """
        Valida el cliente cuando fue seleccionado.
        """

        if value is None:
            return value

        if value.archived_at is not None:
            raise serializers.ValidationError(
                "No puedes utilizar un cliente archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "No puedes utilizar un cliente inactivo."
            )

        customer_roles = (
            value.is_rental_customer
            or value.is_sales_customer
            or value.is_service_customer
            or value.is_distributor
        )

        if not customer_roles:
            raise serializers.ValidationError(
                "El tercero seleccionado no está habilitado como cliente."
            )

        return value

    def validate_import_reference(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_purchase_invoice_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_sale_invoice_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_technical_status_reason(self, value):
        return str(
            value or ""
        ).strip()

    def validate_commercial_status_reason(self, value):
        return str(
            value or ""
        ).strip()

    def validate_warehouse_location(self, value):
        return str(
            value or ""
        ).strip()

    def validate_position_reference(self, value):
        return str(
            value or ""
        ).strip()

    def validate_hostname(self, value):
        return str(
            value or ""
        ).strip()

    def validate_mac_address(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_asset_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_firmware_version(self, value):
        return str(
            value or ""
        ).strip()

    def validate_accessories_description(self, value):
        return str(
            value or ""
        ).strip()

    def validate_unloading_observations(self, value):
        return str(
            value or ""
        ).strip()

    def validate_technical_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate_commercial_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate(self, attrs):
        """
        Valida relaciones, estados, fechas, contadores
        y condiciones comerciales del equipo.
        """

        instance = self.instance

        values = {}

        if instance:
            for field in self.Meta.fields:
                values[field] = getattr(
                    instance,
                    field,
                    None,
                )

        values.update(attrs)

        equipment_model = values.get(
            "equipment_model"
        )

        import_batch = values.get(
            "import_batch"
        )

        supplier = values.get(
            "supplier"
        )

        ownership_type = values.get(
            "ownership_type"
        )

        owner_partner = values.get(
            "owner_partner"
        )

        customer = values.get(
            "customer"
        )

        customer_branch = values.get(
            "customer_branch"
        )

        technical_status = values.get(
            "technical_status"
        )

        technical_status_reason = str(
            values.get(
                "technical_status_reason",
                "",
            )
            or ""
        ).strip()

        commercial_status = values.get(
            "commercial_status"
        )

        reservation_date = values.get(
            "reservation_date"
        )

        reservation_expiration_date = values.get(
            "reservation_expiration_date"
        )

        sale_date = values.get(
            "sale_date"
        )

        delivery_date = values.get(
            "delivery_date"
        )

        purchase_invoice_date = values.get(
            "purchase_invoice_date"
        )

        purchase_date = values.get(
            "purchase_date"
        )

        sale_invoice_date = values.get(
            "sale_invoice_date"
        )

        initial_total_meter = int(
            values.get(
                "initial_total_meter",
                0,
            )
            or 0
        )

        initial_black_meter = int(
            values.get(
                "initial_black_meter",
                0,
            )
            or 0
        )

        initial_color_meter = int(
            values.get(
                "initial_color_meter",
                0,
            )
            or 0
        )

        initial_scan_meter = int(
            values.get(
                "initial_scan_meter",
                0,
            )
            or 0
        )

        current_total_meter = int(
            values.get(
                "current_total_meter",
                0,
            )
            or 0
        )

        current_black_meter = int(
            values.get(
                "current_black_meter",
                0,
            )
            or 0
        )

        current_color_meter = int(
            values.get(
                "current_color_meter",
                0,
            )
            or 0
        )

        current_scan_meter = int(
            values.get(
                "current_scan_meter",
                0,
            )
            or 0
        )

        if not equipment_model:
            raise serializers.ValidationError(
                {
                    "equipment_model": (
                        "Debes seleccionar el modelo del equipo."
                    )
                }
            )

        if (
            import_batch
            and supplier
            and import_batch.supplier_id != supplier.id
        ):
            raise serializers.ValidationError(
                {
                    "supplier": (
                        "El proveedor seleccionado no coincide "
                        "con el proveedor del lote."
                    )
                }
            )

        if (
            import_batch
            and not supplier
        ):
            attrs["supplier"] = import_batch.supplier

        external_ownership_types = {
            Equipment.OwnershipType.CUSTOMER,
            Equipment.OwnershipType.SUPPLIER,
            Equipment.OwnershipType.THIRD_PARTY,
            Equipment.OwnershipType.OTHER,
        }

        if (
            ownership_type in external_ownership_types
            and not owner_partner
        ):
            raise serializers.ValidationError(
                {
                    "owner_partner": (
                        "Debes indicar el propietario cuando "
                        "el equipo no pertenece a la empresa."
                    )
                }
            )

        if (
            ownership_type == Equipment.OwnershipType.OWN
            and owner_partner
        ):
            raise serializers.ValidationError(
                {
                    "owner_partner": (
                        "Un equipo propio no debe tener "
                        "propietario externo."
                    )
                }
            )

        if (
            customer_branch
            and not customer
        ):
            raise serializers.ValidationError(
                {
                    "customer": (
                        "Debes seleccionar el cliente antes "
                        "de seleccionar una sucursal."
                    )
                }
            )

        if (
            customer_branch
            and customer
            and customer_branch.partner_id != customer.id
        ):
            raise serializers.ValidationError(
                {
                    "customer_branch": (
                        "La sucursal seleccionada no pertenece "
                        "al cliente indicado."
                    )
                }
            )

        warehouse_statuses = {
            Equipment.CommercialStatus.WAREHOUSE,
            Equipment.CommercialStatus.RETURNED,
        }

        if (
            customer
            and commercial_status in warehouse_statuses
        ):
            commercial_status = (
                Equipment.CommercialStatus.RESERVED
            )
            attrs["commercial_status"] = commercial_status

            if not reservation_date:
                reservation_date = timezone.now()
                attrs["reservation_date"] = reservation_date

        if (
            not customer
            and commercial_status
            == Equipment.CommercialStatus.RESERVED
        ):
            commercial_status = (
                Equipment.CommercialStatus.WAREHOUSE
            )
            attrs["commercial_status"] = commercial_status
            attrs["customer_branch"] = None
            attrs["advisor"] = None
            attrs["reservation_date"] = None
            attrs["reservation_expiration_date"] = None

            customer_branch = None
            reservation_date = None
            reservation_expiration_date = None

        statuses_requiring_customer = {
            Equipment.CommercialStatus.RESERVED,
            Equipment.CommercialStatus.SOLD,
            Equipment.CommercialStatus.DELIVERY_PREPARATION,
            Equipment.CommercialStatus.IN_TRANSIT,
            Equipment.CommercialStatus.DELIVERED,
            Equipment.CommercialStatus.CONTRACT_ASSIGNED,
            Equipment.CommercialStatus.INSTALLED,
            Equipment.CommercialStatus.TEMPORARY_LOAN,
            Equipment.CommercialStatus.DEMONSTRATION,
            Equipment.CommercialStatus.REPLACEMENT,
        }

        if (
            commercial_status in statuses_requiring_customer
            and not customer
        ):
            raise serializers.ValidationError(
                {
                    "customer": (
                        "El estado comercial seleccionado "
                        "requiere un cliente."
                    )
                }
            )

        if (
            commercial_status
            == Equipment.CommercialStatus.RESERVED
            and not reservation_date
        ):
            raise serializers.ValidationError(
                {
                    "reservation_date": (
                        "Una máquina separada debe registrar "
                        "la fecha de separación."
                    )
                }
            )

        if (
            reservation_expiration_date
            and not reservation_date
        ):
            raise serializers.ValidationError(
                {
                    "reservation_date": (
                        "Debes registrar la fecha de separación "
                        "antes de indicar su vencimiento."
                    )
                }
            )

        if (
            reservation_date
            and reservation_expiration_date
            and reservation_expiration_date < reservation_date
        ):
            raise serializers.ValidationError(
                {
                    "reservation_expiration_date": (
                        "El vencimiento de la separación no puede "
                        "ser anterior a la fecha de separación."
                    )
                }
            )

        sold_statuses = {
            Equipment.CommercialStatus.SOLD,
            Equipment.CommercialStatus.DELIVERY_PREPARATION,
            Equipment.CommercialStatus.IN_TRANSIT,
            Equipment.CommercialStatus.DELIVERED,
        }

        if (
            commercial_status in sold_statuses
            and not sale_date
        ):
            raise serializers.ValidationError(
                {
                    "sale_date": (
                        "Una máquina vendida o en proceso de entrega "
                        "debe registrar la fecha de venta."
                    )
                }
            )

        if (
            commercial_status
            == Equipment.CommercialStatus.DELIVERED
            and not delivery_date
        ):
            raise serializers.ValidationError(
                {
                    "delivery_date": (
                        "Una máquina entregada debe registrar "
                        "la fecha real de entrega."
                    )
                }
            )

        if (
            purchase_invoice_date
            and purchase_date
            and purchase_invoice_date > purchase_date
        ):
            raise serializers.ValidationError(
                {
                    "purchase_invoice_date": (
                        "La fecha de factura de compra no puede "
                        "ser posterior a la fecha de compra."
                    )
                }
            )

        if (
            sale_invoice_date
            and sale_date
            and sale_invoice_date < sale_date
        ):
            raise serializers.ValidationError(
                {
                    "sale_invoice_date": (
                        "La fecha de factura de venta no puede "
                        "ser anterior a la fecha de venta."
                    )
                }
            )

        problem_statuses = {
            Equipment.TechnicalStatus.WITH_PROBLEMS,
            Equipment.TechnicalStatus.FOR_PARTS,
        }

        if (
            technical_status in problem_statuses
            and not technical_status_reason
        ):
            raise serializers.ValidationError(
                {
                    "technical_status_reason": (
                        "Debes indicar el motivo cuando el equipo "
                        "tiene problemas o se destina a partes."
                    )
                }
            )

        if current_total_meter < initial_total_meter:
            raise serializers.ValidationError(
                {
                    "current_total_meter": (
                        "El contador total actual no puede ser menor "
                        "que el contador total de ingreso."
                    )
                }
            )

        if current_black_meter < initial_black_meter:
            raise serializers.ValidationError(
                {
                    "current_black_meter": (
                        "El contador B/N actual no puede ser menor "
                        "que el contador B/N de ingreso."
                    )
                }
            )

        if current_color_meter < initial_color_meter:
            raise serializers.ValidationError(
                {
                    "current_color_meter": (
                        "El contador color actual no puede ser menor "
                        "que el contador color de ingreso."
                    )
                }
            )

        if current_scan_meter < initial_scan_meter:
            raise serializers.ValidationError(
                {
                    "current_scan_meter": (
                        "El contador de escaneo actual no puede ser "
                        "menor que el contador de ingreso."
                    )
                }
            )

        if equipment_model:
            if (
                equipment_model.color_mode
                == EquipmentModel.ColorMode.MONOCHROME
                and (
                    initial_color_meter > 0
                    or current_color_meter > 0
                )
            ):
                raise serializers.ValidationError(
                    {
                        "current_color_meter": (
                            "Un equipo blanco y negro no puede "
                            "registrar contador color."
                        )
                    }
                )

            if (
                not equipment_model.has_scan_meter
                and (
                    initial_scan_meter > 0
                    or current_scan_meter > 0
                )
            ):
                raise serializers.ValidationError(
                    {
                        "current_scan_meter": (
                            "El modelo seleccionado no utiliza "
                            "contador de escaneo."
                        )
                    }
                )

            if (
                not equipment_model.has_color_meter
                and (
                    initial_color_meter > 0
                    or current_color_meter > 0
                )
            ):
                raise serializers.ValidationError(
                    {
                        "current_color_meter": (
                            "El modelo seleccionado no utiliza "
                            "contador color."
                        )
                    }
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """
        Crea la máquina registrando auditoría.

        Cuando los contadores actuales no fueron enviados,
        se copian desde los contadores iniciales.
        """

        actor = get_authenticated_user(
            self
        )

        if (
            "current_total_meter"
            not in validated_data
        ):
            validated_data["current_total_meter"] = (
                validated_data.get(
                    "initial_total_meter",
                    0,
                )
            )

        if (
            "current_black_meter"
            not in validated_data
        ):
            validated_data["current_black_meter"] = (
                validated_data.get(
                    "initial_black_meter",
                    0,
                )
            )

        if (
            "current_color_meter"
            not in validated_data
        ):
            validated_data["current_color_meter"] = (
                validated_data.get(
                    "initial_color_meter",
                    0,
                )
            )

        if (
            "current_scan_meter"
            not in validated_data
        ):
            validated_data["current_scan_meter"] = (
                validated_data.get(
                    "initial_scan_meter",
                    0,
                )
            )

        if (
            not validated_data.get(
                "unloading_registered_by"
            )
            and actor
            and validated_data.get(
                "unloading_date"
            )
        ):
            validated_data[
                "unloading_registered_by"
            ] = actor

        if not validated_data.get(
            "internal_code"
        ):
            validated_data[
                "internal_code"
            ] = Equipment.generate_internal_code()

        equipment = Equipment(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            equipment.full_clean()
            equipment.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return equipment

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        """
        Actualiza la máquina registrando auditoría.
        """

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


class ArchiveEquipmentSerializer(
    serializers.Serializer
):
    """
    Datos requeridos para archivar un equipo.
    """

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )


class ChangeEquipmentTechnicalStatusSerializer(
    serializers.Serializer
):
    """
    Datos para cambiar el estado técnico de una máquina.
    """

    technical_status = serializers.ChoiceField(
        choices=Equipment.TechnicalStatus.choices,
    )

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=3000,
    )


class ChangeEquipmentCommercialStatusSerializer(
    serializers.Serializer
):
    """
    Datos para cambiar el estado comercial o logístico.
    """

    commercial_status = serializers.ChoiceField(
        choices=Equipment.CommercialStatus.choices,
    )

    customer = serializers.UUIDField(
        required=False,
        allow_null=True,
    )

    customer_branch = serializers.UUIDField(
        required=False,
        allow_null=True,
    )

    advisor = serializers.UUIDField(
        required=False,
        allow_null=True,
    )

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=3000,
    )


class RegisterInitialEquipmentMetersSerializer(
    serializers.Serializer
):
    """
    Datos para registrar o corregir los contadores iniciales
    de una máquina durante la descarga.
    """

    initial_total_meter = serializers.IntegerField(
        required=False,
        min_value=0,
        default=0,
    )

    initial_black_meter = serializers.IntegerField(
        required=False,
        min_value=0,
        default=0,
    )

    initial_color_meter = serializers.IntegerField(
        required=False,
        min_value=0,
        default=0,
    )

    initial_scan_meter = serializers.IntegerField(
        required=False,
        min_value=0,
        default=0,
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=3000,
    )