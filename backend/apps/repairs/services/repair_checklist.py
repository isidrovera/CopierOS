# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.equipment.models import (
    ComponentCompatibility,
    ComponentType,
)

from ..models import (
    RepairChecklist,
    RepairChecklistItem,
)


DEFAULT_GENERAL_ITEMS = (
    {
        "code": "GENERAL-001",
        "name": "Limpieza general del equipo",
        "category": RepairChecklistItem.Category.CLEANING,
        "description": (
            "Verificar el estado general de limpieza "
            "interna y externa del equipo."
        ),
        "instructions": (
            "Revisar polvo, residuos de tóner, manchas, "
            "suciedad y partes contaminadas."
        ),
        "is_required": True,
        "requires_photo": True,
        "requires_observation": False,
        "display_order": 10,
    },
    {
        "code": "GENERAL-002",
        "name": "Estado físico exterior",
        "category": RepairChecklistItem.Category.EXTERNAL,
        "description": (
            "Revisar tapas, bandejas, bisagras, seguros "
            "y partes exteriores."
        ),
        "instructions": (
            "Registrar golpes, roturas, faltantes "
            "o piezas mal colocadas."
        ),
        "is_required": True,
        "requires_photo": True,
        "requires_observation": False,
        "display_order": 20,
    },
    {
        "code": "GENERAL-003",
        "name": "Encendido y panel de control",
        "category": RepairChecklistItem.Category.ELECTRICAL,
        "description": (
            "Comprobar que el equipo encienda correctamente "
            "y que el panel responda."
        ),
        "instructions": (
            "Revisar pantalla, botones, indicadores, sonidos "
            "y mensajes de error."
        ),
        "is_required": True,
        "requires_photo": False,
        "requires_observation": False,
        "display_order": 30,
    },
    {
        "code": "GENERAL-004",
        "name": "Sistema de alimentación de papel",
        "category": RepairChecklistItem.Category.PAPER_FEED,
        "description": (
            "Revisar bandejas, sensores, rodillos "
            "y alimentación de papel."
        ),
        "instructions": (
            "Realizar pruebas desde cada bandeja disponible."
        ),
        "is_required": True,
        "requires_photo": False,
        "requires_observation": False,
        "display_order": 40,
    },
    {
        "code": "GENERAL-005",
        "name": "Sistema de salida de papel",
        "category": RepairChecklistItem.Category.MECHANICAL,
        "description": (
            "Verificar la salida correcta del papel "
            "y la ausencia de atascos."
        ),
        "instructions": (
            "Revisar rodillos de salida, sensores "
            "y bandejas de recepción."
        ),
        "is_required": True,
        "requires_photo": False,
        "requires_observation": False,
        "display_order": 50,
    },
    {
        "code": "GENERAL-006",
        "name": "Calidad de impresión",
        "category": RepairChecklistItem.Category.PRINT_QUALITY,
        "description": (
            "Comprobar la calidad de impresión "
            "en blanco y negro y color cuando corresponda."
        ),
        "instructions": (
            "Revisar manchas, líneas, fondo, densidad, "
            "registro y uniformidad."
        ),
        "is_required": True,
        "requires_photo": True,
        "requires_observation": False,
        "display_order": 60,
    },
    {
        "code": "GENERAL-007",
        "name": "Calidad de copia",
        "category": RepairChecklistItem.Category.PRINT_QUALITY,
        "description": (
            "Comprobar la calidad de copia desde el cristal "
            "y alimentador automático."
        ),
        "instructions": (
            "Revisar nitidez, sombras, líneas, reducción, "
            "ampliación y alimentación de originales."
        ),
        "is_required": True,
        "requires_photo": True,
        "requires_observation": False,
        "display_order": 70,
    },
    {
        "code": "GENERAL-008",
        "name": "Escáner y alimentador de documentos",
        "category": RepairChecklistItem.Category.SCANNING,
        "description": (
            "Verificar el escáner, cristal y alimentador "
            "automático de documentos."
        ),
        "instructions": (
            "Realizar pruebas de una cara, dúplex "
            "y diferentes tamaños cuando corresponda."
        ),
        "is_required": True,
        "requires_photo": False,
        "requires_observation": False,
        "display_order": 80,
    },
    {
        "code": "GENERAL-009",
        "name": "Conectividad de red",
        "category": RepairChecklistItem.Category.NETWORK,
        "description": (
            "Revisar conexión de red, dirección IP "
            "y comunicación con el equipo."
        ),
        "instructions": (
            "Comprobar ping, página web interna, impresión "
            "de red y SNMP cuando esté disponible."
        ),
        "is_required": True,
        "requires_photo": False,
        "requires_observation": False,
        "display_order": 90,
    },
    {
        "code": "GENERAL-010",
        "name": "Contadores del equipo",
        "category": RepairChecklistItem.Category.GENERAL,
        "description": (
            "Registrar los contadores disponibles "
            "antes de finalizar la revisión."
        ),
        "instructions": (
            "Registrar contador total, blanco y negro, color, "
            "escaneo y otros disponibles."
        ),
        "is_required": True,
        "requires_photo": True,
        "requires_observation": False,
        "display_order": 100,
    },
    {
        "code": "GENERAL-011",
        "name": "Códigos y alertas activas",
        "category": RepairChecklistItem.Category.OTHER,
        "description": (
            "Revisar códigos de error, advertencias "
            "y alertas activas."
        ),
        "instructions": (
            "Registrar cualquier código o alerta pendiente "
            "antes de completar la reparación."
        ),
        "is_required": True,
        "requires_photo": True,
        "requires_observation": True,
        "display_order": 110,
    },
    {
        "code": "GENERAL-012",
        "name": "Prueba final de funcionamiento",
        "category": RepairChecklistItem.Category.GENERAL,
        "description": (
            "Realizar una prueba completa del equipo "
            "después del trabajo técnico."
        ),
        "instructions": (
            "Comprobar funcionamiento continuo, calidad, "
            "alimentación y ausencia de errores."
        ),
        "is_required": True,
        "requires_photo": True,
        "requires_observation": False,
        "display_order": 120,
    },
)


