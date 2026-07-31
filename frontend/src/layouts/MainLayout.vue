<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue"

import {
  useRoute,
  useRouter,
} from "vue-router"

import {
  clearSession,
  getStoredUser,
} from "../services/auth.service"

import "./styles/app-layout.css"


const router = useRouter()
const route = useRoute()

const user = getStoredUser()

const profileOpen = ref(false)
const radialMenuOpen = ref(false)
const activeSubmenuKey = ref("")


const navigationItems = [
  {
    key: "dashboard",
    label: "Dashboard",
    description: "Panel principal",
    path: "/dashboard",
    color: "#263cc7",
    routeNames: [
      "dashboard",
    ],
  },
  {
    key: "users",
    label: "Usuarios",
    description: "Usuarios y permisos",
    path: "/usuarios",
    color: "#7c3aed",
    routeNames: [
      "users",
      "user-create",
      "user-edit",
    ],
  },
  {
    key: "customers",
    label: "Clientes",
    description: "Clientes y proveedores",
    path: "/clientes",
    color: "#0891b2",
    routeNames: [
      "partners",
      "partner-create",
      "partner-edit",
    ],
  },
  {
    key: "machines",
    label: "Equipos",
    description: "Máquinas e inventario",
    path: "/equipos",
    color: "#2563eb",
    routeNames: [
      "equipment",
      "equipment-create",
      "equipment-detail",
      "equipment-edit",
    ],
  },
  {
    key: "contracts",
    label: "Alquileres",
    description: "Flota, contratos y operaciones",
    path: "/alquileres",
    color: "#d97706",
    routeNames: [
      "rentals-dashboard",
      "rental-equipment-list",
      "rental-equipment-create",
      "rental-equipment-edit",
      "rental-contract-list",
      "rental-contract-create",
      "rental-contract-edit",
      "rental-assignment-list",
      "rental-assignment-create",
      "rental-assignment-edit",
      "rental-warehouse-list",
      "rental-warehouse-create",
      "rental-warehouse-edit",
      "rental-operations",
    ],
  },
  {
    key: "services",
    label: "Servicios",
    description: "Órdenes y atenciones técnicas",
    path: "/servicios",
    color: "#16a34a",
    routeNames: [
      "service-orders",
      "service-order-create",
      "service-order-detail",
      "service-order-edit",
    ],
  },
  {
    key: "repairs",
    label: "Taller",
    description: "Reparaciones y repuestos",
    color: "#e11d48",
    children: [
      {
        label: "Reparaciones",
        path: "/reparaciones",
      },
      {
        label: "Pedidos",
        path: "/reparaciones/pedidos",
      },
      {
        label: "Configuración",
        path: "/reparaciones/configuracion",
      },
    ],
  },
  {
    key: "settings",
    label: "Configuración",
    description: "Tipos, marcas y modelos",
    path: "/equipos/catalogos",
    color: "#475569",
    routeNames: [
      "equipment-catalogs",
    ],
  },
  {
    key: "security",
    label: "Seguridad",
    description: "Acceso y protección",
    path: "/seguridad",
    color: "#dc2626",
    routeNames: [
      "security",
    ],
  },
]


const userName = computed(() => {
  if (!user) {
    return "Usuario"
  }

  const fullName = [
    user.first_name,
    user.paternal_last_name,
    user.maternal_last_name,
  ]
    .filter(Boolean)
    .join(" ")
    .trim()

  return (
    user.full_name ||
    fullName ||
    user.username ||
    user.email ||
    "Usuario"
  )
})


const initials = computed(() => {
  const name = userName.value.trim()

  if (!name) {
    return "U"
  }

  const words = name
    .split(" ")
    .filter(Boolean)

  if (words.length === 1) {
    return words[0]
      .charAt(0)
      .toUpperCase()
  }

  return (
    words[0].charAt(0) +
    words[1].charAt(0)
  ).toUpperCase()
})


function isNavigationActive(item) {
  if (Array.isArray(item.routeNames)) {
    return item.routeNames.includes(
      route.name
    )
  }

  if (Array.isArray(item.children)) {
    return item.children.some(
      child =>
        route.path === child.path ||
        route.path.startsWith(
          `${child.path}/`
        )
    )
  }

  return false
}


function toggleRadialMenu() {
  radialMenuOpen.value =
    !radialMenuOpen.value

  profileOpen.value = false
}


