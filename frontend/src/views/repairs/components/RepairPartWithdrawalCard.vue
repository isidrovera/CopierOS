<script setup>
import "./RepairPartWithdrawalCard.css"
import RepairPartRequestStatusBadge from "./RepairPartRequestStatusBadge.vue"

defineProps({
  withdrawal: { type: Object, required: true },
})
</script>

<template>
  <article class="repair-part-withdrawal-card">
    <header>
      <strong>Retiro</strong>

      <RepairPartRequestStatusBadge
        :status="withdrawal.status"
        :label="withdrawal.status_name"
      />
    </header>

    <div>
      <small>Cantidad: {{ withdrawal.quantity }}</small>
      <small v-if="withdrawal.authorized_person_name">
        Autorizado: {{ withdrawal.authorized_person_name }}
      </small>
      <small v-if="withdrawal.authorized_at">
        {{ withdrawal.authorized_at }}
      </small>
      <small v-if="withdrawal.withdrawn_at">
        Retirado: {{ withdrawal.withdrawn_at }}
      </small>
      <small v-if="withdrawal.received_at">
        Recibido: {{ withdrawal.received_at }}
      </small>
    </div>
  </article>
</template>
