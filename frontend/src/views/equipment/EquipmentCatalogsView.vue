<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue"

import {
  archiveComponentCompatibility,
  archiveComponentType,
  archiveEquipmentBrand,
  archiveEquipmentComponent,
  archiveEquipmentModel,
  archiveEquipmentType,
  createComponentCompatibility,
  createComponentType,
  createEquipmentBrand,
  createEquipmentComponent,
  createEquipmentModel,
  createEquipmentType,
  getComponentCompatibilities,
  getComponentTypes,
  getEquipmentBrands,
  getEquipmentComponents,
  getEquipmentModels,
  getEquipmentTypes,
  restoreComponentCompatibility,
  restoreComponentType,
  restoreEquipmentBrand,
  restoreEquipmentComponent,
  restoreEquipmentModel,
  restoreEquipmentType,
  updateComponentCompatibility,
  updateComponentType,
  updateEquipmentBrand,
  updateEquipmentComponent,
  updateEquipmentModel,
  updateEquipmentType,
} from "../../services/equipment.service"


const activeTab = ref("types")

const loading = ref(false)
const saving = ref(false)
const processingId = ref("")

const errorMessage = ref("")
const successMessage = ref("")

const includeArchived = ref(false)
const search = ref("")

const modalOpen = ref(false)
const editingId = ref("")

const equipmentTypes = ref([])
const brands = ref([])
const equipmentModels = ref([])

const componentTypes = ref([])
const components = ref([])
const compatibilities = ref([])


const tabDefinitions = [
  {
    id: "types",
    label: "Tipos de equipo",
  },
  {
    id: "brands",
    label: "Marcas",
  },
  {
    id: "models",
    label: "Modelos",
  },
  {
    id: "componentTypes",
    label: "Tipos de componentes",
  },
  {
    id: "components",
    label: "Unidades técnicas",
  },
  {
    id: "compatibilities",
    label: "Compatibilidades",
  },
]


const typeForm = reactive({
  code: "",
  name: "",
  description: "",
  requires_color_definition: true,
  requires_meter: true,
  allows_accessories: true,
  is_active: true,
  display_order: 0,
})


const brandForm = reactive({
  code: "",
  name: "",
  legal_name: "",
  country_code: "",
  country_name: "",
  website: "",
  description: "",
  is_active: true,
  display_order: 0,
})


const modelForm = reactive({
  code: "",
  brand: "",
  equipment_type: "",
  name: "",
  commercial_name: "",
  family: "",
  manufacturer_reference: "",
  color_mode: "not_applicable",
  technology: "not_defined",
  maximum_paper_size: "not_defined",
  is_multifunction: false,
  supports_printing: true,
  supports_copying: true,
  supports_scanning: true,
  supports_fax: false,
  supports_network: true,
  supports_duplex: true,
  supports_accessories: true,
  supports_technical_units: true,
  has_total_meter: true,
  has_black_meter: true,
  has_color_meter: false,
  has_scan_meter: false,
  technical_notes: "",
  description: "",
  is_active: true,
  display_order: 0,
})


const componentTypeForm = reactive({
  code: "",
  name: "",
  category: "technical_unit",
  description: "",
  requires_color: false,
  requires_serial_number: false,
  requires_meter: false,
  controls_stock: true,
  is_active: true,
  display_order: 0,
})


const componentForm = reactive({
  component_type: "",
  parent_component: "",
  code: "",
  name: "",
  manufacturer_code: "",
  alternative_code: "",
  color: "not_applicable",
  condition_control: "none",
  expected_life_meter: null,
  expected_life_days: null,
  requires_individual_serial: false,
  is_consumable: false,
  is_reusable: false,
  can_be_repaired: false,
  requires_removed_part_tracking: false,
  unit_of_measure: "unit",
  description: "",
  technical_notes: "",
  is_active: true,
  display_order: 0,
})


const compatibilityForm = reactive({
  component: "",
  equipment_family: null,
  equipment_model: "",
  compatibility_type: "compatible",
  position: "not_applicable",
  manufacturer_reference: "",
  requires_adjustment: false,
  adjustment_instructions: "",
  is_preferred: false,
  technical_notes: "",
  is_active: true,
  display_order: 0,
})


const currentItems = computed(() => {
  const collections = {
    types: equipmentTypes.value,
    brands: brands.value,
    models: equipmentModels.value,
    componentTypes: componentTypes.value,
    components: components.value,
    compatibilities: compatibilities.value,
  }

  return collections[activeTab.value] || []
})


const activeTabLabel = computed(() => {
  return (
    tabDefinitions.find(
      (tab) => tab.id === activeTab.value
    )?.label || "Catálogo"
  )
})


const modalTitle = computed(() => {
  const names = {
    types: "tipo de equipo",
    brands: "marca",
    models: "modelo",
    componentTypes: "tipo de componente",
    components: "unidad o componente",
    compatibilities: "compatibilidad",
  }

  const name =
    names[activeTab.value] || "registro"

  return editingId.value
    ? `Editar ${name}`
    : `Nuevo ${name}`
})


const activeComponentTypes = computed(() => {
  return componentTypes.value.filter(
    (item) =>
      !item.is_archived &&
      item.is_active
  )
})


const activeComponents = computed(() => {
  return components.value.filter(
    (item) =>
      !item.is_archived &&
      item.is_active
  )
})


const activeEquipmentModels = computed(() => {
  return equipmentModels.value.filter(
    (item) =>
      !item.is_archived &&
      item.is_active
  )
})


function normalizeList(response) {
  return Array.isArray(response)
    ? response
    : response?.results || []
}


function clearMessages() {
  errorMessage.value = ""
  successMessage.value = ""
}


function getTabCount(tabId) {
  const collections = {
    types: equipmentTypes.value,
    brands: brands.value,
    models: equipmentModels.value,
    componentTypes: componentTypes.value,
    components: components.value,
    compatibilities: compatibilities.value,
  }

  return collections[tabId]?.length || 0
}


function getRecordName(item) {
  if (activeTab.value === "compatibilities") {
    return (
      `${item.component_name || "Componente"} - ` +
      `${item.target_name || item.equipment_model_name || "modelo"}`
    )
  }

  return (
    item.name ||
    item.code ||
    "el registro"
  )
}


function getStatusLabel(item) {
  if (item.is_archived) {
    return "Archivado"
  }

  if (item.is_active === false) {
    return "Inactivo"
  }

  return "Activo"
}


function getStatusClass(item) {
  if (item.is_archived) {
    return "archived-status"
  }

  if (item.is_active === false) {
    return "inactive-status"
  }

  return "active-status"
}


async function loadCatalogs() {
  loading.value = true
  clearMessages()

  try {
    const [
      typesResponse,
      brandsResponse,
      modelsResponse,
      componentTypesResponse,
      componentsResponse,
      compatibilitiesResponse,
    ] = await Promise.all([
      getEquipmentTypes({
        search: search.value,
        includeArchived:
          includeArchived.value,
      }),
      getEquipmentBrands({
        search: search.value,
        includeArchived:
          includeArchived.value,
      }),
      getEquipmentModels({
        search: search.value,
        includeArchived:
          includeArchived.value,
      }),
      getComponentTypes({
        search: search.value,
        includeArchived:
          includeArchived.value,
      }),
      getEquipmentComponents({
        search: search.value,
        includeArchived:
          includeArchived.value,
      }),
      getComponentCompatibilities({
        search: search.value,
        includeArchived:
          includeArchived.value,
      }),
    ])

    equipmentTypes.value =
      normalizeList(typesResponse)

    brands.value =
      normalizeList(brandsResponse)

    equipmentModels.value =
      normalizeList(modelsResponse)

    componentTypes.value =
      normalizeList(componentTypesResponse)

    components.value =
      normalizeList(componentsResponse)

    compatibilities.value =
      normalizeList(compatibilitiesResponse)
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudieron cargar los catálogos."
  } finally {
    loading.value = false
  }
}


