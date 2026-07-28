# -*- coding: utf-8 -*-
from django.db import transaction

from apps.services.models import (
    ServicePartRequestNotification,
)

from .workflow_utils import (
    authenticated_user,
    save_validated,
)


class PartNotificationService:
    @classmethod
    @transaction.atomic
    def create(
        cls,
        *,
        request_object,
        recipient,
        notification_type,
        title,
        message,
        request_item=None,
        channel=None,
        action_url="",
        metadata=None,
        created_by=None,
        prevent_duplicate=True,
    ):
        if recipient is None:
            return None

        channel = (
            channel
            or ServicePartRequestNotification.Channel.IN_APP
        )

        lookup = {
            "request": request_object,
            "request_item": request_item,
            "recipient": recipient,
            "notification_type": notification_type,
            "channel": channel,
            "delivery_status": (
                ServicePartRequestNotification
                .DeliveryStatus
                .PENDING
            ),
            "archived_at__isnull": True,
        }

        if prevent_duplicate:
            existing = (
                ServicePartRequestNotification.objects
                .filter(**lookup)
                .order_by("-created_at")
                .first()
            )

            if existing:
                return existing

        notification = ServicePartRequestNotification(
            request=request_object,
            request_item=request_item,
            recipient=recipient,
            notification_type=notification_type,
            channel=channel,
            title=str(title or "").strip(),
            message=str(message or "").strip(),
            action_url=str(action_url or "").strip(),
            metadata=metadata or {},
        )

        return save_validated(
            notification,
            user=created_by,
            creating=True,
        )

    @classmethod
    def notify_users(
        cls,
        *,
        request_object,
        recipients,
        notification_type,
        title,
        message,
        request_item=None,
        channel=None,
        action_url="",
        metadata=None,
        created_by=None,
    ):
        created = []

        seen = set()

        for recipient in recipients:
            if not recipient:
                continue

            recipient_id = getattr(recipient, "pk", None)

            if recipient_id in seen:
                continue

            seen.add(recipient_id)

            notification = cls.create(
                request_object=request_object,
                request_item=request_item,
                recipient=recipient,
                notification_type=notification_type,
                title=title,
                message=message,
                channel=channel,
                action_url=action_url,
                metadata=metadata,
                created_by=created_by,
            )

            if notification:
                created.append(notification)

        return created

    @classmethod
    @transaction.atomic
    def mark_sent(
        cls,
        notification,
        *,
        external_reference="",
        user=None,
    ):
        notification.delivery_status = (
            ServicePartRequestNotification
            .DeliveryStatus
            .SENT
        )
        notification.external_reference = str(
            external_reference or ""
        ).strip()

        return save_validated(
            notification,
            user=user,
        )

    @classmethod
    @transaction.atomic
    def mark_failed(
        cls,
        notification,
        *,
        reason,
        user=None,
    ):
        notification.delivery_status = (
            ServicePartRequestNotification
            .DeliveryStatus
            .FAILED
        )
        notification.failure_reason = str(
            reason or ""
        ).strip()
        notification.retry_count += 1

        return save_validated(
            notification,
            user=user,
        )
