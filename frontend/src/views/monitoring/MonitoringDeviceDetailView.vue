<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue"

import {
  useRoute,
  useRouter,
} from "vue-router"

import MonitoringStatusBadge from "../../components/monitoring/MonitoringStatusBadge.vue"
import MonitoringTabs from "../../components/monitoring/MonitoringTabs.vue"

import {
  acknowledgeAlert,
  archiveDevice,
  createManualSnapshot,
  deleteDevice,
  getDeviceDetailData,
  resolveAlert,
  restoreDevice,
  updateDevice,
} from "../../services/monitoring.service"

import "./MonitoringDeviceDetailView.css"


const route = useRoute()
const router = useRouter()


const loading = ref(true)
const saving = ref(false)
const deleting = ref(false)

const error = ref("")
const successMessage = ref("")

const device = ref(null)
const snapshots = ref([])
const counters = ref([])
const consumables = ref([])
const components = ref([])
const trays = ref([])
const accessories = ref([])
const alerts = ref([])

const activeSection = ref("summary")

const showDeviceModal = ref(false)
const showManualModal = ref(false)
const showArchiveModal = ref(false)
const showDeleteModal = ref(false)
const showAlertModal = ref(false)

const selectedAlert = ref(null)
const alertAction = ref("")
const alertNotes = ref("")

const archiveReason = ref("")
const deleteConfirmation = ref("")


const sections = [
  {
    id: "summary",
    label: "Resumen",
    icon: "▦",
  },
  {
    id: "consumables",
    label: "Consumibles",
    icon: "◉",
  },
  {
    id: "counters",
    label: "Contadores",
    icon: "▤",
  },
  {
    id: "alerts",
    label: "Alertas",
    icon: "⚠",
  },
  {
    id: "trays",
    label: "Bandejas",
    icon: "▱",
  },
  {
    id: "components",
    label: "Componentes",
    icon: "⚙",
  },
  {
    id: "accessories",
    label: "Accesorios",
    icon: "⊞",
  },
  {
    id: "snapshots",
    label: "Capturas",
    icon: "◫",
  },
  {
    id: "settings",
    label: "Configuración",
    icon: "☷",
  },
]


const deviceForm = reactive({
  customer: "",
  branch: "",
  agent: "",
  network: "",
  snmp_credential: "",
  equipment: "",
  suggested_equipment: "",
  detected_brand: "",
  detected_model: "",

  status: "discovered",
  operational_status: "unknown",
  identification_status: "unknown",
  link_status: "unlinked",

  ip_address: "",
  snmp_port: 161,
  snmp_version: "",

  mac_address: "",
  hostname: "",
  dns_name: "",
  sys_name: "",
  sys_description: "",
  sys_object_id: "",
  sys_location: "",
  sys_contact: "",

  raw_brand_name: "",
  raw_model_name: "",
  raw_serial_number: "",
  product_code: "",
  asset_number: "",

  firmware_version: "",
  controller_firmware_version: "",
  engine_firmware_version: "",
  scanner_firmware_version: "",

  site_location: "",

  is_color: null,
  is_multifunction: null,

  supports_printing: null,
  supports_copying: null,
  supports_scanning: null,
  supports_fax: null,
  supports_duplex: null,

  supports_job_monitoring: false,
  supports_component_monitoring: false,
  supports_accessory_inventory: false,

  monitoring_enabled: true,
  inventory_enabled: true,
  alert_monitoring_enabled: true,
  job_monitoring_enabled: false,

  is_confirmed_printer: false,
  is_ignored: false,

  notes: "",
})


const manualForm = reactive({
  captured_at: "",
  connection_status: "online",
  operational_status: "ready",

  total_meter: null,
  black_meter: null,
  color_meter: null,
  scan_meter: null,

  notes: "",

  counters: [],
  consumables: [],
  components: [],
  trays: [],
  accessories: [],
  alerts: [],
})


const statusOptions = [
  {
    value: "discovered",
    label: "Descubierto",
  },
  {
    value: "identifying",
    label: "Identificando",
  },
  {
    value: "active",
    label: "Activo",
  },
  {
    value: "offline",
    label: "Sin conexión",
  },
  {
    value: "warning",
    label: "Con advertencias",
  },
  {
    value: "error",
    label: "Con error",
  },
  {
    value: "blocked",
    label: "Bloqueado",
  },
  {
    value: "ignored",
    label: "Ignorado",
  },
  {
    value: "replaced",
    label: "Reemplazado",
  },
]


const operationalStatusOptions = [
  {
    value: "unknown",
    label: "Desconocido",
  },
  {
    value: "ready",
    label: "Listo",
  },
  {
    value: "printing",
    label: "Imprimiendo",
  },
  {
    value: "copying",
    label: "Copiando",
  },
  {
    value: "scanning",
    label: "Escaneando",
  },
  {
    value: "faxing",
    label: "Fax",
  },
  {
    value: "warming_up",
    label: "Calentando",
  },
  {
    value: "energy_saving",
    label: "Ahorro de energía",
  },
  {
    value: "maintenance",
    label: "En mantenimiento",
  },
  {
    value: "warning",
    label: "Con advertencia",
  },
  {
    value: "error",
    label: "Con error",
  },
  {
    value: "blocked",
    label: "Bloqueado",
  },
  {
    value: "offline",
    label: "Sin conexión",
  },
]


const connectionStatusOptions = [
  {
    value: "online",
    label: "En línea",
  },
  {
    value: "offline",
    label: "Sin conexión",
  },
  {
    value: "timeout",
    label: "Tiempo agotado",
  },
  {
    value: "authentication_error",
    label: "Error de autenticación",
  },
  {
    value: "network_error",
    label: "Error de red",
  },
  {
    value: "snmp_error",
    label: "Error SNMP",
  },
  {
    value: "unknown",
    label: "Desconocido",
  },
]


const consumableTypeOptions = [
  {
    value: "toner",
    label: "Tóner",
  },
  {
    value: "ink",
    label: "Tinta",
  },
  {
    value: "waste_toner",
    label: "Depósito de residuos",
  },
  {
    value: "staple",
    label: "Grapas",
  },
  {
    value: "oil",
    label: "Aceite",
  },
  {
    value: "cleaning_web",
    label: "Web de limpieza",
  },
  {
    value: "maintenance_kit",
    label: "Kit de mantenimiento",
  },
  {
    value: "other",
    label: "Otro",
  },
]


const colorOptions = [
  {
    value: "black",
    label: "Negro",
  },
  {
    value: "cyan",
    label: "Cian",
  },
  {
    value: "magenta",
    label: "Magenta",
  },
  {
    value: "yellow",
    label: "Amarillo",
  },
  {
    value: "light_cyan",
    label: "Cian claro",
  },
  {
    value: "light_magenta",
    label: "Magenta claro",
  },
  {
    value: "gray",
    label: "Gris",
  },
  {
    value: "white",
    label: "Blanco",
  },
  {
    value: "clear",
    label: "Transparente",
  },
  {
    value: "multicolor",
    label: "Multicolor",
  },
  {
    value: "not_applicable",
    label: "No aplica",
  },
]


const componentCategoryOptions = [
  {
    value: "imaging_unit",
    label: "Unidad de imagen",
  },
  {
    value: "drum",
    label: "Tambor",
  },
  {
    value: "developer",
    label: "Revelador",
  },
  {
    value: "fuser",
    label: "Unidad fusora",
  },
  {
    value: "transfer",
    label: "Transferencia",
  },
  {
    value: "cleaning",
    label: "Limpieza",
  },
  {
    value: "feed",
    label: "Alimentación",
  },
  {
    value: "adf",
    label: "ADF",
  },
  {
    value: "scanner",
    label: "Escáner",
  },
  {
    value: "laser",
    label: "Láser",
  },
  {
    value: "maintenance_kit",
    label: "Kit de mantenimiento",
  },
  {
    value: "other",
    label: "Otro",
  },
]


const trayTypeOptions = [
  {
    value: "cassette",
    label: "Casetera",
  },
  {
    value: "bypass",
    label: "Bandeja bypass",
  },
  {
    value: "large_capacity",
    label: "Gran capacidad",
  },
  {
    value: "manual",
    label: "Alimentación manual",
  },
  {
    value: "envelope",
    label: "Sobres",
  },
  {
    value: "roll",
    label: "Rollo",
  },
  {
    value: "external",
    label: "Bandeja externa",
  },
  {
    value: "other",
    label: "Otra",
  },
]


const accessoryTypeOptions = [
  {
    value: "adf",
    label: "ADF",
  },
  {
    value: "radf",
    label: "RADF",
  },
  {
    value: "duplex",
    label: "Unidad dúplex",
  },
  {
    value: "finisher",
    label: "Finalizador",
  },
  {
    value: "stapler",
    label: "Engrapador",
  },
  {
    value: "punch",
    label: "Perforador",
  },
  {
    value: "booklet",
    label: "Booklet",
  },
  {
    value: "extra_tray",
    label: "Bandeja adicional",
  },
  {
    value: "large_capacity_tray",
    label: "Gran capacidad",
  },
  {
    value: "fax",
    label: "Fax",
  },
  {
    value: "hard_disk",
    label: "Disco duro",
  },
  {
    value: "memory",
    label: "Memoria",
  },
  {
    value: "wifi",
    label: "Wi-Fi",
  },
  {
    value: "card_reader",
    label: "Lector de tarjetas",
  },
  {
    value: "fiery",
    label: "Fiery",
  },
  {
    value: "postscript",
    label: "PostScript",
  },
  {
    value: "other",
    label: "Otro",
  },
]


const alertCategoryOptions = [
  {
    value: "paper",
    label: "Papel",
  },
  {
    value: "jam",
    label: "Atasco",
  },
  {
    value: "toner",
    label: "Tóner",
  },
  {
    value: "consumable",
    label: "Consumible",
  },
  {
    value: "component",
    label: "Componente",
  },
  {
    value: "tray",
    label: "Bandeja",
  },
  {
    value: "door",
    label: "Puerta o cubierta",
  },
  {
    value: "finisher",
    label: "Finalizador",
  },
  {
    value: "scanner",
    label: "Escáner",
  },
  {
    value: "printer",
    label: "Impresión",
  },
  {
    value: "network",
    label: "Red",
  },
  {
    value: "maintenance",
    label: "Mantenimiento",
  },
  {
    value: "service",
    label: "Servicio técnico",
  },
  {
    value: "system",
    label: "Sistema",
  },
  {
    value: "other",
    label: "Otra",
  },
]


