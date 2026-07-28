# -*- coding: utf-8 -*-
from .service_order import ServiceOrderListSerializer, ServiceOrderSerializer
from .service_history import ServiceAssignmentHistorySerializer, ServiceStatusHistorySerializer
from .service_tracking import ServiceTrackingPointSerializer, ServiceTrackingSessionSerializer
from .service_checklist import ServiceChecklistItemSerializer, ServiceChecklistSerializer
from .service_evidence_meter import ServiceEvidenceSerializer, ServiceMeterReadingSerializer
from .service_part_request import (
    ArchiveServicePartRequestSerializer,
    ServicePartRequestListSerializer,
    ServicePartRequestSerializer,
    ServicePartRequestStatusChangeSerializer,
)
from .service_part_request_item import (
    ServicePartRequestItemDecisionSerializer,
    ServicePartRequestItemListSerializer,
    ServicePartRequestItemSerializer,
    ServicePartRequestItemSupplySerializer,
)
from .service_part_request_history import ServicePartRequestStatusHistorySerializer
from .service_part_request_information import ServicePartRequestInformationSerializer
from .service_reusable_part import ServiceReusablePartSerializer
from .service_reusable_part_history import ServiceReusablePartHistorySerializer
from .service_part_transfer import ServicePartTransferSerializer
from .service_part_transfer_history import ServicePartTransferHistorySerializer
from .service_part_stock_review import ServicePartStockReviewSerializer
from .service_part_stock_review_history import ServicePartStockReviewHistorySerializer
from .service_part_request_decision import ServicePartRequestDecisionSerializer
from .service_part_request_attachment import ServicePartRequestAttachmentSerializer
from .service_part_request_comment import ServicePartRequestCommentSerializer
from .service_part_request_notification import (
    MarkServicePartRequestNotificationReadSerializer,
    ServicePartRequestNotificationSerializer,
)
from .service_installation_item import ServiceInstallationItemSerializer
from .equipment_installed_item import EquipmentInstalledItemSerializer

__all__ = (
    "ServiceOrderSerializer",
    "ServiceOrderListSerializer",
    "ServiceAssignmentHistorySerializer",
    "ServiceStatusHistorySerializer",
    "ServiceTrackingSessionSerializer",
    "ServiceTrackingPointSerializer",
    "ServiceChecklistSerializer",
    "ServiceChecklistItemSerializer",
    "ServiceEvidenceSerializer",
    "ServiceMeterReadingSerializer",
    "ArchiveServicePartRequestSerializer",
    "ServicePartRequestListSerializer",
    "ServicePartRequestSerializer",
    "ServicePartRequestStatusChangeSerializer",
    "ServicePartRequestItemDecisionSerializer",
    "ServicePartRequestItemListSerializer",
    "ServicePartRequestItemSerializer",
    "ServicePartRequestItemSupplySerializer",
    "ServicePartRequestStatusHistorySerializer",
    "ServicePartRequestInformationSerializer",
    "ServiceReusablePartSerializer",
    "ServiceReusablePartHistorySerializer",
    "ServicePartTransferSerializer",
    "ServicePartTransferHistorySerializer",
    "ServicePartStockReviewSerializer",
    "ServicePartStockReviewHistorySerializer",
    "ServicePartRequestDecisionSerializer",
    "ServicePartRequestAttachmentSerializer",
    "ServicePartRequestCommentSerializer",
    "ServicePartRequestNotificationSerializer",
    "MarkServicePartRequestNotificationReadSerializer",
    "ServiceInstallationItemSerializer",
    "EquipmentInstalledItemSerializer",
)
