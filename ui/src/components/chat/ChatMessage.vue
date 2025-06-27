<template>
  <div class="chat-message flex w-8/12 py-5">
    <div v-if="message.role === 'Human'" class="flex w-full justify-end">
      <div class="bg-primary/15 rounded-lg p-3">
        {{ message.content }}
      </div>
    </div>
    <div v-else class="flex w-0 flex-1">
      <VueMarkdown :content="message.content" :fencePlugin="{ echarts: Echarts }"></VueMarkdown>
      <!-- <div v-html="render(message.content)"></div> -->
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Message } from '@/types/chat'
import VueMarkdown from 'vue-markdown-stream-test'
import 'vue-markdown-stream-test/dist/index.css'
import MarkDown from '@/components/markdown/index.vue'
import Echarts from '@/components/visual/ECharts.vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
// import Mermaid from '@/components/visual/Mermaid.vue'
const props = defineProps<{
  message: Message
}>()

const md: MarkdownIt = new MarkdownIt({
  html: true,
  linkify: true,
  breaks: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return (
          '<pre class="hljs"><code>' +
          hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
          '</code></pre>'
        )
      } catch (__) {}
    }

    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>'
  },
})

const render = (text: string) => {
  return md.render(text)
}
</script>

<style scoped></style>
