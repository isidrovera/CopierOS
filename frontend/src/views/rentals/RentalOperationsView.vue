<script setup>
import {
  computed,
  ref,
} from "vue"

import RentalResourceList from "./RentalResourceList.vue"

import "./rental-operations.css"


const selectedType = ref("preparations")

const configurations = {
  preparations: {
    title: "Preparaciones",
    shortTitle: "Preparación",
    description: "Equipos evaluados, acondicionados y listos para alquiler.",
    resource: "preparations",
    tone: "blue",
    icon: "preparation",
    columns: [
      { key: "code", label: "Código" },
      { key: "equipment_serial_number", label: "Serie" },
      { key: "equipment_model_name", label: "Modelo" },
      { key: "assigned_technician_name", label: "Técnico" },
      { key: "status_display", label: "Estado", badge: true },
      { key: "result_display", label: "Resultado" },
    ],
  },

  installations: {
    title: "Instalaciones",
    shortTitle: "Instalación",
    description: "Instalaciones realizadas o pendientes en las sedes del cliente.",
    resource: "installations",
    tone: "green",
    icon: "installation",
    columns: [
      { key: "code", label: "Código" },
      { key: "customer_name", label: "Cliente" },
      { key: "equipment_serial_number", label: "Serie" },
      { key: "assigned_technician_name", label: "Técnico" },
      { key: "status_display", label: "Estado", badge: true },
      { key: "result_display", label: "Resultado" },
    ],
  },

  removals: {
    title: "Retiros",
    shortTitle: "Retiro",
    description: "Recojo de equipos por cierre, cambio o finalización del contrato.",
    resource: "removals",
    tone: "amber",
    icon: "removal",
    columns: [
      { key: "code", label: "Código" },
      { key: "customer_name", label: "Cliente" },
      { key: "equipment_serial_number", label: "Serie" },
      { key: "removal_type_display", label: "Tipo" },
      { key: "status_display", label: "Estado", badge: true },
      { key: "result_display", label: "Resultado" },
    ],
  },

  replacements: {
    title: "Reemplazos",
    shortTitle: "Reemplazo",
    description: "Cambios de equipos instalados por fallas o necesidades operativas.",
    resource: "replacements",
    tone: "purple",
    icon: "replacement",
    columns: [
      { key: "code", label: "Código" },
      { key: "customer_name", label: "Cliente" },
      { key: "outgoing_serial_number", label: "Serie que sale" },
      { key: "incoming_serial_number", label: "Serie que ingresa" },
      { key: "status_display", label: "Estado", badge: true },
      { key: "result_display", label: "Resultado" },
    ],
  },

  movements: {
    title: "Movimientos",
    shortTitle: "Movimiento",
    description: "Historial de traslados, cambios de estado y movimientos de almacén.",
    resource: "movements",
    tone: "cyan",
    icon: "movement",
    columns: [
      { key: "equipment_serial_number", label: "Serie" },
      { key: "movement_type_display", label: "Movimiento" },
      { key: "previous_status_display", label: "Estado anterior" },
      { key: "new_status_display", label: "Estado nuevo", badge: true },
      { key: "source_warehouse_name", label: "Origen" },
      { key: "destination_warehouse_name", label: "Destino" },
    ],
  },

  documents: {
    title: "Documentos",
    shortTitle: "Documento",
    description: "Actas, guías, constancias y evidencias asociadas al alquiler.",
    resource: "documents",
    tone: "slate",
    icon: "document",
    columns: [
      { key: "title", label: "Título" },
      { key: "document_type_display", label: "Tipo" },
      { key: "document_number", label: "Número" },
      { key: "rental_equipment_display", label: "Equipo" },
      { key: "issued_date", label: "Fecha", type: "date" },
      { key: "is_verified", label: "Verificado" },
    ],
  },
}

const currentConfiguration = computed(() => (
  configurations[selectedType.value]
))
</script>

