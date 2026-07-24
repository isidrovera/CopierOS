<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from "vue"

import {
  useRoute,
  useRouter,
} from "vue-router"

import {
  createUser,
  getUser,
  updateUser,
} from "../../services/users.service"

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const errorMessage = ref("")

const isEditing = computed(() => {
  return Boolean(route.params.id)
})

const pageTitle = computed(() => {
  return isEditing.value
    ? "Editar usuario"
    : "Nuevo usuario"
})

const form = reactive({
  dni: "",
  email: "",
  first_name: "",
  paternal_last_name: "",
  maternal_last_name: "",
  personal_phone: "",
  work_phone: "",
  work_extension: "",
  job_title: "",
  department_name: "",
  company_name: "",
  address: "",
  ubigeo: "",
  district: "",
  province: "",
  region: "",
  registration_source: "manual",
  password: "",
  password_confirmation: "",
  is_active: true,
  is_staff: false,
  is_verified: false,
  must_change_password: true,
})

function normalizeText(value) {
  return typeof value === "string"
    ? value.trim()
    : value
}

function buildPayload() {
  const payload = {
    dni: normalizeText(form.dni) || null,
    email: normalizeText(form.email).toLowerCase(),
    first_name: normalizeText(form.first_name),
    paternal_last_name: normalizeText(
      form.paternal_last_name
    ),
    maternal_last_name: normalizeText(
      form.maternal_last_name
    ),
    personal_phone:
      normalizeText(form.personal_phone) || "",
    work_phone:
      normalizeText(form.work_phone) || "",
    work_extension:
      normalizeText(form.work_extension) || "",
    job_title:
      normalizeText(form.job_title) || "",
    department_name:
      normalizeText(form.department_name) || "",
    company_name:
      normalizeText(form.company_name) || "",
    address:
      normalizeText(form.address) || "",
    ubigeo:
      normalizeText(form.ubigeo) || "",
    district:
      normalizeText(form.district) || "",
    province:
      normalizeText(form.province) || "",
    region:
      normalizeText(form.region) || "",
    is_active: form.is_active,
    is_staff: form.is_staff,
    is_verified: form.is_verified,
    must_change_password:
      form.must_change_password,
  }

  if (!isEditing.value) {
    payload.registration_source =
      form.registration_source

    payload.password = form.password
    payload.password_confirmation =
      form.password_confirmation
  }

  return payload
}

function validateForm() {
  if (!form.email.trim()) {
    return "El correo electrónico es obligatorio."
  }

  if (!form.first_name.trim()) {
    return "Los nombres son obligatorios."
  }

  if (!form.paternal_last_name.trim()) {
    return "El apellido paterno es obligatorio."
  }

  if (!isEditing.value) {
    if (!form.password) {
      return "La contraseña es obligatoria."
    }

    if (
      form.password !==
      form.password_confirmation
    ) {
      return "Las contraseñas no coinciden."
    }
  }

  return ""
}

async function loadUser() {
  if (!isEditing.value) {
    return
  }

  loading.value = true
  errorMessage.value = ""

  try {
    const user = await getUser(route.params.id)

    form.dni = user.dni || ""
    form.email = user.email || ""
    form.first_name = user.first_name || ""
    form.paternal_last_name =
      user.paternal_last_name || ""
    form.maternal_last_name =
      user.maternal_last_name || ""
    form.personal_phone =
      user.personal_phone || ""
    form.work_phone =
      user.work_phone || ""
    form.work_extension =
      user.work_extension || ""
    form.job_title =
      user.job_title || ""
    form.department_name =
      user.department_name || ""
    form.company_name =
      user.company_name || ""
    form.address =
      user.address || ""
    form.ubigeo =
      user.ubigeo || ""
    form.district =
      user.district || ""
    form.province =
      user.province || ""
    form.region =
      user.region || ""
    form.registration_source =
      user.registration_source || "manual"
    form.is_active =
      Boolean(user.is_active)
    form.is_staff =
      Boolean(user.is_staff)
    form.is_verified =
      Boolean(user.is_verified)
    form.must_change_password =
      Boolean(user.must_change_password)
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo cargar el usuario."
  } finally {
    loading.value = false
  }
}

