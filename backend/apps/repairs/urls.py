# -*- coding: utf-8 -*-
from django.urls import (
    include,
    path,
)
from rest_framework.routers import DefaultRouter

from .views import (
    RepairAssignmentViewSet,
    RepairChecklistItemViewSet,
    RepairChecklistViewSet,
    RepairComponentViewSet,
    RepairDiagnosisViewSet,
    RepairPhotoViewSet,
    RepairSNMPValidationViewSet,
    RepairStatusHistoryViewSet,
    RepairTestViewSet,
    RepairViewSet,
)


app_name = "repairs"


router = DefaultRouter()

router.register(
    r"repairs",
    RepairViewSet,
    basename="repair",
)

router.register(
    r"assignments",
    RepairAssignmentViewSet,
    basename="repair-assignment",
)

router.register(
    r"status-history",
    RepairStatusHistoryViewSet,
    basename="repair-status-history",
)

router.register(
    r"diagnoses",
    RepairDiagnosisViewSet,
    basename="repair-diagnosis",
)

router.register(
    r"checklists",
    RepairChecklistViewSet,
    basename="repair-checklist",
)

router.register(
    r"checklist-items",
    RepairChecklistItemViewSet,
    basename="repair-checklist-item",
)

router.register(
    r"components",
    RepairComponentViewSet,
    basename="repair-component",
)

router.register(
    r"photos",
    RepairPhotoViewSet,
    basename="repair-photo",
)

router.register(
    r"tests",
    RepairTestViewSet,
    basename="repair-test",
)

router.register(
    r"snmp-validations",
    RepairSNMPValidationViewSet,
    basename="repair-snmp-validation",
)


urlpatterns = [
    path(
        "",
        include(router.urls),
    ),
]