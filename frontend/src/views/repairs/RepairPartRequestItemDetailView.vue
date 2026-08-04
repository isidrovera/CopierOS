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

import RepairPartRequestStatusBadge from "./components/RepairPartRequestStatusBadge.vue"

import {
  authorizeRepairPartWithdrawal,
  completeRepairPartReplacement,
  confirmRepairPartWithdrawal,
  createRepairPartDelivery,
  createRepairPartReplacement,
  createRepairPartRequestDecision,
  createRepairPartRequestReview,
  createRepairPartSource,
  createRepairPartWithdrawal,
  deliverRepairPart,
  getRepairPartDeliveries,
  getRepairPartReplacements,
  getRepairPartRequest,
  getRepairPartRequestComments,
  getRepairPartRequestDecisions,
  getRepairPartRequestHistory,
  getRepairPartRequestItem,
  getRepairPartRequestReviews,
  getRepairPartSources,
  getRepairPartWithdrawals,
  prepareRepairPartDelivery,
  receiveRepairPartDelivery,
  receiveRepairPartWithdrawal,
  updateRepairPartSource,
} from "../../services/repairs.service"

import {
  getEquipment,
} from "../../services/equipment.service"

import {
  getRentalEquipment,
  getWarehouses,
} from "../../services/rentals.service"

import {
  getUsers,
} from "../../services/users.service"

import "./RepairPartRequestItemDetailView.css"


const route = useRoute()
const router = useRouter()


const loading = ref(false)
const actionLoading = ref(false)
const errorMessage = ref("")
const successMessage = ref("")

const item = ref(null)
const request = ref(null)

const reviews = ref([])
const decisions = ref([])
const sources = ref([])
const withdrawals = ref([])
const deliveries = ref([])
const replacements = ref([])
const comments = ref([])
const history = ref([])

const equipmentResults = ref([])
const rentalEquipmentResults = ref([])
const warehouseResults = ref([])
const userResults = ref([])

const equipmentSearch = ref("")
const rentalEquipmentSearch = ref("")
const warehouseSearch = ref("")
const userSearch = ref("")

const searchingEquipment = ref(false)
const searchingRentalEquipment = ref(false)
const searchingWarehouses = ref(false)
const searchingUsers = ref(false)


const reviewForm = reactive({
  result: "",
  proposed_quantity: "",
  justification: "",
  requires_management_approval: true,
  requires_replacement: false,
})

const decisionForm = reactive({
  decision: "",
  approved_quantity: "",
  reason: "",
  information_required: "",
  is_final: true,
})

const sourceForm = reactive({
  source_type: "",
  component_serial_number: "",
  rental_warehouse: "",
  donor_equipment: "",
  donor_rental_equipment: "",
  supplier_name: "",
  purchase_reference: "",
  available_quantity: "",
  reserved_quantity: "",
  warehouse_location: "",
  justification: "",
  is_confirmed: false,
})

const withdrawalForm = reactive({
  source: "",
  quantity: "",
  authorization_notes: "",
})

const authorizationForm = reactive({
  authorized_person: "",
  valid_until: "",
  notes: "",
})

const deliveryForm = reactive({
  quantity: "",
  delivery_document: "",
  notes: "",
})

const deliveryActionForm = reactive({
  delivered_to: "",
  quantity: "",
  delivery_document: "",
  notes: "",
})

const receptionForm = reactive({
  received_quantity: "",
  notes: "",
})

const replacementForm = reactive({
  replacement_type: "none",
  status: "not_applicable",
  source_equipment: "",
  replacement_serial_number: "",
  responsible_user: "",
  due_at: "",
  external_reference: "",
  notes: "",
})


const reviewOptions = [
  {
    value: "stock",
    label: "Disponible en almacén",
  },
  {
    value: "rental_warehouse",
    label: "Almacén de alquiler",
  },
  {
    value: "donor_for_parts",
    label: "Máquina para partes",
  },
  {
    value: "donor_with_problems",
    label: "Máquina con problemas",
  },
  {
    value: "donor_operational",
    label: "Máquina operativa",
  },
  {
    value: "purchase",
    label: "Compra externa",
  },
  {
    value: "external_repair",
    label: "Reparación externa",
  },
  {
    value: "not_available",
    label: "Sin disponibilidad",
  },
  {
    value: "information_required",
    label: "Información requerida",
  },
]

const decisionOptions = [
  {
    value: "approved",
    label: "Aprobar",
  },
  {
    value: "partially_approved",
    label: "Aprobar parcialmente",
  },
  {
    value: "rejected",
    label: "Rechazar",
  },
  {
    value: "information_required",
    label: "Solicitar información",
  },
]

const sourceTypeOptions = [
  {
    value: "component_stock",
    label: "Almacén de repuestos",
  },
  {
    value: "rental_warehouse",
    label: "Almacén de alquiler",
  },
  {
    value: "donor_for_parts",
    label: "Máquina para partes",
  },
  {
    value: "donor_with_problems",
    label: "Máquina con problemas",
  },
  {
    value: "donor_operational",
    label: "Máquina operativa",
  },
  {
    value: "external_purchase",
    label: "Compra externa",
  },
  {
    value: "external_repair",
    label: "Reparación externa",
  },
  {
    value: "not_available",
    label: "Sin disponibilidad",
  },
]

const replacementTypeOptions = [
  {
    value: "none",
    label: "No aplica",
  },
  {
    value: "equivalent_part",
    label: "Reponer parte equivalente",
  },
  {
    value: "damaged_part_return",
    label: "Devolver parte dañada",
  },
  {
    value: "temporary_loan",
    label: "Préstamo temporal",
  },
  {
    value: "external_purchase",
    label: "Reposición por compra",
  },
  {
    value: "external_repair",
    label: "Reposición por reparación externa",
  },
]

const replacementStatusOptions = [
  {
    value: "not_applicable",
    label: "No aplica",
  },
  {
    value: "pending",
    label: "Pendiente",
  },
  {
    value: "in_purchase",
    label: "En compra",
  },
  {
    value: "in_external_repair",
    label: "En reparación externa",
  },
  {
    value: "received",
    label: "Recibida",
  },
  {
    value: "installed_at_source",
    label: "Instalada en equipo de origen",
  },
  {
    value: "returned_to_warehouse",
    label: "Devuelta a almacén",
  },
  {
    value: "overdue",
    label: "Vencida",
  },
  {
    value: "cancelled",
    label: "Cancelada",
  },
  {
    value: "completed",
    label: "Completada",
  },
]


