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

import RepairChecklistSection from "./components/RepairChecklistSection.vue"
import RepairPhotosSection from "./components/RepairPhotosSection.vue"

import {
  archiveRepair,
  cancelRepair,
  changeRepairStatus,
  getRepairAssignments,
  getRepairById,
  getRepairChecklists,
  getRepairComponents,
  getRepairDiagnoses,
  getRepairPhotos,
  getRepairSNMPValidations,
  getRepairStatusHistory,
  getRepairTests,
  reopenRepair,
  restoreRepair,
} from "../../services/repairs.service"

import "./RepairDetailView.css"


const route = useRoute()
const router = useRouter()

const repairId = computed(
  () => route.params.id
)

const loading = ref(false)
const processing = ref(false)
const errorMessage = ref("")
const successMessage = ref("")

const repair = ref(null)

const assignments = ref([])
const checklists = ref([])
const diagnoses = ref([])
const components = ref([])
const photos = ref([])
const tests = ref([])
const snmpValidations = ref([])
const statusHistory = ref([])

const activeTab = ref("general")
const requestedChecklistItem = ref(null)

const statusFormVisible = ref(false)
const selectedNewStatus = ref("")
const statusReason = ref("")
const statusObservations = ref("")

const cancelFormVisible = ref(false)
const cancelReason = ref("")

const reopenFormVisible = ref(false)
const reopenReason = ref("")


const tabs = computed(() => [
  {
    id: "general",
    label: "General",
    icon: "▣",
    count: null,
  },
  {
    id: "assignments",
    label: "Asignaciones",
    icon: "♙",
    count: assignments.value.length,
  },
  {
    id: "checklist",
    label: "Checklist",
    icon: "✓",
    count: totalChecklistItems.value,
  },
  {
    id: "diagnoses",
    label: "Diagnósticos",
    icon: "⌕",
    count: diagnoses.value.length,
  },
  {
    id: "photos",
    label: "Fotografías",
    icon: "▧",
    count: photos.value.length,
  },
  {
    id: "components",
    label: "Repuestos",
    icon: "⚙",
    count: components.value.length,
  },
  {
    id: "tests",
    label: "Pruebas",
    icon: "◉",
    count: tests.value.length,
  },
  {
    id: "snmp",
    label: "SNMP",
    icon: "⌁",
    count: snmpValidations.value.length,
  },
  {
    id: "history",
    label: "Historial",
    icon: "◷",
    count: statusHistory.value.length,
  },
])


const equipmentName = computed(() => {
  if (!repair.value) {
    return "Equipo sin identificar"
  }

  return (
    repair.value.equipment_name ||
    [
      repair.value.equipment_brand_name ||
      repair.value.brand_name,
      repair.value.equipment_model_name ||
      repair.value.model_name,
    ]
      .filter(Boolean)
      .join(" ")
      .trim() ||
    "Equipo sin identificar"
  )
})


const totalChecklistItems = computed(() => {
  return checklists.value.reduce(
    (total, checklist) => {
      if (
        Array.isArray(
          checklist.items
        )
      ) {
        return (
          total +
          checklist.items.length
        )
      }

      return (
        total +
        Number(
          checklist.item_count || 0
        )
      )
    },
    0
  )
})


const completedChecklistItems = computed(() => {
  return checklists.value.reduce(
    (total, checklist) => {
      if (
        Array.isArray(
          checklist.items
        )
      ) {
        const completed =
          checklist.items.filter(
            (item) =>
              [
                "ok",
                "observed",
                "not_applicable",
              ].includes(
                item.status
              )
          ).length

        return total + completed
      }

      return (
        total +
        Number(
          checklist.completed_item_count ||
          0
        )
      )
    },
    0
  )
})


const requiredPhotos = computed(() => {
  return Number(
    repair.value
      ?.minimum_photos_required ||
    0
  )
})


const countedPhotos = computed(() => {
  return photos.value.filter(
    (photo) =>
      photo.counts_for_minimum &&
      !photo.is_archived
  ).length
})


const completedTests = computed(() => {
  return tests.value.filter(
    (test) =>
      test.status === "completed"
  ).length
})


