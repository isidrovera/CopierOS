<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
} from "vue"

import {
  useRouter,
} from "vue-router"

import {
  archivePartner,
  getPartners,
  restorePartner,
} from "../../services/partners.service"


const router = useRouter()

const partners = ref([])
const loading = ref(false)
const processingId = ref("")
const errorMessage = ref("")
const successMessage = ref("")

const search = ref("")
const includeArchived = ref(false)
const selectedStatus = ref("")
const selectedRole = ref("")
const selectedPersonType = ref("")
const selectedCountry = ref("")

let searchTimeout = null


const totalPartners = computed(() => {
  return partners.value.length
})


const activePartners = computed(() => {
  return partners.value.filter(
    (partner) => (
      partner.is_active &&
      !partner.is_archived
    )
  ).length
})


const archivedPartners = computed(() => {
  return partners.value.filter(
    (partner) => partner.is_archived
  ).length
})


const customersCount = computed(() => {
  return partners.value.filter(
    (partner) => (
      partner.is_rental_customer ||
      partner.is_sales_customer ||
      partner.is_service_customer
    )
  ).length
})


const suppliersCount = computed(() => {
  return partners.value.filter(
    (partner) => partner.is_supplier
  ).length
})


async function loadPartners() {
  loading.value = true
  errorMessage.value = ""

  try {
    const isActive =
      selectedStatus.value === "active"
        ? true
        : selectedStatus.value === "inactive"
          ? false
          : ""

    const response = await getPartners({
      search: search.value,
      includeArchived:
        includeArchived.value,
      isActive,
      role: selectedRole.value,
      personType:
        selectedPersonType.value,
      countryCode:
        selectedCountry.value,
    })

    partners.value = Array.isArray(response)
      ? response
      : response?.results || []
  } catch (error) {
    partners.value = []

    errorMessage.value =
      error.message ||
      "No se pudieron cargar los registros."
  } finally {
    loading.value = false
  }
}


function handleSearch() {
  window.clearTimeout(searchTimeout)

  searchTimeout = window.setTimeout(() => {
    loadPartners()
  }, 350)
}


function clearMessages() {
  errorMessage.value = ""
  successMessage.value = ""
}


function clearFilters() {
  search.value = ""
  selectedStatus.value = ""
  selectedRole.value = ""
  selectedPersonType.value = ""
  selectedCountry.value = ""
  includeArchived.value = false

  loadPartners()
}


async function goToCreate() {
  await router.push({
    name: "partner-create",
  })
}


async function goToEdit(partner) {
  await router.push({
    name: "partner-edit",
    params: {
      id: partner.id,
    },
  })
}


async function handleArchive(partner) {
  const partnerName =
    getPartnerName(partner)

  const reason = window.prompt(
    `Indica el motivo para archivar a ${partnerName}:`
  )

  if (reason === null) {
    return
  }

  const confirmed = window.confirm(
    `¿Confirmas que deseas archivar a ${partnerName}?`
  )

  if (!confirmed) {
    return
  }

  clearMessages()
  processingId.value = partner.id

  try {
    await archivePartner(
      partner.id,
      reason.trim()
    )

    successMessage.value =
      "Registro archivado correctamente."

    await loadPartners()
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo archivar el registro."
  } finally {
    processingId.value = ""
  }
}


async function handleRestore(partner) {
  const partnerName =
    getPartnerName(partner)

  const confirmed = window.confirm(
    `¿Confirmas que deseas restaurar a ${partnerName}?`
  )

  if (!confirmed) {
    return
  }

  clearMessages()
  processingId.value = partner.id

  try {
    await restorePartner(partner.id)

    successMessage.value =
      "Registro restaurado correctamente."

    await loadPartners()
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo restaurar el registro."
  } finally {
    processingId.value = ""
  }
}


function getPartnerName(partner) {
  return (
    partner.display_name ||
    partner.trade_name ||
    partner.legal_name ||
    [
      partner.first_names,
      partner.paternal_last_name,
      partner.maternal_last_name,
    ]
      .filter(Boolean)
      .join(" ")
      .trim() ||
    partner.document_number ||
    "Registro sin nombre"
  )
}


