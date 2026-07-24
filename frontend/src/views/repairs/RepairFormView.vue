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
  createRepair,
  getRepairById,
  updateRepair,
} from "../../services/repairs.service"

import {
  clearSession,
  getToken,
} from "../../services/auth.service"

import "./RepairFormView.css"


const EQUIPMENT_API_URL =
  "http://127.0.0.1:8000/api/equipment/"


const route = useRoute()
const router = useRouter()

const loading = ref(false)
const loadingEquipment = ref(false)
const saving = ref(false)

const errorMessage = ref("")
const successMessage = ref("")

const equipment = ref([])
const equipmentSearch = ref("")

const repairId = computed(
  () => route.params.id || ""
)

const isEditing = computed(
  () => Boolean(repairId.value)
)

const pageTitle = computed(
  () =>
    isEditing.value
      ? "Editar reparación"
      : "Nueva reparación"
)

const form = reactive({
  code: "",
  equipment: "",
  repair_type: "initial_review",
  priority: "normal",
  reported_problem: "",
  initial_observations: "",
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
  return equipment.value.find(
    (item) =>
      String(item.id) ===
      String(form.equipment)
  ) || null
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

  const name = [
    brand,
    model,
  ]
    .filter(Boolean)
    .join(" ")
    .trim()

  return (
    name ||
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


function getValidationError(data) {
  if (!data) {
    return null
  }

  if (typeof data === "string") {
    return data
  }

  if (Array.isArray(data)) {
    return data.length
      ? getValidationError(data[0])
      : null
  }

  if (typeof data === "object") {
    for (
      const value
      of Object.values(data)
    ) {
      const error =
        getValidationError(value)

      if (error) {
        return error
      }
    }
  }

  return null
}


async function equipmentRequest(url) {
  const token = getToken()

  const response = await fetch(
    url,
    {
      headers: {
        Accept: "application/json",
        Authorization:
          token
            ? `Token ${token}`
            : "",
      },
    }
  )

  let data = null

  try {
    data = await response.json()
  } catch {
    data = null
  }

  if (response.status === 401) {
    clearSession()

    router.push({
      name: "login",
    })

    throw new Error(
      "Tu sesión terminó. Inicia sesión nuevamente."
    )
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
      getValidationError(data) ||
      "No se pudieron cargar los equipos."
    )
  }

  return data
}


async function loadEquipment() {
  loadingEquipment.value = true

  try {
    const data =
      await equipmentRequest(
        EQUIPMENT_API_URL
      )

    equipment.value =
      normalizeCollection(data)
        .filter(
          (item) =>
            !item.is_archived &&
            item.archived_at == null
        )
  } catch (error) {
    errorMessage.value =
      error.message
  } finally {
    loadingEquipment.value = false
  }
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
  } catch (error) {
    errorMessage.value =
      error.message
  } finally {
    loading.value = false
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


async function handleSubmit() {
  saving.value = true
  errorMessage.value = ""
  successMessage.value = ""

  try {
    validateForm()

    const payload =
      buildPayload()

    let savedRepair = null

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

    successMessage.value =
      isEditing.value
        ? "La reparación se actualizó correctamente."
        : "La reparación se creó correctamente."

    const savedId =
      savedRepair?.id ||
      repairId.value

    window.setTimeout(
      () => {
        router.push({
          name: "repair-detail",
          params: {
            id: savedId,
          },
        })
      },
      600
    )
  } catch (error) {
    errorMessage.value =
      error.message
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


function goBack() {
  if (isEditing.value) {
    router.push({
      name: "repair-detail",
      params: {
        id: repairId.value,
      },
    })

    return
  }

  router.push({
    name: "repairs",
  })
}


onMounted(
  async () => {
    await loadEquipment()
    await loadRepair()
  }
)
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
          Registra la información inicial,
          condiciones y requisitos de la reparación.
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
          :disabled="saving || loading"
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
      <article class="form-card equipment-card">
        <div class="card-heading">
          <div class="heading-icon">
            ▣
          </div>

          <div>
            <h2>
              Equipo
            </h2>

            <p>
              Selecciona la máquina que ingresará al taller.
            </p>
          </div>
        </div>

        <div class="form-grid">
          <label class="field full-width">
            <span>
              Buscar equipo
            </span>

            <input
              v-model="equipmentSearch"
              type="search"
              placeholder="Serie, código, marca o modelo"
              :disabled="isEditing"
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
                isEditing
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
                {{ getEquipmentOptionLabel(item) }}
              </option>
            </select>

            <small v-if="isEditing">
              El equipo no puede cambiarse después de crear la reparación.
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
              {{ getEquipmentName(selectedEquipment) }}
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
                selectedEquipment.technical_status_name ||
                selectedEquipment.technical_status ||
                "Sin estado"
              }}
            </strong>
          </div>

          <div class="equipment-data">
            <span>
              Disponibilidad
            </span>

            <strong>
              {{
                selectedEquipment.is_available
                  ? "Disponible"
                  : "No disponible"
              }}
            </strong>
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

        <div class="form-grid three-columns">
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

          <label class="field full-width">
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

          <label class="field full-width">
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

            <span class="switch-control"></span>

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
              v-model="form.requires_external_service"
              type="checkbox"
            />

            <span class="switch-control"></span>

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
              v-model="form.requires_follow_up"
              type="checkbox"
              @change="handleFollowUpChange"
            />

            <span class="switch-control"></span>

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
              v-model.number="form.minimum_photos_required"
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
              v-model="form.follow_up_date"
              type="date"
              :disabled="!form.requires_follow_up"
              :required="form.requires_follow_up"
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
          <label class="field full-width">
            <span>
              Resumen del trabajo
            </span>

            <textarea
              v-model="form.work_summary"
              rows="5"
              placeholder="Describe los trabajos realizados"
            ></textarea>
          </label>

          <label class="field full-width">
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

              <option value="operational_with_observations">
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

          <label class="field full-width">
            <span>
              Observaciones finales
            </span>

            <textarea
              v-model="form.final_observations"
              rows="4"
              placeholder="Condición de salida y observaciones finales"
            ></textarea>
          </label>

          <label class="field full-width">
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
          :disabled="saving"
        >
          {{
            saving
              ? "Guardando..."
              : isEditing
                ? "Guardar cambios"
                : "Crear reparación"
          }}
        </button>
      </footer>
    </form>
  </section>
</template>