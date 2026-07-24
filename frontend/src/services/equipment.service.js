const API_URL =
  "http://127.0.0.1:8000/api/equipment"

import {
  clearSession,
  getToken,
} from "./auth.service"


async function request(
  url,
  options = {}
) {
  const token = getToken()

  const headers = {
    Accept: "application/json",
    ...options.headers,
  }

  if (token) {
    headers.Authorization = `Token ${token}`
  }

  const response = await fetch(
    url,
    {
      ...options,
      headers,
    }
  )

  let data = null

  try {
    data = await response.json()
  } catch {
    data = null
  }

  if (response.status === 401) {
    clearSession()
    window.location.href = "/login"

    throw new Error(
      "Tu sesión terminó. Inicia sesión nuevamente."
    )
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
      getValidationError(data) ||
      "Ocurrió un error al procesar la solicitud."
    )
  }

  return data
}


function getValidationError(data) {
  if (
    !data ||
    typeof data !== "object"
  ) {
    return null
  }

  for (
    const value
    of Object.values(data)
  ) {
    if (
      Array.isArray(value) &&
      value.length
    ) {
      return String(value[0])
    }

    if (
      value &&
      typeof value === "object"
    ) {
      const nestedError =
        getValidationError(value)

      if (nestedError) {
        return nestedError
      }
    }

    if (typeof value === "string") {
      return value
    }
  }

  return null
}


function addBooleanParam(
  params,
  name,
  value
) {
  if (
    value === true ||
    value === false
  ) {
    params.set(
      name,
      String(value)
    )
  }
}


function addParam(
  params,
  name,
  value
) {
  if (
    value !== undefined &&
    value !== null &&
    String(value).trim() !== ""
  ) {
    params.set(
      name,
      String(value).trim()
    )
  }
}


function buildUrl(
  baseUrl,
  params
) {
  const query = params.toString()

  return query
    ? `${baseUrl}?${query}`
    : baseUrl
}


/* ============================================================= */
/* EQUIPOS                                                       */
/* ============================================================= */

export async function getEquipment({
  search = "",
  includeArchived = false,
  equipmentModel = "",
  brand = "",
  equipmentType = "",
  importBatch = "",
  supplier = "",
  ownerPartner = "",
  customer = "",
  customerBranch = "",
  advisor = "",
  ownershipType = "",
  physicalCondition = "",
  technicalStatus = "",
  commercialStatus = "",
  warehouseLocation = "",
  colorMode = "",
  isAvailable = "",
  isActive = "",
} = {}) {
  const params = new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  if (includeArchived) {
    params.set(
      "include_archived",
      "true"
    )
  }

  addParam(
    params,
    "equipment_model",
    equipmentModel
  )

  addParam(
    params,
    "brand",
    brand
  )

  addParam(
    params,
    "equipment_type",
    equipmentType
  )

  addParam(
    params,
    "import_batch",
    importBatch
  )

  addParam(
    params,
    "supplier",
    supplier
  )

  addParam(
    params,
    "owner_partner",
    ownerPartner
  )

  addParam(
    params,
    "customer",
    customer
  )

  addParam(
    params,
    "customer_branch",
    customerBranch
  )

  addParam(
    params,
    "advisor",
    advisor
  )

  addParam(
    params,
    "ownership_type",
    ownershipType
  )

  addParam(
    params,
    "physical_condition",
    physicalCondition
  )

  addParam(
    params,
    "technical_status",
    technicalStatus
  )

  addParam(
    params,
    "commercial_status",
    commercialStatus
  )

  addParam(
    params,
    "warehouse_location",
    warehouseLocation
  )

  addParam(
    params,
    "color_mode",
    colorMode
  )

  addBooleanParam(
    params,
    "is_available",
    isAvailable
  )

  addBooleanParam(
    params,
    "is_active",
    isActive
  )

  return request(
    buildUrl(
      `${API_URL}/`,
      params
    )
  )
}


export async function getEquipmentById(
  equipmentId
) {
  return request(
    `${API_URL}/${equipmentId}/`
  )
}


