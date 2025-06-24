// useMarkdownVNodeRenderer.ts
import { h, Fragment, type VNode } from 'vue'
import type MarkdownIt from 'markdown-it'
import ECharts from '../components/ECharts.vue'
import type { Token } from 'markdown-it/index.js'

export type VNodeRenderRule = (
  tokens: Token[],
  idx: number,
  options: Options,
  env: any,
  self: Renderer,
) => VNode

export interface MarkdownItVNodeRenderer extends MarkdownIt {
  renderVNode: (tokens: Token[]) => VNode[]
  vnodeRenderer: {
    rules: VNodeRenderRuleRecord
  }
}

export interface VNodeRenderRuleRecord {
  [type: string]: VNodeRenderRule | undefined
  code_inline?: VNodeRenderRule | undefined
  code_block?: VNodeRenderRule | undefined
  fence?: VNodeRenderRule | undefined
  image?: VNodeRenderRule | undefined
  hardbreak?: VNodeRenderRule | undefined
  softbreak?: VNodeRenderRule | undefined
  text?: VNodeRenderRule | undefined
  html_block?: VNodeRenderRule | undefined
  html_inline?: VNodeRenderRule | undefined
}

export function createVNodeRenderer(md: MarkdownIt) {
  const rules = md.renderer.rules

  rules.fence = (tokens, idx) => {
    const token = tokens[idx]
    const lang = token.info.trim()

    if (lang === 'echarts') {
      try {
        const json = JSON.parse(token.content)
        return h(ECharts, { options: json })
      } catch {
        return h('pre', {}, 'ECharts JSON 错误')
      }
    }

    return h('pre', {}, [h('code', {}, token.content)])
  }

  rules.text = (tokens, idx) => tokens[idx].content

  rules.paragraph_open = () => ({ tag: 'p', open: true })
  rules.paragraph_close = () => ({ close: true })

  rules.inline = (tokens, idx, opts, env, self) => {
    const token = tokens[idx]
    return h(
      Fragment,
      {},
      token.children?.map((child) => {
        const rule = rules[child.type]
        return rule ? rule([child], 0) : child.content
      }),
    )
  }

  // 渲染函数
  md.renderVNode = (tokens) => {
    const vnodes: any[] = []
    const stack: any[] = []

    for (let i = 0; i < tokens.length; i++) {
      const token = tokens[i]
      const rule = rules[token.type]

      if (rule) {
        const result = rule(tokens, i, {}, {}, md.renderer)
        if (!result) continue

        if (result.close) {
          const last = stack.pop()
          if (last) vnodes.push(last)
        } else if (result.open) {
          const newVNode = h(result.tag, {}, [])
          stack.push(newVNode)
        } else {
          if (stack.length > 0) {
            stack[stack.length - 1].children.push(result)
          } else {
            vnodes.push(result)
          }
        }
      }
    }

    return vnodes
  }

  return md
}