const itemId = computed(() =>
  String(route.params.id || "")
)

const itemName = computed(() =>
  item.value?.component_name ||
  item.value?.custom_name ||
  "Ítem solicitado"
)

const currentSource = computed(() =>
  sources.value.find(
    (source) => source.is_confirmed
  ) ||
  sources.value[0] ||
  null
)

const currentWithdrawal = computed(() =>
  withdrawals.value[0] || null
)

const currentDelivery = computed(() =>
  deliveries.value[0] || null
)

const currentReplacement = computed(() =>
  replacements.value[0] || null
)

const canReview = computed(() =>
  [
    "pending_area_review",
    "source_evaluation",
    "information_requested",
  ].includes(item.value?.status)
)

const canDecide = computed(() =>
  item.value?.status === "pending_management"
)

const canDefineSource = computed(() =>
  [
    "source_evaluation",
    "approved",
    "partially_approved",
    "pending_reservation",
    "pending_purchase",
    "pending_external_repair",
  ].includes(item.value?.status)
)

const canCreateWithdrawal = computed(() =>
  Boolean(
    currentSource.value &&
    !currentWithdrawal.value &&
    [
      "pending_withdrawal",
      "authorized_for_withdrawal",
      "approved",
      "partially_approved",
      "pending_reservation",
    ].includes(item.value?.status)
  )
)

const canCreateDelivery = computed(() =>
  !currentDelivery.value &&
  [
    "withdrawn",
    "pending_logistics",
    "prepared",
  ].includes(item.value?.status)
)

const canCreateReplacement = computed(() =>
  item.value?.requires_replacement &&
  !currentReplacement.value
)

const quantityRequested = computed(() =>
  Number(item.value?.requested_quantity || 0)
)

const quantityApproved = computed(() =>
  Number(
    item.value?.approved_quantity ||
    item.value?.requested_quantity ||
    0
  )
)

const progressPercentage = computed(() => {
  const approved = quantityApproved.value

  if (approved <= 0) {
    return 0
  }

  const received = Number(
    item.value?.received_quantity || 0
  )

  return Math.min(
    100,
    Math.round(
      (received / approved) * 100
    )
  )
})

const pendingAction = computed(() => {
  const status = item.value?.status

  const labels = {
    draft: {
      title: "Ítem en borrador",
      text: "La solicitud debe enviarse para iniciar el proceso.",
      tone: "neutral",
    },
    requested: {
      title: "Solicitud registrada",
      text: "El ítem está esperando asignación de la siguiente etapa.",
      tone: "info",
    },
    pending_area_review: {
      title: "Revisión del jefe pendiente",
      text: "El jefe de área debe revisar la disponibilidad y proponer una cantidad.",
      tone: "warning",
    },
    source_evaluation: {
      title: "Evaluar origen del repuesto",
      text: "Busca stock, almacén de alquiler, una máquina donante o un proveedor.",
      tone: "warning",
    },
    pending_management: {
      title: "Decisión de gerencia pendiente",
      text: "Gerencia debe aprobar, aprobar parcialmente, rechazar o solicitar información.",
      tone: "warning",
    },
    information_requested: {
      title: "Información solicitada",
      text: "Debe completarse la información requerida antes de continuar.",
      tone: "warning",
    },
    approved: {
      title: "Definir origen",
      text: "El ítem fue aprobado y necesita un origen de abastecimiento.",
      tone: "success",
    },
    partially_approved: {
      title: "Definir origen",
      text: "El ítem fue aprobado parcialmente y necesita un origen.",
      tone: "success",
    },
    pending_reservation: {
      title: "Reserva pendiente",
      text: "Confirma el inventario y la cantidad que será reservada.",
      tone: "warning",
    },
    pending_purchase: {
      title: "Compra pendiente",
      text: "Registra el proveedor y la referencia de compra.",
      tone: "warning",
    },
    pending_external_repair: {
      title: "Reparación externa pendiente",
      text: "Registra el proveedor y la referencia externa.",
      tone: "warning",
    },
    pending_withdrawal: {
      title: "Retiro pendiente",
      text: "Crea y autoriza el retiro del repuesto.",
      tone: "warning",
    },
    authorized_for_withdrawal: {
      title: "Retiro autorizado",
      text: "El repuesto puede ser retirado por la persona autorizada.",
      tone: "info",
    },
    withdrawn: {
      title: "Enviar a logística",
      text: "El repuesto fue retirado y debe prepararse para entrega.",
      tone: "info",
    },
    pending_logistics: {
      title: "Preparación logística",
      text: "Crea o prepara la entrega para el técnico.",
      tone: "warning",
    },
    prepared: {
      title: "Entrega preparada",
      text: "Registra la persona que recibirá el repuesto.",
      tone: "info",
    },
    delivered: {
      title: "Confirmar recepción",
      text: "El técnico debe confirmar la cantidad recibida.",
      tone: "warning",
    },
    received: {
      title: "Instalación pendiente",
      text: "El repuesto fue recibido y está pendiente de instalación.",
      tone: "info",
    },
    installed: {
      title: "Instalación registrada",
      text: "Verifica si existe devolución o reposición pendiente.",
      tone: "success",
    },
    pending_return: {
      title: "Devolución pendiente",
      text: "Debe devolverse la parte dañada.",
      tone: "warning",
    },
    pending_replacement: {
      title: "Reposición pendiente",
      text: "Registra y completa la reposición correspondiente.",
      tone: "warning",
    },
    completed: {
      title: "Proceso finalizado",
      text: "El ítem completó todas las etapas.",
      tone: "success",
    },
    rejected: {
      title: "Ítem rechazado",
      text: "El proceso no puede continuar con este ítem.",
      tone: "danger",
    },
    cancelled: {
      title: "Ítem cancelado",
      text: "El proceso fue cancelado.",
      tone: "danger",
    },
  }

  return labels[status] || {
    title: "Estado actual",
    text: item.value?.status_name || status,
    tone: "neutral",
  }
})


function normalizeResults(response) {
  if (Array.isArray(response)) {
    return response
  }

  return Array.isArray(response?.results)
    ? response.results
    : []
}


function clearMessages() {
  errorMessage.value = ""
  successMessage.value = ""
}


