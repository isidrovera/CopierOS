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

import {
  createServiceOrder,
  getServiceEquipmentOptions,
  getServiceOrder,
  updateServiceOrder,
} from "../../services/services.service"

import {
  getUsers,
} from "../../services/users.service"

import ServiceSearchSelect from "./ServiceSearchSelect.vue"
import ServicesTabs from "./ServicesTabs.vue"

import {
  SERVICE_ORIGIN_OPTIONS,
  SERVICE_PRIORITY_OPTIONS,
  SERVICE_STATUS_OPTIONS,
  SERVICE_TYPE_OPTIONS,
  applyEquipmentSnapshot,
  buildServiceOrderPayload,
  clearEquipmentSelection,
  createEmptyServiceOrderForm,
  hydrateServiceOrderForm,
  normalizeCollection,
  normalizeEquipmentOptions,
} from "./service-lookups"

import "./services-form.css"


const route = useRoute()
const router = useRouter()


const loading = ref(false)
const saving = ref(false)
const equipmentLoading = ref(false)
const technicianLoading = ref(false)

const error = ref("")
const success = ref("")

const equipmentOptions = ref([])
const technicianOptions = ref([])

const selectedEquipment = ref(null)
const selectedTechnician = ref(null)

const form = reactive(
  createEmptyServiceOrderForm(),
)


const isEditing = computed(
  () => Boolean(route.params.id),
)


const pageTitle = computed(
  () => (
    isEditing.value
      ? "Editar orden de servicio"
      : "Nueva orden de servicio"
  ),
)


const equipmentHelpText = computed(() => {
  if (
    form.service_origin === "rental"
  ) {
    return (
      "Solo aparecen máquinas de alquiler "
      + "instaladas, activas o pendientes de retiro."
    )
  }

  return (
    "Solo aparecen máquinas externas "
    + "registradas para servicio técnico."
  )
})


const selectedOriginDescription = computed(
  () => (
    SERVICE_ORIGIN_OPTIONS.find(
      (option) => (
        option.value === form.service_origin
      ),
    )?.description || ""
  ),
)


function resetMessages() {
  error.value = ""
  success.value = ""
}


function getRequestError(requestError) {
  return (
    requestError?.message
    || "Ocurrió un error al procesar la solicitud."
  )
}


function assignFormValues(newForm) {
  Object.keys(form).forEach(
    (fieldName) => {
      form[fieldName] = (
        newForm[fieldName]
        ?? form[fieldName]
      )
    },
  )
}


function createEquipmentFromOrder(order) {
  if (!order?.equipment) {
    return null
  }

  return {
    id: order.equipment,
    equipment: order.equipment,
    serial_number: (
      order.equipment_serial_number || ""
    ),
    internal_code: (
      order.equipment_internal_code || ""
    ),
    brand_name: (
      order.equipment_brand_name || ""
    ),
    model_name: (
      order.equipment_model_name || ""
    ),
    family_name: (
      order.equipment_family_name || ""
    ),
    service_origin: (
      order.service_origin || "rental"
    ),
    label: [
      order.equipment_serial_number,
      [
        order.equipment_brand_name,
        order.equipment_model_name,
      ]
        .filter(Boolean)
        .join(" "),
      order.customer_name,
      order.branch_name,
    ]
      .filter(Boolean)
      .join(" · "),
    snapshot: {
      customer_code: (
        order.customer_code || ""
      ),
      customer_document_type: (
        order.customer_document_type || ""
      ),
      customer_document_number: (
        order.customer_document_number || ""
      ),
      customer_name: (
        order.customer_name || ""
      ),
      customer_trade_name: (
        order.customer_trade_name || ""
      ),
      branch_name: (
        order.branch_name || ""
      ),
      address: (
        order.address || ""
      ),
      address_reference: (
        order.address_reference || ""
      ),
      district: (
        order.district || ""
      ),
      province: (
        order.province || ""
      ),
      region: (
        order.region || ""
      ),
      destination_latitude: (
        order.destination_latitude
      ),
      destination_longitude: (
        order.destination_longitude
      ),
      site_location: (
        order.site_location || ""
      ),
      contact_name: (
        order.contact_name || ""
      ),
      contact_job_title: (
        order.contact_job_title || ""
      ),
      contact_phone: (
        order.contact_phone || ""
      ),
      contact_email: (
        order.contact_email || ""
      ),
      contract_reference: (
        order.contract_reference || ""
      ),
      rental_assignment_reference: (
        order.rental_assignment_reference || ""
      ),
    },
  }
}


