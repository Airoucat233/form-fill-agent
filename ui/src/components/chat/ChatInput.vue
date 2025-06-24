<template>
  <div
    class="chat-input flex w-8/12 items-center rounded-2xl border border-gray-300 bg-white px-4 py-3 shadow-md focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-400"
  >
    <textarea
      v-model="inputText"
      @keyup.enter.exact.prevent="sendMessage"
      rows="3"
      placeholder="请输入内容..."
      class="scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent max-h-24 flex-1 resize-none overflow-y-auto bg-transparent text-gray-900 placeholder-gray-400 outline-none"
    ></textarea>
    <button
      :disabled="!inputText.trim()"
      @click="sendMessage"
      class="ml-3 rounded-full bg-blue-600 px-4 py-2 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
      aria-label="发送消息"
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
