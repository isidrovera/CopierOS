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
  consumable_present: null,
  consumable_level_percent: null,
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
    isCatalogVisualItem(item) &&
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

  const names = isCatalogVisualItem(item)
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
  const category = String(
    item?.component_category ||
    item?.component_category_name ||
    ""
  ).toLowerCase()

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
    text.includes("tacho residual") ||
    text.includes("depósito residual") ||
    text.includes("deposito residual") ||
    text.includes("waste toner") ||
    text.includes("waste container") ||
    text.includes("residual toner")
  ) {
    return "waste_toner"
  }

  if (
    item?.is_primary_consumable === true ||
    item?.is_consumable === true ||
    category === "toner" ||
    category.includes("tóner") ||
    category.includes("toner")
  ) {
    return "toner"
  }

  const fallbackText = [
    item?.component_type_name,
    item?.component_name,
    item?.name,
    item?.component_code,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase()

  if (
    fallbackText.includes("toner") ||
    fallbackText.includes("tóner") ||
    fallbackText.includes("cartucho") ||
    fallbackText.includes("botella")
  ) {
    return "toner"
  }

  if (
    fallbackText.includes("tinta") ||
    fallbackText.includes("ink")
  ) {
    return "ink"
  }

  if (
    fallbackText.includes("duplex") ||
    fallbackText.includes("dúplex")
  ) {
    return "duplex"
  }

  if (
    fallbackText.includes("imagen") ||
    fallbackText.includes("drum") ||
    fallbackText.includes("tambor") ||
    fallbackText.includes("iu")
  ) {
    return "drum"
  }

  if (
    fallbackText.includes("fusor") ||
    fallbackText.includes("fuser") ||
    fallbackText.includes("fusión")
  ) {
    return "fuser"
  }

  if (
    fallbackText.includes("itb") ||
    fallbackText.includes("transfer belt") ||
    fallbackText.includes("transferencia") ||
    fallbackText.includes("banda")
  ) {
    return "itb"
  }

  if (
    fallbackText.includes("adf") ||
    fallbackText.includes("alimentador") ||
    fallbackText.includes("documentos")
  ) {
    return "adf"
  }

  if (
    fallbackText.includes("casetera") ||
    fallbackText.includes("cassette") ||
    fallbackText.includes("bandeja")
  ) {
    return "cassette"
  }

  if (
    fallbackText.includes("revelado") ||
    fallbackText.includes("developer") ||
    fallbackText.includes("revelador")
  ) {
    return "developer"
  }

  if (
    fallbackText.includes("alimentación de papel") ||
    fallbackText.includes("paper feed")
  ) {
    return "paper_feed"
  }

  return "generic"
}


function isConsumableUnit(item) {
  if (
    item?.is_primary_consumable === true
  ) {
    return true
  }

  return [
    "toner",
    "ink",
    "waste_toner",
  ].includes(
    getUnitVisualType(item)
  )
}


function isCatalogVisualItem(item) {
  return (
    isTechnicalUnit(item) ||
    isConsumableUnit(item)
  )
}


function getConsumablePresent(item) {
  if (
    item?.consumable_present === false ||
    item?.has_container === false ||
    item?.has_bottle === false
  ) {
    return false
  }

  if (
    item?.consumable_status === "missing" ||
    item?.consumable_status === "no_bottle"
  ) {
    return false
  }

  return true
}


function getConsumableLevel(item) {
  const rawValue = (
    item?.consumable_level_percent ??
    item?.toner_level_percent ??
    item?.ink_level_percent ??
    item?.level_percent ??
    item?.level ??
    0
  )

  const numericValue = Number(
    rawValue
  )

  if (!Number.isFinite(numericValue)) {
    return 0
  }

  return Math.min(
    100,
    Math.max(
      0,
      Math.round(numericValue)
    )
  )
}


function getConsumableLevelLabel(item) {
  if (!getConsumablePresent(item)) {
    return "Sin botella"
  }

  const level = getConsumableLevel(item)

  if (level === 100) {
    return "Lleno"
  }

  if (level === 0) {
    return "Vacío"
  }

  if (level <= 10) {
    return "Nivel bajo"
  }

  if (level <= 50) {
    return "Nivel medio"
  }

  return "Nivel alto"
}


