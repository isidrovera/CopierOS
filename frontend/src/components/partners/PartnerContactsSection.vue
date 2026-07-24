<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue"

import {
  archiveContact,
  createContact,
  getContacts,
  restoreContact,
  updateContact,
} from "../../services/partners.service"


const props = defineProps({
  partnerId: {
    type: String,
    required: true,
  },

  branches: {
    type: Array,
    default: () => [],
  },
})


const emit = defineEmits([
  "updated",
])


const contacts = ref([])
const loading = ref(false)
const saving = ref(false)
const processingId = ref("")

const includeArchived = ref(false)

const modalOpen = ref(false)
const editingContactId = ref("")

const errorMessage = ref("")
const successMessage = ref("")


const documentTypeOptions = [
  {
    value: "",
    label: "Sin documento",
  },
  {
    value: "dni",
    label: "DNI",
  },
  {
    value: "foreign_id",
    label: "Documento extranjero",
  },
  {
    value: "passport",
    label: "Pasaporte",
  },
  {
    value: "other",
    label: "Otro documento",
  },
]


const areaOptions = [
  {
    value: "management",
    label: "Gerencia",
  },
  {
    value: "administration",
    label: "Administración",
  },
  {
    value: "accounting",
    label: "Contabilidad",
  },
  {
    value: "billing",
    label: "Facturación",
  },
  {
    value: "treasury",
    label: "Tesorería",
  },
  {
    value: "collections",
    label: "Cobranzas",
  },
  {
    value: "purchasing",
    label: "Compras",
  },
  {
    value: "logistics",
    label: "Logística",
  },
  {
    value: "systems",
    label: "Sistemas",
  },
  {
    value: "technical",
    label: "Área técnica",
  },
  {
    value: "operations",
    label: "Operaciones",
  },
  {
    value: "human_resources",
    label: "Recursos humanos",
  },
  {
    value: "legal",
    label: "Área legal",
  },
  {
    value: "commercial",
    label: "Área comercial",
  },
  {
    value: "other",
    label: "Otra área",
  },
]


const contactMethodOptions = [
  {
    value: "email",
    label: "Correo electrónico",
  },
  {
    value: "phone",
    label: "Teléfono",
  },
  {
    value: "mobile",
    label: "Celular",
  },
  {
    value: "whatsapp",
    label: "WhatsApp",
  },
]


function emptyForm() {
  return {
    branch: "",

    document_type: "",
    document_number: "",

    first_names: "",
    paternal_last_name: "",
    maternal_last_name: "",

    job_title: "",
    area: "other",

    primary_email: "",
    secondary_email: "",

    work_phone: "",
    work_extension: "",

    primary_mobile: "",
    secondary_mobile: "",

    whatsapp_number: "",
    has_whatsapp: false,

    is_primary: false,
    is_legal_representative: false,
    is_branch_manager: false,

    receives_contracts: false,
    receives_billing: false,
    receives_collections: false,
    receives_purchase_orders: false,
    receives_delivery_documents: false,
    receives_meter_requests: false,
    receives_service_notifications: false,
    receives_incident_notifications: false,
    receives_commercial_notifications: false,

    can_authorize_equipment_entry: false,
    can_authorize_equipment_removal: false,
    can_sign_documents: false,

    preferred_contact_method: "email",
    contact_schedule: "",

    is_active: true,
    notes: "",
  }
}


const form = reactive(
  emptyForm()
)


const modalTitle = computed(() => {
  return editingContactId.value
    ? "Editar contacto"
    : "Nuevo contacto"
})


const totalContacts = computed(() => {
  return contacts.value.length
})


const activeContacts = computed(() => {
  return contacts.value.filter(
    (contact) => (
      contact.is_active &&
      !contact.is_archived
    )
  ).length
})


const archivedContacts = computed(() => {
  return contacts.value.filter(
    (contact) => contact.is_archived
  ).length
})


const primaryContacts = computed(() => {
  return contacts.value.filter(
    (contact) => (
      contact.is_primary &&
      contact.is_active &&
      !contact.is_archived
    )
  ).length
})


const availableBranches = computed(() => {
  return props.branches.filter(
    (branch) => (
      branch.is_active &&
      !branch.is_archived
    )
  )
})


function normalizeText(value) {
  return typeof value === "string"
    ? value.trim()
    : value
}


function resetForm() {
  Object.assign(
    form,
    emptyForm()
  )

  editingContactId.value = ""
  errorMessage.value = ""
}


function getContactName(contact) {
  return (
    contact.full_name ||
    [
      contact.first_names,
      contact.paternal_last_name,
      contact.maternal_last_name,
    ]
      .filter(Boolean)
      .join(" ")
      .trim() ||
    "Contacto sin nombre"
  )
}


function getAreaName(value) {
  return (
    areaOptions.find(
      (option) => option.value === value
    )?.label ||
    "Otra área"
  )
}


function getBranchName(contact) {
  return (
    contact.branch_name ||
    props.branches.find(
      (branch) => branch.id === contact.branch
    )?.name ||
    "Contacto general"
  )
}


function getPreferredMethodName(value) {
  return (
    contactMethodOptions.find(
      (option) => option.value === value
    )?.label ||
    "Sin preferencia"
  )
}


function getAvailableContact(contact) {
  return (
    contact.primary_email ||
    contact.primary_mobile ||
    contact.whatsapp_number ||
    contact.work_phone ||
    "Sin datos de contacto"
  )
}


