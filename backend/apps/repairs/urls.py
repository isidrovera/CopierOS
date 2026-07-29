# -*- coding: utf-8 -*-
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import *

app_name = "repairs"
router = DefaultRouter()

ROUTES = (
    ("repairs", RepairViewSet, "repair"),
    ("assignments", RepairAssignmentViewSet, "repair-assignment"),
    ("status-history", RepairStatusHistoryViewSet, "repair-status-history"),
    ("diagnoses", RepairDiagnosisViewSet, "repair-diagnosis"),
    ("checklists", RepairChecklistViewSet, "repair-checklist"),
    ("checklist-items", RepairChecklistItemViewSet, "repair-checklist-item"),
    ("components", RepairComponentViewSet, "repair-component"),
    ("photos", RepairPhotoViewSet, "repair-photo"),
    ("tests", RepairTestViewSet, "repair-test"),
    ("snmp-validations", RepairSNMPValidationViewSet, "repair-snmp-validation"),
    ("part-requests", RepairPartRequestViewSet, "repair-part-request"),
    ("part-request-items", RepairPartRequestItemViewSet, "repair-part-request-item"),
    ("part-request-reviews", RepairPartRequestReviewViewSet, "repair-part-request-review"),
    ("part-request-decisions", RepairPartRequestDecisionViewSet, "repair-part-request-decision"),
    ("part-sources", RepairPartSourceViewSet, "repair-part-source"),
    ("part-withdrawals", RepairPartWithdrawalViewSet, "repair-part-withdrawal"),
    ("part-deliveries", RepairPartDeliveryViewSet, "repair-part-delivery"),
    ("part-replacements", RepairPartReplacementViewSet, "repair-part-replacement"),
    ("part-request-history", RepairPartRequestHistoryViewSet, "repair-part-request-history"),
    ("part-request-comments", RepairPartRequestCommentViewSet, "repair-part-request-comment"),
    ("part-request-attachments", RepairPartRequestAttachmentViewSet, "repair-part-request-attachment"),
    ("part-request-notifications", RepairPartRequestNotificationViewSet, "repair-part-request-notification"),
)
for prefix, viewset, basename in ROUTES:
    router.register(prefix, viewset, basename=basename)
urlpatterns = [path("", include(router.urls))]
