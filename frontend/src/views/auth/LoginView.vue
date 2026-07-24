<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"

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
            Copier Company
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
      COPIER COMPANY · Sistema de gestión
    </p>
  </main>
</template>

<style scoped>
button,
input {
  font: inherit;
}

button {
  border: 0;
}

/* ============================================================= */
/* PALETA BASADA EN EL LOGO                                      */
/* ============================================================= */

.auth-page {
  --brand-blue: #1f35c4;
  --brand-blue-deep: #162caa;
  --brand-blue-soft: #4e63d8;
  --brand-gray: #8693a4;
  --brand-gray-soft: #a5afbb;
  --brand-white-soft: rgba(255, 255, 255, 0.88);
  --brand-white-mid: rgba(255, 255, 255, 0.68);
  --brand-white-low: rgba(255, 255, 255, 0.45);
  --glass-bg: rgba(255, 255, 255, 0.09);
  --glass-line: rgba(255, 255, 255, 0.18);
  --input-line: rgba(255, 255, 255, 0.42);
  --card-shadow: rgba(7, 14, 42, 0.38);
}

/* ============================================================= */
/* FONDO                                                         */
/* ============================================================= */

.auth-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  box-sizing: border-box;
  padding: 32px 20px;
  background:
    radial-gradient(
      circle at 16% 18%,
      rgba(31, 53, 196, 0.24),
      transparent 28%
    ),
    radial-gradient(
      circle at 82% 76%,
      rgba(134, 147, 164, 0.26),
      transparent 34%
    ),
    radial-gradient(
      circle at 62% 24%,
      rgba(78, 99, 216, 0.18),
      transparent 24%
    ),
    linear-gradient(
      145deg,
      #0f1730,
      #152451 46%,
      #1d2541 100%
    );
  color: white;
}

.auth-page::before {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      rgba(255, 255, 255, 0.012) 1px,
      transparent 1px
    ),
    linear-gradient(
      90deg,
      rgba(255, 255, 255, 0.012) 1px,
      transparent 1px
    );
  background-size: 40px 40px;
  content: "";
  pointer-events: none;
}

.background-light {
  position: absolute;
  border-radius: 50%;
  filter: blur(28px);
  pointer-events: none;
}

.light-one {
  top: 8%;
  left: 12%;
  width: 300px;
  height: 300px;
  background: rgba(31, 53, 196, 0.15);
}

.light-two {
  right: 10%;
  bottom: 7%;
  width: 360px;
  height: 360px;
  background: rgba(134, 147, 164, 0.18);
}

.light-three {
  top: 33%;
  right: 28%;
  width: 180px;
  height: 180px;
  background: rgba(78, 99, 216, 0.16);
}

/* ============================================================= */
/* TARJETA                                                       */
/* ============================================================= */

.auth-card {
  position: relative;
  z-index: 2;
  width: min(430px, 100%);
  box-sizing: border-box;
  padding: 38px 36px 30px;
  border: 1px solid var(--glass-line);
  border-radius: 30px;
  background:
    linear-gradient(
      145deg,
      rgba(255, 255, 255, 0.13),
      rgba(255, 255, 255, 0.06)
    );
  box-shadow:
    0 32px 80px var(--card-shadow),
    inset 0 1px 0 rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(22px);
}

.auth-card::before {
  position: absolute;
  inset: 1px;
  border-radius: 29px;
  background:
    linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.06),
      transparent 46%
    );
  content: "";
  pointer-events: none;
}

.auth-content {
  position: relative;
  z-index: 1;
}

/* ============================================================= */
/* CABECERA                                                      */
/* ============================================================= */

.auth-header {
  margin-bottom: 28px;
  text-align: center;
}

