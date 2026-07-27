<script setup>
import RentalResourceList from "./RentalResourceList.vue"


const columns = [
  { key: "code", label: "Asignación" },
  { key: "contract_code", label: "Contrato" },
  { key: "customer_name", label: "Cliente" },
  { key: "branch_name", label: "Sede" },
  { key: "equipment_serial_number", label: "Serie" },
  { key: "equipment_model_name", label: "Modelo" },
  { key: "status_display", label: "Estado", badge: true },
  { key: "scheduled_installation_date", label: "Instalación", type: "date" },
]

const filters = [
  {
    key: "status",
    label: "Todos los estados",
    options: [
      { value: "draft", label: "Borrador" },
      { value: "reserved", label: "Reservado" },
      { value: "installation_pending", label: "Pendiente de instalación" },
      { value: "installed", label: "Instalado" },
      { value: "active", label: "Alquiler activo" },
      { value: "removal_pending", label: "Pendiente de retiro" },
      { value: "removed", label: "Retirado" },
      { value: "cancelled", label: "Cancelado" },
    ],
  },
]
</script>

<template>
  <RentalResourceList
    title="Asignaciones"
    subtitle="Relación actual entre contrato, cliente, sede y máquina."
    resource="assignments"
    create-route="rental-assignment-create"
    edit-route="rental-assignment-edit"
    :columns="columns"
    :filters="filters"
  />
</template>
