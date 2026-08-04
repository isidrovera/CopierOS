<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from "vue"

import MonitoringEmptyState from "../../components/monitoring/MonitoringEmptyState.vue"
import MonitoringStatusBadge from "../../components/monitoring/MonitoringStatusBadge.vue"
import MonitoringTabs from "../../components/monitoring/MonitoringTabs.vue"

import {
  archiveInstallationToken,
  createInstallationToken,
  getInstallationTokens,
  normalizeList,
  restoreInstallationToken,
  revokeInstallationToken,
} from "../../services/monitoring.service"

import "./MonitoringInstallationTokensView.css"


const loading = ref(true)
const saving = ref(false)
const copying = ref(false)
const busyTokenId = ref("")

const error = ref("")
const success = ref("")

const generatedToken = ref("")
const tokens = ref([])

const showCreateForm = ref(true)
const showRevokeModal = ref(false)
const showArchiveModal = ref(false)

const selectedToken = ref(null)

const revokeReason = ref("")
const archiveReason = ref("")


const filters = reactive({
  search: "",
  availability: "all",
  includeArchived: false,
})


const form = reactive({
  customer: "",
  branch: "",
  name: "",
  expires_at: "",
  maximum_uses: 1,
  notes: "",
})


const filteredTokens = computed(() => {
  const search = filters.search
    .trim()
    .toLowerCase()

  return tokens.value.filter(
    (item) => {
      if (
        !filters.includeArchived &&
        item.archived_at
      ) {
        return false
      }

      if (
        filters.availability === "available" &&
        !item.can_be_used
      ) {
        return false
      }

      if (
        filters.availability === "unavailable" &&
        item.can_be_used
      ) {
        return false
      }

      if (
        filters.availability === "revoked" &&
        !item.revoked_at
      ) {
        return false
      }

      if (
        filters.availability === "expired" &&
        !isExpired(item)
      ) {
        return false
      }

      if (!search) {
        return true
      }

      const values = [
        item.name,
        item.token_prefix,
        item.customer_name,
        item.customer,
        item.branch_name,
        item.branch,
        item.notes,
      ]

      return values.some(
        (value) =>
          String(value || "")
            .toLowerCase()
            .includes(search)
      )
    }
  )
})


const tokenStatistics = computed(() => {
  const total = tokens.value.length

  const available = tokens.value.filter(
    (item) => item.can_be_used
  ).length

  const revoked = tokens.value.filter(
    (item) => Boolean(item.revoked_at)
  ).length

  const expired = tokens.value.filter(
    (item) => isExpired(item)
  ).length

  return {
    total,
    available,
    revoked,
    expired,
  }
})


function clearMessages() {
  error.value = ""
  success.value = ""
}


function showSuccess(message) {
  error.value = ""
  success.value = message

  window.setTimeout(
    () => {
      if (
        success.value === message
      ) {
        success.value = ""
      }
    },
    5000
  )
}


function formatDate(value) {
  if (!value) {
    return "Sin vencimiento"
  }

  const date = new Date(value)

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return String(value)
  }

  return new Intl.DateTimeFormat(
    "es-PE",
    {
      dateStyle: "medium",
      timeStyle: "short",
    }
  ).format(date)
}


function formatShortDate(value) {
  if (!value) {
    return "—"
  }

  const date = new Date(value)

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return String(value)
  }

  return new Intl.DateTimeFormat(
    "es-PE",
    {
      dateStyle: "short",
      timeStyle: "short",
    }
  ).format(date)
}


function isExpired(item) {
  if (!item?.expires_at) {
    return false
  }

  const expirationDate =
    new Date(item.expires_at)

  if (
    Number.isNaN(
      expirationDate.getTime()
    )
  ) {
    return false
  }

  return (
    expirationDate.getTime() <
    Date.now()
  )
}


