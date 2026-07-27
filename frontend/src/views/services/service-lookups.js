import {
  getUsers,
} from "../../services/users.service"


export const SERVICE_ORIGIN_OPTIONS = [
  {
    value: "rental",
    label: "Alquiler Andes",
    description: (
      "Máquina de la flota de alquiler "
      + "con asignación vigente."
    ),
  },
  {
    value: "external",
    label: "Equipo externo",
    description: (
      "Máquina de un cliente atendida "
      + "mediante servicio técnico."
    ),
  },
]


export const SERVICE_TYPE_OPTIONS = [
  {
    value: "corrective",
    label: "Correctivo",
  },
  {
    value: "preventive",
    label: "Preventivo",
  },
  {
    value: "network",
    label: "Red y configuración",
  },
  {
    value: "meter_reading",
    label: "Lectura de contadores",
  },
  {
    value: "inspection",
    label: "Inspección",
  },
  {
    value: "other",
    label: "Otro",
  },
]


export const SERVICE_PRIORITY_OPTIONS = [
  {
    value: "low",
    label: "Baja",
  },
  {
    value: "normal",
    label: "Normal",
  },
  {
    value: "high",
    label: "Alta",
  },
  {
    value: "urgent",
    label: "Urgente",
  },
]


export const SERVICE_STATUS_OPTIONS = [
  {
    value: "draft",
    label: "Borrador",
  },
  {
    value: "pending_assignment",
    label: "Pendiente de asignación",
  },
  {
    value: "assigned",
    label: "Asignada",
  },
  {
    value: "accepted",
    label: "Aceptada por técnico",
  },
  {
    value: "en_route",
    label: "Técnico en ruta",
  },
  {
    value: "on_site",
    label: "Técnico en ubicación",
  },
  {
    value: "in_progress",
    label: "En proceso",
  },
  {
    value: "pending_parts",
    label: "Pendiente de repuestos",
  },
  {
    value: "requires_return",
    label: "Requiere nueva visita",
  },
  {
    value: "technician_completed",
    label: "Finalizada por técnico",
  },
  {
    value: "pending_conformity",
    label: "Pendiente de conformidad",
  },
  {
    value: "closed",
    label: "Cerrada",
  },
  {
    value: "rescheduled",
    label: "Reprogramada",
  },
  {
    value: "failed_visit",
    label: "Visita no realizada",
  },
  {
    value: "cancelled",
    label: "Cancelada",
  },
]


export const SERVICE_RESULT_OPTIONS = [
  {
    value: "pending",
    label: "Pendiente",
  },
  {
    value: "operational",
    label: "Operativa",
  },
  {
    value: "operational_with_notes",
    label: "Operativa con observaciones",
  },
  {
    value: "pending_parts",
    label: "Pendiente de repuestos",
  },
  {
    value: "requires_return",
    label: "Requiere nueva visita",
  },
  {
    value: "not_repaired",
    label: "No reparada",
  },
  {
    value: "not_attended",
    label: "No atendida",
  },
]


export const EMPTY_SERVICE_SNAPSHOT = {
  customer_code: "",
  customer_document_type: "",
  customer_document_number: "",
  customer_name: "",
  customer_trade_name: "",
  branch_name: "",
  address: "",
  address_reference: "",
  district: "",
  province: "",
  region: "",
  destination_latitude: null,
  destination_longitude: null,
  site_location: "",
  contact_name: "",
  contact_job_title: "",
  contact_phone: "",
  contact_email: "",
  contract_reference: "",
  rental_assignment_reference: "",
}


export function createEmptySnapshot() {
  return {
    ...EMPTY_SERVICE_SNAPSHOT,
  }
}


export function createEmptyServiceOrderForm() {
  return {
    code: "",
    service_origin: "rental",
    equipment: "",
    assigned_technician: "",
    status: "pending_assignment",
    priority: "normal",
    service_type: "corrective",
    result: "pending",
    requested_at: toLocalDateTimeInput(
      new Date(),
    ),
    scheduled_at: "",
    reported_problem: "",
    diagnosis: "",
    work_performed: "",
    technician_observations: "",
    closure_observations: "",
    requires_return_visit: false,
    cancellation_reason: "",
    failed_visit_reason: "",
    ...createEmptySnapshot(),
  }
}


export function normalizeCollection(payload) {
  if (Array.isArray(payload)) {
    return payload
  }

  if (Array.isArray(payload?.results)) {
    return payload.results
  }

  return []
}


