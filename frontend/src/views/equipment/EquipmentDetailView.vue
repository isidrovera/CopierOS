<script setup>
import {
  computed,
  onMounted,
  ref,
} from "vue"

import {
  useRoute,
  useRouter,
} from "vue-router"

import {
  archiveEquipment,
  changeEquipmentCommercialStatus,
  changeEquipmentTechnicalStatus,
  getEquipmentById,
  getEquipmentDocuments,
  getEquipmentMovements,
  getMeterReadings,
  restoreEquipment,
} from "../../services/equipment.service"

import {
  getRepairs,
} from "../../services/repairs.service"


const route = useRoute()
const router = useRouter()

const equipment = ref(null)
const movements = ref([])
const meterReadings = ref([])
const documents = ref([])
const repairs = ref([])

const loading = ref(false)
const loadingRelations = ref(false)
const processing = ref(false)

const errorMessage = ref("")
const successMessage = ref("")

const activeTab = ref("general")

const statusModalOpen = ref(false)
const statusModalType = ref("")
const selectedStatus = ref("")
const statusReason = ref("")
const modalError = ref("")


const equipmentId = computed(() => {
  return String(
    route.params.id || ""
  )
})


const activeRepair = computed(() => {
  return (
    repairs.value.find(
      (repair) =>
        repair.is_active === true &&
        !repair.is_archived
    ) ||
    null
  )
})


const hasActiveRepair = computed(() => {
  return Boolean(
    activeRepair.value?.id
  )
})


const technicalStatusOptions = [
  {
    value: "unreviewed",
    label: "Sin revisar",
  },
  {
    value: "for_review",
    label: "Para revisión",
  },
  {
    value: "in_review",
    label: "En revisión",
  },
  {
    value: "completed",
    label: "Finalizada",
  },
  {
    value: "with_problems",
    label: "Con problemas",
  },
  {
    value: "for_parts",
    label: "De partes",
  },
]


const commercialStatusOptions = [
  {
    value: "warehouse",
    label: "En almacén",
  },
  {
    value: "reserved",
    label: "Separada",
  },
  {
    value: "sold",
    label: "Vendida",
  },
  {
    value: "delivery_preparation",
    label: "En preparación de entrega",
  },
  {
    value: "in_transit",
    label: "En tránsito",
  },
  {
    value: "delivered",
    label: "Entregada",
  },
  {
    value: "contract_assigned",
    label: "Asignada a contrato",
  },
  {
    value: "installed",
    label: "Instalada",
  },
  {
    value: "return_process",
    label: "En proceso de retorno",
  },
  {
    value: "returned",
    label: "Retornada a almacén",
  },
  {
    value: "temporary_loan",
    label: "Préstamo temporal",
  },
  {
    value: "demonstration",
    label: "Demostración",
  },
  {
    value: "replacement",
    label: "Equipo de reemplazo",
  },
  {
    value: "out_of_service",
    label: "Fuera de servicio",
  },
  {
    value: "disposed",
    label: "De baja",
  },
]


const statusModalTitle = computed(() => {
  return statusModalType.value === "technical"
    ? "Cambiar estado técnico"
    : "Cambiar estado comercial"
})


const statusOptions = computed(() => {
  return statusModalType.value === "technical"
    ? technicalStatusOptions
    : commercialStatusOptions
})


const equipmentName = computed(() => {
  if (!equipment.value) {
    return "Equipo"
  }

  const brand =
    equipment.value.brand_name ||
    equipment.value.equipment_model_detail
      ?.brand_name ||
    equipment.value.equipment_model_data
      ?.brand_name ||
    ""

  const model =
    equipment.value.model_name ||
    equipment.value.equipment_model_name ||
    equipment.value.equipment_model_detail
      ?.name ||
    equipment.value.equipment_model_data
      ?.name ||
    ""

  return (
    [
      brand,
      model,
    ]
      .filter(Boolean)
      .join(" ")
      .trim() ||
    equipment.value.serial_number ||
    equipment.value.internal_code ||
    "Equipo"
  )
})


const customerName = computed(() => {
  const item = equipment.value

  if (!item) {
    return "Sin cliente"
  }

  return (
    item.customer_name ||
    item.customer_detail?.display_name ||
    item.customer_detail?.trade_name ||
    item.customer_detail?.legal_name ||
    "Sin cliente"
  )
})


const branchName = computed(() => {
  const item = equipment.value

  if (!item) {
    return "Sin sucursal"
  }

  return (
    item.customer_branch_name ||
    item.customer_branch_detail?.display_name ||
    item.customer_branch_detail?.name ||
    "Sin sucursal"
  )
})


const advisorName = computed(() => {
  const item = equipment.value

  if (!item) {
    return "Sin asesor"
  }

  return (
    item.advisor_name ||
    item.advisor_detail?.full_name ||
    item.advisor_detail?.name ||
    "Sin asesor"
  )
})


const modelName = computed(() => {
  const item = equipment.value

  if (!item) {
    return "Sin modelo"
  }

  return (
    item.model_name ||
    item.equipment_model_name ||
    item.equipment_model_detail?.name ||
    item.equipment_model_data?.name ||
    "Sin modelo"
  )
})


const brandName = computed(() => {
  const item = equipment.value

  if (!item) {
    return "Sin marca"
  }

  return (
    item.brand_name ||
    item.equipment_model_detail?.brand_name ||
    item.equipment_model_data?.brand_name ||
    "Sin marca"
  )
})


