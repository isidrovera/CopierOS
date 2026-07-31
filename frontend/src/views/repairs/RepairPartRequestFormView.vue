<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from "vue"

import {
  useRoute,
  useRouter,
} from "vue-router"

import RentalSearchSelect from "../rentals/components/RentalSearchSelect.vue"

import {
  getEquipmentComponents,
} from "../../services/equipment.service"

import {
  archiveRepairPartRequestItem,
  createRepairPartRequest,
  createRepairPartRequestItem,
  getRepairPartRequest,
  getRepairPartRequestItems,
  getRepairs,
  updateRepairPartRequest,
} from "../../services/repairs.service"

import "./RepairPartRequestFormView.css"


const route = useRoute()
const router = useRouter()

const requestId = computed(() =>
  String(route.params.id || "")
)

const isEdit = computed(() =>
  Boolean(requestId.value)
)

const loading = ref(false)
const saving = ref(false)
const errorMessage = ref("")
const successMessage = ref("")

const selectedRepair = ref(null)
const selectedComponent = ref(null)

const existingItems = ref([])
const pendingItems = ref([])

const showManualEntry = ref(false)

const form = reactive({
  repair: String(route.query.repair || ""),
  title: "",
  description: "",
  technical_justification: "",
  general_observations: "",
  priority: "normal",
  requires_management_approval: true,
  current_responsible_user: null,
})

const itemForm = reactive({
  component: "",
  item_type: "spare_part",
  request_origin: "manual",
  approval_route: "area_manager_review",
  urgency: "normal",
  control_type: "none",
  custom_name: "",
  custom_code: "",
  custom_description: "",
  requested_quantity: 1,
  technical_reason: "",
})

const priorityOptions = [
  ["low", "Baja"],
  ["normal", "Normal"],
  ["high", "Alta"],
  ["urgent", "Urgente"],
  ["critical", "Crítica"],
]

const urgencyOptions = [
  ["normal", "Normal"],
  ["high", "Alta"],
  ["critical", "Crítica"],
]

const itemTypeOptions = [
  ["spare_part", "Repuesto"],
  ["accessory", "Accesorio"],
  ["unit", "Unidad completa"],
  ["subpart", "Subparte"],
  ["consumable", "Consumible"],
  ["toner", "Tóner"],
  ["hdd", "Disco duro"],
  ["power_cable", "Cable de poder"],
  ["base_wheel", "Rueda de base"],
  ["cover", "Tapa"],
  ["panel", "Panel"],
  ["other", "Otro"],
]

const approvalRouteOptions = [
  ["direct_management", "Directa a gerencia"],
  ["area_manager_review", "Revisión previa del jefe de área"],
]

const repairInitialLabel = computed(() => {
  if (!selectedRepair.value) {
    return ""
  }

  return formatRepairLabel(selectedRepair.value)
})

const componentInitialLabel = computed(() => {
  if (!selectedComponent.value) {
    return ""
  }

  return formatComponentLabel(selectedComponent.value)
})

const totalItems = computed(() =>
  existingItems.value.length + pendingItems.value.length
)

const canAddItem = computed(() => {
  const hasComponent = Boolean(itemForm.component)
  const hasCustomName = Boolean(itemForm.custom_name.trim())

  return (
    (hasComponent || hasCustomName) &&
    !(hasComponent && hasCustomName) &&
    Number(itemForm.requested_quantity) > 0 &&
    Boolean(itemForm.technical_reason.trim())
  )
})


function normalizeResults(response) {
  if (Array.isArray(response)) {
    return response
  }

  return Array.isArray(response?.results)
    ? response.results
    : []
}


function formatRepairLabel(repair) {
  const code = repair?.code || "Sin código"

  const equipment =
    repair?.equipment_name ||
    [
      repair?.equipment_brand_name,
      repair?.equipment_model_name,
    ]
      .filter(Boolean)
      .join(" ") ||
    "Equipo sin identificar"

  const serial =
    repair?.equipment_serial_number ||
    "Sin serie"

  return `${code} · ${equipment} · Serie ${serial}`
}


function formatComponentLabel(component) {
  const code = component?.code
    ? `${component.code} · `
    : ""

  return `${code}${component?.name || component?.label || "Componente"}`
}


function getPriorityName(value) {
  return priorityOptions.find(
    option => option[0] === value
  )?.[1] || value
}


function getUrgencyName(value) {
  return urgencyOptions.find(
    option => option[0] === value
  )?.[1] || value
}


