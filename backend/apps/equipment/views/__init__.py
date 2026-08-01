# -*- coding: utf-8 -*-

from .brand import (
    ArchiveEquipmentBrandView,
    EquipmentBrandDetailUpdateView,
    EquipmentBrandListCreateView,
    RestoreEquipmentBrandView,
)
from .component import (
    ArchiveEquipmentComponentView,
    EquipmentComponentDetailUpdateView,
    EquipmentComponentListCreateView,
    RestoreEquipmentComponentView,
)
from .component_compatibility import (
    ArchiveComponentCompatibilityView,
    ComponentCompatibilityDetailUpdateView,
    ComponentCompatibilityListCreateView,
    RestoreComponentCompatibilityView,
)
from .component_type import (
    ArchiveComponentTypeView,
    ComponentTypeDetailUpdateView,
    ComponentTypeListCreateView,
    RestoreComponentTypeView,
)
from .equipment import (
    ArchiveEquipmentView,
    ChangeEquipmentCommercialStatusView,
    ChangeEquipmentTechnicalStatusView,
    EquipmentDetailUpdateView,
    EquipmentListCreateView,
    RegisterInitialEquipmentMetersView,
    RestoreEquipmentView,
)
from .equipment_component_assignment import (
    EquipmentComponentAssignmentDetailUpdateView,
    EquipmentComponentAssignmentListCreateView,
)
from .equipment_document import (
    ArchiveEquipmentDocumentView,
    EquipmentDocumentDetailUpdateView,
    EquipmentDocumentListCreateView,
    RemoveEquipmentDocumentVerificationView,
    RestoreEquipmentDocumentView,
    VerifyEquipmentDocumentView,
)
from .equipment_family import (
    ArchiveEquipmentFamilyView,
    EquipmentFamilyDetailUpdateView,
    EquipmentFamilyListCreateView,
    RestoreEquipmentFamilyView,
)
from .equipment_model import (
    ArchiveEquipmentModelView,
    EquipmentModelDetailUpdateView,
    EquipmentModelListCreateView,
    RestoreEquipmentModelView,
)
from .equipment_movement import (
    ArchiveEquipmentMovementView,
    EquipmentMovementDetailUpdateView,
    EquipmentMovementListCreateView,
    RestoreEquipmentMovementView,
)
from .equipment_type import (
    ArchiveEquipmentTypeView,
    EquipmentTypeDetailUpdateView,
    EquipmentTypeListCreateView,
    RestoreEquipmentTypeView,
    parse_boolean_query_param,
)
from .import_batch import (
    ArchiveImportBatchView,
    ChangeImportBatchStatusView,
    ImportBatchDetailUpdateView,
    ImportBatchListCreateView,
    RestoreImportBatchView,
)
from .meter_reading import (
    ApplyMeterReadingView,
    ArchiveMeterReadingView,
    MeterReadingDetailUpdateView,
    MeterReadingListCreateView,
    RestoreMeterReadingView,
    VerifyMeterReadingView,
)


__all__ = (
    "parse_boolean_query_param",

    # Tipos de equipos
    "EquipmentTypeListCreateView",
    "EquipmentTypeDetailUpdateView",
    "ArchiveEquipmentTypeView",
    "RestoreEquipmentTypeView",

    # Marcas
    "EquipmentBrandListCreateView",
    "EquipmentBrandDetailUpdateView",
    "ArchiveEquipmentBrandView",
    "RestoreEquipmentBrandView",

    # Familias
    "EquipmentFamilyListCreateView",
    "EquipmentFamilyDetailUpdateView",
    "ArchiveEquipmentFamilyView",
    "RestoreEquipmentFamilyView",

    # Modelos de equipos
    "EquipmentModelListCreateView",
    "EquipmentModelDetailUpdateView",
    "ArchiveEquipmentModelView",
    "RestoreEquipmentModelView",

    # Tipos de componentes
    "ComponentTypeListCreateView",
    "ComponentTypeDetailUpdateView",
    "ArchiveComponentTypeView",
    "RestoreComponentTypeView",

    # Componentes
    "EquipmentComponentListCreateView",
    "EquipmentComponentDetailUpdateView",
    "ArchiveEquipmentComponentView",
    "RestoreEquipmentComponentView",

    # Compatibilidades de componentes
    "ComponentCompatibilityListCreateView",
    "ComponentCompatibilityDetailUpdateView",
    "ArchiveComponentCompatibilityView",
    "RestoreComponentCompatibilityView",

    # Componentes asignados a equipos
    "EquipmentComponentAssignmentListCreateView",
    "EquipmentComponentAssignmentDetailUpdateView",

    # Importaciones y lotes
    "ImportBatchListCreateView",
    "ImportBatchDetailUpdateView",
    "ChangeImportBatchStatusView",
    "ArchiveImportBatchView",
    "RestoreImportBatchView",

    # Equipos físicos
    "EquipmentListCreateView",
    "EquipmentDetailUpdateView",
    "ChangeEquipmentTechnicalStatusView",
    "ChangeEquipmentCommercialStatusView",
    "RegisterInitialEquipmentMetersView",
    "ArchiveEquipmentView",
    "RestoreEquipmentView",

    # Movimientos de equipos
    "EquipmentMovementListCreateView",
    "EquipmentMovementDetailUpdateView",
    "ArchiveEquipmentMovementView",
    "RestoreEquipmentMovementView",

    # Lecturas de contadores
    "MeterReadingListCreateView",
    "MeterReadingDetailUpdateView",
    "VerifyMeterReadingView",
    "ApplyMeterReadingView",
    "ArchiveMeterReadingView",
    "RestoreMeterReadingView",

    # Documentos
    "EquipmentDocumentListCreateView",
    "EquipmentDocumentDetailUpdateView",
    "VerifyEquipmentDocumentView",
    "RemoveEquipmentDocumentVerificationView",
    "ArchiveEquipmentDocumentView",
    "RestoreEquipmentDocumentView",
)