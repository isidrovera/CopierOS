<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue"

import {
  archiveRepairPhoto,
  createRepairPhoto,
  getRepairChecklistItems,
  getRepairPhotos,
  removeRepairPhotoVerification,
  restoreRepairPhoto,
  verifyRepairPhoto,
} from "../../../services/repairs.service"

import "./RepairPhotosSection.css"


const props = defineProps({
  repairId: {
    type: String,
    required: true,
  },

  repair: {
    type: Object,
    default: null,
  },

  requestedChecklistItem: {
    type: Object,
    default: null,
  },
})


const emit = defineEmits([
  "updated",
  "request-completed",
])


const loading = ref(false)
const processing = ref(false)
const uploading = ref(false)

const errorMessage = ref("")
const successMessage = ref("")

const photos = ref([])
const checklistItems = ref([])

const selectedStage = ref("")
const selectedCategory = ref("")
const selectedVerification = ref("")
const includeArchived = ref(false)

const uploadModalVisible = ref(false)
const verifyModalVisible = ref(false)
const removeVerificationModalVisible = ref(false)
const previewModalVisible = ref(false)

const selectedPhoto = ref(null)
const selectedFiles = ref([])
const previews = ref([])

const fileInput = ref(null)

const uploadForm = reactive({
  checklist_item: "",
  category: "",
  stage: "",
  title: "",
  description: "",
  taken_at: "",
  is_required: false,
  counts_for_minimum: true,
  latitude: "",
  longitude: "",
  display_order: 0,
})

const verificationForm = reactive({
  verification_notes: "",
  reason: "",
})


const requiredMinimum = computed(() => {
  return Number(
    props.repair
      ?.minimum_photos_required ||
    0
  )
})


const activePhotos = computed(() => {
  return photos.value.filter(
    (photo) =>
      !isArchived(photo)
  )
})


const countedPhotos = computed(() => {
  return activePhotos.value.filter(
    (photo) =>
      photo.counts_for_minimum
  ).length
})


const verifiedPhotos = computed(() => {
  return activePhotos.value.filter(
    (photo) =>
      photo.is_verified
  ).length
})


const pendingVerificationPhotos = computed(() => {
  return activePhotos.value.filter(
    (photo) =>
      !photo.is_verified
  ).length
})


const requiredPhotos = computed(() => {
  return activePhotos.value.filter(
    (photo) =>
      photo.is_required
  ).length
})


const minimumCompleted = computed(() => {
  if (!requiredMinimum.value) {
    return true
  }

  return (
    countedPhotos.value >=
    requiredMinimum.value
  )
})


const progressPercentage = computed(() => {
  if (!requiredMinimum.value) {
    return 100
  }

  return Math.min(
    Math.round(
      (
        countedPhotos.value /
        requiredMinimum.value
      ) * 100
    ),
    100
  )
})


const canUpload = computed(() => {
  return (
    Boolean(props.repairId) &&
    Boolean(props.repair?.is_active) &&
    !props.repair?.is_archived
  )
})


function normalizeCollection(data) {
  if (Array.isArray(data)) {
    return data
  }

  if (
    data &&
    Array.isArray(data.results)
  ) {
    return data.results
  }

  return []
}


function isArchived(photo) {
  return Boolean(
    photo?.is_archived ||
    photo?.archived_at
  )
}