function getItemTypeName(value) {
  return itemTypeOptions.find(
    option => option[0] === value
  )?.[1] || value
}


function getApprovalRouteName(value) {
  return approvalRouteOptions.find(
    option => option[0] === value
  )?.[1] || value
}


function buildAutomaticTitle(repair) {
  if (!repair) {
    return ""
  }

  const code = repair.code || "Sin código"

  const equipment =
    repair.equipment_name ||
    [
      repair.equipment_brand_name,
      repair.equipment_model_name,
    ]
      .filter(Boolean)
      .join(" ") ||
    "Equipo"

  return `Solicitud de repuestos - ${code} - ${equipment}`
}


async function searchRepairs(search) {
  const response = await getRepairs({
    search,
    isActive: true,
    includeArchived: false,
    ordering: "-created_at",
  })

  return normalizeResults(response).map(repair => ({
    ...repair,
    label: formatRepairLabel(repair),
    description: [
      repair.status_name,
      repair.assigned_technician_name
        ? `Técnico: ${repair.assigned_technician_name}`
        : "Sin técnico",
    ]
      .filter(Boolean)
      .join(" · "),
  }))
}


async function searchComponents(search) {
  const response = await getEquipmentComponents({
    search,
    includeArchived: false,
    isActive: true,
  })

  return normalizeResults(response).map(component => ({
    ...component,
    label: formatComponentLabel(component),
    description: [
      component.category_name || component.category,
      component.color_name || component.color,
    ]
      .filter(Boolean)
      .join(" · "),
  }))
}


function selectRepair(repair) {
  selectedRepair.value = repair

  if (
    repair &&
    !form.title.trim()
  ) {
    form.title = buildAutomaticTitle(repair)
  }
}


function selectComponent(component) {
  selectedComponent.value = component

  if (component) {
    showManualEntry.value = false
    itemForm.custom_name = ""
    itemForm.custom_code = ""
    itemForm.custom_description = ""
  }
}


function enableManualEntry() {
  selectedComponent.value = null
  itemForm.component = ""
  showManualEntry.value = true
}


function cancelManualEntry() {
  showManualEntry.value = false
  itemForm.custom_name = ""
  itemForm.custom_code = ""
  itemForm.custom_description = ""
}


function clearItemForm() {
  selectedComponent.value = null
  showManualEntry.value = false

  itemForm.component = ""
  itemForm.item_type = "spare_part"
  itemForm.request_origin = "manual"
  itemForm.approval_route = "area_manager_review"
  itemForm.urgency = "normal"
  itemForm.control_type = "none"
  itemForm.custom_name = ""
  itemForm.custom_code = ""
  itemForm.custom_description = ""
  itemForm.requested_quantity = 1
  itemForm.technical_reason = ""
}


function buildPendingItem() {
  return {
    local_id:
      `${Date.now()}-${Math.random().toString(16).slice(2)}`,

    component:
      itemForm.component || null,

    component_name:
      selectedComponent.value?.name ||
      selectedComponent.value?.label ||
      "",

    component_code:
      selectedComponent.value?.code || "",

    item_type:
      itemForm.item_type,

    item_type_name:
      getItemTypeName(itemForm.item_type),

    request_origin:
      itemForm.request_origin,

    approval_route:
      itemForm.approval_route,

    approval_route_name:
      getApprovalRouteName(itemForm.approval_route),

    urgency:
      itemForm.urgency,

    urgency_name:
      getUrgencyName(itemForm.urgency),

    control_type:
      itemForm.control_type,

    custom_name:
      itemForm.component
        ? ""
        : itemForm.custom_name.trim(),

    custom_code:
      itemForm.component
        ? ""
        : itemForm.custom_code.trim(),

    custom_description:
      itemForm.component
        ? ""
        : itemForm.custom_description.trim(),

    requested_quantity:
      Number(itemForm.requested_quantity),

    technical_reason:
      itemForm.technical_reason.trim(),
  }
}


function addPendingItem() {
  errorMessage.value = ""

  if (!canAddItem.value) {
    errorMessage.value =
      "Selecciona un componente o registra un nombre manual, indica una cantidad válida y escribe el motivo técnico."

    return
  }

  pendingItems.value.push(
    buildPendingItem()
  )

  clearItemForm()
}


function removePendingItem(localId) {
  pendingItems.value =
    pendingItems.value.filter(
      item => item.local_id !== localId
    )
}


function increasePendingQuantity(item) {
  item.requested_quantity =
    Number(item.requested_quantity || 0) + 1
}