async function loadDetail() {
  loading.value = true
  clearMessages()

  try {
    const itemResponse =
      await getRepairPartRequestItem(
        itemId.value
      )

    item.value = itemResponse

    const [
      requestResponse,
      reviewResponse,
      decisionResponse,
      sourceResponse,
      withdrawalResponse,
      deliveryResponse,
      replacementResponse,
      commentResponse,
      historyResponse,
    ] = await Promise.all([
      getRepairPartRequest(
        itemResponse.request
      ),
      getRepairPartRequestReviews({
        item: itemId.value,
      }),
      getRepairPartRequestDecisions({
        item: itemId.value,
      }),
      getRepairPartSources({
        item: itemId.value,
      }),
      getRepairPartWithdrawals({
        item: itemId.value,
      }),
      getRepairPartDeliveries({
        item: itemId.value,
      }),
      getRepairPartReplacements({
        item: itemId.value,
      }),
      getRepairPartRequestComments({
        item: itemId.value,
      }),
      getRepairPartRequestHistory({
        item: itemId.value,
      }),
    ])

    request.value = requestResponse
    reviews.value =
      normalizeResults(reviewResponse)
    decisions.value =
      normalizeResults(decisionResponse)
    sources.value =
      normalizeResults(sourceResponse)
    withdrawals.value =
      normalizeResults(withdrawalResponse)
    deliveries.value =
      normalizeResults(deliveryResponse)
    replacements.value =
      normalizeResults(replacementResponse)
    comments.value =
      normalizeResults(commentResponse)
    history.value =
      normalizeResults(historyResponse)

    setInitialQuantities()
    setCurrentSourceForm()
  } catch (error) {
    errorMessage.value =
      error?.message ||
      "No se pudo cargar el detalle del ítem."
  } finally {
    loading.value = false
  }
}


function setInitialQuantities() {
  const requested =
    String(item.value?.requested_quantity || "")

  const approved =
    String(
      item.value?.approved_quantity ||
      item.value?.requested_quantity ||
      ""
    )

  if (!reviewForm.proposed_quantity) {
    reviewForm.proposed_quantity =
      requested
  }

  if (!decisionForm.approved_quantity) {
    decisionForm.approved_quantity =
      requested
  }

  if (!sourceForm.available_quantity) {
    sourceForm.available_quantity =
      approved
  }

  if (!sourceForm.reserved_quantity) {
    sourceForm.reserved_quantity =
      approved
  }

  if (!withdrawalForm.quantity) {
    withdrawalForm.quantity =
      approved
  }

  if (!deliveryForm.quantity) {
    deliveryForm.quantity =
      approved
  }

  if (!deliveryActionForm.quantity) {
    deliveryActionForm.quantity =
      approved
  }

  if (!receptionForm.received_quantity) {
    receptionForm.received_quantity =
      approved
  }
}


function setCurrentSourceForm() {
  const source = currentSource.value

  if (!source) {
    return
  }

  sourceForm.source_type =
    source.source_type || ""

  sourceForm.component_serial_number =
    source.component_serial_number || ""

  sourceForm.rental_warehouse =
    source.rental_warehouse || ""

  sourceForm.donor_equipment =
    source.donor_equipment || ""

  sourceForm.donor_rental_equipment =
    source.donor_rental_equipment || ""

  sourceForm.supplier_name =
    source.supplier_name || ""

  sourceForm.purchase_reference =
    source.purchase_reference || ""

  sourceForm.available_quantity =
    String(source.available_quantity || "")

  sourceForm.reserved_quantity =
    String(source.reserved_quantity || "")

  sourceForm.warehouse_location =
    source.warehouse_location || ""

  sourceForm.justification =
    source.justification || ""

  sourceForm.is_confirmed =
    Boolean(source.is_confirmed)

  withdrawalForm.source =
    source.id
}


async function runAction(
  callback,
  successText
) {
  actionLoading.value = true
  clearMessages()

  try {
    await callback()

    successMessage.value =
      successText

    await loadDetail()
  } catch (error) {
    errorMessage.value =
      error?.message ||
      "No se pudo completar la acción."
  } finally {
    actionLoading.value = false
  }
}


async function searchEquipment() {
  searchingEquipment.value = true

  try {
    const response =
      await getEquipment({
        search: equipmentSearch.value,
        isActive: true,
      })

    equipmentResults.value =
      normalizeResults(response)
  } catch (error) {
    errorMessage.value =
      error?.message ||
      "No se pudieron buscar equipos."
  } finally {
    searchingEquipment.value = false
  }
}


async function searchRentalEquipment() {
  searchingRentalEquipment.value = true

  try {
    const response =
      await getRentalEquipment({
        search: rentalEquipmentSearch.value,
        is_active: true,
      })

    rentalEquipmentResults.value =
      normalizeResults(response)
  } catch (error) {
    errorMessage.value =
      error?.message ||
      "No se pudieron buscar equipos de alquiler."
  } finally {
    searchingRentalEquipment.value = false
  }
}


async function searchWarehouses() {
  searchingWarehouses.value = true

  try {
    const response =
      await getWarehouses({
        search: warehouseSearch.value,
        is_active: true,
      })

    warehouseResults.value =
      normalizeResults(response)
  } catch (error) {
    errorMessage.value =
      error?.message ||
      "No se pudieron buscar almacenes."
  } finally {
    searchingWarehouses.value = false
  }
}


async function searchUsers() {
  searchingUsers.value = true

  try {
    const response =
      await getUsers({
        search: userSearch.value,
        isActive: true,
      })

    userResults.value =
      normalizeResults(response)
  } catch (error) {
    errorMessage.value =
      error?.message ||
      "No se pudieron buscar usuarios."
  } finally {
    searchingUsers.value = false
  }
}


function equipmentLabel(equipment) {
  return [
    equipment.internal_code,
    equipment.equipment_model_name ||
      equipment.model_name,
    equipment.serial_number,
  ]
    .filter(Boolean)
    .join(" · ")
}


function rentalEquipmentLabel(equipment) {
  return [
    equipment.internal_code ||
      equipment.equipment_code,
    equipment.equipment_model_name ||
      equipment.model_name,
    equipment.serial_number ||
      equipment.equipment_serial_number,
  ]
    .filter(Boolean)
    .join(" · ")
}


function warehouseLabel(warehouse) {
  return [
    warehouse.code,
    warehouse.name,
    warehouse.location,
  ]
    .filter(Boolean)
    .join(" · ")
}


function userLabel(user) {
  return (
    user.full_name ||
    user.name ||
    user.email ||
    user.username ||
    "Usuario"
  )
}