export async function createEquipment(
  equipmentData
) {
  const isFormData =
    equipmentData instanceof FormData

  return request(
    `${API_URL}/`,
    {
      method: "POST",
      headers: isFormData
        ? {}
        : {
            "Content-Type":
              "application/json",
          },
      body: isFormData
        ? equipmentData
        : JSON.stringify(
            equipmentData
          ),
    }
  )
}


export async function updateEquipment(
  equipmentId,
  equipmentData
) {
  const isFormData =
    equipmentData instanceof FormData

  return request(
    `${API_URL}/${equipmentId}/`,
    {
      method: "PATCH",
      headers: isFormData
        ? {}
        : {
            "Content-Type":
              "application/json",
          },
      body: isFormData
        ? equipmentData
        : JSON.stringify(
            equipmentData
          ),
    }
  )
}


export async function changeEquipmentTechnicalStatus(
  equipmentId,
  statusData
) {
  return request(
    `${API_URL}/${equipmentId}/technical-status/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        statusData
      ),
    }
  )
}


export async function changeEquipmentCommercialStatus(
  equipmentId,
  statusData
) {
  return request(
    `${API_URL}/${equipmentId}/commercial-status/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        statusData
      ),
    }
  )
}


export async function registerInitialEquipmentMeters(
  equipmentId,
  meterData
) {
  return request(
    `${API_URL}/${equipmentId}/initial-meters/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        meterData
      ),
    }
  )
}


export async function archiveEquipment(
  equipmentId,
  reason = ""
) {
  return request(
    `${API_URL}/${equipmentId}/archive/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        reason,
      }),
    }
  )
}


export async function restoreEquipment(
  equipmentId
) {
  return request(
    `${API_URL}/${equipmentId}/restore/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
    }
  )
}


/* ============================================================= */
/* TIPOS DE EQUIPO                                               */
/* ============================================================= */

export async function getEquipmentTypes({
  search = "",
  includeArchived = false,
  isActive = "",
} = {}) {
  const params = new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  if (includeArchived) {
    params.set(
      "include_archived",
      "true"
    )
  }

  addBooleanParam(
    params,
    "is_active",
    isActive
  )

  return request(
    buildUrl(
      `${API_URL}/types/`,
      params
    )
  )
}


export async function getEquipmentType(
  equipmentTypeId
) {
  return request(
    `${API_URL}/types/${equipmentTypeId}/`
  )
}


export async function createEquipmentType(
  equipmentTypeData
) {
  return request(
    `${API_URL}/types/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        equipmentTypeData
      ),
    }
  )
}


export async function updateEquipmentType(
  equipmentTypeId,
  equipmentTypeData
) {
  return request(
    `${API_URL}/types/${equipmentTypeId}/`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        equipmentTypeData
      ),
    }
  )
}


export async function archiveEquipmentType(
  equipmentTypeId,
  reason = ""
) {
  return request(
    `${API_URL}/types/${equipmentTypeId}/archive/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        reason,
      }),
    }
  )
}


export async function restoreEquipmentType(
  equipmentTypeId
) {
  return request(
    `${API_URL}/types/${equipmentTypeId}/restore/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
    }
  )
}


/* ============================================================= */
/* MARCAS                                                        */
/* ============================================================= */

export async function getEquipmentBrands({
  search = "",
  includeArchived = false,
  countryCode = "",
  isActive = "",
} = {}) {
  const params = new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  if (includeArchived) {
    params.set(
      "include_archived",
      "true"
    )
  }

  addParam(
    params,
    "country_code",
    countryCode
  )

  addBooleanParam(
    params,
    "is_active",
    isActive
  )

  return request(
    buildUrl(
      `${API_URL}/brands/`,
      params
    )
  )
}


export async function getEquipmentBrand(
  brandId
) {
  return request(
    `${API_URL}/brands/${brandId}/`
  )
}


export async function createEquipmentBrand(
  brandData
) {
  return request(
    `${API_URL}/brands/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        brandData
      ),
    }
  )
}


export async function updateEquipmentBrand(
  brandId,
  brandData
) {
  return request(
    `${API_URL}/brands/${brandId}/`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        brandData
      ),
    }
  )
}


export async function archiveEquipmentBrand(
  brandId,
  reason = ""
) {
  return request(
    `${API_URL}/brands/${brandId}/archive/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        reason,
      }),
    }
  )
}


