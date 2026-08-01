# -*- coding: utf-8 -*-

from .brand import (
    ArchiveEquipmentBrandSerializer,
    EquipmentBrandCreateUpdateSerializer,
    EquipmentBrandDetailSerializer,
    EquipmentBrandListSerializer,
)
from .common import (
    convert_django_validation_error,
    get_authenticated_user,
    raise_drf_validation_error,
)
from .component import (
    ArchiveEquipmentComponentSerializer,
    EquipmentComponentCreateUpdateSerializer,
    EquipmentComponentDetailSerializer,
    EquipmentComponentListSerializer,
)
from .component_compatibility import (
    ArchiveComponentCompatibilitySerializer,
    ComponentCompatibilityCreateUpdateSerializer,
    ComponentCompatibilityDetailSerializer,
    ComponentCompatibilityListSerializer,
)
from .component_type import (
    ArchiveComponentTypeSerializer,
    ComponentTypeCreateUpdateSerializer,
    ComponentTypeDetailSerializer,
    ComponentTypeListSerializer,
)
from .equipment import (
    ArchiveEquipmentSerializer,
    ChangeEquipmentCommercialStatusSerializer,
    ChangeEquipmentTechnicalStatusSerializer,
    EquipmentCreateUpdateSerializer,
    EquipmentDetailSerializer,
    EquipmentListSerializer,
    RegisterInitialEquipmentMetersSerializer,
)
from .equipment_component_assignment import (
    ArchiveEquipmentComponentAssignmentSerializer,
    EquipmentComponentAssignmentCreateUpdateSerializer,
    EquipmentComponentAssignmentDetailSerializer,
    EquipmentComponentAssignmentListSerializer,
    RemoveEquipmentComponentAssignmentSerializer,
)
from .equipment_document import (
    ArchiveEquipmentDocumentSerializer,
    EquipmentDocumentCreateUpdateSerializer,
    EquipmentDocumentDetailSerializer,
    EquipmentDocumentListSerializer,
    RemoveEquipmentDocumentVerificationSerializer,
    VerifyEquipmentDocumentSerializer,
)
from .equipment_family import (
    ArchiveEquipmentFamilySerializer,
    EquipmentFamilyCreateUpdateSerializer,
    EquipmentFamilyDetailSerializer,
    EquipmentFamilyListSerializer,
)
from .equipment_model import (
    ArchiveEquipmentModelSerializer,
    EquipmentModelCreateUpdateSerializer,
    EquipmentModelDetailSerializer,
    EquipmentModelListSerializer,
)
from .equipment_movement import (
    ArchiveEquipmentMovementSerializer,
    EquipmentMovementCreateUpdateSerializer,
    EquipmentMovementDetailSerializer,
    EquipmentMovementListSerializer,
)
from .equipment_type import (
    ArchiveEquipmentTypeSerializer,
    EquipmentTypeCreateUpdateSerializer,
    EquipmentTypeDetailSerializer,
    EquipmentTypeListSerializer,
)
from .import_batch import (
    ArchiveImportBatchSerializer,
    ChangeImportBatchStatusSerializer,
    ImportBatchCreateUpdateSerializer,
    ImportBatchDetailSerializer,
    ImportBatchListSerializer,
)
from .meter_reading import (
    ApplyMeterReadingSerializer,
    ArchiveMeterReadingSerializer,
    MeterReadingCreateUpdateSerializer,
    MeterReadingDetailSerializer,
    MeterReadingListSerializer,
    VerifyMeterReadingSerializer,
)


__all__ = (
    # Funciones comunes
    "convert_django_validation_error",
    "get_authenticated_user",
    "raise_drf_validation_error",

    # Tipos de equipos
    "EquipmentTypeListSerializer",
    "EquipmentTypeDetailSerializer",
    "EquipmentTypeCreateUpdateSerializer",
    "ArchiveEquipmentTypeSerializer",

    # Marcas
    "EquipmentBrandListSerializer",
    "EquipmentBrandDetailSerializer",
    "EquipmentBrandCreateUpdateSerializer",
    "ArchiveEquipmentBrandSerializer",

    # Familias
    "EquipmentFamilyListSerializer",
    "EquipmentFamilyDetailSerializer",
    "EquipmentFamilyCreateUpdateSerializer",
    "ArchiveEquipmentFamilySerializer",

    # Modelos de equipos
    "EquipmentModelListSerializer",
    "EquipmentModelDetailSerializer",
    "EquipmentModelCreateUpdateSerializer",
    "ArchiveEquipmentModelSerializer",

    # Tipos de componentes
    "ComponentTypeListSerializer",
    "ComponentTypeDetailSerializer",
    "ComponentTypeCreateUpdateSerializer",
    "ArchiveComponentTypeSerializer",

    # Componentes
    "EquipmentComponentListSerializer",
    "EquipmentComponentDetailSerializer",
    "EquipmentComponentCreateUpdateSerializer",
    "ArchiveEquipmentComponentSerializer",

    # Compatibilidades
    "ComponentCompatibilityListSerializer",
    "ComponentCompatibilityDetailSerializer",
    "ComponentCompatibilityCreateUpdateSerializer",
    "ArchiveComponentCompatibilitySerializer",

    # Componentes asignados a equipos
    "EquipmentComponentAssignmentListSerializer",
    "EquipmentComponentAssignmentDetailSerializer",
    "EquipmentComponentAssignmentCreateUpdateSerializer",
    "RemoveEquipmentComponentAssignmentSerializer",
    "ArchiveEquipmentComponentAssignmentSerializer",

    # Importaciones y lotes
    "ImportBatchListSerializer",
    "ImportBatchDetailSerializer",
    "ImportBatchCreateUpdateSerializer",
    "ArchiveImportBatchSerializer",
    "ChangeImportBatchStatusSerializer",

    # Equipos físicos
    "EquipmentListSerializer",
    "EquipmentDetailSerializer",
    "EquipmentCreateUpdateSerializer",
    "ArchiveEquipmentSerializer",
    "ChangeEquipmentTechnicalStatusSerializer",
    "ChangeEquipmentCommercialStatusSerializer",
    "RegisterInitialEquipmentMetersSerializer",

    # Movimientos de equipos
    "EquipmentMovementListSerializer",
    "EquipmentMovementDetailSerializer",
    "EquipmentMovementCreateUpdateSerializer",
    "ArchiveEquipmentMovementSerializer",

    # Lecturas de contadores
    "MeterReadingListSerializer",
    "MeterReadingDetailSerializer",
    "MeterReadingCreateUpdateSerializer",
    "VerifyMeterReadingSerializer",
    "ApplyMeterReadingSerializer",
    "ArchiveMeterReadingSerializer",

    # Documentos
    "EquipmentDocumentListSerializer",
    "EquipmentDocumentDetailSerializer",
    "EquipmentDocumentCreateUpdateSerializer",
    "VerifyEquipmentDocumentSerializer",
    "RemoveEquipmentDocumentVerificationSerializer",
    "ArchiveEquipmentDocumentSerializer",
)