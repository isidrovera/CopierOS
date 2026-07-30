<script setup>
import "./RepairPartRequestTimeline.css"

defineProps({
  entries: { type: Array, default: () => [] },
})
</script>

<template>
  <div class="part-request-timeline">
    <article
      v-for="entry in entries"
      :key="entry.id"
      class="part-request-timeline__entry"
    >
      <span class="part-request-timeline__marker" />

      <div>
        <header>
          <strong>{{ entry.event }}</strong>
          <small>{{ entry.changed_at }}</small>
        </header>

        <p v-if="entry.comment">{{ entry.comment }}</p>

        <small v-if="entry.changed_by_name">
          {{ entry.changed_by_name }}
        </small>
      </div>
    </article>

    <div v-if="!entries.length" class="part-request-timeline__empty">
      No hay movimientos registrados.
    </div>
  </div>
</template>
