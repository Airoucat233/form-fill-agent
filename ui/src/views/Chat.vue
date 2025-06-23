<template>
  <div class="flex h-screen w-full">
    <!-- History Sidebar with Toggle -->
    <div
      :class="[
        'flex-shrink-0',
        'overflow-y-auto',
        'border-r',
        'bg-gray-100',
        'transition-width',
        'duration-300',
        'ease-in-out',
        showHistory ? 'w-64' : 'w-16',
      ]"
    >
      <div class="p-4">
        <button
          @click="toggleHistory"
          class="w-full rounded-lg bg-blue-500 px-4 py-2 text-white transition hover:bg-blue-600"
        >
          <span v-if="showHistory">收起历史</span>
          <span v-else>展开历史</span>
        </button>
      </div>
      <ChatHistory
        v-if="showHistory"
        :history-sessions="historySessions"
        :current-session-id="currentSessionId"
        @select-session="handleSelectSession"
        @create-new-chat="handleCreateNewChat"
      />
    </div>

    <!-- Main Chat Area -->
    <div class="flex flex-1 flex-col">
      <ChatContainer>
        <template #header>
          <ChatHeader />
        </template>
        <template #messages>
          <ChatMessages :messages="messages" />
        </template>
        <template #input>
          <ChatInput @send-message="handleSendMessage" />
        </template>
      </ChatContainer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ChatContainer from '@/components/chat/ChatContainer.vue'
import ChatHeader from '@/components/chat/ChatHeader.vue'
import ChatMessages from '@/components/chat/ChatMessages.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import ChatHistory from '@/components/chat/ChatHistory.vue'

interface Message {
  text: string
  sender: 'user' | 'ai'
}

interface HistorySession {
  id: string
  preview: string
}

const messages = ref<Message[]>([{ text: '你好，有什么可以帮你？', sender: 'ai' }])

// 新增历史记录相关的响应式状态
const showHistory = ref(true) // 控制历史记录侧边栏的显示与隐藏
const currentSessionId = ref('session-1') // 追踪当前活跃的聊天会话
const historySessions = ref<HistorySession[]>([
  { id: 'session-1', preview: '会话 1: 你好' },
  { id: 'session-2', preview: '会话 2: 关于AI的问题' },
  { id: 'session-3', preview: '会话 3: 技术讨论' },
])

// 新增历史记录管理函数
const toggleHistory = () => {
  showHistory.value = !showHistory.value
}

const handleSelectSession = (id: string) => {
  currentSessionId.value = id
  // 在这里，您通常会从数据源加载所选会话的消息。
  // 在此示例中，我们仅记录它，如果它是不同的会话，则可能重置消息。
  console.log(`Selected session: ${id}`)
}

const handleCreateNewChat = () => {
  const newId = `session-${historySessions.value.length + 1}`
  historySessions.value.push({ id: newId, preview: `新会话 ${historySessions.value.length + 1}` })
  currentSessionId.value = newId
  messages.value = [] // 清空当前消息，开始新会话
  console.log('Created new chat session')
}

const handleSendMessage = (text: string) => {
  messages.value.push({ text, sender: 'user' })
  // 模拟 AI 回复
  setTimeout(() => {
    messages.value.push({ text: `AI 收到了你的消息: "${text}"`, sender: 'ai' })
  }, 500)
}
</script>

<style lang="scss" scoped>
/* 您可能需要为侧边栏宽度添加过渡效果 */
.flex-shrink-0 {
  transition: width 0.3s ease-in-out;
}
</style>
