<template>
  <div class="w-64 flex-shrink-0 overflow-y-auto border-r bg-gray-100 p-4">
    <h3 class="mb-4 text-lg font-semibold text-gray-800">历史记录</h3>
    <button
      @click="createNewChat"
      class="mb-4 w-full rounded-lg bg-blue-500 px-4 py-2 text-white transition hover:bg-blue-600"
    >
      + 新建聊天
    </button>
    <ul class="space-y-2">
      <li
        v-for="session in historySessions"
        :key="session.id"
        @click="selectSession(session.id)"
        class="cursor-pointer rounded-lg p-2 transition"
        :class="{
          'bg-blue-200 font-medium text-blue-800': session.id === currentSessionId,
          'hover:bg-gray-200': session.id !== currentSessionId,
        }"
      >
        {{ session.preview || '新会话' }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

interface HistorySession {
  id: string
  preview: string
}

defineProps<{
  historySessions: HistorySession[]
  currentSessionId: string | null
}>()

const emit = defineEmits(['select-session', 'create-new-chat'])

const selectSession = (id: string) => {
  emit('select-session', id)
}

const createNewChat = () => {
  emit('create-new-chat')
}
</script>

<style scoped></style>
