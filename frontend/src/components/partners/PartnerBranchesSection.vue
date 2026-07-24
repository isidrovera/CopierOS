<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue"

import {
  archiveBranch,
  createBranch,
  getBranches,
  restoreBranch,
  updateBranch,
} from "../../services/partners.service"


const props = defineProps({
  partnerId: {
    type: String,
    required: true,
  },

  users: {
    type: Array,
    default: () => [],
  },
})


const emit = defineEmits([
  "updated",
])


const branches = ref([])
const loading = ref(false)
const saving = ref(false)
const processingId = ref("")
const errorMessage = ref("")
const successMessage = ref("")
const includeArchived = ref(false)

const modalOpen = ref(false)
const editingBranchId = ref("")


const branchTypeOptions = [
  {
    value: "main",
    label: "Sede principal",
  },
  {
    value: "branch",
    label: "Sucursal",
  },
  {
    value: "office",
    label: "Oficina",
  },
  {
    value: "warehouse",
    label: "Almacén",
  },
  {
    value: "project",
    label: "Proyecto",
  },
  {
    value: "worksite",
    label: "Obra",
  },
  {
    value: "store",
    label: "Local",
  },
  {
    value: "plant",
    label: "Planta",
  },
  {
    value: "workshop",
    label: "Taller",
  },
  {
    value: "other",
    label: "Otro",
  },
]


const emptyForm = () => ({
  code: "",
  name: "",
  branch_type: "branch",

  is_main: false,
  is_fiscal: false,

  allows_equipment_installation: true,
  allows_deliveries: true,

  advisor: "",

  country_code: "PE",
  country_name: "Perú",

  address: "",
  address_reference: "",

  ubigeo: "",
  road_type: "",
  road_name: "",
  zone_code: "",
  zone_type: "",
  address_number: "",
  interior: "",
  lot: "",
  apartment: "",
  block: "",
  kilometer: "",

  district: "",
  province: "",
  region: "",
  postal_code: "",

  latitude: "",
  longitude: "",

  general_phone: "",
  mobile_phone: "",
  general_email: "",

  operating_hours: "",
  access_instructions: "",
  installation_notes: "",

  start_date: "",
  end_date: "",

  is_active: true,
  notes: "",
})


const form = reactive(
  emptyForm()
)


const totalBranches = computed(() => {
  return branches.value.length
})


const activeBranches = computed(() => {
  return branches.value.filter(
    (branch) => (
      branch.is_active &&
      !branch.is_archived
    )
  ).length
})


const archivedBranches = computed(() => {
  return branches.value.filter(
    (branch) => branch.is_archived
  ).length
})


const modalTitle = computed(() => {
  return editingBranchId.value
    ? "Editar sucursal o sede"
    : "Nueva sucursal o sede"
})


function normalizeText(value) {
  return typeof value === "string"
    ? value.trim()
    : value
}


function normalizeNullableNumber(value) {
  if (
    value === "" ||
    value === null ||
    value === undefined
  ) {
    return null
  }

  return value
}


function resetForm() {
  Object.assign(
    form,
    emptyForm()
  )

  editingBranchId.value = ""
  errorMessage.value = ""
}


function getBranchTypeName(value) {
  return (
    branchTypeOptions.find(
      (option) => option.value === value
    )?.label ||
    "Otro"
  )
}


function getUserName(user) {
  return (
    user.full_name ||
    [
      user.first_name,
      user.paternal_last_name,
      user.maternal_last_name,
    ]
      .filter(Boolean)
      .join(" ")
      .trim() ||
    user.email ||
    "Usuario"
  )
}


function getAdvisorName(branch) {
  return (
    branch.advisor_name ||
    branch.effective_advisor_name ||
    "Usa la responsable principal"
  )
}


function getLocation(branch) {
  return [
    branch.district,
    branch.province,
    branch.region,
  ]
    .filter(Boolean)
    .join(", ") ||
    branch.country_name ||
    "Sin ubicación"
}


function getStatusClass(branch) {
  if (branch.is_archived) {
    return "archived"
  }

  return branch.is_active
    ? "active"
    : "inactive"
}


function getStatusName(branch) {
  if (branch.is_archived) {
    return "Archivada"
  }

  return branch.is_active
    ? "Activa"
    : "Inactiva"
}