function getNotificationRoles(contact) {
  if (
    Array.isArray(
      contact.notification_roles
    )
  ) {
    return contact.notification_roles
  }

  const roles = []

  if (contact.receives_contracts) {
    roles.push("Contratos")
  }

  if (contact.receives_billing) {
    roles.push("Facturación")
  }

  if (contact.receives_collections) {
    roles.push("Cobranzas")
  }

  if (contact.receives_purchase_orders) {
    roles.push("Órdenes de compra")
  }

  if (contact.receives_delivery_documents) {
    roles.push("Guías y entregas")
  }

  if (contact.receives_meter_requests) {
    roles.push("Contadores")
  }

  if (contact.receives_service_notifications) {
    roles.push("Servicio técnico")
  }

  if (contact.receives_incident_notifications) {
    roles.push("Incidencias")
  }

  if (contact.receives_commercial_notifications) {
    roles.push("Comercial")
  }

  return roles
}


function getStatusName(contact) {
  if (contact.is_archived) {
    return "Archivado"
  }

  return contact.is_active
    ? "Activo"
    : "Inactivo"
}


function getStatusClass(contact) {
  if (contact.is_archived) {
    return "archived"
  }

  return contact.is_active
    ? "active"
    : "inactive"
}


function buildPayload() {
  return {
    partner: props.partnerId,

    branch:
      form.branch || null,

    document_type:
      form.document_type,

    document_number:
      normalizeText(
        form.document_number
      )
        .replace(/\s+/g, "")
        .toUpperCase(),

    first_names:
      normalizeText(
        form.first_names
      ),

    paternal_last_name:
      normalizeText(
        form.paternal_last_name
      ),

    maternal_last_name:
      normalizeText(
        form.maternal_last_name
      ),

    job_title:
      normalizeText(
        form.job_title
      ),

    area:
      form.area,

    primary_email:
      normalizeText(
        form.primary_email
      ).toLowerCase(),

    secondary_email:
      normalizeText(
        form.secondary_email
      ).toLowerCase(),

    work_phone:
      normalizeText(
        form.work_phone
      ),

    work_extension:
      normalizeText(
        form.work_extension
      ),

    primary_mobile:
      normalizeText(
        form.primary_mobile
      ),

    secondary_mobile:
      normalizeText(
        form.secondary_mobile
      ),

    whatsapp_number:
      normalizeText(
        form.whatsapp_number
      ),

    has_whatsapp:
      form.has_whatsapp,

    is_primary:
      form.is_primary,

    is_legal_representative:
      form.is_legal_representative,

    is_branch_manager:
      form.is_branch_manager,

    receives_contracts:
      form.receives_contracts,

    receives_billing:
      form.receives_billing,

    receives_collections:
      form.receives_collections,

    receives_purchase_orders:
      form.receives_purchase_orders,

    receives_delivery_documents:
      form.receives_delivery_documents,

    receives_meter_requests:
      form.receives_meter_requests,

    receives_service_notifications:
      form.receives_service_notifications,

    receives_incident_notifications:
      form.receives_incident_notifications,

    receives_commercial_notifications:
      form.receives_commercial_notifications,

    can_authorize_equipment_entry:
      form.can_authorize_equipment_entry,

    can_authorize_equipment_removal:
      form.can_authorize_equipment_removal,

    can_sign_documents:
      form.can_sign_documents,

    preferred_contact_method:
      form.preferred_contact_method,

    contact_schedule:
      normalizeText(
        form.contact_schedule
      ),

    is_active:
      form.is_active,

    notes:
      normalizeText(
        form.notes
      ),
  }
}


function hasEmailNotification() {
  return (
    form.receives_contracts ||
    form.receives_billing ||
    form.receives_collections ||
    form.receives_purchase_orders ||
    form.receives_delivery_documents ||
    form.receives_meter_requests ||
    form.receives_service_notifications ||
    form.receives_incident_notifications ||
    form.receives_commercial_notifications
  )
}


function validateForm() {
  if (!form.first_names.trim()) {
    return "Los nombres del contacto son obligatorios."
  }

  if (
    form.document_type &&
    !form.document_number.trim()
  ) {
    return (
      "Ingresa el número de documento del contacto."
    )
  }

  if (
    form.document_number.trim() &&
    !form.document_type
  ) {
    return (
      "Selecciona el tipo de documento del contacto."
    )
  }

  if (
    form.document_type === "dni" &&
    !/^\d{8}$/.test(
      form.document_number.trim()
    )
  ) {
    return (
      "El DNI del contacto debe contener " +
      "exactamente 8 números."
    )
  }

  if (
    form.is_branch_manager &&
    !form.branch
  ) {
    return (
      "Para marcarlo como responsable de sede " +
      "debes seleccionar una sucursal."
    )
  }

  if (
    form.has_whatsapp &&
    !form.whatsapp_number.trim()
  ) {
    return (
      "Ingresa el número de WhatsApp."
    )
  }

  if (
    form.preferred_contact_method === "email" &&
    !form.primary_email.trim()
  ) {
    return (
      "Ingresa un correo principal para usarlo " +
      "como medio de contacto preferido."
    )
  }

  if (
    form.preferred_contact_method === "phone" &&
    !form.work_phone.trim()
  ) {
    return (
      "Ingresa un teléfono de trabajo para usarlo " +
      "como medio de contacto preferido."
    )
  }

  if (
    form.preferred_contact_method === "mobile" &&
    !form.primary_mobile.trim()
  ) {
    return (
      "Ingresa un celular principal para usarlo " +
      "como medio de contacto preferido."
    )
  }

  if (
    form.preferred_contact_method === "whatsapp" &&
    !form.whatsapp_number.trim()
  ) {
    return (
      "Ingresa un número de WhatsApp para usarlo " +
      "como medio de contacto preferido."
    )
  }

  if (
    hasEmailNotification() &&
    !form.primary_email.trim()
  ) {
    return (
      "El contacto recibirá comunicaciones, " +
      "por lo que debe tener un correo principal."
    )
  }

  return ""
}


