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
  createEquipment,
  getEquipmentBrands,
  getEquipmentById,
  getEquipmentModels,
  getEquipmentTypes,
  getImportBatches,
  updateEquipment,
} from "../../services/equipment.service"

import {
  getPartnerBranches,
  getPartners,
} from "../../services/partners.service"

import {
  getUsers,
} from "../../services/users.service"


const route = useRoute()
const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const loadingCatalogs = ref(false)
const loadingBranches = ref(false)
const errorMessage = ref("")

const equipmentTypes = ref([])
const brands = ref([])
const equipmentModels = ref([])
const importBatches = ref([])
const partners = ref([])
const customerBranches = ref([])
const users = ref([])

const mainPhotoFile = ref(null)
const mainPhotoPreview = ref("")


const isEditing = computed(() => {
  return Boolean(route.params.id)
})


const pageTitle = computed(() => {
  return isEditing.value
    ? "Editar equipo"
    : "Nuevo equipo"
})


const selectedModel = computed(() => {
  return equipmentModels.value.find(
    (item) => item.id === form.equipment_model
  ) || null
})


const selectedModelName = computed(() => {
  const model = selectedModel.value

  if (!model) {
    return "Sin modelo seleccionado"
  }

  return [
    model.brand_name,
    model.name,
  ]
    .filter(Boolean)
    .join(" ")
    .trim()
})


const selectedModelIsMonochrome = computed(() => {
  const colorMode =
    selectedModel.value?.color_mode

  return [
    "monochrome",
    "mono",
  ].includes(colorMode)
})


const selectedModelHasScanMeter = computed(() => {
  if (!selectedModel.value) {
    return true
  }

  return Boolean(
    selectedModel.value.has_scan_meter
  )
})


const selectedModelHasColorMeter = computed(() => {
  if (!selectedModel.value) {
    return true
  }

  return Boolean(
    selectedModel.value.has_color_meter
  )
})


const requiresOwnerPartner = computed(() => {
  return [
    "customer",
    "supplier",
    "third_party",
    "other",
  ].includes(
    form.ownership_type
  )
})


const requiresCustomer = computed(() => {
  return [
    "reserved",
    "sold",
    "delivery_preparation",
    "in_transit",
    "delivered",
    "contract_assigned",
    "installed",
    "temporary_loan",
    "demonstration",
    "replacement",
  ].includes(
    form.commercial_status
  )
})


const requiresTechnicalReason = computed(() => {
  return [
    "with_problems",
    "for_parts",
  ].includes(
    form.technical_status
  )
})


const requiresReservationDate = computed(() => {
  return form.commercial_status === "reserved"
})


const requiresSaleDate = computed(() => {
  return [
    "sold",
    "delivery_preparation",
    "in_transit",
    "delivered",
  ].includes(
    form.commercial_status
  )
})


const requiresDeliveryDate = computed(() => {
  return form.commercial_status === "delivered"
})


const customerOptions = computed(() => {
  return partners.value.filter(
    (partner) => (
      partner.is_rental_customer ||
      partner.is_sales_customer ||
      partner.is_service_customer
    )
  )
})


const supplierOptions = computed(() => {
  return partners.value.filter(
    (partner) => partner.is_supplier
  )
})


const ownerOptions = computed(() => {
  return partners.value
})


const filteredModels = computed(() => {
  return equipmentModels.value.filter(
    (model) => {
      const matchesBrand =
        !form.brand_filter ||
        model.brand === form.brand_filter ||
        model.brand_id === form.brand_filter

      const matchesType =
        !form.equipment_type_filter ||
        model.equipment_type ===
          form.equipment_type_filter ||
        model.equipment_type_id ===
          form.equipment_type_filter

      return (
        matchesBrand &&
        matchesType
      )
    }
  )
})


const form = reactive({
  serial_number: "",

  equipment_type_filter: "",
  brand_filter: "",
  equipment_model: "",
  import_batch: "",

  ownership_type: "own",
  physical_condition: "used",

  supplier: "",
  owner_partner: "",
  customer: "",
  customer_branch: "",
  advisor: "",

  import_reference: "",
  purchase_invoice_number: "",
  purchase_invoice_date: "",
  purchase_date: "",
  unloading_date: "",

  purchase_currency: "USD",
  purchase_price: "0.00",
  allocated_import_cost: "0.00",

  sale_currency: "PEN",
  sale_price: "0.00",
  sale_invoice_number: "",
  sale_invoice_date: "",
  reservation_date: "",
  reservation_expiration_date: "",
  sale_date: "",
  delivery_date: "",

  technical_status: "unreviewed",
  commercial_status: "warehouse",

  technical_status_reason: "",
  commercial_status_reason: "",

  warehouse_location: "",
  position_reference: "",

  initial_total_meter: 0,
  initial_black_meter: 0,
  initial_color_meter: 0,
  initial_scan_meter: 0,

  current_total_meter: 0,
  current_black_meter: 0,
  current_color_meter: 0,
  current_scan_meter: 0,

  last_meter_date: "",
  last_meter_source: "manual",

  hostname: "",
  ip_address: "",
  mac_address: "",
  asset_number: "",
  firmware_version: "",

  accessories_description: "",
  unloading_observations: "",
  technical_notes: "",
  commercial_notes: "",
  notes: "",

  is_active: true,
})


function normalizeText(value) {
  return typeof value === "string"
    ? value.trim()
    : value
}


function normalizeNullableId(value) {
  return value || null
}


