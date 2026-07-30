<script setup>
import { computed } from "vue"
import "./RepairPartRequestStatusBadge.css"

const props = defineProps({
  status: { type: String, default: "" },
  label: { type: String, default: "" },
})

const normalizedStatus = computed(() =>
  String(props.status || "").trim().toLowerCase()
)

const visibleLabel = computed(() =>
  props.label ||
  String(props.status || "Sin estado").replaceAll("_", " ")
)
</script>

<template>
  <span
    class="part-request-status"
    :class="normalizedStatus || 'neutral'"
  >
    {{ visibleLabel }}
  </span>
</template>
