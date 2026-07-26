# -*- coding: utf-8 -*-

from .rental_warehouse import (
    RentalWarehouseListSerializer,
    RentalWarehouseSerializer,
)
from .rental_equipment import (
    RentalEquipmentListSerializer,
    RentalEquipmentSerializer,
)
from .rental_equipment_movement import (
    RentalEquipmentMovementListSerializer,
    RentalEquipmentMovementSerializer,
)
from .rental_preparation import (
    RentalPreparationListSerializer,
    RentalPreparationSerializer,
)
from .rental_contract import (
    RentalContractListSerializer,
    RentalContractSerializer,
)
from .rental_contract_equipment import (
    RentalContractEquipmentListSerializer,
    RentalContractEquipmentSerializer,
)
from .rental_assignment import (
    RentalAssignmentListSerializer,
    RentalAssignmentSerializer,
)
from .rental_installation import (
    RentalInstallationListSerializer,
    RentalInstallationSerializer,
)
from .rental_removal import (
    RentalRemovalListSerializer,
    RentalRemovalSerializer,
)
from .rental_replacement import (
    RentalReplacementListSerializer,
    RentalReplacementSerializer,
)
from .rental_document import (
    RentalDocumentListSerializer,
    RentalDocumentSerializer,
)


__all__ = [
    "RentalWarehouseSerializer",
    "RentalWarehouseListSerializer",
    "RentalEquipmentSerializer",
    "RentalEquipmentListSerializer",
    "RentalEquipmentMovementSerializer",
    "RentalEquipmentMovementListSerializer",
    "RentalPreparationSerializer",
    "RentalPreparationListSerializer",
    "RentalContractSerializer",
    "RentalContractListSerializer",
    "RentalContractEquipmentSerializer",
    "RentalContractEquipmentListSerializer",
    "RentalAssignmentSerializer",
    "RentalAssignmentListSerializer",
    "RentalInstallationSerializer",
    "RentalInstallationListSerializer",
    "RentalRemovalSerializer",
    "RentalRemovalListSerializer",
    "RentalReplacementSerializer",
    "RentalReplacementListSerializer",
    "RentalDocumentSerializer",
    "RentalDocumentListSerializer",
]