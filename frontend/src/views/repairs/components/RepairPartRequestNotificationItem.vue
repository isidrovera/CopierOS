<script setup>
import "./RepairPartRequestNotificationItem.css"

defineProps({
  notification: { type: Object, required: true },
})

const emit = defineEmits(["open", "mark-read"])
</script>

<template>
  <article
    class="part-request-notification"
    :class="{ unread: !notification.read_at }"
  >
    <button type="button" @click="emit('open', notification)">
      <strong>{{ notification.title }}</strong>
      <small>{{ notification.message }}</small>
      <span>{{ notification.created_at }}</span>
    </button>

    <button
      v-if="!notification.read_at"
      type="button"
      @click="emit('mark-read', notification)"
    >
      Marcar como leída
    </button>
  </article>
</template>
