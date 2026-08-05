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

import {
  getEquipment,
  getEquipmentById,
} from "../../services/equipment.service"

import {
  assignRepair,
  createRepair,
  getActiveRepairByEquipment,
  getRepairById,
  updateRepair,
} from "../../services/repairs.service"

import {
  getUsers,
} from "../../services/users.service"

import "./RepairFormView.css"


const route = useRoute()
const router = useRouter()

const loading = ref(false)
const loadingEquipment = ref(false)
const loadingTechnicians = ref(false)
const saving = ref(false)

const errorMessage = ref("")
const successMessage = ref("")

const equipment = ref([])
const technicians = ref([])

const equipmentSearch = ref("")
const technicianSearch = ref("")

const originalTechnicianId = ref("")


const repairId = computed(() => {
  return String(
    route.params.id || ""
  )
})


const isEditing = computed(() => {
  return Boolean(
    repairId.value
  )
})


const sourceEquipmentId = computed(() => {
  return String(
    route.query.equipment || ""
  ).trim()
})


const comesFromEquipment = computed(() => {
  return (
    !isEditing.value &&
    Boolean(sourceEquipmentId.value)
  )
})


const equipmentSelectionLocked = computed(() => {
  return (
    isEditing.value ||
    comesFromEquipment.value
  )
})


const pageTitle = computed(() => {
  return isEditing.value
    ? "Editar reparación"
    : "Nueva reparación"
})


const pageDescription = computed(() => {
  if (comesFromEquipment.value) {
    return (
      "Registra una reparación para el equipo seleccionado " +
      "desde su ficha."
    )
  }

  return (
    "Registra la información inicial, condiciones, técnico " +
    "y requisitos de la reparación."
  )
})


const form = reactive({
  code: "",
  equipment: "",
  repair_type: "initial_review",
  priority: "normal",
  reported_problem: "",
  initial_observations: "",

  technician: "",
  assignment_reason: "",

  work_summary: "",
  pending_work: "",
  final_condition: "not_defined",
  final_observations: "",

  requires_parts: false,
  requires_external_service: false,
  requires_follow_up: false,
  follow_up_date: "",

  minimum_photos_required: 10,
  closure_notes: "",
})


const selectedEquipment = computed(() => {
  return (
    equipment.value.find(
      (item) =>
        String(item.id) ===
        String(form.equipment)
    ) ||
    null
  )
})


const selectedTechnician = computed(() => {
  return (
    technicians.value.find(
      (item) =>
        String(item.id) ===
        String(form.technician)
    ) ||
    null
  )
})


const filteredEquipment = computed(() => {
  const query = String(
    equipmentSearch.value || ""
  )
    .trim()
    .toLowerCase()

  if (!query) {
    return equipment.value
  }

  return equipment.value.filter(
    (item) => {
      const values = [
        item.serial_number,
        item.internal_code,
        item.name,
        item.display_name,
        item.brand_name,
        item.model_name,
        item.equipment_brand_name,
        item.equipment_model_name,
        item.equipment_model_detail?.name,
        item.equipment_model_detail?.brand_name,
      ]

      return values.some(
        (value) =>
          String(value || "")
            .toLowerCase()
            .includes(query)
      )
    }
  )
})