function buildPayload() {
  return {
    partner: props.partnerId,

    code:
      normalizeText(form.code).toUpperCase(),

    name:
      normalizeText(form.name),

    branch_type:
      form.branch_type,

    is_main:
      form.is_main,

    is_fiscal:
      form.is_fiscal,

    allows_equipment_installation:
      form.allows_equipment_installation,

    allows_deliveries:
      form.allows_deliveries,

    advisor:
      form.advisor || null,

    country_code:
      normalizeText(
        form.country_code
      ).toUpperCase(),

    country_name:
      normalizeText(
        form.country_name
      ),

    address:
      normalizeText(form.address),

    address_reference:
      normalizeText(
        form.address_reference
      ),

    ubigeo:
      normalizeText(form.ubigeo),

    road_type:
      normalizeText(form.road_type),

    road_name:
      normalizeText(form.road_name),

    zone_code:
      normalizeText(form.zone_code),

    zone_type:
      normalizeText(form.zone_type),

    address_number:
      normalizeText(
        form.address_number
      ),

    interior:
      normalizeText(form.interior),

    lot:
      normalizeText(form.lot),

    apartment:
      normalizeText(form.apartment),

    block:
      normalizeText(form.block),

    kilometer:
      normalizeText(form.kilometer),

    district:
      normalizeText(form.district),

    province:
      normalizeText(form.province),

    region:
      normalizeText(form.region),

    postal_code:
      normalizeText(form.postal_code),

    latitude:
      normalizeNullableNumber(
        form.latitude
      ),

    longitude:
      normalizeNullableNumber(
        form.longitude
      ),

    general_phone:
      normalizeText(
        form.general_phone
      ),

    mobile_phone:
      normalizeText(
        form.mobile_phone
      ),

    general_email:
      normalizeText(
        form.general_email
      ).toLowerCase(),

    operating_hours:
      normalizeText(
        form.operating_hours
      ),

    access_instructions:
      normalizeText(
        form.access_instructions
      ),

    installation_notes:
      normalizeText(
        form.installation_notes
      ),

    start_date:
      form.start_date || null,

    end_date:
      form.end_date || null,

    is_active:
      form.is_active,

    notes:
      normalizeText(form.notes),
  }
}


function validateForm() {
  if (!form.name.trim()) {
    return "El nombre de la sede es obligatorio."
  }

  if (!form.country_code.trim()) {
    return "El código del país es obligatorio."
  }

  if (
    form.country_code.trim().length !== 2
  ) {
    return (
      "El código del país debe contener " +
      "exactamente dos letras."
    )
  }

  if (!form.country_name.trim()) {
    return "El nombre del país es obligatorio."
  }

  if (!form.address.trim()) {
    return "La dirección de la sede es obligatoria."
  }

  if (
    form.country_code === "PE" &&
    form.ubigeo &&
    !/^\d{6}$/.test(form.ubigeo)
  ) {
    return (
      "El ubigeo peruano debe contener " +
      "exactamente 6 números."
    )
  }

  if (
    form.start_date &&
    form.end_date &&
    form.end_date < form.start_date
  ) {
    return (
      "La fecha de finalización no puede ser " +
      "anterior a la fecha de inicio."
    )
  }

  const latitude = Number(form.latitude)

  if (
    form.latitude !== "" &&
    (
      Number.isNaN(latitude) ||
      latitude < -90 ||
      latitude > 90
    )
  ) {
    return (
      "La latitud debe estar entre -90 y 90."
    )
  }

  const longitude = Number(form.longitude)

  if (
    form.longitude !== "" &&
    (
      Number.isNaN(longitude) ||
      longitude < -180 ||
      longitude > 180
    )
  ) {
    return (
      "La longitud debe estar entre -180 y 180."
    )
  }

  return ""
}


async function loadBranches() {
  loading.value = true
  errorMessage.value = ""

  try {
    const response = await getBranches({
      partner: props.partnerId,
      includeArchived:
        includeArchived.value,
    })

    branches.value = Array.isArray(response)
      ? response
      : response?.results || []
  } catch (error) {
    branches.value = []

    errorMessage.value =
      error.message ||
      "No se pudieron cargar las sucursales."
  } finally {
    loading.value = false
  }
}


function openCreateModal() {
  resetForm()
  modalOpen.value = true
}


function openEditModal(branch) {
  resetForm()

  editingBranchId.value =
    branch.id

  for (
    const field of Object.keys(form)
  ) {
    if (
      Object.prototype.hasOwnProperty.call(
        branch,
        field
      )
    ) {
      form[field] =
        branch[field] ?? form[field]
    }
  }

  form.advisor =
    branch.advisor || ""

  form.latitude =
    branch.latitude ?? ""

  form.longitude =
    branch.longitude ?? ""

  form.start_date =
    branch.start_date || ""

  form.end_date =
    branch.end_date || ""

  form.is_main =
    Boolean(branch.is_main)

  form.is_fiscal =
    Boolean(branch.is_fiscal)

  form.allows_equipment_installation =
    Boolean(
      branch.allows_equipment_installation
    )

  form.allows_deliveries =
    Boolean(branch.allows_deliveries)

  form.is_active =
    Boolean(branch.is_active)

  modalOpen.value = true
}


