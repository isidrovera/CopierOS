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

import PartnerRelationsSection from "../../components/partners/PartnerRelationsSection.vue"

import {
  createPartner,
  getPartner,
  updatePartner,
} from "../../services/partners.service"

import {
  getUsers,
} from "../../services/users.service"


const route = useRoute()
const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const loadingUsers = ref(false)
const errorMessage = ref("")

const users = ref([])


const isEditing = computed(() => {
  return Boolean(route.params.id)
})


const pageTitle = computed(() => {
  return isEditing.value
    ? "Editar cliente o proveedor"
    : "Nuevo cliente o proveedor"
})


const isPeruvian = computed(() => {
  return form.country_code === "PE"
})


const isLegalPerson = computed(() => {
  return form.person_type === "legal"
})


const isNaturalPerson = computed(() => {
  return form.person_type === "natural"
})


const requiresAdvisor = computed(() => {
  return (
    form.is_rental_customer ||
    form.is_sales_customer ||
    form.is_service_customer ||
    form.is_distributor
  )
})


const isSupplierOnly = computed(() => {
  return (
    form.is_supplier &&
    !requiresAdvisor.value
  )
})


const hasAnyRole = computed(() => {
  return (
    form.is_rental_customer ||
    form.is_sales_customer ||
    form.is_service_customer ||
    form.is_supplier ||
    form.is_distributor
  )
})


