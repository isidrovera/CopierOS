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
  archiveEquipment,
  getEquipment,
  restoreEquipment,
} from "../../services/equipment.service"

import "./styles/equipment-list.css"


const router = useRouter()

const equipment = ref([])
const loading = ref(false)
const processingId = ref("")
const errorMessage = ref("")
const successMessage = ref("")

const search = ref("")
const includeArchived = ref(false)
const selectedTechnicalStatus = ref("")
const selectedCommercialStatus = ref("")
const selectedAvailability = ref("")
const selectedCondition = ref("")
const selectedOwnership = ref("")
const selectedColorMode = ref("")
const expandedRows = ref(new Set())
const showColumnMenu = ref(false)

const columnOptions = [
  { key: "equipment", label: "Equipo", locked: true },
  { key: "identifiers", label: "Serie / código" },
  { key: "condition", label: "Condición" },
  { key: "technical", label: "Estado técnico" },
  { key: "commercial", label: "Estado comercial" },
  { key: "location", label: "Cliente / ubicación" },
  { key: "meters", label: "Contadores" },
  { key: "availability", label: "Disponibilidad" },
  { key: "updated", label: "Actualizado" },
]

const defaultVisibleColumns = {
  equipment: true,
  identifiers: true,
  condition: false,
  technical: true,
  commercial: true,
  location: true,
  meters: true,
  availability: true,
  updated: false,
}

const visibleColumns = ref({ ...defaultVisibleColumns })

let searchTimeout = null


const visibleColumnCount = computed(() => {
  return Object.values(visibleColumns.value).filter(Boolean).length + 1
})

const activeFilterCount = computed(() => {
  return [
    search.value,
    selectedTechnicalStatus.value,
    selectedCommercialStatus.value,
    selectedAvailability.value,
    selectedCondition.value,
    selectedOwnership.value,
    selectedColorMode.value,
    includeArchived.value,
  ].filter(Boolean).length
})

const totalEquipment = computed(() => {
  return equipment.value.length
})


const availableEquipment = computed(() => {
  return equipment.value.filter(
    (item) => (
      item.is_available &&
      !item.is_archived
    )
  ).length
})


const warehouseEquipment = computed(() => {
  return equipment.value.filter(
    (item) => (
      item.commercial_status === "warehouse" &&
      !item.is_archived
    )
  ).length
})


const reviewEquipment = computed(() => {
  const reviewStatuses = [
    "for_review",
    "in_review",
  ]

  return equipment.value.filter(
    (item) => (
      reviewStatuses.includes(
        item.technical_status
      ) &&
      !item.is_archived
    )
  ).length
})


const soldEquipment = computed(() => {
  const soldStatuses = [
    "sold",
    "delivery_preparation",
    "in_transit",
    "delivered",
  ]

  return equipment.value.filter(
    (item) => (
      soldStatuses.includes(
        item.commercial_status
      ) &&
      !item.is_archived
    )
  ).length
})


const archivedEquipment = computed(() => {
  return equipment.value.filter(
    (item) => item.is_archived
  ).length
})


async function loadEquipment() {
  loading.value = true
  errorMessage.value = ""

  try {
    const isAvailable =
      selectedAvailability.value === "available"
        ? true
        : selectedAvailability.value === "unavailable"
          ? false
          : ""

    const response = await getEquipment({
      search: search.value,
      includeArchived:
        includeArchived.value,
      technicalStatus:
        selectedTechnicalStatus.value,
      commercialStatus:
        selectedCommercialStatus.value,
      physicalCondition:
        selectedCondition.value,
      ownershipType:
        selectedOwnership.value,
      colorMode:
        selectedColorMode.value,
      isAvailable,
    })

    equipment.value = Array.isArray(response)
      ? response
      : response?.results || []
  } catch (error) {
    equipment.value = []

    errorMessage.value =
      error.message ||
      "No se pudieron cargar los equipos."
  } finally {
    loading.value = false
  }
}


function handleSearch() {
  window.clearTimeout(searchTimeout)

  searchTimeout = window.setTimeout(() => {
    loadEquipment()
  }, 350)
}


