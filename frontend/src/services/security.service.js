const API_URL = "http://127.0.0.1:8000/api/users"

import {
  clearSession,
  getToken,
} from "./auth.service"

function getValidationError(data) {
  if (!data || typeof data !== "object") {
    return null
  }

  for (const value of Object.values(data)) {
    if (Array.isArray(value) && value.length) {
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
      "No se pudo completar la solicitud."
    )
  }

  return data
}

export async function getTwoFactorStatus() {
  return request(
    `${API_URL}/security/two-factor/`
  )
}

export async function beginTwoFactorSetup() {
  return request(
    `${API_URL}/security/two-factor/setup/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    }
  )
}

export async function confirmTwoFactorSetup(code) {
  return request(
    `${API_URL}/security/two-factor/confirm/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        code,
      }),
    }
  )
}

export async function disableTwoFactor(
  currentPassword,
  code
) {
  return request(
    `${API_URL}/security/two-factor/disable/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        current_password: currentPassword,
        code,
      }),
    }
  )
}

export async function regenerateRecoveryCodes(
  currentPassword,
  code
) {
  return request(
    `${API_URL}/security/two-factor/recovery-codes/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        current_password: currentPassword,
        code,
      }),
    }
  )
}