export async function restoreEquipmentBrand(
  brandId
) {
  return request(
    `${API_URL}/brands/${brandId}/restore/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
    }
  )
}


/* ============================================================= */
/* MODELOS DE EQUIPO                                             */
/* ============================================================= */

export async function getEquipmentModels({
  search = "",
  includeArchived = false,
  brand = "",
  equipmentType = "",
  family = "",
  colorMode = "",
  technology = "",
  maximumPaperSize = "",
  isActive = "",
  hasTotalMeter = "",
  hasBlackMeter = "",
  hasColorMeter = "",
  hasScanMeter = "",
  supportsAccessories = "",
  supportsTechnicalUnits = "",
} = {}) {
  const params = new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  if (includeArchived) {
    params.set(
      "include_archived",
      "true"
    )
  }

  addParam(
    params,
    "brand",
    brand
  )

  addParam(
    params,
    "equipment_type",
    equipmentType
  )

  addParam(
    params,
    "family",
    family
  )

  addParam(
    params,
    "color_mode",
    colorMode
  )

  addParam(
    params,
    "technology",
    technology
  )

  addParam(
    params,
    "maximum_paper_size",
    maximumPaperSize
  )

  addBooleanParam(
    params,
    "is_active",
    isActive
  )

  addBooleanParam(
    params,
    "has_total_meter",
    hasTotalMeter
  )

  addBooleanParam(
    params,
    "has_black_meter",
    hasBlackMeter
  )

  addBooleanParam(
    params,
    "has_color_meter",
    hasColorMeter
  )

  addBooleanParam(
    params,
    "has_scan_meter",
    hasScanMeter
  )

  addBooleanParam(
    params,
    "supports_accessories",
    supportsAccessories
  )

  addBooleanParam(
    params,
    "supports_technical_units",
    supportsTechnicalUnits
  )

  return request(
    buildUrl(
      `${API_URL}/models/`,
      params
    )
  )
}


export async function getEquipmentModel(
  equipmentModelId
) {
  return request(
    `${API_URL}/models/${equipmentModelId}/`
  )
}


export async function createEquipmentModel(
  equipmentModelData
) {
  return request(
    `${API_URL}/models/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        equipmentModelData
      ),
    }
  )
}


export async function updateEquipmentModel(
  equipmentModelId,
  equipmentModelData
) {
  return request(
    `${API_URL}/models/${equipmentModelId}/`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        equipmentModelData
      ),
    }
  )
}


export async function archiveEquipmentModel(
  equipmentModelId,
  reason = ""
) {
  return request(
    `${API_URL}/models/${equipmentModelId}/archive/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        reason,
      }),
    }
  )
}


export async function restoreEquipmentModel(
  equipmentModelId
) {
  return request(
    `${API_URL}/models/${equipmentModelId}/restore/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
    }
  )
}


/* ============================================================= */
/* IMPORTACIONES Y LOTES                                         */
/* ============================================================= */

export async function getImportBatches({
  search = "",
  includeArchived = false,
  supplier = "",
  purchaseType = "",
  status = "",
  currency = "",
  originCountryCode = "",
  containerNumber = "",
  isActive = "",
} = {}) {
  const params = new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  if (includeArchived) {
    params.set(
      "include_archived",
      "true"
    )
  }

  addParam(
    params,
    "supplier",
    supplier
  )

  addParam(
    params,
    "purchase_type",
    purchaseType
  )

  addParam(
    params,
    "status",
    status
  )

  addParam(
    params,
    "currency",
    currency
  )

  addParam(
    params,
    "origin_country_code",
    originCountryCode
  )

  addParam(
    params,
    "container_number",
    containerNumber
  )

  addBooleanParam(
    params,
    "is_active",
    isActive
  )

  return request(
    buildUrl(
      `${API_URL}/import-batches/`,
      params
    )
  )
}


export async function getImportBatch(
  importBatchId
) {
  return request(
    `${API_URL}/import-batches/${importBatchId}/`
  )
}


