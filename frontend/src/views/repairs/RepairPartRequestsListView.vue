<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from "vue"
import { useRouter } from "vue-router"

import RepairPartRequestStatusBadge from "./components/RepairPartRequestStatusBadge.vue"

import {
  getRepairPartRequests,
} from "../../services/repairs.service"

import "./RepairPartRequestsListView.css"

const router = useRouter()

const loading = ref(false)
const errorMessage = ref("")
const requests = ref([])

const filters = reactive({
  search: "",
  status: "",
  priority: "",
  currentResponsibleArea: "",
  includeArchived: false,
  ordering: "-created_at",
})

const statusOptions = [
  ["draft", "Borrador"],
  ["submitted", "Enviada"],
  ["in_review", "En revisión"],
  ["partially_approved", "Parcialmente aprobada"],
  ["approved", "Aprobada"],
  ["partially_attended", "Parcialmente atendida"],
  ["attended", "Atendida"],
  ["rejected", "Rechazada"],
  ["cancelled", "Cancelada"],
  ["closed", "Cerrada"],
]

const priorityOptions = [
  ["low", "Baja"],
  ["normal", "Normal"],
  ["high", "Alta"],
  ["urgent", "Urgente"],
  ["critical", "Crítica"],
]

const responsibleAreaOptions = [
  ["technical", "Técnica"],
  ["area_manager", "Jefe de área"],
  ["management", "Gerencia"],
  ["warehouse", "Almacén"],
  ["logistics", "Logística"],
  ["purchasing", "Compras"],
  ["closed", "Cerrada"],
]

const activeRequests = computed(() =>
  requests.value.filter(
    request => !request.is_archived
  ).length
)

const archivedRequests = computed(() =>
  requests.value.filter(
    request => request.is_archived
  ).length
)

const urgentRequests = computed(() =>
  requests.value.filter(
    request =>
      request.priority === "urgent" ||
      request.priority === "critical"
  ).length
)

function normalizeResults(response) {
  if (Array.isArray(response)) {
    return response
  }

  return Array.isArray(response?.results)
    ? response.results
    : []
}

async function loadRequests() {
  loading.value = true
  errorMessage.value = ""

  try {
    const response = await getRepairPartRequests({
      search: filters.search,
      status: filters.status,
      priority: filters.priority,
      currentResponsibleArea:
        filters.currentResponsibleArea,
      includeArchived: filters.includeArchived,
      ordering: filters.ordering,
    })

    requests.value = normalizeResults(response)
  } catch (error) {
    errorMessage.value =
      error?.message ||
      "No se pudieron cargar las solicitudes."
  } finally {
    loading.value = false
  }
}

function clearFilters() {
  filters.search = ""
  filters.status = ""
  filters.priority = ""
  filters.currentResponsibleArea = ""
  filters.includeArchived = false
  filters.ordering = "-created_at"

  loadRequests()
}

function createRequest() {
  router.push({
    name: "repair-part-request-create",
  })
}

function openRequest(request) {
  router.push({
    name: "repair-part-request-detail",
    params: {
      id: request.id,
    },
  })
}

function editRequest(request) {
  router.push({
    name: "repair-part-request-edit",
    params: {
      id: request.id,
    },
  })
}

onMounted(loadRequests)
</script>

<template>
  <main class="repair-part-requests-list">
    <header class="repair-part-requests-list__header">
      <div>
        <span>Reparaciones</span>
        <h1>Pedidos de repuestos</h1>
        <p>
          Solicitudes generadas desde reparaciones,
          checklist y diagnósticos técnicos.
        </p>
      </div>

      <button
        type="button"
        class="primary"
        @click="createRequest"
      >
        + Nueva solicitud
      </button>
    </header>

    <section class="repair-part-requests-list__stats">
      <article>
        <strong>{{ activeRequests }}</strong>
        <span>Activas</span>
      </article>

      <article>
        <strong>{{ urgentRequests }}</strong>
        <span>Urgentes o críticas</span>
      </article>

      <article>
        <strong>{{ archivedRequests }}</strong>
        <span>Archivadas</span>
      </article>

      <article>
        <strong>{{ requests.length }}</strong>
        <span>Total mostrado</span>
      </article>
    </section>

    <section class="repair-part-requests-list__filters">
      <input
        v-model.trim="filters.search"
        type="search"
        placeholder="Código, reparación, serie, título..."
        @keyup.enter="loadRequests"
      >

      <select v-model="filters.status">
        <option value="">Todos los estados</option>
        <option
          v-for="[value, label] in statusOptions"
          :key="value"
          :value="value"
        >
          {{ label }}
        </option>
      </select>

      <select v-model="filters.priority">
        <option value="">Todas las prioridades</option>
        <option
          v-for="[value, label] in priorityOptions"
          :key="value"
          :value="value"
        >
          {{ label }}
        </option>
      </select>

      <select v-model="filters.currentResponsibleArea">
        <option value="">Todas las áreas</option>
        <option
          v-for="[value, label] in responsibleAreaOptions"
          :key="value"
          :value="value"
        >
          {{ label }}
        </option>
      </select>

      <label>
        <input
          v-model="filters.includeArchived"
          type="checkbox"
        >
        Incluir archivadas
      </label>

      <button type="button" @click="loadRequests">
        Buscar
      </button>

      <button
        type="button"
        class="secondary"
        @click="clearFilters"
      >
        Limpiar
      </button>
    </section>

    <p
      v-if="errorMessage"
      class="repair-part-requests-list__error"
    >
      {{ errorMessage }}
    </p>

    <section
      v-if="loading"
      class="repair-part-requests-list__state"
    >
      Cargando solicitudes...
    </section>

    <section
      v-else-if="!requests.length"
      class="repair-part-requests-list__state"
    >
      No se encontraron solicitudes.
    </section>

    <section
      v-else
      class="repair-part-requests-list__table-wrap"
    >
      <table>
        <thead>
          <tr>
            <th>Código</th>
            <th>Reparación / equipo</th>
            <th>Solicitud</th>
            <th>Estado</th>
            <th>Prioridad</th>
            <th>Área responsable</th>
            <th>Ítems</th>
            <th>Solicitado por</th>
            <th>Actualización</th>
            <th />
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="request in requests"
            :key="request.id"
            :class="{ archived: request.is_archived }"
          >
            <td>
              <strong>{{ request.code }}</strong>
            </td>

            <td>
              <span>{{ request.repair_code }}</span>
              <small>
                Serie:
                {{ request.equipment_serial_number }}
              </small>
            </td>

            <td>
              <strong>{{ request.title }}</strong>
            </td>

            <td>
              <RepairPartRequestStatusBadge
                :status="request.status"
                :label="request.status_name"
              />
            </td>

            <td>
              <span
                class="priority"
                :class="request.priority"
              >
                {{ request.priority_name }}
              </span>
            </td>

            <td>
              {{ request.responsible_area_name }}
            </td>

            <td>{{ request.total_items }}</td>

            <td>{{ request.requested_by_name }}</td>

            <td>{{ request.updated_at }}</td>

            <td class="actions">
              <button
                type="button"
                @click="openRequest(request)"
              >
                Ver
              </button>

              <button
                v-if="request.status === 'draft'"
                type="button"
                @click="editRequest(request)"
              >
                Editar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </main>
</template>