function resetForms() {
  editingId.value = ""

  Object.assign(typeForm, {
    code: "",
    name: "",
    description: "",
    requires_color_definition: true,
    requires_meter: true,
    allows_accessories: true,
    is_active: true,
    display_order: 0,
  })

  Object.assign(brandForm, {
    code: "",
    name: "",
    legal_name: "",
    country_code: "",
    country_name: "",
    website: "",
    description: "",
    is_active: true,
    display_order: 0,
  })

  Object.assign(modelForm, {
    code: "",
    brand: "",
    equipment_type: "",
    name: "",
    commercial_name: "",
    family: "",
    manufacturer_reference: "",
    color_mode: "not_applicable",
    technology: "not_defined",
    maximum_paper_size: "not_defined",
    is_multifunction: false,
    supports_printing: true,
    supports_copying: true,
    supports_scanning: true,
    supports_fax: false,
    supports_network: true,
    supports_duplex: true,
    supports_accessories: true,
    supports_technical_units: true,
    has_total_meter: true,
    has_black_meter: true,
    has_color_meter: false,
    has_scan_meter: false,
    technical_notes: "",
    description: "",
    is_active: true,
    display_order: 0,
  })

  Object.assign(componentTypeForm, {
    code: "",
    name: "",
    category: "technical_unit",
    description: "",
    requires_color: false,
    requires_serial_number: false,
    requires_meter: false,
    controls_stock: true,
    is_active: true,
    display_order: 0,
  })

  Object.assign(componentForm, {
    component_type: "",
    parent_component: "",
    code: "",
    name: "",
    manufacturer_code: "",
    alternative_code: "",
    color: "not_applicable",
    condition_control: "none",
    expected_life_meter: null,
    expected_life_days: null,
    requires_individual_serial: false,
    is_consumable: false,
    is_reusable: false,
    can_be_repaired: false,
    requires_removed_part_tracking: false,
    unit_of_measure: "unit",
    description: "",
    technical_notes: "",
    is_active: true,
    display_order: 0,
  })

  Object.assign(compatibilityForm, {
    component: "",
    equipment_family: null,
    equipment_model: "",
    compatibility_type: "compatible",
    position: "not_applicable",
    manufacturer_reference: "",
    requires_adjustment: false,
    adjustment_instructions: "",
    is_preferred: false,
    technical_notes: "",
    is_active: true,
    display_order: 0,
  })
}


function openCreateModal() {
  clearMessages()
  resetForms()
  modalOpen.value = true
}


function openEditModal(item) {
  clearMessages()
  resetForms()

  editingId.value = item.id

  if (activeTab.value === "types") {
    Object.assign(typeForm, {
      code: item.code || "",
      name: item.name || "",
      description:
        item.description || "",
      requires_color_definition:
        Boolean(
          item.requires_color_definition
        ),
      requires_meter:
        Boolean(item.requires_meter),
      allows_accessories:
        Boolean(item.allows_accessories),
      is_active:
        Boolean(item.is_active),
      display_order:
        Number(item.display_order || 0),
    })
  }

  if (activeTab.value === "brands") {
    Object.assign(brandForm, {
      code: item.code || "",
      name: item.name || "",
      legal_name:
        item.legal_name || "",
      country_code:
        item.country_code || "",
      country_name:
        item.country_name || "",
      website:
        item.website || "",
      description:
        item.description || "",
      is_active:
        Boolean(item.is_active),
      display_order:
        Number(item.display_order || 0),
    })
  }

  if (activeTab.value === "models") {
    Object.assign(modelForm, {
      code: item.code || "",
      brand: item.brand || "",
      equipment_type:
        item.equipment_type || "",
      name: item.name || "",
      commercial_name:
        item.commercial_name || "",
      family: item.family || "",
      manufacturer_reference:
        item.manufacturer_reference || "",
      color_mode:
        item.color_mode ||
        "not_applicable",
      technology:
        item.technology ||
        "not_defined",
      maximum_paper_size:
        item.maximum_paper_size ||
        "not_defined",
      is_multifunction:
        Boolean(item.is_multifunction),
      supports_printing:
        Boolean(item.supports_printing),
      supports_copying:
        Boolean(item.supports_copying),
      supports_scanning:
        Boolean(item.supports_scanning),
      supports_fax:
        Boolean(item.supports_fax),
      supports_network:
        Boolean(item.supports_network),
      supports_duplex:
        Boolean(item.supports_duplex),
      supports_accessories:
        Boolean(item.supports_accessories),
      supports_technical_units:
        Boolean(
          item.supports_technical_units
        ),
      has_total_meter:
        Boolean(item.has_total_meter),
      has_black_meter:
        Boolean(item.has_black_meter),
      has_color_meter:
        Boolean(item.has_color_meter),
      has_scan_meter:
        Boolean(item.has_scan_meter),
      technical_notes:
        item.technical_notes || "",
      description:
        item.description || "",
      is_active:
        Boolean(item.is_active),
      display_order:
        Number(item.display_order || 0),
    })
  }

  if (
    activeTab.value ===
    "componentTypes"
  ) {
    Object.assign(componentTypeForm, {
      code: item.code || "",
      name: item.name || "",
      category:
        item.category ||
        "technical_unit",
      description:
        item.description || "",
      requires_color:
        Boolean(item.requires_color),
      requires_serial_number:
        Boolean(
          item.requires_serial_number
        ),
      requires_meter:
        Boolean(item.requires_meter),
      controls_stock:
        Boolean(item.controls_stock),
      is_active:
        Boolean(item.is_active),
      display_order:
        Number(item.display_order || 0),
    })
  }

  if (
    activeTab.value ===
    "components"
  ) {
    Object.assign(componentForm, {
      component_type:
        item.component_type || "",
      parent_component:
        item.parent_component || "",
      code: item.code || "",
      name: item.name || "",
      manufacturer_code:
        item.manufacturer_code || "",
      alternative_code:
        item.alternative_code || "",
      color:
        item.color ||
        "not_applicable",
      condition_control:
        item.condition_control ||
        "none",
      expected_life_meter:
        item.expected_life_meter ?? null,
      expected_life_days:
        item.expected_life_days ?? null,
      requires_individual_serial:
        Boolean(
          item.requires_individual_serial
        ),
      is_consumable:
        Boolean(item.is_consumable),
      is_reusable:
        Boolean(item.is_reusable),
      can_be_repaired:
        Boolean(item.can_be_repaired),
      requires_removed_part_tracking:
        Boolean(
          item.requires_removed_part_tracking
        ),
      unit_of_measure:
        item.unit_of_measure || "unit",
      description:
        item.description || "",
      technical_notes:
        item.technical_notes || "",
      is_active:
        Boolean(item.is_active),
      display_order:
        Number(item.display_order || 0),
    })
  }

  if (
    activeTab.value ===
    "compatibilities"
  ) {
    Object.assign(compatibilityForm, {
      component:
        item.component || "",
      equipment_family:
        item.equipment_family || null,
      equipment_model:
        item.equipment_model || "",
      compatibility_type:
        item.compatibility_type ||
        "compatible",
      position:
        item.position ||
        "not_applicable",
      manufacturer_reference:
        item.manufacturer_reference || "",
      requires_adjustment:
        Boolean(
          item.requires_adjustment
        ),
      adjustment_instructions:
        item.adjustment_instructions || "",
      is_preferred:
        Boolean(item.is_preferred),
      technical_notes:
        item.technical_notes || "",
      is_active:
        Boolean(item.is_active),
      display_order:
        Number(item.display_order || 0),
    })
  }

  modalOpen.value = true
}


function closeModal() {
  if (saving.value) {
    return
  }

  modalOpen.value = false
  resetForms()
}


function validateCurrentForm() {
  if (activeTab.value === "types") {
    if (!typeForm.code.trim()) {
      return "El código es obligatorio."
    }

    if (!typeForm.name.trim()) {
      return "El nombre es obligatorio."
    }
  }

  if (activeTab.value === "brands") {
    if (!brandForm.code.trim()) {
      return "El código es obligatorio."
    }

    if (!brandForm.name.trim()) {
      return "El nombre es obligatorio."
    }

    if (
      brandForm.country_code &&
      brandForm.country_code
        .trim()
        .length !== 2
    ) {
      return (
        "El código de país debe " +
        "tener dos letras."
      )
    }
  }

  if (activeTab.value === "models") {
    if (!modelForm.code.trim()) {
      return "El código es obligatorio."
    }

    if (!modelForm.brand) {
      return "Selecciona una marca."
    }

    if (!modelForm.equipment_type) {
      return (
        "Selecciona un tipo de equipo."
      )
    }

    if (!modelForm.name.trim()) {
      return (
        "El nombre del modelo es obligatorio."
      )
    }

    if (
      modelForm.color_mode ===
        "monochrome" &&
      modelForm.has_color_meter
    ) {
      return (
        "Un modelo blanco y negro " +
        "no puede tener contador de color."
      )
    }

    if (
      modelForm.color_mode === "color" &&
      !modelForm.has_color_meter
    ) {
      return (
        "Un modelo de color debe " +
        "tener contador de color."
      )
    }
  }

  if (
    activeTab.value ===
    "componentTypes"
  ) {
    if (!componentTypeForm.code.trim()) {
      return (
        "El código del tipo de " +
        "componente es obligatorio."
      )
    }

    if (!componentTypeForm.name.trim()) {
      return (
        "El nombre del tipo de " +
        "componente es obligatorio."
      )
    }

    if (!componentTypeForm.category) {
      return (
        "Selecciona una categoría."
      )
    }

    if (
      componentTypeForm.category ===
        "toner" &&
      !componentTypeForm.requires_color
    ) {
      return (
        "El tipo tóner debe " +
        "requerir color."
      )
    }
  }

  if (
    activeTab.value ===
    "components"
  ) {
    if (!componentForm.component_type) {
      return (
        "Selecciona un tipo de componente."
      )
    }

    if (!componentForm.code.trim()) {
      return (
        "El código del componente " +
        "es obligatorio."
      )
    }

    if (!componentForm.name.trim()) {
      return (
        "El nombre del componente " +
        "es obligatorio."
      )
    }
  }

  if (
    activeTab.value ===
    "compatibilities"
  ) {
    if (!compatibilityForm.component) {
      return (
        "Selecciona una unidad o componente."
      )
    }

    if (
      !compatibilityForm.equipment_model
    ) {
      return (
        "Selecciona un modelo de equipo."
      )
    }
  }

  return ""
}