function closeModal() {
  if (saving.value) {
    return
  }

  modalOpen.value = false
  resetForm()
}


async function submitBranch() {
  errorMessage.value = ""
  successMessage.value = ""

  const validationError =
    validateForm()

  if (validationError) {
    errorMessage.value =
      validationError

    return
  }

  saving.value = true

  try {
    const payload =
      buildPayload()

    if (editingBranchId.value) {
      await updateBranch(
        editingBranchId.value,
        payload
      )

      successMessage.value =
        "Sucursal actualizada correctamente."
    } else {
      await createBranch(payload)

      successMessage.value =
        "Sucursal creada correctamente."
    }

    modalOpen.value = false
    resetForm()

    await loadBranches()

    emit("updated")
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo guardar la sucursal."
  } finally {
    saving.value = false
  }
}


async function handleArchive(branch) {
  const reason = window.prompt(
    `Indica el motivo para archivar la sede "${branch.name}":`
  )

  if (reason === null) {
    return
  }

  const confirmed = window.confirm(
    `¿Confirmas que deseas archivar la sede "${branch.name}"?`
  )

  if (!confirmed) {
    return
  }

  errorMessage.value = ""
  successMessage.value = ""
  processingId.value = branch.id

  try {
    await archiveBranch(
      branch.id,
      reason.trim()
    )

    successMessage.value =
      "Sucursal archivada correctamente."

    await loadBranches()
    emit("updated")
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo archivar la sucursal."
  } finally {
    processingId.value = ""
  }
}


async function handleRestore(branch) {
  const confirmed = window.confirm(
    `¿Confirmas que deseas restaurar la sede "${branch.name}"?`
  )

  if (!confirmed) {
    return
  }

  errorMessage.value = ""
  successMessage.value = ""
  processingId.value = branch.id

  try {
    await restoreBranch(branch.id)

    successMessage.value =
      "Sucursal restaurada correctamente."

    await loadBranches()
    emit("updated")
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo restaurar la sucursal."
  } finally {
    processingId.value = ""
  }
}


watch(
  () => form.branch_type,
  (branchType) => {
    if (branchType === "main") {
      form.is_main = true
    }
  }
)


watch(
  () => form.is_main,
  (isMain) => {
    if (isMain) {
      form.branch_type = "main"
    } else if (
      form.branch_type === "main"
    ) {
      form.branch_type = "branch"
    }
  }
)


watch(
  () => form.country_code,
  (countryCode) => {
    const normalized = String(
      countryCode || ""
    )
      .trim()
      .toUpperCase()

    form.country_code = normalized

    if (normalized === "PE") {
      form.country_name = "Perú"
    }

    if (
      normalized === "US" &&
      !form.country_name
    ) {
      form.country_name =
        "Estados Unidos"
    }
  }
)


onMounted(() => {
  loadBranches()
})
</script>

