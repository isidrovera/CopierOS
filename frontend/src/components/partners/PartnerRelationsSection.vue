<script setup>
import {
  onMounted,
  ref,
} from "vue"

import PartnerBranchesSection from "./PartnerBranchesSection.vue"
import PartnerContactsSection from "./PartnerContactsSection.vue"

import {
  getBranches,
} from "../../services/partners.service"


const props = defineProps({
  partnerId: {
    type: String,
    required: true,
  },

  users: {
    type: Array,
    default: () => [],
  },
})


const branches = ref([])
const loadingBranches = ref(false)
const branchesError = ref("")


async function loadBranches() {
  if (!props.partnerId) {
    branches.value = []
    return
  }

  loadingBranches.value = true
  branchesError.value = ""

  try {
    const response = await getBranches({
      partner: props.partnerId,
      includeArchived: true,
    })

    branches.value = Array.isArray(response)
      ? response
      : response?.results || []
  } catch (error) {
    branches.value = []

    branchesError.value =
      error.message ||
      "No se pudieron cargar las sucursales para los contactos."
  } finally {
    loadingBranches.value = false
  }
}


async function handleBranchesUpdated() {
  await loadBranches()
}


async function handleContactsUpdated() {
  await loadBranches()
}


onMounted(() => {
  loadBranches()
})
</script>

<template>
  <section class="relations-container">
    <header class="relations-header">
      <div>
        <span class="page-kicker">
          Información relacionada
        </span>

        <h3>
          Sucursales y contactos
        </h3>

        <p>
          Administra las ubicaciones del cliente y
          las personas responsables de cada proceso.
        </p>
      </div>

      <button
        class="refresh-button"
        type="button"
        :disabled="loadingBranches"
        @click="loadBranches"
      >
        <span
          :class="{
            rotating: loadingBranches,
          }"
        >
          ↻
        </span>

        {{
          loadingBranches
            ? "Actualizando..."
            : "Actualizar relaciones"
        }}
      </button>
    </header>

    <div
      v-if="branchesError"
      class="message error-message"
    >
      {{ branchesError }}
    </div>

    <div class="relations-content">
      <PartnerBranchesSection
        :partner-id="partnerId"
        :users="users"
        @updated="handleBranchesUpdated"
      />

      <PartnerContactsSection
        :partner-id="partnerId"
        :branches="branches"
        @updated="handleContactsUpdated"
      />
    </div>
  </section>
</template>

<style scoped>
button {
  font: inherit;
}

.relations-container {
  display: flex;
  flex-direction: column;
  gap: 17px;
}

.relations-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 18px 20px;
  border: 1px solid #dfe3ec;
  border-radius: 15px;
  background:
    linear-gradient(
      135deg,
      #f8f9fd,
      #ffffff
    );
}

.page-kicker {
  display: block;
  margin-bottom: 5px;
  color: #1f35c4;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.relations-header h3 {
  margin: 0;
  color: #1d2940;
  font-size: 18px;
}

.relations-header p {
  margin: 6px 0 0;
  color: #8693a4;
  font-size: 12px;
  line-height: 1.5;
}

.refresh-button {
  min-height: 41px;
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 0 14px;
  border: 1px solid #dfe3ec;
  border-radius: 10px;
  background: white;
  color: #667382;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    background 0.2s ease,
    color 0.2s ease,
    box-shadow 0.2s ease;
}

.refresh-button:hover {
  transform: translateY(-2px);
  border-color: #cfd5f7;
  background: #edf0ff;
  color: #1f35c4;
  box-shadow:
    0 8px 18px rgba(31, 53, 196, 0.09);
}

.refresh-button:disabled {
  opacity: 0.6;
  cursor: wait;
  transform: none;
}

.rotating {
  display: inline-block;
  animation: rotate 0.8s linear infinite;
}

.message {
  padding: 11px 13px;
  border-radius: 10px;
  font-size: 12px;
}

.error-message {
  border: 1px solid #e8caca;
  background: #fff3f3;
  color: #9a4141;
}

.relations-content {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

@keyframes rotate {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 760px) {
  .relations-header {
    flex-direction: column;
  }

  .refresh-button {
    width: 100%;
  }
}
</style>