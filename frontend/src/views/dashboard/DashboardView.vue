<script setup>
import {
  computed,
  onMounted,
  ref,
} from "vue"

import {
  useRouter,
} from "vue-router"

import {
  getStoredUser,
} from "../../services/auth.service"

import {
  getPartners,
} from "../../services/partners.service"

import "./dashboard.css"


const router = useRouter()

const user = getStoredUser()

const loadingCustomers = ref(false)
const customerCount = ref(0)


const userName = computed(() => {
  if (!user) {
    return "Usuario"
  }

  const fullName = [
    user.first_name,
    user.paternal_last_name,
    user.maternal_last_name,
    user.last_name,
  ]
    .filter(Boolean)
    .join(" ")
    .trim()

  return (
    user.full_name ||
    fullName ||
    user.username ||
    user.email ||
    "Usuario"
  )
})


const customerDescription = computed(() => {
  if (loadingCustomers.value) {
    return "Consultando..."
  }

  if (customerCount.value === 0) {
    return "Sin registros"
  }

  if (customerCount.value === 1) {
    return "Cliente registrado"
  }

  return "Clientes registrados"
})


async function loadCustomerCount() {
  loadingCustomers.value = true

  try {
    const response = await getPartners({
      includeArchived: false,
      isActive: true,
    })

    const partners = Array.isArray(response)
      ? response
      : response?.results || []

    customerCount.value = partners.filter(
      (partner) => (
        partner.is_rental_customer ||
        partner.is_sales_customer ||
        partner.is_service_customer
      )
    ).length
  } catch (error) {
    console.error(
      "No se pudo obtener la cantidad de clientes:",
      error
    )

    customerCount.value = 0
  } finally {
    loadingCustomers.value = false
  }
}


async function handleCreateUser() {
  await router.push({
    name: "user-create",
  })
}


async function handleCreateCustomer() {
  await router.push({
    name: "partner-create",
  })
}


async function handleCreateMachine() {
  await router.push({
    name: "equipment-create",
  })
}


function handleCreateService() {
  window.alert(
    "El módulo de servicios se desarrollará próximamente."
  )
}


onMounted(() => {
  loadCustomerCount()
})
</script>

