<script setup>
import "./RepairPartRequestItemCard.css"
import RepairPartRequestStatusBadge from "./RepairPartRequestStatusBadge.vue"

defineProps({
  item: { type: Object, required: true },
})

const emit = defineEmits(["open"])
</script>

<template>
  <article class="part-request-item-card">
    <div class="part-request-item-card__content">
      <header>
        <strong>
          {{ item.display_name || item.component_name || item.custom_name }}
        </strong>

        <RepairPartRequestStatusBadge
          :status="item.status"
          :label="item.status_name"
        />
      </header>

      <div class="part-request-item-card__meta">
        <small>{{ item.item_type_name }}</small>
        <small>{{ item.urgency_name || item.urgency }}</small>
        <small>{{ item.approval_route_name }}</small>
      </div>

      <div class="part-request-item-card__quantities">
        <span>Solicitada: {{ item.requested_quantity }}</span>
        <span>Aprobada: {{ item.approved_quantity }}</span>
        <span>Entregada: {{ item.delivered_quantity }}</span>
        <span>Recibida: {{ item.received_quantity }}</span>
      </div>
    </div>

    <button type="button" @click="emit('open', item)">
      Ver
    </button>
  </article>
</template>
