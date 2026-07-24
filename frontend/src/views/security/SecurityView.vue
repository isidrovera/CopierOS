<script setup>
import {
  computed,
  onMounted,
  ref,
} from "vue"

import {
  beginTwoFactorSetup,
  confirmTwoFactorSetup,
  disableTwoFactor,
  getTwoFactorStatus,
  regenerateRecoveryCodes,
} from "../../services/security.service"

const loading = ref(false)
const processing = ref(false)

const errorMessage = ref("")
const successMessage = ref("")

const securityStatus = ref({
  two_factor_enabled: false,
  two_factor_method: "none",
  require_two_factor_for_login: false,
  allow_password_login: true,
  allow_passkey_login: true,
  totp_confirmed_at: null,
  recovery_codes_available: 0,
  passkeys_registered: 0,
})

const setupData = ref(null)
const confirmationCode = ref("")
const recoveryCodes = ref([])

const showDisableForm = ref(false)
const disablePassword = ref("")
const disableCode = ref("")

const showRegenerateForm = ref(false)
const regeneratePassword = ref("")
const regenerateCode = ref("")

const twoFactorEnabled = computed(() => {
  return Boolean(
    securityStatus.value.two_factor_enabled
  )
})

const hasSetupPending = computed(() => {
  return Boolean(
    setupData.value?.qr_code &&
    !twoFactorEnabled.value
  )
})

async function loadSecurityStatus() {
  loading.value = true
  errorMessage.value = ""

  try {
    const data = await getTwoFactorStatus()

    securityStatus.value = {
      ...securityStatus.value,
      ...data,
    }
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo cargar la configuración de seguridad."
  } finally {
    loading.value = false
  }
}

async function startSetup() {
  processing.value = true
  errorMessage.value = ""
  successMessage.value = ""
  recoveryCodes.value = []
  confirmationCode.value = ""

  try {
    setupData.value =
      await beginTwoFactorSetup()
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo iniciar la configuración."
  } finally {
    processing.value = false
  }
}

async function confirmSetup() {
  errorMessage.value = ""
  successMessage.value = ""

  const code = confirmationCode.value
    .replace(/\s/g, "")
    .trim()

  if (!/^\d{6}$/.test(code)) {
    errorMessage.value =
      "Ingresa un código válido de 6 números."
    return
  }

  processing.value = true

  try {
    const data =
      await confirmTwoFactorSetup(code)

    recoveryCodes.value =
      data.recovery_codes || []

    setupData.value = null
    confirmationCode.value = ""

    successMessage.value =
      "La autenticación en dos pasos fue activada correctamente."

    await loadSecurityStatus()
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo confirmar el código."
  } finally {
    processing.value = false
  }
}

function cancelSetup() {
  setupData.value = null
  confirmationCode.value = ""
  errorMessage.value = ""
}

async function submitDisable() {
  errorMessage.value = ""
  successMessage.value = ""

  if (!disablePassword.value) {
    errorMessage.value =
      "Ingresa tu contraseña actual."
    return
  }

  if (!disableCode.value.trim()) {
    errorMessage.value =
      "Ingresa el código del autenticador o un código de recuperación."
    return
  }

  processing.value = true

  try {
    await disableTwoFactor(
      disablePassword.value,
      disableCode.value.trim()
    )

    showDisableForm.value = false
    disablePassword.value = ""
    disableCode.value = ""
    recoveryCodes.value = []

    successMessage.value =
      "La autenticación en dos pasos fue desactivada."

    await loadSecurityStatus()
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo desactivar la autenticación en dos pasos."
  } finally {
    processing.value = false
  }
}

async function submitRegenerateCodes() {
  errorMessage.value = ""
  successMessage.value = ""

  if (!regeneratePassword.value) {
    errorMessage.value =
      "Ingresa tu contraseña actual."
    return
  }

  if (!regenerateCode.value.trim()) {
    errorMessage.value =
      "Ingresa el código del autenticador."
    return
  }

  processing.value = true

  try {
    const data =
      await regenerateRecoveryCodes(
        regeneratePassword.value,
        regenerateCode.value.trim()
      )

    recoveryCodes.value =
      data.recovery_codes || []

    showRegenerateForm.value = false
    regeneratePassword.value = ""
    regenerateCode.value = ""

    successMessage.value =
      "Se generaron nuevos códigos de recuperación."

    await loadSecurityStatus()
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudieron generar nuevos códigos."
  } finally {
    processing.value = false
  }
}

