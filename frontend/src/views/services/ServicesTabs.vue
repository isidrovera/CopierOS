<script setup>
import { useRoute, useRouter } from "vue-router"

import "./services.css"

const route = useRoute()
const router = useRouter()

const tabs = [
  { label: "Órdenes", route: "service-orders" },
  { label: "Nueva OS", route: "service-order-create" },
]

function go(name) {
  if (route.name !== name) router.push({ name })
}
</script>

<template>
  <nav class="services-tabs">
    <button
      v-for="tab in tabs"
      :key="tab.route"
      type="button"
      :class="{ active: route.name === tab.route }"
      @click="go(tab.route)"
    >
      {{ tab.label }}
    </button>
  </nav>
</template>