function toggleColumnMenu() {
  showColumnMenu.value = !showColumnMenu.value
}

function closeColumnMenu() {
  showColumnMenu.value = false
}

function resetColumns() {
  visibleColumns.value = { ...defaultVisibleColumns }
  window.localStorage.setItem(
    "equipment-list-columns",
    JSON.stringify(visibleColumns.value),
  )
}

function toggleColumn(columnKey) {
  if (columnKey === "equipment") {
    return
  }

  visibleColumns.value = {
    ...visibleColumns.value,
    [columnKey]: !visibleColumns.value[columnKey],
  }

  window.localStorage.setItem(
    "equipment-list-columns",
    JSON.stringify(visibleColumns.value),
  )
}

function restoreColumnPreferences() {
  try {
    const saved = window.localStorage.getItem(
      "equipment-list-columns",
    )

    if (!saved) {
      return
    }

    visibleColumns.value = {
      ...defaultVisibleColumns,
      ...JSON.parse(saved),
      equipment: true,
    }
  } catch {
    visibleColumns.value = { ...defaultVisibleColumns }
  }
}

function clearMessages() {
  errorMessage.value = ""
  successMessage.value = ""
}


function clearFilters() {
  search.value = ""
  includeArchived.value = false
  selectedTechnicalStatus.value = ""
  selectedCommercialStatus.value = ""
  selectedAvailability.value = ""
  selectedCondition.value = ""
  selectedOwnership.value = ""
  selectedColorMode.value = ""

  loadEquipment()
}


async function goToCreate() {
  await router.push({
    name: "equipment-create",
  })
}


async function goToEdit(item) {
  await router.push({
    name: "equipment-edit",
    params: {
      id: item.id,
    },
  })
}


async function goToDetail(item) {
  await router.push({
    name: "equipment-detail",
    params: {
      id: item.id,
    },
  })
}

function isRowExpanded(item) {
  return expandedRows.value.has(item.id)
}


function toggleRow(item) {
  const next = new Set(expandedRows.value)

  if (next.has(item.id)) {
    next.delete(item.id)
  } else {
    next.add(item.id)
  }

  expandedRows.value = next
}


function handleRowClick(item) {
  goToDetail(item)
}


async function handleArchive(item) {
  const equipmentName =
    getEquipmentName(item)

  const reason = window.prompt(
    `Indica el motivo para archivar ${equipmentName}:`
  )

  if (reason === null) {
    return
  }

  const confirmed = window.confirm(
    `¿Confirmas que deseas archivar ${equipmentName}?`
  )

  if (!confirmed) {
    return
  }

  clearMessages()
  processingId.value = item.id

  try {
    await archiveEquipment(
      item.id,
      reason.trim()
    )

    successMessage.value =
      "Equipo archivado correctamente."

    await loadEquipment()
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo archivar el equipo."
  } finally {
    processingId.value = ""
  }
}


async function handleRestore(item) {
  const equipmentName =
    getEquipmentName(item)

  const confirmed = window.confirm(
    `¿Confirmas que deseas restaurar ${equipmentName}?`
  )

  if (!confirmed) {
    return
  }

  clearMessages()
  processingId.value = item.id

  try {
    await restoreEquipment(item.id)

    successMessage.value =
      "Equipo restaurado correctamente."

    await loadEquipment()
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo restaurar el equipo."
  } finally {
    processingId.value = ""
  }
}


function getEquipmentName(item) {
  const brand =
    item.brand_name ||
    item.equipment_model_detail
      ?.brand_name ||
    item.equipment_model_data
      ?.brand_name ||
    ""

  const model =
    item.model_name ||
    item.equipment_model_name ||
    item.equipment_model_detail
      ?.name ||
    item.equipment_model_data
      ?.name ||
    ""

  const completeName = [
    brand,
    model,
  ]
    .filter(Boolean)
    .join(" ")
    .trim()

  return (
    completeName ||
    item.serial_number ||
    item.internal_code ||
    "Equipo sin identificar"
  )
}