function decreasePendingQuantity(item) {
  const currentQuantity =
    Number(item.requested_quantity || 0)

  if (currentQuantity <= 1) {
    return
  }

  item.requested_quantity =
    currentQuantity - 1
}


async function archiveExistingItem(item) {
  const itemName =
    item.display_name ||
    item.component_name ||
    item.custom_name ||
    "Ítem"

  const confirmed = window.confirm(
    `¿Quitar el ítem "${itemName}" de la solicitud?`
  )

  if (!confirmed) {
    return
  }

  errorMessage.value = ""

  try {
    await archiveRepairPartRequestItem(
      item.id,
      "Archivado desde el formulario de solicitud."
    )

    existingItems.value =
      existingItems.value.filter(
        current => current.id !== item.id
      )
  } catch (error) {
    errorMessage.value =
      error?.message ||
      "No se pudo archivar el ítem."
  }
}


function applyRequest(data) {
  form.repair = data.repair || ""
  form.title = data.title || ""
  form.description = data.description || ""

  form.technical_justification =
    data.technical_justification || ""

  form.general_observations =
    data.general_observations || ""

  form.priority =
    data.priority || "normal"

  form.requires_management_approval =
    Boolean(data.requires_management_approval)

  form.current_responsible_user =
    data.current_responsible_user || null

  selectedRepair.value = {
    id: data.repair,
    code: data.repair_code,
    equipment_name: data.equipment_name,
    equipment_serial_number:
      data.equipment_serial_number,
    equipment_id: data.equipment_id,
    status_name: data.repair_status_name,
    assigned_technician_name:
      data.assigned_technician_name,
  }
}


async function loadForm() {
  loading.value = true
  errorMessage.value = ""

  try {
    if (!isEdit.value) {
      if (form.repair) {
        const repairs =
          await searchRepairs(form.repair)

        const match = repairs.find(
          repair =>
            String(repair.id) ===
            String(form.repair)
        )

        if (match) {
          selectRepair(match)
        }
      }

      return
    }

    const [
      requestResponse,
      itemsResponse,
    ] = await Promise.all([
      getRepairPartRequest(requestId.value),

      getRepairPartRequestItems({
        request: requestId.value,
      }),
    ])

    applyRequest(requestResponse)

    existingItems.value =
      normalizeResults(itemsResponse)
  } catch (error) {
    errorMessage.value =
      error?.message ||
      "No se pudo cargar la solicitud."
  } finally {
    loading.value = false
  }
}


function validateRequestForm() {
  if (!form.repair) {
    return "Debes seleccionar una reparación."
  }

  if (!form.title.trim()) {
    return "No se pudo generar el título de la solicitud."
  }

  if (!form.technical_justification.trim()) {
    return "La justificación técnica es obligatoria."
  }

  if (
    !existingItems.value.length &&
    !pendingItems.value.length
  ) {
    return "Debes agregar por lo menos un repuesto o parte."
  }

  const invalidItem =
    pendingItems.value.find(item =>
      Number(item.requested_quantity) <= 0 ||
      !String(item.technical_reason || "").trim()
    )

  if (invalidItem) {
    return "Revisa la cantidad y el motivo técnico de los ítems nuevos."
  }

  return ""
}


async function saveItems(savedRequestId) {
  for (const item of pendingItems.value) {
    await createRepairPartRequestItem({
      request: savedRequestId,
      checklist_item: null,
      component: item.component,
      item_type: item.item_type,
      request_origin: item.request_origin,
      approval_route: item.approval_route,
      urgency: item.urgency,
      control_type: item.control_type,
      custom_name: item.custom_name,
      custom_code: item.custom_code,
      custom_description:
        item.custom_description,
      requested_quantity:
        Number(item.requested_quantity),
      technical_reason:
        String(item.technical_reason || "").trim(),
    })
  }
}


async function save() {
  const validationMessage =
    validateRequestForm()

  if (validationMessage) {
    errorMessage.value = validationMessage
    return
  }

  saving.value = true
  errorMessage.value = ""
  successMessage.value = ""

  const payload = {
    repair: form.repair,
    title: form.title.trim(),
    description: form.description.trim(),

    technical_justification:
      form.technical_justification.trim(),

    general_observations:
      form.general_observations.trim(),

    priority: form.priority,

    requires_management_approval:
      form.requires_management_approval,

    current_responsible_user:
      form.current_responsible_user || null,
  }

  try {
    const savedRequest = isEdit.value
      ? await updateRepairPartRequest(
          requestId.value,
          payload
        )
      : await createRepairPartRequest(
          payload
        )

    if (pendingItems.value.length) {
      await saveItems(savedRequest.id)
    }

    successMessage.value =
      "Solicitud guardada correctamente."

    router.push({
      name: "repair-part-request-detail",
      params: {
        id: savedRequest.id,
      },
    })
  } catch (error) {
    errorMessage.value =
      error?.message ||
      "No se pudo guardar la solicitud."
  } finally {
    saving.value = false
  }
}


