const API_URL =
  "http://127.0.0.1:8000/api/monitoring"

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
      return String(
        value[0]
      )
    }

    if (
      value &&
      typeof value === "object"
    ) {
      const nestedError =
        getValidationError(
          value
        )

      if (nestedError) {
        return nestedError
      }
    }

    if (
      typeof value === "string"
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

  if (
    response.status === 401
  ) {
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
      "No se pudo completar la solicitud."
    )
  }

  return data
}


function buildUrl(
  path,
  filters = {}
) {
  const params =
    new URLSearchParams()

  Object.entries(
    filters
  ).forEach(
    ([
      key,
      value,
    ]) => {
      if (
        value !== undefined &&
        value !== null &&
        value !== ""
      ) {
        params.set(
          key,
          String(value)
        )
      }
    }
  )

  const query =
    params.toString()

  return query
    ? `${API_URL}/${path}?${query}`
    : `${API_URL}/${path}`
}


function normalizeList(data) {
  if (
    Array.isArray(data)
  ) {
    return data
  }

  if (
    Array.isArray(
      data?.results
    )
  ) {
    return data.results
  }

  return []
}


function jsonRequestOptions(
  method,
  payload = null
) {
  const options = {
    method,
    headers: {
      "Content-Type":
        "application/json",
    },
  }

  if (payload !== null) {
    options.body =
      JSON.stringify(payload)
  }

  return options
}


export {
  normalizeList,
}


export function getInstallationTokens(
  filters = {}
) {
  return request(
    buildUrl(
      "installation-tokens/",
      filters
    )
  )
}


export function createInstallationToken(
  payload
) {
  return request(
    `${API_URL}/installation-tokens/`,
    jsonRequestOptions(
      "POST",
      payload
    )
  )
}


export function revokeInstallationToken(
  id,
  reason = ""
) {
  return request(
    (
      `${API_URL}/installation-tokens/` +
      `${id}/revoke/`
    ),
    jsonRequestOptions(
      "POST",
      {
        reason,
      }
    )
  )
}


export function archiveInstallationToken(
  id,
  reason = ""
) {
  return request(
    (
      `${API_URL}/installation-tokens/` +
      `${id}/archive/`
    ),
    jsonRequestOptions(
      "POST",
      {
        reason,
      }
    )
  )
}


export function restoreInstallationToken(
  id
) {
  return request(
    (
      `${API_URL}/installation-tokens/` +
      `${id}/restore/`
    ),
    jsonRequestOptions(
      "POST",
      {}
    )
  )
}


export function getAgents(
  filters = {}
) {
  return request(
    buildUrl(
      "agents/",
      filters
    )
  )
}


export function getAgent(id) {
  return request(
    `${API_URL}/agents/${id}/`
  )
}


export function updateAgent(
  id,
  payload
) {
  return request(
    `${API_URL}/agents/${id}/`,
    jsonRequestOptions(
      "PATCH",
      payload
    )
  )
}


export function archiveAgent(
  id,
  reason = ""
) {
  return request(
    `${API_URL}/agents/${id}/archive/`,
    jsonRequestOptions(
      "POST",
      {
        reason,
      }
    )
  )
}


export function restoreAgent(
  id
) {
  return request(
    `${API_URL}/agents/${id}/restore/`,
    jsonRequestOptions(
      "POST",
      {}
    )
  )
}


export function getNetworks(
  filters = {}
) {
  return request(
    buildUrl(
      "networks/",
      filters
    )
  )
}


export function getNetwork(id) {
  return request(
    `${API_URL}/networks/${id}/`
  )
}


export function createNetwork(
  payload
) {
  return request(
    `${API_URL}/networks/`,
    jsonRequestOptions(
      "POST",
      payload
    )
  )
}


export function updateNetwork(
  id,
  payload
) {
  return request(
    `${API_URL}/networks/${id}/`,
    jsonRequestOptions(
      "PATCH",
      payload
    )
  )
}


export function archiveNetwork(
  id,
  reason = ""
) {
  return request(
    `${API_URL}/networks/${id}/archive/`,
    jsonRequestOptions(
      "POST",
      {
        reason,
      }
    )
  )
}


export function restoreNetwork(
  id
) {
  return request(
    `${API_URL}/networks/${id}/restore/`,
    jsonRequestOptions(
      "POST",
      {}
    )
  )
}


export function getCredentials(
  filters = {}
) {
  return request(
    buildUrl(
      "snmp-credentials/",
      filters
    )
  )
}


export function getCredential(id) {
  return request(
    (
      `${API_URL}/snmp-credentials/` +
      `${id}/`
    )
  )
}


export function createCredential(
  payload
) {
  return request(
    `${API_URL}/snmp-credentials/`,
    jsonRequestOptions(
      "POST",
      payload
    )
  )
}