function getBrandName(item) {
  return (
    item.brand_name ||
    item.equipment_model_detail
      ?.brand_name ||
    item.equipment_model_data
      ?.brand_name ||
    item.equipment_model?.brand_name ||
    "Sin marca"
  )
}


function getModelName(item) {
  return (
    item.model_name ||
    item.equipment_model_name ||
    item.equipment_model_detail
      ?.name ||
    item.equipment_model_data
      ?.name ||
    item.equipment_model?.name ||
    "Sin modelo"
  )
}


function getEquipmentTypeName(item) {
  return (
    item.equipment_type_name ||
    item.equipment_model_detail
      ?.equipment_type_name ||
    item.equipment_model_data
      ?.equipment_type_name ||
    item.equipment_model
      ?.equipment_type_name ||
    "Sin tipo"
  )
}


function getCustomerName(item) {
  return (
    item.customer_name ||
    item.customer_detail
      ?.display_name ||
    item.customer_detail
      ?.trade_name ||
    item.customer_detail
      ?.legal_name ||
    "Sin cliente"
  )
}


function getBranchName(item) {
  return (
    item.customer_branch_name ||
    item.customer_branch_detail
      ?.name ||
    ""
  )
}


function getAdvisorName(item) {
  return (
    item.advisor_name ||
    item.advisor_detail
      ?.full_name ||
    item.advisor_detail
      ?.name ||
    "Sin asesor"
  )
}


function getTechnicalStatusName(item) {
  if (item.technical_status_name) {
    return item.technical_status_name
  }

  const statuses = {
    unreviewed: "Sin revisar",
    for_review: "Para revisión",
    in_review: "En revisión",
    completed: "Finalizada",
    with_problems: "Con problemas",
    for_parts: "De partes",
  }

  return (
    statuses[item.technical_status] ||
    "Sin estado"
  )
}


function getCommercialStatusName(item) {
  if (item.commercial_status_name) {
    return item.commercial_status_name
  }

  const statuses = {
    warehouse: "En almacén",
    reserved: "Separada",
    sold: "Vendida",
    delivery_preparation:
      "Preparando entrega",
    in_transit: "En tránsito",
    delivered: "Entregada",
    contract_assigned:
      "Asignada a contrato",
    installed: "Instalada",
    return_process:
      "En proceso de retorno",
    returned: "Retornada a almacén",
    temporary_loan:
      "Préstamo temporal",
    demonstration: "Demostración",
    replacement:
      "Equipo de reemplazo",
    out_of_service:
      "Fuera de servicio",
    disposed: "De baja",
  }

  return (
    statuses[item.commercial_status] ||
    "Sin estado"
  )
}


function getPhysicalConditionName(item) {
  if (item.physical_condition_name) {
    return item.physical_condition_name
  }

  const conditions = {
    new: "Nueva",
    used: "Usada",
    reconditioned: "Reacondicionada",
    trade_in:
      "Recibida en parte de pago",
    third_party:
      "Propiedad de tercero",
    other: "Otra",
  }

  return (
    conditions[item.physical_condition] ||
    "Sin condición"
  )
}


function getColorModeName(item) {
  const value =
    item.color_mode ||
    item.equipment_model_detail
      ?.color_mode ||
    item.equipment_model_data
      ?.color_mode ||
    item.equipment_model
      ?.color_mode

  const names = {
    monochrome: "Blanco y negro",
    color: "Color",
    mono: "Blanco y negro",
  }

  return names[value] || "Sin información"
}


function getTechnicalStatusClass(item) {
  const statusValue =
    item.technical_status

  const classes = {
    unreviewed: "neutral",
    for_review: "pending",
    in_review: "review",
    completed: "success",
    with_problems: "warning",
    for_parts: "danger",
  }

  return classes[statusValue] || "neutral"
}


