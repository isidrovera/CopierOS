const API_ROOT =
  "http://127.0.0.1:8000/api/repairs"

const REPAIRS_URL =
  `${API_ROOT}/repairs`

const ASSIGNMENTS_URL =
  `${API_ROOT}/assignments`

const CHECKLISTS_URL =
  `${API_ROOT}/checklists`

const CHECKLIST_ITEMS_URL =
  `${API_ROOT}/checklist-items`

const DIAGNOSES_URL =
  `${API_ROOT}/diagnoses`

const COMPONENTS_URL =
  `${API_ROOT}/components`

const PHOTOS_URL =
  `${API_ROOT}/photos`

const TESTS_URL =
  `${API_ROOT}/tests`

const SNMP_VALIDATIONS_URL =
  `${API_ROOT}/snmp-validations`

const STATUS_HISTORY_URL =
  `${API_ROOT}/status-history`

const PART_REQUESTS_URL =
  `${API_ROOT}/part-requests`

const PART_REQUEST_ITEMS_URL =
  `${API_ROOT}/part-request-items`

const PART_REQUEST_REVIEWS_URL =
  `${API_ROOT}/part-request-reviews`

const PART_REQUEST_DECISIONS_URL =
  `${API_ROOT}/part-request-decisions`

const PART_SOURCES_URL =
  `${API_ROOT}/part-sources`

const PART_WITHDRAWALS_URL =
  `${API_ROOT}/part-withdrawals`

const PART_DELIVERIES_URL =
  `${API_ROOT}/part-deliveries`

const PART_REPLACEMENTS_URL =
  `${API_ROOT}/part-replacements`

const PART_REQUEST_COMMENTS_URL =
  `${API_ROOT}/part-request-comments`

const PART_REQUEST_ATTACHMENTS_URL =
  `${API_ROOT}/part-request-attachments`

const PART_REQUEST_HISTORY_URL =
  `${API_ROOT}/part-request-history`

const PART_REQUEST_NOTIFICATIONS_URL =
  `${API_ROOT}/part-request-notifications`


import {
  clearSession,
  getToken,
} from "./auth.service"


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

    if (
      typeof value === "string" &&
      value.trim()
    ) {
      return value
    }
  }

  return null
}


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
    headers.Authorization =
      `Token ${token}`
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

    window.location.href =
      "/login"

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