<template>
  <section class="dashboard">
    <!-- ========================================================= -->
    <!-- BIENVENIDA                                                -->
    <!-- ========================================================= -->
    <header class="welcome-banner">
      <div class="welcome-content">
        <span class="welcome-label">
          Resumen general
        </span>

        <div class="welcome-title">
          <h2>Hola, {{ userName }}</h2>

          <p>
            Información principal de Copier OS.
          </p>
        </div>
      </div>

      <div
        class="welcome-decoration"
        aria-hidden="true"
      >
        <svg viewBox="0 0 24 24">
          <path d="M6 9V3h12v6" />

          <path
            d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"
          />

          <rect
            x="6"
            y="14"
            width="12"
            height="8"
            rx="1"
          />

          <path d="M18 12h.01" />
        </svg>
      </div>
    </header>

    <!-- ========================================================= -->
    <!-- INDICADORES                                               -->
    <!-- ========================================================= -->
    <section class="statistics-grid">
      <article class="statistic-card users-card">
        <div class="statistic-icon users-icon">
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"
            />

            <circle
              cx="9"
              cy="7"
              r="4"
            />

            <path
              d="M22 21v-2a4 4 0 0 0-3-3.87"
            />

            <path
              d="M16 3.13a4 4 0 0 1 0 7.75"
            />
          </svg>
        </div>

        <div class="statistic-content">
          <span>Usuarios</span>
          <strong>1</strong>
          <small>Registrado</small>
        </div>
      </article>

      <article class="statistic-card customers-card">
        <div class="statistic-icon customers-icon">
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M3 21h18" />

            <path
              d="M6 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16"
            />

            <path d="M9 7h2" />
            <path d="M13 7h2" />
            <path d="M9 11h2" />
            <path d="M13 11h2" />
            <path d="M9 15h2" />
            <path d="M13 15h2" />
          </svg>
        </div>

        <div class="statistic-content">
          <span>Clientes</span>

          <strong>
            {{
              loadingCustomers
                ? "..."
                : customerCount
            }}
          </strong>

          <small>
            {{ customerDescription }}
          </small>
        </div>
      </article>

      <article class="statistic-card machines-card">
        <div class="statistic-icon machines-icon">
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M6 9V2h12v7" />

            <path
              d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"
            />

            <rect
              x="6"
              y="14"
              width="12"
              height="8"
              rx="1"
            />

            <path d="M18 12h.01" />
          </svg>
        </div>

        <div class="statistic-content">
          <span>Equipos</span>
          <strong>0</strong>
          <small>Sin registros</small>
        </div>
      </article>

      <article class="statistic-card services-card">
        <div class="statistic-icon services-icon">
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9z"
            />
          </svg>
        </div>

        <div class="statistic-content">
          <span>Servicios</span>
          <strong>0</strong>
          <small>Sin pendientes</small>
        </div>
      </article>
    </section>

    <!-- ========================================================= -->
    <!-- ACCIONES RÁPIDAS                                          -->
    <!-- ========================================================= -->
    <section class="quick-actions-section">
      <header class="section-header">
        <div>
          <span>Accesos directos</span>
          <h3>Acciones rápidas</h3>
        </div>
      </header>

      <div class="quick-actions-grid">
        <button
          type="button"
          class="quick-action-card quick-action-users"
          @click="handleCreateUser"
        >
          <span class="quick-action-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="M15 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"
              />

              <circle
                cx="8.5"
                cy="7"
                r="4"
              />

              <line
                x1="19"
                y1="8"
                x2="19"
                y2="14"
              />

              <line
                x1="22"
                y1="11"
                x2="16"
                y2="11"
              />
            </svg>
          </span>

          <span class="quick-action-content">
            <strong>Crear usuario</strong>
            <small>Nuevo acceso</small>
          </span>

          <span class="quick-action-arrow">
            ›
          </span>
        </button>

        <button
          type="button"
          class="quick-action-card quick-action-customers"
          @click="handleCreateCustomer"
        >
          <span class="quick-action-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M3 21h18" />

              <path
                d="M6 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16"
              />

              <path d="M9 7h2" />
              <path d="M13 7h2" />
              <path d="M9 11h2" />
              <path d="M13 11h2" />
            </svg>
          </span>

          <span class="quick-action-content">
            <strong>Registrar cliente</strong>
            <small>Nueva empresa</small>
          </span>

          <span class="quick-action-arrow">
            ›
          </span>
        </button>

        <button
          type="button"
          class="quick-action-card quick-action-machines"
          @click="handleCreateMachine"
        >
          <span class="quick-action-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M6 9V2h12v7" />

              <path
                d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"
              />

              <rect
                x="6"
                y="14"
                width="12"
                height="8"
                rx="1"
              />
            </svg>
          </span>

          <span class="quick-action-content">
            <strong>Registrar equipo</strong>
            <small>Nueva máquina</small>
          </span>

          <span class="quick-action-arrow">
            ›
          </span>
        </button>

        <button
          type="button"
          class="quick-action-card quick-action-services"
          @click="handleCreateService"
        >
          <span class="quick-action-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9z"
              />
            </svg>
          </span>

          <span class="quick-action-content">
            <strong>Crear servicio</strong>
            <small>Atención técnica</small>
          </span>

          <span class="quick-action-arrow">
            ›
          </span>
        </button>
      </div>
    </section>

    <!-- ========================================================= -->
    <!-- ACTIVIDAD                                                 -->
    <!-- ========================================================= -->
    <section class="activity-section">
      <article class="panel">
        <header class="panel-header">
          <div>
            <span>Actividad</span>
            <h3>Actividad reciente</h3>
          </div>

          <button type="button">
            Ver todo
          </button>
        </header>

        <div class="empty-state">
          <div class="empty-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                cx="12"
                cy="12"
                r="9"
              />

              <path d="M12 7v5l3 2" />
            </svg>
          </div>

          <div>
            <h4>No hay actividad registrada</h4>

            <p>
              Las acciones realizadas aparecerán aquí.
            </p>
          </div>
        </div>
      </article>
    </section>
  </section>
</template>