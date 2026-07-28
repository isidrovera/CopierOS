# -*- coding: utf-8 -*-

from .base import ServicesBaseModel

# Órdenes de servicio
from .service_order import ServiceOrder

# Historial general de órdenes
from .service_history import (
    ServiceAssignmentHistory,
    ServiceStatusHistory,
)

# Tracking GPS
from .service_tracking import (
    ServiceTrackingPoint,
    ServiceTrackingSession,
)

# Checklist técnico
from .service_checklist import (
    ServiceChecklist,
    ServiceChecklistItem,
)

# Evidencias y contadores
from .service_evidence_meter import (
    ServiceEvidence,
    ServiceMeterReading,
)

# Pedidos de repuestos
from .service_part_request import ServicePartRequest
from .service_part_request_item import ServicePartRequestItem
from .service_part_request_history import (
    ServicePartRequestStatusHistory,
)
from .service_part_request_information import (
    ServicePartRequestInformation,
)
from .service_part_request_decision import (
    ServicePartRequestDecision,
)
from .service_part_request_attachment import (
    ServicePartRequestAttachment,
)
from .service_part_request_comment import (
    ServicePartRequestComment,
)
from .service_part_request_notification import (
    ServicePartRequestNotification,
)

# Repuestos reutilizables
from .service_reusable_part import ServiceReusablePart
from .service_reusable_part_history import (
    ServiceReusablePartHistory,
)

# Traslados de repuestos
from .service_part_transfer import ServicePartTransfer
from .service_part_transfer_history import (
    ServicePartTransferHistory,
)

# Revisión física de stock
from .service_part_stock_review import (
    ServicePartStockReview,
)
from .service_part_stock_review_history import (
    ServicePartStockReviewHistory,
)

# Instalación y reemplazo de repuestos
from .service_installation_item import (
    ServiceInstallationItem,
)
from .equipment_installed_item import (
    EquipmentInstalledItem,
)


__all__ = (
    # Base
    "ServicesBaseModel",

    # Órdenes
    "ServiceOrder",
    "ServiceAssignmentHistory",
    "ServiceStatusHistory",

    # Tracking
    "ServiceTrackingSession",
    "ServiceTrackingPoint",

    # Checklist
    "ServiceChecklist",
    "ServiceChecklistItem",

    # Evidencias y contadores
    "ServiceEvidence",
    "ServiceMeterReading",

    # Pedidos
    "ServicePartRequest",
    "ServicePartRequestItem",
    "ServicePartRequestStatusHistory",
    "ServicePartRequestInformation",
    "ServicePartRequestDecision",
    "ServicePartRequestAttachment",
    "ServicePartRequestComment",
    "ServicePartRequestNotification",

    # Repuestos reutilizables
    "ServiceReusablePart",
    "ServiceReusablePartHistory",

    # Traslados
    "ServicePartTransfer",
    "ServicePartTransferHistory",

    # Revisión de stock
    "ServicePartStockReview",
    "ServicePartStockReviewHistory",

    # Instalaciones
    "ServiceInstallationItem",
    "EquipmentInstalledItem",
)