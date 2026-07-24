# -*- coding: utf-8 -*-
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers

from ..models import ImportBatch
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
)


class ImportBatchListSerializer(
    serializers.ModelSerializer
):
    """
    Serializer reducido para listar importaciones
    y lotes de equipos.
    """

    supplier_name = serializers.CharField(
        source="supplier.display_name",
        read_only=True,
    )

    purchase_type_name = serializers.CharField(
        source="get_purchase_type_display",
        read_only=True,
    )

    currency_name = serializers.CharField(
        source="get_currency_display",
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    registered_equipment_count = serializers.SerializerMethodField()

    pending_equipment_count = serializers.SerializerMethodField()

    is_archived = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = ImportBatch

        fields = (
            "id",
            "code",
            "purchase_type",
            "purchase_type_name",
            "supplier",
            "supplier_name",
            "import_number",
            "purchase_order_number",
            "invoice_number",
            "invoice_date",
            "purchase_date",
            "estimated_arrival_date",
            "arrival_date",
            "container_number",
            "warehouse_location",
            "expected_quantity",
            "declared_quantity",
            "registered_equipment_count",
            "pending_equipment_count",
            "currency",
            "currency_name",
            "equipment_subtotal",
            "total_cost",
            "status",
            "status_name",
            "is_active",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_registered_equipment_count(self, obj):
        """
        Cuenta los equipos no archivados registrados
        dentro del lote.
        """

        return obj.equipment_units.filter(
            archived_at__isnull=True,
        ).count()

    def get_pending_equipment_count(self, obj):
        """
        Calcula cuántos equipos todavía faltan registrar
        respecto de la cantidad esperada.
        """

        registered_count = obj.equipment_units.filter(
            archived_at__isnull=True,
        ).count()

        expected_quantity = int(
            obj.expected_quantity or 0
        )

        return max(
            expected_quantity - registered_count,
            0,
        )


class ImportBatchDetailSerializer(
    serializers.ModelSerializer
):
    """
    Serializer completo de una importación o lote.
    """

    supplier_name = serializers.CharField(
        source="supplier.display_name",
        read_only=True,
    )

    supplier_document_number = serializers.CharField(
        source="supplier.document_number",
        read_only=True,
    )

    purchase_type_name = serializers.CharField(
        source="get_purchase_type_display",
        read_only=True,
    )

    currency_name = serializers.CharField(
        source="get_currency_display",
        read_only=True,
    )

    status_name = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    registered_equipment_count = serializers.SerializerMethodField()

    pending_equipment_count = serializers.SerializerMethodField()

    is_quantity_complete = serializers.SerializerMethodField()

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
        model = ImportBatch

        fields = (
            "id",
            "code",
            "purchase_type",
            "purchase_type_name",
            "supplier",
            "supplier_name",
            "supplier_document_number",
            "import_number",
            "purchase_order_number",
            "invoice_number",
            "invoice_date",
            "purchase_date",
            "estimated_arrival_date",
            "arrival_date",
            "unloading_start_date",
            "unloading_end_date",
            "origin_country_code",
            "origin_country_name",
            "origin_port",
            "destination_port",
            "container_number",
            "transport_reference",
            "warehouse_location",
            "expected_quantity",
            "declared_quantity",
            "registered_equipment_count",
            "pending_equipment_count",
            "is_quantity_complete",
            "currency",
            "currency_name",
            "exchange_rate",
            "equipment_subtotal",
            "freight_cost",
            "insurance_cost",
            "customs_cost",
            "tax_cost",
            "other_costs",
            "total_cost",
            "status",
            "status_name",
            "is_active",
            "unloading_notes",
            "notes",
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
            "supplier_name",
            "supplier_document_number",
            "purchase_type_name",
            "currency_name",
            "status_name",
            "registered_equipment_count",
            "pending_equipment_count",
            "is_quantity_complete",
            "total_cost",
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

    def get_registered_equipment_count(self, obj):
        return obj.equipment_units.filter(
            archived_at__isnull=True,
        ).count()

    def get_pending_equipment_count(self, obj):
        registered_count = obj.equipment_units.filter(
            archived_at__isnull=True,
        ).count()

        expected_quantity = int(
            obj.expected_quantity or 0
        )

        return max(
            expected_quantity - registered_count,
            0,
        )

    def get_is_quantity_complete(self, obj):
        """
        Indica si ya se registró la cantidad esperada
        de máquinas del lote.
        """

        if not obj.expected_quantity:
            return False

        registered_count = obj.equipment_units.filter(
            archived_at__isnull=True,
        ).count()

        return registered_count >= obj.expected_quantity


class ImportBatchCreateUpdateSerializer(
    serializers.ModelSerializer
):
    """
    Creación y modificación de importaciones
    y lotes de equipos.
    """

    class Meta:
        model = ImportBatch

        fields = (
            "code",
            "purchase_type",
            "supplier",
            "import_number",
            "purchase_order_number",
            "invoice_number",
            "invoice_date",
            "purchase_date",
            "estimated_arrival_date",
            "arrival_date",
            "unloading_start_date",
            "unloading_end_date",
            "origin_country_code",
            "origin_country_name",
            "origin_port",
            "destination_port",
            "container_number",
            "transport_reference",
            "warehouse_location",
            "expected_quantity",
            "declared_quantity",
            "currency",
            "exchange_rate",
            "equipment_subtotal",
            "freight_cost",
            "insurance_cost",
            "customs_cost",
            "tax_cost",
            "other_costs",
            "status",
            "is_active",
            "unloading_notes",
            "notes",
        )

    def validate_code(self, value):
        """
        Normaliza y valida el código del lote.
        """

        code = str(
            value or ""
        ).strip().upper()

        if not code:
            raise serializers.ValidationError(
                "El código de la importación o lote es obligatorio."
            )

        queryset = ImportBatch.objects.filter(
            code__iexact=code,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una importación o lote con este código."
            )

        return code

    def validate_supplier(self, value):
        """
        Valida que el tercero seleccionado pueda utilizarse
        como proveedor.
        """

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

    def validate_import_number(self, value):
        return str(
            value or ""
        ).strip()

    def validate_purchase_order_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_invoice_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_origin_country_code(self, value):
        """
        El código de país es opcional, pero cuando se registra
        debe contener exactamente dos letras.
        """

        country_code = str(
            value or ""
        ).strip().upper()

        if not country_code:
            return ""

        if len(country_code) != 2:
            raise serializers.ValidationError(
                "El código del país de origen debe contener "
                "exactamente dos letras."
            )

        if not country_code.isalpha():
            raise serializers.ValidationError(
                "El código del país de origen solo puede "
                "contener letras."
            )

        return country_code

    def validate_origin_country_name(self, value):
        return str(
            value or ""
        ).strip()

    def validate_origin_port(self, value):
        return str(
            value or ""
        ).strip()

    def validate_destination_port(self, value):
        return str(
            value or ""
        ).strip()

    def validate_container_number(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_transport_reference(self, value):
        return str(
            value or ""
        ).strip().upper()

    def validate_warehouse_location(self, value):
        return str(
            value or ""
        ).strip()

    def validate_unloading_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate_notes(self, value):
        return str(
            value or ""
        ).strip()

    def validate(self, attrs):
        """
        Valida las fechas, cantidades, estado y datos
        generales del lote.
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

        purchase_type = values.get(
            "purchase_type"
        )

        import_number = str(
            values.get(
                "import_number",
                "",
            )
            or ""
        ).strip()

        invoice_date = values.get(
            "invoice_date"
        )

        purchase_date = values.get(
            "purchase_date"
        )

        estimated_arrival_date = values.get(
            "estimated_arrival_date"
        )

        arrival_date = values.get(
            "arrival_date"
        )

        unloading_start_date = values.get(
            "unloading_start_date"
        )

        unloading_end_date = values.get(
            "unloading_end_date"
        )

        expected_quantity = int(
            values.get(
                "expected_quantity",
                0,
            )
            or 0
        )

        declared_quantity = int(
            values.get(
                "declared_quantity",
                0,
            )
            or 0
        )

        status = values.get(
            "status"
        )

        notes = str(
            values.get(
                "notes",
                "",
            )
            or ""
        ).strip()

        if (
            purchase_type
            == ImportBatch.PurchaseType.IMPORT
            and not import_number
        ):
            raise serializers.ValidationError(
                {
                    "import_number": (
                        "Una importación debe registrar "
                        "su número o referencia de importación."
                    )
                }
            )

        if (
            invoice_date
            and purchase_date
            and invoice_date > purchase_date
        ):
            raise serializers.ValidationError(
                {
                    "invoice_date": (
                        "La fecha de invoice o factura no puede "
                        "ser posterior a la fecha de compra."
                    )
                }
            )

        if (
            estimated_arrival_date
            and purchase_date
            and estimated_arrival_date < purchase_date
        ):
            raise serializers.ValidationError(
                {
                    "estimated_arrival_date": (
                        "La fecha estimada de llegada no puede "
                        "ser anterior a la fecha de compra."
                    )
                }
            )

        if (
            arrival_date
            and purchase_date
            and arrival_date < purchase_date
        ):
            raise serializers.ValidationError(
                {
                    "arrival_date": (
                        "La fecha real de llegada no puede "
                        "ser anterior a la fecha de compra."
                    )
                }
            )

        if (
            unloading_start_date
            and unloading_end_date
            and unloading_end_date < unloading_start_date
        ):
            raise serializers.ValidationError(
                {
                    "unloading_end_date": (
                        "La fecha de finalización de la descarga "
                        "no puede ser anterior a su inicio."
                    )
                }
            )

        if (
            status == ImportBatch.Status.RECEIVING
            and not unloading_start_date
        ):
            raise serializers.ValidationError(
                {
                    "unloading_start_date": (
                        "Un lote en descarga debe registrar "
                        "la fecha de inicio de descarga."
                    )
                }
            )

        if (
            status == ImportBatch.Status.COMPLETED
            and not arrival_date
        ):
            raise serializers.ValidationError(
                {
                    "arrival_date": (
                        "Un lote completado debe registrar "
                        "la fecha real de llegada."
                    )
                }
            )

        if (
            status == ImportBatch.Status.COMPLETED
            and not unloading_end_date
        ):
            raise serializers.ValidationError(
                {
                    "unloading_end_date": (
                        "Un lote completado debe registrar "
                        "la fecha de finalización de descarga."
                    )
                }
            )

        if (
            status == ImportBatch.Status.CANCELLED
            and not notes
        ):
            raise serializers.ValidationError(
                {
                    "notes": (
                        "Debes indicar el motivo de cancelación "
                        "del lote."
                    )
                }
            )

        if (
            expected_quantity
            and declared_quantity
            and expected_quantity != declared_quantity
            and not notes
        ):
            raise serializers.ValidationError(
                {
                    "notes": (
                        "Cuando la cantidad esperada y la declarada "
                        "son diferentes, debes registrar una observación."
                    )
                }
            )

        registered_count = 0

        if instance:
            registered_count = instance.equipment_units.filter(
                archived_at__isnull=True,
            ).count()

        if (
            expected_quantity
            and registered_count > expected_quantity
        ):
            raise serializers.ValidationError(
                {
                    "expected_quantity": (
                        "La cantidad esperada no puede ser menor "
                        "que la cantidad de equipos ya registrados "
                        f"en el lote ({registered_count})."
                    )
                }
            )

        if (
            status == ImportBatch.Status.COMPLETED
            and expected_quantity
            and registered_count
            and registered_count < expected_quantity
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "No puedes completar el lote porque todavía "
                        "faltan equipos por registrar."
                    )
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """
        Crea el lote registrando auditoría.
        """

        actor = get_authenticated_user(
            self
        )

        import_batch = ImportBatch(
            created_by=actor,
            updated_by=actor,
            **validated_data,
        )

        try:
            import_batch.full_clean()
            import_batch.save()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                convert_django_validation_error(
                    exc
                )
            ) from exc

        return import_batch

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        """
        Actualiza el lote registrando auditoría.
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


class ArchiveImportBatchSerializer(
    serializers.Serializer
):
    """
    Datos requeridos para archivar una importación
    o lote.
    """

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
    )


class ChangeImportBatchStatusSerializer(
    serializers.Serializer
):
    """
    Datos utilizados para cambiar el estado operativo
    de una importación o lote.
    """

    status = serializers.ChoiceField(
        choices=ImportBatch.Status.choices,
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=3000,
    )