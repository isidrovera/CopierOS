const API_URL = "http://127.0.0.1:8000/api/users"

async function parseResponse(response) {
  let data = {}

  try {
    data = await response.json()
  } catch {
    data = {}
  }

  if (!response.ok) {
    throw new Error(
      data.detail ||
      getValidationError(data) ||
      "No se pudo completar la solicitud."
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

export async function loginUser(
  email,
  password
) {
  const response = await fetch(
    `${API_URL}/login/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        password,
      }),
    }
  )

  return parseResponse(response)
}

export async function verifyTwoFactorLogin(
  challengeToken,
  code
) {
  const response = await fetch(
    `${API_URL}/login/two-factor/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        challenge_token: challengeToken,
        code,
      }),
    }
  )

  return parseResponse(response)
}

export function saveSession(
  token,
  user,
  remember = true
) {
  clearSession()

  const storage = remember
    ? localStorage
    : sessionStorage

  storage.setItem("token", token)
  storage.setItem(
    "user",
    JSON.stringify(user)
  )
}

export function getStoredUser() {
  const savedUser =
    localStorage.getItem("user") ||
    sessionStorage.getItem("user")

  const token =
    localStorage.getItem("token") ||
    sessionStorage.getItem("token")

  if (!savedUser || !token) {
    return null
  }

  try {
    return JSON.parse(savedUser)
  } catch {
    clearSession()
    return null
  }
}

export function getToken() {
  return (
    localStorage.getItem("token") ||
    sessionStorage.getItem("token")
  )
}

export function isAuthenticated() {
  return Boolean(
    getToken() &&
    getStoredUser()
  )
}

export function clearSession() {
  localStorage.removeItem("token")
  localStorage.removeItem("user")

  sessionStorage.removeItem("token")
  sessionStorage.removeItem("user")
}