<script setup>
import {
  computed,
  onMounted,
  ref,
} from "vue"

import {
  getRentalAssignments,
  getRentalContracts,
  getRentalEquipment,
  getWarehouses,
} from "../../services/rentals.service"

import RentalsTabs from "./RentalsTabs.vue"

import "./rentals-dashboard.css"


const equipment = ref([])
const contracts = ref([])
const assignments = ref([])
const warehouses = ref([])

const loading = ref(false)
const error = ref("")


const stats = computed(() => {
  const fleet = equipment.value.length

  const available = equipment.value.filter(
    (item) => item.is_available_for_rental,
  ).length

  const activeContracts = contracts.value.filter(
    (item) => item.status === "active",
  ).length

  const activeAssignments = assignments.value.filter(
    (item) => [
      "installed",
      "active",
      "removal_pending",
    ].includes(item.status),
  ).length

  const installedAssignments = assignments.value.filter(
    (item) => [
      "installed",
      "active",
    ].includes(item.status),
  ).length

  const pendingRemovals = assignments.value.filter(
    (item) => item.status === "removal_pending",
  ).length

  const activeWarehouses = warehouses.value.filter(
    (item) => item.is_active,
  ).length

  return {
    fleet,
    available,
    activeContracts,
    activeAssignments,
    installedAssignments,
    pendingRemovals,
    activeWarehouses,
  }
})


const fleetUsagePercentage = computed(() => {
  if (!stats.value.fleet) {
    return 0
  }

  const unavailableEquipment = (
    stats.value.fleet - stats.value.available
  )

  return Math.min(
    100,
    Math.max(
      0,
      Math.round(
        (
          unavailableEquipment /
          stats.value.fleet
        ) * 100,
      ),
    ),
  )
})


const availabilityPercentage = computed(() => {
  if (!stats.value.fleet) {
    return 0
  }

  return Math.min(
    100,
    Math.max(
      0,
      Math.round(
        (
          stats.value.available /
          stats.value.fleet
        ) * 100,
      ),
    ),
  )
})


const operationalMessage = computed(() => {
  if (loading.value) {
    return "Actualizando información operativa"
  }

  if (!stats.value.fleet) {
    return "Todavía no existen equipos registrados"
  }

  if (!stats.value.available) {
    return "No existen equipos disponibles para asignar"
  }

  return `${stats.value.available} equipos disponibles para alquiler`
})


const quickActions = [
  {
    title: "Registrar equipo",
    description: "Incorpora una máquina a la flota de alquileres.",
    route: "/alquileres/equipos/nuevo",
    className: "equipment",
    icon: "equipment",
  },
  {
    title: "Nuevo contrato",
    description: "Registra las condiciones comerciales del alquiler.",
    route: "/alquileres/contratos/nuevo",
    className: "contract",
    icon: "contract",
  },
  {
    title: "Asignar equipo",
    description: "Relaciona una máquina con un contrato y cliente.",
    route: "/alquileres/asignaciones/nueva",
    className: "assignment",
    icon: "assignment",
  },
  {
    title: "Ver operaciones",
    description: "Revisa preparaciones, instalaciones y retiros.",
    route: "/alquileres/operaciones",
    className: "operations",
    icon: "operations",
  },
]


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


function getErrorMessage(requestError) {
  const responseData = requestError?.response?.data

  if (typeof responseData === "string") {
    return responseData
  }

  if (typeof responseData?.detail === "string") {
    return responseData.detail
  }

  if (typeof responseData?.message === "string") {
    return responseData.message
  }

  if (typeof requestError?.message === "string") {
    return requestError.message
  }

  return "No se pudo cargar la información del módulo de alquileres."
}