function cancel() {
  if (isEdit.value) {
    router.push({
      name: "repair-part-request-detail",
      params: {
        id: requestId.value,
      },
    })

    return
  }

  router.push({
    name: "repair-part-requests",
  })
}


onMounted(loadForm)
</script>

<template>
  <main class="repair-part-request-form">
    <header class="repair-part-request-form__page-header">
      <div class="repair-part-request-form__heading">
        <span>Pedidos de repuestos</span>

        <h1>
          {{ isEdit ? "Editar solicitud" : "Nueva solicitud" }}
        </h1>

        <p>
          Registra los repuestos necesarios en una lista rápida
          y editable.
        </p>
      </div>

      <div class="repair-part-request-form__header-actions">
        <button
          type="button"
          class="button-neutral"
          @click="cancel"
        >
          Cancelar
        </button>

        <button
          type="button"
          class="primary"
          :disabled="saving || loading"
          @click="save"
        >
          {{ saving ? "Guardando..." : "Guardar solicitud" }}
        </button>
      </div>
    </header>

    <p
      v-if="errorMessage"
      class="repair-part-request-form__message error"
    >
      {{ errorMessage }}
    </p>

    <p
      v-if="successMessage"
      class="repair-part-request-form__message success"
    >
      {{ successMessage }}
    </p>

    <section
      v-if="loading"
      class="repair-part-request-form__state"
    >
      Cargando solicitud...
    </section>

    <form
      v-else
      class="repair-part-request-form__body"
      @submit.prevent="save"
    >
      <section class="repair-part-request-form__card repair-card">
        <header class="repair-part-request-form__card-header">
          <div>
            <strong>Reparación y equipo</strong>

            <small>
              Selecciona la reparación relacionada con el pedido.
            </small>
          </div>

          <span
            v-if="selectedRepair"
            class="repair-part-request-form__status-badge"
          >
            {{ selectedRepair.status_name || "Activo" }}
          </span>
        </header>

        <RentalSearchSelect
          v-model="form.repair"
          label="Buscar reparación"
          placeholder="Código, serie, marca, modelo o técnico..."
          :loader="searchRepairs"
          :initial-label="repairInitialLabel"
          :required="true"
          :disabled="isEdit"
          @select="selectRepair"
        />

        <article
          v-if="selectedRepair"
          class="repair-part-request-form__repair-summary"
        >
          <div>
            <small>Reparación</small>
            <strong>
              {{ selectedRepair.code || "Sin código" }}
            </strong>
          </div>

          <div class="equipment">
            <small>Equipo</small>
            <strong>
              {{
                selectedRepair.equipment_name ||
                "Equipo sin identificar"
              }}
            </strong>
          </div>

          <div>
            <small>Serie</small>
            <strong>
              {{
                selectedRepair.equipment_serial_number ||
                "Sin serie"
              }}
            </strong>
          </div>

          <div>
            <small>Técnico</small>
            <strong>
              {{
                selectedRepair.assigned_technician_name ||
                "Sin asignar"
              }}
            </strong>
          </div>
        </article>
      </section>

      <section class="repair-part-request-form__card request-summary-card">
        <header class="repair-part-request-form__card-header">
          <div>
            <strong>Motivo de la solicitud</strong>

            <small>
              Indica el diagnóstico general y la prioridad.
            </small>
          </div>

          <span
            class="repair-part-request-form__priority-preview"
            :class="`priority-${form.priority}`"
          >
            {{ getPriorityName(form.priority) }}
          </span>
        </header>

        <div class="repair-part-request-form__request-grid">
          <label class="priority-field">
            <span>Prioridad</span>

            <select v-model="form.priority">
              <option
                v-for="[value, label] in priorityOptions"
                :key="value"
                :value="value"
              >
                {{ label }}
              </option>
            </select>
          </label>

          <label class="justification-field">
            <span>Justificación técnica</span>

            <textarea
              v-model.trim="form.technical_justification"
              placeholder="Describe el diagnóstico y por qué se necesitan los repuestos..."
            />
          </label>
        </div>
      </section>

      <section class="repair-part-request-form__card items-card">
        <header class="repair-part-request-form__card-header">
          <div>
            <strong>Repuestos solicitados</strong>

            <small>
              {{ totalItems }}
              {{ totalItems === 1 ? "ítem registrado" : "ítems registrados" }}
            </small>
          </div>

          <button
            v-if="!showManualEntry"
            type="button"
            class="manual-entry-button"
            @click="enableManualEntry"
          >
            + Repuesto no catalogado
          </button>
        </header>

        <div class="repair-part-request-form__table-wrapper">
          <table class="repair-part-request-form__table">
            <thead>
              <tr>
                <th class="item-column">
                  Repuesto o componente
                </th>

                <th class="code-column">
                  Código
                </th>

                <th class="quantity-column">
                  Cantidad
                </th>

                <th class="reason-column">
                  Motivo técnico
                </th>

                <th class="urgency-column">
                  Urgencia
                </th>

                <th class="status-column">
                  Estado
                </th>

                <th class="action-column">
                  Acción
                </th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="item in existingItems"
                :key="item.id"
                class="saved-row"
              >
                <td>
                  <div class="repair-part-request-form__item-name">
                    <strong>
                      {{
                        item.display_name ||
                        item.component_name ||
                        item.custom_name ||
                        "Ítem sin nombre"
                      }}
                    </strong>

                    <small>
                      {{
                        item.item_type_name ||
                        "Repuesto"
                      }}
                    </small>
                  </div>
                </td>

                <td>
                  <span class="repair-part-request-form__code">
                    {{
                      item.component_code ||
                      item.custom_code ||
                      "—"
                    }}
                  </span>
                </td>

                <td>
                  <span class="repair-part-request-form__saved-value">
                    {{ item.requested_quantity }}
                  </span>
                </td>

                <td>
                  <p class="repair-part-request-form__saved-reason">
                    {{ item.technical_reason || "Sin motivo registrado" }}
                  </p>
                </td>

                <td>
                  <span
                    class="repair-part-request-form__urgency-badge"
                    :class="`urgency-${item.urgency || 'normal'}`"
                  >
                    {{
                      item.urgency_name ||
                      getUrgencyName(item.urgency || "normal")
                    }}
                  </span>
                </td>

                <td>
                  <span class="saved-badge">
                    Guardado
                  </span>
                </td>

                <td>
                  <button
                    type="button"
                    class="icon-button danger"
                    title="Quitar ítem"
                    @click="archiveExistingItem(item)"
                  >
                    ×
                  </button>
                </td>
              </tr>

              <tr
                v-for="item in pendingItems"
                :key="item.local_id"
                class="pending-row"
              >
                <td>
                  <div class="repair-part-request-form__item-name">
                    <strong>
                      {{
                        item.component_name ||
                        item.custom_name ||
                        "Ítem sin nombre"
                      }}
                    </strong>

                    <small>
                      {{ item.item_type_name }}
                    </small>
                  </div>
                </td>

                <td>
                  <span class="repair-part-request-form__code">
                    {{
                      item.component_code ||
                      item.custom_code ||
                      "—"
                    }}
                  </span>
                </td>

                <td>
                  <div class="repair-part-request-form__quantity-control">
                    <button
                      type="button"
                      :disabled="Number(item.requested_quantity) <= 1"
                      @click="decreasePendingQuantity(item)"
                    >
                      −
                    </button>

                    <input
                      v-model.number="item.requested_quantity"
                      type="number"
                      min="0.01"
                      step="0.01"
                    >

                    <button
                      type="button"
                      @click="increasePendingQuantity(item)"
                    >
                      +
                    </button>
                  </div>
                </td>

                <td>
                  <textarea
                    v-model.trim="item.technical_reason"
                    class="repair-part-request-form__table-textarea"
                    placeholder="Motivo del cambio"
                  />
                </td>

                <td>
                  <select
                    v-model="item.urgency"
                    class="repair-part-request-form__table-select"
                  >
                    <option
                      v-for="[value, label] in urgencyOptions"
                      :key="value"
                      :value="value"
                    >
                      {{ label }}
                    </option>
                  </select>
                </td>

                <td>
                  <span class="pending-badge">
                    Nuevo
                  </span>
                </td>

                <td>
                  <button
                    type="button"
                    class="icon-button danger"
                    title="Quitar ítem"
                    @click="removePendingItem(item.local_id)"
                  >
                    ×
                  </button>
                </td>
              </tr>

              <tr class="new-item-row">
                <td>
                  <div
                    v-if="!showManualEntry"
                    class="repair-part-request-form__component-search"
                  >
                    <RentalSearchSelect
                      v-model="itemForm.component"
                      label=""
                      placeholder="Buscar componente..."
                      :loader="searchComponents"
                      :initial-label="componentInitialLabel"
                      @select="selectComponent"
                    />
                  </div>

                  <div
                    v-else
                    class="repair-part-request-form__manual-fields"
                  >
                    <input
                      v-model.trim="itemForm.custom_name"
                      type="text"
                      placeholder="Nombre del repuesto"
                    >

                    <input
                      v-model.trim="itemForm.custom_description"
                      type="text"
                      placeholder="Descripción opcional"
                    >
                  </div>
                </td>

                <td>
                  <span
                    v-if="!showManualEntry"
                    class="repair-part-request-form__code preview"
                  >
                    {{ selectedComponent?.code || "Automático" }}
                  </span>

                  <input
                    v-else
                    v-model.trim="itemForm.custom_code"
                    type="text"
                    placeholder="Código"
                  >
                </td>

                <td>
                  <div class="repair-part-request-form__quantity-control">
                    <button
                      type="button"
                      :disabled="Number(itemForm.requested_quantity) <= 1"
                      @click="
                        itemForm.requested_quantity =
                          Math.max(
                            1,
                            Number(itemForm.requested_quantity || 1) - 1
                          )
                      "
                    >
                      −
                    </button>

                    <input
                      v-model.number="itemForm.requested_quantity"
                      type="number"
                      min="0.01"
                      step="0.01"
                    >

                    <button
                      type="button"
                      @click="
                        itemForm.requested_quantity =
                          Number(itemForm.requested_quantity || 0) + 1
                      "
                    >
                      +
                    </button>
                  </div>
                </td>

                <td>
                  <textarea
                    v-model.trim="itemForm.technical_reason"
                    class="repair-part-request-form__table-textarea"
                    placeholder="¿Por qué se necesita?"
                  />
                </td>

                <td>
                  <select
                    v-model="itemForm.urgency"
                    class="repair-part-request-form__table-select"
                  >
                    <option
                      v-for="[value, label] in urgencyOptions"
                      :key="value"
                      :value="value"
                    >
                      {{ label }}
                    </option>
                  </select>
                </td>

                <td>
                  <span class="draft-badge">
                    Por agregar
                  </span>
                </td>

                <td>
                  <button
                    type="button"
                    class="icon-button add"
                    title="Agregar línea"
                    :disabled="!canAddItem"
                    @click="addPendingItem"
                  >
                    +
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          v-if="showManualEntry"
          class="repair-part-request-form__manual-notice"
        >
          <div>
            <strong>Registro manual activo</strong>

            <small>
              Escribe el nombre del repuesto que no aparece
              en el catálogo.
            </small>
          </div>

          <button
            type="button"
            @click="cancelManualEntry"
          >
            Volver al catálogo
          </button>
        </div>

        <div
          v-if="!existingItems.length && !pendingItems.length"
          class="repair-part-request-form__empty-hint"
        >
          Usa la última fila para buscar y agregar el primer repuesto.
        </div>
      </section>

      <section class="repair-part-request-form__card observations-card">
        <details>
          <summary>
            Información adicional
          </summary>

          <div class="repair-part-request-form__additional-grid">
            <label>
              <span>Descripción general</span>

              <textarea
                v-model.trim="form.description"
                placeholder="Descripción opcional de la solicitud"
              />
            </label>

            <label>
              <span>Observaciones generales</span>

              <textarea
                v-model.trim="form.general_observations"
                placeholder="Información adicional para almacén, jefe de área o gerencia"
              />
            </label>
          </div>
        </details>
      </section>

      <footer class="repair-part-request-form__footer">
        <div class="repair-part-request-form__footer-summary">
          <strong>
            {{ totalItems }}
            {{ totalItems === 1 ? "repuesto" : "repuestos" }}
          </strong>

          <span>
            Prioridad {{ getPriorityName(form.priority) }}
          </span>
        </div>

        <div class="repair-part-request-form__footer-actions">
          <button
            type="button"
            @click="cancel"
          >
            Cancelar
          </button>

          <button
            type="submit"
            class="primary"
            :disabled="saving"
          >
            {{ saving ? "Guardando..." : "Guardar solicitud" }}
          </button>
        </div>
      </footer>
    </form>
  </main>
</template>