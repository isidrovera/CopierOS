<template>
  <div
    ref="rootElement"
    class="service-search-select"
    :class="{
      'service-search-select--disabled': disabled,
      'service-search-select--open': isOpen,
      'service-search-select--error': Boolean(error),
    }"
  >
    <label
      v-if="label"
      class="service-search-select__label"
    >
      {{ label }}

      <span
        v-if="required"
        class="service-search-select__required"
      >
        *
      </span>
    </label>

    <div class="service-search-select__control">
      <button
        v-if="selectedOption"
        type="button"
        class="service-search-select__selected"
        :disabled="disabled"
        @click="openDropdown"
      >
        <span class="service-search-select__selected-icon">
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              d="M5 3h11a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3V6a3 3 0 0 1 3-3Zm0 2a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h11a1 1 0 0 0 1-1V6a1 1 0 0 0-1-1H5Zm2 3h7a1 1 0 1 1 0 2H7a1 1 0 1 1 0-2Zm0 4h7a1 1 0 1 1 0 2H7a1 1 0 1 1 0-2Zm0 4h4a1 1 0 1 1 0 2H7a1 1 0 1 1 0-2Z"
            />
          </svg>
        </span>

        <span class="service-search-select__selected-content">
          <strong>
            {{ getOptionTitle(selectedOption) }}
          </strong>

          <small
            v-if="getOptionSubtitle(selectedOption)"
          >
            {{ getOptionSubtitle(selectedOption) }}
          </small>
        </span>

        <span class="service-search-select__arrow">
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              d="m7.4 9.4 4.6 4.6 4.6-4.6L18 10.8l-6 6-6-6 1.4-1.4Z"
            />
          </svg>
        </span>
      </button>

      <button
        v-else
        type="button"
        class="service-search-select__placeholder"
        :disabled="disabled"
        @click="openDropdown"
      >
        <span class="service-search-select__placeholder-icon">
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              d="M10 3a7 7 0 1 1-4.9 12L2 18.1 3.9 20l3.1-3.1A7 7 0 0 1 10 3Zm0 2a5 5 0 1 0 0 10 5 5 0 0 0 0-10Z"
            />
          </svg>
        </span>

        <span>
          {{ placeholder }}
        </span>

        <span class="service-search-select__arrow">
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              d="m7.4 9.4 4.6 4.6 4.6-4.6L18 10.8l-6 6-6-6 1.4-1.4Z"
            />
          </svg>
        </span>
      </button>

      <button
        v-if="
          selectedOption
          && clearable
          && !disabled
        "
        type="button"
        class="service-search-select__clear"
        title="Limpiar selección"
        @click.stop="clearSelection"
      >
        <svg
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            d="M6.7 5.3 12 10.6l5.3-5.3 1.4 1.4-5.3 5.3 5.3 5.3-1.4 1.4-5.3-5.3-5.3 5.3-1.4-1.4 5.3-5.3-5.3-5.3 1.4-1.4Z"
          />
        </svg>
      </button>
    </div>

    <p
      v-if="helpText && !error"
      class="service-search-select__help"
    >
      {{ helpText }}
    </p>

    <p
      v-if="error"
      class="service-search-select__error-message"
    >
      {{ error }}
    </p>

    <Transition name="service-select-fade">
      <div
        v-if="isOpen"
        class="service-search-select__dropdown"
      >
        <div class="service-search-select__search">
          <span class="service-search-select__search-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="M10 3a7 7 0 1 1-4.9 12L2 18.1 3.9 20l3.1-3.1A7 7 0 0 1 10 3Zm0 2a5 5 0 1 0 0 10 5 5 0 0 0 0-10Z"
              />
            </svg>
          </span>

          <input
            ref="searchInput"
            v-model="searchValue"
            type="search"
            :placeholder="searchPlaceholder"
            autocomplete="off"
            @input="handleSearchInput"
            @keydown.escape="closeDropdown"
            @keydown.down.prevent="moveHighlight(1)"
            @keydown.up.prevent="moveHighlight(-1)"
            @keydown.enter.prevent="selectHighlighted"
          />

          <span
            v-if="loading"
            class="service-search-select__spinner"
          />
        </div>

        <div class="service-search-select__results">
          <button
            v-for="(option, index) in displayedOptions"
            :key="getOptionKey(option)"
            type="button"
            class="service-search-select__option"
            :class="{
              'service-search-select__option--selected': (
                isSelected(option)
              ),
              'service-search-select__option--highlighted': (
                highlightedIndex === index
              ),
            }"
            @mouseenter="highlightedIndex = index"
            @click="selectOption(option)"
          >
            <span class="service-search-select__option-icon">
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M5 2h11a4 4 0 0 1 4 4v12a4 4 0 0 1-4 4H5a4 4 0 0 1-4-4V6a4 4 0 0 1 4-4Zm0 2a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2H5Zm2 3h7a1 1 0 0 1 0 2H7a1 1 0 0 1 0-2Zm0 4h7a1 1 0 0 1 0 2H7a1 1 0 0 1 0-2Zm0 4h4a1 1 0 0 1 0 2H7a1 1 0 0 1 0-2Z"
                />
              </svg>
            </span>

            <span class="service-search-select__option-content">
              <strong>
                {{ getOptionTitle(option) }}
              </strong>

              <small
                v-if="getOptionSubtitle(option)"
              >
                {{ getOptionSubtitle(option) }}
              </small>

              <span
                v-if="getOptionMeta(option)"
                class="service-search-select__option-meta"
              >
                {{ getOptionMeta(option) }}
              </span>
            </span>

            <span
              v-if="isSelected(option)"
              class="service-search-select__check"
            >
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="m9.2 16.2-4.4-4.4 1.4-1.4 3 3 8.6-8.6 1.4 1.4-10 10Z"
                />
              </svg>
            </span>
          </button>

          <div
            v-if="
              !loading
              && displayedOptions.length === 0
            "
            class="service-search-select__empty"
          >
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="M10 3a7 7 0 1 1-4.9 12L2 18.1 3.9 20l3.1-3.1A7 7 0 0 1 10 3Zm0 2a5 5 0 1 0 0 10 5 5 0 0 0 0-10Zm-3 4h6v2H7V9Z"
              />
            </svg>

            <strong>
              No se encontraron resultados
            </strong>

            <span>
              Prueba buscando por serie, código, marca,
              modelo, cliente o sede.
            </span>
          </div>

          <div
            v-if="
              loading
              && displayedOptions.length === 0
            "
            class="service-search-select__loading"
          >
            <span class="service-search-select__spinner" />

            <span>
              Buscando equipos...
            </span>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue"

