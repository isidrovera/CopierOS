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
  applyServiceMeterReading,
  assignServiceTechnician,
  createServiceMeterReading,
  changeServiceOrderStatus,
  generateServiceChecklist,
  getCompatibleServiceSubparts,
  getServiceAssignmentHistory,
  getServiceChecklistItems,
  getServiceChecklists,
  getServiceEvidences,
  getServiceMeterReadings,
  getServiceOrder,
  getServicePartRequestItems,
  getServicePartRequests,
  getServiceStatusHistory,
  getServiceTrackingPoints,
  loadCurrentServiceSnapshot,
  saveServiceChecklistItem,
  updateServiceMeterReading,
  updateServicePartRequest,
  uploadServiceEvidence,
} from "../../services/services.service"

import ServiceSearchSelect from "./ServiceSearchSelect.vue"

import {
  searchTechnicians,
} from "./service-lookups"

import "./services-detail.css"


const route = useRoute()
const router = useRouter()

const order = ref(null)
const loading = ref(false)
const actionLoading = ref(false)
const error = ref("")
const success = ref("")
const activeTab = ref("summary")

const technicianId = ref("")
const technicianOption = ref(null)

const checklist = ref(null)
const checklistItems = ref([])
const checklistForms = reactive({})
const compatibleSubparts = reactive({})
const compatibleSubpartsLoading = reactive({})
const checklistSaving = reactive({})

const evidences = ref([])
const evidenceFiles = ref([])
const evidenceFileInput = ref(null)
const evidenceUploading = ref(false)

const evidenceForm = reactive({
  stage: "before",
  notes: "",
})

const meterReading = ref(null)
const meterSaving = ref(false)

const meterForm = reactive({
  initial_total_meter: "",
  initial_black_meter: "",
  initial_color_meter: "",
  initial_scan_meter: "",
  final_total_meter: "",
  final_black_meter: "",
  final_color_meter: "",
  final_scan_meter: "",
  initial_unavailable_reason: "",
  final_unavailable_reason: "",
})

const partRequests = ref([])
const partItems = ref([])
const partRequestSaving = ref(false)
const partRequestNotes = ref("")
const statusHistory = ref([])
const assignmentHistory = ref([])
const trackingPoints = ref([])


const tabs = [
  [
    "summary",
    "Resumen",
  ],
  [
    "checklist",
    "Checklist",
  ],
  [
    "parts",
    "Repuestos",
  ],
  [
    "evidence",
    "Evidencias",
  ],
  [
    "meters",
    "Contadores",
  ],
  [
    "tracking",
    "Tracking",
  ],
  [
    "history",
    "Historial",
  ],
]


const checklistStatusOptions = [
  {
    value: "pending",
    label: "Pendiente",
  },
  {
    value: "ok",
    label: "Correcto",
  },
  {
    value: "observed",
    label: "Regular / observado",
  },
  {
    value: "failed",
    label: "Requiere cambio",
  },
  {
    value: "not_applicable",
    label: "No aplica",
  },
]


const urgencyOptions = [
  {
    value: "normal",
    label: "Normal",
  },
  {
    value: "high",
    label: "Alta",
  },
  {
    value: "critical",
    label: "Crítica",
  },
]


const evidenceStageOptions = [
  {
    value: "before",
    label: "Antes del servicio",
  },
  {
    value: "after",
    label: "Después del servicio",
  },
  {
    value: "meter",
    label: "Contadores",
  },
  {
    value: "part",
    label: "Repuestos",
  },
  {
    value: "general",
    label: "Evidencia general",
  },
]


const nextActions = computed(
  () => {
    const map = {
      draft: [
        [
          "pending_assignment",
          "Enviar a asignación",
        ],
      ],

      pending_assignment: [
        [
          "assigned",
          "Marcar asignada",
        ],
      ],

      assigned: [
        [
          "accepted",
          "Aceptar orden",
        ],
      ],

      accepted: [
        [
          "en_route",
          "Iniciar ruta",
        ],
      ],

      en_route: [
        [
          "on_site",
          "Marcar llegada",
        ],
      ],

      on_site: [
        [
          "in_progress",
          "Iniciar servicio",
        ],
      ],

      in_progress: [
        [
          "pending_parts",
          "Pendiente de repuestos",
        ],
        [
          "requires_return",
          "Requiere retorno",
        ],
        [
          "technician_completed",
          "Finalizar atención",
        ],
      ],

      pending_parts: [
        [
          "requires_return",
          "Programar retorno",
        ],
        [
          "technician_completed",
          "Finalizar atención",
        ],
      ],

      technician_completed: [
        [
          "pending_conformity",
          "Solicitar conformidad",
        ],
        [
          "closed",
          "Cerrar orden",
        ],
      ],

      pending_conformity: [
        [
          "closed",
          "Cerrar orden",
        ],
      ],

      rescheduled: [
        [
          "assigned",
          "Reasignar",
        ],
      ],
    }

    return (
      map[
        order.value?.status
      ]
      || []
    )
  },
)


const checklistProgress = computed(
  () => {
    const total = (
      checklistItems.value.length
    )

    const reviewed = (
      checklistItems.value.filter(
        (item) => (
          item.status !== "pending"
        ),
      ).length
    )

    const failed = (
      checklistItems.value.filter(
        (item) => (
          item.status === "failed"
        ),
      ).length
    )

    return {
      total,
      reviewed,
      pending: total - reviewed,
      failed,
      percent: (
        total
          ? Math.round(
              (
                reviewed
                / total
              )
              * 100,
            )
          : 0
      ),
    }
  },
)


const selectedEvidenceNames = computed(
  () => (
    evidenceFiles.value
      .map(
        (file) => file.name,
      )
      .join(", ")
  ),
)


const activePartRequest = computed(
  () => (
    partRequests.value[0]
    || null
  ),
)


const showTotalMeter = computed(
  () => Boolean(
    order.value?.equipment_has_total_meter,
  ),
)


const showBlackMeter = computed(
  () => Boolean(
    order.value?.equipment_has_black_meter,
  ),
)


const showColorMeter = computed(
  () => Boolean(
    order.value?.equipment_has_color_meter,
  ),
)


const showScanMeter = computed(
  () => Boolean(
    order.value?.equipment_has_scan_meter,
  ),
)


function normalize(data) {
  if (
    Array.isArray(data)
  ) {
    return data
  }

  if (
    Array.isArray(
      data?.results,
    )
  ) {
    return data.results
  }

  return []
}


function cleanText(value) {
  return String(
    value ?? "",
  ).trim()
}


function formatDate(value) {
  if (!value) {
    return "—"
  }

  const date = new Date(value)

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return "—"
  }

  return new Intl.DateTimeFormat(
    "es-PE",
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  ).format(date)
}


function formatQuantity(value) {
  const quantity = Number(value)

  if (
    !Number.isFinite(quantity)
  ) {
    return value || "—"
  }

  return new Intl.NumberFormat(
    "es-PE",
    {
      maximumFractionDigits: 2,
    },
  ).format(quantity)
}


