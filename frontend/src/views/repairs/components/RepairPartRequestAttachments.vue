<script setup>
import "./RepairPartRequestAttachments.css"

defineProps({
  attachments: { type: Array, default: () => [] },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(["add", "open", "delete"])
</script>

<template>
  <section class="part-request-attachments">
    <header>
      <strong>Adjuntos</strong>

      <button type="button" :disabled="disabled" @click="emit('add')">
        + Agregar
      </button>
    </header>

    <div v-if="attachments.length" class="part-request-attachments__list">
      <article
        v-for="attachment in attachments"
        :key="attachment.id"
      >
        <button type="button" @click="emit('open', attachment)">
          <strong>{{ attachment.title || attachment.original_filename }}</strong>
          <small>{{ attachment.attachment_type_name }}</small>
        </button>

        <button
          type="button"
          :disabled="disabled"
          @click="emit('delete', attachment)"
        >
          Eliminar
        </button>
      </article>
    </div>

    <p v-else>No hay archivos adjuntos.</p>
  </section>
</template>
