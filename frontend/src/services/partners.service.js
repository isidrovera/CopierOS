const API_URL =
  "http://127.0.0.1:8000/api/partners"

import {
  clearSession,
  getToken,
} from "./auth.service"


async function request(url, options = {}) {
  const token = getToken()

  const headers = {
    Accept: "application/json",
    ...options.headers,
  }

  if (token) {
    headers.Authorization = `Token ${token}`
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

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
  if (!data || typeof data !== "object") {
    return null
  }

  for (const value of Object.values(data)) {
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
/* CLIENTES, PROVEEDORES Y DISTRIBUIDORES                        */
/* ============================================================= */

export async function getPartners({
  search = "",
  includeArchived = false,
  isActive = "",
  role = "",
  personType = "",
  documentType = "",
  classification = "",
  countryCode = "",
  advisor = "",
  purchasingManager = "",
  isCommerciallyBlocked = "",
  documentVerified = "",
} = {}) {
  const params = new URLSearchParams()

  if (search.trim()) {
    params.set(
      "search",
      search.trim()
    )
  }

  if (includeArchived) {
    params.set(
      "include_archived",
      "true"
    )
  }

  if (role) {
    params.set(
      "role",
      role
    )
  }

  if (personType) {
    params.set(
      "person_type",
      personType
    )
  }

  if (documentType) {
    params.set(
      "document_type",
      documentType
    )
  }

  if (classification) {
    params.set(
      "classification",
      classification
    )
  }

  if (countryCode) {
    params.set(
      "country_code",
      countryCode
        .trim()
        .toUpperCase()
    )
  }

  if (advisor) {
    params.set(
      "advisor",
      advisor
    )
  }

  if (purchasingManager) {
    params.set(
      "purchasing_manager",
      purchasingManager
    )
  }

  addBooleanParam(
    params,
    "is_active",
    isActive
  )

  addBooleanParam(
    params,
    "is_commercially_blocked",
    isCommerciallyBlocked
  )

  addBooleanParam(
    params,
    "document_verified",
    documentVerified
  )

  return request(
    buildUrl(
      `${API_URL}/`,
      params
    )
  )
}


export async function getPartner(
  partnerId
) {
  return request(
    `${API_URL}/${partnerId}/`
  )
}


export async function createPartner(
  partnerData
) {
  return request(
    `${API_URL}/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(
        partnerData
      ),
    }
  )
}


export async function updatePartner(
  partnerId,
  partnerData
) {
  return request(
    `${API_URL}/${partnerId}/`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(
        partnerData
      ),
    }
  )
}


export async function archivePartner(
  partnerId,
  reason = ""
) {
  return request(
    `${API_URL}/${partnerId}/archive/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        reason,
      }),
    }
  )
}


export async function restorePartner(
  partnerId
) {
  return request(
    `${API_URL}/${partnerId}/restore/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  )
}


/* ============================================================= */
/* SUCURSALES Y SEDES                                            */
/* ============================================================= */

export async function getPartnerBranches({
  search = "",
  partner = "",
  includeArchived = false,
  branchType = "",
  isMain = "",
  isFiscal = "",
  allowsEquipmentInstallation = "",
  isActive = "",
} = {}) {
  const params = new URLSearchParams()

  if (search.trim()) {
    params.set(
      "search",
      search.trim()
    )
  }

  if (partner) {
    params.set(
      "partner",
      partner
    )
  }

  if (includeArchived) {
    params.set(
      "include_archived",
      "true"
    )
  }

  if (branchType) {
    params.set(
      "branch_type",
      branchType
    )
  }

  addBooleanParam(
    params,
    "is_main",
    isMain
  )

  addBooleanParam(
    params,
    "is_fiscal",
    isFiscal
  )

  addBooleanParam(
    params,
    "allows_equipment_installation",
    allowsEquipmentInstallation
  )

  addBooleanParam(
    params,
    "is_active",
    isActive
  )

  return request(
    buildUrl(
      `${API_URL}/branches/`,
      params
    )
  )
}


export async function getPartnerBranch(
  branchId
) {
  return request(
    `${API_URL}/branches/${branchId}/`
  )
}


export async function createPartnerBranch(
  branchData
) {
  return request(
    `${API_URL}/branches/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(
        branchData
      ),
    }
  )
}


export async function updatePartnerBranch(
  branchId,
  branchData
) {
  return request(
    `${API_URL}/branches/${branchId}/`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(
        branchData
      ),
    }
  )
}