async function loadContacts() {
  loading.value = true
  errorMessage.value = ""

  try {
    const response = await getContacts({
      partner: props.partnerId,
      includeArchived:
        includeArchived.value,
    })

    contacts.value = Array.isArray(response)
      ? response
      : response?.results || []
  } catch (error) {
    contacts.value = []

    errorMessage.value =
      error.message ||
      "No se pudieron cargar los contactos."
  } finally {
    loading.value = false
  }
}


function openCreateModal() {
  resetForm()
  modalOpen.value = true
}


function openEditModal(contact) {
  resetForm()

  editingContactId.value =
    contact.id

  for (
    const field of Object.keys(form)
  ) {
    if (
      Object.prototype.hasOwnProperty.call(
        contact,
        field
      )
    ) {
      form[field] =
        contact[field] ?? form[field]
    }
  }

  form.branch =
    contact.branch || ""

  form.is_active =
    Boolean(contact.is_active)

  form.has_whatsapp =
    Boolean(contact.has_whatsapp)

  form.is_primary =
    Boolean(contact.is_primary)

  form.is_legal_representative =
    Boolean(
      contact.is_legal_representative
    )

  form.is_branch_manager =
    Boolean(
      contact.is_branch_manager
    )

  form.receives_contracts =
    Boolean(contact.receives_contracts)

  form.receives_billing =
    Boolean(contact.receives_billing)

  form.receives_collections =
    Boolean(contact.receives_collections)

  form.receives_purchase_orders =
    Boolean(
      contact.receives_purchase_orders
    )

  form.receives_delivery_documents =
    Boolean(
      contact.receives_delivery_documents
    )

  form.receives_meter_requests =
    Boolean(
      contact.receives_meter_requests
    )

  form.receives_service_notifications =
    Boolean(
      contact.receives_service_notifications
    )

  form.receives_incident_notifications =
    Boolean(
      contact.receives_incident_notifications
    )

  form.receives_commercial_notifications =
    Boolean(
      contact.receives_commercial_notifications
    )

  form.can_authorize_equipment_entry =
    Boolean(
      contact.can_authorize_equipment_entry
    )

  form.can_authorize_equipment_removal =
    Boolean(
      contact.can_authorize_equipment_removal
    )

  form.can_sign_documents =
    Boolean(
      contact.can_sign_documents
    )

  modalOpen.value = true
}


function closeModal() {
  if (saving.value) {
    return
  }

  modalOpen.value = false
  resetForm()
}


async function submitContact() {
  errorMessage.value = ""
  successMessage.value = ""

  const validationError =
    validateForm()

  if (validationError) {
    errorMessage.value =
      validationError

    return
  }

  saving.value = true

  try {
    const payload =
      buildPayload()

    if (editingContactId.value) {
      await updateContact(
        editingContactId.value,
        payload
      )

      successMessage.value =
        "Contacto actualizado correctamente."
    } else {
      await createContact(payload)

      successMessage.value =
        "Contacto creado correctamente."
    }

    modalOpen.value = false
    resetForm()

    await loadContacts()

    emit("updated")
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo guardar el contacto."
  } finally {
    saving.value = false
  }
}


async function handleArchive(contact) {
  const contactName =
    getContactName(contact)

  const reason = window.prompt(
    `Indica el motivo para archivar a ${contactName}:`
  )

  if (reason === null) {
    return
  }

  const confirmed = window.confirm(
    `¿Confirmas que deseas archivar a ${contactName}?`
  )

  if (!confirmed) {
    return
  }

  errorMessage.value = ""
  successMessage.value = ""
  processingId.value = contact.id

  try {
    await archiveContact(
      contact.id,
      reason.trim()
    )

    successMessage.value =
      "Contacto archivado correctamente."

    await loadContacts()

    emit("updated")
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo archivar el contacto."
  } finally {
    processingId.value = ""
  }
}


async function handleRestore(contact) {
  const contactName =
    getContactName(contact)

  const confirmed = window.confirm(
    `¿Confirmas que deseas restaurar a ${contactName}?`
  )

  if (!confirmed) {
    return
  }

  errorMessage.value = ""
  successMessage.value = ""
  processingId.value = contact.id

  try {
    await restoreContact(
      contact.id
    )

    successMessage.value =
      "Contacto restaurado correctamente."

    await loadContacts()

    emit("updated")
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo restaurar el contacto."
  } finally {
    processingId.value = ""
  }
}


watch(
  () => form.whatsapp_number,
  (value) => {
    if (String(value || "").trim()) {
      form.has_whatsapp = true
    }
  }
)