function getInitials(partner) {
  const name = getPartnerName(partner)

  const words = name
    .split(" ")
    .filter(Boolean)

  if (!words.length) {
    return "C"
  }

  if (words.length === 1) {
    return words[0]
      .charAt(0)
      .toUpperCase()
  }

  return (
    words[0].charAt(0) +
    words[1].charAt(0)
  ).toUpperCase()
}


function getDocumentLabel(partner) {
  const documentType =
    partner.document_type_name ||
    getDocumentTypeName(
      partner.document_type
    )

  const documentNumber =
    partner.document_number ||
    "Sin documento"

  return `${documentType}: ${documentNumber}`
}


function getDocumentTypeName(value) {
  const names = {
    dni: "DNI",
    ruc: "RUC",
    foreign_id: "Documento extranjero",
    ein: "EIN",
    tax_id: "Tax ID",
    registration: "Registro empresarial",
    passport: "Pasaporte",
    other: "Otro",
  }

  return names[value] || "Documento"
}


function getPersonTypeName(partner) {
  if (partner.person_type_name) {
    return partner.person_type_name
  }

  if (partner.person_type === "natural") {
    return "Persona natural"
  }

  if (partner.person_type === "legal") {
    return "Persona jurídica"
  }

  return "Sin clasificación"
}


function getCountryName(partner) {
  if (partner.country_name) {
    return partner.country_name
  }

  const countries = {
    PE: "Perú",
    US: "Estados Unidos",
  }

  return (
    countries[partner.country_code] ||
    partner.country_code ||
    "Sin país"
  )
}


function getRoles(partner) {
  if (
    Array.isArray(
      partner.commercial_roles
    ) &&
    partner.commercial_roles.length
  ) {
    return partner.commercial_roles
  }

  const roles = []

  if (partner.is_rental_customer) {
    roles.push("Cliente de alquiler")
  }

  if (partner.is_sales_customer) {
    roles.push("Cliente de ventas")
  }

  if (partner.is_service_customer) {
    roles.push("Cliente de servicios")
  }

  if (partner.is_supplier) {
    roles.push("Proveedor")
  }

  if (partner.is_distributor) {
    roles.push("Distribuidor")
  }

  return roles
}


function getRoleClass(role) {
  const normalized = String(role)
    .trim()
    .toLowerCase()

  if (normalized.includes("alquiler")) {
    return "rental"
  }

  if (normalized.includes("venta")) {
    return "sales"
  }

  if (normalized.includes("servicio")) {
    return "service"
  }

  if (normalized.includes("proveedor")) {
    return "supplier"
  }

  if (normalized.includes("distribuidor")) {
    return "distributor"
  }

  return "default"
}


function getPrimaryContact(partner) {
  return (
    partner.general_email ||
    partner.billing_email ||
    partner.general_phone ||
    partner.mobile_phone ||
    "Sin contacto"
  )
}


function getAdvisorName(partner) {
  return (
    partner.advisor_name ||
    partner.purchasing_manager_name ||
    "Sin responsable"
  )
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
    }
  ).format(date)
}


onMounted(() => {
  loadPartners()
})


onBeforeUnmount(() => {
  window.clearTimeout(searchTimeout)
})
</script>

