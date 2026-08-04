<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from "vue"

import {
  useRouter,
} from "vue-router"

import MonitoringEmptyState from "../../components/monitoring/MonitoringEmptyState.vue"
import MonitoringStatusBadge from "../../components/monitoring/MonitoringStatusBadge.vue"
import MonitoringTabs from "../../components/monitoring/MonitoringTabs.vue"

import {
  archiveAgent,
  getAgents,
  normalizeList,
  restoreAgent,
} from "../../services/monitoring.service"

import "./MonitoringAgentsView.css"


const router = useRouter()


const loading = ref(true)
const processingId = ref("")

const error = ref("")
const success = ref("")

const agents = ref([])

const selectedAgent = ref(null)

const showArchiveModal = ref(false)
const archiveReason = ref("")


const filters = reactive({
  search: "",
  status: "",
  connection: "",
  includeArchived: false,
})


const statusOptions = [
  {
    value: "",
    label: "Todos los estados",
  },
  {
    value: "active",
    label: "Activos",
  },
  {
    value: "offline",
    label: "Sin conexión",
  },
  {
    value: "pending",
    label: "Pendientes",
  },
  {
    value: "error",
    label: "Con error",
  },
  {
    value: "suspended",
    label: "Suspendidos",
  },
  {
    value: "revoked",
    label: "Revocados",
  },
]


const connectionOptions = [
  {
    value: "",
    label: "Cualquier conexión",
  },
  {
    value: "online",
    label: "Conectados",
  },
  {
    value: "offline",
    label: "Desconectados",
  },
  {
    value: "never",
    label: "Nunca conectados",
  },
]


const filteredAgents = computed(() => {
  const term = filters.search
    .trim()
    .toLowerCase()

  return agents.value.filter(
    (item) => {
      if (
        !filters.includeArchived &&
        item.archived_at
      ) {
        return false
      }

      if (
        filters.status &&
        item.status !== filters.status
      ) {
        return false
      }

      const connectionState =
        getConnectionState(item)

      if (
        filters.connection &&
        connectionState !== filters.connection
      ) {
        return false
      }

      if (!term) {
        return true
      }

      const haystack = [
        item.code,
        item.name,
        item.hostname,
        item.customer_name,
        item.branch_name,
        item.device_identifier,
        item.agent_version,
        item.operating_system,
        item.ip_address,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()

      return haystack.includes(term)
    }
  )
})


const statistics = computed(() => {
  const visibleAgents =
    agents.value.filter(
      (item) => !item.archived_at
    )

  const total =
    visibleAgents.length

  const active =
    visibleAgents.filter(
      (item) =>
        item.status === "active"
    ).length

  const offline =
    visibleAgents.filter(
      (item) =>
        getConnectionState(item) ===
        "offline"
    ).length

  const errors =
    visibleAgents.filter(
      (item) =>
        item.status === "error"
    ).length

  const pending =
    visibleAgents.filter(
      (item) =>
        item.status === "pending"
    ).length

  return {
    total,
    active,
    offline,
    errors,
    pending,
  }
})


function clearMessages() {
  error.value = ""
  success.value = ""
}


function showSuccess(message) {
  error.value = ""
  success.value = message

  window.setTimeout(
    () => {
      if (
        success.value === message
      ) {
        success.value = ""
      }
    },
    5000
  )
}


function formatDate(value) {
  if (!value) {
    return "Nunca"
  }

  const date = new Date(value)

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return String(value)
  }

  return new Intl.DateTimeFormat(
    "es-PE",
    {
      dateStyle: "short",
      timeStyle: "short",
    }
  ).format(date)
}


function formatFullDate(value) {
  if (!value) {
    return "Nunca"
  }

  const date = new Date(value)

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return String(value)
  }

  return new Intl.DateTimeFormat(
    "es-PE",
    {
      dateStyle: "medium",
      timeStyle: "short",
    }
  ).format(date)
}


function getRelativeTime(value) {
  if (!value) {
    return "Nunca conectado"
  }

  const date = new Date(value)

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return "Fecha desconocida"
  }

  const difference =
    Date.now() - date.getTime()

  const minutes =
    Math.floor(
      difference / 60000
    )

  if (minutes < 1) {
    return "Hace menos de un minuto"
  }

  if (minutes < 60) {
    return `Hace ${minutes} min`
  }

  const hours =
    Math.floor(
      minutes / 60
    )

  if (hours < 24) {
    return `Hace ${hours} h`
  }

  const days =
    Math.floor(
      hours / 24
    )

  return `Hace ${days} d`
}


