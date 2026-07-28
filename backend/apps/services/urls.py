# -*- coding: utf-8 -*-
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EquipmentInstalledItemViewSet,
    ServiceAssignmentHistoryViewSet,
    ServiceChecklistItemViewSet,
    ServiceChecklistViewSet,
    ServiceEvidenceViewSet,
    ServiceInstallationItemViewSet,
    ServiceMeterReadingViewSet,
    ServiceOrderViewSet,
    ServicePartRequestAttachmentViewSet,
    ServicePartRequestCommentViewSet,
    ServicePartRequestDecisionViewSet,
    ServicePartRequestInformationViewSet,
    ServicePartRequestItemViewSet,
    ServicePartRequestNotificationViewSet,
    ServicePartRequestStatusHistoryViewSet,
    ServicePartRequestViewSet,
    ServicePartStockReviewHistoryViewSet,
    ServicePartStockReviewViewSet,
    ServicePartTransferHistoryViewSet,
    ServicePartTransferViewSet,
    ServiceReusablePartHistoryViewSet,
    ServiceReusablePartViewSet,
    ServiceStatusHistoryViewSet,
    ServiceTrackingPointViewSet,
    ServiceTrackingSessionViewSet,
)

app_name = "services"

router = DefaultRouter()

router.register("orders", ServiceOrderViewSet, basename="service-order")
router.register("assignment-history", ServiceAssignmentHistoryViewSet, basename="service-assignment-history")
router.register("status-history", ServiceStatusHistoryViewSet, basename="service-status-history")
router.register("tracking-sessions", ServiceTrackingSessionViewSet, basename="service-tracking-session")
router.register("tracking-points", ServiceTrackingPointViewSet, basename="service-tracking-point")
router.register("checklists", ServiceChecklistViewSet, basename="service-checklist")
router.register("checklist-items", ServiceChecklistItemViewSet, basename="service-checklist-item")
router.register("evidences", ServiceEvidenceViewSet, basename="service-evidence")
router.register("meter-readings", ServiceMeterReadingViewSet, basename="service-meter-reading")

router.register("part-requests", ServicePartRequestViewSet, basename="service-part-request")
router.register("part-request-items", ServicePartRequestItemViewSet, basename="service-part-request-item")
router.register("part-request-history", ServicePartRequestStatusHistoryViewSet, basename="service-part-request-history")
router.register("part-request-information", ServicePartRequestInformationViewSet, basename="service-part-request-information")
router.register("part-request-decisions", ServicePartRequestDecisionViewSet, basename="service-part-request-decision")
router.register("part-request-attachments", ServicePartRequestAttachmentViewSet, basename="service-part-request-attachment")
router.register("part-request-comments", ServicePartRequestCommentViewSet, basename="service-part-request-comment")
router.register("part-request-notifications", ServicePartRequestNotificationViewSet, basename="service-part-request-notification")
router.register("part-stock-reviews", ServicePartStockReviewViewSet, basename="service-part-stock-review")
router.register("part-stock-review-history", ServicePartStockReviewHistoryViewSet, basename="service-part-stock-review-history")
router.register("reusable-parts", ServiceReusablePartViewSet, basename="service-reusable-part")
router.register("reusable-part-history", ServiceReusablePartHistoryViewSet, basename="service-reusable-part-history")
router.register("part-transfers", ServicePartTransferViewSet, basename="service-part-transfer")
router.register("part-transfer-history", ServicePartTransferHistoryViewSet, basename="service-part-transfer-history")
router.register("installation-items", ServiceInstallationItemViewSet, basename="service-installation-item")
router.register("installed-item-history", EquipmentInstalledItemViewSet, basename="equipment-installed-item")

urlpatterns = [
    path("", include(router.urls)),
]
