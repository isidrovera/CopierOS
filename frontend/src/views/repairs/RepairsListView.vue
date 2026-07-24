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
  getRepairs,
} from "../../services/repairs.service"

import "./RepairsListView.css"


const router = useRouter()

const repairs = ref([])
const loading = ref(false)
const errorMessage = ref("")

const search = ref("")
const selectedStatus = ref("")
const selectedPriority = ref("")
const selectedRepairType = ref("")
const includeArchived = ref(false)

let searchTimeout = null


const totalRepairs = computed(() => {
  return repairs.value.length
})


const pendingRepairs = computed(() => {
  return repairs.value.filter(
    (item) =>
      item.status === "pending"
  ).length
})


const activeRepairs = computed(() => {
  const activeStatuses = [
    "assigned",
    "under_review",
    "waiting_parts",
    "in_repair",
    "testing",
  ]

  return repairs.value.filter(
    (item) =>
      activeStatuses.includes(
        item.status
      )
  ).length
})


const completedRepairs = computed(() => {
  return repairs.value.filter(
    (item) =>
      item.status === "completed" ||
      item.status === "delivered"
  ).length
})


function normalizeCollection(data) {
  if (Array.isArray(data)) {
    return data
  }

  if (
    data &&
    Array.isArray(data.results)
  ) {
    return data.results
  }

  return []
}


async function loadRepairs() {
  loading.value = true
  errorMessage.value = ""

  try {
    const response = await getRepairs({
      search: search.value,
      status: selectedStatus.value,
      priority: selectedPriority.value,
      repairType:
        selectedRepairType.value,
      includeArchived:
        includeArchived.value,
      ordering: "-created_at",
    })

    repairs.value =
      normalizeCollection(response)
  } catch (error) {
    repairs.value = []

    errorMessage.value =
      error.message ||
      "No se pudieron cargar las reparaciones."
  } finally {
    loading.value = false
  }
}


function handleSearch() {
  window.clearTimeout(
    searchTimeout
  )

  searchTimeout =
    window.setTimeout(
      () => {
        loadRepairs()
      },
      350
    )
}


function clearFilters() {
  search.value = ""
  selectedStatus.value = ""
  selectedPriority.value = ""
  selectedRepairType.value = ""
  includeArchived.value = false

  loadRepairs()
}


function openCreateView() {
  router.push({
    name: "repair-create",
  })
}


function openRepair(item) {
  if (!item?.id) {
    return
  }

  router.push({
    name: "repair-detail",
    params: {
      id: item.id,
    },
  })
}


function editRepair(
  item,
  event
) {
  event?.stopPropagation()

  if (!item?.id) {
    return
  }

  router.push({
    name: "repair-edit",
    params: {
      id: item.id,
    },
  })
}


function getRepairCode(item) {
  return (
    item.code ||
    item.repair_code ||
    "Sin código"
  )
}


function getEquipmentName(item) {
  const directName =
    String(
      item.equipment_name || ""
    ).trim()

  if (directName) {
    return directName
  }

  const brand =
    item.equipment_brand_name ||
    item.brand_name ||
    ""

  const model =
    item.equipment_model_name ||
    item.model_name ||
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
    "Equipo sin identificar"
  )
}


function getSerialNumber(item) {
  return (
    item.equipment_serial_number ||
    item.serial_number ||
    "Sin serie"
  )
}


function getInternalCode(item) {
  return (
    item.equipment_internal_code ||
    item.internal_code ||
    "Sin código interno"
  )
}


function getStatusName(item) {
  const names = {
    pending: "Pendiente",
    assigned: "Asignada",
    under_review: "En revisión",
    waiting_parts:
      "Esperando repuestos",
    in_repair: "En reparación",
    testing: "En pruebas",
    completed: "Finalizada",
    delivered: "Entregada",
    cancelled: "Cancelada",
  }

  return (
    item.status_name ||
    item.status_display ||
    names[item.status] ||
    "Sin estado"
  )
}


function getStatusClass(item) {
  const classes = {
    pending: "pending",
    assigned: "assigned",
    under_review: "review",
    waiting_parts: "waiting",
    in_repair: "repair",
    testing: "testing",
    completed: "completed",
    delivered: "delivered",
    cancelled: "cancelled",
  }

  return (
    classes[item.status] ||
    "neutral"
  )
}


function getPriorityName(item) {
  const names = {
    low: "Baja",
    normal: "Normal",
    high: "Alta",
    urgent: "Urgente",
  }

  return (
    item.priority_name ||
    item.priority_display ||
    names[item.priority] ||
    "Normal"
  )
}


function getPriorityClass(item) {
  return (
    item.priority ||
    "normal"
  )
}


