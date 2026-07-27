# -*- coding: utf-8 -*-
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ServiceAssignmentHistoryViewSet,
    ServiceChecklistItemViewSet,
    ServiceChecklistViewSet,
    ServiceEvidenceViewSet,
    ServiceMeterReadingViewSet,
    ServiceOrderViewSet,
    ServicePartRequestItemViewSet,
    ServicePartRequestViewSet,
    ServiceStatusHistoryViewSet,
    ServiceTrackingPointViewSet,
    ServiceTrackingSessionViewSet,
)


router = DefaultRouter()
router.register(
    "orders",
    ServiceOrderViewSet,
    basename="service-order",
)
router.register(
    "assignment-history",
    ServiceAssignmentHistoryViewSet,
    basename="service-assignment-history",
)
router.register(
    "status-history",
    ServiceStatusHistoryViewSet,
    basename="service-status-history",
)
router.register(
    "tracking-sessions",
    ServiceTrackingSessionViewSet,
    basename="service-tracking-session",
)
router.register(
    "tracking-points",
    ServiceTrackingPointViewSet,
    basename="service-tracking-point",
)
router.register(
    "checklists",
    ServiceChecklistViewSet,
    basename="service-checklist",
)
router.register(
    "checklist-items",
    ServiceChecklistItemViewSet,
    basename="service-checklist-item",
)
router.register(
    "part-requests",
    ServicePartRequestViewSet,
    basename="service-part-request",
)
router.register(
    "part-request-items",
    ServicePartRequestItemViewSet,
    basename="service-part-request-item",
)
router.register(
    "evidences",
    ServiceEvidenceViewSet,
    basename="service-evidence",
)
router.register(
    "meter-readings",
    ServiceMeterReadingViewSet,
    basename="service-meter-reading",
)


urlpatterns = [
    path("", include(router.urls)),
]