function getTokenState(item) {
  if (item.archived_at) {
    return {
      status: "archived",
      label: "Archivado",
    }
  }

  if (item.revoked_at) {
    return {
      status: "revoked",
      label: "Revocado",
    }
  }

  if (isExpired(item)) {
    return {
      status: "expired",
      label: "Vencido",
    }
  }

  if (
    Number(item.used_count || 0) >=
    Number(item.maximum_uses || 0)
  ) {
    return {
      status: "used",
      label: "Usos agotados",
    }
  }

  if (item.can_be_used) {
    return {
      status: "active",
      label: "Disponible",
    }
  }

  return {
    status: "inactive",
    label: "No disponible",
  }
}


function getUsagePercentage(item) {
  const maximum =
    Number(item.maximum_uses || 0)

  const used =
    Number(item.used_count || 0)

  if (maximum <= 0) {
    return 0
  }

  return Math.max(
    0,
    Math.min(
      100,
      (used / maximum) * 100
    )
  )
}


function resetForm() {
  form.customer = ""
  form.branch = ""
  form.name = ""
  form.expires_at = ""
  form.maximum_uses = 1
  form.notes = ""
}


function validateForm() {
  if (!form.customer.trim()) {
    throw new Error(
      "Selecciona o escribe el UUID del cliente."
    )
  }

  if (!form.name.trim()) {
    throw new Error(
      "Ingresa un nombre para identificar el token."
    )
  }

  if (
    !Number.isInteger(
      Number(form.maximum_uses)
    ) ||
    Number(form.maximum_uses) < 1
  ) {
    throw new Error(
      "Los usos máximos deben ser como mínimo 1."
    )
  }

  if (form.expires_at) {
    const expirationDate =
      new Date(form.expires_at)

    if (
      Number.isNaN(
        expirationDate.getTime()
      )
    ) {
      throw new Error(
        "La fecha de vencimiento no es válida."
      )
    }

    if (
      expirationDate.getTime() <=
      Date.now()
    ) {
      throw new Error(
        "La fecha de vencimiento debe ser futura."
      )
    }
  }
}


async function loadTokens() {
  loading.value = true
  error.value = ""

  try {
    const data =
      await getInstallationTokens({
        include_archived: true,
      })

    tokens.value =
      normalizeList(data)
  } catch (exception) {
    error.value =
      exception.message
  } finally {
    loading.value = false
  }
}


async function submitToken() {
  saving.value = true
  clearMessages()
  generatedToken.value = ""

  try {
    validateForm()

    const payload = {
      customer:
        form.customer.trim(),

      branch:
        form.branch.trim() ||
        null,

      name:
        form.name.trim(),

      expires_at:
        form.expires_at
          ? new Date(
              form.expires_at
            ).toISOString()
          : null,

      maximum_uses:
        Number(
          form.maximum_uses
        ),

      notes:
        form.notes.trim(),
    }

    const data =
      await createInstallationToken(
        payload
      )

    generatedToken.value =
      data.token ||
      data.raw_token ||
      ""

    showSuccess(
      "Token creado correctamente. Guárdalo ahora porque solo se mostrará una vez."
    )

    resetForm()

    await loadTokens()
  } catch (exception) {
    error.value =
      exception.message
  } finally {
    saving.value = false
  }
}


async function copyText(value) {
  if (!value) {
    return
  }

  copying.value = true
  clearMessages()

  try {
    if (
      navigator.clipboard &&
      window.isSecureContext
    ) {
      await navigator.clipboard.writeText(
        value
      )
    } else {
      const textarea =
        document.createElement(
          "textarea"
        )

      textarea.value = value
      textarea.style.position = "fixed"
      textarea.style.opacity = "0"

      document.body.appendChild(
        textarea
      )

      textarea.focus()
      textarea.select()

      document.execCommand(
        "copy"
      )

      document.body.removeChild(
        textarea
      )
    }

    showSuccess(
      "Token copiado al portapapeles."
    )
  } catch {
    error.value =
      "No se pudo copiar automáticamente. Selecciona el token y cópialo manualmente."
  } finally {
    copying.value = false
  }
}


function openRevokeModal(item) {
  selectedToken.value = item

  revokeReason.value =
    "Revocado desde Copier OS"

  showRevokeModal.value = true
}


