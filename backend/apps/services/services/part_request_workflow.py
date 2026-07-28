# -*- coding: utf-8 -*-
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.services.models import (
    ServicePartRequest,
    ServicePartRequestComment,
    ServicePartRequestDecision,
    ServicePartRequestInformation,
    ServicePartRequestItem,
    ServicePartRequestStatusHistory,
)

from .part_notification_service import PartNotificationService
from .workflow_utils import (
    authenticated_user,
    require,
    save_validated,
)


class PartRequestWorkflow:
    @classmethod
    def _active_items(cls, request_object):
        return request_object.items.filter(
            archived_at__isnull=True,
        )

    @classmethod
    def _record_history(
        cls,
        *,
        request_object,
        previous_status,
        new_status,
        action,
        user,
        comment="",
        metadata=None,
    ):
        history = ServicePartRequestStatusHistory(
            request=request_object,
            previous_status=previous_status,
            new_status=new_status,
            action=action,
            responsible_area=(
                request_object.current_responsible_area
            ),
            changed_by=authenticated_user(user),
            source="service",
            comment=str(comment or "").strip(),
            metadata=metadata or {},
        )

        return save_validated(
            history,
            user=user,
            creating=True,
        )

    @classmethod
    def _add_comment(
        cls,
        *,
        request_object,
        user,
        message,
        comment_type,
        request_item=None,
    ):
        message = str(message or "").strip()

        if not message:
            return None

        comment = ServicePartRequestComment(
            request=request_object,
            request_item=request_item,
            comment_type=comment_type,
            message=message,
            author=authenticated_user(user),
        )

        return save_validated(
            comment,
            user=user,
            creating=True,
        )

    @classmethod
    def _change_status(
        cls,
        *,
        request_object,
        new_status,
        responsible_area,
        action,
        user,
        responsible_user=None,
        comment="",
        metadata=None,
    ):
        previous_status = request_object.status
        request_object.status = new_status
        request_object.current_responsible_area = (
            responsible_area
        )
        request_object.current_responsible_user = (
            responsible_user
        )

        save_validated(
            request_object,
            user=user,
        )

        cls._record_history(
            request_object=request_object,
            previous_status=previous_status,
            new_status=new_status,
            action=action,
            user=user,
            comment=comment,
            metadata=metadata,
        )

        return request_object

    @classmethod
    @transaction.atomic
    def submit_to_management(
        cls,
        request_object,
        *,
        user,
        management_user=None,
        comment="",
    ):
        request_object = (
            ServicePartRequest.objects
            .select_for_update()
            .get(pk=request_object.pk)
        )

        require(
            request_object.status
            in {
                ServicePartRequest.Status.DRAFT,
                ServicePartRequest.Status.INFORMATION_ANSWERED,
            },
            "Solo puede enviarse un pedido borrador o respondido.",
            "status",
        )

        items = cls._active_items(request_object)

        require(
            items.exists(),
            "El pedido debe contener al menos un artículo.",
            "items",
        )

        require(
            not items.filter(
                requested_quantity__lte=0,
            ).exists(),
            "Todos los artículos deben tener cantidad válida.",
            "items",
        )

        request_object.submitted_by = authenticated_user(user)
        request_object.submitted_at = timezone.now()

        cls._change_status(
            request_object=request_object,
            new_status=(
                ServicePartRequest.Status
                .SUBMITTED_TO_MANAGEMENT
            ),
            responsible_area=(
                ServicePartRequest.ResponsibleArea.MANAGEMENT
            ),
            responsible_user=management_user,
            action=(
                ServicePartRequestStatusHistory
                .Action
                .SUBMITTED
            ),
            user=user,
            comment=comment,
        )

        cls._add_comment(
            request_object=request_object,
            user=user,
            message=comment,
            comment_type=(
                ServicePartRequestComment
                .CommentType
                .TECHNICAL
            ),
        )

        PartNotificationService.create(
            request_object=request_object,
            recipient=management_user,
            notification_type=(
                "request_submitted"
            ),
            title=f"Pedido {request_object.code} enviado",
            message=(
                "El pedido requiere evaluación de gerencia."
            ),
            created_by=user,
        )

        return request_object

    @classmethod
    @transaction.atomic
    def start_management_review(
        cls,
        request_object,
        *,
        user,
        comment="",
    ):
        request_object = (
            ServicePartRequest.objects
            .select_for_update()
            .get(pk=request_object.pk)
        )

        require(
            request_object.status
            in {
                ServicePartRequest.Status
                .SUBMITTED_TO_MANAGEMENT,
                ServicePartRequest.Status
                .MANAGEMENT_REASSESSMENT,
            },
            "El pedido no está disponible para evaluación.",
            "status",
        )

        request_object.management_reviewed_by = (
            authenticated_user(user)
        )
        request_object.management_reviewed_at = (
            timezone.now()
        )

        return cls._change_status(
            request_object=request_object,
            new_status=(
                ServicePartRequest.Status
                .MANAGEMENT_REVIEW
            ),
            responsible_area=(
                ServicePartRequest.ResponsibleArea.MANAGEMENT
            ),
            responsible_user=user,
            action=(
                ServicePartRequestStatusHistory
                .Action
                .REVIEW_STARTED
            ),
            user=user,
            comment=comment,
        )

    @classmethod
    @transaction.atomic
    def request_information(
        cls,
        request_object,
        *,
        user,
        question,
        requested_to_area,
        requested_to_user=None,
        request_item=None,
        due_at=None,
    ):
        request_object = (
            ServicePartRequest.objects
            .select_for_update()
            .get(pk=request_object.pk)
        )

        require(
            request_object.status
            == ServicePartRequest.Status.MANAGEMENT_REVIEW,
            "Gerencia debe estar evaluando el pedido.",
            "status",
        )

        if request_item:
            require(
                request_item.request_id == request_object.id,
                "El artículo pertenece a otro pedido.",
                "request_item",
            )

        information = ServicePartRequestInformation(
            request=request_object,
            status=(
                ServicePartRequestInformation.Status.PENDING
            ),
            requested_by=authenticated_user(user),
            requested_to_area=requested_to_area,
            requested_to_user=requested_to_user,
            question=str(question or "").strip(),
            due_at=due_at,
        )

        save_validated(
            information,
            user=user,
            creating=True,
        )

        request_object.information_requested_at = timezone.now()

        cls._change_status(
            request_object=request_object,
            new_status=(
                ServicePartRequest.Status
                .INFORMATION_REQUESTED
            ),
            responsible_area=(
                ServicePartRequest.ResponsibleArea.SALES
                if requested_to_area == "sales"
                else ServicePartRequest.ResponsibleArea.TECHNICAL
            ),
            responsible_user=requested_to_user,
            action=(
                ServicePartRequestStatusHistory
                .Action
                .INFORMATION_REQUESTED
            ),
            user=user,
            comment=question,
            metadata={
                "information_id": str(information.pk),
            },
        )

        cls._add_comment(
            request_object=request_object,
            request_item=request_item,
            user=user,
            message=question,
            comment_type=(
                ServicePartRequestComment
                .CommentType
                .INFORMATION_REQUEST
            ),
        )

        PartNotificationService.create(
            request_object=request_object,
            request_item=request_item,
            recipient=requested_to_user,
            notification_type="information_required",
            title=f"Información requerida: {request_object.code}",
            message=question,
            created_by=user,
        )

        return information

    @classmethod
    @transaction.atomic
    def answer_information(
        cls,
        information,
        *,
        user,
        response,
        management_user=None,
    ):
        information = (
            ServicePartRequestInformation.objects
            .select_for_update()
            .select_related("request")
            .get(pk=information.pk)
        )

        require(
            information.status
            == ServicePartRequestInformation.Status.PENDING,
            "La solicitud de información ya fue atendida.",
            "status",
        )

        information.status = (
            ServicePartRequestInformation.Status.ANSWERED
        )
        information.response = str(response or "").strip()
        information.answered_by = authenticated_user(user)
        information.answered_at = timezone.now()

        save_validated(
            information,
            user=user,
        )

        request_object = information.request
        request_object.information_answered_at = timezone.now()

        cls._change_status(
            request_object=request_object,
            new_status=(
                ServicePartRequest.Status
                .INFORMATION_ANSWERED
            ),
            responsible_area=(
                ServicePartRequest.ResponsibleArea.MANAGEMENT
            ),
            responsible_user=management_user,
            action=(
                ServicePartRequestStatusHistory
                .Action
                .INFORMATION_ANSWERED
            ),
            user=user,
            comment=information.response,
            metadata={
                "information_id": str(information.pk),
            },
        )

        cls._add_comment(
            request_object=request_object,
            user=user,
            message=information.response,
            comment_type=(
                ServicePartRequestComment
                .CommentType
                .INFORMATION_RESPONSE
            ),
        )

        PartNotificationService.create(
            request_object=request_object,
            recipient=management_user,
            notification_type="information_answered",
            title=f"Información respondida: {request_object.code}",
            message=information.response,
            created_by=user,
        )

        return information

    @classmethod
    @transaction.atomic
    def reassess(
        cls,
        request_object,
        *,
        user,
        management_user=None,
        comment="",
    ):
        request_object = (
            ServicePartRequest.objects
            .select_for_update()
            .get(pk=request_object.pk)
        )

        require(
            request_object.status
            == ServicePartRequest.Status.INFORMATION_ANSWERED,
            "El pedido no tiene información respondida.",
            "status",
        )

        return cls._change_status(
            request_object=request_object,
            new_status=(
                ServicePartRequest.Status
                .MANAGEMENT_REASSESSMENT
            ),
            responsible_area=(
                ServicePartRequest.ResponsibleArea.MANAGEMENT
            ),
            responsible_user=management_user or user,
            action=(
                ServicePartRequestStatusHistory
                .Action
                .REVIEW_STARTED
            ),
            user=user,
            comment=comment,
        )

    @classmethod
    @transaction.atomic
    def decide(
        cls,
        request_object,
        *,
        user,
        decisions,
        reason="",
        stock_user=None,
    ):
        request_object = (
            ServicePartRequest.objects
            .select_for_update()
            .get(pk=request_object.pk)
        )

        require(
            request_object.status
            in {
                ServicePartRequest.Status.MANAGEMENT_REVIEW,
                ServicePartRequest.Status.MANAGEMENT_REASSESSMENT,
            },
            "El pedido no está en evaluación de gerencia.",
            "status",
        )

        active_items = {
            str(item.pk): item
            for item in cls._active_items(
                request_object
            ).select_for_update()
        }

        require(
            active_items,
            "El pedido no contiene artículos.",
            "items",
        )

        decision_values = []

        for data in decisions:
            item_id = str(data.get("request_item_id", ""))
            item = active_items.get(item_id)

            require(
                item is not None,
                "Uno de los artículos no pertenece al pedido.",
                "decisions",
            )

            decision_value = data.get("decision")
            approved_quantity = data.get(
                "approved_quantity"
            )
            item_reason = str(
                data.get("reason", "")
            ).strip()
            information_required = str(
                data.get("information_required", "")
            ).strip()

            decision = ServicePartRequestDecision(
                request=request_object,
                request_item=item,
                decision=decision_value,
                requested_quantity=item.requested_quantity,
                approved_quantity=approved_quantity,
                decided_by=authenticated_user(user),
                decided_at=timezone.now(),
                reason=item_reason,
                information_required=information_required,
                is_final=(
                    decision_value
                    != ServicePartRequestDecision
                    .Decision
                    .INFORMATION_REQUIRED
                ),
            )

            save_validated(
                decision,
                user=user,
                creating=True,
            )

            mapping = {
                ServicePartRequestDecision.Decision.APPROVED: (
                    ServicePartRequestItem
                    .ManagementDecision
                    .APPROVED
                ),
                ServicePartRequestDecision.Decision.PARTIALLY_APPROVED: (
                    ServicePartRequestItem
                    .ManagementDecision
                    .PARTIAL
                ),
                ServicePartRequestDecision.Decision.REJECTED: (
                    ServicePartRequestItem
                    .ManagementDecision
                    .REJECTED
                ),
                ServicePartRequestDecision.Decision.INFORMATION_REQUIRED: (
                    ServicePartRequestItem
                    .ManagementDecision
                    .INFORMATION_REQUIRED
                ),
            }

            item.management_decision = mapping[
                decision_value
            ]
            item.approved_quantity = approved_quantity
            item.management_notes = (
                item_reason
                or information_required
            )

            save_validated(
                item,
                user=user,
            )

            decision_values.append(decision_value)

        request_object.management_reviewed_by = (
            authenticated_user(user)
        )
        request_object.management_reviewed_at = (
            timezone.now()
        )
        request_object.management_notes = str(
            reason or ""
        ).strip()

        if (
            ServicePartRequestDecision
            .Decision
            .INFORMATION_REQUIRED
            in decision_values
        ):
            new_status = (
                ServicePartRequest.Status
                .INFORMATION_REQUESTED
            )
            responsible_area = (
                ServicePartRequest.ResponsibleArea.SALES
            )
            action = (
                ServicePartRequestStatusHistory
                .Action
                .INFORMATION_REQUESTED
            )
        elif all(
            value
            == ServicePartRequestDecision.Decision.REJECTED
            for value in decision_values
        ):
            new_status = ServicePartRequest.Status.REJECTED
            responsible_area = (
                ServicePartRequest.ResponsibleArea.CLOSED
            )
            action = (
                ServicePartRequestStatusHistory
                .Action
                .REJECTED
            )
        else:
            new_status = ServicePartRequest.Status.APPROVED
            responsible_area = (
                ServicePartRequest.ResponsibleArea.SALES
            )
            action = (
                ServicePartRequestStatusHistory
                .Action
                .PARTIALLY_APPROVED
                if (
                    ServicePartRequestDecision
                    .Decision
                    .PARTIALLY_APPROVED
                    in decision_values
                    or ServicePartRequestDecision
                    .Decision
                    .REJECTED
                    in decision_values
                )
                else ServicePartRequestStatusHistory
                .Action
                .APPROVED
            )

        cls._change_status(
            request_object=request_object,
            new_status=new_status,
            responsible_area=responsible_area,
            responsible_user=stock_user,
            action=action,
            user=user,
            comment=reason,
        )

        if new_status == ServicePartRequest.Status.APPROVED:
            previous = request_object.status
            request_object.status = (
                ServicePartRequest.Status
                .PENDING_STOCK_REVIEW
            )
            request_object.current_responsible_area = (
                ServicePartRequest.ResponsibleArea.SALES
            )
            request_object.current_responsible_user = stock_user
            save_validated(request_object, user=user)

            cls._record_history(
                request_object=request_object,
                previous_status=previous,
                new_status=request_object.status,
                action=(
                    ServicePartRequestStatusHistory
                    .Action
                    .STOCK_REVIEWED
                ),
                user=user,
                comment="Pendiente de revisión de stock.",
            )

            PartNotificationService.create(
                request_object=request_object,
                recipient=stock_user,
                notification_type="stock_review_required",
                title=f"Confirmar stock: {request_object.code}",
                message=(
                    "Gerencia aprobó artículos del pedido "
                    "y requiere confirmación de abastecimiento."
                ),
                created_by=user,
            )

        return request_object
