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
  createRentalResource,
  getRentalResource,
  updateRentalResource,
} from "../../services/rentals.service"

import RentalSearchSelect from "./RentalSearchSelect.vue"

import "./rentals-form.css"


const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  resource: {
    type: String,
    required: true,
  },
  listRoute: {
    type: String,
    required: true,
  },
  fields: {
    type: Array,
    required: true,
  },
  defaults: {
    type: Object,
    default: () => ({}),
  },
})

const route = useRoute()
const router = useRouter()

const form = reactive({ ...props.defaults })
const selectedLabels = reactive({})

const loading = ref(false)
const saving = ref(false)
const errorMessage = ref("")

const resourceId = computed(() => route.params.id || "")
const isEditing = computed(() => Boolean(resourceId.value))

const pageTitle = computed(() => (
  isEditing.value
    ? `Editar ${props.title}`
    : `Nueva ${props.title}`
))

function rows(fields) {
  return fields.filter((field) => field.type !== "section")
}

function initializeForm() {
  for (const field of rows(props.fields)) {
    if (form[field.key] === undefined) {
      form[field.key] = field.default ?? ""
    }
  }
}

function displayValue(data, field) {
  if (field.displayKey && data[field.displayKey]) {
    return String(data[field.displayKey])
  }

  return ""
}

async function loadRecord() {
  if (!resourceId.value) {
    return
  }

  loading.value = true
  errorMessage.value = ""

  try {
    const data = await getRentalResource(
      props.resource,
      resourceId.value
    )

    for (const field of rows(props.fields)) {
      if (data[field.key] !== undefined) {
        form[field.key] = data[field.key] ?? ""
      }

      if (field.type === "search") {
        selectedLabels[field.key] = displayValue(data, field)
      }
    }
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

function fieldDisabled(field) {
  if (typeof field.disabled === "function") {
    return field.disabled(form)
  }

  return Boolean(field.disabled)
}

function fieldLoader(field) {
  return (search) => field.loader(search, form)
}

function handleSelection(field, option) {
  selectedLabels[field.key] = option?.label || ""

  if (typeof field.onSelect === "function") {
    field.onSelect(option, form, selectedLabels)
  }
}

function buildPayload() {
  const payload = {}

  for (const field of rows(props.fields)) {
    if (field.readOnly) {
      continue
    }

    let value = form[field.key]

    if (field.type === "number" && value !== "") {
      value = Number(value)
    }

    if (field.type === "checkbox") {
      value = Boolean(value)
    }

    if (field.nullWhenEmpty && value === "") {
      value = null
    }

    payload[field.key] = value
  }

  return payload
}

async function submitForm() {
  saving.value = true
  errorMessage.value = ""

  try {
    const payload = buildPayload()

    if (isEditing.value) {
      await updateRentalResource(
        props.resource,
        resourceId.value,
        payload
      )
    } else {
      await createRentalResource(
        props.resource,
        payload
      )
    }

    router.push({ name: props.listRoute })
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    saving.value = false
  }
}

function goBack() {
  router.push({ name: props.listRoute })
}

initializeForm()

onMounted(loadRecord)
</script>

<template>
  <section class="rental-form-page">
    <header class="page-header">
      <div>
        <span class="page-kicker">Módulo de alquileres</span>
        <h2>{{ pageTitle }}</h2>
        <p>
          Busca y selecciona los registros por nombre, código, modelo o serie.
          Los identificadores internos no se muestran.
        </p>
      </div>

      <button
        type="button"
        class="secondary-button"
        @click="goBack"
      >
        Volver
      </button>
    </header>

    <div v-if="errorMessage" class="message error-message">
      {{ errorMessage }}
    </div>

    <div v-if="loading" class="loading-card">
      <span class="spinner"></span>
      Cargando información...
    </div>

    <form
      v-else
      class="rental-form"
      @submit.prevent="submitForm"
    >
      <template
        v-for="field in fields"
        :key="field.key || field.label"
      >
        <section
          v-if="field.type === 'section'"
          class="form-section-heading"
        >
          <span>{{ field.kicker || "Información" }}</span>
          <h3>{{ field.label }}</h3>
          <p v-if="field.help">{{ field.help }}</p>
        </section>

        <RentalSearchSelect
          v-else-if="field.type === 'search'"
          v-model="form[field.key]"
          :class="{ 'field-full': field.full }"
          :label="field.label"
          :placeholder="field.placeholder"
          :required="field.required"
          :disabled="fieldDisabled(field)"
          :loader="fieldLoader(field)"
          :initial-label="selectedLabels[field.key]"
          @select="handleSelection(field, $event)"
        />

        <label
          v-else-if="field.type === 'textarea'"
          :class="{ 'field-full': field.full }"
          class="form-field"
        >
          <span>{{ field.label }} <strong v-if="field.required">*</strong></span>
          <textarea
            v-model="form[field.key]"
            :required="field.required"
            :placeholder="field.placeholder || ''"
            rows="4"
          ></textarea>
        </label>

        <label
          v-else-if="field.type === 'select'"
          :class="{ 'field-full': field.full }"
          class="form-field"
        >
          <span>{{ field.label }} <strong v-if="field.required">*</strong></span>
          <select
            v-model="form[field.key]"
            :required="field.required"
          >
            <option value="">Seleccionar</option>
            <option
              v-for="option in field.options"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </label>

        <label
          v-else-if="field.type === 'checkbox'"
          :class="{ 'field-full': field.full }"
          class="checkbox-field"
        >
          <input
            v-model="form[field.key]"
            type="checkbox"
          >
          <span>
            <strong>{{ field.label }}</strong>
            <small v-if="field.help">{{ field.help }}</small>
          </span>
        </label>

        <label
          v-else
          :class="{ 'field-full': field.full }"
          class="form-field"
        >
          <span>{{ field.label }} <strong v-if="field.required">*</strong></span>
          <input
            v-model="form[field.key]"
            :type="field.type || 'text'"
            :required="field.required"
            :placeholder="field.placeholder || ''"
            :min="field.min"
            :max="field.max"
          >
        </label>
      </template>

      <footer class="form-actions field-full">
        <button
          type="button"
          class="secondary-button"
          :disabled="saving"
          @click="goBack"
        >
          Cancelar
        </button>

        <button
          type="submit"
          class="primary-button"
          :disabled="saving"
        >
          <span v-if="saving" class="button-spinner"></span>
          {{ saving ? "Guardando..." : "Guardar" }}
        </button>
      </footer>
    </form>
  </section>
</template>
