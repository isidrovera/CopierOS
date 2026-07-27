<script setup>
import "./rentals-tabs.css"


const tabs = [
  {
    name: "rentals-dashboard",
    label: "Resumen",
    icon: "dashboard",
  },
  {
    name: "rental-equipment-list",
    label: "Flota",
    icon: "equipment",
  },
  {
    name: "rental-contract-list",
    label: "Contratos",
    icon: "contract",
  },
  {
    name: "rental-assignment-list",
    label: "Asignaciones",
    icon: "assignment",
  },
  {
    name: "rental-warehouse-list",
    label: "Almacenes",
    icon: "warehouse",
  },
  {
    name: "rental-operations",
    label: "Operaciones",
    icon: "operations",
  },
]
</script>

<template>
  <nav
    class="rentals-tabs"
    aria-label="Navegación de alquileres"
  >
    <RouterLink
      v-for="tab in tabs"
      :key="tab.name"
      :to="{ name: tab.name }"
      class="rentals-tab"
    >
      <span class="rentals-tab__icon">
        <svg
          v-if="tab.icon === 'dashboard'"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <rect
            x="3"
            y="3"
            width="7"
            height="7"
            rx="1"
          />

          <rect
            x="14"
            y="3"
            width="7"
            height="7"
            rx="1"
          />

          <rect
            x="3"
            y="14"
            width="7"
            height="7"
            rx="1"
          />

          <rect
            x="14"
            y="14"
            width="7"
            height="7"
            rx="1"
          />
        </svg>

        <svg
          v-else-if="tab.icon === 'equipment'"
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
        </svg>

        <svg
          v-else-if="tab.icon === 'contract'"
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
        </svg>

        <svg
          v-else-if="tab.icon === 'assignment'"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle
            cx="12"
            cy="8"
            r="3"
          />

          <path d="M5 21v-2a7 7 0 0 1 14 0v2" />
        </svg>

        <svg
          v-else-if="tab.icon === 'warehouse'"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path d="m3 9 9-6 9 6v12H3V9Z" />
          <path d="M7 21v-8h10v8" />
          <path d="M7 16h10" />
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
      </span>

      <span>{{ tab.label }}</span>
    </RouterLink>
  </nav>
</template>