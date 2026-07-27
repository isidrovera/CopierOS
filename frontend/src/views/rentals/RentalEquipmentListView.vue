<script setup>
import RentalResourceList from "./RentalResourceList.vue"


const columns = [
  { key: "equipment_serial_number", label: "Serie" },
  { key: "equipment_brand_name", label: "Marca" },
  { key: "equipment_model_name", label: "Modelo" },
  { key: "warehouse_name", label: "Almacén" },
  { key: "operational_status_display", label: "Estado", badge: true },
  { key: "is_available_for_rental", label: "Disponible" },
]

const filters = [
  {
    key: "operational_status",
    label: "Todos los estados",
    options: [
      { value: "pending_preparation", label: "Pendiente de preparación" },
      { value: "in_preparation", label: "En preparación" },
      { value: "available", label: "Disponible" },
      { value: "reserved", label: "Reservado" },
      { value: "assigned", label: "Asignado" },
      { value: "installed", label: "Instalado" },
      { value: "with_problems", label: "Con problemas" },
      { value: "for_parts", label: "De partes" },
    ],
  },
]
</script>

<template>
  <RentalResourceList
    title="Flota de alquiler"
    subtitle="Máquinas administradas por ANDES para alquiler, reemplazo o uso interno."
    resource="equipment"
    create-route="rental-equipment-create"
    edit-route="rental-equipment-edit"
    :columns="columns"
    :filters="filters"
  />
</template>