const statusOptions = computed(() => {
  const currentStatus =
    repair.value?.status

  const transitions = {
    pending: [
      "assigned",
      "under_review",
      "cancelled",
    ],
    assigned: [
      "under_review",
      "cancelled",
    ],
    under_review: [
      "waiting_parts",
      "in_repair",
      "testing",
      "cancelled",
    ],
    waiting_parts: [
      "in_repair",
      "testing",
      "cancelled",
    ],
    in_repair: [
      "waiting_parts",
      "testing",
      "cancelled",
    ],
    testing: [
      "in_repair",
      "completed",
      "cancelled",
    ],
    completed: [
      "delivered",
    ],
    delivered: [],
    cancelled: [],
  }

  return (
    transitions[currentStatus] || []
  )
})


function normalizeCollection(data) {
  if (Array.isArray(data)) {
    return data
  }

  if (
    data &&
    Array.isArray(data.results)
  ) {
    return data.results
  }

  return []
}


function formatDateTime(value) {
  if (!value) {
    return "Sin registro"
  }

  const date = new Date(value)

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
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


function formatDate(value) {
  if (!value) {
    return "Sin registro"
  }

  const date = new Date(
    `${value}T00:00:00`
  )

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
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


function getStatusClass(status) {
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
    classes[status] ||
    "neutral"
  )
}


function getStatusName(
  status,
  displayName = ""
) {
  if (displayName) {
    return displayName
  }

  const names = {
    pending: "Pendiente",
    assigned: "Asignada",
    under_review: "En revisión",
    waiting_parts:
      "Esperando repuestos",
    in_repair: "En reparación",
    testing: "En pruebas",
    completed: "Finalizada",
    delivered: "Entregada",
    cancelled: "Cancelada",
  }

  return (
    names[status] ||
    "Sin estado"
  )
}


function getPriorityClass(priority) {
  return (
    priority ||
    "normal"
  )
}


function getPriorityName(
  priority,
  displayName = ""
) {
  if (displayName) {
    return displayName
  }

  const names = {
    low: "Baja",
    normal: "Normal",
    high: "Alta",
    urgent: "Urgente",
  }

  return (
    names[priority] ||
    "Normal"
  )
}


function getRepairTypeName() {
  if (
    repair.value?.repair_type_name
  ) {
    return (
      repair.value.repair_type_name
    )
  }

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
    names[
      repair.value?.repair_type
    ] ||
    "Sin tipo"
  )
}


function getFinalConditionName() {
  if (
    repair.value
      ?.final_condition_name
  ) {
    return (
      repair.value
        .final_condition_name
    )
  }

  const names = {
    not_defined:
      "No definida",
    operational:
      "Operativa",
    operational_with_observations:
      "Operativa con observaciones",
    requires_parts:
      "Requiere repuestos",
    not_repairable:
      "No reparable",
    for_parts:
      "Para repuestos",
  }

  return (
    names[
      repair.value
        ?.final_condition
    ] ||
    "No definida"
  )
}


function getPhotoUrl(photo) {
  const image =
    photo?.image || ""

  if (!image) {
    return ""
  }

  if (
    String(image).startsWith(
      "http"
    )
  ) {
    return image
  }

  return (
    `http://127.0.0.1:8000${image}`
  )
}


function getBooleanName(value) {
  return value
    ? "Sí"
    : "No"
}


async function loadRepair() {
  repair.value =
    await getRepairById(
      repairId.value
    )
}


async function loadRelatedData() {
  const [
    assignmentsResponse,
    checklistsResponse,
    diagnosesResponse,
    componentsResponse,
    photosResponse,
    testsResponse,
    snmpResponse,
    historyResponse,
  ] = await Promise.all([
    getRepairAssignments({
      repair: repairId.value,
      ordering: "-assigned_at",
    }),
    getRepairChecklists({
      repair: repairId.value,
      ordering: "-is_main_checklist,-created_at",
    }),
    getRepairDiagnoses({
      repair: repairId.value,
      ordering: "-is_main_diagnosis,-diagnosed_at",
    }),
    getRepairComponents({
      repair: repairId.value,
      ordering: "-created_at",
    }),
    getRepairPhotos({
      repair: repairId.value,
      ordering: "display_order,created_at",
    }),
    getRepairTests({
      repair: repairId.value,
      ordering: "display_order,created_at",
    }),
    getRepairSNMPValidations({
      repair: repairId.value,
      ordering: "-created_at",
    }),
    getRepairStatusHistory({
      repair: repairId.value,
      ordering: "-changed_at",
    }),
  ])

  assignments.value =
    normalizeCollection(
      assignmentsResponse
    )

  checklists.value =
    normalizeCollection(
      checklistsResponse
    )

  diagnoses.value =
    normalizeCollection(
      diagnosesResponse
    )

  components.value =
    normalizeCollection(
      componentsResponse
    )

  photos.value =
    normalizeCollection(
      photosResponse
    )

  tests.value =
    normalizeCollection(
      testsResponse
    )

  snmpValidations.value =
    normalizeCollection(
      snmpResponse
    )

  statusHistory.value =
    normalizeCollection(
      historyResponse
    )
}