function normalizeNullableDate(value) {
  return value || null
}


function normalizeDecimal(value) {
  const number = Number(value || 0)

  if (!Number.isFinite(number)) {
    return "0.00"
  }

  return number.toFixed(2)
}


function normalizeInteger(value) {
  const number = Number(value || 0)

  if (
    !Number.isFinite(number) ||
    number < 0
  ) {
    return 0
  }

  return Math.trunc(number)
}


function toLocalDateTimeInput(value) {
  if (!value) {
    return ""
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return ""
  }

  const offset =
    date.getTimezoneOffset() * 60000

  return new Date(
    date.getTime() - offset
  )
    .toISOString()
    .slice(0, 16)
}


function getPartnerName(partner) {
  return (
    partner.display_name ||
    partner.trade_name ||
    partner.legal_name ||
    [
      partner.first_names,
      partner.paternal_last_name,
      partner.maternal_last_name,
    ]
      .filter(Boolean)
      .join(" ")
      .trim() ||
    partner.document_number ||
    "Registro sin nombre"
  )
}


function getUserName(user) {
  return (
    user.full_name ||
    [
      user.first_name,
      user.paternal_last_name,
      user.maternal_last_name,
    ]
      .filter(Boolean)
      .join(" ")
      .trim() ||
    user.email ||
    "Usuario"
  )
}


function getModelName(model) {
  return [
    model.brand_name,
    model.name,
  ]
    .filter(Boolean)
    .join(" ")
    .trim() ||
    model.commercial_name ||
    "Modelo sin nombre"
}


function getImportBatchName(batch) {
  return (
    batch.display_name ||
    batch.code ||
    batch.reference ||
    batch.import_reference ||
    batch.container_number ||
    "Lote sin referencia"
  )
}


function buildPayload() {
  return {
    serial_number:
      normalizeText(
        form.serial_number
      ).toUpperCase(),

    equipment_model:
      normalizeNullableId(
        form.equipment_model
      ),

    import_batch:
      normalizeNullableId(
        form.import_batch
      ),

    ownership_type:
      form.ownership_type,

    physical_condition:
      form.physical_condition,

    supplier:
      normalizeNullableId(
        form.supplier
      ),

    owner_partner:
      normalizeNullableId(
        form.owner_partner
      ),

    customer:
      normalizeNullableId(
        form.customer
      ),

    customer_branch:
      normalizeNullableId(
        form.customer_branch
      ),

    advisor:
      normalizeNullableId(
        form.advisor
      ),

    import_reference:
      normalizeText(
        form.import_reference
      ),

    purchase_invoice_number:
      normalizeText(
        form.purchase_invoice_number
      ).toUpperCase(),

    purchase_invoice_date:
      normalizeNullableDate(
        form.purchase_invoice_date
      ),

    purchase_date:
      normalizeNullableDate(
        form.purchase_date
      ),

    unloading_date:
      normalizeNullableDate(
        form.unloading_date
      ),

    purchase_currency:
      form.purchase_currency,

    purchase_price:
      normalizeDecimal(
        form.purchase_price
      ),

    allocated_import_cost:
      normalizeDecimal(
        form.allocated_import_cost
      ),

    sale_currency:
      form.sale_currency,

    sale_price:
      normalizeDecimal(
        form.sale_price
      ),

    sale_invoice_number:
      normalizeText(
        form.sale_invoice_number
      ).toUpperCase(),

    sale_invoice_date:
      normalizeNullableDate(
        form.sale_invoice_date
      ),

    reservation_date:
      normalizeNullableDate(
        form.reservation_date
      ),

    reservation_expiration_date:
      normalizeNullableDate(
        form.reservation_expiration_date
      ),

    sale_date:
      normalizeNullableDate(
        form.sale_date
      ),

    delivery_date:
      normalizeNullableDate(
        form.delivery_date
      ),

    technical_status:
      form.technical_status,

    commercial_status:
      form.commercial_status,

    technical_status_reason:
      normalizeText(
        form.technical_status_reason
      ),

    commercial_status_reason:
      normalizeText(
        form.commercial_status_reason
      ),

    warehouse_location:
      normalizeText(
        form.warehouse_location
      ),

    position_reference:
      normalizeText(
        form.position_reference
      ),

    initial_total_meter:
      normalizeInteger(
        form.initial_total_meter
      ),

    initial_black_meter:
      normalizeInteger(
        form.initial_black_meter
      ),

    initial_color_meter:
      normalizeInteger(
        form.initial_color_meter
      ),

    initial_scan_meter:
      normalizeInteger(
        form.initial_scan_meter
      ),

    current_total_meter:
      normalizeInteger(
        form.current_total_meter
      ),

    current_black_meter:
      normalizeInteger(
        form.current_black_meter
      ),

    current_color_meter:
      normalizeInteger(
        form.current_color_meter
      ),

    current_scan_meter:
      normalizeInteger(
        form.current_scan_meter
      ),

    last_meter_date:
      normalizeNullableDate(
        form.last_meter_date
      ),

    last_meter_source:
      form.last_meter_source,

    hostname:
      normalizeText(
        form.hostname
      ),

    ip_address:
      normalizeText(
        form.ip_address
      ) || null,

    mac_address:
      normalizeText(
        form.mac_address
      ).toUpperCase(),

    asset_number:
      normalizeText(
        form.asset_number
      ).toUpperCase(),

    firmware_version:
      normalizeText(
        form.firmware_version
      ),

    accessories_description:
      normalizeText(
        form.accessories_description
      ),

    unloading_observations:
      normalizeText(
        form.unloading_observations
      ),

    technical_notes:
      normalizeText(
        form.technical_notes
      ),

    commercial_notes:
      normalizeText(
        form.commercial_notes
      ),

    notes:
      normalizeText(
        form.notes
      ),

    is_active:
      form.is_active,
  }
}


