<template>
  <div class="flex flex-1 justify-center overflow-x-hidden overflow-y-auto">
    <div class="flex w-8/12 flex-col items-center space-y-3 p-4">
      <ChatMessage v-for="(message, index) in messages" :key="index" :message="message" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import type { Message } from '@/types/chat'

const props = defineProps<{
  messages: Message[]
}>()

const messagesContainer = ref<HTMLElement | null>(null)

watch(
  () => props.messages,
  () => {
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    })
  },
  { deep: true },
)
</script>

<style scoped></style>