const equipmentTypeName = computed(() => {
  const item = equipment.value

  if (!item) {
    return "Sin tipo"
  }

  return (
    item.equipment_type_name ||
    item.equipment_model_detail
      ?.equipment_type_name ||
    item.equipment_model_data
      ?.equipment_type_name ||
    "Sin tipo"
  )
})


function normalizeList(response) {
  if (Array.isArray(response)) {
    return response
  }

  if (
    response &&
    Array.isArray(response.results)
  ) {
    return response.results
  }

  return []
}


function getTechnicalStatusName(value) {
  const names = {
    unreviewed: "Sin revisar",
    for_review: "Para revisión",
    in_review: "En revisión",
    completed: "Finalizada",
    with_problems: "Con problemas",
    for_parts: "De partes",
  }

  return (
    names[value] ||
    value ||
    "Sin estado"
  )
}


function getCommercialStatusName(value) {
  const names = {
    warehouse: "En almacén",
    reserved: "Separada",
    sold: "Vendida",
    delivery_preparation:
      "En preparación de entrega",
    in_transit: "En tránsito",
    delivered: "Entregada",
    contract_assigned:
      "Asignada a contrato",
    installed: "Instalada",
    return_process:
      "En proceso de retorno",
    returned: "Retornada a almacén",
    temporary_loan:
      "Préstamo temporal",
    demonstration: "Demostración",
    replacement:
      "Equipo de reemplazo",
    out_of_service:
      "Fuera de servicio",
    disposed: "De baja",
  }

  return (
    names[value] ||
    value ||
    "Sin estado"
  )
}


function getPhysicalConditionName(value) {
  const names = {
    new: "Nueva",
    used: "Usada",
    reconditioned:
      "Reacondicionada",
    trade_in:
      "Recibida en parte de pago",
    third_party:
      "Propiedad de tercero",
    other: "Otra",
  }

  return (
    names[value] ||
    value ||
    "Sin condición"
  )
}


function getOwnershipName(value) {
  const names = {
    own:
      "Propiedad de la empresa",
    customer:
      "Propiedad de cliente",
    supplier:
      "Propiedad de proveedor",
    third_party:
      "Propiedad de tercero",
    other: "Otra",
  }

  return (
    names[value] ||
    value ||
    "Sin propiedad"
  )
}


function getMovementTypeName(value) {
  const names = {
    registration:
      "Registro inicial",
    unloading:
      "Descarga",
    warehouse_entry:
      "Ingreso a almacén",
    location_change:
      "Cambio de ubicación",
    sent_for_review:
      "Envío para revisión",
    review_started:
      "Inicio de revisión",
    review_completed:
      "Revisión finalizada",
    problem_reported:
      "Problema reportado",
    marked_for_parts:
      "Destinada a partes",
    reserved:
      "Separación",
    reservation_released:
      "Liberación de separación",
    sold:
      "Venta",
    delivery_preparation:
      "Preparación de entrega",
    dispatched:
      "Salida para entrega",
    delivered:
      "Entrega",
    contract_assigned:
      "Asignación a contrato",
    installed:
      "Instalación",
    removal_started:
      "Inicio de retiro",
    removed:
      "Retiro",
    returned_to_warehouse:
      "Retorno a almacén",
    temporary_loan:
      "Préstamo temporal",
    demonstration:
      "Demostración",
    replacement_assigned:
      "Asignación como reemplazo",
    sent_to_supplier:
      "Envío a proveedor",
    received_from_supplier:
      "Recepción desde proveedor",
    ownership_change:
      "Cambio de propiedad",
    out_of_service:
      "Fuera de servicio",
    reactivated:
      "Reactivación",
    disposed:
      "Baja del equipo",
    archived:
      "Archivado",
    restored:
      "Restaurado",
    other:
      "Otro movimiento",
  }

  return (
    names[value] ||
    value ||
    "Movimiento"
  )
}


function getReadingTypeName(value) {
  const names = {
    normal:
      "Lectura normal",
    initial:
      "Lectura inicial",
    correction:
      "Corrección",
    reset:
      "Reinicio de contador",
    estimated:
      "Lectura estimada",
  }

  return (
    names[value] ||
    value ||
    "Lectura"
  )
}


function getDocumentTypeName(value) {
  const names = {
    purchase_invoice:
      "Factura o invoice de compra",
    sale_invoice:
      "Factura de venta",
    import_document:
      "Documento de importación",
    customs_document:
      "Documento aduanero",
    packing_list:
      "Lista de empaque",
    shipping_document:
      "Documento de transporte",
    delivery_note:
      "Guía de remisión",
    delivery_certificate:
      "Acta de entrega",
    installation_certificate:
      "Acta de instalación",
    removal_certificate:
      "Acta de retiro",
    technical_report:
      "Informe técnico",
    repair_report:
      "Informe de reparación",
    technical_sheet:
      "Ficha técnica",
    user_manual:
      "Manual de usuario",
    service_manual:
      "Manual de servicio",
    warranty:
      "Garantía",
    certificate:
      "Certificado",
    contract:
      "Contrato",
    quotation:
      "Cotización",
    purchase_order:
      "Orden de compra",
    photo:
      "Fotografía",
    other:
      "Otro documento",
  }

  return (
    names[value] ||
    value ||
    "Documento"
  )
}


function getRepairStatusName(value) {
  const names = {
    pending:
      "Pendiente",
    assigned:
      "Asignada",
    under_review:
      "En revisión",
    waiting_parts:
      "Esperando repuestos",
    in_repair:
      "En reparación",
    testing:
      "En pruebas",
    completed:
      "Finalizada",
    delivered:
      "Entregada",
    cancelled:
      "Cancelada",
  }

  return (
    names[value] ||
    value ||
    "Sin estado"
  )
}