async function submitForm() {
  errorMessage.value = ""

  const validationError = validateForm()

  if (validationError) {
    errorMessage.value = validationError
    return
  }

  saving.value = true

  try {
    const payload = buildPayload()

    if (isEditing.value) {
      await updateUser(
        route.params.id,
        payload
      )
    } else {
      await createUser(payload)
    }

    await router.push({
      name: "users",
    })
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo guardar el usuario."
  } finally {
    saving.value = false
  }
}

async function cancel() {
  await router.push({
    name: "users",
  })
}

onMounted(() => {
  loadUser()
})
</script>

<template>
  <section class="user-form-page">
    <header class="page-header">
      <div>
        <span class="page-kicker">
          Administración de usuarios
        </span>

        <h2>{{ pageTitle }}</h2>

        <p>
          {{
            isEditing
              ? "Modifica los datos personales, laborales y de acceso."
              : "Registra un nuevo usuario en Copier OS."
          }}
        </p>
      </div>

      <button
        class="back-button"
        type="button"
        @click="cancel"
      >
        <svg
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path d="M19 12H5" />
          <path d="M12 19l-7-7 7-7" />
        </svg>

        <span>Volver</span>
      </button>
    </header>

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
      Cargando información...
    </div>

    <form
      v-else
      class="form-container"
      @submit.prevent="submitForm"
    >
      <section class="form-section">
        <header class="section-header">
          <div>
            <h3>Datos personales</h3>
            <p>
              Información principal de identificación.
            </p>
          </div>
        </header>

        <div class="form-grid">
          <label class="form-field">
            <span>DNI</span>

            <input
              v-model="form.dni"
              type="text"
              maxlength="20"
              placeholder="Número de documento"
            />
          </label>

          <label class="form-field required">
            <span>Correo electrónico</span>

            <input
              v-model="form.email"
              type="email"
              autocomplete="email"
              placeholder="usuario@empresa.com"
              required
            />
          </label>

          <label class="form-field required">
            <span>Nombres</span>

            <input
              v-model="form.first_name"
              type="text"
              placeholder="Nombres"
              required
            />
          </label>

          <label class="form-field required">
            <span>Apellido paterno</span>

            <input
              v-model="form.paternal_last_name"
              type="text"
              placeholder="Apellido paterno"
              required
            />
          </label>

          <label class="form-field">
            <span>Apellido materno</span>

            <input
              v-model="form.maternal_last_name"
              type="text"
              placeholder="Apellido materno"
            />
          </label>

          <label class="form-field">
            <span>Teléfono personal</span>

            <input
              v-model="form.personal_phone"
              type="tel"
              placeholder="Número personal"
            />
          </label>
        </div>
      </section>

      <section class="form-section">
        <header class="section-header">
          <div>
            <h3>Información laboral</h3>
            <p>
              Empresa, cargo, área y datos de contacto.
            </p>
          </div>
        </header>

        <div class="form-grid">
          <label class="form-field">
            <span>Empresa</span>

            <input
              v-model="form.company_name"
              type="text"
              placeholder="Nombre de la empresa"
            />
          </label>

          <label class="form-field">
            <span>Área o departamento</span>

            <input
              v-model="form.department_name"
              type="text"
              placeholder="Área de trabajo"
            />
          </label>

          <label class="form-field">
            <span>Cargo</span>

            <input
              v-model="form.job_title"
              type="text"
              placeholder="Cargo del usuario"
            />
          </label>

          <label class="form-field">
            <span>Teléfono laboral</span>

            <input
              v-model="form.work_phone"
              type="tel"
              placeholder="Teléfono de trabajo"
            />
          </label>

          <label class="form-field">
            <span>Anexo</span>

            <input
              v-model="form.work_extension"
              type="text"
              placeholder="Anexo"
            />
          </label>
        </div>
      </section>

      <section class="form-section">
        <header class="section-header">
          <div>
            <h3>Dirección</h3>
            <p>
              Ubicación y datos geográficos del usuario.
            </p>
          </div>
        </header>

        <div class="form-grid">
          <label class="form-field full-width">
            <span>Dirección</span>

            <input
              v-model="form.address"
              type="text"
              placeholder="Dirección completa"
            />
          </label>

          <label class="form-field">
            <span>Ubigeo</span>

            <input
              v-model="form.ubigeo"
              type="text"
              placeholder="Código de ubigeo"
            />
          </label>

          <label class="form-field">
            <span>Distrito</span>

            <input
              v-model="form.district"
              type="text"
              placeholder="Distrito"
            />
          </label>

          <label class="form-field">
            <span>Provincia</span>

            <input
              v-model="form.province"
              type="text"
              placeholder="Provincia"
            />
          </label>

          <label class="form-field">
            <span>Región</span>

            <input
              v-model="form.region"
              type="text"
              placeholder="Región"
            />
          </label>
        </div>
      </section>

      <section
        v-if="!isEditing"
        class="form-section"
      >
        <header class="section-header">
          <div>
            <h3>Contraseña inicial</h3>
            <p>
              El usuario podrá cambiarla al ingresar.
            </p>
          </div>
        </header>

        <div class="form-grid">
          <label class="form-field required">
            <span>Contraseña</span>

            <input
              v-model="form.password"
              type="password"
              autocomplete="new-password"
              placeholder="Contraseña inicial"
              required
            />
          </label>

          <label class="form-field required">
            <span>Confirmar contraseña</span>

            <input
              v-model="form.password_confirmation"
              type="password"
              autocomplete="new-password"
              placeholder="Repite la contraseña"
              required
            />
          </label>

          <label class="form-field">
            <span>Origen de registro</span>

            <select
              v-model="form.registration_source"
            >
              <option value="manual">
                Registro manual
              </option>

              <option value="dni">
                Consulta por DNI
              </option>

              <option value="import">
                Importación
              </option>
            </select>
          </label>
        </div>
      </section>

      <section class="form-section">
        <header class="section-header">
          <div>
            <h3>Acceso y seguridad</h3>
            <p>
              Configuración de acceso al sistema.
            </p>
          </div>
        </header>

        <div class="options-grid">
          <label class="option-card">
            <input
              v-model="form.is_active"
              type="checkbox"
            />

            <div>
              <strong>Usuario activo</strong>

              <span>
                Puede iniciar sesión en el sistema.
              </span>
            </div>
          </label>

          <label class="option-card">
            <input
              v-model="form.is_staff"
              type="checkbox"
            />

            <div>
              <strong>Administrador</strong>

              <span>
                Puede administrar usuarios y acceder
                al panel administrativo.
              </span>
            </div>
          </label>

          <label class="option-card">
            <input
              v-model="form.is_verified"
              type="checkbox"
            />

            <div>
              <strong>Usuario verificado</strong>

              <span>
                La identidad del usuario fue validada.
              </span>
            </div>
          </label>

          <label class="option-card">
            <input
              v-model="form.must_change_password"
              type="checkbox"
            />

            <div>
              <strong>Cambiar contraseña</strong>

              <span>
                Solicitar cambio de contraseña al
                próximo ingreso.
              </span>
            </div>
          </label>
        </div>
      </section>

      <footer class="form-actions">
        <button
          class="secondary-button"
          type="button"
          :disabled="saving"
          @click="cancel"
        >
          Cancelar
        </button>

        <button
          class="primary-button"
          type="submit"
          :disabled="saving"
        >
          <span
            v-if="saving"
            class="button-spinner"
          ></span>

          {{
            saving
              ? "Guardando..."
              : isEditing
                ? "Guardar cambios"
                : "Crear usuario"
          }}
        </button>
      </footer>
    </form>
  </section>
