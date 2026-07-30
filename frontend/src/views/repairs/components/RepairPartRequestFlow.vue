<script setup>
import "./RepairPartRequestFlow.css"

defineProps({
  currentStatus: { type: String, default: "draft" },
})

const steps = [
  { key: "draft", label: "Solicitud" },
  { key: "in_review", label: "Revisión" },
  { key: "approved", label: "Decisión" },
  { key: "source", label: "Origen" },
  { key: "delivered", label: "Entrega" },
  { key: "received", label: "Recepción" },
]

const statusOrder = {
  draft: 1,
  submitted: 1,
  in_review: 2,
  partially_approved: 3,
  approved: 3,
  source_evaluation: 4,
  pending_reservation: 4,
  pending_purchase: 4,
  pending_external_repair: 4,
  pending_withdrawal: 4,
  authorized_for_withdrawal: 4,
  withdrawn: 4,
  pending_logistics: 5,
  prepared: 5,
  delivered: 5,
  partially_attended: 5,
  attended: 6,
  received: 6,
  installed: 6,
  completed: 6,
  closed: 6,
}
</script>

<template>
  <ol class="part-request-flow">
    <li
      v-for="(step, index) in steps"
      :key="step.key"
      :class="{
        completed: index + 1 < (statusOrder[currentStatus] || 1),
        active: index + 1 === (statusOrder[currentStatus] || 1),
      }"
    >
      <span>{{ index + 1 }}</span>
      <strong>{{ step.label }}</strong>
    </li>
  </ol>
</template>
