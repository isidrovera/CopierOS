# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.equipment.models import Equipment
from apps.partners.models import Partner
from apps.rentals.models import (
    RentalEquipment,
    RentalWarehouse,
)


class RentalEquipmentSerializer(serializers.ModelSerializer):
    """
    Serializer principal para las máquinas administradas
    por ANDES.
    """

    equipment_display = serializers.SerializerMethodField()
    equipment_serial_number = serializers.SerializerMethodField()
    equipment_internal_code = serializers.SerializerMethodField()
    equipment_brand_name = serializers.SerializerMethodField()
    equipment_model_name = serializers.SerializerMethodField()

    purpose_display = serializers.CharField(
        source="get_purpose_display",
        read_only=True,
    )

    acquisition_source_display = serializers.CharField(
        source="get_acquisition_source_display",
        read_only=True,
    )

    operational_status_display = serializers.CharField(
        source="get_operational_status_display",
        read_only=True,
    )

    supplier_name = serializers.SerializerMethodField()
    owner_customer_name = serializers.SerializerMethodField()
    warehouse_name = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    archived_by_name = serializers.SerializerMethodField()

    class Meta:
        model = RentalEquipment
        fields = [
            "id",
            "equipment",
            "equipment_display",
            "equipment_serial_number",
            "equipment_internal_code",
            "equipment_brand_name",
            "equipment_model_name",
            "purpose",
            "purpose_display",
            "acquisition_source",
            "acquisition_source_display",
            "supplier",
            "supplier_name",
            "owner_customer",
            "owner_customer_name",
            "warehouse",
            "warehouse_name",
            "warehouse_location",
            "operational_status",
            "operational_status_display",
            "entry_date",
            "acquisition_document",
            "acquisition_reference",
            "is_available_for_rental",
            "notes",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "archived_at",
            "archived_by",
            "archived_by_name",
            "archived_reason",
            "is_archived",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "archived_at",
            "archived_by",
            "archived_reason",
        ]

    def get_equipment_display(self, obj):
        return str(obj.equipment)

    def get_equipment_serial_number(self, obj):
        return getattr(
            obj.equipment,
            "serial_number",
            "",
        )

    def get_equipment_internal_code(self, obj):
        return getattr(
            obj.equipment,
            "internal_code",
            "",
        )

    def get_equipment_brand_name(self, obj):
        equipment_model = getattr(
            obj.equipment,
            "equipment_model",
            None,
        )

        brand = getattr(
            equipment_model,
            "brand",
            None,
        )

        return getattr(
            brand,
            "name",
            "",
        )

    def get_equipment_model_name(self, obj):
        equipment_model = getattr(
            obj.equipment,
            "equipment_model",
            None,
        )

        return getattr(
            equipment_model,
            "name",
            "",
        )

    def get_supplier_name(self, obj):
        if not obj.supplier:
            return ""

        return str(obj.supplier)

    def get_owner_customer_name(self, obj):
        if not obj.owner_customer:
            return ""

        return str(obj.owner_customer)

    def get_warehouse_name(self, obj):
        if not obj.warehouse:
            return ""

        return obj.warehouse.name

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return ""

        return (
            obj.created_by.get_full_name()
            or obj.created_by.username
        )

    def get_updated_by_name(self, obj):
        if not obj.updated_by:
            return ""

        return (
            obj.updated_by.get_full_name()
            or obj.updated_by.username
        )

    def get_archived_by_name(self, obj):
        if not obj.archived_by:
            return ""

        return (
            obj.archived_by.get_full_name()
            or obj.archived_by.username
        )

    def validate_equipment(self, value):
        queryset = RentalEquipment.objects.filter(
            equipment=value,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Este equipo ya está registrado en ANDES."
            )

        return value

    def validate_supplier(self, value):
        if value and value.archived_at:
            raise serializers.ValidationError(
                "El proveedor seleccionado está archivado."
            )

        return value

    def validate_owner_customer(self, value):
        if value and value.archived_at:
            raise serializers.ValidationError(
                "El cliente propietario está archivado."
            )

        return value

    def validate_warehouse(self, value):
        if not value:
            return value

        if value.archived_at:
            raise serializers.ValidationError(
                "El almacén seleccionado está archivado."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "El almacén seleccionado está inactivo."
            )

        if not value.allows_entries:
            raise serializers.ValidationError(
                "El almacén seleccionado no permite ingresos."
            )

        return value

    def validate(self, attrs):
        purpose = attrs.get(
            "purpose",
            getattr(
                self.instance,
                "purpose",
                RentalEquipment.EquipmentPurpose.RENTAL,
            ),
        )

        acquisition_source = attrs.get(
            "acquisition_source",
            getattr(
                self.instance,
                "acquisition_source",
                None,
            ),
        )

        supplier = attrs.get(
            "supplier",
            getattr(
                self.instance,
                "supplier",
                None,
            ),
        )

        owner_customer = attrs.get(
            "owner_customer",
            getattr(
                self.instance,
                "owner_customer",
                None,
            ),
        )

        warehouse = attrs.get(
            "warehouse",
            getattr(
                self.instance,
                "warehouse",
                None,
            ),
        )

        operational_status = attrs.get(
            "operational_status",
            getattr(
                self.instance,
                "operational_status",
                RentalEquipment.OperationalStatus.RECEIVED,
            ),
        )

        is_available_for_rental = attrs.get(
            "is_available_for_rental",
            getattr(
                self.instance,
                "is_available_for_rental",
                False,
            ),
        )

        if (
            purpose
            == RentalEquipment.EquipmentPurpose.CUSTOMER_SERVICE
        ):
            if not owner_customer:
                raise serializers.ValidationError(
                    {
                        "owner_customer": (
                            "Debe indicar el cliente propietario."
                        ),
                    }
                )

            if warehouse:
                raise serializers.ValidationError(
                    {
                        "warehouse": (
                            "Los equipos de clientes externos no "
                            "deben ingresar al almacén de alquiler."
                        ),
                    }
                )

            if is_available_for_rental:
                raise serializers.ValidationError(
                    {
                        "is_available_for_rental": (
                            "Un equipo de cliente externo no puede "
                            "estar disponible para alquiler."
                        ),
                    }
                )

        if (
            purpose
            == RentalEquipment.EquipmentPurpose.RENTAL
            and owner_customer
        ):
            raise serializers.ValidationError(
                {
                    "owner_customer": (
                        "Un equipo propio para alquiler no debe "
                        "tener cliente propietario."
                    ),
                }
            )

        if (
            acquisition_source
            == RentalEquipment.AcquisitionSource.CUSTOMER_OWNED
            and not owner_customer
        ):
            raise serializers.ValidationError(
                {
                    "owner_customer": (
                        "Debe indicar el propietario del equipo."
                    ),
                }
            )

        supplier_sources = [
            RentalEquipment.AcquisitionSource.CORAPSAC,
            RentalEquipment.AcquisitionSource.EXTERNAL_SUPPLIER,
        ]

        if (
            acquisition_source in supplier_sources
            and not supplier
        ):
            raise serializers.ValidationError(
                {
                    "supplier": (
                        "Debe indicar el proveedor del equipo."
                    ),
                }
            )

        warehouse_required_statuses = [
            RentalEquipment.OperationalStatus.RECEIVED,
            RentalEquipment.OperationalStatus.IN_WAREHOUSE,
            RentalEquipment.OperationalStatus.PENDING_PREPARATION,
            RentalEquipment.OperationalStatus.IN_PREPARATION,
            RentalEquipment.OperationalStatus.READY_FOR_RENTAL,
            RentalEquipment.OperationalStatus.RETURNED_TO_WAREHOUSE,
            RentalEquipment.OperationalStatus.WITH_PROBLEMS,
            RentalEquipment.OperationalStatus.FOR_PARTS,
        ]

        if (
            purpose
            == RentalEquipment.EquipmentPurpose.RENTAL
            and operational_status in warehouse_required_statuses
            and not warehouse
        ):
            raise serializers.ValidationError(
                {
                    "warehouse": (
                        "Debe indicar el almacén actual."
                    ),
                }
            )

        if is_available_for_rental:
            if (
                purpose
                != RentalEquipment.EquipmentPurpose.RENTAL
            ):
                raise serializers.ValidationError(
                    {
                        "is_available_for_rental": (
                            "Solo las máquinas propias de ANDES "
                            "pueden estar disponibles."
                        ),
                    }
                )

            if (
                operational_status
                != RentalEquipment.OperationalStatus.READY_FOR_RENTAL
            ):
                raise serializers.ValidationError(
                    {
                        "is_available_for_rental": (
                            "El equipo debe estar listo para alquiler."
                        ),
                    }
                )

        unavailable_statuses = [
            RentalEquipment.OperationalStatus.RENTED,
            RentalEquipment.OperationalStatus.REMOVAL_PENDING,
            RentalEquipment.OperationalStatus.WITH_PROBLEMS,
            RentalEquipment.OperationalStatus.FOR_PARTS,
            RentalEquipment.OperationalStatus.OUT_OF_SERVICE,
        ]

        if operational_status in unavailable_statuses:
            attrs["is_available_for_rental"] = False

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")

        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["created_by"] = user
        validated_data["updated_by"] = user

        return super().create(
            validated_data
        )

    def update(self, instance, validated_data):
        request = self.context.get("request")

        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        validated_data["updated_by"] = user

        return super().update(
            instance,
            validated_data,
        )


class RentalEquipmentListSerializer(
    RentalEquipmentSerializer
):
    """
    Serializer compacto para listados de la flota de ANDES.
    """

    class Meta(RentalEquipmentSerializer.Meta):
        fields = [
            "id",
            "equipment",
            "equipment_display",
            "equipment_serial_number",
            "equipment_internal_code",
            "equipment_brand_name",
            "equipment_model_name",
            "purpose",
            "purpose_display",
            "acquisition_source",
            "acquisition_source_display",
            "supplier",
            "supplier_name",
            "owner_customer",
            "owner_customer_name",
            "warehouse",
            "warehouse_name",
            "warehouse_location",
            "operational_status",
            "operational_status_display",
            "entry_date",
            "is_available_for_rental",
            "archived_at",
            "is_archived",
        ]