export async function createImportBatch(
  importBatchData
) {
  return request(
    `${API_URL}/import-batches/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        importBatchData
      ),
    }
  )
}


export async function updateImportBatch(
  importBatchId,
  importBatchData
) {
  return request(
    `${API_URL}/import-batches/${importBatchId}/`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        importBatchData
      ),
    }
  )
}


export async function changeImportBatchStatus(
  importBatchId,
  statusData
) {
  return request(
    `${API_URL}/import-batches/${importBatchId}/status/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        statusData
      ),
    }
  )
}


export async function archiveImportBatch(
  importBatchId,
  reason = ""
) {
  return request(
    `${API_URL}/import-batches/${importBatchId}/archive/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        reason,
      }),
    }
  )
}


export async function restoreImportBatch(
  importBatchId
) {
  return request(
    `${API_URL}/import-batches/${importBatchId}/restore/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
    }
  )
}


/* ============================================================= */
/* MOVIMIENTOS                                                   */
/* ============================================================= */

export async function getEquipmentMovements({
  search = "",
  includeArchived = false,
  equipment = "",
  movementType = "",
  referenceType = "",
  referenceId = "",
  responsibleUser = "",
  previousCustomer = "",
  newCustomer = "",
  previousCustomerBranch = "",
  newCustomerBranch = "",
  previousTechnicalStatus = "",
  newTechnicalStatus = "",
  previousCommercialStatus = "",
  newCommercialStatus = "",
  isSystemGenerated = "",
  occurredFrom = "",
  occurredTo = "",
} = {}) {
  const params = new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  if (includeArchived) {
    params.set(
      "include_archived",
      "true"
    )
  }

  addParam(
    params,
    "equipment",
    equipment
  )

  addParam(
    params,
    "movement_type",
    movementType
  )

  addParam(
    params,
    "reference_type",
    referenceType
  )

  addParam(
    params,
    "reference_id",
    referenceId
  )

  addParam(
    params,
    "responsible_user",
    responsibleUser
  )

  addParam(
    params,
    "previous_customer",
    previousCustomer
  )

  addParam(
    params,
    "new_customer",
    newCustomer
  )

  addParam(
    params,
    "previous_customer_branch",
    previousCustomerBranch
  )

  addParam(
    params,
    "new_customer_branch",
    newCustomerBranch
  )

  addParam(
    params,
    "previous_technical_status",
    previousTechnicalStatus
  )

  addParam(
    params,
    "new_technical_status",
    newTechnicalStatus
  )

  addParam(
    params,
    "previous_commercial_status",
    previousCommercialStatus
  )

  addParam(
    params,
    "new_commercial_status",
    newCommercialStatus
  )

  addBooleanParam(
    params,
    "is_system_generated",
    isSystemGenerated
  )

  addParam(
    params,
    "occurred_from",
    occurredFrom
  )

  addParam(
    params,
    "occurred_to",
    occurredTo
  )

  return request(
    buildUrl(
      `${API_URL}/movements/`,
      params
    )
  )
}


export async function getEquipmentMovement(
  movementId
) {
  return request(
    `${API_URL}/movements/${movementId}/`
  )
}


export async function createEquipmentMovement(
  movementData
) {
  return request(
    `${API_URL}/movements/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        movementData
      ),
    }
  )
}


export async function updateEquipmentMovement(
  movementId,
  movementData
) {
  return request(
    `${API_URL}/movements/${movementId}/`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        movementData
      ),
    }
  )
}


export async function archiveEquipmentMovement(
  movementId,
  reason = ""
) {
  return request(
    `${API_URL}/movements/${movementId}/archive/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        reason,
      }),
    }
  )
}


