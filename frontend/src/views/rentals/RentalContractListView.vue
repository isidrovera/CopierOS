<script setup>
import RentalResourceList from "./RentalResourceList.vue"


const columns = [
  { key: "code", label: "Código" },
  { key: "contract_number", label: "Contrato" },
  { key: "customer_name", label: "Cliente" },
  { key: "main_branch_name", label: "Sede principal" },
  { key: "status_display", label: "Estado", badge: true },
  { key: "start_date", label: "Inicio", type: "date" },
  { key: "end_date", label: "Fin", type: "date" },
  { key: "active_equipment_count", label: "Equipos activos" },
]

const filters = [
  {
    key: "status",
    label: "Todos los estados",
    options: [
      { value: "draft", label: "Borrador" },
      { value: "pending_approval", label: "Pendiente de aprobación" },
      { value: "approved", label: "Aprobado" },
      { value: "active", label: "Activo" },
      { value: "suspended", label: "Suspendido" },
      { value: "expired", label: "Vencido" },
      { value: "terminated", label: "Terminado" },
      { value: "cancelled", label: "Cancelado" },
    ],
  },
]
</script>

<template>
  <RentalResourceList
    title="Contratos de alquiler"
    subtitle="Contratos, vigencia, cliente y cantidad de equipos asignados."
    resource="contracts"
    create-route="rental-contract-create"
    edit-route="rental-contract-edit"
    :columns="columns"
    :filters="filters"
  />
</template>