function normalizeTechnicianOption(user) {
  const fullName = (
    user.full_name
    || [
      user.first_name,
      user.last_name,
    ]
      .filter(Boolean)
      .join(" ")
    || user.username
    || user.email
    || "Usuario"
  )

  return {
    ...user,
    id: user.id,
    label: fullName,
    subtitle: (
      user.email
      || user.username
      || ""
    ),
    meta: (
      user.job_title
      || user.position
      || "Técnico"
    ),
  }
}


async function searchEquipment(search = "") {
  equipmentLoading.value = true

  try {
    const response = await getServiceEquipmentOptions({
      serviceOrigin: form.service_origin,
      search,
    })

    equipmentOptions.value = (
      normalizeEquipmentOptions(response)
    )
  } catch (requestError) {
    error.value = getRequestError(
      requestError,
    )

    equipmentOptions.value = []
  } finally {
    equipmentLoading.value = false
  }
}


async function searchTechnicians(search = "") {
  technicianLoading.value = true

  try {
    const response = await getUsers({
      search,
      is_active: true,
    })

    technicianOptions.value = (
      normalizeCollection(response)
        .filter(
          (user) => (
            user.is_active !== false
          ),
        )
        .map(normalizeTechnicianOption)
    )
  } catch (requestError) {
    error.value = getRequestError(
      requestError,
    )

    technicianOptions.value = []
  } finally {
    technicianLoading.value = false
  }
}


function handleEquipmentSelected(option) {
  resetMessages()

  selectedEquipment.value = option

  applyEquipmentSnapshot(
    form,
    option,
  )
}


function handleEquipmentCleared() {
  selectedEquipment.value = null

  clearEquipmentSelection(form)
}


function handleTechnicianSelected(option) {
  selectedTechnician.value = option
  form.assigned_technician = option?.id || ""
}


function handleTechnicianCleared() {
  selectedTechnician.value = null
  form.assigned_technician = ""
}


async function changeServiceOrigin(origin) {
  if (
    form.service_origin === origin
  ) {
    return
  }

  form.service_origin = origin

  handleEquipmentCleared()

  equipmentOptions.value = []

  await searchEquipment("")
}


async function loadOrder() {
  if (!isEditing.value) {
    await Promise.all([
      searchEquipment(""),
      searchTechnicians(""),
    ])

    return
  }

  loading.value = true
  resetMessages()

  try {
    const order = await getServiceOrder(
      route.params.id,
    )

    assignFormValues(
      hydrateServiceOrderForm(order),
    )

    selectedEquipment.value = (
      createEquipmentFromOrder(order)
    )

    if (selectedEquipment.value) {
      equipmentOptions.value = [
        selectedEquipment.value,
      ]
    }

    if (order.assigned_technician) {
      selectedTechnician.value = {
        id: order.assigned_technician,
        label: (
          order.technician_display
          || "Técnico asignado"
        ),
        subtitle: "",
        meta: "",
      }

      technicianOptions.value = [
        selectedTechnician.value,
      ]
    }

    await Promise.all([
      searchEquipment(""),
      searchTechnicians(""),
    ])
  } catch (requestError) {
    error.value = getRequestError(
      requestError,
    )
  } finally {
    loading.value = false
  }
}


async function submitForm() {
  resetMessages()

  if (!form.equipment) {
    error.value = (
      "Debe seleccionar una máquina."
    )

    return
  }

  if (!form.reported_problem.trim()) {
    error.value = (
      "Debe registrar el problema reportado."
    )

    return
  }

  saving.value = true

  try {
    const payload = (
      buildServiceOrderPayload(form)
    )

    const result = isEditing.value
      ? await updateServiceOrder(
          route.params.id,
          payload,
        )
      : await createServiceOrder(
          payload,
        )

    success.value = (
      `La orden ${result.code} `
      + "se guardó correctamente."
    )

    await router.push({
      name: "service-order-detail",
      params: {
        id: result.id,
      },
    })
  } catch (requestError) {
    error.value = getRequestError(
      requestError,
    )
  } finally {
    saving.value = false
  }
}


