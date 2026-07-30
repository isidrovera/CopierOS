<script setup>
import "./RepairPartRequestActions.css"

defineProps({
  request: { type: Object, required: true },
})

const emit = defineEmits(["submit", "cancel", "close", "archive", "restore"])
</script>

<template>
  <div class="part-request-actions">
    <button
      v-if="request.status === 'draft'"
      class="primary"
      type="button"
      @click="emit('submit', request)"
    >
      Enviar solicitud
    </button>

    <button
      v-if="!['closed', 'cancelled', 'rejected'].includes(request.status)"
      class="danger"
      type="button"
      @click="emit('cancel', request)"
    >
      Cancelar
    </button>

    <button
      v-if="['attended', 'completed'].includes(request.status)"
      class="success"
      type="button"
      @click="emit('close', request)"
    >
      Cerrar solicitud
    </button>

    <button
      v-if="!request.is_archived"
      type="button"
      @click="emit('archive', request)"
    >
      Archivar
    </button>

    <button
      v-else
      type="button"
      @click="emit('restore', request)"
    >
      Restaurar
    </button>
  </div>
</template>
