# -*- coding: utf-8 -*-

from .common import (
    convert_django_validation_error,
    get_authenticated_user,
    validate_model_instance,
)

from .repair import (
    ArchiveRepairSerializer,
    RepairAssignmentActionSerializer,
    RepairCreateUpdateSerializer,
    RepairDetailSerializer,
    RepairListSerializer,
    RepairStatusChangeSerializer,
)

from .repair_assignment import (
    ArchiveRepairAssignmentSerializer,
    RepairAssignmentAcceptSerializer,
    RepairAssignmentCancelSerializer,
    RepairAssignmentCompleteSerializer,
    RepairAssignmentCreateSerializer,
    RepairAssignmentDetailSerializer,
    RepairAssignmentListSerializer,
    RepairAssignmentReassignSerializer,
    RepairAssignmentRejectSerializer,
    RepairAssignmentStartSerializer,
    RepairAssignmentUpdateSerializer,
)

from .repair_status_history import (
    RepairStatusHistoryDetailSerializer,
    RepairStatusHistoryListSerializer,
)

from .repair_diagnosis import (
    ArchiveRepairDiagnosisSerializer,
    ConfirmRepairDiagnosisSerializer,
    RepairDiagnosisCreateUpdateSerializer,
    RepairDiagnosisDetailSerializer,
    RepairDiagnosisListSerializer,
    SetMainRepairDiagnosisSerializer,
)

from .repair_checklist import (
    ArchiveRepairChecklistItemSerializer,
    ArchiveRepairChecklistSerializer,
    CompleteRepairChecklistSerializer,
    RepairChecklistCreateUpdateSerializer,
    RepairChecklistDetailSerializer,
    RepairChecklistItemCreateUpdateSerializer,
    RepairChecklistItemDetailSerializer,
    RepairChecklistItemListSerializer,
    RepairChecklistListSerializer,
    ReviewRepairChecklistItemSerializer,
    StartRepairChecklistSerializer,
)

from .repair_component import (
    ArchiveRepairComponentSerializer,
    CancelRepairComponentSerializer,
    ConsumeRepairComponentSerializer,
    DeliverRepairComponentSerializer,
    InstallRepairComponentSerializer,
    RepairComponentCreateUpdateSerializer,
    RepairComponentDetailSerializer,
    RepairComponentListSerializer,
    RequestRepairComponentSerializer,
    ReserveRepairComponentSerializer,
    ReturnRepairComponentSerializer,
)

from .repair_photo import (
    ArchiveRepairPhotoSerializer,
    RemoveRepairPhotoVerificationSerializer,
    RepairPhotoCreateUpdateSerializer,
    RepairPhotoDetailSerializer,
    RepairPhotoListSerializer,
    VerifyRepairPhotoSerializer,
)

from .repair_test import (
    ArchiveRepairTestSerializer,
    PerformRepairTestSerializer,
    RepairTestCreateUpdateSerializer,
    RepairTestDetailSerializer,
    RepairTestListSerializer,
    ResetRepairTestSerializer,
)

from .repair_snmp_validation import (
    ArchiveRepairSNMPValidationSerializer,
    CompleteRepairSNMPValidationSerializer,
    FailRepairSNMPValidationSerializer,
    RecalculateSNMPMatchesSerializer,
    RepairSNMPValidationCreateUpdateSerializer,
    RepairSNMPValidationDetailSerializer,
    RepairSNMPValidationListSerializer,
    StartRepairSNMPValidationSerializer,
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
    "get_authenticated_user",
    "convert_django_validation_error",
    "validate_model_instance",

    "RepairListSerializer",
    "RepairDetailSerializer",
    "RepairCreateUpdateSerializer",
    "RepairStatusChangeSerializer",
    "RepairAssignmentActionSerializer",
    "ArchiveRepairSerializer",

    "RepairAssignmentListSerializer",
    "RepairAssignmentDetailSerializer",
    "RepairAssignmentCreateSerializer",
    "RepairAssignmentUpdateSerializer",
    "RepairAssignmentAcceptSerializer",
    "RepairAssignmentStartSerializer",
    "RepairAssignmentCompleteSerializer",
    "RepairAssignmentReassignSerializer",
    "RepairAssignmentRejectSerializer",
    "RepairAssignmentCancelSerializer",
    "ArchiveRepairAssignmentSerializer",

    "RepairStatusHistoryListSerializer",
    "RepairStatusHistoryDetailSerializer",

    "RepairDiagnosisListSerializer",
    "RepairDiagnosisDetailSerializer",
    "RepairDiagnosisCreateUpdateSerializer",
    "ConfirmRepairDiagnosisSerializer",
    "SetMainRepairDiagnosisSerializer",
    "ArchiveRepairDiagnosisSerializer",

    "RepairChecklistListSerializer",
    "RepairChecklistDetailSerializer",
    "RepairChecklistCreateUpdateSerializer",
    "RepairChecklistItemListSerializer",
    "RepairChecklistItemDetailSerializer",
    "RepairChecklistItemCreateUpdateSerializer",
    "StartRepairChecklistSerializer",
    "CompleteRepairChecklistSerializer",
    "ReviewRepairChecklistItemSerializer",
    "ArchiveRepairChecklistSerializer",
    "ArchiveRepairChecklistItemSerializer",

    "RepairComponentListSerializer",
    "RepairComponentDetailSerializer",
    "RepairComponentCreateUpdateSerializer",
    "RequestRepairComponentSerializer",
    "ReserveRepairComponentSerializer",
    "DeliverRepairComponentSerializer",
    "InstallRepairComponentSerializer",
    "ReturnRepairComponentSerializer",
    "ConsumeRepairComponentSerializer",
    "CancelRepairComponentSerializer",
    "ArchiveRepairComponentSerializer",

    "RepairPhotoListSerializer",
    "RepairPhotoDetailSerializer",
    "RepairPhotoCreateUpdateSerializer",
    "VerifyRepairPhotoSerializer",
    "RemoveRepairPhotoVerificationSerializer",
    "ArchiveRepairPhotoSerializer",

    "RepairTestListSerializer",
    "RepairTestDetailSerializer",
    "RepairTestCreateUpdateSerializer",
    "PerformRepairTestSerializer",
    "ResetRepairTestSerializer",
    "ArchiveRepairTestSerializer",

    "RepairSNMPValidationListSerializer",
    "RepairSNMPValidationDetailSerializer",
    "RepairSNMPValidationCreateUpdateSerializer",
    "StartRepairSNMPValidationSerializer",
    "CompleteRepairSNMPValidationSerializer",
    "FailRepairSNMPValidationSerializer",
    "RecalculateSNMPMatchesSerializer",
    "ArchiveRepairSNMPValidationSerializer",
]

__all__ = sorted(set(__all__) | {name for name in globals() if name.endswith("Serializer")})