<template>
  <section class="partners-page">
    <header class="page-header">
      <div>
        <span class="page-kicker">
          Gestión comercial
        </span>

        <h2>
          Clientes y proveedores
        </h2>

        <p>
          Administra clientes, proveedores,
          distribuidores, sus contactos y sedes.
        </p>
      </div>

      <button
        class="primary-button"
        type="button"
        @click="goToCreate"
      >
        <span>＋</span>
        Nuevo registro
      </button>
    </header>

    <div class="summary-grid">
      <article class="summary-card">
        <span class="summary-icon">
          ◉
        </span>

        <div>
          <small>Total mostrados</small>
          <strong>
            {{ totalPartners }}
          </strong>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon success">
          ✓
        </span>

        <div>
          <small>Activos</small>
          <strong>
            {{ activePartners }}
          </strong>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon customers">
          C
        </span>

        <div>
          <small>Clientes</small>
          <strong>
            {{ customersCount }}
          </strong>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon suppliers">
          P
        </span>

        <div>
          <small>Proveedores</small>
          <strong>
            {{ suppliersCount }}
          </strong>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon archived">
          ▣
        </span>

        <div>
          <small>Archivados</small>
          <strong>
            {{ archivedPartners }}
          </strong>
        </div>
      </article>
    </div>

    <div class="partners-panel">
      <div class="filters">
        <label class="search-field">
          <span>⌕</span>

          <input
            v-model="search"
            type="search"
            placeholder="Buscar por nombre, RUC, DNI, correo, teléfono o contacto"
            @input="handleSearch"
          />
        </label>

        <select
          v-model="selectedRole"
          class="filter-select"
          @change="loadPartners"
        >
          <option value="">
            Todos los tipos
          </option>

          <option value="rental_customer">
            Cliente de alquiler
          </option>

          <option value="sales_customer">
            Cliente de ventas
          </option>

          <option value="service_customer">
            Cliente de servicios
          </option>

          <option value="supplier">
            Proveedor
          </option>

          <option value="distributor">
            Distribuidor
          </option>
        </select>

        <select
          v-model="selectedStatus"
          class="filter-select"
          @change="loadPartners"
        >
          <option value="">
            Todos los estados
          </option>

          <option value="active">
            Activos
          </option>

          <option value="inactive">
            Inactivos
          </option>
        </select>

        <select
          v-model="selectedPersonType"
          class="filter-select"
          @change="loadPartners"
        >
          <option value="">
            Todas las personas
          </option>

          <option value="legal">
            Persona jurídica
          </option>

          <option value="natural">
            Persona natural
          </option>
        </select>

        <select
          v-model="selectedCountry"
          class="filter-select country-filter"
          @change="loadPartners"
        >
          <option value="">
            Todos los países
          </option>

          <option value="PE">
            Perú
          </option>

          <option value="US">
            Estados Unidos
          </option>
        </select>

        <label class="archive-filter">
          <input
            v-model="includeArchived"
            type="checkbox"
            @change="loadPartners"
          />

          <span>
            Mostrar archivados
          </span>
        </label>

        <button
          class="refresh-button"
          type="button"
          :disabled="loading"
          @click="loadPartners"
        >
          ↻
          Actualizar
        </button>

        <button
          class="clear-button"
          type="button"
          :disabled="loading"
          @click="clearFilters"
        >
          Limpiar
        </button>
      </div>

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
        class="loading-state"
      >
        <span class="spinner"></span>

        Cargando clientes y proveedores...
      </div>

      <div
        v-else-if="!partners.length"
        class="empty-state"
      >
        <span>◎</span>

        <strong>
          No se encontraron registros
        </strong>

        <p>
          Cambia los filtros o registra un
          nuevo cliente, proveedor o distribuidor.
        </p>

        <button
          class="empty-create-button"
          type="button"
          @click="goToCreate"
        >
          Crear registro
        </button>
      </div>

      <div
        v-else
        class="table-container"
      >
        <table>
          <thead>
            <tr>
              <th>
                Cliente / proveedor
              </th>

              <th>
                Documento
              </th>

              <th>
                Tipos
              </th>

              <th>
                Contacto
              </th>

              <th>
                Responsable
              </th>

              <th>
                Estado
              </th>

              <th>
                Actualizado
              </th>

              <th class="actions-column">
                Acciones
              </th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="partner in partners"
              :key="partner.id"
              :class="{
                'archived-row':
                  partner.is_archived,
                'blocked-row':
                  partner.is_commercially_blocked,
              }"
            >
              <td>
                <div class="partner-cell">
                  <span class="partner-avatar">
                    {{ getInitials(partner) }}
                  </span>

                  <div class="partner-information">
                    <strong>
                      {{ getPartnerName(partner) }}
                    </strong>

                    <span>
                      {{
                        getPersonTypeName(
                          partner
                        )
                      }}
                      ·
                      {{
                        getCountryName(
                          partner
                        )
                      }}
                    </span>

                    <small
                      v-if="
                        partner.trade_name &&
                        partner.trade_name !==
                          getPartnerName(partner)
                      "
                    >
                      {{
                        partner.trade_name
                      }}
                    </small>
                  </div>
                </div>
              </td>

              <td>
                <div class="document-information">
                  <strong>
                    {{
                      partner.document_number ||
                      "Sin documento"
                    }}
                  </strong>

                  <span>
                    {{
                      partner.document_type_name ||
                      getDocumentTypeName(
                        partner.document_type
                      )
                    }}
                  </span>

                  <small
                    v-if="partner.document_verified"
                    class="verified-document"
                  >
                    ✓ Verificado
                  </small>
                </div>
              </td>

              <td>
                <div class="roles-container">
                  <span
                    v-for="role in getRoles(partner)"
                    :key="role"
                    class="role-badge"
                    :class="getRoleClass(role)"
                  >
                    {{ role }}
                  </span>

                  <span
                    v-if="!getRoles(partner).length"
                    class="role-badge default"
                  >
                    Sin tipo
                  </span>
                </div>
              </td>

              <td>
                <div class="contact-information">
                  <strong>
                    {{
                      getPrimaryContact(
                        partner
                      )
                    }}
                  </strong>

                  <span>
                    {{
                      partner.branches_count || 0
                    }}
                    sede{{
                      partner.branches_count === 1
                        ? ""
                        : "s"
                    }}
                    ·
                    {{
                      partner.contacts_count || 0
                    }}
                    contacto{{
                      partner.contacts_count === 1
                        ? ""
                        : "s"
                    }}
                  </span>
                </div>
              </td>

              <td>
                <div class="responsible-information">
                  <strong>
                    {{
                      getAdvisorName(
                        partner
                      )
                    }}
                  </strong>

                  <span
                    v-if="partner.advisor_name"
                  >
                    Responsable comercial
                  </span>

                  <span
                    v-else-if="
                      partner.purchasing_manager_name
                    "
                  >
                    Responsable de compras
                  </span>

                  <span v-else>
                    No asignado
                  </span>
                </div>
              </td>

              <td>
                <div class="status-container">
                  <span
                    v-if="partner.is_archived"
                    class="status-badge archived"
                  >
                    Archivado
                  </span>

                  <span
                    v-else-if="partner.is_active"
                    class="status-badge active"
                  >
                    Activo
                  </span>

                  <span
                    v-else
                    class="status-badge inactive"
                  >
                    Inactivo
                  </span>

                  <span
                    v-if="
                      partner.is_commercially_blocked
                    "
                    class="blocked-badge"
                  >
                    Bloqueado
                  </span>

                  <span
                    v-if="
                      partner.sunat_status ||
                      partner.sunat_condition
                    "
                    class="sunat-badge"
                  >
                    {{
                      partner.sunat_status ||
                      partner.sunat_condition
                    }}
                  </span>
                </div>
              </td>

              <td>
                {{
                  formatDate(
                    partner.updated_at
                  )
                }}
              </td>

              <td>
                <div class="row-actions">
                  <button
                    class="action-button edit"
                    type="button"
                    :disabled="
                      partner.is_archived ||
                      processingId === partner.id
                    "
                    @click="goToEdit(partner)"
                  >
                    Editar
                  </button>

                  <button
                    v-if="!partner.is_archived"
                    class="action-button archive"
                    type="button"
                    :disabled="
                      processingId === partner.id
                    "
                    @click="
                      handleArchive(partner)
                    "
                  >
                    {{
                      processingId === partner.id
                        ? "Procesando..."
                        : "Archivar"
                    }}
                  </button>

                  <button
                    v-else
                    class="action-button restore"
                    type="button"
                    :disabled="
                      processingId === partner.id
                    "
                    @click="
                      handleRestore(partner)
                    "
                  >
                    {{
                      processingId === partner.id
                        ? "Procesando..."
                        : "Restaurar"
                    }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<style scoped>
button,
input,
select {
  font: inherit;
}

.partners-page {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.page-kicker {
  display: block;
  margin-bottom: 6px;
  color: #2c82a8;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.page-header h2 {
  margin: 0;
  color: #17283f;
  font-size: 28px;
}

.page-header p {
  margin: 8px 0 0;
  color: #768396;
  font-size: 14px;
}

.primary-button {
  min-height: 43px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 10px 17px;
  border: 0;
  border-radius: 10px;
  background: #277fa6;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.primary-button:hover {
  background: #216f91;
}

.summary-grid {
  display: grid;
  grid-template-columns:
    repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.summary-card {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 17px;
  border: 1px solid #e3e9ef;
  border-radius: 14px;
  background: white;
}

.summary-icon {
  width: 43px;
  height: 43px;
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: #e9f4f8;
  color: #277fa6;
  font-size: 18px;
  font-weight: 800;
}

.summary-icon.success {
  background: #eaf7ef;
  color: #288653;
}

.summary-icon.customers {
  background: #e9f1fb;
  color: #396da8;
}

.summary-icon.suppliers {
  background: #f3effb;
  color: #6b55a5;
}

.summary-icon.archived {
  background: #f0f2f5;
  color: #687586;
}

.summary-card small,
.summary-card strong {
  display: block;
}

.summary-card small {
  overflow: hidden;
  margin-bottom: 4px;
  color: #8793a1;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.summary-card strong {
  color: #1b2c42;
  font-size: 23px;
}

.partners-panel {
  overflow: hidden;
  border: 1px solid #e2e8ee;
  border-radius: 15px;
  background: white;
}

.filters {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding: 17px;
  border-bottom: 1px solid #edf1f4;
}

.search-field {
  min-width: 280px;
  min-height: 42px;
  display: flex;
  flex: 1 1 360px;
  align-items: center;
  gap: 8px;
  padding: 0 13px;
  border: 1px solid #dce4eb;
  border-radius: 10px;
  background: #fbfcfd;
}

.search-field span {
  color: #8a96a4;
  font-size: 19px;
}

.search-field input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: #25364b;
}

.search-field input::placeholder {
  color: #9aa5b0;
}

.filter-select {
  min-height: 42px;
  padding: 0 11px;
  border: 1px solid #dce4eb;
  border-radius: 10px;
  outline: none;
  background: white;
  color: #526174;
}

.country-filter {
  max-width: 170px;
}

.archive-filter {
  min-height: 42px;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #647286;
  font-size: 13px;
  white-space: nowrap;
}

.archive-filter input {
  width: 16px;
  height: 16px;
  accent-color: #277fa6;
}

.refresh-button,
.clear-button {
  min-height: 42px;
  padding: 0 13px;
  border: 1px solid #dce4eb;
  border-radius: 10px;
  background: white;
  color: #42708a;
  cursor: pointer;
}

.refresh-button:hover,
.clear-button:hover {
  background: #f3f7f9;
}

.clear-button {
  color: #697789;
}

.refresh-button:disabled,
.clear-button:disabled {
  opacity: 0.6;
  cursor: wait;
}

.message {
  margin: 16px 17px 0;
  padding: 11px 13px;
  border-radius: 9px;
  font-size: 13px;
}

.success-message {
  border: 1px solid #c8ead4;
  background: #edf9f1;
  color: #287344;
}

.error-message {
  border: 1px solid #f0cccc;
  background: #fff1f1;
  color: #a43f3f;
}

.loading-state,
.empty-state {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7a8796;
}

.loading-state {
  gap: 10px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #d9e5eb;
  border-top-color: #277fa6;
  border-radius: 50%;
  animation: rotate 0.8s linear infinite;
}

@keyframes rotate {
  to {
    transform: rotate(360deg);
  }
}

.empty-state {
  flex-direction: column;
  padding: 40px 20px;
  text-align: center;
}

.empty-state > span {
  margin-bottom: 12px;
  color: #9aa6b2;
  font-size: 42px;
}

.empty-state strong {
  color: #34445a;
  font-size: 16px;
}

.empty-state p {
  max-width: 480px;
  margin: 7px 0 16px;
  font-size: 13px;
  line-height: 1.6;
}

.empty-create-button {
  min-height: 39px;
  padding: 0 14px;
  border: 0;
  border-radius: 9px;
  background: #277fa6;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  min-width: 1320px;
  border-collapse: collapse;
}

th,
td {
  padding: 14px 15px;
  border-bottom: 1px solid #edf1f4;
  text-align: left;
  vertical-align: middle;
}

th {
  background: #fafbfd;
  color: #7b8797;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.05em;
  white-space: nowrap;
  text-transform: uppercase;
}

td {
  color: #4b5a6e;
  font-size: 13px;
}

tbody tr:hover {
  background: #fafcfd;
}

tbody tr:last-child td {
  border-bottom: 0;
}

.archived-row {
  opacity: 0.7;
}

.blocked-row:not(.archived-row) {
  background: #fffaf7;
}

.partner-cell {
  min-width: 250px;
  display: flex;
  align-items: center;
  gap: 11px;
}

.partner-avatar {
  width: 42px;
  height: 42px;
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: #e7f2f7;
  color: #257ca3;
  font-weight: 800;
}

.partner-information,
.document-information,
.contact-information,
.responsible-information {
  min-width: 0;
}

.partner-information strong,
.partner-information span,
.partner-information small,
.document-information strong,
.document-information span,
.contact-information strong,
.contact-information span,
.responsible-information strong,
.responsible-information span {
  display: block;
}

.partner-information strong,
.document-information strong,
.contact-information strong,
.responsible-information strong {
  color: #2d3c50;
  font-size: 13px;
}

.partner-information strong {
  max-width: 280px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.partner-information span,
.document-information span,
.contact-information span,
.responsible-information span {
  margin-top: 3px;
  color: #8792a0;
  font-size: 11px;
}

.partner-information small {
  max-width: 260px;
  overflow: hidden;
  margin-top: 3px;
  color: #6b7889;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.verified-document {
  display: inline-flex;
  margin-top: 5px;
  color: #29825c;
  font-size: 10px;
  font-weight: 700;
}

.roles-container {
  min-width: 170px;
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 5px;
}

.role-badge {
  display: inline-flex;
  padding: 5px 8px;
  border-radius: 999px;
  background: #eef1f5;
  color: #5c6979;
  font-size: 10px;
  font-weight: 700;
}

.role-badge.rental {
  background: #e7f3f8;
  color: #267b9f;
}

.role-badge.sales {
  background: #eaf0fb;
  color: #416ca1;
}

.role-badge.service {
  background: #eaf7ef;
  color: #2b7e50;
}

.role-badge.supplier {
  background: #f2edfa;
  color: #6b55a5;
}

.role-badge.distributor {
  background: #fff2e8;
  color: #a96031;
}

.status-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 5px;
}

.status-badge,
.blocked-badge,
.sunat-badge {
  display: inline-flex;
  padding: 5px 8px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
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

.blocked-badge {
  background: #fff0ed;
  color: #ae4f43;
}

.sunat-badge {
  max-width: 130px;
  overflow: hidden;
  background: #e9f1f8;
  color: #3f6c8c;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actions-column {
  text-align: right;
}

.row-actions {
  min-width: 140px;
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}

.action-button {
  padding: 7px 9px;
  border: 1px solid #dce4ea;
  border-radius: 8px;
  background: white;
  color: #4e6073;
  font-size: 11px;
  cursor: pointer;
}

.action-button:hover {
  background: #f3f7f9;
}

.action-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.action-button.edit {
  border-color: #c7dfeb;
  color: #277fa6;
}

.action-button.archive {
  border-color: #f0d2c6;
  color: #ad5c3b;
}

.action-button.restore {
  border-color: #c8e4d3;
  color: #2b8050;
}

@media (max-width: 1250px) {
  .summary-grid {
    grid-template-columns:
      repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .summary-grid {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }

  .filters {
    align-items: stretch;
    flex-direction: column;
  }

  .search-field {
    min-width: 0;
    flex-basis: auto;
  }

  .filter-select,
  .country-filter {
    width: 100%;
    max-width: none;
  }

  .archive-filter {
    min-height: 34px;
  }
}

@media (max-width: 620px) {
  .page-header {
    flex-direction: column;
  }

  .primary-button {
    width: 100%;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>