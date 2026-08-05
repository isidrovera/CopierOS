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

const repair = ref(null)

const assignments = ref([])
const checklists = ref([])
const components = ref([])
const diagnoses = ref([])
const photos = ref([])
const tests = ref([])
const snmpValidations = ref([])
const statusHistory = ref([])

const loading = ref(false)
const loadingRelations = ref(false)
const processing = ref(false)

const errorMessage = ref("")
const successMessage = ref("")

const activeTab = ref("general")

const actionModalOpen = ref(false)
const actionModalType = ref("")
const actionReason = ref("")
const selectedStatus = ref("")
const selectedFinalCondition = ref("not_defined")
const workSummary = ref("")
const finalObservations = ref("")
const closureNotes = ref("")
const modalError = ref("")


const repairId = computed(() => {
  return String(
    route.params.id || ""
  )
})


const equipmentId = computed(() => {
  const value =
    repair.value?.equipment

  if (
    value &&
    typeof value === "object"
  ) {
    return String(
      value.id || ""
    )
  }

  return String(
    value || ""
  )
})


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
    repair.value.equipment_serial_number ||
    "Equipo sin identificar"
  )
})


const isArchived = computed(() => {
  return Boolean(
    repair.value?.is_archived ||
    repair.value?.archived_at
  )
})


const canEdit = computed(() => {
  if (
    !repair.value ||
    isArchived.value
  ) {
    return false
  }

  return ![
    "delivered",
    "cancelled",
  ].includes(
    repair.value.status
  )
})


const canCancel = computed(() => {
  if (
    !repair.value ||
    isArchived.value
  ) {
    return false
  }

  return ![
    "completed",
    "delivered",
    "cancelled",
  ].includes(
    repair.value.status
  )
})


const canReopen = computed(() => {
  if (
    !repair.value ||
    isArchived.value
  ) {
    return false
  }

  return [
    "completed",
    "delivered",
    "cancelled",
  ].includes(
    repair.value.status
  )
})


const photoProgress = computed(() => {
  const required = Math.max(
    Number(
      repair.value
        ?.minimum_photos_required ||
      0
    ),
    1
  )

  const current =
    photos.value.filter(
      (photo) =>
        photo.counts_for_minimum !==
        false &&
        !photo.is_archived
    ).length

  return Math.min(
    Math.round(
      (
        current /
        required
      ) *
      100
    ),
    100
  )
})


const checklistProgress = computed(() => {
  if (!checklists.value.length) {
    return repair.value
      ?.checklist_completed
      ? 100
      : 0
  }

  const completed =
    checklists.value.filter(
      (item) =>
        item.status === "completed" ||
        item.is_completed === true
    ).length

  return Math.round(
    (
      completed /
      checklists.value.length
    ) *
    100
  )
})


const testsProgress = computed(() => {
  if (!tests.value.length) {
    return repair.value
      ?.tests_completed
      ? 100
      : 0
  }

  const completed =
    tests.value.filter(
      (item) =>
        [
          "completed",
          "passed",
          "failed",
        ].includes(item.status) ||
        item.result
    ).length

  return Math.round(
    (
      completed /
      tests.value.length
    ) *
    100
  )
})


const snmpProgress = computed(() => {
  if (!snmpValidations.value.length) {
    return repair.value
      ?.snmp_validation_completed
      ? 100
      : 0
  }

  const completed =
    snmpValidations.value.filter(
      (item) =>
        [
          "completed",
          "failed",
        ].includes(item.status) ||
        item.is_successful !== null
    ).length

  return Math.round(
    (
      completed /
      snmpValidations.value.length
    ) *
    100
  )
})


const actionModalTitle = computed(() => {
  const titles = {
    status:
      "Cambiar estado",
    cancel:
      "Cancelar reparación",
    reopen:
      "Reabrir reparación",
    archive:
      "Archivar reparación",
  }

  return (
    titles[actionModalType.value] ||
    "Actualizar reparación"
  )
})


const statusOptions = [
  {
    value: "pending",
    label: "Pendiente",
  },
  {
    value: "assigned",
    label: "Asignada",
  },
  {
    value: "under_review",
    label: "En revisión",
  },
  {
    value: "waiting_parts",
    label: "Esperando repuestos",
  },
  {
    value: "in_repair",
    label: "En reparación",
  },
  {
    value: "testing",
    label: "En pruebas",
  },
  {
    value: "completed",
    label: "Finalizada",
  },
  {
    value: "delivered",
    label: "Entregada",
  },
  {
    value: "cancelled",
    label: "Cancelada",
  },
]


