<script setup>
import RentalResourceForm from "./RentalResourceForm.vue"

import {
  searchBranches,
  searchContacts,
  searchRentalCustomers,
} from "./rental-lookups"


const fields = [
  {
    type: "section",
    label: "Identificación del contrato",
  },
  {
    key: "code",
    label: "Código interno",
    required: true,
    placeholder: "Ejemplo: CONT-0001",
  },
  {
    key: "contract_number",
    label: "Número de contrato",
    placeholder: "Número indicado en el documento",
  },
  {
    key: "customer",
    label: "Cliente",
    type: "search",
    required: true,
    displayKey: "customer_name",
    placeholder: "Buscar cliente de alquiler por razón social o documento",
    loader: searchRentalCustomers,
    onSelect(option, form, labels) {
      form.main_branch = ""
      form.main_contact = ""

      labels.main_branch = ""
      labels.main_contact = ""
    },
  },
  {
    key: "main_branch",
    label: "Sede principal",
    type: "search",
    displayKey: "main_branch_name",
    placeholder: "Buscar sede o dirección",
    disabled: (form) => !form.customer,
    loader: (search, form) => (
      searchBranches(
        search,
        form.customer,
      )
    ),
    onSelect(option, form, labels) {
      form.main_contact = ""
      labels.main_contact = ""
    },
  },
  {
    key: "main_contact",
    label: "Contacto principal",
    type: "search",
    displayKey: "main_contact_name",
    placeholder: "Buscar contacto por nombre, teléfono o correo",
    disabled: (form) => !form.customer,
    loader: (search, form) => (
      searchContacts(
        search,
        form.customer,
        form.main_branch,
      )
    ),
  },
  {
    type: "section",
    label: "Vigencia y estado",
  },
  {
    key: "contract_type",
    label: "Tipo de contrato",
    type: "select",
    required: true,
    options: [
      {
        value: "fixed_term",
        label: "Plazo determinado",
      },
      {
        value: "open_ended",
        label: "Plazo indeterminado",
      },
      {
        value: "temporary",
        label: "Temporal",
      },
      {
        value: "demonstration",
        label: "Demostración",
      },
      {
        value: "other",
        label: "Otro",
      },
    ],
  },
  {
    key: "status",
    label: "Estado",
    type: "select",
    required: true,
    options: [
      {
        value: "draft",
        label: "Borrador",
      },
      {
        value: "pending_approval",
        label: "Pendiente de aprobación",
      },
      {
        value: "approved",
        label: "Aprobado",
      },
      {
        value: "active",
        label: "Activo",
      },
      {
        value: "suspended",
        label: "Suspendido",
      },
      {
        value: "expired",
        label: "Vencido",
      },
      {
        value: "terminated",
        label: "Finalizado",
      },
      {
        value: "cancelled",
        label: "Cancelado",
      },
    ],
  },
  {
    key: "start_date",
    label: "Fecha de inicio",
    type: "date",
    required: true,
  },
  {
    key: "end_date",
    label: "Fecha de finalización",
    type: "date",
    nullWhenEmpty: true,
    help: (
      "Es obligatoria para contratos de plazo determinado "
      + "cuando estén aprobados o activos."
    ),
  },
  {
    key: "external_reference",
    label: "Referencia externa",
    placeholder: (
      "Orden de compra, cotización u otra referencia"
    ),
  },
  {
    type: "section",
    label: "Condiciones y observaciones",
  },
  {
    key: "service_conditions",
    label: "Condiciones del servicio",
    type: "textarea",
    full: true,
  },
  {
    key: "customer_requirements",
    label: "Requerimientos del cliente",
    type: "textarea",
    full: true,
  },
  {
    key: "suspension_reason",
    label: "Motivo de suspensión",
    type: "textarea",
    full: true,
    visible: (form) => (
      form.status === "suspended"
    ),
    required: (form) => (
      form.status === "suspended"
    ),
  },
  {
    key: "termination_reason",
    label: "Motivo de finalización",
    type: "textarea",
    full: true,
    visible: (form) => (
      form.status === "terminated"
    ),
    required: (form) => (
      form.status === "terminated"
    ),
  },
  {
    key: "cancellation_reason",
    label: "Motivo de cancelación",
    type: "textarea",
    full: true,
    visible: (form) => (
      form.status === "cancelled"
    ),
    required: (form) => (
      form.status === "cancelled"
    ),
  },
  {
    key: "notes",
    label: "Observaciones",
    type: "textarea",
    full: true,
  },
]


const defaults = {
  contract_type: "fixed_term",
  status: "draft",
}
</script>


<template>
  <RentalResourceForm
    title="contrato"
    resource="contracts"
    list-route="rental-contract-list"
    :fields="fields"
    :defaults="defaults"
  />
</template>