function submitReview() {
  if (!reviewForm.result) {
    errorMessage.value =
      "Selecciona el resultado de la revisión."

    return
  }

  if (
    reviewForm.result !== "pending" &&
    !reviewForm.justification.trim()
  ) {
    errorMessage.value =
      "Registra la justificación de la revisión."

    return
  }

  runAction(
    () =>
      createRepairPartRequestReview({
        item: itemId.value,
        result: reviewForm.result,
        justification:
          reviewForm.justification.trim(),
        requires_management_approval:
          reviewForm.requires_management_approval,
        requires_replacement:
          reviewForm.requires_replacement,
        proposed_quantity:
          reviewForm.proposed_quantity || 0,
      }),
    "Revisión registrada correctamente."
  )
}


function submitDecision() {
  if (!decisionForm.decision) {
    errorMessage.value =
      "Selecciona la decisión de gerencia."

    return
  }

  const payload = {
    request: item.value.request,
    item: itemId.value,
    decision: decisionForm.decision,
    requested_quantity:
      item.value.requested_quantity,
    approved_quantity:
      decisionForm.approved_quantity || 0,
    reason:
      decisionForm.reason.trim(),
    information_required:
      decisionForm.information_required.trim(),
    is_final:
      decisionForm.is_final,
  }

  runAction(
    () =>
      createRepairPartRequestDecision(
        payload
      ),
    "Decisión registrada correctamente."
  )
}


function buildSourcePayload() {
  const payload = {
    item: itemId.value,
    source_type:
      sourceForm.source_type,
    component_serial_number:
      sourceForm.component_serial_number.trim(),
    available_quantity:
      sourceForm.available_quantity || 0,
    reserved_quantity:
      sourceForm.reserved_quantity || 0,
    warehouse_location:
      sourceForm.warehouse_location.trim(),
    justification:
      sourceForm.justification.trim(),
    is_confirmed:
      sourceForm.is_confirmed,
  }

  if (
    sourceForm.source_type ===
    "rental_warehouse"
  ) {
    payload.rental_warehouse =
      sourceForm.rental_warehouse
  }

  if (
    [
      "donor_for_parts",
      "donor_with_problems",
      "donor_operational",
    ].includes(sourceForm.source_type)
  ) {
    payload.donor_equipment =
      sourceForm.donor_equipment

    if (
      sourceForm.donor_rental_equipment
    ) {
      payload.donor_rental_equipment =
        sourceForm.donor_rental_equipment
    }
  }

  if (
    [
      "external_purchase",
      "external_repair",
    ].includes(sourceForm.source_type)
  ) {
    payload.supplier_name =
      sourceForm.supplier_name.trim()

    payload.purchase_reference =
      sourceForm.purchase_reference.trim()
  }

  return payload
}


function submitSource() {
  if (!sourceForm.source_type) {
    errorMessage.value =
      "Selecciona el origen del repuesto."

    return
  }

  const payload =
    buildSourcePayload()

  runAction(
    () =>
      currentSource.value
        ? updateRepairPartSource(
            currentSource.value.id,
            payload
          )
        : createRepairPartSource(
            payload
          ),
    currentSource.value
      ? "Origen actualizado correctamente."
      : "Origen registrado correctamente."
  )
}


function submitWithdrawal() {
  if (!currentSource.value?.id) {
    errorMessage.value =
      "Primero debes registrar el origen."

    return
  }

  runAction(
    () =>
      createRepairPartWithdrawal({
        item: itemId.value,
        source:
          currentSource.value.id,
        quantity:
          withdrawalForm.quantity,
        authorization_notes:
          withdrawalForm.authorization_notes.trim(),
      }),
    "Retiro creado correctamente."
  )
}


function authorizeWithdrawal() {
  if (!authorizationForm.authorized_person) {
    errorMessage.value =
      "Selecciona la persona autorizada."

    return
  }

  runAction(
    () =>
      authorizeRepairPartWithdrawal(
        currentWithdrawal.value.id,
        {
          authorized_person:
            authorizationForm.authorized_person,
          valid_until:
            authorizationForm.valid_until ||
            null,
          notes:
            authorizationForm.notes.trim(),
        }
      ),
    "Retiro autorizado correctamente."
  )
}


function confirmWithdrawal() {
  runAction(
    () =>
      confirmRepairPartWithdrawal(
        currentWithdrawal.value.id,
        {
          notes:
            authorizationForm.notes.trim(),
        }
      ),
    "Retiro confirmado correctamente."
  )
}


function receiveWithdrawal() {
  runAction(
    () =>
      receiveRepairPartWithdrawal(
        currentWithdrawal.value.id,
        {
          notes:
            authorizationForm.notes.trim(),
        }
      ),
    "Recepción del retiro registrada."
  )
}


function submitDelivery() {
  runAction(
    () =>
      createRepairPartDelivery({
        item: itemId.value,
        quantity:
          deliveryForm.quantity,
        delivery_document:
          deliveryForm.delivery_document.trim(),
        notes:
          deliveryForm.notes.trim(),
      }),
    "Entrega creada correctamente."
  )
}


function prepareDelivery() {
  runAction(
    () =>
      prepareRepairPartDelivery(
        currentDelivery.value.id,
        {
          notes:
            deliveryForm.notes.trim(),
        }
      ),
    "Entrega preparada correctamente."
  )
}


function deliverPart() {
  if (!deliveryActionForm.delivered_to) {
    errorMessage.value =
      "Selecciona la persona que recibirá el repuesto."

    return
  }

  runAction(
    () =>
      deliverRepairPart(
        currentDelivery.value.id,
        {
          delivered_to:
            deliveryActionForm.delivered_to,
          quantity:
            deliveryActionForm.quantity,
          delivery_document:
            deliveryActionForm.delivery_document.trim(),
          notes:
            deliveryActionForm.notes.trim(),
        }
      ),
    "Entrega registrada correctamente."
  )
}


function receiveDelivery() {
  runAction(
    () =>
      receiveRepairPartDelivery(
        currentDelivery.value.id,
        {
          received_quantity:
            receptionForm.received_quantity,
          notes:
            receptionForm.notes.trim(),
        }
      ),
    "Recepción confirmada correctamente."
  )
}