.company-mark-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.company-mark {
  width: 122px;
  height: 122px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background:
    radial-gradient(
      circle at 30% 30%,
      rgba(255, 255, 255, 0.18),
      rgba(255, 255, 255, 0.05)
    );
  box-shadow:
    0 20px 40px rgba(11, 19, 52, 0.34),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.small-mark {
  width: 104px;
  height: 104px;
}

.company-mark svg {
  width: 108px;
  height: 108px;
}

.ring {
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.ring-main {
  stroke: rgba(255, 255, 255, 0.42);
  stroke-width: 4;
}

.ring-soft {
  stroke: rgba(31, 53, 196, 0.16);
  stroke-width: 2;
}

.node {
  fill: var(--brand-gray-soft);
}

.device-icon {
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.main-device {
  stroke: var(--brand-white-soft);
  stroke-width: 3.2;
}

.secondary-device {
  stroke: var(--brand-gray-soft);
  stroke-width: 2.5;
}

.status-dot {
  fill: var(--brand-blue-soft);
  stroke: none;
}

.system-name {
  display: block;
  margin-bottom: 8px;
  color: var(--brand-gray-soft);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.auth-header h1 {
  margin: 0;
  color: #ffffff;
  font-size: 28px;
  line-height: 1.16;
  letter-spacing: -0.02em;
}

.auth-header p {
  margin: 10px 0 0;
  color: var(--brand-white-mid);
  font-size: 13px;
  line-height: 1.55;
}

/* ============================================================= */
/* FORMULARIO                                                    */
/* ============================================================= */

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.glass-field {
  position: relative;
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--input-line);
  transition:
    border-color 0.2s ease,
    background 0.2s ease;
}

.glass-field:focus-within {
  border-color: rgba(78, 99, 216, 0.95);
  background:
    linear-gradient(
      90deg,
      rgba(31, 53, 196, 0.08),
      transparent
    );
}

.field-icon {
  position: absolute;
  left: 3px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--brand-gray-soft);
  pointer-events: none;
}

.field-icon svg,
.show-password-button svg,
.primary-button svg,
.back-button svg,
.alert-icon svg,
.security-indicator svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.glass-field input {
  width: 100%;
  min-height: 52px;
  box-sizing: border-box;
  padding: 0 44px 0 33px;
  border: 0;
  outline: 0;
  background: transparent;
  color: #ffffff;
  font-size: 14px;
}

.glass-field input::placeholder {
  color: rgba(255, 255, 255, 0.54);
}

.glass-field input:-webkit-autofill,
.glass-field input:-webkit-autofill:hover,
.glass-field input:-webkit-autofill:focus {
  transition:
    background-color 9999s ease-out 0s;
  -webkit-text-fill-color: #ffffff;
}

.show-password-button {
  position: absolute;
  right: 3px;
  width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: transparent;
  color: var(--brand-gray-soft);
  cursor: pointer;
}

.show-password-button:hover {
  background: rgba(255, 255, 255, 0.08);
  color: white;
}

.code-field input {
  padding-right: 20px;
}

.two-factor-input {
  text-align: center;
  font-size: 22px !important;
  font-weight: 800;
  letter-spacing: 0.26em;
}

.field-help {
  display: block;
  margin-top: -8px;
  color: var(--brand-white-low);
  font-size: 11px;
  line-height: 1.5;
  text-align: center;
}

/* ============================================================= */
/* OPCIONES                                                      */
/* ============================================================= */

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.remember-option {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--brand-white-mid);
  font-size: 11px;
  cursor: pointer;
}

.remember-option input {
  width: 15px;
  height: 15px;
  margin: 0;
  accent-color: var(--brand-blue);
}

.link-button {
  padding: 0;
  background: transparent;
  color: var(--brand-gray-soft);
  font-size: 11px;
  cursor: pointer;
}

.link-button:hover {
  color: #ffffff;
  text-decoration: underline;
}

/* ============================================================= */
/* BOTÓN PRINCIPAL                                               */
/* ============================================================= */

.primary-button {
  min-height: 52px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 0 18px;
  border-radius: 12px;
  background:
    linear-gradient(
      90deg,
      var(--brand-blue-deep),
      var(--brand-blue) 52%,
      var(--brand-gray)
    );
  color: white;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  box-shadow:
    0 16px 32px rgba(17, 34, 107, 0.32);
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    opacity 0.2s ease;
}

.primary-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow:
    0 20px 38px rgba(17, 34, 107, 0.38);
}

.primary-button:active:not(:disabled) {
  transform: translateY(0);
}

.primary-button:disabled {
  opacity: 0.62;
  cursor: wait;
}

.button-spinner {
  width: 17px;
  height: 17px;
  box-sizing: border-box;
  border: 2px solid rgba(255, 255, 255, 0.34);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ============================================================= */
/* ALERTAS                                                       */
/* ============================================================= */

.alert {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  margin: 0;
  padding: 11px 12px;
  border-radius: 11px;
  font-size: 12px;
  line-height: 1.5;
}

.alert-icon {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  margin-top: 1px;
}

.error-alert {
  border: 1px solid rgba(255, 136, 136, 0.22);
  background: rgba(153, 48, 48, 0.18);
  color: #ffdede;
}

.success-alert {
  border: 1px solid rgba(120, 181, 146, 0.22);
  background: rgba(73, 116, 96, 0.18);
  color: #e0fff0;
}

/* ============================================================= */
/* VOLVER                                                        */
/* ============================================================= */

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 22px;
  padding: 7px 9px;
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--brand-gray-soft);
  font-size: 12px;
  cursor: pointer;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.11);
  color: white;
}

.back-button:disabled {
  opacity: 0.55;
  cursor: wait;
}

/* ============================================================= */
/* PIE                                                           */
/* ============================================================= */

.auth-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  margin-top: 25px;
  color: var(--brand-white-low);
  font-size: 10px;
}

.security-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--brand-gray-soft);
}

.security-indicator svg {
  width: 14px;
  height: 14px;
}

.page-footer {
  position: relative;
  z-index: 2;
  margin: 18px 0 0;
  color: rgba(255, 255, 255, 0.34);
  font-size: 10px;
  letter-spacing: 0.04em;
}

/* ============================================================= */
/* RESPONSIVE                                                    */
/* ============================================================= */

@media (max-width: 560px) {
  .auth-page {
    padding: 18px 14px;
  }

  .auth-card {
    padding: 32px 24px 27px;
    border-radius: 25px;
  }

  .auth-card::before {
    border-radius: 24px;
  }

  .company-mark {
    width: 108px;
    height: 108px;
  }

  .small-mark {
    width: 96px;
    height: 96px;
  }

  .company-mark svg {
    width: 96px;
    height: 96px;
  }

  .auth-header h1 {
    font-size: 24px;
  }

  .form-options {
    align-items: flex-start;
    flex-direction: column;
    gap: 12px;
  }

  .two-factor-input {
    font-size: 19px !important;
    letter-spacing: 0.18em;
  }
}

@media (max-width: 380px) {
  .auth-card {
    padding-right: 20px;
    padding-left: 20px;
  }

  .auth-header h1 {
    font-size: 22px;
  }
}
</style>