watch(
  () => form.status,
  (statusValue) => {
    if (
      statusValue === "assigned"
      && !form.assigned_technician
    ) {
      error.value = (
        "Para guardar la OS como asignada, "
        + "debe seleccionar un técnico."
      )
    }
  },
)


onMounted(loadOrder)
</script>


<template>
  <section class="service-form-page">
    <header class="services-header">
      <div>
        <span class="page-kicker">
          Órdenes de servicio
        </span>

        <h2>
          {{ pageTitle }}
        </h2>

        <p>
          El número de OS será generado automáticamente
          por el sistema.
        </p>
      </div>

      <button
        class="secondary-button"
        type="button"
        @click="
          router.push({
            name: 'service-orders',
          })
        "
      >
        Volver
      </button>
    </header>

    <ServicesTabs />

    <p
      v-if="error"
      class="message error-message"
    >
      {{ error }}
    </p>

    <p
      v-if="success"
      class="message success-message"
    >
      {{ success }}
    </p>

    <div
      v-if="loading"
      class="loading-card"
    >
      <span class="spinner" />

      Cargando orden...
    </div>

    <form
      v-else
      class="service-form"
      @submit.prevent="submitForm"
    >
      <section class="form-card">
        <div class="form-card-header">
          <div>
            <span class="card-kicker">
              Origen de atención
            </span>

            <h3>
              ¿De dónde proviene la máquina?
            </h3>

            <p>
              {{ selectedOriginDescription }}
            </p>
          </div>
        </div>

        <div class="service-origin-options">
          <button
            v-for="origin in SERVICE_ORIGIN_OPTIONS"
            :key="origin.value"
            type="button"
            class="service-origin-option"
            :class="{
              'service-origin-option--active': (
                form.service_origin
                === origin.value
              ),
            }"
            @click="
              changeServiceOrigin(
                origin.value,
              )
            "
          >
            <span class="service-origin-option__icon">
              <svg
                v-if="origin.value === 'rental'"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M3 21V3h12v6h6v12h-2v-2h-2v2H3Zm2-2h2v-2H5v2Zm0-4h2v-2H5v2Zm0-4h2V9H5v2Zm0-4h2V5H5v2Zm4 12h2v-2H9v2Zm0-4h2v-2H9v2Zm0-4h2V9H9v2Zm0-4h2V5H9v2Zm4 12h2v-2h-2v2Zm0-4h2v-2h-2v2Zm0-4h2V9h-2v2Zm4 6h2v-2h-2v2Zm0-4h2v-2h-2v2Z"
                />
              </svg>

              <svg
                v-else
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M4 3h10a3 3 0 0 1 3 3v2h-2V6a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-2h2v2a3 3 0 0 1-3 3H4a3 3 0 0 1-3-3V6a3 3 0 0 1 3-3Zm14.6 5.6L23 13l-4.4 4.4-1.4-1.4 2-2H9v-2h10.2l-2-2 1.4-1.4Z"
                />
              </svg>
            </span>

            <span>
              <strong>
                {{ origin.label }}
              </strong>

              <small>
                {{ origin.description }}
              </small>
            </span>
          </button>
        </div>
      </section>

      <section class="form-card">
        <div class="form-card-header">
          <div>
            <span class="card-kicker">
              Identificación
            </span>

            <h3>
              Orden y máquina
            </h3>
          </div>

          <span class="automatic-code-badge">
            {{ form.code || "OS automática" }}
          </span>
        </div>

        <div class="form-grid">
          <ServiceSearchSelect
            v-model="form.equipment"
            :selected="selectedEquipment"
            :options="equipmentOptions"
            label="Máquina / serie"
            placeholder="Buscar máquina"
            search-placeholder="Serie, código, marca, modelo, cliente o sede"
            :help-text="equipmentHelpText"
            :loading="equipmentLoading"
            required
            option-value="equipment"
            @search="searchEquipment"
            @select="handleEquipmentSelected"
            @clear="handleEquipmentCleared"
          />

          <label>
            <span>
              Tipo de servicio *
            </span>

            <select
              v-model="form.service_type"
              required
            >
              <option
                v-for="option in SERVICE_TYPE_OPTIONS"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </label>

          <label>
            <span>
              Prioridad *
            </span>

            <select
              v-model="form.priority"
              required
            >
              <option
                v-for="option in SERVICE_PRIORITY_OPTIONS"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </label>

          <label>
            <span>
              Estado
            </span>

            <select v-model="form.status">
              <option
                v-for="option in SERVICE_STATUS_OPTIONS"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </label>

          <label>
            <span>
              Fecha solicitada
            </span>

            <input
              v-model="form.requested_at"
              type="datetime-local"
            >
          </label>

          <label>
            <span>
              Fecha programada
            </span>

            <input
              v-model="form.scheduled_at"
              type="datetime-local"
            >
          </label>

          <ServiceSearchSelect
            v-model="form.assigned_technician"
            :selected="selectedTechnician"
            :options="technicianOptions"
            label="Técnico responsable"
            placeholder="Buscar técnico"
            search-placeholder="Nombre, usuario o correo"
            :loading="technicianLoading"
            option-value="id"
            option-subtitle="subtitle"
            option-meta="meta"
            @search="searchTechnicians"
            @select="handleTechnicianSelected"
            @clear="handleTechnicianCleared"
          />

          <label class="full-field">
            <span>
              Problema reportado *
            </span>

            <textarea
              v-model.trim="form.reported_problem"
              required
              rows="4"
              placeholder="Describe claramente la falla o solicitud del cliente"
            />
          </label>
        </div>
      </section>

      <section class="form-card snapshot-card">
        <div class="form-card-header">
          <div>
            <span class="card-kicker">
              Datos de atención
            </span>

            <h3>
              Cliente, sede y contacto
            </h3>

            <p>
              La información se carga automáticamente al
              seleccionar la máquina.
            </p>
          </div>
        </div>

        <div
          v-if="!form.equipment"
          class="snapshot-empty"
        >
          Selecciona una máquina para cargar el cliente,
          sede, dirección y contacto.
        </div>

        <div
          v-else
          class="form-grid"
        >
          <label>
            <span>Cliente</span>

            <input
              v-model="form.customer_name"
              readonly
            >
          </label>

          <label>
            <span>RUC / documento</span>

            <input
              v-model="form.customer_document_number"
              readonly
            >
          </label>

          <label>
            <span>Sede</span>

            <input
              v-model="form.branch_name"
              readonly
            >
          </label>

          <label class="full-field">
            <span>Dirección</span>

            <input
              v-model="form.address"
              readonly
            >
          </label>

          <label>
            <span>Referencia</span>

            <input
              v-model="form.address_reference"
              readonly
            >
          </label>

          <label>
            <span>Ubicación interna</span>

            <input
              v-model="form.site_location"
              readonly
            >
          </label>

          <label>
            <span>Distrito</span>

            <input
              v-model="form.district"
              readonly
            >
          </label>

          <label>
            <span>Provincia</span>

            <input
              v-model="form.province"
              readonly
            >
          </label>

          <label>
            <span>Región</span>

            <input
              v-model="form.region"
              readonly
            >
          </label>

          <label>
            <span>Contacto</span>

            <input
              v-model="form.contact_name"
              readonly
            >
          </label>

          <label>
            <span>Cargo</span>

            <input
              v-model="form.contact_job_title"
              readonly
            >
          </label>

          <label>
            <span>Teléfono</span>

            <input
              v-model="form.contact_phone"
              readonly
            >
          </label>

          <label>
            <span>Correo</span>

            <input
              v-model="form.contact_email"
              readonly
            >
          </label>

          <label
            v-if="form.service_origin === 'rental'"
          >
            <span>Contrato</span>

            <input
              v-model="form.contract_reference"
              readonly
            >
          </label>

          <label
            v-if="form.service_origin === 'rental'"
          >
            <span>Asignación</span>

            <input
              v-model="form.rental_assignment_reference"
              readonly
            >
          </label>
        </div>
      </section>

      <footer class="form-actions">
        <button
          class="secondary-button"
          type="button"
          @click="
            router.push({
              name: 'service-orders',
            })
          "
        >
          Cancelar
        </button>

        <button
          class="primary-button"
          type="submit"
          :disabled="saving"
        >
          {{
            saving
              ? "Guardando..."
              : "Guardar orden"
          }}
        </button>
      </footer>
    </form>
  </section>
</template>