function getStatusLabel(value) {
  return (
    checklistStatusOptions.find(
      (option) => (
        option.value === value
      ),
    )?.label
    || value
    || "Pendiente"
  )
}


function getUrgencyLabel(value) {
  return (
    urgencyOptions.find(
      (option) => (
        option.value === value
      ),
    )?.label
    || value
    || "Normal"
  )
}


function getChecklistStatusClass(statusValue) {
  return {
    pending: (
      "checklist-status-pending"
    ),
    ok: (
      "checklist-status-ok"
    ),
    observed: (
      "checklist-status-observed"
    ),
    failed: (
      "checklist-status-failed"
    ),
    not_applicable: (
      "checklist-status-not-applicable"
    ),
  }[statusValue] || (
    "checklist-status-pending"
  )
}


function isConsumableItem(item) {
  const category = cleanText(
    item?.category,
  ).toLowerCase()

  const typeName = cleanText(
    item?.component_type_name,
  ).toLowerCase()

  return (
    category.includes(
      "consum",
    )
    || category.includes(
      "toner",
    )
    || category.includes(
      "tóner",
    )
    || typeName.includes(
      "consum",
    )
    || typeName.includes(
      "toner",
    )
    || typeName.includes(
      "tóner",
    )
  )
}


function createChecklistForm(item) {
  return {
    status: (
      item.status
      || "pending"
    ),

    observation: (
      item.observation
      || ""
    ),

    consumable_present: (
      item.consumable_present
      ?? true
    ),

    consumable_level_percent: (
      item.consumable_level_percent
      ?? 100
    ),
  }
}


function initializeChecklistForms() {
  const activeIds = new Set(
    checklistItems.value.map(
      (item) => String(
        item.id,
      ),
    ),
  )

  Object.keys(
    checklistForms,
  ).forEach(
    (id) => {
      if (
        !activeIds.has(
          String(id),
        )
      ) {
        delete checklistForms[id]
        delete compatibleSubparts[id]
        delete compatibleSubpartsLoading[id]
        delete checklistSaving[id]
      }
    },
  )

  checklistItems.value.forEach(
    (item) => {
      checklistForms[item.id] = (
        createChecklistForm(
          item,
        )
      )
    },
  )
}


function normalizeCompatibleSubpart(
  item,
) {
  return {
    ...item,

    selected: Boolean(
      item.selected,
    ),

    quantity: (
      item.quantity
      ?? "1.00"
    ),

    urgency: (
      item.urgency
      || "normal"
    ),

    reason: (
      item.reason
      || ""
    ),

    notes: (
      item.notes
      || ""
    ),
  }
}


async function loadCompatibleSubparts(
  itemId,
  {
    force = false,
  } = {},
) {
  if (
    !itemId
    || compatibleSubpartsLoading[
      itemId
    ]
  ) {
    return
  }

  if (
    !force
    && Array.isArray(
      compatibleSubparts[
        itemId
      ],
    )
  ) {
    return
  }

  compatibleSubpartsLoading[
    itemId
  ] = true

  try {
    const response = (
      await getCompatibleServiceSubparts(
        itemId,
      )
    )

    compatibleSubparts[
      itemId
    ] = normalize(
      response,
    ).map(
      normalizeCompatibleSubpart,
    )
  } catch (requestError) {
    error.value = (
      requestError.message
    )
  } finally {
    compatibleSubpartsLoading[
      itemId
    ] = false
  }
}


async function loadFailedSubparts() {
  const failedItems = (
    checklistItems.value.filter(
      (item) => (
        item.status === "failed"
      ),
    )
  )

  await Promise.all(
    failedItems.map(
      (item) => (
        loadCompatibleSubparts(
          item.id,
          {
            force: true,
          },
        )
      ),
    ),
  )
}


async function handleChecklistStatusChange(
  item,
) {
  const form = (
    checklistForms[
      item.id
    ]
  )

  if (!form) {
    return
  }

  error.value = ""
  success.value = ""

  if (
    form.status === "failed"
  ) {
    await loadCompatibleSubparts(
      item.id,
    )

    const rows = (
      compatibleSubparts[
        item.id
      ]
      || []
    )

    rows.forEach(
      (subpart) => {
        if (
          !cleanText(
            subpart.reason,
          )
        ) {
          subpart.reason = (
            form.observation
          )
        }
      },
    )
  }
}


function toggleSubpart(
  itemId,
  subpart,
) {
  subpart.selected = (
    !subpart.selected
  )

  if (
    subpart.selected
    && !cleanText(
      subpart.reason,
    )
  ) {
    subpart.reason = (
      checklistForms[
        itemId
      ]?.observation
      || ""
    )
  }
}


function selectedSubparts(
  itemId,
) {
  return (
    compatibleSubparts[
      itemId
    ]
    || []
  ).filter(
    (subpart) => (
      subpart.selected
    ),
  )
}


function validateChecklistItem(
  item,
) {
  const form = (
    checklistForms[
      item.id
    ]
  )

  if (!form) {
    return (
      "No se encontró el formulario del checklist."
    )
  }

  if (!form.status) {
    return (
      "Seleccione el resultado del componente."
    )
  }

  if (
    form.status === "failed"
    && !cleanText(
      form.observation,
    )
  ) {
    return (
      "Debe describir la falla del componente."
    )
  }

  if (
    form.status === "failed"
  ) {
    const rows = (
      selectedSubparts(
        item.id,
      )
    )

    if (!rows.length) {
      return (
        "Seleccione al menos una subparte."
      )
    }

    for (
      const subpart
      of rows
    ) {
      const quantity = Number(
        subpart.quantity,
      )

      if (
        !Number.isFinite(
          quantity,
        )
        || quantity <= 0
      ) {
        return (
          `La cantidad de ${subpart.name} `
          + "debe ser mayor que cero."
        )
      }

      if (
        !cleanText(
          subpart.reason,
        )
      ) {
        return (
          `Indique el motivo para ${subpart.name}.`
        )
      }
    }
  }

  return ""
}


async function saveChecklistItem(
  item,
) {
  const validationMessage = (
    validateChecklistItem(
      item,
    )
  )

  if (validationMessage) {
    error.value = (
      validationMessage
    )

    return
  }

  const form = (
    checklistForms[
      item.id
    ]
  )

  checklistSaving[
    item.id
  ] = true

  error.value = ""
  success.value = ""

  try {
    const subparts = (
      form.status === "failed"
        ? selectedSubparts(
            item.id,
          ).map(
            (subpart) => ({
              component: (
                subpart.component
                || subpart.id
              ),

              quantity: (
                subpart.quantity
              ),

              urgency: (
                subpart.urgency
                || "normal"
              ),

              reason: (
                cleanText(
                  subpart.reason,
                )
                || cleanText(
                  form.observation,
                )
              ),

              notes: cleanText(
                subpart.notes,
              ),
            }),
          )
        : []
    )

    await saveServiceChecklistItem({
      id: item.id,
      status: form.status,
      observation: (
        cleanText(
          form.observation,
        )
      ),
      consumablePresent: (
        isConsumableItem(item)
          ? Boolean(
              form.consumable_present,
            )
          : (
              item.consumable_present
              ?? null
            )
      ),
      consumableLevelPercent: (
        isConsumableItem(item)
          ? Number(
              form.consumable_level_percent,
            )
          : (
              item.consumable_level_percent
              ?? null
            )
      ),
      subparts,
    })

    success.value = (
      form.status === "failed"
        ? (
            "Checklist y repuestos "
            + "actualizados correctamente."
          )
        : (
            "Resultado actualizado. "
            + "Las subpartes que ya no aplican "
            + "fueron retiradas."
          )
    )

    await reloadChecklistAndParts()

    if (
      form.status === "failed"
    ) {
      await loadCompatibleSubparts(
        item.id,
        {
          force: true,
        },
      )
    }
  } catch (requestError) {
    error.value = (
      requestError.message
    )
  } finally {
    checklistSaving[
      item.id
    ] = false
  }
}



