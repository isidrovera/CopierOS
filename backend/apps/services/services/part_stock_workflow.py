# -*- coding: utf-8 -*-
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.services.models import (
    ServicePartRequest,
    ServicePartRequestItem,
    ServicePartRequestStatusHistory,
    ServicePartStockReview,
    ServicePartStockReviewHistory,
    ServiceReusablePart,
)

from .part_notification_service import PartNotificationService
from .workflow_utils import (
    authenticated_user,
    require,
    save_validated,
)


class PartStockWorkflow:
    @classmethod
    def _history(
        cls,
        *,
        stock_review,
        event,
        user,
        previous_status="",
        new_status="",
        notes="",
        **changes,
    ):
        history = ServicePartStockReviewHistory(
            stock_review=stock_review,
            event=event,
            previous_status=previous_status,
            new_status=new_status,
            performed_by=authenticated_user(user),
            source="service",
            notes=str(notes or "").strip(),
            **changes,
        )

        return save_validated(
            history,
            user=user,
            creating=True,
        )

    @classmethod
    @transaction.atomic
    def review_item(
        cls,
        request_item,
        *,
        user,
        status,
        available_quantity=Decimal("0"),
        reserved_quantity=Decimal("0"),
        reusable_part=None,
        expected_available_at=None,
        purchase_reference="",
        warehouse_location="",
        notes="",
    ):
        request_item = (
            ServicePartRequestItem.objects
            .select_for_update()
            .select_related("request")
            .get(pk=request_item.pk)
        )

        request_object = request_item.request

        require(
            request_object.status
            in {
                ServicePartRequest.Status.PENDING_STOCK_REVIEW,
                ServicePartRequest.Status.PARTIAL_STOCK,
                ServicePartRequest.Status.OUT_OF_STOCK,
            },
            "El pedido no está pendiente de stock.",
            "status",
        )

        require(
            request_item.management_decision
            in {
                ServicePartRequestItem
                .ManagementDecision
                .APPROVED,
                ServicePartRequestItem
                .ManagementDecision
                .PARTIAL,
            },
            "El artículo no fue aprobado por gerencia.",
            "management_decision",
        )

        review, created = (
            ServicePartStockReview.objects
            .select_for_update()
            .get_or_create(
                request_item=request_item,
                defaults={
                    "request": request_object,
                    "requested_quantity": (
                        request_item.approved_quantity
                        or request_item.requested_quantity
                    ),
                },
            )
        )

        previous_status = review.status
        previous_available = review.available_quantity
        previous_reserved = review.reserved_quantity
        previous_location = review.warehouse_location
        previous_expected = review.expected_available_at

        review.request = request_object
        review.status = status
        review.reviewed_by = authenticated_user(user)
        review.reviewed_at = timezone.now()
        review.requested_quantity = (
            request_item.approved_quantity
            or request_item.requested_quantity
        )
        review.available_quantity = available_quantity
        review.reserved_quantity = reserved_quantity
        review.reusable_part = reusable_part
        review.expected_available_at = expected_available_at
        review.purchase_reference = str(
            purchase_reference or ""
        ).strip()
        review.warehouse_location = str(
            warehouse_location or ""
        ).strip()
        review.notes = str(notes or "").strip()

        save_validated(
            review,
            user=user,
            creating=created,
        )

        supply_map = {
            ServicePartStockReview.Status.AVAILABLE: (
                ServicePartRequestItem.SupplyMethod.STOCK
            ),
            ServicePartStockReview.Status.PARTIAL: (
                ServicePartRequestItem.SupplyMethod.STOCK
            ),
            ServicePartStockReview.Status.REUSABLE_AVAILABLE: (
                ServicePartRequestItem
                .SupplyMethod
                .REUSABLE_PART
            ),
            ServicePartStockReview.Status.DONOR_EQUIPMENT_AVAILABLE: (
                ServicePartRequestItem
                .SupplyMethod
                .DONOR_EQUIPMENT
            ),
            ServicePartStockReview.Status.PURCHASE_REQUIRED: (
                ServicePartRequestItem.SupplyMethod.PURCHASE
            ),
            ServicePartStockReview.Status.EXTERNAL_REPAIR_REQUIRED: (
                ServicePartRequestItem
                .SupplyMethod
                .EXTERNAL_REPAIR
            ),
            ServicePartStockReview.Status.OUT_OF_STOCK: (
                ServicePartRequestItem
                .SupplyMethod
                .NOT_AVAILABLE
            ),
        }

        request_item.supply_method = supply_map.get(
            status,
            ServicePartRequestItem.SupplyMethod.PENDING,
        )
        request_item.stock_confirmed_quantity = (
            reserved_quantity
            if reserved_quantity > 0
            else available_quantity
        )
        request_item.stock_notes = review.notes

        save_validated(
            request_item,
            user=user,
        )

        if reusable_part:
            reusable_part.status = (
                ServiceReusablePart.Status.RESERVED
            )
            save_validated(
                reusable_part,
                user=user,
            )

        event_map = {
            ServicePartStockReview.Status.AVAILABLE: (
                ServicePartStockReviewHistory.Event.AVAILABLE
            ),
            ServicePartStockReview.Status.PARTIAL: (
                ServicePartStockReviewHistory.Event.PARTIAL
            ),
            ServicePartStockReview.Status.OUT_OF_STOCK: (
                ServicePartStockReviewHistory.Event.OUT_OF_STOCK
            ),
            ServicePartStockReview.Status.REUSABLE_AVAILABLE: (
                ServicePartStockReviewHistory
                .Event
                .REUSABLE_SELECTED
            ),
            ServicePartStockReview.Status.DONOR_EQUIPMENT_AVAILABLE: (
                ServicePartStockReviewHistory
                .Event
                .DONOR_EQUIPMENT_SELECTED
            ),
            ServicePartStockReview.Status.PURCHASE_REQUIRED: (
                ServicePartStockReviewHistory
                .Event
                .PURCHASE_REQUIRED
            ),
            ServicePartStockReview.Status.EXTERNAL_REPAIR_REQUIRED: (
                ServicePartStockReviewHistory
                .Event
                .EXTERNAL_REPAIR_REQUIRED
            ),
        }

        cls._history(
            stock_review=review,
            event=event_map.get(
                status,
                ServicePartStockReviewHistory
                .Event
                .REVIEW_STARTED,
            ),
            user=user,
            previous_status=previous_status,
            new_status=status,
            previous_available_quantity=previous_available,
            new_available_quantity=available_quantity,
            previous_reserved_quantity=previous_reserved,
            new_reserved_quantity=reserved_quantity,
            previous_location=previous_location,
            new_location=review.warehouse_location,
            previous_expected_available_at=previous_expected,
            new_expected_available_at=expected_available_at,
            notes=notes,
        )

        return review

    @classmethod
    @transaction.atomic
    def finalize_request_review(
        cls,
        request_object,
        *,
        user,
        logistics_user=None,
        notes="",
    ):
        request_object = (
            ServicePartRequest.objects
            .select_for_update()
            .get(pk=request_object.pk)
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

        require(
            approved_items.exists(),
            "No existen artículos aprobados.",
            "items",
        )

        reviewed_ids = set(
            ServicePartStockReview.objects.filter(
                request=request_object,
                request_item__in=approved_items,
            ).values_list(
                "request_item_id",
                flat=True,
            )
        )

        missing = [
            str(item.pk)
            for item in approved_items
            if item.pk not in reviewed_ids
        ]

        require(
            not missing,
            "Faltan artículos por revisar en stock.",
            "items",
        )

        reviews = ServicePartStockReview.objects.filter(
            request=request_object,
        )

        unavailable_statuses = {
            ServicePartStockReview.Status.OUT_OF_STOCK,
            ServicePartStockReview.Status.CANCELLED,
        }

        partial_statuses = {
            ServicePartStockReview.Status.PARTIAL,
            ServicePartStockReview.Status.PURCHASE_REQUIRED,
            ServicePartStockReview.Status.EXTERNAL_REPAIR_REQUIRED,
        }

        all_unavailable = all(
            review.status in unavailable_statuses
            for review in reviews
        )

        has_partial = any(
            review.status in partial_statuses
            for review in reviews
        )

        previous_status = request_object.status
        request_object.stock_reviewed_by = (
            authenticated_user(user)
        )
        request_object.stock_reviewed_at = timezone.now()
        request_object.stock_notes = str(notes or "").strip()

        if all_unavailable:
            request_object.status = (
                ServicePartRequest.Status.OUT_OF_STOCK
            )
            request_object.current_responsible_area = (
                ServicePartRequest.ResponsibleArea.SALES
            )
        elif has_partial:
            request_object.status = (
                ServicePartRequest.Status.PARTIAL_STOCK
            )
            request_object.current_responsible_area = (
                ServicePartRequest.ResponsibleArea.SALES
            )
        else:
            request_object.status = (
                ServicePartRequest.Status.STOCK_CONFIRMED
            )
            request_object.current_responsible_area = (
                ServicePartRequest.ResponsibleArea.LOGISTICS
            )
            request_object.current_responsible_user = (
                logistics_user
            )

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
                .STOCK_REVIEWED
            ),
            responsible_area=(
                request_object.current_responsible_area
            ),
            changed_by=authenticated_user(user),
            source="service",
            comment=request_object.stock_notes,
        )

        save_validated(
            history,
            user=user,
            creating=True,
        )

        if (
            request_object.status
            == ServicePartRequest.Status.STOCK_CONFIRMED
        ):
            request_object.status = (
                ServicePartRequest.Status.PENDING_LOGISTICS
            )
            save_validated(
                request_object,
                user=user,
            )

            PartNotificationService.create(
                request_object=request_object,
                recipient=logistics_user,
                notification_type="logistics_preparation",
                title=f"Preparar pedido {request_object.code}",
                message=(
                    "El abastecimiento fue confirmado y debe "
                    "prepararse para la instalación."
                ),
                created_by=user,
            )

        return request_object

    @classmethod
    @transaction.atomic
    def mark_preparing(
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
            == ServicePartRequest.Status.PENDING_LOGISTICS,
            "El pedido no está pendiente de logística.",
            "status",
        )

        previous_status = request_object.status
        request_object.status = (
            ServicePartRequest.Status.PREPARING
        )
        request_object.current_responsible_area = (
            ServicePartRequest.ResponsibleArea.LOGISTICS
        )
        request_object.current_responsible_user = user
        request_object.logistics_prepared_by = (
            authenticated_user(user)
        )
        request_object.logistics_notes = str(
            notes or ""
        ).strip()

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
                .PREPARATION_STARTED
            ),
            responsible_area=(
                request_object.current_responsible_area
            ),
            changed_by=authenticated_user(user),
            source="service",
            comment=request_object.logistics_notes,
        )

        save_validated(
            history,
            user=user,
            creating=True,
        )

        return request_object

    @classmethod
    @transaction.atomic
    def mark_ready(
        cls,
        request_object,
        *,
        user,
        installation_coordinator=None,
        notes="",
    ):
        request_object = (
            ServicePartRequest.objects
            .select_for_update()
            .get(pk=request_object.pk)
        )

        require(
            request_object.status
            == ServicePartRequest.Status.PREPARING,
            "El pedido no está en preparación.",
            "status",
        )

        previous_status = request_object.status
        request_object.status = (
            ServicePartRequest.Status.READY_FOR_INSTALLATION
        )
        request_object.current_responsible_area = (
            ServicePartRequest.ResponsibleArea.INSTALLATION
        )
        request_object.current_responsible_user = (
            installation_coordinator
        )
        request_object.logistics_prepared_by = (
            authenticated_user(user)
        )
        request_object.logistics_ready_at = timezone.now()
        request_object.logistics_notes = str(
            notes or ""
        ).strip()

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
                .READY_FOR_INSTALLATION
            ),
            responsible_area=(
                request_object.current_responsible_area
            ),
            changed_by=authenticated_user(user),
            source="service",
            comment=request_object.logistics_notes,
        )

        save_validated(
            history,
            user=user,
            creating=True,
        )

        PartNotificationService.create(
            request_object=request_object,
            recipient=installation_coordinator,
            notification_type="ready_for_installation",
            title=f"Pedido listo: {request_object.code}",
            message=(
                "El pedido está listo para crear y asignar "
                "la OS de instalación."
            ),
            created_by=user,
        )

        return request_object