const documentOptions = computed(() => {
  if (isPeruvian.value) {
    return [
      {
        value: "ruc",
        label: "RUC",
      },
      {
        value: "dni",
        label: "DNI",
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
  }

  return [
    {
      value: "foreign_id",
      label: "Documento extranjero",
    },
    {
      value: "ein",
      label: "EIN",
    },
    {
      value: "tax_id",
      label: "Tax ID",
    },
    {
      value: "registration",
      label: "Registro empresarial",
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
})


const form = reactive({
  code: "",

  person_type: "legal",

  country_code: "PE",
  country_name: "Perú",

  document_type: "ruc",
  document_number: "",
  document_source: "manual",
  document_verified: false,

  legal_name: "",
  trade_name: "",

  first_names: "",
  paternal_last_name: "",
  maternal_last_name: "",

  classification: "other",

  is_rental_customer: false,
  is_sales_customer: false,
  is_service_customer: false,
  is_supplier: false,
  is_distributor: false,

  advisor: "",
  purchasing_manager: "",

  general_phone: "",
  mobile_phone: "",
  general_email: "",
  billing_email: "",
  website: "",

  fiscal_address: "",
  address_reference: "",
  ubigeo: "",
  road_type: "",
  road_name: "",
  zone_code: "",
  zone_type: "",
  address_number: "",
  interior: "",
  lot: "",
  apartment: "",
  block: "",
  kilometer: "",
  district: "",
  province: "",
  region: "",
  postal_code: "",

  sunat_status: "",
  sunat_condition: "",
  taxpayer_type: "",
  economic_activity: "",
  employee_count: null,
  billing_type: "",
  accounting_type: "",
  foreign_trade: "",
  is_withholding_agent: false,

  preferred_currency: "PEN",
  preferred_language: "es",
  payment_terms: "",
  credit_days: 0,
  credit_limit: "0.00",

  requires_purchase_order: false,
  requires_service_conformity: false,
  requires_delivery_guide: false,

  is_commercially_blocked: false,
  commercial_block_reason: "",

  is_active: true,
  notes: "",
})


function normalizeText(value) {
  return typeof value === "string"
    ? value.trim()
    : value
}


function normalizeNullableId(value) {
  return value || null
}


function buildPayload() {
  return {
    code:
      normalizeText(form.code) || "",

    person_type:
      form.person_type,

    country_code:
      normalizeText(
        form.country_code
      ).toUpperCase(),

    country_name:
      normalizeText(
        form.country_name
      ),

    document_type:
      form.document_type,

    document_number:
      normalizeText(
        form.document_number
      )
        .replace(/\s+/g, "")
        .toUpperCase(),

    document_source:
      form.document_source,

    document_verified:
      form.document_verified,

    legal_name:
      normalizeText(
        form.legal_name
      ),

    trade_name:
      normalizeText(
        form.trade_name
      ),

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

    classification:
      form.classification,

    is_rental_customer:
      form.is_rental_customer,

    is_sales_customer:
      form.is_sales_customer,

    is_service_customer:
      form.is_service_customer,

    is_supplier:
      form.is_supplier,

    is_distributor:
      form.is_distributor,

    advisor:
      normalizeNullableId(
        form.advisor
      ),

    purchasing_manager:
      normalizeNullableId(
        form.purchasing_manager
      ),

    general_phone:
      normalizeText(
        form.general_phone
      ),

    mobile_phone:
      normalizeText(
        form.mobile_phone
      ),

    general_email:
      normalizeText(
        form.general_email
      ).toLowerCase(),

    billing_email:
      normalizeText(
        form.billing_email
      ).toLowerCase(),

    website:
      normalizeText(
        form.website
      ),

    fiscal_address:
      normalizeText(
        form.fiscal_address
      ),

    address_reference:
      normalizeText(
        form.address_reference
      ),

    ubigeo:
      normalizeText(
        form.ubigeo
      ),

    road_type:
      normalizeText(
        form.road_type
      ),

    road_name:
      normalizeText(
        form.road_name
      ),

    zone_code:
      normalizeText(
        form.zone_code
      ),

    zone_type:
      normalizeText(
        form.zone_type
      ),

    address_number:
      normalizeText(
        form.address_number
      ),

    interior:
      normalizeText(
        form.interior
      ),

    lot:
      normalizeText(
        form.lot
      ),

    apartment:
      normalizeText(
        form.apartment
      ),

    block:
      normalizeText(
        form.block
      ),

    kilometer:
      normalizeText(
        form.kilometer
      ),

    district:
      normalizeText(
        form.district
      ),

    province:
      normalizeText(
        form.province
      ),

    region:
      normalizeText(
        form.region
      ),

    postal_code:
      normalizeText(
        form.postal_code
      ),

    sunat_status:
      normalizeText(
        form.sunat_status
      ),

    sunat_condition:
      normalizeText(
        form.sunat_condition
      ),

    taxpayer_type:
      normalizeText(
        form.taxpayer_type
      ),

    economic_activity:
      normalizeText(
        form.economic_activity
      ),

    employee_count:
      form.employee_count === ""
        ? null
        : form.employee_count,

    billing_type:
      normalizeText(
        form.billing_type
      ),

    accounting_type:
      normalizeText(
        form.accounting_type
      ),

    foreign_trade:
      normalizeText(
        form.foreign_trade
      ),

    is_withholding_agent:
      form.is_withholding_agent,

    preferred_currency:
      form.preferred_currency,

    preferred_language:
      normalizeText(
        form.preferred_language
      ),

    payment_terms:
      normalizeText(
        form.payment_terms
      ),

    credit_days:
      Number(
        form.credit_days || 0
      ),

    credit_limit:
      String(
        form.credit_limit || "0.00"
      ),

    requires_purchase_order:
      form.requires_purchase_order,

    requires_service_conformity:
      form.requires_service_conformity,

    requires_delivery_guide:
      form.requires_delivery_guide,

    is_commercially_blocked:
      form.is_commercially_blocked,

    commercial_block_reason:
      normalizeText(
        form.commercial_block_reason
      ),

    is_active:
      form.is_active,

    notes:
      normalizeText(
        form.notes
      ),
  }
}


function validateForm() {
  if (!form.country_code.trim()) {
    return "El país es obligatorio."
  }

  if (!form.document_type) {
    return "Selecciona el tipo de documento."
  }

  if (!form.document_number.trim()) {
    return "El número de documento es obligatorio."
  }

  if (
    form.document_type === "dni" &&
    !/^\d{8}$/.test(
      form.document_number.trim()
    )
  ) {
    return "El DNI debe contener exactamente 8 números."
  }

  if (
    form.document_type === "ruc" &&
    !/^\d{11}$/.test(
      form.document_number.trim()
    )
  ) {
    return "El RUC debe contener exactamente 11 números."
  }

  if (
    isLegalPerson.value &&
    !form.legal_name.trim()
  ) {
    return "La razón social es obligatoria."
  }

  if (
    isNaturalPerson.value &&
    !form.first_names.trim()
  ) {
    return "Los nombres son obligatorios."
  }

  if (
    isNaturalPerson.value &&
    !form.paternal_last_name.trim()
  ) {
    return "El apellido paterno es obligatorio."
  }

  if (!hasAnyRole.value) {
    return (
      "Selecciona al menos un tipo comercial: " +
      "cliente, proveedor o distribuidor."
    )
  }

  if (
    requiresAdvisor.value &&
    !form.advisor
  ) {
    return (
      "Debes asignar una asesora o " +
      "responsable comercial."
    )
  }

  if (
    isSupplierOnly.value &&
    !form.purchasing_manager
  ) {
    return (
      "Debes asignar un responsable " +
      "de compras al proveedor."
    )
  }

  if (
    form.is_commercially_blocked &&
    !form.commercial_block_reason.trim()
  ) {
    return (
      "Indica el motivo del bloqueo comercial."
    )
  }

  if (
    Number(form.credit_days) < 0
  ) {
    return (
      "Los días de crédito no pueden ser negativos."
    )
  }

  if (
    Number(form.credit_limit) < 0
  ) {
    return (
      "El límite de crédito no puede ser negativo."
    )
  }

  return ""
}


async function loadUsers() {
  loadingUsers.value = true

  try {
    const response = await getUsers({
      isActive: true,
    })

    users.value = Array.isArray(response)
      ? response
      : response?.results || []
  } catch {
    users.value = []
  } finally {
    loadingUsers.value = false
  }
}


async function loadPartner() {
  if (!isEditing.value) {
    return
  }

  loading.value = true
  errorMessage.value = ""

  try {
    const partner = await getPartner(
      route.params.id
    )

    for (
      const field of Object.keys(form)
    ) {
      if (
        Object.prototype.hasOwnProperty.call(
          partner,
          field
        )
      ) {
        form[field] =
          partner[field] ?? form[field]
      }
    }

    form.advisor =
      partner.advisor || ""

    form.purchasing_manager =
      partner.purchasing_manager || ""

    form.employee_count =
      partner.employee_count ?? null

    form.credit_days =
      partner.credit_days ?? 0

    form.credit_limit =
      partner.credit_limit ?? "0.00"

    form.is_active =
      Boolean(partner.is_active)

    form.document_verified =
      Boolean(
        partner.document_verified
      )

    form.is_rental_customer =
      Boolean(
        partner.is_rental_customer
      )

    form.is_sales_customer =
      Boolean(
        partner.is_sales_customer
      )

    form.is_service_customer =
      Boolean(
        partner.is_service_customer
      )

    form.is_supplier =
      Boolean(
        partner.is_supplier
      )

    form.is_distributor =
      Boolean(
        partner.is_distributor
      )

    form.is_withholding_agent =
      Boolean(
        partner.is_withholding_agent
      )

    form.requires_purchase_order =
      Boolean(
        partner.requires_purchase_order
      )

    form.requires_service_conformity =
      Boolean(
        partner.requires_service_conformity
      )

    form.requires_delivery_guide =
      Boolean(
        partner.requires_delivery_guide
      )

    form.is_commercially_blocked =
      Boolean(
        partner.is_commercially_blocked
      )
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo cargar el registro."
  } finally {
    loading.value = false
  }
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
    const payload =
      buildPayload()

    if (isEditing.value) {
      await updatePartner(
        route.params.id,
        payload
      )
    } else {
      await createPartner(
        payload
      )
    }

    await router.push({
      name: "partners",
    })
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo guardar el registro."

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
    name: "partners",
  })
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


watch(
  () => form.country_code,
  (countryCode) => {
    const normalized = String(
      countryCode || ""
    )
      .trim()
      .toUpperCase()

    form.country_code = normalized

    if (normalized === "PE") {
      form.country_name = "Perú"

      if (
        ![
          "dni",
          "ruc",
          "passport",
          "other",
        ].includes(
          form.document_type
        )
      ) {
        form.document_type =
          form.person_type === "natural"
            ? "dni"
            : "ruc"
      }
    }

    if (
      normalized === "US" &&
      !form.country_name
    ) {
      form.country_name =
        "Estados Unidos"
    }

    if (
      normalized !== "PE" &&
      [
        "dni",
        "ruc",
      ].includes(
        form.document_type
      )
    ) {
      form.document_type =
        form.person_type === "natural"
          ? "foreign_id"
          : "tax_id"
    }
  }
)


watch(
  () => form.person_type,
  (personType) => {
    if (
      personType === "natural" &&
      form.country_code === "PE" &&
      form.document_type === "ruc"
    ) {
      form.document_type = "dni"
    }

    if (
      personType === "legal" &&
      form.country_code === "PE" &&
      form.document_type === "dni"
    ) {
      form.document_type = "ruc"
    }
  }
)


watch(
  () => form.is_commercially_blocked,
  (blocked) => {
    if (!blocked) {
      form.commercial_block_reason = ""
    }
  }
)


onMounted(async () => {
  await Promise.all([
    loadUsers(),
    loadPartner(),
  ])
})
</script>

<template>
  <section class="partner-form-page">
    <header class="page-header">
      <div>
        <span class="page-kicker">
          Gestión comercial
        </span>

        <h2>
          {{ pageTitle }}
        </h2>

        <p>
          {{
            isEditing
              ? "Modifica la información comercial, fiscal y de contacto."
              : "Registra un cliente, proveedor o distribuidor en Copier OS."
          }}
        </p>
      </div>

      <button
        class="back-button"
        type="button"
        @click="cancel"
      >
        <svg
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path d="M19 12H5" />
          <path d="M12 19l-7-7 7-7" />
        </svg>

        <span>Volver</span>
      </button>
    </header>

    <div
      v-if="errorMessage"
      class="message error-message"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="loading"
      class="loading-card"
    >
      <span class="spinner"></span>
      Cargando información...
    </div>

    <form
      v-else
      class="form-container"
      @submit.prevent="submitForm"
    >
      <section class="form-section">
        <header class="section-header">
          <div>
            <h3>
              Identificación
            </h3>

            <p>
              País, tipo de persona y documento.
            </p>
          </div>
        </header>

        <div class="form-grid">
          <label class="form-field">
            <span>Código interno</span>

            <input
              v-model="form.code"
              type="text"
              maxlength="30"
              placeholder="Código opcional"
            />
          </label>

          <label class="form-field required">
            <span>Tipo de persona</span>

            <select
              v-model="form.person_type"
              required
            >
              <option value="legal">
                Persona jurídica
              </option>

              <option value="natural">
                Persona natural
              </option>
            </select>
          </label>

          <label class="form-field required">
            <span>Código de país</span>

            <input
              v-model="form.country_code"
              type="text"
              maxlength="2"
              placeholder="PE"
              required
            />
          </label>

          <label class="form-field required">
            <span>Nombre del país</span>

            <input
              v-model="form.country_name"
              type="text"
              placeholder="Perú"
              required
            />
          </label>

          <label class="form-field required">
            <span>Tipo de documento</span>

            <select
              v-model="form.document_type"
              required
            >
              <option
                v-for="option in documentOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </label>

          <label class="form-field required">
            <span>Número de documento</span>

            <input
              v-model="form.document_number"
              type="text"
              maxlength="20"
              placeholder="Número de documento"
              required
            />
          </label>

          <label class="form-field">
            <span>Origen del documento</span>

            <select
              v-model="form.document_source"
            >
              <option value="manual">
                Registro manual
              </option>

              <option value="sunat">
                Consulta SUNAT
              </option>

              <option value="other">
                Otra fuente
              </option>
            </select>
          </label>

          <label class="option-card compact">
            <input
              v-model="form.document_verified"
              type="checkbox"
            />

            <div>
              <strong>
                Documento verificado
              </strong>

              <span>
                La identidad o información fiscal
                fue validada.
              </span>
            </div>
          </label>
        </div>
      </section>

      <section class="form-section">
        <header class="section-header">
          <div>
            <h3>
              Nombre o razón social
            </h3>

            <p>
              Información principal para identificar
              al registro.
            </p>
          </div>
        </header>

        <div
          v-if="isLegalPerson"
          class="form-grid"
        >
          <label class="form-field required full-width">
            <span>Razón social</span>

            <input
              v-model="form.legal_name"
              type="text"
              placeholder="Razón social completa"
              required
            />
          </label>

          <label class="form-field full-width">
            <span>Nombre comercial</span>

            <input
              v-model="form.trade_name"
              type="text"
              placeholder="Nombre comercial"
            />
          </label>
        </div>

        <div
          v-else
          class="form-grid"
        >
          <label class="form-field required">
            <span>Nombres</span>

            <input
              v-model="form.first_names"
              type="text"
              placeholder="Nombres"
              required
            />
          </label>

          <label class="form-field required">
            <span>Apellido paterno</span>

            <input
              v-model="form.paternal_last_name"
              type="text"
              placeholder="Apellido paterno"
              required
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
            <span>Nombre comercial</span>

            <input
              v-model="form.trade_name"
              type="text"
              placeholder="Nombre comercial opcional"
            />
          </label>
        </div>
      </section>

      <section class="form-section">
        <header class="section-header">
          <div>
            <h3>
              Tipos comerciales
            </h3>

            <p>
              Un mismo registro puede tener varios
              tipos simultáneamente.
            </p>
          </div>
        </header>

        <div class="options-grid roles-grid">
          <label class="option-card">
            <input
              v-model="form.is_rental_customer"
              type="checkbox"
            />

            <div>
              <strong>
                Cliente de alquiler
              </strong>

              <span>
                Puede tener contratos de alquiler
                de equipos.
              </span>
            </div>
          </label>

          <label class="option-card">
            <input
              v-model="form.is_sales_customer"
              type="checkbox"
            />

            <div>
              <strong>
                Cliente de ventas
              </strong>

              <span>
                Puede comprar equipos, repuestos
                o suministros.
              </span>
            </div>
          </label>

          <label class="option-card">
            <input
              v-model="form.is_service_customer"
              type="checkbox"
            />

            <div>
              <strong>
                Cliente de servicios
              </strong>

              <span>
                Puede solicitar mantenimiento
                o asistencia técnica.
              </span>
            </div>
          </label>

          <label class="option-card">
            <input
              v-model="form.is_supplier"
              type="checkbox"
            />

            <div>
              <strong>
                Proveedor
              </strong>

              <span>
                Suministra equipos, repuestos
                o servicios.
              </span>
            </div>
          </label>

          <label class="option-card">
            <input
              v-model="form.is_distributor"
              type="checkbox"
            />

            <div>
              <strong>
                Distribuidor
              </strong>

              <span>
                Distribuye productos o representa
                marcas.
              </span>
            </div>
          </label>
        </div>
      </section>

      <section class="form-section">
        <header class="section-header">
          <div>
            <h3>
              Responsables
            </h3>

            <p>
              Usuario comercial o responsable interno
              asignado.
            </p>
          </div>
        </header>

        <div class="form-grid">
          <label
            class="form-field"
            :class="{
              required: requiresAdvisor,
            }"
          >
            <span>
              Asesora o responsable comercial
            </span>

            <select
              v-model="form.advisor"
              :required="requiresAdvisor"
              :disabled="loadingUsers"
            >
              <option value="">
                Sin asignar
              </option>

              <option
                v-for="user in users"
                :key="user.id"
                :value="user.id"
              >
                {{ getUserName(user) }}
              </option>
            </select>
          </label>

          <label
            class="form-field"
            :class="{
              required: isSupplierOnly,
            }"
          >
            <span>
              Responsable de compras
            </span>

            <select
              v-model="form.purchasing_manager"
              :required="isSupplierOnly"
              :disabled="loadingUsers"
            >
              <option value="">
                Sin asignar
              </option>

              <option
                v-for="user in users"
                :key="user.id"
                :value="user.id"
              >
                {{ getUserName(user) }}
              </option>
            </select>
          </label>

          <label class="form-field">
            <span>Clasificación</span>

            <select
              v-model="form.classification"
            >
              <option value="corporate">
                Corporativo
              </option>

              <option value="small_business">
                Pequeña y mediana empresa
              </option>

              <option value="government">
                Entidad pública
              </option>

              <option value="education">
                Institución educativa
              </option>

              <option value="health">
                Institución de salud
              </option>

              <option value="independent">
                Independiente
              </option>

              <option value="other">
                Otro
              </option>
            </select>
          </label>
        </div>
      </section>

      <section class="form-section">
        <header class="section-header">
          <div>
            <h3>
              Contacto general
            </h3>

            <p>
              Canales generales de comunicación.
            </p>
          </div>
        </header>

        <div class="form-grid">
          <label class="form-field">
            <span>Teléfono general</span>

            <input
              v-model="form.general_phone"
              type="tel"
              placeholder="Teléfono fijo"
            />
          </label>

          <label class="form-field">
            <span>Celular</span>

            <input
              v-model="form.mobile_phone"
              type="tel"
              placeholder="Número celular"
            />
          </label>

          <label class="form-field">
            <span>Correo general</span>

            <input
              v-model="form.general_email"
              type="email"
              placeholder="contacto@empresa.com"
            />
          </label>

          <label class="form-field">
            <span>Correo de facturación</span>

            <input
              v-model="form.billing_email"
              type="email"
              placeholder="facturacion@empresa.com"
            />
          </label>

          <label class="form-field full-width">
            <span>Sitio web</span>

            <input
              v-model="form.website"
              type="url"
              placeholder="https://www.empresa.com"
            />
          </label>
        </div>
      </section>

      <section class="form-section">
        <header class="section-header">
          <div>
            <h3>
              Dirección fiscal
            </h3>

            <p>
              Información fiscal y ubicación principal.
            </p>
          </div>
        </header>

        <div class="form-grid">
          <label class="form-field full-width">
            <span>Dirección fiscal completa</span>

            <input
              v-model="form.fiscal_address"
              type="text"
              placeholder="Dirección fiscal completa"
            />
          </label>

          <label class="form-field full-width">
            <span>Referencia</span>

            <input
              v-model="form.address_reference"
              type="text"
              placeholder="Referencia de ubicación"
            />
          </label>

          <label class="form-field">
            <span>Ubigeo</span>

            <input
              v-model="form.ubigeo"
              type="text"
              placeholder="Código de ubigeo"
            />
          </label>

          <label class="form-field">
            <span>Tipo de vía</span>

            <input
              v-model="form.road_type"
              type="text"
              placeholder="Avenida, calle, jirón"
            />
          </label>

          <label class="form-field">
            <span>Nombre de vía</span>

            <input
              v-model="form.road_name"
              type="text"
              placeholder="Nombre de la vía"
            />
          </label>

          <label class="form-field">
            <span>Número</span>

            <input
              v-model="form.address_number"
              type="text"
              placeholder="Número"
            />
          </label>

          <label class="form-field">
            <span>Interior</span>

            <input
              v-model="form.interior"
              type="text"
              placeholder="Interior"
            />
          </label>

          <label class="form-field">
            <span>Lote</span>

            <input
              v-model="form.lot"
              type="text"
              placeholder="Lote"
            />
          </label>

          <label class="form-field">
            <span>Departamento</span>

            <input
              v-model="form.apartment"
              type="text"
              placeholder="Departamento"
            />
          </label>

          <label class="form-field">
            <span>Manzana</span>

            <input
              v-model="form.block"
              type="text"
              placeholder="Manzana"
            />
          </label>

          <label class="form-field">
            <span>Kilómetro</span>

            <input
              v-model="form.kilometer"
              type="text"
              placeholder="Kilómetro"
            />
          </label>

          <label class="form-field">
            <span>Tipo de zona</span>

            <input
              v-model="form.zone_type"
              type="text"
              placeholder="Urbanización, sector"
            />
          </label>

          <label class="form-field">
            <span>Código de zona</span>

            <input
              v-model="form.zone_code"
              type="text"
              placeholder="Código o nombre de zona"
            />
          </label>

          <label class="form-field">
            <span>Distrito</span>

            <input
              v-model="form.district"
              type="text"
              placeholder="Distrito"
            />
          </label>

          <label class="form-field">
            <span>Provincia</span>

            <input
              v-model="form.province"
              type="text"
              placeholder="Provincia"
            />
          </label>

          <label class="form-field">
            <span>Región</span>

            <input
              v-model="form.region"
              type="text"
              placeholder="Región"
            />
          </label>

          <label class="form-field">
            <span>Código postal</span>

            <input
              v-model="form.postal_code"
              type="text"
              placeholder="Código postal"
            />
          </label>
        </div>
      </section>

      <section
        v-if="isPeruvian"
        class="form-section"
      >
        <header class="section-header">
          <div>
            <h3>
              Información SUNAT
            </h3>

            <p>
              Datos tributarios disponibles para
              registros peruanos.
            </p>
          </div>
        </header>

        <div class="form-grid">
          <label class="form-field">
            <span>Estado SUNAT</span>

            <input
              v-model="form.sunat_status"
              type="text"
              placeholder="ACTIVO"
            />
          </label>

          <label class="form-field">
            <span>Condición SUNAT</span>

            <input
              v-model="form.sunat_condition"
              type="text"
              placeholder="HABIDO"
            />
          </label>

          <label class="form-field">
            <span>Tipo de contribuyente</span>

            <input
              v-model="form.taxpayer_type"
              type="text"
              placeholder="Tipo de contribuyente"
            />
          </label>

          <label class="form-field">
            <span>Actividad económica</span>

            <input
              v-model="form.economic_activity"
              type="text"
              placeholder="Actividad económica"
            />
          </label>

          <label class="form-field">
            <span>Cantidad de trabajadores</span>

            <input
              v-model.number="form.employee_count"
              type="number"
              min="0"
              placeholder="0"
            />
          </label>

          <label class="form-field">
            <span>Tipo de facturación</span>

            <input
              v-model="form.billing_type"
              type="text"
              placeholder="Tipo de facturación"
            />
          </label>

          <label class="form-field">
            <span>Tipo de contabilidad</span>

            <input
              v-model="form.accounting_type"
              type="text"
              placeholder="Tipo de contabilidad"
            />
          </label>

          <label class="form-field">
            <span>Comercio exterior</span>

            <input
              v-model="form.foreign_trade"
              type="text"
              placeholder="Condición de comercio exterior"
            />
          </label>

          <label class="option-card compact">
            <input
              v-model="form.is_withholding_agent"
              type="checkbox"
            />

            <div>
              <strong>
                Agente de retención
              </strong>

              <span>
                Está registrado como agente
                de retención.
              </span>
            </div>
          </label>
        </div>
      </section>

      <section class="form-section">
        <header class="section-header">
          <div>
            <h3>
              Condiciones comerciales
            </h3>

            <p>
              Moneda, crédito y requisitos documentarios.
            </p>
          </div>
        </header>

        <div class="form-grid">
          <label class="form-field">
            <span>Moneda preferida</span>

            <select
              v-model="form.preferred_currency"
            >
              <option value="PEN">
                Soles
              </option>

              <option value="USD">
                Dólares estadounidenses
              </option>

              <option value="EUR">
                Euros
              </option>

              <option value="OTHER">
                Otra moneda
              </option>
            </select>
          </label>

          <label class="form-field">
            <span>Idioma preferido</span>

            <select
              v-model="form.preferred_language"
            >
              <option value="es">
                Español
              </option>

              <option value="en">
                Inglés
              </option>
            </select>
          </label>

          <label class="form-field">
            <span>Condiciones de pago</span>

            <input
              v-model="form.payment_terms"
              type="text"
              placeholder="Ejemplo: crédito a 30 días"
            />
          </label>

          <label class="form-field">
            <span>Días de crédito</span>

            <input
              v-model.number="form.credit_days"
              type="number"
              min="0"
              placeholder="0"
            />
          </label>

          <label class="form-field">
            <span>Límite de crédito</span>

            <input
              v-model="form.credit_limit"
              type="number"
              min="0"
              step="0.01"
              placeholder="0.00"
            />
          </label>
        </div>

        <div class="options-grid">
          <label class="option-card">
            <input
              v-model="form.requires_purchase_order"
              type="checkbox"
            />

            <div>
              <strong>
                Requiere orden de compra
              </strong>

              <span>
                Debe existir una orden antes de
                facturar o entregar.
              </span>
            </div>
          </label>

          <label class="option-card">
            <input
              v-model="form.requires_service_conformity"
              type="checkbox"
            />

            <div>
              <strong>
                Requiere conformidad
              </strong>

              <span>
                Solicita conformidad de servicio
                antes de facturar.
              </span>
            </div>
          </label>

          <label class="option-card">
            <input
              v-model="form.requires_delivery_guide"
              type="checkbox"
            />

            <div>
              <strong>
                Requiere guía de remisión
              </strong>

              <span>
                Solicita guía para traslados
                o entregas.
              </span>
            </div>
          </label>
        </div>
      </section>

      <section class="form-section">
        <header class="section-header">
          <div>
            <h3>
              Estado comercial
            </h3>

            <p>
              Disponibilidad del registro y posibles
              restricciones.
            </p>
          </div>
        </header>

        <div class="options-grid">
          <label class="option-card">
            <input
              v-model="form.is_active"
              type="checkbox"
            />

            <div>
              <strong>
                Registro activo
              </strong>

              <span>
                Puede utilizarse en operaciones
                comerciales.
              </span>
            </div>
          </label>

          <label class="option-card warning">
            <input
              v-model="form.is_commercially_blocked"
              type="checkbox"
            />

            <div>
              <strong>
                Bloqueo comercial
              </strong>

              <span>
                Impide nuevas operaciones hasta
                levantar la restricción.
              </span>
            </div>
          </label>
        </div>

        <div
          v-if="form.is_commercially_blocked"
          class="form-grid block-reason-grid"
        >
          <label class="form-field required full-width">
            <span>Motivo del bloqueo</span>

            <textarea
              v-model="form.commercial_block_reason"
              rows="3"
              placeholder="Indica el motivo del bloqueo comercial"
              required
            ></textarea>
          </label>
        </div>

        <div class="form-grid notes-grid">
          <label class="form-field full-width">
            <span>Observaciones internas</span>

            <textarea
              v-model="form.notes"
              rows="4"
              placeholder="Observaciones comerciales o administrativas"
            ></textarea>
          </label>
        </div>
      </section>

      <PartnerRelationsSection
        v-if="isEditing"
        :partner-id="String(route.params.id)"
        :users="users"
      />

      <section
        v-else
        class="relations-pending-card"
      >
        <span class="relations-pending-icon">
          ◎
        </span>

        <div>
          <strong>
            Sucursales y contactos
          </strong>

          <p>
            Guarda primero el cliente o proveedor.
            Después podrás registrar sus sucursales,
            sedes y personas de contacto.
          </p>
        </div>
      </section>

      <footer class="form-actions">
        <button
          class="secondary-button"
          type="button"
          :disabled="saving"
          @click="cancel"
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
              : isEditing
                ? "Guardar cambios"
                : "Crear registro"
          }}
        </button>
      </footer>
    </form>
  </section>
