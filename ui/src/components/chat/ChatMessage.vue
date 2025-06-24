<template>
  <div class="chat-message flex w-8/12 py-5">
    <div v-if="message.role === 'Human'" class="flex w-full justify-end">
      <div class="bg-primary/15 rounded-lg p-3">
        {{ message.content }}
      </div>
    </div>
    <div v-else class="flex w-0 flex-1">
      <MarkDown v-model="message.content"></MarkDown>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Message } from '@/types/chat'
import MarkDown from '@/components/markdown/index.vue'
defineProps<{
  message: Message
}>()
</script>

<style scoped></style>
