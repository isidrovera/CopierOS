# -*- coding: utf-8 -*-

from .rental_warehouse import RentalWarehouseViewSet
from .rental_equipment import RentalEquipmentViewSet
from .rental_equipment_movement import (
    RentalEquipmentMovementViewSet,
)
from .rental_preparation import RentalPreparationViewSet
from .rental_contract import RentalContractViewSet
from .rental_assignment import RentalAssignmentViewSet
from .rental_installation import RentalInstallationViewSet
from .rental_removal import RentalRemovalViewSet
from .rental_replacement import RentalReplacementViewSet
from .rental_document import RentalDocumentViewSet


__all__ = [
    "RentalWarehouseViewSet",
    "RentalEquipmentViewSet",
    "RentalEquipmentMovementViewSet",
    "RentalPreparationViewSet",
    "RentalContractViewSet",
    "RentalAssignmentViewSet",
    "RentalInstallationViewSet",
    "RentalRemovalViewSet",
    "RentalReplacementViewSet",
    "RentalDocumentViewSet",
]