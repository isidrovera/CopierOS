<script setup>
import { reactive } from "vue"
import "./RepairPartRequestDecisionPanel.css"

const props = defineProps({
  requestId: { type: String, required: true },
  itemId: { type: String, default: "" },
  requestedQuantity: { type: [Number, String], default: 0 },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(["submit"])

const form = reactive({
  decision: "approved",
  approved_quantity: props.requestedQuantity,
  reason: "",
  information_required: "",
  is_final: true,
})

function submit() {
  emit("submit", {
    request: props.requestId,
    item: props.itemId || null,
    requested_quantity: props.requestedQuantity,
    ...form,
  })
}
</script>

<template>
  <section class="part-request-decision-panel">
    <select v-model="form.decision" :disabled="disabled">
      <option value="approved">Aprobado</option>
      <option value="partially_approved">Aprobado parcialmente</option>
      <option value="rejected">Rechazado</option>
      <option value="information_required">Información requerida</option>
    </select>

    <input
      v-model="form.approved_quantity"
      type="number"
      min="0"
      step="0.01"
      :disabled="disabled"
    >

    <textarea
      v-model="form.reason"
      placeholder="Motivo"
      :disabled="disabled"
    />

    <textarea
      v-if="form.decision === 'information_required'"
      v-model="form.information_required"
      placeholder="Información requerida"
      :disabled="disabled"
    />

    <button type="button" :disabled="disabled" @click="submit">
      Registrar decisión
    </button>
  </section>
</template>