function getRepairTypeName(value) {
  const names = {
    initial_review:
      "Revisión inicial",
    preventive:
      "Mantenimiento preventivo",
    corrective:
      "Mantenimiento correctivo",
    reconditioning:
      "Reacondicionamiento",
    warranty:
      "Garantía",
    return_review:
      "Revisión por devolución",
    other:
      "Otro",
  }

  return (
    names[value] ||
    value ||
    "Sin tipo"
  )
}


function getRepairPriorityName(value) {
  const names = {
    low: "Baja",
    normal: "Normal",
    high: "Alta",
    urgent: "Urgente",
  }

  return (
    names[value] ||
    value ||
    "Normal"
  )
}


function getRepairStatusClass(value) {
  const classes = {
    pending: "pending",
    assigned: "assigned",
    under_review: "review",
    waiting_parts: "waiting",
    in_repair: "repair",
    testing: "testing",
    completed: "completed",
    delivered: "delivered",
    cancelled: "cancelled",
  }

  return (
    classes[value] ||
    "neutral"
  )
}


function getRepairPriorityClass(value) {
  const classes = {
    low: "low",
    normal: "normal",
    high: "high",
    urgent: "urgent",
  }

  return (
    classes[value] ||
    "normal"
  )
}


function formatDate(value) {
  if (!value) {
    return "Sin registro"
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return "Sin registro"
  }

  return new Intl.DateTimeFormat(
    "es-PE",
    {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }
  ).format(date)
}


function formatDateTime(value) {
  if (!value) {
    return "Sin registro"
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return "Sin registro"
  }

  return new Intl.DateTimeFormat(
    "es-PE",
    {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }
  ).format(date)
}


function formatMeter(value) {
  const number = Number(
    value || 0
  )

  if (!Number.isFinite(number)) {
    return "0"
  }

  return new Intl.NumberFormat(
    "es-PE"
  ).format(number)
}


function formatMoney(
  value,
  currency = "PEN"
) {
  const number = Number(
    value || 0
  )

  if (!Number.isFinite(number)) {
    return "0.00"
  }

  try {
    return new Intl.NumberFormat(
      "es-PE",
      {
        style: "currency",
        currency:
          currency === "OTHER"
            ? "PEN"
            : currency,
      }
    ).format(number)
  } catch {
    return (
      `${number.toFixed(2)} ` +
      `${currency}`
    )
  }
}


async function loadEquipment() {
  loading.value = true
  errorMessage.value = ""

  try {
    equipment.value =
      await getEquipmentById(
        equipmentId.value
      )
  } catch (error) {
    equipment.value = null

    errorMessage.value =
      error.message ||
      "No se pudo cargar el equipo."
  } finally {
    loading.value = false
  }
}


async function loadRelations() {
  loadingRelations.value = true

  try {
    const [
      movementsResponse,
      readingsResponse,
      documentsResponse,
      repairsResponse,
    ] = await Promise.all([
      getEquipmentMovements({
        equipment:
          equipmentId.value,
      }),
      getMeterReadings({
        equipment:
          equipmentId.value,
      }),
      getEquipmentDocuments({
        equipment:
          equipmentId.value,
      }),
      getRepairs({
        equipment:
          equipmentId.value,
        includeArchived: true,
        ordering:
          "-requested_at",
      }),
    ])

    movements.value =
      normalizeList(
        movementsResponse
      )

    meterReadings.value =
      normalizeList(
        readingsResponse
      )

    documents.value =
      normalizeList(
        documentsResponse
      )

    repairs.value =
      normalizeList(
        repairsResponse
      )
  } catch (error) {
    movements.value = []
    meterReadings.value = []
    documents.value = []
    repairs.value = []

    errorMessage.value =
      error.message ||
      "No se pudieron cargar los registros relacionados."
  } finally {
    loadingRelations.value = false
  }
}


async function goBack() {
  await router.push({
    name: "equipment",
  })
}


async function goToEdit() {
  await router.push({
    name: "equipment-edit",
    params: {
      id: equipmentId.value,
    },
  })
}


async function goToCreateRepair() {
  if (
    !equipment.value ||
    equipment.value.is_archived ||
    processing.value
  ) {
    return
  }

  if (hasActiveRepair.value) {
    await goToRepair(
      activeRepair.value
    )

    return
  }

  await router.push({
    name: "repair-create",
    query: {
      equipment:
        equipmentId.value,
      origin:
        "equipment-detail",
    },
  })
}


async function goToRepair(repair) {
  if (!repair?.id) {
    return
  }

  await router.push({
    name: "repair-detail",
    params: {
      id: repair.id,
    },
  })
}


function openStatusModal(type) {
  if (
    !equipment.value ||
    equipment.value.is_archived ||
    processing.value
  ) {
    return
  }

  statusModalType.value = type

  selectedStatus.value =
    type === "technical"
      ? equipment.value
          .technical_status
      : equipment.value
          .commercial_status

  statusReason.value = ""
  modalError.value = ""
  statusModalOpen.value = true
}


function closeStatusModal() {
  if (processing.value) {
    return
  }

  statusModalOpen.value = false
  statusModalType.value = ""
  selectedStatus.value = ""
  statusReason.value = ""
  modalError.value = ""
}


