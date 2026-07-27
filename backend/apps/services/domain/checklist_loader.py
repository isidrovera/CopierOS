# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models import Q

from apps.equipment.models import ComponentCompatibility
from apps.services.models import ServiceChecklist, ServiceChecklistItem


@transaction.atomic
def create_service_checklist(service_order, user=None):
    checklist, created = ServiceChecklist.objects.get_or_create(
        service_order=service_order,
        defaults={"created_by": user, "updated_by": user},
    )

    if not created and checklist.items.filter(archived_at__isnull=True).exists():
        return checklist

    model = service_order.equipment.equipment_model
    family_id = getattr(model, "equipment_family_id", None)

    target = Q(equipment_model_id=model.id)
    if family_id:
        target |= Q(equipment_family_id=family_id)

    compatibilities = (
        ComponentCompatibility.objects
        .select_related("component", "component__component_type")
        .filter(
            target,
            is_active=True,
            archived_at__isnull=True,
            component__is_active=True,
            component__archived_at__isnull=True,
            component__parent_component__isnull=True,
        )
        .order_by("component__display_order", "display_order", "component__name")
    )

    selected = {}

    for compatibility in compatibilities:
        key = (compatibility.component_id, compatibility.position)
        current = selected.get(key)

        if current is None:
            selected[key] = compatibility
        elif compatibility.equipment_model_id and not current.equipment_model_id:
            selected[key] = compatibility

    for order, compatibility in enumerate(selected.values(), start=1):
        component = compatibility.component
        component_type = component.component_type

        ServiceChecklistItem.objects.create(
            checklist=checklist,
            source_component=component,
            source_component_id_snapshot=component.id,
            component_code=component.code,
            component_name=component.name,
            component_color=component.color,
            component_type_name=str(component_type),
            category=str(getattr(component_type, "code", "component") or "component").lower(),
            position=compatibility.position,
            is_required=True,
            display_order=order,
            created_by=user,
            updated_by=user,
        )

    return checklist
