# -*- coding: utf-8 -*-
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.services.models import (
    EquipmentInstalledItem,
    ServiceInstallationItem,
    ServiceOrder,
    ServicePartRequest,
    ServicePartRequestItem,
    ServicePartRequestStatusHistory,
    ServicePartTransfer,
    ServicePartTransferHistory,
    ServiceReusablePart,
    ServiceReusablePartHistory,
)

from .part_notification_service import PartNotificationService
from .workflow_utils import (
    authenticated_user,
    copy_existing_fields,
    require,
    save_validated,
)


class PartInstallationWorkflow:
    ORDER_COPY_FIELDS = (
        "equipment",
        "service_origin",
        "priority",
        "customer_code",
        "customer_document_type",
        "customer_document_number",
        "customer_name",
        "customer_trade_name",
        "branch_name",
        "address",
        "address_reference",
        "district",
        "province",
        "region",
        "destination_latitude",
        "destination_longitude",
        "geofence_radius_meters",
        "site_location",
        "contact_name",
        "contact_job_title",
        "contact_phone",
        "contact_email",
        "contract_reference",
        "rental_assignment_reference",
    )

    @classmethod
    def _installation_status(cls, assigned_technician):
        if assigned_technician:
            return ServiceOrder.Status.ASSIGNED

        return ServiceOrder.Status.PENDING_ASSIGNMENT

    @classmethod
    @transaction.atomic
    def create_installation_order(
        cls,
        request_object,
        *,
        user,
        assigned_technician=None,
        scheduled_at=None,
        notes="",
    ):
        request_object = (
            ServicePartRequest.objects
            .select_for_update()
            .select_related(
                "service_order",
                "service_order__equipment",
            )
            .get(pk=request_object.pk)
        )

        require(
            request_object.status
            == ServicePartRequest.Status.READY_FOR_INSTALLATION,
            "El pedido no está listo para instalación.",
            "status",
        )

        require(
            not request_object.installation_service_order_id,
            "El pedido ya tiene una OS de instalación.",
            "installation_service_order",
        )

        source_order = request_object.service_order

        values = copy_existing_fields(
            source=source_order,
            destination_model=ServiceOrder,
            field_names=cls.ORDER_COPY_FIELDS,
        )

        detail_lines = [
            (
                "Instalación o reemplazo de artículos "
                f"aprobados en el pedido {request_object.code}."
            )
        ]

        clean_notes = str(notes or "").strip()

        if clean_notes:
            detail_lines.append(clean_notes)

        values.update(
            {
                "service_type": ServiceOrder.ServiceType.OTHER,
                "status": cls._installation_status(
                    assigned_technician
                ),
                "result": ServiceOrder.Result.PENDING,
                "reported_problem": "
".join(detail_lines),
                "assigned_technician": assigned_technician,
                "assigned_by": (
                    authenticated_user(user)
                    if assigned_technician
                    else None
                ),
                "scheduled_at": scheduled_at,
            }
        )

        installation_order = ServiceOrder(**values)

        save_validated(
            installation_order,
            user=user,
            creating=True,
        )

        previous_status = request_object.status
        request_object.installation_service_order = (
            installation_order
        )
        request_object.status = (
            ServicePartRequest.Status
            .INSTALLATION_ORDER_CREATED
        )
        request_object.current_responsible_area = (
            ServicePartRequest.ResponsibleArea.INSTALLATION
        )
        request_object.current_responsible_user = (
            assigned_technician
        )

        save_validated(
            request_object,
            user=user,
        )

        approved_items = request_object.items.filter(
            archived_at__isnull=True,
            management_decision__in=[
                ServicePartRequestItem
                .ManagementDecision
                .APPROVED,
                ServicePartRequestItem
                .ManagementDecision
                .PARTIAL,
            ],
        )

        installation_items = []

        for request_item in approved_items:
            transfer = (
                ServicePartTransfer.objects
                .filter(
                    part_request_item=request_item,
                    archived_at__isnull=True,
                )
                .first()
            )

            quantity = (
                request_item.stock_confirmed_quantity
                or request_item.approved_quantity
                or request_item.requested_quantity
            )

            installation_item = ServiceInstallationItem(
                service_order=installation_order,
                part_request_item=request_item,
                transfer=transfer,
                planned_quantity=quantity,
                installed_quantity=Decimal("0"),
                returned_quantity=Decimal("0"),
                result=(
                    ServiceInstallationItem.Result.PENDING
                ),
            )

            save_validated(
                installation_item,
                user=user,
                creating=True,
            )
            installation_items.append(
                installation_item
            )

        history = ServicePartRequestStatusHistory(
            request=request_object,
            previous_status=previous_status,
            new_status=request_object.status,
            action=(
                ServicePartRequestStatusHistory
                .Action
                .INSTALLATION_ORDER_CREATED
            ),
            responsible_area=(
                request_object.current_responsible_area
            ),
            changed_by=authenticated_user(user),
            source="service",
            comment=str(notes or "").strip(),
            metadata={
                "installation_service_order_id": str(
                    installation_order.pk
                ),
            },
        )

        save_validated(
            history,
            user=user,
            creating=True,
        )

        PartNotificationService.create(
            request_object=request_object,
            recipient=assigned_technician,
            notification_type="installation_order_created",
            title=f"OS de instalación: {request_object.code}",
            message=(
                "Se creó una OS para instalar o reemplazar "
                "los artículos del pedido."
            ),
            created_by=user,
        )

        return installation_order, installation_items

    @classmethod
    def _meter_values(cls, installation_item):
        return {
            "meter_type": installation_item.meter_type,
            "total_meter": installation_item.total_meter,
            "black_meter": installation_item.black_meter,
            "color_meter": installation_item.color_meter,
            "scan_meter": installation_item.scan_meter,
            "reference_meter": (
                installation_item.reference_meter
            ),
        }

    @classmethod
    @transaction.atomic
    def complete_item(
        cls,
        installation_item,
        *,
        user,
        result,
        installed_quantity,
        returned_quantity=Decimal("0"),
        meter_type=None,
        total_meter=None,
        black_meter=None,
        color_meter=None,
        scan_meter=None,
        removed_item_condition="",
        installation_notes="",
        non_installation_reason="",
    ):
        installation_item = (
            ServiceInstallationItem.objects
            .select_for_update()
            .select_related(
                "service_order",
                "part_request_item",
                "part_request_item__request",
                "part_request_item__source_component",
                "transfer",
                "transfer__reusable_part",
                "transfer__source_equipment",
            )
            .get(pk=installation_item.pk)
        )

        require(
            installation_item.result
            == ServiceInstallationItem.Result.PENDING,
            "El artículo ya tiene un resultado registrado.",
            "result",
        )

        installation_item.result = result
        installation_item.installed_quantity = (
            installed_quantity
        )
        installation_item.returned_quantity = (
            returned_quantity
        )
        installation_item.installed_by = (
            authenticated_user(user)
        )

        if result in {
            ServiceInstallationItem.Result.INSTALLED,
            ServiceInstallationItem.Result.PARTIALLY_INSTALLED,
        }:
            installation_item.installed_at = timezone.now()

        if meter_type is not None:
            installation_item.meter_type = meter_type

        installation_item.total_meter = total_meter
        installation_item.black_meter = black_meter
        installation_item.color_meter = color_meter
        installation_item.scan_meter = scan_meter
        installation_item.removed_item_condition = str(
            removed_item_condition or ""
        ).strip()
        installation_item.installation_notes = str(
            installation_notes or ""
        ).strip()
        installation_item.non_installation_reason = str(
            non_installation_reason or ""
        ).strip()

        save_validated(
            installation_item,
            user=user,
        )

        installed_results = {
            ServiceInstallationItem.Result.INSTALLED,
            ServiceInstallationItem.Result.PARTIALLY_INSTALLED,
        }

        if result not in installed_results:
            return installation_item, None

        request_item = installation_item.part_request_item
        request_object = request_item.request
        component = request_item.source_component
        transfer = installation_item.transfer
        reusable_part = (
            transfer.reusable_part
            if transfer
            else None
        )

        origin_map = {
            ServicePartRequestItem.SupplyMethod.STOCK: (
                EquipmentInstalledItem.OriginType.STOCK
            ),
            ServicePartRequestItem.SupplyMethod.REUSABLE_PART: (
                EquipmentInstalledItem
                .OriginType
                .REUSABLE_PART
            ),
            ServicePartRequestItem.SupplyMethod.DONOR_EQUIPMENT: (
                EquipmentInstalledItem
                .OriginType
                .DONOR_EQUIPMENT
            ),
            ServicePartRequestItem.SupplyMethod.PURCHASE: (
                EquipmentInstalledItem.OriginType.PURCHASE
            ),
            ServicePartRequestItem.SupplyMethod.EXTERNAL_REPAIR: (
                EquipmentInstalledItem
                .OriginType
                .EXTERNAL_REPAIR
            ),
        }

        history_item = EquipmentInstalledItem(
            equipment=request_object.service_order.equipment,
            service_order=installation_item.service_order,
            part_request=request_object,
            part_request_item=request_item,
            installation_item=installation_item,
            reusable_part=reusable_part,
            component=component,
            item_type=request_item.item_type,
            origin_type=origin_map.get(
                request_item.supply_method,
                EquipmentInstalledItem.OriginType.OTHER,
            ),
            status=EquipmentInstalledItem.Status.INSTALLED,
            item_code=(
                request_item.component_code
                or request_item.custom_code
            ),
            item_name=request_item.display_name,
            manufacturer_code=(
                request_item.manufacturer_code
            ),
            color=request_item.color,
            serial_number=(
                reusable_part.serial_number
                if reusable_part
                else ""
            ),
            quantity_installed=installed_quantity,
            unit_of_measure=request_item.unit_of_measure,
            installed_by=authenticated_user(user),
            installed_at=installation_item.installed_at,
            source_equipment=(
                transfer.source_equipment
                if transfer
                else None
            ),
            notes=installation_item.installation_notes,
            **cls._meter_values(installation_item),
        )

        save_validated(
            history_item,
            user=user,
            creating=True,
        )

        installation_item.history_generated = True
        save_validated(
            installation_item,
            user=user,
        )

        request_item.delivered_quantity = (
            (request_item.delivered_quantity or Decimal("0"))
            + installed_quantity
        )
        save_validated(
            request_item,
            user=user,
        )

        if transfer:
            previous_status = transfer.status
            transfer.status = ServicePartTransfer.Status.INSTALLED
            transfer.installed_at = (
                installation_item.installed_at
            )
            transfer.installed_by = authenticated_user(user)
            transfer.current_holder = None
            transfer.current_location = (
                str(
                    request_object
                    .service_order
                    .equipment
                )
            )
            save_validated(
                transfer,
                user=user,
            )

            transfer_history = ServicePartTransferHistory(
                transfer=transfer,
                event=(
                    ServicePartTransferHistory.Event.INSTALLED
                ),
                previous_status=previous_status,
                new_status=transfer.status,
                performed_by=authenticated_user(user),
                new_location=transfer.current_location,
                source="service",
                notes=installation_item.installation_notes,
            )
            save_validated(
                transfer_history,
                user=user,
                creating=True,
            )

            if reusable_part:
                reusable_previous_status = reusable_part.status
                reusable_part.status = (
                    ServiceReusablePart.Status.INSTALLED
                )
                reusable_part.current_equipment = (
                    request_object.service_order.equipment
                )
                reusable_part.current_holder = None
                reusable_part.installed_at = (
                    installation_item.installed_at
                )
                reusable_part.location_name = (
                    str(
                        request_object
                        .service_order
                        .equipment
                    )
                )
                save_validated(
                    reusable_part,
                    user=user,
                )

                reusable_history = ServiceReusablePartHistory(
                    reusable_part=reusable_part,
                    event=(
                        ServiceReusablePartHistory.Event.INSTALLED
                    ),
                    previous_status=reusable_previous_status,
                    new_status=reusable_part.status,
                    previous_equipment=(
                        transfer.source_equipment
                    ),
                    new_equipment=(
                        request_object.service_order.equipment
                    ),
                    performed_by=authenticated_user(user),
                    source="service",
                    notes=installation_item.installation_notes,
                )
                save_validated(
                    reusable_history,
                    user=user,
                    creating=True,
                )

        return installation_item, history_item

    @classmethod
    @transaction.atomic
    def complete_request(
        cls,
        request_object,
        *,
        user,
        notes="",
    ):
        request_object = (
            ServicePartRequest.objects
            .select_for_update()
            .get(pk=request_object.pk)
        )

        require(
            request_object.status
            == ServicePartRequest.Status
            .INSTALLATION_ORDER_CREATED,
            "El pedido no tiene una OS de instalación activa.",
            "status",
        )

        installation_items = ServiceInstallationItem.objects.filter(
            service_order=request_object.installation_service_order,
            archived_at__isnull=True,
        )

        require(
            installation_items.exists(),
            "La OS no tiene artículos de instalación.",
            "installation_items",
        )

        require(
            not installation_items.filter(
                result=ServiceInstallationItem.Result.PENDING,
            ).exists(),
            "Existen artículos pendientes de resultado.",
            "installation_items",
        )

        require(
            not installation_items.filter(
                result__in=[
                    ServiceInstallationItem.Result.INSTALLED,
                    ServiceInstallationItem
                    .Result
                    .PARTIALLY_INSTALLED,
                ],
                history_generated=False,
            ).exists(),
            "Existen instalaciones sin historial generado.",
            "installation_items",
        )

        previous_status = request_object.status
        request_object.status = (
            ServicePartRequest.Status.DELIVERED
        )
        request_object.current_responsible_area = (
            ServicePartRequest.ResponsibleArea.CLOSED
        )
        request_object.current_responsible_user = None
        request_object.delivered_at = timezone.now()
        request_object.closed_at = timezone.now()
        request_object.notes = str(notes or "").strip()

        save_validated(
            request_object,
            user=user,
        )

        history = ServicePartRequestStatusHistory(
            request=request_object,
            previous_status=previous_status,
            new_status=request_object.status,
            action=(
                ServicePartRequestStatusHistory
                .Action
                .DELIVERED
            ),
            responsible_area=(
                request_object.current_responsible_area
            ),
            changed_by=authenticated_user(user),
            source="service",
            comment=request_object.notes,
        )

        save_validated(
            history,
            user=user,
            creating=True,
        )

        return request_object
