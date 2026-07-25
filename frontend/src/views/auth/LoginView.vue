<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"

import "./LoginView.css"

import {
  loginUser,
  saveSession,
  verifyTwoFactorLogin,
} from "../../services/auth.service"

const router = useRouter()

const email = ref("")
const password = ref("")
const rememberMe = ref(true)
const showPassword = ref(false)

const loading = ref(false)
const error = ref("")

const requiresTwoFactor = ref(false)
const challengeToken = ref("")
const twoFactorCode = ref("")
const twoFactorMethod = ref("totp")

const showRecovery = ref(false)
const recoveryEmail = ref("")
const recoveryMessage = ref("")

async function login() {
  error.value = ""

  if (!email.value.trim() || !password.value) {
    error.value =
      "Ingresa tu correo electrónico y contraseña."
    return
  }

  loading.value = true

  try {
    const data = await loginUser(
      email.value.trim(),
      password.value
    )

    if (data.requires_two_factor) {
      requiresTwoFactor.value = true
      challengeToken.value =
        data.challenge_token || ""
      twoFactorMethod.value =
        data.two_factor_method || "totp"
      twoFactorCode.value = ""
      return
    }

    await completeLogin(data)
  } catch (err) {
    error.value =
      err.message ||
      "No se pudo conectar con el servidor."
  } finally {
    loading.value = false
  }
}

async function verifyTwoFactor() {
  error.value = ""

  const code = twoFactorCode.value
    .replace(/\s/g, "")
    .trim()

  if (!code) {
    error.value =
      "Ingresa el código de autenticación."
    return
  }

  if (!challengeToken.value) {
    error.value =
      "La solicitud de autenticación no es válida. Inicia sesión nuevamente."
    return
  }

  loading.value = true

  try {
    const data = await verifyTwoFactorLogin(
      challengeToken.value,
      code
    )

    await completeLogin(data)
  } catch (err) {
    error.value =
      err.message ||
      "No se pudo verificar el código."
  } finally {
    loading.value = false
  }
}

async function completeLogin(data) {
  if (!data.token || !data.user) {
    throw new Error(
      "El backend no devolvió una sesión válida."
    )
  }

  saveSession(
    data.token,
    data.user,
    rememberMe.value
  )

  await router.push({
    name: "dashboard",
  })
}

function returnToLogin() {
  requiresTwoFactor.value = false
  challengeToken.value = ""
  twoFactorCode.value = ""
  error.value = ""
}

function handleTwoFactorInput(event) {
  twoFactorCode.value = event.target.value
    .replace(/[^a-zA-Z0-9-]/g, "")
    .toUpperCase()
    .slice(0, 20)
}

function openRecovery() {
  recoveryEmail.value = email.value
  recoveryMessage.value = ""
  error.value = ""
  showRecovery.value = true
}

function closeRecovery() {
  showRecovery.value = false
  recoveryMessage.value = ""
  error.value = ""
}

function recoverPassword() {
  error.value = ""
  recoveryMessage.value = ""

  if (!recoveryEmail.value.trim()) {
    error.value =
      "Ingresa tu correo electrónico."
    return
  }

  recoveryMessage.value =
    "La recuperación todavía debe conectarse al backend."
}
</script>