</template>

<style scoped>
button,
input,
select {
  font: inherit;
}

.user-form-page {
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

.page-header {
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
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

.back-button {
  min-height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 15px;
  border: 1px solid #dfe3ec;
  border-radius: 10px;
  background: white;
  color: #667382;
  cursor: pointer;
}

.back-button:hover {
  transform: translateY(-2px);
  border-color: #cfd5f7;
  background: #edf0ff;
  color: #1f35c4;
  box-shadow: 0 8px 18px rgba(31, 53, 196, 0.10);
}

.back-button svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.message {
  padding: 12px 14px;
  animation: messageReveal 0.25s ease-out;
  border-radius: 10px;
  font-size: 13px;
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

.spinner,
.button-spinner {
  display: inline-block;
  border-radius: 50%;
  animation: rotate 0.8s linear infinite;
}

.spinner {
  width: 21px;
  height: 21px;
  border: 3px solid #d9deea;
  border-top-color: #1f35c4;
}

.button-spinner {
  width: 15px;
  height: 15px;
  border: 2px solid rgba(255, 255, 255, 0.45);
  border-top-color: white;
}

@keyframes rotate {
  to {
    transform: rotate(360deg);
  }
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-section {
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

.form-section:nth-child(2) {
  animation-delay: 0.05s;
}

.form-section:nth-child(3) {
  animation-delay: 0.10s;
}

.form-section:nth-child(4) {
  animation-delay: 0.15s;
}

.form-section:nth-child(5) {
  animation-delay: 0.20s;
}

.form-section:hover {
  transform: translateY(-2px);
  border-color: #cfd5f7;
  box-shadow: 0 14px 28px rgba(31, 53, 196, 0.07);
}

.section-header {
  padding: 18px 20px;
  border-bottom: 1px solid #e8ebf1;
  background: #f8f9fd;
}

.section-header h3 {
  margin: 0;
  color: #1d2940;
  font-size: 16px;
}

.section-header p {
  margin: 5px 0 0;
  color: #8693a4;
  font-size: 12px;
}

.form-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 17px;
  padding: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.form-field.full-width {
  grid-column: 1 / -1;
}

.form-field > span {
  color: #667382;
  font-size: 12px;
  font-weight: 700;
}

.form-field.required > span::after {
  content: " *";
  color: #4e63d8;
}

.form-field input,
.form-field select {
  width: 100%;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease,
    background 0.2s ease;
  min-height: 43px;
  box-sizing: border-box;
  padding: 0 12px;
  border: 1px solid #dfe3ec;
  border-radius: 9px;
  outline: none;
  background: white;
  color: #1d2940;
}

.form-field input:focus,
.form-field select:focus {
  transform: translateY(-1px);
  border-color: #4e63d8;
  box-shadow:
    0 0 0 3px rgba(31, 53, 196, 0.12);
}

.form-field input::placeholder {
  color: #9aa4b2;
}

.options-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 12px;
  padding: 20px;
}

.option-card {
  display: flex;
  position: relative;
  overflow: hidden;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease;
  align-items: flex-start;
  gap: 11px;
  padding: 15px;
  border: 1px solid #dfe3ec;
  border-radius: 11px;
  background: #f8f9fd;
  cursor: pointer;
}

.option-card:hover {
  transform: translateY(-2px);
  border-color: #cfd5f7;
  background: #f4f6ff;
  box-shadow: 0 10px 20px rgba(31, 53, 196, 0.07);
}

.option-card:has(input:checked) {
  border-color: #bfc7f4;
  background: linear-gradient(135deg, #edf0ff, #f8f9ff);
  box-shadow: inset 3px 0 0 #1f35c4;
}

.option-card input {
  width: 17px;
  height: 17px;
  margin-top: 2px;
  accent-color: #1f35c4;
}

.option-card strong,
.option-card span {
  display: block;
}

.option-card strong {
  color: #1d2940;
  font-size: 13px;
}

.option-card span {
  margin-top: 4px;
  color: #8693a4;
  font-size: 11px;
  line-height: 1.45;
}

.form-actions {
  position: sticky;
  z-index: 8;
  bottom: 14px;
  display: flex;
  animation: actionsReveal 0.45s ease-out;
  justify-content: flex-end;
  gap: 10px;
  padding: 17px 20px;
  border: 1px solid #dfe3ec;
  border-radius: 15px;
  background: white;
}

.secondary-button,
.primary-button {
  min-height: 43px;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    background 0.2s ease,
    border-color 0.2s ease;
  padding: 0 18px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}

.secondary-button {
  border: 1px solid #dfe3ec;
  background: white;
  color: #667382;
}

.primary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
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

.secondary-button:hover {
  transform: translateY(-2px);
  border-color: #cfd5f7;
  background: #edf0ff;
  color: #1f35c4;
}

.primary-button:hover {
  transform: translateY(-2px);
  background: linear-gradient(
    135deg,
    #132596,
    #1f35c4 50%,
    #4358d0
  );
  box-shadow: 0 14px 28px rgba(31, 53, 196, 0.28);
}

.secondary-button:disabled,
.primary-button:disabled {
  opacity: 0.6;
  cursor: wait;
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

@keyframes actionsReveal {
  from {
    opacity: 0;
    transform: translateY(12px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
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
  .page-header {
    flex-direction: column;
  }

  .form-grid,
  .options-grid {
    grid-template-columns: 1fr;
  }

  .form-field.full-width {
    grid-column: auto;
  }
}

@media (max-width: 520px) {
  .form-actions {
    flex-direction: column-reverse;
  }

  .secondary-button,
  .primary-button {
    width: 100%;
  }
}
</style>