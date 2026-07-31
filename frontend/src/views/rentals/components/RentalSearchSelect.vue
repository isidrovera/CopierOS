<script setup>
import {
  computed,
  onBeforeUnmount,
  ref,
  watch,
} from "vue"

import "./rental-search-select.css"


const props = defineProps({
  modelValue: {
    type: [String, Number, null],
    default: "",
  },
  label: {
    type: String,
    required: true,
  },
  placeholder: {
    type: String,
    default: "Buscar...",
  },
  required: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  loader: {
    type: Function,
    required: true,
  },
  initialLabel: {
    type: String,
    default: "",
  },
})

const emit = defineEmits([
  "update:modelValue",
  "select",
])

const search = ref(props.initialLabel)
const options = ref([])
const loading = ref(false)
const open = ref(false)
const error = ref("")
let timer = null

const hasValue = computed(() =>
  Boolean(props.modelValue)
)


function normalizeResults(data) {
  if (Array.isArray(data)) {
    return data
  }

  if (Array.isArray(data?.results)) {
    return data.results
  }

  return []
}


async function loadOptions() {
  loading.value = true
  error.value = ""

  try {
    const result = await props.loader(
      search.value.trim()
    )

    options.value = normalizeResults(result)
    open.value = true
  } catch (requestError) {
    options.value = []
    error.value =
      requestError?.message ||
      "No se pudo realizar la búsqueda."
  } finally {
    loading.value = false
  }
}


function scheduleSearch() {
  clearTimeout(timer)

  timer = setTimeout(() => {
    loadOptions()
  }, 280)
}


function optionLabel(option) {
  return String(
    option?.label ||
    option?.display ||
    option?.name ||
    option?.code ||
    option?.id ||
    ""
  )
}


function selectOption(option) {
  const value =
    option?.id ??
    option?.value ??
    ""

  search.value =
    optionLabel(option)

  open.value = false

  emit(
    "update:modelValue",
    value
  )

  emit(
    "select",
    option
  )
}


function clearSelection() {
  search.value = ""
  options.value = []
  open.value = false

  emit(
    "update:modelValue",
    ""
  )

  emit(
    "select",
    null
  )
}


function handleFocus() {
  if (!props.disabled) {
    loadOptions()
  }
}


watch(
  () => props.initialLabel,
  (value) => {
    if (value) {
      search.value = value
    }
  }
)


watch(
  () => props.modelValue,
  (value) => {
    if (!value && hasValue.value) {
      search.value = ""
    }
  }
)


onBeforeUnmount(() => {
  clearTimeout(timer)
})
</script>

<template>
  <label class="rental-search-select">
    <span class="field-label">
      {{ label }}

      <strong v-if="required">
        *
      </strong>
    </span>

    <div class="search-control">
      <span class="search-icon">
        ⌕
      </span>

      <input
        v-model="search"
        type="search"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        autocomplete="off"
        @focus="handleFocus"
        @input="scheduleSearch"
      >

      <span
        v-if="loading"
        class="mini-spinner"
      />

      <button
        v-else-if="modelValue || search"
        type="button"
        class="clear-search-button"
        aria-label="Limpiar selección"
        @click="clearSelection"
      >
        ×
      </button>
    </div>

    <div
      v-if="open && !disabled"
      class="search-results"
    >
      <button
        v-for="option in options"
        :key="option.id || option.value"
        type="button"
        class="search-result"
        @mousedown.prevent="
          selectOption(option)
        "
      >
        <strong>
          {{ optionLabel(option) }}
        </strong>

        <small v-if="option.description">
          {{ option.description }}
        </small>
      </button>

      <p
        v-if="
          !loading &&
          !options.length
        "
        class="empty-search-result"
      >
        No se encontraron coincidencias.
      </p>
    </div>

    <small
      v-if="error"
      class="field-error"
    >
      {{ error }}
    </small>
  </label>
</template>