function getConsumableFillHeight(item) {
  if (!getConsumablePresent(item)) {
    return 0
  }

  return Math.round(
    getConsumableLevel(item) * 0.42
  )
}


function getConsumableFillY(item) {
  return (
    64 -
    getConsumableFillHeight(item)
  )
}


function getConsumableCardClass(item) {
  if (!getConsumablePresent(item)) {
    return "missing"
  }

  const level = getConsumableLevel(item)

  if (level === 0) {
    return "empty"
  }

  if (level <= 10) {
    return "low"
  }

  if (level < 100) {
    return "partial"
  }

  return "full"
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


function getColorDisplayName(item) {
  const color = getUnitIconClass(item)

  const names = {
    cyan: "Cyan",
    magenta: "Magenta",
    yellow: "Yellow",
    black: "Black",
  }

  return names[color] || ""
}


function getDisplayItemName(item) {
  const baseName = String(
    item?.name ||
    item?.component_name ||
    "Componente"
  ).trim()

  const visualType = getUnitVisualType(item)

  if (visualType === "waste_toner") {
    return baseName
  }

  if (
    ["toner", "ink"].includes(
      visualType
    )
  ) {
    const colorName =
      getColorDisplayName(item)

    if (
      colorName &&
      !baseName
        .toLowerCase()
        .includes(
          colorName.toLowerCase()
        )
    ) {
      return `${baseName} ${colorName}`
    }
  }

  return baseName
}


function getItemGroupKey(item) {
  const visualType =
    getUnitVisualType(item)

  if (visualType === "waste_toner") {
    return "waste"
  }

  if (
    ["toner", "ink"].includes(
      visualType
    )
  ) {
    return "toner"
  }

  if (isConsumableUnit(item)) {
    return "consumables"
  }

  if (item?.is_accessory) {
    return "accessories"
  }

  if (isTechnicalUnit(item)) {
    return "technical_units"
  }

  return "general"
}


function getGroupName(key) {
  const names = {
    toner: "Tóner y tinta",
    waste: "Depósitos residuales",
    consumables: "Consumibles",
    technical_units: "Unidades técnicas",
    accessories: "Accesorios",
    general: "Revisión general",
  }

  return names[key] || "Otros"
}


function getGroupDescription(key) {
  const descriptions = {
    toner:
      "Cartuchos y botellas con control de nivel.",
    waste:
      "Tachos y depósitos para residuos de tóner.",
    consumables:
      "Consumibles principales del equipo.",
    technical_units:
      "Unidades completas evaluadas para venta.",
    accessories:
      "Accesorios instalados o compatibles.",
    general:
      "Puntos generales de inspección técnica.",
  }

  return descriptions[key] || ""
}


function getGroupIcon(key) {
  const icons = {
    toner: "◉",
    waste: "▣",
    consumables: "◆",
    technical_units: "▤",
    accessories: "⌁",
    general: "✓",
  }

  return icons[key] || "•"
}


function groupChecklistItems(checklist) {
  const order = [
    "general",
    "technical_units",
    "toner",
    "waste",
    "consumables",
    "accessories",
  ]

  const grouped = new Map()

  getChecklistItems(checklist).forEach(
    (item) => {
      const key = getItemGroupKey(item)

      if (!grouped.has(key)) {
        grouped.set(key, [])
      }

      grouped.get(key).push(item)
    }
  )

  return order
    .filter((key) => grouped.has(key))
    .map((key) => ({
      key,
      name: getGroupName(key),
      description:
        getGroupDescription(key),
      icon: getGroupIcon(key),
      items: grouped.get(key),
    }))
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

  reviewForm.consumable_present =
    isConsumableUnit(item)
      ? (
          item.consumable_present ??
          null
        )
      : null

  reviewForm.consumable_level_percent =
    isConsumableUnit(item) &&
    item.consumable_level_percent !== undefined &&
    item.consumable_level_percent !== null
      ? Number(
          item.consumable_level_percent
        )
      : null

  reviewModalVisible.value = true
}


function closeReviewModal() {
  reviewModalVisible.value = false
  selectedItem.value = null
  reviewForm.status = ""
  reviewForm.observation = ""
  reviewForm.selected_subcomponents = []
  reviewForm.consumable_present = null
  reviewForm.consumable_level_percent = null
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
    !isConsumableUnit(
      selectedItem.value
    ) &&
    reviewForm.status === "failed"
  )
}


