<script setup>
import {
  onMounted,
  ref,
} from "vue"

import MonitoringEmptyState from "../../components/monitoring/MonitoringEmptyState.vue"
import MonitoringTabs from "../../components/monitoring/MonitoringTabs.vue"

import {
  getSnapshots,
  normalizeList,
} from "../../services/monitoring.service"

import "./monitoring.css"


const loading = ref(true)
const error = ref("")
const items = ref([])


function formatValue(value) {
  if (
    value === true ||
    value === false
  ) {
    return value ? "Sí" : "No"
  }

  return (
    value === null ||
    value === undefined ||
    value === ""
  )
    ? "—"
    : value
}


async function loadItems() {
  loading.value = true
  error.value = ""

  try {
    items.value = normalizeList(
      await getSnapshots()
    )
  } catch (exception) {
    error.value = exception.message
  } finally {
    loading.value = false
  }
}


onMounted(loadItems)
</script>

<template>
  <section class="monitoring-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">
          Capturas de dispositivos
        </h1>
        <p class="page-subtitle">
          Historial recibido desde los agentes.
        </p>
      </div>

      <button
        class="button secondary"
        type="button"
        @click="loadItems"
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
      <div
        v-if="loading"
        class="loading"
      >
        Cargando...
      </div>

      <div
        v-else-if="items.length"
        class="table-wrap"
      >
        <table class="data-table">
          <thead>
            <tr>
              <th>ID agente</th>
<th>Dispositivo</th>
<th>Capturada</th>
<th>Conexión</th>
<th>Contador total</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in items"
              :key="item.id"
            >
              <td>{{ formatValue(item.agent_snapshot_id) }}</td>
<td>{{ formatValue(item.device) }}</td>
<td>{{ formatValue(item.captured_at) }}</td>
<td>{{ formatValue(item.connection_status) }}</td>
<td>{{ formatValue(item.total_meter) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <MonitoringEmptyState
        v-else
        title="Sin registros"
      />
    </article>
  </section>
</template>
