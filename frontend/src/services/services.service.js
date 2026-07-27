const API_ROOT = "http://127.0.0.1:8000/api/services"

import {
  clearSession,
  getToken,
} from "./auth.service"


const endpoints = {
  orders: `${API_ROOT}/orders`,
  assignmentHistory: `${API_ROOT}/assignment-history`,
  statusHistory: `${API_ROOT}/status-history`,
  trackingSessions: `${API_ROOT}/tracking-sessions`,
  trackingPoints: `${API_ROOT}/tracking-points`,
  checklists: `${API_ROOT}/checklists`,
  checklistItems: `${API_ROOT}/checklist-items`,
  partRequests: `${API_ROOT}/part-requests`,
  partRequestItems: `${API_ROOT}/part-request-items`,
  evidences: `${API_ROOT}/evidences`,
  meterReadings: `${API_ROOT}/meter-readings`,
}


function getValidationError(data) {
  if (
    !data
    || typeof data !== "object"
  ) {
    return null
  }

  for (
    const value
    of Object.values(data)
  ) {
    if (
      Array.isArray(value)
      && value.length
    ) {
      return String(value[0])
    }

    if (
      value
      && typeof value === "object"
    ) {
      const nestedError = (
        getValidationError(value)
      )

      if (nestedError) {
        return nestedError
      }
    }

    if (
      typeof value === "string"
      && value.trim()
    ) {
      return value
    }
  }

  return null
}


async function request(
  url,
  options = {},
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
    },
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
      "Tu sesión terminó. Inicia sesión nuevamente.",
    )
  }

  if (!response.ok) {
    throw new Error(
      data?.detail
      || getValidationError(data)
      || "Ocurrió un error al procesar la solicitud.",
    )
  }

  return data
}


function buildUrl(
  base,
  filters = {},
) {
  const params = new URLSearchParams()

  Object.entries(filters).forEach(
    ([key, value]) => {
      if (
        value === undefined
        || value === null
        || value === ""
      ) {
        return
      }

      params.set(
        key,
        String(value),
      )
    },
  )

  const query = params.toString()

  return query
    ? `${base}/?${query}`
    : `${base}/`
}


function jsonRequest(
  url,
  method,
  data = {},
) {
  return request(
    url,
    {
      method,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    },
  )
}


export function getServiceOrders(
  filters = {},
) {
  return request(
    buildUrl(
      endpoints.orders,
      filters,
    ),
  )
}


export function getServiceOrder(id) {
  return request(
    `${endpoints.orders}/${id}/`,
  )
}


export function createServiceOrder(data) {
  return jsonRequest(
    `${endpoints.orders}/`,
    "POST",
    data,
  )
}


export function updateServiceOrder(
  id,
  data,
) {
  return jsonRequest(
    `${endpoints.orders}/${id}/`,
    "PATCH",
    data,
  )
}


export function getServiceEquipmentOptions({
  serviceOrigin,
  search = "",
} = {}) {
  return request(
    buildUrl(
      `${endpoints.orders}/equipment-options`,
      {
        service_origin: serviceOrigin,
        search,
      },
    ),
  )
}


export function getServiceEquipmentSnapshot({
  equipment,
  serviceOrigin,
} = {}) {
  return request(
    buildUrl(
      `${endpoints.orders}/equipment-snapshot`,
      {
        equipment,
        service_origin: serviceOrigin,
      },
    ),
  )
}


export function serviceOrderAction(
  id,
  action,
  data = {},
) {
  return jsonRequest(
    `${endpoints.orders}/${id}/${action}/`,
    "POST",
    data,
  )
}


export function assignServiceTechnician(
  id,
  technician,
  reason = "",
) {
  return serviceOrderAction(
    id,
    "assign",
    {
      technician,
      reason,
    },
  )
}


export function changeServiceOrderStatus(
  id,
  status,
  data = {},
) {
  return serviceOrderAction(
    id,
    "change-status",
    {
      status,
      ...data,
    },
  )
}


export function generateServiceChecklist(id) {
  return serviceOrderAction(
    id,
    "generate-checklist",
  )
}


export function loadCurrentServiceSnapshot(id) {
  return serviceOrderAction(
    id,
    "load-current-snapshot",
  )
}


export function startServiceTracking(
  id,
  data = {},
) {
  return serviceOrderAction(
    id,
    "start-tracking",
    data,
  )
}


export function stopServiceTracking(
  id,
  data = {},
) {
  return serviceOrderAction(
    id,
    "stop-tracking",
    data,
  )
}


