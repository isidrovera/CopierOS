<script setup>
import { computed, onMounted, reactive, ref } from "vue"
import { useRouter } from "vue-router"

import {
  archiveServiceOrder,
  getServiceOrders,
  restoreServiceOrder,
} from "../../services/services.service"

import ServicesTabs from "./ServicesTabs.vue"

import "./services.css"

const router = useRouter()
const orders = ref([])
const loading = ref(false)
const error = ref("")
const filters = reactive({
  search: "",
  status: "",
  priority: "",
  service_type: "",
  assigned_technician: "",
  requires_return_visit: "",
  archived: "",
})

const statusOptions = [
  ["draft", "Borrador"],
  ["pending_assignment", "Pendiente de asignación"],
  ["assigned", "Asignada"],
  ["accepted", "Aceptada"],
  ["en_route", "En ruta"],
  ["on_site", "En ubicación"],
  ["in_progress", "En proceso"],
  ["pending_parts", "Pendiente de repuestos"],
  ["requires_return", "Requiere retorno"],
  ["technician_completed", "Finalizada por técnico"],
  ["pending_conformity", "Pendiente de conformidad"],
  ["closed", "Cerrada"],
  ["rescheduled", "Reprogramada"],
  ["failed_visit", "Visita no realizada"],
  ["cancelled", "Cancelada"],
]

const stats = computed(() => ({
  total: orders.value.length,
  pending: orders.value.filter((item) => ["draft", "pending_assignment", "assigned"].includes(item.status)).length,
  active: orders.value.filter((item) => ["accepted", "en_route", "on_site", "in_progress"].includes(item.status)).length,
  parts: orders.value.filter((item) => item.status === "pending_parts").length,
}))

function normalize(data) {
  if (Array.isArray(data)) return data
  return Array.isArray(data?.results) ? data.results : []
}

async function loadOrders() {
  loading.value = true
  error.value = ""

  try {
    orders.value = normalize(await getServiceOrders(filters))
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loading.value = false
  }
}

function formatDate(value) {
  if (!value) return "Sin programar"
  return new Intl.DateTimeFormat("es-PE", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value))
}

function statusClass(status) {
  return `status-${status}`
}

async function toggleArchive(order) {
  try {
    if (order.archived_at) {
      await restoreServiceOrder(order.id)
    } else {
      const reason = window.prompt("Motivo de archivado:", "Registro duplicado o anulado")
      if (reason === null) return
      await archiveServiceOrder(order.id, reason)
    }

    await loadOrders()
  } catch (requestError) {
    error.value = requestError.message
  }
}

onMounted(loadOrders)
</script>

<template>
  <section class="services-page">
    <header class="services-header">
      <div>
        <span class="page-kicker">Servicio técnico de campo</span>
        <h2>Órdenes de servicio</h2>
        <p>Control por serie, técnico, cliente, checklist, evidencias y ruta.</p>
      </div>

      <button class="primary-button" type="button" @click="router.push({ name: 'service-order-create' })">
        + Nueva orden
      </button>
    </header>

    <ServicesTabs />

    <div class="services-stats">
      <article><small>Total visible</small><strong>{{ stats.total }}</strong></article>
      <article><small>Pendientes</small><strong>{{ stats.pending }}</strong></article>
      <article><small>En atención</small><strong>{{ stats.active }}</strong></article>
      <article><small>Esperando repuestos</small><strong>{{ stats.parts }}</strong></article>
    </div>

    <form class="services-filter-card" @submit.prevent="loadOrders">
      <input v-model="filters.search" type="search" placeholder="Código, serie, cliente, sede o dirección">

      <select v-model="filters.status">
        <option value="">Todos los estados</option>
        <option v-for="item in statusOptions" :key="item[0]" :value="item[0]">{{ item[1] }}</option>
      </select>

      <select v-model="filters.priority">
        <option value="">Todas las prioridades</option>
        <option value="low">Baja</option>
        <option value="normal">Normal</option>
        <option value="high">Alta</option>
        <option value="urgent">Urgente</option>
      </select>

      <select v-model="filters.service_type">
        <option value="">Todos los tipos</option>
        <option value="preventive">Preventivo</option>
        <option value="corrective">Correctivo</option>
        <option value="network">Red y configuración</option>
        <option value="meter_reading">Lectura de contadores</option>
        <option value="inspection">Inspección</option>
        <option value="other">Otro</option>
      </select>

      <select v-model="filters.archived">
        <option value="">Activas</option>
        <option value="all">Todas</option>
        <option value="true">Archivadas</option>
      </select>

      <button class="secondary-button" type="submit">Buscar</button>
    </form>

    <p v-if="error" class="message error-message">{{ error }}</p>

    <div v-if="loading" class="loading-card">
      <span class="spinner"></span>
      Cargando órdenes...
    </div>

    <div v-else class="services-table-card">
      <table class="services-table">
        <thead>
          <tr>
            <th>Orden</th>
            <th>Equipo</th>
            <th>Cliente / sede</th>
            <th>Técnico</th>
            <th>Programación</th>
            <th>Estado</th>
            <th>Prioridad</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id">
            <td>
              <button class="table-link" type="button" @click="router.push({ name: 'service-order-detail', params: { id: order.id } })">
                {{ order.code }}
              </button>
              <small>{{ order.service_type_display }}</small>
            </td>
            <td>
              <strong>{{ order.equipment_serial_number }}</strong>
              <small>{{ order.equipment_brand_name }} {{ order.equipment_model_name }}</small>
            </td>
            <td>
              <strong>{{ order.customer_name }}</strong>
              <small>{{ order.branch_name || order.address }}</small>
            </td>
            <td>{{ order.technician_display || "Sin asignar" }}</td>
            <td>{{ formatDate(order.scheduled_at) }}</td>
            <td><span class="status-badge" :class="statusClass(order.status)">{{ order.status_display }}</span></td>
            <td><span class="priority-badge" :class="`priority-${order.priority}`">{{ order.priority_display }}</span></td>
            <td class="row-actions">
              <button type="button" @click="router.push({ name: 'service-order-detail', params: { id: order.id } })">Ver</button>
              <button type="button" @click="router.push({ name: 'service-order-edit', params: { id: order.id } })">Editar</button>
              <button type="button" @click="toggleArchive(order)">{{ order.archived_at ? "Restaurar" : "Archivar" }}</button>
            </td>
          </tr>
          <tr v-if="!orders.length">
            <td colspan="8" class="empty-table">No se encontraron órdenes.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
