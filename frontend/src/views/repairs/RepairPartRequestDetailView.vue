<script setup>
import {
  computed,
  onMounted,
  ref,
} from "vue"
import {
  useRoute,
  useRouter,
} from "vue-router"

import RepairPartDeliveryCard from "./components/RepairPartDeliveryCard.vue"
import RepairPartReplacementCard from "./components/RepairPartReplacementCard.vue"
import RepairPartRequestActions from "./components/RepairPartRequestActions.vue"
import RepairPartRequestAttachments from "./components/RepairPartRequestAttachments.vue"
import RepairPartRequestCommentBox from "./components/RepairPartRequestCommentBox.vue"
import RepairPartRequestDecisionPanel from "./components/RepairPartRequestDecisionPanel.vue"
import RepairPartRequestFlow from "./components/RepairPartRequestFlow.vue"
import RepairPartRequestItemCard from "./components/RepairPartRequestItemCard.vue"
import RepairPartRequestReviewCard from "./components/RepairPartRequestReviewCard.vue"
import RepairPartRequestStatusBadge from "./components/RepairPartRequestStatusBadge.vue"
import RepairPartRequestTimeline from "./components/RepairPartRequestTimeline.vue"
import RepairPartSourceCard from "./components/RepairPartSourceCard.vue"
import RepairPartWithdrawalCard from "./components/RepairPartWithdrawalCard.vue"

import {
  archiveRepairPartRequest,
  cancelRepairPartRequest,
  closeRepairPartRequest,
  createRepairPartRequestComment,
  createRepairPartRequestDecision,
  getRepairPartDeliveries,
  getRepairPartReplacements,
  getRepairPartRequest,
  getRepairPartRequestAttachments,
  getRepairPartRequestComments,
  getRepairPartRequestHistory,
  getRepairPartRequestItems,
  getRepairPartRequestReviews,
  getRepairPartSources,
  getRepairPartWithdrawals,
  restoreRepairPartRequest,
  submitRepairPartRequest,
} from "../../services/repairs.service"

import "./RepairPartRequestDetailView.css"

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const actionLoading = ref(false)
const errorMessage = ref("")
const successMessage = ref("")

const request = ref(null)
const items = ref([])
const history = ref([])
const comments = ref([])
const attachments = ref([])
const reviews = ref([])
const sources = ref([])
const withdrawals = ref([])
const deliveries = ref([])
const replacements = ref([])

const requestId = computed(() =>
  String(route.params.id || "")
)

const firstItem = computed(() =>
  items.value[0] || null
)

function normalizeResults(response) {
  if (Array.isArray(response)) {
    return response
  }

  return Array.isArray(response?.results)
    ? response.results
    : []
}

async function loadDetail() {
  loading.value = true
  errorMessage.value = ""

  try {
    const [
      requestResponse,
      itemsResponse,
      historyResponse,
      commentsResponse,
      attachmentsResponse,
      reviewsResponse,
      sourcesResponse,
      withdrawalsResponse,
      deliveriesResponse,
      replacementsResponse,
    ] = await Promise.all([
      getRepairPartRequest(requestId.value),
      getRepairPartRequestItems({
        request: requestId.value,
      }),
      getRepairPartRequestHistory({
        request: requestId.value,
      }),
      getRepairPartRequestComments({
        request: requestId.value,
      }),
      getRepairPartRequestAttachments({
        request: requestId.value,
      }),
      getRepairPartRequestReviews({
        request: requestId.value,
      }),
      getRepairPartSources({
        request: requestId.value,
      }),
      getRepairPartWithdrawals({
        request: requestId.value,
      }),
      getRepairPartDeliveries({
        request: requestId.value,
      }),
      getRepairPartReplacements({
        request: requestId.value,
      }),
    ])

    request.value = requestResponse
    items.value = normalizeResults(itemsResponse)
    history.value = normalizeResults(historyResponse)
    comments.value = normalizeResults(commentsResponse)
    attachments.value =
      normalizeResults(attachmentsResponse)
    reviews.value = normalizeResults(reviewsResponse)
    sources.value = normalizeResults(sourcesResponse)
    withdrawals.value =
      normalizeResults(withdrawalsResponse)
    deliveries.value =
      normalizeResults(deliveriesResponse)
    replacements.value =
      normalizeResults(replacementsResponse)
  } catch (error) {
    errorMessage.value =
      error?.message ||
      "No se pudo cargar la solicitud."
  } finally {
    loading.value = false
  }
}