function closeRevokeModal() {
  if (busyTokenId.value) {
    return
  }

  showRevokeModal.value = false
  selectedToken.value = null
  revokeReason.value = ""
}


async function confirmRevoke() {
  if (!selectedToken.value) {
    return
  }

  if (!revokeReason.value.trim()) {
    error.value =
      "Ingresa el motivo de revocación."

    return
  }

  busyTokenId.value =
    selectedToken.value.id

  clearMessages()

  try {
    await revokeInstallationToken(
      selectedToken.value.id,
      revokeReason.value.trim()
    )

    closeRevokeModal()

    showSuccess(
      "Token revocado correctamente."
    )

    await loadTokens()
  } catch (exception) {
    error.value =
      exception.message
  } finally {
    busyTokenId.value = ""
  }
}


function openArchiveModal(item) {
  selectedToken.value = item

  archiveReason.value =
    "Archivado desde Copier OS"

  showArchiveModal.value = true
}


function closeArchiveModal() {
  if (busyTokenId.value) {
    return
  }

  showArchiveModal.value = false
  selectedToken.value = null
  archiveReason.value = ""
}


async function confirmArchive() {
  if (!selectedToken.value) {
    return
  }

  busyTokenId.value =
    selectedToken.value.id

  clearMessages()

  try {
    await archiveInstallationToken(
      selectedToken.value.id,
      archiveReason.value.trim()
    )

    closeArchiveModal()

    showSuccess(
      "Token archivado correctamente."
    )

    await loadTokens()
  } catch (exception) {
    error.value =
      exception.message
  } finally {
    busyTokenId.value = ""
  }
}


async function restoreToken(item) {
  busyTokenId.value = item.id
  clearMessages()

  try {
    await restoreInstallationToken(
      item.id
    )

    showSuccess(
      "Token restaurado correctamente."
    )

    await loadTokens()
  } catch (exception) {
    error.value =
      exception.message
  } finally {
    busyTokenId.value = ""
  }
}


onMounted(
  loadTokens
)
</script>