function closeRadialMenu() {
  radialMenuOpen.value = false
  activeSubmenuKey.value = ""
}


function toggleProfileMenu() {
  profileOpen.value =
    !profileOpen.value

  radialMenuOpen.value = false
  activeSubmenuKey.value = ""
}


function closeProfileMenu() {
  profileOpen.value = false
}


function hasChildren(item) {
  return (
    Array.isArray(item.children) &&
    item.children.length > 0
  )
}


function openSubmenu(item) {
  if (!hasChildren(item)) {
    return
  }

  activeSubmenuKey.value = item.key
}


function closeSubmenu(item) {
  if (
    activeSubmenuKey.value === item.key
  ) {
    activeSubmenuKey.value = ""
  }
}


function isSubmenuOpen(item) {
  return (
    radialMenuOpen.value &&
    activeSubmenuKey.value === item.key &&
    hasChildren(item)
  )
}


async function selectNavigationItem(item) {
  if (hasChildren(item)) {
    activeSubmenuKey.value =
      activeSubmenuKey.value === item.key
        ? ""
        : item.key

    return
  }

  closeRadialMenu()

  if (item.comingSoon) {
    window.alert(
      "Este módulo se desarrollará en los siguientes pasos."
    )

    return
  }

  if (!item.path) {
    return
  }

  await router.push(item.path)
}


async function selectSubmenuItem(child) {
  closeRadialMenu()

  await router.push(child.path)
}


async function logout() {
  profileOpen.value = false
  radialMenuOpen.value = false
  activeSubmenuKey.value = ""

  clearSession()

  await router.push({
    name: "login",
  })
}


function showComingSoon() {
  window.alert(
    "Este módulo se desarrollará en los siguientes pasos."
  )

  closeProfileMenu()
  closeRadialMenu()
}


function handleDocumentClick(event) {
  const radialContainer =
    event.target.closest(
      ".radial-menu-container"
    )

  const profileContainer =
    event.target.closest(
      ".profile-container"
    )

  if (!radialContainer) {
    radialMenuOpen.value = false
    activeSubmenuKey.value = ""
  }

  if (!profileContainer) {
    profileOpen.value = false
  }
}


function handleEscape(event) {
  if (event.key !== "Escape") {
    return
  }

  radialMenuOpen.value = false
  profileOpen.value = false
  activeSubmenuKey.value = ""
}


watch(
  () => route.fullPath,
  () => {
    radialMenuOpen.value = false
    profileOpen.value = false
    activeSubmenuKey.value = ""
  }
)


onMounted(() => {
  document.addEventListener(
    "click",
    handleDocumentClick
  )

  document.addEventListener(
    "keydown",
    handleEscape
  )
})


onBeforeUnmount(() => {
  document.removeEventListener(
    "click",
    handleDocumentClick
  )

  document.removeEventListener(
    "keydown",
    handleEscape
  )
})
</script>

