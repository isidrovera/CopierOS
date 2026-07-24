<script setup>
import {
  computed,
  onMounted,
  ref,
} from "vue"

import {
  useRouter,
} from "vue-router"

import {
  archiveUser,
  getUsers,
  restoreUser,
} from "../../services/users.service"

const router = useRouter()

const users = ref([])
const loading = ref(false)
const errorMessage = ref("")
const successMessage = ref("")

const search = ref("")
const includeArchived = ref(false)
const selectedStatus = ref("")

let searchTimeout = null

const totalUsers = computed(() => users.value.length)

const activeUsers = computed(() => {
  return users.value.filter(
    (user) => user.is_active && !user.is_archived
  ).length
})

const archivedUsers = computed(() => {
  return users.value.filter(
    (user) => user.is_archived
  ).length
})

async function loadUsers() {
  loading.value = true
  errorMessage.value = ""

  try {
    const isActive =
      selectedStatus.value === "active"
        ? true
        : selectedStatus.value === "inactive"
          ? false
          : ""

    const response = await getUsers({
      search: search.value,
      includeArchived: includeArchived.value,
      isActive,
    })

    users.value = Array.isArray(response)
      ? response
      : response.results || []
  } catch (error) {
    users.value = []

    errorMessage.value =
      error.message ||
      "No se pudieron cargar los usuarios."
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  window.clearTimeout(searchTimeout)

  searchTimeout = window.setTimeout(() => {
    loadUsers()
  }, 350)
}

async function goToCreate() {
  await router.push({
    name: "user-create",
  })
}

async function goToEdit(user) {
  await router.push({
    name: "user-edit",
    params: {
      id: user.id,
    },
  })
}

async function handleArchive(user) {
  const reason = window.prompt(
    `Indica el motivo para archivar a ${getUserName(user)}:`
  )

  if (reason === null) {
    return
  }

  const confirmed = window.confirm(
    `¿Confirmas que deseas archivar a ${getUserName(user)}?`
  )

  if (!confirmed) {
    return
  }

  errorMessage.value = ""
  successMessage.value = ""

  try {
    await archiveUser(
      user.id,
      reason.trim()
    )

    successMessage.value =
      "Usuario archivado correctamente."

    await loadUsers()
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo archivar el usuario."
  }
}

async function handleRestore(user) {
  const confirmed = window.confirm(
    `¿Confirmas que deseas restaurar a ${getUserName(user)}?`
  )

  if (!confirmed) {
    return
  }

  errorMessage.value = ""
  successMessage.value = ""

  try {
    await restoreUser(user.id)

    successMessage.value =
      "Usuario restaurado correctamente."

    await loadUsers()
  } catch (error) {
    errorMessage.value =
      error.message ||
      "No se pudo restaurar el usuario."
  }
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

function getInitials(user) {
  const name = getUserName(user)
  const words = name.split(" ").filter(Boolean)

  if (!words.length) {
    return "U"
  }

  if (words.length === 1) {
    return words[0]
      .charAt(0)
      .toUpperCase()
  }

  return (
    words[0].charAt(0) +
    words[1].charAt(0)
  ).toUpperCase()
}

function formatDate(value) {
  if (!value) {
    return "Sin registro"
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return "Sin registro"
  }

  return new Intl.DateTimeFormat(
    "es-PE",
    {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }
  ).format(date)
}

onMounted(() => {
  loadUsers()
})
</script>

<template>
  <section class="users-page">
    <header class="page-header">
      <div>
        <span class="page-kicker">
          Administración
        </span>

        <h2>Usuarios</h2>

        <p>
          Administra los usuarios, accesos y estados
          de Copier OS.
        </p>
      </div>

      <button
        class="primary-button"
        type="button"
        @click="goToCreate"
      >
        <span>＋</span>
        Nuevo usuario
      </button>
    </header>

    <div class="summary-grid">
      <article class="summary-card">
        <span class="summary-icon">
          ◉
        </span>

        <div>
          <small>Total mostrados</small>
          <strong>{{ totalUsers }}</strong>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon success">
          ✓
        </span>

        <div>
          <small>Activos</small>
          <strong>{{ activeUsers }}</strong>
        </div>
      </article>

      <article class="summary-card">
        <span class="summary-icon archived">
          ▣
        </span>

        <div>
          <small>Archivados</small>
          <strong>{{ archivedUsers }}</strong>
        </div>
      </article>
    </div>

    <div class="users-panel">
      <div class="filters">
        <label class="search-field">
          <span>⌕</span>

          <input
            v-model="search"
            type="search"
            placeholder="Buscar por nombre, DNI, correo, cargo o área"
            @input="handleSearch"
          />
        </label>

        <select
          v-model="selectedStatus"
          class="status-filter"
          @change="loadUsers"
        >
          <option value="">
            Todos los estados
          </option>

          <option value="active">
            Activos
          </option>

          <option value="inactive">
            Inactivos
          </option>
        </select>

        <label class="archive-filter">
          <input
            v-model="includeArchived"
            type="checkbox"
            @change="loadUsers"
          />

          <span>Mostrar archivados</span>
        </label>

        <button
          class="refresh-button"
          type="button"
          :disabled="loading"
          @click="loadUsers"
        >
          ↻
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
        <span class="spinner"></span>
        Cargando usuarios...
      </div>

      <div
        v-else-if="!users.length"
        class="empty-state"
      >
        <span>◎</span>

        <strong>
          No se encontraron usuarios
        </strong>

        <p>
          Cambia los filtros o registra un nuevo
          usuario.
        </p>

        <button
          class="empty-create-button"
          type="button"
          @click="goToCreate"
        >
          Crear usuario
        </button>
      </div>

      <div
        v-else
        class="table-container"
      >
        <table>
          <thead>
            <tr>
              <th>Usuario</th>
              <th>DNI</th>
              <th>Área / cargo</th>
              <th>Empresa</th>
              <th>Estado</th>
              <th>Último acceso</th>

              <th class="actions-column">
                Acciones
              </th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="user in users"
              :key="user.id"
              :class="{
                'archived-row': user.is_archived,
              }"
            >
              <td>
                <div class="user-cell">
                  <img
                    v-if="user.photo_url"
                    class="user-avatar"
                    :src="user.photo_url"
                    :alt="getUserName(user)"
                  />

                  <span
                    v-else
                    class="user-avatar user-initials"
                  >
                    {{ getInitials(user) }}
                  </span>

                  <div class="user-information">
                    <strong>
                      {{ getUserName(user) }}
                    </strong>

                    <span>{{ user.email }}</span>
                  </div>
                </div>
              </td>

              <td>
                {{ user.dni || "Sin DNI" }}
              </td>

              <td>
                <div class="work-information">
                  <strong>
                    {{
                      user.job_title ||
                      "Sin cargo"
                    }}
                  </strong>

                  <span>
                    {{
                      user.department_name ||
                      "Sin área"
                    }}
                  </span>
                </div>
              </td>

              <td>
                {{
                  user.company_name ||
                  "Sin empresa"
                }}
              </td>

              <td>
                <div class="status-container">
                  <span
                    v-if="user.is_archived"
                    class="status-badge archived"
                  >
                    Archivado
                  </span>

                  <span
                    v-else-if="user.is_active"
                    class="status-badge active"
                  >
                    Activo
                  </span>

                  <span
                    v-else
                    class="status-badge inactive"
                  >
                    Inactivo
                  </span>

                  <span
                    v-if="user.is_staff"
                    class="staff-badge"
                  >
                    Administrador
                  </span>

                  <span
                    v-if="user.is_verified"
                    class="verified-badge"
                    title="Usuario verificado"
                  >
                    ✓ Verificado
                  </span>
                </div>
              </td>

              <td>
                {{ formatDate(user.last_login) }}
              </td>

              <td>
                <div class="row-actions">
                  <button
                    class="action-button edit"
                    type="button"
                    :disabled="user.is_archived"
                    @click="goToEdit(user)"
                  >
                    Editar
                  </button>

                  <button
                    v-if="!user.is_archived"
                    class="action-button archive"
                    type="button"
                    @click="handleArchive(user)"
                  >
                    Archivar
                  </button>

                  <button
                    v-else
                    class="action-button restore"
                    type="button"
                    @click="handleRestore(user)"
                  >
                    Restaurar
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<style scoped>
button,
input,
select {
  font: inherit;
}

.users-page {
  display: flex;
  flex-direction: column;
  gap: 22px;
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
  color: #2c82a8;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.page-header h2 {
  margin: 0;
  color: #17283f;
  font-size: 28px;
}

.page-header p {
  margin: 8px 0 0;
  color: #768396;
  font-size: 14px;
}

.primary-button {
  min-height: 43px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 10px 17px;
  border: 0;
  border-radius: 10px;
  background: #277fa6;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.primary-button:hover {
  background: #216f91;
}

.summary-grid {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 18px;
  border: 1px solid #e3e9ef;
  border-radius: 14px;
  background: white;
}

.summary-icon {
  width: 44px;
  height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: #e9f4f8;
  color: #277fa6;
  font-size: 20px;
  font-weight: 800;
}

.summary-icon.success {
  background: #eaf7ef;
  color: #288653;
}

.summary-icon.archived {
  background: #f0f2f5;
  color: #687586;
}

.summary-card small,
.summary-card strong {
  display: block;
}

.summary-card small {
  margin-bottom: 4px;
  color: #8793a1;
  font-size: 12px;
}

.summary-card strong {
  color: #1b2c42;
  font-size: 24px;
}

.users-panel {
  overflow: hidden;
  border: 1px solid #e2e8ee;
  border-radius: 15px;
  background: white;
}

.filters {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 17px;
  border-bottom: 1px solid #edf1f4;
}

.search-field {
  min-height: 42px;
  display: flex;
  flex: 1;
  align-items: center;
  gap: 8px;
  padding: 0 13px;
  border: 1px solid #dce4eb;
  border-radius: 10px;
  background: #fbfcfd;
}

.search-field span {
  color: #8a96a4;
  font-size: 19px;
}

.search-field input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: #25364b;
}