function addArchivedParam(
  params,
  includeArchived
) {
  if (includeArchived) {
    params.set(
      "include_archived",
      "true"
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


function jsonRequest(
  url,
  method,
  data = {}
) {
  return request(
    url,
    {
      method,
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(data),
    }
  )
}


function createResource(
  baseUrl,
  data
) {
  return jsonRequest(
    `${baseUrl}/`,
    "POST",
    data
  )
}


function updateResource(
  baseUrl,
  resourceId,
  data
) {
  return jsonRequest(
    `${baseUrl}/${resourceId}/`,
    "PATCH",
    data
  )
}


function getResource(
  baseUrl,
  resourceId
) {
  return request(
    `${baseUrl}/${resourceId}/`
  )
}


function deleteResource(
  baseUrl,
  resourceId
) {
  return request(
    `${baseUrl}/${resourceId}/`,
    {
      method: "DELETE",
    }
  )
}


function resourceAction(
  baseUrl,
  resourceId,
  actionName,
  data = {}
) {
  return jsonRequest(
    `${baseUrl}/${resourceId}/${actionName}/`,
    "POST",
    data
  )
}


/* ============================================================= */
/* REPARACIONES                                                  */
/* ============================================================= */

export async function getRepairs({
  search = "",
  includeArchived = false,
  equipment = "",
  repairType = "",
  status = "",
  priority = "",
  technician = "",
  requestedBy = "",
  isActive = "",
  requiresParts = "",
  requiresExternalService = "",
  requiresFollowUp = "",
  requestedFrom = "",
  requestedTo = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  addArchivedParam(
    params,
    includeArchived
  )

  addParam(
    params,
    "equipment",
    equipment
  )

  addParam(
    params,
    "repair_type",
    repairType
  )

  addParam(
    params,
    "status",
    status
  )

  addParam(
    params,
    "priority",
    priority
  )

  addParam(
    params,
    "assigned_technician",
    technician
  )

  addParam(
    params,
    "requested_by",
    requestedBy
  )

  addBooleanParam(
    params,
    "is_active",
    isActive
  )

  addBooleanParam(
    params,
    "requires_parts",
    requiresParts
  )

  addBooleanParam(
    params,
    "requires_external_service",
    requiresExternalService
  )

  addBooleanParam(
    params,
    "requires_follow_up",
    requiresFollowUp
  )

  addParam(
    params,
    "requested_from",
    requestedFrom
  )

  addParam(
    params,
    "requested_to",
    requestedTo
  )

  addParam(
    params,
    "ordering",
    ordering
  )

  return request(
    buildUrl(
      `${REPAIRS_URL}/`,
      params
    )
  )
}


export async function getRepairById(
  repairId
) {
  return getResource(
    REPAIRS_URL,
    repairId
  )
}


export async function getActiveRepairByEquipment(
  equipmentId
) {
  if (
    equipmentId === undefined ||
    equipmentId === null ||
    String(equipmentId).trim() === ""
  ) {
    return null
  }

  const response =
    await getRepairs({
      equipment: equipmentId,
      includeArchived: false,
      isActive: true,
      ordering: "-requested_at",
    })

  const repairs =
    Array.isArray(response)
      ? response
      : Array.isArray(response?.results)
        ? response.results
        : []

  return (
    repairs.find(
      (repair) =>
        repair.is_active === true &&
        repair.is_archived !== true &&
        !repair.archived_at
    ) ||
    null
  )
}


export async function createRepair(
  repairData
) {
  return createResource(
    REPAIRS_URL,
    repairData
  )
}


export async function updateRepair(
  repairId,
  repairData
) {
  return updateResource(
    REPAIRS_URL,
    repairId,
    repairData
  )
}


export async function deleteRepair(
  repairId
) {
  return deleteResource(
    REPAIRS_URL,
    repairId
  )
}


export async function assignRepair(
  repairId,
  assignmentData
) {
  return resourceAction(
    REPAIRS_URL,
    repairId,
    "assign",
    assignmentData
  )
}


export async function changeRepairStatus(
  repairId,
  statusData
) {
  return resourceAction(
    REPAIRS_URL,
    repairId,
    "change-status",
    statusData
  )
}


export async function cancelRepair(
  repairId,
  cancellationData
) {
  return resourceAction(
    REPAIRS_URL,
    repairId,
    "cancel",
    cancellationData
  )
}


export async function reopenRepair(
  repairId,
  reopeningData
) {
  return resourceAction(
    REPAIRS_URL,
    repairId,
    "reopen",
    reopeningData
  )
}


export async function archiveRepair(
  repairId,
  reason = ""
) {
  return resourceAction(
    REPAIRS_URL,
    repairId,
    "archive",
    {
      reason,
    }
  )
}


export async function restoreRepair(
  repairId
) {
  return resourceAction(
    REPAIRS_URL,
    repairId,
    "restore"
  )
}


/* ============================================================= */
/* ASIGNACIONES                                                  */
/* ============================================================= */

export async function getRepairAssignments({
  search = "",
  includeArchived = false,
  repair = "",
  technician = "",
  status = "",
  isActive = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  addArchivedParam(
    params,
    includeArchived
  )

  addParam(
    params,
    "repair",
    repair
  )

  addParam(
    params,
    "technician",
    technician
  )

  addParam(
    params,
    "status",
    status
  )

  addBooleanParam(
    params,
    "is_active",
    isActive
  )

  addParam(
    params,
    "ordering",
    ordering
  )

  return request(
    buildUrl(
      `${ASSIGNMENTS_URL}/`,
      params
    )
  )
}


export async function getRepairAssignment(
  assignmentId
) {
  return getResource(
    ASSIGNMENTS_URL,
    assignmentId
  )
}


export async function createRepairAssignment(
  assignmentData
) {
  return createResource(
    ASSIGNMENTS_URL,
    assignmentData
  )
}


export async function updateRepairAssignment(
  assignmentId,
  assignmentData
) {
  return updateResource(
    ASSIGNMENTS_URL,
    assignmentId,
    assignmentData
  )
}


export async function acceptRepairAssignment(
  assignmentId,
  observations = ""
) {
  return resourceAction(
    ASSIGNMENTS_URL,
    assignmentId,
    "accept",
    {
      observations,
    }
  )
}


export async function startRepairAssignment(
  assignmentId,
  observations = ""
) {
  return resourceAction(
    ASSIGNMENTS_URL,
    assignmentId,
    "start",
    {
      observations,
    }
  )
}


export async function completeRepairAssignment(
  assignmentId,
  completionNotes = ""
) {
  return resourceAction(
    ASSIGNMENTS_URL,
    assignmentId,
    "complete",
    {
      completion_notes:
        completionNotes,
    }
  )
}


export async function reassignRepairAssignment(
  assignmentId,
  reassignmentData
) {
  return resourceAction(
    ASSIGNMENTS_URL,
    assignmentId,
    "reassign",
    reassignmentData
  )
}


export async function rejectRepairAssignment(
  assignmentId,
  rejectionData
) {
  return resourceAction(
    ASSIGNMENTS_URL,
    assignmentId,
    "reject",
    rejectionData
  )
}


export async function cancelRepairAssignment(
  assignmentId,
  reason
) {
  return resourceAction(
    ASSIGNMENTS_URL,
    assignmentId,
    "cancel",
    {
      reason,
    }
  )
}


export async function archiveRepairAssignment(
  assignmentId,
  reason = ""
) {
  return resourceAction(
    ASSIGNMENTS_URL,
    assignmentId,
    "archive",
    {
      reason,
    }
  )
}


export async function restoreRepairAssignment(
  assignmentId
) {
  return resourceAction(
    ASSIGNMENTS_URL,
    assignmentId,
    "restore"
  )
}


/* ============================================================= */
/* CHECKLISTS                                                    */
/* ============================================================= */

export async function getRepairChecklists({
  search = "",
  includeArchived = false,
  repair = "",
  equipment = "",
  status = "",
  isMainChecklist = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  addArchivedParam(
    params,
    includeArchived
  )

  addParam(
    params,
    "repair",
    repair
  )

  addParam(
    params,
    "equipment",
    equipment
  )

  addParam(
    params,
    "status",
    status
  )

  addBooleanParam(
    params,
    "is_main_checklist",
    isMainChecklist
  )

  addParam(
    params,
    "ordering",
    ordering
  )

  return request(
    buildUrl(
      `${CHECKLISTS_URL}/`,
      params
    )
  )
}


export async function getRepairChecklist(
  checklistId
) {
  return getResource(
    CHECKLISTS_URL,
    checklistId
  )
}


export async function createRepairChecklist(
  checklistData
) {
  return createResource(
    CHECKLISTS_URL,
    checklistData
  )
}


export async function updateRepairChecklist(
  checklistId,
  checklistData
) {
  return updateResource(
    CHECKLISTS_URL,
    checklistId,
    checklistData
  )
}


export async function startRepairChecklist(
  checklistId,
  observations = ""
) {
  return resourceAction(
    CHECKLISTS_URL,
    checklistId,
    "start",
    {
      observations,
    }
  )
}


export async function completeRepairChecklist(
  checklistId,
  observations = ""
) {
  return resourceAction(
    CHECKLISTS_URL,
    checklistId,
    "complete",
    {
      observations,
    }
  )
}


export async function reopenRepairChecklist(
  checklistId,
  reason
) {
  return resourceAction(
    CHECKLISTS_URL,
    checklistId,
    "reopen",
    {
      reason,
    }
  )
}


export async function archiveRepairChecklist(
  checklistId,
  reason = ""
) {
  return resourceAction(
    CHECKLISTS_URL,
    checklistId,
    "archive",
    {
      reason,
    }
  )
}


export async function restoreRepairChecklist(
  checklistId
) {
  return resourceAction(
    CHECKLISTS_URL,
    checklistId,
    "restore"
  )
}


export async function loadRepairChecklistCompatibleComponents(
  checklistId
) {
  return resourceAction(
    CHECKLISTS_URL,
    checklistId,
    "load-compatible-components"
  )
}


/* ============================================================= */
/* PUNTOS DEL CHECKLIST                                          */
/* ============================================================= */

export async function getRepairChecklistItems({
  search = "",
  includeArchived = false,
  checklist = "",
  repair = "",
  component = "",
  category = "",
  status = "",
  isRequired = "",
  requiresPhoto = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  addArchivedParam(
    params,
    includeArchived
  )

  addParam(
    params,
    "checklist",
    checklist
  )

  addParam(
    params,
    "repair",
    repair
  )

  addParam(
    params,
    "component",
    component
  )

  addParam(
    params,
    "category",
    category
  )

  addParam(
    params,
    "status",
    status
  )

  addBooleanParam(
    params,
    "is_required",
    isRequired
  )

  addBooleanParam(
    params,
    "requires_photo",
    requiresPhoto
  )

  addParam(
    params,
    "ordering",
    ordering
  )

  return request(
    buildUrl(
      `${CHECKLIST_ITEMS_URL}/`,
      params
    )
  )
}


export async function getRepairChecklistItem(
  itemId
) {
  return getResource(
    CHECKLIST_ITEMS_URL,
    itemId
  )
}


export async function createRepairChecklistItem(
  itemData
) {
  return createResource(
    CHECKLIST_ITEMS_URL,
    itemData
  )
}


export async function updateRepairChecklistItem(
  itemId,
  itemData
) {
  return updateResource(
    CHECKLIST_ITEMS_URL,
    itemId,
    itemData
  )
}


export async function reviewRepairChecklistItem(
  itemId,
  reviewData
) {
  return resourceAction(
    CHECKLIST_ITEMS_URL,
    itemId,
    "review",
    reviewData
  )
}


export async function archiveRepairChecklistItem(
  itemId,
  reason = ""
) {
  return resourceAction(
    CHECKLIST_ITEMS_URL,
    itemId,
    "archive",
    {
      reason,
    }
  )
}


export async function restoreRepairChecklistItem(
  itemId
) {
  return resourceAction(
    CHECKLIST_ITEMS_URL,
    itemId,
    "restore"
  )
}


/* ============================================================= */
/* DIAGNÓSTICOS                                                  */
/* ============================================================= */

export async function getRepairDiagnoses({
  search = "",
  includeArchived = false,
  repair = "",
  equipment = "",
  technician = "",
  diagnosisType = "",
  severity = "",
  repairability = "",
  isMainDiagnosis = "",
  isConfirmed = "",
  requiresParts = "",
  requiresExternalService = "",
  requiresAdditionalTesting = "",
  requiresDisassembly = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  addArchivedParam(
    params,
    includeArchived
  )

  addParam(
    params,
    "repair",
    repair
  )

  addParam(
    params,
    "equipment",
    equipment
  )

  addParam(
    params,
    "technician",
    technician
  )

  addParam(
    params,
    "diagnosis_type",
    diagnosisType
  )

  addParam(
    params,
    "severity",
    severity
  )

  addParam(
    params,
    "repairability",
    repairability
  )

  addBooleanParam(
    params,
    "is_main_diagnosis",
    isMainDiagnosis
  )

  addBooleanParam(
    params,
    "is_confirmed",
    isConfirmed
  )

  addBooleanParam(
    params,
    "requires_parts",
    requiresParts
  )

  addBooleanParam(
    params,
    "requires_external_service",
    requiresExternalService
  )

  addBooleanParam(
    params,
    "requires_additional_testing",
    requiresAdditionalTesting
  )

  addBooleanParam(
    params,
    "requires_disassembly",
    requiresDisassembly
  )

  addParam(
    params,
    "ordering",
    ordering
  )

  return request(
    buildUrl(
      `${DIAGNOSES_URL}/`,
      params
    )
  )
}


export async function getRepairDiagnosis(
  diagnosisId
) {
  return getResource(
    DIAGNOSES_URL,
    diagnosisId
  )
}


export async function createRepairDiagnosis(
  diagnosisData
) {
  return createResource(
    DIAGNOSES_URL,
    diagnosisData
  )
}


export async function updateRepairDiagnosis(
  diagnosisId,
  diagnosisData
) {
  return updateResource(
    DIAGNOSES_URL,
    diagnosisId,
    diagnosisData
  )
}


export async function confirmRepairDiagnosis(
  diagnosisId,
  confirmationData = {}
) {
  return resourceAction(
    DIAGNOSES_URL,
    diagnosisId,
    "confirm",
    confirmationData
  )
}


export async function setMainRepairDiagnosis(
  diagnosisId
) {
  return resourceAction(
    DIAGNOSES_URL,
    diagnosisId,
    "set-main"
  )
}


export async function archiveRepairDiagnosis(
  diagnosisId,
  reason = ""
) {
  return resourceAction(
    DIAGNOSES_URL,
    diagnosisId,
    "archive",
    {
      reason,
    }
  )
}


export async function restoreRepairDiagnosis(
  diagnosisId
) {
  return resourceAction(
    DIAGNOSES_URL,
    diagnosisId,
    "restore"
  )
}


/* ============================================================= */
/* COMPONENTES Y REPUESTOS                                       */
/* ============================================================= */

export async function getRepairComponents({
  search = "",
  includeArchived = false,
  repair = "",
  equipment = "",
  component = "",
  inventory = "",
  movementType = "",
  status = "",
  hasInventory = "",
  hasRemovedComponent = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  addArchivedParam(
    params,
    includeArchived
  )

  addParam(
    params,
    "repair",
    repair
  )

  addParam(
    params,
    "equipment",
    equipment
  )

  addParam(
    params,
    "component",
    component
  )

  addParam(
    params,
    "inventory",
    inventory
  )

  addParam(
    params,
    "movement_type",
    movementType
  )

  addParam(
    params,
    "status",
    status
  )

  addBooleanParam(
    params,
    "has_inventory",
    hasInventory
  )

  addBooleanParam(
    params,
    "has_removed_component",
    hasRemovedComponent
  )

  addParam(
    params,
    "ordering",
    ordering
  )

  return request(
    buildUrl(
      `${COMPONENTS_URL}/`,
      params
    )
  )
}


export async function getRepairComponent(
  repairComponentId
) {
  return getResource(
    COMPONENTS_URL,
    repairComponentId
  )
}


export async function createRepairComponent(
  componentData
) {
  return createResource(
    COMPONENTS_URL,
    componentData
  )
}


export async function updateRepairComponent(
  repairComponentId,
  componentData
) {
  return updateResource(
    COMPONENTS_URL,
    repairComponentId,
    componentData
  )
}


export async function requestRepairComponent(
  repairComponentId,
  notes = ""
) {
  return resourceAction(
    COMPONENTS_URL,
    repairComponentId,
    "request-component",
    {
      notes,
    }
  )
}


export async function reserveRepairComponent(
  repairComponentId,
  reservationData
) {
  return resourceAction(
    COMPONENTS_URL,
    repairComponentId,
    "reserve",
    reservationData
  )
}


export async function deliverRepairComponent(
  repairComponentId,
  deliveryData
) {
  return resourceAction(
    COMPONENTS_URL,
    repairComponentId,
    "deliver",
    deliveryData
  )
}


export async function installRepairComponent(
  repairComponentId,
  installationData
) {
  return resourceAction(
    COMPONENTS_URL,
    repairComponentId,
    "install",
    installationData
  )
}


export async function consumeRepairComponent(
  repairComponentId,
  consumptionData
) {
  return resourceAction(
    COMPONENTS_URL,
    repairComponentId,
    "consume",
    consumptionData
  )
}


export async function returnRepairComponent(
  repairComponentId,
  returnData
) {
  return resourceAction(
    COMPONENTS_URL,
    repairComponentId,
    "return",
    returnData
  )
}


export async function cancelRepairComponent(
  repairComponentId,
  reason
) {
  return resourceAction(
    COMPONENTS_URL,
    repairComponentId,
    "cancel",
    {
      reason,
    }
  )
}


export async function archiveRepairComponent(
  repairComponentId,
  reason = ""
) {
  return resourceAction(
    COMPONENTS_URL,
    repairComponentId,
    "archive",
    {
      reason,
    }
  )
}


export async function restoreRepairComponent(
  repairComponentId
) {
  return resourceAction(
    COMPONENTS_URL,
    repairComponentId,
    "restore"
  )
}


/* ============================================================= */
/* FOTOGRAFÍAS                                                   */
/* ============================================================= */

export async function getRepairPhotos({
  search = "",
  includeArchived = false,
  repair = "",
  equipment = "",
  checklistItem = "",
  category = "",
  stage = "",
  takenBy = "",
  uploadedBy = "",
  isRequired = "",
  countsForMinimum = "",
  isVerified = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  addArchivedParam(
    params,
    includeArchived
  )

  addParam(
    params,
    "repair",
    repair
  )

  addParam(
    params,
    "equipment",
    equipment
  )

  addParam(
    params,
    "checklist_item",
    checklistItem
  )

  addParam(
    params,
    "category",
    category
  )

  addParam(
    params,
    "stage",
    stage
  )

  addParam(
    params,
    "taken_by",
    takenBy
  )

  addParam(
    params,
    "uploaded_by",
    uploadedBy
  )

  addBooleanParam(
    params,
    "is_required",
    isRequired
  )

  addBooleanParam(
    params,
    "counts_for_minimum",
    countsForMinimum
  )

  addBooleanParam(
    params,
    "is_verified",
    isVerified
  )

  addParam(
    params,
    "ordering",
    ordering
  )

  return request(
    buildUrl(
      `${PHOTOS_URL}/`,
      params
    )
  )
}


export async function getRepairPhoto(
  photoId
) {
  return getResource(
    PHOTOS_URL,
    photoId
  )
}


export async function createRepairPhoto(
  photoData
) {
  const formData =
    photoData instanceof FormData
      ? photoData
      : buildRepairPhotoFormData(
          photoData
        )

  return request(
    `${PHOTOS_URL}/`,
    {
      method: "POST",
      body: formData,
    }
  )
}


export async function updateRepairPhoto(
  photoId,
  photoData
) {
  const formData =
    photoData instanceof FormData
      ? photoData
      : buildRepairPhotoFormData(
          photoData
        )

  return request(
    `${PHOTOS_URL}/${photoId}/`,
    {
      method: "PATCH",
      body: formData,
    }
  )
}


export function buildRepairPhotoFormData(
  photoData
) {
  const formData =
    new FormData()

  const fields = (
    photoData || {}
  )

  for (
    const [
      key,
      value,
    ]
    of Object.entries(fields)
  ) {
    if (
      value === undefined ||
      value === null ||
      value === ""
    ) {
      continue
    }

    if (
      typeof value === "boolean"
    ) {
      formData.append(
        key,
        String(value)
      )

      continue
    }

    formData.append(
      key,
      value
    )
  }

  return formData
}


export async function verifyRepairPhoto(
  photoId,
  verificationNotes = ""
) {
  return resourceAction(
    PHOTOS_URL,
    photoId,
    "verify",
    {
      verification_notes:
        verificationNotes,
    }
  )
}


export async function removeRepairPhotoVerification(
  photoId,
  reason
) {
  return resourceAction(
    PHOTOS_URL,
    photoId,
    "remove-verification",
    {
      reason,
    }
  )
}


export async function archiveRepairPhoto(
  photoId,
  reason = ""
) {
  return resourceAction(
    PHOTOS_URL,
    photoId,
    "archive",
    {
      reason,
    }
  )
}


export async function restoreRepairPhoto(
  photoId
) {
  return resourceAction(
    PHOTOS_URL,
    photoId,
    "restore"
  )
}


/* ============================================================= */
/* PRUEBAS TÉCNICAS                                              */
/* ============================================================= */

export async function getRepairTests({
  search = "",
  includeArchived = false,
  repair = "",
  equipment = "",
  testType = "",
  status = "",
  result = "",
  performedBy = "",
  verifiedBy = "",
  isRequired = "",
  isVerified = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  addArchivedParam(
    params,
    includeArchived
  )

  addParam(
    params,
    "repair",
    repair
  )

  addParam(
    params,
    "equipment",
    equipment
  )

  addParam(
    params,
    "test_type",
    testType
  )

  addParam(
    params,
    "status",
    status
  )

  addParam(
    params,
    "result",
    result
  )

  addParam(
    params,
    "performed_by",
    performedBy
  )

  addParam(
    params,
    "verified_by",
    verifiedBy
  )

  addBooleanParam(
    params,
    "is_required",
    isRequired
  )

  addBooleanParam(
    params,
    "is_verified",
    isVerified
  )

  addParam(
    params,
    "ordering",
    ordering
  )

  return request(
    buildUrl(
      `${TESTS_URL}/`,
      params
    )
  )
}


export async function getRepairTest(
  testId
) {
  return getResource(
    TESTS_URL,
    testId
  )
}


export async function createRepairTest(
  testData
) {
  return createResource(
    TESTS_URL,
    testData
  )
}


export async function updateRepairTest(
  testId,
  testData
) {
  return updateResource(
    TESTS_URL,
    testId,
    testData
  )
}


export async function performRepairTest(
  testId,
  resultData
) {
  return resourceAction(
    TESTS_URL,
    testId,
    "perform",
    resultData
  )
}


export async function verifyRepairTest(
  testId,
  verificationNotes = ""
) {
  return resourceAction(
    TESTS_URL,
    testId,
    "verify",
    {
      verification_notes:
        verificationNotes,
    }
  )
}


export async function removeRepairTestVerification(
  testId,
  reason
) {
  return resourceAction(
    TESTS_URL,
    testId,
    "remove-verification",
    {
      reason,
    }
  )
}


export async function resetRepairTest(
  testId,
  reason
) {
  return resourceAction(
    TESTS_URL,
    testId,
    "reset",
    {
      reason,
    }
  )
}


export async function archiveRepairTest(
  testId,
  reason = ""
) {
  return resourceAction(
    TESTS_URL,
    testId,
    "archive",
    {
      reason,
    }
  )
}


export async function restoreRepairTest(
  testId
) {
  return resourceAction(
    TESTS_URL,
    testId,
    "restore"
  )
}


/* ============================================================= */
/* VALIDACIONES SNMP                                             */
/* ============================================================= */

export async function getRepairSNMPValidations({
  search = "",
  includeArchived = false,
  repair = "",
  equipment = "",
  host = "",
  status = "",
  isSuccessful = "",
  serialMatches = "",
  brandMatches = "",
  modelMatches = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  addArchivedParam(
    params,
    includeArchived
  )

  addParam(
    params,
    "repair",
    repair
  )

  addParam(
    params,
    "equipment",
    equipment
  )

  addParam(
    params,
    "host",
    host
  )

  addParam(
    params,
    "status",
    status
  )

  addBooleanParam(
    params,
    "is_successful",
    isSuccessful
  )

  addBooleanParam(
    params,
    "serial_matches",
    serialMatches
  )

  addBooleanParam(
    params,
    "brand_matches",
    brandMatches
  )

  addBooleanParam(
    params,
    "model_matches",
    modelMatches
  )

  addParam(
    params,
    "ordering",
    ordering
  )

  return request(
    buildUrl(
      `${SNMP_VALIDATIONS_URL}/`,
      params
    )
  )
}


export async function getRepairSNMPValidation(
  validationId
) {
  return getResource(
    SNMP_VALIDATIONS_URL,
    validationId
  )
}


export async function createRepairSNMPValidation(
  validationData
) {
  return createResource(
    SNMP_VALIDATIONS_URL,
    validationData
  )
}


export async function updateRepairSNMPValidation(
  validationId,
  validationData
) {
  return updateResource(
    SNMP_VALIDATIONS_URL,
    validationId,
    validationData
  )
}


export async function startRepairSNMPValidation(
  validationId,
  connectionData = {}
) {
  return resourceAction(
    SNMP_VALIDATIONS_URL,
    validationId,
    "start",
    connectionData
  )
}


export async function completeRepairSNMPValidation(
  validationId,
  completionData = {}
) {
  return resourceAction(
    SNMP_VALIDATIONS_URL,
    validationId,
    "complete",
    completionData
  )
}


export async function failRepairSNMPValidation(
  validationId,
  failureData
) {
  return resourceAction(
    SNMP_VALIDATIONS_URL,
    validationId,
    "fail",
    failureData
  )
}


export async function recalculateRepairSNMPMatches(
  validationId
) {
  return resourceAction(
    SNMP_VALIDATIONS_URL,
    validationId,
    "recalculate-matches"
  )
}


export async function archiveRepairSNMPValidation(
  validationId,
  reason = ""
) {
  return resourceAction(
    SNMP_VALIDATIONS_URL,
    validationId,
    "archive",
    {
      reason,
    }
  )
}


export async function restoreRepairSNMPValidation(
  validationId
) {
  return resourceAction(
    SNMP_VALIDATIONS_URL,
    validationId,
    "restore"
  )
}


/* ============================================================= */
/* HISTORIAL DE ESTADOS                                          */
/* ============================================================= */

export async function getRepairStatusHistory({
  search = "",
  includeArchived = false,
  repair = "",
  equipment = "",
  changedBy = "",
  previousStatus = "",
  newStatus = "",
  changedAutomatically = "",
  source = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  addArchivedParam(
    params,
    includeArchived
  )

  addParam(
    params,
    "repair",
    repair
  )

  addParam(
    params,
    "equipment",
    equipment
  )

  addParam(
    params,
    "changed_by",
    changedBy
  )

  addParam(
    params,
    "previous_status",
    previousStatus
  )

  addParam(
    params,
    "new_status",
    newStatus
  )

  addBooleanParam(
    params,
    "changed_automatically",
    changedAutomatically
  )

  addParam(
    params,
    "source",
    source
  )

  addParam(
    params,
    "ordering",
    ordering
  )

  return request(
    buildUrl(
      `${STATUS_HISTORY_URL}/`,
      params
    )
  )
}


export async function getRepairStatusHistoryItem(
  historyId
) {
  return getResource(
    STATUS_HISTORY_URL,
    historyId
  )
}


/* ============================================================= */
/* SOLICITUDES DE PARTES Y REPUESTOS                             */
/* ============================================================= */

export async function getRepairPartRequests({
  search = "",
  includeArchived = false,
  repair = "",
  status = "",
  priority = "",
  requestedBy = "",
  currentResponsibleArea = "",
  currentResponsibleUser = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(
    params,
    "search",
    search
  )

  addArchivedParam(
    params,
    includeArchived
  )

  addParam(
    params,
    "repair",
    repair
  )

  addParam(
    params,
    "status",
    status
  )

  addParam(
    params,
    "priority",
    priority
  )

  addParam(
    params,
    "requested_by",
    requestedBy
  )

  addParam(
    params,
    "current_responsible_area",
    currentResponsibleArea
  )

  addParam(
    params,
    "current_responsible_user",
    currentResponsibleUser
  )

  addParam(
    params,
    "ordering",
    ordering
  )

  return request(
    buildUrl(
      `${PART_REQUESTS_URL}/`,
      params
    )
  )
}


export async function getRepairPartRequest(
  requestId
) {
  return getResource(
    PART_REQUESTS_URL,
    requestId
  )
}


export async function createRepairPartRequest(
  requestData
) {
  return createResource(
    PART_REQUESTS_URL,
    requestData
  )
}


export async function updateRepairPartRequest(
  requestId,
  requestData
) {
  return updateResource(
    PART_REQUESTS_URL,
    requestId,
    requestData
  )
}


export async function deleteRepairPartRequest(
  requestId
) {
  return deleteResource(
    PART_REQUESTS_URL,
    requestId
  )
}


export async function submitRepairPartRequest(
  requestId,
  submitData = {}
) {
  return resourceAction(
    PART_REQUESTS_URL,
    requestId,
    "submit",
    submitData
  )
}


export async function cancelRepairPartRequest(
  requestId,
  cancellationData
) {
  return resourceAction(
    PART_REQUESTS_URL,
    requestId,
    "cancel",
    cancellationData
  )
}


export async function closeRepairPartRequest(
  requestId,
  closeData = {}
) {
  return resourceAction(
    PART_REQUESTS_URL,
    requestId,
    "close",
    closeData
  )
}


export async function archiveRepairPartRequest(
  requestId,
  reason = ""
) {
  return resourceAction(
    PART_REQUESTS_URL,
    requestId,
    "archive",
    {
      reason,
    }
  )
}


export async function restoreRepairPartRequest(
  requestId
) {
  return resourceAction(
    PART_REQUESTS_URL,
    requestId,
    "restore"
  )
}


/* ============================================================= */
/* ÍTEMS DE SOLICITUDES DE PARTES                                */
/* ============================================================= */

export async function getRepairPartRequestItems({
  search = "",
  includeArchived = false,
  request: requestId = "",
  repair = "",
  status = "",
  urgency = "",
  approvalRoute = "",
  sourceType = "",
  component = "",
  requestedBy = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(params, "search", search)
  addArchivedParam(params, includeArchived)
  addParam(params, "request", requestId)
  addParam(params, "repair", repair)
  addParam(params, "status", status)
  addParam(params, "urgency", urgency)
  addParam(
    params,
    "approval_route",
    approvalRoute
  )
  addParam(
    params,
    "source_type",
    sourceType
  )
  addParam(params, "component", component)
  addParam(
    params,
    "requested_by",
    requestedBy
  )
  addParam(params, "ordering", ordering)

  return request(
    buildUrl(
      `${PART_REQUEST_ITEMS_URL}/`,
      params
    )
  )
}


export async function getRepairPartRequestItem(
  itemId
) {
  return getResource(
    PART_REQUEST_ITEMS_URL,
    itemId
  )
}


export async function createRepairPartRequestItem(
  itemData
) {
  return createResource(
    PART_REQUEST_ITEMS_URL,
    itemData
  )
}


export async function updateRepairPartRequestItem(
  itemId,
  itemData
) {
  return updateResource(
    PART_REQUEST_ITEMS_URL,
    itemId,
    itemData
  )
}


export async function deleteRepairPartRequestItem(
  itemId
) {
  return deleteResource(
    PART_REQUEST_ITEMS_URL,
    itemId
  )
}


export async function archiveRepairPartRequestItem(
  itemId,
  reason = ""
) {
  return resourceAction(
    PART_REQUEST_ITEMS_URL,
    itemId,
    "archive",
    {
      reason,
    }
  )
}


export async function restoreRepairPartRequestItem(
  itemId
) {
  return resourceAction(
    PART_REQUEST_ITEMS_URL,
    itemId,
    "restore"
  )
}


/* ============================================================= */
/* REVISIONES DEL JEFE DE ÁREA                                   */
/* ============================================================= */

export async function getRepairPartRequestReviews({
  search = "",
  includeArchived = false,
  item = "",
  request: requestId = "",
  result = "",
  reviewedBy = "",
  isCurrent = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(params, "search", search)
  addArchivedParam(params, includeArchived)
  addParam(params, "item", item)
  addParam(params, "request", requestId)
  addParam(params, "result", result)
  addParam(
    params,
    "reviewed_by",
    reviewedBy
  )
  addBooleanParam(
    params,
    "is_current",
    isCurrent
  )
  addParam(params, "ordering", ordering)

  return request(
    buildUrl(
      `${PART_REQUEST_REVIEWS_URL}/`,
      params
    )
  )
}


export async function getRepairPartRequestReview(
  reviewId
) {
  return getResource(
    PART_REQUEST_REVIEWS_URL,
    reviewId
  )
}


export async function createRepairPartRequestReview(
  reviewData
) {
  return createResource(
    PART_REQUEST_REVIEWS_URL,
    reviewData
  )
}


/* ============================================================= */
/* DECISIONES DE GERENCIA                                        */
/* ============================================================= */

export async function getRepairPartRequestDecisions({
  search = "",
  includeArchived = false,
  request: requestId = "",
  item = "",
  decision = "",
  decidedBy = "",
  isFinal = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(params, "search", search)
  addArchivedParam(params, includeArchived)
  addParam(params, "request", requestId)
  addParam(params, "item", item)
  addParam(params, "decision", decision)
  addParam(
    params,
    "decided_by",
    decidedBy
  )
  addBooleanParam(
    params,
    "is_final",
    isFinal
  )
  addParam(params, "ordering", ordering)

  return request(
    buildUrl(
      `${PART_REQUEST_DECISIONS_URL}/`,
      params
    )
  )
}


export async function getRepairPartRequestDecision(
  decisionId
) {
  return getResource(
    PART_REQUEST_DECISIONS_URL,
    decisionId
  )
}


export async function createRepairPartRequestDecision(
  decisionData
) {
  return createResource(
    PART_REQUEST_DECISIONS_URL,
    decisionData
  )
}


/* ============================================================= */
/* ORÍGENES DE PARTES                                            */
/* ============================================================= */

export async function getRepairPartSources({
  search = "",
  includeArchived = false,
  item = "",
  request: requestId = "",
  sourceType = "",
  inventory = "",
  donorEquipment = "",
  rentalWarehouse = "",
  isConfirmed = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(params, "search", search)
  addArchivedParam(params, includeArchived)
  addParam(params, "item", item)
  addParam(params, "request", requestId)
  addParam(
    params,
    "source_type",
    sourceType
  )
  addParam(params, "inventory", inventory)
  addParam(
    params,
    "donor_equipment",
    donorEquipment
  )
  addParam(
    params,
    "rental_warehouse",
    rentalWarehouse
  )
  addBooleanParam(
    params,
    "is_confirmed",
    isConfirmed
  )
  addParam(params, "ordering", ordering)

  return request(
    buildUrl(
      `${PART_SOURCES_URL}/`,
      params
    )
  )
}


export async function getRepairPartSource(
  sourceId
) {
  return getResource(
    PART_SOURCES_URL,
    sourceId
  )
}


export async function createRepairPartSource(
  sourceData
) {
  return createResource(
    PART_SOURCES_URL,
    sourceData
  )
}


export async function updateRepairPartSource(
  sourceId,
  sourceData
) {
  return updateResource(
    PART_SOURCES_URL,
    sourceId,
    sourceData
  )
}


/* ============================================================= */
/* RETIROS DE PARTES                                             */
/* ============================================================= */

export async function getRepairPartWithdrawals({
  search = "",
  includeArchived = false,
  item = "",
  request: requestId = "",
  status = "",
  authorizedPerson = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(params, "search", search)
  addArchivedParam(params, includeArchived)
  addParam(params, "item", item)
  addParam(params, "request", requestId)
  addParam(params, "status", status)
  addParam(
    params,
    "authorized_person",
    authorizedPerson
  )
  addParam(params, "ordering", ordering)

  return request(
    buildUrl(
      `${PART_WITHDRAWALS_URL}/`,
      params
    )
  )
}


export async function getRepairPartWithdrawal(
  withdrawalId
) {
  return getResource(
    PART_WITHDRAWALS_URL,
    withdrawalId
  )
}


export async function createRepairPartWithdrawal(
  withdrawalData
) {
  return createResource(
    PART_WITHDRAWALS_URL,
    withdrawalData
  )
}


export async function authorizeRepairPartWithdrawal(
  withdrawalId,
  authorizationData
) {
  return resourceAction(
    PART_WITHDRAWALS_URL,
    withdrawalId,
    "authorize",
    authorizationData
  )
}


export async function confirmRepairPartWithdrawal(
  withdrawalId,
  confirmationData = {}
) {
  return resourceAction(
    PART_WITHDRAWALS_URL,
    withdrawalId,
    "confirm-withdrawal",
    confirmationData
  )
}


export async function receiveRepairPartWithdrawal(
  withdrawalId,
  receptionData = {}
) {
  return resourceAction(
    PART_WITHDRAWALS_URL,
    withdrawalId,
    "receive",
    receptionData
  )
}


/* ============================================================= */
/* ENTREGAS DE PARTES                                            */
/* ============================================================= */

export async function getRepairPartDeliveries({
  search = "",
  includeArchived = false,
  item = "",
  request: requestId = "",
  status = "",
  deliveredTo = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(params, "search", search)
  addArchivedParam(params, includeArchived)
  addParam(params, "item", item)
  addParam(params, "request", requestId)
  addParam(params, "status", status)
  addParam(
    params,
    "delivered_to",
    deliveredTo
  )
  addParam(params, "ordering", ordering)

  return request(
    buildUrl(
      `${PART_DELIVERIES_URL}/`,
      params
    )
  )
}


export async function getRepairPartDelivery(
  deliveryId
) {
  return getResource(
    PART_DELIVERIES_URL,
    deliveryId
  )
}


export async function createRepairPartDelivery(
  deliveryData
) {
  return createResource(
    PART_DELIVERIES_URL,
    deliveryData
  )
}


export async function prepareRepairPartDelivery(
  deliveryId,
  preparationData = {}
) {
  return resourceAction(
    PART_DELIVERIES_URL,
    deliveryId,
    "prepare",
    preparationData
  )
}


export async function deliverRepairPart(
  deliveryId,
  deliveryData
) {
  return resourceAction(
    PART_DELIVERIES_URL,
    deliveryId,
    "deliver",
    deliveryData
  )
}


export async function receiveRepairPartDelivery(
  deliveryId,
  receptionData
) {
  return resourceAction(
    PART_DELIVERIES_URL,
    deliveryId,
    "receive",
    receptionData
  )
}


/* ============================================================= */
/* REPOSICIONES                                                  */
/* ============================================================= */

export async function getRepairPartReplacements({
  search = "",
  includeArchived = false,
  item = "",
  request: requestId = "",
  status = "",
  replacementType = "",
  sourceEquipment = "",
  responsibleUser = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(params, "search", search)
  addArchivedParam(params, includeArchived)
  addParam(params, "item", item)
  addParam(params, "request", requestId)
  addParam(params, "status", status)
  addParam(
    params,
    "replacement_type",
    replacementType
  )
  addParam(
    params,
    "source_equipment",
    sourceEquipment
  )
  addParam(
    params,
    "responsible_user",
    responsibleUser
  )
  addParam(params, "ordering", ordering)

  return request(
    buildUrl(
      `${PART_REPLACEMENTS_URL}/`,
      params
    )
  )
}


export async function getRepairPartReplacement(
  replacementId
) {
  return getResource(
    PART_REPLACEMENTS_URL,
    replacementId
  )
}


export async function createRepairPartReplacement(
  replacementData
) {
  return createResource(
    PART_REPLACEMENTS_URL,
    replacementData
  )
}


export async function updateRepairPartReplacement(
  replacementId,
  replacementData
) {
  return updateResource(
    PART_REPLACEMENTS_URL,
    replacementId,
    replacementData
  )
}


export async function completeRepairPartReplacement(
  replacementId,
  completionData = {}
) {
  return resourceAction(
    PART_REPLACEMENTS_URL,
    replacementId,
    "complete",
    completionData
  )
}


/* ============================================================= */
/* COMENTARIOS                                                   */
/* ============================================================= */

export async function getRepairPartRequestComments({
  search = "",
  includeArchived = false,
  request: requestId = "",
  item = "",
  author = "",
  commentType = "",
  isInternal = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(params, "search", search)
  addArchivedParam(params, includeArchived)
  addParam(params, "request", requestId)
  addParam(params, "item", item)
  addParam(params, "author", author)
  addParam(
    params,
    "comment_type",
    commentType
  )
  addBooleanParam(
    params,
    "is_internal",
    isInternal
  )
  addParam(params, "ordering", ordering)

  return request(
    buildUrl(
      `${PART_REQUEST_COMMENTS_URL}/`,
      params
    )
  )
}


export async function getRepairPartRequestComment(
  commentId
) {
  return getResource(
    PART_REQUEST_COMMENTS_URL,
    commentId
  )
}


export async function createRepairPartRequestComment(
  commentData
) {
  return createResource(
    PART_REQUEST_COMMENTS_URL,
    commentData
  )
}


export async function deleteRepairPartRequestComment(
  commentId
) {
  return deleteResource(
    PART_REQUEST_COMMENTS_URL,
    commentId
  )
}


/* ============================================================= */
/* ADJUNTOS                                                      */
/* ============================================================= */

export function buildRepairPartRequestAttachmentFormData(
  attachmentData
) {
  const formData =
    new FormData()

  for (
    const [
      key,
      value,
    ]
    of Object.entries(
      attachmentData || {}
    )
  ) {
    if (
      value === undefined ||
      value === null ||
      value === ""
    ) {
      continue
    }

    formData.append(
      key,
      value
    )
  }

  return formData
}


export async function getRepairPartRequestAttachments({
  search = "",
  includeArchived = false,
  request: requestId = "",
  item = "",
  attachmentType = "",
  uploadedBy = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(params, "search", search)
  addArchivedParam(params, includeArchived)
  addParam(params, "request", requestId)
  addParam(params, "item", item)
  addParam(
    params,
    "attachment_type",
    attachmentType
  )
  addParam(
    params,
    "uploaded_by",
    uploadedBy
  )
  addParam(params, "ordering", ordering)

  return request(
    buildUrl(
      `${PART_REQUEST_ATTACHMENTS_URL}/`,
      params
    )
  )
}


export async function getRepairPartRequestAttachment(
  attachmentId
) {
  return getResource(
    PART_REQUEST_ATTACHMENTS_URL,
    attachmentId
  )
}


export async function createRepairPartRequestAttachment(
  attachmentData
) {
  const formData =
    attachmentData instanceof FormData
      ? attachmentData
      : buildRepairPartRequestAttachmentFormData(
          attachmentData
        )

  return request(
    `${PART_REQUEST_ATTACHMENTS_URL}/`,
    {
      method: "POST",
      body: formData,
    }
  )
}


export async function deleteRepairPartRequestAttachment(
  attachmentId
) {
  return deleteResource(
    PART_REQUEST_ATTACHMENTS_URL,
    attachmentId
  )
}


/* ============================================================= */
/* HISTORIAL DE SOLICITUDES                                      */
/* ============================================================= */

export async function getRepairPartRequestHistory({
  search = "",
  includeArchived = false,
  request: requestId = "",
  item = "",
  event = "",
  changedBy = "",
  source = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(params, "search", search)
  addArchivedParam(params, includeArchived)
  addParam(params, "request", requestId)
  addParam(params, "item", item)
  addParam(params, "event", event)
  addParam(
    params,
    "changed_by",
    changedBy
  )
  addParam(params, "source", source)
  addParam(params, "ordering", ordering)

  return request(
    buildUrl(
      `${PART_REQUEST_HISTORY_URL}/`,
      params
    )
  )
}


export async function getRepairPartRequestHistoryItem(
  historyId
) {
  return getResource(
    PART_REQUEST_HISTORY_URL,
    historyId
  )
}


/* ============================================================= */
/* NOTIFICACIONES DE SOLICITUDES                                 */
/* ============================================================= */

export async function getRepairPartRequestNotifications({
  search = "",
  includeArchived = false,
  request: requestId = "",
  item = "",
  event = "",
  channel = "",
  status = "",
  ordering = "",
} = {}) {
  const params =
    new URLSearchParams()

  addParam(params, "search", search)
  addArchivedParam(params, includeArchived)
  addParam(params, "request", requestId)
  addParam(params, "item", item)
  addParam(params, "event", event)
  addParam(params, "channel", channel)
  addParam(params, "status", status)
  addParam(params, "ordering", ordering)

  return request(
    buildUrl(
      `${PART_REQUEST_NOTIFICATIONS_URL}/`,
      params
    )
  )
}


export async function getRepairPartRequestNotification(
  notificationId
) {
  return getResource(
    PART_REQUEST_NOTIFICATIONS_URL,
    notificationId
  )
}


export async function markRepairPartRequestNotificationRead(
  notificationId
) {
  return resourceAction(
    PART_REQUEST_NOTIFICATIONS_URL,
    notificationId,
    "mark-read"
  )
}

