<script setup>
import {
  computed,
  onMounted,
  ref,
} from "vue"

import MonitoringEmptyState from "../../components/monitoring/MonitoringEmptyState.vue"
import MonitoringMetricCard from "../../components/monitoring/MonitoringMetricCard.vue"
import MonitoringStatusBadge from "../../components/monitoring/MonitoringStatusBadge.vue"
import MonitoringTabs from "../../components/monitoring/MonitoringTabs.vue"

import {
  getDashboardData,
} from "../../services/monitoring.service"

import "./monitoring.css"


const loading = ref(true)
const error = ref("")
const data = ref({
  agents: [],
  devices: [],
  alerts: [],
  snapshots: [],
  networks: [],
})


const activeAgents = computed(
  () => data.value.agents.filter(
    item => item.status === "active"
  ).length
)

const offlineAgents = computed(
  () => data.value.agents.filter(
    item => item.status === "offline"
  ).length
)

const problemDevices = computed(
  () => data.value.devices.filter(
    item => [
      "warning",
      "error",
      "offline",
      "blocked",
    ].includes(item.status)
  ).length
)

const activeAlerts = computed(
  () => data.value.alerts.filter(
    item => ![
      "resolved",
      "closed",
    ].includes(item.status)
  ).length
)


async function loadData() {
  loading.value = true
  error.value = ""

  try {
    data.value = await getDashboardData()
  } catch (exception) {
    error.value = exception.message
  } finally {
    loading.value = false
  }
}


onMounted(loadData)
</script>

<template>
  <section class="monitoring-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">
          Monitoreo
        </h1>
        <p class="page-subtitle">
          Agentes, redes, dispositivos y lecturas SNMP.
        </p>
      </div>

      <button
        class="button secondary"
        type="button"
        :disabled="loading"
        @click="loadData"
      >
        Actualizar
      </button>
    </div>

    <MonitoringTabs />

    <div
      v-if="error"
      class="error-box"
    >
      {{ error }}
    </div>

    <div class="metrics-grid">
      <MonitoringMetricCard
        label="Agentes activos"
        :value="activeAgents"
        tone="green"
      />
      <MonitoringMetricCard
        label="Agentes sin conexión"
        :value="offlineAgents"
        tone="red"
      />
      <MonitoringMetricCard
        label="Dispositivos"
        :value="data.devices.length"
        tone="blue"
      />
      <MonitoringMetricCard
        label="Equipos con problemas"
        :value="problemDevices"
        tone="amber"
      />
      <MonitoringMetricCard
        label="Alertas activas"
        :value="activeAlerts"
        tone="red"
      />
    </div>

    <div
      v-if="loading"
      class="panel loading"
    >
      Cargando información...
    </div>

    <template v-else>
      <article class="panel">
        <div class="panel-header">
          <h2 class="panel-title">
            Últimos dispositivos
          </h2>

          <RouterLink
            class="link"
            to="/monitoreo/dispositivos"
          >
            Ver todos
          </RouterLink>
        </div>

        <div
          v-if="data.devices.length"
          class="table-wrap"
        >
          <table class="data-table">
            <thead>
              <tr>
                <th>Código</th>
                <th>Equipo</th>
                <th>IP</th>
                <th>Estado</th>
                <th>Contador</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="device in data.devices.slice(0, 8)"
                :key="device.id"
              >
                <td>
                  <RouterLink
                    class="link"
                    :to="`/monitoreo/dispositivos/${device.id}`"
                  >
                    {{ device.code }}
                  </RouterLink>
                </td>
                <td>
                  {{ device.raw_brand_name }}
                  {{ device.raw_model_name }}
                </td>
                <td>{{ device.ip_address }}</td>
                <td>
                  <MonitoringStatusBadge
                    :status="device.status"
                    :label="device.status_display"
                  />
                </td>
                <td>
                  {{ device.current_total_meter ?? "—" }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <MonitoringEmptyState
          v-else
          title="Sin dispositivos"
          message="Todavía no existen dispositivos monitoreados."
        />
      </article>
    </template>
  </section>
</template>