function buildRequestData() {
  const payload = buildPayload()

  if (!mainPhotoFile.value) {
    return payload
  }

  const formData = new FormData()

  for (
    const [key, value]
    of Object.entries(payload)
  ) {
    if (
      value === null ||
      value === undefined
    ) {
      continue
    }

    formData.append(
      key,
      String(value)
    )
  }

  formData.append(
    "main_photo",
    mainPhotoFile.value
  )

  return formData
}


function validateForm() {
  if (!form.serial_number.trim()) {
    return "El número de serie es obligatorio."
  }

  if (!form.equipment_model) {
    return "Selecciona el modelo del equipo."
  }

  if (
    requiresOwnerPartner.value &&
    !form.owner_partner
  ) {
    return (
      "Debes indicar el propietario externo " +
      "del equipo."
    )
  }

  if (
    form.ownership_type === "own" &&
    form.owner_partner
  ) {
    return (
      "Un equipo propio no debe tener " +
      "propietario externo."
    )
  }

  if (
    requiresCustomer.value &&
    !form.customer
  ) {
    return (
      "El estado comercial seleccionado " +
      "requiere un cliente."
    )
  }

  if (
    form.customer_branch &&
    !form.customer
  ) {
    return (
      "Selecciona primero el cliente " +
      "antes de seleccionar una sucursal."
    )
  }

  if (
    requiresReservationDate.value &&
    !form.reservation_date
  ) {
    return (
      "Una máquina separada debe registrar " +
      "la fecha de separación."
    )
  }

  if (
    form.reservation_expiration_date &&
    !form.reservation_date
  ) {
    return (
      "Registra primero la fecha de separación."
    )
  }

  if (
    form.reservation_date &&
    form.reservation_expiration_date &&
    new Date(
      form.reservation_expiration_date
    ) <
    new Date(
      form.reservation_date
    )
  ) {
    return (
      "El vencimiento de la separación no puede " +
      "ser anterior a la fecha de separación."
    )
  }

  if (
    requiresSaleDate.value &&
    !form.sale_date
  ) {
    return (
      "Este estado comercial requiere " +
      "registrar la fecha de venta."
    )
  }

  if (
    requiresDeliveryDate.value &&
    !form.delivery_date
  ) {
    return (
      "Una máquina entregada debe registrar " +
      "la fecha real de entrega."
    )
  }

  if (
    requiresTechnicalReason.value &&
    !form.technical_status_reason.trim()
  ) {
    return (
      "Indica el motivo del estado técnico."
    )
  }

  if (
    Number(form.purchase_price) < 0 ||
    Number(form.allocated_import_cost) < 0 ||
    Number(form.sale_price) < 0
  ) {
    return (
      "Los importes económicos no pueden " +
      "ser negativos."
    )
  }

  if (
    Number(form.current_total_meter) <
    Number(form.initial_total_meter)
  ) {
    return (
      "El contador total actual no puede ser " +
      "menor que el contador inicial."
    )
  }

  if (
    Number(form.current_black_meter) <
    Number(form.initial_black_meter)
  ) {
    return (
      "El contador B/N actual no puede ser " +
      "menor que el contador inicial."
    )
  }

  if (
    Number(form.current_color_meter) <
    Number(form.initial_color_meter)
  ) {
    return (
      "El contador color actual no puede ser " +
      "menor que el contador inicial."
    )
  }

  if (
    Number(form.current_scan_meter) <
    Number(form.initial_scan_meter)
  ) {
    return (
      "El contador de escaneo actual no puede " +
      "ser menor que el contador inicial."
    )
  }

  if (
    selectedModelIsMonochrome.value &&
    (
      Number(form.initial_color_meter) > 0 ||
      Number(form.current_color_meter) > 0
    )
  ) {
    return (
      "Un equipo blanco y negro no puede " +
      "registrar contador color."
    )
  }

  if (
    !selectedModelHasScanMeter.value &&
    (
      Number(form.initial_scan_meter) > 0 ||
      Number(form.current_scan_meter) > 0
    )
  ) {
    return (
      "El modelo seleccionado no utiliza " +
      "contador de escaneo."
    )
  }

  return ""
}


async function loadCatalogs() {
  loadingCatalogs.value = true

  try {
    const [
      typesResponse,
      brandsResponse,
      modelsResponse,
      batchesResponse,
      partnersResponse,
      usersResponse,
    ] = await Promise.all([
      getEquipmentTypes({
        isActive: true,
      }),
      getEquipmentBrands({
        isActive: true,
      }),
      getEquipmentModels({
        isActive: true,
      }),
      getImportBatches({
        isActive: true,
      }),
      getPartners({
        isActive: true,
      }),
      getUsers({
        isActive: true,
      }),
    ])

    equipmentTypes.value =
      Array.isArray(typesResponse)
        ? typesResponse
        : typesResponse?.results || []

    brands.value =
      Array.isArray(brandsResponse)
        ? brandsResponse
        : brandsResponse?.results || []

    equipmentModels.value =
      Array.isArray(modelsResponse)
        ? modelsResponse
        : modelsResponse?.results || []

    importBatches.value =
      Array.isArray(batchesResponse)
        ? batchesResponse
        : batchesResponse?.results || []

    partners.value =
      Array.isArray(partnersResponse)
        ? partnersResponse
        : partnersResponse?.results || []

    users.value =
      Array.isArray(usersResponse)
        ? usersResponse
        : usersResponse?.results || []
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudieron cargar los catálogos."
  } finally {
    loadingCatalogs.value = false
  }
}