async function loadData() {
  loading.value = true
  errorMessage.value = ""

  try {
    await loadRepair()
    await loadRelatedData()
  } catch (error) {
    errorMessage.value =
      error.message
  } finally {
    loading.value = false
  }
}


async function refreshData() {
  processing.value = true
  errorMessage.value = ""

  try {
    await loadRepair()
    await loadRelatedData()

    successMessage.value =
      "Información actualizada."

    window.setTimeout(
      () => {
        successMessage.value = ""
      },
      1800
    )
  } catch (error) {
    errorMessage.value =
      error.message
  } finally {
    processing.value = false
  }
}


function handleChecklistPhotoRequest(payload) {
  requestedChecklistItem.value =
    payload?.checklistItem ||
    null

  activeTab.value = "photos"
}


function clearRequestedChecklistItem() {
  requestedChecklistItem.value = null
}


function openStatusForm() {
  selectedNewStatus.value =
    statusOptions.value[0] || ""

  statusReason.value = ""
  statusObservations.value = ""
  statusFormVisible.value = true
}


function closeStatusForm() {
  statusFormVisible.value = false
  selectedNewStatus.value = ""
  statusReason.value = ""
  statusObservations.value = ""
}


async function submitStatusChange() {
  if (!selectedNewStatus.value) {
    errorMessage.value =
      "Selecciona el nuevo estado."

    return
  }

  processing.value = true
  errorMessage.value = ""

  try {
    await changeRepairStatus(
      repairId.value,
      {
        status:
          selectedNewStatus.value,
        reason:
          statusReason.value.trim(),
        observations:
          statusObservations.value.trim(),
      }
    )

    successMessage.value =
      "El estado se actualizó correctamente."

    closeStatusForm()
    await loadData()
  } catch (error) {
    errorMessage.value =
      error.message
  } finally {
    processing.value = false
  }
}


async function submitCancellation() {
  if (
    !cancelReason.value.trim()
  ) {
    errorMessage.value =
      "Debes indicar el motivo de cancelación."

    return
  }

  processing.value = true
  errorMessage.value = ""

  try {
    await cancelRepair(
      repairId.value,
      {
        reason:
          cancelReason.value.trim(),
      }
    )

    cancelFormVisible.value = false
    cancelReason.value = ""

    successMessage.value =
      "La reparación fue cancelada."

    await loadData()
  } catch (error) {
    errorMessage.value =
      error.message
  } finally {
    processing.value = false
  }
}


async function submitReopening() {
  if (
    !reopenReason.value.trim()
  ) {
    errorMessage.value =
      "Debes indicar el motivo de reapertura."

    return
  }

  processing.value = true
  errorMessage.value = ""

  try {
    await reopenRepair(
      repairId.value,
      {
        reason:
          reopenReason.value.trim(),
      }
    )

    reopenFormVisible.value = false
    reopenReason.value = ""

    successMessage.value =
      "La reparación fue reabierta."

    await loadData()
  } catch (error) {
    errorMessage.value =
      error.message
  } finally {
    processing.value = false
  }
}


async function handleArchive() {
  const reason = window.prompt(
    "Indica el motivo del archivo:"
  )

  if (reason === null) {
    return
  }

  processing.value = true
  errorMessage.value = ""

  try {
    await archiveRepair(
      repairId.value,
      reason.trim()
    )

    successMessage.value =
      "La reparación fue archivada."

    await loadData()
  } catch (error) {
    errorMessage.value =
      error.message
  } finally {
    processing.value = false
  }
}


async function handleRestore() {
  processing.value = true
  errorMessage.value = ""

  try {
    await restoreRepair(
      repairId.value
    )

    successMessage.value =
      "La reparación fue restaurada."

    await loadData()
  } catch (error) {
    errorMessage.value =
      error.message
  } finally {
    processing.value = false
  }
}


function goToEdit() {
  router.push({
    name: "repair-edit",
    params: {
      id: repairId.value,
    },
  })
}


function goBack() {
  router.push({
    name: "repairs",
  })
}


onMounted(() => {
  loadData()
})
</script>

