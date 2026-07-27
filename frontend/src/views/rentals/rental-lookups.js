import {
  getEquipment,
} from "../../services/equipment.service"

import {
  getPartnerBranches,
  getPartnerContacts,
  getPartners,
} from "../../services/partners.service"

import {
  getUsers,
} from "../../services/users.service"

import {
  getRentalAssignments,
  getRentalContracts,
  getRentalEquipment,
  getWarehouses,
} from "../../services/rentals.service"


function rows(data) {
  if (Array.isArray(data)) {
    return data
  }

  if (Array.isArray(data?.results)) {
    return data.results
  }

  return []
}


function cleanText(value) {
  return String(value ?? "").trim()
}


function joinParts(parts) {
  return parts
    .map(cleanText)
    .filter(Boolean)
    .join(" · ")
}


function getPartnerName(item) {
  const naturalPersonName = joinParts([
    item?.first_names,
    item?.paternal_last_name,
    item?.maternal_last_name,
  ])

  return (
    cleanText(item?.legal_name)
    || cleanText(item?.trade_name)
    || cleanText(item?.display_name)
    || naturalPersonName
    || cleanText(item?.document_number)
    || "Sin nombre"
  )
}


function normalizePartner(
  item,
  defaultDescription = "Tercero",
) {
  const partnerName = getPartnerName(item)

  const description = joinParts([
    item?.trade_name !== partnerName
      ? item?.trade_name
      : "",
    item?.person_type_display,
    defaultDescription,
  ])

  return {
    id: item.id,
    value: item.id,
    label: joinParts([
      partnerName,
      item.document_number,
    ]),
    description: (
      description
      || defaultDescription
    ),
    raw: item,
  }
}


function normalizeEquipment(item) {
  const label = joinParts([
    item.serial_number,
    item.internal_code,
    item.brand_name,
    item.model_name,
  ])

  return {
    id: item.id,
    value: item.id,
    label: label || "Equipo sin identificación",
    description: joinParts([
      item.equipment_type_name,
      item.is_available
        ? "Equipo disponible"
        : "Equipo no disponible",
    ]),
    raw: item,
  }
}


function normalizeRentalEquipment(item) {
  const label = joinParts([
    item.equipment_serial_number,
    item.equipment_internal_code,
    item.equipment_brand_name,
    item.equipment_model_name,
  ])

  return {
    id: item.id,
    value: item.id,
    label: (
      label
      || item.equipment_display
      || "Máquina de alquiler"
    ),
    description: joinParts([
      item.warehouse_name,
      item.warehouse_location,
      item.operational_status_display,
    ]),
    raw: item,
  }
}


function normalizeContract(item) {
  return {
    id: item.id,
    value: item.id,
    label: joinParts([
      item.code,
      item.contract_number,
      item.customer_name,
    ]) || "Contrato sin identificación",
    description: joinParts([
      item.status_display,
      item.contract_type_display,
      item.start_date,
      item.end_date,
    ]),
    raw: item,
  }
}


function normalizeAssignment(item) {
  return {
    id: item.id,
    value: item.id,
    label: joinParts([
      item.code,
      item.equipment_serial_number,
      item.customer_name,
    ]) || "Asignación sin identificación",
    description: joinParts([
      item.branch_name,
      item.status_display,
      item.contract_reference,
    ]),
    raw: item,
  }
}


function normalizeBranch(item) {
  return {
    id: item.id,
    value: item.id,
    label: joinParts([
      item.name,
      item.address,
    ]) || "Sede sin nombre",
    description: joinParts([
      item.district,
      item.province,
      item.region,
    ]),
    raw: item,
  }
}


function normalizeContact(item) {
  const fullName = (
    cleanText(item.full_name)
    || cleanText(item.display_name)
    || cleanText(item.name)
    || joinParts([
      item.first_names,
      item.paternal_last_name,
      item.maternal_last_name,
    ])
    || "Contacto sin nombre"
  )

  return {
    id: item.id,
    value: item.id,
    label: fullName,
    description: joinParts([
      item.job_title,
      item.primary_mobile
        || item.work_phone
        || item.whatsapp_number,
      item.primary_email,
    ]),
    raw: item,
  }
}


function normalizeUser(item) {
  const fullName = (
    cleanText(item.full_name)
    || joinParts([
      item.first_name,
      item.last_name,
    ])
    || cleanText(item.username)
    || cleanText(item.email)
    || "Usuario"
  )

  return {
    id: item.id,
    value: item.id,
    label: joinParts([
      fullName,
      item.username,
    ]),
    description: joinParts([
      item.email,
      item.job_title || item.position,
    ]) || "Usuario",
    raw: item,
  }
}


