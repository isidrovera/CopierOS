<script setup>
import {
  computed,
  onMounted,
  ref,
  watch,
} from "vue"

import {
  useRouter,
} from "vue-router"

import {
  archiveRentalResource,
  listRentalResource,
  restoreRentalResource,
} from "../../services/rentals.service"

import RentalsTabs from "./RentalsTabs.vue"

import "./rental-resource-list.css"


const props = defineProps({
  title: String,
  subtitle: String,
  resource: String,
  columns: Array,
  createRoute: String,
  editRoute: String,
  filters: {
    type: Array,
    default: () => [],
  },
})

const router = useRouter()

const items = ref([])
const loading = ref(false)
const errorMessage = ref("")
const successMessage = ref("")
const search = ref("")
const includeArchived = ref(false)
const filterValues = ref({})

const rows = computed(() => items.value)

const activeCount = computed(() => (
  items.value.filter((item) => !item.is_archived).length
))

const archivedCount = computed(() => (
  items.value.filter((item) => item.is_archived).length
))


function columnValue(item, column) {
  const alternative = column.keys
    ?.map((key) => item[key])
    .find(
      (value) => (
        value !== undefined &&
        value !== null &&
        value !== ""
      ),
    )

  const raw = alternative ?? item[column.key]

  if (column.type === "date" && raw) {
    return new Date(raw).toLocaleDateString("es-PE")
  }

  if (typeof raw === "boolean") {
    return raw ? "Sí" : "No"
  }

  return raw ?? "—"
}


function badgeClass(item, column) {
  const raw = String(item[column.key] || "")

  if ([
    "active",
    "installed",
    "ready_for_rental",
    "approved",
    "completed",
    "available",
  ].includes(raw)) {
    return "good"
  }

  if ([
    "cancelled",
    "with_problems",
    "failed",
    "rejected",
    "for_parts",
  ].includes(raw)) {
    return "bad"
  }

  return "warn"
}


function normalizeResponse(response) {
  if (Array.isArray(response)) {
    return response
  }

  if (Array.isArray(response?.results)) {
    return response.results
  }

  if (Array.isArray(response?.data)) {
    return response.data
  }

  if (Array.isArray(response?.data?.results)) {
    return response.data.results
  }

  return []
}


function errorText(error) {
  if (typeof error?.response?.data?.detail === "string") {
    return error.response.data.detail
  }

  if (typeof error?.response?.data?.message === "string") {
    return error.response.data.message
  }

  if (typeof error?.message === "string") {
    return error.message
  }

  return "Ocurrió un error al procesar la solicitud."
}


async function loadRecords() {
  loading.value = true
  errorMessage.value = ""

  try {
    const response = await listRentalResource(
      props.resource,
      {
        search: search.value,
        include_archived: includeArchived.value
          ? "true"
          : "",
        ...filterValues.value,
      },
    )

    items.value = normalizeResponse(response)
  } catch (error) {
    items.value = []
    errorMessage.value = errorText(error)
  } finally {
    loading.value = false
  }
}


async function archiveRecord(item) {
  successMessage.value = ""
  errorMessage.value = ""

  const reason = window.prompt(
    "Indica el motivo de archivado:",
  )

  if (reason === null) {
    return
  }

  try {
    await archiveRentalResource(
      props.resource,
      item.id,
      reason,
    )

    successMessage.value = "Registro archivado correctamente."

    await loadRecords()
  } catch (error) {
    errorMessage.value = errorText(error)
  }
}


async function restoreRecord(item) {
  successMessage.value = ""
  errorMessage.value = ""

  try {
    await restoreRentalResource(
      props.resource,
      item.id,
    )

    successMessage.value = "Registro restaurado correctamente."

    await loadRecords()
  } catch (error) {
    errorMessage.value = errorText(error)
  }
}


function openCreate() {
  if (!props.createRoute) {
    return
  }

  router.push({
    name: props.createRoute,
  })
}


function openEdit(item) {
  if (!props.editRoute) {
    return
  }

  router.push({
    name: props.editRoute,
    params: {
      id: item.id,
    },
  })
}


let searchTimer = null

watch(search, () => {
  clearTimeout(searchTimer)

  searchTimer = setTimeout(
    loadRecords,
    350,
  )
})

watch(includeArchived, loadRecords)

watch(
  () => props.resource,
  () => {
    search.value = ""
    includeArchived.value = false
    filterValues.value = {}
    successMessage.value = ""
    errorMessage.value = ""

    loadRecords()
  },
)

onMounted(loadRecords)
</script>

