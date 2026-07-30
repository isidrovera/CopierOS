<script setup>
import "./RepairPartSourceCard.css"

defineProps({
  source: { type: Object, required: true },
})
</script>

<template>
  <article class="repair-part-source-card">
    <header>
      <strong>{{ source.source_type_name }}</strong>
      <span>{{ source.is_confirmed ? "Confirmado" : "Pendiente" }}</span>
    </header>

    <div>
      <small v-if="source.inventory_code">
        Inventario: {{ source.inventory_code }}
      </small>

      <small v-if="source.rental_warehouse_name">
        Almacén: {{ source.rental_warehouse_name }}
      </small>

      <small v-if="source.donor_equipment_code">
        Equipo: {{ source.donor_equipment_code }}
      </small>

      <small v-if="source.supplier_name">
        Proveedor: {{ source.supplier_name }}
      </small>

      <small>
        Disponible: {{ source.available_quantity }}
      </small>

      <small>
        Reservada: {{ source.reserved_quantity }}
      </small>
    </div>
  </article>
</template>
