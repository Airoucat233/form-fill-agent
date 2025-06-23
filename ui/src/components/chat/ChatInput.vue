<template>
  <div class="flex items-center border-t bg-white px-4 py-2">
    <input
      v-model="inputText"
      @keyup.enter="sendMessage"
      type="text"
      class="flex-1 rounded-lg border px-3 py-2 focus:ring-2 focus:ring-blue-400 focus:outline-none"
      placeholder="请输入内容..."
    />
    <button
      @click="sendMessage"
      class="ml-2 rounded-lg bg-blue-500 px-4 py-2 text-white transition hover:bg-blue-600"
    >
      发送
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const inputText = ref('')
const emit = defineEmits(['send-message'])

const sendMessage = () => {
  if (inputText.value.trim()) {
    emit('send-message', inputText.value.trim())
    inputText.value = ''
  }
}
</script>

<style scoped></style>