function meterInputValue(value) {
  return (
    value === null
    || value === undefined
      ? ""
      : value
  )
}


function initializeMeterForm(reading = null) {
  const source = reading || {}

  meterForm.initial_total_meter = meterInputValue(
    source.initial_total_meter,
  )

  meterForm.initial_black_meter = meterInputValue(
    source.initial_black_meter,
  )

  meterForm.initial_color_meter = meterInputValue(
    source.initial_color_meter,
  )

  meterForm.initial_scan_meter = meterInputValue(
    source.initial_scan_meter,
  )

  meterForm.final_total_meter = meterInputValue(
    source.final_total_meter,
  )

  meterForm.final_black_meter = meterInputValue(
    source.final_black_meter,
  )

  meterForm.final_color_meter = meterInputValue(
    source.final_color_meter,
  )

  meterForm.final_scan_meter = meterInputValue(
    source.final_scan_meter,
  )

  meterForm.initial_unavailable_reason = (
    source.initial_unavailable_reason
    || ""
  )

  meterForm.final_unavailable_reason = (
    source.final_unavailable_reason
    || ""
  )
}


function normalizeMeterValue(value) {
  if (
    value === ""
    || value === null
    || value === undefined
  ) {
    return null
  }

  const number = Number(value)

  return Number.isFinite(number)
    ? Math.trunc(number)
    : null
}


function validateMeterForm() {
  const initialValues = [
    showTotalMeter.value
      ? normalizeMeterValue(
          meterForm.initial_total_meter,
        )
      : null,

    showBlackMeter.value
      ? normalizeMeterValue(
          meterForm.initial_black_meter,
        )
      : null,

    showColorMeter.value
      ? normalizeMeterValue(
          meterForm.initial_color_meter,
        )
      : null,

    showScanMeter.value
      ? normalizeMeterValue(
          meterForm.initial_scan_meter,
        )
      : null,
  ]

  const finalValues = [
    showTotalMeter.value
      ? normalizeMeterValue(
          meterForm.final_total_meter,
        )
      : null,

    showBlackMeter.value
      ? normalizeMeterValue(
          meterForm.final_black_meter,
        )
      : null,

    showColorMeter.value
      ? normalizeMeterValue(
          meterForm.final_color_meter,
        )
      : null,

    showScanMeter.value
      ? normalizeMeterValue(
          meterForm.final_scan_meter,
        )
      : null,
  ]

  if (
    initialValues.every(
      (value) => value === null,
    )
    && !cleanText(
      meterForm.initial_unavailable_reason,
    )
  ) {
    return (
      "Registre al menos un contador inicial "
      + "o indique el motivo."
    )
  }

  const pairs = [
    [
      "Total",
      initialValues[0],
      finalValues[0],
    ],
    [
      "B/N",
      initialValues[1],
      finalValues[1],
    ],
    [
      "Color",
      initialValues[2],
      finalValues[2],
    ],
    [
      "Escáner",
      initialValues[3],
      finalValues[3],
    ],
  ]

  for (
    const [
      label,
      initial,
      final,
    ]
    of pairs
  ) {
    if (
      initial !== null
      && final !== null
      && final < initial
    ) {
      return (
        `El contador final ${label} `
        + "no puede ser menor al inicial."
      )
    }
  }

  return ""
}


function buildMeterPayload() {
  const now = new Date().toISOString()

  const payload = {
    service_order: order.value.id,

    initial_total_meter: (
      showTotalMeter.value
        ? normalizeMeterValue(
            meterForm.initial_total_meter,
          )
        : null
    ),

    initial_black_meter: (
      showBlackMeter.value
        ? normalizeMeterValue(
            meterForm.initial_black_meter,
          )
        : null
    ),

    initial_color_meter: (
      showColorMeter.value
        ? normalizeMeterValue(
            meterForm.initial_color_meter,
          )
        : null
    ),

    initial_scan_meter: (
      showScanMeter.value
        ? normalizeMeterValue(
            meterForm.initial_scan_meter,
          )
        : null
    ),

    final_total_meter: (
      showTotalMeter.value
        ? normalizeMeterValue(
            meterForm.final_total_meter,
          )
        : null
    ),

    final_black_meter: (
      showBlackMeter.value
        ? normalizeMeterValue(
            meterForm.final_black_meter,
          )
        : null
    ),

    final_color_meter: (
      showColorMeter.value
        ? normalizeMeterValue(
            meterForm.final_color_meter,
          )
        : null
    ),

    final_scan_meter: (
      showScanMeter.value
        ? normalizeMeterValue(
            meterForm.final_scan_meter,
          )
        : null
    ),

    initial_unavailable_reason: cleanText(
      meterForm.initial_unavailable_reason,
    ),

    final_unavailable_reason: cleanText(
      meterForm.final_unavailable_reason,
    ),
  }

  const hasInitialReading = [
    payload.initial_total_meter,
    payload.initial_black_meter,
    payload.initial_color_meter,
    payload.initial_scan_meter,
  ].some(
    (value) => value !== null,
  )

  const hasFinalReading = [
    payload.final_total_meter,
    payload.final_black_meter,
    payload.final_color_meter,
    payload.final_scan_meter,
  ].some(
    (value) => value !== null,
  )

  payload.initial_reading_at = (
    meterReading.value?.initial_reading_at
    || (
      hasInitialReading
        ? now
        : null
    )
  )

  payload.final_reading_at = (
    hasFinalReading
      ? (
          meterReading.value?.final_reading_at
          || now
        )
      : null
  )

  return payload
}


async function saveMeters() {
  const validationMessage = (
    validateMeterForm()
  )

  if (validationMessage) {
    error.value = validationMessage
    return
  }

  meterSaving.value = true
  error.value = ""
  success.value = ""

  try {
    const payload = buildMeterPayload()

    const saved = (
      meterReading.value?.id
        ? await updateServiceMeterReading(
            meterReading.value.id,
            payload,
          )
        : await createServiceMeterReading(
            payload,
          )
    )

    meterReading.value = saved
    initializeMeterForm(saved)

    success.value = (
      "Contadores guardados correctamente."
    )
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    meterSaving.value = false
  }
}