async function loadCustomerBranches() {
  customerBranches.value = []

  if (!form.customer) {
    form.customer_branch = ""
    return
  }

  loadingBranches.value = true

  try {
    const response =
      await getPartnerBranches({
        partner: form.customer,
        isActive: true,
      })

    customerBranches.value =
      Array.isArray(response)
        ? response
        : response?.results || []

    if (
      form.customer_branch &&
      !customerBranches.value.some(
        (branch) => (
          branch.id === form.customer_branch
        )
      )
    ) {
      form.customer_branch = ""
    }
  } catch {
    customerBranches.value = []
    form.customer_branch = ""
  } finally {
    loadingBranches.value = false
  }
}


async function loadEquipment() {
  if (!isEditing.value) {
    return
  }

  loading.value = true
  errorMessage.value = ""

  try {
    const equipment =
      await getEquipmentById(
        route.params.id
      )

    for (
      const field of Object.keys(form)
    ) {
      if (
        Object.prototype.hasOwnProperty.call(
          equipment,
          field
        )
      ) {
        form[field] =
          equipment[field] ?? form[field]
      }
    }

    form.equipment_model =
      equipment.equipment_model || ""

    form.import_batch =
      equipment.import_batch || ""

    form.supplier =
      equipment.supplier || ""

    form.owner_partner =
      equipment.owner_partner || ""

    form.customer =
      equipment.customer || ""

    form.customer_branch =
      equipment.customer_branch || ""

    const selectedCustomer =
      partners.value.find(
        (partner) => (
          partner.id === form.customer
        )
      )

    form.advisor =
      equipment.advisor ||
      selectedCustomer?.advisor ||
      selectedCustomer?.advisor_id ||
      ""

    form.purchase_invoice_date =
      equipment.purchase_invoice_date || ""

    form.purchase_date =
      equipment.purchase_date || ""

    form.unloading_date =
      toLocalDateTimeInput(
        equipment.unloading_date
      )

    form.sale_invoice_date =
      equipment.sale_invoice_date || ""

    form.reservation_date =
      toLocalDateTimeInput(
        equipment.reservation_date
      )

    form.reservation_expiration_date =
      toLocalDateTimeInput(
        equipment.reservation_expiration_date
      )

    form.sale_date =
      equipment.sale_date || ""

    form.delivery_date =
      toLocalDateTimeInput(
        equipment.delivery_date
      )

    form.last_meter_date =
      toLocalDateTimeInput(
        equipment.last_meter_date
      )

    form.is_active =
      Boolean(equipment.is_active)

    mainPhotoPreview.value =
      equipment.main_photo_url ||
      equipment.main_photo ||
      ""

    const model =
      equipmentModels.value.find(
        (item) => (
          item.id === form.equipment_model
        )
      )

    if (model) {
      form.brand_filter =
        model.brand ||
        model.brand_id ||
        ""

      form.equipment_type_filter =
        model.equipment_type ||
        model.equipment_type_id ||
        ""
    }

    await loadCustomerBranches()
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo cargar el equipo."
  } finally {
    loading.value = false
  }
}


function handlePhotoChange(event) {
  const file =
    event.target.files?.[0]

  if (!file) {
    mainPhotoFile.value = null
    return
  }

  if (!file.type.startsWith("image/")) {
    errorMessage.value =
      "Selecciona un archivo de imagen válido."

    event.target.value = ""
    return
  }

  const maximumSize =
    8 * 1024 * 1024

  if (file.size > maximumSize) {
    errorMessage.value =
      "La fotografía no puede superar 8 MB."

    event.target.value = ""
    return
  }

  mainPhotoFile.value = file

  if (
    mainPhotoPreview.value &&
    mainPhotoPreview.value.startsWith(
      "blob:"
    )
  ) {
    URL.revokeObjectURL(
      mainPhotoPreview.value
    )
  }

  mainPhotoPreview.value =
    URL.createObjectURL(file)
}


function removePhotoSelection() {
  if (
    mainPhotoPreview.value &&
    mainPhotoPreview.value.startsWith(
      "blob:"
    )
  ) {
    URL.revokeObjectURL(
      mainPhotoPreview.value
    )
  }

  mainPhotoFile.value = null
  mainPhotoPreview.value = ""
}


async function submitForm() {
  errorMessage.value = ""

  const validationError =
    validateForm()

  if (validationError) {
    errorMessage.value =
      validationError

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    })

    return
  }

  saving.value = true

  try {
    const requestData =
      buildRequestData()

    if (isEditing.value) {
      await updateEquipment(
        route.params.id,
        requestData
      )
    } else {
      await createEquipment(
        requestData
      )
    }

    await router.push({
      name: "equipment",
    })
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo guardar el equipo."

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    })
  } finally {
    saving.value = false
  }
}


async function cancel() {
  await router.push({
    name: "equipment",
  })
}


