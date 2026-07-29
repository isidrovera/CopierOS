# -*- coding: utf-8 -*-

from .common import (
    convert_django_validation_error,
    django_validation_error_response,
    execute_service_action,
    get_authenticated_actor,
    get_boolean_query_param,
)

from .repair import RepairViewSet

from .repair_assignment import (
    RepairAssignmentViewSet,
)

from .repair_status_history import (
    RepairStatusHistoryViewSet,
)

from .repair_diagnosis import (
    RepairDiagnosisViewSet,
)

from .repair_checklist import (
    RepairChecklistItemViewSet,
    RepairChecklistViewSet,
)

from .repair_component import (
    RepairComponentViewSet,
)

from .repair_photo import (
    RepairPhotoViewSet,
)

from .repair_test import (
    RepairTestViewSet,
)

from .repair_snmp_validation import (
    RepairSNMPValidationViewSet,
)

from .repair_part_request import *
from .repair_part_request_item import *
from .repair_part_request_review import *
from .repair_part_request_decision import *
from .repair_part_source import *
from .repair_part_withdrawal import *
from .repair_part_delivery import *
from .repair_part_replacement import *
from .repair_part_request_history import *
from .repair_part_request_comment import *
from .repair_part_request_attachment import *
from .repair_part_request_notification import *

__all__ = [
    "convert_django_validation_error",
    "django_validation_error_response",
    "execute_service_action",
    "get_authenticated_actor",
    "get_boolean_query_param",

    "RepairViewSet",
    "RepairAssignmentViewSet",
    "RepairStatusHistoryViewSet",
    "RepairDiagnosisViewSet",
    "RepairChecklistViewSet",
    "RepairChecklistItemViewSet",
    "RepairComponentViewSet",
    "RepairPhotoViewSet",
    "RepairTestViewSet",
    "RepairSNMPValidationViewSet",
]

__all__ = sorted(set(__all__) | {name for name in globals() if name.endswith("ViewSet")})
