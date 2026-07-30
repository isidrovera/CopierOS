<script setup>
import { computed, ref } from "vue"
import "./RepairSettingsView.css"

const activeSection = ref("requests")

const sections = [
  {
    key: "requests",
    label: "Solicitudes",
    description:
      "Estados, prioridades y áreas responsables.",
  },
  {
    key: "items",
    label: "Ítems",
    description:
      "Tipos, origen, urgencia y ruta de aprobación.",
  },
  {
    key: "sources",
    label: "Orígenes",
    description:
      "Stock, alquiler, equipos donantes y compras.",
  },
  {
    key: "attachments",
    label: "Adjuntos",
    description:
      "Tipos de evidencia y documentos.",
  },
]

const optionsBySection = {
  requests: {
    title: "Configuración de solicitudes",
    groups: [
      {
        title: "Prioridades",
        values: [
          "Baja",
          "Normal",
          "Alta",
          "Urgente",
          "Crítica",
        ],
      },
      {
        title: "Áreas responsables",
        values: [
          "Técnica",
          "Jefe de área",
          "Gerencia",
          "Almacén",
          "Logística",
          "Compras",
          "Cerrada",
        ],
      },
      {
        title: "Estados",
        values: [
          "Borrador",
          "Enviada",
          "En revisión",
          "Parcialmente aprobada",
          "Aprobada",
          "Parcialmente atendida",
          "Atendida",
          "Rechazada",
          "Cancelada",
          "Cerrada",
        ],
      },
    ],
  },
  items: {
    title: "Configuración de ítems",
    groups: [
      {
        title: "Tipos",
        values: [
          "Repuesto",
          "Accesorio",
          "Unidad completa",
          "Subparte",
          "Consumible",
          "Tóner",
          "Disco duro",
          "Cable de poder",
          "Rueda de base",
          "Tapa",
          "Panel",
          "Otro",
        ],
      },
      {
        title: "Rutas de aprobación",
        values: [
          "Directa a gerencia",
          "Revisión previa del jefe de área",
        ],
      },
      {
        title: "Urgencia",
        values: [
          "Normal",
          "Alta",
          "Crítica",
        ],
      },
    ],
  },
  sources: {
    title: "Configuración de orígenes",
    groups: [
      {
        title: "Tipos de origen",
        values: [
          "Almacén de repuestos",
          "Almacén de alquiler",
          "Máquina para partes",
          "Máquina con problemas",
          "Máquina operativa",
          "Compra externa",
          "Reparación externa",
          "Sin disponibilidad",
        ],
      },
    ],
  },
  attachments: {
    title: "Configuración de adjuntos",
    groups: [
      {
        title: "Tipos de adjunto",
        values: [
          "General",
          "Evidencia técnica",
          "Equipo donante",
          "Evidencia de stock",
          "Cotización",
          "Documento de compra",
          "Evidencia de retiro",
          "Evidencia de entrega",
          "Evidencia de reposición",
          "Otro",
        ],
      },
    ],
  },
}

const currentSection = computed(() =>
  optionsBySection[activeSection.value]
)
</script>

<template>
  <main class="repair-settings-view">
    <header>
      <div>
        <span>Reparaciones</span>
        <h1>Configuración</h1>
        <p>
          Catálogos definidos por el backend para pedidos de repuestos.
        </p>
      </div>
    </header>

    <section class="repair-settings-view__layout">
      <nav>
        <button
          v-for="section in sections"
          :key="section.key"
          type="button"
          :class="{ active: activeSection === section.key }"
          @click="activeSection = section.key"
        >
          <strong>{{ section.label }}</strong>
          <small>{{ section.description }}</small>
        </button>
      </nav>

      <section class="repair-settings-view__content">
        <header>
          <strong>{{ currentSection.title }}</strong>
          <small>
            Valores controlados por los modelos de Django.
          </small>
        </header>

        <div class="repair-settings-view__groups">
          <article
            v-for="group in currentSection.groups"
            :key="group.title"
          >
            <strong>{{ group.title }}</strong>

            <div>
              <span
                v-for="value in group.values"
                :key="value"
              >
                {{ value }}
              </span>
            </div>
          </article>
        </div>

        <footer>
          Estos valores son informativos y no se editan
          directamente desde esta vista.
        </footer>
      </section>
    </section>
  </main>
</template>
