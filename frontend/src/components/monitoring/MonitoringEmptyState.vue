<script setup>
defineProps({
  title: {
    type: String,
    default: "Sin registros",
  },
  message: {
    type: String,
    default: "Todavía no hay información para mostrar.",
  },
})
</script>

<template>
  <div class="empty-state">
    <div class="empty-icon">◎</div>
    <strong>{{ title }}</strong>
    <span>{{ message }}</span>
  </div>
</template>

<style scoped>
.empty-state {
  align-items: center;
  color: #64748b;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  justify-content: center;
  min-height: 180px;
  padding: 2rem;
  text-align: center;
}

.empty-icon {
  color: #94a3b8;
  font-size: 2rem;
}

.empty-state strong {
  color: #334155;
}

.empty-state span {
  font-size: 0.82rem;
}
</style>