async function sendPartRequest() {
  const requestItem = activePartRequest.value

  if (!requestItem?.id) {
    error.value = (
      "No existe un pedido de repuestos "
      + "para enviar."
    )
    return
  }

  if (!partItems.value.length) {
    error.value = (
      "El pedido no contiene repuestos."
    )
    return
  }

  partRequestSaving.value = true
  error.value = ""
  success.value = ""

  try {
    const updated = (
      await updateServicePartRequest(
        requestItem.id,
        {
          status: "requested",
          notes: cleanText(
            partRequestNotes.value,
          ),
        },
      )
    )

    partRequests.value = [
      updated,
      ...partRequests.value.filter(
        (item) => item.id !== updated.id,
      ),
    ]

    partRequestNotes.value = (
      updated.notes
      || ""
    )

    success.value = (
      "Pedido de repuestos enviado correctamente."
    )
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    partRequestSaving.value = false
  }
}


async function reloadChecklistAndParts() {
  if (!checklist.value) {
    checklistItems.value = []
    partItems.value = []

    return
  }

  const [
    itemRows,
    requestRows,
  ] = await Promise.all([
    getServiceChecklistItems({
      checklist: (
        checklist.value.id
      ),
    }),

    getServicePartRequests({
      service_order: (
        route.params.id
      ),
    }),
  ])

  checklistItems.value = (
    normalize(
      itemRows,
    )
  )

  initializeChecklistForms()

  const requests = (
    normalize(
      requestRows,
    )
  )

  partRequests.value = requests
  partRequestNotes.value = (
    requests[0]?.notes
    || ""
  )

  const requestItems = (
    await Promise.all(
      requests.map(
        (requestItem) => (
          getServicePartRequestItems({
            request: (
              requestItem.id
            ),
          })
        ),
      ),
    )
  )

  partItems.value = (
    requestItems.flatMap(
      normalize,
    )
  )
}


async function loadAll() {
  loading.value = true
  error.value = ""

  try {
    order.value = (
      await getServiceOrder(
        route.params.id,
      )
    )

    const [
      checklists,
      evidenceRows,
      meters,
      parts,
      statuses,
      assignments,
      points,
    ] = await Promise.all([
      getServiceChecklists({
        service_order: (
          route.params.id
        ),
      }),

      getServiceEvidences({
        service_order: (
          route.params.id
        ),
      }),

      getServiceMeterReadings({
        service_order: (
          route.params.id
        ),
      }),

      getServicePartRequests({
        service_order: (
          route.params.id
        ),
      }),

      getServiceStatusHistory({
        service_order: (
          route.params.id
        ),
      }),

      getServiceAssignmentHistory({
        service_order: (
          route.params.id
        ),
      }),

      getServiceTrackingPoints({
        service_order: (
          route.params.id
        ),
      }),
    ])

    checklist.value = (
      normalize(
        checklists,
      )[0]
      || null
    )

    evidences.value = (
      normalize(
        evidenceRows,
      )
    )

    meterReading.value = (
      normalize(
        meters,
      )[0]
      || null
    )

    initializeMeterForm(
      meterReading.value,
    )

    const requests = (
      normalize(
        parts,
      )
    )

    partRequests.value = requests
    partRequestNotes.value = (
      requests[0]?.notes
      || ""
    )

    const requestItems = (
      await Promise.all(
        requests.map(
          (item) => (
            getServicePartRequestItems({
              request: item.id,
            })
          ),
        ),
      )
    )

    partItems.value = (
      requestItems.flatMap(
        normalize,
      )
    )

    statusHistory.value = (
      normalize(
        statuses,
      )
    )

    assignmentHistory.value = (
      normalize(
        assignments,
      )
    )

    trackingPoints.value = (
      normalize(
        points,
      )
    )

    if (
      checklist.value
    ) {
      checklistItems.value = normalize(
        await getServiceChecklistItems({
          checklist: (
            checklist.value.id
          ),
        }),
      )
    } else {
      checklistItems.value = []
    }

    initializeChecklistForms()

    await loadFailedSubparts()
  } catch (requestError) {
    error.value = (
      requestError.message
    )
  } finally {
    loading.value = false
  }
}


async function runAction(
  callback,
  message,
) {
  actionLoading.value = true
  error.value = ""
  success.value = ""

  try {
    await callback()

    success.value = (
      message
    )

    await loadAll()
  } catch (requestError) {
    error.value = (
      requestError.message
    )
  } finally {
    actionLoading.value = false
  }
}


function assignTechnician() {
  if (
    !technicianId.value
  ) {
    error.value = (
      "Seleccione un técnico."
    )

    return
  }

  runAction(
    () => (
      assignServiceTechnician(
        order.value.id,
        technicianId.value,
      )
    ),
    "Técnico asignado correctamente.",
  )
}


function changeStatus(statusValue) {
  runAction(
    () => (
      changeServiceOrderStatus(
        order.value.id,
        statusValue,
      )
    ),
    "Estado actualizado correctamente.",
  )
}


function generateChecklist() {
  runAction(
    () => (
      generateServiceChecklist(
        order.value.id,
      )
    ),
    "Checklist generado correctamente.",
  )
}


function reloadSnapshot() {
  runAction(
    () => (
      loadCurrentServiceSnapshot(
        order.value.id,
      )
    ),
    "Datos históricos recargados.",
  )
}


function applyMeters() {
  runAction(
    () => (
      applyServiceMeterReading(
        order.value.id,
      )
    ),
    (
      "Contadores aplicados "
      + "al historial del equipo."
    ),
  )
}


function evidenceByStage(stage) {
  return (
    evidences.value.filter(
      (item) => (
        item.stage === stage
      ),
    )
  )
}


function getNextEvidenceSequence(stage) {
  const sequences = (
    evidenceByStage(
      stage,
    ).map(
      (item) => (
        Number(
          item.sequence,
        )
        || 0
      ),
    )
  )

  return (
    Math.max(
      0,
      ...sequences,
    )
    + 1
  )
}


function handleEvidenceFiles(
  event,
) {
  evidenceFiles.value = Array.from(
    event.target.files
    || [],
  )
}


function clearEvidenceForm() {
  evidenceFiles.value = []
  evidenceForm.notes = ""

  if (
    evidenceFileInput.value
  ) {
    evidenceFileInput.value.value = ""
  }
}


async function uploadEvidenceFiles() {
  if (
    !order.value?.id
  ) {
    error.value = (
      "No se encontró la orden de servicio."
    )

    return
  }

  if (
    !evidenceForm.stage
  ) {
    error.value = (
      "Seleccione el tipo de evidencia."
    )

    return
  }

  if (
    !evidenceFiles.value.length
  ) {
    error.value = (
      "Seleccione al menos una fotografía."
    )

    return
  }

  evidenceUploading.value = true
  error.value = ""
  success.value = ""

  try {
    let sequence = (
      getNextEvidenceSequence(
        evidenceForm.stage,
      )
    )

    for (
      const file
      of evidenceFiles.value
    ) {
      await uploadServiceEvidence({
        serviceOrder: (
          order.value.id
        ),

        stage: (
          evidenceForm.stage
        ),

        file,

        capturedAt: (
          new Date().toISOString()
        ),

        sequence,

        notes: cleanText(
          evidenceForm.notes,
        ),
      })

      sequence += 1
    }

    success.value = (
      evidenceFiles.value.length === 1
        ? (
            "Evidencia subida correctamente."
          )
        : (
            `${evidenceFiles.value.length} `
            + "evidencias subidas correctamente."
          )
    )

    clearEvidenceForm()

    evidences.value = normalize(
      await getServiceEvidences({
        service_order: (
          order.value.id
        ),
      }),
    )
  } catch (requestError) {
    error.value = (
      requestError.message
    )
  } finally {
    evidenceUploading.value = false
  }
}