</template>

<style scoped>
button,
input,
select,
textarea {
  font: inherit;
}

.partner-form-page {
  --brand-blue: #1f35c4;
  --brand-blue-dark: #162caa;
  --brand-blue-soft: #4e63d8;
  --brand-blue-light: #edf0ff;
  --brand-gray: #8693a4;
  --brand-gray-dark: #667382;
  --text-primary: #1d2940;
  --border-color: #dfe3ec;

  display: flex;
  animation: pageReveal 0.42s ease-out;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.page-kicker {
  display: block;
  margin-bottom: 6px;
  color: #1f35c4;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.page-header h2 {
  margin: 0;
  color: #1d2940;
  font-size: 28px;
}

.page-header p {
  margin: 8px 0 0;
  color: #667382;
  font-size: 14px;
}

.back-button {
  min-height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 15px;
  border: 1px solid #dfe3ec;
  border-radius: 10px;
  background: white;
  color: #667382;
  cursor: pointer;
}

.back-button:hover {
  transform: translateY(-2px);
  border-color: #cfd5f7;
  background: #edf0ff;
  color: #1f35c4;
  box-shadow: 0 8px 18px rgba(31, 53, 196, 0.10);
}

.back-button svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.message {
  padding: 12px 14px;
  animation: messageReveal 0.25s ease-out;
  border-radius: 10px;
  font-size: 13px;
}

.error-message {
  border: 1px solid #e8caca;
  background: #fff3f3;
  color: #9a4141;
}

.loading-card {
  min-height: 220px;
  display: flex;
  animation: cardReveal 0.35s ease-out;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: 1px solid #dfe3ec;
  border-radius: 15px;
  background: white;
  color: #667382;
}

.spinner,
.button-spinner {
  display: inline-block;
  border-radius: 50%;
  animation: rotate 0.8s linear infinite;
}

.spinner {
  width: 21px;
  height: 21px;
  border: 3px solid #d9deea;
  border-top-color: #1f35c4;
}

.button-spinner {
  width: 15px;
  height: 15px;
  border: 2px solid rgba(255, 255, 255, 0.45);
  border-top-color: white;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-section {
  overflow: hidden;
  animation: sectionReveal 0.45s ease-out both;
  transition:
    transform 0.22s ease,
    box-shadow 0.22s ease,
    border-color 0.22s ease;
  border: 1px solid #dfe3ec;
  border-radius: 15px;
  background: white;
}

.form-section:hover {
  transform: translateY(-2px);
  border-color: #cfd5f7;
  box-shadow: 0 14px 28px rgba(31, 53, 196, 0.07);
}

.section-header {
  padding: 18px 20px;
  border-bottom: 1px solid #e8ebf1;
  background: #f8f9fd;
}

.section-header h3 {
  margin: 0;
  color: #1d2940;
  font-size: 16px;
}

.section-header p {
  margin: 5px 0 0;
  color: #8693a4;
  font-size: 12px;
}

.form-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 17px;
  padding: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.form-field.full-width {
  grid-column: 1 / -1;
}

.form-field > span {
  color: #667382;
  font-size: 12px;
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
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease,
    background 0.2s ease;
  border: 1px solid #dfe3ec;
  border-radius: 9px;
  outline: none;
  background: white;
  color: #1d2940;
}

.form-field input,
.form-field select {
  min-height: 43px;
  padding: 0 12px;
}

.form-field textarea {
  min-height: 96px;
  resize: vertical;
  padding: 11px 12px;
  line-height: 1.5;
}

.form-field input:focus,
.form-field select:focus,
.form-field textarea:focus {
  transform: translateY(-1px);
  border-color: #4e63d8;
  box-shadow:
    0 0 0 3px rgba(31, 53, 196, 0.12);
}

.form-field input::placeholder,
.form-field textarea::placeholder {
  color: #9aa4b2;
}

.options-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 12px;
  padding: 20px;
}

.roles-grid {
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
}

.option-card {
  display: flex;
  position: relative;
  overflow: hidden;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease;
  align-items: flex-start;
  gap: 11px;
  padding: 15px;
  border: 1px solid #dfe3ec;
  border-radius: 11px;
  background: #f8f9fd;
  cursor: pointer;
}

.option-card.compact {
  align-self: end;
  min-height: 43px;
  box-sizing: border-box;
}

.option-card:hover {
  transform: translateY(-2px);
  border-color: #cfd5f7;
  background: #f4f6ff;
  box-shadow: 0 10px 20px rgba(31, 53, 196, 0.07);
}

.option-card:has(input:checked) {
  border-color: #bfc7f4;
  background: linear-gradient(135deg, #edf0ff, #f8f9ff);
  box-shadow: inset 3px 0 0 #1f35c4;
}

.option-card.warning:has(input:checked) {
  border-color: #efc7bd;
  background: #fff5f2;
  box-shadow: inset 3px 0 0 #b85c45;
}

.option-card input {
  width: 17px;
  height: 17px;
  flex-shrink: 0;
  margin-top: 2px;
  accent-color: #1f35c4;
}

.option-card.warning input {
  accent-color: #b85c45;
}

.option-card strong,
.option-card span {
  display: block;
}

.option-card strong {
  color: #1d2940;
  font-size: 13px;
}

.option-card span {
  margin-top: 4px;
  color: #8693a4;
  font-size: 11px;
  line-height: 1.45;
}

.block-reason-grid {
  padding-top: 0;
}

.notes-grid {
  padding-top: 0;
}

.relations-pending-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  border: 1px dashed #cfd5f7;
  border-radius: 15px;
  background: linear-gradient(
    135deg,
    #f8f9ff,
    #ffffff
  );
}

.relations-pending-icon {
  width: 44px;
  height: 44px;
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: #edf0ff;
  color: #1f35c4;
  font-size: 23px;
  font-weight: 800;
}

.relations-pending-card strong,
.relations-pending-card p {
  display: block;
}

.relations-pending-card strong {
  color: #1d2940;
  font-size: 14px;
}

.relations-pending-card p {
  margin: 5px 0 0;
  color: #8693a4;
  font-size: 12px;
  line-height: 1.5;
}

.form-actions {
  position: sticky;
  z-index: 8;
  bottom: 14px;
  display: flex;
  animation: actionsReveal 0.45s ease-out;
  justify-content: flex-end;
  gap: 10px;
  padding: 17px 20px;
  border: 1px solid #dfe3ec;
  border-radius: 15px;
  background: white;
  box-shadow:
    0 10px 30px rgba(31, 50, 73, 0.08);
}

.secondary-button,
.primary-button {
  min-height: 43px;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    background 0.2s ease,
    border-color 0.2s ease;
  padding: 0 18px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}

.secondary-button {
  border: 1px solid #dfe3ec;
  background: white;
  color: #667382;
}

.primary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 0;
  background: linear-gradient(
    135deg,
    #162caa,
    #1f35c4 55%,
    #4e63d8
  );
  color: white;
  box-shadow: 0 10px 22px rgba(31, 53, 196, 0.20);
}