def normalize_text(value):
    return str(
        value or ""
    ).strip()


def build_component_item_code(
    component,
):
    component_code = normalize_text(
        getattr(
            component,
            "code",
            "",
        )
    ).upper()

    if component_code:
        return f"COMP-{component_code}"

    return (
        "COMP-"
        f"{str(component.pk).replace('-', '').upper()[:12]}"
    )


def build_component_item_name(
    component,
):
    component_name = normalize_text(
        getattr(
            component,
            "name",
            "",
        )
    )

    if component_name:
        return component_name

    return "Componente técnico"


def validate_checklist_editable(
    checklist,
):
    if checklist.archived_at is not None:
        raise ValidationError(
            "La lista de revisión está archivada."
        )

    if not checklist.repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )

    if (
        checklist.status
        == RepairChecklist.Status.COMPLETED
    ):
        raise ValidationError(
            "La lista de revisión ya está completada."
        )


def update_repair_checklist_state(
    repair,
    actor=None,
):
    main_checklist = (
        RepairChecklist.objects.filter(
            repair=repair,
            is_main_checklist=True,
            archived_at__isnull=True,
        )
        .order_by("-created_at")
        .first()
    )

    completed = bool(
        main_checklist
        and (
            main_checklist.status
            == RepairChecklist.Status.COMPLETED
        )
    )

    if repair.checklist_completed != completed:
        repair.checklist_completed = completed

        if actor:
            repair.updated_by = actor

        repair.save(
            update_fields=[
                "checklist_completed",
                "updated_by",
                "updated_at",
            ]
        )

    return completed


