import {
  createRouter,
  createWebHistory,
} from "vue-router"

import {
  isAuthenticated,
} from "../services/auth.service"

import MainLayout from "../layouts/MainLayout.vue"

import LoginView from "../views/auth/LoginView.vue"
import DashboardView from "../views/dashboard/DashboardView.vue"

import EquipmentCatalogsView from "../views/equipment/EquipmentCatalogsView.vue"
import EquipmentDetailView from "../views/equipment/EquipmentDetailView.vue"
import EquipmentFormView from "../views/equipment/EquipmentFormView.vue"
import EquipmentListView from "../views/equipment/EquipmentListView.vue"

import PartnerFormView from "../views/partners/PartnerFormView.vue"
import PartnersListView from "../views/partners/PartnersListView.vue"

import RepairDetailView from "../views/repairs/RepairDetailView.vue"
import RepairFormView from "../views/repairs/RepairFormView.vue"
import RepairsListView from "../views/repairs/RepairsListView.vue"

import SecurityView from "../views/security/SecurityView.vue"

import UserFormView from "../views/users/UserFormView.vue"
import UsersListView from "../views/users/UsersListView.vue"

import RentalsDashboardView from "../views/rentals/RentalsDashboardView.vue"
import RentalEquipmentListView from "../views/rentals/RentalEquipmentListView.vue"
import RentalEquipmentFormView from "../views/rentals/RentalEquipmentFormView.vue"
import RentalContractListView from "../views/rentals/RentalContractListView.vue"
import RentalContractFormView from "../views/rentals/RentalContractFormView.vue"
import RentalAssignmentListView from "../views/rentals/RentalAssignmentListView.vue"
import RentalAssignmentFormView from "../views/rentals/RentalAssignmentFormView.vue"
import RentalWarehouseListView from "../views/rentals/RentalWarehouseListView.vue"
import RentalWarehouseFormView from "../views/rentals/RentalWarehouseFormView.vue"
import RentalOperationsView from "../views/rentals/RentalOperationsView.vue"

import ServiceOrdersListView from "../views/services/ServiceOrdersListView.vue"
import ServiceOrderFormView from "../views/services/ServiceOrderFormView.vue"
import ServiceOrderDetailView from "../views/services/ServiceOrderDetailView.vue"