<template>
  <section class="management-section">
    <header class="management-header">
      <div>
        <span class="section-kicker">
          Ubicaciones
        </span>

        <h3>Sucursales y sedes</h3>

        <p>
          Registra las oficinas, proyectos, obras,
          almacenes y demás ubicaciones del cliente.
        </p>
      </div>

      <button
        class="primary-button"
        type="button"
        @click="openCreateModal"
      >
        <span>＋</span>
        Nueva sucursal
      </button>
    </header>

    <div class="summary-grid">
      <article class="summary-card">
        <small>Total mostradas</small>
        <strong>{{ totalBranches }}</strong>
      </article>

      <article class="summary-card">
        <small>Activas</small>
        <strong>{{ activeBranches }}</strong>
      </article>

      <article class="summary-card">
        <small>Archivadas</small>
        <strong>{{ archivedBranches }}</strong>
      </article>
    </div>

    <div class="toolbar">
      <label class="archive-filter">
        <input
          v-model="includeArchived"
          type="checkbox"
          @change="loadBranches"
        />

        <span>Mostrar archivadas</span>
      </label>

      <button
        class="refresh-button"
        type="button"
        :disabled="loading"
        @click="loadBranches"
      >
        ↻ Actualizar
      </button>
    </div>

    <div
      v-if="successMessage"
      class="message success-message"
    >
      {{ successMessage }}
    </div>

    <div
      v-if="errorMessage && !modalOpen"
      class="message error-message"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="loading"
      class="loading-state"
    >
      <span class="spinner"></span>
      Cargando sucursales...
    </div>

    <div
      v-else-if="!branches.length"
      class="empty-state"
    >
      <span>⌂</span>

      <strong>
        No hay sucursales registradas
      </strong>

      <p>
        Registra la sede principal, una oficina,
        proyecto, obra o almacén.
      </p>

      <button
        class="empty-button"
        type="button"
        @click="openCreateModal"
      >
        Crear primera sucursal
      </button>
    </div>

    <div
      v-else
      class="table-container"
    >
      <table>
        <thead>
          <tr>
            <th>Sucursal</th>
            <th>Ubicación</th>
            <th>Contacto</th>
            <th>Responsable</th>
            <th>Funciones</th>
            <th>Estado</th>
            <th class="actions-column">
              Acciones
            </th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="branch in branches"
            :key="branch.id"
            :class="{
              'archived-row':
                branch.is_archived,
            }"
          >
            <td>
              <div class="main-information">
                <strong>
                  {{ branch.name }}
                </strong>

                <span>
                  {{
                    getBranchTypeName(
                      branch.branch_type
                    )
                  }}
                </span>

                <small v-if="branch.code">
                  Código: {{ branch.code }}
                </small>
              </div>
            </td>

            <td>
              <div class="main-information location-cell">
                <strong>
                  {{ getLocation(branch) }}
                </strong>

                <span>
                  {{
                    branch.address ||
                    "Sin dirección"
                  }}
                </span>
              </div>
            </td>

            <td>
              <div class="main-information">
                <strong>
                  {{
                    branch.general_email ||
                    "Sin correo"
                  }}
                </strong>

                <span>
                  {{
                    branch.general_phone ||
                    branch.mobile_phone ||
                    "Sin teléfono"
                  }}
                </span>
              </div>
            </td>

            <td>
              {{ getAdvisorName(branch) }}
            </td>

            <td>
              <div class="badges-container">
                <span
                  v-if="branch.is_main"
                  class="function-badge main"
                >
                  Principal
                </span>

                <span
                  v-if="branch.is_fiscal"
                  class="function-badge fiscal"
                >
                  Fiscal
                </span>

                <span
                  v-if="
                    branch.allows_equipment_installation
                  "
                  class="function-badge"
                >
                  Instalaciones
                </span>

                <span
                  v-if="branch.allows_deliveries"
                  class="function-badge"
                >
                  Entregas
                </span>
              </div>
            </td>

            <td>
              <span
                class="status-badge"
                :class="getStatusClass(branch)"
              >
                {{ getStatusName(branch) }}
              </span>
            </td>

            <td>
              <div class="row-actions">
                <button
                  class="action-button edit"
                  type="button"
                  :disabled="
                    branch.is_archived ||
                    processingId === branch.id
                  "
                  @click="openEditModal(branch)"
                >
                  Editar
                </button>

                <button
                  v-if="!branch.is_archived"
                  class="action-button archive"
                  type="button"
                  :disabled="
                    processingId === branch.id
                  "
                  @click="handleArchive(branch)"
                >
                  Archivar
                </button>

                <button
                  v-else
                  class="action-button restore"
                  type="button"
                  :disabled="
                    processingId === branch.id
                  "
                  @click="handleRestore(branch)"
                >
                  Restaurar
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <Teleport to="body">
      <div
        v-if="modalOpen"
        class="modal-overlay"
        @click.self="closeModal"
      >
        <form
          class="modal-card"
          @submit.prevent="submitBranch"
        >
          <header class="modal-header">
            <div>
              <span class="section-kicker">
                Ubicación del cliente
              </span>

              <h3>{{ modalTitle }}</h3>

              <p>
                Registra la dirección y condiciones
                operativas de la sede.
              </p>
            </div>

            <button
              class="close-button"
              type="button"
              :disabled="saving"
              aria-label="Cerrar"
              @click="closeModal"
            >
              ×
            </button>
          </header>

          <div
            v-if="errorMessage"
            class="message error-message modal-message"
          >
            {{ errorMessage }}
          </div>

          <div class="modal-content">
            <section class="modal-section">
              <h4>Información principal</h4>

              <div class="form-grid">
                <label class="form-field required">
                  <span>Nombre de la sede</span>

                  <input
                    v-model="form.name"
                    type="text"
                    placeholder="Ejemplo: Proyecto Ica"
                    required
                  />
                </label>

                <label class="form-field">
                  <span>Código interno</span>

                  <input
                    v-model="form.code"
                    type="text"
                    maxlength="30"
                    placeholder="Código opcional"
                  />
                </label>

                <label class="form-field required">
                  <span>Tipo de sede</span>

                  <select
                    v-model="form.branch_type"
                    required
                  >
                    <option
                      v-for="option in branchTypeOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </label>

                <label class="form-field">
                  <span>Responsable de la sede</span>

                  <select v-model="form.advisor">
                    <option value="">
                      Usar responsable principal
                    </option>

                    <option
                      v-for="user in users"
                      :key="user.id"
                      :value="user.id"
                    >
                      {{ getUserName(user) }}
                    </option>
                  </select>
                </label>
              </div>

              <div class="options-grid">
                <label class="option-card">
                  <input
                    v-model="form.is_main"
                    type="checkbox"
                  />

                  <div>
                    <strong>Sede principal</strong>

                    <span>
                      Solo puede existir una sede
                      principal activa.
                    </span>
                  </div>
                </label>

                <label class="option-card">
                  <input
                    v-model="form.is_fiscal"
                    type="checkbox"
                  />

                  <div>
                    <strong>Dirección fiscal</strong>

                    <span>
                      Solo puede existir una dirección
                      fiscal activa.
                    </span>
                  </div>
                </label>

                <label class="option-card">
                  <input
                    v-model="
                      form.allows_equipment_installation
                    "
                    type="checkbox"
                  />

                  <div>
                    <strong>
                      Permite instalaciones
                    </strong>

                    <span>
                      Puede seleccionarse en contratos
                      e instalaciones.
                    </span>
                  </div>
                </label>

                <label class="option-card">
                  <input
                    v-model="form.allows_deliveries"
                    type="checkbox"
                  />

                  <div>
                    <strong>Permite entregas</strong>

                    <span>
                      Puede utilizarse para despachos
                      y entregas.
                    </span>
                  </div>
                </label>
              </div>
            </section>

            <section class="modal-section">
              <h4>Dirección</h4>

              <div class="form-grid">
                <label class="form-field required">
                  <span>Código de país</span>

                  <input
                    v-model="form.country_code"
                    type="text"
                    maxlength="2"
                    placeholder="PE"
                    required
                  />
                </label>

                <label class="form-field required">
                  <span>País</span>

                  <input
                    v-model="form.country_name"
                    type="text"
                    placeholder="Perú"
                    required
                  />
                </label>

                <label class="form-field required full-width">
                  <span>Dirección completa</span>

                  <textarea
                    v-model="form.address"
                    rows="3"
                    placeholder="Dirección completa de la sede"
                    required
                  ></textarea>
                </label>

                <label class="form-field full-width">
                  <span>Referencia</span>

                  <input
                    v-model="form.address_reference"
                    type="text"
                    placeholder="Referencia de ubicación"
                  />
                </label>

                <label class="form-field">
                  <span>Ubigeo</span>

                  <input
                    v-model="form.ubigeo"
                    type="text"
                    maxlength="10"
                    placeholder="Código de ubigeo"
                  />
                </label>

                <label class="form-field">
                  <span>Tipo de vía</span>

                  <input
                    v-model="form.road_type"
                    type="text"
                    placeholder="Avenida, calle, jirón"
                  />
                </label>

                <label class="form-field">
                  <span>Nombre de vía</span>

                  <input
                    v-model="form.road_name"
                    type="text"
                    placeholder="Nombre de la vía"
                  />
                </label>

                <label class="form-field">
                  <span>Número</span>

                  <input
                    v-model="form.address_number"
                    type="text"
                    placeholder="Número"
                  />
                </label>

                <label class="form-field">
                  <span>Interior</span>

                  <input
                    v-model="form.interior"
                    type="text"
                    placeholder="Interior"
                  />
                </label>

                <label class="form-field">
                  <span>Lote</span>

                  <input
                    v-model="form.lot"
                    type="text"
                    placeholder="Lote"
                  />
                </label>

                <label class="form-field">
                  <span>Departamento</span>

                  <input
                    v-model="form.apartment"
                    type="text"
                    placeholder="Departamento"
                  />
                </label>

                <label class="form-field">
                  <span>Manzana</span>

                  <input
                    v-model="form.block"
                    type="text"
                    placeholder="Manzana"
                  />
                </label>

                <label class="form-field">
                  <span>Kilómetro</span>

                  <input
                    v-model="form.kilometer"
                    type="text"
                    placeholder="Kilómetro"
                  />
                </label>

                <label class="form-field">
                  <span>Tipo de zona</span>

                  <input
                    v-model="form.zone_type"
                    type="text"
                    placeholder="Urbanización, sector"
                  />
                </label>

                <label class="form-field">
                  <span>Código de zona</span>

                  <input
                    v-model="form.zone_code"
                    type="text"
                    placeholder="Código o nombre"
                  />
                </label>

                <label class="form-field">
                  <span>Distrito o ciudad</span>

                  <input
                    v-model="form.district"
                    type="text"
                    placeholder="Distrito o ciudad"
                  />
                </label>

                <label class="form-field">
                  <span>Provincia o condado</span>

                  <input
                    v-model="form.province"
                    type="text"
                    placeholder="Provincia"
                  />
                </label>

                <label class="form-field">
                  <span>Región o estado</span>

                  <input
                    v-model="form.region"
                    type="text"
                    placeholder="Región"
                  />
                </label>

                <label class="form-field">
                  <span>Código postal</span>

                  <input
                    v-model="form.postal_code"
                    type="text"
                    placeholder="Código postal"
                  />
                </label>
              </div>
            </section>

            <section class="modal-section">
              <h4>Contacto y acceso</h4>

              <div class="form-grid">
                <label class="form-field">
                  <span>Teléfono</span>

                  <input
                    v-model="form.general_phone"
                    type="tel"
                    placeholder="Teléfono de la sede"
                  />
                </label>

                <label class="form-field">
                  <span>Celular</span>

                  <input
                    v-model="form.mobile_phone"
                    type="tel"
                    placeholder="Celular de la sede"
                  />
                </label>

                <label class="form-field">
                  <span>Correo</span>

                  <input
                    v-model="form.general_email"
                    type="email"
                    placeholder="sede@empresa.com"
                  />
                </label>

                <label class="form-field">
                  <span>Horario de atención</span>

                  <input
                    v-model="form.operating_hours"
                    type="text"
                    placeholder="Lunes a viernes de 08:00 a 17:00"
                  />
                </label>

                <label class="form-field full-width">
                  <span>Indicaciones de acceso</span>

                  <textarea
                    v-model="form.access_instructions"
                    rows="3"
                    placeholder="Requisitos de ingreso o personas que autorizan"
                  ></textarea>
                </label>

                <label class="form-field full-width">
                  <span>
                    Observaciones para instalaciones
                  </span>

                  <textarea
                    v-model="form.installation_notes"
                    rows="3"
                    placeholder="Información para instalar o retirar equipos"
                  ></textarea>
                </label>
              </div>
            </section>

            <section class="modal-section">
              <h4>
                Proyecto, coordenadas y estado
              </h4>

              <div class="form-grid">
                <label class="form-field">
                  <span>Fecha de inicio</span>

                  <input
                    v-model="form.start_date"
                    type="date"
                  />
                </label>

                <label class="form-field">
                  <span>Fecha de finalización</span>

                  <input
                    v-model="form.end_date"
                    type="date"
                  />
                </label>

                <label class="form-field">
                  <span>Latitud</span>

                  <input
                    v-model="form.latitude"
                    type="number"
                    min="-90"
                    max="90"
                    step="0.0000001"
                    placeholder="-12.046374"
                  />
                </label>

                <label class="form-field">
                  <span>Longitud</span>

                  <input
                    v-model="form.longitude"
                    type="number"
                    min="-180"
                    max="180"
                    step="0.0000001"
                    placeholder="-77.042793"
                  />
                </label>

                <label class="form-field full-width">
                  <span>Observaciones</span>

                  <textarea
                    v-model="form.notes"
                    rows="3"
                    placeholder="Observaciones de la sede"
                  ></textarea>
                </label>
              </div>

              <div class="options-grid single-option">
                <label class="option-card">
                  <input
                    v-model="form.is_active"
                    type="checkbox"
                  />

                  <div>
                    <strong>Sucursal activa</strong>

                    <span>
                      Puede utilizarse en contratos,
                      instalaciones y servicios.
                    </span>
                  </div>
                </label>
              </div>
            </section>
          </div>

          <footer class="modal-actions">
            <button
              class="secondary-button"
              type="button"
              :disabled="saving"
              @click="closeModal"
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
                  : editingBranchId
                    ? "Guardar cambios"
                    : "Crear sucursal"
              }}
            </button>
          </footer>
        </form>
      </div>
    </Teleport>
  </section>