async function copyRecoveryCodes() {
  if (!recoveryCodes.value.length) {
    return
  }

  try {
    await navigator.clipboard.writeText(
      recoveryCodes.value.join("\n")
    )

    successMessage.value =
      "Códigos copiados al portapapeles."
  } catch {
    errorMessage.value =
      "No se pudieron copiar los códigos."
  }
}

function downloadRecoveryCodes() {
  if (!recoveryCodes.value.length) {
    return
  }

  const content = [
    "Copier OS",
    "Códigos de recuperación",
    "",
    ...recoveryCodes.value,
    "",
    "Cada código puede utilizarse una sola vez.",
  ].join("\n")

  const blob = new Blob(
    [content],
    {
      type: "text/plain;charset=utf-8",
    }
  )

  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")

  link.href = url
  link.download =
    "copier-os-codigos-recuperacion.txt"

  document.body.appendChild(link)
  link.click()
  link.remove()

  URL.revokeObjectURL(url)
}

function formatDate(value) {
  if (!value) {
    return "Sin registro"
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return "Sin registro"
  }

  return new Intl.DateTimeFormat(
    "es-PE",
    {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }
  ).format(date)
}

onMounted(() => {
  loadSecurityStatus()
})
</script>

<template>
  <section class="security-page">
    <header class="page-header">
      <div>
        <span class="page-kicker">
          Seguridad
        </span>

        <h2>Seguridad de la cuenta</h2>

        <p>
          Configura la autenticación en dos pasos,
          códigos de recuperación y llaves de acceso.
        </p>
      </div>
    </header>

    <div
      v-if="successMessage"
      class="message success-message"
    >
      {{ successMessage }}
    </div>

    <div
      v-if="errorMessage"
      class="message error-message"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="loading"
      class="loading-card"
    >
      <span class="spinner"></span>
      Cargando configuración de seguridad...
    </div>

    <template v-else>
      <section class="security-card">
        <header class="card-header">
          <div class="security-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M12 3l7 4v5c0 5-3.5 7.5-7 9-3.5-1.5-7-4-7-9V7l7-4z" />
              <path d="M9 12l2 2 4-4" />
            </svg>
          </div>

          <div class="card-title">
            <h3>Autenticación en dos pasos</h3>

            <p>
              Protege tu cuenta con un código temporal
              generado por una aplicación autenticadora.
            </p>
          </div>

          <span
            class="status-badge"
            :class="{
              active: twoFactorEnabled,
              inactive: !twoFactorEnabled,
            }"
          >
            {{
              twoFactorEnabled
                ? "Activada"
                : "Desactivada"
            }}
          </span>
        </header>

        <div class="card-content">
          <div class="status-grid">
            <div class="status-item">
              <span>Método</span>

              <strong>
                {{
                  twoFactorEnabled
                    ? "Aplicación autenticadora"
                    : "No configurado"
                }}
              </strong>
            </div>

            <div class="status-item">
              <span>Confirmado el</span>

              <strong>
                {{
                  formatDate(
                    securityStatus.totp_confirmed_at
                  )
                }}
              </strong>
            </div>

            <div class="status-item">
              <span>Códigos disponibles</span>

              <strong>
                {{
                  securityStatus
                    .recovery_codes_available
                }}
              </strong>
            </div>
          </div>

          <div
            v-if="
              !twoFactorEnabled &&
              !hasSetupPending
            "
            class="action-box"
          >
            <div>
              <strong>
                Activa una aplicación autenticadora
              </strong>

              <p>
                Puedes utilizar Google Authenticator,
                Microsoft Authenticator, Authy u otra
                aplicación compatible con códigos TOTP.
              </p>
            </div>

            <button
              class="primary-button"
              type="button"
              :disabled="processing"
              @click="startSetup"
            >
              {{
                processing
                  ? "Preparando..."
                  : "Configurar autenticador"
              }}
            </button>
          </div>

          <div
            v-if="hasSetupPending"
            class="setup-container"
          >
            <div class="setup-instructions">
              <span class="step-number">1</span>

              <div>
                <strong>
                  Escanea el código QR
                </strong>

                <p>
                  Abre tu aplicación autenticadora y
                  agrega una nueva cuenta escaneando
                  este código.
                </p>
              </div>
            </div>

            <div class="qr-container">
              <img
                :src="setupData.qr_code"
                alt="Código QR para configurar el autenticador"
              />
            </div>

            <div class="manual-secret">
              <span>
                También puedes ingresar esta clave
                manualmente:
              </span>

              <code>{{ setupData.secret }}</code>
            </div>

            <div class="setup-instructions">
              <span class="step-number">2</span>

              <div>
                <strong>
                  Confirma el código
                </strong>

                <p>
                  Escribe el código de seis números que
                  muestra la aplicación.
                </p>
              </div>
            </div>

            <form
              class="confirmation-form"
              @submit.prevent="confirmSetup"
            >
              <input
                v-model="confirmationCode"
                class="code-input"
                type="text"
                inputmode="numeric"
                autocomplete="one-time-code"
                maxlength="6"
                placeholder="000000"
                required
              />

              <div class="form-buttons">
                <button
                  class="secondary-button"
                  type="button"
                  :disabled="processing"
                  @click="cancelSetup"
                >
                  Cancelar
                </button>

                <button
                  class="primary-button"
                  type="submit"
                  :disabled="processing"
                >
                  {{
                    processing
                      ? "Confirmando..."
                      : "Confirmar y activar"
                  }}
                </button>
              </div>
            </form>
          </div>

          <div
            v-if="twoFactorEnabled"
            class="enabled-actions"
          >
            <button
              class="secondary-button"
              type="button"
              @click="
                showRegenerateForm =
                  !showRegenerateForm
              "
            >
              Generar nuevos códigos
            </button>

            <button
              class="danger-button"
              type="button"
              @click="
                showDisableForm =
                  !showDisableForm
              "
            >
              Desactivar 2FA
            </button>
          </div>

          <form
            v-if="
              twoFactorEnabled &&
              showRegenerateForm
            "
            class="security-form"
            @submit.prevent="submitRegenerateCodes"
          >
            <h4>
              Generar nuevos códigos de recuperación
            </h4>

            <p>
              Los códigos anteriores dejarán de funcionar.
            </p>

            <label>
              <span>Contraseña actual</span>

              <input
                v-model="regeneratePassword"
                type="password"
                autocomplete="current-password"
                required
              />
            </label>

            <label>
              <span>Código del autenticador</span>

              <input
                v-model="regenerateCode"
                type="text"
                inputmode="numeric"
                autocomplete="one-time-code"
                placeholder="000000"
                required
              />
            </label>

            <div class="form-buttons">
              <button
                class="secondary-button"
                type="button"
                @click="showRegenerateForm = false"
              >
                Cancelar
              </button>

              <button
                class="primary-button"
                type="submit"
                :disabled="processing"
              >
                Generar códigos
              </button>
            </div>
          </form>

          <form
            v-if="
              twoFactorEnabled &&
              showDisableForm
            "
            class="security-form danger-form"
            @submit.prevent="submitDisable"
          >
            <h4>
              Desactivar autenticación en dos pasos
            </h4>

            <p>
              Tu cuenta quedará protegida únicamente
              con la contraseña.
            </p>

            <label>
              <span>Contraseña actual</span>

              <input
                v-model="disablePassword"
                type="password"
                autocomplete="current-password"
                required
              />
            </label>

            <label>
              <span>
                Código del autenticador o recuperación
              </span>

              <input
                v-model="disableCode"
                type="text"
                autocomplete="one-time-code"
                required
              />
            </label>

            <div class="form-buttons">
              <button
                class="secondary-button"
                type="button"
                @click="showDisableForm = false"
              >
                Cancelar
              </button>

              <button
                class="danger-button"
                type="submit"
                :disabled="processing"
              >
                Confirmar desactivación
              </button>
            </div>
          </form>
        </div>
      </section>

      <section
        v-if="recoveryCodes.length"
        class="security-card recovery-card"
      >
        <header class="card-header">
          <div class="security-icon recovery">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <rect x="5" y="3" width="14" height="18" rx="2" />
              <path d="M8 8h8" />
              <path d="M8 12h8" />
              <path d="M8 16h5" />
            </svg>
          </div>

          <div class="card-title">
            <h3>Códigos de recuperación</h3>

            <p>
              Guarda estos códigos en un lugar seguro.
              Cada código funciona una sola vez.
            </p>
          </div>
        </header>

        <div class="card-content">
          <div class="warning-message">
            Estos códigos solo se mostrarán durante
            esta sesión.
          </div>

          <div class="codes-grid">
            <code
              v-for="code in recoveryCodes"
              :key="code"
            >
              {{ code }}
            </code>
          </div>

          <div class="codes-actions">
            <button
              class="secondary-button"
              type="button"
              @click="copyRecoveryCodes"
            >
              Copiar códigos
            </button>

            <button
              class="secondary-button"
              type="button"
              @click="downloadRecoveryCodes"
            >
              Guardar archivo
            </button>
          </div>
        </div>
      </section>

      <section class="security-card">
        <header class="card-header">
          <div class="security-icon passkey">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle cx="8" cy="15" r="3" />
              <path d="M11 15h10" />
              <path d="M17 15v3" />
              <path d="M20 15v2" />
              <path d="M8 12V8a4 4 0 0 1 8 0v1" />
            </svg>
          </div>

          <div class="card-title">
            <h3>Llaves de acceso</h3>

            <p>
              Utiliza Windows Hello, Touch ID,
              Face ID o una llave física compatible.
            </p>
          </div>

          <span class="status-badge inactive">
            Próximamente
          </span>
        </header>

        <div class="card-content">
          <div class="status-grid">
            <div class="status-item">
              <span>Llaves registradas</span>

              <strong>
                {{
                  securityStatus.passkeys_registered
                }}
              </strong>
            </div>

            <div class="status-item">
              <span>Acceso con passkey</span>

              <strong>
                {{
                  securityStatus.allow_passkey_login
                    ? "Permitido"
                    : "Desactivado"
                }}
              </strong>
            </div>
          </div>

          <p class="coming-soon-message">
            El modelo de passkeys ya está creado. Falta
            implementar el registro y validación WebAuthn
            en Django y Vue.
          </p>
        </div>
      </section>
    </template>
  </section>
