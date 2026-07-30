<script setup>
import { ref } from "vue"
import "./RepairPartRequestCommentBox.css"

const props = defineProps({
  requestId: { type: String, required: true },
  itemId: { type: String, default: "" },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(["submit"])

const text = ref("")
const commentType = ref("general")
const isInternal = ref(false)

function submit() {
  if (!text.value.trim()) return

  emit("submit", {
    request: props.requestId,
    item: props.itemId || null,
    comment_type: commentType.value,
    text: text.value.trim(),
    is_internal: isInternal.value,
    mentioned_users: [],
  })
}
</script>

<template>
  <section class="part-request-comment-box">
    <select v-model="commentType" :disabled="disabled">
      <option value="general">General</option>
      <option value="technical">Técnico</option>
      <option value="area_manager">Jefe de área</option>
      <option value="management">Gerencia</option>
      <option value="warehouse">Almacén</option>
      <option value="logistics">Logística</option>
      <option value="purchasing">Compras</option>
      <option value="information_request">Solicitud de información</option>
      <option value="information_response">Respuesta de información</option>
      <option value="internal_note">Nota interna</option>
    </select>

    <textarea
      v-model="text"
      placeholder="Escribir comentario"
      :disabled="disabled"
    />

    <footer>
      <label>
        <input v-model="isInternal" type="checkbox" :disabled="disabled">
        Comentario interno
      </label>

      <button type="button" :disabled="disabled" @click="submit">
        Agregar comentario
      </button>
    </footer>
  </section>
</template>