</template>

<style scoped>
button,
input,
select,
textarea {
  font: inherit;
}

.management-section {
  overflow: hidden;
  border: 1px solid #dfe3ec;
  border-radius: 15px;
  background: white;
}

.management-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 19px 20px;
  border-bottom: 1px solid #e8ebf1;
  background: #f8f9fd;
}

.section-kicker {
  display: block;
  margin-bottom: 5px;
  color: #1f35c4;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.management-header h3,
.modal-header h3 {
  margin: 0;
  color: #1d2940;
  font-size: 17px;
}

.management-header p,
.modal-header p {
  margin: 5px 0 0;
  color: #8693a4;
  font-size: 12px;
}

.primary-button,
.secondary-button {
  min-height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 0 16px;
  border-radius: 10px;
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
  box-shadow: 0 9px 20px rgba(31, 53, 196, 0.18);
}

.secondary-button {
  border: 1px solid #dfe3ec;
  background: white;
  color: #667382;
}

.summary-grid {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  gap: 12px;
  padding: 16px 20px 0;
}

.summary-card {
  padding: 14px 15px;
  border: 1px solid #e4e8ef;
  border-radius: 11px;
  background: #fafbfe;
}

.summary-card small,
.summary-card strong {
  display: block;
}

.summary-card small {
  color: #8793a1;
  font-size: 11px;
}

.summary-card strong {
  margin-top: 4px;
  color: #1d2940;
  font-size: 21px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 11px;
  padding: 14px 20px;
}

.archive-filter {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #667382;
  font-size: 12px;
}

.archive-filter input {
  width: 16px;
  height: 16px;
  accent-color: #1f35c4;
}

.refresh-button {
  min-height: 37px;
  padding: 0 12px;
  border: 1px solid #dfe3ec;
  border-radius: 9px;
  background: white;
  color: #667382;
  cursor: pointer;
}

.message {
  margin: 0 20px 15px;
  padding: 11px 13px;
  border-radius: 9px;
  font-size: 12px;
}

.success-message {
  border: 1px solid #c8ead4;
  background: #edf9f1;
  color: #287344;
}

.error-message {
  border: 1px solid #e8caca;
  background: #fff3f3;
  color: #9a4141;
}

.loading-state,
.empty-state {
  min-height: 210px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7b8797;
}

.loading-state {
  gap: 9px;
}

.spinner,
.button-spinner {
  display: inline-block;
  border-radius: 50%;
  animation: rotate 0.8s linear infinite;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #d9deea;
  border-top-color: #1f35c4;
}

.button-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.45);
  border-top-color: white;
}