.search-field input::placeholder {
  color: #9aa5b0;
}

.status-filter {
  min-height: 42px;
  padding: 0 12px;
  border: 1px solid #dce4eb;
  border-radius: 10px;
  outline: none;
  background: white;
  color: #526174;
}

.archive-filter {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #647286;
  font-size: 13px;
  white-space: nowrap;
}

.archive-filter input {
  width: 16px;
  height: 16px;
  accent-color: #277fa6;
}

.refresh-button {
  min-height: 42px;
  padding: 0 13px;
  border: 1px solid #dce4eb;
  border-radius: 10px;
  background: white;
  color: #42708a;
  cursor: pointer;
}

.refresh-button:hover {
  background: #f3f7f9;
}

.refresh-button:disabled {
  opacity: 0.6;
  cursor: wait;
}

.message {
  margin: 16px 17px 0;
  padding: 11px 13px;
  border-radius: 9px;
  font-size: 13px;
}

.success-message {
  border: 1px solid #c8ead4;
  background: #edf9f1;
  color: #287344;
}

.error-message {
  border: 1px solid #f0cccc;
  background: #fff1f1;
  color: #a43f3f;
}

.loading-state,
.empty-state {
  min-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7a8796;
}

.loading-state {
  gap: 10px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #d9e5eb;
  border-top-color: #277fa6;
  border-radius: 50%;
  animation: rotate 0.8s linear infinite;
}