function normalizeWarehouse(item) {
  return {
    id: item.id,
    value: item.id,
    label: joinParts([
      item.code,
      item.name,
    ]) || "Almacén sin nombre",
    description: joinParts([
      item.address,
      item.warehouse_type_display,
    ]) || "Almacén",
    raw: item,
  }
}


/*
|--------------------------------------------------------------------------
| EQUIPOS GENERALES
|--------------------------------------------------------------------------
*/

export async function searchEquipment(
  search = "",
) {
  const data = await getEquipment({
    search: cleanText(search),
  })

  return rows(data).map(
    normalizeEquipment,
  )
}


/*
|--------------------------------------------------------------------------
| EQUIPOS DISPONIBLES PARA ASIGNAR A UN CONTRATO
|--------------------------------------------------------------------------
*/

export async function searchRentalEquipment(
  search = "",
) {
  const data = await getRentalEquipment({
    search: cleanText(search),
    purpose: "rental",
    operational_status: "ready_for_rental",
    is_available_for_rental: true,
  })

  return rows(data).map(
    normalizeRentalEquipment,
  )
}


/*
|--------------------------------------------------------------------------
| TODOS LOS EQUIPOS DEL ALMACÉN DE ALQUILER
|--------------------------------------------------------------------------
*/

export async function searchAllRentalEquipment(
  search = "",
) {
  const data = await getRentalEquipment({
    search: cleanText(search),
    purpose: "rental",
  })

  return rows(data).map(
    normalizeRentalEquipment,
  )
}


/*
|--------------------------------------------------------------------------
| CONTRATOS
|--------------------------------------------------------------------------
*/

export async function searchContracts(
  search = "",
) {
  const data = await getRentalContracts({
    search: cleanText(search),
  })

  return rows(data).map(
    normalizeContract,
  )
}


export async function searchActiveContracts(
  search = "",
) {
  const data = await getRentalContracts({
    search: cleanText(search),
    status: "active",
  })

  return rows(data).map(
    normalizeContract,
  )
}


/*
|--------------------------------------------------------------------------
| ASIGNACIONES
|--------------------------------------------------------------------------
*/

export async function searchAssignments(
  search = "",
) {
  const data = await getRentalAssignments({
    search: cleanText(search),
  })

  return rows(data).map(
    normalizeAssignment,
  )
}


export async function searchActiveAssignments(
  search = "",
) {
  const data = await getRentalAssignments({
    search: cleanText(search),
    status: "active",
  })

  return rows(data).map(
    normalizeAssignment,
  )
}


/*
|--------------------------------------------------------------------------
| PARTNERS GENÉRICOS
|--------------------------------------------------------------------------
*/

export async function searchPartners(
  search = "",
) {
  const data = await getPartners({
    search: cleanText(search),
    isActive: true,
  })

  return rows(data).map(
    (item) => normalizePartner(
      item,
      "Cliente, proveedor o distribuidor",
    ),
  )
}


/*
|--------------------------------------------------------------------------
| CLIENTES DE ALQUILER
|--------------------------------------------------------------------------
*/

export async function searchRentalCustomers(
  search = "",
) {
  const data = await getPartners({
    search: cleanText(search),
    role: "rental_customer",
    isActive: true,
    isCommerciallyBlocked: false,
  })

  return rows(data).map(
    (item) => normalizePartner(
      item,
      "Cliente de alquiler",
    ),
  )
}


/*
|--------------------------------------------------------------------------
| CLIENTES DE SERVICIO TÉCNICO
|--------------------------------------------------------------------------
*/

export async function searchServiceCustomers(
  search = "",
) {
  const data = await getPartners({
    search: cleanText(search),
    role: "service_customer",
    isActive: true,
    isCommerciallyBlocked: false,
  })

  return rows(data).map(
    (item) => normalizePartner(
      item,
      "Cliente de servicio técnico",
    ),
  )
}


/*
|--------------------------------------------------------------------------
| CLIENTES DE VENTA
|--------------------------------------------------------------------------
*/

export async function searchSalesCustomers(
  search = "",
) {
  const data = await getPartners({
    search: cleanText(search),
    role: "sales_customer",
    isActive: true,
    isCommerciallyBlocked: false,
  })

  return rows(data).map(
    (item) => normalizePartner(
      item,
      "Cliente de venta",
    ),
  )
}


/*
|--------------------------------------------------------------------------
| PROVEEDORES
|--------------------------------------------------------------------------
*/

export async function searchSuppliers(
  search = "",
) {
  const data = await getPartners({
    search: cleanText(search),
    role: "supplier",
    isActive: true,
  })

  return rows(data).map(
    (item) => normalizePartner(
      item,
      "Proveedor",
    ),
  )
}


/*
|--------------------------------------------------------------------------
| DISTRIBUIDORES
|--------------------------------------------------------------------------
*/