<template>
  <section class="rental-resource-page">
    <RentalsTabs />

    <header class="resource-header">
      <div class="resource-header__content">
        <span class="resource-header__eyebrow">
          Gestión de alquileres
        </span>

        <h1>{{ title }}</h1>

        <p>{{ subtitle }}</p>
      </div>

      <div class="resource-header__actions">
        <button
          type="button"
          class="resource-button resource-button--secondary"
          :disabled="loading"
          @click="loadRecords"
        >
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
            :class="{ spinning: loading }"
          >
            <path d="M20 11a8.1 8.1 0 0 0-15.5-2" />
            <path d="M4 4v5h5" />
            <path d="M4 13a8.1 8.1 0 0 0 15.5 2" />
            <path d="M20 20v-5h-5" />
          </svg>

          {{ loading ? "Actualizando" : "Actualizar" }}
        </button>

        <button
          v-if="createRoute"
          type="button"
          class="resource-button resource-button--primary"
          @click="openCreate"
        >
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M12 5v14" />
            <path d="M5 12h14" />
          </svg>

          Nuevo registro
        </button>
      </div>
    </header>

    <div class="resource-summary">
      <article class="resource-stat resource-stat--total">
        <div class="resource-stat__icon">
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M5 5h14v14H5z" />
            <path d="M9 9h6" />
            <path d="M9 13h6" />
            <path d="M9 17h4" />
          </svg>
        </div>

        <div>
          <span>Total mostrado</span>

          <strong>
            {{ rows.length }}
          </strong>
        </div>
      </article>

      <article class="resource-stat resource-stat--active">
        <div class="resource-stat__icon">
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              cx="12"
              cy="12"
              r="9"
            />

            <path d="m8 12 2.5 2.5L16 9" />
          </svg>
        </div>

        <div>
          <span>Activos</span>

          <strong>
            {{ activeCount }}
          </strong>
        </div>
      </article>

      <article class="resource-stat resource-stat--archived">
        <div class="resource-stat__icon">
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M4 7h16" />
            <path d="M6 7v13h12V7" />
            <path d="M9 11h6" />
            <path d="M5 3h14v4H5z" />
          </svg>
        </div>

        <div>
          <span>Archivados</span>

          <strong>
            {{ archivedCount }}
          </strong>
        </div>
      </article>
    </div>

    <div
      v-if="errorMessage"
      class="resource-message resource-message--error"
    >
      <svg
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path d="M12 9v4" />
        <path d="M12 17h.01" />
        <path
          d="
            M10.3 4.3
            2.9 17.1
            A2 2 0 0 0 4.6 20
            h14.8
            a2 2 0 0 0 1.7-2.9
            L13.7 4.3
            a2 2 0 0 0-3.4 0Z
          "
        />
      </svg>

      <span>{{ errorMessage }}</span>
    </div>

    <div
      v-if="successMessage"
      class="resource-message resource-message--success"
    >
      <svg
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle
          cx="12"
          cy="12"
          r="9"
        />

        <path d="m8 12 2.5 2.5L16 9" />
      </svg>

      <span>{{ successMessage }}</span>
    </div>

    <section class="resource-panel">
      <div class="resource-toolbar">
        <label class="resource-search">
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              cx="11"
              cy="11"
              r="7"
            />

            <path d="m20 20-4-4" />
          </svg>

          <input
            v-model="search"
            type="search"
            placeholder="Buscar por código, nombre, cliente, serie o modelo..."
          >
        </label>

        <select
          v-for="filter in filters"
          :key="filter.key"
          v-model="filterValues[filter.key]"
          class="resource-control"
          @change="loadRecords"
        >
          <option value="">
            {{ filter.label }}
          </option>

          <option
            v-for="option in filter.options"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>

        <label class="archive-control">
          <input
            v-model="includeArchived"
            type="checkbox"
          >

          <span class="archive-control__switch" />

          <span>Incluir archivados</span>
        </label>
      </div>

      <div class="resource-table-wrap">
        <table class="resource-table">
          <thead>
            <tr>
              <th
                v-for="column in columns"
                :key="column.key"
              >
                {{ column.label }}
              </th>

              <th class="resource-table__actions-heading">
                Acciones
              </th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="item in rows"
              :key="item.id"
              :class="{
                'resource-table__row--archived': item.is_archived,
              }"
            >
              <td
                v-for="column in columns"
                :key="column.key"
              >
                <span
                  v-if="column.badge"
                  class="resource-badge"
                  :class="badgeClass(item, column)"
                >
                  {{ columnValue(item, column) }}
                </span>

                <span
                  v-else
                  class="resource-cell-value"
                >
                  {{ columnValue(item, column) }}
                </span>
              </td>

              <td>
                <div class="resource-row-actions">
                  <button
                    v-if="editRoute"
                    type="button"
                    class="resource-icon-button resource-icon-button--edit"
                    title="Editar registro"
                    @click="openEdit(item)"
                  >
                    <svg
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path d="M12 20h9" />
                      <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z" />
                    </svg>

                    <span>Editar</span>
                  </button>

                  <button
                    v-if="!item.is_archived"
                    type="button"
                    class="resource-icon-button resource-icon-button--archive"
                    title="Archivar registro"
                    @click="archiveRecord(item)"
                  >
                    <svg
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path d="M4 7h16" />
                      <path d="M6 7v13h12V7" />
                      <path d="M9 11h6" />
                      <path d="M5 3h14v4H5z" />
                    </svg>

                    <span>Archivar</span>
                  </button>

                  <button
                    v-else
                    type="button"
                    class="resource-icon-button resource-icon-button--restore"
                    title="Restaurar registro"
                    @click="restoreRecord(item)"
                  >
                    <svg
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path d="M4 4v6h6" />
                      <path d="M5.5 15a8 8 0 1 0 2-8.5L4 10" />
                    </svg>

                    <span>Restaurar</span>
                  </button>
                </div>
              </td>
            </tr>

            <tr v-if="loading">
              <td
                :colspan="columns.length + 1"
                class="resource-empty"
              >
                <div class="resource-loading">
                  <span class="resource-loading__spinner" />

                  <strong>Cargando información</strong>

                  <small>
                    Consultando los registros del módulo.
                  </small>
                </div>
              </td>
            </tr>

            <tr v-else-if="!rows.length">
              <td
                :colspan="columns.length + 1"
                class="resource-empty"
              >
                <div class="resource-empty__content">
                  <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path d="M5 5h14v14H5z" />
                    <path d="M9 9h6" />
                    <path d="M9 13h6" />
                    <path d="M9 17h4" />
                  </svg>

                  <strong>No se encontraron registros</strong>

                  <small>
                    Cambia los filtros o registra un nuevo elemento.
                  </small>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>