@keyframes rotate {
  to {
    transform: rotate(360deg);
  }
}

.empty-state {
  flex-direction: column;
  padding: 40px 20px;
  text-align: center;
}

.empty-state > span {
  margin-bottom: 12px;
  color: #9aa6b2;
  font-size: 42px;
}

.empty-state strong {
  color: #34445a;
  font-size: 16px;
}

.empty-state p {
  margin: 7px 0 16px;
  font-size: 13px;
}

.empty-create-button {
  min-height: 39px;
  padding: 0 14px;
  border: 0;
  border-radius: 9px;
  background: #277fa6;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 14px 16px;
  border-bottom: 1px solid #edf1f4;
  text-align: left;
  vertical-align: middle;
}

th {
  background: #fafbfd;
  color: #7b8797;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.05em;
  white-space: nowrap;
  text-transform: uppercase;
}

td {
  color: #4b5a6e;
  font-size: 13px;
}

tbody tr:hover {
  background: #fafcfd;
}

tbody tr:last-child td {
  border-bottom: 0;
}

.archived-row {
  opacity: 0.72;
}

.user-cell {
  min-width: 220px;
  display: flex;
  align-items: center;
  gap: 11px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border-radius: 11px;
  object-fit: cover;
}

.user-initials {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #e7f2f7;
  color: #257ca3;
  font-weight: 800;
}

.user-information,
.work-information {
  min-width: 0;
}

.user-information strong,
.user-information span,
.work-information strong,
.work-information span {
  display: block;
}

.user-information strong,
.work-information strong {
  color: #2d3c50;
  font-size: 13px;
}

.user-information span,
.work-information span {
  margin-top: 3px;
  color: #8792a0;
  font-size: 11px;
}

.status-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 5px;
}

.status-badge,
.staff-badge,
.verified-badge {
  display: inline-flex;
  padding: 5px 8px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
}

.status-badge.active {
  background: #e7f6ed;
  color: #277d4c;
}

.status-badge.inactive {
  background: #fff0e8;
  color: #b45e32;
}

.status-badge.archived {
  background: #eceff3;
  color: #657181;
}

.staff-badge {
  background: #e8f0fb;
  color: #3c69a3;
}

.verified-badge {
  background: #eaf7f1;
  color: #29825c;
}

.actions-column {
  text-align: right;
}

.row-actions {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}

.action-button {
  padding: 7px 9px;
  border: 1px solid #dce4ea;
  border-radius: 8px;
  background: white;
  color: #4e6073;
  font-size: 11px;
  cursor: pointer;
}

.action-button:hover {
  background: #f3f7f9;
}

.action-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.action-button.edit {
  border-color: #c7dfeb;
  color: #277fa6;
}

.action-button.archive {
  border-color: #f0d2c6;
  color: #ad5c3b;
}

.action-button.restore {
  border-color: #c8e4d3;
  color: #2b8050;
}

@media (max-width: 900px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .filters {
    align-items: stretch;
    flex-direction: column;
  }

  .archive-filter {
    min-height: 34px;
  }
}

@media (max-width: 620px) {
  .page-header {
    flex-direction: column;
  }

  .primary-button {
    width: 100%;
  }
}
</style>