function normalizeNullableNumber(value) {
  if (
    value === "" ||
    value === null ||
    value === undefined
  ) {
    return null
  }

  return Number(value)
}


async function saveCurrent() {
  clearMessages()

  const validationError =
    validateCurrentForm()

  if (validationError) {
    errorMessage.value =
      validationError

    return
  }

  saving.value = true

  try {
    if (activeTab.value === "types") {
      const payload = {
        ...typeForm,
        code:
          typeForm.code
            .trim()
            .toUpperCase(),
        name:
          typeForm.name.trim(),
        description:
          typeForm.description.trim(),
        display_order:
          Number(
            typeForm.display_order || 0
          ),
      }

      if (editingId.value) {
        await updateEquipmentType(
          editingId.value,
          payload
        )
      } else {
        await createEquipmentType(
          payload
        )
      }
    }

    if (activeTab.value === "brands") {
      const payload = {
        ...brandForm,
        code:
          brandForm.code
            .trim()
            .toUpperCase(),
        name:
          brandForm.name.trim(),
        legal_name:
          brandForm.legal_name.trim(),
        country_code:
          brandForm.country_code
            .trim()
            .toUpperCase(),
        country_name:
          brandForm.country_name.trim(),
        website:
          brandForm.website.trim(),
        description:
          brandForm.description.trim(),
        display_order:
          Number(
            brandForm.display_order || 0
          ),
      }

      if (editingId.value) {
        await updateEquipmentBrand(
          editingId.value,
          payload
        )
      } else {
        await createEquipmentBrand(
          payload
        )
      }
    }

    if (activeTab.value === "models") {
      const payload = {
        ...modelForm,
        code:
          modelForm.code
            .trim()
            .toUpperCase(),
        name:
          modelForm.name.trim(),
        commercial_name:
          modelForm.commercial_name.trim(),
        family:
          modelForm.family.trim(),
        manufacturer_reference:
          modelForm.manufacturer_reference
            .trim(),
        technical_notes:
          modelForm.technical_notes.trim(),
        description:
          modelForm.description.trim(),
        display_order:
          Number(
            modelForm.display_order || 0
          ),
      }

      if (editingId.value) {
        await updateEquipmentModel(
          editingId.value,
          payload
        )
      } else {
        await createEquipmentModel(
          payload
        )
      }
    }

    if (
      activeTab.value ===
      "componentTypes"
    ) {
      const payload = {
        ...componentTypeForm,
        code:
          componentTypeForm.code
            .trim()
            .toUpperCase(),
        name:
          componentTypeForm.name.trim(),
        description:
          componentTypeForm.description
            .trim(),
        display_order:
          Number(
            componentTypeForm
              .display_order || 0
          ),
      }

      if (editingId.value) {
        await updateComponentType(
          editingId.value,
          payload
        )
      } else {
        await createComponentType(
          payload
        )
      }
    }

    if (
      activeTab.value ===
      "components"
    ) {
      const payload = {
        ...componentForm,
        parent_component:
          componentForm.parent_component ||
          null,
        code:
          componentForm.code
            .trim()
            .toUpperCase(),
        name:
          componentForm.name.trim(),
        manufacturer_code:
          componentForm.manufacturer_code
            .trim(),
        alternative_code:
          componentForm.alternative_code
            .trim(),
        expected_life_meter:
          normalizeNullableNumber(
            componentForm
              .expected_life_meter
          ),
        expected_life_days:
          normalizeNullableNumber(
            componentForm
              .expected_life_days
          ),
        unit_of_measure:
          componentForm.unit_of_measure
            .trim(),
        description:
          componentForm.description.trim(),
        technical_notes:
          componentForm.technical_notes
            .trim(),
        display_order:
          Number(
            componentForm.display_order ||
            0
          ),
      }

      if (editingId.value) {
        await updateEquipmentComponent(
          editingId.value,
          payload
        )
      } else {
        await createEquipmentComponent(
          payload
        )
      }
    }

    if (
      activeTab.value ===
      "compatibilities"
    ) {
      const payload = {
        ...compatibilityForm,
        equipment_family: null,
        manufacturer_reference:
          compatibilityForm
            .manufacturer_reference
            .trim(),
        adjustment_instructions:
          compatibilityForm
            .adjustment_instructions
            .trim(),
        technical_notes:
          compatibilityForm
            .technical_notes
            .trim(),
        display_order:
          Number(
            compatibilityForm
              .display_order || 0
          ),
      }

      if (editingId.value) {
        await updateComponentCompatibility(
          editingId.value,
          payload
        )
      } else {
        await createComponentCompatibility(
          payload
        )
      }
    }

    successMessage.value =
      editingId.value
        ? "Registro actualizado correctamente."
        : "Registro creado correctamente."

    modalOpen.value = false
    resetForms()

    await loadCatalogs()
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo guardar el registro."
  } finally {
    saving.value = false
  }
}


async function archiveItem(item) {
  const reason = window.prompt(
    `Indica el motivo para archivar ${getRecordName(item)}:`
  )

  if (reason === null) {
    return
  }

  processingId.value = item.id
  clearMessages()

  try {
    if (activeTab.value === "types") {
      await archiveEquipmentType(
        item.id,
        reason.trim()
      )
    }

    if (activeTab.value === "brands") {
      await archiveEquipmentBrand(
        item.id,
        reason.trim()
      )
    }

    if (activeTab.value === "models") {
      await archiveEquipmentModel(
        item.id,
        reason.trim()
      )
    }

    if (
      activeTab.value ===
      "componentTypes"
    ) {
      await archiveComponentType(
        item.id,
        reason.trim()
      )
    }

    if (
      activeTab.value ===
      "components"
    ) {
      await archiveEquipmentComponent(
        item.id,
        reason.trim()
      )
    }

    if (
      activeTab.value ===
      "compatibilities"
    ) {
      await archiveComponentCompatibility(
        item.id,
        reason.trim()
      )
    }

    successMessage.value =
      "Registro archivado correctamente."

    await loadCatalogs()
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo archivar el registro."
  } finally {
    processingId.value = ""
  }
}


async function restoreItem(item) {
  processingId.value = item.id
  clearMessages()

  try {
    if (activeTab.value === "types") {
      await restoreEquipmentType(
        item.id
      )
    }

    if (activeTab.value === "brands") {
      await restoreEquipmentBrand(
        item.id
      )
    }

    if (activeTab.value === "models") {
      await restoreEquipmentModel(
        item.id
      )
    }

    if (
      activeTab.value ===
      "componentTypes"
    ) {
      await restoreComponentType(
        item.id
      )
    }

    if (
      activeTab.value ===
      "components"
    ) {
      await restoreEquipmentComponent(
        item.id
      )
    }

    if (
      activeTab.value ===
      "compatibilities"
    ) {
      await restoreComponentCompatibility(
        item.id
      )
    }

    successMessage.value =
      "Registro restaurado correctamente."

    await loadCatalogs()
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo restaurar el registro."
  } finally {
    processingId.value = ""
  }
}


watch(
  () => modelForm.color_mode,
  (colorMode) => {
    if (colorMode === "monochrome") {
      modelForm.has_color_meter = false
    }

    if (colorMode === "color") {
      modelForm.has_color_meter = true
    }
  }
)