export function applyServiceMeterReading(id) {
  return serviceOrderAction(
    id,
    "apply-meter-reading",
  )
}


export function archiveServiceOrder(
  id,
  reason = "",
) {
  return serviceOrderAction(
    id,
    "archive",
    {
      reason,
    },
  )
}


export function restoreServiceOrder(id) {
  return serviceOrderAction(
    id,
    "restore",
  )
}


export function listServiceResource(
  resource,
  filters = {},
) {
  const endpoint = endpoints[resource]

  if (!endpoint) {
    throw new Error(
      `El recurso de servicios "${resource}" no existe.`,
    )
  }

  return request(
    buildUrl(
      endpoint,
      filters,
    ),
  )
}


export function getServiceResource(
  resource,
  id,
) {
  const endpoint = endpoints[resource]

  if (!endpoint) {
    throw new Error(
      `El recurso de servicios "${resource}" no existe.`,
    )
  }

  return request(
    `${endpoint}/${id}/`,
  )
}


export function createServiceResource(
  resource,
  data,
) {
  const endpoint = endpoints[resource]

  if (!endpoint) {
    throw new Error(
      `El recurso de servicios "${resource}" no existe.`,
    )
  }

  const url = `${endpoint}/`

  if (data instanceof FormData) {
    return request(
      url,
      {
        method: "POST",
        body: data,
      },
    )
  }

  return jsonRequest(
    url,
    "POST",
    data,
  )
}


export function updateServiceResource(
  resource,
  id,
  data,
) {
  const endpoint = endpoints[resource]

  if (!endpoint) {
    throw new Error(
      `El recurso de servicios "${resource}" no existe.`,
    )
  }

  const url = `${endpoint}/${id}/`

  if (data instanceof FormData) {
    return request(
      url,
      {
        method: "PATCH",
        body: data,
      },
    )
  }

  return jsonRequest(
    url,
    "PATCH",
    data,
  )
}


export function serviceResourceAction(
  resource,
  id,
  action,
  data = {},
) {
  const endpoint = endpoints[resource]

  if (!endpoint) {
    throw new Error(
      `El recurso de servicios "${resource}" no existe.`,
    )
  }

  return jsonRequest(
    `${endpoint}/${id}/${action}/`,
    "POST",
    data,
  )
}


export function getServiceChecklists(
  filters = {},
) {
  return listServiceResource(
    "checklists",
    filters,
  )
}


export function getServiceChecklist(id) {
  return getServiceResource(
    "checklists",
    id,
  )
}


export function updateServiceChecklist(
  id,
  data,
) {
  return updateServiceResource(
    "checklists",
    id,
    data,
  )
}


export function getServiceChecklistItems(
  filters = {},
) {
  return listServiceResource(
    "checklistItems",
    filters,
  )
}


export function getServiceChecklistItem(id) {
  return getServiceResource(
    "checklistItems",
    id,
  )
}


export function getCompatibleServiceSubparts(
  checklistItemId,
) {
  return request(
    (
      `${endpoints.checklistItems}/`
      + `${checklistItemId}/`
      + "compatible-subparts/"
    ),
  )
}


export function checkServiceChecklistItem(
  id,
  data,
) {
  return serviceResourceAction(
    "checklistItems",
    id,
    "check",
    data,
  )
}


export function saveServiceChecklistItem({
  id,
  status,
  observation = "",
  consumablePresent = null,
  consumableLevelPercent = null,
  subparts = [],
} = {}) {
  if (!id) {
    throw new Error(
      "Debe indicar el ítem del checklist.",
    )
  }

  return checkServiceChecklistItem(
    id,
    {
      status,
      observation,
      consumable_present: consumablePresent,
      consumable_level_percent: (
        consumableLevelPercent
      ),
      subparts: Array.isArray(subparts)
        ? subparts.map(
            (subpart) => ({
              component: (
                subpart.component
                || subpart.id
              ),
              quantity: (
                subpart.quantity
                ?? 1
              ),
              urgency: (
                subpart.urgency
                || "normal"
              ),
              reason: (
                subpart.reason
                || observation
              ),
              notes: (
                subpart.notes
                || ""
              ),
            }),
          )
        : [],
    },
  )
}


export function getServicePartRequests(
  filters = {},
) {
  return listServiceResource(
    "partRequests",
    filters,
  )
}


export function getServicePartRequest(id) {
  return getServiceResource(
    "partRequests",
    id,
  )
}


export function createServicePartRequest(data) {
  return createServiceResource(
    "partRequests",
    data,
  )
}