watch(
  () => form.has_whatsapp,
  (hasWhatsapp) => {
    if (!hasWhatsapp) {
      form.whatsapp_number = ""

      if (
        form.preferred_contact_method ===
        "whatsapp"
      ) {
        form.preferred_contact_method =
          "email"
      }
    }
  }
)


watch(
  () => form.branch,
  (branchId) => {
    if (!branchId) {
      form.is_branch_manager = false
    }
  }
)


onMounted(() => {
  loadContacts()
})
</script>

<template>
  <section class="management-section">
    <header class="management-header">
      <div>
        <span class="section-kicker">
          Personas
        </span>

        <h3>Contactos</h3>

        <p>
          Registra responsables de facturación,
          contratos, contadores, servicio, logística
          y otras áreas.
        </p>
      </div>

      <button
        class="primary-button"
        type="button"
        @click="openCreateModal"
      >
        <span>＋</span>
        Nuevo contacto
      </button>
    </header>

    <div class="summary-grid">
      <article class="summary-card">
        <small>Total mostrados</small>
        <strong>{{ totalContacts }}</strong>
      </article>

      <article class="summary-card">
        <small>Activos</small>
        <strong>{{ activeContacts }}</strong>
      </article>

      <article class="summary-card">
        <small>Principales</small>
        <strong>{{ primaryContacts }}</strong>
      </article>

      <article class="summary-card">
        <small>Archivados</small>
        <strong>{{ archivedContacts }}</strong>
      </article>
    </div>

    <div class="toolbar">
      <label class="archive-filter">
        <input
          v-model="includeArchived"
          type="checkbox"
          @change="loadContacts"
        />

        <span>Mostrar archivados</span>
      </label>

      <button
        class="refresh-button"
        type="button"
        :disabled="loading"
        @click="loadContacts"
      >
        ↻ Actualizar
      </button>
    </div>

    <div
      v-if="successMessage"
      class="message success-message"
    >
      {{ successMessage }}
    </div>

    <div
      v-if="errorMessage && !modalOpen"
      class="message error-message"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="loading"
      class="loading-state"
    >
      <span class="spinner"></span>
      Cargando contactos...
    </div>

    <div
      v-else-if="!contacts.length"
      class="empty-state"
    >
      <span>◎</span>

      <strong>
        No hay contactos registrados
      </strong>

      <p>
        Registra una persona responsable de la
        empresa o de alguna sucursal.
      </p>

      <button
        class="empty-button"
        type="button"
        @click="openCreateModal"
      >
        Crear primer contacto
      </button>
    </div>

    <div
      v-else
      class="table-container"
    >
      <table>
        <thead>
          <tr>
            <th>Contacto</th>
            <th>Área / cargo</th>
            <th>Sucursal</th>
            <th>Comunicación</th>
            <th>Funciones</th>
            <th>Estado</th>

            <th class="actions-column">
              Acciones
            </th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="contact in contacts"
            :key="contact.id"
            :class="{
              'archived-row':
                contact.is_archived,
            }"
          >
            <td>
              <div class="main-information">
                <strong>
                  {{ getContactName(contact) }}
                </strong>

                <span>
                  {{
                    contact.document_number ||
                    "Sin documento"
                  }}
                </span>

                <div class="badges-container">
                  <span
                    v-if="contact.is_primary"
                    class="function-badge primary"
                  >
                    Principal
                  </span>

                  <span
                    v-if="
                      contact.is_legal_representative
                    "
                    class="function-badge legal"
                  >
                    Representante legal
                  </span>

                  <span
                    v-if="contact.is_branch_manager"
                    class="function-badge"
                  >
                    Responsable de sede
                  </span>
                </div>
              </div>
            </td>

            <td>
              <div class="main-information">
                <strong>
                  {{
                    contact.job_title ||
                    "Sin cargo"
                  }}
                </strong>

                <span>
                  {{
                    getAreaName(
                      contact.area
                    )
                  }}
                </span>
              </div>
            </td>

            <td>
              {{ getBranchName(contact) }}
            </td>

            <td>
              <div class="main-information communication-cell">
                <strong>
                  {{
                    getAvailableContact(
                      contact
                    )
                  }}
                </strong>

                <span>
                  Preferido:
                  {{
                    getPreferredMethodName(
                      contact.preferred_contact_method
                    )
                  }}
                </span>
              </div>
            </td>

            <td>
              <div class="badges-container functions-cell">
                <span
                  v-for="role in getNotificationRoles(contact)"
                  :key="role"
                  class="function-badge"
                >
                  {{ role }}
                </span>

                <span
                  v-if="
                    contact.can_authorize_equipment_entry
                  "
                  class="function-badge authorization"
                >
                  Autoriza ingreso
                </span>

                <span
                  v-if="
                    contact.can_authorize_equipment_removal
                  "
                  class="function-badge authorization"
                >
                  Autoriza retiro
                </span>

                <span
                  v-if="contact.can_sign_documents"
                  class="function-badge signature"
                >
                  Firma documentos
                </span>

                <span
                  v-if="
                    !getNotificationRoles(contact).length &&
                    !contact.can_authorize_equipment_entry &&
                    !contact.can_authorize_equipment_removal &&
                    !contact.can_sign_documents
                  "
                  class="function-badge empty"
                >
                  Sin funciones
                </span>
              </div>
            </td>

            <td>
              <span
                class="status-badge"
                :class="getStatusClass(contact)"
              >
                {{ getStatusName(contact) }}
              </span>
            </td>

            <td>
              <div class="row-actions">
                <button
                  class="action-button edit"
                  type="button"
                  :disabled="
                    contact.is_archived ||
                    processingId === contact.id
                  "
                  @click="openEditModal(contact)"
                >
                  Editar
                </button>

                <button
                  v-if="!contact.is_archived"
                  class="action-button archive"
                  type="button"
                  :disabled="
                    processingId === contact.id
                  "
                  @click="handleArchive(contact)"
                >
                  Archivar
                </button>

                <button
                  v-else
                  class="action-button restore"
                  type="button"
                  :disabled="
                    processingId === contact.id
                  "
                  @click="handleRestore(contact)"
                >
                  Restaurar
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <Teleport to="body">
      <div
        v-if="modalOpen"
        class="modal-overlay"
        @click.self="closeModal"
      >
        <form
          class="modal-card"
          @submit.prevent="submitContact"
        >
          <header class="modal-header">
            <div>
              <span class="section-kicker">
                Persona de contacto
              </span>

              <h3>{{ modalTitle }}</h3>

              <p>
                Define sus datos, responsabilidades,
                notificaciones y autorizaciones.
              </p>
            </div>

            <button
              class="close-button"
              type="button"
              :disabled="saving"
              aria-label="Cerrar"
              @click="closeModal"
            >
              ×
            </button>
          </header>

          <div
            v-if="errorMessage"
            class="message error-message modal-message"
          >
            {{ errorMessage }}
          </div>

          <div class="modal-content">
            <section class="modal-section">
              <h4>
                Información personal
              </h4>

              <div class="form-grid">
                <label class="form-field required">
                  <span>Nombres</span>

                  <input
                    v-model="form.first_names"
                    type="text"
                    placeholder="Nombres"
                    required
                  />
                </label>

                <label class="form-field">
                  <span>Apellido paterno</span>

                  <input
                    v-model="form.paternal_last_name"
                    type="text"
                    placeholder="Apellido paterno"
                  />
                </label>

                <label class="form-field">
                  <span>Apellido materno</span>

                  <input
                    v-model="form.maternal_last_name"
                    type="text"
                    placeholder="Apellido materno"
                  />
                </label>

                <label class="form-field">
                  <span>Sucursal o sede</span>

                  <select v-model="form.branch">
                    <option value="">
                      Contacto general de la empresa
                    </option>

                    <option
                      v-for="branch in availableBranches"
                      :key="branch.id"
                      :value="branch.id"
                    >
                      {{ branch.name }}
                    </option>
                  </select>
                </label>

                <label class="form-field">
                  <span>Tipo de documento</span>

                  <select
                    v-model="form.document_type"
                  >
                    <option
                      v-for="option in documentTypeOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </label>

                <label class="form-field">
                  <span>Número de documento</span>

                  <input
                    v-model="form.document_number"
                    type="text"
                    maxlength="50"
                    placeholder="Número de documento"
                  />
                </label>

                <label class="form-field">
                  <span>Cargo</span>

                  <input
                    v-model="form.job_title"
                    type="text"
                    placeholder="Ejemplo: Jefe de sistemas"
                  />
                </label>

                <label class="form-field">
                  <span>Área</span>

                  <select v-model="form.area">
                    <option
                      v-for="option in areaOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </label>
              </div>

              <div class="options-grid">
                <label class="option-card">
                  <input
                    v-model="form.is_primary"
                    type="checkbox"
                  />

                  <div>
                    <strong>
                      Contacto principal
                    </strong>

                    <span>
                      Solo puede existir un contacto
                      principal activo.
                    </span>
                  </div>
                </label>

                <label class="option-card">
                  <input
                    v-model="
                      form.is_legal_representative
                    "
                    type="checkbox"
                  />

                  <div>
                    <strong>
                      Representante legal
                    </strong>

                    <span>
                      Representa legalmente a la
                      empresa.
                    </span>
                  </div>
                </label>

                <label class="option-card">
                  <input
                    v-model="form.is_branch_manager"
                    type="checkbox"
                    :disabled="!form.branch"
                  />

                  <div>
                    <strong>
                      Responsable de sede
                    </strong>

                    <span>
                      Requiere seleccionar una
                      sucursal.
                    </span>
                  </div>
                </label>
              </div>
            </section>

            <section class="modal-section">
              <h4>
                Correos y teléfonos
              </h4>

              <div class="form-grid">
                <label class="form-field">
                  <span>Correo principal</span>

                  <input
                    v-model="form.primary_email"
                    type="email"
                    placeholder="contacto@empresa.com"
                  />
                </label>

                <label class="form-field">
                  <span>Correo secundario</span>

                  <input
                    v-model="form.secondary_email"
                    type="email"
                    placeholder="correo.alterno@empresa.com"
                  />
                </label>

                <label class="form-field">
                  <span>Teléfono de trabajo</span>

                  <input
                    v-model="form.work_phone"
                    type="tel"
                    placeholder="Teléfono de trabajo"
                  />
                </label>

                <label class="form-field">
                  <span>Anexo</span>

                  <input
                    v-model="form.work_extension"
                    type="text"
                    maxlength="10"
                    placeholder="Anexo"
                  />
                </label>

                <label class="form-field">
                  <span>Celular principal</span>

                  <input
                    v-model="form.primary_mobile"
                    type="tel"
                    placeholder="Celular principal"
                  />
                </label>

                <label class="form-field">
                  <span>Celular secundario</span>

                  <input
                    v-model="form.secondary_mobile"
                    type="tel"
                    placeholder="Celular secundario"
                  />
                </label>

                <label class="form-field">
                  <span>Número de WhatsApp</span>

                  <input
                    v-model="form.whatsapp_number"
                    type="tel"
                    placeholder="Número de WhatsApp"
                  />
                </label>

                <label class="form-field">
                  <span>
                    Medio de contacto preferido
                  </span>

                  <select
                    v-model="
                      form.preferred_contact_method
                    "
                  >
                    <option
                      v-for="option in contactMethodOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </label>

                <label class="form-field full-width">
                  <span>Horario de contacto</span>

                  <input
                    v-model="form.contact_schedule"
                    type="text"
                    placeholder="Lunes a viernes de 09:00 a 17:00"
                  />
                </label>
              </div>

              <div class="options-grid single-option">
                <label class="option-card">
                  <input
                    v-model="form.has_whatsapp"
                    type="checkbox"
                  />

                  <div>
                    <strong>Tiene WhatsApp</strong>

                    <span>
                      El número registrado puede recibir
                      mensajes por WhatsApp.
                    </span>
                  </div>
                </label>
              </div>
            </section>

            <section class="modal-section">
              <h4>
                Comunicaciones que recibe
              </h4>

              <div class="options-grid communication-options">
                <label class="option-card">
                  <input
                    v-model="form.receives_contracts"
                    type="checkbox"
                  />

                  <div>
                    <strong>Contratos</strong>
                    <span>Recibe contratos y anexos.</span>
                  </div>
                </label>

                <label class="option-card">
                  <input
                    v-model="form.receives_billing"
                    type="checkbox"
                  />

                  <div>
                    <strong>Facturación</strong>
                    <span>Recibe facturas y documentos.</span>
                  </div>
                </label>

                <label class="option-card">
                  <input
                    v-model="form.receives_collections"
                    type="checkbox"
                  />

                  <div>
                    <strong>Cobranzas</strong>
                    <span>Recibe estados y recordatorios.</span>
                  </div>
                </label>

                <label class="option-card">
                  <input
                    v-model="
                      form.receives_purchase_orders
                    "
                    type="checkbox"
                  />

                  <div>
                    <strong>Órdenes de compra</strong>
                    <span>Recibe o gestiona órdenes.</span>
                  </div>
                </label>

                <label class="option-card">
                  <input
                    v-model="
                      form.receives_delivery_documents
                    "
                    type="checkbox"
                  />

                  <div>
                    <strong>Guías y entregas</strong>
                    <span>Recibe documentos de entrega.</span>
                  </div>
                </label>

                <label class="option-card">
                  <input
                    v-model="
                      form.receives_meter_requests
                    "
                    type="checkbox"
                  />

                  <div>
                    <strong>Contadores</strong>
                    <span>Recibe solicitudes de lecturas.</span>
                  </div>
                </label>

                <label class="option-card">
                  <input
                    v-model="
                      form.receives_service_notifications
                    "
                    type="checkbox"
                  />

                  <div>
                    <strong>Servicio técnico</strong>
                    <span>Recibe avisos de servicios.</span>
                  </div>
                </label>

                <label class="option-card">
                  <input
                    v-model="
                      form.receives_incident_notifications
                    "
                    type="checkbox"
                  />

                  <div>
                    <strong>Incidencias</strong>
                    <span>Recibe avisos de incidencias.</span>
                  </div>
                </label>

                <label class="option-card">
                  <input
                    v-model="
                      form.receives_commercial_notifications
                    "
                    type="checkbox"
                  />

                  <div>
                    <strong>Comercial</strong>
                    <span>Recibe comunicaciones comerciales.</span>
                  </div>
                </label>
              </div>
            </section>

            <section class="modal-section">
              <h4>
                Autorizaciones
              </h4>

              <div class="options-grid">
                <label class="option-card">
                  <input
                    v-model="
                      form.can_authorize_equipment_entry
                    "
                    type="checkbox"
                  />

                  <div>
                    <strong>
                      Autoriza ingreso de equipos
                    </strong>

                    <span>
                      Puede autorizar el ingreso de
                      impresoras y materiales.
                    </span>
                  </div>
                </label>

                <label class="option-card">
                  <input
                    v-model="
                      form.can_authorize_equipment_removal
                    "
                    type="checkbox"
                  />

                  <div>
                    <strong>
                      Autoriza retiro de equipos
                    </strong>

                    <span>
                      Puede autorizar el retiro de
                      impresoras y materiales.
                    </span>
                  </div>
                </label>

                <label class="option-card">
                  <input
                    v-model="form.can_sign_documents"
                    type="checkbox"
                  />

                  <div>
                    <strong>
                      Puede firmar documentos
                    </strong>

                    <span>
                      Puede firmar actas, guías,
                      conformidades y contratos.
                    </span>
                  </div>
                </label>
              </div>
            </section>

            <section class="modal-section">
              <h4>
                Estado y observaciones
              </h4>

              <div class="form-grid">
                <label class="form-field full-width">
                  <span>Observaciones</span>

                  <textarea
                    v-model="form.notes"
                    rows="4"
                    placeholder="Observaciones sobre el contacto"
                  ></textarea>
                </label>
              </div>

              <div class="options-grid single-option">
                <label class="option-card">
                  <input
                    v-model="form.is_active"
                    type="checkbox"
                  />

                  <div>
                    <strong>Contacto activo</strong>

                    <span>
                      Puede utilizarse en operaciones
                      y comunicaciones.
                    </span>
                  </div>
                </label>
              </div>
            </section>
          </div>

          <footer class="modal-actions">
            <button
              class="secondary-button"
              type="button"
              :disabled="saving"
              @click="closeModal"
            >
              Cancelar
            </button>

            <button
              class="primary-button"
              type="submit"
              :disabled="saving"
            >
              <span
                v-if="saving"
                class="button-spinner"
              ></span>

              {{
                saving
                  ? "Guardando..."
                  : editingContactId
                    ? "Guardar cambios"
                    : "Crear contacto"
              }}
            </button>
          </footer>
        </form>
      </div>
    </Teleport>
  </section>
