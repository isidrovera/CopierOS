<script setup>
import {
  onMounted,
  ref,
} from "vue"

import {
  useRoute,
} from "vue-router"

import MonitoringStatusBadge from "../../components/monitoring/MonitoringStatusBadge.vue"
import MonitoringTabs from "../../components/monitoring/MonitoringTabs.vue"

import {
  getAgent,
  getDevices,
  getNetworks,
  normalizeList,
} from "../../services/monitoring.service"

import "./monitoring.css"


const route = useRoute()

const loading = ref(true)
const error = ref("")
const agent = ref(null)
const networks = ref([])
const devices = ref([])


async function loadData() {
  loading.value = true
  error.value = ""

  try {
    const [
      agentData,
      networkData,
      deviceData,
    ] = await Promise.all([
      getAgent(route.params.id),
      getNetworks({
        agent: route.params.id,
      }),
      getDevices({
        agent: route.params.id,
      }),
    ])

    agent.value = agentData
    networks.value = normalizeList(
      networkData
    )
    devices.value = normalizeList(
      deviceData
    )
  } catch (exception) {
    error.value = exception.message
  } finally {
    loading.value = false
  }
}


function formatDate(value) {
  if (!value) {
    return "Nunca"
  }

  return new Intl.DateTimeFormat(
    "es-PE",
    {
      dateStyle: "medium",
      timeStyle: "short",
    }
  ).format(
    new Date(value)
  )
}


onMounted(loadData)
</script>

<template>
  <section class="monitoring-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">
          {{ agent?.name || "Detalle del agente" }}
        </h1>
        <p class="page-subtitle">
          {{ agent?.code || route.params.id }}
        </p>
      </div>

      <RouterLink
        class="button secondary"
        to="/monitoreo/agentes"
      >
        Volver
      </RouterLink>
    </div>

    <MonitoringTabs />

    <div
      v-if="error"
      class="error-box"
    >
      {{ error }}
    </div>

    <div
      v-if="loading"
      class="panel loading"
    >
      Cargando agente...
    </div>

    <template v-else-if="agent">
      <article class="panel">
        <div class="panel-header">
          <h2 class="panel-title">
            Información general
          </h2>

          <MonitoringStatusBadge
            :status="agent.status"
            :label="agent.status_display"
          />
        </div>

        <div class="detail-grid">
          <div class="detail-item">
            <span>Cliente</span>
            <strong>{{ agent.customer_name }}</strong>
          </div>
          <div class="detail-item">
            <span>Sede</span>
            <strong>{{ agent.branch_name || "Sin sede" }}</strong>
          </div>
          <div class="detail-item">
            <span>Hostname</span>
            <strong>{{ agent.hostname || "—" }}</strong>
          </div>
          <div class="detail-item">
            <span>Identificador</span>
            <strong>{{ agent.device_identifier }}</strong>
          </div>
          <div class="detail-item">
            <span>IP local</span>
            <strong>{{ agent.local_ip_address || "—" }}</strong>
          </div>
          <div class="detail-item">
            <span>Última conexión</span>
            <strong>{{ formatDate(agent.last_seen_at) }}</strong>
          </div>
          <div class="detail-item">
            <span>Versión</span>
            <strong>{{ agent.agent_version || "—" }}</strong>
          </div>
          <div class="detail-item">
            <span>Sistema operativo</span>
            <strong>{{ agent.operating_system_display }}</strong>
          </div>
          <div class="detail-item">
            <span>Configuración</span>
            <strong>v{{ agent.configuration_version }}</strong>
          </div>
        </div>
      </article>

      <article class="panel">
        <div class="panel-header">
          <h2 class="panel-title">
            Redes asignadas
          </h2>
          <strong>{{ networks.length }}</strong>
        </div>

        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>CIDR</th>
                <th>Método</th>
                <th>Activa</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="network in networks"
                :key="network.id"
              >
                <td>{{ network.name }}</td>
                <td>{{ network.cidr }}</td>
                <td>
                  {{ network.discovery_method_display }}
                </td>
                <td>
                  {{ network.is_enabled ? "Sí" : "No" }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <article class="panel">
        <div class="panel-header">
          <h2 class="panel-title">
            Dispositivos
          </h2>
          <strong>{{ devices.length }}</strong>
        </div>

        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Código</th>
                <th>Modelo</th>
                <th>IP</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="device in devices"
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
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </template>
  </section>
</template>
