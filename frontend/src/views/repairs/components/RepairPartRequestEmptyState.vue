<script setup>
import "./RepairPartRequestEmptyState.css"

defineProps({
  title: { type: String, default: "Sin registros" },
  message: { type: String, default: "" },
})
</script>

<template>
  <div class="part-request-empty-state">
    <strong>{{ title }}</strong>
    <p v-if="message">{{ message }}</p>
    <slot />
  </div>
</template>
