<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  value: {
    type: [
      String,
      Number,
    ],
    default: 0,
  },
  hint: {
    type: String,
    default: "",
  },
  tone: {
    type: String,
    default: "blue",
  },
})
</script>

<template>
  <article
    class="metric-card"
    :class="`tone-${tone}`"
  >
    <div class="metric-label">
      {{ label }}
    </div>

    <strong class="metric-value">
      {{ value }}
    </strong>

    <div
      v-if="hint"
      class="metric-hint"
    >
      {{ hint }}
    </div>
  </article>
</template>

<style scoped>
.metric-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #2563eb;
  border-radius: 14px;
  box-shadow: 0 8px 22px rgb(15 23 42 / 0.05);
  min-height: 104px;
  padding: 1rem;
}

.metric-label {
  color: #64748b;
  font-size: 0.78rem;
  font-weight: 700;
}

.metric-value {
  color: #0f172a;
  display: block;
  font-size: 1.8rem;
  margin-top: 0.35rem;
}

.metric-hint {
  color: #94a3b8;
  font-size: 0.72rem;
  margin-top: 0.3rem;
}

.tone-green {
  border-left-color: #16a34a;
}

.tone-red {
  border-left-color: #e11d48;
}

.tone-amber {
  border-left-color: #d97706;
}

.tone-cyan {
  border-left-color: #0891b2;
}
</style>