<template>
  <div class="app-layout">
    <header class="topbar">
      <div class="topbar-main">
        <div
          class="radial-menu-container"
          :class="{
            open: radialMenuOpen,
          }"
        >
          <button
            class="radial-toggle"
            type="button"
            :class="{
              open: radialMenuOpen,
            }"
            :aria-expanded="radialMenuOpen"
            aria-label="Mostrar menú principal"
            @click.stop="toggleRadialMenu"
          >
            <span class="radial-toggle-glow"></span>
            <span class="radial-toggle-ring"></span>

            <svg
              class="radial-toggle-icon"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <line
                class="menu-line menu-line-top"
                x1="5"
                y1="7"
                x2="19"
                y2="7"
              />

              <line
                class="menu-line menu-line-middle"
                x1="5"
                y1="12"
                x2="19"
                y2="12"
              />

              <line
                class="menu-line menu-line-bottom"
                x1="5"
                y1="17"
                x2="19"
                y2="17"
              />
            </svg>
          </button>

          <Transition name="radial-backdrop">
            <button
              v-if="radialMenuOpen"
              class="radial-menu-backdrop"
              type="button"
              tabindex="-1"
              aria-label="Cerrar menú"
              @click="closeRadialMenu"
            ></button>
          </Transition>

          <div
            class="radial-menu"
            :class="{
              open: radialMenuOpen,
            }"
          >
            <div class="radial-menu-surface">
              <span
                class="
                  radial-decoration
                  radial-decoration-one
                "
              ></span>

              <span
                class="
                  radial-decoration
                  radial-decoration-two
                "
              ></span>

              <span
                class="
                  radial-decoration
                  radial-decoration-three
                "
              ></span>
            </div>

            <div
              v-for="(item, index) in navigationItems"
              :key="item.key"
              class="radial-item-group"
              :class="[
                `radial-item-${index + 1}`,
                {
                  active:
                    isNavigationActive(item),
                  'submenu-open':
                    isSubmenuOpen(item),
                  'has-children':
                    hasChildren(item),
                },
              ]"
              :style="{
                '--item-index': index,
                '--item-color': item.color,
              }"
              @mouseenter="openSubmenu(item)"
              @mouseleave="closeSubmenu(item)"
            >
              <button
                class="radial-item"
                type="button"
                @click.stop="selectNavigationItem(item)"
              >
              <span class="radial-item-icon">
                <!-- Dashboard -->
                <svg
                  v-if="item.key === 'dashboard'"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <rect
                    x="3"
                    y="3"
                    width="7"
                    height="7"
                    rx="1"
                  />

                  <rect
                    x="14"
                    y="3"
                    width="7"
                    height="7"
                    rx="1"
                  />

                  <rect
                    x="3"
                    y="14"
                    width="7"
                    height="7"
                    rx="1"
                  />

                  <rect
                    x="14"
                    y="14"
                    width="7"
                    height="7"
                    rx="1"
                  />
                </svg>

                <!-- Usuarios -->
                <svg
                  v-else-if="item.key === 'users'"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    d="
                      M16 21v-2
                      a4 4 0 0 0-4-4H6
                      a4 4 0 0 0-4 4v2
                    "
                  />

                  <circle
                    cx="9"
                    cy="7"
                    r="4"
                  />

                  <path
                    d="
                      M22 21v-2
                      a4 4 0 0 0-3-3.87
                    "
                  />

                  <path
                    d="
                      M16 3.13
                      a4 4 0 0 1 0 7.75
                    "
                  />
                </svg>

                <!-- Clientes -->
                <svg
                  v-else-if="
                    item.key === 'customers'
                  "
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path d="M3 21h18" />

                  <path
                    d="
                      M6 21V5
                      a2 2 0 0 1 2-2h8
                      a2 2 0 0 1 2 2v16
                    "
                  />

                  <path d="M9 7h2" />
                  <path d="M13 7h2" />
                  <path d="M9 11h2" />
                  <path d="M13 11h2" />
                  <path d="M9 15h2" />
                  <path d="M13 15h2" />
                </svg>

                <!-- Equipos -->
                <svg
                  v-else-if="
                    item.key === 'machines'
                  "
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path d="M6 9V2h12v7" />

                  <path
                    d="
                      M6 18H4
                      a2 2 0 0 1-2-2v-5
                      a2 2 0 0 1 2-2h16
                      a2 2 0 0 1 2 2v5
                      a2 2 0 0 1-2 2h-2
                    "
                  />

                  <rect
                    x="6"
                    y="14"
                    width="12"
                    height="8"
                    rx="1"
                  />

                  <path d="M18 12h.01" />
                </svg>

                <!-- Contratos -->
                <svg
                  v-else-if="
                    item.key === 'contracts'
                  "
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    d="
                      M14 2H6
                      a2 2 0 0 0-2 2v16
                      a2 2 0 0 0 2 2h12
                      a2 2 0 0 0 2-2V8z
                    "
                  />

                  <polyline
                    points="14 2 14 8 20 8"
                  />

                  <line
                    x1="8"
                    y1="13"
                    x2="16"
                    y2="13"
                  />

                  <line
                    x1="8"
                    y1="17"
                    x2="16"
                    y2="17"
                  />
                </svg>

                <!-- Servicios -->
                <svg
                  v-else-if="
                    item.key === 'services'
                  "
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    d="
                      M14.7 6.3
                      a1 1 0 0 0 0 1.4
                      l1.6 1.6
                      a1 1 0 0 0 1.4 0
                      l3.8-3.8
                      a6 6 0 0 1-7.9 7.9
                      l-6.9 6.9
                      a2.1 2.1 0 0 1-3-3
                      l6.9-6.9
                      a6 6 0 0 1 7.9-7.9z
                    "
                  />
                </svg>

                <!-- Taller -->
                <svg
                  v-else-if="
                    item.key === 'repairs'
                  "
                  class="workshop-icon"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    d="
                      M8 7V5
                      a2 2 0 0 1 2-2h4
                      a2 2 0 0 1 2 2v2
                    "
                  />

                  <rect
                    x="3"
                    y="7"
                    width="18"
                    height="13"
                    rx="2"
                  />

                  <path d="M3 12h18" />
                  <path d="M9 12v2h6v-2" />

                  <path
                    d="
                      M15.8 15.2
                      a2.1 2.1 0 0 1-2.7 2.7
                      l-2.6 2.6
                    "
                  />

                  <path d="M14.1 14.1l1.8 1.8" />
                </svg>

                <!-- Configuración -->
                <svg
                  v-else-if="
                    item.key === 'settings'
                  "
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle
                    cx="12"
                    cy="12"
                    r="3"
                  />

                  <path
                    d="
                      M19.4 15
                      a1.7 1.7 0 0 0 .34 1.88
                      l.06.06
                      a2 2 0 1 1-2.83 2.83
                      l-.06-.06
                      a1.7 1.7 0 0 0-1.88-.34
                      a1.7 1.7 0 0 0-1.03 1.56V21
                      a2 2 0 1 1-4 0v-.09
                      A1.7 1.7 0 0 0 9 19.35
                      a1.7 1.7 0 0 0-1.88.34
                      l-.06.06
                      a2 2 0 1 1-2.83-2.83
                      l.06-.06
                      A1.7 1.7 0 0 0 4.63 15
                      a1.7 1.7 0 0 0-1.56-1H3
                      a2 2 0 1 1 0-4h.09
                      A1.7 1.7 0 0 0 4.65 9
                      a1.7 1.7 0 0 0-.34-1.88
                      l-.06-.06
                      a2 2 0 1 1 2.83-2.83
                      l.06.06
                      A1.7 1.7 0 0 0 9 4.63h.02
                      A1.7 1.7 0 0 0 10 3.07V3
                      a2 2 0 1 1 4 0v.09
                      A1.7 1.7 0 0 0 15 4.65
                      a1.7 1.7 0 0 0 1.88-.34
                      l.06-.06
                      a2 2 0 1 1 2.83 2.83
                      l-.06.06
                      A1.7 1.7 0 0 0 19.37 9v.02
                      A1.7 1.7 0 0 0 20.93 10H21
                      a2 2 0 1 1 0 4h-.09
                      A1.7 1.7 0 0 0 19.4 15z
                    "
                  />
                </svg>

                <!-- Seguridad -->
                <svg
                  v-else
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    d="
                      M12 22s8-4 8-10V5
                      l-8-3-8 3v7
                      c0 6 8 10 8 10z
                    "
                  />

                  <path
                    d="m9 12 2 2 4-4"
                  />
                </svg>
              </span>

              <span class="radial-item-information">
                <strong>{{ item.label }}</strong>
                <small>{{ item.description }}</small>
              </span>

              </button>

              <Transition name="workshop-submenu">
                <div
                  v-if="isSubmenuOpen(item)"
                  class="workshop-submenu"
                >
                  <button
                    v-for="child in item.children"
                    :key="child.path"
                    type="button"
                    :class="{
                      active:
                        route.path === child.path ||
                        route.path.startsWith(
                          `${child.path}/`
                        ),
                    }"
                    @click.stop="
                      selectSubmenuItem(child)
                    "
                  >
                    <span class="workshop-submenu-icon">
                      <svg
                        v-if="child.label === 'Reparaciones'"
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                      >
                        <path
                          d="
                            M14.7 6.3
                            a1 1 0 0 0 0 1.4
                            l1.6 1.6
                            a1 1 0 0 0 1.4 0
                            l3.8-3.8
                            a6 6 0 0 1-7.9 7.9
                            l-6.9 6.9
                            a2.1 2.1 0 0 1-3-3
                            l6.9-6.9
                            a6 6 0 0 1 7.9-7.9z
                          "
                        />
                      </svg>

                      <svg
                        v-else-if="child.label === 'Pedidos'"
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                      >
                        <path
                          d="
                            M9 5H6
                            a2 2 0 0 0-2 2v13
                            a2 2 0 0 0 2 2h12
                            a2 2 0 0 0 2-2V7
                            a2 2 0 0 0-2-2h-3
                          "
                        />

                        <rect
                          x="9"
                          y="3"
                          width="6"
                          height="4"
                          rx="1"
                        />

                        <path d="M8 12h8" />
                        <path d="M8 16h5" />
                      </svg>

                      <svg
                        v-else
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                      >
                        <circle
                          cx="12"
                          cy="12"
                          r="3"
                        />

                        <path
                          d="
                            M19.4 15
                            a1.7 1.7 0 0 0 .34 1.88
                            l.06.06
                            a2 2 0 1 1-2.83 2.83
                            l-.06-.06
                            a1.7 1.7 0 0 0-1.88-.34
                            a1.7 1.7 0 0 0-1.03 1.56V21
                            a2 2 0 1 1-4 0v-.09
                            A1.7 1.7 0 0 0 9 19.35
                            a1.7 1.7 0 0 0-1.88.34
                            l-.06.06
                            a2 2 0 1 1-2.83-2.83
                            l.06-.06
                            A1.7 1.7 0 0 0 4.63 15
                            a1.7 1.7 0 0 0-1.56-1H3
                            a2 2 0 1 1 0-4h.09
                            A1.7 1.7 0 0 0 4.65 9
                            a1.7 1.7 0 0 0-.34-1.88
                            l-.06-.06
                            a2 2 0 1 1 2.83-2.83
                            l.06.06
                            A1.7 1.7 0 0 0 9 4.63h.02
                            A1.7 1.7 0 0 0 10 3.07V3
                            a2 2 0 1 1 4 0v.09
                            A1.7 1.7 0 0 0 15 4.65
                            a1.7 1.7 0 0 0 1.88-.34
                            l.06-.06
                            a2 2 0 1 1 2.83 2.83
                            l-.06.06
                            A1.7 1.7 0 0 0 19.37 9v.02
                            A1.7 1.7 0 0 0 20.93 10H21
                            a2 2 0 1 1 0 4h-.09
                            A1.7 1.7 0 0 0 19.4 15z
                          "
                        />
                      </svg>
                    </span>

                    <span>{{ child.label }}</span>
                  </button>
                </div>
              </Transition>
            </div>
          </div>
        </div>

        <div class="page-information">
          <span>Sistema de Taller</span>

          <h1>
            {{ route.meta.title || "Dashboard" }}
          </h1>
        </div>

        <div class="topbar-actions">
          <button
            class="notification-button"
            type="button"
            aria-label="Notificaciones"
          >
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="
                  M18 8
                  a6 6 0 0 0-12 0
                  c0 7-3 7-3 9h18
                  c0-2-3-2-3-9
                "
              />

              <path
                d="
                  M13.73 21
                  a2 2 0 0 1-3.46 0
                "
              />
            </svg>

            <small></small>
          </button>

          <div class="profile-container">
            <button
              class="profile-button"
              type="button"
              :aria-expanded="profileOpen"
              @click.stop="toggleProfileMenu"
            >
              <span class="profile-avatar">
                {{ initials }}
              </span>

              <span class="profile-information">
                <strong>{{ userName }}</strong>

                <small>
                  {{
                    user?.is_superuser ||
                    user?.is_staff
                      ? "Administrador"
                      : "Usuario"
                  }}
                </small>
              </span>

              <span
                class="profile-arrow"
                :class="{
                  open: profileOpen,
                }"
              >
                ▾
              </span>
            </button>

            <Transition name="profile-menu">
              <div
                v-if="profileOpen"
                class="profile-menu"
              >
                <div class="profile-menu-header">
                  <strong>{{ userName }}</strong>
                  <span>{{ user?.email }}</span>
                </div>

                <button
                  type="button"
                  @click="showComingSoon"
                >
                  Mi perfil
                </button>

                <RouterLink
                  class="profile-menu-link"
                  to="/seguridad"
                  @click="closeProfileMenu"
                >
                  Seguridad
                </RouterLink>

                <button
                  class="logout-option"
                  type="button"
                  @click="logout"
                >
                  Cerrar sesión
                </button>
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </header>

    <main class="page-content">
      <RouterView />
    </main>
  </div>
</template>