function getConnectionState(item) {
  if (!item.last_seen_at) {
    return "never"
  }

  const date =
    new Date(item.last_seen_at)

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return "offline"
  }

  const differenceMinutes =
    (
      Date.now() -
      date.getTime()
    ) / 60000

  if (
    item.status === "active" &&
    differenceMinutes <= 15
  ) {
    return "online"
  }

  return "offline"
}


function getConnectionLabel(item) {
  const state =
    getConnectionState(item)

  if (state === "online") {
    return "Conectado"
  }

  if (state === "never") {
    return "Nunca conectado"
  }

  return "Desconectado"
}


function getConnectionClass(item) {
  return (
    `connection-${getConnectionState(
      item
    )}`
  )
}


function getAgentInitials(item) {
  const source =
    item.name ||
    item.code ||
    "AG"

  return source
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map(
      (part) =>
        part.charAt(0).toUpperCase()
    )
    .join("")
}


function clearFilters() {
  filters.search = ""
  filters.status = ""
  filters.connection = ""
  filters.includeArchived = false
}


function openAgent(item) {
  router.push(
    `/monitoreo/agentes/${item.id}`
  )
}


async function loadAgents() {
  loading.value = true
  error.value = ""

  try {
    const data =
      await getAgents({
        include_archived: true,
      })

    agents.value =
      normalizeList(data)
  } catch (exception) {
    error.value =
      exception.message
  } finally {
    loading.value = false
  }
}


function openArchiveModal(item) {
  selectedAgent.value = item

  archiveReason.value =
    "Archivado desde Copier OS"

  showArchiveModal.value = true
}


function closeArchiveModal() {
  if (processingId.value) {
    return
  }

  showArchiveModal.value = false
  selectedAgent.value = null
  archiveReason.value = ""
}


async function confirmArchive() {
  if (!selectedAgent.value) {
    return
  }

  processingId.value =
    selectedAgent.value.id

  clearMessages()

  try {
    await archiveAgent(
      selectedAgent.value.id,
      archiveReason.value.trim()
    )

    closeArchiveModal()

    showSuccess(
      "Agente archivado correctamente."
    )

    await loadAgents()
  } catch (exception) {
    error.value =
      exception.message
  } finally {
    processingId.value = ""
  }
}


async function restoreSelectedAgent(item) {
  processingId.value = item.id

  clearMessages()

  try {
    await restoreAgent(
      item.id
    )

    showSuccess(
      "Agente restaurado correctamente."
    )

    await loadAgents()
  } catch (exception) {
    error.value =
      exception.message
  } finally {
    processingId.value = ""
  }
}


onMounted(
  loadAgents
)
</script>

