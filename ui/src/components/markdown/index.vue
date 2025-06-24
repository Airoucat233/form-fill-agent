<template>
  <div ref="markdownDomRef" v-html="rendered" class="markdown-body"></div>
  <div class="markdown-body">
    <component v-for="(node, i) in vnodeTree" :is="node" :key="i" />
  </div>
</template>

<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import 'github-markdown-css/github-markdown.css'
import '@/assets/markdown.scss'
import ECharts from './components/ECharts.vue'

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
  type VNode,
  h,
  Fragment,
} from 'vue'
import { createVNodeRenderer } from './hook/useMarkdownVNodeRenderer'
import type { Token } from 'markdown-it/index.js'
import { full as emoji } from 'markdown-it-emoji'

const props = defineProps<{
  modelValue: {
    type: String
    default: ''
    required: true
  }
}>()

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

md.use(emoji)

const defaultFence = md.renderer.rules.fence

let stack: { token: Token; children: VNode[] }[] = []

function renderVNode(tokens: Token[], env: any = {}): VNode[] {
  const vnodes: VNode[] = []
  let vnodestrs: string = ''

  const pushChild = (vnode: VNode) => {
    if (stack.length > 0) {
      stack[stack.length - 1].children.push(vnode)
    } else {
      vnodes.push(vnode)
    }
  }

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i]

    if (token.type === 'fence') {
      if (vnodestrs) {
        vnodes.push(h('div', { class: 'text-block', innerHTML: vnodestrs }))
        vnodestrs = ''
      }

      vnodes.push(h(ECharts, { config: token.content }))
    } else {
      const html = md.renderer.render([token], md.options, env)
      vnodestrs += html
    }
    // if (token.hidden) continue
    // // 1. 开标签：入栈
    // if (token.nesting === 1) {
    //   stack.push({ token, children: [] })
    // }

    // // 2. 关闭标签：出栈并构建VNode
    // else if (token.nesting === -1) {
    //   const last = stack.pop()
    //   if (!last) continue

    //   const tag = last.token.tag
    //   const vnode = h(tag, getAttrs(last.token), last.children)

    //   pushChild(vnode)
    // }

    // // 3. 普通token
    // else if (token.nesting === 0) {
    //   if (token.type === 'inline') {
    //     if (token.children) {
    //       const children = renderVNode(token.children, env)
    //       children.forEach(pushChild)
    //     }
    //   } else if (token.type === 'text') {
    //     // 普通文本用 span 包裹（不能是 string）
    //     pushChild(h(Fragment, [token.content]))
    //   } else if (token.type == 'softbreak') {
    //     //自闭和的元素
    //     pushChild(h(token.tag))
    //   } else if (token.tag) {
    //     const html = md.renderer.render([token], md.options, env).trim()
    //     pushChild(h(token.tag, { innerHTML: html }))
    //   } else {
    //     // fallback（不常见），作为 span 文本兜底
    //     pushChild(h('span', {}, token.content))
    //   }
    // }
  }

  return vnodes
}

function getAttrs(token: Token): Record<string, any> {
  const attrs: Record<string, any> = {}
  if (token.attrs) {
    for (const [name, value] of token.attrs) {
      attrs[name] = value
    }
  }
  return attrs
}

const vnodeTree = computed(() => {
  const tokens = md.parse(props.modelValue, {})
  // const tokens = md.parse('- a 111\n- b 222', {})
  stack = []
  return renderVNode(tokens)
})

const rendered = computed(() => {
  return md.render(props.modelValue)
})

onMounted(() => {})

onMounted(() => {})
</script>

<style lang="scss" scoped></style>