watch(
  () => modelForm.supports_scanning,
  (supportsScanning) => {
    if (!supportsScanning) {
      modelForm.has_scan_meter = false
    }
  }
)


watch(
  () => componentTypeForm.category,
  (category) => {
    if (category === "toner") {
      componentTypeForm.requires_color =
        true
    }
  }
)


watch(
  () =>
    compatibilityForm
      .requires_adjustment,
  (requiresAdjustment) => {
    if (!requiresAdjustment) {
      compatibilityForm
        .adjustment_instructions = ""
    }
  }
)


watch(
  activeTab,
  () => {
    search.value = ""
    resetForms()
  }
)


onMounted(() => {
  loadCatalogs()
})
</script>

<template>
  <section class="catalogs-page">
    <header class="page-header">
      <div>
        <span class="page-kicker">
          Configuración de inventario
        </span>

        <h2>Catálogos de equipos</h2>

        <p>
          Administra equipos, modelos, unidades
          técnicas y sus compatibilidades.
        </p>
      </div>

      <button
        class="primary-button"
        type="button"
        @click="openCreateModal"
      >
        ＋ Nuevo registro
      </button>
    </header>

    <nav class="catalog-tabs">
      <button
        v-for="tab in tabDefinitions"
        :key="tab.id"
        type="button"
        :class="{
          active: activeTab === tab.id,
        }"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}

        <span>
          {{ getTabCount(tab.id) }}
        </span>
      </button>
    </nav>

    <section class="catalog-panel">
      <div class="toolbar">
        <div class="active-catalog">
          <span>Catálogo actual</span>
          <strong>{{ activeTabLabel }}</strong>
        </div>

        <label class="search-field">
          <span>⌕</span>

          <input
            v-model="search"
            type="search"
            placeholder="Buscar por código o nombre"
            @keyup.enter="loadCatalogs"
          />
        </label>

        <label class="archive-filter">
          <input
            v-model="includeArchived"
            type="checkbox"
            @change="loadCatalogs"
          />

          Mostrar archivados
        </label>

        <button
          class="secondary-button"
          type="button"
          :disabled="loading"
          @click="loadCatalogs"
        >
          Actualizar
        </button>
      </div>

      <div
        v-if="successMessage"
        class="message success-message"
      >
        {{ successMessage }}
      </div>

      <div
        v-if="errorMessage"
        class="message error-message"
      >
        {{ errorMessage }}
      </div>

      <div
        v-if="loading"
        class="loading-state"
      >
        Cargando catálogos...
      </div>

      <div
        v-else-if="!currentItems.length"
        class="empty-state"
      >
        <strong>No existen registros</strong>

        <span>
          Crea el primer registro para este
          catálogo.
        </span>
      </div>

      <div
        v-else
        class="table-container"
      >
        <table>
          <thead>
            <tr v-if="activeTab === 'types'">
              <th>Código</th>
              <th>Tipo</th>
              <th>Color</th>
              <th>Contadores</th>
              <th>Accesorios</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>

            <tr
              v-else-if="
                activeTab === 'brands'
              "
            >
              <th>Código</th>
              <th>Marca</th>
              <th>País</th>
              <th>Modelos</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>

            <tr
              v-else-if="
                activeTab === 'models'
              "
            >
              <th>Código</th>
              <th>Marca y modelo</th>
              <th>Tipo</th>
              <th>Color</th>
              <th>Tecnología</th>
              <th>Equipos</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>

            <tr
              v-else-if="
                activeTab ===
                'componentTypes'
              "
            >
              <th>Código</th>
              <th>Tipo de componente</th>
              <th>Categoría</th>
              <th>Color</th>
              <th>Serie</th>
              <th>Stock</th>
              <th>Componentes</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>

            <tr
              v-else-if="
                activeTab === 'components'
              "
            >
              <th>Código</th>
              <th>Unidad o componente</th>
              <th>Tipo</th>
              <th>Color</th>
              <th>Control</th>
              <th>Compatibilidades</th>
              <th>Inventario</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>

            <tr v-else>
              <th>Componente</th>
              <th>Modelo compatible</th>
              <th>Marca</th>
              <th>Tipo</th>
              <th>Posición</th>
              <th>Preferida</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody
            v-if="activeTab === 'types'"
          >
            <tr
              v-for="item in equipmentTypes"
              :key="item.id"
              :class="{
                archived: item.is_archived,
              }"
            >
              <td>
                <span class="code-badge">
                  {{ item.code }}
                </span>
              </td>

              <td>
                <strong>{{ item.name }}</strong>

                <small>
                  {{
                    item.description ||
                    "Sin descripción"
                  }}
                </small>
              </td>

              <td>
                {{
                  item.requires_color_definition
                    ? "Sí"
                    : "No"
                }}
              </td>

              <td>
                {{
                  item.requires_meter
                    ? "Sí"
                    : "No"
                }}
              </td>

              <td>
                {{
                  item.allows_accessories
                    ? "Sí"
                    : "No"
                }}
              </td>

              <td>
                <span
                  class="status-badge"
                  :class="getStatusClass(item)"
                >
                  {{ getStatusLabel(item) }}
                </span>
              </td>

              <td>
                <div class="row-actions">
                  <button
                    type="button"
                    title="Editar"
                    :disabled="item.is_archived"
                    @click="openEditModal(item)"
                  >
                    ✎
                  </button>

                  <button
                    v-if="!item.is_archived"
                    type="button"
                    title="Archivar"
                    :disabled="
                      processingId === item.id
                    "
                    @click="archiveItem(item)"
                  >
                    ⌫
                  </button>

                  <button
                    v-else
                    type="button"
                    title="Restaurar"
                    :disabled="
                      processingId === item.id
                    "
                    @click="restoreItem(item)"
                  >
                    ↻
                  </button>
                </div>
              </td>
            </tr>
          </tbody>

          <tbody
            v-else-if="
              activeTab === 'brands'
            "
          >
            <tr
              v-for="item in brands"
              :key="item.id"
              :class="{
                archived: item.is_archived,
              }"
            >
              <td>
                <span class="code-badge">
                  {{ item.code }}
                </span>
              </td>

              <td>
                <strong>{{ item.name }}</strong>

                <small>
                  {{
                    item.legal_name ||
                    "Sin razón social"
                  }}
                </small>
              </td>

              <td>
                {{
                  [
                    item.country_code,
                    item.country_name,
                  ]
                    .filter(Boolean)
                    .join(" · ") ||
                  "Sin país"
                }}
              </td>

              <td>
                {{ item.models_count || 0 }}
              </td>

              <td>
                <span
                  class="status-badge"
                  :class="getStatusClass(item)"
                >
                  {{ getStatusLabel(item) }}
                </span>
              </td>

              <td>
                <div class="row-actions">
                  <button
                    type="button"
                    title="Editar"
                    :disabled="item.is_archived"
                    @click="openEditModal(item)"
                  >
                    ✎
                  </button>

                  <button
                    v-if="!item.is_archived"
                    type="button"
                    title="Archivar"
                    :disabled="
                      processingId === item.id
                    "
                    @click="archiveItem(item)"
                  >
                    ⌫
                  </button>

                  <button
                    v-else
                    type="button"
                    title="Restaurar"
                    :disabled="
                      processingId === item.id
                    "
                    @click="restoreItem(item)"
                  >
                    ↻
                  </button>
                </div>
              </td>
            </tr>
          </tbody>

          <tbody
            v-else-if="
              activeTab === 'models'
            "
          >
            <tr
              v-for="item in equipmentModels"
              :key="item.id"
              :class="{
                archived: item.is_archived,
              }"
            >
              <td>
                <span class="code-badge">
                  {{ item.code }}
                </span>
              </td>

              <td>
                <strong>
                  {{ item.brand_name }}
                  {{ item.name }}
                </strong>

                <small>
                  {{
                    item.family ||
                    item.commercial_name ||
                    "Sin familia"
                  }}
                </small>
              </td>

              <td>
                {{ item.equipment_type_name }}
              </td>

              <td>
                {{ item.color_mode_name }}
              </td>

              <td>
                {{ item.technology_name }}
              </td>

              <td>
                {{ item.equipment_count || 0 }}
              </td>

              <td>
                <span
                  class="status-badge"
                  :class="getStatusClass(item)"
                >
                  {{ getStatusLabel(item) }}
                </span>
              </td>

              <td>
                <div class="row-actions">
                  <button
                    type="button"
                    title="Editar"
                    :disabled="item.is_archived"
                    @click="openEditModal(item)"
                  >
                    ✎
                  </button>

                  <button
                    v-if="!item.is_archived"
                    type="button"
                    title="Archivar"
                    :disabled="
                      processingId === item.id
                    "
                    @click="archiveItem(item)"
                  >
                    ⌫
                  </button>

                  <button
                    v-else
                    type="button"
                    title="Restaurar"
                    :disabled="
                      processingId === item.id
                    "
                    @click="restoreItem(item)"
                  >
                    ↻
                  </button>
                </div>
              </td>
            </tr>
          </tbody>

          <tbody
            v-else-if="
              activeTab ===
              'componentTypes'
            "
          >
            <tr
              v-for="item in componentTypes"
              :key="item.id"
              :class="{
                archived: item.is_archived,
              }"
            >
              <td>
                <span class="code-badge">
                  {{ item.code }}
                </span>
              </td>

              <td>
                <strong>{{ item.name }}</strong>

                <small>
                  {{
                    item.description ||
                    "Sin descripción"
                  }}
                </small>
              </td>

              <td>
                {{
                  item.category_name ||
                  item.category
                }}
              </td>

              <td>
                {{
                  item.requires_color
                    ? "Sí"
                    : "No"
                }}
              </td>

              <td>
                {{
                  item.requires_serial_number
                    ? "Sí"
                    : "No"
                }}
              </td>

              <td>
                {{
                  item.controls_stock
                    ? "Sí"
                    : "No"
                }}
              </td>

              <td>
                {{ item.component_count || 0 }}
              </td>

              <td>
                <span
                  class="status-badge"
                  :class="getStatusClass(item)"
                >
                  {{ getStatusLabel(item) }}
                </span>
              </td>

              <td>
                <div class="row-actions">
                  <button
                    type="button"
                    title="Editar"
                    :disabled="item.is_archived"
                    @click="openEditModal(item)"
                  >
                    ✎
                  </button>

                  <button
                    v-if="!item.is_archived"
                    type="button"
                    title="Archivar"
                    :disabled="
                      processingId === item.id
                    "
                    @click="archiveItem(item)"
                  >
                    ⌫
                  </button>

                  <button
                    v-else
                    type="button"
                    title="Restaurar"
                    :disabled="
                      processingId === item.id
                    "
                    @click="restoreItem(item)"
                  >
                    ↻
                  </button>
                </div>
              </td>
            </tr>
          </tbody>

          <tbody
            v-else-if="
              activeTab === 'components'
            "
          >
            <tr
              v-for="item in components"
              :key="item.id"
              :class="{
                archived: item.is_archived,
              }"
            >
              <td>
                <span class="code-badge">
                  {{ item.code }}
                </span>
              </td>

              <td>
                <strong>{{ item.name }}</strong>

                <small>
                  {{
                    item.manufacturer_code ||
                    item.alternative_code ||
                    "Sin referencia"
                  }}
                </small>
              </td>

              <td>
                {{
                  item.component_type_name
                }}
              </td>

              <td>
                {{
                  item.color_name ||
                  item.color
                }}
              </td>

              <td>
                {{
                  item.condition_control_name ||
                  item.condition_control
                }}
              </td>

              <td>
                {{
                  item.compatibility_count ||
                  0
                }}
              </td>

              <td>
                {{ item.inventory_count || 0 }}
              </td>

              <td>
                <span
                  class="status-badge"
                  :class="getStatusClass(item)"
                >
                  {{ getStatusLabel(item) }}
                </span>
              </td>

              <td>
                <div class="row-actions">
                  <button
                    type="button"
                    title="Editar"
                    :disabled="item.is_archived"
                    @click="openEditModal(item)"
                  >
                    ✎
                  </button>

                  <button
                    v-if="!item.is_archived"
                    type="button"
                    title="Archivar"
                    :disabled="
                      processingId === item.id
                    "
                    @click="archiveItem(item)"
                  >
                    ⌫
                  </button>

                  <button
                    v-else
                    type="button"
                    title="Restaurar"
                    :disabled="
                      processingId === item.id
                    "
                    @click="restoreItem(item)"
                  >
                    ↻
                  </button>
                </div>
              </td>
            </tr>
          </tbody>

          <tbody v-else>
            <tr
              v-for="item in compatibilities"
              :key="item.id"
              :class="{
                archived: item.is_archived,
              }"
            >
              <td>
                <strong>
                  {{ item.component_name }}
                </strong>

                <small>
                  {{ item.component_code }}
                  ·
                  {{
                    item.component_color_name ||
                    item.component_color
                  }}
                </small>
              </td>

              <td>
                <strong>
                  {{
                    item.target_name ||
                    item.equipment_model_name
                  }}
                </strong>

                <small>
                  {{
                    item.manufacturer_reference ||
                    "Sin referencia específica"
                  }}
                </small>
              </td>

              <td>
                {{ item.brand_name }}
              </td>

              <td>
                {{
                  item.compatibility_type_name ||
                  item.compatibility_type
                }}
              </td>

              <td>
                {{
                  item.position_name ||
                  item.position
                }}
              </td>

              <td>
                {{
                  item.is_preferred
                    ? "Sí"
                    : "No"
                }}
              </td>

              <td>
                <span
                  class="status-badge"
                  :class="getStatusClass(item)"
                >
                  {{ getStatusLabel(item) }}
                </span>
              </td>

              <td>
                <div class="row-actions">
                  <button
                    type="button"
                    title="Editar"
                    :disabled="item.is_archived"
                    @click="openEditModal(item)"
                  >
                    ✎
                  </button>

                  <button
                    v-if="!item.is_archived"
                    type="button"
                    title="Archivar"
                    :disabled="
                      processingId === item.id
                    "
                    @click="archiveItem(item)"
                  >
                    ⌫
                  </button>

                  <button
                    v-else
                    type="button"
                    title="Restaurar"
                    :disabled="
                      processingId === item.id
                    "
                    @click="restoreItem(item)"
                  >
                    ↻
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <Teleport to="body">
      <div
        v-if="modalOpen"
        class="modal-backdrop"
        @click.self="closeModal"
      >
        <section class="catalog-modal">
          <header>
            <div>
              <span>
                {{ activeTabLabel }}
              </span>

              <h3>{{ modalTitle }}</h3>
            </div>

            <button
              type="button"
              :disabled="saving"
              @click="closeModal"
            >
              ×
            </button>
          </header>

          <form @submit.prevent="saveCurrent">
            <div
              v-if="activeTab === 'types'"
              class="form-grid"
            >
              <label>
                <span>Código</span>
                <input
                  v-model="typeForm.code"
                  type="text"
                  required
                />
              </label>

              <label>
                <span>Nombre</span>
                <input
                  v-model="typeForm.name"
                  type="text"
                  required
                />
              </label>

              <label class="full-width">
                <span>Descripción</span>
                <textarea
                  v-model="typeForm.description"
                  rows="3"
                ></textarea>
              </label>

              <label class="check">
                <input
                  v-model="
                    typeForm
                      .requires_color_definition
                  "
                  type="checkbox"
                />
                <span>
                  Requiere definir color
                </span>
              </label>

              <label class="check">
                <input
                  v-model="
                    typeForm.requires_meter
                  "
                  type="checkbox"
                />
                <span>
                  Requiere contadores
                </span>
              </label>

              <label class="check">
                <input
                  v-model="
                    typeForm.allows_accessories
                  "
                  type="checkbox"
                />
                <span>
                  Permite accesorios
                </span>
              </label>

              <label class="check">
                <input
                  v-model="typeForm.is_active"
                  type="checkbox"
                />
                <span>Activo</span>
              </label>

              <label>
                <span>Orden</span>
                <input
                  v-model.number="
                    typeForm.display_order
                  "
                  type="number"
                  min="0"
                />
              </label>
            </div>

            <div
              v-if="activeTab === 'brands'"
              class="form-grid"
            >
              <label>
                <span>Código</span>
                <input
                  v-model="brandForm.code"
                  type="text"
                  required
                />
              </label>

              <label>
                <span>Marca</span>
                <input
                  v-model="brandForm.name"
                  type="text"
                  required
                />
              </label>

              <label class="full-width">
                <span>Razón social</span>
                <input
                  v-model="
                    brandForm.legal_name
                  "
                  type="text"
                />
              </label>

              <label>
                <span>Código país</span>
                <input
                  v-model="
                    brandForm.country_code
                  "
                  type="text"
                  maxlength="2"
                />
              </label>

              <label>
                <span>País</span>
                <input
                  v-model="
                    brandForm.country_name
                  "
                  type="text"
                />
              </label>

              <label class="full-width">
                <span>Sitio web</span>
                <input
                  v-model="brandForm.website"
                  type="url"
                />
              </label>

              <label class="full-width">
                <span>Descripción</span>
                <textarea
                  v-model="
                    brandForm.description
                  "
                  rows="3"
                ></textarea>
              </label>

              <label class="check">
                <input
                  v-model="
                    brandForm.is_active
                  "
                  type="checkbox"
                />
                <span>Activa</span>
              </label>

              <label>
                <span>Orden</span>
                <input
                  v-model.number="
                    brandForm.display_order
                  "
                  type="number"
                  min="0"
                />
              </label>
            </div>

            <div
              v-if="activeTab === 'models'"
              class="form-grid"
            >
              <label>
                <span>Código</span>
                <input
                  v-model="modelForm.code"
                  type="text"
                  required
                />
              </label>

              <label>
                <span>Modelo</span>
                <input
                  v-model="modelForm.name"
                  type="text"
                  required
                />
              </label>

              <label>
                <span>Marca</span>
                <select
                  v-model="modelForm.brand"
                  required
                >
                  <option value="">
                    Selecciona una marca
                  </option>

                  <option
                    v-for="item in brands.filter(
                      (brand) =>
                        !brand.is_archived &&
                        brand.is_active
                    )"
                    :key="item.id"
                    :value="item.id"
                  >
                    {{ item.name }}
                  </option>
                </select>
              </label>

              <label>
                <span>Tipo</span>
                <select
                  v-model="
                    modelForm.equipment_type
                  "
                  required
                >
                  <option value="">
                    Selecciona un tipo
                  </option>

                  <option
                    v-for="item in equipmentTypes.filter(
                      (type) =>
                        !type.is_archived &&
                        type.is_active
                    )"
                    :key="item.id"
                    :value="item.id"
                  >
                    {{ item.name }}
                  </option>
                </select>
              </label>

              <label>
                <span>
                  Nombre comercial
                </span>
                <input
                  v-model="
                    modelForm.commercial_name
                  "
                  type="text"
                />
              </label>

              <label>
                <span>Familia</span>
                <input
                  v-model="modelForm.family"
                  type="text"
                />
              </label>

              <label>
                <span>
                  Referencia fabricante
                </span>
                <input
                  v-model="
                    modelForm
                      .manufacturer_reference
                  "
                  type="text"
                />
              </label>

              <label>
                <span>Color</span>
                <select
                  v-model="
                    modelForm.color_mode
                  "
                >
                  <option value="monochrome">
                    Blanco y negro
                  </option>
                  <option value="color">
                    Color
                  </option>
                  <option value="mixed">
                    Mixto
                  </option>
                  <option value="not_applicable">
                    No aplica
                  </option>
                </select>
              </label>

              <label>
                <span>Tecnología</span>
                <select
                  v-model="
                    modelForm.technology
                  "
                >
                  <option value="laser">
                    Láser
                  </option>
                  <option value="inkjet">
                    Inyección de tinta
                  </option>
                  <option value="digital_duplication">
                    Duplicación digital
                  </option>
                  <option value="thermal">
                    Térmica
                  </option>
                  <option value="led">
                    LED
                  </option>
                  <option value="other">
                    Otra
                  </option>
                  <option value="not_defined">
                    No definida
                  </option>
                </select>
              </label>

              <label>
                <span>Papel máximo</span>
                <select
                  v-model="
                    modelForm
                      .maximum_paper_size
                  "
                >
                  <option value="a4">A4</option>
                  <option value="a3">A3</option>
                  <option value="sra3">
                    SRA3
                  </option>
                  <option value="a2">A2</option>
                  <option value="a1">A1</option>
                  <option value="a0">A0</option>
                  <option value="large_format">
                    Gran formato
                  </option>
                  <option value="continuous">
                    Papel continuo
                  </option>
                  <option value="other">
                    Otro
                  </option>
                  <option value="not_defined">
                    No definido
                  </option>
                </select>
              </label>

              <div
                class="checks full-width"
              >
                <label class="check">
                  <input
                    v-model="
                      modelForm
                        .is_multifunction
                    "
                    type="checkbox"
                  />
                  <span>Multifuncional</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      modelForm
                        .supports_printing
                    "
                    type="checkbox"
                  />
                  <span>Impresión</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      modelForm
                        .supports_copying
                    "
                    type="checkbox"
                  />
                  <span>Copia</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      modelForm
                        .supports_scanning
                    "
                    type="checkbox"
                  />
                  <span>Escaneo</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      modelForm.supports_fax
                    "
                    type="checkbox"
                  />
                  <span>Fax</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      modelForm
                        .supports_network
                    "
                    type="checkbox"
                  />
                  <span>Red</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      modelForm
                        .supports_duplex
                    "
                    type="checkbox"
                  />
                  <span>Dúplex</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      modelForm
                        .supports_accessories
                    "
                    type="checkbox"
                  />
                  <span>Accesorios</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      modelForm
                        .supports_technical_units
                    "
                    type="checkbox"
                  />
                  <span>
                    Unidades técnicas
                  </span>
                </label>
              </div>

              <div
                class="checks full-width"
              >
                <label class="check">
                  <input
                    v-model="
                      modelForm.has_total_meter
                    "
                    type="checkbox"
                  />
                  <span>Contador total</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      modelForm.has_black_meter
                    "
                    type="checkbox"
                  />
                  <span>Contador B/N</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      modelForm.has_color_meter
                    "
                    type="checkbox"
                  />
                  <span>Contador color</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      modelForm.has_scan_meter
                    "
                    type="checkbox"
                  />
                  <span>
                    Contador escaneo
                  </span>
                </label>
              </div>

              <label class="full-width">
                <span>Notas técnicas</span>
                <textarea
                  v-model="
                    modelForm.technical_notes
                  "
                  rows="3"
                ></textarea>
              </label>

              <label class="full-width">
                <span>Descripción</span>
                <textarea
                  v-model="
                    modelForm.description
                  "
                  rows="3"
                ></textarea>
              </label>

              <label class="check">
                <input
                  v-model="
                    modelForm.is_active
                  "
                  type="checkbox"
                />
                <span>Activo</span>
              </label>

              <label>
                <span>Orden</span>
                <input
                  v-model.number="
                    modelForm.display_order
                  "
                  type="number"
                  min="0"
                />
              </label>
            </div>

            <div
              v-if="
                activeTab ===
                'componentTypes'
              "
              class="form-grid"
            >
              <label>
                <span>Código</span>
                <input
                  v-model="
                    componentTypeForm.code
                  "
                  type="text"
                  required
                />
              </label>

              <label>
                <span>Nombre</span>
                <input
                  v-model="
                    componentTypeForm.name
                  "
                  type="text"
                  required
                />
              </label>

              <label>
                <span>Categoría</span>
                <select
                  v-model="
                    componentTypeForm
                      .category
                  "
                  required
                >
                  <option value="technical_unit">
                    Unidad técnica
                  </option>
                  <option value="subpart">
                    Subparte
                  </option>
                  <option value="accessory">
                    Accesorio
                  </option>
                  <option value="toner">
                    Tóner
                  </option>
                  <option value="spare_part">
                    Repuesto
                  </option>
                </select>
              </label>

              <label>
                <span>Orden</span>
                <input
                  v-model.number="
                    componentTypeForm
                      .display_order
                  "
                  type="number"
                  min="0"
                />
              </label>

              <label class="full-width">
                <span>Descripción</span>
                <textarea
                  v-model="
                    componentTypeForm
                      .description
                  "
                  rows="3"
                ></textarea>
              </label>

              <div
                class="checks full-width"
              >
                <label class="check">
                  <input
                    v-model="
                      componentTypeForm
                        .requires_color
                    "
                    type="checkbox"
                  />
                  <span>Requiere color</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      componentTypeForm
                        .requires_serial_number
                    "
                    type="checkbox"
                  />
                  <span>
                    Requiere serie
                  </span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      componentTypeForm
                        .requires_meter
                    "
                    type="checkbox"
                  />
                  <span>
                    Requiere contador
                  </span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      componentTypeForm
                        .controls_stock
                    "
                    type="checkbox"
                  />
                  <span>Controla stock</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      componentTypeForm
                        .is_active
                    "
                    type="checkbox"
                  />
                  <span>Activo</span>
                </label>
              </div>
            </div>

            <div
              v-if="
                activeTab === 'components'
              "
              class="form-grid"
            >
              <label>
                <span>
                  Tipo de componente
                </span>

                <select
                  v-model="
                    componentForm
                      .component_type
                  "
                  required
                >
                  <option value="">
                    Selecciona un tipo
                  </option>

                  <option
                    v-for="item in activeComponentTypes"
                    :key="item.id"
                    :value="item.id"
                  >
                    {{ item.name }}
                    ·
                    {{ item.category_name }}
                  </option>
                </select>
              </label>

              <label>
                <span>
                  Componente principal
                </span>

                <select
                  v-model="
                    componentForm
                      .parent_component
                  "
                >
                  <option value="">
                    Sin componente principal
                  </option>

                  <option
                    v-for="item in activeComponents.filter(
                      (component) =>
                        component.id !== editingId
                    )"
                    :key="item.id"
                    :value="item.id"
                  >
                    {{ item.code }}
                    ·
                    {{ item.name }}
                  </option>
                </select>
              </label>

              <label>
                <span>Código interno</span>
                <input
                  v-model="
                    componentForm.code
                  "
                  type="text"
                  required
                  placeholder="IMAGE_UNIT_C"
                />
              </label>

              <label>
                <span>Nombre</span>
                <input
                  v-model="
                    componentForm.name
                  "
                  type="text"
                  required
                  placeholder="Unidad de imagen Cian"
                />
              </label>

              <label>
                <span>
                  Código fabricante
                </span>
                <input
                  v-model="
                    componentForm
                      .manufacturer_code
                  "
                  type="text"
                />
              </label>

              <label>
                <span>
                  Código alternativo
                </span>
                <input
                  v-model="
                    componentForm
                      .alternative_code
                  "
                  type="text"
                />
              </label>

              <label>
                <span>Color</span>
                <select
                  v-model="
                    componentForm.color
                  "
                >
                  <option value="black">
                    Negro
                  </option>
                  <option value="cyan">
                    Cyan
                  </option>
                  <option value="magenta">
                    Magenta
                  </option>
                  <option value="yellow">
                    Amarillo
                  </option>
                  <option value="color">
                    Color genérico
                  </option>
                  <option value="monochrome">
                    Blanco y negro
                  </option>
                  <option value="multicolor">
                    Multicolor
                  </option>
                  <option value="not_applicable">
                    No aplica
                  </option>
                </select>
              </label>

              <label>
                <span>
                  Control de vida útil
                </span>
                <select
                  v-model="
                    componentForm
                      .condition_control
                  "
                >
                  <option value="none">
                    Sin control especial
                  </option>
                  <option value="date">
                    Por fecha
                  </option>
                  <option value="meter">
                    Por contador
                  </option>
                  <option value="date_and_meter">
                    Fecha y contador
                  </option>
                </select>
              </label>

              <label>
                <span>
                  Vida útil por contador
                </span>
                <input
                  v-model.number="
                    componentForm
                      .expected_life_meter
                  "
                  type="number"
                  min="0"
                />
              </label>

              <label>
                <span>
                  Vida útil en días
                </span>
                <input
                  v-model.number="
                    componentForm
                      .expected_life_days
                  "
                  type="number"
                  min="0"
                />
              </label>

              <label>
                <span>
                  Unidad de medida
                </span>
                <select
                  v-model="
                    componentForm
                      .unit_of_measure
                  "
                >
                  <option value="unit">
                    Unidad
                  </option>
                  <option value="kit">
                    Kit
                  </option>
                  <option value="bottle">
                    Botella
                  </option>
                  <option value="kilogram">
                    Kilogramo
                  </option>
                  <option value="meter">
                    Metro
                  </option>
                </select>
              </label>

              <label>
                <span>Orden</span>
                <input
                  v-model.number="
                    componentForm
                      .display_order
                  "
                  type="number"
                  min="0"
                />
              </label>

              <div
                class="checks full-width"
              >
                <label class="check">
                  <input
                    v-model="
                      componentForm
                        .requires_individual_serial
                    "
                    type="checkbox"
                  />
                  <span>
                    Requiere serie individual
                  </span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      componentForm
                        .is_consumable
                    "
                    type="checkbox"
                  />
                  <span>Consumible</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      componentForm
                        .is_reusable
                    "
                    type="checkbox"
                  />
                  <span>Reutilizable</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      componentForm
                        .can_be_repaired
                    "
                    type="checkbox"
                  />
                  <span>Puede repararse</span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      componentForm
                        .requires_removed_part_tracking
                    "
                    type="checkbox"
                  />
                  <span>
                    Controlar parte retirada
                  </span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      componentForm
                        .is_active
                    "
                    type="checkbox"
                  />
                  <span>Activo</span>
                </label>
              </div>

              <label class="full-width">
                <span>Descripción</span>
                <textarea
                  v-model="
                    componentForm.description
                  "
                  rows="3"
                ></textarea>
              </label>

              <label class="full-width">
                <span>Notas técnicas</span>
                <textarea
                  v-model="
                    componentForm
                      .technical_notes
                  "
                  rows="3"
                ></textarea>
              </label>
            </div>

            <div
              v-if="
                activeTab ===
                'compatibilities'
              "
              class="form-grid"
            >
              <label class="full-width">
                <span>
                  Unidad o componente
                </span>

                <select
                  v-model="
                    compatibilityForm
                      .component
                  "
                  required
                >
                  <option value="">
                    Selecciona una unidad
                  </option>

                  <option
                    v-for="item in activeComponents"
                    :key="item.id"
                    :value="item.id"
                  >
                    {{ item.code }}
                    ·
                    {{ item.name }}
                    ·
                    {{ item.color_name }}
                  </option>
                </select>
              </label>

              <label class="full-width">
                <span>
                  Modelo de equipo compatible
                </span>

                <select
                  v-model="
                    compatibilityForm
                      .equipment_model
                  "
                  required
                >
                  <option value="">
                    Selecciona un modelo
                  </option>

                  <option
                    v-for="item in activeEquipmentModels"
                    :key="item.id"
                    :value="item.id"
                  >
                    {{ item.brand_name }}
                    {{ item.name }}
                  </option>
                </select>
              </label>

              <label>
                <span>
                  Tipo de compatibilidad
                </span>

                <select
                  v-model="
                    compatibilityForm
                      .compatibility_type
                  "
                >
                  <option value="original">
                    Original
                  </option>
                  <option value="compatible">
                    Compatible
                  </option>
                  <option value="alternative">
                    Alternativa
                  </option>
                  <option value="adapted">
                    Adaptada
                  </option>
                </select>
              </label>

              <label>
                <span>
                  Color o posición
                </span>

                <select
                  v-model="
                    compatibilityForm
                      .position
                  "
                >
                  <option value="black">
                    Negro
                  </option>
                  <option value="cyan">
                    Cyan
                  </option>
                  <option value="magenta">
                    Magenta
                  </option>
                  <option value="yellow">
                    Amarillo
                  </option>
                  <option value="color">
                    Color genérico
                  </option>
                  <option value="monochrome">
                    Blanco y negro
                  </option>
                  <option value="left">
                    Izquierda
                  </option>
                  <option value="right">
                    Derecha
                  </option>
                  <option value="upper">
                    Superior
                  </option>
                  <option value="lower">
                    Inferior
                  </option>
                  <option value="front">
                    Frontal
                  </option>
                  <option value="rear">
                    Posterior
                  </option>
                  <option value="main">
                    Principal
                  </option>
                  <option value="secondary">
                    Secundaria
                  </option>
                  <option value="not_applicable">
                    No aplica
                  </option>
                </select>
              </label>

              <label>
                <span>
                  Referencia fabricante
                </span>

                <input
                  v-model="
                    compatibilityForm
                      .manufacturer_reference
                  "
                  type="text"
                />
              </label>

              <label>
                <span>Orden</span>

                <input
                  v-model.number="
                    compatibilityForm
                      .display_order
                  "
                  type="number"
                  min="0"
                />
              </label>

              <div
                class="checks full-width"
              >
                <label class="check">
                  <input
                    v-model="
                      compatibilityForm
                        .is_preferred
                    "
                    type="checkbox"
                  />
                  <span>
                    Compatibilidad preferida
                  </span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      compatibilityForm
                        .requires_adjustment
                    "
                    type="checkbox"
                  />
                  <span>
                    Requiere adaptación
                  </span>
                </label>

                <label class="check">
                  <input
                    v-model="
                      compatibilityForm
                        .is_active
                    "
                    type="checkbox"
                  />
                  <span>Activa</span>
                </label>
              </div>

              <label
                v-if="
                  compatibilityForm
                    .requires_adjustment
                "
                class="full-width"
              >
                <span>
                  Instrucciones de adaptación
                </span>

                <textarea
                  v-model="
                    compatibilityForm
                      .adjustment_instructions
                  "
                  rows="3"
                ></textarea>
              </label>

              <label class="full-width">
                <span>Notas técnicas</span>

                <textarea
                  v-model="
                    compatibilityForm
                      .technical_notes
                  "
                  rows="3"
                ></textarea>
              </label>
            </div>

            <footer>
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
                {{
                  saving
                    ? "Guardando..."
                    : editingId
                      ? "Guardar cambios"
                      : "Crear registro"
                }}
              </button>
            </footer>
          </form>
        </section>
      </div>
    </Teleport>
  </section>
