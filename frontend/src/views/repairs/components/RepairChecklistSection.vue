<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue"

import {
  completeRepairChecklist,
  createRepairChecklist,
  getRepairChecklist,
  getRepairChecklists,
  loadRepairChecklistCompatibleComponents,
  reopenRepairChecklist,
  reviewRepairChecklistItem,
  startRepairChecklist,
} from "../../../services/repairs.service"

import "./RepairChecklistSection.css"


const props = defineProps({
  repairId: {
    type: String,
    required: true,
  },

  repair: {
    type: Object,
    default: null,
  },
})


const emit = defineEmits([
  "updated",
  "request-photo",
])


const loading = ref(false)
const processing = ref(false)

const errorMessage = ref("")
const successMessage = ref("")

const checklists = ref([])
const expandedChecklistIds = ref([])

const createModalVisible = ref(false)
const startModalVisible = ref(false)
const completeModalVisible = ref(false)
const reopenModalVisible = ref(false)
const reviewModalVisible = ref(false)

const selectedChecklist = ref(null)
const selectedItem = ref(null)

const createForm = reactive({
  name: "Lista principal de revisión",
  description:
    "Revisión técnica general del equipo.",
  is_main_checklist: true,
  observations: "",
})

const actionForm = reactive({
  observations: "",
  reason: "",
})

const reviewForm = reactive({
  status: "",
  observation: "",
  selected_subcomponents: [],
})


const mainChecklist = computed(() => {
  return (
    checklists.value.find(
      (checklist) =>
        checklist.is_main_checklist
    ) || null
  )
})


const hasMainChecklist = computed(() => {
  return Boolean(mainChecklist.value)
})


const totalItems = computed(() => {
  return checklists.value.reduce(
    (total, checklist) => {
      return (
        total +
        getChecklistItems(checklist).length
      )
    },
    0
  )
})


const completedItems = computed(() => {
  return checklists.value.reduce(
    (total, checklist) => {
      const completed =
        getChecklistItems(
          checklist
        ).filter(
          (item) =>
            isCompletedItem(item)
        ).length

      return total + completed
    },
    0
  )
})


const failedItems = computed(() => {
  return checklists.value.reduce(
    (total, checklist) => {
      const failed =
        getChecklistItems(
          checklist
        ).filter(
          (item) =>
            item.status === "failed"
        ).length

      return total + failed
    },
    0
  )
})


const observedItems = computed(() => {
  return checklists.value.reduce(
    (total, checklist) => {
      const observed =
        getChecklistItems(
          checklist
        ).filter(
          (item) =>
            item.status === "observed"
        ).length

      return total + observed
    },
    0
  )
})


const progressPercentage = computed(() => {
  if (!totalItems.value) {
    return 0
  }

  return Math.min(
    Math.round(
      (
        completedItems.value /
        totalItems.value
      ) * 100
    ),
    100
  )
})


const canCreateChecklist = computed(() => {
  return (
    Boolean(props.repairId) &&
    Boolean(props.repair?.is_active) &&
    !props.repair?.is_archived &&
    !hasMainChecklist.value
  )
})