const alertSeverityOptions = [
  {
    value: "info",
    label: "Informativa",
  },
  {
    value: "warning",
    label: "Advertencia",
  },
  {
    value: "error",
    label: "Error",
  },
  {
    value: "critical",
    label: "Crítica",
  },
]


const deviceTitle = computed(() => {
  const brand =
    device.value?.raw_brand_name ||
    ""

  const model =
    device.value?.raw_model_name ||
    ""

  const title = `${brand} ${model}`.trim()

  return (
    title ||
    device.value?.hostname ||
    device.value?.ip_address ||
    "Dispositivo"
  )
})


const activeAlerts = computed(() => {
  return alerts.value.filter(
    (alert) => alert.is_active
  )
})


const criticalAlerts = computed(() => {
  return activeAlerts.value.filter(
    (alert) =>
      alert.severity === "critical"
  )
})


const sortedCounters = computed(() => {
  return [...counters.value].sort(
    (first, second) => {
      const firstDate =
        new Date(
          first.captured_at || 0
        ).getTime()

      const secondDate =
        new Date(
          second.captured_at || 0
        ).getTime()

      return secondDate - firstDate
    }
  )
})


const latestCounters = computed(() => {
  const seen = new Set()
  const result = []

  for (
    const reading
    of sortedCounters.value
  ) {
    const key =
      reading.metric_code ||
      reading.metric_name

    if (seen.has(key)) {
      continue
    }

    seen.add(key)
    result.push(reading)
  }

  return result
})


function clearMessages() {
  error.value = ""
  successMessage.value = ""
}


function setSuccess(message) {
  error.value = ""
  successMessage.value = message

  window.setTimeout(
    () => {
      if (
        successMessage.value === message
      ) {
        successMessage.value = ""
      }
    },
    5000
  )
}


function formatDate(value) {
  if (!value) {
    return "—"
  }

  const date = new Date(value)

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return String(value)
  }

  return new Intl.DateTimeFormat(
    "es-PE",
    {
      dateStyle: "short",
      timeStyle: "short",
    }
  ).format(date)
}


function formatNumber(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—"
  }

  const number = Number(value)

  if (
    Number.isNaN(number)
  ) {
    return String(value)
  }

  return new Intl.NumberFormat(
    "es-PE",
    {
      maximumFractionDigits: 2,
    }
  ).format(number)
}


function normalizePercentage(value) {
  const number = Number(value)

  if (
    Number.isNaN(number)
  ) {
    return 0
  }

  return Math.max(
    0,
    Math.min(
      number,
      100
    )
  )
}


function getConsumableColor(
  consumable
) {
  return (
    consumable.color ||
    "not_applicable"
  )
}


function getConsumableStatusLabel(
  consumable
) {
  return (
    consumable.status_display ||
    consumable.status ||
    "Desconocido"
  )
}


function isArchived() {
  return Boolean(
    device.value?.archived_at
  )
}


function fillDeviceForm() {
  if (!device.value) {
    return
  }

  const source = device.value

  for (
    const fieldName
    of Object.keys(deviceForm)
  ) {
    if (
      Object.prototype.hasOwnProperty.call(
        source,
        fieldName
      )
    ) {
      deviceForm[fieldName] =
        source[fieldName]
    }
  }
}


function resetManualForm() {
  manualForm.captured_at = ""
  manualForm.connection_status =
    "online"

  manualForm.operational_status =
    device.value?.operational_status ||
    "ready"

  manualForm.total_meter =
    device.value?.current_total_meter ??
    null

  manualForm.black_meter =
    device.value?.current_black_meter ??
    null

  manualForm.color_meter =
    device.value?.current_color_meter ??
    null

  manualForm.scan_meter =
    device.value?.current_scan_meter ??
    null

  manualForm.notes = ""

  manualForm.counters = []
  manualForm.consumables = []
  manualForm.components = []
  manualForm.trays = []
  manualForm.accessories = []
  manualForm.alerts = []
}


async function loadData() {
  loading.value = true
  clearMessages()

  try {
    const result =
      await getDeviceDetailData(
        route.params.id
      )

    device.value =
      result.device

    snapshots.value =
      result.snapshots

    counters.value =
      result.counters

    consumables.value =
      result.consumables

    components.value =
      result.components

    trays.value =
      result.trays

    accessories.value =
      result.accessories

    alerts.value =
      result.alerts

    fillDeviceForm()
  } catch (exception) {
    error.value =
      exception.message
  } finally {
    loading.value = false
  }
}


function openDeviceModal() {
  fillDeviceForm()
  showDeviceModal.value = true
}


function closeDeviceModal() {
  if (saving.value) {
    return
  }

  showDeviceModal.value = false
}


async function saveDevice() {
  if (!device.value) {
    return
  }

  saving.value = true
  clearMessages()

  try {
    const payload = {
      ...deviceForm,
    }

    device.value =
      await updateDevice(
        device.value.id,
        payload
      )

    showDeviceModal.value = false

    setSuccess(
      "Dispositivo actualizado correctamente."
    )

    await loadData()
  } catch (exception) {
    error.value =
      exception.message
  } finally {
    saving.value = false
  }
}


function openManualModal() {
  resetManualForm()
  showManualModal.value = true
}


function closeManualModal() {
  if (saving.value) {
    return
  }

  showManualModal.value = false
}


function addCounter() {
  manualForm.counters.push({
    metric_code: "",
    metric_name: "",
    category: "unknown",
    function_type: "unknown",
    color_mode: "not_applicable",
    sides_mode: "not_applicable",
    numeric_value: null,
    unit: "count",
    value_source: "manual",
    validation_status: "unknown",
    confidence_percent: 100,
    is_primary: false,
    is_visible_in_reports: true,
    notes: "",
  })
}


function addConsumable() {
  manualForm.consumables.push({
    metric_code: "",
    metric_name: "",
    consumable_type: "toner",
    color: "black",
    status: "unknown",
    value_meaning:
      "percent_remaining",
    current_level: null,
    maximum_capacity: null,
    percentage: null,
    is_present: true,
    replacement_required: false,
    confidence_percent: 100,
    is_visible_in_reports: true,
    notes: "",
  })
}


function addComponent() {
  manualForm.components.push({
    metric_code: "",
    metric_name: "",
    component_category: "unknown",
    color: "not_applicable",
    status: "unknown",
    value_meaning:
      "percent_remaining",
    reported_value: null,
    maximum_value: null,
    percentage: null,
    cycle_count: null,
    expected_life_cycles: null,
    is_present: true,
    replacement_required: false,
    confidence_percent: 100,
    is_visible_in_reports: true,
    notes: "",
  })
}


function addTray() {
  manualForm.trays.push({
    tray_code: "",
    tray_name: "",
    tray_type: "cassette",
    status: "unknown",
    paper_size: "",
    paper_type: "",
    current_level: null,
    maximum_capacity: null,
    percentage: null,
    is_present: true,
    is_open: false,
    is_empty: false,
    is_low: false,
    has_feed_error: false,
    has_wrong_size: false,
    has_wrong_type: false,
    has_jam: false,
    unit: "sheets",
    confidence_percent: 100,
    is_visible_in_reports: true,
    notes: "",
  })
}


function addAccessory() {
  manualForm.accessories.push({
    accessory_code: "",
    accessory_name: "",
    accessory_type: "other",
    status: "unknown",
    quantity: 1,
    is_installed: true,
    is_operational: true,
    is_enabled: true,
    manufacturer_name: "",
    model_name: "",
    product_code: "",
    serial_number: "",
    confidence_percent: 100,
    is_visible_in_reports: true,
    notes: "",
  })
}


function addAlert() {
  manualForm.alerts.push({
    normalized_code: "",
    normalized_message: "",
    category: "other",
    severity: "warning",
    status: "active",
    source_type: "manual",
    component_code: "",
    component_name: "",
    location_code: "",
    location_name: "",
    service_code: "",
    is_active: true,
    blocks_printing: false,
    blocks_copying: false,
    blocks_scanning: false,
    requires_user_action: false,
    requires_technical_visit: false,
    is_visible_in_reports: true,
    notes: "",
  })
}


function removeRow(
  collection,
  index
) {
  collection.splice(
    index,
    1
  )
}


function cleanPayloadValue(value) {
  if (value === "") {
    return null
  }

  return value
}


function cleanRows(rows) {
  return rows.map(
    (row) => {
      const result = {}

      for (
        const [
          key,
          value,
        ]
        of Object.entries(row)
      ) {
        result[key] =
          cleanPayloadValue(value)
      }

      return result
    }
  )
}


async function saveManualSnapshot() {
  if (!device.value) {
    return
  }

  saving.value = true
  clearMessages()

  try {
    const payload = {
      device: device.value.id,

      connection_status:
        manualForm.connection_status,

      operational_status:
        manualForm.operational_status,

      total_meter:
        cleanPayloadValue(
          manualForm.total_meter
        ),

      black_meter:
        cleanPayloadValue(
          manualForm.black_meter
        ),

      color_meter:
        cleanPayloadValue(
          manualForm.color_meter
        ),

      scan_meter:
        cleanPayloadValue(
          manualForm.scan_meter
        ),

      notes:
        manualForm.notes,

      counters:
        cleanRows(
          manualForm.counters
        ),

      consumables:
        cleanRows(
          manualForm.consumables
        ),

      components:
        cleanRows(
          manualForm.components
        ),

      trays:
        cleanRows(
          manualForm.trays
        ),

      accessories:
        cleanRows(
          manualForm.accessories
        ),

      alerts:
        cleanRows(
          manualForm.alerts
        ),
    }

    if (
      manualForm.captured_at
    ) {
      payload.captured_at =
        new Date(
          manualForm.captured_at
        ).toISOString()
    }

    await createManualSnapshot(
      payload
    )

    showManualModal.value = false

    setSuccess(
      "Lectura manual registrada correctamente."
    )

    await loadData()
  } catch (exception) {
    error.value =
      exception.message
  } finally {
    saving.value = false
  }
}


function openArchiveModal() {
  archiveReason.value = ""
  showArchiveModal.value = true
}


async function confirmArchive() {
  if (!device.value) {
    return
  }

  saving.value = true
  clearMessages()

  try {
    await archiveDevice(
      device.value.id,
      archiveReason.value
    )

    showArchiveModal.value = false

    setSuccess(
      "Dispositivo archivado correctamente."
    )

    await loadData()
  } catch (exception) {
    error.value =
      exception.message
  } finally {
    saving.value = false
  }
}