import "./service-search-select.css"


const props = defineProps({
  modelValue: {
    type: [
      String,
      Number,
    ],
    default: "",
  },

  options: {
    type: Array,
    default: () => [],
  },

  selected: {
    type: Object,
    default: null,
  },

  label: {
    type: String,
    default: "",
  },

  placeholder: {
    type: String,
    default: "Seleccionar",
  },

  searchPlaceholder: {
    type: String,
    default: "Buscar...",
  },

  helpText: {
    type: String,
    default: "",
  },

  error: {
    type: String,
    default: "",
  },

  required: {
    type: Boolean,
    default: false,
  },

  disabled: {
    type: Boolean,
    default: false,
  },

  loading: {
    type: Boolean,
    default: false,
  },

  clearable: {
    type: Boolean,
    default: true,
  },

  remoteSearch: {
    type: Boolean,
    default: true,
  },

  optionValue: {
    type: String,
    default: "equipment",
  },

  optionLabel: {
    type: String,
    default: "label",
  },

  optionSubtitle: {
    type: String,
    default: "",
  },

  optionMeta: {
    type: String,
    default: "",
  },
})


const emit = defineEmits([
  "update:modelValue",
  "select",
  "clear",
  "search",
  "open",
  "close",
])


const rootElement = ref(null)
const searchInput = ref(null)

const isOpen = ref(false)
const searchValue = ref("")
const highlightedIndex = ref(-1)


const selectedOption = computed(() => {
  if (props.selected) {
    return props.selected
  }

  if (
    props.modelValue === ""
    || props.modelValue === null
    || props.modelValue === undefined
  ) {
    return null
  }

  return (
    props.options.find(
      (option) => (
        String(
          getOptionValue(option),
        ) === String(
          props.modelValue,
        )
      ),
    )
    || null
  )
})