.empty-state {
  flex-direction: column;
  padding: 34px 20px;
  text-align: center;
}

.empty-state > span {
  color: #9ba5b3;
  font-size: 38px;
}

.empty-state strong {
  margin-top: 9px;
  color: #34445a;
}

.empty-state p {
  margin: 6px 0 14px;
  font-size: 12px;
}

.empty-button {
  min-height: 38px;
  padding: 0 14px;
  border: 0;
  border-radius: 9px;
  background: #1f35c4;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.table-container {
  overflow-x: auto;
  border-top: 1px solid #edf0f4;
}

table {
  width: 100%;
  min-width: 1100px;
  border-collapse: collapse;
}

th,
td {
  padding: 13px 15px;
  border-bottom: 1px solid #edf0f4;
  text-align: left;
  vertical-align: middle;
}

th {
  background: #fafbfd;
  color: #7b8797;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

td {
  color: #4d5d70;
  font-size: 12px;
}

.archived-row {
  opacity: 0.7;
}

.main-information strong,
.main-information span,
.main-information small {
  display: block;
}

.main-information strong {
  color: #2d3c50;
  font-size: 12px;
}

.main-information span,
.main-information small {
  margin-top: 3px;
  color: #8792a0;
  font-size: 10px;
}

.location-cell {
  max-width: 280px;
}

.location-cell span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.badges-container {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.function-badge,
.status-badge {
  display: inline-flex;
  padding: 5px 7px;
  border-radius: 999px;
  font-size: 9px;
  font-weight: 700;
}

.function-badge {
  background: #eef1f5;
  color: #647184;
}

.function-badge.main {
  background: #edf0ff;
  color: #1f35c4;
}

.function-badge.fiscal {
  background: #eaf7ef;
  color: #287d4d;
}

.status-badge.active {
  background: #e7f6ed;
  color: #277d4c;
}

.status-badge.inactive {
  background: #fff0e8;
  color: #b45e32;
}

.status-badge.archived {
  background: #eceff3;
  color: #657181;
}

.actions-column {
  text-align: right;
}

.row-actions {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}

.action-button {
  padding: 6px 8px;
  border: 1px solid #dce4ea;
  border-radius: 7px;
  background: white;
  font-size: 10px;
  cursor: pointer;
}

.action-button.edit {
  color: #1f35c4;
}

.action-button.archive {
  color: #ad5c3b;
}

.action-button.restore {
  color: #2b8050;
}

.action-button:disabled {
  opacity: 0.45;
  cursor: wait;
}

.modal-overlay {
  position: fixed;
  z-index: 1000;
  inset: 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  overflow-y: auto;
  padding: 35px 18px;
  background: rgba(21, 31, 48, 0.58);
  backdrop-filter: blur(4px);
}

.modal-card {
  width: min(100%, 980px);
  overflow: hidden;
  border: 1px solid #dfe3ec;
  border-radius: 17px;
  background: white;
  box-shadow:
    0 28px 70px rgba(14, 25, 43, 0.28);
  animation: modalReveal 0.24s ease-out;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 19px 21px;
  border-bottom: 1px solid #e8ebf1;
  background: #f8f9fd;
}

.close-button {
  width: 37px;
  height: 37px;
  flex-shrink: 0;
  border: 1px solid #dfe3ec;
  border-radius: 10px;
  background: white;
  color: #687586;
  font-size: 22px;
  cursor: pointer;
}

.modal-message {
  margin-top: 16px;
}

.modal-content {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  padding: 18px;
  background: #f5f7fb;
}

.modal-section {
  overflow: hidden;
  margin-bottom: 15px;
  border: 1px solid #e0e5ed;
  border-radius: 13px;
  background: white;
}

.modal-section:last-child {
  margin-bottom: 0;
}

.modal-section h4 {
  margin: 0;
  padding: 14px 17px;
  border-bottom: 1px solid #e8ebf1;
  background: #fafbfe;
  color: #26364c;
  font-size: 13px;
}

.form-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 15px;
  padding: 17px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field.full-width {
  grid-column: 1 / -1;
}

.form-field > span {
  color: #667382;
  font-size: 11px;
  font-weight: 700;
}

.form-field.required > span::after {
  content: " *";
  color: #4e63d8;
}

.form-field input,
.form-field select,
.form-field textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #dfe3ec;
  border-radius: 9px;
  outline: none;
  background: white;
  color: #1d2940;
}

.form-field input,
.form-field select {
  min-height: 41px;
  padding: 0 11px;
}

.form-field textarea {
  resize: vertical;
  padding: 10px 11px;
  line-height: 1.45;
}

.form-field input:focus,
.form-field select:focus,
.form-field textarea:focus {
  border-color: #4e63d8;
  box-shadow:
    0 0 0 3px rgba(31, 53, 196, 0.11);
}

.options-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 11px;
  padding: 0 17px 17px;
}