async function confirmRestore() {
  if (!device.value) {
    return
  }

  saving.value = true
  clearMessages()

  try {
    await restoreDevice(
      device.value.id
    )

    setSuccess(
      "Dispositivo restaurado correctamente."
    )

    await loadData()
  } catch (exception) {
    error.value =
      exception.message
  } finally {
    saving.value = false
  }
}


function openDeleteModal() {
  deleteConfirmation.value = ""
  showDeleteModal.value = true
}


async function confirmDelete() {
  if (!device.value) {
    return
  }

  if (
    deleteConfirmation.value
    !== device.value.code
  ) {
    error.value = (
      "Escribe el código exacto del dispositivo."
    )

    return
  }

  deleting.value = true
  clearMessages()

  try {
    await deleteDevice(
      device.value.id
    )

    await router.push(
      "/monitoreo/dispositivos"
    )
  } catch (exception) {
    error.value =
      exception.message
  } finally {
    deleting.value = false
  }
}


function openAlertAction(
  alert,
  actionName
) {
  selectedAlert.value = alert
  alertAction.value = actionName
  alertNotes.value = ""
  showAlertModal.value = true
}


async function confirmAlertAction() {
  if (!selectedAlert.value) {
    return
  }

  saving.value = true
  clearMessages()

  try {
    if (
      alertAction.value
      === "acknowledge"
    ) {
      await acknowledgeAlert(
        selectedAlert.value.id,
        alertNotes.value
      )

      setSuccess(
        "Alerta reconocida correctamente."
      )
    }

    if (
      alertAction.value
      === "resolve"
    ) {
      await resolveAlert(
        selectedAlert.value.id,
        alertNotes.value
      )

      setSuccess(
        "Alerta resuelta correctamente."
      )
    }

    showAlertModal.value = false
    selectedAlert.value = null

    await loadData()
  } catch (exception) {
    error.value =
      exception.message
  } finally {
    saving.value = false
  }
}


watch(
  () => route.params.id,
  () => {
    loadData()
  }
)


onMounted(
  loadData
)
</script>

