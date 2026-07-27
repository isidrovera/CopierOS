<script setup>
import RentalResourceForm from "./RentalResourceForm.vue"

import {
  searchAssignments,
  searchBranches,
  searchContacts,
  searchContracts,
  searchPartners,
  searchRentalEquipment,
} from "./rental-lookups"


const fields = [
  {
    type: "section",
    label: "Contrato y equipo",
    help: "Selecciona por código, cliente, serie, marca o modelo.",
  },
  {
    key: "code",
    label: "Código de asignación",
    required: true,
    placeholder: "Ejemplo: ASG-0001",
  },
  {
    key: "contract",
    label: "Contrato",
    type: "search",
    required: true,
    displayKey: "contract_code",
    placeholder: "Buscar por código, número o cliente",
    loader: searchContracts,
    onSelect(option, form, labels) {
      const contract = option?.raw

      if (!contract) {
        return
      }

      form.customer = contract.customer || ""
      labels.customer = contract.customer_name || ""

      form.branch = contract.main_branch || ""
      labels.branch = contract.main_branch_name || ""

      form.contact = contract.main_contact || ""
      labels.contact = contract.main_contact_name || ""
    },
  },
  {
    key: "rental_equipment",
    label: "Equipo de alquiler",
    type: "search",
    required: true,
    displayKey: "rental_equipment_display",
    placeholder: "Buscar por serie, código, marca o modelo",
    loader: searchRentalEquipment,
  },
  {
    type: "section",
    label: "Cliente y ubicación",
    help: "La sede y el contacto se filtran según el cliente seleccionado.",
  },
  {
    key: "customer",
    label: "Cliente",
    type: "search",
    required: true,
    displayKey: "customer_name",
    placeholder: "Buscar por razón social, nombre o documento",
    loader: searchPartners,
    onSelect(option, form, labels) {
      form.branch = ""
      form.contact = ""
      labels.branch = ""
      labels.contact = ""
    },
  },
  {
    key: "branch",
    label: "Sede",
    type: "search",
    required: true,
    displayKey: "branch_name",
    placeholder: "Buscar sede o dirección",
    disabled: (form) => !form.customer,
    loader: (search, form) => searchBranches(search, form.customer),
    onSelect(option, form, labels) {
      form.contact = ""
      labels.contact = ""
    },
  },
  {
    key: "contact",
    label: "Contacto",
    type: "search",
    displayKey: "contact_name",
    placeholder: "Buscar contacto por nombre, teléfono o correo",
    disabled: (form) => !form.customer,
    loader: (search, form) => searchContacts(
      search,
      form.customer,
      form.branch
    ),
  },
  {
    key: "site_location",
    label: "Ubicación del equipo dentro de la sede",
    full: true,
    placeholder: "Ejemplo: Segundo piso, área de contabilidad",
  },
  {
    type: "section",
    label: "Programación y estado",
  },
  {
    key: "status",
    label: "Estado",
    type: "select",
    required: true,
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
  {
    key: "scheduled_installation_date",
    label: "Fecha programada de instalación",
    type: "date",
    nullWhenEmpty: true,
  },
  {
    key: "installation_notes",
    label: "Indicaciones para la instalación",
    type: "textarea",
    full: true,
  },
  {
    key: "notes",
    label: "Observaciones",
    type: "textarea",
    full: true,
  },
]

const defaults = {
  status: "draft",
}
</script>

<template>
  <RentalResourceForm
    title="asignación"
    resource="assignments"
    list-route="rental-assignment-list"
    :fields="fields"
    :defaults="defaults"
  />
</template>