</template>

<style scoped>
.catalogs-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.page-header,
.toolbar,
.catalog-tabs,
.row-actions,
.catalog-modal > header,
.catalog-modal footer {
  display: flex;
  align-items: center;
}

.page-header {
  justify-content: space-between;
  gap: 16px;
}

.page-header h2 {
  margin: 0;
  color: #1d2f45;
}

.page-header p {
  max-width: 720px;
  margin: 6px 0 0;
  color: #778598;
}

.page-kicker {
  display: block;
  margin-bottom: 5px;
  color: #2d82a8;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.primary-button,
.secondary-button,
.catalog-tabs button,
.row-actions button {
  border-radius: 9px;
  font: inherit;
  cursor: pointer;
  transition:
    transform 160ms ease,
    border-color 160ms ease,
    background 160ms ease,
    box-shadow 160ms ease;
}

.primary-button {
  border: 0;
  padding: 10px 15px;
  background: #277fa6;
  color: white;
  font-weight: 700;
  box-shadow:
    0 7px 18px rgb(39 127 166 / 20%);
}

.primary-button:hover:not(:disabled) {
  transform: translateY(-1px);
  background: #206f94;
}

.secondary-button {
  padding: 9px 13px;
  border: 1px solid #dce4eb;
  background: white;
  color: #506176;
}

.secondary-button:hover:not(:disabled) {
  border-color: #9db7c7;
  background: #f7fafc;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.catalog-tabs {
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 3px;
}

.catalog-tabs button {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 7px;
  border: 1px solid transparent;
  padding: 9px 14px;
  background: #eef3f6;
  color: #5c6b7e;
}

.catalog-tabs button:hover {
  border-color: #cbdbe4;
  transform: translateY(-1px);
}

.catalog-tabs button.active {
  border-color: #277fa6;
  background: #277fa6;
  color: white;
  box-shadow:
    0 7px 16px rgb(39 127 166 / 18%);
}

.catalog-tabs span {
  min-width: 20px;
  padding: 2px 6px;
  border-radius: 999px;
  background: rgb(255 255 255 / 35%);
  font-size: 11px;
  text-align: center;
}

.catalog-panel {
  overflow: hidden;
  border: 1px solid #e2e8ee;
  border-radius: 14px;
  background: white;
  box-shadow:
    0 9px 25px rgb(35 53 71 / 5%);
}

.toolbar {
  gap: 10px;
  flex-wrap: wrap;
  padding: 13px 14px;
  border-bottom: 1px solid #edf1f4;
}

.active-catalog {
  display: flex;
  flex-direction: column;
  min-width: 160px;
}

.active-catalog span {
  color: #8995a4;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
}

.active-catalog strong {
  margin-top: 2px;
  color: #31465c;
  font-size: 13px;
}

.search-field {
  min-width: 250px;
  display: flex;
  flex: 1;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  border: 1px solid #dce4eb;
  border-radius: 9px;
  background: white;
}

.search-field:focus-within {
  border-color: #68a5c0;
  box-shadow:
    0 0 0 3px rgb(39 127 166 / 10%);
}

.search-field input {
  width: 100%;
  min-height: 39px;
  border: 0;
  outline: 0;
  background: transparent;
}

.archive-filter {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #667488;
  font-size: 13px;
}

.message {
  margin: 14px;
  padding: 10px 12px;
  border-radius: 8px;
}

.success-message {
  background: #edf8f1;
  color: #267346;
}

.error-message {
  background: #fff0f0;
  color: #a13f3f;
}

.loading-state,
.empty-state {
  padding: 45px;
  color: #7a8797;
  text-align: center;
}

.empty-state {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.empty-state strong {
  color: #4b5c70;
}

.empty-state span {
  font-size: 13px;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  min-width: 900px;
  border-collapse: collapse;
}

th,
td {
  padding: 11px 13px;
  border-bottom: 1px solid #edf1f4;
  text-align: left;
  vertical-align: middle;
}

th {
  position: sticky;
  z-index: 2;
  top: 0;
  background: #fafbfd;
  color: #7d8998;
  font-size: 10px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

td {
  color: #4d5d70;
  font-size: 12px;
}

tbody tr {
  transition:
    background 150ms ease;
}

tbody tr:hover {
  background: #f9fbfc;
}

td strong,
td small {
  display: block;
}

td strong {
  color: #31445a;
}

td small {
  margin-top: 3px;
  color: #8a95a3;
}

tr.archived {
  opacity: 0.58;
}

.code-badge {
  display: inline-flex;
  padding: 5px 8px;
  border-radius: 7px;
  background: #edf4f8;
  color: #316d89;
  font-size: 10px;
  font-weight: 800;
}

.status-badge {
  display: inline-flex;
  padding: 5px 8px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
}

.active-status {
  background: #eaf6ee;
  color: #2d7b4d;
}

.inactive-status {
  background: #fff5dc;
  color: #926b13;
}

.archived-status {
  background: #eef0f3;
  color: #667180;
}

.row-actions {
  gap: 6px;
}

.row-actions button {
  width: 31px;
  height: 31px;
  border: 1px solid #dce4eb;
  background: white;
  color: #4f6174;
}

.row-actions button:hover:not(:disabled) {
  transform: translateY(-1px);
  border-color: #8fb3c5;
  background: #f4f9fb;
  color: #277fa6;
}

.modal-backdrop {
  position: fixed;
  z-index: 1000;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgb(20 33 49 / 55%);
  backdrop-filter: blur(3px);
}

.catalog-modal {
  width: min(920px, 100%);
  max-height: 92vh;
  overflow: auto;
  border-radius: 14px;
  background: white;
  box-shadow:
    0 24px 70px rgb(0 0 0 / 24%);
  animation:
    modal-enter 180ms ease;
}

@keyframes modal-enter {
  from {
    opacity: 0;
    transform:
      translateY(10px)
      scale(0.985);
  }

  to {
    opacity: 1;
    transform:
      translateY(0)
      scale(1);
  }
}

.catalog-modal > header {
  position: sticky;
  z-index: 4;
  top: 0;
  justify-content: space-between;
  padding: 17px 20px;
  border-bottom: 1px solid #e8edf1;
  background: white;
}

.catalog-modal > header span {
  color: #2b82a8;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.catalog-modal > header h3 {
  margin: 4px 0 0;
  color: #24364b;
}

.catalog-modal > header button {
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 50%;
  background: #eef2f5;
  font-size: 22px;
  cursor: pointer;
}

.catalog-modal form {
  padding: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.form-grid label:not(.check) {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-grid label > span {
  color: #5d6c7e;
  font-size: 12px;
  font-weight: 700;
}

.form-grid input,
.form-grid select,
.form-grid textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #dce4eb;
  border-radius: 9px;
  padding: 10px;
  outline: 0;
  background: white;
  color: #3e5064;
  font: inherit;
}

.form-grid input:focus,
.form-grid select:focus,
.form-grid textarea:focus {
  border-color: #68a5c0;
  box-shadow:
    0 0 0 3px rgb(39 127 166 / 10%);
}

.form-grid textarea {
  resize: vertical;
}

.full-width {
  grid-column: 1 / -1;
}

.check {
  display: inline-flex;
  align-items: center;
  gap: 7px;
}

.check input {
  flex: 0 0 auto;
  width: 16px;
  height: 16px;
}

.checks {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  gap: 10px;
  padding: 12px;
  border: 1px solid #e3e9ee;
  border-radius: 10px;
  background: #fafcfd;
}

.catalog-modal footer {
  position: sticky;
  z-index: 3;
  bottom: -20px;
  justify-content: flex-end;
  gap: 9px;
  margin: 20px -20px -20px;
  padding: 16px 20px;
  border-top: 1px solid #edf1f4;
  background: white;
}

@media (max-width: 800px) {
  .page-header {
    align-items: stretch;
    flex-direction: column;
  }

  .toolbar {
    align-items: stretch;
  }

  .active-catalog,
  .search-field {
    width: 100%;
  }

  .form-grid,
  .checks {
    grid-template-columns: 1fr;
  }

  .full-width {
    grid-column: auto;
  }
}
</style>