<template>
  <div class="flex" :class="{ 'justify-end': message.sender === 'user' }">
    <div
      class="max-w-xs rounded-lg px-4 py-2"
      :class="{
        'bg-blue-500 text-white': message.sender === 'user',
        'bg-gray-200 text-gray-800': message.sender === 'ai',
      }"
    >
      <span>{{ message.text }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Message {
  text: string
  sender: 'user' | 'ai'
}

defineProps<{
  message: Message
}>()
</script>

<style scoped></style>