<template>
  <main class="auth-page">
    <div class="background-light light-one"></div>
    <div class="background-light light-two"></div>
    <div class="background-light light-three"></div>

    <div class="equipment-background" aria-hidden="true">
      <div class="equipment-orbit orbit-one"></div>
      <div class="equipment-orbit orbit-two"></div>

      <div class="equipment-machine machine-left">
        <div class="machine-glow"></div>
        <svg viewBox="0 0 240 330">
          <g class="machine-shell">
            <path d="M58 26h124a16 16 0 0 1 16 16v48H42V42a16 16 0 0 1 16-16Z" />
            <path d="M36 88h168a20 20 0 0 1 20 20v62a20 20 0 0 1-20 20H36a20 20 0 0 1-20-20v-62a20 20 0 0 1 20-20Z" />
            <path d="M42 184h156v118a16 16 0 0 1-16 16H58a16 16 0 0 1-16-16Z" />
            <path d="M62 205h116v42H62z" />
            <path d="M62 258h116v38H62z" />
          </g>
          <g class="machine-details">
            <rect x="60" y="104" width="72" height="38" rx="8" />
            <circle cx="179" cy="121" r="7" />
            <path d="M80 51h80" />
            <path d="M74 160h92" />
          </g>
          <circle class="machine-status" cx="196" cy="121" r="5" />
        </svg>
      </div>

      <div class="equipment-machine machine-right">
        <div class="machine-glow"></div>
        <svg viewBox="0 0 240 330">
          <g class="machine-shell">
            <path d="M54 34h132a15 15 0 0 1 15 15v44H39V49a15 15 0 0 1 15-15Z" />
            <path d="M30 92h180a18 18 0 0 1 18 18v70a18 18 0 0 1-18 18H30a18 18 0 0 1-18-18v-70a18 18 0 0 1 18-18Z" />
            <path d="M48 193h144v111a14 14 0 0 1-14 14H62a14 14 0 0 1-14-14Z" />
            <path d="M66 212h108v36H66z" />
            <path d="M66 258h108v38H66z" />
          </g>
          <g class="machine-details">
            <rect x="58" y="111" width="80" height="40" rx="8" />
            <path d="M75 57h90" />
            <path d="M72 170h96" />
            <circle cx="184" cy="130" r="8" />
          </g>
          <circle class="machine-status" cx="204" cy="130" r="5" />
        </svg>
      </div>

      <div class="equipment-machine machine-back-left">
        <svg viewBox="0 0 220 300">
          <g class="machine-shell">
            <path d="M50 30h120a14 14 0 0 1 14 14v42H36V44a14 14 0 0 1 14-14Z" />
            <path d="M28 84h164a18 18 0 0 1 18 18v58a18 18 0 0 1-18 18H28a18 18 0 0 1-18-18v-58a18 18 0 0 1 18-18Z" />
            <path d="M42 174h136v104H42z" />
          </g>
          <g class="machine-details">
            <rect x="50" y="102" width="68" height="34" rx="7" />
            <path d="M62 54h96" />
          </g>
        </svg>
      </div>

      <div class="equipment-machine machine-back-right">
        <svg viewBox="0 0 220 300">
          <g class="machine-shell">
            <path d="M50 30h120a14 14 0 0 1 14 14v42H36V44a14 14 0 0 1 14-14Z" />
            <path d="M28 84h164a18 18 0 0 1 18 18v58a18 18 0 0 1-18 18H28a18 18 0 0 1-18-18v-58a18 18 0 0 1 18-18Z" />
            <path d="M42 174h136v104H42z" />
          </g>
          <g class="machine-details">
            <rect x="50" y="102" width="68" height="34" rx="7" />
            <path d="M62 54h96" />
          </g>
        </svg>
      </div>

      <div class="floating-paper paper-one"></div>
      <div class="floating-paper paper-two"></div>
      <div class="floating-paper paper-three"></div>
    </div>


    <section class="auth-card">
      <!-- ======================================================= -->
      <!-- LOGIN                                                   -->
      <!-- ======================================================= -->
      <div
        v-if="
          !showRecovery &&
          !requiresTwoFactor
        "
        class="auth-content"
      >
        <header class="auth-header">
          <div class="company-mark-wrap">
            <div class="company-mark">
              <!-- Icono central: fotocopiadora + aro con equipos -->
              <svg
                viewBox="0 0 160 160"
                aria-hidden="true"
              >
                <!-- aro exterior -->
                <circle
                  cx="80"
                  cy="80"
                  r="58"
                  class="ring ring-main"
                />

                <circle
                  cx="80"
                  cy="80"
                  r="72"
                  class="ring ring-soft"
                />

                <!-- nodos -->
                <circle
                  cx="80"
                  cy="18"
                  r="4"
                  class="node"
                />
                <circle
                  cx="142"
                  cy="80"
                  r="4"
                  class="node"
                />
                <circle
                  cx="80"
                  cy="142"
                  r="4"
                  class="node"
                />
                <circle
                  cx="18"
                  cy="80"
                  r="4"
                  class="node"
                />

                <!-- icono superior: impresora -->
                <g
                  class="device-icon secondary-device"
                  transform="translate(66 22)"
                >
                  <rect
                    x="2"
                    y="8"
                    width="24"
                    height="14"
                    rx="3"
                  />
                  <path
                    d="M6 8V2h16v6"
                  />
                  <path
                    d="M7 18h14"
                  />
                </g>

                <!-- icono derecho: plotter -->
                <g
                  class="device-icon secondary-device"
                  transform="translate(120 66)"
                >
                  <rect
                    x="2"
                    y="4"
                    width="18"
                    height="12"
                    rx="2"
                  />
                  <path
                    d="M4 16v8"
                  />
                  <path
                    d="M18 16v8"
                  />
                  <path
                    d="M1 24h20"
                  />
                </g>

                <!-- icono inferior: duplicadora / hojas -->
                <g
                  class="device-icon secondary-device"
                  transform="translate(65 118)"
                >
                  <rect
                    x="7"
                    y="2"
                    width="16"
                    height="20"
                    rx="2"
                  />
                  <rect
                    x="1"
                    y="6"
                    width="16"
                    height="20"
                    rx="2"
                  />
                </g>

                <!-- icono izquierdo: fotocopiadora -->
                <g
                  class="device-icon secondary-device"
                  transform="translate(18 66)"
                >
                  <rect
                    x="2"
                    y="8"
                    width="22"
                    height="16"
                    rx="3"
                  />
                  <path
                    d="M5 8V3h16v5"
                  />
                  <path
                    d="M7 15h12"
                  />
                  <path
                    d="M8 24h10"
                  />
                </g>

                <!-- equipo central: fotocopiadora principal -->
                <g
                  class="device-icon main-device"
                  transform="translate(48 42)"
                >
                  <rect
                    x="10"
                    y="32"
                    width="44"
                    height="38"
                    rx="6"
                  />

                  <path
                    d="M16 32V20h32v12"
                  />

                  <rect
                    x="18"
                    y="8"
                    width="28"
                    height="14"
                    rx="3"
                  />

                  <path
                    d="M22 44h20"
                  />

                  <path
                    d="M22 51h14"
                  />

                  <path
                    d="M24 70h16"
                  />

                  <circle
                    cx="46"
                    cy="44"
                    r="2"
                    class="status-dot"
                  />
                </g>
              </svg>
            </div>
          </div>

          <span class="system-name">
            Copier OS
          </span>

          <h1>Acceso al sistema</h1>

          <p>
            Taller · Impresoras · Fotocopiadoras ·
            Duplicadoras · Plotters
          </p>
        </header>

        <form
          class="auth-form"
          @submit.prevent="login"
        >
          <div class="glass-field">
            <span class="field-icon">
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M4 6h16v12H4z"
                />
                <path
                  d="M4 7l8 6 8-6"
                />
              </svg>
            </span>

            <input
              id="email"
              v-model.trim="email"
              type="email"
              placeholder="Correo electrónico"
              autocomplete="email"
              required
            />
          </div>

          <div class="glass-field">
            <span class="field-icon">
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <rect
                  x="4"
                  y="10"
                  width="16"
                  height="11"
                  rx="2"
                />
                <path
                  d="M8 10V7a4 4 0 0 1 8 0v3"
                />
              </svg>
            </span>

            <input
              id="password"
              v-model="password"
              :type="
                showPassword
                  ? 'text'
                  : 'password'
              "
              placeholder="Contraseña"
              autocomplete="current-password"
              required
            />

            <button
              class="show-password-button"
              type="button"
              :aria-label="
                showPassword
                  ? 'Ocultar contraseña'
                  : 'Mostrar contraseña'
              "
              @click="
                showPassword = !showPassword
              "
            >
              <svg
                v-if="!showPassword"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"
                />
                <circle
                  cx="12"
                  cy="12"
                  r="3"
                />
              </svg>

              <svg
                v-else
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M17.94 17.94A10.94 10.94 0 0 1 12 19C5 19 1 12 1 12a21.8 21.8 0 0 1 5.06-5.94"
                />
                <path
                  d="M9.9 4.24A10.89 10.89 0 0 1 12 4c7 0 11 8 11 8a22.1 22.1 0 0 1-3.22 4.28"
                />
                <path
                  d="M14.12 14.12a3 3 0 1 1-4.24-4.24"
                />
                <path
                  d="M1 1l22 22"
                />
              </svg>
            </button>
          </div>

          <div class="form-options">
            <label class="remember-option">
              <input
                v-model="rememberMe"
                type="checkbox"
              />
              <span>Recordar sesión</span>
            </label>

            <button
              class="link-button"
              type="button"
              @click="openRecovery"
            >
              ¿Olvidaste tu contraseña?
            </button>
          </div>

          <p
            v-if="error"
            class="alert error-alert"
          >
            <span class="alert-icon">
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                />
                <path
                  d="M12 8v4"
                />
                <path
                  d="M12 16h.01"
                />
              </svg>
            </span>

            <span>
              {{ error }}
            </span>
          </p>

          <button
            class="primary-button"
            type="submit"
            :disabled="loading"
          >
            <span
              v-if="loading"
              class="button-spinner"
            ></span>

            <svg
              v-else
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="M5 12h14"
              />
              <path
                d="M12 5l7 7-7 7"
              />
            </svg>

            <span>
              {{
                loading
                  ? "Verificando..."
                  : "Ingresar"
              }}
            </span>
          </button>
        </form>

        <footer class="auth-footer">
          <span class="security-indicator">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="M12 3l7 4v5c0 5-3.5 7.5-7 9-3.5-1.5-7-4-7-9V7l7-4z"
              />
              <path
                d="M9 12l2 2 4-4"
              />
            </svg>
          </span>

          <span>
            Acceso seguro y protegido
          </span>
        </footer>
      </div>

      <!-- ======================================================= -->
      <!-- AUTENTICACIÓN EN DOS PASOS                              -->
      <!-- ======================================================= -->
      <div
        v-else-if="
          requiresTwoFactor &&
          !showRecovery
        "
        class="auth-content"
      >
        <button
          class="back-button"
          type="button"
          :disabled="loading"
          @click="returnToLogin"
        >
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              d="M19 12H5"
            />
            <path
              d="M12 19l-7-7 7-7"
            />
          </svg>

          <span>Volver</span>
        </button>

        <header class="auth-header">
          <div class="company-mark-wrap">
            <div class="company-mark small-mark">
              <svg
                viewBox="0 0 160 160"
                aria-hidden="true"
              >
                <circle
                  cx="80"
                  cy="80"
                  r="58"
                  class="ring ring-main"
                />
                <circle
                  cx="80"
                  cy="80"
                  r="72"
                  class="ring ring-soft"
                />

                <g
                  class="device-icon main-device"
                  transform="translate(48 42)"
                >
                  <rect
                    x="10"
                    y="32"
                    width="44"
                    height="38"
                    rx="6"
                  />
                  <path
                    d="M16 32V20h32v12"
                  />
                  <rect
                    x="18"
                    y="8"
                    width="28"
                    height="14"
                    rx="3"
                  />
                  <path
                    d="M22 44h20"
                  />
                  <path
                    d="M22 51h14"
                  />
                  <circle
                    cx="46"
                    cy="44"
                    r="2"
                    class="status-dot"
                  />
                </g>
              </svg>
            </div>
          </div>

          <span class="system-name">
            Verificación de seguridad
          </span>

          <h1>Autenticación en dos pasos</h1>

          <p v-if="twoFactorMethod === 'totp'">
            Ingresa el código generado por tu
            aplicación autenticadora
          </p>

          <p v-else>
            Ingresa tu código de autenticación
          </p>
        </header>

        <form
          class="auth-form"
          @submit.prevent="verifyTwoFactor"
        >
          <div class="glass-field code-field">
            <span class="field-icon">
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <rect
                  x="3"
                  y="5"
                  width="18"
                  height="16"
                  rx="2"
                />
                <path
                  d="M8 3v4"
                />
                <path
                  d="M16 3v4"
                />
                <path
                  d="M3 10h18"
                />
              </svg>
            </span>

            <input
              id="two-factor-code"
              :value="twoFactorCode"
              class="two-factor-input"
              type="text"
              inputmode="numeric"
              autocomplete="one-time-code"
              placeholder="000000"
              maxlength="20"
              autofocus
              required
              @input="handleTwoFactorInput"
            />
          </div>

          <small class="field-help">
            También puedes ingresar uno de tus códigos
            de recuperación.
          </small>

          <p
            v-if="error"
            class="alert error-alert"
          >
            <span class="alert-icon">
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                />
                <path
                  d="M12 8v4"
                />
                <path
                  d="M12 16h.01"
                />
              </svg>
            </span>

            <span>
              {{ error }}
            </span>
          </p>

          <button
            class="primary-button"
            type="submit"
            :disabled="loading"
          >
            <span
              v-if="loading"
              class="button-spinner"
            ></span>

            <svg
              v-else
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="M20 6L9 17l-5-5"
              />
            </svg>

            <span>
              {{
                loading
                  ? "Validando código..."
                  : "Verificar y continuar"
              }}
            </span>
          </button>
        </form>
      </div>

      <!-- ======================================================= -->
      <!-- RECUPERACIÓN                                            -->
      <!-- ======================================================= -->
      <div
        v-else
        class="auth-content"
      >
        <button
          class="back-button"
          type="button"
          @click="closeRecovery"
        >
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              d="M19 12H5"
            />
            <path
              d="M12 19l-7-7 7-7"
            />
          </svg>

          <span>Volver</span>
        </button>

        <header class="auth-header">
          <div class="company-mark-wrap">
            <div class="company-mark small-mark">
              <svg
                viewBox="0 0 160 160"
                aria-hidden="true"
              >
                <circle
                  cx="80"
                  cy="80"
                  r="58"
                  class="ring ring-main"
                />
                <circle
                  cx="80"
                  cy="80"
                  r="72"
                  class="ring ring-soft"
                />

                <g
                  class="device-icon main-device"
                  transform="translate(48 42)"
                >
                  <rect
                    x="10"
                    y="32"
                    width="44"
                    height="38"
                    rx="6"
                  />
                  <path
                    d="M16 32V20h32v12"
                  />
                  <rect
                    x="18"
                    y="8"
                    width="28"
                    height="14"
                    rx="3"
                  />
                  <path
                    d="M22 44h20"
                  />
                  <path
                    d="M22 51h14"
                  />
                  <circle
                    cx="46"
                    cy="44"
                    r="2"
                    class="status-dot"
                  />
                </g>
              </svg>
            </div>
          </div>

          <span class="system-name">
            Recuperación
          </span>

          <h1>Recuperar contraseña</h1>

          <p>
            Ingresa el correo asociado a tu cuenta
          </p>
        </header>

        <form
          class="auth-form"
          @submit.prevent="recoverPassword"
        >
          <div class="glass-field">
            <span class="field-icon">
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M4 6h16v12H4z"
                />
                <path
                  d="M4 7l8 6 8-6"
                />
              </svg>
            </span>

            <input
              id="recovery-email"
              v-model.trim="recoveryEmail"
              type="email"
              placeholder="Correo electrónico"
              autocomplete="email"
              required
            />
          </div>

          <p
            v-if="error"
            class="alert error-alert"
          >
            <span class="alert-icon">
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                />
                <path
                  d="M12 8v4"
                />
                <path
                  d="M12 16h.01"
                />
              </svg>
            </span>

            <span>
              {{ error }}
            </span>
          </p>

          <p
            v-if="recoveryMessage"
            class="alert success-alert"
          >
            <span class="alert-icon">
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                />
                <path
                  d="M8 12l2.5 2.5L16 9"
                />
              </svg>
            </span>

            <span>
              {{ recoveryMessage }}
            </span>
          </p>

          <button
            class="primary-button"
            type="submit"
          >
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="M22 2L11 13"
              />
              <path
                d="M22 2L15 22l-4-9-9-4 20-7z"
              />
            </svg>

            <span>Enviar enlace</span>
          </button>
        </form>
      </div>
    </section>

    <p class="page-footer">
      COPIER OS · Sistema de gestión técnica
    </p>
  </main>
</template>