const displayedOptions = computed(() => {
  if (props.remoteSearch) {
    return props.options
  }

  const query = searchValue.value
    .trim()
    .toLowerCase()

  if (!query) {
    return props.options
  }

  return props.options.filter(
    (option) => {
      const searchableContent = [
        getOptionTitle(option),
        getOptionSubtitle(option),
        getOptionMeta(option),
        option?.serial_number,
        option?.internal_code,
        option?.brand_name,
        option?.model_name,
        option?.snapshot?.customer_name,
        option?.snapshot?.branch_name,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()

      return searchableContent.includes(
        query,
      )
    },
  )
})


let searchTimer = null


function getOptionValue(option) {
  if (!option) {
    return ""
  }

  return (
    option[props.optionValue]
    ?? option.id
    ?? ""
  )
}


function getOptionKey(option) {
  return String(
    getOptionValue(option)
    || option?.label
    || JSON.stringify(option),
  )
}


function getOptionTitle(option) {
  if (!option) {
    return ""
  }

  const explicitLabel = (
    option[props.optionLabel]
  )

  if (explicitLabel) {
    return explicitLabel
  }

  return (
    option.label
    || option.name
    || option.serial_number
    || option.internal_code
    || "Sin descripción"
  )
}


function getOptionSubtitle(option) {
  if (!option) {
    return ""
  }

  if (
    props.optionSubtitle
    && option[props.optionSubtitle]
  ) {
    return option[props.optionSubtitle]
  }

  const brandModel = [
    option.brand_name,
    option.model_name,
  ]
    .filter(Boolean)
    .join(" ")

  const customer = (
    option?.snapshot?.customer_name
    || option?.owner_customer_name
    || ""
  )

  if (
    customer
    && !getOptionTitle(option).includes(customer)
  ) {
    return [
      brandModel,
      customer,
    ]
      .filter(Boolean)
      .join(" · ")
  }

  return brandModel
}


function getOptionMeta(option) {
  if (!option) {
    return ""
  }

  if (
    props.optionMeta
    && option[props.optionMeta]
  ) {
    return option[props.optionMeta]
  }

  const branch = (
    option?.snapshot?.branch_name
    || ""
  )

  const address = (
    option?.snapshot?.address
    || ""
  )

  return [
    branch,
    address,
  ]
    .filter(Boolean)
    .join(" · ")
}


function isSelected(option) {
  if (!selectedOption.value) {
    return false
  }

  return (
    String(
      getOptionValue(option),
    ) === String(
      getOptionValue(
        selectedOption.value,
      ),
    )
  )
}


async function openDropdown() {
  if (props.disabled) {
    return
  }

  isOpen.value = true
  highlightedIndex.value = -1

  emit("open")

  await nextTick()

  searchInput.value?.focus()
}


function closeDropdown() {
  if (!isOpen.value) {
    return
  }

  isOpen.value = false
  highlightedIndex.value = -1

  emit("close")
}


function selectOption(option) {
  const value = getOptionValue(option)

  emit(
    "update:modelValue",
    value,
  )

  emit(
    "select",
    option,
  )

  searchValue.value = ""
  closeDropdown()
}


function clearSelection() {
  emit(
    "update:modelValue",
    "",
  )

  emit("clear")

  searchValue.value = ""
  highlightedIndex.value = -1
}


function handleSearchInput() {
  highlightedIndex.value = -1

  if (searchTimer) {
    clearTimeout(searchTimer)
  }

  searchTimer = setTimeout(
    () => {
      emit(
        "search",
        searchValue.value.trim(),
      )
    },
    350,
  )
}


function moveHighlight(direction) {
  const total = displayedOptions.value.length

  if (!total) {
    highlightedIndex.value = -1
    return
  }

  let nextIndex = (
    highlightedIndex.value + direction
  )

  if (nextIndex < 0) {
    nextIndex = total - 1
  }

  if (nextIndex >= total) {
    nextIndex = 0
  }

  highlightedIndex.value = nextIndex
}


function selectHighlighted() {
  if (
    highlightedIndex.value < 0
    || highlightedIndex.value
      >= displayedOptions.value.length
  ) {
    return
  }

  selectOption(
    displayedOptions.value[
      highlightedIndex.value
    ],
  )
}


function handleDocumentClick(event) {
  if (
    rootElement.value
    && !rootElement.value.contains(
      event.target,
    )
  ) {
    closeDropdown()
  }
}


watch(
  () => props.disabled,
  (disabled) => {
    if (disabled) {
      closeDropdown()
    }
  },
)


watch(
  () => props.options,
  () => {
    if (
      highlightedIndex.value
      >= displayedOptions.value.length
    ) {
      highlightedIndex.value = -1
    }
  },
  {
    deep: true,
  },
)


onMounted(() => {
  document.addEventListener(
    "mousedown",
    handleDocumentClick,
  )
})


onBeforeUnmount(() => {
  document.removeEventListener(
    "mousedown",
    handleDocumentClick,
  )

  if (searchTimer) {
    clearTimeout(searchTimer)
  }
})
</script>