const finalConditionOptions = [
  {
    value: "not_defined",
    label: "No definida",
  },
  {
    value: "operational",
    label: "Operativa",
  },
  {
    value:
      "operational_with_observations",
    label:
      "Operativa con observaciones",
  },
  {
    value: "requires_parts",
    label: "Requiere repuestos",
  },
  {
    value: "not_repairable",
    label: "No reparable",
  },
  {
    value: "for_parts",
    label: "Para repuestos",
  },
]


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


function getStatusName(value) {
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
    names[value] ||
    value ||
    "Sin estado"
  )
}


function getStatusClass(value) {
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


function getPriorityName(value) {
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


function getFinalConditionName(value) {
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
    names[value] ||
    value ||
    "No definida"
  )
}


function getBooleanText(value) {
  return value
    ? "Sí"
    : "No"
}


function getRecordStatusName(value) {
  const names = {
    pending: "Pendiente",
    assigned: "Asignada",
    accepted: "Aceptada",
    rejected: "Rechazada",
    in_progress: "En proceso",
    under_review: "En revisión",
    requested: "Solicitado",
    waiting_parts:
      "Esperando repuestos",
    installed: "Instalado",
    completed: "Completado",
    cancelled: "Cancelado",
    passed: "Aprobada",
    failed: "Fallida",
    ok: "Correcto",
  }

  return (
    names[value] ||
    value ||
    "Sin estado"
  )
}


async function loadRepair() {
  loading.value = true
  errorMessage.value = ""

  try {
    repair.value =
      await getRepairById(
        repairId.value
      )
  } catch (error) {
    repair.value = null

    errorMessage.value =
      error.message ||
      "No se pudo cargar la reparación."
  } finally {
    loading.value = false
  }
}


async function loadRelations() {
  loadingRelations.value = true

  try {
    const responses =
      await Promise.all([
        getRepairAssignments({
          repair: repairId.value,
          includeArchived: true,
          ordering: "-created_at",
        }),
        getRepairChecklists({
          repair: repairId.value,
          includeArchived: true,
          ordering: "-created_at",
        }),
        getRepairComponents({
          repair: repairId.value,
          includeArchived: true,
          ordering: "-created_at",
        }),
        getRepairDiagnoses({
          repair: repairId.value,
          includeArchived: true,
          ordering: "-created_at",
        }),
        getRepairPhotos({
          repair: repairId.value,
          includeArchived: true,
          ordering: "-created_at",
        }),
        getRepairTests({
          repair: repairId.value,
          includeArchived: true,
          ordering: "-created_at",
        }),
        getRepairSNMPValidations({
          repair: repairId.value,
          includeArchived: true,
          ordering: "-created_at",
        }),
        getRepairStatusHistory({
          repair: repairId.value,
          includeArchived: true,
          ordering: "-created_at",
        }),
      ])

    assignments.value =
      normalizeList(responses[0])

    checklists.value =
      normalizeList(responses[1])

    components.value =
      normalizeList(responses[2])

    diagnoses.value =
      normalizeList(responses[3])

    photos.value =
      normalizeList(responses[4])

    tests.value =
      normalizeList(responses[5])

    snmpValidations.value =
      normalizeList(responses[6])

    statusHistory.value =
      normalizeList(responses[7])
  } catch (error) {
    assignments.value = []
    checklists.value = []
    components.value = []
    diagnoses.value = []
    photos.value = []
    tests.value = []
    snmpValidations.value = []
    statusHistory.value = []

    errorMessage.value =
      error.message ||
      "No se pudieron cargar los registros relacionados."
  } finally {
    loadingRelations.value = false
  }
}


async function reloadAll() {
  await Promise.all([
    loadRepair(),
    loadRelations(),
  ])
}


async function goBack() {
  await router.push({
    name: "repairs",
  })
}


async function goToEdit() {
  if (!repair.value?.id) {
    return
  }

  await router.push({
    name: "repair-edit",
    params: {
      id: repair.value.id,
    },
  })
}


async function goToEquipment() {
  if (!equipmentId.value) {
    errorMessage.value =
      "La reparación no tiene un equipo relacionado."

    return
  }

  await router.push({
    name: "equipment-detail",
    params: {
      id: equipmentId.value,
    },
  })
}


async function goToPartRequest() {
  if (!repair.value?.id) {
    return
  }

  await router.push({
    name:
      "repair-part-request-create",
    query: {
      repair: repair.value.id,
    },
  })
}


function openActionModal(type) {
  if (
    !repair.value ||
    processing.value
  ) {
    return
  }

  actionModalType.value = type
  actionReason.value = ""
  modalError.value = ""

  selectedStatus.value =
    repair.value.status || ""

  selectedFinalCondition.value =
    repair.value.final_condition ||
    "not_defined"

  workSummary.value =
    repair.value.work_summary || ""

  finalObservations.value =
    repair.value.final_observations ||
    ""

  closureNotes.value =
    repair.value.closure_notes || ""

  actionModalOpen.value = true
}


function closeActionModal() {
  if (processing.value) {
    return
  }

  actionModalOpen.value = false
  actionModalType.value = ""
  actionReason.value = ""
  selectedStatus.value = ""
  selectedFinalCondition.value =
    "not_defined"

  workSummary.value = ""
  finalObservations.value = ""
  closureNotes.value = ""
  modalError.value = ""
}


async function submitAction() {
  if (!repair.value?.id) {
    return
  }

  processing.value = true
  modalError.value = ""
  errorMessage.value = ""
  successMessage.value = ""

  try {
    if (
      actionModalType.value ===
      "status"
    ) {
      if (!selectedStatus.value) {
        throw new Error(
          "Selecciona el nuevo estado."
        )
      }

      const payload = {
        status:
          selectedStatus.value,
        reason:
          actionReason.value.trim(),
        observations:
          actionReason.value.trim(),
      }

      if (
        [
          "completed",
          "delivered",
        ].includes(
          selectedStatus.value
        )
      ) {
        payload.final_condition =
          selectedFinalCondition.value

        payload.work_summary =
          workSummary.value.trim()

        payload.final_observations =
          finalObservations.value.trim()

        payload.closure_notes =
          closureNotes.value.trim()
      }

      await changeRepairStatus(
        repair.value.id,
        payload
      )

      successMessage.value =
        "Estado actualizado correctamente."
    }

    if (
      actionModalType.value ===
      "cancel"
    ) {
      if (!actionReason.value.trim()) {
        throw new Error(
          "Indica el motivo de cancelación."
        )
      }

      await cancelRepair(
        repair.value.id,
        {
          reason:
            actionReason.value.trim(),
          observations:
            actionReason.value.trim(),
        }
      )

      successMessage.value =
        "Reparación cancelada correctamente."
    }

    if (
      actionModalType.value ===
      "reopen"
    ) {
      if (!actionReason.value.trim()) {
        throw new Error(
          "Indica el motivo de reapertura."
        )
      }

      await reopenRepair(
        repair.value.id,
        {
          reason:
            actionReason.value.trim(),
          observations:
            actionReason.value.trim(),
        }
      )

      successMessage.value =
        "Reparación reabierta correctamente."
    }

    if (
      actionModalType.value ===
      "archive"
    ) {
      await archiveRepair(
        repair.value.id,
        actionReason.value.trim()
      )

      successMessage.value =
        "Reparación archivada correctamente."
    }

    actionModalOpen.value = false

    await reloadAll()
  } catch (error) {
    modalError.value =
      error.message ||
      "No se pudo completar la acción."
  } finally {
    processing.value = false
  }
}


async function handleRestore() {
  if (!repair.value?.id) {
    return
  }

  const confirmed =
    window.confirm(
      "¿Confirmas que deseas restaurar esta reparación?"
    )

  if (!confirmed) {
    return
  }

  processing.value = true
  errorMessage.value = ""
  successMessage.value = ""

  try {
    await restoreRepair(
      repair.value.id
    )

    successMessage.value =
      "Reparación restaurada correctamente."

    await reloadAll()
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo restaurar la reparación."
  } finally {
    processing.value = false
  }
}


function openPhoto(photo) {
  const url =
    photo.file_url ||
    photo.image_url ||
    photo.file ||
    photo.image

  if (!url) {
    errorMessage.value =
      "La fotografía no tiene un archivo disponible."

    return
  }

  window.open(
    url,
    "_blank",
    "noopener,noreferrer"
  )
}


onMounted(async () => {
  await reloadAll()
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
          ← Volver
        </button>

        <span class="page-kicker">
          Expediente de taller
        </span>

        <div class="heading-line">
          <h1>
            {{
              repair?.code ||
              "Detalle de reparación"
            }}
          </h1>

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
              repair.status_name ||
              getStatusName(
                repair.status
              )
            }}
          </span>

          <span
            v-if="repair"
            class="priority-badge"
            :class="
              repair.priority ||
              'normal'
            "
          >
            {{
              repair.priority_name ||
              getPriorityName(
                repair.priority
              )
            }}
          </span>
        </div>

        <p v-if="repair">
          Solicitada el
          {{
            formatDateTime(
              repair.requested_at
            )
          }}
        </p>
      </div>

      <div
        v-if="repair"
        class="detail-actions"
      >
        <button
          class="secondary-button"
          type="button"
          :disabled="
            processing ||
            !equipmentId
          "
          @click="goToEquipment"
        >
          Ver equipo
        </button>

        <button
          v-if="canEdit"
          class="secondary-button"
          type="button"
          :disabled="processing"
          @click="goToEdit"
        >
          Editar
        </button>

        <button
          v-if="
            !isArchived &&
            repair.is_active
          "
          class="primary-button"
          type="button"
          :disabled="processing"
          @click="
            openActionModal('status')
          "
        >
          Cambiar estado
        </button>

        <button
          v-if="
            !isArchived &&
            repair.is_active
          "
          class="warning-button"
          type="button"
          :disabled="processing"
          @click="goToPartRequest"
        >
          Solicitar repuestos
        </button>

        <button
          v-if="canReopen"
          class="success-button"
          type="button"
          :disabled="processing"
          @click="
            openActionModal('reopen')
          "
        >
          Reabrir
        </button>

        <button
          v-if="canCancel"
          class="danger-outline-button"
          type="button"
          :disabled="processing"
          @click="
            openActionModal('cancel')
          "
        >
          Cancelar
        </button>

        <button
          v-if="!isArchived"
          class="danger-button"
          type="button"
          :disabled="processing"
          @click="
            openActionModal('archive')
          "
        >
          Archivar
        </button>

        <button
          v-else
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

      Cargando reparación...
    </div>

    <template v-else-if="repair">
      <section
        class="equipment-hero equipment-hero-link"
        role="button"
        tabindex="0"
        @click="goToEquipment"
        @keydown.enter="goToEquipment"
      >
        <div class="equipment-icon">
          ▣
        </div>

        <div class="equipment-title">
          <span>
            Equipo relacionado
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
          <span>Código interno</span>

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
            {{
              repair.repair_type_name ||
              getRepairTypeName(
                repair.repair_type
              )
            }}
          </strong>
        </div>

        <div class="hero-data">
          <span>Técnico</span>

          <strong>
            {{
              repair.assigned_technician_name ||
              "Sin técnico asignado"
            }}
          </strong>
        </div>

        <div class="hero-data">
          <span>Acceso directo</span>

          <strong class="equipment-link-label">
            Ver ficha del equipo →
          </strong>
        </div>
      </section>

      <section class="progress-grid">
        <article class="progress-card">
          <header class="progress-card-header">
            <span>Fotografías</span>

            <strong>
              {{ photoProgress }}%
            </strong>
          </header>

          <div class="progress-track">
            <div
              class="progress-fill"
              :style="{
                width:
                  `${photoProgress}%`,
              }"
            ></div>
          </div>
        </article>

        <article class="progress-card">
          <header class="progress-card-header">
            <span>Checklist</span>

            <strong>
              {{ checklistProgress }}%
            </strong>
          </header>

          <div class="progress-track">
            <div
              class="progress-fill"
              :style="{
                width:
                  `${checklistProgress}%`,
              }"
            ></div>
          </div>
        </article>

        <article class="progress-card">
          <header class="progress-card-header">
            <span>Pruebas</span>

            <strong>
              {{ testsProgress }}%
            </strong>
          </header>

          <div class="progress-track">
            <div
              class="progress-fill"
              :style="{
                width:
                  `${testsProgress}%`,
              }"
            ></div>
          </div>
        </article>

        <article class="progress-card">
          <header class="progress-card-header">
            <span>Validación SNMP</span>

            <strong>
              {{ snmpProgress }}%
            </strong>
          </header>

          <div class="progress-track">
            <div
              class="progress-fill"
              :style="{
                width:
                  `${snmpProgress}%`,
              }"
            ></div>
          </div>
        </article>
      </section>

      <nav class="detail-tabs">
        <button
          class="tab-button"
          :class="{
            active:
              activeTab === 'general',
          }"
          type="button"
          @click="
            activeTab = 'general'
          "
        >
          <span class="tab-icon">
            ◉
          </span>

          General
        </button>

        <button
          class="tab-button"
          :class="{
            active:
              activeTab === 'assignments',
          }"
          type="button"
          @click="
            activeTab = 'assignments'
          "
        >
          Asignaciones

          <small>
            {{ assignments.length }}
          </small>
        </button>

        <button
          class="tab-button"
          :class="{
            active:
              activeTab === 'checklists',
          }"
          type="button"
          @click="
            activeTab = 'checklists'
          "
        >
          Checklist

          <small>
            {{ checklists.length }}
          </small>
        </button>

        <button
          class="tab-button"
          :class="{
            active:
              activeTab === 'diagnoses',
          }"
          type="button"
          @click="
            activeTab = 'diagnoses'
          "
        >
          Diagnósticos

          <small>
            {{ diagnoses.length }}
          </small>
        </button>

        <button
          class="tab-button"
          :class="{
            active:
              activeTab === 'components',
          }"
          type="button"
          @click="
            activeTab = 'components'
          "
        >
          Componentes

          <small>
            {{ components.length }}
          </small>
        </button>

        <button
          class="tab-button"
          :class="{
            active:
              activeTab === 'photos',
          }"
          type="button"
          @click="
            activeTab = 'photos'
          "
        >
          Fotografías

          <small>
            {{ photos.length }}
          </small>
        </button>

        <button
          class="tab-button"
          :class="{
            active:
              activeTab === 'tests',
          }"
          type="button"
          @click="
            activeTab = 'tests'
          "
        >
          Pruebas

          <small>
            {{ tests.length }}
          </small>
        </button>

        <button
          class="tab-button"
          :class="{
            active:
              activeTab === 'snmp',
          }"
          type="button"
          @click="
            activeTab = 'snmp'
          "
        >
          SNMP

          <small>
            {{ snmpValidations.length }}
          </small>
        </button>

        <button
          class="tab-button"
          :class="{
            active:
              activeTab === 'history',
          }"
          type="button"
          @click="
            activeTab = 'history'
          "
        >
          Historial

          <small>
            {{ statusHistory.length }}
          </small>
        </button>
      </nav>

      <section
        v-if="activeTab === 'general'"
        class="tab-panel"
      >
        <div class="panel-grid">
          <article class="detail-card">
            <header class="card-heading">
              <h2>
                Problema reportado
              </h2>
            </header>

            <p class="text-content">
              {{
                repair.reported_problem ||
                "Sin problema reportado"
              }}
            </p>
          </article>

          <article class="detail-card">
            <header class="card-heading">
              <h2>
                Observaciones iniciales
              </h2>
            </header>

            <p class="text-content">
              {{
                repair.initial_observations ||
                "Sin observaciones"
              }}
            </p>
          </article>

          <article class="detail-card">
            <header class="card-heading">
              <h2>
                Datos de la reparación
              </h2>
            </header>

            <dl class="detail-list">
              <div>
                <dt>Código</dt>
                <dd>{{ repair.code }}</dd>
              </div>

              <div>
                <dt>Tipo</dt>

                <dd>
                  {{
                    repair.repair_type_name ||
                    getRepairTypeName(
                      repair.repair_type
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>Prioridad</dt>

                <dd>
                  {{
                    repair.priority_name ||
                    getPriorityName(
                      repair.priority
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>Solicitada por</dt>

                <dd>
                  {{
                    repair.requested_by_name ||
                    "Sin registro"
                  }}
                </dd>
              </div>

              <div>
                <dt>Técnico</dt>

                <dd>
                  {{
                    repair.assigned_technician_name ||
                    "Sin técnico"
                  }}
                </dd>
              </div>

              <div>
                <dt>Asignada por</dt>

                <dd>
                  {{
                    repair.assigned_by_name ||
                    "Sin registro"
                  }}
                </dd>
              </div>
            </dl>
          </article>

          <article class="detail-card">
            <header class="card-heading">
              <h2>
                Fechas
              </h2>
            </header>

            <dl class="detail-list">
              <div>
                <dt>Solicitud</dt>

                <dd>
                  {{
                    formatDateTime(
                      repair.requested_at
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>Asignación</dt>

                <dd>
                  {{
                    formatDateTime(
                      repair.assigned_at
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>Inicio revisión</dt>

                <dd>
                  {{
                    formatDateTime(
                      repair.review_started_at
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>Inicio reparación</dt>

                <dd>
                  {{
                    formatDateTime(
                      repair.repair_started_at
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>Inicio pruebas</dt>

                <dd>
                  {{
                    formatDateTime(
                      repair.testing_started_at
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>Finalización</dt>

                <dd>
                  {{
                    formatDateTime(
                      repair.completed_at
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>Entrega</dt>

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

          <article class="detail-card">
            <header class="card-heading">
              <h2>
                Requisitos
              </h2>
            </header>

            <dl class="detail-list">
              <div>
                <dt>Requiere repuestos</dt>

                <dd>
                  {{
                    getBooleanText(
                      repair.requires_parts
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>Servicio externo</dt>

                <dd>
                  {{
                    getBooleanText(
                      repair.requires_external_service
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>Seguimiento</dt>

                <dd>
                  {{
                    getBooleanText(
                      repair.requires_follow_up
                    )
                  }}
                </dd>
              </div>

              <div>
                <dt>
                  Fecha seguimiento
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
            <header class="card-heading">
              <h2>
                Condición final
              </h2>
            </header>

            <span class="final-condition">
              {{
                repair.final_condition_name ||
                getFinalConditionName(
                  repair.final_condition
                )
              }}
            </span>

            <p class="text-content final-text">
              {{
                repair.final_observations ||
                "Sin observaciones finales"
              }}
            </p>
          </article>

          <article
            class="detail-card wide-card"
          >
            <header class="card-heading">
              <h2>
                Trabajo realizado
              </h2>
            </header>

            <p class="text-content">
              {{
                repair.work_summary ||
                "Sin resumen registrado"
              }}
            </p>
          </article>

          <article
            class="detail-card wide-card"
          >
            <header class="card-heading">
              <h2>
                Trabajo pendiente
              </h2>
            </header>

            <p class="text-content">
              {{
                repair.pending_work ||
                "Sin trabajo pendiente"
              }}
            </p>
          </article>

          <article
            class="detail-card wide-card"
          >
            <header class="card-heading">
              <h2>
                Notas de cierre
              </h2>
            </header>

            <p class="text-content">
              {{
                repair.closure_notes ||
                "Sin notas de cierre"
              }}
            </p>
          </article>
        </div>
      </section>

      <section
        v-else
        class="tab-panel"
      >
        <div
          v-if="loadingRelations"
          class="empty-records"
        >
          Cargando registros...
        </div>

        <template
          v-else-if="
            activeTab === 'assignments'
          "
        >
          <div
            v-if="!assignments.length"
            class="empty-records"
          >
            No existen asignaciones.
          </div>

          <div
            v-else
            class="records-list"
          >
            <article
              v-for="item in assignments"
              :key="item.id"
              class="record-card"
            >
              <div class="record-icon">
                👤
              </div>

              <div class="record-content">
                <strong>
                  {{
                    item.technician_name ||
                    item.assigned_technician_name ||
                    "Técnico"
                  }}
                </strong>

                <p>
                  {{
                    item.reason ||
                    item.observations ||
                    "Sin observaciones"
                  }}
                </p>
              </div>

              <span
                class="record-status"
                :class="
                  item.status ||
                  'pending'
                "
              >
                {{
                  getRecordStatusName(
                    item.status
                  )
                }}
              </span>

              <time class="record-date">
                {{
                  formatDateTime(
                    item.assigned_at ||
                    item.created_at
                  )
                }}
              </time>
            </article>
          </div>
        </template>

        <template
          v-else-if="
            activeTab === 'checklists'
          "
        >
          <div
            v-if="!checklists.length"
            class="empty-records"
          >
            No existen checklist.
          </div>

          <div
            v-else
            class="records-list"
          >
            <article
              v-for="item in checklists"
              :key="item.id"
              class="record-card"
            >
              <div class="record-icon">
                ✓
              </div>

              <div class="record-content">
                <strong>
                  {{
                    item.name ||
                    item.code ||
                    "Checklist"
                  }}
                </strong>

                <p>
                  {{
                    item.observations ||
                    "Sin observaciones"
                  }}
                </p>
              </div>

              <span
                class="record-status"
                :class="
                  item.status ||
                  'pending'
                "
              >
                {{
                  getRecordStatusName(
                    item.status
                  )
                }}
              </span>

              <time class="record-date">
                {{
                  formatDateTime(
                    item.completed_at ||
                    item.created_at
                  )
                }}
              </time>
            </article>
          </div>
        </template>

        <template
          v-else-if="
            activeTab === 'diagnoses'
          "
        >
          <div
            v-if="!diagnoses.length"
            class="empty-records"
          >
            No existen diagnósticos.
          </div>

          <div
            v-else
            class="records-list"
          >
            <article
              v-for="item in diagnoses"
              :key="item.id"
              class="record-card"
            >
              <div class="record-icon">
                ⌕
              </div>

              <div class="record-content">
                <strong>
                  {{
                    item.title ||
                    item.diagnosis_type_name ||
                    "Diagnóstico"
                  }}
                </strong>

                <p>
                  {{
                    item.description ||
                    item.diagnosis ||
                    item.observations ||
                    "Sin descripción"
                  }}
                </p>
              </div>

              <span
                class="record-status"
                :class="
                  item.is_confirmed
                    ? 'completed'
                    : 'pending'
                "
              >
                {{
                  item.is_confirmed
                    ? "Confirmado"
                    : "Pendiente"
                }}
              </span>

              <time class="record-date">
                {{
                  formatDateTime(
                    item.diagnosed_at ||
                    item.created_at
                  )
                }}
              </time>
            </article>
          </div>
        </template>

        <template
          v-else-if="
            activeTab === 'components'
          "
        >
          <div
            v-if="!components.length"
            class="empty-records"
          >
            No existen componentes registrados.
          </div>

          <div
            v-else
            class="records-list"
          >
            <article
              v-for="item in components"
              :key="item.id"
              class="record-card"
            >
              <div class="record-icon">
                ⚙
              </div>

              <div class="record-content">
                <strong>
                  {{
                    item.component_name ||
                    item.inventory_name ||
                    "Componente"
                  }}
                </strong>

                <p>
                  {{
                    item.notes ||
                    item.observations ||
                    "Sin observaciones"
                  }}
                </p>
              </div>

              <span
                class="record-status"
                :class="
                  item.status ||
                  'pending'
                "
              >
                {{
                  getRecordStatusName(
                    item.status
                  )
                }}
              </span>

              <time class="record-date">
                {{
                  formatDateTime(
                    item.installed_at ||
                    item.created_at
                  )
                }}
              </time>
            </article>
          </div>
        </template>

        <template
          v-else-if="
            activeTab === 'photos'
          "
        >
          <div
            v-if="!photos.length"
            class="empty-records"
          >
            No existen fotografías.
          </div>

          <div
            v-else
            class="photos-grid"
          >
            <article
              v-for="photo in photos"
              :key="photo.id"
              class="photo-card"
              @click="openPhoto(photo)"
            >
              <img
                v-if="
                  photo.file_url ||
                  photo.image_url ||
                  photo.file ||
                  photo.image
                "
                :src="
                  photo.file_url ||
                  photo.image_url ||
                  photo.file ||
                  photo.image
                "
                :alt="
                  photo.title ||
                  'Fotografía'
                "
              />

              <div
                v-else
                class="photo-placeholder"
              >
                Sin imagen
              </div>

              <footer>
                <strong>
                  {{
                    photo.title ||
                    photo.category_name ||
                    "Fotografía"
                  }}
                </strong>

                <small>
                  {{
                    formatDateTime(
                      photo.taken_at ||
                      photo.created_at
                    )
                  }}
                </small>
              </footer>
            </article>
          </div>
        </template>

        <template
          v-else-if="
            activeTab === 'tests'
          "
        >
          <div
            v-if="!tests.length"
            class="empty-records"
          >
            No existen pruebas.
          </div>

          <div
            v-else
            class="records-list"
          >
            <article
              v-for="item in tests"
              :key="item.id"
              class="record-card test-card"
            >
              <div class="test-icon">
                ✓
              </div>

              <div class="record-content">
                <strong>
                  {{
                    item.name ||
                    item.test_type_name ||
                    "Prueba técnica"
                  }}
                </strong>

                <p>
                  {{
                    item.observations ||
                    item.result_notes ||
                    "Sin observaciones"
                  }}
                </p>
              </div>

              <span
                class="record-status"
                :class="
                  item.result ||
                  item.status ||
                  'pending'
                "
              >
                {{
                  getRecordStatusName(
                    item.result ||
                    item.status
                  )
                }}
              </span>
            </article>
          </div>
        </template>

        <template
          v-else-if="
            activeTab === 'snmp'
          "
        >
          <div
            v-if="!snmpValidations.length"
            class="empty-records"
          >
            No existen validaciones SNMP.
          </div>

          <div
            v-else
            class="records-list"
          >
            <article
              v-for="
                item in snmpValidations
              "
              :key="item.id"
              class="record-card snmp-card"
            >
              <div class="snmp-indicator">
                S
              </div>

              <div class="record-content">
                <strong>
                  {{
                    item.host ||
                    "Validación SNMP"
                  }}
                </strong>

                <p>
                  {{
                    item.error_message ||
                    item.observations ||
                    "Sin observaciones"
                  }}
                </p>
              </div>

              <div class="snmp-matches">
                <span
                  :class="{
                    success:
                      item.serial_matches,
                    danger:
                      item.serial_matches ===
                      false,
                  }"
                >
                  Serie
                </span>

                <span
                  :class="{
                    success:
                      item.brand_matches,
                    danger:
                      item.brand_matches ===
                      false,
                  }"
                >
                  Marca
                </span>

                <span
                  :class="{
                    success:
                      item.model_matches,
                    danger:
                      item.model_matches ===
                      false,
                  }"
                >
                  Modelo
                </span>
              </div>
            </article>
          </div>
        </template>

        <template
          v-else-if="
            activeTab === 'history'
          "
        >
          <div
            v-if="!statusHistory.length"
            class="empty-records"
          >
            No existe historial de estados.
          </div>

          <div
            v-else
            class="timeline"
          >
            <article
              v-for="item in statusHistory"
              :key="item.id"
              class="timeline-item"
            >
              <span
                class="timeline-dot"
                :class="
                  getStatusClass(
                    item.new_status
                  )
                "
              ></span>

              <div class="timeline-content">
                <header class="timeline-heading">
                  <strong>
                    {{
                      getStatusName(
                        item.previous_status
                      )
                    }}
                    →
                    {{
                      getStatusName(
                        item.new_status
                      )
                    }}
                  </strong>

                  <span>
                    {{
                      formatDateTime(
                        item.changed_at ||
                        item.created_at
                      )
                    }}
                  </span>
                </header>

                <p>
                  {{
                    item.reason ||
                    item.observations ||
                    "Sin observaciones"
                  }}
                </p>

                <small>
                  {{
                    item.changed_by_name ||
                    "Sistema"
                  }}
                </small>
              </div>
            </article>
          </div>
        </template>
      </section>
    </template>

    <Teleport to="body">
      <div
        v-if="actionModalOpen"
        class="modal-backdrop"
        @click.self="closeActionModal"
      >
        <section
          class="action-modal"
          role="dialog"
          aria-modal="true"
        >
          <header class="modal-heading">
            <div>
              <h2>
                {{ actionModalTitle }}
              </h2>

              <p>
                {{
                  repair?.code ||
                  "Reparación"
                }}
              </p>
            </div>

            <button
              class="modal-close"
              type="button"
              :disabled="processing"
              @click="closeActionModal"
            >
              ×
            </button>
          </header>

          <div
            v-if="modalError"
            class="detail-message error"
          >
            {{ modalError }}
          </div>

          <label
            v-if="
              actionModalType === 'status'
            "
            class="modal-field"
          >
            <span>
              Nuevo estado
            </span>

            <select
              v-model="selectedStatus"
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

          <template
            v-if="
              actionModalType ===
                'status' &&
              [
                'completed',
                'delivered',
              ].includes(
                selectedStatus
              )
            "
          >
            <label class="modal-field">
              <span>
                Condición final
              </span>

              <select
                v-model="
                  selectedFinalCondition
                "
              >
                <option
                  v-for="
                    option in
                    finalConditionOptions
                  "
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
            </label>

            <label class="modal-field">
              <span>
                Resumen del trabajo
              </span>

              <textarea
                v-model="workSummary"
                rows="4"
              ></textarea>
            </label>

            <label class="modal-field">
              <span>
                Observaciones finales
              </span>

              <textarea
                v-model="
                  finalObservations
                "
                rows="4"
              ></textarea>
            </label>

            <label class="modal-field">
              <span>
                Notas de cierre
              </span>

              <textarea
                v-model="closureNotes"
                rows="4"
              ></textarea>
            </label>
          </template>

          <label class="modal-field">
            <span>
              {{
                actionModalType ===
                'cancel'
                  ? "Motivo de cancelación"
                  : actionModalType ===
                    'reopen'
                    ? "Motivo de reapertura"
                    : actionModalType ===
                      'archive'
                      ? "Motivo de archivado"
                      : "Motivo u observaciones"
              }}
            </span>

            <textarea
              v-model="actionReason"
              rows="4"
              placeholder="Escribe una observación"
            ></textarea>
          </label>

          <footer class="modal-actions">
            <button
              class="secondary-button"
              type="button"
              :disabled="processing"
              @click="closeActionModal"
            >
              Cancelar
            </button>

            <button
              class="primary-button"
              type="button"
              :disabled="processing"
              @click="submitAction"
            >
              {{
                processing
                  ? "Procesando..."
                  : "Confirmar"
              }}
            </button>
          </footer>
        </section>
      </div>
    </Teleport>
  </section>
</template>