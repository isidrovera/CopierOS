<script setup>
import {
  computed,
} from "vue"


const props = defineProps({
  status: {
    type: String,
    default: "unknown",
  },
  label: {
    type: String,
    default: "",
  },
})


const normalizedStatus = computed(
  () => String(
    props.status || "unknown"
  )
    .toLowerCase()
    .replaceAll("_", "-")
)


const visibleLabel = computed(
  () => (
    props.label ||
    String(
      props.status || "Sin estado"
    )
      .replaceAll("_", " ")
  )
)
</script>

<template>
  <span
    class="monitoring-status"
    :class="`status-${normalizedStatus}`"
  >
    <span class="status-dot"></span>
    {{ visibleLabel }}
  </span>
</template>

<style scoped>
.monitoring-status {
  align-items: center;
  background: #eef2f7;
  border: 1px solid #d8e0ea;
  border-radius: 999px;
  color: #475569;
  display: inline-flex;
  font-size: 0.72rem;
  font-weight: 700;
  gap: 0.38rem;
  line-height: 1;
  padding: 0.38rem 0.58rem;
  text-transform: capitalize;
}

.status-dot {
  background: currentColor;
  border-radius: 999px;
  height: 0.42rem;
  width: 0.42rem;
}

.status-active,
.status-ready,
.status-online,
.status-completed {
  background: #ecfdf3;
  border-color: #bbf7d0;
  color: #15803d;
}

.status-offline,
.status-error,
.status-revoked,
.status-blocked {
  background: #fff1f2;
  border-color: #fecdd3;
  color: #be123c;
}

.status-warning,
.status-partial,
.status-pending,
.status-testing {
  background: #fffbeb;
  border-color: #fde68a;
  color: #b45309;
}

.status-discovered,
.status-identifying,
.status-running {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1d4ed8;
}
</style>
