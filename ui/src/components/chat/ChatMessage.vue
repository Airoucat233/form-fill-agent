<template>
  <div class="flex w-full py-5">
    <div v-if="message.role === 'Human'" class="flex w-full justify-end">
      <div class="bg-primary/15 max-w-7/12 rounded-lg p-3">
        {{ message.content }}
      </div>
    </div>
    <div v-else class="flex w-full">
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