export async function restoreEquipmentMovement(
  movementId
) {
  return request(
    `${API_URL}/movements/${movementId}/restore/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
    }
  )
}


/* ============================================================= */
/* LECTURAS DE CONTADORES                                        */
/* ============================================================= */

export async function getMeterReadings({
  search = "",
  includeArchived = false,
  equipment = "",
  readingType = "",
  source = "",
  referenceType = "",
  referenceId = "",
  registeredBy = "",
  verifiedBy = "",
  isVerified = "",
  isAppliedToEquipment = "",
  readingFrom = "",
  readingTo = "",
} = {}) {
  const params = new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  if (includeArchived) {
    params.set(
      "include_archived",
      "true"
    )
  }

  addParam(
    params,
    "equipment",
    equipment
  )

  addParam(
    params,
    "reading_type",
    readingType
  )

  addParam(
    params,
    "source",
    source
  )

  addParam(
    params,
    "reference_type",
    referenceType
  )

  addParam(
    params,
    "reference_id",
    referenceId
  )

  addParam(
    params,
    "registered_by",
    registeredBy
  )

  addParam(
    params,
    "verified_by",
    verifiedBy
  )

  addBooleanParam(
    params,
    "is_verified",
    isVerified
  )

  addBooleanParam(
    params,
    "is_applied_to_equipment",
    isAppliedToEquipment
  )

  addParam(
    params,
    "reading_from",
    readingFrom
  )

  addParam(
    params,
    "reading_to",
    readingTo
  )

  return request(
    buildUrl(
      `${API_URL}/meter-readings/`,
      params
    )
  )
}


export async function getMeterReading(
  readingId
) {
  return request(
    `${API_URL}/meter-readings/${readingId}/`
  )
}


export async function createMeterReading(
  readingData
) {
  return request(
    `${API_URL}/meter-readings/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        readingData
      ),
    }
  )
}


export async function updateMeterReading(
  readingId,
  readingData
) {
  return request(
    `${API_URL}/meter-readings/${readingId}/`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        readingData
      ),
    }
  )
}


export async function verifyMeterReading(
  readingId,
  verificationData = {}
) {
  return request(
    `${API_URL}/meter-readings/${readingId}/verify/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        verificationData
      ),
    }
  )
}


export async function applyMeterReading(
  readingId,
  applyData = {}
) {
  return request(
    `${API_URL}/meter-readings/${readingId}/apply/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        applyData
      ),
    }
  )
}


export async function archiveMeterReading(
  readingId,
  reason = ""
) {
  return request(
    `${API_URL}/meter-readings/${readingId}/archive/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        reason,
      }),
    }
  )
}


export async function restoreMeterReading(
  readingId
) {
  return request(
    `${API_URL}/meter-readings/${readingId}/restore/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
    }
  )
}


/* ============================================================= */
/* DOCUMENTOS DE EQUIPOS                                         */
/* ============================================================= */

export async function getEquipmentDocuments({
  search = "",
  includeArchived = false,
  equipment = "",
  documentType = "",
  referenceType = "",
  referenceId = "",
  uploadedBy = "",
  verifiedBy = "",
  isPrimary = "",
  isConfidential = "",
  isVerified = "",
  isActive = "",
  documentFrom = "",
  documentTo = "",
  expirationFrom = "",
  expirationTo = "",
} = {}) {
  const params = new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  if (includeArchived) {
    params.set(
      "include_archived",
      "true"
    )
  }

  addParam(
    params,
    "equipment",
    equipment
  )

  addParam(
    params,
    "document_type",
    documentType
  )

  addParam(
    params,
    "reference_type",
    referenceType
  )

  addParam(
    params,
    "reference_id",
    referenceId
  )

  addParam(
    params,
    "uploaded_by",
    uploadedBy
  )

  addParam(
    params,
    "verified_by",
    verifiedBy
  )

  addBooleanParam(
    params,
    "is_primary",
    isPrimary
  )

  addBooleanParam(
    params,
    "is_confidential",
    isConfidential
  )

  addBooleanParam(
    params,
    "is_verified",
    isVerified
  )

  addBooleanParam(
    params,
    "is_active",
    isActive
  )

  addParam(
    params,
    "document_from",
    documentFrom
  )

  addParam(
    params,
    "document_to",
    documentTo
  )

  addParam(
    params,
    "expiration_from",
    expirationFrom
  )

  addParam(
    params,
    "expiration_to",
    expirationTo
  )

  return request(
    buildUrl(
      `${API_URL}/documents/`,
      params
    )
  )
}


export async function getEquipmentDocument(
  documentId
) {
  return request(
    `${API_URL}/documents/${documentId}/`
  )
}


export async function createEquipmentDocument(
  documentData
) {
  const isFormData =
    documentData instanceof FormData

  return request(
    `${API_URL}/documents/`,
    {
      method: "POST",
      headers: isFormData
        ? {}
        : {
            "Content-Type":
              "application/json",
          },
      body: isFormData
        ? documentData
        : JSON.stringify(
            documentData
          ),
    }
  )
}


