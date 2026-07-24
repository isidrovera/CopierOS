const API_URL = "http://127.0.0.1:8000/api/users"

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

export async function getUsers({
  search = "",
  includeArchived = false,
  isActive = "",
} = {}) {
  const params = new URLSearchParams()

  if (search.trim()) {
    params.set("search", search.trim())
  }

  if (includeArchived) {
    params.set("include_archived", "true")
  }

  if (
    isActive === true ||
    isActive === false
  ) {
    params.set(
      "is_active",
      String(isActive)
    )
  }

  const query = params.toString()

  const url = query
    ? `${API_URL}/?${query}`
    : `${API_URL}/`

  return request(url)
}

export async function getUser(userId) {
  return request(
    `${API_URL}/${userId}/`
  )
}

export async function createUser(userData) {
  return request(`${API_URL}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userData),
  })
}

export async function updateUser(
  userId,
  userData
) {
  return request(
    `${API_URL}/${userId}/`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    }
  )
}

export async function archiveUser(
  userId,
  reason = ""
) {
  return request(
    `${API_URL}/${userId}/archive/`,
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

export async function restoreUser(userId) {
  return request(
    `${API_URL}/${userId}/restore/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  )
}

export async function resetUserPassword(
  userId,
  newPassword,
  newPasswordConfirmation,
  forceChange = true
) {
  return request(
    `${API_URL}/${userId}/reset-password/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        new_password: newPassword,
        new_password_confirmation:
          newPasswordConfirmation,
        force_change: forceChange,
      }),
    }
  )
}