export function normalizeEquipmentOptions(payload) {
  return normalizeCollection(payload).map(
    normalizeEquipmentOption,
  )
}


export function normalizeEquipmentOption(option) {
  const snapshot = {
    ...createEmptySnapshot(),
    ...(option?.snapshot || {}),
  }

  const serialNumber = cleanText(
    option?.serial_number,
  )

  const internalCode = cleanText(
    option?.internal_code,
  )

  const brandName = cleanText(
    option?.brand_name,
  )

  const modelName = cleanText(
    option?.model_name,
  )

  const customerName = cleanText(
    snapshot.customer_name
    || option?.owner_customer_name,
  )

  const branchName = cleanText(
    snapshot.branch_name,
  )

  const label = (
    cleanText(option?.label)
    || buildEquipmentLabel({
      serialNumber,
      internalCode,
      brandName,
      modelName,
      customerName,
      branchName,
    })
  )

  return {
    ...option,
    id: option?.id || option?.equipment || "",
    equipment: option?.equipment || option?.id || "",
    serial_number: serialNumber,
    internal_code: internalCode,
    brand_name: brandName,
    model_name: modelName,
    family_name: cleanText(
      option?.family_name,
    ),
    service_origin: cleanText(
      option?.service_origin,
    ),
    service_origin_display: cleanText(
      option?.service_origin_display,
    ),
    label,
    snapshot,
  }
}


export function buildEquipmentLabel({
  serialNumber = "",
  internalCode = "",
  brandName = "",
  modelName = "",
  customerName = "",
  branchName = "",
} = {}) {
  const identifier = (
    cleanText(serialNumber)
    || cleanText(internalCode)
    || "Equipo sin identificación"
  )

  const brandModel = [
    cleanText(brandName),
    cleanText(modelName),
  ]
    .filter(Boolean)
    .join(" ")

  return [
    identifier,
    brandModel,
    cleanText(customerName),
    cleanText(branchName),
  ]
    .filter(Boolean)
    .join(" · ")
}


export function applyEquipmentSnapshot(
  form,
  option,
) {
  if (!form || !option) {
    return form
  }

  const normalizedOption = (
    normalizeEquipmentOption(option)
  )

  form.equipment = (
    normalizedOption.equipment
  )

  Object.entries(
    normalizedOption.snapshot,
  ).forEach(
    ([fieldName, value]) => {
      form[fieldName] = value ?? ""
    },
  )

  return form
}


export function clearEquipmentSelection(form) {
  if (!form) {
    return form
  }

  form.equipment = ""

  Object.keys(
    EMPTY_SERVICE_SNAPSHOT,
  ).forEach(
    (fieldName) => {
      form[fieldName] = (
        EMPTY_SERVICE_SNAPSHOT[fieldName]
      )
    },
  )

  return form
}


export function buildServiceOrderPayload(form) {
  return {
    service_origin: form.service_origin,
    equipment: form.equipment,

    assigned_technician: (
      form.assigned_technician
      || null
    ),

    status: form.status,
    priority: form.priority,
    service_type: form.service_type,
    result: form.result,

    requested_at: (
      toApiDateTime(
        form.requested_at,
      )
    ),

    scheduled_at: (
      form.scheduled_at
        ? toApiDateTime(
            form.scheduled_at,
          )
        : null
    ),

    reported_problem: cleanText(
      form.reported_problem,
    ),

    diagnosis: cleanText(
      form.diagnosis,
    ),

    work_performed: cleanText(
      form.work_performed,
    ),

    technician_observations: cleanText(
      form.technician_observations,
    ),

    closure_observations: cleanText(
      form.closure_observations,
    ),

    requires_return_visit: Boolean(
      form.requires_return_visit,
    ),

    cancellation_reason: cleanText(
      form.cancellation_reason,
    ),

    failed_visit_reason: cleanText(
      form.failed_visit_reason,
    ),

    customer_code: cleanText(
      form.customer_code,
    ),

    customer_document_type: cleanText(
      form.customer_document_type,
    ),

    customer_document_number: cleanText(
      form.customer_document_number,
    ),

    customer_name: cleanText(
      form.customer_name,
    ),

    customer_trade_name: cleanText(
      form.customer_trade_name,
    ),

    branch_name: cleanText(
      form.branch_name,
    ),

    address: cleanText(
      form.address,
    ),

    address_reference: cleanText(
      form.address_reference,
    ),

    district: cleanText(
      form.district,
    ),

    province: cleanText(
      form.province,
    ),

    region: cleanText(
      form.region,
    ),

    destination_latitude: (
      normalizeNullableNumber(
        form.destination_latitude,
      )
    ),

    destination_longitude: (
      normalizeNullableNumber(
        form.destination_longitude,
      )
    ),

    site_location: cleanText(
      form.site_location,
    ),

    contact_name: cleanText(
      form.contact_name,
    ),

    contact_job_title: cleanText(
      form.contact_job_title,
    ),

    contact_phone: cleanText(
      form.contact_phone,
    ),

    contact_email: cleanText(
      form.contact_email,
    ),
  }
}