</template>

<style scoped>
button,
input {
  font: inherit;
}

.security-page {
  --brand-blue: #1f35c4;
  --brand-blue-dark: #162caa;
  --brand-blue-soft: #4e63d8;
  --brand-blue-light: #edf0ff;
  --brand-gray: #8693a4;
  --brand-gray-dark: #667382;
  --brand-gray-light: #f1f3f7;
  --text-primary: #1d2940;
  --border-color: #dfe3ec;

  display: flex;
  animation: pageReveal 0.42s ease-out;
  flex-direction: column;
  gap: 20px;
}

.page-header h2 {
  margin: 0;
  color: #1d2940;
  font-size: 28px;
}

.page-header p {
  margin: 8px 0 0;
  color: #667382;
  font-size: 14px;
}

.page-kicker {
  display: block;
  margin-bottom: 6px;
  color: #1f35c4;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.message {
  padding: 12px 14px;
  animation: messageReveal 0.25s ease-out;
  border-radius: 10px;
  font-size: 13px;
}

.success-message {
  border: 1px solid #cfd5f7;
  background: #edf0ff;
  color: #1f35c4;
}

.error-message {
  border: 1px solid #d8ddea;
  background: #f3f5fb;
  color: #667382;
}

.loading-card {
  min-height: 220px;
  animation: cardReveal 0.35s ease-out;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: 1px solid #dfe3ec;
  border-radius: 15px;
  background: white;
  color: #667382;
}