onMounted(
  loadAll,
)
</script>


<template>
  <section class="service-detail-page">
    <header class="services-header">
      <div>
        <span class="page-kicker">
          Orden de servicio
        </span>

        <h2>
          {{ order?.code || "Cargando..." }}
        </h2>

        <p v-if="order">
          {{ order.equipment_serial_number }}
          ·
          {{ order.customer_name }}
        </p>
      </div>

      <div class="header-actions">
        <button
          class="secondary-button"
          type="button"
          @click="
            router.push({
              name: 'service-orders',
            })
          "
        >
          Volver
        </button>

        <button
          v-if="order"
          class="primary-button"
          type="button"
          @click="
            router.push({
              name: 'service-order-edit',
              params: {
                id: order.id,
              },
            })
          "
        >
          Editar
        </button>
      </div>
    </header>

    <p
      v-if="error"
      class="message error-message"
    >
      {{ error }}
    </p>

    <p
      v-if="success"
      class="message success-message"
    >
      {{ success }}
    </p>

    <div
      v-if="loading"
      class="loading-card"
    >
      <span class="spinner"></span>
      Cargando detalle...
    </div>

    <template v-else-if="order">
      <section class="service-hero-card">
        <div>
          <small>Equipo</small>

          <strong>
            {{ order.equipment_brand_name }}
            {{ order.equipment_model_name }}
          </strong>

          <span>
            Serie:
            {{ order.equipment_serial_number }}
          </span>
        </div>

        <div>
          <small>Cliente y sede</small>

          <strong>
            {{ order.customer_name }}
          </strong>

          <span>
            {{
              order.branch_name
              || order.address
            }}
          </span>
        </div>

        <div>
          <small>Técnico</small>

          <strong>
            {{
              order.technician_display
              || "Sin asignar"
            }}
          </strong>

          <span>
            {{ formatDate(order.scheduled_at) }}
          </span>
        </div>

        <div>
          <small>Estado</small>

          <strong>
            <span
              class="status-badge"
              :class="`status-${order.status}`"
            >
              {{ order.status_display }}
            </span>
          </strong>

          <span>
            {{ order.priority_display }}
            ·
            {{ order.service_type_display }}
          </span>
        </div>
      </section>

      <section class="service-action-card">
        <div class="technician-assignment">
          <ServiceSearchSelect
            v-model="technicianId"
            label="Asignar o cambiar técnico"
            placeholder="Buscar por nombre o usuario"
            :loader="searchTechnicians"
            :initial-label="
              technicianOption?.label
              || ''
            "
            @select="
              technicianOption = $event
            "
          />

          <button
            class="secondary-button"
            type="button"
            :disabled="actionLoading"
            @click="assignTechnician"
          >
            Asignar
          </button>
        </div>

        <div class="workflow-actions">
          <button
            v-for="action in nextActions"
            :key="action[0]"
            type="button"
            class="primary-button"
            :disabled="actionLoading"
            @click="changeStatus(action[0])"
          >
            {{ action[1] }}
          </button>

          <button
            v-if="!checklist"
            class="secondary-button"
            type="button"
            :disabled="actionLoading"
            @click="generateChecklist"
          >
            Generar checklist
          </button>

          <button
            v-if="
              [
                'draft',
                'pending_assignment',
              ].includes(order.status)
            "
            class="secondary-button"
            type="button"
            :disabled="actionLoading"
            @click="reloadSnapshot"
          >
            Recargar cliente
          </button>
        </div>
      </section>

      <nav class="detail-tabs">
        <button
          v-for="tab in tabs"
          :key="tab[0]"
          type="button"
          :class="{
            active: (
              activeTab === tab[0]
            ),
          }"
          @click="
            activeTab = tab[0]
          "
        >
          {{ tab[1] }}
        </button>
      </nav>

      <section
        v-if="activeTab === 'summary'"
        class="detail-panel"
      >
        <div class="detail-grid">
          <article>
            <small>
              Problema reportado
            </small>

            <p>
              {{ order.reported_problem }}
            </p>
          </article>

          <article>
            <small>Diagnóstico</small>

            <p>
              {{
                order.diagnosis
                || "Pendiente"
              }}
            </p>
          </article>

          <article>
            <small>
              Trabajo realizado
            </small>

            <p>
              {{
                order.work_performed
                || "Pendiente"
              }}
            </p>
          </article>

          <article>
            <small>Dirección</small>

            <p>
              {{ order.address }}
              {{ order.address_reference }}
            </p>
          </article>

          <article>
            <small>Contacto</small>

            <p>
              {{
                order.contact_name
                || "Sin contacto"
              }}
              ·
              {{ order.contact_phone }}
            </p>
          </article>

          <article>
            <small>Contrato</small>

            <p>
              {{
                order.contract_reference
                || "Sin referencia"
              }}
            </p>
          </article>
        </div>
      </section>

      <section
        v-if="activeTab === 'checklist'"
        class="detail-panel"
      >
        <div class="panel-header">
          <div>
            <span class="card-kicker">
              Revisión técnica
            </span>

            <h3>
              Checklist de la serie
            </h3>

            <p v-if="checklist">
              {{
                checklistProgress.reviewed
              }}
              de
              {{
                checklistProgress.total
              }}
              revisados ·
              {{
                checklistProgress.failed
              }}
              requieren cambio
            </p>
          </div>

          <button
            v-if="!checklist"
            class="primary-button"
            type="button"
            @click="generateChecklist"
          >
            Generar checklist
          </button>
        </div>

        <div
          v-if="checklist"
          class="checklist-progress"
        >
          <div class="checklist-progress__header">
            <strong>
              Avance del checklist
            </strong>

            <span>
              {{
                checklistProgress.percent
              }}%
            </span>
          </div>

          <div class="checklist-progress__track">
            <span
              :style="{
                width: (
                  `${checklistProgress.percent}%`
                ),
              }"
            ></span>
          </div>
        </div>

        <div
          v-if="checklistItems.length"
          class="checklist-edit-grid"
        >
          <article
            v-for="item in checklistItems"
            :key="item.id"
            class="checklist-edit-card"
            :class="
              getChecklistStatusClass(
                checklistForms[item.id]?.status,
              )
            "
          >
            <header class="checklist-edit-card__header">
              <div>
                <strong>
                  {{ item.component_name }}
                </strong>

                <small>
                  {{ item.component_type_name }}
                  ·
                  {{
                    item.position
                    || "General"
                  }}
                </small>
              </div>

              <span
                class="checklist-result-badge"
                :class="
                  getChecklistStatusClass(
                    checklistForms[item.id]?.status,
                  )
                "
              >
                {{
                  getStatusLabel(
                    checklistForms[item.id]?.status,
                  )
                }}
              </span>
            </header>

            <div
              v-if="checklistForms[item.id]"
              class="checklist-edit-card__body"
            >
              <label class="checklist-field">
                <span>Resultado</span>

                <select
                  v-model="
                    checklistForms[
                      item.id
                    ].status
                  "
                  :disabled="
                    checklistSaving[item.id]
                  "
                  @change="
                    handleChecklistStatusChange(
                      item,
                    )
                  "
                >
                  <option
                    v-for="option in checklistStatusOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </label>

              <label class="checklist-field">
                <span>
                  Observación
                  <b
                    v-if="
                      checklistForms[
                        item.id
                      ].status === 'failed'
                    "
                  >
                    *
                  </b>
                </span>

                <textarea
                  v-model="
                    checklistForms[
                      item.id
                    ].observation
                  "
                  rows="3"
                  :disabled="
                    checklistSaving[item.id]
                  "
                  placeholder="
                    Describe el estado,
                    falla o trabajo requerido
                  "
                ></textarea>
              </label>

              <div
                v-if="isConsumableItem(item)"
                class="consumable-fields"
              >
                <label class="checklist-checkbox">
                  <input
                    v-model="
                      checklistForms[
                        item.id
                      ].consumable_present
                    "
                    type="checkbox"
                    :disabled="
                      checklistSaving[item.id]
                    "
                  >

                  <span>
                    Consumible presente
                  </span>
                </label>

                <label class="checklist-field">
                  <span>
                    Nivel estimado
                  </span>

                  <div class="consumable-level">
                    <input
                      v-model.number="
                        checklistForms[
                          item.id
                        ].consumable_level_percent
                      "
                      type="range"
                      min="0"
                      max="100"
                      step="10"
                      :disabled="
                        checklistSaving[item.id]
                      "
                    >

                    <strong>
                      {{
                        checklistForms[
                          item.id
                        ].consumable_level_percent
                      }}%
                    </strong>
                  </div>
                </label>
              </div>

              <section
                v-if="
                  checklistForms[
                    item.id
                  ].status === 'failed'
                "
                class="subparts-panel"
              >
                <header class="subparts-panel__header">
                  <div>
                    <strong>
                      Subpartes compatibles
                    </strong>

                    <small>
                      Seleccione las piezas y
                      registre su cantidad.
                    </small>
                  </div>

                  <button
                    type="button"
                    class="mini-button"
                    :disabled="
                      compatibleSubpartsLoading[
                        item.id
                      ]
                    "
                    @click="
                      loadCompatibleSubparts(
                        item.id,
                        {
                          force: true,
                        },
                      )
                    "
                  >
                    Actualizar
                  </button>
                </header>

                <div
                  v-if="
                    compatibleSubpartsLoading[
                      item.id
                    ]
                  "
                  class="subparts-loading"
                >
                  <span class="spinner"></span>
                  Cargando subpartes...
                </div>

                <div
                  v-else-if="
                    compatibleSubparts[
                      item.id
                    ]?.length
                  "
                  class="subparts-list"
                >
                  <article
                    v-for="subpart in compatibleSubparts[item.id]"
                    :key="
                      subpart.compatibility
                      || subpart.id
                    "
                    class="subpart-card"
                    :class="{
                      'subpart-card--selected': (
                        subpart.selected
                      ),
                    }"
                  >
                    <div class="subpart-card__selection">
                      <button
                        type="button"
                        class="subpart-check"
                        :class="{
                          'subpart-check--active': (
                            subpart.selected
                          ),
                        }"
                        :disabled="
                          checklistSaving[
                            item.id
                          ]
                        "
                        @click="
                          toggleSubpart(
                            item.id,
                            subpart,
                          )
                        "
                      >
                        <span>
                          {{
                            subpart.selected
                              ? "✓"
                              : ""
                          }}
                        </span>
                      </button>

                      <img
                        v-if="subpart.image"
                        :src="subpart.image"
                        :alt="subpart.name"
                      >

                      <div
                        v-else
                        class="subpart-placeholder"
                      >
                        ⚙
                      </div>

                      <div>
                        <strong>
                          {{ subpart.name }}
                        </strong>

                        <small>
                          {{
                            subpart.code
                            || "Sin código"
                          }}
                          ·
                          {{
                            subpart.color_display
                            || "Sin color"
                          }}
                        </small>

                        <small
                          v-if="
                            subpart.manufacturer_reference
                            || subpart.manufacturer_code
                          "
                        >
                          Ref.:
                          {{
                            subpart.manufacturer_reference
                            || subpart.manufacturer_code
                          }}
                        </small>
                      </div>
                    </div>

                    <div
                      v-if="subpart.selected"
                      class="subpart-fields"
                    >
                      <label>
                        <span>Cantidad</span>

                        <input
                          v-model.number="
                            subpart.quantity
                          "
                          type="number"
                          min="0.01"
                          step="0.01"
                          :disabled="
                            checklistSaving[
                              item.id
                            ]
                          "
                        >
                      </label>

                      <label>
                        <span>Urgencia</span>

                        <select
                          v-model="
                            subpart.urgency
                          "
                          :disabled="
                            checklistSaving[
                              item.id
                            ]
                          "
                        >
                          <option
                            v-for="urgency in urgencyOptions"
                            :key="urgency.value"
                            :value="urgency.value"
                          >
                            {{ urgency.label }}
                          </option>
                        </select>
                      </label>

                      <label class="subpart-field-full">
                        <span>
                          Motivo
                        </span>

                        <textarea
                          v-model="
                            subpart.reason
                          "
                          rows="2"
                          :disabled="
                            checklistSaving[
                              item.id
                            ]
                          "
                          placeholder="
                            Motivo de la solicitud
                          "
                        ></textarea>
                      </label>

                      <label class="subpart-field-full">
                        <span>
                          Nota adicional
                        </span>

                        <textarea
                          v-model="
                            subpart.notes
                          "
                          rows="2"
                          :disabled="
                            checklistSaving[
                              item.id
                            ]
                          "
                          placeholder="
                            Información adicional
                          "
                        ></textarea>
                      </label>
                    </div>
                  </article>
                </div>

                <p
                  v-else
                  class="subparts-empty"
                >
                  No existen subpartes compatibles
                  configuradas para esta unidad y
                  modelo de equipo.
                </p>
              </section>

              <footer class="checklist-edit-card__footer">
                <small
                  v-if="item.checked_at"
                >
                  Última revisión:
                  {{ formatDate(item.checked_at) }}
                  ·
                  {{
                    item.checked_by_display
                    || "Técnico"
                  }}
                </small>

                <span v-else></span>

                <button
                  type="button"
                  class="primary-button"
                  :disabled="
                    checklistSaving[item.id]
                  "
                  @click="
                    saveChecklistItem(item)
                  "
                >
                  {{
                    checklistSaving[item.id]
                      ? "Guardando..."
                      : "Guardar resultado"
                  }}
                </button>
              </footer>
            </div>
          </article>
        </div>

        <p
          v-else
          class="empty-panel"
        >
          Aún no hay checklist generado.
        </p>
      </section>

      <section
        v-if="activeTab === 'parts'"
        class="detail-panel"
      >
        <div class="panel-header">
          <div>
            <span class="card-kicker">
              Solicitud de repuestos
            </span>

            <h3>
              Repuestos y subpartes
            </h3>

            <p>
              Las piezas se generan al guardar un
              componente como “Requiere cambio”.
            </p>
          </div>

          <div
            v-if="activePartRequest"
            class="part-request-status"
          >
            <small>Estado del pedido</small>

            <strong
              :class="
                `part-request-status--${activePartRequest.status}`
              "
            >
              {{
                activePartRequest.status_display
                || activePartRequest.status
              }}
            </strong>
          </div>
        </div>

        <div
          v-if="activePartRequest"
          class="part-request-card"
        >
          <div>
            <small>Pedido</small>

            <strong>
              {{
                activePartRequest.id
                  .slice(0, 8)
                  .toUpperCase()
              }}
            </strong>
          </div>

          <div>
            <small>Creado</small>

            <strong>
              {{
                formatDate(
                  activePartRequest.created_at,
                )
              }}
            </strong>
          </div>

          <div>
            <small>Solicitado</small>

            <strong>
              {{
                formatDate(
                  activePartRequest.requested_at,
                )
              }}
            </strong>
          </div>

          <div>
            <small>Total de piezas</small>

            <strong>
              {{ partItems.length }}
            </strong>
          </div>
        </div>

        <label
          v-if="activePartRequest"
          class="part-request-notes"
        >
          <span>Observación general del pedido</span>

          <textarea
            v-model="partRequestNotes"
            rows="3"
            :disabled="
              partRequestSaving
              || activePartRequest.status !== 'draft'
            "
            placeholder="
              Información adicional para almacén
              o el responsable de repuestos
            "
          ></textarea>
        </label>

        <div class="services-table-card">
          <table class="services-table">
            <thead>
              <tr>
                <th>Unidad</th>
                <th>Subparte</th>
                <th>Código</th>
                <th>Cantidad</th>
                <th>Urgencia</th>
                <th>Motivo</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="item in partItems"
                :key="item.id"
              >
                <td>
                  {{
                    item.parent_component_name
                    || item.checklist_component_name
                    || "—"
                  }}
                </td>

                <td>
                  <strong>
                    {{ item.component_name }}
                  </strong>

                  <small>
                    {{
                      item.color
                      || "Sin color"
                    }}
                  </small>
                </td>

                <td>
                  {{
                    item.component_code
                    || "—"
                  }}
                </td>

                <td>
                  {{
                    formatQuantity(
                      item.quantity,
                    )
                  }}
                  {{
                    item.unit_of_measure
                    || ""
                  }}
                </td>

                <td>
                  <span
                    class="part-urgency-badge"
                    :class="
                      `part-urgency-${item.urgency}`
                    "
                  >
                    {{
                      item.urgency_display
                      || getUrgencyLabel(
                        item.urgency,
                      )
                    }}
                  </span>
                </td>

                <td>
                  {{ item.reason }}
                </td>
              </tr>

              <tr v-if="!partItems.length">
                <td
                  colspan="6"
                  class="empty-table"
                >
                  No hay repuestos solicitados.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          v-if="
            activePartRequest?.status === 'draft'
            && partItems.length
          "
          class="part-request-actions"
        >
          <button
            type="button"
            class="primary-button"
            :disabled="partRequestSaving"
            @click="sendPartRequest"
          >
            {{
              partRequestSaving
                ? "Enviando..."
                : "Enviar pedido"
            }}
          </button>
        </div>
      </section>

      <section
        v-if="activeTab === 'evidence'"
        class="detail-panel"
      >
        <div class="panel-header">
          <div>
            <span class="card-kicker">
              Evidencias
            </span>

            <h3>
              Fotografías del servicio
            </h3>

            <p>
              Se requieren como mínimo tres fotos
              antes y tres después para cerrar
              la orden.
            </p>
          </div>
        </div>

        <div class="evidence-summary">
          <article>
            <small>Antes</small>

            <strong>
              {{
                evidenceByStage(
                  "before",
                ).length
              }}/3
            </strong>
          </article>

          <article>
            <small>Después</small>

            <strong>
              {{
                evidenceByStage(
                  "after",
                ).length
              }}/3
            </strong>
          </article>

          <article>
            <small>Contadores</small>

            <strong>
              {{
                evidenceByStage(
                  "meter",
                ).length
              }}
            </strong>
          </article>

          <article>
            <small>Repuestos</small>

            <strong>
              {{
                evidenceByStage(
                  "part",
                ).length
              }}
            </strong>
          </article>
        </div>

        <form
          class="evidence-upload-card"
          @submit.prevent="
            uploadEvidenceFiles
          "
        >
          <div class="evidence-upload-grid">
            <label>
              <span>
                Tipo de evidencia
              </span>

              <select
                v-model="
                  evidenceForm.stage
                "
                :disabled="
                  evidenceUploading
                "
              >
                <option
                  v-for="stage in evidenceStageOptions"
                  :key="stage.value"
                  :value="stage.value"
                >
                  {{ stage.label }}
                </option>
              </select>
            </label>

            <label class="evidence-file-field">
              <span>Fotografías</span>

              <input
                ref="evidenceFileInput"
                type="file"
                accept="image/*"
                multiple
                :disabled="
                  evidenceUploading
                "
                @change="
                  handleEvidenceFiles
                "
              >

              <small>
                {{
                  selectedEvidenceNames
                  || "Puede seleccionar una o varias fotos."
                }}
              </small>
            </label>

            <label class="evidence-notes-field">
              <span>Observación</span>

              <textarea
                v-model="
                  evidenceForm.notes
                "
                rows="3"
                :disabled="
                  evidenceUploading
                "
                placeholder="
                  Describe lo que se observa
                  en las fotografías
                "
              ></textarea>
            </label>
          </div>

          <div class="evidence-upload-actions">
            <button
              type="button"
              class="secondary-button"
              :disabled="
                evidenceUploading
              "
              @click="clearEvidenceForm"
            >
              Limpiar
            </button>

            <button
              type="submit"
              class="primary-button"
              :disabled="
                evidenceUploading
              "
            >
              {{
                evidenceUploading
                  ? "Subiendo..."
                  : "Subir evidencias"
              }}
            </button>
          </div>
        </form>

        <div class="evidence-grid">
          <article
            v-for="item in evidences"
            :key="item.id"
          >
            <img
              :src="item.file"
              :alt="item.stage_display"
            >

            <div>
              <strong>
                {{ item.stage_display }}
              </strong>

              <small>
                {{ formatDate(item.captured_at) }}
                ·
                Foto {{ item.sequence }}
              </small>

              <p>
                {{
                  item.notes
                  || "Sin observaciones"
                }}
              </p>
            </div>
          </article>
        </div>

        <p
          v-if="!evidences.length"
          class="empty-panel"
        >
          No hay evidencias registradas.
        </p>
      </section>

      <section
        v-if="activeTab === 'meters'"
        class="detail-panel"
      >
        <div class="panel-header">
          <div>
            <span class="card-kicker">
              Lecturas
            </span>

            <h3>
              Contadores iniciales y finales
            </h3>

            <p>
              Registra únicamente los contadores
              habilitados para este modelo.
            </p>
          </div>

          <div class="meter-header-actions">
            <button
              class="secondary-button"
              type="button"
              :disabled="meterSaving"
              @click="saveMeters"
            >
              {{
                meterSaving
                  ? "Guardando..."
                  : (
                      meterReading
                        ? "Actualizar contadores"
                        : "Guardar contadores"
                    )
              }}
            </button>

            <button
              v-if="
                meterReading
                && !meterReading.applied_to_equipment_history
              "
              class="primary-button"
              type="button"
              :disabled="
                meterSaving
                || actionLoading
              "
              @click="applyMeters"
            >
              Aplicar al equipo
            </button>
          </div>
        </div>

        <div class="meter-form-grid">
          <article class="meter-form-card">
            <header>
              <div>
                <span class="card-kicker">
                  Llegada
                </span>

                <h4>Lectura inicial</h4>
              </div>

              <small>
                {{
                  formatDate(
                    meterReading?.initial_reading_at,
                  )
                }}
              </small>
            </header>

            <div class="meter-fields">
              <label v-if="showTotalMeter">
                <span>Contador total</span>

                <input
                  v-model.number="
                    meterForm.initial_total_meter
                  "
                  type="number"
                  min="0"
                  step="1"
                  :disabled="meterSaving"
                  placeholder="0"
                >
              </label>

              <label v-if="showBlackMeter">
                <span>Blanco y negro</span>

                <input
                  v-model.number="
                    meterForm.initial_black_meter
                  "
                  type="number"
                  min="0"
                  step="1"
                  :disabled="meterSaving"
                  placeholder="0"
                >
              </label>

              <label v-if="showColorMeter">
                <span>Color</span>

                <input
                  v-model.number="
                    meterForm.initial_color_meter
                  "
                  type="number"
                  min="0"
                  step="1"
                  :disabled="meterSaving"
                  placeholder="0"
                >
              </label>

              <label v-if="showScanMeter">
                <span>Escáner</span>

                <input
                  v-model.number="
                    meterForm.initial_scan_meter
                  "
                  type="number"
                  min="0"
                  step="1"
                  :disabled="meterSaving"
                  placeholder="0"
                >
              </label>
            </div>

            <label class="meter-reason-field">
              <span>
                Motivo si no se pudo obtener
                la lectura inicial
              </span>

              <textarea
                v-model="
                  meterForm.initial_unavailable_reason
                "
                rows="3"
                :disabled="meterSaving"
                placeholder="
                  Ejemplo: equipo apagado,
                  pantalla dañada o sin acceso
                "
              ></textarea>
            </label>
          </article>

          <article class="meter-form-card">
            <header>
              <div>
                <span class="card-kicker">
                  Finalización
                </span>

                <h4>Lectura final</h4>
              </div>

              <small>
                {{
                  formatDate(
                    meterReading?.final_reading_at,
                  )
                }}
              </small>
            </header>

            <div class="meter-fields">
              <label v-if="showTotalMeter">
                <span>Contador total</span>

                <input
                  v-model.number="
                    meterForm.final_total_meter
                  "
                  type="number"
                  min="0"
                  step="1"
                  :disabled="meterSaving"
                  placeholder="0"
                >
              </label>

              <label v-if="showBlackMeter">
                <span>Blanco y negro</span>

                <input
                  v-model.number="
                    meterForm.final_black_meter
                  "
                  type="number"
                  min="0"
                  step="1"
                  :disabled="meterSaving"
                  placeholder="0"
                >
              </label>

              <label v-if="showColorMeter">
                <span>Color</span>

                <input
                  v-model.number="
                    meterForm.final_color_meter
                  "
                  type="number"
                  min="0"
                  step="1"
                  :disabled="meterSaving"
                  placeholder="0"
                >
              </label>

              <label v-if="showScanMeter">
                <span>Escáner</span>

                <input
                  v-model.number="
                    meterForm.final_scan_meter
                  "
                  type="number"
                  min="0"
                  step="1"
                  :disabled="meterSaving"
                  placeholder="0"
                >
              </label>
            </div>

            <label class="meter-reason-field">
              <span>
                Motivo si no se pudo obtener
                la lectura final
              </span>

              <textarea
                v-model="
                  meterForm.final_unavailable_reason
                "
                rows="3"
                :disabled="meterSaving"
                placeholder="
                  Registra el motivo únicamente
                  cuando no existe lectura final
                "
              ></textarea>
            </label>
          </article>
        </div>

        <div
          v-if="meterReading"
          class="meter-application-status"
        >
          <strong>
            {{
              meterReading.applied_to_equipment_history
                ? "Lectura aplicada al historial del equipo"
                : "Lectura pendiente de aplicar al equipo"
            }}
          </strong>
        </div>
      </section>

      <section
        v-if="activeTab === 'tracking'"
        class="detail-panel"
      >
        <div class="panel-header">
          <div>
            <span class="card-kicker">
              Ruta GPS
            </span>

            <h3>Puntos recibidos</h3>
          </div>

          <strong>
            {{ trackingPoints.length }}
            puntos
          </strong>
        </div>

        <div class="tracking-summary">
          <article
            v-for="point in trackingPoints.slice(0, 100)"
            :key="point.id"
          >
            <strong>
              {{ point.event_type_display }}
            </strong>

            <span>
              {{ point.latitude }},
              {{ point.longitude }}
            </span>

            <small>
              {{
                formatDate(
                  point.device_recorded_at,
                )
              }}
              · precisión
              {{
                point.accuracy_meters
                || "—"
              }}
              m
            </small>
          </article>
        </div>

        <p
          v-if="!trackingPoints.length"
          class="empty-panel"
        >
          La aplicación móvil aún no envió
          puntos GPS.
        </p>
      </section>

      <section
        v-if="activeTab === 'history'"
        class="detail-panel"
      >
        <div class="history-columns">
          <div>
            <h3>Estados</h3>

            <article
              v-for="item in statusHistory"
              :key="item.id"
              class="history-item"
            >
              <strong>
                {{ item.new_status_display }}
              </strong>

              <small>
                {{ formatDate(item.created_at) }}
                ·
                {{
                  item.changed_by_display
                  || "Sistema"
                }}
              </small>

              <p>
                {{ item.notes || "" }}
              </p>
            </article>
          </div>

          <div>
            <h3>Asignaciones</h3>

            <article
              v-for="item in assignmentHistory"
              :key="item.id"
              class="history-item"
            >
              <strong>
                {{
                  item.new_technician_display
                }}
              </strong>

              <small>
                {{ formatDate(item.created_at) }}
                ·
                {{
                  item.assigned_by_display
                  || "Sistema"
                }}
              </small>

              <p>
                {{ item.reason || "" }}
              </p>
            </article>
          </div>
        </div>
      </section>
    </template>
  </section>
</template>