<template>
  <section class="repair-detail-page">
    <header class="detail-header">
      <div class="detail-heading">
        <button
          class="back-button"
          type="button"
          @click="goBack"
        >
          ← Volver a reparaciones
        </button>

        <div class="heading-line">
          <div>
            <span class="page-kicker">
              Taller técnico
            </span>

            <h1>
              {{
                repair?.code ||
                "Reparación"
              }}
            </h1>
          </div>

          <span
            v-if="repair"
            class="status-badge"
            :class="
              getStatusClass(
                repair.status
              )
            "
          >
            {{
              getStatusName(
                repair.status,
                repair.status_name
              )
            }}
          </span>
        </div>

        <p>
          Expediente técnico completo de la reparación.
        </p>
      </div>

      <div class="detail-actions">
        <button
          class="secondary-button"
          type="button"
          :disabled="
            loading ||
            processing
          "
          @click="refreshData"
        >
          ↻ Actualizar
        </button>

        <button
          v-if="
            repair &&
            !repair.is_archived
          "
          class="secondary-button"
          type="button"
          :disabled="
            loading ||
            processing
          "
          @click="goToEdit"
        >
          ✎ Editar
        </button>

        <button
          v-if="
            repair?.is_active &&
            statusOptions.length
          "
          class="primary-button"
          type="button"
          :disabled="
            loading ||
            processing
          "
          @click="openStatusForm"
        >
          Cambiar estado
        </button>

        <button
          v-if="
            repair?.is_active &&
            repair?.status !==
              'cancelled'
          "
          class="danger-outline-button"
          type="button"
          :disabled="processing"
          @click="
            cancelFormVisible = true
          "
        >
          Cancelar
        </button>

        <button
          v-if="
            repair?.status ===
              'completed' ||
            repair?.status ===
              'delivered'
          "
          class="warning-button"
          type="button"
          :disabled="processing"
          @click="
            reopenFormVisible = true
          "
        >
          Reabrir
        </button>

        <button
          v-if="
            repair &&
            !repair.is_archived &&
            !repair.is_active
          "
          class="danger-outline-button"
          type="button"
          :disabled="processing"
          @click="handleArchive"
        >
          Archivar
        </button>

        <button
          v-if="
            repair?.is_archived
          "
          class="success-button"
          type="button"
          :disabled="processing"
          @click="handleRestore"
        >
          Restaurar
        </button>
      </div>
    </header>

    <div
      v-if="errorMessage"
      class="detail-message error"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="successMessage"
      class="detail-message success"
    >
      {{ successMessage }}
    </div>

    <div
      v-if="loading"
      class="detail-loading"
    >
      <span class="spinner"></span>

      Cargando expediente de reparación...
    </div>

    <template v-else-if="repair">
      <section class="equipment-hero">
        <div class="equipment-icon">
          ▣
        </div>

        <div class="equipment-title">
          <span>
            Equipo
          </span>

          <strong>
            {{ equipmentName }}
          </strong>

          <small>
            Serie:
            {{
              repair.equipment_serial_number ||
              "Sin serie"
            }}
          </small>
        </div>

        <div class="hero-data">
          <span>
            Código interno
          </span>

          <strong>
            {{
              repair.equipment_internal_code ||
              "Sin código"
            }}
          </strong>
        </div>

        <div class="hero-data">
          <span>
            Tipo de reparación
          </span>

          <strong>
            {{ getRepairTypeName() }}
          </strong>
        </div>

        <div class="hero-data">
          <span>
            Prioridad
          </span>

          <strong
            class="priority-badge"
            :class="
              getPriorityClass(
                repair.priority
              )
            "
          >
            {{
              getPriorityName(
                repair.priority,
                repair.priority_name
              )
            }}
          </strong>
        </div>

        <div class="hero-data">
          <span>
            Técnico
          </span>

          <strong>
            {{
              repair.assigned_technician_name ||
              "Sin técnico asignado"
            }}
          </strong>
        </div>
      </section>

      <section class="progress-grid">
        <article class="progress-card">
          <div class="progress-card-header">
            <span>
              Checklist
            </span>

            <strong>
              {{
                completedChecklistItems
              }}
              /
              {{
                totalChecklistItems
              }}
            </strong>
          </div>

          <div class="progress-track">
            <div
              class="progress-fill"
              :style="{
                width:
                  totalChecklistItems
                    ? `${
                        (
                          completedChecklistItems /
                          totalChecklistItems
                        ) * 100
                      }%`
                    : '0%',
              }"
            ></div>
          </div>
        </article>

        <article class="progress-card">
          <div class="progress-card-header">
            <span>
              Fotografías
            </span>

            <strong>
              {{ countedPhotos }}
              /
              {{ requiredPhotos }}
            </strong>
          </div>

          <div class="progress-track">
            <div
              class="progress-fill"
              :style="{
                width:
                  requiredPhotos
                    ? `${Math.min(
                        (
                          countedPhotos /
                          requiredPhotos
                        ) * 100,
                        100
                      )}%`
                    : '0%',
              }"
            ></div>
          </div>
        </article>

        <article class="progress-card">
          <div class="progress-card-header">
            <span>
              Pruebas
            </span>

            <strong>
              {{ completedTests }}
              /
              {{ tests.length }}
            </strong>
          </div>

          <div class="progress-track">
            <div
              class="progress-fill"
              :style="{
                width:
                  tests.length
                    ? `${
                        (
                          completedTests /
                          tests.length
                        ) * 100
                      }%`
                    : '0%',
              }"
            ></div>
          </div>
        </article>

        <article class="progress-card">
          <div class="progress-card-header">
            <span>
              Validación SNMP
            </span>

            <strong>
              {{
                repair.snmp_validation_completed
                  ? "Completa"
                  : "Pendiente"
              }}
            </strong>
          </div>

          <div class="progress-track">
            <div
              class="progress-fill"
              :style="{
                width:
                  repair.snmp_validation_completed
                    ? '100%'
                    : '0%',
              }"
            ></div>
          </div>
        </article>
      </section>

      <nav class="detail-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          type="button"
          class="tab-button"
          :class="{
            active:
              activeTab === tab.id,
          }"
          @click="
            activeTab = tab.id
          "
        >
          <span class="tab-icon">
            {{ tab.icon }}
          </span>

          <span>
            {{ tab.label }}
          </span>

          <small
            v-if="
              tab.count !== null
            "
          >
            {{ tab.count }}
          </small>
        </button>
      </nav>

      <section
        v-if="
          activeTab === 'general'
        "
        class="tab-panel"
      >
        <div class="panel-grid">
          <article class="detail-card wide-card">
            <div class="card-heading">
              <h2>
                Problema reportado
              </h2>
            </div>

            <p class="text-content">
              {{
                repair.reported_problem ||
                "Sin información"
              }}
            </p>
          </article>

          <article class="detail-card wide-card">
            <div class="card-heading">
              <h2>
                Observaciones iniciales
              </h2>
            </div>

            <p class="text-content">
              {{
                repair.initial_observations ||
                "Sin observaciones"
              }}
            </p>
          </article>

          <article class="detail-card">
            <div class="card-heading">
              <h2>
                Requisitos
              </h2>
            </div>

            <dl class="detail-list">
              <div>
                <dt>
                  Requiere repuestos
                </dt>

                <dd>
                  {{
                    getBooleanName(
                      repair.requires_parts
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>
                  Servicio externo
                </dt>

                <dd>
                  {{
                    getBooleanName(
                      repair.requires_external_service
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>
                  Seguimiento
                </dt>

                <dd>
                  {{
                    getBooleanName(
                      repair.requires_follow_up
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>
                  Fecha de seguimiento
                </dt>

                <dd>
                  {{
                    formatDate(
                      repair.follow_up_date
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>
                  Fotografías mínimas
                </dt>

                <dd>
                  {{
                    repair.minimum_photos_required
                  }}
                </dd>
              </div>
            </dl>
          </article>

          <article class="detail-card">
            <div class="card-heading">
              <h2>
                Fechas del proceso
              </h2>
            </div>

            <dl class="detail-list">
              <div>
                <dt>
                  Solicitada
                </dt>

                <dd>
                  {{
                    formatDateTime(
                      repair.requested_at
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>
                  Asignada
                </dt>

                <dd>
                  {{
                    formatDateTime(
                      repair.assigned_at
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>
                  Revisión iniciada
                </dt>

                <dd>
                  {{
                    formatDateTime(
                      repair.review_started_at
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>
                  Reparación iniciada
                </dt>

                <dd>
                  {{
                    formatDateTime(
                      repair.repair_started_at
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>
                  Pruebas iniciadas
                </dt>

                <dd>
                  {{
                    formatDateTime(
                      repair.testing_started_at
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>
                  Finalizada
                </dt>

                <dd>
                  {{
                    formatDateTime(
                      repair.completed_at
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>
                  Entregada
                </dt>

                <dd>
                  {{
                    formatDateTime(
                      repair.delivered_at
                    )
                  }}
                </dd>
              </div>
            </dl>
          </article>

          <article class="detail-card wide-card">
            <div class="card-heading">
              <h2>
                Resumen del trabajo
              </h2>
            </div>

            <p class="text-content">
              {{
                repair.work_summary ||
                "Aún no se ha registrado el resumen del trabajo."
              }}
            </p>
          </article>

          <article class="detail-card wide-card">
            <div class="card-heading">
              <h2>
                Trabajo pendiente
              </h2>
            </div>

            <p class="text-content">
              {{
                repair.pending_work ||
                "No hay trabajo pendiente registrado."
              }}
            </p>
          </article>

          <article class="detail-card">
            <div class="card-heading">
              <h2>
                Condición final
              </h2>
            </div>

            <strong class="final-condition">
              {{
                getFinalConditionName()
              }}
            </strong>
          </article>

          <article class="detail-card">
            <div class="card-heading">
              <h2>
                Cierre
              </h2>
            </div>

            <p class="text-content">
              {{
                repair.closure_notes ||
                "Sin notas de cierre."
              }}
            </p>
          </article>
        </div>
      </section>

      <section
        v-if="
          activeTab === 'assignments'
        "
        class="tab-panel"
      >
        <div
          v-if="
            !assignments.length
          "
          class="empty-panel"
        >
          No existen asignaciones registradas.
        </div>

        <div
          v-else
          class="records-list"
        >
          <article
            v-for="
              assignment
              in assignments
            "
            :key="assignment.id"
            class="record-card"
          >
            <div class="record-main">
              <strong>
                {{
                  assignment.technician_name ||
                  "Técnico sin nombre"
                }}
              </strong>

              <span>
                {{
                  assignment.assignment_reason ||
                  "Sin motivo de asignación"
                }}
              </span>
            </div>

            <span
              class="record-status"
              :class="
                assignment.status
              "
            >
              {{
                assignment.status_name ||
                assignment.status
              }}
            </span>

            <div class="record-date">
              {{
                formatDateTime(
                  assignment.assigned_at
                )
              }}
            </div>
          </article>
        </div>
      </section>

      <section
        v-if="
          activeTab === 'checklist'
        "
        class="tab-panel"
      >
        <RepairChecklistSection
          :repair-id="repair.id"
          :repair="repair"
          @updated="refreshData"
          @request-photo="
            handleChecklistPhotoRequest
          "
        />
      </section>

      <section
        v-if="
          activeTab === 'diagnoses'
        "
        class="tab-panel"
      >
        <div
          v-if="
            !diagnoses.length
          "
          class="empty-panel"
        >
          No hay diagnósticos registrados.
        </div>

        <div
          v-else
          class="records-list"
        >
          <article
            v-for="
              diagnosis
              in diagnoses
            "
            :key="diagnosis.id"
            class="diagnosis-card"
          >
            <div class="diagnosis-heading">
              <div>
                <strong>
                  {{
                    diagnosis.diagnosis_type_name ||
                    "Diagnóstico técnico"
                  }}
                </strong>

                <span>
                  {{
                    diagnosis.technician_name ||
                    "Técnico no identificado"
                  }}
                </span>
              </div>

              <div class="diagnosis-badges">
                <span
                  v-if="
                    diagnosis.is_main_diagnosis
                  "
                  class="main-badge"
                >
                  Principal
                </span>

                <span
                  v-if="
                    diagnosis.is_confirmed
                  "
                  class="verified-badge"
                >
                  Confirmado
                </span>
              </div>
            </div>

            <p>
              {{
                diagnosis.technical_diagnosis ||
                "Sin diagnóstico técnico"
              }}
            </p>

            <div class="diagnosis-footer">
              <span>
                Severidad:
                {{
                  diagnosis.severity_name ||
                  diagnosis.severity
                }}
              </span>

              <span>
                Reparabilidad:
                {{
                  diagnosis.repairability_name ||
                  diagnosis.repairability
                }}
              </span>

              <span>
                {{
                  formatDateTime(
                    diagnosis.diagnosed_at
                  )
                }}
              </span>
            </div>
          </article>
        </div>
      </section>

      <section
        v-if="
          activeTab === 'photos'
        "
        class="tab-panel"
      >
        <RepairPhotosSection
          :repair-id="repair.id"
          :repair="repair"
          :requested-checklist-item="
            requestedChecklistItem
          "
          @updated="refreshData"
          @request-completed="
            clearRequestedChecklistItem
          "
        />
      </section>

      <section
        v-if="
          activeTab === 'components'
        "
        class="tab-panel"
      >
        <div
          v-if="
            !components.length
          "
          class="empty-panel"
        >
          No hay repuestos o componentes registrados.
        </div>

        <div
          v-else
          class="table-container"
        >
          <table>
            <thead>
              <tr>
                <th>
                  Componente
                </th>

                <th>
                  Movimiento
                </th>

                <th>
                  Estado
                </th>

                <th>
                  Cantidad
                </th>

                <th>
                  Instalado
                </th>

                <th>
                  Costo
                </th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="
                  component
                  in components
                "
                :key="component.id"
              >
                <td>
                  <strong>
                    {{
                      component.component_name
                    }}
                  </strong>

                  <small>
                    {{
                      component.component_code
                    }}
                  </small>
                </td>

                <td>
                  {{
                    component.movement_type_name ||
                    component.movement_type
                  }}
                </td>

                <td>
                  <span
                    class="record-status"
                    :class="
                      component.status
                    "
                  >
                    {{
                      component.status_name ||
                      component.status
                    }}
                  </span>
                </td>

                <td>
                  {{ component.quantity }}
                </td>

                <td>
                  {{
                    component.installed_quantity ||
                    0
                  }}
                </td>

                <td>
                  S/
                  {{
                    component.total_cost ||
                    "0.00"
                  }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section
        v-if="
          activeTab === 'tests'
        "
        class="tab-panel"
      >
        <div
          v-if="
            !tests.length
          "
          class="empty-panel"
        >
          No hay pruebas técnicas registradas.
        </div>

        <div
          v-else
          class="records-list"
        >
          <article
            v-for="
              test
              in tests
            "
            :key="test.id"
            class="test-card"
          >
            <div class="test-icon">
              {{
                test.result === "passed"
                  ? "✓"
                  : test.result === "failed"
                    ? "×"
                    : "○"
              }}
            </div>

            <div class="record-main">
              <strong>
                {{ test.name }}
              </strong>

              <span>
                {{
                  test.test_type_name ||
                  test.test_type
                }}
              </span>

              <small>
                {{
                  test.result_name ||
                  test.result
                }}
              </small>
            </div>

            <span
              class="record-status"
              :class="
                test.status
              "
            >
              {{
                test.status_name ||
                test.status
              }}
            </span>
          </article>
        </div>
      </section>

      <section
        v-if="
          activeTab === 'snmp'
        "
        class="tab-panel"
      >
        <div
          v-if="
            !snmpValidations.length
          "
          class="empty-panel"
        >
          No hay validaciones SNMP registradas.
        </div>

        <div
          v-else
          class="records-list"
        >
          <article
            v-for="
              validation
              in snmpValidations
            "
            :key="validation.id"
            class="snmp-card"
          >
            <div class="snmp-indicator">
              {{
                validation.is_successful
                  ? "✓"
                  : "⌁"
              }}
            </div>

            <div class="record-main">
              <strong>
                {{
                  validation.host ||
                  "Host no registrado"
                }}
              </strong>

              <span>
                {{
                  validation.detected_brand ||
                  ""
                }}
                {{
                  validation.detected_model ||
                  ""
                }}
              </span>

              <small>
                Serie detectada:
                {{
                  validation.device_serial_number ||
                  "Sin serie"
                }}
              </small>
            </div>

            <div class="snmp-matches">
              <span
                :class="{
                  success:
                    validation.serial_matches,
                  danger:
                    validation.serial_matches === false,
                }"
              >
                Serie
              </span>

              <span
                :class="{
                  success:
                    validation.brand_matches,
                  danger:
                    validation.brand_matches === false,
                }"
              >
                Marca
              </span>

              <span
                :class="{
                  success:
                    validation.model_matches,
                  danger:
                    validation.model_matches === false,
                }"
              >
                Modelo
              </span>
            </div>
          </article>
        </div>
      </section>

      <section
        v-if="
          activeTab === 'history'
        "
        class="tab-panel"
      >
        <div
          v-if="
            !statusHistory.length
          "
          class="empty-panel"
        >
          No existe historial de estados.
        </div>

        <div
          v-else
          class="timeline"
        >
          <article
            v-for="
              history
              in statusHistory
            "
            :key="history.id"
            class="timeline-item"
          >
            <span
              class="timeline-dot"
              :class="
                getStatusClass(
                  history.new_status
                )
              "
            ></span>

            <div class="timeline-content">
              <div class="timeline-heading">
                <strong>
                  {{
                    history.new_status_name ||
                    getStatusName(
                      history.new_status
                    )
                  }}
                </strong>

                <span>
                  {{
                    formatDateTime(
                      history.changed_at
                    )
                  }}
                </span>
              </div>

              <p>
                {{
                  history.reason ||
                  "Cambio de estado"
                }}
              </p>

              <small>
                Modificado por:
                {{
                  history.changed_by_name ||
                  "Sistema"
                }}
              </small>

              <small
                v-if="
                  history.duration_minutes
                "
              >
                Duración anterior:
                {{
                  history.duration_minutes
                }}
                minutos
              </small>
            </div>
          </article>
        </div>
      </section>
    </template>

    <div
      v-if="statusFormVisible"
      class="modal-backdrop"
      @click.self="closeStatusForm"
    >
      <form
        class="action-modal"
        @submit.prevent="
          submitStatusChange
        "
      >
        <div class="modal-heading">
          <div>
            <h2>
              Cambiar estado
            </h2>

            <p>
              Actualiza la etapa actual de la reparación.
            </p>
          </div>

          <button
            type="button"
            class="modal-close"
            @click="closeStatusForm"
          >
            ×
          </button>
        </div>

        <label class="modal-field">
          <span>
            Nuevo estado
          </span>

          <select
            v-model="
              selectedNewStatus
            "
            required
          >
            <option
              v-for="
                item
                in statusOptions
              "
              :key="item"
              :value="item"
            >
              {{
                getStatusName(item)
              }}
            </option>
          </select>
        </label>

        <label class="modal-field">
          <span>
            Motivo
          </span>

          <textarea
            v-model="statusReason"
            rows="3"
            placeholder="Motivo del cambio"
          ></textarea>
        </label>

        <label class="modal-field">
          <span>
            Observaciones
          </span>

          <textarea
            v-model="
              statusObservations
            "
            rows="4"
            placeholder="Observaciones adicionales"
          ></textarea>
        </label>

        <div class="modal-actions">
          <button
            class="secondary-button"
            type="button"
            @click="closeStatusForm"
          >
            Cancelar
          </button>

          <button
            class="primary-button"
            type="submit"
            :disabled="processing"
          >
            {{
              processing
                ? "Procesando..."
                : "Cambiar estado"
            }}
          </button>
        </div>
      </form>
    </div>

    <div
      v-if="cancelFormVisible"
      class="modal-backdrop"
      @click.self="
        cancelFormVisible = false
      "
    >
      <form
        class="action-modal"
        @submit.prevent="
          submitCancellation
        "
      >
        <div class="modal-heading">
          <div>
            <h2>
              Cancelar reparación
            </h2>

            <p>
              Esta acción detendrá el proceso técnico.
            </p>
          </div>

          <button
            type="button"
            class="modal-close"
            @click="
              cancelFormVisible = false
            "
          >
            ×
          </button>
        </div>

        <label class="modal-field">
          <span>
            Motivo de cancelación
          </span>

          <textarea
            v-model="cancelReason"
            rows="5"
            required
            placeholder="Describe el motivo"
          ></textarea>
        </label>

        <div class="modal-actions">
          <button
            class="secondary-button"
            type="button"
            @click="
              cancelFormVisible = false
            "
          >
            Volver
          </button>

          <button
            class="danger-button"
            type="submit"
            :disabled="processing"
          >
            Confirmar cancelación
          </button>
        </div>
      </form>
    </div>

    <div
      v-if="reopenFormVisible"
      class="modal-backdrop"
      @click.self="
        reopenFormVisible = false
      "
    >
      <form
        class="action-modal"
        @submit.prevent="
          submitReopening
        "
      >
        <div class="modal-heading">
          <div>
            <h2>
              Reabrir reparación
            </h2>

            <p>
              Registra el motivo de la reapertura.
            </p>
          </div>

          <button
            type="button"
            class="modal-close"
            @click="
              reopenFormVisible = false
            "
          >
            ×
          </button>
        </div>

        <label class="modal-field">
          <span>
            Motivo
          </span>

          <textarea
            v-model="reopenReason"
            rows="5"
            required
            placeholder="Describe el motivo de reapertura"
          ></textarea>
        </label>

        <div class="modal-actions">
          <button
            class="secondary-button"
            type="button"
            @click="
              reopenFormVisible = false
            "
          >
            Cancelar
          </button>

          <button
            class="warning-button"
            type="submit"
            :disabled="processing"
          >
            Reabrir reparación
          </button>
        </div>
      </form>
    </div>
  </section>
</template>