@transaction.atomic
def create_main_checklist(
    *,
    repair,
    actor=None,
    name="Lista principal de revisión",
    description="",
    include_general_items=True,
    include_compatible_components=True,
):
    repair = (
        repair.__class__.objects
        .select_for_update()
        .select_related(
            "equipment",
        )
        .get(pk=repair.pk)
    )

    if repair.archived_at is not None:
        raise ValidationError(
            "La reparación está archivada."
        )

    if not repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )

    existing_checklist = (
        RepairChecklist.objects
        .select_for_update()
        .filter(
            repair=repair,
            is_main_checklist=True,
            archived_at__isnull=True,
        )
        .first()
    )

    if existing_checklist:
        raise ValidationError(
            {
                "repair": (
                    "La reparación ya tiene una "
                    "lista principal de revisión."
                )
            }
        )

    checklist = RepairChecklist(
        repair=repair,
        name=(
            normalize_text(name)
            or "Lista principal de revisión"
        ),
        description=normalize_text(
            description
        ),
        status=RepairChecklist.Status.PENDING,
        is_main_checklist=True,
        created_by=actor,
        updated_by=actor,
    )

    checklist.full_clean()
    checklist.save()

    if include_general_items:
        create_general_checklist_items(
            checklist=checklist,
            actor=actor,
        )

    if include_compatible_components:
        create_compatible_component_items(
            checklist=checklist,
            actor=actor,
        )

    update_repair_checklist_state(
        repair,
        actor,
    )

    return checklist


@transaction.atomic
def create_general_checklist_items(
    *,
    checklist,
    actor=None,
):
    checklist = (
        RepairChecklist.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=checklist.pk)
    )

    validate_checklist_editable(
        checklist
    )

    created_items = []

    for item_data in DEFAULT_GENERAL_ITEMS:
        item, created = (
            RepairChecklistItem.objects
            .get_or_create(
                checklist=checklist,
                code=item_data["code"],
                defaults={
                    **item_data,
                    "created_by": actor,
                    "updated_by": actor,
                },
            )
        )

        if created:
            created_items.append(
                item
            )

    return created_items


@transaction.atomic
def create_compatible_component_items(
    *,
    checklist,
    actor=None,
):
    checklist = (
        RepairChecklist.objects
        .select_for_update()
        .select_related(
            "repair",
            "repair__equipment",
            "repair__equipment__equipment_model",
        )
        .get(pk=checklist.pk)
    )

    validate_checklist_editable(
        checklist
    )

    equipment = checklist.repair.equipment

    equipment_model = getattr(
        equipment,
        "equipment_model",
        None,
    )

    if not equipment_model:
        return []

    equipment_model_id = (
        equipment_model.pk
    )

    equipment_family_id = getattr(
        equipment_model,
        "equipment_family_id",
        None,
    )

    compatibility_filter = Q(
        equipment_model_id=equipment_model_id,
    )

    if equipment_family_id:
        compatibility_filter |= Q(
            equipment_family_id=(
                equipment_family_id
            ),
        )

    allowed_categories = (
        ComponentType.Category.TECHNICAL_UNIT,
        ComponentType.Category.ACCESSORY,
    )

    compatibilities = (
        ComponentCompatibility.objects
        .filter(
            compatibility_filter,
            archived_at__isnull=True,
            is_active=True,
            component__archived_at__isnull=True,
            component__is_active=True,
            component__parent_component__isnull=True,
            component__component_type__archived_at__isnull=True,
            component__component_type__is_active=True,
            component__component_type__category__in=(
                allowed_categories
            ),
        )
        .select_related(
            "component",
            "component__component_type",
            "equipment_family",
            "equipment_model",
        )
        .order_by(
            "-is_preferred",
            "display_order",
            "component__display_order",
            "component__component_type__display_order",
            "component__name",
        )
    )

    current_order = (
        checklist.items.filter(
            archived_at__isnull=True,
        )
        .order_by(
            "-display_order"
        )
        .values_list(
            "display_order",
            flat=True,
        )
        .first()
        or 0
    )

    existing_component_ids = set(
        checklist.items.filter(
            archived_at__isnull=True,
            component_id__isnull=False,
        ).values_list(
            "component_id",
            flat=True,
        )
    )

    processed_component_ids = set()
    created_items = []

    for compatibility in compatibilities:
        component = compatibility.component

        if not component:
            continue

        if component.parent_component_id:
            continue

        component_type = getattr(
            component,
            "component_type",
            None,
        )

        if not component_type:
            continue

        if (
            component_type.category
            not in allowed_categories
        ):
            continue

        if component.pk in processed_component_ids:
            continue

        processed_component_ids.add(
            component.pk
        )

        if component.pk in existing_component_ids:
            continue

        current_order += 10

        code = build_component_item_code(
            component
        )

        compatibility_target = (
            "la familia del equipo"
            if compatibility.equipment_family_id
            else "el modelo del equipo"
        )

        item, created = (
            RepairChecklistItem.objects
            .get_or_create(
                checklist=checklist,
                code=code,
                defaults={
                    "component": component,
                    "name": build_component_item_name(
                        component
                    ),
                    "category": (
                        RepairChecklistItem
                        .Category
                        .COMPONENT
                    ),
                    "description": (
                        "Revisión de la unidad compatible "
                        f"con {compatibility_target}."
                    ),
                    "instructions": (
                        "Revisar condición, desgaste, limpieza, "
                        "funcionamiento y necesidad de cambio."
                    ),
                    "status": (
                        RepairChecklistItem
                        .Status
                        .PENDING
                    ),
                    "is_required": bool(
                        getattr(
                            compatibility,
                            "is_required",
                            False,
                        )
                    ),
                    "requires_photo": False,
                    "requires_observation": False,
                    "display_order": current_order,
                    "created_by": actor,
                    "updated_by": actor,
                },
            )
        )

        if created:
            existing_component_ids.add(
                component.pk
            )

            created_items.append(
                item
            )

    return created_items