function getRepairTypeName(item) {
  const names = {
    initial_review:
      "Revisión inicial",
    preventive:
      "Mantenimiento preventivo",
    corrective:
      "Mantenimiento correctivo",
    reconditioning:
      "Reacondicionamiento",
    warranty:
      "Garantía",
    return_review:
      "Revisión por devolución",
    other:
      "Otro",
  }

  return (
    item.repair_type_name ||
    item.repair_type_display ||
    names[item.repair_type] ||
    "Sin tipo"
  )
}


function getTechnicianName(item) {
  return (
    item.assigned_technician_name ||
    "Sin técnico"
  )
}


function formatDate(value) {
  if (!value) {
    return "Sin registro"
  }

  const date = new Date(value)

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
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


function getChecklistProgress(item) {
  return item.checklist_completed
    ? "Completo"
    : "Pendiente"
}


function getPhotosProgress(item) {
  if (
    item.minimum_photos_completed
  ) {
    return "Completo"
  }

  const photoCount =
    Number(
      item.photo_count || 0
    )

  const required =
    Number(
      item.minimum_photos_required ||
      0
    )

  return `${photoCount}/${required}`
}


function getTestsProgress(item) {
  return item.tests_completed
    ? "Completo"
    : "Pendiente"
}


function isArchived(item) {
  return Boolean(
    item.is_archived ||
    item.archived_at
  )
}


onMounted(() => {
  loadRepairs()
})


onBeforeUnmount(() => {
  window.clearTimeout(
    searchTimeout
  )
})
</script>

<template>
  <section class="repairs-page">
    <header class="repairs-header">
      <div>
        <span class="page-kicker">
          Taller técnico
        </span>

        <h1>
          Reparaciones
        </h1>

        <p>
          Control de revisiones,
          asignaciones, evidencias,
          pruebas y entregas.
        </p>
      </div>

      <button
        class="primary-button"
        type="button"
        @click="openCreateView"
      >
        <span>
          ＋
        </span>

        Nueva reparación
      </button>
    </header>

    <section class="summary-grid">
      <article class="summary-card">
        <span class="summary-icon">
          ▦
        </span>

        <div>
          <small>
            Total visible
          </small>

          <strong>
            {{ totalRepairs }}
          </strong>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon pending">
          ◷
        </span>

        <div>
          <small>
            Pendientes
          </small>

          <strong>
            {{ pendingRepairs }}
          </strong>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon active">
          ⚙
        </span>

        <div>
          <small>
            En proceso
          </small>

          <strong>
            {{ activeRepairs }}
          </strong>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon completed">
          ✓
        </span>

        <div>
          <small>
            Finalizadas
          </small>

          <strong>
            {{ completedRepairs }}
          </strong>
        </div>
      </article>
    </section>

    <section class="repairs-panel">
      <div class="filters-section">
        <label class="search-field">
          <span class="search-icon">
            ⌕
          </span>

          <input
            v-model="search"
            type="search"
            placeholder="Buscar por código, serie, marca, modelo o técnico"
            @input="handleSearch"
          />
        </label>

        <select
          v-model="selectedStatus"
          @change="loadRepairs"
        >
          <option value="">
            Todos los estados
          </option>

          <option value="pending">
            Pendiente
          </option>

          <option value="assigned">
            Asignada
          </option>

          <option value="under_review">
            En revisión
          </option>

          <option value="waiting_parts">
            Esperando repuestos
          </option>

          <option value="in_repair">
            En reparación
          </option>

          <option value="testing">
            En pruebas
          </option>

          <option value="completed">
            Finalizada
          </option>

          <option value="delivered">
            Entregada
          </option>

          <option value="cancelled">
            Cancelada
          </option>
        </select>

        <select
          v-model="selectedPriority"
          @change="loadRepairs"
        >
          <option value="">
            Todas las prioridades
          </option>

          <option value="low">
            Baja
          </option>

          <option value="normal">
            Normal
          </option>

          <option value="high">
            Alta
          </option>

          <option value="urgent">
            Urgente
          </option>
        </select>

        <select
          v-model="selectedRepairType"
          @change="loadRepairs"
        >
          <option value="">
            Todos los tipos
          </option>

          <option value="initial_review">
            Revisión inicial
          </option>

          <option value="preventive">
            Preventivo
          </option>

          <option value="corrective">
            Correctivo
          </option>

          <option value="reconditioning">
            Reacondicionamiento
          </option>

          <option value="warranty">
            Garantía
          </option>

          <option value="return_review">
            Devolución
          </option>

          <option value="other">
            Otro
          </option>
        </select>

        <label class="archive-filter">
          <input
            v-model="includeArchived"
            type="checkbox"
            @change="loadRepairs"
          />

          <span class="archive-control"></span>

          <span>
            Ver archivadas
          </span>
        </label>

        <button
          class="secondary-button"
          type="button"
          :disabled="loading"
          @click="loadRepairs"
        >
          ↻ Actualizar
        </button>

        <button
          class="secondary-button"
          type="button"
          :disabled="loading"
          @click="clearFilters"
        >
          Limpiar
        </button>
      </div>

      <div
        v-if="errorMessage"
        class="error-message"
      >
        {{ errorMessage }}
      </div>

      <div
        v-if="loading"
        class="loading-state"
      >
        <span class="spinner"></span>

        Cargando reparaciones...
      </div>

      <div
        v-else-if="!repairs.length"
        class="empty-state"
      >
        <span class="empty-icon">
          ⚙
        </span>

        <strong>
          No se encontraron reparaciones
        </strong>

        <p>
          Registra una nueva reparación
          o cambia los filtros aplicados.
        </p>

        <button
          class="primary-button"
          type="button"
          @click="openCreateView"
        >
          ＋ Nueva reparación
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
                Reparación
              </th>

              <th>
                Equipo
              </th>

              <th>
                Tipo
              </th>

              <th>
                Estado
              </th>

              <th>
                Prioridad
              </th>

              <th>
                Técnico
              </th>

              <th>
                Avance técnico
              </th>

              <th>
                Ingreso
              </th>

              <th class="actions-column">
                Acciones
              </th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="item in repairs"
              :key="item.id"
              class="repair-row"
              :class="{
                archived:
                  isArchived(item),
              }"
              @click="openRepair(item)"
            >
              <td>
                <div class="repair-code-cell">
                  <strong>
                    {{ getRepairCode(item) }}
                  </strong>

                  <span
                    v-if="isArchived(item)"
                    class="archived-badge"
                  >
                    Archivada
                  </span>

                  <small>
                    {{
                      item.reported_problem ||
                      "Sin problema reportado"
                    }}
                  </small>
                </div>
              </td>

              <td>
                <div class="equipment-cell">
                  <span class="equipment-icon">
                    ▣
                  </span>

                  <div>
                    <strong>
                      {{ getEquipmentName(item) }}
                    </strong>

                    <span>
                      Serie:
                      {{ getSerialNumber(item) }}
                    </span>

                    <small>
                      {{ getInternalCode(item) }}
                    </small>
                  </div>
                </div>
              </td>

              <td>
                <span class="type-badge">
                  {{ getRepairTypeName(item) }}
                </span>
              </td>

              <td>
                <span
                  class="state-badge"
                  :class="
                    getStatusClass(item)
                  "
                >
                  {{ getStatusName(item) }}
                </span>
              </td>

              <td>
                <span
                  class="priority-badge"
                  :class="
                    getPriorityClass(item)
                  "
                >
                  {{ getPriorityName(item) }}
                </span>
              </td>

              <td>
                <div class="technician-cell">
                  <span class="technician-avatar">
                    ♙
                  </span>

                  <span>
                    {{ getTechnicianName(item) }}
                  </span>
                </div>
              </td>

              <td>
                <div class="progress-summary">
                  <span
                    :class="{
                      complete:
                        item.checklist_completed,
                    }"
                  >
                    <strong>
                      Checklist
                    </strong>

                    {{
                      getChecklistProgress(item)
                    }}
                  </span>

                  <span
                    :class="{
                      complete:
                        item.minimum_photos_completed,
                    }"
                  >
                    <strong>
                      Fotos
                    </strong>

                    {{
                      getPhotosProgress(item)
                    }}
                  </span>

                  <span
                    :class="{
                      complete:
                        item.tests_completed,
                    }"
                  >
                    <strong>
                      Pruebas
                    </strong>

                    {{
                      getTestsProgress(item)
                    }}
                  </span>
                </div>
              </td>

              <td>
                <div class="date-cell">
                  <strong>
                    {{
                      formatDate(
                        item.requested_at
                      )
                    }}
                  </strong>

                  <small>
                    Creada:
                    {{
                      formatDate(
                        item.created_at
                      )
                    }}
                  </small>
                </div>
              </td>

              <td
                class="actions-cell"
                @click.stop
              >
                <button
                  class="icon-button"
                  type="button"
                  title="Ver reparación"
                  @click="openRepair(item)"
                >
                  ◉
                </button>

                <button
                  v-if="!isArchived(item)"
                  class="icon-button"
                  type="button"
                  title="Editar reparación"
                  @click="
                    editRepair(
                      item,
                      $event
                    )
                  "
                >
                  ✎
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>