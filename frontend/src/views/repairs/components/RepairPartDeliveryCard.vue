<script setup>
import "./RepairPartDeliveryCard.css"
import RepairPartRequestStatusBadge from "./RepairPartRequestStatusBadge.vue"

defineProps({
  delivery: { type: Object, required: true },
})
</script>

<template>
  <article class="repair-part-delivery-card">
    <header>
      <strong>Entrega</strong>

      <RepairPartRequestStatusBadge
        :status="delivery.status"
        :label="delivery.status_name"
      />
    </header>

    <div>
      <small>Cantidad: {{ delivery.quantity }}</small>
      <small>Recibida: {{ delivery.received_quantity }}</small>
      <small v-if="delivery.prepared_by_name">
        Preparó: {{ delivery.prepared_by_name }}
      </small>
      <small v-if="delivery.delivered_by_name">
        Entregó: {{ delivery.delivered_by_name }}
      </small>
      <small v-if="delivery.delivered_to_name">
        Entregado a: {{ delivery.delivered_to_name }}
      </small>
      <small v-if="delivery.delivery_document">
        Documento: {{ delivery.delivery_document }}
      </small>
    </div>
  </article>
</template>