</template>

<style scoped>
button,
input,
select,
textarea {
  font: inherit;
}

.management-section {
  overflow: hidden;
  border: 1px solid #dfe3ec;
  border-radius: 15px;
  background: white;
}

.management-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 19px 20px;
  border-bottom: 1px solid #e8ebf1;
  background: #f8f9fd;
}

.section-kicker {
  display: block;
  margin-bottom: 5px;
  color: #1f35c4;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.management-header h3,
.modal-header h3 {
  margin: 0;
  color: #1d2940;
  font-size: 17px;
}

.management-header p,
.modal-header p {
  margin: 5px 0 0;
  color: #8693a4;
  font-size: 12px;
}

.primary-button,
.secondary-button {
  min-height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 0 16px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}

.primary-button {
  border: 0;
  background: linear-gradient(
    135deg,
    #162caa,
    #1f35c4 55%,
    #4e63d8
  );
  color: white;
  box-shadow:
    0 9px 20px rgba(31, 53, 196, 0.18);
}

.secondary-button {
  border: 1px solid #dfe3ec;
  background: white;
  color: #667382;
}

.summary-grid {
  display: grid;
  grid-template-columns:
    repeat(4, minmax(0, 1fr));
  gap: 12px;
  padding: 16px 20px 0;
}

.summary-card {
  padding: 14px 15px;
  border: 1px solid #e4e8ef;
  border-radius: 11px;
  background: #fafbfe;
}

.summary-card small,
.summary-card strong {
  display: block;
}

.summary-card small {
  color: #8793a1;
  font-size: 11px;
}

.summary-card strong {
  margin-top: 4px;
  color: #1d2940;
  font-size: 21px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 11px;
  padding: 14px 20px;
}

.archive-filter {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #667382;
  font-size: 12px;
}

.archive-filter input {
  width: 16px;
  height: 16px;
  accent-color: #1f35c4;
}

.refresh-button {
  min-height: 37px;
  padding: 0 12px;
  border: 1px solid #dfe3ec;
  border-radius: 9px;
  background: white;
  color: #667382;
  cursor: pointer;
}

.message {
  margin: 0 20px 15px;
  padding: 11px 13px;
  border-radius: 9px;
  font-size: 12px;
}

.success-message {
  border: 1px solid #c8ead4;
  background: #edf9f1;
  color: #287344;
}

.error-message {
  border: 1px solid #e8caca;
  background: #fff3f3;
  color: #9a4141;
}

.loading-state,
.empty-state {
  min-height: 210px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7b8797;
}

.loading-state {
  gap: 9px;
}

.spinner,
.button-spinner {
  display: inline-block;
  border-radius: 50%;
  animation: rotate 0.8s linear infinite;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #d9deea;
  border-top-color: #1f35c4;
}

.button-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.45);
  border-top-color: white;
}

