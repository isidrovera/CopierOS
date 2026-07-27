# -*- coding: utf-8 -*-
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.rentals.views import (
    RentalAssignmentViewSet,
    RentalContractViewSet,
    RentalDocumentViewSet,
    RentalEquipmentMovementViewSet,
    RentalEquipmentViewSet,
    RentalInstallationViewSet,
    RentalPreparationViewSet,
    RentalRemovalViewSet,
    RentalReplacementViewSet,
    RentalWarehouseViewSet,
)


app_name = "rentals"


router = DefaultRouter()

router.register(
    r"warehouses",
    RentalWarehouseViewSet,
    basename="rental-warehouse",
)

router.register(
    r"equipment",
    RentalEquipmentViewSet,
    basename="rental-equipment",
)

router.register(
    r"equipment-movements",
    RentalEquipmentMovementViewSet,
    basename="rental-equipment-movement",
)

router.register(
    r"preparations",
    RentalPreparationViewSet,
    basename="rental-preparation",
)

router.register(
    r"contracts",
    RentalContractViewSet,
    basename="rental-contract",
)

router.register(
    r"assignments",
    RentalAssignmentViewSet,
    basename="rental-assignment",
)

router.register(
    r"installations",
    RentalInstallationViewSet,
    basename="rental-installation",
)

router.register(
    r"removals",
    RentalRemovalViewSet,
    basename="rental-removal",
)

router.register(
    r"replacements",
    RentalReplacementViewSet,
    basename="rental-replacement",
)

router.register(
    r"documents",
    RentalDocumentViewSet,
    basename="rental-document",
)


urlpatterns = [
    path(
        "",
        include(router.urls),
    ),
]