export function updateCredential(
  id,
  payload
) {
  return request(
    (
      `${API_URL}/snmp-credentials/` +
      `${id}/`
    ),
    jsonRequestOptions(
      "PATCH",
      payload
    )
  )
}


export function archiveCredential(
  id,
  reason = ""
) {
  return request(
    (
      `${API_URL}/snmp-credentials/` +
      `${id}/archive/`
    ),
    jsonRequestOptions(
      "POST",
      {
        reason,
      }
    )
  )
}


export function restoreCredential(
  id
) {
  return request(
    (
      `${API_URL}/snmp-credentials/` +
      `${id}/restore/`
    ),
    jsonRequestOptions(
      "POST",
      {}
    )
  )
}


export function getDevices(
  filters = {}
) {
  return request(
    buildUrl(
      "devices/",
      filters
    )
  )
}


export function getDevice(id) {
  return request(
    `${API_URL}/devices/${id}/`
  )
}


export function createDevice(
  payload
) {
  return request(
    `${API_URL}/devices/`,
    jsonRequestOptions(
      "POST",
      payload
    )
  )
}


export function updateDevice(
  id,
  payload
) {
  return request(
    `${API_URL}/devices/${id}/`,
    jsonRequestOptions(
      "PATCH",
      payload
    )
  )
}


export function deleteDevice(
  id
) {
  return request(
    `${API_URL}/devices/${id}/`,
    {
      method: "DELETE",
    }
  )
}


export function archiveDevice(
  id,
  reason = ""
) {
  return request(
    `${API_URL}/devices/${id}/archive/`,
    jsonRequestOptions(
      "POST",
      {
        reason,
      }
    )
  )
}


export function restoreDevice(
  id
) {
  return request(
    `${API_URL}/devices/${id}/restore/`,
    jsonRequestOptions(
      "POST",
      {}
    )
  )
}


export function getSnapshots(
  filters = {}
) {
  return request(
    buildUrl(
      "snapshots/",
      filters
    )
  )
}


export function getSnapshot(id) {
  return request(
    `${API_URL}/snapshots/${id}/`
  )
}


export function createManualSnapshot(
  payload
) {
  return request(
    `${API_URL}/snapshots/manual/`,
    jsonRequestOptions(
      "POST",
      payload
    )
  )
}


export function updateSnapshot(
  id,
  payload
) {
  return request(
    `${API_URL}/snapshots/${id}/`,
    jsonRequestOptions(
      "PATCH",
      payload
    )
  )
}


export function getCounterReadings(
  filters = {}
) {
  return request(
    buildUrl(
      "counter-readings/",
      filters
    )
  )
}


export function getCounterReading(
  id
) {
  return request(
    (
      `${API_URL}/counter-readings/` +
      `${id}/`
    )
  )
}


export function updateCounterReading(
  id,
  payload
) {
  return request(
    (
      `${API_URL}/counter-readings/` +
      `${id}/`
    ),
    jsonRequestOptions(
      "PATCH",
      payload
    )
  )
}


export function getConsumableReadings(
  filters = {}
) {
  return request(
    buildUrl(
      "consumable-readings/",
      filters
    )
  )
}


export function getConsumableReading(
  id
) {
  return request(
    (
      `${API_URL}/consumable-readings/` +
      `${id}/`
    )
  )
}


export function updateConsumableReading(
  id,
  payload
) {
  return request(
    (
      `${API_URL}/consumable-readings/` +
      `${id}/`
    ),
    jsonRequestOptions(
      "PATCH",
      payload
    )
  )
}


export function getComponentReadings(
  filters = {}
) {
  return request(
    buildUrl(
      "component-readings/",
      filters
    )
  )
}


export function getComponentReading(
  id
) {
  return request(
    (
      `${API_URL}/component-readings/` +
      `${id}/`
    )
  )
}


export function updateComponentReading(
  id,
  payload
) {
  return request(
    (
      `${API_URL}/component-readings/` +
      `${id}/`
    ),
    jsonRequestOptions(
      "PATCH",
      payload
    )
  )
}


export function getTrayReadings(
  filters = {}
) {
  return request(
    buildUrl(
      "tray-readings/",
      filters
    )
  )
}


export function getTrayReading(
  id
) {
  return request(
    (
      `${API_URL}/tray-readings/` +
      `${id}/`
    )
  )
}


export function updateTrayReading(
  id,
  payload
) {
  return request(
    (
      `${API_URL}/tray-readings/` +
      `${id}/`
    ),
    jsonRequestOptions(
      "PATCH",
      payload
    )
  )
}


export function getAccessoryReadings(
  filters = {}
) {
  return request(
    buildUrl(
      "accessory-readings/",
      filters
    )
  )
}


export function getAccessoryReading(
  id
) {
  return request(
    (
      `${API_URL}/accessory-readings/` +
      `${id}/`
    )
  )
}