export async function searchDistributors(
  search = "",
) {
  const data = await getPartners({
    search: cleanText(search),
    role: "distributor",
    isActive: true,
    isCommerciallyBlocked: false,
  })

  return rows(data).map(
    (item) => normalizePartner(
      item,
      "Distribuidor",
    ),
  )
}


/*
|--------------------------------------------------------------------------
| SEDES
|--------------------------------------------------------------------------
*/

export async function searchBranches(
  search = "",
  partnerId = "",
) {
  const normalizedPartnerId = cleanText(
    partnerId,
  )

  if (!normalizedPartnerId) {
    return []
  }

  const data = await getPartnerBranches({
    partner: normalizedPartnerId,
    search: cleanText(search),
    isActive: true,
  })

  return rows(data).map(
    normalizeBranch,
  )
}


/*
|--------------------------------------------------------------------------
| SEDES APTAS PARA INSTALAR EQUIPOS
|--------------------------------------------------------------------------
*/

export async function searchInstallationBranches(
  search = "",
  partnerId = "",
) {
  const normalizedPartnerId = cleanText(
    partnerId,
  )

  if (!normalizedPartnerId) {
    return []
  }

  const data = await getPartnerBranches({
    partner: normalizedPartnerId,
    search: cleanText(search),
    isActive: true,
    allowsEquipmentInstallation: true,
  })

  return rows(data).map(
    normalizeBranch,
  )
}


/*
|--------------------------------------------------------------------------
| CONTACTOS
|--------------------------------------------------------------------------
*/

export async function searchContacts(
  search = "",
  partnerId = "",
  branchId = "",
) {
  const normalizedPartnerId = cleanText(
    partnerId,
  )

  const normalizedBranchId = cleanText(
    branchId,
  )

  if (!normalizedPartnerId) {
    return []
  }

  const filters = {
    partner: normalizedPartnerId,
    search: cleanText(search),
    isActive: true,
  }

  if (normalizedBranchId) {
    filters.branch = normalizedBranchId
  }

  const data = await getPartnerContacts(
    filters,
  )

  return rows(data).map(
    normalizeContact,
  )
}


/*
|--------------------------------------------------------------------------
| CONTACTOS QUE RECIBEN AVISOS DE SERVICIO
|--------------------------------------------------------------------------
*/

export async function searchServiceContacts(
  search = "",
  partnerId = "",
  branchId = "",
) {
  const normalizedPartnerId = cleanText(
    partnerId,
  )

  const normalizedBranchId = cleanText(
    branchId,
  )

  if (!normalizedPartnerId) {
    return []
  }

  const filters = {
    partner: normalizedPartnerId,
    search: cleanText(search),
    isActive: true,
    receivesServiceNotifications: true,
  }

  if (normalizedBranchId) {
    filters.branch = normalizedBranchId
  }

  const data = await getPartnerContacts(
    filters,
  )

  return rows(data).map(
    normalizeContact,
  )
}


/*
|--------------------------------------------------------------------------
| USUARIOS
|--------------------------------------------------------------------------
*/

export async function searchUsers(
  search = "",
) {
  const data = await getUsers({
    search: cleanText(search),
    isActive: true,
  })

  return rows(data)
    .filter(
      (item) => item.is_active !== false,
    )
    .map(
      normalizeUser,
    )
}


/*
|--------------------------------------------------------------------------
| TÉCNICOS
|--------------------------------------------------------------------------
*/

export async function searchTechnicians(
  search = "",
) {
  const data = await getUsers({
    search: cleanText(search),
    isActive: true,
  })

  return rows(data)
    .filter(
      (item) => {
        if (item.is_active === false) {
          return false
        }

        const role = cleanText(
          item.role
          || item.user_type
          || item.position,
        ).toLowerCase()

        if (!role) {
          return true
        }

        return (
          role.includes("technician")
          || role.includes("tecnico")
          || role.includes("técnico")
          || role.includes("service")
          || role.includes("servicio")
        )
      },
    )
    .map(
      normalizeUser,
    )
}


/*
|--------------------------------------------------------------------------
| ALMACENES
|--------------------------------------------------------------------------
*/

export async function searchWarehouses(
  search = "",
) {
  const data = await getWarehouses({
    search: cleanText(search),
    is_active: true,
  })

  return rows(data).map(
    normalizeWarehouse,
  )
}


/*
|--------------------------------------------------------------------------
| ALMACENES QUE PERMITEN INGRESOS
|--------------------------------------------------------------------------
*/

export async function searchEntryWarehouses(
  search = "",
) {
  const data = await getWarehouses({
    search: cleanText(search),
    is_active: true,
    allows_entries: true,
  })

  return rows(data).map(
    normalizeWarehouse,
  )
}