async function runAction(callback, successText) {
  actionLoading.value = true
  errorMessage.value = ""
  successMessage.value = ""

  try {
    await callback()
    successMessage.value = successText
    await loadDetail()
  } catch (error) {
    errorMessage.value =
      error?.message ||
      "No se pudo completar la acción."
  } finally {
    actionLoading.value = false
  }
}

function editRequest() {
  router.push({
    name: "repair-part-request-edit",
    params: {
      id: requestId.value,
    },
  })
}

function submitRequest() {
  runAction(
    () =>
      submitRepairPartRequest(
        requestId.value,
        {
          observations: "",
        }
      ),
    "Solicitud enviada correctamente."
  )
}

function cancelRequest() {
  const reason = window.prompt(
    "Indica el motivo de cancelación:"
  )

  if (!reason?.trim()) return

  runAction(
    () =>
      cancelRepairPartRequest(
        requestId.value,
        {
          reason: reason.trim(),
        }
      ),
    "Solicitud cancelada."
  )
}

function closeRequest() {
  runAction(
    () =>
      closeRepairPartRequest(
        requestId.value,
        {
          observations: "",
        }
      ),
    "Solicitud cerrada."
  )
}

function archiveRequest() {
  const reason = window.prompt(
    "Indica el motivo de archivado:"
  )

  if (!reason?.trim()) return

  runAction(
    () =>
      archiveRepairPartRequest(
        requestId.value,
        reason.trim()
      ),
    "Solicitud archivada."
  )
}

function restoreRequest() {
  runAction(
    () =>
      restoreRepairPartRequest(
        requestId.value
      ),
    "Solicitud restaurada."
  )
}

async function addComment(payload) {
  await runAction(
    () =>
      createRepairPartRequestComment(
        payload
      ),
    "Comentario agregado."
  )
}

async function addDecision(payload) {
  await runAction(
    () =>
      createRepairPartRequestDecision(
        payload
      ),
    "Decisión registrada."
  )
}

function openItem(item) {
  router.push({
    name: "repair-part-request-item-detail",
    params: {
      id: item.id,
    },
  })
}

onMounted(loadDetail)
</script>