export async function updateEquipmentDocument(
  documentId,
  documentData
) {
  const isFormData =
    documentData instanceof FormData

  return request(
    `${API_URL}/documents/${documentId}/`,
    {
      method: "PATCH",
      headers: isFormData
        ? {}
        : {
            "Content-Type":
              "application/json",
          },
      body: isFormData
        ? documentData
        : JSON.stringify(
            documentData
          ),
    }
  )
}


export async function verifyEquipmentDocument(
  documentId,
  verificationData = {}
) {
  return request(
    `${API_URL}/documents/${documentId}/verify/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        verificationData
      ),
    }
  )
}


export async function removeEquipmentDocumentVerification(
  documentId,
  verificationData = {}
) {
  return request(
    `${API_URL}/documents/${documentId}/remove-verification/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        verificationData
      ),
    }
  )
}


export async function archiveEquipmentDocument(
  documentId,
  reason = ""
) {
  return request(
    `${API_URL}/documents/${documentId}/archive/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        reason,
      }),
    }
  )
}


export async function restoreEquipmentDocument(
  documentId
) {
  return request(
    `${API_URL}/documents/${documentId}/restore/`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
    }
  )
}


/* ============================================================= */
/* TIPOS DE COMPONENTES                                          */
/* ============================================================= */

export async function getComponentTypes({
  search = "",
  includeArchived = false,
  category = "",
  requiresColor = "",
  requiresSerialNumber = "",
  requiresMeter = "",
  controlsStock = "",
  isActive = "",
} = {}) {
  const params = new URLSearchParams()

  addParam(params, "search", search)
  addParam(params, "category", category)

  if (includeArchived) {
    params.set("include_archived", "true")
  }

  addBooleanParam(params, "requires_color", requiresColor)
  addBooleanParam(params, "requires_serial_number", requiresSerialNumber)
  addBooleanParam(params, "requires_meter", requiresMeter)
  addBooleanParam(params, "controls_stock", controlsStock)
  addBooleanParam(params, "is_active", isActive)

  return request(
    buildUrl(
      `${API_URL}/component-types/`,
      params
    )
  )
}

export async function getComponentType(componentTypeId) {
  return request(
    `${API_URL}/component-types/${componentTypeId}/`
  )
}

export async function createComponentType(componentTypeData) {
  return request(
    `${API_URL}/component-types/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(componentTypeData),
    }
  )
}

export async function updateComponentType(
  componentTypeId,
  componentTypeData
) {
  return request(
    `${API_URL}/component-types/${componentTypeId}/`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(componentTypeData),
    }
  )
}

export async function archiveComponentType(
  componentTypeId,
  reason = ""
) {
  return request(
    `${API_URL}/component-types/${componentTypeId}/archive/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ reason }),
    }
  )
}

export async function restoreComponentType(componentTypeId) {
  return request(
    `${API_URL}/component-types/${componentTypeId}/restore/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  )
}


/* ============================================================= */
/* COMPONENTES Y UNIDADES TÉCNICAS                               */
/* ============================================================= */

export async function getEquipmentComponents({
  search = "",
  includeArchived = false,
  componentType = "",
  category = "",
  parentComponent = "",
  color = "",
  conditionControl = "",
  isConsumable = "",
  isReusable = "",
  canBeRepaired = "",
  requiresIndividualSerial = "",
  isActive = "",
} = {}) {
  const params = new URLSearchParams()

  addParam(params, "search", search)

  if (includeArchived) {
    params.set("include_archived", "true")
  }

  addParam(params, "component_type", componentType)
  addParam(params, "category", category)
  addParam(params, "parent_component", parentComponent)
  addParam(params, "color", color)
  addParam(params, "condition_control", conditionControl)
  addBooleanParam(params, "is_consumable", isConsumable)
  addBooleanParam(params, "is_reusable", isReusable)
  addBooleanParam(params, "can_be_repaired", canBeRepaired)
  addBooleanParam(
    params,
    "requires_individual_serial",
    requiresIndividualSerial
  )
  addBooleanParam(params, "is_active", isActive)

  return request(
    buildUrl(
      `${API_URL}/components/`,
      params
    )
  )
}