<template>
  <section class="rental-operations-page">
    <header
      class="operations-header"
      :class="`operations-header--${currentConfiguration.tone}`"
    >
      <div class="operations-header__content">
        <span class="operations-header__eyebrow">
          Gestión de alquileres
        </span>

        <h1>Operaciones</h1>

        <p>
          Controla la preparación, instalación, retiro, reemplazo,
          traslado y documentación de los equipos alquilados.
        </p>
      </div>

      <div class="operations-header__graphic">
        <svg viewBox="0 0 120 120" aria-hidden="true">
          <rect x="30" y="27" width="60" height="35" rx="7" />
          <rect x="20" y="55" width="80" height="42" rx="8" />
          <path d="M35 97v12h50V97" />
          <path d="M42 40h36" />
          <path d="M35 70h8" />
          <path d="M72 77h15" />
          <path d="M72 84h15" />
        </svg>
      </div>
    </header>

    <nav
      class="operations-navigation"
      aria-label="Tipos de operación"
    >
      <button
        v-for="(configuration, key) in configurations"
        :key="key"
        type="button"
        class="operations-navigation__item"
        :class="[
          `operations-navigation__item--${configuration.tone}`,
          {
            'operations-navigation__item--active': selectedType === key,
          },
        ]"
        @click="selectedType = key"
      >
        <span class="operations-navigation__icon">
          <svg
            v-if="configuration.icon === 'preparation'"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L4 17v3h3l5.3-5.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-3-3 2.5-2.5Z" />
          </svg>

          <svg
            v-else-if="configuration.icon === 'installation'"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M4 21V10l8-6 8 6v11" />
            <path d="M9 21v-7h6v7" />
            <path d="m9 10 2 2 4-4" />
          </svg>

          <svg
            v-else-if="configuration.icon === 'removal'"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M9 6 4 11l5 5" />
            <path d="M4 11h10a6 6 0 0 1 6 6v2" />
          </svg>

          <svg
            v-else-if="configuration.icon === 'replacement'"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M7 7h11l-3-3" />
            <path d="m18 7-3 3" />
            <path d="M17 17H6l3 3" />
            <path d="m6 17 3-3" />
          </svg>

          <svg
            v-else-if="configuration.icon === 'movement'"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M5 7h14" />
            <path d="m15 3 4 4-4 4" />
            <path d="M19 17H5" />
            <path d="m9 13-4 4 4 4" />
          </svg>

          <svg
            v-else
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M6 3h9l3 3v15H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" />
            <path d="M14 3v4h4" />
            <path d="M8 12h8" />
            <path d="M8 16h6" />
          </svg>
        </span>

        <span class="operations-navigation__text">
          <strong>{{ configuration.title }}</strong>
          <small>{{ configuration.shortTitle }}</small>
        </span>

        <span class="operations-navigation__indicator" />
      </button>
    </nav>

    <div
      class="operations-current-section"
      :class="`operations-current-section--${currentConfiguration.tone}`"
    >
      <div class="operations-current-section__icon">
        <svg
          v-if="currentConfiguration.icon === 'preparation'"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L4 17v3h3l5.3-5.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-3-3 2.5-2.5Z" />
        </svg>

        <svg
          v-else-if="currentConfiguration.icon === 'installation'"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path d="M4 21V10l8-6 8 6v11" />
          <path d="M9 21v-7h6v7" />
          <path d="m9 10 2 2 4-4" />
        </svg>

        <svg
          v-else-if="currentConfiguration.icon === 'removal'"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path d="M9 6 4 11l5 5" />
          <path d="M4 11h10a6 6 0 0 1 6 6v2" />
        </svg>

        <svg
          v-else-if="currentConfiguration.icon === 'replacement'"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path d="M7 7h11l-3-3" />
          <path d="m18 7-3 3" />
          <path d="M17 17H6l3 3" />
          <path d="m6 17 3-3" />
        </svg>

        <svg
          v-else-if="currentConfiguration.icon === 'movement'"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path d="M5 7h14" />
          <path d="m15 3 4 4-4 4" />
          <path d="M19 17H5" />
          <path d="m9 13-4 4 4 4" />
        </svg>

        <svg
          v-else
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path d="M6 3h9l3 3v15H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" />
          <path d="M14 3v4h4" />
          <path d="M8 12h8" />
          <path d="M8 16h6" />
        </svg>
      </div>

      <div>
        <span>Sección seleccionada</span>
        <h2>{{ currentConfiguration.title }}</h2>
        <p>{{ currentConfiguration.description }}</p>
      </div>
    </div>

    <div class="operations-resource-panel">
      <RentalResourceList
        :key="selectedType"
        :title="currentConfiguration.title"
        :subtitle="currentConfiguration.description"
        :resource="currentConfiguration.resource"
        :columns="currentConfiguration.columns"
      />
    </div>
  </section>
</template>