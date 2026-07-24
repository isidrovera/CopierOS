# -*- coding: utf-8 -*-

from .repair_code import (
    build_repair_code,
    generate_repair_code,
)

from .repair_workflow import (
    ALLOWED_STATUS_TRANSITIONS,
    STATUS_TIMESTAMP_FIELDS,
    assign_repair,
    calculate_duration_minutes,
    cancel_repair,
    change_repair_status,
    create_repair,
    get_status_timestamp,
    reopen_completed_repair,
    validate_repair_closure,
    validate_status_transition,
)

from .repair_assignment import (
    accept_repair_assignment,
    archive_repair_assignment,
    cancel_repair_assignment,
    complete_repair_assignment,
    create_repair_assignment,
    reassign_repair_assignment,
    reject_repair_assignment,
    restore_repair_assignment,
    start_repair_assignment,
)

from .repair_diagnosis import (
    archive_repair_diagnosis,
    confirm_repair_diagnosis,
    create_repair_diagnosis,
    restore_repair_diagnosis,
    set_main_repair_diagnosis,
    update_repair_diagnosis,
    update_repair_requirements,
    validate_diagnosis_available,
)

from .repair_checklist import (
    DEFAULT_GENERAL_ITEMS,
    complete_checklist,
    create_compatible_component_items,
    create_general_checklist_items,
    create_main_checklist,
    reopen_checklist,
    review_checklist_item,
    start_checklist,
    update_repair_checklist_state,
    validate_checklist_editable,
)

from .repair_inventory import (
    cancel_component_request,
    consume_component,
    deliver_component,
    install_component,
    request_component,
    reserve_component,
    return_component,
    validate_inventory_component,
    validate_repair_component_active,
)

from .repair_photo import (
    archive_repair_photo,
    create_repair_photo,
    remove_photo_verification,
    restore_repair_photo,
    update_repair_photo_state,
    validate_photo_available,
    verify_repair_photo,
)

from .repair_test import (
    archive_repair_test,
    create_repair_test,
    perform_repair_test,
    remove_repair_test_verification,
    reset_repair_test,
    restore_repair_test,
    update_repair_test_state,
    validate_test_available,
    verify_repair_test,
)

from .repair_snmp import (
    archive_snmp_validation,
    complete_snmp_validation,
    create_snmp_validation,
    fail_snmp_validation,
    recalculate_snmp_matches,
    reset_snmp_validation,
    restore_snmp_validation,
    start_snmp_validation,
    update_repair_snmp_state,
    validate_snmp_available,
)
from .repair_component_lifecycle import (
    archive_repair_component,
    restore_repair_component,
)
__all__ = [
    "build_repair_code",
    "generate_repair_code",

    "STATUS_TIMESTAMP_FIELDS",
    "ALLOWED_STATUS_TRANSITIONS",
    "get_status_timestamp",
    "calculate_duration_minutes",
    "validate_status_transition",
    "validate_repair_closure",
    "create_repair",
    "assign_repair",
    "change_repair_status",
    "cancel_repair",
    "reopen_completed_repair",

    "create_repair_assignment",
    "accept_repair_assignment",
    "start_repair_assignment",
    "complete_repair_assignment",
    "reassign_repair_assignment",
    "reject_repair_assignment",
    "cancel_repair_assignment",
    "archive_repair_assignment",
    "restore_repair_assignment",

    "validate_diagnosis_available",
    "update_repair_requirements",
    "create_repair_diagnosis",
    "confirm_repair_diagnosis",
    "set_main_repair_diagnosis",
    "update_repair_diagnosis",
    "archive_repair_diagnosis",
    "restore_repair_diagnosis",

    "DEFAULT_GENERAL_ITEMS",
    "validate_checklist_editable",
    "update_repair_checklist_state",
    "create_main_checklist",
    "create_general_checklist_items",
    "create_compatible_component_items",
    "start_checklist",
    "review_checklist_item",
    "complete_checklist",
    "reopen_checklist",

    "validate_repair_component_active",
    "validate_inventory_component",
    "request_component",
    "reserve_component",
    "deliver_component",
    "install_component",
    "consume_component",
    "return_component",
    "cancel_component_request",

    "validate_photo_available",
    "update_repair_photo_state",
    "create_repair_photo",
    "verify_repair_photo",
    "remove_photo_verification",
    "archive_repair_photo",
    "restore_repair_photo",

    "validate_test_available",
    "update_repair_test_state",
    "create_repair_test",
    "perform_repair_test",
    "verify_repair_test",
    "remove_repair_test_verification",
    "reset_repair_test",
    "archive_repair_test",
    "restore_repair_test",

    "validate_snmp_available",
    "update_repair_snmp_state",
    "create_snmp_validation",
    "start_snmp_validation",
    "complete_snmp_validation",
    "fail_snmp_validation",
    "recalculate_snmp_matches",
    "reset_snmp_validation",
    "archive_snmp_validation",
    "restore_snmp_validation",
    "archive_repair_component",
    "restore_repair_component",
]