export async function archivePartnerBranch(
  branchId,
  reason = ""
) {
  return request(
    `${API_URL}/branches/${branchId}/archive/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        reason,
      }),
    }
  )
}


export async function restorePartnerBranch(
  branchId
) {
  return request(
    `${API_URL}/branches/${branchId}/restore/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  )
}


/* ============================================================= */
/* CONTACTOS                                                     */
/* ============================================================= */

export async function getPartnerContacts({
  search = "",
  partner = "",
  branch = "",
  includeArchived = false,
  area = "",
  isPrimary = "",
  isActive = "",
  receivesBilling = "",
  receivesMeterRequests = "",
  receivesServiceNotifications = "",
} = {}) {
  const params = new URLSearchParams()

  if (search.trim()) {
    params.set(
      "search",
      search.trim()
    )
  }

  if (partner) {
    params.set(
      "partner",
      partner
    )
  }

  if (branch) {
    params.set(
      "branch",
      branch
    )
  }

  if (includeArchived) {
    params.set(
      "include_archived",
      "true"
    )
  }

  if (area) {
    params.set(
      "area",
      area
    )
  }

  addBooleanParam(
    params,
    "is_primary",
    isPrimary
  )

  addBooleanParam(
    params,
    "is_active",
    isActive
  )

  addBooleanParam(
    params,
    "receives_billing",
    receivesBilling
  )

  addBooleanParam(
    params,
    "receives_meter_requests",
    receivesMeterRequests
  )

  addBooleanParam(
    params,
    "receives_service_notifications",
    receivesServiceNotifications
  )

  return request(
    buildUrl(
      `${API_URL}/contacts/`,
      params
    )
  )
}


export async function getPartnerContact(
  contactId
) {
  return request(
    `${API_URL}/contacts/${contactId}/`
  )
}


export async function createPartnerContact(
  contactData
) {
  return request(
    `${API_URL}/contacts/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(
        contactData
      ),
    }
  )
}


export async function updatePartnerContact(
  contactId,
  contactData
) {
  return request(
    `${API_URL}/contacts/${contactId}/`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(
        contactData
      ),
    }
  )
}


export async function archivePartnerContact(
  contactId,
  reason = ""
) {
  return request(
    `${API_URL}/contacts/${contactId}/archive/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        reason,
      }),
    }
  )
}


export async function restorePartnerContact(
  contactId
) {
  return request(
    `${API_URL}/contacts/${contactId}/restore/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  )
}


/* ============================================================= */
/* HISTORIAL DE CONSULTAS DE DOCUMENTOS                           */
/* ============================================================= */

export async function getDocumentLookups({
  documentType = "",
  documentNumber = "",
  status = "",
  provider = "",
  requestedBy = "",
  partner = "",
  isSuccessful = "",
} = {}) {
  const params = new URLSearchParams()

  if (documentType) {
    params.set(
      "document_type",
      documentType
    )
  }

  if (documentNumber.trim()) {
    params.set(
      "document_number",
      documentNumber
        .replace(/\s+/g, "")
        .trim()
    )
  }

  if (status) {
    params.set(
      "status",
      status
    )
  }

  if (provider) {
    params.set(
      "provider",
      provider
    )
  }

  if (requestedBy) {
    params.set(
      "requested_by",
      requestedBy
    )
  }

  if (partner) {
    params.set(
      "partner",
      partner
    )
  }

  addBooleanParam(
    params,
    "is_successful",
    isSuccessful
  )

  return request(
    buildUrl(
      `${API_URL}/document-lookups/`,
      params
    )
  )
}


/* ============================================================= */
/* NOMBRES ABREVIADOS UTILIZADOS POR LOS COMPONENTES VUE         */
/* ============================================================= */

/*
 * Estos alias permiten que los componentes usen nombres como
 * getBranches o archiveContact sin duplicar las solicitudes.
 */

export const getBranches =
  getPartnerBranches

export const getBranch =
  getPartnerBranch

export const createBranch =
  createPartnerBranch

export const updateBranch =
  updatePartnerBranch

export const archiveBranch =
  archivePartnerBranch

export const restoreBranch =
  restorePartnerBranch


export const getContacts =
  getPartnerContacts

export const getContact =
  getPartnerContact

export const createContact =
  createPartnerContact

export const updateContact =
  updatePartnerContact

export const archiveContact =
  archivePartnerContact

export const restoreContact =
  restorePartnerContact