export function updateAccessoryReading(
  id,
  payload
) {
  return request(
    (
      `${API_URL}/accessory-readings/` +
      `${id}/`
    ),
    jsonRequestOptions(
      "PATCH",
      payload
    )
  )
}


export function getAlerts(
  filters = {}
) {
  return request(
    buildUrl(
      "device-alerts/",
      filters
    )
  )
}


export function getAlert(id) {
  return request(
    `${API_URL}/device-alerts/${id}/`
  )
}


export function updateAlert(
  id,
  payload
) {
  return request(
    `${API_URL}/device-alerts/${id}/`,
    jsonRequestOptions(
      "PATCH",
      payload
    )
  )
}


export function acknowledgeAlert(
  id,
  notes = ""
) {
  return request(
    (
      `${API_URL}/device-alerts/` +
      `${id}/acknowledge/`
    ),
    jsonRequestOptions(
      "POST",
      {
        notes,
      }
    )
  )
}


export function resolveAlert(
  id,
  notes = ""
) {
  return request(
    (
      `${API_URL}/device-alerts/` +
      `${id}/resolve/`
    ),
    jsonRequestOptions(
      "POST",
      {
        notes,
      }
    )
  )
}


export function getProfiles(
  filters = {}
) {
  return request(
    buildUrl(
      "snmp-profiles/",
      filters
    )
  )
}


export function getProfile(id) {
  return request(
    `${API_URL}/snmp-profiles/${id}/`
  )
}


export function createProfile(
  payload
) {
  return request(
    `${API_URL}/snmp-profiles/`,
    jsonRequestOptions(
      "POST",
      payload
    )
  )
}


export function updateProfile(
  id,
  payload
) {
  return request(
    `${API_URL}/snmp-profiles/${id}/`,
    jsonRequestOptions(
      "PATCH",
      payload
    )
  )
}


export function archiveProfile(
  id,
  reason = ""
) {
  return request(
    `${API_URL}/snmp-profiles/${id}/archive/`,
    jsonRequestOptions(
      "POST",
      {
        reason,
      }
    )
  )
}


export function restoreProfile(
  id
) {
  return request(
    `${API_URL}/snmp-profiles/${id}/restore/`,
    jsonRequestOptions(
      "POST",
      {}
    )
  )
}


export function getProfileMetrics(
  filters = {}
) {
  return request(
    buildUrl(
      "snmp-profile-metrics/",
      filters
    )
  )
}


export function createProfileMetric(
  payload
) {
  return request(
    `${API_URL}/snmp-profile-metrics/`,
    jsonRequestOptions(
      "POST",
      payload
    )
  )
}


export function updateProfileMetric(
  id,
  payload
) {
  return request(
    (
      `${API_URL}/snmp-profile-metrics/` +
      `${id}/`
    ),
    jsonRequestOptions(
      "PATCH",
      payload
    )
  )
}


export function getJobReadings(
  filters = {}
) {
  return request(
    buildUrl(
      "job-readings/",
      filters
    )
  )
}


export function getRawOidReadings(
  filters = {}
) {
  return request(
    buildUrl(
      "raw-oid-readings/",
      filters
    )
  )
}


export async function getDeviceDetailData(
  deviceId
) {
  const [
    deviceData,
    snapshotData,
    counterData,
    consumableData,
    componentData,
    trayData,
    accessoryData,
    alertData,
  ] = await Promise.all([
    getDevice(
      deviceId
    ),
    getSnapshots({
      device: deviceId,
    }),
    getCounterReadings({
      device: deviceId,
    }),
    getConsumableReadings({
      device: deviceId,
      latest: true,
    }),
    getComponentReadings({
      device: deviceId,
      latest: true,
    }),
    getTrayReadings({
      device: deviceId,
      latest: true,
    }),
    getAccessoryReadings({
      device: deviceId,
      latest: true,
    }),
    getAlerts({
      device: deviceId,
    }),
  ])

  return {
    device: deviceData,

    snapshots: normalizeList(
      snapshotData
    ),

    counters: normalizeList(
      counterData
    ),

    consumables: normalizeList(
      consumableData
    ),

    components: normalizeList(
      componentData
    ),

    trays: normalizeList(
      trayData
    ),

    accessories: normalizeList(
      accessoryData
    ),

    alerts: normalizeList(
      alertData
    ),
  }
}


export async function getDashboardData() {
  const [
    agentsData,
    devicesData,
    alertsData,
    snapshotsData,
    networksData,
  ] = await Promise.all([
    getAgents(),
    getDevices(),
    getAlerts(),
    getSnapshots(),
    getNetworks(),
  ])

  const agents =
    normalizeList(
      agentsData
    )

  const devices =
    normalizeList(
      devicesData
    )

  const alerts =
    normalizeList(
      alertsData
    )

  const snapshots =
    normalizeList(
      snapshotsData
    )

  const networks =
    normalizeList(
      networksData
    )

  return {
    agents,
    devices,
    alerts,
    snapshots,
    networks,
  }
}