function submitReplacement() {
  const payload = {
    item: itemId.value,
    replacement_type:
      replacementForm.replacement_type,
    status:
      replacementForm.status,
    source_equipment:
      replacementForm.source_equipment ||
      null,
    replacement_serial_number:
      replacementForm.replacement_serial_number.trim(),
    responsible_user:
      replacementForm.responsible_user ||
      null,
    due_at:
      replacementForm.due_at ||
      null,
    external_reference:
      replacementForm.external_reference.trim(),
    notes:
      replacementForm.notes.trim(),
  }

  runAction(
    () =>
      createRepairPartReplacement(
        payload
      ),
    "Reposición creada correctamente."
  )
}


function completeReplacement() {
  runAction(
    () =>
      completeRepairPartReplacement(
        currentReplacement.value.id,
        {
          notes:
            replacementForm.notes.trim(),
        }
      ),
    "Reposición completada correctamente."
  )
}


function goBack() {
  if (item.value?.request) {
    router.push({
      name: "repair-part-request-detail",
      params: {
        id: item.value.request,
      },
    })

    return
  }

  router.push({
    name: "repair-part-requests",
  })
}


watch(
  () => sourceForm.source_type,
  (sourceType) => {
    if (
      sourceType === "rental_warehouse" &&
      !warehouseResults.value.length
    ) {
      searchWarehouses()
    }

    if (
      [
        "donor_for_parts",
        "donor_with_problems",
        "donor_operational",
      ].includes(sourceType) &&
      !equipmentResults.value.length
    ) {
      searchEquipment()
    }
  }
)


onMounted(async () => {
  await loadDetail()
  await searchUsers()
})
</script>

