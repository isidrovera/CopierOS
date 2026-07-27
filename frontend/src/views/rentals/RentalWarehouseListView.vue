<script setup>
import RentalResourceList from "./RentalResourceList.vue"


const columns = [
  { key: "code", label: "Código" },
  { key: "name", label: "Almacén" },
  { key: "address", label: "Dirección" },
  { key: "equipment_count", label: "Equipos" },
  { key: "available_equipment_count", label: "Disponibles" },
  { key: "preparation_equipment_count", label: "En preparación" },
  { key: "problem_equipment_count", label: "Con problemas" },
  { key: "is_active", label: "Activo" },
]
</script>

<template>
  <RentalResourceList
    title="Almacenes de alquiler"
    subtitle="Ubicaciones físicas y resumen de la flota almacenada."
    resource="warehouses"
    create-route="rental-warehouse-create"
    edit-route="rental-warehouse-edit"
    :columns="columns"
  />
</template>
