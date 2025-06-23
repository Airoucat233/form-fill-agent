<template>
  <div ref="markdownDomRef" v-html="rendered" class="markdown-body w-full" :style="style"></div>
</template>

<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import 'github-markdown-css/github-markdown.css'

import {
  nextTick,
  onUpdated,
  reactive,
  toRef,
  onBeforeUnmount,
  watchEffect,
  ref,
  computed,
  onMounted,
  watch,
} from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
    required: true,
  },
  style: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['event', 'update:modelValue'])

const markdownDomRef = ref(null)

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

const rendered = computed(() => {
  return md.render(props.modelValue)
})

onMounted(() => {})

onMounted(() => {})
</script>

<style lang="scss" scoped></style>