function formatDateTime(value) {
  if (!value) {
    return "Sin registro"
  }

  const date = new Date(value)

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
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


function formatFileSize(value) {
  const bytes = Number(
    value || 0
  )

  if (!bytes) {
    return ""
  }

  if (bytes < 1024) {
    return `${bytes} B`
  }

  if (
    bytes <
    1024 * 1024
  ) {
    return (
      `${(
        bytes / 1024
      ).toFixed(1)} KB`
    )
  }

  return (
    `${(
      bytes /
      (
        1024 * 1024
      )
    ).toFixed(1)} MB`
  )
}


function getPhotoUrl(photo) {
  const image =
    photo?.image || ""

  if (!image) {
    return ""
  }

  if (
    String(image).startsWith(
      "http://"
    ) ||
    String(image).startsWith(
      "https://"
    )
  ) {
    return image
  }

  return (
    `http://127.0.0.1:8000${image}`
  )
}


function getStageName(photo) {
  return (
    photo?.stage_name ||
    photo?.stage ||
    "Sin etapa"
  )
}


function getCategoryName(photo) {
  return (
    photo?.category_name ||
    photo?.category ||
    "Sin categoría"
  )
}


function getChecklistItemName(photo) {
  return (
    photo?.checklist_item_name ||
    "Sin punto vinculado"
  )
}


function showMessage(
  type,
  message
) {
  if (type === "success") {
    successMessage.value =
      message

    errorMessage.value = ""
  } else {
    errorMessage.value =
      message

    successMessage.value = ""
  }

  if (type === "success") {
    window.setTimeout(
      () => {
        if (
          successMessage.value ===
          message
        ) {
          successMessage.value = ""
        }
      },
      2200
    )
  }
}


async function loadChecklistItems() {
  try {
    const response =
      await getRepairChecklistItems({
        repair: props.repairId,
        ordering:
          "display_order,created_at",
      })

    checklistItems.value =
      normalizeCollection(response)
  } catch {
    checklistItems.value = []
  }
}


async function loadPhotos() {
  loading.value = true
  errorMessage.value = ""

  try {
    const response =
      await getRepairPhotos({
        repair: props.repairId,
        stage:
          selectedStage.value,
        category:
          selectedCategory.value,
        isVerified:
          selectedVerification.value,
        includeArchived:
          includeArchived.value,
        ordering:
          "display_order,created_at",
      })

    photos.value =
      normalizeCollection(response)
  } catch (error) {
    photos.value = []

    errorMessage.value =
      error.message ||
      "No se pudieron cargar las fotografías."
  } finally {
    loading.value = false
  }
}


async function loadData() {
  await Promise.all([
    loadPhotos(),
    loadChecklistItems(),
  ])
}


function revokePreviews() {
  for (
    const preview
    of previews.value
  ) {
    if (preview.url) {
      URL.revokeObjectURL(
        preview.url
      )
    }
  }

  previews.value = []
}


function resetUploadForm() {
  revokePreviews()

  selectedFiles.value = []

  uploadForm.checklist_item = ""
  uploadForm.category = ""
  uploadForm.stage = ""
  uploadForm.title = ""
  uploadForm.description = ""
  uploadForm.taken_at = ""
  uploadForm.is_required = false
  uploadForm.counts_for_minimum = true
  uploadForm.latitude = ""
  uploadForm.longitude = ""
  uploadForm.display_order = 0

  if (fileInput.value) {
    fileInput.value.value = ""
  }
}


function openUploadModal(
  checklistItem = null
) {
  resetUploadForm()

  const item =
    checklistItem ||
    props.requestedChecklistItem

  if (item?.id) {
    uploadForm.checklist_item =
      item.id

    uploadForm.is_required =
      Boolean(
        item.requires_photo
      )

    uploadForm.counts_for_minimum =
      true

    uploadForm.title =
      item.name || ""
  }

  uploadModalVisible.value = true
}


function closeUploadModal() {
  uploadModalVisible.value = false
  resetUploadForm()

  emit("request-completed")
}


function handleFiles(event) {
  const files = Array.from(
    event.target.files || []
  )

  const validFiles = []

  for (const file of files) {
    const allowedTypes = [
      "image/jpeg",
      "image/jpg",
      "image/png",
      "image/webp",
    ]

    if (
      file.type &&
      !allowedTypes.includes(
        file.type
      )
    ) {
      showMessage(
        "error",
        `${file.name}: solo se permiten imágenes JPG, PNG o WEBP.`
      )

      continue
    }

    if (
      file.size >
      10 * 1024 * 1024
    ) {
      showMessage(
        "error",
        `${file.name}: la imagen supera los 10 MB.`
      )

      continue
    }

    validFiles.push(file)
  }

  revokePreviews()

  selectedFiles.value =
    validFiles

  previews.value =
    validFiles.map(
      (file) => ({
        file,
        url:
          URL.createObjectURL(
            file
          ),
      })
    )
}


function removeSelectedFile(index) {
  const preview =
    previews.value[index]

  if (preview?.url) {
    URL.revokeObjectURL(
      preview.url
    )
  }

  previews.value.splice(
    index,
    1
  )

  selectedFiles.value.splice(
    index,
    1
  )

  if (
    !selectedFiles.value.length &&
    fileInput.value
  ) {
    fileInput.value.value = ""
  }
}


function appendOptionalField(
  formData,
  name,
  value
) {
  if (
    value !== undefined &&
    value !== null &&
    String(value).trim() !== ""
  ) {
    formData.append(
      name,
      String(value).trim()
    )
  }
}


function buildPhotoFormData(
  file,
  index
) {
  const formData =
    new FormData()

  formData.append(
    "repair",
    props.repairId
  )

  formData.append(
    "image",
    file
  )

  appendOptionalField(
    formData,
    "checklist_item",
    uploadForm.checklist_item
  )

  appendOptionalField(
    formData,
    "category",
    uploadForm.category
  )

  appendOptionalField(
    formData,
    "stage",
    uploadForm.stage
  )

  const title =
    selectedFiles.value.length > 1
      ? (
          uploadForm.title
            ? `${uploadForm.title} ${index + 1}`
            : file.name
        )
      : (
          uploadForm.title ||
          file.name
        )

  appendOptionalField(
    formData,
    "title",
    title
  )

  appendOptionalField(
    formData,
    "description",
    uploadForm.description
  )

  appendOptionalField(
    formData,
    "taken_at",
    uploadForm.taken_at
  )

  formData.append(
    "is_required",
    String(
      uploadForm.is_required
    )
  )

  formData.append(
    "counts_for_minimum",
    String(
      uploadForm.counts_for_minimum
    )
  )

  appendOptionalField(
    formData,
    "latitude",
    uploadForm.latitude
  )

  appendOptionalField(
    formData,
    "longitude",
    uploadForm.longitude
  )

  formData.append(
    "display_order",
    String(
      Number(
        uploadForm.display_order ||
        0
      ) + index
    )
  )

  return formData
}


function validateUpload() {
  if (
    !selectedFiles.value.length
  ) {
    throw new Error(
      "Selecciona al menos una fotografía."
    )
  }

  if (
    uploadForm.is_required &&
    !uploadForm.counts_for_minimum
  ) {
    throw new Error(
      "Una fotografía obligatoria debe contabilizar para el mínimo."
    )
  }

  if (
    uploadForm.latitude !== "" &&
    (
      Number(
        uploadForm.latitude
      ) < -90 ||
      Number(
        uploadForm.latitude
      ) > 90
    )
  ) {
    throw new Error(
      "La latitud debe estar entre -90 y 90."
    )
  }

  if (
    uploadForm.longitude !== "" &&
    (
      Number(
        uploadForm.longitude
      ) < -180 ||
      Number(
        uploadForm.longitude
      ) > 180
    )
  ) {
    throw new Error(
      "La longitud debe estar entre -180 y 180."
    )
  }
}


async function submitPhotos() {
  uploading.value = true
  errorMessage.value = ""

  try {
    validateUpload()

    for (
      let index = 0;
      index <
      selectedFiles.value.length;
      index += 1
    ) {
      const file =
        selectedFiles.value[index]

      const formData =
        buildPhotoFormData(
          file,
          index
        )

      await createRepairPhoto(
        formData
      )
    }

    const total =
      selectedFiles.value.length

    closeUploadModal()

    showMessage(
      "success",
      total === 1
        ? "La fotografía se cargó correctamente."
        : `${total} fotografías se cargaron correctamente.`
    )

    await loadPhotos()

    emit("updated")
  } catch (error) {
    showMessage(
      "error",
      error.message
    )
  } finally {
    uploading.value = false
  }
}


function openPreview(photo) {
  selectedPhoto.value =
    photo

  previewModalVisible.value =
    true
}


function closePreview() {
  previewModalVisible.value =
    false

  selectedPhoto.value = null
}


function openVerifyModal(photo) {
  selectedPhoto.value =
    photo

  verificationForm
    .verification_notes = ""

  verifyModalVisible.value =
    true
}


function closeVerifyModal() {
  verifyModalVisible.value =
    false

  selectedPhoto.value = null

  verificationForm
    .verification_notes = ""
}


async function submitVerification() {
  if (!selectedPhoto.value) {
    return
  }

  processing.value = true
  errorMessage.value = ""

  try {
    await verifyRepairPhoto(
      selectedPhoto.value.id,
      String(
        verificationForm
          .verification_notes ||
        ""
      ).trim()
    )

    closeVerifyModal()

    showMessage(
      "success",
      "La fotografía fue verificada."
    )

    await loadPhotos()

    emit("updated")
  } catch (error) {
    showMessage(
      "error",
      error.message
    )
  } finally {
    processing.value = false
  }
}


function openRemoveVerificationModal(
  photo
) {
  selectedPhoto.value =
    photo

  verificationForm.reason = ""

  removeVerificationModalVisible.value =
    true
}


function closeRemoveVerificationModal() {
  removeVerificationModalVisible.value =
    false

  selectedPhoto.value = null
  verificationForm.reason = ""
}


async function submitRemoveVerification() {
  if (!selectedPhoto.value) {
    return
  }

  processing.value = true
  errorMessage.value = ""

  try {
    await removeRepairPhotoVerification(
      selectedPhoto.value.id,
      String(
        verificationForm.reason ||
        ""
      ).trim()
    )

    closeRemoveVerificationModal()

    showMessage(
      "success",
      "La verificación fue retirada."
    )

    await loadPhotos()

    emit("updated")
  } catch (error) {
    showMessage(
      "error",
      error.message
    )
  } finally {
    processing.value = false
  }
}


async function handleArchive(photo) {
  const reason =
    window.prompt(
      "Indica el motivo para archivar la fotografía:"
    )

  if (reason === null) {
    return
  }

  processing.value = true
  errorMessage.value = ""

  try {
    await archiveRepairPhoto(
      photo.id,
      reason.trim()
    )

    showMessage(
      "success",
      "La fotografía fue archivada."
    )

    await loadPhotos()

    emit("updated")
  } catch (error) {
    showMessage(
      "error",
      error.message
    )
  } finally {
    processing.value = false
  }
}


async function handleRestore(photo) {
  processing.value = true
  errorMessage.value = ""

  try {
    await restoreRepairPhoto(
      photo.id
    )

    showMessage(
      "success",
      "La fotografía fue restaurada."
    )

    await loadPhotos()

    emit("updated")
  } catch (error) {
    showMessage(
      "error",
      error.message
    )
  } finally {
    processing.value = false
  }
}


watch(
  () =>
    props.requestedChecklistItem,
  (item) => {
    if (item?.id) {
      openUploadModal(item)
    }
  },
  {
    deep: true,
  }
)


watch(
  () => props.repairId,
  () => {
    loadData()
  }
)


onMounted(() => {
  loadData()

  if (
    props.requestedChecklistItem?.id
  ) {
    openUploadModal(
      props.requestedChecklistItem
    )
  }
})


onBeforeUnmount(() => {
  revokePreviews()
})
</script>

<template>
  <section class="repair-photos-section">
    <header class="photos-section-header">
      <div>
        <span class="photos-kicker">
          Evidencias técnicas
        </span>

        <h2>
          Fotografías
        </h2>

        <p>
          Registra el estado del equipo antes,
          durante y después de la reparación.
        </p>
      </div>

      <div class="photos-header-actions">
        <button
          class="photos-secondary-button"
          type="button"
          :disabled="
            loading ||
            processing ||
            uploading
          "
          @click="loadData"
        >
          ↻ Actualizar
        </button>

        <button
          v-if="canUpload"
          class="photos-primary-button"
          type="button"
          :disabled="
            processing ||
            uploading
          "
          @click="openUploadModal()"
        >
          ＋ Subir fotografías
        </button>
      </div>
    </header>

    <div
      v-if="errorMessage"
      class="photos-message error"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="successMessage"
      class="photos-message success"
    >
      {{ successMessage }}
    </div>

    <section class="photos-summary-grid">
      <article class="photos-summary-card">
        <span class="photos-summary-icon">
          ▧
        </span>

        <div>
          <small>
            Fotografías
          </small>

          <strong>
            {{ activePhotos.length }}
          </strong>
        </div>
      </article>

      <article class="photos-summary-card">
        <span
          class="photos-summary-icon"
          :class="{
            completed:
              minimumCompleted,
          }"
        >
          ✓
        </span>

        <div>
          <small>
            Mínimo requerido
          </small>

          <strong>
            {{ countedPhotos }}
            /
            {{ requiredMinimum }}
          </strong>
        </div>
      </article>

      <article class="photos-summary-card">
        <span class="photos-summary-icon verified">
          ◉
        </span>

        <div>
          <small>
            Verificadas
          </small>

          <strong>
            {{ verifiedPhotos }}
          </strong>
        </div>
      </article>

      <article class="photos-summary-card">
        <span class="photos-summary-icon required">
          !
        </span>

        <div>
          <small>
            Obligatorias
          </small>

          <strong>
            {{ requiredPhotos }}
          </strong>
        </div>
      </article>
    </section>

    <section class="photos-progress-card">
      <div class="photos-progress-heading">
        <div>
          <span>
            Evidencias requeridas
          </span>

          <strong>
            {{ progressPercentage }}%
          </strong>
        </div>

        <small
          :class="{
            completed:
              minimumCompleted,
          }"
        >
          {{
            minimumCompleted
              ? "Requisito cumplido"
              : `${Math.max(
                  requiredMinimum -
                  countedPhotos,
                  0
                )} pendientes`
          }}
        </small>
      </div>

      <div class="photos-progress-track">
        <span
          :class="{
            completed:
              minimumCompleted,
          }"
          :style="{
            width:
              `${progressPercentage}%`,
          }"
        ></span>
      </div>
    </section>

    <section class="photos-filters">
      <input
        v-model="selectedStage"
        type="text"
        placeholder="Filtrar por valor de etapa"
        @change="loadPhotos"
      />

      <input
        v-model="selectedCategory"
        type="text"
        placeholder="Filtrar por valor de categoría"
        @change="loadPhotos"
      />

      <select
        v-model="selectedVerification"
        @change="loadPhotos"
      >
        <option value="">
          Todas las verificaciones
        </option>

        <option :value="true">
          Verificadas
        </option>

        <option :value="false">
          Pendientes
        </option>
      </select>

      <label class="photos-archive-filter">
        <input
          v-model="includeArchived"
          type="checkbox"
          @change="loadPhotos"
        />

        <span></span>

        Ver archivadas
      </label>

      <div class="verification-total">
        Pendientes de verificación:
        <strong>
          {{ pendingVerificationPhotos }}
        </strong>
      </div>
    </section>

    <div
      v-if="loading"
      class="photos-loading"
    >
      <span class="photos-spinner"></span>

      Cargando fotografías...
    </div>

    <div
      v-else-if="!photos.length"
      class="photos-empty-state"
    >
      <span class="photos-empty-icon">
        ▧
      </span>

      <strong>
        No existen fotografías
      </strong>

      <p>
        Sube las evidencias del estado del equipo
        y vincúlalas con el checklist cuando corresponda.
      </p>

      <button
        v-if="canUpload"
        class="photos-primary-button"
        type="button"
        @click="openUploadModal()"
      >
        Subir primera fotografía
      </button>
    </div>

    <div
      v-else
      class="repair-photos-grid"
    >
      <article
        v-for="photo in photos"
        :key="photo.id"
        class="repair-photo-card"
        :class="{
          archived:
            isArchived(photo),
        }"
      >
        <button
          class="photo-preview-button"
          type="button"
          @click="openPreview(photo)"
        >
          <img
            v-if="getPhotoUrl(photo)"
            :src="getPhotoUrl(photo)"
            :alt="
              photo.title ||
              photo.original_filename ||
              'Fotografía'
            "
          />

          <span
            v-else
            class="photo-without-image"
          >
            Sin imagen
          </span>

          <div class="photo-top-badges">
            <span class="photo-stage-badge">
              {{ getStageName(photo) }}
            </span>

            <span
              v-if="photo.is_verified"
              class="photo-verified-badge"
            >
              ✓ Verificada
            </span>
          </div>
        </button>

        <div class="photo-card-content">
          <div class="photo-card-heading">
            <div>
              <strong>
                {{
                  photo.title ||
                  photo.original_filename ||
                  "Fotografía"
                }}
              </strong>

              <span>
                {{ getCategoryName(photo) }}
              </span>
            </div>

            <span
              v-if="isArchived(photo)"
              class="photo-archived-badge"
            >
              Archivada
            </span>
          </div>

          <p
            v-if="photo.description"
            class="photo-description"
          >
            {{ photo.description }}
          </p>

          <dl class="photo-information">
            <div>
              <dt>
                Checklist
              </dt>

              <dd>
                {{
                  getChecklistItemName(
                    photo
                  )
                }}
              </dd>
            </div>

            <div>
              <dt>
                Tomada
              </dt>

              <dd>
                {{
                  formatDateTime(
                    photo.taken_at
                  )
                }}
              </dd>
            </div>

            <div>
              <dt>
                Subida
              </dt>

              <dd>
                {{
                  formatDateTime(
                    photo.uploaded_at ||
                    photo.created_at
                  )
                }}
              </dd>
            </div>

            <div>
              <dt>
                Usuario
              </dt>

              <dd>
                {{
                  photo.uploaded_by_name ||
                  photo.taken_by_name ||
                  "Sin registro"
                }}
              </dd>
            </div>

            <div
              v-if="photo.file_size"
            >
              <dt>
                Tamaño
              </dt>

              <dd>
                {{
                  formatFileSize(
                    photo.file_size
                  )
                }}
              </dd>
            </div>
          </dl>

          <div class="photo-requirements">
            <span
              v-if="photo.is_required"
              class="photo-requirement required"
            >
              Obligatoria
            </span>

            <span
              v-if="photo.counts_for_minimum"
              class="photo-requirement counts"
            >
              Cuenta para mínimo
            </span>

            <span
              v-if="photo.checklist_item"
              class="photo-requirement checklist"
            >
              Vinculada al checklist
            </span>
          </div>

          <div class="photo-card-actions">
            <button
              class="photo-action-button view"
              type="button"
              @click="openPreview(photo)"
            >
              Ver
            </button>

            <button
              v-if="
                !photo.is_verified &&
                !isArchived(photo)
              "
              class="photo-action-button verify"
              type="button"
              :disabled="processing"
              @click="openVerifyModal(photo)"
            >
              Verificar
            </button>

            <button
              v-if="
                photo.is_verified &&
                !isArchived(photo)
              "
              class="photo-action-button verification"
              type="button"
              :disabled="processing"
              @click="
                openRemoveVerificationModal(
                  photo
                )
              "
            >
              Quitar verificación
            </button>

            <button
              v-if="!isArchived(photo)"
              class="photo-action-button archive"
              type="button"
              :disabled="processing"
              @click="handleArchive(photo)"
            >
              Archivar
            </button>

            <button
              v-else
              class="photo-action-button restore"
              type="button"
              :disabled="processing"
              @click="handleRestore(photo)"
            >
              Restaurar
            </button>
          </div>
        </div>
      </article>
    </div>

    <!-- SUBIR FOTOGRAFÍAS -->
    <div
      v-if="uploadModalVisible"
      class="photos-modal-backdrop"
      @click.self="closeUploadModal"
    >
      <form
        class="photos-modal upload-modal"
        @submit.prevent="submitPhotos"
      >
        <header class="photos-modal-header">
          <div>
            <h3>
              Subir fotografías
            </h3>

            <p>
              Puedes seleccionar varias imágenes.
              Máximo 10 MB por archivo.
            </p>
          </div>

          <button
            class="photos-modal-close"
            type="button"
            @click="closeUploadModal"
          >
            ×
          </button>
        </header>

        <label class="photo-dropzone">
          <input
            ref="fileInput"
            type="file"
            accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
            multiple
            @change="handleFiles"
          />

          <span class="dropzone-icon">
            ▧
          </span>

          <strong>
            Seleccionar fotografías
          </strong>

          <small>
            JPG, PNG o WEBP
          </small>
        </label>

        <div
          v-if="previews.length"
          class="selected-photo-previews"
        >
          <article
            v-for="(
              preview,
              index
            ) in previews"
            :key="
              `${preview.file.name}-${index}`
            "
          >
            <img
              :src="preview.url"
              :alt="preview.file.name"
            />

            <div>
              <strong>
                {{ preview.file.name }}
              </strong>

              <small>
                {{
                  formatFileSize(
                    preview.file.size
                  )
                }}
              </small>
            </div>

            <button
              type="button"
              title="Quitar archivo"
              @click="
                removeSelectedFile(
                  index
                )
              "
            >
              ×
            </button>
          </article>
        </div>

        <div class="photos-form-grid">
          <label class="photos-field full-width">
            <span>
              Punto del checklist
            </span>

            <select
              v-model="
                uploadForm.checklist_item
              "
            >
              <option value="">
                Sin punto vinculado
              </option>

              <option
                v-for="item in checklistItems"
                :key="item.id"
                :value="item.id"
              >
                {{ item.code }}
                ·
                {{ item.name }}
              </option>
            </select>
          </label>

          <label class="photos-field">
            <span>
              Categoría
            </span>

            <input
              v-model="uploadForm.category"
              type="text"
              placeholder="Vacío: valor predeterminado"
            />
          </label>

          <label class="photos-field">
            <span>
              Etapa
            </span>

            <input
              v-model="uploadForm.stage"
              type="text"
              placeholder="Vacío: valor predeterminado"
            />
          </label>

          <label class="photos-field full-width">
            <span>
              Título
            </span>

            <input
              v-model="uploadForm.title"
              type="text"
              maxlength="200"
              placeholder="Ejemplo: Vista frontal del equipo"
            />
          </label>

          <label class="photos-field full-width">
            <span>
              Descripción
            </span>

            <textarea
              v-model="
                uploadForm.description
              "
              rows="4"
              placeholder="Describe el estado o la evidencia mostrada"
            ></textarea>
          </label>

          <label class="photos-field">
            <span>
              Fecha y hora de toma
            </span>

            <input
              v-model="uploadForm.taken_at"
              type="datetime-local"
            />
          </label>

          <label class="photos-field">
            <span>
              Orden inicial
            </span>

            <input
              v-model.number="
                uploadForm.display_order
              "
              type="number"
              min="0"
            />
          </label>

          <label class="photos-field">
            <span>
              Latitud
            </span>

            <input
              v-model="uploadForm.latitude"
              type="number"
              min="-90"
              max="90"
              step="any"
            />
          </label>

          <label class="photos-field">
            <span>
              Longitud
            </span>

            <input
              v-model="uploadForm.longitude"
              type="number"
              min="-180"
              max="180"
              step="any"
            />
          </label>
        </div>

        <div class="photo-options">
          <label>
            <input
              v-model="
                uploadForm.is_required
              "
              type="checkbox"
              @change="
                uploadForm.is_required
                  ? uploadForm.counts_for_minimum = true
                  : null
              "
            />

            <span></span>

            <div>
              <strong>
                Fotografía obligatoria
              </strong>

              <small>
                Debe mantenerse como evidencia.
              </small>
            </div>
          </label>

          <label>
            <input
              v-model="
                uploadForm.counts_for_minimum
              "
              type="checkbox"
              :disabled="
                uploadForm.is_required
              "
            />

            <span></span>

            <div>
              <strong>
                Cuenta para el mínimo
              </strong>

              <small>
                Suma al requisito de la reparación.
              </small>
            </div>
          </label>
        </div>

        <footer class="photos-modal-actions">
          <button
            class="photos-secondary-button"
            type="button"
            :disabled="uploading"
            @click="closeUploadModal"
          >
            Cancelar
          </button>

          <button
            class="photos-primary-button"
            type="submit"
            :disabled="
              uploading ||
              !selectedFiles.length
            "
          >
            {{
              uploading
                ? "Subiendo..."
                : `Subir ${
                    selectedFiles.length ||
                    ""
                  } fotografía${
                    selectedFiles.length === 1
                      ? ""
                      : "s"
                  }`
            }}
          </button>
        </footer>
      </form>
    </div>

    <!-- VERIFICAR -->
    <div
      v-if="verifyModalVisible"
      class="photos-modal-backdrop"
      @click.self="closeVerifyModal"
    >
      <form
        class="photos-modal"
        @submit.prevent="
          submitVerification
        "
      >
        <header class="photos-modal-header">
          <div>
            <h3>
              Verificar fotografía
            </h3>

            <p>
              {{
                selectedPhoto?.title ||
                selectedPhoto?.original_filename
              }}
            </p>
          </div>

          <button
            class="photos-modal-close"
            type="button"
            @click="closeVerifyModal"
          >
            ×
          </button>
        </header>

        <label class="photos-field">
          <span>
            Notas de verificación
          </span>

          <textarea
            v-model="
              verificationForm.verification_notes
            "
            rows="5"
            placeholder="Observaciones de la revisión de evidencia"
          ></textarea>
        </label>

        <footer class="photos-modal-actions">
          <button
            class="photos-secondary-button"
            type="button"
            @click="closeVerifyModal"
          >
            Cancelar
          </button>

          <button
            class="photos-success-button"
            type="submit"
            :disabled="processing"
          >
            Confirmar verificación
          </button>
        </footer>
      </form>
    </div>

    <!-- QUITAR VERIFICACIÓN -->
    <div
      v-if="
        removeVerificationModalVisible
      "
      class="photos-modal-backdrop"
      @click.self="
        closeRemoveVerificationModal
      "
    >
      <form
        class="photos-modal"
        @submit.prevent="
          submitRemoveVerification
        "
      >
        <header class="photos-modal-header">
          <div>
            <h3>
              Quitar verificación
            </h3>

            <p>
              La fotografía volverá a quedar pendiente.
            </p>
          </div>

          <button
            class="photos-modal-close"
            type="button"
            @click="
              closeRemoveVerificationModal
            "
          >
            ×
          </button>
        </header>

        <label class="photos-field">
          <span>
            Motivo
          </span>

          <textarea
            v-model="
              verificationForm.reason
            "
            rows="5"
            placeholder="Indica por qué se retira la verificación"
          ></textarea>
        </label>

        <footer class="photos-modal-actions">
          <button
            class="photos-secondary-button"
            type="button"
            @click="
              closeRemoveVerificationModal
            "
          >
            Cancelar
          </button>

          <button
            class="photos-warning-button"
            type="submit"
            :disabled="processing"
          >
            Quitar verificación
          </button>
        </footer>
      </form>
    </div>

    <!-- VISTA PREVIA -->
    <div
      v-if="
        previewModalVisible &&
        selectedPhoto
      "
      class="photos-modal-backdrop preview-backdrop"
      @click.self="closePreview"
    >
      <div class="photo-preview-modal">
        <header>
          <div>
            <strong>
              {{
                selectedPhoto.title ||
                selectedPhoto.original_filename ||
                "Fotografía"
              }}
            </strong>

            <span>
              {{ getCategoryName(selectedPhoto) }}
              ·
              {{ getStageName(selectedPhoto) }}
            </span>
          </div>

          <button
            type="button"
            @click="closePreview"
          >
            ×
          </button>
        </header>

        <img
          v-if="
            getPhotoUrl(
              selectedPhoto
            )
          "
          :src="
            getPhotoUrl(
              selectedPhoto
            )
          "
          :alt="
            selectedPhoto.title ||
            'Fotografía'
          "
        />

        <div
          v-if="
            selectedPhoto.description
          "
          class="preview-description"
        >
          {{
            selectedPhoto.description
          }}
        </div>
      </div>
    </div>
  </section>
</template>