<script setup>
import RentalResourceForm from "./RentalResourceForm.vue"


const fields = [
  {
    type: "section",
    label: "Datos del almacén",
  },
  {
    key: "code",
    label: "Código",
    required: true,
    placeholder: "Ejemplo: ALM-ANDES-01",
  },
  {
    key: "name",
    label: "Nombre",
    required: true,
    placeholder: "Nombre visible del almacén",
  },
  {
    key: "address",
    label: "Dirección",
    full: true,
  },
  {
    key: "description",
    label: "Descripción",
    type: "textarea",
    full: true,
  },
  {
    key: "display_order",
    label: "Orden de visualización",
    type: "number",
    min: 0,
  },
  {
    type: "section",
    label: "Permisos operativos",
  },
  {
    key: "is_active",
    label: "Almacén activo",
    type: "checkbox",
  },
  {
    key: "allows_entries",
    label: "Permite ingresos",
    type: "checkbox",
  },
  {
    key: "allows_dispatches",
    label: "Permite despachos",
    type: "checkbox",
  },
  {
    key: "notes",
    label: "Observaciones",
    type: "textarea",
    full: true,
  },
]

const defaults = {
  display_order: 0,
  is_active: true,
  allows_entries: true,
  allows_dispatches: true,
}
</script>

<template>
  <RentalResourceForm
    title="almacén"
    resource="warehouses"
    list-route="rental-warehouse-list"
    :fields="fields"
    :defaults="defaults"
  />
</template>
