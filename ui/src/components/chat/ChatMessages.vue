<template>
  <div class="flex-1 space-y-3 overflow-y-auto p-4">
    <ChatMessage v-for="(message, index) in messages" :key="index" :message="message" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import ChatMessage from '@/components/chat/ChatMessage.vue'

interface Message {
  text: string
  sender: 'user' | 'ai'
}

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