@transaction.atomic
def start_checklist(
    *,
    checklist,
    actor=None,
    observations="",
):
    checklist = (
        RepairChecklist.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=checklist.pk)
    )

    validate_checklist_editable(
        checklist
    )

    if (
        checklist.status
        != RepairChecklist.Status.PENDING
    ):
        raise ValidationError(
            {
                "status": (
                    "Solo una lista pendiente puede iniciarse."
                )
            }
        )

    checklist.status = (
        RepairChecklist.Status.IN_PROGRESS
    )
    checklist.started_by = actor
    checklist.started_at = timezone.now()

    observation_text = normalize_text(
        observations
    )

    if observation_text:
        checklist.observations = (
            observation_text
        )

    checklist.updated_by = actor
    checklist.full_clean()
    checklist.save()

    update_repair_checklist_state(
        checklist.repair,
        actor,
    )

    return checklist


@transaction.atomic
def review_checklist_item(
    *,
    item,
    status,
    actor=None,
    observation="",
):
    item = (
        RepairChecklistItem.objects
        .select_for_update()
        .select_related(
            "checklist",
            "checklist__repair",
        )
        .get(pk=item.pk)
    )

    validate_checklist_editable(
        item.checklist
    )

    valid_statuses = {
        value
        for value, _label
        in RepairChecklistItem.Status.choices
    }

    if status not in valid_statuses:
        raise ValidationError(
            {
                "status": (
                    "El resultado seleccionado no es válido."
                )
            }
        )

    if status == RepairChecklistItem.Status.PENDING:
        raise ValidationError(
            {
                "status": (
                    "Debes registrar un resultado "
                    "para el punto revisado."
                )
            }
        )

    observation_text = normalize_text(
        observation
    )

    if (
        status == RepairChecklistItem.Status.FAILED
        and not observation_text
    ):
        raise ValidationError(
            {
                "observation": (
                    "Debes describir la falla encontrada."
                )
            }
        )

    if (
        status
        == RepairChecklistItem.Status.NOT_APPLICABLE
        and item.is_required
        and not observation_text
    ):
        raise ValidationError(
            {
                "observation": (
                    "Debes indicar por qué el punto "
                    "obligatorio no aplica."
                )
            }
        )

    if (
        item.requires_observation
        and status in (
            RepairChecklistItem.Status.OBSERVED,
            RepairChecklistItem.Status.FAILED,
        )
        and not observation_text
    ):
        raise ValidationError(
            {
                "observation": (
                    "Debes registrar una observación."
                )
            }
        )

    if (
        item.checklist.status
        == RepairChecklist.Status.PENDING
    ):
        item.checklist.status = (
            RepairChecklist.Status.IN_PROGRESS
        )
        item.checklist.started_by = actor
        item.checklist.started_at = timezone.now()
        item.checklist.updated_by = actor

        item.checklist.save(
            update_fields=[
                "status",
                "started_by",
                "started_at",
                "updated_by",
                "updated_at",
            ]
        )

    item.status = status
    item.observation = observation_text
    item.checked_by = actor
    item.checked_at = timezone.now()
    item.updated_by = actor

    item.full_clean()
    item.save()

    update_repair_checklist_state(
        item.checklist.repair,
        actor,
    )

    return item


