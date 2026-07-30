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
  createRepairPartRequest,
  getRepairById,
  getRepairPartRequest,
  updateRepairPartRequest,
} from "../../services/repairs.service"

import "./RepairPartRequestFormView.css"

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const errorMessage = ref("")
const repairSummary = ref(null)

const requestId = computed(() =>
  String(route.params.id || "")
)

const isEdit = computed(() =>
  Boolean(requestId.value)
)

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

const priorities = [
  ["low", "Baja"],
  ["normal", "Normal"],
  ["high", "Alta"],
  ["urgent", "Urgente"],
  ["critical", "Crítica"],
]

function applyRequest(data) {
  form.repair = data.repair || ""
  form.title = data.title || ""
  form.description = data.description || ""
  form.technical_justification =
    data.technical_justification || ""
  form.general_observations =
    data.general_observations || ""
  form.priority = data.priority || "normal"
  form.requires_management_approval =
    Boolean(data.requires_management_approval)
  form.current_responsible_user =
    data.current_responsible_user || null
}

async function loadRepairSummary() {
  if (!form.repair) {
    repairSummary.value = null
    return
  }

  try {
    repairSummary.value =
      await getRepairById(form.repair)
  } catch {
    repairSummary.value = null
  }
}

async function loadForm() {
  loading.value = true
  errorMessage.value = ""

  try {
    if (isEdit.value) {
      const data =
        await getRepairPartRequest(
          requestId.value
        )

      applyRequest(data)
    }

    await loadRepairSummary()
  } catch (error) {
    errorMessage.value =
      error?.message ||
      "No se pudo cargar la solicitud."
  } finally {
    loading.value = false
  }
}

function validateForm() {
  if (!form.repair) {
    return "Debes seleccionar una reparación."
  }

  if (!form.title.trim()) {
    return "El título es obligatorio."
  }

  if (!form.technical_justification.trim()) {
    return "La justificación técnica es obligatoria."
  }

  return ""
}

async function save() {
  const validationMessage = validateForm()

  if (validationMessage) {
    errorMessage.value = validationMessage
    return
  }

  saving.value = true
  errorMessage.value = ""

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
    const saved = isEdit.value
      ? await updateRepairPartRequest(
          requestId.value,
          payload
        )
      : await createRepairPartRequest(
          payload
        )

    router.push({
      name: "repair-part-request-detail",
      params: {
        id: saved.id,
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
    <header>
      <div>
        <span>Pedidos de repuestos</span>
        <h1>
          {{ isEdit ? "Editar solicitud" : "Nueva solicitud" }}
        </h1>
        <p>
          Registra la necesidad técnica vinculada a una reparación.
        </p>
      </div>

      <div class="repair-part-request-form__header-actions">
        <button type="button" @click="cancel">
          Cancelar
        </button>

        <button
          type="button"
          class="primary"
          :disabled="saving || loading"
          @click="save"
        >
          {{ saving ? "Guardando..." : "Guardar" }}
        </button>
      </div>
    </header>

    <p
      v-if="errorMessage"
      class="repair-part-request-form__error"
    >
      {{ errorMessage }}
    </p>

    <section
      v-if="loading"
      class="repair-part-request-form__state"
    >
      Cargando...
    </section>

    <form
      v-else
      class="repair-part-request-form__body"
      @submit.prevent="save"
    >
      <section class="repair-part-request-form__card">
        <header>
          <strong>Reparación relacionada</strong>
          <small>
            La solicitud siempre pertenece a una reparación.
          </small>
        </header>

        <div class="repair-part-request-form__grid">
          <label class="full">
            <span>ID de reparación</span>
            <input
              v-model.trim="form.repair"
              type="text"
              :disabled="isEdit"
              placeholder="UUID de la reparación"
              @blur="loadRepairSummary"
            >
          </label>

          <article
            v-if="repairSummary"
            class="repair-part-request-form__repair"
          >
            <strong>{{ repairSummary.code }}</strong>
            <span>
              {{ repairSummary.equipment_name }}
            </span>
            <small>
              Serie:
              {{ repairSummary.equipment_serial_number }}
            </small>
          </article>
        </div>
      </section>

      <section class="repair-part-request-form__card">
        <header>
          <strong>Datos generales</strong>
          <small>
            Información principal de la solicitud.
          </small>
        </header>

        <div class="repair-part-request-form__grid">
          <label class="full">
            <span>Título</span>
            <input
              v-model.trim="form.title"
              type="text"
              maxlength="200"
              placeholder="Ejemplo: cambio de unidad de imagen negra"
            >
          </label>

          <label>
            <span>Prioridad</span>
            <select v-model="form.priority">
              <option
                v-for="[value, label] in priorities"
                :key="value"
                :value="value"
              >
                {{ label }}
              </option>
            </select>
          </label>

          <label class="checkbox">
            <input
              v-model="form.requires_management_approval"
              type="checkbox"
            >
            <span>Requiere aprobación de gerencia</span>
          </label>

          <label class="full">
            <span>Descripción</span>
            <textarea
              v-model.trim="form.description"
              placeholder="Descripción general de la necesidad"
            />
          </label>

          <label class="full">
            <span>Justificación técnica</span>
            <textarea
              v-model.trim="form.technical_justification"
              placeholder="Diagnóstico, falla y motivo del cambio"
            />
          </label>

          <label class="full">
            <span>Observaciones generales</span>
            <textarea
              v-model.trim="form.general_observations"
              placeholder="Información adicional"
            />
          </label>
        </div>
      </section>

      <footer>
        <button type="button" @click="cancel">
          Cancelar
        </button>

        <button
          type="submit"
          class="primary"
          :disabled="saving"
        >
          {{ saving ? "Guardando..." : "Guardar solicitud" }}
        </button>
      </footer>
    </form>
  </main>
</template>