watch(
  () => form.customer,
  async (customer) => {
    if (customer) {
      const selectedCustomer =
        partners.value.find(
          (partner) => (
            partner.id === customer
          )
        )

      form.advisor =
        selectedCustomer?.advisor ||
        selectedCustomer?.advisor_id ||
        ""

      if (
        [
          "warehouse",
          "returned",
        ].includes(form.commercial_status)
      ) {
        form.commercial_status = "reserved"
      }

      if (!form.reservation_date) {
        form.reservation_date =
          toLocalDateTimeInput(
            new Date().toISOString()
          )
      }

      await loadCustomerBranches()
      return
    }

    form.customer_branch = ""
    form.advisor = ""
    customerBranches.value = []

    if (
      form.commercial_status === "reserved"
    ) {
      form.commercial_status = "warehouse"
    }

    form.reservation_date = ""
    form.reservation_expiration_date = ""
  }
)


watch(
  () => form.ownership_type,
  (ownershipType) => {
    if (ownershipType === "own") {
      form.owner_partner = ""
    }
  }
)


watch(
  () => form.technical_status,
  (technicalStatus) => {
    if (
      ![
        "with_problems",
        "for_parts",
      ].includes(technicalStatus)
    ) {
      form.technical_status_reason = ""
    }
  }
)


watch(
  () => form.commercial_status,
  (commercialStatus) => {
    if (
      commercialStatus === "reserved" &&
      !form.reservation_date
    ) {
      form.reservation_date =
        toLocalDateTimeInput(
          new Date().toISOString()
        )
    }

    if (
      [
        "warehouse",
        "returned",
      ].includes(commercialStatus)
    ) {
      form.customer = ""
      form.customer_branch = ""
      form.advisor = ""
      form.reservation_date = ""
      form.reservation_expiration_date = ""
    }
  }
)


watch(
  () => form.equipment_model,
  () => {
    if (selectedModelIsMonochrome.value) {
      form.initial_color_meter = 0
      form.current_color_meter = 0
    }

    if (!selectedModelHasScanMeter.value) {
      form.initial_scan_meter = 0
      form.current_scan_meter = 0
    }
  }
)


watch(
  [
    () => form.brand_filter,
    () => form.equipment_type_filter,
  ],
  () => {
    if (
      form.equipment_model &&
      !filteredModels.value.some(
        (model) => (
          model.id === form.equipment_model
        )
      )
    ) {
      form.equipment_model = ""
    }
  }
)


onMounted(async () => {
  await loadCatalogs()
  await loadEquipment()
})
</script>

