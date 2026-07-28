# -*- coding: utf-8 -*-
from django.db import transaction
from django.utils import timezone

from apps.services.models import (
    ServicePartTransfer,
    ServicePartTransferHistory,
    ServiceReusablePart,
    ServiceReusablePartHistory,
)

from .workflow_utils import (
    authenticated_user,
    require,
    save_validated,
)


class PartTransferWorkflow:
    @classmethod
    def _transfer_history(
        cls,
        transfer,
        *,
        event,
        user,
        previous_status="",
        new_status="",
        notes="",
        previous_holder=None,
        new_holder=None,
        previous_location="",
        new_location="",
        previous_condition="",
        new_condition="",
    ):
        history = ServicePartTransferHistory(
            transfer=transfer,
            event=event,
            previous_status=previous_status,
            new_status=new_status,
            performed_by=authenticated_user(user),
            previous_holder=previous_holder,
            new_holder=new_holder,
            previous_location=previous_location,
            new_location=new_location,
            previous_condition=previous_condition,
            new_condition=new_condition,
            source="service",
            notes=str(notes or "").strip(),
        )

        return save_validated(
            history,
            user=user,
            creating=True,
        )

    @classmethod
    def _reusable_history(
        cls,
        reusable_part,
        *,
        event,
        user,
        previous_status="",
        new_status="",
        previous_holder=None,
        new_holder=None,
        previous_location="",
        new_location="",
        previous_condition="",
        new_condition="",
        previous_equipment=None,
        new_equipment=None,
        notes="",
    ):
        history = ServiceReusablePartHistory(
            reusable_part=reusable_part,
            event=event,
            previous_status=previous_status,
            new_status=new_status,
            previous_condition=previous_condition,
            new_condition=new_condition,
            previous_equipment=previous_equipment,
            new_equipment=new_equipment,
            previous_holder=previous_holder,
            new_holder=new_holder,
            previous_location=previous_location,
            new_location=new_location,
            performed_by=authenticated_user(user),
            source="service",
            notes=str(notes or "").strip(),
        )

        return save_validated(
            history,
            user=user,
            creating=True,
        )

    @classmethod
    @transaction.atomic
    def create_transfer(
        cls,
        *,
        request_item,
        reusable_part,
        destination_equipment,
        approved_by,
        removal_technician,
        reception_technician,
        source_equipment=None,
        removal_scheduled_at=None,
        reception_scheduled_at=None,
        notes="",
    ):
        require(
            request_item.supply_method
            in {
                request_item.SupplyMethod.REUSABLE_PART,
                request_item.SupplyMethod.DONOR_EQUIPMENT,
            },
            "El artículo no fue definido como reutilizable o donante.",
            "supply_method",
        )

        source_equipment = (
            source_equipment
            or reusable_part.source_equipment
        )

        transfer = ServicePartTransfer(
            part_request_item=request_item,
            reusable_part=reusable_part,
            source_equipment=source_equipment,
            destination_equipment=destination_equipment,
            status=ServicePartTransfer.Status.APPROVED,
            approved_by=authenticated_user(approved_by),
            approved_at=timezone.now(),
            removal_technician=removal_technician,
            removal_scheduled_at=removal_scheduled_at,
            reception_technician=reception_technician,
            reception_scheduled_at=reception_scheduled_at,
            notes=str(notes or "").strip(),
        )

        save_validated(
            transfer,
            user=approved_by,
            creating=True,
        )

        previous_status = reusable_part.status
        reusable_part.status = (
            ServiceReusablePart.Status.PENDING_REMOVAL
            if source_equipment
            else ServiceReusablePart.Status.RESERVED
        )
        reusable_part.current_holder = None

        save_validated(
            reusable_part,
            user=approved_by,
        )

        cls._transfer_history(
            transfer,
            event=(
                ServicePartTransferHistory.Event.APPROVED
            ),
            user=approved_by,
            new_status=transfer.status,
            notes=notes,
        )

        cls._reusable_history(
            reusable_part,
            event=(
                ServiceReusablePartHistory.Event.RESERVED
            ),
            user=approved_by,
            previous_status=previous_status,
            new_status=reusable_part.status,
            notes=notes,
        )

        return transfer

    @classmethod
    @transaction.atomic
    def assign_removal(
        cls,
        transfer,
        *,
        user,
        technician,
        scheduled_at=None,
        notes="",
    ):
        transfer = (
            ServicePartTransfer.objects
            .select_for_update()
            .get(pk=transfer.pk)
        )

        previous_status = transfer.status
        transfer.status = (
            ServicePartTransfer.Status.ASSIGNED_FOR_REMOVAL
        )
        transfer.removal_technician = technician
        transfer.removal_scheduled_at = scheduled_at

        save_validated(
            transfer,
            user=user,
        )

        cls._transfer_history(
            transfer,
            event=(
                ServicePartTransferHistory
                .Event
                .REMOVAL_ASSIGNED
            ),
            user=user,
            previous_status=previous_status,
            new_status=transfer.status,
            notes=notes,
        )

        return transfer

    @classmethod
    @transaction.atomic
    def register_removal(
        cls,
        transfer,
        *,
        user,
        condition,
        location="",
        notes="",
    ):
        transfer = (
            ServicePartTransfer.objects
            .select_for_update()
            .select_related("reusable_part")
            .get(pk=transfer.pk)
        )

        require(
            transfer.status
            in {
                ServicePartTransfer.Status.APPROVED,
                ServicePartTransfer.Status
                .ASSIGNED_FOR_REMOVAL,
            },
            "La transferencia no está lista para retiro.",
            "status",
        )

        previous_status = transfer.status
        previous_holder = transfer.current_holder
        previous_location = transfer.current_location

        transfer.status = ServicePartTransfer.Status.REMOVED
        transfer.removed_at = timezone.now()
        transfer.removal_condition = condition
        transfer.removal_notes = str(notes or "").strip()
        transfer.handed_over_by = authenticated_user(user)
        transfer.current_holder = transfer.removal_technician
        transfer.current_location = str(location or "").strip()

        save_validated(
            transfer,
            user=user,
        )

        reusable_part = transfer.reusable_part

        if reusable_part:
            reusable_previous_status = reusable_part.status
            reusable_part.status = (
                ServiceReusablePart.Status.IN_CUSTODY
            )
            reusable_part.condition = condition
            reusable_part.removed_from_source_at = (
                transfer.removed_at
            )
            reusable_part.current_holder = (
                transfer.current_holder
            )
            reusable_part.location_name = (
                transfer.current_location
            )

            save_validated(
                reusable_part,
                user=user,
            )

            cls._reusable_history(
                reusable_part,
                event=(
                    ServiceReusablePartHistory.Event.REMOVED
                ),
                user=user,
                previous_status=reusable_previous_status,
                new_status=reusable_part.status,
                previous_holder=previous_holder,
                new_holder=transfer.current_holder,
                previous_location=previous_location,
                new_location=transfer.current_location,
                new_condition=condition,
                previous_equipment=transfer.source_equipment,
                notes=notes,
            )

        cls._transfer_history(
            transfer,
            event=ServicePartTransferHistory.Event.REMOVED,
            user=user,
            previous_status=previous_status,
            new_status=transfer.status,
            previous_holder=previous_holder,
            new_holder=transfer.current_holder,
            previous_location=previous_location,
            new_location=transfer.current_location,
            new_condition=condition,
            notes=notes,
        )

        return transfer

    @classmethod
    @transaction.atomic
    def register_handover(
        cls,
        transfer,
        *,
        user,
        received_by,
        location="",
        notes="",
    ):
        transfer = (
            ServicePartTransfer.objects
            .select_for_update()
            .select_related("reusable_part")
            .get(pk=transfer.pk)
        )

        require(
            transfer.status
            in {
                ServicePartTransfer.Status.REMOVED,
                ServicePartTransfer.Status.IN_TRANSIT,
                ServicePartTransfer.Status.PENDING_RECEPTION,
            },
            "La parte no está disponible para entrega.",
            "status",
        )

        previous_status = transfer.status
        previous_holder = transfer.current_holder
        previous_location = transfer.current_location

        transfer.status = (
            ServicePartTransfer.Status.PENDING_RECEPTION
        )
        transfer.handed_over_by = authenticated_user(user)
        transfer.received_by = received_by
        transfer.current_holder = received_by
        transfer.current_location = str(location or "").strip()

        save_validated(
            transfer,
            user=user,
        )

        if transfer.reusable_part:
            part = transfer.reusable_part
            part.current_holder = received_by
            part.location_name = transfer.current_location

            save_validated(
                part,
                user=user,
            )

        cls._transfer_history(
            transfer,
            event=(
                ServicePartTransferHistory.Event.HANDED_OVER
            ),
            user=user,
            previous_status=previous_status,
            new_status=transfer.status,
            previous_holder=previous_holder,
            new_holder=received_by,
            previous_location=previous_location,
            new_location=transfer.current_location,
            notes=notes,
        )

        return transfer

    @classmethod
    @transaction.atomic
    def register_reception(
        cls,
        transfer,
        *,
        user,
        condition,
        location="",
        notes="",
    ):
        transfer = (
            ServicePartTransfer.objects
            .select_for_update()
            .select_related("reusable_part")
            .get(pk=transfer.pk)
        )

        require(
            transfer.status
            in {
                ServicePartTransfer.Status.PENDING_RECEPTION,
                ServicePartTransfer.Status.IN_TRANSIT,
                ServicePartTransfer.Status.REMOVED,
            },
            "La transferencia no está pendiente de recepción.",
            "status",
        )

        previous_status = transfer.status
        previous_holder = transfer.current_holder
        previous_location = transfer.current_location
        previous_condition = transfer.reception_condition

        transfer.status = ServicePartTransfer.Status.RECEIVED
        transfer.received_at = timezone.now()
        transfer.reception_condition = condition
        transfer.reception_notes = str(notes or "").strip()
        transfer.received_by = authenticated_user(user)
        transfer.current_holder = (
            transfer.reception_technician
            or authenticated_user(user)
        )
        transfer.current_location = str(location or "").strip()

        save_validated(
            transfer,
            user=user,
        )

        if transfer.reusable_part:
            part = transfer.reusable_part
            previous_part_status = part.status
            part.status = (
                ServiceReusablePart
                .Status
                .READY_FOR_INSTALLATION
            )
            part.condition = condition
            part.current_holder = transfer.current_holder
            part.location_name = transfer.current_location

            save_validated(
                part,
                user=user,
            )

            cls._reusable_history(
                part,
                event=(
                    ServiceReusablePartHistory
                    .Event
                    .READY_FOR_INSTALLATION
                ),
                user=user,
                previous_status=previous_part_status,
                new_status=part.status,
                previous_holder=previous_holder,
                new_holder=part.current_holder,
                previous_location=previous_location,
                new_location=part.location_name,
                previous_condition=previous_condition,
                new_condition=condition,
                notes=notes,
            )

        cls._transfer_history(
            transfer,
            event=ServicePartTransferHistory.Event.RECEIVED,
            user=user,
            previous_status=previous_status,
            new_status=transfer.status,
            previous_holder=previous_holder,
            new_holder=transfer.current_holder,
            previous_location=previous_location,
            new_location=transfer.current_location,
            previous_condition=previous_condition,
            new_condition=condition,
            notes=notes,
        )

        return transfer