const filteredTechnicians = computed(() => {
  const query = String(
    technicianSearch.value || ""
  )
    .trim()
    .toLowerCase()

  if (!query) {
    return technicians.value
  }

  return technicians.value.filter(
    (item) => {
      const values = [
        getUserName(item),
        item.username,
        item.email,
        item.dni,
        item.document_number,
        item.job_title,
        item.position,
      ]

      return values.some(
        (value) =>
          String(value || "")
            .toLowerCase()
            .includes(query)
      )
    }
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


function appendEquipment(item) {
  if (!item?.id) {
    return
  }

  const exists =
    equipment.value.some(
      (currentItem) =>
        String(currentItem.id) ===
        String(item.id)
    )

  if (!exists) {
    equipment.value.unshift(item)
  }
}


function appendTechnician(item) {
  if (!item?.id) {
    return
  }

  const exists =
    technicians.value.some(
      (currentItem) =>
        String(currentItem.id) ===
        String(item.id)
    )

  if (!exists) {
    technicians.value.unshift(item)
  }
}


function getEquipmentBrand(item) {
  return (
    item?.brand_name ||
    item?.equipment_brand_name ||
    item?.equipment_model_detail?.brand_name ||
    item?.equipment_model?.brand_name ||
    ""
  )
}


function getEquipmentModel(item) {
  return (
    item?.model_name ||
    item?.equipment_model_name ||
    item?.equipment_model_detail?.name ||
    item?.equipment_model?.name ||
    ""
  )
}


function getEquipmentName(item) {
  if (!item) {
    return "Equipo sin identificar"
  }

  const brand =
    getEquipmentBrand(item)

  const model =
    getEquipmentModel(item)

  const completeName = [
    brand,
    model,
  ]
    .filter(Boolean)
    .join(" ")
    .trim()

  return (
    completeName ||
    item.display_name ||
    item.name ||
    item.serial_number ||
    "Equipo sin identificar"
  )
}


function getEquipmentOptionLabel(item) {
  const name =
    getEquipmentName(item)

  const serial =
    item.serial_number ||
    "Sin serie"

  const internalCode =
    item.internal_code ||
    "Sin código"

  return (
    `${name} · ${serial} · ${internalCode}`
  )
}


function getTechnicalStatusName(item) {
  if (!item) {
    return "Sin estado"
  }

  if (item.technical_status_name) {
    return item.technical_status_name
  }

  const names = {
    unreviewed: "Sin revisar",
    for_review: "Para revisión",
    in_review: "En revisión",
    completed: "Finalizada",
    with_problems: "Con problemas",
    for_parts: "De partes",
  }

  return (
    names[item.technical_status] ||
    item.technical_status ||
    "Sin estado"
  )
}


function getCommercialStatusName(item) {
  if (!item) {
    return "Sin estado"
  }

  if (item.commercial_status_name) {
    return item.commercial_status_name
  }

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
    returned:
      "Retornada a almacén",
    temporary_loan:
      "Préstamo temporal",
    demonstration:
      "Demostración",
    replacement:
      "Equipo de reemplazo",
    out_of_service:
      "Fuera de servicio",
    disposed: "De baja",
  }

  return (
    names[item.commercial_status] ||
    item.commercial_status ||
    "Sin estado"
  )
}


function getUserName(user) {
  if (!user) {
    return "Usuario sin nombre"
  }

  const fullName =
    [
      user.first_name,
      user.last_name,
    ]
      .filter(Boolean)
      .join(" ")
      .trim()

  return (
    user.full_name ||
    user.display_name ||
    fullName ||
    user.name ||
    user.username ||
    user.email ||
    "Usuario sin nombre"
  )
}


function getUserOptionLabel(user) {
  const name =
    getUserName(user)

  const additional =
    user.job_title ||
    user.position ||
    user.email ||
    user.username ||
    ""

  return additional
    ? `${name} · ${additional}`
    : name
}


async function loadEquipmentList() {
  loadingEquipment.value = true

  try {
    const response =
      await getEquipment({
        includeArchived: false,
        isActive: true,
      })

    equipment.value =
      normalizeCollection(response)
        .filter(
          (item) =>
            !item.is_archived &&
            item.archived_at == null &&
            item.is_active !== false
        )
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudieron cargar los equipos."
  } finally {
    loadingEquipment.value = false
  }
}


async function loadTechnicians() {
  loadingTechnicians.value = true

  try {
    const response =
      await getUsers({
        includeArchived: false,
        isActive: true,
      })

    technicians.value =
      normalizeCollection(response)
        .filter(
          (item) =>
            item.is_active !== false &&
            !item.is_archived &&
            item.archived_at == null
        )
        .sort(
          (firstItem, secondItem) =>
            getUserName(firstItem)
              .localeCompare(
                getUserName(secondItem),
                "es",
                {
                  sensitivity: "base",
                }
              )
        )
  } catch (error) {
    technicians.value = []

    errorMessage.value =
      error.message ||
      "No se pudieron cargar los usuarios."
  } finally {
    loadingTechnicians.value = false
  }
}


async function loadSourceEquipment() {
  if (!sourceEquipmentId.value) {
    return
  }

  loadingEquipment.value = true
  errorMessage.value = ""

  try {
    const item =
      await getEquipmentById(
        sourceEquipmentId.value
      )

    if (
      item.is_archived ||
      item.archived_at
    ) {
      throw new Error(
        "No puedes crear una reparación para un equipo archivado."
      )
    }

    appendEquipment(item)

    form.equipment = item.id

    const activeRepair =
      await getActiveRepairByEquipment(
        item.id
      )

    if (activeRepair?.id) {
      await router.replace({
        name: "repair-detail",
        params: {
          id: activeRepair.id,
        },
      })
    }
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo cargar el equipo seleccionado."
  } finally {
    loadingEquipment.value = false
  }
}


function getRepairTechnicianId(repair) {
  const technician =
    repair?.assigned_technician

  if (
    technician &&
    typeof technician === "object"
  ) {
    return String(
      technician.id || ""
    )
  }

  return String(
    technician || ""
  )
}


function setFormData(repair) {
  form.code =
    repair.code || ""

  form.equipment =
    repair.equipment || ""

  form.repair_type =
    repair.repair_type ||
    "initial_review"

  form.priority =
    repair.priority ||
    "normal"

  form.reported_problem =
    repair.reported_problem || ""

  form.initial_observations =
    repair.initial_observations || ""

  const technicianId =
    getRepairTechnicianId(repair)

  form.technician =
    technicianId

  originalTechnicianId.value =
    technicianId

  form.assignment_reason = ""

  form.work_summary =
    repair.work_summary || ""

  form.pending_work =
    repair.pending_work || ""

  form.final_condition =
    repair.final_condition ||
    "not_defined"

  form.final_observations =
    repair.final_observations || ""

  form.requires_parts =
    Boolean(
      repair.requires_parts
    )

  form.requires_external_service =
    Boolean(
      repair.requires_external_service
    )

  form.requires_follow_up =
    Boolean(
      repair.requires_follow_up
    )

  form.follow_up_date =
    repair.follow_up_date || ""

  form.minimum_photos_required =
    Number(
      repair.minimum_photos_required ??
      10
    )

  form.closure_notes =
    repair.closure_notes || ""
}


async function loadRepair() {
  if (!isEditing.value) {
    return
  }

  loading.value = true
  errorMessage.value = ""

  try {
    const repair =
      await getRepairById(
        repairId.value
      )

    setFormData(repair)

    if (repair.equipment) {
      const equipmentIdentifier =
        typeof repair.equipment ===
        "object"
          ? repair.equipment.id
          : repair.equipment

      form.equipment =
        equipmentIdentifier

      const item =
        await getEquipmentById(
          equipmentIdentifier
        )

      appendEquipment(item)
    }

    const technicianId =
      getRepairTechnicianId(repair)

    if (technicianId) {
      const existingTechnician =
        technicians.value.find(
          (item) =>
            String(item.id) ===
            technicianId
        )

      if (
        !existingTechnician &&
        repair.assigned_technician_detail
      ) {
        appendTechnician(
          repair.assigned_technician_detail
        )
      }
    }
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo cargar la reparación."
  } finally {
    loading.value = false
  }
}


async function validateActiveRepair() {
  if (
    isEditing.value ||
    !form.equipment
  ) {
    return
  }

  const activeRepair =
    await getActiveRepairByEquipment(
      form.equipment
    )

  if (activeRepair?.id) {
    throw new Error(
      "El equipo seleccionado ya tiene una reparación activa."
    )
  }
}


function validateForm() {
  if (!form.equipment) {
    throw new Error(
      "Debes seleccionar un equipo."
    )
  }

  if (
    !String(
      form.reported_problem || ""
    ).trim()
  ) {
    throw new Error(
      "Debes indicar el problema reportado."
    )
  }

  if (
    Number(
      form.minimum_photos_required
    ) < 1
  ) {
    throw new Error(
      "Debe requerirse al menos una fotografía."
    )
  }

  if (
    form.requires_follow_up &&
    !form.follow_up_date
  ) {
    throw new Error(
      "Debes indicar la fecha de seguimiento."
    )
  }
}


function buildPayload() {
  return {
    code:
      String(
        form.code || ""
      ).trim(),

    equipment:
      form.equipment,

    repair_type:
      form.repair_type,

    priority:
      form.priority,

    reported_problem:
      String(
        form.reported_problem || ""
      ).trim(),

    initial_observations:
      String(
        form.initial_observations || ""
      ).trim(),

    work_summary:
      String(
        form.work_summary || ""
      ).trim(),

    pending_work:
      String(
        form.pending_work || ""
      ).trim(),

    final_condition:
      form.final_condition,

    final_observations:
      String(
        form.final_observations || ""
      ).trim(),

    requires_parts:
      Boolean(
        form.requires_parts
      ),

    requires_external_service:
      Boolean(
        form.requires_external_service
      ),

    requires_follow_up:
      Boolean(
        form.requires_follow_up
      ),

    follow_up_date:
      form.requires_follow_up
        ? form.follow_up_date
        : null,

    minimum_photos_required:
      Number(
        form.minimum_photos_required
      ),

    closure_notes:
      String(
        form.closure_notes || ""
      ).trim(),
  }
}


function technicianChanged() {
  return (
    String(
      form.technician || ""
    ) !==
    String(
      originalTechnicianId.value || ""
    )
  )
}


async function assignSelectedTechnician(
  savedRepairId
) {
  if (
    !form.technician ||
    !savedRepairId
  ) {
    return
  }

  if (
    isEditing.value &&
    !technicianChanged()
  ) {
    return
  }

  await assignRepair(
    savedRepairId,
    {
      technician:
        form.technician,

      reason:
        String(
          form.assignment_reason || ""
        ).trim(),
    }
  )
}


async function handleSubmit() {
  if (saving.value) {
    return
  }

  saving.value = true
  errorMessage.value = ""
  successMessage.value = ""

  let savedRepair = null

  try {
    validateForm()

    await validateActiveRepair()

    const payload =
      buildPayload()

    if (isEditing.value) {
      savedRepair =
        await updateRepair(
          repairId.value,
          payload
        )
    } else {
      savedRepair =
        await createRepair(
          payload
        )
    }

    const savedId =
      savedRepair?.id ||
      repairId.value

    if (!savedId) {
      throw new Error(
        "La reparación se guardó, pero no se recibió su identificador."
      )
    }

    try {
      await assignSelectedTechnician(
        savedId
      )
    } catch (assignmentError) {
      errorMessage.value =
        (
          isEditing.value
            ? "La reparación se actualizó, pero no se pudo reasignar al técnico. "
            : "La reparación se creó, pero no se pudo asignar al técnico. "
        ) +
        (
          assignmentError.message ||
          "Revisa la asignación desde el detalle."
        )

      await router.push({
        name: "repair-detail",
        params: {
          id: savedId,
        },
      })

      return
    }

    successMessage.value =
      isEditing.value
        ? "La reparación se actualizó correctamente."
        : form.technician
          ? "La reparación se creó y fue asignada correctamente."
          : "La reparación se creó correctamente."

    await router.push({
      name: "repair-detail",
      params: {
        id: savedId,
      },
    })
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo guardar la reparación."
  } finally {
    saving.value = false
  }
}


function handleFollowUpChange() {
  if (
    !form.requires_follow_up
  ) {
    form.follow_up_date = ""
  }
}


function handleTechnicianChange() {
  if (!form.technician) {
    form.assignment_reason = ""
  }
}


async function goBack() {
  if (isEditing.value) {
    await router.push({
      name: "repair-detail",
      params: {
        id: repairId.value,
      },
    })

    return
  }

  if (
    comesFromEquipment.value &&
    sourceEquipmentId.value
  ) {
    await router.push({
      name: "equipment-detail",
      params: {
        id:
          sourceEquipmentId.value,
      },
    })

    return
  }

  await router.push({
    name: "repairs",
  })
}


onMounted(async () => {
  await Promise.all([
    loadEquipmentList(),
    loadTechnicians(),
  ])

  if (isEditing.value) {
    await loadRepair()

    return
  }

  if (sourceEquipmentId.value) {
    await loadSourceEquipment()
  }
})
</script>

<template>
  <section class="repair-form-page">
    <header class="repair-form-header">
      <div>
        <button
          class="back-button"
          type="button"
          @click="goBack"
        >
          ← Volver
        </button>

        <span class="page-kicker">
          Taller técnico
        </span>

        <h1>
          {{ pageTitle }}
        </h1>

        <p>
          {{ pageDescription }}
        </p>
      </div>

      <div class="header-actions">
        <button
          class="secondary-button"
          type="button"
          :disabled="saving"
          @click="goBack"
        >
          Cancelar
        </button>

        <button
          class="primary-button"
          type="button"
          :disabled="
            saving ||
            loading ||
            loadingEquipment ||
            loadingTechnicians
          "
          @click="handleSubmit"
        >
          {{
            saving
              ? "Guardando..."
              : isEditing
                ? "Guardar cambios"
                : "Crear reparación"
          }}
        </button>
      </div>
    </header>

    <div
      v-if="errorMessage"
      class="form-message error"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="successMessage"
      class="form-message success"
    >
      {{ successMessage }}
    </div>

    <div
      v-if="loading"
      class="form-loading"
    >
      <span class="spinner"></span>

      Cargando reparación...
    </div>

    <form
      v-else
      class="repair-form"
      @submit.prevent="handleSubmit"
    >
      <article
        class="form-card equipment-card"
      >
        <div class="card-heading">
          <div class="heading-icon">
            ▣
          </div>

          <div>
            <h2>
              Equipo
            </h2>

            <p v-if="comesFromEquipment">
              La máquina fue seleccionada desde su ficha.
            </p>

            <p v-else>
              Selecciona la máquina que ingresará al taller.
            </p>
          </div>
        </div>

        <div class="form-grid">
          <label
            v-if="!equipmentSelectionLocked"
            class="field full-width"
          >
            <span>
              Buscar equipo
            </span>

            <input
              v-model="equipmentSearch"
              type="search"
              placeholder="Serie, código, marca o modelo"
              :disabled="loadingEquipment"
            />
          </label>

          <label class="field full-width">
            <span>
              Equipo
              <strong>*</strong>
            </span>

            <select
              v-model="form.equipment"
              :disabled="
                loadingEquipment ||
                equipmentSelectionLocked
              "
              required
            >
              <option value="">
                {{
                  loadingEquipment
                    ? "Cargando equipos..."
                    : "Selecciona un equipo"
                }}
              </option>

              <option
                v-for="item in filteredEquipment"
                :key="item.id"
                :value="item.id"
              >
                {{
                  getEquipmentOptionLabel(
                    item
                  )
                }}
              </option>
            </select>

            <small v-if="isEditing">
              El equipo no puede cambiarse después de crear la reparación.
            </small>

            <small
              v-else-if="comesFromEquipment"
            >
              Para elegir otra máquina, vuelve a la lista de equipos.
            </small>
          </label>
        </div>

        <div
          v-if="selectedEquipment"
          class="selected-equipment"
        >
          <div class="equipment-avatar">
            ▣
          </div>

          <div class="equipment-main">
            <strong>
              {{
                getEquipmentName(
                  selectedEquipment
                )
              }}
            </strong>

            <span>
              Serie:
              {{
                selectedEquipment.serial_number ||
                "Sin serie"
              }}
            </span>
          </div>

          <div class="equipment-data">
            <span>
              Código interno
            </span>

            <strong>
              {{
                selectedEquipment.internal_code ||
                "Sin código"
              }}
            </strong>
          </div>

          <div class="equipment-data">
            <span>
              Estado técnico
            </span>

            <strong>
              {{
                getTechnicalStatusName(
                  selectedEquipment
                )
              }}
            </strong>
          </div>

          <div class="equipment-data">
            <span>
              Estado comercial
            </span>

            <strong>
              {{
                getCommercialStatusName(
                  selectedEquipment
                )
              }}
            </strong>
          </div>
        </div>
      </article>

      <article class="form-card">
        <div class="card-heading">
          <div class="heading-icon">
            👤
          </div>

          <div>
            <h2>
              Técnico responsable
            </h2>

            <p>
              Puedes asignar la reparación ahora o dejarla pendiente.
            </p>
          </div>
        </div>

        <div class="form-grid">
          <label class="field">
            <span>
              Buscar usuario
            </span>

            <input
              v-model="technicianSearch"
              type="search"
              placeholder="Nombre, usuario o correo"
              :disabled="loadingTechnicians"
            />
          </label>

          <label class="field">
            <span>
              Técnico asignado
            </span>

            <select
              v-model="form.technician"
              :disabled="loadingTechnicians"
              @change="handleTechnicianChange"
            >
              <option value="">
                {{
                  loadingTechnicians
                    ? "Cargando usuarios..."
                    : "Dejar pendiente de asignación"
                }}
              </option>

              <option
                v-for="user in filteredTechnicians"
                :key="user.id"
                :value="user.id"
              >
                {{
                  getUserOptionLabel(
                    user
                  )
                }}
              </option>
            </select>

            <small>
              La asignación colocará la reparación a cargo del usuario seleccionado.
            </small>
          </label>

          <label
            v-if="form.technician"
            class="field full-width"
          >
            <span>
              Motivo o indicación para el técnico
            </span>

            <textarea
              v-model="form.assignment_reason"
              rows="3"
              maxlength="2000"
              placeholder="Ejemplo: revisar primero unidad de imagen y sistema de alimentación"
            ></textarea>

            <small>
              {{ form.assignment_reason.length }}/2000
            </small>
          </label>
        </div>

        <div
          v-if="selectedTechnician"
          class="selected-technician"
        >
          <div class="technician-avatar">
            {{
              getUserName(
                selectedTechnician
              )
                .charAt(0)
                .toUpperCase()
            }}
          </div>

          <div class="technician-information">
            <span>
              Técnico seleccionado
            </span>

            <strong>
              {{
                getUserName(
                  selectedTechnician
                )
              }}
            </strong>

            <small>
              {{
                selectedTechnician.email ||
                selectedTechnician.username ||
                selectedTechnician.job_title ||
                "Usuario activo"
              }}
            </small>
          </div>
        </div>
      </article>

      <article class="form-card">
        <div class="card-heading">
          <div class="heading-icon">
            ⚙
          </div>

          <div>
            <h2>
              Información general
            </h2>

            <p>
              Define el tipo, prioridad y motivo de ingreso.
            </p>
          </div>
        </div>

        <div
          class="form-grid three-columns"
        >
          <label class="field">
            <span>
              Código
            </span>

            <input
              v-model="form.code"
              type="text"
              maxlength="50"
              placeholder="Automático"
              :disabled="isEditing"
            />

            <small>
              Déjalo vacío para generar el código automáticamente.
            </small>
          </label>

          <label class="field">
            <span>
              Tipo de reparación
              <strong>*</strong>
            </span>

            <select
              v-model="form.repair_type"
              required
            >
              <option value="initial_review">
                Revisión inicial
              </option>

              <option value="preventive">
                Mantenimiento preventivo
              </option>

              <option value="corrective">
                Mantenimiento correctivo
              </option>

              <option value="reconditioning">
                Reacondicionamiento
              </option>

              <option value="warranty">
                Garantía
              </option>

              <option value="return_review">
                Revisión por devolución
              </option>

              <option value="other">
                Otro
              </option>
            </select>
          </label>

          <label class="field">
            <span>
              Prioridad
              <strong>*</strong>
            </span>

            <select
              v-model="form.priority"
              required
            >
              <option value="low">
                Baja
              </option>

              <option value="normal">
                Normal
              </option>

              <option value="high">
                Alta
              </option>

              <option value="urgent">
                Urgente
              </option>
            </select>
          </label>

          <label
            class="field full-width"
          >
            <span>
              Problema reportado
              <strong>*</strong>
            </span>

            <textarea
              v-model="form.reported_problem"
              rows="4"
              maxlength="5000"
              placeholder="Describe el motivo por el que la máquina ingresa al taller"
              required
            ></textarea>
          </label>

          <label
            class="field full-width"
          >
            <span>
              Observaciones iniciales
            </span>

            <textarea
              v-model="form.initial_observations"
              rows="4"
              placeholder="Estado físico, accesorios recibidos, daños visibles y otras observaciones"
            ></textarea>
          </label>
        </div>
      </article>

      <article class="form-card">
        <div class="card-heading">
          <div class="heading-icon">
            ✓
          </div>

          <div>
            <h2>
              Requisitos de revisión
            </h2>

            <p>
              Configura evidencias, repuestos y seguimiento.
            </p>
          </div>
        </div>

        <div class="requirements-grid">
          <label class="switch-card">
            <input
              v-model="form.requires_parts"
              type="checkbox"
            />

            <span
              class="switch-control"
            ></span>

            <div>
              <strong>
                Requiere repuestos
              </strong>

              <small>
                La reparación puede necesitar componentes o unidades.
              </small>
            </div>
          </label>

          <label class="switch-card">
            <input
              v-model="
                form.requires_external_service
              "
              type="checkbox"
            />

            <span
              class="switch-control"
            ></span>

            <div>
              <strong>
                Servicio externo
              </strong>

              <small>
                Requiere trabajo realizado fuera del taller.
              </small>
            </div>
          </label>

          <label class="switch-card">
            <input
              v-model="
                form.requires_follow_up
              "
              type="checkbox"
              @change="
                handleFollowUpChange
              "
            />

            <span
              class="switch-control"
            ></span>

            <div>
              <strong>
                Requiere seguimiento
              </strong>

              <small>
                Programa una revisión posterior.
              </small>
            </div>
          </label>
        </div>

        <div class="form-grid">
          <label class="field">
            <span>
              Fotografías mínimas
              <strong>*</strong>
            </span>

            <input
              v-model.number="
                form.minimum_photos_required
              "
              type="number"
              min="1"
              max="100"
              required
            />

            <small>
              Cantidad mínima requerida para finalizar.
            </small>
          </label>

          <label class="field">
            <span>
              Fecha de seguimiento
            </span>

            <input
              v-model="
                form.follow_up_date
              "
              type="date"
              :disabled="
                !form.requires_follow_up
              "
              :required="
                form.requires_follow_up
              "
            />
          </label>
        </div>
      </article>

      <article
        v-if="isEditing"
        class="form-card"
      >
        <div class="card-heading">
          <div class="heading-icon">
            ◉
          </div>

          <div>
            <h2>
              Trabajo y condición final
            </h2>

            <p>
              Información que se completa durante el proceso técnico.
            </p>
          </div>
        </div>

        <div class="form-grid">
          <label
            class="field full-width"
          >
            <span>
              Resumen del trabajo
            </span>

            <textarea
              v-model="form.work_summary"
              rows="5"
              placeholder="Describe los trabajos realizados"
            ></textarea>
          </label>

          <label
            class="field full-width"
          >
            <span>
              Trabajo pendiente
            </span>

            <textarea
              v-model="form.pending_work"
              rows="4"
              placeholder="Trabajos o validaciones que aún faltan"
            ></textarea>
          </label>

          <label class="field">
            <span>
              Condición final
            </span>

            <select
              v-model="form.final_condition"
            >
              <option value="not_defined">
                No definida
              </option>

              <option value="operational">
                Operativa
              </option>

              <option
                value="operational_with_observations"
              >
                Operativa con observaciones
              </option>

              <option value="requires_parts">
                Requiere repuestos
              </option>

              <option value="not_repairable">
                No reparable
              </option>

              <option value="for_parts">
                Para repuestos
              </option>
            </select>
          </label>

          <label
            class="field full-width"
          >
            <span>
              Observaciones finales
            </span>

            <textarea
              v-model="
                form.final_observations
              "
              rows="4"
              placeholder="Condición de salida y observaciones finales"
            ></textarea>
          </label>

          <label
            class="field full-width"
          >
            <span>
              Notas de cierre
            </span>

            <textarea
              v-model="form.closure_notes"
              rows="4"
              placeholder="Información administrativa o técnica del cierre"
            ></textarea>
          </label>
        </div>
      </article>

      <footer class="form-footer">
        <button
          class="secondary-button"
          type="button"
          :disabled="saving"
          @click="goBack"
        >
          Cancelar
        </button>

        <button
          class="primary-button"
          type="submit"
          :disabled="
            saving ||
            loadingEquipment ||
            loadingTechnicians
          "
        >
          {{
            saving
              ? "Guardando..."
              : isEditing
                ? "Guardar cambios"
                : form.technician
                  ? "Crear y asignar"
                  : "Crear reparación"
          }}
        </button>
      </footer>
    </form>
  </section>
</template>