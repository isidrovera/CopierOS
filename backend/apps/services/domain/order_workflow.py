# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.services.models import (
    ServiceAssignmentHistory,
    ServiceOrder,
    ServiceStatusHistory,
)


ALLOWED_TRANSITIONS = {
    ServiceOrder.Status.DRAFT: {
        ServiceOrder.Status.PENDING_ASSIGNMENT,
        ServiceOrder.Status.ASSIGNED,
        ServiceOrder.Status.CANCELLED,
    },
    ServiceOrder.Status.PENDING_ASSIGNMENT: {
        ServiceOrder.Status.ASSIGNED,
        ServiceOrder.Status.CANCELLED,
    },
    ServiceOrder.Status.ASSIGNED: {
        ServiceOrder.Status.ACCEPTED,
        ServiceOrder.Status.RESCHEDULED,
        ServiceOrder.Status.CANCELLED,
    },
    ServiceOrder.Status.ACCEPTED: {
        ServiceOrder.Status.EN_ROUTE,
        ServiceOrder.Status.RESCHEDULED,
        ServiceOrder.Status.CANCELLED,
    },
    ServiceOrder.Status.EN_ROUTE: {
        ServiceOrder.Status.ON_SITE,
        ServiceOrder.Status.FAILED_VISIT,
        ServiceOrder.Status.RESCHEDULED,
    },
    ServiceOrder.Status.ON_SITE: {
        ServiceOrder.Status.IN_PROGRESS,
        ServiceOrder.Status.FAILED_VISIT,
    },
    ServiceOrder.Status.IN_PROGRESS: {
        ServiceOrder.Status.PENDING_PARTS,
        ServiceOrder.Status.REQUIRES_RETURN,
        ServiceOrder.Status.TECHNICIAN_COMPLETED,
    },
    ServiceOrder.Status.PENDING_PARTS: {
        ServiceOrder.Status.REQUIRES_RETURN,
        ServiceOrder.Status.TECHNICIAN_COMPLETED,
    },
    ServiceOrder.Status.REQUIRES_RETURN: {
        ServiceOrder.Status.TECHNICIAN_COMPLETED,
        ServiceOrder.Status.CLOSED,
    },
    ServiceOrder.Status.TECHNICIAN_COMPLETED: {
        ServiceOrder.Status.PENDING_CONFORMITY,
        ServiceOrder.Status.CLOSED,
    },
    ServiceOrder.Status.PENDING_CONFORMITY: {
        ServiceOrder.Status.CLOSED,
    },
    ServiceOrder.Status.RESCHEDULED: {
        ServiceOrder.Status.ASSIGNED,
        ServiceOrder.Status.CANCELLED,
    },
    ServiceOrder.Status.FAILED_VISIT: {
        ServiceOrder.Status.RESCHEDULED,
        ServiceOrder.Status.CLOSED,
    },
}


@transaction.atomic
def assign_technician(
    service_order,
    technician,
    assigned_by=None,
    reason="",
):
    previous = service_order.assigned_technician

    if previous and previous.pk == technician.pk:
        raise ValidationError(
            {"assigned_technician": "La OS ya está asignada a este técnico."}
        )

    ServiceAssignmentHistory.objects.create(
        service_order=service_order,
        previous_technician=previous,
        new_technician=technician,
        assigned_by=assigned_by,
        reason=str(reason or "").strip(),
        created_by=assigned_by,
        updated_by=assigned_by,
    )

    service_order.assigned_technician = technician
    service_order.assigned_by = assigned_by
    service_order.assigned_at = timezone.now()

    if service_order.status in {
        ServiceOrder.Status.DRAFT,
        ServiceOrder.Status.PENDING_ASSIGNMENT,
        ServiceOrder.Status.RESCHEDULED,
    }:
        service_order.status = ServiceOrder.Status.ASSIGNED

    service_order.updated_by = assigned_by
    service_order.save()

    return service_order


@transaction.atomic
def change_service_status(
    service_order,
    new_status,
    user=None,
    latitude=None,
    longitude=None,
    source="web",
    notes="",
):
    current_status = service_order.status

    if current_status == new_status:
        return service_order

    allowed = ALLOWED_TRANSITIONS.get(current_status, set())

    if new_status not in allowed:
        raise ValidationError(
            {
                "status": (
                    f"No se permite cambiar de "
                    f"{service_order.get_status_display()} "
                    f"a {dict(ServiceOrder.Status.choices).get(new_status, new_status)}."
                )
            }
        )

    now = timezone.now()

    timestamp_fields = {
        ServiceOrder.Status.ACCEPTED: "accepted_at",
        ServiceOrder.Status.EN_ROUTE: "route_started_at",
        ServiceOrder.Status.ON_SITE: "arrived_at",
        ServiceOrder.Status.IN_PROGRESS: "service_started_at",
        ServiceOrder.Status.TECHNICIAN_COMPLETED: (
            "technician_completed_at"
        ),
        ServiceOrder.Status.CLOSED: "closed_at",
    }

    timestamp_field = timestamp_fields.get(new_status)

    if timestamp_field and not getattr(service_order, timestamp_field):
        setattr(service_order, timestamp_field, now)

    if new_status == ServiceOrder.Status.REQUIRES_RETURN:
        service_order.requires_return_visit = True

    service_order.status = new_status
    service_order.updated_by = user
    service_order.save()

    ServiceStatusHistory.objects.create(
        service_order=service_order,
        previous_status=current_status,
        new_status=new_status,
        changed_by=user,
        latitude=latitude,
        longitude=longitude,
        source=str(source or "web").strip().lower(),
        notes=str(notes or "").strip(),
        created_by=user,
        updated_by=user,
    )

    return service_order
