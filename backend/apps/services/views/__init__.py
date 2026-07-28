# -*- coding: utf-8 -*-
from .service_order import ServiceOrderViewSet
from .service_resources import (
    ServiceAssignmentHistoryViewSet,
    ServiceChecklistItemViewSet,
    ServiceChecklistViewSet,
    ServiceEvidenceViewSet,
    ServiceMeterReadingViewSet,
    ServiceStatusHistoryViewSet,
    ServiceTrackingPointViewSet,
    ServiceTrackingSessionViewSet,
)
from .service_part_request import ServicePartRequestViewSet
from .service_part_request_item import ServicePartRequestItemViewSet
from .service_part_request_history import ServicePartRequestStatusHistoryViewSet
from .service_part_request_information import ServicePartRequestInformationViewSet
from .service_reusable_part import ServiceReusablePartViewSet
from .service_reusable_part_history import ServiceReusablePartHistoryViewSet
from .service_part_transfer import ServicePartTransferViewSet
from .service_part_transfer_history import ServicePartTransferHistoryViewSet
from .service_part_stock_review import ServicePartStockReviewViewSet
from .service_part_stock_review_history import ServicePartStockReviewHistoryViewSet
from .service_part_request_decision import ServicePartRequestDecisionViewSet
from .service_part_request_attachment import ServicePartRequestAttachmentViewSet
from .service_part_request_comment import ServicePartRequestCommentViewSet
from .service_part_request_notification import ServicePartRequestNotificationViewSet
from .service_installation_item import ServiceInstallationItemViewSet
from .equipment_installed_item import EquipmentInstalledItemViewSet

__all__ = (
    "ServiceOrderViewSet",
    "ServiceAssignmentHistoryViewSet",
    "ServiceStatusHistoryViewSet",
    "ServiceTrackingSessionViewSet",
    "ServiceTrackingPointViewSet",
    "ServiceChecklistViewSet",
    "ServiceChecklistItemViewSet",
    "ServiceEvidenceViewSet",
    "ServiceMeterReadingViewSet",
    "ServicePartRequestViewSet",
    "ServicePartRequestItemViewSet",
    "ServicePartRequestStatusHistoryViewSet",
    "ServicePartRequestInformationViewSet",
    "ServiceReusablePartViewSet",
    "ServiceReusablePartHistoryViewSet",
    "ServicePartTransferViewSet",
    "ServicePartTransferHistoryViewSet",
    "ServicePartStockReviewViewSet",
    "ServicePartStockReviewHistoryViewSet",
    "ServicePartRequestDecisionViewSet",
    "ServicePartRequestAttachmentViewSet",
    "ServicePartRequestCommentViewSet",
    "ServicePartRequestNotificationViewSet",
    "ServiceInstallationItemViewSet",
    "EquipmentInstalledItemViewSet",
)
