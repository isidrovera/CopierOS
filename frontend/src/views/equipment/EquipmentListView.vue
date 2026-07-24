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

let searchTimeout = null


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

              <th>
                Serie / código
              </th>

              <th>
                Condición
              </th>

              <th>
                Estado técnico
              </th>

              <th>
                Estado comercial
              </th>

              <th>
                Cliente / ubicación
              </th>

              <th>
                Contadores
              </th>

              <th>
                Disponibilidad
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

              <td>
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

              <td>
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

              <td>
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

              <td>
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

              <td>
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

              <td>
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

              <td>
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

              <td>
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
                <td colspan="10">
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

<style scoped>
button,
input,
select {
  font: inherit;
}

.equipment-page {
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
    repeat(6, minmax(0, 1fr));
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

.summary-icon.available {
  background: #eaf7ef;
  color: #288653;
}

.summary-icon.warehouse {
  background: #e9f1fb;
  color: #396da8;
}

.summary-icon.review {
  background: #fff5e7;
  color: #b06b21;
}

.summary-icon.sold {
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

.equipment-panel {
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
  min-width: 300px;
  min-height: 42px;
  display: flex;
  flex: 1 1 420px;
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
  max-width: 220px;
  padding: 0 11px;
  border: 1px solid #dce4eb;
  border-radius: 10px;
  outline: none;
  background: white;
  color: #526174;
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
  min-width: 1750px;
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

.equipment-row {
  cursor: pointer;
  transition:
    background 0.18s ease,
    box-shadow 0.18s ease;
}

.equipment-row:focus-visible {
  outline: 2px solid #77b7d2;
  outline-offset: -2px;
}

.equipment-row.expanded-row {
  background: #f7fafc;
}

.equipment-expanded-row td {
  padding: 0;
  background: #fbfcfd;
}

.expanded-information-grid {
  display: grid;
  grid-template-columns:
    repeat(4, minmax(0, 1fr));
  gap: 1px;
  padding: 12px 16px 16px;
  border-top: 1px solid #e8edf1;
  background: #e8edf1;
}

.expanded-information-grid article {
  min-width: 0;
  padding: 12px 14px;
  background: white;
}

.expanded-information-grid small,
.expanded-information-grid strong {
  display: block;
}

.expanded-information-grid small {
  margin-bottom: 5px;
  color: #8390a0;
  font-size: 10px;
  text-transform: uppercase;
}

.expanded-information-grid strong {
  overflow: hidden;
  color: #324257;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

tbody tr:last-child td {
  border-bottom: 0;
}

.archived-row {
  opacity: 0.7;
}

.unavailable-row:not(.archived-row) {
  background: #fffaf7;
}

.equipment-cell {
  min-width: 245px;
  display: flex;
  align-items: center;
  gap: 11px;
}

.equipment-avatar {
  width: 42px;
  height: 42px;
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: #e7f2f7;
  color: #257ca3;
  font-size: 18px;
  font-weight: 800;
}

.equipment-information,
.identifier-information,
.location-information {
  min-width: 0;
}

.equipment-information strong,
.equipment-information span,
.equipment-information small,
.identifier-information strong,
.identifier-information span,
.identifier-information small,
.location-information strong,
.location-information span,
.location-information small {
  display: block;
}

.equipment-information strong,
.identifier-information strong,
.location-information strong {
  color: #2d3c50;
  font-size: 13px;
}

.equipment-information strong {
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.equipment-information span,
.identifier-information span,
.location-information span {
  margin-top: 3px;
  color: #8792a0;
  font-size: 11px;
}

.equipment-information small,
.identifier-information small,
.location-information small {
  margin-top: 3px;
  color: #6b7889;
  font-size: 11px;
}

.condition-badge,
.state-badge,
.availability-badge {
  display: inline-flex;
  padding: 5px 8px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
}

.condition-badge {
  background: #e9f1f8;
  color: #3f6c8c;
}

.ownership-label,
.reason-label {
  display: block;
  max-width: 180px;
  margin-top: 5px;
  overflow: hidden;
  color: #8792a0;
  font-size: 10px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.state-badge.neutral {
  background: #edf0f4;
  color: #687585;
}

.state-badge.pending {
  background: #fff3e5;
  color: #a76625;
}

.state-badge.review {
  background: #e8f2fa;
  color: #326f9a;
}

.state-badge.success {
  background: #e7f6ed;
  color: #277d4c;
}

.state-badge.warning {
  background: #fff0e8;
  color: #b45e32;
}

.state-badge.danger {
  background: #fff0ed;
  color: #ae4f43;
}

.state-badge.assigned {
  background: #f2edfa;
  color: #6b55a5;
}

.state-badge.sold {
  background: #eaf0fb;
  color: #416ca1;
}

.meters-container {
  min-width: 135px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meters-container span {
  color: #7d8997;
  font-size: 10px;
}

.meters-container strong {
  color: #34445a;
  font-size: 11px;
}

.availability-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 5px;
}

.availability-badge.available {
  background: #e7f6ed;
  color: #277d4c;
}

.availability-badge.unavailable {
  background: #fff0e8;
  color: #b45e32;
}

.availability-badge.archived {
  background: #eceff3;
  color: #657181;
}

.availability-container small {
  color: #8a96a3;
  font-size: 10px;
}

.actions-column {
  text-align: right;
}

.row-actions {
  min-width: 180px;
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}

.action-button {
  width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: 1px solid #dce4ea;
  border-radius: 8px;
  background: white;
  color: #4e6073;
  cursor: pointer;
}

.action-button svg {
  width: 17px;
  height: 17px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.action-button.expand svg path {
  transform-origin: center;
  transition: transform 0.2s ease;
}

.action-button.expand svg path.rotated {
  transform: rotate(180deg);
}

.action-button:hover {
  background: #f3f7f9;
}

.action-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.action-button.detail {
  border-color: #d6dee5;
  color: #586b7e;
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

@media (max-width: 1450px) {
  .summary-grid {
    grid-template-columns:
      repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 1100px) {
  .expanded-information-grid {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
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

  .filter-select {
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