.single-option {
  grid-template-columns: 1fr;
}

.option-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 13px;
  border: 1px solid #dfe3ec;
  border-radius: 10px;
  background: #f8f9fd;
  cursor: pointer;
}

.option-card:has(input:checked) {
  border-color: #bfc7f4;
  background: #edf0ff;
  box-shadow: inset 3px 0 0 #1f35c4;
}

.option-card input {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  margin-top: 2px;
  accent-color: #1f35c4;
}

.option-card strong,
.option-card span {
  display: block;
}

.option-card strong {
  color: #1d2940;
  font-size: 12px;
}

.option-card span {
  margin-top: 3px;
  color: #8693a4;
  font-size: 10px;
  line-height: 1.4;
}

.modal-actions {
  position: sticky;
  bottom: 0;
  display: flex;
  justify-content: flex-end;
  gap: 9px;
  padding: 15px 20px;
  border-top: 1px solid #e8ebf1;
  background: white;
}

.primary-button:disabled,
.secondary-button:disabled {
  opacity: 0.6;
  cursor: wait;
}

@keyframes rotate {
  to {
    transform: rotate(360deg);
  }
}

@keyframes modalReveal {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.985);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (max-width: 760px) {
  .management-header {
    flex-direction: column;
  }

  .management-header .primary-button {
    width: 100%;
  }

  .summary-grid,
  .form-grid,
  .options-grid {
    grid-template-columns: 1fr;
  }

  .form-field.full-width {
    grid-column: auto;
  }

  .toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .modal-overlay {
    padding: 10px;
  }

  .modal-content {
    max-height: calc(100vh - 180px);
    padding: 10px;
  }
}

@media (max-width: 520px) {
  .modal-actions {
    flex-direction: column-reverse;
  }

  .modal-actions button {
    width: 100%;
  }
}
</style>