function isReviewingConsumable() {
  return isConsumableUnit(
    selectedItem.value
  )
}


function getReviewConsumableLevelLabel() {
  if (
    reviewForm.consumable_present === false
  ) {
    return "Sin botella"
  }

  const level = Number(
    reviewForm.consumable_level_percent
  )

  if (!Number.isFinite(level)) {
    return "Sin registrar"
  }

  if (level === 0) {
    return "Vacío"
  }

  if (level === 100) {
    return "Lleno"
  }

  if (level <= 10) {
    return "Nivel bajo"
  }

  if (level <= 50) {
    return "Nivel medio"
  }

  return "Nivel alto"
}


function selectConsumablePresence(value) {
  reviewForm.consumable_present = value

  if (value === false) {
    reviewForm.consumable_level_percent = null
  }

  if (
    value === true &&
    reviewForm.consumable_level_percent === null
  ) {
    reviewForm.consumable_level_percent = 100
  }
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
  if (isCatalogVisualItem(selectedItem.value)) {
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

  if (
    isReviewingConsumable() &&
    reviewForm.consumable_present === null
  ) {
    showMessage(
      "error",
      "Indica si la botella o cartucho está instalado."
    )

    return
  }

  if (
    isReviewingConsumable() &&
    reviewForm.consumable_present === true
  ) {
    const level = Number(
      reviewForm.consumable_level_percent
    )

    if (
      !Number.isFinite(level) ||
      level < 0 ||
      level > 100
    ) {
      showMessage(
        "error",
        "El nivel del consumible debe estar entre 0 y 100."
      )

      return
    }
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

        consumable_present:
          isReviewingConsumable()
            ? reviewForm
                .consumable_present
            : null,

        consumable_level_percent:
          isReviewingConsumable() &&
          reviewForm
            .consumable_present === true
            ? Number(
                reviewForm
                  .consumable_level_percent
              )
            : null,
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
            class="checklist-groups"
          >
            <section
              v-for="
                group
                in groupChecklistItems(
                  checklist
                )
              "
              :key="group.key"
              class="checklist-group"
              :class="`group-${group.key}`"
            >
              <header class="checklist-group-header">
                <span class="checklist-group-icon">
                  {{ group.icon }}
                </span>

                <div>
                  <strong>
                    {{ group.name }}
                  </strong>

                  <small>
                    {{ group.description }}
                  </small>
                </div>

                <span class="checklist-group-count">
                  {{ group.items.length }}
                </span>
              </header>

              <div class="checklist-items-list">
                <article
                  v-for="item in group.items"
                  :key="item.id"
                  class="checklist-item-card"
              :class="[
                getItemStatusClass(
                  item
                ),
                {
                  'technical-unit-card':
                    isCatalogVisualItem(item),
                  'consumable-unit-card':
                    isConsumableUnit(item),
                },
              ]"
            >
              <div
                v-if="
                  isCatalogVisualItem(item) &&
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
                  isCatalogVisualItem(item)
                "
                class="component-fallback-icon"
                :class="[
                  getUnitIconClass(item),
                  `unit-${getUnitVisualType(item)}`,
                  {
                    'is-consumable':
                      isConsumableUnit(item),
                    'is-missing':
                      isConsumableUnit(item) &&
                      !getConsumablePresent(item),
                  },
                ]"
                aria-hidden="true"
              >
                <svg
                  v-if="
                    getUnitVisualType(item) === 'drum'
                  "
                  viewBox="0 0 220 120"
                  class="unit-illustration realistic-unit-svg"
                >
                  <defs>
                    <linearGradient
                      :id="`drumBody-${item.id}`"
                      x1="0"
                      y1="0"
                      x2="1"
                      y2="0"
                    >
                      <stop offset="0%" stop-color="color-mix(in srgb, currentColor 62%, black)" />
                      <stop offset="18%" stop-color="currentColor" />
                      <stop offset="48%" stop-color="color-mix(in srgb, currentColor 75%, white)" />
                      <stop offset="76%" stop-color="currentColor" />
                      <stop offset="100%" stop-color="color-mix(in srgb, currentColor 55%, black)" />
                    </linearGradient>
                  </defs>

                  <ellipse cx="42" cy="60" rx="28" ry="31" fill="#111827" />
                  <ellipse cx="42" cy="60" rx="21" ry="23" fill="#202b36" />
                  <ellipse cx="42" cy="60" rx="11" ry="12" fill="#a3b0bc" />
                  <rect x="42" y="31" width="132" height="58" rx="29" :fill="`url(#drumBody-${item.id})`" />
                  <ellipse cx="174" cy="60" rx="14" ry="18" fill="#1f2937" />
                  <rect x="165" y="42" width="24" height="36" rx="7" fill="#111827" />
                  <path d="M58 40h95" stroke="rgba(255,255,255,.42)" stroke-width="6" stroke-linecap="round" />
                  <path d="M58 82h97" stroke="rgba(0,0,0,.18)" stroke-width="5" stroke-linecap="round" />
                  <circle cx="42" cy="60" r="24" fill="none" stroke="rgba(255,255,255,.24)" stroke-width="3" />
                </svg>

                <svg
                  v-else-if="
                    getUnitVisualType(item) === 'fuser'
                  "
                  viewBox="0 0 220 120"
                  class="unit-illustration realistic-unit-svg"
                >
                  <rect x="22" y="28" width="162" height="62" rx="12" fill="#1f2937" />
                  <rect x="34" y="39" width="112" height="15" rx="7" fill="#0f172a" />
                  <rect x="34" y="58" width="112" height="17" rx="8" fill="currentColor" />
                  <rect x="146" y="36" width="24" height="43" rx="8" fill="#334155" />
                  <rect x="170" y="43" width="19" height="26" rx="6" fill="#22c55e" />
                  <rect x="12" y="45" width="18" height="23" rx="5" fill="#111827" />
                  <path d="M30 34h132" stroke="rgba(255,255,255,.16)" stroke-width="3" />
                  <path d="M28 83h138" stroke="rgba(255,255,255,.12)" stroke-width="3" />
                </svg>

                <svg
                  v-else-if="
                    getUnitVisualType(item) === 'itb'
                  "
                  viewBox="0 0 220 120"
                  class="unit-illustration realistic-unit-svg"
                >
                  <path d="M26 41h138l22 14v26l-22 14H26l-10-10V51z" fill="#0f172a" />
                  <rect x="44" y="50" width="92" height="25" rx="12" fill="currentColor" />
                  <rect x="136" y="47" width="30" height="31" rx="8" fill="#1f2937" />
                  <circle cx="36" cy="63" r="9" fill="#475569" />
                  <circle cx="172" cy="63" r="11" fill="#475569" />
                  <path d="M49 55h82" stroke="rgba(255,255,255,.4)" stroke-width="4" stroke-linecap="round" />
                </svg>

                <svg
                  v-else-if="
                    getUnitVisualType(item) === 'adf'
                  "
                  viewBox="0 0 220 120"
                  class="unit-illustration realistic-unit-svg"
                >
                  <rect x="38" y="54" width="92" height="34" rx="9" fill="#d1d5db" />
                  <rect x="57" y="66" width="54" height="8" rx="4" fill="#9ca3af" />
                  <path d="M62 33h60l26 19H88z" fill="#1f2937" />
                  <path d="M50 47h70l16 11H65z" fill="#475569" />
                  <rect x="28" y="82" width="120" height="8" rx="4" fill="#9ca3af" />
                </svg>

                <svg
                  v-else-if="
                    getUnitVisualType(item) === 'cassette' ||
                    getUnitVisualType(item) === 'paper_feed'
                  "
                  viewBox="0 0 220 120"
                  class="unit-illustration realistic-unit-svg"
                >
                  <path d="M32 48h110l22 15v26l-22 13H32l-12-11V58z" fill="#d1d5db" />
                  <rect x="54" y="58" width="70" height="25" rx="5" fill="#f8fafc" />
                  <path d="M48 48l15-12h78l13 12" fill="#94a3b8" />
                  <rect x="86" y="87" width="30" height="7" rx="3.5" fill="#475569" />
                  <path d="M62 64h52" stroke="#cbd5e1" stroke-width="3" />
                </svg>

                <svg
                  v-else-if="
                    getUnitVisualType(item) === 'developer'
                  "
                  viewBox="0 0 220 120"
                  class="unit-illustration realistic-unit-svg"
                >
                  <rect x="28" y="38" width="128" height="44" rx="22" fill="#263746" />
                  <circle cx="40" cy="60" r="20" fill="#1e293b" />
                  <circle cx="40" cy="60" r="10" fill="currentColor" />
                  <rect x="54" y="46" width="82" height="12" rx="6" fill="currentColor" />
                  <rect x="54" y="62" width="82" height="10" rx="5" fill="#475569" />
                  <rect x="152" y="48" width="20" height="24" rx="6" fill="#1f2937" />
                  <path d="M60 50h68" stroke="rgba(255,255,255,.36)" stroke-width="4" />
                </svg>

                <svg
                  v-else-if="
                    getUnitVisualType(item) === 'duplex'
                  "
                  viewBox="0 0 220 120"
                  class="unit-illustration realistic-unit-svg"
                >
                  <rect x="36" y="35" width="118" height="52" rx="9" fill="#d1d5db" />
                  <rect x="70" y="49" width="50" height="18" rx="4" fill="#64748b" />
                  <rect x="122" y="45" width="18" height="28" rx="4" fill="#94a3b8" />
                  <path d="M40 78h110" stroke="#9ca3af" stroke-width="4" />
                  <path d="M40 44h110" stroke="rgba(255,255,255,.55)" stroke-width="3" />
                </svg>

                <svg
                  v-else-if="
                    getUnitVisualType(item) === 'waste_toner'
                  "
                  viewBox="0 0 120 120"
                  class="unit-illustration realistic-unit-svg waste-toner-svg"
                >
                  <defs>
                    <linearGradient
                      :id="`wasteBody-${item.id}`"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop
                        offset="0%"
                        stop-color="#f7fafc"
                      />
                      <stop
                        offset="100%"
                        stop-color="#cbd5df"
                      />
                    </linearGradient>

                    <clipPath
                      :id="`wasteClip-${item.id}`"
                    >
                      <path
                        d="M29 28h62l-6 71H35z"
                      />
                    </clipPath>
                  </defs>

                  <rect
                    x="25"
                    y="18"
                    width="70"
                    height="13"
                    rx="5"
                    fill="#3b4753"
                  />

                  <rect
                    x="37"
                    y="11"
                    width="46"
                    height="9"
                    rx="4"
                    fill="#687582"
                  />

                  <path
                    d="M29 28h62l-6 71H35z"
                    :fill="`url(#wasteBody-${item.id})`"
                    stroke="#8d9aa5"
                    stroke-width="2"
                  />

                  <g
                    :clip-path="`url(#wasteClip-${item.id})`"
                  >
                    <rect
                      x="29"
                      :y="
                        99 -
                        (
                          64 *
                          getConsumableLevel(item) /
                          100
                        )
                      "
                      width="62"
                      :height="
                        64 *
                        getConsumableLevel(item) /
                        100
                      "
                      fill="#505861"
                      opacity="0.82"
                    />

                    <path
                      v-if="
                        getConsumableLevel(item) > 0
                      "
                      :d="`
                        M29 ${
                          99 -
                          (
                            64 *
                            getConsumableLevel(item) /
                            100
                          )
                        }
                        C44 ${
                          96 -
                          (
                            64 *
                            getConsumableLevel(item) /
                            100
                          )
                        },
                        66 ${
                          102 -
                          (
                            64 *
                            getConsumableLevel(item) /
                            100
                          )
                        },
                        91 ${
                          98 -
                          (
                            64 *
                            getConsumableLevel(item) /
                            100
                          )
                        }
                      `"
                      fill="none"
                      stroke="rgba(255,255,255,.45)"
                      stroke-width="3"
                    />
                  </g>

                  <rect
                    x="42"
                    y="43"
                    width="36"
                    height="25"
                    rx="5"
                    fill="rgba(255,255,255,.68)"
                    stroke="#9ca8b2"
                  />

                  <text
                    x="60"
                    y="59"
                    text-anchor="middle"
                    class="waste-toner-label"
                  >
                    RESIDUAL
                  </text>

                  <g
                    v-if="
                      !getConsumablePresent(item)
                    "
                    class="toner-missing-overlay"
                  >
                    <path
                      d="M34 34L86 88M86 34L34 88"
                    />
                  </g>
                </svg>

                <svg
                  v-else-if="
                    [
                      'toner',
                      'ink',
                    ].includes(
                      getUnitVisualType(item)
                    )
                  "
                  viewBox="0 0 100 120"
                  class="unit-illustration realistic-unit-svg consumable-unit-svg toner-cartridge-svg"
                >
                  <defs>
                    <clipPath
                      :id="`tonerBodyClip-${item.id}`"
                    >
                      <rect
                        x="20"
                        y="15"
                        width="60"
                        height="75"
                        rx="5"
                      />
                    </clipPath>
                  </defs>

                  <rect
                    x="28"
                    y="8"
                    width="44"
                    height="8"
                    rx="2"
                    class="toner-cap"
                  />

                  <rect
                    x="31"
                    y="5"
                    width="38"
                    height="4"
                    rx="2"
                    class="toner-cap-highlight"
                  />

                  <rect
                    x="20"
                    y="15"
                    width="60"
                    height="75"
                    rx="5"
                    class="toner-shell"
                  />

                  <g
                    :clip-path="`url(#tonerBodyClip-${item.id})`"
                  >
                    <rect
                      x="22"
                      :y="
                        17 +
                        (
                          71 *
                          (
                            100 -
                            getConsumableLevel(item)
                          ) /
                          100
                        )
                      "
                      width="56"
                      :height="
                        71 *
                        getConsumableLevel(item) /
                        100
                      "
                      class="toner-fill"
                    />

                    <line
                      x1="18"
                      :y1="
                        17 +
                        (
                          71 *
                          (
                            100 -
                            getConsumableLevel(item)
                          ) /
                          100
                        )
                      "
                      x2="82"
                      :y2="
                        17 +
                        (
                          71 *
                          (
                            100 -
                            getConsumableLevel(item)
                          ) /
                          100
                        )
                      "
                      class="toner-level-line"
                    />
                  </g>

                  <rect
                    x="22"
                    y="92"
                    width="56"
                    height="18"
                    rx="3"
                    class="toner-label"
                  />

                  <text
                    x="50"
                    y="105"
                    text-anchor="middle"
                    class="toner-label-text"
                  >
                    {{
                      getUnitIconClass(item) === "cyan"
                        ? "C"
                        : getUnitIconClass(item) === "magenta"
                          ? "M"
                          : getUnitIconClass(item) === "yellow"
                            ? "Y"
                            : "K"
                    }}
                  </text>

                  <g
                    v-if="
                      !getConsumablePresent(item)
                    "
                    class="toner-missing-overlay"
                  >
                    <rect
                      x="20"
                      y="15"
                      width="60"
                      height="95"
                      rx="5"
                    />

                    <path
                      d="M31 38L69 76M69 38L31 76"
                    />
                  </g>
                </svg>

                <svg
                  v-else
                  viewBox="0 0 220 120"
                  class="unit-illustration realistic-unit-svg"
                >
                  <rect x="38" y="38" width="112" height="45" rx="12" fill="#d8e2ea" />
                  <circle cx="94" cy="60" r="14" fill="currentColor" />
                  <path d="M94 34v10M94 76v10M68 60H58M130 60h10M76 43l6 6M112 71l6 6M112 49l6-6M76 77l6-6" stroke="#334155" stroke-width="4" stroke-linecap="round" fill="none" />
                </svg>
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
                      {{ getDisplayItemName(item) }}
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
                  v-if="
                    isConsumableUnit(item)
                  "
                  class="consumable-level-card"
                  :class="[
                    getUnitIconClass(item),
                    getConsumableCardClass(item),
                  ]"
                >
                  <div class="consumable-level-header">
                    <div>
                      <span class="consumable-color-dot"></span>

                      <strong>
                        {{
                          getUnitVisualType(item) === "waste_toner"
                            ? "Nivel residual"
                            : getUnitVisualType(item) === "ink"
                              ? "Nivel de tinta"
                              : "Nivel de tóner"
                        }}
                      </strong>
                    </div>

                    <span
                      class="consumable-level-state"
                    >
                      {{
                        getConsumableLevelLabel(
                          item
                        )
                      }}
                    </span>
                  </div>

                  <div
                    v-if="
                      getConsumablePresent(item)
                    "
                    class="consumable-level-value"
                  >
                    <strong>
                      {{
                        getConsumableLevel(
                          item
                        )
                      }}%
                    </strong>

                    <div class="consumable-level-track">
                      <span
                        :style="{
                          width:
                            `${getConsumableLevel(item)}%`,
                        }"
                      ></span>
                    </div>

                    <div class="consumable-level-scale">
                      <span>0%</span>
                      <span>100%</span>
                    </div>
                  </div>

                  <div
                    v-else
                    class="consumable-missing-message"
                  >
                    <span class="missing-x">
                      ×
                    </span>

                    <div>
                      <strong>
                        {{
                    getUnitVisualType(
                      selectedItem
                    ) === "waste_toner"
                      ? "Sin depósito"
                      : "Sin botella"
                  }}
                      </strong>

                      <small>
                        No instalada
                      </small>
                    </div>
                  </div>
                </div>

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
            </section>
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
          v-if="isReviewingConsumable()"
          class="consumable-review-panel"
        >
          <div class="consumable-review-heading">
            <div>
              <strong>
                {{
                  getUnitVisualType(
                    selectedItem
                  ) === "waste_toner"
                    ? "Estado del depósito residual"
                    : "Estado del cartucho o botella"
                }}
              </strong>

              <small>
                Registra presencia y nivel actual.
              </small>
            </div>

            <span
              class="consumable-review-label"
              :class="{
                missing:
                  reviewForm
                    .consumable_present === false,
                empty:
                  reviewForm
                    .consumable_present === true &&
                  Number(
                    reviewForm
                      .consumable_level_percent
                  ) === 0,
                full:
                  reviewForm
                    .consumable_present === true &&
                  Number(
                    reviewForm
                      .consumable_level_percent
                  ) === 100,
              }"
            >
              {{
                getReviewConsumableLevelLabel()
              }}
            </span>
          </div>

          <div class="consumable-presence-options">
            <button
              type="button"
              class="consumable-presence-button"
              :class="{
                active:
                  reviewForm
                    .consumable_present === true,
              }"
              @click="
                selectConsumablePresence(
                  true
                )
              "
            >
              <span class="presence-icon">
                ✓
              </span>

              <span>
                <strong>
                  {{
                    getUnitVisualType(
                      selectedItem
                    ) === "waste_toner"
                      ? "Con depósito"
                      : "Con botella"
                  }}
                </strong>

                <small>
                  Instalada
                </small>
              </span>
            </button>

            <button
              type="button"
              class="consumable-presence-button missing"
              :class="{
                active:
                  reviewForm
                    .consumable_present === false,
              }"
              @click="
                selectConsumablePresence(
                  false
                )
              "
            >
              <span class="presence-icon">
                ×
              </span>

              <span>
                <strong>
                  Sin botella
                </strong>

                <small>
                  No instalada
                </small>
              </span>
            </button>
          </div>

          <div
            v-if="
              reviewForm
                .consumable_present === true
            "
            class="consumable-level-editor"
          >
            <div class="consumable-level-row">
              <label>
                Nivel actual
              </label>

              <strong>
                {{
                  Number(
                    reviewForm
                      .consumable_level_percent
                  )
                }}%
              </strong>
            </div>

            <input
              v-model.number="
                reviewForm
                  .consumable_level_percent
              "
              type="range"
              min="0"
              max="100"
              step="1"
            />

            <div class="consumable-level-scale">
              <span>0% · Vacío</span>
              <span>100% · Lleno</span>
            </div>

            <div class="consumable-quick-levels">
              <button
                v-for="level in [
                  0,
                  10,
                  25,
                  50,
                  75,
                  100,
                ]"
                :key="level"
                type="button"
                :class="{
                  active:
                    Number(
                      reviewForm
                        .consumable_level_percent
                    ) === level,
                }"
                @click="
                  reviewForm
                    .consumable_level_percent =
                    level
                "
              >
                {{ level }}%
              </button>
            </div>
          </div>

          <div
            v-else-if="
              reviewForm
                .consumable_present === false
            "
            class="consumable-absent-preview"
          >
            <span>×</span>

            <div>
              <strong>
                Sin botella o cartucho
              </strong>

              <small>
                No se registra porcentaje.
              </small>
            </div>
          </div>
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