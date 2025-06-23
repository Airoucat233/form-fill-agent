<template>
  <div class="w-64 flex-shrink-0 overflow-y-auto bg-white p-4 shadow-md">
    <button
      @click="createNewChat"
      class="focus:ring-opacity-50 mb-6 flex w-full items-center justify-center rounded-full bg-blue-600 px-4 py-3 text-white transition-colors hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:outline-none"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="mr-2 h-5 w-5"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fill-rule="evenodd"
          d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
          clip-rule="evenodd"
        />
      </svg>
      新建聊天
    </button>

    <h3 class="mb-4 text-sm font-semibold tracking-wider text-gray-500 uppercase">最近</h3>

    <ul class="space-y-2">
      <li
        v-for="session in historySessions"
        :key="session.id"
        @click="selectSession(session.id)"
        class="group flex cursor-pointer items-center rounded-lg p-3 transition-all duration-200"
        :class="{
          'bg-blue-100 font-medium text-blue-800': session.id === currentSessionId,
          'text-gray-700 hover:bg-gray-100': session.id !== currentSessionId,
        }"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="mr-3 h-5 w-5"
          :class="{
            'text-blue-600': session.id === currentSessionId,
            'text-gray-500 group-hover:text-gray-600': session.id !== currentSessionId,
          }"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fill-rule="evenodd"
            d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.336-3.11c-.813-1.33-.895-2.823-.131-4.212A8.006 8.006 0 0110 2c4.418 0 8 3.134 8 7z"
            clip-rule="evenodd"
          />
        </svg>
        <span class="truncate">{{ session.preview || '新会话' }}</span>
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