async function submitStatusChange() {
  if (!selectedStatus.value) {
    modalError.value =
      "Selecciona el nuevo estado."

    return
  }

  if (!statusReason.value.trim()) {
    modalError.value =
      "Indica el motivo del cambio."

    return
  }

  processing.value = true
  errorMessage.value = ""
  successMessage.value = ""
  modalError.value = ""

  try {
    if (
      statusModalType.value ===
      "technical"
    ) {
      await changeEquipmentTechnicalStatus(
        equipmentId.value,
        {
          technical_status:
            selectedStatus.value,
          reason:
            statusReason.value
              .trim(),
        }
      )

      successMessage.value =
        "Estado técnico actualizado."
    } else {
      await changeEquipmentCommercialStatus(
        equipmentId.value,
        {
          commercial_status:
            selectedStatus.value,
          customer:
            equipment.value
              .customer ||
            null,
          customer_branch:
            equipment.value
              .customer_branch ||
            null,
          advisor:
            equipment.value
              .advisor ||
            null,
          reason:
            statusReason.value
              .trim(),
        }
      )

      successMessage.value =
        "Estado comercial actualizado."
    }

    statusModalOpen.value = false

    await Promise.all([
      loadEquipment(),
      loadRelations(),
    ])
  } catch (error) {
    modalError.value =
      error.message ||
      "No se pudo cambiar el estado."
  } finally {
    processing.value = false
  }
}


async function handleArchive() {
  if (!equipment.value) {
    return
  }

  const reason = window.prompt(
    "Indica el motivo para archivar el equipo:"
  )

  if (reason === null) {
    return
  }

  const confirmed =
    window.confirm(
      `¿Confirmas que deseas archivar ${equipmentName.value}?`
    )

  if (!confirmed) {
    return
  }

  processing.value = true
  errorMessage.value = ""
  successMessage.value = ""

  try {
    await archiveEquipment(
      equipmentId.value,
      reason.trim()
    )

    successMessage.value =
      "Equipo archivado correctamente."

    await Promise.all([
      loadEquipment(),
      loadRelations(),
    ])
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo archivar el equipo."
  } finally {
    processing.value = false
  }
}


async function handleRestore() {
  if (!equipment.value) {
    return
  }

  const confirmed =
    window.confirm(
      `¿Confirmas que deseas restaurar ${equipmentName.value}?`
    )

  if (!confirmed) {
    return
  }

  processing.value = true
  errorMessage.value = ""
  successMessage.value = ""

  try {
    await restoreEquipment(
      equipmentId.value
    )

    successMessage.value =
      "Equipo restaurado correctamente."

    await Promise.all([
      loadEquipment(),
      loadRelations(),
    ])
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo restaurar el equipo."
  } finally {
    processing.value = false
  }
}


function openDocument(document) {
  const url =
    document.file_url ||
    document.file

  if (!url) {
    errorMessage.value =
      "El documento no tiene un archivo disponible."

    return
  }

  window.open(
    url,
    "_blank",
    "noopener,noreferrer"
  )
}


onMounted(async () => {
  await Promise.all([
    loadEquipment(),
    loadRelations(),
  ])
})
</script>