.spinner {
  width: 21px;
  height: 21px;
  border: 3px solid #d9deea;
  border-top-color: #1f35c4;
  border-radius: 50%;
  animation: rotate 0.8s linear infinite;
}

@keyframes rotate {
  to {
    transform: rotate(360deg);
  }
}

.security-card {
  overflow: hidden;
  animation: sectionReveal 0.45s ease-out both;
  transition:
    transform 0.22s ease,
    box-shadow 0.22s ease,
    border-color 0.22s ease;
  border: 1px solid #dfe3ec;
  border-radius: 15px;
  background: white;
}

.qr-container img:hover {
  transform: scale(1.025);
  box-shadow: 0 16px 30px rgba(31, 53, 196, 0.12);
}

.security-card:nth-of-type(2) {
  animation-delay: 0.08s;
}

.security-card:nth-of-type(3) {
  animation-delay: 0.16s;
}

.security-card:hover {
  transform: translateY(-2px);
  border-color: #cfd5f7;
  box-shadow: 0 16px 30px rgba(31, 53, 196, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  border-bottom: 1px solid #e8ebf1;
  background: #f8f9fd;
}

.security-icon {
  width: 48px;
  height: 48px;
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 13px;
  background: #edf0ff;
  color: #1f35c4;
  font-size: 21px;
  font-weight: 900;
  animation: iconFloat 4s ease-in-out infinite;
}

.security-icon svg {
  width: 23px;
  height: 23px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.security-icon.recovery {
  background: #f1f3ff;
  color: #4e63d8;
}

.security-icon.passkey {
  background: #eef0f4;
  color: #667382;
}

.card-title {
  flex: 1;
}

.card-title h3 {
  margin: 0;
  color: #1d2940;
  font-size: 16px;
}

.card-title p {
  margin: 5px 0 0;
  color: #8693a4;
  font-size: 12px;
  line-height: 1.5;
}

.status-badge {
  display: inline-flex;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
}

.status-badge.active {
  background: #edf0ff;
  color: #1f35c4;
}

.status-badge.inactive {
  background: #eef0f4;
  color: #667382;
}

.card-content {
  padding: 20px;
}

.status-grid {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.status-item {
  padding: 14px;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease;
  border: 1px solid #dfe3ec;
  border-radius: 10px;
  background: #f8f9fd;
}

.status-item:hover {
  transform: translateY(-2px);
  border-color: #cfd5f7;
  background: #f4f6ff;
  box-shadow: 0 8px 16px rgba(31, 53, 196, 0.06);
}

.status-item span,
.status-item strong {
  display: block;
}

.status-item span {
  color: #8693a4;
  font-size: 11px;
}

.status-item strong {
  margin-top: 5px;
  color: #1d2940;
  font-size: 13px;
}

.action-box {
  display: flex;
  animation: panelReveal 0.35s ease-out;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-top: 18px;
  padding: 17px;
  border: 1px solid #cfd5f7;
  border-radius: 11px;
  background: #f4f6ff;
}

.action-box strong {
  color: #1d2940;
  font-size: 13px;
}

.action-box p {
  margin: 5px 0 0;
  color: #667382;
  font-size: 12px;
  line-height: 1.5;
}

.setup-container {
  margin-top: 18px;
  animation: panelReveal 0.35s ease-out;
  padding: 20px;
  border: 1px solid #cfd5f7;
  border-radius: 12px;
  background: #f8f9ff;
}

.setup-instructions {
  display: flex;
  align-items: flex-start;
  gap: 11px;
}

.setup-instructions strong {
  color: #1d2940;
  font-size: 13px;
}

.setup-instructions p {
  margin: 5px 0 0;
  color: #667382;
  font-size: 12px;
  line-height: 1.5;
}

.step-number {
  width: 26px;
  height: 26px;
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #1f35c4;
  color: white;
  font-size: 12px;
  font-weight: 800;
}

.qr-container {
  display: flex;
  justify-content: center;
  padding: 22px 0;
}

.qr-container img {
  width: min(250px, 100%);
  transition:
    transform 0.25s ease,
    box-shadow 0.25s ease;
  padding: 10px;
  border: 1px solid #dfe3ec;
  border-radius: 12px;
  background: white;
}

.manual-secret {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-bottom: 22px;
  text-align: center;
}

.manual-secret span {
  color: #8693a4;
  font-size: 11px;
}

.manual-secret code {
  max-width: 100%;
  overflow-wrap: anywhere;
  padding: 9px 12px;
  border-radius: 8px;
  background: #eef0f4;
  color: #1d2940;
  font-size: 12px;
  font-weight: 800;
}

.confirmation-form {
  margin-top: 16px;
}

.code-input {
  width: 100%;
  min-height: 52px;
  box-sizing: border-box;
  padding: 0 14px;
  border: 1px solid #dfe3ec;
  border-radius: 10px;
  outline: none;
  text-align: center;
  color: #1d2940;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: 0.3em;
}

.code-input:focus {
  border-color: #4e63d8;
  box-shadow:
    0 0 0 4px rgba(31, 53, 196, 0.12);
}

.enabled-actions,
.codes-actions,
.form-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 9px;
}

.enabled-actions {
  margin-top: 18px;
}

.form-buttons {
  margin-top: 15px;
}

.primary-button,
.secondary-button,
.danger-button {
  min-height: 41px;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    background 0.2s ease,
    border-color 0.2s ease;
  padding: 0 15px;
  border-radius: 9px;
  font-weight: 700;
  cursor: pointer;
}

.primary-button {
  border: 0;
  background: linear-gradient(
    135deg,
    #162caa,
    #1f35c4 55%,
    #4e63d8
  );
  color: white;
  box-shadow: 0 10px 22px rgba(31, 53, 196, 0.20);
}

.secondary-button {
  border: 1px solid #dfe3ec;
  background: white;
  color: #667382;
}

.danger-button {
  border: 1px solid #d8ddea;
  background: #f3f5fb;
  color: #667382;
}

.primary-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 14px 28px rgba(31, 53, 196, 0.28);
}

.secondary-button:hover:not(:disabled) {
  transform: translateY(-2px);
  border-color: #cfd5f7;
  background: #edf0ff;
  color: #1f35c4;
}

.danger-button:hover:not(:disabled) {
  transform: translateY(-2px);
  border-color: #cfd5f7;
  background: #eef0f5;
  color: #4e63d8;
}

.primary-button:disabled,
.secondary-button:disabled,
.danger-button:disabled {
  opacity: 0.6;
  cursor: wait;
}

.security-form {
  display: flex;
  animation: panelReveal 0.3s ease-out;
  flex-direction: column;
  gap: 14px;
  margin-top: 18px;
  padding: 17px;
  border: 1px solid #dfe3ec;
  border-radius: 11px;
  background: #f8f9fd;
}

.security-form.danger-form {
  border-color: #d8ddea;
  background: #f8f9fd;
}

.security-form h4 {
  margin: 0;
  color: #1d2940;
  font-size: 14px;
}

.security-form p {
  margin: -7px 0 2px;
  color: #8693a4;
  font-size: 12px;
}

.security-form label {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.security-form label span {
  color: #667382;
  font-size: 12px;
  font-weight: 700;
}

.security-form input {
  min-height: 43px;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
  padding: 0 12px;
  border: 1px solid #dfe3ec;
  border-radius: 9px;
  outline: none;
}

.security-form input:focus {
  transform: translateY(-1px);
  border-color: #4e63d8;
  box-shadow: 0 0 0 3px rgba(31, 53, 196, 0.12);
}

.warning-message {
  padding: 12px 13px;
  border: 1px solid #d8ddea;
  border-radius: 9px;
  background: #f5f6fa;
  color: #667382;
  font-size: 12px;
}

.codes-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 9px;
  margin: 16px 0;
}

.codes-grid code {
  padding: 11px;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    background 0.2s ease;
  border: 1px solid #dfe3ec;
  border-radius: 8px;
  background: #f5f6fa;
  color: #1d2940;
  text-align: center;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.codes-grid code:hover {
  transform: translateY(-2px);
  border-color: #cfd5f7;
  background: #edf0ff;
}

.coming-soon-message {
  margin: 18px 0 0;
  padding: 13px;
  border-radius: 9px;
  background: #f1f3f7;
  color: #667382;
  font-size: 12px;
  line-height: 1.5;
}

@keyframes pageReveal {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes sectionReveal {
  from {
    opacity: 0;
    transform: translateY(14px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes cardReveal {
  from {
    opacity: 0;
    transform: scale(0.985);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes messageReveal {
  from {
    opacity: 0;
    transform: translateY(-6px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes panelReveal {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes iconFloat {
  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-3px);
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

@media (max-width: 760px) {
  .card-header {
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .status-grid,
  .codes-grid {
    grid-template-columns: 1fr;
  }

  .action-box {
    align-items: stretch;
    flex-direction: column;
  }

  .enabled-actions,
  .codes-actions,
  .form-buttons {
    flex-direction: column;
  }

  .primary-button,
  .secondary-button,
  .danger-button {
    width: 100%;
  }
}
</style>