function getCommercialStatusClass(item) {
  const statusValue =
    item.commercial_status

  const successStatuses = [
    "warehouse",
    "returned",
  ]

  const pendingStatuses = [
    "reserved",
    "delivery_preparation",
    "in_transit",
    "return_process",
  ]

  const assignedStatuses = [
    "contract_assigned",
    "installed",
    "temporary_loan",
    "demonstration",
    "replacement",
  ]

  if (
    successStatuses.includes(statusValue)
  ) {
    return "success"
  }

  if (
    pendingStatuses.includes(statusValue)
  ) {
    return "pending"
  }

  if (
    assignedStatuses.includes(statusValue)
  ) {
    return "assigned"
  }

  if (
    statusValue === "sold" ||
    statusValue === "delivered"
  ) {
    return "sold"
  }

  if (
    statusValue === "out_of_service" ||
    statusValue === "disposed"
  ) {
    return "danger"
  }

  return "neutral"
}


function formatMeter(value) {
  const number = Number(value || 0)

  if (!Number.isFinite(number)) {
    return "0"
  }

  return new Intl.NumberFormat(
    "es-PE"
  ).format(number)
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
  restoreColumnPreferences()
  loadEquipment()
})


onBeforeUnmount(() => {
  window.clearTimeout(searchTimeout)
})
</script>