<template>
  <section class="equipment-detail-page">
    <header class="page-header">
      <div>
        <span class="page-kicker">
          Inventario de máquinas
        </span>

        <h2>
          {{ equipmentName }}
        </h2>

        <p v-if="equipment">
          Serie:
          <strong>
            {{ equipment.serial_number }}
          </strong>

          · Código:
          <strong>
            {{ equipment.internal_code }}
          </strong>
        </p>
      </div>

      <div class="header-actions">
        <button
          class="secondary-button"
          type="button"
          @click="goBack"
        >
          Volver
        </button>

        <button
          class="primary-button"
          type="button"
          :disabled="
            processing ||
            equipment?.is_archived
          "
          @click="goToEdit"
        >
          Editar equipo
        </button>
      </div>
    </header>

    <div
      v-if="successMessage"
      class="message success-message"
    >
      {{ successMessage }}
    </div>

    <div
      v-if="errorMessage"
      class="message error-message"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="loading"
      class="loading-card"
    >
      <span class="spinner"></span>

      Cargando equipo...
    </div>

    <template v-else-if="equipment">
      <section
        v-if="activeRepair"
        class="active-repair-card"
      >
        <div class="active-repair-icon">
          ⚙
        </div>

        <div class="active-repair-information">
          <span>
            Reparación activa
          </span>

          <strong>
            {{ activeRepair.code }}
          </strong>

          <small>
            {{
              activeRepair.status_name ||
              getRepairStatusName(
                activeRepair.status
              )
            }}
            ·
            {{
              activeRepair.assigned_technician_name ||
              "Sin técnico asignado"
            }}
          </small>
        </div>

        <button
          type="button"
          @click="goToRepair(activeRepair)"
        >
          Abrir reparación
        </button>
      </section>

      <section class="hero-card">
        <div class="equipment-photo">
          <img
            v-if="
              equipment.main_photo_url ||
              equipment.main_photo
            "
            :src="
              equipment.main_photo_url ||
              equipment.main_photo
            "
            alt="Fotografía del equipo"
          />

          <div
            v-else
            class="photo-placeholder"
          >
            ▣
          </div>
        </div>

        <div class="hero-information">
          <div class="hero-title">
            <div>
              <span>
                {{ equipmentTypeName }}
              </span>

              <h3>
                {{ brandName }}
                {{ modelName }}
              </h3>
            </div>

            <span
              class="availability-badge"
              :class="{
                available:
                  equipment.is_available &&
                  !equipment.is_archived,
                unavailable:
                  !equipment.is_available &&
                  !equipment.is_archived,
                archived:
                  equipment.is_archived,
              }"
            >
              {{
                equipment.is_archived
                  ? "Archivado"
                  : equipment.is_available
                    ? "Disponible"
                    : "No disponible"
              }}
            </span>
          </div>

          <div class="hero-grid">
            <div>
              <small>Serie</small>

              <strong>
                {{ equipment.serial_number }}
              </strong>
            </div>

            <div>
              <small>Código interno</small>

              <strong>
                {{ equipment.internal_code }}
              </strong>
            </div>

            <div>
              <small>Estado técnico</small>

              <strong>
                {{
                  equipment.technical_status_name ||
                  getTechnicalStatusName(
                    equipment.technical_status
                  )
                }}
              </strong>
            </div>

            <div>
              <small>Estado comercial</small>

              <strong>
                {{
                  equipment.commercial_status_name ||
                  getCommercialStatusName(
                    equipment.commercial_status
                  )
                }}
              </strong>
            </div>

            <div>
              <small>Ubicación</small>

              <strong>
                {{
                  equipment.warehouse_location ||
                  "Sin ubicación"
                }}
              </strong>
            </div>

            <div>
              <small>Cliente</small>

              <strong>
                {{ customerName }}
              </strong>
            </div>
          </div>
        </div>
      </section>

      <section class="quick-actions">
        <button
          v-if="!hasActiveRepair"
          class="repair-action-button"
          type="button"
          :disabled="
            processing ||
            equipment.is_archived
          "
          @click="goToCreateRepair"
        >
          Crear reparación
        </button>

        <button
          v-else
          class="repair-action-button active"
          type="button"
          :disabled="processing"
          @click="goToRepair(activeRepair)"
        >
          Abrir reparación activa
        </button>

        <button
          type="button"
          :disabled="
            processing ||
            equipment.is_archived
          "
          @click="openStatusModal('technical')"
        >
          Cambiar estado técnico
        </button>

        <button
          type="button"
          :disabled="
            processing ||
            equipment.is_archived
          "
          @click="openStatusModal('commercial')"
        >
          Cambiar estado comercial
        </button>

        <button
          v-if="!equipment.is_archived"
          class="danger-button"
          type="button"
          :disabled="processing"
          @click="handleArchive"
        >
          Archivar
        </button>

        <button
          v-else
          class="restore-button"
          type="button"
          :disabled="processing"
          @click="handleRestore"
        >
          Restaurar
        </button>
      </section>

      <nav class="detail-tabs">
        <button
          type="button"
          :class="{
            active:
              activeTab === 'general',
          }"
          @click="
            activeTab = 'general'
          "
        >
          Información general
        </button>

        <button
          type="button"
          :class="{
            active:
              activeTab === 'repairs',
          }"
          @click="
            activeTab = 'repairs'
          "
        >
          Reparaciones

          <span>
            {{ repairs.length }}
          </span>
        </button>

        <button
          type="button"
          :class="{
            active:
              activeTab === 'meters',
          }"
          @click="
            activeTab = 'meters'
          "
        >
          Contadores

          <span>
            {{ meterReadings.length }}
          </span>
        </button>

        <button
          type="button"
          :class="{
            active:
              activeTab === 'movements',
          }"
          @click="
            activeTab = 'movements'
          "
        >
          Movimientos

          <span>
            {{ movements.length }}
          </span>
        </button>

        <button
          type="button"
          :class="{
            active:
              activeTab === 'documents',
          }"
          @click="
            activeTab = 'documents'
          "
        >
          Documentos

          <span>
            {{ documents.length }}
          </span>
        </button>
      </nav>

      <div
        v-if="activeTab === 'general'"
        class="details-grid"
      >
        <section class="detail-card">
          <header>
            <h3>
              Identificación
            </h3>
          </header>

          <dl>
            <div>
              <dt>Marca</dt>
              <dd>{{ brandName }}</dd>
            </div>

            <div>
              <dt>Modelo</dt>
              <dd>{{ modelName }}</dd>
            </div>

            <div>
              <dt>Tipo</dt>
              <dd>{{ equipmentTypeName }}</dd>
            </div>

            <div>
              <dt>Condición física</dt>

              <dd>
                {{
                  equipment.physical_condition_name ||
                  getPhysicalConditionName(
                    equipment.physical_condition
                  )
                }}
              </dd>
            </div>

            <div>
              <dt>Tipo de propiedad</dt>

              <dd>
                {{
                  equipment.ownership_type_name ||
                  getOwnershipName(
                    equipment.ownership_type
                  )
                }}
              </dd>
            </div>

            <div>
              <dt>Código patrimonial</dt>

              <dd>
                {{
                  equipment.asset_number ||
                  "Sin registro"
                }}
              </dd>
            </div>
          </dl>
        </section>

        <section class="detail-card">
          <header>
            <h3>
              Estados
            </h3>
          </header>

          <dl>
            <div>
              <dt>Estado técnico</dt>

              <dd>
                {{
                  equipment.technical_status_name ||
                  getTechnicalStatusName(
                    equipment.technical_status
                  )
                }}
              </dd>
            </div>

            <div>
              <dt>Motivo técnico</dt>

              <dd>
                {{
                  equipment.technical_status_reason ||
                  "Sin observaciones"
                }}
              </dd>
            </div>

            <div>
              <dt>Estado comercial</dt>

              <dd>
                {{
                  equipment.commercial_status_name ||
                  getCommercialStatusName(
                    equipment.commercial_status
                  )
                }}
              </dd>
            </div>

            <div>
              <dt>Motivo comercial</dt>

              <dd>
                {{
                  equipment.commercial_status_reason ||
                  "Sin observaciones"
                }}
              </dd>
            </div>

            <div>
              <dt>Registro activo</dt>

              <dd>
                {{
                  equipment.is_active
                    ? "Sí"
                    : "No"
                }}
              </dd>
            </div>

            <div>
              <dt>Disponible</dt>

              <dd>
                {{
                  equipment.is_available
                    ? "Sí"
                    : "No"
                }}
              </dd>
            </div>
          </dl>
        </section>

        <section class="detail-card">
          <header>
            <h3>
              Cliente y ubicación
            </h3>
          </header>

          <dl>
            <div>
              <dt>Cliente</dt>
              <dd>{{ customerName }}</dd>
            </div>

            <div>
              <dt>Sucursal</dt>
              <dd>{{ branchName }}</dd>
            </div>

            <div>
              <dt>Asesor</dt>
              <dd>{{ advisorName }}</dd>
            </div>

            <div>
              <dt>Ubicación interna</dt>

              <dd>
                {{
                  equipment.warehouse_location ||
                  "Sin ubicación"
                }}
              </dd>
            </div>

            <div>
              <dt>Referencia</dt>

              <dd>
                {{
                  equipment.position_reference ||
                  "Sin referencia"
                }}
              </dd>
            </div>

            <div>
              <dt>Fecha de entrega</dt>

              <dd>
                {{
                  formatDateTime(
                    equipment.delivery_date
                  )
                }}
              </dd>
            </div>
          </dl>
        </section>

        <section class="detail-card">
          <header>
            <h3>
              Compra e importación
            </h3>
          </header>

          <dl>
            <div>
              <dt>Proveedor</dt>

              <dd>
                {{
                  equipment.supplier_name ||
                  "Sin proveedor"
                }}
              </dd>
            </div>

            <div>
              <dt>Lote o importación</dt>

              <dd>
                {{
                  equipment.import_batch_code ||
                  equipment.import_batch_name ||
                  equipment.import_reference ||
                  "Sin lote"
                }}
              </dd>
            </div>

            <div>
              <dt>Factura de compra</dt>

              <dd>
                {{
                  equipment.purchase_invoice_number ||
                  "Sin registro"
                }}
              </dd>
            </div>

            <div>
              <dt>Fecha de compra</dt>

              <dd>
                {{
                  formatDate(
                    equipment.purchase_date
                  )
                }}
              </dd>
            </div>

            <div>
              <dt>Precio de compra</dt>

              <dd>
                {{
                  formatMoney(
                    equipment.purchase_price,
                    equipment.purchase_currency
                  )
                }}
              </dd>
            </div>

            <div>
              <dt>Costo total</dt>

              <dd>
                {{
                  formatMoney(
                    equipment.total_acquisition_cost,
                    equipment.purchase_currency
                  )
                }}
              </dd>
            </div>
          </dl>
        </section>

        <section class="detail-card">
          <header>
            <h3>
              Venta
            </h3>
          </header>

          <dl>
            <div>
              <dt>Precio de venta</dt>

              <dd>
                {{
                  formatMoney(
                    equipment.sale_price,
                    equipment.sale_currency
                  )
                }}
              </dd>
            </div>

            <div>
              <dt>Factura de venta</dt>

              <dd>
                {{
                  equipment.sale_invoice_number ||
                  "Sin registro"
                }}
              </dd>
            </div>

            <div>
              <dt>Fecha de venta</dt>

              <dd>
                {{
                  formatDate(
                    equipment.sale_date
                  )
                }}
              </dd>
            </div>

            <div>
              <dt>Fecha de separación</dt>

              <dd>
                {{
                  formatDateTime(
                    equipment.reservation_date
                  )
                }}
              </dd>
            </div>

            <div>
              <dt>Vencimiento</dt>

              <dd>
                {{
                  formatDateTime(
                    equipment.reservation_expiration_date
                  )
                }}
              </dd>
            </div>
          </dl>
        </section>

        <section class="detail-card">
          <header>
            <h3>
              Red y firmware
            </h3>
          </header>

          <dl>
            <div>
              <dt>Hostname</dt>

              <dd>
                {{
                  equipment.hostname ||
                  "Sin registro"
                }}
              </dd>
            </div>

            <div>
              <dt>Dirección IP</dt>

              <dd>
                {{
                  equipment.ip_address ||
                  "Sin registro"
                }}
              </dd>
            </div>

            <div>
              <dt>Dirección MAC</dt>

              <dd>
                {{
                  equipment.mac_address ||
                  "Sin registro"
                }}
              </dd>
            </div>

            <div>
              <dt>Firmware</dt>

              <dd>
                {{
                  equipment.firmware_version ||
                  "Sin registro"
                }}
              </dd>
            </div>
          </dl>
        </section>

        <section
          class="detail-card full-width"
        >
          <header>
            <h3>
              Observaciones
            </h3>
          </header>

          <div class="notes-grid">
            <div>
              <strong>
                Configuración recibida
              </strong>

              <p>
                {{
                  equipment.accessories_description ||
                  "Sin observaciones"
                }}
              </p>
            </div>

            <div>
              <strong>
                Observaciones de descarga
              </strong>

              <p>
                {{
                  equipment.unloading_observations ||
                  "Sin observaciones"
                }}
              </p>
            </div>

            <div>
              <strong>
                Notas técnicas
              </strong>

              <p>
                {{
                  equipment.technical_notes ||
                  "Sin observaciones"
                }}
              </p>
            </div>

            <div>
              <strong>
                Notas comerciales
              </strong>

              <p>
                {{
                  equipment.commercial_notes ||
                  "Sin observaciones"
                }}
              </p>
            </div>

            <div>
              <strong>
                Observaciones generales
              </strong>

              <p>
                {{
                  equipment.notes ||
                  "Sin observaciones"
                }}
              </p>
            </div>
          </div>
        </section>
      </div>

      <section
        v-if="activeTab === 'repairs'"
        class="tab-card"
      >
        <div
          class="repairs-tab-header"
        >
          <div>
            <strong>
              Historial de reparaciones
            </strong>

            <span>
              {{ repairs.length }}
              registro(s)
            </span>
          </div>

          <button
            v-if="!hasActiveRepair"
            class="primary-button"
            type="button"
            :disabled="
              processing ||
              equipment.is_archived
            "
            @click="goToCreateRepair"
          >
            Crear reparación
          </button>

          <button
            v-else
            class="primary-button"
            type="button"
            :disabled="processing"
            @click="
              goToRepair(activeRepair)
            "
          >
            Abrir reparación activa
          </button>
        </div>

        <div
          v-if="loadingRelations"
          class="tab-loading"
        >
          Cargando reparaciones...
        </div>

        <div
          v-else-if="!repairs.length"
          class="empty-state"
        >
          No existen reparaciones registradas.
        </div>

        <div
          v-else
          class="table-container"
        >
          <table>
            <thead>
              <tr>
                <th>Código</th>
                <th>Fecha</th>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Prioridad</th>
                <th>Técnico</th>
                <th>Problema reportado</th>
                <th>Activa</th>
                <th></th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="repair in repairs"
                :key="repair.id"
                class="repair-history-row"
                :class="{
                  archived:
                    repair.is_archived,
                }"
                @click="goToRepair(repair)"
              >
                <td>
                  <strong
                    class="repair-code-link"
                  >
                    {{ repair.code }}
                  </strong>
                </td>

                <td>
                  {{
                    formatDateTime(
                      repair.requested_at
                    )
                  }}
                </td>

                <td>
                  {{
                    repair.repair_type_name ||
                    getRepairTypeName(
                      repair.repair_type
                    )
                  }}
                </td>

                <td>
                  <span
                    class="repair-status-badge"
                    :class="
                      getRepairStatusClass(
                        repair.status
                      )
                    "
                  >
                    {{
                      repair.status_name ||
                      getRepairStatusName(
                        repair.status
                      )
                    }}
                  </span>
                </td>

                <td>
                  <span
                    class="repair-priority-badge"
                    :class="
                      getRepairPriorityClass(
                        repair.priority
                      )
                    "
                  >
                    {{
                      repair.priority_name ||
                      getRepairPriorityName(
                        repair.priority
                      )
                    }}
                  </span>
                </td>

                <td>
                  {{
                    repair.assigned_technician_name ||
                    "Sin técnico"
                  }}
                </td>

                <td>
                  <span
                    class="repair-problem-text"
                  >
                    {{
                      repair.reported_problem ||
                      "Sin problema reportado"
                    }}
                  </span>
                </td>

                <td>
                  {{
                    repair.is_active &&
                    !repair.is_archived
                      ? "Sí"
                      : "No"
                  }}
                </td>

                <td>
                  <button
                    class="table-action-button"
                    type="button"
                    @click.stop="
                      goToRepair(repair)
                    "
                  >
                    Abrir
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section
        v-if="activeTab === 'meters'"
        class="tab-card"
      >
        <div class="meter-summary">
          <article>
            <small>Total actual</small>

            <strong>
              {{
                formatMeter(
                  equipment.current_total_meter
                )
              }}
            </strong>
          </article>

          <article>
            <small>B/N actual</small>

            <strong>
              {{
                formatMeter(
                  equipment.current_black_meter
                )
              }}
            </strong>
          </article>

          <article>
            <small>Color actual</small>

            <strong>
              {{
                formatMeter(
                  equipment.current_color_meter
                )
              }}
            </strong>
          </article>

          <article>
            <small>Escaneo actual</small>

            <strong>
              {{
                formatMeter(
                  equipment.current_scan_meter
                )
              }}
            </strong>
          </article>
        </div>

        <div
          v-if="loadingRelations"
          class="tab-loading"
        >
          Cargando lecturas...
        </div>

        <div
          v-else-if="
            !meterReadings.length
          "
          class="empty-state"
        >
          No existen lecturas registradas.
        </div>

        <div
          v-else
          class="table-container"
        >
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Tipo</th>
                <th>Fuente</th>
                <th>Total</th>
                <th>B/N</th>
                <th>Color</th>
                <th>Escaneo</th>
                <th>Verificada</th>
                <th>Aplicada</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="
                  reading in meterReadings
                "
                :key="reading.id"
              >
                <td>
                  {{
                    formatDateTime(
                      reading.reading_date
                    )
                  }}
                </td>

                <td>
                  {{
                    reading.reading_type_name ||
                    getReadingTypeName(
                      reading.reading_type
                    )
                  }}
                </td>

                <td>
                  {{
                    reading.source_name ||
                    reading.source ||
                    "Sin fuente"
                  }}
                </td>

                <td>
                  {{
                    formatMeter(
                      reading.total_meter
                    )
                  }}
                </td>

                <td>
                  {{
                    formatMeter(
                      reading.black_meter
                    )
                  }}
                </td>

                <td>
                  {{
                    formatMeter(
                      reading.color_meter
                    )
                  }}
                </td>

                <td>
                  {{
                    formatMeter(
                      reading.scan_meter
                    )
                  }}
                </td>

                <td>
                  {{
                    reading.is_verified
                      ? "Sí"
                      : "No"
                  }}
                </td>

                <td>
                  {{
                    reading.is_applied_to_equipment
                      ? "Sí"
                      : "No"
                  }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section
        v-if="activeTab === 'movements'"
        class="tab-card"
      >
        <div
          v-if="loadingRelations"
          class="tab-loading"
        >
          Cargando movimientos...
        </div>

        <div
          v-else-if="!movements.length"
          class="empty-state"
        >
          No existen movimientos registrados.
        </div>

        <div
          v-else
          class="timeline"
        >
          <article
            v-for="
              movement in movements
            "
            :key="movement.id"
            class="timeline-item"
          >
            <span
              class="timeline-dot"
            ></span>

            <div>
              <header>
                <strong>
                  {{
                    movement.movement_type_name ||
                    getMovementTypeName(
                      movement.movement_type
                    )
                  }}
                </strong>

                <time>
                  {{
                    formatDateTime(
                      movement.occurred_at
                    )
                  }}
                </time>
              </header>

              <p v-if="movement.reason">
                {{ movement.reason }}
              </p>

              <small>
                {{
                  movement.reference_number ||
                  movement.document_number ||
                  movement.reference_type_name ||
                  movement.reference_type ||
                  "Sin referencia"
                }}
              </small>
            </div>
          </article>
        </div>
      </section>

      <section
        v-if="activeTab === 'documents'"
        class="tab-card"
      >
        <div
          v-if="loadingRelations"
          class="tab-loading"
        >
          Cargando documentos...
        </div>

        <div
          v-else-if="!documents.length"
          class="empty-state"
        >
          No existen documentos registrados.
        </div>

        <div
          v-else
          class="documents-grid"
        >
          <article
            v-for="
              document in documents
            "
            :key="document.id"
            class="document-card"
          >
            <div
              class="document-icon"
            >
              ▤
            </div>

            <div
              class="document-information"
            >
              <strong>
                {{
                  document.title ||
                  "Documento"
                }}
              </strong>

              <span>
                {{
                  document.document_type_name ||
                  getDocumentTypeName(
                    document.document_type
                  )
                }}
              </span>

              <small>
                {{
                  document.document_number ||
                  document.original_filename ||
                  "Sin número"
                }}
              </small>
            </div>

            <div
              class="document-actions"
            >
              <span
                v-if="
                  document.is_verified
                "
                class="verified-badge"
              >
                Verificado
              </span>

              <button
                type="button"
                @click="
                  openDocument(document)
                "
              >
                Abrir
              </button>
            </div>
          </article>
        </div>
      </section>
    </template>

    <Teleport to="body">
      <Transition name="modal-fade">
        <div
          v-if="statusModalOpen"
          class="status-modal-backdrop"
          @click.self="
            closeStatusModal
          "
        >
          <section
            class="status-modal"
            role="dialog"
            aria-modal="true"
            :aria-label="
              statusModalTitle
            "
          >
            <header
              class="status-modal-header"
            >
              <div>
                <span
                  class="status-modal-kicker"
                >
                  Actualización del equipo
                </span>

                <h3>
                  {{ statusModalTitle }}
                </h3>

                <p>
                  {{ equipmentName }}
                  · Serie
                  {{
                    equipment
                      ?.serial_number
                  }}
                </p>
              </div>

              <button
                class="modal-close-button"
                type="button"
                :disabled="processing"
                aria-label="Cerrar"
                @click="
                  closeStatusModal
                "
              >
                ×
              </button>
            </header>

            <form
              class="status-modal-body"
              @submit.prevent="
                submitStatusChange
              "
            >
              <div
                v-if="modalError"
                class="modal-error"
              >
                {{ modalError }}
              </div>

              <label
                class="modal-field"
              >
                <span>
                  Nuevo estado
                </span>

                <select
                  v-model="
                    selectedStatus
                  "
                  required
                >
                  <option value="">
                    Selecciona un estado
                  </option>

                  <option
                    v-for="
                      option in statusOptions
                    "
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </label>

              <label
                class="modal-field"
              >
                <span>
                  Motivo del cambio
                </span>

                <textarea
                  v-model="
                    statusReason
                  "
                  rows="4"
                  maxlength="500"
                  placeholder="Describe brevemente por qué se cambia el estado"
                  required
                ></textarea>

                <small>
                  {{
                    statusReason.length
                  }}/500
                </small>
              </label>

              <footer
                class="status-modal-actions"
              >
                <button
                  class="modal-secondary-button"
                  type="button"
                  :disabled="processing"
                  @click="
                    closeStatusModal
                  "
                >
                  Cancelar
                </button>

                <button
                  class="modal-primary-button"
                  type="submit"
                  :disabled="processing"
                >
                  <span
                    v-if="processing"
                    class="button-spinner"
                  ></span>

                  {{
                    processing
                      ? "Guardando..."
                      : "Guardar cambio"
                  }}
                </button>
              </footer>
            </form>
          </section>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>

<style
  scoped
  src="./styles/equipment-detail.css"
></style>