.empty-state {
  flex-direction: column;
  padding: 34px 20px;
  text-align: center;
}

.empty-state > span {
  color: #9ba5b3;
  font-size: 38px;
}

.empty-state strong {
  margin-top: 9px;
  color: #34445a;
}

.empty-state p {
  margin: 6px 0 14px;
  font-size: 12px;
}

.empty-button {
  min-height: 38px;
  padding: 0 14px;
  border: 0;
  border-radius: 9px;
  background: #1f35c4;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.table-container {
  overflow-x: auto;
  border-top: 1px solid #edf0f4;
}

table {
  width: 100%;
  min-width: 1180px;
  border-collapse: collapse;
}

th,
td {
  padding: 13px 15px;
  border-bottom: 1px solid #edf0f4;
  text-align: left;
  vertical-align: middle;
}

th {
  background: #fafbfd;
  color: #7b8797;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

td {
  color: #4d5d70;
  font-size: 12px;
}

.archived-row {
  opacity: 0.7;
}

.main-information strong,
.main-information span {
  display: block;
}

.main-information strong {
  color: #2d3c50;
  font-size: 12px;
}

.main-information span {
  margin-top: 3px;
  color: #8792a0;
  font-size: 10px;
}

.communication-cell {
  max-width: 245px;
}

.communication-cell strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.badges-container {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 6px;
}

.functions-cell {
  max-width: 310px;
}

.function-badge,
.status-badge {
  display: inline-flex;
  padding: 5px 7px;
  border-radius: 999px;
  font-size: 9px;
  font-weight: 700;
}

.function-badge {
  background: #eef1f5;
  color: #647184;
}

.function-badge.primary {
  background: #edf0ff;
  color: #1f35c4;
}

.function-badge.legal {
  background: #f2edfa;
  color: #6b55a5;
}

.function-badge.authorization {
  background: #fff2e8;
  color: #a96031;
}

.function-badge.signature {
  background: #eaf7ef;
  color: #287d4d;
}

.function-badge.empty {
  background: #f1f2f4;
  color: #8a94a0;
}

.status-badge.active {
  background: #e7f6ed;
  color: #277d4c;
}

.status-badge.inactive {
  background: #fff0e8;
  color: #b45e32;
}

.status-badge.archived {
  background: #eceff3;
  color: #657181;
}

.actions-column {
  text-align: right;
}

.row-actions {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}

.action-button {
  padding: 6px 8px;
  border: 1px solid #dce4ea;
  border-radius: 7px;
  background: white;
  font-size: 10px;
  cursor: pointer;
}

.action-button.edit {
  color: #1f35c4;
}

.action-button.archive {
  color: #ad5c3b;
}

.action-button.restore {
  color: #2b8050;
}

.action-button:disabled {
  opacity: 0.45;
  cursor: wait;
}

.modal-overlay {
  position: fixed;
  z-index: 1000;
  inset: 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  overflow-y: auto;
  padding: 35px 18px;
  background: rgba(21, 31, 48, 0.58);
  backdrop-filter: blur(4px);
}

.modal-card {
  width: min(100%, 1020px);
  overflow: hidden;
  border: 1px solid #dfe3ec;
  border-radius: 17px;
  background: white;
  box-shadow:
    0 28px 70px rgba(14, 25, 43, 0.28);
  animation: modalReveal 0.24s ease-out;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 19px 21px;
  border-bottom: 1px solid #e8ebf1;
  background: #f8f9fd;
}

.close-button {
  width: 37px;
  height: 37px;
  flex-shrink: 0;
  border: 1px solid #dfe3ec;
  border-radius: 10px;
  background: white;
  color: #687586;
  font-size: 22px;
  cursor: pointer;
}

.modal-message {
  margin-top: 16px;
}

.modal-content {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  padding: 18px;
  background: #f5f7fb;
}

.modal-section {
  overflow: hidden;
  margin-bottom: 15px;
  border: 1px solid #e0e5ed;
  border-radius: 13px;
  background: white;
}

.modal-section:last-child {
  margin-bottom: 0;
}

.modal-section h4 {
  margin: 0;
  padding: 14px 17px;
  border-bottom: 1px solid #e8ebf1;
  background: #fafbfe;
  color: #26364c;
  font-size: 13px;
}

.form-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 15px;
  padding: 17px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field.full-width {
  grid-column: 1 / -1;
}

.form-field > span {
  color: #667382;
  font-size: 11px;
  font-weight: 700;
}

.form-field.required > span::after {
  content: " *";
  color: #4e63d8;
}

.form-field input,
.form-field select,
.form-field textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #dfe3ec;
  border-radius: 9px;
  outline: none;
  background: white;
  color: #1d2940;
}