export function hydrateServiceOrderForm(order) {
  const form = (
    createEmptyServiceOrderForm()
  )

  if (!order) {
    return form
  }

  Object.keys(form).forEach(
    (fieldName) => {
      if (
        Object.prototype.hasOwnProperty.call(
          order,
          fieldName,
        )
      ) {
        form[fieldName] = (
          order[fieldName]
          ?? form[fieldName]
        )
      }
    },
  )

  form.equipment = (
    order.equipment || ""
  )

  form.assigned_technician = (
    order.assigned_technician || ""
  )

  form.requested_at = (
    toLocalDateTimeInput(
      order.requested_at,
    )
  )

  form.scheduled_at = (
    order.scheduled_at
      ? toLocalDateTimeInput(
          order.scheduled_at,
        )
      : ""
  )

  form.requires_return_visit = Boolean(
    order.requires_return_visit,
  )

  return form
}


export async function searchTechnicians(
  search = "",
) {
  const response = await getUsers({
    search,
    isActive: true,
  })

  return normalizeCollection(response)
    .filter(
      (user) => (
        user.is_active !== false
      ),
    )
    .map(
      (user) => {
        const fullName = (
          user.full_name
          || [
            user.first_name,
            user.last_name,
          ]
            .filter(Boolean)
            .join(" ")
          || user.username
          || user.email
          || "Usuario"
        )

        return {
          ...user,
          id: user.id,
          value: user.id,
          label: fullName,
          subtitle: (
            user.email
            || user.username
            || ""
          ),
          meta: (
            user.job_title
            || user.position
            || "Técnico"
          ),
        }
      },
    )
}


export function getServiceOriginLabel(value) {
  return (
    SERVICE_ORIGIN_OPTIONS.find(
      (option) => (
        option.value === value
      ),
    )?.label
    || value
    || ""
  )
}


export function getServiceTypeLabel(value) {
  return (
    SERVICE_TYPE_OPTIONS.find(
      (option) => (
        option.value === value
      ),
    )?.label
    || value
    || ""
  )
}


export function getServicePriorityLabel(value) {
  return (
    SERVICE_PRIORITY_OPTIONS.find(
      (option) => (
        option.value === value
      ),
    )?.label
    || value
    || ""
  )
}


export function getServiceStatusLabel(value) {
  return (
    SERVICE_STATUS_OPTIONS.find(
      (option) => (
        option.value === value
      ),
    )?.label
    || value
    || ""
  )
}


export function getServiceResultLabel(value) {
  return (
    SERVICE_RESULT_OPTIONS.find(
      (option) => (
        option.value === value
      ),
    )?.label
    || value
    || ""
  )
}


export function cleanText(value) {
  return String(
    value ?? "",
  ).trim()
}


export function normalizeNullableNumber(value) {
  if (
    value === ""
    || value === null
    || value === undefined
  ) {
    return null
  }

  const number = Number(value)

  return Number.isFinite(number)
    ? number
    : null
}


export function toLocalDateTimeInput(value) {
  if (!value) {
    return ""
  }

  const date = (
    value instanceof Date
      ? value
      : new Date(value)
  )

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return ""
  }

  const year = date.getFullYear()

  const month = String(
    date.getMonth() + 1,
  ).padStart(
    2,
    "0",
  )

  const day = String(
    date.getDate(),
  ).padStart(
    2,
    "0",
  )

  const hours = String(
    date.getHours(),
  ).padStart(
    2,
    "0",
  )

  const minutes = String(
    date.getMinutes(),
  ).padStart(
    2,
    "0",
  )

  return (
    `${year}-${month}-${day}`
    + `T${hours}:${minutes}`
  )
}


export function toApiDateTime(value) {
  if (!value) {
    return null
  }

  const date = new Date(value)

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return value
  }

  return date.toISOString()
}