export async function getEquipmentComponent(componentId) {
  return request(
    `${API_URL}/components/${componentId}/`
  )
}

export async function createEquipmentComponent(componentData) {
  const isFormData = componentData instanceof FormData

  return request(
    `${API_URL}/components/`,
    {
      method: "POST",
      headers: isFormData
        ? {}
        : {
            "Content-Type": "application/json",
          },
      body: isFormData
        ? componentData
        : JSON.stringify(componentData),
    }
  )
}

export async function updateEquipmentComponent(
  componentId,
  componentData
) {
  const isFormData = componentData instanceof FormData

  return request(
    `${API_URL}/components/${componentId}/`,
    {
      method: "PATCH",
      headers: isFormData
        ? {}
        : {
            "Content-Type": "application/json",
          },
      body: isFormData
        ? componentData
        : JSON.stringify(componentData),
    }
  )
}

export async function archiveEquipmentComponent(
  componentId,
  reason = ""
) {
  return request(
    `${API_URL}/components/${componentId}/archive/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ reason }),
    }
  )
}

export async function restoreEquipmentComponent(componentId) {
  return request(
    `${API_URL}/components/${componentId}/restore/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  )
}


/* ============================================================= */
/* COMPATIBILIDADES DE COMPONENTES                               */
/* ============================================================= */

export async function getComponentCompatibilities({
  search = "",
  includeArchived = false,
  component = "",
  equipmentFamily = "",
  equipmentModel = "",
  compatibilityType = "",
  position = "",
  brand = "",
  equipmentType = "",
  requiresAdjustment = "",
  isPreferred = "",
  isActive = "",
} = {}) {
  const params = new URLSearchParams()

  addParam(params, "search", search)

  if (includeArchived) {
    params.set("include_archived", "true")
  }

  addParam(params, "component", component)
  addParam(params, "equipment_family", equipmentFamily)
  addParam(params, "equipment_model", equipmentModel)
  addParam(params, "compatibility_type", compatibilityType)
  addParam(params, "position", position)
  addParam(params, "brand", brand)
  addParam(params, "equipment_type", equipmentType)
  addBooleanParam(params, "requires_adjustment", requiresAdjustment)
  addBooleanParam(params, "is_preferred", isPreferred)
  addBooleanParam(params, "is_active", isActive)

  return request(
    buildUrl(
      `${API_URL}/component-compatibilities/`,
      params
    )
  )
}

export async function getComponentCompatibility(compatibilityId) {
  return request(
    `${API_URL}/component-compatibilities/${compatibilityId}/`
  )
}

export async function createComponentCompatibility(
  compatibilityData
) {
  return request(
    `${API_URL}/component-compatibilities/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(compatibilityData),
    }
  )
}

export async function updateComponentCompatibility(
  compatibilityId,
  compatibilityData
) {
  return request(
    `${API_URL}/component-compatibilities/${compatibilityId}/`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(compatibilityData),
    }
  )
}

export async function archiveComponentCompatibility(
  compatibilityId,
  reason = ""
) {
  return request(
    `${API_URL}/component-compatibilities/${compatibilityId}/archive/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ reason }),
    }
  )
}

export async function restoreComponentCompatibility(compatibilityId) {
  return request(
    `${API_URL}/component-compatibilities/${compatibilityId}/restore/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  )
}


/* ============================================================= */
/* ALIAS                                                         */
/* ============================================================= */

export const getEquipments =
  getEquipment

export const getMachine =
  getEquipmentById

export const createMachine =
  createEquipment

export const updateMachine =
  updateEquipment

export const archiveMachine =
  archiveEquipment

export const restoreMachine =
  restoreEquipment


export const getBrands =
  getEquipmentBrands

export const getBrand =
  getEquipmentBrand

export const createBrand =
  createEquipmentBrand

export const updateBrand =
  updateEquipmentBrand

export const archiveBrand =
  archiveEquipmentBrand

export const restoreBrand =
  restoreEquipmentBrand


export const getModels =
  getEquipmentModels

export const getModel =
  getEquipmentModel

export const createModel =
  createEquipmentModel

export const updateModel =
  updateEquipmentModel

export const archiveModel =
  archiveEquipmentModel

export const restoreModel =
  restoreEquipmentModel