.form-field input,
.form-field select {
  min-height: 41px;
  padding: 0 11px;
}

.form-field textarea {
  resize: vertical;
  padding: 10px 11px;
  line-height: 1.45;
}

.form-field input:focus,
.form-field select:focus,
.form-field textarea:focus {
  border-color: #4e63d8;
  box-shadow:
    0 0 0 3px rgba(31, 53, 196, 0.11);
}

.options-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 11px;
  padding: 0 17px 17px;
}

.communication-options {
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  padding-top: 17px;
}

.single-option {
  grid-template-columns: 1fr;
}

.option-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 13px;
  border: 1px solid #dfe3ec;
  border-radius: 10px;
  background: #f8f9fd;
  cursor: pointer;
}

.option-card:has(input:checked) {
  border-color: #bfc7f4;
  background: #edf0ff;
  box-shadow: inset 3px 0 0 #1f35c4;
}

.option-card input {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  margin-top: 2px;
  accent-color: #1f35c4;
}

.option-card input:disabled {
  opacity: 0.45;
}

.option-card strong,
.option-card span {
  display: block;
}

.option-card strong {
  color: #1d2940;
  font-size: 12px;
}

.option-card span {
  margin-top: 3px;
  color: #8693a4;
  font-size: 10px;
  line-height: 1.4;
}

.modal-actions {
  position: sticky;
  bottom: 0;
  display: flex;
  justify-content: flex-end;
  gap: 9px;
  padding: 15px 20px;
  border-top: 1px solid #e8ebf1;
  background: white;
}

.primary-button:disabled,
.secondary-button:disabled {
  opacity: 0.6;
  cursor: wait;
}

@keyframes rotate {
  to {
    transform: rotate(360deg);
  }
}

@keyframes modalReveal {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.985);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (max-width: 900px) {
  .communication-options {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .management-header {
    flex-direction: column;
  }

  .management-header .primary-button {
    width: 100%;
  }

  .summary-grid,
  .form-grid,
  .options-grid,
  .communication-options {
    grid-template-columns: 1fr;
  }

  .form-field.full-width {
    grid-column: auto;
  }

  .toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .modal-overlay {
    padding: 10px;
  }

  .modal-content {
    max-height: calc(100vh - 180px);
    padding: 10px;
  }
}

@media (max-width: 520px) {
  .modal-actions {
    flex-direction: column-reverse;
  }

  .modal-actions button {
    width: 100%;
  }
}
</style>