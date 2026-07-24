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