<template>
  <section class="equipment-form-page">
    <header class="page-header">
      <div>
        <span class="page-kicker">Inventario de máquinas</span>
        <h2>{{ pageTitle }}</h2>
        <p>
          {{
            isEditing
              ? "Actualiza la información comercial, técnica y documental del equipo."
              : "Registra la máquina con la información necesaria para almacén, taller y ventas."
          }}
        </p>
      </div>

      <button class="secondary-button" type="button" @click="cancel">
        Volver
      </button>
    </header>

    <div v-if="errorMessage" class="message error-message">
      {{ errorMessage }}
    </div>

    <div v-if="loading || loadingCatalogs" class="loading-card">
      <span class="spinner"></span>
      Cargando información del equipo...
    </div>

    <form v-else class="form-container" @submit.prevent="submitForm">
      <section class="form-hero-card">
        <div class="equipment-photo-panel">
          <div class="photo-preview">
            <img
              v-if="mainPhotoPreview"
              :src="mainPhotoPreview"
              alt="Fotografía del equipo"
            />

            <div v-else class="photo-placeholder">
              <span>▣</span>
              <strong>Sin fotografía</strong>
            </div>
          </div>

          <div class="photo-controls">
            <label class="upload-button">
              <input type="file" accept="image/*" @change="handlePhotoChange" />
              Seleccionar fotografía
            </label>

            <button
              v-if="mainPhotoPreview"
              class="remove-photo-button"
              type="button"
              @click="removePhotoSelection"
            >
              Quitar selección
            </button>

            <small>Imagen de hasta 8 MB.</small>
          </div>
        </div>

        <div class="hero-form-content">
          <div class="hero-form-header">
            <div>
              <span class="hero-type-label">
                {{ selectedModel?.equipment_type_name || "Equipo" }}
              </span>

              <h3>{{ selectedModelName }}</h3>
            </div>

            <div class="status-preview-group">
              <span
                class="status-badge"
                :class="`technical-${form.technical_status}`"
              >
                {{
                  {
                    unreviewed: "Sin revisar",
                    for_review: "Para revisión",
                    in_review: "En revisión",
                    completed: "Finalizada",
                    with_problems: "Con problemas",
                    for_parts: "De partes",
                  }[form.technical_status]
                }}
              </span>

              <span
                class="status-badge"
                :class="`commercial-${form.commercial_status}`"
              >
                {{
                  {
                    warehouse: "En almacén",
                    reserved: "Separada",
                    sold: "Vendida",
                    delivery_preparation: "Preparando entrega",
                    in_transit: "En tránsito",
                    delivered: "Entregada",
                    contract_assigned: "Asignada a contrato",
                    installed: "Instalada",
                    return_process: "En retorno",
                    returned: "Retornada",
                    temporary_loan: "Préstamo",
                    demonstration: "Demostración",
                    replacement: "Reemplazo",
                    out_of_service: "Fuera de servicio",
                    disposed: "De baja",
                  }[form.commercial_status]
                }}
              </span>
            </div>
          </div>

          <div class="hero-fields-grid">
            <label class="form-field required">
              <span>Número de serie</span>
              <input
                v-model="form.serial_number"
                type="text"
                maxlength="150"
                placeholder="Serie del fabricante"
                required
              />
            </label>

            <label class="form-field">
              <span>Código interno</span>
              <input
                type="text"
                :value="
                  isEditing
                    ? 'El código actual no se modificará'
                    : 'Se generará automáticamente al guardar'
                "
                disabled
              />
            </label>

            <label class="form-field">
              <span>Tipo de equipo</span>
              <select v-model="form.equipment_type_filter">
                <option value="">Todos los tipos</option>
                <option v-for="item in equipmentTypes" :key="item.id" :value="item.id">
                  {{ item.name }}
                </option>
              </select>
            </label>

            <label class="form-field">
              <span>Marca</span>
              <select v-model="form.brand_filter">
                <option value="">Todas las marcas</option>
                <option v-for="brand in brands" :key="brand.id" :value="brand.id">
                  {{ brand.name }}
                </option>
              </select>
            </label>

            <label class="form-field required full-width">
              <span>Modelo</span>
              <select v-model="form.equipment_model" required>
                <option value="">Selecciona el modelo</option>
                <option v-for="model in filteredModels" :key="model.id" :value="model.id">
                  {{ getModelName(model) }}
                </option>
              </select>
            </label>
          </div>
        </div>
      </section>

      <div class="form-two-column-layout">
        <section class="form-card card-blue">
          <header>
            <div>
              <span class="card-kicker">Información principal</span>
              <h3>Datos del equipo</h3>
            </div>
          </header>

          <div class="compact-form-grid">
            <label class="form-field">
              <span>Condición física</span>
              <select v-model="form.physical_condition">
                <option value="new">Nueva</option>
                <option value="used">Usada</option>
                <option value="reconditioned">Reacondicionada</option>
                <option value="trade_in">Recibida en parte de pago</option>
                <option value="third_party">Propiedad de tercero</option>
                <option value="other">Otra</option>
              </select>
            </label>

            <label class="form-field">
              <span>Tipo de propiedad</span>
              <select v-model="form.ownership_type">
                <option value="own">Propiedad de la empresa</option>
                <option value="customer">Propiedad de cliente</option>
                <option value="supplier">Propiedad de proveedor</option>
                <option value="third_party">Propiedad de tercero</option>
                <option value="other">Otra</option>
              </select>
            </label>

            <label v-if="requiresOwnerPartner" class="form-field required full-width">
              <span>Propietario externo</span>
              <select v-model="form.owner_partner" required>
                <option value="">Selecciona el propietario</option>
                <option v-for="partner in ownerOptions" :key="partner.id" :value="partner.id">
                  {{ getPartnerName(partner) }}
                </option>
              </select>
            </label>

            <label class="form-field">
              <span>Ubicación actual</span>
              <input
                v-model="form.warehouse_location"
                type="text"
                maxlength="200"
                placeholder="Almacén, taller o zona"
              />
            </label>

            <label class="form-field">
              <span>Referencia de ubicación</span>
              <input
                v-model="form.position_reference"
                type="text"
                maxlength="100"
                placeholder="Fila, estante o espacio"
              />
            </label>
          </div>
        </section>

        <section class="form-card card-cyan">
          <header>
            <div>
              <span class="card-kicker">Procedencia</span>
              <h3>Datos de importación</h3>
            </div>
          </header>

          <div class="compact-form-grid">
            <label class="form-field">
              <span>Importación o lote</span>
              <select v-model="form.import_batch">
                <option value="">Sin lote relacionado</option>
                <option v-for="batch in importBatches" :key="batch.id" :value="batch.id">
                  {{ getImportBatchName(batch) }}
                </option>
              </select>
            </label>

            <label class="form-field">
              <span>Proveedor directo</span>
              <select v-model="form.supplier">
                <option value="">Sin proveedor</option>
                <option v-for="partner in supplierOptions" :key="partner.id" :value="partner.id">
                  {{ getPartnerName(partner) }}
                </option>
              </select>
            </label>

            <label class="form-field">
              <span>Referencia de importación</span>
              <input v-model="form.import_reference" type="text" maxlength="100" />
            </label>

            <label class="form-field">
              <span>Factura o invoice</span>
              <input v-model="form.purchase_invoice_number" type="text" maxlength="100" />
            </label>

            <label class="form-field">
              <span>Fecha de factura</span>
              <input v-model="form.purchase_invoice_date" type="date" />
            </label>

            <label class="form-field">
              <span>Fecha de compra</span>
              <input v-model="form.purchase_date" type="date" />
            </label>

            <label class="form-field full-width">
              <span>Fecha y hora de descarga</span>
              <input v-model="form.unloading_date" type="datetime-local" />
            </label>
          </div>
        </section>

        <section class="form-card card-red">
          <header>
            <div>
              <span class="card-kicker">Taller</span>
              <h3>Estado para revisión</h3>
            </div>
          </header>

          <div class="compact-form-grid">
            <label class="form-field required full-width">
              <span>Estado técnico</span>
              <select v-model="form.technical_status" required>
                <option value="unreviewed">Sin revisar</option>
                <option value="for_review">Para revisión</option>
                <option value="in_review">En revisión</option>
                <option value="completed">Finalizada</option>
                <option value="with_problems">Con problemas</option>
                <option value="for_parts">De partes</option>
              </select>
            </label>

            <label
              class="form-field full-width"
              :class="{ required: requiresTechnicalReason }"
            >
              <span>Motivo del estado técnico</span>
              <textarea
                v-model="form.technical_status_reason"
                rows="3"
                :required="requiresTechnicalReason"
                placeholder="Motivo, falla o trabajo pendiente"
              ></textarea>
            </label>

            <label class="form-field full-width">
              <span>Notas técnicas</span>
              <textarea
                v-model="form.technical_notes"
                rows="4"
                placeholder="Observaciones de revisión"
              ></textarea>
            </label>
          </div>
        </section>

        <section class="form-card card-green">
          <header>
            <div>
              <span class="card-kicker">Ventas</span>
              <h3>Situación comercial</h3>
            </div>
          </header>

          <div class="compact-form-grid">
            <label class="form-field required full-width">
              <span>Estado comercial</span>
              <select v-model="form.commercial_status" required>
                <option value="warehouse">En almacén</option>
                <option value="reserved">Separada</option>
                <option value="sold">Vendida</option>
                <option value="delivery_preparation">En preparación de entrega</option>
                <option value="in_transit">En tránsito</option>
                <option value="delivered">Entregada</option>
                <option value="contract_assigned">Asignada a contrato</option>
                <option value="installed">Instalada</option>
                <option value="return_process">En proceso de retorno</option>
                <option value="returned">Retornada a almacén</option>
                <option value="temporary_loan">Préstamo temporal</option>
                <option value="demonstration">Demostración</option>
                <option value="replacement">Equipo de reemplazo</option>
                <option value="out_of_service">Fuera de servicio</option>
                <option value="disposed">De baja</option>
              </select>
            </label>

            <label class="form-field full-width">
              <span>Motivo del estado comercial</span>
              <textarea
                v-model="form.commercial_status_reason"
                rows="3"
                placeholder="Motivo u observación"
              ></textarea>
            </label>

            <label class="form-field" :class="{ required: requiresCustomer }">
              <span>Cliente</span>
              <select v-model="form.customer" :required="requiresCustomer">
                <option value="">Sin cliente asignado</option>
                <option v-for="partner in customerOptions" :key="partner.id" :value="partner.id">
                  {{ getPartnerName(partner) }}
                </option>
              </select>
            </label>

            <label class="form-field">
              <span>Sucursal, obra o proyecto</span>
              <select
                v-model="form.customer_branch"
                :disabled="!form.customer || loadingBranches"
              >
                <option value="">Sin sucursal asignada</option>
                <option v-for="branch in customerBranches" :key="branch.id" :value="branch.id">
                  {{ branch.display_name || branch.name || branch.code || "Sucursal" }}
                </option>
              </select>
            </label>

            <label class="form-field full-width">
              <span>Asesor comercial</span>
              <select
                v-model="form.advisor"
                :disabled="Boolean(form.customer)"
              >
                <option value="">
                  {{
                    form.customer
                      ? "El cliente no tiene asesor asignado"
                      : "Sin asesor asignado"
                  }}
                </option>
                <option v-for="user in users" :key="user.id" :value="user.id">
                  {{ getUserName(user) }}
                </option>
              </select>
              <small v-if="form.customer">
                Se asigna automáticamente según el cliente.
              </small>
            </label>
          </div>
        </section>
      </div>

      <section class="form-section-card">
        <header class="section-title-row">
          <div>
            <span class="card-kicker">Lecturas</span>
            <h3>Contadores del equipo</h3>
          </div>
        </header>

        <div class="meters-layout">
          <div class="meter-group">
            <h4>Contadores de ingreso</h4>
            <div class="meter-grid">
              <label class="form-field"><span>Total inicial</span><input v-model.number="form.initial_total_meter" type="number" min="0" step="1" /></label>
              <label class="form-field"><span>B/N inicial</span><input v-model.number="form.initial_black_meter" type="number" min="0" step="1" /></label>
              <label class="form-field"><span>Color inicial</span><input v-model.number="form.initial_color_meter" type="number" min="0" step="1" :disabled="selectedModelIsMonochrome || !selectedModelHasColorMeter" /></label>
              <label class="form-field"><span>Escaneo inicial</span><input v-model.number="form.initial_scan_meter" type="number" min="0" step="1" :disabled="!selectedModelHasScanMeter" /></label>
            </div>
          </div>

          <div class="meter-group">
            <h4>Contadores actuales</h4>
            <div class="meter-grid">
              <label class="form-field"><span>Total actual</span><input v-model.number="form.current_total_meter" type="number" min="0" step="1" /></label>
              <label class="form-field"><span>B/N actual</span><input v-model.number="form.current_black_meter" type="number" min="0" step="1" /></label>
              <label class="form-field"><span>Color actual</span><input v-model.number="form.current_color_meter" type="number" min="0" step="1" :disabled="selectedModelIsMonochrome || !selectedModelHasColorMeter" /></label>
              <label class="form-field"><span>Escaneo actual</span><input v-model.number="form.current_scan_meter" type="number" min="0" step="1" :disabled="!selectedModelHasScanMeter" /></label>
            </div>
          </div>
        </div>

        <div class="section-form-grid">
          <label class="form-field">
            <span>Fecha de última lectura</span>
            <input v-model="form.last_meter_date" type="datetime-local" />
          </label>

          <label class="form-field">
            <span>Fuente de última lectura</span>
            <select v-model="form.last_meter_source">
              <option value="manual">Ingreso manual</option>
              <option value="download">Registro de descarga</option>
              <option value="mobile_app">Aplicación móvil</option>
              <option value="snmp">Lectura SNMP</option>
              <option value="repair">Reparación</option>
              <option value="installation">Instalación</option>
              <option value="removal">Retiro</option>
              <option value="delivery">Entrega</option>
              <option value="other">Otra fuente</option>
            </select>
          </label>
        </div>
      </section>

      <div class="form-two-column-layout">
        <section class="form-card card-indigo">
          <header><div><span class="card-kicker">Costos</span><h3>Compra</h3></div></header>
          <div class="compact-form-grid">
            <label class="form-field"><span>Moneda de compra</span><select v-model="form.purchase_currency"><option value="PEN">Soles</option><option value="USD">Dólares</option><option value="EUR">Euros</option><option value="OTHER">Otra</option></select></label>
            <label class="form-field"><span>Precio de compra</span><input v-model="form.purchase_price" type="number" min="0" step="0.01" /></label>
            <label class="form-field full-width"><span>Costo de importación asignado</span><input v-model="form.allocated_import_cost" type="number" min="0" step="0.01" /></label>
            <div class="calculated-card full-width"><span>Costo total estimado</span><strong>{{ new Intl.NumberFormat("es-PE", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(form.purchase_price || 0) + Number(form.allocated_import_cost || 0)) }} {{ form.purchase_currency }}</strong></div>
          </div>
        </section>

        <section class="form-card card-purple">
          <header><div><span class="card-kicker">Venta</span><h3>Datos de venta y separación</h3></div></header>
          <div class="compact-form-grid">
            <label class="form-field"><span>Moneda de venta</span><select v-model="form.sale_currency"><option value="PEN">Soles</option><option value="USD">Dólares</option><option value="EUR">Euros</option><option value="OTHER">Otra</option></select></label>
            <label class="form-field"><span>Precio de venta</span><input v-model="form.sale_price" type="number" min="0" step="0.01" /></label>
            <label class="form-field"><span>Factura de venta</span><input v-model="form.sale_invoice_number" type="text" maxlength="100" /></label>
            <label class="form-field"><span>Fecha de factura</span><input v-model="form.sale_invoice_date" type="date" /></label>
            <label class="form-field" :class="{ required: requiresReservationDate }"><span>Fecha de separación</span><input v-model="form.reservation_date" type="datetime-local" :required="requiresReservationDate" /></label>
            <label class="form-field"><span>Vencimiento de separación</span><input v-model="form.reservation_expiration_date" type="datetime-local" /></label>
            <label class="form-field" :class="{ required: requiresSaleDate }"><span>Fecha de venta</span><input v-model="form.sale_date" type="date" :required="requiresSaleDate" /></label>
            <label class="form-field" :class="{ required: requiresDeliveryDate }"><span>Fecha real de entrega</span><input v-model="form.delivery_date" type="datetime-local" :required="requiresDeliveryDate" /></label>
          </div>
        </section>
      </div>

      <section class="form-section-card">
        <header class="section-title-row"><div><span class="card-kicker">Instalación y monitoreo</span><h3>Red, activos y configuración</h3></div></header>
        <div class="section-form-grid three-columns">
          <label class="form-field"><span>Nombre de red</span><input v-model="form.hostname" type="text" maxlength="150" placeholder="Hostname" /></label>
          <label class="form-field"><span>Dirección IP</span><input v-model="form.ip_address" type="text" placeholder="192.168.1.100" /></label>
          <label class="form-field"><span>Dirección MAC</span><input v-model="form.mac_address" type="text" maxlength="50" placeholder="00:00:00:00:00:00" /></label>
          <label class="form-field"><span>Código patrimonial</span><input v-model="form.asset_number" type="text" maxlength="100" /></label>
          <label class="form-field"><span>Versión de firmware</span><input v-model="form.firmware_version" type="text" maxlength="100" /></label>
          <label class="form-field"><span>Equipo activo</span><label class="active-toggle"><input v-model="form.is_active" type="checkbox" /><span>Disponible para operaciones</span></label></label>
        </div>
      </section>

      <section class="form-section-card">
        <header class="section-title-row"><div><span class="card-kicker">Información adicional</span><h3>Configuración y observaciones</h3></div></header>
        <div class="section-form-grid">
          <label class="form-field full-width"><span>Configuración recibida</span><textarea v-model="form.accessories_description" rows="4" placeholder="ADF, finalizador, bandejas, pedestal y otros accesorios"></textarea></label>
          <label class="form-field full-width"><span>Observaciones de descarga</span><textarea v-model="form.unloading_observations" rows="4"></textarea></label>
          <label class="form-field full-width"><span>Notas comerciales</span><textarea v-model="form.commercial_notes" rows="4"></textarea></label>
          <label class="form-field full-width"><span>Observaciones generales</span><textarea v-model="form.notes" rows="5"></textarea></label>
        </div>
      </section>

      <footer class="form-actions">
        <button class="secondary-button" type="button" :disabled="saving" @click="cancel">
          Cancelar
        </button>

        <button class="primary-button" type="submit" :disabled="saving">
          <span v-if="saving" class="button-spinner"></span>
          {{ saving ? "Guardando..." : isEditing ? "Guardar cambios" : "Crear equipo" }}
        </button>
      </footer>
    </form>
  </section>
</template>

<style scoped src="./styles/equipment-form.css"></style>