const canLoadCompatibleComponents = computed(() => {
  return (
    Boolean(mainChecklist.value?.id) &&
    mainChecklist.value.status !== "completed" &&
    !mainChecklist.value.is_archived &&
    Boolean(props.repair?.is_active) &&
    !props.repair?.is_archived
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


function getChecklistItems(checklist) {
  return Array.isArray(
    checklist?.items
  )
    ? checklist.items
    : []
}


function getChecklistStatusName(checklist) {
  if (checklist?.status_name) {
    return checklist.status_name
  }

  const names = {
    pending: "Pendiente",
    in_progress: "En proceso",
    completed: "Completada",
  }

  return (
    names[checklist?.status] ||
    "Sin estado"
  )
}


function getChecklistStatusClass(checklist) {
  const classes = {
    pending: "pending",
    in_progress: "in-progress",
    completed: "completed",
  }

  return (
    classes[checklist?.status] ||
    "neutral"
  )
}


function isTechnicalUnit(item) {
  return Boolean(
    item?.is_technical_unit
  )
}


function getItemStatusName(item) {
  if (
    isTechnicalUnit(item) &&
    item?.commercial_status_name
  ) {
    return item.commercial_status_name
  }

  if (item?.status_name) {
    return item.status_name
  }

  const technicalNames = {
    pending: "Pendiente",
    ok: "Nuevo",
    observed: "Desgastado",
    failed: "Requiere cambio",
    not_applicable: "No aplica",
  }

  const generalNames = {
    pending: "Pendiente",
    ok: "Correcto",
    observed: "Observado",
    failed: "Falla",
    not_applicable: "No aplica",
  }

  const names = isTechnicalUnit(item)
    ? technicalNames
    : generalNames

  return (
    names[item?.status] ||
    "Sin estado"
  )
}


function getItemStatusClass(item) {
  const classes = {
    pending: "pending",
    ok: "ok",
    observed: "observed",
    failed: "failed",
    not_applicable:
      "not-applicable",
  }

  return (
    classes[item?.status] ||
    "neutral"
  )
}


function getItemStatusIcon(item) {
  const icons = {
    pending: "○",
    ok: "✓",
    observed: "!",
    failed: "×",
    not_applicable: "—",
  }

  return (
    icons[item?.status] ||
    "○"
  )
}


function getUnitVisualType(item) {
  const text = [
    item?.component_type_name,
    item?.component_name,
    item?.name,
    item?.component_code,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase()

  if (
    text.includes("imagen") ||
    text.includes("drum") ||
    text.includes("tambor") ||
    text.includes("iu")
  ) {
    return "drum"
  }

  if (
    text.includes("fusor") ||
    text.includes("fuser") ||
    text.includes("fusión")
  ) {
    return "fuser"
  }

  if (
    text.includes("itb") ||
    text.includes("transfer") ||
    text.includes("transferencia") ||
    text.includes("banda")
  ) {
    return "itb"
  }

  if (
    text.includes("adf") ||
    text.includes("alimentador") ||
    text.includes("document")
  ) {
    return "adf"
  }

  if (
    text.includes("cassette") ||
    text.includes("casetera") ||
    text.includes("bandeja")
  ) {
    return "cassette"
  }

  if (
    text.includes("developer") ||
    text.includes("revelador")
  ) {
    return "developer"
  }

  if (
    text.includes("toner") ||
    text.includes("tóner")
  ) {
    return "toner"
  }

  if (
    text.includes("scanner") ||
    text.includes("escáner")
  ) {
    return "scanner"
  }

  if (
    text.includes("laser") ||
    text.includes("láser")
  ) {
    return "laser"
  }

  return "generic"
}


function getUnitIconClass(item) {
  const color = String(
    item?.component_color ||
    item?.component_color_name ||
    ""
  ).toLowerCase()

  if (
    color.includes("cyan") ||
    color.includes("cian")
  ) {
    return "cyan"
  }

  if (
    color.includes("magenta")
  ) {
    return "magenta"
  }

  if (
    color.includes("yellow") ||
    color.includes("amarillo")
  ) {
    return "yellow"
  }

  if (
    color.includes("black") ||
    color.includes("negro")
  ) {
    return "black"
  }

  return "neutral"
}


function getCategoryName(item) {
  return (
    item?.category_name ||
    item?.category ||
    "Sin categoría"
  )
}


function isCompletedItem(item) {
  return [
    "ok",
    "observed",
    "not_applicable",
  ].includes(item?.status)
}


function isChecklistExpanded(
  checklistId
) {
  return expandedChecklistIds.value.includes(
    checklistId
  )
}


function toggleChecklist(
  checklistId
) {
  if (
    isChecklistExpanded(
      checklistId
    )
  ) {
    expandedChecklistIds.value =
      expandedChecklistIds.value.filter(
        (id) =>
          id !== checklistId
      )

    return
  }

  expandedChecklistIds.value.push(
    checklistId
  )
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


function showMessage(
  type,
  message
) {
  if (type === "success") {
    successMessage.value = message
    errorMessage.value = ""
  } else {
    errorMessage.value = message
    successMessage.value = ""
  }

  window.setTimeout(
    () => {
      if (
        type === "success" &&
        successMessage.value === message
      ) {
        successMessage.value = ""
      }
    },
    2200
  )
}


async function loadChecklistDetail(
  checklist
) {
  if (!checklist?.id) {
    return checklist
  }

  try {
    return await getRepairChecklist(
      checklist.id
    )
  } catch {
    return checklist
  }
}


async function loadChecklists() {
  loading.value = true
  errorMessage.value = ""

  try {
    const response =
      await getRepairChecklists({
        repair: props.repairId,
        ordering:
          "-is_main_checklist,-created_at",
      })

    const collection =
      normalizeCollection(response)

    const details =
      await Promise.all(
        collection.map(
          (checklist) =>
            loadChecklistDetail(
              checklist
            )
        )
      )

    checklists.value = details

    if (
      details.length &&
      !expandedChecklistIds.value.length
    ) {
      expandedChecklistIds.value =
        details.map(
          (checklist) =>
            checklist.id
        )
    }
  } catch (error) {
    checklists.value = []

    errorMessage.value =
      error.message ||
      "No se pudo cargar el checklist."
  } finally {
    loading.value = false
  }
}


function resetCreateForm() {
  createForm.name =
    "Lista principal de revisión"

  createForm.description =
    "Revisión técnica general del equipo."

  createForm.is_main_checklist =
    !hasMainChecklist.value

  createForm.observations = ""
}


function openCreateModal() {
  resetCreateForm()
  createModalVisible.value = true
}


function closeCreateModal() {
  createModalVisible.value = false
}


async function submitCreateChecklist() {
  if (
    !String(
      createForm.name || ""
    ).trim()
  ) {
    showMessage(
      "error",
      "El nombre del checklist es obligatorio."
    )

    return
  }

  processing.value = true
  errorMessage.value = ""

  try {
    await createRepairChecklist({
      repair: props.repairId,

      name:
        String(
          createForm.name || ""
        ).trim(),

      description:
        String(
          createForm.description ||
          ""
        ).trim(),

      is_main_checklist:
        Boolean(
          createForm
            .is_main_checklist
        ),

      observations:
        String(
          createForm.observations ||
          ""
        ).trim(),
    })

    closeCreateModal()

    showMessage(
      "success",
      "El checklist se creó correctamente."
    )

    await loadChecklists()

    emit("updated")
  } catch (error) {
    showMessage(
      "error",
      error.message
    )
  } finally {
    processing.value = false
  }
}


async function loadCompatibleComponents() {
  if (!mainChecklist.value?.id) {
    showMessage(
      "error",
      "No existe un checklist principal activo."
    )

    return
  }

  processing.value = true
  errorMessage.value = ""

  try {
    const response =
      await loadRepairChecklistCompatibleComponents(
        mainChecklist.value.id
      )

    const createdCount =
      Number(response?.created_count || 0)

    showMessage(
      "success",
      response?.detail ||
      (
        createdCount > 0
          ? `Se agregaron ${createdCount} unidades de la familia.`
          : "No existen unidades nuevas para agregar."
      )
    )

    await loadChecklists()

    emit("updated")
  } catch (error) {
    showMessage(
      "error",
      error.message ||
      "No se pudieron cargar las unidades de la familia."
    )
  } finally {
    processing.value = false
  }
}


function openStartModal(checklist) {
  selectedChecklist.value =
    checklist

  actionForm.observations = ""
  actionForm.reason = ""
  startModalVisible.value = true
}


function closeStartModal() {
  startModalVisible.value = false
  selectedChecklist.value = null
  actionForm.observations = ""
}


async function submitStartChecklist() {
  if (!selectedChecklist.value) {
    return
  }

  processing.value = true
  errorMessage.value = ""

  try {
    await startRepairChecklist(
      selectedChecklist.value.id,
      String(
        actionForm.observations ||
        ""
      ).trim()
    )

    closeStartModal()

    showMessage(
      "success",
      "El checklist se inició correctamente."
    )

    await loadChecklists()

    emit("updated")
  } catch (error) {
    showMessage(
      "error",
      error.message
    )
  } finally {
    processing.value = false
  }
}


function openCompleteModal(
  checklist
) {
  selectedChecklist.value =
    checklist

  actionForm.observations = ""
  actionForm.reason = ""
  completeModalVisible.value = true
}


function closeCompleteModal() {
  completeModalVisible.value = false
  selectedChecklist.value = null
  actionForm.observations = ""
}


async function submitCompleteChecklist() {
  if (!selectedChecklist.value) {
    return
  }

  processing.value = true
  errorMessage.value = ""

  try {
    await completeRepairChecklist(
      selectedChecklist.value.id,
      String(
        actionForm.observations ||
        ""
      ).trim()
    )

    closeCompleteModal()

    showMessage(
      "success",
      "El checklist se completó correctamente."
    )

    await loadChecklists()

    emit("updated")
  } catch (error) {
    showMessage(
      "error",
      error.message
    )
  } finally {
    processing.value = false
  }
}


function openReopenModal(
  checklist
) {
  selectedChecklist.value =
    checklist

  actionForm.reason = ""
  actionForm.observations = ""
  reopenModalVisible.value = true
}


function closeReopenModal() {
  reopenModalVisible.value = false
  selectedChecklist.value = null
  actionForm.reason = ""
}


async function submitReopenChecklist() {
  if (!selectedChecklist.value) {
    return
  }

  const reason = String(
    actionForm.reason || ""
  ).trim()

  if (!reason) {
    showMessage(
      "error",
      "El motivo de reapertura es obligatorio."
    )

    return
  }

  processing.value = true
  errorMessage.value = ""

  try {
    await reopenRepairChecklist(
      selectedChecklist.value.id,
      reason
    )

    closeReopenModal()

    showMessage(
      "success",
      "El checklist se reabrió correctamente."
    )

    await loadChecklists()

    emit("updated")
  } catch (error) {
    showMessage(
      "error",
      error.message
    )
  } finally {
    processing.value = false
  }
}


function openReviewModal(
  item
) {
  selectedItem.value = item

  reviewForm.status =
    item.status === "pending"
      ? ""
      : item.status

  reviewForm.observation =
    item.observation || ""

  reviewForm.selected_subcomponents =
    Array.isArray(
      item.selected_subcomponent_ids
    )
      ? [
          ...item.selected_subcomponent_ids,
        ]
      : []

  reviewModalVisible.value = true
}


function closeReviewModal() {
  reviewModalVisible.value = false
  selectedItem.value = null
  reviewForm.status = ""
  reviewForm.observation = ""
  reviewForm.selected_subcomponents = []
}


function requiresReviewObservation() {
  const item = selectedItem.value
  const status = reviewForm.status

  if (!item || !status) {
    return false
  }

  if (status === "failed") {
    return true
  }

  if (
    status === "not_applicable" &&
    item.is_required
  ) {
    return true
  }

  return (
    item.requires_observation &&
    [
      "observed",
      "failed",
    ].includes(status)
  )
}


function shouldSelectSubcomponents() {
  return (
    isTechnicalUnit(
      selectedItem.value
    ) &&
    reviewForm.status === "failed"
  )
}


function getAvailableSubcomponents(item) {
  return Array.isArray(
    item?.subcomponents
  )
    ? item.subcomponents
    : []
}


function getSelectedSubcomponents(item) {
  return Array.isArray(
    item?.selected_subcomponents
  )
    ? item.selected_subcomponents
    : []
}


function getReviewOptionName(status) {
  if (isTechnicalUnit(selectedItem.value)) {
    const names = {
      ok: "Nuevo",
      observed: "Desgastado",
      failed: "Requiere cambio",
      not_applicable: "No aplica",
    }

    return names[status] || status
  }

  const names = {
    ok: "Correcto",
    observed: "Observado",
    failed: "Falla",
    not_applicable: "No aplica",
  }

  return names[status] || status
}


async function submitItemReview() {
  if (!selectedItem.value) {
    return
  }

  if (!reviewForm.status) {
    showMessage(
      "error",
      "Selecciona el resultado de la revisión."
    )

    return
  }

  const observation = String(
    reviewForm.observation ||
    ""
  ).trim()

  if (
    requiresReviewObservation() &&
    !observation
  ) {
    showMessage(
      "error",
      "Debes registrar una observación."
    )

    return
  }

  if (
    shouldSelectSubcomponents() &&
    !reviewForm
      .selected_subcomponents
      .length
  ) {
    showMessage(
      "error",
      "Selecciona al menos una subparte que requiera cambio."
    )

    return
  }

  processing.value = true
  errorMessage.value = ""

  try {
    await reviewRepairChecklistItem(
      selectedItem.value.id,
      {
        status:
          reviewForm.status,

        observation,

        selected_subcomponents:
          shouldSelectSubcomponents()
            ? [
                ...reviewForm
                  .selected_subcomponents,
              ]
            : [],
      }
    )

    closeReviewModal()

    showMessage(
      "success",
      "El punto fue revisado correctamente."
    )

    await loadChecklists()

    emit("updated")
  } catch (error) {
    showMessage(
      "error",
      error.message
    )
  } finally {
    processing.value = false
  }
}


function requestItemPhoto(item) {
  emit(
    "request-photo",
    {
      checklistItem: item,
      checklistItemId: item.id,
    }
  )
}


function getChecklistProgress(
  checklist
) {
  const items =
    getChecklistItems(checklist)

  if (!items.length) {
    return {
      total: 0,
      completed: 0,
      percentage: 0,
    }
  }

  const completed =
    items.filter(
      (item) =>
        isCompletedItem(item)
    ).length

  return {
    total: items.length,
    completed,

    percentage:
      Math.min(
        Math.round(
          (
            completed /
            items.length
          ) * 100
        ),
        100
      ),
  }
}


function canReviewChecklist(
  checklist
) {
  return (
    checklist.status !==
      "completed" &&
    !checklist.is_archived &&
    props.repair?.is_active
  )
}


function canStartChecklist(
  checklist
) {
  return (
    checklist.status ===
      "pending" &&
    !checklist.is_archived &&
    props.repair?.is_active
  )
}


function canCompleteChecklist(
  checklist
) {
  return (
    checklist.status ===
      "in_progress" &&
    !checklist.is_archived &&
    props.repair?.is_active
  )
}


function canReopenChecklist(
  checklist
) {
  return (
    checklist.status ===
      "completed" &&
    !checklist.is_archived &&
    props.repair?.is_active
  )
}


watch(
  () => props.repairId,
  () => {
    loadChecklists()
  }
)


onMounted(() => {
  loadChecklists()
})
</script>

<template>
  <section class="repair-checklist-section">
    <header class="checklist-section-header">
      <div>
        <span class="section-kicker">
          Control técnico
        </span>

        <h2>
          Checklist de revisión
        </h2>

        <p>
          Registra cada punto revisado,
          observaciones y evidencias.
        </p>
      </div>

      <div class="section-actions">
        <button
          class="checklist-secondary-button"
          type="button"
          :disabled="
            loading ||
            processing
          "
          @click="loadChecklists"
        >
          ↻ Actualizar
        </button>

        <button
          v-if="canLoadCompatibleComponents"
          class="checklist-secondary-button"
          type="button"
          :disabled="
            loading ||
            processing
          "
          @click="loadCompatibleComponents"
        >
          ⤓ Cargar unidades de la familia
        </button>

        <button
          v-if="canCreateChecklist"
          class="checklist-primary-button"
          type="button"
          :disabled="processing"
          @click="openCreateModal"
        >
          ＋ Crear checklist
        </button>
      </div>
    </header>

    <div
      v-if="errorMessage"
      class="checklist-message error"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="successMessage"
      class="checklist-message success"
    >
      {{ successMessage }}
    </div>

    <section class="checklist-summary-grid">
      <article class="checklist-summary-card">
        <span class="summary-icon">
          ▦
        </span>

        <div>
          <small>
            Listas
          </small>

          <strong>
            {{ checklists.length }}
          </strong>
        </div>
      </article>

      <article class="checklist-summary-card">
        <span class="summary-icon">
          ✓
        </span>

        <div>
          <small>
            Revisados
          </small>

          <strong>
            {{ completedItems }}
            /
            {{ totalItems }}
          </strong>
        </div>
      </article>

      <article class="checklist-summary-card warning">
        <span class="summary-icon">
          !
        </span>

        <div>
          <small>
            Observados
          </small>

          <strong>
            {{ observedItems }}
          </strong>
        </div>
      </article>

      <article class="checklist-summary-card danger">
        <span class="summary-icon">
          ×
        </span>

        <div>
          <small>
            Con falla
          </small>

          <strong>
            {{ failedItems }}
          </strong>
        </div>
      </article>
    </section>

    <section class="global-progress-card">
      <div>
        <span>
          Progreso general
        </span>

        <strong>
          {{ progressPercentage }}%
        </strong>
      </div>

      <div class="global-progress-track">
        <span
          :style="{
            width:
              `${progressPercentage}%`,
          }"
        ></span>
      </div>
    </section>

    <div
      v-if="loading"
      class="checklist-loading"
    >
      <span class="checklist-spinner"></span>

      Cargando checklist...
    </div>

    <div
      v-else-if="
        !checklists.length
      "
      class="checklist-empty-state"
    >
      <span class="empty-checklist-icon">
        ✓
      </span>

      <strong>
        Aún no existe un checklist
      </strong>

      <p>
        Crea la lista principal para generar
        automáticamente los puntos generales
        y componentes compatibles.
      </p>

      <button
        v-if="canCreateChecklist"
        class="checklist-primary-button"
        type="button"
        @click="openCreateModal"
      >
        Crear checklist principal
      </button>
    </div>

    <div
      v-else
      class="checklist-list"
    >
      <article
        v-for="checklist in checklists"
        :key="checklist.id"
        class="checklist-card"
      >
        <header class="checklist-card-header">
          <button
            class="checklist-expand-button"
            type="button"
            @click="
              toggleChecklist(
                checklist.id
              )
            "
          >
            <span
              class="expand-arrow"
              :class="{
                expanded:
                  isChecklistExpanded(
                    checklist.id
                  ),
              }"
            >
              ›
            </span>

            <span class="checklist-card-icon">
              ✓
            </span>

            <span class="checklist-heading-content">
              <span class="checklist-title-line">
                <strong>
                  {{ checklist.name }}
                </strong>

                <small
                  v-if="
                    checklist.is_main_checklist
                  "
                  class="main-checklist-badge"
                >
                  Principal
                </small>
              </span>

              <small>
                {{
                  checklist.description ||
                  "Sin descripción"
                }}
              </small>
            </span>
          </button>

          <div class="checklist-card-status">
            <span
              class="checklist-status-badge"
              :class="
                getChecklistStatusClass(
                  checklist
                )
              "
            >
              {{
                getChecklistStatusName(
                  checklist
                )
              }}
            </span>

            <span class="checklist-count">
              {{
                getChecklistProgress(
                  checklist
                ).completed
              }}
              /
              {{
                getChecklistProgress(
                  checklist
                ).total
              }}
            </span>
          </div>

          <div class="checklist-card-actions">
            <button
              v-if="
                checklist.is_main_checklist &&
                canLoadCompatibleComponents
              "
              class="small-action-button primary"
              type="button"
              :disabled="processing"
              @click="
                loadCompatibleComponents
              "
            >
              Cargar unidades
            </button>

            <button
              v-if="
                canStartChecklist(
                  checklist
                )
              "
              class="small-action-button primary"
              type="button"
              :disabled="processing"
              @click="
                openStartModal(
                  checklist
                )
              "
            >
              Iniciar
            </button>

            <button
              v-if="
                canCompleteChecklist(
                  checklist
                )
              "
              class="small-action-button success"
              type="button"
              :disabled="processing"
              @click="
                openCompleteModal(
                  checklist
                )
              "
            >
              Completar
            </button>

            <button
              v-if="
                canReopenChecklist(
                  checklist
                )
              "
              class="small-action-button warning"
              type="button"
              :disabled="processing"
              @click="
                openReopenModal(
                  checklist
                )
              "
            >
              Reabrir
            </button>
          </div>
        </header>

        <div class="checklist-progress">
          <span
            :style="{
              width:
                `${
                  getChecklistProgress(
                    checklist
                  ).percentage
                }%`,
            }"
          ></span>
        </div>

        <div
          v-if="
            isChecklistExpanded(
              checklist.id
            )
          "
          class="checklist-card-body"
        >
          <div class="checklist-metadata">
            <span>
              <strong>
                Iniciada:
              </strong>

              {{
                formatDateTime(
                  checklist.started_at
                )
              }}
            </span>

            <span>
              <strong>
                Por:
              </strong>

              {{
                checklist.started_by_name ||
                "Sin registro"
              }}
            </span>

            <span>
              <strong>
                Finalizada:
              </strong>

              {{
                formatDateTime(
                  checklist.completed_at
                )
              }}
            </span>
          </div>

          <div
            v-if="
              checklist.observations
            "
            class="checklist-observations"
          >
            <strong>
              Observaciones generales
            </strong>

            <p>
              {{ checklist.observations }}
            </p>
          </div>

          <div
            v-if="
              !getChecklistItems(
                checklist
              ).length
            "
            class="items-empty-state"
          >
            Esta lista no tiene puntos de revisión.
          </div>

          <div
            v-else
            class="checklist-items-list"
          >
            <article
              v-for="
                item
                in getChecklistItems(
                  checklist
                )
              "
              :key="item.id"
              class="checklist-item-card"
              :class="[
                getItemStatusClass(
                  item
                ),
                {
                  'technical-unit-card':
                    isTechnicalUnit(item),
                },
              ]"
            >
              <div
                v-if="
                  isTechnicalUnit(item) &&
                  item.component_image
                "
                class="component-catalog-image"
                :class="
                  getUnitIconClass(
                    item
                  )
                "
              >
                <img
                  :src="item.component_image"
                  :alt="item.component_name || item.name"
                />
              </div>

              <div
                v-else-if="
                  isTechnicalUnit(item)
                "
                class="component-fallback-icon"
                :class="[
                  getUnitIconClass(
                    item
                  ),
                  `unit-${getUnitVisualType(item)}`,
                ]"
                aria-hidden="true"
              >
                <svg
                  v-if="
                    getUnitVisualType(item) === 'drum'
                  "
                  viewBox="0 0 120 80"
                  class="unit-illustration"
                >
                  <rect
                    x="24"
                    y="27"
                    width="72"
                    height="26"
                    rx="13"
                    class="unit-main-fill"
                  />
                  <circle
                    cx="24"
                    cy="40"
                    r="15"
                    class="unit-dark-fill"
                  />
                  <circle
                    cx="24"
                    cy="40"
                    r="7"
                    class="unit-light-fill"
                  />
                  <rect
                    x="91"
                    y="32"
                    width="15"
                    height="16"
                    rx="4"
                    class="unit-dark-fill"
                  />
                  <path
                    d="M10 40h28M24 26v28"
                    class="unit-line"
                  />
                </svg>

                <svg
                  v-else-if="
                    getUnitVisualType(item) === 'fuser'
                  "
                  viewBox="0 0 120 80"
                  class="unit-illustration"
                >
                  <rect
                    x="14"
                    y="22"
                    width="92"
                    height="36"
                    rx="10"
                    class="unit-soft-fill"
                  />
                  <rect
                    x="26"
                    y="29"
                    width="68"
                    height="10"
                    rx="5"
                    class="unit-main-fill"
                  />
                  <rect
                    x="26"
                    y="43"
                    width="68"
                    height="9"
                    rx="4.5"
                    class="unit-dark-fill"
                  />
                  <circle
                    cx="18"
                    cy="40"
                    r="7"
                    class="unit-dark-fill"
                  />
                  <circle
                    cx="102"
                    cy="40"
                    r="7"
                    class="unit-dark-fill"
                  />
                </svg>

                <svg
                  v-else-if="
                    getUnitVisualType(item) === 'itb'
                  "
                  viewBox="0 0 120 80"
                  class="unit-illustration"
                >
                  <path
                    d="M20 26h80l10 28H10z"
                    class="unit-soft-fill"
                  />
                  <path
                    d="M28 32h64l7 16H21z"
                    class="unit-main-fill"
                  />
                  <circle
                    cx="24"
                    cy="54"
                    r="8"
                    class="unit-dark-fill"
                  />
                  <circle
                    cx="96"
                    cy="54"
                    r="8"
                    class="unit-dark-fill"
                  />
                </svg>

                <svg
                  v-else-if="
                    getUnitVisualType(item) === 'adf'
                  "
                  viewBox="0 0 120 80"
                  class="unit-illustration"
                >
                  <path
                    d="M20 24h65l15 13H35z"
                    class="unit-main-fill"
                  />
                  <rect
                    x="30"
                    y="37"
                    width="70"
                    height="23"
                    rx="6"
                    class="unit-soft-fill"
                  />
                  <rect
                    x="41"
                    y="42"
                    width="48"
                    height="6"
                    rx="3"
                    class="unit-dark-fill"
                  />
                  <path
                    d="M35 24l8-8h38l8 8"
                    class="unit-line"
                  />
                </svg>

                <svg
                  v-else-if="
                    getUnitVisualType(item) === 'cassette'
                  "
                  viewBox="0 0 120 80"
                  class="unit-illustration"
                >
                  <rect
                    x="18"
                    y="19"
                    width="84"
                    height="43"
                    rx="7"
                    class="unit-soft-fill"
                  />
                  <rect
                    x="27"
                    y="27"
                    width="66"
                    height="23"
                    rx="4"
                    class="unit-light-fill"
                  />
                  <rect
                    x="48"
                    y="54"
                    width="24"
                    height="5"
                    rx="2.5"
                    class="unit-dark-fill"
                  />
                  <path
                    d="M35 34h50"
                    class="unit-line"
                  />
                </svg>

                <svg
                  v-else
                  viewBox="0 0 120 80"
                  class="unit-illustration"
                >
                  <circle
                    cx="60"
                    cy="40"
                    r="23"
                    class="unit-soft-fill"
                  />
                  <circle
                    cx="60"
                    cy="40"
                    r="12"
                    class="unit-main-fill"
                  />
                  <path
                    d="M60 10v10M60 60v10M30 40H20M100 40H90M39 19l7 7M81 54l7 7M81 26l7-7M39 61l7-7"
                    class="unit-line"
                  />
                </svg>

                <span class="unit-visual-label">
                  {{
                    item.component_type_name ||
                    item.component_name ||
                    "Unidad técnica"
                  }}
                </span>
              </div>

              <div
                v-else
                class="item-status-icon"
                :class="
                  getItemStatusClass(
                    item
                  )
                "
              >
                {{
                  getItemStatusIcon(
                    item
                  )
                }}
              </div>

              <div class="item-main-content">
                <div class="item-heading">
                  <div>
                    <strong>
                      {{ item.name }}
                    </strong>

                    <small>
                      {{ item.code }}
                      ·
                      {{
                        getCategoryName(
                          item
                        )
                      }}
                    </small>
                  </div>

                  <span
                    class="item-status-badge"
                    :class="
                      getItemStatusClass(
                        item
                      )
                    "
                  >
                    {{
                      getItemStatusName(
                        item
                      )
                    }}
                  </span>
                </div>

                <p
                  v-if="item.description"
                  class="item-description"
                >
                  {{ item.description }}
                </p>

                <div
                  v-if="item.instructions"
                  class="item-instructions"
                >
                  <strong>
                    Instrucciones:
                  </strong>

                  {{ item.instructions }}
                </div>

                <div class="item-requirements">
                  <span
                    v-if="
                      item.is_required
                    "
                    class="requirement-badge required"
                  >
                    Obligatorio
                  </span>

                  <span
                    v-if="
                      item.requires_photo
                    "
                    class="requirement-badge photo"
                  >
                    Requiere foto
                  </span>

                  <span
                    v-if="
                      item.requires_observation
                    "
                    class="requirement-badge observation"
                  >
                    Requiere observación
                  </span>

                  <span
                    v-if="
                      item.component_name
                    "
                    class="requirement-badge component"
                  >
                    {{
                      item.component_name
                    }}
                  </span>
                </div>

                <div
                  v-if="item.observation"
                  class="item-observation"
                >
                  <strong>
                    Observación:
                  </strong>

                  <p>
                    {{ item.observation }}
                  </p>
                </div>

                <div
                  v-if="
                    item.status === 'failed' &&
                    getSelectedSubcomponents(
                      item
                    ).length
                  "
                  class="selected-subcomponents"
                >
                  <strong>
                    Subpartes que requieren cambio
                  </strong>

                  <div class="selected-subcomponents-list">
                    <span
                      v-for="
                        subcomponent
                        in getSelectedSubcomponents(
                          item
                        )
                      "
                      :key="subcomponent.id"
                      class="selected-subcomponent-badge"
                    >
                      {{
                        subcomponent.name
                      }}
                    </span>
                  </div>
                </div>

                <div
                  v-if="item.checked_at"
                  class="item-review-metadata"
                >
                  Revisado por
                  <strong>
                    {{
                      item.checked_by_name ||
                      "Usuario"
                    }}
                  </strong>

                  el
                  {{
                    formatDateTime(
                      item.checked_at
                    )
                  }}
                </div>
              </div>

              <div class="item-actions">
                <button
                  v-if="
                    canReviewChecklist(
                      checklist
                    )
                  "
                  class="item-action-button review"
                  type="button"
                  :disabled="processing"
                  @click="
                    openReviewModal(
                      item
                    )
                  "
                >
                  {{
                    item.status ===
                      "pending"
                      ? "Revisar"
                      : "Cambiar resultado"
                  }}
                </button>

                <button
                  v-if="
                    item.requires_photo
                  "
                  class="item-action-button photo"
                  type="button"
                  :disabled="processing"
                  @click="
                    requestItemPhoto(
                      item
                    )
                  "
                >
                  Subir evidencia
                </button>
              </div>
            </article>
          </div>
        </div>
      </article>
    </div>

    <!-- CREAR CHECKLIST -->
    <div
      v-if="createModalVisible"
      class="checklist-modal-backdrop"
      @click.self="closeCreateModal"
    >
      <form
        class="checklist-modal"
        @submit.prevent="
          submitCreateChecklist
        "
      >
        <header class="modal-header">
          <div>
            <h3>
              Crear checklist
            </h3>

            <p>
              Se generarán los puntos generales
              y componentes compatibles.
            </p>
          </div>

          <button
            type="button"
            class="modal-close-button"
            @click="closeCreateModal"
          >
            ×
          </button>
        </header>

        <label class="modal-field">
          <span>
            Nombre
            <strong>*</strong>
          </span>

          <input
            v-model="createForm.name"
            type="text"
            maxlength="200"
            required
          />
        </label>

        <label class="modal-field">
          <span>
            Descripción
          </span>

          <textarea
            v-model="
              createForm.description
            "
            rows="3"
          ></textarea>
        </label>

        <label class="check-option">
          <input
            v-model="
              createForm.is_main_checklist
            "
            type="checkbox"
            :disabled="hasMainChecklist"
          />

          <span></span>

          <div>
            <strong>
              Checklist principal
            </strong>

            <small>
              Solo puede existir uno activo
              por reparación.
            </small>
          </div>
        </label>

        <label class="modal-field">
          <span>
            Observaciones
          </span>

          <textarea
            v-model="
              createForm.observations
            "
            rows="4"
          ></textarea>
        </label>

        <footer class="modal-actions">
          <button
            class="checklist-secondary-button"
            type="button"
            @click="closeCreateModal"
          >
            Cancelar
          </button>

          <button
            class="checklist-primary-button"
            type="submit"
            :disabled="processing"
          >
            {{
              processing
                ? "Creando..."
                : "Crear checklist"
            }}
          </button>
        </footer>
      </form>
    </div>

    <!-- INICIAR -->
    <div
      v-if="startModalVisible"
      class="checklist-modal-backdrop"
      @click.self="closeStartModal"
    >
      <form
        class="checklist-modal"
        @submit.prevent="
          submitStartChecklist
        "
      >
        <header class="modal-header">
          <div>
            <h3>
              Iniciar checklist
            </h3>

            <p>
              {{
                selectedChecklist?.name
              }}
            </p>
          </div>

          <button
            type="button"
            class="modal-close-button"
            @click="closeStartModal"
          >
            ×
          </button>
        </header>

        <label class="modal-field">
          <span>
            Observaciones iniciales
          </span>

          <textarea
            v-model="
              actionForm.observations
            "
            rows="5"
            placeholder="Estado inicial o indicaciones para la revisión"
          ></textarea>
        </label>

        <footer class="modal-actions">
          <button
            class="checklist-secondary-button"
            type="button"
            @click="closeStartModal"
          >
            Cancelar
          </button>

          <button
            class="checklist-primary-button"
            type="submit"
            :disabled="processing"
          >
            Iniciar revisión
          </button>
        </footer>
      </form>
    </div>

    <!-- COMPLETAR -->
    <div
      v-if="completeModalVisible"
      class="checklist-modal-backdrop"
      @click.self="
        closeCompleteModal
      "
    >
      <form
        class="checklist-modal"
        @submit.prevent="
          submitCompleteChecklist
        "
      >
        <header class="modal-header">
          <div>
            <h3>
              Completar checklist
            </h3>

            <p>
              Se validarán puntos obligatorios,
              fallas y fotografías.
            </p>
          </div>

          <button
            type="button"
            class="modal-close-button"
            @click="
              closeCompleteModal
            "
          >
            ×
          </button>
        </header>

        <div class="completion-warning">
          <strong>
            Antes de continuar
          </strong>

          <span>
            Los puntos obligatorios deben estar
            correctos o justificados como no aplicables.
            Los puntos con fotografía obligatoria
            deben tener una evidencia cargada.
          </span>
        </div>

        <label class="modal-field">
          <span>
            Observaciones finales
          </span>

          <textarea
            v-model="
              actionForm.observations
            "
            rows="5"
          ></textarea>
        </label>

        <footer class="modal-actions">
          <button
            class="checklist-secondary-button"
            type="button"
            @click="
              closeCompleteModal
            "
          >
            Cancelar
          </button>

          <button
            class="checklist-success-button"
            type="submit"
            :disabled="processing"
          >
            Completar checklist
          </button>
        </footer>
      </form>
    </div>

    <!-- REABRIR -->
    <div
      v-if="reopenModalVisible"
      class="checklist-modal-backdrop"
      @click.self="
        closeReopenModal
      "
    >
      <form
        class="checklist-modal"
        @submit.prevent="
          submitReopenChecklist
        "
      >
        <header class="modal-header">
          <div>
            <h3>
              Reabrir checklist
            </h3>

            <p>
              El motivo quedará registrado.
            </p>
          </div>

          <button
            type="button"
            class="modal-close-button"
            @click="
              closeReopenModal
            "
          >
            ×
          </button>
        </header>

        <label class="modal-field">
          <span>
            Motivo
            <strong>*</strong>
          </span>

          <textarea
            v-model="
              actionForm.reason
            "
            rows="5"
            required
          ></textarea>
        </label>

        <footer class="modal-actions">
          <button
            class="checklist-secondary-button"
            type="button"
            @click="
              closeReopenModal
            "
          >
            Cancelar
          </button>

          <button
            class="checklist-warning-button"
            type="submit"
            :disabled="processing"
          >
            Reabrir checklist
          </button>
        </footer>
      </form>
    </div>

    <!-- REVISAR PUNTO -->
    <div
      v-if="reviewModalVisible"
      class="checklist-modal-backdrop"
      @click.self="
        closeReviewModal
      "
    >
      <form
        class="checklist-modal review-modal"
        @submit.prevent="
          submitItemReview
        "
      >
        <header class="modal-header">
          <div>
            <h3>
              Revisar punto
            </h3>

            <p>
              {{
                selectedItem?.name
              }}
            </p>
          </div>

          <button
            type="button"
            class="modal-close-button"
            @click="
              closeReviewModal
            "
          >
            ×
          </button>
        </header>

        <div
          v-if="
            selectedItem?.instructions
          "
          class="review-instructions"
        >
          <strong>
            Instrucciones
          </strong>

          <p>
            {{
              selectedItem.instructions
            }}
          </p>
        </div>

        <div class="review-status-options">
          <label class="review-option ok">
            <input
              v-model="
                reviewForm.status
              "
              type="radio"
              value="ok"
            />

            <span class="review-option-icon">
              ✓
            </span>

            <strong>
              {{
                getReviewOptionName(
                  "ok"
                )
              }}
            </strong>
          </label>

          <label class="review-option observed">
            <input
              v-model="
                reviewForm.status
              "
              type="radio"
              value="observed"
            />

            <span class="review-option-icon">
              !
            </span>

            <strong>
              {{
                getReviewOptionName(
                  "observed"
                )
              }}
            </strong>
          </label>

          <label class="review-option failed">
            <input
              v-model="
                reviewForm.status
              "
              type="radio"
              value="failed"
            />

            <span class="review-option-icon">
              ×
            </span>

            <strong>
              {{
                getReviewOptionName(
                  "failed"
                )
              }}
            </strong>
          </label>

          <label class="review-option not-applicable">
            <input
              v-model="
                reviewForm.status
              "
              type="radio"
              value="not_applicable"
            />

            <span class="review-option-icon">
              —
            </span>

            <strong>
              {{
                getReviewOptionName(
                  "not_applicable"
                )
              }}
            </strong>
          </label>
        </div>

        <div
          v-if="shouldSelectSubcomponents()"
          class="subcomponent-selector"
        >
          <div class="subcomponent-selector-header">
            <strong>
              Subpartes que requieren cambio
            </strong>

            <small>
              Selecciona solo las piezas afectadas.
            </small>
          </div>

          <div
            v-if="
              !getAvailableSubcomponents(
                selectedItem
              ).length
            "
            class="subcomponent-empty"
          >
            Esta unidad no tiene subpartes configuradas.
          </div>

          <div
            v-else
            class="subcomponent-options"
          >
            <label
              v-for="
                subcomponent
                in getAvailableSubcomponents(
                  selectedItem
                )
              "
              :key="subcomponent.id"
              class="subcomponent-option"
            >
              <input
                v-model="
                  reviewForm.selected_subcomponents
                "
                type="checkbox"
                :value="String(subcomponent.id)"
              />

              <span class="subcomponent-option-content">
                <strong>
                  {{ subcomponent.name }}
                </strong>

                <small>
                  {{
                    subcomponent.code ||
                    subcomponent.component_type_name
                  }}
                </small>
              </span>
            </label>
          </div>
        </div>

        <label class="modal-field">
          <span>
            Observación
            <strong
              v-if="
                requiresReviewObservation()
              "
            >
              *
            </strong>
          </span>

          <textarea
            v-model="
              reviewForm.observation
            "
            rows="5"
            :required="
              requiresReviewObservation()
            "
            placeholder="Describe la condición encontrada"
          ></textarea>
        </label>

        <div
          v-if="
            selectedItem?.requires_photo
          "
          class="photo-requirement-warning"
        >
          Este punto requiere una fotografía
          antes de completar el checklist.
        </div>

        <footer class="modal-actions">
          <button
            class="checklist-secondary-button"
            type="button"
            @click="
              closeReviewModal
            "
          >
            Cancelar
          </button>

          <button
            class="checklist-primary-button"
            type="submit"
            :disabled="processing"
          >
            Guardar resultado
          </button>
        </footer>
      </form>
    </div>
  </section>
</template>