const routes = [
  {
    path: "/",
    redirect: "/dashboard",
  },
  {
    path: "/login",
    name: "login",
    component: LoginView,
    meta: {
      guestOnly: true,
      title: "Iniciar sesión",
    },
  },
  {
    path: "/",
    component: MainLayout,
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: "dashboard",
        name: "dashboard",
        component: DashboardView,
        meta: {
          requiresAuth: true,
          title: "Dashboard",
        },
      },

      /* ========================================================= */
      /* USUARIOS                                                  */
      /* ========================================================= */

      {
        path: "usuarios",
        name: "users",
        component: UsersListView,
        meta: {
          requiresAuth: true,
          title: "Usuarios",
        },
      },
      {
        path: "usuarios/nuevo",
        name: "user-create",
        component: UserFormView,
        meta: {
          requiresAuth: true,
          title: "Nuevo usuario",
        },
      },
      {
        path: "usuarios/:id/editar",
        name: "user-edit",
        component: UserFormView,
        meta: {
          requiresAuth: true,
          title: "Editar usuario",
        },
      },

      /* ========================================================= */
      /* CLIENTES, PROVEEDORES Y DISTRIBUIDORES                    */
      /* ========================================================= */

      {
        path: "clientes",
        name: "partners",
        component: PartnersListView,
        meta: {
          requiresAuth: true,
          title: "Clientes y proveedores",
        },
      },
      {
        path: "clientes/nuevo",
        name: "partner-create",
        component: PartnerFormView,
        meta: {
          requiresAuth: true,
          title: "Nuevo cliente o proveedor",
        },
      },
      {
        path: "clientes/:id/editar",
        name: "partner-edit",
        component: PartnerFormView,
        meta: {
          requiresAuth: true,
          title: "Editar cliente o proveedor",
        },
      },

      /* ========================================================= */
      /* EQUIPOS                                                   */
      /* ========================================================= */

      {
        path: "equipos",
        name: "equipment",
        component: EquipmentListView,
        meta: {
          requiresAuth: true,
          title: "Equipos",
        },
      },
      {
        path: "equipos/catalogos",
        name: "equipment-catalogs",
        component: EquipmentCatalogsView,
        meta: {
          requiresAuth: true,
          title: "Catálogos de equipos",
        },
      },
      {
        path: "equipos/nuevo",
        name: "equipment-create",
        component: EquipmentFormView,
        meta: {
          requiresAuth: true,
          title: "Nuevo equipo",
        },
      },
      {
        path: "equipos/:id",
        name: "equipment-detail",
        component: EquipmentDetailView,
        meta: {
          requiresAuth: true,
          title: "Detalle del equipo",
        },
      },
      {
        path: "equipos/:id/editar",
        name: "equipment-edit",
        component: EquipmentFormView,
        meta: {
          requiresAuth: true,
          title: "Editar equipo",
        },
      },


      /* ========================================================= */
      /* ALQUILERES                                                */
      /* ========================================================= */

      { path: "alquileres", name: "rentals-dashboard", component: RentalsDashboardView, meta: { requiresAuth: true, title: "Alquileres" } },
      { path: "alquileres/equipos", name: "rental-equipment-list", component: RentalEquipmentListView, meta: { requiresAuth: true, title: "Flota de alquiler" } },
      { path: "alquileres/equipos/nuevo", name: "rental-equipment-create", component: RentalEquipmentFormView, meta: { requiresAuth: true, title: "Nuevo equipo de alquiler" } },
      { path: "alquileres/equipos/:id/editar", name: "rental-equipment-edit", component: RentalEquipmentFormView, meta: { requiresAuth: true, title: "Editar equipo de alquiler" } },
      { path: "alquileres/contratos", name: "rental-contract-list", component: RentalContractListView, meta: { requiresAuth: true, title: "Contratos de alquiler" } },
      { path: "alquileres/contratos/nuevo", name: "rental-contract-create", component: RentalContractFormView, meta: { requiresAuth: true, title: "Nuevo contrato" } },
      { path: "alquileres/contratos/:id/editar", name: "rental-contract-edit", component: RentalContractFormView, meta: { requiresAuth: true, title: "Editar contrato" } },
      { path: "alquileres/asignaciones", name: "rental-assignment-list", component: RentalAssignmentListView, meta: { requiresAuth: true, title: "Asignaciones de alquiler" } },
      { path: "alquileres/asignaciones/nueva", name: "rental-assignment-create", component: RentalAssignmentFormView, meta: { requiresAuth: true, title: "Nueva asignación" } },
      { path: "alquileres/asignaciones/:id/editar", name: "rental-assignment-edit", component: RentalAssignmentFormView, meta: { requiresAuth: true, title: "Editar asignación" } },
      { path: "alquileres/almacenes", name: "rental-warehouse-list", component: RentalWarehouseListView, meta: { requiresAuth: true, title: "Almacenes de alquiler" } },
      { path: "alquileres/almacenes/nuevo", name: "rental-warehouse-create", component: RentalWarehouseFormView, meta: { requiresAuth: true, title: "Nuevo almacén" } },
      { path: "alquileres/almacenes/:id/editar", name: "rental-warehouse-edit", component: RentalWarehouseFormView, meta: { requiresAuth: true, title: "Editar almacén" } },
      { path: "alquileres/operaciones", name: "rental-operations", component: RentalOperationsView, meta: { requiresAuth: true, title: "Operaciones de alquiler" } },


      /* ========================================================= */
      /* ÓRDENES DE SERVICIO                                      */
      /* ========================================================= */

      {
        path: "servicios",
        name: "service-orders",
        component: ServiceOrdersListView,
        meta: { requiresAuth: true, title: "Órdenes de servicio" },
      },
      {
        path: "servicios/nueva",
        name: "service-order-create",
        component: ServiceOrderFormView,
        meta: { requiresAuth: true, title: "Nueva orden de servicio" },
      },
      {
        path: "servicios/:id",
        name: "service-order-detail",
        component: ServiceOrderDetailView,
        meta: { requiresAuth: true, title: "Detalle de orden de servicio" },
      },
      {
        path: "servicios/:id/editar",
        name: "service-order-edit",
        component: ServiceOrderFormView,
        meta: { requiresAuth: true, title: "Editar orden de servicio" },
      },

      /* ========================================================= */
      /* REPARACIONES                                              */
      /* ========================================================= */

      {
        path: "reparaciones",
        name: "repairs",
        component: RepairsListView,
        meta: {
          requiresAuth: true,
          title: "Reparaciones",
        },
      },
      {
        path: "reparaciones/nueva",
        name: "repair-create",
        component: RepairFormView,
        meta: {
          requiresAuth: true,
          title: "Nueva reparación",
        },
      },
      {
        path: "reparaciones/:id",
        name: "repair-detail",
        component: RepairDetailView,
        meta: {
          requiresAuth: true,
          title: "Detalle de reparación",
        },
      },
      {
        path: "reparaciones/:id/editar",
        name: "repair-edit",
        component: RepairFormView,
        meta: {
          requiresAuth: true,
          title: "Editar reparación",
        },
      },

      /* ========================================================= */
      /* SEGURIDAD                                                 */
      /* ========================================================= */

      {
        path: "seguridad",
        name: "security",
        component: SecurityView,
        meta: {
          requiresAuth: true,
          title: "Seguridad",
        },
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/dashboard",
  },
]


const router = createRouter({
  history: createWebHistory(),
  routes,
})


router.beforeEach((to) => {
  const authenticated =
    isAuthenticated()

  if (
    to.matched.some(
      (record) =>
        record.meta.requiresAuth
    ) &&
    !authenticated
  ) {
    return {
      name: "login",
    }
  }

  if (
    to.meta.guestOnly &&
    authenticated
  ) {
    return {
      name: "dashboard",
    }
  }

  return true
})


router.afterEach((to) => {
  const title =
    to.meta.title ||
    "Copier OS"

  document.title =
    `${title} | Copier OS`
})


export default router