<template>
  <section class="monitoring-agents-page">
    <header class="agents-page-header">
      <div>
        <span class="agents-page-eyebrow">
          Monitoreo
        </span>

        <h1 class="agents-page-title">
          Agentes de monitoreo
        </h1>

        <p class="agents-page-subtitle">
          Controla las instalaciones activas dentro de las
          redes de cada cliente y revisa su última conexión.
        </p>
      </div>

      <div class="agents-header-actions">
        <button
          class="agents-button agents-button-secondary"
          type="button"
          :disabled="loading"
          @click="loadAgents"
        >
          <span>↻</span>

          {{
            loading
              ? "Actualizando..."
              : "Actualizar"
          }}
        </button>
      </div>
    </header>

    <MonitoringTabs />

    <div
      v-if="error"
      class="agents-message agents-message-error"
    >
      <span>{{ error }}</span>

      <button
        type="button"
        @click="error = ''"
      >
        ×
      </button>
    </div>

    <div
      v-if="success"
      class="agents-message agents-message-success"
    >
      <span>{{ success }}</span>

      <button
        type="button"
        @click="success = ''"
      >
        ×
      </button>
    </div>

    <section class="agents-statistics-grid">
      <article class="agent-stat-card">
        <span>Total</span>

        <strong>
          {{ statistics.total }}
        </strong>

        <small>
          Agentes registrados
        </small>
      </article>

      <article class="agent-stat-card agent-stat-active">
        <span>Activos</span>

        <strong>
          {{ statistics.active }}
        </strong>

        <small>
          Funcionando normalmente
        </small>
      </article>

      <article class="agent-stat-card agent-stat-offline">
        <span>Sin conexión</span>

        <strong>
          {{ statistics.offline }}
        </strong>

        <small>
          Requieren revisión
        </small>
      </article>

      <article class="agent-stat-card agent-stat-error">
        <span>Con error</span>

        <strong>
          {{ statistics.errors }}
        </strong>

        <small>
          Presentan incidencias
        </small>
      </article>

      <article class="agent-stat-card agent-stat-pending">
        <span>Pendientes</span>

        <strong>
          {{ statistics.pending }}
        </strong>

        <small>
          Instalación incompleta
        </small>
      </article>
    </section>

    <article class="agents-panel">
      <header class="agents-panel-header">
        <div>
          <span class="agents-panel-kicker">
            Instalaciones
          </span>

          <h2>
            Agentes registrados
          </h2>

          <p>
            Busca por cliente, sede, código, hostname
            o identificador del dispositivo.
          </p>
        </div>

        <span class="agents-result-count">
          {{ filteredAgents.length }}
          resultados
        </span>
      </header>

      <div class="agents-toolbar">
        <label class="agents-search-field">
          <span>⌕</span>

          <input
            v-model.trim="filters.search"
            type="search"
            placeholder="Buscar agente, cliente, sede, hostname..."
          />
        </label>

        <label class="agents-filter-field">
          <span>Estado</span>

          <select
            v-model="filters.status"
          >
            <option
              v-for="option in statusOptions"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </label>

        <label class="agents-filter-field">
          <span>Conexión</span>

          <select
            v-model="filters.connection"
          >
            <option
              v-for="option in connectionOptions"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </label>

        <label class="agents-archived-filter">
          <input
            v-model="filters.includeArchived"
            type="checkbox"
          />

          <span>
            Mostrar archivados
          </span>
        </label>

        <button
          class="agents-clear-filters"
          type="button"
          @click="clearFilters"
        >
          Limpiar
        </button>
      </div>

      <div
        v-if="loading"
        class="agents-loading"
      >
        <div class="agents-spinner"></div>

        <span>
          Cargando agentes...
        </span>
      </div>

      <template
        v-else-if="filteredAgents.length"
      >
        <div class="agents-card-grid">
          <article
            v-for="agent in filteredAgents"
            :key="agent.id"
            class="agent-card"
            :class="{
              'agent-card-archived':
                agent.archived_at,
            }"
          >
            <header class="agent-card-header">
              <button
                class="agent-avatar"
                type="button"
                @click="openAgent(agent)"
              >
                {{
                  getAgentInitials(agent)
                }}
              </button>

              <div class="agent-card-title">
                <RouterLink
                  :to="`/monitoreo/agentes/${agent.id}`"
                >
                  {{
                    agent.name ||
                    agent.code
                  }}
                </RouterLink>

                <span>
                  {{ agent.code }}
                </span>
              </div>

              <div class="agent-card-badges">
                <MonitoringStatusBadge
                  :status="agent.status"
                  :label="
                    agent.status_display ||
                    agent.status
                  "
                />

                <span
                  v-if="agent.archived_at"
                  class="agent-archived-badge"
                >
                  Archivado
                </span>
              </div>
            </header>

            <div class="agent-customer-section">
              <div>
                <span>Cliente</span>

                <strong>
                  {{
                    agent.customer_name ||
                    agent.customer ||
                    "Sin cliente"
                  }}
                </strong>
              </div>

              <div>
                <span>Sede</span>

                <strong>
                  {{
                    agent.branch_name ||
                    agent.branch ||
                    "Sin sede específica"
                  }}
                </strong>
              </div>
            </div>

            <div class="agent-connection-row">
              <div
                class="agent-connection-indicator"
                :class="
                  getConnectionClass(
                    agent
                  )
                "
              ></div>

              <div>
                <strong>
                  {{
                    getConnectionLabel(
                      agent
                    )
                  }}
                </strong>

                <span
                  :title="
                    formatFullDate(
                      agent.last_seen_at
                    )
                  "
                >
                  {{
                    getRelativeTime(
                      agent.last_seen_at
                    )
                  }}
                </span>
              </div>
            </div>

            <div class="agent-information-grid">
              <div>
                <span>Hostname</span>

                <strong>
                  {{
                    agent.hostname ||
                    "—"
                  }}
                </strong>
              </div>

              <div>
                <span>Versión</span>

                <strong>
                  {{
                    agent.agent_version ||
                    "—"
                  }}
                </strong>
              </div>

              <div>
                <span>Dispositivo</span>

                <strong>
                  {{
                    agent.device_identifier ||
                    "—"
                  }}
                </strong>
              </div>

              <div>
                <span>Última sincronización</span>

                <strong>
                  {{
                    formatDate(
                      agent.last_sync_at ||
                      agent.last_seen_at
                    )
                  }}
                </strong>
              </div>
            </div>

            <div
              v-if="
                agent.last_error_message ||
                agent.error_message
              "
              class="agent-error-summary"
            >
              <strong>
                Último error
              </strong>

              <p>
                {{
                  agent.last_error_message ||
                  agent.error_message
                }}
              </p>
            </div>

            <footer class="agent-card-footer">
              <button
                class="agent-card-action agent-card-action-primary"
                type="button"
                @click="openAgent(agent)"
              >
                Ver detalle
              </button>

              <button
                v-if="!agent.archived_at"
                class="agent-card-action"
                type="button"
                :disabled="
                  processingId === agent.id
                "
                @click="openArchiveModal(agent)"
              >
                Archivar
              </button>

              <button
                v-else
                class="agent-card-action agent-card-action-restore"
                type="button"
                :disabled="
                  processingId === agent.id
                "
                @click="
                  restoreSelectedAgent(
                    agent
                  )
                "
              >
                {{
                  processingId === agent.id
                    ? "Restaurando..."
                    : "Restaurar"
                }}
              </button>
            </footer>
          </article>
        </div>

        <div class="agents-table-wrap">
          <table class="agents-table">
            <thead>
              <tr>
                <th>Agente</th>
                <th>Cliente / sede</th>
                <th>Hostname</th>
                <th>Versión</th>
                <th>Estado</th>
                <th>Conexión</th>
                <th>Última conexión</th>
                <th></th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="agent in filteredAgents"
                :key="`table-${agent.id}`"
                :class="{
                  'agent-row-archived':
                    agent.archived_at,
                }"
              >
                <td>
                  <div class="agent-table-name">
                    <RouterLink
                      :to="`/monitoreo/agentes/${agent.id}`"
                    >
                      {{
                        agent.name ||
                        agent.code
                      }}
                    </RouterLink>

                    <span>
                      {{ agent.code }}
                    </span>
                  </div>
                </td>

                <td>
                  <div class="agent-table-owner">
                    <strong>
                      {{
                        agent.customer_name ||
                        agent.customer ||
                        "—"
                      }}
                    </strong>

                    <span>
                      {{
                        agent.branch_name ||
                        agent.branch ||
                        "Sin sede"
                      }}
                    </span>
                  </div>
                </td>

                <td>
                  {{
                    agent.hostname ||
                    "—"
                  }}
                </td>

                <td>
                  {{
                    agent.agent_version ||
                    "—"
                  }}
                </td>

                <td>
                  <MonitoringStatusBadge
                    :status="agent.status"
                    :label="
                      agent.status_display ||
                      agent.status
                    "
                  />
                </td>

                <td>
                  <span
                    class="agent-connection-badge"
                    :class="
                      getConnectionClass(
                        agent
                      )
                    "
                  >
                    {{
                      getConnectionLabel(
                        agent
                      )
                    }}
                  </span>
                </td>

                <td>
                  <div class="agent-table-date">
                    <strong>
                      {{
                        formatDate(
                          agent.last_seen_at
                        )
                      }}
                    </strong>

                    <span>
                      {{
                        getRelativeTime(
                          agent.last_seen_at
                        )
                      }}
                    </span>
                  </div>
                </td>

                <td>
                  <button
                    class="agent-table-detail"
                    type="button"
                    @click="openAgent(agent)"
                  >
                    Abrir
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <MonitoringEmptyState
        v-else
        title="Sin agentes"
        message="No se encontraron agentes con los filtros actuales."
      />
    </article>

    <div
      v-if="showArchiveModal"
      class="agent-modal-backdrop"
      @click.self="closeArchiveModal"
    >
      <section class="agent-modal">
        <header class="agent-modal-header">
          <div>
            <h2>
              Archivar agente
            </h2>

            <p>
              {{
                selectedAgent?.name ||
                selectedAgent?.code
              }}
            </p>
          </div>

          <button
            type="button"
            @click="closeArchiveModal"
          >
            ×
          </button>
        </header>

        <div class="agent-modal-body">
          <div class="agent-modal-warning">
            El agente dejará de aparecer entre las
            instalaciones activas, pero conservará su historial.
          </div>

          <label class="agent-modal-field">
            <span>
              Motivo de archivado
            </span>

            <textarea
              v-model.trim="archiveReason"
              rows="4"
              placeholder="Indica el motivo..."
            ></textarea>
          </label>
        </div>

        <footer class="agent-modal-footer">
          <button
            class="agents-button agents-button-secondary"
            type="button"
            :disabled="Boolean(processingId)"
            @click="closeArchiveModal"
          >
            Cancelar
          </button>

          <button
            class="agents-button agents-button-warning"
            type="button"
            :disabled="Boolean(processingId)"
            @click="confirmArchive"
          >
            {{
              processingId
                ? "Archivando..."
                : "Archivar agente"
            }}
          </button>
        </footer>
      </section>
    </div>
  </section>
</template>