const API_ROOT = "http://127.0.0.1:8000/api/rentals"

import { clearSession, getToken } from "./auth.service"

const endpoints = {
  warehouses: `${API_ROOT}/warehouses`, equipment: `${API_ROOT}/equipment`,
  movements: `${API_ROOT}/equipment-movements`, preparations: `${API_ROOT}/preparations`,
  contracts: `${API_ROOT}/contracts`, assignments: `${API_ROOT}/assignments`,
  installations: `${API_ROOT}/installations`, removals: `${API_ROOT}/removals`,
  replacements: `${API_ROOT}/replacements`, documents: `${API_ROOT}/documents`,
}

function validationError(data) {
  if (!data || typeof data !== "object") return null
  for (const value of Object.values(data)) {
    if (Array.isArray(value) && value.length) return String(value[0])
    if (value && typeof value === "object") {
      const nested = validationError(value)
      if (nested) return nested
    }
    if (typeof value === "string" && value.trim()) return value
  }
  return null
}

async function request(url, options = {}) {
  const token = getToken()
  const headers = { Accept: "application/json", ...options.headers }
  if (token) headers.Authorization = `Token ${token}`
  const response = await fetch(url, { ...options, headers })
  let data = null
  try { data = await response.json() } catch { data = null }
  if (response.status === 401) {
    clearSession(); window.location.href = "/login"
    throw new Error("Tu sesión terminó. Inicia sesión nuevamente.")
  }
  if (!response.ok) throw new Error(data?.detail || validationError(data) || "Ocurrió un error al procesar la solicitud.")
  return data
}

function url(base, filters = {}) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") return
    params.set(key, String(value))
  })
  const query = params.toString()
  return query ? `${base}/?${query}` : `${base}/`
}

function json(base, method, data) {
  return request(base, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(data || {}) })
}

export function listRentalResource(resource, filters = {}) { return request(url(endpoints[resource], filters)) }
export function getRentalResource(resource, id) { return request(`${endpoints[resource]}/${id}/`) }
export function createRentalResource(resource, data) {
  if (data instanceof FormData) return request(`${endpoints[resource]}/`, { method: "POST", body: data })
  return json(`${endpoints[resource]}/`, "POST", data)
}
export function updateRentalResource(resource, id, data) {
  if (data instanceof FormData) return request(`${endpoints[resource]}/${id}/`, { method: "PATCH", body: data })
  return json(`${endpoints[resource]}/${id}/`, "PATCH", data)
}
export function rentalAction(resource, id, action, data = {}) { return json(`${endpoints[resource]}/${id}/${action}/`, "POST", data) }
export function archiveRentalResource(resource, id, reason = "") { return rentalAction(resource, id, "archive", { reason }) }
export function restoreRentalResource(resource, id) { return rentalAction(resource, id, "restore") }

export const getWarehouses = (f={}) => listRentalResource("warehouses", f)
export const getRentalEquipment = (f={}) => listRentalResource("equipment", f)
export const getRentalContracts = (f={}) => listRentalResource("contracts", f)
export const getRentalAssignments = (f={}) => listRentalResource("assignments", f)
export const getRentalPreparations = (f={}) => listRentalResource("preparations", f)
export const getRentalInstallations = (f={}) => listRentalResource("installations", f)
export const getRentalRemovals = (f={}) => listRentalResource("removals", f)
export const getRentalReplacements = (f={}) => listRentalResource("replacements", f)
export const getRentalMovements = (f={}) => listRentalResource("movements", f)
export const getRentalDocuments = (f={}) => listRentalResource("documents", f)