.secondary-button:hover {
  transform: translateY(-2px);
  border-color: #cfd5f7;
  background: #edf0ff;
  color: #1f35c4;
}

.primary-button:hover {
  transform: translateY(-2px);
  background: linear-gradient(
    135deg,
    #132596,
    #1f35c4 50%,
    #4358d0
  );
  box-shadow: 0 14px 28px rgba(31, 53, 196, 0.28);
}

.secondary-button:disabled,
.primary-button:disabled {
  opacity: 0.6;
  cursor: wait;
}

@keyframes rotate {
  to {
    transform: rotate(360deg);
  }
}

@keyframes pageReveal {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes sectionReveal {
  from {
    opacity: 0;
    transform: translateY(14px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes cardReveal {
  from {
    opacity: 0;
    transform: scale(0.985);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes messageReveal {
  from {
    opacity: 0;
    transform: translateY(-6px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes actionsReveal {
  from {
    opacity: 0;
    transform: translateY(12px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

@media (max-width: 1050px) {
  .roles-grid {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .page-header {
    flex-direction: column;
  }

  .form-grid,
  .options-grid,
  .roles-grid {
    grid-template-columns: 1fr;
  }

  .form-field.full-width {
    grid-column: auto;
  }
}

@media (max-width: 520px) {
  .form-actions {
    flex-direction: column-reverse;
  }

  .secondary-button,
  .primary-button {
    width: 100%;
  }
}
</style>