<template>
  <main class="repair-part-request-detail">
    <section
      v-if="loading"
      class="repair-part-request-detail__state"
    >
      Cargando solicitud...
    </section>

    <template v-else-if="request">
      <header class="repair-part-request-detail__header">
        <div>
          <span>Pedido de repuestos</span>
          <h1>{{ request.code }}</h1>
          <p>{{ request.title }}</p>
        </div>

        <div class="repair-part-request-detail__header-actions">
          <button
            v-if="request.status === 'draft'"
            type="button"
            @click="editRequest"
          >
            Editar
          </button>

          <RepairPartRequestActions
            :request="request"
            @submit="submitRequest"
            @cancel="cancelRequest"
            @close="closeRequest"
            @archive="archiveRequest"
            @restore="restoreRequest"
          />
        </div>
      </header>

      <p
        v-if="errorMessage"
        class="repair-part-request-detail__message error"
      >
        {{ errorMessage }}
      </p>

      <p
        v-if="successMessage"
        class="repair-part-request-detail__message success"
      >
        {{ successMessage }}
      </p>

      <RepairPartRequestFlow
        :current-status="request.status"
      />

      <section class="repair-part-request-detail__summary">
        <article>
          <small>Estado</small>
          <RepairPartRequestStatusBadge
            :status="request.status"
            :label="request.status_name"
          />
        </article>

        <article>
          <small>Prioridad</small>
          <strong>{{ request.priority_name }}</strong>
        </article>

        <article>
          <small>Reparación</small>
          <strong>{{ request.repair_code }}</strong>
        </article>

        <article>
          <small>Serie</small>
          <strong>
            {{ request.equipment_serial_number }}
          </strong>
        </article>

        <article>
          <small>Área responsable</small>
          <strong>
            {{ request.responsible_area_name }}
          </strong>
        </article>

        <article>
          <small>Solicitado por</small>
          <strong>
            {{ request.requested_by_name }}
          </strong>
        </article>
      </section>

      <section class="repair-part-request-detail__grid">
        <article class="repair-part-request-detail__card span-2">
          <header>
            <strong>Información técnica</strong>
          </header>

          <dl>
            <div>
              <dt>Descripción</dt>
              <dd>{{ request.description || "Sin descripción" }}</dd>
            </div>

            <div>
              <dt>Justificación técnica</dt>
              <dd>
                {{
                  request.technical_justification ||
                  "Sin justificación registrada"
                }}
              </dd>
            </div>

            <div>
              <dt>Observaciones</dt>
              <dd>
                {{
                  request.general_observations ||
                  "Sin observaciones"
                }}
              </dd>
            </div>
          </dl>
        </article>

        <article class="repair-part-request-detail__card span-2">
          <header>
            <strong>Ítems solicitados</strong>
            <span>{{ items.length }}</span>
          </header>

          <div class="repair-part-request-detail__stack">
            <RepairPartRequestItemCard
              v-for="item in items"
              :key="item.id"
              :item="item"
              @open="openItem"
            />

            <p v-if="!items.length">
              No hay ítems registrados.
            </p>
          </div>
        </article>

        <article class="repair-part-request-detail__card">
          <header>
            <strong>Revisión del jefe</strong>
          </header>

          <div class="repair-part-request-detail__stack">
            <RepairPartRequestReviewCard
              v-for="review in reviews"
              :key="review.id"
              :review="review"
            />

            <p v-if="!reviews.length">
              Sin revisiones.
            </p>
          </div>
        </article>

        <article class="repair-part-request-detail__card">
          <header>
            <strong>Origen seleccionado</strong>
          </header>

          <div class="repair-part-request-detail__stack">
            <RepairPartSourceCard
              v-for="source in sources"
              :key="source.id"
              :source="source"
            />

            <p v-if="!sources.length">
              Sin origen definido.
            </p>
          </div>
        </article>

        <article class="repair-part-request-detail__card">
          <header>
            <strong>Retiros</strong>
          </header>

          <div class="repair-part-request-detail__stack">
            <RepairPartWithdrawalCard
              v-for="withdrawal in withdrawals"
              :key="withdrawal.id"
              :withdrawal="withdrawal"
            />

            <p v-if="!withdrawals.length">
              Sin retiros.
            </p>
          </div>
        </article>

        <article class="repair-part-request-detail__card">
          <header>
            <strong>Entregas</strong>
          </header>

          <div class="repair-part-request-detail__stack">
            <RepairPartDeliveryCard
              v-for="delivery in deliveries"
              :key="delivery.id"
              :delivery="delivery"
            />

            <p v-if="!deliveries.length">
              Sin entregas.
            </p>
          </div>
        </article>

        <article class="repair-part-request-detail__card">
          <header>
            <strong>Reposiciones</strong>
          </header>

          <div class="repair-part-request-detail__stack">
            <RepairPartReplacementCard
              v-for="replacement in replacements"
              :key="replacement.id"
              :replacement="replacement"
            />

            <p v-if="!replacements.length">
              Sin reposiciones.
            </p>
          </div>
        </article>

        <article class="repair-part-request-detail__card">
          <header>
            <strong>Decisión de gerencia</strong>
          </header>

          <RepairPartRequestDecisionPanel
            :request-id="request.id"
            :item-id="firstItem?.id || ''"
            :requested-quantity="
              firstItem?.requested_quantity || 0
            "
            :disabled="actionLoading || !firstItem"
            @submit="addDecision"
          />
        </article>

        <article class="repair-part-request-detail__card">
          <RepairPartRequestAttachments
            :attachments="attachments"
          />
        </article>

        <article class="repair-part-request-detail__card">
          <RepairPartRequestCommentBox
            :request-id="request.id"
            :disabled="actionLoading"
            @submit="addComment"
          />

          <div class="repair-part-request-detail__comments">
            <article
              v-for="comment in comments"
              :key="comment.id"
            >
              <header>
                <strong>{{ comment.author_name }}</strong>
                <small>{{ comment.created_at }}</small>
              </header>

              <p>{{ comment.text }}</p>

              <span>
                {{ comment.comment_type_name }}
              </span>
            </article>
          </div>
        </article>

        <article class="repair-part-request-detail__card">
          <header>
            <strong>Historial</strong>
          </header>

          <RepairPartRequestTimeline
            :entries="history"
          />
        </article>
      </section>
    </template>

    <section
      v-else
      class="repair-part-request-detail__state"
    >
      No se encontró la solicitud.
    </section>
  </main>
</template>