<template>
  <section class="installation-token-page">
    <header class="token-page-header">
      <div>
        <span class="token-page-eyebrow">
          Monitoreo
        </span>

        <h1 class="token-page-title">
          Tokens de instalación
        </h1>

        <p class="token-page-subtitle">
          Genera credenciales temporales para registrar
          agentes de monitoreo por cliente y sede.
        </p>
      </div>

      <div class="token-header-actions">
        <button
          class="token-button token-button-secondary"
          type="button"
          :disabled="loading"
          @click="loadTokens"
        >
          <span>↻</span>

          Actualizar
        </button>

        <button
          class="token-button token-button-primary"
          type="button"
          @click="
            showCreateForm =
              !showCreateForm
          "
        >
          <span>
            {{ showCreateForm ? "−" : "+" }}
          </span>

          {{
            showCreateForm
              ? "Ocultar formulario"
              : "Nuevo token"
          }}
        </button>
      </div>
    </header>

    <MonitoringTabs />

    <div
      v-if="error"
      class="token-message token-message-error"
    >
      <span>{{ error }}</span>

      <button
        type="button"
        @click="error = ''"
      >
        ×
      </button>
    </div>

    <div
      v-if="success"
      class="token-message token-message-success"
    >
      <span>{{ success }}</span>

      <button
        type="button"
        @click="success = ''"
      >
        ×
      </button>
    </div>

    <section class="token-statistics-grid">
      <article class="token-stat-card">
        <span>Total</span>

        <strong>
          {{ tokenStatistics.total }}
        </strong>

        <small>
          Tokens registrados
        </small>
      </article>

      <article class="token-stat-card token-stat-available">
        <span>Disponibles</span>

        <strong>
          {{ tokenStatistics.available }}
        </strong>

        <small>
          Pueden utilizarse
        </small>
      </article>

      <article class="token-stat-card token-stat-revoked">
        <span>Revocados</span>

        <strong>
          {{ tokenStatistics.revoked }}
        </strong>

        <small>
          Acceso cancelado
        </small>
      </article>

      <article class="token-stat-card token-stat-expired">
        <span>Vencidos</span>

        <strong>
          {{ tokenStatistics.expired }}
        </strong>

        <small>
          Fuera de vigencia
        </small>
      </article>
    </section>

    <article
      v-if="generatedToken"
      class="token-panel generated-token-panel"
    >
      <header class="token-panel-header">
        <div>
          <span class="token-panel-kicker">
            Credencial generada
          </span>

          <h2>
            Guarda este token ahora
          </h2>

          <p>
            Por seguridad, el valor completo no volverá
            a mostrarse.
          </p>
        </div>

        <button
          class="token-button token-button-copy"
          type="button"
          :disabled="copying"
          @click="copyText(generatedToken)"
        >
          {{
            copying
              ? "Copiando..."
              : "Copiar token"
          }}
        </button>
      </header>

      <div class="generated-token-value">
        <code>
          {{ generatedToken }}
        </code>
      </div>

      <div class="generated-token-warning">
        <span>!</span>

        <p>
          Entrega este token únicamente a la persona
          responsable de instalar el agente.
        </p>
      </div>
    </article>

    <article
      v-if="showCreateForm"
      class="token-panel"
    >
      <header class="token-panel-header">
        <div>
          <span class="token-panel-kicker">
            Registro
          </span>

          <h2>
            Nuevo token de instalación
          </h2>

          <p>
            Define el cliente, la sede y los límites
            de uso.
          </p>
        </div>
      </header>

      <form
        class="token-form"
        @submit.prevent="submitToken"
      >
        <div class="token-form-grid">
          <label class="token-field">
            <span>
              UUID del cliente
              <strong>*</strong>
            </span>

            <input
              v-model.trim="form.customer"
              type="text"
              required
              autocomplete="off"
              placeholder="b83016c7-59cd-4b45-a307-228fd990813e"
            />

            <small>
              Cliente al que pertenecerá el agente.
            </small>
          </label>

          <label class="token-field">
            <span>
              UUID de la sede
            </span>

            <input
              v-model.trim="form.branch"
              type="text"
              autocomplete="off"
              placeholder="Opcional"
            />

            <small>
              Déjalo vacío para una instalación sin sede.
            </small>
          </label>

          <label class="token-field">
            <span>
              Nombre del token
              <strong>*</strong>
            </span>

            <input
              v-model.trim="form.name"
              type="text"
              required
              maxlength="255"
              placeholder="Agente sede principal"
            />

            <small>
              Usa un nombre que permita reconocer la instalación.
            </small>
          </label>

          <label class="token-field">
            <span>
              Fecha de vencimiento
            </span>

            <input
              v-model="form.expires_at"
              type="datetime-local"
            />

            <small>
              Sin fecha significa que no vence automáticamente.
            </small>
          </label>

          <label class="token-field">
            <span>
              Usos máximos
              <strong>*</strong>
            </span>

            <input
              v-model.number="form.maximum_uses"
              type="number"
              min="1"
              step="1"
              required
            />

            <small>
              Normalmente debe ser 1 por instalación.
            </small>
          </label>

          <label class="token-field token-field-full">
            <span>
              Observaciones
            </span>

            <textarea
              v-model.trim="form.notes"
              rows="4"
              maxlength="1000"
              placeholder="Detalles de la instalación, responsable o ubicación..."
            ></textarea>
          </label>
        </div>

        <footer class="token-form-footer">
          <button
            class="token-button token-button-secondary"
            type="button"
            :disabled="saving"
            @click="resetForm"
          >
            Limpiar
          </button>

          <button
            class="token-button token-button-primary"
            type="submit"
            :disabled="saving"
          >
            {{
              saving
                ? "Creando token..."
                : "Crear token"
            }}
          </button>
        </footer>
      </form>
    </article>

    <article class="token-panel">
      <header class="token-panel-header token-list-header">
        <div>
          <span class="token-panel-kicker">
            Historial
          </span>

          <h2>
            Tokens registrados
          </h2>

          <p>
            Consulta disponibilidad, uso, vencimiento
            y revocación.
          </p>
        </div>

        <span class="token-result-count">
          {{ filteredTokens.length }}
          resultados
        </span>
      </header>

      <div class="token-filter-bar">
        <label class="token-search-field">
          <span>⌕</span>

          <input
            v-model.trim="filters.search"
            type="search"
            placeholder="Buscar por nombre, prefijo, cliente o sede..."
          />
        </label>

        <label class="token-filter-field">
          <span>Estado</span>

          <select
            v-model="filters.availability"
          >
            <option value="all">
              Todos
            </option>

            <option value="available">
              Disponibles
            </option>

            <option value="unavailable">
              No disponibles
            </option>

            <option value="revoked">
              Revocados
            </option>

            <option value="expired">
              Vencidos
            </option>
          </select>
        </label>

        <label class="token-archive-filter">
          <input
            v-model="filters.includeArchived"
            type="checkbox"
          />

          <span>
            Mostrar archivados
          </span>
        </label>
      </div>

      <div
        v-if="loading"
        class="token-loading"
      >
        <div class="token-spinner"></div>

        <span>
          Cargando tokens...
        </span>
      </div>

      <div
        v-else-if="filteredTokens.length"
        class="token-table-wrap"
      >
        <table class="token-table">
          <thead>
            <tr>
              <th>Token</th>
              <th>Cliente y sede</th>
              <th>Uso</th>
              <th>Estado</th>
              <th>Vencimiento</th>
              <th>Creación</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="item in filteredTokens"
              :key="item.id"
              :class="{
                'token-row-archived':
                  item.archived_at,
              }"
            >
              <td>
                <div class="token-name-cell">
                  <strong>
                    {{ item.name }}
                  </strong>

                  <div>
                    <code>
                      {{ item.token_prefix }}
                    </code>

                    <button
                      v-if="item.token_prefix"
                      class="token-inline-copy"
                      type="button"
                      title="Copiar prefijo"
                      @click="
                        copyText(
                          item.token_prefix
                        )
                      "
                    >
                      Copiar
                    </button>
                  </div>

                  <small>
                    {{ item.id }}
                  </small>
                </div>
              </td>

              <td>
                <div class="token-owner-cell">
                  <strong>
                    {{
                      item.customer_name ||
                      item.customer ||
                      "Sin cliente"
                    }}
                  </strong>

                  <span>
                    {{
                      item.branch_name ||
                      item.branch ||
                      "Sin sede específica"
                    }}
                  </span>
                </div>
              </td>

              <td>
                <div class="token-usage-cell">
                  <div>
                    <strong>
                      {{ item.used_count || 0 }}
                    </strong>

                    <span>
                      /
                      {{ item.maximum_uses }}
                    </span>
                  </div>

                  <div class="token-usage-progress">
                    <div
                      :style="{
                        width:
                          `${getUsagePercentage(
                            item
                          )}%`,
                      }"
                    ></div>
                  </div>

                  <small>
                    {{
                      Math.round(
                        getUsagePercentage(
                          item
                        )
                      )
                    }}%
                    utilizado
                  </small>
                </div>
              </td>

              <td>
                <MonitoringStatusBadge
                  :status="
                    getTokenState(
                      item
                    ).status
                  "
                  :label="
                    getTokenState(
                      item
                    ).label
                  "
                />

                <small
                  v-if="item.revoked_at"
                  class="token-state-date"
                >
                  {{
                    formatShortDate(
                      item.revoked_at
                    )
                  }}
                </small>
              </td>

              <td>
                <div class="token-date-cell">
                  <strong>
                    {{
                      formatDate(
                        item.expires_at
                      )
                    }}
                  </strong>

                  <span
                    v-if="isExpired(item)"
                    class="token-expired-note"
                  >
                    Vencido
                  </span>
                </div>
              </td>

              <td>
                <div class="token-date-cell">
                  <strong>
                    {{
                      formatShortDate(
                        item.created_at
                      )
                    }}
                  </strong>

                  <span>
                    {{
                      item.created_by_name ||
                      item.created_by ||
                      ""
                    }}
                  </span>
                </div>
              </td>

              <td>
                <div class="token-actions-cell">
                  <button
                    v-if="
                      item.can_be_used &&
                      !item.archived_at
                    "
                    class="token-action-button token-action-revoke"
                    type="button"
                    :disabled="
                      busyTokenId === item.id
                    "
                    @click="openRevokeModal(item)"
                  >
                    Revocar
                  </button>

                  <button
                    v-if="!item.archived_at"
                    class="token-action-button"
                    type="button"
                    :disabled="
                      busyTokenId === item.id
                    "
                    @click="openArchiveModal(item)"
                  >
                    Archivar
                  </button>

                  <button
                    v-else
                    class="token-action-button token-action-restore"
                    type="button"
                    :disabled="
                      busyTokenId === item.id
                    "
                    @click="restoreToken(item)"
                  >
                    {{
                      busyTokenId === item.id
                        ? "Restaurando..."
                        : "Restaurar"
                    }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <MonitoringEmptyState
        v-else
        title="Sin tokens"
        description="No existen tokens que coincidan con los filtros seleccionados."
      />
    </article>

    <div
      v-if="showRevokeModal"
      class="token-modal-backdrop"
      @click.self="closeRevokeModal"
    >
      <section class="token-modal">
        <header class="token-modal-header">
          <div>
            <h2>
              Revocar token
            </h2>

            <p>
              {{
                selectedToken?.name
              }}
            </p>
          </div>

          <button
            type="button"
            @click="closeRevokeModal"
          >
            ×
          </button>
        </header>

        <div class="token-modal-body">
          <div class="token-modal-warning">
            El agente ya no podrá registrarse utilizando
            este token.
          </div>

          <label class="token-field token-field-full">
            <span>
              Motivo de revocación
            </span>

            <textarea
              v-model.trim="revokeReason"
              rows="4"
              required
              placeholder="Indica el motivo..."
            ></textarea>
          </label>
        </div>

        <footer class="token-modal-footer">
          <button
            class="token-button token-button-secondary"
            type="button"
            :disabled="Boolean(busyTokenId)"
            @click="closeRevokeModal"
          >
            Cancelar
          </button>

          <button
            class="token-button token-button-danger"
            type="button"
            :disabled="
              Boolean(busyTokenId) ||
              !revokeReason.trim()
            "
            @click="confirmRevoke"
          >
            {{
              busyTokenId
                ? "Revocando..."
                : "Revocar token"
            }}
          </button>
        </footer>
      </section>
    </div>

    <div
      v-if="showArchiveModal"
      class="token-modal-backdrop"
      @click.self="closeArchiveModal"
    >
      <section class="token-modal">
        <header class="token-modal-header">
          <div>
            <h2>
              Archivar token
            </h2>

            <p>
              {{
                selectedToken?.name
              }}
            </p>
          </div>

          <button
            type="button"
            @click="closeArchiveModal"
          >
            ×
          </button>
        </header>

        <div class="token-modal-body">
          <label class="token-field token-field-full">
            <span>
              Motivo de archivado
            </span>

            <textarea
              v-model.trim="archiveReason"
              rows="4"
              placeholder="Indica el motivo..."
            ></textarea>
          </label>
        </div>

        <footer class="token-modal-footer">
          <button
            class="token-button token-button-secondary"
            type="button"
            :disabled="Boolean(busyTokenId)"
            @click="closeArchiveModal"
          >
            Cancelar
          </button>

          <button
            class="token-button token-button-warning"
            type="button"
            :disabled="Boolean(busyTokenId)"
            @click="confirmArchive"
          >
            {{
              busyTokenId
                ? "Archivando..."
                : "Archivar token"
            }}
          </button>
        </footer>
      </section>
    </div>
  </section>
</template>