export function updateServicePartRequest(
  id,
  data,
) {
  return updateServiceResource(
    "partRequests",
    id,
    data,
  )
}


export function getServicePartRequestItems(
  filters = {},
) {
  return listServiceResource(
    "partRequestItems",
    filters,
  )
}


export function getServicePartRequestItem(id) {
  return getServiceResource(
    "partRequestItems",
    id,
  )
}


export function createServicePartRequestItem(
  data,
) {
  return createServiceResource(
    "partRequestItems",
    data,
  )
}


export function updateServicePartRequestItem(
  id,
  data,
) {
  return updateServiceResource(
    "partRequestItems",
    id,
    data,
  )
}


export function getServiceEvidences(
  filters = {},
) {
  return listServiceResource(
    "evidences",
    filters,
  )
}


export function getServiceEvidence(id) {
  return getServiceResource(
    "evidences",
    id,
  )
}


export function createServiceEvidence(data) {
  return createServiceResource(
    "evidences",
    data,
  )
}


export function updateServiceEvidence(
  id,
  data,
) {
  return updateServiceResource(
    "evidences",
    id,
    data,
  )
}


export function archiveServiceEvidence(
  id,
  reason = "",
) {
  return serviceResourceAction(
    "evidences",
    id,
    "archive",
    {
      reason,
    },
  )
}


export function restoreServiceEvidence(id) {
  return serviceResourceAction(
    "evidences",
    id,
    "restore",
  )
}


export function buildServiceEvidenceFormData({
  serviceOrder,
  stage,
  file,
  capturedAt,
  sequence = 1,
  notes = "",
  latitude = null,
  longitude = null,
  accuracyMeters = null,
  deviceId = "",
  isMockLocation = false,
} = {}) {
  if (!serviceOrder) {
    throw new Error(
      "Debe indicar la orden de servicio.",
    )
  }

  if (!stage) {
    throw new Error(
      "Debe indicar el tipo de evidencia.",
    )
  }

  if (!file) {
    throw new Error(
      "Debe seleccionar una fotografía.",
    )
  }

  const formData = new FormData()

  formData.append(
    "service_order",
    serviceOrder,
  )

  formData.append(
    "stage",
    stage,
  )

  formData.append(
    "file",
    file,
  )

  formData.append(
    "captured_at",
    (
      capturedAt
      || new Date().toISOString()
    ),
  )

  formData.append(
    "sequence",
    String(sequence),
  )

  formData.append(
    "notes",
    String(notes || "").trim(),
  )

  formData.append(
    "device_id",
    String(deviceId || "").trim(),
  )

  formData.append(
    "is_mock_location",
    isMockLocation
      ? "true"
      : "false",
  )

  if (
    latitude !== null
    && latitude !== undefined
    && latitude !== ""
  ) {
    formData.append(
      "latitude",
      String(latitude),
    )
  }

  if (
    longitude !== null
    && longitude !== undefined
    && longitude !== ""
  ) {
    formData.append(
      "longitude",
      String(longitude),
    )
  }

  if (
    accuracyMeters !== null
    && accuracyMeters !== undefined
    && accuracyMeters !== ""
  ) {
    formData.append(
      "accuracy_meters",
      String(accuracyMeters),
    )
  }

  return formData
}


export function uploadServiceEvidence(
  values,
) {
  const formData = (
    buildServiceEvidenceFormData(values)
  )

  return createServiceEvidence(
    formData,
  )
}


export function getServiceMeterReadings(
  filters = {},
) {
  return listServiceResource(
    "meterReadings",
    filters,
  )
}


export function getServiceMeterReading(id) {
  return getServiceResource(
    "meterReadings",
    id,
  )
}


export function createServiceMeterReading(
  data,
) {
  return createServiceResource(
    "meterReadings",
    data,
  )
}


export function updateServiceMeterReading(
  id,
  data,
) {
  return updateServiceResource(
    "meterReadings",
    id,
    data,
  )
}


export function getServiceStatusHistory(
  filters = {},
) {
  return listServiceResource(
    "statusHistory",
    filters,
  )
}


export function getServiceAssignmentHistory(
  filters = {},
) {
  return listServiceResource(
    "assignmentHistory",
    filters,
  )
}


export function getServiceTrackingSessions(
  filters = {},
) {
  return listServiceResource(
    "trackingSessions",
    filters,
  )
}


export function getServiceTrackingPoints(
  filters = {},
) {
  return listServiceResource(
    "trackingPoints",
    filters,
  )
}