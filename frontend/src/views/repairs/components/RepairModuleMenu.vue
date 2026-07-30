<script setup>
import "./RepairModuleMenu.css"

defineProps({
  open: { type: Boolean, default: false },
  activeKey: { type: String, default: "" },
})

const emit = defineEmits(["close", "select"])

const options = [
  {
    key: "repairs",
    label: "Reparaciones",
    description: "Órdenes, diagnósticos y checklist",
  },
  {
    key: "part-requests",
    label: "Pedidos",
    description: "Solicitudes de partes y repuestos",
  },
  {
    key: "repair-settings",
    label: "Configuración",
    description: "Catálogos y parámetros del taller",
  },
]
</script>

<template>
  <Transition name="repair-module-menu">
    <section
      v-if="open"
      class="repair-module-menu"
      aria-label="Opciones del módulo Reparaciones"
    >
      <header class="repair-module-menu__header">
        <div>
          <span>Módulo</span>
          <strong>Reparaciones</strong>
        </div>

        <button type="button" @click="emit('close')">
          ×
        </button>
      </header>

      <div class="repair-module-menu__options">
        <button
          v-for="option in options"
          :key="option.key"
          type="button"
          :class="{ active: activeKey === option.key }"
          @click="emit('select', option.key)"
        >
          <span class="repair-module-menu__content">
            <strong>{{ option.label }}</strong>
            <small>{{ option.description }}</small>
          </span>

          <span>›</span>
        </button>
      </div>
    </section>
  </Transition>
</template>
