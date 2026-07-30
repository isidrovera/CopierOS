<script setup>
import "./RepairPartReplacementCard.css"
import RepairPartRequestStatusBadge from "./RepairPartRequestStatusBadge.vue"

defineProps({
  replacement: { type: Object, required: true },
})
</script>

<template>
  <article class="repair-part-replacement-card">
    <header>
      <strong>{{ replacement.replacement_type_name }}</strong>

      <RepairPartRequestStatusBadge
        :status="replacement.status"
        :label="replacement.status_name"
      />
    </header>

    <div>
      <small v-if="replacement.source_equipment_code">
        Equipo: {{ replacement.source_equipment_code }}
      </small>
      <small v-if="replacement.responsible_user_name">
        Responsable: {{ replacement.responsible_user_name }}
      </small>
      <small v-if="replacement.due_at">
        Fecha límite: {{ replacement.due_at }}
      </small>
      <small v-if="replacement.external_reference">
        Referencia: {{ replacement.external_reference }}
      </small>
    </div>
  </article>
</template>