<template>
  <section class="equipment-page">
    <header class="page-header">
      <div>
        <span class="page-kicker">
          Inventario de máquinas
        </span>

        <h2>
          Equipos
        </h2>

        <p>
          Administra las máquinas, series,
          estados técnicos, ubicación,
          contadores y asignaciones comerciales.
        </p>
      </div>

      <button
        class="primary-button"
        type="button"
        @click="goToCreate"
      >
        <span>＋</span>
        Nuevo equipo
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
            {{ totalEquipment }}
          </strong>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon available">
          ✓
        </span>

        <div>
          <small>Disponibles</small>

          <strong>
            {{ availableEquipment }}
          </strong>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon warehouse">
          ▦
        </span>

        <div>
          <small>En almacén</small>

          <strong>
            {{ warehouseEquipment }}
          </strong>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon review">
          ⚙
        </span>

        <div>
          <small>En revisión</small>

          <strong>
            {{ reviewEquipment }}
          </strong>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon sold">
          $
        </span>

        <div>
          <small>Vendidos / entrega</small>

          <strong>
            {{ soldEquipment }}
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
            {{ archivedEquipment }}
          </strong>
        </div>
      </article>
    </div>

    <div class="equipment-panel">
      <div class="panel-toolbar">
        <div class="panel-toolbar__title">
          <strong>Listado de equipos</strong>
          <span>{{ totalEquipment }} resultados</span>
        </div>

        <div class="column-selector" @mouseleave="closeColumnMenu">
          <button
            class="columns-button"
            type="button"
            :aria-expanded="showColumnMenu"
            @click="toggleColumnMenu"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M4 6h16M4 12h16M4 18h16" />
              <path d="M8 4v4M14 10v4M18 16v4" />
            </svg>
            Columnas
          </button>

          <div v-if="showColumnMenu" class="columns-menu">
            <div class="columns-menu__header">
              <strong>Campos visibles</strong>
              <button type="button" @click="resetColumns">Restablecer</button>
            </div>

            <label
              v-for="column in columnOptions"
              :key="column.key"
              class="column-option"
              :class="{ locked: column.locked }"
            >
              <input
                type="checkbox"
                :checked="visibleColumns[column.key]"
                :disabled="column.locked"
                @change="toggleColumn(column.key)"
              />
              <span>{{ column.label }}</span>
            </label>
          </div>
        </div>
      </div>

      <div class="filters">
        <label class="search-field">
          <span>⌕</span>

          <input
            v-model="search"
            type="search"
            placeholder="Buscar por serie, código, marca, modelo, cliente, IP o ubicación"
            @input="handleSearch"
          />
        </label>

        <select
          v-model="selectedTechnicalStatus"
          class="filter-select"
          @change="loadEquipment"
        >
          <option value="">
            Todos los estados técnicos
          </option>

          <option value="unreviewed">
            Sin revisar
          </option>

          <option value="for_review">
            Para revisión
          </option>

          <option value="in_review">
            En revisión
          </option>

          <option value="completed">
            Finalizada
          </option>

          <option value="with_problems">
            Con problemas
          </option>

          <option value="for_parts">
            De partes
          </option>
        </select>

        <select
          v-model="selectedCommercialStatus"
          class="filter-select"
          @change="loadEquipment"
        >
          <option value="">
            Todos los estados comerciales
          </option>

          <option value="warehouse">
            En almacén
          </option>

          <option value="reserved">
            Separada
          </option>

          <option value="sold">
            Vendida
          </option>

          <option value="delivery_preparation">
            Preparando entrega
          </option>

          <option value="in_transit">
            En tránsito
          </option>

          <option value="delivered">
            Entregada
          </option>

          <option value="contract_assigned">
            Asignada a contrato
          </option>

          <option value="installed">
            Instalada
          </option>

          <option value="returned">
            Retornada a almacén
          </option>

          <option value="temporary_loan">
            Préstamo temporal
          </option>

          <option value="demonstration">
            Demostración
          </option>

          <option value="replacement">
            Reemplazo
          </option>

          <option value="out_of_service">
            Fuera de servicio
          </option>

          <option value="disposed">
            De baja
          </option>
        </select>

        <select
          v-model="selectedAvailability"
          class="filter-select"
          @change="loadEquipment"
        >
          <option value="">
            Toda disponibilidad
          </option>

          <option value="available">
            Disponibles
          </option>

          <option value="unavailable">
            No disponibles
          </option>
        </select>

        <select
          v-model="selectedCondition"
          class="filter-select"
          @change="loadEquipment"
        >
          <option value="">
            Todas las condiciones
          </option>

          <option value="new">
            Nueva
          </option>

          <option value="used">
            Usada
          </option>

          <option value="reconditioned">
            Reacondicionada
          </option>

          <option value="trade_in">
            Parte de pago
          </option>

          <option value="third_party">
            De tercero
          </option>
        </select>

        <select
          v-model="selectedColorMode"
          class="filter-select"
          @change="loadEquipment"
        >
          <option value="">
            Todo tipo de impresión
          </option>

          <option value="monochrome">
            Blanco y negro
          </option>

          <option value="color">
            Color
          </option>
        </select>

        <label class="archive-filter">
          <input
            v-model="includeArchived"
            type="checkbox"
            @change="loadEquipment"
          />

          <span>
            Mostrar archivados
          </span>
        </label>

        <button
          class="refresh-button"
          type="button"
          :disabled="loading"
          @click="loadEquipment"
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
          <span v-if="activeFilterCount" class="filter-count">
            {{ activeFilterCount }}
          </span>
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

        Cargando equipos...
      </div>

      <div
        v-else-if="!equipment.length"
        class="empty-state"
      >
        <span>▣</span>

        <strong>
          No se encontraron equipos
        </strong>

        <p>
          Cambia los filtros o registra
          una nueva máquina en el inventario.
        </p>

        <button
          class="empty-create-button"
          type="button"
          @click="goToCreate"
        >
          Registrar equipo
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
                Equipo
              </th>

              <th v-if="visibleColumns.identifiers">
                Serie / código
              </th>

              <th v-if="visibleColumns.condition">
                Condición
              </th>

              <th v-if="visibleColumns.technical">
                Estado técnico
              </th>

              <th v-if="visibleColumns.commercial">
                Estado comercial
              </th>

              <th v-if="visibleColumns.location">
                Cliente / ubicación
              </th>

              <th v-if="visibleColumns.meters">
                Contadores
              </th>

              <th v-if="visibleColumns.availability">
                Disponibilidad
              </th>

              <th v-if="visibleColumns.updated">
                Actualizado
              </th>

              <th class="actions-column">
                Acciones
              </th>
            </tr>
          </thead>

          <tbody>
            <template
              v-for="item in equipment"
              :key="item.id"
            >
              <tr
                class="equipment-row"
                :class="{
                  'archived-row':
                    item.is_archived,
                  'unavailable-row':
                    !item.is_available &&
                    !item.is_archived,
                  'expanded-row':
                    isRowExpanded(item),
                }"
                tabindex="0"
                @click="handleRowClick(item)"
                @keydown.enter="handleRowClick(item)"
              >
              <td>
                <div class="equipment-cell">
                  <span class="equipment-avatar">
                    ▣
                  </span>

                  <div class="equipment-information">
                    <strong>
                      {{ getEquipmentName(item) }}
                    </strong>

                    <span>
                      {{ getEquipmentTypeName(item) }}
                      ·
                      {{ getColorModeName(item) }}
                    </span>

                    <small>
                      {{ getBrandName(item) }}
                      ·
                      {{ getModelName(item) }}
                    </small>
                  </div>
                </div>
              </td>

              <td v-if="visibleColumns.identifiers">
                <div class="identifier-information">
                  <strong>
                    {{
                      item.serial_number ||
                      "Sin serie"
                    }}
                  </strong>

                  <span>
                    {{
                      item.internal_code ||
                      "Sin código interno"
                    }}
                  </span>

                  <small
                    v-if="item.asset_number"
                  >
                    Patrimonial:
                    {{ item.asset_number }}
                  </small>
                </div>
              </td>

              <td v-if="visibleColumns.condition">
                <span class="condition-badge">
                  {{
                    getPhysicalConditionName(
                      item
                    )
                  }}
                </span>

                <small class="ownership-label">
                  {{
                    item.ownership_type_name ||
                    item.ownership_type ||
                    "Sin propiedad"
                  }}
                </small>
              </td>

              <td v-if="visibleColumns.technical">
                <span
                  class="state-badge"
                  :class="
                    getTechnicalStatusClass(
                      item
                    )
                  "
                >
                  {{
                    getTechnicalStatusName(
                      item
                    )
                  }}
                </span>

                <small
                  v-if="
                    item.technical_status_reason
                  "
                  class="reason-label"
                >
                  {{
                    item.technical_status_reason
                  }}
                </small>
              </td>

              <td v-if="visibleColumns.commercial">
                <span
                  class="state-badge"
                  :class="
                    getCommercialStatusClass(
                      item
                    )
                  "
                >
                  {{
                    getCommercialStatusName(
                      item
                    )
                  }}
                </span>

                <small
                  v-if="
                    item.commercial_status_reason
                  "
                  class="reason-label"
                >
                  {{
                    item.commercial_status_reason
                  }}
                </small>
              </td>

              <td v-if="visibleColumns.location">
                <div class="location-information">
                  <strong>
                    {{ getCustomerName(item) }}
                  </strong>

                  <span
                    v-if="getBranchName(item)"
                  >
                    {{ getBranchName(item) }}
                  </span>

                  <span v-else>
                    {{
                      item.warehouse_location ||
                      "Sin ubicación"
                    }}
                  </span>

                  <small>
                    {{ getAdvisorName(item) }}
                  </small>
                </div>
              </td>

              <td v-if="visibleColumns.meters">
                <div class="meters-container">
                  <span>
                    Total:
                    <strong>
                      {{
                        formatMeter(
                          item.current_total_meter
                        )
                      }}
                    </strong>
                  </span>

                  <span>
                    B/N:
                    <strong>
                      {{
                        formatMeter(
                          item.current_black_meter
                        )
                      }}
                    </strong>
                  </span>

                  <span>
                    Color:
                    <strong>
                      {{
                        formatMeter(
                          item.current_color_meter
                        )
                      }}
                    </strong>
                  </span>
                </div>
              </td>

              <td v-if="visibleColumns.availability">
                <div class="availability-container">
                  <span
                    v-if="item.is_archived"
                    class="availability-badge archived"
                  >
                    Archivado
                  </span>

                  <span
                    v-else-if="item.is_available"
                    class="availability-badge available"
                  >
                    Disponible
                  </span>

                  <span
                    v-else
                    class="availability-badge unavailable"
                  >
                    No disponible
                  </span>

                </div>
              </td>

              <td v-if="visibleColumns.updated" class="updated-cell">
                {{
                  formatDate(
                    item.updated_at
                  )
                }}
              </td>

              <td>
                <div class="row-actions">
                  <button
                    class="action-button expand"
                    type="button"
                    :title="
                      isRowExpanded(item)
                        ? 'Ocultar información'
                        : 'Mostrar más información'
                    "
                    :aria-label="
                      isRowExpanded(item)
                        ? 'Ocultar información'
                        : 'Mostrar más información'
                    "
                    @click.stop="toggleRow(item)"
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        d="m7 10 5 5 5-5"
                        :class="{ rotated: isRowExpanded(item) }"
                      />
                    </svg>
                  </button>

                  <button
                    class="action-button detail"
                    type="button"
                    title="Ver equipo"
                    aria-label="Ver equipo"
                    :disabled="
                      processingId === item.id
                    "
                    @click.stop="goToDetail(item)"
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" />
                      <circle cx="12" cy="12" r="2.7" />
                    </svg>
                  </button>

                  <button
                    class="action-button edit"
                    type="button"
                    title="Editar equipo"
                    aria-label="Editar equipo"
                    :disabled="
                      item.is_archived ||
                      processingId === item.id
                    "
                    @click.stop="goToEdit(item)"
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M4 20h4l11-11-4-4L4 16v4Z" />
                      <path d="m13.5 6.5 4 4" />
                    </svg>
                  </button>

                  <button
                    v-if="!item.is_archived"
                    class="action-button archive"
                    type="button"
                    title="Archivar equipo"
                    aria-label="Archivar equipo"
                    :disabled="
                      processingId === item.id
                    "
                    @click.stop="
                      handleArchive(item)
                    "
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M4 7h16" />
                      <path d="M9 7V4h6v3" />
                      <path d="M6 7l1 13h10l1-13" />
                      <path d="M10 11v5M14 11v5" />
                    </svg>
                  </button>

                  <button
                    v-else
                    class="action-button restore"
                    type="button"
                    title="Restaurar equipo"
                    aria-label="Restaurar equipo"
                    :disabled="
                      processingId === item.id
                    "
                    @click.stop="
                      handleRestore(item)
                    "
                  >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path d="M4 4v6h6" />
                      <path d="M5.5 15a7 7 0 1 0 1.6-7.4L4 10" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>

              <tr
                v-if="isRowExpanded(item)"
                class="equipment-expanded-row"
              >
                <td :colspan="visibleColumnCount">
                  <div class="expanded-information-grid">
                    <article>
                      <small>Importación</small>
                      <strong>
                        {{
                          item.import_batch_code ||
                          item.import_reference ||
                          "Sin importación"
                        }}
                      </strong>
                    </article>

                    <article>
                      <small>Proveedor</small>
                      <strong>
                        {{
                          item.supplier_name ||
                          "Sin proveedor"
                        }}
                      </strong>
                    </article>

                    <article>
                      <small>Precio de compra</small>
                      <strong>
                        {{
                          item.purchase_price || "0.00"
                        }}
                        {{ item.purchase_currency || "" }}
                      </strong>
                    </article>

                    <article>
                      <small>Precio de venta</small>
                      <strong>
                        {{
                          item.sale_price || "0.00"
                        }}
                        {{ item.sale_currency || "" }}
                      </strong>
                    </article>

                    <article>
                      <small>Fecha de descarga</small>
                      <strong>
                        {{ formatDate(item.unloading_date) }}
                      </strong>
                    </article>

                    <article>
                      <small>IP</small>
                      <strong>
                        {{ item.ip_address || "Sin IP" }}
                      </strong>
                    </article>

                    <article>
                      <small>Código patrimonial</small>
                      <strong>
                        {{ item.asset_number || "Sin código" }}
                      </strong>
                    </article>

                    <article>
                      <small>Última lectura</small>
                      <strong>
                        {{ formatDate(item.last_meter_date) }}
                      </strong>
                    </article>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>
