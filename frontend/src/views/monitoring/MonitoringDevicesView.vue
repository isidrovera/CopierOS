<script setup>
import {
  computed,
  onMounted,
  ref,
} from "vue"

import MonitoringEmptyState from "../../components/monitoring/MonitoringEmptyState.vue"
import MonitoringStatusBadge from "../../components/monitoring/MonitoringStatusBadge.vue"
import MonitoringTabs from "../../components/monitoring/MonitoringTabs.vue"

import {
  getDevices,
  normalizeList,
} from "../../services/monitoring.service"

import "./monitoring.css"


const loading = ref(true)
const error = ref("")
const search = ref("")
const devices = ref([])


const filteredDevices = computed(() => {
  const term = search.value
    .trim()
    .toLowerCase()

  if (!term) {
    return devices.value
  }

  return devices.value.filter(
    item => [
      item.code,
      item.ip_address,
      item.hostname,
      item.raw_brand_name,
      item.raw_model_name,
      item.raw_serial_number,
      item.agent_code,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase()
      .includes(term)
  )
})


async function loadDevices() {
  loading.value = true
  error.value = ""

  try {
    devices.value = normalizeList(
      await getDevices()
    )
  } catch (exception) {
    error.value = exception.message
  } finally {
    loading.value = false
  }
}


onMounted(loadDevices)
</script>

<template>
  <section class="monitoring-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">
          Dispositivos monitoreados
        </h1>
        <p class="page-subtitle">
          Impresoras, copiadoras y multifuncionales detectados.
        </p>
      </div>

      <button
        class="button secondary"
        type="button"
        @click="loadDevices"
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

    <article class="panel">
      <div class="panel-header">
        <h2 class="panel-title">
          {{ filteredDevices.length }} dispositivos
        </h2>

        <input
          v-model="search"
          class="input"
          type="search"
          placeholder="Buscar equipo..."
        />
      </div>

      <div
        v-if="loading"
        class="loading"
      >
        Cargando dispositivos...
      </div>

      <div
        v-else-if="filteredDevices.length"
        class="table-wrap"
      >
        <table class="data-table">
          <thead>
            <tr>
              <th>Código</th>
              <th>Marca / modelo</th>
              <th>Serie</th>
              <th>IP</th>
              <th>Agente</th>
              <th>Estado</th>
              <th>Contador</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="device in filteredDevices"
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
              <td>
                {{ device.raw_serial_number || "—" }}
              </td>
              <td>{{ device.ip_address }}</td>
              <td>{{ device.agent_code }}</td>
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
      />
    </article>
  </section>
</template>
