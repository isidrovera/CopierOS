<script setup>
import RentalResourceForm from "./RentalResourceForm.vue"

import {
  searchEquipment,
  searchSuppliers,
  searchWarehouses,
} from "./rental-lookups"


const fields = [
  {
    type: "section",
    label: "Máquina para alquiler",
    help: (
      "Busca una máquina de ANDES por serie, "
      + "código interno, marca o modelo."
    ),
  },
  {
    key: "equipment",
    label: "Equipo",
    type: "search",
    required: true,
    displayKey: "equipment_display",
    placeholder: (
      "Buscar por serie, código, marca o modelo"
    ),
    loader: searchEquipment,
  },
  {
    key: "purpose",
    label: "Finalidad",
    type: "select",
    required: true,
    options: [
      {
        value: "rental",
        label: "Alquiler",
      },
    ],
    help: (
      "Esta vista administra únicamente máquinas "
      + "propias destinadas al alquiler."
    ),
  },
  {
    key: "acquisition_source",
    label: "Origen de adquisición",
    type: "select",
    required: true,
    options: [
      {
        value: "corapsac",
        label: "Compra a Corapsac",
      },
      {
        value: "external_supplier",
        label: "Proveedor externo",
      },
      {
        value: "customer_owned",
        label: "Propiedad de cliente",
      },
    ],
  },
  {
    key: "supplier",
    label: "Proveedor",
    type: "search",
    displayKey: "supplier_name",
    placeholder: (
      "Buscar proveedor por nombre o documento"
    ),
    loader: searchSuppliers,
    help: (
      "Es obligatorio cuando el origen es "
      + "Corapsac o proveedor externo."
    ),
  },
  {
    type: "section",
    label: "Ubicación y condición operativa",
  },
  {
    key: "warehouse",
    label: "Almacén actual",
    type: "search",
    required: true,
    displayKey: "warehouse_name",
    placeholder: (
      "Buscar almacén de alquiler por código o nombre"
    ),
    loader: searchWarehouses,
  },
  {
    key: "warehouse_location",
    label: "Ubicación dentro del almacén",
    placeholder: (
      "Pasillo, zona, nivel o posición"
    ),
  },
  {
    key: "operational_status",
    label: "Estado operativo",
    type: "select",
    required: true,
    options: [
      {
        value: "received",
        label: "Recibido",
      },
      {
        value: "in_warehouse",
        label: "En almacén",
      },
      {
        value: "pending_preparation",
        label: "Pendiente de preparación",
      },
      {
        value: "in_preparation",
        label: "En preparación",
      },
      {
        value: "ready_for_rental",
        label: "Lista para alquiler",
      },
      {
        value: "rented",
        label: "Alquilada",
      },
      {
        value: "removal_pending",
        label: "Pendiente de retiro",
      },
      {
        value: "returned_to_warehouse",
        label: "Retornada al almacén",
      },
      {
        value: "with_problems",
        label: "Con problemas",
      },
      {
        value: "for_parts",
        label: "De partes",
      },
      {
        value: "out_of_service",
        label: "Fuera de servicio",
      },
    ],
  },
  {
    key: "entry_date",
    label: "Fecha de ingreso",
    type: "date",
    required: true,
  },
  {
    key: "is_available_for_rental",
    label: "Disponible para alquiler",
    type: "checkbox",
    help: (
      "Solo puede activarse cuando el estado "
      + "sea «Lista para alquiler»."
    ),
  },
  {
    type: "section",
    label: "Documentación de adquisición",
  },
  {
    key: "acquisition_document",
    label: "Documento de adquisición",
    placeholder: (
      "Factura, guía u otro documento"
    ),
  },
  {
    key: "acquisition_reference",
    label: "Referencia",
    placeholder: (
      "Número o referencia de compra"
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
  purpose: "rental",
  acquisition_source: "corapsac",
  operational_status: "received",
  is_available_for_rental: false,
}
</script>


<template>
  <RentalResourceForm
    title="equipo de alquiler"
    resource="equipment"
    list-route="rental-equipment-list"
    :fields="fields"
    :defaults="defaults"
  />
</template>