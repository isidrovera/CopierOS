# -*- coding: utf-8 -*-

from .base import RentalsBaseModel
from .rental_warehouse import RentalWarehouse
from .rental_equipment import RentalEquipment
from .rental_equipment_movement import RentalEquipmentMovement
from .rental_preparation import RentalPreparation
from .rental_contract import RentalContract
from .rental_contract_equipment import RentalContractEquipment
from .rental_assignment import RentalAssignment
from .rental_installation import RentalInstallation
from .rental_removal import RentalRemoval
from .rental_replacement import RentalReplacement
from .rental_document import RentalDocument


__all__ = [
    "RentalsBaseModel",
    "RentalWarehouse",
    "RentalEquipment",
    "RentalEquipmentMovement",
    "RentalPreparation",
    "RentalContract",
    "RentalContractEquipment",
    "RentalAssignment",
    "RentalInstallation",
    "RentalRemoval",
    "RentalReplacement",
    "RentalDocument",
]