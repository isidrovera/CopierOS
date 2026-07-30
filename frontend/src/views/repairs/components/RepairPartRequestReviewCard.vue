<script setup>
import "./RepairPartRequestReviewCard.css"

defineProps({
  review: { type: Object, required: true },
})
</script>

<template>
  <article class="part-request-review-card">
    <header>
      <strong>{{ review.result_name }}</strong>
      <span>{{ review.is_current ? "Vigente" : "Anterior" }}</span>
    </header>

    <div>
      <small>{{ review.reviewed_by_name }}</small>
      <small>{{ review.reviewed_at }}</small>
      <small>Propuesta: {{ review.proposed_quantity }}</small>
      <small v-if="review.requires_management_approval">
        Requiere gerencia
      </small>
      <small v-if="review.requires_replacement">
        Requiere reposición
      </small>
    </div>

    <p v-if="review.justification">
      {{ review.justification }}
    </p>
  </article>
</template>