async function load() {
  loading.value = true
  error.value = ""

  try {
    const [
      equipmentResponse,
      contractsResponse,
      assignmentsResponse,
      warehousesResponse,
    ] = await Promise.all([
      getRentalEquipment(),
      getRentalContracts(),
      getRentalAssignments(),
      getWarehouses(),
    ])

    equipment.value = normalizeResponse(equipmentResponse)
    contracts.value = normalizeResponse(contractsResponse)
    assignments.value = normalizeResponse(assignmentsResponse)
    warehouses.value = normalizeResponse(warehousesResponse)
  } catch (requestError) {
    error.value = getErrorMessage(requestError)

    console.error(
      "Error cargando el panel de alquileres:",
      requestError,
    )
  } finally {
    loading.value = false
  }
}


onMounted(load)
</script>

<template>
  <section class="rentals-page">
    <RentalsTabs />

    <header class="rentals-hero">
      <div class="rentals-hero__content">
        <div class="rentals-hero__eyebrow">
          <span class="rentals-hero__eyebrow-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M4 7.5 12 3l8 4.5v9L12 21l-8-4.5v-9Z" />
              <path d="m4 7.5 8 4.5 8-4.5" />
              <path d="M12 12v9" />
            </svg>
          </span>

          <span>Gestión operativa</span>
        </div>

        <h1>Alquileres</h1>

        <p>
          Control integral de flota, almacenes, contratos,
          asignaciones y operaciones de ANDES.
        </p>

        <div class="rentals-hero__status">
          <span
            class="rentals-status-dot"
            :class="{ loading }"
          />

          <span>{{ operationalMessage }}</span>
        </div>
      </div>

      <div class="rentals-hero__actions">
        <button
          type="button"
          class="rentals-refresh"
          :disabled="loading"
          @click="load"
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

          <span>
            {{ loading ? "Actualizando" : "Actualizar" }}
          </span>
        </button>

        <RouterLink
          class="rentals-main-action"
          to="/alquileres/asignaciones/nueva"
        >
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M12 5v14" />
            <path d="M5 12h14" />
          </svg>

          <span>Nueva asignación</span>
        </RouterLink>
      </div>

      <div
        class="
          rentals-hero__decoration
          rentals-hero__decoration--one
        "
      />

      <div
        class="
          rentals-hero__decoration
          rentals-hero__decoration--two
        "
      />
    </header>

    <div
      v-if="error"
      class="rentals-error"
    >
      <div class="rentals-error__icon">
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
      </div>

      <div>
        <strong>No se pudo cargar el resumen</strong>
        <span>{{ error }}</span>
      </div>

      <button
        type="button"
        :disabled="loading"
        @click="load"
      >
        Reintentar
      </button>
    </div>

    <div class="summary-grid">
      <article class="summary-card summary-card--fleet">
        <div class="summary-card__top">
          <div class="summary-card__icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <rect
                x="5"
                y="3"
                width="14"
                height="7"
                rx="2"
              />

              <rect
                x="3"
                y="9"
                width="18"
                height="9"
                rx="2"
              />

              <path d="M7 18v3h10v-3" />
              <path d="M8 6h8" />
              <path d="M7 13h.01" />
            </svg>
          </div>

          <span class="summary-card__badge">
            Total
          </span>
        </div>

        <div class="summary-card__content">
          <small>Flota registrada</small>

          <strong>
            <span
              v-if="loading"
              class="summary-skeleton"
            />

            <template v-else>
              {{ stats.fleet }}
            </template>
          </strong>

          <p>
            Equipos incorporados al módulo de alquileres.
          </p>
        </div>
      </article>

      <article class="summary-card summary-card--available">
        <div class="summary-card__top">
          <div class="summary-card__icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="m8 12 2.5 2.5L16 9" />
              <circle
                cx="12"
                cy="12"
                r="9"
              />
            </svg>
          </div>

          <span class="summary-card__badge">
            {{ availabilityPercentage }}%
          </span>
        </div>

        <div class="summary-card__content">
          <small>Disponibles</small>

          <strong>
            <span
              v-if="loading"
              class="summary-skeleton"
            />

            <template v-else>
              {{ stats.available }}
            </template>
          </strong>

          <p>
            Máquinas listas para una nueva asignación.
          </p>
        </div>
      </article>

      <article class="summary-card summary-card--contracts">
        <div class="summary-card__top">
          <div class="summary-card__icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="
                  M6 3
                  h9
                  l3 3
                  v15
                  H6
                  a2 2 0 0 1-2-2
                  V5
                  a2 2 0 0 1 2-2Z
                "
              />

              <path d="M14 3v4h4" />
              <path d="M8 12h6" />
              <path d="M8 16h7" />
              <path d="M8 8h2" />
            </svg>
          </div>

          <span class="summary-card__badge">
            Vigentes
          </span>
        </div>

        <div class="summary-card__content">
          <small>Contratos activos</small>

          <strong>
            <span
              v-if="loading"
              class="summary-skeleton"
            />

            <template v-else>
              {{ stats.activeContracts }}
            </template>
          </strong>

          <p>
            Contratos actualmente activos con clientes.
          </p>
        </div>
      </article>

      <article class="summary-card summary-card--installed">
        <div class="summary-card__top">
          <div class="summary-card__icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M4 21V10l8-6 8 6v11" />
              <path d="M9 21v-7h6v7" />
              <path d="M3 21h18" />
            </svg>
          </div>

          <span class="summary-card__badge">
            Operando
          </span>
        </div>

        <div class="summary-card__content">
          <small>Equipos instalados</small>

          <strong>
            <span
              v-if="loading"
              class="summary-skeleton"
            />

            <template v-else>
              {{ stats.activeAssignments }}
            </template>
          </strong>

          <p>
            Equipos instalados, activos o pendientes de retiro.
          </p>
        </div>
      </article>

      <article class="summary-card summary-card--warehouse">
        <div class="summary-card__top">
          <div class="summary-card__icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="m3 9 9-6 9 6v12H3V9Z" />
              <path d="M7 21v-8h10v8" />
              <path d="M7 16h10" />
            </svg>
          </div>

          <span class="summary-card__badge">
            Activos
          </span>
        </div>

        <div class="summary-card__content">
          <small>Almacenes</small>

          <strong>
            <span
              v-if="loading"
              class="summary-skeleton"
            />

            <template v-else>
              {{ stats.activeWarehouses }}
            </template>
          </strong>

          <p>
            Ubicaciones activas para controlar la flota.
          </p>
        </div>
      </article>
    </div>

    <div class="rentals-dashboard-grid">
      <section class="rentals-quick-panel">
        <div class="panel-heading">
          <div>
            <span class="panel-heading__eyebrow">
              Navegación
            </span>

            <h2>Accesos rápidos</h2>

            <p>
              Ejecuta las operaciones principales del módulo.
            </p>
          </div>

          <div class="panel-heading__icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M12 3v4" />
              <path d="M12 17v4" />
              <path d="M3 12h4" />
              <path d="M17 12h4" />
              <path d="m5.6 5.6 2.8 2.8" />
              <path d="m15.6 15.6 2.8 2.8" />
              <path d="m18.4 5.6-2.8 2.8" />
              <path d="m8.4 15.6-2.8 2.8" />

              <circle
                cx="12"
                cy="12"
                r="3"
              />
            </svg>
          </div>
        </div>

        <div class="quick-actions-grid">
          <RouterLink
            v-for="action in quickActions"
            :key="action.route"
            :to="action.route"
            class="quick-action-card"
            :class="`quick-action-card--${action.className}`"
          >
            <div class="quick-action-card__icon">
              <svg
                v-if="action.icon === 'equipment'"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <rect
                  x="5"
                  y="3"
                  width="14"
                  height="7"
                  rx="2"
                />

                <rect
                  x="3"
                  y="9"
                  width="18"
                  height="9"
                  rx="2"
                />

                <path d="M7 18v3h10v-3" />
                <path d="M8 6h8" />
                <path d="M7 13h.01" />
              </svg>

              <svg
                v-else-if="action.icon === 'contract'"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="
                    M6 3
                    h9
                    l3 3
                    v15
                    H6
                    a2 2 0 0 1-2-2
                    V5
                    a2 2 0 0 1 2-2Z
                  "
                />

                <path d="M14 3v4h4" />
                <path d="M8 12h7" />
                <path d="M8 16h5" />
                <path d="M8 8h2" />
              </svg>

              <svg
                v-else-if="action.icon === 'assignment'"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle
                  cx="12"
                  cy="8"
                  r="3"
                />

                <path d="M5 21v-2a7 7 0 0 1 14 0v2" />
                <path d="M19 7v6" />
                <path d="M16 10h6" />
              </svg>

              <svg
                v-else
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path d="M4 6h16" />
                <path d="M4 12h16" />
                <path d="M4 18h16" />

                <circle
                  cx="8"
                  cy="6"
                  r="2"
                />

                <circle
                  cx="16"
                  cy="12"
                  r="2"
                />

                <circle
                  cx="10"
                  cy="18"
                  r="2"
                />
              </svg>
            </div>

            <div class="quick-action-card__content">
              <strong>{{ action.title }}</strong>
              <span>{{ action.description }}</span>
            </div>

            <div class="quick-action-card__arrow">
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path d="m9 18 6-6-6-6" />
              </svg>
            </div>
          </RouterLink>
        </div>
      </section>

      <aside class="rentals-overview-panel">
        <div class="panel-heading panel-heading--compact">
          <div>
            <span class="panel-heading__eyebrow">
              Resumen
            </span>

            <h2>Estado de la operación</h2>
          </div>
        </div>

        <div class="overview-main">
          <div class="overview-ring">
            <svg
              viewBox="0 0 120 120"
              aria-hidden="true"
            >
              <circle
                class="overview-ring__background"
                cx="60"
                cy="60"
                r="48"
              />

              <circle
                class="overview-ring__progress"
                cx="60"
                cy="60"
                r="48"
                :style="{
                  strokeDashoffset:
                    301.59 -
                    (
                      301.59 *
                      fleetUsagePercentage
                    ) /
                    100,
                }"
              />
            </svg>

            <div class="overview-ring__value">
              <strong>
                {{ fleetUsagePercentage }}%
              </strong>

              <span>en uso</span>
            </div>
          </div>

          <div class="overview-main__content">
            <span>Utilización de flota</span>

            <strong>
              {{ stats.fleet - stats.available }}
              de
              {{ stats.fleet }}
              equipos
            </strong>

            <p>
              Equipos asignados o incluidos actualmente
              dentro de una operación.
            </p>
          </div>
        </div>

        <div class="overview-list">
          <div class="overview-item">
            <div
              class="
                overview-item__icon
                overview-item__icon--blue
              "
            >
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path d="M4 21V10l8-6 8 6v11" />
                <path d="M9 21v-7h6v7" />
              </svg>
            </div>

            <div>
              <span>Instalaciones activas</span>
              <strong>{{ stats.installedAssignments }}</strong>
            </div>
          </div>

          <div class="overview-item">
            <div
              class="
                overview-item__icon
                overview-item__icon--amber
              "
            >
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path d="M8 7 4 11l4 4" />
                <path d="M4 11h11a5 5 0 0 1 5 5v2" />
              </svg>
            </div>

            <div>
              <span>Retiros pendientes</span>
              <strong>{{ stats.pendingRemovals }}</strong>
            </div>
          </div>

          <div class="overview-item">
            <div
              class="
                overview-item__icon
                overview-item__icon--green
              "
            >
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path d="m8 12 2.5 2.5L16 9" />

                <circle
                  cx="12"
                  cy="12"
                  r="9"
                />
              </svg>
            </div>

            <div>
              <span>Disponibilidad</span>
              <strong>{{ availabilityPercentage }}%</strong>
            </div>
          </div>
        </div>

        <RouterLink
          class="overview-footer-link"
          to="/alquileres/equipos"
        >
          <span>Revisar flota completa</span>

          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="m9 18 6-6-6-6" />
          </svg>
        </RouterLink>
      </aside>
    </div>
  </section>
</template>