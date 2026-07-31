<script setup>
import {
  computed,
} from "vue"

import "./RepairPartRequestFlow.css"


const props = defineProps({
  currentStatus: {
    type: String,
    default: "draft",
  },
})


const steps = [
  {
    key: "draft",
    label: "Solicitud",
    description: "Registro y envío",
    color: "blue",
  },
  {
    key: "in_review",
    label: "Revisión",
    description: "Validación del jefe",
    color: "purple",
  },
  {
    key: "approved",
    label: "Decisión",
    description: "Aprobación del pedido",
    color: "orange",
  },
  {
    key: "source",
    label: "Origen",
    description: "Reserva, compra o retiro",
    color: "cyan",
  },
  {
    key: "delivered",
    label: "Entrega",
    description: "Preparación y despacho",
    color: "amber",
  },
  {
    key: "received",
    label: "Recepción",
    description: "Recepción y cierre",
    color: "green",
  },
]


const statusOrder = {
  draft: 1,
  submitted: 1,

  in_review: 2,

  partially_approved: 3,
  approved: 3,

  source_evaluation: 4,
  pending_reservation: 4,
  pending_purchase: 4,
  pending_external_repair: 4,
  pending_withdrawal: 4,
  authorized_for_withdrawal: 4,
  withdrawn: 4,

  pending_logistics: 5,
  prepared: 5,
  delivered: 5,
  partially_attended: 5,

  attended: 6,
  received: 6,
  installed: 6,
  completed: 6,
  closed: 6,
}


const statusLabels = {
  draft: "Borrador",
  submitted: "Solicitud enviada",

  in_review: "En revisión",

  partially_approved: "Aprobación parcial",
  approved: "Aprobado",

  source_evaluation: "Evaluando origen",
  pending_reservation: "Pendiente de reserva",
  pending_purchase: "Pendiente de compra",
  pending_external_repair: "Pendiente de reparación externa",
  pending_withdrawal: "Pendiente de retiro",
  authorized_for_withdrawal: "Retiro autorizado",
  withdrawn: "Retirado",

  pending_logistics: "Pendiente de logística",
  prepared: "Preparado",
  delivered: "Entregado",
  partially_attended: "Atendido parcialmente",

  attended: "Atendido",
  received: "Recibido",
  installed: "Instalado",
  completed: "Completado",
  closed: "Cerrado",
}


const currentStepNumber = computed(() =>
  statusOrder[props.currentStatus] || 1
)


const currentStatusLabel = computed(() =>
  statusLabels[props.currentStatus] ||
  props.currentStatus ||
  "Estado no definido"
)


function isCompleted(index) {
  return index + 1 < currentStepNumber.value
}


function isActive(index) {
  return index + 1 === currentStepNumber.value
}


function getStepClass(step, index) {
  return [
    `step-${step.color}`,
    {
      completed: isCompleted(index),
      active: isActive(index),
      pending:
        !isCompleted(index) &&
        !isActive(index),
    },
  ]
}
</script>

<template>
  <section class="part-request-flow-wrapper">
    <header class="part-request-flow-header">
      <div>
        <span>Flujo de atención</span>

        <strong>
          {{ currentStatusLabel }}
        </strong>
      </div>

      <div class="part-request-flow-progress">
        <span>
          Etapa {{ currentStepNumber }} de {{ steps.length }}
        </span>

        <div class="part-request-flow-progress__track">
          <div
            class="part-request-flow-progress__value"
            :style="{
              width: `${(currentStepNumber / steps.length) * 100}%`,
            }"
          />
        </div>
      </div>
    </header>

    <div class="part-request-flow-scroll">
      <ol class="part-request-flow">
        <li
          v-for="(step, index) in steps"
          :key="step.key"
          :class="getStepClass(step, index)"
        >
          <div class="part-request-flow__connector">
            <span />
          </div>

          <div class="part-request-flow__indicator">
            <span
              v-if="isCompleted(index)"
              class="part-request-flow__check"
            >
              ✓
            </span>

            <span v-else>
              {{ index + 1 }}
            </span>
          </div>

          <div class="part-request-flow__content">
            <strong>
              {{ step.label }}
            </strong>

            <small>
              {{
                isActive(index)
                  ? currentStatusLabel
                  : step.description
              }}
            </small>
          </div>

          <span
            v-if="isActive(index)"
            class="part-request-flow__current"
          >
            Actual
          </span>
        </li>
      </ol>
    </div>
  </section>
</template>