@transaction.atomic
def complete_checklist(
    *,
    checklist,
    actor=None,
    observations="",
):
    checklist = (
        RepairChecklist.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=checklist.pk)
    )

    validate_checklist_editable(
        checklist
    )

    if actor is None:
        raise ValidationError(
            {
                "completed_by": (
                    "Debe indicar quién completa la lista."
                )
            }
        )

    required_items = checklist.items.filter(
        archived_at__isnull=True,
        is_required=True,
    )

    if not required_items.exists():
        raise ValidationError(
            {
                "items": (
                    "La lista no tiene puntos obligatorios."
                )
            }
        )

    pending_items = required_items.filter(
        status=RepairChecklistItem.Status.PENDING,
    )

    if pending_items.exists():
        raise ValidationError(
            {
                "items": (
                    "Existen puntos obligatorios pendientes."
                )
            }
        )

    failed_items = required_items.filter(
        status=RepairChecklistItem.Status.FAILED,
    )

    if failed_items.exists():
        raise ValidationError(
            {
                "items": (
                    "Existen puntos obligatorios con falla."
                )
            }
        )

    observed_items = required_items.filter(
        status=RepairChecklistItem.Status.OBSERVED,
    )

    if observed_items.exists():
        raise ValidationError(
            {
                "items": (
                    "Existen puntos obligatorios "
                    "con observaciones pendientes."
                )
            }
        )

    not_applicable_without_notes = (
        required_items.filter(
            status=(
                RepairChecklistItem
                .Status
                .NOT_APPLICABLE
            ),
            observation="",
        )
    )

    if not_applicable_without_notes.exists():
        raise ValidationError(
            {
                "items": (
                    "Existen puntos obligatorios marcados "
                    "como no aplicables sin explicación."
                )
            }
        )

    required_photo_items = required_items.filter(
        requires_photo=True,
    )

    missing_photo_items = []

    for item in required_photo_items:
        has_photo = item.photos.filter(
            archived_at__isnull=True,
        ).exists()

        if not has_photo:
            missing_photo_items.append(
                item.name
            )

    if missing_photo_items:
        raise ValidationError(
            {
                "items": (
                    "Faltan fotografías en: "
                    + ", ".join(
                        missing_photo_items
                    )
                )
            }
        )

    checklist.status = (
        RepairChecklist.Status.COMPLETED
    )
    checklist.completed_by = actor
    checklist.completed_at = timezone.now()

    observation_text = normalize_text(
        observations
    )

    if observation_text:
        current_observations = normalize_text(
            checklist.observations
        )

        checklist.observations = (
            f"{current_observations}\n"
            f"{observation_text}"
        ).strip()

    checklist.updated_by = actor
    checklist.full_clean()
    checklist.save()

    update_repair_checklist_state(
        checklist.repair,
        actor,
    )

    return checklist


@transaction.atomic
def reopen_checklist(
    *,
    checklist,
    actor=None,
    reason="",
):
    reopening_reason = normalize_text(
        reason
    )

    if not reopening_reason:
        raise ValidationError(
            {
                "reason": (
                    "El motivo de reapertura es obligatorio."
                )
            }
        )

    checklist = (
        RepairChecklist.objects
        .select_for_update()
        .select_related(
            "repair",
        )
        .get(pk=checklist.pk)
    )

    if checklist.archived_at is not None:
        raise ValidationError(
            "La lista de revisión está archivada."
        )

    if not checklist.repair.is_active:
        raise ValidationError(
            "La reparación ya no está activa."
        )

    if (
        checklist.status
        != RepairChecklist.Status.COMPLETED
    ):
        raise ValidationError(
            {
                "status": (
                    "Solo puede reabrirse una lista completada."
                )
            }
        )

    checklist.status = (
        RepairChecklist.Status.IN_PROGRESS
    )
    checklist.completed_by = None
    checklist.completed_at = None
    checklist.observations = (
        f"{normalize_text(checklist.observations)}\n"
        f"Reapertura: {reopening_reason}"
    ).strip()
    checklist.updated_by = actor

    checklist.full_clean()
    checklist.save()

    update_repair_checklist_state(
        checklist.repair,
        actor,
    )

    return checklist