<template>
  <main class="repair-part-item-detail">
    <section
      v-if="loading"
      class="repair-part-item-detail__state"
    >
      Cargando ítem...
    </section>

    <template v-else-if="item">
      <header class="repair-part-item-detail__header">
        <button
          type="button"
          class="repair-part-item-detail__back"
          @click="goBack"
        >
          ← Volver al pedido
        </button>

        <div class="repair-part-item-detail__heading">
          <div>
            <span>
              {{ item.request_code }}
            </span>

            <h1>
              {{ itemName }}
            </h1>

            <p>
              {{ item.technical_reason }}
            </p>
          </div>

          <RepairPartRequestStatusBadge
            :status="item.status"
            :label="item.status_name"
          />
        </div>
      </header>

      <p
        v-if="errorMessage"
        class="repair-part-item-detail__message error"
      >
        {{ errorMessage }}
      </p>

      <p
        v-if="successMessage"
        class="repair-part-item-detail__message success"
      >
        {{ successMessage }}
      </p>

      <section
        class="repair-part-item-detail__pending-action"
        :class="`tone-${pendingAction.tone}`"
      >
        <div>
          <span>Acción pendiente</span>
          <strong>{{ pendingAction.title }}</strong>
          <p>{{ pendingAction.text }}</p>
        </div>

        <div class="repair-part-item-detail__progress">
          <span>
            Recepción {{ progressPercentage }}%
          </span>

          <div>
            <i
              :style="{
                width: `${progressPercentage}%`,
              }"
            />
          </div>
        </div>
      </section>

      <section class="repair-part-item-detail__summary">
        <article>
          <small>Solicitada</small>
          <strong>{{ item.requested_quantity }}</strong>
        </article>

        <article>
          <small>Aprobada</small>
          <strong>{{ item.approved_quantity }}</strong>
        </article>

        <article>
          <small>Reservada</small>
          <strong>{{ item.reserved_quantity }}</strong>
        </article>

        <article>
          <small>Entregada</small>
          <strong>{{ item.delivered_quantity }}</strong>
        </article>

        <article>
          <small>Recibida</small>
          <strong>{{ item.received_quantity }}</strong>
        </article>

        <article>
          <small>Instalada</small>
          <strong>{{ item.installed_quantity }}</strong>
        </article>
      </section>

      <section class="repair-part-item-detail__layout">
        <div class="repair-part-item-detail__main">
          <article
            v-if="canReview"
            class="repair-part-item-detail__card action-card"
          >
            <header>
              <div>
                <span>Etapa 1</span>
                <strong>Revisión del jefe de área</strong>
              </div>
            </header>

            <div class="repair-part-item-detail__form-grid">
              <label class="span-2">
                <span>Resultado</span>

                <select v-model="reviewForm.result">
                  <option value="">
                    Seleccionar resultado
                  </option>

                  <option
                    v-for="option in reviewOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </label>

              <label>
                <span>Cantidad propuesta</span>

                <input
                  v-model="reviewForm.proposed_quantity"
                  type="number"
                  min="0"
                  :max="quantityRequested"
                  step="0.01"
                />
              </label>

              <label class="check-field">
                <input
                  v-model="reviewForm.requires_management_approval"
                  type="checkbox"
                />

                <span>Requiere gerencia</span>
              </label>

              <label class="check-field">
                <input
                  v-model="reviewForm.requires_replacement"
                  type="checkbox"
                />

                <span>Requiere reposición</span>
              </label>

              <label class="span-2">
                <span>Justificación</span>

                <textarea
                  v-model="reviewForm.justification"
                  rows="4"
                  placeholder="Explica la disponibilidad y la propuesta..."
                />
              </label>
            </div>

            <footer>
              <button
                type="button"
                :disabled="actionLoading"
                @click="submitReview"
              >
                Registrar revisión
              </button>
            </footer>
          </article>

          <article
            v-if="canDecide"
            class="repair-part-item-detail__card action-card"
          >
            <header>
              <div>
                <span>Etapa 2</span>
                <strong>Decisión de gerencia</strong>
              </div>
            </header>

            <div class="repair-part-item-detail__form-grid">
              <label class="span-2">
                <span>Decisión</span>

                <select v-model="decisionForm.decision">
                  <option value="">
                    Seleccionar decisión
                  </option>

                  <option
                    v-for="option in decisionOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </label>

              <label>
                <span>Cantidad aprobada</span>

                <input
                  v-model="decisionForm.approved_quantity"
                  type="number"
                  min="0"
                  :max="quantityRequested"
                  step="0.01"
                />
              </label>

              <label class="check-field">
                <input
                  v-model="decisionForm.is_final"
                  type="checkbox"
                />

                <span>Decisión final</span>
              </label>

              <label class="span-2">
                <span>Motivo</span>

                <textarea
                  v-model="decisionForm.reason"
                  rows="3"
                  placeholder="Motivo de la decisión..."
                />
              </label>

              <label
                v-if="
                  decisionForm.decision ===
                  'information_required'
                "
                class="span-2"
              >
                <span>Información requerida</span>

                <textarea
                  v-model="decisionForm.information_required"
                  rows="3"
                  placeholder="Indica qué información debe completarse..."
                />
              </label>
            </div>

            <footer>
              <button
                type="button"
                :disabled="actionLoading"
                @click="submitDecision"
              >
                Registrar decisión
              </button>
            </footer>
          </article>

          <article
            v-if="canDefineSource"
            class="repair-part-item-detail__card action-card"
          >
            <header>
              <div>
                <span>Etapa 3</span>
                <strong>Buscar y definir origen</strong>
              </div>

              <em v-if="currentSource">
                Origen registrado
              </em>
            </header>

            <div class="repair-part-item-detail__form-grid">
              <label class="span-2">
                <span>Tipo de origen</span>

                <select v-model="sourceForm.source_type">
                  <option value="">
                    Seleccionar origen
                  </option>

                  <option
                    v-for="option in sourceTypeOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </label>

              <template
                v-if="
                  sourceForm.source_type ===
                  'component_stock'
                "
              >
                <label>
                  <span>Serie del componente</span>

                  <input
                    v-model="sourceForm.component_serial_number"
                    type="text"
                    placeholder="Serie física, cuando corresponda"
                  />
                </label>

                <label>
                  <span>Ubicación referencial</span>

                  <input
                    v-model="sourceForm.warehouse_location"
                    type="text"
                    placeholder="Estante, área o referencia"
                  />
                </label>
              </template>

              <div
                v-if="
                  sourceForm.source_type ===
                  'rental_warehouse'
                "
                class="repair-part-item-detail__search span-2"
              >
                <label>
                  <span>Buscar almacén</span>

                  <div>
                    <input
                      v-model="warehouseSearch"
                      type="search"
                      placeholder="Nombre o ubicación del almacén"
                      @keyup.enter="searchWarehouses"
                    />

                    <button
                      type="button"
                      :disabled="searchingWarehouses"
                      @click="searchWarehouses"
                    >
                      Buscar
                    </button>
                  </div>
                </label>

                <select v-model="sourceForm.rental_warehouse">
                  <option value="">
                    Seleccionar almacén
                  </option>

                  <option
                    v-for="warehouse in warehouseResults"
                    :key="warehouse.id"
                    :value="warehouse.id"
                  >
                    {{ warehouseLabel(warehouse) }}
                  </option>
                </select>
              </div>

              <template
                v-if="
                  [
                    'donor_for_parts',
                    'donor_with_problems',
                    'donor_operational',
                  ].includes(sourceForm.source_type)
                "
              >
                <div class="repair-part-item-detail__search span-2">
                  <label>
                    <span>Buscar equipo donante</span>

                    <div>
                      <input
                        v-model="equipmentSearch"
                        type="search"
                        placeholder="Código, modelo o serie"
                        @keyup.enter="searchEquipment"
                      />

                      <button
                        type="button"
                        :disabled="searchingEquipment"
                        @click="searchEquipment"
                      >
                        Buscar
                      </button>
                    </div>
                  </label>

                  <select v-model="sourceForm.donor_equipment">
                    <option value="">
                      Seleccionar equipo
                    </option>

                    <option
                      v-for="equipment in equipmentResults"
                      :key="equipment.id"
                      :value="equipment.id"
                    >
                      {{ equipmentLabel(equipment) }}
                    </option>
                  </select>
                </div>

                <div class="repair-part-item-detail__search span-2">
                  <label>
                    <span>Perfil de alquiler, cuando corresponda</span>

                    <div>
                      <input
                        v-model="rentalEquipmentSearch"
                        type="search"
                        placeholder="Buscar equipo de alquiler"
                        @keyup.enter="searchRentalEquipment"
                      />

                      <button
                        type="button"
                        :disabled="searchingRentalEquipment"
                        @click="searchRentalEquipment"
                      >
                        Buscar
                      </button>
                    </div>
                  </label>

                  <select
                    v-model="sourceForm.donor_rental_equipment"
                  >
                    <option value="">
                      No vincular perfil de alquiler
                    </option>

                    <option
                      v-for="rentalEquipment in rentalEquipmentResults"
                      :key="rentalEquipment.id"
                      :value="rentalEquipment.id"
                    >
                      {{ rentalEquipmentLabel(rentalEquipment) }}
                    </option>
                  </select>
                </div>
              </template>

              <template
                v-if="
                  [
                    'external_purchase',
                    'external_repair',
                  ].includes(sourceForm.source_type)
                "
              >
                <label>
                  <span>Proveedor</span>

                  <input
                    v-model="sourceForm.supplier_name"
                    type="text"
                    placeholder="Nombre del proveedor"
                  />
                </label>

                <label>
                  <span>Referencia</span>

                  <input
                    v-model="sourceForm.purchase_reference"
                    type="text"
                    placeholder="OC, cotización o referencia"
                  />
                </label>
              </template>

              <label>
                <span>Cantidad disponible</span>

                <input
                  v-model="sourceForm.available_quantity"
                  type="number"
                  min="0"
                  step="0.01"
                />
              </label>

              <label>
                <span>Cantidad reservada</span>

                <input
                  v-model="sourceForm.reserved_quantity"
                  type="number"
                  min="0"
                  step="0.01"
                />
              </label>

              <label class="span-2">
                <span>Ubicación</span>

                <input
                  v-model="sourceForm.warehouse_location"
                  type="text"
                  placeholder="Pasillo, estante, almacén o referencia"
                />
              </label>

              <label class="span-2">
                <span>Justificación</span>

                <textarea
                  v-model="sourceForm.justification"
                  rows="3"
                  placeholder="Explica por qué se selecciona este origen..."
                />
              </label>

              <label class="check-field span-2">
                <input
                  v-model="sourceForm.is_confirmed"
                  type="checkbox"
                />

                <span>Confirmar este origen</span>
              </label>
            </div>

            <footer>
              <button
                type="button"
                :disabled="actionLoading"
                @click="submitSource"
              >
                {{
                  currentSource
                    ? "Actualizar origen"
                    : "Registrar origen"
                }}
              </button>
            </footer>
          </article>

          <article
            v-if="canCreateWithdrawal"
            class="repair-part-item-detail__card action-card"
          >
            <header>
              <div>
                <span>Etapa 4</span>
                <strong>Crear retiro</strong>
              </div>
            </header>

            <div class="repair-part-item-detail__form-grid">
              <label>
                <span>Cantidad</span>

                <input
                  v-model="withdrawalForm.quantity"
                  type="number"
                  min="0.01"
                  step="0.01"
                />
              </label>

              <label class="span-2">
                <span>Condiciones de autorización</span>

                <textarea
                  v-model="withdrawalForm.authorization_notes"
                  rows="3"
                  placeholder="Condiciones u observaciones..."
                />
              </label>
            </div>

            <footer>
              <button
                type="button"
                :disabled="actionLoading"
                @click="submitWithdrawal"
              >
                Crear retiro
              </button>
            </footer>
          </article>

          <article
            v-if="currentWithdrawal"
            class="repair-part-item-detail__card action-card"
          >
            <header>
              <div>
                <span>Retiro</span>
                <strong>
                  {{ currentWithdrawal.status_name }}
                </strong>
              </div>
            </header>

            <div class="repair-part-item-detail__form-grid">
              <div class="repair-part-item-detail__search span-2">
                <label>
                  <span>Buscar persona autorizada</span>

                  <div>
                    <input
                      v-model="userSearch"
                      type="search"
                      placeholder="Nombre o correo"
                      @keyup.enter="searchUsers"
                    />

                    <button
                      type="button"
                      :disabled="searchingUsers"
                      @click="searchUsers"
                    >
                      Buscar
                    </button>
                  </div>
                </label>

                <select
                  v-model="authorizationForm.authorized_person"
                >
                  <option value="">
                    Seleccionar persona
                  </option>

                  <option
                    v-for="user in userResults"
                    :key="user.id"
                    :value="user.id"
                  >
                    {{ userLabel(user) }}
                  </option>
                </select>
              </div>

              <label>
                <span>Válido hasta</span>

                <input
                  v-model="authorizationForm.valid_until"
                  type="datetime-local"
                />
              </label>

              <label class="span-2">
                <span>Observaciones</span>

                <textarea
                  v-model="authorizationForm.notes"
                  rows="3"
                />
              </label>
            </div>

            <footer class="multiple-actions">
              <button
                v-if="currentWithdrawal.status === 'pending'"
                type="button"
                :disabled="actionLoading"
                @click="authorizeWithdrawal"
              >
                Autorizar retiro
              </button>

              <button
                v-if="
                  [
                    'authorized',
                    'in_progress',
                  ].includes(currentWithdrawal.status)
                "
                type="button"
                :disabled="actionLoading"
                @click="confirmWithdrawal"
              >
                Confirmar retiro
              </button>

              <button
                v-if="currentWithdrawal.status === 'withdrawn'"
                type="button"
                :disabled="actionLoading"
                @click="receiveWithdrawal"
              >
                Confirmar recepción
              </button>
            </footer>
          </article>

          <article
            v-if="canCreateDelivery"
            class="repair-part-item-detail__card action-card"
          >
            <header>
              <div>
                <span>Etapa 5</span>
                <strong>Crear entrega</strong>
              </div>
            </header>

            <div class="repair-part-item-detail__form-grid">
              <label>
                <span>Cantidad</span>

                <input
                  v-model="deliveryForm.quantity"
                  type="number"
                  min="0.01"
                  step="0.01"
                />
              </label>

              <label>
                <span>Documento</span>

                <input
                  v-model="deliveryForm.delivery_document"
                  type="text"
                  placeholder="Guía, vale o documento"
                />
              </label>

              <label class="span-2">
                <span>Observaciones</span>

                <textarea
                  v-model="deliveryForm.notes"
                  rows="3"
                />
              </label>
            </div>

            <footer>
              <button
                type="button"
                :disabled="actionLoading"
                @click="submitDelivery"
              >
                Crear entrega
              </button>
            </footer>
          </article>

          <article
            v-if="currentDelivery"
            class="repair-part-item-detail__card action-card"
          >
            <header>
              <div>
                <span>Entrega</span>
                <strong>
                  {{ currentDelivery.status_name }}
                </strong>
              </div>
            </header>

            <div
              v-if="
                [
                  'ready',
                  'preparing',
                ].includes(currentDelivery.status)
              "
              class="repair-part-item-detail__form-grid"
            >
              <div class="repair-part-item-detail__search span-2">
                <label>
                  <span>Entregar a</span>

                  <div>
                    <input
                      v-model="userSearch"
                      type="search"
                      placeholder="Buscar técnico o usuario"
                      @keyup.enter="searchUsers"
                    />

                    <button
                      type="button"
                      :disabled="searchingUsers"
                      @click="searchUsers"
                    >
                      Buscar
                    </button>
                  </div>
                </label>

                <select
                  v-model="deliveryActionForm.delivered_to"
                >
                  <option value="">
                    Seleccionar usuario
                  </option>

                  <option
                    v-for="user in userResults"
                    :key="user.id"
                    :value="user.id"
                  >
                    {{ userLabel(user) }}
                  </option>
                </select>
              </div>

              <label>
                <span>Cantidad</span>

                <input
                  v-model="deliveryActionForm.quantity"
                  type="number"
                  min="0.01"
                  step="0.01"
                />
              </label>

              <label>
                <span>Documento</span>

                <input
                  v-model="deliveryActionForm.delivery_document"
                  type="text"
                />
              </label>

              <label class="span-2">
                <span>Observaciones</span>

                <textarea
                  v-model="deliveryActionForm.notes"
                  rows="3"
                />
              </label>
            </div>

            <div
              v-if="currentDelivery.status === 'delivered'"
              class="repair-part-item-detail__form-grid"
            >
              <label>
                <span>Cantidad recibida</span>

                <input
                  v-model="receptionForm.received_quantity"
                  type="number"
                  min="0"
                  :max="currentDelivery.quantity"
                  step="0.01"
                />
              </label>

              <label class="span-2">
                <span>Observaciones de recepción</span>

                <textarea
                  v-model="receptionForm.notes"
                  rows="3"
                />
              </label>
            </div>

            <footer class="multiple-actions">
              <button
                v-if="currentDelivery.status === 'pending'"
                type="button"
                :disabled="actionLoading"
                @click="prepareDelivery"
              >
                Preparar entrega
              </button>

              <button
                v-if="
                  [
                    'preparing',
                    'ready',
                  ].includes(currentDelivery.status)
                "
                type="button"
                :disabled="actionLoading"
                @click="deliverPart"
              >
                Registrar entrega
              </button>

              <button
                v-if="currentDelivery.status === 'delivered'"
                type="button"
                :disabled="actionLoading"
                @click="receiveDelivery"
              >
                Confirmar recepción
              </button>
            </footer>
          </article>

          <article
            v-if="canCreateReplacement"
            class="repair-part-item-detail__card action-card"
          >
            <header>
              <div>
                <span>Control posterior</span>
                <strong>Registrar reposición</strong>
              </div>
            </header>

            <div class="repair-part-item-detail__form-grid">
              <label>
                <span>Tipo de reposición</span>

                <select
                  v-model="replacementForm.replacement_type"
                >
                  <option
                    v-for="option in replacementTypeOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </label>

              <label>
                <span>Estado</span>

                <select v-model="replacementForm.status">
                  <option
                    v-for="option in replacementStatusOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </label>

              <label>
                <span>Equipo de origen</span>

                <select
                  v-model="replacementForm.source_equipment"
                >
                  <option value="">
                    Seleccionar equipo
                  </option>

                  <option
                    v-for="equipment in equipmentResults"
                    :key="equipment.id"
                    :value="equipment.id"
                  >
                    {{ equipmentLabel(equipment) }}
                  </option>
                </select>
              </label>

              <label>
                <span>Serie del componente de reposición</span>

                <input
                  v-model="replacementForm.replacement_serial_number"
                  type="text"
                  placeholder="Serie física, cuando corresponda"
                />
              </label>

              <label>
                <span>Responsable</span>

                <select
                  v-model="replacementForm.responsible_user"
                >
                  <option value="">
                    Seleccionar usuario
                  </option>

                  <option
                    v-for="user in userResults"
                    :key="user.id"
                    :value="user.id"
                  >
                    {{ userLabel(user) }}
                  </option>
                </select>
              </label>

              <label>
                <span>Fecha límite</span>

                <input
                  v-model="replacementForm.due_at"
                  type="datetime-local"
                />
              </label>

              <label class="span-2">
                <span>Referencia externa</span>

                <input
                  v-model="replacementForm.external_reference"
                  type="text"
                />
              </label>

              <label class="span-2">
                <span>Observaciones</span>

                <textarea
                  v-model="replacementForm.notes"
                  rows="3"
                />
              </label>
            </div>

            <footer>
              <button
                type="button"
                :disabled="actionLoading"
                @click="submitReplacement"
              >
                Registrar reposición
              </button>
            </footer>
          </article>

          <article
            v-if="currentReplacement"
            class="repair-part-item-detail__card"
          >
            <header>
              <div>
                <span>Reposición</span>
                <strong>
                  {{ currentReplacement.status_name }}
                </strong>
              </div>
            </header>

            <dl>
              <div>
                <dt>Tipo</dt>
                <dd>
                  {{
                    currentReplacement.replacement_type_name
                  }}
                </dd>
              </div>

              <div>
                <dt>Equipo de origen</dt>
                <dd>
                  {{
                    currentReplacement.source_equipment_code ||
                    "No registrado"
                  }}
                </dd>
              </div>

              <div>
                <dt>Responsable</dt>
                <dd>
                  {{
                    currentReplacement.responsible_user_name ||
                    "No registrado"
                  }}
                </dd>
              </div>
            </dl>

            <footer
              v-if="
                currentReplacement.status !==
                'completed'
              "
            >
              <button
                type="button"
                :disabled="actionLoading"
                @click="completeReplacement"
              >
                Completar reposición
              </button>
            </footer>
          </article>
        </div>

        <aside class="repair-part-item-detail__sidebar">
          <article class="repair-part-item-detail__card">
            <header>
              <strong>Datos del ítem</strong>
            </header>

            <dl>
              <div>
                <dt>Tipo</dt>
                <dd>{{ item.item_type_name }}</dd>
              </div>

              <div>
                <dt>Urgencia</dt>
                <dd>{{ item.urgency_name }}</dd>
              </div>

              <div>
                <dt>Ruta</dt>
                <dd>{{ item.approval_route_name }}</dd>
              </div>

              <div>
                <dt>Origen solicitado</dt>
                <dd>{{ item.request_origin_name }}</dd>
              </div>

              <div>
                <dt>Control posterior</dt>
                <dd>{{ item.control_type_name }}</dd>
              </div>

              <div>
                <dt>Reparación</dt>
                <dd>{{ item.repair_code }}</dd>
              </div>
            </dl>
          </article>

          <article class="repair-part-item-detail__card">
            <header>
              <strong>Revisiones</strong>
              <span>{{ reviews.length }}</span>
            </header>

            <div class="repair-part-item-detail__records">
              <article
                v-for="review in reviews"
                :key="review.id"
              >
                <strong>{{ review.result_name }}</strong>
                <small>{{ review.reviewed_by_name }}</small>
                <p>{{ review.justification }}</p>
              </article>

              <p v-if="!reviews.length">
                Sin revisiones registradas.
              </p>
            </div>
          </article>

          <article class="repair-part-item-detail__card">
            <header>
              <strong>Decisiones</strong>
              <span>{{ decisions.length }}</span>
            </header>

            <div class="repair-part-item-detail__records">
              <article
                v-for="decision in decisions"
                :key="decision.id"
              >
                <strong>{{ decision.decision_name }}</strong>
                <small>{{ decision.decided_by_name }}</small>
                <p>
                  Aprobada:
                  {{ decision.approved_quantity }}
                </p>
              </article>

              <p v-if="!decisions.length">
                Sin decisiones registradas.
              </p>
            </div>
          </article>

          <article class="repair-part-item-detail__card">
            <header>
              <strong>Historial</strong>
              <span>{{ history.length }}</span>
            </header>

            <div class="repair-part-item-detail__timeline">
              <article
                v-for="entry in history"
                :key="entry.id"
              >
                <i />

                <div>
                  <strong>{{ entry.event }}</strong>
                  <span>
                    {{
                      entry.previous_status ||
                      "Inicio"
                    }}
                    →
                    {{
                      entry.new_status ||
                      "Sin cambio"
                    }}
                  </span>
                  <small>{{ entry.changed_at }}</small>
                </div>
              </article>

              <p v-if="!history.length">
                Sin movimientos registrados.
              </p>
            </div>
          </article>
        </aside>
      </section>
    </template>

    <section
      v-else
      class="repair-part-item-detail__state"
    >
      No se encontró el ítem.
    </section>
  </main>
</template>