<template>
  <section class="monitoring-device-page">
    <header class="device-page-header">
      <div class="device-title-area">
        <RouterLink
          class="back-link"
          to="/monitoreo/dispositivos"
        >
          ← Dispositivos
        </RouterLink>

        <div class="device-title-line">
          <div>
            <h1 class="device-page-title">
              {{ deviceTitle }}
            </h1>

            <div class="device-title-meta">
              <span>
                {{ device?.code || route.params.id }}
              </span>

              <span>
                {{ device?.ip_address || "Sin IP" }}
              </span>

              <span>
                {{
                  device?.site_location ||
                  device?.sys_location ||
                  "Sin ubicación"
                }}
              </span>
            </div>
          </div>

          <div class="device-header-status">
            <MonitoringStatusBadge
              v-if="device"
              :status="device.status"
              :label="device.status_display"
            />

            <span
              v-if="isArchived()"
              class="archive-badge"
            >
              Archivado
            </span>
          </div>
        </div>
      </div>

      <div class="device-header-actions">
        <button
          class="monitor-button monitor-button-secondary"
          type="button"
          :disabled="loading"
          @click="loadData"
        >
          Actualizar
        </button>

        <button
          class="monitor-button monitor-button-primary"
          type="button"
          :disabled="loading || isArchived()"
          @click="openManualModal"
        >
          Registrar lectura
        </button>

        <button
          class="monitor-button monitor-button-dark"
          type="button"
          :disabled="loading"
          @click="openDeviceModal"
        >
          Editar
        </button>
      </div>
    </header>

    <MonitoringTabs />

    <div
      v-if="error"
      class="monitor-message monitor-message-error"
    >
      <span>{{ error }}</span>

      <button
        type="button"
        @click="error = ''"
      >
        ×
      </button>
    </div>

    <div
      v-if="successMessage"
      class="monitor-message monitor-message-success"
    >
      <span>{{ successMessage }}</span>

      <button
        type="button"
        @click="successMessage = ''"
      >
        ×
      </button>
    </div>

    <div
      v-if="loading"
      class="device-loading-panel"
    >
      <div class="device-loading-spinner"></div>

      <span>
        Cargando información del dispositivo...
      </span>
    </div>

    <template v-else-if="device">
      <section class="device-kpi-grid">
        <article class="device-kpi-card">
          <span class="device-kpi-label">
            Contador total
          </span>

          <strong class="device-kpi-value">
            {{
              formatNumber(
                device.current_total_meter
              )
            }}
          </strong>

          <small>
            Última lectura registrada
          </small>
        </article>

        <article class="device-kpi-card">
          <span class="device-kpi-label">
            Blanco y negro
          </span>

          <strong class="device-kpi-value">
            {{
              formatNumber(
                device.current_black_meter
              )
            }}
          </strong>

          <small>
            Impresiones y copias B/N
          </small>
        </article>

        <article class="device-kpi-card">
          <span class="device-kpi-label">
            Color
          </span>

          <strong class="device-kpi-value">
            {{
              formatNumber(
                device.current_color_meter
              )
            }}
          </strong>

          <small>
            Impresiones y copias color
          </small>
        </article>

        <article class="device-kpi-card">
          <span class="device-kpi-label">
            Escáner
          </span>

          <strong class="device-kpi-value">
            {{
              formatNumber(
                device.current_scan_meter
              )
            }}
          </strong>

          <small>
            Documentos escaneados
          </small>
        </article>

        <article
          class="device-kpi-card device-kpi-alert"
          :class="{
            critical:
              criticalAlerts.length > 0,
          }"
        >
          <span class="device-kpi-label">
            Alertas activas
          </span>

          <strong class="device-kpi-value">
            {{ activeAlerts.length }}
          </strong>

          <small>
            {{ criticalAlerts.length }}
            críticas
          </small>
        </article>

        <article class="device-kpi-card">
          <span class="device-kpi-label">
            Última conexión
          </span>

          <strong class="device-kpi-date">
            {{
              formatDate(
                device.last_seen_at
              )
            }}
          </strong>

          <small>
            {{
              device.consecutive_failure_count ||
              0
            }}
            errores consecutivos
          </small>
        </article>
      </section>

      <nav class="device-section-tabs">
        <button
          v-for="section in sections"
          :key="section.id"
          type="button"
          class="device-section-tab"
          :class="{
            active:
              activeSection === section.id,
          }"
          @click="activeSection = section.id"
        >
          <span class="device-section-icon">
            {{ section.icon }}
          </span>

          <span>
            {{ section.label }}
          </span>

          <span
            v-if="
              section.id === 'alerts' &&
              activeAlerts.length
            "
            class="device-tab-counter"
          >
            {{ activeAlerts.length }}
          </span>
        </button>
      </nav>

      <section
        v-if="activeSection === 'summary'"
        class="device-content-grid"
      >
        <article class="device-panel">
          <header class="device-panel-header">
            <div>
              <h2>Información principal</h2>

              <p>
                Identificación y conexión del equipo.
              </p>
            </div>
          </header>

          <div class="device-detail-grid">
            <div class="device-detail-item">
              <span>Marca</span>

              <strong>
                {{
                  device.raw_brand_name ||
                  "—"
                }}
              </strong>
            </div>

            <div class="device-detail-item">
              <span>Modelo</span>

              <strong>
                {{
                  device.raw_model_name ||
                  "—"
                }}
              </strong>
            </div>

            <div class="device-detail-item">
              <span>Serie</span>

              <strong>
                {{
                  device.raw_serial_number ||
                  "—"
                }}
              </strong>
            </div>

            <div class="device-detail-item">
              <span>IP</span>

              <strong>
                {{ device.ip_address }}
              </strong>
            </div>

            <div class="device-detail-item">
              <span>MAC</span>

              <strong>
                {{
                  device.mac_address ||
                  "—"
                }}
              </strong>
            </div>

            <div class="device-detail-item">
              <span>Hostname</span>

              <strong>
                {{
                  device.hostname ||
                  "—"
                }}
              </strong>
            </div>

            <div class="device-detail-item">
              <span>Nombre SNMP</span>

              <strong>
                {{
                  device.sys_name ||
                  "—"
                }}
              </strong>
            </div>

            <div class="device-detail-item">
              <span>SNMP</span>

              <strong>
                {{
                  device.snmp_version ||
                  "—"
                }}
                · {{ device.snmp_port }}
              </strong>
            </div>

            <div class="device-detail-item">
              <span>Agente</span>

              <strong>
                {{
                  device.agent_code ||
                  device.agent ||
                  "—"
                }}
              </strong>
            </div>

            <div class="device-detail-item">
              <span>Red</span>

              <strong>
                {{
                  device.network_cidr ||
                  device.network ||
                  "—"
                }}
              </strong>
            </div>

            <div class="device-detail-item">
              <span>Firmware</span>

              <strong>
                {{
                  device.firmware_version ||
                  "—"
                }}
              </strong>
            </div>

            <div class="device-detail-item">
              <span>Ubicación</span>

              <strong>
                {{
                  device.site_location ||
                  device.sys_location ||
                  "—"
                }}
              </strong>
            </div>
          </div>
        </article>

        <article class="device-panel">
          <header class="device-panel-header">
            <div>
              <h2>Capacidades</h2>

              <p>
                Funciones detectadas o configuradas.
              </p>
            </div>
          </header>

          <div class="capability-list">
            <div class="capability-row">
              <span>Equipo color</span>

              <strong>
                {{
                  device.is_color
                    ? "Sí"
                    : "No"
                }}
              </strong>
            </div>

            <div class="capability-row">
              <span>Multifunción</span>

              <strong>
                {{
                  device.is_multifunction
                    ? "Sí"
                    : "No"
                }}
              </strong>
            </div>

            <div class="capability-row">
              <span>Impresión</span>

              <strong>
                {{
                  device.supports_printing
                    ? "Disponible"
                    : "No detectado"
                }}
              </strong>
            </div>

            <div class="capability-row">
              <span>Copia</span>

              <strong>
                {{
                  device.supports_copying
                    ? "Disponible"
                    : "No detectado"
                }}
              </strong>
            </div>

            <div class="capability-row">
              <span>Escaneo</span>

              <strong>
                {{
                  device.supports_scanning
                    ? "Disponible"
                    : "No detectado"
                }}
              </strong>
            </div>

            <div class="capability-row">
              <span>Fax</span>

              <strong>
                {{
                  device.supports_fax
                    ? "Disponible"
                    : "No detectado"
                }}
              </strong>
            </div>

            <div class="capability-row">
              <span>Dúplex</span>

              <strong>
                {{
                  device.supports_duplex
                    ? "Disponible"
                    : "No detectado"
                }}
              </strong>
            </div>
          </div>
        </article>

        <article class="device-panel device-panel-wide">
          <header class="device-panel-header">
            <div>
              <h2>Consumibles actuales</h2>

              <p>
                Última lectura disponible por consumible.
              </p>
            </div>

            <button
              class="text-action"
              type="button"
              @click="activeSection = 'consumables'"
            >
              Ver todos
            </button>
          </header>

          <div
            v-if="consumables.length"
            class="consumable-summary-grid"
          >
            <article
              v-for="consumable in consumables"
              :key="consumable.id"
              class="consumable-summary-card"
              :class="[
                `consumable-${getConsumableColor(
                  consumable
                )}`,
                `status-${consumable.status}`,
              ]"
            >
              <div class="consumable-drop-wrap">
                <div
                  class="consumable-drop"
                  :style="{
                    '--fill-level':
                      `${normalizePercentage(
                        consumable.percentage
                      )}%`,
                  }"
                >
                  <div class="consumable-drop-fill"></div>

                  <span>
                    {{
                      consumable.percentage !== null
                        ? `${formatNumber(
                            consumable.percentage
                          )}%`
                        : "—"
                    }}
                  </span>
                </div>
              </div>

              <div class="consumable-summary-info">
                <strong>
                  {{
                    consumable.metric_name ||
                    consumable.consumable_type_display
                  }}
                </strong>

                <span>
                  {{
                    consumable.color_display ||
                    consumable.color
                  }}
                </span>

                <small>
                  {{
                    getConsumableStatusLabel(
                      consumable
                    )
                  }}
                </small>
              </div>
            </article>
          </div>

          <div
            v-else
            class="empty-state"
          >
            No existen lecturas de consumibles.
          </div>
        </article>

        <article class="device-panel device-panel-wide">
          <header class="device-panel-header">
            <div>
              <h2>Alertas recientes</h2>

              <p>
                Problemas que requieren atención.
              </p>
            </div>

            <button
              class="text-action"
              type="button"
              @click="activeSection = 'alerts'"
            >
              Ver alertas
            </button>
          </header>

          <div
            v-if="activeAlerts.length"
            class="alert-compact-list"
          >
            <article
              v-for="alert in activeAlerts.slice(0, 5)"
              :key="alert.id"
              class="alert-compact-item"
              :class="`severity-${alert.severity}`"
            >
              <div class="alert-compact-icon">
                !
              </div>

              <div class="alert-compact-content">
                <strong>
                  {{ alert.normalized_message }}
                </strong>

                <span>
                  {{
                    alert.location_name ||
                    alert.category_display ||
                    alert.category
                  }}
                </span>
              </div>

              <small>
                {{
                  formatDate(
                    alert.last_detected_at
                  )
                }}
              </small>
            </article>
          </div>

          <div
            v-else
            class="empty-state empty-state-success"
          >
            No existen alertas activas.
          </div>
        </article>
      </section>

      <section
        v-if="activeSection === 'consumables'"
        class="device-panel"
      >
        <header class="device-panel-header">
          <div>
            <h2>Tóneres y consumibles</h2>

            <p>
              Niveles actuales, estado y necesidad de cambio.
            </p>
          </div>

          <button
            class="monitor-button monitor-button-primary"
            type="button"
            @click="openManualModal"
          >
            Agregar lectura
          </button>
        </header>

        <div
          v-if="consumables.length"
          class="consumable-grid"
        >
          <article
            v-for="consumable in consumables"
            :key="consumable.id"
            class="consumable-card"
            :class="[
              `consumable-${getConsumableColor(
                consumable
              )}`,
              `status-${consumable.status}`,
            ]"
          >
            <div class="consumable-card-top">
              <div>
                <span class="consumable-type">
                  {{
                    consumable.consumable_type_display ||
                    consumable.consumable_type
                  }}
                </span>

                <h3>
                  {{ consumable.metric_name }}
                </h3>
              </div>

              <span
                class="consumable-status"
                :class="`status-${consumable.status}`"
              >
                {{
                  getConsumableStatusLabel(
                    consumable
                  )
                }}
              </span>
            </div>

            <div class="consumable-main">
              <div
                class="consumable-drop consumable-drop-large"
                :style="{
                  '--fill-level':
                    `${normalizePercentage(
                      consumable.percentage
                    )}%`,
                }"
              >
                <div class="consumable-drop-fill"></div>

                <span>
                  {{
                    consumable.percentage !== null
                      ? `${formatNumber(
                          consumable.percentage
                        )}%`
                      : "—"
                  }}
                </span>
              </div>

              <div class="consumable-values">
                <div>
                  <span>Nivel actual</span>

                  <strong>
                    {{
                      formatNumber(
                        consumable.current_level
                      )
                    }}
                  </strong>
                </div>

                <div>
                  <span>Capacidad</span>

                  <strong>
                    {{
                      formatNumber(
                        consumable.maximum_capacity
                      )
                    }}
                  </strong>
                </div>

                <div>
                  <span>Anterior</span>

                  <strong>
                    {{
                      consumable.previous_percentage !== null
                        ? `${formatNumber(
                            consumable.previous_percentage
                          )}%`
                        : "—"
                    }}
                  </strong>
                </div>

                <div>
                  <span>Variación</span>

                  <strong>
                    {{
                      consumable.delta_percentage !== null
                        ? `${formatNumber(
                            consumable.delta_percentage
                          )}%`
                        : "—"
                    }}
                  </strong>
                </div>
              </div>
            </div>

            <footer class="consumable-footer">
              <span>
                {{
                  consumable.color_display ||
                  consumable.color
                }}
              </span>

              <span>
                {{
                  consumable.is_present === false
                    ? "No instalado"
                    : "Instalado"
                }}
              </span>

              <span
                v-if="consumable.replacement_required"
                class="replacement-warning"
              >
                Requiere cambio
              </span>
            </footer>
          </article>
        </div>

        <div
          v-else
          class="empty-state"
        >
          No existen lecturas de consumibles.
        </div>
      </section>

      <section
        v-if="activeSection === 'counters'"
        class="device-panel"
      >
        <header class="device-panel-header">
          <div>
            <h2>Lecturas de contador</h2>

            <p>
              Historial completo de métricas y variaciones.
            </p>
          </div>

          <button
            class="monitor-button monitor-button-primary"
            type="button"
            @click="openManualModal"
          >
            Registrar contador
          </button>
        </header>

        <div class="device-table-wrap">
          <table class="device-data-table">
            <thead>
              <tr>
                <th>Métrica</th>
                <th>Categoría</th>
                <th>Valor</th>
                <th>Anterior</th>
                <th>Variación</th>
                <th>Validación</th>
                <th>Capturada</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="reading in sortedCounters"
                :key="reading.id"
              >
                <td>
                  <strong>
                    {{ reading.metric_name }}
                  </strong>

                  <small>
                    {{ reading.metric_code }}
                  </small>
                </td>

                <td>
                  {{
                    reading.category_display ||
                    reading.category
                  }}
                </td>

                <td>
                  {{
                    formatNumber(
                      reading.numeric_value
                    )
                  }}
                </td>

                <td>
                  {{
                    formatNumber(
                      reading.previous_value
                    )
                  }}
                </td>

                <td>
                  <span
                    class="delta-value"
                    :class="{
                      negative:
                        Number(
                          reading.delta_value
                        ) < 0,
                    }"
                  >
                    {{
                      formatNumber(
                        reading.delta_value
                      )
                    }}
                  </span>
                </td>

                <td>
                  <span
                    class="reading-validation"
                    :class="`validation-${reading.validation_status}`"
                  >
                    {{
                      reading.validation_status_display ||
                      reading.validation_status
                    }}
                  </span>
                </td>

                <td>
                  {{
                    formatDate(
                      reading.captured_at
                    )
                  }}
                </td>
              </tr>

              <tr
                v-if="!sortedCounters.length"
              >
                <td
                  colspan="7"
                  class="table-empty-cell"
                >
                  No existen lecturas de contador.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section
        v-if="activeSection === 'alerts'"
        class="device-panel"
      >
        <header class="device-panel-header">
          <div>
            <h2>Alertas del dispositivo</h2>

            <p>
              Reconoce, resuelve y consulta el historial.
            </p>
          </div>

          <button
            class="monitor-button monitor-button-primary"
            type="button"
            @click="openManualModal"
          >
            Crear alerta
          </button>
        </header>

        <div
          v-if="alerts.length"
          class="device-alert-list"
        >
          <article
            v-for="alert in alerts"
            :key="alert.id"
            class="device-alert-card"
            :class="[
              `severity-${alert.severity}`,
              {
                resolved:
                  !alert.is_active,
              },
            ]"
          >
            <div class="device-alert-leading">
              <div class="device-alert-symbol">
                !
              </div>
            </div>

            <div class="device-alert-body">
              <div class="device-alert-heading">
                <div>
                  <span class="device-alert-category">
                    {{
                      alert.category_display ||
                      alert.category
                    }}
                  </span>

                  <h3>
                    {{ alert.normalized_message }}
                  </h3>
                </div>

                <div class="device-alert-badges">
                  <span
                    class="severity-badge"
                    :class="`severity-${alert.severity}`"
                  >
                    {{
                      alert.severity_display ||
                      alert.severity
                    }}
                  </span>

                  <span
                    class="alert-status-badge"
                    :class="{
                      active:
                        alert.is_active,
                    }"
                  >
                    {{
                      alert.status_display ||
                      alert.status
                    }}
                  </span>
                </div>
              </div>

              <p
                v-if="
                  alert.raw_message ||
                  alert.raw_description
                "
                class="device-alert-description"
              >
                {{
                  alert.raw_message ||
                  alert.raw_description
                }}
              </p>

              <div class="device-alert-meta">
                <span>
                  Código:
                  {{
                    alert.normalized_code ||
                    "—"
                  }}
                </span>

                <span>
                  Ubicación:
                  {{
                    alert.location_name ||
                    "—"
                  }}
                </span>

                <span>
                  Detectada:
                  {{
                    formatDate(
                      alert.first_detected_at
                    )
                  }}
                </span>

                <span>
                  Última vez:
                  {{
                    formatDate(
                      alert.last_detected_at
                    )
                  }}
                </span>
              </div>

              <div class="device-alert-flags">
                <span
                  v-if="alert.blocks_printing"
                >
                  Bloquea impresión
                </span>

                <span
                  v-if="alert.blocks_copying"
                >
                  Bloquea copia
                </span>

                <span
                  v-if="alert.blocks_scanning"
                >
                  Bloquea escaneo
                </span>

                <span
                  v-if="alert.requires_user_action"
                >
                  Requiere acción del usuario
                </span>

                <span
                  v-if="alert.requires_technical_visit"
                >
                  Requiere visita técnica
                </span>
              </div>

              <div
                v-if="alert.resolution_notes"
                class="device-alert-resolution"
              >
                <strong>
                  Resolución:
                </strong>

                {{ alert.resolution_notes }}
              </div>

              <div
                v-if="alert.is_active"
                class="device-alert-actions"
              >
                <button
                  v-if="
                    alert.status !==
                    'acknowledged'
                  "
                  class="monitor-button monitor-button-secondary"
                  type="button"
                  @click="
                    openAlertAction(
                      alert,
                      'acknowledge'
                    )
                  "
                >
                  Reconocer
                </button>

                <button
                  class="monitor-button monitor-button-success"
                  type="button"
                  @click="
                    openAlertAction(
                      alert,
                      'resolve'
                    )
                  "
                >
                  Resolver
                </button>
              </div>
            </div>
          </article>
        </div>

        <div
          v-else
          class="empty-state empty-state-success"
        >
          No existen alertas para este dispositivo.
        </div>
      </section>

      <section
        v-if="activeSection === 'trays'"
        class="device-panel"
      >
        <header class="device-panel-header">
          <div>
            <h2>Bandejas de papel</h2>

            <p>
              Capacidad, papel disponible y problemas detectados.
            </p>
          </div>

          <button
            class="monitor-button monitor-button-primary"
            type="button"
            @click="openManualModal"
          >
            Agregar bandeja
          </button>
        </header>

        <div
          v-if="trays.length"
          class="tray-grid"
        >
          <article
            v-for="tray in trays"
            :key="tray.id"
            class="tray-card"
            :class="`tray-status-${tray.status}`"
          >
            <header>
              <div>
                <span>
                  {{
                    tray.tray_type_display ||
                    tray.tray_type
                  }}
                </span>

                <h3>
                  {{ tray.tray_name }}
                </h3>
              </div>

              <span class="tray-status">
                {{
                  tray.status_display ||
                  tray.status
                }}
              </span>
            </header>

            <div class="tray-level">
              <div class="tray-level-top">
                <span>
                  Papel disponible
                </span>

                <strong>
                  {{
                    tray.percentage !== null
                      ? `${formatNumber(
                          tray.percentage
                        )}%`
                      : "—"
                  }}
                </strong>
              </div>

              <div class="tray-progress">
                <div
                  :style="{
                    width:
                      `${normalizePercentage(
                        tray.percentage
                      )}%`,
                  }"
                ></div>
              </div>
            </div>

            <div class="tray-info-grid">
              <div>
                <span>Tamaño</span>

                <strong>
                  {{
                    tray.paper_size ||
                    "—"
                  }}
                </strong>
              </div>

              <div>
                <span>Tipo</span>

                <strong>
                  {{
                    tray.paper_type ||
                    "—"
                  }}
                </strong>
              </div>

              <div>
                <span>Actual</span>

                <strong>
                  {{
                    formatNumber(
                      tray.current_level
                    )
                  }}
                </strong>
              </div>

              <div>
                <span>Capacidad</span>

                <strong>
                  {{
                    formatNumber(
                      tray.maximum_capacity
                    )
                  }}
                </strong>
              </div>
            </div>

            <div class="tray-flags">
              <span
                v-if="tray.is_open"
              >
                Abierta
              </span>

              <span
                v-if="tray.is_empty"
              >
                Vacía
              </span>

              <span
                v-if="tray.is_low"
              >
                Papel bajo
              </span>

              <span
                v-if="tray.has_jam"
              >
                Atascada
              </span>

              <span
                v-if="tray.has_feed_error"
              >
                Error de alimentación
              </span>
            </div>
          </article>
        </div>

        <div
          v-else
          class="empty-state"
        >
          No existen lecturas de bandejas.
        </div>
      </section>

      <section
        v-if="activeSection === 'components'"
        class="device-panel"
      >
        <header class="device-panel-header">
          <div>
            <h2>Componentes y unidades</h2>

            <p>
              Vida útil, ciclos y reemplazos necesarios.
            </p>
          </div>

          <button
            class="monitor-button monitor-button-primary"
            type="button"
            @click="openManualModal"
          >
            Agregar componente
          </button>
        </header>

        <div
          v-if="components.length"
          class="component-grid"
        >
          <article
            v-for="component in components"
            :key="component.id"
            class="component-card"
            :class="`component-status-${component.status}`"
          >
            <header>
              <div>
                <span>
                  {{
                    component.component_category_display ||
                    component.component_category
                  }}
                </span>

                <h3>
                  {{ component.metric_name }}
                </h3>
              </div>

              <span class="component-status">
                {{
                  component.status_display ||
                  component.status
                }}
              </span>
            </header>

            <div class="component-percentage">
              <div class="component-percentage-value">
                {{
                  component.percentage !== null
                    ? `${formatNumber(
                        component.percentage
                      )}%`
                    : "—"
                }}
              </div>

              <div class="component-progress">
                <div
                  :style="{
                    width:
                      `${normalizePercentage(
                        component.percentage
                      )}%`,
                  }"
                ></div>
              </div>
            </div>

            <div class="component-info-grid">
              <div>
                <span>Color</span>

                <strong>
                  {{
                    component.color_display ||
                    component.color
                  }}
                </strong>
              </div>

              <div>
                <span>Ciclos</span>

                <strong>
                  {{
                    formatNumber(
                      component.cycle_count
                    )
                  }}
                </strong>
              </div>

              <div>
                <span>Vida esperada</span>

                <strong>
                  {{
                    formatNumber(
                      component.expected_life_cycles
                    )
                  }}
                </strong>
              </div>

              <div>
                <span>Restantes</span>

                <strong>
                  {{
                    formatNumber(
                      component.remaining_cycles
                    )
                  }}
                </strong>
              </div>
            </div>

            <div
              v-if="component.replacement_required"
              class="component-replacement"
            >
              Requiere reemplazo
            </div>
          </article>
        </div>

        <div
          v-else
          class="empty-state"
        >
          No existen lecturas de componentes.
        </div>
      </section>

      <section
        v-if="activeSection === 'accessories'"
        class="device-panel"
      >
        <header class="device-panel-header">
          <div>
            <h2>Accesorios instalados</h2>

            <p>
              Finalizadores, ADF, dúplex, memoria y otros.
            </p>
          </div>

          <button
            class="monitor-button monitor-button-primary"
            type="button"
            @click="openManualModal"
          >
            Agregar accesorio
          </button>
        </header>

        <div
          v-if="accessories.length"
          class="accessory-grid"
        >
          <article
            v-for="accessory in accessories"
            :key="accessory.id"
            class="accessory-card"
            :class="`accessory-status-${accessory.status}`"
          >
            <div class="accessory-icon">
              ⚙
            </div>

            <div class="accessory-body">
              <span>
                {{
                  accessory.accessory_type_display ||
                  accessory.accessory_type
                }}
              </span>

              <h3>
                {{ accessory.accessory_name }}
              </h3>

              <div class="accessory-meta">
                <span>
                  Estado:
                  {{
                    accessory.status_display ||
                    accessory.status
                  }}
                </span>

                <span>
                  Cantidad:
                  {{ accessory.quantity }}
                </span>

                <span>
                  Modelo:
                  {{
                    accessory.model_name ||
                    "—"
                  }}
                </span>

                <span>
                  Serie:
                  {{
                    accessory.serial_number ||
                    "—"
                  }}
                </span>
              </div>
            </div>

            <div class="accessory-state">
              <span
                :class="{
                  available:
                    accessory.is_installed,
                }"
              >
                {{
                  accessory.is_installed
                    ? "Instalado"
                    : "No instalado"
                }}
              </span>

              <span
                :class="{
                  available:
                    accessory.is_operational,
                }"
              >
                {{
                  accessory.is_operational
                    ? "Operativo"
                    : "Con problema"
                }}
              </span>
            </div>
          </article>
        </div>

        <div
          v-else
          class="empty-state"
        >
          No existen accesorios registrados.
        </div>
      </section>

      <section
        v-if="activeSection === 'snapshots'"
        class="device-panel"
      >
        <header class="device-panel-header">
          <div>
            <h2>Capturas históricas</h2>

            <p>
              Registros automáticos y manuales del dispositivo.
            </p>
          </div>

          <button
            class="monitor-button monitor-button-primary"
            type="button"
            @click="openManualModal"
          >
            Nueva captura manual
          </button>
        </header>

        <div class="device-table-wrap">
          <table class="device-data-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Tipo</th>
                <th>Procesamiento</th>
                <th>Conexión</th>
                <th>Total</th>
                <th>Consumibles</th>
                <th>Alertas</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="snapshot in snapshots"
                :key="snapshot.id"
              >
                <td>
                  {{
                    formatDate(
                      snapshot.captured_at
                    )
                  }}
                </td>

                <td>
                  {{
                    snapshot.snapshot_type_display ||
                    snapshot.snapshot_type
                  }}
                </td>

                <td>
                  {{
                    snapshot.processing_status_display ||
                    snapshot.processing_status
                  }}
                </td>

                <td>
                  {{
                    snapshot.connection_status_display ||
                    snapshot.connection_status
                  }}
                </td>

                <td>
                  {{
                    formatNumber(
                      snapshot.total_meter
                    )
                  }}
                </td>

                <td>
                  {{
                    snapshot.consumable_reading_count ||
                    0
                  }}
                </td>

                <td>
                  {{
                    snapshot.active_alert_count ||
                    0
                  }}
                </td>
              </tr>

              <tr
                v-if="!snapshots.length"
              >
                <td
                  colspan="7"
                  class="table-empty-cell"
                >
                  No existen capturas.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section
        v-if="activeSection === 'settings'"
        class="device-content-grid"
      >
        <article class="device-panel">
          <header class="device-panel-header">
            <div>
              <h2>Configuración de monitoreo</h2>

              <p>
                Funciones activas del dispositivo.
              </p>
            </div>

            <button
              class="monitor-button monitor-button-dark"
              type="button"
              @click="openDeviceModal"
            >
              Modificar
            </button>
          </header>

          <div class="settings-status-list">
            <div>
              <span>Monitoreo general</span>

              <strong
                :class="{
                  enabled:
                    device.monitoring_enabled,
                }"
              >
                {{
                  device.monitoring_enabled
                    ? "Habilitado"
                    : "Deshabilitado"
                }}
              </strong>
            </div>

            <div>
              <span>Inventario</span>

              <strong
                :class="{
                  enabled:
                    device.inventory_enabled,
                }"
              >
                {{
                  device.inventory_enabled
                    ? "Habilitado"
                    : "Deshabilitado"
                }}
              </strong>
            </div>

            <div>
              <span>Alertas</span>

              <strong
                :class="{
                  enabled:
                    device.alert_monitoring_enabled,
                }"
              >
                {{
                  device.alert_monitoring_enabled
                    ? "Habilitado"
                    : "Deshabilitado"
                }}
              </strong>
            </div>

            <div>
              <span>Trabajos</span>

              <strong
                :class="{
                  enabled:
                    device.job_monitoring_enabled,
                }"
              >
                {{
                  device.job_monitoring_enabled
                    ? "Habilitado"
                    : "Deshabilitado"
                }}
              </strong>
            </div>
          </div>
        </article>

        <article class="device-panel">
          <header class="device-panel-header">
            <div>
              <h2>Estado de vinculación</h2>

              <p>
                Relación con el inventario de Copier OS.
              </p>
            </div>
          </header>

          <div class="device-detail-grid">
            <div class="device-detail-item">
              <span>Identificación</span>

              <strong>
                {{
                  device.identification_status_display ||
                  device.identification_status
                }}
              </strong>
            </div>

            <div class="device-detail-item">
              <span>Vinculación</span>

              <strong>
                {{
                  device.link_status_display ||
                  device.link_status
                }}
              </strong>
            </div>

            <div class="device-detail-item">
              <span>Equipo vinculado</span>

              <strong>
                {{
                  device.equipment ||
                  "Sin vincular"
                }}
              </strong>
            </div>

            <div class="device-detail-item">
              <span>Equipo sugerido</span>

              <strong>
                {{
                  device.suggested_equipment ||
                  "—"
                }}
              </strong>
            </div>
          </div>
        </article>

        <article class="device-panel device-panel-wide danger-zone">
          <header class="device-panel-header">
            <div>
              <h2>Zona de control</h2>

              <p>
                Archivado, restauración y eliminación definitiva.
              </p>
            </div>
          </header>

          <div class="danger-actions">
            <button
              v-if="!isArchived()"
              class="monitor-button monitor-button-warning"
              type="button"
              @click="openArchiveModal"
            >
              Archivar dispositivo
            </button>

            <button
              v-else
              class="monitor-button monitor-button-success"
              type="button"
              @click="confirmRestore"
            >
              Restaurar dispositivo
            </button>

            <button
              class="monitor-button monitor-button-danger"
              type="button"
              @click="openDeleteModal"
            >
              Eliminar definitivamente
            </button>
          </div>

          <p class="danger-note">
            La eliminación puede ser rechazada cuando el dispositivo
            tenga capturas, lecturas o alertas protegidas.
          </p>
        </article>
      </section>
    </template>

    <div
      v-if="showDeviceModal"
      class="monitor-modal-backdrop"
      @click.self="closeDeviceModal"
    >
      <section class="monitor-modal monitor-modal-large">
        <header class="monitor-modal-header">
          <div>
            <h2>Editar dispositivo</h2>

            <p>
              Modifica identificación, conexión y monitoreo.
            </p>
          </div>

          <button
            type="button"
            class="modal-close"
            @click="closeDeviceModal"
          >
            ×
          </button>
        </header>

        <form
          class="monitor-modal-body"
          @submit.prevent="saveDevice"
        >
          <div class="form-section">
            <h3>Identificación</h3>

            <div class="monitor-form-grid">
              <label>
                <span>Marca reportada</span>

                <input
                  v-model.trim="deviceForm.raw_brand_name"
                  type="text"
                />
              </label>

              <label>
                <span>Modelo reportado</span>

                <input
                  v-model.trim="deviceForm.raw_model_name"
                  type="text"
                />
              </label>

              <label>
                <span>Serie reportada</span>

                <input
                  v-model.trim="deviceForm.raw_serial_number"
                  type="text"
                />
              </label>

              <label>
                <span>Código de producto</span>

                <input
                  v-model.trim="deviceForm.product_code"
                  type="text"
                />
              </label>

              <label>
                <span>Código patrimonial</span>

                <input
                  v-model.trim="deviceForm.asset_number"
                  type="text"
                />
              </label>

              <label>
                <span>Ubicación</span>

                <input
                  v-model.trim="deviceForm.site_location"
                  type="text"
                />
              </label>
            </div>
          </div>

          <div class="form-section">
            <h3>Conexión</h3>

            <div class="monitor-form-grid">
              <label>
                <span>Dirección IP</span>

                <input
                  v-model.trim="deviceForm.ip_address"
                  type="text"
                  required
                />
              </label>

              <label>
                <span>Puerto SNMP</span>

                <input
                  v-model.number="deviceForm.snmp_port"
                  type="number"
                  min="1"
                  max="65535"
                  required
                />
              </label>

              <label>
                <span>Versión SNMP</span>

                <input
                  v-model.trim="deviceForm.snmp_version"
                  type="text"
                />
              </label>

              <label>
                <span>MAC</span>

                <input
                  v-model.trim="deviceForm.mac_address"
                  type="text"
                />
              </label>

              <label>
                <span>Hostname</span>

                <input
                  v-model.trim="deviceForm.hostname"
                  type="text"
                />
              </label>

              <label>
                <span>Nombre DNS</span>

                <input
                  v-model.trim="deviceForm.dns_name"
                  type="text"
                />
              </label>

              <label>
                <span>Nombre SNMP</span>

                <input
                  v-model.trim="deviceForm.sys_name"
                  type="text"
                />
              </label>

              <label>
                <span>Ubicación SNMP</span>

                <input
                  v-model.trim="deviceForm.sys_location"
                  type="text"
                />
              </label>
            </div>
          </div>

          <div class="form-section">
            <h3>Estado</h3>

            <div class="monitor-form-grid">
              <label>
                <span>Estado de monitoreo</span>

                <select
                  v-model="deviceForm.status"
                >
                  <option
                    v-for="option in statusOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </label>

              <label>
                <span>Estado operativo</span>

                <select
                  v-model="deviceForm.operational_status"
                >
                  <option
                    v-for="option in operationalStatusOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </label>
            </div>
          </div>

          <div class="form-section">
            <h3>Capacidades</h3>

            <div class="monitor-check-grid">
              <label>
                <input
                  v-model="deviceForm.is_color"
                  type="checkbox"
                />

                <span>Equipo color</span>
              </label>

              <label>
                <input
                  v-model="deviceForm.is_multifunction"
                  type="checkbox"
                />

                <span>Multifunción</span>
              </label>

              <label>
                <input
                  v-model="deviceForm.supports_printing"
                  type="checkbox"
                />

                <span>Impresión</span>
              </label>

              <label>
                <input
                  v-model="deviceForm.supports_copying"
                  type="checkbox"
                />

                <span>Copia</span>
              </label>

              <label>
                <input
                  v-model="deviceForm.supports_scanning"
                  type="checkbox"
                />

                <span>Escaneo</span>
              </label>

              <label>
                <input
                  v-model="deviceForm.supports_fax"
                  type="checkbox"
                />

                <span>Fax</span>
              </label>

              <label>
                <input
                  v-model="deviceForm.supports_duplex"
                  type="checkbox"
                />

                <span>Dúplex</span>
              </label>
            </div>
          </div>

          <div class="form-section">
            <h3>Monitoreo</h3>

            <div class="monitor-check-grid">
              <label>
                <input
                  v-model="deviceForm.monitoring_enabled"
                  type="checkbox"
                />

                <span>Monitoreo habilitado</span>
              </label>

              <label>
                <input
                  v-model="deviceForm.inventory_enabled"
                  type="checkbox"
                />

                <span>Inventario habilitado</span>
              </label>

              <label>
                <input
                  v-model="deviceForm.alert_monitoring_enabled"
                  type="checkbox"
                />

                <span>Alertas habilitadas</span>
              </label>

              <label>
                <input
                  v-model="deviceForm.job_monitoring_enabled"
                  type="checkbox"
                />

                <span>Trabajos habilitados</span>
              </label>

              <label>
                <input
                  v-model="deviceForm.supports_component_monitoring"
                  type="checkbox"
                />

                <span>Monitorear componentes</span>
              </label>

              <label>
                <input
                  v-model="deviceForm.supports_accessory_inventory"
                  type="checkbox"
                />

                <span>Inventario de accesorios</span>
              </label>

              <label>
                <input
                  v-model="deviceForm.is_confirmed_printer"
                  type="checkbox"
                />

                <span>Confirmado como impresora</span>
              </label>

              <label>
                <input
                  v-model="deviceForm.is_ignored"
                  type="checkbox"
                />

                <span>Ignorar dispositivo</span>
              </label>
            </div>
          </div>

          <div class="form-section">
            <label class="form-field-full">
              <span>Observaciones</span>

              <textarea
                v-model.trim="deviceForm.notes"
                rows="4"
              ></textarea>
            </label>
          </div>

          <footer class="monitor-modal-footer">
            <button
              class="monitor-button monitor-button-secondary"
              type="button"
              :disabled="saving"
              @click="closeDeviceModal"
            >
              Cancelar
            </button>

            <button
              class="monitor-button monitor-button-primary"
              type="submit"
              :disabled="saving"
            >
              {{
                saving
                  ? "Guardando..."
                  : "Guardar cambios"
              }}
            </button>
          </footer>
        </form>
      </section>
    </div>

    <div
      v-if="showManualModal"
      class="monitor-modal-backdrop"
      @click.self="closeManualModal"
    >
      <section class="monitor-modal monitor-modal-extra-large">
        <header class="monitor-modal-header">
          <div>
            <h2>Registrar lectura manual</h2>

            <p>
              Agrega contadores, consumibles, componentes,
              bandejas, accesorios y alertas.
            </p>
          </div>

          <button
            type="button"
            class="modal-close"
            @click="closeManualModal"
          >
            ×
          </button>
        </header>

        <form
          class="monitor-modal-body"
          @submit.prevent="saveManualSnapshot"
        >
          <div class="form-section">
            <h3>Datos de la captura</h3>

            <div class="monitor-form-grid">
              <label>
                <span>Fecha y hora</span>

                <input
                  v-model="manualForm.captured_at"
                  type="datetime-local"
                />
              </label>

              <label>
                <span>Estado de conexión</span>

                <select
                  v-model="manualForm.connection_status"
                >
                  <option
                    v-for="option in connectionStatusOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </label>

              <label>
                <span>Estado operativo</span>

                <select
                  v-model="manualForm.operational_status"
                >
                  <option
                    v-for="option in operationalStatusOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </label>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section-heading">
              <div>
                <h3>Contadores principales</h3>

                <p>
                  Actualizan los contadores actuales del dispositivo.
                </p>
              </div>
            </div>

            <div class="monitor-form-grid">
              <label>
                <span>Contador total</span>

                <input
                  v-model.number="manualForm.total_meter"
                  type="number"
                  min="0"
                />
              </label>

              <label>
                <span>Contador B/N</span>

                <input
                  v-model.number="manualForm.black_meter"
                  type="number"
                  min="0"
                />
              </label>

              <label>
                <span>Contador color</span>

                <input
                  v-model.number="manualForm.color_meter"
                  type="number"
                  min="0"
                />
              </label>

              <label>
                <span>Contador escáner</span>

                <input
                  v-model.number="manualForm.scan_meter"
                  type="number"
                  min="0"
                />
              </label>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section-heading">
              <div>
                <h3>Contadores adicionales</h3>

                <p>
                  Agrega métricas específicas del fabricante.
                </p>
              </div>

              <button
                class="monitor-button monitor-button-secondary"
                type="button"
                @click="addCounter"
              >
                + Agregar contador
              </button>
            </div>

            <div
              v-for="(counter, index) in manualForm.counters"
              :key="`counter-${index}`"
              class="manual-row-card"
            >
              <button
                class="manual-row-remove"
                type="button"
                @click="
                  removeRow(
                    manualForm.counters,
                    index
                  )
                "
              >
                ×
              </button>

              <div class="monitor-form-grid">
                <label>
                  <span>Código</span>

                  <input
                    v-model.trim="counter.metric_code"
                    type="text"
                    required
                    placeholder="PRINT_COLOR"
                  />
                </label>

                <label>
                  <span>Nombre</span>

                  <input
                    v-model.trim="counter.metric_name"
                    type="text"
                    required
                    placeholder="Impresiones color"
                  />
                </label>

                <label>
                  <span>Valor</span>

                  <input
                    v-model.number="counter.numeric_value"
                    type="number"
                    step="0.0001"
                    required
                  />
                </label>

                <label>
                  <span>Unidad</span>

                  <input
                    v-model.trim="counter.unit"
                    type="text"
                    placeholder="pages"
                  />
                </label>

                <label>
                  <span>Categoría</span>

                  <select
                    v-model="counter.category"
                  >
                    <option value="total">
                      Total
                    </option>

                    <option value="print">
                      Impresión
                    </option>

                    <option value="copy">
                      Copia
                    </option>

                    <option value="scan">
                      Escaneo
                    </option>

                    <option value="fax">
                      Fax
                    </option>

                    <option value="duplex">
                      Dúplex
                    </option>

                    <option value="maintenance">
                      Mantenimiento
                    </option>

                    <option value="other">
                      Otro
                    </option>

                    <option value="unknown">
                      Sin clasificar
                    </option>
                  </select>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="counter.is_primary"
                    type="checkbox"
                  />

                  <span>Contador principal</span>
                </label>
              </div>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section-heading">
              <div>
                <h3>Consumibles</h3>

                <p>
                  Tóneres, tintas, residuos y otros.
                </p>
              </div>

              <button
                class="monitor-button monitor-button-secondary"
                type="button"
                @click="addConsumable"
              >
                + Agregar consumible
              </button>
            </div>

            <div
              v-for="(
                consumable,
                index
              ) in manualForm.consumables"
              :key="`consumable-${index}`"
              class="manual-row-card"
            >
              <button
                class="manual-row-remove"
                type="button"
                @click="
                  removeRow(
                    manualForm.consumables,
                    index
                  )
                "
              >
                ×
              </button>

              <div class="monitor-form-grid">
                <label>
                  <span>Código</span>

                  <input
                    v-model.trim="consumable.metric_code"
                    type="text"
                    required
                    placeholder="TONER_BLACK"
                  />
                </label>

                <label>
                  <span>Nombre</span>

                  <input
                    v-model.trim="consumable.metric_name"
                    type="text"
                    required
                    placeholder="Tóner negro"
                  />
                </label>

                <label>
                  <span>Tipo</span>

                  <select
                    v-model="consumable.consumable_type"
                  >
                    <option
                      v-for="option in consumableTypeOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </label>

                <label>
                  <span>Color</span>

                  <select
                    v-model="consumable.color"
                  >
                    <option
                      v-for="option in colorOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </label>

                <label>
                  <span>Porcentaje</span>

                  <input
                    v-model.number="consumable.percentage"
                    type="number"
                    min="0"
                    max="100"
                    step="0.01"
                  />
                </label>

                <label>
                  <span>Nivel actual</span>

                  <input
                    v-model.number="consumable.current_level"
                    type="number"
                    step="0.0001"
                  />
                </label>

                <label>
                  <span>Capacidad máxima</span>

                  <input
                    v-model.number="consumable.maximum_capacity"
                    type="number"
                    min="0"
                    step="0.0001"
                  />
                </label>

                <label>
                  <span>Estado</span>

                  <select
                    v-model="consumable.status"
                  >
                    <option value="unknown">
                      Desconocido
                    </option>

                    <option value="normal">
                      Normal
                    </option>

                    <option value="low">
                      Bajo
                    </option>

                    <option value="very_low">
                      Muy bajo
                    </option>

                    <option value="empty">
                      Vacío
                    </option>

                    <option value="missing">
                      No instalado
                    </option>

                    <option value="replacement_required">
                      Requiere cambio
                    </option>

                    <option value="error">
                      Con error
                    </option>
                  </select>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="consumable.is_present"
                    type="checkbox"
                  />

                  <span>Instalado</span>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="consumable.replacement_required"
                    type="checkbox"
                  />

                  <span>Requiere reemplazo</span>
                </label>
              </div>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section-heading">
              <div>
                <h3>Componentes</h3>

                <p>
                  Tambor, revelador, fusor y unidades.
                </p>
              </div>

              <button
                class="monitor-button monitor-button-secondary"
                type="button"
                @click="addComponent"
              >
                + Agregar componente
              </button>
            </div>

            <div
              v-for="(
                component,
                index
              ) in manualForm.components"
              :key="`component-${index}`"
              class="manual-row-card"
            >
              <button
                class="manual-row-remove"
                type="button"
                @click="
                  removeRow(
                    manualForm.components,
                    index
                  )
                "
              >
                ×
              </button>

              <div class="monitor-form-grid">
                <label>
                  <span>Código</span>

                  <input
                    v-model.trim="component.metric_code"
                    type="text"
                    required
                    placeholder="DRUM_BLACK"
                  />
                </label>

                <label>
                  <span>Nombre</span>

                  <input
                    v-model.trim="component.metric_name"
                    type="text"
                    required
                    placeholder="Tambor negro"
                  />
                </label>

                <label>
                  <span>Categoría</span>

                  <select
                    v-model="component.component_category"
                  >
                    <option
                      v-for="option in componentCategoryOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </label>

                <label>
                  <span>Color</span>

                  <select
                    v-model="component.color"
                  >
                    <option
                      v-for="option in colorOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </label>

                <label>
                  <span>Porcentaje restante</span>

                  <input
                    v-model.number="component.percentage"
                    type="number"
                    min="0"
                    max="100"
                    step="0.01"
                  />
                </label>

                <label>
                  <span>Ciclos actuales</span>

                  <input
                    v-model.number="component.cycle_count"
                    type="number"
                    min="0"
                  />
                </label>

                <label>
                  <span>Vida esperada</span>

                  <input
                    v-model.number="component.expected_life_cycles"
                    type="number"
                    min="0"
                  />
                </label>

                <label>
                  <span>Estado</span>

                  <select
                    v-model="component.status"
                  >
                    <option value="unknown">
                      Desconocido
                    </option>

                    <option value="normal">
                      Normal
                    </option>

                    <option value="warning">
                      Advertencia
                    </option>

                    <option value="low">
                      Vida baja
                    </option>

                    <option value="very_low">
                      Vida muy baja
                    </option>

                    <option value="replacement_required">
                      Requiere reemplazo
                    </option>

                    <option value="missing">
                      No instalado
                    </option>

                    <option value="error">
                      Con error
                    </option>
                  </select>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="component.is_present"
                    type="checkbox"
                  />

                  <span>Instalado</span>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="component.replacement_required"
                    type="checkbox"
                  />

                  <span>Requiere cambio</span>
                </label>
              </div>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section-heading">
              <div>
                <h3>Bandejas</h3>

                <p>
                  Nivel de papel, capacidad y problemas.
                </p>
              </div>

              <button
                class="monitor-button monitor-button-secondary"
                type="button"
                @click="addTray"
              >
                + Agregar bandeja
              </button>
            </div>

            <div
              v-for="(
                tray,
                index
              ) in manualForm.trays"
              :key="`tray-${index}`"
              class="manual-row-card"
            >
              <button
                class="manual-row-remove"
                type="button"
                @click="
                  removeRow(
                    manualForm.trays,
                    index
                  )
                "
              >
                ×
              </button>

              <div class="monitor-form-grid">
                <label>
                  <span>Código</span>

                  <input
                    v-model.trim="tray.tray_code"
                    type="text"
                    required
                    placeholder="TRAY_1"
                  />
                </label>

                <label>
                  <span>Nombre</span>

                  <input
                    v-model.trim="tray.tray_name"
                    type="text"
                    required
                    placeholder="Bandeja 1"
                  />
                </label>

                <label>
                  <span>Tipo</span>

                  <select
                    v-model="tray.tray_type"
                  >
                    <option
                      v-for="option in trayTypeOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </label>

                <label>
                  <span>Tamaño de papel</span>

                  <input
                    v-model.trim="tray.paper_size"
                    type="text"
                    placeholder="A4"
                  />
                </label>

                <label>
                  <span>Tipo de papel</span>

                  <input
                    v-model.trim="tray.paper_type"
                    type="text"
                    placeholder="Normal"
                  />
                </label>

                <label>
                  <span>Porcentaje</span>

                  <input
                    v-model.number="tray.percentage"
                    type="number"
                    min="0"
                    max="100"
                    step="0.01"
                  />
                </label>

                <label>
                  <span>Cantidad actual</span>

                  <input
                    v-model.number="tray.current_level"
                    type="number"
                    min="0"
                  />
                </label>

                <label>
                  <span>Capacidad máxima</span>

                  <input
                    v-model.number="tray.maximum_capacity"
                    type="number"
                    min="0"
                  />
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="tray.is_present"
                    type="checkbox"
                  />

                  <span>Instalada</span>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="tray.is_open"
                    type="checkbox"
                  />

                  <span>Abierta</span>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="tray.is_empty"
                    type="checkbox"
                  />

                  <span>Vacía</span>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="tray.is_low"
                    type="checkbox"
                  />

                  <span>Papel bajo</span>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="tray.has_jam"
                    type="checkbox"
                  />

                  <span>Atasco</span>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="tray.has_feed_error"
                    type="checkbox"
                  />

                  <span>Error de alimentación</span>
                </label>
              </div>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section-heading">
              <div>
                <h3>Accesorios</h3>

                <p>
                  ADF, dúplex, finalizadores y otros.
                </p>
              </div>

              <button
                class="monitor-button monitor-button-secondary"
                type="button"
                @click="addAccessory"
              >
                + Agregar accesorio
              </button>
            </div>

            <div
              v-for="(
                accessory,
                index
              ) in manualForm.accessories"
              :key="`accessory-${index}`"
              class="manual-row-card"
            >
              <button
                class="manual-row-remove"
                type="button"
                @click="
                  removeRow(
                    manualForm.accessories,
                    index
                  )
                "
              >
                ×
              </button>

              <div class="monitor-form-grid">
                <label>
                  <span>Código</span>

                  <input
                    v-model.trim="accessory.accessory_code"
                    type="text"
                    required
                    placeholder="FINISHER_1"
                  />
                </label>

                <label>
                  <span>Nombre</span>

                  <input
                    v-model.trim="accessory.accessory_name"
                    type="text"
                    required
                    placeholder="Finalizador"
                  />
                </label>

                <label>
                  <span>Tipo</span>

                  <select
                    v-model="accessory.accessory_type"
                  >
                    <option
                      v-for="option in accessoryTypeOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </label>

                <label>
                  <span>Cantidad</span>

                  <input
                    v-model.number="accessory.quantity"
                    type="number"
                    min="1"
                  />
                </label>

                <label>
                  <span>Fabricante</span>

                  <input
                    v-model.trim="accessory.manufacturer_name"
                    type="text"
                  />
                </label>

                <label>
                  <span>Modelo</span>

                  <input
                    v-model.trim="accessory.model_name"
                    type="text"
                  />
                </label>

                <label>
                  <span>Código de producto</span>

                  <input
                    v-model.trim="accessory.product_code"
                    type="text"
                  />
                </label>

                <label>
                  <span>Serie</span>

                  <input
                    v-model.trim="accessory.serial_number"
                    type="text"
                  />
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="accessory.is_installed"
                    type="checkbox"
                  />

                  <span>Instalado</span>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="accessory.is_operational"
                    type="checkbox"
                  />

                  <span>Operativo</span>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="accessory.is_enabled"
                    type="checkbox"
                  />

                  <span>Habilitado</span>
                </label>
              </div>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section-heading">
              <div>
                <h3>Alertas</h3>

                <p>
                  Registra problemas detectados manualmente.
                </p>
              </div>

              <button
                class="monitor-button monitor-button-secondary"
                type="button"
                @click="addAlert"
              >
                + Agregar alerta
              </button>
            </div>

            <div
              v-for="(
                alert,
                index
              ) in manualForm.alerts"
              :key="`alert-${index}`"
              class="manual-row-card"
            >
              <button
                class="manual-row-remove"
                type="button"
                @click="
                  removeRow(
                    manualForm.alerts,
                    index
                  )
                "
              >
                ×
              </button>

              <div class="monitor-form-grid">
                <label>
                  <span>Código</span>

                  <input
                    v-model.trim="alert.normalized_code"
                    type="text"
                    required
                    placeholder="PAPER_JAM"
                  />
                </label>

                <label class="form-field-span-2">
                  <span>Mensaje</span>

                  <input
                    v-model.trim="alert.normalized_message"
                    type="text"
                    required
                    placeholder="Atasco de papel en bandeja 2"
                  />
                </label>

                <label>
                  <span>Categoría</span>

                  <select
                    v-model="alert.category"
                  >
                    <option
                      v-for="option in alertCategoryOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </label>

                <label>
                  <span>Severidad</span>

                  <select
                    v-model="alert.severity"
                  >
                    <option
                      v-for="option in alertSeverityOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </label>

                <label>
                  <span>Componente</span>

                  <input
                    v-model.trim="alert.component_name"
                    type="text"
                  />
                </label>

                <label>
                  <span>Ubicación</span>

                  <input
                    v-model.trim="alert.location_name"
                    type="text"
                  />
                </label>

                <label>
                  <span>Código de servicio</span>

                  <input
                    v-model.trim="alert.service_code"
                    type="text"
                  />
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="alert.blocks_printing"
                    type="checkbox"
                  />

                  <span>Bloquea impresión</span>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="alert.blocks_copying"
                    type="checkbox"
                  />

                  <span>Bloquea copia</span>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="alert.blocks_scanning"
                    type="checkbox"
                  />

                  <span>Bloquea escaneo</span>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="alert.requires_user_action"
                    type="checkbox"
                  />

                  <span>Requiere acción del usuario</span>
                </label>

                <label class="checkbox-field">
                  <input
                    v-model="alert.requires_technical_visit"
                    type="checkbox"
                  />

                  <span>Requiere visita técnica</span>
                </label>
              </div>
            </div>
          </div>

          <div class="form-section">
            <label class="form-field-full">
              <span>Observaciones generales</span>

              <textarea
                v-model.trim="manualForm.notes"
                rows="4"
              ></textarea>
            </label>
          </div>

          <footer class="monitor-modal-footer">
            <button
              class="monitor-button monitor-button-secondary"
              type="button"
              :disabled="saving"
              @click="closeManualModal"
            >
              Cancelar
            </button>

            <button
              class="monitor-button monitor-button-primary"
              type="submit"
              :disabled="saving"
            >
              {{
                saving
                  ? "Registrando..."
                  : "Registrar lectura"
              }}
            </button>
          </footer>
        </form>
      </section>
    </div>

    <div
      v-if="showArchiveModal"
      class="monitor-modal-backdrop"
      @click.self="showArchiveModal = false"
    >
      <section class="monitor-modal monitor-modal-small">
        <header class="monitor-modal-header">
          <div>
            <h2>Archivar dispositivo</h2>

            <p>
              El monitoreo quedará deshabilitado.
            </p>
          </div>

          <button
            class="modal-close"
            type="button"
            @click="showArchiveModal = false"
          >
            ×
          </button>
        </header>

        <div class="monitor-modal-body">
          <label class="form-field-full">
            <span>Motivo</span>

            <textarea
              v-model.trim="archiveReason"
              rows="4"
              placeholder="Indica el motivo del archivado"
            ></textarea>
          </label>
        </div>

        <footer class="monitor-modal-footer">
          <button
            class="monitor-button monitor-button-secondary"
            type="button"
            :disabled="saving"
            @click="showArchiveModal = false"
          >
            Cancelar
          </button>

          <button
            class="monitor-button monitor-button-warning"
            type="button"
            :disabled="saving"
            @click="confirmArchive"
          >
            {{
              saving
                ? "Archivando..."
                : "Archivar"
            }}
          </button>
        </footer>
      </section>
    </div>

    <div
      v-if="showDeleteModal"
      class="monitor-modal-backdrop"
      @click.self="showDeleteModal = false"
    >
      <section class="monitor-modal monitor-modal-small">
        <header class="monitor-modal-header">
          <div>
            <h2>Eliminar dispositivo</h2>

            <p>
              Esta operación puede ser permanente.
            </p>
          </div>

          <button
            class="modal-close"
            type="button"
            @click="showDeleteModal = false"
          >
            ×
          </button>
        </header>

        <div class="monitor-modal-body">
          <div class="delete-warning">
            Escribe el código
            <strong>
              {{ device?.code }}
            </strong>
            para confirmar.
          </div>

          <label class="form-field-full">
            <span>Código del dispositivo</span>

            <input
              v-model.trim="deleteConfirmation"
              type="text"
              autocomplete="off"
            />
          </label>
        </div>

        <footer class="monitor-modal-footer">
          <button
            class="monitor-button monitor-button-secondary"
            type="button"
            :disabled="deleting"
            @click="showDeleteModal = false"
          >
            Cancelar
          </button>

          <button
            class="monitor-button monitor-button-danger"
            type="button"
            :disabled="
              deleting ||
              deleteConfirmation !== device?.code
            "
            @click="confirmDelete"
          >
            {{
              deleting
                ? "Eliminando..."
                : "Eliminar definitivamente"
            }}
          </button>
        </footer>
      </section>
    </div>

    <div
      v-if="showAlertModal"
      class="monitor-modal-backdrop"
      @click.self="showAlertModal = false"
    >
      <section class="monitor-modal monitor-modal-small">
        <header class="monitor-modal-header">
          <div>
            <h2>
              {{
                alertAction === "resolve"
                  ? "Resolver alerta"
                  : "Reconocer alerta"
              }}
            </h2>

            <p>
              {{
                selectedAlert?.normalized_message
              }}
            </p>
          </div>

          <button
            class="modal-close"
            type="button"
            @click="showAlertModal = false"
          >
            ×
          </button>
        </header>

        <div class="monitor-modal-body">
          <label class="form-field-full">
            <span>
              {{
                alertAction === "resolve"
                  ? "Notas de resolución"
                  : "Observaciones"
              }}
            </span>

            <textarea
              v-model.trim="alertNotes"
              rows="5"
            ></textarea>
          </label>
        </div>

        <footer class="monitor-modal-footer">
          <button
            class="monitor-button monitor-button-secondary"
            type="button"
            :disabled="saving"
            @click="showAlertModal = false"
          >
            Cancelar
          </button>

          <button
            class="monitor-button monitor-button-success"
            type="button"
            :disabled="saving"
            @click="confirmAlertAction"
          >
            {{
              saving
                ? "Guardando..."
                : (
                  alertAction === "resolve"
                    ? "Resolver alerta"
                    : "Reconocer alerta"
                )
            }}
          </button>
        </footer>
      </section>
    </div>
  </section>
</template>